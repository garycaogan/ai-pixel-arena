"""陪练基准：中等强度、思路常规。正式排名里它是 0 分线。

每回合：排除马上会死的方向，避开比自己长（或一样长）的蛇头旁边的格子，
用洪水填充看每个方向还剩多少空间，空间够用的方向里，选离最近食物最近的那个。
"""
from collections import deque

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def decide(state):
    w, h = state["width"], state["height"]
    me = next(s for s in state["snakes"] if s["id"] == state["you"])
    head = tuple(me["body"][0])
    blocked = set()
    for s in state["snakes"]:
        body = [tuple(p) for p in s["body"]]
        # 蛇尾下回合会移开（刚吃过的除外，那时尾巴是重叠的两节）
        tail_moves = len(body) > 1 and body[-1] != body[-2]
        blocked.update(body[:-1] if tail_moves else body)
    danger = set()
    for s in state["snakes"]:
        if s["id"] == me["id"]:
            continue
        if s["length"] >= me["length"]:
            hx, hy = s["body"][0]
            for dx, dy in DIRS.values():
                danger.add((hx + dx, hy + dy))

    def ok(p):
        return 0 <= p[0] < w and 0 <= p[1] < h and p not in blocked

    def space(start, cap):
        seen = {start}
        q = deque([start])
        while q and len(seen) < cap:
            x, y = q.popleft()
            for dx, dy in DIRS.values():
                n = (x + dx, y + dy)
                if n not in seen and ok(n):
                    seen.add(n)
                    q.append(n)
        return len(seen)

    def food_dist(start):
        food = {tuple(f) for f in state["food"]}
        if not food:
            return 0
        seen = {start}
        q = deque([(start, 0)])
        while q:
            p, d = q.popleft()
            if p in food:
                return d
            for dx, dy in DIRS.values():
                n = (p[0] + dx, p[1] + dy)
                if n not in seen and ok(n):
                    seen.add(n)
                    q.append((n, d + 1))
        return 999

    options = []
    for name, (dx, dy) in DIRS.items():
        p = (head[0] + dx, head[1] + dy)
        if not ok(p):
            continue
        room = space(p, me["length"] * 2)
        options.append((p in danger, room < me["length"], food_dist(p), -room, name))
    if not options:
        return "up"
    options.sort()
    return options[0][-1]
