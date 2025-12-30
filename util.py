import numpy as np
import requests

def cluster_positions(positions, threshold=20):
    """
    positions: list of int (x 또는 y 좌표)
    threshold: 같은 그룹으로 묶을 최대 거리(픽셀)
    return: 정렬된 대표값 리스트, 각 좌표의 인덱스 매핑 dict
    """
    sorted_pos = sorted(set(positions))
    clusters = []
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

def send_data(data):
    URL = "localhost:3000"
    payload = {'data': data}
    response = requests.post(URL, json=payload)
    print(response.json())