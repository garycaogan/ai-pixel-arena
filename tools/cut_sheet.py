"""把一张五人角色图切成五张单人图：先去白底，再在相邻两人之间找一条最少穿过人物的竖向折线（seam）分开。

python tools/cut_sheet.py <sheet.png> name1 name2 name3 name4 name5
输出 cast/cut/<name>.png（白底，四周留白）。
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sprite import _background  # noqa: E402  去白底，和 tools/sprite.py 同一套


def seam(fg, lo, hi):
    """在列 [lo, hi) 之间找一条从上到下、每行最多左右挪一列的路径，穿过前景越少越好。"""
    h = fg.shape[0]
    band = fg[:, lo:hi].astype(np.float64) * 50 + 1
    w = band.shape[1]
    cost = band.copy()
    back = np.zeros((h, w), np.int8)
    for y in range(1, h):
        prev = cost[y - 1]
        left = np.r_[np.inf, prev[:-1]]
        right = np.r_[prev[1:], np.inf]
        stack = np.vstack([left, prev, right])
        k = stack.argmin(0)
        cost[y] += stack[k, np.arange(w)]
        back[y] = k - 1
    x = int(cost[-1].argmin())
    path = np.zeros(h, int)
    for y in range(h - 1, -1, -1):
        path[y] = x + lo
        x = int(np.clip(x + int(back[y, x]), 0, w - 1))
    return path


def main(sheet, names):
    a = np.asarray(Image.open(sheet).convert("RGB"))
    h, w, _ = a.shape
    fg = ~_background(a.astype(int))
    cols = fg.sum(0)
    # 五个人的大致中心：把列上的前景量分成五等份
    cum = np.cumsum(cols) / cols.sum()
    centers = [int(np.searchsorted(cum, (2 * k + 1) / 10)) for k in range(5)]
    seams = [np.zeros(h, int)]
    for k in range(4):
        seams.append(seam(fg, centers[k] + 60, centers[k + 1] - 60))
    seams.append(np.full(h, w))
    out_dir = ROOT / "cast" / "cut"
    out_dir.mkdir(parents=True, exist_ok=True)
    xs = np.arange(w)
    for k, name in enumerate(names):
        mask = fg & (xs[None, :] >= seams[k][:, None]) & (xs[None, :] < seams[k + 1][:, None])
        ys, xx = np.nonzero(mask)
        y0, y1, x0, x1 = ys.min(), ys.max(), xx.min(), xx.max()
        crop = a[y0:y1 + 1, x0:x1 + 1].copy()
        crop[~mask[y0:y1 + 1, x0:x1 + 1]] = 255
        pad = 24
        out = np.full((crop.shape[0] + 2 * pad, crop.shape[1] + 2 * pad, 3), 255, np.uint8)
        out[pad:-pad, pad:-pad] = crop
        Image.fromarray(out).save(out_dir / f"{name}.png")
        cut = int((fg[np.arange(h), np.clip(seams[k + 1], 0, w - 1)]).sum()) if k < 4 else 0
        print(name, (x0, y0, x1, y1), "seam 穿过人物的像素", cut)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:7])
