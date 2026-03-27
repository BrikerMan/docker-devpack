#!/usr/bin/env bash
set -e

for f in /etc/profile.d/*.sh; do
    [ -r "$f" ] && . "$f"
done

exec "$@"
