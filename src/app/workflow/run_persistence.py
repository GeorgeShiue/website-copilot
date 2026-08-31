"""Module-specific persistence & discovery functions for run results.

Extracted from RunManager to separate persistence/discovery concerns
from path management. Functions here are stateless and accept explicit
parameters instead of relying on RunManager instance state.
"""

import json
import logging
import os

QUERY_MD_FILE_PREFIX = "query_"
RESULTS_JSON_NAME = "results.json"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------


def _filter_run_folders(base_folder: str) -> list[str]:
    """篩選出符合實驗資料夾命名規則的資料夾名稱列表。"""
    folder_names = os.listdir(base_folder)
    run_folder_names = []
    for folder_name in folder_names:
        if folder_name.startswith("20") and len(folder_name) == 15:
            run_folder_names.append(folder_name)
    if not run_folder_names:
        raise FileNotFoundError(f"No run folders found in {base_folder}.")
    return run_folder_names


def load_latest_results(
    base_folder: str,
    module_name: str = "website_crawler",
) -> dict[str, dict]:
    """從 JSON 檔案讀取最新模組的爬取結果列表。

    Args:
        base_folder: runs/ 根目錄（如 "runs" 或 "chats"）。
        module_name: 模組資料夾名稱（如 "website_crawler"）。

    Returns:
        最新一份 results.json 的 dict 內容。
    """
    logger.info("Looking for run folders in %s...", base_folder)
    run_folder_names = _filter_run_folders(base_folder)

    latest_results_json_path = ""
    for folder_name in sorted(run_folder_names, reverse=True):
        module_folder_path = os.path.join(base_folder, folder_name, module_name)
        if not os.path.isdir(module_folder_path):
            continue

        for root, dirs, files in os.walk(module_folder_path):
            dirs.sort()
            files.sort()
            if RESULTS_JSON_NAME in files:
                latest_results_json_path = os.path.join(root, RESULTS_JSON_NAME)
                break

        if latest_results_json_path:
            break

    if not latest_results_json_path:
        raise FileNotFoundError(f"No {module_name} results found in {base_folder}.")

    if not os.path.isfile(latest_results_json_path):
        raise FileNotFoundError(
            f"Failed to load results from {latest_results_json_path}."
        )

    logger.info("Latest results found at: %s", latest_results_json_path)
    with open(latest_results_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_latest_run_path(
    base_folder: str,
    module_name: str = "webpage_image_summarizer",
) -> str:
    """回傳最新指定模組的 run path（results 的上一層）。

    Args:
        base_folder: runs/ 根目錄。
        module_name: 模組資料夾名稱。

    Returns:
        最新一份包含 results/ 的 run path。
    """
    logger.info("Looking for %s run path in %s...", module_name, base_folder)
    run_folder_names = _filter_run_folders(base_folder)

    latest_run_path = ""
    for folder_name in sorted(run_folder_names, reverse=True):
        module_folder_path = os.path.join(base_folder, folder_name, module_name)
        if not os.path.isdir(module_folder_path):
            continue

        for root, dirs, files in os.walk(module_folder_path):
            dirs.sort()
            files.sort()
            if os.path.basename(root) == "results":
                latest_run_path = os.path.dirname(root)
                break

        if latest_run_path:
            break

    if not latest_run_path:
        raise FileNotFoundError(f"No {module_name} run path found in {base_folder}.")

    logger.info("Found latest run path at: %s", latest_run_path)
    return latest_run_path


# ---------------------------------------------------------------------------
# Markdown persistence
# ---------------------------------------------------------------------------


def save_results_as_md(
    results: dict[str, dict],
    folder_path: str,
    markdown_type: str,
    save_images: bool = False,
) -> None:
    """將爬取結果寫入 Markdown 檔案。"""
    for page_title, result in results.items():
        md_file_path = page_title + ".md"
        markdown_file_path = os.path.join(folder_path, md_file_path)
        markdown = result[markdown_type]
        images = result["images"]

        with open(markdown_file_path, "w", encoding="utf-8") as f:
            f.write(markdown)
            if images and save_images:
                f.write("\n" + "-" * 5 + "\n")
                f.write("Images:\n\n")
                for image in images:
                    f.write(f"![]({image['src']})\n")
                f.write("\n" + "-" * 5 + "\n")


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


# ---------------------------------------------------------------------------
# Markdown rendering helpers
# ---------------------------------------------------------------------------


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
