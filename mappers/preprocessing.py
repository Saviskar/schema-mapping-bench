# Preprocessing.py - This turns the raw data into what the model sees

# longest a sample value can be before it gets cut 
# (ADJUST THRESHOLD) - 80 WAS SET BECAUSE COLUMNS MIGHT HAVE PRODUCT DESCRIPTION AND THAT CAN BE TOO LONG
# SO THE MODEL WILL BE SLOW AND CAN BE EXPENSIVE AS WELL (HAVE TO TEST IF THE REASONING IS ACTUALLY CORRECT)
MAX_SAMPLE_LEN = 80

# cuts long values so one big text cell can't fill up the prompt
# ("..." at the end tells the model it was cut)
def shorten(value):
    if len(value) > MAX_SAMPLE_LEN:
        return value[:MAX_SAMPLE_LEN] + "..."
    return value

# Picks up to n example values from a column: first the most common values that repeat
# (up to half of n), then a random pick from the rest so values from the whole file show up
# (The seed is fixed so the same file always gives the same samples)

# (LINE 38)
# Why "more than once": in an ID column every value appears once, so nothing is "common." Without this rule, the code would just take the first few IDs, which brings back the problem of only seeing the top of the file.
# Why "up to half": so common values can't take every slot. There is always room for random values from across the file.
def get_samples(series, n=10, seed=0):
    # drop the empty cells, turn every value into text and cut the long ones
    values = series.dropna()
    values = values.astype(str)
    values = values.map(shorten)

    # how many times each value appears, most common first
    counts = values.value_counts()

    # few unique values: show all of them, most common first
    if len(counts) <= n:
        return counts.index.tolist()

    # values that appear more than once, up to half of n (n // 2 is half of n rounded down)
    common = []
    for value, count in counts.items():
        if count > 1 and len(common) < n // 2:
            common.append(value)

    # common values first, then fill the slots that are left with a random pick from the rest
    # (the seed makes it pick the same values every run)
    rest = counts.drop(common)
    random_pick = rest.sample(n - len(common), random_state=seed)
    return common + random_pick.index.tolist()

# Takes a table of data and builds a short summary of each columns: its data type,
# some example values, how much of it is empty and how much of it is unique
# (This is the summary that the model gets to see)
def get_upstream_columns(df, n_samples=10, seed=0):
    upstream_columns = {}
    for col in df.columns:
        series = df[col]

        # % of cells that are empty
        empty_count = int(series.isna().sum())
        null_pct = round(empty_count / len(series) * 100, 1)

        # % of cells that hold a different value
        unique_pct = round(series.nunique() / len(series) * 100, 1)

        upstream_columns[col] = {
            "type": str(series.dtype),
            "samples": get_samples(series, n_samples, seed),
            "null_pct": null_pct,
            "unique_pct": unique_pct,
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
def build_ticket(df, target, n_samples=10, seed=0):
    return {
        "downstream_node": target,
        "upstream_columns": get_upstream_columns(df, n_samples, seed),
    }