# pdfLaTeX compatibility changes

The Japanese content-review manuscript now compiles with **pdfLaTeX**.

Changes made:

- Replaced `luatexja` and `luatexja-fontspec` with `CJKutf8` and `CJKspace`.
- Removed the Noto CJK system-font declarations and font-search dependency.
- Enabled CJK decoding for the full document, including acmart end-document hooks and deferred floats.
- Loaded the bundled CJK Mincho font definition and mapped acmart's bold/italic requests to available pdfLaTeX shapes.
- Kept PDF metadata ASCII-only to avoid pdfLaTeX Unicode metadata errors.
- Updated the Japanese compile instructions to `pdflatex -> bibtex -> pdflatex -> pdflatex`.
- The English manuscript text and setup were not changed.

Overleaf settings:

1. Select the desired main `.tex` file.
2. Set **Compiler = pdfLaTeX**.
3. Run **Recompile from scratch** once if references are not initially displayed.
