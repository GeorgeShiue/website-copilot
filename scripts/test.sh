#!/usr/bin/env bash
# 單元測試（略過 slow）；額外參數會傳給 pytest，例如 ./scripts/test.sh -x tests/unit
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> pytest -m \"not slow\""
uv run pytest -m "not slow" "$@"
