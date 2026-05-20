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
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.rag_config import (
    DEFAULT_QDRANT_DB_FOLER_PATH,
    WEBPAGES_DATA_FOLDER_PATH,
)
from utils.log_helper import log_session
from utils.rag_helper import (
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
    format_sources_text,
)

logger = logging.getLogger(__name__)


class Rag:
    def __init__(
        self,
        webpages_data_folder_path: str = WEBPAGES_DATA_FOLDER_PATH,
        force_rebuild: bool = False,
    ) -> None:
        # ===== init args =====
        self.webpages_data_folder_path = webpages_data_folder_path
        self.force_rebuild = force_rebuild

        # ===== internal state =====
        self.md_docs_folder_path = os.path.join(webpages_data_folder_path, "results")
        self.results_json_path = os.path.join(webpages_data_folder_path, "results.json")
        self.results_json: dict[str, Any] = self._load_results_json()
        self.vector_store_exist = False

        self.client: QdrantClient | None = None
        self.vector_store: QdrantVectorStore | None = None
        self.index: VectorStoreIndex | None = None
        self.retriever: VectorIndexRetriever | None = None
        self.query_engine: RetrieverQueryEngine | None = None

    def build_vector_store(
        self,
        qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH,
        collection_name: str = "webpages",
    ) -> None:
        if os.path.exists(qdrant_db_folder_path):
            if self.force_rebuild:
                shutil.rmtree(qdrant_db_folder_path)  # * 清理既存的 Vector Store
                logger.info("Successfully cleaned existing vector store")
            else:
                self.vector_store_exist = True

        self.client = QdrantClient(path=qdrant_db_folder_path)
        self.vector_store = QdrantVectorStore(
            collection_name, self.client, index_doc_id=False
        )

        if self.vector_store_exist:
            logger.info("Successfully loaded vector store")
        else:
            logger.info("Successfully built vector store")

    def _load_results_json(self) -> dict[str, Any]:
        if os.path.exists(self.results_json_path):
            with open(self.results_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        raise FileNotFoundError(
            f"Results JSON file not found at {self.results_json_path}"
        )

    def _file_metadata(self, file_path: str) -> dict[str, Any]:
        """Extract file metadata for a given file path using instance results JSON."""
        page_title = os.path.basename(file_path).replace(".md", "")
        page_info = self.results_json.get(page_title, {})

        metadata: dict[str, Any] = {
            "page_title": page_title,
            "page_url": page_info.get("url", ""),
        }

        return metadata

    def build_index(
        self,
        embedding_model_name: str = "text-embedding-3-small",
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        paragraph_separator: str = "\n\n",
    ) -> None:
        if self.vector_store is None:
            raise RuntimeError("Vector store is not initialized, cannot build index")
        embed_model = self._set_embed_model(embedding_model_name)

        if not self.force_rebuild and self.vector_store_exist:
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model, show_progress=True
            )
            logger.info("Successfully built index from vector store")
            return

        md_docs: list[Document] = SimpleDirectoryReader(
            self.md_docs_folder_path,
            exclude_empty=True,
            filename_as_id=True,
            required_exts=[".md"],
            file_metadata=self._file_metadata,
        ).load_data(show_progress=True)

        logger.info(f"Loading {len(md_docs)} Markdown Documents")
        logger.info("-" * 90)
        # for md_doc in md_docs: # debug
        #     print(md_doc.metadata)
        # return

        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser.from_defaults(),
                SentenceSplitter.from_defaults(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    paragraph_separator=paragraph_separator,
                ),
                MarkdownHeadingMergeParser(),
                MarkdownImageExtractor(),
            ]
        )

        nodes = pipeline.run(documents=md_docs, show_progress=True)
        logger.info(f"Pipeline produced {len(nodes)} nodes")
        logger.info("-" * 90)
        # self._log_page_node_info(nodes, page_title="Prospective_Students") # debug
        # print("-" * 90)

        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        logger.info("Successfully built index from nodes")

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

    def _set_embed_model(self, embedding_model_name):
        api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
        embed_model = OpenAIEmbedding(
            model=embedding_model_name,
            embed_batch_size=256,
            api_key=api_key,
        )
        return embed_model

    def build_retriever(self, top_k: int = 5) -> None:
        if self.index is None:
            raise RuntimeError("Index is not initialized, cannot build retriever")
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k,
        )
        logger.info("Successfully built retriever")

    def build_query_engine(
        self,
        llm_model_name: str = "gemini-3.1-flash-lite",
        cutoff: float = 0.5,
    ) -> None:
        if self.retriever is None:
            raise RuntimeError(
                "Retriever is not initialized, cannot build query engine"
            )

        llm = self._set_llm(llm_model_name)
        response_synthesizer = get_response_synthesizer(llm)
        similarity_postprocessor = SimilarityPostprocessor(similarity_cutoff=cutoff)
        self.query_engine = RetrieverQueryEngine(
            self.retriever,
            response_synthesizer,
            node_postprocessors=[similarity_postprocessor],
        )

        logger.info("Successfully built query engine")

    def _set_llm(self, llm_model_name: str) -> GoogleGenAI:
        api_key = os.getenv("GEMINI_RAG_QUERY_ENGINE_API_KEY")
        llm = GoogleGenAI(
            model=llm_model_name,
            api_key=api_key,
        )
        return llm

    def query(self, query: str, log: bool = True) -> Response:
        if self.query_engine is None:
            raise RuntimeError("RAG service is not initialized")

        response = self.query_engine.query(query)
        if isinstance(response, Response):
            if log:
                self._log_query_response(query, response)
            return response
        else:
            raise TypeError(
                f"Query engine returned unexpected response type: {type(response)}"
            )

    @staticmethod
    def _log_query_response(
        query: str, response: Response, content_length: int = 1000
    ) -> None:
        logger.info(f"Query: {query}")
        if isinstance(response, Response):
            logger.info(f"Response: {response.response}")

            log_session("Response Sources", style="blue")
            logger.info(f"Retrieved {len(response.source_nodes)} sources")
            source_text = format_sources_text(
                response.source_nodes, content_length=content_length
            )
            logger.info(source_text)

            log_session("Response Metadata", style="blue")
            metadata_json = json.dumps(
                response.metadata,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            logger.info("%s", metadata_json)

    def close(self) -> None:
        client = self.client
        if client is not None:
            client.close()

        self.client = None
        self.vector_store = None

    def override_init_config(self, **init_kwargs) -> None:
        """覆寫建構子參數並同步更新內部狀態（paths、vector store 等）。"""
        self.webpages_data_folder_path = init_kwargs.get(
            "webpages_data_folder_path", self.webpages_data_folder_path
        )
        self.force_rebuild = init_kwargs.get("force_rebuild", self.force_rebuild)

        self.md_docs_folder_path = os.path.join(
            self.webpages_data_folder_path, "results"
        )
        self.results_json_path = os.path.join(
            self.webpages_data_folder_path, "results.json"
        )
        self.results_json = self._load_results_json()

        client: QdrantClient | None = getattr(self, "client", None)
        if client is not None:
            client.close()

        self.client = None
        self.vector_store = None
        self.index = None
        self.retriever = None
        self.query_engine = None
