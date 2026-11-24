#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストーリーズ見本・動画版 v4（v3の冒頭をゆっくり読めるようにした版）
  1080x1920 / 30fps / H.264 + AAC / 3社版 12.8秒・2社版 10.8秒

使い方:  python3 make_motion_v4.py
出力先:  このフォルダ（*_v4.mp4）、se_v4/（音のwav）、../_check/motion_v4_frames_*.jpg

v3（make_motion_v3.py）からの変更は時間の配分だけ（絵・言葉・音色は同じ）。1拍=0.4秒。
    A 0.0〜2.0  地名を叩きつけ（勢いはそのまま）→ 0.47秒で赤い帯 → そのまま約1.5秒止めて読ませる
    B 2.0〜3.2  「まず」→ 0.2秒後に「ここ見て」→ 約1秒見せる
    C 3.2〜4.4  「3社」＋「最後に まとめあり」
    D 4.4〜     会社を1社ずつ、各1.6秒
    E           まとめ画面 → 最後の2秒は静止
  ビートは赤い帯のあと（0.8秒）から入れて、長くなった冒頭が無音にならないようにした。

素材の出どころ: v3 と同じ（フォント=Noto Sans CJK JP / SIL OFL 1.1、アイコン・マーク・音はすべて自作。
  写真・他社ロゴ・人物素材なし。会社名・電話番号は架空）
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_motion_v3 as v3  # noqa: E402

v2, v1, ms = v3.v2, v3.v1, v3.ms
W, H, FPS, SR, BEAT = v3.W, v3.H, v3.FPS, v3.SR, v3.BEAT
blit, slam, sunburst, back_out, clamp = v3.blit, v3.slam, v3.sunburst, v3.back_out, v3.clamp
BEAT0 = 0.8               # ビートが入る時刻
B_L2 = 0.2                # B の中で「ここ見て」が着地する時刻


def timeline(n):
    T = dict(A=0.0, B=2.0, C=3.2, D0=4.4, d_len=1.6)
    T["E"] = T["D0"] + T["d_len"] * n
    T["cta"] = T["E"] + .4
    T["static"] = T["cta"] + 1.2
    T["dur"] = T["static"] + 2.0
    return T


def scene_B(M, u):
    B = M["B"]
    off = 20
    fr = sunburst(ms.YELLOW, (255, 208, 30), -u * 25 + 9, cy=H * .52)
    blit(fr, B["l1"], W / 2 - 40, B["y1"] + off)
    p = (u - .3) / .2
    if p > 0:
        blit(fr, M["mark"], min(955, W / 2 + B["l1"].width / 2 - 20), B["y1"] + off - B["l1"].height * .3,
             s=.2 + .8 * back_out(p, 3.2), angle=14 - 30 * (1 - clamp(p)) ** 2)
    r = slam(u - B_L2, big=2.6)
    if r:
        blit(fr, B["l2"], W / 2, B["y2"] + off, sx=r[0], sy=r[1], alpha=r[2], angle=-3)
    if u > B_L2 + .1:
        v = (u - B_L2 - .1) % .2 / .2
        blit(fr, M["arrow"], W / 2, B["y2"] + off + B["l2"].height / 2 + 72 + 24 * abs(math.sin(v * math.pi)))
    return fr


def render(M, T, tm):
    n, A = M["n"], M["A"]
    if tm >= T["static"]:
        return M["final"]
    hits = [(ld, .8) for ld in A["lands"]] + [(A["de_land"], .4), (A["band_land"], 1.25),
                                              (T["B"] + B_L2, .9), (T["C"] + .4, 1.2)]
    punches = [(T["B"], .16, True), (T["C"], .1, True), (T["E"], .14, True)]
    for i in range(n):
        hits.append((T["D0"] + i * T["d_len"] + .4, .45))
        punches.append((T["D0"] + i * T["d_len"], .06, True))
    b = 0                                                     # 拍ごとに小さく寄る
    while BEAT0 + b * BEAT < T["E"] - 1e-6:
        punches.append((BEAT0 + b * BEAT, .03, False))
        b += 1

    bar = False
    if tm < T["B"]:
        u, key = tm, "color"
        fr = v3.scene_A(M, u)
        creep = .06 * max(0, u - .5) / (T["B"] - .5)          # 止めている間もゆっくり寄り続ける
    elif tm < T["C"]:
        u, key, bar = tm - T["B"], "yellow", True
        fr = scene_B(M, u)
        creep = .05 * u / (T["C"] - T["B"])
    elif tm < T["D0"]:
        u, key, bar = tm - T["C"], "color", True
        fr = v3.scene_C(M, u)
        creep = .05 * u / (T["D0"] - T["C"])
    elif tm < T["E"]:
        i = int((tm - T["D0"]) / T["d_len"] + 1e-6)
        u, key, bar = tm - T["D0"] - i * T["d_len"], "card", True
        fr = v3.scene_D(M, i, u, T["d_len"])
        creep = 0
    else:
        u, key = tm - T["E"], None
        fr = v2.scene_E(M, u, T).copy()
        creep = 0

    z, dx, dy, flash = 1 + creep, 0.0, 0.0, 0.0
    for (t0, amp) in hits:
        v = tm - t0
        if 0 <= v < .3:
            env = math.exp(-v * 12) * amp
            z += .045 * env
            dx += 16 * env * math.sin(v * 2 * math.pi * 17)
            dy += 34 * env * math.cos(v * 2 * math.pi * 13)
            flash = max(flash, .2 * amp * max(0, 1 - v / .07))
    for (t0, amt, fl) in punches:
        v = tm - t0
        if 0 <= v < .17:
            z += amt * (1 - v / .17) ** 2
            if fl:
                flash = max(flash, amt * 3 * max(0, 1 - v / .07))
    fr = v2.camera(fr, z, dx, dy)
    if flash > 0.01:
        fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), min(.45, flash))
    if bar:
        p = clamp((tm - T["B"]) / .1)
        fr.paste(M["bar"], (0, round(v3.BAR_Y - 260 * (1 - p) ** 2)), M["bar"])
    if key:
        v2.overlay(fr, M, key)
    return fr


