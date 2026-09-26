"""`website-copilot exp <name>`：執行批次實驗（定義於 pipelines.exp.EXPERIMENTS）。"""

from dataclasses import dataclass
from typing import Annotated, Literal

import tyro

# 與 pipelines.exp.EXPERIMENTS 的 key 保持一致（由測試比對）；
# 在此列出而非 import，避免解析參數時就載入 RAG 相關依賴。
ExperimentName = Literal[
    "webpage_image_summarizer_model",
    "webpage_image_summarizer_prompt",
    "rag_dense_model",
    "rag_hybrid_ranker",
    "rag_hybrid_ranker_weights",
    "rag_hybrid_top_k",
    "rag_hybrid_five_question",
    "rag_dense_vs_hybrid",
]


@dataclass
class ExpCLI:
    name: Annotated[ExperimentName, tyro.conf.Positional] = "rag_dense_vs_hybrid"


def main(cli: ExpCLI) -> None:
    import asyncio

    from website_copilot.pipelines.exp import run_experiment
    from website_copilot.utils.log_helper import setup_logging

    setup_logging("debug")
    asyncio.set_event_loop(asyncio.new_event_loop())
    run_experiment(cli.name)
