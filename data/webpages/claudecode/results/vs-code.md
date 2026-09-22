![VS Code 編輯器，右側開啟 Claude Code 擴充功能面板，顯示與 Claude 的對話](https://mintcdn.com/claude-code/-YhHHmtSxwr7W8gy/images/vs-code-extension-interface.jpg?fit=max&auto=format&n=-YhHHmtSxwr7W8gy&q=85&s=300652d5678c63905e6b0ea9e50835f8)
> # Image-1
>
> **圖片摘要：**
> Claude-Cafe 專案的 VS Code 介面顯示 App.css、LocalizationUtil 測試程式與 Unit Tests 面板
>
> **主要元素：**
> 1. 實體: Claude-Cafe, App.css, localizationUtils.ts, Unit Tests, VS Code
> 2. OCR文字:
> EXPLORER
> CLAUDE-CAFE
> .claude
> agents
> qa.md
> quebec-french-complian...
> visual-testing-playwright...
> checkpoints
> settings.local.json
> dist
> node_modules
> playwright-traces
> public
> src
> assets
> components
> data
> pages
> types
> utils
> App.css
> App.tsx
> src > App.css > :root
> :root {
> --primary-green: #667a60;
> --dark-bg: #2b2b2a;
> --light-text: #d4d1cd;
> --button-pink: #c98fa5;
> --font-times: 'Tiempos', serif;
> --font-styrene: 'Styrene', sans-serif;
> }
> * {
> box-sizing: border-box;
> margin: 0;
> padding: 0;
> }
> body {
> font-family: var(--font-styrene);
> color: var(--dark-bg);
> margin: 0;
> background-color: var(--light-text);
> min-height: 100vh;
> }
> /* Menu Page Styles */
> .menu-page, .confirmation-page {
> Unit Tests
> can you add tests for this file?
> localizationUtils.ts
> Sure, let me take a look at the file:
> Read localizationUtils.ts
> Read 256 lines
> Write (src/test/localization.ts)
> import { formatDate, translateKey, getCurrencyS
> describe('LocalizationUtil', () => {
> describe('formatDate', () => {
> it('should format date correctly', () => {
> Pondering...
> Queue another message...
> Ask before editing
> localizationUtils.ts
> 3. 主題標籤: Claude-Cafe, App.css, 單元測試, LocalizationUtil, CSS
>
> **頁面關聯：**
> Claude-Cafe 專案程式碼與 localizationUtils.ts 單元測試頁面
VS Code 擴充功能為 Claude Code 提供了原生圖形介面，直接整合到您的 IDE 中。這是在 VS Code 中使用 Claude Code 的推薦方式。 使用此擴充功能，您可以在接受 Claude 的計畫之前進行審查和編輯，在進行編輯時自動接受，從您的選擇中 @-提及具有特定行範圍的檔案，存取對話歷史記錄，以及在單獨的標籤或視窗中開啟多個對話。

## 先決條件

安裝前，請確保您擁有：

- VS Code 1.94.0 或更高版本
- Anthropic 帳戶：任何付費 Claude 訂閱（Pro、Max、Team 或 Enterprise）或 Claude Console 帳戶都可以使用，不需要 API 金鑰。首次開啟擴充功能時，您將[使用此帳戶登入](https://code.claude.com/docs/zh-TW/authentication#log-in-to-claude-code)。如果您透過第三方提供者（如 Amazon Bedrock 或 Google Cloud 的 Agent Platform）存取 Claude，請參閱[使用第三方提供者](https://code.claude.com/docs/zh-TW/vs-code#use-third-party-providers)以取得設定說明。

此擴充功能包含其自有的 CLI（命令列介面）副本供聊天面板使用。若要在 VS Code 的整合終端機中執行 `claude`，您還需要[獨立 CLI 安裝](https://code.claude.com/docs/zh-TW/setup)。詳細資訊請參閱 [VS Code 擴充功能與 Claude Code CLI](https://code.claude.com/docs/zh-TW/vs-code#vs-code-extension-vs-claude-code-cli)。

## 安裝擴充功能

點擊您的 IDE 的連結以直接安裝：

- [為 VS Code 安裝](vscode:extension/anthropic.claude-code)
- [為 Cursor 安裝](cursor:extension/anthropic.claude-code)

或在 VS Code 中，按 `Cmd+Shift+X`（Mac）或 `Ctrl+Shift+X`（Windows/Linux）開啟擴充功能檢視，搜尋「Claude Code」，然後點擊**安裝** 。 擴充功能也會安裝在其他 VS Code 分支中，例如 Devin Desktop 或 Kiro。在編輯器的擴充功能檢視中搜尋「Claude Code」，或從 [Open VSX registry](https://open-vsx.org/extension/Anthropic/claude-code) 安裝。如果您的編輯器無法安裝擴充功能，請[安裝 CLI](https://code.claude.com/docs/zh-TW/quickstart) 並在其整合終端中執行 `claude`。CLI 可在任何終端中運作。 如果安裝後擴充功能未出現，請重新啟動 VS Code 或從命令面板執行「Developer: Reload Window」。

## 開始使用

安裝後，您可以透過 VS Code 介面開始使用 Claude Code： 1 開啟 Claude Code 面板 在整個 VS Code 中，Spark 圖示表示 Claude Code：![Spark icon](https://mintcdn.com/claude-code/c5r9_6tjPMzFdDDT/images/vs-code-spark-icon.svg?fit=max&auto=format&n=c5r9_6tjPMzFdDDT&q=85&s=3ca45e00deadec8c8f4b4f807da94505)
> # Image-2
>
> **圖片摘要：**
> utils.py 顯示 calculate_average 函式，檢查空值後累加 numbers 並計算平均值。
>
> **主要元素：**
> 1. 實體: Python, 平均值計算函式, numbers 參數, total 累加變數, 程式編輯器
> 2. OCR文字:
> utils.py
> 1    def calculate_average(numbers):
> 2        if not numbers:
> 3            return 0
> 4    total = 0
> 5    for num in numbers:
> 6        total += num
> 7    return total / len(numbers)
> 8
> 3. 主題標籤: Python, 函式, 平均值計算, 迴圈, 程式碼
>
> **頁面關聯：**
> utils.py 程式碼頁面，錨點 calculate_average
開啟 Claude 最快的方式是點擊**編輯器工具列** （編輯器右上角）中的 Spark 圖示。只有當您開啟檔案時，該圖示才會出現。![VS Code 編輯器顯示編輯器工具列中的 Spark 圖示](https://mintcdn.com/claude-code/mfM-EyoZGnQv8JTc/images/vs-code-editor-icon.png?fit=max&auto=format&n=mfM-EyoZGnQv8JTc&q=85&s=eb4540325d94664c51776dbbfec4cf02)
> # Image-3
>
> **圖片摘要：**
> utils.py 顯示 calculate_average 函式，右側 Claude Code 說明空值判斷
>
> **主要元素：**
> 1. 實體: utils.py, calculate_average, Python, Claude Code
> 2. OCR文字:
> utils.py
> def calculate_average(numbers):
> if not numbers:
> return 0
> total = 0
> for num in numbers:
> total += num
> return total / len(numbers)
>
> CHAT
> CLAUDE CODE
> @utils.py#2-3 What does this li....
> @utils.py#2-3 What does this line do?
> utils.py#2-3
> This code is a guard clause that
> handles the edge case of an empty
> input:
> Line 2: if not numbers: —
> checks if the numbers list is
> empty or None/falsy
> Line 3: return 0 — if empty,
> returns 0 immediately instead of
> attempting to calculate
> This prevents errors that would occur
> if you tried to operate on an empty
> list e.g., dividing by zero when
>
> ⌘ Esc to focus or unfocus Claude
> Ask before...
> 2 lines sel...
> +
> /
>
> 0
> 0
> -- VISUAL --
> Ln 2, Col 1 36 selected
> Spaces: 4
> UTF-8
> LF
> Python
> Python 3.14.0 homebrew
> Claude Code
> 3. 主題標籤: Python, calculate_average, 空值判斷, Claude Code
>
> **頁面關聯：**
> utils.py 的 Python 函式與 Claude Code 說明面板，錨點 calculate_average
開啟 Claude Code 的其他方式：

- **活動列** ：點擊左側邊欄中的 Spark 圖示以開啟工作階段清單。點擊任何工作階段以將其開啟至您的[偏好位置](https://code.claude.com/docs/zh-TW/vs-code#extension-settings)，或開始新的工作階段。此圖示在活動列中始終可見。
- **命令面板** ：`Cmd+Shift+P`（Mac）或 `Ctrl+Shift+P`（Windows/Linux），輸入「Claude Code」，然後選擇一個選項，例如「在新標籤中開啟」
- **狀態列** ：如果您已將 [`preferredLocation`](https://code.claude.com/docs/zh-TW/vs-code#extension-settings) 設定為 `sidebar`，或使用**Claude Code: Open in Side Bar** 開啟 Claude，請點擊視窗右下角的 **✻ Claude Code** 。即使沒有開啟檔案，這也能運作。

您可以拖曳 Claude 面板以在 VS Code 中的任何位置重新定位。詳細資訊請參閱[自訂您的工作流程](https://code.claude.com/docs/zh-TW/vs-code#customize-your-workflow)。 2 登入 第一次開啟面板時，會出現登入畫面。點擊**登入** 並在瀏覽器中完成授權。如果您稍後看到**未登入 · 請執行 /login** ，擴充功能會自動重新開啟登入畫面。如果沒有出現，請從命令面板使用**開發人員：重新載入視窗** 重新載入視窗。如果您在 shell 中設定了 `ANTHROPIC_API_KEY` 但仍然看到登入提示，VS Code 可能未繼承您的 shell 環境。從終端機使用 `code .` 啟動 VS Code，以便它繼承您的環境變數，或改為使用您的 Claude 帳戶登入。登入後，會出現**學習 Claude Code** 檢查清單。透過點擊**顯示給我** 來完成每個項目，或使用 X 關閉它。若要稍後重新開啟它，請在 VS Code 設定中的「擴充功能」→「Claude Code」下取消勾選**隱藏上線教學** 。 3 傳送提示 要求 Claude 協助您的程式碼或檔案，無論是解釋某些內容的運作方式、除錯問題或進行變更。 Claude 會自動看到您選取的文字。按 `Option+K`（Mac）/ `Alt+K`（Windows/Linux）也可以在您的提示中插入 @-mention 參考（例如 `@file.ts#5-10`）。 以下是詢問檔案中特定行的範例：![VS Code 編輯器在 Python 檔案中選取第 2-3 行，Claude Code 面板顯示關於這些行的問題，並帶有 @-mention 參考](https://mintcdn.com/claude-code/FVYz38sRY-VuoGHA/images/vs-code-send-prompt.png?fit=max&auto=format&n=FVYz38sRY-VuoGHA&q=85&s=ede3ed8d8d5f940e01c5de636d009cfd)
> # Image-4
>
> **圖片摘要：**
> VS Code 顯示 utils.py 的 calculate_average 函式與 Claude Code 編輯確認面板。
>
> **主要元素：**
> 1. 實體: utils.py, calculate_average, Claude Code, Python, docstring
> 2. OCR文字:
> utils.py
> [Claude Code] utils.py
>
> def calculate_average(numbers):
>     """Calculate the arithmetic average of a list of numbers.
>
>     Args:
>         numbers: A list of numeric values.
>
>     Returns:
>         The average of the numbers, or 0 if the list is empty.
>     """
>     if not numbers:
>         return 0
>     total = 0
>     for num in numbers:
>         total += num
>     return total / len(numbers)
>
> CHAT
> CLAUDE CODE
> @utils.py#2-3 What does this l...
> attempting to calculate
> This prevents errors that would occur
> if you tried to operate on an empty
> list (e.g., dividing by zero when
> calculating an average, or getting an
> error from sum() on None).
> Add docstrings
> utils.py
> Read utils.py
> Make this edit to utils.py?
> 1 Yes
> 2 Yes, and don't ask again
> 3 No
> Tell Claude what to do instead
> 0
> 0
> -- NORMAL --
> Ln 2, Col 1
> Spaces: 4
> UTF-8
> LF
> Python
> Claude Code
> 3. 主題標籤: Python, 函式, 算術平均, Claude Code, docstring
>
> **頁面關聯：**
> utils.py 的 Python 函式編輯與 Claude Code 修改確認頁面
4 檢閱變更 您看到的內容取決於提示框底部顯示的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)：

- 在自動或自動編輯模式中，Claude 會編輯工作區中的大多數檔案而不詢問。
- 在手動模式中，當 Claude 想要編輯檔案時，它會顯示原始檔案和建議變更的並排比較，然後要求權限。您可以接受、拒絕或告訴 Claude 改為執行什麼操作。如果您在接受前直接在差異檢視中編輯建議的內容，Claude 會被告知您已修改它，因此不會假設檔案與其原始提案相符。 ![VS Code 顯示 Claude 建議變更的差異，以及詢問是否進行編輯的權限提示](https://mintcdn.com/claude-code/FVYz38sRY-VuoGHA/images/vs-code-edits.png?fit=max&auto=format&n=FVYz38sRY-VuoGHA&q=85&s=e005f9b41c541c5c7c59c082f7c4841c)
如需更多關於您可以使用 Claude Code 執行的操作的想法，請參閱[常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)。 從命令面板執行「Claude Code: Open Walkthrough」以取得基礎知識的引導式導覽。

## 使用提示框

提示框支援多項功能：

- **權限模式** ：點擊提示框底部的模式指示器以切換權限模式。在 Pro、Max 和 Team 方案上，Auto 是內建的起始權限模式。請參閱[擴充功能如何選擇起始權限模式](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)以了解會改變該模式的因素，以及指示器提供的每個權限模式。
  - **Auto** ：分類器會檢查大多數操作，而不是詢問您。請參閱 [auto 模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)以了解它檢查和阻止的內容。
  - **Manual** ：Claude 在檔案編輯和大多數 shell 命令前詢問權限。
  - **Plan** ：Claude 描述它將執行的操作，並在進行變更前等待批准。VS Code 會自動將計畫作為完整 Markdown 文件開啟，您可以在其中新增內嵌註解以在 Claude 開始前提供回饋。
  - **Edit automatically** ：Claude 進行編輯而不詢問。
- **Model** ：從命令菜單中選擇 **Switch model…** 以在會話中途變更模型。您也可以點擊提示框底部的模型名稱以開啟相同的選擇器。當目前的模型支援[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)時，選擇器也會顯示 **Effort** 列和模型名稱按鈕會顯示選定的等級。模型名稱按鈕和 **Effort** 列需要 Claude Code v2.1.257 或更新版本。
- **Command menu** ：點擊 `/` 或輸入 `/` 以開啟命令菜單。選項包括附加檔案、切換模型和切換延伸思考。Customize 部分提供對 MCP 伺服器、slash commands、輸出樣式、hooks、記憶、權限和外掛程式的存取。帶有終端機圖示的項目會在整合終端機中開啟。
  - 若要瀏覽 `/usage` 或 [`/remote-control`](https://code.claude.com/docs/zh-TW/remote-control) 等命令，請在 Customize 部分中選擇 **Slash commands** 。對話方塊會列出它們並提供篩選框。選擇一個以執行它。在提示框中輸入 `/` 仍會內嵌建議命令。需要 Claude Code v2.1.257 或更新版本。
  - 在 Customize 部分中選擇 **Output styles** 以選擇[輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)，包括您的自訂樣式。需要 Claude Code v2.1.257 或更新版本。 若要改為建立自訂樣式，請從 **Output styles** 菜單中選擇 **Build a custom style** 。Claude Code 會在專案或使用者層級為您寫入[樣式檔案](https://code.claude.com/docs/zh-TW/output-styles#create-a-custom-output-style)。需要 Claude Code v2.1.261 或更新版本。
  - 在 Customize 部分中選擇 **Hooks** 以檢視會話中載入的 [hooks](https://code.claude.com/docs/zh-TW/hooks)，按事件分組。您可以新增、編輯或移除儲存在您的使用者、專案和本機設定檔中的 hooks。來自其他來源（例如受管設定或外掛程式）的 Hooks 是唯讀的。需要 Claude Code v2.1.269 或更新版本。
  - 在 Customize 部分中選擇 **Permissions** 以檢視會話的[權限規則](https://code.claude.com/docs/zh-TW/permissions)，分組為 Allow、Ask 和 Deny。您可以將規則新增到您的使用者、專案或本機設定，並移除儲存在那裡的規則。來自其他來源（例如受管設定或僅針對此會話進行的批准）的規則是唯讀的。需要 Claude Code v2.1.269 或更新版本。
  - Settings 部分包括 **Enable Remote Control for all sessions** ，它設定 [`remoteControlAtStartup`](https://code.claude.com/docs/zh-TW/settings-reference#remotecontrolatstartup) 以控制[新的互動式會話是否自動連接到 Remote Control](https://code.claude.com/docs/zh-TW/remote-control#enable-remote-control-for-all-sessions)。需要 Claude Code v2.1.203 或更新版本。 當您在 VS Code 視窗中開啟或關閉切換開關時，變更會套用到該 VS Code 視窗中已開啟的會話，而不僅僅是您之後啟動的會話。如果您關閉它，開啟的會話會中斷連接。使用 Claude Code v2.1.261 或更新版本，變更也會到達您其他 VS Code 視窗中開啟的會話。
  - Settings 部分也包括 **Focus view** ，它隱藏工具呼叫、工具結果和思考在可展開的列後面，只留下您的提示和 Claude 的回應。在那裡切換它，使用 `Ctrl+Option+F`（Mac）/ `Ctrl+Alt+F`（Windows/Linux），或從命令選擇區使用 **Claude Code: Toggle Focus view** 。變更會套用到每個開啟的會話並在會話間保持。需要 Claude Code v2.1.221 或更新版本。 Claude 最新的待辦事項清單保持可見，待處理問題中 Claude 詢問的文字也保持可見；這需要 Claude Code v2.1.225 或更新版本。當 Claude 執行 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 時，帶有其最新活動的即時進度列會出現在啟動它們的工具呼叫群組下。這需要 Claude Code v2.1.269 或更新版本。
  - 若要報告錯誤，請點擊菜單底部的 **Report a problem** ，或輸入 `/bug` 或 `/feedback` 並附上可選的描述以預填報告。當您提交報告且您已在第一方連接上登入 Anthropic 時，Claude Code 會將其傳送給 Anthropic。在第三方提供者上，或沒有 Anthropic 認證時，對話方塊仍會開啟，但提交會顯示錯誤且不傳送任何內容：與 CLI 的 `/bug` 不同，擴充功能不會寫入本機存檔。需要 Claude Code v2.1.229 或更新版本。 如果您的組織政策關閉產品回饋，**Report a problem** 不會出現在菜單中，而 `/bug` 和 `/feedback` 會顯示 `Feedback is turned off by your organization's policy or this environment's settings.` 通知，而不是開啟報告。
- **Side questions** ：輸入 `/btw` 後跟一個問題以詢問有關您的會話的問題[而不新增到對話](https://code.claude.com/docs/zh-TW/interactive-mode#side-questions-with-%2Fbtw)。答案會在聊天旁的面板中開啟，您可以在其中提出後續問題。執行緒在視窗重新載入後仍然存在。Claude Code 保留最新的 20 個交換，並根據 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 排程過期儲存的執行緒，只要 Claude Code 可以[安全地確定保留期](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)。若要清除執行緒，請點擊面板中的垃圾桶圖示。需要 Claude Code v2.1.227 或更新版本。
- **Context indicator** ：提示框顯示您使用了多少 Claude 的內容視窗。Claude 會在需要時自動壓縮，或您可以手動執行 `/compact`。
- **Prompt cache clock** ：內容指示器旁的時鐘圖示估計對話的 [prompt cache](https://code.claude.com/docs/zh-TW/prompt-caching) 在過期前還剩多少時間。它從快取的五分鐘或一小時[生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)倒數，每個使用快取的回應都會重新啟動倒數。除了壓縮外，[使快取失效的操作](https://code.claude.com/docs/zh-TW/prompt-caching#actions-that-invalidate-the-cache)不會重設時鐘，因此在您切換模型後它仍然可以顯示剩餘的分鐘數。
  - 在倒數結束前，圖示會顯示剩餘的分鐘數，例如 **12m** 。
  - 當倒數結束時，分鐘數消失，圖示變為紅色，或您主題的錯誤顏色，直到下一個回應。快取可能已過期，因此預期您下一條訊息的回應會更慢、更昂貴，同時快取重建。如果五分鐘的生命週期在您的訊息之間不斷用完，請參閱[自己選擇 TTL](https://code.claude.com/docs/zh-TW/prompt-caching#choose-the-ttl-yourself)。
  - 對話[壓縮](https://code.claude.com/docs/zh-TW/prompt-caching#compacting-the-conversation)後，圖示也會變為紅色，沒有分鐘數直到下一個回應，因為快取還不涵蓋壓縮的對話。
- **Agent map** ：當對話包括 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 時，代理計數（例如 **2 agents** ）會出現在提示框底部。其點顯示任何 subagent 是否正在工作或等待您的權限。 點擊代理計數以開啟代理地圖，它將對話的 subagents 繪製為主代理下的樹，每個都有其狀態、經過的時間和令牌計數。點擊 subagent 以查看其提示和工具呼叫、開啟其唯讀文字記錄，或在其執行時停止它。需要 Claude Code v2.1.269 或更新版本。
- **Extended thinking** ：讓 Claude 花更多時間推理複雜問題。透過命令菜單（`/`）開啟它。Claude 的推理在對話中顯示為摺疊的區塊：點擊一個區塊以閱讀它，或按 `Ctrl+O` 以展開或摺疊會話中的每個思考區塊。請參閱[Extended thinking](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)以了解詳細資訊。
- **Multi-line input** ：按 `Shift+Enter` 以新增一行而不傳送。這也適用於問題對話的「Other」自由文字輸入。

### 參考檔案和資料夾

使用 @-mentions 為 Claude 提供有關特定檔案或資料夾的內容。當您輸入 `@` 後跟檔案或資料夾名稱時，Claude 會讀取該內容，並可以回答有關它的問題或對其進行變更。Claude Code 支援模糊匹配，因此您可以輸入部分名稱以找到您需要的內容：

```
Explain the logic in @auth (fuzzy matches auth.js, AuthService.ts, etc.)
What's in @src/components/ (include a trailing slash for folders)

```

對於大型 PDF，您可以要求 Claude 讀取特定頁面而不是整個檔案：單一頁面、範圍如第 1-10 頁，或開放式範圍如第 3 頁起。 當您在編輯器中選擇文字時，Claude 可以自動看到您的反白程式碼。提示框頁尾顯示選擇了多少行。按 `Option+K`（Mac）/ `Alt+K`（Windows/Linux）以插入帶有檔案路徑和行號的 @-mention（例如 `@app.ts#5-10`）。點擊選擇指示器上的 **X** 以將其從內容中移除，使 Claude 不會接收選擇。當您選擇其他文字時，指示器會重新出現。 Claude 也會看到您在編輯器中開啟的檔案，即使沒有選擇任何內容，提示框也會顯示其名稱。若要僅新增您選擇的文字，請關閉[附加開啟檔案設定](vscode://settings/claudeCode.attachOpenFile)。此設定需要 Claude Code v2.1.271 或更新版本。 若要附加影像，請從您的剪貼簿將其貼到提示框中。您也可以在將檔案拖入提示框時按住 `Shift` 以將它們新增為附件。點擊任何附件上的 X 以將其從內容中移除。

### 恢復過去的對話

點擊 Claude Code 面板頂部的 **Session history** 按鈕以存取您的對話歷史。您可以按關鍵字搜尋或按時間瀏覽。 點擊任何對話以使用完整的訊息歷史恢復它。如果對話已在目前視窗的另一個標籤中開啟，點擊它會切換到該標籤。如需有關恢復會話的更多資訊，請參閱[管理會話](https://code.claude.com/docs/zh-TW/sessions)。

- **Session titles** ：新會話根據您的第一條訊息接收 AI 生成的標題。
- **Rename and archive** ：將滑鼠懸停在會話上以顯示這些操作。重新命名以給它一個描述性標題，或存檔以將其移動到清單底部的 **Archived sessions** 群組。

預設情況下，14 天內沒有活動的會話會自動移動到 **Archived sessions** ，除非它已開啟、未讀或在[群組](https://code.claude.com/docs/zh-TW/vs-code#organize-sessions-into-groups)中。自動存檔需要 Claude Code v2.1.265 或更新版本。若要變更期間或關閉它，請開啟[存檔非活動會話設定](vscode://settings/claudeCode.archiveInactiveSessions)並選擇天數或 **Never** 。 若要恢復已存檔的會話，請展開 **Archived sessions** 並點擊 **Unarchive session** 。在 v2.1.257 之前，操作是 **Delete session** ，它隱藏了一個會話且無法恢復。您當時刪除的會話在升級後會出現在 **Archived sessions** 下。 當您恢復的對話以計畫模式結束時，Claude Code 會恢復計畫模式。需要 Claude Code v2.1.246 或更新版本。Claude Code 在兩種情況下不會恢復它：

- 擴充功能從 `claudeCode.initialPermissionMode` 或從較早對話中進行的選擇[選擇起始權限模式](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)
- 您已設定 `claudeCode.claudeProcessWrapper`

### 從 Claude.ai 恢復雲端會話

如果您使用[網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，您可以直接在 VS Code 中恢復這些雲端會話。這需要使用 **Claude.ai Subscription** 登入，而不是 Anthropic Console。 1 開啟會話歷史 點擊 Claude Code 面板頂部的 **Session history** 按鈕。 2 選擇 Web 標籤 對話方塊顯示兩個標籤：Local 和 Web。點擊 **Web** 以查看來自 claude.ai 的會話。 3 選擇要恢復的會話 瀏覽或搜尋您的雲端會話。點擊任何會話以下載它並在本機繼續對話。 只有使用 GitHub 存放庫啟動的網路會話才會出現在 Web 標籤中。恢復會在本機載入對話歷史；變更不會同步回 claude.ai。

### 檢查帳戶和使用情況

執行 `/usage` 以開啟帳戶和使用情況對話方塊。對話方塊需要 claude.ai 登入，因此在[第三方提供者](https://code.claude.com/docs/zh-TW/vs-code#use-third-party-providers)上不提供。它顯示您登入的帳戶、您的方案和您方案限制的使用情況列，例如目前會話和週。每個列顯示其限制重設的時間。 對話方塊也會分解對您的方案限制有貢獻的內容。它標記佔最近使用情況 10% 或以上的行為，例如快取未命中、長內容和子代理程式繁重或高度平行會話，每個都有減少它的提示。Attribution 表格顯示每個 skill、subagent、外掛程式和 MCP 伺服器貢獻了多少使用情況。 使用 Day 和 Week 切換以在過去 24 小時和過去 7 天之間切換。這些數字是近似值，並從此機器上的本機會話計算，因此不包括來自其他裝置或 claude.ai 的使用情況。如需有關追蹤和減少使用情況的更多資訊，請參閱[追蹤您的成本](https://code.claude.com/docs/zh-TW/costs#track-your-costs)。

## 自訂您的工作流程

您可以重新定位 Claude 面板、執行多個對話、將工作階段清單組織成群組，或切換到終端機模式。

### 選擇 Claude 的位置

您可以拖曳 Claude 面板在 VS Code 中重新定位到任何位置。抓住面板的標籤或標題列並拖曳到：

- **次要側邊欄** ：視窗的右側。在您編寫程式碼時保持 Claude 可見。
- **主要側邊欄** ：左側邊欄，包含 Explorer、Search 等圖示。
- **編輯器區域** ：將 Claude 作為標籤開啟，與您的檔案並排。適合處理附帶工作。

將側邊欄用於您的主要 Claude 工作階段，並為附帶工作開啟額外的標籤。Claude 會記住您偏好的位置。Activity Bar 工作階段清單圖示與 Claude 面板分開：工作階段清單始終在 Activity Bar 中可見，而 Claude 面板圖示只有在面板停靠到左側邊欄時才會出現在那裡。 執行 **Developer: Reload Window** 或重新啟動 VS Code 後，對話是否會回到其對話內容取決於它在哪裡開啟：

- **編輯器標籤** ：對話會與其標籤一起回到。
- **側邊欄** ：如果您在過去 10 分鐘內傳送了訊息或 Claude 在其中回應，對話會回到。如果它沒有回到，請從 [工作階段歷史記錄](https://code.claude.com/docs/zh-TW/vs-code#resume-past-conversations) 繼續對話。

### 執行多個對話

使用命令選擇板中的 **Open in New Tab** 或 **Open in New Window** 來啟動額外的對話。每個對話都維護自己的歷史記錄和上下文，讓您可以並行處理不同的工作。 使用標籤時，spark 圖示上的小彩色點表示狀態：藍色表示權限要求待處理，橙色表示 Claude 在標籤隱藏時已完成。

### 將工作階段組織成群組

在 Activity Bar 的工作階段清單中，您可以將相關工作階段收集到具名的、可摺疊的群組中。需要 Claude Code v2.1.229 或更新版本。

- **群組或取消群組工作階段** ：右鍵點擊工作階段以從其建立群組、將其移動到現有群組，或將其從其群組中移除。每個工作階段一次只屬於一個群組，因此將其移動到另一個群組會將其從第一個群組中移除。
- **一次移動多個工作階段** ：`Cmd`-點擊 (Mac) / `Ctrl`-點擊 (Windows/Linux) 每個工作階段，或 `Shift`-點擊以選擇一個範圍，然後右鍵點擊選擇。
- **從其標籤群組工作階段** ：從命令選擇板執行 **Claude Code: Add Session Tab to Group** ，然後選擇或建立群組。需要 Claude Code v2.1.257 或更新版本。
- **重新命名或刪除群組** ：右鍵點擊群組標題。刪除群組只會移除群組，其工作階段會回到未群組的清單。

擴充功能會按工作區資料夾儲存群組，因此它們在視窗重新載入後仍然存在，並在您開啟相同資料夾的每個視窗中出現。當您搜尋清單時，擴充功能會在所有群組中的一個平面清單中顯示符合項目。

### 切換到終端機模式

根據預設，擴充功能會開啟圖形化聊天面板。如果您偏好 CLI 風格的介面，請開啟 [Use Terminal 設定](vscode://settings/claudeCode.useTerminal) 並勾選該方塊。 您也可以開啟 VS Code 設定 (Mac 上為 `Cmd+,` 或 Windows/Linux 上為 `Ctrl+,`)，前往 Extensions → Claude Code，並勾選 **Use Terminal** 。

## 管理 plugins

VS Code 擴充功能包含一個圖形介面，用於安裝和管理 [plugins](https://code.claude.com/docs/zh-TW/plugins)。在提示框中輸入 `/plugins` 以開啟**管理 plugins** 介面。

### 安裝 plugins

plugin 對話框顯示兩個標籤：**Plugins** 和 **Marketplaces** 。 在 Plugins 標籤中：

- **已安裝的 plugins** 顯示在頂部，並帶有切換開關以啟用或停用它們
- **可用的 plugins** 來自您設定的 marketplaces，顯示在下方
- 搜尋以按名稱或描述篩選 plugins
- 點擊任何可用 plugin 上的**安裝**

當您安裝 plugin 時，請選擇安裝範圍：

- **為您安裝** ：在您的所有專案中可用（使用者範圍）
- **為此專案安裝** ：與專案協作者共享（專案範圍）
- **本機安裝** ：僅供您使用，僅在此儲存庫中（本機範圍）

### 分享 plugin 安裝連結

若要直接將某人導向安裝特定 plugin，請提供擴充功能的 `install-plugin` URL。開啟它會啟動或聚焦 VS Code、開啟 Claude Code 面板，並在該 plugin 的範圍選擇上開啟**管理 plugins** 對話框。在該人選擇範圍之前，不會安裝任何內容。如果 Claude Code 中尚未設定該 plugin 的 marketplace，對話框會先要求他們新增它。

```
vscode://anthropic.claude-code/install-plugin?plugin=code-review&marketplace=anthropics/claude-plugins-official

```

該 URL 採用兩個查詢參數：

| 參數                                           | 描述                                                                                                                                                                                                                                                   |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `plugin`                                       | plugin 的名稱，如其 marketplace 所列。必需。                                                                                                                                                                                                           |
| `marketplace`                                  | plugin 的來源，採用 [Marketplaces 標籤](https://code.claude.com/docs/zh-TW/vs-code#manage-marketplaces) 接受的任何形式，例如 GitHub `owner/repo` 或 git URL。如果包含 `&` 等字元，請進行 URL 編碼。省略時預設為 `anthropics/claude-plugins-official`。 |
| 兩種情況在對話框中以訊息結束，而不是範圍選擇： |                                                                                                                                                                                                                                                        |

- **marketplace 未按該名稱列出 plugin** ：對話框報告找不到該 plugin。根據 marketplace 的清單檢查 `plugin` 值。
- **plugin 已安裝** ：對話框會說明這一點，且不會進行任何變更。

GitHub README、議題和某些其他 Markdown 主機會移除其方案不是 `http` 或 `https` 的連結，因此 `vscode://` 連結在那裡呈現為純文字。將 URL 放在這些主機上的程式碼區塊中，如 [連結呈現為純文字而不是可點擊的](https://code.claude.com/docs/zh-TW/deep-links#the-link-renders-as-plain-text-instead-of-being-clickable) 針對 `claude-cli://` 連結所描述的那樣。

### 管理 marketplaces

切換到 **Marketplaces** 標籤以新增或移除 plugin 來源：

- 輸入 GitHub 儲存庫、URL 或本機路徑以新增 marketplace
- 點擊重新整理圖示以更新 marketplace 的 plugin 清單
- 點擊垃圾桶圖示以移除 marketplace

您在對話框中進行的 plugin 變更會立即套用到該 VS Code 視窗中開啟的 Claude Code 工作階段。如果您開啟對話框的工作階段無法重新載入其 plugins，對話框會提供重試或在該工作階段中重新啟動 Claude 的選項。 VS Code 中的 plugin 管理在幕後使用相同的 CLI 命令。您在擴充功能中設定的 plugins 和 marketplaces 也可在 CLI 中使用，反之亦然。 如需深入瞭解 plugin 系統，請參閱 [Plugins](https://code.claude.com/docs/zh-TW/plugins) 和 [Plugin marketplaces](https://code.claude.com/docs/zh-TW/plugin-marketplaces)。

## 使用 Chrome 自動化瀏覽器任務

將 Claude 連接到您的 Chrome 瀏覽器，以測試網頁應用程式、使用主控台日誌進行除錯，以及在不離開 VS Code 的情況下自動化瀏覽器工作流程。這需要 [Claude in Chrome 擴充功能](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) 版本 1.0.36 或更高版本。 在提示框中輸入 `@browser`，然後輸入您想要 Claude 執行的操作：

```
@browser go to localhost:3000 and check the console for errors

```

您也可以開啟附件選單，選擇特定的瀏覽器工具，例如開啟新分頁或讀取頁面內容。 Claude 會為瀏覽器任務開啟新分頁，並共享您瀏覽器的登入狀態，因此它可以存取您已登入的任何網站。 如需設定說明、完整的功能清單和疑難排解，請參閱 [使用 Claude Code 搭配 Chrome](https://code.claude.com/docs/zh-TW/chrome)。

## VS Code 命令和快捷鍵

開啟命令面板（Mac 上按 `Cmd+Shift+P` 或 Windows/Linux 上按 `Ctrl+Shift+P`），然後輸入「Claude Code」以查看 Claude Code 擴充功能的所有可用 VS Code 命令。 某些快捷鍵取決於哪個面板「獲得焦點」（接收鍵盤輸入）。當您的游標在程式碼檔案中時，編輯器獲得焦點。當您的游標在 Claude 的提示框中時，Claude 獲得焦點。使用 `Cmd+Esc` / `Ctrl+Esc` 在它們之間切換。 這些是用於控制擴充功能的 VS Code 命令。並非所有內建的 Claude Code 命令都可在擴充功能中使用。詳見 [VS Code 擴充功能與 Claude Code CLI](https://code.claude.com/docs/zh-TW/vs-code#vs-code-extension-vs-claude-code-cli) 以了解詳情。

| 命令                       | 快捷鍵                                                   | 說明                                                                                                                                                                                 |
| -------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Focus Input                | `Cmd+Esc` (Mac) / `Ctrl+Esc` (Windows/Linux)             | 在編輯器和 Claude 之間切換焦點                                                                                                                                                       |
| Open in Side Bar           | -                                                        | 在側邊欄中開啟 Claude                                                                                                                                                                |
| Open in Terminal           | -                                                        | 在終端機模式中開啟 Claude                                                                                                                                                            |
| Open in New Tab            | `Cmd+Shift+Esc` (Mac) / `Ctrl+Shift+Esc` (Windows/Linux) | 以編輯器標籤頁開啟新對話                                                                                                                                                             |
| Open in New Window         | -                                                        | 在單獨的視窗中開啟新對話                                                                                                                                                             |
| New Conversation           | `Cmd+N` (Mac) / `Ctrl+N` (Windows/Linux)                 | 開始新對話。需要 Claude 獲得焦點且 `enableNewConversationShortcut` 設定為 `true`                                                                                                     |
| Reopen Closed Session      | `Cmd+Shift+T` (Mac) / `Ctrl+Shift+T` (Windows/Linux)     | 重新開啟最近關閉的 Claude 工作階段標籤頁。當最後關閉的標籤頁不是 Claude 工作階段時，會回退到 VS Code 的正常重新開啟關閉編輯器功能。可使用 `enableReopenClosedSessionShortcut` 停用   |
| Insert @-Mention Reference | `Option+K` (Mac) / `Alt+K` (Windows/Linux)               | 插入對目前檔案和選取項目的參考（需要編輯器獲得焦點）                                                                                                                                 |
| Toggle Focus view          | `Ctrl+Option+F` (Mac) / `Ctrl+Alt+F` (Windows/Linux)     | 隱藏或顯示對話中的工具活動。在 Claude 面板或側邊欄可見時有效。需要 Claude Code v2.1.221 或更新版本                                                                                   |
| Rename Session Tab         | -                                                        | 重新命名作用中 Claude 標籤頁中的工作階段。需要 Claude Code v2.1.257 或更新版本                                                                                                       |
| Add Session Tab to Group   | -                                                        | 將作用中 Claude 標籤頁中的工作階段新增至您選擇或建立的[工作階段群組](https://code.claude.com/docs/zh-TW/vs-code#organize-sessions-into-groups)。需要 Claude Code v2.1.257 或更新版本 |
| Mark Session as Unread     | -                                                        | 在工作階段清單中將作用中 Claude 標籤頁中的工作階段標記為未讀。需要 Claude Code v2.1.257 或更新版本                                                                                   |
| Show Logs                  | -                                                        | 檢視擴充功能偵錯日誌                                                                                                                                                                 |
| Logout                     | -                                                        | 登出您的 Anthropic 帳戶                                                                                                                                                              |

### 從其他工具啟動 VS Code 標籤頁

該擴充功能在 `vscode://anthropic.claude-code/open` 註冊了 URI 處理程式。使用它從您自己的工具（shell 別名、瀏覽器書籤或任何可以開啟 URL 的指令碼）開啟新的 Claude Code 標籤頁。如果 VS Code 尚未執行，開啟 URL 會先啟動它。如果 VS Code 已在執行，URL 會在目前獲得焦點的視窗中開啟。 使用您的作業系統的 URL 開啟程式叫用處理程式。

- macOS
- Linux
- Windows

```
open "vscode://anthropic.claude-code/open"

```

```
xdg-open "vscode://anthropic.claude-code/open"

```

`xdg-open` 命令來自 `xdg-utils` 套件。如果 shell 報告找不到它，請參閱 [xdg-open is not found on Linux](https://code.claude.com/docs/zh-TW/deep-links#xdg-open-is-not-found-on-linux)。 在 PowerShell 中：

```
Start-Process "vscode://anthropic.claude-code/open"

```

在 `cmd.exe` 中，`start` 將其第一個引號引數視為視窗標題，因此在 URL 之前傳遞空標題：

```
start "" "vscode://anthropic.claude-code/open"

```

該處理程式接受兩個選用查詢參數：

| 參數                                                  | 說明                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`                                              | 在提示框中預先填入的文字。必須進行 URL 編碼。提示會預先填入但不會自動提交。                                                                                                                                                                                                                           |
| `session`                                             | 要繼續的工作階段 ID，而不是開始新對話。工作階段必須屬於目前在 VS Code 中開啟的工作區。如果找不到工作階段，則改為開始新對話。如果工作階段已在標籤頁中開啟，則會焦點該標籤頁。若要以程式設計方式擷取工作階段 ID，請參閱[繼續對話](https://code.claude.com/docs/zh-TW/headless#continue-conversations)。 |
| 例如，若要開啟預先填入「review my changes」的標籤頁： |                                                                                                                                                                                                                                                                                                       |

```
vscode://anthropic.claude-code/open?prompt=review%20my%20changes

```

該擴充功能也會處理 `vscode://anthropic.claude-code/install-plugin`，它會[在一個外掛程式上開啟外掛程式對話](https://code.claude.com/docs/zh-TW/vs-code#share-a-plugin-install-link)。若要啟動終端機工作階段而不是 VS Code 標籤頁，請使用 CLI 的 `claude-cli://` 處理程式。請參閱[從連結啟動工作階段](https://code.claude.com/docs/zh-TW/deep-links)。

## 設定設定

此擴充功能有兩種類型的設定：

- **VS Code 中的擴充功能設定** ：控制擴充功能在 VS Code 中的行為。使用 `Cmd+,`（Mac）或 `Ctrl+,`（Windows/Linux）開啟，然後前往 Extensions → Claude Code。您也可以輸入 `/` 並選擇 **General config…** 來開啟設定。
- **`~/.claude/settings.json`中的 Claude Code 設定** ：在擴充功能和 CLI 之間共享。用於允許的命令、環境變數、hooks 和 MCP 伺服器。在 Pro、Max 和 Team 方案上，它也是權限模式對話開始時的一個輸入。[切換權限模式](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)列出順序。詳見[設定](https://code.claude.com/docs/zh-TW/settings)。

將 `"$schema": "https://json.schemastore.org/claude-code-settings.json"` 新增至您的 `settings.json`，以在 VS Code 中直接取得所有可用設定的自動完成和內嵌驗證。

### 擴充功能設定

VS Code 從您的使用者設定讀取 `initialPermissionMode`，並忽略工作區值。在 v2.1.225 之前，VS Code 預設將設定設為 `default` 並套用工作區值。

| 設定                                | 預設值  | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `useTerminal`                       | `false` | 以終端機模式而非圖形面板啟動 Claude                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `initialPermissionMode`             | -       | 控制新對話的核准提示：`default`、`plan`、`acceptEdits` 或 `bypassPermissions`。`manual` 是 `default` 的別名，並選擇模式指示器中標示為 **Manual** 的模式。當您將其保留為未設定時，擴充功能會選擇起始權限模式，如[切換權限模式](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)中所述。                                                                                                                                                                                                                                                                                                                                       |
| `preferredLocation`                 | `panel` | Claude 開啟的位置：`sidebar`（右側）或 `panel`（新標籤）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `autosave`                          | `true`  | Claude 讀取或寫入檔案前自動儲存檔案                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `attachOpenFile`                    | `true`  | 將編輯器中開啟的檔案新增至您的訊息，並在提示框中顯示。關閉時，只會新增您選取的文字。需要 Claude Code v2.1.271 或更新版本                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `useCtrlEnterToSend`                | `false` | 使用 Ctrl/Cmd+Enter 而非 Enter 來傳送提示                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `enableNewConversationShortcut`     | `false` | 啟用 Cmd/Ctrl+N 以開始新對話                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `enableReopenClosedSessionShortcut` | `true`  | 使用 Cmd/Ctrl+Shift+T 重新開啟最近關閉的 Claude 工作階段標籤。當最後關閉的標籤不是 Claude 工作階段時，快捷鍵會改為執行 VS Code 的正常重新開啟已關閉編輯器命令。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `archiveInactiveSessions`           | `14`    | 在無活動的這許多天後[自動封存工作階段](https://code.claude.com/docs/zh-TW/vs-code#resume-past-conversations)：`1`、`2`、`7` 或 `14`。設定為 `0` 以關閉。需要 Claude Code v2.1.265 或更新版本                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `hideOnboarding`                    | `false` | 隱藏上線檢查清單（畢業帽圖示）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `focusView`                         | `false` | 將工具呼叫、工具結果和思考隱藏在可展開的列後面，只留下您的提示和 Claude 的回應。Claude 的最新待辦事項清單保持可見；這需要 Claude Code v2.1.225 或更新版本。您也可以從命令選單切換焦點檢視。需要 Claude Code v2.1.221 或更新版本                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `respectGitIgnore`                  | `true`  | 從檔案搜尋中排除 .gitignore 模式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `usePythonEnvironment`              | `true`  | 執行 Claude 時啟動工作區的 Python 環境。需要 Python 擴充功能。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `environmentVariables`              | `[]`    | 為 Claude 程序設定環境變數。使用 Claude Code 設定以改為共享設定。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `disableLoginPrompt`                | `false` | 略過驗證提示（用於第三方提供者設定）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `allowDangerouslySkipPermissions`   | `false` | 將略過權限新增至模式選擇器。僅在沒有網際網路存取的沙箱中使用。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `claudeProcessWrapper`              | -       | 用於啟動 Claude 程序的可執行檔。當存在時，組合的二進位路徑會作為引數傳遞。如果擴充功能組建不包含您平台的二進位檔，請將其設定為單獨安裝的 `claude` 二進位檔。在包裝的設定中，對話以 Manual 模式開始，除非您設定 `initialPermissionMode` 或在較早的對話中選擇了 Manual、Edit automatically 或 Auto，因為擴充功能會在那裡略過設定和內建預設步驟；請參閱[切換權限模式](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)。啟動時出現「不支援的平台」錯誤表示您的平台沒有組合的二進位檔；請參閱[哪些平台有預先建置的二進位檔](https://code.claude.com/docs/zh-TW/troubleshoot-install#native-binary-not-found-after-npm-install)。 |

## 使用螢幕閱讀器

擴充功能的聊天面板可與螢幕閱讀器搭配使用。您無需開啟任何設定：擴充功能會為每位使用者宣告對話活動，不會有任何視覺變化。這與 CLI 的選擇加入 [螢幕閱讀器模式](https://code.claude.com/docs/zh-TW/accessibility) 不同，後者會調整終端機介面。 聊天面板中的螢幕閱讀器支援需要 Claude Code v2.1.236 或更新版本。 在對話期間，擴充功能會宣告：

- **Claude 的回覆** ：擴充功能會在回覆完成時宣告一次，並在文字串流進入時保持沉默。您的螢幕閱讀器會將程式碼區塊讀作行數摘要，按標籤讀取連結，並逐個儲存格讀取表格；完整回覆在文字記錄中保持可讀。
- **權限請求和問題** ：當權限提示出現時，擴充功能會宣告請求，並命名 Claude 想要使用的工具。當 Claude 向您提出問題以及當 Claude 完成計畫並等待您的審查時，它也會以相同方式宣告。
- **狀態變更** ：當 Claude 開始工作、Claude 準備好接收您的輸入，以及 Claude Code 開始壓縮對話時，擴充功能會宣告。
- **錯誤和模型提示** ：擴充功能會宣告對話中的錯誤，並在 [使用額度同意提示](https://code.claude.com/docs/zh-TW/model-config#fable-and-usage-credits) 或 [標記請求提示](https://code.claude.com/docs/zh-TW/model-config#ask-before-switching) 出現時宣告。

文字記錄中的每一輪都以視覺上隱藏的標題開始，標題標有啟動該輪的提示，因此您可以使用螢幕閱讀器的標題導覽在各輪之間跳轉。您也可以使用 `Tab` 將焦點移至文字記錄本身，因為擴充功能會將其公開為標記區域，並按自己的步調讀取。當 Claude 工作時，您的螢幕閱讀器會讀取文字標籤，以取代進度微調器的動畫。 當您重新開啟工作階段或切換到另一個工作階段時，擴充功能不會宣告任何內容：已還原的歷史記錄、待處理的權限提示和進行中的狀態會保持沉默，直到發生新的事情。

## VS Code 擴充功能 vs. Claude Code CLI

Claude Code 可作為 VS Code 擴充功能（圖形面板）和 CLI（終端機中的命令列介面）使用。某些功能僅在 CLI 中可用。如果您需要 CLI 專用功能，請在 VS Code 的整合終端機中執行 `claude`。這需要[獨立 CLI 安裝](https://code.claude.com/docs/zh-TW/setup)：擴充功能不會將 `claude` 新增至您的 PATH。請參閱[在 VS Code 中執行 CLI](https://code.claude.com/docs/zh-TW/vs-code#run-cli-in-vs-code)。

| 功能              | CLI                             | VS Code 擴充功能                                                                                                                |
| ----------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 命令和 skills     | 子集（輸入 `/` 以查看可用項目） |                                                                                                                                 |
| MCP 伺服器設定    | 是                              | 是（在聊天面板中使用 `/mcp` [新增和管理伺服器](https://code.claude.com/docs/zh-TW/vs-code#connect-to-external-tools-with-mcp)） |
| Checkpoints       | 是                              | 是                                                                                                                              |
| `!` Bash 快捷方式 | 是                              | 否                                                                                                                              |
| Tab 完成          | 是                              | 否                                                                                                                              |

### 使用 checkpoints 進行 Rewind

VS Code 擴充功能支援 checkpoints，可追蹤 Claude 的檔案編輯並讓您 rewind 到先前的狀態。將滑鼠懸停在任何訊息上以顯示 rewind 按鈕，然後從三個選項中選擇：

- **Fork conversation from here** ：從此訊息開始新的對話分支，同時保持所有程式碼變更
- **Rewind code to here** ：將檔案變更還原到對話中的此點，同時保持完整的對話歷史記錄
- **Fork conversation and rewind code** ：開始新的對話分支並將檔案變更還原到此點

如需有關 checkpoints 如何運作及其限制的完整詳細資訊，請參閱 [Checkpointing](https://code.claude.com/docs/zh-TW/checkpointing)。

### 在 VS Code 中執行 CLI

若要在 VS Code 中使用 CLI，請開啟整合終端機（Windows/Linux 上為 ``` Ctrl+``，Mac 上為  ```Cmd+\`\`）並執行 `claude`。CLI 會自動與您的 IDE 整合，以支援差異檢視和診斷共享等功能。 安裝擴充功能不會將 `claude` 放在您的 shell PATH 上。擴充功能為其聊天面板提供了 CLI 的私人副本，但在終端機中輸入 `claude` 需要[獨立 CLI 安裝](https://code.claude.com/docs/zh-TW/setup)。執行一次安裝，此頁面上的命令（包括 `claude mcp add` 和 `claude --resume`）將在任何終端機中運作。如果安裝後仍找不到 `claude`，請[驗證您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)。 如果使用外部終端機，請在 Claude Code 內執行 `/ide` 以將其連接到 VS Code。

### 在擴充功能和 CLI 之間切換

擴充功能和 CLI 共享相同的對話歷史記錄。若要在 CLI 中繼續擴充功能對話，請在終端機中執行 `claude --resume`。這會開啟互動式選擇器，您可以在其中搜尋並選擇您的對話。

### 在提示中包含終端機輸出

使用 `@terminal:name` 在您的提示中參考終端機輸出，其中 `name` 是終端機的標題。這讓 Claude 可以看到命令輸出、錯誤訊息或日誌，而無需複製貼上。

### 監控背景程序

擴充功能中背景工作的可見性與 CLI 相比受限。為了獲得更好的可見性，讓 Claude 輸出命令，以便您可以在 VS Code 的整合終端機中執行它。

### 使用 MCP 連接到外部工具

MCP（Model Context Protocol）伺服器讓 Claude 可以存取外部工具、資料庫和 API。 若要在不離開 VS Code 的情況下管理 MCP 伺服器，請在聊天面板中輸入 `/mcp`。從開啟的對話方塊中，您可以新增伺服器、移除儲存在本機、使用者或專案[範圍](https://code.claude.com/docs/zh-TW/mcp#mcp-installation-scopes)的伺服器、啟用或停用伺服器、重新連接到伺服器以及管理 OAuth 驗證。在對話方塊中新增和移除伺服器需要 Claude Code v2.1.261 或更新版本。 您也可以在 VS Code 的整合終端機中執行 `claude mcp add`（``` Ctrl+`` 或  ```Cmd+\`\`）。對話方塊和終端機命令會儲存到相同的 MCP 設定，來自任一方的變更會在您之後開始的對話中生效。下面的範例新增了 GitHub 的遠端 MCP 伺服器，該伺服器使用作為標頭傳遞的[個人存取權杖](https://github.com/settings/personal-access-tokens)進行驗證：

```
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

```

將 `YOUR_GITHUB_PAT` 替換為您的個人存取權杖。`claude mcp add` 命令會儲存設定而不驗證認證，因此此處接受預留位置值，但伺服器稍後無法連接。若要驗證連接，請開始新對話、輸入 `/mcp`，並檢查伺服器是否顯示**已連接** 。具有不良認證的伺服器會顯示**失敗** 。 設定完成後，要求 Claude 使用這些工具（例如，「Review PR #456」）。 若要尋找要連接的伺服器，請參閱[尋找和建置 MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp#find-and-build-mcp-servers)。

## 使用 git

Claude Code 與 git 整合，協助您直接在 VS Code 中進行版本控制工作流程。要求 Claude 提交變更、建立提取請求或跨分支工作。若要在具有自己的檔案和分支的隔離 worktree 中啟動 Claude，請參閱 [使用 worktrees 執行平行工作階段](https://code.claude.com/docs/zh-TW/worktrees)。

### 建立提交和提取請求

Claude 可以暫存變更、撰寫提交訊息，以及根據您的工作建立提取請求：

```
commit my changes with a descriptive message
create a pr for this feature
summarize the changes I've made to the auth module

```

建立提取請求時，Claude 會根據實際的程式碼變更產生描述，並可以新增有關測試或實作決策的內容。

## 使用第三方提供者

根據預設，Claude Code 直接連接到 Anthropic 的 API。如果您的組織使用 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 來存取 Claude，請設定擴充功能以改用您的提供者： 1 停用登入提示 開啟[停用登入提示設定](vscode://settings/claudeCode.disableLoginPrompt)並勾選該方塊。您也可以開啟 VS Code 設定（Mac 上按 `Cmd+,` 或 Windows/Linux 上按 `Ctrl+,`），搜尋「Claude Code login」，然後勾選**停用登入提示** 。 2 設定您的提供者 按照您提供者的設定指南進行：

- [Claude Code on Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)
- [Claude Code on Google Cloud’s Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai)
- [Claude Code on Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry)

這些指南涵蓋在 `~/.claude/settings.json` 中設定您的提供者，這可確保您的設定在 VS Code 擴充功能和 CLI 之間共享。 在第三方提供者上，擴充功能不提供需要 claude.ai 帳戶的功能，例如使用情況追蹤、[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)和用於[從 Claude.ai 繼續雲端工作階段](https://code.claude.com/docs/zh-TW/vs-code#resume-cloud-sessions-from-claude-ai)的 Web 標籤。來自較早 `/login` 的 claude.ai 登入會保留下來但未使用：擴充功能不會在任何請求中傳送它。

## 安全性和隱私

您的程式碼保持私密。Claude Code 會處理您的程式碼以提供協助，但不會使用它來訓練模型。如需有關資料處理和如何選擇退出記錄的詳細資訊，請參閱[資料和隱私](https://code.claude.com/docs/zh-TW/data-usage)。 啟用自動編輯權限後，Claude Code 可以修改 VS Code 設定檔（例如 `settings.json` 或 `tasks.json`），VS Code 可能會自動執行這些檔案。為了在處理不受信任的程式碼時降低風險：

- 為不受信任的工作區啟用 [VS Code 受限模式](https://code.visualstudio.com/docs/editor/workspace-trust#_restricted-mode)
- 使用手動模式而不是自動編輯或自動進行編輯
- 在接受變更前仔細檢查

### 內建 IDE MCP 伺服器

當擴充功能處於活動狀態時，它會執行一個本機 MCP 伺服器，CLI 會自動連接到該伺服器。這就是 CLI 如何在 VS Code 的原生差異檢視器中開啟差異、讀取您目前的選擇以進行 `@` 提及，以及在您在 Jupyter 筆記本中工作時要求 VS Code 執行儲存格的方式。 伺服器名稱為 `ide`，並且從 `/mcp` 隱藏，因為沒有任何要設定的內容。不過，如果您的組織使用 `PreToolUse` hook 來允許列表 MCP 工具，您需要知道它的存在。 **選擇和開啟檔案內容。** 連接時，CLI 會在您傳送的每個提示上包含您目前的編輯器選擇和活動檔案的路徑作為內容。當發生這種情況時，文字記錄會顯示 `⧉ Selected N lines from <file>` 行。若要排除敏感檔案（例如 `.env`），請為其路徑新增 [`Read` 拒絕規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)。相符的拒絕規則會防止該檔案的選定文字和開啟檔案通知到達 Claude。 如果您關閉[附加開啟檔案設定](https://code.claude.com/docs/zh-TW/vs-code#extension-settings)，CLI 只有在您在該檔案中選取文字時才會接收活動檔案的路徑。 **傳輸和驗證。** 伺服器繫結到 `127.0.0.1` 上的隨機連接埠，範圍在 10000–65535，連接埠不可設定。傳輸是未加密的 `ws://`；因為通訊端是僅限迴圈的，任何可以擷取流量的程序也可以從鎖定檔案讀取權杖，所以 TLS 不會增加保護。每次擴充功能啟動都會產生一個新的隨機驗證權杖，將其寫入位於 `~/.claude/ide/<port>.lock` 的鎖定檔案，CLI 必須將其作為 `X-Claude-Code-Ide-Authorization` 標頭呈現以進行連接。鎖定檔案在 `0700` 目錄中具有 `0600` 權限，因此只有執行 VS Code 的使用者可以讀取它。如果設定了 `CLAUDE_CONFIG_DIR`，鎖定檔案會改為寫入 `$CLAUDE_CONFIG_DIR/ide/`。 **公開給模型的工具。** 伺服器裝載十幾個工具，但只有兩個對模型可見。其餘的是 CLI 用於自己的 UI 的內部 RPC（開啟差異、讀取選擇、儲存檔案），在工具清單到達 Claude 之前會被篩選掉。

| 工具名稱（如 hooks 所見）                                                                                                                                                                                                                                                                                                                                                                             | 它的作用                                                                      | 唯讀 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---- |
| `mcp__ide__getDiagnostics`                                                                                                                                                                                                                                                                                                                                                                            | 傳回語言伺服器診斷 — VS Code 的問題面板中的錯誤和警告。可選擇限定於一個檔案。 | 是   |
| `mcp__ide__executeCode`                                                                                                                                                                                                                                                                                                                                                                               | 在活動 Jupyter 筆記本的核心中執行 Python 程式碼。請參閱下面的確認流程。       | 否   |
| **Jupyter 執行始終先詢問。** `mcp__ide__executeCode` 無法以無聲方式執行任何操作。在每次呼叫時，程式碼會作為新儲存格插入到活動筆記本的末尾，VS Code 會將其捲動到檢視中，原生快速選擇會要求您**執行** 或**取消** 。取消 — 或使用 `Esc` 關閉選擇器 — 會向 Claude 傳回錯誤，不會執行任何操作。當沒有活動筆記本、未安裝 Jupyter 擴充功能 (`ms-toolsai.jupyter`) 或核心不是 Python 時，該工具也會直接拒絕。 |                                                                               |      |
| 快速選擇確認與 `PreToolUse` hooks 分開。`mcp__ide__executeCode` 的允許列表項目讓 Claude _提議_ 執行儲存格；VS Code 內的快速選擇是讓它 _實際_ 執行的原因。                                                                                                                                                                                                                                             |                                                                               |      |

## 修復常見問題

### 擴充功能無法安裝

- 確保您有相容的 VS Code 版本（1.94.0 或更新版本）
- 檢查 VS Code 是否有權限安裝擴充功能
- 嘗試直接從 [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) 安裝

### Spark 圖示不可見

當您開啟檔案時，Spark 圖示會出現在**編輯器工具列** （編輯器右上角）。如果您看不到它：

1. **開啟檔案** ：該圖示需要開啟檔案。只開啟資料夾是不夠的。
1. **檢查 VS Code 版本** ：需要 1.94.0 或更高版本（說明 → 關於）
1. **重新啟動 VS Code** ：從命令選擇板執行「Developer: Reload Window」
1. **停用衝突的擴充功能** ：暫時停用其他 AI 擴充功能（Cline、Continue 等）
1. **檢查工作區信任** ：擴充功能在受限模式下無法運作

或者，如果您已將 [`preferredLocation`](https://code.claude.com/docs/zh-TW/vs-code#extension-settings) 設定為 `sidebar`，或使用 **Claude Code: Open in Side Bar** 開啟 Claude，請點擊**狀態列** （右下角）中的「✻ Claude Code」。即使沒有開啟檔案，這也能運作。您也可以使用**命令選擇板** （`Cmd+Shift+P` / `Ctrl+Shift+P`）並輸入「Claude Code」。

### Cmd+Esc 在 macOS 上無法運作

在 macOS Tahoe 及更新版本上，系統遊戲覆蓋快捷鍵預設綁定到 `Cmd+Esc`，並在按鍵到達 VS Code 之前攔截它。若要釋放快捷鍵：

1. 開啟系統設定
1. 前往鍵盤，然後鍵盤快捷鍵，然後遊戲控制器
1. 清除遊戲覆蓋核取方塊

或者，將擴充功能重新綁定到不同的按鍵：開啟 VS Code [快捷鍵編輯器](https://code.visualstudio.com/docs/configure/keybindings)（`Cmd+K Cmd+S`），搜尋 `Claude Code: Focus input`，並指派新的綁定。

### Claude Code 從不回應

如果 Claude Code 沒有回應您的提示：

1. **檢查您的網際網路連線** ：確保您有穩定的網際網路連線
1. **開始新對話** ：嘗試開始新的對話，看看問題是否仍然存在
1. **嘗試 CLI** ：從終端執行 `claude` 以查看是否獲得更詳細的錯誤訊息

如果問題仍然存在，請[在 GitHub 上提交問題](https://github.com/anthropics/claude-code/issues)，並提供有關錯誤的詳細資訊。

## 解除安裝擴充功能

若要解除安裝 Claude Code 擴充功能：

1. 開啟擴充功能檢視（Mac 上按 `Cmd+Shift+X` 或 Windows/Linux 上按 `Ctrl+Shift+X`）
1. 搜尋「Claude Code」
1. 點擊**解除安裝**

如果您在 VS Code 整合式終端中執行 `claude`，Claude Code 會自動重新安裝擴充功能。若要保持解除安裝狀態，請在 `/config` 中關閉**自動安裝 IDE 擴充功能** ，或將 [`autoInstallIdeExtension`](https://code.claude.com/docs/zh-TW/settings-reference#autoinstallideextension) 設定為 `false`。您也可以將 [`CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數設定為 `1`。 若要同時移除擴充功能資料並重設所有設定，請刪除您平台的擴充功能儲存目錄。 在 macOS 上：

```
rm -rf ~/Library/"Application Support"/Code/User/globalStorage/anthropic.claude-code

```

在 Linux 上：

```
rm -rf ~/.config/Code/User/globalStorage/anthropic.claude-code

```

在 Windows 上，在 PowerShell 中：

```
Remove-Item -Recurse -Force "$env:APPDATA\Code\User\globalStorage\anthropic.claude-code"

```

如需其他協助，請參閱[疑難排解指南](https://code.claude.com/docs/zh-TW/troubleshooting)。

## 後續步驟

現在您已在 VS Code 中設定好 Claude Code：

- [探索常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)以充分利用 Claude Code
- [設定 MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)以使用外部工具擴展 Claude 的功能。在聊天面板中使用 `/mcp` 新增和管理它們。
- [設定 Claude Code 設定](https://code.claude.com/docs/zh-TW/settings)以自訂允許的命令、hooks 等。這些設定在擴充功能和 CLI 之間共用。

是否 助手