# -*- coding: utf-8 -*-
"""Body Salon RISE 試作サイトの書き出し用スクリプト。
共通のヘッダー・フッター・予約欄・構造化データをまとめて、
index.html と 4本柱のページ（diet/ seitai/ ikumou/ hada/）を書き出します。

使い方:  python3 sites/rise/_src/build.py
本番公開時: BASE_URL に本番ドメイン（例 https://〇〇.jp/）を入れて書き出し直すと、
canonical・og:url・og:image・構造化データのURLが絶対URLになります。noindex も NOINDEX=False で外れます。
"""
import json, os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

BASE_URL = ""      # 本番ドメインに置き換え（末尾は / ）。空のあいだは相対パスで出力
NOINDEX = True     # 試作のあいだは True（検索に出さない）。本番公開時に False

LINE_IBU = "https://lin.ee/f8p4RiD"
LINE_TANI = "https://lin.ee/Wqf1iIA"
IG_IBU = "https://www.instagram.com/wada.ibusuki/"
IG_TANI = "https://www.instagram.com/taniyama.diet/"

KW = "マイタウンを見た"

SHOPS = {
    "ibu": dict(name="指宿院", full="Body Salon RISE 指宿院", zip="891-0401", region="鹿児島県", city="指宿市",
                street="大牟礼3丁目25-23-1", addr="鹿児島県指宿市大牟礼3丁目25-23-1", addr_q="鹿児島県指宿市大牟礼3丁目25-23-1", short="指宿市大牟礼 3-25-23-1",
                tel="080-4279-2503", telh="08042792503", line=LINE_IBU, ig=IG_IBU, igname="@wada.ibusuki",
                hours="10:00～19:00（完全予約制）", closed="日曜・祝日", chief="和田 諒真（柔道整復師）",
                extra="指宿駅から車で約3分／駐車場3台",
                map="https://www.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E7%9C%8C%E6%8C%87%E5%AE%BF%E5%B8%82%E5%A4%A7%E7%89%9F%E7%A4%BC3%E4%B8%81%E7%9B%AE25-23-1&output=embed",
                spec=[dict(d=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], o="10:00", c="19:00")]),
    "tani": dict(name="谷山院", full="Body Salon RISE 谷山院", zip="891-0114", region="鹿児島県", city="鹿児島市",
                 street="小松原1丁目48-11 SEAGREEN小松原102号", addr='鹿児島県鹿児島市小松原1丁目48-11 <span class="ib">SEAGREEN 小松原102号</span>', addr_q="鹿児島県鹿児島市小松原1丁目48-11",
                 short='<span class="ib">鹿児島市小松原 1-48-11</span> <span class="ib">SEAGREEN 小松原 102 号</span>',
                 tel="070-2376-8715", telh="07023768715", line=LINE_TANI, ig=IG_TANI, igname="@taniyama.diet",
                 hours="平日 9:30～19:00／土曜 9:30～18:00（完全予約制）", closed="日曜・祝日", chief="和田 一真（作業療法士）",
                 extra="鹿児島市谷山エリア",
                 map="https://www.google.com/maps?q=%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82%E5%B0%8F%E6%9D%BE%E5%8E%9F1-48-11&output=embed",
                 spec=[dict(d=["Monday","Tuesday","Wednesday","Thursday","Friday"], o="09:30", c="19:00"),
                       dict(d=["Saturday"], o="09:30", c="18:00")]),
}

PILLARS = [
    dict(key="diet", no="01", label="体質改善", name="ダイエット", pill="食事と習慣から体質を整える",
         img="ai-waist.jpg", pos="62% 45%", card="ai-food.jpg", cardpos="50% 40%",
         alt="ウエストにメジャーを当てる女性（ダイエットのイメージ）",
         cardalt="和食をおいしそうに食べる女性（食事の見直しのイメージ）",
         desc="遺伝子検査で体質を知り、整体と食事の見直しで、きつい運動や我慢の食事制限に頼らないダイエットを目指します。",
         chips=["遺伝子検査", "栄養指導", "3ヶ月コース"]),
    dict(key="seitai", no="02", label="からだケア", name="整体", pill="腰痛・肩こり・膝痛・ブライダル",
         img="r-treat3.jpg", pos="40% 40%", card="r-treat2.jpg", cardpos="50% 30%",
         alt="ひざの施術をする院長（整体のイメージ）",
         cardalt="うつぶせのお客様の脚を調整する施術の様子",
         desc="腰痛・肩こり・膝の痛み、骨盤や姿勢のゆがみに。国家資格をもつ院長が、体の土台から整えます。",
         chips=["腰痛・肩こり", "骨盤矯正", "ブライダル整体"]),
    dict(key="ikumou", no="03", label="頭皮ケア", name="育毛", pill="髪と頭皮のお悩みに",
         img="ikumou.jpg", pos="30% 40%", card="ikumou.jpg", cardpos="42% 30%",
         alt="頭皮ケアを受けるロングヘアの女性（育毛・頭皮ケアのイメージ）",
         cardalt="スタッフに頭皮を確かめてもらう女性（頭皮ケアのイメージ）",
         desc="髪のボリュームや頭皮の状態など、相談しにくいお悩みに。カウンセリングで状態を確かめてからご提案します。",
         chips=["頭皮の状態チェック", "頭皮ケア", "生活習慣の相談"]),
    dict(key="hada", no="04", label="フェイシャル", name="肌質改善", pill="お肌のお悩みに",
         img="hada.jpg", pos="45% 40%", card="hada.jpg", cardpos="62% 40%",
         alt="フェイシャルケアを受けてリラックスする女性（肌質改善のイメージ）",
         cardalt="フェイシャルケアを受ける女性（肌質改善のイメージ）",
         desc="乾燥やくすみ、年齢とともに感じる肌の変化に。今の肌の状態をていねいに確かめ、ケアの進め方をご提案します。",
         chips=["肌の状態チェック", "フェイシャルケア", "生活習慣の相談"]),
]
P = {p["key"]: p for p in PILLARS}

ICON_CHAT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3C6.5 3 2 6.6 2 11c0 2.6 1.6 4.9 4 6.4V21l3.6-2.2c.8.1 1.6.2 2.4.2 5.5 0 10-3.6 10-8s-4.5-8-10-8Zm-4 9.3a1.3 1.3 0 1 1 0-2.6 1.3 1.3 0 0 1 0 2.6Zm4 0a1.3 1.3 0 1 1 0-2.6 1.3 1.3 0 0 1 0 2.6Zm4 0a1.3 1.3 0 1 1 0-2.6 1.3 1.3 0 0 1 0 2.6Z"/></svg>'
ICON_TEL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1l-2.3 2.2Z"/></svg>'
ICON_CAM = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="#e9cf8a" stroke-width="2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="#e9cf8a" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2" fill="#e9cf8a"/></svg>'


