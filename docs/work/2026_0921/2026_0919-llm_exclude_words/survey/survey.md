# 使用 LLM 產生 exclude_words：方案調查與實驗結果

> 調查能否用 LLM 取代「人工看爬取結果、逐一挑出雜訊寫進 `exclude_words`」的工作，並以 nculab、ncucsie 兩個站台實測。最終方案為 **vote1 + 全站行覆蓋率驗證**，在 ncucsie 與人工清單重合 99.3%、多刪 3 行、殘留 19 行。實驗細節見 [exp.md](exp.md)。

## 調查背景

`clean_markdown()`（`src/app/engines/webpage_markdown_cleaner.py`）的雜訊移除核心是 `exclude_words` 行級過濾：一行**包含**清單中任一詞就整行刪除。清單由人工維護於 `configs/website_crawler/<site>.toml`，每個新站台都要重做。

前一輪 winnow-md 實驗（`../2026_0917-winnow_webpage_clean/claude/survey.md`）結論：啟發式工具清不掉固定頁面元件文字，對清單型正文還會誤刪。純頻率掃描同樣不懂語意而誤刪大量內容；LLM 讀全站又成本太高。本次的折衷是：**LLM 只看固定比例的樣本頁提議詞，再用全站頻率驗證這些詞。**

---

## 一、LLM 取得乾淨 Markdown 的方法（依 LLM 介入位置分類）

| # | 方法 | LLM 做什麼 | 代表工具 | 主要優點 | 主要缺點 |
|---|---|---|---|---|---|
| 1 | 逐頁 LLM 過濾 | 每頁全文重新生成乾淨 Markdown | Crawl4AI `LLMContentFilter` | 與現有 crawl4ai 相容 | 每頁花 token；生成式有改寫、截斷、靜默遺失風險 |
| 2 | 專用小模型 HTML→Markdown | 1.5B 級模型直接轉換 | Jina ReaderLM-v2 | 成本低、可本地跑 | 同樣是生成式；長頁面易重複或截斷 |
| 3 | 區塊分類 | 小模型判斷每區塊正文/雜訊 | Dripper、Web2Text、Pulpie | 只刪不改寫，零幻覺 | 需部署模型；清單型頁面是否誤刪待驗證 |
| 4 | 由 LLM 產生規則 | 只看少數樣本頁，輸出 `exclude_words` | （自行實作） | 每站約一次成本；規則確定、可審查 | 規則品質取決於樣本 |
| 5 | LLM 後審 | 只判斷「不確定區塊」 | （自行實作） | 兼顧 recall 與成本 | 需設計篩選條件 |
| 6 | 託管 API | 直接回傳乾淨 Markdown | Firecrawl、Jina Reader | 省工 | 收費、無法客製 |

以上為依搜尋摘要與架構性質整理，未逐頁閱讀原文。

**選擇方案 4**：專案已有 `exclude_words` 介面，方案 4 只是把「人工挑」換成「LLM 提議」，成本與頁數無關、規則可審查；方案 1 的長頁面靜默遺失風險正好打在清單型正文誤刪問題上。方案 5 未實測。

---

## 二、實驗結果摘要

各項實驗的設計、數據與過程見 [exp.md](exp.md)，以下只列結論。除非另有說明，實驗皆在 ncucsie（204 頁）上進行，人工清單 B 為 31 詞。

| 主題 | 結論 | 細節 |
|---|---|---|
| 取樣與合併策略 | 選 vote1（各次聯集）；交集（vote2、vote5）recall 太低。ncucsie 各次詞清單穩定度只有 4.7%～50%，結果高度依賴抽到的頁面 | exp.md 第二節 |
| 全站行覆蓋率驗證 | 命中次數落在低覆蓋行（行覆蓋率 < 5%）的比例 > 0.1 的詞剔除；R≤0.1 為最佳取捨。只能刪詞，補不了詞 | exp.md 第三節 |
| 殘留分析與人工清單 B 審核 | B 不是標準答案：類別標籤移出、URL 片段規則移除、分享類詞新增；兩份 toml 已同步 | exp.md 第四節 |
| Prompt 與保護規則 | 維持現行 prompt（V1／V2 沒有優勢）；最短詞長 3 → 2，由驗證機制取代長度檢查。現行 prompt + 驗證：recall 99.3%、多刪 3 行、殘留 19 行 | exp.md 第五節 |
| 單次大量取樣 vs 重抽再聯集 | 單次抽 10%～50% 的 recall 都在 87%～91%，低於 5×10% 的 97.6%；抽更多頁沒有改善，維持重抽再聯集 | exp.md 第六節 |
| 重抽框架下調整取樣比例 | 維持 10%：5% recall 明顯下降；20% 多花約 1.8 倍成本換約 1 個百分點 recall，優勢不穩；比例抽樣的成本會隨頁數線性增加 | exp.md 第七節 |
| 重抽次數 k | 維持 k=5：k=1→2 收益最大，k=3～5 差別在最差情況（P(recall<95%) 14.5% → 2.7%），k>5 收益遞減 | exp.md 第八節 |
| 重抽是否重疊、互斥抽樣 | 不採用互斥抽樣：不省 token，涵蓋量與品質相關性接近 0（推估約 +0.1 個百分點 recall） | exp.md 第八節（附） |

