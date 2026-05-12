# 基本方案

## 實作流程

### 載入資料
- **工具**：使用 LlamaIndex 的 `SimpleDirectoryReader`。
- **路徑**：`data/webpages/prompt-v3/results`。
- **配置**：設定 `required_exts=[".md"]`，確保僅處理爬蟲生成的 Markdown 成果。

### 轉換資料
1. **MarkdownNodeParser**：初步解析 Markdown 結構，將標題路徑存入 Metadata (`header_path`)。
2. **SentenceSplitter**：進行細分塊。
    - **參數設定**
        - 參數a：`chunk_size: 500`, `chunk_overlap: 80`，過於細碎，資訊易斷裂
        - 參數b：`chunk_size: 800`, `chunk_overlap: 100`，表現最平衡 **(目前最佳)**
        - 參數c：`chunk_size: 1000`, `chunk_overlap: 150`，粒度過大，雜訊增加
    - **評估結果**：此配置能確保一張圖片的「摘要 + OCR 文字 + 關聯」完整保留在單一 Node 中，避免資訊斷裂。
3. **MarkdownHeadingMergeParser**：將 `MarkdownNodeParser` 產生的純標題節點，直接在解析階段併入下一個包含實質內容的節點。
4. **MarkdownImageExtractor**：將 node content 中的 markdown 圖片抽出到 metadata["images"]，格式為 `[{"url": ..., "alt": ...}]`，並把 content 中的圖片標記替換為其 alt 文字。

### 向量索引

### 混和檢索

### 查詢引擎

### 成效評估
- LlamaIndex
- Ragas

# 進階方案1：階層式分塊 (Hierarchical Chunking)

# 進階方案2：脈絡感知檢索 (Contextual Retrieval)

# 當前進度
- [ ] 基本方案
    - [x] 載入資料
        - [x] SimpleDirectoryReader 設定
        - [x] 自訂文件 metadata
    - [x] 轉換資料
        - [x] SentenceSplitter 參數調整 (800/100)
        - [x] MarkdownHeadingMergeParser 去除標題單獨 node
        - [x] MarkdownImageExtractor 擷取圖片資訊到 metadata
        - [ ] Embedding
    - [ ] 向量索引
    - [ ] 混和檢索
    - [ ] 查詢引擎
    - [ ] 成效評估
