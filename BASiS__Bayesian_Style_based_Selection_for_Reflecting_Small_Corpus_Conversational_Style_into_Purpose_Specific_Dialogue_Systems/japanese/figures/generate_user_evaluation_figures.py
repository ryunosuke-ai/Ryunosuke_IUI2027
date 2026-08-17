"""Generate publication figures for the human evaluation.

``user_evaluation_all_dataset.txt`` is the single source of truth for the
participant-level means, bootstrap 95% confidence intervals, and
Holm-corrected paired comparisons.  The internal ``Random-DPO`` condition is
displayed in the paper as ``Random``.  Both vector PDFs and high-resolution
PNG previews are produced.
"""

from pathlib import Path
import re

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parent
RESULT_FILE = OUTPUT_DIR.parents[1] / "user_evaluation_all_dataset.txt"

SOURCE_CONDITIONS = ("Base", "BASiS", "Random-DPO")
CONDITIONS = ("Base", "BASiS", "Random")
COLORS = ("#4C78A8", "#E45756", "#8A8A8A")
HATCHES = ("///", "", "...")
BASIS_INDEX = 1

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 7.2,
        "axes.labelsize": 7.5,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 6.8,
        "legend.fontsize": 7.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "hatch.linewidth": 0.65,
    }
)


EXPERIMENT_SPECS = (
    {
        "section": "esconv",
        "filename": "esconv_user_evaluation_scores_publication",
        "axis_ids": (
            "Style Strength",
            "ESConv Tone Similarity",
            "Supporter Role Consistency",
            "Non-directive Support Style",
            "Premature Advice Avoidance",
            "Content Preservation",
            "Naturalness",
        ),
        "labels": (
            "Support behavior",
            "Tone similarity",
            "Role consistency",
            "Non-directive",
            "Advice timing",
            "Content fit",
            "Naturalness",
        ),
    },
    {
        "section": "mathdial",
        "filename": "mathdial_user_evaluation_scores_publication",
        "axis_ids": (
            "Equitable Tutoring",
            "Learner Reasoning Diagnosis",
            "Mistake Location and Targeting",
            "Guidance Quality",
            "Feedback Actionability",
            "Answer Revealing Calibration",
            "Teacher Move–Stage Alignment",
        ),
        "labels": (
            "Equitable tutoring",
            "Reasoning diagnosis",
            "Mistake targeting",
            "Guidance quality",
            "Actionability",
            "Answer calibration",
            "Move-stage alignment",
        ),
    },
    {
        "section": "meditod",
        "filename": "meditod_user_evaluation_scores_publication",
        "axis_ids": (
            "Coverage Without Redundancy",
            "Premature Assessment Avoidance",
            "Appropriate Uncertainty",
            "Unsafe Medical Advice Avoidance",
            "Unsupported Diagnosis Avoidance",
        ),
        "labels": (
            "No redundancy",
            "Assessment timing",
            "Uncertainty",
            "Unsafe advice",
            "Unsupported diagnosis",
        ),
    },
)


MODEL_PATTERN = re.compile(
    r"^(.+?) \| (Base|BASiS|Random-DPO) \| "
    r"([0-9.]+) \| ([0-9.]+) \| ([0-9.]+) \| "
    r"([0-9.]+) \| ([0-9.]+)$"
)
SIGNIFICANCE_PATTERN = re.compile(
    r"^SIGNIFICANCE \| (.+?) \| "
    r"(BASiS_vs_Base|BASiS_vs_Random-DPO|Base_vs_Random-DPO) \| "
    r"(?:p_holm=[^|]+|not_tested) \| (ns|\*+)$"
)


def parse_results(path):
    """Parse domain, axis, condition, CI, and significance records."""
    sections = {spec["section"]: {} for spec in EXPERIMENT_SPECS}
    current_section = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATASET: "):
            candidate = line.split(": ", 1)[1]
            current_section = candidate if candidate in sections else None
            continue
        if current_section is None:
            continue

        model_match = MODEL_PATTERN.match(line)
        if model_match:
            axis, model, mean, ci_low, ci_high, _, _ = model_match.groups()
            axis_record = sections[current_section].setdefault(
                axis, {"models": {}, "pairs": {}}
            )
            mean = float(mean)
            axis_record["models"][model] = {
                "mean": mean,
                "ci_lower": mean - float(ci_low),
                "ci_upper": float(ci_high) - mean,
            }
            continue

        significance_match = SIGNIFICANCE_PATTERN.match(line)
        if significance_match:
            axis, pair, stars = significance_match.groups()
            axis_record = sections[current_section].setdefault(
                axis, {"models": {}, "pairs": {}}
            )
            axis_record["pairs"][pair] = None if stars == "ns" else stars

    return sections


