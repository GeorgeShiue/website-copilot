Hooks 是使用者定義的 shell 命令。Claude Code 在其生命週期的特定時間點執行它們，這給予您確定性的控制：某些操作總是會發生，而不是依賴 LLM 選擇執行它們。使用 hooks 來強制執行專案規則、自動化重複性任務，並將 Claude Code 與您現有的工具整合。 對於需要判斷而不是確定性規則的決策，您也可以使用[基於提示的 hooks](https://code.claude.com/docs/zh-TW/hooks-guide#prompt-based-hooks) 或[基於代理的 hooks](https://code.claude.com/docs/zh-TW/hooks-guide#agent-based-hooks)，它們使用 Claude 模型來評估條件。 有關擴展 Claude Code 的其他方式，請參閱[skills](https://code.claude.com/docs/zh-TW/skills)以提供 Claude 額外的指令和可執行命令、[subagents](https://code.claude.com/docs/zh-TW/sub-agents)以在隔離的上下文中執行任務，以及[plugins](https://code.claude.com/docs/zh-TW/plugins)以打包要在專案間共享的擴展。 本指南涵蓋常見用例和入門方式。有關完整的事件架構、JSON 輸入/輸出格式和非同步 hooks 和 MCP 工具 hooks 等進階功能，請參閱 [Hooks 參考](https://code.claude.com/docs/zh-TW/hooks)。

## 設定您的第一個 hook

若要建立 hook，請將 `hooks` 區塊新增到[設定檔](https://code.claude.com/docs/zh-TW/hooks-guide#configure-hook-location)。本逐步解說建立一個桌面通知 hook，因此每當 Claude 等待您的輸入而不是監視終端時，您都會收到警報。 1 將 hook 新增到您的設定 開啟 `~/.claude/settings.json` 並新增 `Notification` hook。如果檔案不存在，請建立它。下面的範例使用 `osascript` 進行 macOS；有關 Linux 和 Windows 命令，請參閱[當 Claude 需要輸入時收到通知](https://code.claude.com/docs/zh-TW/hooks-guide#get-notified-when-claude-needs-input)。

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}

```

如果您的設定檔已經有 `hooks` 鍵，請將 `Notification` 作為現有事件鍵的同級項目新增，而不是替換整個物件。每個事件名稱是單個 `hooks` 物件內的鍵：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'" }]
      }
    ]
  }
}

```

您也可以透過在 CLI 中描述您想要的內容，要求 Claude 為您編寫 hook。 2 驗證設定 輸入 `/hooks` 以開啟 hooks 瀏覽器。您將看到所有可用 hook 事件的列表，每個配置了 hooks 的事件旁邊都有一個計數。選擇 `Notification` 以確認您的新 hook 出現在列表中。選擇 hook 會顯示其詳細資訊：事件、匹配器、類型、來源檔案和命令。 3 測試 hook 按 `Esc` 返回 CLI。按 `Shift+Tab` 直到狀態列顯示 `⏸ manual mode on`，要求 Claude 執行需要權限的操作，然後切換離開終端。您應該會收到桌面通知。 `/hooks` 選單是唯讀的。若要新增、修改或移除 hooks，請直接編輯您的設定 JSON 或要求 Claude 進行變更。

## 您可以自動化的內容

Hooks 讓您在 Claude Code 生命週期的關鍵點執行程式碼：編輯後格式化檔案、在執行前阻止命令、當 Claude 需要輸入時發送通知、在工作階段開始時注入上下文等。有關 hook 事件的完整列表，請參閱 [Hooks 參考](https://code.claude.com/docs/zh-TW/hooks#hook-lifecycle)。 每個範例都包含一個現成可用的配置區塊，您可以將其新增到[設定檔](https://code.claude.com/docs/zh-TW/hooks-guide#configure-hook-location)。 有關 hooks 執行單獨模型審查並將發現結果反饋到工作階段中的生產範例，請參閱 [`security-guidance` plugin 如何與 Claude Code 整合](https://code.claude.com/docs/zh-TW/security-guidance#how-the-plugin-integrates-with-claude-code)。

### 當 Claude 需要輸入時收到通知

每當 Claude 完成工作並需要您的輸入時收到桌面通知，這樣您可以切換到其他任務而無需檢查終端。 此 hook 使用 `Notification` 事件，當 Claude 等待輸入或權限時觸發。請參閱[每個通知類型何時觸發](https://code.claude.com/docs/zh-TW/hooks#notification)以了解確切的時機。下面的每個標籤使用平台的原生通知命令。將此新增到 `~/.claude/settings.json`：

- macOS
- Linux
- Windows (PowerShell)

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}

```

如果沒有出現通知 `osascript` 透過內建的 Script Editor 應用程式路由通知。如果 Script Editor 沒有通知權限，命令會無聲地失敗，macOS 不會提示您授予它。在終端中執行一次以使 Script Editor 出現在您的通知設定中：

```
osascript -e 'display notification "test"'

```

目前不會出現任何內容。開啟**系統設定 > 通知**，在列表中找到 **Script Editor** ，並開啟**允許通知** 。再次執行命令以確認測試通知出現。

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
          }
        ]
      }
    ]
  }
}

```

如果沒有出現通知 `notify-send` 需要桌面通知守護程式，無頭伺服器、SSH 工作階段和大多數容器都沒有。首先直接測試命令：

```
notify-send 'Claude Code' 'test'

```

如果找不到命令，請在 Debian 和 Ubuntu 上安裝 `libnotify-bin` 套件，或安裝您的發行版的等效套件。

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -Command \"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('Claude Code needs your attention', 'Claude Code')\""
          }
        ]
      }
    ]
  }
}

