# 模型花費

## 實驗批次 1：20260428_181956

### 實驗資訊

- 來源 log：
  - [gpt-5-mini terminal.log](../../../data/test/20260428_181956/webpage_image_summarizer/model-gpt-5-mini/terminal.log)
  - [gpt-4.1-mini terminal.log](../../../data/test/20260428_181956/webpage_image_summarizer/model-gpt-4.1-mini/terminal.log)
  - [gpt-4o-mini terminal.log](../../../data/test/20260428_181956/webpage_image_summarizer/model-gpt-4o-mini/terminal.log)

### 最終花費比較

| 模型 | 成功數 | 失敗數 | 最終花費 (USD) |
|---|---:|---:|---:|
| gpt-5-mini | 8 | 0 | 0.026415 |
| gpt-4.1-mini | 8 | 0 | 0.004440 |
| gpt-4o-mini | 8 | 0 | 0.014477 |

**批次小計**：3 模型，總花費 0.045332 USD

---

## 實驗批次 2：20260429_112648

### 實驗資訊

- 來源 log：
  - [gemini-2.5-flash-lite terminal.log](../../../data/test/20260429_112648/webpage_image_summarizer/model-gemini-2.5-flash-lite/terminal.log)
  - [gemini-3.1-flash-lite-preview terminal.log](../../../data/test/20260429_112648/webpage_image_summarizer/model-gemini-3.1-flash-lite-preview/terminal.log)

### 最終花費比較

| 模型 | 成功數 | 失敗數 | 最終花費 (USD) |
|---|---:|---:|---:|
| gemini-2.5-flash-lite | 8 | 0 | 0.000846 |
| gemini-3.1-flash-lite-preview | 8 | 0 | 0.006016 |

**批次小計**：2 模型，總花費 0.006862 USD

---

## 總體統計摘要

| 批次 | 模型數 | 成功 | 失敗 | 總花費 (USD) |
|---|---:|---:|---:|---:|
| 20260428_181956 | 3 | 24 | 0 | 0.045332 |
| 20260429_112648 | 2 | 16 | 0 | 0.006862 |
| **合計** | **5** | **40** | **0** | **0.052194** |

## 結論

- **成本效率最佳**：gemini-2.5-flash-lite（0.000846 USD），比 OpenAI 的 gpt-4.1-mini 便宜 5 倍以上。
- **成本次佳**：gpt-4.1-mini（0.004440 USD）。
- **高成本模型**：gpt-5-mini（0.026415 USD），最貴的選項。
- Gemini Flash Lite 系列提供了極具競爭力的定價，適合大規模生產環境。