def url(path):
    """BASE_URL があれば絶対URL、なければ相対（そのページから見たパス）を返す"""
    return BASE_URL + path if BASE_URL else None


def kw_ribbon():
    return f'<p class="kw">ご予約・ご来店の際に<b>「{KW}」</b>とお伝えください</p>'


def kw_mini():
    return f'<span class="kw-mini"><span class="ib">ご予約時に<b>「{KW}」</b></span><span class="ib">とお伝えください</span></span>'


def head(r, title, desc, path, og_img, ld):
    canon = url(path)
    canon_html = (f'<link rel="canonical" href="{canon}">' if canon else
                  f'<!-- 本番公開時：canonical・og:url を本番ドメインの絶対URLに置き換え（_src/build.py の BASE_URL） -->\n'
                  f'<link rel="canonical" href="{r}{path}">')
    ogimg = url(og_img) or (r + og_img)
    ogurl = canon or (r + path)
    robots = ('<!-- 試作のため検索に出さない設定。本番公開時に外す（_src/build.py の NOINDEX=False） -->\n'
              '<meta name="robots" content="noindex,nofollow">' if NOINDEX else '')
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}
<title>{title}</title>
<meta name="description" content="{desc}">
{canon_html}
<meta property="og:type" content="{'website' if path == '' else 'article'}">
<meta property="og:site_name" content="Body Salon RISE">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{ogurl}">
<meta property="og:image" content="{ogimg}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1d5a3e">
<link rel="icon" href="{r}img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&family=Noto+Serif+JP:wght@600;900&family=Cormorant+Garamond:ital,wght@1,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/rise.css">
<script>document.documentElement.classList.add('js')</script>
<!-- 構造化データ。本番公開時は url・image が本番ドメインの絶対URLになるよう BASE_URL を設定して書き出し直す -->
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
'''


def header(r, cur):
    items = [("diet/", "ダイエット", "diet"), ("seitai/", "整体", "seitai"), ("ikumou/", "育毛", "ikumou"),
             ("hada/", "肌質改善", "hada"), ("#staff" if cur == "top" else "./#staff", "院長紹介", None),
             ("#access", "アクセス", None)]
    lis = []
    for href, label, key in items:
        if href.startswith("#") or href.startswith("./#"):
            h = href if cur == "top" else (r + "#" + href.split("#")[1])
            if label == "アクセス":
                h = "#access"
        else:
            h = r + href
        ac = ' aria-current="page"' if key == cur else ''
        lis.append(f'<li><a href="{h}"{ac}>{label}</a></li>')
    lis.append('<li><a href="#yoyaku">ご予約</a></li>')
    home = "./" if cur == "top" else r
    return f'''<header class="hdr">
 <div class="in">
  <a class="logo" href="{home}" aria-label="Body Salon RISE ホームへ"><img src="{r}img/logo.png" alt="Body Salon RISE" width="225" height="32"></a>
  <nav class="gnav" id="gnav" aria-label="メインメニュー"><ul>{''.join(lis)}</ul></nav>
  <a class="btn btn-green cta" href="#yoyaku">LINEで予約</a>
  <button class="menu-btn" type="button" aria-controls="gnav" aria-expanded="false" aria-label="メニューを開く"><span></span><span></span><span></span></button>
 </div>
</header>
'''


def line_btn(shop, label=None):
    s = SHOPS[shop]
    return f'<a class="btn btn-line" href="{s["line"]}" target="_blank" rel="noopener">{ICON_CHAT}{label or s["name"] + "のLINEで予約"}</a>'


def yoyaku(r, title='<span class="ib">ご予約・ご相談は、</span><span class="ib">LINEがかんたんです</span>'):
    cards = []
    for k in ("ibu", "tani"):
        s = SHOPS[k]
        cards.append(f'''<div class="yc">
   <h3>{s["name"]}</h3>
   <p class="ad">{s["short"]}</p>
   {line_btn(k)}
   {kw_mini()}
   <div class="sub">
    <a class="btn btn-ghost" href="tel:{s["telh"]}">{ICON_TEL}{s["tel"]}</a>
    <a class="btn btn-ghost" href="{s["ig"]}" target="_blank" rel="noopener">Instagram</a>
   </div>
   <p class="hr">営業時間 {s["hours"]}<br>定休日 {s["closed"]}</p>
  </div>''')
    return f'''<section class="yoyaku on-dark" id="yoyaku">
 <div class="wrap">
  <div class="sh"><span class="en">Reservation</span><h2>{title}</h2><p>通いやすい院の公式LINEから、お気軽にどうぞ。施術中はお電話に出られないことが多いため、LINEかInstagramのDMが確実です。</p></div>
  <div class="kwwrap">{kw_ribbon()}<p class="kw-note">LINEでご予約の方は、メッセージに「{KW}」と書いていただくだけでOKです。</p></div>
  <div class="ygrid">
  {cards[0]}
  {cards[1]}
  </div>
 </div>
</section>
'''


def access(r):
    out = []
    for k in ("ibu", "tani"):
        s = SHOPS[k]
        out.append(f'''<div class="shop">
   <div class="hd"><h3>{s["name"]}</h3><p>{s["extra"]}</p></div>
   <a class="tel" href="tel:{s["telh"]}"><small>TEL</small>{s["tel"]}</a>
   <dl>
    <dt>住所</dt><dd>〒{s["zip"]}<br>{s["addr"]}</dd>
    <dt>営業時間</dt><dd>{s["hours"]}</dd>
    <dt>定休日</dt><dd>{s["closed"]}</dd>
    <dt>院長</dt><dd>{s["chief"]}</dd>
    <dt>SNS</dt><dd><a href="{s["ig"]}" target="_blank" rel="noopener">Instagram {s["igname"]}</a></dd>
   </dl>
   <div class="acts">
    {kw_mini()}
    <div class="row">{line_btn(k, "LINEで予約")}</div>
   </div>
   <div class="map"><a class="mapph" href="https://www.google.com/maps/search/?api=1&amp;query={quote(s["addr_q"])}" target="_blank" rel="noopener"><b>Googleマップで開く</b><span>{s["addr_q"]}</span></a><iframe src="{s["map"]}" title="{s["name"]}の地図" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
   <a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query={quote(s["addr_q"])}" target="_blank" rel="noopener">Googleマップで道順を見る →</a>
  </div>''')
    return f'''<section class="access" id="access">
 <div class="wrap">
  <div class="sh"><span class="en">Access</span><h2>店舗情報・アクセス</h2><p>指宿市と鹿児島市谷山の2院。どちらも完全予約制です。子連れの方、男性の方もお気軽にどうぞ。</p></div>
  <div class="shops">
  {out[0]}
  {out[1]}
  </div>
 </div>
