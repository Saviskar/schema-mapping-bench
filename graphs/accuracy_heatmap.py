# Draws a per-case accuracy heatmap (models x cases) from the saved runs in results/
# and saves the chart and the table behind it to graphs/

import glob
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from accuracy_vs_latency import parse_run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
GRAPHS = os.path.join(ROOT, "graphs")
FIGURES = os.path.join(ROOT, "figures")

# results folder -> row label, top to bottom
MODELS = {
    "jev": "Jev",
    "ollama-glm": "GLM 4.6V Flash",
    "ollama-qwen": "Qwen3 8B",
    "ollama-mimo": "MiMo 9B",
    "ollama-deepseek": "DeepSeek R1 8B",
}

# csv number prefix -> column label (dataset 10 gets one column per month instead)
DATASETS = {
    "01": "01 Suppliers",
    "02": "02 Shipments",
    "03": "03 Stock",
    "04": "04 Regional sales",
    "05": "05 Products",
    "06": "06 PO lines",
    "07": "07 Payroll",
    "08": "08 Cold chain",
    "09": "09 POS",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
COLUMNS = list(DATASETS.values()) + [f"10 {m}" for m in MONTHS[:9]]

GROUP_LABEL = "Dataset 10 (wide file, one case per month)"
NOTE = "Each cell = correct picks / total inputs across all runs of that case"

TEXT = "#0b0b0b"
MUTED = "#52514e"
MISSING = "#e6e5e1"

# <csv>.<target>.<timestamp>.txt -> short column label (None if it isn't one of the 18 cases)
def case_label(name):
    case = re.match(r"^(.*)\.\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.txt$", name)
    if not case:
        return None
    case = case.group(1)
    prefix = case[:2]
    if prefix in DATASETS:
        return DATASETS[prefix]
    month = re.search(r"store_sales_2024_(\d{2})$", case)
    if prefix == "10" and month:
        label = f"10 {MONTHS[int(month.group(1)) - 1]}"
        return label if label in COLUMNS else None
    return None

# one row per run for every model in MODELS
def load_runs():
    rows = []
    for folder, model in MODELS.items():
        for path in sorted(glob.glob(os.path.join(RESULTS, folder, "*.txt"))):
            name = os.path.basename(path)
            case = case_label(name)
            if case is None:
                print(f"warning: unknown case in {folder}/{name}, skipped")
                continue
            run = parse_run(path)
            if run is None:
                print(f"warning: no score line in {folder}/{name}, skipped")
                continue
            rows.append({"model": model, "case": case, "right": run["right"], "total": run["total"]})
    return pd.DataFrame(rows)

# micro accuracy per model and case: all right picks over all inputs across its runs, as a %
def accuracy_table(runs):
    sums = runs.groupby(["model", "case"])[["right", "total"]].sum()
    acc = (100 * sums["right"] / sums["total"]).unstack("case")
    acc = acc.reindex(index=list(MODELS.values()), columns=COLUMNS)
    acc.index.name = "model"
    acc.columns.name = None
    return acc

# white or dark text, whichever has more contrast on the cell (WCAG relative luminance)
def text_colour(rgba):
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgba[:3]]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "white" if (1.05 / (lum + 0.05)) > ((lum + 0.05) / 0.05) else TEXT

def plot(table, path):
    values = np.ma.masked_invalid(table.to_numpy(dtype=float))
    cmap = plt.get_cmap("RdYlGn").with_extremes(bad=MISSING)
    n_rows, n_cols = values.shape

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("white")
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect="auto")

    # white gaps between cells
    ax.set_xticks(np.arange(n_cols + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n_rows + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i in range(n_rows):
        for j in range(n_cols):
            v = values[i, j]
            if np.ma.is_masked(v):
                ax.text(j, i, "–", ha="center", va="center", fontsize=9, color=MUTED)
            else:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9, color=text_colour(im.cmap(im.norm(v))))

    ax.set_xticks(range(n_cols), table.columns, rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticks(range(n_rows), table.index)
    ax.tick_params(colors=TEXT, labelsize=9)

    # split datasets 01-09 from the dataset 10 months, and label the dataset 10 group
    split = COLUMNS.index("10 Jan") - 0.5
    ax.axvline(split, color=TEXT, linewidth=3)
    ax.text((split + n_cols - 0.5) / 2, -0.6, GROUP_LABEL, ha="center", va="bottom", fontsize=9, color=MUTED)

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015, ticks=range(0, 101, 20))
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(colors=MUTED, labelsize=9, length=0)
    cbar.set_label("Accuracy (%)", color=MUTED, fontsize=10)

    ax.set_title("Accuracy per case and model", color=TEXT, fontsize=13, loc="left", pad=24)

    fig.subplots_adjust(left=0.09, right=0.955, top=0.86, bottom=0.27)
    fig.text(0.01, 0.02, NOTE, fontsize=8, color=MUTED)
    fig.savefig(path, dpi=200)
    plt.close(fig)

def main():
    os.makedirs(GRAPHS, exist_ok=True)
    os.makedirs(FIGURES, exist_ok=True)
    table = accuracy_table(load_runs())
    with pd.option_context("display.width", 250, "display.max_columns", None):
        print(table.round(1).to_string())
    table.round(1).to_csv(os.path.join(GRAPHS, "accuracy_per_case.csv"))
    plot(table, os.path.join(FIGURES, "accuracy_heatmap.png"))
    print("saved figures/accuracy_heatmap.png and graphs/accuracy_per_case.csv")

if __name__ == "__main__":
    main()
