import argparse
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
from llama_index.core.extractors import DocumentContextExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    MarkdownNodeParser,
    get_leaf_nodes,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.llms.openai import OpenAI

load_dotenv()

# --- 基本設定 ---
INDEX_CONFIGS_PATH = "/home/george/website-copilot/config/index_configs.json"
DEFAULT_CONFIG_NAME = "balanced_v1"
BASE_PATH = "/home/george/website-copilot/data/test/rag_pipeline"
STORAGE_CONTEXT_DIR = os.path.join(BASE_PATH, "storage_context")
INGESTION_CACHE_DIR = os.path.join(BASE_PATH, "ingestion_cache")
QUESTION = "用中文介紹實驗室"
# QUESTION = "Introduce the lab in English."
CONTEXT_EXTRACT_MODEL = "gpt-4o-mini"
CONTEXT_KEY = "context"
CONTEXT_MAX_CONTEXT_LENGTH = 6000
CONTEXT_MAX_OUTPUT_TOKENS = 120


def main() -> None:
    args = parse_args()
    rebuild_index = args.rebuild_index

    setup_runtime()
    active_config = load_active_config(INDEX_CONFIGS_PATH, DEFAULT_CONFIG_NAME)

    print(f"Using experiment config: {DEFAULT_CONFIG_NAME}")
    print("Active config:")
    for key, value in active_config.items():
        print(f"  - {key}: {value}")
    print("-" * 30)

    chunk_sizes = active_config["chunk_sizes"]
    chunk_overlap = int(active_config["chunk_overlap"])
    include_metadata = bool(active_config["include_metadata"])
    similarity_top_k = int(active_config.get("similarity_top_k", 5))

    storage_context_persist_dir, ingest_cache_persist_dir = init_cache_paths(
        config_name=DEFAULT_CONFIG_NAME,
        chunk_sizes=chunk_sizes,
        include_metadata=include_metadata,
        similarity_top_k=similarity_top_k,
        rebuild_index=rebuild_index,
    )

    baseline_index_persist_dir = os.path.join(storage_context_persist_dir, "baseline")
    index_persist_dir = os.path.join(storage_context_persist_dir, "contextual")

    if rebuild_index:
        index, baseline_index = build_index(
            baseline_index_persist_dir=baseline_index_persist_dir,
            index_persist_dir=index_persist_dir,
            ingest_cache_persist_dir=ingest_cache_persist_dir,
            chunk_sizes=chunk_sizes,
            chunk_overlap=chunk_overlap,
            include_metadata=include_metadata,
        )
    else:
        baseline_index = load_index(
            persist_dir=baseline_index_persist_dir, index_type="baseline"
        )
        index = load_index(persist_dir=index_persist_dir, index_type="contextual")

        if baseline_index is None or index is None:
            print("Failed to load. Rebuilding indices...")
            index, baseline_index = build_index(
                baseline_index_persist_dir=baseline_index_persist_dir,
                index_persist_dir=index_persist_dir,
                ingest_cache_persist_dir=ingest_cache_persist_dir,
                chunk_sizes=chunk_sizes,
                chunk_overlap=chunk_overlap,
                include_metadata=include_metadata,
            )

    print("=" * 30)
    print("Q:", QUESTION)

    baseline_query_engine = build_query_engine(
        index=baseline_index,
        similarity_top_k=similarity_top_k,
    )
    baseline_response = baseline_query_engine.query(QUESTION)
    print_query_result("[A/B] Baseline (without context extractor)", baseline_response)
    print("=" * 30)

    query_engine = build_query_engine(index=index, similarity_top_k=similarity_top_k)
    contextual_response = query_engine.query(QUESTION)
    print_query_result(
        "[A/B] Contextualized (with context extractor)", contextual_response
    )


def parse_args() -> argparse.Namespace:
    """解析終端機參數。"""
    parser = argparse.ArgumentParser(description="Run RAG pipeline experiment")
    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Force rebuild index and clear cached index directories",
    )
    return parser.parse_args()


