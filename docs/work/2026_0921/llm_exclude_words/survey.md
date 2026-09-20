# 使用 LLM 產生 exclude_words：方案調查與實驗結果

> 調查能否用 LLM 取代「人工看爬取結果、逐一挑出雜訊寫進 `exclude_words`」的工作，並以 nculab、ncucsie 兩個站台實測。

## 調查背景

`clean_markdown()`（`src/utils/markdown_cleaner.py`）的雜訊移除核心是 `exclude_words` 行級過濾：只要一行**包含**清單中任一詞，整行刪除。清單由人工維護於 `configs/website_crawler/<site>.toml`，每個新站台都要重做。

前一輪 winnow-md 實驗（`../winnow_webpage_clean/claude/survey.md`）結論是：啟發式工具清不掉固定頁面元件文字（`Google Sites`、`焦點新聞`…），對清單型正文還會誤刪，無法取代 `exclude_words`。本次改問：**能否讓 LLM 幫忙產生 `exclude_words`？**

---

## 一、LLM 取得乾淨 Markdown 的方法（依 LLM 介入位置分類）

| # | 方法 | LLM 做什麼 | 代表工具 | 主要優點 | 主要缺點 |
|---|---|---|---|---|---|
| 1 | 逐頁 LLM 過濾 | 每頁全文重新生成乾淨 Markdown | Crawl4AI `LLMContentFilter` | 與現有 crawl4ai 相容；可用自然語言指令 | 每頁花 token；生成式有改寫、截斷、靜默遺失風險 |
| 2 | 專用小模型 HTML→Markdown | 1.5B 級模型直接轉換 | Jina ReaderLM-v2 | 成本低、可本地跑 | 同樣是生成式；長頁面易重複或截斷；中文需自行驗證 |
| 3 | 區塊分類 | 小模型對每個區塊判斷正文/雜訊，只保留或刪除 | Dripper（MinerU-HTML）、Web2Text、Pulpie | 只刪不改寫，零幻覺；token 小 | 需部署模型；清單型頁面是否誤刪待驗證 |
| 4 | 由 LLM 產生規則 | 只看少數樣本頁，輸出 `exclude_words`／selector | （自行實作） | 每站約一次成本；規則確定、可審查、可寫進設定檔 | 規則品質取決於樣本；改版要重跑 |
| 5 | LLM 後審 | 只判斷「不確定區塊」該刪或留 | （自行實作） | 兼顧 recall 與成本 | 需設計不確定區塊的篩選條件 |
| 6 | 託管 API | 服務直接回傳乾淨 Markdown | Firecrawl、Jina Reader | 省工 | 收費、無法客製，難搭配跨頁去重與 metadata |

以上為依搜尋摘要與架構性質整理，沒有逐頁閱讀原文，模型大小等細節以摘要為準。

### 方案 4+5 與方案 1 的差異（架構性質推論，未實測）

| 面向 | 方案 4+5 | 方案 1 |
|---|---|---|
| LLM 看什麼 | 4：每站少數樣本；5：只看不確定區塊 | 每頁全部內容 |
| LLM 輸出 | 規則或刪留判斷 | 重新生成的整份 Markdown |
| 成本 | 低，與頁數幾乎無關 | 隨頁數線性增加 |
| 幻覺／改寫風險 | 低 | 中到高 |
| 可重現、可審查 | 高（規則寫進設定檔） | 低（只能比對輸入輸出） |
| 跨頁一致性 | 高（同站共用規則） | 低（各頁獨立判斷） |
| 處理特殊版型 | 弱 | 強 |
| 對現有 pipeline 影響 | 小 | 大（`fit_markdown` 來源改變） |

**選擇方案 4 的理由**：專案已有 `exclude_words` 這個設定介面，方案 4 只是把「人工挑」換成「LLM 提議」；方案 1 的最大風險（長頁面靜默遺失）正好打在先前遇過的清單型正文誤刪問題上。方案 5 待方案 4 的殘留類型出來後再決定。

---

