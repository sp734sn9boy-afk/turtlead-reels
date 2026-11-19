import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from tad import *

OUT = '/home/user/turtlead-reels/img/turtle_ad/2026-11/'
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350
X = 80
MW = W - 2 * X


def base(seed, label, i=None, n=None, nodes=True):
    img = background(W, H, seed, nodes)
    eyebrow(img, X, 104, label)
    if i:
        page_num(img, i, n)
    paste_logo(img, 80, 1190)
    return img


# ---------- 11/22 カルーセル：古いホームページ チェック7 ----------
def c1122():
    n = 9
    img = base(22, 'HOMEPAGE CHECK', nodes=True)
    y = 230
    y = text_block(img, X, y, 'そのホームページ、', 'black', 96, maxw=MW, lh=1.3)
    y = text_block(img, X, y, '古くないですか？', 'black', 110, maxw=MW, lh=1.3, grad=True)
    y += 40
    card(img, (X, y, W - X, y + 230), glow=True)
    text_block(img, X + 50, y + 40, 'あてはまる数を\n数えてみてください', 'bold', 60, maxw=MW - 100, lh=1.4)
    y += 290
    pill(img, X, y, 'チェック 7項目', size=46, outline=YELLOW, color=YELLOW)
    swipe_hint(img, 'スワイプしてね →', y=1210)
    save(img, OUT + '2026-11-22_HPチェック7_01.jpg')

    items = [
        'スマホで見ると\n文字が小さい・\n横にはみ出す',
        '営業時間・定休日が\n今と違う',
        '「お知らせ」の\n最終更新が\n1年以上前',
        'アドレスの横に\n鍵マークがない\n（https になっていない）',
        'スマホで電話番号を\n押しても\n電話がかからない',
        '地図・アクセスが\n載っていない',
        '写真が\n何年も前のまま',
    ]
    for k, t in enumerate(items):
        img = base(22 + k + 1, f'CHECK {k + 1:02d}', k + 2, n, nodes=False)
        d = ImageDraw.Draw(img)
        # 大きな番号（うすく）
        d.text((W - 430, 170), f'{k + 1:02d}', font=font('black', 300), fill=(30, 46, 90))
        checkbox(img, X, 420, size=130)
        size = 86 if 'https' not in t else 76
        y = text_block(img, X, 620, t, 'black', size, maxw=MW, lh=1.38)
        d.text((X, 1090), 'あてはまったら □ に1つ数えてください', font=font('med', 34), fill=SUB)
        save(img, OUT + f'2026-11-22_HPチェック7_{k + 2:02d}.jpg')

    img = base(40, 'RESULT', 9, n)
    y = 260
    y = text_block(img, X, y, '3つ以上', 'black', 150, maxw=MW, lh=1.2, grad=True)
    y = text_block(img, X, y, 'あてはまったら、\n見直しどきです', 'black', 90, maxw=MW, lh=1.35)
    y += 70
    card(img, (X, y, W - X, y + 190), glow=True)
    text_block(img, X, y + 30, '相談は無料', 'black', 62, maxw=MW, align='center', fill=YELLOW)
    text_block(img, X, y + 112, 'プロフィールのリンクから', 'bold', 44, maxw=MW, align='center')
    save(img, OUT + '2026-11-22_HPチェック7_09.jpg')


# ---------- 11/23 画像：年末年始のお知らせ ----------
def i1123():
    img = background(W, H, 23)
    eyebrow(img, X, 96, 'NEW YEAR HOLIDAY')
    y = 200
    y = text_block(img, X, y, '年末年始のお休み、', 'black', 82, maxw=MW, lh=1.3)
    y = text_block(img, X, y, 'お客様に', 'black', 82, maxw=MW, lh=1.3)
    y = text_block(img, X, y, '届いていますか？', 'black', 96, maxw=MW, lh=1.3, grad=True)
    y += 26
    y = text_block(img, X, y, '店頭のお知らせ・POP・SNS画像を\nお作りします', 'bold', 46, maxw=MW, lh=1.45, fill=SUB)
    y += 34
    rows = [('梅', '3,500'), ('竹', '5,500'), ('松', '8,000')]
    cw = (MW - 40) // 3
    for k, (a, p) in enumerate(rows):
        x0 = X + k * (cw + 20)
        card(img, (x0, y, x0 + cw, y + 230), glow=(k == 2), outline=(CYAN if k == 2 else (60, 80, 130)))
        text_block(img, x0, y + 20, a, 'black', 66, maxw=cw, align='center', fill=YELLOW)
        d = ImageDraw.Draw(img)
        f = font('black', 64)
        fs = font('bold', 32)
        tw = d.textlength(p, font=f) + d.textlength('円', font=fs) + 6
        tx = x0 + (cw - tw) / 2
        d.text((tx, y + 120), p, font=f, fill=WHITE)
        d.text((tx + d.textlength(p, font=f) + 6, y + 150), '円', font=fs, fill=WHITE)
    y += 250
    d = ImageDraw.Draw(img)
    d.text((W - X - d.textlength('（税込）', font=font('med', 32)), y), '（税込）', font=font('med', 32), fill=SUB)
    y += 60
    b1 = pill(img, X, y, '受付 12/20まで', size=44, outline=YELLOW, color=YELLOW)
    pill(img, b1[2] + 20, y, '営業日まとめへの掲載は無料', size=36, pady=22)
    paste_logo(img, 80, 1210)
    save(img, OUT + '2026-11-23_年末年始お知らせ制作.jpg')


