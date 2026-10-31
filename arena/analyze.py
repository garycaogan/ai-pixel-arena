"""正式赛结果汇总：实力值（总榜、单挑、大乱斗）、两两胜率、每位选手的打法数据。

python -m arena.analyze results/games.jsonl.gz --out results/
写出 ratings.json、ratings.md、pairwise.csv、player-stats.csv。
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

from . import bt

NAMES = {"opus": "Claude Opus 5.5", "astra": "GPT-6 Astra", "gemini": "Gemini 4 Argon", "deepseek": "DeepSeek V4.1 Flash",
         "kimi": "Kimi K3", "doubao": "豆包 Seed 2.0 Pro", "qwen": "Qwen 3.8 Max", "glm": "GLM 5.3",
         "minimax": "MiniMax M3.1 Flash", "grok": "Grok 4.7", "baseline": "陪练基准"}


def load(path):
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            r.pop("moves", None)
            rows.append(r)
    return rows


def stats(rows, names):
    st = {n: defaultdict(float) for n in names}
    for r in rows:
        k = r["kind"]
        n = len(r["seats"])
        for i, who in enumerate(r["seats"]):
            s = st[who]
            s[f"{k}_games"] += 1
            place = r["place"][i]
            if k == "duel":
                other = r["place"][1 - i]
                s["duel_win"] += 1.0 if place < other else 0.5 if place == other else 0.0
            else:
                s["melee_place_sum"] += place
                s["melee_first"] += 1 if place == 1 else 0
                s["melee_top3"] += 1 if place <= 3 else 0
            d = r["death"][i]
            if d is None:
                s[f"{k}_survive"] += 1
            else:
                s[f"{k}_death_{d[1]}"] += 1
                s[f"{k}_death_turn_sum"] += d[0]
            s[f"{k}_kills"] += r["kills"][i]
            s[f"{k}_ate"] += r["ate"][i]
            s[f"{k}_len_sum"] += r["length"][i]
            pst = r["stats"][i]
            for key in ("timeouts", "errors", "invalid", "killed"):
                s[key] += pst[key]
            s["cpu_sum"] += pst["cpu"]
            s["moves"] += pst["turns"]
            s["max_cpu"] = max(s["max_cpu"], pst["max_cpu"])
    out = {}
    for n, s in st.items():
        d = {k: v for k, v in s.items()}
        dg, mg = s["duel_games"] or 1, s["melee_games"] or 1
        d["duel_winrate"] = s["duel_win"] / dg
        d["melee_avg_place"] = s["melee_place_sum"] / mg
        d["melee_first_rate"] = s["melee_first"] / mg
        d["melee_survive_rate"] = s["melee_survive"] / mg
        d["duel_kills_avg"] = s["duel_kills"] / dg
        d["melee_kills_avg"] = s["melee_kills"] / mg
        d["melee_len_avg"] = s["melee_len_sum"] / mg
        d["duel_len_avg"] = s["duel_len_sum"] / dg
        d["melee_ate_avg"] = s["melee_ate"] / mg
        d["cpu_ms_avg"] = 1000 * s["cpu_sum"] / (s["moves"] or 1)
        d["max_cpu_ms"] = 1000 * s["max_cpu"]
        out[n] = d
    return out


def pairwise(rows, names):
    w = defaultdict(float)
    g = defaultdict(int)
    for r in rows:
        if r["kind"] != "duel":
            continue
        a, b = r["seats"]
        pa, pb = r["place"]
        sa = 1.0 if pa < pb else 0.5 if pa == pb else 0.0
        w[a, b] += sa
        w[b, a] += 1 - sa
        g[a, b] += 1
        g[b, a] += 1
    return {(a, b): (w[a, b] / g[a, b] if g[a, b] else None, g[a, b]) for a in names for b in names if a != b}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("--out", default="results")
    ap.add_argument("--boot", type=int, default=200)
    a = ap.parse_args()
    rows = load(a.games)
    names = sorted({s for r in rows for s in r["seats"]})
    total = bt.rate(rows, names, boot=a.boot)
    duel = bt.rate([r for r in rows if r["kind"] == "duel"], names, boot=a.boot)
    melee = bt.rate([r for r in rows if r["kind"] == "melee"], names, boot=a.boot)
    st = stats(rows, names)
    order = sorted(names, key=lambda n: -total[n][0])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    counts = {k: sum(1 for r in rows if r["kind"] == k) for k in ("duel", "melee")}
    res = {"games": len(rows), "counts": counts, "rounds": len({r["round"] for r in rows}),
           "order": order,
           "total": {n: [round(x, 1) for x in total[n]] for n in names},
           "duel": {n: [round(x, 1) for x in duel[n]] for n in names},
           "melee": {n: [round(x, 1) for x in melee[n]] for n in names},
           "stats": st}
    (out / "ratings.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    pw = pairwise(rows, names)
    with open(out / "pairwise.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["行胜列（单挑胜率）"] + order)
        for x in order:
            wr.writerow([x] + ["" if x == y else f"{pw[x, y][0]:.3f}" for y in order])
    keys = ["duel_games", "duel_winrate", "melee_games", "melee_avg_place", "melee_first_rate", "melee_survive_rate",
            "melee_kills_avg", "melee_len_avg", "melee_ate_avg", "duel_kills_avg", "timeouts", "errors", "invalid", "killed",
            "cpu_ms_avg", "max_cpu_ms"]
    with open(out / "player-stats.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["选手"] + keys)
        for n in order:
            wr.writerow([n] + [round(st[n].get(k, 0), 4) for k in keys])
    lines = [f"# 正式赛成绩\n\n共 {len(rows)} 局：单挑 {counts['duel']} 局，大乱斗 {counts['melee']} 局。"
             "实力值用 Bradley–Terry 拟合，陪练基准 = 0，强 10 倍记 +400；两种赛制总权重相等。区间是 95% 重抽样区间。\n",
             "| 名次 | 选手 | 实力值 | 95% 区间 | 单挑 | 大乱斗 | 单挑胜率 | 大乱斗平均名次 |", "|---:|---|---:|---|---:|---:|---:|---:|"]
    for i, n in enumerate(order, 1):
        p, lo, hi = total[n]
        lines.append(f"| {i} | {NAMES.get(n, n)} | {p:.0f} | {lo:.0f} ~ {hi:.0f} | {duel[n][0]:.0f} | {melee[n][0]:.0f} | "
                     f"{st[n]['duel_winrate']*100:.1f}% | {st[n]['melee_avg_place']:.2f} |")
    (out / "ratings.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
