# Implementation Log

> 對應規劃文件：[plan.md](./plan.md)

---

## Plan 1 執行摘要（commit `969ca57`，先前工作階段完成）

Plan 1 的實作發生在本工作階段之前，此處僅摘要其對 `log_helper.py` / `main.py` 建立的核心慣例，作為 Plan 2、Plan 3 的基礎：

- `log_helper.py` 新增執行摘要累加器：`log_run_time(title, record=True)` 選擇性記錄階段耗時與 stage stack；`record_cost()` / `record_elapsed()` / `reset_run_summary()` / `log_run_summary()` 產生一張統一的 Stage/Elapsed/Cost 彙總表。
- 新增 `NOISY_LOGGER_LEVELS` dict，於 `setup_logging()` 中統一過濾 `llama_index.core.readers.file.base`（設 ERROR）與 `grpc._server`（設 CRITICAL）。
- 新增 `disable_model_progress_bars()`（`HF_HUB_DISABLE_PROGRESS_BARS=1`），關閉 huggingface_hub 進度條。
- `print_log()` 新增 `soft_wrap` 參數（供長 URL 等不換行輸出使用）。
- `main.py`：整個 crawler→summarizer→RAG-build 流程包在 `try/finally: log_run_summary()`，確保提前 return 或例外時仍印出已完成階段的摘要；新增 `except KeyboardInterrupt: logger.info(...)` 處理 Ctrl-C。
- 新增測試：`test_log_helper.py`、`test_dedup_key.py`、`test_image_failure_summary.py`。

---

## Plan 2 執行紀錄

### 1. 簡化 Image Summarization log

**檔案**：`src/app/engines/webpage_image_summarizer.py`

- `__init__` 新增 `self._page_stats_by_page: list[tuple[str, dict]] = []`。
- 迴圈內移除逐頁的 `log_session(...)` 與逐頁 `_log_stats(...)`，改為 `self._page_stats_by_page.append((page_title, dict(self._page_stats)))`。
- 新增 `_log_page_stats_table(title)`：組出含 Page 欄位的合併表格（逐頁一列 + Total 一列），取代原本的 `_log_stats(self._all_page_stats, "All Image Summarize Stats")` 呼叫。
- Total 列改為對 `_page_stats_by_page` 逐一加總（不依賴 `_all_page_stats` 的 shape，避免欄位對不齊）。

### 2. 新增 LLM Generated exclude_words 過程 log

**檔案**：`src/app/engines/webpage_markdown_cleaner.py`

- `generate_exclude_words()` 開頭加 `log_session("Generating exclude_words", style="cyan")`。
- 迴圈內 `_propose_words()` 成功後印 `print_log(f"Run {i+1}/{self.repeat}: sampled {len(samples)} pages, proposed {len(words)} exclude_words (cost ${usage['cost_usd']:.4f})")`。

### 3. 新增 RAG build log session

**檔案**：`src/app/workflow/workflow.py`、`src/app/engines/rag/rag_factory.py`

- `workflow.py::run_rag_build()` 在呼叫 `create_rag(...)` 前加 `log_session("RAG Build", style="cyan")`。
- `RAGBuilder.__init__` 新增 `self._build_stats: dict[str, str] = {}`；`build_reusable()` 開頭重置，結尾印 `log_session("RAG Build Stats", style="green")` + Table。
- 各子步驟寫入對應列：`build_nodes()` → Documents loaded / Nodes produced（`NodePipelineBuilder` 新增 `last_doc_count` 屬性以取得文件數）；`build_vector_store()` → Vector store；`build_index()` / `load_index()` → Index nodes；`build_retriever()` → Retriever；`build_query_engine()` → Query engine。移除對應的 `logger.info("Successfully built ...")`。

### 4. 修改 Agent 建置過程 log

**檔案**：`src/app/agent/agent.py`

- 移除 LLM / Checkpointer / Agent graph 三行 `logger.info`。
- **決策過程**：先詢問使用者「除了 LLM/Tools/Agent graph，`Tool()`（建立 RAGRegistry）與可用知識庫列表兩個階段完全沒有 log，是否一併加入？」使用者選擇兩者都加入 → 初版表格含 Registry 設定、Knowledge bases、LLM、Checkpointer、Tools 五列。
- 使用者接著要求移除 Checkpointer 列，再要求移除 Registry 列並把 Knowledge bases 移到 Tools 下方 → 最終表格定案為 **LLM → Tools → Knowledge bases** 三列（`tool._registry.list_sites()`）。