# ---------- 11/24 カルーセル：AIでお知らせ文 ----------
def c1124():
    n = 5
    img = base(24, 'AI HOW-TO')
    y = 230
    y = text_block(img, X, y, '年末年始の\nお知らせ文、', 'black', 100, maxw=MW, lh=1.3)
    y = text_block(img, X, y, 'AIに作ってもらう', 'black', 96, maxw=MW, lh=1.3, grad=True)
    y = text_block(img, X, y, '頼み方', 'black', 100, maxw=MW, lh=1.3)
    y += 40
    pill(img, X, y, 'そのまま使える頼み方つき', size=44, outline=YELLOW, color=YELLOW)
    swipe_hint(img, 'スワイプしてね →', y=1210)
    save(img, OUT + '2026-11-24_AIお知らせ文の頼み方_01.jpg')

    img = base(25, 'STEP 1', 2, n, nodes=False)
    y = text_block(img, X, 230, '① お店の情報を\n先に渡す', 'black', 88, maxw=MW, lh=1.35)
    y += 50
    for t in ['店名', '最終営業日', '営業開始日', '時間が変わる日']:
        card(img, (X, y, W - X, y + 120))
        checkbox(img, X + 34, y + 25, size=70, checked=True)
        ImageDraw.Draw(img).text((X + 140, y + 22), t, font=font('bold', 56), fill=WHITE)
        y += 140
    save(img, OUT + '2026-11-24_AIお知らせ文の頼み方_02.jpg')

    img = base(26, 'STEP 2', 3, n, nodes=False)
    y = text_block(img, X, 220, '② こう頼む', 'black', 88, maxw=MW, lh=1.3)
    y = text_block(img, X, y, '（そのまま使えます）', 'bold', 48, maxw=MW, fill=YELLOW)
    y += 30
    prompt = ('次の内容で、店頭に貼る年末年始のお知らせ文を、やさしい言葉で3案作ってください。\n'
              '店名：〇〇\n最終営業日：12月〇日\n営業開始日：1月〇日\n一言：今年もありがとうございました')
    hh = len(wrap(prompt, font('bold', 46), MW - 100)) * int(46 * 1.55) + 70
    card(img, (X, y, W - X, y + hh), fill=(240, 244, 252), outline=CYAN, width=4)
    text_block(img, X + 50, y + 34, prompt, 'bold', 46, fill=(16, 24, 52), maxw=MW - 100, lh=1.55)
    save(img, OUT + '2026-11-24_AIお知らせ文の頼み方_03.jpg')

    img = base(27, 'STEP 3', 4, n, nodes=False)
    y = text_block(img, X, 240, '③ できた文は、', 'black', 88, maxw=MW, lh=1.35)
    y = text_block(img, X, y, '日付と曜日を', 'black', 100, maxw=MW, lh=1.3, grad=True)
    y = text_block(img, X, y, '必ず自分で確認', 'black', 100, maxw=MW, lh=1.3)
    y += 60
    card(img, (X, y, W - X, y + 170), outline=YELLOW)
    text_block(img, X + 40, y + 34, 'AIは日付や曜日を\nまちがえることがあります', 'bold', 44, maxw=MW - 80, lh=1.4, fill=YELLOW)
    save(img, OUT + '2026-11-24_AIお知らせ文の頼み方_04.jpg')

    img = base(28, 'TURTLE AD', 5, n)
    y = text_block(img, X, 240, '作る時間がない\nお店は、', 'black', 96, maxw=MW, lh=1.3)
    y = text_block(img, X, y, 'お作りします', 'black', 110, maxw=MW, lh=1.3, grad=True)
    y += 60
    card(img, (X, y, W - X, y + 260), glow=True)
    text_block(img, X, y + 36, '梅 3,500円〜', 'black', 80, maxw=MW, align='center', fill=YELLOW)
    text_block(img, X, y + 160, '（税込）受付 12/20まで', 'bold', 46, maxw=MW, align='center')
    save(img, OUT + '2026-11-24_AIお知らせ文の頼み方_05.jpg')


if __name__ == '__main__':
    c1122(); i1123(); c1124()
