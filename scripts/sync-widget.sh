#!/usr/bin/env bash
# 以 server/static/widget.js 為來源同步到 extension/（兩份皆進版控，CI 會比對）。
set -euo pipefail
cd "$(dirname "$0")/.."

cp src/website_copilot/server/static/widget.js extension/widget.js
echo "已同步 extension/widget.js"
