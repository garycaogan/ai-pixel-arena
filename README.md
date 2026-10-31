# AI 像素擂台

让一群 AI 模型拿到一字不差的同一份提示词，各自写一个游戏程序，再把这些程序放进同一个赛场里打几千局，按真实成绩排名。这里是视频系列「AI 像素擂台」的全部比赛材料：规则、提示词、裁判、每个模型交上来的原样代码、逐局记录、评分脚本，以及做视频用的分镜、回放渲染、角色图和封面脚本。

第 1 集是贪吃蛇大乱斗。

## 第 1 集 · 贪吃蛇

10 个模型拿到同一份提示词（[`prompt/PROMPT.md`](prompt/PROMPT.md)），各写一个 Python 贪吃蛇程序，正赛打了 8,470 局：单挑 7,700 局（55 对，每对 140 局，换边），大乱斗 770 局（10 个 AI 加陪练基准，11 条蛇同场）。

| 名次 | 选手 | 接入 | 实力值 | 95% 区间 | 单挑 | 大乱斗 | 单挑胜率 | 大乱斗平均名次 |
|---:|---|---|---:|---|---:|---:|---:|---:|
| 1 | GPT-6 Astra | Codex（Mac Pro，不走 API） | +389 | +370 ~ +408 | +394 | +374 | 83.5% | 2.38 |
| 2 | Claude Opus 5.5 | Claude Code（本机，不走 API） | +328 | +313 ~ +349 | +456 | +229 | 88.2% | 3.96 |
| 3 | Gemini 4 Argon | Evolink API | +183 | +166 ~ +202 | +36 | +331 | 43.9% | 2.80 |
| 4 | Kimi K3 | Evolink API | +177 | +160 ~ +194 | +212 | +142 | 65.5% | 5.11 |
| 5 | DeepSeek V4.1 Flash | Evolink API | +62 | +46 ~ +78 | +83 | +41 | 49.8% | 6.55 |
| 6 | Grok 4.7 | Evolink API | +48 | +35 ~ +68 | +120 | -18 | 54.5% | 7.37 |
| 7 | GLM 5.3 | Evolink API | +26 | +9 ~ +42 | +23 | +28 | 42.2% | 6.73 |
| 8 | MiniMax M3.1 Flash | Evolink API | +8 | -7 ~ +26 | +18 | -1 | 41.6% | 7.14 |
| — | 陪练基准 | 主办方写的 | 0 | | 0 | 0 | 39.5% | 7.12 |
| 9 | 豆包 Seed 2.0 Pro | Evolink API | -14 | -29 ~ +4 | -16 | -11 | 37.5% | 7.27 |
| 10 | Qwen 3.8 Max | Evolink API | -306 | -322 ~ -284 | -467 | -196 | 3.7% | 9.51 |

- 第 1、2 名的区间不重叠；第 3、4 名（Gemini、Kimi）区间大幅重叠，算并列。MiniMax 和豆包的区间跨过 0，和陪练基准在误差范围内。
- 单挑最强的是 Claude Opus 5.5（单挑 +456），大乱斗最强的是 GPT-6 Astra（大乱斗 +374，770 局里拿了 415 局第一）。两两胜率见 `results/pairwise.csv`，每家的打法数据见 `results/player-stats.csv`。
- 千问的程序在全部 2,170 局里有一半是饿死的，770 局大乱斗里有 168 局正好饿死在第 100 回合。原因在它的打分里：能绕回自己尾巴加 180,000 分，离食物每远一格只扣 1,500 分。赛后只把这一项改成 0 做了个不计成绩的小实验，见 `results/extra/qwen_tail_experiment.json`。
- 每家写程序的过程（交卷用时、思考 token、自检报告、修复、截断作废）在 `contest/` 和 [`docs/CONDITIONS.md`](docs/CONDITIONS.md)，花费在 [`docs/LEDGER.md`](docs/LEDGER.md)。
- 片子里放的几局怎么挑的写在 `results/picks.json`：都是按规则挑的典型局，不挑反杀。

## 规则速览

