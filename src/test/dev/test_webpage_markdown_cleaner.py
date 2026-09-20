"""WebpageMarkdownCleaner 的 LLM 產生 exclude_words 與清理單元測試。"""

import json
import random
from unittest.mock import patch

import pytest
from litellm import ModelResponse

from app.engines.webpage_markdown_cleaner import (
    ExcludeWordsGenerationError,
    WebpageMarkdownCleaner,
)

MOD = "app.engines.webpage_markdown_cleaner"


def _response(words):
    return ModelResponse(
        choices=[
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps({"exclude_words": words}),
                }
            }
        ],
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    )


PAGES = {
    f"p{i}": f"Skip to main content\nbody {i}\nFooter text\nonly{i}" for i in range(10)
}
# 30 頁：單頁獨有行的覆蓋率 1/30 < LOW_COVERAGE（少於 20 頁時沒有任何行算低覆蓋）
PAGES30 = {
    f"p{i}": f"Skip to main content\nbody {i}\nFooter text\nonly{i}" for i in range(30)
}


def test_guard_words_rules():
    samples = {"a": "Skip to main\nfoo\nxy", "b": "Skip to main\nbar\nxy", "c": "zzz"}
    kept = WebpageMarkdownCleaner.guard_words(
        ["Skip to main", "Skip to main", "xy", "x", "foo", 3, "zzz"], samples
    )
    assert kept == ["Skip to main", "xy"]  # 去重、長度 ≥2、需出現 ≥2 頁、非字串略過


def test_sample_pages_min_and_no_repeat():
    rng = random.Random(1)
    got = WebpageMarkdownCleaner.sample_pages(PAGES, 0.1, rng)
    assert len(got) == 2
    got = WebpageMarkdownCleaner.sample_pages({"a": "x"}, 0.1, rng)
    assert list(got) == ["a"]
    a = WebpageMarkdownCleaner.sample_pages(PAGES, 0.5, random.Random(7))
    b = WebpageMarkdownCleaner.sample_pages(PAGES, 0.5, random.Random(7))
    assert a == b and len(a) == 5


def test_generate_union_and_vote_order():
    responses = [
        _response(["Skip to main content"]),
        _response(["Skip to main content", "Footer text"]),
        _response(["Footer text", "Skip to main content"]),
    ]
    cleaner = WebpageMarkdownCleaner(repeat=3, seed=0)
    with (
        patch(f"{MOD}.completion", side_effect=responses),
        patch(f"{MOD}.completion_cost", return_value=0.01),
        patch(f"{MOD}.token_counter", return_value=100),
    ):
        result = cleaner.generate_exclude_words(PAGES)
    assert result.words == ["Skip to main content", "Footer text"]
    assert result.votes == {"Skip to main content": 3, "Footer text": 2}
    assert result.cost_usd == pytest.approx(0.03)


def test_single_run_failure_is_skipped_all_fail_raises():
    cleaner = WebpageMarkdownCleaner(repeat=2, seed=0)
    with (
        patch(
            f"{MOD}.completion",
            side_effect=[RuntimeError("x"), _response(["Footer text"])],
        ),
        patch(f"{MOD}.completion_cost", return_value=0.0),
        patch(f"{MOD}.token_counter", return_value=100),
    ):
        assert cleaner.generate_exclude_words(PAGES).words == ["Footer text"]
    with (
        patch(f"{MOD}.completion", side_effect=RuntimeError("x")),
        patch(f"{MOD}.token_counter", return_value=100),
    ):
        with pytest.raises(ExcludeWordsGenerationError):
            cleaner.generate_exclude_words(PAGES)


def test_prompt_over_limit_raises():
    cleaner = WebpageMarkdownCleaner(repeat=2, max_prompt_tokens=10)
    with (
        patch(f"{MOD}.token_counter", return_value=11),
        patch(f"{MOD}.completion") as c,
    ):
        with pytest.raises(ExcludeWordsGenerationError):
            cleaner.generate_exclude_words(PAGES)
        c.assert_not_called()


def test_clean_pages_applies_exclude_words():
    out = WebpageMarkdownCleaner().clean_pages(PAGES, ["Footer text"])
    assert all("Footer text" not in v and "body" in v for v in out.values())


def test_propose_words_rejects_stream_response():
    cleaner = WebpageMarkdownCleaner(repeat=1, seed=0)
    with (
        patch(f"{MOD}.completion", return_value=object()),
        patch(f"{MOD}.token_counter", return_value=100),
    ):
        # 非 ModelResponse 視為單次失敗；唯一一次失敗 → 全部失敗
        with pytest.raises(ExcludeWordsGenerationError):
            cleaner.generate_exclude_words(PAGES)


