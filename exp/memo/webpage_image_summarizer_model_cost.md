# Webpage Image Summarize 模型花費

## 實驗資訊

- 實驗批次：20260428_181956
- 來源 log：
  - [gpt-5-mini terminal.log](../../../data/test/20260428_181956/webpage_image_summarizer/model-gpt-5-mini/terminal.log)
  - [gpt-4.1-mini terminal.log](../../../data/test/20260428_181956/webpage_image_summarizer/model-gpt-4.1-mini/terminal.log)
  - [gpt-4o-mini terminal.log](../../../data/test/20260428_181956/webpage_image_summarizer/model-gpt-4o-mini/terminal.log)

## 最終花費比較

| 模型 | 成功數 | 失敗數 | 最終花費 (USD) |
|---|---:|---:|---:|
| gpt-5-mini | 8 | 0 | 0.026415 |
| gpt-4.1-mini | 8 | 0 | 0.004440 |
| gpt-4o-mini | 8 | 0 | 0.014477 |

## 統計摘要

- 三份 log 全部成功，沒有任何 download_failure 或 summarize_failure。
- 三者總花費為 0.045332 USD。
- 本次最便宜的是 gpt-4.1-mini，最貴的是 gpt-5-mini。

## 結論

若本次重點是控制成本，gpt-4.1-mini 的表現最佳；若需要保留較高版本模型作為對照，gpt-4o-mini 可作為中間方案，gpt-5-mini 則是成本最高的版本。
