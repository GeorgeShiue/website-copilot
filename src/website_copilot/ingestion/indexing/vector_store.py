"""Milvus 向量庫的建立。"""

import logging
import os
from typing import Any

from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.milvus.utils import (
    BGEM3SparseEmbeddingFunction,
)

logger = logging.getLogger(__name__)

EMBEDDING_DIM_MAP: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


class VectorStoreBuilder:
    @staticmethod
    def resolve_embedding_dim(embedding_name: str) -> int:
        dim = EMBEDDING_DIM_MAP.get(embedding_name)
        if dim is None:
            raise ValueError(
                f"Unknown embedding_name '{embedding_name}'. "
                f"Supported embeddings: {list(EMBEDDING_DIM_MAP.keys())}."
            )
        return dim

    @staticmethod
    def default_hybrid_ranker_params(hybrid_ranker: str) -> dict[str, Any]:
        if hybrid_ranker == "RRFRanker":
            return {"k": 60}
        elif hybrid_ranker == "WeightedRanker":
            return {"weights": [1.0, 0.5]}
        else:
            raise ValueError(
                f"Unsupported hybrid_ranker: '{hybrid_ranker}'. "
                f"Supported: 'RRFRanker', 'WeightedRanker'."
            )

    @staticmethod
    def build(
        collection_name: str,
        milvus_uri: str,
        embedding_name: str,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> MilvusVectorStore:
        """建立 MilvusVectorStore。

        固定不使用 MilvusVectorStore 內建的 overwrite（collection 層級的
        drop + recreate），一律沿用既有 collection；若要重建，呼叫端須先以
        IndexBuilder.clean() 整檔刪除，讓這裡等同於全新建立。
        """
        dim = VectorStoreBuilder.resolve_embedding_dim(embedding_name)
        if hybrid_ranker_params is None:
            hybrid_ranker_params = VectorStoreBuilder.default_hybrid_ranker_params(
                hybrid_ranker
            )

        if "://" not in milvus_uri:
            # milvus-lite 本地模式需要父目錄存在，否則連線會失敗
            os.makedirs(os.path.dirname(milvus_uri), exist_ok=True)

        vector_store = MilvusVectorStore(
            milvus_uri,
            collection_name=collection_name,
            overwrite=False,
            dim=dim,
            output_fields=["_node_content", "_node_type"],
            enable_sparse=True,
            sparse_embedding_function=BGEM3SparseEmbeddingFunction(),
            hybrid_ranker=hybrid_ranker,
            hybrid_ranker_params=hybrid_ranker_params,
            # Align client keepalive with MilvusLite server default (5 min) to
            # prevent ENHANCE_YOUR_CALM GOAWAY from ping-strike.
            grpc_options={
                "grpc.keepalive_time_ms": 300_000,
                "grpc.keepalive_permit_without_calls": False,
            },
        )
        logger.debug(
            "Built MilvusVectorStore at %s (collection=%s, dim=%d)",
            milvus_uri,
            collection_name,
            dim,
        )
        return vector_store