</section>
'''


def others(r, cur):
    cards = []
    for p in PILLARS:
        if p["key"] == cur:
            continue
        cards.append(f'''<a class="oc" href="{r}{p["key"]}/"><img src="{r}img/{p["img"]}" style="object-position:{p["pos"]}" alt="{p["alt"]}" loading="lazy">
   <span class="t"><span class="no goldtxt">{p["no"]}</span><b><small>{p["label"]}</small>{p["name"]}</b><span class="go">くわしく見る →</span></span></a>''')
    return f'''<section class="others">
 <div class="wrap">
  <div class="sh"><span class="en">Other Menus</span><h2><span class="ib">ほかのお悩みも、</span><span class="ib"><b>ひとつのサロン</b>で。</span></h2><p>ダイエット・整体・育毛・肌質改善は、組み合わせてのご相談も歓迎です。</p></div>
  <div class="ocards">
  {''.join(cards)}
  </div>
 </div>
</section>
'''


def footer(r, cur):
    links = [f'<a href="{"./" if cur == "top" else r}">ホーム</a>'] + [f'<a href="{r}{p["key"]}/">{p["name"]}</a>' for p in PILLARS]
    cols = []
    for k in ("ibu", "tani"):
        s = SHOPS[k]
        cols.append(f'''<div><h3>{s["name"]}</h3><p class="ad">{s["short"]}</p><a class="tel" href="tel:{s["telh"]}"><small>TEL</small>{s["tel"]}</a><p class="hr">営業時間 {s["hours"]}<br>定休日 {s["closed"]}</p></div>''')
    return f'''<footer class="ftr">
 <div class="wrap">
  <div class="top">
   <div class="brand"><img src="{r}img/logo.png" alt="Body Salon RISE" width="211" height="30"><p>ダイエット・整体・育毛・肌質改善。<br>4つの悩みを、ひとつのサロンで。指宿・谷山の2院。</p><nav class="links" aria-label="フッターメニュー">{''.join(links)}</nav></div>
   {cols[0]}
   {cols[1]}
  </div>
  <p class="copy">&copy; Body Salon RISE</p>
 </div>
</footer>
<div class="fbar" aria-label="ご予約">
 <p class="kwl">ご予約時に<b>「{KW}」</b>とお伝えください</p>
 <div class="row">{line_btn("ibu", "指宿院 LINE予約")}{line_btn("tani", "谷山院 LINE予約")}</div>
</div>
<script src="{r}assets/rise.js" defer></script>
</body>
</html>
'''


def faq_html(items):
    return '\n'.join(f'<details><summary>{q}</summary><div class="a"><p>{a}</p></div></details>' for q, a in items)


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a.replace('<br>', '')}} for q, a in items]}


def biz_ld(r):
    out = []
    for k in ("ibu", "tani"):
        s = SHOPS[k]
        d = {"@type": "HealthAndBeautyBusiness", "@id": (url("") or "") + "#" + k, "name": s["full"],
             "alternateName": "ボディサロンライズ " + s["name"],
             "description": "ダイエット・整体・育毛・肌質改善の4つのメニューを提供するボディサロン（完全予約制）。",
             "image": url("img/ogp.jpg") or "img/ogp.jpg",
             "telephone": s["tel"],
             "address": {"@type": "PostalAddress", "postalCode": s["zip"], "addressRegion": s["region"],
                         "addressLocality": s["city"], "streetAddress": s["street"], "addressCountry": "JP"},
             "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": x["d"], "opens": x["o"], "closes": x["c"]} for x in s["spec"]],
             "sameAs": [s["ig"]],
             "parentOrganization": {"@type": "Organization", "name": "Body Salon RISE"}}
        if BASE_URL:
            d["url"] = BASE_URL
        out.append(d)
    return out


def crumb_ld(r, p):
    home = url("") or "../"
    me = url(p["key"] + "/") or "./"
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": home},
        {"@type": "ListItem", "position": 2, "name": p["name"], "item": me}]}


def write(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)


# ======================================================================
# トップページ
# ======================================================================
def build_top():
    r = ""
    faq = [
        ("予約は必要ですか？", "完全予約制です。予約時間ちょうど、または5分前にお越しください。はじめての方は10分前にお越しください。"),
        ("予約・問い合わせの方法は？", "施術中はお電話に出られないことが多いため、公式LINEかInstagramのDMからのご連絡が確実です。ご予約・ご来店の際に「マイタウンを見た」とお伝えください。"),
        ("いくつかのメニューを組み合わせられますか？", "はい、ご相談いただけます。カウンセリングで優先したいお悩みをうかがい、無理のない進め方と料金をご案内します。"),
        ("育毛・肌質改善だけでも利用できますか？", "まずは公式LINEからお気軽にご相談ください。お悩みやご希望をうかがい、合うメニューをご案内します。"),
        ("支払い方法は何がありますか？", "現金・クレジットカードがご利用いただけます。"),
        ("子ども連れや男性でも利用できますか？", "はい。子連れの方も男性の方も歓迎しています。完全予約制なので、周りを気にせずご相談いただけます。"),
        ("駐車場はありますか？", "指宿院は3台分ご用意しています。谷山院は、ご予約の際にお問い合わせください。"),
    ]
    title = "指宿・谷山のダイエット・整体・育毛・肌質改善｜Body Salon RISE"
    desc = "鹿児島県指宿市・鹿児島市谷山のBody Salon RISE（ボディサロンライズ）。ダイエット・整体・育毛・肌質改善の4つの悩みを、ひとつのサロンで。国家資格（柔道整復師・作業療法士）をもつ院長がご案内します。完全予約制。"
    ld = {"@context": "https://schema.org", "@graph": biz_ld(r) + [faq_ld(faq)]}
    if BASE_URL:
        ld["@graph"].append({"@type": "WebSite", "name": "Body Salon RISE", "url": BASE_URL})

    cells = []
    for i, p in enumerate(PILLARS, 1):
        cells.append(f'''<a class="cell c{i}" href="{p["key"]}/"><img src="img/{p["img"]}" style="object-position:{p["pos"]}" alt="{p["alt"]}"{' fetchpriority="high"' if i == 1 else ''}>
   <span class="tx"><span class="no goldtxt">{p["no"]}</span><span class="nm"><small>{p["label"]}</small>{p["name"]}</span><span class="pill">{p["pill"]}</span></span></a>''')

    pcards = []
    for p in PILLARS:
        chips = ''.join(f'<li>{c}</li>' for c in p["chips"])
        pcards.append(f'''<a class="pcard" href="{p["key"]}/">
   <div class="ph"><img src="img/{p["card"]}" style="object-position:{p["cardpos"]}" alt="{p["cardalt"]}" loading="lazy"><div class="t"><span class="no goldtxt">{p["no"]}</span><h3><small>{p["label"]}</small>{p["name"]}</h3></div></div>
   <div class="bd"><span class="h3m" aria-hidden="true"><small>{p["label"]}</small>{p["name"]}</span><p>{p["desc"]}</p><ul class="chips">{chips}</ul><span class="more">くわしく見る<i>→</i></span></div>
  </a>''')

    worries = [
        ("diet", "体重・体型", ["少しずつ体重が増えてきた", "色々試しても痩せない", "リバウンドが怖い", "ぽっこりお腹・下半身が気になる"]),
        ("seitai", "痛み・姿勢", ["肩こり・腰痛・膝の痛みがつらい", "病院では「異常なし」と言われた", "猫背・巻き肩が気になる", "産後の骨盤が気になる"]),
        ("ikumou", "髪・頭皮", ["髪のボリュームが気になってきた", "頭皮の状態が気になる", "どこに相談すればいいか分からない"]),
        ("hada", "肌", ["肌の調子が気になる", "年齢とともに肌の変化を感じる", "自分に合うケアが分からない"]),
    ]
    wb = []
    for key, t, items in worries:
        p = P[key]
        lis = ''.join(f'<li>{x}</li>' for x in items)
        wb.append(f'<div class="wbox"><h3><span>{p["no"]}</span>{t}</h3><ul>{lis}</ul><a href="{key}/">{p["name"]}について →</a></div>')

    html = head(r, title, desc, "", "img/ogp.jpg", ld) + header(r, "top") + f'''<main id="top">
