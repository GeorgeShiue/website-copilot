import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from app.configs.base_config import BaseModuleConfig
from utils.config_helper import (
    ConfigValidationError,
    _normalize_toml_types,
)

logger = logging.getLogger(__name__)


DEFAULT_VECTOR_STORE_TYPE = "qdrant"
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_VECTOR_STORE_CONFIG_SECTION = "vector_store"
DEFAULT_NODES_CONFIG_SECTION = "nodes"
DEFAULT_INDEX_CONFIG_SECTION = "index"
DEFAULT_RETRIEVER_CONFIG_SECTION = "retriever"
DEFAULT_QUERY_ENGINE_CONFIG_SECTION = "query_engine"


def _default_webpages_path(site_id: str) -> str:
    return f"data/webpages/{site_id}"


def _default_milvus_uri(site_id: str) -> str:
    return f"data/rag/{site_id}/milvus.db"


def _default_qdrant_db_path(site_id: str) -> str:
    return f"data/rag/{site_id}/qdrant_db"


INIT_KEYS = {
    "site_id",
    "webpages_data_folder_path",
}
VECTOR_STORE_KEYS = {
    "qdrant_db_folder_path",
    "vector_store_type",
    "milvus_uri",
    "hybrid_ranker",
    "hybrid_ranker_params",
}
NODES_KEYS = {
    "chunk_size",
    "chunk_overlap",
    "paragraph_separator",
}
INDEX_KEYS = {
    "embedding_name",
}
RETRIEVER_KEYS = {
    "similarity_top_k",
    "query_mode",
    "hybrid_top_k",
    "alpha",
}
QUERY_ENGINE_KEYS = {
    "query_llm_name",
    "evaluator_llm_name",
    "cutoff",
    "query",
}
SECTIONS_TO_KEYS = {
    DEFAULT_INIT_CONFIG_SECTION: INIT_KEYS,
    DEFAULT_VECTOR_STORE_CONFIG_SECTION: VECTOR_STORE_KEYS,
    DEFAULT_NODES_CONFIG_SECTION: NODES_KEYS,
    DEFAULT_INDEX_CONFIG_SECTION: INDEX_KEYS,
    DEFAULT_RETRIEVER_CONFIG_SECTION: RETRIEVER_KEYS,
    DEFAULT_QUERY_ENGINE_CONFIG_SECTION: QUERY_ENGINE_KEYS,
}


@dataclass
class RAGConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/rag"
    sections_to_keys: ClassVar[dict[str, set[str]]] = SECTIONS_TO_KEYS

    # ----- init config -----
    site_id: str
    webpages_data_folder_path: str | None = None
    # ----- vector store config -----
    vector_store_type: str = DEFAULT_VECTOR_STORE_TYPE
    qdrant_db_folder_path: str | None = None
    milvus_uri: str | None = None
    hybrid_ranker: str = "WeightedRanker"
    hybrid_ranker_params: dict[str, Any] | None = None
    # ----- nodes config -----
    chunk_size: int = 800
    chunk_overlap: int = 100
    paragraph_separator: str = "\n\n"
    # ----- index config -----
    embedding_name: str = "text-embedding-3-small"
    # ----- retriever config -----
    query_mode: str = "hybrid"
    similarity_top_k: int = 10
    hybrid_top_k: int = 10
    alpha: float = 0.5
    # ----- query engine config -----
    query_llm_name: str = "gemini-3.1-flash-lite"
    evaluator_llm_name: str = "gpt-5.4"
    cutoff: float = 0.0
    query: str = "實驗室發表過的論文"

    def __post_init__(self) -> None:
        _validate_config(vars(self))
        # 未指定路徑時，由 site_id 動態產生預設路徑
        if self.webpages_data_folder_path is None:
            self.webpages_data_folder_path = _default_webpages_path(self.site_id)
        if self.qdrant_db_folder_path is None:
            self.qdrant_db_folder_path = _default_qdrant_db_path(self.site_id)
        if self.milvus_uri is None:
            self.milvus_uri = _default_milvus_uri(self.site_id)

    @classmethod
    def from_toml(
        cls,
        config_name: str = "default",
        **overrides,
    ):
        """從 TOML 設定檔建立 RAGConfig。"""
        return super().from_toml(config_name, **overrides)

    def _post_process_run_name(self, run_name: str) -> str:
        run_name = run_name.replace("/", "-")
        if run_name.find("-gemini") > 1:
            run_name = run_name.replace("-gemini", "", 1)
        return run_name


