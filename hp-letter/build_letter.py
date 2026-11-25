# ホームページ案内文（A・B）の HTML を作る。python3 build_letter.py → letter.html
import pathlib
D = pathlib.Path(__file__).parent
LOGO = (D / "ref/logo-mark.svg").read_text()

HEAD = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>ホームページ案内文</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Outfit:wght@500;700&family=M+PLUS+Rounded+1c:wght@800&display=block" rel="stylesheet">
<link rel="stylesheet" href="style.css"></head><body>
"""

def header():
    return f"""<header class="hd">
  <div class="logo">{LOGO}<div>turtle <b>ad</b><small>合同会社turtle ad（タートルアド）</small></div></div>
  <div class="hd-badge">マイタウンガイド掲載企業さま限定のご案内</div>
</header>"""

ADDR = """<div class="addr"><div class="to">様</div><div class="date">令和　　年　　月　　日</div></div>"""

def icon(name):
    p = {
     "search": '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>',
     "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
     "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
     "people": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2c2.8.2 5 2.4 5 5.8"/>',
     "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/>',
     "home": '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
     "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
     "refresh": '<path d="M20 11a8 8 0 0 0-14.5-4.5L4 8M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.5 4.5L20 16M20 20v-4h-4"/>',
    }[name]
    return f'<svg viewBox="0 0 24 24">{p}</svg>'

def merit(n, ic, h, p):
    return f"""<div class="mt"><div class="mt-h"><div class="ic"><span class="n">{n}</span>{icon(ic)}</div><h3>{h}</h3></div><p>{p}</p></div>"""

def merit2(n, ic, h, p):
    return f"""<div class="mt"><div class="mt-h"><div class="ic"><span class="n">{n}</span>{icon(ic)}</div></div><div class="mt-b"><h3>{h}</h3></div></div>"""

def merit3(n, ic, h, p):
    return f"""<div class="mt"><div class="ic"><span class="n">{n}</span>{icon(ic)}</div><div class="mt-b"><h3>{h}</h3><p>{p}</p></div></div>"""

def price(title_extra=""):
    def card(name, old, new, pages, feat, mid=False):
        badge = '<span class="pl-badge">おすすめ</span>' if mid else ""
        return f"""<div class="pl{' mid' if mid else ''}">{badge}
  <p class="pl-name">{name}</p>
  <p class="pl-old">通常 <s>{old}円〜</s></p>
  <p class="pl-price">{new}<span>円〜</span></p>
  <p class="pl-pages">{pages}</p>
  <p class="pl-feat">{feat}</p>
</div>"""
    return f"""<section>
<div class="sec-h"><h2><span class="blank"></span>様だけの特別価格です<small>（すべて税込）</small></h2><span class="pl-lab big">掲載企業さま価格</span><span class="en">PRICE</span></div>
<div class="plans">
{card("ライト","55,000","33,000","TOP＋基本2ページ","SNSリンク")}
{card("スタンダード","88,000","55,000","TOP＋基本4〜5ページ","SNS連携／検索対策（基本）",True)}
{card("しっかり","132,000","88,000","TOP＋6〜8ページ","SNS連携／検索対策／ブログ機能")}
</div>
<p class="plans-note">どのプランも<b>スマホ対応・お問い合わせフォーム</b>込み。原稿づくり・写真撮影はオプション（別途お見積もり）。</p>
</section>"""

def monthly(h3, line=True):
    return f"""<section class="monthly">
  <div class="m-price"><p class="k">制作費とは別に</p><p class="v"><span class="pre">月々</span>5,500<span>円</span><small>（税込）</small></p><p class="s">ドメインは御社名義</p></div>
  <div class="m-body">
    <ul class="tags"><li>サーバー・ドメイン代</li><li>写真の差し替え・文章の変更</li><li>Googleマップの情報更新</li><li>WordPressの更新</li><li>セキュリティ対策・バックアップ</li></ul>
    <p>写真の差し替えや文章の変更は、<b>LINEで送るだけ</b>。パソコンが苦手でも安心。</p>
  </div>
  <p class="m-term">月額は<b>24か月のご利用が前提</b>です（24か月未満で解約の場合は5,500円×残りの月数）</p>
</section>"""

def push(strong, span):
    return f"""<section class="push">
  <div class="tag">無料<b>見本</b></div>
  <div class="t"><strong>{strong}</strong><span>{span}</span></div>
  <div class="lim">お申込み期限<b>＿＿月＿＿日まで</b></div>
  <ol class="flow"><li><i>1</i>お電話・QRでご連絡</li><li><i>2</i>2営業日以内にご連絡・無料で見本作成</li><li><i>3</i>見本を見てからご判断</li></ol>
