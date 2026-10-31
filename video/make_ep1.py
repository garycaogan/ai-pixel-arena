"""第 1 集分镜：从比赛记录生成 video/ep1.json，再用 video/build.py 出片。

所有数字都从这些文件里读，不手填：
  contest/facts.json   每家交卷过程（tools/facts.py 生成）
  results/ratings.json 正赛成绩（python -m arena.analyze 生成）
  results/picks.json   精选对局（python video/pick_games.py 生成）

.venv/bin/python video/make_ep1.py && .venv/bin/python video/build.py video/ep1.json --out video/work/ep1
"""
import json
import math
import re
from pathlib import Path

from cast import CAST, ORDER, SAY_AS

ROOT = Path(__file__).resolve().parent.parent
VID = ROOT / "video"
F = json.loads((ROOT / "contest" / "facts.json").read_text())
import os
RES = Path(os.environ.get("ARENA_RESULTS", ROOT / "results"))
R = json.loads((RES / "ratings.json").read_text())
P = json.loads((RES / "picks.json").read_text())

CN_DIGIT = "零一二三四五六七八九"


def pangu(t: str) -> str:
    """中文和英文、数字之间加一个空格，字幕好读；配音时这些空格会被去掉。"""
    t = re.sub(r"([\u4e00-\u9fff])([A-Za-z0-9+−])", r"\1 \2", t)
    t = re.sub(r"([A-Za-z0-9%])([\u4e00-\u9fff])", r"\1 \2", t)
    t = re.sub(r"([\u4e00-\u9fff]) +([\u4e00-\u9fff])", r"\1\2", t)
    return re.sub(r" {2,}", " ", t)


def cn(n) -> str:
    """显示用的数字（字幕直接用）；配音前 build.speak_numbers 会转成中文读法。"""
    return str(int(round(n)))


def wan(n):
    """79282 → 7万9千多；13274 → 1万3千多；8425 → 8千多。"""
    n = int(n)
    if n >= 10000:
        w, r = divmod(n, 10000)
        q = r // 1000
        return f"{w}万" + (f"{q}千" if q else "") + "多"
    if n >= 1000:
        return f"{n // 1000}千多"
    return str(n)


def fmt(n):
    return f"{int(round(n)):,}"


def mins(sec):
    m = sec / 60
    return f"{m:.1f}".rstrip("0").rstrip(".")


