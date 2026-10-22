# llm.py - Asks any OpenAI-compatible model which upstream column feeds each downstream input

import json
import os

from openai import OpenAI

# OpenRouter hosts many open models (DeepSeek, Qwen, Kimi, GLM, MiMo) behind one key
OPENROUTER_URL = "https://openrouter.ai/api/v1"
# keep reasoning low (the answer is short), and only use OpenRouter hosts that follow the JSON schema
OPENROUTER_EXTRA = {"reasoning": {"effort": "low"}, "provider": {"require_parameters": True}}

# one entry per model: its model name, where to send it, which .env key to use,
# and any extra settings only that model needs
LLMS = {
    "gemini-flash": {
        "model": "gemini-3.8-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "extra": {"reasoning_effort": "low"},
    },
    "deepseek-flash": {
        "model": "deepseek/deepseek-v4.1-flash",
        "base_url": OPENROUTER_URL,
        "api_key_env": "OPENROUTER_API_KEY",
        "extra": OPENROUTER_EXTRA,
    },
    "qwen-27b": {
        "model": "qwen/qwen3.8-27b",
        "base_url": OPENROUTER_URL,
        "api_key_env": "OPENROUTER_API_KEY",
        "extra": OPENROUTER_EXTRA,
    },
    "kimi-k3": {
        "model": "moonshotai/kimi-k3",
        "base_url": OPENROUTER_URL,
        "api_key_env": "OPENROUTER_API_KEY",
        "extra": OPENROUTER_EXTRA,
    },
    "glm-flash": {
        "model": "z-ai/glm-5.3-flash",
        "base_url": OPENROUTER_URL,
        "api_key_env": "OPENROUTER_API_KEY",
        "extra": OPENROUTER_EXTRA,
    },
    "mimo-flash": {
        "model": "xiaomi/mimo-v2.6-flash",
        "base_url": OPENROUTER_URL,
        "api_key_env": "OPENROUTER_API_KEY",
        "extra": OPENROUTER_EXTRA,
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
