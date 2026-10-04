"""文件檢索問題集：只呼叫 retriever（不經 Agent 的 LLM），斷言預期文件出現在 top-k。

費用僅查詢的 embedding（標記 cost）。預設查詢 data/ 中已 publish 的向量庫；
設定環境變數 DOCUMENT_QUESTIONS_VECTOR_STORE_RUN 為 rag-build 的 run 資料夾時，改查該 run 的向量庫
（供各階段在不 publish 的情況下驗證）。問題集見 tests/fixtures/document_questions.yml。
"""

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from website_copilot.config.rag_config import RAGConfig
from website_copilot.retrieval.factory import (
    load_rag,
    published_target,
    vector_store_run_target,
)
from website_copilot.utils.log_helper import setup_logging

setup_logging("info")

QUESTIONS_PATH = Path("tests/fixtures/document_questions.yml")
VECTOR_STORE_RUN_ENV = "DOCUMENT_QUESTIONS_VECTOR_STORE_RUN"


def _is_expected(question: dict[str, Any], result: dict[str, Any]) -> bool:
    url = result.get("url", "")
    title = result.get("page_title", "")
    return any(part in url for part in question.get("expected_urls", [])) or any(
        title == expected for expected in question.get("expected_titles", [])
    )


@pytest.mark.cost
def test_document_questions_find_expected_documents() -> None:
    spec = yaml.safe_load(QUESTIONS_PATH.read_text(encoding="utf-8"))
    site, top_k = spec["site"], spec["top_k"]
    run_path = os.environ.get(VECTOR_STORE_RUN_ENV)
    target = (
        vector_store_run_target(site, run_path) if run_path else published_target(site)
    )
    rag = load_rag(RAGConfig.from_yaml("default"), target)

    missed: list[str] = []
    for question in spec["questions"]:
        results = rag.retrieve(question["question"], similarity_top_k=top_k)
        ranks = [i for i, r in enumerate(results, 1) if _is_expected(question, r)]
        if not ranks:
            actual = [f"{r.get('page_type')}:{r.get('page_title')}" for r in results]
            missed.append(f"{question['question']} → 未命中；實際排名：{actual}")

    assert not missed, "\n".join(missed)
