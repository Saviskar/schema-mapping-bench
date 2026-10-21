# Every model adapter takes (ticket, options) and returns {input: {"choice": column, "confidence": 0-1}}
# (an adapter can also add "probabilities": {column: p} if its model gives one for every column, like Jev)
# To add a model: write a file here with a map_columns function, then add it to MODELS

from mappers.models import jev

MODELS = {
    "jev": jev.map_columns,
}
