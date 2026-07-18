import logging
import os
from dataclasses import dataclass, field
from typing import Any, Self

from utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
    load_config_from_toml,
    override_config,
)

logger = logging.getLogger(__name__)

WEBPAGES_DATA_FOLDER_PATH = "data/webpages"
RAG_RESULTS_FOLDER_PATH = "data/rag/results"
DEFAULT_VECTOR_STORE_TYPE = "qdrant"
DEFALULT_COLLECTION_NAME = "webpages"
DEFAULT_QDRANT_DB_FOLER_PATH = os.path.join(RAG_RESULTS_FOLDER_PATH, "qdrant_db")
DEFAULT_MILVUS_DB_FOLDER_PATH = os.path.join(RAG_RESULTS_FOLDER_PATH, "milvus.db")
DEFAULT_CONFIG_FOLDER_PATH = "configs/rag"
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_VECTOR_STORE_CONFIG_SECTION = "vector_store"
DEFAULT_NODES_CONFIG_SECTION = "nodes"
DEFAULT_INDEX_CONFIG_SECTION = "index"
DEFAULT_RETRIEVER_CONFIG_SECTION = "retriever"
DEFAULT_QUERY_ENGINE_CONFIG_SECTION = "query_engine"

INIT_KEYS = {
    "webpages_data_folder_path",
}
VECTOR_STORE_KEYS = {
    "qdrant_db_folder_path",
    "collection_name",
    "vector_store_type",
    "milvus_uri",
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
    "llm_name",
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
class RagConfig:
    # ----- metadata (no default values)-----
    config_name: str
    # ----- init config -----
    webpages_data_folder_path: str = WEBPAGES_DATA_FOLDER_PATH
    # ----- vector store config -----
    vector_store_type: str = DEFAULT_VECTOR_STORE_TYPE
    qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH
    milvus_uri: str = DEFAULT_MILVUS_DB_FOLDER_PATH
    collection_name: str = DEFALULT_COLLECTION_NAME
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
    llm_name: str = "gemini-3.1-flash-lite"
    cutoff: float = 0.4
    query: str = "實驗室發表過的論文"
    # ----- metadata -----
    sections_to_keys: dict[str, set[str]] = field(
        default_factory=lambda: SECTIONS_TO_KEYS
    )

    def __post_init__(self) -> None:
        _validate_config(vars(self))

    @classmethod
    def from_toml(
        cls,
        config_name: str = "default",
        **overrides,
    ) -> Self:
        """從 TOML 設定檔建立 RagConfig。"""
        config_path = os.path.join(DEFAULT_CONFIG_FOLDER_PATH, f"{config_name}.toml")
        config = load_config_from_toml(config_path, SECTIONS_TO_KEYS)
        config = override_config(config, overrides, SECTIONS_TO_KEYS)
        config["config_name"] = config_name
        return cls(**config)

    @property
    def run_name(self) -> str:
        """根據 config TOML 中的註解生成 run name。"""
        config_path = os.path.join(
            DEFAULT_CONFIG_FOLDER_PATH, f"{self.config_name}.toml"
        )
        commented_configs = filter_commented_configs(config_path, "run name")
        if not commented_configs:
            return "default"

        run_name = ""
        for config in commented_configs:
            value = getattr(self, config, None)
            if value is not None:
                run_name += f"{config}-{value}_"
        run_name = run_name.rstrip("_").replace("/", "-")

        if run_name.find("-gemini") > 1:
            run_name = run_name.replace("-gemini", "", 1)

        return run_name


def _validate_config(config: dict[str, Any]) -> None:
    # ----- init config -----
    webpages_data_folder_path = config.get("webpages_data_folder_path")

    if webpages_data_folder_path is not None:
        if not isinstance(webpages_data_folder_path, str):
            raise ConfigValidationError("webpages_data_folder_path 必須是字串")
        if not webpages_data_folder_path.strip():
            raise ConfigValidationError("webpages_data_folder_path 不可為空字串")

    # ----- vector store config -----
    qdrant_db_folder_path = config.get("qdrant_db_folder_path")
    collection_name = config.get("collection_name")
    vector_store_type = config.get("vector_store_type")

    if vector_store_type is not None and vector_store_type not in ("qdrant", "milvus"):
        raise ConfigValidationError("vector_store_type 必須是 'qdrant' 或 'milvus'")

    if qdrant_db_folder_path is not None:
        if not isinstance(qdrant_db_folder_path, str):
            raise ConfigValidationError("qdrant_db_folder_path 必須是字串")
        if not qdrant_db_folder_path.strip():
            raise ConfigValidationError("qdrant_db_folder_path 不可為空字串")

    if collection_name is not None:
        if not isinstance(collection_name, str):
            raise ConfigValidationError("collection_name 必須是字串")
        if not collection_name.strip():
            raise ConfigValidationError("collection_name 不可為空字串")

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
    llm_name = config.get("llm_name")
    cutoff = config.get("cutoff")
    query = config.get("query")

    if llm_name is not None:
        if not isinstance(llm_name, str):
            raise ConfigValidationError("llm_name 必須是字串")
        if not llm_name.strip():
            raise ConfigValidationError("llm_name 不可為空字串")

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
