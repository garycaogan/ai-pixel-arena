"""把同一份提示词发给 Evolink 上的选手，收代码、跑自检、按需给修复机会，全程记账。

python tools/contest.py gemini kimi ...      （一家一家按顺序跑，方便用余额差记真实花费）

每家的全部记录在 contest/<slug>/：每次请求的原始回复、思考内容、用量、前后余额，以及最终的 bots/<slug>.py。
Key 从环境变量 EVOLINK_API_KEY 读（或 EVOLINK_API_KEY_FILE 指向的文件，默认 ~/.config/evolink/api.key），不会打印。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from arena import selfcheck  # noqa: E402

API = "https://api.evolink.ai"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36"
PROMPT = (ROOT / "prompt" / "PROMPT.md").read_text()
FIXES = 2


def _key() -> str:
    """Evolink API key：环境变量 EVOLINK_API_KEY；没设就读 EVOLINK_API_KEY_FILE 指向的文件（默认 ~/.config/evolink/api.key）。"""
    key = os.environ.get("EVOLINK_API_KEY", "").strip()
    if not key:
        f = Path(os.environ.get("EVOLINK_API_KEY_FILE") or "~/.config/evolink/api.key").expanduser()
        key = f.read_text().strip() if f.is_file() else ""
    if not key:
        raise RuntimeError("需要 Evolink API key：设环境变量 EVOLINK_API_KEY，或用 EVOLINK_API_KEY_FILE 指向存 key 的文件")
    return key


MODELS = {
    "gemini": "gemini-4-argon",
    "deepseek": "deepseek-v4.1-flash-1017",
    "kimi": "kimi-k3",
    "doubao": "doubao-seed-2.0-pro",
    "qwen": "qwen3.8-max",
    "glm": "glm-5.3",
    "minimax": "minimax-m3.1-flash",
    "grok": "grok-4.7",
}


def _redact(s: str) -> str:
    return s.replace(_key(), "[KEY]")


def credits() -> float:
    r = urllib.request.Request(API + "/v1/credits", headers={"Authorization": "Bearer " + _key(), "User-Agent": UA})
    d = json.loads(urllib.request.urlopen(r, timeout=60).read())
    return float(d["data"]["token"]["used_credits"])


def stream_chat(model: str, messages: list, extra: dict) -> dict:
    body = {"model": model, "messages": messages, "max_tokens": 65536, "stream": True,
            "stream_options": {"include_usage": True}, **extra}
    req = urllib.request.Request(API + "/v1/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json",
                                          "User-Agent": UA, "Accept": "text/event-stream"})
    t0 = time.time()
    content, reasoning, usage, finish, first = [], [], None, None, None
    try:
        resp = urllib.request.urlopen(req, timeout=1200)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {_redact(e.read().decode('utf-8', 'replace'))[:800]}", "seconds": time.time() - t0}
    for raw in resp:
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            ch = json.loads(data)
        except json.JSONDecodeError:
            continue
        if ch.get("usage"):
            usage = ch["usage"]
        for c in ch.get("choices") or []:
            d = c.get("delta") or {}
            if d.get("content"):
                first = first or time.time()
                content.append(d["content"])
            for k in ("reasoning_content", "reasoning"):
                if isinstance(d.get(k), str) and d[k]:
                    reasoning.append(d[k])
            if c.get("finish_reason"):
                finish = c["finish_reason"]
    return {"content": "".join(content), "reasoning": "".join(reasoning), "usage": usage, "finish": finish,
            "seconds": round(time.time() - t0, 1), "first_content_s": round(first - t0, 1) if first else None}


def truncated(r: dict, code) -> bool:
    """回复没写完就断了：结束原因是 length，或者正文为空，或者有开头的代码围栏却没有结尾。"""
    content = r.get("content") or ""
    if r.get("finish") == "length":
        return True
    if not content.strip():
        return True
    if content.count("```") % 2 == 1 and code is None:
        return True
    return False


def extract(text: str) -> str | None:
    blocks = re.findall(r"```(?:python|py)\s*\n(.*?)```", text, re.S)
    if not blocks:
        blocks = [b for b in re.findall(r"```[a-zA-Z]*\s*\n(.*?)```", text, re.S) if "def decide" in b]
    return blocks[-1] if blocks else None


def no_code_report(attempt: int) -> str:
    return ("自检结果：未通过。\n裁判在你的回复里没有找到 ```python 代码块，所以没法运行。\n\n"
            f"这是你的第 {attempt} 次修复机会（一共 {FIXES} 次）。请按原来的格式重新交一次：回复里只放一个 ```python 代码块，"
            "里面是完整的 bot.py，后面可以用不超过 300 字说明改了什么。")


def run(slug: str, resume: bool = False):
    model = MODELS[slug]
    out = ROOT / "contest" / slug
    out.mkdir(parents=True, exist_ok=True)
    log = {"slug": slug, "model": model, "channel": "Evolink API", "attempts": []}
    messages = [{"role": "user", "content": PROMPT}]
    extra = {"reasoning_effort": "high"}
    final_code = None
    start = 0
    if resume:
        # 接着上次跑：丢掉末尾的请求失败记录（没算机会），按已完成的几次重建对话
        log = json.loads((out / "log.json").read_text())
        log.setdefault("notes", []).append("续跑：" + time.strftime("%Y-%m-%d %H:%M:%S %z"))
        done = [a for a in log["attempts"] if a.get("result") != "request_error"]
        log["dropped"] = [a for a in log["attempts"] if a.get("result") == "request_error"]
        log["attempts"] = done
        for a in done:
            content = (out / f"attempt-{a['attempt']}.md").read_text()
            rep = (out / f"report-{a['attempt']}.txt").read_text()
            if content.strip():
                messages += [{"role": "assistant", "content": content}, {"role": "user", "content": rep}]
            else:
                messages = [{"role": "user", "content": messages[0]["content"] + "\n\n---\n\n（裁判对你上一次回复的反馈）\n\n" + rep}]
        start = len(done)
    attempt = start
    while attempt <= FIXES:
        c0 = credits()
        r = stream_chat(model, messages, extra)
        if r.get("error") and "reasoning" in r["error"].lower():
            log.setdefault("notes", []).append(f"reasoning_effort 被拒：{r['error'][:200]}，去掉后重发")
            extra = {}
            r = stream_chat(model, messages, extra)
        time.sleep(8)
        c1 = credits()
        rec = {"attempt": attempt, "params": dict(extra), "started": time.strftime("%Y-%m-%d %H:%M:%S %z"),
               "credits_before": c0, "credits_after": c1, "credits_delta": round(c1 - c0, 4),
               **{k: v for k, v in r.items() if k not in ("content", "reasoning")}}
        (out / f"attempt-{attempt}.md").write_text(r.get("content") or r.get("error") or "")
        if r.get("reasoning"):
            (out / f"attempt-{attempt}.reasoning.md").write_text(r["reasoning"])
        rec["reasoning_chars"] = len(r.get("reasoning") or "")
        rec["content_chars"] = len(r.get("content") or "")
        if r.get("error"):
            rec["result"] = "request_error"
            log["attempts"].append(rec)
            print(slug, "请求失败", r["error"][:300], flush=True)
            break
        code = extract(r["content"])
        if truncated(r, code):
            # 通道截断（输出额度用完或连接断开）：这一次作废，不算机会，降一档思考强度重跑
            rec["result"] = "void_truncated"
            log.setdefault("void", []).append(rec)
            (out / f"attempt-{attempt}.md").rename(out / f"void-{attempt}-{len(log['void'])}.md")
            if (out / f"attempt-{attempt}.reasoning.md").exists():
                (out / f"attempt-{attempt}.reasoning.md").rename(out / f"void-{attempt}-{len(log['void'])}.reasoning.md")
            print(slug, attempt, "截断作废", rec.get("finish"), rec.get("usage"), "credits", rec["credits_delta"], flush=True)
            cur = extra.get("reasoning_effort", "high")
            if cur == "low" or len(log["void"]) >= 4:
                log["final"] = "gave_up_truncated"
                break
            extra = {"reasoning_effort": {"high": "medium", "medium": "low"}[cur]}
            continue
        if code is None:
            rec["result"] = "no_code"
            rep = no_code_report(attempt + 1)
        else:
            path = out / f"bot-{attempt}.py"
            path.write_text(code)
            final_code = code
            sc = selfcheck.run(str(path))
            rec["selfcheck"] = {k: v for k, v in sc.items() if k != "games"}
            rec["result"] = "passed" if sc["passed"] else "failed"
            rep = None if sc["passed"] else selfcheck.report(sc, attempt + 1, FIXES)
        log["attempts"].append(rec)
        print(slug, attempt, rec["result"], rec.get("usage"), "credits", rec["credits_delta"], f"{rec['seconds']}s", flush=True)
        if rep is None:
            break
        (out / f"report-{attempt}.txt").write_text(rep)
        if attempt == FIXES:
            break
        attempt += 1
        if r["content"].strip():
            messages += [{"role": "assistant", "content": r["content"]}, {"role": "user", "content": rep}]
        else:
            # 上一次回复正文是空的（输出额度全用在思考上）。有的接口不接受空的 assistant 消息，
            # 所以把报告接在原提示词后面，作为同一条用户消息重发。
            messages = [{"role": "user", "content": messages[0]["content"] + "\n\n---\n\n（裁判对你上一次回复的反馈）\n\n" + rep}]
    if final_code is not None:
        (ROOT / "bots" / f"{slug}.py").write_text(final_code)
    log["final"] = log["attempts"][-1]["result"] if log["attempts"] else None
    (out / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    resume = "--resume" in sys.argv
    for s in [a for a in sys.argv[1:] if not a.startswith("--")]:
        try:
            run(s, resume)
        except Exception as e:  # 一家出问题不影响下一家
            print(s, "异常", _redact(f"{type(e).__name__}: {e}")[:300], flush=True)
