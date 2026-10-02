#!/usr/bin/env bash
# 確認 extension/widget.js 與來源 server/static/widget.js 一致。
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> widget.js 同步檢查"
if ! cmp -s src/website_copilot/server/static/widget.js extension/widget.js; then
    echo "widget.js 不一致，請執行 ./scripts/sync-widget.sh" >&2
    exit 1
fi
