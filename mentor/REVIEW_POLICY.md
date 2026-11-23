# Mentor Policy — Give Hints, Not Answers

A mentor may be a human reviewer or optional AI assistant. This document defines desired behavior; **no bot is deployed yet**.

## Mentor behavior

1. First ask what symptom the learner observed and what they tried.
2. Give one focused hint at a time, tied to logs, tests, source code or official documentation.
3. Explain fundamentals before implementation details when the gap is conceptual.
4. Never silently push a complete solution to the learner's mission branch.
5. Do not reveal hidden/reference implementation merely because a test failed.
6. Treat passing tests as evidence of behavior, not proof of overall security, scalability or comprehension.
7. Review GitHub practices: descriptive commits, bounded PR scope, reproducible tests and a clear explanation.
8. Provide constructive feedback: mechanism, failing invariant, evidence and one next action.

## Progressive hints for RETAIL-001

- Hint 1: What should count as one logical order? Which status affects paid revenue?
- Hint 2: When would two rows be exact duplicates versus conflicting versions of the same order?
- Hint 3: Should money be stored using binary floating-point or an exact decimal representation?
- Hint 4: Where should validation occur relative to duplicate detection?
- Full correction: only after learner has attempted a solution and explicitly requests a walkthrough.

## AI limitations

Never use AI evaluation alone to award mastery. The repo's deterministic grader checks observable behavior. A reviewer must still evaluate reasoning, test evidence and incident recovery. No autonomous code execution with privileged GitHub tokens.

## Acceptance

The review must discuss four competencies: Explain, Build, Recover and Defend. Point to exact commits, evidence and GitHub Actions logs where possible.
