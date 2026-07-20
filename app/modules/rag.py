import json
import logging
import os
import shutil
from typing import Any, Sequence

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
)
from llama_index.core.base.response.schema import Response
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
)
from llama_index.core.evaluation.base import EvaluationResult
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode, Document, NodeWithScore
from llama_index.core.utils import truncate_text
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.milvus.utils import (
    BGEM3SparseEmbeddingFunction,
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.configs.rag_config import (
    DEFALULT_COLLECTION_NAME,
    DEFAULT_MILVUS_DB_FOLDER_PATH,
    DEFAULT_QDRANT_DB_FOLER_PATH,
    DEFAULT_VECTOR_STORE_TYPE,
    WEBPAGES_DATA_FOLDER_PATH,
)
from utils.log_helper import log_session, log_source_title
from utils.rag_helper import (
    MarkdownDateExtractor,
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
    extract_sources_info,
)

logger = logging.getLogger(__name__)


EMBEDDING_DIM_MAP: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


FAITHFULNESS_EVAL_TEMPLATE = PromptTemplate(
    "Please tell if a given piece of information "
    "is supported by the context.\n"
    "You need to answer with either YES or NO, followed by a short reason.\n"
    "Answer YES if any of the context supports the information, even "
    "if most of the context is unrelated. "
    "If you answer YES or NO, add a second line starting with 'Reason:' "
    "and explain your decision briefly. "
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。 "
    "Some examples are provided below. \n\n"
    "Information: Apple pie is generally double-crusted.\n"
    "Context: An apple pie is a fruit pie in which the principal filling "
    "ingredient is apples. \n"
    "Apple pie is often served with whipped cream, ice cream "
    "('apple pie à la mode'), custard or cheddar cheese.\n"
    "It is generally double-crusted, with pastry both above "
    "and below the filling; the upper crust may be solid or "
    "latticed (woven of crosswise strips).\n"
    "Answer: YES\n"
    "Reason: The context explicitly says the pie is generally double-crusted.\n"
    "Information: Apple pies tastes bad.\n"
    "Context: An apple pie is a fruit pie in which the principal filling "
    "ingredient is apples. \n"
    "Apple pie is often served with whipped cream, ice cream "
    "('apple pie à la mode'), custard or cheddar cheese.\n"
    "It is generally double-crusted, with pastry both above "
    "and below the filling; the upper crust may be solid or "
    "latticed (woven of crosswise strips).\n"
    "Answer: NO\n"
    "Reason: The context describes the pie, but it does not say anything about taste.\n"
    "Information: {query_str}\n"
    "Context: {context_str}\n"
    "Answer: "
)

FAITHFULNESS_REFINE_TEMPLATE = PromptTemplate(
    "We want to understand if the following information is present "
    "in the context information: {query_str}\n"
    "We have provided an existing YES/NO answer: {existing_answer}\n"
    "We have the opportunity to refine the existing answer "
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "If the existing answer was already YES, still answer YES. "
    "If the information is present in the new context, answer YES. "
    "Otherwise answer NO.\n"
    "After YES or NO, add a new line starting with 'Reason:' and briefly "
    "explain the decision based on the available context.\n"
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。\n"
)

RELEVANCY_EVAL_TEMPLATE = PromptTemplate(
    "Please tell if the response for the query is in line with the context \n"
    "information provided.\n"
    "You need to answer with either YES or NO, followed by a short reason.\n"
    "Answer YES if the response for the query is in line with the context \n"
    "information, otherwise NO.\n"
    "After YES or NO, add a second line starting with 'Reason:' and explain \n"
    "your decision briefly.\n"
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。\n"
    "Query and Response: \n {query_str}\n"
    "Context: \n {context_str}\n"
    "Answer: "
)

RELEVANCY_REFINE_TEMPLATE = PromptTemplate(
    "We want to understand if the following query and response is in line with \n"
    "the context information: \n {query_str}\n"
    "We have provided an existing YES/NO answer: \n {existing_answer}\n"
    "We have the opportunity to refine the existing answer (only if needed) with \n"
    "some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "If the existing answer was already YES, still answer YES. If the information \n"
    "is present in the new context, answer YES. Otherwise answer NO.\n"
    "After YES or NO, add a new line starting with 'Reason:' and briefly explain \n"
    "the decision based on the available context.\n"
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。\n"
)


class Rag:
    def __init__(
        self,
        webpages_data_folder_path: str = WEBPAGES_DATA_FOLDER_PATH,
    ) -> None:
        # ===== init args =====
        self.webpages_data_folder_path = webpages_data_folder_path
        self.md_docs_folder_path = os.path.join(webpages_data_folder_path, "results")
        self.results_json_path = os.path.join(webpages_data_folder_path, "results.json")
        self.results_json: dict[str, Any] = self._load_results_json()

        # ===== internal state =====
        self.qdrant_client: QdrantClient | None = None
        self.vector_store: QdrantVectorStore | MilvusVectorStore | None = None
        self.index: VectorStoreIndex | None = None
        self.nodes: Sequence[BaseNode] | None = None
        self.retriever: VectorIndexRetriever | None = None
        self.query_engine: RetrieverQueryEngine | None = None

    def clean_vector_store(
        self,
        qdrant_db_folder_path: str | None = None,
        milvus_uri: str | None = None,
    ) -> None:
        if qdrant_db_folder_path and os.path.exists(qdrant_db_folder_path):
            shutil.rmtree(qdrant_db_folder_path)
            logger.info("Cleaned Qdrant vector store")

        if milvus_uri and os.path.exists(milvus_uri):
            shutil.rmtree(milvus_uri)
            logger.info("Cleaned Milvus vector store")

    def build_vector_store(
        self,
        vector_store_type: str = DEFAULT_VECTOR_STORE_TYPE,
        qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH,
        milvus_uri: str = DEFAULT_MILVUS_DB_FOLDER_PATH,
        collection_name: str = DEFALULT_COLLECTION_NAME,
        embedding_name: str = "text-embedding-3-small",
        overwrite: bool = True,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> None:
        if vector_store_type == "qdrant":
            os.makedirs(qdrant_db_folder_path, exist_ok=True)
            self.qdrant_client = QdrantClient(path=qdrant_db_folder_path)
            self.vector_store = QdrantVectorStore(
                collection_name,
                self.qdrant_client,
                index_doc_id=False,
                enable_hybrid=True,
                fastembed_sparse_model="Qdrant/bm25",
            )
        elif vector_store_type == "milvus":
            dim = EMBEDDING_DIM_MAP.get(embedding_name)

            if hybrid_ranker_params is None:
                if hybrid_ranker == "RRFRanker":
                    hybrid_ranker_params = {"k": 60}
                elif hybrid_ranker == "WeightedRanker":
                    hybrid_ranker_params = {"weights": [1.0, 0.5]}
                else:
                    raise ValueError(f"Unsupported hybrid_ranker: {hybrid_ranker}")

            # * MilvusLite search 須明確指定 output_fields 才能回傳節點完整資料
            self.vector_store = MilvusVectorStore(
                milvus_uri,
                collection_name=collection_name,
                overwrite=overwrite,
                dim=dim,
                output_fields=["_node_content", "_node_type"],
                enable_sparse=True,
                sparse_embedding_function=BGEM3SparseEmbeddingFunction(),
                hybrid_ranker=hybrid_ranker,
                hybrid_ranker_params=hybrid_ranker_params,
            )
        else:
            raise ValueError(f"Unsupported vector_store_type: {vector_store_type}")

        logger.info(
            f"Successfully built vector store "
            f"(type={vector_store_type}, hybrid_ranker={hybrid_ranker})"
        )

    def _load_results_json(self) -> dict[str, Any]:
        if os.path.exists(self.results_json_path):
            with open(self.results_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        raise FileNotFoundError(
            f"Results JSON file not found at {self.results_json_path}"
        )

    def _file_metadata(self, file_path: str) -> dict[str, Any]:
        """Extract file metadata for a given file path using instance results JSON.

        Injects ``page_type`` and ``description`` from the results.json ``metadata``
        sub-dictionary into the LlamaIndex Document metadata, so they are persisted
        to Qdrant and available for both pre-filtering and LLM context.
        """
        page_title = os.path.basename(file_path).replace(".md", "")
        page_info = self.results_json.get(page_title, {})
        page_metadata: dict[str, Any] = page_info.get("metadata", {})

        metadata: dict[str, Any] = {
            "page_title": page_title,
            "page_url": page_info.get("url", ""),
            "page_type": page_metadata.get("page_type", "general"),
            "description": page_metadata.get("description", ""),
        }

        return metadata

    def load_index(self, embedding_name: str = "text-embedding-3-small") -> None:
        if self.vector_store is None:
            raise RuntimeError("Vector store have not been built, cannot load index")

        embed_model = self._set_embed_model(embedding_name)
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store, embed_model, show_progress=True
        )

        logger.info("Successfully loaded index from vector store")

    def build_index(
        self,
        embedding_name: str = "text-embedding-3-small",
    ) -> None:
        if self.vector_store is None:
            raise RuntimeError("Vector store have not been built, cannot build index")
        if self.nodes is None:
            raise RuntimeError("Nodes have not been built, cannot build index")

        # * milvus vector store 使用 sparse embeddnig 時在這裡會造成畫面短暫凍結
        embed_model = self._set_embed_model(embedding_name)
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex(
            self.nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        logger.info("Successfully built index from nodes")

    def build_nodes(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        paragraph_separator: str = "\n\n",
    ) -> None:
        md_docs: list[Document] = SimpleDirectoryReader(
            self.md_docs_folder_path,
            exclude_empty=True,
            filename_as_id=True,
            required_exts=[".md"],
            file_metadata=self._file_metadata,
        ).load_data(show_progress=True)
        # for md_doc in md_docs: # debug
        #     print(md_doc.metadata)
        # return

        logger.info(f"Loading {len(md_docs)} Markdown Documents")

        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser.from_defaults(),
                MarkdownDateExtractor(),
                SentenceSplitter.from_defaults(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    paragraph_separator=paragraph_separator,
                ),
                MarkdownHeadingMergeParser(),
                MarkdownImageExtractor(),
            ]
        )
        self.nodes = pipeline.run(documents=md_docs, show_progress=True)
        logger.info(f"Pipeline produced {len(self.nodes)} nodes")
        # self._log_page_node_info(self.nodes, page_title="Prospective_Students") # debug

    @staticmethod
    def _log_page_node_info(
        nodes: Sequence[BaseNode], page_title: str
    ) -> None:  # debug
        counter = 0
        for node in nodes:
            if node.metadata.get("page_title") == page_title:
                counter += 1
                logger.debug("Node content:")
                logger.debug(node.get_content())
                logger.debug("")
                logger.debug("Node metadata:")
                logger.debug(node.get_metadata_str())
                logger.debug("-" * 90)
        logger.debug(f"Found {counter} nodes from {page_title}")

    def _set_embed_model(self, embedding_name):
        api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
        embed_model = OpenAIEmbedding(
            model=embedding_name,
            embed_batch_size=256,
            api_key=api_key,
        )
        return embed_model

    def build_retriever(
        self,
        query_mode: str = "hybrid",  # "default" or "hybrid"
        filter_dict: dict[str, str | int | tuple] | None = None,
        similarity_top_k: int = 10,
        hybrid_top_k: int = 10,
        alpha: float = 0.5,
    ) -> None:
        if self.index is None:
            raise RuntimeError("Index have not been built, cannot build retriever")

        filters: MetadataFilters | None = None
        if filter_dict:
            filter_list = []
            for key, entry in filter_dict.items():
                if isinstance(entry, tuple):
                    value, operator = entry
                else:
                    value, operator = entry, FilterOperator.EQ
                filter_list.append(
                    MetadataFilter(key=key, value=value, operator=operator)
                )
            filters = MetadataFilters(filters=filter_list)

        vector_store_query_mode = (
            VectorStoreQueryMode.HYBRID
            if query_mode == "hybrid"
            else VectorStoreQueryMode.DEFAULT
        )
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=similarity_top_k,
            filters=filters,
            vector_store_query_mode=vector_store_query_mode,
            hybrid_top_k=hybrid_top_k,
            alpha=alpha,
        )
        logger.info(f"Successfully built retriever (query mode={query_mode})")

    def _log_sources(self, source_nodes: Sequence[NodeWithScore]) -> None:
        log_session("Sources", style="blue")
        logger.info(f"Retrieved {len(source_nodes)} sources")
        for source_node in source_nodes:
            page_title, score, page_type = extract_sources_info(source_node)
            log_source_title(page_title, score, page_type)

            raw_content = source_node.node.get_content()
            format_content = truncate_text(raw_content, max_length=500)
            logger.info(format_content)

            # logger.debug(f"Node metadata: \n{source_node.node.get_metadata_str()}")

    # ? filter 在 retriever, 還有需要 query engine 嗎
    # TODO: 新增 retrieve method，retriever + similarity postprocessor
    def build_query_engine(
        self,
        llm_name: str = "gemini-3.1-flash-lite",
        cutoff: float = 0.0,
        query_mode: str = "hybrid",
    ) -> None:
        if self.retriever is None:
            raise RuntimeError(
                "Retriever have not been built, cannot build query engine"
            )

        if "gemini" in llm_name:
            api_key_name = "GEMINI_RAG_QUERY_ENGINE_API_KEY"
        elif "gpt" in llm_name:
            api_key_name = "OPENAI_RAG_QUERY_ENGINE_API_KEY"
        else:
            raise ValueError(f"Unsupported LLM name: {llm_name}")

        llm = self._set_llm(llm_name, api_key_name)
        response_synthesizer = get_response_synthesizer(llm)

        node_postprocessors = []
        if query_mode != "hybrid":
            node_postprocessors.append(
                SimilarityPostprocessor(similarity_cutoff=cutoff)
            )

        self.query_engine = RetrieverQueryEngine(
            self.retriever,
            response_synthesizer,
            node_postprocessors=node_postprocessors,
        )

        logger.info("Successfully built query engine")

    def _set_llm(self, llm_name: str, api_key_name: str) -> GoogleGenAI | OpenAI:
        api_key = os.getenv(api_key_name)

        if "gemini" in llm_name:
            llm = GoogleGenAI(
                model=llm_name,
                api_key=api_key,
            )
        elif "gpt" in llm_name:
            llm = OpenAI(
                model=llm_name,
                api_key=api_key,
            )

        return llm

    def query(self, query: str, log_sources: bool = False) -> Response:
        if self.query_engine is None:
            raise RuntimeError("RAG service have not been built, cannot execute query")

        logger.info(f"Query: {query}")
        response = self.query_engine.query(query)
        if isinstance(response, Response):
            logger.info(f"Response: {response.response}")
            if log_sources:
                self._log_sources(response.source_nodes)
            return response
        else:
            raise TypeError(
                f"Query engine returned unexpected response type: {type(response)}"
            )

    def evaluate(
        self,
        query: str,
        response: Response,
        llm_name: str = "gpt-5.4",  # gemini-3.1-pro-preview 每日限額太低
    ) -> tuple[EvaluationResult, EvaluationResult]:
        if "gemini" in llm_name:
            api_key_name = "GEMINI_RAG_EVALUATOR_API_KEY"
        elif "gpt" in llm_name:
            api_key_name = "OPENAI_RAG_EVALUATOR_API_KEY"
        else:
            raise ValueError(f"Unsupported LLM name: {llm_name}")

        llm = self._set_llm(llm_name, api_key_name)
        faithfulness_evaluator = FaithfulnessEvaluator(
            llm=llm,
            eval_template=FAITHFULNESS_EVAL_TEMPLATE,
            refine_template=FAITHFULNESS_REFINE_TEMPLATE,
        )
        faithfulness_result = faithfulness_evaluator.evaluate_response(
            response=response
        )
        self._log_evaluation_result("Faithfulness", faithfulness_result)

        relevancy_evaluator = RelevancyEvaluator(
            llm=llm,
            eval_template=RELEVANCY_EVAL_TEMPLATE,
            refine_template=RELEVANCY_REFINE_TEMPLATE,
        )
        relevancy_result = relevancy_evaluator.evaluate_response(
            query=query,
            response=response,
        )
        self._log_evaluation_result("Relevancy", relevancy_result)

        return faithfulness_result, relevancy_result

    def _log_evaluation_result(
        self, evaluation_type: str, evaluation_result: EvaluationResult
    ) -> None:
        log_session(f"{evaluation_type} Result", style="blue")
        logger.info(f"Passing: {evaluation_result.passing}")
        reason = None
        if evaluation_result.feedback:
            reason = evaluation_result.feedback.split("Reason:", 1)[-1].strip()
        logger.info(f"Reason: {reason}")

    def close(self) -> None:
        if self.qdrant_client is not None:
            self.qdrant_client.close()

        self.qdrant_client = None
        self.vector_store = None

    def override_init_config(self, **init_kwargs) -> None:
        self.webpages_data_folder_path = init_kwargs.get(
            "webpages_data_folder_path", self.webpages_data_folder_path
        )

        self.md_docs_folder_path = os.path.join(
            self.webpages_data_folder_path, "results"
        )
        self.results_json_path = os.path.join(
            self.webpages_data_folder_path, "results.json"
        )
        self.results_json = self._load_results_json()

        client: QdrantClient | None = self.qdrant_client
        if client is not None:
            client.close()

        self.qdrant_client = None
        self.vector_store = None
        self.index = None
        self.retriever = None
        self.query_engine = None
