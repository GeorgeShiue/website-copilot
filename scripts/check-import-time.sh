#!/usr/bin/env bash
# import 耗時回歸檢查（警告模式，永遠回傳 0）：
# 量測 CLI 入口與 pipelines.prepare 的 import 累計耗時，超過門檻時輸出 GitHub Actions 的 ::warning::。
# 這兩個入口刻意保持輕量（重依賴在子命令／階段函式內才載入），頂層新增重依賴會讓耗時暴增。
# 基準（本機）：cli 約 0.13 s、pipelines.prepare 約 0.11 s。
# 門檻可用環境變數 IMPORT_TIME_THRESHOLD（秒）調整，預設 0.75。
set -euo pipefail
cd "$(dirname "$0")/.."

uv run python - "${IMPORT_TIME_THRESHOLD:-0.75}" website_copilot.cli website_copilot.pipelines.prepare <<'PY'
import subprocess
import sys

threshold = float(sys.argv[1])
for module in sys.argv[2:]:
    result = subprocess.run(
        [sys.executable, "-X", "importtime", "-c", f"import {module}"],
        capture_output=True,
        text=True,
        check=True,
    )
    line = [x for x in result.stderr.splitlines() if x.rstrip().endswith(f"| {module}")][-1]
    seconds = int(line.split("|")[1]) / 1e6
    if seconds > threshold:
        print(f"::warning::import {module} 耗時 {seconds:.2f}s，超過門檻 {threshold:.2f}s")
    else:
        print(f"OK  import {module}: {seconds:.2f}s (門檻 {threshold:.2f}s)")
PY