```

如果沒有出現對話框 此命令開啟對話框而不是螢幕角落的通知，因此對話框可能會在終端視窗後面開啟。首先在 PowerShell 中直接測試命令。如果您在 WSL 內執行 Claude Code，`powershell.exe` 必須透過 Windows 互操作在您的 `PATH` 上可用。 空的 `matcher` 會在所有通知類型上觸發。若要僅在特定事件上觸發，請將其設定為以下其中一個值：

| Matcher                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 觸發時機                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `permission_prompt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Claude 需要您批准工具使用或沙箱命令的[網路請求](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)，且提示已等待約六秒                                                                                                                                                                                                                    |
| `idle_prompt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Claude 完成回應約 60 秒前，且您未輸入任何內容                                                                                                                                                                                                                                                                                                           |
| `auth_success`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 驗證完成                                                                                                                                                                                                                                                                                                                                                |
| `elicitation_dialog`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | MCP 伺服器開啟引導表單，且您未輸入約六秒                                                                                                                                                                                                                                                                                                                |
| `elicitation_url_dialog`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | MCP 伺服器要求您開啟瀏覽器 URL，且您未輸入約六秒                                                                                                                                                                                                                                                                                                        |
| `elicitation_complete`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | MCP 伺服器報告[URL 模式引導](https://code.claude.com/docs/zh-TW/hooks#elicitation-input)已完成                                                                                                                                                                                                                                                          |
| `elicitation_response`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | MCP 引導回應被發送回伺服器                                                                                                                                                                                                                                                                                                                              |
| `agent_needs_input`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 背景工作階段開始等待您的輸入，同時 [agent view](https://code.claude.com/docs/zh-TW/agent-view) 已開啟，或當前工作階段詢問您一個[代理團隊隊友的終端設定問題](https://code.claude.com/docs/zh-TW/agent-teams#choose-a-display-mode)，且您未輸入約六秒                                                                                                     |
| `agent_completed`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 背景工作階段完成或失敗。僅在 [agent view](https://code.claude.com/docs/zh-TW/agent-view) 開啟時觸發                                                                                                                                                                                                                                                     |
| `quota_auto_resume_fired`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Claude Code 在 claude.ai 使用限制暫停後繼續您的任務：在重設時，或更早當您在等待期間於 Claude Code 中執行的操作（例如新增使用額度、升級計畫或切換模型）使使用量再次可用時，但有[模型設定例外](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)                                                                       |
| `quota_auto_resume_stale`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | claude.ai 使用限制在您的電腦睡眠超過約 30 分鐘時重設。Claude Code 等待您按 `Enter` 而不是繼續。在較短的睡眠後，它會繼續並改為觸發 `quota_auto_resume_fired`                                                                                                                                                                                             |
| `quota_auto_resume_disabled`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Claude Code 結束其對 claude.ai 使用限制的等待而不繼續您的任務：[`autoContinueAtUsageLimit`](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit) 已關閉，或重設在 Claude Code 自行啟動的等待期間移動超過 24 小時，繼續的任務持續觸發限制，或在到達模型之前阻止了繼續。當您按 `Esc` 或 `Ctrl+C` 或選擇**不自動繼續** 時不觸發 |
| Claude Code 在終端和在 Claude Desktop、VS Code 擴充功能和其他透過 Agent SDK 回答權限請求的主機中以不同方式計時 `permission_prompt`。請參閱[每個通知類型何時觸發](https://code.claude.com/docs/zh-TW/hooks#notification)以了解兩種計時。 `agent_needs_input` 和 `agent_completed` 匹配器需要 Claude Code v2.1.198 或更新版本。 `quota_auto_resume_fired`、`quota_auto_resume_stale` 和 `quota_auto_resume_disabled` 匹配器需要 Claude Code v2.1.234 或更新版本。 在終端工作階段中，沙箱命令的網路請求的 `permission_prompt` 需要 Claude Code v2.1.246 或更新版本。 隊友終端設定問題的 `agent_needs_input` 需要 Claude Code v2.1.248 或更新版本。 輸入 `/hooks` 並選擇 `Notification` 以確認 hook 已註冊。有關完整的事件架構，請參閱 [Notification 參考](https://code.claude.com/docs/zh-TW/hooks#notification)。 |                                                                                                                                                                                                                                                                                                                                                         |

### 編輯後自動格式化程式碼

在 Claude 編輯的每個檔案上自動執行 [Prettier](https://prettier.io/)，以便格式保持一致而無需手動干預。 此 hook 使用 `PostToolUse` 事件搭配 `Edit|Write` 匹配器，因此它只在檔案編輯工具之後執行。該命令使用 [`jq`](https://jqlang.org/) 提取編輯的檔案路徑並將其傳遞給 Prettier。將此新增到您的專案根目錄中的 `.claude/settings.json`：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}

```

若要測試 hook，請要求 Claude 將帶有單引號字串的行新增到 JavaScript 檔案，然後開啟該檔案：使用 Prettier 的預設設定，hook 會將它們重寫為雙引號。 當 hook 成功時，Claude Code 在對話中不顯示任何內容。若要確認 hook 已執行，請檢查編輯的檔案是否已重新格式化，或參閱[偵錯技術](https://code.claude.com/docs/zh-TW/hooks-guide#debug-techniques)。 若要重新格式化特定檔案（無論它如何變更），包括當 `Bash` 命令重寫它時，請改用 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) hook。 本頁上的 Bash 範例使用 `jq` 進行 JSON 解析。使用 `brew install jq`（macOS）、`apt-get install jq`（Debian 和 Ubuntu）安裝它，或參閱 [`jq` 下載](https://jqlang.org/download/)。

### 阻止編輯受保護的檔案

防止 Claude 修改敏感檔案，如 `.env`、`package-lock.json` 或 `.git/` 中的任何內容。Claude 會收到解釋編輯被阻止原因的回饋，因此它可以調整其方法。 此範例使用 hook 呼叫的單獨指令檔。該指令檢查目標檔案路徑是否與受保護的模式列表相符，並以代碼 2 退出以阻止編輯。 1 建立 hook 指令 將此儲存到 `.claude/hooks/protect-files.sh`：

```
#!/bin/bash
# protect-files.sh

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Normalize Windows backslash separators so the patterns below match
FILE_PATH="${FILE_PATH//\\//}"

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0

```

2 在 macOS 和 Linux 上使指令可執行 Hook 指令必須可執行，Claude Code 才能執行它們：

```
chmod +x .claude/hooks/protect-files.sh

```

3 註冊 hook 將 `PreToolUse` hook 新增到 `.claude/settings.json`，在任何 `Edit` 或 `Write` 工具呼叫之前執行指令：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}

```

4 測試 hook 要求 Claude 將註解新增到您的 `.env` 檔案。Claude Code 在執行前阻止編輯，並將指令的 `Blocked:` 訊息作為回饋傳遞給 Claude。

### 壓縮後重新注入上下文

當 Claude 的上下文視窗填滿時，壓縮會總結對話以釋放空間。這可能會遺失重要細節。使用帶有 `compact` 匹配器的 `SessionStart` hook 在每次壓縮後重新注入關鍵上下文。 Claude Code 將您的命令寫入 stdout 的任何純文字新增到 Claude 的上下文中。此範例提醒 Claude 專案慣例和最近的工作。將此新增到您的專案根目錄中的 `.claude/settings.json`：

```
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}

```

您可以將 `echo` 替換為任何產生動態輸出的命令，如 `git log --oneline -5` 以顯示最近的提交。有關在每個工作階段開始時注入上下文，請考慮改用 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)。有關環境變數，請參閱參考中的 [`CLAUDE_ENV_FILE`](https://code.claude.com/docs/zh-TW/hooks#persist-environment-variables)。

### 審計配置變更

追蹤工作階段期間設定或 skills 檔案何時變更。`ConfigChange` 事件在外部程序或編輯器修改配置檔案時觸發，因此您可以記錄變更以進行合規性檢查或阻止未授權的修改。 此範例將每個變更附加到審計日誌。將此新增到 `~/.claude/settings.json`：

```
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log"
          }
        ]
      }
    ]
  }
}

```

匹配器按配置類型篩選：`user_settings`、`project_settings`、`local_settings`、`policy_settings` 或 `skills`。要阻止變更生效，以代碼 2 退出或傳回 `{"decision": "block"}`。有關完整的輸入架構，請參閱 [ConfigChange 參考](https://code.claude.com/docs/zh-TW/hooks#configchange)。 若要確認 hook 記錄變更，請在工作階段執行時在另一個編輯器中編輯設定檔，然後開啟 `~/claude-config-audit.log`：hook 會為每個變更附加一行 JSON，包含時間戳記、來源和檔案路徑。

### 當目錄或檔案變更時重新載入環境

某些專案根據您所在的目錄設定不同的環境變數。[direnv](https://direnv.net/) 之類的工具在您的 shell 中自動執行此操作，但 Claude 的 Bash 工具不會自行選取這些變更。 配對 `SessionStart` hook 與 `CwdChanged` hook 可以修復此問題。`SessionStart` 載入您啟動時所在目錄的變數，`CwdChanged` 在 Claude 每次變更目錄時重新載入它們。兩者都寫入 `CLAUDE_ENV_FILE`，Claude Code 在每個 Bash 命令之前執行為指令碼前置。將此新增到 `~/.claude/settings.json`：

```
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ],
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}

