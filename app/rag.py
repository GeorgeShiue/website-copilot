import json
import logging
import os
import shutil
from typing import Any, Sequence

import qdrant_client
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
        qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH,
        vector_store_collection_name: str = "webpages",
        force_rebuild: bool = False,
    ) -> None:
        # ----- init args -----
        self.webpages_data_folder_path = webpages_data_folder_path
        self.qdrant_db_folder_path = qdrant_db_folder_path
        self.vector_store_collection_name = vector_store_collection_name
        self.force_rebuild = force_rebuild

        # ----- internal state -----
        self.results_json_path = os.path.join(webpages_data_folder_path, "results.json")
        self.md_docs_folder_path = os.path.join(webpages_data_folder_path, "results")
        self.results_json: dict[str, Any] = self._load_results_json()
        log_session("Building Vector Store", style="cyan")
        self.client, self.vector_store = self.build_vector_store()
        self.index: VectorStoreIndex | None = None
        self.query_engine: RetrieverQueryEngine | None = None

    def build_vector_store(
        self,
    ) -> tuple[qdrant_client.QdrantClient, QdrantVectorStore]:
        vector_store_exist = False

        if os.path.exists(self.qdrant_db_folder_path):
            vector_store_exist = True
            if self.force_rebuild:
                vector_store_exist = False
                shutil.rmtree(self.qdrant_db_folder_path)  # * 清理既存的 Vector Store
                logger.info("Successfully cleaned existing vector store")

        client = qdrant_client.QdrantClient(path=self.qdrant_db_folder_path)
        vector_store = QdrantVectorStore(
            self.vector_store_collection_name, client, index_doc_id=False
        )

        if vector_store_exist:
            logger.info("Successfully loaded vector store")
        else:
            logger.info("Successfully built vector store")

        return client, vector_store

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
        embed_model = self._set_embed_model(embedding_model_name)

        if os.path.exists(self.qdrant_db_folder_path) and not self.force_rebuild:
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

    def build_query_engine(
        self,
        llm_model_name: str = "gemini-3.1-flash-lite",
        similarity_top_k: int = 5,
        similarity_cutoff: float = 0.5,
    ) -> None:
        if self.index is None:
            raise RuntimeError("Index is not initialized, cannot build query engine")
        llm = self._set_llm(llm_model_name)

        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=similarity_top_k,
        )
        response_synthesizer = get_response_synthesizer(llm)
        similarity_postprocessor = SimilarityPostprocessor(
            similarity_cutoff=similarity_cutoff
        )
        self.query_engine = RetrieverQueryEngine(
            retriever,
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
            source_text = format_sources_text(
                response.source_nodes, content_length=content_length
            )
            logger.info(source_text)

            log_session("Response Metadata", style="blue")
            logger.info(response.metadata)

    def close(self) -> None:
        if self.client:
            self.client.close()
