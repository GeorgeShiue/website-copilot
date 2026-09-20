"""方案 4 實驗：LLM 產生 exclude_words vs 人工 exclude_words。

三組共用同一份原始 fit_markdown（未經 clean_markdown）：
  A. none    無 exclude_words
  B. manual  configs/website_crawler/{config}.toml 的人工清單
  C. llm     LLM 從樣本頁產生（經程式端保護過濾）

不修改 src/。輸出到 runs/<timestamp>/ab_test_llm_exclude_words/。

執行：
  uv run python scripts/ab_test_llm_exclude_words.py --config nculab
"""

import argparse
from collections import Counter
import json
import math
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from app.configs.website_crawler_config import WebsiteCrawlerConfig
from app.engines.website_crawler import WebsiteCrawler
from app.engines.webpage_markdown_cleaner import (
    ExcludeWordsGenerationError,
    WebpageMarkdownCleaner,
)

DEFAULT_MODEL = "gpt-5.6-luna"


# ── 爬取 ─────────────────────────────────────────────────────────────


def crawl_site(config: WebsiteCrawlerConfig) -> dict[str, str]:
    crawler = WebsiteCrawler(
        max_depth=config.max_depth,
        max_pages=config.max_pages,
        content_threshold=config.content_threshold,
        light_mode=config.light_mode,
        wait_for_images=config.wait_for_images,
    )
    # 不傳 exclude_words；crawler.raw_pages 為未清理的原始 fit_markdown
    results = crawler.crawl_website(
        url=config.url,
        url_patterns=config.url_patterns,
        allowed_domains=config.allowed_domains,
        path_prefix=config.path_prefix,
    )
    if results is None:
        raise RuntimeError("crawl failed")
    return crawler.raw_pages


# ── 指標 ─────────────────────────────────────────────────────────────


def hit_lines(pages: dict[str, str], words: list[str]) -> dict[str, list[str]]:
    """每頁被 words 命中的原始行（與 clean_markdown 的行級過濾同一判準）。"""
    out: dict[str, list[str]] = {}
    for key, md in pages.items():
        lines = [
            ln.strip()
            for ln in md.splitlines()
            if ln.strip() and any(w in ln for w in words)
        ]
        if lines:
            out[key] = lines
    return out


def count(hits: dict[str, list[str]]) -> int:
    return sum(len(v) for v in hits.values())


def line_set(hits: dict[str, list[str]]) -> set[tuple[str, str]]:
    return {(k, ln) for k, v in hits.items() for ln in v}


def run_group(pages: dict[str, str], words: list[str] | None) -> dict[str, str]:
    return WebpageMarkdownCleaner().clean_pages(pages, words)


def total_chars(cleaned: dict[str, str]) -> int:
    return sum(len(v) for v in cleaned.values())


# ── 報告 ─────────────────────────────────────────────────────────────


