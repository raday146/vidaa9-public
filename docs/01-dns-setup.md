# Step-by-step: DNS redirect for the VIDAA launcher setup

This guide is written for **everyone** — you do not need to be a developer.
Where a step needs a terminal, the exact command is given and explained.

This DNS redirect is only needed **during setup**, and you undo it at the end
(see Part 6). Nothing here changes your TV's software or your home network
permanently.

---

## Part 0 — What this does, in plain words

VIDAA TVs only give their hidden "install an app" powers to web pages that
appear to come from Hisense's own address, **`vidaahub.com`**. We cannot change
that rule.

Instead, we tell the TV a small white lie: that `vidaahub.com` lives on **your
own computer**, just for the setup. The setup tool's page then loads from your
computer, but the TV trusts it as if it were Hisense.

The mechanism is called a **DNS override**.

### What is DNS? (skip if you know)
DNS is the internet's phone book. When any device wants to reach `vidaahub.com`,
it asks a DNS server, "what's the number (IP address) for this name?" We are
going to run our own little phone book that answers that one name with your
computer's address, and passes every other name through untouched.

### The job has TWO halves — you need both
1. **On the computer:** run a tiny DNS server that answers
   `vidaahub.com` -> *your computer's address*, and forwards everything else to
   a normal DNS server so the TV's other apps keep working.
2. **On the TV:** set the TV's DNS to *your computer's address*, so the TV
   actually asks your computer.

Half 1 provides the answer. Half 2 makes the TV listen. One without the other
does nothing.

---

## Part 1 — Before you start (checklist)

- [ ] The computer and the TV are on the **same Wi-Fi network**.
- [ ] You can keep the computer **awake** for the whole setup (30–60 min).
- [ ] You have the computer's Wi-Fi **IP address** (Part 2).
- [ ] The computer and TV can actually **see each other** (Part 3 ping test).

---

## Part 2 — Find your computer's IP address

You will reuse this number several times. Call it **COMPUTER-IP**
(it looks like `192.168.1.42`).

**macOS**
- Click the Apple menu -> System Settings -> Wi-Fi -> Details (next to your
  network) -> the "IP address" line.
- Or, in the Terminal app:
  ```
  ipconfig getifaddr en0
  ```
  (If that prints nothing, try `en1` instead of `en0`.)

**Windows**
- Settings -> Network & Internet -> Wi-Fi -> Hardware properties -> "IPv4
  address".
- Or, in Command Prompt: `ipconfig` and read the "IPv4 Address" line.

**Write it down:** COMPUTER-IP = ____________________

---

## Part 3 — Confirm the computer and TV can see each other

Some Wi-Fi networks (especially "guest" networks) block devices from talking to
each other. If yours does, this method cannot work on that network, so test it
now before doing anything else.

1. On the TV: Settings -> Network (or Network -> Advanced) and note the TV's IP
   address. Call it **TV-IP**.
2. On the computer, in a terminal/command prompt:
   ```
   ping TV-IP
   ```
   (replace `TV-IP` with the real number)

- **Replies coming back** = good, the two can see each other. Continue.
- **"Request timed out" / no reply** = this network isolates devices. Stop here;
  this approach needs a network without that restriction.

---

## Part 4 — Run the DNS server on the computer (Half 1)

You will keep this running in a terminal window during setup, and simply close
it when done. No permanent install, no config files to clean up.

### macOS / Linux

1. Install `dnsmasq` (a tiny, standard DNS tool). On macOS with Homebrew:
   ```
   brew install dnsmasq
   ```
   (Linux: `sudo apt install dnsmasq` or your distro's equivalent.)

2. Run it **in the foreground**, replacing `COMPUTER-IP` with your number:
   ```
   sudo dnsmasq -d \
     --address=/vidaahub.com/COMPUTER-IP \
     --server=1.1.1.1
   ```
   What each part means:
   - `-d` — run in this window so you can watch it and stop it with **Ctrl-C**.
   - `--address=/vidaahub.com/COMPUTER-IP` — the one white lie: this name points
     to your computer.
   - `--server=1.1.1.1` — forward every *other* name to a real DNS server
     (Cloudflare), so the TV's normal apps and updates keep working.

3. Leave this window open. When you see it waiting (no errors), Half 1 is live.
   - If it says the port is in use, another DNS tool is already running; stop
     that one first, or ask and we'll adjust.

### Windows
Windows has no built-in equivalent, so use a small free tool such as **Acrylic
DNS Proxy**: install it, add the single line
`vidaahub.com COMPUTER-IP` to its hosts file, and start the service. (Full
Windows steps can be added to the repo later.)

---

## Part 5 — Point the TV at the computer (Half 2)

Menu names vary a little between VIDAA versions; the shape is the same.

1. On the TV: Settings -> Network (or Network -> Advanced / Network
   Configuration).
2. Switch the connection from **Automatic** to **Manual**.
3. The TV may now ask for several numbers. Fill them in like this:
   - **IP address:** the TV-IP you already noted (keep it the same).
   - **Gateway / Subnet:** leave as shown, or copy what it displayed in
     Automatic mode.
   - **DNS / Preferred DNS:** enter **COMPUTER-IP**. This is the only value that
     really changes.
4. Save / apply.

> Tip: if the TV refuses to keep its internet connection after this, double-check
> the IP, gateway and subnet match what it showed in Automatic mode — only DNS
> should differ.

---

## Part 6 — Undo (do this when setup is finished)

The redirect is only needed while installing. To return everything to normal:

1. **On the TV:** Settings -> Network -> set the connection back to
   **Automatic** (DHCP). This removes the custom DNS.
2. **On the computer:** go to the terminal running `dnsmasq` and press
   **Ctrl-C**. The little phone book stops. (On Windows, stop/uninstall the
   Acrylic service.)

That's it. The TV resolves names normally again, and your computer is back to
how it was. Nothing was installed on the TV by this DNS step itself — that
happens in the next guide.

---

## Quick reference

| Thing | Where | Value |
|------|-------|-------|
| COMPUTER-IP | your computer (Part 2) | e.g. 192.168.1.42 |
| TV-IP | TV network settings (Part 3) | e.g. 192.168.1.50 |
| DNS override | computer runs dnsmasq (Part 4) | vidaahub.com -> COMPUTER-IP |
| TV DNS setting | TV network settings (Part 5) | set to COMPUTER-IP |
| Undo | TV back to Automatic + Ctrl-C dnsmasq (Part 6) | — |
