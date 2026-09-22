Claude Code 是一個由 AI 驅動的編碼助手，可幫助您建立功能、修復錯誤和自動化開發任務。它理解您的整個程式碼庫，並可以跨多個檔案和工具工作以完成任務。

## 開始使用

Claude Code 在多個平台上執行：終端機、IDE 擴充功能、桌面應用程式和網頁。從下方的標籤中選擇一個以開始使用。大多數平台需要 [Claude 訂閱](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=overview_pricing)或 [Anthropic Console](https://platform.claude.com/) 帳戶。終端機 CLI、VS Code 和 JetBrains 也支援[第三方提供商](https://code.claude.com/docs/zh-TW/third-party-integrations)。

- 終端機
- VS Code
- 桌面應用程式
- 網頁
- JetBrains

功能完整的 CLI，用於直接在您的終端機中使用 Claude Code。編輯檔案、執行命令，並從命令列管理您的整個專案。若要安裝 Claude Code，請使用下列其中一種方法：

- 原生安裝（建議）
- Homebrew
- WinGet

**macOS、Linux、WSL：**

```
curl -fsSL https://claude.ai/install.sh | bash

```

**Windows PowerShell：**

```
irm https://claude.ai/install.ps1 | iex

```

**Windows CMD：**

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```

如果您看到 `The token '&&' is not a valid statement separator`，表示您在 PowerShell 中，而非 CMD。如果您看到 `'irm' is not recognized as an internal or external command`，表示您在 CMD 中，而非 PowerShell。當您在 PowerShell 中時，提示符會顯示 `PS C:\`，而在 CMD 中時會顯示 `C:\`（不含 `PS`）。如果安裝命令失敗並出現 `syntax error near unexpected token '<'`、`403` 或其他 curl 錯誤，請參閱[疑難排解安裝](https://code.claude.com/docs/zh-TW/troubleshoot-install#find-your-error)以將錯誤與修正相對應，並查看替代安裝方法。建議在原生 Windows 上安裝 [Git for Windows](https://git-scm.com/downloads/win)，以便 Claude Code 可以使用 Bash 工具。如果未安裝 Git for Windows，Claude Code 會改用 PowerShell 作為殼層工具。WSL 設定不需要 Git for Windows。 原生安裝會在背景自動更新，以保持您使用最新版本。

```
brew install --cask claude-code

```

Homebrew 提供兩個 casks。`claude-code` 追蹤穩定版本通道，通常比最新版本晚約一週，並跳過有重大迴歸的版本。`claude-code@latest` 追蹤最新通道，並在新版本發佈時立即接收。 Homebrew 安裝不會自動更新。執行 `brew upgrade claude-code` 或 `brew upgrade claude-code@latest`（取決於您安裝的 cask），以取得最新功能和安全修正。

```
winget install Anthropic.ClaudeCode

```

WinGet 安裝不會自動更新。定期執行 `winget upgrade Anthropic.ClaudeCode` 以取得最新功能和安全修正。 您也可以在 Debian、Fedora、RHEL 和 Alpine 上使用 [apt、dnf 或 apk](https://code.claude.com/docs/zh-TW/setup#install-with-linux-package-managers) 進行安裝。然後在任何專案中啟動 Claude Code。將 `your-project` 替換為您機器上的專案目錄路徑：

```
cd your-project
claude

```

首次使用時，系統會提示您登入。如果您已設定 `ANTHROPIC_API_KEY` 環境變數，Claude Code 會跳過登入提示，改為要求您核准該金鑰。就這麼簡單！[繼續進行快速入門 →](https://code.claude.com/docs/zh-TW/quickstart) 請參閱[進階設定](https://code.claude.com/docs/zh-TW/setup)以了解安裝選項、手動更新或卸載說明。如果遇到問題，請造訪[安裝疑難排解](https://code.claude.com/docs/zh-TW/troubleshoot-install)。 VS Code 擴充功能在您的編輯器中直接提供內嵌差異、@-提及、計畫審查和對話歷史記錄。

- [安裝 VS Code](vscode:extension/anthropic.claude-code)
- [安裝 Cursor](cursor:extension/anthropic.claude-code)

或在擴充功能檢視中搜尋「Claude Code」（Mac 上為 `Cmd+Shift+X`，Windows/Linux 上為 `Ctrl+Shift+X`）。安裝後，開啟命令選擇板（`Cmd+Shift+P` / `Ctrl+Shift+P`），輸入「Claude Code」，然後選擇**在新標籤中開啟** 。[開始使用 VS Code →](https://code.claude.com/docs/zh-TW/vs-code#get-started) 一個獨立應用程式，用於在 IDE 或終端機外執行 Claude Code。以視覺方式審查差異、並排執行多個工作階段、排程重複任務，以及啟動雲端工作階段。下載並安裝：

- [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs)（Intel 和 Apple Silicon）
- [Windows](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)（x64）
- [Windows ARM64](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)
- 在 Ubuntu 或 Debian 上，應用程式處於測試版，請按照 [Linux 安裝說明](https://code.claude.com/docs/zh-TW/desktop-linux)使用 apt 安裝

安裝後，啟動 Claude，登入，然後按一下**程式碼** 標籤以開始編碼。應用程式包含 Claude Code，因此您無需單獨安裝 CLI。需要[付費訂閱](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=overview_desktop_pricing)。[深入了解桌面應用程式 →](https://code.claude.com/docs/zh-TW/desktop-quickstart) 在您的瀏覽器中執行 Claude Code，無需本機設定。啟動長時間執行的任務，並在完成時檢查，處理您本機沒有的儲存庫，或並行執行多個任務。如需較長期的工作，請建立[專案](https://code.claude.com/docs/zh-TW/claude-projects)，讓 Claude 為您協調平行工作階段。可在桌面瀏覽器和 [Claude iOS 和 Android 應用程式](https://code.claude.com/docs/zh-TW/mobile)上使用。在 [claude.ai/code](https://claude.ai/code) 開始編碼。[開始在網頁上使用 →](https://code.claude.com/docs/zh-TW/web-quickstart) IntelliJ IDEA、PyCharm、WebStorm 和其他 JetBrains IDE 的外掛程式，具有互動式差異檢視和選擇內容共享。從 JetBrains Marketplace 安裝 [Claude Code 外掛程式](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-)，然後重新啟動您的 IDE。外掛程式需要單獨安裝的 Claude Code CLI；請參閱 [JetBrains 設定步驟](https://code.claude.com/docs/zh-TW/jetbrains#installation)。[開始使用 JetBrains →](https://code.claude.com/docs/zh-TW/jetbrains)

## 您可以做什麼

以下是您可以使用 Claude Code 的一些方式： 自動化您一直在推遲的工作 Claude Code 處理佔用您一整天的繁瑣任務：為未測試的程式碼編寫測試、修復整個專案中的 lint 錯誤、解決合併衝突、更新依賴項和編寫發行說明。

```
claude "write tests for the auth module, run them, and fix any failures"

```

建立功能和修復錯誤 用純文字描述您想要的內容。Claude Code 規劃方法、跨多個檔案編寫程式碼，並驗證其是否有效。對於錯誤，貼上錯誤訊息或描述症狀。Claude Code 透過您的程式碼庫追蹤問題、識別根本原因並實施修復。請參閱[常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)以了解更多範例。 建立提交和拉取請求 Claude Code 直接與 git 配合使用。它暫存變更、編寫提交訊息、建立分支並開啟拉取請求。

```
claude "commit my changes with a descriptive message"

```

在 CI 中，您可以使用 [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 或 [GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd) 自動化程式碼審查和問題分類。 使用 MCP 連接您的工具 [Model Context Protocol (MCP)](https://code.claude.com/docs/zh-TW/mcp) 是一個開放標準，用於將 AI 工具連接到外部資料來源。使用 MCP，Claude Code 可以讀取 Google Drive 中的設計文件、更新 Jira 中的票證、從 Slack 提取資料，或使用您自己的自訂工具。[MCP 快速入門](https://code.claude.com/docs/zh-TW/mcp-quickstart)端到端連接您的第一個伺服器。 使用說明、skills 和 hooks 進行自訂 [`CLAUDE.md`](https://code.claude.com/docs/zh-TW/memory) 是您新增到專案根目錄的 markdown 檔案，Claude Code 在每個工作階段開始時都會讀取。使用它來設定編碼標準、架構決策、首選程式庫和審查檢查清單。如果您的儲存庫已經有用於其他編碼代理的 `AGENTS.md`，Claude Code [可以自行讀取](https://code.claude.com/docs/zh-TW/memory#agents-md)或與 `CLAUDE.md` 一起讀取。Claude 也會在工作時建立[自動記憶](https://code.claude.com/docs/zh-TW/memory#auto-memory)，儲存學習內容，跨工作階段而無需您編寫任何內容。建立[skills](https://code.claude.com/docs/zh-TW/skills) 以封裝您的團隊可以共享的可重複工作流程，例如 `/review-pr` 或 `/deploy-staging`。[Hooks](https://code.claude.com/docs/zh-TW/hooks) 可讓您在 Claude Code 動作之前或之後執行 shell 命令，例如在每次檔案編輯後自動格式化或在提交前執行 lint。 執行代理團隊並建立自訂代理 生成[多個 Claude Code 代理](https://code.claude.com/docs/zh-TW/sub-agents)，同時處理任務的不同部分。主導代理協調工作、指派子任務並合併結果。若要在平行執行多個完整工作階段並從一個螢幕監視它們，請使用[背景代理](https://code.claude.com/docs/zh-TW/agent-view)。對於完全自訂的工作流程，[Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 可讓您建立由 Claude Code 的工具和功能驅動的自己的代理，並完全控制編排、工具存取和權限。 使用 CLI 進行管道、指令碼和自動化 Claude Code 是可組合的，遵循 Unix 哲學。將日誌管道傳入其中、在 CI 中執行它，或將其與其他工具鏈接：

```
# 分析最近的日誌輸出
tail -200 app.log | claude -p "Slack me if you see any anomalies"

# 在 CI 中自動化翻譯
claude -p "translate new strings into French and raise a PR for review"

# 跨檔案的大量操作
git diff main --name-only | claude -p "review these changed files for security issues"

```

請參閱 [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference)以了解完整的命令和旗標集。 排程重複任務 按排程執行 Claude 以自動化重複的工作：早上 PR 審查、隔夜 CI 失敗分析、每週依賴項審計或在 PR 合併後同步文件。

- [Routines](https://code.claude.com/docs/zh-TW/routines) 在雲端執行，因此即使您的電腦關閉，它們也會繼續執行。它們也可以在 API 呼叫或 GitHub 事件上觸發。從網頁、桌面應用程式或在 CLI 中執行 `/schedule` 來建立它們。
- [桌面排程任務](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)在您的機器上執行，可直接存取您的本機檔案和工具
- [`/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks) 在 CLI 工作階段中重複提示以進行快速輪詢

