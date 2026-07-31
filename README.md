# Debugging Olympics — Month 3 (FastAPI)

A 30-minute timed challenge. This is a small ticketing API with **3 intentional
bugs**. Find them and fix them before the clock runs out.

## The bugs

Somewhere in this codebase:

1. **Broken access control** — an action that should be admin-only is not
   actually restricted to admins.
2. **SQL injection** — a query is built from user input in a way that lets
   an attacker manipulate it.
3. **Missing input validation** — an endpoint accepts data it shouldn't
   (empty/out-of-range values that should be rejected).

No hints beyond that — that's the exercise. Read the code, poke the API,
and use the grader below to check your work.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API comes up on `http://localhost:8000`. Interactive docs are at
`http://localhost:8000/docs`.

Two seeded accounts:

| username | password    | role  |
|----------|-------------|-------|
| admin    | admin123    | admin |
| trainee  | trainee123  | user  |

## Rules

- Solo exercise, 30 minutes on the clock.
- You may use any tool (including AI) to help you find bugs, but you must
  understand and be able to explain every fix you make.
- Don't change the API's shape (endpoint paths, request/response fields) —
  only fix the underlying bugs.



It logs in, hits each buggy endpoint, and prints `PASS`/`FAIL` per bug plus
a score out of 3. Use it to confirm you're done before submitting.

## Submitting

1. Clone or download this repo.
2. Create your **own public repo** on GitHub.
3. Push your fixed version there.
4. Share the repo link 1:1 with your instructor.

Do not open a pull request against this template — this is a solo exercise
and everyone starts from the same bugs.
