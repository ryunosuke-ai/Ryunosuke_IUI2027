# 図の挿入方法について

このフォルダに，パワースライドから翻訳・トリミングした図を，以下のファイル名で保存してください
（英語版・日本語版の両方の .tex から，この `figures/` フォルダを参照する想定です）。

| ファイル名（拡張子なしで可） | 元スライド | 内容 |
|---|---|---|
| `fig1_pipeline_overview` | スライド8 | BASiS パイプライン全体像 |
| `fig2_feature_extraction` | スライド9 | 小規模コーパスからのLLMによる特徴抽出（状態・戦略・遷移） |
| `fig3_bayesian_model` | スライド10 | ベイズ的対話モデル（状態遷移グラフ） |
| `fig4_scoring` | スライド11 | ベイズ更新によるスコアリング |
| `fig5_selection_dpo` | スライド12 | データ選別とLoRA/DPO学習 |

## 手順

1. PowerPoint内の該当スライドの図を，英語表記に翻訳し，必要な部分だけを画像としてトリミングしてください。
2. PDF/PNG/JPGいずれの形式でも構いません（推奨: PDFまたは高解像度PNG）。
3. ファイル名を上表の名前（例: `fig1_pipeline_overview.pdf`）にして，このフォルダに保存してください。
4. `.tex` ファイル内で，該当する図のプレースホルダー部分（`%% \includegraphics[width=\linewidth]{figures/fig1_pipeline_overview}` という行）の
   - コメントアウト（`%%`）を外す
   - 直後の `\fbox{...}` によるプレースホルダーの行（複数行）を削除する

   例（変更前）:
   ```latex
   \centering
   %% \includegraphics[width=\linewidth]{figures/fig1_pipeline_overview}
   \fbox{\parbox{0.9\linewidth}{\centering\vspace{2em}Figure placeholder: ...\vspace{2em}}}
   \caption{...}
   ```

   例（変更後）:
   ```latex
   \centering
   \includegraphics[width=\linewidth]{figures/fig1_pipeline_overview}
   \caption{...}
   ```

5. 画像の拡張子が `.pdf` の場合は `\includegraphics` の引数に拡張子を書かなくてもコンパイルできます
   （pdfLaTeX / LuaLaTeX いずれも同様）。`.png` / `.jpg` の場合も同様に拡張子なしで動作しますが，
   念のため拡張子まで書いても構いません。

6. 各図には ACM の要件により `\Description{...}` （代替テキスト）が既に用意されています。
   実際の図に差し替えたら，`\Description{}` の内容も実際の図の内容に合わせて更新してください
   （視覚障がいのある読者のための説明文であり，キャプションと同じ内容を繰り返さないようにしてください）。

## 図がまだない場合

図を挿入しなくても，現状のプレースホルダー（灰色の枠と説明文）のままコンパイルは通ります。
レビュー用に図なしで提出することも可能ですが，実際の投稿前には必ず差し替えてください。
