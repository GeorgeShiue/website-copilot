# configs

各模組的設定檔，一律為 YAML（`.yml`），由 `src/website_copilot/config/*_config.py` 的 pydantic model 載入與驗證。

```
configs/
├── website_crawler/   # WebsiteCrawlerConfig
├── image_summarizer/  # ImageSummarizerConfig
├── rag/               # RAGConfig
└── agent/             # AgentConfig
```

每個模組資料夾中：

- `default.yml`：完整設定，其他設定檔以 `extends: default` 繼承。
- `{site}.yml`：站點設定（`nculab`／`ncucsie`／`claudecode`），只寫與 default 不同的欄位。
- `test_{site}.yml`：測試用設定（如 `max_pages: 40`），繼承 `{site}.yml`；`test.yml` 等同 `test_nculab.yml`。

CLI 的 `--run.config <name>` 對應 `configs/<module>/<name>.yml`。

## 結構

巢狀 mapping 與 config model 的 section 一一對應，例如 `retriever.similarity_top_k` 即 `RAGConfig.retriever.similarity_top_k`。

- 未知的 key 會直接報錯（包含拼錯的欄位名稱）。
- 必填欄位缺少時報錯；只有語意為「未設定」的欄位可省略或寫 `null`（如 `max_pages`、`path_prefix`、`hybrid_ranker_params`）。
- 各欄位的型別、範圍與說明見對應的 config model。

## 保留 key（只在檔案最上層有效）

| key | 說明 |
|---|---|
| `extends` | 繼承同資料夾的設定，值為設定名稱（不含副檔名），如 `extends: default`。處理後移除，不會被繼承 |
| `run_name_fields` | 決定 run 名稱（`runs/` 資料夾名稱）的欄位，dotted path 的 list，如 `[init.max_pages]`；run 名稱以最後一段欄位名組成（`max_pages-40`）。省略時為 `[]`，run 名稱為 `default`。和一般欄位一樣會被繼承，子檔寫了就整個取代 |

其他層級出現同名 key 視為一般欄位，會被拒絕。

## extends

- 只能繼承同資料夾的設定（單一繼承），可以多層（`test.yml → test_nculab.yml → nculab.yml → default.yml`）；循環繼承或找不到被繼承的檔案時報錯並列出繼承鏈。
- 合併規則（子檔疊在父檔上）：
  - 兩邊都是 mapping：遞迴合併，子檔只需寫要改的欄位。
  - 其他情況（list、純量、`null`、型別不同）：子檔的值整個取代父檔的值。例如 `url_patterns` 在子檔寫了就完全取代，不會與父檔的 list 合併。
- 清除值：寫 `key: null`。可選欄位變成「未設定」；必填欄位則驗證失敗。
  - 子檔寫 `key: {}` **不會**清空父檔的 mapping；要移除 mapping 中的某個 key，需明確寫該 key 為 `null`。
  - 例：父檔用 `WeightedRanker`，子檔改用 `RRFRanker` 時要寫 `hybrid_ranker_params: {weights: null, k: 60}`，否則合併後同時有 `weights` 與 `k`，會被跨欄位規則擋下。
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

每次執行在 `runs/` 與 `data/` 寫出的 `module_config.yml` 是 extends 展開後的完整設定（不含 `extends`），檔頭註解記錄來源與 run name 欄位：

```yaml
# source: configs/rag/test.yml (extends: test_nculab → nculab → default)
# run_name_fields: [vector_store.vector_store_type]
```
