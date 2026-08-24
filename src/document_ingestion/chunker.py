"""
Fixed-size sliding-window chunker (SYSTEM_DESIGN.md Section 3.1 / 7).

char_start/char_end are offsets into the *cleaned* text (post
preprocessor.clean_text), not the raw parser output - that's the text that
actually gets embedded, so citations should point at it, not the original
whitespace-noisy extraction.
"""
import math
from dataclasses import dataclass

from src.document_ingestion.preprocessor import clean_text

# Matches SYSTEM_DESIGN.md Section 7's chunking config defaults.
DEFAULT_CHUNK_SIZE_CHARS = 512
DEFAULT_OVERLAP_CHARS = 100
DEFAULT_MIN_CHUNK_SIZE_CHARS = 50


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    char_start: int
    char_end: int
    token_count: int  # rough estimate: chars / 4 (see Section 7's comment)


def chunk_text(
    text: str,
    chunk_size_chars: int = DEFAULT_CHUNK_SIZE_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
    min_chunk_size_chars: int = DEFAULT_MIN_CHUNK_SIZE_CHARS,
) -> list[TextChunk]:
    if chunk_size_chars <= 0:
        raise ValueError(f"chunk_size_chars must be positive, got {chunk_size_chars}")
    if overlap_chars < 0:
        raise ValueError(f"overlap_chars cannot be negative, got {overlap_chars}")
    if overlap_chars >= chunk_size_chars:
        raise ValueError(
            f"overlap_chars ({overlap_chars}) must be smaller than "
            f"chunk_size_chars ({chunk_size_chars}), or the window never advances"
        )

    text = clean_text(text)
    if not text:
        return []

    step = chunk_size_chars - overlap_chars
    text_len = len(text)
    chunks: list[TextChunk] = []
    start = 0

    while start < text_len:
        end = min(start + chunk_size_chars, text_len)
        content = text[start:end]
        chunks.append(
            TextChunk(
                chunk_index=len(chunks),
                content=content,
                char_start=start,
                char_end=end,
                token_count=max(1, math.ceil(len(content) / 4)),
            )
        )
        if end == text_len:
            break
        start += step

    # Safety net for unusual configs (e.g. min_chunk_size_chars > overlap_chars):
    # merge a too-small trailing chunk into the previous one instead of
    # leaving an orphan sliver. With the defaults above this rarely fires,
    # since the sliding window's overlap already guarantees the trailing
    # chunk is longer than overlap_chars.
    if len(chunks) > 1 and len(chunks[-1].content) < min_chunk_size_chars:
        last = chunks.pop()
        prev = chunks[-1]
        merged_content = text[prev.char_start : last.char_end]
        chunks[-1] = TextChunk(
            chunk_index=prev.chunk_index,
            content=merged_content,
            char_start=prev.char_start,
            char_end=last.char_end,
            token_count=max(1, math.ceil(len(merged_content) / 4)),
        )

    return chunks
