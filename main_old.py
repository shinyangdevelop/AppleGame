from tensorflow.python.debug.lib.source_utils import guess_is_tensorflow_py_library

from core import scan, restart_game
from search import iterative_solver, n_iterative_solver, r_iteration_solver, h_iteration_solver, exhaustive_solver
import pyautogui
import time
import numpy

min_score = 120
difficulty = 10

def run(ex=False):
    initial_grid, x_reps, y_reps, pos_dict = scan()
    max_score, best_move_sequence = 0,0
    if not ex:
        n_max_score, n_best_move_sequence = n_iterative_solver(initial_grid, guess_limit=50000)
        max_score, best_move_sequence = iterative_solver(initial_grid, guess_limit=50000)
        r_max_score, r_best_move_sequence = r_iteration_solver(initial_grid, max_iteration=50000)
        h_max_score, h_best_move_sequence = h_iteration_solver(initial_grid, n_iteration=50, branches=10)
        print(f"NNNN: {n_max_score}, RRRR: {r_max_score}, HHHH: {h_max_score}, Iterative: {max_score}")
        if n_max_score > max_score and n_max_score > r_max_score and n_max_score > h_max_score:
            max_score = n_max_score
            best_move_sequence = n_best_move_sequence
            print("NNNN")
        elif r_max_score > max_score and r_max_score > h_max_score:
            max_score = r_max_score
            best_move_sequence = r_best_move_sequence
            print("RRRR")
        elif h_max_score > max_score:
            max_score = h_max_score
            best_move_sequence = h_best_move_sequence
            print("HHHH")
        else:
            print("____")
    else:
        max_score, best_move_sequence = h_iteration_solver(initial_grid, n_iteration=100, branches=20)


    print(f"탐색 완료. 최고 점수: {max_score}")
    print(f"최적의 이동 순서(총 {len(best_move_sequence)}회):")
    for i, area in enumerate(best_move_sequence):
        print(f"  {i + 1}. {area}")
    if max_score < min_score:
        print("점수가 너무 낮아 재시작합니다.")
        return 0
    print("\n최적의 순서대로 드래그를 시작합니다.")
    for area in best_move_sequence:
        (top_left, bottom_right) = area
        r1, c1 = top_left
        r2, c2 = bottom_right
        # 드래그 시작점: 왼쪽 위 사과의 중앙에서 약간 더 위/왼쪽
        # 드래그 끝점: 오른쪽 아래 사과의 중앙에서 약간 더 아래/오른쪽
        if (r1, c1) not in pos_dict or (r2, c2) not in pos_dict:
            print(f"좌표 정보 없음: ({r1},{c1}) 또는 ({r2},{c2})")
            continue
        left1, top1, w1, h1 = pos_dict[(r1, c1)]
        left2, top2, w2, h2 = pos_dict[(r2, c2)]
        start_x = left1 + w1 // 2 - 10
        start_y = top1 + h1 // 2 - 10
        end_x = left2 + w2 // 2 + 10
        end_y = top2 + h2 // 2 + 10
        # 시작점이 0(빈칸)이면 건너뜀
        if initial_grid[r1][c1] == 0:
            print(f"시작점 ({r1},{c1})이 0이므로 건너뜀")
            continue
        print(f"드래그 실행: ({r1},{c1})~({r2},{c2}) → 화면좌표 ({start_x},{start_y})~({end_x},{end_y})")
        pyautogui.mouseDown(start_x, start_y)
        pyautogui.moveTo(end_x, end_y)
        time.sleep((10 - difficulty) * 0.08)
        pyautogui.moveRel(1, 1)
        pyautogui.mouseUp()
    print("완료.")
    return 1

if __name__ == "__main__":
    code = 0
    while code == 0:
        restart_game()
        code = run(ex=True)
