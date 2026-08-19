"""RAG 子套件 — 向量檢索 + 評估全流程。"""

from app.engines.rag.rag import RAG
from app.engines.rag.rag_eval_prompts import (
    FAITHFULNESS_EVAL_TEMPLATE,
    FAITHFULNESS_REFINE_TEMPLATE,
    RELEVANCY_EVAL_TEMPLATE,
    RELEVANCY_REFINE_TEMPLATE,
)
from app.engines.rag.rag_factory import (
    NodePipelineBuilder,
    RAGBuilder,
    VectorStoreBuilder,
)

__all__ = [
    "RAG",
    "RAGBuilder",
    "NodePipelineBuilder",
    "VectorStoreBuilder",
    "FAITHFULNESS_EVAL_TEMPLATE",
    "FAITHFULNESS_REFINE_TEMPLATE",
    "RELEVANCY_EVAL_TEMPLATE",
    "RELEVANCY_REFINE_TEMPLATE",
]