## 二、方案 4 的實驗設計

腳本：`scripts/ab_test_llm_exclude_words.py`（不修改 `src/`）。

### 三組共用同一份原始 fit_markdown

| 組別 | exclude_words 來源 |
|---|---|
| A none | 無 |
| B manual | 現有 toml 的人工清單（視為近似標準答案） |
| C llm | LLM 從樣本頁產生 |

輸入取自 `crawl_result.markdown.fit_markdown` 的原始文字（不傳入 `exclude_words`），避免重蹈前一輪「輸入已被自訂清理處理過」的缺陷。

### 指標

| 指標 | 定義 |
|---|---|
| Recall | C 命中的行中，也被 B 命中的比例（以 B 命中行為分母） |
| 多刪行（C − B） | C 刪、B 沒刪的行，需人工判斷是雜訊或正文 |
| 漏掉行（B − C） | B 刪、C 沒刪的行，即殘留雜訊 |
| 詞清單穩定度 | 重跑各次詞清單的交集／聯集 |
| 成本 | `litellm.completion_cost` |

判準（實驗前先訂）：recall ≥ 80%、誤刪正文為 0（由人工確認）、穩定度 ≥ 70%。

### LLM 提議與程式端保護

- 呼叫 `litellm.completion`（預設 `gpt-5.6-luna`），要求輸出 JSON `{"exclude_words": [...]}`，只列「多頁逐字出現的模板／元件文字」。
- 程式端不信任 LLM，逐詞檢查：非空字串、長度 ≥ 3、不重複、必須逐字出現在該次**至少 2 個樣本頁**。
- 送出前用 `token_counter` 估算 prompt，超過 `--max-prompt-tokens`（預設 20 萬）就中止，不做靜默截斷。

### 取樣與合併機制的演進

| 輪次 | 取樣 | 重跑 | C 組詞清單 |
|---|---|---|---|
| 1 | 固定：字典序首頁、中間頁、最長頁，共 3 頁 | 3 | 第 1 次 |
| 2 | 隨機不重複，固定 5 頁 | 3 | 第 1 次 |
| 3 | 隨機不重複，總頁數 10%（至少 2 頁） | 3 | 第 1 次 |
| 4 | 同 3，每次重跑各自重新抽樣 | 5 | 比較合併策略 |

固定取樣的缺點：首頁與中間頁只是排序結果，未必代表不同版型；最長頁的雜訊佔比反而低；且重跑用同一組頁面，穩定度只反映 LLM 自身隨機性。

**合併策略**（輪 4）：`first` 只用第 1 次；`voteK` 取 5 次中至少出現 K 次的詞（vote1＝聯集，vote5＝交集）。

---

## 三、實驗結果

### 輪 1、輪 2（nculab，早期取樣）

| | 輪 1（固定 3 頁） | 輪 2（隨機 5 頁） |
|---|---|---|
| Recall | 100%（282/282） | 100%（282/282） |
| 多刪／漏掉行 | 0 / 0 | 0 / 0 |
| 穩定度 | 100% | 100% |
| 成本 | $0.0078 | $0.0055 |

LLM 提出 6 個英文詞，人工清單有 12 個（多出的 6 個中文詞在這 47 頁命中為 0，爬到的是英文介面）。

### 輪 3（10% 取樣，只用第 1 次）

| | recall | 多刪行 | 漏掉行 | 穩定度 |
|---|---|---|---|---|
| nculab（47 頁，抽 5 頁） | 66.7%（未過） | 0 | 94 | 66.7%（未過） |
| ncucsie（204 頁，抽 21 頁） | 87.0%（過） | 281 | 312 | 7.7%（未過） |

nculab 退步是因為某次抽樣 LLM 只提出 4 個詞，漏了 2 個。固定取樣的結果掩蓋了這種變異。

### 輪 4（5 次重跑，合併策略比較）

nculab：

| 策略 | 詞數 | recall | 多刪行 | 漏掉行 |
|---|---|---|---|---|
| first、vote2、vote3、vote5 | 6 | 100% | 0 | 0 |
| vote1（聯集） | 7 | 100% | 18 | 0 |

