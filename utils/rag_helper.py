import re
from typing import Any, Dict, List, Sequence

from llama_index.core.bridge.pydantic import Field
from llama_index.core.extractors.interface import BaseExtractor
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import BaseNode

HEADING_ONLY_RE = re.compile(r"^#{1,6}\s+.+$")
IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


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

    image_pattern: str = Field(
        default=r"!\[([^\]]*)\]\(([^)]+)\)",
        description="用於匹配 Markdown 圖片的正則表達式",
    )

    @classmethod
    def class_name(cls) -> str:
        return "MarkdownImageExtractor"

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        """提取圖片元數據並清理節點內容。"""
        metadata_list = []
        pattern = re.compile(self.image_pattern)

        for node in nodes:
            content = node.get_content()

            images = [
                {"url": match.group(2), "alt": match.group(1).strip()}
                for match in pattern.finditer(content)
            ]

            metadata_dict = {}
            if images:
                metadata_dict["images"] = [
                    *(node.metadata.get("images") or []),
                    *images,
                ]

                cleaned_content = pattern.sub(
                    lambda match: match.group(1).strip(), content
                )
                node.set_content(cleaned_content)

            metadata_list.append(metadata_dict)

        return metadata_list
