# 調査：HP制作の見た目をプロ並みにする道具（Claude Code から使えるもの）

- 調査日：2026-11-25
- 対象：静的HTML＋FTP公開のサイト（WordPressは補足）
- 表記ルール：**【事実】**＝出典URLあり／**【推測】**＝調べた事実からの判断／**【未確認】**＝確かめられなかったこと
- 調査の制約：この作業環境では gsap.com・ai.google.dev・webflow.com・unpkg.com などに直接アクセスできなかった。そのため一部の料金・ライセンスは「検索結果に出た公式ページの内容」をもとにしている（該当箇所に明記）。npm（ライブラリの公式配布先）では直接確認できた。

---

## 結論（先に）

1. **お金をかけずに今すぐ効果が大きいのは「GSAP＋ScrollTrigger（スクロール連動）」「動画背景（無料素材 or Canvaで生成）」「Playwrightで見た目チェック」の3つ。** どれも追加費用0円。
2. **動画素材はまず今あるCanva連携で足りる見込み。** Canva MCPに画像生成・動画生成の道具があり、商用利用もCanvaのライセンス内でOK。足りない時だけ有料の動画AI（Google Veo など）を検討。
3. 新しい有料契約は不要。Figma MCPは無料枠が小さく、Figmaを使っていないなら不要（重複）。

---

## ① すぐ無料で使えるもの（おすすめ順）

### 1. GSAP ＋ ScrollTrigger（スクロールに合わせた動き）★最優先
- **何ができるか**：スクロールに合わせて文字がふわっと出る、画像がゆっくり拡大する、セクションを固定して中身だけ切り替える、見出しを1文字ずつ出す（SplitText）など、プロの制作会社が使っている動きのほぼすべて。
- **費用**：0円。商用（お客さまのサイト）でも無料。
  - 【事実】npmでの版：3.15.1、ライセンス表記「Standard 'no charge' license」（npmで直接確認 2026-11-25）
  - 【事実・検索結果経由】Webflow社がGSAPを買収後「100%無料化」。以前は有料会員限定だった SplitText・MorphSVG なども商用無料。 https://webflow.com/blog/gsap-becomes-free ／ https://gsap.com/community/standard-license/
  - 【事実・検索結果経由】禁止されているのは「コードを書かずにアニメーションを作れる、Webflowと競合するツール」に組み込むこと。お客さまのHPに使うのは対象外。
  - 【注意】オープンソース（MIT）ではなく独自ライセンス。権利はWebflow社。
- **やり方**：
  1. HTMLの `</body>` の直前に読み込みを2行入れる
     ```html
     <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/gsap.min.js"></script>
     <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/ScrollTrigger.min.js"></script>
     ```
  2. Claude Code に「見出しと段落を、画面に入ったら下から20pxふわっと出す。GSAPとScrollTriggerで。prefers-reduced-motion の人には動かさない」と指示。
  3. Playwright（下の3）でスマホ幅とPC幅のスクリーンショットを撮って確認。

### 2. 動画背景（いま「画像が流れている」部分の置き換え）
- **何ができるか**：トップの大きな画像を、10秒前後の無音ループ動画に。工事現場・料理・店内の雰囲気が一気にプロっぽくなる。
- **費用**：0円（無料素材 or Canva生成。Canvaは月のAI利用枠を使う）。
- **スマホで自動再生させる条件**：
  - 【事実】iPhone（Safari）では `playsinline` がないと全画面再生になる。 https://webkit.org/blog/6784/new-video-policies-for-ios/
  - 【事実】iPhoneの「低電力モード」では、無音でも自動再生が止まり再生ボタンが出る。回避策はない。 https://bugs.webkit.org/show_bug.cgi?id=216887
  - → **ポスター画像（最初の1コマ）を必ず設定**して、止まっても見た目が崩れないようにする。
- **やり方（定番の書き方）**：
  ```html
  <video class="hero-video" autoplay muted loop playsinline preload="metadata"
         poster="img/hero-poster.webp">
    <source src="video/hero.webm" type="video/webm">
    <source src="video/hero.mp4"  type="video/mp4">
  </video>
  ```
  - 「動きを減らす」設定の人（`prefers-reduced-motion: reduce`）には動画を消してポスターだけ表示。
  - 文字が読めるよう、動画の上に半透明の黒（30〜50%）を重ねる。
