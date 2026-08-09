# Src Layout Refactor (2026/08/09)

## 1. 摘要

| 日期 | 階段 |
|------|------|
| 08/09 | 規劃：盤點 import 相依網與 `__file__` 依賴，決定 `src/` 搬移範圍與 workflow 去留 |
| 08/09 | 決策：捨棄根目錄 `scripts/` 方案，workflow 保留在 `src/app/workflow/`（套件階層不變） |
| 08/09 | 實作完成：`git mv` 將核心程式碼搬入 `src/`，入口腳本與測試同步遷移 |
| 08/09 | 驗證：完整回歸 42 passed、ruff All checks passed、pyright 0 errors、CLI smoke 成功 |

**結論**：將專案由平鋪式 root-layout 改為 `src/` layout，核心程式碼（`app/`、`utils/`、入口腳本、測試）全部收進 `src/`。**import 套件名維持不變**（`app.*`、`utils.*`），因此所有程式碼 import 零變更；`workflow/` 隨 `app/` 一起搬入 `src/app/workflow/`，不另立 `scripts/`。

## 2. 動機（現狀問題）

| 問題 | 描述 |
|------|------|
| 核心程式碼與設定/資料混雜在根目錄 | `app/`、`utils/`、`cli.py` 等與 `configs/`、`data/`、`runs/` 平鋪，無法一眼區分「程式碼」與「執行期資料」 |
| 入口腳本在根目錄 | `cli.py` / `main.py` / `exp.py` 與設定檔、gitignore 混放，不符合 src-layout 慣例 |
| 測試在根目錄 `test/` | pytest `pythonpath = ["."]` 依賴 cwd，任何子資料夾執行都會失效 |
| 歷史脈絡 | `docs/work/2026_0530-run_refactor.md` 已規劃過「workflow 脫離 root」；本次為其延伸（src-layout 化），且先前曾討論 `scripts/` 方案（已捨棄） |

## 3. 決策過程

| 決策點 | 選項 | 結果 | 理由 |
|------|------|------|------|
| 搬移範圍 | ① 僅 `app/` + `utils/`；② **全部（含入口與測試）** | ② | 使用者選擇，根目錄只留設定與資料 |
| `workflow/` 去向 | ① 根目錄 `scripts/`；② `src/app/workflow/` | ② | 位置符合慣例（orchestration 屬 app 層套件），**import 路徑零變更**，且 `scripts/` 慣例語意（不可 import 的執行腳本）與實際內容不符 |
| import 策略 | ① 套件名不變（`app.*`/`utils.*`）；② 重新命名套件 | ① | 測試 mock 字串（`app.workflow.workflow_manager.RUNS_FOLDER_PATH`）不需更動，改動半徑最小 |

> 註：`scripts/` 方案需改 8 個檔案、17 處 import + 2 處 mock 字串；`src/app/workflow/` 方案為 **0 處 import 變更**。

## 4. 目標結構（Before / After）

### 4.1 Before（root-layout）

```text
website-copilot/
├── cli.py  main.py  exp.py       # 入口腳本散落根目錄
├── app/
│   ├── configs/  modules/  tools/  workflow/
├── utils/                        # 3 個 helper
├── test/                         # 3 個測試檔
├── configs/  data/  runs/  dev/  docs/
```

### 4.2 After（src-layout）

```text
website-copilot/
├── src/
│   ├── cli.py  main.py  exp.py   # 入口腳本
│   ├── app/
│   │   ├── configs/              # rag_config 等 3 檔
│   │   ├── modules/              # rag、rag_factory 等 5 檔
│   │   ├── tools/                # webpage_retriever
│   │   └── workflow/             # workflow / workflow_config / workflow_manager
│   ├── test/                     # 3 個測試檔
│   └── utils/                    # config_helper / log_helper / rag_helper
├── configs/  data/  runs/  dev/  docs/   # 不動
└── pyproject.toml  README.md  uv.lock  prek.toml
```

## 5. 實作內容

### 5.1 搬移（`git mv`，全部保留 git 歷史為 `R`）

```bash
mkdir -p src
git mv app src/app          # workflow/ 自動成為 src/app/workflow/
git mv utils src/utils
git mv cli.py main.py exp.py src/
git mv test src/test
```

