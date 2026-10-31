"""Bradley–Terry 实力值。

- 每局按名次拆成两两比较：名次靠前记胜，并列记半胜。
- 单挑和大乱斗两种赛制总权重相等（大乱斗一局能拆出 55 组比较，不加权会压过单挑）。
- 每对选手额外加一局虚拟平局，防止全胜或全负时发散。
- 陪练基准 = 0 分；强 10 倍（期望胜率约 91%）记 +400。
- 95% 区间：在每种赛制内按局重抽样，重新拟合。
"""
from __future__ import annotations

import itertools
import math
import random
from collections import defaultdict


def comparisons(rows, kinds=None):
    kinds = kinds or sorted({r["kind"] for r in rows})
    count = {k: sum(1 for r in rows if r["kind"] == k) for k in kinds}
    pairs = defaultdict(lambda: [0.0, 0.0])
    total = len(rows)
    for r in rows:
        if r["kind"] not in count:
            continue
        seats, place = r["seats"], r["place"]
        valid = list(itertools.combinations(range(len(seats)), 2))
        w = total / (len(kinds) * count[r["kind"]] * len(valid))
        for i, j in valid:
            a, b = seats[i], seats[j]
            win = 1.0 if place[i] < place[j] else 0.5 if place[i] == place[j] else 0.0
            if a > b:
                a, b, win = b, a, 1 - win
            pairs[a, b][0] += w
            pairs[a, b][1] += w * win
    return pairs


def fit(rows, names, anchor="baseline", kinds=None):
    pairs = comparisons(rows, kinds)
    games = {p: (g + 1, w + 0.5) for p, (g, w) in pairs.items()}
    wins = dict.fromkeys(names, 0.0)
    for (a, b), (g, w) in games.items():
        wins[a] += w
        wins[b] += g - w
    s = dict.fromkeys(names, 1.0)
    for _ in range(5000):
        den = dict.fromkeys(names, 0.0)
        for (a, b), (g, _w) in games.items():
            v = g / (s[a] + s[b])
            den[a] += v
            den[b] += v
        new = {n: wins[n] / den[n] if den[n] else 1.0 for n in names}
        c = sum(math.log(v) for v in new.values()) / len(names)
        new = {n: math.exp(math.log(v) - c) for n, v in new.items()}
        delta = max(abs(math.log(new[n] / s[n])) for n in names)
        s = new
        if delta < 1e-9:
            break
    o = math.log(s[anchor])
    return {n: 400 / math.log(10) * (math.log(s[n]) - o) for n in names}


def rate(rows, names, anchor="baseline", kinds=None, boot=200, seed=0):
    point = fit(rows, names, anchor, kinds)
    rng = random.Random(seed)
    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r["kind"]].append(r)
    samples = defaultdict(list)
    for _ in range(boot):
        sample = []
        for k, rs in by_kind.items():
            if kinds and k not in kinds:
                continue
            sample.extend(rs[rng.randrange(len(rs))] for _ in range(len(rs)))
        est = fit(sample, names, anchor, kinds)
        for n in names:
            samples[n].append(est[n])
    out = {}
    for n in names:
        xs = sorted(samples[n])
        lo, hi = xs[int(0.025 * len(xs))], xs[min(len(xs) - 1, int(0.975 * len(xs)))]
        out[n] = (point[n], lo, hi)
    return out
