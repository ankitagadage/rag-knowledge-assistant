"""
Text cleanup applied between parsing (parsers.py) and chunking (chunker.py).
Kept intentionally minimal: normalize line endings and collapse excess
whitespace, without altering actual content, so chunk char_start/char_end
offsets stay meaningful and embeddings aren't diluted by formatting noise.
"""
import re


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)  # collapse runs of spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse 3+ blank lines to 1
    return text.strip()