def make_audio(M, T, wav_path):
    """音色は v2/v3 と同じ自作の合成。並べ方だけ v4 の時間に合わせる"""
    n, A = M["n"], M["A"]
    N = int(SR * T["dur"])
    mix = np.zeros(N)
    saved = {}

    def add(name, x, at, gain):
        x = x / (np.max(np.abs(x)) + 1e-9)
        saved.setdefault(name, x)
        i = int(round(at * SR))
        if i >= N:
            return
        j = min(N, i + len(x))
        mix[i:j] += x[: j - i] * gain

    boom, kick, clap, hat = v2.a_boom(), v2.a_kick(), v2.a_clap(), v2.a_hat()
    whoosh = v1.se_whoosh(.16, 600, 5000, 7)
    for ld in A["lands"]:
        add("boom", boom, ld, .8)
    add("clap", clap, A["de_land"], .5)
    add("boom", boom, A["band_land"], 1.0)
    # ビート: 冒頭を止めている間（0.8〜2.0秒）はキックとベースだけで静かに、B から全部入り
    roots = [110.0, 110.0, 87.31, 98.0]
    chords = [(220, 261.63, 329.63), (220, 261.63, 329.63), (174.61, 220, 261.63), (196, 246.94, 293.66)]
    b = 0
    while BEAT0 + b * BEAT < T["E"] - 1e-6:
        at = BEAT0 + b * BEAT
        full = at >= T["B"] - 1e-6
        bar = (b // 4) % 4
        add("kick", kick, at, .8 if full else .6)
        add("bass", v2.a_bass(roots[bar]), at + BEAT / 2, .5 if full else .4)
        if full:
            add("hat", hat, at + BEAT / 2, .2)
            if b % 2 == 0:
                add("clap", clap, at + BEAT, .4)
            add("bass", v2.a_bass(roots[bar] * 2, .1), at + BEAT * .75, .22)
        b += 1
    add("riser", v2.a_riser(.3), T["B"] - .3, .5)
    add("boom", boom, T["B"], 1.0)
    add("boom", boom, T["B"] + B_L2, .75)
    add("riser", v2.a_riser(.2), T["C"] + .2, .35)
    add("boom", boom, T["C"] + .4, 1.0)
    cuts = [T["C"]] + [T["D0"] + i * T["d_len"] for i in range(n)]
    for c in cuts:
        bar = int(round((c - BEAT0) / BEAT)) // 4 % 4
        add("whoosh", whoosh, c - .14, .3)
        add("stab", v2.a_stab(chords[bar]), c, .32)
    for i in range(n):
        add("pon", v1.se_pon([659.25, 783.99, 880.0, 1046.5][i], .22), T["D0"] + i * T["d_len"] + .4, .32)
    add("riser", v2.a_riser(.3), T["E"] - .3, .5)
    add("boom", boom, T["E"], 1.0)
    add("stab_end", v2.a_stab((261.63, 329.63, 392.0, 523.25), 1.4), T["E"], .4)
    add("pyoko", v1.se_pyoko(), T["cta"], .3)
    add("kiran", v1.se_kiran(), T["cta"] + .2, .34)

    mix = np.tanh(mix * 1.15)
    mix = mix / np.max(np.abs(mix)) * 0.40
    fade = int(SR * .05)
    mix[-fade:] *= np.linspace(1, 0, fade)

    def write(path, x, g=1.0):
        pcm = (np.clip(x * g, -1, 1) * 32767).astype("<i2")
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())

    os.makedirs(os.path.dirname(wav_path), exist_ok=True)
    write(wav_path, mix)
    for k, x in saved.items():
        write(os.path.join(os.path.dirname(wav_path), k + ".wav"), x, .5)


def make_video(out_name, check_name, spec):
    M = v3.prepare(spec)
    T = timeline(M["n"])
    dur = T["dur"]
    out = os.path.join(HERE, out_name)
    wav = os.path.join(HERE, "se_v4", out_name.replace(".mp4", "_mix.wav"))
    make_audio(M, T, wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", str(dur), "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(dur * FPS))
    for k in range(nf):
        pr.stdin.write(render(M, T, k / FPS + 1e-6).tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("saved", out, {k: round(v, 2) for k, v in T.items()},
          "帯の着地", M["A"]["band_land"], "→ 止めて見せる", round(T["B"] - M["A"]["band_land"], 2), "秒")
    stamps = [.1, .3, .6, 1.9, T["B"] + .1, T["B"] + 1.1, T["C"] + 1.0, T["D0"] + 1.2,
              T["E"] + .7, (nf - 1) / FPS]
    v2.check_sheet(out, check_name, stamps)


if __name__ == "__main__":
    for out_name, check_name, spec in v3.SPECS:
        make_video(out_name.replace("_v3", "_v4"), check_name.replace("_v3_", "_v4_"), spec)
