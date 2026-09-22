本頁涵蓋 Claude Code 執行後的效能、穩定性和搜尋問題。如需其他問題，請從符合您遇到問題位置的頁面開始：

| 症狀                                                                                                                                                                                                                                                   | 前往                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `command not found`、安裝失敗、PATH 問題、`EACCES`、TLS 錯誤                                                                                                                                                                                           | [故障排除安裝和登入](https://code.claude.com/docs/zh-TW/troubleshoot-install)                             |
| 更新或安裝下載失敗，出現 `The connection dropped while downloading the update` 或 `aborted`                                                                                                                                                            | [錯誤參考](https://code.claude.com/docs/zh-TW/errors#the-connection-dropped-while-downloading-the-update) |
| 登入迴圈、OAuth 錯誤、`403 Forbidden`、「組織已停用」、Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 認證                                                                                                                        | [故障排除安裝和登入](https://code.claude.com/docs/zh-TW/troubleshoot-install#login-and-authentication)    |
| 設定未套用、hooks 未觸發、MCP 伺服器未載入                                                                                                                                                                                                             | [偵錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config)                                      |
| 工作階段以自動模式啟動，或 Claude 編輯檔案並執行命令而不詢問                                                                                                                                                                                           | [工作階段啟動的模式](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)  |
| `API Error: 5xx`、`529 Overloaded`、`429`、請求驗證錯誤                                                                                                                                                                                                | [錯誤參考](https://code.claude.com/docs/zh-TW/errors)                                                     |
| `model not found` 或 `you may not have access to it`                                                                                                                                                                                                   | [錯誤參考](https://code.claude.com/docs/zh-TW/errors#theres-an-issue-with-the-selected-model)             |
| VS Code 擴充功能未連接或未偵測到 Claude                                                                                                                                                                                                                | [VS Code 整合](https://code.claude.com/docs/zh-TW/vs-code#fix-common-issues)                              |
| VS Code 或 SDK 應用程式中出現 `Claude Code process exited with code 1`                                                                                                                                                                                 | [錯誤參考](https://code.claude.com/docs/zh-TW/errors#claude-code-process-exited-with-code-n)              |
| JetBrains 外掛程式或 IDE 未偵測到                                                                                                                                                                                                                      | [JetBrains 整合](https://code.claude.com/docs/zh-TW/jetbrains#troubleshooting)                            |
| 高 CPU 或記憶體、回應緩慢、掛起、搜尋找不到檔案                                                                                                                                                                                                        | [效能和穩定性](https://code.claude.com/docs/zh-TW/troubleshooting#performance-and-stability)下方          |
| 如果您不確定哪個適用，請在 Claude Code 內執行 `/doctor` 以自動檢查您的安裝、設定、擴充功能和上下文使用情況；它會提議可以在您確認後套用的修復。如果 `claude` 根本無法啟動，請改為從您的 shell 執行 `claude doctor`。執行 `/mcp` 以檢查 MCP 伺服器狀態。 |                                                                                                           |

______________________________________________________________________

## title: “效能和穩定性” description: “涵蓋與資源使用、回應性和搜尋行為相關的問題。”

## 效能和穩定性

這些部分涵蓋與資源使用、回應性和搜尋行為相關的問題。

### 高 CPU 或記憶體使用

Claude Code 設計用於與大多數開發環境配合使用，但在處理大型程式碼庫時可能消耗大量資源。如果您遇到效能問題：

1. 定期使用 `/compact` 減少上下文大小。如果它傳回 `Not enough messages to compact.`，表示對話的輪次太少而無法摘要；即使上下文已滿，單次大型貼上也可能導致這種情況
1. 在主要任務之間關閉並重新啟動 Claude Code
1. 考慮將大型構建目錄新增到您的 `.gitignore` 檔案
1. 使用 [`claude --safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 重新啟動以檢查外掛程式、MCP 伺服器或 hook 是否為來源。它會停用該工作階段的所有自訂；如果使用量下降，請參閱[偵錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config#test-against-a-clean-configuration)以找出是哪一個

如果在這些步驟後記憶體使用仍然很高，請執行 `/heapdump` 以將兩個檔案寫入 `~/Desktop`：一個名為 `<session-id>.heapsnapshot` 的 JavaScript 堆快照和一個名為 `<session-id>-diagnostics.json` 的記憶體分解。Claude Code [從命令選單隱藏該命令](https://code.claude.com/docs/zh-TW/commands#how-the-command-menu-matches-what-you-type)；請完整輸入。在沒有 Desktop 資料夾的 Linux 上，檔案會寫入您的主目錄。 `.heapsnapshot` 檔案包含程序中的每個字串，包括您的完整對話和認證。請勿將其附加到公開問題或分享。 該命令也會在對話中列印摘要，顯示常駐集合大小、JS 堆積、陣列緩衝區和未計算的原生記憶體，以及它偵測到的任何洩漏指標，例如高記憶體成長率或異常高的開啟控制代碼數量。摘要會說明大部分記憶體是在 JS 堆積中（快照會擷取），還是在原生記憶體中（快照不會擷取）。 對輸出執行以下兩項操作之一：

- **報告它** ：開啟 [GitHub 問題](https://github.com/anthropics/claude-code/issues)並僅附加 `-diagnostics.json` 檔案，該檔案包含列印摘要背後的統計資訊，不包含任何對話內容或認證
- **自行調查** ：如果摘要說大部分記憶體是 JS 堆積，請在 Chrome DevTools 中的 Memory → Load 下開啟 `.heapsnapshot` 檔案，並按保留大小排序以查看什麼佔用了記憶體

如果摘要說大部分記憶體是原生的，快照無法顯示它；請改為在您的報告中包含摘要的洩漏指標。

### 大型表格在終端中被截斷

超過 200 列的 Markdown 表格會呈現其前 200 列，後面跟著 `… N more rows not shown` 行。只有顯示受到限制：完整表格保留在對話中，[`/copy`](https://code.claude.com/docs/zh-TW/commands) 會複製每一列。對於在終端中太大而無法閱讀的表格，請要求 Claude 改為將其寫入檔案。在 v2.1.208 之前，Claude Code 呈現每一列，因此繼續包含非常大型表格的工作階段可能會在重新呈現時停滯。

### Auto-compaction 停止並出現 thrashing 錯誤

如果您看到 `Autocompact is thrashing: the context refilled to the limit...`，自動 compaction 成功，但檔案或工具輸出立即多次重新填充上下文視窗。Claude Code 停止重試以避免在沒有進展的迴圈上浪費 API 呼叫。 若要復原：

1. 要求 Claude 以較小的塊讀取超大檔案，例如特定行範圍或函式，而不是整個檔案
1. 執行 `/compact` 並關注丟棄大輸出，例如 `/compact keep only the plan and the diff`
1. 將大檔案工作移動到 [subagent](https://code.claude.com/docs/zh-TW/sub-agents)，以便它在單獨的上下文視窗中執行
1. 如果早期對話不再需要，執行 `/clear`

### 命令掛起或凍結

如果 Claude Code 似乎無回應：

1. 按 Ctrl+C 嘗試取消目前操作
1. 如果無回應，您可能需要關閉終端並重新啟動

重新啟動不會遺失您的對話。在同一目錄中執行 `claude --resume` 以繼續會話。

### 編輯器整合終端中的文字亂碼或損毀

如果在 VS Code、Cursor 或 Devin Desktop 整合終端中執行 Claude Code 時字元呈現為方塊、塗抹或錯誤的字形，終端的 GPU 渲染器可能是原因。在 Claude Code 中執行 `/terminal-setup` 以將 `terminal.integrated.gpuAcceleration` 設定為 `"off"`，或在您的編輯器設定中手動設定並重新載入視窗。請參閱[終端配置](https://code.claude.com/docs/zh-TW/terminal-config)以了解 `/terminal-setup` 寫入的其他設定。

### 全螢幕渲染中滑鼠滾輪一次滾動一行

在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中，Claude Code 會滾動對話本身，而不是將其留給您的終端。如果每個滾輪刻度移動的行數少於您想要的，請執行 `/scroll-speed` 以提高每個刻度的行數並儲存它，或設定 `CLAUDE_CODE_SCROLL_SPEED` 環境變數，除了在 JetBrains IDE 終端中，Claude Code 會應用自己的滾動處理，兩者都不會生效。請參閱[滑鼠滾輪滾動](https://code.claude.com/docs/zh-TW/fullscreen#mouse-wheel-scrolling)以了解每個接受的值。 若要在不改變速度的情況下移動得更快，請按 `PgUp` 和 `PgDn` 一次滾動半個螢幕。若要將滾動交還給您的終端的原生回滾，請執行 `/tui default` 以切換到經典渲染器。

### 沙箱內的剪貼簿命令（例如 `pbcopy`）失敗

當[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)開啟時，剪貼簿公用程式（例如 `pbcopy`、`xclip` 和 `wl-copy`）可能無法從沙箱化 Bash 命令內部到達系統剪貼簿，在 Claude 將文字傳送到它們後保持您的剪貼簿不變。 若要將 Claude 的輸出放在您的剪貼簿上，請要求 Claude 在其回應中列印內容，然後執行 [`/copy`](https://code.claude.com/docs/zh-TW/commands)。`/copy` 從 Claude Code 程序本身而不是從沙箱化命令寫入剪貼簿，因此沙箱不會阻止它。它可以複製單個程式碼區塊而不是整個回應，它也會將複製的內容寫入檔案並列印路徑，這在剪貼簿寫入無法到達您的終端時提供備用方案，例如透過 SSH。 若要讓管道化命令直接到達剪貼簿，請將 `pbcopy *`、`wl-copy *` 或 `xclip *` 新增到 [`excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands)，以便命令在沙箱外執行。

### 複製的文字無法透過 SSH 到達您的本機剪貼簿

當 Claude Code 在遠端機器上透過 SSH 執行時，它無法在您的本機機器上執行剪貼簿工具。在 tmux 外，當您在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中選取文字或執行 `/copy` 時，Claude Code 會改為將文字作為 OSC 52 逸出序列傳送到您的終端。您的終端決定是否將其放在您的剪貼簿上。`/copy` 報告 `Copied to clipboard`，無論文字是否到達，在 tmux 外選取通知讀取 `sent N chars via OSC 52`。 某些終端不會對 OSC 52 採取行動。iTerm2 會忽略它，直到您開啟**Settings > General > Selection > Applications in terminal may access clipboard**，而 macOS Terminal.app 不支援它。 若要在沒有 OSC 52 的情況下取得文字：

- 按住您的終端的原生選取鍵同時拖曳，然後使用您的終端的常用快捷方式複製，例如 `Cmd+C`。該鍵在 Terminal.app 中是 `Fn`，在 iTerm2 中是 `Option`。[保持原生文字選取](https://code.claude.com/docs/zh-TW/fullscreen#keep-native-text-selection)列出其他終端的鍵。
- 在遠端機器上設定 [`CLAUDE_CODE_DISABLE_MOUSE=1`](https://code.claude.com/docs/zh-TW/env-vars)，以便您的終端為整個工作階段處理選取。

### 搜尋和發現問題

如果搜尋工具、`@file` 提及、自訂代理或自訂 skills 找不到檔案，捆綁的 `ripgrep` 二進位檔可能無法在您的系統上執行。安裝您平台的 `ripgrep` 套件並告訴 Claude Code 改用它：

- macOS
- Ubuntu/Debian
- Alpine
- Arch
- Windows

```
brew install ripgrep

```

```
sudo apt install ripgrep

```

```
apk add ripgrep

```

`ripgrep` 在 Alpine 的社群儲存庫中。如果 `apk` 報告套件遺失，請參閱 [Alpine Linux 設定](https://code.claude.com/docs/zh-TW/setup#alpine-linux-and-musl-based-distributions)。

```
pacman -S ripgrep

```

```
winget install BurntSushi.ripgrep.MSVC

```

然後在您的 shell [環境](https://code.claude.com/docs/zh-TW/env-vars)中或在您的 [`settings.json`](https://code.claude.com/docs/zh-TW/settings-reference#all-settings) 的 `env` 區塊中將 `USE_BUILTIN_RIPGREP` 設定為 `0`：

```
{
  "env": {
    "USE_BUILTIN_RIPGREP": "0"
  }
}

```

若要確認切換生效，請在您的終端中執行 `claude doctor` 並檢查搜尋行是否顯示您的系統 ripgrep 的路徑，而不是 `OK (bundled)`。

### WSL 上的搜尋速度緩慢或結果不完整

在 WSL 上[跨檔案系統工作](https://learn.microsoft.com/en-us/windows/wsl/filesystems)時的磁碟讀取效能損失可能導致在 WSL 上使用 Claude Code 時匹配數少於預期。搜尋仍然有效，但返回的結果比在原生檔案系統上少。 `claude doctor` 在這種情況下將搜尋顯示為正常。 **解決方案：**

1. **提交更具體的搜尋** ：透過指定目錄或檔案類型來減少搜尋的檔案數量：「Search for JWT validation logic in the auth-service package」或「Find use of md5 hash in JS files」。
1. **將專案移動到 Linux 檔案系統** ：如果可能，確保您的專案位於 Linux 檔案系統（`/home/`）而不是 Windows 檔案系統（`/mnt/c/`）。
1. **改用原生 Windows** ：考慮在 Windows 上原生執行 Claude Code 而不是透過 WSL，以獲得更好的檔案系統效能。

## 取得更多協助

如果您遇到此處未涵蓋的問題：

1. 執行 `/doctor` 進行設定檢查，並執行 `/mcp` 檢查 MCP 伺服器狀態
1. 在 Claude Code 中使用 `/feedback` 命令直接向 Anthropic 回報問題
1. 查看 [GitHub 儲存庫](https://github.com/anthropics/claude-code) 以了解已知問題
1. 直接詢問 Claude 其功能和特性。Claude 內建可存取其文件。

如有帳戶、帳單或訂閱問題，請改為聯絡 Anthropic 支援：登入 [claude.ai](https://claude.ai)（Console 使用者：[platform.claude.com](https://platform.claude.com)），點擊左下角的您的首字母縮寫，然後選擇**取得協助** 。請參閱[如何取得支援](https://support.claude.com/en/articles/9015913-how-to-get-support)以了解完整流程，包括每個方案上哪些人可以聯絡人工代理。 是否 助手
