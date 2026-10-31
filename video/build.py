"""分集 JSON → HyperFrames 项目 →（可选）MP4。

python video/build.py video/ep1.json --out video/work/ep1 [--render out/ep1.mp4] [--no-tts]

旁白逐句用 Evolink TTS 合成（按文本缓存，花费记到 video/cache/tts-costs.json），
场景时长由旁白长度决定；场景里的出现时间可以写 "L2"（第 2 句开始时）或秒数。
配音要 Evolink 的 key：环境变量 EVOLINK_API_KEY，或者 EVOLINK_API_KEY_FILE 指向的文件（默认 ~/.config/evolink/api.key）。
--no-tts 不调接口、不需要 key：按字数估每句时长、配音留空，用来排版和预览。
画面全部由 template.html 里的 render(t) 按时间画，可以任意 seek。
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VID = ROOT / "video"
sys.path.insert(0, str(ROOT))
from arena.export import export  # noqa: E402
from arena import demos as demo_mod  # noqa: E402
sys.path.insert(0, str(VID))
import chiptune as pda  # noqa: E402  芯片音乐和音效合成，来自 pixel-diary（同一作者，MIT）

HF_VERSION = "0.8.181"
SR = pda.SR
CACHE = VID / "cache"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36"}
# 正文字体 Noto Sans SC（OFL，17 MB，不随仓库发布，下载方法见 README）；放别处时用 ARENA_CJK_FONT 指过去。
# 找不到时正文先用像素字体代替，能出片，但和发布的那版字形不一样。
NOTO = Path(os.environ.get("ARENA_CJK_FONT") or ROOT / "fonts" / "NotoSansSC-VF.ttf").expanduser()
PIXEL = ROOT / "fonts" / "fusion-pixel-12px-proportional-zh_hans.ttf"
e = html.escape


# ------------------------------------------------------------------ 配音
def _key():
    key = os.environ.get("EVOLINK_API_KEY", "").strip()
    if not key:
        f = Path(os.environ.get("EVOLINK_API_KEY_FILE") or "~/.config/evolink/api.key").expanduser()
        key = f.read_text().strip() if f.is_file() else ""
    if not key:
        raise RuntimeError("配音要 Evolink API key：设环境变量 EVOLINK_API_KEY（或用 EVOLINK_API_KEY_FILE 指向存 key 的文件）；"
                           "不配音就加 --no-tts")
    return key


def _ev(method, path, body=None):
    req = urllib.request.Request("https://api.evolink.ai/v1" + path, method=method,
                                 data=None if body is None else json.dumps(body, ensure_ascii=False).encode(),
                                 headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json", **UA})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())


CN_D = "零一二三四五六七八九"


def cn_int(n: int) -> str:
    if n < 10:
        return CN_D[n]
    out, zero = "", False
    for u, name in [(100000000, "亿"), (10000, "万"), (1000, "千"), (100, "百"), (10, "十")]:
        q, n = divmod(n, u)
        if q:
            if zero:
                out += "零"
            out += ("" if (u == 10 and q == 1 and not out) else cn_int(q)) + name
            zero = False
        elif out:
            zero = True
    if n:
        out += ("零" if zero else "") + CN_D[n]
    return out


def speak_numbers(t: str) -> str:
    """字幕里写阿拉伯数字，配音前转成中文读法：8,470 → 八千四百七十，1.85 → 一点八五，54% → 百分之五十四，+172 → 正一百七十二。"""
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)
    t = re.sub(r"(\d+)\s*×\s*(\d+)", lambda m: f"{m.group(1)}乘{m.group(2)}", t)

    def num(m):
        a, b = m.group(1), m.group(2)
        return cn_int(int(a)) + ("点" + "".join(CN_D[int(c)] for c in b) if b else "")
    t = re.sub(r"(\d+)(?:\.(\d+))?\s*%", lambda m: "百分之" + num(m), t)
    t = re.sub(r"(^|[\s（(，、：])\+(?=\d)", r"\1正", t)
    t = re.sub(r"(^|[\s（(，、：])[−-](?=\d)", r"\1负", t)
    t = re.sub(r"(\d+)(?:\.(\d+))?", num, t)
    t = re.sub(r"(?<=[\u4e00-\u9fff]) (?=[\u4e00-\u9fff])", "", t)
    return t


def tts(text: str, voice: dict, offline=False) -> Path:
    """一句旁白 → 单声道 wav（缓存）。"""
    CACHE.mkdir(parents=True, exist_ok=True)
    spoken = text
    for a, b in voice.get("say_as", []):
        spoken = spoken.replace(a, b)
    spoken = speak_numbers(spoken)
    h = hashlib.sha1(json.dumps([spoken, voice["model"], voice["voice"], voice.get("instruction", "")], ensure_ascii=False).encode()).hexdigest()[:16]
    out = CACHE / f"tts-{h}.wav"
    if out.exists():
        return out
    if offline:  # 不调接口时按字数估一个静音占位，用来排版
        n = int(SR * max(1.0, len(re.sub(r"\s", "", spoken)) / 4.6))
        pda.write_wav(out.with_suffix(".est.wav"), np.zeros(n))
        return out.with_suffix(".est.wav")
    body = {"model": voice["model"], "prompt": spoken, "voice": voice["voice"], "response_format": "wav"}
    if voice.get("instruction"):
        body["instruction"] = voice["instruction"]
    t = _ev("POST", "/audios/generations", body)
    for _ in range(150):
        time.sleep(2)
        st = _ev("GET", f"/tasks/{t['id']}")
        if st["status"] in ("completed", "failed", "cancelled"):
            break
    if st["status"] != "completed":
        raise RuntimeError(f"TTS 失败：{json.dumps(st.get('error'), ensure_ascii=False)[:300]}")
    url = st["results"][0]
    url = url if isinstance(url, str) else url["url"]
    raw = out.with_suffix(".raw.wav")
    raw.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                    "-ar", str(SR), "-ac", "1", str(out)], check=True)
    raw.unlink()
    log = CACHE / "tts-costs.json"
    rows = json.loads(log.read_text()) if log.exists() else []
    rows.append({"hash": h, "task": t["id"], "chars": len(spoken), "cny": ((st.get("usage") or {}).get("cost") or {}).get("cny"),
                 "at": time.strftime("%Y-%m-%d %H:%M:%S %z")})
    log.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    return out


def wav_read(p: Path) -> np.ndarray:
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1)
        if w.getframerate() != SR:
            raise RuntimeError(f"{p} 采样率不是 {SR}")
    return x


# ------------------------------------------------------------------ 字幕
def chunks(text: str, limit=24):
    parts = re.split(r"(?<=[，。！？；：,!?;:])", text)
    out, cur = [], ""
    for p in parts:
        if not p:
            continue
        if len(cur) + len(p) <= limit:
            cur += p
        else:
            if cur:
                out.append(cur)
            cur = p
            while len(cur) > limit:
                out.append(cur[:limit])
                cur = cur[limit:]
    if cur:
        out.append(cur)
    return [c.strip().rstrip("，。；：,;") for c in out if c.strip()]


# ------------------------------------------------------------------ 场景 HTML
def img(c, cls="sprite", extra=""):
    return f'<img class="{cls}" src="assets/cast/{c}.png" alt="" {extra}/>'


def scene_html(s, cast):
    sid, T = s["id"], s["type"]
    if T == "title":
        row = "".join(f'<div class="c" id="{sid}-c{i}">{img(c)}<b style="color:{cast[c]["color"]}">{e(cast[c]["short"])}</b></div>'
                      for i, c in enumerate(s["cast"]))
        return (f'<div class="t-logo px" id="{sid}-logo">{e(s["logo"])}</div><div class="t-sub px" id="{sid}-sub">{e(s["sub"])}</div>'
                f'<div class="t-row">{row}</div><div class="t-foot" id="{sid}-foot">{e(s["foot"])}</div>')
    if T == "demo":
        items = "".join(f'<div class="it" id="{sid}-i{i}">{e(it["text"])}</div>' for i, it in enumerate(s["items"]))
        size = s["w"] * s["cell"] + s["cell"]
        hp = (f'<div class="hpbar"><span id="{sid}-hpv"></span><div class="track"><div class="fill" id="{sid}-hpf"></div></div></div>'
              if s.get("hp") else "")
        return (f'<canvas class="demo-board" id="{sid}-cv" width="{size}" height="{size}"></canvas>{hp}'
                f'<div class="win demo-card"><h2 class="px">{e(s["title"])}</h2>{items}</div>')
    if T == "list":
        items = "".join(f'<div class="it" id="{sid}-i{i}">{it["html"]}</div>' for i, it in enumerate(s["items"]))
        return f'<div class="win list"><h2 class="px" id="{sid}-h">{e(s["title"])}</h2>{items}</div>'
    if T == "doc":
        keys = "".join(f'<div class="k" id="{sid}-k{i}">{e(k["text"])}</div>' for i, k in enumerate(s["keys"]))
        return (f'<div class="win doc{" small" if s.get("small") else ""}"><div class="bar"><i></i><i></i><i></i><span>{e(s["doc_title"])}</span></div>'
                f'<div class="clipbox"><div class="body" id="{sid}-body">{e(s["text"])}</div></div></div><div class="doc-side">{keys}</div>')
    if T == "intro":
        c = cast[s["who"]]
        chips = "".join(f'<span class="chip">{e(x)}</span>' for x in s.get("chips", []))
        facts = "".join(f'<div class="fact" id="{sid}-f{i}">{f["html"]}</div>' for i, f in enumerate(s["facts"]))
        return (f'<div class="intro-por" id="{sid}-por">{img(s["who"], extra=f"id=\"{sid}-img\"")}</div>'
                f'<div class="win intro-card" id="{sid}-card"><i class="swatch" style="background:{c["color"]}"></i>'
                f'<div class="no px">{e(s.get("no", ""))}</div><div class="nm" style="color:{c["color"]}">{e(c["name"])}</div>'
                f'<div class="ch">{e(s.get("channel", ""))}</div><div class="chips">{chips}</div>{facts}</div>')
    if T == "bars":
        rows = []
        for i, r in enumerate(s["rows"]):
            c = cast[r["who"]]
            rows.append(f'<div class="row" id="{sid}-r{i}">{img(r["who"])}<div class="nm" style="color:{c["color"]}">{e(c["short"])}</div>'
                        f'<div class="bar" id="{sid}-b{i}" style="background:{c["color"]};width:0"></div><div class="v" id="{sid}-v{i}"></div></div>')
        return (f'<div class="win bars"><h2 class="px" id="{sid}-h">{e(s["title"])}</h2><div class="note">{e(s.get("note", ""))}</div>'
                + "".join(rows) + "</div>")
    if T == "timeline":
        ticks = "".join(f'<div class="tl-tick" style="left:{x}px">{e(lab)}</div>' for x, lab in s["ticks"])
        items = "".join(f'<div class="tl-item" id="{sid}-t{i}" style="left:{it["x"] - 60}px;top:{it["y"]}px">{img(it["who"])}'
                        f'<div class="st" style="background:{cast[it["who"]]["color"]}">{e(it["label"])}</div></div>'
                        for i, it in enumerate(s["items"]))
        return (f'<div class="tl-title px">{e(s["title"])}</div><div class="tl-note">{e(s.get("note", ""))}</div>'
                f'<div class="tl-axis"></div>{ticks}{items}')
    if T == "quote":
        c = cast[s["who"]]
        return (f'<div class="q-por" id="{sid}-por">{img(s["who"])}</div><div class="win q-box" id="{sid}-box">'
                f'<div class="who" style="color:{c["color"]}">{e(c["name"])}{e(s.get("who_note", ""))}</div>'
                f'<div class="tx" id="{sid}-tx"></div><div class="src">{e(s.get("src", ""))}</div></div>')
    if T == "counter":
        minis = "".join(f'<canvas id="{sid}-m{i}" width="{m["size"]}" height="{m["size"]}" style="position:absolute;left:{m["x"]}px;top:{m["y"]}px;opacity:0.22"></canvas>'
                        for i, m in enumerate(s["minis"]))
        return (f'{minis}<div class="cnt-big px" id="{sid}-n">0</div><div class="cnt-lab" id="{sid}-lab">{e(s["label"])}</div>'
                f'<div class="cnt-sub" id="{sid}-sub">{e(s["sub"])}</div>')
    if T in ("match", "cold"):
        size = s["w"] * s["cell"] + s["cell"]
        board = f'<canvas id="{sid}-cv" width="{size}" height="{size}" style="position:absolute;left:{s["bx"]}px;top:{s["by"]}px"></canvas>'
        if T == "cold":
            lines = "".join(f'<div class="a{" g" if l.get("gold") else ""}" id="{sid}-a{i}">{e(l["text"])}</div>' for i, l in enumerate(s["lines"]))
            return (board + f'<div class="cold-txt px">{lines}</div>'
                    f'<div id="{sid}-turn" class="px" style="position:absolute;left:{s["bx"]}px;top:{s["by"] - 44}px;font-size:30px;color:#9aa8c7"></div>')
        rows = []
        for seat in s["order"]:
            who = s["seats"][seat]
            c = cast[who]
            rows.append(f'<div class="m-row" id="{sid}-row{seat}"><i class="sw" style="background:{c["color"]}"></i>{img(who)}'
                        f'<div class="nm" style="color:{c["color"]}">{e(c["short"])}</div><div class="ln" id="{sid}-ln{seat}"></div>'
                        f'<div class="hp"><i id="{sid}-hp{seat}"></i></div><div class="st" id="{sid}-st{seat}"></div></div>')
        callouts = "".join(f'<div class="callout" id="{sid}-co{i}" style="left:{c["x"]}px;top:{c["y"]}px;opacity:0">{e(c["text"])}</div>'
                           for i, c in enumerate(s.get("callouts", [])))
        chart = (f'<canvas class="m-chart" id="{sid}-ch" width="860" height="{s.get("chart_h", 220)}" style="top:{s.get("chart_y", 800)}px"></canvas>'
                 if s.get("chart") else "")
        big = " m-big" if len(s["order"]) <= 3 else ""
        return (board + f'<div class="m-title px">{e(s["title"])}</div><div class="m-meta"><span>{e(s.get("meta", ""))}</span>'
                f'<span class="m-speed px" id="{sid}-sp"></span></div><div class="m-turn px" id="{sid}-turn"></div>'
                f'<div class="m-rows{big}">{"".join(rows)}</div>{chart}{callouts}')
    if T == "rank":
        c = cast[s["who"]]
        ticks = "".join(f'<div class="nl-tick" style="left:{x}px">{e(lab)}</div>' for x, lab in s["ticks"])
        marks = "".join(f'<div class="nl-av" id="{sid}-a{i}" style="left:{m["x"]}px;top:{800 - m.get("lift", 0)}px">{img(m["who"])}'
                        f'<i style="background:{cast[m["who"]]["color"]}"></i></div>' for i, m in enumerate(s["marks"]))
        return (f'<div class="rk-por" id="{sid}-por">{img(s["who"])}</div><div class="rk-txt"><div class="no px" id="{sid}-no">{e(s["no"])}</div>'
                f'<div class="nm" id="{sid}-nm" style="color:{c["color"]}">{e(c["name"])}</div><div class="sc px" id="{sid}-sc"></div>'
                f'<div class="ex" id="{sid}-ex">{e(s.get("ex", ""))}</div></div>'
                f'<div class="nl"></div><div class="nl-zero" style="left:{s["zero_x"] - 2}px"></div>{ticks}{marks}')
    if T == "podium":
        out = []
        for i, it in enumerate(s["items"]):
            c = cast[it["who"]]
            out.append(f'<div class="pod" id="{sid}-p{i}" style="left:{it["x"]}px">{img(it["who"])}'
                       f'<div class="blk" style="height:{it["h"]}px;background:{it["bg"]}"><div class="r px">{e(it["rank"])}</div>'
                       f'<div class="n" style="color:#fff">{e(c["name"])}</div><div class="s">{e(it["score"])}</div></div></div>')
        return "".join(out)
    if T == "table":
        head = "".join(f'<th class="{"num" if i in s.get("num_cols", []) else ""}">{e(h)}</th>' for i, h in enumerate(s["head"]))
        rows = []
        for i, r in enumerate(s["rows"]):
            who = r[0]
            cells = [f'<td>{img(who)}<span style="color:{cast[who]["color"]}">{e(cast[who]["name"])}</span></td>']
            for j, v in enumerate(r[1:], 1):
                cells.append(f'<td class="{"num" if j in s.get("num_cols", []) else ""}">{e(str(v))}</td>')
            rows.append(f'<tr id="{sid}-r{i}">{"".join(cells)}</tr>')
        return (f'<div class="win tbl"><h2 class="px" id="{sid}-h">{e(s["title"])}</h2><div class="note">{e(s.get("note", ""))}</div>'
                f'<table><tr>{head}</tr>{"".join(rows)}</table></div>')
    if T == "labels":
        cards = "".join(f'<div class="lab" id="{sid}-l{i}">{img(it["who"])}<div class="n" style="color:{cast[it["who"]]["color"]}">{e(cast[it["who"]]["short"])}</div>'
                        f'<div class="w px">{e(it["word"])}</div><div class="s">{e(it["stat"])}</div></div>' for i, it in enumerate(s["items"]))
        return f'<div class="lab-grid">{cards}</div>'
    if T == "end":
        items = "".join(f'<div class="it" id="{sid}-i{i}">{it["html"]}</div>' for i, it in enumerate(s["items"]))
        row = "".join(f'<div id="{sid}-c{i}">{img(c)}</div>' for i, c in enumerate(s["cast"]))
        return f'<div class="end-t px" id="{sid}-t">{e(s["title"])}</div><div class="end-l">{items}</div><div class="end-row">{row}</div>'
    raise ValueError(f"未知场景类型 {T}")


# ------------------------------------------------------------------ 主流程
def resolve_at(v, lines_at):
    if isinstance(v, str) and v.startswith("L"):
        k = v[1:]
        off = 0.0
        if "+" in k:
            k, o = k.split("+")
            off = float(o)
        return lines_at[int(k)] + off
    return float(v)


TIME_KEYS = ("at", "until", "reveal_at", "type_at", "play_at", "foot_at", "ex_at", "sub_at")
TIME_LISTS = ("row_at", "light")


def fix_times(obj, lines_at):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in TIME_KEYS:
                out[k] = resolve_at(v, lines_at)
            elif k in TIME_LISTS and isinstance(v, list):
                out[k] = [resolve_at(x, lines_at) for x in v]
            else:
                out[k] = fix_times(v, lines_at)
        return out
    if isinstance(obj, list):
        return [fix_times(v, lines_at) for v in obj]
    return obj


def build(ep_path: str, out_dir: str, offline=False):
    ep = json.loads(Path(ep_path).read_text())
    out = Path(out_dir).resolve()
    (out / "assets" / "audio").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "cast").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    cast = ep["cast"]
    for slug, c in cast.items():
        shutil.copy2(ROOT / c["img"], out / "assets" / "cast" / f"{slug}.png")
    voice = ep["voice"]
    # 旁白
    t = 0.0
    scenes, subs, voices, sfx, duck = [], [], [], [], []
    for s in ep["scenes"]:
        s = dict(s)
        lead, gap, tail = s.get("lead", 0.4), s.get("gap", 0.35), s.get("tail", 0.8)
        lt = lead
        lines_at = []
        for line in s.get("say", []):
            p = tts(line, voice, offline)
            x = wav_read(p)
            d = len(x) / SR
            lines_at.append(lt)
            voices.append((t + lt, x))
            duck.append((t + lt - 0.1, t + lt + d + 0.1))
            # 字幕按字数分配时长
            cs = chunks(line)
            tot = sum(len(c) for c in cs) or 1
            a = t + lt
            for c in cs:
                b = a + d * len(c) / tot
                subs.append([round(a, 3), round(b, 3), c])
                a = b
            lt += d + gap
        dur = max(lt - gap + tail, s.get("min", 0))
        s["start"], s["dur"] = round(t, 3), round(dur, 3)
        s = fix_times(s, lines_at)
        s["lines_at"] = lines_at
        for ev_ in s.get("sfx", []):
            sfx.append((t + ev_["at"], ev_["kind"]))
        scenes.append(s)
        t += dur
    total = round(t + 0.5, 3)
    # 对局数据
    games = {}
    for gid, g in ep.get("games", {}).items():
        games[gid] = json.loads((ROOT / g).read_text()) if isinstance(g, str) else g
    dm = demo_mod.build()
    # 场景里需要的派生字段
    for s in scenes:
        if s["type"] in ("match", "cold"):
            G = games[s["game"]]
            s.setdefault("w", G["w"])
            s.setdefault("colors", [cast[w]["color"] for w in G["seats"]])
            s.setdefault("seats", G["seats"])
            s.setdefault("order", list(range(len(G["seats"]))))
            causes = {"wall": "撞墙", "body": "撞到身体", "self": "撞到自己", "head": "撞头输了", "starve": "饿死"}
            deaths = {}
            for ev_ in G["events"]:
                if ev_["type"] == "die":
                    deaths[ev_["id"]] = f'第 {ev_["t"]} 回合 · {causes.get(ev_["cause"], ev_["cause"])}'
            s["deaths"] = {str(k): v for k, v in deaths.items()}
            s["deaths"] = [deaths.get(i, "") for i in range(len(G["seats"]))]
            if s.get("death_sfx", True):
                for ev_ in G["events"]:
                    if ev_["type"] == "die":
                        # 回合 → 时间
                        for a, b, ta, tb, *_ in s["segs"]:
                            if ta <= ev_["t"] <= tb and tb > ta:
                                sfx.append((s["start"] + a + (b - a) * (ev_["t"] - ta) / (tb - ta), "die"))
                                break
        if s["type"] == "demo":
            s["w"] = 9
    # 音频
    n = int(SR * (total + 1))
    vo = np.zeros(n)
    for at, x in voices:
        i = int(at * SR)
        vo[i:i + len(x)] += x[: max(0, n - i)]
    fx = np.zeros(n)
    for at, kind in sfx:
        if kind == "pop":
            pda._pop(fx, at, hi=True)
        elif kind == "thud":
            pda._thud(fx, at)
        elif kind == "die":
            pda._pop(fx, at)
        elif kind == "sweep":
            pda._sweep(fx, at, 0.4)
        elif kind == "jingle":
            pda._jingle(fx, at)
        elif kind == "click":
            pda._click(fx, at, int(at * 1000))
    bgm = pda.bgm_track(total, ep.get("bgm", "cheerful"))
    bgm = np.pad(bgm, (0, max(0, n - len(bgm))))[:n]
    env = np.ones(n) * ep.get("bgm_level", 0.55)
    for a, b in duck:
        i0, i1 = int(a * SR), int(b * SR)
        env[max(0, i0):i1] = ep.get("bgm_duck", 0.22)
    # 平滑包络
    k = int(SR * 0.25)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    mix = vo * 1.0 + bgm * env + fx * ep.get("sfx_level", 0.5)
    pda.write_wav(out / "assets" / "audio" / "mix.wav", mix)
    # 字体
    texts = json.dumps(ep, ensure_ascii=False) + "".join(c[2] for c in subs) + "0123456789+-−×·%., ?！？分局回合第名"
    _fonts(texts, out / "assets" / "fonts")
    # 页面
    plan = {"duration": total, "scenes": [{k: v for k, v in s.items() if k not in ("say",)} for s in scenes],
            "subs": subs, "cast": {k: {"color": v["color"]} for k, v in cast.items()}}
    parts = [f'<div class="scene clip" id="{s["id"]}" data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="1">{scene_html(s, cast)}</div>'
             for s in scenes]
    tpl = (VID / "template.html").read_text()
    rep = {"__DURATION__": str(total), "__SCENES__": "\n".join(parts), "__BOARD_JS__": (VID / "board.js").read_text(),
           "__PLAN__": json.dumps(plan, ensure_ascii=False), "__GAMES__": json.dumps(games, separators=(",", ":")),
           "__DEMOS__": json.dumps(dm, separators=(",", ":"))}
    for k_, v in rep.items():
        tpl = tpl.replace(k_, v)
    (out / "index.html").write_text(tpl)
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    (out / "hyperframes.json").write_text(json.dumps({"paths": {"assets": "assets"}, "media": {"autoProxy": True}}, indent=2))
    (out / "meta.json").write_text(json.dumps({"id": out.name, "name": out.name}, indent=2))
    (out / "package.json").write_text(json.dumps({"name": out.name, "private": True, "type": "module", "scripts": {
        "check": f"npx --yes hyperframes@{HF_VERSION} check", "render": f"npx --yes hyperframes@{HF_VERSION} render"}}, indent=2))
    return plan


def _fonts(text: str, out_dir: Path):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    chars = "".join(sorted(set(text + "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?:;'\"()-+×✓·…/%")))
    body = NOTO
    if not NOTO.is_file():
        print(f"没找到正文字体 {NOTO}，先用像素字体代替（下载 Noto Sans SC 的方法见 README）", file=sys.stderr)
        body = PIXEL
    for name, src, wght in [("as-500", body, 500), ("as-800", body, 800), ("as-900", body, 900), ("px", PIXEL, None)]:
        dst = out_dir / f"{name}.woff2"
        stamp = dst.with_suffix(".chars")
        key = chars if body == NOTO or name == "px" else "pixel-fallback\n" + chars  # 换回 Noto 后不复用代替字体的缓存
        if dst.exists() and stamp.exists() and stamp.read_text() == key:
            continue
        f = TTFont(src)
        if wght and "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        o = subset.Options()
        o.flavor = "woff2"
        o.layout_features = ["*"]
        sb = subset.Subsetter(o)
        sb.populate(text=chars)
        sb.subset(f)
        f.flavor = "woff2"
        f.save(dst)
        stamp.write_text(key)


def render(out_dir: str, mp4: str):
    out = Path(out_dir).resolve()
    target = Path(mp4).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = target.with_suffix(".raw.mp4")
    subprocess.run(["npx", "--yes", f"hyperframes@{HF_VERSION}", "render", "--quality", "high", "--output", str(raw)], cwd=out, check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", str(target)], check=True)
    raw.unlink()
    return target


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--out", required=True)
    ap.add_argument("--render")
    ap.add_argument("--no-tts", action="store_true")
    a = ap.parse_args()
    p = build(a.episode, a.out, offline=a.no_tts)
    print(f"built {a.out}: {p['duration']}s, {len(p['scenes'])} scenes")
    for s in p["scenes"]:
        print(f"  {s['id']:14s} {s['type']:9s} {s['start']:8.2f} +{s['dur']:6.2f}")
    if a.render:
        print("rendered", render(a.out, a.render))
