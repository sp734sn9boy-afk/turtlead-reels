# -*- coding: utf-8 -*-
"""今週のAIニュース 第1回（ショート・縦型1080x1920・30fps）を作る。

使い方（VOICEVOX ENGINE を先に起動。turtle_video.py の説明を参照）：
  python3 make_vol1.py                         # 声＝春日部つむぎ → turtle_ainews_vol1_tsumugi.mp4
  python3 make_vol1.py --voice ナースロボ＿タイプＴ --name nurserobo
  python3 make_vol1.py --voice 雀松朱司 --speed 1.05 --intonation 1.15 --name akashi
台本の元：同じフォルダの 台本_ショート.md
"""
import argparse, math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from turtle_video import *   # noqa

PW, PH = 1080, 500          # パネルの大きさ（画面の y=425〜925）

# ---------------------------------------------------------------- 台本（台本_ショート.md と同じ文）
LINES = [
    Line([Chunk(["タートルアドのタートルです。"])], body="intro", gap=0.25),
    Line([Chunk(["今週のAIニュースを、3つ紹介します。"])], body="intro", gap=0.38),
    Line([Chunk(["ひとつめ。アンソロピックが、"]),
          Chunk(["新しいAI「Claude Fable 5.2」を", "出しました。"])], head="n1", body="n1_main", chime=True),
    Line([Chunk(["前の型より、答えが出るのが", "最大3割ほど速くなったそうです。"])], head="n1", body="n1_fast"),
    Line([Chunk(["ふだんの仕事は、今のAIで十分。"]),
          Chunk(["むずかしい作業のときに", "試すのがおすすめです。"])], head="n1", body="n1_tip", gap=0.38),
    Line([Chunk(["ふたつめ。ChatGPTで、", "会社やお店の情報を、"]),
          Chunk(["自分で管理できる仕組みが", "始まりました。"])], head="n2", body="n2_main", chime=True),
    Line([Chunk(["まだ試験中の機能です。"])], head="n2", body="n2_beta"),
    Line([Chunk(["Googleマップと同じように、", "AIの中で、"]),
          Chunk(["自分の会社が", "どう紹介されているか、"]),
          Chunk(["確かめる時代です。"])], head="n2", body="n2_tip", gap=0.38),
    Line([Chunk(["みっつめ。GoogleのGeminiの", "「タスク」機能が、"]),
          Chunk(["日本でも無料になりました。"])], head="n3", body="n3_main", chime=True),
    Line([Chunk(["アメリカでは、", "AIがお店に電話して、"]),
          Chunk(["値段を聞くこともできます。"])], head="n3", body="n3_call"),
    Line([Chunk(["AIがお客さんの代わりに", "調べる時代。"]),
          Chunk(["営業時間や料金は、", "いつも最新にしておきましょう。"])], head="n3", body="n3_tip", gap=0.38),
    Line([Chunk(["AIは、毎週のように", "新しくなっています。"])], body="weekly", nod=True, gap=0.35),   # 「しめ」の1文目（--full のときだけ入れる）
    Line([Chunk(["タートルアドでは、AIの使い方の", "ご相談を受け付けています。"]),
          Chunk(["また来週。"])], body="ending", gap=0.0, nod=True),
]

NEWS = {
    "n1": ("1", "新しいAI「Claude Fable 5.2」", "発表 11月9日", "出典：Anthropic公式"),
    "n2": ("2", "ChatGPTで 自分の会社の情報を管理", "発表 11月10日", "出典：OpenAI公式X"),
    "n3": ("3", "Geminiの「タスク」が 日本で無料に", "発表 11月17日", "出典：Android Authorityほか"),
}
DISCLOSURE = ["この動画は、タートルアドのAIチームが", "情報収集から台本・音声・映像まで", "作っています"]


# ---------------------------------------------------------------- パネルの絵
def canvas():
    return Image.new("RGBA", (PW, PH), (0, 0, 0, 0))

