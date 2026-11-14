# Gate 3b/3c runbook (Stage E2, D-pad test via Appinfo.json) — APPROVED

Status: APPROVED (Architect review of gate3b/gate3c/06, fixes applied). Gate 3b
is read-only; gate 3c writes `websdk/Appinfo.json`.

Why: the legacy `Hisense_installApp` returned `0` but no tile appeared and
`Appinfo.json` read as empty (`docs/05-gate3-runbook.md`, Step 3 result).
vidaa-edge's `installAppNew` writes the app list file directly through
`HiUtils_createRequest`. 3b checks that read path; 3c tries that write, with
locks and an undo.

Gate 3 passes only if the TV remote's D-pad reaches our test tile as native key
events. A virtual cursor or no key events means STOP and full rollback
(`docs/00-project-plan.md`).

## Setup — same as `docs/05-gate3-runbook.md`

Do these exactly as written there; only the served page differs:

- **Step 0** (hotspot, re-read TV-IP / MAC-IP, photograph network info and the
  TV app row, ping gate, `curl` TEST_URL and `icon.png`, `make-cert.sh`).
- **Step 1** (dnsmasq in window A, TV DNS = MAC-IP, server in window B).

Window A (dnsmasq), exactly:
```
sudo /opt/homebrew/sbin/dnsmasq -d --listen-address=172.20.10.3 --bind-interfaces --address=/vidaahub.com/172.20.10.3 --server=1.1.1.1
```

Window B server command per step below (`PAGE_DIR` is the only change):
```
sudo PAGE_DIR=<gate3b|gate3c> python3 discovery/server.py <MAC-IP> <TV-IP>
```
It must print `serving .../discovery/<page>/index.html`. With a non-default
`PAGE_DIR` every POST is a NEW file `discovery/out/<page>-<UTC time>.json`.
Nothing is overwritten.

## Step A — gate 3b read (read-only)

**Worker:** start the server with `PAGE_DIR=gate3b`.

**You (TV remote):** Browser → `https://vidaahub.com/`. The page shows
YES/NO for "test app in `getInstalledApps`" and the `HiUtils fileRead` result.
Photograph the screen. No buttons, nothing is written.

**Worker:** `python3 -I -m json.tool` the new `discovery/out/gate3b-*.json`
files. Report to the Architect: `ret`, `msgLength`, `valid`.

**Decision:** go to Step B **only if gate3b shows NO (test app not in
`getInstalledApps`) AND the `fileRead` is either `ret: true` OR a clean
**MISSING**: `ret: false` with `msg.code === "ENOENT"` (or `msg.errno === -2`)**.
If YES: STOP, close down (Step C), report. Any other `ret: false`, or a read
that threw: also STOP, close down, report.

**Undo:** nothing changed on the TV.

## Step B — gate 3c install (writes `websdk/Appinfo.json`)

Same session if Step A said go. **You (human):** Ctrl-C window B (`server.py`,
keep dnsmasq in window A) and restart it with `PAGE_DIR=gate3c`. The Worker does
not do this. TV DNS stays on MAC-IP.

**What the page does:**
1. On load: `HiUtils_createRequest('fileRead', {path:'websdk/Appinfo.json', mode:6})`.
   `HiUtils_createRequest` may return `{ret,msg}` directly or a Promise; the page
   handles both (locks apply to the resolved value). Shows `ret`, length, parsed
   JSON. POSTs the raw text as `appinfo-backup` (`original:"MISSING"` when the
   file does not exist; see below). Also saves it in the TV
   browser's `localStorage` (so Restore still works after a reload; if
   `localStorage` is unavailable, do NOT reload).
2. **Install is locked** unless all hold (the screen shows which failed):
   a) `ret === true`, or the file is cleanly MISSING (`ret === false` and
   `msg.code === "ENOENT"` or `msg.errno === -2`; any other failure stays
   locked); b) `msg` is `""` or an object with an `AppInfo` array (MISSING
   starts as `{AppInfo:[]}`);
   c) the backup POST got HTTP 200; d) an original (not already-modified)
   backup is in hand; e) the test entry is not already in the file.
3. **Install D-pad Test** adds ONE entry (`Id vidaa-launcher-gate3`,
   `AppName/Title D-pad Test`, `URL/StartCommand` = workers.dev URL, icons =
   `.../icon.png`, `Type Browser`, `StoreType custom`, `PreInstall false`),
   keeps every other entry, writes, waits 1000 ms, re-reads, POSTs
   `appinfo-after`, and shows one big outcome:
   - **MATCH**: re-read text is exactly what was written.
   - **DIFFERENT**: re-read parses to `{AppInfo:[...]}`, contains our entry, and
     every original entry is still present (compared by `JSON.stringify`).
   - **BROKEN**: re-read failed, `ret` not true, invalid JSON, no `AppInfo`
     array, our entry missing, or an original entry missing.
   **MISSING start:** the original is "no file". The page stores
   `{"original":"MISSING"}` in `localStorage` (same key) and in the backup POST.
   Install writes `{"AppInfo":[entry]}`; MATCH/DIFFERENT/BROKEN as above (no
   original entries to keep).
