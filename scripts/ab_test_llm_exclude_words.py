"""方案 4 實驗：LLM 產生 exclude_words vs 人工 exclude_words。

共用同一份原始 fit_markdown（未經 clean_markdown）：
  A. none    無 exclude_words（只用來算字元減少率，不落盤）
  B. manual  configs/website_crawler/{config}.toml 的人工清單
  C. llm     LLM 從樣本頁產生（vote1 聯集），再以行覆蓋率驗證剔除詞

驗證：詞命中的每一行，以「正規化（strip、一般連結去除 URL、圖片保留 URL）後完整相同的行」
計算全站覆蓋率；命中次數中落在低覆蓋行（< --low-coverage）的比例高於門檻 R 的詞被剔除。

離線模式 --from-run：讀取先前輸出目錄的 raw/ 與 samples.json，不爬取、不呼叫 LLM，
並以目前的程式端保護規則重新過濾已保存的 LLM 原始輸出。

輸出到 runs/<timestamp>/ab_test_llm_exclude_words/<config>/。

執行：
  uv run python scripts/ab_test_llm_exclude_words.py --config ncucsie
  uv run python scripts/ab_test_llm_exclude_words.py --config ncucsie \\
      --from-run runs/<ts>/ab_test_llm_exclude_words/ncucsie

取樣策略比較 --arms：每個 arm（<重跑次數>x<抽樣比例>）跑 --trials 次，共用同一份頁面
（--pages-from 讀既有 raw/ 而不爬取，LLM 照常呼叫），輸出到 <out>/compare/：
  uv run python scripts/ab_test_llm_exclude_words.py --config ncucsie \\
      --pages-from runs/<ts>/ab_test_llm_exclude_words/ncucsie \\
      --arms 5x0.1 1x0.1 1x0.2 1x0.3 1x0.5 --trials 5
"""

import argparse
import json
import os
import random
import re
from collections import Counter
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from app.configs.website_crawler_config import WebsiteCrawlerConfig
from app.engines.webpage_markdown_cleaner import (
    ExcludeWordsGenerationError,
    WebpageMarkdownCleaner,
)
from app.engines.website_crawler import WebsiteCrawler

DEFAULT_MODEL = "gpt-5.6-luna"
MAIN_RATIO = 0.1  # 主策略：低覆蓋比例 <= 此值才保留
HOME_KEY = "index"  # 首頁的 raw 檔名（殘留行來源標註用）


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


def line_set(hits: dict[str, list[str]]) -> set[tuple[str, str]]:
    return {(k, ln) for k, v in hits.items() for ln in v}


# 圖片 ![alt](url) 保留 URL（不同圖片即使 alt 相同也視為不同行）；一般連結去除 URL
LINK_URL_RE = re.compile(r"(!\[[^\]]*\]\(\s*[^\s)]+)|\]\(\s*[^\s)]+")


def normalize_line(line: str) -> str:
    """比對「同一行」用：strip 並移除一般連結的 URL，保留連結文字、title 與圖片 URL。"""
    return LINK_URL_RE.sub(lambda m: m.group(1) or "](", line.strip())


def line_coverage(pages: dict[str, str]) -> dict[str, float]:
    """正規化後完整相同的行，出現在多少比例的頁面（每頁只算一次）。"""
    counter: Counter[str] = Counter()
    for md in pages.values():
        counter.update({normalize_line(ln) for ln in md.splitlines() if ln.strip()})
    total = len(pages)
    return {ln: n / total for ln, n in counter.items()} if total else {}


def word_stats(
    pages: dict[str, str], word: str, coverage: dict[str, float], low: float
) -> dict[str, Any]:
    """詞的命中行數，及命中次數中落在低覆蓋行（覆蓋率 < low）的比例。"""
    covs = [
        coverage[normalize_line(ln)]
        for md in pages.values()
        for ln in md.splitlines()
        if ln.strip() and word in ln
    ]
    return {
        "hits": len(covs),
        "low_occ_ratio": sum(c < low for c in covs) / len(covs) if covs else 0.0,
    }


def merge_vote1(runs: list[list[str]]) -> tuple[list[str], Counter[str]]:
    """vote1（各次聯集），依得票多到少排序。"""
    votes = Counter(w for r in runs for w in r)
    order = {w: i for i, w in enumerate(w for r in runs for w in r)}
    return sorted(votes, key=lambda w: (-votes[w], order[w])), votes


