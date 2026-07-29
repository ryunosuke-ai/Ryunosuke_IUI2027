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
