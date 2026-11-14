# The Unofficial Guide

Baset Sowab — corpus: `advice_threads`

How the starter works, and every command, is in `RUNNING.md`.

---

# Unit 1

## What This Does

The Unofficial Guide answers plain-English questions about student life from
`advice_threads`: 23 forum-style threads where students answer each other's
questions about things like laundry timing, meal plans, printing quotas,
pass/fail rules, parking and commuting. Ask it something like "Is there a
deadline for switching my meal plan tier?" and it finds the closest replies,
answers from them only, and names the thread file the answer came from. If no
reply is close enough (best distance over 0.45), it says "I don't have enough
information about that" instead of guessing. It runs from the command line:
`python app.py ask "your question"`.

## Chunking Strategy

**Chunk size:** one reply per chunk, with its thread title on top — 131 to 280
characters, 201 on average, 75 chunks from 23 documents. `CHUNK_SIZE` (800) is
kept only as a safety ceiling; no reply in this corpus comes near it.
**Overlap:** no reply text is shared between chunks. The thread's `THREAD:`
title line is repeated at the top of every chunk from that thread, and that
repeated title is the only overlap.

Why: every document in advice_threads is a forum thread — a `THREAD:` question
followed by 2–5 replies, each opened by a `--- reply N (V votes) ---` line.
Documents average only ~540 characters, and each reply is one to three
sentences giving one person's opinion. Replies in the same thread often
disagree (the bike thread's second reply starts with "Counterpoint, I sold
mine"), so keeping a whole thread as one chunk would blend opposite advice into
one vector. Splitting by character count was worse: the starter's
`fallback_split` made 26 chunks, cut replies mid-sentence at the 800-character
mark, and produced a 2-character chunk out of the tail of one thread.

A reply on its own often doesn't say what it is about ("Tuesday and Wednesday
mornings, every building. Sunday evening is the worst"), which is why the title
is repeated. With the title, every chunk can answer a question by itself
without reading its neighbours. The split happens on the reply marker line
(a regex in `chunker.py`), so it never cuts a sentence.

What I considered and rejected: whole-thread chunks (23 chunks). They would be
the right call for a corpus of single-topic posts, but here a question about
the meal-plan *deadline* would match the meal-plan thread equally through its
replies about *which tier to buy*, and the useful sentence would be buried.

## Sample Chunks

Printed with `python app.py chunks -n 5`. All five come from
`chunker.py::split_documents`.

**Chunk 1** — source: `thread_bike_commute.txt` (chunk #0) — produced by: `chunker.py::split_documents`

```
THREAD: Is a bike worth it for a 20 minute walk commute?
--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.
```

**Chunk 2** — source: `thread_first_gen.txt` (chunk #1) — produced by: `chunker.py::split_documents`

```
THREAD: Anything specific for first-generation students?
--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.
```

**Chunk 3** — source: `thread_laptop_specs.txt` (chunk #2) — produced by: `chunker.py::split_documents`

```
THREAD: How much laptop do I actually need for CS courses?
--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

**Chunk 4** — source: `thread_parking.txt` (chunk #1) — produced by: `chunker.py::split_documents`

```
THREAD: Worth getting a parking permit?
--- reply 2 (21 votes) ---
Street parking on Verrill is legal and free and unmarked, which is why half the upper years do it.
```

**Chunk 5** — source: `thread_sleep_schedule.txt` (chunk #1) — produced by: `chunker.py::split_documents`

```
THREAD: Everyone says fix your sleep. Does it actually matter?
--- reply 2 (37 votes) ---
The library being open until 2am is a trap. It's a resource, not a schedule.
```

## Sample Answer

**Question:** Is there a deadline for switching my meal plan tier?

**Answer:**

```
PENDING — needs a real model response. The Gemini key in .env is still the
placeholder, so no answer has been generated yet. Run:
    python app.py ask "Is there a deadline for switching my meal plan tier?"
and paste the output here verbatim, including the "Source:" line.
```

Retrieval for this question, pasted from
`python app.py retrieve "Is there a deadline for switching my meal plan tier?"`
(no model call), so the chunk the answer should come from is visible:

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.2204     thread_meal_plan_tier.txt        THREAD: Which meal plan tier is right? --- reply 3 (...
2   0.3356     thread_meal_plan_tier.txt        THREAD: Which meal plan tier is right? --- reply 4 (...
3   0.3489     thread_meal_plan_tier.txt        THREAD: Which meal plan tier is right? --- reply 2 (...
4   0.3765     thread_meal_plan_tier.txt        THREAD: Which meal plan tier is right? --- reply 1 (...
5   0.5735     thread_first_year_regret.txt     THREAD: What do you wish you'd known in first year? ...

Gate: best distance 0.220 is under the 0.45 cutoff
```

Rank 1 is reply 3: "Remember you can only change it once and only in
the first ten days."

> **Correction (Unit 2):** an earlier version of this block showed
> four-decimal distances (0.2198, 0.3357, ...) that were not copied from real
> output. This one is pasted directly from the command above.

**Top-k:** kept at 5. Every thread has 2–5 replies, so k=5 can bring back a
whole thread's worth of replies for the question's topic. For the pass/fail
question that matters: the answer ("week eight") is in two threads, and the
`thread_pass_fail.txt` copy only came back at position 4. At k=3 it would
have been lost, leaving only the `first_year_regret` copy.

**Grounding prompt:** I tightened `GROUNDING_INSTRUCTION` in `generate.py` with
three rules for this corpus: only cite a file for a claim that's actually in
that file's excerpt, report replies as what students say and flag it when
they disagree, and end every answer with a `Source: <filename>` line so
criterion 2 can be checked by looking at one line.

**My relevance cutoff: 0.45** (`config.THRESHOLD`; the starter shipped 0.6).

Measured with `store.py::search`, top-k 5, on the reply-per-chunk index:

| Question | In corpus? | Best distance |
|---|---|---|
| How late in the semester can I still declare a course pass/fail? | yes | 0.291 |
| How many black and white pages does the $30 printing quota cover? | yes | 0.166 |
| What days are the dorm laundry machines least busy? | yes | 0.275 |
| Is there a deadline for switching my meal plan tier? | yes | 0.220 |
| How much does it cost to rent a locker in the commuter lounge? | yes | 0.289 |
| What is the capital of Mongolia? | no | 0.893 |
| How do I change the oil in a diesel engine? | no | 0.896 |
| Who won the 1994 World Cup? | no | 0.893 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.807 |
| How do I write a for loop in Rust? | no | 0.835 |

The two groups are far apart: in-corpus 0.166–0.291, out-of-corpus
0.807–0.896. Any number from 0.3 to 0.8 separates *these* ten. So the gap alone
didn't pick the number. What did was a third group I tried: campus questions
that sound like they belong but that the threads don't actually answer.

| Near-miss question (not answered by the corpus) | Best distance | Closest file |
|---|---|---|
| Can I get a refund on my printing quota? | 0.414 | thread_printing.txt |
| When do the dorms open in August? | 0.491 | thread_laundry_timing.txt |
| Which dining hall has the best food? | 0.501 | thread_meal_plan_tier.txt |
| What time does the campus gym open? | 0.541 | thread_study_spots.txt |
| Which professor is best for intro CS? | 0.549 | thread_laptop_specs.txt |
| Is the housing lottery actually random? | 0.573 | thread_transfer_credits.txt |
| Do professors curve exams? | 0.583 | thread_pass_fail.txt |
| How do I appeal a parking ticket? | 0.614 | thread_parking.txt |

At the starter's 0.6, seven of those eight would reach the model with chunks
that are on the right *topic* but don't hold an answer — exactly the case
where a model writes something plausible and wrong. At 0.45, seven of eight are
refused and the eighth (printing refund, 0.414) still gets through to the
grounding prompt, which has to catch it.

What 0.45 gets wrong: vague questions the corpus *does* cover can land above
it. "What should I wear in winter?" scored 0.460 against
`thread_winter_advice.txt` and is refused, even though that thread answers it.
I accepted that: my five test questions sit at 0.291 or below, and a refusal
is easier for a reader to recover from (rephrase) than a confident wrong
answer they don't know to doubt.

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1. Writing the criteria.** I asked Claude Code (Claude Opus 5.5) to do
the project for me, end to end. Before writing anything it pointed out that the
brief says the test questions and criteria 4–5 should be my own and asked how I
wanted to handle that. I told it to go ahead, so the five questions in
`questions.py`, criteria 4 and 5, and the "why" lines under all five were
drafted by Claude from what it read in the corpus. They were committed
(`ded199c`, "Milestone 2") before any retrieval was run, so the order the brief asks for held,
but the wording is the model's, not mine.

**2. Picking the cutoff.** Claude ran my ten questions through retrieval and
the two groups came out 0.166–0.291 and 0.807–0.896, so any cutoff between 0.3
and 0.8 would have separated them, and the starter's 0.6 looked fine. Instead
of stopping there, it tried eight campus-sounding questions the threads don't
actually answer (gym hours, housing lottery, curved exams). Seven of them
scored under 0.6, so at 0.6 they would have reached the model. That's why the
cutoff went down to 0.45. The cost it flagged was that a vague but covered
question ("What should I wear in winter?", 0.460) now gets refused.

**Setup note:** `pip install -r requirements.txt` failed on Python 3.12 on
Windows because `chroma-hnswlib` 0.7.6 has no prebuilt wheel for it and needs
a C++ compiler. Claude checked which versions had wheels and rebuilt the venv
on Python 3.11, which the course supports.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
