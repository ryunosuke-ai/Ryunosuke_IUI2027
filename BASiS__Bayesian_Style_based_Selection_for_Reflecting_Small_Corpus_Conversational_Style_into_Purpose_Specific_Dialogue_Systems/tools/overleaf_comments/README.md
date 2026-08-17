# Overleaf Comment Exporter

OverleafのReview/Commentsを手で1件ずつ転記せず、Codexが読めるJSON/Markdownへ抽出するためのツールです。

## 重要

Overleafはコメント用の公開Export APIを公式には提供していません。
そのためこのツールは、ログイン済みブラウザ上で以下を非破壊で行います。

1. Review/Comment関連のネットワークJSONを捕捉
2. 必要に応じてReviewパネルDOMからコメント候補を抽出
3. JSON / Markdownとして保存
4. 抽出できなかった場合に、HTML・スクリーンショット・ネットワークログを保存

コメントをResolveしたり、編集・削除したりする処理はありません。

## セットアップ（Mac）

プロジェクトのルートで:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/overleaf_comments/requirements.txt
python -m playwright install chromium
```

## 実行

```bash
python tools/overleaf_comments/export_comments.py \
  "https://www.overleaf.com/project/あなたのPROJECT_ID"
```

初回はChromiumが開きます。

- Overleafへのログインが必要なら自分でログインしてください。
- Review / Commentsパネルが閉じている場合は開いてください。
- コメントが見える状態になったら、VSCodeのターミナルへ戻って **Enter** を押してください。
- **待機時間の制限はありません。**
- パスワードをスクリプトへ入力する必要はありません。
- ログインセッションは `.overleaf_playwright_profile/` に保存されます。

自動待機時間を指定したい場合だけ、たとえば `--wait 180` を付けます。
通常は付けない方が使いやすいです。

## 出力

デフォルトでは:

```text
docs/overleaf_review/
├── overleaf_review_comments.json
├── overleaf_review_comments.md
├── captured_network_payloads.json
├── captured_relevant_urls.txt
├── overleaf_page_snapshot.html
└── overleaf_page_snapshot.png
```

Codexには基本的に:

```text
docs/overleaf_review/overleaf_review_comments.json
english/basis_iui2027.tex
```

を読ませればOKです。

## Codexへの指示例

```text
docs/overleaf_review/overleaf_review_comments.json に、
指導教員からOverleafで受けたレビューコメントを自動抽出してあります。

english/basis_iui2027.tex とコメントを両方確認し、
未解決のレビューコメントの意図を一つずつ理解して修正してください。

コメント文をそのまま本文へコピーせず、
論文全体の主張、前後関係、用語統一、関連研究との整合性を踏まえて
IUI論文として最も自然な形へ修正してください。

特に、既に受けている研究方針と矛盾する修正は行わないでください。

最後に、
- どのコメントに対応したか
- どこをどのように修正したか
- 対応しなかったコメントとその理由
を報告してください。
```

## 抽出できない場合

Overleafの内部UI/APIは変更される可能性があります。

もし `Extracted candidates: 0` または明らかに件数がおかしい場合でも、
コメントを手作業で転記する必要はありません。

次のいずれかをこのChatGPTチャットへアップロードしてください。

- `docs/overleaf_review/overleaf_page_snapshot.html`
- `docs/overleaf_review/captured_network_payloads.json`
- 必要なら `overleaf_page_snapshot.png`

それを基に、現在のOverleaf UIに合わせて抽出ロジックを修正できます。

## Git管理上の注意

`.overleaf_playwright_profile/` にはログインセッションが含まれるため、
Gitへcommitしないでください。

`.gitignore` に以下を追加してください。

```gitignore
.overleaf_playwright_profile/
docs/overleaf_review/overleaf_page_snapshot.html
docs/overleaf_review/overleaf_page_snapshot.png
docs/overleaf_review/captured_network_payloads.json
```

`overleaf_review_comments.json` / `.md` をGit管理するかは任意です。
