# schema-mapping-bench

Uses the TypeSafe `jev-latest` model to match the columns in a CSV file (upstream) to the inputs a downstream node needs (the target).

## Setup

```bash
git clone https://github.com/Saviskar/schema-mapping-bench.git
cd schema-mapping-bench

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Then put your real key in `.env`. `.env` is gitignored, and `.env.example` is the committed template.

## Run

```bash
python main.py data/store_orders.csv --target targets/store_revenue_summary.json
```

This prints one answer per target input:

```json
{
  "store_name_column": {
    "type": "choice",
    "choice": "<csv column or \"none\">",
    "confidence": 0.0,
    "probabilities": { "<column>": 0.0, "none": 0.0 }
  }
}
```

`--expected` is accepted but not used yet. It's reserved for scoring the answers against known mappings.

## Layout

```
data/       input CSVs (the upstream data)
targets/    JSON descriptions of what a downstream node needs
mappers/
  preprocessing.py   turns a CSV + target into what the model sees
  model.py           asks the model to make the mapping
main.py     CLI that wires the parts together
requirements.txt   pinned dependencies
.env.example       template for .env
```

## `data/` and `targets/`

- **`data/`**: raw CSVs whose column names don't match the target names, e.g. `branch`, `unit_cost`, `qty_ordered`.
- **`targets/`**: each file describes one downstream node: its `name`, its `purpose`, and an `inputs` map of input name → description.

Keeping these in separate folders means any CSV can be tested against any target. To add a test case, put a CSV in `data/` and a target in `targets/`.

## `mappers/preprocessing.py`

| Function | What it does | Why |
|---|---|---|
| `get_upstream_columns(df, n_samples=10, seed=0)` | For each column, records its dtype, up to `n_samples` non-null sample values (repeated common values plus a seeded random pick, each cut to 80 characters), its null % and its unique % | Column names alone are ambiguous. Seeing actual values (`Downtown`, `19.99`), types and the null/unique ratios gives the model evidence. For example, 100% unique means an ID. |
| `get_options(df)` | Builds `{column: column}` for every column, plus `"none"` | These are the only answers the model can choose from, so it can't make up a column name. `"none"` covers target inputs that have no source, like `discount_pct` in the sample data. |
| `build_ticket(df, target)` | Returns `{"downstream_node": target, "upstream_columns": ...}` | This is the `state` sent to the model: what's needed next to what's available. |

## `mappers/model.py`

`schema_mapping_model_typesafe(ticket, options)`:

1. Creates one `Choice` question for each input in `ticket["downstream_node"]["inputs"]`, keyed `<input>_column`.
2. Each question's instructions point at `downstream_node.inputs.<name>`, a path into the ticket, so the key names in `build_ticket` must stay as they are.
3. All the questions use the same `options` as their `criteria`.
4. Sends everything in one `client.system_one(state=ticket, questions=...)` call and returns `response.answers`. Each answer contains `choice`, `confidence` and a `probabilities` value for every option.

## `main.py`

1. Loads `.env` to get `TYPESAFE_API_KEY`.
2. Parses `csv_file`, `--target`, `--expected` and `--samples` (sample values per column, default 10).
3. Loads the target JSON and reads the CSV with pandas.
4. Runs `build_ticket` → `get_options` → `schema_mapping_model_typesafe`.
5. Prints the answers as JSON.
