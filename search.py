import random
from util import contain_or_adjacent_to_zero

def find_all_sum_10_areas(result):
    """
    모든 (임의 크기) 직사각형에 대해 합이 10인 영역을 찾아 반환합니다.
    빠른 합 계산을 위해 2D 누적합(prefix sum)을 사용합니다.
    반환 형식: [(priority, (r1,c1), (r2,c2)), ...]
    priority는 해당 영역 내에 값이 0 또는 1인 칸의 개수(원래 코드 의미와 동일).
    """
    found = []
    n_rows = len(result)
    if n_rows == 0:
        return found
    n_cols = len(result[0])

    # 2D 누적합 준비 (크기: (n_rows+1) x (n_cols+1))
    ps = [[0] * (n_cols + 1) for _ in range(n_rows + 1)]
    pc = [[0] * (n_cols + 1) for _ in range(n_rows + 1)]  # priority 누적합(0 또는 1 카운트)

    for i in range(n_rows):
        for j in range(n_cols):
            val = result[i][j]
            is_priority = 1 if (val == 1 or val == 0) else 0
            ps[i + 1][j + 1] = val + ps[i][j + 1] + ps[i + 1][j] - ps[i][j]
            pc[i + 1][j + 1] = is_priority + pc[i][j + 1] + pc[i + 1][j] - pc[i][j]

    # 모든 가능한 사각형을 검사 (r1,c1)부터 (r2,c2)까지
    for r1 in range(0, n_rows):
        for r2 in range(r1, n_rows):
            for c1 in range(0, n_cols):
                for c2 in range(c1, n_cols):
                    # 누적합을 이용해 합 계산
                    sub_sum = ps[r2 + 1][c2 + 1] - ps[r1][c2 + 1] - ps[r2 + 1][c1] + ps[r1][c1]
                    if sub_sum == 10:
                        priority = pc[r2 + 1][c2 + 1] - pc[r1][c2 + 1] - pc[r2 + 1][c1] + pc[r1][c1]
                        found.append((priority, (r1, c1), (r2, c2)))

    # 기존 정렬 기준 유지: priority 오름차순, 면적은 내림차순
    found.sort(key=lambda x: (x[0], -((x[2][1] - x[1][1] + 1) * (x[2][0] - x[1][0] + 1))))
    return found


def n_iterative_solver(initial_grid, guess_limit):
    print("n")
    max_score = 0
    best_move_sequence = []
    stack = [(initial_grid, [], 0)]
    iteration = 0
    while iteration < guess_limit:
        if len(stack) == 0:
            stack = [(initial_grid, [], 0)]
        (current_grid, move_sequence, current_score) = stack.pop()
        available_action = find_all_sum_10_areas(current_grid)
        if random.randint(0, 9) * iteration % 10 <= 2:
            iteration += 0.25
            continue
        if not available_action:
            if current_score > max_score:
                max_score = current_score
                best_move_sequence = move_sequence
                stack = stack[:len(stack) - min(random.randint(1, 5 ** 5), len(stack)) + 1]
            iteration += 1
            continue
        possible_actions = [action for action in available_action if
                            contain_or_adjacent_to_zero(current_grid, action[1], action[2])]
        if not possible_actions:
            possible_actions = available_action
        possible_actions.sort(key=lambda x: (x[0]))
        for (priority, top_left, bottom_right) in possible_actions[:5]:
            new_grid = [row[:] for row in current_grid]
            (r1, c1) = top_left
            (r2, c2) = bottom_right
            add_score = 0
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if new_grid[r][c] != 0:
                        add_score += 1
                    new_grid[r][c] = 0
            new_move_sequence = move_sequence + [(top_left, bottom_right)]
            new_score = current_score + add_score
            stack.append((new_grid, new_move_sequence, new_score))
        iteration += 1
    return max_score, best_move_sequence


