"""账号头像：深色底，一条十色像素蛇绕成一圈，中间是粗体像素字「AI」。全部用代码画，不用任何品牌图形。
B 站头像会裁成圆形，所以蛇走的是圆圈，四角留空。

.venv/bin/python brand/make_avatar.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
COLORS = ["#FF9838", "#1FC77E", "#A57BFF", "#4567FF", "#F2F2F2", "#2FD3E6", "#F05BC9", "#FFDD3C", "#FF4B4B", "#9BE23A"]
G = 40
A = ["..XXXX..", ".XXXXXX.", "XXX..XXX", "XX....XX", "XX....XX", "XXXXXXXX", "XXXXXXXX", "XX....XX", "XX....XX", "XX....XX"]
I = ["XXXXXX", "XXXXXX", "..XX..", "..XX..", "..XX..", "..XX..", "..XX..", "..XX..", "XXXXXX", "XXXXXX"]


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def ring(r, cx, cy):
    """顺时针走一圈的格子序列（相邻格子 4 连通）。"""
    pts = []
    for k in range(720):
        a = -math.pi / 2 + 2 * math.pi * k / 720
        p = (round(cx + r * math.cos(a)), round(cy + r * math.sin(a)))
        if not pts or p != pts[-1]:
            if pts and abs(p[0] - pts[-1][0]) + abs(p[1] - pts[-1][1]) == 2:
                pts.append((p[0], pts[-1][1]))
            pts.append(p)
    return pts[:-1] if pts[-1] == pts[0] else pts


def make(size=1024):
    im = Image.new("RGB", (G, G), (11, 19, 36))
    d = ImageDraw.Draw(im)
    for y in range(G):
        for x in range(G):
            if (x + y) % 2:
                d.point((x, y), (15, 26, 48))
    c = (G - 1) / 2
    path = ring(14.5, c, c)
    n = len(path) - 7          # 留一个缺口：蛇头前面空出来放樱桃
    seg = n / len(COLORS)
    for i in range(n):
        x, y = path[i]
        col = hexrgb(COLORS[min(len(COLORS) - 1, int(i / seg))])
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=col)
    hx, hy = path[n - 1]
    d.rectangle((hx - 2, hy - 2, hx + 2, hy + 2), fill=hexrgb(COLORS[-1]))
    d.point((hx - 1, hy - 1), (255, 255, 255)); d.point((hx + 1, hy - 1), (255, 255, 255))
    d.point((hx - 1, hy), (20, 20, 28)); d.point((hx + 1, hy), (20, 20, 28))
    fx, fy = path[n + 3]
    d.rectangle((fx - 1, fy - 1, fx + 1, fy + 1), fill=(255, 74, 90))
    d.point((fx, fy - 2), (95, 211, 90))
    # 「AI」
    w = len(A[0]) + 2 + len(I[0])
    ox, oy = int(c - w / 2) + 1, int(c - len(A) / 2) + 1
    for glyph, gx in ((A, ox), (I, ox + len(A[0]) + 2)):
        for r, row in enumerate(glyph):
            for q, ch in enumerate(row):
                if ch == "X":
                    d.point((gx + q + 1, oy + r + 1), (0, 0, 0))
        for r, row in enumerate(glyph):
            for q, ch in enumerate(row):
                if ch == "X":
                    d.point((gx + q, oy + r), (255, 210, 63))
    return im.resize((size, size), Image.NEAREST)


if __name__ == "__main__":
    make(1024).save(OUT / "avatar-1024.png")
    print(OUT / "avatar-1024.png")
