"""Generate the publication Oracle-evaluation figures from the result file.

``all_dataset_score.txt`` is the single source of truth for the means,
bootstrap 95% confidence intervals, and Holm-corrected pairwise tests.  The
internal ``Gold-only DPO`` condition is displayed in the paper as
``Target-only``.  Both vector PDFs and high-resolution PNG previews are
produced.
"""

from pathlib import Path
import re

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parent
RESULT_FILE = OUTPUT_DIR.parents[1] / "all_dataset_score.txt"

SOURCE_CONDITIONS = ("Base", "Gold-only DPO", "BASiS-DPO", "Random-DPO")
CONDITIONS = ("Base", "Target-only", "BASiS", "Random")
COLORS = ("#4C78A8", "#72B7B2", "#E45756", "#8A8A8A")
HATCHES = ("///", "\\\\", "", "...")
BASIS_INDEX = 2

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
        "filename": "esconv_dailydialog_oracle_scores_publication",
        "axis_ids": (
            "text_style_transfer.style_strength",
            "conversation_style.esconv_tone_similarity",
            "conversation_style.supporter_role_consistency",
            "conversation_style.non_directive_support_style",
            "strategy_transition.strategy_stage_alignment",
            "strategy_transition.premature_advice_avoidance",
            "text_style_transfer.naturalness",
        ),
        "labels": (
            "Style strength",
            "Tone similarity",
            "Role consistency",
            "Non-directive",
            "Stage alignment",
            "Advice timing",
            "Naturalness",
        ),
    },
    {
        "section": "mathdial",
        "filename": "mathdial_wildchat_oracle_scores_publication",
        "axis_ids": (
            "pedagogical_v2.equitable_tutoring",
            "pedagogical_v2.learner_reasoning_diagnosis",
            "pedagogical_v2.mistake_location_and_targeting",
            "pedagogical_v2.guidance_quality",
            "pedagogical_v2.feedback_actionability",
            "pedagogical_v2.answer_revealing_calibration",
            "pedagogical_v2.teacher_move_stage_alignment",
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
        "filename": "meditod_wildchat_oracle_scores_publication",
        "axis_ids": (
            "general.response_relevance",
            "general.overall_quality",
            "history.premature_assessment_avoidance",
            "safety.appropriate_uncertainty",
            "general.understandable",
            "safety.unsafe_medical_advice",
            "safety.unsupported_diagnosis",
        ),
        "labels": (
            "Response relevance",
            "Overall quality",
            "Assessment timing",
            "Uncertainty",
            "Understandability",
            "Unsafe advice",
            "Unsupported diagnosis",
        ),
    },
)


AXIS_PATTERN = re.compile(r"^AXIS: (.+) \(n=(\d+)\)$")
MODEL_PATTERN = re.compile(
    r"^\s{2}(Base|Gold-only DPO|BASiS-DPO|Random-DPO): "
    r"mean=([0-9.]+), std=[0-9.]+, "
    r"bootstrap_ci95=\[([0-9.]+), ([0-9.]+)\]"
)
PAIR_PATTERN = re.compile(
    r"^\s{4}([^:]+): mean_diff=[^,]+, p_holm=[^,]+, stars=(ns|\*+)$"
)


def parse_results(path):
    """Parse the three experiments while preserving their source order."""
    sections = {spec["section"]: [] for spec in EXPERIMENT_SPECS}
    current_section = None
    current_axis = None

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped in sections:
            current_section = stripped
            current_axis = None
            continue

        axis_match = AXIS_PATTERN.match(line)
        if axis_match and current_section is not None:
            current_axis = {
                "id": axis_match.group(1),
                "n": int(axis_match.group(2)),
                "models": {},
                "pairs": {},
            }
            sections[current_section].append(current_axis)
            continue

        if current_axis is None:
            continue

        model_match = MODEL_PATTERN.match(line)
        if model_match:
            model, mean, ci_low, ci_high = model_match.groups()
            mean = float(mean)
            current_axis["models"][model] = {
                "mean": mean,
                "ci_lower": mean - float(ci_low),
                "ci_upper": float(ci_high) - mean,
            }
            continue

        pair_match = PAIR_PATTERN.match(line)
        if pair_match:
            pair, stars = pair_match.groups()
            current_axis["pairs"][pair] = None if stars == "ns" else stars

    return sections


