#!/usr/bin/env python3
"""Tiny read-only discovery server.

Serves discovery/page/index.html over HTTPS on :443 and accepts exactly ONE
POST to /result, writing discovery/out/result.json (client-supplied names are
ignored). Binds to the given interface only and answers only the TV's IP.

    sudo python3 discovery/server.py <BIND_IP> <TV_IP> [cert.pem] [key.pem]

<BIND_IP>  the Mac's hotspot address (e.g. 172.20.10.3)
<TV_IP>    the TV's hotspot address (e.g. 172.20.10.2)
cert/key   default to discovery/cert.pem and discovery/key.pem (make-cert.sh)

Set PAGE_DIR=gate3 to serve discovery/gate3/index.html instead. POSTs then go
to out/gate3-<UTC timestamp>.json, created exclusively, so a repeat POST can
never overwrite an earlier one (e.g. the "before" backup) or result.json.

Everything is stdlib. Stop with Ctrl-C.
"""
import http.server
import os
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE_DIR = os.environ.get("PAGE_DIR", "page")
PAGE = HERE / PAGE_DIR / "index.html"
MAX_BODY = 8 * 1024 * 1024  # reject absurd uploads


def out_path(page_dir, now):
    """Fixed name for the default page; unique timestamped name otherwise."""
    if page_dir == "page":
        return HERE / "out" / "result.json"
    return HERE / "out" / ("%s-%s.json" % (page_dir, now.strftime("%Y%m%dT%H%M%S%fZ")))


def make_handler(tv_ip):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "discovery/1"

        def _denied(self):
            # Only the TV may talk to us, even though we also bind to one iface.
            if self.client_address[0] != tv_ip:
                self.send_error(403, "forbidden")
                return True
            return False

        def do_GET(self):
            if self._denied():
                return
            try:
                body = PAGE.read_bytes()
            except OSError as e:
                self.send_error(500, str(e))
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self._denied():
                return
            if self.path != "/result":
                self.send_error(404, "post to /result only")
                return
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > MAX_BODY:
                self.send_error(400, "bad length")
                return
            data = self.rfile.read(length)
            # Fixed output path; the client cannot choose the filename.
            out = out_path(PAGE_DIR, datetime.now(timezone.utc))
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "wb" if PAGE_DIR == "page" else "xb") as f:  # "x": never overwrite
                f.write(data)
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")
            print("wrote %s (%d bytes)" % (out, len(data)))

    return Handler


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    bind_ip, tv_ip = argv[1], argv[2]
    cert = Path(argv[3]) if len(argv) > 3 else HERE / "cert.pem"
    key = Path(argv[4]) if len(argv) > 4 else HERE / "key.pem"

    httpd = http.server.HTTPServer((bind_ip, 443), make_handler(tv_ip))
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    print("serving %s on https://%s:443, answering only %s" % (PAGE, bind_ip, tv_ip))
    print("POST /result -> %s   (Ctrl-C to stop)" % out_path(PAGE_DIR, datetime.now(timezone.utc)))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
