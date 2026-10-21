import argparse
import glob
import json
import os

import dotenv
import pandas as pd

from mappers.model import schema_mapping_model_typesafe
from mappers.preprocessing import build_ticket, get_options

# how many inputs it got right, the average probability it gave the right column,
# and for each input: the column it picked and the probability it gave the right one
def score(answers, expected):
    right = 0
    picks = {}
    for name, correct in expected.items():
        answer = answers[name + "_column"]
        right += answer.choice == correct
        picks[name] = (answer.choice, answer.probabilities.get(correct, 0.0))
    p_right = sum(p for _, p in picks.values()) / len(picks)
    return right, p_right, picks

# one line per input: the right column, then what the model picked and the probability it gave the right column
# (x marks a wrong pick)
def print_detail(expected, picks):
    for name, correct in expected.items():
        choice, p = picks[name]
        mark = " " if choice == correct else "x"
        print(f"    {name:20} right={correct:14}  {mark} {choice:14} p={p:.2f}")

def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Score the model's column picks against the expected answers.")
    parser.add_argument("expected_files", nargs="*", help="Expected files to run (default: every file in expected/)")
    parser.add_argument("--seed", type=int, default=0, help="Seed for the random pick of samples")
    parser.add_argument("--detail", action="store_true", help="Also show each input's pick and probability")
    args = parser.parse_args()

    print(f"seed = {args.seed}")
    # totals across every file, so one run can be compared to another
    total_right = total_inputs = 0
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
        right, p, picks = score(schema_mapping_model_typesafe(ticket, options), expected)
        print(f"{name:22}  {target_name:22}  {right}/{len(expected)}  p={p:.2f}")
        if args.detail:
            print_detail(expected, picks)
        total_right += right
        total_inputs += len(expected)
        total_p += p * len(expected)

    if total_inputs:
        print(f"{'total':22}  {'':22}  {total_right}/{total_inputs}  p={total_p / total_inputs:.2f}")

if __name__ == "__main__":
    main()
