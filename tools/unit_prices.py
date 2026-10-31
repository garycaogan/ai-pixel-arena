"""实测 Evolink 上每个选手模型的输入、输出单价（credit / 百万 token）。

长时间的流式请求扣费会延后入账，按「请求前后余额差」给每家分摊不可靠，所以单独量单价：
每个模型发两次短请求，一次大输入小输出，一次小输入大输出；每次请求后等余额稳定再读。
解两个方程得到输入价和输出价。结果写 contest/unit_prices.json。

python tools/unit_prices.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contest import MODELS, credits, stream_chat  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FILLER = (ROOT / "prompt" / "PROMPT.md").read_text() * 6


def settle(c_before, wait=20):
    """等余额不再变化。"""
    last = credits()
    for _ in range(12):
        time.sleep(wait)
        now = credits()
        if abs(now - last) < 1e-6:
            return now - c_before
        last = now
    return last - c_before


def tokens(u):
    """计费的输入和输出。Grok 的 completion_tokens 不含思考，思考 token 单独列，所以输出取 总数 − 输入。"""
    u = u or {}
    pi, po = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
    tot = int(u.get("total_tokens") or 0)
    if tot > pi + po:
        po = tot - pi
    return pi, po


def main(only=None):
    path = ROOT / "contest" / "unit_prices.json"
    out = json.loads(path.read_text()) if path.exists() else {}
    for slug, model in MODELS.items():
        if only and slug not in only:
            continue
        rows = []
        for kind, msg, mx in [("in", "下面这段文字只读一遍，读完只回复一个字：好。\n\n" + FILLER, 50),
                              ("out", "写一篇大约 2500 字的贪吃蛇游戏策略介绍，分小节写，不要用表格。", 6000)]:
            c0 = credits()
            r = stream_chat(model, [{"role": "user", "content": msg}], {"reasoning_effort": "low", "max_tokens": mx})
            d = settle(c0)
            pi, po = tokens(r.get("usage"))
            rows.append({"kind": kind, "prompt": pi, "completion": po, "credits": round(d, 5), "seconds": r.get("seconds"),
                         "error": r.get("error"), "usage": r.get("usage")})
            print(slug, kind, pi, po, round(d, 5), flush=True)
        (a1, b1, c1), (a2, b2, c2) = [(x["prompt"], x["completion"], x["credits"]) for x in rows]
        det = a1 * b2 - a2 * b1
        if det:
            p_in = (c1 * b2 - c2 * b1) / det * 1e6
            p_out = (a1 * c2 - a2 * c1) / det * 1e6
        else:
            p_in = p_out = None
        out[slug] = {"model": model, "requests": rows, "credits_per_M_in": p_in, "credits_per_M_out": p_out}
        print(slug, "输入", p_in, "输出", p_out, "credit/百万 token", flush=True)
    (ROOT / "contest" / "unit_prices.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
