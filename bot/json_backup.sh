#!/usr/bin/env bash
set -euo pipefail

# Future Sky — JSON backup (data/)
# Usage:
#   ./json_backup.sh            # backs up ./data into ./data/_backups/<timestamp>/
#   ./json_backup.sh --reason boot
#
# Run from bot root: /home/karun777/futuresky/bot

REASON="manual"
if [[ "${1:-}" == "--reason" ]]; then
  REASON="${2:-manual}"
fi

if [[ ! -d "data" ]]; then
  echo "ERROR: data/ directory not found. Run this from the bot root."
  exit 1
fi

TS="$(date -u +%Y%m%d_%H%M%S)"
DEST="data/_backups/${TS}_${REASON}"
mkdir -p "$DEST"

# Copy JSON files, preserving directory structure under data/
# Exclude backups folder itself.
rsync -a --prune-empty-dirs \
  --include='*/' --include='*.json' --exclude='*' \
  --exclude='_backups/' \
  data/ "$DEST/"

# Write a manifest (paths + sha256) for integrity and diffing
MANIFEST="$DEST/manifest.txt"
{
  echo "timestamp_utc=${TS}"
  echo "reason=${REASON}"
  echo "source=$(pwd)/data"
  echo ""
  echo "sha256:"
  (cd "$DEST" && find . -type f -name "*.json" -print0 | sort -z | xargs -0 sha256sum) || true
} > "$MANIFEST"

# Retention: keep last 10 backups by default
KEEP="${FS_BACKUP_KEEP:-10}"
if [[ "$KEEP" =~ ^[0-9]+$ ]]; then
  # list backups newest-first, delete extras
  mapfile -t backups < <(ls -1dt data/_backups/* 2>/dev/null || true)
  if (( ${#backups[@]} > KEEP )); then
    for ((i=KEEP; i<${#backups[@]}; i++)); do
      rm -rf "${backups[$i]}"
    done
  fi
fi

echo "OK: backup created at $DEST"
echo "Manifest: $MANIFEST"