<section class="hero" aria-label="4つのメニュー">
 <div class="hgrid">
  {''.join(cells)}
 </div>
 <div class="badge" aria-hidden="true"><div class="in">
  <div class="r1"><span class="n4 goldtxt">4</span><span class="t1">つの悩みを、</span></div>
  <div class="t2"><b>ひとつ</b>の<br>サロンで。</div>
  <div class="t3">指宿・谷山の2院</div>
 </div></div>
</section>
<div class="band">
 <h1><span class="pre">指宿・谷山のボディサロン「Body Salon RISE」</span><span class="w">ダイエット</span><span class="sep">・</span><span class="w">整体</span><span class="sep">・</span><span class="w">育毛</span><span class="sep">・</span><span class="w">肌質改善</span></h1>
</div>
<div class="kwbar">
 <div class="wrap in">
  {kw_ribbon()}
  <div class="btns">{line_btn("ibu", "指宿院 LINE予約")}{line_btn("tani", "谷山院 LINE予約")}</div>
 </div>
</div>

<section class="concept">
 <div class="wrap">
  <div class="sh"><span class="en">Concept</span><h2><span class="ib"><span class="goldtxt" style="font-size:1.25em">4</span>つの悩みを、</span><span class="ib"><b>ひとつのサロン</b>で。</span></h2></div>
  <div class="row">
   <div class="txt">
    <p class="big"><span class="ib">痩せたい。</span><span class="ib">痛みをなんとかしたい。</span><br><span class="ib">髪や肌のことも、</span><b class="ib">まとめて相談したい。</b></p>
    <p>Body Salon RISE（ボディサロンライズ）は、鹿児島県指宿市と鹿児島市谷山にある、完全予約制のボディサロンです。</p>
    <p>ダイエット・整体・育毛・肌質改善の4つのメニューを、ひとつのサロンでご相談いただけます。いくつもお店を回らなくても大丈夫。カウンセリングで、今のあなたにいちばん合う進め方からご提案します。</p>
    <p>施術するのは、国家資格（柔道整復師・作業療法士）をもつ院長です。</p>
   </div>
   <figure class="door"><img src="img/r-door.jpg" alt="Body Salon RISEのロゴが入った入口のドア" loading="lazy"><figcaption>完全予約制。周りを気にせず、落ち着いてご相談いただけます。</figcaption></figure>
  </div>
 </div>
</section>

<section class="pillars" id="pillars">
 <div class="wrap">
  <div class="sh"><span class="en">4 Menus</span><h2>RISEの<b>4つのメニュー</b></h2><p>気になるメニューを押すと、くわしい説明のページに移動します。組み合わせてのご相談も歓迎です。</p></div>
  <div class="pcards">
  {''.join(pcards)}
  </div>
 </div>
</section>

<section class="worries">
 <div class="wrap">
  <div class="sh"><span class="en">Worries</span><h2>こんなお悩み、ありませんか？</h2></div>
  <div class="wgrid">{''.join(wb)}</div>
  <p class="answer">体のこと、髪や肌のことも。<br><b><span class="ib">ひとつのサロンで、</span><span class="ib">まとめてご相談いただけます。</span></b></p>
 </div>
</section>

<section class="reason" id="reason">
 <div class="wrap">
  <div class="sh"><span class="en">Reason</span><h2>RISEが選ばれる<b>3つの理由</b></h2></div>
  <div class="rgrid">
   <div class="rcard"><div class="ph"><img src="img/r-exterior.jpg" alt="Body Salon RISE 指宿院の外観" loading="lazy"></div><div class="bd"><span class="num">01</span><h3>4つの悩みを、<br>ひとつのサロンで</h3><p>ダイエット・整体・育毛・肌質改善。いくつもお店を回らなくても、気になることをまとめてご相談いただけます。</p></div></div>
   <div class="rcard"><div class="ph"><img src="img/r-posture.jpg" style="object-position:30% 40%" alt="お客様の姿勢を確かめる院長" loading="lazy"></div><div class="bd"><span class="num">02</span><h3>国家資格をもつ<br>院長が担当</h3><p>指宿院は柔道整復師、谷山院は作業療法士の院長が担当します。整骨院での経験を活かし、姿勢や骨格のゆがみから整えます。</p></div></div>
   <div class="rcard"><div class="ph"><img src="img/r-counsel.jpg" style="object-position:50% 35%" alt="カウンセリングシートを手に笑顔で話す院長" loading="lazy"></div><div class="bd"><span class="num">03</span><h3>一人ひとりに合わせた<br>オーダーメイド</h3><p>マニュアル通りではなく、体質や生活に合わせて無理のない進め方をご提案します。無理な提案や押しつけはしません。</p></div></div>
  </div>
 </div>
</section>

