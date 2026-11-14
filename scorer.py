"""
Decides whether one answer passes. run_eval.py finds `judge` automatically.

The rule is criterion 5 in criteria.md: an answer passes only if it

  1. contains the question's `expects` phrase (case-insensitive), AND
  2. names at least one source file that actually contains that phrase on disk.

A refusal, or a failed generation, contains neither, so it fails.
"""

import re

import config

_FILENAME = re.compile(r"[\w\-]+\.txt")


def cited_files(answer: str) -> set[str]:
    """Every corpus filename mentioned anywhere in the answer."""
    folder = config.corpus_path()
    return {name for name in _FILENAME.findall(answer or "") if (folder / name).exists()}


def files_containing(phrase: str) -> set[str]:
    """Corpus files whose text contains the phrase."""
    folder = config.corpus_path()
    phrase = phrase.lower()
    return {
        p.name for p in folder.iterdir()
        if p.suffix == ".txt" and phrase in p.read_text(encoding="utf-8").lower()
    }


def judge(question, expects, answer, results) -> bool:
    if not expects or expects.lower() not in (answer or "").lower():
        return False
    return bool(cited_files(answer) & files_containing(expects))
