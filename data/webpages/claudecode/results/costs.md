Claude Code 按 API token 消耗量計費。如需訂閱計畫定價（Pro、Max、Team、Enterprise），請參閱 [claude.com/pricing](https://claude.com/pricing)。每位開發人員的成本差異很大，取決於模型選擇、程式碼庫大小和使用模式，例如執行多個執行個體或自動化。 在企業部署中，平均成本約為每位開發人員每個活躍日 13，每位開發人員每月13，每位開發人員每月 13，每位開發人員每月150-250，90% 的使用者成本保持在每個活躍日 $30 以下。若要估計您自己團隊的支出，請從小型試點群組開始，並使用下面的追蹤工具建立基準，然後再進行更廣泛的推出。 本頁涵蓋如何[追蹤您的成本](https://code.claude.com/docs/zh-TW/costs#track-your-costs)、[管理團隊成本](https://code.claude.com/docs/zh-TW/costs#manage-costs-for-your-organization)和[減少 token 使用](https://code.claude.com/docs/zh-TW/costs#reduce-token-usage)。

## 追蹤您的成本

### 使用 `/usage` 命令

`/usage` 中的 Session 區塊顯示 API token 使用情況，適用於 API 使用者。Claude Max 和 Pro 訂閱者的使用情況已包含在其訂閱中，因此工作階段成本數字與計費無關。訂閱者會在同一畫面上看到計畫使用情況列、活動統計資訊和使用情況明細。 `/usage` 頂部的 Session 區塊顯示您目前工作階段的詳細 token 使用統計資訊。Claude Code 根據 token 計數在本地計算美元數字，採用列表價格，除非 [`modelPricing`](https://code.claude.com/docs/zh-TW/settings-reference#modelpricing) 表格生效。管理員在您組織的受管設定中設定一個表格，以便該數字使用您的合約費率，當表格生效時，`Total cost` 行會附帶 `at your organization's configured rates` 的備註。該數字是估計值，因此如需權威計費資訊，請參閱 [Claude Console](https://platform.claude.com/usage) 中的「使用情況」頁面。

```
Total cost:            $0.55
Total duration (API):  6m 20s
Total duration (wall): 6h 33m 10s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
   claude-sonnet-4-6:  1.2k input, 5.3k output, 940.0k cache read, 50.0k cache write ($0.55)

```

當 `/clear` 啟動新工作階段時，這些總計會重設，因此下一個工作階段的總成本從 $0 開始。在 v2.1.211 之前，它們在 `/clear` 期間持續累積，直到 Claude Code 程序的生命週期結束。 對於以 1.1× [資料駐留費率](https://platform.claude.com/docs/en/about-claude/pricing#data-residency-pricing)計費的 Claude API 回應，Claude Code 會將該回應的 token 列表價格乘以 1.1，以計入工作階段成本數字。Claude Code 在[狀態行的成本欄位](https://code.claude.com/docs/zh-TW/statusline#cost-and-duration-tracking)中報告相同的總計，並將其與 [`--max-budget-usd`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 進行比較。在 v2.1.239 之前，Claude Code 沒有對這些回應應用 1.1×，因此工作階段成本數字低於帳單。

#### Prompt cache 統計資訊

在主要對話的第一個 API 回應之後，Claude Code 還會在 Session 區塊中新增 `Prompt cache (main)` 行，總結工作階段的 [prompt cache](https://code.claude.com/docs/zh-TW/prompt-caching) 使用情況：請求計數、從快取提供的輸入 token 份額、快取未命中，以及快取現在是否溫暖。需要 Claude Code v2.1.251 或更新版本。

```
Prompt cache (main):   14 requests · 91% of input tokens from cache · 2 misses (last 6m 10s ago, 310.2k tokens re-cached) · 1 expected rebuild (compaction or tool-result clearing) · warm (1h TTL, last activity 40s ago)

```

行中的未命中、預期重建以及溫暖或冷部分的含義如下：

- **Misses** ：重新處理快取已保存內容的請求，包括最後一次未命中的時間以及這些請求寫回快取的 token 數量。當請求重新處理超過 5% 且至少 2,000 個 token 的內容時，Claude Code 會將請求計為未命中，這些內容本可從快取中讀取。[使快取失效的操作](https://code.claude.com/docs/zh-TW/prompt-caching#actions-that-invalidate-the-cache)列出了常見原因。當 Claude Code 可以識別最後一次未命中的可能原因時，該行也會命名它，例如 `likely cause: tool definitions changed`。可能原因文字需要 Claude Code v2.1.260 或更新版本。
- **Expected rebuilds** ：當 Claude Code 本身剛剛重寫對話時，通過[壓縮](https://code.claude.com/docs/zh-TW/prompt-caching#compacting-the-conversation)或從上下文中清除舊工具結果，它會將相同類型的未命中計為預期重建。此部分僅在至少發生一次預期重建後才出現。
- **Warm or cold** ：快取的前綴是否仍在其[快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)內，以及生效的 TTL。當快取冷時，該行顯示工作階段已閒置多長時間。當沒有回應報告快取 token 時，該行以 `no prompt caching reported by the API` 結尾。

計數來自 API 回應中的快取 token 欄位，因此該行適用於每個提供者和閘道。它僅涵蓋主要對話，不涵蓋子代理。`/clear` 會將其與 Session 區塊的其餘部分一起重設。 狀態行指令碼可以從 [`prompt_cache` 物件](https://code.claude.com/docs/zh-TW/statusline#prompt-cache-fields)讀取相同的數字。

#### 計畫使用情況明細

在 Pro、Max、Team 或 Enterprise 計畫上，`/usage` 還會顯示計入您計畫限制的內容明細：

- **Attribution** ：最近使用情況歸因於 skills、subagents、plugins 和個別 MCP servers，每個都顯示為總數的百分比。MCP server 的份額僅計算消耗其工具結果之一的請求。在 v2.1.222 之前，在一次呼叫 MCP server 後，Claude Code 將每個後續請求歸因於該伺服器，高估了其份額。
- **Behavior flags** ：行為，例如長上下文或快取未命中，當其佔最近使用情況的 10% 或更多時被標記。
- **Loops** ：最近執行的最重的 [`/loop` 或其他排定任務](https://code.claude.com/docs/zh-TW/scheduled-tasks)的每一行，按總 token 排序，其餘的計數。Claude Code 報告每個任務的執行頻率、執行次數、其總 token 和每次執行的 token，以及上次執行的時間。Claude Code 根據任務的提示鍵入一行，因此您停止並重新建立的迴圈保持為一行。需要 Claude Code v2.1.242 或更新版本。

按 `d` 或 `w` 在過去 24 小時和過去 7 天之間切換。這些數字是近似值，根據此機器上的本地工作階段歷史記錄計算，因此不包括來自其他裝置或 claude.ai 的使用情況。 在 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code#check-account-and-usage)中，歸因份額和行為標記會出現在「帳戶與使用情況」對話框中，並提供「日」和「週」切換，不包括「迴圈」行。

#### 檢查您的使用額度支出

`/usage` 還會在[使用額度](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription)開啟時顯示使用額度行。該行顯示的內容取決於您的計畫：

- **Pro 和 Max** ：您當月的支出，根據您設定的每月支出限制進行衡量。當您未設定限制時，該行顯示 `Unlimited`，沒有支出數字。
- **Team 和 Enterprise** ：您當月的支出，根據您的[組織設定](https://code.claude.com/docs/zh-TW/costs#claude-for-teams-and-enterprise)的任何適用限制進行衡量。涵蓋整個組織的限制不會出現在該行中。當您沒有自己的限制時，該行顯示您的支出，旁邊沒有限制。當您關閉使用額度時，`/usage` 不顯示使用額度行。

當您有支出限制時，該行在使用額度開啟後立即出現，並顯示 0%，直到您首次支出使用額度。在 v2.1.236 之前，`/usage` 僅在 Pro 和 Max 計畫上顯示該行，具有支出限制的行在您支出某些內容之前保持隱藏。

#### 當使用情況請求失敗時

當您的計畫限制請求失敗時（通常是因為使用情況端點受到速率限制），`/usage` 會顯示它在過去 60 分鐘內在此機器上載入的最後使用情況列，以及一個 `Showing last-known usage` 備註，說明該資料是多久前取得的。按 `r` 重試；成功重試會用新資料取代最後已知的列。如果沒有過去 60 分鐘內的快照，`/usage` 會報告使用情況端點受到速率限制，並提供相同的重試快捷方式。在 v2.1.208 之前，在尚未載入使用情況的工作階段中受到速率限制的請求始終會顯示錯誤，沒有任何列。

### 分析您的使用情況模式

執行 [`/insights`](https://code.claude.com/docs/zh-TW/commands#all-commands) 以取得關於您如何工作而不是您使用了多少 token 的報告。它分析您在此機器上的最近工作階段，並撰寫涵蓋您所從事工作、摩擦點（例如誤解的請求或有缺陷的程式碼）以及有關如何更有效地使用 Claude Code 的建議的 HTML 報告。單次執行分析最多 200 個它尚未看過的工作階段，並跳過非常短的工作階段。當工作階段被排除時，報告標題會顯示分析的計數，括號中為總計，例如 `200 sessions (412 total)`。 Claude Code 將最新報告寫入 `~/.claude/usage-data/report.html`，並在同一目錄中保存每次執行的時間戳記副本，因此不會覆蓋較早的報告。Claude Code 按照與其餘工作階段資料相同的時間表刪除報告：在啟動時，它會移除早於 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically) 的檔案，預設為 30 天。 您可以在任何計畫和任何提供者上執行 `/insights`。分析通過與您的常規工作階段相同的提供者和帳戶執行，token 計入您的計畫或 API 使用情況。不包括來自其他裝置和 claude.ai 的工作階段。

### 將使用額度新增到您的訂閱

[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)讓您可以在計畫的使用限制之外繼續工作。若要管理它們，請在通過 `/login` 使用您的 claude.ai 訂閱登入後執行 `/usage-credits`；該命令不適用於 API 金鑰驗證。在自助服務 Enterprise 組織、Enterprise 試用版和通過 AWS Marketplace 計費的 Enterprise 組織中，該命令需要 Claude Code v2.1.248 或更新版本；較早的版本會以 [`Unknown command: /usage-credits`](https://code.claude.com/docs/zh-TW/errors#unknown-command) 拒絕它。它開啟的內容取決於您的角色：

| 您的角色                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | `/usage-credits` 的作用                                                                                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pro 或 Max 訂閱者                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 在瀏覽器中開啟 claude.ai 上的 [**Settings > Usage**](https://claude.ai/settings/usage)。在其 **Usage credits** 部分中，您可以開啟或關閉使用額度，並檢查您的額度餘額、本月支出和每月支出限制 |
| 具有計費存取權限的 Team 或 Enterprise 成員                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 在瀏覽器中開啟您的組織的使用情況設定 [**Admin settings > Usage**](https://claude.ai/admin-settings/usage)                                                                                   |
| 沒有計費存取權限的 Team 或 Enterprise 成員                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 要求您確認，然後向您的組織管理員傳送請求。在 v2.1.211 之前，Claude Code 在沒有確認步驟的情況下傳送請求                                                                                      |
| 對於沒有計費存取權限的 Team 和 Enterprise 成員，確認僅出現在互動式工作階段中：在使用 `-p` 旗標的非互動式模式和從[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)中，該命令不傳送請求，並告訴您改為在互動式工作階段中執行它。 如果您在較早的請求等待管理員時再次執行 `/usage-credits`，Claude Code 會告訴您已傳送請求，而不是傳送重複項。在管理員關閉您的請求後，再次執行該命令會傳送新請求。在 v2.1.222 之前，已關閉的請求也會阻止新請求。 在 Pro 和 Max 計畫上，當您在仍有可用使用額度的情況下達到支出限制時，Claude Code 會提示您提高或移除限制，而無需離開 CLI。如果伺服器拒絕變更，請參閱[無法更新您的支出限制](https://code.claude.com/docs/zh-TW/errors#could-not-update-your-spend-limit)。 |                                                                                                                                                                                             |

## 管理組織的成本

您對 Claude Code 的控制方式取決於您的組織如何存取 Claude Code：透過 Claude for Teams 或 Enterprise 方案、Claude Console 或雲端提供者。在 Teams 和 Enterprise 方案上，使用量會從每位成員的座位額度中扣除。在 Console 和雲端提供者上，使用量按 token 計費至您的組織。如果您的組織混合使用登入方法，每位開發人員會根據他們驗證的方法進行計量。 下表將每種設定對應到您查看支出的位置、您限制支出的位置，以及您如何提取每位使用者的數字。在個人 Pro 或 Max 方案上，您沒有組織可管理，因此請追蹤您自己的使用額度支出，包括[快速模式](https://code.claude.com/docs/zh-TW/fast-mode#see-where-fast-mode-spend-appears)，在[將使用額度新增至您的訂閱](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription)下。

| 您的設定                                                                                                                                                                         | 查看支出                                                                                                                   | 限制支出               | 每位使用者報告                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Claude for Teams 或 Enterprise](https://code.claude.com/docs/zh-TW/costs#claude-for-teams-and-enterprise)                                                                       | [組織分析中的支出報告](https://support.claude.com/en/articles/12883420-view-usage-analytics-for-team-and-enterprise-plans) | 管理員設定中的支出限制 | [支出報告 CSV](https://support.claude.com/en/articles/12883420-view-usage-analytics-for-team-and-enterprise-plans)；Enterprise 上的 [Enterprise Analytics API](https://platform.claude.com/docs/en/api/admin/analytics) |
| [Claude Console (API)](https://code.claude.com/docs/zh-TW/costs#claude-console)                                                                                                  | [Console 使用情況頁面](https://platform.claude.com/usage)                                                                  | 工作區支出限制         | [Console 儀表板](https://platform.claude.com/claude-code)、[Claude Code Analytics API](https://platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api)                                                 |
| [Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry](https://code.claude.com/docs/zh-TW/costs#cloud-providers)                                                  | 您的雲端計費主控台                                                                                                         | 您的雲端預算控制       | [OpenTelemetry](https://code.claude.com/docs/zh-TW/monitoring-usage) 或 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway)                                                                                   |
| [OpenTelemetry 匯出](https://code.claude.com/docs/zh-TW/monitoring-usage)適用於每種設定，是唯一能以近乎即時的方式將每位使用者 token 和成本指標串流到您自己的可觀測性堆疊的選項。 |                                                                                                                            |                        |                                                                                                                                                                                                                         |

### 按您的合約費率報告支出

根據預設，Claude Code 會以清單價格計算它向開發人員顯示的每個成本數字，因此如果您的組織支付合約費率，`/usage`、狀態行和 OpenTelemetry 中的數字與您的帳單不符。若要使其相符，請將 [`modelPricing`](https://code.claude.com/docs/zh-TW/settings-reference#modelpricing) 受管設定設為您的費率。該設定會變更 Claude Code 報告的內容，而不是 Anthropic 收費的內容。需要 Claude Code v2.1.242 或更新版本。 1 從您的合約中取得費率 輸入您合約中的每百萬 token 費率。Claude Code 不會從 Claude Console 取得它們，因此在合約變更時更新設定。 2 寫入設定 為清單價格設定 `multiplier` 以獲得固定百分比折扣，在 `overrides` 下列出每個模型的四個每 token 費率，或兩者都做。加價需要 Claude Code v2.1.271 或更新版本。[`modelPricing` 項目](https://code.claude.com/docs/zh-TW/settings-reference#modelpricing)具有形狀和可貼上的範例。 3 透過受管設定部署它 將其作為[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)傳遞：伺服器管理的設定、MDM 原則、`managed-settings.json` 或[原則協助程式](https://code.claude.com/docs/zh-TW/managed-settings#compute-the-policy-with-a-helper-program)。Claude Code 會忽略使用者、專案和本機設定以及 `--settings` 中的金鑰。 若要確認費率已生效，請在已[接收受管設定](https://code.claude.com/docs/zh-TW/managed-settings#read-the-source-in-%2Fstatus)的工作階段中執行 `/usage`：「工作階段」區塊的「總成本」行會帶有註記「按您的組織設定的費率」。這些數字仍然是估計值，而不是發票。`/model` 選擇器中的每百萬 token 價格仍保持清單價格。

### Claude for Teams 和 Enterprise

在 Claude for Teams 和 Enterprise 方案上，每位成員的 Claude Code 使用量會從每座位額度中扣除，該額度在滾動五小時視窗和每週視窗上重設。該額度與 Claude chat 和 Cowork 共享，其大小取決於成員的[座位層級](https://support.claude.com/en/articles/11845131-use-claude-code-with-your-team-or-enterprise-plan)（Standard 或 Premium）。您的控制項位於 claude.ai 管理員主控台中，而不是 Claude Console。

- **查看支出** ：[組織分析中的支出報告](https://support.claude.com/en/articles/12883420-view-usage-analytics-for-team-and-enterprise-plans)顯示每位使用者和每個模型的估計支出，具有 CSV 匯出功能，每日更新。該報告涵蓋使用額度支出，並在啟用使用額度後出現。座位額度內的使用量不以美元計量。
- **查看採用情況** ：[分析儀表板](https://claude.ai/analytics/claude-code)顯示每日活躍使用者、工作階段和貢獻指標，具有貢獻資料的 CSV 匯出。請參閱[使用分析追蹤團隊使用情況](https://code.claude.com/docs/zh-TW/analytics)。
- **限制支出** ：座位額度是預設上限。若要讓成員超過該額度繼續使用，請啟用[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)，並在組織、群組或個別成員層級設定支出限制。
- **提取每位使用者的數字** ：在 Enterprise 方案上，[Enterprise Analytics API](https://platform.claude.com/docs/en/api/admin/analytics) 會傳回跨 Claude 表面（包括 Claude Code）的每位使用者使用量和成本報告。主要擁有者在 [claude.ai/analytics/api-keys](https://claude.ai/analytics/api-keys) 建立具有 `read:analytics` 範圍的金鑰。在 Teams 方案上，匯出[支出報告 CSV](https://support.claude.com/en/articles/12883420-view-usage-analytics-for-team-and-enterprise-plans)，其中列出每位使用者和每個模型的 token 使用量和估計支出。

[Claude Enterprise 消費指南](https://support.claude.com/en/articles/14782391-claude-enterprise-consumption-guide)是管理員的規劃參考。它說明消費在 Claude chat、Claude Code 和 Cowork 之間的差異，並提供每位使用者的美元起點以供預算編制。為編碼座位預算比聊天座位更多：每個 Claude Code 回合都包含檔案內容、工具呼叫和多步驟推理，因此一個除錯工作階段可能會消耗超過一天的聊天。

### Claude Console

API 組織透過[工作區](https://platform.claude.com/docs/en/build-with-claude/workspaces)管理 Claude Code 支出。您可以[設定工作區支出限制](https://platform.claude.com/docs/en/build-with-claude/workspaces#workspace-limits)以限制 Claude Code 總支出，並在 Console 中[檢視成本和使用情況報告](https://platform.claude.com/docs/en/build-with-claude/workspaces#usage-and-cost-tracking)。 當您首次使用 Claude Console 帳戶驗證 Claude Code 時，系統會自動為您建立一個名為「Claude Code」的工作區。此工作區為您的組織中所有 Claude Code 使用情況提供集中式成本追蹤和管理。您無法為此工作區建立 API 金鑰；它專門用於 Claude Code 驗證和使用。對於具有自訂速率限制的組織，此工作區中的 Claude Code 流量計入您的組織整體 API 速率限制。您可以在 Claude Console 的此工作區的「限制」頁面上設定[工作區速率限制](https://platform.claude.com/docs/en/api/rate-limits#setting-lower-limits-for-workspaces)，以限制 Claude Code 的份額並保護其他生產工作負載。 對於每位使用者報告，[Console 儀表板](https://platform.claude.com/claude-code)顯示每位成員的支出和接受的行數，[Claude Code Analytics API](https://platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api) 使用 [Admin API 金鑰](https://platform.claude.com/settings/admin-keys)以程式設計方式傳回相同的每日每位使用者指標。請參閱 [API 客戶的分析](https://code.claude.com/docs/zh-TW/analytics#access-analytics-for-api-customers)。

#### 速率限制建議

為團隊設定 Claude Code 時，請根據您的組織規模考慮這些每位使用者的 Token Per Minute (TPM) 和 Request Per Minute (RPM) 建議：

| 團隊規模                                                                                                                                                                                                                                                                                                                                            | 每位使用者 TPM | 每位使用者 RPM |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------- |
| 1-5 位使用者                                                                                                                                                                                                                                                                                                                                        | 200k-300k      | 5-7            |
| 5-20 位使用者                                                                                                                                                                                                                                                                                                                                       | 100k-150k      | 2.5-3.5        |
| 20-50 位使用者                                                                                                                                                                                                                                                                                                                                      | 50k-75k        | 1.25-1.75      |
| 50-100 位使用者                                                                                                                                                                                                                                                                                                                                     | 25k-35k        | 0.62-0.87      |
| 100-500 位使用者                                                                                                                                                                                                                                                                                                                                    | 15k-20k        | 0.37-0.47      |
| 500+ 位使用者                                                                                                                                                                                                                                                                                                                                       | 10k-15k        | 0.25-0.35      |
| 例如，如果您有 200 位使用者，您可能會為每位使用者請求 20k TPM，或總共 400 萬 TPM (200\*20,000 = 400 萬)。 隨著團隊規模增長，每位使用者的 TPM 會減少，因為在較大的組織中，傾向於較少的使用者同時使用 Claude Code。這些速率限制適用於組織層級，而不是每個個別使用者，這意味著當其他人未主動使用該服務時，個別使用者可以暫時消耗超過其計算份額的資源。 |                |                |
| 如果您預期會出現異常高的並行使用情況（例如與大型群組進行的即時培訓課程），您可能需要更高的每位使用者 TPM 配置。                                                                                                                                                                                                                                     |                |                |

### 雲端提供者

在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上，Claude Code 按 token 計費至您的雲端帳戶，支出控制項位於您的雲端提供者的計費主控台中。Claude Code 不會從您的雲端傳送指標回 Anthropic，因此[分析儀表板](https://code.claude.com/docs/zh-TW/analytics)和 Claude Code Analytics API 不涵蓋此使用情況。 對於每位使用者成本歸因，您有三個選項：

- **OpenTelemetry** ：[匯出指標](https://code.claude.com/docs/zh-TW/monitoring-usage)從每位開發人員的機器到您自己的可觀測性堆疊。無論提供者為何，這都會為您提供每位使用者的 token 計數、成本和工具活動。
- **Claude apps gateway** ：自託管的 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 提供每位使用者的使用情況歸因、包含 token 計數的 OTLP 指標，以及這些提供者上的[每位使用者支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)。
- **LLM gateway** ：透過追蹤每個金鑰支出的代理路由所有 Claude Code 流量。幾家大型企業報告使用 [LiteLLM](https://code.claude.com/docs/zh-TW/llm-gateway)，一個開源工具，可[按金鑰追蹤支出](https://docs.litellm.ai/docs/proxy/virtual_keys#tracking-spend)。此專案與 Anthropic 無關，尚未進行安全審計。

### 當開發人員詢問限制時

開發人員通常會向其管理員提出限制問題，因此了解他們達到的上限會很有幫助。這些情況意味著不同的事情：

- **「您已達到工作階段限制」或「您已達到每週限制」** ：訂閱方案上基於座位的使用視窗，在所有模型中共享，因此開發人員無法透過使用 `/model` 切換模型來恢復存取權限。該訊息顯示視窗何時重設。在模型特定的「您已達到 Opus 限制」或「您已達到 Sonnet 限制」訊息之後，使用 `/model` 切換到該系列外的模型確實會讓開發人員繼續工作。請參閱[使用限制錯誤](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-session-limit)。開發人員在此期間可以做什麼：
  - 執行 `/usage-credits` 以請求超過額度的使用量，如果您已啟用[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)。
  - 在 Claude Code v2.1.234 或更新版本上，[在重設後自動等待並繼續中斷的任務](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)；該部分列出 Claude Code 何時自行開始等待以及開發人員何時從 `/rate-limit-options` 選擇它。若要控制您的機隊 Claude Code 是否自行開始該等待，請在[受管設定](https://code.claude.com/docs/zh-TW/settings#settings-precedence)中設定 [`autoContinueAtUsageLimit`](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit)。
- **「您已達到個人支出限制」、「組織的每月支出限制」或「團隊的共享預算」** ：開發人員的請求將被計費至使用額度，而這些額度已達到您設定的支出限制。若要讓開發人員繼續，請前往[**管理員設定 > 使用**](https://claude.ai/admin-settings/usage)並增加訊息命名的限制。當訊息也命名計畫重設時間時，開發人員可以改為等待直到那時。請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-monthly-spend-limit)以了解每個變體。
- **來自[Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 的支出限制訊息**：開發人員超過了您在自託管閘道上設定的支出上限，閘道會阻止他們的請求，直到期間重設或您提高上限。請參閱[閘道支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)以了解上限、重設時間表和開發人員看到的訊息。
- **上下文或自動壓縮警告** ：不是使用限制。對話已接近工作階段的[自動壓縮視窗](https://code.claude.com/docs/zh-TW/model-config#set-the-auto-compact-window)，Claude Code 會總結較舊的歷史記錄以釋放空間的閾值。將開發人員指向[減少 token 使用量](https://code.claude.com/docs/zh-TW/costs#reduce-token-usage)。
- **API 或雲端提供者方案上的意外高支出** ：通常可追溯到從未清除的長工作階段或留作預設模型的 Opus。分享的最高影響習慣是在不相關的任務之間清除和將模型與工作相匹配，兩者都涵蓋在[減少 token 使用量](https://code.claude.com/docs/zh-TW/costs#reduce-token-usage)中。

### Agent 團隊 token 成本

[Agent 團隊](https://code.claude.com/docs/zh-TW/agent-teams)會產生多個 Claude Code 執行個體，每個都有自己的上下文視窗。Token 使用量會隨著活躍隊友數量和每個隊友執行時間的長短而擴展。 為了保持 agent 團隊成本可控：

- 為隊友使用 Sonnet。它為協調任務平衡了功能和成本。
- 保持團隊規模小。每位隊友執行自己的上下文視窗，因此 token 使用量大致與團隊規模成正比。
- 保持產生提示的焦點。隊友會自動載入 CLAUDE.md、MCP 伺服器和 skills，但產生提示中的所有內容都會從一開始就新增到其上下文中。
- 工作完成時關閉隊友。每個活躍隊友會繼續消耗 token，直到它退出或工作階段結束。
- Agent 團隊預設為停用。在您的[settings.json](https://code.claude.com/docs/zh-TW/settings)或環境中設定 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 以啟用它們。請參閱[啟用 agent 團隊](https://code.claude.com/docs/zh-TW/agent-teams#enable-agent-teams)。

## 減少 token 使用

Token 成本隨上下文大小而擴展：Claude 處理的上下文越多，您使用的 token 就越多。Claude Code 透過 [prompt caching](https://code.claude.com/docs/zh-TW/prompt-caching)（減少重複內容（如系統提示）的成本）和 auto-compact（在接近上下文限制時總結對話歷史記錄）自動優化成本。 以下策略可幫助您保持上下文較小並降低每條訊息的成本。

### 主動管理上下文

使用 `/usage` 檢查您目前的 token 使用情況，或[設定您的狀態行](https://code.claude.com/docs/zh-TW/statusline#context-window-usage)以持續顯示它。

- **在任務之間清除** ：切換到不相關的工作時，使用 `/clear` 重新開始。過時的上下文會在後續的每條訊息上浪費 token。在清除之前使用 `/rename` 以便稍後輕鬆找到工作階段，然後使用 `/resume` 返回到它。
- **新增自訂壓縮指示** ：`/compact Focus on code samples and API usage` 告訴 Claude 在總結期間要保留什麼。在新的工作階段中，`/compact` 會列印 `Not enough messages to compact.`，因為還沒有對話歷史記錄可以總結。

您也可以在專案根目錄的 CLAUDE.md 檔案中自訂壓縮行為：

```
# Compact instructions

When you are using compact, please focus on test output and code changes

```

### 選擇正確的模型

Sonnet 能很好地處理大多數編碼任務，成本低於 Opus。為複雜的架構決策或多步驟推理保留 Opus。使用 `/model` 在工作階段中途切換模型，或在 `/config` 中設定預設值。對於簡單的 subagent 任務，在您的 [subagent 設定](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)中指定 `model: haiku`。

### 減少 MCP 伺服器開銷

MCP 工具定義[預設為延遲](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search)，因此只有工具名稱和伺服器指示進入上下文，直到 Claude 使用特定工具。執行 `/context` 以查看消耗空間的內容。

- **在可用時偏好 CLI 工具** ：`gh`、`aws`、`gcloud` 和 `sentry-cli` 等工具比 MCP 伺服器更具上下文效率，因為它們不會新增任何每個工具的列表。Claude 可以直接執行 CLI 命令。
- **停用未使用的伺服器** ：執行 `/mcp` 以查看已設定的伺服器，並停用任何您未主動使用的伺服器。

### 為型別化語言安裝程式碼智慧外掛

[程式碼智慧外掛](https://code.claude.com/docs/zh-TW/discover-plugins#code-intelligence)為 Claude 提供精確的符號導航，而不是基於文字的搜尋，在探索不熟悉的程式碼時減少不必要的檔案讀取。單一「前往定義」呼叫取代了可能需要的 grep 後跟讀取多個候選檔案。已安裝的語言伺服器也會在編輯後自動報告型別錯誤，因此 Claude 無需執行編譯器即可捕捉錯誤。

### 將處理卸載到 hooks 和 skills

自訂 [hooks](https://code.claude.com/docs/zh-TW/hooks)可以在 Claude 看到資料之前對其進行預處理。Claude 不是讀取 10,000 行日誌檔案來尋找錯誤，hook 可以 grep `ERROR` 並僅返回匹配的行，將上下文從數萬個 token 減少到數百個。 [skill](https://code.claude.com/docs/zh-TW/skills)可以為 Claude 提供領域知識，因此它不必進行探索。例如，「codebase-overview」skill 可以描述您的專案架構、關鍵目錄和命名慣例。當 Claude 呼叫該 skill 時，它會立即獲得此上下文，而不是花費 token 讀取多個檔案來理解結構。 例如，此 PreToolUse hook 篩選測試輸出以僅顯示失敗：

- settings.json
- filter-test-output.sh

將此新增到您的 [settings.json](https://code.claude.com/docs/zh-TW/settings#where-settings-live) 以在每個 Bash 命令之前執行 hook：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/filter-test-output.sh"
          }
        ]
      }
    ]
  }
}

```

hook 呼叫此指令碼。建立資料夾，使用 `mkdir -p ~/.claude/hooks`，將下面的指令碼儲存為 `~/.claude/hooks/filter-test-output.sh`，並使用 `chmod +x ~/.claude/hooks/filter-test-output.sh` 使其可執行。它檢查命令是否為測試執行器並修改它以僅顯示失敗：

```
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')

# If running tests, filter to show only failures
if [[ "$cmd" =~ ^(npm test|pytest|go test) ]]; then
  filtered_cmd="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:)' | head -100"
  echo "$input" | jq --arg filtered "$filtered_cmd" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "allow", updatedInput: (.tool_input + {command: $filtered})}}'
else
  echo "{}"
fi

```

若要驗證設定，執行 `/hooks` 並檢查 hook 是否出現在 PreToolUse 下。您也可以使用 `claude --debug-file ./claude-debug.txt` 啟動 Claude Code，並要求 Claude 執行 `npm test`。當 hook 重寫命令時，該日誌檔案包含列出 `command` 和其他 Bash 輸入欄位的 `modified tool input keys` 行。

### 將指示從 CLAUDE.md 移至 skills

您的 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory) 檔案在工作階段開始時載入到上下文中。如果它包含特定工作流程的詳細指示（例如 PR 審查或資料庫遷移），即使您在進行不相關的工作時，這些 token 也會存在。[Skills](https://code.claude.com/docs/zh-TW/skills)僅在呼叫時按需載入，因此將專門指示移至 skills 可以保持您的基本上下文較小。目標是透過僅包含必要內容來將 CLAUDE.md 保持在 200 行以下。

### 調整延伸思考

延伸思考預設為啟用，因為它可以顯著改善複雜規劃和推理任務的效能。思考 token 會作為輸出 token 計費，預設預算可能是每個請求數萬個 token，取決於模型。 對於不需要深度推理的較簡單任務，您可以透過在 `/effort` 中降低[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)或在 `/model` 中降低、在 `/config` 中停用思考，或在具有[固定思考預算](https://code.claude.com/docs/zh-TW/model-config#adaptive-reasoning-and-fixed-thinking-budgets)的模型上，透過設定 `MAX_THINKING_TOKENS` [環境變數](https://code.claude.com/docs/zh-TW/env-vars)（例如 `MAX_THINKING_TOKENS=8000`）來降低預算，以降低成本。自適應推理模型會忽略非零預算，因此請改用努力等級。您無法在 Fable 模型上關閉思考，它們始終使用延伸思考。

### 將詳細操作委派給 subagents

執行測試、擷取文件或處理日誌檔案可能會消耗大量上下文。將這些委派給 [subagents](https://code.claude.com/docs/zh-TW/sub-agents#isolate-high-volume-operations)，以便詳細輸出保留在 subagent 的上下文中，而只有摘要返回到您的主要對話。

### 管理 agent 團隊成本

當隊友在 plan mode 中執行時，Agent 團隊使用的 token 大約是標準工作階段的 7 倍，因為每位隊友維護自己的上下文視窗並作為單獨的 Claude 執行個體執行。保持團隊任務小且自成一體，以限制每位隊友的 token 使用。有關詳細資訊，請參閱 [agent 團隊](https://code.claude.com/docs/zh-TW/agent-teams)。

### 撰寫具體提示

模糊的請求（例如「改進此程式碼庫」）會觸發廣泛掃描。具體的請求（例如「在 auth.ts 中的登入函式中新增輸入驗證」）讓 Claude 能夠以最少的檔案讀取高效地工作。

### 有效處理複雜任務

對於較長或更複雜的工作，這些習慣有助於避免因走錯方向而浪費的 token：

- **對複雜任務使用 plan mode** ：按 Shift+Tab 進入 [plan mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode)，然後再進行實施。Claude 探索程式碼庫並提出一個方法供您批准，防止當初始方向錯誤時進行昂貴的返工。
- **及早糾正方向** ：如果 Claude 開始朝著錯誤的方向前進，按 Escape 立即停止。使用 `/rewind` 或雙擊 Escape 將對話和程式碼恢復到先前的 checkpoint。
- **提供驗證目標** ：在您的提示中包含測試案例、貼上螢幕截圖或定義預期輸出。當 Claude 可以驗證自己的工作時，它會在您需要請求修復之前捕捉問題。
- **增量測試** ：寫一個檔案、測試它，然後繼續。這會在問題便宜時及早捕捉問題。

## 背景 token 使用

Claude Code 即使在閒置時也會為某些背景功能使用 token：

- **對話總結** ：為 `claude --resume` 功能總結先前對話的背景工作
- **命令處理** ：某些命令（例如 `/usage`）可能會產生檢查狀態的請求

這些背景程序即使沒有主動互動也會消耗少量 token（通常每個工作階段不到 $0.04）。

## 為什麼長時間工作階段中的使用量會增加

已開啟數小時的工作階段可能會使用遠超過您的活動所暗示的計畫限額，通常是由於以下原因之一：

- **長上下文** ：Claude Code 在每次請求時都會傳送您與其的完整對話，每當 Claude 使用工具時，它會傳送另一個請求，其中包含該批工具結果。使用 [prompt caching](https://code.claude.com/docs/zh-TW/prompt-caching)，Claude Code 會以 [快取代幣費率](https://platform.claude.com/docs/en/about-claude/pricing) 重新讀取該歷史記錄，因此在已開啟一整天的工作階段中提出的一行問題仍然會為整個對話消耗使用量。請參閱 [主動管理上下文](https://code.claude.com/docs/zh-TW/costs#manage-context-proactively) 以了解保持上下文較小的方法
- **快取未命中** ：在超過 [快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime) 的中斷後的第一條訊息會未命中快取並重新處理您的完整上下文。在訂閱上生命週期為一小時，一旦您開始使用 [使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)，生命週期會降至五分鐘；在 API 金鑰或雲端提供者上，預設為五分鐘。若要在使用使用額度時保持一小時的生命週期，[自行選擇 TTL](https://code.claude.com/docs/zh-TW/prompt-caching#choose-the-ttl-yourself)。在 Pro 和 Max 計畫上，當您在長時間中斷後恢復大型工作階段時，Claude Code [提供從摘要恢復](https://code.claude.com/docs/zh-TW/sessions#resume-from-a-summary) 的選項，以便稍後的請求不會攜帶完整歷史記錄
- **排程工作** ：[排程工作](https://code.claude.com/docs/zh-TW/scheduled-tasks) 在其間隔上執行，即使工作階段處於閒置狀態，每次都傳送您的完整上下文
- **跨工作階段訊息** ：Claude Code 在此工作階段處於閒置時，將 [來自您另一個工作階段的訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging) 作為新回合傳送，每次都傳送您的完整上下文。若要保留入站訊息而不是傳送它們，請將 [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound) 設定為 `hold`
- **目標檢查** ：當背景工作保持活躍 [目標](https://code.claude.com/docs/zh-TW/goal) 等待時，Claude Code [要求 Claude 檢查該工作](https://code.claude.com/docs/zh-TW/goal#background-work-defers-evaluation)，即使工作階段處於閒置狀態，啟動傳送您完整上下文的新回合。Claude Code 在您的提示之間每個目標最多啟動三個閒置檢查。在 v2.1.246 之前，閒置檢查是無上限的。若要關閉檢查，請將 [`CLAUDE_CODE_GOAL_CHECKIN_MINUTES`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `0`。閒置檢查需要 Claude Code v2.1.236 或更新版本
- **代理隊友** ：每個活躍 [隊友](https://code.claude.com/docs/zh-TW/costs#agent-team-token-costs) 會持續消耗代幣，直到它退出
- **壓縮** ：`/compact` 讀取它摘要的對話，因此 [壓縮大型上下文](https://code.claude.com/docs/zh-TW/prompt-caching#compacting-the-conversation) 本身是一個大型請求。當您想要全新開始而不是連續性時，`/clear` 不需要任何成本

在 Pro、Max、Team 或 Enterprise 計畫上，`/usage` 細目會標記佔您最近使用量 10% 或以上的行為，例如長上下文或快取未命中，每個都附帶減少它的提示。

## 了解 Claude Code 行為的變更

Claude Code 會定期接收更新，這些更新可能會改變功能的運作方式，包括成本報告。執行 `claude --version` 以檢查您目前的版本。 如有關於您特定帳戶的計費問題，請透過應用程式內訊息聯絡 Anthropic 支援：

- **訂閱方案** （Pro、Max、Team、Enterprise）：登入 [claude.ai](https://claude.ai)，點擊左下角的您的首字母縮寫，然後選擇**取得協助**
- **Console（API）計費** ：登入 [platform.claude.com](https://platform.claude.com)，點擊您的首字母縮寫，然後選擇**取得協助**

請參閱[如何取得支援](https://support.claude.com/en/articles/9015913-how-to-get-support)以了解完整流程，包括每個方案上哪些人可以聯絡人工代理。 是否 助手
