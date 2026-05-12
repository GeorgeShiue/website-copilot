import json
import os
from typing import Any

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import (
    MarkdownNodeParser,
    SentenceSplitter,
)
from llama_index.core.schema import Document

from utils.rag_helper import (
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
)

DATA_FOLDER_PATH = "data/webpages/prompt-v3"
MD_DOCS_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "results")
RESULTS_JSON_PATH = os.path.join(DATA_FOLDER_PATH, "results.json")
RUNS_FOLER_PATH = "runs"
PIPELINE_STORAGE_PATH = os.path.join(RUNS_FOLER_PATH, "pipeline_storage")

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
    ).load_data()
    print(f"Loading {len(md_docs)} Markdown Documents")
    print("-" * 50)

    # ----- 轉換資料 -----
    splitter_config = {
        "chunk_size": 800,
        "chunk_overlap": 100,
        "paragraph_separator": "\n\n",
    }

    # TODO: embedding + vector store
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
    nodes = list(pipeline.run(documents=md_docs))

    counter = 0
    page_title = "Web_智慧與資料探勘實驗室"
    for node in nodes:
        if node.metadata.get("page_title") == page_title:
            counter += 1
            print("Node content:")
            print(node.get_content())
            print()
            print("Node metadata:")
            print(node.get_metadata_str())
            print("-" * 50)
    print(f"Pipeline produced {len(nodes)} nodes")
    print(f"Found {counter} nodes from {page_title}")

    # print("=" * 50)

    # ----- 向量索引 -----


if __name__ == "__main__":
    main()