def card(d, box, outline=CYAN, fill=(4, 7, 15, 215), r=30, width=3):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def pill(d, cx, cy, s, size=34, fill=YELLOW, color=INK, padx=26):
    w = fB(size).getlength(s) + padx * 2; h = size + 22
    d.rounded_rectangle((cx - w/2, cy - h/2, cx + w/2, cy + h/2), h/2, fill=fill)
    d.text((cx, cy), s, font=fB(size), fill=color, anchor="mm")

def head_layer(key):
    num, title, date, src = NEWS[key]
    im = canvas(); d = ImageDraw.Draw(im)
    card(d, (50, 0, PW - 50, 128))
    d.ellipse((72, 14, 172, 114), fill=CYAN)
    d.text((122, 62), num, font=fR(70), fill=INK, anchor="mm")
    text_fit(d, (196, 46), title, 46, PW - 50 - 196 - 24, fill=WHITE, anchor="lm")
    d.text((196, 98), f"{date}　｜　{src}", font=fB(28), fill=DIM, anchor="lm")
    return im

def body_canvas():
    im = canvas(); d = ImageDraw.Draw(im)
    card(d, (50, 146, PW - 50, PH - 4), outline=(60, 214, 240, 120), width=2)
    return im, d

def disclosure_box(d, y0, y1, size=42):
    card(d, (70, y0, PW - 70, y1), outline=YELLOW, fill=(20, 16, 4, 225), width=4)
    lh = size + 16; top = (y0 + y1) / 2 - lh * (len(DISCLOSURE) - 1) / 2
    for k, l in enumerate(DISCLOSURE):
        d.text((PW/2, top + lh*k), l, font=fB(size), fill=WHITE, anchor="mm")

def telop(lines, sub=None, color=WHITE, size=66, chip=None, y=None):
    im, d = body_canvas()
    lh = size + 22
    cy = y or (330 if not sub else 300)
    top = cy - lh * (len(lines) - 1) / 2
    if chip: pill(d, PW/2, 200, chip); top += 20
    for k, l in enumerate(lines):
        text_fit(d, (PW/2, top + lh*k), l, size, PW - 160, fill=color, anchor="mm")
    if sub: d.text((PW/2, PH - 50), sub, font=fB(30), fill=DIM, anchor="mm")
    return im

def tip_header(d):
    pill(d, PW/2, 196, "中小企業なら", size=34)

# --- アイコン（他社のロゴは使わない。図形だけで描く）
def icon_pin(d, cx, cy, s):
    r = s * 0.36
    d.polygon([(cx - r*0.92, cy - s*0.12), (cx + r*0.92, cy - s*0.12), (cx, cy + s*0.5)], fill=(255, 99, 99))
    d.ellipse((cx - r, cy - s*0.5, cx + r, cy - s*0.5 + 2*r), fill=(255, 99, 99))
    d.ellipse((cx - r*0.42, cy - s*0.5 + r*0.58, cx + r*0.42, cy - s*0.5 + r*1.42), fill=WHITE)

def icon_bubble(d, cx, cy, s):
    d.rounded_rectangle((cx - s*0.5, cy - s*0.42, cx + s*0.5, cy + s*0.22), s*0.16, fill=CYAN)
    d.polygon([(cx - s*0.2, cy + s*0.2), (cx - s*0.32, cy + s*0.48), (cx + s*0.04, cy + s*0.2)], fill=CYAN)
    d.text((cx, cy - s*0.1), "AI", font=fR(int(s*0.38)), fill=INK, anchor="mm")

def icon_phone(d, cx, cy, s):
    d.rounded_rectangle((cx - s*0.26, cy - s*0.48, cx + s*0.26, cy + s*0.48), s*0.08, fill=WHITE)
    d.rounded_rectangle((cx - s*0.2, cy - s*0.38, cx + s*0.2, cy + s*0.34), s*0.03, fill=(20, 36, 90))
    d.ellipse((cx - s*0.04, cy + s*0.38, cx + s*0.04, cy + s*0.45), fill=(20, 36, 90))
    for k in range(3):
        rr = s * (0.42 + 0.14*k)
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), -40, 40, fill=CYAN, width=int(s*0.05))
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), 140, 220, fill=CYAN, width=int(s*0.05))
    d.text((cx, cy - s*0.04), "AI", font=fR(int(s*0.24)), fill=CYAN, anchor="mm")

