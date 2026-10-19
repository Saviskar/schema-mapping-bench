# Preprocessing.py - This turns the raw data into what the model sees

# Takes a table of data and builds a short summary of each columns: its data type,
# some example values, how much of it is empty and how much of it is unique
# (This is the summary that the model gets to see)
def get_upstream_columns(df):
    upstream_columns = {}
    for col in df.columns:
        series = df[col]
        upstream_columns[col] = {
            "type": str(series.dtype),
            "samples": series.dropna().astype(str).unique()[:10].tolist(), # up to 10 unique non-empty values
            "null_pct": round(float(series.isna().mean()) * 100, 1),
            "unique_pct": round(series.nunique() / len(series) * 100, 1),
        }
    return upstream_columns

# one option for every column in the dataframe, plus "none"
def get_options(df):
    options = {}
    for col in df.columns:
        options[col] = col
    options["none"] = "No upstream column holds this data"
    return options

# describes what the downstream node needs, along with the upstream columns
def build_ticket(df, target):
    return {
        "downstream_node": target,
        "upstream_columns": get_upstream_columns(df),
    }