# Draws how often Jev was right at each confidence level (bar chart, one bar per confidence bucket)
# and saves the chart and every pick behind it to figures/

import glob
import json
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from accuracy_vs_latency import AXIS, DOT, GRID, MUTED, TEXT, parse_run
from consistency_strip import header_case

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")

BAR_WIDTH = 0.6

# bucket label -> lowest confidence in it, left to right on the chart
BUCKETS = [("1.0", 0.995), ("0.9–0.99", 0.9), ("0.7–0.9", 0.7), ("0.5–0.7", 0.5), ("below 0.5", 0.0)]
CUTOFFS = [0.5, 0.7, 0.8, 0.9, 0.95]
CONFIDENT = 0.9  # wrong picks at or above this are listed one by one

# Jev's confidence is (p - 1/n) / (1 - 1/n), not p itself (p = probability of the picked column, n = options),
# so the two differ when there are few options, e.g. the last round of dataset 10
NOTE = (
    "Confidence = Jev's confidence score for its pick: 1 when all the probability is on that column, "
    "0 when it is spread evenly across the options.\n"
    "All Jev picks across all runs (n = {total:,})."
)

# the JSON block of answers in a run file ({input: {"choice", "confidence", "probabilities"}})
def answers(text):
    block, _ = json.JSONDecoder().raw_decode(text, text.index("\n{") + 1)
    return block

# one row per input of every scored Jev run (runs with no score line crashed and are skipped)
def load_picks():
    rows = []
    skipped = 0
    for path in sorted(glob.glob(os.path.join(RESULTS, "jev", "*.txt"))):
        if parse_run(path) is None:
            skipped += 1
            continue
        case = header_case(path)
        if case is None:
            print(f"warning: unknown case in jev/{os.path.basename(path)}, skipped")
            continue
        with open(path) as f:
            text = f.read()
        with open(os.path.join(ROOT, re.search(r"^expected\s+=\s+(\S+)", text, re.M).group(1))) as f:
            expected = json.load(f)
        picked = answers(text)
        for name, correct in expected.items():
            # a list when more than one column is right (same rule as eval.py)
            rights = correct if isinstance(correct, list) else [correct]
            answer = picked[name]
            rows.append({
                "case": case,
                "input": name,
                "expected": "|".join(rights),
                "choice": answer["choice"],
                "confidence": answer["confidence"],
                "right": answer["choice"] in rights,
            })
    print(f"skipped (no score line): {skipped}")
    return pd.DataFrame(rows)

# the label of the bucket a confidence falls in
def bucket(confidence):
    for label, lowest in BUCKETS:
        if confidence >= lowest:
            return label

# one row per bucket: picks, right, wrong and % right
def bucket_table(picks):
    labels = picks["confidence"].map(bucket)
    table = picks.groupby(labels)["right"].agg(n="count", right="sum")
    table = table.reindex([label for label, _ in BUCKETS], fill_value=0)
    table["wrong"] = table["n"] - table["right"]
    table["pct_right"] = 100 * table["right"] / table["n"]
    table.index.name = "bucket"
    return table.reset_index()

# one row per cutoff: share of picks filled in automatically (confidence >= cutoff), how many of those were right,
# share sent to the user instead, and how many of all wrong picks the user step would catch
def thresholds(picks):
    wrong = int((~picks["right"]).sum())
    rows = []
    for cutoff in CUTOFFS:
        auto = picks["confidence"] >= cutoff
        caught = int((~picks["right"] & ~auto).sum())
        rows.append({
            "cutoff": cutoff,
            "auto_filled": f"{100 * auto.mean():.1f}%",
            "auto_accuracy": f"{100 * picks.loc[auto, 'right'].mean():.1f}%",
            "sent_to_user": f"{100 * (~auto).mean():.1f}%",
            "wrong_caught": f"{caught}/{wrong}",
        })
    return pd.DataFrame(rows)

# wrong picks with confidence >= CONFIDENT, one row per (case, input, expected, choice) with how often it happened
def confident_wrong(picks):
    wrong = picks[~picks["right"] & (picks["confidence"] >= CONFIDENT)]
    table = wrong.groupby(["case", "input", "expected", "choice"]).size().rename("count").reset_index()
    return table.sort_values("count", ascending=False, kind="stable")

def plot(table, total, path):
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    x = range(len(table))
    ax.bar(x, table["pct_right"], BAR_WIDTH, color=DOT, zorder=2)

    # "% right" above each bar with "n = <picks>" between it and the bar
    for i, row in table.iterrows():
        ax.annotate(f"n = {row['n']:,}", xy=(i, row["pct_right"]), xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8, color=MUTED)
        ax.annotate(f"{row['pct_right']:.1f}%", xy=(i, row["pct_right"]), xytext=(0, 16), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, color=TEXT)

    ax.set_xlim(-0.5, len(table) - 0.5)
    ax.set_xticks(x, table["bucket"])
    # room above 100 for the labels on the tallest bar
    ax.set_ylim(0, 112)
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

    ax.set_xlabel("Jev's confidence in its pick", color=MUTED, fontsize=10)
    ax.set_ylabel("% of picks that were right", color=MUTED, fontsize=10)
    ax.set_title("How often Jev was right at each confidence level", color=TEXT, fontsize=13, loc="left", pad=12)

    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.2)
    fig.text(0.01, 0.02, NOTE.format(total=total), fontsize=8, color=MUTED, va="bottom", linespacing=1.5)
    fig.savefig(path, dpi=300)
    plt.close(fig)

def main():
    os.makedirs(FIGURES, exist_ok=True)
    picks = load_picks()
    print(f"picks: {len(picks)}  wrong: {int((~picks['right']).sum())}")
    table = bucket_table(picks)
    print(table.round(1).to_string(index=False))
    print()
    print(thresholds(picks).to_string(index=False))
    print()
    print(f"wrong picks with confidence >= {CONFIDENT}:")
    print(confident_wrong(picks).to_string(index=False))
    picks.to_csv(os.path.join(FIGURES, "fig5_jev_picks.csv"), index=False)
    plot(table, len(picks), os.path.join(FIGURES, "fig5_jev_confidence.png"))
    print("saved figures/fig5_jev_confidence.png and figures/fig5_jev_picks.csv")

if __name__ == "__main__":
    main()
