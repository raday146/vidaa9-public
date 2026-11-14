# My TV

## Device

| Field | Value |
|-------|-------|
| Firmware | V0000.09.60A.Q0707 (VIDAA 9) |
| Network mode | DHCP |
| TV IP | <TV-IP> |
| Netmask | 255.255.255.0 |
| Gateway | <ROUTER-IP> |
| DNS | <ROUTER-IP> |

## Gate 1 — network reachability (2026-11-14)

Read-only checks from the Mac (<MAC-IP>, en0, same subnet).

| Check | Result |
|-------|--------|
| PING | no replies (5/5 lost, "No route to host") |
| TCP 36669 | closed (no route to host) |
| TCP 9226 | closed (no route to host) |
| ARP for TV IP | incomplete (TV never answered ARP; gateway did) |

**Gate 1: FAIL (first attempt).** "No route to host" on the same subnet means
the TV did not answer ARP. Likely causes: TV off or in deep standby, TV IP has
changed, or the Wi-Fi isolates clients from each other. Re-test with the TV on
and its IP re-confirmed before concluding the network isolates devices.

## Gate 1 — second attempt (2026-11-14)

Same read-only checks, TV IP <TV-IP>.

| Check | Result |
|-------|--------|
| PING | no replies (5/5 lost, "No route to host") |
| TCP 36669 | closed (no route to host) |
| TCP 9226 | closed (no route to host) |
| ARP for TV IP | incomplete |

**Gate 1: FAIL (second attempt).** Identical to the first attempt: the TV
does not answer ARP at <TV-IP>.

## Gate 1 — third attempt, via iPhone hotspot (2026-11-14)

Mac and TV both joined an iPhone Personal Hotspot instead of the home router.

| Field | Value |
|-------|-------|
| TV IP (hotspot) | 172.20.10.2 |

| Check | Result |
|-------|--------|
| PING | replies OK |
| TCP 36669 | open |
| TCP 9226 | refused |

**Gate 1: PASSED (2026-11-14, via iPhone hotspot).**

Root cause of the earlier failures: the ISP router (Partner) silently isolates
Wi-Fi clients from each other, so the TV never answered ARP on the home
network. Until a new router replaces it, all TV work runs over the iPhone
hotspot. The permanent setup (including the Stage J watcher) waits for the new
router.

## Gate 2 — discovery (2026-11-14, via iPhone hotspot)

**Gate 2: PASS (2026-11-14).** Stage E ran; page POSTed `/result` -> 200.
No TV function was called other than the page's read-only enumeration,
`Hisense_GetFirmWareVersion` and one `Hisense_FileRead` of Appinfo.json.

| Field | Value |
|-------|-------|
| Firmware | V0000.09.60A.Q0707 |
| Functions exposed | 130 (names + arity in `compatibility/discovery/functions-20261114T140249Z.json`) |
| Install fn present | true (`Hisense_installApp`, arity 11; `Hisense_installApp_V2`, arity 2) |
| FileRead fn present | true (`Hisense_FileRead`, arity 2) |
| "Launch" flag | true, but only because the page's name regex matched `app`/`start`; no function named launch/run/open exists |
| Appinfo.json | read returned empty (`content: ""`, `length: 0`, no error); no backup taken |

Note: the page cannot tell a missing file from an empty one; it treats `""`,
`null` and `undefined` from `Hisense_FileRead` alike. `Hisense_FileWrite`
also exists (not called).

## Gate 3 — install session (2026-11-14, via iPhone hotspot)

| Item | Result |
|------|--------|
| "Before" snapshot (`Hisense_getInstalledApps`) | 57 apps, all `from: "preset"`; saved as `compatibility/backups/installed-apps-before-20261114T142940Z.json`, SHA-256 `f9d9962f75649b30f1c6f661c3f922222a9b0fecec3bc09c8b74321cca07d84b` |
| `Hisense_installApp` (8 args, reference order) | callback `0` at 2026-11-14 14:30:53 UTC (16:30:53 local); sync return null |
| `Appinfo.json` read right after the install | still empty (`content: ""`, length 0); the page can't tell empty from missing |
| Tile visible on TV right after install | no (restart pending, per the reference installer) |

Session closed down on the Mac: server and dnsmasq stopped, `lsof` shows nothing
listening on TCP 443 / UDP 53. D-pad test (Step 5) and tile removal (Step 6) not
done yet.

## Gate 3c — Appinfo.json write via HiUtils (2026-11-14, via iPhone hotspot)

| Item | Result |
|------|--------|
| gate3b read of `websdk/Appinfo.json` | `ret:false`, `msg {errno:-2, code:"ENOENT", syscall:"open", path:"/APPS/websdk/Appinfo.json"}`, sdkVersion 1.5.0: the file does not exist (this also explains the empty reads in Gate 2/3) |
| gate3c start state | MISSING (backup POST `original:"MISSING"`) |
| `HiUtils_createRequest('fileWrite')` (install) | refused: `ret:false`, msg "client request permission check error, please check appconfig" (msg text from the on-screen log, human-reported; not in the POST) |
| Restore (write `{"AppInfo":[]}`) | refused the same way |
| Last re-read after install and after restore | still ENOENT (`gate3c-20261114T154717538853Z.json`, `gate3c-20261114T154726546276Z.json`: `readRet:false`, same ENOENT msg). File was never created; nothing on the TV changed. |

Verdicts recorded by the page: install `BROKEN`, restore `match:false`. Both are
refusals, not damage. No undo needed.

## Gate 3 — STOP (2026-11-14)

**Gate 3: STOP (Architect decision).** Native D-pad launcher not possible on
this firmware. Two independent stop conditions: (1) both install/write paths
refused — legacy `Hisense_installApp` callback `0` but no tile and empty
re-read; `HiUtils_createRequest('fileWrite')` on `websdk/Appinfo.json`
outright refused, `"client request permission check error, please check
appconfig"`, file stays ENOENT; (2) TV Browser runs under a virtual cursor,
not native D-pad key events. Full detail, evidence and sources:
`docs/07-gate3-stop.md`.

Rollback done: `discovery/cert.pem`/`key.pem` removed; Cloudflare Worker
`vidaa-dpad-test` deleted and confirmed 404. Nothing was ever written to the
TV; `websdk/Appinfo.json` remains absent. No TV-side undo needed.
