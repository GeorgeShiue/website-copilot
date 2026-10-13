# Python 設計修正：實作紀錄

> 計畫見 [plan.md](./plan.md)。只記錄與 plan 不同的決定、過程中的發現與驗證結果。除特別註明外，每組的驗證皆為共同關卡：`scripts/check.sh`、9 個 CLI `--help` 冒煙測試，以及與基準點的 `--help` 輸出逐字比對；B、C、D 組另跑 `pytest tests/integration -m "not cost"`。括號內為 `check.sh` 通過的測試數。

分支 `chore/python-fixes`（從 `dev` 切出）。

| 階段 | commit | 說明 |
|---|---|---|
| 基準點 | `7ac6ac1` | 文件 commit（plan、python.md、todo.md），`check.sh` 620 passed |
| A 組 | `cf84325` | 冗餘程式碼（624 passed） |
| B 組 | `a65b6a0` | 穩健性與型別一致（632 passed） |
| C 組 | `1fbe2bb` | 裝飾器（632 passed） |
| D 組 | `34f8a26` | 模組 import 策略（632 passed、import-linter 4 kept） |

新增 12 個測試（620 → 632）：`test_log_helper`（3）、`test_documents` 並列標題（1）、`test_registry_close`（3）、`test_page_stats`（4）、`test_http_downloader` 的 `on_complete`（1）。

**測試先行的確認**：A1、A2 的特徵測試在舊程式碼上通過；B2（2 個失敗）、B3（反射運算元 1 個失敗）、B4（1 個失敗）在舊程式碼上確實失敗，改後通過。

**CLI 冒煙測試**：計畫寫 7 個，實際為 9 個（頂層、`prepare`、`serve`、`run`，以及 `run` 的 5 個子命令）；每組皆 9/9 通過，`--help` 輸出與基準點逐字相同（以 `git worktree` 檢出基準點比對）。

---

# 與 plan 不同的決定

## A4-6 取消（plan 已更正）

plan 原本要把 5 處 `# noqa: BLE001／DTZ007／SIM115` 改成一般註解，前提是「專案 ruff 用預設規則，這些規則未啟用」。**前提錯誤**：ruff 0.16 的預設規則已包含它們，改成一般註解後 `ruff check` 立即報 5 個錯誤。先前是用 `--select` 覆蓋了專案設定才誤判。已還原 5 處 `noqa` 與 `docs/code/python.md`，A4 只做 1～5 項。

連帶發現：ruff 對「以 `logger.exception()`／`exc_info=True` 記錄」的 `except Exception` 不報 `BLE001`，所以 B2、B4 新增的 `except Exception` 不需要 `noqa`（加了反而觸發 `RUF100`），只保留說明用的一般註解。

## D1 改在 `pipelines/prepare.py` 的階段層級實作

plan 的預設切點是 `RAGRegistry.get()` 內才載入 `load_rag`。實際量測後決定不動 `registry`／`serve`，改切 `pipelines/prepare.py`：

| 路徑 | 量測 | 結論 |
|---|---|---|
| `pipelines.prepare` | 3.06 s：`augmenter` 1.65 + `retrieval.factory` 1.00 + `website_crawler` 0.28 | **有受益路徑**：只跑 `run website-crawler`／`augmenter`／`rag-build` 的人被迫載入其他階段的依賴 |
| `retrieval.registry` | 1.40 s：`factory` 1.31（`llama_index.core` 0.58 + `indexing.index` 0.54） | 不做：`serve` 最終仍需要，只是把成本搬到第一個請求；且 `test_rag_tools` 多處 patch `registry.load_rag` |
| `pipelines.serve`／`server.app` | 1.8～1.9 s，`agent.agent` 約 1.7 s | 不做：同上，`serve` 必須載入 |

做法：爬蟲、augmenter、RAG 建置三個階段各自在函式內才 import 自己的依賴（每個名稱都只在一個階段使用）。測試的 patch 目標因此從 `pipelines.prepare.X` 改為依賴所在模組（`test_pipeline_prepare.py` 共 7 處：`WebsiteCrawler`、`WebpageMarkdownCleaner`、`Augmenter` 4 處、`build_rag`）。

## D2：CLI 的 `log_helper` 維持延遲 import

`cli/prepare.py`、`serve.py`、`run.py` 的 `setup_logging` 延遲 import 只值 0.03 s，依「重依賴才延遲」的原則本應改回頂層，但 `test_cli.py` 以 `website_copilot.utils.log_helper.setup_logging` 為 patch 目標，改了要動測試。為 0.03 s 不划算，維持延遲並補上原因註解。

## D3：`config`、`utils` 是 namespace 資料夾

這兩個資料夾沒有 `__init__.py`，import-linter 找不到套件，契約改用 `website_copilot.config.*`／`website_copilot.utils.*` 萬用字元，不為了工具改套件結構。最後 4 份契約：底層不依賴 `agent`／`server`、`pipelines.prepare` 不依賴 `agent`／`server`、`agent.tools` 分層、主要套件分層。**反向驗證**：在 `retrieval/rag.py` 暫時加入對 `agent` 的 import，4 份契約全部 BROKEN，還原後 4 kept。

