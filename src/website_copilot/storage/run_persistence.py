"""Module-specific persistence & discovery functions for run results.

Extracted from RunManager to separate persistence/discovery concerns
from path management. Functions here are stateless and accept explicit
parameters instead of relying on RunManager instance state.
"""

import json
import logging
import os
from collections.abc import Iterator, Mapping
from typing import Any

from website_copilot.schemas import GenerationResult

QUERY_MD_FILE_PREFIX = "query_"
RESULTS_JSON_NAME = "results.json"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _filter_run_folders(base_folder: str) -> list[str]:
    """篩選出符合實驗資料夾命名規則的資料夾名稱列表。"""
    run_folder_names = [name for name in os.listdir(base_folder) if is_run_folder(name)]
    if not run_folder_names:
        raise FileNotFoundError(f"No run folders found in {base_folder}.")
    return run_folder_names


def _iter_site_run_folders(
    base_folder: str, module_name: str, site_id: str
) -> Iterator[str]:
    """由新到舊列出存在的 runs/<ts>/<module>/<site_id>/（只認時間戳資料夾）。

    Raises:
        FileNotFoundError: base_folder 內沒有任何時間戳資料夾時。
    """
    for folder_name in sorted(_filter_run_folders(base_folder), reverse=True):
        site_folder = os.path.join(base_folder, folder_name, module_name, site_id)
        if os.path.isdir(site_folder):
            yield site_folder


def _walk_sorted(folder: str) -> Iterator[tuple[str, list[str]]]:
    """以固定順序（目錄與檔名排序）由上而下走訪，yield (目前資料夾, 其中的檔名)。"""
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        files.sort()
        yield root, files


def _render_query_result_md(result: dict) -> str:
    """將單次 query 的結果渲染為獨立的 Markdown 檔案（內部使用）。"""
    lines: list[str] = []
    lines.append(f"# Query #{result.get('index')}: {result.get('query', '')}")
    timestamp = result.get("timestamp")
    if timestamp:
        lines.append("")
        lines.append(f"> {timestamp}")
    lines.append("")
    lines.append("# Response")
    lines.append("")
    lines.append(str(result.get("response", "")))
    lines.append("")

    evaluation = result.get("evaluation")
    if evaluation:
        lines.append("# Evaluation")
        lines.append("")
        lines.append("| Metric | Passing | Score | Reason |")
        lines.append("|--------|:-------:|:-----:|--------|")
        for metric in ("faithfulness", "relevancy"):
            ev = evaluation.get(metric)
            if ev is None:
                continue
            passing = ev.get("passing")
            mark = ":white_check_mark:" if passing else ":x:"
            score = ev.get("score")
            score_text = _format_score(score)
            reason = _escape_md_cell((ev.get("feedback") or "").replace("\n", " "))
            lines.append(
                f"| {metric.capitalize()} | {mark} | {score_text} | {reason} |"
            )
        lines.append("")

    sources = result.get("sources", [])
    lines.append(f"# Sources ({len(sources)})")
    lines.append("")
    if sources:
        lines.append("| # | Page | Type | Score | URL |")
        lines.append("|---|------|------|:-----:|-----|")
        for i, source in enumerate(sources, start=1):
            lines.append(
                f"| {i} | {_escape_md_cell(source.get('page_title', ''))} "
                f"| {_escape_md_cell(source.get('page_type', ''))} "
                f"| {_format_score(source.get('score'))} "
                f"| {_escape_md_cell(source.get('url', ''))} |"
            )
        lines.append("")
        for i, source in enumerate(sources, start=1):
            content = source.get("content", "")
            lines.append(f"**#{i} 內容片段：**")
            lines.append("")
            lines.append(_to_blockquote(content))
            lines.append("")

    return "\n".join(lines)


def _format_score(score: object) -> str:
    return f"{score:.4f}" if isinstance(score, (int, float)) else "-"


def _escape_md_cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _to_blockquote(text: object) -> str:
    """將多行文字轉為每行皆為引用區塊的 Markdown。"""
    return "\n".join(f"> {line}" for line in str(text).splitlines())


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def is_run_folder(name: str) -> bool:
    """資料夾名稱是否為 run 時間戳資料夾（如 20260830_172330：以 20 開頭、共 15 字元）。"""
    return name.startswith("20") and len(name) == 15


