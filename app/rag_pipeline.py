import json
import logging
import os
import shutil
from typing import Any

from dotenv import load_dotenv
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.base.response.schema import Response
from llama_index.core.ingestion import IngestionCache, IngestionPipeline
from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    MarkdownNodeParser,
    get_leaf_nodes,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore

load_dotenv()

# --- 基本設定 ---
INDEX_CONFIGS_PATH = "/home/george/website-copilot/config/index_configs.json"
DEFAULT_CONFIG_NAME = "balanced_v1"
BASE_PATH = "/home/george/website-copilot/data/test/rag_pipeline"
STORAGE_CONTEXT_DIR = os.path.join(BASE_PATH, "storage_context")
INGESTION_CACHE_DIR = os.path.join(BASE_PATH, "ingestion_cache")
QUESTION = "用中文介紹實驗室"
FORCE_REBUILD = True


def configure_logging() -> None:
    """降低第三方 HTTP 請求日誌等級，避免干擾終端輸出。"""
    for logger_name in ["httpx", "httpcore", "openai"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def configure_openai_api_key() -> None:
    """從環境變數載入 API Key，並寫入 OPENAI_API_KEY。"""
    api_key = os.getenv("OPENAI_LLAMA_INDEX_TEST_API_KEY")
    if not api_key:
        raise RuntimeError("請設定 OPENAI_LLAMA_INDEX_TEST_API_KEY 或 OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = api_key


def load_index_configs(path: str) -> dict[str, dict]:
    """讀取索引設定檔。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Index config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        configs = json.load(f)

    if not isinstance(configs, dict) or not configs:
        raise ValueError(f"No configs found in {path}")

    return configs


def resolve_active_config(configs: dict[str, dict], config_name: str) -> dict:
    """驗證並取得目前要使用的 config。"""
    if config_name not in configs:
        available_configs = ", ".join(sorted(configs.keys()))
        raise ValueError(
            f"Unknown INDEX_CONFIG: {config_name}. Available configs: {available_configs}"
        )
    return configs[config_name]


def build_paths(
    config_name: str,
    chunk_sizes: list[int],
    include_metadata: bool,
    similarity_top_k: int,
) -> tuple[str, str]:
    """根據 config 產生索引與 ingestion cache 路徑。"""
    chunk_signature = "_".join(str(size) for size in chunk_sizes)
    metadata_signature = "mdtrue" if include_metadata else "mdfalse"
    experiment_signature = (
        f"{config_name}_h{chunk_signature}_{metadata_signature}_top{similarity_top_k}"
    )
    persist_dir = os.path.join(STORAGE_CONTEXT_DIR, f"storage_{experiment_signature}")
    cache_path = os.path.join(
        INGESTION_CACHE_DIR, f"ingest_cache_{experiment_signature}.json"
    )
    return persist_dir, cache_path


def load_or_build_index(
    persist_dir: str,
    cache_path: str,
    chunk_sizes: list[int],
    chunk_overlap: int,
    include_metadata: bool,
    force_rebuild: bool,
) -> Any:
    """載入既有索引；若不存在則執行 ingestion pipeline 重新建立。"""
    if force_rebuild and os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        print(f"Removed existing index: {persist_dir}")

    if os.path.exists(persist_dir):
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        print(f"Loaded index from {persist_dir}.")
        return load_index_from_storage(storage_context)

    # 優先使用既有 cache，減少重複 ingestion 成本。
    if os.path.exists(cache_path):
        ingest_cache = IngestionCache.from_persist_path(cache_path)
        print(f"Loaded ingestion cache from {cache_path}.")
    else:
        ingest_cache = IngestionCache()
        print("No existing ingestion cache found. Starting with a new cache.")

    docs = SimpleDirectoryReader(
        input_dir="/home/george/website-copilot/data/test/webpage_enhanced_markdown",
        required_exts=[".md"],
    ).load_data()

    pipeline = IngestionPipeline(
        transformations=[
            MarkdownNodeParser(),
            HierarchicalNodeParser.from_defaults(
                chunk_sizes=chunk_sizes,
                chunk_overlap=chunk_overlap,
                include_metadata=include_metadata,
            ),
        ],
        cache=ingest_cache,
    )

    all_nodes = list(pipeline.run(documents=docs))
    leaf_nodes = get_leaf_nodes(all_nodes)

    docstore = SimpleDocumentStore()
    docstore.add_documents(all_nodes)

    storage_context = StorageContext.from_defaults(docstore=docstore)
    index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)
    index.storage_context.persist(persist_dir)
    pipeline.cache.persist(cache_path)

    print(f"Created new index and persisted to {persist_dir}.")
    return index


def build_query_engine(index: Any, similarity_top_k: int) -> RetrieverQueryEngine:
    """建立 AutoMergingRetriever 查詢引擎。"""
    base_retriever = index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        vector_retriever=base_retriever,
        storage_context=index.storage_context,
    )
    return RetrieverQueryEngine.from_args(retriever=retriever)


def main() -> None:
    configure_logging()
    configure_openai_api_key()

    os.makedirs(STORAGE_CONTEXT_DIR, exist_ok=True)
    os.makedirs(INGESTION_CACHE_DIR, exist_ok=True)

    configs = load_index_configs(INDEX_CONFIGS_PATH)
    active_config = resolve_active_config(configs, DEFAULT_CONFIG_NAME)

    chunk_sizes = active_config["chunk_sizes"]
    chunk_overlap = int(active_config["chunk_overlap"])
    include_metadata = bool(active_config["include_metadata"])
    similarity_top_k = int(active_config.get("similarity_top_k", 5))

    persist_dir, cache_path = build_paths(
        config_name=DEFAULT_CONFIG_NAME,
        chunk_sizes=chunk_sizes,
        include_metadata=include_metadata,
        similarity_top_k=similarity_top_k,
    )

    print(f"Using experiment config: {DEFAULT_CONFIG_NAME}")
    print("Active config:")
    for key, value in active_config.items():
        print(f"  - {key}: {value}")

    index = load_or_build_index(
        persist_dir=persist_dir,
        cache_path=cache_path,
        chunk_sizes=chunk_sizes,
        chunk_overlap=chunk_overlap,
        include_metadata=include_metadata,
        force_rebuild=FORCE_REBUILD,
    )

    query_engine = build_query_engine(index=index, similarity_top_k=similarity_top_k)

    response = query_engine.query(QUESTION)
    print("=" * 30)
    print("Q:", QUESTION)
    if isinstance(response, Response):
        print("A:", response.response)
        print(f"共參考 {len(response.source_nodes)} 個資料來源。")
        print("=" * 30)
        print(response.get_formatted_sources(length=1000))
    else:
        print("Response:", response)


if __name__ == "__main__":
    main()
