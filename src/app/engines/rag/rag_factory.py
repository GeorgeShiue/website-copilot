import logging
import os
import shutil
from functools import partial
from typing import Any

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
)
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode, Document
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.milvus.utils import (
    BGEM3SparseEmbeddingFunction,
)
from rich.table import Table

from app.configs.rag_config import RAGConfig
from app.engines.rag import RAG
from app.engines.rag.rag_eval_prompts import (
    FAITHFULNESS_EVAL_TEMPLATE,
    FAITHFULNESS_REFINE_TEMPLATE,
    RELEVANCY_EVAL_TEMPLATE,
    RELEVANCY_REFINE_TEMPLATE,
)
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
from utils.log_helper import log_run_time, log_session, print_log
from utils.rag_helper import (
    MarkdownDateExtractor,
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
    build_filters,
    create_llm,
)

logger = logging.getLogger(__name__)

EMBEDDING_DIM_MAP: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


class NodePipelineBuilder:
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        paragraph_separator: str = "\n\n",
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.paragraph_separator = paragraph_separator
        self.last_doc_count = 0

    @staticmethod
    def _build_file_metadata(
        results_json: dict[str, Any], file_path: str, site_id: str
    ) -> dict[str, Any]:
        page_title = os.path.basename(file_path).replace(".md", "")
        page_info = results_json.get(page_title, {})
        page_metadata: dict[str, Any] = page_info.get("metadata", {})

        file_metadata: dict[str, Any] = {
            "page_title": page_title,
            "page_url": page_info.get("url", ""),
            "page_type": page_metadata.get("page_type", "general"),
            "published_date": page_metadata.get("published_date", ""),
            "description": page_metadata.get("description", ""),
            "site_id": site_id,
        }

        return file_metadata

    def build(
        self,
        md_folder_path: str,
        results_json: dict[str, Any],
        site_id: str,
    ) -> list[BaseNode]:
        if not os.path.isdir(md_folder_path):
            raise FileNotFoundError(f"Markdown folder not found: {md_folder_path}")

        file_metadata_fn = partial(
            self._build_file_metadata, results_json, site_id=site_id
        )

        try:
            md_docs: list[Document] = SimpleDirectoryReader(
                md_folder_path,
                exclude_empty=True,
                filename_as_id=True,
                required_exts=[".md"],
                file_metadata=file_metadata_fn,
            ).load_data(show_progress=True)
        except ValueError:
            logger.info(
                "No .md files found in %s, returning empty list", md_folder_path
            )
            return []
        self.last_doc_count = len(md_docs)
        logger.info("Loading %d Markdown Documents", len(md_docs))

        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser.from_defaults(),
                MarkdownDateExtractor(),
                SentenceSplitter.from_defaults(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    paragraph_separator=self.paragraph_separator,
                ),
                MarkdownHeadingMergeParser(),
                MarkdownImageExtractor(),
            ]
        )
        nodes = pipeline.run(documents=md_docs, show_progress=True)
        logger.info("Pipeline produced %d nodes", len(nodes))

        return list(nodes)


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
    def clean_milvus(milvus_uri: str | None) -> None:
        if milvus_uri and os.path.exists(milvus_uri):
            if os.path.isdir(milvus_uri):
                shutil.rmtree(milvus_uri)
            else:
                os.remove(milvus_uri)
            logger.info("Cleaned Milvus vector store: %s", milvus_uri)

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
        clean_milvus() 整檔刪除，讓這裡等同於全新建立。
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


