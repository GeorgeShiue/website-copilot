"""檢索來源序列化：rag-query 的 extract_sources_list 與 Agent tool 用的 RAG.retrieve。"""

from unittest.mock import MagicMock

from llama_index.core.schema import NodeWithScore, TextNode

from website_copilot.retrieval.evaluation import extract_sources_list
from website_copilot.retrieval.rag import RAG

LONG_TEXT = "x" * 1000


def _node(text: str, score: float, **metadata: str) -> NodeWithScore:
    return NodeWithScore(node=TextNode(text=text, metadata=metadata), score=score)


NODES = [
    _node(
        LONG_TEXT,
        0.9,
        page_title="Lab",
        page_type="about",
        page_url="https://ex.com/lab",
    ),
    _node("short", 0.5),  # 缺少 metadata
]


def _expected(content_0: str) -> list[dict]:
    return [
        {
            "page_title": "Lab",
            "score": 0.9,
            "page_type": "about",
            "url": "https://ex.com/lab",
            "content": content_0,
        },
        {
            "page_title": "Unknown",
            "score": 0.5,
            "page_type": "Unknown",
            "url": "",
            "content": "short",
        },
    ]


def test_extract_sources_list_truncates_content() -> None:
    assert extract_sources_list(NODES) == _expected(LONG_TEXT[:800])


def test_extract_sources_list_without_truncation() -> None:
    assert extract_sources_list(NODES, max_content_length=None) == _expected(LONG_TEXT)


def test_rag_retrieve_returns_full_content_and_restores_retriever() -> None:
    retriever = MagicMock()
    retriever.retrieve.return_value = NODES
    retriever._filters = None
    retriever.similarity_top_k = 5
    rag = RAG(MagicMock(), retriever=retriever)

    results = rag.retrieve("q", filter_dict={"page_type": "about"}, similarity_top_k=2)

    assert results == _expected(LONG_TEXT)
    assert (retriever._filters, retriever.similarity_top_k) == (None, 5)


def test_source_key_order_is_shared() -> None:
    """兩處的 key 順序一致（url 在 content 之前），results.json 與 tool 輸入同形。"""
    retriever = MagicMock()
    retriever.retrieve.return_value = NODES
    rag = RAG(MagicMock(), retriever=retriever)
    order = ["page_title", "score", "page_type", "url", "content"]

    assert list(extract_sources_list(NODES)[0]) == order
    assert list(rag.retrieve("q")[0]) == order
