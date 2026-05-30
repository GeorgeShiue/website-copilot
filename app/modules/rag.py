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
    DatasetGenerator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
)
from llama_index.core.evaluation.base import EvaluationResult
from llama_index.core.evaluation.dataset_generation import QueryResponseDataset
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode, Document, NodeWithScore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.configs.rag_config import (
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
        self.vector_store: QdrantVectorStore | None = None
        self.index: VectorStoreIndex | None = None
        self.nodes: Sequence[BaseNode] | None = None
        self.retriever: VectorIndexRetriever | None = None
        self.query_engine: RetrieverQueryEngine | None = None

    def clean_vector_store(
        self, qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH
    ) -> None:
        shutil.rmtree(qdrant_db_folder_path)
        logger.info("Successfully cleaned existing vector store")

    def build_vector_store(
        self,
        qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH,
        collection_name: str = "webpages",
    ) -> None:
        self.qdrant_client = QdrantClient(path=qdrant_db_folder_path)
        self.vector_store = QdrantVectorStore(
            collection_name, self.qdrant_client, index_doc_id=False
        )
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

    def build_retriever(self, top_k: int = 5) -> None:
        if self.index is None:
            raise RuntimeError("Index have not been built, cannot build retriever")
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k,
        )
        logger.info("Successfully built retriever")

    # 暫時不需要
    def retrieve(self, query: str, log: bool = True) -> None:
        if self.retriever is None:
            raise RuntimeError("Retriever have not been built, cannot retrieve")

        retrieved_nodes: list[NodeWithScore] = self.retriever.retrieve(query)
        if log:
            logger.info(f"Query: {query}")
            self._log_sources(retrieved_nodes)

    # 暫時不需要
    def build_dataset(
        self,
        llm_name: str = "gemini-3.1-flash-lite",
        num_questions_per_chunk: int = 10,
    ) -> None:
        if self.nodes is None:
            raise RuntimeError(
                "Nodes have not been built, cannot build evaluation dataset"
            )

        llm = self._set_llm(llm_name)
        dataset_generator = DatasetGenerator(
            nodes=list(self.nodes),
            llm=llm,
            num_questions_per_chunk=num_questions_per_chunk,
            show_progress=True,
        )
        dataset: QueryResponseDataset = dataset_generator.generate_dataset_from_nodes(
            num=10  # test
        )

        logger.info("-" * 90)
        # for i in range(len(dataset.questions)):
        #     logger.info(f"Question {i+1}: {dataset.questions[i]}")
        #     logger.info("-" * 90)
        for i in range(len(dataset.qr_pairs)):
            logger.info(f"Q&A Pair {i + 1}:")
            logger.info(f"  Question: {dataset.qr_pairs[i][0]}")
            logger.info(f"  Answer: {dataset.qr_pairs[i][1]}")
            logger.info("-" * 90)

    def _log_sources(
        self, source_nodes: Sequence[NodeWithScore], content_length: int = 1000
    ) -> None:
        log_session("Sources", style="blue")
        logger.info(f"Retrieved {len(source_nodes)} sources")
        source_text = format_sources_text(source_nodes, content_length=content_length)
        logger.info(source_text)

    def build_query_engine(
        self,
        llm_name: str = "gemini-3.1-flash-lite",
        cutoff: float = 0.5,
    ) -> None:
        if self.retriever is None:
            raise RuntimeError(
                "Retriever have not been built, cannot build query engine"
            )

        llm = self._set_llm(llm_name)
        response_synthesizer = get_response_synthesizer(llm)
        similarity_postprocessor = SimilarityPostprocessor(similarity_cutoff=cutoff)
        self.query_engine = RetrieverQueryEngine(
            self.retriever,
            response_synthesizer,
            node_postprocessors=[similarity_postprocessor],
        )

        logger.info("Successfully built query engine")

    def _set_llm(self, llm_name: str) -> GoogleGenAI:
        api_key = os.getenv("GEMINI_RAG_QUERY_ENGINE_API_KEY")
        llm = GoogleGenAI(
            model=llm_name,
            api_key=api_key,
        )
        return llm

    def query(
        self, query: str, log_sources: bool = False, content_length: int = 1000
    ) -> Response:
        if self.query_engine is None:
            raise RuntimeError("RAG service have not been built, cannot execute query")

        logger.info(f"Query: {query}")
        response = self.query_engine.query(query)
        if isinstance(response, Response):
            logger.info(f"Response: {response.response}")
            if log_sources:
                self._log_sources(response.source_nodes, content_length)
            return response
        else:
            raise TypeError(
                f"Query engine returned unexpected response type: {type(response)}"
            )

    def evaluate(
        self,
        query: str,
        response: Response,
        llm_name: str = "gemini-3.1-flash-lite",
    ) -> tuple[EvaluationResult, EvaluationResult]:
        llm = self._set_llm(llm_name)

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
        client = self.qdrant_client
        if client is not None:
            client.close()

        self.qdrant_client = None
        self.vector_store = None

    def override_init_config(self, **init_kwargs) -> None:
        """覆寫建構子參數並同步更新內部狀態（paths、vector store 等）。"""
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

        client: QdrantClient | None = getattr(self, "client", None)
        if client is not None:
            client.close()

        self.qdrant_client = None
        self.vector_store = None
        self.index = None
        self.retriever = None
        self.query_engine = None
