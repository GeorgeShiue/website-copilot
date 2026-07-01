# Run Refactor (2026/5/30)

本文整理這一輪對 run 相關模組與 workflow manager 的結構調整討論，重點是把「workflow」、「執行留檔」與「入口腳本」分開，讓專案在檔案結構層面更容易維護與擴充。

## 1. 重構目標

這次調整主要想解決四件事：

1. run 相關邏輯目前散落在 `run.py`、`main.py`、`cli.py`、`exp.py`，入口責任不夠清楚。
2. `run.py` 其實已經不是單純 helper，而是四個 workflow 的共用 workflow 層。
3. `run_manager.py` 負責的不只是工具函式，而是整個執行 artefact 的路徑、結果、設定與 log 管理。
4. 目前的資料夾命名雖可運作，但尚未把「入口」、「workflow」、「workflow manager」、「modules」、「configs」分成更明確的邊界。

因此目前的方向是：

- 把 run 的流程編排獨立成專門的 workflow 模組。
- 把 `run_manager` 移到 workflow 資料夾下，作為 workflow manager。
- 保留現有的模組 config 結構與 `config/*.toml` 分層，避免不必要的改動。
- 讓入口檔只保留薄包裝，降低 root 層腳本的混亂度。

## 2. 目前的 run 結構

### 2.1 入口層

目前專案有三個明顯的 run 入口：

- `main.py`：預設串接網站爬蟲與圖片摘要流程。
- `cli.py`：使用 `tyro` 暴露四種流程的正式 CLI 入口。
- `exp.py`：偏向人工實驗與批次跑不同 `config_name` / model / prompt 組合。

這三者都在根目錄，但其用途不同，適合進一步區分成「正式 CLI」、「demo pipeline」、「experiments」。

### 2.2 Workflow 層

`run.py` 目前集中定義四個 workflow：

- `run_website_crawler()`
- `run_webpage_image_summarizer()`
- `run_rag_build()`
- `run_rag_query()`

它們都做同樣類型的事情：

1. 載入對應 config。
2. 建立或重用 `RunManager`。
3. 決定 run path。
4. 記錄 log、設定與結果。
5. 執行對應的模組流程。

所以 `run.py` 已經是 workflow 層，而不是單純的工具集合。

### 2.3 Workflow manager / artefact 層

`run_manager.py` 目前負責：

- 建立 `runs/<timestamp>/<module>/<run>/`。
- 管理 `results.json`、`results/`、`module_config.toml`、`run_config.toml`、`terminal.log`。
- 寫入與載入執行結果。
- 提供執行路徑的 log 顯示。

這表示它是執行 artefact 的生命週期管理器，也就是 workflow manager，而不是一般通用 utils。

### 2.4 Modules / configs 層

目前 app 底下的程式碼與 config 已經可以拆成兩群：modules 與 configs。

- `app/modules/` 放各模組的實作邏輯，例如 crawler、summarizer、rag。
- `app/configs/` 放各模組的 config dataclass，例如 crawler config、summarizer config、rag config。

這一層的切法可以讓 workflow、module implementation、config 三者分工更清楚。

## 3. 建議的檔案結構調整

### 3.1 調整原則

1. 入口檔要薄。
2. workflow 要集中。
3. workflow manager 要獨立且放在 workflow 相關資料夾內。
4. modules 與 configs 要分區，不再平鋪放在 app 根目錄。

### 3.2 建議歸位方式

- `run.py` → 移到 `app/workflow/workflows.py`
- `run_config.py` → 移到 `app/workflow/workflow_config.py`
- `run_manager.py` → 移到 `app/workflow/workflow_manager.py`
- `cli.py` → 保留為正式 CLI 入口，但只做參數組裝與 workflow 呼叫
- `main.py` → 保留為預設 demo pipeline，或後續改放 `scripts/`
- `exp.py` → 改放 `experiments/` 或 `scripts/experiments/`

這樣拆之後，`utils/` 就只保留真正通用的 helper，例如 config、log、rag helper。

## 4. 調整後的專案結構示意圖

```text
website-copilot/
├── cli.py                        # 正式 CLI 入口，薄包裝
├── main.py                       # 預設 demo pipeline
├── exp.py                        # 實驗入口，建議後續移出 root
├── app/
│   ├── workflow/
│   │   ├── workflows.py          # 由 run.py 拆出：四個 workflow
│   │   ├── workflow_config.py    # 由 run_config.py 搬入：workflow 用 dataclass
│   │   └── workflow_manager.py   # 由 run_manager.py 搬入
│   ├── modules/
│   │   ├── rag.py
│   │   ├── webpage_image_summarizer.py
│   │   └── website_crawler.py
│   └── configs/
│       ├── rag_config.py
│       ├── webpage_image_summarizer_config.py
│       └── website_crawler_config.py
├── utils/
│   ├── config_helper.py
│   ├── log_helper.py
│   └── rag_helper.py
├── config/
│   ├── rag/
│   ├── webpage_image_summarizer/
│   └── website_crawler/
├── data/
├── runs/
├── test/
└── docs/
    └── works/
        ├── config_refactor.md
        └── run_refactor.md
```

## 5. 建議的遷移順序

1. 先把 `run.py` 內四個 workflow 搬進 `app/workflow/workflows.py`，讓 workflow 先脫離 root。
2. 再把 `run_manager.py` 移到 `app/workflow/workflow_manager.py`，先保留既有概念，降低改動半徑。
3. 接著把 `run_config.py` 改放進 `app/workflow/workflow_config.py`，讓 workflow config 跟 workflow 放在一起。
4. 最後把 `app` 底下的程式碼整理成 `modules/` 與 `configs/`，讓模組實作與 config 分離。

## 6. 目前的邊界與限制

這次調整建議保留幾個邊界：

- `config/` 的分模組 TOML 結構維持不變。
- 各模組 config dataclass 仍然保留自己的驗證規則。
- `workflow manager` 的行為邊界不變，只是位置與命名更明確。
- `main.py` 與 `exp.py` 是否保留在 root，取決於團隊是否要把它們視為正式入口。

這些限制是刻意保留的，目的是先把責任邊界整理好，而不是一次把整個專案重構成新架構。

## 7. 結論

這一輪 run 結構重構的本質，是把目前已經存在的四種角色明確落位：

- 入口層負責啟動。
- workflow 層負責流程。
- workflow manager 層負責 artefact。
- configs 層負責模組設定與驗證。
- modules 層負責各模組實作。

對專案的實際效果是：

- `run.py` 不再承擔過多 root-level 責任。
- `run_manager` 會和 workflow 放在同一區塊，語意更一致。
- app 底下會更接近「modules、configs、workflow」三層分明的形狀。

## Evidence

- [run.py](run.py)
- [cli.py](cli.py)
- [main.py](main.py)
- [exp.py](exp.py)
- [run_config.py](run_config.py)
- [utils/run_manager.py](utils/run_manager.py)
- [utils/config_helper.py](utils/config_helper.py)
- [app/website_crawler_config.py](app/website_crawler_config.py)
- [app/webpage_image_summarizer_config.py](app/webpage_image_summarizer_config.py)
- [app/rag_config.py](app/rag_config.py)
- [config/website_crawler/default.toml](config/website_crawler/default.toml)
- [config/webpage_image_summarizer/default.toml](config/webpage_image_summarizer/default.toml)
- [config/rag/default.toml](config/rag/default.toml)
- [docs/works/config_refactor.md](docs/works/config_refactor.md)