<section class="staff" id="staff">
 <div class="wrap">
  <div class="sh"><span class="en">Staff</span><h2><span class="ib">施術するのは、</span><span class="ib"><b>国家資格をもつ院長</b>です</span></h2></div>
  <div class="row">
   <div class="prof">
    <div class="pc"><div class="ph"><img src="img/r-posture.jpg" style="object-position:30% 40%" alt="指宿院 院長 和田諒真が姿勢を確かめている様子" loading="lazy"></div><div class="bd"><span class="in">指宿院 院長</span><h3>和田 諒真<small>柔道整復師</small></h3><p class="q">「無理な提案や押しつけはせず、納得していただいてから施術します。」</p><ul class="quals"><li>柔道整復師（国家資格）</li><li>ダイエットエキスパート</li></ul></div></div>
    <div class="pc"><div class="ph"><img src="img/r-treat.jpg" style="object-position:40% 40%" alt="谷山院 院長 和田一真が施術している様子" loading="lazy"></div><div class="bd"><span class="in">谷山院 院長</span><h3>和田 一真<small>作業療法士</small></h3><p class="q">「お悩みやご希望を、ていねいにうかがってから進めます。」</p><ul class="quals"><li>作業療法士（国家資格）</li></ul></div></div>
   </div>
   <div class="duo"><div class="ring"></div><div class="medal"><b>国家資格<small>柔道整復師<br>作業療法士</small></b></div><picture><source srcset="img/inchou.webp" type="image/webp"><img src="img/inchou.png" alt="笑顔でガッツポーズをする和田諒真院長と和田一真院長" loading="lazy" width="1101" height="750"></picture></div>
  </div>
  <div class="msg">
   <h3>「本当の改善とは何だろう」から、RISEは始まりました。</h3>
   <p>整骨院に勤めていた頃、肩こりや腰痛の施術をしても、すぐに再発してしまう方を多く見てきました。「痩せていた頃はこんな痛みはなかった」――そんな声を何度も耳にし、その場しのぎではなく、生活習慣と体質から変えることが大切だと考えるようになりました。</p>
   <p>目指すのは、地域の誰もが気軽に相談できる、身近なサロンです。体のことも、髪や肌のことも、まずはお気軽にご相談ください。</p>
   <p class="sig">指宿院 院長 和田 諒真</p>
  </div>
 </div>
</section>

<section class="cp on-dark" id="cp">
 <div class="wrap">
  <div class="sh"><span class="en">First Visit</span><h2><span class="ib">はじめての方へ</span> <b class="ib">初回限定キャンペーン</b></h2><p>はじめての方に、まずは気軽に体験していただける料金をご用意しています。</p></div>
  <div class="kwwrap">{kw_ribbon()}<p class="kw-note">ご予約・ご来店の際にお伝えいただくと、下の初回料金で体験いただけます。</p></div>
  <div class="cpgrid">
   <div class="cpc"><div class="hd"><span>01</span><h3>ダイエット</h3></div><ul><li><span class="nm">初回カウンセリング＆姿勢矯正</span><span class="pr">500<small>円</small></span></li></ul><a class="more" href="diet/">ダイエットについて →</a></div>
   <div class="cpc"><div class="hd"><span>02</span><h3>整体</h3></div><ul><li><span class="nm">整体 初回施術</span><span class="pr">1,000<small>円</small></span></li><li><span class="nm">ブライダル整体 初回施術</span><span class="pr">3,500<small>円</small></span></li><li><span class="nm">不調改善 カウンセリング＆初回施術</span><span class="pr">3,500<small>円</small></span></li></ul><a class="more" href="seitai/">整体について →</a></div>
   <div class="cpc"><div class="hd"><span>03</span><h3>育毛</h3></div><ul><li><p class="ask">料金は、カウンセリング時にご案内します。<small>頭皮の状態とご希望をうかがってから、内容と料金をお伝えします。</small></p></li></ul><a class="more" href="ikumou/">育毛について →</a></div>
   <div class="cpc"><div class="hd"><span>04</span><h3>肌質改善</h3></div><ul><li><p class="ask">料金は、カウンセリング時にご案内します。<small>肌の状態とご希望をうかがってから、内容と料金をお伝えします。</small></p></li></ul><a class="more" href="hada/">肌質改善について →</a></div>
  </div>
  <p class="note">※料金はすべて税込です。2回目以降の料金・3ヶ月コースの料金は、カウンセリング時にご案内します。<br>※お支払いは現金・クレジットカードがご利用いただけます。</p>
 </div>
</section>

<section class="flow">
 <div class="wrap">
  <div class="sh"><span class="en">Flow</span><h2>ご来店の流れ</h2></div>
  <ol class="steps">
   <li><span class="n">1</span><h3>LINEでご予約</h3><p>通いやすい院の公式LINEから。「{KW}」と一言添えてください。</p></li>
   <li><span class="n">2</span><h3>カウンセリング</h3><p>お悩みや「こうなりたい」というご希望を、じっくりうかがいます。</p></li>
   <li><span class="n">3</span><h3>状態のチェック</h3><p>体・姿勢・頭皮・肌など、お悩みに合わせて今の状態を確かめます。</p></li>
   <li><span class="n">4</span><h3>施術・ご提案</h3><p>お体に合わせた施術と、これからの進め方をご提案します。</p></li>
  </ol>
 </div>
</section>

<section class="faq" id="faq">
 <div class="wrap">
  <div class="sh"><span class="en">Q&amp;A</span><h2>よくあるご質問</h2></div>
  <div class="faqlist">
{faq_html(faq)}
  </div>
 </div>
</section>

{access(r)}

<section class="ig" id="instagram">
 <div class="wrap">
  <div class="sh"><span class="en">Instagram</span><h2><span class="ib">Instagramで、</span><span class="ib">日々の様子を発信中</span></h2><p>お客様の変化や施術の様子、体にいい食事のヒントなどを投稿しています。DMからもご予約・ご相談いただけます。</p></div>
  <div class="iggrid">
   <a class="igc" href="{IG_IBU}" target="_blank" rel="noopener"><span class="ic">{ICON_CAM}</span><span><b>指宿院</b><span>@wada.ibusuki</span></span><i>見る →</i></a>
   <a class="igc" href="{IG_TANI}" target="_blank" rel="noopener"><span class="ic">{ICON_CAM}</span><span><b>谷山院</b><span>@taniyama.diet</span></span><i>見る →</i></a>
  </div>
 </div>
</section>

{yoyaku(r)}
</main>
''' + footer(r, "top")
    write("index.html", html)


# ======================================================================
# 4本柱のページ
# ======================================================================
def pillar_page(key, d):
    r = "../"
    p = P[key]
    ld = {"@context": "https://schema.org", "@graph": biz_ld(r) + [faq_ld(d["faq"]), crumb_ld(r, p)]}
    fw = ''.join(f'<li>{x}</li>' for x in d["forwho"])
    feats = ''.join(f'<div class="fc"><span class="no goldtxt">0{i}</span><h3>{t}</h3><p>{tx}</p></div>' for i, (t, tx) in enumerate(d["feats"], 1))
    steps = ''.join(f'<li><span class="n">{i}</span><h3>{t}</h3><p>{tx}</p></li>' for i, (t, tx) in enumerate(d["flow"], 1))
    prices = ''.join(
        (f'<li><span class="nm">{n}<small>{s}</small></span><span class="pr">{v}<small>円</small></span></li>' if v else
         f'<li><span class="nm">{n}<small>{s}</small></span><span class="ask">カウンセリング時にご案内</span></li>')
        for n, s, v in d["prices"])
    html = head(r, d["title"], d["desc"], key + "/", "img/ogp.jpg", ld) + header(r, key) + f'''<main>
