DIR_VECS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIR_NAMES = {(0, -1): "up", (1, 0): "right", (0, 1): "down", (-1, 0): "left"}


def infer_dir(body):
    if not body or len(body) < 2:
        return None
    hx, hy = body[0][0], body[0][1]
    for p in body[1:]:
        dx = hx - p[0]
        dy = hy - p[1]
        if dx or dy:
            if dx > 0:
                return (1, 0)
            if dx < 0:
                return (-1, 0)
            if dy > 0:
                return (0, 1)
            return (0, -1)
    return None


def legal_moves(cur):
    if cur is None:
        return DIR_VECS
    dx, dy = cur
    res = [cur]
    a = (-dy, dx)
    b = (dy, -dx)
    if a not in res:
        res.append(a)
    if b not in res:
        res.append(b)
    return res


def bfs_metrics(start, blocked, food_idx, W, H, N):
    if start < 0 or start >= N or blocked[start]:
        return 0, 999
    seen = bytearray(N)
    seen[start] = 1
    current = [start]
    area = 0
    dist = 0
    min_food = 999
    while current:
        nxt = []
        for idx in current:
            area += 1
            if idx in food_idx and dist < min_food:
                min_food = dist
            if idx >= W:
                n = idx - W
                if not seen[n] and not blocked[n]:
                    seen[n] = 1
                    nxt.append(n)
            if idx < N - W:
                n = idx + W
                if not seen[n] and not blocked[n]:
                    seen[n] = 1
                    nxt.append(n)
            if idx % W != 0:
                n = idx - 1
                if not seen[n] and not blocked[n]:
                    seen[n] = 1
                    nxt.append(n)
            if idx % W != W - 1:
                n = idx + 1
                if not seen[n] and not blocked[n]:
                    seen[n] = 1
                    nxt.append(n)
        current = nxt
        dist += 1
    return area, min_food


def count_free_neighbors(idx, blocked, W, H, N):
    cnt = 0
    if idx >= W and not blocked[idx - W]:
        cnt += 1
    if idx < N - W and not blocked[idx + W]:
        cnt += 1
    if idx % W != 0 and not blocked[idx - 1]:
        cnt += 1
    if idx % W != W - 1 and not blocked[idx + 1]:
        cnt += 1
    return cnt


def beam_search(body_list, health, food_mask, cur_vec, other_blocked,
                other_blocked_bool, W, H, N, food_coords, depth, beamw):
    b0 = tuple(body_list)
    states = [(b0, health, food_mask, cur_vec, 0.0)]

    for _ in range(depth):
        expanded = []
        for b, h, mask, cur, acc in states:
            head = b[0]
            for vec in legal_moves(cur):
                tx = head[0] + vec[0]
                ty = head[1] + vec[1]
                if tx < 0 or tx >= W or ty < 0 or ty >= H:
                    continue
                if (tx, ty) in other_blocked:
                    continue

                bad = False
                for i in range(len(b) - 1):
                    if b[i] == (tx, ty):
                        bad = True
                        break
                if bad:
                    continue

                idx = ty * W + tx
                grow = (mask >> idx) & 1
                if grow:
                    nh = 100
                else:
                    nh = h - 1
                    if nh <= 0:
                        continue

                nb_list = [(tx, ty)]
                nb_list.extend(b[:-1])
                if grow:
                    nb_list.append(nb_list[-1])
                nb = tuple(nb_list)
                nmask = (mask & ~(1 << idx)) if grow else mask

                selfset = set(nb[1:])
                mob = 0
                for d in DIR_VECS:
                    nx = tx + d[0]
                    ny = ty + d[1]
                    if 0 <= nx < W and 0 <= ny < H:
                        if (nx, ny) not in other_blocked and (nx, ny) not in selfset:
                            mob += 1

                mind = 999
                for fc in food_coords:
                    cx, cy = fc
                    bidx = cy * W + cx
                    if (nmask >> bidx) & 1:
                        d = abs(tx - cx) + abs(ty - cy)
                        if d < mind:
                            mind = d

                acc2 = acc + 1.0
                if grow:
                    acc2 += 45.0
                    if h < 70:
                        acc2 += (100 - h) * 0.15

                hval = acc2 + len(nb) * 1.5 + mob * 4.0 + nh * 0.05
                if mind < 999:
                    hval -= mind * (4.0 if nh < 50 else 2.0)
                if mob == 0:
                    hval -= 100.0

                expanded.append((hval, nb, nh, nmask, vec, acc2))

        if not expanded:
            break
        expanded.sort(key=lambda z: z[0], reverse=True)
        states = []
        for _, nb, nh, nmask, vec, acc2 in expanded[:beamw]:
            states.append((nb, nh, nmask, vec, acc2))

    best = -1e18
    for b, h, mask, cur, acc in states:
        blocked = bytearray(other_blocked_bool)
        for seg in b[1:]:
            blocked[seg[1] * W + seg[0]] = 1

        start = b[0][1] * W + b[0][0]
        if blocked[start]:
            area = 0
        else:
            seen = bytearray(N)
            seen[start] = 1
            q = [start]
            qi = 0
            area = 0
            while qi < len(q):
                idx = q[qi]
                qi += 1
                area += 1
                if idx >= W:
                    n = idx - W
                    if not seen[n] and not blocked[n]:
                        seen[n] = 1
                        q.append(n)
                if idx < N - W:
                    n = idx + W
                    if not seen[n] and not blocked[n]:
                        seen[n] = 1
                        q.append(n)
                if idx % W != 0:
                    n = idx - 1
                    if not seen[n] and not blocked[n]:
                        seen[n] = 1
                        q.append(n)
                if idx % W != W - 1:
                    n = idx + 1
                    if not seen[n] and not blocked[n]:
                        seen[n] = 1
                        q.append(n)

        val = acc + area * 2.5 + len(b) * 6.0 + h * 0.1
        if val > best:
            best = val

    return best


