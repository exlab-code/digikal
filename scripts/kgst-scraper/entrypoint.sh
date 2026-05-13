#!/bin/sh
# Snapshot container env so cron jobs (which run with an empty env) can source it.
# Quote values single-quoted and escape embedded single quotes.
printenv | while IFS='=' read -r name value; do
  esc=$(printf '%s' "$value" | sed "s/'/'\\\\''/g")
  printf "export %s='%s'\n" "$name" "$esc"
done > /etc/cron-env

exec cron -f
