# Workflow — three roles

How this project is run. Three roles, one loop.

---

## The roles

### 1. Architect — Claude (web)
The brain. Does not touch your machine or TV.
- Designs the approach, writes the specs, docs, and the launcher page.
- Audits third-party code before anything runs.
- Reviews outputs you paste back and decides the next step.
- Owns the GO/NO-GO gates.

### 2. Worker — Claude Code (on your Mac)
The hands on the computer side. Has a real terminal on your machine.
- Scaffolds the repo, runs scripts, runs the setup tool's local server.
- Executes **only** the runbooks the Architect provides — does not improvise
  steps that touch the TV or network.
- Reports command output back (to you, to pass on).

### 3. Router — you
The link, and the only one who touches the TV.
- Carry artifacts/outputs between Architect and Worker.
- Do the TV-remote steps (DNS setting, opening the tool page, navigating).
- **Final say on anything irreversible.** Nothing permanent happens without
  your explicit OK.

---

## The loop

```
Architect writes a spec/runbook
        │
        ▼
   You hand it to the Worker
        │
        ▼
Worker runs it on the Mac ──► output
        │
        ▼
 You paste output back to Architect
        │
        ▼
Architect reviews ──► next spec, or a gate decision
```

TV-remote steps branch off to you directly; you report what the TV did.

---

## Rules that bind all three

- **Reversible only.** Every change has a tested undo.
- **Backup before any write** to the TV's app-list file.
- **Two gates** (ping, discovery) — the Architect calls stop/go.
- **Never** run the tool's reset, DNS-set, or run-arbitrary-code functions.
- When in doubt, the Worker stops and asks (via you) rather than guessing.

---

## Worker coding convention

During **implementation / code-writing** phases, the Worker uses the
**mattpocock ponytail skill**. Not during planning or discussion — code phases
only. (Standing preference; also recorded in the repo's `CLAUDE.md`.)
