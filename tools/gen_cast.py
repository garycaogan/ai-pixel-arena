"""用 GPT Image 2.5（Evolink）画 10 位选手的角色草稿：两张图，每张 5 人，同一套画风约束。

python tools/gen_cast.py a|b [--n 2]
草稿存到 cast/drafts/，任务花费（人民币）记到 cast/drafts/costs.json。
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ev  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cast" / "drafts"

STYLE = ("Character design lineup of five original chibi anime girls standing side by side in one row, full body, all facing the viewer, "
         "relaxed symmetrical idle poses, plain flat pure white background, no shadow, no text, no logos, no letters, no numbers. "
         "Same art style for all five: flat cel-shaded colors (two tones per material), thick clean dark outlines, no gradients, "
         "no texture, chibi proportions about 4 heads tall, big expressive eyes with one white highlight each, simple shapes, "
         "bold saturated hair color that is the main identifying color of each girl. ")
TAIL = ("All five full figures fit the frame height from hair top to shoes, evenly spaced with clear empty white space between "
        "every two girls so each can be cropped separately. Similar heights, each girl about one fifth of the image width.")

SHEETS = {
    "a": [
        "1 (far left): ORANGE. long bright orange hair in one thick braid over the shoulder, calm confident half smile, amber eyes, "
        "cream knit vest over a white shirt with a small orange necktie, dark brown pleated skirt, brown loafers, holding a small closed notebook",
        "2: EMERALD GREEN. short sleek black bob with bright emerald green inner color and a green hairband, sharp focused eyes, "
        "green and white zip-up track jacket, black shorts, white sneakers, one hand on hip",
        "3: VIOLET. long lavender violet twin tails with small star-shaped hairclips, cheerful sparkling eyes, violet sailor-style top "
        "with a white collar, violet pleated skirt, white socks, flashing a peace sign",
        "4: ROYAL BLUE. messy medium royal blue hair with one big ahoge, sleepy relaxed half-closed eyes, oversized deep blue hoodie "
        "with a small white wave pattern on the pocket, grey shorts, blue slide sandals, holding a fish-shaped snack",
        "5 (far right): WHITE. very long straight silver white hair with a crescent moon hairpin, gentle calm eyes, long white coat "
        "over a dark grey turtleneck, dark tights, short black boots, holding a thick book",
    ],
    "b": [
        "1 (far left): CYAN. bright cyan hair in two round buns on top of the head, big energetic open-mouth smile, cyan puffy short "
        "jacket, white skirt, cyan sneakers, holding a white steamed bun",
        "2: MAGENTA. long magenta pink high ponytail, confident wink, magenta sporty top with a mandarin collar and white cloud-pattern "
        "trim, white leggings, magenta flat shoes",
        "3: YELLOW. short messy golden yellow hair with a big yellow bow, determined toothy grin, bright yellow raincoat-style jacket, "
        "blue denim overalls shorts, yellow rubber boots, fists clenched",
        "4: RED. long straight red hair with blunt bangs, cool expressionless face, red blazer school uniform with a black ribbon, "
        "black pleated skirt, black knee socks, arms crossed",
        "5 (far right): LIME GREEN. spiky messy short lime green hair, mischievous smirk with tongue out, dark sunglasses pushed up "
        "on the head, black bomber jacket with lime green trim, grey cargo pants, chunky sneakers, hands in pockets",
    ],
}


def run(sheet: str, n: int = 2):
    OUT.mkdir(parents=True, exist_ok=True)
    prompt = STYLE + " ".join(SHEETS[sheet]) + ". " + TAIL
    costs_path = OUT / "costs.json"
    costs = json.loads(costs_path.read_text()) if costs_path.exists() else []
    ids = []
    for _ in range(n):
        r = ev.post("/images/generations", {"model": "gpt-image-2.5-sunburst", "prompt": prompt, "size": "3:2",
                                            "resolution": "2K", "n": 1, "quality": "high"})
        ids.append(r["id"])
    for k, tid in enumerate(ids):
        st = ev.task(tid, quiet=True)
        out = OUT / f"sheet-{sheet}-{int(time.time())}-{k}.png"
        ev.download(ev.result_url(st), out)
        cny = ((st.get("usage") or {}).get("cost") or {}).get("cny")
        costs.append({"sheet": sheet, "task": tid, "file": out.name, "cny": cny, "at": time.strftime("%Y-%m-%d %H:%M:%S %z")})
        print(out, cny, flush=True)
    costs_path.write_text(json.dumps(costs, ensure_ascii=False, indent=1))
    (OUT / f"prompt-{sheet}.txt").write_text(prompt)


if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 2)
