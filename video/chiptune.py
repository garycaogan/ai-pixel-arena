"""芯片音乐和音效合成。取自 pixel-diary（https://github.com/garycaogan/pixel-diary，MIT）的 audio.py，
只删掉了这里用不到的 plan 依赖。原说明：Typing blips, UI sounds and an 8-bit music bed, all synthesised from the same timeline as the text."""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


SR = 44100


def tone(freq, dur, duty=0.5, kind="pulse"):
    n = int(SR * dur)
    ph = (np.arange(n) * freq / SR) % 1.0
    if kind == "tri":
        return 4 * np.abs(ph - 0.5) - 1
    if kind == "sine":
        return np.sin(2 * np.pi * ph)
    return np.where(ph < duty, 1.0, -1.0)


def env(n, attack=0.003, decay_to=0.0, curve=4.0):
    e = np.ones(n)
    a = max(1, int(SR * attack))
    e[:a] = np.linspace(0, 1, a)
    e[a:] = decay_to + (1 - decay_to) * np.exp(-curve * np.linspace(0, 1, n - a))
    return e


def lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def noise(dur, seed):
    return np.random.default_rng(seed).uniform(-1, 1, int(SR * dur))


def add(buf, t, sig, vol):
    i = int(t * SR)
    j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf):
        buf[i:j] += sig[: j - i] * vol


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ sound effects
def _pop(buf, t, hi=False):
    for k, m in enumerate((91, 96) if hi else (84, 91)):
        s = tone(note(m), 0.05, duty=0.25)
        add(buf, t + k * 0.05, s * env(len(s), 0.002, 0, 4), 0.07)


def _thud(buf, t):
    n = noise(0.14, 7)
    add(buf, t, lowpass(n, 0.18) * env(len(n), 0.001, 0, 6), 0.32)
    s = tone(70, 0.28, kind="sine") * env(int(SR * 0.28), 0.001, 0, 5)
    add(buf, t, s, 0.4)


def _sweep(buf, t, dur):
    steps = max(1, int(dur / 0.0625))
    for k in range(steps):
        s = tone(note(60 + (k * 5) % 36), 0.03, duty=0.125)
        add(buf, t + k * 0.0625, s * env(len(s), 0.001, 0, 5), 0.05)


def _click(buf, t, seed):
    n = noise(0.018, seed)
    add(buf, t, n * env(len(n), 0.001, 0, 8), 0.12)


def _jingle(buf, t):
    for k, m in enumerate((84, 88, 91, 96)):
        s = tone(note(m), 0.12, duty=0.5)
        add(buf, t + k * 0.1, s * env(len(s), 0.002, 0.2, 3), 0.08)


def sfx_track(plan: dict, events: list[tuple], cast: dict) -> np.ndarray:
    buf = np.zeros(int(SR * (plan["duration"] + 1)))
    silent = LANG[plan["lang"]]["silent"]
    wobble = [1.0, 1.06, 0.97, 1.03, 0.94, 1.08]
    for ln in plan["lines"]:
        base = float((cast.get(ln["who"]) or {}).get("blip", 520))
        last = -1.0
        for k, (ch, t) in enumerate(zip(ln["text"], ln["times"])):
            if ch in silent or t - last < 0.05:  # English types fast: keep at most ~20 blips a second
                continue
            last = t
            f = base * wobble[k % len(wobble)]
            s = 0.75 * tone(f, 0.03, kind="tri") + 0.25 * tone(f, 0.03, duty=0.25)
            add(buf, t, s * env(len(s), 0.002, 0, 6), 0.05)
    for ev in events:
        kind, t = ev[0], ev[1]
        if kind == "pop":
            _pop(buf, t)
        elif kind == "ping":
            _pop(buf, t, hi=True)
        elif kind == "thud":
            _thud(buf, t)
        elif kind == "sweep":
            _sweep(buf, t, ev[2])
        elif kind == "click":
            _click(buf, t, int(t * 1000))
        elif kind == "jingle":
            _jingle(buf, t)
    return buf


