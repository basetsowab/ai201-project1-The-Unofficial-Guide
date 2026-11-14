# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**How I check it:** a question counts if the exact `expects` phrase from
`questions.py` appears in at least one of the top-k retrieved chunks.

**Why this target:** Not 5 of 5, because two of my questions are deliberately
hard for meaning-only search: the laundry question says "least busy" while the
thread says "free", and the pass/fail answer is split across two threads that
both compete for the top slots. Not 3 of 5, because every thread is short and
on a single topic, so a question naming the topic should land in the right
thread almost every time.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**How I check it:** an answer counts if it contains a `.txt` filename from
`corpora/advice_threads/documents/`. A refusal from the gate is not an answer
and is not counted against this.

**Why this target:** All of them, not most, because citing is the one thing the
grounding instruction asks for on every single call and every chunk carries its
filename into the prompt. If even one answer comes back without a filename,
the prompt isn't doing its job and a reader can't check the claim.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** When I set the cutoff (0.45) the five `OUT_OF_SCOPE`
questions scored 0.807–0.896 and my in-corpus questions 0.166–0.291, a clean
gap, so I expect all five to be refused. I kept 4 of 5 rather than raising it
to 5 of 5 because I set the cutoff on these exact questions, and the near-miss
campus questions I also tried (0.414–0.614) show that a question sharing
vocabulary with a thread can creep much closer than these five do.

---

## 4. Every chunk is one whole reply with its thread title

Every chunk in the index (100%, counted over the whole corpus, not a sample)
meets all three of these: it starts with its thread's `THREAD:` line, it holds
exactly one `--- reply` block, and it is between 60 and 400 characters long.

**How I check it:** `python app.py chunks -n 200` prints every chunk; count the
ones that fail any of the three tests. Zero failures is the target.

**Why this target:** Every thread in advice_threads is a title plus 2–5 voted
replies of one to three sentences, and each reply is a separate opinion. A
reply without its title loses the topic ("Tuesday and Wednesday mornings,
every building" — of what?), and two replies merged together mix advice that
often disagrees (the bike thread's reply 2 is literally "Counterpoint"). The
60 floor is there because the starter's chunker made a 2-character chunk out of
the tail of a thread; the 400 ceiling is about the longest reply plus its
title, so anything bigger means replies got merged. It is 100% and not "most"
because this is a structural property of my chunker, not a judgment call: if
one chunk breaks it, the splitting rule is wrong.

---

## 5. The cited source is the right source

In each of the three runs, for at least 4 of my 5 test questions the answer
both contains the `expects` phrase from `questions.py` and names a source file
that actually contains that phrase.

**How I check it:** for each answer, look for the `expects` phrase, then check
that at least one `.txt` file named in the answer contains that phrase on disk.
A refusal counts as a miss.

**Why this target:** Criterion 2 only checks that *a* filename appears; this one
checks it's the *right* one, which is what a student reading the answer would
actually rely on. 4 of 5 and not 5 of 5 because the pass/fail question has its
answer in two threads and the laundry question is paraphrased, so I expect at
least one of them to wobble. It has to hold in every run, not on average,
because a citation that's right two times in three isn't one you can trust.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
