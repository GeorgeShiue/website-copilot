#!/usr/bin/env bash
# 單元測試（只跑 tests/unit）；額外參數會傳給 pytest，例如 ./scripts/test.sh -x
# 整合測試需 API 金鑰，手動執行：
#   uv run pytest tests/integration                 # 全部（含 cost：會產生 API 費用）
#   uv run pytest tests/integration -m "not cost"   # 略過會呼叫 LLM API 的測試
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> pytest tests/unit"
uv run pytest tests/unit "$@"
