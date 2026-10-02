"""Import 冒煙測試：逐一 import 所有套件模組（含 cli 入口），及早發現壞掉的 import 與循環 import；
並確認 CLI 與 serve 路徑不載入爬蟲模組。

以檔案系統掃描（而非 pkgutil.walk_packages）列出模組，因為部分目錄是沒有
__init__.py 的 namespace package，walk_packages 會略過。
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
PACKAGE_ROOTS = ["website_copilot"]


def _discover_modules() -> list[str]:
    modules: list[str] = []
    for root in PACKAGE_ROOTS:
        for path in sorted((SRC_ROOT / root).rglob("*.py")):
            parts = path.relative_to(SRC_ROOT).with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            modules.append(".".join(parts))
    return modules


@pytest.mark.parametrize("module_name", _discover_modules())
def test_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)


def test_cli_and_serve_path_do_not_load_crawler() -> None:
    """CLI 與 serve 路徑不載入爬蟲模組（serve 只讀向量庫）。"""
    code = (
        "import sys, website_copilot.cli, website_copilot.cli.serve, "
        "website_copilot.pipelines.serve; "
        "print([m for m in sys.modules if 'crawl4ai' in m or 'ingestion.crawling' in m])"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "[]"
