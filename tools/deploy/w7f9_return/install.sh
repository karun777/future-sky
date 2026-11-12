#!/bin/bash
# Operator-only maintenance entry point; the Python installer owns code backups.
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then
    echo "Run this reviewed script from the privileged server terminal." >&2
    exit 1
fi
cd "$(dirname "$0")/../../.."
export PYTHONPATH=.
RETURN_PYTHON=/opt/futuresky/.venv-web-pilot-20261029/bin/python
"$RETURN_PYTHON" -m tools.deploy.w7f9_return.activate preflight
systemctl stop futuresky-bot.service
trap 'echo "Maintenance stopped on an error. Retain the transaction and check service state before continuing." >&2' ERR
"$RETURN_PYTHON" -m tools.deploy.w7f9_return.activate install
"$RETURN_PYTHON" -m tools.deploy.w7f9_return.activate verify
systemctl start futuresky-bot.service
systemctl is-active futuresky-bot.service
echo "Code installed and service started. Wait for Discord readiness before the owner uses !awaken."
