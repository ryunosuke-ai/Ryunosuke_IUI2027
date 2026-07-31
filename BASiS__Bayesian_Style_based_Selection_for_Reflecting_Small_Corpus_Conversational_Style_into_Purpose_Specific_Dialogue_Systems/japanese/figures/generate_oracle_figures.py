"""Generate publication-ready Oracle evaluation figures.

The means, asymmetric bootstrap 95% confidence intervals, and
Holm-corrected significance levels are transcribed from the source result
plots. Both vector PDF files (used by LaTeX) and high-resolution PNG
previews are produced.
"""

from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parent

CONDITIONS = ("Base", "BASiS", "Random")
COLORS = ("#4C78A8", "#E45756", "#7A7A7A")
HATCHES = ("///", "", "...")

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 8,
        "legend.fontsize": 8.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "hatch.linewidth": 0.65,
    }
)


EXPERIMENTS = (
    {
        "filename": "esconv_dailydialog_oracle_scores_publication",
        "labels": (
            "Style Strength",
            "ESConv Tone\nSimilarity",
            "Supporter Role\nConsistency",
            "Non-directive\nSupport Style",
            "Strategy/Stage\nAlignment",
            "Premature Advice\nAvoidance",
            "Naturalness",
        ),
        "means": (
            (8.26, 8.21, 8.34, 7.84, 7.84, 8.57, 8.35),
            (8.65, 8.52, 8.60, 8.34, 8.32, 9.44, 8.53),
            (8.21, 8.13, 8.41, 7.99, 7.98, 8.92, 8.17),
        ),
        "ci_lower": (
            (0.16, 0.11, 0.10, 0.24, 0.23, 0.35, 0.12),
            (0.10, 0.10, 0.10, 0.20, 0.18, 0.20, 0.13),
            (0.18, 0.14, 0.12, 0.23, 0.23, 0.29, 0.15),
        ),
        "ci_upper": (
            (0.14, 0.11, 0.10, 0.23, 0.22, 0.33, 0.12),
            (0.09, 0.10, 0.09, 0.19, 0.16, 0.18, 0.12),
            (0.16, 0.14, 0.12, 0.22, 0.21, 0.28, 0.14),
        ),
        "significance": (
            ("***", "***"),
            ("***", "***"),
            ("**", "*"),
            ("**", "*"),
            ("**", None),
            ("***", "*"),
            (None, "**"),
        ),
        "figsize": (7.15, 3.25),
    },
    {
        "filename": "mathdial_wildchat_oracle_scores_publication",
        "labels": (
            "Equitable\nTutoring",
            "Reasoning\nDiagnosis",
            "Mistake\nTargeting",
            "Guidance\nQuality",
            "Feedback\nActionability",
            "Answer\nCalibration",
            "Move/Stage\nAlignment",
        ),
        "means": (
            (6.77, 7.38, 7.53, 6.88, 7.01, 7.88, 7.44),
            (7.75, 8.70, 8.85, 8.02, 8.03, 8.86, 8.62),
            (6.00, 6.97, 7.27, 6.57, 6.18, 7.50, 7.06),
        ),
        "ci_lower": (
            (0.451, 0.606, 0.605, 0.530, 0.489, 0.484, 0.526),
            (0.336, 0.400, 0.389, 0.324, 0.364, 0.299, 0.331),
            (0.505, 0.678, 0.657, 0.581, 0.583, 0.556, 0.598),
        ),
        "ci_upper": (
            (0.444, 0.587, 0.647, 0.495, 0.466, 0.461, 0.508),
            (0.331, 0.416, 0.387, 0.322, 0.342, 0.307, 0.326),
            (0.490, 0.664, 0.626, 0.562, 0.550, 0.538, 0.605),
        ),
        "significance": tuple(("***", "***") for _ in range(7)),
        "figsize": (7.15, 3.25),
    },
    {
        "filename": "meditod_wildchat_oracle_scores_publication",
        "labels": (
            "Response\nRelevance",
            "Overall\nQuality",
            "Premature\nAssessment\nAvoidance",
            "Appropriate\nUncertainty",
            "Understandability",
            "Unsafe Medical\nAdvice\nAvoidance",
            "Unsupported\nDiagnosis\nAvoidance",
        ),
        "means": (
            (4.46, 5.16, 8.43, 7.84, 8.56, 9.52, 9.62),
            (5.09, 5.69, 8.90, 8.26, 8.77, 9.71, 9.82),
            (4.91, 5.46, 8.63, 7.92, 8.55, 9.36, 9.61),
        ),
        "ci_lower": (
            (0.48, 0.38, 0.48, 0.28, 0.15, 0.26, 0.22),
            (0.52, 0.40, 0.38, 0.24, 0.12, 0.18, 0.12),
            (0.48, 0.36, 0.42, 0.32, 0.17, 0.31, 0.25),
        ),
        "ci_upper": (
            (0.53, 0.40, 0.43, 0.27, 0.14, 0.20, 0.18),
            (0.52, 0.39, 0.35, 0.21, 0.12, 0.15, 0.09),
            (0.47, 0.39, 0.41, 0.29, 0.15, 0.25, 0.18),
        ),
        # Each tuple is (BASiS vs Base, BASiS vs Random).
        "significance": (
            ("**", None),
            ("**", None),
            (None, None),
            ("**", "**"),
            ("*", "*"),
            ("***", "*"),
            ("*", "*"),
        ),
        "figsize": (7.15, 3.25),
    },
)