<section class="phero" style="padding:0">
 <div class="bg"><img src="{r}img/{p["img"]}" style="object-position:{d.get("heropos", p["pos"])}" alt="{p["alt"]}" fetchpriority="high"></div>
 <div class="in">
  <span class="no goldtxt">{p["no"]}</span>
  <h1><small>{d["h1small"]}</small><span class="ib">指宿・谷山の</span><span class="ib">{d["h1"].replace("指宿・谷山の", "")}</span></h1>
  <p class="lead">{d["lead"]}</p>
  <div class="acts">{line_btn("ibu", "指宿院 LINE予約")}{line_btn("tani", "谷山院 LINE予約")}</div>
  {kw_mini()}
 </div>
</section>
<nav class="crumb" aria-label="パンくずリスト"><div class="wrap"><ol><li><a href="{r}">ホーム</a></li><li aria-current="page">{p["name"]}</li></ol></div></nav>

<section class="intro">
 <div class="wrap row">
  <div class="txt">
   <h2>{d["intro_h"]}</h2>
   {d["intro"]}
  </div>
  <div class="ph"><img src="{r}img/{d["intro_img"]}" style="object-position:{d.get("intro_pos", "50% 40%")}" alt="{d["intro_alt"]}" loading="lazy"></div>
 </div>
</section>

<section class="forwho">
 <div class="wrap">
  <div class="sh"><span class="en">For You</span><h2>こんな方に<b>おすすめ</b>です</h2></div>
  <ul class="fwgrid">{fw}</ul>
 </div>
</section>

<section class="feat">
 <div class="wrap">
  <div class="sh"><span class="en">Approach</span><h2>{d["feat_h"]}</h2>{d.get("feat_p", "")}</div>
  <div class="fgrid">{feats}</div>
 </div>
</section>
{d.get("extra", "")}
<section class="flow">
 <div class="wrap">
  <div class="sh"><span class="en">Flow</span><h2>{p["name"]}の施術の流れ</h2></div>
  <ol class="steps">{steps}</ol>
 </div>
</section>

<section class="price" id="price">
 <div class="wrap">
  <div class="sh"><span class="en">Price</span><h2>{p["name"]}の料金</h2></div>
  <div class="pbox">
   <div class="hd">{d["price_h"]}</div>
   <ul>{prices}</ul>
   <div class="ft">{kw_ribbon()}<p>{d["price_note"]}</p></div>
  </div>
 </div>
</section>

<section class="faq">
 <div class="wrap">
  <div class="sh"><span class="en">Q&amp;A</span><h2>{p["name"]}のよくあるご質問</h2></div>
  <div class="faqlist">
{faq_html(d["faq"])}
  </div>
 </div>
</section>

{yoyaku(r, '<span class="ib">' + p["name"] + 'のご予約は、</span><span class="ib">LINEで</span>')}
{others(r, key)}
{access(r)}
</main>
''' + footer(r, key)
    write(f"{key}/index.html", html)


COMMON_FLOW_1 = ("LINEでご予約", "通いやすい院の公式LINEから。「マイタウンを見た」と一言添えてください。")

PAGES = {
    "diet": dict(
        title="指宿・谷山のダイエット（体質改善）｜Body Salon RISE",
        desc="指宿市・鹿児島市谷山のBody Salon RISEの体質改善ダイエット。遺伝子検査で体質を知り、整体と食事の見直しで、きつい運動や我慢の食事制限に頼らないダイエットをサポートします。完全予約制。",
        h1small="体質改善ダイエット", h1="指宿・谷山のダイエット",
        lead="食事と習慣から、体質を整える。<br>きつい運動も、我慢の食事制限もしません。",
        intro_h="「色々試したのに痩せない」<br>その理由は、<b>体質</b>にあるかもしれません。",
        intro='''<p>Body Salon RISEのダイエットは、「自分の体を知ること」から始まります。遺伝子検査で体質の傾向を知り、整体でゆがみや巡りを整え、栄養指導で無理のない食習慣へ。リバウンドしにくい体を目指します。</p>
   <p>指宿院（指宿市）・谷山院（鹿児島市）のどちらでも、国家資格をもつ院長がカウンセリングから担当します。</p>''',
        intro_img="ai-food.jpg", intro_alt="バランスのよい和食を食べる女性（食事の見直しのイメージ）",
        forwho=["少しずつ体重が増えてきた", "色々試しても痩せない・続かない", "リバウンドが怖い", "ぽっこりお腹・下半身が気になる", "運動が苦手、時間がない", "産後の体型が戻らない"],
        feat_h="RISEのダイエット<b>3つの特徴</b>",
        feats=[("遺伝子検査で、体質を知る", "まずは自分の体質を知るところから始めます。結果をもとに、あなたに合った進め方を考えます。"),
               ("整体で、体の土台を整える", "骨盤や姿勢のゆがみを整え、巡りのよい体へ。柔道整復師・作業療法士の院長が担当します。"),
               ("栄養指導で、食習慣を見直す", "分子栄養学をもとに、我慢ではなく「何をどう食べるか」をご提案。毎日続けられる食習慣をつくります。")],
        extra='''<section class="result">
 <div class="wrap">
  <div class="sh"><span class="en">Result</span><h2><span class="ib">ダイエットコースの</span><b class="ib">お客様の結果</b></h2></div>
  <div class="row">
   <div class="big">
    <p class="k">ダイエット（3ヶ月の減量プログラム）で</p>
    <p class="v"><small>平均</small>−7.5<small>kg</small></p>
    <p class="s">これまでにサポートした方々の実績です</p>
    <ul class="vs"><li>3ヶ月で −10.9kg</li><li>3ヶ月で −9.1kg</li><li>3ヶ月で −8.9kg</li></ul>
    <p class="note-ind">※効果には個人差があります。</p>
   </div>
   <figure><img src="../img/results-ad.jpg" alt="ダイエットコースを受けたお客様が結果を書いたボードを持つ写真" loading="lazy"><figcaption>ダイエットコースのお客様</figcaption><p class="note-ind">※効果には個人差があります。</p></figure>
  </div>
 </div>
