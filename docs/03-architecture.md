# Architecture — three tiers

The project is split into three independent tiers. Each tier is optional on top
of the one below it, and each can be removed without affecting the others.

---

## Tier 0 — Settings clean-up guide

- **What:** a written guide to reduce ads, tracking and clutter using only the
  TV's own settings menus.
- **Who:** every VIDAA owner. No computer, no network changes.
- **Needs:** the TV remote only.
- **Undo:** change the settings back (or factory-reset the settings menu).

## Tier 1 — Core launcher + installer kit

- **Launcher:** a single web page (wallpaper, clock, dock of apps) hosted on
  **Cloudflare Pages**. Nothing runs permanently on the user's network.
- **Installer kit** (one-time use, lives in `installer/`):
  - DNS helper — temporarily points the TV at the computer during install.
  - Add / remove tile — adds our one app-list entry, or removes it.
  - Backup / restore — saves the TV's app-list file before any write and puts
    it back on request.
- **Personalisation:** users choose their apps, city (weather/clock) and look
  in the launcher's own **Home settings** screen on the TV. No rebuild or
  reinstall needed.
- **Undo:** remove the tile (tool uninstall or restore the app-list backup),
  set the TV network back to Automatic.

## Tier 2 — Watcher (optional)

- **What:** a small multi-arch Docker image (lives in `watcher/`) that opens the
  launcher tile when the TV powers on and after the Home button is pressed.
- **Runs on:** a Raspberry Pi, NAS, Home Assistant, or K3s — anything always-on
  in the home.
- **Network:** needs exactly one firewall rule: watcher host -> TV, TCP 36669
  only. No inbound ports, nothing else.
- **Certificate:** the Hisense client certificate is **never shipped** with the
  image or the repo. Each user extracts their own and mounts it into the
  container.
- **Undo:** stop and remove the container, delete the firewall rule.

---

## How the tiers relate

| Tier | Needs a computer | Always-on device | Touches the TV app list |
|------|------------------|------------------|-------------------------|
| 0 | No | No | No |
| 1 | Once, for install | No | Yes, one tile (backed up) |
| 2 | No | Yes | No |