ncucsie：

| 策略 | 詞數 | recall | 多刪行 | 漏掉行 | 字元減少率 |
|---|---|---|---|---|---|
| B 人工清單 | 30 | 100% | 0 | 0 | 72.2% |
| first | 18 | 71.8% | 200 | 674 | 34.0% |
| vote1 | 39 | 90.8% | 258 | 221 | 51.8% |
| vote2 | 23 | 87.1% | 207 | 309 | 43.2% |
| vote3 | 18 | 79.0% | 207 | 503 | 36.4% |
| vote5 | 5 | 40.2% | 0 | 1431 | 19.7% |

穩定度：nculab 85.7%，ncucsie 12.8%。成本：nculab 約 $0.007，ncucsie 約 $0.052（5 次呼叫）。

### 多 seed 驗證（vote1 與 vote2 誰更穩定）

nculab：seed 1～4 每組 vote1、vote2 皆為 recall 100%、多刪 0、漏掉 0，兩者無差別。前一輪 vote1 的 `Post date:` 誤刪在這 4 組沒有再出現，是偶發。

ncucsie（seed 1～4 加輪 4 的隨機 seed 共 5 個資料點）：

| 資料點 | vote1 recall | vote1 多刪行 | vote2 recall | vote2 多刪行 |
|---|---|---|---|---|
| seed 1 | 89.2% | 254 | 79.0% | 207 |
| seed 2 | 87.1% | 302 | 87.1% | 207 |
| seed 3 | 89.4% | 228 | 79.0% | 207 |
| seed 4 | 87.1% | 281 | 87.1% | 207 |
| 輪 4 | 90.8% | 258 | 87.1% | 207 |
| **範圍** | 87.1%～90.8% | 228～302 | 79.0%～87.1% | 固定 207 |
| **≥ 80% 次數** | 5/5 | — | 3/5 | — |

- **recall 穩定度**：vote1 較好（5 次全過），vote2 只有 79.0% 或 87.1% 兩種值，2/5 未過。
- **多刪行穩定度**：vote2 較好（固定 207），vote1 在 228～302 之間變動。
- 207 行是各策略共有的多刪底線，依 diff 內容判斷主要是 `教室借用` 連結與分頁按鈕，推測為雜訊；vote1 超出底線的 14～95 行才是額外的誤刪風險。
- 各 seed 下 ncucsie 的詞清單穩定度只有 6.0%～50.0%。

### 多刪行的內容（依 diff 列表的人工判讀，尚未逐行確認）

| 內容 | 行數 | 判讀 |
|---|---|---|
| `教室借用` 連結 | 192 | 導覽，多半為雜訊 |
| Google+ 分享連結 | 74 | 雜訊 |
| `下一頁 >`、`最終頁 »` | 各 7 | 分頁，雜訊 |
| `enter image description here`（圖片 alt） | 50 | 可能是正文圖，誤刪風險 |
| `Post date: …`（nculab） | 18 | 文章日期，正文，誤刪 |
| docx 下載連結 | 1 | 正文，誤刪 |

---

## 四、結論

1. **方案 4 在模板單純的站台可行**：nculab 上 LLM 產生的詞清單與人工清單效果一致（recall 100%、多刪 0），成本不到 $0.01。
2. **不能只用單次結果**：ncucsie 的 `first` 在不同抽樣下 recall 從 87.0% 掉到 71.8%，取決於抽樣運氣。
3. **多次呼叫加合併比單次可靠**：vote1（聯集）在 5 個資料點 recall 都在 87.1% 以上，vote2 有 2/5 掉到 79.0%；交集（vote5）太保守，recall 只剩 40.2%。
4. **選擇 vote1**：經使用者自行判斷後，採用 vote1（聯集）。代價是每次多刪 14～95 行超出底線的內容，其中已觀察到的誤刪詞有 `Post date:`、`enter image description here`。
5. **ncucsie 的詞清單穩定度很差**（6.0%～50.0%），結果高度依賴抽到哪些頁面；首頁專屬區塊（如 `焦點新聞`、`更多`）因只出現在少數頁，樣本常抽不到，兩種策略都會漏。

