# Every model adapter takes (ticket, options) and returns {input: {"choice": column, "confidence": 0-1}}
# (an adapter can also add "probabilities": {column: p} if its model gives one for every column, like Jev)
# To add a model: write a file here with a map_columns function, then add it to MODELS
# (OpenAI-compatible models only need an entry in LLMS in llm.py)

from functools import partial

from mappers.models import jev, llm

MODELS = {"jev": jev.map_columns}
# every model in llm.LLMS gets an entry under its name, e.g. "gemini-flash"
for name, config in llm.LLMS.items():
    MODELS[name] = partial(llm.map_columns, config=config)
