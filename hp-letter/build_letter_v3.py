# 案内文 第3版（見本付き・スタンダード1本・v3.1 安さを大きく）A・B。
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
PHONES = g["PHONES"].replace("いちばん下の<br>QRから", "右下の<br>QRから").replace('御社のホームページの見本、<br><em>できています</em>', '御社のホームページの見本、<em>できています</em>')
i = PHONES.rindex("</div>")
PHONES = PHONES[:i] + '<p class="std-cap"><b>仕上がり</b>は、この見本でご確認ください</p>' + PHONES[i:]

def push(strong, span, flow=None):
    return f"""<section class="push p3">
  <div class="tag">御社の<b>見本</b></div>
  <div class="t"><div class="t-h"><strong>{strong}</strong><div class="lim">お申込み期限<b>＿＿月＿＿日まで</b></div></div><span>{span}</span></div>
</section>"""

def header3():
    h = header()
    return h.replace('<div class="hd-badge">マイタウンガイド掲載企業さま限定のご案内</div>',
        '<div class="hd-r"><div class="hd-badge">マイタウンガイド掲載企業さま限定のご案内</div><p class="hd-co">代表 見立 大作　〒891-0109 鹿児島市清和3-25-15</p></div>')

def cta3(call, qtxt):
    h = cta(call, qtxt)
    i = h.index('<p class="co">'); j = h.index('</p>', i) + 4
    return h[:i] + h[j:]

def check_ic():
    return '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'

def price3():
    items = ["トップページ＋基本4〜5ページ", "スマホ対応", "お問い合わせフォーム", "SNS連携",
             "検索対策<small class='in'>（検索で見つけてもらうための基本設定）</small>"]
    lis = "".join(f'<li class="{"wide" if k in (0, 4) else ""}">{check_ic()}<span>{x}</span></li>' for k, x in enumerate(items))
    return f"""<section class="price3">
<div class="sec-h"><h2>いつもお世話になっている<span class="blank"></span>様への、<em class="hl">感謝価格</em>です<small>（税込）</small></h2><span class="en">PRICE</span></div>
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
<p class="cmp">この内容でこの価格は、掲載企業さまだけの感謝価格です。<b>ぜひ他社のお見積もりと比べてみてください。</b></p>
</section>"""

def domain(title, items, note=""):
    cells = "".join(f'<li><span class="di">{icon(ic)}</span><b>{h}</b></li>' for ic, h in items)
    n = f'<p class="dom-n">{note}</p>' if note else ""
    return f"""<section class="dom"><div class="dom-h">{title}</div><ul class="dom-l">{cells}</ul>{n}</section>"""

def monthly3(line):
    return f"""<section class="monthly m3">
  <div class="m-top"><span class="m-k">制作費とは別に</span><h3>これが全部込みで、月々<b>5,500</b>円<small>（税込）</small></h3><p class="m-line">{line}</p></div>
  <ul class="tags"><li>サーバー・ドメイン代</li><li>写真の差し替え・文章の変更</li><li>Googleマップの情報更新</li><li>WordPressの更新</li><li>暗号化（https）・セキュリティ・バックアップ</li></ul>
  <p class="m-term">月額は<b>24か月のご利用が前提</b>です（24か月未満で解約の場合は5,500円×残りの月数）</p>
</section>"""

def catch():
    return """<div class="catch c4">
  <p class="c0"><b>スタンダードプラン</b><span>（TOP＋4〜5ページ・<br>検索対策込み）</span></p>
  <p class="c2"><em>制作費</em> 通常 <s>88,000円〜</s><i>→</i><b>55,000</b><span>円〜</span><small>（税込）</small></p>
  <p class="c1">月々<b>5,500</b><span>円</span>に、サーバー・ドメイン代まで込み。</p>
</div>"""

FINE = """<p class="fine">※ドメインは御社名義で、候補をご提案してお取りします（取得・更新の費用は月額に含みます）。※24か月以上のご利用で、サイトのデータ（ZIP）とドメインの移管<wbr>手続きを無償でお渡しします。※ご解約は毎月25日までのご連絡で翌月分から停止します。※ページの追加・デザイン変更、原稿<wbr>づくり・写真撮影は別途お見積もりです。ほかのプランもご相談ください。※特別価格（感謝価格）はマイタウンガイド掲載企業さま限定です。※見本はお申込み期限を過ぎたら削除します。詳しい条件は契約書に明記します。※同封のチラシでは、AI動画づくりもご紹介しています。</p>"""
FINE_B = FINE.replace("※同封のチラシでは、AI動画づくりもご紹介しています。", "").replace("（取得・更新の費用は月額に含みます）。", "（取得・更新の費用は月額に含みます。今お持ちのドメインを使う場合は別途ご説明します）。")

SPAN_TAIL = ('お作りした<wbr>見本は、<b>検索対策込みの<wbr>スタンダードプラン（55,000円〜）の<wbr>内容</b>です。'
        '<b>見るだけ・<wbr>お断りでも<wbr>費用は<wbr>かかりません。</b>文章や<wbr>写真は<wbr>仮のもので、打ち合わせで<wbr>直してから<wbr>公開します。')
SPAN_A = '今は多くの方が<wbr>スマホで<wbr>ホームページを<wbr>見ます。パソコンでも<wbr>スマホでも<wbr>見やすく<wbr>作ります。' + SPAN_TAIL
SPAN_B = '今は多くの方が<wbr>スマホで<wbr>見るため、パソコンでも<wbr>スマホでも<wbr>見やすく<wbr>作ります。QRから<wbr>今のページと<wbr>見比べてください。' + SPAN_TAIL
PUSH_H = '価格は抑えても、<em>仕上がりには手を抜きません。</em>'
DOM_NOTE = '<b>ドメイン（御社名入りのアドレス）は、こちらで候補をいくつかご提案し、お選びいただきます。</b>'
CALL2 = '<small>見ていただいた感想だけでもかまいません。</small>'

