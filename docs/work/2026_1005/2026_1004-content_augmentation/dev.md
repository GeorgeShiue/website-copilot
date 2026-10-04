# Augmentation 重構與讀取網站文件：實作紀錄

> 計畫見 [plan.md](./plan.md)，逐階段的驗證數字見 [verification.md](./verification.md)。這裡只記錄與 plan 不同的決定、過程中的發現與取捨。共同關卡（`scripts/check.sh`、`tests/integration -m "not cost and not network and not heavy"`）每階段皆通過。

基準點：P0 `bd1e0b8`；P1（P1a～P1d 合併）`8150158`；P2（P2a～P2c 合併）`1ce052c`；正式發布為最後的資料 commit。

---

## P0：爬蟲排除文件 URL

- 文件規則放在 `utils/document_rules.py`（通用副檔名常數 + `is_document_url` + `normalize_url`），爬蟲與 P2a 的 `DocumentCollector` 共用；副檔名只比對 path（不分大小寫、忽略 query），`pdf.gif%20` 之類不會誤判。
- **與 plan 不同**：`error_no_markdown` 由 47 降到 **0**，而非「約 2」。原因是 `success=False` 的頁面改記為新的統計項 `error_failed`（3 筆：2 張被 anti-bot 擋的圖片 URL、1 個無副檔名的附件），不再混進 `no markdown`。
- 無副檔名且非站點樣式的附件（如 `static/file/13/1013/img/681518947`）仍會被導航一次並失敗，URL 規則無法辨識，已知限制。
- FilterChain 抽成 `_build_filter_chain()` 以便測試。

## P1：Augmenter 重構

### P1a：基準快照 + 共用下載器

- 快照 fake 的行為由 URL 的 sha1 決定（404、Content-Type 不符、首次逾時後成功、VLM 失敗、正常），與實作無關，重構時只替換 fake 掛入的位置。
- 注入的 svg 排在頁面最後一張，避免觸發 P1c 才修正的描述對位 bug。
- 發現 `prek` 的 end-of-file／trailing-whitespace hook 會改寫快照基準，導致逐字比對失敗；將 `tests/fixtures/` 排除在這些 hook 之外。
- 順手修正 `test_serve_command` 的過時 patch 目標（前一個 commit 將 `serve` 改名 `run_serve` 時漏改）。
- httpx 移到正式依賴，新增 `network`、`heavy` marker。

### P1b：改名與 config 分段

- `docs/exp/memo/webpage_image_summarizer/` 的 3 支實驗腳本同步改名（pyright 會檢查它們）。

### P1c：架構重構

- `Augmenter` 改為注入下載器（`Downloader` Protocol）、以 `augment()` 為入口；`ImageCaptioner` 在 `augment()` 開始時建立，無法判斷供應商或缺 API key 仍在下載前失敗。
- 統計單位改為不重複資源：成功／失敗／略過記在第一個引用頁面，其餘引用記 `cache_reuse`；重試時仍以頁面為單位顯示本輪涉及的頁面。
- 整輪重試的 `max_retries` 沿用舊語意：**最大輪數（含第一輪）**。
- 可恢復／永久失敗的判斷最後放在 `DownloadResult.recoverable`（P2a 時由 `Augmenter._is_recoverable` 搬入，兩種資源共用）：逾時、連線錯誤、5xx、429、403 為可恢復。
- 下載已成功、只有 VLM 失敗的項目，重試時只重做摘要，不重新下載（舊版會重新下載）。
- 實測：nculab 的舊爬取資料圖片是 Google Sites 簽名連結，已過期（全 403），重爬後才能做真實 VLM 比較。耗時 194.5 → 27.3 秒（約 7 倍）。
- `docs/exp/memo/webpage_image_summarizer/` 的實驗腳本依賴舊版內部方法，不再對應，改為從 pyright 排除（腳本與結果保留作歷史紀錄）。

### P1d：圖片過濾

- 計畫估計「VLM 呼叫約 161 → 約 105」是把小圖 28 張與內容相同 28 張當成互不重疊；實測兩者幾乎重疊（內容相同的主要就是那些圖示），實際為 166 → 132。
- 內容相同的圖片只有「代表圖片」（第一個下載到該內容者）有自己的記錄，其餘以 `shared_with` 指向它，寫回時即時解析，代表重試成功後共用者自動跟上。
- 尺寸先於內容去重；無法解碼尺寸的圖片不依尺寸過濾。
- 快照差異以腳本歸類（小圖略過 10 處、共用描述 5 處、未歸類 0 處）後才更新。

