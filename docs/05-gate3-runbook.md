# Gate 3 runbook (Stage E2, D-pad test) — APPROVED by Architect 2026-11-14

Status: approved. Gate 3 passes only if the TV remote's D-pad reaches our page
as native key events. A virtual cursor, or no key events, means STOP and full
rollback (`docs/00-project-plan.md`, "Full rollback").

Network: iPhone Personal Hotspot only (see `compatibility/my-tv.md`).

## What the kit does

| Piece | File | Does |
|-------|------|------|
| Test tile | `launcher/gate3-test/index.html` | One self-contained page, no network. 3x2 tiles, arrows move focus, OK highlights, shows last key name + keyCode. Hosted on Cloudflare Pages. |
| Install page | `discovery/gate3/index.html` | Served by `discovery/server.py` with `PAGE_DIR=gate3`. On load calls ONLY `Hisense_getInstalledApps` and POSTs the result ("before"). Two buttons: install the test tile, remove it. Nothing else runs until a button is pressed. After a successful install (callback `0`) it also does one read-only chunked `Hisense_FileRead` of `websdk/Appinfo.json` and POSTs it. |

The server answers only the TV's IP, binds only to the Mac's hotspot
interface, and with `PAGE_DIR=gate3` writes every POST to a NEW file
`discovery/out/gate3-<UTC time>.json` (never overwrites, never touches
`result.json`). A page reload therefore adds a new file; it can't destroy the
"before" backup.

## Reference: how `tools/vidaa-edge` calls the four functions

Reference only. Nothing under `tools/` is run. Paths are relative to
`tools/vidaa-edge/`.

### `Hisense_installApp` (TV firmware arity: **11**)

Call site: `src/app/services/app-management.service.ts:79-101`
(`installAppLegacy`, signature at `:60-68`, doc at `:50-58`). Declared at
`src/global.d.ts:25`. Same order in `README.md:151`.

| # | Arg | Meaning (service.ts doc `:52-58`) | Value the reference passes |
|---|-----|-----------------------------------|----------------------------|
| 1 | `appId` | unique app ID | free text from the form (`installer.component.ts:192`) |
| 2 | `appName` | app name | form text |
| 3 | `thumbnail` | thumbnail URL | `iconUrl`, default `/favicon.ico` (`installer.component.ts:13,157`) |
| 4 | `iconSmall` | small icon URL | same `iconUrl` |
| 5 | `iconBig` | big icon URL | same `iconUrl` |
| 6 | `appUrl` | URL the tile opens | form text |
| 7 | `storeType` | store type | literal `'store'` (`installer.component.ts:198,209`) |
| 8 | `callback(res: number)` | `res === 0` = success, anything else = failure (`app-management.service.ts:88-99`) | |

Return value is `void` (`global.d.ts:25`); the reference ignores it.

**Mismatch:** the reference passes 8 arguments; the TV reports `fn.length`
11 (Gate 2). We don't know what args 9-11 are. See "Risks".

### `Hisense_installApp_V2` (TV arity: 2)

**No call site in `tools/`.** The only mention is a name in a comment list,
`src/global.d.ts:34`, headed "List of all available Hisense functions"
(`:31`, source given as `vidaa.service.ts: getAvailableHisenseFunctions()`;
that file does not exist in the copy). No argument information at all.
We do **not** call it.

### `Hisense_uninstallApp` (TV arity: 2, matches the reference)

Call site: `app-management.service.ts:299-312` (`uninstallAppLegacy`, `:287`).
Declared at `global.d.ts:26`.

| # | Arg | Meaning |
|---|-----|---------|
| 1 | `appId` | the same ID used at install |
| 2 | `callback(status: boolean)` | truthy = success (`app-management.service.ts:300-311`) |

Called from `installer.component.ts:260,263`.

### `Hisense_getInstalledApps` (TV arity: 1)

**No call site in `tools/`.** Only a name in the comment list,
`global.d.ts:37`. The reference has no declaration, no argument list and no
return type. Arity 1 suggests one callback, so our page passes one callback
and also logs the synchronous return value. This is a guess, flagged below.

### What the reference does instead (not used by us)

