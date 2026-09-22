[Skip to main content](https://code.claude.com/docs/zh-TW/terminal-guide#content-area) 即使您從未使用過終端機，也可以使用 Claude Code。本指南將引導您開啟終端機、安裝 Claude Code 以及進行首次互動。

- [macOS 和 Linux](https://code.claude.com/docs/zh-TW/terminal-guide#macos-and-linux)
- [Windows](https://code.claude.com/docs/zh-TW/terminal-guide#windows)

不想使用終端機？Claude Code 桌面應用程式可讓您完全跳過終端機。下載 [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs) 或 [Windows](https://claude.com/download?utm_source=claude_code&utm_medium=docs) 版本，然後查看[桌面快速入門](https://code.claude.com/docs/zh-TW/desktop-quickstart)以開始使用。在 Linux 上，請按照 [Linux 安裝說明](https://code.claude.com/docs/zh-TW/desktop-linux)使用 apt 安裝應用程式。

## macOS 和 Linux

按照以下步驟從 macOS 或 Linux 終端機安裝並啟動 Claude Code。Claude Code 需要 macOS 13.0 或更新版本。請查看[系統需求](https://code.claude.com/docs/zh-TW/setup#system-requirements)以了解支援的 Linux 發行版。 1 開啟終端機 **macOS** ：按 `Cmd + Space` 開啟 Spotlight 搜尋，輸入 `Terminal`，然後按 `Enter`。**Linux** ：開啟您的終端機應用程式。在大多數發行版上，按 `Ctrl + Alt + T` 或在應用程式選單中搜尋’Terminal’。一個視窗將出現，顯示閃爍的游標。這就是您的終端機，您可以在此輸入命令。 2 安裝 Claude Code 複製此行，將其貼到您的終端機中（macOS 上按 `Cmd + V`，Linux 上按 `Ctrl + Shift + V`），然後按 `Enter`：

```
curl -fsSL https://claude.ai/install.sh | bash

```

這會從 claude.ai 下載並執行 Claude Code 安裝程式。您會看到文字滾動。完成後，您會看到「Claude Code successfully installed!」訊息。如果您看到錯誤，請查看下方的[疑難排解部分](https://code.claude.com/docs/zh-TW/terminal-guide#macos-and-linux-troubleshooting)。 3 啟動 Claude Code 輸入 `claude` 並按 `Enter`：

```
claude

```

如果您看到 `command not found: claude`，安裝目錄還未在您的 PATH 上。請按照下方的[’command not found: claude’](https://code.claude.com/docs/zh-TW/terminal-guide#macos-and-linux-troubleshooting)修復步驟，然後開啟新的終端機視窗並重試。系統會提示您使用 Claude 帳戶[登入](https://code.claude.com/docs/zh-TW/authentication)。按照螢幕上的指示進行。瀏覽器視窗將開啟供您登入。 4 開始使用 Claude Code 登入後，您可以開始詢問 Claude 有關您的程式碼或任何其他事項的問題。Claude Code 完全以文字形式執行。您輸入訊息並按 `Enter` 發送。以下是一些需要了解的事項：

- 您無法在終端機中點擊任何內容。使用箭頭鍵移動。
- 按 `Esc` 中斷 Claude（如果它正在執行）。
- 輸入 `exit` 或在空提示符上按 `Ctrl + D` 兩次以離開 Claude Code。
- 輸入 `/help` 以查看可用命令。

______________________________________________________________________

## Windows

按照以下步驟在 Windows 上選擇性地安裝 Git for Windows、設定 PowerShell 並啟動 Claude Code。Claude Code 需要 Windows 10 版本 1809 或更新版本。請查看[系統需求](https://code.claude.com/docs/zh-TW/setup#system-requirements)以了解完整詳細資訊。 1 安裝 Git for Windows（選擇性） Git for Windows 提供 Git Bash，可啟用 Bash 工具。沒有它，Claude Code 會改用 PowerShell。您不需要自己學習 Git。如果您還沒有安裝：

1. 前往 [git-scm.com/downloads/win](https://git-scm.com/downloads/win) 並下載安裝程式
1. 執行安裝程式。在每個畫面上點擊 Next 以接受預設值。安裝程式有許多畫面，但您不需要變更任何內容。
1. 如果它要求您選擇編輯器，保持預設值並點擊 Next。
1. 當您看到’Adjusting your PATH environment’時，保持建議的選項被選中。

已經有 Git？您可以跳過此步驟。如果您不確定，無論如何安裝它。重新安裝不會造成問題。 2 開啟 PowerShell PowerShell 是 Windows 內建的終端機，用於輸入命令。它預先安裝在每台 Windows 電腦上。按 `Win + X` 並從選單中選擇 **Windows PowerShell** （或 **Terminal** ）。一個帶有閃爍游標的視窗將出現。這是您輸入命令的地方。 Windows 有兩個命令列程式：PowerShell 和 CMD。它們看起來相似但使用不同的命令。確保您在 PowerShell 中進行下一步。判斷您在哪一個的方法：

- **PowerShell** ：在每行的開始顯示 `PS C:\Users\YourName>`
- **CMD** ：顯示 `C:\Users\YourName>`，沒有 `PS`

3 安裝 Claude Code 複製此行，使用 `Ctrl + V` 或右鍵點擊將其貼到 PowerShell 中，然後按 `Enter`：

```
irm https://claude.ai/install.ps1 | iex

```

這會下載並執行 Claude Code 安裝程式。`irm` 會擷取檔案，`iex` 會執行它。您會看到文字滾動。完成後，您會看到’Claude Code successfully installed!’訊息。如果您看到錯誤，請查看下方的[疑難排解部分](https://code.claude.com/docs/zh-TW/terminal-guide#windows-troubleshooting)。 如果您在 CMD 而不是 PowerShell 中，請使用此命令：

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```

4 啟動 Claude Code 執行 `claude`。如果 PowerShell 顯示 `'claude' is not recognized`，安裝目錄還不在您的 PATH 上。按照下方的 [‘claude is not recognized’](https://code.claude.com/docs/zh-TW/terminal-guide#windows-troubleshooting) 修復，然後開啟新的 PowerShell 視窗並再試一次。

```
claude

```

系統會提示您使用 Claude 帳戶[登入](https://code.claude.com/docs/zh-TW/authentication)。按照螢幕上的指示進行。瀏覽器視窗將開啟供您登入。 5 開始使用 Claude Code 登入後，您可以開始詢問 Claude 有關您的程式碼或任何其他事項的問題。Claude Code 完全以文字形式執行。您輸入訊息並按 `Enter` 發送。以下是一些需要了解的事項：

- 您無法在終端機中點擊任何內容。使用箭頭鍵移動。
- 按 `Esc` 中斷 Claude（如果它正在執行）。
- 輸入 `exit` 或按 `Ctrl + D` 兩次在空提示符上以離開 Claude Code。
- 輸入 `/help` 以查看可用命令。

______________________________________________________________________

## 接下來呢？

一旦您看到 Claude Code 歡迎畫面，您就可以開始了。您不需要知道如何編寫程式碼。用簡單的英文描述您想要的內容，Claude 會為您編寫程式碼。

### 建立一些東西

Claude 可以根據描述建立專案：

```
make me a simple webpage that says hello world

```

在建立或變更檔案之前，Claude 會要求您的許可。按 `Enter` 鍵選擇**是** 並核准。Claude 建立檔案後，雙擊 HTML 檔案以在瀏覽器中開啟它。

### 使用電腦上的檔案

Claude 可以讀取和組織您已有的檔案：

```
look at the screenshots on my Desktop and rename them based on what's in each image

```

### 提出問題

Claude 可以解釋事物、幫助您學習或規劃專案：

```
I want to build a personal budget tracker. What would I need?

```

如果您還沒有專案，沒關係。Claude 可以幫助您開始一個新專案。

### 使用 Claude Code 的其他方式

您不必使用終端機。Claude Code 也可在以下位置使用：

- [VS Code](https://code.claude.com/docs/zh-TW/vs-code) 和 [JetBrains IDE](https://code.claude.com/docs/zh-TW/jetbrains) 作為編輯器擴充功能
- [桌面應用程式](https://code.claude.com/docs/zh-TW/desktop-quickstart)，無需終端機
- [網頁](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)上的 claude.ai/code 用於遠端工作階段
- [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 和 [GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd) 用於自動化

### 深入了解

- [快速入門](https://code.claude.com/docs/zh-TW/quickstart)：Claude Code 首個專案的引導式逐步解說
- [Claude Code 如何運作](https://code.claude.com/docs/zh-TW/how-claude-code-works)：了解 Claude 如何讀取您的檔案、執行命令和進行編輯
- [最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)：透過有效的提示和專案設定獲得更好的結果
- [常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)：除錯、測試、重構等的逐步指南
- [終端機設定](https://code.claude.com/docs/zh-TW/terminal-config)：自訂您的終端機以獲得最佳 Claude Code 體驗

______________________________________________________________________

## 疑難排解

### macOS 和 Linux 疑難排解

如果您在 macOS 或 Linux 上安裝時遇到問題，請檢查這些常見問題： 'command not found: claude' 如果在安裝後看到 `command not found: claude`，安裝程式放置 `claude` 的資料夾不在您的 PATH 中。安裝程式在安裝結束時的 `Setup notes` 下列印了確切的修復方法，所以請執行該命令，或使用下面適用於您的 shell 的命令。對於 Zsh，macOS 預設 shell：

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

```

對於 Bash，Linux 預設 shell：

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

```

然後開啟新的終端機並再試一次 `claude`。如果仍然找不到，請檢查檔案 `~/.local/bin/claude` 是否存在。如果不存在，表示安裝未完成。如需更多詳細資訊，請參閱[修復您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)。 HTML 程式碼錯誤或 'syntax error near unexpected token' 如果您看到 `bash: line 1: syntax error near unexpected token '<'` 或終端機中出現 HTML 程式碼（如 `<!DOCTYPE html>`），安裝 URL 傳回的是網頁而不是安裝程式指令碼。如果頁面顯示’App unavailable in region’，Claude Code 在您的國家/地區不可用。請參閱[支援的國家/地區](https://www.anthropic.com/supported-countries)。否則，請嘗試再次執行命令。如果持續發生，請改用 [Homebrew](https://brew.sh) 安裝：

```
brew install --cask claude-code

```

完成後，開啟新的終端機視窗，輸入 `claude --version`，然後按 Enter：當安裝成功時，命令會列印版本號碼，例如 `2.1.211 (Claude Code)`。 'dyld' 錯誤或 'built for Mac OS X 13.0' 如果您看到 `dyld: cannot load`、`dyld: Symbol not found` 或 `built for Mac OS X 13.0`，您的 macOS 版本可能比 Claude Code 支援的版本更舊。開啟 Apple 選單並選擇「About This Mac」以檢查您的版本。如果它比 13.0 更舊，請透過軟體更新更新 macOS。請參閱 [macOS 疑難排解指南](https://code.claude.com/docs/zh-TW/troubleshoot-install#dyld-cannot-load-on-macos)以了解更多詳細資訊。 如需其他錯誤，請參閱完整的[安裝疑難排解指南](https://code.claude.com/docs/zh-TW/troubleshoot-install)。

### Windows 疑難排解

如果您在 Windows 上安裝時遇到問題，請檢查這些常見問題： 'irm is not recognized' 您在 CMD 中，而不是 PowerShell。關閉此視窗並改為開啟 PowerShell（`Win + X` 然後選擇 Windows PowerShell）。或者，使用 CMD 安裝命令：

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```

SSL/TLS 錯誤或 'Could not create SSL/TLS secure channel' 這通常發生在較舊的 Windows 10 系統上。先執行此行，然後重試安裝：

```
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
irm https://claude.ai/install.ps1 | iex

```

'Claude Code on Windows requires either Git for Windows (for bash) or PowerShell' 找不到 PowerShell 或 Git Bash。Claude Code 需要至少一個 shell。

1. 確保 `powershell.exe` 在您的 `PATH` 上。其預設位置是 `C:\Windows\System32\WindowsPowerShell\v1.0\`。或者，安裝 [PowerShell 7](https://aka.ms/powershell)，它提供 `pwsh`。
1. 如果您寧願使用 Git Bash，請安裝 [Git for Windows](https://git-scm.com/downloads/win)，按照 [Windows 部分的第一步](https://code.claude.com/docs/zh-TW/terminal-guide#windows)。
1. 如果已安裝 Git 但 Claude Code 找不到它，請告訴它在哪裡查找：

```
$env:CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"

```

然後再次執行 `claude`。如果您的 Git 安裝在其他地方，請透過執行以下命令找到路徑：

```
Get-Command git | Select-Object Source

```

在該路徑中查找 `Git\bin` 資料夾並改用它。

要使其永久化，以便您不必每次都設定它，請參閱[設定 Git Bash 路徑](https://code.claude.com/docs/zh-TW/troubleshoot-install#claude-code-on-windows-requires-either-git-for-windows-for-bash-or-powershell)。 'claude is not recognized' 此錯誤表示安裝目錄不在您的 PATH 中。在 PowerShell 中執行這些命令以新增它：

```
$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
[Environment]::SetEnvironmentVariable('PATH', "$currentPath;$env:USERPROFILE\.local\bin", 'User')

```

關閉 PowerShell，開啟新視窗，然後再試一次 `claude`。您應該會看到 Claude Code 歡迎畫面。請參閱[驗證您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)以了解更多詳細資訊。 'Claude Code does not support 32-bit Windows' 在 64 位元機器上，此錯誤表示您開啟了 `Windows PowerShell (x86)` 而不是 `Windows PowerShell`。x86 項目以 32 位元程序執行。關閉它，開啟「開始」選單項目（名稱中沒有 `(x86)`），然後再次執行安裝命令。如果您不確定您的機器是否為 64 位元，或錯誤仍然存在，請參閱[完整說明](https://code.claude.com/docs/zh-TW/troubleshoot-install#claude-code-does-not-support-32-bit-windows)。 如需其他錯誤，請參閱完整的[安裝疑難排解指南](https://code.claude.com/docs/zh-TW/troubleshoot-install)。 Was this page helpful? YesNo Assistant Responses are generated using AI and may contain mistakes.
