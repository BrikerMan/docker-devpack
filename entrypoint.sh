#!/usr/bin/env bash
set -eo pipefail

for f in /etc/profile.d/*.sh; do
    [ -r "$f" ] && . "$f" || true
done

exec "$@"
