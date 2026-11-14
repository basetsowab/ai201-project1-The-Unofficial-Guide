"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Strategy for advice_threads: ONE CHUNK PER REPLY, each one prefixed with
    its thread's title line.

    Every document is a `THREAD:` title followed by 2-5 replies, each opened by
    a `--- reply N (V votes) ---` marker. Replies are one to three sentences and
    each is a separate opinion (some openly disagree with the one before), so a
    reply is the natural unit of meaning. On its own, though, a reply often
    doesn't say what it's about ("Tuesday and Wednesday mornings, every
    building"), so the title is repeated at the top of every chunk. That
    repeated title is the overlap: it's the only context neighbouring chunks
    share, and no reply text is duplicated.

    A document with no reply markers (or a reply longer than CHUNK_SIZE, which
    doesn't happen in this corpus) falls back to the fixed-window splitter so
    nothing is silently dropped.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        lines = doc.text.split("\n")
        title = lines[0].strip() if lines and lines[0].startswith("THREAD:") else ""
        parts = _REPLY_MARKER.split(doc.text)

        # parts = [preamble, marker1, body1, marker2, body2, ...]
        replies = [
            (parts[i].strip(), parts[i + 1].strip())
            for i in range(1, len(parts) - 1, 2)
            if parts[i + 1].strip()
        ]

        if not title or not replies:
            chunks.extend(fallback_split([doc]))
            continue

        for index, (marker, body) in enumerate(replies):
            text = f"{title}\n{marker}\n{body}"
            if len(text) > config.CHUNK_SIZE:
                chunks.extend(fallback_split([Document(doc.source, text)]))
                continue
            chunks.append(
                Chunk(
                    text=text,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


# Matches the reply header line, e.g. "--- reply 3 (22 votes) ---".
_REPLY_MARKER = re.compile(r"^(---\s*reply\s+\d+.*?---)\s*$", re.MULTILINE)


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
