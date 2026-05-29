# Config

## 待辦事項
- [x] webpage_image_summarizer 的 litellm_kwargs 改為獨立的 section，並且保存到 module_config.toml
- [x] 調整 website_crawler 的 參數型態和預設值 (max_depth 改成 0 代表不限制深度, exclude_words 改成 list)
- [x] 重構 config 架構
- [x] 保留建置 vector store 的 config 到 data/rag/qdrant_db
- [x] 設計 run config class
- [x] 提供 CLI 參數覆寫 config 功能
- [ ] 使用 yaml + pydantic 取代 toml + dataclass

## 一、config 架構

專案現在的模組參數都集中放在 [config/](config) 底下的 TOML 檔，再由各模組對應的 config dataclass 讀取。

三條主要流程如下：

- website crawler 由 [app/website_crawler_config.py](app/website_crawler_config.py) 對應 [config/website_crawler/](config/website_crawler)
- webpage image summarizer 由 [app/webpage_image_summarizer_config.py](app/webpage_image_summarizer_config.py) 對應 [config/webpage_image_summarizer/](config/webpage_image_summarizer)
- RAG 由 [app/rag_config.py](app/rag_config.py) 對應 [config/rag/](config/rag)

這三個 config class 都採用同一個方向：

1. 先用 config_name 組出對應的 TOML 檔路徑
2. 再用 sections_to_keys 描述每個 section 允許的欄位
3. 透過 shared helper 載入與覆寫
4. 最後在 dataclass 建構後做型別與範圍驗證

## 二、各模組怎麼載入與覆寫

### Website crawler

- 讀取 section：init、crawl
- 對應欄位見 [app/website_crawler_config.py](app/website_crawler_config.py)
- [WebsiteCrawlerConfig.from_toml()](app/website_crawler_config.py) 會：
	- 組出 `config/website_crawler/{config_name}.toml`
	- 呼叫 load_config_from_toml() 載入所有 section
	- 呼叫 override_config() 套用 runtime overrides
	- 補上 config_name 後再建立 dataclass

欄位語意是：

- init 控制 max_depth、max_pages、content_threshold、light_mode、wait_for_images
- crawl 控制 url、url_patterns、allowed_domains、exclude_words

的型態重點是：

- max_depth 是 int 或 None
- max_pages 是 int 或 None
- exclude_words 是 list[str] 或 None

### Webpage image summarizer

- 讀取 section：init、summarize、litellm_kwargs
- 對應欄位見 [app/webpage_image_summarizer_config.py](app/webpage_image_summarizer_config.py)
- [WebpageImageSummarizerConfig.from_toml()](app/webpage_image_summarizer_config.py) 會：
	- 組出 `config/webpage_image_summarizer/{config_name}.toml`
	- 先用 load_config_from_toml() 讀入固定 section
	- 再用 override_config() 套用 runtime overrides
	- 補上 config_name 後建立 dataclass

欄位語意是：

- init 控制 download_timeout、success_threshold、max_retries、cache_download_images、cache_image_captions
- summarize 控制 model、prompt、image_source、vlm_max_workers
- litellm_kwargs 是獨立的延伸參數區

的驗證集中在 [WebpageImageSummarizerConfig._validate_config()](app/webpage_image_summarizer_config.py) 內。

### RAG

- 讀取 section：init、vector_store、nodes、index、retriever、query_engine
- 對應欄位見 [app/rag_config.py](app/rag_config.py)
- [RagConfig.from_toml()](app/rag_config.py) 會：
	- 組出 `config/rag/{config_name}.toml`
	- 用 load_config_from_toml() 讀入六個 section
	- 用 override_config() 套用 runtime overrides
	- 補上 config_name 與 config_path 後建立 dataclass

欄位語意是：

- init 控制 webpages_data_folder_path
- vector_store 控制 qdrant_db_folder_path、collection_name
- nodes 控制 chunk_size、chunk_overlap、paragraph_separator
- index 控制 embedding_name
- retriever 控制 top_k
- query_engine 控制 llm_name、cutoff

的驗證集中在 [RagConfig._validate_config()](app/rag_config.py) 內。

## 三、共用載入、覆寫與驗證機制