## 五、vote1 的完整流程（現況：僅存在於實驗腳本，未接進正式流程）

```
爬取全站 → 重複 N 次 [隨機抽樣 → LLM 提議 → 程式端過濾] → 聯集 → 逐頁 clean_markdown → 輸出
```

1. **爬取**（一次）：`WebsiteCrawler` 爬全站，取原始 fit_markdown（不傳 `exclude_words`）。
2. **重複 5 次**（`--repeat`）：
   - 隨機不重複抽 10%（至少 2 頁）；
   - 組 prompt、估算 token，超過上限則中止；
   - 呼叫 LLM 取得 JSON 詞清單；
   - 程式端過濾：長度 ≥ 3、去重、逐字出現於該次至少 2 個樣本頁。
3. **合併**：5 次通過過濾的詞取聯集，依得票數多到少排序。
4. **清理全站**：對每頁 `clean_markdown()`——`exclude_words` 行級過濾 → 移除空錨點與空清單標題 → 空標題提升 → 圖片間距 → mdformat → 圖片後換行修復。
5. **輸出**：各頁清理後 Markdown、`proposed_words_vote1.toml`、每詞得票與命中行數、各次抽樣與詞清單（`samples.json`）、與人工清單的差異、成本。

要正式使用，目前需手動把 `proposed_words_vote1.toml` 的詞貼進 `configs/website_crawler/<site>.toml` 的 `exclude_words`。

## 六、限制與未驗證項目

- 只測了 nculab 與 ncucsie 兩個站台；nculab 每頁模板相同，屬最容易的情況。
- ncucsie 各策略只有 5 個資料點，vote1 與 vote2 的差距大小不宜過度解讀。
- 多刪行是否為誤刪，只是依 diff 列表判讀，尚未逐行核對；B 人工清單本身也不一定完整。
- 未查明 vote2 的 recall 在 79.0% 與 87.1% 之間跳動，是哪些詞造成的。
- 未跑更高取樣比例（20%、30%）的對照。
- 未實測方案 1、2、3、5，比較僅為架構性質推論。
- 只測了單一模型（`gpt-5.6-luna`）。
- 聯集本身沒有額外過濾，單次抽樣中偶發的詞只要通過該次「≥2 個樣本頁」檢查就會進入最終清單。
- **人工審核關卡與全站出現比例門檻**兩項改善方向，已決定本階段不納入討論，留待後續。

## 參考來源

- 專案內：`src/utils/markdown_cleaner.py`、`src/app/engines/website_crawler.py`、`configs/website_crawler/{nculab,ncucsie}.toml`、`scripts/ab_test_llm_exclude_words.py`、`../winnow_webpage_clean/claude/survey.md`
- [Reader-LM: Small Language Models for Cleaning and Converting HTML to Markdown](https://jina.ai/news/reader-lm-small-language-models-for-cleaning-and-converting-html-to-markdown/)
- [Markdown Generation - Crawl4AI Documentation](https://docs.crawl4ai.com/core/markdown-generation/)
- [Jina AI vs. Firecrawl for web-LLM extraction](https://blog.apify.com/jina-ai-vs-firecrawl/)
- [opendatalab/MinerU-HTML（Hugging Face）](https://huggingface.co/opendatalab/MinerU-HTML)
- [Dripper: Token-Efficient Main HTML Extraction（OpenReview）](https://openreview.net/pdf/e2b774a7481c9ccba439fa31dd837e9e32088b81.pdf)
- [Pulpie: Pareto-Optimal Models for Cleaning the Web](https://usefeyn.com/blog/pulpie-pareto-optimal-models-for-cleaning-the-web/)
- [Web2Text: Deep Structured Boilerplate Removal](https://health-nlp.com/files/pubs/ecir18a.pdf)