## D4

`scripts/check-import-time.sh`：量測 `website_copilot.cli` 與 `website_copilot.pipelines.prepare`，超過門檻（預設 0.75 s，可用 `IMPORT_TIME_THRESHOLD` 調整）輸出 `::warning::`，永遠回傳 0（警告模式）。門檻約為基準（0.12 s）的 6 倍，足以抓到頂層新增重依賴（至少 1 s 以上）而不被 CI 機器變慢誤觸發。加入 `ci.yml` 與 `ci-test.yml` 兩份 workflow；沒有加進 `scripts/check.sh`（保持本機檢查快速且確定）。

## 其他小差異

- C2 順手把 `default_hybrid_ranker_params` 的 `elif` 跟在 `return` 後面改成連續 `if`（原本預計歸 C2 處理的 RET505）；並更新 `docs/code/phase1/modules/data_retrieve.md` 對 `VectorStoreBuilder` 的引用。
- B4 依約定「預設做」，已實作。
- A1 維持單獨實作（沒有併入 log_helper 重構）。

---

# Import 耗時對照

中位數（3 次），秒；`python -X importtime` 的累計時間。

| 入口 | 基準 | 完成後 |
|---|---|---|
| `website_copilot.cli` | 0.13 | 0.12 |
| `website_copilot.pipelines.prepare` | 2.91 | **0.11** |
| `website_copilot.retrieval.registry` | 1.46 | 1.40 |
| `website_copilot.server.app` | 1.86 | 1.77 |
| `website_copilot.pipelines.serve` | 1.79 | 1.87 |

進入各階段前需要付出的 import 成本（import `pipelines.prepare` 加上該階段函式內載入的依賴）：

| 階段 | 基準 | 完成後 | 節省 |
|---|---|---|---|
| `run website-crawler` | 3.03 s | 1.85 s | 約 1.2 s |
| `run augmenter` | 2.82 s | 1.56 s | 約 1.3 s |
| `run rag-build` | 2.98 s | 1.33 s | 約 1.65 s |
| 完整 `prepare`（三階段全載入） | 2.90 s | 2.78 s | 基本不變 |

- 完整 `prepare` 與 `serve` 的總成本沒有降低（它們本來就需要全部依賴），效益只在單階段執行；`registry`／`server` 的小差異在量測誤差內。
- `--help` 的 wall time 沒有變化（基準 0.15～0.20 s，之後 0.15～0.20 s）：CLI 本來就已延遲 import。
- 數字受檔案快取影響，單次機器量測，只看相對大小。

---

# 付費整合測試

`pytest tests/integration -m cost`：**6 passed**（200 s）。缺金鑰或網路的情況沒有發生。全部通過，所以沒有重跑基準點。

費用（僅就測試輸出中可見的摘要）：`test_prepare` 的 Prepare Pipeline 總計 $0.0703（爬蟲 $0.0117、augmenter $0.0586）；爬蟲測試的 exclude_words LLM 呼叫另有 $0.0087 與 $0.0117（5 次呼叫各一輪）。agent 與 rag query 等測試的輸出沒有費用摘要，未統計。測試在 `runs/` 留下產物，該資料夾已被 `.gitignore` 忽略。

---

# 過程中的發現（計畫外，未處理）

- `RAGRegistry._evict_if_needed()` 淘汰時呼叫 `evicted_rag.close()`，若丟例外會讓 `get()` 失敗，且該項目已從快取移除。**後續已修正**：比照 `close()` 只記錄、不往外拋，並補測試（舊程式碼上失敗）。
- `config/`、`utils/` 沒有 `__init__.py`（implicit namespace package）。目前運作正常，但會讓部分工具（如 import-linter）無法直接指定套件。
- pre-commit hook 會跑 trailing-whitespace、ruff、undersort，commit 時會自動修正行尾空白（第一次提交 `todo.md` 因此需要重新 add）。

# 未處理項目與後續建議

- **C3**：`WebpageMarkdownCleaner` 的 8 個公開 `@staticmethod`，與「Webpage Markdown Cleaner 獨立成一個模組」一併處理。
- **C4**：計時／重試裝飾器版本（新增功能，未評估）。
- **`try/except/pass` 改 `contextlib.suppress`**、`office_parser.py` 的 `list.extend`、3 處迴圈變數覆寫：風格調整，未做。
- `todo.md`「新增」段落的項目（`StrEnum`、`dataclass(slots=True)`、`match`、`lru_cache`、`itertools.batched`、`TaskGroup`）不在本計畫內。
- 建議合併前先讓 CI 跑一次，確認 `import-linter` 與 `check-import-time.sh` 在 GitHub Actions 環境正常（本機已通過，但 CI 尚未執行）。
