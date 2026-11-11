# Draws accuracy vs median latency per model from the saved runs in results/
# and saves the chart and a summary table to graphs/

import glob
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
GRAPHS = os.path.join(ROOT, "graphs")
FIGURES = os.path.join(ROOT, "figures")

# results folder -> name on the chart, and where its label sits next to the dot
# (MiMo and Qwen have almost the same accuracy and latency, so their labels go on opposite sides)
MODELS = {
    "jev": {"name": "Jev", "offset": (9, 0), "ha": "left"},
    "ollama-qwen": {"name": "Qwen3 8B", "offset": (9, 0), "ha": "left"},
    "ollama-glm": {"name": "GLM 4.6V Flash", "offset": (-9, 0), "ha": "right"},
    "ollama-mimo": {"name": "MiMo 9B", "offset": (-9, 0), "ha": "right"},
    "ollama-deepseek": {"name": "DeepSeek R1 8B", "offset": (-9, 0), "ha": "right"},
}

NOTE = (
    "Accuracy = correct picks / total inputs across all runs. "
    "Jev runs on TypeSafe's API; other models run locally via Ollama on a laptop"
)

DOT = "#2a78d6"
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e6e5e1"
AXIS = "#b5b4ae"

# the right/total and latency from one run file written by scripts/RunMain.sh
# (None if it has no score line; latency is None if it has no latency line)
def parse_run(path):
    with open(path) as f:
        text = f.read()
    score = re.search(r"right\s+=\s+(\d+)/(\d+)", text)
    if not score:
        return None
    latency = re.search(r"latency=(\d+)ms", text) # find the latency line from the results file and keeps the number as milliseconds
    return {
        "right": int(score.group(1)),
        "total": int(score.group(2)),
        "latency_ms": int(latency.group(1)) if latency else None,
    }

# one row per run for every model in MODELS
def load_runs():
    rows = []
    for folder in MODELS:
        for path in sorted(glob.glob(os.path.join(RESULTS, folder, "*.txt"))):
            name = os.path.basename(path)
            run = parse_run(path)
            if run is None:
                print(f"warning: no score line in {name}, skipped")
                continue
            rows.append({"model": folder, "file": name, "dataset10": name.startswith("10_"), **run})
    return pd.DataFrame(rows)

# micro accuracy: all right picks over all inputs, as a %
def accuracy(runs):
    return 100 * runs["right"].sum() / runs["total"].sum()

# one row per model: runs counted, accuracy over all runs / datasets 01-09 / dataset 10, median latency
def summarise(runs):
    rows = []
    for folder, model in MODELS.items():
        mine = runs[runs["model"] == folder]
        rows.append({
            "model": model["name"],
            "runs": len(mine),
            "accuracy_all": round(accuracy(mine), 1),
            "accuracy_01_09": round(accuracy(mine[~mine["dataset10"]]), 1),
            "accuracy_10": round(accuracy(mine[mine["dataset10"]]), 1),
            "median_latency_s": round(mine["latency_ms"].median() / 1000, 2),
        })
    return pd.DataFrame(rows)

# 1, 10, 100, 1,000 instead of 10^0, 10^1, ...
def plain_seconds(x, _):
    return f"{x:,.0f}" if x >= 1 else f"{x:g}"

def plot(summary, path):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")

    ax.scatter(summary["median_latency_s"], summary["accuracy_all"], s=90, color=DOT, edgecolor="white", linewidth=1.5, zorder=3)
    for model, (_, row) in zip(MODELS.values(), summary.iterrows()):
        ax.annotate(model["name"], xy=(row["median_latency_s"], row["accuracy_all"]), xytext=model["offset"],
                    textcoords="offset points", ha=model["ha"], va="center", fontsize=10, color=TEXT)

    # log x with some room on both sides so the labels fit
    ax.set_xscale("log")
    ax.set_xlim(summary["median_latency_s"].min() / 3, summary["median_latency_s"].max() * 3)
    ax.xaxis.set_major_formatter(FuncFormatter(plain_seconds))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda x, _: ""))
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))

    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9, which="both")

    ax.set_xlabel("Median latency per run (seconds, log scale)", color=MUTED, fontsize=10)
    ax.set_ylabel("Accuracy (%)", color=MUTED, fontsize=10)
    ax.set_title("Accuracy vs latency per model", color=TEXT, fontsize=13, loc="left", pad=12)

    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.17)
    fig.text(0.01, 0.015, NOTE, fontsize=8, color=MUTED)
    fig.savefig(path, dpi=200)
    plt.close(fig)

def main():
    os.makedirs(GRAPHS, exist_ok=True)
    os.makedirs(FIGURES, exist_ok=True)
    summary = summarise(load_runs())
    print(summary.to_string(index=False))
    summary.to_csv(os.path.join(GRAPHS, "accuracy_summary.csv"), index=False)
    plot(summary, os.path.join(FIGURES, "accuracy_vs_latency.png"))
    print("saved figures/accuracy_vs_latency.png and graphs/accuracy_summary.csv")

if __name__ == "__main__":
    main()
