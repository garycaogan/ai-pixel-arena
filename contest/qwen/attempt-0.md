```python
import random
import time

DIR_ORDER = ["up", "down", "left", "right"]
DELTA = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
OPP = {"up": "down", "down": "up", "left": "right", "right": "left"}
DIR_INDEX = {d: i for i, d in enumerate(DIR_ORDER)}
DELTA_TO_DIR = {v: k for k, v in DELTA.items()}
INF = 9999

GRID_W = 0
GRID_H = 0
CELLS = 0
NEIGHBORS = []
DIR_NEXT = []
COORDS = []
LAST_DIR = None


def ensure_grid(w, h):
    global GRID_W, GRID_H, CELLS, NEIGHBORS, DIR_NEXT, COORDS
    if GRID_W == w and GRID_H == h:
        return
    GRID_W = w
    GRID_H = h
    CELLS = w * h
    COORDS = [None] * CELLS
    DIR_NEXT = [None] * CELLS
    NEIGHBORS = [None] * CELLS

    for y in range(h):
        for x in range(w):
            i = y * w + x
            COORDS[i] = (x, y)
            nxt = []
            neigh = []
            for d in DIR_ORDER:
                dx, dy = DELTA[d]
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    ni = ny * w + nx
                else:
                    ni = -1
                nxt.append(ni)
                if ni != -1:
                    neigh.append(ni)
            DIR_NEXT[i] = nxt
            NEIGHBORS[i] = neigh


def direction_between(head, neck):
    if head == neck:
        return None
    hx, hy = COORDS[head]
    nx, ny = COORDS[neck]
    return DELTA_TO_DIR.get((hx - nx, hy - ny))


def body_to_idx(body, w, h):
    out = []
    for p in body:
        x, y = p[0], p[1]
        if 0 <= x < w and 0 <= y < h:
            out.append(y * w + x)
    return out


def flood(start, occ, own_mask, threat, food_mask, target, deadline, block_threat=True):
    visited = bytearray(CELLS)
    visited[start] = 1
    current = [start]
    dist = 0
    total = 0
    safe = 0
    min_food = INF
    tail_found = (target != -1 and start == target)
    pt = time.process_time

    while current:
        if pt() > deadline:
            break
        nxt = []
        for p in current:
            total += 1
            if (not threat[p]) or p == start:
                safe += 1
            if min_food == INF and food_mask[p]:
                min_food = dist
            if target != -1 and p == target:
                tail_found = True

            for nb in NEIGHBORS[p]:
                if visited[nb] or occ[nb] or own_mask[nb]:
                    continue
                if block_threat and threat[nb] and nb != start:
                    continue
                visited[nb] = 1
                nxt.append(nb)

        current = nxt
        dist += 1

    return total, safe, min_food, tail_found


def fallback(state):
    try:
        w = int(state["width"])
        h = int(state["height"])
        you = state.get("you")
        head = None
        for s in state.get("snakes", []):
            if s.get("id") == you:
                body = s.get("body", [])
                if body:
                    head = body[0]
                break

        if head is not None:
            hx, hy = head[0], head[1]

            if LAST_DIR in DELTA:
                dx, dy = DELTA[LAST_DIR]
                if 0 <= hx + dx < w and 0 <= hy + dy < h:
                    return LAST_DIR

            best = None
            best_score = -10**9
            for d in DIR_ORDER:
                dx, dy = DELTA[d]
                nx, ny = hx + dx, hy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    score = -abs(nx * 2 - (w - 1)) - abs(ny * 2 - (h - 1))
                    score += random.random()
                    if score > best_score:
                        best_score = score
                        best = d
            if best is not None:
                return best

        if LAST_DIR in DIR_INDEX:
            return LAST_DIR
    except Exception:
        pass

    return LAST_DIR if LAST_DIR in DIR_INDEX else "up"


def decide_main(state):
    global LAST_DIR

    turn = int(state.get("turn", 1))
    if turn <= 1:
        LAST_DIR = None

    w = int(state["width"])
    h = int(state["height"])
    ensure_grid(w, h)

    deadline = time.process_time() + (0.85 if turn <= 1 else 0.045)

    you = state.get("you")
    snakes = state.get("snakes", [])

    my = None
    for s in snakes:
        if s.get("id") == you:
            my = s
            break

    if my is None:
        return fallback(state)

    raw_body = my.get("body", [])
    if not raw_body:
        return fallback(state)

    my_body = body_to_idx(raw_body, w, h)
    if not my_body:
        return fallback(state)

    my_head = my_body[0]
    my_length = int(my.get("length", len(my_body)))
    my_health = int(my.get("health", 100))
    max_turns = int(state.get("max_turns", 500))
    turns_left = max(0, max_turns - turn)

    food_mask = bytearray(CELLS)
    for p in state.get("food", []):
        try:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                food_mask[y * w + x] = 1
        except Exception:
            pass

    current_dir = None
    if len(my_body) >= 2:
        current_dir = direction_between(my_body[0], my_body[1])
    if current_dir is None:
        current_dir = LAST_DIR

    opp_dir = OPP.get(current_dir) if current_dir else None
    candidate_dirs = [d for d in DIR_ORDER if d != opp_dir]
    if not candidate_dirs:
        candidate_dirs = DIR_ORDER[:]

    my_tail_stays = len(my_body) >= 2 and my_body[-1] == my_body[-2]

    own_full = bytearray(CELLS)
    for p in my_body:
        own_full[p] = 1

    own_move = bytearray(CELLS)
    for p in my_body[:-1]:
        own_move[p] = 1

    own_space_normal = bytearray(CELLS)
    for p in my_body[:-2]:
        own_space_normal[p] = 1

    own_space_stay = bytearray(CELLS)
    for p in my_body[:-1]:
        own_space_stay[p] = 1

    occ_others = bytearray(CELLS)
    occ_others_space = bytearray(CELLS)
    threat_fatal = bytearray(CELLS)
    threat_win = bytearray(CELLS)
    enemy_head_coords = []
    max_enemy_len = 0

    for s in snakes:
        if s.get("id") == you:
            continue

        raw = s.get("body", [])
        if not raw:
            continue

        body = body_to_idx(raw, w, h)
        if not body:
            continue

        length = int(s.get("length", len(body)))
        if length > max_enemy_len:
            max_enemy_len = length

        head = body[0]
        enemy_head_coords.append(COORDS[head])

        tail_stays = len(body) >= 2 and body[-1] == body[-2]
        mark_imm = body if tail_stays else body[:-1]
        mark_space = body if tail_stays else body[:-2]

        for p in mark_imm:
            occ_others[p] = 1
        for p in mark_space:
            occ_others_space[p] = 1

        edir = None
        if len(body) >= 2:
            edir = direction_between(body[0], body[1])
        eopp = OPP.get(edir) if edir else None

        emark = set(mark_imm)
        for di, dname in enumerate(DIR_ORDER):
            if eopp is not None and dname == eopp:
                continue
            ni = DIR_NEXT[head][di]
            if ni == -1:
                continue
            if ni in emark:
                continue
            if length >= my_length:
                threat_fatal[ni] = 1
            else:
                threat_win[ni] = 1

    best_dir = None
    best_score = -10**30

    desperate = (my_health <= 25 and turns_left >= my_health)
    fatal_penalty = 1_000_000 if desperate else 5_000_000

    tail_bonus = 60_000 if desperate else 180_000
    if my_health <= 45 and not desperate and turns_left > 30:
        tail_bonus = 100_000

    i_am_longest = my_length >= max_enemy_len

    fw = 1500
    if my_health < 60:
        fw *= 2
    if my_health < 35:
        fw *= 2

    if turns_left < 40:
        if i_am_longest:
            fw = int(fw * 1.1)
        else:
            fw *= 2
    if turns_left < 15 and not i_am_longest:
        fw *= 2
    if desperate:
        fw *= 2

    min_space_threshold = max(4, min(80, my_length))

    for d in candidate_dirs:
        di = DIR_INDEX[d]
        ni = DIR_NEXT[my_head][di]
        if ni == -1:
            continue

        eating = bool(food_mask[ni])
        imm_mask = own_full if (eating or my_tail_stays) else own_move

        if occ_others[ni] or imm_mask[ni]:
            continue

        if time.process_time() > deadline:
            if best_dir is None:
                best_dir = d
            break

        if eating:
            space_mask = own_full
            target = -1
        elif my_tail_stays:
            space_mask = own_space_stay
            target = -1
        else:
            space_mask = own_space_normal
            target = my_body[-2] if len(my_body) >= 2 else -1

        total_space, safe_space, food_dist, tail_found = flood(
            ni,
            occ_others_space,
            space_mask,
            threat_fatal,
            food_mask,
            target,
            deadline,
            block_threat=not desperate,
        )

        fatal = bool(threat_fatal[ni])
        win = bool(threat_win[ni])

        hx, hy = COORDS[ni]
        min_enemy = 99
        for ex, ey in enemy_head_coords:
            md = abs(hx - ex) + abs(hy - ey)
            if md < min_enemy:
                min_enemy = md

        center = abs(hx * 2 - (w - 1)) + abs(hy * 2 - (h - 1))

        space_metric = safe_space if not desperate else max(safe_space, total_space // 2)

        score = 0.0
        if fatal:
            score -= fatal_penalty
        if win:
            score += 20_000 if i_am_longest else 5_000

        if tail_found:
            score += tail_bonus

        if space_metric < min_space_threshold:
            score -= 350_000

        score += space_metric * 80 + total_space * 5

        food_eff = food_dist if food_dist < INF else 200
        score -= food_eff * fw

        score += min_enemy * (30 if my_health > 50 else 10)
        score -= center * 5
        score += random.random()

        if score > best_score:
            best_score = score
            best_dir = d

    if best_dir is not None:
        return best_dir

    dirs_to_try = candidate_dirs if candidate_dirs else DIR_ORDER
    best = None
    best_val = -10**9

    for d in dirs_to_try:
        di = DIR_INDEX[d]
        ni = DIR_NEXT[my_head][di]
        val = random.random()

        if ni != -1:
            val += 10
            if not occ_others[ni]:
                val += 5
            if not own_full[ni]:
                val += 3
            if not threat_fatal[ni]:
                val += 2
            hx, hy = COORDS[ni]
            val -= 0.01 * (abs(hx * 2 - (w - 1)) + abs(hy * 2 - (h - 1)))

        if val > best_val:
            best_val = val
            best = d

    if best is not None:
        return best

    if current_dir in DIR_INDEX:
        return current_dir

    return LAST_DIR if LAST_DIR in DIR_INDEX else "up"


def decide(state):
    global LAST_DIR
    try:
        result = decide_main(state)
        if result not in DIR_INDEX:
            result = LAST_DIR if LAST_DIR in DIR_INDEX else "up"
        LAST_DIR = result
        return result
    except Exception:
        result = fallback(state)
        if result not in DIR_INDEX:
            result = "up"
        LAST_DIR = result
        return result
```

策略：单步安全 + 洪泛评估。先按“对手下一回合仍占用的身体”排除必死格，会动的尾巴视为可通过；把长度不短于我的敌头下一步可撞的格子标为致命风险。对每个候选方向做 BFS：统计可活动空间、是否能绕回自己的尾巴、到最近食物距离。正常时优先无致命碰撞、保持尾部可达与大空间；饥饿或残局时提高抢食物权重，必要时降低风险厌恶。