</section>"""

TEL_SVG = '<svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>'

def cta(call):
    return f"""<footer class="cta">
  <div class="cta-l">
    <p class="call">{call}</p>
    <div class="tel"><div class="ti">{TEL_SVG}</div><b>099-210-3511</b><span>受付 9:00〜18:00<br>土日祝休み<br><em>info@turtle-ad.com</em></span></div>
    <p class="co"><b>合同会社turtle ad</b>　代表 見立 大作　〒891-0109 鹿児島市清和3-25-15</p>
  </div>
  <div class="cta-r"><div class="qrbox"><img src="qr-hp.svg" alt="無料見本お申込みページのQRコード"></div>
    <p>QRから<br>無料見本の<br>お申込み<small>24時間受付</small></p></div>
</footer>"""

FINE = """<p class="fine">※24か月以上のご利用で、サイトのデータ（ZIP）とドメインの移管手続きを無償でお渡しします。※ご解約は毎月25日までのご連絡で翌月分から停止します。※ページの追加・デザイン変更は別途お見積もりです。※特別価格はマイタウンガイド掲載企業さま限定です。詳しい条件は契約書に明記します。※同封のチラシでは、AI動画づくりもご紹介しています。</p>"""

PHONES = """<div class="phones">
  <p class="phones-ttl">こんなホームページを、<br><em>御社の内容で</em>お作りします</p>
  <div class="ph-row"><div class="stage">
    <div class="ph back"><div class="scr">
      <div class="bar" style="color:#1d3557"><span>御社名 工務店</span><i></i></div>
      <div class="hero"><svg viewBox="0 0 100 70" preserveAspectRatio="none"><rect width="100" height="70" fill="#1d3557"/><rect y="48" width="100" height="22" fill="#14263f"/><path d="M58 48V30l16-12 16 12v18z" fill="#e9eef5" opacity=".9"/><path d="M54 32l20-16 20 16" stroke="#f4a261" stroke-width="3" fill="none"/><rect x="69" y="36" width="9" height="12" fill="#1d3557"/><circle cx="18" cy="14" r="6" fill="#f4a261" opacity=".8"/></svg><p>住まいの困った、<br>すぐ伺います<small>地域密着で30年</small></p></div>
      <div class="btns"><span style="background:#f4a261">施工事例</span><span style="background:#1d3557">無料見積り</span></div>
      <div class="row"><b style="background:#c9d6e6"></b><span><i></i><i></i></span></div>
      <div class="row"><b style="background:#e6d3c2"></b><span><i></i><i></i></span></div>
      <div class="row"><b style="background:#d4e2d4"></b><span><i></i><i></i></span></div>
    </div></div>
    <div class="ph front"><div class="scr">
      <div class="bar" style="color:#7a4a2a"><span>御社名 食堂</span><i></i></div>
      <div class="hero"><svg viewBox="0 0 100 70" preserveAspectRatio="none"><defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6c28b"/><stop offset="1" stop-color="#d9824b"/></linearGradient></defs><rect width="100" height="70" fill="url(#sk)"/><rect x="12" y="30" width="76" height="40" fill="#5b3a29"/><path d="M8 30h84l-6-12H14z" fill="#c0392b"/><path d="M14 18h12l-2 12H8zM38 18h12v12H36zM62 18h12l2 12H64z" fill="#fff" opacity=".85"/><rect x="22" y="40" width="22" height="18" rx="1" fill="#f7d9a8"/><rect x="56" y="40" width="22" height="30" rx="1" fill="#3b2418"/><circle cx="74" cy="56" r="1.4" fill="#f7d9a8"/></svg><p>毎日食べたい、<br>まちの定食屋<small>11:00〜20:00　水曜定休</small></p></div>
      <div class="btns"><span style="background:#c0392b">電話する</span><span style="background:#2a9d8f">地図を見る</span></div>
      <div class="row"><b style="background:#f2c48d"></b><span><i></i><i></i></span></div>
      <div class="row"><b style="background:#e8a87c"></b><span><i></i><i></i></span></div>
      <div class="map"></div>
    </div></div>
  </div>
  <div class="qcol"><div class="qrbox"><img src="qr-demo.svg" alt="見本サイトのQRコード"></div><p>見本サイトを<br>スマホで見る<small>業種別の見本</small></p></div></div>
