本快速入門指南將在幾分鐘內讓您使用 AI 驅動的編碼協助。完成後，您將了解如何使用 Claude Code 進行常見的開發任務。

## 開始前

確保您擁有：

- 已開啟的終端或命令提示字元
  - 如果您從未使用過終端，請查看[終端指南](https://code.claude.com/docs/zh-TW/terminal-guide)
- 一個可以使用的程式碼專案
- 一個 [Claude 訂閱](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=quickstart_prereq)（Pro、Max、Team 或 Enterprise）、[Claude Console](https://platform.claude.com/) 帳戶，或透過[支援的雲端提供商](https://code.claude.com/docs/zh-TW/third-party-integrations)存取

本指南涵蓋終端 CLI。Claude Code 也可在[網頁](https://claude.ai/code)、[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop)、[VS Code](https://code.claude.com/docs/zh-TW/vs-code) 和 [JetBrains IDE](https://code.claude.com/docs/zh-TW/jetbrains)、[Slack](https://code.claude.com/docs/zh-TW/slack) 中使用，以及透過 [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 和 [GitLab](https://code.claude.com/docs/zh-TW/gitlab-ci-cd) 進行 CI/CD。請參閱[所有介面](https://code.claude.com/docs/zh-TW/overview#use-claude-code-everywhere)。

## 步驟 1：安裝 Claude Code

若要安裝 Claude Code，請使用下列其中一種方法：

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

WinGet 安裝不會自動更新。定期執行 `winget upgrade Anthropic.ClaudeCode` 以取得最新功能和安全修正。 您也可以在 Debian、Fedora、RHEL 和 Alpine 上使用 [apt、dnf 或 apk](https://code.claude.com/docs/zh-TW/setup#install-with-linux-package-managers) 進行安裝。 若要確認安裝成功，請執行：

```
claude --version

```

此命令會列印版本號碼，後面跟著 `(Claude Code)`。

## 步驟 2：登入您的帳戶

Claude Code 需要帳戶才能使用。使用 `claude` 命令啟動互動式工作階段，首次使用時系統會提示您登入：

```
claude

```

對於 Claude 訂閱或 Console 帳戶，請按照提示在瀏覽器中完成驗證。如果您已設定 `ANTHROPIC_API_KEY` 環境變數，Claude Code 會略過登入提示，改為要求您核准該金鑰。若要稍後切換帳戶或重新驗證，請在執行中的工作階段內輸入 `/login`：

```
/login

```

您可以使用以下任何帳戶類型登入：

- [Claude Pro、Max、Team 或 Enterprise](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=quickstart_login)（推薦）
- [Claude Console](https://platform.claude.com/)（具有預付額度的 API 存取）。首次登入時，Console 中會自動建立「Claude Code」工作區以進行集中成本追蹤。
- [Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry](https://code.claude.com/docs/zh-TW/third-party-integrations)（企業雲端提供商）
- 自行託管的 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)（如果您的組織執行一個的話）：您的管理員會預先設定閘道 URL，`/login` 會直接在 **Cloud gateway** 畫面上開啟，供您使用公司 SSO 登入

登入後，您的認證將被儲存，您無需再次登入。深入瞭解 [認證管理](https://code.claude.com/docs/zh-TW/authentication#credential-management)。

## 步驟 3：啟動您的第一個工作階段

在任何專案目錄中開啟您的終端並啟動 Claude Code：

```
cd /path/to/your/project
claude

```

將 `/path/to/your/project` 替換為您要處理的專案路徑。 您將看到 Claude Code 提示，其中顯示版本、目前的模型和工作目錄。輸入 `/help` 以查看可用命令，或輸入 `/resume` 以繼續之前的對話。

## 步驟 4：提出您的第一個問題

讓我們從了解您的程式碼庫開始。嘗試以下命令之一：

```
what does this project do?

```

Claude 將分析您的檔案並提供摘要。您也可以提出更具體的問題：

```
what technologies does this project use?

```

```
where is the main entry point?

```

```
explain the folder structure

```

您也可以詢問 Claude 其自身的功能：

```
what can Claude Code do?

```

```
how do I create custom skills in Claude Code?

```

```
can Claude Code work with Docker?

```

Claude Code 會根據需要讀取您的專案檔案。您無需手動新增內容。

## 步驟 5：進行您的第一次程式碼變更

現在讓我們讓 Claude Code 進行一些實際的編碼。嘗試一個簡單的任務：

```
add a hello world function to the main file

```

Claude Code 找到適當的檔案並向您顯示變更。如果它在進行變更前詢問，請選擇 **是** 以批准。 Auto mode 是 [內建的起始權限模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)，適用於 Pro、Max 和 Team 方案上的互動式終端工作階段：分類器會檢查動作而不是由您檢查，Claude 可以在不詢問的情況下編輯大多數檔案並執行大多數命令。在其他方案上，Manual mode 是內建的起始權限模式。對於您安裝後立即開始的工作階段，請參閱 [安裝或升級後的第一個工作階段](https://code.claude.com/docs/zh-TW/env-vars#first-session-after-an-install-or-upgrade)。 您的設定或您的組織可以設定不同的起始權限模式。[工作階段開始時的權限模式](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in) 列出了相關內容。隨時按 `Shift+Tab` 以切換您所在工作階段的權限模式。

## 步驟 6：使用 Git 與 Claude Code

Claude Code 使 Git 操作變得對話式：

```
what files have I changed?

```

```
commit my changes with a descriptive message

```

您也可以提示進行更複雜的 Git 操作：

```
create a new branch called feature/quickstart

```

```
show me the last 5 commits

```

```
help me resolve merge conflicts

```

## 步驟 7：修復錯誤或新增功能

Claude 擅長除錯和功能實現。 用自然語言描述您想要的內容：

```
add input validation to the user registration form

```

或修復現有問題：

```
there's a bug where users can submit empty forms - fix it

```

Claude Code 將：

- 定位相關程式碼
- 理解上下文
- 實現解決方案
- 如果可用，執行測試

## 步驟 8：測試其他常見工作流程

有許多方式可以與 Claude 合作： **重構程式碼**

```
refactor the authentication module to use async/await instead of callbacks

```

**編寫測試**

```
write unit tests for the calculator functions

```

**更新文件**

```
update the README with installation instructions

```

**程式碼審查**

```
review my changes and suggest improvements

```

像與有幫助的同事交談一樣與 Claude 交談。描述您想要達成的目標，它將幫助您實現。

## 基本命令

以下是日常使用中最重要的命令。Shell 命令從您的終端機執行以啟動或繼續 Claude Code。工作階段命令在 Claude Code 啟動後在其內部執行。 **Shell 命令**

| 命令                                                                                                                                                                                       | 功能                       | 範例                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- | ----------------------------------- |
| `claude`                                                                                                                                                                                   | 啟動互動模式               | `claude`                            |
| `claude "task"`                                                                                                                                                                            | 使用初始提示啟動互動模式   | `claude "fix the build error"`      |
| `claude -p "query"`                                                                                                                                                                        | 執行一次性查詢，然後退出   | `claude -p "explain this function"` |
| `claude -c`                                                                                                                                                                                | 在目前目錄中繼續最近的對話 | `claude -c`                         |
| `claude -r`                                                                                                                                                                                | 恢復之前的對話             | `claude -r`                         |
| **工作階段命令**                                                                                                                                                                           |                            |                                     |
| 命令                                                                                                                                                                                       | 功能                       | 範例                                |
| ---                                                                                                                                                                                        | ---                        | ---                                 |
| `/clear`                                                                                                                                                                                   | 清除對話歷史               | `/clear`                            |
| `/help`                                                                                                                                                                                    | 顯示可用命令               | `/help`                             |
| `/exit` 或 Ctrl+D 兩次                                                                                                                                                                     | 退出 Claude Code           | `/exit`                             |
| 請參閱 [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference)以取得完整的 shell 命令清單，以及 [命令參考](https://code.claude.com/docs/zh-TW/commands)以取得完整的工作階段命令清單。 |                            |                                     |

## 初學者的專業提示

如需更多資訊，請參閱[最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)和[常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)。 對您的請求要具體 不要這樣做：“修復錯誤”試試這樣：“修復登入錯誤，使用者輸入錯誤認證後看到空白畫面” 使用逐步說明 將複雜任務分解為步驟：

```
1. create a new database table for user profiles
2. create an API endpoint to get and update user profiles
3. build a webpage that allows users to see and edit their information

```

讓 Claude 先探索 在進行變更之前，讓 Claude 了解您的程式碼：

```
analyze the database schema

```

```
build a dashboard showing products that are most frequently returned by our UK customers

```

使用快捷方式節省時間

- 輸入 `/` 查看所有命令和 skills
- 使用 Tab 進行命令完成
- 按 ↑ 查看命令歷史
- 按 `Shift+Tab` 循環切換權限模式

## 接下來呢？

現在您已經學習了基礎知識，請探索更多進階功能：

## [Claude Code 如何運作 了解代理迴圈、內建工具以及 Claude Code 如何與您的專案互動 ](https://code.claude.com/docs/zh-TW/how-claude-code-works)

## [最佳實踐 透過有效的提示和專案設定獲得更好的結果 ](https://code.claude.com/docs/zh-TW/best-practices)

## [常見工作流程 常見任務的逐步指南 ](https://code.claude.com/docs/zh-TW/common-workflows)

## [擴展 Claude Code 使用 CLAUDE.md、skills、hooks、MCP 等進行自訂 ](https://code.claude.com/docs/zh-TW/features-overview)

## 獲取幫助

- **在 Claude Code 中** ：輸入 `/help` 或詢問「how do I…」
- **文件** ：您在這裡！瀏覽其他指南
- **社群** ：加入我們的 [Discord](https://www.anthropic.com/discord) 以獲取提示和支援

是否 助手
