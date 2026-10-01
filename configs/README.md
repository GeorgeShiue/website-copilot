# configs

各模組的設定檔，一律為 YAML（`.yml`），由 `src/website_copilot/config/*_config.py` 的 pydantic model 載入與驗證。

**參數的預設值寫在 config class**（欄位預設值是唯一的預設值來源，長 prompt 在 `config/prompts.py`），設定檔只寫與預設值不同的部分；設定檔沒寫的欄位一律使用 class 預設值。CLI 的 `--help` 會以 `(default: X)` 顯示這些預設值。

```
configs/
├── website_crawler/   # WebsiteCrawlerConfig
├── image_summarizer/  # ImageSummarizerConfig
├── rag/               # RAGConfig
└── agent/             # AgentConfig
```

每個模組資料夾中：

- `default.yml`：預設站點（nculab）的站點欄位（`site_id`、`crawl.*`、`query_engine.query` 等，Phase D 移到 `configs/sites/`）。`default.yml` 可省略：檔案不存在時 `--run.config default` 等於 class 預設值（如 `agent/` 沒有 `default.yml`）。
- `{site}.yml`：站點設定（`nculab`／`ncucsie`／`claudecode`），`extends: default`，只寫站點欄位與差異。
- `test_{site}.yml`：測試用設定（如 `max_pages: 40`），繼承 `{site}.yml`；`test.yml` 等同 `test_nculab.yml`。

CLI 的 `--run.config <name>` 對應 `configs/<module>/<name>.yml`；除了 `default` 以外，找不到檔案時報錯。

## 結構

巢狀 mapping 與 config model 的 section 一一對應，例如 `retriever.similarity_top_k` 即 `RAGConfig.retriever.similarity_top_k`。

- 未知的 key 會直接報錯（包含拼錯的欄位名稱）。
- 省略的欄位使用 class 預設值；只有站點欄位（`site_id`、`crawl.url`、`query_engine.query`）沒有預設值、必須寫在設定檔。
- 寫 `null` 代表「未設定」，只適用於允許 `null` 的欄位（如 `max_depth`、`max_pages`、`path_prefix`、`hybrid_ranker_params`）。
- 各欄位的型別、範圍、預設值與說明見對應的 config model，或 `uv run website-copilot run <module> --help`。

## 保留 key（只在檔案最上層有效）

| key | 說明 |
|---|---|
| `extends` | 繼承同資料夾的設定，值為設定名稱（不含副檔名），如 `extends: default`。處理後移除，不會被繼承 |
| `run_name_fields` | 決定 run 名稱（`runs/` 資料夾名稱）的欄位，dotted path 的 list，如 `[init.max_pages]`；run 名稱以最後一段欄位名組成（`max_pages-40`）。整條繼承鏈都沒寫時使用 class 的 `_DEFAULT_RUN_NAME_FIELDS`（rag 為 `[vector_store.vector_store_type]`，其餘為 `[]`）；寫 `[]` 明確清空，run 名稱為 `default`。和一般欄位一樣會被繼承，子檔寫了就整個取代 |

其他層級出現同名 key 視為一般欄位，會被拒絕。

## extends

- 只能繼承同資料夾的設定（單一繼承），可以多層（`test.yml → test_nculab.yml → nculab.yml → default.yml`）；循環繼承或找不到被繼承的檔案時報錯並列出繼承鏈（`extends: default` 指向不存在的 `default.yml` 也會報錯）。
- 繼承鏈合併完成後，仍未寫到的欄位才使用 class 預設值。
- 合併規則（子檔疊在父檔上）：
  - 兩邊都是 mapping：遞迴合併，子檔只需寫要改的欄位。
  - 其他情況（list、純量、`null`、型別不同）：子檔的值整個取代父檔的值。例如 `url_patterns` 在子檔寫了就完全取代，不會與父檔的 list 合併。
- 清除值：寫 `key: null`。可選欄位變成「未設定」；必填欄位則驗證失敗。
  - 子檔寫 `key: {}` **不會**清空父檔的 mapping；要移除 mapping 中的某個 key，需明確寫該 key 為 `null`。
  - class 預設值不會與設定檔寫的 mapping 逐欄合併：設定檔寫了 `hybrid_ranker_params: {k: 60}`，結果就是 `{weights: null, k: 60}`，不會帶入 class 預設的 `weights`。因此改用 `RRFRanker` 時寫 `hybrid_ranker_params: {k: 60}` 即可；但若繼承鏈中有檔案寫了 `weights`，合併後會同時有 `weights` 與 `k` 而被跨欄位規則擋下，此時要寫 `{weights: null, k: 60}`。
- 只驗證合併後的最終結果；錯誤訊息包含實際載入的檔案與繼承鏈，如 `configs/rag/test.yml (extends: test_nculab → nculab → default): retriever.similarity_top_k: ...`。

## YAML 撰寫注意事項

載入使用 PyYAML（YAML 1.1），以下寫法的型別可能與預期不同；config 採 strict 模式，這些情況會被報為型別錯誤，而不是被靜默轉換：

| 寫法 | 解析結果 | 應改為 |
|---|---|---|
| `1e-3` | 字串 | `1.0e-3` |
| `on`／`off`／`yes`／`no` | bool | 需要字串時加引號，如 `"yes"` |
| `2026-09-30` | date | 需要字串時加引號 |
| `*nculab*` | alias 語法錯誤 | 以 `*` 開頭的字串加引號，如 `"*nculab*"` |

- 多行字串（prompt）使用 `|` block scalar，內容原樣保留換行。
- int 可以放進 float 欄位（`download_timeout: 10`），但 bool、字串不能放進數字欄位。

## 執行紀錄

每次執行在 `runs/` 與 `data/` 寫出的 `module_config.yml` 是完整設定（extends 展開並補上 class 預設值，不含 `extends`），檔頭註解記錄來源與 run name 欄位：

```yaml
# source: configs/rag/test.yml (extends: test_nculab → nculab → default)
# run_name_fields: [vector_store.vector_store_type]
```
