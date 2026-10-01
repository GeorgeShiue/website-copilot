# 資料儲存重構 plan

> 對應 [todo.md](../../todo.md)「技術債 → 資料儲存」。網站知識庫版本控制不在本次範圍（見 D2）。

## Context

1. **`rag-query --force-rebuild` 直接重建正式向量庫**：`pipelines/exp.py` 的 `run_rag_query` 以 `published_target(site_id)` 呼叫 `build_rag(..., force_rebuild=...)`，會清掉並重建 `data/rag/{site_id}/milvus.db`。違反「建庫不直接寫入 data/」，也繞過 `publish_vector_store` 的原子替換；重建中途失敗時正式向量庫會損毀。
2. **向量庫內部路徑過深且有重複片段**：目前 `data/rag/nculab/milvus.db` 是目錄（Milvus Lite），parquet 檔實際位置為

   ```
   data/rag/nculab/milvus.db/collections/nculab/partitions/_default/data/data_000001_000277.parquet
   ```

   `nculab` 在路徑中出現兩次（站點資料夾、Milvus collection 名稱），`milvus.db` 又是目錄而非單一檔案。
3. **載入向量庫會寫入 data/**：Milvus Lite 載入 collection 時會在 `collections/{collection}/partitions/_default/indexes/` 建立索引檔（已實測：對複本執行 `load_collection` 後出現 `data_000001_000277.embedding.flat.idx`，`close()` 後仍保留）。此行為與 rag-query／serve 無關，任何載入 `data/rag/{site}/milvus.db` 的程式都會觸發；因此 git 工作樹在跑完整合測試後會出現未追蹤檔案。

## 已確認決策

| # | 問題 | 決策 |
|---|---|---|
| Q1 | `rag-query --force-rebuild` | 重建到 run 的 `results/` 的方案 A 已被 D4 取代：**移除 `run_rag_query` 的 `force_rebuild`**，建庫邏輯只留在 `run_rag_build` |
| Q2 | 路徑重整的範圍 | 解決「parquet 路徑過深且有重複片段」，見 D1 |
| Q3 | 載入時寫入 data/ | 來源已查出（Context 3）；處理方式見 D5 |
| D1 | 向量庫目錄佈局 | **兩項都做**：collection 名稱固定為 `chunks`；去掉 `milvus.db/` 這一層，Milvus 資料夾直接以 `{site_id}.db` 命名（受 `.db` 結尾限制，見 D8、D10），設定紀錄移到其中的 `meta/` |
| D2 | 版本控制 | **移出本次規劃**：版本控制日後一次在所有模組的儲存機制引入，本次不為此預留目錄結構 |
| D3 | webpages 是否版本化 | 隨 D2 移出 |
| D4 | rag-query 的重建功能 | 移除；`run_rag_query` 只查詢已發布向量庫，要建庫一律走 `run_rag_build` |
| D5 | 載入時寫入 data/ | **暫時採 `.gitignore` 忽略 `indexes/`**（方案 B）；索引檔用途見下 |
| D6 | 向量庫是否進 git | **暫時保留**進 git |
| D7 | 既有向量庫的遷移 | 方案 b：從 `data/webpages/{site}` 只重跑建庫階段（`run rag-build` + publish），不重爬、不重跑圖片摘要 |
| D8 | `meta/` 放在 Milvus 資料夾內 | 已驗證可行，並發現資料夾須以 `.db` 結尾的限制（見「D8 驗證結果」） |
| D9 | 查詢 runs/ 中的實驗向量庫 | 方案 b：`rag-query` 新增 `--run.vector-store-run <run 路徑>`，**本次一併實作**（見 Phase 1） |
| D10 | 受 `.db` 結尾限制的佈局 | **採 (i)**：`data/rag/{site_id}.db/` 為 Milvus 資料夾，`meta/` 放在其中；publish 以整個資料夾原子替換，向量庫與紀錄同版（代價：與 `data/webpages/{site}` 命名不一致） |
| D11 | `vector_store_run` 是否核對建置參數 | 不比對（與已發布向量庫一致），只在 log 印出建庫 run 的 `source` |

### D1／D10：更新後的路徑

```
# 現況
data/rag/nculab/
├── milvus.db/                                   ← Milvus Lite 資料夾（名字像檔案但是目錄）
│   ├── collections/
│   │   └── nculab/                              ← collection 名稱 = site_id（重複）
│   │       └── partitions/_default/data/data_000001_000277.parquet
│   ├── databases/  LOCK  ...
├── module_config.yml                            ← 設定紀錄與向量庫混在同一層
├── run_config.yml
└── terminal.log

# 更新後（D10 方案 i）
data/rag/nculab.db/                              ← Milvus 資料夾（名稱須以 .db 結尾）
├── collections/
│   └── chunks/                                  ← 固定名稱，不再重複 site_id
│       └── partitions/_default/data/data_000001_000277.parquet
├── databases/  LOCK  ...
└── meta/                                        ← 設定紀錄集中，與向量庫同一次原子替換
    ├── module_config.yml
    ├── run_config.yml
    ├── site_config.yml
    └── terminal.log
```

parquet 路徑由 `data/rag/nculab/milvus.db/collections/nculab/partitions/_default/data/*.parquet` 縮短為 `data/rag/nculab.db/collections/chunks/partitions/_default/data/*.parquet`。`collections/…/partitions/_default/data/` 是 Milvus Lite 的內部結構，無法移除。

站點資訊仍保留在 node metadata（`index.py` 寫入的 `site_id`），不受 collection 改名影響。

### D5：索引檔（`indexes/*.idx`）的用途

- parquet 是向量庫的**資料本體**；`indexes/` 下的 `.idx` 是 Milvus Lite 載入 collection 時，依 `manifest.json` 的 `index_specs`（dense embedding 為 `FLAT`／`IP`、sparse embedding 為 `SPARSE_INVERTED_INDEX`／`IP`）由 parquet 建出的**檢索索引**，供向量搜尋使用。
- 已實測可重建：刪除 `indexes/` 後再次載入，`data_000001_000277.embedding.flat.idx` 會重新產生，因此不屬於需要版控的內容。實測只觀察到 dense 的 `.idx`，sparse 索引是否也落地未確認。
- 因此選擇 `.gitignore` 忽略（`data/rag/**/indexes/`）：接受載入時寫入 `data/`，只避免誤提交。限制：載入仍會改動 `data/`，若日後 `data/` 掛載為唯讀會失敗，屆時再改為載入前複製到暫存。

### D8 驗證結果

在 `data/rag/nculab` 的複本上實測（pymilvus／Milvus Lite）：

| 項目 | 結果 |
|---|---|
| Milvus 資料夾內放額外的 `meta/` | 可行：載入、查詢、關閉都正常，`meta/` 不受影響 |
| 整個資料夾 `os.replace` 改名後重新載入 | 可行（原子替換整個資料夾沒問題） |
| 資料夾名稱 | **必須以 `.db` 結尾**：`MilvusClient("nculab")` 會報 `uri: nculab is illegal, needs start with [unix, http, https, tcp] or a local file endswith [.db]` |
| `rename_collection("nculab", "chunks")` | 可行（成功，collection 改名後資料夾內的 `collections/` 也改名），表示 D7 的方案 c（改名遷移）技術上可行；已依決策採方案 b |

因此「站點資料夾直接作為 Milvus 資料夾」不能照原樣實現，改採 D10 方案 (i)。

## 變更範圍

### Phase 1：移除 `run_rag_query` 的 `force_rebuild`（D4）

- `RAGQueryRunConfig` 刪除 `force_rebuild`；`run_rag_query` 不再傳 `force_rebuild`，只以 `published_target` 載入查詢；向量庫不存在時報錯並提示先執行 `prepare` 或 `run rag-build`。
- `build_rag` 的 `force_rebuild` 參數保留（`run_prepare` 仍使用 `force_rebuild=True`）；`rag-query` 路徑改為 `build_or_load` 的載入分支，確認不會觸發重建。
- 同步更新：`exp.py` docstring、`tests/unit/test_rag_tools.py`、`docs/code/runs/{cli,workflow}.md`、`docs/code/phase1/modules/data_retrieve.md`、README 中的 `--run.force-rebuild`；新增 CLI 測試確認 `--run.force-rebuild` 已被拒絕。
- `.gitignore` 加入 `data/rag/**/indexes/`（D5）。
- **D9：`rag-query --run.vector-store-run <run 路徑>`**
  - `RAGQueryRunConfig` 新增 `vector_store_run: str | None = None`：指向 `rag-build` 的 run 資料夾（如 `runs/20261001_162227/rag_build/nculab/vector_store_type-milvus`），向量庫位置為 `<路徑>/results/milvus.db`；未指定時查詢已發布向量庫（`published_target`）。
  - 查詢用的 `RAGConfig` 仍由 `--run.config` 與 `--module.*` 決定（可以對同一份向量庫試不同的 retriever／query engine 參數）；向量庫本身的建置參數（embedding、nodes 等）需與建庫時一致，載入時不做額外比對，只在 log 印出建庫 run 的 `source`（D11）。
  - 路徑不存在或找不到 `results/milvus.db` 時報錯；站點以 `<路徑>/site_config.yml` 的 `site_id` 核對 `run_config.site`，不一致時報錯。
  - 此模式完全唯讀（與已發布向量庫相同），不寫入 `data/`。
  - 測試：以 `rag-build`（save）建出的 run 路徑查詢；路徑錯誤／站點不一致報錯；`published_target` 與 `vector_store_run` 的 target 位置。

### Phase 2：向量庫路徑重整（D1、D10）

- collection 名稱改為常數 `chunks`（`IndexBuilder`、`RAGRegistry`、`load_rag`）；`RAGTarget.milvus_uri` 在 data/ 為 `data/rag/{site_id}.db`，在 runs/ 維持 `results/milvus.db`（皆以 `.db` 結尾）。
- **publish 流程**：staging 改為 `data/rag/.staging-*.db`（Milvus 資料夾本身）→ 建庫 → 將 `meta/`（module／run／site config、log）寫入 staging → 以 `os.replace` 整個資料夾換成 `{site_id}.db`（先 `.old` 備份、失敗還原，沿用現行邏輯）。因此 `publish_run_metadata` 的 rag 部分改為寫入 staging 的 `meta/`，不再寫到 `data/rag/{site_id}/`。
- 受影響：`ingestion/indexing/index.py`、`retrieval/{factory,registry}.py`（`RAGRegistry.has` 與列出站點改以 `*.db` 資料夾判斷，並忽略 `.staging-*`／`.old`／`.tmp`）、`agent/tools/site_discovery.py`、`storage/data_manager.py`（`create_vector_store_staging`、`publish_vector_store`、`publish_run_metadata`）、`pipelines/prepare.py`。
- 既有 `data/rag/{nculab,ncucsie,claudecode}` 以 `run rag-build` + publish 重建（D7 方案 b，需 embedding 費用，執行前先向使用者確認）；舊的 `data/rag/{site}/` 資料夾隨重建刪除。
- 測試：`test_serve_rag_loading.py`（repo 內已發布向量庫可載入）、`test_pipeline_prepare.py`（publish 位置與 `meta/`）、`test_rag_tools.py`、`test_data_manager`（原子替換）；文件：README、`docs/code/runs/{config,workflow}.md`、`docs/code/phase1/modules/data_retrieve.md`、`phase2_3_mvp/modules/*.md`。

## 驗證

### 共同關卡（每個 Phase 的 commit 都必須通過）

1. `scripts/check.sh`（ruff、pyright、`tests/unit`、widget 同步）通過。
2. `uv run pytest tests/integration -m "not cost"`（免費）通過。
3. CLI 冒煙：`website-copilot {prepare,serve} --help`、`run <module> --help` 皆 exit 0。
4. 測試前後 `git status --short` 無新增未追蹤檔（驗證 `indexes/` 已被忽略、測試不會弄髒 `data/`）。
5. 結果記錄在該 Phase 的 `dev.md`（沿用上一份 plan 的做法）。

### 驗證 `data/` 不被寫入的方法

- **單元測試（mock）**：`run_rag_query` 全程不呼叫 `build_rag(force_rebuild=True)`、不呼叫 `publish_*`；以 `tmp_path` 作為 data 資料夾，執行前後比對整個目錄樹（檔名 + 內容 hash）完全相同。
- **實測**：對真實的 `data/rag/{site}` 計算「排除 `indexes/` 的目錄樹 hash」，執行 `rag-query`（已發布與 `--run.vector-store-run` 兩種模式）前後比對相同。

### Phase 1 額外檢查

- CLI：`--run.force-rebuild` 被 tyro 拒絕；`run rag-query --help` 顯示 `--run.vector-store-run`。
- `vector_store_run` 單元測試：
  - 以 `rag-build`（save）建出的 run 路徑，target 的 `milvus_uri` 為 `<路徑>/results/milvus.db`、`site_id` 為 run 的站點。
  - 路徑不存在、缺 `results/milvus.db`、`site_config.yml` 與 `run_config.site` 不一致都報錯，訊息含路徑。
  - 未指定時使用 `published_target`；向量庫不存在時錯誤訊息提示先 `prepare` 或 `run rag-build`。
  - log 印出建庫 run 的 `source`（D11）。
- `.gitignore`：`git check-ignore -v data/rag/nculab/milvus.db/collections/nculab/partitions/_default/indexes/x.idx` 命中規則；`data/rag/**/indexes/` 以外的路徑不被誤忽略（如 `data/rag/**/data/*.parquet` 仍可被追蹤）。
- grep：`grep -rn "force_rebuild\|force-rebuild" src tests README.md docs/code` 只剩 `build_rag`／`run_prepare`／`IndexBuilder` 內部使用，無 `rag-query` 相關。
- **付費實測**（每次先向使用者確認）：對 `nculab` 執行
  1. `run rag-build nculab --run.config test`（建出實驗向量庫，記下 run 路徑）；
  2. `run rag-query nculab --run.config test --run.vector-store-run <該路徑>`；
  3. `run rag-query nculab --run.config test`（已發布向量庫）。
  確認兩種模式皆成功、`module_config.yml` 與 log 正確，且 data/ 的目錄樹 hash 前後相同。

### Phase 2 額外檢查

**遷移前基準（動工前以舊程式產生，腳本放 scratchpad、不進版控，結果貼進 dev.md）**：對 `data/rag/{nculab,ncucsie,claudecode}` 輸出 collection 的筆數、每筆 node 的 `text` hash 與 metadata（`site_id`、url 等）的排序清單、`du -sh` 體積，作為遷移後比對的基準。（`embedding` 向量不比對：重建後可能有微小差異，由檢索結果驗證。）

**路徑與結構**

- 每個站點：`data/rag/{site}.db/` 存在、`list_collections()` 恰為 `['chunks']`、`meta/` 含 `module_config.yml`／`run_config.yml`／`site_config.yml`／`terminal.log`；舊的 `data/rag/{site}/` 不存在。
- 路徑品質：所有 parquet 的路徑中，`site_id` 只出現一次（資料夾名）、沒有 `milvus.db` 目錄層；單元測試以 regex 斷言。
- node metadata 的 `site_id` 仍存在且等於站點。

**publish 原子性（單元測試，沿用 `tmp_path` 假 data 資料夾）**

- 成功：舊版被新版取代，`meta/` 與向量庫來自同一次建置；無殘留 `.staging-*`／`.old`／`.tmp`。
- 失敗注入（在 `os.replace` 前後各丟例外）：正式資料夾維持舊版內容不變、staging 被刪除。
- 前次中斷殘留的 `.old`／`.tmp` 在下次 publish 時被清掉。
- 已開啟舊版的 reader（Registry）在 publish 期間不報錯（沿用現有測試的做法）。

**讀取端**

- `RAGRegistry.has`／列出站點（`list_knowledge_bases`）只認 `*.db` 資料夾，忽略 `.staging-*`／`.old`／`.tmp`；單元測試放入這些干擾資料夾確認不被列為站點。
- `test_serve_rag_loading.py`：repo 內三個已發布向量庫皆能以 site_id 載入（collection 名稱 `chunks`、位置）。
- `serve` 整合測試與 `agent` 對三個站點的 `webpage_retriever` 呼叫（免費部分以現有測試涵蓋）。

**遷移後比對（付費，先向使用者確認；D7 方案 b：每站 `rag-build` + publish）**

- 筆數與 text hash、metadata 排序清單與基準完全相同（webpages 資料來源未變，建庫結果應一致）；不同者逐一檢視原因。
- 檢索一致性：每站以 `sample_query` 查詢，top-k 的 url 集合與遷移前基準重疊（預期完全相同或僅排序差異）；結果貼進 dev.md。
- 體積：`du -sh data/rag/*` 與基準比較；git 差異不應有 `indexes/` 檔案。
- grep：`grep -rn "milvus.db" src tests README.md docs/code` 只剩 runs/ 的 `results/milvus.db`（含 `vector_store_run`）與刻意保留者；舊路徑 `data/rag/{site}/milvus.db` 不再出現。
- 整合測試（含 cost）：`uv run pytest tests/integration` 全數通過；`prepare nculab --run.config test` 完整流程後，確認發布位置與 `meta/`。

### 付費測試的安排

- 時機：Phase 1 完成後做一次（驗證 D9），Phase 2 遷移與完整整合測試做一次。
- 執行者：Claude 執行，**每次執行前先向使用者確認**；結果與花費摘要記錄在 `dev.md`。

## 執行順序

| Phase | 內容 | 依賴 |
|---|---|---|
| 1 | 移除 `run_rag_query` 的 `force_rebuild`、新增 `--run.vector-store-run`（D9、D11）、`.gitignore` 忽略 `indexes/` | — |
| 2 | 向量庫路徑重整（D1、D10）；既有三個站點以 `run rag-build` + publish 重建（D7 方案 b） | 1 |

每個 Phase 一個 commit；Phase 2 動工前先產生遷移前基準。
