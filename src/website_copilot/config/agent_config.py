"""Agent 層的設定資料結構。

AgentConfig 定義 Agent 的 LLM 與提示詞設定。
llm_name 與 RAG config 的 query_llm_name 解耦：Agent 可獨立換 model 而不影響 RAG。
retriever 的 top-k 等檢索參數由 RAG config 管理，Agent 不覆寫。

Agent 不綁定特定 site_id：多站管理由 RAGRegistry 在工具層級處理。
"""

from typing import ClassVar

from pydantic import Field

from website_copilot.config.base_config import BaseModuleConfig, NonEmptyStr
from website_copilot.config.prompts import AGENT_SYSTEM_PROMPT


class AgentConfig(BaseModuleConfig):
    """Agent 執行設定。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/agent"

    llm_name: NonEmptyStr = Field(
        default="gpt-5.6-luna", description="Agent 使用的 LLM（與 RAG query LLM 解耦）"
    )
    system_prompt: NonEmptyStr = Field(
        default=AGENT_SYSTEM_PROMPT,
        description="Agent 的系統提示詞（見 config/prompts.py）",
    )
