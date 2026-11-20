#!/bin/sh
set -eu
exec python3 -m gunicorn --bind "0.0.0.0:${PORT:-10000}" --workers 1 --threads 4 --access-logfile - --error-logfile - app:app
