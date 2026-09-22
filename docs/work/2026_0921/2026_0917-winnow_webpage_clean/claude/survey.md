# winnow-md 實驗結果調查：為什麼清不掉雜訊、又會誤刪正文

> 承接 `copilot/` 的第一輪實驗（nculab，aggressiveness=0.5，Token 減少率 13.2%、保留率 87.8%），調查結果偏離預期的原因，並評估 winnow 能否取代 `exclude_words`。

## 調查問題

1. nculab 上被排除的 2 頁與 Token Reduction 最高的 5 頁，為什麼會被 winnow 移除？
2. 實驗的輸入與 baseline 是否公平（是否已經被自訂清理邏輯處理過）？
3. winnow 是否處理得了 `exclude_words` 針對的「網站頁面元件文字」？
4. 換成 ncucsie（有真實導覽與頁尾）結論是否改變？

---

## 發現 1：winnow 的判定機制（來源：`.venv/.../winnow/decide.py`、`signals/__init__.py`）

- 每個區塊收到多個訊號，權重以 noisy-or 合併成分數，`分數 >= 門檻` 即移除，門檻 = `0.85 - 0.45 × aggressiveness`（0.5 → 0.625；0.1 → 0.805；0.4 → 0.67）。
- 「核心正文」偵測不到時（頁面沒有長段落），所有「短或連結多」的區塊都會被加上 `PAGE_CHROME`（0.35），且不受 `PROTECTED_CORE` 保護。
- 清單型內容容易命中的訊號：
  - `NAV_LINK_LIST`（0.7）：清單項目 ≥70% 是連結
  - `CITATION_LIST`（0.65）：清單項目含年份加連結、長度 ≥40
  - `LINK_HEAVY`（0.65–0.7）：段落連結密度 ≥0.65 且連結 ≥2
  - `FOOTER_ZONE`、`SECTION_JUNK`：標題被判成頁尾或雜項區，其下內容連帶移除
- 移除清單後，其標題再被 `EMPTY_SECTION` 一併移除。
- 模板記憶（`TEMPLATE_REPEAT`）需要區塊在足夠比例的頁面重複出現。

## 發現 2：nculab 被排除與被大量清除的頁面（重爬後逐區塊檢視）

| 頁面 | Token Reduction | 主要原因 |
|---|---|---|
| `news_校內奬項`（被排除） | 100% | 清單 `NAV_LINK_LIST` 0.7 加 `PAGE_CHROME` 0.35，合併約 0.8；標題 `EMPTY_SECTION` |
| `news_碩論口試`（被排除） | 100% | 清單 `CITATION_LIST` 0.65（略高於門檻 0.625）；標題 `EMPTY_SECTION` |
| `publication_thesisadvised` | 82.5% | 23 個論文段落被 `LINK_HEAVY` 加 `PAGE_CHROME` 判為連結雜訊 |
| `news_校外奬項` | 81.5% | 1,204 字元獎項清單被 `CITATION_LIST` 判為參考文獻 |
| `projects_eventgo` | 75.3% | `Demo`、`Publication`、`Related Technologies` 被 `FOOTER_ZONE`、`SECTION_JUNK` 判為頁尾 |
| `publication_publication-by-year` | 63.1% | 舊年份清單 `CITATION_LIST` 加 `PAGE_CHROME`，約 0.77 |
| `publication` | 62.7% | 同上；部分區塊因 `RESCUED_PROSE` 被救回 |

47 頁中沒有任何區塊因 `TEMPLATE_REPEAT` 被移除。被移除的都是網站的主要內容（論文、獎項、專案連結），屬誤判，而非有效去雜訊。

## 發現 3：輸入已被自訂清理邏輯處理過（原實驗設計缺陷）

`WebsiteCrawler._filter_crawl_results()` 已對 `crawl_result.markdown.fit_markdown` 呼叫過 `clean_markdown()`（`website_crawler.py:181-184`），且 crawl4ai 內部還有 `PruningContentFilter(threshold=0.25)`。所以第一輪實驗：

- baseline = `clean_markdown` 連跑兩次（幾乎等於輸入）
- winnow = 接在 `clean_markdown` 之後的第三層

比較的是「輸入 vs 輸入再加 winnow」，回答不了「winnow 能否取代現有清理」。

## 發現 4：winnow 處理不了 `exclude_words` 針對的元件文字

改用原始 fit_markdown 為共同輸入後，數 `clean_markdown` 會清掉的三類雜訊在輸出中的殘留（nculab）：

| 雜訊類型 | baseline | winnow a=0.1 | winnow a=0.5 |
|---|---|---|---|
| `exclude_words` 命中行（`Google Sites`、`Report abuse`） | 0 | 94 處 / 47 頁 | 92 處 / 46 頁 |
| 空錨點 `[](...#h.xxx)` | 0 | 69 處 / 18 頁 | 68 處 / 17 頁 |
| 空清單標題 `* ##` | 0 | 12 處 / 2 頁 | 12 處 / 2 頁 |

殘留的兩行位於每頁底部，各為 12 字元內的短區塊，模板記憶未觸發；winnow 詞典為 en/de/es/fr，無中文。空錨點與空清單標題是標記殘渣，winnow 只做區塊保留或移除，不改寫內容。調整 aggressiveness 對這些殘留幾乎沒有影響。

## 發現 5：ncucsie 與 nculab 的差異

| | nculab | ncucsie |
|---|---|---|
| 頁數 | 47 | 204 |
| Token Reduction（a=0.1–0.5） | 8–11% | 38–64% |
| winnow 輸出總字元數 vs baseline | 相近或略長 | 1.1–2.1 倍 |
| 主要問題 | 清單型正文被誤刪 | 元件文字大量殘留；a=0.5 時 71 頁被清空 |

- ncucsie 有真實的跨頁重複導覽與側欄，模板記憶有作用，Token Reduction 明顯較高。
- 但 winnow 仍不及 `exclude_words`：`exclude_words` 命中行在 baseline 為 0，winnow a=0.1 殘留 611 處、a=0.5 殘留 232 處（側欄公告連結、頁首 logo、`焦點新聞`、`前一頁`、`第一頁` 等）。
- a=0.5 多出的 71 頁空白，多是 `announcement_page_N_category_*`，其 baseline 只剩約 53 字元。

## 限制與未驗證項目

- 只測了 nculab 與 ncucsie 兩個站台。
- 被誤刪的內容只做了個別頁面抽查，沒有系統性人工比對。
- ncucsie 上 winnow 額外抓到而 `exclude_words` 沒抓到的真正雜訊，未量化。
- 只測 aggressiveness 0.1–0.5，未測 `use_model`、`languages`、`drop_images`。
- `Content Retention`（`len(winnow)/len(baseline)`）在原始輸入下會超過 100%（winnow 保留 baseline 已清掉的標記），不能當品質指標；`Noise Residual` 用字串包含比對，會受 `clean_markdown` 的格式重排影響而失準。

## 結論

- 不適合以 winnow 全面取代 `exclude_words` 與 `clean_markdown`：它清不掉固定頁面元件文字與標記殘渣，且對清單型正文會誤刪。
- 在有真實跨頁模板的站台（ncucsie）winnow 有實際去雜訊效果，若引入，適合作為 `clean_markdown` 之後的可選後處理，aggressiveness 建議 0.1–0.2，並人工檢查被移除的區塊。
