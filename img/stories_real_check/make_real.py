#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイタウンガイド ストーリーズ（本番用・最初の6本）
  1080x1920 / 30fps / H.264 + AAC。公開前の確認用（このフォルダに保存）

使い方:  python3 make_real.py            … 6本すべて
         python3 make_real.py 20261202   … ファイル名の頭が合うものだけ
出力先:  このフォルダ（mp4）と _check/（確認画像）

型は img/stories_sample/motion/ の make_motion_v4.py（強い版）と make_motion_v4_soft.py（やさしい版）。
時間配分は v4 のとおり（呼びかけを約1.5秒止める／1社1.6秒／最後は2秒静止）。
  複数社: 呼びかけ → まず ここ見て → 〇社 → 1社ずつ → まとめ → 静止
  1社  : 呼びかけ → まず ここ見て → 会社の画面（約3秒）→ 同じ画面に「保存してね」を足して静止
会社名・電話番号・強みは、リーダーから受けた原稿どおり（SPECS）。ここ以外で文字を作り変えない。

素材の出どころ: フォント=Noto Sans CJK JP（強い版）/ M PLUS Rounded 1c（やさしい版）。どちらも SIL OFL 1.1。
  アイコン・飾り・音はすべて自作（音は numpy で合成）。写真・ロゴ・人物素材は使っていない。
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MOTION = os.path.join(os.path.dirname(HERE), "stories_sample", "motion")
sys.path.insert(0, MOTION)
import make_motion_v4 as v4            # noqa: E402
import make_motion_v4_soft as vs       # noqa: E402

v3, v2, v1, ms = v4.v3, v4.v2, v4.v1, v4.ms
W, H, S, FPS, SR, BEAT = v2.W, v2.H, v2.S, v2.FPS, v2.SR, v2.BEAT
blit, shape, tsprite, fit, clamp, back_out = v2.blit, v2.shape, v2.tsprite, v2.fit, v2.clamp, v2.back_out
TMP = os.environ.get("REAL_TMP", os.path.join(HERE, "_audio_tmp"))
RED0, RED_D0 = v3.RED, v3.RED_D


# ---------- 業種の色とアイコンを足す ----------
def icon_bag(d, cx, cy, r, col):
    """買い物袋（図形で自作）"""
    d.arc(ms.P(cx - r * .25, cy - r * .56, cx + r * .25, cy + r * .06), 180, 360, fill=col, width=int(r * .09 * S))
    d.rounded_rectangle(ms.P(cx - r * .44, cy - r * .2, cx + r * .44, cy + r * .5), radius=int(r * .08 * S), fill=col)
    for sx in (-.25, .25):
        d.ellipse(ms.P(cx + r * sx - r * .045, cy - r * .1, cx + r * sx + r * .045, cy - r * .01), fill=ms.WHITE)


ms.ICONS["shop"] = icon_bag
ms.ICONS["pest"] = ms.icon_house
ms.THEMES["shop"] = dict(main=(224, 82, 128), dark=(146, 30, 78), pale=(253, 230, 238))      # お買い物: ピンク
vs.SOFT["pest"] = dict(main=(196, 156, 118), deep=(134, 92, 58), pale=(246, 236, 224))       # シロアリ: 茶系

CTA_TEXT = "保存して、あとで見返してね"
SINGLE_LABEL = "マイタウンガイド掲載"


# ---------- 6本の原稿（ここを直せば作り直せる） ----------
def ed(name):
    return f"マイタウンガイド2026（{name}）"