</section>''',
        flow=[COMMON_FLOW_1, ("カウンセリング", "目標や生活習慣、これまで試したダイエットのことをうかがいます。"),
              ("測定・姿勢チェック", "体の状態や姿勢のゆがみを確かめ、太りやすい原因を探ります。"),
              ("プランのご提案", "整体と食事の見直しを組み合わせ、3ヶ月コースなどあなたに合うプランをご提案します。")],
        price_h="はじめての方へ　初回限定",
        prices=[("初回カウンセリング＆姿勢矯正", "ダイエットのご相談がはじめての方", "500"),
                ("3ヶ月コース", "カウンセリングの内容に合わせてご案内", None)],
        price_note="※料金は税込です。2回目以降の料金・3ヶ月コースの料金は、カウンセリング時にご案内します。お支払いは現金・クレジットカードがご利用いただけます。",
        faq=[("本当に運動しなくても痩せますか？", "ハードな運動や無理な食事制限は行いません。体質に合わせた食事の見直しと整体で、無理なく健康的に痩せる方法をご提案します（効果には個人差があります）。"),
             ("食事制限はありますか？", "我慢するための制限ではなく、体質に合わせて「何をどう食べるか」の見直しをご提案します。毎日の生活に取り入れやすい方法を一緒に考えます。"),
             ("遺伝子検査はどんなものですか？", "体質の傾向を知るための検査です。結果をもとに、食事の見直し方や進め方を一緒に考えます。くわしくはカウンセリングでご説明します。"),
             ("どのくらいの期間通いますか？", "3ヶ月コースを中心に、目標や生活に合わせてご提案します。無理な提案や押しつけはしませんので、ご安心ください。"),
             ("男性も利用できますか？", "はい、男性の方も歓迎しています。完全予約制なので、周りを気にせずご相談いただけます。")]),
    "seitai": dict(
        title="指宿・谷山の整体（腰痛・肩こり）｜Body Salon RISE",
        desc="指宿市・鹿児島市谷山の整体ならBody Salon RISE。国家資格（柔道整復師・作業療法士）をもつ院長が、腰痛・肩こり・膝の痛み、骨盤や姿勢のゆがみ、産後の骨盤ケアやブライダル整体のご相談をお受けします。",
        h1small="腰痛・肩こり・膝痛・ブライダル", h1="指宿・谷山の整体",
        lead="その場しのぎではなく、<br>体の土台から整える整体。",
        intro_h="腰痛・肩こり・膝の痛み。<br><b>くり返すつらさ</b>に、体の土台から。",
        intro='''<p>腰痛・肩こり・首こり・膝の痛み、慢性的な疲れなど、くり返すつらさには、姿勢や骨格のゆがみ、生活習慣が関わっていることがあります。</p>
   <p>Body Salon RISEの整体では、筋肉の調整・骨盤矯正・栄養サポートの3つの視点で、体の土台から整えます。産後の骨盤ケアやブライダル整体・小顔矯正もご相談いただけます。</p>''',
        intro_img="r-posture.jpg", intro_pos="30% 40%", intro_alt="立ったお客様の姿勢を確かめる院長",
        forwho=["肩こり・腰痛・膝の痛みがつらい", "病院では「異常なし」と言われた", "猫背・巻き肩・ストレートネックが気になる", "産後の骨盤が気になる", "結婚式までに姿勢やフェイスラインを整えたい", "慢性的な疲れ・だるさがある"],
        feat_h="RISEの整体<b>3つの特徴</b>",
        feats=[("国家資格をもつ院長が担当", "指宿院は柔道整復師、谷山院は作業療法士の院長が担当します。整骨院での経験を活かして施術します。"),
               ("筋肉の調整 × 骨盤矯正", "つらい部分だけでなく、骨盤や肩甲骨まわりなど体全体のバランスを確かめながら整えます。"),
               ("栄養サポートで内側からも", "食事や生活習慣のご相談にも対応。体の内側と外側の両方から、くり返しにくい体を目指します。")],
        extra='''<section class="also">
 <div class="wrap">
  <div class="sh"><span class="en">Also</span><h2>整体は、<b>こんな方にも</b>選ばれています</h2></div>
  <div class="agrid">
   <div class="ac"><div class="ph"><img src="../img/ai-mama.jpg" style="object-position:50% 30%" alt="赤ちゃんを抱っこする女性（産後のイメージ）" loading="lazy"></div><div class="bd"><h3>産後の体型・骨盤が気になる方</h3><p>抱っこや授乳で崩れがちな骨盤と姿勢を、体の回復に合わせてやさしく整えます。子連れでのご来院もOKです。</p><ul class="chips"><li>産後骨盤ケア</li><li>姿勢改善</li></ul></div></div>
   <div class="ac"><div class="ph"><img src="../img/ai-bride.jpg" style="object-position:50% 25%" alt="ウェディングドレス姿の女性（ブライダルのイメージ）" loading="lazy"></div><div class="bd"><h3>結婚式までに整えたい方</h3><p>小顔矯正と姿勢の調整で、フェイスラインと立ち姿をすっきりと。ドレス姿に自信が持てるようサポートします。</p><ul class="chips"><li>ブライダル整体</li><li>小顔矯正</li></ul></div></div>
  </div>
 </div>
