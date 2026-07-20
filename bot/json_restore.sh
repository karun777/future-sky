\
#!/usr/bin/env bash
set -euo pipefail

# Future Sky — restore JSON backup (data/)
# Usage:
#   ./json_restore.sh data/_backups/<timestamp_reason>
#
# SAFETY:
# - Stops the systemd service first (server use).
# - Restores only *.json files into ./data
# - Creates a pre-restore safety backup first.

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 data/_backups/<backup_folder>"
  exit 1
fi

BACKUP_DIR="$1"

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "ERROR: Backup directory not found: $BACKUP_DIR"
  exit 1
fi

if [[ ! -d "data" ]]; then
  echo "ERROR: data/ directory not found. Run this from the bot root."
  exit 1
fi

echo "Restoring from: $BACKUP_DIR"
echo "Creating safety backup first..."
./json_backup.sh --reason pre_restore

# If systemctl exists, attempt to stop service (safe on server, harmless locally if no sudo rights)
if command -v systemctl >/dev/null 2>&1; then
  echo "Stopping service (if available): futuresky-bot"
  sudo systemctl stop futuresky-bot || true
fi

echo "Restoring JSON files..."
rsync -a --prune-empty-dirs \
  --include='*/' --include='*.json' --exclude='*' \
  "$BACKUP_DIR/" data/

echo "Validating JSON parses..."
find data -name "*.json" -print0 | xargs -0 -I{} sh -c 'python -m json.tool "{}" >/dev/null || (echo "BAD JSON: {}" && exit 1)'

echo "Restore complete."

if command -v systemctl >/dev/null 2>&1; then
  echo "Starting service: futuresky-bot"
  sudo systemctl start futuresky-bot || true
fi

echo "Done."
