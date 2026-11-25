# 案内文「見本付き版」（A・B）。build_letter.py を土台に、変わる所だけ差し替える。
# python3 build_letter_sample.py → letter_sample.html（元の letter.html は変えない）
import pathlib, re
D = pathlib.Path(__file__).parent
src = (D / "build_letter.py").read_text()

def rep(old, new):
    global src
    assert old in src, "見つからない: " + old[:60]
    src = src.replace(old, new)

# 追加のCSS
rep('<link rel="stylesheet" href="style.css">', '<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="style_sample.css">')

# 中ほどの欄：タグ・流れを引数に
rep('''def push(strong, span):
    return f"""<section class="push">
  <div class="tag">無料<b>見本</b></div>''', '''def push(strong, span, flow):
    fl = "".join(f"<li><i>{i+1}</i>{x}</li>" for i, x in enumerate(flow))
    return f"""<section class="push">
  <div class="tag">御社の<b>見本</b></div>''')
rep('''  <div class="lim">お申込み期限<b>＿＿月＿＿日まで</b></div>
  <ol class="flow"><li><i>1</i>お電話・QRでご連絡</li><li><i>2</i>2営業日以内にご連絡・無料で見本作成</li><li><i>3</i>見本を見てからご判断</li></ol>''',
    '''  <div class="row2"><ol class="flow">{fl}</ol><div class="lim">お申込み期限<b>＿＿月＿＿日まで</b></div></div>''')

# 右下：QRの貼り付け枠
rep('def cta(call):', 'def cta(call, qtxt):')
rep('''<div class="qrbox"><img src="qr-hp.svg" alt="無料見本お申込みページのQRコード"></div>
    <p>QRから<br>無料見本の<br>お申込み<small>24時間受付</small></p>''',
    '''<div class="qrbox paste" aria-label="QRコード貼り付け欄"></div>
    <p>{qtxt}<small>スマホのカメラで<br>読み取り</small></p>''')

rep('''</div>
</footer>"""''', '''</div>
  <p class="noqr">QRが読めない方は、お電話で<b>「見本を見たい」</b>とお伝えください。見本のアドレスをお送りします。</p>
</footer>"""''')

# B：比較図の下の一言を1行に（紙面の都合）
rep('今のページの文章や写真も、活かして作り直します。<br>今のドメインを使い続けたい場合もご相談ください。','今のページの文章や写真も、活かして作り直します。')

# A 左パネル：/demo/ QRを外して文字に
rep('<p class="phones-ttl">こんなホームページを、<br><em>御社の内容で</em>お作りします</p>',
    '<p class="phones-ttl">御社のホームページの見本、<br><em>できています</em></p>')
rep('''<div class="qcol"><div class="qrbox"><img src="qr-demo.svg" alt="見本サイトのQRコード"></div><p>見本サイトを<br>スマホで見る<small>業種別の見本</small></p></div>''',
    '''<div class="qcol go"><span class="arw">↓</span><p><em>いちばん下の<br>QRから</em></p><p><small>スマホのカメラで<br>読むだけ</small></p></div>''')

# A 見出し・リード
rep('<h1>お客さまは、来る前に「<em>スマホで調べて</em>」います。</h1>',
    '<h1>御社のホームページの<em>見本</em>を、ひとつお作りしました。</h1>')
rep('誌面やチラシで御社を知ったお客さまも、電話や来店の前に、まずスマホで名前を調べます。そのとき御社のページが出てくるように。日頃の感謝を込めて、掲載企業さまだけの特別価格をご用意しました。',
    'お客さまは、電話や来店の前に、まずスマホで御社の名前を調べます。日頃の感謝を込めて、御社のホームページの見本をひとつお作りしました。右下のQRコードから、スマホでご覧ください。')
# B 見出し・リード
rep('<h1>そのホームページ、「<em>御社のもの</em>」になっていますか？</h1>',
    '<h1 class="long">御社のホームページを「<em>作り直したら</em>」の見本を、お作りしました。</h1>')
rep('無料のブログや作成サービスは手軽で便利です。ただ、アドレスは御社のものにはなりません。御社名義のアドレスで、もっと信頼されるホームページにしませんか。',
    '日頃の感謝を込めて、今の御社のページを拝見し、作り直した場合の見本をひとつお作りしました。右下のQRコードから、今のページと見比べてみてください。')

# 中ほどの欄（A・B）
src = re.sub(r'\{push\("まずは無料で、.*?\)\}',
    '{push("すでに<em>御社の見本</em>をお作りしました。スマホでQRを読んで、ご覧ください。",'
    '"<b>見るだけ・お断りでも費用はかかりません。</b>文章や写真は仮のもので、打ち合わせで直してから公開します。見本は御社にご覧いただくためだけのもので、お申込み期限を過ぎたら削除します。",'
    '["QRで見本を見る","気に入ったらお電話","打ち合わせで直して公開"])}', src, count=1)
src = re.sub(r'\{push\("今のページを拝見して、.*?\)\}',
    '{push("今のページをもとに、<em>作り直した見本</em>をお作りしました。QRからご覧ください。",'
    '"<b>見るだけ・お断りでも費用はかかりません。</b>文章や写真は仮のもので、打ち合わせで直してから公開します。見本は御社にご覧いただくためだけのもので、お申込み期限を過ぎたら削除します。",'
    '["QRで今のページと見比べる","気に入ったらお電話","打ち合わせで直して公開"])}', src, count=1)

# お問い合わせ帯（A・B）
rep('{cta("お電話ひとつで大丈夫です。<em>「案内を見た」</em>とお伝えください。")}',
    '{cta("気になったらお電話ください。<em>「見本を見た」</em>とお伝えください。<small>こちらからお電話することはありません。見るだけでもかまいません。</small>","御社の<br>ホームページの<br><em>見本はこちら</em>")}')
rep('{cta("「今のページ、どうかな？」の<em>ご相談だけでも</em>大丈夫です。")}',
    '{cta("<em>「見本を見た」</em>のひとことで大丈夫です。ご相談だけでもどうぞ。<small>こちらからお電話することはありません。見るだけでもかまいません。</small>","作り直した<br>御社の見本は<br><em>こちら</em>")}')

rep('(D / "letter.html")', '(D / "letter_sample.html")')
assert "毎月先着3社" not in src and "2営業日以内" not in src and "qr-demo" not in src
exec(compile(src, "build_letter_sample", "exec"), {"__file__": str(D / "build_letter.py")})
