# Draws how often each model returned an unusable reply (every pick invalid), stacked by case,
# and saves the chart and the table behind it to figures/

import glob
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from accuracy_heatmap import COLUMNS, MODELS
from accuracy_vs_latency import AXIS, GRID, MUTED, TEXT, parse_run
from consistency_strip import header_case

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")

Y_MAX = 20
BAR_WIDTH = 0.55

# one colour per case that had an unusable run, given out in COLUMNS order
# (muted blue, orange, aqua, ochre, rose, violet; checked for colour-blind separation in this order)
CASE_COLOURS = ["#5b8fd0", "#e08a5e", "#4fae8c", "#d9a83e", "#d886a8", "#7c6fc0"]

JEV_NOTE = "can't be invalid (fixed answer list)"
NOTE = (
    "Unusable reply = every answer in the run came back invalid "
    "(broken JSON, wrong keys, or column names not in the list).\n"
    "No model ever had only some answers invalid. Crashed runs with no reply are excluded."
)

# invalid picks and total picks in a run file (mappers/models/llm.py writes "invalid" when the reply can't be used)
def pick_counts(path):
    with open(path) as f:
        picks = re.findall(r"picked=(\S+)", f.read())
    return sum(pick == "invalid" for pick in picks), len(picks)

# one row per scored run for every model in MODELS (runs with no score line crashed before any reply and are skipped)
def load_runs():
    rows = []
    for folder, model in MODELS.items():
        skipped = 0
        for path in sorted(glob.glob(os.path.join(RESULTS, folder, "*.txt"))):
            if parse_run(path) is None:
                skipped += 1
                continue
            case = header_case(path)
            if case is None:
                print(f"warning: unknown case in {folder}/{os.path.basename(path)}, skipped")
                continue
            invalid, total = pick_counts(path)
            rows.append({
                "model": model,
                "case": case,
                "invalid_picks": invalid,
                "total_picks": total,
                "unusable": total > 0 and invalid == total,
                "partial": 0 < invalid < total,
            })
        print(f"skipped (no reply): {model} {skipped}")
    return pd.DataFrame(rows)

# one row per model and case: scored runs, unusable runs, invalid picks and total picks
def invalid_table(runs):
    table = runs.groupby(["model", "case"]).agg(
        valid_runs=("unusable", "count"),
        unusable_runs=("unusable", "sum"),
        invalid_picks=("invalid_picks", "sum"),
        total_picks=("total_picks", "sum"),
    )
    order = pd.MultiIndex.from_product([MODELS.values(), COLUMNS], names=["model", "case"])
    table = table.reindex(order).dropna(subset=["valid_runs"])
    return table.astype(int).reset_index()

# unusable runs and invalid picks per model, as counts and %, plus runs with only some picks invalid
def summarise(runs):
    rows = []
    for model in MODELS.values():
        mine = runs[runs["model"] == model]
        unusable = int(mine["unusable"].sum())
        invalid = int(mine["invalid_picks"].sum())
        total = int(mine["total_picks"].sum())
        rows.append({
            "model": model,
            "unusable_runs": f"{unusable}/{len(mine)} ({100 * unusable / len(mine):.1f}%)",
            "invalid_picks": f"{invalid}/{total} ({100 * invalid / total:.1f}%)",
            "partial_runs": int(mine["partial"].sum()),
        })
    return pd.DataFrame(rows)

def plot(table, path):
    valid = table.groupby("model", sort=False)["valid_runs"].sum()
    unusable = table.groupby("model", sort=False)["unusable_runs"].sum()
    # % of the model's runs that were unusable, split by case (model x case)
    share = table.pivot(index="model", columns="case", values="unusable_runs").reindex(
        index=list(MODELS.values()), columns=COLUMNS).fillna(0)
    share = share.div(valid, axis=0) * 100
    cases = [case for case in COLUMNS if share[case].sum() > 0]
    if len(cases) > len(CASE_COLOURS):
        raise SystemExit(f"{len(cases)} cases have unusable runs but there are only {len(CASE_COLOURS)} colours")
    if share.sum(axis=1).max() > Y_MAX:
        print(f"warning: a bar goes past {Y_MAX}%, the y-axis needs raising")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    x = range(len(MODELS))
    bottom = pd.Series(0.0, index=share.index)
    # zorder 2 keeps the white segment edges under the x-axis line
    for case, colour in zip(cases, CASE_COLOURS):
        ax.bar(x, share[case], BAR_WIDTH, bottom=bottom, color=colour, edgecolor="white", linewidth=1.5, zorder=2)
        bottom += share[case]

    # "<unusable>/<valid>" above each bar, or just "0" sitting on the axis
    for i, model in enumerate(MODELS.values()):
        if unusable[model]:
            ax.text(i, bottom[model] + 0.3, f"{unusable[model]}/{valid[model]}",
                    ha="center", va="bottom", fontsize=10, color=TEXT)
        else:
            ax.text(i, 0.3, "0", ha="center", va="bottom", fontsize=10, color=TEXT)

    # legend reversed so it reads top to bottom like the stack
    handles = [Patch(facecolor=colour, edgecolor="white") for colour in CASE_COLOURS[:len(cases)]]
    legend = ax.legend(handles[::-1], cases[::-1], title="Case", loc="upper left",
                       alignment="left", frameon=False, fontsize=9, labelcolor=TEXT, title_fontsize=9)
    legend.get_title().set_color(MUTED)

    ax.set_xlim(-0.5, len(MODELS) - 0.5)
    ax.set_xticks(x, MODELS.values())
    ax.set_ylim(0, Y_MAX)
    ax.set_yticks(range(0, Y_MAX + 1, 5))

    jev = list(MODELS.values()).index("Jev")
    ax.annotate(JEV_NOTE, xy=(jev, 0), xycoords=ax.get_xaxis_transform(), xytext=(0, -20),
                textcoords="offset points", ha="center", va="top", fontsize=8, color=MUTED)

    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.tick_params(axis="x", colors=TEXT, labelsize=10, length=0)

    ax.set_ylabel("Runs with an unusable reply (%)", color=MUTED, fontsize=10)
    ax.set_title("Unusable replies per model", color=TEXT, fontsize=13, loc="left", pad=12)

    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.2)
    fig.text(0.01, 0.02, NOTE, fontsize=8, color=MUTED, va="bottom", linespacing=1.5)
    fig.savefig(path, dpi=300)
    plt.close(fig)

def main():
    os.makedirs(FIGURES, exist_ok=True)
    runs = load_runs()
    summary = summarise(runs)
    print(summary.to_string(index=False))
    if summary["partial_runs"].sum():
        print("warning: some runs had only some picks invalid, the footnote needs updating")
    table = invalid_table(runs)
    table.to_csv(os.path.join(FIGURES, "fig4_invalid.csv"), index=False)
    plot(table, os.path.join(FIGURES, "fig4_invalid.png"))
    print("saved figures/fig4_invalid.png and figures/fig4_invalid.csv")

if __name__ == "__main__":
    main()
