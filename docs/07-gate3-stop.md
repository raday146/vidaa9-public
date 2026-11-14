# Gate 3 — STOP (2026-11-14)

**Decision (Architect): STOP. Full rollback.** Native D-pad launcher is not
possible on this TV's current firmware, `V0000.09.60A.Q0707`.

Two independent, each-sufficient reasons:

1. **Write path blocked.** Both app-install routes refused on this firmware:
   - Legacy `Hisense_installApp` (Gate 3, Step 3): callback `0` (reported
     success), but no tile appeared and `Appinfo.json` read back empty/ENOENT
     right after.
   - New-method write via `HiUtils_createRequest('fileWrite', ...)` on
     `websdk/Appinfo.json` (Gate 3c, Step B): refused outright, `ret:false`,
     `msg: "client request permission check error, please check appconfig"`.
     Restore attempt refused the same way. Re-read after both attempts: still
     `ENOENT` (`errno:-2`, `code:"ENOENT"`, `path:"/APPS/websdk/Appinfo.json"`).
     File never existed, never created. Nothing on the TV changed.
2. **Virtual cursor.** The TV Browser runs pages under a virtual cursor, not
   native D-pad key events. This alone fails the Gate 3 pass condition in
   `docs/00-project-plan.md` ("native D-pad or abort").

Either failure alone is a stop condition per the project's ground rules.

## What we tried, in order

| Step | What | Result |
|------|------|--------|
| Gate 2 (Stage E, discovery) | Read `websdk/Appinfo.json`, enumerate 130 TV functions | `Hisense_installApp` (arity 11, undocumented arg count), `Hisense_installApp_V2` (arity 2), `Hisense_FileRead`/`Hisense_FileWrite` present; file read as empty, no error surfaced |
| Gate 3, Step 3 (legacy install) | `Hisense_installApp(appId, appName, thumbnail, iconSmall, iconBig, appUrl, storeType, callback)`, 8 args, reference order | Callback `0`; no tile on TV; `Appinfo.json` re-read empty |
| Gate 3b (read-only) | `HiUtils_createRequest('fileRead', {path:'websdk/Appinfo.json', mode:6})` | `ret:false`, `msg {errno:-2, code:"ENOENT", syscall:"open", path:"/APPS/websdk/Appinfo.json"}` — file does not exist. Explains the "empty" reads above: empty and missing look the same through this page. |
| Gate 3c, Step B (write, MISSING-start) | `HiUtils_createRequest('fileWrite', {path:'websdk/Appinfo.json', mode:6, writedata: '{"AppInfo":[entry]}'})` | Refused: `ret:false`, `msg: "client request permission check error, please check appconfig"` |
| Gate 3c, Restore | Same call with `{"AppInfo":[]}` | Refused the same way |
| Gate 3c, final re-read (both attempts) | `fileRead` | Still `ENOENT`, byte-for-byte same error as the first read |

Raw evidence: `discovery/out/gate3-*.json`, `discovery/out/gate3b-*.json`,
`discovery/out/gate3c-*.json`.

## Why we stopped (sources)

The `"client request permission check error, please check appconfig"` string
is a known, named block on current VIDAA firmware, documented by the
community root-research project `carteakey/alvidaa` (unofficial, unverified
by Hisense — treated here as evidence, not instruction):

- Per their reports, newer VIDAA firmware checks the *client's TLS/MQTT
  identity certificate* before allowing `fileWrite`-class calls, accepting
  only the certificate the official VIDAA Smart TV mobile app carries, plus
  per-connection dynamic credentials tied to device identity and time. This
  is below the web-page layer — not something a hosted page's origin/domain
  can satisfy.
- Multiple reports on 09.60-family firmware hit the same error on
  `fileWrite`, `uninstallApp`, and device-code calls.
- One report (different model/firmware/region) describes a successful
  `websdk/Appinfo.json` write. The gate is not universal — it varies by
  firmware build, region, or model — but it blocks our exact unit on
  `V0000.09.60A.Q0707`.
- No public, non-destructive method bypasses this from a plain web page.
  Deeper workarounds that project describes (boot hooks, sandbox escapes,
  root access) are out of scope: this project's hard rules forbid
  run-arbitrary-code and anything but read/add-one-tile/remove-one-tile.

No vendor documentation exists for `Hisense_installApp_V2` (arity 2) or an
11-arg `Hisense_installApp`; both remain unknown and moot now that the write
path itself is gated.

Full citations: `carteakey/alvidaa` issues #10, PR #5, PR #41;
`carteakey.dev/blog/alvidaa/alvidaa`; `weinzii/vidaa-edge` issue #33;
`bananamafia.dev/post/hisensehax` (2021, documents the original 8-arg
`Hisense_installApp`, pre-dates this gate).

## Rollback performed

1. `rm discovery/cert.pem discovery/key.pem` — done.
2. Cloudflare Worker `vidaa-dpad-test` deleted (`npx wrangler delete
   vidaa-dpad-test`) — confirmed gone, `https://vidaa-dpad-test.raday146.workers.dev/`
   now returns `404`.
3. This document and `compatibility/my-tv.md` updated, committed.
4. Local DNS/server tools were never left running this session (no `dnsmasq`,
   no `discovery/server.py` process); still, uninstall `dnsmasq` to fully
   remove the DNS-redirect tool: `brew uninstall dnsmasq`.

Nothing was ever written to the TV. `websdk/Appinfo.json` remains exactly as
found: absent (`ENOENT`). No tile, test or otherwise, exists on the TV app
row. No further TV-side undo is needed.

## Status

**Gate 3: STOP.** Per `docs/00-project-plan.md`, Stages F–J (launcher build,
install, watcher) do not proceed on this firmware. The project's Tier 1/2
native-launcher goal is not achievable on `V0000.09.60A.Q0707` as currently
understood. Record stands for the compatibility table; a firmware update or a
different unit/region could change this result.