`installAppNew` / `uninstallAppNew` (`app-management.service.ts:121-201`,
`:210-279`) read and rewrite `websdk/Appinfo.json` through
`HiUtils_createRequest('fileRead' | 'fileWrite', {path, mode: 6, writedata})`
(`:138-141`, `:175-179`, constants `:26-28`). That is a direct write to the
app-list file. Our pages never call `HiUtils_createRequest` or
`Hisense_FileWrite`.

## Values (re-confirm every session, Step 0)

| Name | Where | Value |
|------|-------|-------|
| TV-IP | TV network info on the hotspot | 172.20.10.2 (last known) |
| MAC-IP | `ipconfig getifaddr en0` on the hotspot | 172.20.10.3 (last known) |
| TS | `date -u +%Y%m%dT%H%M%SZ` | fill in on the day |
| TEST_URL | Cloudflare deploy of `launcher/gate3-test/` (project `vidaa-dpad-test`) | `https://vidaa-dpad-test.raday146.workers.dev/` (set in `discovery/gate3/index.html`) |
| TEST_APP_ID | constant in `discovery/gate3/index.html` | `vidaa-launcher-gate3` |

The hotspot may hand out different addresses each session; Step 0 re-reads both.

## Step 0 — Preconditions and manual backup

**You do (TV remote):**
1. Hotspot on, TV on the hotspot (Automatic). Photograph Settings → Network →
   Network information (restore point for DNS).
2. **Photograph the TV app row** (Home screen, every tile visible). This is
   the manual backup of the app list. If the row scrolls, take more than one
   photo so every tile is covered.

**Worker does (Mac):**
1. Join the hotspot; `ipconfig getifaddr en0` → MAC-IP. `ping -c 3 <TV-IP>`
   must reply, otherwise STOP.
2. `curl -sIL <TEST_URL>index.html` ends in 200 (Cloudflare answers 307 to `/` first) and `curl -sI <TEST_URL>icon.png` is 200.
3. `./discovery/make-cert.sh` (fresh self-signed cert, 30 days, never committed).

**Undo:** nothing changed on the TV. `rm -f discovery/cert.pem discovery/key.pem`.

## Step 1 — Session setup: DNS redirect and server

(Repeated for removal, see Step 6.)

**Worker does (Mac), window A:**
```
sudo dnsmasq -d --address=/vidaahub.com/<MAC-IP> --server=1.1.1.1
```
Check: `dig @<MAC-IP> vidaahub.com +short` prints MAC-IP and
`dig @<MAC-IP> example.com +short` prints a real address.

**You do (TV remote):** Settings → Network → Manual; keep IP, gateway and
subnet as photographed; DNS = MAC-IP; save.

**Worker does (Mac), window B:**
```
sudo PAGE_DIR=gate3 python3 discovery/server.py <MAC-IP> <TV-IP>
```
It must print `serving .../discovery/gate3/index.html`.

**Undo:** Ctrl-C both windows; TV network back to Automatic.

## Step 2 — "Before" snapshot (read-only)

**You do (TV remote):** TV Browser → exactly `https://vidaahub.com/`. If a
certificate warning appears, note its text and STOP for the Architect. Do not
press either button yet. Photograph the log (`Hisense_getInstalledApps`
return value, callback value, `POST /result -> 200`).

