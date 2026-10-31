"""B 站封面 1920×1080：
左上系列名，右上「第 N 集 · 游戏」红色角标和「N 局实测」描边角标，中间两行悬念大字（白一行、黄一行，黑色粗描边），
下面一排参赛角色贴纸，角色头顶各顶一个所属产品的 logo 徽章，背景是对局画面。
- 背景是一局大乱斗放大到格子很大的一块，蛇身又长又亮，一眼看得出是贪吃蛇；只在字的后面压暗。
- 左上和右上的角标往里收，保证 4:3 居中裁切后字、人物和 logo 都完整。
logo 取自 @lobehub/icons-static-png，商标归各公司所有，不随仓库发布：先跑 brand/fetch_logos.py 下载到 brand/logos/；
没有这些文件时封面照样出，只是角色头顶不带徽章。

python brand/fetch_logos.py
python brand/make_cover.py --games 8470 --bg results/games/melee_typical.json --turn 330 --cell 46 --dy 300 --shade 0.35 --out brand/cover.jpg
"""
import argparse
import base64
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["opus", "astra", "gemini", "deepseek", "kimi", "doubao", "qwen", "glm", "minimax", "grok"]


def b64(p):
    return "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()


def cast():
    import sys
    sys.path.insert(0, str(ROOT / "video"))
    from cast import CAST
    return CAST


def page(games: int, bg: Path, turn: int, cell=62, dy=140, shade=0.8, episode="第 1 集 · 贪吃蛇", line1="10 个 AI 各写一条贪吃蛇", line2="谁能活到最后？"):
    C = cast()
    G = json.loads(Path(bg).read_text())
    colors = [C[s]["color"] for s in G["seats"]]
    logos = ROOT / "brand" / "logos"
    chars = "".join(
        f'<div class="p">' + (f'<div class="b" style="border-color:{C[s]["color"]}"><img src="{b64(logos / (s + ".png"))}" /></div>'
                              if (logos / (s + ".png")).is_file() else "") +
        f'<img class="c" src="{b64(ROOT / "cast" / s / "n.png")}" /></div>' for s in ORDER)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: H; font-weight: 900; src: url("fonts/as-900.woff2"); }}
