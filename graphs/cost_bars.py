# Draws the estimated API cost per 1,000 connections for each model (grouped bars, typical file vs dataset 10)
# and saves the chart and the table behind it to figures/

import glob
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

from accuracy_heatmap import MODELS
from accuracy_vs_latency import AXIS, GRID, MUTED, TEXT, parse_run
from invalid_bars import CASE_COLOURS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")

# results folder -> (input, output) API price in USD per million tokens, left to right on the chart
# (ollama-mimo is left out, no API exists for it)
PRICES = {
    "jev": (0.042, 0.0),              # TypeSafe, output tokens are free
    "ollama-qwen": (0.05, 0.40),      # OpenRouter
    "ollama-glm": (0.02, 0.21),       # zenmux
    "ollama-deepseek": (0.06, 0.09),  # Novita AI
}

# group -> legend label, and its colour (same muted blue and orange as fig 4)
GROUPS = {
    "Typical file": "Typical file (datasets 01–09)",
    "Dataset 10": "Dataset 10 (255 columns)",
}
COLOURS = CASE_COLOURS[:2]

Y_MIN, Y_MAX = 0.1, 30
BAR_WIDTH = 0.36

NOTE = (
    "Median tokens per run × API price per million tokens.\n"
    "Prices: TypeSafe (Jev, output tokens free), OpenRouter (Qwen3 8B), zenmux (GLM 4.6V Flash), "
    "Novita AI (DeepSeek R1 8B), November 2026.\n"
    "MiMo 9B has no API. GLM's typical-file tokens were limited by a 4,096-token context."
)

# input and output tokens from the "latency=... input_tokens=... output_tokens=..." line (None if it has none)
def tokens(path):
    with open(path) as f:
        found = re.search(r"input_tokens=(\d+)\s+output_tokens=(\d+)", f.read())
    return (int(found.group(1)), int(found.group(2))) if found else None

# one row per scored run for every model in PRICES (runs with no score line crashed and are skipped)
def load_runs():
    rows = []
    for folder in PRICES:
        skipped = 0
        for path in sorted(glob.glob(os.path.join(RESULTS, folder, "*.txt"))):
            name = os.path.basename(path)
            if parse_run(path) is None:
                skipped += 1
                continue
            counts = tokens(path)
            if counts is None:
                print(f"warning: no token line in {folder}/{name}, skipped")
                continue
            rows.append({
                "model": MODELS[folder],
                "group": "Dataset 10" if name.startswith("10_") else "Typical file",
                "input_tokens": counts[0],
                "output_tokens": counts[1],
            })
        print(f"skipped (no score line): {MODELS[folder]} {skipped}")
    return pd.DataFrame(rows)

# one row per model and group: median input and output tokens, cost per connection and per 1,000 connections
def cost_table(runs):
    rows = []
    for folder, (in_price, out_price) in PRICES.items():
        for group in GROUPS:
            mine = runs[(runs["model"] == MODELS[folder]) & (runs["group"] == group)]
            median_in = int(mine["input_tokens"].median())
            median_out = int(mine["output_tokens"].median())
            cost = median_in * in_price / 1e6 + median_out * out_price / 1e6
            rows.append({
                "model": MODELS[folder],
                "group": group,
                "median_input_tokens": median_in,
                "median_output_tokens": median_out,
                "cost_per_connection": cost,
                "cost_per_1000": cost * 1000,
            })
    return pd.DataFrame(rows)

# $0.1, $1, $10 instead of 10^-1, 10^0, ...
def dollars(x, _):
    return f"${x:g}"

def plot(table, path):
    models = [MODELS[folder] for folder in PRICES]
    if table["cost_per_1000"].min() < Y_MIN or table["cost_per_1000"].max() > Y_MAX:
        print(f"warning: a bar is outside ${Y_MIN:g}–${Y_MAX:g}, the y-axis needs changing")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    # bars start at the bottom of the axis (a log axis has no 0)
    for k, (group, colour) in enumerate(zip(GROUPS, COLOURS)):
        values = table[table["group"] == group].set_index("model")["cost_per_1000"].reindex(models)
        x = [i + (k - 0.5) * BAR_WIDTH for i in range(len(models))]
        ax.bar(x, values - Y_MIN, BAR_WIDTH, bottom=Y_MIN, color=colour, edgecolor="white",
               linewidth=1.5, label=GROUPS[group], zorder=2)
        for xi, v in zip(x, values):
            ax.annotate(f"${v:.2f}", xy=(xi, v), xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, color=TEXT)

    ax.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=TEXT)

    ax.set_xlim(-0.5, len(models) - 0.5)
    ax.set_xticks(range(len(models)), models)
    ax.set_yscale("log")
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.yaxis.set_major_formatter(FuncFormatter(dollars))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda x, _: ""))

    ax.grid(True, axis="y", which="major", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9, which="both")
    ax.tick_params(axis="x", colors=TEXT, labelsize=10, length=0)

    ax.set_ylabel("Estimated cost per 1,000 connections (USD, log scale)", color=MUTED, fontsize=10)
    ax.set_title("Estimated cost per 1,000 connections", color=TEXT, fontsize=13, loc="left", pad=12)

    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.2)
    fig.text(0.01, 0.02, NOTE, fontsize=8, color=MUTED, va="bottom", linespacing=1.5)
    fig.savefig(path, dpi=300)
    plt.close(fig)

def main():
    os.makedirs(FIGURES, exist_ok=True)
    table = cost_table(load_runs())
    print(table.to_string(index=False))
    table.round({"cost_per_connection": 9, "cost_per_1000": 6}).to_csv(os.path.join(FIGURES, "fig6_cost.csv"), index=False)
    plot(table, os.path.join(FIGURES, "fig6_cost.png"))
    print("saved figures/fig6_cost.png and figures/fig6_cost.csv")

if __name__ == "__main__":
    main()
