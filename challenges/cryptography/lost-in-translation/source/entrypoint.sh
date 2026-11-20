#!/bin/sh
set -eu
umask 027
python3 /opt/challenge/generate.py --output /tmp/ctf-data/ciphertext.json
unset FLAG
exec nginx -g 'daemon off;'