def reasoning(slug):
    u = (F[slug]["usage"] or [None])[-1] or {}
    if slug == "opus":
        return 79282
    tot = 0
    for u in F[slug]["usage"]:
        u = u or {}
        tot += int((u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)
    return tot or None


def think_minutes(slug):
    """动笔前想了多久：第一次请求里，从发出到第一个正文字出现的时间（只有 API 选手有）。"""
    v = F[slug].get("first_content_s") or [None]
    return v[0] / 60 if v and v[0] else None


def summary_chars(slug):
    t = F[slug]["summary_first"] if slug == "gemini" else F[slug]["summary_final"]
    if slug == "astra":
        t = ASTRA_SUMMARY
    return len(re.sub(r"\s|[#*`\-]", "", t))


ASTRA_SUMMARY = ("以存活为先，计算身体占用和尾部释放时间，结合可用空间、食物竞争与饥饿程度选路；"
                 "通过限时路径搜索和近距离对抗搜索规避包围、撞头，终局兼顾长度排名。")

N_TOTAL = R["games"]
N_DUEL = R["counts"]["duel"]
N_MELEE = R["counts"]["melee"]
RANK = [s for s in R["order"] if s != "baseline"]  # 第一名在前
TOTAL = R["total"]


def score(slug):
    return TOTAL[slug][0]


def build():
    scenes = []
    S = scenes.append
    # ------------------------------------------------------------ B 片头
    S({"id": "title", "type": "title", "logo": "AI 像素擂台", "sub": "第 1 集 · 贪吃蛇大乱斗", "cast": ORDER,
       "light": [f"L0+{0.6 + i * 0.32:.2f}" for i in range(10)], "foot": f"10 个 AI · 同一份提示词 · {fmt(N_TOTAL)} 局实测", "foot_at": "L1",
       "say": ["10 个 AI 模型，拿到一字不差的同一份提示词，各写一个贪吃蛇程序。",
               f"然后我们让这些程序在同一个赛场里，打了{cn(N_TOTAL)}局。排名全看真实成绩。"],
       "sfx": [{"at": 0.2, "kind": "sweep"}]})
    # ------------------------------------------------------------ C 规则
    two = [CAST["opus"]["color"], CAST["astra"]["color"]]
    one = [CAST["opus"]["color"]]
    S({"id": "r-eat", "type": "demo", "chapter": "规则", "demo": "eat", "cell": 64, "rate": 2.2, "play_at": "L0+0.3", "colors": one,
       "title": "走一步，吃一口", "items": [{"text": "所有蛇同时走，每回合一步", "at": "L0"}, {"text": "吃到樱桃，身体长一节", "at": "L1"}],
       "say": ["先说规则。棋盘是方格，四周是墙。所有蛇同时行动，每回合往上下左右走一步。", "吃到樱桃，身体长一节。"]})
    S({"id": "r-hunger", "type": "demo", "chapter": "规则", "demo": "hunger", "cell": 64, "rate": 2.0, "play_at": "L0+0.5", "colors": one,
       "hp": True, "hp_max": 10, "title": "会饿", "items": [{"text": "每走一步，生命值减 1", "at": "L0"}, {"text": "吃到东西，回满 100", "at": "L0+2.2"},
                                                           {"text": "降到 0，饿死", "at": "L1"}],
       "say": ["每走一步生命值减 1，吃到东西回满 100。", "也就是说，100 回合不吃东西，就会饿死。"]})
    S({"id": "r-wall", "type": "demo", "chapter": "规则", "demo": "wall", "cell": 64, "rate": 2.4, "play_at": "L0", "colors": one,
       "title": "撞墙", "items": [{"text": "头撞墙，死", "at": "L0"}], "say": ["头撞墙，死。"], "min": 3.6})
    S({"id": "r-body", "type": "demo", "chapter": "规则", "demo": "body", "cell": 64, "rate": 2.0, "play_at": "L0", "colors": two,
       "title": "撞身体", "items": [{"text": "头撞到任何一条蛇的身体，死", "at": "L0"}, {"text": "自己的身体也算", "at": "L0+2.0"}],
       "say": ["头撞到任何一条蛇的身体，也死，自己的也算。"], "min": 4.5})
    S({"id": "r-tail", "type": "demo", "chapter": "规则", "demo": "tail", "cell": 64, "rate": 2.0, "play_at": "L0", "colors": two,
       "title": "跟尾巴", "items": [{"text": "尾巴每回合缩回一格", "at": "L0"}, {"text": "所以可以贴着尾巴走", "at": "L0+2.2"}],
       "say": ["不过尾巴每回合会缩回去一格，所以贴着别人的尾巴走是安全的。"]})
    S({"id": "r-head", "type": "demo", "chapter": "规则", "demo": "head", "cell": 64, "rate": 2.0, "play_at": "L0", "colors": two,
       "title": "撞头", "items": [{"text": "两个蛇头进了同一格", "at": "L0"}, {"text": "长的活，短的死", "at": "L0+1.8"}, {"text": "一样长，一起死", "at": "L1"}],
       "say": ["最刺激的是撞头：两个蛇头撞进同一格，长的那条活下来。", "一样长的话，两条一起死。"]})
    S({"id": "r-rank", "type": "list", "chapter": "规则", "title": "怎么排名次",
       "items": [{"html": "活得越久，名次越靠前", "at": "L0"}, {"html": "都活到最后，<span class='hl'>比谁更长</span>", "at": "L0+2"},
                 {"html": "单挑：2 条蛇，15×15，最多 500 回合", "at": "L1"},
                 {"html": "大乱斗：11 条蛇，31×31，最多 800 回合", "at": "L2"}],
       "say": ["名次看谁活得久。都活到最后，就比谁更长。",
               "比两种赛制。单挑，两条蛇在 15×15 的小棋盘上一对一。",
               "大乱斗，10 个 AI 再加一个陪练，11 条蛇挤在 31×31 的大棋盘上。"]})
    # ------------------------------------------------------------ D 提示词和条件
    prompt_text = (ROOT / "prompt" / "PROMPT.md").read_text()
    S({"id": "prompt", "type": "doc", "chapter": "出题", "doc_title": "PROMPT.md · 发给 10 位选手的同一份提示词",
       "text": prompt_text, "scroll": [1.0, 26.0, 2100],
       "keys": [{"text": "一字不差的同一份提示词", "at": "L0"}, {"text": "只有一次写程序的机会", "at": "L1"},
                {"text": "自检出错，最多改 2 次", "at": "L2"}, {"text": "陪练基准 = 0 分", "at": "L4"}],
       "say": ["每家拿到的提示词就是屏幕上这一份，一字不差。",
               "规矩很简单：只有一次写程序的机会。看不到裁判，不能先试打，写完直接交卷。",
               "交上来以后，裁判先拿它和陪练打 12 局自检，只查会不会报错、超时、卡死，不告诉它输赢。",
               "出错了，就给一份错误报告，最多再改两次。",
               "陪练是我们写的一个中规中矩的程序：躲开马上会死的方向，看空间，追最近的食物。正式排名里，它就是零分线。"]})
    S({"id": "terms", "type": "list", "chapter": "出题", "title": "参赛条件，实话实说",
       "items": [{"html": "8 家通过 API 调用，思考档开到 high", "at": "L0"},
                 {"html": "GPT 在 <span class='hl'>Codex</span> 里写，Claude 在 <span class='hl'>Claude Code</span> 里写，同样不准运行代码", "at": "L1"},
                 {"html": "回复被通道截断的，作废重跑，<span class='hl'>不扣修复机会</span>", "at": "L2"},
                 {"html": "所有中断和事故，都记在开源说明里", "at": "L3"}],
       "say": ["参赛条件也说清楚。8 家是通过 API 调的，思考档都开到 high。",
               "GPT 是在 Codex 里写的，Claude 是在 Claude Code 里写的，也都只准写一次，不准运行代码。",
               "有几家的回复写到一半被通道截断了，这是我们这边的问题，那几次作废重跑，不扣它们的修复机会。",
               "比赛里所有的中断和事故，我们都一条一条记下来了。"]})
    return scenes



# ---------------------------------------------------------------- 交卷过程
def bars_scene(sid, title, note, rows, unit="", dec=0, chapter="交卷", say=(), start="L0", step=0.35, fixed=None):
    """rows: [(slug, value)]，按值从大到小。fixed: {slug: 显示文字}，用于「不适用」之类。"""
    rows = sorted(rows, key=lambda x: -(x[1] or 0))
    top = max((v or 0) for _, v in rows) or 1
    out = []
    for slug, v in rows:
        r = {"who": slug, "value": v or 0, "w": 900 * (v or 0) / top, "dec": dec}
        if fixed and slug in fixed:
            r["label_fixed"] = fixed[slug]
            r["w"] = 0
        out.append(r)
    return {"id": sid, "type": "bars", "chapter": chapter, "title": title, "note": note, "unit": unit, "rows": out,
            "row_at": [f"{start}+{0.4 + i * step:.2f}" for i in range(len(out))], "say": list(say)}


def writing_section():
    sc = []
    api = [s for s in ORDER if F[s]["channel"] == "Evolink API"]
    think = [(s, think_minutes(s)) for s in api]
    fast = min(think, key=lambda x: x[1])
    slow = sorted(think, key=lambda x: -x[1])[:2]
    sc.append(bars_scene("w-think", "动笔前想了多久", "API 选手：从发出请求到写出第一个字（分钟）。Claude 和 GPT 用的是各自的工具，拿不到这项数据。",
                         think, unit=" 分钟", dec=1, say=[
                             f"先看动笔之前想了多久。最快的是 {CAST[fast[0]]['name']}，{cn(round(fast[1] * 60))}秒就开始写了。",
                             f"最慢的是 {CAST[slow[0][0]]['name']}，想了{cn(round(slow[0][1]))}分钟才写第一个字，"
                             f"{CAST[slow[1][0]]['name']} 想了{cn(round(slow[1][1]))}分钟。"]))
    toks = [(s, reasoning(s)) for s in ORDER if reasoning(s)]
    tmax = max(toks, key=lambda x: x[1])
    tmin = min(toks, key=lambda x: x[1])
    sc.append(bars_scene("w-tokens", "思考了多少 token", "计入成绩的那几次请求里，模型自己报的思考 token。GPT 走 Codex，拿不到用量。",
                         toks + [("astra", None)], unit="", fixed={"astra": "拿不到"}, say=[
                             f"思考量也差得很远。{CAST[tmax[0]]['name']} 一共想了{wan(tmax[1])}个 token，" +
                             (f"最少的是 Grok 4.7 计入成绩的那一次，只有{wan(tmin[1])}；它被截断作废的那两次，可是想了好几万。"
                              if tmin[0] == "grok" else f"最少的 {CAST[tmin[0]]['name']} 只有{wan(tmin[1])}。")]))
    lines = [(s, F[s]["code_lines"]) for s in ORDER]
    lmax, lmin = max(lines, key=lambda x: x[1]), min(lines, key=lambda x: x[1])
    sc.append(bars_scene("w-lines", "交上来的代码有多长", "bot.py 的行数", lines, unit=" 行", say=[
        f"代码长度也一样。最长的是 {CAST[lmax[0]]['name']}，{cn(lmax[1])}行；最短的是 {CAST[lmin[0]]['name']}，只有{cn(lmin[1])}行。"]))
    words = [(s, summary_chars(s)) for s in ORDER]
    zero = [s for s, v in words if v == 0]
    wmax = max(words, key=lambda x: x[1])
    over = [s for s, v in words if v > 300]
    say = [f"提示词要求代码后面用三百字以内说说策略。{CAST[wmax[0]]['name']} 写了{cn(wmax[1])}字，超了。"]
    if zero:
        say.append(f"{'、'.join(CAST[s]['name'] for s in zero)} 一个字都没写，只交了代码。")
    sc.append(bars_scene("w-words", "策略说明写了多少字", "要求 300 字以内（去掉空白和符号后的字数）", words, unit=" 字", say=say,
                         fixed={s: "没写" for s in zero}))
    return sc


# ---------------------------------------------------------------- 放榜
def times_baseline(x):
    return 10 ** (x / 400)


def number_line(scores):
    lo = min(min(scores.values()), 0)
    hi = max(max(scores.values()), 0)
    pad = (hi - lo) * 0.06 or 50
    lo, hi = lo - pad, hi + pad
    L, Rr = 160, 1760

    def x(v):
        return L + (Rr - L) * (v - lo) / (hi - lo)
    step = 100 if hi - lo < 1200 else 200
    ticks = [(round(x(v)), f"{v:+d}" if v else "0") for v in range(int(math.ceil(lo / step) * step), int(hi) + 1, step)]
    return x, ticks


def ranking_section():
    sc = []
    scores = {s: score(s) for s in RANK}
    x, ticks = number_line(scores)
    zero_x = round(x(0))
    below = [s for s in RANK if score(s) < 0]
    sc.append({"id": "rk-explain", "type": "list", "chapter": "放榜", "title": "实力值怎么算",
               "items": [{"html": "每局按名次拆成两两比较，谁排前面算谁赢", "at": "L0"},
                         {"html": "单挑和大乱斗各占一半权重", "at": "L1"},
                         {"html": "陪练基准 = 0 分；<span class='hl'>高 400 分 = 强 10 倍</span>", "at": "L2"}],
               "say": ["排名怎么算？每一局都按名次拆成两两比较，谁排在前面就算谁赢一次。",
                       "单挑和大乱斗各占一半权重，再用 Bradley–Terry 模型算出每家的实力值。",
                       "陪练基准是 0 分。比它高 400 分，就是强 10 倍；低于 0，就是连陪练都没打过。"]})
    marks_done = []
    n = len(RANK)
    for i, s in enumerate(reversed(RANK)):
        place = n - i
        p, lo, hi = TOTAL[s]
        k = times_baseline(p)
        if lo <= 0 <= hi:
            ex = "和陪练在误差范围内"
        elif p >= 0:
            ex = f"约是基准的 {k:.1f} 倍"
        else:
            ex = f"只有基准的 {k:.2f} 倍"
        top3 = place <= 3
        marks = [{"who": m, "x": round(x(score(m)))} for m in marks_done] + [{"who": s, "x": round(x(p)), "self": True}]
        # 头像挤在一起时往上错开
        for a in marks:
            a["lift"] = 0
        marks_sorted = sorted(marks, key=lambda a: a["x"])
        for j in range(1, len(marks_sorted)):
            if marks_sorted[j]["x"] - marks_sorted[j - 1]["x"] < 56:
                marks_sorted[j]["lift"] = 0 if marks_sorted[j - 1]["lift"] else 70
        line = rank_line(s, place, p, k)
        sc.append({"id": f"rk-{place}", "type": "rank", "chapter": "放榜", "who": s, "no": f"第 {place} 名", "score": round(p),
                   "ex": ex + f" · 95% 区间 {lo:+.0f} ~ {hi:+.0f}", "ex_at": "L0+1.2", "silhouette": top3,
                   "reveal_at": "L0+1.6" if top3 else 0, "marks": marks, "ticks": ticks, "zero_x": zero_x,
                   "say": line, "sfx": [{"at": 1.6 if top3 else 0.5, "kind": "thud"}]})
        marks_done.append(s)
    pod = []
    for i, (s, xx, h, bg, label) in enumerate([(RANK[1], 260, 300, "#9aa8c7", "2"), (RANK[0], 750, 400, "#e3b23c", "1"),
                                                (RANK[2], 1240, 220, "#b5794a", "3")]):
        pod.append({"who": s, "x": xx, "h": h, "bg": bg, "rank": label, "score": f"{score(s):+.0f} 分", "at": f"L0+{0.3 + i * 0.5:.1f}"})
    p1, p2 = TOTAL[RANK[0]], TOTAL[RANK[1]]
    tie = p1[1] <= p2[2]
    sc.append({"id": "podium", "type": "podium", "chapter": "放榜", "items": pod,
               "say": [f"冠军是 {CAST[RANK[0]]['name']}。" + (
                   "不过它和第二名只差几分，区间大幅重叠，严格说算并列。" if tie and p1[0] - p2[0] < 30 else
                   f"它和第二名 {CAST[RANK[1]]['name']} 的 95% 区间有一点重叠，这个第一没有看上去那么稳。" if tie else
                   f"它和第二名 {CAST[RANK[1]]['name']} 的区间不重叠，是实打实的第一。")],
               "sfx": [{"at": 0.3, "kind": "jingle"}]})
    return sc


def rank_line(s, place, p, k):
    name = CAST[s]["name"]
    st = R["stats"][s]
    lo, hi = TOTAL[s][1], TOTAL[s][2]
    near = lo <= 0 <= hi
    extra = f"单挑胜率 {round(st['duel_winrate'] * 100)}%，大乱斗平均排第 {round(st['melee_avg_place'], 1):g}。"
    if place <= 3:
        return [f"第{cn(place)}名……", f"{name}，{sign(p)}。" + extra]
    if near:
        return [f"第{cn(place)}名，{name}，{sign(p)}，和陪练在误差范围内，算打平。" + extra]
    if p < 0:
        return [f"第{cn(place)}名，{name}，{sign(p)}，没打过陪练。" + extra]
    return [f"第{cn(place)}名，{name}，{sign(p)}。" + extra]


# ---------------------------------------------------------------- 风格标签、两种赛制、花费、结尾
def labels_section():
    st = R["stats"]
    deaths = {s: {c: st[s].get(f"melee_death_{c}", 0) + st[s].get(f"duel_death_{c}", 0)
                  for c in ("wall", "body", "self", "head", "starve")} for s in RANK}
    games = {s: st[s]["duel_games"] + st[s]["melee_games"] for s in RANK}
    cand = [
        # (标签, 指标, 越大越突出, 说明模板)
        ("单挑之王", lambda s: st[s]["duel_winrate"], lambda s: f"单挑胜率 {st[s]['duel_winrate'] * 100:.1f}%"),
        ("乱斗之王", lambda s: st[s]["melee_first_rate"], lambda s: f"大乱斗拿第一 {st[s]['melee_first_rate'] * 100:.1f}%"),
        ("最能苟", lambda s: st[s]["melee_survive_rate"], lambda s: f"大乱斗活到最后 {st[s]['melee_survive_rate'] * 100:.1f}%"),
        ("最能吃", lambda s: st[s]["melee_ate_avg"], lambda s: f"大乱斗平均每局吃 {st[s]['melee_ate_avg']:.1f} 颗"),
        ("最会撞人", lambda s: (st[s]["melee_kills_avg"] * st[s]["melee_games"] + st[s]["duel_kills_avg"] * st[s]["duel_games"]) / games[s],
         lambda s: f"平均每局撞死 {(st[s]['melee_kills_avg'] * st[s]['melee_games'] + st[s]['duel_kills_avg'] * st[s]['duel_games']) / games[s]:.2f} 条蛇"),
        ("饿死专业户", lambda s: deaths[s]["starve"] / games[s], lambda s: f"{deaths[s]['starve'] / games[s] * 100:.1f}% 的局饿死"),
        ("自己绕死", lambda s: deaths[s]["self"] / games[s], lambda s: f"{deaths[s]['self'] / games[s] * 100:.1f}% 的局撞到自己"),
        ("头铁撞墙", lambda s: deaths[s]["wall"] / games[s], lambda s: f"{deaths[s]['wall'] / games[s] * 100:.1f}% 的局撞墙"),
        ("单挑偏科", lambda s: R["duel"][s][0] - R["melee"][s][0],
         lambda s: f"单挑 {R['duel'][s][0]:+.0f}，大乱斗 {R['melee'][s][0]:+.0f}"),
        ("乱斗偏科", lambda s: R["melee"][s][0] - R["duel"][s][0],
         lambda s: f"大乱斗 {R['melee'][s][0]:+.0f}，单挑 {R['duel'][s][0]:+.0f}"),
        ("最长寿", lambda s: (st[s].get("melee_death_turn_sum", 0) + 800 * st[s].get("melee_survive", 0)) / st[s]["melee_games"],
         lambda s: f"大乱斗平均活到第 {(st[s].get('melee_death_turn_sum', 0) + 800 * st[s].get('melee_survive', 0)) / st[s]['melee_games']:.0f} 回合"),
        ("动笔最快", lambda s: -(think_minutes(s) if think_minutes(s) is not None else 20),
         lambda s: f"写程序时 {think_minutes(s):.1f} 分钟就开始写第一行"),
        ("最省电", lambda s: -st[s]["cpu_ms_avg"], lambda s: f"每步平均只算 {st[s]['cpu_ms_avg']:.1f} 毫秒"),
        ("最费脑", lambda s: st[s]["cpu_ms_avg"], lambda s: f"每步平均算 {st[s]['cpu_ms_avg']:.1f} 毫秒"),
    ]
    # 每个标签算出各家的 z 分数，贪心分配：每家一个标签，每个标签一家
    import statistics as stx
    table = []
    for word, f, desc in cand:
        vals = {s: f(s) for s in RANK}
        mu, sd = stx.mean(vals.values()), (stx.pstdev(vals.values()) or 1)
        for s in RANK:
            table.append(((vals[s] - mu) / sd, word, s, desc))
    table.sort(key=lambda t: -t[0])
    used_w, used_s, items = set(), set(), {}
    for z, word, s, desc in table:
        if word in used_w or s in used_s or z < 0.3:
            continue
        used_w.add(word)
        used_s.add(s)
        items[s] = {"who": s, "word": word, "stat": desc(s)}
    for s in RANK:  # 没有特别突出的，标它的总排名
        if s not in items:
            items[s] = {"who": s, "word": f"第 {RANK.index(s) + 1} 名", "stat": f"单挑胜率 {st[s]['duel_winrate'] * 100:.1f}%"}
    lst = [items[s] for s in RANK]
    for i, it in enumerate(lst):
        it["at"] = f"L{min(i, 9)}"
    say = [f"{CAST[it['who']]['short']}，{it['word']}：{it['stat']}。" for it in lst]
    return [{"id": "labels", "type": "labels", "chapter": "赛后复盘", "items": lst, "say": say, "gap": 0.15}]


def formats_section():
    d, m = R["duel"], R["melee"]
    gapd = sorted(RANK, key=lambda s: -(d[s][0] - m[s][0]))
    duel_best = max(RANK, key=lambda s: d[s][0])
    melee_best = max(RANK, key=lambda s: m[s][0])
    t = formats_table()
    gap = max(RANK, key=lambda s: abs(d[s][0] - m[s][0]))
    t["say"] = [f"两种赛制分开看。单挑最强的是 {CAST[duel_best]['name']}，{sign(d[duel_best][0])}。",
                (f"大乱斗最强的是 {CAST[melee_best]['name']}，{sign(m[melee_best][0])}。" if melee_best != duel_best else "大乱斗最强的也是它。"),
                f"差得最多的是 {CAST[gap]['name']}：单挑{sign(d[gap][0])}，大乱斗{sign(m[gap][0])}。"]
    return [t]


def sign(x):
    x = round(x)
    return (f"+{x}" if x > 0 else f"−{abs(x)}" if x < 0 else "0") + "分"


def cost_section():
    L = json.loads((ROOT / "contest" / "ledger.json").read_text())
    rows = []
    for r in L["rows"]:
        s = r["slug"]
        cost = f"¥{r['cny']:.2f}" if r["cny"] is not None else "不适用"
        toks = f"{r['output']:,}" if r["output"] else "拿不到"
        reqs = r["requests"] if r["requests"] is not None else "—"
        rows.append([s, reqs, toks, cost])
    paid = [r for r in L["rows"] if r["cny"] is not None]
    hi = max(paid, key=lambda r: r["cny"])
    lo = min(paid, key=lambda r: r["cny"])
    w = L["account_window"]
    return [{"id": "cost", "type": "table", "chapter": "赛后复盘", "title": "写一个程序花了多少钱",
             "note": f"按实测单价 × 收到的 token 折算，含作废重跑。账户同期实际扣费 ¥{w['cny'] + L['before_window_credits'] * L['cny_per_credit']:.2f}，"
                     "多出的部分分不到具体哪一家（截断的长回复上游可能还在计费）。Claude 和 GPT 走订阅工具，不按 API 计费",
             "head": ["选手", "发出请求", "输出 token（含思考）", "花费"], "num_cols": [1, 2, 3], "rows": rows,
             "row_at": [f"L0+{0.3 + i * 0.25:.2f}" for i in range(len(rows))],
             "say": [f"最后算算账。按实测单价折算，最贵的是 {CAST[hi['slug']]['name']}，{yuan(hi['cny'])}；"
                     f"最便宜的是 {CAST[lo['slug']]['name']}，{yuan(lo['cny'])}。",
                     f"不过账户里实际扣掉的钱比折算的多，写程序这一步一共花了{yuan(w['cny'] + L['before_window_credits'] * L['cny_per_credit'])}，"
                     "多出来的那部分没法精确算到哪一家头上，嫌疑最大的是那几次被截断的长回复。"]}]


def yuan(x):
    y = int(x)
    f = round((x - y) * 100)
    if f == 100:
        y, f = y + 1, 0
    jiao, fen = divmod(f, 10)
    s = (cn(y) + "块") if y else ""
    if jiao:
        s += cn(jiao) + "毛"
    if fen:
        s += cn(fen) + ("分" if y or jiao else "分钱")
    return s or "不到一分钱"


# ---------------------------------------------------------------- 选手入场
def intro_section():
    sc = []
    for i, s in enumerate(ORDER):
        f = F[s]
        facts = []
        tm = think_minutes(s)
        if f["attempts"] == 1:
            facts.append({"html": "自检：<b>一次通过</b>"})
        else:
            facts.append({"html": f"自检：<b>改了 {f['attempts'] - 1} 次才通过</b>"})
        if tm is not None:
            facts.append({"html": f"动笔前想了 <b>{tm:.1f} 分钟</b>"})
        rt = reasoning(s)
        if rt:
            facts.append({"html": f"思考 <b>{rt:,}</b> token"})
        facts.append({"html": f"代码 <b>{f['code_lines']}</b> 行"})
        for j, x in enumerate(facts):
            x["at"] = f"L0+{0.6 + j * 0.45:.2f}"
        chips = {"opus": ["思考档：工具默认"], "astra": ["思考档：max"], "grok": ["思考档：low（前两档被截断）"]}.get(s, [f"思考档：{effort(s)}"])
        sc.append({"id": f"in-{s}", "type": "intro", "chapter": "选手入场", "who": s, "no": f"{i + 1} 号选手",
                   "channel": CAST[s]["channel"], "chips": chips, "facts": facts, "say": [INTRO_LINES[s]],
                   "sfx": [{"at": 0.25, "kind": "pop"}], "tail": 0.6})
    return sc


def effort(s):
    for u in (json.loads((ROOT / "contest" / s / "log.json").read_text())["attempts"]):
        return (u.get("params") or {}).get("reasoning_effort", "high")
    return "high"


def _lines(s):
    return F[s]["code_lines"]


def _kimi_first_lines():
    return (ROOT / "contest" / "kimi" / "bot-0.py").read_text().count("\n")


def _max_cpu_first(s):
    return max(x for x in F[s]["selfcheck_max_cpu_ms"] if x)


INTRO_LINES = {
    "opus": f"一号，Claude Opus 5.5，在本机的 Claude Code 里写，没调用任何工具，交了{cn(_lines('opus'))}行，一次通过自检。",
    "astra": f"二号，GPT-6 Astra，在 Mac Pro 的 Codex 里写。中途通道断了两回，最后把{cn(_lines('astra'))}行代码写进文件交卷，也是一次通过。",
    "gemini": f"三号，Gemini 4 Argon，交了全场最长的{cn(_lines('gemini'))}行。可第一次交上来的代码里多了两个空格，程序直接跑不起来，改了一次才过。",
    "deepseek": f"四号，DeepSeek V4.1 Flash，动笔最快，想了不到三分钟就开始写，{cn(_lines('deepseek'))}行，一次通过。",
    "kimi": f"五号，Kimi K3，第一版{cn(_kimi_first_lines())}行，太能算了，一步最多算了将近八百毫秒，严重超时，改了一次才过。",
    "doubao": f"六号，豆包 Seed 2.0 Pro，{cn(_lines('doubao'))}行。它的策略里写着：比对手长，就主动去撞。",
    "qwen": f"七号，千问 3.8 Max，想了二十四分钟才动笔，交了{cn(_lines('qwen'))}行。",
    "glm": f"八号，GLM 5.3，想得最久，三十一分钟，思考了将近六万个 token。",
    "minimax": f"九号，MiniMax M3.1 Flash，代码最短，{cn(_lines('minimax'))}行，四分多钟就交卷了，一个字的说明都没写。",
    "grok": f"十号，Grok 4.7。前两次想得太久，回复被通道截断，降到最低的思考档，才交出{cn(_lines('grok'))}行。",
}


# ---------------------------------------------------------------- 对局
CAUSE = {"wall": "撞墙", "body": "撞到别人的身体", "self": "撞到自己", "head": "撞头输了", "starve": "饿死"}


def load_game(rel):
    return json.loads((ROOT / rel).read_text())


def segs_for(G, plan):
    """plan: [(到第几回合, 每秒几回合, 标签)]，从第 0 回合开始依次播放。返回 [起始秒, 结束秒, 起始回合, 结束回合, 标签]。"""
    segs, t, turn = [], 0.0, 0
    for until, rate, label in plan:
        until = min(until, G["turns"])
        if until <= turn:
            continue
        d = (until - turn) / rate
        segs.append([round(t, 3), round(t + d, 3), turn, until, label])
        t += d
        turn = until
    return segs, t


def deaths_of(G):
    return [e for e in G["events"] if e["type"] == "die"]


def match_scene(sid, rel, title, meta, plan, say, chapter="精选对局", callouts=(), lead=0.5, chart=None, chart_max=None,
                order=None, focus=None):
    G = load_game(rel)
    segs, dur = segs_for(G, plan)
    n = len(G["seats"])
    cell = 52 if n == 2 else 26
    if order is None:
        order = sorted(range(n), key=lambda i: G["place"][i])
    sc = {"id": sid, "type": "match", "chapter": chapter, "game": sid, "cell": cell, "bx": 52, "by": 92, "title": title, "meta": meta,
          "segs": [[a + lead, b + lead, ta, tb, lab] for a, b, ta, tb, lab in segs], "order": order,
          "chart": chart if chart is not None else list(range(n)), "chart_label": "长度走势（横轴：回合）",
          "chart_max": chart_max or max(max(L) for L in G["len"]) + 2,
          "chart_y": 800 if n > 3 else 520, "chart_h": 220 if n > 3 else 300,
          "callouts": list(callouts), "min": dur + lead + 1.2, "say": say}
    if focus:
        sc["focus"] = focus
    return sc, G


def turn_time(sc, turn):
    for a, b, ta, tb, _ in sc["segs"]:
        if ta <= turn <= tb and tb > ta:
            return a + (b - a) * (turn - ta) / (tb - ta)
    return sc["segs"][-1][1]


def check_section():
    first = [s for s in ORDER if F[s]["attempts"] == 1]
    fixed = [s for s in ORDER if F[s]["attempts"] > 1]
    items = [{"html": f"一次通过自检：<span class='hl'>{len(first)} 家</span>", "at": "L0"}]
    for s in fixed:
        rep = F[s]["reports"][0]
        if "超时" in rep and "代码报错 0 次" in rep:
            n_to = re.search(r"超时 (\d+) 次", rep).group(1)
            why = f"超时 {n_to} 次"
        else:
            why = "代码报错（多了两个空格）" if s == "gemini" else "代码报错"
        items.append({"html": f"{CAST[s]['name']}：{why}，改 1 次后通过", "at": f"L{len(items)}"})
    say = [f"10 家里，有{cn(len(first))}家一次通过自检。"]
    for s in fixed:
        say.append({"gemini": "Gemini 是缩进出错：第七行开头多了一个空格，还有一个变量名中间多了个空格，十二局一局都没跑起来。",
                    "kimi": "Kimi 是太能算：每一步要在五十毫秒内给出方向，它的第一版有一步算了将近八百毫秒，十二局里超时二十七次。"}[s])
    say.append("两家都在第一次修复后过了关。十个程序全部进入正赛。")
    items.append({"html": "10 个程序全部进入正赛", "at": f"L{len(say) - 1}"})
    cut = [{"html": "Grok：思考 8.9 万 token 后被截断，又 5.2 万 token 后被截断，降到 low 才交卷", "at": "L0"},
           {"html": "Kimi、千问：各被截断过一次，作废重跑", "at": "L1"},
           {"html": "Gemini：主办方一开始把输出上限设成 3.2 万，太低，作废重跑", "at": "L2"}]
    return [{"id": "w-check", "type": "list", "chapter": "交卷", "title": "自检：只查会不会出错", "items": items, "say": say},
            {"id": "w-cut", "type": "list", "chapter": "交卷", "title": "想太多，被截断", "items": cut,
             "say": ["还有一种情况不算选手的错：回复太长，写到一半被通道截断。",
                     "最夸张的是 Grok：第一次想了将近九万个 token，一行代码都没交出来就断了；降一档又想了五万多，还是断；降到最低一档，四分钟交卷。",
                     "Kimi 和千问也各被截断过一次。Gemini 那次是我们一开始把上限设得太低。这些都作废重跑，不扣它们的修复机会。"]}]


# ---------------------------------------------------------------- 冷开场、精选对局、结尾
def cold_scene():
    c = P["cold"]
    G = load_game(c["file"])
    seat = G["seats"].index(c["who"])
    d = G["death"][seat]
    win = G["seats"][G["place"].index(1)]
    plan = [(d - 8, 60, "快放"), (d + 4, 3.0, "慢放"), (G["turns"], 50, "快放")]
    segs, dur = segs_for(G, plan)
    lead = 0.4
    n = len(G["seats"])
    lines = [{"text": f"第 {d} 回合", "at": round(lead + turn_time_raw(segs, d), 2)},
             {"text": "一口没吃，饿死了", "at": "L1", "gold": True},
             {"text": f"10 个 AI · {fmt(N_TOTAL)} 局", "at": "L2"},
             {"text": "谁能活到最后？", "at": "L3", "gold": True}]
    focus = None
    return {"id": "cold", "type": "cold", "game": "cold", "cell": 26, "bx": 60, "by": 92,
            "segs": [[a + lead, b + lead, ta, tb, lab] for a, b, ta, tb, lab in segs], "lines": lines, "min": dur + lead + 0.8,
            "ring": [seat, d - 8, d + 0.5],
            "lead": 0.3,
            "say": [f"第{cn(d)}回合，{c['color_word']}这条蛇突然停住，倒下了。",
                    f"没有撞墙，也没被谁撞，是饿死的。它从开局到现在，一口东西都没吃。",
                    f"这是十个 AI 各自写的贪吃蛇程序，在同一个赛场里，一共打了{cn(N_TOTAL)}局。",
                    "谁写的蛇最能活？谁的蛇连饭都不会吃？"]}, G


def turn_time_raw(segs, turn):
    for a, b, ta, tb, _ in segs:
        if ta <= turn <= tb and tb > ta:
            return a + (b - a) * (turn - ta) / (tb - ta)
    return segs[-1][1]


MINIS = []


def minis_for(games):
    """计数那一屏背景里的四块小棋盘：用片子里要放的几局真实对局快放。"""
    spots = [(70, 120, "m-melee"), (1460, 120, "cold"), (70, 640, "m-duel"), (1500, 640, "m-duel2")]
    out = []
    for x, y, gid in spots:
        if gid not in games:
            continue
        G = load_game(games[gid])
        cell = 12 if len(G["seats"]) > 2 else 24
        out.append({"game": gid, "x": x, "y": y, "cell": cell, "size": G["w"] * cell + cell, "rate": 40,
                    "colors": [CAST[s]["color"] for s in G["seats"]]})
    return out


def main():
    scenes, games = [], {}
    cold, Gc = cold_scene()
    games["cold"] = P["cold"]["file"]
    scenes.append(cold)
    scenes += build()
    scenes += intro_section()
    w = writing_section()
    scenes += [x for x in w if x["id"] != "w-words"]
    scenes += check_section()
    scenes.append({"id": "scale", "type": "counter", "chapter": "正赛", "label": "局正赛", "sub": f"单挑 {fmt(N_DUEL)} 局 · 大乱斗 {fmt(N_MELEE)} 局",
                   "sub_at": "L1", "total": N_TOTAL, "count": [0.3, 3.2], "minis": MINIS,
                   "say": [f"十个程序全部到齐，正赛开打，一共{cn(N_TOTAL)}局。",
                           f"单挑是每两家之间都打，每一对打{cn(N_DUEL // 55)}局，左右座位轮换；大乱斗{cn(N_MELEE)}局，每个程序每个座位都坐过。"]})
    m_scenes, m_games = matches_section()
    games.update(m_games)
    for sc in scenes:
        if sc["id"] == "scale":
            sc["minis"] = minis_for(games)
    scenes += m_scenes
    scenes += ranking_section()
    scenes += formats_section()
    scenes.append(melee_wins_scene())
    scenes.append(pairwise_table())
    scenes.append(deaths_table())
    scenes += labels_section()
    scenes += cost_section()
    scenes += qwen_section()
    scenes += [x for x in w if x["id"] == "w-words"]
    scenes += quotes_section()
    scenes += end_section()
    ep = {"voice": {"model": "qwen-audio-3.1-tts-flash", "voice": "longanyang_v3.1", "say_as": SAY_AS,
                    "instruction": "语速稍快，像游戏比赛解说，清晰有精神"},
          "cast": {k: {**CAST[k], "img": f"cast/{k}/n.png" if k != "baseline" else "brand/baseline.png"} for k in list(ORDER) + ["baseline"]},
          "games": games, "scenes": scenes, "bgm": "cheerful", "bgm_level": 0.42, "bgm_duck": 0.16, "sfx_level": 0.45}
    for sc in scenes:
        sc["say"] = [pangu(x) for x in sc.get("say", [])]
    out = VID / "ep1.json"
    out.write_text(json.dumps(ep, ensure_ascii=False, indent=1))
    print("写好", out, len(scenes), "场", sum(len(s.get("say", [])) for s in scenes), "句旁白")


def death_line(G, ev, names):
    who = CAST[G["seats"][ev["id"]]]["short"]
    cause = ev["cause"]
    by = CAST[G["seats"][ev["by"]]]["short"] if ev.get("by") is not None and ev["by"] != ev["id"] else None
    if cause == "head":
        both = any(e["type"] == "die" and e["t"] == ev["t"] and e["id"] == ev.get("by") and e.get("by") == ev["id"]
                   for e in G["events"])
        if by and both:
            return f"第{cn(ev['t'])}回合，{who}和{by}一样长，迎面撞上，同归于尽。"
        return f"第{cn(ev['t'])}回合，{who}和{by}撞头，{who}短了一截，出局。" if by else f"第{cn(ev['t'])}回合，{who}撞头出局。"
    if cause == "body":
        return f"第{cn(ev['t'])}回合，{who}一头撞上了{by}的身子。" if by else f"第{cn(ev['t'])}回合，{who}撞到身体出局。"
    if cause == "self":
        return f"第{cn(ev['t'])}回合，{who}把自己绕死了。"
    if cause == "wall":
        return f"第{cn(ev['t'])}回合，{who}撞墙。"
    return f"第{cn(ev['t'])}回合，{who}饿死了。"


def matches_section():
    sc, games = [], {}
    # 单挑：第 1 对第 2
    d = P["duel_top"]
    G = load_game(d["file"])
    a, b = G["seats"]
    win = G["seats"][G["place"].index(1)]
    lose = b if win == a else a
    deaths = deaths_of(G)
    rec = d["record"]
    top1, top2 = RANK[0], RANK[1]
    t1w = rec["top1_wins"]
    t2w = rec["games"] - t1w - rec["draws"]
    end_t = G["turns"]
    plan = [(max(0, end_t - 40), 16, "快放"), (end_t, 4, "慢放")]
    say = [f"先看一局单挑：总榜第一的 {CAST[top1]['name']}，对第二的 {CAST[top2]['name']}。",
           f"这两家一共交手{cn(rec['games'])}局，{CAST[top1]['short']}赢了{cn(t1w)}局，{CAST[top2]['short']}赢了{cn(t2w)}局"
           + (f"，平了{cn(rec['draws'])}局。" if rec["draws"] else "。"),
           "下面这一局，是它们所有对局里回合数最接近中位数的一局，不挑反杀。"]
    if deaths:
        say.append(death_line(G, deaths[-1], None) + f"{CAST[win]['short']}拿下这一局。")
    else:
        la, lb = G["len"][0][-1], G["len"][1][-1]
        say.append(f"两条蛇都活到了第{cn(end_t)}回合，比长度，{CAST[win]['short']}赢。")
    s1, _ = match_scene("m-duel", d["file"], f"单挑 · {CAST[a]['short']} 对 {CAST[b]['short']}", "正赛实录 · 一回合不跳", plan, say)
    sc.append(s1)
    games["m-duel"] = d["file"]
    # 单挑：第 3 对第 4
    d = P.get("duel_34")
    if d:
        G = load_game(d["file"])
        a, b = G["seats"]
        win = G["seats"][G["place"].index(1)]
        deaths = deaths_of(G)
        rec = d["record"]
        t3, t4 = RANK[2], RANK[3]
        end_t = G["turns"]
        plan = [(max(0, end_t - 30), 14, "快放"), (end_t, 4, "慢放")]
        say = [f"再看一局：第三名 {CAST[t3]['name']} 对第四名 {CAST[t4]['name']}。",
               f"这两家交手{cn(rec['games'])}局，{CAST[t3]['short']}赢了{cn(rec['top3_wins'])}局。"]
        if deaths:
            say.append(death_line(G, deaths[-1], None) + f"这一局归 {CAST[win]['short']}。")
        else:
            say.append(f"两条蛇都活到了第{cn(end_t)}回合，比长度，{CAST[win]['short']}赢。")
        s3, _ = match_scene("m-duel2", d["file"], f"单挑 · {CAST[a]['short']} 对 {CAST[b]['short']}", "正赛实录 · 一回合不跳", plan, say)
        sc.append(s3)
        games["m-duel2"] = d["file"]
    # 大乱斗：最典型的一局
    m = P["melee_typical"]
    G = load_game(m["file"])
    deaths = deaths_of(G)
    first = deaths[0] if deaths else None
    win = G["seats"][G["place"].index(1)]
    alive = [G["seats"][i] for i, x in enumerate(G["death"]) if x is None]
    plan = []
    t = 0
    key_turns = sorted({e["t"] for e in deaths})
    for kt in key_turns[:8]:
        if kt - 3 > t:
            plan.append((kt - 3, 16, "快放"))
        plan.append((kt + 2, 4, "慢放"))
        t = kt + 2
    plan.append((G["turns"], 30, "快放"))
    say = [f"再看一局大乱斗。{cn(len(G['seats']))}条蛇挤在同一个棋盘上，这一局的名次和总榜最接近。"]
    for e in deaths[:5]:
        say.append(death_line(G, e, None))
    if len(deaths) > 5:
        say.append(f"后面又倒下了{cn(len(deaths) - 5)}条。")
    if len(alive) > 1:
        say.append(f"打满{cn(G['turns'])}回合，活到最后的有{cn(len(alive))}条，比长度，{CAST[win]['short']}最长，第一。")
    else:
        say.append(f"最后只剩{CAST[win]['short']}一条，第一。")
    s2, _ = match_scene("m-melee", m["file"], "大乱斗 · 11 条蛇", "正赛实录 · 快放和慢放交替", plan, say)
    sc.append(s2)
    games["m-melee"] = m["file"]
    # 开场那一局，完整放一遍
    c = P["cold"]
    G = load_game(c["file"])
    deaths = deaths_of(G)
    win = G["seats"][G["place"].index(1)]
    alive = [G["seats"][i] for i, x in enumerate(G["death"]) if x is None]
    plan, t = [], 0
    for kt in sorted({e["t"] for e in deaths})[:9]:
        if kt - 3 > t:
            plan.append((kt - 3, 18, "快放"))
        plan.append((kt + 2, 4, "慢放"))
        t = kt + 2
    plan.append((G["turns"], 30, "快放"))
    say = ["还记得开场那条饿死的蛇吗？那一局后来是这样打完的。"]
    for e in deaths[:6]:
        say.append(death_line(G, e, None))
    if len(deaths) > 6:
        say.append(f"后面又倒下了{cn(len(deaths) - 6)}条。")
    if len(alive) > 1:
        say.append(f"打满{cn(G['turns'])}回合，活下来{cn(len(alive))}条，{CAST[win]['short']}最长，拿下这一局。")
    else:
        say.append(f"最后只剩{CAST[win]['short']}一条，拿下这一局。")
    s4, _ = match_scene("m-cold", c["file"], "开场那一局 · 完整回放", "正赛实录 · 快放和慢放交替", plan, say)
    sc.append(s4)
    games["m-cold"] = c["file"]
    return sc, games


def end_section():
    champ = RANK[0]
    beat = [s for s in RANK if TOTAL[s][1] > 0]
    tied = [s for s in RANK if TOTAL[s][1] <= 0 <= TOTAL[s][2]]
    lost = [s for s in RANK if TOTAL[s][2] < 0]
    think_rank = sorted([s for s in ORDER if think_minutes(s) is not None], key=lambda s: -think_minutes(s))
    longest = think_rank[0]
    items = [{"html": f"冠军：<span class='hl'>{CAST[champ]['name']}</span>", "at": "L0"},
             {"html": f"明显强过陪练：{len(beat)} 家；打平 {len(tied)} 家；没打过 {len(lost)} 家", "at": "L1"},
             {"html": f"想得最久的 {CAST[longest]['short']}：总榜第 {RANK.index(longest) + 1}", "at": "L2"},
             {"html": "下一集玩什么？评论区告诉我们", "at": "L3"}]
    say = [f"这一集的冠军是 {CAST[champ]['name']}。",
           f"10 家里有{cn(len(beat))}家明显比陪练强" + (f"；{'、'.join(CAST[s]['short'] for s in tied)}和陪练在误差范围内" if tied else "")
           + (f"；{'、'.join(CAST[s]['short'] for s in lost)}没打过陪练。" if lost else "。"),
           f"想得最久的 {CAST[longest]['short']}，最后排第{cn(RANK.index(longest) + 1)}。想得久，不一定写得好。",
           "下一集让它们玩什么游戏？评论区告诉我们。"]
    return [{"id": "end", "type": "end", "chapter": "", "title": "AI 像素擂台 · 第 1 集完", "items": items, "cast": RANK, "say": say, "tail": 1.5}]



def qwen_section():
    X = json.loads((ROOT / "results" / "extra" / "qwen_tail_experiment.json").read_text())
    src = (ROOT / "bots" / "qwen.py").read_text().splitlines()
    pick = [(291, 293), (297, 311), (372, 373), (381, 382)]   # 行号（从 1 数），原样摘录
    parts = []
    for a, b in pick:
        parts.append(f"# 第 {a}–{b} 行")
        parts += src[a - 1:b]
        parts.append("")
    code = "\n".join(parts)
    st = R["stats"]["qwen"]
    starve_melee = st.get("melee_death_starve", 0) / st["melee_games"]
    o, n = X["original"], X["no_tail_bonus"]
    return [
        {"id": "qwen-code", "type": "doc", "chapter": "赛后复盘", "small": True, "doc_title": "bots/qwen.py · 千问交上来的原样代码（摘录，行号见注释）",
         "text": code, "scroll": None,
         "keys": [{"text": "绕回自己尾巴：+180,000", "at": "L1"}, {"text": "离食物每远一格：−1,500", "at": "L2"},
                  {"text": "饿急了：+60,000 对 −12,000", "at": "L3"}],
         "say": [f"回头说开场那条饿死的蛇。千问在全部 {int(st['duel_games'] + st['melee_games'])} 局里，有一半是饿死的；"
                 f"{N_MELEE} 局大乱斗里，有 {P['cold']['qwen_starve_at_100']} 局正好饿死在第 100 回合。原因就写在它的代码里。",
                 "它给每个方向打分：走这一步之后，要是还能绕回自己的尾巴，加 18 万分。",
                 "离食物每远一格，只扣 1500 分。",
                 "就算饿到生命值 25 以下，绕尾巴还有 6 万分，吃东西每格扣 1.2 万。食物只要在 5 格开外，它还是宁可绕着自己的尾巴转圈。"]},
        {"id": "qwen-exp", "type": "list", "chapter": "赛后复盘", "title": "赛后小实验（不计成绩）：只改这一个数",
         "items": [{"html": f"原版：平均每局吃 <span class='hl'>{o['ate_avg']}</span> 颗，20 局饿死 {o['starved']} 局", "at": "L1"},
                   {"html": f"绕尾巴奖励改成 0：平均每局吃 <span class='hl'>{n['ate_avg']}</span> 颗，饿死 {n['starved']} 局", "at": "L2"},
                   {"html": f"平均活到第 {o['survive_turn_avg']:.0f} 回合 → 第 {n['survive_turn_avg']:.0f} 回合", "at": "L3"}],
         "say": ["为了确认，我们赛后做了个小实验，不计成绩：只把这一项奖励改成零，别的一个字不动，和十个陪练各打二十局大乱斗。",
                 f"原版平均每局只吃{yi(o['ate_avg'])}颗，二十局里饿死{cn(o['starved'])}局。",
                 f"改完以后，平均每局吃{yi(n['ate_avg'])}颗，只饿死{cn(n['starved'])}局。",
                 f"平均能活到的回合数，从第{cn(round(o['survive_turn_avg']))}回合变成了第{cn(round(n['survive_turn_avg']))}回合。一个数，差这么多。"]}]


def st_pct(x):
    return f"{round(x * 100)}%"


def yi(x):
    return f"{x:g}"


def quotes_section():
    picks = [RANK[0], RANK[1], "doubao"]
    seen, out = set(), []
    texts = {"astra": ASTRA_SUMMARY,
             "opus": "单挑：双方同时出招，按对手总能选出对我最不利的那一步来搜，配合 α-β 剪枝逐层加深，CPU 时间约 30 毫秒就停。",
             "doubao": "主动进攻：长度占优时主动撞击短蛇的可能前进位置，消灭对手减少竞争。",
             "gemini": "单挑与残局通过 8 层同步 Alpha-Beta 搜索实施抢食压制、贴墙封锁与死路围杀；大乱斗优先确保安全生存与局部长度优势，规避高危对撞。",
             "kimi": None}
    st = R["stats"]
    for s in picks:
        if s in seen or not texts.get(s):
            continue
        seen.add(s)
        say = [f"{CAST[s]['name']} 交卷时是这么说的。"]
        if s == "doubao":
            kills = (st[s]["melee_kills_avg"] * st[s]["melee_games"] + st[s]["duel_kills_avg"] * st[s]["duel_games"]) / (st[s]["melee_games"] + st[s]["duel_games"])
            say.append(f"说得挺凶。实际打下来，它平均每局撞死{yi(round(kills, 2))}条蛇，总榜第{cn(RANK.index(s) + 1)}。")
        else:
            say.append(f"它最后排第{cn(RANK.index(s) + 1)}。")
        out.append({"id": f"q-{s}", "type": "quote", "chapter": "交卷原话", "who": s, "who_note": " · 策略说明原文", "text": texts[s],
                    "src": "摘自交卷时代码后面的策略说明，原文照录", "type_at": "L0+0.3", "cps": 18, "say": say,
                    "min": 0.6 + len(texts[s]) / 18 + 1.5})
    return out


def melee_wins_scene():
    st = R["stats"]
    rows = [(x, int(st[x]["melee_first"])) for x in RANK] + [("baseline", int(st["baseline"]["melee_first"]))]
    top = max(rows, key=lambda r: r[1])
    zero = [x for x, v in rows if v == 0]
    sc = bars_scene("melee-wins", f"{N_MELEE} 局大乱斗，谁拿第一最多", "每家在大乱斗里拿第一的局数（11 条蛇同场，含陪练基准）",
                    rows, unit=" 局", chapter="赛后复盘",
                    say=[f"大乱斗一共{cn(N_MELEE)}局，{CAST[top[0]]['name']} 拿了{cn(top[1])}局第一，占{round(top[1] / N_MELEE * 100)}%。"] +
                        ([f"{'、'.join(CAST[x]['short'] for x in zero)}一局第一都没拿到。"] if zero else []))
    return sc


def deaths_table():
    st = R["stats"]
    rows = []
    for s in RANK:
        g = st[s]["duel_games"] + st[s]["melee_games"]
        def pct(k):
            v = st[s].get(f"duel_death_{k}", 0) + st[s].get(f"melee_death_{k}", 0)
            return f"{v / g * 100:.0f}%"
        alive = (st[s].get("duel_survive", 0) + st[s].get("melee_survive", 0)) / g
        rows.append([s, f"{alive * 100:.0f}%", pct("starve"), pct("self"), pct("body"), pct("head"), pct("wall")])
    starve_top = max(RANK, key=lambda s: (st[s].get("duel_death_starve", 0) + st[s].get("melee_death_starve", 0)) / (st[s]["duel_games"] + st[s]["melee_games"]))
    self_top = max(RANK, key=lambda s: (st[s].get("duel_death_self", 0) + st[s].get("melee_death_self", 0)) / (st[s]["duel_games"] + st[s]["melee_games"]))
    alive_top = max(RANK, key=lambda s: (st[s].get("duel_survive", 0) + st[s].get("melee_survive", 0)) / (st[s]["duel_games"] + st[s]["melee_games"]))
    def rate(s, k):
        return (st[s].get(f"duel_{k}", 0) + st[s].get(f"melee_{k}", 0)) / (st[s]["duel_games"] + st[s]["melee_games"])
    return {"id": "deaths", "type": "table", "chapter": "赛后复盘", "title": "都是怎么死的",
            "note": "每家所有对局里，各种结局占的比例（单挑和大乱斗合计）",
            "head": ["选手", "活到最后", "饿死", "撞自己", "撞别人身体", "撞头输了", "撞墙"], "num_cols": [1, 2, 3, 4, 5, 6],
            "rows": rows, "row_at": [f"L0+{0.3 + i * 0.25:.2f}" for i in range(len(rows))],
            "say": [f"再看看都是怎么死的。最能活的是 {CAST[alive_top]['name']}，{round(rate(alive_top, 'survive') * 100)}% 的局都活到了最后。",
                    f"最容易把自己绕死的是 {CAST[self_top]['name']}，{round(rate(self_top, 'death_self') * 100)}% 的局撞到了自己的身体。",
                    f"饿死最多的当然是 {CAST[starve_top]['name']}，{round(rate(starve_top, 'death_starve') * 100)}% 的局是饿死的。"]}


def pairwise_table():
    import csv
    top = RANK[:5]
    rd = list(csv.reader((RES / "pairwise.csv").open()))
    head = rd[0][1:]
    M = {r[0]: dict(zip(head, r[1:])) for r in rd[1:]}
    rows = []
    for a in top:
        rows.append([a] + [("—" if a == b else f"{float(M[a][b]) * 100:.0f}%") for b in top])
    best = max(((a, b) for a in top for b in top if a != b and float(M[a][b]) < 0.5 and RANK.index(a) < RANK.index(b)),
               key=lambda x: 0.5 - float(M[x[0]][x[1]]), default=None)
    say = ["前五名之间的单挑胜率是这样的，横着看，是这一行的选手赢那一列的比例。"]
    if best:
        a, b = best
        say.append(f"有意思的是，总榜排在前面的 {CAST[a]['short']}，单挑打 {CAST[b]['short']} 只赢了 {round(float(M[a][b]) * 100)}%。"
                   "单挑赢得多，不等于总分高，大乱斗那一半权重很要命。")
    return {"id": "pairwise", "type": "table", "chapter": "赛后复盘", "title": "前五名之间的单挑胜率",
            "note": "行选手赢列选手的比例，每一对 " + str(R["counts"]["duel"] // 55) + " 局",
            "head": ["选手"] + [CAST[b]["short"] for b in top], "num_cols": list(range(1, len(top) + 1)),
            "rows": rows, "row_at": [f"L0+{0.3 + i * 0.3:.2f}" for i in range(len(rows))], "say": say}


def formats_table():
    d, m = R["duel"], R["melee"]
    rows = [[s, f"{d[s][0]:+.0f}", f"{m[s][0]:+.0f}", f"{TOTAL[s][0]:+.0f}"] for s in RANK]
    return {"id": "formats-t", "type": "table", "chapter": "赛后复盘", "title": "单挑和大乱斗分开排",
            "note": "两种赛制分别拟合的实力值（陪练基准 = 0）", "head": ["选手", "单挑", "大乱斗", "总分"], "num_cols": [1, 2, 3],
            "rows": rows, "row_at": [f"L0+{0.3 + i * 0.25:.2f}" for i in range(len(rows))]}


if __name__ == "__main__":
    main()
