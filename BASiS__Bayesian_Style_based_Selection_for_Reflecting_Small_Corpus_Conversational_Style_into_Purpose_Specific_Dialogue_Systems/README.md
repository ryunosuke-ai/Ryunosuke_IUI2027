# BASiS — IUI 2027 投稿用ドラフト一式

このzipには，IUI 2027（ACM International Conference on Intelligent User Interfaces）への
投稿を想定した論文ドラフトが，**英語版**と**内容確認用の日本語版**の2セット入っています。
ACM公式テンプレート（`ACM_Conference_Proceedings_Primary_Article_Template.zip` 内の `acmart.cls` 等）を
そのまま使用しており，IUI 2027 の公式CFPで指定されている
`\documentclass[manuscript,review,anonymous]{acmart}`（単一カラム・ダブルブラインド）
形式で作成しています。

```
paper/
├── english/                 … 投稿用の英語版（正本）
│   ├── basis_iui2027.tex    … 本文（pdfLaTeXでコンパイル）
│   ├── basis.bib            … 参考文献
│   ├── acmart.cls
│   ├── ACM-Reference-Format.bst
│   └── figures/              … 図を挿入するフォルダ（README_figures.md参照）
│
├── japanese/                 … 内容確認用の日本語版（pdfLaTeXでコンパイル）
│   ├── basis_iui2027_ja.tex … 本文（pdfLaTeX + CJKutf8）
│   ├── basis_ja.bib          … 参考文献（英語版と同一）
│   ├── acmart.cls
│   ├── ACM-Reference-Format.bst
│   └── figures/               … 図を挿入するフォルダ（README_figures.md参照）
│
└── README.md（このファイル）
```

---

## 1. コンパイラ設定

英語版・日本語版ともに **pdfLaTeX** でコンパイルできます。日本語版では，従来のLuaLaTeX用
`luatexja-fontspec` と外部日本語フォント指定を使わず，TeX Liveに標準収録されている
`CJKutf8` を利用しています。このため，Overleaf上でのシステムフォント探索が不要になり，
無料プランでも比較的短時間でコンパイルできます。

---

## 2. Overleafでの使い方

### 英語版（`english/` フォルダ）

1. Overleaf で「New Project」→「Upload Project」を選び，このzipをアップロードしてください。
2. 「Menu」→「Main document」で `paper/english/basis_iui2027.tex` を選択してください。
3. 「Menu」→「Compiler」で **pdfLaTeX** を選択してください。
4. 参考文献が表示されない場合は，「Logs and output files」→「Recompile from scratch」を実行してください。

### 日本語版（`japanese/` フォルダ）

1. 「Menu」→「Main document」で `paper/japanese/basis_iui2027_ja.tex` を選択してください。
2. 「Menu」→「Compiler」で **pdfLaTeX** を選択してください。
3. 「Recompile」を実行してください。初回に参考文献が表示されない場合は，
   「Recompile from scratch」を一度実行してください。
4. 日本語フォントの追加アップロードやフォント名の設定は不要です。

`basis_iui2027_ja.tex` では，`CJKutf8` を読み込み，ACMクラスの文書末処理や
遅延配置された図表まで日本語デコードが有効になるよう，本文開始時にCJK処理を有効化しています。
さらに，pdfLaTeXに同梱された日本語フォントの太字・斜体代替を設定しています。
通常の本文編集では，この設定部分を変更する必要はありません。


## 3. 図の挿入について

パワーポイントの提案手法スライド（スライド8〜12）にある5つの図は，論文内で参照できるよう
プレースホルダー（灰色の枠）を用意してあります。実際の図は，ご自身で英語に翻訳・トリミングした画像を
`english/figures/` と `japanese/figures/`（同じ画像で構いません）に配置し，
各フォルダ内の `README_figures.md` の手順に従って `.tex` 側のプレースホルダーを画像参照に差し替えてください。

図を挿入しなくても，現状のプレースホルダーのままレビュー・コンパイルは可能です。

---

## 4. 参考文献について

`basis.bib`（英語版）と `basis_ja.bib`（日本語版）は同一内容です。パワースライドの参考文献[1]〜[8]，
評価軸に付随する[9]〜[12]をすべて含み，さらに関連研究セクションのために追加で調査した
MathDial・MediTOD・WildChat-1M・DPO（Rafailov et al.）・LoRA（Hu et al.）・AlpaGasus（Chen et al.）・
POMDPベースの対話管理（Young et al.; Thomson & Young）の文献を合わせて，20件の参考文献を収録しています
（関連研究セクションだけで10件以上を参照する，というご要望に対応しています）。

---

## 5. 未完了・要確認の項目（投稿前に必ず対応してください）

- **著者名・所属**：ダブルブラインドのため `Anonymous Author(s)` のままにしてあります。
  最終カメラレディ版でのみ実名に戻してください（レビュー中は匿名のままにしてください）。
- **GenAI Usage Disclosure**：IUI 2027 の投稿規定で参考文献の直前に必須のセクションとして用意していますが，
  本文中に *[Author note: ...]* という注記付きのテンプレート文にしてあります。ご自身の実際のGenAI利用実態
  （本研究のBASiS手法自体でのLLM利用は既に本文中で説明済みです。ここでは主に執筆支援等の利用実態）に
  合わせて，投稿前に必ず内容を確認・編集し，注記部分は削除してください。
- **統計量（Kendall's W，標準化効果量）**：表3（5軸ルーブリック）内で「確定中 / pending」としている
  セルは，パワースライド内に具体的な数値が記載されていなかったため空欄にしてあります。
  最終的な統計分析が完了次第，数値を埋めてください。
- **追加コーパスペア（MathDial+MediTOD，WildChat-1M）の実験結果**：進行中の実験として，結果表の
  枠組みのみを用意しています（表4）。実験が完了次第，値を埋めてください。
- **人手評価**：計画中として記述していますが，実施後は結果セクションと考察を更新してください。
- **ACM Submission ID**：投稿システムから発行されたら，`.tex` 冒頭の
  `%% \acmSubmissionID{...}` のコメントアウトを外してIDを入力してください。
- **語数**：現在の英語版本文（Abstract〜結論，倫理声明・GenAI開示・参考文献を除く）はおよそ7,300〜7,800語です。
  IUI 2027 は8,000語を推奨上限としているため範囲内ですが，追加実験の結果を書き加えると増えるため，
  適宜削って調整してください。
