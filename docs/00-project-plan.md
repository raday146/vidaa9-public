# VIDAA Launcher — Project Plan

A minimal, Apple-style launcher for Hisense **VIDAA 9** TVs, with **no
always-on server** and every change **reversible**. This plan is the roadmap;
each stage will get its own detailed guide in the repo.

---

## Goal (two tracks)

1. **Clean up** — reduce ads/tracking/clutter using the TV's own settings.
   Always available, zero risk. (Covered in a separate `cleanup.md`.)
2. **Launcher** — install a minimal home-screen *page* (wallpaper, clock, dock
   of your apps) through VIDAA's own app-list mechanism. Experimental on VIDAA 9
   "Q" firmware; this is the research part.

Secondary goal: **document it all** so other VIDAA owners can reproduce it, and
collect a compatibility table across firmware versions.

---

## Ground rules (non-negotiable)

- **Reversible only.** Nothing proceeds without a tested undo.
- **Backup before any write.** The TV's app-list file is copied before we touch
  it. That copy is the restore point.
- **Read before write.** We confirm what the firmware allows (read-only) before
  changing anything.
- **Hands off the dangerous controls.** We never use the tool's reset,
  DNS-set, or run-arbitrary-code functions. Only: read app list, add one tile,
  remove one tile.
- **Native D-pad or abort.** If the launcher can only run in the TV Browser
  with the virtual cursor, the project stops and everything is rolled back
  (see [Full rollback](#full-rollback)).
- **GO / NO-GO gates.** Three hard checkpoints. If any fails, we stop with a
  clean result and no harm done.
- **Hosting = Cloudflare Pages.** The launcher page is served from Cloudflare
  Pages. See [03-architecture.md](03-architecture.md) for the three tiers.

---

## Stages at a glance

| # | Stage | Side | Priority | Gate |
|---|-------|------|----------|------|
| A | Computer prep | Computer | Critical | |
| B | TV prep | TV | Critical | |
| C | Communication (ping) | Both | **Critical** | **GATE 1** |
| D | DNS redirect | Both | Critical | |
| E | Discovery (read-only) | Both | **Critical** | **GATE 2** |
| E2 | D-pad test tile | Both | **Critical** | **GATE 3** |
| F | Launcher build | Computer | Medium | |
| G | Change (install one tile) | Both | Medium | backup+undo |
| H | Test & record | Both | Medium | |
| I | Repo & share | Computer | Not urgent | |
| J | Watcher auto-open (K3s) | Both | **Primary goal** | |

---

## Stage A — Computer side (prep)  · Critical
Goal: the computer is ready to serve the tool and act as the DNS.
- Note the computer's Wi-Fi IP (**COMPUTER-IP**).
- Install the setup tool locally and the DNS tool (`dnsmasq`).
- Keep the machine awake for the session.
- *Undo:* nothing changed on the TV yet; just close the tools.

## Stage B — TV side (prep)  · Critical
Goal: the TV is reachable and we know its numbers.
- Note the TV's IP (**TV-IP**), gateway, subnet (from Network settings in
  Automatic mode — screenshot it).
- Confirm the TV's software version (for the compatibility table).
- *Undo:* nothing changed; reading only.

## Stage C — Communication / ping  · Critical · **GATE 1**
Goal: prove the computer and TV can see each other on this Wi-Fi.
- From the computer: `ping TV-IP`.
- **Replies → proceed. Timeout → STOP** (network isolates devices; this method
  can't work on that network).

## Stage D — DNS redirect  · Critical
Goal: the TV treats `vidaahub.com` as the computer, temporarily.
- Computer runs the small DNS server (Half 1).
- TV's DNS set to COMPUTER-IP (Half 2).
- Full steps + undo already written in `01-dns-setup.md`.
- *Undo:* TV back to Automatic; stop the DNS server.

## Stage E — Discovery (read-only)  · Critical · **GATE 2**
Goal: find out what this firmware actually allows — the real go/no-go.
- Open the tool's page on the TV; run only:
  - the function explorer (lists the TV's built-in functions),
  - read the app-list file,
  - **save an untouched copy of the app-list file = restore point**.
- Questions answered: does `HiUtils_createRequest` / file-read exist? Is there
  any app-launch function? Can we add a tile?
- **Nothing exposed → STOP** and record "VIDAA 9 Q: closed." Still a useful
  result for the repo.
- *Undo:* read-only; nothing to undo.

## Stage E2 — D-pad test tile  · Critical · **GATE 3**
Goal: prove the remote's D-pad reaches our page as native key events.
- Precondition: the Stage E backup exists.
- Install a minimal test tile whose page only shows which key events arrive
  (arrows, OK, Back).
- **Native key events arrive → proceed. Virtual cursor appears, or no key
  events → STOP** and run the [Full rollback](#full-rollback).
- *Undo:* remove the test tile via the tool's uninstall, or restore the backup
  app-list file.

## Stage F — Launcher build  · Medium
Goal: the launcher page itself (matches your reference screenshot — see spec
below). Built on the computer, hosted on Cloudflare Pages.
- *Undo:* it's just a web page; nothing on the TV yet.

## Stage G — Change stage (install one tile)  · Medium · backup + undo
Goal: add a single app-list entry pointing to the launcher.
- Precondition: the Stage E backup exists.
- Add one tile via the tool's install method; it appears at the end of the app
  row.
- *Undo:* remove that one tile via the tool's uninstall, or restore the backup
  app-list file.

## Stage H — Test & record  · Medium
Goal: see what actually works and write it down.
- Does the launcher open? Do tiles open apps? Which apps work (web-based vs
  native like Netflix)?
- Record results for the compatibility table.

## Stage I — Repo & share  · Not urgent
Goal: package it for other VIDAA owners.
- Private repo first; make public once tested on your TV.
- Contents: README, `cleanup.md`, `01-dns-setup.md`, discovery + install
  guides, the launcher page, a compatibility table others can add rows to.

## Stage J — Watcher auto-open  · **Primary goal**
Goal: the launcher opens by itself on TV power-on and after Home.
- Run the watcher container (Tier 2, `watcher/`) on our K3s cluster.
- It opens the launcher tile when the TV powers on and after Home is pressed.
- One firewall rule only: watcher host -> TV, TCP 36669.
- Uses our own extracted Hisense client certificate; never committed.
- Why it's needed: the TV's "last used" startup option does **not** reopen
  apps (tested on our VIDAA 9), so there is no built-in way to boot into the
  launcher.
- *Undo:* remove the watcher deployment and its firewall rule.

---

## Full rollback

Returns the TV and network to exactly how they were before the project:

1. Remove our tile: tool uninstall, or restore the app-list backup from
   Stage E.
2. TV network back to **Automatic** (DNS no longer pointing at the computer).
3. Stop the DNS tool and the local server on the computer.
4. Delete the Cloudflare Pages project.
5. Remove the watcher and its firewall rule (watcher host -> TV, TCP 36669).

---

## Priority summary

**Critical (do carefully, in order):** A, B, C (gate), D, E (gate), E2 (gate).
These decide whether the launcher is even possible on your TV, and protect
against anything irreversible.

**Medium (the actual build, only after both gates pass):** F, G, H.

**Not urgent (polish / nice-to-have):**
- Repo made public.
- Home-button takeover: now Stage J (watcher), the primary goal.
- "Keep watching" row (needs playback state; hard, maybe not possible).
- Profile switch ("Person 1 / Person 2").
- Standby/sleep button, light/dark, wallpaper rotation.

---

## App / launcher design spec (from your reference image)

Single self-contained HTML page, navigable with the TV remote's arrow keys and
OK. Layout:

- **Background:** full-screen wallpaper (swappable).
- **Top centre:** date, then a large clock.
- **Top-right:** standby / sleep button. *(not urgent)*
- **Top-left:** profile switch. *(not urgent)*
- **Middle:** "Keep watching" row. *(not urgent — depends on what's possible)*
- **Bottom dock (the core):** a row of **app tiles** (your chosen apps), then a
  **Store** tile and a **Settings** tile on the side, all clickable — exactly
  like your screenshot.
  - App tile → opens that app (method decided by Stage E).
  - Store tile → opens the VIDAA app store.
  - Settings tile → opens TV settings (if a function allows; else best effort).

Tiles light up / scale on focus as you move the remote, matching the reference
look.

---

## Current status

- [x] `01-dns-setup.md` written.
- [ ] **Next action: Stage C ping test** (GATE 1).
- [ ] Choose dock apps for Stage F.