### 5.2 `pyproject.toml`

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]         # 原本 ["."]
testpaths = ["src/test"]     # 新增
addopts = "-s -v"
```

- ruff / pyright 設定**不需變更**（`dev/**` 排除不受影響，`src/` 自動納入檢查）。
- runtime 路徑（`RUNS_FOLDER_PATH = "./runs"`、`configs/`、`data/`）基於 cwd，**搬移後不變**——只要從專案根目錄執行即可。

### 5.3 文件同步

| 檔案 | 變更 |
|------|------|
| `README.md` | 結構樹改為 src-layout |
| `docs/code/runs/cli.md` | 路徑加 `src/` 前綴；執行範例改 `python src/cli.py` |
| `docs/code/runs/config.md` | 同上 |
| `docs/code/runs/workflow.md` | 同上 |
| `docs/code/modules/data_collect.md` | 同上 |
| `docs/code/modules/data_preprocess.md` | 同上 |
| `docs/code/modules/data_retrieve.md` | 同上 |
| `docs/work/*` | **保留不動**（歷史決策記錄） |

## 6. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `app/`（12 檔） | `git mv` → `src/app/` | configs 3 + modules 5 + tools 2 + workflow 3 |
| `utils/`（3 檔） | `git mv` → `src/utils/` | config_helper / log_helper / rag_helper |
| `cli.py` / `main.py` / `exp.py` | `git mv` → `src/` | 入口腳本 |
| `test/`（4 檔） | `git mv` → `src/test/` | 含 `__init__.py` |
| `pyproject.toml` | 修改 | pytest `pythonpath = ["src"]` + `testpaths` |
| `README.md` | 修改 | 結構樹 |
| `docs/code/**`（6 檔） | 修改 | 路徑引用加 `src/` 前綴 |
| `src/test/test_rag_refactor.py` | 修改 | **修正既有測試 bug**（見 §7） |

## 7. 測試與驗證

| 驗證 | 結果 |
|------|------|
| `uv run pytest` | **42 passed**（8 warnings） |
| `uv run python src/cli.py --help` | ✅ tyro subcommands 正常（sys.path[0]=`src/`） |
| `uv run ruff check src` | ✅ All checks passed |
| `uv run pyright` | ✅ 0 errors（`typeEvaluation` unrecognized 為既有警告） |
| 根目錄殘留檢查 | ✅ 無 `app/`、`utils/`、`test/`、`cli.py` 等 |

### 7.1 修正的既有測試 bug（非搬移引起）

`test_qdrant_override_when_flag_true` 原本使用 `config_name="default"`，但 `configs/rag/default.toml` 自 commit `47c8426`（milvus hybrid）起 `vector_store_type = "milvus"`，導致 `run_rag_build` 走 milvus 分支、`qdrant_db_folder_path` 不被覆寫而斷言失敗。

```diff
- captured = self._run(monkeypatch, "default", save_vector_store_to_runs=True)
+ captured = self._run(monkeypatch, "qdrant", save_vector_store_to_runs=True)
```

> 此 bug 在 `dev` 分支（搬移前）同樣存在，與 src-layout 無關；屬順手修正。

### 7.2 執行方式變更

```bash
uv run python src/cli.py ...      # 原 cli.py
uv run pytest                     # 自動使用 src/test
```

> 注意：`uv run python -c "import app..."` 在根目錄會 `ModuleNotFoundError`（`python -c` 的 sys.path[0] 為 cwd，不含 `src/`）；透過入口腳本或 pytest 執行則正常。

## 8. 設計決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| workflow 位置 | `src/app/workflow/`（跟隨 app） | import 零變更；orchestration 屬 app 層，不拆獨立套件 |
| 捨棄 `scripts/` 名稱 | 不採用 | `scripts/` 慣例語意是「不可 import 的執行腳本」，與 workflow（可 import 套件）不符 |
| 套件名 | 維持 `app.*` / `utils.*` | 測試 mock 字串與全部 import 不需改動；改名可日後獨立進行 |
| 入口腳本 | 搬入 `src/` | 使用者決定「全部搬入」；根目錄只留設定與資料 |
| pytest 設定 | `pythonpath = ["src"]` + `testpaths = ["src/test"]` | 取代 root-layout 的 `["."]`，測試定位明確 |
| 測試 | 修正 qdrant 測試 config_name | 使測試與 `default.toml`（milvus）現況一致 |

## 9. 後續調整

- **commit 策略**：目前變更未 commit（`dev-refactor` 分支），建議拆成邏輯 commit：① 搬移（`git mv` + pyproject）② 文件更新 ③ 測試修正。
- **執行入口**：`docs/code/runs/*.md` 內範例已改為 `python src/cli.py`；若 README 未來新增執行範例，記得用新路徑。
- **改名彈性**：日後若想改 `workflow` 名稱（例如 `orchestration`），可獨立進行，與本次搬移正交。
- **CI 檢查**：若日後新增 CI，pytest 需以專案根目錄為 working directory 執行（`configs/`、`data/`、`runs/` 相對路徑依賴 cwd）。

## 10. 參考與證據

- `docs/work/2026_0530-run_refactor.md`（先前 run 相關結構調整，本次為其延伸）
- 完整測試輸出：42 passed；`git status` 顯示全部 `R`（rename）追蹤
- import 相依盤點：`app.workflow.*` 引用 17 處（cli/main/exp/tools/測試）、無 `__file__` 相對路徑依賴
