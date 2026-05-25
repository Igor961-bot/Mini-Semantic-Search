from dataclasses import dataclass


@dataclass(slots=True)
class TextChunk:
    index: int
    text: str


def clean_text(text: str) -> str:
    # keep only simple single-space text so chunking stays predictable
    return " ".join(text.replace("\x00", " ").split())


def split_into_chunks(
    text: str,
    chunk_size_words: int,
    chunk_overlap_words: int,
) -> list[TextChunk]:
    # overlap cannot be bigger than the chunk itself
    if chunk_size_words <= chunk_overlap_words:
        raise ValueError("chunk_size_words must be larger than chunk_overlap_words")

    # clean once and split by words
    cleaned = clean_text(text)
    if not cleaned:
        return []

    words = cleaned.split()
    step = chunk_size_words - chunk_overlap_words
    chunks: list[TextChunk] = []

    # build overlapping windows of words
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size_words]
        if not chunk_words:
            continue

        chunks.append(
            TextChunk(
                index=len(chunks),
                text=" ".join(chunk_words),
            )
        )

        if start + chunk_size_words >= len(words):
            break

    return chunks


def make_snippet(text: str, max_chars: int = 280) -> str:
    # keep search previews short for the page
    cleaned = clean_text(text)
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip() + "..."
