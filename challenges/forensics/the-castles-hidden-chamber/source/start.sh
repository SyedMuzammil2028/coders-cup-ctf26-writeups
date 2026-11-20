#!/bin/sh
set -eu
exec python3 /app/src/server.py \
  --artifact /run/challenge/challenge.jpg \
  --index /app/public/index.html

