"""重抽次數 k 的離線模擬：用已保存的單次 LLM 提議池，重抽樣估計「k 次 × 10% + 聯集」的表現。

池子來源：runs/*/ab_test_llm_exclude_words/<config>/compare/trials/{5x0.1,1x0.1}/trial_*/samples.json
中每次呼叫（samples[i] 的頁面 key、runs[i] 過濾後的詞）。每次呼叫是對頁面獨立的 10% 抽樣，
因此依「抽到的頁面集合」去重（重複使用相同 seed 會抽到相同頁面，不算獨立樣本）。

對每個 k：從池子隨機抽 k 筆做聯集（vote1），套用行覆蓋率驗證（R<=MAIN_RATIO），
計算 recall / 多刪行 / 殘留行，重複 --draws 次。不呼叫 LLM。

執行：
  uv run python scripts/sim_llm_exclude_words_repeat.py --config ncucsie \\
      --pages-from runs/<ts>/ab_test_llm_exclude_words/ncucsie --ks 1 2 3 5 8 10
"""

import argparse
import glob
import json
import os
import random
import statistics
from datetime import datetime

from ab_test_llm_exclude_words import (
    MAIN_RATIO,
    hit_lines,
    line_coverage,
    line_set,
    load_manual_baseline,
    load_raw_pages,
    word_stats,
    write,
)
from dotenv import load_dotenv


POOL_ARMS = ("5x0.1", "1x0.1")


def load_pool(config: str) -> tuple[list[list[str]], list[frozenset[str]], int]:
    """回傳 (池子：每筆為一次呼叫通過保護的詞, 對應的抽樣頁面 key, 去重前的呼叫總數)。"""
    pattern = os.path.join(
        "runs", "*", "ab_test_llm_exclude_words", config, "compare", "trials",
        "*", "trial_*", "samples.json",
    )  # fmt: skip
    seen: dict[frozenset[str], list[str]] = {}
    total = 0
    for path in sorted(glob.glob(pattern)):
        if path.split("/trials/")[1].split("/")[0] not in POOL_ARMS:
            continue
        with open(path, encoding="utf-8") as f:
            saved = json.load(f)
        for keys, words in zip(saved["samples"], saved["runs"]):
            total += 1
            seen.setdefault(frozenset(keys), words)
    return list(seen.values()), list(seen), total


def pct(sorted_vals: list[float], p: float) -> float:
    return sorted_vals[min(len(sorted_vals) - 1, int(p * len(sorted_vals)))]


def ranks(vals: list[float]) -> list[float]:
    """平均名次（處理同分）。"""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        for t in range(i, j + 1):
            out[order[t]] = (i + j) / 2
        i = j + 1
    return out


