# -*- coding: utf-8 -*-
"""
AI顧問（月額）セクションの見本HTMLを作るスクリプト。
元ページ: 元ページ/ai_index_original.html （2026-11-20 に https://www.turtle-ad.com/ai/ から取得）
出力   : ai_index_komon_sample.html
既存の文章は消さず、追加と見出し番号の繰り下げ（04→05, 05→06）だけを行う。
実行: python3 -I build_sample.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / "元ページ" / "ai_index_original.html").read_text(encoding="utf-8")
out = src


def rep(old, new, count=1):
    global out
    n = out.count(old)
    if n != count:
        raise SystemExit(f"置き換え対象の数が想定と違います ({n}件): {old[:60]!r}")
    out = out.replace(old, new)


# ---------- 1. CSS（料金のCSSの後ろ、よくある質問のCSSの前に追加） ----------
CSS = r"""
/* ===== AI顧問（月額）【追加】 ===== */
.km-sec{background:linear-gradient(180deg,var(--bg) 0%,#0a1330 45%,var(--bg) 100%);overflow:hidden}
.km-sec::before{content:"";position:absolute;width:760px;height:760px;max-width:130vw;left:-260px;top:18%;background:radial-gradient(circle,rgba(79,227,255,.12),transparent 65%);pointer-events:none}
.km-points{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(16px,2vw,28px);margin-bottom:clamp(48px,6vw,80px);position:relative}
.km-point{padding:26px 24px;border-top:2px solid var(--cyan);background:linear-gradient(180deg,rgba(79,227,255,.07),transparent)}
.km-point .k{font-family:var(--en);font-size:12px;letter-spacing:.25em;color:var(--cyan)}
.km-point h3{font-size:clamp(18px,1.8vw,21px);font-weight:900;margin:6px 0 8px;line-height:1.5}
.km-point p{font-size:14px;color:#b9c4e2}
.km-plans{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(16px,2vw,28px);align-items:stretch;position:relative}
.km-plans .plan{grid-column:auto;display:flex;flex-direction:column;padding:34px 26px 28px}
.km-badge{position:absolute;top:-14px;left:50%;transform:translateX(-50%);font-size:13px;font-weight:900;color:#04101c;background:linear-gradient(90deg,var(--cyan),#9fb6ff);padding:4px 18px;border-radius:999px;white-space:nowrap;box-shadow:0 6px 24px rgba(79,227,255,.35)}
.km-for{font-size:14px;color:var(--muted);margin:-8px 0 16px;line-height:1.6}
.km-tax{display:block;margin-top:8px;font-size:13px;color:var(--muted)}
.km-block{margin-top:20px;border-top:1px solid var(--line);padding-top:14px}
.km-label{font-size:12px;font-weight:700;letter-spacing:.1em;color:var(--cyan)}
.km-block ul{list-style:none;margin-top:4px;border:0;padding:0}
.km-plans .plan li{margin:6px 0}
.km-ex{margin-top:20px;padding:16px 16px 12px;border-radius:6px;background:rgba(79,227,255,.06);border:1px dashed rgba(79,227,255,.35)}
.km-ex .km-label{color:#d4ddf5}
.km-ex .km-label b{color:var(--cyan);font-family:var(--en);font-size:15px}
.km-ex ul{list-style:none;margin-top:6px;border:0;padding:0}
.km-ex li{position:relative;padding-left:18px;font-size:14px;color:#c2cdea;margin:7px 0;line-height:1.65}
.km-ex li::before{content:"";position:absolute;left:2px;top:.55em;width:7px;height:7px;border-right:2px solid var(--cyan);border-bottom:2px solid var(--cyan);transform:rotate(-45deg);background:none;box-shadow:none;border-radius:0}
.km-term{margin-top:auto;padding-top:18px;font-size:13px;color:var(--muted)}
.km-term b{color:var(--text)}
.km-diag{margin-top:clamp(28px,4vw,48px);display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px 40px;align-items:center}
.km-diag .plan-price{font-size:clamp(34px,3.4vw,44px)}
.km-diag h3 small{display:inline-block}
.km-diag p{color:#b9c4e2;font-size:15px;margin-top:4px}
.km-diag ul{display:flex;flex-wrap:wrap;gap:4px 24px;margin-top:12px;border:0;padding:0}
.km-diag .km-sep{font-size:13px;color:var(--muted)}
.km-notes{margin-top:28px;font-size:13px;color:var(--muted);line-height:1.9}
.km-cta{margin-top:36px;display:flex;flex-wrap:wrap;gap:16px 24px;align-items:center}
.km-cta p{font-weight:700;color:#d4ddf5}
.btn-line{display:inline-flex;align-items:center;gap:10px;padding:11px 24px;border-radius:999px;text-decoration:none;font-weight:700;font-size:14px;color:var(--text);border:1px solid rgba(6,199,85,.7);background:rgba(6,199,85,.10);transition:background .2s,transform .2s}
.btn-line:hover{background:rgba(6,199,85,.2);transform:translateY(-2px)}
.btn-line::before{content:"";width:8px;height:8px;border-radius:50%;background:#06C755;box-shadow:0 0 10px rgba(6,199,85,.8)}
.way.line .way-label{color:#3ee08a}
.way.line:hover{border-color:#06C755;box-shadow:0 12px 40px rgba(6,199,85,.18)}
.plan .more{display:inline-block;margin-top:14px;font-size:14px;font-weight:700;color:var(--cyan);text-decoration:none;border-bottom:1px solid rgba(79,227,255,.4)}
@media (max-width:860px){
  .km-points{grid-template-columns:minmax(0,1fr);gap:12px}
  .km-plans{grid-template-columns:minmax(0,1fr);gap:34px}
  .km-diag{grid-template-columns:minmax(0,1fr)}
}

"""
rep("/* ===== よくある質問 ===== */", CSS.lstrip("\n") + "/* ===== よくある質問 ===== */")

# ---------- 2. ページ内メニュー・フッターに「AI顧問」を追加 ----------
rep('    <a href="#flow">ご相談の流れ</a>\n    <a href="#price">料金</a>',
    '    <a href="#flow">ご相談の流れ</a>\n    <a href="#komon">AI顧問</a>\n    <a href="#price">料金</a>')
rep('        <a href="#flow">ご相談の流れ</a>\n        <a href="#price">料金</a>',
    '        <a href="#flow">ご相談の流れ</a>\n        <a href="#komon">AI顧問</a>\n        <a href="#price">料金</a>')

# ---------- 3. AI顧問セクション（「ご相談の流れ」と「料金の目安」の間） ----------
def plan_list(items):
    return "\n".join(f"              <li>{i}</li>" for i in items)


def plan(cls, en, name, who, price, consult, work, price_label, examples, term, badge=False):
    badge_html = '\n        <span class="km-badge">おすすめ</span>' if badge else ""
    work_html = ""
    if work:
        work_html = f"""
        <div class="km-block">
          <div class="km-label">作業込み（タートルアドが作ります）</div>
          <ul>
{plan_list(work)}
          </ul>
        </div>"""
    return f"""      <article class="plan {cls} rv">{badge_html}
        <div class="plan-name">{en}</div>
        <h3>{name}</h3>
        <p class="km-for">{who}</p>
        <div class="plan-price"><span class="pre">月額</span>{price}<span>円</span></div>
        <span class="km-tax">（税込）</span>
        <div class="km-block">
          <div class="km-label">ご相談</div>
          <ul>
{plan_list(consult)}
          </ul>
        </div>{work_html}
        <div class="km-ex">
          <div class="km-label">月額<b>{price_label}</b>円で、たとえば</div>
          <ul>
{plan_list(examples)}
          </ul>
        </div>
        <p class="km-term">最低契約期間 <b>{term}</b></p>
      </article>"""


plans = "\n".join([
    plan("", "LIGHT", "ライト", "まずは社内でAIを使い始めたい",
         "22,000",
         ["オンライン相談 月1回", "LINE相談 月10件まで"],
         [],
         "22,000",
         ["よく来るメールの返信文を、AIで下書きする手順を一緒に作る",
          "求人文やSNS投稿を、メモから作るためのひな形を整える",
          "「この作業、AIでできる？」をLINEで気軽に聞ける"],
         "3か月"),
    plan("hot", "STANDARD", "スタンダード", "仕事を変えて、集客も任せたい",
         "55,000",
         ["訪問 月1回＋オンライン 月1回", "LINE相談 回数制限なし"],
         ["AIで作る紹介動画 月2本", "Google検索広告の運用", "社員さん向け講習（3か月に1回）"],
         "55,000",
         ["物件や商品の紹介文を、写真とメモからAIで作る仕組みを社内に入れる",
          "毎月2本の紹介動画を、SNSやホームページですぐ使える形でお渡し",
          "検索広告の言葉を見直しながら、問い合わせにつながる形を探る"],
         "6か月", badge=True),
    plan("", "FULL SUPPORT", "しっかり", "AIを会社全体の土台にしたい",
         "110,000",
         ["訪問 月2回＋オンライン 月1回", "LINE相談 回数制限なし"],
         ["AIで作る紹介動画 月4本", "Google検索広告の運用＋毎月の報告", "社員さん向け講習（毎月）"],
         "110,000",
         ["部署ごとの仕事の流れを見直し、AIに任せる作業を毎月少しずつ増やす",
          "紹介動画を月4本。商品・求人・会社紹介など、使い道に合わせて作る",
          "広告の結果を毎月ご報告し、次の月にやることを一緒に決める"],
         "6か月"),
])

SECTION = f"""<!-- ===== 4. AI顧問（月額）【追加】 ===== -->
<section class="sec km-sec" id="komon">
  <div class="wrap">
    <div class="sec-head rv">
      <span class="sec-en" aria-hidden="true">ADVISOR</span>
      <h2 class="sec-title"><span class="num">04</span>AI顧問（月額）</h2>
      <p class="sec-desc">AIの使い方を覚えるだけで終わらせず、御社の仕事のやり方を一緒に見直します。手間を減らして、売上につながる仕事に時間を使えるように。相談だけでなく、動画・文章・広告づくりもタートルアドがお引き受けします。</p>
    </div>

    <div class="km-points">
      <div class="km-point rv">
        <div class="k">POINT 01</div>
        <h3>仕事の流れから見直す</h3>
        <p>今のやり方をお聞きして、AIに任せられるところと、人がやるところを一緒に決めます。</p>
      </div>
      <div class="km-point rv">
        <div class="k">POINT 02</div>
        <h3>社内の仕組みにして残す</h3>
        <p>頼み方のひな形や手順をまとめて、社員さんが同じように使える形にします。</p>
      </div>
      <div class="km-point rv">
        <div class="k">POINT 03</div>
        <h3>手が回らない作業は代わりに</h3>
        <p>紹介動画・文章・Google検索広告など、作る作業もタートルアドがお引き受けします。</p>
      </div>
    </div>

    <div class="km-plans">
{plans}
    </div>

    <article class="plan km-diag rv">
      <div>
        <div class="plan-name">WORK REVIEW</div>
        <h3>業務の見直し診断 <small>（顧問とは別のメニュー）</small></h3>
        <p>「顧問の前に、まず一度見てほしい」という方へ。今の仕事の流れをお聞きして、AIで楽になるところを洗い出します。</p>
        <ul>
          <li>今の仕事の流れの聞き取り</li>
          <li>AIで楽になるところの洗い出し</li>
        </ul>
      </div>
      <div class="plan-price">33,000<span>円</span><span class="km-tax">（税込）</span></div>
    </article>

    <p class="km-notes">
      ※料金はすべて税込です。AI顧問は月額です。<br>
      ※訪問は鹿児島県内（離島を除く）です。それ以外の地域は、Zoomなどのオンラインで全国対応します。<br>
      ※LINE相談は、受付時間（9:00〜18:00、土日祝休み）内に順にお返事します。<br>
      ※Google検索広告の広告費（Googleにお支払いいただく分）は、月額とは別にかかります。<br>
      ※AIで作った文章や動画は、内容を人が確認してからお渡しします。
    </p>

    <div class="km-cta rv">
      <p>どのプランが合うかは、無料の初回相談で一緒に考えます。</p>
      <a class="btn" href="#contact">無料で相談する <span aria-hidden="true">→</span></a>
      <a class="btn-line" href="https://line.me/R/ti/p/@486zunqz" target="_blank" rel="noopener">LINEで相談する</a>
    </div>
  </div>
</section>

<!-- ===== 5. 料金の目安 ===== -->"""
rep("<!-- ===== 4. 料金の目安 ===== -->", SECTION)

# ---------- 4. 見出し番号の繰り下げ ----------
rep('<span class="num">04</span>料金の目安', '<span class="num">05</span>料金の目安')
rep('<!-- ===== 5. よくある質問 ===== -->', '<!-- ===== 6. よくある質問 ===== -->')
rep('<span class="num">05</span>よくある質問', '<span class="num">06</span>よくある質問')
rep('<!-- ===== 6. お問い合わせ ===== -->', '<!-- ===== 7. お問い合わせ ===== -->')

# ---------- 5. 料金の目安に AI顧問・診断のカードを追加（研修カードのあと） ----------
PRICE_CARDS = """      <article class="plan wide rv">
        <div class="plan-name">AI ADVISOR</div>
        <h3>AI顧問 <small>（月額・3プラン）</small></h3>
        <div class="plan-price"><span class="pre">月額</span>22,000<span>円〜</span></div>
        <ul>
          <li>ライト 22,000円</li>
          <li>スタンダード 55,000円（おすすめ）</li>
          <li>しっかり 110,000円</li>
        </ul>
        <a class="more" href="#komon">プランの内容を見る →</a>
      </article>
      <article class="plan wide rv">
        <div class="plan-name">WORK REVIEW</div>
        <h3>業務の見直し診断</h3>
        <div class="plan-price">33,000<span>円</span></div>
        <ul>
          <li>今の仕事の流れをお聞きして、AIで楽になるところを洗い出します</li>
        </ul>
      </article>
      <article class="plan rv">
        <div class="plan-name">WEB SITE</div>"""
rep("""      <article class="plan rv">
        <div class="plan-name">WEB SITE</div>""", PRICE_CARDS)

# ---------- 6. よくある質問を追加（最後の質問の前） ----------
FAQ = """      <details>
        <summary><span class="q">Q</span>研修とAI顧問は、何が違いますか？</summary>
        <p class="a">研修は、2時間でAIの使い方を練習する講座です。AI顧問は毎月つづけて、御社の仕事の流れを一緒に見直しながら、紹介動画や広告などの作業もお引き受けします。</p>
      </details>
      <details>
        <summary><span class="q">Q</span>鹿児島県外でもAI顧問を頼めますか？</summary>
        <p class="a">はい。訪問は鹿児島県内（離島を除く）ですが、それ以外の地域はZoomなどのオンラインで、全国どこでも対応します。</p>
      </details>
      <details>
        <summary><span class="q">Q</span>AI顧問の最低契約期間はありますか？</summary>
        <p class="a">ライトは3か月、スタンダードとしっかりは6か月です。</p>
      </details>
      <details>
        <summary><span class="q">Q</span>料金は、このページの金額で決まりですか？</summary>"""
rep("""      <details>
        <summary><span class="q">Q</span>料金は、このページの金額で決まりですか？</summary>""", FAQ)

# ---------- 6b. 公開用の追加（2026-11-20 オーナー承認） ----------
LINE_URL = "https://line.me/R/ti/p/@486zunqz"
# お問い合わせ欄に LINE ボタン（電話とメールの間）
rep("""      </a>
      <a class="way" href="mailto:info@turtle-ad.com?subject=""",
    f"""      </a>
      <a class="way line" href="{LINE_URL}" target="_blank" rel="noopener">
        <span class="way-label">LINE</span>
        <span class="way-main">LINEで相談する</span>
        <span class="way-sub">公式LINEから、お気軽にメッセージください</span>
      </a>
      <a class="way" href="mailto:info@turtle-ad.com?subject=""")
rep("AI活用の初回相談は無料です。お電話かメールでご連絡ください。",
    "AI活用の初回相談は無料です。お電話・LINE・メールでご連絡ください。")
# ご相談の流れ
rep("<p>お電話かメールで、お気軽にご連絡ください。", "<p>お電話・LINE・メールで、お気軽にご連絡ください。")
rep('<span class="term">電話・メール</span>', '<span class="term">電話・LINE・メール</span>')
rep("研修の内容やホームページの作業の範囲を決めて", "研修・AI顧問の内容やホームページの作業の範囲を決めて")
rep("<h3>研修・制作のスタート</h3>", "<h3>研修・顧問・制作のスタート</h3>")
rep("ホームページは、内容を確認していただきながら進めます。</p>",
    "AI顧問では、毎月のご相談で仕事の流れを一緒に見直します。ホームページは、内容を確認していただきながら進めます。</p>")
rep('<span class="term">研修・制作</span>', '<span class="term">研修・顧問・制作</span>')
# ページ説明文（description / og:description）
rep("少人数研修（2時間・33,000円〜税込）で、", "少人数研修（2時間・33,000円〜税込）、AI顧問（月額）で、", count=2)

PUB_DIR = HERE / "公開用" / "ai"
PUB_DIR.mkdir(parents=True, exist_ok=True)
(PUB_DIR / "index.html").write_text(out, encoding="utf-8")
print("public ok", len(out))

# ---------- 7. 見本として手元で開けるように ----------
# ロゴ用CSSは本番の相対パス（../assets/logo.css）だと手元で読めないため、見本だけ絶対URLにする。
# 公開時は ../assets/logo.css に戻すこと。
rep('<link rel="stylesheet" href="../assets/logo.css">',
    '<!-- 見本用：本番では ../assets/logo.css に戻す -->\n<link rel="stylesheet" href="https://www.turtle-ad.com/assets/logo.css">')
rep('<title>AI活用サポート・ChatGPT研修｜鹿児島｜合同会社turtle ad</title>',
    '<title>【見本・未公開】AI活用サポート・ChatGPT研修｜鹿児島｜合同会社turtle ad</title>\n<meta name="robots" content="noindex">')

(HERE / "ai_index_komon_sample.html").write_text(out, encoding="utf-8")
print("ok", len(out))
