"""PageStats：逐欄位加總。"""

from typing import Any

from website_copilot.ingestion.augmentation.augmenter import PageStats


def test_add_sums_every_field() -> None:
    total = PageStats(cost_usd=1.5, success=2, download_failure=1, skipped=3) + (
        PageStats(cost_usd=0.5, success=1, summarize_failure=2, cache_reuse=4)
    )

    assert total == PageStats(
        cost_usd=2.0,
        success=3,
        download_failure=1,
        summarize_failure=2,
        skipped=3,
        cache_reuse=4,
    )
    assert total.failure == 3


def test_sum_with_start_value() -> None:
    stats = [PageStats(success=1), PageStats(success=2)]

    assert sum(stats, PageStats()).success == 3


def test_add_defers_to_reflected_operand_of_other_type() -> None:
    # 回傳 NotImplemented 才會輪到對方的 __radd__
    class Other:
        def __radd__(self, left: Any) -> str:
            return "radd"

    assert PageStats() + Other() == "radd"  # type: ignore[operator]