import re as _re
def fine_wrap(h):
    """注意書き：文節の切れ目（助詞のあと）にだけ改行の候補を入れる。※はうしろの語と離さない。"""
    h = h.replace("<wbr>", "")
    h = _re.sub(r"([をにではがのとも])(?=[^ぁ-ゖ、。）」<]|[ごお][一-龥])", r"\1<wbr>", h)
    h = _re.sub(r"(?<=[一-龥ァ-ヶ])(?=[ごお][一-龥ぁ-ゖ])", "<wbr>", h)   # 「別途｜ご説明」など、敬語の前でも折り返せる
    return h.replace("※", "※\u2060")

PAGE_A = f"""<div class="page v3" id="A">
{header3()}
<main class="body">
{ADDR}
<section>
  <h1>御社のホームページの<em>見本</em>を、ひとつお作りしました。</h1>
  {catch()}
  <p class="lead ka">いつもマイタウンガイドにご掲載いただき、ありがとうございます。日頃の感謝を込めてお作りした見本を、右下のQRからスマホでご覧ください。</p>
</section>
<section class="show">
{PHONES}
  <div class="merits3">
    {merit3(1,"search","調べたときに、ちゃんと出てくるように","")}
    {merit3(2,"moon","お休みの日も夜中も、御社を案内","")}
    {merit3(3,"phone","同じ説明の電話が減る","")}
  </div>
</section>
{domain('<b>「www.<em>御社名</em>.com」</b>自社のアドレスで、<br>信用が変わります', [
  ("globe","名刺・チラシ・誌面で、きちんとした印象に"),
  ("people","取引先・求人の応募者・金融機関にも安心を"),
  ("home","御社名義の「財産」として残る"),
  ("shield","突然消える心配が少ない")], DOM_NOTE)}
{price3()}
{monthly3("変更のご依頼は、<b>LINEで送るだけ</b>です。")}
{push(PUSH_H, SPAN_A, ["QRで見本を見る","気に入ったらお電話","打ち合わせで直して公開"])}
</main>
{cta3("気になったらお電話ください。<em>「見本を見た」</em>とお伝えください。" + CALL2, "御社の<br>ホームページの<br><em>見本はこちら</em>")}
{fine_wrap(FINE)}
</div>"""

PAGE_B = f"""<div class="page pB v3" id="B">
{header3()}
<main class="body">
{ADDR}
<section>
  <h1 class="long">御社のホームページを「<em>作り直したら</em>」の見本を、お作りしました。</h1>
  {catch()}
  <p class="lead ka">いつもマイタウンガイドにご掲載いただき、ありがとうございます。日頃の感謝を込めて<wbr>今の御社のページを拝見し、<span class="nw">アドレス・スマホでの見やすさ・安心して見られるか</span>まで<wbr>見直した見本をお作りしました。</p>
</section>
<section class="check-wrap">
  <div class="check"><h3>ひとつでも当てはまったら、<em>見直しどき</em>です</h3>
    <ul><li>アドレスに、無料サービスや他社の名前が入っている</li><li>ページに、知らない広告が出る</li><li>「保護されていない通信」と出る</li><li>スマホで見ると、文字が小さい・崩れる</li><li>何年も更新していない</li><li>直したいとき、どこに頼めばいいか分からない</li></ul>
  </div>
  <div class="ba">
    <div class="url old o3"><span class="lb">いま</span><div class="st"><span class="u">〇〇blog.jp/…<i class="ad">広告</i></span><span><i class="wn">!</i>保護されていない通信</span><span><i class="wn">!</i>スマホで崩れる・古いまま</span></div></div>
    <div class="arrow">▼</div>
    <div class="url new"><span class="lb">これから</span><span>www.<em>御社名</em>.com</span></div>
    <div class="nt"><span><b>✓</b>鍵マーク付き（https）</span><span><b>✓</b>スマホでもパソコンでも見やすい</span></div>
    <p>アドレス・安心・見やすさを、<em>まとめて新しく。</em></p>
    <p class="r">今お持ちのドメインを使い続けたい場合もご相談ください<br>（費用の扱いはご相談時にご説明します）。</p>
  </div>
</section>
{domain('<b>作り直すと、</b>ここが変わります', [
  ("globe","御社名のアドレスで、<br>信用が変わる"),
  ("shield","安全の鍵マーク<br>付き（https）に"),
  ("phone","スマホでも<br>パソコンでも見やすい"),
  ("home","借りものでなく、<br>御社の財産に")])}
{price3()}
{monthly3("作り直したあとも、変更は<b>LINEで送るだけ</b>。")}
{push(PUSH_H, SPAN_B, ["QRで今のページと見比べる","気に入ったらお電話","打ち合わせで直して公開"])}
</main>
{cta3("<em>「見本を見た」</em>のひとことで大丈夫です。ご相談だけでもどうぞ。" + CALL2, "作り直した<br>御社の見本は<br><em>こちら</em>")}
{fine_wrap(FINE_B)}
</div>"""

out = HEAD + PAGE_A + "\n" + PAGE_B + "\n</body></html>\n"
for bad in ("33,000", "132,000", "ライトプラン", "しっかりプラン", "毎月先着3社", "2営業日以内", "月額は任意", "49,000", "最短7日", ".jp」", "名</em>.jp", "業界最安", "他にない", "どこよりも", "他社に負けない", "Instagram・LINE"):
    assert bad not in out, bad
(D / "letter_v3.html").write_text(out)
print("ok")