---

## 三、最佳方案的完整流程

```
爬取全站（原始 fit_markdown，不傳 exclude_words）
 → 重複 5 次：隨機抽 10%（至少 2 頁）→ LLM 提議 → guard_words（長度 ≥ 2、去重、≥ 2 樣本頁）
 → 聯集（vote1）
 → 全站行覆蓋率驗證（低覆蓋比例 > 0.1 的詞剔除）    ← 已進正式流程（`validate_words`）
 → 逐頁 clean_markdown：exclude_words 行級過濾 → 移除空錨點與空清單標題 → 空標題提升
   → 圖片間距 → mdformat → 圖片後換行修復
```

正式流程（`WebsiteCrawler`）已含 vote1 與驗證；人工 `exclude_words` 與 `llm_exclude_words` 開關已移除，一律由 LLM 產生。人工清單保存於 `manual_baseline/` 作為評測基準。

**與人工清單的對照（ncucsie，B 31 詞）**：重合 99.3%、多刪 3 行、殘留 19 行（`焦點新聞` 區塊 10、首頁輪播圖 7、其他 2）；詞數 36 對 31；成本約 $0.05（與頁數幾乎無關）；新站台不需人工挑詞，但各次詞清單穩定度低（可重現性差）。

---

## 四、限制與未驗證項目

- 只在 ncucsie 驗證過完整方案（一組 5 次抽樣）；nculab 沒有用驗證機制重跑。
- **少於約 20 頁的站台驗證實質失效**：`LOW_COVERAGE = 0.05`，單頁獨有行的覆蓋率 = 1/頁數，頁數 ≤ 20 時不會被算成低覆蓋行，所有詞的 low_occ_ratio 皆為 0。
- 門檻 0.1、低覆蓋界線 5%、V1／V2 的比較都只有單一資料點，V1 與現行 prompt 的差異有一部分是隨機性。
- 驗證只能刪詞，補不了詞：首頁專屬內容（`焦點新聞` 區塊、輪播圖）殘留 19 行是全站統計方法難以處理的範圍。
- 「≥2 樣本頁」放行條件改為全站頻率的想法暫緩：會與驗證機制重複使用同一種全站證據，且對 LLM 根本沒提出的詞無幫助。
- 未實測方案 1、2、3、5，更高單次取樣比例的結果見 exp.md 第六節，只測單一模型（`gpt-5.6-luna`）。
- 多刪行的判讀依 diff 列表與人工審核，B 本身的價值判斷（如列表頁公告項目算不算內容）會影響指標。

## 參考來源

- 實驗細節：[exp.md](exp.md)
- 專案內：`src/app/engines/webpage_markdown_cleaner.py`、`src/app/engines/website_crawler.py`、`configs/website_crawler/{nculab,ncucsie}.toml`、`scripts/ab_test_llm_exclude_words.py`、`scripts/sim_llm_exclude_words_repeat.py`、`../2026_0917-winnow_webpage_clean/claude/survey.md`
- [Reader-LM: Small Language Models for Cleaning and Converting HTML to Markdown](https://jina.ai/news/reader-lm-small-language-models-for-cleaning-and-converting-html-to-markdown/)
- [Markdown Generation - Crawl4AI Documentation](https://docs.crawl4ai.com/core/markdown-generation/)
- [Jina AI vs. Firecrawl for web-LLM extraction](https://blog.apify.com/jina-ai-vs-firecrawl/)
- [opendatalab/MinerU-HTML（Hugging Face）](https://huggingface.co/opendatalab/MinerU-HTML)
- [Dripper: Token-Efficient Main HTML Extraction（OpenReview）](https://openreview.net/pdf/e2b774a7481c9ccba439fa31dd837e9e32088b81.pdf)
- [Pulpie: Pareto-Optimal Models for Cleaning the Web](https://usefeyn.com/blog/pulpie-pareto-optimal-models-for-cleaning-the-web/)
- [Web2Text: Deep Structured Boilerplate Removal](https://health-nlp.com/files/pubs/ecir18a.pdf)