### 5. 新增 Server Stop 之後的 log session

**檔案**：`src/main.py`

- 初版方案：在 `except KeyboardInterrupt:` 印 `log_session("Server Stopping", ...)`。使用者指出這樣仍會晚於 uvicorn 自己的關閉訊息（因為 `server.run()` 內部已經完成 graceful shutdown 才把控制權交還），要求改成「按下 Ctrl+C 當下就輸出」。
- 改為 monkey-patch `server.handle_exit`（uvicorn 收到 SIGINT 時第一個呼叫的方法）：
  ```python
  original_handle_exit = server.handle_exit
  def _handle_exit_with_log(*args, **kwargs):
      log_session("Server Stopping", style="cyan")
      original_handle_exit(*args, **kwargs)
  server.handle_exit = _handle_exit_with_log
  ```
- `except KeyboardInterrupt:` 改為 `pass`；`finally: chat_app.close()` 後印 `log_session("Server Stopped", style="cyan")`。
- 移除因此變成未使用的 `logger`/`logging` import。

### Plan 2 驗證結果

- `test_webpage_markdown_cleaner.py`、`test_log_helper.py`、`test_image_failure_summary.py`、`test_rag_tools.py`、`test_run_agent.py`、`test_agent_server.py`、`test_runmanager_agent_results.py` 全數通過。
- 完整非 slow 測試套件（`src/test -m "not slow"`）：**193 passed**，另 2 個失敗（見下）。
- **附帶發現但本輪未處理的既有問題**：`test_run_rag_build_publish.py` 的 2 個測試失敗。追查後確認 `run_rag_build()` 在某次**先前、非本工作階段**的未提交變更中，把「發布中繼資料」（`data_manager.publish_run_metadata(...)`）的呼叫順序移到「儲存 `module_config.toml`」（`save_module_config_as_toml(...)`）之前，導致發布時來源檔案還不存在。此問題屬於 `docs/work/todo.md` 另一個獨立項目「更新 workflow 留檔機制」的範疇，與本輪 log 改動無關，未動它。
- 清掉一個測試殘留的空檔案 `fake_module_config.toml`（`test_run_agent.py` 對 `mock_rm.module_config_toml_path` 寫死相對路徑造成的既有問題，與本次改動無關）。

---

## Plan 3 執行紀錄

### 1. generate_exclude_words() stats log 搬到 webpage_markdown_cleaner.py + 2. kept/rejected 合併表

**檔案**：`src/app/workflow/run_persistence.py` → `src/app/engines/webpage_markdown_cleaner.py`

- `webpage_markdown_cleaner.py` 新增 `from rich.markup import escape` / `from rich.table import Table`。
- `generate_exclude_words()` 在 `validate_words()` 之後、`return GenerationResult(...)` 之前插入：
  ```python
  hits = self.count_word_hits(pages, ranked)
  total_cost_usd = sum(u["cost_usd"] for u in usages)
  log_session("Generating exclude_words Stats", style="green")
  print_log(f"Total {len(usages)} calls, cost: ${total_cost_usd:.4f}")
  table = Table(...)
  table.add_column("Word", ...); table.add_column("Votes", ...)
  table.add_column("Hit lines", ...); table.add_column("Low-occ ratio", ...)
  table.add_column("Status", ...)
  for w in ranked:
      table.add_row(escape(w), str(votes[w]), str(hits[w]),
                     f"{stats[w]['low_occ_ratio']:.1%}",
                     "Kept" if w in kept else "Rejected")
  print_log(table)
  ```
- `run_persistence.py::save_generated_exclude_words()` 移除整段 `log_session`/`Table`/`print_log`/`escape` 邏輯，只保留兩個檔案的寫入；docstring 同步更新（移除「並輸出 log 表格」字樣）。移除不再使用的 `escape`、`Table`、`log_session`、`print_log` import（`WebpageMarkdownCleaner` 保留，因為 `hits = WebpageMarkdownCleaner.count_word_hits(...)` 仍為 JSON 報告所需）。