```

在每個具有 `.envrc` 的目錄中執行一次 `direnv allow`，以便允許 direnv 載入它。如果您使用 devbox 或 nix 而不是 direnv，相同的模式適用於 `devbox shellenv` 或 `devbox global shellenv` 代替 `direnv export bash`。 若要對特定檔案而不是每次目錄變更做出反應，請使用 `FileChanged` 搭配 `matcher` 列出要監視的檔案名稱（以 `|` 分隔）。建立監視清單時，Claude Code 會將此值分割為字面檔案名稱，而不是作為正規表達式進行評估。有關輸入架構、`watchPaths` 輸出和 `CLAUDE_ENV_FILE` 詳細資訊，請參閱 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged)。此範例監視工作目錄中 `.envrc` 和 `.env` 的變更：

```
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": ".envrc|.env",
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}

```

有關輸入架構、`watchPaths` 輸出和 `CLAUDE_ENV_FILE` 詳細資訊，請參閱 [CwdChanged](https://code.claude.com/docs/zh-TW/hooks#cwdchanged) 和 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) 參考項目。

### 自動批准特定權限提示

跳過您始終允許的工具呼叫的批准對話。此範例自動批准 `ExitPlanMode`，這是 Claude 在完成呈現計畫並要求繼續時呼叫的工具，因此您不會在每次計畫準備好時被提示。 與上面的退出代碼範例不同，自動批准要求您的 hook 將 JSON 決策寫入 stdout。Claude Code 在即將要求您的權限時執行 `PermissionRequest` hooks，如果您的 hook 傳回 `"behavior": "allow"`，Claude Code 會代表您回答請求。 匹配器將 hook 的範圍限制為僅 `ExitPlanMode`，因此不會影響其他提示。將此新增到 `~/.claude/settings.json`：

```
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}

```

當 hook 批准時，Claude Code 退出計畫模式並恢復進入計畫模式之前處於活動狀態的任何權限模式。文字記錄顯示「由 PermissionRequest hook 允許」，其中對話會出現。hook 路徑始終保持當前對話：它無法清除上下文並以對話可以執行的方式啟動新的實現工作階段。 若要改為設定特定的權限模式，您的 hook 的輸出可以包含帶有 `setMode` 項目的 `updatedPermissions` 陣列。`mode` 值是任何權限模式，如 `default`、`acceptEdits` 或 `bypassPermissions`，`destination: "session"` 僅將其應用於當前工作階段。 `bypassPermissions` 只有在您啟動工作階段時繞過模式已經可用的情況下才適用：`--dangerously-skip-permissions`、`--permission-mode bypassPermissions`、`--allow-dangerously-skip-permissions` 或[使用者、`--settings` 或受管設定](https://code.claude.com/docs/zh-TW/settings-reference#permissions-defaultmode)中的 `permissions.defaultMode: "bypassPermissions"`。如果繞過模式已被 [`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/zh-TW/permissions#managed-settings) 停用，或您是在[受限模式](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)中啟動工作階段，則它不適用。Claude Code 永遠不會將其儲存為 `defaultMode`。 若要將工作階段切換到 `acceptEdits`，您的 hook 會將此 JSON 寫入 stdout：

```
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedPermissions": [
        { "type": "setMode", "mode": "acceptEdits", "destination": "session" }
      ]
    }
  }
}

```

