# llm.py - Asks any OpenAI-compatible model which upstream column feeds each downstream input

import json
import os
import time

from openai import OpenAI

# Ollama runs models on this machine; its key is ignored but the client needs one
OLLAMA_URL = "http://localhost:11434/v1"

# a local model on a laptop can take much longer than the client's default 10 minute timeout on a big file,
# and a retry would just start the same slow request again (and add its time to the latency), so wait up to an hour, once
OLLAMA_CLIENT = {"timeout": 3600, "max_retries": 0}

# one entry per model: its model name, where to send it, which .env key to use,
# and any extra settings only that model needs
LLMS = {
    "gemini-flash": {
        "model": "gemini-3.8-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "extra": {"reasoning_effort": "low"},
    },
    "ollama-deepseek": {
        "model": "deepseek-r1:8b",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "client": OLLAMA_CLIENT,
    },
    "ollama-qwen": {
        "model": "qwen3:8b",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "client": OLLAMA_CLIENT,
    },
    "ollama-glm": {
        "model": "hf.co/ggml-org/GLM-4.6V-Flash-GGUF:Q4_K_M",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "client": OLLAMA_CLIENT,
    },
    "ollama-mimo": {
        "model": "hf.co/bartowski/MiMo-V2.6-Distill-Qwen-9B-GGUF:Q4_K_M",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "client": OLLAMA_CLIENT,
        # its GGUF stops on <think>, which it opens every reply with, so replace the stop list
        "extra": {"stop": ["<|im_end|>", "<|im_start|>"]},
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

    # client settings only some models need (e.g. a longer timeout), passed to the client as they are
    client = OpenAI(api_key=os.environ[config["api_key_env"]], base_url=config["base_url"], **config.get("client", {}))
    start = time.perf_counter()
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
    latency_ms = (time.perf_counter() - start) * 1000

    # some providers leave usage out; completion_tokens includes any reasoning tokens
    if response.usage is None:
        input_tokens = None
        output_tokens = None
    else:
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
    stats = {"latency_ms": latency_ms, "input_tokens": input_tokens, "output_tokens": output_tokens}

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
    return answers, stats
