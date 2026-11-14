#!/usr/bin/env python3
"""
Score all five criteria in criteria.md, one row per criterion, three runs.

    python criteria_eval.py --label before

run_eval.py writes one row per QUESTION. This writes the one-row-per-CRITERION
table the README run log asks for, using the same `run_eval.run_once`, so both
files measure exactly the same pipeline. Output goes to results/.

How each criterion is counted (wording from criteria.md):
  1  questions whose top-k retrieved chunks contain the `expects` phrase, of 5
  2  answers that name a corpus .txt file, of the answers produced
     (gate refusals are not answers; a failed generation IS counted, as a miss)
  3  OUT_OF_SCOPE questions the gate refuses, of 5 (deterministic, one pass)
  4  chunks that start with THREAD:, hold exactly one "--- reply" block and
     are 60-400 chars, of all chunks (deterministic, one pass)
  5  questions whose answer passes scorer.judge, of 5

Also records a supplementary NEAR_MISS set (campus questions the corpus does
not answer) and COVERED_VAGUE set, which are not criteria but are what the
Unit 2 improvement targets.
"""

import argparse
import datetime as dt

import config
import gate
import questions as qs
import scorer
from chunker import split_documents
from ingest import load_documents
from run_eval import GENERATION_FAILED, run_once
from store import search

NEAR_MISS = [
    "Can I get a refund on my printing quota?",
    "When do the dorms open in August?",
    "Which dining hall has the best food?",
    "What time does the campus gym open?",
    "Which professor is best for intro CS?",
    "Is the housing lottery actually random?",
    "Do professors curve exams?",
    "How do I appeal a parking ticket?",
]
COVERED_VAGUE = [
    "What should I wear in winter?",
    "Is a bike worth it?",
]


def chunk_ok(text: str) -> bool:
    return text.startswith("THREAD:") and text.count("--- reply") == 1 and 60 <= len(text) <= 400


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=None)
    args = ap.parse_args()

    threshold = config.THRESHOLD if args.threshold is None else args.threshold
    top_k, corpus, variant = config.TOP_K, config.CORPUS, "default"
    items = qs.answered()

    runs = []          # per run: dict of criterion -> (num, den)
    samples = []       # real output from run 1
    for run in range(1, args.runs + 1):
        c1 = c2n = c2d = c5 = 0
        for item in items:
            answer, results, decision = run_once(item["question"], top_k, threshold, corpus, variant)
            exp = item["expects"].lower()
            hit = any(exp in r.text.lower() for r in results)
            c1 += hit
            if decision.passed:
                c2d += 1
                c2n += bool(scorer.cited_files(answer))
            c5 += scorer.judge(item["question"], item["expects"], answer, results)
            if run == 1:
                samples.append((item, answer, results, decision, hit))
            print(f"run {run}  c1={'Y' if hit else 'n'}  d={decision.best_distance:.3f}  {item['question'][:50]}")
        runs.append({"c1": (c1, len(items)), "c2": (c2n, c2d), "c5": (c5, len(items))})

    oos = [(q, gate.check(search(q, top_k=top_k), threshold=threshold)) for q in qs.OUT_OF_SCOPE]
    c3 = sum(not d.passed for _, d in oos)
    chunks = split_documents(load_documents(corpus))
    bad = [c for c in chunks if not chunk_ok(c.text)]
    c4 = (len(chunks) - len(bad), len(chunks))
    near = [(q, gate.check(search(q, top_k=top_k), threshold=threshold)) for q in NEAR_MISS]
    vague = [(q, gate.check(search(q, top_k=top_k), threshold=threshold)) for q in COVERED_VAGUE]

    f = lambda t: f"{t[0]}/{t[1]}"  # noqa: E731
    lines = [
        f"# Criteria run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `criteria_eval.py::main` (calls `run_eval.py::run_once`, `scorer.py::judge`)",
        f"- Corpus `{corpus}`, top-k {top_k}, relevance cutoff {threshold}, {args.runs} runs, cache off",
        f"- Model: `{config.MODEL}`",
        f"- When: {dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
        "| Criterion | Target | " + " | ".join(f"Run {i+1}" for i in range(args.runs)) + " |",
        "|---|---|" + "---|" * args.runs,
        "| 1. Retrieved chunk contains the answer | 4 of 5 | " + " | ".join(f(r["c1"]) for r in runs) + " |",
        "| 2. Every answer names a source | all answers | " + " | ".join(f(r["c2"]) for r in runs) + " |",
        f"| 3. Gate stops out-of-corpus questions | 4 of 5 | " + " | ".join([f"{c3}/{len(oos)}"] * args.runs) + " |",
        f"| 4. Every chunk is one whole reply with title | 100% | " + " | ".join([f(c4)] * args.runs) + " |",
        "| 5. Cited source is the right source | 4 of 5 each run | " + " | ".join(f(r["c5"]) for r in runs) + " |",
        "",
        "## Supplementary: near-miss campus questions (should be refused)",
        "",
        f"Refused {sum(not d.passed for _, d in near)} of {len(near)}.",
        "",
        "| Question | Best distance | Gate |", "|---|---|---|",
        *[f"| {q} | {d.best_distance:.3f} | {'refused' if not d.passed else '**let through**'} |" for q, d in near],
        "",
        "## Supplementary: vague questions the corpus does cover (should pass)",
        "",
        "| Question | Best distance | Gate |", "|---|---|---|",
        *[f"| {q} | {d.best_distance:.3f} | {'passed' if d.passed else '**refused**'} |" for q, d in vague],
        "",
        "## Real output (run 1)",
        "",
    ]
    for item, answer, results, decision, hit in samples:
        top = results[0]
        lines += [
            f"### {item['question']}",
            "",
            f"- expects: `{item['expects']}` · in retrieved chunks: {'yes' if hit else 'NO'} · "
            f"best distance {decision.best_distance:.4f} ({'passed' if decision.passed else 'refused'})",
            f"- top chunk ({top.source}):",
            "", "```", top.text, "```", "",
            "- answer:", "", "```", answer, "```", "",
        ]
    lines += ["### Criterion 3 — out-of-scope questions", "", "```"]
    lines += [f"{d.best_distance:.3f}  {'refused' if not d.passed else 'LET THROUGH'}  {q}" for q, d in oos]
    lines += ["```", "", "### Criterion 4 — chunks failing the structure test", "",
              "```", "\n".join(c.label for c in bad) or "(none)", "```", ""]
    failed = sum(GENERATION_FAILED in s[1] for s in samples)
    if failed:
        lines += [f"> {failed} of {len(samples)} answers in run 1 are generation failures, not model output.", ""]

    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"criteria_{dt.datetime.now():%Y-%m-%d_%H%M}{'_' + args.label if args.label else ''}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