def icon_clock(d, cx, cy, s):
    r = s * 0.46
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=CYAN, width=int(s*0.07))
    d.line((cx, cy, cx, cy - r*0.62), fill=INK, width=int(s*0.07))
    d.line((cx, cy, cx + r*0.48, cy + r*0.1), fill=INK, width=int(s*0.07))
    d.ellipse((cx - s*0.05, cy - s*0.05, cx + s*0.05, cy + s*0.05), fill=INK)

def icon_tag(d, cx, cy, s):
    pts = [(cx - s*0.5, cy - s*0.3), (cx + s*0.22, cy - s*0.3), (cx + s*0.5, cy), (cx + s*0.22, cy + s*0.3), (cx - s*0.5, cy + s*0.3)]
    d.polygon(pts, fill=YELLOW)
    d.ellipse((cx + s*0.17, cy - s*0.06, cx + s*0.29, cy + s*0.06), fill=INK)
    d.text((cx - s*0.14, cy), "¥", font=fB(int(s*0.42)), fill=INK, anchor="mm")


def build_layers(voice):
    L = {"__bg__": make_background(f"turtle ad ｜ 音声：VOICEVOX:{voice}")}
    for k in NEWS: L[k] = head_layer(k)

    # 冒頭：タイトル＋「この動画は…」を大きめに
    im = canvas(); d = ImageDraw.Draw(im)
    d.text((PW/2 - 100, 70), "今週のAIニュース", font=fB(76), fill=WHITE, anchor="mm")
    pill(d, PW/2 + 345, 72, "11/20号", size=38)
    disclosure_box(d, 150, 470, size=46)
    L["intro"] = im

    L["n1_main"] = telop(["新しいAI", "「Claude Fable 5.2」"], size=70, color=WHITE)
    im, d = body_canvas()
    d.text((PW/2, 240), "答えが出るのが", font=fB(46), fill=WHITE, anchor="mm")
    d.text((PW/2, 340), "最大30%速く", font=fB(112), fill=YELLOW, anchor="mm", stroke_width=3, stroke_fill=INK)
    d.text((PW/2, 440), "前の型（Fable 5.1）と比べて", font=fB(32), fill=DIM, anchor="mm")
    L["n1_fast"] = im
    im, d = body_canvas(); tip_header(d)
    for k, (a, b) in enumerate([("ふだん", "今のAI"), ("むずかしい作業", "新しいAI")]):
        y = 278 + k * 80
        d.text((PW/2 - 40, y), a, font=fB(50), fill=WHITE, anchor="rm")
        d.text((PW/2, y), "→", font=fB(50), fill=CYAN, anchor="mm")
        d.text((PW/2 + 40, y), b, font=fB(50), fill=YELLOW, anchor="lm")
    d.text((PW/2, 440), "使い分けがコツ", font=fB(44), fill=CYAN, anchor="mm")
    L["n1_tip"] = im

    L["n2_main"] = telop(["ChatGPTで", "自分の会社の情報を管理"], size=66)
    im, d = body_canvas()
    d.text((PW/2, 270), "まだ試験中", font=fB(96), fill=WHITE, anchor="mm")
    pill(d, PW/2, 400, "ベータ", size=46, fill=(255, 140, 66), color=INK, padx=40)
    L["n2_beta"] = im
    im, d = body_canvas(); tip_header(d)
    icon_pin(d, PW/2 - 170, 300, 116); d.text((PW/2 - 170, 385), "Googleマップ", font=fB(30), fill=DIM, anchor="mm")
    d.text((PW/2, 290), "＋", font=fB(60), fill=WHITE, anchor="mm")
    icon_bubble(d, PW/2 + 170, 300, 116); d.text((PW/2 + 170, 385), "AIの中", font=fB(30), fill=DIM, anchor="mm")
    d.text((PW/2, 448), "AIの中の自社の紹介も確認を", font=fB(40), fill=YELLOW, anchor="mm")
    L["n2_tip"] = im

    im, d = body_canvas()
    d.text((PW/2, 230), "Geminiの「タスク」が", font=fB(60), fill=WHITE, anchor="mm")
    d.text((PW/2, 318), "日本で無料に", font=fB(76), fill=YELLOW, anchor="mm", stroke_width=2, stroke_fill=INK)
    pill(d, PW/2, 425, "日本を含む6か国", size=36, fill=CYAN)
    L["n3_main"] = im
    im, d = body_canvas()
    icon_phone(d, 250, 320, 190)
    d.text((440, 250), "米国では", font=fB(48), fill=DIM, anchor="lm")
    d.text((440, 330), "AIがお店に電話も", font=fB(56), fill=WHITE, anchor="lm")
    d.text((440, 420), "※アメリカでの機能", font=fB(32), fill=YELLOW, anchor="lm")
    L["n3_call"] = im
    im, d = body_canvas(); tip_header(d)
    icon_clock(d, 200, 340, 120); icon_tag(d, 360, 340, 130)
    d.text((470, 300), "営業時間・料金は", font=fB(48), fill=WHITE, anchor="lm")
    d.text((470, 378), "いつも最新に", font=fB(60), fill=YELLOW, anchor="lm")
    L["n3_tip"] = im

    L["weekly"] = telop(["AIは毎週", "新しくなっています"], size=74, y=320)

    # 最後：ロゴ＋ご相談＋「この動画は…」
    im = canvas(); d = ImageDraw.Draw(im)
    card(d, (50, 0, PW - 50, PH - 4), outline=CYAN, width=3)
    mk = logo_mark(130); im.paste(mk, (250, 22), mk)
    d.text((400, 88), "turtle ", font=fR(92), fill=WHITE, anchor="lm")
    d.text((400 + fR(92).getlength("turtle "), 88), "ad", font=fR(92), fill=CYAN, anchor="lm")
    d.text((PW/2, 200), "AIの使い方　ご相談受付中", font=fB(50), fill=YELLOW, anchor="mm")
    disclosure_box(d, 250, 480, size=42)
    L["ending"] = im
    return L


