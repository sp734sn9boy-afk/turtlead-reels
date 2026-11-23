# 1分返信パック（Google Apps Script ひな形）

お客さまのGoogleスプレッドシートに入れて使う。Googleフォーム（＋任意でGmail）→ 受付記録 → 自動返信メール → LINE通知（＋任意でClaudeの返信下書き）。

- `Code.gs` … プログラム本体（Apps Scriptエディタに1ファイルで貼る）
- `appsscript.json` … 設定ファイル（タイムゾーン・V8・必要な許可）
- `test/` … Googleの部品を差し替えて node で動かす自動テスト

テストの実行：

```
node --test gas/reply-pack/test/reply-pack.test.js
```

お客さま専用の値はコードに書かない（すべて「設定」シート）。導入手順は docs/automation/1分返信パック_導入手順書_下書き.md。
