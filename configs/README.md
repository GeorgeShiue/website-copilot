# configs

設定檔一律為 YAML（`.yml`），由 `src/website_copilot/config/` 的 pydantic model 載入與驗證。分成兩類：

- **站點設定**（`sites/{site_id}.yml`，`SiteConfig`）：站點身分與爬取範圍，與模組參數無關。
- **模組設定**（`{module}/{name}.yml`）：各模組的參數。**參數的預設值寫在 config class**（欄位預設值是唯一的預設值來源，長 prompt 在 `config/prompts.py`），設定檔只寫與預設值不同的部分；設定檔沒寫的欄位一律使用 class 預設值。CLI 的 `--help` 會以 `(default: X)` 顯示這些預設值。

```
configs/
├── sites/             # SiteConfig：nculab.yml / ncucsie.yml
├── website_crawler/   # WebsiteCrawlerConfig：test.yml
├── image_summarizer/  # ImageSummarizerConfig：test.yml
├── rag/               # RAGConfig：test.yml
└── agent/             # AgentConfig：test.yml
```

CLI 以位置參數指定站點、`--run.config <name>` 指定模組設定，兩者獨立組合：

```bash
uv run website-copilot prepare ncucsie --run.config test   # sites/ncucsie.yml + 各模組的 test.yml
uv run website-copilot run rag-query nculab                # sites/nculab.yml + 各模組 class 預設值
```

- `--run.config` 省略時為 `default`。各模組都沒有 `default.yml`：檔案不存在時 `default` 等於 class 預設值；其他名稱找不到檔案時報錯。
- agent／serve 為多站，不需要站點參數。

## 站點設定（`sites/{site_id}.yml`）

```yaml
site_id: ncucsie             # 須與檔名一致；只能包含英數字與底線，且不可以數字開頭（Milvus collection 名稱）
sample_query: 介紹資工系課程   # rag-query 未指定 --run.query 時使用
crawl:
  url: https://www.csie.ncu.edu.tw/
  url_patterns: ["*csie.ncu.edu.tw*"]   # null 為不過濾
  allowed_domains: [www.csie.ncu.edu.tw] # null 為不限制
  path_prefix: /                        # null 時取起始網址的父路徑
```

`site_id` 同時決定 `data/{category}/{site_id}/`、`runs/<ts>/<module>/{site_id}/` 與向量庫的 collection 名稱。每次執行會把站點設定另存為 `site_config.yml`（runs/ 與 data/ 皆有）。

## 模組設定的結構

巢狀 mapping 與 config model 的 section 一一對應，例如 `retriever.similarity_top_k` 即 `RAGConfig.retriever.similarity_top_k`。

- 未知的 key 會直接報錯（包含拼錯的欄位名稱，以及已移到站點設定的 `site_id`、`crawl` 等欄位）。
- 省略的欄位使用 class 預設值。
- 寫 `null` 代表「未設定」，只適用於允許 `null` 的欄位（如 `max_depth`、`max_pages`、`hybrid_ranker_params`）。
- 各欄位的型別、範圍、預設值與說明見對應的 config model，或 `uv run website-copilot run <module> --help`。

## 保留 key（只在檔案最上層有效）

| key | 說明 |
|---|---|
| `extends` | 繼承同資料夾的設定，值為設定名稱（不含副檔名），如 `extends: test`。處理後移除，不會被繼承 |
| `run_name_fields` | 決定 run 名稱（`runs/` 資料夾名稱）的欄位，dotted path 的 list，如 `[init.max_pages]`；run 名稱以最後一段欄位名組成（`max_pages-40`）。整條繼承鏈都沒寫時使用 class 的 `_DEFAULT_RUN_NAME_FIELDS`（website_crawler 為 `[init.max_depth]`、image_summarizer 為 `[summarize.model]`、rag 為 `[vector_store.vector_store_type]`、agent 為 `[]`）；寫 `[]` 明確清空，run 名稱為 `default`。和一般欄位一樣會被繼承，子檔寫了就整個取代 |

其他層級出現同名 key 視為一般欄位，會被拒絕。

## extends

- 只能繼承同資料夾的設定（單一繼承），可以多層（如 `test_small.yml → test.yml`）；循環繼承或找不到被繼承的檔案時報錯並列出繼承鏈（`extends: default` 指向不存在的 `default.yml` 也會報錯）。站點設定也支援 extends（繼承 `sites/` 中的其他站點）。
- 繼承鏈合併完成後，仍未寫到的欄位才使用 class 預設值。
- 合併規則（子檔疊在父檔上）：
  - 兩邊都是 mapping：遞迴合併，子檔只需寫要改的欄位。
  - 其他情況（list、純量、`null`、型別不同）：子檔的值整個取代父檔的值。例如 `url_patterns` 在子檔寫了就完全取代，不會與父檔的 list 合併。
- 清除值：寫 `key: null`。可選欄位變成「未設定」；必填欄位則驗證失敗。
  - 子檔寫 `key: {}` **不會**清空父檔的 mapping；要移除 mapping 中的某個 key，需明確寫該 key 為 `null`。
  - class 預設值不會與設定檔寫的 mapping 逐欄合併：設定檔寫了 `hybrid_ranker_params: {k: 60}`，結果就是 `{weights: null, k: 60}`，不會帶入 class 預設的 `weights`。因此改用 `RRFRanker` 時寫 `hybrid_ranker_params: {k: 60}` 即可；但若繼承鏈中有檔案寫了 `weights`，合併後會同時有 `weights` 與 `k` 而被跨欄位規則擋下，此時要寫 `{weights: null, k: 60}`。
- 只驗證合併後的最終結果；錯誤訊息包含實際載入的檔案與繼承鏈，如 `configs/rag/test_small.yml (extends: test): retriever.similarity_top_k: ...`。

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

每次執行在 `runs/` 與 `data/` 寫出：

- `module_config.yml`：完整的模組設定（extends 展開並補上 class 預設值，不含 `extends`），檔頭註解記錄來源與 run name 欄位；不含站點與向量庫位置等執行期資訊。
- `site_config.yml`：本次使用的站點設定。

```yaml
# source: configs/rag/test.yml
# run_name_fields: [vector_store.vector_store_type]
```