@font-face {{ font-family: P; src: url("fonts/px.woff2"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1920px; height:1080px; overflow:hidden; background:#0b1324; }}
.bg {{ position:absolute; inset:0; filter:brightness(0.92) saturate(1.15); }}
.bg canvas {{ position:absolute; left:0; top:0; width:1920px; height:1080px; }}
.shade {{ position:absolute; left:0; right:0; top:0; height:560px;
         background:linear-gradient(rgba(8,12,28,{min(1, shade + 0.12)}) 0%, rgba(8,12,28,{shade}) 55%, rgba(8,12,28,0) 100%); }}
.logo {{ position:absolute; left:262px; top:40px; display:flex; align-items:center; gap:18px; }}
.logo img {{ width:92px; height:92px; image-rendering:pixelated; border-radius:14px; }}
.logo .t {{ font-family:P; font-size:60px; color:#fff; line-height:1; text-shadow:4px 4px 0 #000; }}
.logo .e {{ font-family:P; font-size:24px; color:#ffd23f; margin-top:6px; letter-spacing:2px; }}
.ep {{ position:absolute; right:262px; top:40px; background:#e8503a; color:#fff; font-family:H; font-weight:900; font-size:52px;
      padding:6px 30px 10px; border-radius:16px; }}
.n {{ position:absolute; right:262px; top:132px; color:#bfe0ff; font-family:H; font-weight:900; font-size:40px; padding:4px 22px 8px;
     border:4px solid #6db7ff; border-radius:14px; background:rgba(10,20,40,0.75); }}
.l1, .l2 {{ position:absolute; left:0; right:0; text-align:center; font-family:H; font-weight:900; white-space:nowrap; }}
.l1 {{ top:196px; font-size:100px; color:#fff; -webkit-text-stroke:22px #000; paint-order:stroke fill; }}
.l2 {{ top:318px; font-size:184px; color:#ffd23f; -webkit-text-stroke:32px #000; paint-order:stroke fill; letter-spacing:4px; }}
.row {{ position:absolute; left:244px; right:244px; bottom:0; height:520px; display:flex; justify-content:center; align-items:flex-end; }}
.p {{ display:flex; flex-direction:column; align-items:center; margin:0 -4px; }}
.b {{ width:104px; height:104px; border-radius:50%; background:#fff; border:7px solid; display:flex; align-items:center; justify-content:center;
     margin-bottom:8px; box-shadow:0 0 0 4px #000, 5px 6px 0 4px rgba(0,0,0,0.45); }}
.b img {{ width:70px; height:70px; }}
.c {{ height:392px; width:auto; image-rendering:pixelated;
     filter: drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(6px 6px 0 rgba(0,0,0,0.5)); }}
</style></head><body>
<div class="bg"><canvas id="cv" width="1920" height="1080"></canvas></div>
<div class="shade"></div>
<div class="logo"><img src="{b64(ROOT / 'brand/avatar-1024.png')}" /><div><div class="t">AI 像素擂台</div><div class="e">AI PIXEL ARENA</div></div></div>
<div class="ep">{episode}</div><div class="n">{games} 局实测</div>
<div class="l1">{line1}</div><div class="l2">{line2}</div>
<div class="row">{chars}</div>
<script>{(ROOT / "video" / "board.js").read_text()}</script>
<script>
const G = {json.dumps(G)};
const colors = {json.dumps(colors)};
const ctx = document.getElementById("cv").getContext("2d");
ctx.fillStyle = "#0b1324"; ctx.fillRect(0, 0, 1920, 1080);
// 格子放大，整盘比画面大，只露出一块：蛇身够粗，缩成小图也认得出
const cell = {cell}, W = G.w * cell;
drawBoard(ctx, G, {turn}, {{cell, ox: (1920 - W) / 2, oy: (1080 - W) / 2 + {dy}, colors}});
</script>
</body></html>"""


def shoot(html: str, out: Path):
    """用 HyperFrames 自带的浏览器截一张图：包成一个 1 秒的合成，截第 0.5 秒。"""
    work = ROOT / "video" / "work" / "cover"
    work.mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0, str(ROOT / "video"))
    from build import _fonts
    (work / "fonts").mkdir(exist_ok=True)
    _fonts(html, work / "fonts")
    body = html.split("<body>")[1].split("</body>")[0]
    head = html.split("<head>")[1].split("</head>")[0]
    (work / "index.html").write_text(f"""<!doctype html><html><head>{head}
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="1">{body}</div>
<script>const tl = gsap.timeline({{ paused: true }}); tl.to({{}}, {{ duration: 1 }}); window.__timelines["main"] = tl;</script>
</body></html>""")
    snaps = work / "snaps"
    subprocess.run(["npx", "--yes", "hyperframes@0.8.181", "snapshot", "--at", "0.5", "--no-end", "-o", str(snaps), "--describe", "false"],
                   cwd=work, check=True, capture_output=True)
    png = next(snaps.glob("frame-*.png"))
    from PIL import Image
    Image.open(png).convert("RGB").save(out, quality=94)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, required=True)
    ap.add_argument("--bg", required=True, help="一局的回放数据（arena/export.py 的输出），画它某一回合当背景")
    ap.add_argument("--turn", type=int, required=True)
    ap.add_argument("--cell", type=int, default=62, help="格子边长（像素）")
    ap.add_argument("--dy", type=int, default=140, help="棋盘相对居中往下挪多少像素")
    ap.add_argument("--shade", type=float, default=0.8, help="字后面压暗的程度")
    ap.add_argument("--out", default=str(ROOT / "brand" / "cover.jpg"))
    a = ap.parse_args()
    print(shoot(page(a.games, Path(a.bg), a.turn, a.cell, a.dy, a.shade), Path(a.out)))