4. **Restore backup** writes the saved original back byte-for-byte, waits 1000 ms,
   re-reads, POSTs `restore-result`, shows **RESTORE MATCH / MISMATCH** (exact
   text) plus a log line `parsed equal: yes/no`. After RESTORE MATCH the
   `localStorage` backup key is removed. **MISSING start:** Restore writes
   `{"AppInfo":[]}`, re-reads, and shows **RESTORE OK** if the result parses
   to an empty `AppInfo` array (else MISMATCH). The file then EXISTS but is
   empty: the page cannot delete files, so "file absent" is not restored. A thrown write or read is logged and
   never leaves the buttons stuck.
5. Only `fileRead` / `fileWrite`, only on `websdk/Appinfo.json`. No other
   function, no other file.

**You (TV remote):** Browser → `https://vidaahub.com/`. Photograph the lock
list. If all five (a-e) say OK, press **Install D-pad Test** once. Photograph the
result. Then:
- **MATCH** → continue.
- **DIFFERENT** → photograph, do NOT press Restore, STOP and report.
- **BROKEN** → press **Restore backup** at once, photograph that too, then
  STOP and report.

**Worker:** confirm the files and show them to the Architect:
```
ls discovery/out/gate3c-*.json
python3 -I -m json.tool discovery/out/gate3c-<stamp>.json
mkdir -p compatibility/backups
cp <the appinfo-backup file> compatibility/backups/appinfo-original-<TS>.json
shasum -a 256 compatibility/backups/appinfo-original-<TS>.json
```
The `raw` field of the `appinfo-backup` POST is the original file text. Keep
this copy: it is the off-TV copy of the undo.

## Step C — Close down BEFORE restarting the TV

Same as 05 Step 4: exit the Browser; TV Settings → Network → **Automatic**,
check against the Step 0 photo; Ctrl-C server and dnsmasq;
`lsof -nP -iTCP:443 -iUDP:53` shows nothing from them.

## Step D — Restart the TV and run the D-pad test (the gate)

Same as 05 Step 5: restart the TV on the Automatic network, Home → app row →
**D-pad Test**. Compare the row with the Step 0 photo; the only difference
should be our tile. Press arrows, OK, Back, Home once each and report what
you see (ring moves? OK turns a tile green? key name and keyCode per key?
any mouse-like cursor?). Exit the app.

Gate 3 decision (Architect): native key events and no virtual cursor = PASS.
Virtual cursor or no key events = STOP and run the undo below plus the full
rollback. If no tile appears at all after the restart: the write did not
register; run the undo and report.

Record key codes in `compatibility/my-tv.md`.

## UNDO

After Step D:
- **D-pad test PASSES:** keep the tile. Its removal happens in the real-launcher
  session, not here.
- **D-pad test FAILS, or no tile appears:** run Restore (below).

1. **Restore (normal):** repeat Setup (Step 0 items that apply, Step 1 in
   full) with the server on `PAGE_DIR=gate3c`. TV Browser →
   `https://vidaahub.com/` → press **Restore backup**. It must show
   **RESTORE MATCH**. Close down (Step C), restart the TV, compare the app row
   with the Step 0 photo.
   - Do NOT reload first if localStorage is unavailable; the in-page backup
     is lost on reload. After a reload with localStorage working, Restore
     uses the saved original, and the log says so.
   - If the page lost the backup entirely, STOP and ask the Architect;
     the off-TV copy in `compatibility/backups/appinfo-original-<TS>.json` is
     the source of truth.
2. **Restore says MISMATCH or fails:** stop; tell the Architect; do not retry
   with other tools. Photograph the screen.
3. **Legacy tile from gate 3:** if `Hisense_uninstallApp` cleanup of the
   legacy gate 3 install is still pending, handle per `docs/05` Step 6, not
   here.
4. **Network:** TV → Automatic; stop dnsmasq and the server.
5. **Last resort: TV factory reset.** Destructive: erases settings, accounts
   and installed apps. Only the human, from the TV's own Settings menu, and
   only after the Architect agrees.

## Risks / decisions

1. **The write is a whole-file rewrite** of the app list. The page keeps
   other entries unchanged, but re-serialises them with `JSON.stringify`
   (spacing may differ from the original; content is the same). Restore
   writes the original text byte-for-byte.
2. **`fileRead` of an empty or missing file** both look like `msg ""`; lock b
   treats `""` as empty and the original backup is then `""`. Restore of `""`
   writes an empty file: that matches the "before", not necessarily "file
   absent".
3. **Path/mode** (`websdk/Appinfo.json`, mode 6) copied from vidaa-edge; the
   discovery pages used a different read path. 3b exists to check this before
   3c writes.
4. **Entry may not render** (firmware may ignore `Appinfo.json` or cache the
   list). Then the gate is inconclusive, not failed; run the undo.
5. **`localStorage`** on the TV browser is assumed to work; the page says when
   it doesn't.
