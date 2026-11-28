# Googleマップ（ローカル検索）の順位に、口コミ以外で影響するもの・ツール

調査日：2026-11-28（営業担当）
表示ルール：【公式（Google）】＝Googleのヘルプ・ブログ等に書いてある／【業界調査】＝公式ではないが専門家の調査・実験／【未検証】＝出典が二次情報だけ、または確認しきれていない／【推測】＝営業担当の考え

## 調べ方についての注意（正直に書きます）
- Googleのヘルプ（support.google.com）は直接開いて原文を確認した。
- **whitespark.ca と sterlingsky.ca は、この作業環境のネット設定で開けなかった**（接続先が許可されていない）。この2社の内容は「検索結果の抜粋」と「それを紹介した記事（Search Engine Roundtable、Search Engine Land など）」で確認した。数字の細部は原文で再確認が必要。原文を読みたい場合は、作業環境の設定で whitespark.ca と www.sterlingsky.ca を許可する必要がある。

---

## 1. Google公式の説明

### 1-1. 順位は「関連性・距離・知名度」で決まる【公式（Google）】
出典：https://support.google.com/business/answer/7091?hl=ja （直接確認）
- 「ローカル検索結果は、主に関連性、距離、知名度に基づいて表示されます。」
- 関連性＝検索語句とプロフィールが合う度合い。距離＝検索した人からお店までの距離。知名度＝どれだけ広く知られているか。
- 知名度は「ビジネスにリンクしているウェブサイトの数やクチコミの数などの情報にも基づいています」。→ **口コミ以外では「リンクしているウェブサイトの数」が公式に名前が出ている唯一の具体的な要因。**
- 「ビジネス情報の内容が充実していて正確なほど、ローカル検索結果に表示される可能性が高くなります。」
- 「Google では、ランキングを上げるためのリクエストや金銭の受け取りには一切応じておりません。」→ お金でGoogleに順位を上げてもらう方法は存在しない。

### 1-2. 同じページの「順位を上げるヒント」【公式（Google）】
出典：同上（日本語版・英語版 https://support.google.com/business/answer/7091?hl=en を直接確認）
1. オーナー確認をする（英語版：確認すると検索結果に表示されやすくなる、と明記）
2. 情報を最新にする（住所・営業時間〈特別営業時間を含む〉・カテゴリ・属性〈駐車場・Wi-Fiなど〉）
3. 口コミに返信する（※返信が順位に効くとは書いていない。「フィードバックを重視していることをアピールできる」という書き方）
4. 写真や動画を追加する（※順位との関係は書いていない。「お客さまに伝わる」という書き方）
5. 店舗の商品を追加する（小売店向け・対象国のみ）

### 1-3. 機能ごとの「順位との関係」の公式記載【公式（Google）】
| 機能 | 順位との関係についての公式の記載 |
|---|---|
| オーナー確認 | あり（表示されやすくなる） |
| 住所・営業時間・カテゴリ・属性など基本情報 | あり（充実・正確だと表示されやすい） |
| 被リンク（他サイトからのリンク数） | あり（知名度の材料） |
| 写真・動画 | **公式の記載なし**（ヒントには載っているが順位への効果は書かれていない） |
| 口コミへの返信 | **公式の記載なし**（同上） |
| 投稿（最新情報） | **公式の記載なし** |
| 商品 | **公式の記載なし**（ヒントに載っているのみ） |
| サービス | **公式の記載なし** |
| Q&A | **公式の記載なし**。なお2025年12月、GoogleはマップのQ&Aを縮小し、Geminiによる「質問する（Ask）」ボタンに置き換えると発表（出典：Search Engine Roundtable https://www.seroundtable.com/google-maps-qa-feature-ask-40594.html ／検索結果の抜粋で確認）【業界調査】 |
| ウェブサイト連携・SEO | 現在の7091ページには「SEO」の記載なし（日本語版で直接確認）。以前はこのページに「ウェブ検索結果での掲載順位も要素になる」旨の記載があったとされるが、**今のページでは確認できなかった**【未検証】 |
| 構造化データ（LocalBusiness） | Googleは「構造化データで順位は上がらない」と繰り返し発言（出典：https://www.seroundtable.com/google-structured-data-ranking-39232.html 、https://www.searchenginejournal.com/google-confirms-that-structured-data-wont-make-a-site-rank-better/544433/ ／検索結果の抜粋で確認）【公式発言の二次報道】。マークアップはリッチリザルトの「対象になる」ためのもの（https://developers.google.com/search/docs/appearance/structured-data/local-business ）【公式（Google）】 |

