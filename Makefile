WIDGET_SRC := src/website_copilot/server/static/widget.js
WIDGET_DST := extension/widget.js

.PHONY: help install check lint format typecheck test sync-widget check-widget serve

help:  ## 列出可用指令
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-14s %s\n", $$1, $$2}'

install:  ## 安裝依賴（含 dev group）
	uv sync

check: lint typecheck test check-widget  ## ruff + pyright + pytest + widget 同步檢查（亦供 git bisect run 使用）

lint:  ## ruff check 與 format 檢查
	uv run ruff check .
	uv run ruff format --check .

format:  ## 自動修正 ruff 問題並格式化
	uv run ruff check --fix .
	uv run ruff format .

typecheck:  ## pyright 型別檢查
	uv run pyright

test:  ## 單元測試（略過 slow）
	uv run pytest -m "not slow"

sync-widget:  ## 以 server/static/widget.js 為來源同步到 extension/
	cp $(WIDGET_SRC) $(WIDGET_DST)

check-widget:  ## 確認 extension/widget.js 與來源一致
	@cmp -s $(WIDGET_SRC) $(WIDGET_DST) || (echo "widget.js 不一致，請執行 make sync-widget" && exit 1)

serve:  ## 啟動 Chat Server
	uv run website-copilot serve
