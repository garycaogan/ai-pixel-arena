"""把每位选手交卷过程的事实收进 contest/facts.json：片子和文档里的数字都从这里取。

python tools/facts.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["opus", "astra", "gemini", "deepseek", "kimi", "doubao", "qwen", "glm", "minimax", "grok"]


def summary_of(text: str) -> str:
    """回复里代码块后面的那段策略自述。"""
    parts = re.split(r"```(?:python|py)?\s*\n.*?```", text, flags=re.S)
    tail = parts[-1].strip() if len(parts) > 1 else ""
    return tail


def main():
    out = {}
    for slug in ORDER:
        d = ROOT / "contest" / slug
        if not (d / "log.json").exists():
            continue
        log = json.loads((d / "log.json").read_text())
        atts = [a for a in log["attempts"] if a.get("result") != "request_error"]
        last = atts[-1]
        final_md = (d / f"attempt-{last['attempt']}.md").read_text() if (d / f"attempt-{last['attempt']}.md").exists() else ""
        first_md = (d / "attempt-0.md").read_text() if (d / "attempt-0.md").exists() else ""
        bot = (ROOT / "bots" / f"{slug}.py").read_text() if (ROOT / "bots" / f"{slug}.py").exists() else ""
        lines = bot.count("\n") + (0 if bot.endswith("\n") or not bot else 1)
        rec = {
            "model": log["model"], "channel": log["channel"],
            "attempts": len(atts), "fixes_used": max(0, len(atts) - 1),
            "void": len(log.get("void", [])),
            "results": [a.get("result") for a in atts],
            "seconds": [a.get("seconds") for a in atts],
            "first_content_s": [a.get("first_content_s") for a in atts],
            "usage": [a.get("usage") for a in atts],
            "credits": [a.get("credits_delta") for a in atts],
            "selfcheck_max_cpu_ms": [((a.get("selfcheck") or {}).get("max_cpu_ms")) for a in atts],
            "code_lines": lines, "code_bytes": len(bot.encode()),
            "summary_first": summary_of(first_md), "summary_final": summary_of(final_md),
        }
        for k in ("seconds_note", "usage_note", "cost", "delivery"):
            if k in last:
                rec[k] = last[k]
        reports = sorted(d.glob("report-*.txt"))
        rec["reports"] = [r.read_text() for r in reports]
        out[slug] = rec
    (ROOT / "contest" / "facts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for s, r in out.items():
        print(s, r["attempts"], r["results"], r["code_lines"], "行", r["seconds"], r["summary_final"][:60].replace("\n", " "))


if __name__ == "__main__":
    main()