**驗證**（`test_webpage_markdown_cleaner.py`，實際跑）：

```
─────────────────────────── Generating exclude_words ───────────────────────────
Run 1/3: sampled 2 pages, proposed 1 exclude_words (cost $0.0100)
...
──────────────────────── Generating exclude_words Stats ────────────────────────
Total 3 calls, cost: $0.0300
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Word                 ┃ Votes ┃ Hit lines ┃ Low-occ ratio ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Skip to main content │ 3     │ 10        │ 0.0%          │ Kept   │
│ Footer text          │ 2     │ 10        │ 0.0%          │ Kept   │
└──────────────────────┴───────┴───────────┴───────────────┴────────┘
```

`test_save_generated_exclude_words` 原本就只斷言檔案輸出（toml/json），未涉及 log，故無需更新即通過。14/14 測試通過。

### 3. download / generate image log 補上正在處理哪個頁面

**檔案**：`src/app/engines/webpage_image_summarizer.py`

- `_download_images()` 的 `progress.add_task("Downloading images...", ...)` 與 `_agenerate_image_captions()` 的 `progress.add_task("Generating captions...", ...)` 改為帶上 `self._current_page`。

**過程中發現並修正的 bug：Rich markup 吞掉方括號**

第一次實測（headless 執行，見下方「Plan 3 驗證」）發現 `[page_title]` 完全消失，只剩兩個空白：

```
Downloading images...  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 0.047s
```

**根因**：`TaskCountProgress` 底層 `TextColumn("[yellow]{task.description}")` 本身是 Rich markup 模板，`task.description` 代入後**整串**會被當成 markup 解析；描述文字裡的 `[page_title]` 因此被誤判成一個（不存在的）樣式標籤，整段被吃掉。

第一次嘗試：`f"Downloading images... [{escape(self._current_page)}]"` —— **未修好**，因為只 escape 了 `self._current_page` 本身，方括號是程式碼自己加的字面字元，不在被 escape 的範圍內。用最小重現腳本確認：

```python
>>> escape('labintro')
'labintro'   # 沒有變化，因為字串本身不含方括號
```

**正確修法**：對**整串組好的描述文字**呼叫 `escape()`：

```python
task_id = progress.add_task(
    escape(f"Downloading images... [{self._current_page}]"),
    total=len(futures),
)
```

用最小重現腳本確認修法有效後（`escape(f'Downloading images... [labintro]')` → `'Downloading images... \\[labintro]'`，正確渲染為 `Downloading images... [labintro]`），套用到 `_download_images()` 與 `_agenerate_image_captions()` 兩處。

### 4. All Image Summarize Stats 裁剪太長的 Page 名稱

**檔案**：`src/app/engines/webpage_image_summarizer.py`

- 新增 staticmethod：
  ```python
  @staticmethod
  def _truncate_page_title(title: str, max_len: int = 40) -> str:
      if len(title) <= max_len:
          return title
      return title[:max_len] + "…"
  ```
- `_log_page_stats_table()` 組 row 時對 `page_title` 套用此 helper。

### 5. RAG Build Stats 移除 vector store / retriever / query_engine 的 log

**檔案**：`src/app/engines/rag/rag_factory.py`

- 移除 `build_vector_store()` 裡 `self._build_stats["Vector store"] = ...`。
- 移除 `build_retriever()` 裡 `self._build_stats["Retriever"] = ...`。
- 移除 `build_query_engine()` 裡 `self._build_stats["Query engine"] = ...`。

### Plan 3 驗證

由於本輪改動集中在「真實資料才會暴露的問題」（表格寬度、頁面名稱），單元測試不足以驗證，因此直接呼叫 `run_website_crawler` / `run_webpage_image_summarizer` / `run_rag_build`（跳過需要 Ctrl+C 的 server 階段）對 `nculab` 設定跑了 3 輪真實流程：

| 輪次 | 條件 | 結果 |
|------|------|------|
| 第 1 輪 | 無 TTY（headless，預設 80 欄寬度） | 抓到 markup escape bug；`[page_title]` 完全消失 |
| 第 2 輪 | `COLUMNS=150`（模擬真實終端寬度），escape 修法**未**正確套用 | bug 依舊（證明第一次修法無效，而非寬度問題） |
| 第 3 輪 | `COLUMNS=150`，套用正確的 escape 修法 | 全部符合 plan.md 的「改動後 log 示意」 |

