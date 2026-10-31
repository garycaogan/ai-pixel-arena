"""写程序这一步的账：每家真实 token、按实测单价折算的花费、账户余额的真实总变化。

为什么不用「每次请求前后的余额差」直接分给各家：长时间的流式请求扣费会延后入账，
千问（25 分钟）那次余额只变了 0.13、GLM（32 分钟）那次是 0，钱落到了后面 Grok 的时段里。
所以每家的花费 = 它所有请求（含作废重跑）的真实 token × 实测单价（tools/unit_prices.py），
总数再和账户余额的真实变化对一遍。1 credit = 0.1 元（用出图任务的人民币账单对过：4.2629 credit = ¥0.427）。

python tools/ledger.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["opus", "astra", "gemini", "deepseek", "kimi", "doubao", "qwen", "glm", "minimax", "grok"]
CNY_PER_CREDIT = 0.427 / 4.2629


def billed(u):
    u = u or {}
    pi, po = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
    tot = int(u.get("total_tokens") or 0)
    if tot > pi + po:
        po = tot - pi
    return pi, po


def requests_of(slug):
    """这一家所有真实发出去的请求：计入成绩的、截断作废的、更早整轮作废的。"""
    out = []
    d = ROOT / "contest" / slug
    if (d / "log.json").exists():
        log = json.loads((d / "log.json").read_text())
        for a in log.get("void", []):
            out.append(("作废（截断）", a))
        for a in log["attempts"]:
            out.append(("计入", a))
    for vd in sorted((ROOT / "contest" / "void").glob(f"{slug}-*/log.json")):
        for a in json.loads(vd.read_text()).get("attempts", []):
            out.append(("作废（整轮）", a))
    if slug == "gemini":
        vl = json.loads((ROOT / "contest" / "void" / "log.json").read_text())
        for a in vl["items"]:
            if a["slug"] == "gemini" and a.get("usage"):
                out.append(("作废（上限 32000）", {"usage": {"prompt_tokens": a["usage"]["prompt_tokens"],
                                                         "completion_tokens": a["usage"]["completion_tokens"]}}))
    if slug == "qwen":
        # 第二轮被截断的那次没写 log.json，用量取自当时的运行记录
        out.append(("作废（截断）", {"usage": {"prompt_tokens": 2108, "completion_tokens": 8425}}))
    return out


def main():
    prices = json.loads((ROOT / "contest" / "unit_prices.json").read_text())
    facts = json.loads((ROOT / "contest" / "facts.json").read_text())
    rows = []
    for slug in ORDER:
        f = facts[slug]
        api = f["channel"] == "Evolink API"
        reqs = requests_of(slug) if api else []
        tin = tout = 0
        for _, a in reqs:
            if a.get("result") == "request_error":
                continue
            pi, po = billed(a.get("usage"))
            tin += pi
            tout += po
        r = {"slug": slug, "model": f["model"], "channel": f["channel"],
             "requests": len([1 for _, a in reqs if a.get("result") != "request_error"]) if api else None,
             "counted": f["attempts"], "input": tin, "output": tout}
        if api:
            p = prices[slug]
            cr = tin / 1e6 * p["credits_per_M_in"] + tout / 1e6 * p["credits_per_M_out"]
            r.update(credits=round(cr, 2), cny=round(cr * CNY_PER_CREDIT, 2),
                     price_in=round(p["credits_per_M_in"], 1), price_out=round(p["credits_per_M_out"], 1))
        else:
            r.update(credits=None, cny=None)
            if slug == "opus":
                r.update(input=61286, output=86287, note="本机 Claude Code 子代理，用量取自它的记录；走订阅，不按 API 计费")
            if slug == "astra":
                r.update(input=None, output=None, note="Mac Pro 上的 Codex，桥接不返回用量；走订阅，不按 API 计费")
        rows.append(r)
    # 账户余额的真实变化：从 Gemini 第二轮第一次请求之前，到 Kimi 最后一次请求之后（公开版只留差值，不留账户读数）
    window = 473.7234
    paid = [r for r in rows if r["credits"] is not None]
    total_est = sum(r["credits"] for r in paid)
    early = 24.5954  # Gemini 第一轮（上限 32000）发生在这个区间之前，余额差就是它
    out = {"cny_per_credit": CNY_PER_CREDIT, "rows": rows,
           "account_window": {"credits": round(window, 2), "cny": round(window * CNY_PER_CREDIT, 2),
                              "note": "10/21 04:23–07:21 UTC 账户余额的真实变化，含 8 次 65536 上限试探、所有计入和作废的请求；"
                                      "同一把 key 在这段时间也可能被别的任务用到（每次几百到一两千 token）"},
           "before_window_credits": early,
           "estimated_total_credits": round(total_est, 2), "estimated_total_cny": round(total_est * CNY_PER_CREDIT, 2)}
    (ROOT / "contest" / "ledger.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    lines = ["# 写程序的用量和花费\n",
             "每家的花费 = 它发出的所有请求（含作废重跑）的真实 token × 实测单价。"
             "实测单价是用两次受控请求在 Evolink 上量出来的（`tools/unit_prices.py`，结果在 `contest/unit_prices.json`）。"
             "没有直接用每次请求前后的余额差，是因为长时间的流式请求扣费会延后入账，余额差会把前一家的钱记到后一家头上。"
             "1 credit = 0.1 元（出图任务账单 ¥0.427 对应扣费 4.2629 credit）。\n",
             "| 选手 | 接入 | 发出请求 | 计入成绩 | 输入 token | 输出 token（含思考） | 实测单价（credit / 百万 token，入 / 出） | 花费 |",
             "|---|---|---:|---:|---:|---:|---|---:|"]
    for r in rows:
        if r["cny"] is None:
            lines.append(f"| {r['model']} | {r['channel']} | — | {r['counted']} | {r['input'] or '拿不到'} | {r['output'] or '拿不到'} | — | 不适用 |")
        else:
            lines.append(f"| {r['model']} | {r['channel']} | {r['requests']} | {r['counted']} | {r['input']:,} | {r['output']:,} | "
                         f"{r['price_in']} / {r['price_out']} | ¥{r['cny']:.2f} |")
    w = out["account_window"]
    lines += ["", f"按单价折算的合计：{out['estimated_total_credits']} credit，约 ¥{out['estimated_total_cny']}。",
              f"账户余额在比赛窗口里的真实变化：{w['credits']} credit，约 ¥{w['cny']}（{w['note']}）。"
              f"在这之前，Gemini 第一轮作废的那次单独扣了 {early} credit。"]
    doc = ROOT / "docs" / "LEDGER.md"
    # 「做视频的花费」那节是照账单手写的，重算写程序这部分时原样保留
    old = doc.read_text() if doc.exists() else ""
    keep = old[old.index("\n## 做视频的花费"):] if "\n## 做视频的花费" in old else ""
    doc.write_text("\n".join(lines) + "\n" + keep)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
