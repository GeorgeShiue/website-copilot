"""Agent 層的設定資料結構（M1）。

AgentConfig 定義 Agent 的 LLM 與提示詞設定。
llm_name 預設與 RAG config 的 query_llm_name 相同（gemini-3.1-flash-lite），
但兩者解耦：Agent 可獨立換 model（如 gemini-3-flash）而不影響 RAG。
retriever 的 top-k 等檢索參數由 RAG config 管理，Agent 不覆寫。

與其他 config 統一介面（對齊 rag_config / website_crawler_config）：
- from_toml()：從 configs/agent/{name}.toml 載入（含 overrides）
- __post_init__ → _validate_config()：欄位型態與內容驗證
- run_name：根據 config TOML 中 # run name 註解的欄位生成
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Self

from utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
    load_config_from_toml,
    override_config,
)

logger = logging.getLogger(__name__)

DEFAULT_LLM_NAME = "gemini-3.1-flash-lite"
DEFAULT_SYSTEM_PROMPT = (
    "你是網站助理。回答問題前，請先使用 webpage_retriever 工具"
    "檢索網站中的相關資訊，再根據檢索結果回答。"
    "回答時必須列出參考來源的 URL。若檢索結果不足以回答，請誠實說明。"
)

DEFAULT_CONFIG_FOLDER_PATH = "configs/agent"
DEFAULT_CONFIG_NAME = "default"
DEFAULT_INIT_CONFIG_SECTION = "init"
AGENT_SECTION = "agent"
INIT_KEYS = {
    "site_id",
}
AGENT_KEYS = {
    "llm_name",
    "system_prompt",
}
SECTIONS_TO_KEYS = {
    DEFAULT_INIT_CONFIG_SECTION: INIT_KEYS,
    AGENT_SECTION: AGENT_KEYS,
}


@dataclass
class AgentConfig:
    """Agent 執行設定。

    Attributes:
        config_name: 設定名稱（用於 run name 與落盤識別）。
        site_id: 站點識別碼（必要，建立四層路徑結構）。
        llm_name: Agent 使用的 LLM 名稱（與 RAG query LLM 解耦）。
        system_prompt: Agent 的系統提示詞。
    """

    # ----- metadata (no default values)-----
    site_id: str
    # ----- config (with defaults)-----
    config_name: str = DEFAULT_CONFIG_NAME
    llm_name: str = DEFAULT_LLM_NAME
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    # ----- metadata -----
    sections_to_keys: dict[str, set[str]] = field(
        default_factory=lambda: SECTIONS_TO_KEYS
    )

    def __post_init__(self) -> None:
        _validate_config(vars(self))

    @classmethod
    def from_toml(
        cls,
        config_name: str = DEFAULT_CONFIG_NAME,
        **overrides,
    ) -> Self:
        """從 TOML 設定檔建立 AgentConfig。"""
        config_path = os.path.join(DEFAULT_CONFIG_FOLDER_PATH, f"{config_name}.toml")
        config = load_config_from_toml(config_path, SECTIONS_TO_KEYS)
        config = override_config(config, overrides, SECTIONS_TO_KEYS)
        config["config_name"] = config_name
        return cls(**config)

    @property
    def run_name(self) -> str:
        """根據 config TOML 中的註解生成 run name。"""
        config_path = os.path.join(
            DEFAULT_CONFIG_FOLDER_PATH, f"{self.config_name}.toml"
        )
        commented_configs = filter_commented_configs(config_path, "run name")
        if not commented_configs:
            return "default"

        run_name = ""
        for config in commented_configs:
            value = getattr(self, config, None)
            if value is not None:
                run_name += f"{config}-{value}_"
        run_name = run_name.rstrip("_")

        return run_name


def _validate_config(config: dict[str, Any]) -> None:
    # ----- metadata -----
    site_id = config.get("site_id")
    if not isinstance(site_id, str) or not site_id.strip():
        raise ConfigValidationError("site_id 必須是非空字串")

    # ----- agent config -----
    llm_name = config.get("llm_name")
    system_prompt = config.get("system_prompt")

    if llm_name is None:
        raise ConfigValidationError("llm_name 不可為 None")
    if not isinstance(llm_name, str):
        raise ConfigValidationError("llm_name 必須是字串")
    if not llm_name.strip():
        raise ConfigValidationError("llm_name 不可為空字串")

    if system_prompt is None:
        raise ConfigValidationError("system_prompt 不可為 None")
    if not isinstance(system_prompt, str):
        raise ConfigValidationError("system_prompt 必須是字串")
    if not system_prompt.strip():
        raise ConfigValidationError("system_prompt 不可為空字串")