def iterative_solver(initial_grid, guess_limit):
    print("_")
    max_score = 0
    best_move_sequence = []
    stack = [(initial_grid, [], 0)]
    iteration = 0
    while iteration < guess_limit:
        if len(stack) == 0:
            stack = [(initial_grid, [], 0)]
        (current_grid, move_sequence, current_score) = stack.pop()
        available_action = find_all_sum_10_areas(current_grid)
        if not available_action:
            if current_score < 100:
                emergency_action = find_all_sum_10_areas(initial_grid)
                k = random.randint(0, len(emergency_action) - 1)
                (top_left, bottom_right) = emergency_action[k][1], emergency_action[k][2]
                current_grid = initial_grid
                new_grid = [row[:] for row in current_grid]
                (r1, c1) = top_left
                (r2, c2) = bottom_right
                add_score = 0
                for r in range(r1, r2 + 1):
                    for c in range(c1, c2 + 1):
                        if new_grid[r][c] != 0:
                            add_score += 1
                        new_grid[r][c] = 0
                new_move_sequence = [(top_left, bottom_right)]
                new_score = add_score
                stack = [(new_grid, new_move_sequence, new_score)]  # ← 수정됨
                iteration += 1
                continue
            if current_score > max_score:
                max_score = current_score
                best_move_sequence = move_sequence
                for i in range(1, min(random.randint(1, 5 ** 3), len(stack))):
                    stack.pop()
            iteration += 1
            continue
        possible_actions = [action for action in available_action if
                            contain_or_adjacent_to_zero(current_grid, action[1], action[2])]
        if not possible_actions:
            possible_actions = available_action
        possible_actions.sort(key=lambda x: (x[0]))
        for (priority, top_left, bottom_right) in possible_actions[:8]:
            new_grid = [row[:] for row in current_grid]
            (r1, c1) = top_left
            (r2, c2) = bottom_right
            add_score = 0
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if new_grid[r][c] != 0:
                        add_score += 1
                    new_grid[r][c] = 0
            new_move_sequence = move_sequence + [(top_left, bottom_right)]
            new_score = current_score + add_score
            stack.append((new_grid, new_move_sequence, new_score))  # ← 수정됨
        iteration += 1
    return max_score, best_move_sequence


def r_iteration_solver(initial_grid, max_iteration):
    print("r")
    max_score = 0
    best_move_sequence = []
    stack = [(initial_grid, [], 0)]
    iteration = 0
    while stack and iteration < max_iteration:
        current_grid, move_sequence, current_score = stack.pop()
        available_action = find_all_sum_10_areas(current_grid)
        if not available_action:
            if current_score > max_score:
                max_score = current_score
                best_move_sequence = move_sequence
            iteration += 1
            continue
        for (_, top_left, bottom_right) in available_action:
            new_grid = [row[:] for row in current_grid]
            r1, c1 = top_left
            r2, c2 = bottom_right
            add_score = 0
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if new_grid[r][c] != 0:
                        add_score += 1
                    new_grid[r][c] = 0
            new_move_sequence = move_sequence + [(top_left, bottom_right)]
            new_score = current_score + add_score
            stack.append((new_grid, new_move_sequence, new_score))
        iteration += 1
    return max_score, best_move_sequence


