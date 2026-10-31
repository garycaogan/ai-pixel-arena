"""交卷后的自检：12 局，对手全是陪练基准。所有选手用同一组种子和同一个报告模板。

只看程序有没有出错（报错、超时、返回值不对、进程卡死），不报胜负。
python -m arena.selfcheck bots/xxx.py [--report out.txt]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .referee import BotProc, play, TURN_LIMIT

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "bots" / "baseline.py"
# (人数, 种子, 选手坐几号位)
GAMES = [(2, 1001, 0), (2, 1001, 1), (2, 1002, 0), (2, 1002, 1), (2, 1003, 0), (2, 1003, 1),
         (11, 2001, 0), (11, 2002, 3), (11, 2003, 5), (11, 2004, 7), (11, 2005, 9), (11, 2006, 10)]
KIND = {"errors": "代码报错", "timeouts": "超时", "invalid": "返回值不对", "killed": "进程卡死或退出"}


def run(bot_path: str) -> dict:
    cand = BotProc(bot_path)
    pool = [BotProc(str(BASELINE)) for _ in range(10)]
    games = []
    try:
        for n, seed, seat in GAMES:
            others = iter(pool)
            bots = [cand if i == seat else next(others) for i in range(n)]
            rec = play(bots, seed, collect_errors=True)
            mine = rec["stats"][seat]
            errs = [e for e in rec["errors"] if e["seat"] == seat]
            games.append({"n": n, "seed": seed, "seat": seat, "stats": mine, "errors": errs,
                          "turns_played": mine["turns"]})
    finally:
        for b in [cand] + pool:
            b.kill()
    totals = {k: sum(g["stats"][k] for g in games) for k in KIND}
    max_cpu = max(g["stats"]["max_cpu"] for g in games)
    return {"passed": not any(totals.values()), "totals": totals, "max_cpu_ms": round(max_cpu * 1000, 2),
            "games": games}


def _clean(tb: str) -> str:
    """去掉外壳自己的那一帧，只留选手代码里的位置。"""
    out, skip = [], False
    for ln in tb.splitlines():
        if skip:
            skip = False
            continue
        if "runner.py" in ln:
            skip = True
            continue
        out.append(ln)
    return "\n".join(out)


def report(result: dict, attempt: int, attempts_total: int = 2) -> str:
    """出错时发给选手的报告（所有选手同一个模板）。"""
    t = result["totals"]
    lines = ["自检结果：未通过。",
             "自检一共 12 局（6 局单挑、6 局大乱斗，对手都是陪练基准）。你的程序在这 12 局里："
             + "，".join(f"{KIND[k]} {t[k]} 次" for k in KIND) + "。",
             f"单回合最多用了 {result['max_cpu_ms']} 毫秒 CPU（上限 {TURN_LIMIT*1000:.0f} 毫秒，第 1 回合 1000 毫秒）。", ""]
    seen = set()
    shown = 0
    for gi, g in enumerate(result["games"], 1):
        for e in g["errors"]:
            sig = (e["kind"], (e["detail"] or "")[-300:] if e["kind"] == "errors" else e["kind"])
            if sig in seen:
                continue
            seen.add(sig)
            shown += 1
            mode = "单挑" if g["n"] == 2 else "大乱斗"
            lines.append(f"问题 {shown}：第 {gi} 局（{mode}，你是 {g['seat']} 号），第 {e['turn']} 回合，{KIND[e['kind']]}。")
            lines.append(_clean(str(e["detail"])).strip()[-2500:])
            if e.get("state"):
                st = json.dumps(e["state"], ensure_ascii=False, separators=(",", ":"))
                lines.append("当时的 state：" + (st if len(st) <= 3000 else st[:3000] + "……（后面省略）"))
            lines.append("")
            if shown >= 3:
                break
        if shown >= 3:
            break
    lines.append(f"这是你的第 {attempt} 次修复机会（一共 {attempts_total} 次）。请修好以后按原来的格式重新交一次：回复里只放一个 ```python 代码块，里面是完整的 bot.py，后面可以用不超过 300 字说明改了什么。")
    return "\n".join(lines)


if __name__ == "__main__":
    res = run(sys.argv[1])
    print(json.dumps({k: v for k, v in res.items() if k != "games"}, ensure_ascii=False))
    if "--report" in sys.argv and not res["passed"]:
        Path(sys.argv[sys.argv.index("--report") + 1]).write_text(report(res, 1))