完整规则就是发给选手的提示词：[`prompt/PROMPT.md`](prompt/PROMPT.md)。

- 正方形棋盘，四周是墙。所有蛇同时行动，每回合走一格。
- 吃到食物长一节、生命值回满 100；每走一步生命值减 1，降到 0 饿死。
- 头撞墙、撞到任何一条蛇的身体（包括自己的）就死；尾巴每回合缩回，可以贴着走。
- 两个蛇头进了同一格，长的活、短的死，一样长一起死。
- 名次看谁活得久，都活到最后就比长度。
- 两种赛制各占一半权重：单挑（2 条蛇，15×15，最多 500 回合）和大乱斗（11 条蛇：10 个 AI 加陪练基准，31×31，最多 800 回合）。

## 比赛方式

- 每家只有一次写程序的机会，看不到裁判代码，不能试打。
- 交卷后裁判跑 12 局自检（对手全是陪练基准），只查报错、超时、返回值不对、进程卡死，不告诉胜负。出错时发统一模板的报告，最多 2 次修复机会。
- 回复被通道截断（输出额度用完、连接断开、正文为空）的那一次作废重跑，不扣修复机会；同一档思考强度装不下时降一档。
- 选手程序跑在独立进程里，用 macOS 沙箱禁止联网、写文件和启动子进程。每步限时按 CPU 时间算：加载 1 秒、第 1 回合 1 秒、之后每回合 50 毫秒。
- 实力值用 Bradley–Terry 拟合：每局按名次拆成两两比较，陪练基准 = 0 分，高 400 分 = 强 10 倍，95% 区间用重抽样。
- 8 家走 API 的选手，发题、收卷、自检、修复都由 `tools/contest.py` 自动跑。GPT 和 Claude 两家是在 Codex 和 Claude Code 里发同一份题（前面加一段 [`prompt/HARNESS_NOTE.md`](prompt/HARNESS_NOTE.md)），手工收卷，经过写在 [`docs/CONDITIONS.md`](docs/CONDITIONS.md) 里，这一步没有脚本。

参赛条件和比赛中的所有中断、事故见 [`docs/CONDITIONS.md`](docs/CONDITIONS.md)。每家写程序的真实用量和花费见 [`docs/LEDGER.md`](docs/LEDGER.md)。

## 自己跑

需要 Python 3.11 以上。比赛、自检和评分只用标准库，不用装包。

```bash
python -m arena.selfcheck bots/opus.py
```

```bash
python -m arena.tournament --rounds 2 --workers 8 --out my-games.jsonl.gz
```

```bash
python -m arena.analyze my-games.jsonl.gz --out my-results
```

写一个自己的 `bot.py`（接口见提示词），放进 `bots/`，把名字加进 `arena/tournament.py` 的 `ENTRANTS`，就能和这些 AI 打。沙箱用的是 macOS 的 `sandbox-exec`；在 Linux 上设 `ARENA_NO_SANDBOX=1` 跑（没有沙箱，只跑你信得过的代码）。

## 出片

片子也是代码做的。`video/make_ep1.py` 从比赛记录生成分镜和旁白稿 `video/ep1.json`，里面的数字全从 `results/` 和 `contest/` 读，不手填；`video/build.py` 把分镜变成一个 HyperFrames 项目，棋盘回放、字幕、音乐和音效都在里面，最后用 HyperFrames 渲染成 MP4。挑哪几局上片子是 `video/pick_games.py` 按 `results/picks.json` 里写的规则挑的，结果已经在仓库里，不用重跑。

要准备的东西：

- Python 包：`pip install -r requirements.txt`（numpy、Pillow、fontTools、brotli）
- Node.js 22 以上。渲染用 `npx` 自动下载的 HyperFrames 0.8.181，它会自己准备浏览器
- ffmpeg
- 正文字体 Noto Sans SC。它有 17 MB，按 OFL 授权，没放进仓库，下载到 `fonts/`：

```bash
curl -L -o fonts/NotoSansSC-VF.ttf "https://raw.githubusercontent.com/google/fonts/2894aab31764f10f29c421bdfd2340d3b382d384/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
```

