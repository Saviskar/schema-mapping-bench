import argparse
import glob
import json
import os

import dotenv
import pandas as pd

from mappers.models import MODELS
from mappers.preprocessing import build_ticket, get_options

# an expected answer is one column, or a list when more than one column is right
# (e.g. the same date column appears twice in the CSV)
def right_columns(correct):
    if isinstance(correct, list):
        return correct
    return [correct]

# how many inputs it got right, the average probability it gave the right column,
# and for each input: the column it picked and the probability it gave the right one
# (probability is None for models that don't give one for every column)
def score(answers, expected):
    right = 0
    picks = {}
    ps = []
    for name, correct in expected.items():
        rights = right_columns(correct)
        answer = answers[name]
        if answer["choice"] in rights:
            right += 1

        # with several right columns, p is the probability it gave any of them
        probabilities = answer.get("probabilities")
        if probabilities:
            p = sum(probabilities.get(column, 0.0) for column in rights)
        else:
            p = None

        picks[name] = (answer["choice"], p)
        ps.append(p)

    # the average is None if any input has no probability
    if None in ps:
        p_right = None
    else:
        p_right = sum(ps) / len(ps)
    return right, p_right, picks

# "-" when the model gave no probability, otherwise the probability with 2 decimal places
def fmt_p(p):
    if p is None:
        return "-"
    return f"{p:.2f}"

# "-" when the API didn't report a token count
def fmt_tokens(n):
    if n is None:
        return "-"
    return str(n)

# one line per input: the right column, then what the model picked and the probability it gave the right column
# (x marks a wrong pick)
def print_detail(expected, picks):
    for name, correct in expected.items():
        rights = right_columns(correct)
        choice, p = picks[name]
        if choice in rights:
            mark = " "
        else:
            mark = "x"
        print(f"    {name.ljust(20)} right={'|'.join(rights).ljust(14)}  {mark} {choice.ljust(14)} p={fmt_p(p)}")

def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Score the model's column picks against the expected answers.")
    parser.add_argument("expected_files", nargs="*", help="Expected files to run (default: every file in expected/)")
    parser.add_argument("--model", choices=sorted(MODELS.keys()), default="jev", help="Model to run")
    parser.add_argument("--seed", type=int, default=0, help="Seed for the random pick of samples")
    parser.add_argument("--detail", action="store_true", help="Also show each input's pick and probability")
    args = parser.parse_args()

    print(f"model = {args.model}  seed = {args.seed}")
    # totals across every file, so one run can be compared to another
    # (p only counts the files where the model gave probabilities, tokens only the files where the API reported them)
    total_right = 0
    total_inputs = 0
    total_p_inputs = 0
    total_p = 0.0
    total_calls = 0
    total_latency_ms = 0.0
    total_input_tokens = None
    total_output_tokens = None

    # no files given: run every file in expected/
    expected_files = args.expected_files
    if len(expected_files) == 0:
        expected_files = sorted(glob.glob("expected/*.json"))

    for path in expected_files:
        # each expected file is named <csv>.<target>.json, which says which CSV and target to use
        # e.g. store_orders_drift.store_revenue_summary.json
        file_name = os.path.basename(path)
        parts = file_name.split(".")
        name = parts[0]
        target_name = parts[1]

        csv_path = f"data/{name}.csv"
        if not os.path.exists(csv_path):
            print(f"{name.ljust(22)}  skipped: {csv_path} not found")
            continue

        df = pd.read_csv(csv_path)
        with open(f"targets/{target_name}.json") as f:
            target = json.load(f)
        with open(path) as f:
            expected = json.load(f)

        options = get_options(df)
        ticket = build_ticket(df, target, seed=args.seed)
        answers, stats = MODELS[args.model](ticket, options)
        right, p, picks = score(answers, expected)

        print(
            f"{name.ljust(22)}  {target_name.ljust(22)}  {right}/{len(expected)}  p={fmt_p(p)}"
            f"  {stats['latency_ms']:.0f}ms  in={fmt_tokens(stats['input_tokens'])} out={fmt_tokens(stats['output_tokens'])}"
        )
        if args.detail:
            print_detail(expected, picks)

        total_right += right
        total_inputs += len(expected)
        if p is not None:
            total_p += p * len(expected)
            total_p_inputs += len(expected)

        total_calls += 1
        total_latency_ms += stats["latency_ms"]
        if stats["input_tokens"] is not None:
            total_input_tokens = (total_input_tokens or 0) + stats["input_tokens"]
        if stats["output_tokens"] is not None:
            total_output_tokens = (total_output_tokens or 0) + stats["output_tokens"]

    if total_inputs > 0:
        if total_p_inputs > 0:
            p = total_p / total_p_inputs
        else:
            p = None
        # latency is the average per file (one API call each), tokens are summed
        avg_latency_ms = total_latency_ms / total_calls
        print(
            f"{'total'.ljust(22)}  {' ' * 22}  {total_right}/{total_inputs}  p={fmt_p(p)}"
            f"  avg={avg_latency_ms:.0f}ms  in={fmt_tokens(total_input_tokens)} out={fmt_tokens(total_output_tokens)}"
        )

if __name__ == "__main__":
    main()
