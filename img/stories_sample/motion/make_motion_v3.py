#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストーリーズ見本・動画版 v3（呼びかけ型のつかみ＋固定の見出しバー）
  1080x1920 / 30fps / H.264 + AAC / 9.6秒

使い方:  python3 make_motion_v3.py
出力先:  このフォルダ（*_v3.mp4）、se_v3/（音のwav）、../_check/motion_v3_frames_*.jpg

v2（make_motion_v2.py）からの変更:
  ダイエット・育毛・整体・肌質改善の広告動画でよく使われる「つかみ」の型を、地域の業者紹介に置き換えた。
    A 0.0〜 地名を叩きつけ → 赤い帯で「家を建てる人へ」（だれ向けかを最初の0.5秒で言う）
    B 0.8〜 黄色に反転「まず／ここ見て」＋注目マークと矢印。ここから上に見出しバーを固定
    C 1.6〜 特大の数字「3社」＋「最後に まとめあり」（最後まで見る理由）
    D 2.4〜 会社を1社ずつ。強みの中の数字は赤く大きく。拍ごとに画面が小さく寄る
    E       全社が並ぶまとめ画面 → 最後の約2秒は静止
  使わないと決めたもの: ビフォー・アフターの対比、「絶対」「No.1」「知らないと損」などの断定・あおり、
  驚いた顔など人の顔の素材（マークは図形で自作）。

素材の出どころ: v2 と同じ（フォント=Noto Sans CJK JP / SIL OFL 1.1、アイコン・マーク・音はすべて自作。
  写真・他社ロゴ・人物素材なし。会社名・電話番号は架空）
