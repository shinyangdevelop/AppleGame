import sys
import io
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QLabel, QGridLayout, QFrame, QSlider, QTextEdit, QSplitter,
                             QGroupBox, QSpinBox, QAbstractSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QFont, QColor
from search import iterative_solver, h_iteration_solver, r_iteration_solver, exhaustive_solver, n_iterative_solver

from core import scan, solve, restart_game
from util import send_data

class EmittingStream(QObject):
    textWritten = pyqtSignal(str)
    def write(self, text): self.textWritten.emit(str(text))
    def flush(self): pass

THEMES = {
    "Dark": {
        "background": "rgb(22, 25, 28)",
        "text": "#ECEFF4",
        "accent": "#88C0D0",
        "dropdown_bg": "rgb(59, 66, 82)",
        "button_bg": "rgb(76, 86, 106)",
        "button_hover": "rgb(94, 129, 172)",
        "button_pressed": "rgb(129, 161, 193)",
        "border": "#6B768A",
        "frame_bg": "rgb(39, 46, 62)",
        "scrollbar_bg": "rgb(59, 66, 82)",
        "scrollbar_handle": "rgb(59, 66, 82)",
        "sub_background": "rgb(32, 35, 38)",
        "third_background": "rgb(42, 45, 48)",
        "second_border": "rgb(52, 55, 58)"
    },
    "Light": {
        "background": "rgb(250, 252, 255)",
        "text": "#2B3035",
        "accent": "#5FA9C0",
        "dropdown_bg": "rgb(230, 235, 245)",
        "button_bg": "rgb(210, 220, 235)",
        "button_hover": "rgb(190, 210, 235)",
        "button_pressed": "rgb(150, 180, 210)",
        "border": "#A4B0C0",            
        "frame_bg": "rgb(230, 235, 245)",
        "scrollbar_bg": "rgb(220, 230, 240)",
        "scrollbar_handle": "rgb(230, 235, 245)",       
        "sub_background": "rgb(240, 242, 245)",
        "third_background": "rgb(230, 232, 235)",
        "second_border": "rgb(220, 222, 225)"
    }
}

