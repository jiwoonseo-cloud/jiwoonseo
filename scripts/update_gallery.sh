#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
if [[ "${1:-}" != "--no-fetch" ]]; then
  git fetch --prune origin '+refs/heads/*:refs/remotes/origin/*'
fi
python3 scripts/update_gallery.py
