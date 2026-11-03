"""Token counting.

The default is an approximation (about four characters per token), which is enough to compare
retrievers against each other and against loading the whole vault. Swap in a real tokenizer
before quoting absolute numbers.
"""

import math


def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)
