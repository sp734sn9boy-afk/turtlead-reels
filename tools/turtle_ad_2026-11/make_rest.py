import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from make_1122_1124 import *


def title_page(seed, label, parts, fn, chip=None, n=None):
    """parts: [(文字, サイズ, grad)]"""
    img = base(seed, label)
    y = 230
    for t, s, g in parts:
        y = text_block(img, X, y, t, 'black', s, maxw=MW, lh=1.3, grad=g)
    if chip:
        pill(img, X, y + 40, chip, size=44, outline=YELLOW, color=YELLOW)
    swipe_hint(img, 'スワイプしてね →', y=1210)
    save(img, OUT + fn)


def step_page(seed, label, i, n, head, body=None, fn='', body_box=False, note=None):
    img = base(seed, label, i, n, nodes=False)
    y = text_block(img, X, 230, head, 'black', 86, maxw=MW, lh=1.35)
    if body:
        y += 50
        if body_box:
            hh = len(wrap(body, font('bold', 46), MW - 100)) * int(46 * 1.55) + 70
            card(img, (X, y, W - X, y + hh), fill=(240, 244, 252), outline=CYAN, width=4)
            y = text_block(img, X + 50, y + 34, body, 'bold', 46, fill=(16, 24, 52), maxw=MW - 100, lh=1.55) + 40
        else:
            card(img, (X, y, W - X, y + 200))
            text_block(img, X + 44, y + 40, body, 'bold', 50, maxw=MW - 88, lh=1.45, fill=YELLOW)
            y += 240
    if note:
        y += 20
        text_block(img, X, y, note, 'bold', 42, maxw=MW, lh=1.5, fill=SUB)
    save(img, OUT + fn)


def end_page(seed, label, i, n, parts, box_main, box_sub, fn):
    img = base(seed, label, i, n)
    y = 240
    for t, s, g in parts:
        y = text_block(img, X, y, t, 'black', s, maxw=MW, lh=1.3, grad=g)
    y += 60
    hh = 200 if box_sub else 140
    card(img, (X, y, W - X, y + hh), glow=True)
    text_block(img, X, y + 30, box_main, 'black', 60, maxw=MW, align='center', fill=YELLOW)
    if box_sub:
        text_block(img, X, y + 116, box_sub, 'bold', 44, maxw=MW, align='center')
    save(img, OUT + fn)


# ---------- 11/26 画像：スマホで3秒チェック ----------
def i1126():
    img = background(W, H, 26)
    eyebrow(img, X, 96, '3 SECONDS CHECK')
    y = text_block(img, X, 190, '自分のホームページ、\nスマホで開いてみてください', 'bold', 52, maxw=MW, lh=1.45, fill=SUB)
    y += 20
    y = text_block(img, X, y, '3秒で、', 'black', 120, maxw=MW, lh=1.25, grad=True)
    y = text_block(img, X, y, '何のお店か\nわかりますか？', 'black', 84, maxw=MW, lh=1.28)
    y += 24
    for t in ['店名・業種', '電話番号', '営業時間']:
        card(img, (X, y, W - X, y + 100))
        checkbox(img, X + 30, y + 16, size=68)
        ImageDraw.Draw(img).text((X + 136, y + 14), t, font=font('black', 54), fill=WHITE)
        y += 112
    y += 16
    text_block(img, X, y, '1つでも見つからなければ、見直しどき', 'black', 46, maxw=MW, fill=YELLOW)
    paste_logo(img, 80, 1220)
    save(img, OUT + '2026-11-26_スマホで3秒チェック.jpg')


