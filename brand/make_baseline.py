"""陪练基准的像素形象：灰色的训练机器人，全部用代码画。输出 brand/baseline.png（44×120）。

python brand/make_baseline.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "baseline.png"
W, H = 44, 120
O = (30, 32, 40, 255)
G1, G2, G3 = (125, 131, 143, 255), (96, 101, 112, 255), (160, 166, 178, 255)


def main():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def box(x0, y0, x1, y1, c):
        d.rectangle((x0, y0, x1, y1), fill=O)
        d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=c)

    box(12, 10, 31, 33, G1)  # 头
    d.rectangle((15, 19, 18, 22), fill=(240, 240, 245, 255)); d.rectangle((25, 19, 28, 22), fill=(240, 240, 245, 255))  # 眼
    d.rectangle((16, 20, 17, 21), fill=O); d.rectangle((26, 20, 27, 21), fill=O)
    d.rectangle((18, 27, 25, 28), fill=O)  # 嘴
    box(20, 4, 23, 10, G2); box(18, 1, 25, 4, (255, 210, 63, 255))  # 天线
    box(8, 34, 35, 78, G2)  # 身体
    box(14, 42, 29, 60, G3)  # 胸牌
    d.rectangle((17, 48, 26, 53), fill=O); d.rectangle((18, 49, 25, 52), fill=(255, 255, 255, 255))
    box(1, 38, 8, 70, G1); box(35, 38, 42, 70, G1)  # 手臂
    box(11, 78, 19, 112, G1); box(24, 78, 32, 112, G1)  # 腿
    box(8, 110, 20, 118, G2); box(23, 110, 35, 118, G2)  # 脚
    im.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
