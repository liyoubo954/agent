---
name: backend-interview
description: Generate a targeted backend engineering interview from a candidate resume or profile. Use when the user asks to simulate a backend interview, create interview questions, evaluate a backend candidate, design resume-based technical questions, or prepare interviewer notes. Focuses on backend fundamentals, project deep dives, system design, tradeoffs, and risk signals.
allowedTools:
  - ReadFile
  - Grep
  - Glob
  - parse_resume
mode: fork
context: none
---

# Backend Interview Designer

Create a practical interview plan that tests the candidate's real experience, not a generic question bank.

## Workflow

1. Locate and parse the resume.
   - If a path is provided, read or parse that file.
   - If no path is provided, search for common names such as `resume.*`, `cv.*`, `简历.*`, `*resume*`, or `*cv*`.
   - Prefer `parse_resume` when available; otherwise extract the key facts manually.
2. Build a candidate profile.
   - Years of experience.
   - Primary languages and frameworks.
   - Databases, middleware, infrastructure, and cloud exposure.
   - Most substantial projects and the candidate's stated role.
   - Claims that need verification, such as high concurrency, performance tuning, distributed systems, or ownership.
3. Generate interview questions in three layers.
   - Fundamentals: verify depth in the declared stack.
   - Project deep dive: test actual ownership, decisions, tradeoffs, and failure handling.
   - System design: match the candidate's level and domain experience.
4. Provide evaluation guidance.
   - Include what a strong answer should cover.
   - Include follow-up probes for vague answers.
   - Include risk signals that may indicate shallow experience.

## Output

Use this structure:

```text
## Candidate Profile
- Seniority signal:
- Core stack:
- Strongest project evidence:
- Main risk signals:

## Interview Plan

### Round 1: Backend Fundamentals
1. [Topic] Question
   Strong answer:
   Follow-up:

### Round 2: Project Deep Dive
1. [Project] Question
   What to listen for:
   Risk signal:

### Round 3: System Design
1. Scenario
   Evaluation dimensions:
   Follow-up probes:

## Interviewer Notes
- Recommended focus:
- Areas to verify:
```

Do not overfit to buzzwords. Prefer questions that force the candidate to explain decisions, constraints, metrics, and incident handling.

$ARGUMENTS
