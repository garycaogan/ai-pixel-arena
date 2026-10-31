"""Small Evolink helper: upload, async tasks, Gemini watch/listen.

The key comes from EVOLINK_API_KEY (or the file named by EVOLINK_API_KEY_FILE, default ~/.config/evolink/api.key)
and is never printed.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.evolink.ai"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36"}


def _key() -> str:
    """Evolink API key：环境变量 EVOLINK_API_KEY；没设就读 EVOLINK_API_KEY_FILE 指向的文件（默认 ~/.config/evolink/api.key）。"""
    key = os.environ.get("EVOLINK_API_KEY", "").strip()
    if not key:
        f = Path(os.environ.get("EVOLINK_API_KEY_FILE") or "~/.config/evolink/api.key").expanduser()
        key = f.read_text().strip() if f.is_file() else ""
    if not key:
        raise RuntimeError("需要 Evolink API key：设环境变量 EVOLINK_API_KEY，或用 EVOLINK_API_KEY_FILE 指向存 key 的文件")
    return key


def _req(method, url, body=None, timeout=120):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    r = urllib.request.Request(url, data=data, method=method,
                               headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json", **UA})
    try:
        return json.loads(urllib.request.urlopen(r, timeout=timeout).read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace').replace(_key(), '[KEY]')[:600]}") from None


def post(path, body):
    return _req("POST", API + "/v1" + path, body)


def task(task_id, every=4, tries=600, quiet=False):
    for _ in range(tries):
        st = _req("GET", f"{API}/v1/tasks/{task_id}")
        if st.get("status") in ("completed", "failed", "cancelled"):
            if st.get("status") != "completed":
                raise RuntimeError(f"task {task_id} {st.get('status')}: {json.dumps(st.get('error') or st, ensure_ascii=False)[:600]}")
            return st
        if not quiet:
            print(f"  {task_id} {st.get('status')} {st.get('progress')}", file=sys.stderr, flush=True)
        time.sleep(every)
    raise RuntimeError(f"task {task_id} timed out")


def result_url(st):
    u = st["results"][0]
    return u if isinstance(u, str) else u["url"]


def download(url, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read())
    return out


def upload(path, mime=None):
    import mimetypes
    import httpx
    path = Path(path)
    mime = mime or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as fh:
        r = httpx.post("https://files-api.evolink.ai/api/v1/files/upload/stream",
                       headers={"Authorization": "Bearer " + _key(), **UA},
                       files={"file": (path.name, fh, mime)}, timeout=300)
    r.raise_for_status()
    d = r.json()
    url = (d.get("data") or d).get("file_url")
    if not url:
        raise RuntimeError("upload failed: " + json.dumps(d, ensure_ascii=False)[:300])
    return url


def gemini(parts, model="gemini-3.8-flash", max_tokens=16000, temperature=0.2, timeout=900):
    """parts: list of str (text) or Path (video/audio/image sent inline)."""
    import mimetypes
    out_parts = []
    for p in parts:
        if isinstance(p, Path):
            mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            out_parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(p.read_bytes()).decode()}})
        else:
            out_parts.append({"text": p})
    body = {"contents": [{"role": "user", "parts": out_parts}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}}
    d = _req("POST", f"{API}/v1beta/models/{model}:generateContent", body, timeout=timeout)
    parts = ((d.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))