# ------------------------------------------------------------------ music bed
MOODS = {
    # bpm, chord roots/triads, lead volume, swing of the melody
    "cheerful": {"bpm": 112, "shift": 0},
    "cozy": {"bpm": 92, "shift": -3},
    "brisk": {"bpm": 128, "shift": 2},
}
CHORDS = [(48, (60, 64, 67)), (43, (59, 62, 67)), (45, (57, 60, 64)), (41, (57, 60, 65))]
MELODY = [
    [(76, 2), (79, 2), (84, 2), (79, 1), (76, 1)],
    [(74, 2), (79, 2), (83, 2), (79, 1), (74, 1)],
    [(72, 2), (76, 2), (81, 2), (79, 1), (76, 1)],
    [(77, 2), (76, 2), (74, 2), (72, 2)],
    [(76, 1), (79, 1), (84, 1), (86, 1), (84, 2), (79, 2)],
    [(83, 2), (81, 2), (79, 2), (74, 2)],
    [(76, 2), (79, 1), (81, 1), (79, 2), (76, 2)],
    [(77, 2), (76, 2), (74, 2), (None, 2)],
]


def bgm_track(duration: float, mood: str = "cheerful", duck: list | None = None) -> np.ndarray:
    cfg = MOODS.get(mood, MOODS["cheerful"])
    beat = 60 / cfg["bpm"]
    e8 = beat / 2
    sh = cfg["shift"]
    total = duration + 1
    n = int(SR * total)
    lead, bass, arp, drums = (np.zeros(n) for _ in range(4))
    bar, t0 = 0, 0.0
    soft = mood == "cozy"
    while t0 < total:
        root, triad = CHORDS[bar % 4]
        t = t0
        for m, ln in MELODY[bar % 8]:
            if m is not None:
                f = note(m - 12 + sh)
                s = 0.6 * tone(f, ln * e8 * 0.92, duty=0.5) + 0.4 * tone(f, ln * e8 * 0.92, kind="tri")
                add(lead, t, s * env(len(s), 0.004, 0.35, 3), 1.0)
            t += ln * e8
        for k in range(8):
            m = root + sh if k % 2 == 0 else root + 12 + sh
            s = tone(note(m), e8 * 0.9, kind="tri")
            add(bass, t0 + k * e8, s * env(len(s), 0.003, 0.5, 2), 1.0)
        tones = [x + sh for x in triad] + [triad[0] + 12 + sh]
        for k in range(16):
            s = tone(note(tones[k % 4] + 12), e8 / 2 * 0.8, duty=0.125)
            add(arp, t0 + k * e8 / 2, s * env(len(s), 0.002, 0, 4), 1.0)
        for b in range(4):
            tb = t0 + b * beat
            if b in (0, 2):
                m = int(SR * 0.13)
                f = np.linspace(150, 45, m)
                add(drums, tb, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, 0.001, 0, 5), 0.6 if soft else 0.9)
            elif not soft:
                sn = noise(0.09, bar * 4 + b)
                add(drums, tb, lowpass(sn, 0.5) * env(len(sn), 0.001, 0, 6), 0.25)
            hat = noise(0.02, 1000 + bar * 4 + b)
            hat = hat - lowpass(hat, 0.3)
            add(drums, tb + e8, hat * env(len(hat), 0.001, 0, 6), 0.06 if soft else 0.1)
        t0 += 4 * beat
        bar += 1
    lead = lowpass(lead, 0.16 if soft else 0.2)
    mix = lead * 0.1 + bass * 0.12 + lowpass(arp, 0.3) * 0.014 + drums * 0.13
    fade, end = int(SR * 2.0), int(SR * duration)
    mix[max(0, end - fade):end] *= np.linspace(1, 0, min(fade, end))
    mix[end:] = 0
    mix[: int(SR * 0.3)] *= np.linspace(0, 1, int(SR * 0.3))
    for a, b in duck or []:  # a clip with its own sound: music down to 15 % with short fades
        env_ = np.ones(len(mix))
        i0, i1, f = int(SR * a), int(SR * b), int(SR * 0.3)
        env_[i0:i1] = 0.15
        env_[max(0, i0 - f):i0] = np.linspace(1, 0.15, i0 - max(0, i0 - f))
        env_[i1:i1 + f] = np.linspace(0.15, 1, len(env_[i1:i1 + f]))
        mix *= env_
    return mix


def write_wav(path: Path, x: np.ndarray) -> None:
    peak = np.abs(x).max() if len(x) else 0
    if peak > 0.95:
        x = x * 0.95 / peak
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