### 1-4. ガイドライン（やってはいけないこと）【公式（Google）】
出典：https://support.google.com/business/answer/3038177?hl=ja ／英語版 ?hl=en（直接確認）
- **ビジネス名**：看板・名刺など実際に使っている名前だけ。「ビジネス名に不要な情報を含めることは認められていない」「プロフィールの停止につながる可能性がある」。キャッチコピー、店舗コード、営業時間、場所の情報、電話番号、URLなどは入れない。
  - 注意：名前の項目に「キーワード」という単語そのものは出てこない。ただし「不要な情報」の例に場所情報やサービス情報が含まれるため、**「鹿児島 ホームページ制作 タートルアド」のように名前へ地名・業種を足すのは違反**と読むのが妥当。住所の項目には「URLやキーワード」を入れないと明記。
- **住所**：実際の所在地。バーチャルオフィス、看板とスタッフ常駐のないコワーキングは不可。同じ拠点に複数のプロフィールは不可。
- **サービス提供地域**：お客さまの所に出向く業態は、住所を非表示にしてサービス提供地域を設定する。
- **カテゴリ**：事業の中核を表す、できるだけ具体的なものを必要最小限。「キーワード」的なカテゴリは不可。
- 違反すると、プロフィールや他のGoogleサービスの利用停止もありうる。

### 1-5. スパム対策（不正な口コミ・偽の利用）【公式（Google）】
- 「偽のエンゲージメント」は禁止：一人が複数アカウントで投稿、エミュレーター等の利用、謝礼と引き換えの口コミ、不自然な量・パターンの口コミ、競合への妨害投稿など。出典：https://support.google.com/contributionpolicy/answer/7400114?hl=ja （検索結果の抜粋で確認）
- 違反が続くと、口コミの一時非公開、「偽の口コミを削除しました」という警告表示などの制限がかかる。出典：https://support.google.com/business/answer/14114287 （検索結果の抜粋で確認）
- Googleの発表：2024年に2億4,000万件超の違反口コミと1,200万件超の偽プロフィールを削除・ブロック。出典：https://blog.google/products/maps/google-business-profiles-ai-fake-reviews/ （検索結果の抜粋で確認）。2025年分は口コミ2億9,200万件・偽プロフィール1,300万件超（Search Engine Roundtable https://www.seroundtable.com/google-maps-spam-fighting-2025-41176.html の報道／抜粋で確認）

### 1-6. Search Liaison（Danny Sullivan氏）の発言
- ビジネス名キーワード・投稿・写真が順位に効くかについての同氏の発言は、**検索では見つからなかった**（公式の記載なし扱い）。

---

## 2. 業界の調査（公式ではないが信頼度の高いもの）

### 2-1. Whitespark「Local Search Ranking Factors 2026」【業界調査】
- 種類：**専門家アンケート**（実験ではない）。2025年11月6日公開、回答者47人の地域SEO専門家（Darren Shaw氏）。
- マップ（ローカルパック）上位の要因（点数）：
  1. メインカテゴリ（227）
  2. 検索地点からの距離（225）
  3. ビジネス名にキーワード（223）※ガイドライン違反のため、正規の名前に元から含まれる場合以外は使えない
  4. 検索した市内に実住所がある（213）
  5. 検索時に営業中である（189）
  - その後に評価の高さ（181）、住所の表示（176）、追加カテゴリ（173）、Google口コミの数（170）、地図ピンの正しい位置（165）、口コミの新しさ（164）
- 要因グループ別の比率は紹介記事によって数字が食い違うため【未検証】。
- 出典：https://whitespark.ca/local-search-ranking-factors/ （開けず、検索結果の抜粋と紹介記事 https://gmbapi.com/news/local-ranking-factors-comparison-2026-2023/ 、https://seomadman.com/reports/whitespark-local-ranking-factors-2026 で確認）

### 2-2. Sterling Sky（Joy Hawkins氏の会社）の実験【業界調査】
種類：**実際のプロフィールでの実験**（件数は少ない）。出典はすべて検索結果の抜粋・紹介記事で確認。
- **投稿**：他の施策をしていない3件で投稿を追加 → 順位の変化は測定できず。「投稿は直接は順位に影響しない」。https://www.sterlingsky.ca/do-google-posts-impact-ranking/
- **写真**：4件に写真追加 → 順位の変化なし。https://www.sterlingsky.ca/photos-ranking-google-my-business/ 。写真の位置情報（ジオタグ）も効果なし（Search Engine Land https://searchengineland.com/geotagging-photos-google-business-profile-rank-453525 ）
- **サービス**：用意された選択肢のサービス（定義済みサービス）は順位に効く、自分で作るサービスも効くが小さい（2024年1月）。https://www.seroundtable.com/custom-google-business-profile-services-impact-rankings-36794.html
- **クリック操作（CTR操作）**：最初は上がるが長続きしない。https://www.sterlingsky.ca/does-ctr-manipulation-work-long-term/
- **口コミ本文のキーワード**：順位に影響しないという調査報道あり。https://www.seroundtable.com/keywords-local-reviews-google-local-rankings-34334.html

