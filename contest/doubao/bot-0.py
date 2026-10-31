import random
from collections import deque

DIRS = [("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))]

def bfs_single(start, obstacles, width, height):
    sx, sy = start
    dist = [[float('inf')] * height for _ in range(width)]
    if not (0 <= sx < width and 0 <= sy < height) or (sx, sy) in obstacles:
        return dist
    q = deque([(sx, sy)])
    dist[sx][sy] = 0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while q:
        x, y = q.popleft()
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacles and dist[nx][ny] > dist[x][y] + 1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))
    return dist

def bfs_multi(starts, obstacles, width, height):
    dist = [[float('inf')] * height for _ in range(width)]
    q = deque()
    for (x, y) in starts:
        if 0 <= x < width and 0 <= y < height and (x, y) not in obstacles:
            dist[x][y] = 0
            q.append((x, y))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while q:
        x, y = q.popleft()
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacles and dist[nx][ny] > dist[x][y] + 1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))
    return dist

def compute_space_map(obstacles, width, height):
    space_map = [[0] * height for _ in range(width)]
    visited = set(obstacles)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for x in range(width):
        for y in range(height):
            if (x, y) not in visited:
                q = deque()
                q.append((x, y))
                visited.add((x, y))
                component = []
                while q:
                    cx, cy = q.popleft()
                    component.append((cx, cy))
                    for dx, dy in dirs:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            q.append((nx, ny))
                size = len(component)
                for (cx, cy) in component:
                    space_map[cx][cy] = size
    return space_map

def decide(state):
    width = state["width"]
    height = state["height"]
    my_id = state["you"]
    me = next(s for s in state["snakes"] if s["id"] == my_id)
    my_head = tuple(me["body"][0])
    my_neck = tuple(me["body"][1])
    my_length = me["length"]
    my_health = me["health"]
    others = [s for s in state["snakes"] if s["id"] != my_id]
    foods = [tuple(f) for f in state["food"]]
    turn = state["turn"]
    max_turns = state["max_turns"]

    all_body_but_last = set()
    for snake in state["snakes"]:
        for pos in snake["body"][:-1]:
            all_body_but_last.add(tuple(pos))

    forbidden_dir = None
    if my_head != my_neck:
        dx = my_head[0] - my_neck[0]
        dy = my_head[1] - my_neck[1]
        for dir_name, (ddx, ddy) in DIRS:
            if ddx == -dx and ddy == -dy:
                forbidden_dir = dir_name
                break

    candidates = []
    for dir_name, (dx, dy) in DIRS:
        if dir_name == forbidden_dir:
            continue
        nx = my_head[0] + dx
        ny = my_head[1] + dy
        new_head = (nx, ny)
        if 0 <= nx < width and 0 <= ny < height and new_head not in all_body_but_last:
            candidates.append((dir_name, new_head))

    if not candidates:
        if my_head != my_neck:
            dx = my_head[0] - my_neck[0]
            dy = my_head[1] - my_neck[1]
            for dir_name, (ddx, ddy) in DIRS:
                if ddx == dx and ddy == dy:
                    return dir_name
        return "up"

    my_dist = bfs_single(my_head, all_body_but_last, width, height)
    min_food_dist = float('inf')
    for (fx, fy) in foods:
        if my_dist[fx][fy] < min_food_dist:
            min_food_dist = my_dist[fx][fy]
    is_hungry = my_health <= (min_food_dist + 10) if min_food_dist != float('inf') else True

    preferred_foods = []
    for (fx, fy) in foods:
        d_me = my_dist[fx][fy]
        if d_me == float('inf'):
            continue
        can_take = True
        for other in others:
            ohx, ohy = other["body"][0]
            d_other = abs(ohx - fx) + abs(ohy - fy)
            if d_other < d_me:
                can_take = False
                break
            if d_other == d_me and other["length"] >= my_length:
                can_take = False
                break
        if can_take:
            preferred_foods.append((fx, fy))
    if not preferred_foods:
        preferred_foods = foods

    preferred_food_dist = bfs_multi(preferred_foods, all_body_but_last, width, height)
    space_map = compute_space_map(all_body_but_last, width, height)

    other_legal_heads = {}
    for other in others:
        oid = other["id"]
        obody = other["body"]
        ohead = tuple(obody[0])
        oneck = tuple(obody[1])
        o_forbidden = None
        if ohead != oneck:
            odx = ohead[0] - oneck[0]
            ody = ohead[1] - oneck[1]
            for _, (ddx, ddy) in DIRS:
                if ddx == -odx and ddy == -ody:
                    o_forbidden = (ddx, ddy)
                    break
        legal = set()
        for _, (dx, dy) in DIRS:
            if (dx, dy) == o_forbidden:
                continue
            nx = ohead[0] + dx
            ny = ohead[1] + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in all_body_but_last:
                legal.add((nx, ny))
        other_legal_heads[oid] = legal

    scored = []
    endgame = (max_turns - turn) < 50
    for dir_name, new_head in candidates:
        high_risk = False
        for other in others:
            if other["length"] >= my_length and new_head in other_legal_heads[other["id"]]:
                high_risk = True
                break

        attack_bonus = 0
        for other in others:
            if other["length"] < my_length and new_head in other_legal_heads[other["id"]]:
                attack_bonus += 50

        space = space_map[new_head[0]][new_head[1]]
        d_food = preferred_food_dist[new_head[0]][new_head[1]]
        d_food = 1000 if d_food == float('inf') else d_food

        longer_dist = float('inf')
        for other in others:
            if other["length"] > my_length:
                ohx, ohy = other["body"][0]
                dist = abs(new_head[0] - ohx) + abs(new_head[1] - ohy)
                if dist < longer_dist:
                    longer_dist = dist
        distance_to_longer = longer_dist if longer_dist != float('inf') else 1000

        score = 0
        if endgame:
            score += space * 20
            score += distance_to_longer * 5
            score += attack_bonus * 2
            score += 1000 / (d_food + 1) if is_hungry else 100 / (d_food + 1)
            if high_risk:
                score -= 1000
        else:
            if is_hungry:
                score += 1000 / (d_food + 1)
                score += space * 2
                score += attack_bonus * 1
                score += distance_to_longer * 1
                if high_risk:
                    score -= 2000
            else:
                score += space * 10
                score += attack_bonus * 3
                score += distance_to_longer * 2
                score += 100 / (d_food + 1)
                if high_risk:
                    score -= 100

        scored.append((score, random.random(), dir_name))

    scored.sort(reverse=True)
    return scored[0][2]