SPECS = [
    dict(file="20261202_kamizono", style="strong", kind="car", area="串木野", particle="で", hook="車のことなら",
         edition_name="いちき串木野市版", count_label="たよれる車屋さん",
         companies=[("かみぞの自動車", "立会診断＋事前見積で安心", "0996-33-1150")]),
    dict(file="20261204_amamitsusho", style="soft", kind="pest", area="奄美大島", particle="で",
         hook="シロアリ・害虫にこまったら", edition_name="奄美大島版", count_label="シロアリ・害虫の相談先",
         companies=[("有限会社奄美通商", "施工後5年保証＋毎年無料点検", "0997-53-0067")]),
    dict(file="20261207_aira_isa_reform", style="soft", kind="house", area="姶良・伊佐", area_big="姶良伊佐",
         particle="で", hook="リフォームするなら", edition_name="姶良市版・伊佐版", count_label="リフォームの相談先",
         companies=[("合同会社カネユミ建築", "外壁塗装から水まわりまでおまかせ", "0120-698-222"),
                    ("匠塗（TAKUTO）", "一級技能士が施工・見積無料", "090-8839-2538")]),
    dict(file="20261209_tanegashima_kuruma1", style="strong", kind="car", area="種子島", particle="で",
         hook="車のことなら", edition_name="種子島版", count_label="たよれる車屋さん", part="その1",
         companies=[("ロータスイトウ", "指定工場で車検・整備", "0997-22-0222"),
                    ("株式会社 南星", "スピード車検・当日仕上げOK", "0997-23-2838"),
                    ("種子島ファミリーモータース", "新車・中古車の販売と買取", "0997-28-0913")]),
    dict(file="20261211_okinoerabu_omise1", style="strong", kind="shop", area="沖永良部", particle="で",
         hook="お店をさがすなら", edition_name="沖永良部版", count_label="島のお店・蔵元", part="その1",
         companies=[("ニシムタ", "キャン★ドゥの100円ショップあり", "0997-93-1147"),
                    ("沖永良部酒造株式会社", "島の焼酎をつくる蔵元", "0997-92-0185"),
                    ("新納酒造株式会社", "予約で工場見学ができる", "0997-93-4620")]),
    dict(file="20261214_minamikyushu_reform", style="soft", kind="house", area="南九州市", particle="で",
         hook="家をリフォームするなら", edition_name="南九州市版", count_label="リフォームの相談先",
         companies=[("株式会社塗木板金塗装", "一級塗装技能士が在籍", "0993-84-0408"),
                    ("株式会社 元脇板金工業", "一級技能士の屋根・外壁板金", "0993-25-4114"),
                    ("冨山塗装", "遮熱・断熱塗装と雨漏り防水", "0993-23-4552")]),
]


def single_timeline():
    """1社版: A 0〜2.0 / B 2.0〜3.2 / 会社 3.2〜（3.2秒）/ 6.8秒で「保存してね」/ 8.0〜10.0秒 静止"""
    return dict(A=0.0, B=2.0, C=3.2, D0=3.2, d_len=3.2, E=6.4, cta=6.8, static=8.0, dur=10.0)


# =====================================================================
# 強い版
# =====================================================================
def cta_strong(fr, M, v):
    """黄色の「保存して〜」: ピョコっと出て左右に揺れる＋きらめき（v = 出てからの秒）"""
    if v < 0:
        return
    spr = M["L"]["cta"]
    x0, y0, x1, y1 = spr.box
    p = v / .26
    ang = 8 * math.exp(-v * 3.2) * math.sin(v * 2 * math.pi * 4.2) if v < 1.15 else 0
    blit(fr, spr.img, (x0 + x1) / 2, (y0 + y1) / 2 + 60 * (1 - clamp(p)) ** 2,
         s=.3 + .7 * back_out(p, 3.2), angle=ang, alpha=clamp(p * 5))
    for (x, y, sc, dl) in ((x0 - 6, y0 + 4, .55, 0), (x1 + 6, y0 + 2, .65, .08), (x1 - 2, y1 + 2, .4, .18), (x0 + 14, y1 + 4, .36, .24)):
        q = (v - .2 - dl) / .42
        if 0 < q < 1:
            blit(fr, M["spark"], x, y, s=sc * math.sin(q * math.pi))