### 2-3. BrightLocal【業界調査】
- Vicinityアップデート（2021年12月）の分析：米国391件・5,019データ。キーワードを詰め込んだ名前は平均5.5〜7.9位下落、キーワードなしは平均4.1位上昇。ただし「他の要因を考慮していない」と批判もある。https://www.brightlocal.com/research/vicinity-gbp-spam-impact/
- サイテーション調査（2018年）：上位3位の店は平均85件のサイテーション。**相関で、因果ではない**。https://www.brightlocal.com/research/businesses-ranking-top-3-in-google-local-have-85-citations/

---

## 3. 名前・住所・電話の表記をそろえる（NAP・サイテーション）は効くか

- 【公式（Google）】Googleは「NAP」「サイテーション」という言葉では説明していない。言えるのは「知名度は、リンクしているウェブサイトの数などにも基づく」「情報が正確なほど表示されやすい」まで（7091）。
- 【業界調査】Whitespark 2026でも、サイテーション関連は上位10位に入らない。「ウェブサイトとプロフィールの情報一致」は15位程度とする紹介あり（https://cloutly.com/blog/listing-consistency-nap/ ／抜粋で確認）。BrightLocalの2018年調査は相関のみ。
- 【業界調査】専門家の間では、2013年頃より重要度が下がったという見方が多い（BrightLocal 2013年専門家調査では当時「量より一貫性」が重視）。https://www.brightlocal.com/research/expert-local-citation-survey-2013/
- **結論：根拠の強さは「弱〜中」。** 大きく順位を上げる決め手ではない。ただし表記がバラバラだとお客さまが迷う・情報が誤って上書きされる問題があるので、「主要な数か所だけ正しくそろえる」は低コストでやる価値あり。有料で大量登録するサービスに払う根拠は弱い【推測】。

---

## 4. ツール

### 4-1. 無料・公式
| ツール | できること | 根拠 |
|---|---|---|
| Googleビジネスプロフィールの「パフォーマンス」 | 表示回数、電話・ルート・ウェブサイトのクリック数、**どの検索語句で表示されたか**。オーナー確認済みのプロフィールのみ | 【公式（Google）】https://support.google.com/business/answer/9918094?hl=ja （抜粋で確認） |
| Google Search Console | ウェブ検索での表示回数・クリック・掲載順位（ホームページ側）。**マップの順位そのものは出ない** | 【公式（Google）】https://search.google.com/search-console |
| Business Profile Performance API | 月ごとの検索語句データを取得（API申請が必要） | 【公式（Google）】https://developers.google.com/my-business/reference/performance/rest |

※マップの「何位か」をGoogle公式で地点ごとに測る機能はない。→ 順位を見るには有料ツールか、手で検索して確認する。

### 4-2. 日本のMEOツール（順位計測・管理）【未検証：料金は比較サイトの記載。公式で要確認】
| ツール | 料金の例 | 出典 |
|---|---|---|
| Gyro-n MEO | 順位計測のみ 1店舗 月1,500円（10語・競合1店）、パッケージ 月14,500円（初期5,000円）とする記載あり | https://www.aspicjapan.org/asu/service/9951 、https://www.issoh.co.jp/column/details/16341/ |
| MEOチェキ | エントリー 月3,278円（8語）、プレミアム 月5,478円（10語） | https://www.itreview.jp/products/meocheki/price |
| MEO Dash! byGMO | Professional 月18,750円〜の記載あり。公式は問い合わせ | https://saas.imitsu.jp/cate-seo-tool/service/5867/price |
| カンリー | 「カンリーMEOエージェント」月4,980円（2026年8月開始、AIが運用）と発表 | https://prtimes.jp/main/html/rd/p/000000599.000037205.html |

