"""选手资料：名字、简称、颜色、接入方式。颜色和棋盘上的蛇一致。"""

ORDER = ["opus", "astra", "gemini", "deepseek", "kimi", "doubao", "qwen", "glm", "minimax", "grok"]

CAST = {
    "opus": {"name": "Claude Opus 5.5", "short": "Claude", "color": "#FF9838", "channel": "本机 Claude Code"},
    "astra": {"name": "GPT-6 Astra", "short": "GPT", "color": "#1FC77E", "channel": "Codex（Mac Pro）"},
    "gemini": {"name": "Gemini 4 Argon", "short": "Gemini", "color": "#A57BFF", "channel": "Evolink API"},
    "deepseek": {"name": "DeepSeek V4.1 Flash", "short": "DeepSeek", "color": "#4567FF", "channel": "Evolink API"},
    "kimi": {"name": "Kimi K3", "short": "Kimi", "color": "#F2F2F2", "channel": "Evolink API"},
    "doubao": {"name": "豆包 Seed 2.0 Pro", "short": "豆包", "color": "#2FD3E6", "channel": "Evolink API"},
    "qwen": {"name": "Qwen 3.8 Max", "short": "千问", "color": "#F05BC9", "channel": "Evolink API"},
    "glm": {"name": "GLM 5.3", "short": "GLM", "color": "#FFDD3C", "channel": "Evolink API"},
    "minimax": {"name": "MiniMax M3.1 Flash", "short": "MiniMax", "color": "#FF4B4B", "channel": "Evolink API"},
    "grok": {"name": "Grok 4.7", "short": "Grok", "color": "#9BE23A", "channel": "Evolink API"},
    "baseline": {"name": "陪练基准", "short": "基准", "color": "#7D838F", "channel": "主办方写的"},
}

# 旁白里英文名的读法（只影响配音，字幕照原样）
SAY_AS = [
    ("Claude Opus 5.5", "克劳德 Opus 五点五"), ("GPT-6 Astra", "GPT 六 Astra"), ("Gemini 4 Argon", "Gemini 四 Argon"),
    ("DeepSeek V4.1 Flash", "DeepSeek V 四点一 Flash"), ("Kimi K3", "Kimi K 三"), ("Seed 2.0 Pro", "Seed 二点零 Pro"),
    ("Qwen 3.8 Max", "千问三点八 Max"), ("GLM 5.3", "GLM 五点三"), ("MiniMax M3.1 Flash", "MiniMax M 三点一 Flash"),
    ("Grok 4.7", "Grok 四点七"), ("Claude", "克劳德"),
]
