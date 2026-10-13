"""Augmenter 各步驟（下載、圖片摘要）的狀態。"""

from enum import StrEnum


class StepStatus(StrEnum):
    """單一步驟的結果。值與舊的裸字串相同，與 `str` 比較仍然成立。"""

    PENDING = ""  # 尚未進行（falsy）
    SUCCESS = "success"
    FAILED = "failed"
