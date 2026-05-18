import os

import qdrant_client
from dotenv import load_dotenv
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
)
from llama_index.core.base.response.schema import Response
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import (
    MarkdownNodeParser,
    SentenceSplitter,
)
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore

from utils.rag_helper import (
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
    file_metadata,
    get_formatted_sources_with_scores,
)

MD_DOCS_FOLDER_PATH = "data/webpages/prompt-v3/results"
QDRANT_DB_PATH = "data/rag/qdrant_db"


# TODO: 重構以準備測試並調整 Query Engine 的參數
def main():
    # ----- 資源設置 -----
    load_dotenv()

    embed_model_name = "text-embedding-3-small"
    embedding_api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
    embed_model = OpenAIEmbedding(
        model=embed_model_name,
        embed_batch_size=256,
        api_key=embedding_api_key,
    )

    query_engine_model_name = "gemini-3.1-flash-lite"
    query_engine_api_key = os.getenv("GEMINI_RAG_QUERY_ENGINE_API_KEY")
    llm = GoogleGenAI(model=query_engine_model_name, api_key=query_engine_api_key)

    if os.path.exists(QDRANT_DB_PATH):
        # ----- 載入儲存和索引 -----
        client = qdrant_client.QdrantClient(path=QDRANT_DB_PATH)
        vector_store = QdrantVectorStore("webpages", client, index_doc_id=False)
        print(f"Load vector store from {QDRANT_DB_PATH}")

        index = VectorStoreIndex.from_vector_store(
            vector_store, embed_model, show_progress=True
        )

        print("Create index from vector store")
    else:
        # ----- 載入資料 -----
        md_docs: list[Document] = SimpleDirectoryReader(
            MD_DOCS_FOLDER_PATH,
            exclude_empty=True,
            filename_as_id=True,
            required_exts=[".md"],
            file_metadata=file_metadata,
            # num_files_limit=10, # test
        ).load_data(show_progress=True)

        print(f"Loading {len(md_docs)} Markdown Documents")
        print("-" * 90)

        # ----- 轉換資料 -----
        splitter_config = {
            "chunk_size": 800,
            "chunk_overlap": 100,
            "paragraph_separator": "\n\n",
        }

        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser.from_defaults(),
                SentenceSplitter.from_defaults(
                    chunk_size=splitter_config["chunk_size"],
                    chunk_overlap=splitter_config["chunk_overlap"],
                    paragraph_separator=splitter_config["paragraph_separator"],
                ),
                MarkdownHeadingMergeParser(),
                MarkdownImageExtractor(),
            ],
        )

        nodes = pipeline.run(documents=md_docs, show_progress=True)
        # log_page_node_info(nodes, page_title="Web_智慧與資料探勘實驗室")
        print(f"Pipeline produced {len(nodes)} nodes")
        print("-" * 90)

        # ----- 建立儲存和索引 -----
        client = qdrant_client.QdrantClient(path=QDRANT_DB_PATH)
        vector_store = QdrantVectorStore("webpages", client, index_doc_id=False)
        print(f"Persist vector store to {QDRANT_DB_PATH}")

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        print("Create index from nodes")

    print("=" * 90)

    # ----- 查詢引擎 -----
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5,  # 每次查詢返回的相關節點數量
        # vector_store_query_mode: VectorStoreQueryMode = VectorStoreQueryMode.DEFAULT, # 切換不同向量查詢模式
        # filters: Optional[MetadataFilters] = None, # Metadata過濾器
        # embed_model: Optional[BaseEmbedding] = None, # 查詢時使用的嵌入模型（可與索引不同）
    )
    response_synthesizer = get_response_synthesizer(
        llm,
        # response_mode=ResponseMode.COMPACT, # 切換不同回答模式
    )
    similarity_postprocessor = SimilarityPostprocessor(
        similarity_cutoff=0.5  # 過濾掉相似度低於0.5的節點
    )

    query_engine = RetrieverQueryEngine(
        retriever,
        response_synthesizer,
        node_postprocessors=[similarity_postprocessor],
    )

    query = "介紹實驗室"
    response = query_engine.query(query)
    print(f"Query: {query}")
    print("-" * 90)
    if isinstance(response, Response):
        print(f"Response: {response.response}")
        print("-" * 90)
        print("Sources:")
        source_text = get_formatted_sources_with_scores(
            response.source_nodes, content_length=1000
        )
        print(source_text)
        print("-" * 90)
        print("Metadata:")
        print(response.metadata)
    print("-" * 90)

    client.close()


if __name__ == "__main__":
    main()
