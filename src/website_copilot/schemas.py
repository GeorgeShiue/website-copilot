"""跨層共用的資料型別。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationResult:
    """generate_exclude_words 的結果。"""

    words: list[str]  # vote1 聯集，依得票多到少排序
    votes: dict[str, int]  # 每詞在各次重跑中的得票數
    seed: int
    samples: list[list[str]]  # 每次重跑抽到的頁面 key
    runs: list[list[str]]  # 每次重跑通過程式端保護的詞
    raw_runs: list[list[Any]]  # 每次重跑 LLM 的原始輸出
    usages: list[dict[str, float]] = field(default_factory=list)
    rejected: dict[str, float] = field(
        default_factory=dict
    )  # 被驗證剔除的詞 → 低覆蓋比例
    stats: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )  # 每詞 hits、low_occ_ratio
    hits: dict[str, int] = field(default_factory=dict)  # 每詞在全站的命中行數

    @property
    def cost_usd(self) -> float:
        return sum(u["cost_usd"] for u in self.usages)