</section>''',
        flow=[COMMON_FLOW_1, ("カウンセリング", "痛む場所やいつからか、お仕事や生活のことをうかがいます。"),
              ("姿勢・体のチェック", "姿勢や骨盤のゆがみ、動きのクセを確かめて、原因を探ります。"),
              ("施術・セルフケアのご提案", "体に合わせて施術し、ご自宅でできるケアや通い方をご提案します。")],
        price_h="はじめての方へ　初回限定",
        prices=[("整体 初回施術", "腰痛・肩こり・膝の痛みなど", "1,000"),
                ("ブライダル整体 初回施術", "花嫁さまに", "3,500"),
                ("不調改善 カウンセリング＆初回施術", "慢性的な不調のご相談に", "3,500")],
        price_note="※料金は税込です。2回目以降の料金は、カウンセリング時にご案内します。お支払いは現金・クレジットカードがご利用いただけます。",
        faq=[("痛みが強くても受けられますか？", "強い痛みやしびれ、けがの直後などは、まず医療機関の受診をおすすめします。状態をうかがったうえで、施術ができるかをご案内します。"),
             ("骨盤矯正は痛くないですか？", "力加減を確かめながら行います。痛みや不安があるときは、施術中でもお気軽にお伝えください。"),
             ("産後はいつから受けられますか？", "体の回復の状態によって異なります。まずは公式LINEで、出産の時期や今の体調をお知らせください。子連れでのご来院もOKです。"),
             ("ブライダル整体はいつから通えばいいですか？", "式の日取りとご希望をうかがって、通い方をご提案します。早めにご相談いただくと、余裕をもって進められます。"),
             ("子ども連れでも大丈夫ですか？", "はい、子連れでのご来院もOKです。完全予約制なので、周りを気にせず施術を受けられます。")]),
    "ikumou": dict(
        title="指宿・谷山の育毛・頭皮ケア｜Body Salon RISE",
        desc="指宿市・鹿児島市谷山のBody Salon RISEの育毛・頭皮ケア。髪のボリュームや頭皮の状態など、相談しにくいお悩みを、カウンセリングで確かめたうえで、一人ひとりに合ったケアをご提案します。完全予約制。",
        h1small="頭皮ケア", h1="指宿・谷山の育毛・頭皮ケア",
        lead="髪と頭皮の悩みも、<br>ひとりで抱えずに。",
        intro_h="気になっていても、<br><b>相談しにくい</b>髪と頭皮のこと。",
        intro='''<p>髪のボリュームや頭皮の状態など、気になっていても、なかなか人に相談しにくいお悩み。Body Salon RISEでは、はじめに頭皮の状態をカウンセリングで確かめ、生活習慣もうかがったうえで、一人ひとりに合ったケアをご提案します。</p>
   <p>完全予約制なので、周りを気にせずご相談いただけます。体の内側から整えるダイエット・整体と組み合わせたご相談もできます。</p>''',
        intro_img="r-counsel.jpg", intro_pos="50% 35%", intro_alt="カウンセリングでお話をうかがう院長",
        forwho=["髪のボリュームが気になってきた", "頭皮の状態が気になる", "どこに相談すればいいか分からない", "人に相談するのが少し恥ずかしい", "自分に合うケアを知りたい", "食事や睡眠など生活習慣も見直したい"],
        feat_h="RISEの育毛・頭皮ケアで<b>大切にしていること</b>",
        feats=[("まずは頭皮の状態を確かめる", "いきなり施術を始めるのではなく、カウンセリングで頭皮の状態とお悩みをていねいにうかがいます。"),
               ("一人ひとりに合ったケアのご提案", "状態やご希望、通いやすさに合わせて、無理のないケアの進め方をご提案します。"),
               ("生活習慣もいっしょに見直す", "食事や睡眠など、毎日の過ごし方のご相談にも対応します。ダイエット・整体との組み合わせも可能です。")],
        flow=[COMMON_FLOW_1, ("カウンセリング", "気になっていること、いつ頃からか、生活習慣などをうかがいます。"),
              ("頭皮の状態チェック", "今の頭皮の状態を確かめ、気になる点をいっしょに見ていきます。"),
              ("ケアのご提案", "状態に合わせたケアの内容・通い方・料金をご案内します。")],
        price_h="育毛・頭皮ケア",
        prices=[("育毛・頭皮ケア", "内容は頭皮の状態とご希望に合わせてご提案", None)],
        price_note="※料金は、頭皮の状態とご希望をうかがったうえで、カウンセリング時にご案内します。お支払いは現金・クレジットカードがご利用いただけます。",
        faq=[("どんなケアをしますか？", "頭皮の状態とご希望をカウンセリングでうかがったうえで、内容をご案内します。気になることは何でもお気軽にお聞かせください。"),
             ("料金はいくらですか？", "頭皮の状態とご希望によって内容が変わるため、カウンセリング時にご案内します。"),
             ("育毛だけでも利用できますか？", "まずは公式LINEからお気軽にご相談ください。お悩みやご希望をうかがい、合うメニューをご案内します。"),
             ("どのくらいで変化を感じられますか？", "頭皮や髪の状態には個人差があるため、一概にはお伝えできません。カウンセリングで、通い方の目安をご相談しながら進めます。"),
             ("ほかのメニューと組み合わせられますか？", "はい。ダイエットや整体など、ほかのお悩みとあわせてご相談いただけます。")]),
    "hada": dict(
        title="指宿・谷山の肌質改善・フェイシャル｜Body Salon RISE",
        desc="指宿市・鹿児島市谷山のBody Salon RISEの肌質改善・フェイシャル。乾燥やくすみ、年齢とともに感じる肌の変化に。今の肌の状態をていねいに確かめ、お悩みとご希望に合わせたケアの進め方をご提案します。",
        h1small="フェイシャル", h1="指宿・谷山の肌質改善・フェイシャル",
        lead="肌の調子も、<br>いっしょに見直す。",
        heropos="62% 40%",
        intro_h="乾燥、くすみ、年齢による変化。<br><b>今の肌</b>を知ることから。",
        intro='''<p>乾燥やくすみ、年齢とともに感じる肌の変化。「自分に合うケアが分からない」という方も多いのではないでしょうか。</p>
   <p>Body Salon RISEでは、今の肌の状態をていねいに確かめて、お悩みとご希望に合わせたケアの進め方をご提案します。食事や睡眠など、毎日の過ごし方のご相談もお気軽にどうぞ。</p>''',
        intro_img="hada-pexels.jpg", intro_pos="50% 30%", intro_alt="頬に手を添えて肌の調子を確かめる女性（肌質改善のイメージ）",
        forwho=["肌の調子が気になる", "乾燥・くすみが気になる", "年齢とともに肌の変化を感じる", "自分に合うケアが分からない", "大切な日に向けて肌を整えたい", "食事や睡眠も見直したい"],
        feat_h="RISEの肌質改善で<b>大切にしていること</b>",
        feats=[("まずは肌の状態を確かめる", "カウンセリングで、今の肌の状態やふだんのお手入れ、気になっていることをうかがいます。"),
               ("フェイシャルケア", "肌の状態とご希望に合わせて、ケアの内容と進め方をご提案します。"),
               ("生活習慣のご相談", "食事や睡眠など、肌に関わる毎日の過ごし方もいっしょに見直します。ダイエット・整体との組み合わせも可能です。")],
        flow=[COMMON_FLOW_1, ("カウンセリング", "気になっていること、ふだんのお手入れや生活習慣をうかがいます。"),
              ("肌の状態チェック", "今の肌の状態を確かめ、気になる点をいっしょに見ていきます。"),
              ("ケアのご提案", "状態に合わせたケアの内容・通い方・料金をご案内します。")],
        price_h="肌質改善・フェイシャル",
        prices=[("肌質改善・フェイシャル", "内容は肌の状態とご希望に合わせてご提案", None)],
        price_note="※料金は、肌の状態とご希望をうかがったうえで、カウンセリング時にご案内します。お支払いは現金・クレジットカードがご利用いただけます。",
        faq=[("どんなケアをしますか？", "肌の状態とご希望をカウンセリングでうかがったうえで、内容をご案内します。気になることは何でもお気軽にお聞かせください。"),
             ("料金はいくらですか？", "肌の状態とご希望によって内容が変わるため、カウンセリング時にご案内します。"),
             ("肌質改善だけでも利用できますか？", "まずは公式LINEからお気軽にご相談ください。お悩みやご希望をうかがい、合うメニューをご案内します。"),
             ("どのくらいで変化を感じられますか？", "肌の状態には個人差があるため、一概にはお伝えできません。カウンセリングで、通い方の目安をご相談しながら進めます。"),
             ("ほかのメニューと組み合わせられますか？", "はい。ダイエットや整体など、ほかのお悩みとあわせてご相談いただけます。")]),
}

if __name__ == "__main__":
    build_top()
    for k, d in PAGES.items():
        pillar_page(k, d)
