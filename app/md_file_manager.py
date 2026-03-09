import os
import shutil

WEBPAGE_FIT_MARKDOWN_FOLDER_PATH = "./data/test/webpage_fit_markdown"
WEBPAGE_ENHANCED_MARKDOWN_FOLDER_PATH = "./data/test/webpage_enhanced_markdown"


class MdFileManager:
    @classmethod
    def save_crawl_results_as_md(
        cls, craw_results: list[dict], markdown_type: str
    ) -> None:
        """將所有爬取結果寫入 Markdown 檔案。"""
        match markdown_type:
            case "fit_markdown":
                markdown_folder_path = WEBPAGE_FIT_MARKDOWN_FOLDER_PATH
            case "enhanced_markdown":
                markdown_folder_path = WEBPAGE_ENHANCED_MARKDOWN_FOLDER_PATH
            case _:
                raise ValueError(f"Unknown markdown type: {markdown_type}")
        shutil.rmtree(markdown_folder_path, ignore_errors=True)
        os.makedirs(markdown_folder_path, exist_ok=True)

        for filtered_result in craw_results:
            markdown_file_name = filtered_result["markdown_file_name"]
            markdown_file_path = os.path.join(markdown_folder_path, markdown_file_name)
            url = filtered_result["url"]
            # markdown_type: "fit_markdown" or "enhanced_markdown"
            markdwon = filtered_result[markdown_type]
            images = filtered_result["images"]

            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write("-" * 5 + "\n")
                f.write(f"URL: {url}\n")
                f.write("-" * 5 + "\n")
                f.write(markdwon)

                # if images and markdown_type == "fit_markdown":
                if images:  # test
                    f.write("\n" + "-" * 5 + "\n")
                    f.write("Images:\n\n")
                    for image in images:
                        f.write(f"![]({image['src']})\n")
                    f.write("\n" + "-" * 5 + "\n")
