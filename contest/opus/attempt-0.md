```python
import time

DIRS = ("up", "down", "left", "right")
_DXY = ((0, -1), (0, 1), (-1, 0), (1, 0))

INF = 1 << 30
WIN = 100000.0
LOSS = -100000.0
DRAW = -1500.0

_GEOM = {}
_NB = ()
_N = 0
_W = 1
_DL = 0.0
_DLW = 0.0
_T = 1
_MAXT = 500


class _Timeout(Exception):
    pass


def _geom(W, H):
    key = (W, H)
    g = _GEOM.get(key)
    if g is not None:
        return g
    N = W * H
    nb = []
    nbd = []
    for i in range(N):
        x = i % W
        y = i // W
        a = []
        b = []
        for d in range(4):
            nx = x + _DXY[d][0]
            ny = y + _DXY[d][1]
            if 0 <= nx < W and 0 <= ny < H:
                j = ny * W + nx
                a.append(j)
                b.append((d, j))
        nb.append(tuple(a))
        nbd.append(tuple(b))
    g = (N, tuple(nb), tuple(nbd))
    _GEOM[key] = g
    return g


for _sz in (15, 31):
    try:
        _geom(_sz, _sz)
    except Exception:
        pass


def _free_times(N, bodies):
    # fa[c] = number of moves after which cell c is no longer occupied
    fa = [0] * N
    for b in bodies:
        v = len(b)
        for c in b:
            if v > fa[c]:
                fa[c] = v
            v -= 1
    return fa


def _voronoi(N, NB, fa, seeds, lens, food):
    # Level-synchronous multi-source BFS with timed obstacles.
    # seeds: (snake_index, cell, start_level). Ties go to the longer snake, equal -> contested.
    owner = [-1] * N
    ns = len(lens)
    counts = [0] * ns
    fdist = [INF] * ns
    frontier = []
    late = []
    for s, c, lv in seeds:
        if lv <= 0:
            if owner[c] == -1:
                owner[c] = s
                counts[s] += 1
                frontier.append(c)
        else:
            late.append((s, c))
    delayed = {}
    level = 0
    limit = 2 * N + 10
    while frontier or late or delayed:
        level += 1
        if level > limit:
            break
        newf = []
        if late:
            for s, c in late:
                if owner[c] == -1:
                    owner[c] = s
                    counts[s] += 1
                    newf.append(c)
                    if c in food and level < fdist[s]:
                        fdist[s] = level
            late = []
        claim = {}
        tie = set()
        if delayed:
            dl = delayed.pop(level, None)
            if dl:
                lim = level - 1
                for n, o in dl:
                    if owner[n] != -1 or counts[o] < lim:
                        continue
                    p = claim.get(n)
                    if p is None:
                        claim[n] = o
                    elif p != o:
                        lo = lens[o]
                        lp = lens[p]
                        if lo > lp:
                            claim[n] = o
                            tie.discard(n)
                        elif lo == lp:
                            tie.add(n)
        for c in frontier:
            o = owner[c]
            lo = lens[o]
            for n in NB[c]:
                if owner[n] != -1:
                    continue
                f = fa[n]
                if f > level:
                    lst = delayed.get(f)
                    if lst is None:
                        delayed[f] = [(n, o)]
                    else:
                        lst.append((n, o))
                    continue
                p = claim.get(n)
                if p is None:
                    claim[n] = o
                elif p != o:
                    lp = lens[p]
                    if lo > lp:
                        claim[n] = o
                        tie.discard(n)
                    elif lo == lp:
                        tie.add(n)
        for n, o in claim.items():
            if n in tie:
                owner[n] = -2
            else:
                owner[n] = o
                counts[o] += 1
                newf.append(n)
                if level < fdist[o] and n in food:
                    fdist[o] = level
        frontier = newf
    return counts, fdist


# ---------------------------------------------------------------- duel search

def _eval2(b0, b1, h0, h1, food):
    L0 = len(b0)
    L1 = len(b1)
    fa = _free_times(_N, (b0, b1))
    cnt, fd = _voronoi(_N, _NB, fa, ((0, b0[0], 0), (1, b1[0], 0)), (L0, L1), food)
    a0 = cnt[0]
    a1 = cnt[1]
    s = 3.0 * (a0 - a1)
    if a0 < L0:
        s -= 1200.0 + 40.0 * (L0 - a0)
    if a1 < L1:
        s += 800.0 + 20.0 * (L1 - a1)
    d = L0 - L1
    s += 30.0 * max(-2, min(2, d)) + 12.0 * d
    f0 = fd[0]
    w = 1.0 if d >= 2 else 2.5
    if h0 < 50:
        w += (50 - h0) * 0.1
    if f0 < INF:
        s -= w * f0
        if f0 > h0:
            s -= 1500.0
    else:
        s -= w * 25.0
        if h0 < 30:
            s -= 50.0 * (30 - h0)
    f1 = fd[1]
    if h1 < 40 and (f1 >= INF or f1 > h1):
        s += 400.0
    return s


def _child(b0, b1, h0, h1, food, m0, m1, depth, ply, alpha, beta):
    L0 = len(b0)
    L1 = len(b1)
    d0 = m0 < 0
    d1 = m1 < 0
    e0 = (not d0) and (m0 in food)
    e1 = (not d1) and (m1 in food)
    if e0:
        nh0 = 100
        L0 += 1
    else:
        nh0 = h0 - 1
        if nh0 <= 0:
            d0 = True
    if e1:
        nh1 = 100
        L1 += 1
    else:
        nh1 = h1 - 1
        if nh1 <= 0:
            d1 = True
    if m0 == m1 and m0 >= 0:
        if L0 > L1:
            d1 = True
        elif L1 > L0:
            d0 = True
        else:
            d0 = True
            d1 = True
    if d0 or d1:
        if d0 and d1:
            if L0 > L1:
                return WIN - ply * 100.0
            if L0 < L1:
                return LOSS + ply * 100.0
            return DRAW
        if d0:
            return LOSS + ply * 100.0
        return WIN - ply * 100.0
    nb0 = [m0] + b0[:-1]
    if e0:
        nb0.append(nb0[-1])
    nb1 = [m1] + b1[:-1]
    if e1:
        nb1.append(nb1[-1])
    if e0 or e1:
        nf = food - {m0, m1}
    else:
        nf = food
    return _ab(nb0, nb1, nh0, nh1, nf, depth, ply, alpha, beta)


def _ab(b0, b1, h0, h1, food, depth, ply, alpha, beta):
    if time.process_time() > _DL or time.perf_counter() > _DLW:
        raise _Timeout()
    if _T + ply - 1 >= _MAXT:
        L0 = len(b0)
        L1 = len(b1)
        if L0 > L1:
            return WIN - ply * 100.0
        if L0 < L1:
            return LOSS + ply * 100.0
        return DRAW
    if depth <= 0:
        return _eval2(b0, b1, h0, h1, food)
    NB = _NB
    obst = set(b0[:-1])
    obst.update(b1[:-1])
    ML = [n for n in NB[b0[0]] if n not in obst]
    if not ML:
        ML = [-1]
    OL = [n for n in NB[b1[0]] if n not in obst]
    if not OL:
        OL = [-1]
    elif len(OL) > 1:
        W = _W
        hx = b0[0] % W
        hy = b0[0] // W
        OL.sort(key=lambda n: abs(n % W - hx) + abs(n // W - hy))
    best = -INF
    for m0 in ML:
        v = INF
        for m1 in OL:
            cv = _child(b0, b1, h0, h1, food, m0, m1, depth - 1, ply + 1,
                        alpha, v if v < beta else beta)
            if cv < v:
                v = cv
                if v <= alpha:
                    break
        if v > best:
            best = v
            if v > alpha:
                alpha = v
                if alpha >= beta:
                    break
    return best


def _root(b0, b1, h0, h1, food, depth, order):
    obst = set(b0[:-1])
    obst.update(b1[:-1])
    OL = [n for n in _NB[b1[0]] if n not in obst]
    if not OL:
        OL = [-1]
    elif len(OL) > 1:
        W = _W
        hx = b0[0] % W
        hy = b0[0] // W
        OL.sort(key=lambda n: abs(n % W - hx) + abs(n // W - hy))
    vals = {}
    alpha = -INF
    for m0 in order:
        v = INF
        for m1 in OL:
            cv = _child(b0, b1, h0, h1, food, m0, m1, depth - 1, 1, alpha, v)
            if cv < v:
                v = cv
                if v <= alpha:
                    break
        vals[m0] = v
        if v > alpha:
            alpha = v
    return vals


def _duel(mb, mh, ob, oh, food, cands, turn, maxt, t0, w0, budget, N, NB, W):
    global _NB, _N, _W, _DL, _DLW, _T, _MAXT
    _NB = NB
    _N = N
    _W = W
    _DL = t0 + budget
    _DLW = w0 + max(0.5, 3.0 * budget)
    _T = turn
    _MAXT = maxt
    order = [n for _d, n in cands]
    best = None
    depth = 1
    while depth <= 60:
        try:
            vals = _root(mb, ob, mh, oh, food, depth, order)
        except _Timeout:
            break
        bm = order[0]
        bv = vals[bm]
        for m in order:
            if vals[m] > bv:
                bm = m
                bv = vals[m]
        best = bm
        rest = [m for m in order if m != bm]
        rest.sort(key=lambda m: -vals[m])
        order = [bm] + rest
        if bv >= WIN - 50000.0 or bv <= LOSS + 50000.0:
            break
        if _T + depth - 1 >= _MAXT:
            break
        depth += 1
    return best


# ---------------------------------------------------------------- free-for-all

def _multi(mb, mh, others, food, cands, obst, N, NB, W, deadline):
    myL = len(mb)
    bodies = [b for b, _h in others]
    bodies.append(mb)
    fa = _free_times(N, bodies)
    ne = len(others)
    epm = []
    elen = []
    ehead = []
    for b, _h in others:
        epm.append([n for n in NB[b[0]] if n not in obst])
        elen.append(len(b))
        ehead.append(b[0])
    maxE = max(elen) if elen else 0
    infos = []
    ta = time.process_time()
    for d, n in cands:
        eat = n in food
        if eat:
            L2 = myL + 1
            fa2 = fa[:]
            v = L2
            for c in mb:
                if v > fa2[c]:
                    fa2[c] = v
                v -= 1
        else:
            L2 = myL
            fa2 = fa
        cf, ff = _voronoi(N, NB, fa2, ((0, n, 1),), (L2,), food)
        infos.append([d, n, eat, L2, fa2, cf[0], ff[0], -1, INF])
    tb = time.process_time()
    if ne > 0 and tb + 1.6 * (tb - ta) + 0.002 < deadline:
        lens = [0] + elen
        for inf in infos:
            lens[0] = inf[3]
            seeds = [(i + 1, ehead[i], 0) for i in range(ne)]
            seeds.append((0, inf[1], 1))
            cv, fv = _voronoi(N, NB, inf[4], seeds, lens, food)
            inf[7] = cv[0]
            inf[8] = fv[0]
    best = cands[0][0]
    bs = -1e18
    for d, n, eat, L2, fa2, af, fany, av, fo in infos:
        s = 0.0
        risk = 0.0
        kill = 0.0
        near = 0
        nx = n % W
        ny = n // W
        for i in range(ne):
            Le = elen[i]
            pm = epm[i]
            if n in pm:
                k = len(pm)
                if Le >= myL:
                    p = 1.0 / k
                    if eat and p < 0.6:
                        p = 0.6
                    risk += p
                else:
                    kill += 1.0 if k == 1 else 0.4 / k
            elif Le >= myL:
                eh = ehead[i]
                if abs(eh % W - nx) + abs(eh // W - ny) == 2:
                    near += 1
        if risk > 1.0:
            risk = 1.0
        if kill > 1.0:
            kill = 1.0
        s -= 4000.0 * risk
        s += 300.0 * kill
        s -= 25.0 * near
        if af < L2:
            s -= 2500.0 + 50.0 * (L2 - af)
        if av < 0:
            av = af
            fo = fany
        comfy = 2 * L2 + 12
        if av < comfy:
            s += 3.0 * av
        else:
            s += 3.0 * comfy + 0.3 * (av - comfy)
        if av < L2:
            s -= 500.0 + 15.0 * (L2 - av)
        w = 1.5
        if myL <= maxE + 1:
            w = 3.0
        if mh < 60:
            w += (60 - mh) * 0.12
        if fo < INF:
            s -= w * min(fo, 40)
        elif fany < INF:
            s -= w * (min(fany, 40) + 6)
        else:
            s -= w * 46.0
        if mh < 40 and (fany >= INF or fany > mh):
            s -= 1500.0
        if eat:
            s += 30.0
        if s > bs:
            bs = s
            best = d
    return best


# ---------------------------------------------------------------- driver

def _desperate(mb, NBD):
    neck = mb[1] if len(mb) > 1 else -1
    for d, n in NBD[mb[0]]:
        if n != neck:
            return DIRS[d]
    return "up"


def _decide(state, t0, w0):
    W = int(state["width"])
    H = int(state["height"])
    N, NB, NBD = _geom(W, H)
    you = state.get("you")
    me = None
    others = []
    for s in state.get("snakes") or []:
        bl = s.get("body") or []
        body = []
        for p in bl:
            x = int(p[0])
            y = int(p[1])
            if 0 <= x < W and 0 <= y < H:
                body.append(y * W + x)
        if not body:
            continue
        try:
            hp = int(s.get("health", 100))
        except Exception:
            hp = 100
        if s.get("id") == you:
            me = (body, hp)
        else:
            others.append((body, hp))
    if me is None:
        return None
    fl = []
    for f in state.get("food") or []:
        x = int(f[0])
        y = int(f[1])
        if 0 <= x < W and 0 <= y < H:
            fl.append(y * W + x)
    food = frozenset(fl)
    turn = int(state.get("turn") or 1)
    maxt = int(state.get("max_turns") or 500)
    budget = 0.25 if turn <= 1 else 0.030
    mb, mh = me
    obst = set(mb[:-1])
    for b, _h in others:
        obst.update(b[:-1])
    cands = [(d, n) for d, n in NBD[mb[0]] if n not in obst]
    if not cands:
        return _desperate(mb, NBD)
    if len(cands) == 1:
        return DIRS[cands[0][0]]
    if len(others) == 1:
        ob, oh = others[0]
        m = _duel(mb, mh, ob, oh, food, cands, turn, maxt, t0, w0, budget, N, NB, W)
        if m is not None:
            for d, n in cands:
                if n == m:
                    return DIRS[d]
    d = _multi(mb, mh, others, food, cands, obst, N, NB, W, t0 + budget)
    return DIRS[d]


def _fallback(state):
    W = int(state["width"])
    H = int(state["height"])
    N, NB, NBD = _geom(W, H)
    you = state.get("you")
    obst = set()
    head = None
    neck = -1
    for s in state.get("snakes") or []:
        body = [int(p[1]) * W + int(p[0]) for p in (s.get("body") or [])]
        if not body:
            continue
        obst.update(body[:-1])
        if s.get("id") == you:
            head = body[0]
            if len(body) > 1 and body[1] != body[0]:
                neck = body[1]
    if head is None or head < 0 or head >= N:
        return "up"
    best = None
    bc = -1
    for d, n in NBD[head]:
        if n in obst:
            continue
        seen = {n}
        stack = [n]
        c = 0
        while stack and c < 200:
            x = stack.pop()
            c += 1
            for m in NB[x]:
                if m not in seen and m not in obst:
                    seen.add(m)
                    stack.append(m)
        if c > bc:
            bc = c
            best = d
    if best is None:
        for d, n in NBD[head]:
            if n != neck:
                return DIRS[d]
        return "up"
    return DIRS[best]


def decide(state):
    t0 = time.process_time()
    w0 = time.perf_counter()
    try:
        r = _decide(state, t0, w0)
        if r in DIRS:
            return r
    except Exception:
        pass
    try:
        return _fallback(state)
    except Exception:
        return "up"
```

策略说明：

**安全底线**：每回合先算出哪些方向会撞墙或撞身体。算的时候考虑了尾巴会缩回，刚吃过东西的蛇尾巴不动，所以能贴着别人的尾巴走。如果只剩一个能走的方向，就直接走它。

**单挑**（大乱斗打到只剩两条蛇时也用这一套）：双方同时出招，按对手总能选出对我最不利的那一步来搜，配合 α-β 剪枝逐层加深，CPU 时间约 30 毫秒就停。搜到最深处时这样打分：

- 看双方谁先到哪些格子来划分地盘。会算上身体什么时候让出格子，也算上绕圈等尾巴的空间。
- 再看长度优势、离自己能先抢到的食物有多远、血量够不够撑到吃饭，以及会不会被困死。
- 同样长度对头相撞是双亡，按劣势处理。

**大乱斗**：每个候选方向分别打分。

- 先估算撞头的概率：对方和我一样长或比我长就重罚，比我短就给一点奖励。
- 再单独做一次空间填充，判断这一步会不会把自己困死。
- 然后多蛇同时扩散，估算地盘大小和哪颗食物归我。
- 进食欲望看血量，也看自己比最长的对手短多少。

万一出错，就退回到"只求安全、选空间最大的方向"的简单策略。