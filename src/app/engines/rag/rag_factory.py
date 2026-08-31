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

from app.configs.rag_config import RAGConfig
from app.engines.rag.rag import RAG
from app.engines.rag.rag_eval_prompts import (
    FAITHFULNESS_EVAL_TEMPLATE,
    FAITHFULNESS_REFINE_TEMPLATE,
    RELEVANCY_EVAL_TEMPLATE,
    RELEVANCY_REFINE_TEMPLATE,
)
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
    def build_milvus(
        collection_name: str,
        milvus_uri: str,
        embedding_name: str,
        overwrite: bool = True,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> MilvusVectorStore:
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
            overwrite=overwrite,
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

    @staticmethod
    def build(
        collection_name: str,
        embedding_name: str,
        milvus_uri: str,
        overwrite: bool = True,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> MilvusVectorStore:
        return VectorStoreBuilder.build_milvus(
            collection_name=collection_name,
            milvus_uri=milvus_uri,
            embedding_name=embedding_name,
            overwrite=overwrite,
            hybrid_ranker=hybrid_ranker,
            hybrid_ranker_params=hybrid_ranker_params,
        )


class RAGBuilder:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config

    def build(self, rag: RAG | None = None) -> RAG:
        rag = rag or self._create_rag()
        self.build_to_retriever(rag)
        self.build_query_engine(rag)
        return rag

    def build_to_retriever(self, rag: RAG | None = None) -> RAG:
        rag = rag or self._create_rag()
        self.build_nodes(rag)
        self.build_vector_store(rag)
        self.build_index(rag)
        self.build_retriever(rag)
        return rag

    def build_reusable(self, rag: RAG, force_rebuild: bool = False) -> None:
        """建到 query engine 層級，視情況重建或載入既有 index。

        - force_rebuild=True 或 store 路徑不存在時重建。
        - 重建：clean → nodes → vector store → index。
        - 載入：build_vector_store(overwrite=False) → load_index。
        - 最後一律 build_retriever → build_query_engine。
        """
        rebuild = self._should_rebuild(force_rebuild)
        if rebuild:
            self.clean_vector_store(rag)
            self.build_nodes(rag)
            self.build_vector_store(rag)
            self.build_index(rag)
        else:
            self.build_vector_store(rag, overwrite=False)
            # Milvus 重用既有 collection 時，需手動載入（ released → loaded ）
            if self.config.vector_store_type == "milvus":
                assert rag.vector_store is not None
                rag.vector_store.client.load_collection(
                    rag.vector_store.collection_name
                )
            self.load_index(rag)

        self.build_retriever(rag)
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

    def build_vector_store(self, rag: RAG, overwrite: bool = True) -> None:
        vector_store = VectorStoreBuilder.build(
            collection_name=self.config.site_id,
            embedding_name=self.config.embedding_name,
            milvus_uri=self.config.milvus_uri,
            overwrite=overwrite,
            hybrid_ranker=self.config.hybrid_ranker,
            hybrid_ranker_params=self.config.hybrid_ranker_params,
        )
        rag.vector_store = vector_store
        logger.info(
            "Successfully built vector store (type=%s, hybrid_ranker=%s)",
            self.config.vector_store_type,
            self.config.hybrid_ranker,
        )

    def clean_vector_store(self, rag: RAG) -> None:
        VectorStoreBuilder.clean_milvus(self.config.milvus_uri)

    def build_index(self, rag: RAG) -> None:
        if rag.vector_store is None:
            raise RuntimeError("Vector store have not been built, cannot build index")
        if rag.nodes is None:
            raise RuntimeError("Nodes have not been built, cannot build index")

        embed_model = self._set_embed_model(self.config.embedding_name)
        storage_context = StorageContext.from_defaults(vector_store=rag.vector_store)
        rag.index = VectorStoreIndex(
            rag.nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        logger.info("Successfully built index from nodes")

    def load_index(self, rag: RAG) -> None:
        if rag.vector_store is None:
            raise RuntimeError("Vector store have not been built, cannot load index")

        embed_model = self._set_embed_model(self.config.embedding_name)
        rag.index = VectorStoreIndex.from_vector_store(
            rag.vector_store, embed_model, show_progress=True
        )
        logger.info("Successfully loaded index from vector store")

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
        logger.info(
            f"Successfully built retriever (query mode={self.config.query_mode})"
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

        logger.info("Successfully built query engine")

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
        api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
        return OpenAIEmbedding(
            model=embedding_name, embed_batch_size=256, api_key=api_key
        )

    def _create_rag(self) -> RAG:
        assert self.config.webpages_data_folder_path is not None
        return RAG(webpages_data_folder_path=self.config.webpages_data_folder_path)
