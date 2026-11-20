#!/bin/sh
set -eu

# generator.py validates FLAG and exits non-zero without revealing it on error.
python -m src.generator --output /app/generated/malware.pyc

# The long-running HTTP process has no reason to retain the injected secret.
unset FLAG

# The generator has finished; this is the only long-running process.
exec python -m src.server --artifact /app/generated/malware.pyc --public-dir /app/public

