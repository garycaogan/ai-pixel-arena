"""Turn a flat-coloured character drawing into a clean pixel sprite.

Vendored from pixel-diary (https://github.com/garycaogan/pixel-diary, MIT, same author), including the
--merge option used for this episode. tools/make_cast.py runs it with the exact settings of episode 1.

    python tools/sprite.py draft.png cast/name/n.png --width 52 [--crop x0,y0,x1,y1]

Steps: cut the white background, quantise to a small palette, take each cell's majority colour
(keeping outlines and pupils), remove speckles, add a 1-px outer outline. Then write a preview
with a coordinate grid so you can find the eyes and mouth for face.json.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _background(a: np.ndarray) -> np.ndarray:
    h, w, _ = a.shape
    near = (a.min(axis=2) > 232) & ((a.max(axis=2) - a.min(axis=2)) < 18)
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not bg[y, x]:
                bg[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not bg[y, x]:
                bg[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                q.append((ny, nx))
    return bg


def pixelize(img: Image.Image, width: int = 0, colors: int = 16, dark_frac: float = 0.42, cell: float = 0) -> np.ndarray:
    """Give either the sprite width in pixels or the cell size in draft pixels (same cell = same scale across a cast)."""
    a = np.asarray(img.convert("RGB")).astype(int)
    bg = _background(a)
    ys, xs = np.where(~bg)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = img.convert("RGB").crop((x0, y0, x1, y1))
    mask = ~bg[y0:y1, x0:x1]
    pal_img = crop.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    idx = np.asarray(pal_img)
    palette = np.array(pal_img.getpalette()[: colors * 3]).reshape(-1, 3)
    lum = palette @ np.array([0.299, 0.587, 0.114])
    dark = np.where(lum < 75)[0]
    outline = palette[dark[np.argmin(lum[dark])]] if len(dark) else np.array([30, 24, 40])
    ch, cw = idx.shape
    if cell:
        width = max(1, int(round(cw / cell)))
    else:
        cell = cw / width
    h = int(round(ch / cell))
    grid = -np.ones((h, width), int)
    for j in range(h):
        for i in range(width):
            ya, yb = int(j * cell), max(int(j * cell) + 1, int((j + 1) * cell))
            xa, xb = int(i * cell), max(int(i * cell) + 1, int((i + 1) * cell))
            m = mask[ya:yb, xa:xb]
            if m.size == 0 or m.mean() < 0.5:
                continue
            vals = idx[ya:yb, xa:xb][m]
            counts = np.bincount(vals, minlength=colors).astype(float)
            if len(dark) and counts[dark].sum() / len(vals) >= dark_frac:
                grid[j, i] = dark[np.argmax(counts[dark])]
            else:
                c2 = counts.copy()
                c2[dark] = 0
                grid[j, i] = int(np.argmax(c2))
    for _ in range(2):  # a pixel whose four neighbours agree on another colour takes it
        g2 = grid.copy()
        for j in range(1, h - 1):
            for i in range(1, width - 1):
                nb = [grid[j - 1, i], grid[j + 1, i], grid[j, i - 1], grid[j, i + 1]]
                if grid[j, i] >= 0 and nb.count(nb[0]) == 4 and nb[0] >= 0 and nb[0] != grid[j, i]:
                    g2[j, i] = nb[0]
        grid = g2
    pad = np.pad(grid, 1, constant_values=-1)
    h2, w2 = pad.shape
    out = np.zeros((h2, w2, 4), np.uint8)
    for j in range(h2):
        for i in range(w2):
            k = pad[j, i]
            if k >= 0:
                out[j, i, :3] = palette[k]
                out[j, i, 3] = 255
            elif any(0 <= y < h2 and 0 <= x < w2 and pad[y, x] >= 0 for y, x in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1))):
                out[j, i, :3] = outline
                out[j, i, 3] = 255
    return _despeckle(out)


def _despeckle(a: np.ndarray) -> np.ndarray:
    """Lone dark pixels inside the figure (not on its edge) take the most common neighbouring colour."""
    h, w, _ = a.shape
    op = a[..., 3] > 0
    for _ in range(2):
        lum = a[..., :3] @ np.array([0.299, 0.587, 0.114])
        dark = op & (lum < 75)
        b = a.copy()
        for j in range(h):
            for i in range(w):
                if not dark[j, i]:
                    continue
                if any(not (0 <= y < h and 0 <= x < w) or not op[y, x] for y, x in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1))):
                    continue
                nb = [(y, x) for y in range(j - 1, j + 2) for x in range(i - 1, i + 2) if (y, x) != (j, i) and 0 <= y < h and 0 <= x < w]
                if sum(dark[y, x] for y, x in nb) <= 1:
                    cols = Counter(tuple(a[y, x]) for y, x in nb if op[y, x] and not dark[y, x])
                    if cols:
                        b[j, i] = cols.most_common(1)[0][0]
        a = b
    return a


def merge(a: np.ndarray, dist: float) -> np.ndarray:
    """Colours closer than dist (RGB distance) become the more common one, so near-identical shades stop speckling."""
    op = a[..., 3] > 0
    cols = Counter(tuple(int(v) for v in p[:3]) for p in a[op])
    keep: list[tuple] = []
    remap = {}
    for c, _ in cols.most_common():
        near = next((k for k in keep if sum((x - y) ** 2 for x, y in zip(c, k)) ** 0.5 < dist), None)
        if near is None:
            keep.append(c)
        else:
            remap[c] = near
    b = a.copy()
    for j, i in zip(*np.where(op)):
        c = tuple(int(v) for v in a[j, i, :3])
        if c in remap:
            b[j, i, :3] = remap[c]
    return b


def smooth(a: np.ndarray, protect: tuple) -> np.ndarray:
    """Pixels that share their colour with none of their 8 neighbours take the neighbours' majority colour,
    except inside the protected box (eyes keep their one-pixel highlights)."""
    h, w, _ = a.shape
    px0, py0, px1, py1 = protect
    b = a.copy()
    for j in range(1, h - 1):
        for i in range(1, w - 1):
            if a[j, i, 3] == 0 or (px0 <= i <= px1 and py0 <= j <= py1):
                continue
            nb = [tuple(a[y, x]) for y in range(j - 1, j + 2) for x in range(i - 1, i + 2) if (y, x) != (j, i)]
            if any(p[3] == 0 for p in nb) or tuple(a[j, i]) in nb:
                continue
            b[j, i] = Counter(nb).most_common(1)[0][0]
    return b


def grid_preview(sprite: np.ndarray, out_path: str, scale: int = 14, bg=(214, 232, 240)) -> None:
    h, w, _ = sprite.shape
    big = Image.fromarray(sprite, "RGBA").resize((w * scale, h * scale), Image.NEAREST)
    canvas = Image.new("RGBA", big.size, bg + (255,))
    canvas.alpha_composite(big)
    d = ImageDraw.Draw(canvas)
    for x in range(0, w, 2):
        d.line([(x * scale, 0), (x * scale, h * scale)], fill=(255, 0, 0, 160) if x % 10 == 0 else (0, 0, 0, 40))
    for y in range(0, h, 2):
        d.line([(0, y * scale), (w * scale, y * scale)], fill=(255, 0, 0, 160) if y % 10 == 0 else (0, 0, 0, 40))
    canvas.convert("RGB").save(out_path)


def char_map(sprite: np.ndarray, x0: int, x1: int, y0: int, y1: int) -> str:
    """A text map of a region, one letter per colour, for picking face coordinates."""
    cols = {}

    def ch(p):
        if p[3] == 0:
            return " "
        t = tuple(int(v) for v in p[:3])
        if t not in cols:
            cols[t] = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[len(cols) % 62]
        return cols[t]

    lines = ["    " + "".join(str(x % 10) for x in range(x0, x1))]
    for y in range(y0, y1):
        lines.append(f"{y:3d} " + "".join(ch(sprite[y, x]) for x in range(x0, x1)))
    lines += [f"{v} {k}" for k, v in cols.items()]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sprite.py")
    ap.add_argument("draft")
    ap.add_argument("out")
    ap.add_argument("--width", type=int, default=52)
    ap.add_argument("--cell", type=float, default=0, help="draft pixels per sprite pixel; overrides --width")
    ap.add_argument("--colors", type=int, default=16)
    ap.add_argument("--dark", type=float, default=0.42)
    ap.add_argument("--crop", help="x0,y0,x1,y1 in the draft, for a sheet with several characters")
    ap.add_argument("--thicken", type=int, default=0, help="darken-filter size (3 or 5) so thin outlines survive")
    ap.add_argument("--smooth", help="x0,y0,x1,y1 protected box (the face); lone pixels elsewhere are smoothed away")
    ap.add_argument("--merge", type=float, default=0, help="merge colours closer than this RGB distance (try 14)")
    a = ap.parse_args(argv)
    img = Image.open(a.draft)
    if a.crop:
        img = img.crop(tuple(int(v) for v in a.crop.split(",")))
    if a.thicken:
        img = img.convert("RGB").filter(ImageFilter.MinFilter(a.thicken))
    sp = pixelize(img, a.width, a.colors, a.dark, a.cell)
    if a.merge:
        sp = merge(sp, a.merge)
    if a.smooth:
        sp = smooth(sp, tuple(int(v) for v in a.smooth.split(",")))
    Image.fromarray(sp, "RGBA").save(a.out)
    grid_preview(sp, a.out.replace(".png", "_grid.png"))
    print(f"{a.out}: {sp.shape[1]}×{sp.shape[0]} px")


if __name__ == "__main__":
    main()
