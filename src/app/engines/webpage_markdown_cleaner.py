"""網頁 Markdown 清洗引擎。

- 清理：exclude_words 行級過濾 + Regex 預處理 + mdformat 格式化 + 結構修復
- 產生 exclude_words：對全站原始 fit_markdown 重複 N 次「隨機抽樣 → LLM 提議 →
  程式端過濾」，取聯集（vote1），再以全站行覆蓋率驗證剔除會誤傷正文的詞，詳見 docs/work/2026_0921/2026_0919-llm_exclude_words/survey.md
"""

import json
import logging
import math
import random
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import mdformat
from litellm import ModelResponse, completion, completion_cost, token_counter

logger = logging.getLogger(__name__)


# ── 正則常數 ─────────────────────────────────────────────────────────

EMPTY_ANCHOR_LINK_PATTERN = re.compile(r"\[\]\(.*?#h\.[a-z0-9]+\)")
EMPTY_LIST_NOISE_PATTERN = re.compile(r"^\s*\*\s*#{1,6}\s*$", flags=re.MULTILINE)
EMPTY_HEADING_LINE_PATTERN = re.compile(r"^(\s{0,3}#{1,6})\s*$")
SKIP_AS_HEADING_PATTERN = re.compile(r"^\s*!?\[.*?\]\(.*?\)\s*$")
IMAGE_ABOVE_SPACING_PATTERN = re.compile(
    r"([^\n])\n(?=[ \t]*!\[.*?\]\()", flags=re.MULTILINE
)
IMAGE_FOLLOW_TEXT_PATTERN = re.compile(r"(!\[.*?\]\(.*?\))\s*(?=\S)")


# ── LLM 產生 exclude_words 的常數 ────────────────────────────────────

MIN_WORD_LEN = 2  # 過短的詞是否誤傷正文，交由全站行覆蓋率驗證判斷
MIN_SAMPLE_PAGES = 2  # 詞必須逐字出現在至少這麼多個樣本頁；全站頁數不足時跳過產生
LOW_COVERAGE = 0.05  # 行覆蓋率低於此值的行視為較像正文（survey：單一資料點）

# 圖片 ![alt](url) 保留 URL（不同圖片即使 alt 相同也視為不同行）；一般連結去除 URL
LINK_URL_RE = re.compile(r"(!\[[^\]]*\]\(\s*[^\s)]+)|\]\(\s*[^\s)]+")

PROMPT = """你會看到同一個網站的數個頁面的 Markdown（由爬蟲產生）。
請找出「網站模板 / 頁面元件」產生的雜訊文字，這些文字與頁面正文無關，
例如：導覽列、跳到主要內容、搜尋框、頁首頁尾、版權宣告、檢舉連結、分享、分頁按鈕。

規則：
- 只輸出「在多個頁面都逐字出現」的片段。
- 不得輸出任何只出現在單一頁面的內容、人名、標題或正文詞彙。
- 每個片段要盡量短且具辨識性，但不可短到會誤傷正文（例如單一常見詞）。
- 輸出格式為 JSON：{{"exclude_words": ["片段1", "片段2"]}}，不要輸出其他文字。

{pages}"""


class ExcludeWordsGenerationError(RuntimeError):
    """LLM 產生 exclude_words 失敗（prompt 超限，或所有重跑皆失敗）。"""


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

    @property
    def cost_usd(self) -> float:
        return sum(u["cost_usd"] for u in self.usages)