不下也能出片，正文会先用像素字体顶上，只是和发布的那版字形不一样。

然后两条命令：

```bash
python video/make_ep1.py
```

```bash
python video/build.py video/ep1.json --out video/work/ep1 --render out/ep1.mp4
```

旁白是逐句调 Evolink 上的通义千问 TTS 合成的，要用你自己的 Evolink key：`export EVOLINK_API_KEY=你的key`，或者把 key 存进一个文件，用 `EVOLINK_API_KEY_FILE` 指过去。没有 key 就在第二条命令后面加 `--no-tts`，这样不调任何接口，按字数估每句多长，出一版只有音乐、音效和字幕的片子，用来看画面。配音按句缓存在 `video/cache/`，再跑不会重复花钱。

重新合成的配音每句长短和发布那版会差一点，画面时间轴是跟着配音走的，所以自己出的片子和发布版不会逐帧一样；比赛数据、分镜和画面代码是同一份。

不想等整集渲染，可以去掉 `--render`，到 `video/work/ep1` 里用 `npx --yes hyperframes@0.8.181 preview` 边拖边看，或者用 `snapshot --at 秒数` 截几帧。

角色图、头像和封面也都在仓库里。`tools/gen_cast.py` 用 GPT Image 画了两张五人草稿，存在 `cast/drafts/`（重画每次都不一样，所以后面从存下来的草稿开始）；`python tools/make_cast.py` 把草稿切开、压成像素形象，出来的 `cast/` 和仓库里的逐字节一致。`brand/make_baseline.py` 画陪练机器人，`brand/make_avatar.py` 画频道头像。封面上每个角色头顶有所属产品的标志，这些标志商标归各公司所有，不随仓库发布：先跑 `python brand/fetch_logos.py` 下载到 `brand/logos/`，再照 `brand/make_cover.py` 开头那条命令出图；不下载也能出，只是没有标志。

想换个游戏，可以把这个仓库交给 Claude Code 或 Codex，让它照着贪吃蛇的结构换成你想要的游戏：规则引擎、提示词、陪练、回放画法和分镜，再让你挑的几家 AI 来写程序。

## 目录

| 路径 | 内容 |
|---|---|
| `prompt/` | 发给选手的提示词原文，以及给两家工具选手（Codex、Claude Code）多加的那段条件说明 |
| `arena/` | 规则引擎、裁判、自检、正赛调度、评分、回放导出 |
| `bots/` | 10 个模型交上来的原样代码，和陪练基准 |
| `contest/` | 每家每次请求的原始回复、思考内容（接口返回了的）、用量、扣费、自检报告；`void/` 是作废的请求 |
| `results/` | 逐局记录（含每回合的走法，可以完整重放）、成绩、两两胜率、选手数据、片子里的精选对局 |
| `docs/` | 比赛条件与事故记录、花费账本 |
| `video/` | 视频的分镜生成和 HyperFrames 渲染（像素棋盘、旁白、字幕、芯片音乐） |
| `cast/` | 角色草稿（GPT Image）、切出来的单人图、像素形象 |
| `brand/` | 头像、陪练机器人和封面的生成脚本，封面标志的下载脚本 |
| `tools/` | API 选手的发题收卷脚本、实测单价和花费账本、角色草稿生成、切图和像素化 |
| `fonts/` | 缝合像素字体（OFL）；正文字体 Noto Sans SC 要另外下载 |

## 许可

代码按 MIT 许可开源。`fonts/` 里的缝合像素字体（Fusion Pixel Font）按 SIL Open Font License 1.1 授权，许可证在 `fonts/` 目录里。正文字体 Noto Sans SC 不在仓库里，下载后按 OFL 使用。角色立绘是用 GPT Image 画草稿再用代码压成像素的原创形象，不代表任何公司或模型的官方形象。选手代码是各家模型生成的，主办方没有修改。各家 AI 的名字和商标归各自公司所有，封面用到的产品标志不随仓库发布。

本项目和各家模型公司没有关系，也不是任何模型的官方账号。
