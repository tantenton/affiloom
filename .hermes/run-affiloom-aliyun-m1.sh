#!/usr/bin/env bash
set -euo pipefail
PROJECT="/home/ubuntu/affiloom"
cd "$PROJECT"
exec /home/ubuntu/.local/bin/hermes chat -q "Continue the existing Affiloom project in this directory. Complete exactly one milestone: fix backend packaging, imports, and test failures. Use actual current directory; never use /workspace paths. Inspect files before edits, run backend tests, commit only if tests pass, then exit. Do not delegate. Keep output compact."