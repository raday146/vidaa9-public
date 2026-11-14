# Discovery runbook (Stage E, GATE 2) — APPROVED by Architect 2026-11-14

Status: draft by the Worker. Do not run any step until the Architect approves
this file. This runbook drives **our own** read-only kit under `discovery/`,
not `tools/vidaa-edge` (which stays as read-only reference only).

Network: iPhone Personal Hotspot only (the Partner ISP router isolates Wi-Fi
clients; see `compatibility/my-tv.md`).

## What the kit does

The TV browser opens `https://vidaahub.com/` (redirected by DNS to the Mac).
The Mac serves one static page (`discovery/page/index.html`) that runs ONLY:

- `Hisense_GetFirmWareVersion()` (read-only),
- a name/arity scan of `window` properties matching
  `/^(Hisense|HiUtils|vowOS|omi|vidaa)/i` — records each NAME and argument
  count only, never the function source, never calling them,
- `Hisense_FileRead("websdk/Appinfo.json", offset)` in chunks (read-only),

then shows a short on-screen summary and POSTs the full result to the Mac,
which writes it to `discovery/out/result.json` (one file, fixed name).

The page never calls `Hisense_installApp`, `HiUtils_createRequest`, or anything
whose name contains Write/reset/DNS/setting; it runs no `eval` and no code
fetched from the network. The server accepts requests only from the TV's IP and
binds only to the Mac's hotspot interface.

## Values used below (re-confirm every session — Step 0)

| Name | Where to get it | Last known |
|------|-----------------|------------|
| TV-IP | TV network info on the hotspot | 172.20.10.2 (Gate 1) |
| MAC-IP | Mac: `ipconfig getifaddr en0` on the hotspot | fill in on the day |
| TS | `date +%Y%m%dT%H%M%S` | fill in on the day |

The hotspot may hand out different addresses each session, so Step 0 re-reads
both and the rest of the runbook uses those values.

---

## Step 0 — Re-confirm addresses on the hotspot

**You do (TV remote):**
1. Turn on iPhone Personal Hotspot; make sure no other device is joined.
2. Connect the TV to the hotspot (connection mode Automatic).
3. Settings → Network → Network information: **photograph the screen** (IP,
   gateway, subnet, DNS). This photo is the restore point for DNS later.
   Record TV-IP.

**Worker does (Mac):**
1. Join the same hotspot.
2. `ipconfig getifaddr en0` → record MAC-IP.
3. `ping -c 3 <TV-IP>` → must reply (repeat of Gate 1). No reply = STOP.

**Undo:** disconnect both from the hotspot. Nothing changed on either device.

## Step 1 — Make a fresh certificate (Mac)

**Worker does (Mac):**
```
cd discovery
./make-cert.sh
```
Writes `discovery/cert.pem` and `discovery/key.pem` (CN=vidaahub.com, 30-day,
self-signed, never committed).

**Undo:** `rm -f discovery/cert.pem discovery/key.pem`.

## Step 2 — DNS redirect (from `01-dns-setup.md`)

Points `vidaahub.com` at the Mac so the TV loads our page. This is the TV's own
network DNS setting, not any tool "DNS-set" feature.

**Worker does (Mac):** in its own terminal window, following
`docs/01-dns-setup.md` Part 4 with hotspot values:
```
sudo dnsmasq -d --address=/vidaahub.com/<MAC-IP> --server=1.1.1.1
```
Check: `dig @<MAC-IP> vidaahub.com +short` prints MAC-IP, and
`dig @<MAC-IP> example.com +short` prints a real address.

**You do (TV remote):** following `01-dns-setup.md` Part 5:
1. Settings → Network → switch to Manual.
2. Keep IP, gateway and subnet exactly as photographed in Step 0.
3. Set DNS to MAC-IP. Save.

**Undo:**
1. TV: Settings → Network → back to Automatic (check against the Step 0 photo).
2. Mac: Ctrl-C the dnsmasq window.

