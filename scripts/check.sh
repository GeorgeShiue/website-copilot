#!/usr/bin/env bash
# 依序執行 lint.sh（ruff + pyright）、test.sh（pytest tests/unit）、check-widget.sh。
# 任一組失敗即中止並回傳非 0（亦供 git bisect run 使用）。
set -euo pipefail
cd "$(dirname "$0")"

./lint.sh
./test.sh
./check-widget.sh