def h_iteration_solver(initial_grid, branches, n_iteration):
    """
    휴리스틱 탐색 함수 (hybrid random + priority).
    - initial_grid: 시작 그리드
    - max_iteration: 전체 행동(노드 처리) 제한
    - branches: 분화 시 생성할 분기 수
    - n_iteration: 분화 빈도(몇 번 진행할 때마다 분화할지)

    동작 요약:
    1) 현재 상태에서 우선순위에 따라 한 가지 후보만 고르고 계속 전개한다.
    2) steps가 n_iteration마다(즉 일정 간격마다) 분화 시점이 되어야 하면 가능한 액션들을 섞어 최대 branches개를 스택에 넣어 다른 경로들을 나중에 탐색하도록 한다.
    3) 분화할 때도 현재 경로는 그중 하나를 선택하여 즉시 계속 전개한다.
    4) 가능한 액션 선택 시에는 contain_or_adjacent_to_zero 필터를 우선 적용한다(없으면 전체 사용).
    """
    print("h")
    max_score = 0
    best_move_sequence = []
    stack = [(initial_grid, [], 0)]
    iteration = 0
    random_gen = random.Random()

    # 안전한 기본값
    if branches < 1:
        branches = 1
    if n_iteration < 1:
        n_iteration = 10

    # 메인 루프: 스택이 비거나 iteration 초과 시 종료
    while stack:
        current_grid, move_sequence, current_score = stack.pop()
        # 각 스택 항목마다 한 경로를 휴리스틱하게 전개
        steps = 0
        grid = [row[:] for row in current_grid]
        seq = move_sequence[:]
        score = current_score

        while True:
            available_action = find_all_sum_10_areas(grid)
            if not available_action:
                # 종료 상태: 점수 갱신
                if score > max_score:
                    max_score = score
                    best_move_sequence = seq[:]
                break

            # 가능한 액션에 대해 0 인접성 필터 적용
            possible_actions = [action for action in available_action if contain_or_adjacent_to_zero(grid, action[1], action[2])]
            if not possible_actions:
                possible_actions = available_action[:]

            # 분화 시점 판단: 일정 스텝마다 분화
            do_branch = (steps > 0 and steps % n_iteration == 0)

            if do_branch:
                # 무작위로 섞고 최대 branches개를 스택에 추가
                shuffled = possible_actions[:]
                random_gen.shuffle(shuffled)
                # 제한: branches보다 적을 수 있음
                chosen_for_stack = shuffled[:min(branches, len(shuffled))]

                for (priority, top_left, bottom_right) in chosen_for_stack:
                    # 각 분기별로 새로운 그리드 계산하여 스택에 넣음
                    new_grid = [row[:] for row in grid]
                    (r1, c1) = top_left
                    (r2, c2) = bottom_right
                    add_score = 0
                    for r in range(r1, r2 + 1):
                        for c in range(c1, c2 + 1):
                            if new_grid[r][c] != 0:
                                add_score += 1
                            new_grid[r][c] = 0
                    new_move_sequence = seq + [(top_left, bottom_right)]
                    new_score = score + add_score
                    stack.append((new_grid, new_move_sequence, new_score))
                    iteration += 1
                # 현재 경로는 우선순위 기반으로 하나만 선택해서 계속 진행
                possible_actions.sort(key=lambda x: (x[0]))
                chosen = possible_actions[0]
            else:
                # 분화 전: 우선순위만으로 단일 선택
                possible_actions.sort(key=lambda x: (x[0]))
                chosen = possible_actions[0]

            # 선택된 행동을 현재 경로에 적용
            (_, top_left, bottom_right) = chosen
            new_grid = [row[:] for row in grid]
            (r1, c1) = top_left
            (r2, c2) = bottom_right
            add_score = 0
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if new_grid[r][c] != 0:
                        add_score += 1
                    new_grid[r][c] = 0

            # 업데이트
            seq = seq + [(top_left, bottom_right)]
            score = score + add_score
            grid = new_grid

            steps += 1
            iteration += 1

        # while -> 다음 스택 항목으로 넘어감
    return max_score, best_move_sequence


def exhaustive_solver(initial_grid, max_calls):
    """
    완전 탐색(exhaustive DFS)으로 가능한 모든 직사각형 제거 시퀀스를 탐색하여
    최대 점수(직사각형 안의 0이 아닌 숫자 개수 합)를 찾습니다.

    인자:
    - initial_grid: 2D 리스트(int)
    - max_calls: 탐색 노드(재귀 호출) 상한 — 너무 오래 돌아가지 않도록 제한

    반환: (max_score, best_move_sequence) — best_move_sequence는 [(r1,c1),(r2,c2), ...]
    """
    print("e")
    # 전처리/안전성
    if not initial_grid or not initial_grid[0]:
        return 0, []

    # 헬퍼: 그리드를 튜플(immutable)로 변환하여 해시 가능하게 함
    def grid_to_key(g):
        return tuple(tuple(row) for row in g)

    best_score = 0
    best_sequence = []
    calls = 0
    memo = {}  # grid_key -> best score seen for that grid (가지치기용)

    # 내부 DFS 재귀
    def dfs(grid, sequence, score):
        nonlocal best_score, best_sequence, calls
        calls += 1
        if calls > max_calls:
            return
        key = grid_to_key(grid)
        # 가지치기: 같은 그리드에서 이미 더 높은 점수를 본 경우 중단
        prev_best = memo.get(key)
        if prev_best is not None and score <= prev_best:
            return
        memo[key] = score

        # 업데이트 최고
        if score > best_score:
            best_score = score
            best_sequence = sequence[:]

        # 가능한 행동 모두 구함
        actions = find_all_sum_10_areas(grid)
        if not actions:
            return

        # 완전 탐색: 모든 가능한 행동에 대해 재귀
        for (priority, top_left, bottom_right) in actions:
            r1, c1 = top_left
            r2, c2 = bottom_right
            # 적용: 해당 영역의 0이 아닌 갯수를 세고 0으로 만듬
            new_grid = [row[:] for row in grid]
            add = 0
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if new_grid[r][c] != 0:
                        add += 1
                        new_grid[r][c] = 0
            if add == 0:
                # 의미없는 행동(영역이 이미 0으로만 구성) 건너뜀
                continue
            dfs(new_grid, sequence + [(top_left, bottom_right)], score + add)
            if calls > max_calls:
                return

    # 시작
    start_grid = [row[:] for row in initial_grid]
    dfs(start_grid, [], 0)
    return best_score, best_sequence
