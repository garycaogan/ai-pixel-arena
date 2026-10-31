```python
import random
import time
from collections import deque

DIRS = ("up", "down", "left", "right")
DELTA = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
OPP = {"up": "down", "down": "up", "left": "right", "right": "left"}

def _dir_of(body):
    if len(body) < 2 or body[0] == body[1]:
        return None
    dx = body[0][0] - body[1][0]
    dy = body[0][1] - body[1][1]
    for name, (sx, sy) in DELTA.items():
        if (dx, dy) == (sx, sy):
            return name
    return None

def _advance(body, nh, food):
    nb = [nh] + body[:-1]
    if nh in food:
        nb.append(nb[-1])
    return nb

def _tail_cells_remaining(body):
    """Cells still occupied after this snake's tail shrink (before its new head)."""
    if len(body) >= 2 and body[-1] != body[-2]:
        return body[:-1]
    return body

def _flood(start, blocked, w, h):
    if not (0 <= start[0] < w and 0 <= start[1] < h):
        return 0
    seen = {start}
    q = deque([start])
    n = 0
    while q:
        x, y = q.popleft()
        n += 1
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            p = (nx, ny)
            if p in seen or p in blocked:
                continue
            seen.add(p)
            q.append(p)
    return n

def _nearest_food(start, blocked, food, w, h):
    if start in food:
        return 0
    seen = {start}
    q = deque([(start, 0)])
    while q:
        (x, y), d = q.popleft()
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            p = (nx, ny)
            if p in seen or p in blocked:
                continue
            if p in food:
                return d + 1
            seen.add(p)
            q.append((p, d + 1))
    return 10 ** 6

def _legal_targets(body, w, h):
    banned = OPP.get(_dir_of(body))
    hx, hy = body[0]
    out = []
    for name in DIRS:
        if name == banned:
            continue
        dx, dy = DELTA[name]
        nh = (hx + dx, hy + dy)
        if 0 <= nh[0] < w and 0 <= nh[1] < h:
            out.append((name, nh))
    return out

def _static_blocked(snakes, you):
    blocked = set()
    for s in snakes:
        body = [tuple(p) for p in s["body"]]
        cells = _tail_cells_remaining(body)
        if s["id"] == you:
            blocked.update(cells)
        else:
            blocked.update(cells)
    return blocked

def _heuristic(state, me, others, food, w, h):
    body = [tuple(p) for p in me["body"]]
    my_len = me["length"]
    health = me["health"]
    head = body[0]
    food_set = set(food)
    banned = OPP.get(_dir_of(body))

    blocked = set()
    for s in others:
        blocked.update(_tail_cells_remaining([tuple(p) for p in s["body"]]))
    blocked.update(_tail_cells_remaining(body))

    # cells a threatening enemy head can enter this turn, and max arrival length
    threat_len = {}
    near_longer = []
    for s in others:
        ob = [tuple(p) for p in s["body"]]
        olen = s["length"]
        near_longer.append((ob[0], olen))
        for _, nh in _legal_targets(ob, w, h):
            alen = olen + (1 if nh in food_set else 0)
            prev = threat_len.get(nh, 0)
            if alen > prev:
                threat_len[nh] = alen

    cx, cy = (w - 1) / 2, (h - 1) / 2
    best = None
    best_s = -10 ** 18
    options = []
    for name in DIRS:
        if name == banned:
            continue
        dx, dy = DELTA[name]
        nh = (head[0] + dx, head[1] + dy)
        options.append((name, nh))
    if not options:
        return _dir_of(body) or "up"

    for name, nh in options:
        if not (0 <= nh[0] < w and 0 <= nh[1] < h) or nh in blocked:
            score = -10 ** 17
        else:
            ate = nh in food_set
            new_len = my_len + (1 if ate else 0)
            tlen = threat_len.get(nh, 0)
            # flood obstacles: everyone remaining, my new head not blocking the fill start
            area = _flood(nh, blocked, w, h)
            fd = _nearest_food(nh, blocked, food_set, w, h)
            score = area * 120 + new_len * 8
            score -= abs(nh[0] - cx) + abs(nh[1] - cy)
            if area < new_len:
                score -= 80000
            elif area < new_len * 2:
                score -= 8000
            # starvation: must reach food in <= health moves
            if fd > health:
                score -= 200000
            elif fd > health - 6:
                score -= (fd - (health - 6)) * 4000
            hungry = health < 45 or fd + 8 >= health
            if hungry:
                score -= fd * 350
            else:
                score -= min(fd, 40) * 6
            if ate and fd == 0:
                # immediate eat bonus scaled by hunger and whether food is contested
                contested = tlen >= new_len
                if not contested:
                    score += 2500 if hungry else 400
            if tlen > new_len:
                score -= 500000
            elif tlen == new_len:
                score -= 500000  # equal heads both die
            elif tlen > 0:
                score += 800  # shorter snake dies, we live
            # keep distance from longer or equal heads
            for eh, elen in near_longer:
                dist = abs(nh[0] - eh[0]) + abs(nh[1] - eh[1])
                if elen >= new_len:
                    if dist <= 1:
                        score -= 12000
                    elif dist == 2:
                        score -= 2500
                elif dist == 0:
                    score -= 10 ** 8
            # don't step on a cell a longer snake is sitting on as future neck — already in blocked
            # prefer continuing if scores tie (stability)
            if name == _dir_of(body):
                score += 3
        if score > best_s + 1e-9:
            best_s = score
            best = name
        elif abs(score - best_s) < 1e-6:
            if random.random() < 0.5:
                best = name
    return best or "up"

def _search_duel(state, me, opp, food, w, h):
    """Adversarial search for 1v1. Returns a direction."""
    my_body = [tuple(p) for p in me["body"]]
    op_body = [tuple(p) for p in opp["body"]]
    food_set = set(food)
    deadline = time.perf_counter() + 0.028
    nodes = [0]

    def obstacles(mb, ob):
        blocked = set(_tail_cells_remaining(mb))
        blocked.update(_tail_cells_remaining(ob))
        return blocked

    def evaluate(mb, ob, mh, oh, food_s):
        blocked = obstacles(mb, ob)
        # tails that leave are not walls; heads are inside remaining cells
        my_area = _flood(mb[0], blocked - {mb[0]}, w, h)
        op_area = _flood(ob[0], blocked - {ob[0]}, w, h)
        my_len = len(mb)
        op_len = len(ob)
        fd = _nearest_food(mb[0], blocked - {mb[0]}, food_s, w, h)
        ofd = _nearest_food(ob[0], blocked - {ob[0]}, food_s, w, h)
        score = (my_area - op_area) * 40
        score += (my_len - op_len) * 25
        if my_area < my_len:
            score -= 20000
        if op_area < op_len:
            score += 20000
        if fd > mh:
            score -= 100000
        elif mh < 50:
            score -= fd * 80
        else:
            score -= min(fd, 30) * 4
        if ofd > oh:
            score += 15000
        elif oh < 40:
            score += ofd * 20
        # foods I uniquely reach
        return score

    def resolve(mb, ob, mh, oh, food_s, mnh, onh):
        m_oob = not (0 <= mnh[0] < w and 0 <= mnh[1] < h)
        o_oob = not (0 <= onh[0] < w and 0 <= onh[1] < h)
        m_ate = (not m_oob) and mnh in food_s
        o_ate = (not o_oob) and onh in food_s
        mb2 = _advance(mb, mnh, food_s) if not m_oob else None
        ob2 = _advance(ob, onh, food_s) if not o_oob else None
        m_dead = m_oob or ((mh - 1) <= 0 and not m_ate)
        o_dead = o_oob or ((oh - 1) <= 0 and not o_ate)
        if not m_oob and not o_oob and mnh == onh:
            if len(mb2) > len(ob2):
                o_dead = True
            elif len(mb2) < len(ob2):
                m_dead = True
            else:
                m_dead = o_dead = True
        if not m_dead:
            # hit any body except heads
            if mnh in mb2[1:]:
                m_dead = True
            elif ob2 is not None and mnh in ob2[1:]:
                m_dead = True
        if not o_dead:
            if onh in ob2[1:]:
                o_dead = True
            elif mb2 is not None and onh in mb2[1:]:
                o_dead = True
        nf = food_s
        if (m_ate or o_ate) and not (m_dead and o_dead):
            nf = set(food_s)
            if m_ate and not m_dead:
                nf.discard(mnh)
            if o_ate and not o_dead:
                nf.discard(onh)
            if m_ate and o_ate and mnh == onh and not m_dead and not o_dead:
                nf.discard(mnh)
        mh2 = 100 if m_ate and not m_dead else mh - 1
        oh2 = 100 if o_ate and not o_dead else oh - 1
        return m_dead, o_dead, mb2, ob2, mh2, oh2, nf

    def recurse(mb, ob, mh, oh, food_s, depth, alpha, beta):
        nodes[0] += 1
        if time.perf_counter() > deadline:
            return evaluate(mb, ob, mh, oh, food_s), None
        my_moves = _legal_targets(mb, w, h)
        if not my_moves:
            # forced? engine would go forward and die; treat as loss
            return -10 ** 9, None
        # order: straight first, then toward food-ish
        cur = _dir_of(mb)
        my_moves.sort(key=lambda t: 0 if t[0] == cur else 1)
        best_val = -10 ** 18
        best_move = my_moves[0][0]
        for mname, mnh in my_moves:
            # opponent minimizes
            op_moves = _legal_targets(ob, w, h)
            if not op_moves:
                val = 10 ** 9
            else:
                val = 10 ** 18
                ocur = _dir_of(ob)
                op_moves.sort(key=lambda t: 0 if t[0] == ocur else 1)
                for _, onh in op_moves:
                    m_dead, o_dead, mb2, ob2, mh2, oh2, nf = resolve(
                        mb, ob, mh, oh, food_s, mnh, onh
                    )
                    if m_dead and o_dead:
                        # same-turn death: longer ranks better
                        ml = len(mb) + (1 if mnh in food_s else 0)
                        ol = len(ob) + (1 if onh in food_s else 0)
                        child = 200 if ml > ol else (-200 if ml < ol else 0)
                    elif m_dead:
                        child = -10 ** 9
                    elif o_dead:
                        child = 10 ** 9
                    elif depth == 1:
                        child = evaluate(mb2, ob2, mh2, oh2, nf)
                    else:
                        child, _ = recurse(mb2, ob2, mh2, oh2, nf, depth - 1, alpha, beta)
                    if child < val:
                        val = child
                    if val <= alpha:
                        break
            if val > best_val:
                best_val = val
                best_move = mname
            if best_val > alpha:
                alpha = best_val
            if alpha >= beta:
                break
        return best_val, best_move

    # iterative deepening
    best = _dir_of(my_body) or "up"
    for depth in (1, 2, 3):
        if time.perf_counter() > deadline:
            break
        val, move = recurse(
            my_body, op_body, me["health"], opp["health"], food_set, depth, -10 ** 18, 10 ** 18
        )
        if move:
            best = move
        if time.perf_counter() > deadline:
            break
    return best

def decide(state):
    w = state["width"]
    h = state["height"]
    you = state["you"]
    food = [tuple(f) for f in state["food"]]
    me = None
    others = []
    for s in state["snakes"]:
        if s["id"] == you:
            me = s
        else:
            others.append(s)
    if me is None:
        return "up"
    if len(others) == 1 and w <= 17:
        try:
            return _search_duel(state, me, others[0], food, w, h)
        except Exception:
            return _heuristic(state, me, others, food, w, h)
    return _heuristic(state, me, others, food, w, h)
```

先保证不死：避开墙、身体和同等或更长的蛇头对撞，尾巴格在缩回后才跟。用洪水填充选空间更大、下一步还走得开的方向；血量紧或食物就在自己可达范围内时再去吃，优先没人更近的食物。单挑用对抗搜索比空间和长度，大乱斗则远离更长的头、把活到最后放在变长前面。