#!/usr/bin/env bash
set -euo pipefail

LATEST_RUN=$(gh run list --limit 1 --json databaseId,status,conclusion,headBranch,event --jq '.[0]')
RUN_ID=$(echo "$LATEST_RUN" | jq -r '.databaseId')
BRANCH=$(echo "$LATEST_RUN" | jq -r '.headBranch')
EVENT=$(echo "$LATEST_RUN" | jq -r '.event')

echo "Watching run #$RUN_ID ($EVENT on $BRANCH)"
echo "Press Ctrl+C to stop"
echo "========================================="

gh run watch "$RUN_ID" --exit-status 2>&1

echo "========================================="
RESULT=$(gh run view "$RUN_ID" --json status,conclusion --jq '"\(.status) \(.conclusion)"')
echo "Run #$RUN_ID finished: $RESULT"
