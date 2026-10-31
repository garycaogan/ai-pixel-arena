# bot.py
import random
from collections import deque

DIRS = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))
VALID = ("up", "down", "left", "right")

_prev_target = None


def decide(state):
    try:
        mv = _decide(state)
        if mv in VALID:
            return mv
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        pass
    return random.choice(VALID)


def _fallback(state):
    try:
        w = state["width"]
        h = state["height"]
        me = None
        for s in state["snakes"]:
            if s["id"] == state["you"]:
                me = s
                break
        if me is None or not me["body"]:
            return random.choice(VALID)
        body = [(p[0], p[1]) for p in me["body"]]
        head = body[0]
        neck = body[1] if len(body) > 1 else (-99, -99)
        blocked = set(body[:-1])
        if len(body) == 1:
            blocked.add(head)
        if len(body) >= 2 and body[-1] == body[-2]:
            blocked.add(body[-1])
        straight = None
        if head != neck:
            v = (head[0] - neck[0], head[1] - neck[1])
            for name, dx, dy in DIRS:
                if (dx, dy) == v:
                    straight = name
                    break
        order = list(DIRS)
        if straight is not None:
            order.sort(key=lambda d: d[0] != straight)
        for name, dx, dy in order:
            nh = (head[0] + dx, head[1] + dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h and nh not in blocked:
                return name
        for name, dx, dy in order:
            nh = (head[0] + dx, head[1] + dy)
            if nh == neck:
                continue
            if 0 <= nh[0] < w and 0 <= nh[1] < h:
                return name
    except Exception:
        pass
    return random.choice(VALID)


def _decide(state):
    global _prev_target

    w = state["width"]
    h = state["height"]
    turn = state.get("turn", 1)
    maxt = state.get("max_turns", 500)
    me_id = state["you"]

    snakes = [s for s in state["snakes"] if s.get("body")]
    me = None
    others = []
    for s in snakes:
        if s["id"] == me_id:
            me = s
        else:
            others.append(s)
    if me is None:
        return random.choice(VALID)

    my_body = [(p[0], p[1]) for p in me["body"]]
    L = len(my_body)
    head = my_body[0]
    neck = my_body[1] if L > 1 else (-99, -99)
    my_health = me["health"]
    foods = [(f[0], f[1]) for f in state["food"]]

    # ---- occupancy model for this turn ----
    blocked = set()   # cells fatal to enter this turn (bodies with tails retracted, dup-tails stay)
    free_time = {}    # cell -> earliest flood step at which it becomes passable
    for s in snakes:
        b = [(p[0], p[1]) for p in s["body"]]
        sl = len(b)
        if sl == 0:
            continue
        stall = 1 if s["id"] == me_id else 2
        dup = sl >= 2 and b[-1] == b[-2]
        for i in range(sl):
            c = b[i]
            if i < sl - 1 or dup or sl == 1:
                blocked.add(c)
            if sl == 1:
                t = 3
            elif i == sl - 1 and not dup:
                t = 0
            else:
                t = sl - 1 - i + stall
            if c not in free_time or t < free_time[c]:
                free_time[c] = t

    opp_info = []
    for s in others:
        b = [(p[0], p[1]) for p in s["body"]]
        oh = b[0]
        on = b[1] if len(b) > 1 else (-99, -99)
        opp_info.append((oh, on, len(b)))
    n_opp = len(opp_info)

    # ---- helpers ----
    def bfs_dist(start):
        dist = {start: 0}
        dq = deque([start])
        while dq:
            cur = dq.popleft()
            x, y = cur
            d = dist[cur] + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    n = (nx, ny)
                    if n not in dist and n not in blocked:
                        dist[n] = d
                        dq.append(n)
        return dist

    def flood(start, extra_walls):
        # time-aware flood fill: body cells become passable as tails retract
        seen = {start}
        cnt = 1
        dq = deque([(start[0], start[1], 0)])
        while dq:
            x, y, d = dq.popleft()
            nd = d + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    c = (nx, ny)
                    if c in seen or c in extra_walls:
                        continue
                    ft = free_time.get(c)
                    if ft is not None and nd < ft:
                        continue
                    seen.add(c)
                    cnt += 1
                    dq.append((nx, ny, nd))
        return cnt

    # ---- food target ----
    dist_me = bfs_dist(head)
    dmin = None
    for f in foods:
        if f in dist_me:
            dd = dist_me[f]
            if dmin is None or dd < dmin:
                dmin = dd

    target = None
    best_cost = None
    for f in foods:
        if f in dist_me:
            dm = dist_me[f]
            contesters = 0
            if my_health >= 30:
                for oh, _on, _ol in opp_info:
                    if abs(oh[0] - f[0]) + abs(oh[1] - f[1]) < dm:
                        contesters += 1
            if n_opp == 1:
                cost = dm + (2 if contesters else 0)
            else:
                cost = dm + 2 * min(contesters, 3)
        else:
            cost = 150 + abs(head[0] - f[0]) + abs(head[1] - f[1])
        if f == _prev_target:
            cost -= 1.5
        if best_cost is None or cost < best_cost:
            best_cost = cost
            target = f
    _prev_target = target
    field_t = bfs_dist(target) if target is not None else None

    # ---- weights ----
    turns_left = maxt - turn + 1
    max_olen = 0
    for _oh, _on, ol in opp_info:
        if ol > max_olen:
            max_olen = ol
    safe_to_end = my_health > turns_left + 1
    can_coast = my_health > turns_left + 5

    starving = (not safe_to_end) and (
        (dmin is not None and my_health <= dmin + 6)
        or (dmin is None and my_health < 30))
    certain = (not safe_to_end) and (
        (dmin is not None and my_health <= dmin + 1) or my_health <= 3)

    if my_health > 85:
        fw, hpen = 1.8, 500.0
    elif my_health > 50:
        fw, hpen = 2.5, 500.0
    elif my_health > 30:
        fw, hpen = 4.0, 420.0
    else:
        fw, hpen = 6.5, 320.0
    eq_pen = 140.0 if n_opp == 1 else 500.0
    if can_coast:
        if L >= max_olen:
            fw, hpen, eq_pen = 0.8, 900.0, 800.0
        else:
            fw, hpen = 2.0, 650.0
    if starving:
        fw = max(fw, 8.0)
        if n_opp == 1:
            hpen = min(hpen, 150.0)
            eq_pen = min(eq_pen, 110.0)
        else:
            hpen = min(hpen, 250.0)
    if certain:
        fw = max(fw, 9.0)
        hpen = min(hpen, 70.0)
        if n_opp == 1:
            eq_pen = min(eq_pen, 60.0)
    trap_pen = 40.0
    if starving:
        trap_pen = 16.0
    if certain:
        trap_pen = 6.0
    area_cap = (w * h) // 3 + 10

    # ---- squeeze (single opponent left) ----
    squeeze_k = 0.0
    opp_head = None
    opp_base = 0
    if n_opp == 1:
        oh, _on, ol = opp_info[0]
        opp_head = oh
        opp_base = flood(oh, {oh})
        if not can_coast and my_health > 35 and not starving:
            squeeze_k = 2.0 if L > ol + 1 else 0.4

    # ---- candidates ----
    straight = None
    if L > 1 and head != neck:
        v = (head[0] - neck[0], head[1] - neck[1])
        for name, dx, dy in DIRS:
            if (dx, dy) == v:
                straight = name
                break

    cands = []
    for name, dx, dy in DIRS:
        nh = (head[0] + dx, head[1] + dy)
        if nh == neck:
            continue
        if not (0 <= nh[0] < w and 0 <= nh[1] < h):
            continue
        if nh in blocked:
            continue
        cands.append((name, nh))

    if not cands:
        names = []
        if straight is not None:
            names.append(straight)
        for n, _dx, _dy in DIRS:
            if n != straight:
                names.append(n)
        for n in names:
            for dn, dx, dy in DIRS:
                if dn == n:
                    nh = (head[0] + dx, head[1] + dy)
                    if nh != neck and 0 <= nh[0] < w and 0 <= nh[1] < h:
                        return n
        return random.choice(VALID)

    best_score = None
    best_name = None
    for name, nh in cands:
        score = 0.0
        # head-on risk: a longer/equal snake could also step here this turn
        for oh, on, ol in opp_info:
            if abs(oh[0] - nh[0]) + abs(oh[1] - nh[1]) == 1 and nh != on:
                if ol > L:
                    score -= hpen
                elif ol == L:
                    score -= min(eq_pen, hpen)
        # space (time-aware flood)
        area = flood(nh, {nh})
        if area <= L + 1:
            score -= (L + 2 - area) * trap_pen
        score += min(area, area_cap) * 1.2
        # food pull toward chosen target
        if field_t is not None:
            fd = field_t.get(nh)
            if fd is None:
                fd = 60 + abs(nh[0] - target[0]) + abs(nh[1] - target[1])
            score -= fd * fw
        # proximity to bigger heads
        for oh, on, ol in opp_info:
            md = abs(oh[0] - nh[0]) + abs(oh[1] - nh[1])
            if md == 1:
                if ol >= L:
                    score -= 20.0
                else:
                    score += 2.0
            elif md == 2 and ol > L:
                score -= 4.0
        # space denial vs last opponent
        if squeeze_k > 0:
            a2 = flood(opp_head, {opp_head, nh})
            gain = opp_base - a2
            if gain > 0:
                score += min(gain, 60) * squeeze_k
        if name == straight:
            score += 0.15
        score += random.random() * 0.3
        if best_score is None or score > best_score:
            best_score = score
            best_name = name
    return best_name
