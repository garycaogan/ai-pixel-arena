"""从正赛里挑片子要放的对局，导出回放数据，写 results/picks.json。

挑法（写进开源说明，不挑反杀）：
- 单挑：总榜第 1 对第 2 的所有对局里，回合数最接近这对选手中位数的一局（典型局）。
- 大乱斗：名次和总榜排名最一致（Spearman 相关最高）的一局，相关一样取回合数多的。
- 开场：大乱斗里事件最集中的那段（同一局），只截一小段。

.venv/bin/python video/pick_games.py results/games.jsonl.gz
"""
import gzip
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from arena.export import export  # noqa: E402


def spearman(a, b):
    n = len(a)
    ra = {x: i for i, x in enumerate(a)}
    d2 = sum((ra[x] - i) ** 2 for i, x in enumerate(b))
    return 1 - 6 * d2 / (n * (n * n - 1))


def load(path):
    with gzip.open(path, "rt") as fh:
        for line in fh:
            yield json.loads(line)


def main(path, ratings_path=ROOT / "results" / "ratings.json", out_dir=ROOT / "results" / "games"):
    out_dir = Path(out_dir).resolve()
    R = json.loads(Path(ratings_path).read_text())
    order = R["order"]
    top1, top2 = [s for s in order if s != "baseline"][:2]
    duels, melees, duels34 = [], [], []
    top3, top4 = [s for s in order if s != "baseline"][2:4]
    for r in load(path):
        if r["kind"] == "duel" and set(r["seats"]) == {top1, top2}:
            duels.append(r)
        elif r["kind"] == "duel" and set(r["seats"]) == {top3, top4}:
            duels34.append(r)
        elif r["kind"] == "melee":
            r2 = {k: v for k, v in r.items() if k != "moves"}
            r2["_line"] = r
            melees.append(r2)
    out_dir.mkdir(parents=True, exist_ok=True)
    picks = {}
    if duels:
        med = statistics.median(r["turns"] for r in duels)
        d = min(duels, key=lambda r: (abs(r["turns"] - med), r["round"]))
        picks["duel_top"] = {"round": d["round"], "seed": d["seed"], "seats": d["seats"], "turns": d["turns"],
                             "place": d["place"], "file": str((out_dir / "duel_top.json").relative_to(ROOT)),
                             "why": f"总榜第 1、2 名的 {len(duels)} 局单挑里，回合数最接近中位数（{med:g}）的一局"}
        (out_dir / "duel_top.json").write_text(json.dumps(export(d)))
        wins = sum(1 for r in duels if r["place"][r["seats"].index(top1)] < r["place"][r["seats"].index(top2)])
        picks["duel_top"]["record"] = {"games": len(duels), "top1_wins": wins,
                                       "draws": sum(1 for r in duels if r["place"][0] == r["place"][1])}
    if duels34:
        med = statistics.median(r["turns"] for r in duels34)
        d = min(duels34, key=lambda r: (abs(r["turns"] - med), r["round"]))
        w3 = sum(1 for r in duels34 if r["place"][r["seats"].index(top3)] < r["place"][r["seats"].index(top4)])
        picks["duel_34"] = {"round": d["round"], "seed": d["seed"], "seats": d["seats"], "turns": d["turns"], "place": d["place"],
                            "file": str((out_dir / "duel_34.json").relative_to(ROOT)),
                            "why": f"总榜第 3、4 名的 {len(duels34)} 局单挑里，回合数最接近中位数（{med:g}）的一局",
                            "record": {"games": len(duels34), "top3_wins": w3,
                                       "draws": sum(1 for r in duels34 if r["place"][0] == r["place"][1])}}
        (out_dir / "duel_34.json").write_text(json.dumps(export(d)))
    best = None
    for r in melees:
        ranked = [s for _, s in sorted(zip(r["place"], r["seats"]))]
        rho = spearman([s for s in order if s in r["seats"]], ranked)
        key = (round(rho, 3), r["turns"])
        if best is None or key > best[0]:
            best = (key, r)
    if best:
        m = best[1]["_line"]
        picks["melee_typical"] = {"round": m["round"], "seed": m["seed"], "seats": m["seats"], "turns": m["turns"],
                                  "place": m["place"], "spearman": best[0][0], "file": str((out_dir / "melee_typical.json").relative_to(ROOT)),
                                  "why": f"{len(melees)} 局大乱斗里，名次和总榜最一致的一局（Spearman {best[0][0]}）"}
        (out_dir / "melee_typical.json").write_text(json.dumps(export(m)))
    # 开场：千问饿死在第 100 回合、一口没吃、冠军赢下的大乱斗里，名次和总榜最一致的一局
    top = [s for s in order if s != "baseline"][0]
    cand = []
    for r in melees:
        i = r["seats"].index("qwen")
        d = r["death"][i]
        if d and d[1] == "starve" and d[0] == 100 and r["ate"][i] == 0 and r["place"][r["seats"].index(top)] == 1:
            ranked = [s for _, s in sorted(zip(r["place"], r["seats"]))]
            cand.append((spearman([x for x in order if x in r["seats"]], ranked), r["turns"], r))
    if cand:
        rho, _, c = max(cand, key=lambda x: (round(x[0], 3), x[1]))
        n_starve = sum(1 for r in melees if (lambda d: d and d[1] == "starve" and d[0] == 100)(r["death"][r["seats"].index("qwen")]))
        picks["cold"] = {"round": c["round"], "seed": c["seed"], "who": "qwen", "color_word": "粉色", "file": str((out_dir / "cold.json").relative_to(ROOT)),
                         "why": f"千问在第 100 回合饿死、一口没吃、总榜第一赢下的 {len(cand)} 局大乱斗里，名次和总榜最一致的一局（Spearman {rho:.3f}）",
                         "qwen_starve_at_100": n_starve, "melees": len(melees)}
        (out_dir / "cold.json").write_text(json.dumps(export(c["_line"])))
    (out_dir.parent / "picks.json").write_text(json.dumps(picks, ensure_ascii=False, indent=1))
    print(json.dumps(picks, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], *(sys.argv[2:3] or []))
