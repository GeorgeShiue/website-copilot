"""文件內嵌圖片的共用型別與佔位符。"""

import re
from dataclasses import dataclass

# 解析器在內嵌圖片的位置放此佔位符（Docling 原生輸出的格式），描述完成後取代
IMAGE_PLACEHOLDER = "<!-- image -->"
IMAGE_PLACEHOLDER_PATTERN = re.compile(r"<!--\s*image\s*-->")


@dataclass
class ParsedImage:
    """文件內嵌的圖片（位元組與 MIME type）。"""

    content: bytes
    media_type: str
