"""LLM 供應商路由：依模型名稱選擇 client 類別、API key 環境變數與 litellm 前綴。

三個呼叫端（RAG 的 llama_index create_llm、Agent 的 langchain create_llm、
Augmenter 的 litellm 呼叫）皆以 mock 取代 client，不連網、不產生費用。
"""

import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from website_copilot.agent import langchain_helper
from website_copilot.ingestion.augmentation.augmenter import Augmenter
from website_copilot.ingestion.augmentation.processors import image_captioner
from website_copilot.ingestion.augmentation.processors.image_captioner import (
    ImageCaptioner,
)
from website_copilot.retrieval import llama_index_helpers
from website_copilot.utils import llm_provider
from website_copilot.utils.config_helper import EnvironmentVariableError
from website_copilot.utils.llm_provider import (
    UnsupportedModelError,
    get_api_key,
    resolve_provider,
)


@pytest.fixture(autouse=True)
def api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")


# ----- RAG（llama_index） -----


@pytest.mark.parametrize(
    ("model", "client", "key"),
    [
        ("gpt-5.6-luna", "OpenAI", "openai-key"),
        ("gemini-2.5-flash", "GoogleGenAI", "gemini-key"),
    ],
)
def test_llama_index_create_llm_routes_by_model_name(
    model: str, client: str, key: str
) -> None:
    with patch.object(llama_index_helpers, client) as client_cls:
        llm = llama_index_helpers.create_llm(model)

    assert llm is client_cls.return_value
    client_cls.assert_called_once_with(model=model, api_key=key)


# ----- Agent（langchain） -----


def test_langchain_create_llm_routes_gpt_to_openai() -> None:
    with patch.object(langchain_helper, "ChatOpenAI") as client_cls:
        llm = langchain_helper.create_llm("gpt-5.6-luna")

    assert llm is client_cls.return_value
    kwargs = client_cls.call_args.kwargs
    assert kwargs["model"] == "gpt-5.6-luna"
    assert kwargs["api_key"].get_secret_value() == "openai-key"
    assert kwargs["use_responses_api"] is True


def test_langchain_create_llm_routes_gemini_to_google() -> None:
    with patch.object(langchain_helper, "ChatGoogleGenerativeAI") as client_cls:
        llm = langchain_helper.create_llm("gemini-2.5-flash")

    assert llm is client_cls.return_value
    client_cls.assert_called_once_with(model="gemini-2.5-flash", api_key="gemini-key")


# ----- Augmenter（litellm） -----


@pytest.mark.parametrize(
    ("model", "litellm_model", "key"),
    [
        ("gpt-5.6-luna", "openai/gpt-5.6-luna", "openai-key"),
        ("gemini-2.5-flash", "gemini/gemini-2.5-flash", "gemini-key"),
    ],
)
def test_augmenter_routes_by_model_name(
    monkeypatch: pytest.MonkeyPatch, model: str, litellm_model: str, key: str
) -> None:
    calls: list[dict[str, Any]] = []

    async def fake_acompletion(**kwargs: Any) -> Any:
        calls.append(kwargs)
        message = SimpleNamespace(content="caption")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)

    monkeypatch.setattr(image_captioner, "acompletion", fake_acompletion)
    monkeypatch.setattr(image_captioner, "completion_cost", lambda **_: 0.0)
    captioner = ImageCaptioner(
        model=model,
        prompt="describe",
        max_concurrency=1,
        litellm_kwargs={"timeout": 5},
    )

    caption, status, _ = asyncio.run(captioner._agenerate_image_caption("data"))

    assert (caption, status) == ("caption", "success")
    assert calls[0]["model"] == litellm_model
    assert calls[0]["api_key"] == key
    assert calls[0]["timeout"] == 5


# ----- 共用路由（llm_provider） -----


@pytest.mark.parametrize(
    ("model", "env_var", "prefix"),
    [
        ("gpt-5.6-luna", "OPENAI_API_KEY", "openai/"),
        ("GPT-4o", "OPENAI_API_KEY", "openai/"),
        ("gemini-2.5-flash", "GEMINI_API_KEY", "gemini/"),
        ("Gemini-2.5-Pro", "GEMINI_API_KEY", "gemini/"),
    ],
)
def test_resolve_provider_is_case_insensitive(
    model: str, env_var: str, prefix: str
) -> None:
    provider = resolve_provider(model)

    assert (provider.env_var, provider.litellm_prefix) == (env_var, prefix)


def test_resolve_provider_rejects_unknown_model() -> None:
    with pytest.raises(UnsupportedModelError, match="claude-x"):
        resolve_provider("claude-x")


def test_get_api_key_reads_environment() -> None:
    assert get_api_key(resolve_provider("gpt-5.6-luna")) == "openai-key"


def test_get_api_key_rejects_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_provider, "load_dotenv", lambda: None)  # 不讀 .env
    monkeypatch.delenv("OPENAI_API_KEY")

    with pytest.raises(EnvironmentVariableError, match="OPENAI_API_KEY"):
        get_api_key(resolve_provider("gpt-5.6-luna"))


# ----- 三個呼叫端的一致行為 -----


@pytest.mark.parametrize(
    "create_llm", [llama_index_helpers.create_llm, langchain_helper.create_llm]
)
def test_create_llm_rejects_unknown_model(create_llm: Any) -> None:
    """Agent 原本把未知模型預設為 OpenAI，現在與 RAG 一致：直接報錯。"""
    with pytest.raises(UnsupportedModelError):
        create_llm("claude-x")


@pytest.mark.parametrize(
    "create_llm", [llama_index_helpers.create_llm, langchain_helper.create_llm]
)
def test_create_llm_rejects_missing_key(
    monkeypatch: pytest.MonkeyPatch, create_llm: Any
) -> None:
    """RAG 原本把 None 當 api_key 傳給 SDK，現在與 Agent 一致：建構時報錯。"""
    monkeypatch.setattr(llm_provider, "load_dotenv", lambda: None)
    monkeypatch.delenv("GEMINI_API_KEY")

    with pytest.raises(EnvironmentVariableError, match="GEMINI_API_KEY"):
        create_llm("gemini-2.5-flash")


def test_augmenter_fails_fast_on_unknown_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """原本每張圖各自報錯（被當成摘要失敗）；現在開始前就失敗，不下載任何圖片。"""
    downloader = MagicMock()
    downloader.download.side_effect = AssertionError("should not download")
    summarizer = Augmenter(downloader=downloader, success_threshold=0.8, max_retries=0)

    with pytest.raises(UnsupportedModelError):
        summarizer.augment(
            {"page": {"fit_markdown": "![a](https://ex.com/a.png)"}},
            model="claude-x",
            prompt="describe",
            image_max_concurrency=1,
            image_source="markdown",
            image_min_size=100,
        )

    downloader.download.assert_not_called()