def test_save_generated_exclude_words(tmp_path):
    from app.engines.webpage_markdown_cleaner import GenerationResult
    from app.workflow.run_persistence import save_generated_exclude_words

    result = GenerationResult(
        words=["Footer text"],
        votes={"Footer text": 2, "only0": 1},
        seed=1,
        samples=[["p0", "p1"]],
        runs=[["Footer text"]],
        raw_runs=[["Footer text"]],
        usages=[{"prompt_tokens": 1, "completion_tokens": 1, "cost_usd": 0.02}],
        rejected={"only0": 1.0},
        stats={"Footer text": {"hits": 10, "low_occ_ratio": 0.0}},
    )
    save_generated_exclude_words(result, PAGES, str(tmp_path))

    toml_text = (tmp_path / "generated_exclude_words.toml").read_text(encoding="utf-8")
    assert '"Footer text"' in toml_text
    report = json.loads((tmp_path / "exclude_words_report.json").read_text("utf-8"))
    assert report["words"] == [
        {"word": "Footer text", "votes": 2, "hit_lines": 10, "low_occ_ratio": 0.0}
    ]
    assert report["rejected"] == [{"word": "only0", "votes": 1, "low_occ_ratio": 1.0}]
    assert report["total_cost_usd"] == pytest.approx(0.02)


def test_line_coverage_and_word_stats():
    cov = WebpageMarkdownCleaner.line_coverage(PAGES)
    assert cov["Footer text"] == 1.0
    assert cov["only3"] == pytest.approx(0.1)
    stats = WebpageMarkdownCleaner.word_stats(PAGES, "only", cov, low=0.15)
    assert stats == {"hits": 10, "low_occ_ratio": 1.0}
    stats = WebpageMarkdownCleaner.word_stats(PAGES, "Footer", cov, low=0.15)
    assert stats == {"hits": 10, "low_occ_ratio": 0.0}


def test_normalize_line_strips_link_url_keeps_image_url():
    n = WebpageMarkdownCleaner.normalize_line
    assert n(" [首頁](/a) ") == "[首頁]()" and n("[首頁](/b)") == n("[首頁](/a)")
    assert n("![x](a.png)") != n("![x](b.png)")


def test_validate_words_threshold_boundary():
    # 30 頁（單頁行覆蓋率 1/30 < LOW_COVERAGE）：導覽詞每頁都有；「正文」只在 p0 出現
    pages = {f"p{i}": f"nav bar\nbody {i}" for i in range(30)}
    pages["p0"] += "\n正文 sentence"
    cleaner = WebpageMarkdownCleaner(max_low_occ_ratio=0.1)
    kept, stats = cleaner.validate_words(pages, ["nav bar", "正文"])
    assert kept == ["nav bar"]
    assert stats["正文"]["low_occ_ratio"] == 1.0
    # 「body」30 行皆為低覆蓋行（各只在 1 頁）→ 比例 1.0；放寬到 1.0 才保留
    assert cleaner.validate_words(pages, ["body"])[0] == []
    assert WebpageMarkdownCleaner(max_low_occ_ratio=1.0).validate_words(
        pages, ["body"]
    )[0] == ["body"]


def test_generate_rejects_low_coverage_word():
    responses = [_response(["Footer text", "only"])] * 2
    cleaner = WebpageMarkdownCleaner(repeat=2, seed=0)
    with (
        patch(f"{MOD}.completion", side_effect=responses),
        patch(f"{MOD}.completion_cost", return_value=0.0),
        patch(f"{MOD}.token_counter", return_value=100),
    ):
        result = cleaner.generate_exclude_words(PAGES30)
    assert result is not None
    assert result.words == ["Footer text"]
    assert result.rejected == {"only": 1.0}
    assert result.votes["only"] == 2  # votes 仍保留被剔除詞


def test_generate_all_rejected_returns_empty_words():
    cleaner = WebpageMarkdownCleaner(repeat=1, seed=0)
    with (
        patch(f"{MOD}.completion", return_value=_response(["only"])),
        patch(f"{MOD}.completion_cost", return_value=0.0),
        patch(f"{MOD}.token_counter", return_value=100),
    ):
        result = cleaner.generate_exclude_words(PAGES30)
    assert result is not None and result.words == []


def test_generate_skips_llm_when_too_few_pages():
    cleaner = WebpageMarkdownCleaner(repeat=2)
    with patch(f"{MOD}.completion") as c:
        assert cleaner.generate_exclude_words({"a": "Footer text"}) is None
        c.assert_not_called()
