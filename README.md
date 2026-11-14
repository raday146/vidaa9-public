# vidaa-launcher

**Status: STOPPED.** Native D-pad install is not possible on firmware
`V0000.09.60A.Q0707` — both app-install paths are refused by a firmware-side
permission gate, and the TV Browser runs under a virtual cursor rather than
native key events either way. Full findings, evidence and sources:
[docs/07-gate3-stop.md](docs/07-gate3-stop.md).

**What's reusable:**
- `launcher/web/` — the couch-tv home-screen UI (vendored, see
  [launcher/UPSTREAM.md](launcher/UPSTREAM.md)) and our config/app-list layer
  on top of it. Works as a page; only the TV-side install step is blocked.
- `discovery/` — the discovery/install test kit (function explorer, gate3
  test pages, DNS-redirect + HTTPS server setup) for probing what a given
  VIDAA firmware actually allows, read-only and reversible.
- `compatibility/` — per-device/firmware compatibility notes and the raw
  discovery output format, so results across firmware versions are
  comparable.

**Contributions from other firmware versions, models, or regions are
welcome** — if install works on your TV, or fails differently, a
compatibility report (even a short one) is useful.

A minimal, Apple-style home-screen launcher for Hisense VIDAA 9 TVs, installed
through VIDAA's own app-list mechanism, with no always-on server and every
change reversible. See the full roadmap in
[docs/00-project-plan.md](docs/00-project-plan.md).

## Three tiers

See [docs/03-architecture.md](docs/03-architecture.md).

- **Tier 0 — Settings clean-up:** a guide to cut ads, tracking and clutter
  using only the TV's own settings. Remote only; for every VIDAA owner.
- **Tier 1 — Core launcher:** a launcher page on Cloudflare Pages plus a
  one-time installer kit (DNS helper, add/remove tile, backup/restore).
  Personalise apps, city and look in the launcher's Home settings on the TV.
- **Tier 2 — Watcher (optional):** a small multi-arch Docker image that opens
  the launcher on TV power-on and after Home. Runs on a Pi, NAS, Home
  Assistant or K3s; needs one firewall rule (host -> TV, TCP 36669).

**Status:** STOPPED on `V0000.09.60A.Q0707` (see top of this file).
