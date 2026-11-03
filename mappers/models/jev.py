# jev.py - This asks the TypeSafe Jev model which upstream column feeds each downstream input

import math
import os
import time

from typesafe_sdk import Choice, TypeSafeClient

# (ADJUST THRESHOLD) most columns the model is asked about in one call
# Jev takes at most 255 choices per question and 64k tokens per call, and every question repeats
# all the column names, so it adds up fast: 32 date columns with 34 inputs was already ~40k tokens
# (files with more columns than this are asked in two rounds, see map_columns)
MAX_COLUMNS_PER_CALL = 40


# a copy of the ticket that only has the given columns
# (so the model only sees samples for the columns it can pick)
def narrow_ticket(ticket, columns):
    return {
        "downstream_node": ticket["downstream_node"],
        "upstream_columns": {col: ticket["upstream_columns"][col] for col in columns},
    }


# the options for the given columns, plus "none"
def narrow_options(options, columns):
    small_options = {col: options[col] for col in columns}
    small_options["none"] = options["none"]
    return small_options


# Builds one question for each downstream input and sends them all to the model in one call
# (criteria has the options for each input, so different inputs can choose from different columns)
# (Each answer has the column the model picked, how confident it is and the probability of every column)
def ask(client, ticket, criteria):
    # Start with an empty dictionary of questions
    questions = {}

    # Add one question for each downstream input
    for name, options in criteria.items():
        key = name + "_column"
        questions[key] = Choice(
            instructions="Which upstream column provides `downstream_node.inputs." + name + "`",
            criteria=options,
        )

    # time only the API call (retries included), so it lines up with the LLM adapter
    start = time.perf_counter()
    response = client.system_one(
        state=ticket,
        questions=questions,
    )
    latency_ms = (time.perf_counter() - start) * 1000

    # tokens can be None if the API didn't report them
    stats = {
        "latency_ms": latency_ms,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return response, stats


# adds up the stats of several calls (a token count is None if any call didn't report it)
def add_stats(all_stats):
    total = {"latency_ms": sum(s["latency_ms"] for s in all_stats)}
    for key in ("input_tokens", "output_tokens"):
        counts = [s[key] for s in all_stats]
        if None in counts:
            total[key] = None
        else:
            total[key] = sum(counts)
    return total


# Asks the model which column feeds each input
# (With more than MAX_COLUMNS_PER_CALL columns it asks in two rounds: first each chunk of columns picks
# its best column for every input, then one last call where each input picks between its own finalists)
def map_columns(ticket, options):
    inputs = ticket["downstream_node"]["inputs"]
    columns = [col for col in options if col != "none"]

    with TypeSafeClient(model="jev-latest", api_key=os.environ["TYPESAFE_API_KEY"]) as client:
        if len(columns) <= MAX_COLUMNS_PER_CALL:
            criteria = {name: options for name in inputs}
            response, stats = ask(client, ticket, criteria)
        else:
            # split the columns into even chunks of at most MAX_COLUMNS_PER_CALL
            n_chunks = math.ceil(len(columns) / MAX_COLUMNS_PER_CALL)
            size = math.ceil(len(columns) / n_chunks)

            # round 1: the column each chunk picks for an input becomes one of that input's finalists
            # (chunks go through the file in order, so the finalists stay in file order)
            finalists = {name: [] for name in inputs}
            all_stats = []
            for i in range(0, len(columns), size):
                chunk = columns[i:i + size]
                chunk_options = narrow_options(options, chunk)
                criteria = {name: chunk_options for name in inputs}
                chunk_response, chunk_stats = ask(client, narrow_ticket(ticket, chunk), criteria)
                all_stats.append(chunk_stats)
                for name in inputs:
                    pick = chunk_response.answers[name + "_column"].choice
                    if pick != "none":
                        finalists[name].append(pick)

            # round 2: each input picks between its own finalists (or "none" if every chunk said none)
            # (the ticket keeps every finalist column, so the model can compare them side by side)
            keep = [col for col in columns if any(col in picks for picks in finalists.values())]
            criteria = {name: narrow_options(options, finalists[name]) for name in inputs}
            response, final_stats = ask(client, narrow_ticket(ticket, keep), criteria)
            all_stats.append(final_stats)
            stats = add_stats(all_stats)

    # turn the SDK answers into the shared shape, keyed by input name (without "_column")
    answers = {}
    for name in inputs:
        answer = response.answers[name + "_column"]
        answers[name] = {
            "choice": answer.choice,
            "confidence": answer.confidence,
            "probabilities": answer.probabilities,
        }
    return answers, stats
