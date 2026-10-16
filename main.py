import argparse
import json

import dotenv
import pandas as pd

from mappers.model import schema_mapping_model_typesafe
from mappers.preprocessing import build_ticket, get_options


def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Map CSV columns using the model.")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("--target", required=True, help="Path to the target JSON file")
    parser.add_argument("--expected", help="Path to a JSON file of expected column mappings")

    args = parser.parse_args()

    with open(args.target) as f:
        target = json.load(f)

    df = pd.read_csv(args.csv_file)
    ticket = build_ticket(df, target)
    options = get_options(df)
    answers = schema_mapping_model_typesafe(ticket, options)
    print(json.dumps({k: v.model_dump() for k, v in answers.items()}, indent=2))

if __name__ == "__main__":
    main()

# STEP 01: WRITE DOWN THE EXPECTED VALUE AND THE VALUE GOT FROM THE MODEL
# STEP 01: DISPLAY THE ACCURACY AND CONFIDENCE (PROBABILITES IF NEEDED)