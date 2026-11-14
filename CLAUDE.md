# CLAUDE.md — vidaa-launcher

## What this is
Minimal Apple-style launcher for Hisense VIDAA 9 TVs, installed via VIDAA's
app-list mechanism. Tier 1 needs no always-on server. Tier 2 (optional
watcher) runs on the user's own always-on box. Every change reversible.
See docs/03-architecture.md.

## Roles
- Architect = Claude web (designs, writes specs/launcher, reviews, owns gates).
- Worker = Claude Code here (runs computer-side commands, reports output).
- Router = the human (routes between us, does TV-remote steps, final say on
  anything irreversible).

## Hard rules
- Reversible only; tested undo for every change.
- Native D-pad or abort.
- Back up the TV app-list file before any write.
- Never run the setup tool's reset, DNS-set, or run-arbitrary-code functions.
- Only run runbooks the Architect provides. Don't improvise TV/network steps.
- If unsure, stop and ask via the human.

## Gates
- GATE 1 = ping (computer <-> TV must see each other).
- GATE 2 = discovery (firmware must expose the needed functions).
- GATE 3 = native D-pad test tile (cursor or no key events = STOP and full
  rollback, see docs/00-project-plan.md).
Work past a gate only after the Architect confirms it passed.

## Coding convention
Use the mattpocock ponytail skill during implementation (code-writing) phases
only — not during planning.
