```python
import time
from collections import deque

DIRS = ("up", "down", "left", "right")
DIR_DELTAS = ((0, -1), (0, 1), (-1, 0), (1, 0))

WIN_SCORE = 100000.0
DEAD_SCORE = -100000.0
TRAP_SCORE = -65000.0


class _SearchTimeout(Exception):
    pass


class GridCache:
    __slots__ = (
        "w",
        "h",
        "n",
        "next_cell",
        "adj",
        "parity",
        "manhattan",
        "border_dist",
        "center_bias",
    )

    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        n = w * h
        self.n = n

        next_cell = []
        adj = []
        parity = [0] * n
        border_dist = [0] * n
        center_bias = [0.0] * n

        cx = (w - 1) * 0.5
        cy = (h - 1) * 0.5
        max_c = max(1.0, cx + cy)

        for y in range(h):
            for x in range(w):
                pos = y * w + x
                parity[pos] = (x + y) & 1
                bd = min(x, w - 1 - x, y, h - 1 - y)
                border_dist[pos] = bd
                dist_c = abs(x - cx) + abs(y - cy)
                center_bias[pos] = (1.0 - dist_c / max_c) * 18.0 + min(bd, 3) * 12.0

                row_dirs = [-1, -1, -1, -1]
                neighbors = []
                for d, (dx, dy) in enumerate(DIR_DELTAS):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        npos = ny * w + nx
                        row_dirs[d] = npos
                        neighbors.append(npos)
                next_cell.append(tuple(row_dirs))
                adj.append(tuple(neighbors))

        self.next_cell = tuple(next_cell)
        self.adj = tuple(adj)
        self.parity = tuple(parity)
        self.border_dist = tuple(border_dist)
        self.center_bias = tuple(center_bias)

        manhattan = []
        for p1 in range(n):
            x1, y1 = p1 % w, p1 // w
            row = [0] * n
            for p2 in range(n):
                row[p2] = abs(x1 - (p2 % w)) + abs(y1 - (p2 // w))
            manhattan.append(tuple(row))
        self.manhattan = tuple(manhattan)


_GRID_CACHE: dict[tuple[int, int], GridCache] = {
    (15, 15): GridCache(15, 15),
    (31, 31): GridCache(31, 31),
}

# Persistent per-game tracking
_RECENT_HEADS: deque[int] = deque(maxlen=16)
_LAST_ATE_TURN: int = 0
_LAST_LEN: int = 3
_PREV_ENEMY_HEADS: dict[int, int] = {}
_ENEMY_AGGRESSION: dict[int, int] = {}


def _get_grid(w: int, h: int) -> GridCache:
    key = (w, h)
    grid = _GRID_CACHE.get(key)
    if grid is None:
        grid = GridCache(w, h)
        _GRID_CACHE[key] = grid
    return grid


class SnakeObj:
    __slots__ = ("id", "body", "head", "neck", "tail", "health", "length")

    def __init__(self, sid: int, body: tuple[int, ...], health: int, length: int):
        self.id = sid
        self.body = body
        self.head = body[0]
        self.neck = body[1] if len(body) > 1 and body[1] != body[0] else -1
        self.tail = body[-1]
        self.health = health
        self.length = length

    def step(self, next_pos: int, ate_food: bool) -> "SnakeObj":
        b = self.body
        if ate_food:
            new_body = (next_pos,) + b[:-1] + (b[-2],)
            return SnakeObj(self.id, new_body, 100, self.length + 1)
        else:
            new_body = (next_pos,) + b[:-1]
            return SnakeObj(self.id, new_body, self.health - 1, self.length)


def _build_release_time(n: int, snakes: list[SnakeObj]) -> list[int]:
    rel = [0] * n
    for s in snakes:
        b = s.body
        length = len(b)
        for i in range(length - 2, -1, -1):
            rel[b[i]] = length - 1 - i
    return rel


def _valid_step1_moves(
    snake: SnakeObj,
    rel: list[int],
    food_set: set[int],
    adj: tuple[tuple[int, ...], ...],
) -> list[int]:
    head = snake.head
    neck = snake.neck
    hp = snake.health
    res = []
    for npos in adj[head]:
        if npos == neck:
            continue
        if rel[npos] >= 1:
            continue
        if hp <= 1 and npos not in food_set:
            continue
        res.append(npos)
    return res


def _compute_space_and_voronoi(
    me: SnakeObj,
    enemies: list[SnakeObj],
    rel: list[int],
    food_set: set[int],
    grid: GridCache,
    root_food_dist: list[int],
    max_dist: int,
) -> tuple[int, int, bool, bool, int, int, float, int]:
    """
    Returns:
      (total_cap, voronoi_cap, can_reach_tail, voronoi_reach_tail,
       width_1, width_2, food_score, min_food_dist)
    """
    n = grid.n
    adj = grid.adj
    parity = grid.parity

    # 1. Multi-source enemy BFS (sorted by length descending so longest enemy claims ties)
    en_dist = [999] * n
    en_len = [0] * n
    eq: list[int] = []

    if enemies:
        sorted_enemies = sorted(enemies, key=lambda e: e.length, reverse=True)
        for e in sorted_enemies:
            elen = e.length
            ehead = e.head
            eneck = e.neck
            ehp = e.health
            for npos in adj[ehead]:
                if npos == eneck or rel[npos] >= 1:
                    continue
                if ehp <= 1 and npos not in food_set:
                    continue
                if en_dist[npos] == 999:
                    en_dist[npos] = 1
                    en_len[npos] = elen
                    eq.append(npos)

        for u in eq:
            d = en_dist[u]
            if d >= max_dist:
                continue
            nd = d + 1
            elen = en_len[u]
            for nxt in adj[u]:
                if en_dist[nxt] == 999 and rel[nxt] < nd:
                    en_dist[nxt] = nd
                    en_len[nxt] = elen
                    eq.append(nxt)

    # 2. Our Voronoi-Shadowed BFS
    my_head = me.head
    my_neck = me.neck
    my_len = me.length
    my_tail = me.tail
    my_hp = me.health

    v_dist = [999] * n
    vq: list[int] = []
    v_even = 0
    v_odd = 0
    width_1 = 0
    width_2 = 0
    voronoi_reach_tail = False

    food_scores: list[float] = []
    min_food_dist = 999

    for npos in adj[my_head]:
        if npos == my_neck or rel[npos] >= 1:
            continue
        if my_hp <= 1 and npos not in food_set:
            continue
        ed = en_dist[npos]
        if 1 < ed or (1 == ed and my_len > en_len[npos]):
            v_dist[npos] = 1
            vq.append(npos)
            width_1 += 1
            if parity[npos]:
                v_odd += 1
            else:
                v_even += 1
            if npos == my_tail:
                voronoi_reach_tail = True

    for u in vq:
        d = v_dist[u]
        if u in food_set:
            # Verify food is not a 1-step dead-end trap
            open_deg = 0
            for fn in adj[u]:
                if rel[fn] <= d:
                    open_deg += 1
            if open_deg >= 2 or d > 1:
                if d < min_food_dist:
                    min_food_dist = d
                food_scores.append(210.0 / (d + 1.2))

        if d >= max_dist:
            continue
        nd = d + 1
        for nxt in adj[u]:
            if v_dist[nxt] == 999 and rel[nxt] < nd:
                ed = en_dist[nxt]
                if nd < ed or (nd == ed and my_len > en_len[nxt]):
                    v_dist[nxt] = nd
                    vq.append(nxt)
                    if nd == 2:
                        width_2 += 1
                    if parity[nxt]:
                        v_odd += 1
                    else:
                        v_even += 1
                    if nxt == my_tail:
                        voronoi_reach_tail = True

    voronoi_raw = v_even + v_odd
    voronoi_cap = min(voronoi_raw, 2 * min(v_even, v_odd) + 2)

    # 3. Total Time-Aware Survival Capacity (with Frontier Tail-Opening Check)
    t_dist = [999] * n
    tq: list[int] = []
    t_even = 0
    t_odd = 0
    can_reach_tail = voronoi_reach_tail
    target_safe_cap = min(n, max(my_len + 8, 28))

    for npos in adj[my_head]:
        if npos == my_neck or rel[npos] >= 1:
            continue
        if my_hp <= 1 and npos not in food_set:
            continue
        t_dist[npos] = 1
        tq.append(npos)
        if parity[npos]:
            t_odd += 1
        else:
            t_even += 1
        if npos == my_tail:
            can_reach_tail = True

    idx = 0
    while idx < len(tq):
        u = tq[idx]
        idx += 1
        d = t_dist[u]
        if u in food_set and v_dist[u] == 999:
            open_deg = 0
            for fn in adj[u]:
                if rel[fn] <= d:
                    open_deg += 1
            if open_deg >= 2:
                if d < min_food_dist:
                    min_food_dist = d
                ed = en_dist[u]
                if d == ed and my_len == en_len[u]:
                    food_scores.append(30.0 / (d + 2.0))
                else:
                    food_scores.append(45.0 / (d + 2.5))

        if d >= max_dist and (t_even + t_odd) >= target_safe_cap:
            continue
        nd = d + 1
        for nxt in adj[u]:
            if t_dist[nxt] == 999 and rel[nxt] < nd:
                t_dist[nxt] = nd
                tq.append(nxt)
                if parity[nxt]:
                    t_odd += 1
                else:
                    t_even += 1
                if nxt == my_tail:
                    can_reach_tail = True

    total_cap = min(t_even + t_odd, 2 * min(t_even, t_odd) + 2)

    # Frontier stalling check: if pocket looks small, check if stalling inside the pocket
    # allows an adjacent body segment (whose release_time <= total_cap) to open!
    if total_cap < my_len + 4 and total_cap > 0:
        while total_cap < my_len + 4:
            opened_any = False
            cur_len = len(tq)
            for i in range(cur_len):
                u = tq[i]
                for nxt in adj[u]:
                    if t_dist[nxt] == 999 and 0 < rel[nxt] <= total_cap:
                        t_dist[nxt] = rel[nxt] + 1
                        tq.append(nxt)
                        if parity[nxt]:
                            t_odd += 1
                        else:
                            t_even += 1
                        if nxt == my_tail:
                            can_reach_tail = True
                        opened_any = True
            if not opened_any:
                break
            while idx < len(tq):
                u = tq[idx]
                idx += 1
                d = t_dist[u]
                nd = d + 1
                for nxt in adj[u]:
                    if t_dist[nxt] == 999 and rel[nxt] < nd:
                        t_dist[nxt] = nd
                        tq.append(nxt)
                        if parity[nxt]:
                            t_odd += 1
                        else:
                            t_even += 1
                        if nxt == my_tail:
                            can_reach_tail = True
            total_cap = min(t_even + t_odd, 2 * min(t_even, t_odd) + 2)

    # Combine food scores
    food_total = 0.0
    if food_scores:
        food_scores.sort(reverse=True)
        food_total = food_scores[0]
        if len(food_scores) > 1:
            food_total += 0.35 * food_scores[1]
    elif root_food_dist[my_head] < 999:
        rfd = root_food_dist[my_head]
        min_food_dist = rfd
        food_total = 60.0 / (rfd + 2.0)

    return (
        total_cap,
        voronoi_cap,
        can_reach_tail,
        voronoi_reach_tail,
        width_1,
        width_2,
        food_total,
        min_food_dist,
    )


def _evaluate_state(
    me: SnakeObj,
    enemies: list[SnakeObj],
    food_set: set[int],
    grid: GridCache,
    root_food_dist: list[int],
    turn_offset: int,
    is_duel: bool,
    max_dist: int,
) -> float:
    if me.health <= 0:
        return DEAD_SCORE + turn_offset * 500.0 + me.length * 20.0
    if not enemies:
        return WIN_SCORE - turn_offset * 500.0 + me.length * 20.0

    all_snakes = [me] + enemies
    rel = _build_release_time(grid.n, all_snakes)

    (
        total_cap,
        voronoi_cap,
        can_reach_tail,
        voronoi_reach_tail,
        width_1,
        width_2,
        food_score,
        min_food_dist,
    ) = _compute_space_and_voronoi(
        me, enemies, rel, food_set, grid, root_food_dist, max_dist
    )

    my_len = me.length
    my_head = me.head

    # 1. Self-trap / Survival check
    if total_cap == 0 and width_1 == 0:
        return DEAD_SCORE + (turn_offset + 1) * 500.0 + my_len * 20.0

    score = 0.0
    if total_cap < my_len and not can_reach_tail:
        # Sealed pocket that won't open in time
        score += TRAP_SCORE + total_cap * 1100.0 + my_len * 20.0
    elif voronoi_cap < my_len and not voronoi_reach_tail:
        # Enemy can outrace us to seal our region
        deficit = my_len - voronoi_cap
        if voronoi_cap <= 3:
            score -= 16000.0 + deficit * 500.0
        else:
            score -= deficit * 420.0

    # 2. Mode-specific spatial & opponent evaluation
    if is_duel and len(enemies) == 1:
        opp = enemies[0]
        opp_len = opp.length
        len_diff = my_len - opp_len

        # Evaluate opponent's survival & Voronoi space
        (
            opp_total_cap,
            opp_voronoi_cap,
            opp_reach_tail,
            opp_v_reach_tail,
            opp_w1,
            _,
            _,
            _,
        ) = _compute_space_and_voronoi(
            opp, [me], rel, food_set, grid, root_food_dist, max_dist
        )

        if opp_total_cap == 0 and opp_w1 == 0:
            score += 75000.0 - turn_offset * 300.0
        elif opp_total_cap < opp_len and not opp_reach_tail:
            score += 48000.0 - opp_total_cap * 800.0
        elif opp_voronoi_cap < opp_len and not opp_v_reach_tail:
            opp_deficit = opp_len - opp_voronoi_cap
            if opp_voronoi_cap <= 3:
                score += 12000.0 + opp_deficit * 400.0
            else:
                score += opp_deficit * 360.0

        # Territory control
        score += (voronoi_cap - opp_voronoi_cap) * 24.0 + voronoi_cap * 8.0

        # Length dominance in 1v1
        score += my_len * 280.0 + len_diff * 240.0
        if len_diff >= 2:
            score += 950.0
        elif len_diff == 1:
            score += 520.0
        elif len_diff < 0:
            score -= 420.0

        # Aggressive zoning when strictly longer and healthy
        head_dist = grid.manhattan[my_head][opp.head]
        if len_diff >= 1 and me.health > 30 and total_cap >= my_len:
            score -= abs(head_dist - 3) * 28.0
            score -= grid.border_dist[opp.head] * 45.0
        elif len_diff <= 0 and head_dist <= 3:
            # Avoid being pinned on the border by an equal/longer opponent
            if grid.border_dist[my_head] == 0 and grid.border_dist[opp.head] >= 1:
                score -= 260.0
    else:
        # Battle Royale / Multi-snake evaluation
        cap_limit = max(50, my_len * 3)
        score += min(voronoi_cap, cap_limit) * 22.0 + min(total_cap, 90) * 6.0
        score += my_len * 320.0

        # Compare length & proximity with nearby enemies
        m_row = grid.manhattan[my_head]
        my_bd = grid.border_dist[my_head]
        num_en = len(enemies)
        for e in enemies:
            d = m_row[e.head]
            if d <= 10:
                if my_len > e.length:
                    score += 110.0
                    if num_en <= 4 and d <= 5:
                        score += (6 - d) * 18.0
                elif my_len == e.length:
                    score -= 40.0
                    if d <= 5:
                        score -= (6 - d) * 38.0
                else:
                    score -= 120.0
                    if d <= 6:
                        score -= (7 - d) * 65.0
                if d <= 4 and my_bd == 0 and grid.border_dist[e.head] >= 1:
                    score -= 160.0

    # 3. Food & Starvation Urgency
    spare_hp = me.health - min_food_dist
    if spare_hp <= 2:
        score -= 14000.0 - spare_hp * 2500.0
    urgency = 1.0
    if me.health < 50:
        urgency += (50 - me.health) * 0.075
    if is_duel and len(enemies) == 1 and my_len <= enemies[0].length + 1:
        urgency += 0.45

    score += food_score * urgency

    # 4. Immediate Freedom / Corridor Width & Center Bias
    if width_1 == 0:
        score -= 3500.0
    elif width_1 == 1:
        score -= 210.0
    else:
        score += width_1 * 65.0 + min(width_2, 6) * 24.0

    score += grid.center_bias[my_head]

    # 5. Anti-oscillation penalty at root/near-root when not growing
    if turn_offset <= 1 and _RECENT_HEADS:
        reps = 0
        for h in _RECENT_HEADS:
            if h == my_head:
                reps += 1
        if reps >= 2:
            score -= reps * 45.0

    return score


def _search_alphabeta(
    me: SnakeObj,
    opp: SnakeObj,
    other_enemies: list[SnakeObj],
    food_set: set[int],
    grid: GridCache,
    root_food_dist: list[int],
    depth: int,
    turn_offset: int,
    alpha: float,
    beta: float,
    deadline: float,
    is_duel: bool,
    max_dist: int,
) -> float:
    if time.perf_counter() >= deadline:
        raise _SearchTimeout()

    if me.health <= 0:
        return DEAD_SCORE + turn_offset * 500.0 + me.length * 20.0
    if opp.health <= 0:
        if not other_enemies:
            return WIN_SCORE - turn_offset * 500.0 + me.length * 20.0
        return _evaluate_state(
            me, other_enemies, food_set, grid, root_food_dist, turn_offset, False, max_dist
        )

    if depth <= 0:
        return _evaluate_state(
            me,
            [opp] + other_enemies,
            food_set,
            grid,
            root_food_dist,
            turn_offset,
            is_duel,
            max_dist,
        )

    all_snakes = [me, opp] + other_enemies
    rel = _build_release_time(grid.n, all_snakes)
    adj = grid.adj

    my_moves = _valid_step1_moves(me, rel, food_set, adj)
    if not my_moves:
        return DEAD_SCORE + (turn_offset + 1) * 500.0 + me.length * 20.0

    opp_moves = _valid_step1_moves(opp, rel, food_set, adj)
    if not opp_moves:
        if not other_enemies:
            return WIN_SCORE - (turn_offset + 1) * 500.0 + me.length * 20.0
        # Opponent dies this turn; evaluate our best continuation against remaining snakes
        best_kill = -1e9
        for m_me in my_moves:
            ate = m_me in food_set
            next_me = me.step(m_me, ate)
            n_food = food_set - {m_me} if ate else food_set
            val = (
                15000.0
                + _evaluate_state(
                    next_me,
                    other_enemies,
                    n_food,
                    grid,
                    root_food_dist,
                    turn_offset + 1,
                    False,
                    max_dist,
                )
            )
            if val > best_kill:
                best_kill = val
        return best_kill

    # Advance background enemies by shrinking their tails by 1 step
    next_others: list[SnakeObj] = []
    for e in other_enemies:
        if len(e.body) > 2 and e.health > 1:
            next_others.append(SnakeObj(e.id, e.body[:-1], e.health - 1, e.length))

    # Order our moves by quick proximity to center/food
    my_moves.sort(
        key=lambda m: (m in food_set, grid.center_bias[m], -root_food_dist[m]),
        reverse=True,
    )

    best_val = -1e9
    opp_num_moves = len(opp_moves)
    my_len = me.length
    opp_len = opp.length

    for m_me in my_moves:
        ate_me = m_me in food_set
        next_me = me.step(m_me, ate_me)

        # Check if m_me walks into a background enemy's head-to-head
        bg_h2h_pen = 0.0
        if other_enemies:
            for e in other_enemies:
                if grid.manhattan[m_me][e.head] == 1:
                    if e.length >= my_len:
                        bg_h2h_pen -= 28000.0 if turn_offset == 0 else 12000.0
                    else:
                        bg_h2h_pen += 200.0

        # Check simultaneous interaction between m_me and opp_moves
        worst_reply = 1e9
        h2h_pen = bg_h2h_pen

        if m_me in opp_moves:
            if my_len > opp_len:
                if opp_num_moves == 1:
                    # Guaranteed kill on opp!
                    if not other_enemies:
                        reply_val = WIN_SCORE - (turn_offset + 1) * 500.0 + next_me.length * 20.0
                    else:
                        n_food = food_set - {m_me} if ate_me else food_set
                        reply_val = 18000.0 + _evaluate_state(
                            next_me,
                            next_others,
                            n_food,
                            grid,
                            root_food_dist,
                            turn_offset + 1,
                            False,
                            max_dist,
                        )
                    worst_reply = reply_val
                else:
                    # Opp will avoid suiciding into m_me; we get a zoning bonus
                    h2h_pen += 320.0
            else:
                # opp_len >= my_len: we die if opp picks m_me!
                if opp_num_moves == 1:
                    worst_reply = DEAD_SCORE + (turn_offset + 1) * 500.0 + next_me.length * 20.0
                else:
                    aggr_mult = 1.25 if _ENEMY_AGGRESSION.get(opp.id, 0) > 0 else 1.0
                    food_mult = 1.35 if ate_me else 1.0
                    if opp_len > my_len:
                        base_pen = 38000.0 if turn_offset == 0 else (20000.0 / (turn_offset + 1))
                    else:
                        base_pen = 26000.0 if turn_offset == 0 else (11000.0 / (turn_offset + 1))
                    h2h_pen -= (base_pen * aggr_mult * food_mult) / (opp_num_moves * 0.5)

        if worst_reply == 1e9:
            for m_opp in opp_moves:
                if m_opp == m_me:
                    continue
                ate_opp = m_opp in food_set
                next_opp = opp.step(m_opp, ate_opp)
                if ate_me or ate_opp:
                    n_food = food_set - {m_me, m_opp}
                else:
                    n_food = food_set

                val = _search_alphabeta(
                    next_me,
                    next_opp,
                    next_others,
                    n_food,
                    grid,
                    root_food_dist,
                    depth - 1,
                    turn_offset + 1,
                    alpha - h2h_pen,
                    worst_reply,
                    deadline,
                    is_duel,
                    max_dist,
                )
                if val < worst_reply:
                    worst_reply = val
                if worst_reply + h2h_pen <= alpha:
                    break

        total_val = worst_reply + h2h_pen
        if total_val > best_val:
            best_val = total_val
        if best_val > alpha:
            alpha = best_val
        if alpha >= beta:
            break

    return best_val


def _search_solo(
    me: SnakeObj,
    enemies: list[SnakeObj],
    food_set: set[int],
    grid: GridCache,
    root_food_dist: list[int],
    depth: int,
    turn_offset: int,
    deadline: float,
    max_dist: int,
) -> float:
    if time.perf_counter() >= deadline:
        raise _SearchTimeout()

    if me.health <= 0:
        return DEAD_SCORE + turn_offset * 500.0 + me.length * 20.0
    if depth <= 0:
        return _evaluate_state(
            me, enemies, food_set, grid, root_food_dist, turn_offset, False, max_dist
        )

    all_snakes = [me] + enemies
    rel = _build_release_time(grid.n, all_snakes)
    my_moves = _valid_step1_moves(me, rel, food_set, grid.adj)
    if not my_moves:
        return DEAD_SCORE + (turn_offset + 1) * 500.0 + me.length * 20.0

    next_enemies: list[SnakeObj] = []
    for e in enemies:
        if len(e.body) > 2 and e.health > 1:
            next_enemies.append(SnakeObj(e.id, e.body[:-1], e.health - 1, e.length))

    best_val = -1e9
    for m_me in my_moves:
        ate = m_me in food_set
        next_me = me.step(m_me, ate)
        n_food = food_set - {m_me} if ate else food_set
        val = _search_solo(
            next_me,
            next_enemies,
            n_food,
            grid,
            root_food_dist,
            depth - 1,
            turn_offset + 1,
            deadline,
            max_dist,
        )
        if val > best_val:
            best_val = val
    return best_val


def _compute_root_food_dist(
    n: int, food_set: set[int], rel: list[int], adj: tuple[tuple[int, ...], ...]
) -> list[int]:
    fdist = [999] * n
    fq: list[int] = []
    for f in food_set:
        fdist[f] = 0
        fq.append(f)
    for u in fq:
        nd = fdist[u] + 1
        for nxt in adj[u]:
            if fdist[nxt] == 999 and rel[nxt] < nd:
                fdist[nxt] = nd
                fq.append(nxt)
    return fdist


def _update_game_history(
    turn: int, me: SnakeObj, enemies: list[SnakeObj], grid: GridCache
) -> None:
    global _LAST_ATE_TURN, _LAST_LEN
    if turn <= 1:
        _RECENT_HEADS.clear()
        _PREV_ENEMY_HEADS.clear()
        _ENEMY_AGGRESSION.clear()
        _LAST_ATE_TURN = 1
        _LAST_LEN = me.length

    if me.length > _LAST_LEN:
        _LAST_ATE_TURN = turn
        _LAST_LEN = me.length
        _RECENT_HEADS.clear()
    _RECENT_HEADS.append(me.head)

    # Track if any enemy moved aggressively into a contested cell last turn
    if _PREV_ENEMY_HEADS:
        for e in enemies:
            prev_h = _PREV_ENEMY_HEADS.get(e.id)
            if prev_h is not None:
                for other in enemies:
                    if other.id != e.id and other.length >= e.length:
                        prev_oh = _PREV_ENEMY_HEADS.get(other.id)
                        if prev_oh is not None and grid.manhattan[e.head][prev_oh] == 1:
                            _ENEMY_AGGRESSION[e.id] = _ENEMY_AGGRESSION.get(e.id, 0) + 1

    _PREV_ENEMY_HEADS.clear()
    for e in enemies:
        _PREV_ENEMY_HEADS[e.id] = e.head


def decide(state: dict) -> str:
    t0 = time.perf_counter()
    try:
        turn = state.get("turn", 1)
        budget = 0.380 if turn == 1 else 0.033
        deadline = t0 + budget

        w = state["width"]
        h = state["height"]
        grid = _get_grid(w, h)
        you_id = state["you"]

        me: SnakeObj | None = None
        enemies: list[SnakeObj] = []
        for s in state["snakes"]:
            body_tuple = tuple(pt[1] * w + pt[0] for pt in s["body"])
            sobj = SnakeObj(s["id"], body_tuple, s["health"], s["length"])
            if s["id"] == you_id:
                me = sobj
            else:
                enemies.append(sobj)

        if me is None:
            return "up"

        _update_game_history(turn, me, enemies, grid)

        food_set = {pt[1] * w + pt[0] for pt in state["food"]}
        all_snakes = [me] + enemies
        rel = _build_release_time(grid.n, all_snakes)

        next_cell_row = grid.next_cell[me.head]
        in_bounds_dirs: list[tuple[int, int]] = []
        safe_dirs: list[tuple[int, int]] = []

        for d in range(4):
            npos = next_cell_row[d]
            if npos == -1 or npos == me.neck:
                continue
            in_bounds_dirs.append((d, npos))
            if rel[npos] >= 1:
                continue
            if me.health <= 1 and npos not in food_set:
                continue
            safe_dirs.append((d, npos))

        if not in_bounds_dirs:
            return "up"
        if len(in_bounds_dirs) == 1:
            return DIRS[in_bounds_dirs[0][0]]

        if not safe_dirs:
            # All in-bounds moves hit a body or starve; pick the one with earliest release_time
            best_d = min(in_bounds_dirs, key=lambda item: rel[item[1]])[0]
            return DIRS[best_d]
        if len(safe_dirs) == 1:
            return DIRS[safe_dirs[0][0]]

        root_food_dist = _compute_root_food_dist(grid.n, food_set, rel, grid.adj)
        is_duel = len(enemies) == 1

        # Precompute enemy step-1 moves for exact root head-to-head risk classification
        enemy_step1: dict[int, list[int]] = {}
        for e in enemies:
            enemy_step1[e.id] = _valid_step1_moves(e, rel, food_set, grid.adj)

        # Evaluate all safe root directions with full-board vision (max_dist = 999)
        scored_moves: list[tuple[float, int, int, float]] = []
        for d, npos in safe_dirs:
            ate = npos in food_set
            next_me = me.step(npos, ate)
            n_food = food_set - {npos} if ate else food_set

            # Root head-to-head assessment across ALL enemies
            h2h_adj = 0.0
            max_en_reaching = 0
            min_en_moves = 99
            en_reaching_list: list[SnakeObj] = []

            for e in enemies:
                emoves = enemy_step1[e.id]
                if npos in emoves:
                    en_reaching_list.append(e)
                    if e.length > max_en_reaching:
                        max_en_reaching = e.length
                    if len(emoves) < min_en_moves:
                        min_en_moves = len(emoves)

            if en_reaching_list:
                if max_en_reaching < me.length:
                    if min_en_moves == 1:
                        # Guaranteed kill on a shorter enemy!
                        h2h_adj += 22000.0 if is_duel else 8500.0
                    else:
                        h2h_adj += 350.0
                else:
                    # At least one enemy reaching npos has length >= me.length
                    forced_fatal = any(
                        e.length >= me.length and len(enemy_step1[e.id]) == 1
                        for e in en_reaching_list
                    )
                    if forced_fatal:
                        h2h_adj += DEAD_SCORE + 500.0 + next_me.length * 20.0
                    else:
                        for e in en_reaching_list:
                            if e.length < me.length:
                                continue
                            k = max(1, len(enemy_step1[e.id]))
                            aggr = 1.25 if _ENEMY_AGGRESSION.get(e.id, 0) > 0 else 1.0
                            f_mult = 1.35 if ate else 1.0
                            if e.length > me.length:
                                h2h_adj -= (38000.0 * aggr * f_mult) / (k * 0.5)
                            else:
                                h2h_adj -= (26000.0 * aggr * f_mult) / (k * 0.5)

            base_val = _evaluate_state(
                next_me, enemies, n_food, grid, root_food_dist, 1, is_duel, 999
            )
            scored_moves.append((base_val + h2h_adj, d, npos, h2h_adj))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        best_dir = scored_moves[0][1]

        # Identify closest tactical threats within Manhattan distance
        m_row = grid.manhattan[me.head]
        nearby_enemies = [e for e in enemies if m_row[e.head] <= (14 if is_duel else 8)]
        nearby_enemies.sort(key=lambda e: (m_row[e.head], -e.length))

        leaf_max_dist = 999 if (w <= 15 or len(enemies) <= 2) else 18
        max_search_depth = 8 if is_duel else 4

        # Iterative Deepening Search
        for depth in range(1, max_search_depth + 1):
            if time.perf_counter() >= deadline:
                break

            new_scored: list[tuple[float, int, int, float]] = []
            alpha = -1e9
            completed_first = False
            current_best_dir = best_dir
            current_best_score = -1e9

            try:
                for prev_score, d, npos, root_h2h in scored_moves:
                    if time.perf_counter() >= deadline:
                        raise _SearchTimeout()

                    ate = npos in food_set
                    next_me = me.step(npos, ate)

                    if nearby_enemies:
                        primary_opp = nearby_enemies[0]
                        others = [e for e in enemies if e.id != primary_opp.id]
                        opp_moves = enemy_step1[primary_opp.id]

                        # Evaluate step 1 simultaneous interaction with primary_opp
                        worst_reply = 1e9
                        if not opp_moves:
                            if not others:
                                worst_reply = WIN_SCORE - 500.0 + next_me.length * 20.0
                            else:
                                n_food = food_set - {npos} if ate else food_set
                                worst_reply = 15000.0 + _evaluate_state(
                                    next_me,
                                    others,
                                    n_food,
                                    grid,
                                    root_food_dist,
                                    1,
                                    False,
                                    leaf_max_dist,
                                )
                        elif npos in opp_moves and len(opp_moves) == 1:
                            if me.length > primary_opp.length:
                                if not others:
                                    worst_reply = WIN_SCORE - 500.0 + next_me.length * 20.0
                                else:
                                    n_food = food_set - {npos} if ate else food_set
                                    worst_reply = 18000.0 + _evaluate_state(
                                        next_me,
                                        others,
                                        n_food,
                                        grid,
                                        root_food_dist,
                                        1,
                                        False,
                                        leaf_max_dist,
                                    )
                            else:
                                worst_reply = DEAD_SCORE + 500.0 + next_me.length * 20.0
                        else:
                            next_others = [
                                SnakeObj(e.id, e.body[:-1], e.health - 1, e.length)
                                for e in others
                                if len(e.body) > 2 and e.health > 1
                            ]
                            for m_opp in opp_moves:
                                if m_opp == npos:
                                    continue
                                ate_opp = m_opp in food_set
                                next_opp = primary_opp.step(m_opp, ate_opp)
                                n_food = (
                                    food_set - {npos, m_opp}
                                    if (ate or ate_opp)
                                    else food_set
                                )
                                val = _search_alphabeta(
                                    next_me,
                                    next_opp,
                                    next_others,
                                    n_food,
                                    grid,
                                    root_food_dist,
                                    depth - 1,
                                    1,
                                    alpha - root_h2h,
                                    worst_reply,
                                    deadline,
                                    is_duel,
                                    leaf_max_dist,
                                )
                                if val < worst_reply:
                                    worst_reply = val
                                if worst_reply + root_h2h <= alpha:
                                    break
                        move_val = worst_reply + root_h2h
                    else:
                        next_enemies = [
                            SnakeObj(e.id, e.body[:-1], e.health - 1, e.length)
                            for e in enemies
                            if len(e.body) > 2 and e.health > 1
                        ]
                        n_food = food_set - {npos} if ate else food_set
                        move_val = root_h2h + _search_solo(
                            next_me,
                            next_enemies,
                            n_food,
                            grid,
                            root_food_dist,
                            depth - 1,
                            1,
                            deadline,
                            leaf_max_dist,
                        )

                    new_scored.append((move_val, d, npos, root_h2h))
                    if not completed_first or move_val > current_best_score:
                        current_best_score = move_val
                        current_best_dir = d
                        completed_first = True
                    if move_val > alpha:
                        alpha = move_val

                new_scored.sort(key=lambda x: x[0], reverse=True)
                scored_moves = new_scored
                best_dir = scored_moves[0][1]
            except _SearchTimeout:
                if completed_first:
                    best_dir = current_best_dir
                break

        return DIRS[best_dir]
    except Exception:
        # Fail-safe fallback
        try:
            w = state["width"]
            h = state["height"]
            you_id = state["you"]
            snakes = state["snakes"]
            blocked = set()
            my_head = (0, 0)
            for s in snakes:
                b = s["body"]
                for pt in b[:-1]:
                    blocked.add((pt[0], pt[1]))
                if s["id"] == you_id:
                    my_head = (b[0][0], b[0][1])
            for d, (dx, dy) in enumerate(DIR_DELTAS):
                nx, ny = my_head[0] + dx, my_head[1] + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    return DIRS[d]
        except Exception:
            pass
        return "up"
```

### 修复说明

1. 修复了第 7 行 `WIN_SCORE = 100000.0` 前多余空格导致的 `IndentationError`。
2. 修复了第 51 行 `row_dirs` 变量名中误入空格导致的语法错误，并全面复查了全文件的缩进与语法规范。