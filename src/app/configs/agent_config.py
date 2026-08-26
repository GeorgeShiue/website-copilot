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
from dataclasses import dataclass
from typing import Any, ClassVar

from app.configs.base_config import BaseModuleConfig
from utils.config_helper import ConfigValidationError

logger = logging.getLogger(__name__)

DEFAULT_LLM_NAME = "gemini-3.1-flash-lite"
DEFAULT_SYSTEM_PROMPT = (
    "你是多站網站助理，可從多個學校網站知識庫中檢索資訊。\n\n"
    "## 使用工具的流程\n"
    "1. 若不確定有哪些可用的知識庫，先使用 list_knowledge_bases 查詢\n"
    "2. 使用 webpage_retriever 時必須提供 site_id 參數\n"
    "3. 若問題來自特定網站（如對話中有 site 語境），直接使用該 site 檢索\n\n"
    "## 回答規則\n"
    "- 根據檢索結果回答，必須列出參考來源的 URL\n"
    "- 若檢索結果不足以回答，請誠實說明\n"
    "- 若問題可能涉及多個站點，可分別檢索後合併回答"
)

DEFAULT_INIT_CONFIG_FOLDER_PATH = "configs/agent"
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
class AgentConfig(BaseModuleConfig):
    """Agent 執行設定。

    Attributes:
        llm_name: Agent 使用的 LLM 名稱（與 RAG query LLM 解耦）。
        system_prompt: Agent 的系統提示詞。
    """

    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/agent"
    sections_to_keys: ClassVar[dict[str, set[str]]] = SECTIONS_TO_KEYS

    # ----- config (with defaults)-----
    llm_name: str = DEFAULT_LLM_NAME
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    def __post_init__(self) -> None:
        _validate_config(vars(self))

    @classmethod
    def from_toml(
        cls,
        config_name: str = DEFAULT_CONFIG_NAME,
        **overrides,
    ):
        """從 TOML 設定檔建立 AgentConfig。"""
        return super().from_toml(config_name, **overrides)


def _validate_config(config: dict[str, Any]) -> None:
    # ----- metadata -----
    BaseModuleConfig.validate_site_id(config.get("site_id", ""))

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
