import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self

from utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
    load_config_section_from_toml,
)

logger = logging.getLogger(__name__)

WEBPAGES_DATA_FOLDER_PATH = "data/webpages/prompt-v3"
DEFAULT_QDRANT_DB_FOLER_PATH = "data/rag/qdrant_db"
DEFAULT_CONFIG_FOLDER_PATH = "./config/rag"
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_VECTOR_STORE_CONFIG_SECTION = "vector_store"
DEFAULT_INDEX_CONFIG_SECTION = "index"
DEFAULT_QUERY_ENGINE_CONFIG_SECTION = "query_engine"

INIT_KEYS = {
    "webpages_data_folder_path",
    "force_rebuild",
}
VECTOR_STORE_KEYS = {
    "qdrant_db_folder_path",
    "collection_name",
}
INDEX_KEYS = {
    "embedding_model_name",
    "chunk_size",
    "chunk_overlap",
    "paragraph_separator",
}
QUERY_ENGINE_KEYS = {
    "llm_model_name",
    "top_k",
    "cutoff",
}
SECTIONS_TO_KEYS = {
    "init": INIT_KEYS,
    "vector_store": VECTOR_STORE_KEYS,
    "index": INDEX_KEYS,
    "query_engine": QUERY_ENGINE_KEYS,
}


@dataclass
class RagConfig:
    # ----- metadata (no default values)-----
    config_path: str
    # ----- init args -----
    webpages_data_folder_path: str = WEBPAGES_DATA_FOLDER_PATH
    force_rebuild: bool = False
    # ----- vector store args -----
    qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH
    collection_name: str = "webpages"
    # ----- index args -----
    embedding_model_name: str = "text-embedding-3-small"
    chunk_size: int = 800
    chunk_overlap: int = 100
    paragraph_separator: str = "\n\n"
    # ----- query engine args -----
    llm_model_name: str = "gemini-3.1-flash-lite"
    top_k: int = 5
    cutoff: float = 0.5
    # ----- metadata -----
    sections_to_keys: dict[str, set[str]] = field(
        default_factory=lambda: SECTIONS_TO_KEYS
    )

    def __post_init__(self) -> None:
        _validate_init_config(
            webpages_data_folder_path=self.webpages_data_folder_path,
            force_rebuild=self.force_rebuild,
        )
        _validate_vector_store_config(
            qdrant_db_folder_path=self.qdrant_db_folder_path,
            collection_name=self.collection_name,
        )
        _validate_index_config(
            embedding_model_name=self.embedding_model_name,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            paragraph_separator=self.paragraph_separator,
        )
        _validate_query_engine_config(
            llm_model_name=self.llm_model_name,
            top_k=self.top_k,
            cutoff=self.cutoff,
        )

    @classmethod
    def from_toml(
        cls,
        config_name: str = "default",
        init_config_section: str = DEFAULT_INIT_CONFIG_SECTION,
        vector_store_config_section: str = DEFAULT_VECTOR_STORE_CONFIG_SECTION,
        index_config_section: str = DEFAULT_INDEX_CONFIG_SECTION,
        query_engine_config_section: str = DEFAULT_QUERY_ENGINE_CONFIG_SECTION,
    ) -> Self:
        """從 TOML 設定檔建立 RagConfig。"""
        config_path = os.path.join(DEFAULT_CONFIG_FOLDER_PATH, f"{config_name}.toml")
        init_config = _load_init_config_from_toml(config_path, init_config_section)
        vector_store_config = _load_vector_store_config_from_toml(
            config_path, vector_store_config_section
        )
        index_config = _load_index_config_from_toml(config_path, index_config_section)
        query_engine_config = _load_query_engine_config_from_toml(
            config_path, query_engine_config_section
        )
        return cls(
            **init_config,
            **vector_store_config,
            **index_config,
            **query_engine_config,
            config_path=config_path,
        )

    def override_init_config(self, **overrides) -> None:
        """覆寫 init 參數並驗證。"""
        _override_init_config(vars(self), **overrides)

    def override_vector_store_config(self, **overrides) -> None:
        """覆寫 vector store 參數並驗證。"""
        _override_vector_store_config(vars(self), **overrides)

    def override_index_config(self, **overrides) -> None:
        """覆寫 index 參數並驗證。"""
        _override_index_config(vars(self), **overrides)

    def override_query_engine_config(self, **overrides) -> None:
        """覆寫 query engine 參數並驗證。"""
        _override_query_engine_config(vars(self), **overrides)

    @property
    def run_name(self) -> str:
        """根據 config TOML 中的註解生成 run name。"""
        if not self.config_path or not Path(self.config_path).is_file():
            return "default"

        commented_configs = filter_commented_configs(self.config_path, "run name")
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