</div>"""

PAGE_A = f"""<div class="page" id="A">
{header()}
<main class="body">
{ADDR}
<section>
  <h1>お客さまは、来る前に「<em>スマホで調べて</em>」います。</h1>
  <p class="sub">御社のホームページ、<b>33,000</b>円（税込）からお作りします。<small class="plus">＋月々5,500円（税込）</small></p>
  <p class="lead">いつもマイタウンガイドにご掲載いただき、ありがとうございます。誌面やチラシで御社を知ったお客さまも、電話や来店の前に、まずスマホで名前を調べます。そのとき御社のページが出てくるように。日頃の感謝を込めて、掲載企業さまだけの特別価格をご用意しました。</p>
</section>
<section class="show">
{PHONES}
  <div class="merits3">
    {merit3(1,"search","調べたときに、ちゃんと出てくるように","名前で調べて何も出ないと、お客さまは不安になります。")}
    {merit3(2,"moon","お休みの日も夜中も、御社を案内","メニュー・料金・地図を、いつでも見てもらえます。")}
    {merit3(3,"phone","同じ説明の電話が減る","よくある質問をのせれば、電話の前に分かっていただけます。")}
  </div>
</section>
{price()}
{monthly("作ったあとも、まかせて安心")}
{push("まずは無料で、<em>御社のトップページの見本</em>をお見せします","<b>毎月先着3社まで。</b>※見本は打ち合わせ用です（そのまま公開はできません）。")}
</main>
{cta("お電話ひとつで大丈夫です。<em>「案内を見た」</em>とお伝えください。")}
{FINE}
</div>"""

PAGE_B = f"""<div class="page pB" id="B">
{header()}
<main class="body">
{ADDR}
<section>
  <h1>そのホームページ、「<em>御社のもの</em>」になっていますか？</h1>
  <p class="sub">御社名義のアドレスで、もっと信頼されるホームページに。<span class="br"></span><b>33,000</b>円（税込）から。<small class="plus">＋月々5,500円（税込）</small></p>
  <p class="lead">いつもマイタウンガイドにご掲載いただき、ありがとうございます。無料のブログや作成サービスは手軽で便利です。ただ、アドレスは御社のものにはなりません。御社名義のアドレスで、もっと信頼されるホームページにしませんか。</p>
</section>
<section class="check-wrap">
  <div class="check"><h3>ひとつでも当てはまったら、<em>見直しどき</em>です</h3>
    <ul><li>アドレスに無料サービスの名前が入っている</li><li>ページに、知らない広告が出る</li><li>スマホで見ると、文字が小さい・崩れる</li><li>「保護されていない通信」と出る</li><li>何年も更新していない</li><li>作った業者に連絡がつかない・直し方が分からない</li></ul>
  </div>
  <div class="ba">
    <div class="url old"><span class="lb">いま</span><span>〇〇blog.jp/user/〇〇〇</span><span class="ad">広告</span></div>
    <div class="arrow">▼</div>
    <div class="url new"><span class="lb">これから</span><span>www.<em>御社名</em>.jp</span></div>
    <p>アドレスだけで「<em>しっかりした会社</em>」だと伝わります。</p>
    <p class="r">今のページの文章や写真も、活かして作り直します。<br>今のドメインを使い続けたい場合もご相談ください。</p>
  </div>
</section>
<section class="merits4">
  {merit2(1,"globe","アドレスだけで、<br>信用が変わる","名刺やチラシでの印象が、まったく違います。")}
  {merit2(2,"home","突然消える<br>心配が少ない","ドメインは御社名義なので安心です。")}
  {merit2(3,"shield","セキュリティ対策・<br>バックアップ込み","WordPressの更新も、月額に込みです。")}
  {merit2(4,"refresh","いつも<br>新しい情報に","写真や文章の変更は、LINEで送るだけ。")}
</section>
{price()}
{monthly("作り直したあとも、まかせて安心")}
{push("今のページを拝見して、<em>作り直した場合の見本</em>を無料でお見せします","<b>毎月先着3社まで。</b>※見本は打ち合わせ用です（そのまま公開はできません）。")}
</main>
{cta("「今のページ、どうかな？」の<em>ご相談だけでも</em>大丈夫です。")}
{FINE}
</div>"""

(D / "letter.html").write_text(HEAD + PAGE_A + "\n" + PAGE_B + "\n</body></html>\n")
print("ok")
