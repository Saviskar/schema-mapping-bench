# Draws how much each model's accuracy moves between repeated runs of the same case
# (strip plot, one dot per case) and saves the chart and the table behind it to figures/

import glob
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from accuracy_heatmap import COLUMNS, DATASETS, MODELS, MONTHS
from accuracy_vs_latency import AXIS, DOT, GRID, MUTED, TEXT, parse_run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")

JITTER = 0.22      # dots spread this far either side of the model's column
EXPLAINS_GAP = 15  # an invalid run explains the gap if the other runs agree within this many points

NOTE = (
    "Each dot = one case. Gap = best run accuracy − worst run accuracy across that case's runs.\n"
    "Seed fixed at 0, so every run saw the same input. Every case has {runs} scored runs; "
    "an invalid run is a reply that couldn't be parsed (scored 0%)."
)
MISSING_NOTE = "\nNot shown, every run invalid: {missing}."

# "csv =" and "target =" header lines of a run file -> short case label (None if it isn't one of the 18 cases)
def header_case(path):
    with open(path) as f:
        text = f.read()
    csv = re.search(r"^csv\s+=\s+(\S+)", text, re.M)
    target = re.search(r"^target\s+=\s+(\S+)", text, re.M)
    if not csv or not target:
        return None
    prefix = os.path.basename(csv.group(1))[:2]
    if prefix in DATASETS:
        return DATASETS[prefix]
    month = re.search(r"store_sales_2024_(\d{2})\.json$", target.group(1))
    if prefix == "10" and month:
        label = f"10 {MONTHS[int(month.group(1)) - 1]}"
        return label if label in COLUMNS else None
    return None

# True if every pick in a run file is "invalid" (mappers/models/llm.py does that when the reply can't be parsed)
def invalid_run(path):
    with open(path) as f:
        picks = re.findall(r"picked=(\S+)", f.read())
    return bool(picks) and all(pick == "invalid" for pick in picks)

# one row per scored run for every model in MODELS (runs with no score line crashed and are skipped)
def load_runs():
    rows = []
    for folder, model in MODELS.items():
        skipped = 0
        for path in sorted(glob.glob(os.path.join(RESULTS, folder, "*.txt"))):
            run = parse_run(path)
            if run is None:
                skipped += 1
                continue
            case = header_case(path)
            if case is None:
                print(f"warning: unknown case in {folder}/{os.path.basename(path)}, skipped")
                continue
            rows.append({
                "model": model,
                "case": case,
                "accuracy": 100 * run["right"] / run["total"],
                "invalid": invalid_run(path),
            })
        print(f"skipped (no score line): {model} {skipped}")
    return pd.DataFrame(rows)

# one row per model and case: scored runs, how many were invalid, worst and best run accuracy,
# the gap between them, and the gap again without the invalid runs (empty if every run was invalid)
def consistency(runs):
    table = runs.groupby(["model", "case"]).agg(
        runs=("accuracy", "count"),
        invalid_runs=("invalid", "sum"),
        min_acc=("accuracy", "min"),
        max_acc=("accuracy", "max"),
    )
    table["range_pp"] = table["max_acc"] - table["min_acc"]
    valid = runs[~runs["invalid"]].groupby(["model", "case"])["accuracy"]
    table["range_without_invalid_pp"] = valid.max() - valid.min()
    order = pd.MultiIndex.from_product([MODELS.values(), COLUMNS], names=["model", "case"])
    table = table.reindex(order).dropna(subset=["runs"])
    return table.astype({"runs": int, "invalid_runs": int}).reset_index()

# rows where every run was invalid (no real gap to show)
def all_invalid(table):
    return table["invalid_runs"] == table["runs"]

# median and largest gap per model, and how many cases scored the same every run (all-invalid cases left out)
def summarise(table):
    table = table[~all_invalid(table)]
    rows = []
    for model in MODELS.values():
        mine = table[table["model"] == model]["range_pp"]
        rows.append({
            "model": model,
            "median_range_pp": round(mine.median(), 1),
            "max_range_pp": round(mine.max(), 1),
            "cases_range_0": int((mine == 0).sum()),
        })
    return pd.DataFrame(rows)

# x position for each dot: its model's column plus a fixed-seed offset
# (evenly spaced offsets in a shuffled order, so dots with the same value never share an x)
def jittered_x(table):
    rng = np.random.default_rng(0)
    x = pd.Series(0.0, index=table.index)
    for i, model in enumerate(MODELS.values()):
        mine = table.index[table["model"] == model]
        x[mine] = i + rng.permutation(np.linspace(-JITTER, JITTER, len(mine)))
    return x

# "GLM 4.6V Flash 06 PO lines, 07 Payroll; MiMo 9B 06 PO lines" for the footnote
def missing_cases(table):
    return "; ".join(f"{model} " + ", ".join(rows["case"]) for model, rows in table.groupby("model", sort=False))

def plot(table, path):
    missing = table[all_invalid(table)]
    table = table[~all_invalid(table)]
    table = table.assign(x=jittered_x(table))
    runs = table["runs"].unique()
    if len(runs) > 1:
        print(f"warning: scored runs per case vary ({sorted(runs)}), the footnote needs updating")

    # hollow when the invalid runs are what made the gap, i.e. the other runs agree
    hollow = (table["invalid_runs"] > 0) & (table["range_without_invalid_pp"] <= EXPLAINS_GAP)
    solid = table[~hollow]
    hollow = table[hollow]

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    ax.scatter(solid["x"], solid["range_pp"], s=45, color=DOT, alpha=0.65, edgecolor="white", linewidth=0.6, zorder=3)
    ax.scatter(hollow["x"], hollow["range_pp"], s=45, facecolor="white", edgecolor=DOT, linewidth=1.2, zorder=3)
    marker = Line2D([], [], marker="o", linestyle="none", markersize=7,
                    markerfacecolor="white", markeredgecolor=DOT, markeredgewidth=1.2)
    ax.legend([marker], ["hollow = gap caused by an invalid run"], loc="upper left",
              frameon=False, fontsize=9, labelcolor=TEXT)

    ax.set_xlim(-0.5, len(MODELS) - 0.5)
    ax.set_xticks(range(len(MODELS)), MODELS.values())
    # a little room past 0 and 100 so dots on the limits aren't cut off
    ax.set_ylim(-4, 104)
    ax.set_yticks(range(0, 101, 20))

    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.spines["left"].set_bounds(0, 100)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.tick_params(axis="x", colors=TEXT, labelsize=10, length=0)

    ax.set_ylabel("Gap between best and worst run (percentage points)", color=MUTED, fontsize=10)
    ax.set_title("Consistency across repeated runs", color=TEXT, fontsize=13, loc="left", pad=12)

    note = NOTE.format(runs=runs.max())
    if len(missing):
        note += MISSING_NOTE.format(missing=missing_cases(missing))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.17)
    fig.text(0.01, 0.02, note, fontsize=8, color=MUTED, va="bottom", linespacing=1.5)
    fig.savefig(path, dpi=300)
    plt.close(fig)

def main():
    os.makedirs(FIGURES, exist_ok=True)
    table = consistency(load_runs())
    print(summarise(table).to_string(index=False))
    table.round(1).to_csv(os.path.join(FIGURES, "fig3_consistency.csv"), index=False)
    plot(table, os.path.join(FIGURES, "fig3_consistency.png"))
    print("saved figures/fig3_consistency.png and figures/fig3_consistency.csv")

if __name__ == "__main__":
    main()
