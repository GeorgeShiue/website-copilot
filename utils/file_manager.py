import json
import os
import shutil

WEBSITE_CRAWL_RESULTS_JSON_PATH = "./data/test/website_crawl_results.json"
WEBPAGE_FIT_MARKDOWN_FOLDER_PATH = "./data/test/webpage_fit_markdown"
WEBPAGE_ENHANCED_MARKDOWN_FOLDER_PATH = "./data/test/webpage_enhanced_markdown"

MARKDOWN_TYPE_TO_FOLDER_PATH = {
    "fit_markdown": WEBPAGE_FIT_MARKDOWN_FOLDER_PATH,
    "enhanced_markdown": WEBPAGE_ENHANCED_MARKDOWN_FOLDER_PATH,
}


def save_crawl_results_as_json(crawl_results: list[dict]) -> None:
    """將爬取結果列表寫入 JSON 檔案。"""
    os.makedirs(os.path.dirname(WEBSITE_CRAWL_RESULTS_JSON_PATH), exist_ok=True)
    with open(WEBSITE_CRAWL_RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(crawl_results, f, ensure_ascii=False, indent=4)


def load_crawl_results_from_json() -> list[dict]:
    """從 JSON 檔案讀取爬取結果列表。"""
    if not os.path.exists(WEBSITE_CRAWL_RESULTS_JSON_PATH):
        raise FileNotFoundError(f"{WEBSITE_CRAWL_RESULTS_JSON_PATH} not found.")
    with open(WEBSITE_CRAWL_RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_crawl_results_as_md(
    craw_results: list[dict],
    markdown_type: str,
    save_images: bool = False,
) -> None:
    """將爬取結果寫入 Markdown 檔案。"""
    markdown_folder_path = MARKDOWN_TYPE_TO_FOLDER_PATH[markdown_type]
    shutil.rmtree(markdown_folder_path, ignore_errors=True)
    os.makedirs(markdown_folder_path, exist_ok=True)

    for filtered_result in craw_results:
        markdown_file_name = filtered_result["markdown_file_name"]
        markdown_file_path = os.path.join(markdown_folder_path, markdown_file_name)
        markdown = filtered_result[markdown_type]
        images = filtered_result["images"]

        with open(markdown_file_path, "w", encoding="utf-8") as f:
            f.write(markdown)
            if images and save_images:
                f.write("\n" + "-" * 5 + "\n")
                f.write("Images:\n\n")
                for image in images:
                    f.write(f"![]({image['src']})\n")
                f.write("\n" + "-" * 5 + "\n")
