# 案内文 第3版（見本付き・スタンダード1本）A・B。
# 見本付き版（build_letter_sample.py）の部品を土台に、ページの中身を組み直す。
# python3 build_letter_v3.py → letter_v3.html（ほかの版のファイルは変えない）
import pathlib
D = pathlib.Path(__file__).parent

# 見本付き版の差し替え済みソースを取り出す（書き出しはしない）
code = (D / "build_letter_sample.py").read_text()
code = code.replace('exec(compile(src, "build_letter_sample", "exec"), {"__file__": str(D / "build_letter.py")})', '')
ns = {"__file__": str(D / "build_letter_sample.py")}
exec(compile(code, "build_letter_sample", "exec"), ns)
src = ns["src"]
src = src[:src.index('PAGE_A = f"""')]   # 部品（HEAD・関数・PHONES など）だけ使う
src = src.replace('<link rel="stylesheet" href="style_sample.css">',
                  '<link rel="stylesheet" href="style_sample.css"><link rel="stylesheet" href="style_v3.css">')
g = {"__file__": str(D / "build_letter.py")}
exec(compile(src, "parts", "exec"), g)
header, icon, merit3, push, cta, ADDR, HEAD = (g[k] for k in ("header", "icon", "merit3", "push", "cta", "ADDR", "HEAD"))

# 左パネル：枠の下に一言（スタンダード内容）
PHONES = g["PHONES"]
i = PHONES.rindex("</div>")
PHONES = PHONES[:i] + '<p class="std-cap">見本は<b>検索対策込みのスタンダード</b>内容です</p>' + PHONES[i:]

def check_ic():
    return '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'

def price3():
    items = ["トップページ＋基本4〜5ページ", "スマホ対応", "お問い合わせフォーム", "SNS連携",
             "検索対策<small>（検索で見つけてもらうための基本設定）</small>"]
    lis = "".join(f'<li class="{"wide" if k == 0 else ""}">{check_ic()}<span>{x}</span></li>' for k, x in enumerate(items))
    return f"""<section class="price3">
<div class="sec-h"><h2><span class="blank"></span>様だけの特別価格です<small>（税込）</small></h2><span class="pl-lab big">掲載企業さま価格</span><span class="en">PRICE</span></div>
<div class="pcard">
  <span class="pc-badge">見本と同じプラン</span>
  <div class="pc-l">
    <p class="pc-name">スタンダードプラン<span class="chip">検索対策込み</span></p>
    <p class="pc-old">通常 <s>88,000円〜</s></p>
    <p class="pc-price">55,000<span>円〜</span><small>（税込）</small></p>
    <p class="pc-mon">＋月々 <b>5,500</b>円（税込）</p>
  </div>
  <ul class="pc-r">{lis}</ul>
</div>
<p class="plans-note">原稿づくり・写真撮影はオプション（別途お見積もり）です。ほかのプランもご用意しています。お気軽にご相談ください。</p>
</section>"""

def domain(title, items):
    cells = "".join(f'<li><span class="di">{icon(ic)}</span><b>{h}</b></li>' for ic, h in items)
    return f"""<section class="dom"><div class="dom-h">{title}</div><ul class="dom-l">{cells}</ul></section>"""

def monthly3(line):
    return f"""<section class="monthly">
  <div class="m-price"><p class="k">制作費とは別に</p><p class="v"><span class="pre">月々</span>5,500<span>円</span><small>（税込）</small></p><p class="s">ドメインは御社名義</p></div>
  <div class="m-body">
    <ul class="tags"><li>サーバー・ドメイン代</li><li>写真の差し替え・文章の変更</li><li>Googleマップの情報更新</li><li>WordPressの更新</li><li>セキュリティ対策・バックアップ</li></ul>
    <p>{line}</p>
  </div>
  <p class="m-term">月額は<b>24か月のご利用が前提</b>です（24か月未満で解約の場合は5,500円×残りの月数）</p>
</section>"""

FINE = """<p class="fine">※価格はすべて税込です。※制作費とは別に月額5,500円（税込）のご契約が必要です。※ドメインは御社名義でお取りします（取得・更新の費用は月額に含みます）。※24か月以上のご利用で、サイトのデータ（ZIP）とドメインの移管手続きを無償でお渡しします。※ご解約は毎月25日までのご連絡で翌月分から停止します。※ページの追加・デザイン変更は別途お見積もりです。※特別価格はマイタウンガイド掲載企業さま限定です。詳しい条件は契約書に明記します。※同封のチラシでは、AI動画づくりもご紹介しています。</p>"""

SPAN = ('お作りした見本は、<b>検索対策込みのスタンダードプラン（55,000円〜）の内容</b>です。'
        '<b>見るだけ・お断りでも費用はかかりません。</b>文章や写真は仮のもので、打ち合わせで直してから公開します。'
        '')
CALL2 = '<small>こちらからお電話することはありません。見るだけでもかまいません。</small>'

