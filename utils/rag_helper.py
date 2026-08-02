import os
import re
from typing import Any, ClassVar, Dict, List, Sequence

from llama_index.core.bridge.pydantic import Field
from llama_index.core.extractors.interface import BaseExtractor
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import BaseNode, NodeWithScore
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI

LLM_API_KEY_ENV_VARS: dict[str, dict[str, str]] = {
    "gemini": {
        "query_engine": "GEMINI_RAG_QUERY_ENGINE_API_KEY",
        "evaluator": "GEMINI_RAG_EVALUATOR_API_KEY",
    },
    "gpt": {
        "query_engine": "OPENAI_RAG_QUERY_ENGINE_API_KEY",
        "evaluator": "OPENAI_RAG_EVALUATOR_API_KEY",
    },
}


def build_filters(filter_dict: dict[str, Any] | None) -> MetadataFilters | None:
    if filter_dict is None:
        return None
    filter_list = []
    for key, entry in filter_dict.items():
        if isinstance(entry, tuple):
            value, operator = entry
        else:
            value, operator = entry, FilterOperator.EQ
        filter_list.append(MetadataFilter(key=key, value=value, operator=operator))
    return MetadataFilters(filters=filter_list)


def create_llm(llm_name: str, usage: str = "query_engine") -> GoogleGenAI | OpenAI:
    for provider, env_vars in LLM_API_KEY_ENV_VARS.items():
        if provider in llm_name:
            api_key = os.getenv(env_vars[usage])
            if provider == "gemini":
                return GoogleGenAI(model=llm_name, api_key=api_key)
            elif provider == "gpt":
                return OpenAI(model=llm_name, api_key=api_key)
    raise ValueError(f"Unsupported LLM name: {llm_name}")


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


# TODO: 支援更多擷取日期的方式
class MarkdownDateExtractor(BaseExtractor):
    """從 node content 萃取日期資訊寫入 metadata (year/month/day)。

    必須放在 SentenceSplitter 之前，確保 child chunks 繼承日期 metadata。
    支援四層遞減優先級：
      1. Section heading 年份 (### 2026)
      2. Post date 行 (Post date: Mon DD, YYYY)
      3. 列表結尾日期標記 (— Mon. DD, YYYY)
      4. 內容年份回落 (第一個 20\d{2})
    """

    is_text_node_only: bool = False

    MONTH_MAP: ClassVar[dict[str, int]] = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    # Pattern 1: ### 2026
    heading_year_pattern: re.Pattern = Field(
        default=re.compile(r"^#{1,6}\s+(20\d{2})\s*$", re.MULTILINE),
        description="匹配章節 heading 中的四位數年份",
    )

    # Pattern 2: Post date: Feb 15, 2011 3:16:55 AM
    post_date_pattern: re.Pattern = Field(
        default=re.compile(
            r"Post date:\s*"
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\.?\s+(\d{1,2}),?\s+(20\d{2})",
            re.IGNORECASE,
        ),
        description="匹配 Google Sites Post date 行",
    )

    # Pattern 3: — Dec. 5, 2024  or  — Mar 5, 2020 2:25:00 PM
    trailing_date_pattern: re.Pattern = Field(
        default=re.compile(
            r"—\s*"
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\.?\s+(\d{1,2}),?\s+(20\d{2})",
        ),
        description="匹配列表項目結尾的日期標記 (— Mon. DD, YYYY)",
    )

    @classmethod
    def class_name(cls) -> str:
        return "MarkdownDateExtractor"

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        """對每個 node 執行日期萃取。"""
        return [self._extract_date(node) for node in nodes]

    def _extract_date(self, node: BaseNode) -> Dict[str, Any]:
        content = node.get_content()

        # Strategy 1: Section heading 年份 (### 2026)
        match = self.heading_year_pattern.search(content)
        if match:
            return {"year": int(match.group(1))}

        # Strategy 2: Post date 行 (Post date: Mon DD, YYYY)
        match = self.post_date_pattern.search(content)
        if match:
            month = self.MONTH_MAP[match.group(1).lower()[:3]]
            return {
                "year": int(match.group(3)),
                "month": month,
                "day": int(match.group(2)),
            }

        # Strategy 3: 列表結尾日期標記 (— Mon. DD, YYYY)
        match = self.trailing_date_pattern.search(content)
        if match:
            month = self.MONTH_MAP[match.group(1).lower()[:3]]
            return {
                "year": int(match.group(3)),
                "month": month,
                "day": int(match.group(2)),
            }

        # Strategy 4: 內容年份回落 (第一個 20\d{2})
        match = re.search(r"20\d{2}", content)
        if match:
            return {"year": int(match.group(0))}

        return {}


def extract_sources_info(source_node: NodeWithScore) -> tuple[str, float, str]:
    try:
        page_title = source_node.node.metadata.get("page_title", "Unknown")
    except Exception:
        page_title = "Unknown"

    score = source_node.get_score()

    try:
        page_type = source_node.node.metadata.get("page_type", "Unknown")
    except Exception:
        page_type = "Unknown"

    return page_title, score, page_type