def load_raw_pages(run_dir: str) -> dict[str, str]:
    """讀取先前實驗保存的 raw/ 頁面。"""
    raw_dir = os.path.join(run_dir, "raw")
    pages: dict[str, str] = {}
    for name in sorted(os.listdir(raw_dir)):
        with open(os.path.join(raw_dir, name), encoding="utf-8") as f:
            pages[os.path.splitext(name)[0]] = f.read()
    return pages


def load_run(run_dir: str) -> tuple[dict[str, str], dict[str, Any]]:
    """離線模式：讀取先前實驗保存的 raw/ 頁面與 samples.json。"""
    pages = load_raw_pages(run_dir)
    with open(os.path.join(run_dir, "samples.json"), encoding="utf-8") as f:
        return pages, json.load(f)


def reguard(
    raw_runs: list[list[Any]], sample_keys: list[list[str]], pages: dict[str, str]
) -> list[list[str]]:
    """以目前的程式端保護規則重新過濾已保存的 LLM 原始輸出（規則改動後不必重新呼叫 LLM）。"""
    return [
        WebpageMarkdownCleaner.guard_words(raw, {k: pages[k] for k in keys})
        for raw, keys in zip(raw_runs, sample_keys)
    ]


# ── 輸出 ─────────────────────────────────────────────────────────────


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


# ── 取樣策略比較（--arms）────────────────────────────────────────────


def parse_arm(spec: str) -> tuple[int, float]:
    """'5x0.1' → (repeat=5, sample_ratio=0.1)。"""
    repeat, ratio = spec.split("x")
    return int(repeat), float(ratio)


def agg(vals: list[float], scale: float = 1.0, digits: int = 1) -> str:
    """平均（最小–最大）。"""
    if not vals:
        return "n/a"
    v = [x * scale for x in vals]
    return f"{sum(v) / len(v):.{digits}f} ({min(v):.{digits}f}–{max(v):.{digits}f})"


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def stability(word_sets: list[list[str]]) -> float | None:
    """trial 間詞集合的 交集 / 聯集。"""
    if len(word_sets) < 2:
        return None
    sets = [set(ws) for ws in word_sets]
    union = set.union(*sets)
    return len(set.intersection(*sets)) / len(union) if union else 1.0


