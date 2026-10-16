# describes every column so the model can see what's inside
def get_upstream_columns(df):
    upstream_columns = {}
    for col in df.columns:
        series = df[col]
        upstream_columns[col] = {
            "type": str(series.dtype),
            "samples": series.dropna().astype(str).unique()[:10].tolist(),
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
    
