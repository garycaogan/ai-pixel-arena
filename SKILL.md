---
name: ai-pixel-arena
description: AI 像素擂台：让一群大模型拿一字不差的同一份提示词，各写一个游戏程序（第 1 集是贪吃蛇），放进同一个像素赛场打几千局，按真实成绩排名；再从比赛记录自动出分镜、旁白、棋盘回放、角色图和封面，用 HyperFrames 渲染成 B 站横版长片。8 家走 Evolink 自动发题、收卷、自检，GPT 和 Claude 可以在 Codex、Claude Code 里用订阅参赛。第 1 集的规则、10 家原样代码、8470 局记录和出片代码都在里面，能原样重做；换游戏照「换个游戏」一节让 Agent 改。Use for AI 写代码比赛、AI 编程对战视频、大模型贪吃蛇大乱斗、赛博斗蛐蛐、AI 算法对抗赛。让 AI 不写程序、亲自上桌玩的那种用 deepsea-ai-holdem。
---

# AI 像素擂台

这个 skill 就是开源仓库 [garycaogan/ai-pixel-arena](https://github.com/garycaogan/ai-pixel-arena)（MIT）本身。第 1 集《贪吃蛇大乱斗》全程用它做完：10 家模型各写一个贪吃蛇程序，正赛 8,470 局，按 Bradley–Terry 排名，再从记录里出片。这一页是给 Agent 的做法；每个脚本的参数和细节在 `README.md`，比赛条件和事故在 `docs/CONDITIONS.md`，花费在 `docs/LEDGER.md`。

下面的命令都在这个 skill 文件夹里跑。

## 准备

- Python 3.11 以上。比赛、裁判、自检、评分只用标准库；出片、角色图和封面要 `pip install -r requirements.txt`（numpy、Pillow、fontTools、brotli），建议先建一个 `.venv`。
- 出片要 Node.js 22 以上和 ffmpeg。渲染用 `npx` 自动下载的 HyperFrames 0.8.181，它会自己准备浏览器。
- 一把 Evolink key：8 家选手写程序、旁白配音（通义千问 TTS）、角色草稿（GPT Image）都走它。设环境变量 `EVOLINK_API_KEY`，或者把 key 存进一个文件、用 `EVOLINK_API_KEY_FILE` 指过去（默认找 `~/.config/evolink/api.key`）。脚本不打印 key。
- 选填：本机的 Codex 和 Claude Code，让 GPT、Claude 用订阅参赛。没有就只比 Evolink 上那几家，或者照 `tools/contest.py` 的 `MODELS` 把 Evolink 上有的 GPT、Claude 型号加进去。
- 正文字体 Noto Sans SC 按 README「出片」一节的命令下载到 `fonts/`。不下也能出片，正文先用像素字体顶上。
- 选手程序在 macOS 上跑在 `sandbox-exec` 沙箱里（不能联网、写文件、开子进程）。Linux 上设 `ARENA_NO_SANDBOX=1`，那就没有沙箱，只跑信得过的代码。Windows 没测过。

## 一、先把第 1 集跑一遍（不花钱，几分钟）

先确认整条链在这台电脑上能走通，再做自己的一期：

```bash
python -m arena.selfcheck bots/opus.py
python -m arena.tournament --rounds 2 --workers 8 --out my-games.jsonl.gz
python -m arena.analyze my-games.jsonl.gz --out my-results
python video/make_ep1.py
python video/build.py video/ep1.json --out video/work/ep1 --no-tts
```

前三条打两轮 242 局、出一份排名；后两条从仓库里的第 1 集记录出分镜，再搭成一个 HyperFrames 工程（`--no-tts` 不调任何接口，按字数估每句多长）。看画面不用整集渲染，到 `video/work/ep1` 里截几帧：

```bash
npx --yes hyperframes@0.8.181 snapshot --at 5,30,600 --describe false
```

`--describe false` 别省，环境里有 `GEMINI_API_KEY` 时它默认会调 Gemini 给每帧写描述，要花钱。要出整集成片，去掉 `--no-tts`、加上 `--render out/ep1.mp4`：整集旁白配音不到 0.2 元，配音按句缓存在 `video/cache/`，再跑不重复花钱。

## 二、做新的一期

1. **挑游戏。** 看点在画面、玩法和故事，不在局数。挑规则一句话讲得清、很多个程序同场会乱成一团、画成像素画面好看的游戏（贪吃蛇、炸弹人、坦克、格斗这一类）。先想好片子里要讲的故事：谁会赢、谁会出洋相、哪个设计会把某家坑死。
2. **写规则引擎和陪练。** 照 `arena/snake.py` 里 `Game` 的接口写新游戏；`arena/referee.py`、`selfcheck.py`、`tournament.py`、`export.py`、`demos.py` 都直接 import 贪吃蛇，把 import 换掉，比赛、自检、评分就能原样用。写一个陪练 `bots/baseline.py`，名字必须叫 `baseline`，评分拿它当 0 分线。选手少于 11 家时调 `arena/tournament.py` 里的大乱斗席位。README「换个游戏」一节列了贪吃蛇写死的每一处，先让 Agent 读那一节。
3. **写提示词。** 新游戏的 `prompt/PROMPT.md` 写全规则、程序接口、每步限时，所有选手一字不差。每家只有一次写程序的机会，看不到裁判代码，不能试打。
4. **发题、收卷。** 先查一次 Evolink 现在有哪些模型（`GET https://api.evolink.ai/v1/models`），改 `tools/contest.py` 的 `MODELS`。它写死了第 1 集的路径，直接跑会覆盖第 1 集的程序和记录，先复制一份改成新游戏的路径，再一家一家跑：`python tools/contest.py gemini kimi deepseek ...`。它自动收代码、跑 12 局自检，出错发统一的报告，最多给 2 次修复机会，回复被截断的那次作废重跑，每次请求的原文、思考、用量都记进 `contest/<模型>/`。GPT、Claude 走订阅时，在 Codex 和 Claude Code 里发 `prompt/HARNESS_NOTE.md` 加 `PROMPT.md`，把回复里的代码存成 `bots/<名字>.py`，自检和修复照同一套规矩手工做，经过写进 `docs/CONDITIONS.md`。
5. **正赛和排名。** 新程序名字加进 `arena/tournament.py` 的 `ENTRANTS`，跑 `python -m arena.tournament --rounds <轮数> --workers 8 --out <记录>`，再 `python -m arena.analyze <记录> --out <成绩目录>`。一轮 121 局，8 个进程在一台 Mac 上不到 2 分钟。打到排名的区间分得开、名场面够挑就停；几千局不是卖点。
6. **挑局和分镜。** 设 `ARENA_RESULTS=<成绩目录>`，用 `video/pick_games.py` 照 `results/picks.json` 的规则挑典型局（不专挑反杀）。`video/make_ep1.py` 是第 1 集专用的，新游戏照 `video/ep1.json` 的格式写自己的分镜，片子里每个数字都从成绩和 `contest/` 里读，不手填。
7. **出片。** `video/board.js` 画的是蛇和樱桃，`video/template.html` 底栏写着「第 1 集 · 贪吃蛇大乱斗」，生命值条和死因文字也是贪吃蛇的，换游戏一起改。然后 `python video/build.py <分镜> --out video/work/<期> --render out/<期>.mp4`。
8. **角色和封面。** `tools/gen_cast.py` 用 GPT Image 画角色草稿（每次都不一样，存下来再用），`python tools/make_cast.py` 切开、压成像素形象；`brand/make_cover.py` 出封面。封面上的产品标志商标归各公司，先跑 `brand/fetch_logos.py` 下载到 `brand/logos/`，不随包分发。
9. **审片。** 开头 15 秒有没有钩子、画面有没有空着的地方；模型名字读没读错（念错就在分镜 `voice.say_as` 里加一条改写）；片子里的数字和成绩表对不对得上。

## 花多少钱

第 1 集有账单的部分合计约 53 元：8 家写程序按实测单价折合约 24 元（同一段时间账户余额实际少了约 47 元，含试探和作废的请求）；角色草稿和封面背景用 GPT Image 约 1.7 元；6,930 字旁白用通义千问 TTS 约 0.2 元。GPT、Claude 走订阅不另算。贵的是写程序那步，思考强度开得越高越贵，单价和每家用量见 `docs/LEDGER.md`。

## 做片子的几条经验

- 观众爱看的是乱斗，规则和选手介绍要短。规则最好压在比赛画面上用演示讲，不单独切一页；选手入场也在赛场上弹角色卡介绍。
- 局数不是卖点，画面、玩法、故事和解说才是。画面做到观众看完想自己玩一把。
- 开头 15 秒要又快又满，前几秒就放最离谱的那一局；旁白要有活人感，不念稿。
- 每期看各平台的评论再改下一期。我们几期下来，评论里呼声最高的是复仇赛：让每家看到对手的代码、改一版再打。
- 片长跟着同类爆款走，B 站这类比赛片十几到二三十分钟；第 1 集 B 站的留存显示只有讲规则那段掉得快。

## 目录

| 路径 | 内容 |
|---|---|
| `prompt/` | 发给选手的提示词，和给 Codex、Claude Code 两家多加的条件说明 |
| `arena/` | 规则引擎、裁判、自检、正赛调度、评分、回放导出 |
| `bots/` | 10 家交上来的原样代码和陪练基准 |
| `contest/` | 每家每次请求的原始回复、思考、用量、自检报告 |
| `results/` | 逐局记录（能完整重放）、成绩、两两胜率、选手数据、精选对局 |
| `video/` | 分镜生成和 HyperFrames 出片（像素棋盘、旁白、字幕、芯片音乐） |
| `cast/`、`brand/` | 角色像素形象、头像、陪练机器人、封面脚本 |
| `tools/` | API 选手发题收卷、实测单价和账本、角色草稿和切图 |
| `docs/` | 比赛条件与事故记录、花费账本 |

代码按 MIT 许可；`fonts/` 里的像素字体按 SIL OFL 1.1；各家 AI 的名字和商标归各自公司，本项目和各家模型公司没有关系。