- **軽量化（ffmpeg。Claude Codeが実行できる）**：
  ```bash
  # mp4（音を消す・横1280・24コマ・ネット再生向け）
  ffmpeg -i 元.mp4 -an -vf "scale=1280:-2,fps=24" -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -movflags +faststart hero.mp4
  # webm（さらに軽い）
  ffmpeg -i 元.mp4 -an -vf "scale=1280:-2,fps=24" -c:v libvpx-vp9 -crf 38 -b:v 0 hero.webm
  # ポスター画像（1秒目）
  ffmpeg -ss 1 -i hero.mp4 -frames:v 1 -q:v 3 hero-poster.jpg
  ```
  - 【推測】目安は 8〜15秒・720p〜1080p・1本 2〜4MB以内。これより重いとスマホで表示が遅れる。実測（PageSpeed Insights）で確認する。
- **素材の入手先（無料・商用OK・クレジット表記不要）**：
  - 【事実】Pexels：商用・改変OK、クレジット不要。ただし写っている人・ロゴ等の許可は保証されない。 https://www.pexels.com/terms-of-service/
  - 【事実】Pixabay：商用・改変OK、クレジット不要。素材のまま転売は不可。人物・ロゴ・ブランドは別途権利の可能性。 https://pixabay.com/service/license-summary/
  - いちばん良いのは**お客さま自身の現場をスマホで10秒撮影**してもらうこと（権利の心配ゼロ・本物感が出る）。【推測】ただし営業・手渡しはしない方針なので、LINEで動画を送ってもらう形。

### 3. Playwright MCP（Claude Code が自分でブラウザを開いて見た目チェック）
- **何ができるか**：Claude Codeがサイトを開き、スマホ幅・PC幅でスクリーンショットを撮って崩れを自分で直す。動きの確認、リンク切れ確認にも。
- **費用**：0円。【事実】ライセンス Apache-2.0、版 0.0.86（npmで確認 2026-11-25）
- **やり方**：
  1. パソコンのターミナルで1回だけ：
     ```bash
     claude mcp add playwright -- npx @playwright/mcp@latest
     ```
     【事実】公式手順 https://playwright.dev/docs/getting-started-mcp
  2. Claude Codeを起動し直し、`/mcp` で playwright が出ていればOK。
  3. 指示例：「index.html を開いて、幅375pxと1440pxでスクリーンショットを撮り、崩れを直して」
  - 必要：Node.js 20以上（推奨）。

### 4. frontend-design プラグイン（Anthropic公式：デザインの質を上げる）
- **何ができるか**：Claude Code がページを作る前に「デザインの方向性（配色・文字・余白・個性）」を考える手順を足す。ありきたりな"AIっぽい"見た目を避けやすくなる。動きのコードが正しいかは見ないので、Playwrightと併用。
- **費用**：0円。
- **やり方**：
  1. Claude Code で `/plugin install frontend-design@claude-plugins-official`
     - 【事実】公式マーケットプレイス名は `claude-plugins-official`、インストール手順。 https://code.claude.com/docs/en/discover-plugins
     - 【事実】プラグイン紹介ページ https://claude.com/marketplace/plugins/frontend-design （中身はAnthropic公式リポジトリ内。検索結果で確認）
  2. クラウドのセッションで使うときは https://claude.ai/customize/plugins で追加してから新しいセッションを始める（公式ドキュメント記載）。
  3. 自動で働く（コマンドを打つ必要なし）。

### 5. その他の無料ライブラリ（必要に応じて）
| 名前 | できること | 商用 | 静的サイト向き | 確認 |
|---|---|---|---|---|
| Lenis | スクロールをぬるっと滑らかにする（高級感）。GSAPと相性が良い | 無料（MIT） | ◎ CDN1行 | npm 1.3.28 / MIT |
| Swiper | スライダー（施工事例・お客様の声） | 無料（MIT） | ◎ | npm 14.4.0 / MIT |
| AOS | 属性を書くだけで「ふわっと出る」 | 無料（MIT） | ◎ ただしGSAPで代用できるので重複 | npm 2.3.4 / MIT。長く更新がない【未確認：最終更新日】 |
| Lottie（dotlottie-web） | 軽いアニメーションアイコン・イラスト | 無料（MIT） | ○ | npm 0.83.2 / MIT。素材はLottieFiles等（素材ごとにライセンス確認） |
| Three.js | 3D表現（回る商品、粒子の背景） | 無料（MIT） | △ 重い・作業量大。5.5万〜13.2万円の案件には過剰【推測】 | npm 0.187.0 / MIT |

- **重複の指摘**：AOS と GSAP は役割がかぶる。GSAPに一本化するのがおすすめ（覚えることが1つで済む）。