class RAGBuilder:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config
        self._build_stats: dict[str, str] = {}

    def build_to_vector_store(self, rag: RAG, force_rebuild: bool = False) -> None:
        """建到 index 層級，視情況重建或載入既有 index。不含 retriever／query engine。

        - force_rebuild=True 或 store 路徑不存在時重建。
        - 重建：clean（整檔刪除）→ nodes → vector store → index。
        - 載入：build_vector_store（沿用既有 collection）→ load_index。
        """
        self._build_stats = {}
        rebuild = self._should_rebuild(force_rebuild)
        if rebuild:
            # record=False：細部步驟只印耗時，不進入 main workflow 的階段摘要
            with log_run_time("Clean vector store", record=False):
                self.clean_vector_store(rag)
            with log_run_time("Build nodes", record=False):
                self.build_nodes(rag)
            with log_run_time("Build vector store", record=False):
                self.build_vector_store(rag)
            with log_run_time("Build index", record=False):
                self.build_index(rag)
        else:
            self.build_vector_store(rag)
            # Milvus 重用既有 collection 時，需手動載入（ released → loaded ）
            if self.config.vector_store_type == "milvus":
                assert rag.vector_store is not None
                rag.vector_store.client.load_collection(
                    rag.vector_store.collection_name
                )
            self.load_index(rag)

        log_session("RAG Build Stats", style="green")
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        for metric, value in self._build_stats.items():
            table.add_row(metric, value)
        print_log(table)

    def build_to_retriever(self, rag: RAG, force_rebuild: bool = False) -> None:
        """建到 retriever 層級：build_to_vector_store → build_retriever。不含 query engine。"""
        self.build_to_vector_store(rag, force_rebuild=force_rebuild)
        self.build_retriever(rag)

    def build_to_query_engine(self, rag: RAG, force_rebuild: bool = False) -> None:
        """建到 query engine 層級：build_to_retriever → build_query_engine。"""
        self.build_to_retriever(rag, force_rebuild=force_rebuild)
        self.build_query_engine(rag)

    def _should_rebuild(self, force_rebuild: bool) -> bool:
        """決定是否需要重建 vector store / index。

        force_rebuild=True 或 store 路徑不存在時重建。
        """
        if force_rebuild:
            return True
        assert self.config.milvus_uri is not None
        return not os.path.exists(self.config.milvus_uri)

    def build_nodes(self, rag: RAG) -> None:
        builder = NodePipelineBuilder(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            paragraph_separator=self.config.paragraph_separator,
        )
        rag.nodes = builder.build(
            md_folder_path=rag.md_docs_folder_path,
            results_json=rag.results_json,
            site_id=self.config.site_id,
        )
        self._build_stats["Documents loaded"] = str(builder.last_doc_count)
        self._build_stats["Nodes produced"] = str(len(rag.nodes))

    def build_vector_store(self, rag: RAG) -> None:
        assert self.config.milvus_uri is not None
        logger.info(
            "Building Milvus vector store (sparse embedding: BGE-M3, hybrid_ranker=%s)",
            self.config.hybrid_ranker,
        )
        rag.vector_store = VectorStoreBuilder.build(
            collection_name=self.config.site_id,
            embedding_name=self.config.embedding_name,
            milvus_uri=self.config.milvus_uri,
            hybrid_ranker=self.config.hybrid_ranker,
            hybrid_ranker_params=self.config.hybrid_ranker_params,
        )

    def clean_vector_store(self, rag: RAG) -> None:
        VectorStoreBuilder.clean_milvus(self.config.milvus_uri)

    def build_index(self, rag: RAG) -> None:
        if rag.vector_store is None:
            raise RuntimeError("Vector store have not been built, cannot build index")
        if rag.nodes is None:
            raise RuntimeError("Nodes have not been built, cannot build index")

        logger.info(
            "Building index (dense embedding: %s, nodes=%d)",
            self.config.embedding_name,
            len(rag.nodes),
        )
        embed_model = self._set_embed_model(self.config.embedding_name)
        storage_context = StorageContext.from_defaults(vector_store=rag.vector_store)
        rag.index = VectorStoreIndex(
            rag.nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        self._build_stats["Index nodes"] = str(len(rag.nodes))

    def load_index(self, rag: RAG) -> None:
        if rag.vector_store is None:
            raise RuntimeError("Vector store have not been built, cannot load index")

        embed_model = self._set_embed_model(self.config.embedding_name)
        rag.index = VectorStoreIndex.from_vector_store(
            rag.vector_store, embed_model, show_progress=True
        )
        self._build_stats["Index nodes"] = "loaded from existing vector store"

    def build_retriever(
        self, rag: RAG, filter_dict: dict[str, Any] | None = None
    ) -> None:
        if rag.index is None:
            raise RuntimeError("Index have not been built, cannot build retriever")

        filters = build_filters(filter_dict)
        if filter_dict:
            logger.info(f"Building retriever with filters: {filter_dict}")

        vector_store_query_mode = (
            VectorStoreQueryMode.HYBRID
            if self.config.query_mode == "hybrid"
            else VectorStoreQueryMode.DEFAULT
        )
        rag.retriever = VectorIndexRetriever(
            index=rag.index,
            similarity_top_k=self.config.similarity_top_k,
            filters=filters,
            vector_store_query_mode=vector_store_query_mode,
            hybrid_top_k=self.config.hybrid_top_k,
            alpha=self.config.alpha,
        )

    def build_query_engine(self, rag: RAG) -> None:
        if rag.retriever is None:
            raise RuntimeError(
                "Retriever have not been built, cannot build query engine"
            )

        llm = create_llm(self.config.query_llm_name)
        response_synthesizer = get_response_synthesizer(llm)

        node_postprocessors = []
        if self.config.query_mode != "hybrid":
            node_postprocessors.append(
                SimilarityPostprocessor(similarity_cutoff=self.config.cutoff)
            )

        rag.query_engine = RetrieverQueryEngine(
            rag.retriever,
            response_synthesizer,
            node_postprocessors=node_postprocessors,
        )

    def build_evaluators(self, rag: RAG) -> None:
        """建立 Faithfulness / Relevancy evaluator 並注入 rag.evaluators。"""
        llm = create_llm(self.config.evaluator_llm_name, "evaluator")
        faithfulness_evaluator = FaithfulnessEvaluator(
            llm=llm,
            eval_template=FAITHFULNESS_EVAL_TEMPLATE,
            refine_template=FAITHFULNESS_REFINE_TEMPLATE,
        )
        relevancy_evaluator = RelevancyEvaluator(
            llm=llm,
            eval_template=RELEVANCY_EVAL_TEMPLATE,
            refine_template=RELEVANCY_REFINE_TEMPLATE,
        )
        rag.evaluators = (faithfulness_evaluator, relevancy_evaluator)
        logger.info(
            "Successfully built evaluators (llm=%s)",
            self.config.evaluator_llm_name,
        )

    @staticmethod
    def _set_embed_model(embedding_name: str) -> OpenAIEmbedding:
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIEmbedding(
            model=embedding_name, embed_batch_size=256, api_key=api_key
        )


def create_rag(
    config_name: str = "default",
    force_rebuild: bool = False,
    webpages_data_use_latest_results: bool = False,
    run_manager: RunManager | None = None,
    build_query_engine: bool = True,
    data_manager: DataManager | None = None,
    config: RAGConfig | None = None,
    **config_overrides,
) -> RAG:
    """建立並建構 RAG 實例。僅執行建構流程，不包含 query 步驟。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.toml）。config 為
            None 時才會用它從 toml 解析。
        force_rebuild: 是否強制重建向量庫。
        webpages_data_use_latest_results: 是否使用最新的 webpage 資料。
        run_manager: 呼叫端已建立的 RunManager（可選）。傳入時向量庫會建到
            該 run 的 results/ 目錄下；None 時使用 config 的預設持久化路徑。
        build_query_engine: 是否建到 retriever／query engine 層級；
            False 時僅建到 vector store／index 層級。
        data_manager: DataManager 實例（可選，用於解決 webpages 資料路徑）。
        config: 呼叫端已建立的 RAGConfig（可選）。傳入時直接沿用，不再重新
            解析 toml；此時 config_name／**config_overrides 會被忽略。
        **config_overrides: RAGConfig 覆寫值（含 site_id），僅在 config 為
            None 時生效。

    Returns:
        已建構的 RAG 實例（呼叫端負責 close）。
    """
    if config is None:
        config = RAGConfig.from_toml(config_name, **config_overrides)

    # ----- 解決 webpages 資料路徑（如有需要可覆蓋 config 預設值）-----
    if webpages_data_use_latest_results:
        if data_manager is None:
            raise ValueError(
                "data_manager is required when webpages_data_use_latest_results=True"
            )
        log_session("Finding Latest Webpages Data", style="cyan")
        webpages_data_folder_path = data_manager.get_webpages_path(config.site_id)
        config.webpages_data_folder_path = webpages_data_folder_path

    # ----- 解決向量庫存放位置（預設位置 vs 呼叫端 run 的 results/）-----
    if run_manager is not None:
        config.milvus_uri = os.path.join(run_manager.results_folder_path, "milvus.db")

    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")
    builder = RAGBuilder(config)
    if build_query_engine:
        log_session("Building RAG to Query Engine", style="cyan")
        builder.build_to_query_engine(rag, force_rebuild=force_rebuild)
    else:
        log_session("Building RAG to Vector Store", style="cyan")
        builder.build_to_vector_store(rag, force_rebuild=force_rebuild)
    rag.milvus_uri = config.milvus_uri

    return rag