class WebpageMarkdownCleaner:
    def __init__(
        self,
        model: str = "gpt-5.6-luna",
        sample_ratio: float = 0.1,
        repeat: int = 5,
        max_prompt_tokens: int = 200_000,
        seed: int | None = None,
        max_low_occ_ratio: float = 0.1,
    ) -> None:
        # ===== init args =====
        self.model = model
        self.sample_ratio = sample_ratio
        self.repeat = repeat
        self.max_prompt_tokens = max_prompt_tokens
        self.seed = seed
        self.max_low_occ_ratio = max_low_occ_ratio

    # ── 清理 ─────────────────────────────────────────────────────────

    def clean_pages(
        self, pages: dict[str, str], exclude_words: list[str] | None = None
    ) -> dict[str, str]:
        """逐頁清理 Markdown。"""
        return {
            key: self.clean_markdown(md, exclude_words=exclude_words)
            for key, md in pages.items()
        }

    @staticmethod
    def promote_empty_heading_line(fit_markdown: str) -> str:
        """將空標題行提升為下一個可用文字標題，並保留中間內容。"""
        lines = fit_markdown.splitlines(keepends=True)
        fixed_lines: list[str] = []
        i = 0

        while i < len(lines):
            current_line = lines[i]
            heading_match = EMPTY_HEADING_LINE_PATTERN.match(
                current_line.rstrip("\r\n")
            )
            if heading_match:
                j = i + 1
                while j < len(lines):
                    candidate = lines[j].strip()
                    if candidate and not SKIP_AS_HEADING_PATTERN.match(candidate):
                        fixed_lines.append(f"{heading_match.group(1)} {candidate}\n")
                        fixed_lines.extend(lines[i + 1 : j])
                        i = j + 1
                        break
                    j += 1
                else:
                    fixed_lines.append(current_line)
                    i += 1
            else:
                fixed_lines.append(current_line)
                i += 1

        return "".join(fixed_lines)

    @staticmethod
    def clean_markdown(
        markdown: str,
        exclude_words: list[str] | None = None,
    ) -> str:
        """Markdown 清理：Regex 預處理 + mdformat 格式化 + 結構修復。

        Args:
            markdown: 原始 Markdown 文字。
            exclude_words: 要排除的關鍵字列表（行級過濾）。
        """
        # --- 資料清洗 ---
        if exclude_words is not None:
            markdown = "".join(
                line
                for line in markdown.splitlines(keepends=True)
                if not any(word in line for word in exclude_words)
            )
        markdown = EMPTY_ANCHOR_LINK_PATTERN.sub("", markdown)
        markdown = EMPTY_LIST_NOISE_PATTERN.sub("", markdown)

        # ----- 結構修復 (前) -----
        markdown = WebpageMarkdownCleaner.promote_empty_heading_line(markdown)
        markdown = IMAGE_ABOVE_SPACING_PATTERN.sub(r"\1\n\n", markdown)

        # ----- 格式化 -----
        try:
            markdown = mdformat.text(
                markdown,
                options={"wrap": "no"},
                extensions={"gfm"},
            )
        except (ValueError, KeyError) as e:
            logger.warning("mdformat failed, using unformatted markdown: %s", e)

        # ----- 結構修復 (後) -----
        markdown = IMAGE_FOLLOW_TEXT_PATTERN.sub(r"\1\n", markdown)
        markdown = IMAGE_ABOVE_SPACING_PATTERN.sub(r"\1\n\n", markdown)

        return markdown

    # ── 產生 exclude_words（vote1）───────────────────────────────────

    def generate_exclude_words(self, pages: dict[str, str]) -> GenerationResult | None:
        """對全站原始 fit_markdown 產生 exclude_words（重複 repeat 次，取聯集後驗證）。

        單次 LLM 呼叫失敗只略過該次；prompt 超過 max_prompt_tokens 或所有重跑
        皆失敗則拋出 ExcludeWordsGenerationError。全站頁數少於 MIN_SAMPLE_PAGES
        時無法通過樣本頁保護，跳過 LLM 並回傳 None。
        """
        if len(pages) < MIN_SAMPLE_PAGES:
            logger.warning(
                "只有 %d 頁（< %d），跳過 LLM 產生 exclude_words",
                len(pages),
                MIN_SAMPLE_PAGES,
            )
            return None

        seed = self.seed if self.seed is not None else random.randrange(2**32)
        rng = random.Random(seed)

        sample_keys: list[list[str]] = []
        runs: list[list[str]] = []
        raw_runs: list[list[Any]] = []
        usages: list[dict[str, float]] = []
        for i in range(self.repeat):
            samples = self.sample_pages(pages, self.sample_ratio, rng)
            try:
                words, raw_words, usage = self._propose_words(samples)
            except ExcludeWordsGenerationError:
                raise
            except Exception as e:
                logger.warning(
                    "exclude_words run %d/%d failed: %s", i + 1, self.repeat, e
                )
                continue
            sample_keys.append(list(samples))
            runs.append(words)
            raw_runs.append(raw_words)
            usages.append(usage)

        if not runs:
            raise ExcludeWordsGenerationError(
                f"all {self.repeat} exclude_words runs failed"
            )

        votes = Counter(w for r in runs for w in r)
        order = {w: i for i, w in enumerate(w for r in runs for w in r)}
        ranked = sorted(votes, key=lambda w: (-votes[w], order[w]))
        kept, stats = self.validate_words(pages, ranked)
        rejected = {w: stats[w]["low_occ_ratio"] for w in ranked if w not in kept}
        if not kept:
            logger.warning("驗證後沒有可用的 exclude_words，不做行級過濾")
        return GenerationResult(
            words=kept,
            votes={w: votes[w] for w in ranked},
            seed=seed,
            samples=sample_keys,
            runs=runs,
            raw_runs=raw_runs,
            usages=usages,
            rejected=rejected,
            stats=stats,
        )

    @staticmethod
    def sample_pages(
        pages: dict[str, str], ratio: float, rng: random.Random
    ) -> dict[str, str]:
        """隨機不重複取樣：總頁數的 ratio（至少 MIN_SAMPLE_PAGES 頁，至多全部）。"""
        k = min(len(pages), max(MIN_SAMPLE_PAGES, math.ceil(len(pages) * ratio)))
        chosen = rng.sample(sorted(pages), k)
        return {key: pages[key] for key in chosen}

    @staticmethod
    def guard_words(words: list[Any], samples: dict[str, str]) -> list[str]:
        """程式端保護：長度下限、去重、需逐字出現於 >= MIN_SAMPLE_PAGES 個樣本頁。"""
        kept: list[str] = []
        for word in words:
            if not isinstance(word, str):
                continue
            word = word.strip()
            if len(word) < MIN_WORD_LEN or word in kept:
                continue
            if sum(word in md for md in samples.values()) < MIN_SAMPLE_PAGES:
                continue
            kept.append(word)
        return kept

    @staticmethod
    def normalize_line(line: str) -> str:
        """比對「同一行」用：strip 並移除一般連結的 URL，保留連結文字、title 與圖片 URL。"""
        return LINK_URL_RE.sub(lambda m: m.group(1) or "](", line.strip())

    @staticmethod
    def line_coverage(pages: dict[str, str]) -> dict[str, float]:
        """正規化後完整相同的行，出現在多少比例的頁面（每頁只算一次）。"""
        normalize = WebpageMarkdownCleaner.normalize_line
        counter: Counter[str] = Counter()
        for md in pages.values():
            counter.update({normalize(ln) for ln in md.splitlines() if ln.strip()})
        total = len(pages)
        return {ln: n / total for ln, n in counter.items()} if total else {}

    @staticmethod
    def word_stats(
        pages: dict[str, str],
        word: str,
        coverage: dict[str, float],
        low: float = LOW_COVERAGE,
    ) -> dict[str, Any]:
        """詞的命中行數，及命中次數中落在低覆蓋行（覆蓋率 < low）的比例。"""
        normalize = WebpageMarkdownCleaner.normalize_line
        covs = [
            coverage[normalize(ln)]
            for md in pages.values()
            for ln in md.splitlines()
            if ln.strip() and word in ln
        ]
        return {
            "hits": len(covs),
            "low_occ_ratio": sum(c < low for c in covs) / len(covs) if covs else 0.0,
        }

    def validate_words(
        self, pages: dict[str, str], words: list[str]
    ) -> tuple[list[str], dict[str, dict[str, Any]]]:
        """全站行覆蓋率驗證：低覆蓋比例超過 max_low_occ_ratio 的詞剔除。

        回傳 (保留的詞（維持輸入順序）, 每詞統計)。
        """
        coverage = self.line_coverage(pages)
        stats = {w: self.word_stats(pages, w, coverage) for w in words}
        kept = [w for w in words if stats[w]["low_occ_ratio"] <= self.max_low_occ_ratio]
        return kept, stats

    @staticmethod
    def count_word_hits(pages: dict[str, str], words: list[str]) -> dict[str, int]:
        """每詞在全站原始頁面中命中的行數。"""
        return {
            w: sum(w in ln for md in pages.values() for ln in md.splitlines())
            for w in words
        }

    def _propose_words(
        self, samples: dict[str, str]
    ) -> tuple[list[str], list[Any], dict[str, float]]:
        """單次 LLM 提議。回傳 (通過保護的詞, LLM 原始詞, 用量)。"""
        pages_text = "\n\n".join(
            f"===== 頁面 {i}（{key}）=====\n{md}"
            for i, (key, md) in enumerate(samples.items(), 1)
        )
        prompt = PROMPT.format(pages=pages_text)
        try:
            est_tokens = token_counter(model=self.model, text=prompt)
        except Exception:
            est_tokens = len(prompt) // 2  # 保守估計
        logger.debug("prompt ≈ %d tokens（%d 頁）", est_tokens, len(samples))
        if est_tokens > self.max_prompt_tokens:
            raise ExcludeWordsGenerationError(
                f"prompt ≈ {est_tokens} tokens 超過 max_prompt_tokens="
                f"{self.max_prompt_tokens}，請調低 sample_ratio"
            )
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            stream=False,
        )
        # stream=False 時必為 ModelResponse；型別上 completion 也可能回傳串流物件
        if not isinstance(response, ModelResponse):
            raise TypeError(f"unexpected response type: {type(response).__name__}")
        content = response.choices[0].message.content or "{}"
        try:
            raw_words = json.loads(content).get("exclude_words", [])
        except (json.JSONDecodeError, AttributeError):
            raw_words = []
        if not isinstance(raw_words, list):
            raw_words = []
        usage_info = getattr(response, "usage", None)
        usage = {
            "prompt_tokens": getattr(usage_info, "prompt_tokens", 0),
            "completion_tokens": getattr(usage_info, "completion_tokens", 0),
            "cost_usd": completion_cost(completion_response=response),
        }
        return self.guard_words(raw_words, samples), raw_words, usage
