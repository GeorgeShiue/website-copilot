"""LLM 供應商路由：依模型名稱（不分大小寫）決定 API key 環境變數與 litellm 前綴。

RAG（llama_index）、Agent（langchain）與 Augmenter（litellm）共用；
各呼叫端只負責建構自己的 client。
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from website_copilot.utils.config_helper import EnvironmentVariableError


@dataclass(frozen=True)
class Provider:
    keyword: str  # 模型名稱包含此關鍵字即屬此供應商
    env_var: str
    litellm_prefix: str


PROVIDERS: tuple[Provider, ...] = (
    Provider(keyword="gemini", env_var="GEMINI_API_KEY", litellm_prefix="gemini/"),
    Provider(keyword="gpt", env_var="OPENAI_API_KEY", litellm_prefix="openai/"),
)


class UnsupportedModelError(ValueError):
    """模型名稱無法對應到任何供應商。"""


def resolve_provider(model_name: str) -> Provider:
    """依模型名稱找出供應商；找不到時拋出 UnsupportedModelError。"""
    lowered = model_name.lower()
    for provider in PROVIDERS:
        if provider.keyword in lowered:
            return provider
    raise UnsupportedModelError(
        f"無法根據模型名稱 '{model_name}' 判斷供應商。"
        f"請確保模型名稱包含 {[p.keyword for p in PROVIDERS]} 之一"
    )


def get_api_key(provider: Provider) -> str:
    """讀取供應商的 API key（先載入 .env）；未設定時拋出 EnvironmentVariableError。"""
    load_dotenv()
    api_key = os.getenv(provider.env_var)
    if not api_key:
        raise EnvironmentVariableError(
            f"環境變數 {provider.env_var} 未設定。請檢查 .env 或系統環境變數。"
        )
    return api_key