def decide(state):
    W = state["width"]
    H = state["height"]
    N = W * H
    you = state["you"]
    snakes = state["snakes"]

    me = None
    for s in snakes:
        if s["id"] == you:
            me = s
            break
    if me is None:
        return "up"

    my_body = [(int(p[0]), int(p[1])) for p in me["body"]]
    my_head = my_body[0]
    my_health = int(me.get("health", 100))
    my_len = int(me.get("length", len(my_body)))

    occ_set = set()
    for s in snakes:
        b = s["body"]
        for i in range(len(b) - 1):
            occ_set.add((int(b[i][0]), int(b[i][1])))

    occ_bool = bytearray(N)
    for x, y in occ_set:
        occ_bool[y * W + x] = 1

    food_coords = [(int(f[0]), int(f[1])) for f in state["food"]]
    food_set = set(food_coords)
    food_mask = 0
    food_idx = set()
    for x, y in food_coords:
        idx = y * W + x
        food_mask |= 1 << idx
        food_idx.add(idx)

    other_blocked = set()
    for s in snakes:
        if s["id"] == you:
            continue
        b = s["body"]
        for i in range(len(b) - 1):
            other_blocked.add((int(b[i][0]), int(b[i][1])))

    other_bool = bytearray(N)
    for x, y in other_blocked:
        other_bool[y * W + x] = 1

    op_records = []
    for s in snakes:
        if s["id"] == you:
            continue
        b = s["body"]
        if not b:
            continue
        oh = (int(b[0][0]), int(b[0][1]))
        ocur = infer_dir([(int(p[0]), int(p[1])) for p in b])
        olen = int(s.get("length", len(b)))
        for ov in legal_moves(ocur):
            ox = oh[0] + ov[0]
            oy = oh[1] + ov[1]
            if ox < 0 or ox >= W or oy < 0 or oy >= H:
                continue
            if (ox, oy) in occ_set:
                continue
            op_records.append((ox, oy, olen, s["id"]))

    cur = infer_dir(my_body)
    moves = legal_moves(cur)

    if state["num_snakes"] <= 2:
        depth = 12
        beamw = 12
    else:
        depth = 9
        beamw = 10

    best_vec = None
    best_score = -1e100

    for vec in moves:
        tx = my_head[0] + vec[0]
        ty = my_head[1] + vec[1]
        if tx < 0 or tx >= W or ty < 0 or ty >= H:
            continue
        target = (tx, ty)
        if target in occ_set:
            continue

        grow = target in food_set
        if grow:
            health_after = 100
        else:
            health_after = my_health - 1
            if health_after <= 0:
                continue

        nb_list = [target]
        nb_list.extend(my_body[:-1])
        if grow:
            nb_list.append(nb_list[-1])
        new_len = len(nb_list)

        risk = 0
        aggr = 0
        for rx, ry, olen, _ in op_records:
            if rx == tx and ry == ty:
                olen_after = olen + (1 if grow else 0)
                if olen_after >= new_len:
                    risk += 1
                else:
                    aggr += 1

        score = new_len * 25.0
        if grow:
            score += 180.0
        score += max(0, health_after) * 0.4
        score -= risk * 5000.0
        score += aggr * 35.0

        idx = ty * W + tx
        area, fdist = bfs_metrics(idx, occ_bool, food_idx, W, H, N)
        mob = count_free_neighbors(idx, occ_bool, W, H, N)

        score += min(area, 180) * 4.0
        score += mob * 10.0
        need = new_len + 2
        if area < need:
            score -= (need - area) * 180.0

        if fdist < 999:
            if health_after < 25:
                score += max(0, 350 - fdist * 35)
            elif health_after < 55:
                score += max(0, 180 - fdist * 15)
            else:
                score += max(0, 80 - fdist * 8)
        else:
            if health_after < 70:
                score -= 250.0

        if health_after < 20:
            score -= 150.0

        for s in snakes:
            if s["id"] == you:
                continue
            ob = s["body"]
            if not ob:
                continue
            ox = int(ob[0][0])
            oy = int(ob[0][1])
            d = abs(tx - ox) + abs(ty - oy)
            slen = int(s.get("length", len(ob)))
            if slen >= new_len:
                if d == 1:
                    score -= 130.0
                elif d == 2:
                    score -= 30.0
                elif d == 3:
                    score -= 6.0
            else:
                if d == 1:
                    score += 12.0

        edge = min(tx, ty, W - 1 - tx, H - 1 - ty)
        score += edge * 1.5

        mask_after = (food_mask & ~(1 << idx)) if grow else food_mask
        score += beam_search(
            nb_list, health_after, mask_after, vec,
            other_blocked, other_bool, W, H, N,
            food_coords, depth, beamw
        )

        if score > best_score:
            best_score = score
            best_vec = vec

    if best_vec is None:
        fallback = legal_moves(cur)
        best_vec = None
        best_fb = -1e100
        for vec in fallback:
            tx = my_head[0] + vec[0]
            ty = my_head[1] + vec[1]
            if tx < 0 or tx >= W or ty < 0 or ty >= H:
                continue
            sc = 0.0
            if (tx, ty) in occ_set:
                sc -= 100000.0
            if (tx, ty) in food_set:
                sc += 1000.0
            for d in DIR_VECS:
                nx = tx + d[0]
                ny = ty + d[1]
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in occ_set:
                    sc += 1.0
            if sc > best_fb:
                best_fb = sc
                best_vec = vec
        if best_vec is None:
            if cur is not None:
                best_vec = cur
            else:
                best_vec = (0, -1)

    return DIR_NAMES.get(best_vec, "up")