## P2：讀取網站文件

### P2a：文件骨架

- **與 plan 不同**：原檔資料夾放在與 `results/` 並列的 `files/`（plan 為 `results/files`），讓 `--run.use-latest-results` 取用的 run 資料夾與 `data/aug_webpages/<site>/` 結構一致。
- 爬取結果沒有保存頁面連結，`DocumentCollector` 改由 `fit_markdown` 解析 Markdown 連結（含圖示圖片的連結文字、`title` 屬性）。
- 格式判斷直接用 anydoc 的 `format_from_bytes`（PDF 標頭、OLE stream 名稱、ZIP 套件內容）作為 magic bytes 這一層，其後依序 Content-Disposition 檔名、Content-Type、URL 副檔名。
- 內容去重的代表在回寫時才決定（資源順序中的第一個），不在下載時決定，避免重試造成代表（與 entry 鍵）不穩定。
- **`source_pages` 在切塊之後才寫入 node**（`SourcePagesInjector`）：放在文件 metadata 會讓 `SentenceSplitter` 的 metadata 長度超過 chunk size 而失敗，且 llama-index 計算長度時不看 `excluded_*_metadata_keys`。同時排除於 embedding 與 LLM 文字之外。
- `source_pages` 的 `title` 用頁面鍵（與頁面的 `page_title` 一致），另附連結文字；爬取結果沒有保存頁面的人類可讀標題。
- 標題規則補了 Markdown 強調標記的清理（實跑發現 `**獎學金申請表**`）。
- `images.enabled: false` 時不建立 `ImageCaptioner`，因此不需要 API key，方便只跑文件。
- 文件 entry 加上 `alternate_urls`（內容相同的其他 URL），只存在 `results.json`，沒有帶進 node。

### P2b：PDF（Docling）

- Docling 延遲到第一份 PDF 才載入，converter 只建立一次並以鎖序列化（共用 GPU）。
- 依賴實測與計畫一致：新增 39 個套件，torch 版本不變，既有套件只有 `requests` 升版。模型快取：HuggingFace 與 RapidOCR（後者在 site-packages，`uv sync --reinstall` 後需重新下載）。
- 不重複 PDF 為 39 份（計畫以較早的爬取估 44 份）：38 份成功、1 份掃描檔記錄為失敗並略過。

### P2c：文件內圖片

- Docling 以 2 倍解析度裁切圖片，VLM 才看得清截圖小字；`PictureItem` 數與佔位符數不一致時不回傳圖片（佔位符移除）。
- anydoc 的 Markdown 輸出不含內嵌圖片，所以從文件模型找出圖片所在的頂層 block，以該 block 的第一段文字為錨點定位並插入佔位符（圖片在表格中時放在整個表格之後）。屬於啟發式定位，找不到錨點時放在目前位置。
- 文件內圖片以 `doc-image:<內容 sha1>` 為資源 URL（不需下載），與頁面圖片共用過濾、內容去重、並行上限與整輪重試；統計表中的「頁面」用文件內容 sha1 的標籤，不受代表 URL 變動影響。
- 只有 `images.enabled` 且 `documents.caption_images` 時才抽圖，否則所有佔位符移除（P2b 時殘留的 80 個佔位符因此消失）。
- 驗證 `fake VLM` 時發現沒有 key 的真實圖片會讓 fake 解碼失敗，改以內容雜湊代表。

## 正式發布

- `prepare ncucsie`、`prepare nculab` 以最終程式碼重跑並 publish：ncucsie 393 秒、$0.3629（217 筆，71 份文件）；nculab 93 秒、$0.0906。
- 發布後 `pytest tests/integration -m cost` 6 passed（含 19 題文件檢索問題集）。
- 資料 commit 時，prek 的 EOF／行尾／空白 hook 會改寫已發布的 md、json、二進位原檔與向量庫，第一次提交失敗；還原工作目錄後以 `--no-verify` 提交，並將 `data/` 加入這三個 hook 的排除清單。

## 未做／後續

- 檢索結果目前只回傳 `url`、`page_title`、`page_type`、`score`、`content`；node 上的 `source_pages`、`file_name` 沒有放進回傳（暫不需要）。
- 掃描版 PDF 的 OCR、xlsx／pptx 解析另案。