def coverage_analysis(args, pool, pool_keys, kept, evaluate, n_pages, rng) -> None:
    """隨機抽 k 筆，看「不重複頁數」與 recall／殘留的關係（互斥抽樣機制的免費檢查）。"""
    k = args.coverage_k
    recs = []
    for _ in range(args.draws):
        idx = rng.sample(range(len(pool)), k)
        pages_seen = len(set().union(*(pool_keys[i] for i in idx)))
        valid = {w for i in idx for w in pool[i]} & kept
        recall, extra, missed = evaluate(valid)
        recs.append((pages_seen, recall, missed, extra, len(valid)))
    cov = [r[0] for r in recs]
    recall = [r[1] for r in recs]
    missed = [r[2] for r in recs]
    words = [r[4] for r in recs]
    corr = statistics.correlation
    rc, rr, rm = ranks(cov), ranks(recall), ranks(missed)
    order = sorted(range(len(recs)), key=lambda i: cov[i])
    q = len(order) // 5
    groups = {
        "涵蓋最低 20%": order[:q],
        "中間 60%": order[q : len(order) - q],
        "涵蓋最高 20%": order[len(order) - q :],
    }
    rows = ""
    for name, ids in groups.items():
        rows += (
            f"| {name} | {min(cov[i] for i in ids)}–{max(cov[i] for i in ids)} "
            f"| {statistics.mean(cov[i] for i in ids):.1f} "
            f"| {statistics.mean(recall[i] for i in ids) * 100:.2f}% "
            f"| {statistics.mean(missed[i] for i in ids):.1f} "
            f"| {sum(recall[i] < 0.95 for i in ids) / len(ids) * 100:.1f}% |\n"
        )
    lo, hi = groups["涵蓋最低 20%"], groups["涵蓋最高 20%"]
    text = (
        f"# 涵蓋量與品質的關係：{args.config}，k={k}\n\n"
        f"池子 {len(pool)} 筆；隨機抽 {args.draws} 組 {k} 筆；全站 {n_pages} 頁。"
        f"互斥抽樣的涵蓋量為 {k}×每次頁數。\n\n"
        f"不重複頁數：平均 {statistics.mean(cov):.1f}，範圍 {min(cov)}–{max(cov)}。\n\n"
        "| 相關性（不重複頁數 vs） | Pearson | Spearman |\n|---|---|---|\n"
        f"| recall | {corr(cov, recall):+.3f} | {corr(rc, rr):+.3f} |\n"
        f"| 殘留行 | {corr(cov, missed):+.3f} | {corr(rc, rm):+.3f} |\n"
        f"| 詞數 | {corr(cov, words):+.3f} | |\n\n"
        "| 分組 | 不重複頁數範圍 | 平均頁數 | Recall 平均 | 殘留行 平均 | P(recall<95%) |\n"
        "|---|---|---|---|---|---|\n" + rows + "\n"
        f"高涵蓋組 − 低涵蓋組：recall {(statistics.mean(recall[i] for i in hi) - statistics.mean(recall[i] for i in lo)) * 100:+.2f}pt、"
        f"殘留 {statistics.mean(missed[i] for i in hi) - statistics.mean(missed[i] for i in lo):+.1f} 行\n"
    )
    out = os.path.join(
        "runs",
        datetime.now().strftime("%Y%m%d_%H%M%S"),
        "sim_llm_exclude_words_repeat",
        args.config,
        f"coverage_k{k}.md",
    )
    write(out, text)
    print(text)
    print(f"done → {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="ncucsie")
    parser.add_argument("--pages-from", required=True)
    parser.add_argument("--ks", type=int, nargs="+", default=[1, 2, 3, 5, 8, 10])
    parser.add_argument("--draws", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--coverage-k",
        type=int,
        default=None,
        help="涵蓋量分析：隨機抽 k 筆，檢查不重複頁數與 recall／殘留的關係（不跑 k 比較）",
    )
    parser.add_argument("--low-coverage", type=float, default=0.05)
    parser.add_argument(
        "--cost-per-call",
        type=float,
        default=None,
        help="單次呼叫成本（USD，無快取）；未指定則不列成本",
    )
    args = parser.parse_args()

    load_dotenv()
    manual = load_manual_baseline(args.config)
    pages = load_raw_pages(args.pages_from)
    pool, pool_keys, total = load_pool(args.config)
    print(f"pool: {len(pool)} distinct calls (from {total} calls), {len(pages)} pages")
    if max(args.ks) > len(pool):
        raise SystemExit(f"k={max(args.ks)} 大於池子 {len(pool)}")

    coverage = line_coverage(pages)
    all_words = sorted({w for words in pool for w in words})
    kept = {
        w
        for w in all_words
        if word_stats(pages, w, coverage, args.low_coverage)["low_occ_ratio"]
        <= MAIN_RATIO
    }
    word_lines = {w: line_set(hit_lines(pages, [w])) for w in all_words}
    set_b = line_set(hit_lines(pages, manual))

    def evaluate(words: set[str]) -> tuple[float, int, int]:
        c: set[tuple[str, str]] = set()
        for w in words:
            c |= word_lines[w]
        return (
            len(set_b & c) / len(set_b) if set_b else 0.0,
            len(c - set_b),
            len(set_b - c),
        )

    rng = random.Random(args.seed)
    if args.coverage_k:
        coverage_analysis(args, pool, pool_keys, kept, evaluate, len(pages), rng)
        return
    rows = []
    prev_missed = None
    for k in args.ks:
        recs = []
        for _ in range(args.draws):
            union = {w for i in rng.sample(range(len(pool)), k) for w in pool[i]}
            valid = union & kept
            recall, extra, missed = evaluate(valid)
            recs.append((recall, extra, missed, len(valid), union, valid))
        rec_sorted = sorted(r[0] for r in recs)
        miss_sorted = sorted(r[2] for r in recs)
        mean_missed = sum(r[2] for r in recs) / len(recs)
        # 穩定度：相鄰兩次抽樣的詞集合 Jaccard
        jac = [
            len(a[5] & b[5]) / len(a[5] | b[5])
            for a, b in zip(recs[::2], recs[1::2])
            if a[5] | b[5]
        ]
        rows.append(
            {
                "k": k,
                "words": sum(r[3] for r in recs) / len(recs),
                "recall": sum(r[0] for r in recs) / len(recs),
                "recall_p5": pct(rec_sorted, 0.05),
                "recall_p95": pct(rec_sorted, 0.95),
                "p_lt95": sum(r[0] < 0.95 for r in recs) / len(recs),
                "extra": sum(r[1] for r in recs) / len(recs),
                "missed": mean_missed,
                "missed_p5": pct(miss_sorted, 0.05),
                "missed_p95": pct(miss_sorted, 0.95),
                "jaccard": sum(jac) / len(jac) if jac else 0.0,
                "delta_missed": None
                if prev_missed is None
                else mean_missed - prev_missed,
            }
        )
        prev_missed = mean_missed
        print(
            f"k={k}: recall {rows[-1]['recall'] * 100:.1f}% "
            f"missed {mean_missed:.0f} extra {rows[-1]['extra']:.1f}"
        )

    out_dir = os.path.join(
        "runs",
        datetime.now().strftime("%Y%m%d_%H%M%S"),
        "sim_llm_exclude_words_repeat",
        args.config,
    )
    cost_col = args.cost_per_call is not None
    table = (
        "| k | 詞數 | Recall 平均（p5–p95） | P(recall<95%) | 多刪行 | 殘留行 平均（p5–p95） "
        "| 較前一個 k 殘留變化 | 穩定度（Jaccard） |"
        + (" 成本/站台 |" if cost_col else "")
        + "\n|---|---|---|---|---|---|---|---|"
        + ("---|" if cost_col else "")
        + "\n"
    )
    for r in rows:
        delta = "" if r["delta_missed"] is None else f"{r['delta_missed']:+.0f}"
        table += (
            f"| {r['k']} | {r['words']:.1f} | {r['recall'] * 100:.1f}%"
            f"（{r['recall_p5'] * 100:.1f}–{r['recall_p95'] * 100:.1f}） "
            f"| {r['p_lt95'] * 100:.1f}% | {r['extra']:.1f} "
            f"| {r['missed']:.0f}（{r['missed_p5']}–{r['missed_p95']}） | {delta} "
            f"| {r['jaccard'] * 100:.1f}% |"
            + (f" ${r['k'] * args.cost_per_call:.3f} |" if cost_col else "")  # type: ignore[operator]
            + "\n"
        )
    write(
        os.path.join(out_dir, "summary.md"),
        f"# 重抽次數 k 離線模擬：{args.config}\n\n"
        f"池子：{len(pool)} 筆獨立 10% 抽樣的 LLM 提議（去重前 {total} 筆）；"
        f"頁數 {len(pages)}；B {len(manual)} 詞；每個 k 抽 {args.draws} 次、"
        f"不放回；驗證 R≤{MAIN_RATIO:g}。\n\n"
        "k 接近池子大小時各次抽樣高度重疊，範圍（p5–p95）會被低估。\n\n" + table,
    )
    write(
        os.path.join(out_dir, "pool.json"),
        json.dumps(pool, ensure_ascii=False, indent=1),
    )
    print(f"done → {out_dir}/summary.md")


if __name__ == "__main__":
    main()
