# -*- coding: utf-8 -*-
"""声の聞き比べ動画を作る（台本の冒頭 約15秒 × 4つの声 ＋ 4本をつなげた1本）。

使い方（VOICEVOX ENGINE を先に起動。../2026-11-20_第1回/turtle_video.py の説明を参照）：
  python3 make_voice_compare.py
出力：同じフォルダに voice_A_〜D_*.mp4 と voice_compare_all.mp4
"""
import os, subprocess, sys
from PIL import Image, ImageDraw
OUTDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(OUTDIR, "..", "2026-11-20_第1回"))
from turtle_video import *          # noqa
from make_vol1 import LINES, PW, PH, canvas, card, pill

# 候補：(記号, 声の名前, ファイル名, 速さ, 高さ, 抑揚)。聞き取りやすさで少しずつ調整
VOICES = [
    ("A", "ナースロボ＿タイプＴ", "nurserobo", 1.10, 0.00, 1.15),
    ("B", "雀松朱司", "akashi", 1.10, 0.00, 1.25),
    ("C", "ちび式じい", "chibijii", 1.15, 0.00, 1.10),
    ("D", "春日部つむぎ", "tsumugi", 1.15, 0.00, 1.10),
]
# 冒頭4文：あいさつ → 3つ紹介 → ひとつめ（アンソロピック・クロード フェイブル5.2）→ 最大3割
CLIP = [Line(l.chunks, head=None, body="cand", gap=l.gap) for l in LINES[:4]]


def cand_layer(mark, voice, speed, pitch, inton):
    im = canvas(); d = ImageDraw.Draw(im)
    card(d, (50, 0, PW - 50, PH - 4), outline=YELLOW, width=5)
    d.text((PW/2, 80), f"声の候補{mark}", font=fB(72), fill=YELLOW, anchor="mm")
    text_fit(d, (PW/2, 225), voice, 104, PW - 160, fill=WHITE, anchor="mm", stroke_width=2, stroke_fill=INK)
    d.text((PW/2, 345), "VOICEVOX（無料・クレジット表記で商用可）", font=fB(34), fill=DIM, anchor="mm")
    d.text((PW/2, 420), f"話す速さ {speed:.2f}倍 ／ 抑揚 {inton:.2f}", font=fB(34), fill=CYAN, anchor="mm")
    return im


if __name__ == "__main__":
    outs = []
    for mark, voice, name, sp, pi, it in VOICES:
        try:
            speaker_id(voice)
        except ValueError as e:
            print("注意:", e); continue
        log = []
        va, mix, subs, spans = build_audio(CLIP, voice, sp, pi, it, head=1.0, tail=0.9, log=log)
        L = {"__bg__": make_background(f"VOICEVOX:{voice}", credit_size=44), "cand": cand_layer(mark, voice, sp, pi, it)}
        out = os.path.join(OUTDIR, f"voice_{mark}_{name}.mp4")
        total = render(out, CLIP, L, va, mix, subs, spans)
        open(out[:-4] + "_読み方.txt", "w").write("\n".join(log) + "\n")
        print(f"{out}  {total:.2f}秒"); outs.append(out)
    lst = os.path.join(OUTDIR, "_concat.txt")
    open(lst, "w").write("".join(f"file '{os.path.basename(o)}'\n" for o in outs))
    allout = os.path.join(OUTDIR, "voice_compare_all.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", allout], check=True, cwd=OUTDIR)
    os.remove(lst)
    print("つなげた1本:", allout)
