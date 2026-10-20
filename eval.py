import argparse
import glob
import json
import os

import dotenv
import pandas as pd

from mappers.model import schema_mapping_model_typesafe
from mappers.preprocessing import build_ticket, get_options

# A = old samples (first 10 in the file), B = new samples (random pick uses the seed), everything else the same
def build_tickets(df, target, seed):
    new = build_ticket(df, target, seed=seed)
    old = build_ticket(df, target)
    for col in df.columns:
        old["upstream_columns"][col]["samples"] = df[col].dropna().astype(str).unique()[:10].tolist()
    return old, new

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

# one line per input: the right column, then what A and B picked and the probability each gave the right column
# (x marks a wrong pick)
def print_detail(expected, a_picks, b_picks):
    for name, correct in expected.items():
        a_choice, a_p = a_picks[name]
        b_choice, b_p = b_picks[name]
        a_mark = " " if a_choice == correct else "x"
        b_mark = " " if b_choice == correct else "x"
        print(
            f"    {name:20} right={correct:14}"
            f"  A {a_mark} {a_choice:14} p={a_p:.2f}"
            f"   B {b_mark} {b_choice:14} p={b_p:.2f}"
        )

def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Score old (A) and new (B) samples against the expected answers.")
    parser.add_argument("expected_files", nargs="*", help="Expected files to run (default: every file in expected/)")
    parser.add_argument("--seed", type=int, default=0, help="Seed for B's random pick of samples")
    parser.add_argument("--detail", action="store_true", help="Also show each input's pick and probability")
    args = parser.parse_args()

    print(f"B seed = {args.seed}")
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
        old, new = build_tickets(df, target, args.seed)
        a_right, a_p, a_picks = score(schema_mapping_model_typesafe(old, options), expected)
        b_right, b_p, b_picks = score(schema_mapping_model_typesafe(new, options), expected)
        print(f"{name:22}  {target_name:22}  A {a_right}/{len(expected)}  p={a_p:.2f}   B {b_right}/{len(expected)}  p={b_p:.2f}")
        if args.detail:
            print_detail(expected, a_picks, b_picks)

if __name__ == "__main__":
    main()