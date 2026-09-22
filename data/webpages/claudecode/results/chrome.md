Claude Code 與 [Claude in Chrome 瀏覽器擴充功能](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn)整合，為您提供從 CLI 或 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code#automate-browser-tasks-with-chrome) 進行瀏覽器自動化的功能。建立您的程式碼，然後在瀏覽器中測試和除錯，無需切換上下文。 Claude 為瀏覽器任務開啟新標籤頁，並共享您瀏覽器的登入狀態，因此它可以存取您已登入的任何網站。瀏覽器操作在可見的 Chrome 視窗中即時執行。當 Claude 遇到登入頁面或 CAPTCHA 時，它會暫停並要求您手動處理。 Chrome 整合適用於 Google Chrome 和 Microsoft Edge。尚不支援 Brave、Arc 或其他基於 Chromium 的瀏覽器。也不支援 Windows Subsystem for Linux (WSL)。

## 功能

連接 Chrome 後，您可以在單一工作流程中鏈接瀏覽器操作與編碼任務：

- **即時除錯** ：直接讀取控制台錯誤和 DOM 狀態，然後修復導致它們的程式碼
- **設計驗證** ：從 Figma 模型建立 UI，然後在瀏覽器中開啟以驗證它是否相符
- **網頁應用程式測試** ：測試表單驗證、檢查視覺回歸或驗證使用者流程
- **已驗證的網頁應用程式** ：與 Google Docs、Gmail、Notion 或您已登入的任何應用程式互動，無需 API 連接器
- **資料提取** ：從網頁中提取結構化資訊並將其儲存在本地
- **任務自動化** ：自動化重複的瀏覽器任務，如資料輸入、表單填充或多網站工作流程
- **工作階段錄製** ：將瀏覽器互動錄製為 GIF，以記錄或分享發生的情況

## 先決條件

在使用 Claude Code 與 Chrome 之前，您需要：

