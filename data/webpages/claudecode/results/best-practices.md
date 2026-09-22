Claude Code 是一個代理式編碼環境。與等待回答問題的聊天機器人不同，Claude Code 可以讀取您的檔案、執行命令、進行變更，並在您觀看、重新導向或完全離開時自主地解決問題。 這改變了您的工作方式。您不再自己編寫程式碼並要求 Claude 審查，而是描述您想要的內容，Claude 會找出如何建立它。Claude 會探索、規劃和實施。 但這種自主性仍然伴隨著學習曲線。Claude 在您需要理解的某些限制條件內工作。 本指南涵蓋了在 Anthropic 內部團隊和在各種程式碼庫、語言和環境中使用 Claude Code 的工程師中已證明有效的模式。有關代理式迴圈在幕後如何運作的資訊，請參閱 [Claude Code 如何運作](https://code.claude.com/docs/zh-TW/how-claude-code-works)。

______________________________________________________________________

大多數最佳實踐都基於一個限制條件：Claude 的內容視窗填滿得很快，隨著填滿，效能會下降。 Claude 的內容視窗保存您的整個對話，包括每條訊息、Claude 讀取的每個檔案和每個命令輸出。但是，這可能會很快填滿。單一除錯工作階段或程式碼庫探索可能會產生並消耗數萬個 token。 這很重要，因為隨著內容填滿，LLM 效能會下降。當內容視窗即將滿時，Claude 可能會開始「忘記」早期的指示或犯更多錯誤。內容視窗是最重要的資源，需要管理。若要查看工作階段在實踐中如何填滿，請 [觀看互動式逐步解說](https://code.claude.com/docs/zh-TW/context-window)，了解啟動時載入的內容以及每個檔案讀取的成本。使用 [自訂狀態列](https://code.claude.com/docs/zh-TW/statusline) 持續追蹤內容使用情況，並查看 [減少 token 使用](https://code.claude.com/docs/zh-TW/costs#reduce-token-usage) 以了解減少 token 使用的策略。

______________________________________________________________________

## 給 Claude 一種驗證其工作的方式

給 Claude 一個可以運行的檢查：測試、構建、截圖比較。這是您可以觀看的會話和可以離開的會話之間的區別。 Claude 在工作看起來完成時停止。沒有可以運行的檢查，「看起來完成」是唯一可用的信號，您成為驗證循環：每個錯誤都在等待您注意到它。給 Claude 一些能產生通過或失敗的東西，循環就會自動關閉。Claude 完成工作、運行檢查、讀取結果，並迭代直到檢查通過。 檢查是任何在對話中返回 Claude 可以讀取的信號的東西：測試套件、構建退出代碼、linter、針對固定裝置比較輸出的腳本，或與設計進行比較的[瀏覽器截圖](https://code.claude.com/docs/zh-TW/chrome)。執行 [`/verify`](https://code.claude.com/docs/zh-TW/skills#run-and-verify-your-app) 在 Claude 的檢查通過後自己確認針對執行中應用程式的變更。

| 策略                                     | 之前                                 | 之後                                                                                                                 |
| ---------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| **提供驗證標準**                         | _「實現一個驗證電子郵件地址的函數」_ | _「編寫一個 validateEmail 函數。示例測試用例：user@example.com 為真，invalid 為假，user@.com 為假。實施後運行測試」_ |
| **以視覺方式驗證 UI 更改**               | _「使儀表板看起來更好」_             | _「[粘貼截圖] 實施此設計。對結果進行截圖並與原始設計進行比較。列出差異並修復它們」_                                  |
| **解決根本原因，而不是症狀**             | _「構建失敗」_                       | _「構建失敗，出現此錯誤：[粘貼錯誤]。修復它並驗證構建成功。解決根本原因，不要抑制錯誤」_                             |
| 檢查存在後，決定它對停止的限制有多嚴格： |                                      |                                                                                                                      |

- **在一個提示中** ：要求 Claude 運行檢查並在同一消息中迭代，如上表所示。
- **在整個會話中** ：將檢查設置為 [`/goal` 條件](https://code.claude.com/docs/zh-TW/goal)。單獨的評估器在每次轉換後重新檢查它，Claude 繼續工作直到目標解決。如果 Claude 停滯，Claude Code 最終會停止運行，目標仍然設置 — 請參閱 [/goal 評估如何運作](https://code.claude.com/docs/zh-TW/goal#how-evaluation-works)。
- **作為確定性門** ：[Stop hook](https://code.claude.com/docs/zh-TW/hooks#stop) 將您的檢查作為腳本運行，並阻止轉換結束直到它通過。Claude Code 覆蓋該 hook 並在 8 次連續阻止後結束轉換。
- **由第二意見** ：[驗證子代理](https://code.claude.com/docs/zh-TW/sub-agents)或[動態工作流](https://code.claude.com/docs/zh-TW/workflows)檢查自己的發現，有一個新鮮的模型嘗試反駁結果，所以做工作的代理不是給它評分的那個。

每一步都用設置換取關注。提示版本適用於今天的任何任務。`/goal` 和 Stop hook 版本是讓無人值守運行正確完成而無需您的版本。 讓 Claude 展示證據而不是聲稱成功：測試輸出、它運行的命令及其返回的內容，或結果的截圖。審查證據比自己重新運行驗證要快得多，並且它適用於您沒有觀看的會話。

______________________________________________________________________

## 先探索，然後規劃，然後編碼

將研究和規劃與實施分開，以避免解決錯誤的問題。 讓 Claude 直接跳到編碼可能會產生解決錯誤問題的代碼。使用 [Plan Mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 將探索與執行分開。 推薦的工作流程有四個階段： 1 探索 按 `Shift+Tab` 進入 Plan Mode，直到狀態欄顯示 `⏸ plan mode on`，或使用 `claude --permission-mode plan` 啟動工作階段。Claude 讀取文件並回答問題，不進行任何更改。 claude (plan mode)

```
read /src/auth and understand how we handle sessions and login.
also look at how we manage environment variables for secrets.

```

2 規劃 要求 Claude 創建詳細的實施計劃。 claude (plan mode)

```
I want to add Google OAuth. What files need to change?
What's the session flow? Create a plan.

```

按 `Ctrl+G` 在文本編輯器中打開計劃進行直接編輯，然後 Claude 再繼續。 3 實施 通過批准計劃或按 `Shift+Tab` 切換出 Plan Mode，然後讓 Claude 編碼，根據其計劃進行驗證。 claude

```
implement the OAuth flow from your plan. write tests for the
callback handler, run the test suite and fix any failures.

```

4 提交 要求 Claude 使用描述性消息進行提交並創建 PR。 claude

```
commit with a descriptive message and open a PR

```

Plan Mode 很有用，但也增加了開銷。對於範圍明確且修復很小的任務（如修復拼寫錯誤、添加日誌行或重命名變量），直接要求 Claude 執行。當您對方法不確定、更改修改多個文件或您不熟悉被修改的代碼時，規劃最有用。如果您可以用一句話描述 diff，請跳過計劃。

______________________________________________________________________

## 在提示中提供具體的背景資訊

您的指示越精確，需要的修正就越少。 Claude 可以推斷意圖，但無法讀心術。參考特定檔案、提及限制條件，並指出範例模式。

| 策略                                                                                                                               | 之前                                             | 之後                                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **限定任務範圍。** 指定哪個檔案、什麼情境和測試偏好。                                                                              | _「為 foo.py 新增測試」_                         | _「為 foo.py 編寫測試，涵蓋使用者未登入的邊界情況。避免使用 mock。」_                                                                                                                                                      |
| **指向來源。** 引導 Claude 查看可以回答問題的來源。                                                                                | _「為什麼 ExecutionFactory 有這麼奇怪的 API？」_ | _「查看 ExecutionFactory 的 git 歷史記錄，並總結其 API 是如何演變的」_                                                                                                                                                     |
| **參考現有模式。** 指向您程式碼庫中的模式。                                                                                        | _「新增日曆小工具」_                             | _「查看首頁上現有小工具的實作方式以了解模式。HotDogWidget.php 是一個很好的例子。按照模式實作新的日曆小工具，讓使用者選擇月份並向前/向後分頁以選擇年份。從頭開始構建，除了程式碼庫中已使用的程式庫外，不使用其他程式庫。」_ |
| **描述症狀。** 提供症狀、可能的位置，以及「修復」的樣子。                                                                          | _「修復登入錯誤」_                               | _「使用者報告在工作階段逾時後登入失敗。檢查 src/auth/ 中的驗證流程，特別是權杖重新整理。編寫一個失敗的測試來重現問題，然後修復它」_                                                                                        |
| 模糊的提示在您進行探索且能夠進行過程修正時很有用。像 `「您會改進這個檔案的哪些地方？」` 這樣的提示可以發現您不會想到要詢問的事項。 |                                                  |                                                                                                                                                                                                                            |

### 提供豐富的內容

使用 `@` 參考檔案、貼上螢幕擷取畫面/影像，或直接傳送資料。 您可以透過多種方式向 Claude 提供豐富的資料：

- **使用`@` 參考檔案**，而不是描述程式碼的位置。Claude 會在回應前讀取檔案。
- **直接貼上影像** 。複製/貼上或拖放影像到提示中。
- **提供文件和 API 參考的 URL** 。使用 `/permissions` 將常用網域加入允許清單。
- **透過執行`cat error.log | claude` 來傳送檔案內容，直接傳送資料**。
- **讓 Claude 自行取得所需內容** 。告訴 Claude 使用 Bash 命令、MCP 工具或讀取檔案來自行提取背景資訊。

______________________________________________________________________

## 設定你的環境

幾個設定步驟可以讓 Claude Code 在所有工作階段中發揮更大的效能。如需完整概述擴充功能及何時使用各功能，請參閱[擴充 Claude Code](https://code.claude.com/docs/zh-TW/features-overview)。

### 撰寫有效的 CLAUDE.md

執行 `/init` 以根據你目前的專案結構產生入門 CLAUDE.md 檔案，然後隨著時間推移進行調整。 CLAUDE.md 是一個特殊檔案，Claude 在每次對話開始時都會讀取。包含 Bash 命令、程式碼風格和工作流程規則。這讓 Claude 擁有它無法從程式碼單獨推斷的持久性背景資訊。 CLAUDE.md 檔案沒有必需的格式，但要保持簡短且易於人類閱讀。例如： CLAUDE.md

```
# 程式碼風格
- 使用 ES modules (import/export) 語法，而不是 CommonJS (require)
- 盡可能解構匯入 (例如 import { foo } from 'bar')

# 工作流程
- 完成一系列程式碼變更後，務必進行型別檢查
- 優先執行單一測試，而不是整個測試套件，以提高效能

```

執行 `/context` 以確認 Claude 已載入該檔案。CLAUDE.md 在每個工作階段都會被載入，所以只包含廣泛適用的內容。對於只有在某些時候相關的領域知識或工作流程，請改用[技能](https://code.claude.com/docs/zh-TW/skills)。Claude 會按需載入它們，而不會讓每次對話都變得臃腫。 保持簡潔。對於每一行，問自己： _「移除這一行會導致 Claude 犯錯嗎？」_ 如果不會，就刪除它。臃腫的 CLAUDE.md 檔案會導致 Claude 忽略你的實際指示！

| ✅ 包含                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | ❌ 排除                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Claude 無法猜測的 Bash 命令                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Claude 可以透過閱讀程式碼推斷的任何內容 |
| 與預設值不同的程式碼風格規則                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Claude 已經知道的標準語言慣例           |
| 測試指示和偏好的測試執行器                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 詳細的 API 文件（改為連結到文件）       |
| 儲存庫禮儀（分支命名、PR 慣例）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 經常變更的資訊                          |
| 專案特定的架構決策                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 冗長的解釋或教學                        |
| 開發人員環境怪癖（必需的環境變數）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 檔案逐一描述程式碼庫                    |
| 常見陷阱或非顯而易見的行為                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 自明的做法，如「編寫乾淨的程式碼」      |
| 如果 Claude 儘管有規則反對仍持續做某件事，該檔案可能太長，規則被遺漏了。如果 Claude 詢問你在 CLAUDE.md 中已回答的問題，措辭可能不明確。將 CLAUDE.md 視為程式碼：當事情出錯時檢查它，定期修剪它，並透過觀察 Claude 的行為是否實際改變來測試變更。對於簽入的 CLAUDE.md，執行[`/doctor`](https://code.claude.com/docs/zh-TW/commands#all-commands)，Claude 會建議刪除它可以從程式碼庫衍生的內容。 如果 Claude 持續跳過一項指示，請在該行單獨添加強調，例如「重要」。如果你強調許多行，沒有一行會突出。將 CLAUDE.md 簽入 git，以便你的團隊可以貢獻。該檔案的價值會隨著時間推移而複合增長。 CLAUDE.md 檔案可以使用 `@path/to/import` 語法匯入其他檔案。如需匯入規則和 CLAUDE.md 檔案可以存放的位置，請參閱 [CLAUDE.md 檔案](https://code.claude.com/docs/zh-TW/memory#claude-md-files)。 |                                         |

### 設定權限

若要減少提示而不放棄控制，請使用 `/permissions` 預先核准你信任的工具，並使用 `/sandbox` 讓沙箱命令無需詢問即可執行。當你想自己核准編輯和命令時，切換到手動模式。 在 Pro、Max 和 Team 方案上，自動模式是互動式終端和 VS Code 工作階段的[內建起始權限模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)：一個單獨的分類器模型會檢查大多數操作，而不是你，並且只會阻止看起來有風險的操作，例如範圍提升、未知基礎設施或敵對內容驅動的操作。 在手動模式（其他方案上的內建起始權限模式）中，Claude Code 會在可能修改你的系統的操作前詢問：檔案寫入、Bash 命令、MCP 工具。這很安全但很繁瑣。在第十次核准後，你就是在點擊而不是檢查。兩個工具在手動模式中減少了這些中斷，也適用於自動模式：

- **權限允許清單** ：允許你知道是安全的特定工具，如 `npm run lint` 或 `git commit`
- **沙箱** ：啟用作業系統級隔離，限制檔案系統和網路存取，讓 Claude 在定義的邊界內更自由地工作

深入瞭解[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)、[權限規則](https://code.claude.com/docs/zh-TW/permissions)和[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)。

### 使用 CLI 工具

告訴 Claude Code 在與外部服務互動時使用 CLI 工具，如 `gh`、`aws`、`gcloud` 和 `sentry-cli`。 CLI 工具是與外部服務互動最具背景資訊效率的方式。如果你使用 GitHub，請安裝 `gh` CLI。Claude 知道如何使用它來建立議題、開啟提取請求和閱讀評論。沒有 `gh`，Claude 仍然可以使用 GitHub API，但未經驗證的請求經常會達到速率限制。 Claude 也很擅長學習它還不知道的 CLI 工具。嘗試像 `Use 'foo-cli-tool --help' to learn about foo tool, then use it to solve A, B, C.` 這樣的提示。

### 連接 MCP 伺服器

執行 `claude mcp add` 並提供伺服器名稱和 URL 或命令，以連接外部工具，如 Notion、Figma 或你的資料庫。例如：`claude mcp add --transport http notion https://mcp.notion.com/mcp`。 使用 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)，你可以要求 Claude 從議題追蹤器實現功能、查詢資料庫、分析監控資料、整合來自 Figma 的設計，以及自動化工作流程。

### 設定 hooks

對於必須每次都發生且沒有例外的操作，使用 hooks。 [Hooks](https://code.claude.com/docs/zh-TW/hooks-guide) 在 Claude 工作流程中的特定點自動執行指令碼。與作為建議的 CLAUDE.md 指示不同，hooks 是確定性的，並保證操作會發生。 Claude 可以為你編寫 hooks。嘗試像 _「編寫一個在每次檔案編輯後執行 eslint 的 hook」_ 或 _「編寫一個阻止寫入遷移資料夾的 hook。」_ 這樣的提示。直接編輯 `.claude/settings.json` 以手動設定 hooks，並執行 `/hooks` 以瀏覽已設定的內容。

### 建立技能

在 `.claude/skills/` 中建立 `SKILL.md` 檔案，以提供 Claude 領域知識和可重複使用的工作流程。 [技能](https://code.claude.com/docs/zh-TW/skills)使用特定於你的專案、團隊或領域的資訊擴充 Claude 的知識。Claude 在相關時自動應用它們，或者你可以使用 `/skill-name` 直接呼叫它們。 透過在 `.claude/skills/` 中添加包含 `SKILL.md` 的目錄來建立技能： .claude/skills/api-conventions/SKILL.md

```
---
name: api-conventions
description: REST API design conventions for our services
---
# API 慣例
- 為 URL 路徑使用 kebab-case
- 為 JSON 屬性使用 camelCase
- 始終為清單端點包含分頁
- 在 URL 路徑中版本化 API (/v1/, /v2/)

```

技能也可以定義你直接呼叫的可重複工作流程： .claude/skills/fix-issue/SKILL.md

```
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
分析並修復 GitHub 議題：$ARGUMENTS。

1. 使用 `gh issue view` 取得議題詳細資訊
2. 理解議題中描述的問題
3. 搜尋程式碼庫以尋找相關檔案
4. 實現必要的變更以修復議題
5. 編寫並執行測試以驗證修復
6. 確保程式碼通過 linting 和型別檢查
7. 建立描述性提交訊息
8. 推送並建立 PR

```

執行 `/fix-issue 1234` 以呼叫它。對於具有副作用且你想手動觸發的工作流程，使用 `disable-model-invocation: true`。

### 建立自訂子代理

在 `.claude/agents/` 中定義專門的助手，Claude 可以委派給它們以執行隔離的任務。 [子代理](https://code.claude.com/docs/zh-TW/sub-agents)在自己的背景資訊中執行，具有自己的一組允許工具。它們對於讀取許多檔案或需要專門關注而不會讓主要對話變得混亂的任務很有用。 .claude/agents/security-reviewer.md

```
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
你是一名資深安全工程師。檢查程式碼以查找：
- 注入漏洞 (SQL、XSS、命令注入)
- 驗證和授權缺陷
- 程式碼中的祕密或認證
- 不安全的資料處理

提供特定的行參考和建議的修復。

```

明確告訴 Claude 使用子代理： _「使用子代理檢查此程式碼是否存在安全問題。」_

### 安裝外掛程式

執行 `/plugin` 以瀏覽市場。外掛程式無需設定即可添加技能、工具和整合。 [外掛程式](https://code.claude.com/docs/zh-TW/plugins)將技能、hooks、子代理和 MCP 伺服器從社群和 Anthropic 捆綁到單個可安裝單位中。如果你使用型別語言，請安裝[程式碼智慧外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins#code-intelligence)，以提供 Claude 精確的符號導航和編輯後的自動錯誤偵測。 如需有關在技能、子代理、hooks 和 MCP 之間選擇的指導，請參閱[擴充 Claude Code](https://code.claude.com/docs/zh-TW/features-overview#match-features-to-your-goal)。

______________________________________________________________________

## 有效溝通

詢問 Claude 您會詢問另一位工程師的問題，對於較大的功能，讓 Claude 採訪您並在開始實施前撰寫規格。

### 詢問代碼庫問題

詢問 Claude 您會問資深工程師的問題。 當加入新代碼庫時，使用 Claude Code 進行學習和探索。您可以詢問 Claude 與詢問另一位工程師相同類型的問題：

- 日誌記錄如何工作？
- 我如何建立新的 API 端點？
- `foo.rs` 第 134 行的 `async move { ... }` 做什麼？
- `CustomerOnboardingFlowImpl` 處理哪些邊界情況？
- 為什麼此代碼在第 333 行呼叫 `foo()` 而不是 `bar()`？

以這種方式使用 Claude Code 是一個有效的入職工作流程，改進了入職時間並減少了對其他工程師的負擔。無需特殊提示：直接提出問題。

### 讓 Claude 採訪您

對於較大的功能，讓 Claude 先採訪您。從最小的提示開始，並要求 Claude 使用 `AskUserQuestion` 工具採訪您。 Claude 會詢問您可能還沒有考慮的事情，包括技術實施、UI/UX、邊界情況和權衡。將 `[brief description]` 替換為您的功能，然後再傳送提示。

```
I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs. Don't ask obvious questions, dig into the hard parts I might not have considered.

Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.

```

規格完成後，開始新會話以執行它。新會話具有完全專注於實施的乾淨 context，您有一個書面規格可供參考。 最有用的規格是自包含的：它們命名涉及的檔案和介面、說明什麼超出範圍，並以端到端驗證步驟結束，證明該功能有效。花費時間使規格精確的回報遠大於花費時間觀看實施的回報。

______________________________________________________________________

## 管理您的工作階段

對話是持久且可逆的。善加利用這一點！

### 及早且頻繁地修正方向

一旦發現 Claude 偏離軌道，請立即修正。 最佳結果來自於緊密的回饋迴圈。雖然 Claude 有時能在第一次嘗試時完美解決問題，但快速修正通常能更快產生更好的解決方案。

- **`Esc`**：使用`Esc` 鍵在 Claude 執行中途停止。內容會被保留，因此您可以重新導向。
- **`Esc + Esc`或`/rewind`** ：按兩次 `Esc` 或執行 `/rewind` 以開啟倒帶選單，並復原先前的對話和程式碼狀態，或從選定的訊息進行摘要。
- **`"Undo that"`**：讓 Claude 復原其變更。
- **`/clear`**：在不相關的任務之間重設內容。包含無關內容的長工作階段可能會降低效能。

如果您在一個工作階段中針對同一問題修正 Claude 超過兩次，內容會因失敗的方法而變得混亂。執行 `/clear` 並使用更具體的提示重新開始，該提示應納入您所學到的內容。具有更好提示的乾淨工作階段幾乎總是優於包含累積修正的長工作階段。

### 積極管理內容

在不相關的任務之間執行 `/clear` 以重設內容。 Claude Code 會在您接近內容限制時自動壓縮對話歷史，這會保留重要的程式碼和決策，同時釋放空間。 在長工作階段期間，Claude 的內容視窗可能會填滿無關的對話、檔案內容和命令。這可能會降低效能，有時甚至會分散 Claude 的注意力。

- 在任務之間頻繁使用 `/clear` 以完全重設內容視窗
- 當自動壓縮觸發時，Claude 會摘要最重要的內容，包括程式碼模式、檔案狀態和關鍵決策
- 為了獲得更多控制，執行 `/compact <instructions>`，例如 `/compact Focus on the API changes`
- 若要只壓縮對話的一部分，使用 `Esc + Esc` 或 `/rewind`，選擇訊息檢查點，然後選擇**從此處摘要** 或**摘要至此處** 。第一個選項會壓縮該點之後的訊息，同時保留較早的內容；第二個選項會壓縮較早的訊息，同時保留最近的訊息完整。請參閱[倒帶選單的摘要選項](https://code.claude.com/docs/zh-TW/checkpointing#rewind-and-summarize)。
- 在 CLAUDE.md 中使用 `"When compacting, always preserve the full list of modified files and any test commands"` 之類的指示來自訂壓縮行為，以確保關鍵內容在摘要後倖存
- 對於不需要保留在內容中的問題，使用 [`/btw`](https://code.claude.com/docs/zh-TW/interactive-mode#side-questions-with-%2Fbtw)。答案永遠不會進入對話歷史，因此您可以檢查詳細資訊而不會增加內容。

### 使用子代理進行調查

使用 `"use subagents to investigate X"` 委派研究。它們在單獨的內容中進行探索，保持您的主要對話乾淨以供實施。 由於內容是您的基本限制，請使用子代理將研究保持在內容之外。當 Claude 研究程式碼庫時，它會讀取許多檔案，所有這些都會消耗您的內容。子代理在單獨的內容視窗中執行並報告摘要：

```
Use subagents to investigate how our authentication system handles token
refresh, and whether we have any existing OAuth utilities I should reuse.

```

您也可以在 Claude 實施某些內容後使用子代理進行驗證。請參閱[新增對抗性審查步驟](https://code.claude.com/docs/zh-TW/best-practices#add-an-adversarial-review-step)。

### 使用檢查點倒帶

您發送的每個提示都會建立一個檢查點。您可以將對話、程式碼或兩者復原到任何先前的檢查點。 Claude 會在每次變更前自動快照檔案，因此檢查點可以復原它們。按兩次 `Escape` 或執行 `/rewind` 以開啟倒帶選單。您可以只復原對話、只復原程式碼、復原兩者，或從選定的訊息進行摘要。詳細資訊請參閱[檢查點](https://code.claude.com/docs/zh-TW/checkpointing)。 與其仔細規劃每一步，您可以告訴 Claude 嘗試一些冒險的事情。如果不起作用，倒帶並嘗試不同的方法。檢查點會與對話一起保存，因此您可以關閉終端機、稍後復原工作階段，並仍然可以倒帶。 檢查點只追蹤透過 Claude 的檔案編輯工具所做的變更。透過 Bash 命令或外部程序所做的變更不會被捕獲。這不是 git 的替代品。

### 復原對話

使用 `/rename` 命名工作階段，並將它們視為分支：每個工作流都有自己的持久內容。 Claude Code 在本地保存對話，因此當任務跨越多個工作階段時，您不必重新解釋內容。執行 [`claude --continue`](https://code.claude.com/docs/zh-TW/sessions#resume-a-session) 以從中斷的地方繼續，或執行 `claude --resume` 以從清單中選擇。給工作階段起描述性名稱，例如 `oauth-migration`，以便稍後找到它們。完整的復原、分支和命名控制集合請參閱[管理工作階段](https://code.claude.com/docs/zh-TW/sessions)。

______________________________________________________________________

## 自動化和擴展

一旦您對一個 Claude 有效，通過平行會話、非交互模式和扇出模式將您的輸出乘以倍數。

### 運行非交互模式

在 CI、pre-commit hooks 或腳本中使用 `claude -p "prompt"`。添加 `--output-format stream-json --verbose` 以獲得流式 JSON 輸出。 使用 `claude -p "your prompt"`，您可以非交互地運行 Claude，不需要互動式提示。除非您傳遞 `--no-session-persistence`，否則執行仍會建立可恢復的會話。[非交互模式](https://code.claude.com/docs/zh-TW/headless)是您將 Claude 整合到 CI 管道、pre-commit hooks 或任何自動化工作流中的方式。輸出格式讓您以編程方式解析結果：純文本、JSON 或流式 JSON。

```
# One-off queries
claude -p "Explain what this project does"

# Structured output for scripts
claude -p "List all API endpoints" --output-format json

# Streaming for real-time processing
claude -p "Analyze this log file" --output-format stream-json --verbose

```

第一個命令列印純文本。`json` 格式傳回一個具有 `result` 欄位的單一 JSON 物件。`stream-json` 格式每行列印一個 JSON 物件，從初始化事件開始。

### 運行多個 Claude 會話

並行運行多個 Claude 會話以加快開發、運行隔離的實驗或啟動複雜的工作流。 選擇適合您想要自己進行多少協調的平行方法，並在會話需要相互傳遞發現時添加訊息：

- [Worktrees](https://code.claude.com/docs/zh-TW/worktrees)：在隔離的 git 檢出中運行單獨的 CLI 會話，以便編輯不會衝突
- [跨會話訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)：讓您自己運行的會話相互傳遞發現
- [桌面應用](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)：以視覺方式管理多個本地會話，每個會話都在自己的 worktree 中
- [Claude Code 在網路上](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：在雲端運行會話，預設情況下在 Anthropic 管理的基礎設施上
- [Agent view](https://code.claude.com/docs/zh-TW/agent-view)：研究預覽。執行 `claude agents` 以分派在背景中持續運行的會話，並從一個螢幕監視它們
- [Agent teams](https://code.claude.com/docs/zh-TW/agent-teams)：實驗性且預設停用。多個會話的自動協調，具有共享任務、訊息和團隊領導

除了並行化工作外，多個會話還支持質量聚焦的工作流。新鮮的 context 改進代碼審查，因為 Claude 不會偏向於它剛剛編寫的代碼。 例如，使用 Writer/Reviewer 模式：

| 會話 A（Writer）                                                                 | 會話 B（Reviewer）                                                                                               |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `實施我們 API 端點的速率限制器`                                                  |                                                                                                                  |
|                                                                                  | `審查 @src/middleware/rateLimiter.ts 中的速率限制器實施。查找邊界情況、競態條件和與我們現有中間件模式的一致性。` |
| `這是審查反饋：[會話 B 輸出]。解決這些問題。`                                    |                                                                                                                  |
| 您可以對測試做類似的事情：讓一個 Claude 編寫測試，然後另一個編寫代碼來通過它們。 |                                                                                                                  |

### 跨文件扇出

循環遍歷任務，為每個任務調用 `claude -p`。使用 `--allowedTools` 為批量操作限定權限。 對於大型遷移或分析，您可以在許多平行 Claude 調用中分配工作。在 git 儲存庫中，執行 [`/batch <instruction>`](https://code.claude.com/docs/zh-TW/commands#all-commands) 讓 Claude 將變更分割到 5 到 30 個子代理。每個子代理在自己的 worktree 中工作並開啟拉取請求。要改為從您自己的腳本驅動扇出，請循環遍歷 `claude -p`： 1 生成任務列表 讓 Claude 將需要遷移的文件列表寫入文件，以便下一步中的循環可以讀取它，使用類似 `list all 2,000 Python files that need migrating and save the list to files.txt` 的提示 2 編寫腳本以循環遍歷列表

```
for file in $(cat files.txt); do
  claude -p "Migrate $file from Python 2 to Python 3. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done

```

3 在幾個文件上測試，然後大規模運行 根據前 2-3 個文件出現的問題改進您的提示，然後在完整集合上運行。`--allowedTools` 旗標限制 Claude 可以做什麼，這在您無人值守運行時很重要。 您也可以將 Claude 整合到現有的資料/處理管道中：

```
claude -p "<your prompt>" --output-format json | your_command

```

### 使用 auto mode 自主運行

對於不間斷的執行和背景安全檢查，使用 [auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)。分類器模型在命令運行前審查它們，阻止範圍升級、未知基礎設施和由敵對內容驅動的操作，同時讓常規工作無提示進行。

```
claude --permission-mode auto -p "fix all lint errors"

```

當分類器在使用 `-p` 旗標的非交互運行中重複阻止操作時，Claude Code 不會停止執行。請參閱 [auto mode 何時回退](https://code.claude.com/docs/zh-TW/permission-modes#when-auto-mode-falls-back) 以了解發生的情況以及閾值。

### 添加對抗性審查步驟

在將任務視為完成之前，讓一個子代理在新鮮的 context 中審查差異並報告缺陷。 Claude 無人值守工作的時間越長，在您將工作視為完成之前進行獨立檢查就越重要。在新鮮的 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) context 中運行的審查者只看到差異和您給它的標準，而不是產生變更的推理，因此它按自己的條款評估結果。 對於正確性檢查，執行捆綁的 [`/code-review` skill](https://code.claude.com/docs/zh-TW/commands)，它在新鮮的子代理中審查當前差異以查找錯誤，並將發現返回到會話。要檢查差異是否符合您的計劃，請自己編寫審查提示。命名要檢查的工作、要檢查的計劃以及什麼算作發現：

```
使用子代理根據 PLAN.md 審查速率限制器差異。檢查
每個要求都已實施、列出的邊界情況都有測試，以及
任務範圍之外沒有任何內容更改。報告缺陷，而不是風格偏好。

```

因為審查者作為子代理運行，實施會話直接接收缺陷，可以修復它們並重新審查，而無需您在窗口之間複製發現。 被提示尋找缺陷的審查者通常會報告一些，即使工作是健全的，因為那是它被要求做的。追逐每個發現會導致過度工程：額外的抽象層、防禦性代碼和無法發生的情況的測試。告訴審查者只標記影響正確性或陳述要求的缺陷，並將其餘的視為可選。

______________________________________________________________________

## 避免常見的失敗模式

這些是常見的錯誤。及早識別它們可以節省時間：

- **廚房水槽會話。** 你從一項任務開始，然後問 Claude 一些無關的事情，然後回到第一項任務。上下文充滿了無關的資訊。

> **修正** ：在無關的任務之間使用 `/clear`。

- **一次又一次地更正。** Claude 做錯了什麼，你更正它，它仍然是錯的，你再次更正。上下文被失敗的方法污染了。

> **修正** ：在兩次失敗的更正後，使用 `/clear` 並寫一個更好的初始提示，納入你所學到的內容。

- **過度指定的 CLAUDE.md。** 如果你的 CLAUDE.md 太長，Claude 會忽略其中一半，因為重要的規則在雜訊中丟失了。

> **修正** ：無情地修剪。如果 Claude 已經在沒有指令的情況下正確地做了某事，請刪除它或將其轉換為 hook。

- **信任然後驗證的差距。** Claude 產生了一個看起來合理的實現，但沒有處理邊界情況。

> **修正** ：始終提供驗證（測試、指令碼、螢幕截圖）。如果你無法驗證它，就不要發佈它。

- **無限探索。** 你要求 Claude「調查」某些東西而沒有限定範圍。Claude 讀取數百個檔案，填滿了上下文。

> **修正** ：將調查範圍縮小或使用子代理，以便探索不會消耗你的主要上下文。

______________________________________________________________________

## 培養您的直覺

本指南中的模式不是一成不變的。它們是通常效果很好的起點，但可能不是每種情況的最優選擇。 有時您_應該_讓 context 累積，因為您深入一個複雜的問題，歷史很有價值。有時您應該跳過規劃，讓 Claude 找出答案，因為任務是探索性的。有時模糊的提示正是您想要的，因為您想在限制它之前看到 Claude 如何解釋問題。 注意什麼有效。當 Claude 產生出色的輸出時，注意您做了什麼：提示結構、您提供的 context、您所在的模式。當 Claude 遇到困難時，問為什麼。Context 太嘈雜了嗎？提示太模糊了嗎？任務對於一次通過來說太大了嗎？ 隨著時間的推移，您將培養沒有指南可以捕捉的直覺。您將知道何時具體以及何時開放，何時規劃以及何時探索，何時清除 context 以及何時讓它累積。

## 相關資源

- [Claude Code 如何工作](https://code.claude.com/docs/zh-TW/how-claude-code-works)：代理循環、工具和 context 管理
- [擴展 Claude Code](https://code.claude.com/docs/zh-TW/features-overview)：skills、hooks、MCP、subagents 和 plugins
- [常見工作流](https://code.claude.com/docs/zh-TW/common-workflows)：調試、測試、PR 等的分步配方
- [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)：存儲項目約定和持久 context

是否 助手
