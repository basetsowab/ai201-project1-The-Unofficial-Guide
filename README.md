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

**Read this first:** there is no Gemini API key on this machine, so every
call to the answer-writing model failed with `400 INVALID_ARGUMENT: API key not
valid`. Retrieval, the gate and chunking all ran for real. Generation produced
no answers. I didn't invent any, and the run log shows the failures as they
happened.

Files: `results/run_2026-11-14_1654_before.md` (from `run_eval.py::main`, one
row per question) and `results/criteria_2026-11-14_1654_before.md` (from
`criteria_eval.py::main`, one row per criterion). Three runs, cache off, top-k
5, cutoff 0.45.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | all answers | 0/5 | 0/5 | 0/5 | MISSED |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Every chunk is one whole reply with title | 100% of chunks | 75/75 | 75/75 | 75/75 | MET |
| 5. Cited source is the right source | 4 of 5, every run | 0/5 | 0/5 | 0/5 | MISSED |

Criteria 3 and 4 are one deterministic pass each (a fixed gate comparison and a
count over the chunk list), so the same number is in all three columns.
Criterion 1 is also deterministic: retrieval returned identical distances on
all three runs, as the run log shows. The only part that could have varied
between runs is the model's answer, and it never ran.

**Real output, run 1** (from `results/criteria_2026-11-14_1654_before.md`):

Criterion 1: `store.py::search` for "Is there a deadline for switching my meal
plan tier?" (expects `ten days`). Rank 1 chunk, distance 0.2204:

```
THREAD: Which meal plan tier is right?
--- reply 3 (11 votes) ---
Remember you can only change it once and only in the first ten days. I waited and got stuck on a plan I didn't use.
```

Criteria 2 and 5: the answer `run_eval.py::run_once` recorded for that
question, which is the same for all five questions on all three runs:

```
[GENERATION FAILED — no answer produced] ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type':
```

Criterion 3: `run_eval.py::check_out_of_scope`, cutoff 0.45:

```
0.893  refused  What is the capital of Mongolia?
0.896  refused  How do I change the oil in a diesel engine?
0.893  refused  Who won the 1994 World Cup?
0.807  refused  What is the recommended dosage of ibuprofen for a headache?
0.835  refused  How do I write a for loop in Rust?
```

Criterion 4: chunks from `chunker.py::split_documents` failing the
title / one-reply / 60–400-character test:

```
(none)
```

Also recorded, though it isn't a criterion: the near-miss campus questions from
Unit 1. 7 of 8 were refused. "Can I get a refund on my printing quota?" (0.414)
got through, and the covered-but-vague "What should I wear in winter?" (0.460)
was refused.

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | The `expects` phrase was in a retrieved chunk for 5 of 5 questions on every run, and the target is 4 of 5. Not close. |
| 2 | Every answer names a source | MISSED | No answer named a file. There were no real answers at all, and an error string isn't a cited answer. The criterion is about what the system produces, and what it produced cited nothing. I'm not calling this "N/A": the user would get no source. |
| 3 | Gate stops out-of-corpus questions | MET | 5 of 5 refused, against a target of 4 of 5, and the closest out-of-scope question (0.807) is nearly twice the cutoff away. |
| 4 | Every chunk is one whole reply with title | MET | 75 of 75 chunks passed all three structure checks. The target was 100%, so a single failure would have been a miss. |
| 5 | Cited source is the right source | MISSED | 0 of 5 in each run, against 4 of 5 in each run. `scorer.py::judge` needs the `expects` phrase and a correct filename in the answer, and the answer held neither. |

**Arguing the other side on 2 and 5:** you could say they were never tested,
so "missed" is unfair to the pipeline. I still call them missed, because the
target says what the system has to *produce* and it produced nothing usable. I
haven't revised either criterion, because the measurement isn't broken: with
a key, exactly the same check would run unchanged.

## Diagnoses

**Criteria 2 and 5: generation stage.** The mechanism: `generate.py::generate`
sends the prompt to Gemini with the `GEMINI_API_KEY` from `.env`, which is
still the `.env.example` placeholder. Google rejects it with HTTP 400
`API_KEY_INVALID`, so no text ever comes back. `run_eval.py::run_once` records
the exception string as the answer. That string has no `.txt` filename
(criterion 2) and no `expects` phrase (criterion 5).

It is *only* the generation stage. Working backwards, as the brief suggests:
for every one of the five questions, the chunk containing the answer was
retrieved (at rank 1 for all five), and the gate passed it (best distances
0.166–0.291, cutoff 0.45). Loading, chunking, embedding and retrieval all did
their job. The prompt was correct too: `app.py ask --show-prompt` prints the
right chunks and the grounding instruction.

**Pattern:** both misses are one failure, not two. Every question that reached
the model failed the same way, with the same error.

**What the misses can't tell me:** whether the grounding prompt actually
makes the model cite correctly. That is the real question behind criteria 2
and 5, and it is still unanswered.

**On the three I met:** they were all met on the first try with room to spare,
which suggests those targets were safe rather than that the system is
excellent:

- Criterion 1 at 4 of 5 is loose. All five answers are at **rank 1**, so the
  stricter version I'd write now is "the top-1 chunk contains the answer for
  5 of 5".
- Criterion 3's five `OUT_OF_SCOPE` questions (capital of Mongolia, diesel
  engines) are so far from campus life that no plausible cutoff would let
  them through. The real test is the near-miss campus questions, where the
  gate went 7 of 8.
- Criterion 4 tests something my own chunker guarantees by construction.

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
