# learnings.md — execution memory

## Protocol
- START of session: read this file before acting
- END of session (mandatory wrap-up): record what to avoid, which rule should change, what to do differently

## Active rules (semantic — always apply)   ← promote recurrences into CLAUDE.md
- [generalized, short, imperative rule]

## Incident log (episodic)
### [YYYY-MM-DD] <trigger / observed defect>
- Root cause: <what actually caused it>
- Fix applied: <the smallest durable correction>
- Rule learned: <generalization — or "n/a, one-off">
- Scope: <files/area in the causal path>
- Reversible: <commit/patch ref + how to revert>
- Status: candidate → promoted → retired

## Consolidation (run periodically)
- Proven recurrence (2–3x) → promote the rule into CLAUDE.md and mark the entry retired- Remove obsolete entries / ones referencing deleted files- Keep the file lean (mirror the ~200-line budget)