- [Google Chrome](https://www.google.com/chrome/) 或 [Microsoft Edge](https://www.microsoft.com/edge) 瀏覽器
- [Claude in Chrome 擴充功能](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) 版本 1.0.36 或更高版本，可在 Chrome Web Store 中為兩個瀏覽器取得
- [Claude Code](https://code.claude.com/docs/zh-TW/quickstart#step-1-install-claude-code)
- 直接 Anthropic 計畫（Pro、Max、Team 或 Enterprise）

Chrome 整合不適用於 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 等第三方提供商。如果您只透過第三方提供商存取 Claude，則需要單獨的 claude.ai 帳戶才能使用此功能。

## 在 CLI 中開始

1 使用 Chrome 啟動 Claude Code 使用 `--chrome` 標誌啟動 Claude Code：

```
claude --chrome

```

您也可以透過執行 `/chrome` 在現有工作階段中啟用 Chrome。 2 要求 Claude 使用瀏覽器 此範例導航到頁面、與其互動並報告其發現，全部來自您的終端或編輯器：

```
Go to code.claude.com/docs, click on the search box,
type "hooks", and tell me what results appear

```

第一個瀏覽器操作會要求使用 `claude-in-chrome` 技能的權限。批准它，Claude 會開啟新標籤並開始執行任務。 隨時執行 `/chrome` 以檢查連接狀態、管理權限、重新連接擴充功能，或選擇要使用的已連接瀏覽器。如果在瀏覽器操作開始時連接了多個瀏覽器，Claude 會提示您選擇一個。 對於 VS Code，請參閱 [VS Code 中的瀏覽器自動化](https://code.claude.com/docs/zh-TW/vs-code#automate-browser-tasks-with-chrome)。

### 預設啟用 Chrome

為了避免每個工作階段都傳遞 `--chrome`，執行 `/chrome` 並選擇「預設啟用」。 在 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code#automate-browser-tasks-with-chrome) 中，只要安裝了 Chrome 擴充功能，Chrome 就可用。無需額外標誌。 在 CLI 中預設啟用 Chrome 會增加上下文使用量，因為瀏覽器工具始終被載入。如果您注意到上下文消耗增加，請停用此設定，並僅在需要時使用 `--chrome`。

### 管理網站權限

網站級權限繼承自 Chrome 擴充功能。在 Chrome 擴充功能設定中管理權限，以控制 Claude 可以瀏覽、點擊和輸入的網站。

### 計畫模式中的瀏覽器工具

在 [計畫模式](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 中，只讀取頁面或瀏覽器狀態的瀏覽器工具呼叫無需權限提示即可執行，而改變狀態的呼叫會提示批准。

- **唯讀呼叫** ：`read_page`、`get_page_text`、`find`、讀取主控台訊息或網路請求，以及擷取螢幕截圖
- **改變狀態的呼叫** ：點擊、輸入、導航、標籤和視窗管理，以及錄製 GIF

自 v2.1.199 起，設定狀態改變輸入標誌的唯讀呼叫（例如 `tabs_context_mcp` 上的 `createIfEmpty`、主控台和網路讀取器上的 `clear`，或螢幕截圖上的 `save_to_disk`）也會提示批准。`browser_batch` 呼叫只有在其中的每個操作都是唯讀時，才會無提示執行。

## 範例工作流程

這些範例展示了將瀏覽器操作與編碼任務結合的常見方式。執行 `/mcp`，選擇 `claude-in-chrome`，然後選擇 **View tools** 以查看可用瀏覽器工具的完整清單。

### 測試本地網頁應用程式

開發網頁應用程式時，要求 Claude 驗證您的變更是否正確運作：

```
I just updated the login form validation. Can you open localhost:3000,
try submitting the form with invalid data, and check if the error
messages appear correctly?

```

Claude 導航到您的本地伺服器、與表單互動並報告其觀察結果。

### 使用控制台日誌進行除錯

Claude 可以讀取控制台輸出以幫助診斷問題。告訴 Claude 要尋找的模式，而不是要求所有控制台輸出，因為日誌可能很冗長：

```
Open the dashboard page and check the console for any errors when
the page loads.

```

Claude 讀取控制台訊息，可以篩選特定模式或錯誤類型。

### 自動填充表單

加快重複資料輸入任務的速度：

```
I have a spreadsheet of customer contacts in contacts.csv. For each row,
go to the CRM at crm.example.com, click "Add Contact", and fill in the
name, email, and phone fields.

```

Claude 讀取您的本地檔案、導航網頁介面並為每筆記錄輸入資料。

### 在 Google Docs 中起草內容

使用 Claude 直接在您的文件中寫入，無需 API 設定：

```
Draft a project update based on the recent commits and add it to my
Google Doc at docs.google.com/document/d/abc123

```

Claude 開啟文件、點擊編輯器並輸入內容。這適用於您已登入的任何網頁應用程式：Gmail、Notion、Sheets 等。

### 從網頁中提取資料

從網站中提取結構化資訊：

```
Go to the product listings page and extract the name, price, and
availability for each item. Save the results as a CSV file.

```

Claude 導航到頁面、讀取內容並將資料編譯成結構化格式。

### 執行多網站工作流程

協調多個網站之間的任務：

```
Check my calendar for meetings tomorrow, then for each meeting with
an external attendee, look up their company website and add a note
about what they do.

```

Claude 跨標籤頁工作以收集資訊並完成工作流程。

### 錄製演示 GIF

建立瀏覽器互動的可共享錄製：

```
Record a GIF showing how to complete the checkout flow, from adding
an item to the cart through to the confirmation page.

```

Claude 錄製互動序列並將其儲存為 GIF 檔案。

## 故障排除

### 未偵測到擴充功能

如果 Claude Code 無法偵測到 Chrome 擴充功能：

1. 驗證 Chrome 擴充功能已安裝並在 `chrome://extensions` 中啟用
1. 透過執行 `claude --version` 驗證 Claude Code 是否為最新版本
1. 檢查 Chrome 是否正在執行
1. 執行 `/chrome` 並選擇「重新連接擴充功能」以重新建立連接
1. 如果問題仍然存在，請重新啟動 Claude Code 和 Chrome

第一次啟用 Chrome 整合時，Claude Code 會安裝原生訊息主機設定檔。Chrome 在啟動時讀取此檔案，因此如果擴充功能在您的第一次嘗試中未被偵測到，請重新啟動 Chrome 以取得新設定。 自 v2.1.199 起，Claude Code 會在第一次安裝時開啟瀏覽器標籤頁，提示您連接擴充功能。稍後重寫設定檔的工作階段（例如在切換 Claude Code 組建或設定目錄後）不會重新開啟它。 如果連接仍然失敗，請驗證主機設定檔是否存在於： 對於 Chrome：

- **macOS** ：`~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Linux** ：`~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Windows** ：在 Windows 登錄中檢查 `HKCU\Software\Google\Chrome\NativeMessagingHosts\`

對於 Edge：

- **macOS** ：`~/Library/Application Support/Microsoft Edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Linux** ：`~/.config/microsoft-edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Windows** ：在 Windows 登錄中檢查 `HKCU\Software\Microsoft\Edge\NativeMessagingHosts\`

### 瀏覽器無回應

如果 Claude 的瀏覽器命令停止工作：

1. 檢查是否有模態對話框（警告、確認、提示）阻止頁面。JavaScript 對話框會阻止瀏覽器事件並防止 Claude 接收命令。手動關閉對話框，然後告訴 Claude 繼續。
1. 要求 Claude 建立新標籤頁並重試
1. 透過在 `chrome://extensions` 中停用並重新啟用 Chrome 擴充功能來重新啟動它

### 長工作階段期間連接中斷

Chrome 擴充功能的服務工作者可能在延長的工作階段期間進入閒置狀態，這會中斷連接。如果瀏覽器工具在一段時間不活動後停止工作，請執行 `/chrome` 並選擇「重新連接擴充功能」。

### Windows 特定問題

在 Windows 上，您可能會遇到：

- **命名管道衝突 (EADDRINUSE)** ：如果另一個程序正在使用相同的命名管道，請重新啟動 Claude Code。關閉任何可能使用 Chrome 的其他 Claude Code 工作階段。
- **原生訊息主機錯誤** ：如果原生訊息主機在啟動時崩潰，請嘗試重新安裝 Claude Code 以重新產生主機設定。

### 常見錯誤訊息

以下是最常遇到的錯誤及其解決方法：

| 錯誤                     | 原因                              | 修復                                                          |
| ------------------------ | --------------------------------- | ------------------------------------------------------------- |
| 「瀏覽器擴充功能未連接」 | 原生訊息主機無法到達擴充功能      | 重新啟動 Chrome 和 Claude Code，然後執行 `/chrome` 以重新連接 |
| 「未偵測到擴充功能」     | Chrome 擴充功能未安裝或已停用     | 在 `chrome://extensions` 中安裝或啟用擴充功能                 |
| 「沒有可用的標籤頁」     | Claude 在標籤頁準備好之前嘗試操作 | 要求 Claude 建立新標籤頁並重試                                |
| 「接收端不存在」         | 擴充功能服務工作者進入閒置狀態    | 執行 `/chrome` 並選擇「重新連接擴充功能」                     |

## 另請參閱

- [電腦使用](https://code.claude.com/docs/zh-TW/computer-use)：當任務無法在瀏覽器中完成時控制原生 macOS 應用程式
- [在 VS Code 中使用 Claude Code](https://code.claude.com/docs/zh-TW/vs-code#automate-browser-tasks-with-chrome)：VS Code 擴充功能中的瀏覽器自動化
- [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference)：命令列標誌，包括 `--chrome`
- [常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)：更多使用 Claude Code 的方式
- [資料和隱私](https://code.claude.com/docs/zh-TW/data-usage)：Claude Code 如何處理您的資料
- [Claude in Chrome 入門](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome)：Chrome 擴充功能的完整文件，包括快捷鍵、排程和權限

是否 助手
