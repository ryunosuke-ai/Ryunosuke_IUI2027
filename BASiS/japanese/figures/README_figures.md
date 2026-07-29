# BASiS 図1・図2

図1と図2は，拡大しても劣化しないTikZベクター図として作成している．図中の文字は，後の英語論文でもそのまま利用できるように英語で統一した．

| 掲載図 | 編集用ソース | LaTeXから参照するPDF |
|---|---|---|
| 図1：BASiSの全体構成 | `fig1_basis_architecture.tex` | `fig1_basis_architecture.pdf` |
| 図2：ベイズ的スコアリング | `fig2_bayesian_scoring.tex` | `fig2_bayesian_scoring.pdf` |

## 再生成

このディレクトリで次を実行する．

```sh
pdflatex -interaction=nonstopmode -halt-on-error fig1_basis_architecture.tex
pdflatex -interaction=nonstopmode -halt-on-error fig2_bayesian_scoring.tex
```

色，文言，数値，矢印の位置などは各 `.tex` を編集して変更できる．本文側では，二段組でも可読性を保てるように `figure*` と `width=\textwidth` でPDFを挿入している．

## PowerPointで編集する場合

`BASiS_figures_editable.pptx`には，図1と図2を1枚ずつ，合計2枚のスライドとして収録している．PDFを画像として貼り付けたものではなく，ボックス，テキスト，棒グラフ，矢印をすべてPowerPointの独立した図形として作成しているため，位置，改行，色，線幅などを個別に変更できる．

使用フォントは，通常の文字がAptos，数式部分がCambria Mathである．編集後は，各スライドをPDFとして書き出し，論文中の対応するPDFと置き換える．

PowerPoint版をプログラムから再生成する場合は，`python-pptx`を導入した環境で次を実行する．

```sh
python3 generate_editable_pptx.py
```