class SolverThread(QThread):
    result_ready = pyqtSignal(int, list)
    finished = pyqtSignal()
    def __init__(self, solver_func, kwargs):
        super().__init__()
        self.solver_func = solver_func
        self.kwargs = kwargs
    def run(self):
        try:
            max_score, move_sequence = self.solver_func(**self.kwargs)
            self.result_ready.emit(max_score, move_sequence)
        except Exception as e:
            print(f"Error in solver thread: {e}")
        finally:
            self.finished.emit()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Game Solver")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry.width() // 2, 50, screen_geometry.width() // 2, 0)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        self.initial_grid = None
        self.pos_dict = None
        self.solver_thread = None
        self.last_move_sequence = None
        self.current_theme = "Dark"

        self.init_ui()
        self.apply_theme(self.current_theme)
        sys.stdout = EmittingStream(textWritten=self.normal_output_written)
        

    def showEvent(self, event):
        super().showEvent(event)

    def __del__(self):
        sys.stdout = sys.__stdout__

    def normal_output_written(self, text):
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        
        self.container = QWidget()
        self.container.setObjectName("container")
        self.main_layout.addWidget(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0,0,0,0)
        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.scan_grid)
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(restart_game)
        self.theme_toggle_button = QPushButton("Light Theme")
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        toolbar_layout.addWidget(self.scan_button)
        toolbar_layout.addWidget(self.restart_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.theme_toggle_button)
        layout.addWidget(toolbar)

        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)

        grid_frame = QFrame()
        grid_frame.setFrameShape(QFrame.Shape.StyledPanel)
        grid_layout_container = QVBoxLayout(grid_frame)
        self.scanned_result_label = QLabel("Scanned Result:")
        self.scanned_result_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.scanned_result_label.setFixedSize(520, 40)
        self.grid_widget = QWidget()
        self.grid_widget.setFixedSize(520, 320)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(1)
        grid_layout_container.addWidget(self.scanned_result_label)
        grid_layout_container.addWidget(self.grid_widget)
        top_layout.addWidget(grid_frame)

        right_panel = QVBoxLayout()
        
        status_score_frame = QFrame()
        status_score_frame.setObjectName('status-score-frame')
        status_score_frame.setFixedHeight(120)
        status_score_layout = QVBoxLayout(status_score_frame)
        self.best_score_display = QLabel("Best Score: N/A")
        self.best_score_display.setFixedHeight(40)
        self.best_score_display.setFont(QFont("Segoe UI", 11))
        self.status_display = QLabel("Status: Idle")
        self.status_display.setFixedHeight(40)
        self.status_display.setFont(QFont("Segoe UI", 11))
        status_score_layout.addWidget(self.best_score_display)
        status_score_layout.addWidget(self.status_display)
        right_panel.addWidget(status_score_frame)
        
        self.action_controls_frame = QFrame()
        self.action_controls_frame.setObjectName('action-controls-frame')
        action_controls_layout = QVBoxLayout(self.action_controls_frame)
        self.action_controls_frame.setFixedHeight(220)
        algo_layout = QHBoxLayout()
        self.algo_label = QLabel("Algorithm:")
        algo_layout.addWidget(self.algo_label)
        self.algorithm_dropdown = QComboBox()
        self.algorithm_dropdown.addItems(["iterative", "exhaustive", "h-iteration", "r-iteration", "n-iteration"])
        self.algorithm_dropdown.currentTextChanged.connect(self.update_search_params)
        algo_layout.addWidget(self.algorithm_dropdown)
        action_controls_layout.addLayout(algo_layout)
        
        self.search_params_group = QGroupBox("Search Parameters")
        self.search_params_group.setFixedHeight(70)
        self.search_params_layout = QGridLayout()
        self.search_params_group.setLayout(self.search_params_layout)
        
        self.max_calls_spin = QSpinBox()
        self.max_calls_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.max_calls_spin.setRange(1, 1000000)
        self.max_calls_spin.setValue(100000)
        self.branches_spin = QSpinBox()
        self.branches_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.branches_spin.setRange(1, 100)
        self.branches_spin.setValue(6)
        self.branches_spin.setFixedHeight(30)
        self.n_iteration_spin = QSpinBox()
        self.n_iteration_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.n_iteration_spin.setRange(1, 100)
        self.n_iteration_spin.setValue(6)
        self.n_iteration_spin.setFixedHeight(30)
        self.guess_limit_spin = QSpinBox()
        self.guess_limit_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.guess_limit_spin.setRange(1, 100000)
        self.guess_limit_spin.setValue(10000)
        
        self.max_calls_label = QLabel("Max Calls:")
        self.branches_label = QLabel("Branches:")
        self.n_iteration_label = QLabel("N Iteration:")
        self.guess_limit_label = QLabel("Guess/Max Iter:")

        self.search_params_layout.addWidget(self.max_calls_label, 0, 0)
        self.search_params_layout.addWidget(self.max_calls_spin, 0, 1)
        self.search_params_layout.addWidget(self.branches_label, 1, 0)
        self.search_params_layout.addWidget(self.branches_spin, 1, 1)
        self.search_params_layout.addWidget(self.n_iteration_label, 2, 0)
        self.search_params_layout.addWidget(self.n_iteration_spin, 2, 1)
        self.search_params_layout.addWidget(self.guess_limit_label, 3, 0)
        self.search_params_layout.addWidget(self.guess_limit_spin, 3, 1)
        
        action_controls_layout.addWidget(self.search_params_group)
        self.update_search_params("iterative")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.on_run)
        action_controls_layout.addWidget(self.search_button)
        action_controls_layout.addWidget(self.run_button)
        right_panel.addWidget(self.action_controls_frame)

        difficulty_frame = QFrame()
        difficulty_frame.setObjectName('difficulty-frame')
        difficulty_frame.setFixedHeight(120)
        difficulty_layout = QHBoxLayout(difficulty_frame)
        self.difficulty_label = QLabel("Difficulty:")
        self.difficulty_slider = QSlider(Qt.Orientation.Horizontal)
        self.difficulty_slider.setRange(1, 10)
        self.difficulty_slider.setValue(10)
        difficulty_layout.addWidget(self.difficulty_label)
        difficulty_layout.addWidget(self.difficulty_slider)
        right_panel.addWidget(difficulty_frame)
        
        top_layout.addLayout(right_panel, 1)
        
        content_splitter.addWidget(top_widget)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        content_splitter.addWidget(self.log_output)
        
        content_splitter.setSizes([400, 100])

        layout.addWidget(content_splitter)
        
        self.adjustSize()

    def update_search_params(self, algorithm):
        is_exhaustive = (algorithm == 'exhaustive')
        is_h_iteration = (algorithm == 'h-iteration')
        is_other_iterative = (algorithm in ['r-iteration', 'n-iteration', 'iterative'])

        self.max_calls_spin.setVisible(is_exhaustive)
        self.max_calls_label.setVisible(is_exhaustive)
        self.branches_spin.setVisible(is_h_iteration)
        self.branches_label.setVisible(is_h_iteration)
        self.n_iteration_spin.setVisible(is_h_iteration)
        self.n_iteration_label.setVisible(is_h_iteration)
        self.guess_limit_spin.setVisible(is_other_iterative)
        self.guess_limit_label.setVisible(is_other_iterative)
        
        
        if is_h_iteration:
            self.action_controls_frame.setFixedHeight(250)
            self.search_params_group.setFixedHeight(100)
        else:
            self.action_controls_frame.setFixedHeight(220)
            self.search_params_group.setFixedHeight(70)

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = THEMES[theme_name]
        self.setStyleSheet(f"""
            #container {{ background-color: {theme['background']}; }}
            QLabel {{ color: {theme['text']}; background-color: transparent; }}
            QPushButton {{ background-color: {theme['button_bg']}; color: {theme['text']}; border: none; padding: 10px; border-radius: 5px; font-family: "Segoe UI Variable"; }}
            QPushButton:hover {{ background-color: {theme['button_hover']}; }}
            QPushButton:pressed {{ background-color: {theme['button_pressed']}; }}
            QComboBox {{ background-color: {theme['button_bg']}; color: {theme['text']}; border: 1px solid {theme['border']}; padding: 8px; border-radius: 4px; }}
            QComboBox QAbstractItemView {{ background-color: {theme['dropdown_bg']}; color: {theme['text']}; border: 1px solid {theme['border']}; selection-background-color: {theme['accent']}; }}
            QSpinBox {{ background-color: {theme['button_bg']}; color: {theme['text']}; border: 1px solid {theme['border']}; padding: 8px; border-radius: 4px; }}
            QFrame {{ background-color: {theme['frame_bg']}; border-radius: 8px;}}
            QTextEdit {{ background-color: {theme['frame_bg']}; border: none; color: {theme['text']}; }}
            QGroupBox {{ border: 1px solid {theme['border']}; border-radius: 8px; margin-top: 10px; color: {theme['text']}; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }}
            QScrollBar:vertical {{ border: none; background: {theme['scrollbar_bg']}; width: 10px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {theme['scrollbar_handle']}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            #status-score-frame {{background-color: {theme['sub_background']};}}
            #action-controls-frame {{background-color: {theme['sub_background']};}}
            #difficulty-frame {{background-color: {theme['sub_background']};}}
            QLabel {{background-color: {theme['third_background']}; border-radius: 8px; border: 1px solid {theme['second_border']};}}
            QSpinBox::up-button, QSpinBox::down-button {{ background-color: transparent; }}
        """)
        if self.initial_grid:
            self.scan_grid()

    def toggle_theme(self):
        self.setUpdatesEnabled(False)
        if self.current_theme == "Dark":
            self.apply_theme("Light")
            self.theme_toggle_button.setText("Dark Theme")
        else:
            self.apply_theme("Dark")
            self.theme_toggle_button.setText("Light Theme")
        self.setUpdatesEnabled(True)


    def scan_grid(self):
        self.status_display.setText("Status: Scanning...")
        QApplication.processEvents()
        
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        self.initial_grid, _, _, self.pos_dict = scan()
        send_data(str(self.initial_grid))

        if self.initial_grid and any(any(row) for row in self.initial_grid):
            for r, row_data in enumerate(self.initial_grid):
                for c, cell_value in enumerate(row_data):
                    cell = QLabel(str(cell_value) if cell_value != 0 else "")
                    cell.setFrameShape(QFrame.Shape.Box)
                    cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cell.setFixedSize(30, 30)
                    self.grid_layout.addWidget(cell, r, c)
            self.status_display.setText("Status: Scan complete.")
            self.search_button.setEnabled(True)
        else:
            self.status_display.setText("Status: Scan failed. No items found.")
            self.search_button.setEnabled(False)

        self.best_score_display.setText("Best Score: N/A")

    def on_search(self):
        if self.initial_grid is None or not any(any(row) for row in self.initial_grid):
            self.status_display.setText("Status: Please perform a successful scan first.")
            return

        self.search_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.status_display.setText("Status: Searching for solution...")
        
        solver_name = self.algorithm_dropdown.currentText()
        search_func = globals()[f"{solver_name.replace('-', '_')}_solver"]
        
        argument = {'initial_grid': self.initial_grid}
        if solver_name == 'exhaustive':
            argument['max_calls'] = self.max_calls_spin.value()
        elif solver_name == 'h-iteration':
            argument['branches'] = self.branches_spin.value()
            argument['n_iteration'] = self.n_iteration_spin.value()
        else:
            argument['max_iteration' if solver_name == 'r-iteration' else 'guess_limit'] = self.guess_limit_spin.value()

        self.solver_thread = SolverThread(search_func, argument)
        self.solver_thread.result_ready.connect(self.on_search_complete)
        self.solver_thread.finished.connect(self.on_thread_finished)
        self.solver_thread.start()

    def on_search_complete(self, max_score, move_sequence):
        self.best_score_display.setText(f"Best Score: {max_score}")
        self.last_move_sequence = move_sequence
        self.status_display.setText("Status: Search complete.")

    def on_thread_finished(self):
        self.search_button.setEnabled(True)
        self.run_button.setEnabled(True)
        if self.status_display.text() == "Status: Searching for solution...":
            self.status_display.setText("Status: Search finished (no solution found).")

    def on_run(self):
        if self.last_move_sequence is None:
            self.status_display.setText("Status: Please run a search first.")
            return
        
        self.status_display.setText("Status: Executing moves...")
        QApplication.processEvents()
        solve(self.last_move_sequence, self.pos_dict, self.initial_grid, difficulty=self.difficulty_slider.value())
        self.status_display.setText("Status: Run complete.")

def run():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run()