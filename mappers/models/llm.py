# llm.py - Asks any OpenAI-compatible model which upstream column feeds each downstream input

import json
import os

from openai import OpenAI

# one entry per model: its model name, where to send it, which .env key to use,
# and any extra settings only that model needs
LLMS = {
    "gemini-flash": {
        "model": "gemini-3.8-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "extra": {"reasoning_effort": "low"},
    },
}

INSTRUCTIONS = 'For each input in downstream_node.inputs, pick which upstream column provides it. Answer "none" if no upstream column holds that data. Also give your confidence in each pick, from 0 to 1.'

def map_columns(ticket, options, config):
    inputs = ticket["downstream_node"]["inputs"]

    # one answer per input: a column from options (or "none") and a confidence
    properties = {}
    for name in inputs:
        properties[name] = {
            "type": "object",
            "properties": {
                "choice": {"type": "string", "enum": list(options.keys())},
                "confidence": {"type": "number"},
            },
            "required": ["choice", "confidence"],
        }
    schema = {"type": "object", "properties": properties, "required": list(inputs.keys())}

    client = OpenAI(api_key=os.environ[config["api_key_env"]], base_url=config["base_url"])
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": json.dumps(ticket)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "column_mapping", "schema": schema},
        },
        # extra settings only this model needs (e.g. reasoning_effort), added to the request as they are
        extra_body=config.get("extra", {}),
    )

    # an empty or broken reply becomes {} so every input comes back "invalid" instead of crashing the run
    content = response.choices[0].message.content
    if content is None:
        content = ""
    try:
        reply = json.loads(content)
    except json.JSONDecodeError:
        reply = {}

    answers = {}
    for name in inputs:
        answer = reply.get(name, {})
        choice = answer.get("choice", "invalid")
        # some providers don't enforce the enum, so a made-up column counts as invalid too
        if choice not in options:
            choice = "invalid"
        answers[name] = {
            "choice": choice,
            "confidence": answer.get("confidence", 0.0),
        }
    return answers