def _validate_config(config: dict[str, Any]) -> None:
    # ----- init config -----
    site_id = config.get("site_id", "")
    if not isinstance(site_id, str) or not site_id.strip():
        raise ConfigValidationError("site_id 必須是非空字串")

    webpages_data_folder_path = config.get("webpages_data_folder_path")

    if webpages_data_folder_path is not None:
        if not isinstance(webpages_data_folder_path, str):
            raise ConfigValidationError("webpages_data_folder_path 必須是字串")
        if not webpages_data_folder_path.strip():
            raise ConfigValidationError("webpages_data_folder_path 不可為空字串")

    # ----- vector store config -----
    qdrant_db_folder_path = config.get("qdrant_db_folder_path")
    vector_store_type = config.get("vector_store_type")

    if vector_store_type is not None and vector_store_type not in ("qdrant", "milvus"):
        raise ConfigValidationError("vector_store_type 必須是 'qdrant' 或 'milvus'")

    if qdrant_db_folder_path is not None:
        if not isinstance(qdrant_db_folder_path, str):
            raise ConfigValidationError("qdrant_db_folder_path 必須是字串")
        if not qdrant_db_folder_path.strip():
            raise ConfigValidationError("qdrant_db_folder_path 不可為空字串")

    hybrid_ranker = config.get("hybrid_ranker")

    if hybrid_ranker is not None:
        if hybrid_ranker not in ("RRFRanker", "WeightedRanker"):
            raise ConfigValidationError(
                "hybrid_ranker 必須是 'RRFRanker' 或 'WeightedRanker'"
            )

    hybrid_ranker_params = config.get("hybrid_ranker_params")

    if hybrid_ranker_params is not None:
        if not isinstance(hybrid_ranker_params, dict):
            raise ConfigValidationError("hybrid_ranker_params 必須是 dict")

        if "weights" in hybrid_ranker_params:
            weights = hybrid_ranker_params["weights"]
            if not isinstance(weights, list) or len(weights) != 2:
                raise ConfigValidationError("weights 必須是長度 2 的列表")
            for w in weights:
                if not isinstance(w, (int, float)):
                    raise ConfigValidationError("weights 元素必須為數值")

        if "k" in hybrid_ranker_params:
            k = hybrid_ranker_params["k"]
            if not isinstance(k, int):
                raise ConfigValidationError("hybrid_ranker_params.k 必須是整數")
            if k <= 0:
                raise ConfigValidationError("hybrid_ranker_params.k 必須大於 0")

        # 驗證通過後將 tomlkit 型別轉換為原生 Python 型別
        config["hybrid_ranker_params"] = _normalize_toml_types(hybrid_ranker_params)

    # ----- nodes config -----
    chunk_size = config.get("chunk_size")
    chunk_overlap = config.get("chunk_overlap")
    paragraph_separator = config.get("paragraph_separator")

    for value, field_name in (
        (chunk_size, "chunk_size"),
        (chunk_overlap, "chunk_overlap"),
    ):
        if value is not None:
            if not isinstance(value, int):
                raise ConfigValidationError(f"{field_name} 必須是整數")
            if value <= 0:
                raise ConfigValidationError(f"{field_name} 必須大於 0")

    if paragraph_separator is not None and not isinstance(paragraph_separator, str):
        raise ConfigValidationError("paragraph_separator 必須是字串")

    # ----- index config -----
    embedding_name = config.get("embedding_name")

    if embedding_name is not None:
        if not isinstance(embedding_name, str):
            raise ConfigValidationError("embedding_name 必須是字串")
        if not embedding_name.strip():
            raise ConfigValidationError("embedding_name 不可為空字串")

    # ----- retriever config -----
    similarity_top_k = config.get("similarity_top_k")
    query_mode = config.get("query_mode")
    hybrid_top_k = config.get("hybrid_top_k")
    alpha = config.get("alpha")

    if similarity_top_k is not None:
        if not isinstance(similarity_top_k, int):
            raise ConfigValidationError("similarity_top_k 必須是整數")
        if similarity_top_k <= 0:
            raise ConfigValidationError("similarity_top_k 必須大於 0")

    if query_mode is not None:
        if query_mode not in ("hybrid", "default"):
            raise ConfigValidationError("query_mode 必須是 'hybrid' 或 'default'")

    if hybrid_top_k is not None:
        if not isinstance(hybrid_top_k, int):
            raise ConfigValidationError("hybrid_top_k 必須是整數")
        if hybrid_top_k <= 0:
            raise ConfigValidationError("hybrid_top_k 必須大於 0")

    if alpha is not None:
        if not isinstance(alpha, (int, float)):
            raise ConfigValidationError("alpha 必須是數值")
        if not 0.0 <= float(alpha) <= 1.0:
            raise ConfigValidationError("alpha 必須介於 0.0 到 1.0")

    # ----- query engine config -----
    query_llm_name = config.get("query_llm_name")
    evaluator_llm_name = config.get("evaluator_llm_name")
    cutoff = config.get("cutoff")
    query = config.get("query")

    if query_llm_name is not None:
        if not isinstance(query_llm_name, str):
            raise ConfigValidationError("query_llm_name 必須是字串")
        if not query_llm_name.strip():
            raise ConfigValidationError("query_llm_name 不可為空字串")

    if evaluator_llm_name is not None:
        if not isinstance(evaluator_llm_name, str):
            raise ConfigValidationError("evaluator_llm_name 必須是字串")
        if not evaluator_llm_name.strip():
            raise ConfigValidationError("evaluator_llm_name 不可為空字串")

    if cutoff is not None:
        if not isinstance(cutoff, (int, float)):
            raise ConfigValidationError("cutoff 必須是數字")
        if not 0 <= float(cutoff) <= 1:
            raise ConfigValidationError("cutoff 必須介於 0 到 1")

    if query is not None:
        if not isinstance(query, str):
            raise ConfigValidationError("query 必須是字串")
        if not query.strip():
            raise ConfigValidationError("query 不可為空字串")
