#!/usr/bin/env bash
# 靜態檢查：undersort（class 方法順序）+ ruff check + ruff format + pyright 型別檢查。
# 預設只檢查不改檔；加 --fix 時改為自動排序方法、修正 ruff 問題並格式化。
set -euo pipefail
cd "$(dirname "$0")/.."

fix=false
case "${1:-}" in
    "") ;;
    --fix) fix=true ;;
    *) echo "用法：$0 [--fix]" >&2; exit 2 ;;
esac

if $fix; then
    echo "==> undersort"
    uv run undersort src
    echo "==> ruff check --fix"
    uv run ruff check --fix .
    echo "==> ruff format"
    uv run ruff format .
else
    echo "==> undersort --check"
    uv run undersort --check src
    echo "==> ruff check"
    uv run ruff check .
    echo "==> ruff format --check"
    uv run ruff format --check .
fi

echo "==> pyright"
uv run pyright