def load_latest_results(
    base_folder: str,
    module_name: str,
    site_id: str,
) -> dict[str, dict]:
    """從 JSON 檔案讀取指定站點最新一次模組執行的結果。

    只搜尋 runs/<ts>/<module>/<site_id>/；找不到該站點的結果時報錯，不退回其他站點。
    較新的 run 有該站點資料夾但沒有 results.json（失敗的 run）時，改用較舊的 run。

    Args:
        base_folder: runs/ 根目錄。
        module_name: 模組資料夾名稱（如 "website_crawler"）。
        site_id: 站點識別碼。

    Returns:
        最新一份 results.json 的 dict 內容。
    """
    logger.info(
        "Looking for %s results of %s in %s...", module_name, site_id, base_folder
    )
    for site_folder in _iter_site_run_folders(base_folder, module_name, site_id):
        for root, files in _walk_sorted(site_folder):
            if RESULTS_JSON_NAME in files:
                results_json_path = os.path.join(root, RESULTS_JSON_NAME)
                logger.info("Latest results found at: %s", results_json_path)
                with open(results_json_path, "r", encoding="utf-8") as f:
                    return json.load(f)

    raise FileNotFoundError(
        f"No {module_name} results of site '{site_id}' found in {base_folder}."
    )


def load_latest_run_path(base_folder: str, module_name: str, site_id: str) -> str:
    """回傳指定站點最新一次模組執行的 run path（results/ 的上一層）。

    只搜尋 runs/<ts>/<module>/<site_id>/；規則與 load_latest_results 相同。

    Args:
        base_folder: runs/ 根目錄。
        module_name: 模組資料夾名稱（如 "augmenter"）。
        site_id: 站點識別碼。

    Returns:
        最新一份包含 results/ 的 run path。
    """
    logger.info("Looking for %s run path in %s...", module_name, base_folder)
    for site_folder in _iter_site_run_folders(base_folder, module_name, site_id):
        for root, _files in _walk_sorted(site_folder):
            if os.path.basename(root) == "results":
                run_path = os.path.dirname(root)
                logger.info("Found latest run path at: %s", run_path)
                return run_path

    raise FileNotFoundError(f"No {module_name} run path found in {base_folder}.")


# ---------------------------------------------------------------------------
# Markdown persistence
# ---------------------------------------------------------------------------


def save_results_as_md(
    results: dict[str, dict],
    folder_path: str,
    markdown_type: str,
) -> None:
    """將爬取結果寫入 Markdown 檔案。"""
    for page_title, result in results.items():
        md_file_path = page_title + ".md"
        markdown_file_path = os.path.join(folder_path, md_file_path)
        markdown = result[markdown_type]

        with open(markdown_file_path, "w", encoding="utf-8") as f:
            f.write(markdown)


def save_document_files(files: Mapping[str, Any], folder_path: str) -> None:
    """把文件原檔寫入 folder_path（檔名為 file.file_name），並清掉資料夾內已不屬於本次結果的舊檔。

    files 的值需有 file_name 與 content 屬性（見 DocumentFile）；沒有文件時資料夾內容一併清空。
    """
    os.makedirs(folder_path, exist_ok=True)
    keep = {file.file_name for file in files.values()}
    for name in os.listdir(folder_path):
        if name not in keep:
            os.remove(os.path.join(folder_path, name))
    for file in files.values():
        with open(os.path.join(folder_path, file.file_name), "wb") as f:
            f.write(file.content)


def save_generated_exclude_words(
    result: GenerationResult, raw_pages: dict[str, str], run_path: str
) -> None:
    """落盤 LLM 產生的 exclude_words 報告（exclude_words_report.json）。"""
    report = {
        "seed": result.seed,
        "words": [
            {
                "word": w,
                "votes": result.votes[w],
                "hit_lines": result.hits[w],
                "low_occ_ratio": result.stats[w]["low_occ_ratio"],
            }
            for w in result.words
        ],
        "rejected": [
            {
                "word": w,
                "votes": result.votes[w],
                "low_occ_ratio": ratio,
            }
            for w, ratio in result.rejected.items()
        ],
        "samples": result.samples,
        "runs": result.runs,
        "raw_runs": result.raw_runs,
        "usages": result.usages,
        "total_cost_usd": result.cost_usd,
    }
    with open(os.path.join(run_path, "exclude_words.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def save_query_results_as_md(
    query_results: dict,
    folder_path: str,
) -> None:
    """將每次 query 與回覆各寫為一份 Markdown 檔案。"""
    for result in query_results.get("results", []):
        index = result.get("index", 1)
        markdown = _render_query_result_md(result)
        md_file_name = f"{QUERY_MD_FILE_PREFIX}{index}.md"
        md_file_path = os.path.join(folder_path, md_file_name)
        os.makedirs(os.path.dirname(md_file_path), exist_ok=True)
        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(markdown)
