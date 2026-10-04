"""Markdown 文件 → nodes 的 ingestion pipeline。"""

import logging
import os
from functools import partial
from typing import Any

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import BaseNode, Document

from website_copilot.ingestion.indexing.transforms import (
    MarkdownDateExtractor,
    MarkdownHeadingMergeParser,
    MarkdownImageExtractor,
    SourcePagesInjector,
)
from website_copilot.utils.text_helper import clean_description

logger = logging.getLogger(__name__)


class NodePipelineBuilder:
    def __init__(
        self,
        *,
        chunk_size: int,
        chunk_overlap: int,
        paragraph_separator: str,
    ) -> None:
        """參數皆由 RAGConfig.nodes 傳入（預設值見 config）。"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.paragraph_separator = paragraph_separator
        self.last_doc_count = 0

    @staticmethod
    def _build_file_metadata(
        results_json: dict[str, Any], file_path: str, site_id: str
    ) -> dict[str, Any]:
        key = os.path.basename(file_path).replace(".md", "")
        page_info = results_json.get(key, {})
        page_metadata: dict[str, Any] = page_info.get("metadata", {})

        file_metadata: dict[str, Any] = {
            # 文件 entry 的鍵是 doc_<hash>，顯示用標題在 entry 的 title
            "page_title": page_info.get("title") or key,
            "page_url": page_info.get("url", ""),
            "page_type": page_metadata.get("page_type", "general"),
            "published_date": page_metadata.get("published_date", ""),
            "description": clean_description(page_metadata.get("description")),
            "site_id": site_id,
        }
        if page_metadata.get("file_format"):
            file_metadata["file_format"] = page_metadata["file_format"]
            file_metadata["file_name"] = page_metadata.get("file_name", "")

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
                SourcePagesInjector(
                    source_pages_by_url={
                        entry["url"]: entry["metadata"]["source_pages"]
                        for entry in results_json.values()
                        if entry.get("metadata", {}).get("source_pages")
                    }
                ),
            ]
        )
        nodes = pipeline.run(documents=md_docs, show_progress=True)
        logger.info("Pipeline produced %d nodes", len(nodes))

        return list(nodes)
