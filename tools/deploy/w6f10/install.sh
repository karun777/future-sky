#!/usr/bin/env bash
# Static assets only. Does not control services or read player data.
set -euo pipefail
review_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
review_python="/opt/futuresky/.venv-web-pilot-20261029/bin/python"
cd "$review_repo"
for review_step in check install verify; do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$review_repo" "$review_python" \
    -m tools.deploy.w6f10.activate "$review_step"
done