**Worker does (Mac):**
```
ls discovery/out/gate3-*.json
python3 -I -m json.tool discovery/out/gate3-<stamp>.json
mkdir -p compatibility/backups
cp discovery/out/gate3-<stamp>.json compatibility/backups/installed-apps-before-<TS>.json
shasum -a 256 compatibility/backups/installed-apps-before-<TS>.json
```
Show the Architect the file. The snapshot may be empty or in an unknown
format (Risks #3); the app-row photo from Step 0 is the backup that counts.

**Undo:** `rm` the copied file. Nothing on the TV changed.

## Step 3 — Install the test tile

**You do (TV remote):** press **Install test tile** once. Photograph the log.
On success (callback `0`) the page then calls `Hisense_FileRead` on
`websdk/Appinfo.json` (read-only, same chunked read as discovery) and POSTs
it, so we see how the tile was recorded. If the callback is not `0`, nothing
is read; do not press it again, stop and report.

**Worker does (Mac):** confirm two new files: `gate3-*.json` with
`"kind":"install-result"` and (on success) `"kind":"appinfo-after-install"`.
```
python3 -I -m json.tool discovery/out/gate3-<stamp>.json
```
Show the Architect the `appinfo` content (does it contain our entry, what do
the fields look like).

**Undo:** Step 6 (Remove).

## Step 4 — Close down BEFORE restarting the TV

The restart must not depend on the Mac.

**You do (TV remote):**
1. Exit the Browser.
2. Settings → Network → **Automatic**; check against the Step 0 photo (DNS
   back to the router/hotspot value).

**Worker does (Mac):**
1. Ctrl-C the `server.py` window, then the dnsmasq window.
2. `lsof -nP -iTCP:443 -iUDP:53` shows nothing from these tools.
3. Optionally `rm -f discovery/cert.pem discovery/key.pem`.

Only when both sides are done:

## Step 5 — Restart the TV and run the D-pad test (the gate)

**You do (TV remote):**
1. Restart the TV (power off/on). It is on Automatic network now.
2. Home → app row → open **D-pad Test** (the tile loads from Cloudflare over
   the hotspot; Mac not involved). Compare the app row with the Step 0 photo:
   the only difference should be our tile.
3. Press arrows, OK, Back, Home once each. Say what you see: does a ring move
   between tiles, does OK turn a tile green, what does the bottom line show
   (key name and keyCode) for each key, and does a mouse-like cursor appear.
4. Exit the app.

**Gate 3 decision (Architect):**
- Native key events arrive (ring moves, key codes shown) and no virtual
  cursor: **PASS**.
- Virtual cursor appears, or no key events: **STOP**, run Step 6 and the full
  rollback.
Record the key codes (Back, Home if they show) in `compatibility/my-tv.md`.

## Step 6 — Remove the test tile (ALWAYS, pass or fail)

Removal repeats the session setup:

1. **Worker + You:** Step 0 items that apply (hotspot, addresses, cert; no new
   photos needed) and **Step 1 in full** (dnsmasq, TV DNS to MAC-IP, server
   with `PAGE_DIR=gate3`).
2. **You (TV remote):** Browser → `https://vidaahub.com/` → press **Remove
   test tile**. Photograph the log (callback should be `true`).
3. **You:** reload the page ("after" read; `getInstalledApps` runs again).
4. **Worker (Mac):** compare the newest `discovery/out/gate3-*.json` with the
   "before" file; report both stamps and any difference.
5. **Close down** exactly as Step 4 (Browser exit, TV DNS Automatic, stop
   server and dnsmasq, `lsof`). Then restart the TV if the tile is still
   shown, and compare the app row with the Step 0 photo.

## UNDO

1. **Normal:** Step 6 (Remove test tile), confirmed by the reload and the app
   row compared with the Step 0 photo.
2. **Button reports failure or no callback:** stop and tell the Architect. Do
   not improvise: no `tools/vidaa-edge`, no `HiUtils_createRequest`, no
   `Hisense_FileWrite`.
3. **Network:** TV → Automatic; stop dnsmasq and the server.
4. **Last resort: TV factory reset.** Destructive: erases TV settings,
   accounts and installed apps; only the human may do it, from the TV's own
   Settings menu, and only after the Architect agrees.

## Risks / decisions

1. **Arity mismatch (ACCEPTED by the Architect 2026-11-14):** the reference
   passes 8 args to `Hisense_installApp`, the TV function declares 11.
   Missing args arrive as `undefined`. Effect unknown (could fail, could
   record a broken entry). We copy the reference exactly rather than guess
   args 9-11.
2. **`getInstalledApps` argument is a guess** (one callback, from arity 1);
   no reference call site. A getter by name, but untested.
3. **No Appinfo.json backup exists** (Gate 2 read it as empty; the page can't
   tell empty from missing). The manual backup is the Step 0 app-row photo;
   the `getInstalledApps` snapshot is a bonus and may be empty.
4. `Hisense_installApp_V2` is not used: no reference exists for it.
5. **Icon:** `launcher/gate3-test/icon.png` (512x512, hosted next to the
   tile). The page passes `TEST_URL + "icon.png"` for thumbnail and both
   icons.
6. **App ID:** `vidaa-launcher-gate3` is a free-text guess; the reference
   doesn't say what IDs the TV accepts.
7. **Uninstall callback only says true/false.** Verify by the reload and the
   app row.
8. **Back/Home** may be intercepted by the TV and never reach the page; then
   we get no code for them (not a Gate 3 failure by itself).