def end_credit(voice):
    im = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 10, W - 60, 230), 28, fill=(4, 7, 15, 222), outline=(60, 214, 240, 120), width=2)
    d.text((W/2, 70), "クレジット", font=fB(30), fill=DIM, anchor="mm")
    text_fit(d, (W/2, 128), f"音声：VOICEVOX:{voice}", 46, W - 200, fill=WHITE, anchor="mm")
    d.text((W/2, 190), "制作：タートルアド AIチーム", font=fB(36), fill=WHITE, anchor="mm")
    return im


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="春日部つむぎ")
    ap.add_argument("--name", default="tsumugi", help="出力ファイル名の末尾")
    ap.add_argument("--speed", type=float, default=1.25)
    ap.add_argument("--pitch", type=float, default=0.0)
    ap.add_argument("--intonation", type=float, default=1.1)
    ap.add_argument("--no-chime", action="store_true")
    ap.add_argument("--full", action="store_true", help="「AIは、毎週のように新しくなっています。」も入れる（約3秒長くなる）")
    a = ap.parse_args()
    # 台本の注記「長ければ『しめ』の1文目を削る」に従い、ふだんは「AIは、毎週のように…」を省いて55秒前後に収める
    lines = LINES if a.full else [ln for ln in LINES if ln.body != "weekly"]
    if a.no_chime:
        for ln in lines: ln.chime = False
    log = []
    voice_a, mix, subs, spans = build_audio(lines, a.voice, a.speed, a.pitch, a.intonation, log=log)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"turtle_ainews_vol1_{a.name}.mp4")
    for b in sub_overflow_check(subs): print("字幕の注意:", b)
    total = render(out, lines, build_layers(a.voice), voice_a, mix, subs, spans, end_layer=end_credit(a.voice))
    open(out[:-4] + "_読み方.txt", "w").write("番号\t読み上げた文\tVOICEVOXの読み（アクセント記号つき）\n" + "\n".join(log) + "\n")
    print(f"できました: {out}  長さ {total:.2f}秒")
    for (s, e, ls) in subs: print(f"{s:6.2f}-{e:6.2f}  {' / '.join(ls)}")