def _validate_init_config(init_config: dict[str, Any] = {}, **init_kwargs) -> None:
    """驗證 init 參數型別與範圍。"""
    if init_config:
        webpages_data_folder_path = init_config.get("webpages_data_folder_path")
        force_rebuild = init_config.get("force_rebuild")
    else:
        webpages_data_folder_path = init_kwargs.get("webpages_data_folder_path")
        force_rebuild = init_kwargs.get("force_rebuild")

    if webpages_data_folder_path is not None:
        if not isinstance(webpages_data_folder_path, str):
            raise ConfigValidationError("webpages_data_folder_path 必須是字串")
        if not webpages_data_folder_path.strip():
            raise ConfigValidationError("webpages_data_folder_path 不可為空字串")

    if force_rebuild is not None and not isinstance(force_rebuild, bool):
        raise ConfigValidationError("force_rebuild 必須是布林值")


def _validate_vector_store_config(
    vector_store_config: dict[str, Any] = {}, **vector_store_kwargs
) -> None:
    """驗證 vector store 參數型別與範圍。"""
    if vector_store_config:
        qdrant_db_folder_path = vector_store_config.get("qdrant_db_folder_path")
        collection_name = vector_store_config.get("collection_name")
    else:
        qdrant_db_folder_path = vector_store_kwargs.get("qdrant_db_folder_path")
        collection_name = vector_store_kwargs.get("collection_name")

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


def _validate_index_config(index_config: dict[str, Any] = {}, **index_kwargs) -> None:
    """驗證 index 參數型別與範圍。"""
    if index_config:
        embedding_model_name = index_config.get("embedding_model_name")
        chunk_size = index_config.get("chunk_size")
        chunk_overlap = index_config.get("chunk_overlap")
        paragraph_separator = index_config.get("paragraph_separator")
    else:
        embedding_model_name = index_kwargs.get("embedding_model_name")
        chunk_size = index_kwargs.get("chunk_size")
        chunk_overlap = index_kwargs.get("chunk_overlap")
        paragraph_separator = index_kwargs.get("paragraph_separator")

    if embedding_model_name is not None:
        if not isinstance(embedding_model_name, str):
            raise ConfigValidationError("embedding_model_name 必須是字串")
        if not embedding_model_name.strip():
            raise ConfigValidationError("embedding_model_name 不可為空字串")

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


def _validate_query_engine_config(
    query_engine_config: dict[str, Any] = {}, **query_engine_kwargs
) -> None:
    """驗證 query engine 參數型別與範圍。"""
    if query_engine_config:
        llm_model_name = query_engine_config.get("llm_model_name")
        top_k = query_engine_config.get("top_k")
        cutoff = query_engine_config.get("cutoff")
    else:
        llm_model_name = query_engine_kwargs.get("llm_model_name")
        top_k = query_engine_kwargs.get("top_k")
        cutoff = query_engine_kwargs.get("cutoff")

    if llm_model_name is not None:
        if not isinstance(llm_model_name, str):
            raise ConfigValidationError("llm_model_name 必須是字串")
        if not llm_model_name.strip():
            raise ConfigValidationError("llm_model_name 不可為空字串")

    if top_k is not None:
        if not isinstance(top_k, int):
            raise ConfigValidationError("top_k 必須是整數")
        if top_k <= 0:
            raise ConfigValidationError("top_k 必須大於 0")

    if cutoff is not None:
        if not isinstance(cutoff, (int, float)):
            raise ConfigValidationError("cutoff 必須是數字")
        if not 0 <= float(cutoff) <= 1:
            raise ConfigValidationError("cutoff 必須介於 0 到 1")


def _load_init_config_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """從 TOML 讀取 init 參數。"""
    return load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=INIT_KEYS,
        unknown_keys_warning="Unknown init config keys will be ignored: %s",
    )


def _load_vector_store_config_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """從 TOML 讀取 vector store 參數。"""
    return load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=VECTOR_STORE_KEYS,
        unknown_keys_warning="Unknown vector store config keys will be ignored: %s",
    )


def _load_index_config_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """從 TOML 讀取 index 參數。"""
    return load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=INDEX_KEYS,
        unknown_keys_warning="Unknown index config keys will be ignored: %s",
    )


def _load_query_engine_config_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """從 TOML 讀取 query engine 參數。"""
    return load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=QUERY_ENGINE_KEYS,
        unknown_keys_warning="Unknown query engine config keys will be ignored: %s",
    )


def _override_init_config(
    init_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 init overrides 並輸出更新後的設定。"""
    for key, value in overrides.items():
        if key in INIT_KEYS:
            init_config[key] = value

    _validate_init_config(init_config)
    return init_config


def _override_vector_store_config(
    vector_store_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 vector store overrides 並輸出更新後的設定。"""
    for key, value in overrides.items():
        if key in VECTOR_STORE_KEYS:
            vector_store_config[key] = value

    _validate_vector_store_config(vector_store_config)
    return vector_store_config


def _override_index_config(
    index_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 index overrides 並輸出更新後的設定。"""
    for key, value in overrides.items():
        if key in INDEX_KEYS:
            index_config[key] = value

    _validate_index_config(index_config)
    return index_config


def _override_query_engine_config(
    query_engine_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 query engine overrides 並輸出更新後的設定。"""
    for key, value in overrides.items():
        if key in QUERY_ENGINE_KEYS:
            query_engine_config[key] = value

    _validate_query_engine_config(query_engine_config)
    return query_engine_config
