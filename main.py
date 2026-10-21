# Main.py - This runs the whole mapping from the command line

import argparse
import json

import dotenv
import pandas as pd

from mappers.models import MODELS
from mappers.preprocessing import build_ticket, get_options


# Loads the API key, reads the CSV and the target, builds the ticket and options,
# asks the model to map the columns and prints the answers as JSON
# (with --expected it also prints each pick next to the expected column)
def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Map CSV columns using the model.")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("--target", required=True, help="Path to the target JSON file")
    parser.add_argument("--expected", help="Path to a JSON file of expected column mappings")
    parser.add_argument("--model", choices=sorted(MODELS), default="jev", help="Model to run")
    # to change the number of sample rows that the model takes so we can experiment with how much samples do we need for better accuracy
    parser.add_argument("--samples", type=int, default=10, help="Number of example values per column")

    args = parser.parse_args()

    with open(args.target) as f:
        target = json.load(f)

    df = pd.read_csv(args.csv_file)
    ticket = build_ticket(df, target, args.samples)
    options = get_options(df)
    answers = MODELS[args.model](ticket, options)
    print(json.dumps(answers, indent=2))

    if args.expected:
        with open(args.expected) as f:
            expected = json.load(f)

        # one line per input: the expected column and the column the model picked (x marks a wrong pick)
        print()
        for name, correct in expected.items():
            choice = answers[name]["choice"]
            mark = " " if choice == correct else "x"
            print(f"{mark} {name:17} expected={correct:14} picked={choice}")

if __name__ == "__main__":
    main()