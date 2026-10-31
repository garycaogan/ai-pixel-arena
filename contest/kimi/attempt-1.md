```python
import time

DIRS = ("up", "right", "down", "left")
VEC = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
BY_DELTA = {(0, -1): "up", (0, 1): "down", (-1, 0): "left", (1, 0): "right"}
INF = 10 ** 18

W = H = AREA = MAXT = 0
NEIGH = []
YOU = -1
ROOT = None
DEADLINE = 0.0
NODES = 0
CANDIDATE_ORDER = []

DIRS_BY_ID = {}
LAST_HEADS = {}
BODY_MASKS = {}
EVAL_CACHE = {}
POLICY_CACHE = {}
PLAN_CACHE = {}


class SearchTimeout(Exception):
    pass


def setup_board(w, h):
    global W, H, AREA, NEIGH
    if W == w and H == h and NEIGH:
        return
    W, H = w, h
    AREA = w * h
    NEIGH = []
    for y in range(h):
        for x in range(w):
            ns = []
            if y > 0:
                ns.append((y - 1) * w + x)
            if x + 1 < w:
                ns.append(y * w + x + 1)
            if y + 1 < h:
                ns.append((y + 1) * w + x)
            if x > 0:
                ns.append(y * w + x - 1)
            NEIGH.append(tuple(ns))


def check_time():
    global NODES
    NODES += 1
    if (NODES & 7) == 0 and time.process_time() > DEADLINE:
        raise SearchTimeout()


def cid(p):
    return p[1] * W + p[0]


def bit(p):
    return 1 << cid(p)


def manh(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def in_bounds(p):
    return 0 <= p[0] < W and 0 <= p[1] < H


def body_mask(body, mode):
    key = (mode, body)
    m = BODY_MASKS.get(key)
    if m is not None:
        return m
    if mode == 0:
        start, end = 0, len(body) - 1
    elif mode == 1:
        start, end = 0, len(body)
    else:
        start, end = 1, len(body)
    m = 0
    for i in range(start, end):
        m |= bit(body[i])
    if len(BODY_MASKS) > 30000:
        BODY_MASKS.clear()
    BODY_MASKS[key] = m
    return m


def board_block(st):
    m = 0
    for s in st[1]:
        m |= body_mask(s[1], 0)
    return m


def find_snake(st, sid):
    for s in st[1]:
        if s[0] == sid:
            return s
    return None


def default_dir(head):
    x, y = head
    if x < W // 2:
        return "right"
    if x > (W - 1) // 2:
        return "left"
    if y < H // 2:
        return "down"
    return "up"


def effective_dir(s, action):
    body = s[1]
    head = body[0]
    cur = s[3]
    if cur and len(body) > 1 and body[1] != head:
        dx, dy = VEC[action]
        nxt = (head[0] + dx, head[1] + dy)
        if nxt == body[1]:
            return cur
    return action


def shifted_body(body, d, foodset):
    dx, dy = VEC[d]
    nh = (body[0][0] + dx, body[0][1] + dy)
    nb = (nh,) + body[:-1]
    ate = nh in foodset
    if ate:
        nb += (body[-1],)
    return nh, nb, ate


def valid_actions(st, sid):
    s = find_snake(st, sid)
    if s is None:
        return ["up"]
    body = s[1]
    head = body[0]
    self_block = body_mask(body, 0)
    out = []
    seen = set()
    for a in DIRS:
        d = effective_dir(s, a)
        if d in seen:
            continue
        seen.add(d)
        dx, dy = VEC[d]
        nh = (head[0] + dx, head[1] + dy)
        if not in_bounds(nh):
            continue
        if bit(nh) & self_block:
            continue
        out.append(d)
    if out:
        return out
    for a in DIRS:
        d = effective_dir(s, a)
        dx, dy = VEC[d]
        nh = (head[0] + dx, head[1] + dy)
        if in_bounds(nh):
            return [d]
    return [s[3] or default_dir(head)]


def next_state(st, moves):
    turn, snakes, foods = st
    foodset = set(foods)
    records = []
    eaten = set()

    for s in snakes:
        sid, body, health, cur = s
        a = moves.get(sid)
        if a is None:
            a = cur or default_dir(body[0])
        d = effective_dir(s, a)
        nh, nb, ate = shifted_body(body, d, foodset)
        nh_health = health - 1
        starved = nh_health <= 0
        if ate:
            eaten.add(nh)
            nh_health = 100
        out = not in_bounds(nh)
        records.append((sid, nb, nh, nh_health, ate, out, starved, d))

    segmask = 0
    for r in records:
        segmask |= body_mask(r[1], 2)

    dead = set()
    for r in records:
        sid, nb, nh = r[0], r[1], r[2]
        if r[5] or r[6]:
            dead.add(sid)
        elif bit(nh) & segmask:
            dead.add(sid)

    groups = {}
    for r in records:
        if not r[5]:
            groups.setdefault(cid(r[2]), []).append(r)

    for group in groups.values():
        if len(group) > 1:
            maxlen = max(len(r[1]) for r in group)
            winners = [r[0] for r in group if len(r[1]) == maxlen]
            if len(winners) == 1:
                winner = winners[0]
                for r in group:
                    if r[0] != winner:
                        dead.add(r[0])
            else:
                for r in group:
                    dead.add(r[0])

    survivors = []
    for r in records:
        if r[0] not in dead:
            survivors.append((r[0], r[1], r[3], r[7]))

    remaining = [f for f in foods if f not in eaten]
    foodset = set(remaining)
    need = len(survivors) + 1 - len(foodset)
    if need > 0:
        occ = 0
        seed = ((turn + 1) * 1103515247 + len(survivors) * 2654435761) & 0x7FFFFFFF
        for s in survivors:
            occ |= body_mask(s[1], 1)
            seed ^= (s[1][0][0] + 31 * s[1][0][1] + 131 * s[0]) & 0x7FFFFFFF
        for k in range(need):
            seed = (seed * 1664525 + 1013904223 + k * 97) & 0x7FFFFFFF
            start = seed % AREA
            for j in range(AREA):
                idx = (start + j) % AREA
                b = 1 << idx
                if not (occ & b):
                    p = (idx % W, idx // W)
                    if p not in foodset:
                        foodset.add(p)
                        occ |= b
                        break

    return (turn + 1, tuple(survivors), tuple(sorted(foodset)))


def region_food(st, sid, cap, want_food=True):
    check_time()
    s = find_snake(st, sid)
    if s is None:
        return 0, None
    start = cid(s[1][0])
    blocked = board_block(st)
    foodmask = 0
    for f in st[2]:
        foodmask |= bit(f)

    seen = 1 << start
    q = [start]
    count = 0
    dist = 0
    found = None
    maxdist = max(0, min(s[2] - 1, 120))

    while q:
        check_time()
        dist += 1
        nq = []
        for c in q:
            for n in NEIGH[c]:
                b = 1 << n
                if (seen | blocked) & b:
                    continue
                seen |= b
                if count < cap:
                    count += 1
                if want_food and found is None and (foodmask & b):
                    found = dist
                nq.append(n)
        if count >= cap:
            if not want_food or found is not None or dist > maxdist:
                break
        q = nq
    return count, found


def policy_actions(st, sid, topn, detailed=False):
    key = (sid, topn, detailed, st)
    cached = POLICY_CACHE.get(key)
    if cached is not None:
        return cached

    s = find_snake(st, sid)
    if s is None:
        return ()
    sid_, body, health, cur = s
    head = body[0]
    foodset = set(st[2])
    self_block = body_mask(body, 0)

    other_block = 0
    for o in st[1]:
        if o[0] != sid:
            other_block |= body_mask(o[1], 0)
    all_block = self_block | other_block

    vals = []
    seen = set()
    for a in DIRS:
        d = effective_dir(s, a)
        if d in seen:
            continue
        seen.add(d)
        dx, dy = VEC[d]
        nh = (head[0] + dx, head[1] + dy)
        if not in_bounds(nh):
            continue
        nb = bit(nh)
        if nb & self_block or nb & other_block:
            continue

        _, nbody, ate = shifted_body(body, d, foodset)
        post_health = health - 1
        score = 0
        if post_health <= 0:
            score -= 1000000
        if ate:
            score += 220 + max(0, 45 - health) * 4
            foods_after = tuple(f for f in st[2] if f != nh)
        else:
            foods_after = st[2]

        if foods_after:
            fd = min(manh(nh, f) for f in foods_after)
            score -= fd * (5 if health > 30 else 15)
        else:
            score -= 200

        c = cid(nh)
        open_count = 0
        for n in NEIGH[c]:
            if not ((1 << n) & all_block):
                open_count += 1
        score += open_count * 12
        if d == cur:
            score += 7

        my_len = len(nbody)
        for o in st[1]:
            if o[0] == sid:
                continue
            oh = o[1][0]
            od = manh(nh, oh)
            if od == 1:
                if len(o[1]) > my_len:
                    score -= 220
                elif len(o[1]) == my_len:
                    score -= 140
                else:
                    score += 55
            if od <= 6:
                if my_len > len(o[1]) + 1:
                    score += (7 - od) * 9
                elif len(o[1]) >= my_len:
                    score -= (7 - od) * 14

        score -= (abs(nh[0] - (W - 1) / 2.0) + abs(nh[1] - (H - 1) / 2.0)) * 0.5

        if detailed:
            check_time()
            tmp_snakes = []
            for o in st[1]:
                if o[0] == sid:
                    tmp_snakes.append((sid, nbody, 100 if ate else post_health, d))
                else:
                    tmp_snakes.append(o)
            tmp_foods = tuple(f for f in st[2] if f != nh)
            tmp = (st[0], tuple(tmp_snakes), tmp_foods)
            rg, _ = region_food(tmp, sid, 40, False)
            score += min(rg, 40) * 3
            if rg < len(nbody):
                score -= 1300 + (len(nbody) - rg) * 80

        vals.append((score, d))

    if not vals:
        result = tuple(valid_actions(st, sid)[:1])
    else:
        vals.sort(reverse=True)
        result = tuple(d for _, d in vals[:topn])
    if len(POLICY_CACHE) > 30000:
        POLICY_CACHE.clear()
    POLICY_CACHE[key] = result
    return result


def evaluate(st):
    cached = EVAL_CACHE.get(st)
    if cached is not None:
        return cached

    turn, snakes, foods = st
    own = find_snake(st, YOU)
    if own is None:
        v = -9000000 + min(turn, MAXT) * 1000
        EVAL_CACHE[st] = v
        return v
    enemies = [s for s in snakes if s[0] != YOU]
    if not enemies:
        v = 9000000 - min(turn, MAXT) * 1000
        EVAL_CACHE[st] = v
        return v

    length = len(own[1])
    if turn > MAXT:
        best_other = max(len(e[1]) for e in enemies)
        v = 6000000 + (length - best_other) * 100000 + length * 1000 + own[2]
        EVAL_CACHE[st] = v
        return v

    if len(snakes) == 2:
        cap = min(AREA - 1, max(55, length * 3))
    else:
        cap = min(AREA - 1, max(50, min(120, length * 3)))

    space, fd = region_food(st, YOU, cap, True)
    score = length * 75 + own[2]

    if space < length:
        score -= 8000 + (length - space) * 140
    elif space < length + 4:
        score -= 2700 + (length + 4 - space) * 120
    elif space < length * 2:
        score -= 650
    score += min(space, cap) * 3

    if fd is None:
        score -= 10500 + own[2] * 22
        score -= manh(own[1][0], own[1][-1]) * 8
    else:
        if fd >= own[2]:
            score -= 6500 + (fd - own[2] + 1) * 300
        urgency = max(0, 105 - own[2]) // 7
        score -= fd * (7 + urgency)
        if own[2] <= 18:
            score -= fd * (19 - own[2]) * 25

    mobility = len(valid_actions(st, YOU))
    score += mobility * 35

    if len(enemies) == 1:
        e = enemies[0]
        elen = len(e[1])
        d = manh(own[1][0], e[1][0])
        ecap = min(AREA - 1, max(55, elen * 3))
        espace, _ = region_food(st, e[0], ecap, False)
        score += (min(space, cap) - min(espace, ecap)) * 2
        if espace < elen:
            score += 5200 + (elen - espace) * 120
        if length > elen:
            score += max(0, 8 - d) * 30
            if d <= 2:
                score += 300
        else:
            score -= max(0, 8 - d) * (30 + max(0, elen - length) * 5)
    else:
        for e in enemies:
            d = manh(own[1][0], e[1][0])
            if d <= 5:
                elen = len(e[1])
                if length > elen + 1:
                    score += (6 - d) * 12
                elif elen >= length:
                    score -= (6 - d) * 20

    left = MAXT - turn
    if left < 20:
        score += length * (20 - left) * 30

    EVAL_CACHE[st] = score
    return score


def terminal(st):
    own = find_snake(st, YOU)
    return own is None or len(st[1]) <= 1 or st[0] > MAXT


def state_action_quick(st, sid, d):
    s = find_snake(st, sid)
    if s is None:
        return -INF
    head = s[1][0]
    dx, dy = VEC[d]
    nh = (head[0] + dx, head[1] + dy)
    score = 0
    if nh in st[2]:
        score += 260
    if st[2]:
        score -= min(manh(nh, f) for f in st[2]) * 9
    blocked = board_block(st)
    c = cid(nh)
    for n in NEIGH[c]:
        if not ((1 << n) & blocked):
            score += 12
    return score


def duel_search(st, depth, alpha, beta):
    check_time()
    if depth <= 0 or terminal(st):
        return evaluate(st)
    if len(st[1]) > 2:
        return brawl_search(st, depth)

    enemies = [s for s in st[1] if s[0] != YOU]
    if not enemies:
        return evaluate(st)
    eid = enemies[0][0]

    oacts = valid_actions(st, YOU)
    oacts.sort(key=lambda a: state_action_quick(st, YOU, a), reverse=True)
    eacts = list(policy_actions(st, eid, 3, False))
    for a in valid_actions(st, eid):
        if a not in eacts:
            eacts.append(a)

    best = -INF
    for oa in oacts:
        worst = INF
        for ea in eacts:
            ns = next_state(st, {YOU: oa, eid: ea})
            if depth <= 1:
                v = evaluate(ns)
            else:
                v = duel_search(ns, depth - 1, alpha, beta)
            if v < worst:
                worst = v
            if worst <= alpha:
                break
        if worst > best:
            best = worst
        if best > alpha:
            alpha = best
    return best


def duel_values(depth):
    enemies = [s for s in ROOT[1] if s[0] != YOU]
    if not enemies:
        return {a: evaluate(next_state(ROOT, {YOU: a})) for a in CANDIDATE_ORDER}
    eid = enemies[0][0]
    eacts = list(policy_actions(ROOT, eid, 3, True))
    for a in valid_actions(ROOT, eid):
        if a not in eacts:
            eacts.append(a)

    vals = {}
    best = -INF
    for oa in CANDIDATE_ORDER:
        check_time()
        worst = INF
        for ea in eacts:
            ns = next_state(ROOT, {YOU: oa, eid: ea})
            if depth <= 1:
                v = evaluate(ns)
            else:
                v = duel_search(ns, depth - 1, best, INF)
            if v < worst:
                worst = v
            if worst <= best:
                break
        vals[oa] = worst
        if worst > best:
            best = worst
    return vals


def enemy_plan(st):
    cached = PLAN_CACHE.get(st)
    if cached is not None:
        return cached
    plan = {}
    for s in st[1]:
        if s[0] == YOU:
            continue
        acts = policy_actions(st, s[0], 1, False)
        if not acts:
            acts = tuple(valid_actions(st, s[0])[:1])
        plan[s[0]] = acts[0]
    if len(PLAN_CACHE) > 30000:
        PLAN_CACHE.clear()
    PLAN_CACHE[st] = plan
    return plan


def brawl_search(st, depth):
    check_time()
    if depth <= 0 or terminal(st):
        return evaluate(st)
    if len(st[1]) == 2:
        return duel_search(st, depth, -INF, INF)

    plan = enemy_plan(st)
    acts = valid_actions(st, YOU)
    acts.sort(key=lambda a: state_action_quick(st, YOU, a), reverse=True)
    best = -INF
    for oa in acts:
        moves = dict(plan)
        moves[YOU] = oa
        ns = next_state(st, moves)
        if depth <= 1:
            v = evaluate(ns)
        else:
            v = brawl_search(ns, depth - 1)
        if v > best:
            best = v
    return best


def brawl_values(depth):
    baseplan = {}
    for s in ROOT[1]:
        if s[0] == YOU:
            continue
        acts = policy_actions(ROOT, s[0], 1, False)
        if not acts:
            acts = tuple(valid_actions(ROOT, s[0])[:1])
        baseplan[s[0]] = acts[0]

    own_head = find_snake(ROOT, YOU)[1][0]
    near = []
    for s in ROOT[1]:
        if s[0] != YOU:
            near.append((manh(own_head, s[1][0]), s[0]))
    near.sort()
    near_ids = [sid for d, sid in near if d <= 9][:3]
    if not near_ids and near:
        near_ids = [near[0][1]]

    near_options = {}
    near_valid = {}
    for eid in near_ids:
        near_options[eid] = list(policy_actions(ROOT, eid, 3, True))
        near_valid[eid] = valid_actions(ROOT, eid)

    vals = {}
    for oa in CANDIDATE_ORDER:
        check_time()
        os = find_snake(ROOT, YOU)
        oh, onb, _ = shifted_body(os[1], oa, set(ROOT[2]))
        scenarios = [None]

        for eid in near_ids:
            alts = []
            for a in near_options[eid]:
                if a != baseplan[eid] and a not in alts:
                    alts.append(a)
            es = find_snake(ROOT, eid)
            for a in near_valid[eid]:
                if a in alts or a == baseplan[eid]:
                    continue
                eh, enb, eate = shifted_body(es[1], a, set(ROOT[2]))
                threatening = eh == oh
                if not threatening and in_bounds(eh):
                    sm = body_mask(es[1], 1 if eate else 0)
                    threatening = bool(bit(oh) & sm)
                if threatening:
                    alts.append(a)
                    break
            for a in alts[:2]:
                scenarios.append((eid, a))

        base_val = None
        worst = INF
        for sc in scenarios:
            moves = dict(baseplan)
            moves[YOU] = oa
            if sc is not None:
                moves[sc[0]] = sc[1]
            ns = next_state(ROOT, moves)
            if depth <= 1:
                v = evaluate(ns)
            else:
                v = brawl_search(ns, depth - 1)
            if sc is None:
                base_val = v
            if v < worst:
                worst = v
        vals[oa] = (2 * base_val + worst) // 3
    return vals


def root_risks(st, action):
    own = find_snake(st, YOU)
    oh, onb, _ = shifted_body(own[1], action, set(st[2]))
    bad = 0
    good = 0
    for e in st[1]:
        if e[0] == YOU:
            continue
        for ea in valid_actions(st, e[0]):
            eh, enb, eate = shifted_body(e[1], ea, set(st[2]))
            if not in_bounds(eh):
                continue
            sm = body_mask(e[1], 1 if eate else 0)
            if bit(oh) & sm:
                bad += 2
            if eh == oh:
                if len(enb) >= len(onb):
                    bad += 4
                else:
                    good += 1
    return bad, good


def quick_score(st, action, bad, good):
    own = find_snake(st, YOU)
    head = own[1][0]
    dx, dy = VEC[action]
    nh = (head[0] + dx, head[1] + dy)
    score = -bad * 10000 + good * 350
    if nh in st[2]:
        score += 520
    if st[2]:
        score -= min(manh(nh, f) for f in st[2]) * 17
    blocked = board_block(st)
    c = cid(nh)
    for n in NEIGH[c]:
        if not ((1 << n) & blocked):
            score += 28
    if action == own[3]:
        score += 6
    return score


def infer_directions(raw):
    global LAST_HEADS
    new_heads = {}
    for s in raw.get("snakes", []):
        sid = s.get("id")
        body = s.get("body") or []
        if not body:
            continue
        head = (body[0][0], body[0][1])
        old = LAST_HEADS.get(sid)
        if old is not None:
            d = BY_DELTA.get((head[0] - old[0], head[1] - old[1]))
            if d is not None:
                DIRS_BY_ID[sid] = d
        new_heads[sid] = head
    LAST_HEADS = new_heads


def make_state(raw):
    snakes = []
    for s in raw["snakes"]:
        body = tuple((int(p[0]), int(p[1])) for p in s["body"])
        snakes.append((int(s["id"]), body, int(s["health"]), DIRS_BY_ID.get(int(s["id"]))))
    foods = tuple(sorted((int(p[0]), int(p[1])) for p in raw["food"]))
    return (int(raw["turn"]), tuple(snakes), foods)


def _decide(raw):
    global YOU, MAXT, ROOT, DEADLINE, NODES, CANDIDATE_ORDER

    start = time.process_time()
    turn = int(raw.get("turn", 1))
    DEADLINE = start + (0.65 if turn <= 1 else 0.030)
    NODES = 0

    setup_board(int(raw["width"]), int(raw["height"]))
    YOU = int(raw["you"])
    MAXT = int(raw.get("max_turns", 500))
    infer_directions(raw)
    st = make_state(raw)
    ROOT = st

    EVAL_CACHE.clear()
    POLICY_CACHE.clear()
    PLAN_CACHE.clear()

    actions = valid_actions(st, YOU)
    risks = {a: root_risks(st, a) for a in actions}
    minbad = min(risks[a][0] for a in actions)
    candidates = [a for a in actions if risks[a][0] == minbad]
    vals = {a: quick_score(st, a, risks[a][0], risks[a][1]) for a in candidates}
    CANDIDATE_ORDER = sorted(candidates, key=lambda a: vals[a], reverse=True)

    if len(st[1]) == 2:
        maxdepth = 5 if turn <= 1 else 4
        for depth in range(1, maxdepth + 1):
            try:
                new_vals = duel_values(depth)
            except SearchTimeout:
                break
            vals = new_vals
            CANDIDATE_ORDER = sorted(CANDIDATE_ORDER, key=lambda a: vals.get(a, -INF), reverse=True)
    else:
        maxdepth = 3 if turn <= 1 else 2
        for depth in range(1, maxdepth + 1):
            try:
                new_vals = brawl_values(depth)
            except SearchTimeout:
                break
            vals = new_vals
            CANDIDATE_ORDER = sorted(CANDIDATE_ORDER, key=lambda a: vals.get(a, -INF), reverse=True)

    best = max(CANDIDATE_ORDER, key=lambda a: vals.get(a, -INF) + risks[a][1] * 120)
    DIRS_BY_ID[YOU] = best
    return best


def emergency(raw):
    try:
        w = int(raw["width"])
        h = int(raw["height"])
        you = int(raw["you"])
        own = None
        for s in raw.get("snakes", []):
            if int(s.get("id", -1)) == you:
                own = s
                break
        if own is None or not own.get("body"):
            return "up"
        body = [(int(p[0]), int(p[1])) for p in own["body"]]
        head = body[0]
        cur = DIRS_BY_ID.get(you)
        occupied = set()
        for s in raw.get("snakes", []):
            b = [(int(p[0]), int(p[1])) for p in s.get("body", [])]
            occupied.update(b[:-1])
        foods = {(int(p[0]), int(p[1])) for p in raw.get("food", [])}
        best_a = "up"
        best_s = -10 ** 18
        seen = set()
        for a in DIRS:
            d = a
            if cur and len(body) > 1 and body[1] != head:
                dx0, dy0 = VEC[a]
                if (head[0] + dx0, head[1] + dy0) == body[1]:
                    d = cur
            if d in seen:
                continue
            seen.add(d)
            dx, dy = VEC[d]
            nh = (head[0] + dx, head[1] + dy)
            if not (0 <= nh[0] < w and 0 <= nh[1] < h):
                continue
            if nh in set(body[:-1]):
                continue
            score = 100 if nh in foods else 0
            for vx, vy in VEC.values():
                q = (nh[0] + vx, nh[1] + vy)
                if 0 <= q[0] < w and 0 <= q[1] < h and q not in occupied:
                    score += 1
            if score > best_s:
                best_s = score
                best_a = d
        DIRS_BY_ID[you] = best_a
        return best_a
    except Exception:
        return "up"


def decide(state):
    try:
        return _decide(state)
    except Exception:
        return emergency(state)
```

改动：收紧每回合 CPU 预算，把全局耗时检查加密到搜索与洪泛扩展中；降低大乱斗/单挑搜索深度，减少敌方策略的洪泛评估和近敌变体数量，确保超时前总能保留已完成的可行着法。