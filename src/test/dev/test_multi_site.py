"""小規模多網站知識庫驗證腳本。

對 nculab 與 ncucsie 兩個網站各爬取 10 頁，執行圖片摘要與 RAG 建庫，
驗證 DataManager 多 site 隔離機制及 publish_run_metadata 是否正常運作。

執行：uv run python src/test/dev/test_multi_site.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.configs.workflow_config import (
    RAGBuildRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)
from app.workflow.data_manager import DataManager
from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.config_helper import save_run_config_as_toml

# 各 site 的 pipeline 設定（crawler / image / rag 各自對應同名 test config）
SITES: list[dict[str, str]] = [
    {
        "crawler": "test_nculab",
        "image": "test_nculab",
        "rag": "test_nculab",
    },
    {
        "crawler": "test_ncucsie",
        "image": "test_ncucsie",
        "rag": "test_ncucsie",
    },
]

# publish_run_metadata 預期產出的元資料檔
EXPECTED_METADATA_FILES = ["module_config.toml", "run_config.toml", "terminal.log"]


def _check_published_files(
    site_label: str,
    data_manager: DataManager,
    site_id: str,
    category: str,
) -> list[str]:
    """檢查 data/{category}/{site_id}/ 下的元資料檔是否存在。

    Returns:
        缺失的檔案名稱列表（空列表表示全部存在）。
    """
    dest_folder = os.path.join(data_manager.base_folder, category, site_id)
    missing: list[str] = []
    for filename in EXPECTED_METADATA_FILES:
        fpath = os.path.join(dest_folder, filename)
        if os.path.isfile(fpath):
            print(f"  [OK]   {dest_folder}/{filename}")
        else:
            print(f"  [MISS] {dest_folder}/{filename}")
            missing.append(filename)
    return missing


def run_site_pipeline(
    site_label: str,
    crawler_config: str,
    image_config: str,
    rag_config: str,
) -> tuple[bool, list[str]]:
    """對單一 site 執行完整 pipeline：爬蟲 → 圖片摘要 → RAG 建庫。

    Returns:
        (全流程成功與否, 缺失的元資料檔列表)。
    """
    print(f"\n{'=' * 60}")
    print(f"  Site: {site_label}")
    print(f"  Crawler config: {crawler_config}")
    print(f"  Image config:   {image_config}")
    print(f"  RAG config:     {rag_config}")
    print(f"{'=' * 60}\n")

    data_manager = DataManager()
    all_missing: list[str] = []

    # ----- 1. 網站爬蟲 -----
    crawler_run_config = WebsiteCrawlerRunConfig(config_name=crawler_config)
    crawl_results, crawl_run_manager = run_website_crawler(
        config_name=crawler_config,
        data_manager=data_manager,
    )
    if crawl_results is None:
        print(f"[FAIL] {site_label}: 爬蟲失敗，終止 pipeline")
        return False, all_missing
    save_run_config_as_toml(crawler_run_config, crawl_run_manager.run_config_toml_path)
    data_manager.publish_run_metadata(
        site_id=crawl_run_manager.site_id,
        category="webpages",
        module_config_path=crawl_run_manager.module_config_toml_path,
        run_config_path=crawl_run_manager.run_config_toml_path,
        log_path=crawl_run_manager.log_path,
    )
    print(f"[OK]   {site_label}: 爬蟲完成，共 {len(crawl_results)} 頁")

    # ----- 2. 圖片摘要 -----
    image_run_config = WebpageImageSummarizerRunConfig(config_name=image_config)
    enhanced_results, image_run_manager = run_webpage_image_summarizer(
        config_name=image_config,
        crawl_results=crawl_results,
        data_manager=data_manager,
    )
    if enhanced_results is None:
        print(f"[FAIL] {site_label}: 圖片摘要失敗，終止 pipeline")
        return False, all_missing
    save_run_config_as_toml(image_run_config, image_run_manager.run_config_toml_path)
    data_manager.publish_run_metadata(
        site_id=image_run_manager.site_id,
        category="webpages",
        module_config_path=image_run_manager.module_config_toml_path,
        run_config_path=image_run_manager.run_config_toml_path,
        log_path=image_run_manager.log_path,
    )
    print(f"[OK]   {site_label}: 圖片摘要完成")

    # ----- 3. RAG 建庫 -----
    # save_vector_store_to_runs=True：向量庫先建在 runs/ 再 publish 到 data/rag/，
    # 避免 config.milvus_uri 與 publish 目標路徑相同導致 self-copy 錯誤。
    rag_run_config = RAGBuildRunConfig(
        config_name=rag_config,
        webpages_data_use_latest_results=True,
        save_vector_store_to_runs=True,
    )
    rag_run_manager = run_rag_build(
        config_name=rag_config,
        webpages_data_use_latest_results=True,
        save_vector_store_to_runs=True,
        data_manager=data_manager,
    )
    save_run_config_as_toml(rag_run_config, rag_run_manager.run_config_toml_path)
    data_manager.publish_run_metadata(
        site_id=rag_run_manager.site_id,
        category="rag",
        module_config_path=rag_run_manager.module_config_toml_path,
        run_config_path=rag_run_manager.run_config_toml_path,
        log_path=rag_run_manager.log_path,
    )
    print(f"[OK]   {site_label}: RAG 建庫完成")

    # ----- 4. 驗證 publish 結果 -----
    print(f"\n--- Verify published files for {site_label} ---")
    site_id = crawl_run_manager.site_id
    for cat in ("webpages", "rag"):
        missing = _check_published_files(site_label, data_manager, site_id, cat)
        all_missing.extend(f"{cat}/{m}" for m in missing)

    return True, all_missing


def main() -> None:
    results: dict[str, bool] = {}
    missing_files: dict[str, list[str]] = {}

    for site in SITES:
        site_label = site["crawler"].replace("test_", "")
        success, missing = run_site_pipeline(
            site_label=site_label,
            crawler_config=site["crawler"],
            image_config=site["image"],
            rag_config=site["rag"],
        )
        results[site_label] = success
        missing_files[site_label] = missing

    # ----- 總結 -----
    print(f"\n{'=' * 60}")
    print("  Multi-Site Test Summary")
    print(f"{'=' * 60}")
    for site_label, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {site_label:12s} : [{status}]")
    print(f"{'=' * 60}")

    all_passed = all(results.values())
    all_metadata_present = all(len(v) == 0 for v in missing_files.values())

    if all_passed:
        print("\nAll sites completed successfully.")
        print("Verify data isolation:")
        for site in SITES:
            site_id = site["crawler"].replace("test_", "")
            print(f"  data/webpages/{site_id}/results.json")
            print(f"  data/webpages/{site_id}/results/")
            print(f"  data/webpages/{site_id}/module_config.toml")
            print(f"  data/webpages/{site_id}/run_config.toml")
            print(f"  data/webpages/{site_id}/terminal.log")
            print(f"  data/rag/{site_id}/milvus.db/")
            print(f"  data/rag/{site_id}/module_config.toml")
            print(f"  data/rag/{site_id}/run_config.toml")
            print(f"  data/rag/{site_id}/terminal.log")
    else:
        print("\nSome sites failed. Check logs above for details.")

    if all_metadata_present:
        print("\nAll metadata files published correctly.")
    else:
        print("\nMissing metadata files:")
        for site_label, missing in missing_files.items():
            if missing:
                for f in missing:
                    print(f"  {site_label}: {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