[utils/config_helper.py](utils/config_helper.py) 是三個模組共用的設定工具中心，主要負責讀取、過濾、覆寫與留檔。

### 載入規則

load_config_section_from_toml() 的流程是：

1. 先確認設定檔存在
2. 再讀出指定 section
3. section 必須是 table
4. 只保留允許的 keys，未知 keys 會被忽略並記 warning

load_config_from_toml() 則是把多個 section 依照 sections_to_keys 逐一載入並合併成單一 dict。

### 覆寫規則

override_config() 會把 runtime overrides 先經過 allowed keys 篩選，再合併回 config。

這代表：

- 只會接受 sections_to_keys 定義過的欄位
- 未知 override key 會被丟掉
- 三個模組現在都走同一套覆寫邏輯

### 驗證規則

真正的型別與範圍驗證都放在 dataclass 建構後執行的 [__post_init__()](app/website_crawler_config.py)、[__post_init__()](app/webpage_image_summarizer_config.py)、[__post_init__()](app/rag_config.py) 中，再統一呼叫各模組自己的 _validate_config()。

這樣的好處是：

- TOML 讀取只處理結構與允許欄位
- 模組本身負責 business rules
- 驗證邏輯可以跟欄位定義放在同一個檔案

### run name 規則

filter_commented_configs() 會掃描 TOML 裡帶有 run name 註解的欄位，只把這些欄位納入 run name。

所以 run name 不是全部設定值的序列化，而是只取被標記的欄位。

## 四、留檔機制

[run.py](run.py) 與 [utils/run_manager.py](utils/run_manager.py) 負責把一次執行的輸入、輸出與路徑留檔。

### RunManager 建立的目錄

RunManager 會在 runs/<timestamp>/<module>/<run>/ 下建立：

- results.json
- results/
- module_config.toml
- run_config.toml
- terminal.log

### module_config.toml

save_module_config_as_toml() 會根據 config 的 sections_to_keys，把模組設定寫成分 section 的 TOML。

的行為重點是：

- 只有 sections_to_keys 中的欄位會被顯式寫出
- 若 config 內存在 residual section，未被前面 section 消耗的欄位會寫進那個 residual section
- 沒有 residual section 時，未消耗欄位不會進入 module_config.toml

### run_config.toml

save_run_config_as_toml() 會把 CLI 或執行控制用的 dataclass 扁平化後寫成一份 run config。

在 [run.py](run.py) 裡，RagBuild 與 RagQuery 這兩個流程還保留這個留檔概念，但其他流程主要還是以 module_config.toml 為主。

### 結果檔案

- RunManager.save_results_as_json() 會寫出 results.json
- RunManager.save_results_as_md() 會把每頁內容寫到 results/ 底下

三個模組的主流程都會在適當時機寫出設定檔與結果檔：

- run_website_crawler()
- run_webpage_image_summarizer()
- run_rag_build()
- run_rag_query()

## 五、測試與實驗如何使用 config

[test/test_module.py](test/test_module.py) 是最直接的 smoke test，會分別呼叫：

- run_website_crawler(config_name="test")
- run_webpage_image_summarizer(config_name="test")
- run_rag_build(config_name="test")

[exp.py](exp.py) 則偏向手動實驗入口，通常會搭配特定 config_name 或模型版本，比較不同 prompt / 模型 / 參數組合的結果。

## 六、的結論

專案的設定處理可以簡化成一句話：

TOML 分 section 載入 → shared helper 過濾與覆寫 → dataclass 驗證 → RunManager 留檔。

最重要的三個現況是：

- website crawler、webpage image summarizer、RAG 已經統一到同一套 config 載入與覆寫模式
- 驗證邏輯現在都集中在各模組自己的 _validate_config()
- module_config.toml 的實際輸出會受 sections_to_keys 與 residual section 影響

## Evidence

- [utils/config_helper.py](utils/config_helper.py)
- [app/website_crawler_config.py](app/website_crawler_config.py)
- [app/webpage_image_summarizer_config.py](app/webpage_image_summarizer_config.py)
- [app/rag_config.py](app/rag_config.py)
- [run.py](run.py)
- [utils/run_manager.py](utils/run_manager.py)
- [test/test_module.py](test/test_module.py)