# ---------- 11/27 カルーセル：口コミ返信 ----------
def c1127():
    n = 5
    p = '2026-11-27_口コミ返信をAIで下書き_'
    title_page(30, 'AI HOW-TO', [('口コミの返信、', 100, False), ('AIに下書き', 110, True), ('してもらう方法', 100, False)], p + '01.jpg', chip='Googleマップの口コミに')
    step_page(31, 'STEP 1', 2, n, '① 口コミを\nコピーして\nAIに貼る', fn=p + '02.jpg', note='ChatGPTなどのAIに貼りつけます')
    step_page(32, 'STEP 2', 3, n, '② こう頼む', 'この口コミに、お店の店主として、ていねいで短いお礼の返信を作ってください。名前や個人情報は書かないでください', fn=p + '03.jpg', body_box=True, note='そのまま使えます')
    step_page(33, 'STEP 3', 4, n, '③ 自分の言葉を\n一言足して返信', fn=p + '04.jpg', note='AIの文に、お店の言葉を一言だけ')
    img = base(34, 'CAUTION', 5, n)
    y = text_block(img, X, 240, '低い評価の口コミは、', 'black', 80, maxw=MW, lh=1.35)
    y = text_block(img, X, y, 'AIの文を\nそのまま使わず、', 'black', 96, maxw=MW, lh=1.3, grad=True)
    y = text_block(img, X, y, '必ず自分で\n読み直す', 'black', 96, maxw=MW, lh=1.3)
    save(img, OUT + p + '05.jpg')


# ---------- 11/29 カルーセル：料金 ----------
def c1129():
    n = 6
    p = '2026-11-29_HP料金と月額の中身_'
    title_page(40, 'PRICE', [('ホームページ制作の', 86, False), ('料金、', 120, True), ('ぜんぶ見せます', 100, False)], p + '01.jpg')
    # 2 制作費
    img = base(41, 'PRICE', 2, n, nodes=False)
    y = text_block(img, X, 220, '制作費（税込）', 'black', 80, maxw=MW)
    y += 30
    for k, (nm, pr) in enumerate([('ライト', '55,000'), ('スタンダード', '88,000'), ('しっかり', '132,000')]):
        card(img, (X, y, W - X, y + 160), glow=(k == 1), outline=(CYAN if k == 1 else (60, 80, 130)))
        d = ImageDraw.Draw(img)
        d.text((X + 44, y + 44), nm, font=font('black', 54), fill=WHITE)
        f = font('black', 84); fs = font('bold', 38)
        tw = d.textlength(pr, font=f); sw = d.textlength('円〜', font=fs)
        d.text((W - X - 40 - sw - tw - 8, y + 22), pr, font=f, fill=WHITE)
        d.text((W - X - 40 - sw, y + 76), '円〜', font=fs, fill=WHITE)
        y += 186
    save(img, OUT + p + '02.jpg')
    # 3 月額
    img = base(42, 'MONTHLY', 3, n, nodes=False)
    y = text_block(img, X, 260, '別途', 'black', 80, maxw=MW)
    d = ImageDraw.Draw(img)
    y = text_block(img, X, y, '月額5,500円', 'black', 136, maxw=MW, lh=1.25, grad=True)
    y = text_block(img, X, y, '（税込）の契約が\n必要です', 'black', 86, maxw=MW, lh=1.35)
    y += 40
    text_block(img, X, y, 'ドメイン・サーバー代込み', 'bold', 46, maxw=MW, fill=SUB)
    save(img, OUT + p + '03.jpg')
    # 4 月額に入っているもの
    img = base(43, 'MONTHLY', 4, n, nodes=False)
    y = text_block(img, X, 210, '月額に入っているもの', 'black', 72, maxw=MW)
    y += 24
    items = ['サーバー・ドメイン代', 'WordPressの更新・保守', 'セキュリティ対策', 'バックアップ', '文章の変更・写真の差し替え', 'Googleマップの情報更新']
    for t in items:
        card(img, (X, y, W - X, y + 118))
        checkbox(img, X + 26, y + 22, size=74, checked=True)
        ImageDraw.Draw(img).text((X + 130, y + 26), t, font=font('bold', 48), fill=WHITE)
        y += 132
    save(img, OUT + p + '04.jpg')
    # 5 LINEで送るだけ
    img = base(44, 'EASY', 5, n, nodes=False)
    y = text_block(img, X, 260, '頼み方は', 'black', 90, maxw=MW, lh=1.3)
    y = text_block(img, X, y, 'LINEで\n送るだけ', 'black', 136, maxw=MW, lh=1.25, grad=True)
    y += 60
    card(img, (X, y, W - X, y + 130))
    text_block(img, X + 40, y + 36, '※ページ追加・デザイン変更は別見積もり', 'bold', 42, maxw=MW - 80, fill=SUB)
    save(img, OUT + p + '05.jpg')
    end_page(45, 'TURTLE AD', 6, n, [('月額があるぶん、', 84, False), ('最初の制作費を', 96, True), ('おさえています', 96, False)], '相談は無料', 'プロフィールのリンクから', p + '06.jpg')


