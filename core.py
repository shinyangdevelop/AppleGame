import pyautogui
from pyautogui import ImageNotFoundException
from util import cluster_positions
import time
import numpy as np

def restart_game():
    try:
        reset = pyautogui.locateCenterOnScreen('images/reset.png', confidence=0.9)
        if reset:
            pyautogui.leftClick(reset.x, reset.y)
        play = pyautogui.locateCenterOnScreen('images/play.png', confidence=0.9)
        if play:
            pyautogui.leftClick(play.x, play.y)
    except (ImageNotFoundException, TypeError):
        print("Could not find reset or play button.")

def solve(move_sequence, pos_dict, initial_grid, difficulty):
    for area in move_sequence:
        (top_left, bottom_right) = area
        r1, c1 = top_left
        r2, c2 = bottom_right
        if (r1, c1) not in pos_dict or (r2, c2) not in pos_dict:
            continue
        left1, top1, w1, h1 = pos_dict[(r1, c1)]
        left2, top2, w2, h2 = pos_dict[(r2, c2)]
        start_x = left1 + w1 // 2 - 10
        start_y = top1 + h1 // 2 - 10
        end_x = left2 + w2 // 2 + 10
        end_y = top2 + h2 // 2 + 10
        if initial_grid[r1][c1] == 0:
            continue
        pyautogui.mouseDown(start_x, start_y)
        pyautogui.moveTo(end_x, end_y)
        time.sleep((10-difficulty)*0.08)
        pyautogui.moveRel((1, 1))
        pyautogui.mouseUp()


def scan():
    try:
        one = list(pyautogui.locateAllOnScreen('images/1.png', confidence=0.9))
        two = list(pyautogui.locateAllOnScreen('images/2.png', confidence=0.9))
        three = list(pyautogui.locateAllOnScreen('images/3.png', confidence=0.9))
        four = list(pyautogui.locateAllOnScreen('images/4.png', confidence=0.9))
        five = list(pyautogui.locateAllOnScreen('images/5.png', confidence=0.9))
        six = list(pyautogui.locateAllOnScreen('images/6.png', confidence=0.9))
        seven = list(pyautogui.locateAllOnScreen('images/7.png', confidence=0.9))
        eight = list(pyautogui.locateAllOnScreen('images/8.png', confidence=0.9))
        nine = list(pyautogui.locateAllOnScreen('images/9.png', confidence=0.9))
    except Exception as e:
        print(f"An error occurred during screen scan: {e}")
        return [], [], [], {}
        
    m = {}
    pos_dict = {}
    all_finds = {1: one, 2: two, 3: three, 4: four, 5: five, 6: six, 7: seven, 8: eight, 9: nine}
    
    processed_finds = []
    for num, finds in all_finds.items():
        num_finds = []
        for find in finds:
            num_finds.append((find.left, find.top))
            m[(find.left, find.top)] = num
            pos_dict[(find.left, find.top)] = (find.left, find.top, find.width, find.height)
        processed_finds.append(num_finds)

    if not any(processed_finds):
        print("No number images found on the screen.")
        return [], [], [], {}

    # Filter out empty lists before concatenation
    combined = np.concatenate([finds for finds in processed_finds if finds])
    
    combined = sorted(combined, key=lambda x: (x[0], x[1]))
    result = []
    for i in range(10):
        result.append([0] * 17)
        
    if combined:
        xs = [x for x, y in combined]
        ys = [y for x, y in combined]
        x_reps, x_map = cluster_positions(xs, threshold=20)
        y_reps, y_map = cluster_positions(ys, threshold=20)
        for (x, y) in combined:
            col = x_map[x]
            row = y_map[y]
            if 0 <= row < 10 and 0 <= col < 17:
                result[row][col] = m[(x, y)]
                pos_dict[(row, col)] = pos_dict[(x, y)]
    else:
        x_reps, y_reps = [], []
        
    for row in result:
        print(row)
    return result, x_reps, y_reps, pos_dict

def get_cluster_positions(positions, threshold=20):
    if not positions:
        return [], {}
    sorted_pos = sorted(set(positions))
    clusters = []
    if not sorted_pos:
        return [], {}
    current_cluster = [sorted_pos[0]]
    for pos in sorted_pos[1:]:
        if abs(pos - current_cluster[-1]) <= threshold:
            current_cluster.append(pos)
        else:
            clusters.append(current_cluster)
            current_cluster = [pos]
    clusters.append(current_cluster)
    rep_values = [int(sum(c) / len(c)) for c in clusters]
    pos_to_idx = {}
    for idx, cluster in enumerate(clusters):
        for v in cluster:
            pos_to_idx[v] = idx
    return rep_values, pos_to_idx

def index_to_screen(row, col, x_reps, y_reps):
    if col < len(x_reps) and row < len(y_reps):
        return x_reps[col], y_reps[row]
    return None, None

def contain_or_adjacent_to_zero(initial_grid, top_left, bottom_right):
    (r1, c1) = top_left
    (r2, c2) = bottom_right
    n_rows = len(initial_grid)
    n_cols = len(initial_grid[0])
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            if initial_grid[r][c] == 0:
                return True
    for r in range(r1, r2 + 1):
        if c1 > 0 and initial_grid[r][c1 - 1] == 0:
            return True
        if c2 < n_cols - 1 and initial_grid[r][c2 + 1] == 0:
            return True
    for c in range(c1, c2 + 1):
        if r1 > 0 and initial_grid[r1 - 1][c] == 0:
            return True
        if r2 < n_rows - 1 and initial_grid[r2 + 1][c] == 0:
            return True
    return False