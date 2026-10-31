"""把一局（种子 + 走法记录）重放成画面要用的紧凑数据。

每条蛇：每回合的蛇头位置、可见长度（去掉叠在一起的格子后的节数）、生命值；
食物：每回合的位置表（只在变化时记一次）；事件：吃、死（原因、凶手）。
身体 = 最近 k 个蛇头位置，所以只存蛇头就够了。
"""
from __future__ import annotations

import json

from .snake import Game, FROM_LETTER


def _distinct(body):
    out = [body[0]]
    for p in body[1:]:
        if p != out[-1]:
            out.append(p)
    return len(out)


def export(rec: dict) -> dict:
    n, seed, rows = rec["n"], rec["seed"], rec["moves"]
    g = Game.new(n, seed)
    heads = [[list(s.head)] for s in g.snakes]
    vis = [[1] for _ in g.snakes]
    hp = [[s.health] for s in g.snakes]
    lens = [[len(s.body)] for s in g.snakes]
    food = [[0, [list(f) for f in g.food]]]
    events = []
    for row in rows:
        moves = {i: FROM_LETTER[c] for i, c in enumerate(row) if c in FROM_LETTER and g.snakes[i].alive}
        alive_before = [s.alive for s in g.snakes]
        ev = g.step(moves)
        events.extend(ev)
        for s in g.snakes:
            if alive_before[s.id]:
                heads[s.id].append(list(s.head))
                vis[s.id].append(_distinct(s.body))
                hp[s.id].append(s.health)
                lens[s.id].append(len(s.body))
        cur = [list(f) for f in g.food]
        if cur != food[-1][1]:
            food.append([g.turn, cur])
    return {
        "n": n, "seed": seed, "w": g.width, "turns": g.turn, "seats": rec["seats"],
        "place": g.placements(),
        "heads": heads, "vis": vis, "hp": hp, "len": lens, "food": food, "events": events,
        "death": [None if s.alive else s.death_turn for s in g.snakes],
    }


if __name__ == "__main__":
    import gzip
    import sys
    want = sys.argv[2:]
    with gzip.open(sys.argv[1], "rt") as fh:
        for line in fh:
            r = json.loads(line)
            print(json.dumps(export(r))[:200])
            break
