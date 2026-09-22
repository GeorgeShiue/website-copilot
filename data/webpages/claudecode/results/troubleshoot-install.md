如果安裝失敗或無法登入，請在下方找到您的錯誤。如需 Claude Code 正常運作後的執行時問題，請參閱[排除故障](https://code.claude.com/docs/zh-TW/troubleshooting)。如需設定問題（例如設定未套用或 hooks 未觸發），請參閱[偵錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config)。

## 找到您的錯誤

將您看到的錯誤訊息或症狀與修復方案相符：

| 您看到的內容                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 解決方案                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `command not found: claude` 或 `'claude' is not recognized`                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | [修復您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#command-not-found-claude-after-installation)                                                                          |
| `syntax error near unexpected token '<'`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | [安裝指令碼傳回 HTML](https://code.claude.com/docs/zh-TW/troubleshoot-install#install-script-returns-html-instead-of-a-shell-script)                                                          |
| `curl: (22) The requested URL returned error: 403`                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | [安裝指令碼傳回 403](https://code.claude.com/docs/zh-TW/troubleshoot-install#install-script-returns-html-instead-of-a-shell-script)                                                           |
| `curl: (23)` 或 `curl: (56) Failure writing output to destination`                                                                                                                                                                                                                                                                                                                                                                                                                                                          | [檢查連線或使用替代安裝程式](https://code.claude.com/docs/zh-TW/troubleshoot-install#curl-56-failure-writing-output-to-destination)                                                           |
| Linux 上安裝期間 `Killed`，或 `Installation was killed before it could finish (exit code 137)`                                                                                                                                                                                                                                                                                                                                                                                                                              | [釋放記憶體或新增交換空間](https://code.claude.com/docs/zh-TW/troubleshoot-install#install-killed-on-low-memory-linux-servers)                                                                |
| `Raw mode is not supported` 安裝期間                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | [重新執行安裝程式](https://code.claude.com/docs/zh-TW/troubleshoot-install#raw-mode-is-not-supported-during-install)                                                                          |
| `TLS connect error` 或 `SSL/TLS secure channel`                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | [更新 CA 憑證](https://code.claude.com/docs/zh-TW/troubleshoot-install#tls-or-ssl-connection-errors)                                                                                          |
| `Failed to fetch version` 或無法連線到下載伺服器                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [檢查網路和代理設定](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-network-connectivity)                                                                                      |
| `irm is not recognized` 或 `&& is not valid`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | [在您的 shell 上使用正確的命令](https://code.claude.com/docs/zh-TW/troubleshoot-install#wrong-install-command-on-windows)                                                                     |
| `Cask 'claude-code' is unavailable: No Cask with this name exists`                                                                                                                                                                                                                                                                                                                                                                                                                                                          | [更新 Homebrew](https://code.claude.com/docs/zh-TW/troubleshoot-install#homebrew-cask-unavailable-or-outdated)                                                                                |
| `'bash' is not recognized as the name of a cmdlet`                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | [使用 Windows 安裝程式命令](https://code.claude.com/docs/zh-TW/troubleshoot-install#wrong-install-command-on-windows)                                                                         |
| `A parameter cannot be found that matches parameter name 'fsSL'`                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [使用 Windows 安裝程式命令](https://code.claude.com/docs/zh-TW/troubleshoot-install#wrong-install-command-on-windows)                                                                         |
| `Claude Code on Windows requires either Git for Windows (for bash) or PowerShell`                                                                                                                                                                                                                                                                                                                                                                                                                                           | [安裝 shell](https://code.claude.com/docs/zh-TW/troubleshoot-install#claude-code-on-windows-requires-either-git-for-windows-for-bash-or-powershell)                                           |
| `Claude Code does not support 32-bit Windows`                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | [開啟 Windows PowerShell，而非 x86 項目](https://code.claude.com/docs/zh-TW/troubleshoot-install#claude-code-does-not-support-32-bit-windows)                                                 |
| `The process cannot access the file ... because it is being used by another process`                                                                                                                                                                                                                                                                                                                                                                                                                                        | [清除下載資料夾並重試](https://code.claude.com/docs/zh-TW/troubleshoot-install#the-process-cannot-access-the-file-during-windows-install)                                                     |
| `Error loading shared library`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | [您的系統的二進位變體錯誤](https://code.claude.com/docs/zh-TW/troubleshoot-install#linux-musl-or-glibc-binary-mismatch)                                                                       |
| `Illegal instruction`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | [架構或 CPU 指令集不相符](https://code.claude.com/docs/zh-TW/troubleshoot-install#illegal-instruction)                                                                                        |
| WSL 中的 `cannot execute binary file: Exec format error`                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | [WSL1 原生二進位回歸](https://code.claude.com/docs/zh-TW/troubleshoot-install#exec-format-error-on-wsl1)                                                                                      |
| PowerShell 安裝程式完成但找不到 `claude` 或顯示舊版本                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | [新增安裝目錄到您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)，然後開啟新的終端                                                                         |
| macOS 上的 `dyld: Symbol not found`、`dyld: cannot load` 或 `Abort trap`                                                                                                                                                                                                                                                                                                                                                                                                                                                    | [二進位不相容](https://code.claude.com/docs/zh-TW/troubleshoot-install#dyld-cannot-load-on-macos)                                                                                             |
| `claude update` 在 `Checking for updates` 後掛起，或 `claude doctor` 掛起且無輸出                                                                                                                                                                                                                                                                                                                                                                                                                                           | [移動 shell 設定路徑上的目錄](https://code.claude.com/docs/zh-TW/troubleshoot-install#claude-update-or-claude-doctor-hangs)                                                                   |
| `Invoke-Expression` 或 `iex` 解析錯誤引用 HTML 標籤或 CSS，或 `ParserError` 搭配 `ParseException`                                                                                                                                                                                                                                                                                                                                                                                                                           | [安裝指令碼傳回 HTML](https://code.claude.com/docs/zh-TW/troubleshoot-install#install-script-returns-html-instead-of-a-shell-script)                                                          |
| `running scripts is disabled on this system` 或 `PSSecurityException`                                                                                                                                                                                                                                                                                                                                                                                                                                                       | [允許 npm shims 執行](https://code.claude.com/docs/zh-TW/troubleshoot-install#running-scripts-is-disabled-on-this-system)                                                                     |
| `Error: claude native binary not installed`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | [完成 npm 安裝](https://code.claude.com/docs/zh-TW/troubleshoot-install#native-binary-not-found-after-npm-install)                                                                            |
| `npm error code ENOTEMPTY` 在更新或重新安裝期間                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | [移除剩餘的套件目錄](https://code.claude.com/docs/zh-TW/troubleshoot-install#npm-enotempty-during-update-or-reinstall)                                                                        |
| 在 Windows 上，安裝命令列印指令碼文字且未安裝任何內容                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | [執行完整的安裝命令](https://code.claude.com/docs/zh-TW/troubleshoot-install#wrong-install-command-on-windows)                                                                                |
| `App unavailable in region`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Claude Code 在您的國家/地區不可用。請參閱[支援的國家/地區](https://www.anthropic.com/supported-countries)。                                                                                   |
| `unable to get local issuer certificate`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | [設定公司 CA 憑證](https://code.claude.com/docs/zh-TW/troubleshoot-install#tls-or-ssl-connection-errors)                                                                                      |
| `OAuth error` 或 `403 Forbidden`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [修復身份驗證](https://code.claude.com/docs/zh-TW/troubleshoot-install#login-and-authentication)                                                                                              |
| 設定期間 `Unable to connect to Anthropic services`                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 請參閱錯誤參考中的 [Unable to connect to Anthropic services](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-anthropic-services)                                               |
| `Could not load the default credentials` 或 `Could not load credentials from any providers`                                                                                                                                                                                                                                                                                                                                                                                                                                 | [Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 認證](https://code.claude.com/docs/zh-TW/troubleshoot-install#bedrock-agent-platform-or-foundry-credentials-not-loading) |
| `ChainedTokenCredential authentication failed` 或 `CredentialUnavailableError`                                                                                                                                                                                                                                                                                                                                                                                                                                              | [Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 認證](https://code.claude.com/docs/zh-TW/troubleshoot-install#bedrock-agent-platform-or-foundry-credentials-not-loading) |
| `API Error: 500`、`529 Overloaded`、`429` 或上面未列出的其他 4xx 和 5xx 錯誤                                                                                                                                                                                                                                                                                                                                                                                                                                                | 請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors)                                                                                                                                   |
| 如果您的問題未列出，請執行下面的診斷檢查以縮小原因範圍。                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                               |
| 如果您寧願完全跳過終端，[Claude Code Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop-quickstart)可讓您透過圖形介面安裝和使用 Claude Code。下載適用於 [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs) 或 [Windows](https://claude.com/download?utm_source=claude_code&utm_medium=docs) 的版本，無需任何命令列設定即可開始編碼。在 Linux 上，請按照 [Linux 安裝說明](https://code.claude.com/docs/zh-TW/desktop-linux)使用 apt 安裝應用程式。 |                                                                                                                                                                                               |

## 執行診斷檢查

### 檢查網路連線

安裝程式從 `downloads.claude.ai` 下載。驗證您可以連線到它：

- macOS/Linux
- Windows PowerShell

```
curl -sI https://downloads.claude.ai/claude-code-releases/latest

```

```
curl.exe -sI https://downloads.claude.ai/claude-code-releases/latest

```

PowerShell 將 `curl` 別名為 `Invoke-WebRequest`，它會拒絕 `-sI` 旗標，所以明確呼叫 `curl.exe`。 如果第一行顯示 `200` 狀態，表示您已連線到伺服器。在 macOS 和 Linux 上您會看到 `HTTP/2 200`，在 Windows 上從 `curl.exe` 會看到 `HTTP/1.1 200 OK`。其他結果指向原因：

- `403`：通常是代理或網路篩選器阻止主機，或 Claude Code [在您的地區不可用](https://www.anthropic.com/supported-countries)
- `5xx`：通常是暫時性服務問題；等待幾分鐘後重試

如果您看不到任何輸出、`Could not resolve host` 或連線逾時，您的網路正在阻止連線。常見原因：

- 公司防火牆或代理阻止 `downloads.claude.ai`
- 區域網路限制：嘗試 VPN 或替代網路
- TLS/SSL 問題：更新您系統的 CA 憑證，或檢查是否設定了 `HTTPS_PROXY`

如果您在公司代理後面，在安裝前設定 `HTTPS_PROXY` 和 `HTTP_PROXY` 為您的代理位址。如果您不知道代理 URL，請詢問您的 IT 團隊，或檢查您的瀏覽器代理設定。 此範例設定兩個代理變數，然後透過您的代理執行安裝程式：

- macOS/Linux
- Windows PowerShell

```
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
curl -fsSL https://claude.ai/install.sh | bash

```

```
$env:HTTP_PROXY = 'http://proxy.example.com:8080'
$env:HTTPS_PROXY = 'http://proxy.example.com:8080'
irm https://claude.ai/install.ps1 | iex

```

### 驗證您的 PATH

如果安裝成功但執行 `claude` 時收到 `command not found` 或 `not recognized` 錯誤，安裝目錄不在您的 PATH 中。您的 shell 在 PATH 中列出的目錄中搜尋程式，安裝程式在 macOS/Linux 上將 `claude` 放在 `~/.local/bin/claude`，或在 Windows 上放在 `%USERPROFILE%\.local\bin\claude.exe`。 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)不會將 `claude` 放在此位置。它在擴充功能目錄內為其自己的聊天面板捆綁了一份私有的 CLI 副本，並且不會將其新增到 PATH。如果您只安裝了擴充功能，`~/.local/bin/claude` 將不存在。執行[獨立安裝](https://code.claude.com/docs/zh-TW/setup)以從終端使用 `claude`，然後繼續下面的步驟。 透過列出您的 PATH 項目並篩選 `local/bin` 來檢查安裝目錄是否在您的 PATH 中：

- macOS/Linux
- Windows PowerShell
- Windows CMD

```
echo $PATH | tr ':' '\n' | grep -Fx "$HOME/.local/bin"

```

如果這列印 `/Users/you/.local/bin` 或 `/home/you/.local/bin`，該目錄在您的 PATH 中，您可以跳到[檢查衝突的安裝](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-for-conflicting-installations)。如果沒有輸出，請將其新增到您的 shell 設定。對於 Zsh（macOS 上的預設值）：

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

```

對於 Bash（大多數 Linux 發行版上的預設值）：

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

```

或者，關閉並重新開啟您的終端。對於其他 shell（例如 fish 或 Nushell），使用您的 shell 自己的設定語法將 `~/.local/bin` 新增到您的 PATH，然後重新啟動您的終端。驗證修復是否有效：

```
claude --version

```

```
$env:PATH -split ';' | Select-String '\.local\\bin'

```

如果沒有輸出，請將安裝目錄新增到您的使用者 PATH：

```
$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
[Environment]::SetEnvironmentVariable('PATH', "$currentPath;$env:USERPROFILE\.local\bin", 'User')

```

重新啟動您的終端以使變更生效。驗證修復是否有效：

```
claude --version

```

```
echo %PATH% | findstr /i "local\bin"

```

如果沒有輸出，請開啟系統設定，前往環境變數，並將 `%USERPROFILE%\.local\bin` 新增到您的使用者 PATH 變數。重新啟動您的終端。驗證修復是否有效：

```
claude --version

```

### 檢查衝突的安裝

多個 Claude Code 安裝可能導致版本不相符或意外行為。檢查已安裝的內容：

- macOS/Linux
- Windows PowerShell

列出在您的 PATH 中找到的所有 `claude` 二進位檔：

```
which -a claude

```

如果這列印任何內容，沒有 `claude` 在您的 PATH 上。回到[驗證您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)。檢查 `claude` 二進位檔可能來自的三個位置。`~/.local/bin/claude` 是原生安裝程式，`~/.claude/local/` 是由舊版 Claude Code 建立的舊版本地 npm 安裝，npm 全域清單顯示 `-g` 安裝：

```
ls -la ~/.local/bin/claude

```

原生安裝會顯示一個指向 `~/.local/share/claude/versions/` 的符號連結。您在此路徑建立的指令碼或符號連結是自訂啟動程式，[自動更新會保留在原位](https://code.claude.com/docs/zh-TW/setup#auto-updates)。如果任一 `ls` 命令列印 `No such file or directory`，那不是錯誤。這表示該位置沒有安裝任何內容，所以繼續進行下一個檢查。

```
ls -la ~/.claude/local/

```

```
npm -g ls @anthropic-ai/claude-code 2>/dev/null

```

列出在您的 PATH 中找到的所有 `claude` 二進位檔：

```
where.exe claude

```

檢查原生安裝程式是否放置了二進位檔：

```
Test-Path "$env:USERPROFILE\.local\bin\claude.exe"

```

如果您找到多個安裝，只保留一個。macOS/Linux 上 `~/.local/bin/claude` 或 Windows 上 `%USERPROFILE%\.local\bin\claude.exe` 的原生安裝是推薦的。移除額外的： 解除安裝 npm 全域安裝：

```
npm uninstall -g @anthropic-ai/claude-code

```

移除舊版本地 npm 安裝：

- macOS/Linux
- Windows PowerShell

```
rm -rf ~/.claude/local

```

```
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\local"

```

在 macOS 上移除 Homebrew 安裝。如果您安裝了 `claude-code@latest` cask，請替換該名稱：

```
brew uninstall --cask claude-code

```

在 Windows 上移除 WinGet 安裝：

```
winget uninstall Anthropic.ClaudeCode

```

### 檢查目錄權限

安裝程式需要對 macOS 和 Linux 上的 `~/.local/bin/` 和 `~/.claude/` 有寫入存取權限。在 Windows 上，安裝位置在 `%USERPROFILE%` 下，預設情況下您的使用者可寫入，因此此部分很少適用於 Windows。 檢查目錄是否可寫入：

```
test -w ~/.local/bin && echo "writable" || echo "not writable"
test -w ~/.claude && echo "writable" || echo "not writable"

```

如果任一目錄不可寫入，請建立安裝目錄並將您的使用者設定為擁有者：

```
sudo mkdir -p ~/.local/bin
sudo chown -R $(whoami) ~/.local

```

### 驗證二進位檔是否有效

如果 `claude --version` 列印版本但 `claude` 在啟動時崩潰或掛起，請執行這些檢查以縮小原因範圍。如果 `claude --version` 說 command not found，請先前往[驗證您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)；下面的命令假設 `claude` 在您的 PATH 上。 確認二進位檔存在且可執行：

- macOS/Linux
- Windows PowerShell

```
ls -la "$(command -v claude)"

```

```
Get-Command claude | Select-Object Source

```

在 Linux 上，檢查遺失的共用程式庫。如果 `ldd` 顯示遺失的程式庫，您可能需要安裝系統套件。在 Alpine Linux 和其他基於 musl 的發行版上，請參閱 [Alpine Linux 設定](https://code.claude.com/docs/zh-TW/setup#alpine-linux-and-musl-based-distributions)。

```
ldd "$(command -v claude)" | grep "not found"

```

確認二進位檔可以執行：

```
claude --version

```

## 常見安裝問題

這些是最常見的安裝問題及其解決方案。

### 安裝指令碼傳回 HTML 而非 shell 指令碼

執行安裝命令時，您可能會看到以下其中一個錯誤：

```
bash: line 1: syntax error near unexpected token `<'
bash: line 1: `<!DOCTYPE html>'

```

在 PowerShell 上，同樣的問題顯示為解析錯誤，指向傳回的頁面，`iex` 嘗試執行 HTML 和 CSS 作為 PowerShell：

```
iex : At line:1 char:2310
+ ... igin="anonymous"/><script type="text/javascript">!function(o,c){var n ...
Missing argument in parameter list.
...

```

措辭因 PowerShell 版本和系統語言而異：您可能會看到 `Missing expression after unary operator '--'` 或帶有 `ParseException` 的 `ParserError`。引用文字中的 HTML 標籤或 CSS 識別此失敗。如果您改用 `-OutFile install.ps1` 下載，保存的檔案是相同的網頁，所以這也無法幫助。 根據請求的路由方式，您可能會看到 403 且沒有 HTML 主體：

```
curl: (22) The requested URL returned error: 403

```

這些都表示安裝 URL 傳回了 HTML 頁面或錯誤狀態，而非安裝指令碼。如果 HTML 頁面顯示「App unavailable in region」，Claude Code 在您的國家/地區不可用。請參閱[支援的國家/地區](https://www.anthropic.com/supported-countries)。 沒有主體的單純 403 通常有相同的原因，但也可能來自公司代理或防火牆阻止下載。如果您在支援的國家/地區但仍然看到 403，在嘗試下面的替代安裝程式前，請先完成[檢查網路連線](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-network-connectivity)，因為這些會連線到相同的主機。 否則，這可能由於網路問題、區域路由或暫時服務中斷而發生。 **解決方案：**

1. **使用替代安裝方法** ： 在 macOS 上，透過 Homebrew 安裝：

```
brew install --cask claude-code

```

在 Windows 上，透過 WinGet 安裝：

```
winget install Anthropic.ClaudeCode

```

然後執行 `claude --version` 以確認：命令列印版本號，例如 `2.1.211 (Claude Code)`。如果 shell 報告找不到 `claude`，開啟新的終端視窗並重試：您安裝的工作階段保留其舊的 `PATH`。 2. **幾分鐘後重試** ：問題通常是暫時的。等待並再次嘗試原始命令。

### 安裝後 `command not found: claude`

安裝完成但 `claude` 無法運作。確切的錯誤因平台而異：

| 平台                                                                                                                                                              | 錯誤訊息                                                               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| macOS                                                                                                                                                             | `zsh: command not found: claude`                                       |
| Linux                                                                                                                                                             | `bash: claude: command not found`                                      |
| Windows CMD                                                                                                                                                       | `'claude' is not recognized as an internal or external command`        |
| PowerShell                                                                                                                                                        | `claude : The term 'claude' is not recognized as the name of a cmdlet` |
| 這表示安裝目錄不在您的 shell 搜尋路徑中。請參閱[驗證您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path) 以取得每個平台上的修復。 |                                                                        |

### `curl: (56) Failure writing output to destination`

`curl ... | bash` 命令下載指令碼並將其傳送到 Bash 以執行。此錯誤以及相關的 `curl: (23) Failure writing output to destination` 表示 Bash 未收到完整的指令碼。結束代碼 56 表示下載本身被中斷，結束代碼 23 表示 curl 無法將其收到的內容寫入管道，通常是因為 Bash 提前結束。 測試您是否可以連線到 `downloads.claude.ai`，請參閱[檢查網路連線](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-network-connectivity)中的檢查。如果您連線到伺服器，原始失敗可能是間歇性的；重試安裝命令。您也可以[嘗試替代安裝方法](https://code.claude.com/docs/zh-TW/setup#install-claude-code)。

### Homebrew cask 無法使用或已過時

Homebrew 報告 `Error: Cask 'claude-code' is unavailable: No Cask with this name exists` 當您的 Homebrew cask 索引本機副本早於 cask 的發佈時間。重新整理索引並重試：

```
brew update
brew install --cask claude-code

```

如果 Homebrew 安裝的 Claude Code 版本比您預期的舊，通常是相同的過時索引導致的。`claude-code` cask 追蹤穩定通道，通常比最新版本晚約一週；若要取得最新版本，請改為執行 `brew install --cask claude-code@latest`。請參閱[設定發行通道](https://code.claude.com/docs/zh-TW/setup#configure-release-channel)以了解兩個 cask 之間的差異。

### TLS 或 SSL 連線錯誤

錯誤如 `curl: (35) TLS connect error`、`schannel: next InitializeSecurityContext failed` 或 PowerShell 的 `Could not establish trust relationship for the SSL/TLS secure channel` 表示 TLS 握手失敗。 **解決方案：**

1. **更新您的系統 CA 憑證** ： 在 Ubuntu/Debian 上：

```
sudo apt-get update && sudo apt-get install ca-certificates

```

在 macOS 上，系統 curl 使用 Keychain 信任存放區；更新 macOS 本身會更新根憑證。 2. **在 Windows 上，在執行安裝程式前在 PowerShell 中啟用 TLS 1.2** ：

```
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
irm https://claude.ai/install.ps1 | iex

```

3. **檢查代理或防火牆干擾** ：執行 TLS 檢查的公司代理可能導致這些錯誤，包括 `unable to get local issuer certificate` 和 `SELF_SIGNED_CERT_IN_CHAIN`。對於安裝步驟，使用 `--cacert` 將 curl 指向您的公司 CA 套件：
   - macOS/Linux
   - Windows PowerShell

```
curl --cacert /path/to/corporate-ca.pem -fsSL https://claude.ai/install.sh | bash

```

PowerShell 安裝程式透過 .NET 下載，該 .NET 針對 Windows 憑證存放區驗證 TLS。如果代理的 CA 憑證尚未在 Windows 存放區中，請要求您的 IT 團隊新增它，然後執行安裝程式：

```
irm https://claude.ai/install.ps1 | iex

```

對於安裝後的 Claude Code 本身，設定 `NODE_EXTRA_CA_CERTS` 以便 API 請求信任相同的套件： * macOS/Linux * Windows PowerShell

```
export NODE_EXTRA_CA_CERTS=/path/to/corporate-ca.pem

```

```
$env:NODE_EXTRA_CA_CERTS = 'C:\path\to\corporate-ca.pem'

```

如果您沒有憑證檔案，請詢問您的 IT 團隊。您也可以嘗試直接連線以確認代理是原因。 4. **在 Windows 上，解決被阻止的撤銷檢查** 。錯誤 `CRYPT_E_NO_REVOCATION_CHECK (0x80092012)` 和 `CRYPT_E_REVOCATION_OFFLINE (0x80092013)` 表示 curl 已連線到伺服器，但您的網路阻止了憑證撤銷查詢，這在公司防火牆後面很常見。如果失敗的命令是下載 `install.cmd` 的 `curl`，從命令提示字元重新執行它，並新增 `--ssl-revoke-best-effort`：

```
curl --ssl-revoke-best-effort -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```

當指令碼自己的下載遇到相同的錯誤時，它會自動使用最佳努力撤銷檢查重試它們，因此旗標僅在您自己執行的命令上需要。最佳努力檢查容許無法連線的撤銷伺服器，但仍然拒絕已知被撤銷的憑證，符合瀏覽器處理撤銷的方式。您也可以透過從 PowerShell 執行 PowerShell 安裝程式來完全避免 curl 的撤銷檢查，該程式透過 .NET 下載，當撤銷伺服器無法連線時不會失敗：

```
irm https://claude.ai/install.ps1 | iex

```

您也可以使用 `winget install Anthropic.ClaudeCode` 安裝，這完全避免了 curl。

### `Failed to fetch version from downloads.claude.ai`

安裝程式無法連線到下載伺服器。這通常表示 `downloads.claude.ai` 在您的網路上被阻止。請參閱[檢查網路連線](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-network-connectivity)。

### Windows 上的錯誤安裝命令

如果您看到 `'irm' is not recognized`、`The token '&&' is not valid`、`A parameter cannot be found that matches parameter name 'fsSL'` 或 `'bash' is not recognized as the name of a cmdlet`，您複製了不同 shell 或作業系統的安裝命令。如果命令列印指令碼的文字而不是安裝任何東西，您只執行了它的一部分。

- **`irm`未被識別** ：您在 CMD 中，而非 PowerShell。您有兩個選項： 透過在開始功能表中搜尋「PowerShell」開啟 PowerShell，然後執行原始安裝命令：

```
irm https://claude.ai/install.ps1 | iex

```

或留在 CMD 中並改用 CMD 安裝程式：

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```

- **`&&`無效** ：您在 PowerShell 中但執行了 CMD 安裝程式命令。使用 PowerShell 安裝程式：

```
irm https://claude.ai/install.ps1 | iex

```

- **`A parameter cannot be found that matches parameter name 'fsSL'`**：您在 Windows PowerShell 中執行了 macOS/Linux`curl -fsSL ... | bash` 安裝程式，其中 `curl` 是 `Invoke-WebRequest` 的別名，會拒絕 `-fsSL` 旗標。改用 PowerShell 安裝程式：

```
irm https://claude.ai/install.ps1 | iex

```

- **`bash`未被識別** ：您在 Windows 上執行了 macOS/Linux 安裝程式。改用 PowerShell 安裝程式：

```
irm https://claude.ai/install.ps1 | iex

```

- **命令列印指令碼文字而不是安裝** ：您執行了命令的下載部分，但沒有執行它的部分。`irm https://claude.ai/install.ps1` 單獨會將下載的指令碼列印到終端。將其傳送到 `iex` 以執行它：

```
irm https://claude.ai/install.ps1 | iex

```

在 CMD 中，`curl -fsSL https://claude.ai/install.cmd` 沒有 `-o` 會列印批次指令碼而不是保存它。執行完整命令：

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```

無論您使用哪個安裝程式，確認它有效：開啟新的終端並執行 `claude --version`，它列印版本號，例如 `2.1.211 (Claude Code)`。

### `running scripts is disabled on this system`

在 Windows 上透過 npm 安裝或執行 Claude Code 可能因 `SecurityError` 而失敗：

```
npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
...
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException

```

當您在 npm 安裝後執行 `claude` 時，相同的錯誤名稱 `claude.ps1`。PowerShell 的執行原則正在阻止 npm 為其命令建立的 `.ps1` 啟動器指令碼。該原則適用於指令碼檔案，因此它不影響 PowerShell 安裝程式 `irm https://claude.ai/install.ps1 | iex`，它直接執行下載的文字。 **解決方案：**

1. **允許您的使用者本機建立的指令碼** ，然後重試：

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

```

2. **改為呼叫`.cmd` 啟動器**：`npm.cmd` 和 `claude.cmd` 做相同的工作，該原則不涵蓋它們。
1. **改用[PowerShell 安裝程式](https://code.claude.com/docs/zh-TW/setup#install-claude-code)**，而不是 npm。它安裝二進位檔而不是 `.ps1` 指令碼。

### Windows 安裝期間的 `The process cannot access the file`

如果 PowerShell 安裝程式因 `Failed to download binary: The process cannot access the file ... because it is being used by another process` 而失敗，安裝程式無法寫入 `%USERPROFILE%\.claude\downloads`。這通常表示先前的安裝嘗試仍在執行，或防毒軟體正在掃描該資料夾中部分下載的二進位檔。 關閉任何其他執行安裝程式的 PowerShell 視窗，並等待防毒軟體掃描釋放該檔案。然後刪除下載資料夾並再次執行安裝程式：

```
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\downloads"
irm https://claude.ai/install.ps1 | iex

```

### 低記憶體 Linux 伺服器上安裝被終止

在安裝期間出現 `Killed` 訊息通常表示 Linux 記憶體不足 (OOM) 殺手終止了 `claude install` 步驟，因為系統用盡了可用記憶體。這在小型 VPS 和雲端執行個體上很常見。安裝指令碼報告原因並以代碼 137 結束。在此範例中，行號和程序 ID 因版本和執行而異：

```
Setting up Claude Code...
bash: line 183: 34803 Killed    "$binary_path" install ${TARGET:+"$TARGET"}
Installation was killed before it could finish (exit code 137). This usually means the system ran out of memory.
Claude Code needs roughly 512MB of free memory to install. Free up memory, then run this script again.

```

安裝需要大約 512 MB 的可用記憶體，執行 Claude Code 需要更多。請參閱[系統需求](https://code.claude.com/docs/zh-TW/setup#system-requirements)。 **解決方案：**

1. **新增交換空間** （如果您的伺服器 RAM 有限）。交換使用磁碟空間作為溢出記憶體，讓安裝即使在低物理 RAM 的情況下也能完成。 建立 2 GB 交換檔案並啟用它：

```
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

```

然後重試安裝：

```
curl -fsSL https://claude.ai/install.sh | bash

```

2. **在安裝前關閉其他程序** 以釋放記憶體。
1. **如果可能，使用更大的執行個體** 。Claude Code 需要至少 4 GB 的 RAM。

### Docker 中安裝掛起

在 Docker 容器中安裝 Claude Code 時，以 root 身份安裝到 `/` 可能導致掛起。 **解決方案：**

1. **在執行安裝程式前設定工作目錄** 。在 `/` 執行時，安裝程式掃描整個檔案系統，導致過度的記憶體使用。設定 `WORKDIR` 將掃描限制在小目錄：

```
WORKDIR /tmp
RUN curl -fsSL https://claude.ai/install.sh | bash

```

2. **如果使用 Docker Desktop，請增加 Docker 記憶體** 。建置容器共享分配給 Docker Desktop 虛擬機器的記憶體，因此開啟 Docker Desktop 中的 **Settings > Resources**，提高記憶體限制，然後重新執行建置。

### 安裝期間的 `Raw mode is not supported`

當您的組織的[伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings)包含需要[安全性核准](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)的變更時，Claude Code 2.1.246 之前的版本嘗試在 `claude install` 期間顯示核准對話方塊。對話方塊需要 stdin 上的終端。當安裝程式從管道執行 `claude install` 時，如 `curl -fsSL https://claude.ai/install.sh | bash` 所做的，stdin 是管道而不是終端，因此安裝因包含 `Raw mode is not supported` 的錯誤而失敗。 Claude Code v2.1.246 及更新版本在 `claude install` 或 `claude update` 期間不顯示對話方塊。命令使用您上次核准的設定執行，Claude Code 在您的下一個互動工作階段中顯示對話方塊。如果您的組織的啟動設定[等待設定擷取](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup)，例如當它設定 `forceRemoteSettingsRefresh` 時，對話方塊仍會在這些命令期間出現，從管道執行的安裝仍會失敗。 在每個其他設定中，重新執行安裝程式會超過此錯誤，因為即使您要求它安裝舊版本，指令碼也會執行最新版本的 `install` 命令。為您的平台重新執行命令：

- macOS/Linux
- Windows PowerShell

```
curl -fsSL https://claude.ai/install.sh | bash

```

```
irm https://claude.ai/install.ps1 | iex

```

`claude --version` 列印重新執行安裝的版本。

### `claude update` 或 `claude doctor` 掛起

`claude update` 和 `claude doctor` 掃描您的 shell 設定檔以尋找過時的 `claude` 別名：`~/.zshrc`、`~/.bashrc` 和 `~/.config/fish/config.fish`，加上在 macOS 上存在的 `~/.bash_profile`、`~/.bash_login` 或 `~/.profile` 中的第一個。如果您設定 `ZDOTDIR`，Zsh 檔案是 `$ZDOTDIR/.zshrc`。當這些路徑之一是目錄時，Claude Code 會跳過它，兩個命令都正常完成。在 v2.1.214 之前，這些路徑之一的目錄使兩個命令掛起，並使 `/status` 的系統診斷部分保持空白。`claude doctor` 掛起且沒有輸出；`claude update` 在列印 `Checking for updates` 後立即掛起。 如果您在較早版本上遇到掛起，請找到目錄。在此命令的輸出中，以 `d` 開頭的行將該路徑標記為目錄。`No such file or directory` 行表示該路徑上沒有任何內容，不是原因：

```
ls -ld ~/.zshrc ~/.bashrc ~/.bash_profile ~/.bash_login ~/.profile ~/.config/fish/config.fish

```

將目錄移到一邊，或更新到 v2.1.214 或更新版本。由於 `claude update` 在受影響的版本上掛起，改為透過重新執行[安裝指令碼](https://code.claude.com/docs/zh-TW/setup#install-claude-code)進行更新。

### Claude Desktop 在 Windows 上覆蓋 `claude` 命令

如果您安裝了舊版本的 Claude Desktop，它可能在 `WindowsApps` 目錄中註冊 `Claude.exe`，其 PATH 優先級高於 Claude Code CLI。執行 `claude` 會開啟 Desktop 應用程式而非 CLI。 更新 Claude Desktop 到最新版本以修復此問題。

### Windows 上的 Claude Code 需要 Git for Windows（用於 bash）或 PowerShell

Git for Windows 是選用的。Claude Code 在缺少 Git Bash 時使用 [PowerShell 工具](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool)，因此此錯誤表示找不到任何一個 shell。 **如果 PowerShell 不在您的 PATH 中** ，其預設位置是 `C:\Windows\System32\WindowsPowerShell\v1.0\`。將該目錄新增到您的 `PATH`，或安裝 [PowerShell 7](https://aka.ms/powershell)，它提供 `pwsh`。 **若要改為安裝 Git for Windows** ，請從 [git-scm.com/downloads/win](https://git-scm.com/downloads/win) 下載。在設定期間，選擇「Add to PATH」。安裝後重新啟動您的終端。安裝它會啟用 Bash 工具，在使用基於 Bash 的指令碼和工具時很有用。 **如果 Git 已安裝** 但 Claude Code 找不到它，請比較其位置與 Claude Code 檢查的位置。當 `CLAUDE_CODE_GIT_BASH_PATH` 未設定時，Claude Code 按此順序尋找 `bash.exe`：

1. 預設安裝位置 `C:\Program Files\Git` 和 `C:\Program Files (x86)\Git`。
1. 您的 `PATH` 上的 `git`，使用該 Git 安裝中的 `bin\bash.exe`。

在步驟 2 中，Claude Code 跳過位於您啟動 Claude Code 的資料夾中的 `git`，或在包含 `node_modules` 或虛擬環境資料夾（例如 `.venv` 或 `env`）的路徑下方，例如當您從 `C:\dev\env\myproject` 啟動時的 `C:\dev\env\myproject\Git`。這可防止 Claude Code 執行專案放在那裡的可執行檔。如果您的 Git 在這樣的位置，請將 `CLAUDE_CODE_GIT_BASH_PATH` 指向它。 **若要將 Claude Code 指向特定的 Git 安裝** ，透過在 PowerShell 中執行 `where.exe git` 找到它，然後在您的 [settings.json 檔案](https://code.claude.com/docs/zh-TW/settings)中將該安裝中的 `bin\bash.exe` 路徑設定為 `CLAUDE_CODE_GIT_BASH_PATH`：

```
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}

```

**如果`CLAUDE_CODE_GIT_BASH_PATH` 設定為正確的路徑且檔案存在**但 Claude Code 仍然不使用它，請先檢查檔案的名稱。Claude Code 僅接受名為 `bash.exe`、`sh.exe`、`bash` 或 `sh` 的檔案；使用任何其他名稱（例如 Git for Windows 的 `git-bash.exe` 啟動器），它會忽略變數並自動偵測 Git Bash，就像它未設定一樣，記錄可透過 `--debug` 看到的警告。不存在的路徑會得到相同的後備和警告。在 v2.1.219 之前，Claude Code 使用任何現有檔案作為 shell，而不檢查其名稱，當路徑不存在時在啟動時以 `Claude Code was unable to find CLAUDE_CODE_GIT_BASH_PATH path` 結束。 如果檔案的名稱正確，端點安全軟體（例如 AppLocker、群組原則軟體限制原則或 EDR 代理）可能正在干擾。要求您的 IT 團隊在您的端點保護原則中將 `claude.exe` 和它生成的程序（包括 `cmd.exe` 和 `bash.exe`）加入允許清單。

### Claude Code 不支援 32 位元 Windows

Windows 在開始功能表中包含兩個 PowerShell 項目：`Windows PowerShell` 和 `Windows PowerShell (x86)`。x86 項目以 32 位元程序執行，即使在 64 位元機器上也會觸發此錯誤。要檢查您在哪種情況下，請在產生錯誤的同一視窗中執行此命令：

```
[Environment]::Is64BitOperatingSystem

```

如果這列印 `True`，您的作業系統沒問題。關閉視窗，開啟不帶 x86 後綴的 `Windows PowerShell`，然後再次執行安裝命令。 如果這列印 `False`，您在 32 位元版本的 Windows 上。Claude Code 需要 64 位元作業系統。請參閱[系統需求](https://code.claude.com/docs/zh-TW/setup#system-requirements)。

### Linux musl 或 glibc 二進位不相符

如果在安裝後看到有關遺失共用程式庫的錯誤，如 `libstdc++.so.6` 或 `libgcc_s.so.1`，安裝程式可能為您的系統下載了錯誤的二進位變體。

```
Error loading shared library libstdc++.so.6: No such file or directory

```

這可能發生在已安裝 musl 交叉編譯套件的基於 glibc 的系統上，導致安裝程式將系統誤檢測為 musl。 **解決方案：**

1. **檢查您的系統使用哪個 libc** ：

```
ldd --version 2>&1 | head -1

```

提及 `GNU libc` 或 `GLIBC` 的輸出表示 glibc。提及 `musl` 的輸出表示 musl。 2. **如果您在 glibc 上但得到了 musl 二進位檔** ，移除安裝並重新安裝。您也可以使用 `https://downloads.claude.ai/claude-code-releases/{VERSION}/manifest.json` 上的清單手動下載正確的二進位檔。使用 `ldd --version` 和 `ls /lib/libc.musl*` 的輸出提交 [GitHub 問題](https://github.com/anthropics/claude-code/issues)。 3. **如果您實際上在 musl 上** ，例如 Alpine Linux，請安裝所需的套件：

```
apk add libgcc libstdc++ ripgrep

```

在 Alpine 上，`ripgrep` 在社群儲存庫中。如果 `apk` 報告套件遺失，請參閱 [Alpine Linux 設定](https://code.claude.com/docs/zh-TW/setup#alpine-linux-and-musl-based-distributions)。

### `Illegal instruction`

如果執行 `claude` 或安裝程式列印 `Illegal instruction`，原生二進位檔使用您的處理器不支援的 CPU 指令。有兩個不同的原因。 **架構不相符。** 安裝程式下載了錯誤的二進位檔，例如在 ARM 伺服器上的 x86。在 macOS 或 Linux 上使用 `uname -m` 檢查，或在 PowerShell 中使用 `$env:PROCESSOR_ARCHITECTURE`。如果結果與您收到的二進位檔不相符，[提交 GitHub 問題](https://github.com/anthropics/claude-code/issues)並附上輸出。 **遺失 AVX 指令集。** 如果您的架構正確但仍然看到 `Illegal instruction`，您的 CPU 可能缺少 AVX 或二進位檔需要的其他指令。這影響大約 2013 年之前的 Intel 和 AMD 處理器，以及超管理程式不將 AVX 傳遞給客體的虛擬機器。 在 VPS 或 VM 上，執行 `grep -m1 -ow avx /proc/cpuinfo`；空結果表示 AVX 對客體不可用。 沒有原生二進位檔解決方法；追蹤[問題 #50384](https://github.com/anthropics/claude-code/issues/50384) 以取得狀態，並在報告時包含您的 CPU 型號，從 Linux 上的 `grep -m1 "model name" /proc/cpuinfo` 或 macOS 上的 `sysctl -n machdep.cpu.brand_string`。 替代安裝方法下載相同的原生二進位檔，不會解決任一原因。

### macOS 上的 `dyld: cannot load`

如果在安裝期間看到 `dyld: Symbol not found`、`dyld: cannot load` 或 `Abort trap: 6`，二進位檔與您的 macOS 版本或硬體不相容。 參考 `libicucore` 的 `Symbol not found` 錯誤表示您的 macOS 版本比二進位檔支援的版本更舊：

```
dyld: Symbol not found: _ubrk_clone
  Referenced from: claude-darwin-x64 (which was built for Mac OS X 13.0)
  Expected in: /usr/lib/libicucore.A.dylib

```

載入器可以改為拒絕二進位檔的載入命令，這也表示您的 macOS 版本太舊：

```
dyld: cannot load 'claude-2.1.42-darwin-x64' (load command 0x80000034 is unknown)
Abort trap: 6

```

**解決方案：**

1. **檢查您的 macOS 版本** ：Claude Code 需要 macOS 13.0 或更新版本。開啟 Apple 功能表並選擇「關於本機」以檢查您的版本。
1. **更新 macOS** （如果您在舊版本上）。二進位檔使用舊 macOS 版本不支援的載入命令和系統程式庫。Homebrew 等替代安裝方法下載相同的二進位檔，不會解決此錯誤。

### WSL1 上的 `Exec format error`

如果在 WSL 中執行 `claude` 列印 `cannot execute binary file: Exec format error`，您在 WSL1 上並遇到[問題 #38788](https://github.com/anthropics/claude-code/issues/38788) 中追蹤的已知原生二進位檔回歸。二進位檔的程式頭以 WSL1 的載入器無法處理的方式改變。 最簡潔的修復是從 PowerShell 將您的發行版轉換為 WSL2：

```
wsl --set-version <DistroName> 2

```

如果您需要留在 WSL1 上，透過動態連結器叫用二進位檔。將此函數新增到 WSL 內的 `~/.bashrc`，如果您的主目錄不同，請替換路徑：

```
claude() {
  /lib64/ld-linux-x86-64.so.2 "$(readlink -f "$HOME/.local/bin/claude")" "$@"
}

```

然後執行 `source ~/.bashrc` 並重試 `claude`。

### WSL 中的 npm 安裝錯誤

如果您在 WSL 內使用 `npm install -g` 安裝了 Claude Code，這些問題適用。如果您使用了[原生安裝程式](https://code.claude.com/docs/zh-TW/setup)，請跳過此部分。 **OS 或平台偵測問題。** 如果 npm 在安裝期間報告平台不相符，WSL 可能正在使用 Windows `npm`。首先執行 `npm config set os linux`，然後使用 `npm install -g @anthropic-ai/claude-code --force` 安裝。不要使用 `sudo`。 **執行`claude` 時的 `exec: node: not found`。** 您的 WSL 環境可能使用 Windows 安裝的 Node.js。使用 `which npm` 和 `which node` 確認：以 `/mnt/c/` 開頭的路徑是 Windows 二進位檔，而 Linux 路徑以 `/usr/` 開頭。要修復此問題，請透過您的 Linux 發行版的套件管理器或透過 [`nvm`](https://github.com/nvm-sh/nvm) 安裝 Node。 **nvm 版本衝突。** 如果您在 WSL 和 Windows 中都安裝了 nvm，在 WSL 中切換 Node 版本可能會中斷，因為 WSL 預設匯入 Windows PATH，Windows nvm 優先。最常見的原因是 nvm 未在您的 shell 中載入。將 nvm 載入器新增到 `~/.bashrc` 或 `~/.zshrc`：

```
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

```

或在您的目前工作階段中載入它：

```
source ~/.nvm/nvm.sh

```

如果 nvm 已載入但 Windows 路徑仍優先，明確地預先設定您的 Linux Node 路徑：

```
export PATH="$HOME/.nvm/versions/node/$(node -v)/bin:$PATH"

```

避免透過 `appendWindowsPath = false` 停用 Windows PATH 匯入，因為這會破壞從 WSL 呼叫 Windows 可執行檔的能力。同樣，如果您在 Windows 開發中使用 Node.js，請避免從 Windows 解除安裝它。

### 安裝期間的權限錯誤

如果原生安裝程式因權限錯誤而失敗，目標目錄可能不可寫入。請參閱[檢查目錄權限](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-directory-permissions)。 如果您之前使用 npm 安裝並遇到 npm 特定的權限錯誤，請切換到原生安裝程式：

```
curl -fsSL https://claude.ai/install.sh | bash

```

### npm 安裝後找不到原生二進位檔

`@anthropic-ai/claude-code` npm 套件透過每個平台的可選相依性（如 `@anthropic-ai/claude-code-darwin-arm64`）拉入原生二進位檔。npm 然後執行套件的 postinstall 指令碼，該指令碼將該二進位檔複製到位置作為 `claude` 命令；在它執行之前，`claude` 是佔位符指令碼。如果下載或 postinstall 步驟被跳過，佔位符保留在位置，在 macOS 和 Linux 上執行 `claude` 列印：

```
Error: claude native binary not installed.

Either postinstall did not run (--ignore-scripts, some pnpm configs)
or the platform-native optional dependency was not downloaded
(--omit=optional).

Run the postinstall manually (adjust path for local vs global install):
  node node_modules/@anthropic-ai/claude-code/install.cjs

Or reinstall without --ignore-scripts / --omit=optional.

```

在 Windows 上，`bin/claude.exe` 是相同的 shell 指令碼佔位符而不是真實可執行檔，因此 PowerShell 和 CMD 報告他們無法執行檔案，而不是列印此訊息。 檢查以下原因：

- **可選相依性已停用。** 從您的 npm 安裝命令中移除 `--omit=optional`、從 pnpm 移除 `--no-optional` 或從 yarn 移除 `--ignore-optional`，並檢查 `.npmrc` 是否未設定 `optional=false`。然後重新安裝。原生二進位檔僅作為可選相依性提供，因此如果跳過它，沒有 JavaScript 後備，重新執行 `install.cjs` 無法放置從未下載的二進位檔。
- **安裝指令碼已停用。** `--ignore-scripts` 和某些 pnpm 設定跳過 postinstall 步驟，但仍然下載平台套件。執行 `node node_modules/@anthropic-ai/claude-code/install.cjs`，如訊息所建議，或不使用旗標重新安裝。如果 postinstall 根本無法在您的環境中執行，`node node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs` 找到下載的套件並啟動它，代價是每次啟動時額外的 Node 程序。如果包裝器改為列印 `Could not find native binary package`，平台套件從未下載，因此首先修復上面的可選相依性原因。
- **不支援的平台。** 預建二進位檔針對 `darwin-arm64`、`darwin-x64`、`linux-x64`、`linux-arm64`、`linux-x64-musl`、`linux-arm64-musl`、`win32-x64` 和 `win32-arm64` 發佈。Claude Code 不為其他平台提供二進位檔；請參閱[系統需求](https://code.claude.com/docs/zh-TW/setup#system-requirements)。在 FreeBSD 上，安裝程式報告平台為不支援。在 v2.1.205 之前，它將 FreeBSD 視為 Linux 並下載了無法執行的二進位檔。
- **公司 npm 鏡像缺少平台套件。** 確保您的登錄鏡像除了元套件外，還鏡像所有八個 `@anthropic-ai/claude-code-*` 平台套件。

### npm `ENOTEMPTY` 錯誤在更新或重新安裝期間

當您在現有安裝上執行 `npm install -g @anthropic-ai/claude-code` 時，npm 在移動舊套件目錄時可能失敗：

```
npm error code ENOTEMPTY
npm error syscall rename
npm error path /home/you/.nvm/versions/node/v22.13.1/lib/node_modules/@anthropic-ai/claude-code
npm error dest /home/you/.nvm/versions/node/v22.13.1/lib/node_modules/@anthropic-ai/.claude-code-tVWAnUUt
npm error errno -39
npm error ENOTEMPTY: directory not empty, rename '...'

```

`npm error path` 行命名 npm 無法移動的目錄。刪除該目錄和其旁邊的任何剩餘 `.claude-code-*` 目錄，較早中斷的執行可能會留下。下面的命令使用 `npm root -g` 找到您的全域套件目錄；如果 `npm error path` 行命名的目錄不在 `npm root -g` 列印的目錄下，例如因為您使用 nvm 切換了 Node 版本，改為刪除錯誤命名的目錄：

- macOS/Linux
- Windows PowerShell

```
rm -rf "$(npm root -g)/@anthropic-ai/claude-code"

```

然後移除任何剩餘的臨時目錄。如果 zsh 列印 `no matches found`，沒有要移除的：

```
rm -rf "$(npm root -g)/@anthropic-ai/.claude-code-"*

```

```
Remove-Item -Recurse -Force "$(npm root -g)/@anthropic-ai/claude-code", "$(npm root -g)/@anthropic-ai/.claude-code-*"

```

然後重新安裝：

```
npm install -g @anthropic-ai/claude-code

```

使用 `claude --version` 確認，它列印版本號，例如 `2.1.211 (Claude Code)`。

## 登入和身份驗證

這些部分涉及登入失敗、OAuth 錯誤和令牌問題。

### 重設您的登入

當登入失敗且原因不明顯時，乾淨的重新身份驗證可解決大多數情況：

1. 執行 `/logout` 以完全登出
1. 關閉 Claude Code
1. 使用 `claude` 重新啟動並再次完成身份驗證程序

如果瀏覽器在登入期間未自動開啟，按 `c` 將 OAuth URL 複製到您的剪貼簿，然後手動將其貼到瀏覽器中。當 URL 在狹窄或 SSH 終端中跨行換行且無法直接點擊時，這也有效。

### OAuth 錯誤：無效代碼

如果您看到 `OAuth error: Invalid code. Please make sure the full code was copied`，登入代碼已過期或在複製貼上期間被截斷。 **解決方案：**

- 在瀏覽器開啟後按 Enter 以重試並快速完成登入
- 如果瀏覽器未自動開啟，輸入 `c` 複製完整 URL
- 如果使用遠端/SSH 工作階段，瀏覽器可能在錯誤的機器上開啟。複製終端中顯示的 URL 並在您的本地瀏覽器中開啟它。

### 登入後 403 Forbidden

如果您在登入後看到 `API Error: 403 {"error":{"type":"forbidden","message":"Request not allowed"}}`：

- **Claude Pro/Max 使用者** ：在 [claude.ai/settings](https://claude.ai/settings) 驗證您的訂閱是否有效
- **Anthropic Console 使用者** ：確認您的帳戶具有「Claude Code」或「Developer」角色。管理員在 Anthropic Console 的「設定」→「成員」中指派此角色。
- **在代理後面** ：公司代理可能干擾 API 請求。請參閱[網路設定](https://code.claude.com/docs/zh-TW/network-config)以取得代理設定。

### 此組織已停用，但有有效的訂閱

如果您看到 `API Error: 400 ... "This organization has been disabled"`，儘管有有效的 Claude 訂閱，`ANTHROPIC_API_KEY` 環境變數正在覆蓋您的訂閱。這通常發生在舊 API 金鑰（來自先前的雇主或專案）仍在您的 shell 設定檔中時。 當 `ANTHROPIC_API_KEY` 存在且您已核准它時，Claude Code 使用該金鑰而非您訂閱的 OAuth 認證。在使用 `-p` 旗標的非互動模式下，當存在時始終使用該金鑰。請參閱[身份驗證優先順序](https://code.claude.com/docs/zh-TW/authentication#authentication-precedence)以取得完整的解決順序。 要改用您的訂閱，請取消設定環境變數並從您的 shell 設定檔中移除它：

- macOS/Linux
- Windows PowerShell

```
unset ANTHROPIC_API_KEY
claude

```

```
Remove-Item Env:ANTHROPIC_API_KEY
claude

```

檢查 `~/.zshrc`、`~/.bashrc` 或 `~/.profile` 中的 `export ANTHROPIC_API_KEY=...` 行並移除它們以永久進行變更。在 Windows 上，檢查您在 `$PROFILE` 的 PowerShell 設定檔和您的使用者環境變數中的 `ANTHROPIC_API_KEY`。在 Claude Code 內執行 `/status` 以確認哪個身份驗證方法是有效的。

### WSL2、SSH 或容器中的 OAuth 登入失敗

當 Claude Code 在 WSL2 中執行、透過 SSH 在遠端機器上執行或在容器內執行時，瀏覽器通常在不同的主機上開啟，其重新導向無法到達 Claude Code 的本地回呼伺服器。在您登入後，瀏覽器會顯示登入代碼而不是自動重新導向回來。將該代碼貼到終端的 `Paste code here if prompted` 提示中以完成登入。 如果瀏覽器根本不從 WSL2 開啟，請將 `BROWSER` 環境變數設定為您的 Windows 瀏覽器路徑：

```
export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
claude

```

或者，在互動式登入提示時按 `c` 複製 OAuth URL，或複製 `claude auth login` 列印的 URL，並在您的本地機器上的瀏覽器中開啟它。 如果將代碼貼到互動式提示中沒有任何反應，您的終端的貼上繫結可能無法到達輸入欄位。嘗試您的終端的替代貼上快捷鍵，通常在 Windows Terminal 中是右鍵點擊或 Shift+Insert，或改用 `claude auth login`，它從標準輸入讀取貼上的代碼：

```
claude auth login

```

此後備也適用於原生 Windows 或任何將代碼貼到互動式提示失敗的終端。

### 未登入或令牌已過期

如果 Claude Code 在工作階段後提示您再次登入，您的 OAuth 令牌可能已過期。 執行 `/login` 以重新身份驗證。如果這經常發生，請檢查您的系統時鐘是否準確，因為令牌驗證取決於正確的時間戳。 一台機器上的平行工作階段共享已儲存的登入，並協調其更新，以便只有一個程序一次重新整理令牌。在 v2.1.211 之前，從睡眠喚醒機器可能導致兩個工作階段使用相同令牌進行更新，這會撤銷已儲存的登入，並提示每個開啟的工作階段立即再次登入。 在 macOS 上，Claude Code 將認證儲存到登入 Keychain。當 Keychain 拒絕寫入時，例如當它在 SSH 工作階段中被鎖定或其密碼與您的帳戶密碼不同步時，Claude Code 改為將您的登入儲存到純文字 `~/.claude/.credentials.json` 檔案。建立 API 金鑰的 Console 登入會失敗，直到 Keychain 再次可寫入。 要使 Keychain 再次可寫入並將您的登入移回加密的 Keychain： 1 檢查 Keychain 存取 執行 `claude doctor` 以檢查 Keychain 存取。當 Keychain 拒絕寫入時，報告會列出以 `macOS Keychain is not writable` 開頭的警告，後面跟著建議的修正。當報告未列出 Keychain 警告時，Keychain 可寫入，您可以跳到最後一步。 2 解鎖 Keychain

```
security unlock-keychain ~/Library/Keychains/login.keychain-db

```

當命令要求時輸入您的 Keychain 密碼，然後再次執行 `claude doctor`。當解鎖成功時，報告不再列出 Keychain 警告。 3 如果解鎖無幫助，請重新同步 Keychain 密碼 開啟 Keychain Access，選擇 `login` keychain，並選擇「編輯」>「變更 Keychain ‘login’ 的密碼」以將其與您的帳戶密碼重新同步。然後再次執行 `claude doctor`。一旦報告不再列出 Keychain 警告，請繼續下一步。 4 登出並重新登入 一旦 Keychain 再次可寫入，Claude Code 會在下次寫入認證時將認證移回。要立即強制執行，請執行 `/logout`，然後執行 `/login`。登出會移除所有已儲存的認證，包括純文字檔案的內容、已儲存的 MCP 伺服器登入和外掛敏感值，因此預期之後需要重新授權 MCP 伺服器和重新輸入外掛祕密。再次登入會將您的登入儲存在 Keychain 中。

### Bedrock、Agent Platform 或 Foundry 認證未載入

如果您設定了 Claude Code 以使用雲端提供者，並在 Amazon Bedrock 上看到 `Could not load credentials from any providers`、在 Google Cloud 的 Agent Platform 上看到 `Could not load the default credentials` 或在 Microsoft Foundry 上看到 `ChainedTokenCredential authentication failed`，您的雲端提供者 CLI 可能在目前 shell 中未進行身份驗證。 對於 Amazon Bedrock，確認您的 AWS 認證有效：

```
aws sts get-caller-identity

```

對於 Google Cloud 的 Agent Platform，確認 `ANTHROPIC_VERTEX_PROJECT_ID` 和 `CLOUD_ML_REGION` 在您的 shell 中設定，然後設定應用程式預設認證：

```
gcloud auth application-default login

```

對於 Microsoft Foundry，確認 `ANTHROPIC_FOUNDRY_API_KEY` 已設定，或使用 Azure CLI 登入，以便預設認證鏈可以找到您的帳戶：

```
az login

```

如果認證在您的終端中有效但在 VS Code 或 JetBrains 擴充功能中無效，IDE 程序可能未繼承您的 shell 環境。在 IDE 自己的設定中設定提供者環境變數，或從已匯出它們的終端啟動 IDE。 請參閱 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 以取得完整的提供者設定。

## 仍然卡住

如果上述任何方法都無法解決您的問題：

1. 檢查 [GitHub 儲存庫](https://github.com/anthropics/claude-code/issues)以了解已知問題，或使用您的作業系統、您執行的安裝命令和完整錯誤輸出開啟新問題
1. 如果 `claude --version` 有效但其他內容有問題，執行 `claude doctor` 以取得自動診斷報告
1. 如果您可以啟動工作階段，請在 Claude Code 內使用 `/feedback` 報告問題
1. 如果問題與您的帳戶而非安裝有關，例如登入迴圈、無法識別的訂閱或已停用的組織，請聯絡 Anthropic 支援：登入 [claude.ai](https://claude.ai)（Console 使用者：[platform.claude.com](https://platform.claude.com)），點擊左下角的您的首字母縮寫，然後選擇**取得協助** 。請參閱[如何取得支援](https://support.claude.com/en/articles/9015913-how-to-get-support)以了解完整流程。

是否 助手
