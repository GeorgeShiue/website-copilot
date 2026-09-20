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


def test_guard_words_rules():
    samples = {"a": "Skip to main\nfoo", "b": "Skip to main\nbar", "c": "zzz"}
    kept = WebpageMarkdownCleaner.guard_words(
        ["Skip to main", "Skip to main", "ab", "foo", 3, "zzz"], samples
    )
    assert kept == ["Skip to main"]  # 去重、長度 ≥3、需出現 ≥2 頁、非字串略過


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
        votes={"Footer text": 2},
        seed=1,
        samples=[["p0", "p1"]],
        runs=[["Footer text"]],
        raw_runs=[["Footer text"]],
        usages=[{"prompt_tokens": 1, "completion_tokens": 1, "cost_usd": 0.02}],
    )
    save_generated_exclude_words(result, PAGES, str(tmp_path))

    toml_text = (tmp_path / "generated_exclude_words.toml").read_text(encoding="utf-8")
    assert '"Footer text"' in toml_text
    report = json.loads((tmp_path / "exclude_words_report.json").read_text("utf-8"))
    assert report["words"] == [{"word": "Footer text", "votes": 2, "hit_lines": 10}]
    assert report["total_cost_usd"] == pytest.approx(0.02)
