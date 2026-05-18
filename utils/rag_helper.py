import json
import os
import re
from typing import Any, Dict, List, Sequence

from llama_index.core.bridge.pydantic import Field
from llama_index.core.extractors.interface import BaseExtractor
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import BaseNode, NodeWithScore
from llama_index.core.utils import truncate_text

RESULTS_JSON_PATH = "data/webpages/prompt-v3/results.json"
HEADING_ONLY_RE = re.compile(r"^#{1,6}\s+.+$")
IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

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


def log_page_node_info(nodes: Sequence[BaseNode], page_title: str) -> None:
    counter = 0
    for node in nodes:
        if node.metadata.get("page_title") == page_title:
            counter += 1
            print("Node content:")
            print(node.get_content())
            print()
            print("Node metadata:")
            print(node.get_metadata_str())
            print("-" * 90)
    print(f"Found {counter} nodes from {page_title}")


class MarkdownHeadingMergeParser(NodeParser):
    def _merge_heading_only_nodes(self, nodes: Sequence[BaseNode]) -> List[BaseNode]:
        merged_nodes: List[BaseNode] = []
        pending_nodes: List[BaseNode] = []

        for node in nodes:
            if self._is_heading_only(node):
                pending_nodes.append(node)
                continue

            if pending_nodes:
                heading_text = "\n".join(
                    pending_node.get_content().strip() for pending_node in pending_nodes
                )
                body_text = node.get_content().strip()
                node.set_content(f"{heading_text}\n{body_text}")
                pending_nodes.clear()

            merged_nodes.append(node)

        return merged_nodes

    def _is_heading_only(self, node: BaseNode) -> bool:
        content = node.get_content().strip()
        if not content:
            return False
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(lines) != 1:
            return False
        line = lines[0]
        return bool(
            HEADING_ONLY_RE.match(line)
            or (len(line) <= 40 and not line.endswith((".", "!", "?", ":", ";")))
        )

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        merged_nodes = self._merge_heading_only_nodes(nodes)
        return merged_nodes


class MarkdownImageExtractor(BaseExtractor):
    is_text_node_only: bool = False

    image_pattern: re.Pattern = Field(
        default=IMAGE_PATTERN,
        description="用於匹配 Markdown 圖片的正則表達式",
    )

    @classmethod
    def class_name(cls) -> str:
        return "MarkdownImageExtractor"

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        """提取圖片元數據並清理節點內容。"""
        metadata_list = []

        for node in nodes:
            content = node.get_content()

            images = [
                {"url": match.group(2), "alt": match.group(1).strip()}
                for match in self.image_pattern.finditer(content)
            ]

            metadata_dict = {}
            if images:
                metadata_dict["images"] = [
                    *(node.metadata.get("images") or []),
                    *images,
                ]

                cleaned_content = self.image_pattern.sub(
                    lambda match: match.group(1).strip(), content
                )
                node.set_content(cleaned_content)

            metadata_list.append(metadata_dict)

        return metadata_list


def get_formatted_sources_with_scores(
    source_nodes: Sequence[NodeWithScore], content_length: int = 100
) -> str:
    texts: List[str] = []
    for source_node in source_nodes:
        try:
            raw_content = source_node.node.get_content()
        except Exception:
            raw_content = ""

        fmt_text_chunk = truncate_text(raw_content, content_length)

        try:
            doc_id = source_node.node.node_id or "None"
        except Exception:
            doc_id = "None"

        score = source_node.get_score()

        source_text = (
            f"> Source (Doc id: {doc_id}, Score: {score:0.3f}): {fmt_text_chunk}"
        )
        texts.append(source_text)

    return "\n\n".join(texts)