保持匹配器盡可能狹窄。在 `.*` 上進行匹配或留空匹配器會自動批准每個工具權限提示，包括檔案寫入和 shell 命令。有關決策欄位的完整集合，請參閱 [PermissionRequest 參考](https://code.claude.com/docs/zh-TW/hooks#permissionrequest-decision-control)。

## Hooks 如何工作

Claude Code 在其生命週期的特定點觸發 hook 事件。當事件觸發時，Claude Code 會並行執行所有匹配的 hooks；請參閱 [Hook 處理程式欄位](https://code.claude.com/docs/zh-TW/hooks#hook-handler-fields)以了解如何處理重複的處理程式。下表顯示每個事件及其觸發時間：

| 事件                                                                                                                         | 何時觸發                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SessionStart`                                                                                                               | 當工作階段開始或繼續時                                                                                                                                                          |
| `Setup`                                                                                                                      | 當您使用 `--init-only` 啟動 Claude Code，或在 `-p` 模式中使用 `--init` 或 `--maintenance` 時。用於 CI 或指令碼中的一次性準備                                                    |
| `UserPromptSubmit`                                                                                                           | 當您提交提示詞時，在 Claude 處理之前                                                                                                                                            |
| `UserPromptExpansion`                                                                                                        | 當使用者輸入的命令擴展為提示詞時，在到達 Claude 之前。可以阻止擴展                                                                                                              |
| `PreToolUse`                                                                                                                 | 在工具呼叫執行之前。可以阻止它                                                                                                                                                  |
| `PermissionRequest`                                                                                                          | 當工具呼叫需要權限決定時                                                                                                                                                        |
| `PermissionDenied`                                                                                                           | 當自動模式拒絕工具呼叫時，包括沒有分類器判決的拒絕。使用 JSON `hookSpecificOutput.retry: true` 告訴模型它可能重試被拒絕的工具呼叫。Claude Code 在分類器未產生判決時忽略 `retry` |
| `PostToolUse`                                                                                                                | 在工具呼叫成功後                                                                                                                                                                |
| `PostToolUseFailure`                                                                                                         | 在工具呼叫失敗後                                                                                                                                                                |
| `PostToolBatch`                                                                                                              | 在完整的平行工具呼叫批次解決後，在下一個模型呼叫之前                                                                                                                            |
| `Notification`                                                                                                               | 當 Claude Code 傳送通知時                                                                                                                                                       |
| `MessageDisplay`                                                                                                             | 在助手訊息文字顯示時                                                                                                                                                            |
| `SubagentStart`                                                                                                              | 當子代理被生成時                                                                                                                                                                |
| `SubagentStop`                                                                                                               | 當子代理完成時                                                                                                                                                                  |
| `TaskCreated`                                                                                                                | 當透過 `TaskCreate` 建立任務時                                                                                                                                                  |
| `TaskCompleted`                                                                                                              | 當任務被標記為已完成時                                                                                                                                                          |
| `Stop`                                                                                                                       | 當 Claude 完成回應時                                                                                                                                                            |
| `StopFailure`                                                                                                                | 當回合因 API 錯誤而結束時                                                                                                                                                       |
| `TeammateIdle`                                                                                                               | 當[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友即將閒置時                                                                                                      |
| `InstructionsLoaded`                                                                                                         | 當 CLAUDE.md 或 `.claude/rules/*.md` 檔案被載入到上下文時。在工作階段開始時以及在工作階段期間延遲載入檔案時觸發                                                                 |
| `ConfigChange`                                                                                                               | 當設定檔在工作階段期間變更時                                                                                                                                                    |
| `CwdChanged`                                                                                                                 | 當工作目錄變更時，例如當 Claude 執行 `cd` 命令時。適用於使用 direnv 等工具進行反應式環境管理                                                                                    |
| `DirectoryAdded`                                                                                                             | 當工作目錄在工作階段中期透過 `/add-dir` 或 SDK `register_repo_root` 控制請求新增時                                                                                              |
| `FileChanged`                                                                                                                | 當監視的檔案在磁碟上變更時。`matcher` 欄位指定要監視的檔案名稱                                                                                                                  |
| `WorktreeCreate`                                                                                                             | 當透過 `--worktree`、`isolation: "worktree"` 建立 worktree 時，或用於背景工作階段時。取代預設的 git 行為                                                                        |
| `WorktreeRemove`                                                                                                             | 當在工作階段結束時、子代理完成時或您刪除背景工作階段時移除 worktree 時                                                                                                          |
| `PreCompact`                                                                                                                 | 在上下文壓縮之前                                                                                                                                                                |
| `PostCompact`                                                                                                                | 在上下文壓縮完成後                                                                                                                                                              |
| `PreModelSwitch`                                                                                                             | 在 Claude Code 應用您或用戶端要求的模型切換之前。可以阻止切換                                                                                                                   |
| `PostModelSwitch`                                                                                                            | 在工作階段的模型變更後，包括 Claude Code 自行進行的變更，例如當您繼續工作階段時恢復模型                                                                                         |
| `Elicitation`                                                                                                                | 當 MCP 伺服器在工具呼叫期間要求使用者輸入時                                                                                                                                     |
| `ElicitationResult`                                                                                                          | 在使用者回應 MCP 引出後，在回應傳送回伺服器之前                                                                                                                                 |
| `SessionEnd`                                                                                                                 | 當工作階段終止時                                                                                                                                                                |
| 每個 hook 都有一個 `type` 來決定它如何執行。大多數 hooks 使用 `"type": "command"`，它執行 shell 命令。還有四種其他類型可用： |                                                                                                                                                                                 |

- `"type": "http"`：POST 事件資料到 URL。請參閱 [HTTP hooks](https://code.claude.com/docs/zh-TW/hooks-guide#http-hooks)。
- `"type": "mcp_tool"`：在已連接的 MCP 伺服器上呼叫工具。請參閱 [MCP tool hooks](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields)。
- `"type": "prompt"`：單輪 LLM 評估。請參閱 [Prompt-based hooks](https://code.claude.com/docs/zh-TW/hooks-guide#prompt-based-hooks)。
- `"type": "agent"`：具有工具存取的多輪驗證。Agent hooks 是實驗性的，可能會改變。請參閱 [Agent-based hooks](https://code.claude.com/docs/zh-TW/hooks-guide#agent-based-hooks)。

### 合併來自多個 hooks 的結果

當多個 hooks 相符同一事件時，每個 hook 的命令都會執行到完成，然後 Claude Code 合併結果。一個 hook 傳回 `deny` 不會阻止同級 hooks 執行。不要依賴一個 hook 的 `deny` 來抑制另一個 hook 中的副作用。 所有匹配的 hooks 完成後，Claude Code 合併它們的輸出。對於 `PreToolUse` 權限決策，最具限制性的答案獲勝，順序為 `deny`、`defer`、`ask`、`allow`。來自 `additionalContext` 的文字會從每個 hook 保留並一起傳遞給 Claude。 下面的範例在 `Bash` 上註冊了兩個 `PreToolUse` hooks。第一個將每個命令附加到日誌檔案並退出 0。第二個執行一個指令碼，當命令包含 `rm -rf` 時退出 2 以拒絕：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r .tool_input.command >> ~/.claude/bash.log"
          },
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm-rf.sh"
          }
        ]
      }
    ]
  }
}

```

當 Claude 嘗試執行 `rm -rf /tmp/build` 時，兩個 hooks 並行執行。日誌記錄 hook 將命令寫入 `~/.claude/bash.log` 並退出 0，這表示沒有決策。防護欄 hook 退出 2，這拒絕了工具呼叫。拒絕獲勝，所以 Claude Code 阻止命令並向 Claude 顯示防護欄的 stderr。日誌項仍然被寫入，因為日誌記錄 hook 已經執行。

### 讀取輸入並傳回輸出

Hooks 透過 stdin、stdout、stderr 和退出代碼與 Claude Code 通訊。當事件觸發時，Claude Code 將事件特定的資料作為 JSON 傳遞到您的指令的 stdin。您的指令讀取該資料、執行其工作，並透過退出代碼告訴 Claude Code 接下來要做什麼。

#### Hook 輸入

每個事件都包含常見欄位，如 `session_id`（工作階段的唯一 ID）和 `cwd`（事件觸發時的工作目錄），但每個事件類型都新增不同的資料。當 Claude 執行 Bash 命令時，`PreToolUse` hook 在 stdin 上接收這些欄位：

- `hook_event_name`：觸發 hook 的事件
- `tool_name`：Claude 即將使用的工具
- `tool_input`：Claude 傳遞給工具的引數。對於 Bash，其 `command` 欄位保存 shell 命令。

例如，`npm test` 命令的 hook 輸入看起來像這樣：

```
{
  "session_id": "abc123",
  "cwd": "/Users/sarah/myproject",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  }
}

```

您的指令可以解析該 JSON 並對任何這些欄位採取行動。`UserPromptSubmit` hooks 改為取得 `prompt` 文字，`SessionStart` hooks 取得 `source`（`startup`、`resume`、`clear`、`compact` 或 `fork`），等等。有關共享欄位，請參閱參考中的 [Common input fields](https://code.claude.com/docs/zh-TW/hooks#common-input-fields)，以及每個事件的部分以了解事件特定的架構。

#### Hook 輸出

您的指令透過寫入 stdout 或 stderr 並以特定代碼退出來告訴 Claude Code 接下來要做什麼。以下 `PreToolUse` hook 阻止命令：

```
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q "drop table"; then
  echo "Blocked: dropping tables is not allowed" >&2  # stderr 變成 Claude 的回饋
  exit 2 # exit 2 = 阻止操作
fi

exit 0  # exit 0 = 沒有決策；正常的權限流程適用

```

退出代碼決定接下來會發生什麼：

- **Exit 0** ：您的 hook 透過其退出代碼報告沒有異議。
  - 對於 `PreToolUse` hook，這不會批准工具呼叫：正常的 [permission flow](https://code.claude.com/docs/zh-TW/permissions) 仍然適用。
  - 對於 `UserPromptSubmit`、`UserPromptExpansion`、`SessionStart` 和 `PostModelSwitch` hooks，Claude Code 將 stdout [視為純文字](https://code.claude.com/docs/zh-TW/hooks#exit-code-0)新增到 Claude 的上下文中。
- **Exit 2** ：Claude Code 阻止操作。寫入原因到 stderr。它落在哪裡取決於事件：某些事件將其提供給 Claude 作為回饋，以便它可以調整，其他事件向使用者顯示它，還有一些（例如 `ConfigChange` 和 `Elicitation`）不顯示任何訊息。某些事件無法被阻止：對於 `SessionStart` 和其他事件，exit 2 向使用者顯示 stderr，執行繼續。有關完整清單，請參閱 [exit code 2 behavior per event](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event)。
- **任何其他退出代碼** ：對於大多數事件，結果取決於您的 hook 列印到 stdout 的內容：
  - 通過架構驗證的已解析物件：Claude Code 忽略退出代碼，JSON 單獨決定結果，hook 不被報告為錯誤。每個事件的例外（例如 `WorktreeCreate` 在任何非零退出時失敗）列在參考的 [Exit code output](https://code.claude.com/docs/zh-TW/hooks#exit-code-output) 部分中。
  - 未通過架構驗證的已解析物件，或 Claude Code [嘗試解析為 JSON](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 但不是有效 JSON 的 stdout：非阻止錯誤；通知包含驗證或解析訊息。
  - Claude Code [視為純文字](https://code.claude.com/docs/zh-TW/hooks#exit-code-0)的 stdout，或空 stdout：操作作為非阻止錯誤進行。文字記錄顯示 `<hook name> hook error` 通知，然後是 stderr 的第一行，前綴為 `Failed with non-blocking status code:`。若要捕獲完整的 stderr，請使用 `claude --debug` 或在工作階段中執行 `/debug` 啟用 [debug logging](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)。

#### 結構化 JSON 輸出

退出代碼只讓您阻止或保持沉默。為了獲得更多控制，退出 0 並改為將 JSON 物件列印到 stdout。 使用 exit 2 以 stderr 訊息阻止，或使用 exit 0 和 JSON 進行結構化控制。每個 hook 選擇一種方法。有關混合它們時會發生什麼，請參閱 [Exit code output](https://code.claude.com/docs/zh-TW/hooks#exit-code-output)。 例如，`PreToolUse` hook 可以拒絕工具呼叫並告訴 Claude 為什麼，或將其升級給使用者以獲得批准：

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep for better performance"
  }
}

```

使用 `"deny"`，Claude Code 會取消工具呼叫並將 `permissionDecisionReason` 回饋給 Claude。 在 `PreToolUse` 上，Claude Code 處理每個 `permissionDecision` 值如下：

- `"allow"`：跳過互動式權限提示。拒絕和詢問規則（包括企業受管拒絕清單）仍然適用，標記為 [`requiresUserInteraction`](https://code.claude.com/docs/zh-TW/mcp#require-approval-for-a-specific-tool) 的 MCP 工具的提示，以及[您的組織設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 的連接器工具在該設定到達 Claude Code 的工作階段中的提示也同樣適用
- `"deny"`：取消工具呼叫並將原因傳送給 Claude
- `"ask"`：照常向使用者顯示權限提示

第四個值 `"defer"` 在 [non-interactive mode](https://code.claude.com/docs/zh-TW/headless) 中使用 `-p` 旗標時可用。它以保留的工具呼叫退出程序，以便 Agent SDK 包裝器可以收集輸入並繼續。請參閱參考中的 [Defer a tool call for later](https://code.claude.com/docs/zh-TW/hooks#defer-a-tool-call-for-later)。 `PreModelSwitch` hook 傳回相同的 `permissionDecision` 欄位：`"allow"` 讓模型切換進行，`"deny"` 取消它。`"ask"` 在您在互動工作階段中執行 `/model` 時讓您確認切換；在其他地方，Claude Code 將 `"ask"` 視為拒絕。請參閱 [PreModelSwitch decision control](https://code.claude.com/docs/zh-TW/hooks#premodelswitch-decision-control)。 其他事件使用不同的決策模式。例如，`PostToolUse` 和 `Stop` hooks 使用頂級 `decision: "block"` 欄位，而 `PermissionRequest` 使用 `hookSpecificOutput.decision.behavior`。有關按事件的完整分解，請參閱參考中的 [summary table](https://code.claude.com/docs/zh-TW/hooks#decision-control)。 對於 `UserPromptSubmit` hooks，改用 `hookSpecificOutput.additionalContext` 將文字注入到 Claude 的上下文中。將 `additionalContext` 嵌套在 `hookSpecificOutput` 內；如果您將其放在 JSON 的頂級，Claude Code 會無聲地忽略它。例如，此輸出將目前分支狀態新增到每個提示：

```
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Current branch: release-42. Deploy freeze until Friday."
  }
}

```

有關完整的輸出形狀（包括阻止提示和設定工作階段標題），請參閱 [UserPromptSubmit decision control](https://code.claude.com/docs/zh-TW/hooks#userpromptsubmit-decision-control)。 具有 `type: "prompt"` 的 Hooks 以不同方式處理輸出：請參閱 [Prompt-based hooks](https://code.claude.com/docs/zh-TW/hooks-guide#prompt-based-hooks)。

### 使用匹配器篩選 hooks

沒有匹配器，hook 會在其事件的每次出現時觸發。匹配器讓您縮小範圍。例如，如果您只想在檔案編輯後執行格式化程式（而不是在每次工具呼叫後），請將匹配器新增到您的 `PostToolUse` hook：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "prettier --write ..." }
        ]
      }
    ]
  }
}

```

`"Edit|Write"` 匹配器只在 Claude 使用 `Edit` 或 `Write` 工具時觸發，而不是在它使用 `Bash`、`Read` 或任何其他工具時。在 Claude Code v2.1.191 或更新版本上，逗號以相同方式分隔替代項，因此 `"Edit, Write"` 是等效的。請參閱 [Matcher patterns](https://code.claude.com/docs/zh-TW/hooks#matcher-patterns) 以了解純名稱和正規表達式如何被評估。 Claude 也可以透過執行 shell 命令來建立或修改檔案。如果您的 hook 必須看到每個檔案變更（例如用於合規掃描或稽核日誌），請新增一個 [`Stop`](https://code.claude.com/docs/zh-TW/hooks#stop) hook，它每輪掃描一次工作樹。為了獲得每次呼叫的覆蓋範圍，也請匹配 `Bash|PowerShell` 並讓您的指令使用 `git status --porcelain` 列出修改和未追蹤的檔案。[PowerShell hook input section](https://code.claude.com/docs/zh-TW/hooks#powershell) 解釋了為什麼單獨匹配 `Bash` 是不夠的。若要在特定檔案在磁碟上變更時執行 hook（無論是什麼寫入它），請使用 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) hook。 每個事件類型都在特定欄位上進行匹配：

| 事件                                                                                                                                                            | 匹配器篩選的內容                                                                                                    | 範例匹配器值                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`                                                                      | 工具名稱                                                                                                            | `Bash`、\`Edit                                                                                                                                                                                                                                                                 |
| `SessionStart`                                                                                                                                                  | 工作階段如何開始                                                                                                    | `startup`、`resume`、`clear`、`compact`、`fork`                                                                                                                                                                                                                                |
| `Setup`                                                                                                                                                         | 哪個 CLI 旗標觸發了設定                                                                                             | `init`、`maintenance`                                                                                                                                                                                                                                                          |
| `SessionEnd`                                                                                                                                                    | 工作階段為什麼結束                                                                                                  | `clear`、`resume`、`logout`、`prompt_input_exit`、`other`                                                                                                                                                                                                                      |
| `Notification`                                                                                                                                                  | 通知類型                                                                                                            | `permission_prompt`、`idle_prompt`、`auth_success`、`elicitation_dialog`、`elicitation_url_dialog`、`elicitation_complete`、`elicitation_response`、`agent_needs_input`、`agent_completed`、`quota_auto_resume_fired`、`quota_auto_resume_stale`、`quota_auto_resume_disabled` |
| `SubagentStart`                                                                                                                                                 | agent 類型                                                                                                          | `general-purpose`、`Explore`、`Plan` 或自訂 agent 名稱                                                                                                                                                                                                                         |
| `PreCompact`、`PostCompact`                                                                                                                                     | 什麼觸發了壓縮                                                                                                      | `manual`、`auto`                                                                                                                                                                                                                                                               |
| `PreModelSwitch`、`PostModelSwitch`                                                                                                                             | 工作階段切換到的模型的規範名稱，如 [PreModelSwitch](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 下所述 | `claude-opus-5`、\`claude-opus-4-6                                                                                                                                                                                                                                             |
| `SubagentStop`                                                                                                                                                  | agent 類型                                                                                                          | 與 `SubagentStart` 相同的值                                                                                                                                                                                                                                                    |
| `ConfigChange`                                                                                                                                                  | 配置來源                                                                                                            | `user_settings`、`project_settings`、`local_settings`、`policy_settings`、`skills`                                                                                                                                                                                             |
| `DirectoryAdded`                                                                                                                                                | 目錄如何被新增                                                                                                      | `slash_command`、`register_repo_root`                                                                                                                                                                                                                                          |
| `StopFailure`                                                                                                                                                   | 錯誤類型                                                                                                            | `rate_limit`、`overloaded`、`authentication_failed`、`oauth_org_not_allowed`、`account_on_hold`、`billing_error`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens`、`cloud_credential_error`、`unknown`                                               |
| `InstructionsLoaded`                                                                                                                                            | 載入原因                                                                                                            | `session_start`、`nested_traversal`、`path_glob_match`、`include`、`compact`                                                                                                                                                                                                   |
| `Elicitation`                                                                                                                                                   | MCP 伺服器名稱                                                                                                      | 您配置的 MCP 伺服器名稱                                                                                                                                                                                                                                                        |
| `ElicitationResult`                                                                                                                                             | MCP 伺服器名稱                                                                                                      | 與 `Elicitation` 相同的值                                                                                                                                                                                                                                                      |
| `FileChanged`                                                                                                                                                   | 字面檔案名稱以監視（請參閱 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged)）                    | \`.envrc                                                                                                                                                                                                                                                                       |
| `UserPromptExpansion`                                                                                                                                           | 命令名稱                                                                                                            | 您的 skill 或命令名稱                                                                                                                                                                                                                                                          |
| `UserPromptSubmit`、`PostToolBatch`、`Stop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`WorktreeCreate`、`WorktreeRemove`、`CwdChanged`、`MessageDisplay` | 不支援匹配器                                                                                                        | 始終在每次出現時觸發                                                                                                                                                                                                                                                           |
| 下面的標籤頁顯示不同事件類型上匹配器的更多範例。                                                                                                                |                                                                                                                     |                                                                                                                                                                                                                                                                                |

- 記錄每個 Bash 命令
- 匹配 MCP 工具
- 在工作階段結束時清理

只匹配 `Bash` 工具呼叫並將每個命令記錄到檔案。`PostToolUse` 事件在命令完成後觸發，因此 `tool_input.command` 包含執行的內容。hook 在 stdin 上接收事件資料作為 JSON，`jq -r '.tool_input.command'` 只提取命令字串，`>>` 將其附加到日誌檔案：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' >> ~/.claude/command-log.txt"
          }
        ]
      }
    ]
  }
}

```

MCP 工具使用與內建工具不同的命名慣例：`mcp__<server>__<tool>`，其中 `<server>` 是 MCP 伺服器名稱，`<tool>` 是它提供的工具。例如，`mcp__github__search_repositories` 或 `mcp__filesystem__read_file`。來自 [plugin-bundled server](https://code.claude.com/docs/zh-TW/mcp#plugin-provided-mcp-servers) 的工具使用範圍伺服器段，例如 `mcp__plugin_my-plugin_db__query`。使用正規表達式匹配器來針對來自特定伺服器的所有工具，或使用 `mcp__.*__write.*` 之類的模式跨伺服器進行匹配。有關完整的範例列表，請參閱參考中的 [Match MCP tools](https://code.claude.com/docs/zh-TW/hooks#match-mcp-tools)。下面的命令使用 `jq` 從 hook 的 JSON 輸入中提取工具名稱，並將其寫入 stderr。寫入 stderr 會保持 stdout 乾淨以用於 JSON 輸出，並將訊息發送到 [debug log](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__github__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"GitHub tool called: $(jq -r '.tool_name')\" >&2"
          }
        ]
      }
    ]
  }
}

```

`SessionEnd` 事件支援工作階段結束原因的匹配器。此 hook 只在 `clear` 時觸發（當您執行 `/clear` 時），而不是在正常退出時：

```
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "clear",
        "hooks": [
          {
            "type": "command",
            "command": "rm -f /tmp/claude-scratch-*.txt"
          }
        ]
      }
    ]
  }
}

```

#### 使用 `if` 欄位按工具名稱和引數篩選

`if` 欄位使用 [permission rule syntax](https://code.claude.com/docs/zh-TW/permissions) 按工具名稱和引數一起篩選 hooks，因此 hook 程序只在工具呼叫相符時生成。這超越了 `matcher`，它只在工具名稱級別篩選。 例如，這個配置只在 Claude 使用 `git` 命令而不是所有 Bash 命令時執行 hook：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-git-policy.sh"
          }
        ]
      }
    ]
  }
}

```

您的 hook 命令是否執行取決於您的 `if` 模式的形狀和 Claude 正在呼叫的 Bash 命令：

| `if` 模式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Bash 命令              | Hook 執行？ | 為什麼                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------- | ----------- | ----------------------------------------------------------- |
| `Bash(git *)`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `git push`             | 是          | 命令名稱相符                                                |
| `Bash(git *)`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `npm test && git push` | 是          | 每個子命令都被檢查；`git push` 相符                         |
| `Bash(git *)`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `echo $(git log)`      | 是          | `$()` 和反引號內的命令被檢查；`git log` 相符                |
| `Bash(git *)`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `echo $(date)`         | 否          | 沒有子命令相符 `git *`                                      |
| `Bash(git push *)`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | `echo $(date)`         | 是          | 指定超過命令名稱的模式在 `$()`、反引號或 `$VAR` 上執行 hook |
| 當 Claude Code 無法確定 Bash 輸入執行哪些命令時，它會無論如何執行您的 hook。[Bash matching table](https://code.claude.com/docs/zh-TW/hooks#bash-if-matching) 涵蓋 Claude Code 可以和不能按子命令縮小的命令形狀。因為篩選器是盡力而為，請使用 [permission system](https://code.claude.com/docs/zh-TW/permissions) 而不是 hook 來強制執行硬允許或拒絕。 `if` 欄位接受與權限規則相同的模式：`"Bash(git *)"`、`"Edit(*.ts)"` 等。若要匹配多個工具名稱，請使用每個都有自己的 `if` 值的單獨處理程式，或在 `matcher` 級別進行匹配，其中支援管道交替。 `if` 只適用於工具事件：`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest` 和 `PermissionDenied`。將其新增到任何其他事件會防止 hook 執行。 |                        |             |                                                             |

### 配置 hook 位置

您新增 hook 的位置決定了其範圍：

| 位置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 範圍                                                                                                                                            | 可共享                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| `~/.claude/settings.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 您的所有專案                                                                                                                                    | 否，本機到您的機器                     |
| `.claude/settings.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 單個專案                                                                                                                                        | 是，可以提交到儲存庫                   |
| `.claude/settings.local.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 單個專案                                                                                                                                        | 否，gitignored 當 Claude Code 建立它時 |
| 受管理的原則設定                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 組織範圍                                                                                                                                        | 是，由管理員控制                       |
| [Plugin](https://code.claude.com/docs/zh-TW/plugins) `hooks/hooks.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 啟用外掛時                                                                                                                                      | 是，與外掛捆綁                         |
| [Skill](https://code.claude.com/docs/zh-TW/skills) frontmatter                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 一旦 skill 被呼叫，工作階段的其餘部分。請參閱 [Hooks in skills and agents](https://code.claude.com/docs/zh-TW/hooks#hooks-in-skills-and-agents) | 是，在 skill 檔案中定義                |
| [Subagent](https://code.claude.com/docs/zh-TW/sub-agents) frontmatter                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 當該 subagent 執行時                                                                                                                            | 是，在 subagent 檔案中定義             |
| 在 Claude Code 中執行 [`/hooks`](https://code.claude.com/docs/zh-TW/hooks#the-%2Fhooks-menu) 以瀏覽按事件分組的所有配置的 hooks。 若要禁用 hooks，請在設定檔中設定 `"disableAllHooks": true`。Claude Code 讀取 [settings precedence](https://code.claude.com/docs/zh-TW/hooks#disable-or-remove-hooks) 適用後剩下的值，因此專案的設定檔可以覆蓋您的。在受管理的設定中配置的 Hooks 仍會執行，除非 `disableAllHooks` 也在那裡設定。有關每個級別的完整範圍，請參閱 [`disableAllHooks`](https://code.claude.com/docs/zh-TW/settings-reference#disableallhooks)。 如果您在 Claude Code 執行時直接編輯設定檔，檔案監視程式通常會自動選取 hook 變更。 |                                                                                                                                                 |                                        |

## 基於提示的 hooks

對於需要判斷而不是確定性規則的決策，使用 `type: "prompt"` hooks。Claude Code 不執行 shell 命令，而是將您的提示和 hook 的輸入資料傳送到 Claude 模型（預設為 Haiku）以做出決策。如果您需要更多功能，可以使用 `model` 欄位指定不同的模型。 模型的唯一工作是傳回其決策作為 JSON：

- `"ok": true`：操作繼續
- `"ok": false`：發生的情況取決於事件：
  - `Stop` 和 `SubagentStop`：`reason` 被回饋給 Claude，以便它繼續工作，除非回應也設定 `"impossible": true` 以標記該條件為永遠無法滿足的條件，在這種情況下 Claude Code 允許停止並結束回合
  - `PreToolUse`：工具呼叫被拒絕；預設情況下回合結束，拒絕 `reason` 在聊天中顯示為警告行。在 hook 上設定 `continueOnBlock: true` 以改為將 `reason` 傳回給 Claude 作為工具錯誤，以便它可以調整並繼續。在 v2.1.210 之前，拒絕 `reason` 被傳回給 Claude 作為工具錯誤，回合繼續
  - `PostToolUse`：預設情況下回合結束，`reason` 在聊天中顯示為警告行。設定 `continueOnBlock: true` 以將 `reason` 回饋給 Claude 並改為繼續回合
  - `PostToolBatch`、`UserPromptSubmit` 和 `UserPromptExpansion`：回合結束，`reason` 在聊天中顯示為警告行

此範例使用 `Stop` hook 詢問模型是否所有請求的任務都已完成。如果模型傳回 `"ok": false` 因為條件尚未滿足，Claude 會繼續工作並使用 `reason` 作為其下一個指令：

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}."
          }
        ]
      }
    ]
  }
}

```

有關完整的配置選項，請參閱參考中的[基於提示的 hooks](https://code.claude.com/docs/zh-TW/hooks#prompt-based-hooks)。

## 基於代理的 hooks

Agent hooks 是實驗性的。行為和配置可能在未來版本中改變。對於生產工作流程，優先使用[命令 hooks](https://code.claude.com/docs/zh-TW/hooks#command-hook-fields)。 當驗證需要檢查檔案或執行命令時，使用 `type: "agent"` hooks。與只進行單個 LLM 呼叫的提示 hooks 不同，代理 hooks 生成一個 subagent，可以讀取檔案、搜尋程式碼和使用其他工具在傳回決策之前驗證條件。 代理 hooks 使用 `"ok"` / `"reason"` 回應格式，預設超時時間更長（60 秒），最多 50 個工具使用輪次。它們不支援提示 hook 的 `impossible` 欄位。當 `ok: false` 時，Claude Code 處理代理 hook 的方式與處理在同一事件上設定 `continueOnBlock: true` 的提示 hook 相同，因此在 `PreToolUse` 和 `PostToolUse` 上輪次會繼續；代理 hooks 沒有 `continueOnBlock` 欄位。請參閱[代理 hook 配置](https://code.claude.com/docs/zh-TW/hooks#agent-hook-configuration)以了解欄位，包括 Claude Code 用 hook 的 JSON 輸入替換的 `$ARGUMENTS` 預留位置。 此範例驗證在允許 Claude 停止之前測試通過：

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}

```

當 hook 輸入資料本身足以做出決策時，使用提示 hooks。當您需要根據程式碼庫的實際狀態驗證某些內容時，使用代理 hooks。 有關完整的配置選項，請參閱參考中的[基於代理的 hooks](https://code.claude.com/docs/zh-TW/hooks#agent-based-hooks)。

## HTTP hooks

使用 `type: "http"` hooks 將事件資料 POST 到 HTTP 端點，而不是執行 shell 命令。端點接收命令 hook 在 stdin 上接收的相同 JSON，並使用相同的 JSON 格式透過 HTTP 回應主體傳回結果。 HTTP hooks 在您希望 Web 伺服器、雲端函數或外部服務處理 hook 邏輯時很有用：例如，一個共享的審計服務，在整個團隊中記錄工具使用事件。 此範例將每個工具使用 POST 到本機記錄服務：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}

```

端點應使用與命令 hooks 相同的[輸出格式](https://code.claude.com/docs/zh-TW/hooks#json-output)傳回 JSON 回應主體。要阻止工具呼叫，傳回 2xx 回應並包含適當的 `hookSpecificOutput` 欄位。HTTP 狀態代碼本身無法阻止操作。 標頭值支援使用 `$VAR_NAME` 或 `${VAR_NAME}` 語法的環境變數插值。只有在 `allowedEnvVars` 陣列中列出的變數才會被解析；所有其他 `$VAR` 參考保持為空。 有關完整的配置選項和回應處理，請參閱參考中的 [HTTP hooks](https://code.claude.com/docs/zh-TW/hooks#http-hook-fields)。

## 限制和故障排除

### 限制

設計 hooks 時請記住這些限制：

- 命令 hooks 只透過 stdout、stderr 和退出代碼通訊。它們無法觸發 `/` 命令或工具呼叫。透過 `additionalContext` 傳回的文字會作為系統提醒注入，Claude 將其讀取為純文字。HTTP hooks 改為透過回應主體通訊。
- Hook 超時因類型而異。透過 `timeout` 欄位（以秒為單位）按 hook 覆寫。
  - `command`、`http`、`mcp_tool`：10 分鐘。Claude Code 將 `UserPromptSubmit`、`PreModelSwitch` 和 `PostModelSwitch` hooks 的預設值降低至 30 秒，將 `MessageDisplay` 的預設值降低至 10 秒。
  - `prompt`：30 秒。
  - `agent`：60 秒。
  - [`SessionEnd`](https://code.claude.com/docs/zh-TW/hooks#sessionend) hooks 的任何類型共享 1.5 秒的預算。如果您的設定為 hook 設定了更長的 `timeout`，Claude Code 會將預算提高以匹配，最多 60 秒。
- `PostToolUse` hooks 無法撤銷操作，因為工具已經執行。
- `PermissionRequest` hooks 在 Claude Code 即將要求您的權限時觸發。
  - 在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p` 旗標時，該提示只在 Agent SDK 的 [`canUseTool` 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/permissions)提供時存在。在純 `-p` 執行或使用 `--permission-prompt-tool` 時，改用 `PreToolUse` hooks 進行自動化權限決策。
  - 背景子代理在非互動模式中無法顯示提示。Claude Code 仍會為其工具呼叫執行 hooks，如果沒有 hook 傳回決策，它會拒絕該呼叫。在互動式工作階段中，背景子代理提示會在您的主要工作階段中顯示，hooks 會照常觸發。
- `Stop` hooks 在 Claude 完成回應時觸發，而不僅在任務完成時。它們在使用者中斷時不觸發。API 錯誤觸發 [StopFailure](https://code.claude.com/docs/zh-TW/hooks#stopfailure) 代替。
- 當多個 `PreToolUse` hooks 傳回 [`updatedInput`](https://code.claude.com/docs/zh-TW/hooks#pretooluse) 以重寫工具的引數時，最後完成的會獲勝。由於 hooks 並行執行，順序是非確定性的。避免有多個 hook 修改同一工具的輸入。

### Hooks 和權限模式

`PreToolUse` hooks 在任何權限模式檢查之前觸發，在每個[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)中，包括 `dontAsk`。傳回 `permissionDecision: "deny"` 的 hook 會阻止工具，即使在 `bypassPermissions` 模式或使用 `--dangerously-skip-permissions`。這讓您強制執行使用者無法透過變更其權限模式來繞過的原則。 反面不成立：傳回 `"allow"` 的 hook 不會繞過來自設定的拒絕規則，它也無法抑制標記為 [`requiresUserInteraction`](https://code.claude.com/docs/zh-TW/mcp#require-approval-for-a-specific-tool) 的 MCP 工具的提示或[您的組織設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 的連接器工具在該設定到達 Claude Code 的工作階段中的提示。Hooks 可以加強限制，但不能放寬超過權限規則允許的限制。

### Hook 未觸發

Hook 已配置但從不執行。

- 執行 `/hooks` 並確認 hook 出現在正確的事件下
- 檢查匹配器模式是否與工具名稱完全相符。匹配器區分大小寫
- 驗證您觸發的是正確的事件類型：`PreToolUse` 在工具執行前觸發，`PostToolUse` 在之後觸發。`PermissionRequest` hook 在 Claude Code 即將要求您的權限時觸發；請參閱[限制](https://code.claude.com/docs/zh-TW/hooks-guide#limitations)以了解非互動模式的情況

### Hook 輸出中的錯誤

您在文字記錄中看到類似「PreToolUse hook error: …」的訊息。

- 您的指令意外以非零代碼退出。透過管道傳輸範例 JSON 來手動測試它：

```
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
echo $?  # 檢查退出代碼

```

- 如果您看到「command not found」，使用絕對路徑或 `${CLAUDE_PROJECT_DIR}` 來參考指令。為了完全避免 shell 引用，添加 `"args": []` 以切換到 [exec 形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)，它直接生成指令而不使用 shell
- 如果您看到「jq: command not found」，安裝 `jq` 或使用 Python/Node.js 進行 JSON 解析
- 如果通知顯示 JSON 驗證訊息，您的 hook 的 stdout 解析為 JSON 但未通過架構驗證。如果顯示 JSON 解析訊息，stdout 看起來像 JSON 物件但不是有效的 JSON。即使在退出 0 時也會發生這兩種情況。 要修復解析失敗，使用 JSON 編碼器（例如 `jq`）而不是字串連接來建立有效負載，以便值內的引號和反斜線被轉義。參考的[退出代碼輸出](https://code.claude.com/docs/zh-TW/hooks#exit-code-output)部分涵蓋了退出代碼和 JSON 組合
- 如果指令根本沒有執行，使其可執行：`chmod +x ./my-hook.sh`

### `/hooks` 顯示未配置任何 hooks

您編輯了設定檔但 hooks 未出現在選單中。

- 檔案編輯通常會自動選取。如果在幾秒鐘後仍未出現，檔案監視程式可能已錯過變更：重新啟動您的工作階段以強制重新載入。
- 驗證您的 JSON 有效：不允許尾隨逗號和註解
- 確認設定檔在正確的位置：`.claude/settings.json` 用於專案 hooks，`~/.claude/settings.json` 用於全域 hooks

### Stop hook 觸發區塊上限

Claude 繼續工作而不是停止，然後以警告結束回合，表示 Stop hook 連續阻止了太多次。 Claude Code 在 Stop hook 連續阻止 8 次而沒有進展後會覆寫它。您的 hook 指令需要檢查它是否已經觸發了延續。從 JSON 輸入解析 `stop_hook_active` 欄位，如果為 `true` 則提前退出：

```
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # 允許 Claude 停止
fi
# ... 您的 hook 邏輯的其餘部分

```

如果您的 hook 合理地需要超過八次迭代才能收斂，使用 [`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`](https://code.claude.com/docs/zh-TW/env-vars) 提高上限。

### Hook JSON 沒有效果

您的 hook 列印有效的 JSON，但決策沒有生效，文字記錄中也沒有出現錯誤。檢查哪個原因適用：

- **JSON 前的額外輸出** ：其他東西首先寫入 stdout，通常是您 shell 設定檔中的無條件 `echo`，所以輸出不再以 `{` 開頭，Claude Code 不會將其解析為 JSON。原因和修復方案如下所示。
- **欄位位置錯誤** ：將每個欄位的位置與 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output)格式進行比較。例如，`permissionDecision` 應該在 `hookSpecificOutput` 內，而不是在頂層。

當 Claude Code 執行 shell 形式的命令 hook（沒有 `args` 的）時，它在 macOS 和 Linux 上生成 `sh -c`，在 Windows 上生成 Git Bash，或在預設未安裝 Git Bash 時生成 PowerShell。此 shell 是非互動式的，但 Git Bash 和某些配置（例如 `BASH_ENV` 指向 `~/.bashrc`）仍然會來源您的設定檔。如果該設定檔包含無條件的 `echo` 陳述式，輸出會被前置到您的 hook 的 JSON：

```
Shell ready on arm64
{"decision": "block", "reason": "Not allowed"}

```

組合的輸出不再以 `{` 開頭，所以 Claude Code 將所有 stdout 視為純文字並忽略 JSON。在退出 0 時，文字記錄中不會報告任何內容；解析嘗試只在[除錯日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)中記錄。要修復此問題，在您的 shell 設定檔中包裝 echo 陳述式，使其只在互動式 shell 中執行：

```
# 在 ~/.zshrc 或 ~/.bashrc 中
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi

```

`$-` 變數包含 shell 旗標，`i` 表示互動式。Hooks 在非互動式 shell 中執行，因此 echo 被跳過。 當您的 hook 在頂層而不是在 `hookSpecificOutput` 內傳回 `permissionDecision` 或 `additionalContext` 時，JSON 仍然會解析，Claude Code 會忽略放置錯誤的欄位而不報告錯誤。要查看它忽略了哪些欄位，使用 `claude --debug` 啟動 Claude Code 並在[除錯日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)中搜尋 `Hook JSON output had unrecognized keys`。

### 除錯技術

按 `Ctrl+O` 開啟文字記錄檢視以檢查 hook 執行的結果：

- **成功執行** ：您看不到任何內容，除非 hook 的 JSON 顯示某些內容，例如 `systemMessage` 或 Stop hook 回饋。
  - 要確認 hook 已執行，檢查其效果，例如重新格式化的檔案，或按照下面所述開啟除錯記錄並再次觸發 hook
- **阻止錯誤** ：在大多數事件上，您會看到 hook 的回饋。當 hook 的 JSON 做出阻止決策時，回饋是該決策的原因；否則它是 hook 的 stderr。在少數事件上，例如 `ConfigChange` 和 `Elicitation`，阻止不會顯示訊息。
- **非阻止錯誤** ：操作繼續進行，您會看到 `<hook name> hook error` 通知，其中包含簡短說明，例如 stderr 的第一行，前置 `Failed with non-blocking status code:`，或 JSON 驗證或解析訊息。

哪些退出代碼和 JSON 組合會產生每個結果，包括每個事件的例外，在參考的[退出代碼輸出](https://code.claude.com/docs/zh-TW/hooks#exit-code-output)部分中定義。 有關完整的執行詳細資訊，包括哪些 hooks 相符、它們的退出代碼、stdout 和 stderr，請閱讀除錯日誌。使用 `claude --debug-file /tmp/claude.log` 啟動 Claude Code 以寫入已知路徑，然後在另一個終端中執行 `tail -f /tmp/claude.log`。如果您啟動時沒有該旗標，在工作階段中執行 `/debug` 以啟用記錄並找到日誌路徑。

## 深入瞭解

- [Hooks 參考](https://code.claude.com/docs/zh-TW/hooks)：完整的事件架構、JSON 輸出格式、非同步 hooks 和 MCP 工具 hooks
- [安全考量](https://code.claude.com/docs/zh-TW/hooks#security-considerations)：在共享或生產環境中部署 hooks 之前進行檢查
- [Bash 命令驗證器範例](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py)：完整的參考實現

是否 助手