### 6. Canva MCP（すでに連携済み・画像も動画も作れる）
- **何ができるか**（このセッションで道具の中身を確認 2026-11-25）：
  - `generate-image`：文章から画像を生成（16:9 など比率指定可）。ヒーロー画像、背景、イラスト。
  - `create-video`：動画を生成。**5〜30秒、16:9 または 9:16、画質は 480p か 720p**（エンジン：seedance）。
  - `generate-design`／`export-design`：デザインを作ってMP4・PNG等で書き出し。
- **費用**：今のCanvaの契約内。ただし動画生成は**月のAI利用枠を大きく使う**（道具の説明に明記）。
- **商用利用**：【事実】Canva AIで作った画像・動画は、Canvaのコンテンツライセンス契約の範囲でお客さまのHPに商用利用できる（Canvaヘルプの回答）。 https://www.canva.com/trust/legal/
- **足りるか**：【推測】背景動画は上に暗い膜と文字を重ねるので720pでも実用上ほぼ問題ない。ただし大画面PCではやや粗く見える可能性。まずCanvaで1本作って実物で判断 → 足りなければ下の有料AIへ。
- **やり方**：Claudeに「〇〇塗装のトップ用に、外壁を塗る職人の手元、ゆっくり横移動、16:9、10秒、文字なし、720pで動画を作って」と頼む → MP4をダウンロード → 上の ffmpeg で軽量化 → サイトへ。

---

## ② お金がかかるもの（契約・登録はしていない。使うならオーナー承認が必要）

料金は確認日 2026-11-25。いずれも**検索結果経由**（公式ページを直接開けなかった）なので、契約前に公式で再確認すること。

| サービス | 料金の目安 | 10秒動画1本の目安 | API（Claudeから指示） | 出典 |
|---|---|---|---|---|
| Google Veo 3.1 Fast（Gemini API） | 720p 約$0.10/秒、1080p 約$0.12/秒 | 約$1〜1.2（約150〜180円）×やり直し回数 | あり | https://benchlm.ai/media-pricing/veo （Google公式価格ページを引用） ※Veo 3.1プレビュー版終了・後継モデルの情報もあり【未確認】 |
| Runway（gen4_turbo） | 5クレジット/秒、1クレジット≒$0.01 → 約$0.05/秒。最初に$10の前払い | 約$0.5（約75円） | あり | https://docs.dev.runwayml.com/guides/pricing/ |
| Kling（3.0） | 1ユニット$0.14。1080pで約0.8ユニット/秒 | 約$1.1（約170円） | あり（前払いパック） | https://www.atlascloud.ai/blog/tips/kling-ai-api-pricing 等（第三者）【公式未確認】 |
| Luma（Ray 3.2） | 5秒単位課金。720pで5秒$0.30、1080pで5秒$1.20 | 720pで$0.6 | あり | https://lumalabs.ai/api.md |
| 画像生成：Gemini「Nano Banana 2」 | 1K画像 約$0.067、2K 約$0.101 | ― | あり | https://benchlm.ai/media-pricing/nano-banana |
| Figma MCP | 無料枠は月数回〜20回程度。実用には有料の Dev/Full 席 | ― | ― | https://developers.figma.com/docs/figma-mcp-server/plans-access-and-permissions |

- **Claudeからの使い方**：APIキーを環境に登録（Claudeは値を見ない安全な入力画面がある）→ Claude Code が短いスクリプトで生成依頼 → 動画を受け取り軽量化 → サイトに配置、まで自動にできる。
- **商用利用**：Runway・Kling・Luma・Veo の「生成物を商用で使ってよいか」の条件は今回確認できず【未確認】。契約前に各社の利用規約を確認する。
- **元が取れる条件**【推測】：1サイトで動画背景1本、やり直し3〜5回でも 約$2〜6（300〜900円）。HP1件の受注（55,000円〜）につながるなら十分に元が取れる。**Canvaの720pで質が足りない時・Canvaの月の枠を使い切った時だけ**使えばよい。
- **使わなくてよいもの**：Figma（使っていなければ重複）。Claude Motion（Anthropicのアニメ動画機能。コードで文字・図形を動かすもので実写映像は作れない。ベータで Team/Enterprise 向けとの情報） https://runway.com/news/company-news/runway-claude-motion 【利用可否は未確認】

---

## ③ 見本サイト1つに入れるならこの組み合わせ（全部無料）

例：塗装・工務店・飲食店などの地元企業トップページ

