"""Agent 層的設定資料結構（M1）。

AgentConfig 定義 Agent 的 LLM 與提示詞設定。
llm_name 預設與 RAG config 的 query_llm_name 相同（gemini-3.1-flash-lite），
但兩者解耦：Agent 可獨立換 model（如 gemini-3-flash）而不影響 RAG。
retriever 的 top-k 等檢索參數由 RAG config 管理，Agent 不覆寫。
"""

from dataclasses import dataclass, field

DEFAULT_LLM_NAME = "gemini-3.1-flash-lite"
DEFAULT_SYSTEM_PROMPT = (
    "你是實驗室網站問答助理。回答問題前，請先使用 webpage_retriever 工具"
    "檢索實驗室網站中的相關資訊，再根據檢索結果回答。"
    "回答時必須列出參考來源的 URL。若檢索結果不足以回答，請誠實說明。"
)

AGENT_SECTION = "agent"
AGENT_KEYS = {
    "llm_name",
    "system_prompt",
}
SECTIONS_TO_KEYS = {AGENT_SECTION: AGENT_KEYS}


@dataclass
class AgentConfig:
    """Agent 執行設定。

    Attributes:
        config_name: 設定名稱（用於 run name 與落盤識別）。
        llm_name: Agent 使用的 LLM 名稱（與 RAG query LLM 解耦）。
        system_prompt: Agent 的系統提示詞。
    """

    config_name: str = "default"
    llm_name: str = DEFAULT_LLM_NAME
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    # ----- metadata -----
    sections_to_keys: dict[str, set[str]] = field(
        default_factory=lambda: SECTIONS_TO_KEYS
    )