def run_compare(
    args: argparse.Namespace,
    config: WebsiteCrawlerConfig,
    manual: list[str],
    out_dir: str,
) -> None:
    """比較多組取樣策略（repeat×ratio）：每個 arm 跑 trials 次，共用同一份頁面。"""
    arms: list[str] = args.arms
    if args.pages_from:
        print(f"[1/3] loading pages from {args.pages_from} ...")
        pages = load_raw_pages(args.pages_from)
    else:
        print(f"[1/3] crawling {args.config} ...")
        pages = crawl_site(config)
        for key, md in pages.items():
            write(os.path.join(out_dir, "raw", f"{key}.md"), md)
    base_seed = args.seed if args.seed is not None else random.randrange(2**32)
    print(f"      {len(pages)} pages, base_seed={base_seed}, arms={arms}")

    coverage = line_coverage(pages)
    set_b = line_set(hit_lines(pages, manual))
    static = WebpageMarkdownCleaner()
    stat_cache: dict[str, dict[str, Any]] = {}

    def validated(words: list[str]) -> list[str]:
        for w in words:
            if w not in stat_cache:
                stat_cache[w] = word_stats(pages, w, coverage, args.low_coverage)
        return [w for w in words if stat_cache[w]["low_occ_ratio"] <= MAIN_RATIO]

    cdir = os.path.join(out_dir, "compare")
    write_b = True
    results: dict[str, list[dict[str, Any]]] = {}
    print(f"[2/3] running {len(arms)} arms x {args.trials} trials ...")
    for spec in arms:
        repeat, ratio = parse_arm(spec)
        trials: list[dict[str, Any]] = []
        for t in range(args.trials):
            cleaner = WebpageMarkdownCleaner(
                model=args.model,
                sample_ratio=ratio,
                repeat=repeat,
                max_prompt_tokens=args.max_prompt_tokens,
                seed=base_seed + t,
            )
            try:
                gen = cleaner.generate_exclude_words(pages)
            except ExcludeWordsGenerationError as e:
                print(f"      {spec} trial {t}: {e}")
                trials.append({"error": str(e)})
                break  # 超限或全部失敗，後續 trial 不會不同
            trial: dict[str, Any] = {"gen": gen}
            for label, words in (("raw", gen.words), ("valid", validated(gen.words))):
                set_c = line_set(hit_lines(pages, words))
                trial[label] = {
                    "words": words,
                    "recall": len(set_b & set_c) / len(set_b) if set_b else 0.0,
                    "extra": sorted(set_c - set_b),
                    "missed": sorted(set_b - set_c),
                }
            trials.append(trial)
            tdir = os.path.join(cdir, "trials", spec, f"trial_{t}")
            write(
                os.path.join(tdir, "samples.json"),
                json.dumps(
                    {
                        "seed": gen.seed,
                        "samples": gen.samples,
                        "runs": gen.runs,
                        "raw_runs": gen.raw_runs,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
            )
            write(
                os.path.join(tdir, "cost.json"),
                json.dumps(
                    {
                        "calls": len(gen.usages),
                        "total_cost_usd": gen.cost_usd,
                        "usages": gen.usages,
                    },
                    indent=2,
                ),
            )
            v = trial["valid"]
            print(
                f"      {spec} trial {t}: {len(gen.words)}→{len(v['words'])} words, "
                f"recall {v['recall'] * 100:.1f}%, extra {len(v['extra'])}, "
                f"missed {len(v['missed'])}, ${gen.cost_usd:.4f}"
            )
        results[spec] = trials

        ok = [tr for tr in trials if "gen" in tr]
        if not ok:
            continue
        if write_b:
            for key, md in static.clean_pages(pages, manual).items():
                write(os.path.join(cdir, "markdown", "B_manual", f"{key}.md"), md)
            write_b = False
        first = ok[0]["valid"]["words"]
        write(
            os.path.join(cdir, f"proposed_words_{spec}.toml"),
            f"# model={args.model} arm={spec} trial=0 (validated R<={MAIN_RATIO:g})\n"
            + toml_list(first),
        )
        for key, md in static.clean_pages(pages, first).items():
            write(os.path.join(cdir, "markdown", f"C_{spec}", f"{key}.md"), md)

        # 多刪行／殘留行：跨 trial 出現次數，殘留行標註首頁 vs 其他
        n_ok = len(ok)
        extra_c = Counter(x for tr in ok for x in tr["valid"]["extra"])
        missed_c = Counter(x for tr in ok for x in tr["valid"]["missed"])
        home = sum(1 for (k, _) in missed_c if k == HOME_KEY)
        write(
            os.path.join(cdir, f"diff_{spec}_vs_B.md"),
            f"# {spec} vs B（驗證後，{n_ok} 個 trial 的聯集；括號為出現的 trial 數）\n\n"
            f"## 多刪行（C 刪、B 沒刪；需人工判斷是雜訊還是正文）：{len(extra_c)} 種\n\n"
            + "".join(
                f"- ({n}/{n_ok}) `{k}`: {ln}\n"
                for (k, ln), n in sorted(extra_c.items())
            )
            + f"\n## 殘留行（B 刪、C 沒刪）：{len(missed_c)} 種"
            f"（首頁 `{HOME_KEY}` {home}／其他 {len(missed_c) - home}）\n\n"
            + "".join(
                f"- ({n}/{n_ok}){' [首頁]' if k == HOME_KEY else ''} `{k}`: {ln}\n"
                for (k, ln), n in sorted(missed_c.items())
            ),
        )

    print("[3/3] writing report ...")
    manual_set = set(manual)

    def summarize(spec: str, label: str) -> dict[str, Any] | None:
        ok = [tr for tr in results[spec] if "gen" in tr]
        if not ok:
            return None
        return {
            "n": len(ok),
            "words": [len(tr[label]["words"]) for tr in ok],
            "recall": [tr[label]["recall"] for tr in ok],
            "extra": [len(tr[label]["extra"]) for tr in ok],
            "missed": [len(tr[label]["missed"]) for tr in ok],
            "stab": stability([tr[label]["words"] for tr in ok]),
            "calls": [len(tr["gen"].usages) for tr in ok],
            "cost": [tr["gen"].cost_usd for tr in ok],
            "tokens": [
                mean([u["prompt_tokens"] for u in tr["gen"].usages]) for tr in ok
            ],
        }

    tables = ""
    for label, title in (
        ("raw", "驗證前（vote1）"),
        ("valid", f"驗證後（R≤{MAIN_RATIO:g}）"),
    ):
        rows = ""
        for spec in arms:
            s = summarize(spec, label)
            if s is None:
                err = next((t["error"] for t in results[spec] if "error" in t), "")
                rows += f"| {spec} | 0/{args.trials} | 超限或失敗：{err[:60]} | | | | | | | |\n"
                continue
            stab = "n/a" if s["stab"] is None else f"{s['stab'] * 100:.1f}%"
            rows += (
                f"| {spec} | {s['n']}/{args.trials} | {agg(s['words'], digits=0)} "
                f"| {agg(s['recall'], 100)}% | {agg(s['extra'], digits=0)} "
                f"| {agg(s['missed'], digits=0)} | {stab} | {mean(s['calls']):.0f} "
                f"| ${mean(s['cost']):.4f} | {mean(s['tokens']):,.0f} |\n"
            )
        tables += (
            f"## {title}\n\n"
            "| arm | 成功 trial | 詞數 | Recall vs B (%) | 多刪行 | 殘留行 | 穩定度(交集/聯集) "
            "| 呼叫數/trial | 成本/trial | prompt tokens/呼叫 |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n" + rows + "\n"
        )
    write(
        os.path.join(cdir, "compare.md"),
        f"# 取樣策略比較：{args.config}\n\n"
        f"model: `{args.model}`　頁數: {len(pages)}　trials: {args.trials}　"
        f"base_seed: {base_seed}（trial n 用 base_seed+n）　B: {len(manual)} 詞\n\n"
        "arm 格式 `<重跑次數>x<抽樣比例>`；各欄為 trials 平均（最小–最大）。\n\n"
        + tables,
    )

    # ----- 判準（不自動下結論，只列通過與否）-----
    base_name = "5x0.1"
    base = summarize(base_name, "valid") if base_name in results else None
    verdict = f"# 判準檢查：{args.config}（驗證後、trials 平均）\n\n"
    if base is None:
        verdict += f"基準 arm `{base_name}` 沒有成功的 trial，無法比較。\n"
    else:
        verdict += (
            f"基準 `{base_name}`：recall {mean(base['recall']) * 100:.1f}%、"
            f"多刪 {mean(base['extra']):.1f}、殘留 {mean(base['missed']):.1f}、"
            f"穩定度 {'n/a' if base['stab'] is None else format(base['stab'] * 100, '.1f') + '%'}、"
            f"成本 ${mean(base['cost']):.4f}\n\n"
            "| arm | Recall 不低於基準超過 1pt | 多刪 ≤ 基準+2 | 殘留較少 或 穩定度 +15pt | 成本 ≤ 基準×1.5 | 結論 |\n"
            "|---|---|---|---|---|---|\n"
        )
        for spec in arms:
            if spec == base_name:
                continue
            s = summarize(spec, "valid")
            if s is None:
                verdict += f"| {spec} | 超限或失敗 | | | | 不適用 |\n"
                continue
            c_recall = mean(s["recall"]) >= mean(base["recall"]) - 0.01
            c_extra = mean(s["extra"]) <= mean(base["extra"]) + 2
            c_better = mean(s["missed"]) < mean(base["missed"]) or (
                s["stab"] is not None
                and base["stab"] is not None
                and s["stab"] >= base["stab"] + 0.15
            )
            c_cost = mean(s["cost"]) <= 1.5 * mean(base["cost"])
            if not c_recall:
                conclusion = "維持現行（recall 下降）"
            elif c_recall and c_extra and c_better and c_cost:
                conclusion = "勝出"
            elif c_recall and c_extra and c_cost:
                conclusion = "持平（未在殘留／穩定度上勝出）"
            else:
                conclusion = "未達標"
            mark = lambda b: "✓" if b else "✗"  # noqa: E731
            verdict += (
                f"| {spec} | {mark(c_recall)} ({mean(s['recall']) * 100:.1f}%) "
                f"| {mark(c_extra)} ({mean(s['extra']):.1f}) "
                f"| {mark(c_better)} (殘留 {mean(s['missed']):.1f}) "
                f"| {mark(c_cost)} (${mean(s['cost']):.4f}) | {conclusion} |\n"
            )
        verdict += "\n門檻為暫定值，來自 ncucsie 單一資料點；結論請對照 compare.md 的範圍與 diff 人工判斷。\n"
    write(os.path.join(cdir, "verdict.md"), verdict)

    # ----- 每 arm 詞清單 -----
    words_md = f"# 各 arm 提出的詞：{args.config}\n\n"
    for spec in arms:
        ok = [tr for tr in results[spec] if "gen" in tr]
        if not ok:
            continue
        appear = Counter(w for tr in ok for w in tr["raw"]["words"])
        words_md += (
            f"## {spec}（{len(ok)} trials）\n\n"
            "| 詞 | 出現 trial 數 | 命中行數 | 低覆蓋比例 | 人工清單 | 驗證保留 |\n"
            "|---|---|---|---|---|---|\n"
        )
        for w, n in sorted(appear.items(), key=lambda x: (-x[1], x[0])):
            st = stat_cache[w]
            words_md += (
                f"| {w[:70]} | {n}/{len(ok)} | {st['hits']} "
                f"| {st['low_occ_ratio'] * 100:.1f}% | {'是' if w in manual_set else ''} "
                f"| {'是' if st['low_occ_ratio'] <= MAIN_RATIO else '否'} |\n"
            )
        words_md += "\n"
    write(os.path.join(cdir, "words_by_arm.md"), words_md)
    print(f"done → {cdir}/compare.md")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="nculab")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--sample-ratio", type=float, default=0.1)
    parser.add_argument("--max-prompt-tokens", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument(
        "--from-run",
        default=None,
        help="離線模式：讀取先前實驗輸出目錄的 raw/ 與 samples.json，不爬取、不呼叫 LLM",
    )
    parser.add_argument(
        "--low-coverage",
        type=float,
        default=0.05,
        help="低覆蓋行的界線（行覆蓋率低於此值視為低覆蓋行）",
    )
    parser.add_argument(
        "--low-ratio-thresholds",
        type=float,
        nargs="+",
        default=[0.02, 0.05, MAIN_RATIO, 0.2, 0.5],
        help="低覆蓋比例（按命中次數）門檻：比例高於門檻的詞被剔除",
    )
    parser.add_argument(
        "--arms",
        nargs="+",
        default=None,
        metavar="REPEATxRATIO",
        help="取樣策略比較模式：例如 5x0.1 1x0.1 1x0.2 1x0.3 1x0.5（重跑次數x抽樣比例）",
    )
    parser.add_argument(
        "--trials", type=int, default=5, help="--arms 模式：每個 arm 的重複試驗次數"
    )
    parser.add_argument(
        "--pages-from",
        default=None,
        help="--arms 模式：只載入先前輸出目錄的 raw/ 頁面（不爬取），但照常呼叫 LLM",
    )
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

    if args.arms:
        run_compare(args, config, manual, out_dir)
        return

    usages: list[dict[str, float]] = []
    if args.from_run:
        print(f"[1/4] loading {args.from_run} ...")
        pages, saved = load_run(args.from_run)
        seed, sample_keys = saved["seed"], saved["samples"]
        raw_runs = saved["raw_runs"]
        runs = reguard(raw_runs, sample_keys, pages)
    else:
        print(f"[1/4] crawling {args.config} ...")
        pages = crawl_site(config)
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
        seed, sample_keys = generation.seed, generation.samples
        runs, raw_runs, usages = generation.runs, generation.raw_runs, generation.usages
    print(f"      {len(pages)} pages, seed={seed}")

    # ----- vote1 與低覆蓋比例驗證 -----
    coverage = line_coverage(pages)
    vote1, votes = merge_vote1(runs)
    stats = {w: word_stats(pages, w, coverage, args.low_coverage) for w in vote1}
    strategies: dict[str, list[str]] = {"vote1": vote1}
    for r in args.low_ratio_thresholds:
        strategies[f"vote1_lowocc_R{r:g}"] = [
            w for w in vote1 if stats[w]["low_occ_ratio"] <= r
        ]

    print(f"[3/4] cleaning A/B/C ({len(strategies)} strategies) ...")
    cleaner_static = WebpageMarkdownCleaner()
    chars_a = sum(len(md) for md in pages.values())
    out_b = cleaner_static.clean_pages(pages, manual)
    chars_b = sum(len(v) for v in out_b.values())
    set_b = line_set(hit_lines(pages, manual))

    results: dict[str, dict[str, Any]] = {}
    for name, words in strategies.items():
        cleaned = cleaner_static.clean_pages(pages, words)
        set_c = line_set(hit_lines(pages, words))
        results[name] = {
            "words": words,
            "cleaned": cleaned,
            "chars": sum(len(v) for v in cleaned.values()),
            "recall": len(set_b & set_c) / len(set_b) if set_b else 0.0,
            "extra": sorted(set_c - set_b),
            "missed": sorted(set_b - set_c),
        }

    print("[4/4] writing report ...")
    if not args.from_run:
        for key, md in pages.items():
            write(os.path.join(out_dir, "raw", f"{key}.md"), md)
    main_name = f"vote1_lowocc_R{MAIN_RATIO:g}"
    for key, md in out_b.items():
        write(os.path.join(out_dir, "markdown", "B_manual", f"{key}.md"), md)
    for key, md in results[main_name]["cleaned"].items():
        write(os.path.join(out_dir, "markdown", "C_main", f"{key}.md"), md)
    for label, name in (("vote1", "vote1"), ("main", main_name)):
        r = results[name]
        write(
            os.path.join(out_dir, f"diff_C_{label}_vs_B.md"),
            "## C 多刪的行（需人工判斷是雜訊還是正文）\n\n"
            + "".join(f"- `{k}`: {ln}\n" for k, ln in r["extra"])
            + "\n## C 漏掉的行（B 有刪、C 沒刪＝殘留雜訊）\n\n"
            + "".join(f"- `{k}`: {ln}\n" for k, ln in r["missed"]),
        )
        write(
            os.path.join(out_dir, f"proposed_words_{label}.toml"),
            f"# model={args.model} seed={seed} strategy={name}\n"
            + toml_list(r["words"]),
        )
    write(
        os.path.join(out_dir, "samples.json"),
        json.dumps(
            {
                "seed": seed,
                "samples": sample_keys,
                "runs": runs,
                "raw_runs": raw_runs,
            },
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

    manual_set = set(manual)
    rows = "".join(
        f"| {name} | {len(r['words'])} | {r['recall'] * 100:.1f}% "
        f"| {len(r['extra'])} | {len(r['missed'])} | {reduction(r['chars'])} |\n"
        for name, r in results.items()
    )
    word_rows = "".join(
        f"| {w[:70]} | {votes[w]} | {stats[w]['hits']} "
        f"| {stats[w]['low_occ_ratio'] * 100:.1f}% "
        f"| {'是' if w in manual_set else ''} "
        f"| {'是' if w in results[main_name]['words'] else '否（被驗證剔除）'} |\n"
        for w in sorted(stats, key=lambda w: stats[w]["low_occ_ratio"], reverse=True)
    )
    summary = f"""# LLM exclude_words 實驗：{args.config}

model: `{args.model}`　頁數: {len(pages)}　每次樣本頁: {len(sample_keys[0])}　seed: {seed}　重跑: {len(sample_keys)}

低覆蓋行：正規化後完整相同的行，出現在全站 < {args.low_coverage * 100:g}% 的頁面。
`vote1_lowocc_R{{r}}`：vote1 詞清單中，命中次數落在低覆蓋行的比例 ≤ r 的詞。主策略 R={MAIN_RATIO:g}。

| 策略 | 詞數 | Recall（vs B） | 多刪行 | 漏掉行 | 字元減少率（vs A） |
|---|---|---|---|---|---|
| B manual（{len(manual)} 詞） | {len(manual)} | 100% | 0 | 0 | {reduction(chars_b)} |
{rows}
LLM 成本：${total_cost:.4f}（{len(usages)} 次呼叫；離線讀檔不計）

## vote1 每詞

| 詞 | 得票 | 命中行數 | 低覆蓋比例（按次數） | 人工清單 | 主策略保留 |
|---|---|---|---|---|---|
{word_rows}"""
    write(os.path.join(out_dir, "summary.md"), summary)
    print(f"done → {out_dir}/summary.md")


if __name__ == "__main__":
    main()