第 3 輪實際輸出摘錄：

```
Downloading images... [labintro] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 0.412s
Generating captions... [labintro] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 6.244s
...
─────────────────────────────────────────────────────────────── All Image Summarize Stats ──────────────────────────────────────────────────────────────
┃ Page                                                                     ┃ cost_usd  ┃ success ┃ download_failure ┃ summarize_failu… ┃ cache_reuse ┃
│ news_校外奬項_賀邱威誠同學獲科技部108年度產學合作計畫成果發表暨績效考評… │ $0.006896 │ 4       │ 0                │ 0                │ 0           │
│ Total                                                                    │ $0.080048 │ 73      │ 1                │ 0                │ 0           │
...
─────────────────────────────────────────────────────────────── Generating exclude_words Stats ───────────────────────────────────────────────────────────────
│ Post date:           │ 1     │ 18        │ 100.0%        │ Rejected │
...
────────────────────────────────────────────────────────────────────── RAG Build Stats ───────────────────────────────────────────────────────────────────
┃ Metric           ┃ Value ┃
│ Documents loaded │ 47    │
│ Nodes produced   │ 275   │
│ Index nodes      │ 275   │
```

（`Post date:` 為此次真實跑到、被驗證剔除的詞——巧合驗證了 kept/rejected 合併表格在有 Rejected 詞時的實際呈現。）

完整非 slow 測試套件重跑：**193 passed, 8 deselected**（deselect 為 slow 端到端測試 + 前述 2 個既有失敗）。

驗證完成後清理：暫存驗證腳本（`/tmp/verify_plan3*.py`）與 3 次驗證產生的 log 檔案、再次出現的 `fake_module_config.toml`。因為驗證跑的是真實流程（非 mock），`data/webpages/nculab/` 與 `data/rag/nculab/` 底下部分檔案因此被更新／向量庫重建，這是正常的流程副作用，不是誤動作。

---

## Final Summary

### 變更檔案總表

| 檔案 | Plan 2 | Plan 3 |
|------|--------|--------|
| `src/app/engines/webpage_image_summarizer.py` | 移除逐頁 Rule/表格，改為合併表格 | 進度條補頁面名稱（含 escape 修正）、長頁名截斷 |
| `src/app/engines/webpage_markdown_cleaner.py` | 新增逐次 LLM 呼叫過程 log | 移入並改寫統計表格為 kept/rejected 合併版 |
| `src/app/workflow/run_persistence.py` | — | 移除已搬移的 log 邏輯與對應 import |
| `src/app/workflow/workflow.py` | 新增 `"RAG Build"` 起始 session | — |
| `src/app/engines/rag/rag_factory.py` | 新增 `_build_stats` 累積與 `"RAG Build Stats"` 表格 | 移除 Vector store / Retriever / Query engine 三列 |
| `src/app/agent/agent.py` | 三行 INFO 改為一張表格（LLM / Tools / Knowledge bases） | — |
| `src/main.py` | `handle_exit` monkey-patch + Server Stopping/Stopped session | — |

### 測試結果

- Plan 2 完成後：193 passed（非 slow）。
- Plan 3 完成後：193 passed, 8 deselected（非 slow）。
- 兩輪皆有的既有失敗（與本輪改動無關）：`test_run_rag_build_publish.py::test_publishes_vector_store_and_metadata`、`test_missing_vector_store_skips_vector_publish_but_publishes_metadata`。

### 已知限制 / 未處理事項

| 類別 | 說明 |
|------|------|
| **`run_rag_build()` 發布順序 bug** | 見 Plan 2 驗證結果；屬於「更新 workflow 留檔機制」項目範疇，未在本輪處理 |
| **本文件記錄範圍之外的後續變動** | 完成 Plan 2、Plan 3 之後（本工作階段之外）觀察到 `main.py`、`agent.py`、`webpage_image_summarizer.py` 上有進一步變動（例如 `log_main_workflow_run_summary()`、`"Agent Stats"` 改名、逐頁 `log_session` 疑似重新出現），研判是接續的 Plan 4「包裝 `log_helper.py`」工作，不在本文件記錄與驗證範圍內 |