1. **ファーストビュー**：Canvaで作った10秒の無音ループ動画（または本人撮影）＋暗い膜＋大きなキャッチコピー。コピーは1文字ずつ（または1行ずつ）ふわっと表示（GSAP SplitText）。
2. **スクロール全体**：Lenis で滑らかスクロール。
3. **各セクション**：見出し・本文・写真が画面に入ったら下からふわっと（ScrollTrigger）。数字（創業年数・施工件数）はカウントアップ。
4. **施工事例**：横に流れる写真を Swiper のスライダーに（スマホで指でめくれる）。
5. **「選ばれる理由」**：セクションを画面に固定し、スクロールで3つの理由が順に切り替わる（ScrollTrigger の pin）。
6. **仕上げ**：Playwrightでスマホ375px／PC1440pxを撮影して確認 → PageSpeed Insights（ https://pagespeed.web.dev/ ）で重さを実測。

Claude Code への指示文の例（コピーして使える）：
> トップの背景画像スライドを、video/hero.mp4 の無音ループ動画背景に置き換えて。autoplay muted loop playsinline、poster画像つき、動きを減らす設定の人には動画を出さない。見出しはGSAPのSplitTextで1行ずつふわっと出す。各セクションはScrollTriggerで画面に入ったら下から20pxフェードイン。Lenisで滑らかスクロール。終わったらPlaywrightで幅375pxと1440pxのスクリーンショットを撮って崩れを直して。

---

## ④ 注意点

- **表示の重さ**：動画は1本2〜4MB以内を目安（推測）。ライブラリはGSAP＋Lenis＋Swiperで十分。Three.jsや動きの盛りすぎは遅くなり、Googleの評価も下がる可能性。必ず PageSpeed Insights で実測。
- **スマホ**：iPhoneの低電力モードでは動画が止まる（回避不可）→ ポスター画像必須。スマホでは動きを控えめに。
- **見る人への配慮**：`prefers-reduced-motion`（動きを減らす設定）を尊重する。動きで酔う人がいる。
- **著作権・商用**：
  - Pexels・Pixabay は商用OKだが、写っている人物・ロゴ・建物の権利までは保証されない。
  - Canva AIの生成物はCanvaのライセンス範囲で商用OK。
  - 有料動画AIの商用条件は未確認 → 使う前に規約確認。
  - GSAPは無料だが独自ライセンス（「ノーコードのアニメ作成ツール」に組み込むのは禁止。HP制作は対象外）。
- **WordPressを使う場合（簡単に）**：
  - 標準のブロックテーマ（例：WordPress標準の Twenty Twenty-Five）＋アニメーション用の無料プラグインで対応可能。
  - 【事実】「Animations for Blocks」（AOS使用、Lenisの滑らかスクロールも同梱） https://wordpress.org/plugins/animations-for-blocks/
  - 【事実】「Animora: Animations for Blocks」（CSSのみで軽い） https://wordpress.org/plugins/animora/
  - GSAPを使う無料の定番プラグインは見つからなかった → 使うならテーマに自分で読み込む。
  - 【推測】動きの自由度・表示の速さ・保守の手間を考えると、5.5万〜13.2万円の案件は今の静的HTMLのほうが有利。WordPressは「お客さま自身がブログ更新したい」場合に限定するのが無難。

---

## 調べた出典一覧
- Claude Code プラグイン公式：https://code.claude.com/docs/en/discover-plugins
- frontend-design：https://claude.com/marketplace/plugins/frontend-design
- Playwright MCP：https://playwright.dev/docs/getting-started-mcp
- GSAP無料化：https://webflow.com/blog/gsap-becomes-free ／ https://gsap.com/community/standard-license/
- iOS動画ポリシー：https://webkit.org/blog/6784/new-video-policies-for-ios/ ／ https://bugs.webkit.org/show_bug.cgi?id=216887
- Pexels：https://www.pexels.com/terms-of-service/ ／ Pixabay：https://pixabay.com/service/license-summary/
- Canva：https://www.canva.com/trust/legal/ ／ https://www.canva.com/help/mcp-canva-usage/
- Veo：https://benchlm.ai/media-pricing/veo ／ Runway：https://docs.dev.runwayml.com/guides/pricing/ ／ Luma：https://lumalabs.ai/api.md ／ Kling：https://www.atlascloud.ai/blog/tips/kling-ai-api-pricing
- Nano Banana：https://benchlm.ai/media-pricing/nano-banana
- Figma MCP：https://developers.figma.com/docs/figma-mcp-server/plans-access-and-permissions
- WordPress：https://wordpress.org/plugins/animations-for-blocks/ ／ https://wordpress.org/plugins/animora/
- ライブラリの版・ライセンス：npm（`npm view` で 2026-11-25 確認）