### 4-3. 「順位を上げる」とうたうツール・業者の実態
- 【公式（Google）】Googleはお金やリクエストで順位を上げない（7091）。だから「順位を上げる」の中身は、プロフィールの入力代行・投稿代行・口コミ集めのどれか。
- 投稿・写真の大量追加は、実験では順位への直接効果が確認されていない（2-2）。
- 口コミの謝礼・自作・業者による大量投稿、クリックの水増しは**規約違反（偽のエンゲージメント）**。口コミ非公開・警告表示などの制限がある（1-5）。CTR操作は効果も長続きしない（2-2）。
- ビジネス名への地名・業種の追加は違反で、停止リスクあり（1-4）。
- 国民生活センターでMEO業者の勧誘トラブルに絞った資料は、今回の検索では見つからなかった。

---

## 5. 結論：turtle adが自社と顧客に「効く根拠がある順」でやること

順位の根拠は【公式】＞【業界調査（実験）】＞【業界調査（アンケート）】の順に強いとみなした。

| 順 | やること | 根拠 | 画面・URL |
|---|---|---|---|
| 1 | オーナー確認を済ませる | 公式 | https://business.google.com/ →「ビジネスを追加」→確認方法を選ぶ（手順：https://support.google.com/business/answer/7107242?hl=ja ） |
| 2 | **メインカテゴリを最も具体的なものに**、追加カテゴリは必要最小限 | 公式（カテゴリは関連性の材料）＋Whitespark 1位 | Googleで自社名を検索→「プロフィールを編集」→「ビジネス情報」→「カテゴリ」 |
| 3 | 住所・サービス提供地域を正しく（出張型は住所非表示＋地域設定）、地図ピンの位置確認 | 公式ガイドライン＋Whitespark上位 | 同「プロフィールを編集」→「所在地」「サービス提供地域」 |
| 4 | 営業時間・特別営業時間（祝日・年末年始）を正確に | 公式＋Whitespark 5位（営業中かどうか） | 同「営業時間」「特別営業時間」 |
| 5 | 属性・ビジネスの説明・電話・ウェブサイトを埋める | 公式（充実・正確） | 同「ビジネス情報」「その他」 |
| 6 | **サービスを「定義済み（選択肢）」から追加**、足りない分だけ自作 | Sterling Sky実験（公式の記載なし） | 同「サービスを編集」 |
| 7 | ホームページを整え、地域のサイト（商工会・地域情報誌のWeb版・取引先など）からリンクをもらう | 公式（リンク数が知名度の材料） | 社内作業。マイタウンガイドのWeb掲載ページからのリンクが使えるかは要確認【推測】 |
| 8 | 主要な掲載先（自社HP・Instagram・ココナラ等のプロフィール）で名前・住所・電話の表記をそろえる | 業界調査（弱〜中） | 各サービスのプロフィール編集画面 |
| 9 | 写真・投稿は「お客さまが見て選ぶため」に定期的に（順位目的ではない） | 公式は順位効果を書いていない／実験では効果なし | 「写真を追加」「最新情報を追加」 |
| 10 | 効果測定はパフォーマンス画面の「検索語句」「電話・ルート数」で毎月見る | 公式 | https://business.google.com/ →パフォーマンス（https://support.google.com/business/answer/9918094?hl=ja ） |

やらないこと：ビジネス名に地名・業種を足す／口コミの謝礼・代筆・業者購入／クリック水増し／バーチャルオフィス住所での登録（すべて規約違反・停止リスク）。

### 営業に使える言い方（顧客向け）【推測：根拠は上記】
- 「Googleはお金で順位を上げないと公式に書いています。効くのはカテゴリ・住所・営業時間・サービスなど基本情報の正確さと、お店の知名度です」→ ホームページ月額契約に含まれる「Googleマップの情報更新」の価値説明に使える。
- 「投稿を毎週すれば上がる」「写真を増やせば上がる」とは言わない（実験で否定的な結果）。言うなら「見た人に選ばれやすくする」まで。

## 出典一覧（主なもの）
- https://support.google.com/business/answer/7091?hl=ja
- https://support.google.com/business/answer/3038177?hl=ja
- https://support.google.com/contributionpolicy/answer/7400114?hl=ja
- https://support.google.com/business/answer/14114287
- https://support.google.com/business/answer/9918094?hl=ja
- https://blog.google/products/maps/google-business-profiles-ai-fake-reviews/
- https://whitespark.ca/local-search-ranking-factors/ （抜粋で確認）
- https://www.sterlingsky.ca/do-google-posts-impact-ranking/ （抜粋で確認）
- https://www.seroundtable.com/custom-google-business-profile-services-impact-rankings-36794.html
- https://www.brightlocal.com/research/vicinity-gbp-spam-impact/
- https://www.brightlocal.com/research/businesses-ranking-top-3-in-google-local-have-85-citations/