def setup_runtime() -> None:
    """初始化執行環境：設定第三方 logger 與 OpenAI API Key。"""
    for logger_name in ["httpx", "httpcore", "openai"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    api_key = os.getenv("OPENAI_LLAMA_INDEX_TEST_API_KEY")
    if not api_key:
        raise RuntimeError("請設定 OPENAI_LLAMA_INDEX_TEST_API_KEY 或 OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = api_key


def load_active_config(path: str, config_name: str) -> dict:
    """讀取索引設定檔並回傳指定 config。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Index config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        configs = json.load(f)

    if not isinstance(configs, dict) or not configs:
        raise ValueError(f"No configs found in {path}")

    if config_name not in configs:
        available_configs = ", ".join(sorted(configs.keys()))
        raise ValueError(
            f"Unknown INDEX_CONFIG: {config_name}. Available configs: {available_configs}"
        )

    return configs[config_name]


def init_cache_paths(
    config_name: str,
    chunk_sizes: list[int],
    include_metadata: bool,
    similarity_top_k: int,
    rebuild_index: bool,
) -> tuple[str, str]:
    """根據 config 產生索引與 ingestion cache 路徑。"""
    os.makedirs(STORAGE_CONTEXT_DIR, exist_ok=True)
    os.makedirs(INGESTION_CACHE_DIR, exist_ok=True)

    chunk_signature = "_".join(str(size) for size in chunk_sizes)
    metadata_signature = "mdtrue" if include_metadata else "mdfalse"
    experiment_signature = (
        f"{config_name}_h{chunk_signature}_{metadata_signature}_top{similarity_top_k}"
    )
    storage_context_persist_dir = os.path.join(
        STORAGE_CONTEXT_DIR, experiment_signature
    )
    ingest_cache_persist_dir = os.path.join(INGESTION_CACHE_DIR, experiment_signature)

    if rebuild_index:
        shutil.rmtree(ingest_cache_persist_dir, ignore_errors=True)
        shutil.rmtree(storage_context_persist_dir, ignore_errors=True)
        print(
            f"Force rebuild enabled: cleared cache directories for {experiment_signature}"
        )

    return storage_context_persist_dir, ingest_cache_persist_dir


def build_index(
    baseline_index_persist_dir: str,
    index_persist_dir: str,
    ingest_cache_persist_dir: str,
    chunk_sizes: list[int],
    chunk_overlap: int,
    include_metadata: bool,
) -> tuple[Any, Any | None]:
    """執行 ingestion pipeline 重新建立。"""
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
        documents=docs,
        docstore=SimpleDocumentStore(),
    )

    if os.path.exists(ingest_cache_persist_dir):
        pipeline.load(ingest_cache_persist_dir)
        all_nodes = list(pipeline.run())
        print(f"Loaded ingestion pipeline with cache from {ingest_cache_persist_dir}.")
    else:
        os.makedirs(ingest_cache_persist_dir, exist_ok=True)
        all_nodes = list(pipeline.run())
        pipeline.persist(ingest_cache_persist_dir)  # 先run再persist
        print(
            f"Created new ingestion pipeline and persisted to {ingest_cache_persist_dir}."
        )

    leaf_nodes = get_leaf_nodes(all_nodes)
    all_nodes_docstore = SimpleDocumentStore()
    all_nodes_docstore.add_documents(all_nodes)

    # baseline：不加 context extractor，直接用原始 leaf nodes。
    os.makedirs(baseline_index_persist_dir, exist_ok=True)
    baseline_storage_context = StorageContext.from_defaults(docstore=all_nodes_docstore)
    baseline_index = VectorStoreIndex(
        leaf_nodes,
        storage_context=baseline_storage_context,
    )
    baseline_index.storage_context.persist(baseline_index_persist_dir)
    print(f"Created new baseline index and persisted to {baseline_index_persist_dir}.")

    # context extractor：對 leaf nodes 執行 extractor，產生帶有額外 context 的節點，再建立索引。
    os.makedirs(index_persist_dir, exist_ok=True)
    all_docs_docstore = SimpleDocumentStore()
    all_docs_docstore.add_documents(docs)
    context_extractor = DocumentContextExtractor(
        docstore=all_docs_docstore,
        llm=OpenAI(model=CONTEXT_EXTRACT_MODEL),
        key=CONTEXT_KEY,
        max_context_length=CONTEXT_MAX_CONTEXT_LENGTH,
        max_output_tokens=CONTEXT_MAX_OUTPUT_TOKENS,
        oversized_document_strategy="warn",
    )
    context_pipeline = IngestionPipeline(transformations=[context_extractor])
    contextual_leaf_nodes = list(context_pipeline.run(nodes=leaf_nodes))
    storage_context = StorageContext.from_defaults(docstore=all_nodes_docstore)
    index = VectorStoreIndex(contextual_leaf_nodes, storage_context=storage_context)
    index.storage_context.persist(index_persist_dir)
    print(f"Created new index and persisted to {index_persist_dir}.")

    return index, baseline_index


def load_index(persist_dir: str, index_type: str) -> Any | None:
    """嘗試載入索引；若索引殘缺則清除後回傳 None。"""
    try:
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        loaded_index = load_index_from_storage(storage_context)
        print(f"Loaded {index_type} index from {persist_dir}.")
        return loaded_index
    except Exception as exc:
        print(f"Warning: failed to load {index_type} index from {persist_dir}: {exc}")
        shutil.rmtree(persist_dir, ignore_errors=True)
        print(f"Removed corrupted {index_type} index directory: {persist_dir}")
        return None


def build_query_engine(index: Any, similarity_top_k: int) -> RetrieverQueryEngine:
    """建立 AutoMergingRetriever 查詢引擎。"""
    base_retriever = index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        vector_retriever=base_retriever,
        storage_context=index.storage_context,
    )
    return RetrieverQueryEngine.from_args(retriever=retriever)


def print_query_result(title: str, response: Response | Any) -> None:
    print(title)
    if isinstance(response, Response):
        print("A:", response.response)
        print(f"共參考 {len(response.source_nodes)} 個資料來源。")
        print("-" * 30)
        print(response.get_formatted_sources(length=1000))
    else:
        print("Response:", response)


if __name__ == "__main__":
    main()
