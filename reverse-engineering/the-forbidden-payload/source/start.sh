#!/bin/sh
# Start only after the entrypoint has generated the per-instance artifact and
# removed FLAG from this process environment.
set -eu

exec python -m src.server \
  --artifact /app/generated/malware.pyc \
  --public-dir /app/public
