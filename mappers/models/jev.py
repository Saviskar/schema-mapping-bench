# jev.py - This asks the TypeSafe Jev model which upstream column feeds each downstream input

import os

from typesafe_sdk import Choice, TypeSafeClient


# Builds one question for each downstream input and sends them all to the model in one call
# (Each answer has the column the model picked, how confident it is and the probability of every column)
def map_columns(ticket, options):
    # Start with an empty dictionary of questions
    questions = {}

    # Add one question for each downstream input
    inputs = ticket["downstream_node"]["inputs"]
    for name in inputs:
        key = name + "_column"
        questions[key] = Choice(
            instructions="Which upstream column provides `downstream_node.inputs." + name + "`",
            criteria=options,
        )

    with TypeSafeClient(model="jev-latest", api_key=os.environ["TYPESAFE_API_KEY"]) as client:
        response = client.system_one(
            state=ticket,
            questions=questions,
        )

    # turn the SDK answers into the shared shape, keyed by input name (without "_column")
    answers = {}
    for name in inputs:
        answer = response.answers[name + "_column"]
        answers[name] = {
            "choice": answer.choice,
            "confidence": answer.confidence,
            "probabilities": answer.probabilities,
        }
    return answers
