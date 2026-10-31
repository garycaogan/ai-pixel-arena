"""规则演示：在小棋盘上摆好局面、按写好的走法跑真实引擎，导出给画面用。

每个演示都是 snake.Game 真跑出来的，不是手画的动画，所以画面和规则一字不差。
导出格式和 export.py 一样，只是多了 bodies（每回合每条蛇的完整身体），因为开局身体是摆出来的。
"""
from __future__ import annotations

import json
import random

from .snake import Game, Snake, DIRS


def _setup(w, snakes, food, health=None):
    g = Game(n=len(snakes), seed=0)
    g.width = g.height = w
    g.rng = random.Random(0)
    for i, body in enumerate(snakes):
        g.snakes.append(Snake(id=i, body=[tuple(p) for p in body], health=(health or {}).get(i, 100)))
    g.food = [tuple(f) for f in food]
    return g


def _run(g, script, tail=4):
    """script: 每回合的方向列表（按蛇的 id），None 表示沿原方向。演示里吃掉的食物不补，棋盘上只留摆好的那几颗。"""
    allowed = set(g.food)
    frames = [_snap(g)]
    for step in script:
        moves = {}
        for i, s in enumerate(g.snakes):
            if s.alive:
                moves[i] = step[i] if step and i < len(step) and step[i] else (s.direction() or "up")
        before = set(g.food)
        g.step(moves)
        allowed -= before - set(g.food)
        g.food = [f for f in g.food if f in allowed]
        frames.append(_snap(g))
    for _ in range(tail):
        frames.append(frames[-1])
    return frames


def _snap(g):
    return {"bodies": [[list(p) for p in s.body] if s.alive else None for s in g.snakes],
            "hp": [s.health for s in g.snakes], "food": [list(f) for f in g.food],
            "dead": [None if s.alive else s.death_cause for s in g.snakes]}


def build():
    demos = {}
    # 1 移动和吃食物：往右走，吃到樱桃，身体长一节
    g = _setup(9, [[(2, 4), (1, 4), (0, 4)]], [(5, 4)])
    fr = _run(g, [["right"]] * 3 + [["down"], ["down"], ["left"]], tail=6)
    demos["eat"] = fr
    # 2 撞墙
    g = _setup(9, [[(5, 2), (4, 2), (3, 2)]], [(1, 7)])
    demos["wall"] = _run(g, [["right"]] * 5, tail=8)
    # 3 撞身体：橙蛇横穿过来撞上绿蛇的身体
    g = _setup(9, [[(1, 2), (0, 2), (0, 1)], [(4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6)]], [(7, 7)])
    demos["body"] = _run(g, [["right", "up"]] * 1 + [["right", "right"]] + [["right", "right"]] * 2, tail=8)
    # 4 撞头：两条蛇的头进了同一格，长的活下来
    g = _setup(9, [[(1, 4), (0, 4), (0, 3), (0, 2), (0, 1)], [(7, 4), (8, 4), (8, 5)]], [(4, 8)])
    demos["head"] = _run(g, [["right", "left"]] * 3, tail=8)
    # 5 跟尾巴：尾巴每回合会缩回去，所以可以贴着别人的尾巴走
    g = _setup(9, [[(2, 5), (2, 6), (2, 7)], [(6, 4), (5, 4), (4, 4), (3, 4), (2, 4)]], [(8, 8)])
    demos["tail"] = _run(g, [["up", "right"], ["right", "right"], ["right", "down"], ["right", "down"]], tail=6)
    # 6 饥饿：生命值每回合减 1，到 0 就饿死
    g = _setup(9, [[(1, 1), (1, 2), (1, 3)]], [(7, 7)], health={0: 6})
    script = [["right"]] * 6
    demos["hunger"] = _run(g, script, tail=8)
    return demos


if __name__ == "__main__":
    d = build()
    for k, fr in d.items():
        print(k, len(fr), [f["dead"] for f in fr][-1], [f["hp"][0] for f in fr][:8])
    print(json.dumps(d)[:300])
