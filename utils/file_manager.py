import json
import os

TEST_DATA_FOLDER_PATH = "./data/test"
WEBSITE_CRAWL_RESULTS_JSON_NAME = "website_crawl_results.json"


def save_crawl_results_as_json(crawl_results: list[dict]) -> None:
    """將爬取結果列表寫入 JSON 檔案。"""
    website_crawl_results_path = os.path.join(
        TEST_DATA_FOLDER_PATH, WEBSITE_CRAWL_RESULTS_JSON_NAME
    )
    os.makedirs(os.path.dirname(website_crawl_results_path), exist_ok=True)
    with open(website_crawl_results_path, "w", encoding="utf-8") as f:
        json.dump(crawl_results, f, ensure_ascii=False, indent=4)


def load_crawl_results_from_json() -> list[dict]:
    """從 JSON 檔案讀取爬取結果列表。"""
    website_crawl_results_path = os.path.join(
        TEST_DATA_FOLDER_PATH, WEBSITE_CRAWL_RESULTS_JSON_NAME
    )
    if not os.path.exists(website_crawl_results_path):
        raise FileNotFoundError(f"{website_crawl_results_path} not found.")
    with open(website_crawl_results_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_crawl_results_as_md(
    craw_results: list[dict],
    markdown_folder_path: str,
    markdown_type: str,
    save_images: bool = False,
) -> None:
    """將爬取結果寫入 Markdown 檔案。"""
    for crawl_result in craw_results:
        markdown_file_name = crawl_result["markdown_file_name"]
        markdown_file_path = os.path.join(markdown_folder_path, markdown_file_name)
        markdown = crawl_result[markdown_type]
        images = crawl_result["images"]

        with open(markdown_file_path, "w", encoding="utf-8") as f:
            f.write(markdown)
            if images and save_images:
                f.write("\n" + "-" * 5 + "\n")
                f.write("Images:\n\n")
                for image in images:
                    f.write(f"![]({image['src']})\n")
                f.write("\n" + "-" * 5 + "\n")
