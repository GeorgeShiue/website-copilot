from typing import Annotated, ClassVar, Literal, Self

from pydantic import Field, PositiveInt, model_validator

from website_copilot.config.base_config import (
    BaseModuleConfig,
    ConfigModel,
    NonEmptyStr,
)


class NodesConfig(ConfigModel):
    chunk_size: PositiveInt = 800
    chunk_overlap: PositiveInt = 100
    paragraph_separator: str = "\n\n"

    @model_validator(mode="after")
    def _check_overlap(self) -> Self:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap 必須小於 chunk_size")
        return self


class HybridRankerParams(ConfigModel):
    weights: Annotated[list[float], Field(min_length=2, max_length=2)] | None = Field(
        default=None, description="WeightedRanker 的 [dense, sparse] 權重"
    )
    k: PositiveInt | None = Field(default=None, description="RRFRanker 的 k 值")


class VectorStoreConfig(ConfigModel):
    vector_store_type: Literal["milvus"] = "milvus"
    hybrid_ranker: Literal["RRFRanker", "WeightedRanker"] = "WeightedRanker"
    hybrid_ranker_params: HybridRankerParams | None = Field(
        default_factory=lambda: HybridRankerParams(weights=[1.0, 0.5]),
        description=(
            "null 時依 hybrid_ranker 使用內建參數；改用 RRFRanker 時寫 {k: 60}"
            "（繼承鏈中已寫 weights 時需另寫 weights: null）"
        ),
    )

    @model_validator(mode="after")
    def _check_ranker_params(self) -> Self:
        params = self.hybrid_ranker_params
        if params is None:
            return self
        if self.hybrid_ranker == "WeightedRanker":
            if params.weights is None or params.k is not None:
                raise ValueError(
                    "WeightedRanker 的 hybrid_ranker_params 必須有 weights 且不可有 k"
                )
        elif params.k is None or params.weights is not None:
            raise ValueError(
                "RRFRanker 的 hybrid_ranker_params 必須有 k 且不可有 weights"
            )
        return self


class IndexConfig(ConfigModel):
    embedding_name: NonEmptyStr = "text-embedding-3-small"


class RetrieverConfig(ConfigModel):
    query_mode: Literal["hybrid", "default"] = "hybrid"
    similarity_top_k: PositiveInt = Field(
        default=10, description="dense 檢索回傳的節點數"
    )
    hybrid_top_k: PositiveInt = Field(
        default=10, description="hybrid 檢索最終回傳的節點數"
    )
    alpha: float = Field(
        default=0.5, ge=0, le=1, description="hybrid 檢索的 dense 權重"
    )


class QueryEngineConfig(ConfigModel):
    query_llm_name: NonEmptyStr = "gpt-5.6-luna"
    evaluator_llm_name: NonEmptyStr = "gpt-5.6-terra"
    cutoff: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="相似度門檻，僅在 query_mode 非 hybrid 時生效",
    )


class RAGConfig(BaseModuleConfig):
    """RAG 參數；站點（collection 名稱）、建庫來源與向量庫位置為執行期值，見 RAGTarget。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/rag"
    _DEFAULT_RUN_NAME_FIELDS: ClassVar[tuple[str, ...]] = (
        "vector_store.vector_store_type",
    )

    nodes: NodesConfig = Field(default_factory=NodesConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    index: IndexConfig = Field(default_factory=IndexConfig)
    retriever: RetrieverConfig = Field(default_factory=RetrieverConfig)
    query_engine: QueryEngineConfig = Field(default_factory=QueryEngineConfig)

    def _post_process_run_name(self, run_name: str) -> str:
        run_name = run_name.replace("/", "-")
        if run_name.find("-gemini") > 1:
            run_name = run_name.replace("-gemini", "", 1)
        return run_name