def build_experiment(spec, sections):
    """Validate and convert one parsed experiment to plotting arrays."""
    axes = sections[spec["section"]]
    axis_ids = tuple(axis["id"] for axis in axes)
    if axis_ids != spec["axis_ids"]:
        raise ValueError(
            f"Unexpected axis order for {spec['section']}: {axis_ids}"
        )
    if any(axis["n"] != 100 for axis in axes):
        raise ValueError(f"Expected n=100 for every {spec['section']} axis")
    for axis in axes:
        if tuple(axis["models"]) != SOURCE_CONDITIONS:
            raise ValueError(
                f"Unexpected model order for {axis['id']}: "
                f"{tuple(axis['models'])}"
            )

    means = []
    ci_lower = []
    ci_upper = []
    for source_condition in SOURCE_CONDITIONS:
        means.append(
            tuple(axis["models"][source_condition]["mean"] for axis in axes)
        )
        ci_lower.append(
            tuple(
                axis["models"][source_condition]["ci_lower"] for axis in axes
            )
        )
        ci_upper.append(
            tuple(
                axis["models"][source_condition]["ci_upper"] for axis in axes
            )
        )

    significance = tuple(
        (
            axis["pairs"]["BASiS_vs_Base"],
            axis["pairs"]["BASiS_vs_Gold-only"],
            axis["pairs"]["BASiS_vs_Random-DPO"],
        )
        for axis in axes
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
    height = 0.07
    ax.plot(
        (x1, x1, x2, x2),
        (y, y + height, y + height, y),
        color="#222222",
        linewidth=0.85,
        clip_on=False,
    )
    ax.text(
        (x1 + x2) / 2,
        y + height + 0.012,
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

    n_metrics = len(labels)
    x = np.arange(n_metrics, dtype=float)
    width = 0.18
    offsets = tuple((index - 1.5) * width for index in range(4))

    fig, ax = plt.subplots(figsize=spec["figsize"])
    ax.set_axisbelow(True)

    for condition_index, (condition, color, hatch, offset) in enumerate(
        zip(CONDITIONS, COLORS, HATCHES, offsets)
    ):
        values = means[condition_index]
        errors = np.vstack(
            (ci_lower[condition_index], ci_upper[condition_index])
        )
        ax.bar(
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
                "elinewidth": 0.85,
                "capsize": 2.4,
                "capthick": 0.85,
            },
            zorder=3,
        )

    comparison_indices = (1, 3, 0)  # Short brackets first; widest last.
    for metric_index, significance in enumerate(spec["significance"]):
        stars_by_index = {
            0: significance[0],
            1: significance[1],
            3: significance[2],
        }
        active_comparisons = [
            index
            for index in comparison_indices
            if stars_by_index[index] is not None
        ]
        upper_extent = means[:, metric_index] + ci_upper[:, metric_index]
        # Alternate the bracket baseline for adjacent metrics so that the
        # larger significance labels remain visually distinct at one-column
        # publication size.
        first_y = float(
            np.max(upper_extent) + 0.34 + 0.22 * (metric_index % 2)
        )
        for level, comparison_index in enumerate(active_comparisons):
            add_bracket(
                ax,
                x[metric_index] + offsets[comparison_index],
                x[metric_index] + offsets[BASIS_INDEX],
                first_y + 0.78 * level,
                stars_by_index[comparison_index],
            )

    ax.set_ylabel("Oracle score (1–10)")
    ax.set_xticks(x, labels, rotation=35, ha="right", rotation_mode="anchor")
    ax.set_xlim(-1.2, len(labels) - 0.35)
    ax.set_ylim(0, 12.8)
    ax.set_yticks(np.arange(0, 11, 2))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.65)
    ax.axhline(10, color="#8A8A8A", linewidth=0.7, linestyle=(0, (2, 2)))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", width=0.7, length=3)

    ax.legend(
        loc="upper left",
        ncol=4,
        frameon=False,
        columnspacing=1.15,
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
