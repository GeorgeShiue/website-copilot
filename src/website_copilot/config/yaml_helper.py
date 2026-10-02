"""YAML 設定檔的讀取（含 extends 繼承）。

`load_config_dict(folder, name)` 逐層讀取 `extends` 指向的同資料夾設定檔，
以 `deep_merge` 由父到子疊合成單一 dict（只驗證最終結果，不驗證各層）。
寫出（module_config.yml／run_config.yml）見 `utils/config_helper.py`。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from website_copilot.utils.config_helper import ConfigValidationError

CONFIG_SUFFIX = ".yml"
EXTENDS_KEY = "extends"


@dataclass(frozen=True)
class LoadedConfig:
    """extends 展開後的設定 dict 與繼承鏈。

    Attributes:
        data: 由父到子 deep merge 後的 dict（已移除 extends）。
        path: 實際載入的設定檔路徑。
        chain: 繼承鏈的設定名稱，第一個為本身，其後依序為父、祖父…。
    """

    data: dict[str, Any]
    path: Path
    chain: tuple[str, ...]

    @property
    def source(self) -> str:
        """錯誤訊息與存檔檔頭使用的來源描述，如 `configs/rag/test.yml (extends: default)`。"""
        if len(self.chain) == 1:
            return str(self.path)
        return f"{self.path} (extends: {' → '.join(self.chain[1:])})"


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """將 override 疊在 base 上：兩邊都是 dict 時遞迴合併，其他情況整個取代。"""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigValidationError(f"{path}: 設定檔最上層必須是 mapping")
    return data


def load_config_dict(folder: str | Path, name: str) -> LoadedConfig:
    """讀取 `{folder}/{name}.yml` 並展開 extends（只能繼承同資料夾的設定）。

    Raises:
        FileNotFoundError: 設定檔本身不存在。
        ConfigValidationError: 被繼承的設定檔不存在、循環繼承或 extends 格式錯誤。
    """
    folder = Path(folder)
    path = folder / f"{name}{CONFIG_SUFFIX}"
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    chain: list[str] = []
    layers: list[dict[str, Any]] = []
    current = name
    while True:
        if current in chain:
            raise ConfigValidationError(
                f"{path}: 循環繼承：{' → '.join([*chain, current])}"
            )
        chain.append(current)
        current_path = folder / f"{current}{CONFIG_SUFFIX}"
        if not current_path.is_file():
            raise ConfigValidationError(
                f"{path}: 找不到被繼承的設定檔 {current_path}"
                f"（繼承鏈：{' → '.join(chain)}）"
            )

        layer = _read_yaml_mapping(current_path)
        layers.append(layer)
        if EXTENDS_KEY not in layer:
            break
        parent = layer.pop(EXTENDS_KEY)
        if not isinstance(parent, str) or not parent.strip():
            raise ConfigValidationError(
                f"{current_path}: extends 必須是同資料夾的設定名稱（不含副檔名）"
            )
        current = parent

    data: dict[str, Any] = {}
    for layer in reversed(layers):
        data = deep_merge(data, layer)
    return LoadedConfig(data=data, path=path, chain=tuple(chain))
