#!/bin/sh
set -eu

umask 077
artifact='/run/challenge/challenge.jpg'

python3 /app/src/generate_challenge.py \
  --source /opt/challenge/castle_original.jpg \
  --output "$artifact"

unset FLAG
exec "$@"

