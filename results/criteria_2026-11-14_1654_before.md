# Criteria run log — before

- Produced by: `criteria_eval.py::main` (calls `run_eval.py::run_once`, `scorer.py::judge`)
- Corpus `advice_threads`, top-k 5, relevance cutoff 0.45, 3 runs, cache off
- Model: `gemini-3.5-flash-lite`
- When: 2026-11-14 16:54

| Criterion | Target | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 |
| 2. Every answer names a source | all answers | 0/5 | 0/5 | 0/5 |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 |
| 4. Every chunk is one whole reply with title | 100% | 75/75 | 75/75 | 75/75 |
| 5. Cited source is the right source | 4 of 5 each run | 0/5 | 0/5 | 0/5 |

## Supplementary: near-miss campus questions (should be refused)

Refused 7 of 8.

| Question | Best distance | Gate |
|---|---|---|
| Can I get a refund on my printing quota? | 0.414 | **let through** |
| When do the dorms open in August? | 0.491 | refused |
| Which dining hall has the best food? | 0.501 | refused |
| What time does the campus gym open? | 0.541 | refused |
| Which professor is best for intro CS? | 0.549 | refused |
| Is the housing lottery actually random? | 0.573 | refused |
| Do professors curve exams? | 0.583 | refused |
| How do I appeal a parking ticket? | 0.614 | refused |

## Supplementary: vague questions the corpus does cover (should pass)

| Question | Best distance | Gate |
|---|---|---|
| What should I wear in winter? | 0.460 | **refused** |
| Is a bike worth it? | 0.297 | passed |

## Real output (run 1)

### How late in the semester can I still declare a course pass/fail?

- expects: `week eight` · in retrieved chunks: yes · best distance 0.2908 (passed)
- top chunk (thread_first_year_regret.txt):

```
THREAD: What do you wish you'd known in first year?
--- reply 2 (28 votes) ---
That you can take a course pass/fail and declare it late — up to week eight. I carried a grade I didn't need to.
```

- answer:

```
[GENERATION FAILED — no answer produced] ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 
```

### How many black and white pages does the $30 printing quota cover?

- expects: `600` · in retrieved chunks: yes · best distance 0.1660 (passed)
- top chunk (thread_printing.txt):

```
THREAD: Is the printing quota enough?
--- reply 1 (17 votes) ---
For most people yes. $30 is about 600 pages black and white. It's the colour printing that eats it — eight times the cost per page.
```

- answer:

```
[GENERATION FAILED — no answer produced] ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 
```

### What days are the dorm laundry machines least busy?

- expects: `Tuesday` · in retrieved chunks: yes · best distance 0.2747 (passed)
- top chunk (thread_laundry_timing.txt):

```
THREAD: When is laundry actually free in the dorms?
--- reply 1 (27 votes) ---
Tuesday and Wednesday mornings, every building. Sunday evening is the worst and it isn't close.
```

- answer:

```
[GENERATION FAILED — no answer produced] ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 
```

### Is there a deadline for switching my meal plan tier?

- expects: `ten days` · in retrieved chunks: yes · best distance 0.2204 (passed)
- top chunk (thread_meal_plan_tier.txt):

```
THREAD: Which meal plan tier is right?
--- reply 3 (11 votes) ---
Remember you can only change it once and only in the first ten days. I waited and got stuck on a plan I didn't use.
```

- answer:

```
[GENERATION FAILED — no answer produced] ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 
```

### How much does it cost to rent a locker in the commuter lounge?

- expects: `$20` · in retrieved chunks: yes · best distance 0.2892 (passed)
- top chunk (thread_commuting.txt):

```
THREAD: Commuting an hour each way — is it survivable?
--- reply 2 (21 votes) ---
The commuter lounge in the student centre has lockers you can rent for $20 a year and it changes the experience completely.
```

- answer:

```
[GENERATION FAILED — no answer produced] ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 
```

### Criterion 3 — out-of-scope questions

```
0.893  refused  What is the capital of Mongolia?
0.896  refused  How do I change the oil in a diesel engine?
0.893  refused  Who won the 1994 World Cup?
0.807  refused  What is the recommended dosage of ibuprofen for a headache?
0.835  refused  How do I write a for loop in Rust?
```

### Criterion 4 — chunks failing the structure test

```
(none)
```

> 5 of 5 answers in run 1 are generation failures, not model output.