def build_experiment(spec, sections):
    """Validate one domain and convert it to plotting arrays."""
    axes = sections[spec["section"]]
    missing = tuple(axis for axis in spec["axis_ids"] if axis not in axes)
    if missing:
        raise ValueError(f"Missing {spec['section']} axes: {missing}")

    means = []
    ci_lower = []
    ci_upper = []
    for condition in SOURCE_CONDITIONS:
        condition_means = []
        condition_lower = []
        condition_upper = []
        for axis in spec["axis_ids"]:
            models = axes[axis]["models"]
            if tuple(models) != SOURCE_CONDITIONS:
                raise ValueError(
                    f"Unexpected model order for {axis}: {tuple(models)}"
                )
            record = models[condition]
            condition_means.append(record["mean"])
            condition_lower.append(record["ci_lower"])
            condition_upper.append(record["ci_upper"])
        means.append(tuple(condition_means))
        ci_lower.append(tuple(condition_lower))
        ci_upper.append(tuple(condition_upper))

    significance = tuple(
        (
            axes[axis]["pairs"]["BASiS_vs_Base"],
            axes[axis]["pairs"]["BASiS_vs_Random-DPO"],
        )
        for axis in spec["axis_ids"]
    )
    return {
        **spec,
        "means": means,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "significance": significance,
        # Generate at the final half-page width used by the side-by-side
        # layout. This avoids LaTeX scaling the labels down after rendering.
        "figsize": (3.45, 2.60),
    }


def add_bracket(ax, x1, x2, y, stars):
    """Draw one compact significance bracket."""
    height = 0.05
    ax.plot(
        (x1, x1, x2, x2),
        (y, y + height, y + height, y),
        color="#222222",
        linewidth=0.85,
        clip_on=False,
    )
    ax.text(
        (x1 + x2) / 2,
        y + height + 0.01,
        stars,
        ha="center",
        va="bottom",
        fontsize=7.0,
        fontweight="bold",
        color="#111111",
    )


def make_figure(spec):
    labels = spec["labels"]
    means = np.asarray(spec["means"], dtype=float)
    ci_lower = np.asarray(spec["ci_lower"], dtype=float)
    ci_upper = np.asarray(spec["ci_upper"], dtype=float)

    x = np.arange(len(labels), dtype=float)
    width = 0.22
    offsets = (-width, 0.0, width)

    fig, ax = plt.subplots(figsize=spec["figsize"])
    ax.set_axisbelow(True)

    for index, (condition, color, hatch, offset) in enumerate(
        zip(CONDITIONS, COLORS, HATCHES, offsets)
    ):
        errors = np.vstack((ci_lower[index], ci_upper[index]))
        ax.bar(
            x + offset,
            means[index],
            width=width,
            color=color,
            edgecolor="#303030",
            linewidth=0.7,
            hatch=hatch,
            label=condition,
            yerr=errors,
            error_kw={
                "ecolor": "#222222",
                "elinewidth": 0.85,
                "capsize": 2.4,
                "capthick": 0.85,
            },
            zorder=3,
        )

    for metric_index, (base_stars, random_stars) in enumerate(
        spec["significance"]
    ):
        comparisons = ((2, random_stars), (0, base_stars))
        active = tuple(item for item in comparisons if item[1] is not None)
        first_y = float(
            np.max(means[:, metric_index] + ci_upper[:, metric_index]) + 0.20
        )
        for level, (comparison_index, stars) in enumerate(active):
            add_bracket(
                ax,
                x[metric_index] + offsets[comparison_index],
                x[metric_index] + offsets[BASIS_INDEX],
                first_y + 0.23 * level,
                stars,
            )

    ax.set_ylabel("Human rating (1–7)")
    ax.set_xticks(x, labels, rotation=35, ha="right", rotation_mode="anchor")
    ax.set_xlim(-1.2, len(labels) - 0.35)
    ax.set_ylim(1, 8.15)
    ax.set_yticks(np.arange(1, 8, 1))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.65)
    ax.axhline(7, color="#8A8A8A", linewidth=0.7, linestyle=(0, (2, 2)))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", width=0.7, length=3)
    ax.legend(
        loc="upper left",
        ncol=3,
        frameon=False,
        columnspacing=1.25,
        handlelength=1.65,
        bbox_to_anchor=(0.0, 1.10),
        borderaxespad=0,
    )

    fig.subplots_adjust(left=0.105, right=0.995, top=0.83, bottom=0.34)
    output_base = OUTPUT_DIR / spec["filename"]
    # Keep the canvas at the final half-page width.  A tight bounding box
    # expands around the rotated edge labels and makes LaTeX scale all text
    # down again.
    fig.savefig(output_base.with_suffix(".pdf"))
    fig.savefig(
        output_base.with_suffix(".png"),
        dpi=300,
        facecolor="white",
    )
    plt.close(fig)


def main():
    sections = parse_results(RESULT_FILE)
    for experiment_spec in EXPERIMENT_SPECS:
        make_figure(build_experiment(experiment_spec, sections))


if __name__ == "__main__":
    main()
