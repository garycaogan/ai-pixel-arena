"""下载封面上用的 10 个产品标志到 brand/logos/（不随仓库发布，商标归各公司所有）。

python brand/fetch_logos.py

来源是 @lobehub/icons-static-png@1.90.0 的 light 版，和第 1 集封面用的同一批文件。
Kimi 用的是单色版 kimi.png（彩色版是白字，放在白底徽章上看不见）。
"""
import urllib.request
from pathlib import Path

BASE = "https://unpkg.com/@lobehub/icons-static-png@1.90.0/light/"
LOGOS = {
    "opus": "claude-color", "astra": "openai", "gemini": "gemini-color", "deepseek": "deepseek-color", "kimi": "kimi",
    "doubao": "doubao-color", "qwen": "qwen-color", "glm": "zhipu-color", "minimax": "minimax-color", "grok": "grok",
}


def main():
    out = Path(__file__).resolve().parent / "logos"
    out.mkdir(exist_ok=True)
    for slug, name in LOGOS.items():
        data = urllib.request.urlopen(BASE + name + ".png", timeout=60).read()
        (out / f"{slug}.png").write_bytes(data)
        print(slug, name, len(data))


if __name__ == "__main__":
    main()
