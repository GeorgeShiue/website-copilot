# 1. 資料獲取
> [docs/code/modules/data_collect.md](modules/data_collect.md)

## 實作進度
- [x] **網站爬蟲**
    - [x] **網頁轉Markdown**
    - [x] **篩選網域**、**雜訊**
    - [x] **平行處理**

## 已知問題
- [ ] **HTML** 可包含更多**結構化資訊**

## 未來規劃
- [ ] 爬取**網站地圖**
- [ ] 讀取網站**後端資料庫**

# 2. 資料前處理
> [docs/code/modules/data_preprocess.md](modules/data_preprocess.md)

## 實作進度
- [x] **圖片處理**
	- [x] **下載圖片**
	- [x] **VLM 摘要圖片資訊**
	- [x] **平行處理**、**快取**
	- [x] **自動重試**
	- [x] **VLM Prompt 調整**
		- [x] **prompt-v1**
		- [x] **prompt-v2**
		- [x] **prompt-v3**
    - [ ] **下載和摘要拆成兩個模組**

## 已知問題
- [ ] **圖片摘要**可能喪失資訊
    1. 將圖片加入**多模態RAG**
    2. 保留**原始圖片**給**Agent**

## 未來規劃
- [ ] **表格處理**（對應多欄位→資料庫策略）
- [ ] **文件處理**（對應長文本→RAG 策略延伸）

# 3. 資料查詢 (當前進度)
> [docs/code/modules/data_retrieve.md](modules/data_retrieve.md)

## 實作進度
- [x] **RAG 檢索-長文本資料**
    - [x] **載入資料**（SimpleDirectoryReader + results.json）
    - [x] **轉換資料**（MarkdownNodeParser / SentenceSplitter / MarkdownHeadingMergeParser / MarkdownImageExtractor）
    - [x] **向量索引**（OpenAI **text-embedding-3-small** + **Qdrant** 本地持久化）
    - [x] **查詢引擎**（RetrieverQueryEngine + **Gemini** / **GPT** 回答生成）
    - [x] **成效評估**（FaithfulnessEvaluator + RelevancyEvaluator）
- [ ] **知識圖譜檢索（網站結構）** — 規劃中
- [ ] **資料庫檢索（多欄位資料）** — 規劃中

## 已知問題
- [ ] **純向量 RAG 本質局限**：對結構化列表（名單型）、時間範圍型查詢表現不佳；單一策略無法涵蓋所有資料類型
    1. **時間範圍型**— 時間表述未轉為明確年份，檢索易混入不同頁型
    2. **名單型**— 來源頁面含大量 VLM 圖片描述導致語義向量偏移，純向量檢索對結構化列表有本質局限
- [ ] **改善方向**：導入混合檢索（向量 + BM25 關鍵字）、動態降閾或備援機制，最終走向**資料類型分流路由**

## 未來規劃
- [ ] **資料類型分類器**：判斷查詢/資料類型，自動路由至適當檢索策略
- [ ] **知識圖譜檢索**：處理網站結構、頁面關聯性與導覽路徑
- [ ] **資料庫檢索**：處理表格、規格表等多欄位結構化資料