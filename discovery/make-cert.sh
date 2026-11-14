#!/usr/bin/env bash
# Generate a fresh self-signed cert for vidaahub.com into discovery/.
# Never committed (see .gitignore). Re-run any time; it overwrites.
set -euo pipefail
cd "$(dirname "$0")"

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout key.pem -out cert.pem \
  -days 30 -subj "/CN=vidaahub.com" \
  -addext "subjectAltName=DNS:vidaahub.com"

echo "wrote discovery/cert.pem and discovery/key.pem (CN=vidaahub.com, 30 days)"
