import os

from typesafe_sdk import Choice, TypeSafeClient


def schema_mapping_model_typesafe(ticket, options):
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

        return response.answers
