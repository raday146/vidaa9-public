# Upstream

Vendored from couch-tv's TV home, unmodified.

- Source: https://github.com/Seagey/couch-tv
- Commit: fd568c03ce3f3fbb33b801025110e511f258f00b
- Vendored: 2026-11-14
- License: MIT License, (c) 2026 Seagey (see `LICENSE-couch-tv`)

Copied paths:

- `tv-home/web/` -> `launcher/web/`
- `remote/src/app-logos/` -> `remote/src/app-logos/`

## Changes from upstream

Added (ours):

- `launcher/web/config.js`: our `window.COUCH_CONFIG`, using couch-tv's own settings: no people (no profile switcher), `home.keep_watching: false`, `home.dock_size: 11`, `home.now_playing: false`, and `home.lighter` when the address has `lighter=1`. Sets `window.COUCH_STANDALONE` (couch-tv's no-bridge mode). `index.html` already loaded `config.js`.
- `launcher/web/vidaa-apps.js`: `window.VIDAA`, holding our 11 dock apps and the 8 More-menu entries (each with id, label, icon and an empty url), icon lookup, and the OK handler. Until a url is set, OK shows "<label> is not connected yet". The launch method is still a TODO.

Changed (couch-tv files; every changed line is marked `vidaa-launcher:`):

- `launcher/web/index.html`: one line loads `vidaa-apps.js`.
- `launcher/web/app.js`:
  - reads the app list from `window.VIDAA`, keeping our order (no bridge, no mock);
  - takes icons from `window.VIDAA.icon`, so apps with no logo use couch-tv's built-in name tile;
  - our apps are never tucked behind More (upstream tucks Spotify and anything named "Browser");
  - `home.dock_size` can be up to 11 (upstream: 10), and the Night dock is 13 columns wide (11 apps, Settings and More) instead of 12;
  - More opens our menu in couch-tv's existing hold-OK popup instead of expanding the app grid;
  - OK on one of our apps or More-menu entries shows the note from `window.VIDAA.open` instead of calling a bridge.

No Keep watching or profile code was deleted; both are switched off by configuration.
