"""小規模多網站知識庫驗證腳本。

對 nculab 與 ncucsie 兩個網站各爬取 10 頁，執行圖片摘要與 RAG 建庫，
驗證 DataManager 多 site 隔離機制是否正常運作。

執行：uv run python src/test/dev/test_multi_site.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)

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


def run_site_pipeline(
    site_label: str,
    crawler_config: str,
    image_config: str,
    rag_config: str,
) -> bool:
    """對單一 site 執行完整 pipeline：爬蟲 → 圖片摘要 → RAG 建庫。

    Returns:
        True 表示全流程成功，False 表示中途失敗。
    """
    print(f"\n{'=' * 60}")
    print(f"  Site: {site_label}")
    print(f"  Crawler config: {crawler_config}")
    print(f"  Image config:   {image_config}")
    print(f"  RAG config:     {rag_config}")
    print(f"{'=' * 60}\n")

    run_manager = RunManager()
    data_manager = DataManager()

    # ----- 1. 網站爬蟲 -----
    run_manager.set_module_path("website_crawler")
    crawl_results = run_website_crawler(
        run_manager=run_manager,
        config_name=crawler_config,
        data_manager=data_manager,
    )
    if crawl_results is None:
        print(f"[FAIL] {site_label}: 爬蟲失敗，終止 pipeline")
        return False
    print(f"[OK]   {site_label}: 爬蟲完成，共 {len(crawl_results)} 頁")

    # ----- 2. 圖片摘要 -----
    run_manager.set_module_path("webpage_image_summarizer")
    enhanced_results = run_webpage_image_summarizer(
        run_manager=run_manager,
        config_name=image_config,
        crawl_results=crawl_results,
        data_manager=data_manager,
    )
    if enhanced_results is None:
        print(f"[FAIL] {site_label}: 圖片摘要失敗，終止 pipeline")
        return False
    print(f"[OK]   {site_label}: 圖片摘要完成")

    # ----- 3. RAG 建庫 -----
    # save_vector_store_to_runs=True：向量庫先建在 runs/ 再 publish 到 data/rag/，
    # 避免 config.milvus_uri 與 publish 目標路徑相同導致 self-copy 錯誤。
    run_manager.set_module_path("rag_build")
    run_rag_build(
        run_manager=run_manager,
        config_name=rag_config,
        webpages_data_use_latest_results=True,
        save_vector_store_to_runs=True,
        data_manager=data_manager,
    )
    print(f"[OK]   {site_label}: RAG 建庫完成")

    return True


def main() -> None:
    results: dict[str, bool] = {}

    for site in SITES:
        site_label = site["crawler"].replace("test_", "")
        success = run_site_pipeline(
            site_label=site_label,
            crawler_config=site["crawler"],
            image_config=site["image"],
            rag_config=site["rag"],
        )
        results[site_label] = success

    # ----- 總結 -----
    print(f"\n{'=' * 60}")
    print("  Multi-Site Test Summary")
    print(f"{'=' * 60}")
    for site_label, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {site_label:12s} : [{status}]")
    print(f"{'=' * 60}")

    all_passed = all(results.values())
    if all_passed:
        print("\nAll sites completed successfully.")
        print("Verify data isolation:")
        print("  data/webpages/nculab/results.json")
        print("  data/webpages/ncucsie/results.json")
        print("  data/rag/nculab/milvus.db/")
        print("  data/rag/ncucsie/milvus.db/")
    else:
        print("\nSome sites failed. Check logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