"""
import math
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_motion_v2 as v2  # noqa: E402

v1, ms = v2.v1, v2.ms
W, H, S, FPS, SR, BEAT, DUR = v2.W, v2.H, v2.S, v2.FPS, v2.SR, v2.BEAT, v2.DUR
tsprite, shape, blit, fit, slam, sunburst, mix_col = v2.tsprite, v2.shape, v2.blit, v2.fit, v2.slam, v2.sunburst, v2.mix_col
back_out, clamp = v2.back_out, v2.clamp
RED = (222, 48, 40)
RED_D = (150, 24, 20)
BAR_Y, BAR_H = 340, 124          # 固定の見出しバー（PR表記のすぐ下。上250pxより下）


def hstack(parts, gap=0):
    """スプライトを下ぞろえで横に並べる"""
    w = sum(p.width for p in parts) + gap * (len(parts) - 1)
    h = max(p.height for p in parts)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        out.alpha_composite(p, (x, h - p.height))
        x += p.width + gap
    return out


def strong_sprite(text, t, w):
    """強みの1行。数字（50年・30台など）だけ赤く大きくする"""
    parts = [p for p in re.split(r"(\d+[^\d。、・\s]?)", text) if p]
    size = 70
    while size > 40:
        tot = sum(ms.font(size * (1.38 if p[0].isdigit() else 1)).getlength(p) / S for p in parts)
        if tot <= w - 80:
            break
        size -= 2
    row = hstack([tsprite(p, size * 1.38, RED, stroke=1.5) if p[0].isdigit() else tsprite(p, size, t["dark"])
                  for p in parts])
    hh = 150
    box = shape(w, hh, lambda d: d.rounded_rectangle(ms.P(0, 0, w, hh), radius=int(24 * S), fill=ms.WHITE,
                                                     outline=t["main"], width=int(5 * S)))
    box.alpha_composite(row, (int((w - row.width) / 2), int((hh - row.height) / 2) - 2))
    return box


def prepare(spec):
    M = v2.prepare(spec)
    t = M["t"]
    WH, YEL, INK = ms.WHITE, ms.YELLOW, ms.INK
    area, hook = spec["area"], spec["line2"]
    n = len(area)
    # A: 地名（少し小さくして、下に赤い帯を置く）
    if n <= 3:
        size = min(500, int(1000 / n))
        pos = [(440, 350 + size * .97 * (i + .5)) for i in range(n)]
        de = (440 + size / 2 + 120, pos[-1][1] + size * .2, 220)
        bottom = 350 + size * .97 * n
        lands = [.067 + .133 * i for i in range(n)]
    else:
        size = 420
        pos = [(270 + 420 * (i % 2), 400 + 205 + 410 * (i // 2)) for i in range(n)]
        de = (978, pos[-1][1] + 120, 150)
        bottom = 400 + 820
        lands = [.067 + .067 * i for i in range(n)]
    hs = fit(hook, 900, 132, 3)
    bh = hs * 1.55

    def f_band(d):
        d.rectangle(ms.P(0, 12, W + 120, bh + 12), fill=RED_D)
        d.rectangle(ms.P(0, 0, W + 120, bh), fill=RED)
        d.rectangle(ms.P(0, 8, W + 120, 16), fill=YEL)
        d.rectangle(ms.P(0, bh - 16, W + 120, bh - 8), fill=YEL)
        ms.draw_text(d, ((W + 120) / 2, bh * .47), hook, ms.font(hs), WH, stroke=3, anchor="mm")
    M["A"] = dict(
        chars=[tsprite(c, size, YEL, stroke=6, shadow=t["dark"], off=14) for c in area], pos=pos, lands=lands,
        de=tsprite(spec["particle"], de[2], WH, stroke=4, shadow=t["dark"], off=9), de_pos=de[:2],
        de_land=lands[-1] + .1, band=shape(W + 120, bh + 12, f_band), band_y=min(1440, bottom + 150),
        band_land=.467)
    # 固定の見出しバー: 「北薩で家を建てる人へ」
    a_txt = area + spec["particle"]
    sz = 86
    while sz > 40 and ms.font(sz).getlength(a_txt + hook) / S > W - 90:
        sz -= 2
    row = hstack([tsprite(a_txt, sz, YEL, stroke=1.5), tsprite(hook, sz, WH, stroke=1.5)], gap=4)
    bar = shape(W, BAR_H + 10, lambda d: (d.rectangle(ms.P(0, 8, W, BAR_H + 10), fill=RED_D),
                                          d.rectangle(ms.P(0, 0, W, BAR_H), fill=RED)))
    bar.alpha_composite(row, (int((W - row.width) / 2), int((BAR_H - row.height) / 2) - 2))
    M["bar"] = bar
    # B: 注目マークと矢印（図形で自作）
    def f_mark(d):
        d.ellipse(ms.P(8, 10, 208, 210), fill=RED_D)
        d.ellipse(ms.P(0, 0, 200, 200), fill=RED)
        ms.draw_text(d, (100, 94), "!", ms.font(160), WH, stroke=4, anchor="mm")
    M["mark"] = shape(210, 212, f_mark)
    M["arrow"] = shape(150, 90, lambda d: d.polygon([ms.P(0, 0), ms.P(150, 0), ms.P(75, 90)], fill=RED))
    # C: 「最後に まとめあり」
    ft = "最後に まとめあり"

    def f_last(d):
        d.rounded_rectangle(ms.P(0, 0, 760, 118), radius=int(59 * S), fill=YEL)
        ms.draw_text(d, (380, 55), ft, ms.font(66), INK, anchor="mm")
    M["last"] = shape(760, 118, f_last)
    # D: 強みの数字を目立たせる
    for E, (_, strong, _) in zip(M["D"], spec["companies"]):
        E["strong"] = strong_sprite(strong, t, W - 120)
    return M


# ---------- 画面ごとの絵 ----------
def scene_A(M, u):
    t, A = M["t"], M["A"]
    fr = sunburst(t["main"], mix_col(t["main"], t["dark"], .22), u * 25)
    for im, (x, y), ld in zip(A["chars"], A["pos"], A["lands"]):
        r = slam(u - ld)
        if r:
            blit(fr, im, x, y, sx=r[0], sy=r[1], alpha=r[2])
    r = slam(u - A["de_land"], big=2.0)
    if r:
        blit(fr, A["de"], *A["de_pos"], sx=r[0], sy=r[1], alpha=r[2], angle=-6)
    r = slam(u - A["band_land"], big=2.2)
    if r:
        blit(fr, A["band"], W / 2, A["band_y"], sx=r[0], sy=r[1], alpha=r[2], angle=-4)
    return fr


def scene_B(M, u):
    B = M["B"]
    off = 20
    fr = sunburst(ms.YELLOW, (255, 208, 30), -u * 25 + 9, cy=H * .52)
    blit(fr, B["l1"], W / 2 - 40, B["y1"] + off)
    p = (u - .2) / .2
    if p > 0:
        blit(fr, M["mark"], min(955, W / 2 + B["l1"].width / 2 - 20), B["y1"] + off - B["l1"].height * .3,
             s=.2 + .8 * back_out(p, 3.2), angle=14 - 30 * (1 - clamp(p)) ** 2)
    r = slam(u - .4, big=2.6)
    if r:
        blit(fr, B["l2"], W / 2, B["y2"] + off, sx=r[0], sy=r[1], alpha=r[2], angle=-3)
    if u > .45:                                               # 下を指す矢印がトントンと弾む
        v = (u - .45) % .2 / .2
        blit(fr, M["arrow"], W / 2, B["y2"] + off + B["l2"].height / 2 + 72 + 24 * abs(math.sin(v * math.pi)))
    return fr


def scene_C(M, u):
    t, C = M["t"], M["C"]
    bg = mix_col(t["dark"], (0, 0, 0), .25)
    fr = sunburst(bg, mix_col(bg, t["main"], .28), u * 25 + 4, cy=1060)
    blit(fr, C["label"], W / 2 - 700 * (1 - clamp(u / .13)) ** 2, 590)
    r = slam(u - .4, big=3.2)
    if r:
        blit(fr, C["count"], W / 2 + 10, 1010, sx=r[0] * .92, sy=r[1] * .92, alpha=r[2])
    p = (u - .55) / .2
    if p > 0:
        blit(fr, M["last"], W / 2, 1475, s=.3 + .7 * back_out(p, 3), angle=-3)
    return fr


def scene_D(M, i, u, d_len):
    t, E, n = M["t"], M["D"][i], M["n"]
    bg = ms.CREAM if i % 2 == 0 else t["pale"]
    fr = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(fr)
    d.rectangle((0, 0, W, BAR_Y + 10), fill=t["main"])
    # 何社目かの目盛り（ストーリーズの進み具合のように伸びる）
    seg = (W - 120 - 16 * (n - 1)) / n
    for k in range(n):
        x0 = 60 + k * (seg + 16)
        d.rounded_rectangle((x0, 500, x0 + seg, 516), radius=8, fill=mix_col(bg, t["dark"], .22))
        f = 1 if k < i else (clamp(u / d_len) if k == i else 0)
        if f > 0:
            d.rounded_rectangle((x0, 500, x0 + max(16, seg * f), 516), radius=8, fill=t["main"])
    y0 = 185
    p = u / .22
    blit(fr, E["badge"], 176, 470 + y0, s=.2 + .8 * back_out(p, 3.2), angle=40 * (1 - clamp(p)) ** 2)
    blit(fr, E["prog"], 320 + 500 * (1 - clamp(u / .15)) ** 2, 470 + y0, anchor=(0, .5))
    q = clamp(u / .17)
    blit(fr, E["name"], 60 + 1000 * (1 - q) ** 2.2, 745 + y0, anchor=(0, .5), sx=1 + .12 * (1 - q))
    q2 = clamp((u - .12) / .16)
    blit(fr, E["strong"], W / 2, 965 + y0 + 60 * (1 - q2) ** 2, alpha=q2)
    r = slam(u - .4, dur=.07, big=1.9)
    if r:
        blit(fr, E["tel"], W / 2 + 4, 1200 + y0, sx=r[0], sy=r[1], alpha=r[2])
    if u < .134:
        x = -500 + 2100 * (u / .134)
        ImageDraw.Draw(fr).polygon([(x, 0), (x + 420, 0), (x + 200, H), (x - 220, H)], fill=t["main"])
    return fr


def render(M, T, tm):
    n, A = M["n"], M["A"]
    if tm >= T["static"]:
        return M["final"]
    hits = [(ld, .8) for ld in A["lands"]] + [(A["de_land"], .4), (A["band_land"], 1.25),
                                              (T["B"] + .4, .9), (T["C"] + .4, 1.2)]
    punches = [(T["B"], .16, True), (T["C"], .1, True), (T["E"], .14, True)]
    for i in range(n):
        hits.append((T["D0"] + i * T["d_len"] + .4, .45))
        punches.append((T["D0"] + i * T["d_len"], .06, True))
    b = 1                                                     # 拍ごとに小さく寄る（0.4秒ごと）
    while T["B"] + b * BEAT < T["E"] - 1e-6:
        punches.append((T["B"] + b * BEAT, .03, False))
        b += 1

    bar = False
    if tm < T["B"]:
        u, key = tm, "color"
        fr = scene_A(M, u)
        creep = .05 * max(0, u - .5) / .3
    elif tm < T["C"]:
        u, key, bar = tm - T["B"], "yellow", True
        fr = scene_B(M, u)
        creep = .05 * u / .8
    elif tm < T["D0"]:
        u, key, bar = tm - T["C"], "color", True
        fr = scene_C(M, u)
        creep = .05 * u / .8
    elif tm < T["E"]:
        i = int((tm - T["D0"]) / T["d_len"] + 1e-6)
        u, key, bar = tm - T["D0"] - i * T["d_len"], "card", True
        fr = scene_D(M, i, u, T["d_len"])
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
    if bar:                                                   # 見出しバーは揺らさず固定（Bの頭で上から下りる）
        p = clamp((tm - T["B"]) / .1)
        fr.paste(M["bar"], (0, round(BAR_Y - 260 * (1 - p) ** 2)), M["bar"])
    if key:
        v2.overlay(fr, M, key)
    return fr


def make_video(out_name, check_name, spec):
    M = prepare(spec)
    T = v2.timeline(M["n"])
    out = os.path.join(HERE, out_name)
    wav = os.path.join(HERE, "se_v3", out_name.replace(".mp4", "_mix.wav"))
    # 音は v2 と同じ自作の合成。叩く位置だけ v3 の動きに合わせる（最後の一発＝赤い帯）
    Ma = dict(M, A=dict(M["A"], lands=M["A"]["lands"] + [M["A"]["band_land"]]))
    v2.make_audio(Ma, T, wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", str(DUR), "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(round(DUR * FPS))):
        pr.stdin.write(render(M, T, k / FPS + 1e-6).tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("saved", out, {k: round(v, 2) for k, v in T.items()})
    stamps = [.1, .3, .6, 1.0, 1.4, 2.2, T["D0"] + .9, T["D0"] + T["d_len"] + .9, T["E"] + .7, DUR - 1 / FPS]
    v2.check_sheet(out, check_name, stamps)


SPECS = [
    ("01_hokusatsu_koumuten_v3.mp4", "motion_v3_frames_01_hokusatsu.jpg", dict(
        kind="house", edition="マイタウンガイド 北薩版", area="北薩", particle="で",
        line2="家を建てる人へ", line2_split=("まず", "ここ見て"), count_label="おすすめ工務店",
        pill="おすすめ工務店・建築会社　3社", companies=ms.HOUSE,
        footer="マイタウンガイド2026（北薩版）に掲載中")),
    ("02_amami_kuruma_v3.mp4", "motion_v3_frames_02_amami.jpg", dict(
        kind="car", edition="マイタウンガイド 奄美大島版", area="奄美大島", particle="で",
        line2="車検に迷ってる人へ", line2_split=("まず", "ここ見て"), count_label="たよれる車屋さん",
        pill="車検・修理・中古車　おすすめ2社", companies=ms.CAR,
        footer="マイタウンガイド2026（奄美大島版）に掲載中")),
]

if __name__ == "__main__":
    for out_name, check_name, spec in SPECS:
        make_video(out_name, check_name, spec)