def toml_list(words: list[str]) -> str:
    return (
        "exclude_words = [\n"
        + "".join(f"    {json.dumps(w, ensure_ascii=False)},\n" for w in words)
        + "]\n"
    )


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="nculab")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--sample-ratio", type=float, default=0.1)
    parser.add_argument("--max-prompt-tokens", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args()

    load_dotenv()
    config = WebsiteCrawlerConfig.from_toml(args.config)
    manual = config.exclude_words or []
    out_dir = os.path.join(
        "runs",
        datetime.now().strftime("%Y%m%d_%H%M%S"),
        "ab_test_llm_exclude_words",
        args.config,
    )

    print(f"[1/4] crawling {args.config} ...")
    pages = crawl_site(config)
    print(f"      {len(pages)} pages")

    print(f"[2/4] proposing exclude_words x{args.repeat} ({args.model}) ...")
    cleaner = WebpageMarkdownCleaner(
        model=args.model,
        sample_ratio=args.sample_ratio,
        repeat=args.repeat,
        max_prompt_tokens=args.max_prompt_tokens,
        seed=args.seed,
    )
    try:
        generation = cleaner.generate_exclude_words(pages)
    except ExcludeWordsGenerationError as e:
        raise SystemExit(str(e))
    seed = generation.seed
    print(f"      seed={seed}")
    sample_keys = generation.samples
    runs = generation.runs
    raw_runs = generation.raw_runs
    usages = generation.usages
    sets = [set(r) for r in runs]
    inter = set.intersection(*sets) if sets else set()
    union = set.union(*sets) if sets else set()
    stability = len(inter) / len(union) if union else 0.0

    # ----- 合併策略：first / vote>=k（k=1 即聯集，k=repeat 即交集）-----
    votes = Counter(w for r in runs for w in r)
    order = {w: i for i, w in enumerate(w for r in runs for w in r)}
    ranked = sorted(votes, key=lambda w: (-votes[w], order[w]))
    thresholds = sorted(
        {k for k in (1, 2, math.ceil(args.repeat / 2), args.repeat) if k <= args.repeat}
    )
    strategies: dict[str, list[str]] = {"first": runs[0]}
    for k in thresholds:
        strategies[f"vote{k}"] = [w for w in ranked if votes[w] >= k]

    print(f"[3/4] cleaning groups A/B/C ({', '.join(strategies)}) ...")
    out_a = run_group(pages, None)
    out_b = run_group(pages, manual)
    chars_a, chars_b = total_chars(out_a), total_chars(out_b)
    hits_b = hit_lines(pages, manual)
    set_b = line_set(hits_b)

    results: dict[str, dict[str, Any]] = {}
    for name, words in strategies.items():
        cleaned = run_group(pages, words)
        set_c = line_set(hit_lines(pages, words))
        results[name] = {
            "words": words,
            "cleaned": cleaned,
            "chars": total_chars(cleaned),
            "hits": len(set_c),
            "recall": len(set_b & set_c) / len(set_b) if set_b else 0.0,
            "extra": sorted(set_c - set_b),
            "missed": sorted(set_b - set_c),
            "missed_words": [
                w for w in manual if not any(w in c or c in w for c in words)
            ],
        }

    print("[4/4] writing report ...")
    for group, cleaned in (("A_none", out_a), ("B_manual", out_b)):
        for key, md in cleaned.items():
            write(os.path.join(out_dir, "markdown", group, f"{key}.md"), md)
    for name, r in results.items():
        for key, md in r["cleaned"].items():
            write(os.path.join(out_dir, "markdown", f"C_{name}", f"{key}.md"), md)
        write(
            os.path.join(out_dir, f"diff_C_{name}_vs_B.md"),
            "## C 多刪的行（需人工判斷是雜訊還是正文）\n\n"
            + "".join(f"- `{k}`: {ln}\n" for k, ln in r["extra"])
            + "\n## C 漏掉的行（B 有刪、C 沒刪＝殘留雜訊）\n\n"
            + "".join(f"- `{k}`: {ln}\n" for k, ln in r["missed"])
            + "\n## 人工清單中 LLM 完全沒涵蓋的詞\n\n"
            + "".join(f"- {w}\n" for w in r["missed_words"]),
        )
        write(
            os.path.join(out_dir, f"proposed_words_{name}.toml"),
            f"# model={args.model} seed={seed} strategy={name}\n"
            + toml_list(r["words"]),
        )
    write(
        os.path.join(out_dir, "samples.json"),
        json.dumps(
            {"seed": seed, "samples": sample_keys, "runs": runs, "raw_runs": raw_runs},
            indent=2,
            ensure_ascii=False,
        ),
    )
    total_cost = sum(u["cost_usd"] for u in usages)
    write(
        os.path.join(out_dir, "cost.json"),
        json.dumps(
            {"calls": len(usages), "total_cost_usd": total_cost, "usages": usages},
            indent=2,
        ),
    )

    def reduction(after: int) -> str:
        return f"{(1 - after / chars_a) * 100:.1f}%" if chars_a else "n/a"

    rows = "".join(
        f"| C {name} | {len(r['words'])} | {r['hits']} | {r['recall'] * 100:.1f}% "
        f"| {len(r['extra'])} | {len(r['missed'])} | {r['chars']} | {reduction(r['chars'])} |\n"
        for name, r in results.items()
    )
    all_words = sorted(votes, key=lambda w: (-votes[w], order[w]))
    summary = (
        f"""# LLM exclude_words 實驗：{args.config}

model: `{args.model}`　頁數: {len(pages)}　每次樣本頁: {len(sample_keys[0])}（比例 {args.sample_ratio}）　seed: {seed}　重跑: {args.repeat}

合併策略：`first`＝只用第 1 次；`voteK`＝在 {args.repeat} 次中至少 K 次出現的詞（vote1＝聯集，vote{args.repeat}＝交集）。

| 組別 | 詞數 | 命中行數 | Recall（vs B） | 多刪行數 | 漏掉行數 | 輸出字元 | 字元減少率（vs A） |
|---|---|---|---|---|---|---|---|
| A none | 0 | 0 | — | — | — | {chars_a} | 0% |
| B manual | {len(manual)} | {count(hits_b)} | 100% | 0 | 0 | {chars_b} | {reduction(chars_b)} |
{rows}
| 指標 | 值 | 判準 |
|---|---|---|
| 各次詞清單穩定度（交集/聯集） | {stability * 100:.1f}%（{len(inter)}/{len(union)}） | ≥ 70% |
| LLM 成本 | ${total_cost:.4f}（{len(usages)} 次呼叫） | — |

Recall 判準 ≥ 80%；多刪行需人工確認皆為雜訊；漏掉行越少越好。
各策略詞清單見 `proposed_words_<策略>.toml`，差異明細見 `diff_C_<策略>_vs_B.md`，每次抽樣頁與各次詞清單見 `samples.json`。
清理後的網頁 markdown 見 `markdown/<A_none｜B_manual｜C_策略>/<page>.md`。

## 每詞得票與全站命中行數

| 詞 | 得票（/{args.repeat}） | 全站命中行數 |
|---|---|---|
"""
        + "".join(
            f"| {w} | {votes[w]} | {n} |\n"
            for w, n in WebpageMarkdownCleaner.count_word_hits(pages, all_words).items()
        )
        + "\n## B 人工清單每詞全站命中行數\n\n| 詞 | 命中行數 |\n|---|---|\n"
        + "".join(
            f"| {w} | {n} |\n"
            for w, n in WebpageMarkdownCleaner.count_word_hits(pages, manual).items()
        )
    )
    write(os.path.join(out_dir, "summary.md"), summary)
    print(f"done → {out_dir}/summary.md")


if __name__ == "__main__":
    main()