從任何地方工作 工作階段不受限於單一介面。當您的內容變更時，在環境之間移動工作：

- 離開您的辦公桌，使用[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)從您的手機或任何瀏覽器繼續工作
- 從您的手機向 [Dispatch](https://code.claude.com/docs/zh-TW/desktop#sessions-from-dispatch) 傳送任務，並開啟它建立的桌面工作階段
- 在[網頁](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)或 [Claude 行動應用程式](https://code.claude.com/docs/zh-TW/mobile)上啟動長時間執行的任務，然後使用 `claude --teleport` 將其提取到您的終端機中。Teleport 需要 claude.ai 訂閱。
- 執行 `/desktop` 以在[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop)中繼續您目前的終端機工作階段，您可以在其中以視覺方式審查差異。`/desktop` 交付需要 claude.ai 訂閱。適用於 macOS 和 x64 Windows。
- 從團隊聊天路由任務：在 [Slack](https://code.claude.com/docs/zh-TW/slack) 中提及 `@Claude` 並提供錯誤報告，然後取回拉取請求

## 在任何地方使用 Claude Code

每個[介面](https://code.claude.com/docs/zh-TW/glossary#surface)都連接到相同的基礎 Claude Code 引擎，因此您的 CLAUDE.md 檔案、設定和 MCP servers 可在所有介面中工作。 除了上述[終端機](https://code.claude.com/docs/zh-TW/quickstart)、[VS Code](https://code.claude.com/docs/zh-TW/vs-code)、[JetBrains](https://code.claude.com/docs/zh-TW/jetbrains)、[桌面](https://code.claude.com/docs/zh-TW/desktop)和[網頁](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)環境外，Claude Code 還與 CI/CD、聊天和瀏覽器工作流程整合：

| 我想要…                                                               | 最佳選項                                                                                                                                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 從我的手機或其他裝置繼續本機工作階段                                  | [遠端控制](https://code.claude.com/docs/zh-TW/remote-control)                                                                                                                   |
| 從 Telegram、Discord、iMessage 或我自己的 webhooks 推送事件到工作階段 | [Channels](https://code.claude.com/docs/zh-TW/channels)                                                                                                                         |
| 在本機啟動任務，在行動裝置上繼續                                      | [`claude --cloud`](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud)，然後使用 [Claude 行動應用程式](https://code.claude.com/docs/zh-TW/mobile) |
| 按重複排程執行 Claude                                                 | [Routines](https://code.claude.com/docs/zh-TW/routines) 或[桌面排程任務](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)                                            |
| 自動化 PR 審查和問題分類                                              | [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 或 [GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd)                                          |
| 在每個 PR 上獲得自動程式碼審查                                        | [GitHub Code Review](https://code.claude.com/docs/zh-TW/code-review)                                                                                                            |
| 將 Slack 中的錯誤報告路由到拉取請求                                   | [Slack](https://code.claude.com/docs/zh-TW/slack)                                                                                                                               |
| 除錯即時網頁應用程式                                                  | [Chrome](https://code.claude.com/docs/zh-TW/chrome)                                                                                                                             |
| 為您自己的工作流程建立自訂代理                                        | [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview)                                                                                                              |

## 後續步驟

安裝 Claude Code 後，這些指南可幫助您深入了解。

- [快速入門](https://code.claude.com/docs/zh-TW/quickstart)：逐步完成您的第一個真實任務，從探索程式碼庫到提交修復
- [儲存說明和記憶](https://code.claude.com/docs/zh-TW/memory)：使用 CLAUDE.md 檔案和自動記憶為 Claude 提供持久說明
- [常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)和[最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)：充分利用 Claude Code 的模式
- [每項任務的工具](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)：Claude Code 團隊如何使用[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)大規模協調子代理
- [設定](https://code.claude.com/docs/zh-TW/settings)：為您的工作流程自訂 Claude Code
- [疑難排解](https://code.claude.com/docs/zh-TW/troubleshooting)：常見問題的解決方案
- [code.claude.com](https://code.claude.com/)：演示、定價和產品詳細資訊

是否 助手
