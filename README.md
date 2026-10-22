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
python3 main.py data/store_orders.csv --target targets/store_revenue_summary.json --model jev
```

This prints one answer per target input:

```json
{
  "store_name": {
    "choice": "<csv column or \"none\">",
    "confidence": 0.0,
    "probabilities": { "<column>": 0.0, "none": 0.0 }
  }
}
```

`probabilities` is only there for models that give one for every column (Jev does). `--model` defaults to `jev`. `--expected` prints each pick next to the expected column.

## Layout

```
data/       input CSVs (the upstream data)
targets/    JSON descriptions of what a downstream node needs
mappers/
  preprocessing.py   turns a CSV + target into what the model sees
  models/            one adapter per model, all with the same map_columns signature
    __init__.py      MODELS registry (name → adapter)
    jev.py           TypeSafe Jev adapter
    llm.py           shared adapter for OpenAI-compatible models (Gemini, DeepSeek, ...)
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

## `mappers/models/`

Every adapter is `map_columns(ticket, options)` and returns `{input: {"choice": column, "confidence": 0-1}}`, plus `"probabilities"` if the model gives them. `main.py` and `eval.py` pick one by name from `MODELS` with `--model`.

To add a model:
- **OpenAI-compatible** (Gemini, Grok, DeepSeek, Qwen, GLM, Kimi, MiniMax, OpenRouter): add an entry to `LLMS` in `llm.py`, and its key to `.env` and `.env.example`. It shows up in `MODELS` under the entry's name.
- **Anything else**: write `mappers/models/<name>.py` with a `map_columns` function, then add it to `MODELS` in `__init__.py`.

`jev.py`:

1. Creates one `Choice` question for each input in `ticket["downstream_node"]["inputs"]`, keyed `<input>_column`.
2. Each question's instructions point at `downstream_node.inputs.<name>`, a path into the ticket, so the key names in `build_ticket` must stay as they are.
3. All the questions use the same `options` as their `criteria`.
4. Sends everything in one `client.system_one(state=ticket, questions=...)` call, then returns each answer's `choice`, `confidence` and `probabilities` under the input name.

`llm.py`:

1. Each `LLMS` entry has `model`, `base_url`, `api_key_env` and optional `extra` (settings only that model needs, e.g. `reasoning_effort`).
2. Sends the ticket as JSON in one call, with a JSON schema whose `enum` limits each `choice` to the real columns or `"none"`.
3. A broken reply, a missing input or a column that isn't in `options` comes back as `"invalid"`, so it counts as wrong.
4. No `probabilities` (the model reports its own `confidence`), so `eval.py` shows `p=-`.

## `main.py`

1. Loads `.env` to get the API keys.
2. Parses `csv_file`, `--target`, `--expected`, `--model` (default `jev`) and `--samples` (sample values per column, default 10).
3. Loads the target JSON and reads the CSV with pandas.
4. Runs `build_ticket` → `get_options` → `MODELS[--model]`.
5. Prints the answers as JSON.