# ---------- 11/30 画像：貼るのは12月上旬 ----------
def i1130():
    img = background(W, H, 30)
    eyebrow(img, X, 96, 'NEW YEAR HOLIDAY')
    y = text_block(img, X, 180, '年末年始のお知らせ、', 'black', 66, maxw=MW, lh=1.3)
    y = text_block(img, X, y, '貼るのは', 'black', 80, maxw=MW, lh=1.25)
    y = text_block(img, X, y, '12月上旬が', 'black', 120, maxw=MW, lh=1.2, grad=True)
    y = text_block(img, X, y, 'おすすめ', 'black', 80, maxw=MW, lh=1.3)
    y += 20
    y = text_block(img, X, y, '書くのは4つだけ', 'black', 54, maxw=MW, fill=YELLOW)
    y += 6
    items = ['① 最終営業日', '② 営業開始日', '③ 時間が変わる日', '④ 急ぎの連絡先']
    cw = (MW - 20) // 2
    for k, t in enumerate(items):
        x0 = X + (k % 2) * (cw + 20)
        y0 = y + (k // 2) * 116
        card(img, (x0, y0, x0 + cw, y0 + 100))
        ImageDraw.Draw(img).text((x0 + 26, y0 + 22), t, font=font('bold', 44), fill=WHITE)
    y += 250
    card(img, (X, y, W - X, y + 130), glow=True)
    text_block(img, X, y + 18, '作るのはおまかせ：梅3,500円〜（税込）', 'black', 40, maxw=MW, align='center', fill=YELLOW)
    text_block(img, X, y + 72, '受付12/20まで', 'bold', 38, maxw=MW, align='center')
    save(img, OUT + '2026-11-30_お知らせは12月上旬に.jpg')


# ---------- 12/1 カルーセル：AIに頼むコツ3つ ----------
def c1201():
    n = 5
    p = '2026-12-01_AIに頼むコツ3つ_'
    title_page(50, 'AI HOW-TO', [('AIの答えが', 96, False), ('イマイチな人へ', 104, True)], p + '01.jpg', chip='頼み方のコツ3つ')
    step_page(51, 'TIP 1', 2, n, '① 自分が誰かを\n伝える', '例：鹿児島市の美容室の店主です', fn=p + '02.jpg')
    step_page(52, 'TIP 2', 3, n, '② 何に使うかを\n伝える', '例：Instagramに載せる、\n40代の女性向け', fn=p + '03.jpg')
    step_page(53, 'TIP 3', 4, n, '③ 形を決める', '例：100字以内で3案、\nやさしい言葉で', fn=p + '04.jpg')
    end_page(54, 'TURTLE AD', 5, n, [('AIの使い方、', 96, False), ('お教えします', 110, True)], '全国オンライン', 'ご相談はプロフィールのリンクから', p + '05.jpg')


# ---------- 12/3 カルーセル：問い合わせが来ないHP ----------
def c1203():
    n = 6
    p = '2026-12-03_問い合わせが来ないHPの共通点_'
    title_page(60, 'HOMEPAGE', [('問い合わせが', 96, False), ('来ない', 130, True), ('ホームページ、', 96, False)], p + '01.jpg', chip='3つの共通点')
    for k, t in enumerate(['① 何をしてくれるのかが\n最初にない', '② 料金の目安が\n書いていない', '③ 問い合わせボタンが\n見つからない']):
        img = base(61 + k, f'POINT {k + 1:02d}', k + 2, n, nodes=False)
        d = ImageDraw.Draw(img)
        d.text((W - 430, 170), f'{k + 1:02d}', font=font('black', 300), fill=(30, 46, 90))
        text_block(img, X, 600, t, 'black', 82, maxw=MW, lh=1.38)
        save(img, OUT + p + f'{k + 2:02d}.jpg')
    img = base(64, 'HOW TO FIX', 5, n, nodes=False)
    y = text_block(img, X, 240, '直すなら：', 'black', 86, maxw=MW, lh=1.3)
    y = text_block(img, X, y, '一番上に', 'black', 86, maxw=MW, lh=1.3)
    y += 30
    for t in ['何を', 'どこで', 'いくらから']:
        card(img, (X, y, W - X, y + 140), glow=True)
        text_block(img, X, y + 26, f'「{t}」', 'black', 74, maxw=MW, align='center', fill=YELLOW)
        y += 160
    save(img, OUT + p + '05.jpg')
    end_page(65, 'TURTLE AD', 6, n, [('見直しの相談は', 96, False), ('無料', 160, True)], 'プロフィールのリンクから', None, p + '06.jpg')


# ---------- 12/4 画像：あと16日 ----------
def i1204():
    img = background(W, H, 44)
    eyebrow(img, X, 96, 'NEW YEAR HOLIDAY')
    y = text_block(img, X, 190, '年末年始お知らせセット', 'black', 66, maxw=MW, lh=1.3)
    y = text_block(img, X, y, '受付は12/20まで', 'black', 66, maxw=MW, lh=1.3, fill=SUB)
    y += 10
    d = ImageDraw.Draw(img)
    f1 = font('black', 120); f2 = font('black', 330)
    d.text((X, y + 120), 'あと', font=f1, fill=WHITE)
    x2 = X + d.textlength('あと', font=f1) + 10
    gradient_text(img, int(x2), int(y - 20), '16', f2, c1=(255, 230, 120), c2=YELLOW, c3=(255, 170, 60))
    d.text((x2 + d.textlength('16', font=f2) + 10, y + 120), '日', font=f1, fill=WHITE)
    y += 440
    rows = [('梅', '3,500'), ('竹', '5,500'), ('松', '8,000')]
    cw = (MW - 40) // 3
    for k, (a, pr) in enumerate(rows):
        x0 = X + k * (cw + 20)
        card(img, (x0, y, x0 + cw, y + 200))
        text_block(img, x0, y + 16, a, 'black', 60, maxw=cw, align='center', fill=YELLOW)
        f = font('black', 60); fs = font('bold', 30)
        tw = d.textlength(pr, font=f) + d.textlength('円', font=fs) + 6
        tx = x0 + (cw - tw) / 2
        d.text((tx, y + 104), pr, font=f, fill=WHITE)
        d.text((tx + d.textlength(pr, font=f) + 6, y + 132), '円', font=fs, fill=WHITE)
    y += 214
    d.text((W - X - d.textlength('（税込）', font=font('med', 32)), y), '（税込）', font=font('med', 32), fill=SUB)
    y += 56
    pill(img, X, y, '営業日まとめへの掲載は無料', size=44, outline=YELLOW, color=YELLOW)
    paste_logo(img, 80, 1210)
    save(img, OUT + '2026-12-04_受付終了まであと16日.jpg')


if __name__ == '__main__':
    i1126(); c1127(); c1129(); i1130(); c1201(); c1203(); i1204()
