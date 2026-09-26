"""Import 冒煙測試：逐一 import 所有套件模組與入口，及早發現壞掉的 import 與循環 import。

以檔案系統掃描（而非 pkgutil.walk_packages）列出模組，因為部分目錄是沒有
__init__.py 的 namespace package，walk_packages 會略過。
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOTS = ["app", "utils"]
ENTRY_MODULES = ["cli", "prepare", "serve"]


def _discover_modules() -> list[str]:
    modules: list[str] = []
    for root in PACKAGE_ROOTS:
        for path in sorted((SRC_ROOT / root).rglob("*.py")):
            parts = path.relative_to(SRC_ROOT).with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            modules.append(".".join(parts))
    return modules + ENTRY_MODULES


@pytest.mark.parametrize("module_name", _discover_modules())
def test_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)