def add_bracket(ax, x1, x2, y, stars):
    """Draw one compact significance bracket."""
    if stars is None:
        return
    height = 0.075
    ax.plot(
        (x1, x1, x2, x2),
        (y, y + height, y + height, y),
        color="#222222",
        linewidth=0.9,
        clip_on=False,
    )
    ax.text(
        (x1 + x2) / 2,
        y + height + 0.015,
        stars,
        ha="center",
        va="bottom",
        fontsize=8.5,
        fontweight="bold",
        color="#111111",
    )


def make_figure(spec):
    labels = spec["labels"]
    means = np.asarray(spec["means"], dtype=float)
    ci_lower = np.asarray(spec["ci_lower"], dtype=float)
    ci_upper = np.asarray(spec["ci_upper"], dtype=float)

    n_metrics = len(labels)
    x = np.arange(n_metrics, dtype=float)
    width = 0.22
    offsets = (-width, 0.0, width)
    # Nudge numeric labels slightly away from the center of each group. This
    # preserves separation when three values near 10 are shown in one column.
    value_label_offsets = (-0.025, 0.0, 0.025)

    fig, ax = plt.subplots(figsize=spec["figsize"])
    ax.set_axisbelow(True)

    for condition_index, (condition, color, hatch, offset) in enumerate(
        zip(CONDITIONS, COLORS, HATCHES, offsets)
    ):
        values = means[condition_index]
        errors = np.vstack(
            (ci_lower[condition_index], ci_upper[condition_index])
        )
        bars = ax.bar(
            x + offset,
            values,
            width=width,
            color=color,
            edgecolor="#303030",
            linewidth=0.7,
            hatch=hatch,
            label=condition,
            yerr=errors,
            error_kw={
                "ecolor": "#222222",
                "elinewidth": 0.9,
                "capsize": 2.7,
                "capthick": 0.9,
            },
            zorder=3,
        )

        for metric_index, bar in enumerate(bars):
            value = values[metric_index]
            upper = ci_upper[condition_index, metric_index]
            ax.text(
                bar.get_x()
                + bar.get_width() / 2
                + value_label_offsets[condition_index],
                value + upper + 0.075,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=6.8,
                color="#222222",
                zorder=5,
                bbox={
                    "facecolor": "white",
                    "edgecolor": "none",
                    "pad": 0.1,
                },
            )

    for metric_index, (base_sig, random_sig) in enumerate(
        spec["significance"]
    ):
        upper_extent = means[:, metric_index] + ci_upper[:, metric_index]
        # Keep the brackets clear of both the error bars and their numeric labels.
        label_clearance = 0.42
        first_y = float(np.max(upper_extent) + label_clearance)
        if base_sig is not None:
            add_bracket(
                ax,
                x[metric_index] + offsets[0],
                x[metric_index] + offsets[1],
                first_y,
                base_sig,
            )
        if random_sig is not None:
            second_y = first_y + (0.38 if base_sig is not None else 0.0)
            add_bracket(
                ax,
                x[metric_index] + offsets[1],
                x[metric_index] + offsets[2],
                second_y,
                random_sig,
            )

    ax.set_ylabel("Oracle score (1–10)")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 11.25)
    ax.set_yticks(np.arange(0, 11, 2))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.65)
    ax.axhline(10, color="#8A8A8A", linewidth=0.7, linestyle=(0, (2, 2)))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="x", length=0, pad=5)
    ax.tick_params(axis="y", width=0.7, length=3)

    ax.legend(
        loc="upper left",
        ncol=3,
        frameon=False,
        columnspacing=1.25,
        handlelength=1.8,
        bbox_to_anchor=(0.0, 1.005),
        borderaxespad=0,
    )

    fig.subplots_adjust(left=0.075, right=0.995, top=0.91, bottom=0.22)

    output_base = OUTPUT_DIR / spec["filename"]
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(
        output_base.with_suffix(".png"),
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def main():
    for experiment in EXPERIMENTS:
        make_figure(experiment)


if __name__ == "__main__":
    main()