PAGE_A = f"""<div class="page v3" id="A">
{header()}
<main class="body">
{ADDR}
<section>
  <h1>御社のホームページの<em>見本</em>を、ひとつお作りしました。</h1>
  <p class="sub">御社のホームページ、<b>55,000</b>円（税込）からお作りします。<small class="plus">＋月々5,500円（税込）</small></p>
  <p class="lead">いつもマイタウンガイドにご掲載いただき、ありがとうございます。お客さまは、電話や来店の前に、まずスマホで御社の名前を調べます。日頃の感謝を込めて、御社のホームページの見本をひとつお作りしました。右下のQRコードから、スマホでご覧ください。</p>
</section>
<section class="show">
{PHONES}
  <div class="merits3">
    {merit3(1,"search","調べたときに、ちゃんと出てくるように","名前で調べて何も出ないと、お客さまは不安になります。")}
    {merit3(2,"moon","お休みの日も夜中も、御社を案内","メニュー・料金・地図を、いつでも見てもらえます。")}
    {merit3(3,"phone","同じ説明の電話が減る","よくある質問をのせれば、電話の前に分かっていただけます。")}
  </div>
</section>
{domain('<b>「www.<em>御社名</em>.jp」</b>自社のアドレスを持つと、信用が変わります', [
  ("globe","名刺・チラシ・誌面で、きちんとした印象に"),
  ("people","取引先・求人の応募者・金融機関にも安心を"),
  ("home","御社名義の「財産」として残る"),
  ("shield","突然消える心配が少ない")])}
{price3()}
{monthly3("写真の差し替えや文章の変更は、<b>LINEで送るだけ</b>。パソコンが苦手でも安心。")}
{push("すでに<em>御社の見本</em>をお作りしました。スマホでQRを読んで、ご覧ください。", SPAN, ["QRで見本を見る","気に入ったらお電話","打ち合わせで直して公開"])}
</main>
{cta("気になったらお電話ください。<em>「見本を見た」</em>とお伝えください。" + CALL2, "御社の<br>ホームページの<br><em>見本はこちら</em>")}
{FINE}
</div>"""

PAGE_B = f"""<div class="page pB v3" id="B">
{header()}
<main class="body">
{ADDR}
<section>
  <h1 class="long">御社のホームページを「<em>作り直したら</em>」の見本を、お作りしました。</h1>
  <p class="sub">御社名のアドレスで、もっと信頼されるホームページに。<span class="br"></span><b>55,000</b>円（税込）から。<small class="plus">＋月々5,500円（税込）</small></p>
  <p class="lead">いつもマイタウンガイドにご掲載いただき、ありがとうございます。日頃の感謝を込めて、今の御社のページを拝見し、御社名のアドレスで作り直した場合の見本をひとつお作りしました。右下のQRコードから、今のページと見比べてみてください。</p>
</section>
<section class="check-wrap">
  <div class="check"><h3>ひとつでも当てはまったら、<em>見直しどき</em>です</h3>
    <ul><li>アドレスに、無料サービスや他社の名前が入っている</li><li>ページに、知らない広告が出る</li><li>スマホで見ると、文字が小さい・崩れる</li><li>「保護されていない通信」と出る</li><li>何年も更新していない</li><li>直したいとき、どこに頼めばいいか分からない</li></ul>
  </div>
  <div class="ba">
    <div class="url old"><span class="lb">いま</span><span>〇〇blog.jp/user/〇〇〇</span><span class="ad">広告</span></div>
    <div class="arrow">▼</div>
    <div class="url new"><span class="lb">これから</span><span>www.<em>御社名</em>.jp</span></div>
    <p>アドレスだけで「<em>しっかりした会社</em>」だと伝わります。</p>
    <p class="r">今のページの文章や写真も、活かして作り直します。<br>今お持ちのドメインを使い続けたい場合もご相談ください。</p>
  </div>
</section>
{domain('<b>今のアドレスと、</b>ここが違います', [
  ("globe","アドレスだけで、信用が変わる"),
  ("home","借りものではなく、御社の財産に"),
  ("shield","突然消える心配が少ない"),
  ("people","取引先・求人にも安心感")])}
{price3()}
{monthly3("作り直したあとも、写真や文章の変更は<b>LINEで送るだけ</b>。ほったらかしにしません。")}
{push("今のページをもとに、<em>作り直した見本</em>をお作りしました。QRからご覧ください。", SPAN, ["QRで今のページと見比べる","気に入ったらお電話","打ち合わせで直して公開"])}
</main>
{cta("<em>「見本を見た」</em>のひとことで大丈夫です。ご相談だけでもどうぞ。" + CALL2, "作り直した<br>御社の見本は<br><em>こちら</em>")}
{FINE}
</div>"""

out = HEAD + PAGE_A + "\n" + PAGE_B + "\n</body></html>\n"
for bad in ("33,000", "132,000", "ライトプラン", "しっかりプラン", "毎月先着3社", "2営業日以内", "月額は任意", "49,000", "最短7日"):
    assert bad not in out, bad
(D / "letter_v3.html").write_text(out)
print("ok")
