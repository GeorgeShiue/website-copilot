# Query Experiment

## 5 種問題實驗 (2026/6/26)

### 實驗
- [x] 實驗室近三年發表過哪些論文？
- [x] 實驗室的成員有哪些人？
- [x] 實驗室在2024年有哪些活動？
- [x] 加入實驗室需要準備哪些資料？
- [x] 如何聯絡研究室指導教授？

### 統整
- [x] 整理實驗結論

## 語言模型實驗 (2026/6/26)

### 前置修正

- [x] **修正 evaluator confound**：`evaluate()` 中 evaluator 與 query engine 使用同一個 LLM，造成評分偏差。需將 evaluator 固定為 `gpt-5.4`（獨立的 OpenAI 模型），與被測試模型脫鉤。

### 設定檔

- [x] 建立 5 個 LLM 實驗用 TOML 設定檔（`configs/rag/*.toml`），共用 `top_k=5, cutoff=0.45`
  - [x] `configs/rag/gemini-3.1-flash-lite.toml`（對照組，與 default 一致）
  - [x] `configs/rag/gemini-3-flash.toml`（mid-tier frontier flash）
  - [x] `configs/rag/gemini-3.5-flash.toml`（旗艦 stable flash）
  - [x] `configs/rag/gemini-2.5-pro.toml`（前代 pro）
  - [x] `configs/rag/gemini-3.1-pro.toml`（當前 top-tier pro，⚠️ 因 daily limit 過低，尚未測試）

### 批次執行
> 分 3 輪，每輪測 1 個問題 × 4 個模型（`gemini-3.1-pro` 因 daily limit 過低暫跳過）

- [x] **第一輪**：時間理解 + 摘要 + 推理（核心鑑別題） - `實驗室近三年發表過哪些論文？`
- [x] **第二輪**：檢索失敗時的生成品質（邊界測試） - `實驗室的成員有哪些人？`
- [x] **第三輪**：跨 chunk 整合推理（補充推理題）  - `實驗室開發過哪些與 AI 相關的應用？`

### 分析

- [x] 定量分析：彙整 Faithfulness / Relevancy pass rate 對照表（4 models × 3 questions，實際測試 4 個；`gemini-3.1-pro` 待日後補測）
- [x] 定量分析：紀錄各模型的 Empty Response 次數
- [x] 定性分析：挑選 1~2 次 response 人工審閱——邏輯連貫性、拒答誠實度、回答長度
- [x] 整理結論：決定是否更換預設 LLM，或保留 `gemini-3.1-flash-lite`
