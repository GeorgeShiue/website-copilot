"""模組 config 的共用基底類。

BaseModuleConfig 提供所有 module config 的共通欄位與行為：
- config_name / site_id / sections_to_keys
- from_toml() classmethod
- run_name property
- validate_site_id() 靜態方法

子類必須設定 ClassVar：
- _CONFIG_FOLDER_PATH: TOML 設定檔所在目錄
- sections_to_keys: section → keys 對照表（用於 TOML 讀寫）
"""

import logging
import os
from dataclasses import dataclass
from typing import ClassVar, Self

from utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
    load_config_from_toml,
    override_config,
)

logger = logging.getLogger(__name__)


@dataclass
class BaseModuleConfig:
    """模組 config 的共用基底類。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = ""
    sections_to_keys: ClassVar[dict[str, set[str]]] = {}

    # ----- metadata (no default values) -----
    config_name: str
    site_id: str

    @classmethod
    def from_toml(cls, config_name: str, **overrides) -> Self:
        """從 TOML 設定檔建立 config。"""
        config_path = os.path.join(cls._CONFIG_FOLDER_PATH, f"{config_name}.toml")
        config = load_config_from_toml(config_path, cls.sections_to_keys)
        config = override_config(config, overrides, cls.sections_to_keys)
        config["config_name"] = config_name
        return cls(**config)

    @property
    def run_name(self) -> str:
        """根據 config TOML 中的註解生成 run name。"""
        config_path = os.path.join(self._CONFIG_FOLDER_PATH, f"{self.config_name}.toml")
        commented_configs = filter_commented_configs(config_path, "run name")
        if not commented_configs:
            return "default"

        run_name = ""
        for config in commented_configs:
            value = getattr(self, config, None)
            if value is not None:
                run_name += f"{config}-{value}_"
        run_name = run_name.rstrip("_")
        return self._post_process_run_name(run_name)

    def _post_process_run_name(self, run_name: str) -> str:
        """子類可覆寫以自訂 run_name 的後處理邏輯。"""
        return run_name

    @staticmethod
    def validate_site_id(site_id: str) -> None:
        """驗證 site_id 非空字串。"""
        if not isinstance(site_id, str) or not site_id.strip():
            raise ConfigValidationError("site_id 必須是非空字串")
