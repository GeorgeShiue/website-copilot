"""送 VLM 前的圖片過濾：內容雜湊（去重）與尺寸（小圖門檻）。

設計為所有圖片共用（頁面圖片、文件內嵌圖片）。
"""

import hashlib
import io

from PIL import Image, UnidentifiedImageError


def content_sha1(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()


def image_long_edge(content: bytes) -> int | None:
    """圖片長邊像素；無法解碼時回傳 None（呼叫端不應據此過濾）。"""
    try:
        with Image.open(io.BytesIO(content)) as image:
            return max(image.size)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return None
