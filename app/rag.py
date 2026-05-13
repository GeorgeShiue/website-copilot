import json
import os
import time
from typing import Any

import qdrant_client
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import (
    MarkdownNodeParser,
    SentenceSplitter,
)
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from utils.rag_helper import (
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
)

DATA_FOLDER_PATH = "data/webpages/prompt-v3"
MD_DOCS_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "results")
RESULTS_JSON_PATH = os.path.join(DATA_FOLDER_PATH, "results.json")
RAG_FOLER_PATH = "data/rag"
QDRANT_DB_PATH = os.path.join(RAG_FOLER_PATH, "qdrant_db")

results_json = {}
if os.path.exists(RESULTS_JSON_PATH):
    with open(RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        results_json = json.load(f)
else:
    raise FileNotFoundError(f"Results JSON file not found at {RESULTS_JSON_PATH}")


def file_metadata(file_path: str) -> dict[str, Any]:
    """Extract file metadata for a given file path."""
    page_title = os.path.basename(file_path).replace(".md", "")

    images = []
    for result_json_image in results_json[page_title]["images"]:
        url = result_json_image["url"]
        images.append({"url": url})

    metadata = {
        "page_title": page_title,
        "page_url": results_json[page_title]["url"],
    }

    return metadata


def main():
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
    print("-" * 50)

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

    # counter = 0
    # page_title = "Web_智慧與資料探勘實驗室"
    # for node in nodes:
    #     if node.metadata.get("page_title") == page_title:
    #         counter += 1
    #         print("Node content:")
    #         print(node.get_content())
    #         print()
    #         print("Node metadata:")
    #         print(node.get_metadata_str())
    #         print("-" * 50)
    # print(f"Found {counter} nodes from {page_title}")
    print(f"Pipeline produced {len(nodes)} nodes")
    print("-" * 50)

    # ----- 向量索引 -----
    load_dotenv()
    api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        embed_batch_size=256,
        api_key=api_key,
    )

    if os.path.exists(QDRANT_DB_PATH):
        client = qdrant_client.QdrantClient(path=QDRANT_DB_PATH)
        vector_store = QdrantVectorStore("webpages", client, index_doc_id=False)
        print(f"Load vector store from {QDRANT_DB_PATH}")

        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model,
            show_progress=True,
        )

        print("Create index from vector store")
        client.close()
    else:
        client = qdrant_client.QdrantClient(path=QDRANT_DB_PATH)
        vector_store = QdrantVectorStore("webpages", client, index_doc_id=False)
        print(f"Persist vector store to {QDRANT_DB_PATH}")

        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
        )

        start_time = time.time()
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        end_time = time.time()
        print(f"Indexing time: {end_time - start_time:.2f} seconds")

        print("Create index from nodes")
        client.close()

    print(f"Index summary: {index.summary}")  # debug


if __name__ == "__main__":
    main()