## Step 3 — Start the discovery server (Mac)

**Worker does (Mac):** in a second terminal window:
```
sudo python3 discovery/server.py <MAC-IP> <TV-IP>
```
(`sudo` only because port 443 is privileged; the server is read-only and
answers only TV-IP.) Leave it open; it prints every request.

Check on the Mac only: `curl -k https://localhost/` fails to connect (the server
binds MAC-IP, not localhost) — that is expected; do not loosen the bind.

**Undo:** Ctrl-C in that window. Confirm: `lsof -nP -iTCP:443 -sTCP:LISTEN`
prints nothing.

## Step 4 — Open the page on the TV

**You do (TV remote):**
1. Open the TV's Browser app.
2. Go to exactly `https://vidaahub.com/`.
3. If a certificate warning appears, note its exact text and stop for the
   Architect. Do not change any TV security setting to get past it.
4. The page shows "VIDAA discovery — read-only" and within a couple of seconds
   a summary (Firmware; Functions found; Install/Launch/FileRead fn exists;
   Appinfo.json length). Read the summary aloud / photograph it. Do not press
   anything else on the TV.

**Worker does (Mac):** confirm the server window logged
`wrote .../discovery/out/result.json` and:
```
python3 -I -m json.tool discovery/out/result.json > /dev/null && echo valid
```

**Undo:** close the TV Browser (Exit / Home) — that stops the page. On the Mac,
`discovery/out/result.json` is gitignored; `rm` it to undo.

## Step 5 — Save the evidence into the repo (Mac)

`result.json` lives in the gitignored `out/`. Keep a trimmed, committable copy —
names and arities only, no function source (the scan never captured source, but
this is the file we actually commit):

**Worker does (Mac):**
```
mkdir -p compatibility/discovery
TS=$(date +%Y%m%dT%H%M%S)
python3 -I - <<'PY' > compatibility/discovery/functions-$TS.json
import json
d = json.load(open("discovery/out/result.json"))
print(json.dumps({
    "collectedAt": d.get("collectedAt"),
    "firmware": d.get("firmware"),
    "functionCount": d.get("functionCount"),
    "functions": d.get("functions"),
    "has": d.get("has"),
    "appinfoLength": (d.get("appinfo") or {}).get("length"),
    "appinfoValid": (d.get("appinfo") or {}).get("valid"),
}, indent=2))
PY
```
If `appinfo` came back non-empty, also back it up (it is the restore point for
later stages — never edit it):
```
python3 -I -c 'import json;print(json.load(open("discovery/out/result.json"))["appinfo"]["content"])' \
  > compatibility/backups/Appinfo-$TS.json
shasum -a 256 compatibility/backups/Appinfo-$TS.json
```
Record the firmware, function count, the three `has` flags, the Appinfo length
and SHA-256 in `compatibility/my-tv.md`.

**Undo:** delete the new files under `compatibility/`.

## Step 6 — Close down (ALWAYS run, even after a STOP)

**You do (TV remote):**
1. Exit the TV Browser.
2. Settings → Network → Automatic (check against the Step 0 photo).

**Worker does (Mac):**
1. Ctrl-C the `server.py` window.
2. Ctrl-C the dnsmasq window.
3. `lsof -nP -iTCP:443 -iUDP:53` prints nothing from these tools.
4. Optionally `rm -f discovery/cert.pem discovery/key.pem`.
5. `git status`: only intended new files under `compatibility/` are present
   (`discovery/out/`, `*.pem`, `*.key` are gitignored).

**Undo:** this step is the undo.

## Gate 2 decision (Architect)

The Worker reports: firmware, function count, the three `has` flags, the
`compatibility/discovery/functions-*.json` path, and (if present) the Appinfo
backup path + SHA-256. The Architect decides GATE 2. Nothing beyond Step 6 runs
from this runbook.
