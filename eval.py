import argparse
import glob
import json
import os

import dotenv
import pandas as pd

from mappers.models import MODELS
from mappers.preprocessing import build_ticket, get_options

# how many inputs it got right, the average probability it gave the right column,
# and for each input: the column it picked and the probability it gave the right one
# (probability is None for models that don't give one for every column)
def score(answers, expected):
    right = 0
    picks = {}
    for name, correct in expected.items():
        answer = answers[name]
        right += answer["choice"] == correct
        probabilities = answer.get("probabilities")
        p = probabilities.get(correct, 0.0) if probabilities else None
        picks[name] = (answer["choice"], p)
    ps = [p for _, p in picks.values()]
    p_right = None if None in ps else sum(ps) / len(ps)
    return right, p_right, picks

# "-" when the model gave no probability
def fmt_p(p):
    return "-" if p is None else f"{p:.2f}"

# one line per input: the right column, then what the model picked and the probability it gave the right column
# (x marks a wrong pick)
def print_detail(expected, picks):
    for name, correct in expected.items():
        choice, p = picks[name]
        mark = " " if choice == correct else "x"
        print(f"    {name:20} right={correct:14}  {mark} {choice:14} p={fmt_p(p)}")

def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Score the model's column picks against the expected answers.")
    parser.add_argument("expected_files", nargs="*", help="Expected files to run (default: every file in expected/)")
    parser.add_argument("--model", choices=sorted(MODELS), default="jev", help="Model to run")
    parser.add_argument("--seed", type=int, default=0, help="Seed for the random pick of samples")
    parser.add_argument("--detail", action="store_true", help="Also show each input's pick and probability")
    args = parser.parse_args()

    print(f"model = {args.model}  seed = {args.seed}")
    # totals across every file, so one run can be compared to another
    # (p only counts the files where the model gave probabilities)
    total_right = total_inputs = total_p_inputs = 0
    total_p = 0.0
    # each expected file is named <csv>.<target>.json, which says which CSV and target to use
    for path in args.expected_files or sorted(glob.glob("expected/*.json")):
        name, target_name = os.path.basename(path).split(".")[:2]  # e.g. store_orders_drift, store_revenue_summary
        csv_path = f"data/{name}.csv"
        if not os.path.exists(csv_path):
            print(f"{name:22}  skipped: {csv_path} not found")
            continue
        df = pd.read_csv(csv_path)
        target = json.load(open(f"targets/{target_name}.json"))
        expected = json.load(open(path))
        options = get_options(df)
        ticket = build_ticket(df, target, seed=args.seed)
        right, p, picks = score(MODELS[args.model](ticket, options), expected)
        print(f"{name:22}  {target_name:22}  {right}/{len(expected)}  p={fmt_p(p)}")
        if args.detail:
            print_detail(expected, picks)
        total_right += right
        total_inputs += len(expected)
        if p is not None:
            total_p += p * len(expected)
            total_p_inputs += len(expected)

    if total_inputs:
        p = total_p / total_p_inputs if total_p_inputs else None
        print(f"{'total':22}  {'':22}  {total_right}/{total_inputs}  p={fmt_p(p)}")

if __name__ == "__main__":
    main()