def prepare_strong(spec):
    if spec["kind"] == "shop":            # ピンク地に赤い帯は沈むので、帯はこげ茶にする
        v3.RED, v3.RED_D = (62, 42, 36), (30, 20, 18)
    else:
        v3.RED, v3.RED_D = RED0, RED_D0
    n = len(spec["companies"])
    full = dict(spec, line2=spec["hook"], line2_split=("まず", "ここ見て"), edition=ed(spec["edition_name"]),
                footer=ed(spec["edition_name"]) + "に掲載中", pill=f"{n}社をご紹介")
    M = v3.prepare(full)
    t = M["t"]
    M["spark"] = shape(90, 90, lambda d: (v1.star(d, 45 * S, 45 * S, 43 * S, ms.WHITE + (255,)),
                                          v1.star(d, 45 * S, 45 * S, 27 * S, (255, 214, 40, 255))))
    if n == 1:
        # 会社の画面: 番号のかわりに業種アイコン、「おすすめ 1/1」のかわりに掲載表記
        M["D"][0]["badge"] = M["C"]["icon"]
        M["D"][0]["prog"] = tsprite(SINGLE_LABEL, 66, t["dark"])
        return M
    # まとめ画面（長い社名でもはみ出さないよう、カードは 社名／強み／電話 の3段）
    area, part, hook, comps = spec["area"], spec["particle"], spec["hook"], spec["companies"]
    hb = 670
    bg = Image.new("RGB", (W * S, H * S), ms.CREAM)
    d = ImageDraw.Draw(bg)
    d.rectangle(ms.P(0, 0, W, hb), fill=t["main"])
    band = tuple(int(m * .88 + k * .12) for m, k in zip(t["main"], t["dark"]))
    d.polygon([ms.P(W * .52, 0), ms.P(W * .9, 0), ms.P(W * .45, hb), ms.P(W * .07, hb)], fill=band)
    for i in range(-1, W // 90 + 2):
        d.ellipse(ms.P(i * 90, hb - 45, i * 90 + 90, hb + 45), fill=t["main"])
    s1 = fit(area, 600, 170, 2)
    F = dict(bg=bg.resize((W, H), Image.LANCZOS),
             l1=v3.hstack([tsprite(area, s1, ms.YELLOW, stroke=2, shadow=t["dark"], off=7),
                           tsprite(part, s1 * .56, ms.WHITE, stroke=1.5, shadow=t["dark"], off=5)], gap=8),
             l2=tsprite(hook, fit(hook, 960 - (230 if spec.get("part") else 0), 118, 2), ms.WHITE, stroke=1.5,
                        shadow=t["dark"], off=6))
    if spec.get("part"):
        F["tag"] = shape(190, 76, lambda d: (d.rounded_rectangle(ms.P(0, 0, 190, 76), radius=int(38 * S), fill=ms.WHITE),
                                             ms.draw_text(d, (95, 36), spec["part"], ms.font(44), t["dark"], anchor="mm")))
    top, bot, gap = 722, 1470, 24
    cw = W - 120
    ch = min((bot - top - gap * (n - 1)) / n, 300)
    y0 = top + (bot - top - (ch * n + gap * (n - 1))) / 2
    F["cards"], F["card_y"] = [], []
    for i, (name, strong, tel) in enumerate(comps):
        def f_card(d, i=i, name=name, strong=strong, tel=tel):
            d.rounded_rectangle(ms.P(6, 8, cw + 6, ch + 8), radius=int(26 * S), fill=t["pale"])
            d.rounded_rectangle(ms.P(0, 0, cw, ch), radius=int(26 * S), fill=ms.WHITE, outline=t["main"], width=int(4 * S))
            nr = 44
            d.ellipse(ms.P(28, ch / 2 - nr, 28 + nr * 2, ch / 2 + nr), fill=t["main"])
            ms.draw_text(d, (28 + nr, ch / 2 - 3), str(i + 1), ms.font(60), ms.WHITE, anchor="mm")
            tx = 28 + nr * 2 + 24
            inner = cw - 28 - tx
            ms.draw_text(d, (tx, ch * .22), name, ms.font(fit(name, inner, 60)), ms.INK, anchor="lm")
            ms.draw_text(d, (tx, ch * .52), strong, ms.font(fit(strong, inner, 40, min_size=26), bold=False), ms.SUB, anchor="lm")
            ms.icon_phone(d, tx, ch * .81 - 19, 38, t["main"])
            ms.draw_text(d, (tx + 38 * 1.9 + 14, ch * .81), tel, ms.font(54), t["dark"], anchor="lm")
        F["cards"].append(shape(cw + 8, ch + 10, f_card))
        F["card_y"].append(y0 + i * (ch + gap) + (ch + 10) / 2)
    M["F"] = F
    return M


def scene_F(M, u, T):
    """強い版のまとめ画面"""
    F = M["F"]
    fr = F["bg"].copy()
    blit(fr, F["l1"], 60, 420, anchor=(0, .5))
    blit(fr, F["l2"], 60, 572, anchor=(0, .5))
    blit(fr, M["C"]["icon"], W - 60 - 96, 415, s=.82)
    if "tag" in F:
        blit(fr, F["tag"], W - 60 - 96, 574)
    for k, (card, cy) in enumerate(zip(F["cards"], F["card_y"])):
        p = (u - .1 - .12 * k) / .3
        if p > 0:
            blit(fr, card, 60 + card.width / 2, cy + 70 * (1 - clamp(p)) ** 2, s=.55 + .45 * back_out(p, 2.8), alpha=clamp(p * 4))
    cta_strong(fr, M, u - (T["cta"] - T["E"]))
    return fr


def render_strong(M, T, tm, cache):
    n, A = M["n"], M["A"]
    single = n == 1
    if tm >= T["static"]:
        if "final" in cache:
            return cache["final"]
        tm = T["static"]
    hits = [(ld, .8) for ld in A["lands"]] + [(A["de_land"], .4), (A["band_land"], 1.25), (T["B"] + v4.B_L2, .9)]
    punches = [(T["B"], .16, True), (T["E"], .1 if single else .14, True)]
    if not single:
        hits.append((T["C"] + .4, 1.2))
        punches.append((T["C"], .1, True))
    for i in range(n):
        hits.append((T["D0"] + i * T["d_len"] + .4, .45))
        punches.append((T["D0"] + i * T["d_len"], .1 if single else .06, True))
    b = 0
    while v4.BEAT0 + b * BEAT < T["E"] - 1e-6:
        punches.append((v4.BEAT0 + b * BEAT, .03, False))
        b += 1

    bar, creep = False, 0
    if tm < T["B"]:
        u, key = tm, "color"
        fr = v3.scene_A(M, u)
        creep = .06 * max(0, u - .5) / (T["B"] - .5)
    elif tm < T["C"]:
        u, key, bar = tm - T["B"], "yellow", True
        fr = v4.scene_B(M, u)
        creep = .05 * u / (T["C"] - T["B"])
    elif tm < T["D0"]:
        u, key, bar = tm - T["C"], "color", True
        fr = v3.scene_C(M, u)
        creep = .05 * u / (T["D0"] - T["C"])
    elif single or tm < T["E"]:
        i = 0 if single else int((tm - T["D0"]) / T["d_len"] + 1e-6)
        u, key, bar = tm - T["D0"] - i * T["d_len"], "card", True
        fr = v3.scene_D(M, i, u, T["d_len"])
    else:
        u, key = tm - T["E"], "card"
        fr = scene_F(M, u, T)

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
    if single and tm >= T["cta"]:
        cta_strong(fr, M, tm - T["cta"])
    v2.overlay(fr, M, key)
    if tm >= T["static"]:
        cache["final"] = fr
    return fr


# =====================================================================
# やさしい版
# =====================================================================
def prepare_soft(spec):
    full = dict(spec, b_lines=("まずは", "ここをチェック"), edition=ed(spec["edition_name"]),
                footer=ed(spec["edition_name"]) + "に掲載中", card_rows3=True)
    M = vs.prepare(full)
    if M["n"] == 1:
        M["D"][0]["badge"] = M["E"]["icon"]
        M["D"][0]["prog"] = vs.stxt(SINGLE_LABEL, 60, M["t"]["deep"])
    return M


def render_soft_single(M, T, tm, cache):
    if tm >= T["static"]:
        if "final" in cache:
            return cache["final"]
        tm = T["static"]
    bounds = [0.0, T["B"], T["D0"], 1e9]

    def raw(k, t_abs):
        u = t_abs - bounds[k]
        if k == 0:
            return v2.camera(vs.scene_A(M, u, t_abs), 1 + .03 * clamp(u / T["B"]))
        if k == 1:
            return v2.camera(vs.scene_B(M, u, t_abs), 1 + .03 * clamp(u / (T["D0"] - T["B"])))
        fr = v2.camera(vs.scene_D(M, 0, u, min(t_abs, T["static"]), T["d_len"]), 1 + .02 * clamp(u / T["d_len"]))
        v = t_abs - T["cta"]
        p = vs.poyon(v, .5)
        if p:
            E = M["E"]
            ang = 3.5 * math.exp(-v * 4) * math.sin(v * 2 * math.pi * 2.2) if v < 1.1 else 0
            blit(fr, E["cta"], W / 2, 1534, s=p[0], alpha=p[1], angle=ang)
            cw = E["cta"].width / 2 - 30
            for (x, y, dl, sc) in ((W / 2 - cw, 1494, .1, .6), (W / 2 + cw, 1502, .25, .75), (W / 2 + cw - 60, 1574, .4, .45)):
                q = (v - dl) / .55
                if 0 < q < 1:
                    blit(fr, M["spark"], x, y, s=sc * math.sin(q * math.pi))
        return fr
    k = 0 if tm < T["B"] else (1 if tm < T["D0"] else 2)
    fr = raw(k, tm)
    u = tm - bounds[k]
    if k > 0 and u < vs.XF:
        if ("prev", k) not in cache:
            cache[("prev", k)] = raw(k - 1, bounds[k] - 1e-3)
        p = u / vs.XF
        fr = Image.blend(cache[("prev", k)], fr, p * p * (3 - 2 * p))
    vs.overlay(fr, M, dict(T, E=1e9), tm)
    if tm >= T["static"]:
        cache["final"] = fr
    return fr


# =====================================================================
# 書き出しと確認画像
# =====================================================================
def encode(frames, wav, out, dur, gain_db=0.0):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-af", f"volume={gain_db}dB",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", str(dur), "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames:
        pr.stdin.write(fr.tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")


def grab(mp4, n, path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", f"select=eq(n\\,{n})",
                    "-frames:v", "1", path], check=True)
    return Image.open(path).convert("RGB")


def check_images(mp4, name, stamps, nf):
    """コマを並べた確認画像と、最後のコマ（原寸）を _check/ に保存"""
    chk = os.path.join(HERE, "_check")
    os.makedirs(chk, exist_ok=True)
    cw, chh, cols = 432, 768, 5
    rows = math.ceil(len(stamps) / cols)
    sheet = Image.new("RGB", (cols * (cw + 12) + 12, rows * (chh + 70) + 10), (50, 50, 50))
    d = ImageDraw.Draw(sheet)
    f = ms.ImageFont.truetype(ms.FONT_B, 38)
    tmp = os.path.join(chk, "_tmp.png")
    for i, ts in enumerate(stamps):
        im = grab(mp4, min(nf - 1, round(ts * FPS)), tmp).convert("RGBA")
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        do = ImageDraw.Draw(ov)
        do.rectangle((0, 0, W, ms.SAFE_TOP), fill=(0, 0, 0, 90))
        do.rectangle((0, ms.SAFE_BOTTOM, W, H), fill=(0, 0, 0, 90))
        im = Image.alpha_composite(im, ov).convert("RGB").resize((cw, chh), Image.LANCZOS)
        x, y = 12 + (i % cols) * (cw + 12), 8 + (i // cols) * (chh + 70)
        sheet.paste(im, (x, y + 56))
        d.text((x + 6, y), "最後" if i == len(stamps) - 1 else f"{ts:.1f}秒", font=f, fill=(255, 255, 255))
    sheet.save(os.path.join(chk, f"{name}_frames.jpg"), quality=90)
    grab(mp4, nf - 1, tmp).save(os.path.join(chk, f"{name}_last.jpg"), quality=92)
    os.remove(tmp)


def make(spec):
    name, n = spec["file"], len(spec["companies"])
    out = os.path.join(HERE, name + ".mp4")
    os.makedirs(os.path.join(TMP, name), exist_ok=True)
    wav = os.path.join(TMP, name, "mix.wav")
    T = single_timeline() if n == 1 else v4.timeline(n)
    nf = int(round(T["dur"] * FPS))
    cache = {}
    if spec["style"] == "strong":
        M = prepare_strong(spec)
        v4.make_audio(M, T, wav)
        frames = (render_strong(M, T, k / FPS + 1e-6, cache) for k in range(nf))
    else:
        M = prepare_soft(spec)
        vs.make_audio(M, T, wav)
        fn = render_soft_single if n == 1 else vs.render
        frames = (fn(M, T, k / FPS + 1e-6, cache) for k in range(nf))
    # 強い版の1社版は音の山が少し高く出るので、ほかの強い版（約-6dB）にそろえる
    encode(frames, wav, out, T["dur"], gain_db=-1.0 if (spec["style"] == "strong" and n == 1) else 0.0)
    if n == 1:
        stamps = [.3, 1.9, T["B"] + 1.1, T["D0"] + 1.0, T["D0"] + 3.0, (nf - 1) / FPS]
    else:
        stamps = [.3, 1.9, T["B"] + 1.1, T["C"] + 1.0] + [T["D0"] + i * T["d_len"] + 1.3 for i in range(n)] \
                 + [T["E"] + .7, (nf - 1) / FPS]
    check_images(out, name, stamps, nf)
    print("saved", out, f"{T['dur']}秒", spec["style"], f"{n}社")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for spec in SPECS:
        if spec["file"].startswith(only):
            make(spec)
