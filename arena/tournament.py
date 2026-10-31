"""正式赛。一轮 = 单挑循环赛（55 对 × 换边，110 局）+ 大乱斗一组（11 局，每个选手每个座位各坐一次）。
一轮一轮往下打，直到打满 --rounds 或者有人建了 results/STOP。所有局逐行写进 results/games.jsonl.gz。

python -m arena.tournament --rounds 100 --workers 6
"""
from __future__ import annotations

import argparse
import gzip
import itertools
import json
import multiprocessing as mp
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOTS = ROOT / "bots"
RESULTS = ROOT / "results"
ENTRANTS = ["opus", "astra", "gemini", "deepseek", "kimi", "doubao", "qwen", "glm", "minimax", "grok", "baseline"]

_procs: dict = {}


def _work(task):
    from .referee import BotProc, play
    kind, seed, seats = task
    bots = []
    for name in seats:
        bp = _procs.get(name)
        if bp is None:
            bp = _procs[name] = BotProc(str(BOTS / f"{name}.py"))
        bots.append(bp)
    t0 = time.time()
    rec = play(bots, seed, names=list(seats))
    rec["kind"] = kind
    rec["wall"] = round(time.time() - t0, 2)
    return rec


def round_tasks(r: int, names: list[str]):
    tasks = []
    for a, b in itertools.combinations(names, 2):
        seed = 100000 + r
        tasks.append(("duel", seed, (a, b)))
        tasks.append(("duel", seed, (b, a)))
    perm = names[:]
    random.Random(900000 + r).shuffle(perm)
    for k in range(len(names)):
        tasks.append(("melee", 500000 + r * 100 + k, tuple(perm[k:] + perm[:k])))
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=str(RESULTS / "games.jsonl.gz"))
    a = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)
    stop = RESULTS / "STOP"
    names = [n for n in ENTRANTS if (BOTS / f"{n}.py").exists()]
    print("选手", names, flush=True)
    with mp.Pool(a.workers) as pool, gzip.open(a.out, "at") as fh:
        for r in range(a.start, a.start + a.rounds):
            if stop.exists():
                print("收到 STOP，停在第", r, "轮之前", flush=True)
                break
            t0 = time.time()
            tasks = round_tasks(r, names)
            # 大乱斗先发，慢的先跑
            tasks.sort(key=lambda t: t[0] != "melee")
            n = 0
            for rec in pool.imap_unordered(_work, tasks):
                rec["round"] = r
                fh.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
                n += 1
            fh.flush()
            print(f"第 {r} 轮 {n} 局 {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
