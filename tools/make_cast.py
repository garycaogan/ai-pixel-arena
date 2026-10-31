"""从两张角色草稿重做 10 位选手的像素形象，参数和第 1 集用的一样，输出和仓库里的 cast/ 逐字节一致。

python tools/make_cast.py

1. tools/cut_sheet.py 把每张五人草稿切成单人图 → cast/cut/<选手>.png
2. Grok 那张左边带进来一缕旁边 MiniMax 的红头发，涂白（当时手工做的一步，原样写在这里）
3. tools/sprite.py 把单人图压成像素形象 → cast/<选手>/n.png（另存一张带坐标格的 n_grid.png 预览，不进仓库）
   Kimi 是白头发白衣服，通用参数下脸会糊，单独用了一组参数，并保护脸部那块不被平滑掉。

草稿本身是 GPT Image 画的（tools/gen_cast.py），重新画每次都不一样，所以这里从仓库里存的草稿开始。
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SHEETS = {
    "cast/drafts/sheet-a-1792567340-0.png": ["opus", "astra", "gemini", "deepseek", "kimi"],
    "cast/drafts/sheet-b-1792567397-0.png": ["doubao", "qwen", "glm", "minimax", "grok"],
}
COMMON = ["--cell", "12", "--colors", "20", "--dark", "0.30", "--thicken", "3", "--merge", "14"]
SPECIAL = {"kimi": ["--cell", "12", "--colors", "16", "--dark", "0.55", "--thicken", "3", "--merge", "14", "--smooth", "13,17,36,36"]}


def main():
    for sheet, names in SHEETS.items():
        subprocess.run([sys.executable, str(TOOLS / "cut_sheet.py"), str(ROOT / sheet), *names], check=True)
    grok = ROOT / "cast" / "cut" / "grok.png"
    a = np.asarray(Image.open(grok).convert("RGB")).copy()
    a[600:930, :74] = 255
    Image.fromarray(a).save(grok)
    for names in SHEETS.values():
        for name in names:
            (ROOT / "cast" / name).mkdir(parents=True, exist_ok=True)
            subprocess.run([sys.executable, str(TOOLS / "sprite.py"), str(ROOT / "cast" / "cut" / f"{name}.png"),
                            str(ROOT / "cast" / name / "n.png"), *SPECIAL.get(name, COMMON)], check=True)


if __name__ == "__main__":
    main()
