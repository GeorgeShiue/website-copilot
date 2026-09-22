[Skip to main content](https://code.claude.com/docs/zh-TW/hooks#content-area) 如需快速入門指南和範例，請參閱 [使用 hooks 自動化工作流程](https://code.claude.com/docs/zh-TW/hooks-guide)。 Hooks 是使用者定義的 shell 命令、HTTP 端點、MCP 工具呼叫、LLM 提示或子代理，在 Claude Code 生命週期的特定時間點自動執行。Claude Code 在任何地方執行時都會觸發相同的 hook 事件：終端機中的工作階段、IDE 擴充功能、[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop-quickstart) 和 [Claude Code 網頁版](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)。使用此參考來查詢事件架構、配置選項、JSON 輸入/輸出格式，以及非同步 hooks、HTTP hooks 和 MCP 工具 hooks 等進階功能。

## Hook 生命週期

Claude Code 在工作階段期間的特定時間點執行 hooks。當事件觸發且匹配器符合時，Claude Code 會將有關該事件的 JSON 上下文傳遞給您的 hook 處理程式。對於命令 hooks，輸入會到達 stdin。對於 HTTP hooks，它會作為 POST 請求正文到達。您的處理程式可以檢查輸入、採取行動，並可選擇性地返回決定。 事件分為三種節奏：

- 每個工作階段一次：`SessionStart` 和 `SessionEnd`
- 每個轉向一次：`UserPromptSubmit`、`Stop` 和 `StopFailure`
- 在代理迴圈內每個工具呼叫上：`PreToolUse` 和 `PostToolUse`，除了 [`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior) 呼叫外，兩者都會跳過

![Hook 生命週期圖表，顯示可選的 Setup 進入 SessionStart，然後是每個轉向的迴圈，包含 UserPromptSubmit、用於 slash commands 的 UserPromptExpansion、嵌套的代理迴圈（PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、PostToolBatch、SubagentStart/Stop、TaskCreated、TaskCompleted）和 Stop 或 StopFailure，接著是 TeammateIdle、PreCompact、PostCompact 和 SessionEnd，Elicitation 和 ElicitationResult 嵌套在 MCP 工具執行內，PermissionDenied 作為 PermissionRequest 的側分支用於自動模式拒絕，WorktreeCreate、WorktreeRemove、Notification、ConfigChange、InstructionsLoaded、CwdChanged、FileChanged 和 DirectoryAdded 作為獨立非同步事件，PreModelSwitch 作為獨立順序事件，在請求的模型切換之前執行，PostModelSwitch 作為獨立非同步事件，在工作階段的模型變更後執行，以及 MessageDisplay 作為顯示專用事件，在助手訊息文字串流時執行](https://mintcdn.com/claude-code/x7pO8l4XcvAXCoVc/images/hooks-lifecycle.svg?fit=max&auto=format&n=x7pO8l4XcvAXCoVc&q=85&s=81b9256c1bbe8832553485f5d9e9c746)

![Hook 生命週期圖表，顯示可選的 Setup 進入 SessionStart，然後是每個轉向的迴圈，包含 UserPromptSubmit、用於 slash commands 的 UserPromptExpansion、嵌套的代理迴圈（PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、PostToolBatch、SubagentStart/Stop、TaskCreated、TaskCompleted）和 Stop 或 StopFailure，接著是 TeammateIdle、PreCompact、PostCompact 和 SessionEnd，Elicitation 和 ElicitationResult 嵌套在 MCP 工具執行內，PermissionDenied 作為 PermissionRequest 的側分支用於自動模式拒絕，WorktreeCreate、WorktreeRemove、Notification、ConfigChange、InstructionsLoaded、CwdChanged、FileChanged 和 DirectoryAdded 作為獨立非同步事件，PreModelSwitch 作為獨立順序事件，在請求的模型切換之前執行，PostModelSwitch 作為獨立非同步事件，在工作階段的模型變更後執行，以及 MessageDisplay 作為顯示專用事件，在助手訊息文字串流時執行](https://mintcdn.com/claude-code/x7pO8l4XcvAXCoVc/images/hooks-lifecycle-dark.svg?fit=max&auto=format&n=x7pO8l4XcvAXCoVc&q=85&s=c9b3d88487335f58cce0b52e2f9e7531)
下表總結了每個事件何時觸發。[Hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events)部分記錄了每個事件的完整輸入架構和決定控制選項。

| 事件                  | 何時觸發                                                                                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SessionStart`        | 當工作階段開始或繼續時                                                                                                                                                          |
| `Setup`               | 當您使用 `--init-only` 啟動 Claude Code，或在 `-p` 模式中使用 `--init` 或 `--maintenance` 時。用於 CI 或指令碼中的一次性準備                                                    |
| `UserPromptSubmit`    | 當您提交提示詞時，在 Claude 處理之前                                                                                                                                            |
| `UserPromptExpansion` | 當使用者輸入的命令擴展為提示詞時，在到達 Claude 之前。可以阻止擴展                                                                                                              |
| `PreToolUse`          | 在工具呼叫執行之前。可以阻止它                                                                                                                                                  |
| `PermissionRequest`   | 當工具呼叫需要權限決定時                                                                                                                                                        |
| `PermissionDenied`    | 當自動模式拒絕工具呼叫時，包括沒有分類器判決的拒絕。使用 JSON `hookSpecificOutput.retry: true` 告訴模型它可能重試被拒絕的工具呼叫。Claude Code 在分類器未產生判決時忽略 `retry` |
| `PostToolUse`         | 在工具呼叫成功後                                                                                                                                                                |
| `PostToolUseFailure`  | 在工具呼叫失敗後                                                                                                                                                                |
| `PostToolBatch`       | 在完整的平行工具呼叫批次解決後，在下一個模型呼叫之前                                                                                                                            |
| `Notification`        | 當 Claude Code 傳送通知時                                                                                                                                                       |
| `MessageDisplay`      | 在助手訊息文字顯示時                                                                                                                                                            |
| `SubagentStart`       | 當子代理被生成時                                                                                                                                                                |
| `SubagentStop`        | 當子代理完成時                                                                                                                                                                  |
| `TaskCreated`         | 當透過 `TaskCreate` 建立任務時                                                                                                                                                  |
| `TaskCompleted`       | 當任務被標記為已完成時                                                                                                                                                          |
| `Stop`                | 當 Claude 完成回應時                                                                                                                                                            |
| `StopFailure`         | 當回合因 API 錯誤而結束時                                                                                                                                                       |
| `TeammateIdle`        | 當[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友即將閒置時                                                                                                      |
| `InstructionsLoaded`  | 當 CLAUDE.md 或 `.claude/rules/*.md` 檔案被載入到上下文時。在工作階段開始時以及在工作階段期間延遲載入檔案時觸發                                                                 |
| `ConfigChange`        | 當設定檔在工作階段期間變更時                                                                                                                                                    |
| `CwdChanged`          | 當工作目錄變更時，例如當 Claude 執行 `cd` 命令時。適用於使用 direnv 等工具進行反應式環境管理                                                                                    |
| `DirectoryAdded`      | 當工作目錄在工作階段中期透過 `/add-dir` 或 SDK `register_repo_root` 控制請求新增時                                                                                              |
| `FileChanged`         | 當監視的檔案在磁碟上變更時。`matcher` 欄位指定要監視的檔案名稱                                                                                                                  |
| `WorktreeCreate`      | 當透過 `--worktree`、`isolation: "worktree"` 建立 worktree 時，或用於背景工作階段時。取代預設的 git 行為                                                                        |
| `WorktreeRemove`      | 當在工作階段結束時、子代理完成時或您刪除背景工作階段時移除 worktree 時                                                                                                          |
| `PreCompact`          | 在上下文壓縮之前                                                                                                                                                                |
| `PostCompact`         | 在上下文壓縮完成後                                                                                                                                                              |
| `PreModelSwitch`      | 在 Claude Code 應用您或用戶端要求的模型切換之前。可以阻止切換                                                                                                                   |
| `PostModelSwitch`     | 在工作階段的模型變更後，包括 Claude Code 自行進行的變更，例如當您繼續工作階段時恢復模型                                                                                         |
| `Elicitation`         | 當 MCP 伺服器在工具呼叫期間要求使用者輸入時                                                                                                                                     |
| `ElicitationResult`   | 在使用者回應 MCP 引出後，在回應傳送回伺服器之前                                                                                                                                 |
| `SessionEnd`          | 當工作階段終止時                                                                                                                                                                |

### Hook 如何解析

為了了解事件、匹配器和處理程式如何組合在一起，請考慮此 `PreToolUse` hook，它會阻止破壞性 shell 命令。

- macOS/Linux
- Windows (PowerShell)

`matcher` 縮小到 Bash 工具呼叫，`if` 條件進一步縮小到符合 `rm *` 的 Bash 子命令，因此 `block-rm.sh` 僅在兩個篩選器都符合時才生成：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}

```

該指令碼從 stdin 讀取 JSON 輸入，提取命令，如果包含 `rm -rf`，則返回 `permissionDecision` 為 `"deny"`。將其儲存到您的專案中的 `.claude/hooks/block-rm.sh`，並使用 `chmod +x .claude/hooks/block-rm.sh` 使其可執行，以便 Claude Code 可以執行它：

```
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0  # no decision; normal permission flow applies
fi

```

此指令碼，如同本頁面上解析 JSON 輸入的其他 Bash 範例，使用 `jq`，因此在嘗試之前請安裝 `jq` 並確保它在您的 `PATH` 上。 匹配器 `Bash|PowerShell` 涵蓋 [PowerShell 工具](https://code.claude.com/docs/zh-TW/hooks#powershell)以及 Bash。單一 `if` 規則只符合一個工具的呼叫，因此每個工具都有自己的處理程式：第一個縮小到符合 `rm *` 的 Bash 子命令，第二個縮小到符合 `Remove-Item *` 的 PowerShell 命令。兩者都透過 `powershell.exe` 執行相同的指令碼：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.ps1"
            ]
          },
          {
            "type": "command",
            "if": "PowerShell(Remove-Item *)",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.ps1"
            ]
          }
        ]
      }
    ]
  }
}

```

`-NoProfile` 旗標會跳過載入您的 PowerShell 設定檔，以便 hook 快速啟動，而 `-ExecutionPolicy Bypass` 讓 PowerShell 執行本機指令碼檔案。該指令碼從 stdin 讀取 JSON 輸入，提取命令，如果包含 `rm -rf` 或 `Remove-Item` 後跟 `-Recurse`，則返回 `permissionDecision` 為 `"deny"`。將其儲存到您的專案中的 `.claude/hooks/block-rm.ps1`：

```
# .claude/hooks/block-rm.ps1
$callInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
$command = $callInput.tool_input.command

if ($command -match 'rm -rf|Remove-Item.*-Recurse') {
  @{
    hookSpecificOutput = @{
      hookEventName = "PreToolUse"
      permissionDecision = "deny"
      permissionDecisionReason = "Destructive command blocked by hook"
    }
  } | ConvertTo-Json
} else {
  exit 0  # no decision; normal permission flow applies
}

```

現在假設 Claude Code 決定針對 macOS/Linux 設定執行 `Bash "rm -rf /tmp/build"`。以下是發生的情況：

![Hook 解析圖表：PreToolUse 觸發，匹配器檢查 Bash 符合，然後 if 條件檢查 Bashrm * 符合。如果兩者都符合，hook 命令執行並返回 permissionDecision deny，因此工具呼叫被阻止，Claude Code 繼續。如果任一檢查未能符合，hook 被跳過，工具呼叫允許繼續進行。](https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/hook-resolution.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=be0bf3053550c26de5f54cd64674c197)

![Hook 解析圖表：PreToolUse 觸發，匹配器檢查 Bash 符合，然後 if 條件檢查 Bashrm * 符合。如果兩者都符合，hook 命令執行並返回 permissionDecision deny，因此工具呼叫被阻止，Claude Code 繼續。如果任一檢查未能符合，hook 被跳過，工具呼叫允許繼續進行。](https://mintcdn.com/claude-code/_xqph1dUOslCOwsj/images/hook-resolution-dark.svg?fit=max&auto=format&n=_xqph1dUOslCOwsj&q=85&s=e80af91f8507cee6bd51ac3c2dd92f63)
1 事件觸發 `PreToolUse` 事件觸發。Claude Code 將工具輸入作為 JSON 在 stdin 上發送到 hook：

```
{ "tool_name": "Bash", "tool_input": { "command": "rm -rf /tmp/build" }, ... }

```

2 匹配器檢查 匹配器 `"Bash"` 符合工具名稱，因此此 hook 群組啟動。如果您省略匹配器或使用 `"*"`，群組在事件的每次出現時啟動。 3 If 條件檢查 `if` 條件 `"Bash(rm *)"` 符合，因為 `rm -rf /tmp/build` 是符合 `rm *` 的子命令，因此此處理程式生成。如果命令是 `npm test`，`if` 檢查會失敗，`block-rm.sh` 永遠不會執行，避免程序生成開銷。`if` 欄位是可選的；沒有它，符合群組中的每個處理程式都執行。 4 Hook 處理程式執行 該指令碼檢查完整命令並找到 `rm -rf`，因此它將決定列印到 stdout：

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by hook"
  }
}

```

如果命令是更安全的 `rm` 變體，如 `rm file.txt`，指令碼會改為執行 `exit 0`。Exit code 0 且沒有輸出表示 hook 沒有決定要報告，因此工具呼叫會繼續通過正常的[權限流程](https://code.claude.com/docs/zh-TW/permissions)。Hook 可以拒絕呼叫，但保持沉默不會批准它。 5 Claude Code 根據結果採取行動 Claude Code 讀取 JSON 決定，阻止工具呼叫，並向 Claude 顯示原因。 下面的[設定](https://code.claude.com/docs/zh-TW/hooks#configuration)部分記錄了完整架構，每個 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events)部分記錄了您的命令接收的輸入以及它可以返回的輸出。

## 配置

Hooks 在 JSON 設定檔中定義。配置有三個嵌套層級：

1. 選擇要回應的 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events)，例如 `PreToolUse` 或 `Stop`
1. 新增 [匹配器群組](https://code.claude.com/docs/zh-TW/hooks#matcher-patterns) 以篩選何時觸發，例如「僅針對 Bash 工具」
1. 定義一個或多個 [hook 處理程式](https://code.claude.com/docs/zh-TW/hooks#hook-handler-fields) 以在匹配時執行

有關完整的逐步說明和註解範例，請參閱上面的 [Hook 如何解析](https://code.claude.com/docs/zh-TW/hooks#how-a-hook-resolves)。 此頁面為每個層級使用特定術語：**hook 事件** 表示生命週期點，**匹配器群組** 表示篩選器，**hook 處理程式** 表示執行的 shell 命令、HTTP 端點、MCP 工具、提示或代理。‘Hook’ 本身指的是一般功能。

### Hook 位置

您定義 hook 的位置決定了其範圍：

| 位置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 範圍                                                                                                                                   | 可共享                                              |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `~/.claude/settings.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 您的所有專案                                                                                                                           | 否，本機限定                                        |
| `.claude/settings.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 單一專案                                                                                                                               | 是，可提交到儲存庫                                  |
| `.claude/settings.local.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 單一專案                                                                                                                               | 否，gitignored（當 Claude Code 將設定儲存到其中時） |
| 受管理的原則設定                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 組織範圍                                                                                                                               | 是，由管理員控制                                    |
| [Plugin](https://code.claude.com/docs/zh-TW/plugins) `hooks/hooks.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 啟用外掛程式時                                                                                                                         | 是，與外掛程式一起打包                              |
| [Skill](https://code.claude.com/docs/zh-TW/skills) frontmatter                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 叫用 skill 後的工作階段其餘部分。請參閱 [Skills 和代理中的 Hooks](https://code.claude.com/docs/zh-TW/hooks#hooks-in-skills-and-agents) | 是，在 skill 檔案中定義                             |
| [Subagent](https://code.claude.com/docs/zh-TW/sub-agents) frontmatter                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 該 subagent 執行時                                                                                                                     | 是，在 subagent 檔案中定義                          |
| [Claude Code on the web](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 上的雲端工作階段不會讀取您的本機 `~/.claude/settings.json`；那裡的 hooks 來自儲存庫和您組織的伺服器管理設定。在 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#permissions-and-tool-approval) 中，Claude Code 也執行操作員從執行器主機的 `~/.claude/` 中植入的 hooks，並在該檔案位於 [Claude Code 應用的受管理來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources) 中時執行執行器映像的受管理設定檔中的 hooks，預設情況下僅當伺服器管理設定或 MDM 傳遞的 Claude Code 原則都不提供受管理層級時。請參閱 [您的設定中哪些內容會轉移到雲端工作階段](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup) 以了解哪些檔案到達雲端工作階段。 有關設定檔解析的詳細資訊，請參閱 [settings](https://code.claude.com/docs/zh-TW/settings)。 來自設定檔、受管理的原則設定和外掛程式的 Hooks 也在 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 內執行。當 subagent 呼叫工具時，工具事件（例如 `PreToolUse` 和 `PostToolUse`）會觸發與主要對話中相同的已配置 hooks，輸入會攜帶 `agent_id` 和 `agent_type` [通用輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 以識別 subagent。 企業管理員可以使用 `allowManagedHooksOnly` 來限制哪些 hooks 執行： |                                                                                                                                        |                                                     |

- 您的使用者、專案、本機和外掛程式 hooks 被阻止。在受管理設定 `enabledPlugins` 中強制啟用的外掛程式的 Hooks 是例外
- Claude Code 也將您的 [`statusLine`](https://code.claude.com/docs/zh-TW/statusline)、[`fileSuggestion`](https://code.claude.com/docs/zh-TW/settings-reference#filesuggestion) 和 [`subagentStatusLine`](https://code.claude.com/docs/zh-TW/statusline#subagent-status-lines) 設定縮小到受管理設定
- Claude Code 也停用具有 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources) 的外掛程式，包括在受管理設定 `enabledPlugins` 中強制啟用的外掛程式，除非 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources) 明確設定為 `false`。`command` 來源需要 Claude Code v2.1.229 或更新版本
- Claude Code 也阻止市場 [`headersHelper` 命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#authenticate-archive-downloads)，除非 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources) 明確設定為 `false`，除了受管理設定本身宣告的市場

請參閱 [在 `allowManagedHooksOnly` 下執行的內容](https://code.claude.com/docs/zh-TW/settings-reference#what-runs-under-allowmanagedhooksonly)。 Hook 項目在設定層級之間合併而不是相互替換：使用者、專案和本機設定新增自己的 hooks 而不移除受管理的 hooks，[`disableAllHooks`](https://code.claude.com/docs/zh-TW/hooks#disable-or-remove-hooks) 設定無法停用來自受管理設定外部的受管理 hooks。 [HTTP hook 允許清單](https://code.claude.com/docs/zh-TW/settings-reference#hook-and-skill-settings) 適用於來自每個來源的 hooks，包括受管理的原則設定：

- `allowedHttpHookUrls`：在任何設定層級定義時，Claude Code 僅在其 URL 與合併的允許清單相符時執行 HTTP hook 處理程式
- `httpHookAllowedEnvVars`：定義時，Claude Code 僅將該清單上的環境變數插值到 hook 標頭中

### 匹配器模式

`matcher` 欄位篩選 hooks 何時觸發。匹配器的評估方式取決於它包含的字元：

| 匹配器值                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 評估為                                                                                                              | 範例                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `"*"`、`""` 或省略                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 匹配所有                                                                                                            | 在事件的每次出現時觸發                                                                                                                                                                                                                                                         |
| 僅字母、數字、`_`、`-`、空格、`,` 和 \`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | \`                                                                                                                  | 精確字串或由 \`                                                                                                                                                                                                                                                                |
| 包含任何其他字元                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | JavaScript 正規表達式，未錨定                                                                                       | `^Notebook` 匹配任何以 Notebook 開頭的工具；`mcp__memory__.*` 匹配來自 `memory` 伺服器的每個工具                                                                                                                                                                               |
| 在正規表達式路徑上的匹配器使用 JavaScript 的 `RegExp.prototype.test` 進行測試，該測試在值中任何位置的匹配時成功。`Edit.*` 匹配 `Edit` 和 `NotebookEdit`；當您需要整個字串匹配時，用 `^` 和 `$` 包裝模式，如 `^Edit$`。 逗號分隔符和周圍空格容差需要 Claude Code v2.1.191 或更新版本。 精確匹配集中的連字號需要 Claude Code v2.1.195 或更新版本。在較早的版本上，像 `code-reviewer` 這樣的連字號名稱被評估為未錨定的正規表達式，因此它也會針對 `senior-code-reviewer` 觸發；在這些版本上將其錨定為 `^code-reviewer$` 以僅匹配該名稱。 `FileChanged` 和 `StopFailure` 使用更窄的精確匹配集，僅包含字母、數字、`_` 和 \`                                                                                                                           | `。匹配器中的連字號、空格或逗號會將其保留在正規表達式路徑上，只有 `                                                 | `分隔替代項。表格中列出的支援匹配器的所有其他事件接受`                                                                                                                                                                                                                         |
| 事件                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 匹配器篩選的內容                                                                                                    | 範例匹配器值                                                                                                                                                                                                                                                                   |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | ---                                                                                                                 | ---                                                                                                                                                                                                                                                                            |
| `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 工具名稱                                                                                                            | `Bash`、\`Edit                                                                                                                                                                                                                                                                 |
| `SessionStart`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 工作階段如何開始                                                                                                    | `startup`、`resume`、`clear`、`compact`、`fork`                                                                                                                                                                                                                                |
| `Setup`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 哪個 CLI 旗標觸發設定                                                                                               | `init`、`maintenance`                                                                                                                                                                                                                                                          |
| `SessionEnd`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 工作階段為何結束                                                                                                    | `clear`、`resume`、`logout`、`prompt_input_exit`、`other`                                                                                                                                                                                                                      |
| `Notification`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 通知類型                                                                                                            | `permission_prompt`、`idle_prompt`、`auth_success`、`elicitation_dialog`、`elicitation_url_dialog`、`elicitation_complete`、`elicitation_response`、`agent_needs_input`、`agent_completed`、`quota_auto_resume_fired`、`quota_auto_resume_stale`、`quota_auto_resume_disabled` |
| `SubagentStart`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 代理類型                                                                                                            | `general-purpose`、`Explore`、`Plan`、自訂代理名稱或外掛程式範圍名稱，如 `^my-plugin:reviewer$`                                                                                                                                                                                |
| `PreCompact`、`PostCompact`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 觸發壓縮的原因                                                                                                      | `manual`、`auto`                                                                                                                                                                                                                                                               |
| `PreModelSwitch`、`PostModelSwitch`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 工作階段切換到的模型的規範名稱，如 [PreModelSwitch](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 下所述 | `claude-opus-5`、\`claude-opus-4-6                                                                                                                                                                                                                                             |
| `SubagentStop`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 代理類型                                                                                                            | 與 `SubagentStart` 相同的值                                                                                                                                                                                                                                                    |
| `ConfigChange`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 配置來源                                                                                                            | `user_settings`、`project_settings`、`local_settings`、`policy_settings`、`skills`                                                                                                                                                                                             |
| `CwdChanged`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 不支援匹配器                                                                                                        | 總是在每次出現時觸發                                                                                                                                                                                                                                                           |
| `DirectoryAdded`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 目錄如何被新增                                                                                                      | `slash_command`、`register_repo_root`                                                                                                                                                                                                                                          |
| `FileChanged`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 要監視的字面檔案名稱（請參閱 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged)）                  | \`.envrc                                                                                                                                                                                                                                                                       |
| `StopFailure`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 錯誤類型                                                                                                            | `rate_limit`、`overloaded`、`authentication_failed`、`oauth_org_not_allowed`、`account_on_hold`、`billing_error`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens`、`cloud_credential_error`、`unknown`                                               |
| `InstructionsLoaded`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 載入原因                                                                                                            | `session_start`、`nested_traversal`、`path_glob_match`、`include`、`compact`                                                                                                                                                                                                   |
| `UserPromptExpansion`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 命令名稱                                                                                                            | 您的 skill 或命令名稱                                                                                                                                                                                                                                                          |
| `Elicitation`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | MCP 伺服器名稱                                                                                                      | 您配置的 MCP 伺服器名稱                                                                                                                                                                                                                                                        |
| `ElicitationResult`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | MCP 伺服器名稱                                                                                                      | 與 `Elicitation` 相同的值                                                                                                                                                                                                                                                      |
| `UserPromptSubmit`、`PostToolBatch`、`Stop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`WorktreeCreate`、`WorktreeRemove`、`MessageDisplay`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 不支援匹配器                                                                                                        | 總是在每次出現時觸發                                                                                                                                                                                                                                                           |
| 在 `cloud_credential_error` 上匹配 `StopFailure` 需要 Claude Code v2.1.267 或更新版本，這是第一個在該值下報告認證載入失敗而不是 `server_error` 或 `unknown` 的版本。 對於大多數事件，Claude Code 針對它在 stdin 上發送給您的 hook 的 [JSON 輸入](https://code.claude.com/docs/zh-TW/hooks#hook-input-and-output) 中的欄位評估匹配器。對於工具事件，該欄位是 `tool_name`。對於 `PreModelSwitch` 和 `PostModelSwitch`，Claude Code 針對它從 `to_model` 衍生的規範名稱評估匹配器，如 [PreModelSwitch](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 下所述。每個 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events) 部分列出了該事件的完整匹配器值集和輸入架構。 此範例僅在 Claude 寫入或編輯檔案時執行 linting 指令碼： |                                                                                                                     |                                                                                                                                                                                                                                                                                |

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/lint-check.sh"
          }
        ]
      }
    ]
  }
}

```

如果您將 `matcher` 欄位新增到不支援匹配器的事件，它會被無聲地忽略。 對於工具事件，您可以通過在個別 hook 處理程式上設定 [`if` 欄位](https://code.claude.com/docs/zh-TW/hooks#common-fields) 來更狹隘地篩選。`if` 使用 [權限規則語法](https://code.claude.com/docs/zh-TW/permissions) 來匹配工具名稱和參數，因此 `"Bash(git *)"` 僅在任何 Bash 輸入的子命令匹配 `git *` 時執行，`"Edit(*.ts)"` 僅針對 TypeScript 檔案執行。

#### 匹配 MCP 工具

[MCP](https://code.claude.com/docs/zh-TW/mcp) 伺服器工具在工具事件中顯示為常規工具（`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`），因此您可以像匹配任何其他工具名稱一樣匹配它們。 MCP 工具遵循命名模式 `mcp__<server>__<tool>`，例如：

- `mcp__memory__create_entities`：Memory 伺服器的建立實體工具
- `mcp__filesystem__read_file`：Filesystem 伺服器的讀取檔案工具
- `mcp__github__search_repositories`：GitHub 伺服器的搜尋工具

要匹配來自伺服器的每個工具，請在伺服器前綴後附加 `.*`。`.*` 是必需的：像 `mcp__memory` 或 `mcp__brave-search` 這樣的匹配器僅包含精確匹配字元，因此它被比較為精確字串，不匹配任何工具。

- `mcp__memory__.*` 匹配來自 `memory` 伺服器的所有工具
- `mcp__brave-search__.*` 匹配來自名稱包含連字號的伺服器的所有工具
- `mcp__.*__write.*` 匹配來自任何伺服器的任何名稱以 `write` 開頭的工具

精確匹配集中的連字號需要 Claude Code v2.1.195 或更新版本。在較早的版本上，像 `mcp__brave-search` 這樣的裸連字號前綴被評估為未錨定的正規表達式，並匹配來自該伺服器的每個工具。`mcp__brave-search__.*` 形式在每個版本上都有效。 來自 [plugin-bundled MCP server](https://code.claude.com/docs/zh-TW/mcp#plugin-provided-mcp-servers) 的工具使用包含外掛程式名稱的範圍伺服器段：`mcp__plugin_<plugin-name>_<server-name>__<tool>`。針對裸伺服器金鑰編寫的匹配器永遠不會針對這些工具觸發。對於名為 `my-plugin` 的外掛程式，在金鑰 `db` 下打包伺服器，`query` 工具顯示為 `mcp__plugin_my-plugin_db__query`，因此來自該伺服器的每個工具的匹配器是 `mcp__plugin_my-plugin_db__.*`。在處理程式的 [`if` 欄位](https://code.claude.com/docs/zh-TW/hooks#common-fields) 中使用相同的範圍工具名稱。請參閱 [Plugin-provided MCP servers](https://code.claude.com/docs/zh-TW/mcp#plugin-provided-mcp-servers) 以了解如何建立範圍名稱。 此範例記錄所有 memory 伺服器操作並驗證來自任何 MCP 伺服器的寫入操作：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__memory__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Memory operation initiated' >> ~/mcp-operations.log"
          }
        ]
      },
      {
        "matcher": "mcp__.*__write.*",
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/scripts/validate-mcp-write.py"
          }
        ]
      }
    ]
  }
}

```

### Hook 處理程式欄位

內部 `hooks` 陣列中的每個物件都是一個 hook 處理程式：當匹配器匹配時執行的 shell 命令、HTTP 端點、MCP 工具、LLM 提示或代理。有五種類型：

- **[命令 hooks](https://code.claude.com/docs/zh-TW/hooks#command-hook-fields)** （`type: "command"`）：執行 shell 命令。您的指令碼在 stdin 上接收事件的 [JSON 輸入](https://code.claude.com/docs/zh-TW/hooks#hook-input-and-output)，並通過退出代碼和 stdout 傳回結果。
- **[HTTP hooks](https://code.claude.com/docs/zh-TW/hooks#http-hook-fields)** （`type: "http"`）：將事件的 JSON 輸入作為 HTTP POST 請求發送到 URL。端點通過使用與命令 hooks 相同的 [JSON 輸出格式](https://code.claude.com/docs/zh-TW/hooks#json-output) 的回應正文傳回結果。
- **[MCP 工具 hooks](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields)** （`type: "mcp_tool"`）：在已連接的 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp) 上呼叫工具。工具的文字輸出被視為類似命令 hook stdout。
- **[提示 hooks](https://code.claude.com/docs/zh-TW/hooks#prompt-and-agent-hook-fields)** （`type: "prompt"`）：將提示發送到 Claude 模型進行單輪評估。模型以 JSON 形式返回決定。請參閱 [基於提示的 hooks](https://code.claude.com/docs/zh-TW/hooks#prompt-based-hooks)。
- **[代理 hooks](https://code.claude.com/docs/zh-TW/hooks#prompt-and-agent-hook-fields)** （`type: "agent"`）：生成一個可以使用 Read、Grep 和 Glob 等工具來驗證條件的 subagent，然後返回決定。代理 hooks 是實驗性的，可能會變更。請參閱 [基於代理的 hooks](https://code.claude.com/docs/zh-TW/hooks#agent-based-hooks)。

所有匹配的 hooks 並行執行。如果您在多個設定檔中定義相同的處理程式，它執行一次。外掛程式或 skill 的相同處理程式副本保持分開。 處理程式在目前目錄中執行，使用 Claude Code 的環境。如果目前目錄不再存在，例如另一個 shell 在工作階段中途刪除的 worktree 或臨時目錄，Claude Code 從以下第一個仍然存在的目錄執行命令 hooks：工作階段開始的目錄、專案根目錄、您的主目錄或系統臨時目錄。Claude Code 在 [debug log](https://code.claude.com/docs/zh-TW/hooks#debug-hooks) 中記錄一個警告，命名回退目錄。 `$CLAUDE_CODE_REMOTE` 環境變數在遠端網路環境中為 `"true"`，在本機 CLI 中未設定。Claude Code v2.1.199 及更新版本在本機工作階段具有活動的 Remote Control 連接時將 [`$CLAUDE_CODE_BRIDGE_SESSION_ID`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段 ID。

#### 通用欄位

這些欄位適用於所有 hook 類型：

| 欄位                                                                                                                                                                                                               | 必需                        | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                                                                                                                                                                                                             | 是                          | `"command"`、`"http"`、`"mcp_tool"`、`"prompt"` 或 `"agent"`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `if`                                                                                                                                                                                                               | 否                          | 權限規則語法以篩選此 hook 何時執行，例如 `"Bash(git *)"` 或 `"Edit(*.ts)"`。Hook 命令僅在工具呼叫匹配模式時執行。請參閱下面的 [Bash 匹配表](https://code.claude.com/docs/zh-TW/hooks#bash-if-matching) 以了解 Bash 模式如何針對子命令、`$()` 和反引號進行評估。僅在工具事件上評估：`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest` 和 `PermissionDenied`。在其他事件上，設定 `if` 的 hook 永遠不會執行。使用與 [權限規則](https://code.claude.com/docs/zh-TW/permissions) 相同的語法                                                                                                                                                                                                                                                                                                                                 |
| `timeout`                                                                                                                                                                                                          | 否                          | 取消前的秒數。Claude Code 不會在您使用 [`async: true`](https://code.claude.com/docs/zh-TW/hooks#run-hooks-in-the-background) 執行的命令 hook 上強制執行。預設值：`command`、`http` 和 `mcp_tool` 為 600；`prompt` 為 30；`agent` 為 60。Claude Code 在 [`UserPromptSubmit`](https://code.claude.com/docs/zh-TW/hooks#userpromptsubmit)、[`PreModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 和 [`PostModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#postmodelswitch) 上將 `command`、`http` 和 `mcp_tool` 的預設值降低到 30，在 [`MessageDisplay`](https://code.claude.com/docs/zh-TW/hooks#messagedisplay) 上降低到 10。[`SessionEnd`](https://code.claude.com/docs/zh-TW/hooks#sessionend) hooks 共享 1.5 秒的預算；如果您的設定設定了更長的每個 hook `timeout`，Claude Code 會提高預算以匹配，最多 60 秒 |
| `statusMessage`                                                                                                                                                                                                    | 否                          | hook 執行時顯示的自訂微調訊息                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `once`                                                                                                                                                                                                             | 否                          | 如果為 `true`，Claude Code 在第一次成功執行後移除 hook。執行失敗、以退出代碼 2 阻止或逾時的執行會將 hook 保留在原位，因此它在下一個匹配事件上再次執行。僅在 [skill frontmatter](https://code.claude.com/docs/zh-TW/hooks#hooks-in-skills-and-agents) 中受尊重；在設定檔和代理 frontmatter 中被忽略                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `if` 欄位恰好包含一個權限規則。沒有 `&&`、\`                                                                                                                                                                       |                             | `或清單語法來組合規則；要應用多個條件，請為每個條件定義一個單獨的 hook 處理程式。 在檔案工具的`if`條件中，單一段目錄模式如`"Edit(src/**)"`僅匹配工作目錄中的`src`目錄及其下的檔案。要匹配任何深度的名為`src`的目錄，請寫`"Edit(**/src/**)"`。在 v2.1.214 之前，`"Edit(src/**)"`匹配工作目錄下任何深度的名為`src`的目錄。 對於 Bash 模式，您的 hook 命令是否執行取決於模式的形狀和 Claude 正在呼叫的 Bash 命令。前導`VAR=value\` 指派在匹配前被移除。                                                                                                                                                                                                                                                                                                                                                                                        |
| `if` 模式                                                                                                                                                                                                          | Bash 命令                   | Hook 執行？                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ---                                                                                                                                                                                                                | ---                         | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `Bash(git *)`                                                                                                                                                                                                      | `FOO=bar git push`          | 是                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Bash(git *)`                                                                                                                                                                                                      | `npm test && git push`      | 是                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Bash(rm *)`                                                                                                                                                                                                       | `echo $(rm -rf /)`          | 是                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Bash(rm *)`                                                                                                                                                                                                       | `echo $(date)`              | 否                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Bash(cat *)`                                                                                                                                                                                                      | `echo before $(date) after` | 否                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Bash(git *)`                                                                                                                                                                                                      | `$TOOL git push`            | 是                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Bash(git push *)`                                                                                                                                                                                                 | `echo $(date)`              | 是                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 當 Claude Code 無法確定 Bash 輸入執行哪些命令時，它無論如何都會執行您的 hook。因為 `if` 篩選器是盡力而為的，請使用 [權限系統](https://code.claude.com/docs/zh-TW/permissions) 而不是 hook 來強制執行硬允許或拒絕。 |                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

#### 命令 hook 欄位

除了 [通用欄位](https://code.claude.com/docs/zh-TW/hooks#common-fields) 外，命令 hooks 還接受這些欄位：

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 必需 | 描述                                                                                                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 是   | 要執行的 shell 命令。使用 `args` 時，要直接生成的可執行檔。請參閱 [Exec 形式和 shell 形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)                                                                                                                               |
| `args`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 否   | 參數清單。存在時，`command` 被解析為可執行檔並直接使用 `args` 作為參數向量生成，不涉及 shell。請參閱 [Exec 形式和 shell 形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)                                                                                            |
| `async`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 否   | 如果為 `true`，在背景執行而不阻止。請參閱 [在背景執行 hooks](https://code.claude.com/docs/zh-TW/hooks#run-hooks-in-the-background)                                                                                                                                                          |
| `asyncRewake`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 否   | 如果為 `true`，在背景執行並在退出代碼 2 時喚醒 Claude。Hook 的 stderr，或如果 stderr 為空則為 stdout，作為系統提醒顯示給 Claude，以便它可以對長時間執行的背景失敗做出反應                                                                                                                   |
| `shell`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 否   | 用於此 hook 的 shell。接受 `"bash"` 或 `"powershell"`。預設為 `"bash"`，或在未安裝 Git Bash 時在 Windows 上預設為 `"powershell"`。設定 `"powershell"` 在 Windows 上通過 PowerShell 執行命令。不需要 `CLAUDE_CODE_USE_POWERSHELL_TOOL`，因為 hooks 直接生成 PowerShell。設定 `args` 時被忽略 |
| 當設定 `args` 時，命令 hook 以 exec 形式執行，當省略 `args` 時以 shell 形式執行。每當 hook 參考 [路徑佔位符](https://code.claude.com/docs/zh-TW/hooks#reference-scripts-by-path) 時設定 `args`，因為每個元素作為一個參數傳遞，不進行引用。當您需要 shell 功能（如管道或 `&&`）時，或當兩個問題都不適用時，省略 `args`。 **Exec 形式** 在設定 `args` 時執行。Claude Code 在 `PATH` 上解析 `command` 作為可執行檔並直接使用 `args` 作為參數向量生成它。沒有 shell，因此每個 `args` 元素恰好是一個參數，完全按照編寫的方式，路徑佔位符如 `${CLAUDE_PLUGIN_ROOT}` 被替換為 `command` 和每個 `args` 元素中的純字串。特殊字元如撇號、`$` 和反引號逐字傳遞，因為沒有 shell 來解釋它們。任何平台上都不會發生 shell 標記化。 **Shell 形式** 在省略 `args` 時執行。`command` 字串被傳遞到 shell：macOS 和 Linux 上的 `sh -c`、Windows 上的 Git Bash，或未安裝 Git Bash 時的 PowerShell。設定 `shell` 欄位以明確選擇。Shell 標記化字串、展開變數並解釋管道、`&&`、重定向和 glob。 |      |                                                                                                                                                                                                                                                                                             |
| 在 Windows 上，exec 形式需要 `command` 解析為真實可執行檔，如 `.exe`。npm、npx、eslint 和其他工具在 `node_modules/.bin` 中安裝的 `.cmd` 和 `.bat` 填充程式不是可執行檔，無法在沒有 shell 的情況下生成。要在 exec 形式中執行它們，直接使用 `node` 呼叫底層指令碼，例如 `"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/node_modules/eslint/bin/eslint.js"]`。`node` 加上指令碼路徑模式在每個平台上都有效，因為 `node.exe` 是真實二進位檔。要按名稱執行 `.cmd` 或 `.bat` 填充程式，請使用 shell 形式。                                                                                                                                                                                                                                                                                                                                                                                                                                                               |      |                                                                                                                                                                                                                                                                                             |
| 此範例執行與外掛程式一起打包的 Node 指令碼。Exec 形式將解析的指令碼路徑作為一個參數傳遞，不進行引用：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |      |                                                                                                                                                                                                                                                                                             |

```
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}

```

等效的 shell 形式需要引用以處理包含空格或特殊字元的路徑：

```
{
  "type": "command",
  "command": "node \"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.js --fix"
}

```

兩種形式都支援相同的 [路徑佔位符](https://code.claude.com/docs/zh-TW/hooks#reference-scripts-by-path)，並且都將它們作為環境變數 `CLAUDE_PROJECT_DIR`、`CLAUDE_PLUGIN_ROOT` 和 `CLAUDE_PLUGIN_DATA` 匯出到生成的程序，因此指令碼可以讀取 `process.env.CLAUDE_PLUGIN_ROOT`，無論它是如何啟動的。 外掛程式 hooks 另外替換 [`${user_config.*}`](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration) 值，僅在 exec 形式中：該值被替換為 `command` 和每個 `args` 元素中的純字串，因此沒有 shell 重新解析它。 shell 形式的外掛程式 hook，其 `command` 參考 `${user_config.*}` 會失敗並出現 [錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config)，而不是執行。要在 shell 形式的 hook 中使用選項值，請讀取 `$CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數，例如 `webhook_url` 選項的 `$CLAUDE_PLUGIN_OPTION_WEBHOOK_URL`，或設定 `args` 以將 hook 切換到 exec 形式。在 v2.1.207 之前，shell 形式的外掛程式 hook 命令也替換了 `${user_config.*}`。 在 exec 形式中，`command` 僅是可執行檔名稱或路徑。如果 `command` 是沒有路徑分隔符的裸名稱，並且與 `args` 一起包含空格，Claude Code 會記錄警告，因為生成將失敗：沒有名為 `node script.js` 的可執行檔。將額外的令牌移到 `args` 中。包含空格的絕對路徑，如 `C:\Program Files\nodejs\node.exe`，是單個有效的可執行檔，不會觸發警告。

#### HTTP hook 欄位

除了 [通用欄位](https://code.claude.com/docs/zh-TW/hooks#common-fields) 外，HTTP hooks 還接受這些欄位：

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 必需 | 描述                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `url`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 是   | 要發送 POST 請求的 URL                                                                                                             |
| `headers`                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 否   | 其他 HTTP 標頭作為鍵值對。值支援使用 `$VAR_NAME` 或 `${VAR_NAME}` 語法的環境變數插值。只有列在 `allowedEnvVars` 中的變數才會被解析 |
| `allowedEnvVars`                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 否   | 可能被插值到標頭值中的環境變數名稱清單。對未列出的變數的參考會被替換為空字串。任何環境變數插值都需要此項                           |
| Claude Code 將 hook 的 [JSON 輸入](https://code.claude.com/docs/zh-TW/hooks#hook-input-and-output) 作為 POST 請求正文發送，`Content-Type: application/json`。回應正文使用與命令 hooks 相同的 [JSON 輸出格式](https://code.claude.com/docs/zh-TW/hooks#json-output)。 錯誤處理與命令 hooks 不同；請參閱 [HTTP 回應處理](https://code.claude.com/docs/zh-TW/hooks#http-response-handling)。 此範例將 `PreToolUse` 事件發送到本機驗證服務，使用來自 `MY_TOKEN` 環境變數的令牌進行驗證： |      |                                                                                                                                    |

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/pre-tool-use",
            "timeout": 30,
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

#### MCP 工具 hook 欄位

除了 [通用欄位](https://code.claude.com/docs/zh-TW/hooks#common-fields) 外，MCP 工具 hooks 還接受這些欄位：

| 欄位                                                                                                                                                                                                                                                                                                                                                       | 必需 | 描述                                                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `server`                                                                                                                                                                                                                                                                                                                                                   | 是   | 已配置的 MCP 伺服器的名稱。對於 [plugin-bundled server](https://code.claude.com/docs/zh-TW/mcp#plugin-provided-mcp-servers)，這是範圍名稱 `plugin:<plugin-name>:<server-name>`，例如 `plugin:my-plugin:db`，而不是裸伺服器金鑰。伺服器必須已連接；hook 永遠不會觸發 OAuth 或連接流程 |
| `tool`                                                                                                                                                                                                                                                                                                                                                     | 是   | 該伺服器上要呼叫的工具名稱                                                                                                                                                                                                                                                           |
| `input`                                                                                                                                                                                                                                                                                                                                                    | 否   | 傳遞給工具的參數。字串值支援來自 hook 的 [JSON 輸入](https://code.claude.com/docs/zh-TW/hooks#hook-input-and-output) 的 `${path}` 替換，例如 `"${tool_input.file_path}"`                                                                                                             |
| Claude Code 讀取工具的文字內容的方式與讀取命令 hook stdout 相同，遵循 [退出代碼 0 下的解析規則](https://code.claude.com/docs/zh-TW/hooks#exit-code-0)。如果命名的伺服器未連接，或工具返回 `isError: true`，hook 會產生非阻止性錯誤，執行繼續。 此範例在每個 `Write` 或 `Edit` 後在 `my_server` MCP 伺服器上呼叫 `security_scan` 工具，傳遞編輯檔案的路徑： |      |                                                                                                                                                                                                                                                                                      |

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "mcp_tool",
            "server": "my_server",
            "tool": "security_scan",
            "input": { "file_path": "${tool_input.file_path}" }
          }
        ]
      }
    ]
  }
}

```

MCP 工具 hook 只能在 Claude Code 將工作階段的 MCP 伺服器提供給 hooks 後執行。`SessionStart` 和 `Setup` 可能在該點之前觸發：

- **在啟動時** ：`SessionStart` 在伺服器可用之前觸發，包括當您使用 `--continue` 或 `--resume` 啟動時。Claude Code 跳過事件的 `mcp_tool` hooks 而不呼叫其工具，[debug log](https://code.claude.com/docs/zh-TW/hooks#debug-hooks) 記錄 `mcp_tool hooks are not available for the 'SessionStart' hook event (no MCP client context)`。
- **稍後在執行中的工作階段** ：在 `/clear` 或壓縮後，`SessionStart` 再次觸發，伺服器已可用，其 `mcp_tool` hooks 執行。
- **在`Setup` 上**：`Setup` 總是在伺服器可用之前觸發，因此 Claude Code 每次都跳過其 `mcp_tool` hooks 並記錄相同的訊息，命名 `Setup`。

例如，此配置在 `SessionStart` hook 上呼叫 `my_server` MCP 伺服器上的 `load_context` 工具，沒有匹配器，因此它適用於每個 `SessionStart` 來源：

```
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "mcp_tool",
            "server": "my_server",
            "tool": "load_context"
          }
        ]
      }
    ]
  }
}

```

當您執行 `claude` 時，Claude Code 跳過此 hook，永遠不呼叫 `load_context`，並將 `no MCP client context` 訊息寫入 debug log。在該相同工作階段中執行 `/clear`，hook 執行並呼叫 `load_context`。`type: "command"` hook 在 `SessionStart` 上執行，因此對於工作階段從其第一個轉向需要的任何內容，請使用一個。

#### 提示和代理 hook 欄位

除了 [通用欄位](https://code.claude.com/docs/zh-TW/hooks#common-fields) 外，提示和代理 hooks 還接受這些欄位：

| 欄位     | 必需 | 描述                                                                                                                          |
| -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| `prompt` | 是   | 要發送到模型的提示文字。使用 `$ARGUMENTS` 作為 hook 輸入 JSON 的佔位符。使用反斜線逸出以包含字面文字：`\$1.00` 呈現為 `$1.00` |
| `model`  | 否   | 用於評估的模型。預設為快速模型                                                                                                |

### 按路徑參考指令碼

使用這些佔位符按相對於專案或外掛程式根目錄的路徑參考 hook 指令碼，無論 hook 執行時的工作目錄如何：

- `${CLAUDE_PROJECT_DIR}`：工作階段開始的專案根目錄。Claude Code 也在 [stdio MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp#option-3-add-a-local-stdio-server) 和外掛程式 LSP 伺服器的環境中設定此變數。
- `${CLAUDE_PLUGIN_ROOT}`：外掛程式的安裝目錄，用於與 [plugin](https://code.claude.com/docs/zh-TW/plugins) 一起打包的指令碼。請參閱 [外掛程式環境變數](https://code.claude.com/docs/zh-TW/plugins-reference#environment-variables) 以了解路徑在更新中的行為。
- `${CLAUDE_PLUGIN_DATA}`：外掛程式的 [持久資料目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)，用於應該在外掛程式更新後保留的依賴項和狀態。

**Worktrees 不同。** 如果 Claude 在工作階段期間進入 [worktree](https://code.claude.com/docs/zh-TW/worktrees)，Claude Code 將 `${CLAUDE_PROJECT_DIR}` 保留在原位，並以不同的方式將 worktree 路徑傳遞給您的 hooks：

- **`${CLAUDE_PROJECT_DIR}`保持不變** ：它仍然指向工作階段開始的專案根目錄，因此像 `${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh` 這樣的命令仍然在主簽出中執行指令碼。
- **`cwd`跟隨 Claude** ：hook 的 [輸入 JSON](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 中的 `cwd` 欄位在 Claude 進入 worktree 後是 worktree 根目錄，在 Claude 執行 `cd` 後是新目錄。當 hook 需要知道 Claude 正在哪個目錄中工作時，讀取它。

對於任何參考路徑佔位符的 hook，優先使用 [exec 形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)。在 shell 形式中，用雙引號括起每個佔位符。

- 專案指令碼
- 外掛程式指令碼

此範例使用 `${CLAUDE_PROJECT_DIR}` 在任何 `Write` 或 `Edit` 工具呼叫後從專案的 `.claude/hooks/` 目錄執行樣式檢查器：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh",
            "args": []
          }
        ]
      }
    ]
  }
}

```

在 `hooks/hooks.json` 中定義外掛程式 hooks，使用可選的頂層 `description` 欄位。啟用外掛程式時，其 hooks 會與您的使用者和專案 hooks 合併。此範例執行與外掛程式一起打包的格式化指令碼：

```
{
  "description": "Automatic code formatting",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh",
            "args": [],
            "timeout": 30
          }
        ]
      }
    ]
  }
}

```

有關建立外掛程式 hooks 的詳細資訊，請參閱 [外掛程式元件參考](https://code.claude.com/docs/zh-TW/plugins-reference#hooks)。

### Skills 和代理中的 Hooks

除了設定檔和外掛程式外，hooks 還可以使用 frontmatter 直接在 [skills](https://code.claude.com/docs/zh-TW/skills) 和 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 中定義，使用與基於設定的 hooks 相同的配置格式。Claude Code 保持它們註冊的時間取決於元件：

- **Subagent hooks** ：Claude Code 僅在該 subagent 執行時執行它們，並在其完成時移除它們。Claude Code 在此處將 `Stop` hook 轉換為 `SubagentStop`，這是 subagent 完成時觸發的事件。
- **Skill hooks** ：Claude Code 在您或 Claude 叫用 skill 時註冊它們，並在工作階段的其餘部分保持執行它們，在 skill 自己的轉向之後的轉向上也是如此。要讓 Claude Code 在第一次成功執行後移除 hook，請在其上設定 [`once: true`](https://code.claude.com/docs/zh-TW/hooks#common-fields)。

此 skill 定義了一個 `PreToolUse` hook，在每個 `Bash` 命令之前執行安全驗證指令碼：

```
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---

```

Subagents 在其 YAML frontmatter 中使用相同的格式。 專案 skill 中的 Frontmatter hooks 遵循與設定檔中 hooks 相同的 [工作區信任規則](https://code.claude.com/docs/zh-TW/hooks#workspace-trust)。Claude Code 在您或 Claude 叫用 skill 時註冊它們，包括在您未信任的資料夾中的 `-p` 執行。 專案 subagent 中的 Frontmatter hooks 僅在您接受代理檔案來自的資料夾的 [工作區信任對話](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust) 後執行。`-p` 工作階段不計為接受它。[在您信任資料夾之前執行的內容](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 將此與設定檔規則進行比較，subagents 頁面列出 [哪些範圍是豁免的](https://code.claude.com/docs/zh-TW/sub-agents#hooks-in-subagent-frontmatter)。在 v2.1.218 之前，這些 hooks 可以從您未信任的資料夾執行。

### `/hooks` 選單

在 Claude Code 中輸入 `/hooks` 以開啟唯讀瀏覽器來查看您配置的 hooks。選單顯示每個 hook 事件及其配置的 hooks 計數，讓您深入查看匹配器，並顯示每個 hook 處理程式的完整詳細資訊。使用它來驗證配置、檢查 hook 來自哪個設定檔，或檢查 hook 的命令、提示或 URL。 選單顯示所有五種 hook 類型：`command`、`prompt`、`agent`、`http` 和 `mcp_tool`。每個 hook 都標有 `[type]` 前綴和指示其定義位置的來源：

- `User Settings`：來自 `~/.claude/settings.json`
- `Project Settings`：來自 `.claude/settings.json`
- `Local Settings`：來自 `.claude/settings.local.json`
- `Plugin Hooks`：來自外掛程式的 `hooks/hooks.json`
- `Session Hooks`：在目前工作階段中記錄在記憶體中

選擇 hook 會開啟詳細檢視，顯示其事件、匹配器、類型、來源檔案和完整命令、提示或 URL。選單是唯讀的：要新增、修改或移除 hooks，請直接編輯設定 JSON 或要求 Claude 進行變更。

### 停用或移除 hooks

要移除 hook，請從設定 JSON 檔案中刪除其項目。 要暫時停用所有 hooks 而不移除它們，請在設定檔中設定 `"disableAllHooks": true`。Claude Code 讀取 [設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence) 應用後剩下的值，因此專案的 `.claude/settings.json` 中的 `"disableAllHooks": false` 會覆蓋您的使用者設定中的 `true`。要根據專案的設定關閉一次執行的 hooks，請傳遞 `--settings '{"disableAllHooks": true}'`，這優先於專案和本機設定。沒有辦法在保留 hook 在配置中的同時停用單個 hook。 `disableAllHooks` 設定遵循受管理的設定階層。如果管理員已通過受管理的原則設定配置了 hooks，則在使用者、專案或本機設定中設定的 `disableAllHooks` 無法停用這些受管理的 hooks。只有在受管理的設定層級設定的 `disableAllHooks` 才能停用受管理的 hooks。有關每個層級的完整範圍，請參閱 [`disableAllHooks`](https://code.claude.com/docs/zh-TW/settings-reference#disableallhooks)。 對設定檔中 hooks 的直接編輯通常由檔案監視程式自動拾取。

## Hook 輸入和輸出

命令 hooks 通過 stdin 接收 JSON 資料，並通過退出代碼、stdout 和 stderr 傳回結果。HTTP hooks 接收相同的 JSON 作為 POST 請求正文，並通過 HTTP 回應正文傳回結果。本部分涵蓋所有事件通用的欄位和行為。每個事件在 [Hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events) 下的部分包括其特定的輸入架構和決定控制選項。 在 macOS 和 Linux 上，命令 hooks 在沒有控制終端的自己的工作階段中執行。Hook 程序和任何子程序無法開啟 `/dev/tty` 或直接向 Claude Code 介面發送逃逸序列。Windows 沒有 `/dev/tty`。 要在任何平台上向使用者顯示訊息，請在 JSON 輸出中返回 [`systemMessage`](https://code.claude.com/docs/zh-TW/hooks#json-output)。某些事件會捨棄它或將其傳遞到其他地方，每個 [事件的部分](https://code.claude.com/docs/zh-TW/hooks#hook-events) 都會說明。要觸發桌面通知、設定視窗標題或響鈴，請改為返回 [`terminalSequence`](https://code.claude.com/docs/zh-TW/hooks#emit-terminal-notifications)。

### 通用輸入欄位

Hook 事件接收這些欄位作為 JSON，除了每個 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events) 部分中記錄的事件特定欄位。對於命令 hooks，此 JSON 通過 stdin 到達。對於 HTTP hooks，它作為 POST 請求正文到達。

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `session_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 目前工作階段識別碼                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `prompt_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | UUID 識別目前正在處理的使用者提示。與 [OpenTelemetry 事件上的 `prompt.id` 屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes) 相符，因此您可以將 hook 輸出與單一提示的遙測相關聯。在第一個使用者輸入之前不存在。需要 Claude Code v2.1.196 或更新版本                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `transcript_path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 對話 JSON 的路徑。成績單檔案以非同步方式寫入，可能滯後於記憶體中的對話，因此當 hook 觸發時，它可能尚未包含目前回合的最新訊息。需要目前回合最後助手文字的 Hooks 應在 [Stop](https://code.claude.com/docs/zh-TW/hooks#stop) 和 [SubagentStop](https://code.claude.com/docs/zh-TW/hooks#subagentstop) 上使用 `last_assistant_message`，而不是讀取成績單                                                                                                                                                                                                                                                                                                                                                                           |
| `cwd`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 叫用 hook 時的目前工作目錄                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `scratchpad_dir`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 工作階段的暫存目錄的路徑，Claude 在其中保存臨時工作檔案。當工作階段沒有暫存或臨時目錄不可用時不存在。需要 Claude Code v2.1.257 或更新版本                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `permission_mode`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 目前 [權限模式](https://code.claude.com/docs/zh-TW/permissions#permission-modes)：`"default"`、`"plan"`、`"acceptEdits"`、`"auto"`、`"dontAsk"` 或 `"bypassPermissions"`。標記為**手動** 的模式以 `"default"` 到達，永遠不會以 `"manual"` 到達，因此匹配 `"default"` 的指令碼繼續工作。並非所有事件都接收此欄位。檢查每個 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events) 部分中的 JSON 範例                                                                                                                                                                                                                                                                                                                 |
| `effort`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 物件，其 `level` 欄位保存執行 hook 時生效的 [努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)：`"low"`、`"medium"`、`"high"`、`"xhigh"` 或 `"max"`。如果您設定的等級是活躍模型不支援的，`level` 會報告 Claude Code 實際執行的等級；[調整努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level) 說明它如何選擇該等級。Ultracode 不是一個不同的等級，報告為 `"xhigh"`。該物件與 [狀態行](https://code.claude.com/docs/zh-TW/statusline#available-data) `effort` 欄位相符。存在於在工具使用上下文中觸發的事件，例如 `PreToolUse`、`PostToolUse`、`Stop` 和 `SubagentStop`，當目前模型支援努力參數時。該等級也可作為 `$CLAUDE_EFFORT` 環境變數提供給 hook 命令和 Bash 工具。 |
| `hook_event_name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 觸發的事件名稱                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 使用 `--agent` 執行或在 subagent 內執行時，包括兩個額外欄位：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `agent_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Subagent 的唯一識別碼。僅當 hook 在 subagent 呼叫內觸發時出現。使用此項來區分 subagent hook 呼叫與主執行緒呼叫。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `agent_type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 代理名稱（例如 `"Explore"` 或 `"security-reviewer"`）。當工作階段使用 `--agent` 或 hook 在 subagent 內觸發時出現。對於 subagents，subagent 的類型優先於工作階段的 `--agent` 值。請參閱 [SubagentStart](https://code.claude.com/docs/zh-TW/hooks#subagentstart) 以了解自訂和 plugin subagents 報告的值，以及如何針對 plugin 範圍名稱編寫匹配器。                                                                                                                                                                                                                                                                                                                                                                                |
| 只有 [`SessionStart`](https://code.claude.com/docs/zh-TW/hooks#sessionstart) hooks 可以接收 `model` 欄位，且 Claude Code 不一定包含它。[`PreModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 和 [`PostModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#postmodelswitch) hooks 接收 `from_model` 和 `to_model` 代替，因此使用 PostModelSwitch hook 來追蹤模型在工作階段期間的變化。 沒有 `$CLAUDE_MODEL` 環境變數。如果您在 shell 中設定它，hook 可以讀取 `$ANTHROPIC_MODEL`，但當您在工作階段期間使用 `/model` 切換模型時，該值不會改變。 Hook 程序繼承父環境，除了 Claude Code [從它產生的每個子程序中移除](https://code.claude.com/docs/zh-TW/monitoring-usage#administrator-configuration) 的 `OTEL_*` 匯出器變數，以及當 [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/zh-TW/env-vars#variables) 設定為 `1` 時，它剝離的變數。 例如，Bash 命令的 `PreToolUse` hook 在 stdin 上接收此內容： |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

```
{
  "session_id": "abc123",
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "scratchpad_dir": "/tmp/claude-1000/-home-user-my-project/abc123/scratchpad",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run test suite",
    "timeout": 120000,
    "run_in_background": false
  },
  "tool_use_id": "toolu_01ABC123..."
}

```

`tool_name`、`tool_input` 和 `tool_use_id` 欄位是事件特定的。每個 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events) 部分記錄了該事件的額外欄位。

### 退出代碼輸出

來自您的 hook 命令的退出代碼告訴 Claude Code 該操作是應該進行、被阻止還是被忽略。退出代碼不單獨起作用。Claude Code 在每個退出代碼上從 stdout 讀取 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output)，而不僅僅是 0，對於使用標準決定模型的事件，通過架構驗證的已解析物件與代碼一起生效。Exit 2 的阻止是 JSON 無法覆蓋的唯一結果。 兩個表格擁有每個事件的例外：[每個事件的退出代碼 2 行為](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event) 說明每個事件的退出代碼做什麼，[決定控制](https://code.claude.com/docs/zh-TW/hooks#decision-control) 說明每個事件接受哪些決定欄位。通用欄位（如 `systemMessage`）在大多數事件中工作，並列在 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output) 表格中。

#### 退出代碼 0

退出 0 表示成功，是當您列印 JSON 進行結構化控制時的預期退出代碼。 對於大多數事件，Claude Code 將 stdout 寫入詳細日誌，不在成績單中顯示。例外是 `UserPromptSubmit`、`UserPromptExpansion`、`SessionStart` 和 `PostModelSwitch`，其中 Claude Code 將純文字 stdout 新增為 Claude 可以看到和作用的上下文。 Claude Code 是否將您的 stdout 讀取為 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output) 或純文字取決於它如何開始和結束，忽略周圍的空白：

- **以`{` 開始並以 `}` 結束**：Claude Code 將其解析為 JSON。當輸出是兩行或更多行，每行本身都解析為 JSON，且沒有行是設定欄位的 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output) 物件時，Claude Code 將整個輸出視為純文字。當其中一行確實設定欄位時，整個輸出是解析失敗，如下所述。
- **以`{` 開始但不以 `}` 結束**：Claude Code 將其視為純文字。
- **以其他任何內容開始** ：Claude Code 將其視為純文字、JSON 陣列或包含的引用 JSON 字串。

對於使用標準決定模型的事件，以已解析物件退出 0 但未通過架構驗證是非阻止性錯誤：操作進行，成績單顯示 `<hook name> hook error` 通知，帶有驗證訊息。在任何退出代碼上都會發生相同情況，除了 2，而 [exit 2 仍然阻止](https://code.claude.com/docs/zh-TW/hooks#exit-code-2)。 對於使用標準決定模型的事件，當 Claude Code 嘗試將您的 stdout 解析為 JSON 且無法時，它在除 2 以外的每個退出代碼上報告非阻止性錯誤。成績單顯示 `<hook name> hook error` 通知，帶有解析訊息。在新增純文字 stdout 作為上下文的事件上，Claude Code 不新增文字。在 v2.1.248 之前，Claude Code 將該 stdout 視為純文字。 來自以 0 退出的 hook 的 Stderr 僅進入詳細日誌，永遠不進入成績單，Claude 永遠看不到它。要自己讀取它，請啟用 [詳細日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)。要從 `PostToolUse` 或 `PostToolUseFailure` hook 向 Claude 顯示警告，請改為退出 2，以便 [Claude 看到 stderr](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event)，儘管工具已執行。

#### 退出代碼 2

退出 2 表示阻止性錯誤。在 [可以阻止的事件](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event) 上，退出 2 無論您是否列印 JSON 都會阻止：即使 JSON `permissionDecision` 為 `"allow"` 也無法覆蓋它。Claude Code 仍然在 stdout 上讀取任何有效的 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output)。在 `Elicitation` 和 `ElicitationResult` 上，exit-2 hook 的 `hookSpecificOutput` 被忽略。 阻止訊息是您的 JSON 的阻止決定的原因（當它做出決定時），否則是您的 stderr 文字。阻止做什麼因事件而異：`PreToolUse` 阻止工具呼叫，`UserPromptSubmit` 拒絕提示，等等。[每個事件的退出代碼 2 行為](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event) 列出每個事件的效果，每個事件的部分說明訊息去哪裡。 在列印未通過 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output) 架構驗證的 JSON 時退出 2 的 hook 仍然阻止：Claude Code 使用 stderr 作為阻止原因，並在詳細日誌中記錄驗證失敗。在 v2.1.214 之前，Claude Code 將該組合視為非阻止性錯誤，操作進行。 此指令碼通過退出 2 阻止 `rm` 命令，並將每個其他命令留給正常權限流程：

```
#!/bin/bash
# 從 stdin 讀取 JSON 輸入，檢查命令
input=$(cat)
command=$(jq -r '.tool_input.command' <<<"$input")

if [[ "$command" == rm* ]]; then
  echo "Blocked: rm commands are not allowed" >&2
  exit 2  # 阻止性錯誤：工具呼叫被阻止
fi

exit 0  # 無決定：正常權限流程適用

```

#### 其他退出代碼

任何其他退出代碼對於大多數 hook 事件本身不會阻止。發生的情況取決於您的 stdout：

- 使用通過架構驗證的已解析物件，對於使用標準決定模型的事件，Claude Code 忽略退出代碼，JSON 單獨決定結果：
  - 事件支援的每個欄位都被接受，包括 `permissionDecision`、`additionalContext`、`updatedInput` 和 `systemMessage`，hook 不被報告為錯誤。
  - [決定控制](https://code.claude.com/docs/zh-TW/hooks#decision-control) 列出每個事件的決定欄位；通用欄位如 `systemMessage` 遵循 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output) 表格。
- 使用未通過架構驗證的已解析物件，對於使用標準決定模型的事件，它與 [exit 0 上](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 相同的非阻止性錯誤：操作進行，`<hook name> hook error` 通知帶有驗證訊息。
- 使用 Claude Code [嘗試解析為 JSON](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 且無法的 stdout，Claude Code 對於使用標準決定模型的事件報告與 exit 0 上相同的非阻止性錯誤。操作進行，通知帶有解析訊息。
- 使用 Claude Code [視為純文字](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 的 stdout，或使用空 stdout，對於大多數 hook 事件是非阻止性錯誤：操作進行，成績單顯示 `<hook name> hook error` 通知，後跟 stderr 的第一行，前綴為 `Failed with non-blocking status code:`。要捕獲完整 stderr，請啟用 [詳細日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)。

標準決定模型之外的事件在 [每個事件表](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event) 中保持自己的行：`WorktreeCreate` 在任何非零退出時失敗建立，無論您的 JSON 說什麼，事件完全捨棄 hook 輸出（如 `StopFailure`）除了副作用欄位（如 `terminalSequence`）在每個退出代碼上忽略您的 JSON，除了副作用欄位（如 `terminalSequence`），它仍然觸發。 無法啟動的 hook 落入相同的非阻止性桶。當指令碼路徑不存在或不可執行時，shell 以代碼（如 127）退出，您看到相同的通知，帶有解釋器的訊息，例如 `Failed with non-blocking status code: /bin/sh: /path/to/hook.sh: No such file or directory`。對於大多數 hook 事件，操作進行。當您設定原則 hook 時，在其第一次執行時監視此通知：`settings.json` 中的拼寫錯誤路徑使閘門無聲地禁用。 對於大多數 hook 事件，退出代碼 2 是唯一通過代碼單獨阻止的退出代碼。沒有 stdout 上的有效 JSON，Claude Code 將退出代碼 1 視為非阻止性錯誤並繼續操作，儘管 1 是傳統的 Unix 失敗代碼。如果您的 hook 旨在強制執行原則，請使用 `exit 2`。Worktree 事件不同：來自 `WorktreeCreate` 的任何非零退出代碼都會中止 worktree 建立，來自 `WorktreeRemove` 的任何非零退出代碼會在目錄仍然存在後使 worktree 移除失敗。

#### 逾時

除了您使用 [`async: true`](https://code.claude.com/docs/zh-TW/hooks#run-hooks-in-the-background) 執行的命令 hook，Claude Code 取消達到其 [`timeout`](https://code.claude.com/docs/zh-TW/hooks#common-fields) 的 `command`、`http` 或 `mcp_tool` hook，捨棄 hook 的輸出，因此在大多數事件上，逾時的 hook 不呈現決定。 在 [`PreModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 上，在其逾時時取消的 hook 阻止模型切換。在 `PreToolUse` 上，兩個 hook 系列不同：

- 逾時的 `command`、`http` 或 `mcp_tool` hook 不阻止工具呼叫。呼叫通過正常 [權限流程](https://code.claude.com/docs/zh-TW/permissions) 繼續，因此不要指望停滯的 hook 充當閘門。
- 超過其逾時的 [Agent SDK 回調 hook](https://code.claude.com/docs/zh-TW/agent-sdk/hooks) [阻止工具呼叫](https://code.claude.com/docs/zh-TW/hooks#pretooluse)。

#### 每個事件的退出代碼 2 行為

退出代碼 2 是 hook 發出「停止，不要這樣做」的方式。效果取決於事件，因為某些事件代表可以被阻止的操作（例如尚未發生的工具呼叫），而其他事件代表已經發生或無法防止的事情。

| Hook 事件                                                                                                                                                                                                                                                                                                                                                       | 可以阻止？ | 退出 2 時發生的情況                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PreToolUse`                                                                                                                                                                                                                                                                                                                                                    | 是         | 阻止工具呼叫                                                                                                                                                                                                                                |
| `PermissionRequest`                                                                                                                                                                                                                                                                                                                                             | 否         | 此事件不接受退出代碼 2，權限流程保持不變。改為通過 [`decision` 物件](https://code.claude.com/docs/zh-TW/hooks#permissionrequest-decision-control) 拒絕                                                                                      |
| `UserPromptSubmit`                                                                                                                                                                                                                                                                                                                                              | 是         | 阻止提示處理並清除提示                                                                                                                                                                                                                      |
| `UserPromptExpansion`                                                                                                                                                                                                                                                                                                                                           | 是         | 阻止擴展                                                                                                                                                                                                                                    |
| `Stop`                                                                                                                                                                                                                                                                                                                                                          | 是         | 防止 Claude 停止，繼續對話                                                                                                                                                                                                                  |
| `SubagentStop`                                                                                                                                                                                                                                                                                                                                                  | 是         | 防止 subagent 停止                                                                                                                                                                                                                          |
| `TeammateIdle`                                                                                                                                                                                                                                                                                                                                                  | 是         | 防止隊友閒置，所以它繼續工作                                                                                                                                                                                                                |
| `TaskCreated`                                                                                                                                                                                                                                                                                                                                                   | 是         | 回滾任務建立                                                                                                                                                                                                                                |
| `TaskCompleted`                                                                                                                                                                                                                                                                                                                                                 | 是         | 防止任務被標記為已完成                                                                                                                                                                                                                      |
| `ConfigChange`                                                                                                                                                                                                                                                                                                                                                  | 是         | 阻止配置變更生效（除了 `policy_settings`）                                                                                                                                                                                                  |
| `StopFailure`                                                                                                                                                                                                                                                                                                                                                   | 否         | 輸出和退出代碼被忽略，除了 `terminalSequence`                                                                                                                                                                                               |
| `PostToolUse`                                                                                                                                                                                                                                                                                                                                                   | 否         | 向 Claude 顯示 stderr；工具已執行                                                                                                                                                                                                           |
| `PostToolUseFailure`                                                                                                                                                                                                                                                                                                                                            | 否         | 向 Claude 顯示 stderr；工具已失敗                                                                                                                                                                                                           |
| `PostToolBatch`                                                                                                                                                                                                                                                                                                                                                 | 是         | 在下一個模型呼叫之前停止代理迴圈                                                                                                                                                                                                            |
| `PermissionDenied`                                                                                                                                                                                                                                                                                                                                              | 否         | 退出代碼和 stderr 被忽略，因為拒絕已發生。使用 JSON `hookSpecificOutput.retry: true` 告訴模型它可能重試；Claude Code 忽略 [no-verdict denials](https://code.claude.com/docs/zh-TW/hooks#permissiondenied-decision-control) 的 `retry: true` |
| `Notification`                                                                                                                                                                                                                                                                                                                                                  | 否         | 退出代碼和 stderr 被忽略                                                                                                                                                                                                                    |
| `SubagentStart`                                                                                                                                                                                                                                                                                                                                                 | 否         | 僅向使用者顯示 stderr                                                                                                                                                                                                                       |
| `SessionStart`                                                                                                                                                                                                                                                                                                                                                  | 否         | 僅向使用者顯示 stderr                                                                                                                                                                                                                       |
| `Setup`                                                                                                                                                                                                                                                                                                                                                         | 否         | 退出代碼和 stderr 被忽略                                                                                                                                                                                                                    |
| `SessionEnd`                                                                                                                                                                                                                                                                                                                                                    | 否         | 僅向使用者顯示 stderr                                                                                                                                                                                                                       |
| `CwdChanged`                                                                                                                                                                                                                                                                                                                                                    | 否         | 僅向使用者顯示 stderr                                                                                                                                                                                                                       |
| `DirectoryAdded`                                                                                                                                                                                                                                                                                                                                                | 否         | Stderr 進入詳細日誌；目錄已新增                                                                                                                                                                                                             |
| `FileChanged`                                                                                                                                                                                                                                                                                                                                                   | 否         | 僅向使用者顯示 stderr                                                                                                                                                                                                                       |
| `PreCompact`                                                                                                                                                                                                                                                                                                                                                    | 是         | 阻止壓縮                                                                                                                                                                                                                                    |
| `PostCompact`                                                                                                                                                                                                                                                                                                                                                   | 否         | 僅向使用者顯示 stderr                                                                                                                                                                                                                       |
| `PreModelSwitch`                                                                                                                                                                                                                                                                                                                                                | 是         | 阻止模型切換並向使用者顯示 stderr                                                                                                                                                                                                           |
| `PostModelSwitch`                                                                                                                                                                                                                                                                                                                                               | 否         | 僅向使用者顯示 stderr；模型已切換                                                                                                                                                                                                           |
| `Elicitation`                                                                                                                                                                                                                                                                                                                                                   | 是         | 拒絕徵詢                                                                                                                                                                                                                                    |
| `ElicitationResult`                                                                                                                                                                                                                                                                                                                                             | 是         | 阻止回應（操作變為拒絕）                                                                                                                                                                                                                    |
| `WorktreeCreate`                                                                                                                                                                                                                                                                                                                                                | 是         | 任何非零退出代碼都會導致 worktree 建立失敗                                                                                                                                                                                                  |
| `WorktreeRemove`                                                                                                                                                                                                                                                                                                                                                | 是         | 任何非零退出代碼會在目錄仍然存在後使 worktree 移除失敗。請參閱 [WorktreeRemove](https://code.claude.com/docs/zh-TW/hooks#worktreeremove) 以了解目錄發生的情況                                                                               |
| `InstructionsLoaded`                                                                                                                                                                                                                                                                                                                                            | 否         | 退出代碼被忽略                                                                                                                                                                                                                              |
| `MessageDisplay`                                                                                                                                                                                                                                                                                                                                                | 否         | 原始文字被顯示                                                                                                                                                                                                                              |
| 對於 `SessionStart`、`SubagentStart` 和 `PostModelSwitch`，Claude Code 在成績單中呈現退出代碼 2 stderr 作為 `<hook name> hook error` 通知，與 [非阻止性錯誤](https://code.claude.com/docs/zh-TW/hooks#exit-code-output) 相同的方式。Claude 看不到它，工作階段或 subagent 繼續進行。對於 `SubagentStart`，通知出現在 subagent 自己的成績單中，而不是在父對話中。 |            |                                                                                                                                                                                                                                             |

### HTTP 回應處理

HTTP hooks 使用 HTTP 狀態代碼和回應正文，而不是退出代碼和 stdout。下面的結果適用於大多數事件；在 [每個事件表](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event) 中有自己的失敗合約的事件（如 `WorktreeCreate`）將該合約應用於失敗的 HTTP hook：

- **2xx 且正文為空** ：成功，等同於退出代碼 0 且無輸出
- **2xx 且 JSON 物件正文** ：使用與命令 hooks 相同的 [JSON 輸出](https://code.claude.com/docs/zh-TW/hooks#json-output) 架構進行解析。未通過架構驗證的正文是非阻止性錯誤
- **2xx 且任何其他正文，如純文字** ：非阻止性錯誤，處理方式與非 2xx 狀態相同。Claude Code 不將文字新增到 Claude 的上下文
- **非 2xx 狀態** ：非阻止性錯誤，執行繼續
- **連線失敗** ：非阻止性錯誤，執行繼續
- **逾時** ：hook 被取消，如 [逾時](https://code.claude.com/docs/zh-TW/hooks#timeouts) 下所述

與命令 hooks 不同，HTTP hooks 無法僅通過狀態代碼發出阻止性錯誤信號。要阻止工具呼叫或拒絕權限，請返回 2xx 回應，其 JSON 正文包含適當的決定欄位。

### JSON 輸出

退出代碼只讓您阻止或保持沉默，但 JSON 輸出提供更細粒度的控制。與其以代碼 2 退出來阻止，不如退出 0 並將 JSON 物件列印到 stdout。Claude Code 從該 JSON 讀取特定欄位以控制行為，包括 [決定控制](https://code.claude.com/docs/zh-TW/hooks#decision-control) 以阻止、允許或升級給使用者。 為每個 hook 選擇一種方法：要麼單獨使用退出代碼進行信號傳遞，要麼退出 0 並列印 JSON 進行結構化控制。如果您混合它們，退出 2 保持其 [阻止效果](https://code.claude.com/docs/zh-TW/hooks#exit-code-2-behavior-per-event)，Claude Code 仍然讀取 JSON 欄位，除了 [Exit code 2](https://code.claude.com/docs/zh-TW/hooks#exit-code-2) 下記錄的一個徵詢例外。 您的 hook 的 stdout 必須僅包含 JSON 物件。如果您的 shell 設定檔在啟動時列印文字，它可能會干擾 JSON 解析。請參閱故障排除指南中的 [Hook JSON 無效](https://code.claude.com/docs/zh-TW/hooks-guide#hook-json-has-no-effect)。 Hook 的 `additionalContext`、`systemMessage` 和 `initialUserMessage` 字串，以及其純 stdout，上限為 10,000 個字元：

- **範圍** ：Claude Code 分別測量每個字串，即使多個 hooks 為同一事件執行。對於 JSON 輸出，每個欄位分別測量；純 stdout 整體測量。
- **超過限制** ：Claude Code 將輸出儲存到工作階段目錄中的檔案，並將其替換為檔案路徑和最多前 2,000 個字元的預覽。大型有效 Bash 結果的處理方式相同，如 [輸出限制](https://code.claude.com/docs/zh-TW/tools-reference#output-limits) 下所述。與該 Bash 上限不同，此上限沒有設定或環境變數來提高它。
- **讀取檔案** ：Claude Code 不要求 Claude 讀取檔案，因此將 Claude 必須始終看到的任何內容保持在上限內。

JSON 物件支援三種欄位：

- **通用欄位** ，如 `continue`，列在下表中。每個事件都接受它們，但某些事件捨棄它們或將 `systemMessage` 傳遞到成績單以外的地方。每個事件的部分都說明。`terminalSequence` 在這些事件上也工作，除了 [發出終端通知](https://code.claude.com/docs/zh-TW/hooks#emit-terminal-notifications) 下列出的例外。
- **頂層`decision` 和 `reason`** 由某些事件用來阻止或提供反饋。
- \*\*`hookSpecificOutput`\*\*是一個嵌套物件，用於需要更豐富控制的事件。它需要一個設定為事件名稱的`hookEventName` 欄位。

| 欄位                | 預設    | 描述                                                                                                                                                                                                                                                                                                               |
| ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `continue`          | `true`  | 如果為 `false`，Claude 在 hook 執行後完全停止處理。優先於任何事件特定的決定欄位                                                                                                                                                                                                                                    |
| `stopReason`        | 無      | 當 `continue` 為 `false` 時向使用者顯示的訊息。它停留在對話中，因此如果對話繼續，Claude 會看到它                                                                                                                                                                                                                   |
| `suppressOutput`    | `false` | 無效果：Claude Code 接受欄位但不作用。成功的 hook 的 stdout 永遠不在成績單中顯示，並在詳細日誌中記錄                                                                                                                                                                                                               |
| `systemMessage`     | 無      | 向使用者顯示的警告訊息。在 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 和 [`--output-format stream-json`](https://code.claude.com/docs/zh-TW/headless) 輸出中，它可以作為 [`SDKInformationalMessage`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkinformationalmessage) 到達 |
| `terminalSequence`  | 無      | Claude Code 代表您發出的終端逃逸序列，例如桌面通知、視窗標題或響鈴。限制為 OSC `0`/`1`/`2`/`9`/`99`/`777` 和 BEL。如果值包含允許清單外的任何內容，該欄位將被忽略。使用此項而不是寫入 `/dev/tty`，後者對 hooks 不可用                                                                                               |
| 要完全停止 Claude： |         |                                                                                                                                                                                                                                                                                                                    |

```
{ "continue": false, "stopReason": "Build failed, fix errors before continuing" }

```

對於 `PreToolUse` 和 `PostToolUse` hooks，停止適用，即使工具呼叫失敗或在 Claude 仍在串流回應時完成。

#### 發出終端通知

Hooks 在沒有控制終端的情況下執行，因此直接寫入逃逸序列到 `/dev/tty` 會失敗。相反，在 `terminalSequence` 欄位中返回逃逸序列，Claude Code 通過其自己的終端寫入路徑為您發出它。這是無競爭的，在 tmux 和 GNU screen 內工作，並在沒有 `/dev/tty` 的 Windows 上工作。 該欄位接受一個或多個允許清單逃逸序列的字串：

- OSC `0`、`1`、`2`：視窗和圖示標題
- OSC `9`：iTerm2、ConEmu、Windows Terminal 和 WezTerm 通知，包括 `9;4` 工作列進度
- OSC `99`：Kitty 通知
- OSC `777`：urxvt、Ghostty 和 Warp 通知
- 裸 BEL

序列可以用 BEL 或 ST 終止。允許清單外的任何內容，包括 CSI 游標和顏色序列、OSC 調色板序列、OSC 8 超連結、OSC 52 剪貼簿寫入和 OSC 1337，都會被拒絕，該欄位將被忽略。 Claude Code 在處理您的 hook 輸出時寫入序列本身，因此該欄位在捨棄 `systemMessage` 和 `continue` 的事件上工作，例如 `Notification` 和 `StopFailure`。它有兩個限制：

- Claude Code 僅在互動式工作階段中寫入序列，且僅在其介面在螢幕上時。在使用 `-p` 旗標的非互動式模式和 Agent SDK 中，它忽略該欄位。
- `WorktreeCreate` 命令 hook 無法返回 JSON，因為 Claude Code 將其 stdout 讀取為 worktree 路徑。HTTP `WorktreeCreate` hook 返回 JSON 並可以包含該欄位。

下面的範例從 `Notification` hook 觸發桌面通知。逃逸序列使用 `printf` 八進位逃逸構建，因此控制位元組永遠不會出現在 shell 命令行上，`jq -n --arg` 構建 JSON 輸出，因此通知訊息中的引號、反斜線和換行符被正確逃逸：

```
#!/bin/bash
# Notification hook：當 Claude Code 需要注意時 ping 桌面。
input=$(cat)
title="Claude Code"
body=$(jq -r '.message // "Needs your attention"' <<<"$input")
seq=$(printf '\033]777;notify;%s;%s\007' "$title" "$body")
jq -nc --arg seq "$seq" '{terminalSequence: $seq}'

```

`{ "terminalSequence": "..." }` 形狀在任何 shell 或語言中都相同。

#### 為 Claude 新增上下文

`additionalContext` 欄位將字串從您的 hook 傳遞到 Claude 的上下文視窗。Claude Code 將字串包裝在系統提醒中，並將其插入到 hook 觸發的對話點。Claude 在下一個模型請求時讀取提醒，但它不會在介面中顯示為聊天訊息。 在 `hookSpecificOutput` 中返回 `additionalContext` 以及事件名稱：

```
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "This file is generated. Edit src/schema.ts and run `bun generate` instead."
  }
}

```

提醒出現的位置取決於事件：

- [SessionStart](https://code.claude.com/docs/zh-TW/hooks#sessionstart) 和 [SubagentStart](https://code.claude.com/docs/zh-TW/hooks#subagentstart)：在對話開始，在第一個提示之前
- [UserPromptSubmit](https://code.claude.com/docs/zh-TW/hooks#userpromptsubmit) 和 [UserPromptExpansion](https://code.claude.com/docs/zh-TW/hooks#userpromptexpansion)：與提交的提示一起
- [PreToolUse](https://code.claude.com/docs/zh-TW/hooks#pretooluse)、[PostToolUse](https://code.claude.com/docs/zh-TW/hooks#posttooluse)、[PostToolUseFailure](https://code.claude.com/docs/zh-TW/hooks#posttoolusefailure) 和 [PostToolBatch](https://code.claude.com/docs/zh-TW/hooks#posttoolbatch)：在工具結果旁邊
- [Stop](https://code.claude.com/docs/zh-TW/hooks#stop) 和 [SubagentStop](https://code.claude.com/docs/zh-TW/hooks#subagentstop)：在回合結束。對話繼續，以便 Claude 可以對反饋採取行動。請參閱 [Stop 決定控制](https://code.claude.com/docs/zh-TW/hooks#stop-decision-control)
- [PostModelSwitch](https://code.claude.com/docs/zh-TW/hooks#postmodelswitch)：與切換後的下一個請求一起。請參閱 [PostModelSwitch 決定控制](https://code.claude.com/docs/zh-TW/hooks#postmodelswitch-decision-control) 以了解時機

當多個 hooks 為同一事件返回 `additionalContext` 時，Claude 接收所有值。 如果值超過 10,000 個字元，Claude Code 會將文字寫入工作階段目錄中的檔案，並將檔案路徑與最多前 2,000 個字元的預覽傳遞給 Claude。Claude 可以讀取檔案，但 Claude Code 不要求它。 使用 `additionalContext` 來提供 Claude 應該知道的有關您環境目前狀態或剛剛執行的操作的資訊：

- **環境狀態** ：目前分支、部署目標或活躍的功能旗標
- **條件專案規則** ：哪個測試命令適用於剛編輯的檔案，此 worktree 中哪些目錄是唯讀的
- **外部資料** ：分配給您的開放問題、最近的 CI 結果、從內部服務擷取的內容

對於永遠不會改變的指示，優先使用 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)。它無需執行指令碼即可載入，是靜態專案約定的標準位置。 將文字寫成事實陳述，而不是命令式系統指示。「部署目標是生產」或「此儲存庫使用 `bun test`」之類的措辭讀起來像專案資訊。框架為帶外系統命令的文字可能會觸發 Claude 的提示注入防禦，這會導致 Claude 將文字呈現給您，而不是將其視為上下文。 Claude Code 在工作階段成績單中儲存注入的文字。對於 `PostToolUse` 或 `UserPromptSubmit` 等中期事件，當您使用 `--continue` 或 `--resume` 繼續時，Claude Code 重播儲存的文字，而不是為過去的回合重新執行 hook，因此時間戳或提交 SHA 等值變得陳舊。`SessionStart` hooks 在使用 `source` 設定為 `"resume"` 的 `--resume` 時再次執行，或如果您新增了 `--fork-session` 則為 `"fork"`，因此它們可以刷新其上下文。

#### 決定控制

並非每個事件都支援阻止或通過 JSON 控制行為。支援的事件各自使用不同的欄位集來表達該決定。在編寫 hook 之前，使用此表作為快速參考：

| 事件                                                                                                                                | 決定模式                               | 關鍵欄位                                                                                                                                                                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| UserPromptSubmit、UserPromptExpansion、PostToolUse、PostToolUseFailure、PostToolBatch、Stop、SubagentStop、ConfigChange、PreCompact | 頂層 `decision`                        | `decision: "block"`、`reason`。Stop 和 SubagentStop 也接受 `hookSpecificOutput.additionalContext` 用於 [繼續對話的非錯誤反饋](https://code.claude.com/docs/zh-TW/hooks#stop-decision-control)                                                               |
| TeammateIdle、TaskCompleted                                                                                                         | 退出代碼或 `continue: false`           | 退出代碼 2 使用 stderr 反饋阻止操作。JSON `{"continue": false, "stopReason": "..."}` 也會完全停止隊友，匹配 `Stop` hook 行為；[TaskCompleted 在 `TaskUpdate` 工具觸發事件時忽略它](https://code.claude.com/docs/zh-TW/hooks#taskcompleted-decision-control) |
| TaskCreated                                                                                                                         | 退出代碼或頂層 `decision`              | 退出代碼 2 或 `decision: "block"` [取消任務](https://code.claude.com/docs/zh-TW/hooks#taskcreated-decision-control) 並將訊息返回給 Claude。`continue: false` 被忽略                                                                                         |
| PreToolUse                                                                                                                          | `hookSpecificOutput`                   | `permissionDecision`（allow/deny/ask/defer）、`permissionDecisionReason`                                                                                                                                                                                    |
| PreModelSwitch                                                                                                                      | `hookSpecificOutput` 或頂層 `decision` | `permissionDecision`（allow/deny/ask）、`permissionDecisionReason`。`decision: "block"` 也 [取消切換](https://code.claude.com/docs/zh-TW/hooks#premodelswitch-decision-control)                                                                             |
| PermissionRequest                                                                                                                   | `hookSpecificOutput`                   | `decision.behavior`（allow/deny）                                                                                                                                                                                                                           |
| PermissionDenied                                                                                                                    | `hookSpecificOutput`                   | `retry: true` 告訴模型它可能重試被拒絕的工具呼叫；Claude Code 忽略 [no-verdict denials](https://code.claude.com/docs/zh-TW/hooks#permissiondenied-decision-control) 的 `retry: true`                                                                        |
| WorktreeCreate                                                                                                                      | 路徑返回                               | 命令 hook 在 stdout 上列印路徑；HTTP hook 通過 `hookSpecificOutput.worktreePath` 返回。Hook 失敗或缺少路徑會導致建立失敗                                                                                                                                    |
| WorktreeRemove                                                                                                                      | 退出代碼                               | 任何非零退出代碼會在目錄仍然存在後使移除失敗。JSON 輸出被捨棄                                                                                                                                                                                               |
| Elicitation                                                                                                                         | `hookSpecificOutput`                   | `action`（accept/decline/cancel）、`content`（accept 的表單欄位值）                                                                                                                                                                                         |
| ElicitationResult                                                                                                                   | `hookSpecificOutput`                   | `action`（accept/decline/cancel）、`content`（覆蓋表單欄位值）                                                                                                                                                                                              |
| MessageDisplay                                                                                                                      | `hookSpecificOutput`                   | `displayContent` 替換螢幕上顯示的文字。僅顯示：成績單和 Claude 看到的內容保持原始                                                                                                                                                                           |
| SessionStart、SubagentStart、PostModelSwitch                                                                                        | 僅上下文                               | `hookSpecificOutput.additionalContext` 為 Claude 新增上下文。SessionStart 也接受 [`initialUserMessage`、`watchPaths`、`sessionTitle` 和 `reloadSkills`](https://code.claude.com/docs/zh-TW/hooks#sessionstart-decision-control)。無阻止或決定控制           |
| Setup、Notification、SessionEnd、PostCompact、InstructionsLoaded、StopFailure、CwdChanged、DirectoryAdded、FileChanged              | 無                                     | 無決定控制。用於副作用，如記錄或清理                                                                                                                                                                                                                        |
| 一些事件也可以重寫內容，而不僅僅是允許或阻止它：                                                                                    |                                        |                                                                                                                                                                                                                                                             |

- `PreToolUse`：`updatedInput` 直接在 `hookSpecificOutput` 下替換工具的引數，然後執行。請參閱 [PreToolUse 決定控制](https://code.claude.com/docs/zh-TW/hooks#pretooluse-decision-control) 以取得完整的選項集。
- `PermissionRequest`：`updatedInput` 在 `decision` 物件內。請參閱 [PermissionRequest 決定控制](https://code.claude.com/docs/zh-TW/hooks#permissionrequest-decision-control) 以取得完整的選項集。
- `PostToolUse`：`updatedToolOutput` 替換工具的結果。請參閱 [PostToolUse 決定控制](https://code.claude.com/docs/zh-TW/hooks#posttooluse-decision-control) 以取得完整的選項集。
- `UserPromptSubmit`：無法替換提示；僅在其旁邊注入 `additionalContext`

對於編輯或轉換使用案例，在 `PreToolUse` 攔截出站工具輸入，在 `PostToolUse` 攔截入站工具結果。 以下是每種模式的實際範例：

- 頂層決定
- PreToolUse
- PermissionRequest

`decision` 的唯一值是 `"block"`。要允許操作進行，請從 JSON 中省略 `decision`，或以 0 退出而不帶任何 JSON：

```
{
  "decision": "block",
  "reason": "Test suite must pass before proceeding"
}

```

使用 `hookSpecificOutput` 進行更豐富的控制：允許、拒絕或升級給使用者。您還可以在執行前修改工具輸入或為 Claude 注入額外上下文。有關完整的選項集，請參閱 [PreToolUse 決定控制](https://code.claude.com/docs/zh-TW/hooks#pretooluse-decision-control)。

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Database writes are not allowed"
  }
}

```

使用 `hookSpecificOutput` 代表使用者允許或拒絕權限請求。允許時，您還可以修改工具的輸入或應用權限規則，以便使用者不會再次被提示。有關完整的選項集，請參閱 [PermissionRequest 決定控制](https://code.claude.com/docs/zh-TW/hooks#permissionrequest-decision-control)。

```
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}

```

有關擴展範例，包括 Bash 命令驗證、提示篩選和自動批准指令碼，請參閱指南中的 [您可以自動化的內容](https://code.claude.com/docs/zh-TW/hooks-guide#what-you-can-automate) 和 [Bash 命令驗證器參考實現](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py)。

## Hook 事件

每個事件對應於 Claude Code 生命週期中的一個點，hooks 可以在該點執行。下面的章節按照生命週期排序：從工作階段設定到代理迴圈再到工作階段結束。每個章節描述事件何時觸發、支援的匹配器、接收的 JSON 輸入，以及如何透過輸出控制行為。

### SessionStart

在 Claude Code 啟動新工作階段或恢復現有工作階段時執行。適用於載入開發環境背景資訊，例如現有問題或程式碼庫的最近變更，或設定環境變數。對於不需要指令碼的靜態背景資訊，請改用 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)。 SessionStart 在每個工作階段執行，因此請保持這些 hooks 快速。僅支援 `type: "command"` 和 `type: "mcp_tool"` hooks。請參閱 [MCP tool hook 欄位](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields)，了解 `mcp_tool` hooks 何時執行。 匹配器值對應於工作階段的啟動方式：

| 匹配器                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 何時觸發                                                                                                       |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `startup`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 新工作階段                                                                                                     |
| `resume`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `--resume`、`--continue` 或 `/resume`                                                                          |
| `clear`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | `/clear`                                                                                                       |
| `compact`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 自動或手動壓縮                                                                                                 |
| `fork`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 從現有工作階段分支的新工作階段：`--fork-session` 搭配 `--resume` 或 `--continue`、`/fork` 背景複本或 `/branch` |
| 在 v2.1.214 之前，分支工作階段報告來源為 `"resume"`。 當您啟動互動式工作階段、在啟動時使用 `--continue` 或 `--resume` 恢復對話，或執行 `/clear` 時，SessionStart hooks 在背景執行。您可以立即輸入，恢復的對話會立即出現，無需等待 hooks。Claude 的第一個回應仍會等待 hooks 完成，因此它們的背景資訊會到達 Claude。 當您在工作階段內使用 `/resume` 切換對話時，切換會等待 hooks 完成。如果您在背景 hooks 仍在執行時執行 `/clear` 或切換到另一個對話，它們返回的任何內容都不會套用到工作階段。 相同的等待也適用於啟動，包括恢復的工作階段：您在 SessionStart hooks 仍在執行時發送的提示不會到達 Claude，直到它們完成。 在任一等待期間，按 `Esc` 將提示返回到輸入中而不發送。Hooks 會繼續執行。 |                                                                                                                |

#### SessionStart 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，SessionStart hooks 還會接收 `source` 和可選的 `model`、`agent_type` 和 `session_title`：

| 欄位                                                                                                                                                                                                                                                                                                                         | 描述                                                                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `source`                                                                                                                                                                                                                                                                                                                     | 工作階段如何啟動：新工作階段為 `"startup"`、恢復的工作階段為 `"resume"`、`/clear` 後為 `"clear"`、壓縮後為 `"compact"`，或從現有工作階段分支的新工作階段為 `"fork"` |
| `model`                                                                                                                                                                                                                                                                                                                      | 作用中的模型識別碼。例如在 `/clear` 後或透過對話恢復恢復工作階段時可能會省略，因此在讀取前檢查欄位                                                                  |
| `agent_type`                                                                                                                                                                                                                                                                                                                 | 代理名稱，當您使用 `claude --agent <name>` 啟動 Claude Code 時出現                                                                                                  |
| `session_title`                                                                                                                                                                                                                                                                                                              | 目前工作階段標題（如果已設定），例如透過 `--name` 或 `/rename`。發出 `sessionTitle` 的 hook 可以先檢查 `session_title` 以避免覆寫使用者明確設定的標題               |
| 當 `source` 為 `"resume"` 或 `"fork"` 且文字記錄包含至少一個來自 Claude 的回應時，SessionStart hooks 也會接收下面的四個欄位。您的 hook 可以使用它們在第一個請求之前報告恢復陳舊對話的成本，例如在 [`systemMessage`](https://code.claude.com/docs/zh-TW/hooks#json-output) 中。這些欄位需要 Claude Code v2.1.251 或更新版本。 |                                                                                                                                                                     |
| 欄位                                                                                                                                                                                                                                                                                                                         | 描述                                                                                                                                                                |
| ---                                                                                                                                                                                                                                                                                                                          | ---                                                                                                                                                                 |
| `seconds_since_last_response`                                                                                                                                                                                                                                                                                                | 自恢復文字記錄中最後一個回應以來的掛鐘秒數                                                                                                                          |
| `context_tokens`                                                                                                                                                                                                                                                                                                             | 恢復工作階段的第一個請求作為其提示重新發送的令牌                                                                                                                    |
| `prompt_cache_likely_expired`                                                                                                                                                                                                                                                                                                | 當最後一個回應早於工作階段的 [prompt cache 生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime) 或更新的壓縮替換了快取的對話時為 `true`      |
| `estimated_cache_write_usd`                                                                                                                                                                                                                                                                                                  | 將 `context_tokens` 寫入工作階段模型上的 prompt cache 的估計成本（美元），不包括回應                                                                                |
| 此範例顯示在最後一個回應後 90 分鐘恢復的工作階段的輸入：                                                                                                                                                                                                                                                                     |                                                                                                                                                                     |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SessionStart",
  "source": "resume",
  "model": "claude-opus-5",
  "seconds_since_last_response": 5400,
  "context_tokens": 182340,
  "prompt_cache_likely_expired": true,
  "estimated_cache_write_usd": 1.1396
}

```

#### SessionStart 決策控制

Claude Code 將其 [視為純文字](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 的 stdout 新增到 Claude 的背景資訊。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您還可以返回這些事件特定欄位：

| 欄位                 | 描述                                                                                                                                                                                                                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `additionalContext`  | 在對話開始時、第一個提示之前新增到 Claude 背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude)，了解文字如何傳遞以及要放入其中的內容                                                              |
| `initialUserMessage` | 用作工作階段第一個使用者訊息的字串。適用於 [非互動模式](https://code.claude.com/docs/zh-TW/headless)，搭配 `-p` 旗標，即使未提供提示，它也會成為第一個回合。如果提供了提示，它會作為下一個回合跟隨。與附加到現有回合的 `additionalContext` 不同，這會建立回合 |
| `sessionTitle`       | 設定工作階段標題，效果與 `/rename` 相同。用於根據啟動資料夾、git 分支或 worktree 名稱自動命名工作階段。當 `source` 為 `"startup"`、`"resume"` 或 `"fork"` 時適用；在 `"clear"` 和 `"compact"` 上忽略                                                          |
| `watchPaths`         | 絕對路徑陣列，用於在此工作階段期間監視 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) 事件                                                                                                                                               |
| `reloadSkills`       | 布林值。當為 `true` 時，Claude Code 在 SessionStart hooks 完成後重新掃描 [skill](https://code.claude.com/docs/zh-TW/skills) 和命令目錄，因此 hook 安裝的 skills 在同一工作階段中可用，從第一個提示開始                                                        |

```
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted changes: src/auth.ts, src/login.tsx\nActive issue: #4211 Migrate to OAuth2",
    "sessionTitle": "auth-refactor"
  }
}

```

由於此事件的純文字 stdout 已到達 Claude，只載入背景資訊的 hook 可以直接列印到 stdout，而無需建立 JSON。當您需要將背景資訊與其他欄位（例如 `sessionTitle`）結合時，請使用 JSON 形式。 當 SessionStart hook 安裝或更新 skills 時使用 `reloadSkills`。Skill 探索通常在 SessionStart hooks 完成之前執行，因此 hook 寫入 `~/.claude/skills/` 或 `.claude/skills/` 的檔案否則只會在下一個工作階段中出現。此範例同步共享 skills 儲存庫並請求重新掃描：

```
#!/bin/bash

git -C ~/.claude/skills/team-skills pull --quiet 2>/dev/null || \
  git clone --quiet https://git.example.com/your-org/team-skills.git ~/.claude/skills/team-skills

echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "reloadSkills": true}}'

```

儲存庫 URL 是佔位符；將其替換為您自己的 skills 儲存庫。使用佔位符時，複製會失敗並列印 `fatal:` 訊息到 stderr。來自以 0 退出的 SessionStart hook 的 stderr 僅供參考，因此 `reloadSkills` 請求仍然適用。

#### 保留環境變數

SessionStart hooks 可以存取 `CLAUDE_ENV_FILE` 環境變數，該變數提供一個檔案路徑，您可以在其中保留後續 Bash 命令的環境變數。 若要設定個別環境變數，請將 `export` 陳述式寫入 `CLAUDE_ENV_FILE`。使用附加 (`>>`) 以保留由其他 hooks 設定的變數：

```
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
  echo 'export PATH="$PATH:./node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
fi

exit 0

```

若要捕獲設定命令中的所有環境變更，請比較之前和之後的匯出變數：

```
#!/bin/bash

ENV_BEFORE=$(export -p | sort)

# Run your setup commands that modify the environment
source ~/.nvm/nvm.sh
nvm use 20

if [ -n "$CLAUDE_ENV_FILE" ]; then
  ENV_AFTER=$(export -p | sort)
  comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"
fi

exit 0

```

`CLAUDE_ENV_FILE` 適用於 SessionStart、[Setup](https://code.claude.com/docs/zh-TW/hooks#setup)、[CwdChanged](https://code.claude.com/docs/zh-TW/hooks#cwdchanged) 和 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) hooks。其他 hook 類型無法存取此變數。

### Setup

僅當您使用 `--init-only` 啟動 Claude Code，或在 [非互動模式](https://code.claude.com/docs/zh-TW/headless) 中使用 `--init` 或 `--maintenance` 搭配 `-p` 旗標時觸發。在正常啟動時不觸發。用於一次性相依性安裝或您從 CI 或指令碼明確觸發的排程清理，與正常工作階段啟動分開。對於每個工作階段的初始化，請改用 [SessionStart](https://code.claude.com/docs/zh-TW/hooks#sessionstart)。 匹配器值對應於觸發 hook 的 CLI 旗標：

| 匹配器                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 何時觸發                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `init`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `claude --init-only` 或 `claude -p --init` |
| `maintenance`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `claude -p --maintenance`                  |
| 當您執行 `claude --init-only` 時，Claude Code 執行 Setup hooks 和 `startup` 匹配器的 `SessionStart` hooks，然後退出而不啟動對話。 當您使用 `-p` 啟動或繼續對話時，您還需要提供提示，作為引數或透過 stdin 管道傳輸。當 `SessionStart` hook 提供 [`initialUserMessage`](https://code.claude.com/docs/zh-TW/hooks#sessionstart-decision-control) 或當您使用 [延遲工具呼叫](https://code.claude.com/docs/zh-TW/hooks#defer-a-tool-call-for-later) 恢復工作階段時，您可以跳過提示。 成功時，`--init-only` 不會列印任何內容到終端。若要確認 hooks 已執行，請使用 `claude --debug-file <path> --init-only` 啟動，將 `<path>` 替換為日誌檔案位置，並檢查日誌中的 Setup 和 SessionStart hook 項目。 由於 Setup 不會在每次啟動時觸發，需要安裝相依性的外掛無法僅依賴 Setup。實用的模式是在首次使用時檢查相依性，如果缺少則安裝，例如測試 `${CLAUDE_PLUGIN_DATA}/node_modules` 的 hook 或 skill，如果不存在則執行 `npm install`。請參閱 [持久資料目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)，了解儲存已安裝相依性的位置。如果您透過市場發佈外掛，您可能不需要此模式：Claude Code [在快取外掛時自動安裝符合條件的 Node.js 套件相依性](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)。 |                                            |

#### Setup 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，Setup hooks 還會接收設定為 `"init"` 或 `"maintenance"` 的 `trigger` 欄位：

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Setup",
  "trigger": "init"
}

```

#### Setup 決策控制

Setup hooks 無法阻止；執行在任何退出代碼上繼續。在每個退出代碼上，Claude Code 捨棄 Setup hook 的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output)，例如 `systemMessage`、`continue` 和 `hookSpecificOutput.additionalContext`。使用 `-p` 時，Setup hook 的 stdout、stderr 和退出代碼僅在您使用 `--output-format stream-json --verbose` 啟動時作為 [`hook_response` 事件](https://code.claude.com/docs/zh-TW/headless#read-session-metadata) 出現在執行的輸出中。 Setup hooks 可以存取 `CLAUDE_ENV_FILE`。寫入該檔案的變數會保留到工作階段的後續 Bash 命令中，就像在 [SessionStart hooks](https://code.claude.com/docs/zh-TW/hooks#persist-environment-variables) 中一樣。只有 `type: "command"` hooks 在 `Setup` 上執行。`type: "mcp_tool"` hook 在 `Setup` 上始終被跳過，如 [MCP tool hook 欄位](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields) 下所述。

### InstructionsLoaded

在載入 `CLAUDE.md` 或 `.claude/rules/*.md` 檔案到背景資訊時觸發。此事件在工作階段啟動時對於急切載入的檔案觸發，稍後在檔案被延遲載入時再次觸發，例如當 Claude 存取包含巢狀 `CLAUDE.md` 的子目錄或當具有 `paths:` frontmatter 的條件規則匹配時。Hook 不支援阻止或決策控制。它以非同步方式執行以用於可觀測性目的。 此事件在 Claude [直接透過 **Project instructions** 設定讀取 `AGENTS.md`](https://code.claude.com/docs/zh-TW/memory#agents-md) 時不觸發。當 `CLAUDE.md` 匯入您的 `AGENTS.md` 時它會觸發，其中 `load_reason` 設定為 `include`（如同任何其他匯入的檔案），以及當 `CLAUDE.md` 是它的符號連結時，作為正常 `CLAUDE.md` 載入。 匹配器針對 `load_reason` 執行。例如，使用 `"matcher": "session_start"` 僅對工作階段啟動時載入的檔案觸發，或使用 `"matcher": "path_glob_match|nested_traversal"` 僅對延遲載入觸發。

#### InstructionsLoaded 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，InstructionsLoaded hooks 還會接收這些欄位：

| 欄位                | 描述                                                                                                                                                       |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file_path`         | 已載入的指令檔案的絕對路徑                                                                                                                                 |
| `memory_type`       | 檔案的範圍：`"User"`、`"Project"`、`"Local"` 或 `"Managed"`                                                                                                |
| `load_reason`       | 檔案載入的原因：`"session_start"`、`"nested_traversal"`、`"path_glob_match"`、`"include"` 或 `"compact"`。`"compact"` 值在壓縮事件後重新載入指令檔案時觸發 |
| `globs`             | 檔案 `paths:` frontmatter 中的路徑 glob 模式（如果有）。僅對 `path_glob_match` 載入出現                                                                    |
| `trigger_file_path` | 觸發此載入的檔案的路徑，用於延遲載入                                                                                                                       |
| `parent_file_path`  | 包含此檔案的父指令檔案的路徑，用於 `include` 載入                                                                                                          |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "InstructionsLoaded",
  "file_path": "/Users/my-project/CLAUDE.md",
  "memory_type": "Project",
  "load_reason": "session_start"
}

```

#### InstructionsLoaded 決策控制

InstructionsLoaded hooks 沒有決策控制。它們無法阻止或修改指令載入。Claude Code 捨棄它們的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output)，例如 `systemMessage` 和 `continue`。使用此事件進行稽核日誌、合規性追蹤或可觀測性。

### UserPromptSubmit

在使用者提交提示時執行，在 Claude 處理之前。這允許您根據提示/對話新增額外背景資訊、驗證提示或阻止某些類型的提示。 `UserPromptSubmit` hooks 對 `command`、`http` 和 `mcp_tool` 類型的預設逾時為 30 秒，比大多數其他事件上這些類型的 600 秒預設值更短。因為此 hook 在每個提示之前執行並阻止模型處理直到完成，卡住的 hook 會停滯工作階段。如果您的 hook 需要更多時間，請在 hook 項目中設定 `timeout` 欄位。 除了使用 [`async: true`](https://code.claude.com/docs/zh-TW/hooks#run-hooks-in-the-background) 執行的命令 hook 外，達到其逾時的 `UserPromptSubmit` 命令、HTTP 或 MCP tool hook 會被取消，其輸出（包括任何 `additionalContext`）會被捨棄。提示仍會到達 Claude 而不會有該背景資訊。文字記錄顯示一個通知，命名 hook、觸發的逾時以及輸出已被捨棄。 在 `UserPromptSubmit` 上達到其逾時的 [Agent SDK 回呼 hook](https://code.claude.com/docs/zh-TW/agent-sdk/hooks) 會用命名 hook 和逾時的訊息阻止提示，因為該處的回呼可能充當必須不失敗開放的原則閘道。工作階段繼續。在 v2.1.208 之前，該事件上的回呼逾時以執行錯誤結束回合。

#### UserPromptSubmit 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，UserPromptSubmit hooks 還會接收包含使用者提交的文字的 `prompt` 欄位。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate the factorial of a number"
}

```

#### UserPromptSubmit 決策控制

`UserPromptSubmit` hooks 可以控制是否處理使用者提示並新增背景資訊。所有 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 都可用。 有兩種方式可以在退出代碼 0 上新增背景資訊到對話：

- **純文字 stdout** ：Claude Code 將其 [視為純文字](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 的 stdout 新增到 Claude 的背景資訊
- **JSON 搭配`additionalContext`** ：使用下面的 JSON 格式以獲得更多控制。`additionalContext` 欄位作為背景資訊新增

兩個通道都不會產生可見的文字記錄項目。純文字和 `additionalContext` 值各自作為以 hook 名稱開頭的系統提醒注入；Claude 讀取兩者。若要確認傳遞，請檢查 [偵錯日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)。 若要阻止提示，請返回一個 JSON 物件，其中 `decision` 設定為 `"block"`：

| 欄位                                                                                                    | 描述                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `decision`                                                                                              | `"block"` 防止提示被處理並從背景資訊中清除。省略以允許提示繼續                                                                                 |
| `reason`                                                                                                | 當 `decision` 為 `"block"` 時顯示給使用者。不新增到背景資訊                                                                                    |
| `additionalContext`                                                                                     | 與提交的提示一起新增到 Claude 背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude) |
| `sessionTitle`                                                                                          | 設定工作階段標題。用於根據提示內容自動命名工作階段                                                                                             |
| `suppressOriginalPrompt`                                                                                | 當 `decision` 為 `"block"` 時，如果為 `true`，則從顯示給使用者的阻止訊息中省略原始提示文字                                                     |
| 透過退出 2 阻止的 hook 路由方式與 `reason` 相同：阻止訊息向使用者顯示 stderr 文字，且不新增到背景資訊。 |                                                                                                                                                |

```
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here",
    "sessionTitle": "My session title"
  }
}

```

### UserPromptExpansion

在使用者輸入的命令擴展為到達 Claude 之前的提示時執行。使用此來阻止特定命令的直接呼叫、為特定 skill 注入背景資訊，或記錄使用者呼叫的命令。例如，匹配 `deploy` 的 hook 可以阻止 `/deploy`，除非存在核准檔案，或匹配審查 skill 的 hook 可以將團隊的審查檢查清單附加為 `additionalContext`。 此事件涵蓋 `PreToolUse` 不涵蓋的路徑：匹配 `Skill` 工具的 `PreToolUse` hook 僅在 Claude 呼叫工具時觸發，但直接輸入 `/skillname` 會繞過 `PreToolUse`。`UserPromptExpansion` 在該直接路徑上觸發。 在 `command_name` 上匹配。將匹配器留空以對每個提示類型命令觸發。

#### UserPromptExpansion 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，UserPromptExpansion hooks 還會接收 `expansion_type`、`command_name`、`command_args`、`command_source` 和原始 `prompt` 字串。`expansion_type` 欄位對於 skill 和自訂命令為 `slash_command`，或對於 MCP 伺服器提示為 `mcp_prompt`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../00893aaf.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptExpansion",
  "expansion_type": "slash_command",
  "command_name": "example-skill",
  "command_args": "arg1 arg2",
  "command_source": "plugin",
  "prompt": "/example-skill arg1 arg2"
}

```

#### UserPromptExpansion 決策控制

`UserPromptExpansion` hooks 可以阻止擴展或新增背景資訊。所有 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 都可用。

| 欄位                                                                                | 描述                                                                                                                                           |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `decision`                                                                          | `"block"` 防止命令擴展。省略以允許它繼續                                                                                                       |
| `reason`                                                                            | 當 `decision` 為 `"block"` 時顯示給使用者                                                                                                      |
| `additionalContext`                                                                 | 與擴展的提示一起新增到 Claude 背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude) |
| 透過退出 2 阻止的 hook 路由方式與 `reason` 相同：阻止訊息向使用者顯示 stderr 文字。 |                                                                                                                                                |

```
{
  "decision": "block",
  "reason": "This slash command is not available",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptExpansion",
    "additionalContext": "Additional context for this expansion"
  }
}

```

### MessageDisplay

在助手訊息流向螢幕時執行。Claude Code 分批顯示訊息：每次一批新完成的行準備好呈現時，hook 執行一次，其中包含這些行，Claude Code 呈現 hook 的替換文字代替它們。長訊息會產生多個呼叫；短訊息可能只產生一個。 使用 MessageDisplay 來：

- 為最小顯示去除 markdown
- 轉換 Agent SDK 應用程式向其使用者顯示的文字
- 從 Claude 的回應中編輯 API 金鑰或內部主機名稱

Claude Code 保留每個批次直到您的 hook 返回，因此請保持 hook 快速。如果 hook 失敗或逾時，Claude Code 顯示原始文字。此事件的預設逾時為 10 秒；如果您的 hook 需要更多時間，請在 hook 項目中設定 `timeout` 欄位。 MessageDisplay 僅用於顯示：替換文字僅更改螢幕上呈現的內容。文字記錄和 Claude 看到的內容保持原始文字，因此 Claude 永遠看不到替換，詳細模式顯示原始文字。Hook 僅接收助手訊息文字，因此工具結果和您輸入的文字呈現不變。 MessageDisplay 不支援匹配器，對每個流向文字的助手訊息觸發；沒有文字的訊息（例如僅工具呼叫回應）不觸發它。 在非互動執行中，包括 Agent SDK 查詢和 `claude -p`，MessageDisplay 每個助手訊息執行一次而不是每批行執行一次。單個呼叫在訊息完成後到達並攜帶完整訊息文字：`index` 為 `0`、`final` 為 `true`，`delta` 保留整個訊息。為每個訊息收集 `delta` 文字的 hook 在兩種模式中接收相同的總文字。

#### MessageDisplay 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，MessageDisplay hooks 還會接收回合和訊息的識別碼、此呼叫在訊息中的位置，以及 `delta` 中的新文字。批次邊界取決於文字流的方式，因此使用 `index` 和 `final` 追蹤訊息的進度，而不是期望行以特定方式分組。

| 欄位         | 描述                                                                                                                                                                                                                                                        |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `turn_id`    | 目前回合的 UUID                                                                                                                                                                                                                                             |
| `message_id` | 正在顯示的助手訊息的 UUID。在同一訊息的每個批次中穩定。這不是 API `msg_…` id，因此無法與文字記錄訊息 id 相關聯                                                                                                                                              |
| `index`      | 訊息內此批次的零基索引                                                                                                                                                                                                                                      |
| `final`      | 在訊息的最後一個批次上為 `true`。每個訊息恰好有一個最終批次                                                                                                                                                                                                 |
| `delta`      | 自上一個批次以來新完成的行，包括終止換行符。始終是完整行，除了最終批次可能在行中結束。在互動執行中，當訊息以換行符結束時，最終批次的 delta 為空，因此將 `final` 而不是非空 delta 視為訊息結束信號。在 Agent SDK 和 `claude -p` 執行中，單個呼叫攜帶整個訊息 |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "MessageDisplay",
  "turn_id": "0c9e6a2f-7d41-4f4e-9a15-3f4f7c2b8d10",
  "message_id": "5b2a9c8e-1f63-4d8a-b7c4-9e0d2a6f1c3b",
  "index": 0,
  "final": false,
  "delta": "Here is the plan:\n"
}

```

#### MessageDisplay 輸出

除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，MessageDisplay hooks 可以返回 `displayContent` 以替換螢幕上的 delta：

| 欄位                                                                                                                                                                                                                                                                                                                                                                   | 描述                                      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `displayContent`                                                                                                                                                                                                                                                                                                                                                       | 顯示代替 delta 的文字。省略以顯示原始文字 |
| MessageDisplay hooks 沒有決策控制。它們無法阻止訊息或更改文字記錄中儲存或發送給 Claude 的內容。Claude Code 作用於它們的 JSON 輸出中的 `displayContent` 並捨棄 `systemMessage` 和 `continue`。 此範例從 Claude 的回應中去除 markdown 格式以獲得純文字顯示。指令碼從 stdin 讀取每個批次，從 `delta` 中移除粗體標記和內聯代碼反引號，並將結果作為 `displayContent` 返回。 |                                           |

- macOS/Linux
- Windows (PowerShell)

在您的設定檔中為事件註冊命令 hook：

```
{
  "hooks": {
    "MessageDisplay": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/plain-display.sh",
            "args": []
          }
        ]
      }
    ]
  }
}

```

將此指令碼儲存到您專案中的 `.claude/hooks/plain-display.sh` 並使用 `chmod +x` 使其可執行：

```
#!/bin/bash
jq '{hookSpecificOutput: {hookEventName: "MessageDisplay", displayContent: (.delta | gsub("\\*\\*"; "") | gsub("`"; ""))}}'

```

註冊一個命令 hook，透過 PowerShell 執行指令碼：

```
{
  "hooks": {
    "MessageDisplay": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/plain-display.ps1"
            ]
          }
        ]
      }
    ]
  }
}

```

`-NoProfile` 旗標跳過載入您的 PowerShell 設定檔，以便 hook 快速啟動，`-ExecutionPolicy Bypass` 讓 PowerShell 執行本機指令碼檔案。將此指令碼儲存到您專案中的 `.claude/hooks/plain-display.ps1`：

```
$batch = [Console]::In.ReadToEnd() | ConvertFrom-Json
$text = $batch.delta -replace '\*\*', '' -replace '`', ''
@{
  hookSpecificOutput = @{
    hookEventName = "MessageDisplay"
    displayContent = $text
  }
} | ConvertTo-Json

```

沒有 markdown 的批次通過不變。如果指令碼失敗，例如因為 `jq` 缺失，Claude Code 顯示原始文字並僅在 [偵錯輸出](https://code.claude.com/docs/zh-TW/hooks#debug-hooks) 中記錄失敗，而不是在工作階段中。

### PreToolUse

在 Claude 建立工具參數之後、處理工具呼叫之前執行。在除 `EndConversation` 外的任何工具名稱上匹配：內建工具，例如 `Bash`、`PowerShell`、`Edit`、`Write`、`Read`、`Glob`、`Grep`、`Agent`、`Workflow`、`WebFetch`、`WebSearch`、`AskUserQuestion` 和 `ExitPlanMode`，以及任何 [MCP 工具名稱](https://code.claude.com/docs/zh-TW/hooks#match-mcp-tools)。 若要在磁碟上的特定檔案變更時執行 hook，無論什麼寫入它，請改用 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) 而不是按名稱匹配檔案編輯工具。與 PreToolUse 不同，Claude Code 在變更後執行 FileChanged hooks，它們沒有決策控制，因此無法阻止寫入。 PreToolUse 僅在 Claude 呼叫工具時執行。您在提示中 [使用 `@` 參考的檔案](https://code.claude.com/docs/zh-TW/common-workflows#reference-files-and-directories) 會被新增而不進行任何工具呼叫：Claude Code 在建立提示時插入其內容，因此沒有 PreToolUse hook 對它們觸發，包括匹配 `Read` 的 hooks。若要阻止特定路徑的 `@` 參考，請改用 [`Read` 拒絕規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)。PreToolUse 也不對 [`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior) 觸發。 使用 [PreToolUse 決策控制](https://code.claude.com/docs/zh-TW/hooks#pretooluse-decision-control) 來允許、拒絕、詢問或延遲工具呼叫。 在 `PreToolUse` 上超過其逾時的 [Agent SDK 回呼 hook](https://code.claude.com/docs/zh-TW/agent-sdk/hooks) 會阻止工具呼叫，Claude 接收命名逾時的錯誤結果。另一個 hook 返回的明確拒絕仍然優先。

#### PreToolUse 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，PreToolUse hooks 還會接收 `tool_name`、`tool_input` 和 `tool_use_id`。 對於 [MCP 工具](https://code.claude.com/docs/zh-TW/hooks#match-mcp-tools)，輸入也攜帶 `mcp_server`，一個具有伺服器 `name` 和 `source` 的物件，說明伺服器定義來自何處。`source` 值包括 `plugin`、`sdk` 和設定範圍，例如 `user` 和 `project`。Agent SDK 參考中的 [`McpServerProvenance`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#mcpserverprovenance) 列出它們全部並說明如何對待您不認識的。基於 `source` 而不是 `name` 或 `mcp__<server>__` 工具名稱前綴進行信任決策。`mcp_server` 欄位需要 Claude Code v2.1.274 或更新版本。 對於檔案工具 `Write`、`Edit` 和 `Read`，`tool_input.file_path` 始終是絕對的：

- Claude Code 在 hooks 執行之前擴展 `~` 和相對路徑，因此匹配路徑的 hook 無法透過 `~` 或相同路徑的相對拼寫繞過
- 在 Windows 上，路徑到達時使用反斜線分隔符，即使您的 hook 在 Git Bash 下執行，其中 `$PWD` 看起來像 `/c/project`
- 使用正斜線編寫的比較，例如 `/src/` 檢查，永遠不會匹配反斜線路徑，工具呼叫會如同 hook 沒有要阻止的內容一樣進行
- 在比較前規範化分隔符：Bash 中的 `FILE_PATH="${FILE_PATH//\\//}"`，或 Python 中的 `file_path.replace("\\", "/")`，然後匹配路徑段，例如 `/src/`，而不是使用 `^` 錨定，因為路徑是絕對的

Windows 上的 `Write` 呼叫傳遞：

```
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "C:\\project\\src\\index.ts",
    "content": "..."
  },
  ...
}

```

`tool_input` 欄位取決於工具： 執行 shell 命令。

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 類型                                 | 範例                                                    | 描述                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | string                               | `"npm test"`                                            | 要執行的 shell 命令                                                                                                                   |
| `description`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | string                               | `"Run test suite"`                                      | 命令執行內容的可選描述                                                                                                                |
| `timeout`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | number                               | `120000`                                                | 可選逾時（毫秒）。超過 [最大值](https://code.claude.com/docs/zh-TW/tools-reference#bash-tool-behavior) 的值會減少到最大值而不是被拒絕 |
| `run_in_background`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | boolean                              | `false`                                                 | 是否在背景執行命令                                                                                                                    |
| 當 Bash 命令更改 Git 儲存庫中的檔案時，Claude Code 可以記錄變更的內容。當 [`bashEditDiffEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#basheditdiffenabled) 設定打開記錄時，它在每個權限模式中記錄；該設定的項目說明哪些檔案可以設定它。否則它僅在自動模式和 `bypassPermissions` 模式中記錄，並且僅當 Claude Code 指導 Claude 透過 Bash 編輯檔案時。設定 `bashEditDiffEnabled` 為 `false` 以關閉記錄。背景命令和唯讀命令不攜帶 diff。 您的 [PostToolUse hook](https://code.claude.com/docs/zh-TW/hooks#posttooluse) 然後在 `tool_response.bashEditDiff` 中接收變更的檔案。該清單涵蓋命令執行時在儲存庫下變更的內容。Git 忽略的檔案和子模組中的檔案不被列出。需要 Claude Code v2.1.269 或更新版本。 |                                      |                                                         |                                                                                                                                       |
| 該清單是盡力而為的，處於公開測試版。Claude Code 可能會遺漏變更、包含另一個程序同時變更的檔案，或在其大小限制處停止。欄位形狀可能會變更。使用該清單找到要審查的內容，而不是強制執行原則。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                      |                                                         |                                                                                                                                       |
| `changedFiles` 和 `files` 列出命令變更的內容；其餘欄位說明該清單的完整性和可靠性。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                      |                                                         |                                                                                                                                       |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 類型                                 | 範例                                                    | 描述                                                                                                                                  |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | ---                                  | ---                                                     | ---                                                                                                                                   |
| `changedFiles`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | array                                | `["/path/to/src/app.ts"]`                               | 命令變更的檔案的絕對路徑，最多 200 個。每當 `files` 保留 diff 或 `moreFiles` 高於零時出現                                             |
| `files`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | array                                | `[{"filePath": "/path/to/src/app.ts", "hunks": [...]}]` | 最多 5 個變更檔案的 diffs，用於顯示。對於命令新增或移除的檔案，`created` 或 `deleted` 為 `true`                                       |
| `moreFiles`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | number                               | `2`                                                     | 在 `files` 中沒有 diff 的變更檔案計數                                                                                                 |
| `unavailable`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | boolean                              | `true`                                                  | 當 diff 不完整或無法進行時設定                                                                                                        |
| `skipped`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | boolean                              | `true`                                                  | 對於移動工作樹的 Git 命令設定，例如 `git checkout` 或 `git stash`，因此 Claude Code 不進行 diff                                       |
| `shared`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | boolean                              | `true`                                                  | 當另一個 Bash 工具呼叫（例如子代理的）同時在同一儲存庫中執行時設定，因此某些列出的變更可能是該命令的                                  |
| 執行 PowerShell 命令。請參閱 [PowerShell 工具](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool)，了解按平台的可用性。 欄位與 Bash 工具匹配，命令字串在 `command` 中：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                      |                                                         |                                                                                                                                       |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 類型                                 | 範例                                                    | 描述                                                                                                                                  |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | ---                                  | ---                                                     | ---                                                                                                                                   |
| `command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | string                               | `"Get-ChildItem -Recurse"`                              | 要執行的 PowerShell 命令                                                                                                              |
| `description`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | string                               | `"List files recursively"`                              | 命令執行內容的可選描述                                                                                                                |
| `timeout`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | number                               | `120000`                                                | 可選逾時（毫秒）                                                                                                                      |
| `run_in_background`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | boolean                              | `false`                                                 | 是否在背景執行命令                                                                                                                    |
| 在檢查 shell 命令的 hooks 中匹配 \`Bash                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | PowerShell\`，以便它們涵蓋兩個工具： |                                                         |                                                                                                                                       |

- 在 Windows 上，只要啟用了 PowerShell 工具，Claude 就會將 PowerShell 視為主要 shell 並透過它路由 shell 命令。
- 在沒有 Git Bash 的 Windows 上，工具會自動啟用，Claude Code 根本不會註冊 Bash 工具。
- 僅匹配 `Bash` 的 hook 永遠不會在那裡觸發。

建立或覆寫檔案。

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file_path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | string  | `"/path/to/file.txt"`                                                                                              | 要寫入的檔案的絕對路徑                                                                                                                                        |
| `content`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | string  | `"file content"`                                                                                                   | 要寫入檔案的內容                                                                                                                                              |
| 替換現有檔案中的字串。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `file_path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | string  | `"/path/to/file.txt"`                                                                                              | 要編輯的檔案的絕對路徑                                                                                                                                        |
| `old_string`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | string  | `"original text"`                                                                                                  | 要尋找和替換的文字                                                                                                                                            |
| `new_string`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | string  | `"replacement text"`                                                                                               | 替換文字                                                                                                                                                      |
| `replace_all`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | boolean | `false`                                                                                                            | 是否替換所有出現次數                                                                                                                                          |
| 讀取檔案內容。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `file_path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | string  | `"/path/to/file.txt"`                                                                                              | 要讀取的檔案的絕對路徑                                                                                                                                        |
| `offset`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | number  | `10`                                                                                                               | 可選行號以開始讀取                                                                                                                                            |
| `limit`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | number  | `50`                                                                                                               | 可選要讀取的行數                                                                                                                                              |
| 尋找與 glob 模式匹配的檔案。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `pattern`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | string  | `"**/*.ts"`                                                                                                        | 要匹配檔案的 glob 模式                                                                                                                                        |
| `path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | string  | `"/path/to/dir"`                                                                                                   | 可選要搜尋的目錄。預設為目前工作目錄                                                                                                                          |
| 使用正規表達式搜尋檔案內容。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `pattern`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | string  | `"TODO.*fix"`                                                                                                      | 要搜尋的正規表達式模式                                                                                                                                        |
| `path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | string  | `"/path/to/dir"`                                                                                                   | 可選要搜尋的檔案或目錄                                                                                                                                        |
| `glob`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | string  | `"*.ts"`                                                                                                           | 可選 glob 模式以篩選檔案                                                                                                                                      |
| `output_mode`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | string  | `"content"`                                                                                                        | `"content"`、`"files_with_matches"` 或 `"count"`。預設為 `"files_with_matches"`                                                                               |
| `-i`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | boolean | `true`                                                                                                             | 不區分大小寫搜尋                                                                                                                                              |
| `multiline`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | boolean | `false`                                                                                                            | 啟用多行匹配                                                                                                                                                  |
| 擷取和處理網路內容。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `url`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | string  | `"https://example.com/api"`                                                                                        | 要擷取內容的 URL                                                                                                                                              |
| `prompt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | string  | `"Extract the API endpoints"`                                                                                      | 在擷取的內容上執行的提示                                                                                                                                      |
| 搜尋網路。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `query`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | string  | `"react hooks best practices"`                                                                                     | 搜尋查詢                                                                                                                                                      |
| `allowed_domains`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | array   | `["docs.example.com"]`                                                                                             | 可選：僅包含來自這些網域的結果                                                                                                                                |
| `blocked_domains`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | array   | `["spam.example.com"]`                                                                                             | 可選：排除來自這些網域的結果                                                                                                                                  |
| 生成 [子代理](https://code.claude.com/docs/zh-TW/sub-agents)。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `prompt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | string  | `"Find all API endpoints"`                                                                                         | 代理要執行的任務                                                                                                                                              |
| `description`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | string  | `"Find API endpoints"`                                                                                             | 任務的簡短描述                                                                                                                                                |
| `subagent_type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | string  | `"Explore"`                                                                                                        | 要使用的專門代理類型                                                                                                                                          |
| `model`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | string  | `"sonnet"`                                                                                                         | 可選模型別名以覆寫預設值                                                                                                                                      |
| 當前景 Agent 呼叫完成時，您的 [PostToolUse hook](https://code.claude.com/docs/zh-TW/hooks#posttooluse) 在 `tool_response` 中接收子代理的結果和執行遙測。讀取這些欄位以檢查執行；對於跨子代理的令牌和成本匯總，使用 [令牌和成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#token-counter)，篩選為 `query_source` `"subagent"`，因為 `totalTokens` 和 `usage` 僅涵蓋最終請求：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `status`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | string  | `"completed"`                                                                                                      | 前景子代理為 `"completed"`，背景子代理為 `"async_launched"`。自 v2.1.198 起，子代理預設在背景執行，因此省略的 `run_in_background` 也會產生 `"async_launched"` |
| `agentId`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | string  | `"a4d2c8f1e0b3a297"`                                                                                               | 子代理執行的識別碼                                                                                                                                            |
| `content`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | array   | `[{"type": "text", "text": "Found 12 endpoints..."}]`                                                              | 子代理的最終文字區塊，或對於其報告透過 `SubagentHandback` 的子代理，關於該交接的簡短說明代替                                                                  |
| `resolvedModel`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | string  | `"claude-sonnet-4-5"`                                                                                              | 子代理啟動的模型，可能與請求的模型不同                                                                                                                        |
| `modelsUsed`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | array   | `["claude-sonnet-4-5", "claude-haiku-4-5"]`                                                                        | 按順序使用的模型，連續重複摺疊；僅在模型在執行中交換時設定。需要 Claude Code v2.1.212 或更新版本                                                              |
| `totalTokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | number  | `12450`                                                                                                            | 子代理最終 API 請求的令牌計數：輸入、輸出和快取令牌結合。這不是整個執行的總計                                                                                 |
| `totalDurationMs`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | number  | `48211`                                                                                                            | 子代理執行的掛鐘持續時間                                                                                                                                      |
| `totalToolUseCount`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | number  | `7`                                                                                                                | 子代理進行的工具呼叫計數                                                                                                                                      |
| `usage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | object  | `{"input_tokens": 8320, ...}`                                                                                      | 最終 API 請求的每類型令牌細目：`input_tokens`、`output_tokens`、`cache_creation_input_tokens`、`cache_read_input_tokens`                                      |
| 在 Claude Code v2.1.271 或更新版本上，使用 [`SubagentHandback`](https://code.claude.com/docs/zh-TW/tools-reference) 工具執行的子代理（Claude Code 在 [自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 中提供）透過該工具傳遞其報告，而不是作為文字返回。其 `completed` 結果的 `content` 欄位然後攜帶關於該交接的簡短說明，而不是報告本身。若要讀取報告，請在 `SubagentHandback` 上匹配 `PreToolUse` 或 `PostToolUse` hook 並讀取 `tool_input.message`。 對於背景子代理，工具在任務移到背景時返回，因此 `tool_response` 不攜帶使用欄位：背景啟動立即返回，前景任務在執行中被背景化時返回。它有 `status: "async_launched"`、`agentId`、`description`、`prompt`、`outputFile` 和 `resolvedModel`。 在 `completed` 回應上，`resolvedModel` 命名子代理啟動的模型，可能與 `tool_input` 中的 `model` 值不同，例如當 `availableModels` 或其他覆寫適用時。在 `async_launched` 回應上，`resolvedModel` 命名代理移到背景時使用的模型，因此在背景化之前發生的交換會反映在那裡。`modelsUsed` 和背景化時間 `resolvedModel` 行為需要 Claude Code v2.1.212 或更新版本。 詢問使用者一到四個多選題。 |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `questions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | array   | `[{"question": "Which framework?", "header": "Framework", "options": [{"label": "React"}], "multiSelect": false}]` | 要呈現的問題，每個都有 `question` 字串、簡短 `header`、`options` 陣列和可選 `multiSelect` 旗標                                                                |
| `answers`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | object  | `{"Which framework?": "React"}`                                                                                    | 可選。將問題文字對應到選定的選項標籤。多選答案用逗號連接標籤。Claude 不設定此欄位；透過 `updatedInput` 提供以程式設計方式回答                                 |
| 呈現計畫並要求使用者在 Claude 離開 [計畫模式](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 之前核准。Claude 在呼叫工具之前將計畫寫入磁碟上的檔案，因此模型的字面 `tool_input` 通常是空的。Claude Code 在將輸入傳遞給 hooks 之前注入計畫內容和檔案路徑。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |         |                                                                                                                    |                                                                                                                                                               |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 類型    | 範例                                                                                                               | 描述                                                                                                                                                          |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | ---     | ---                                                                                                                | ---                                                                                                                                                           |
| `plan`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | string  | `"## Refactor auth\n1. Extract..."`                                                                                | Markdown 中的計畫內容。從磁碟上的計畫檔案注入                                                                                                                 |
| `planFilePath`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | string  | `"/Users/.../plans/refactor-auth.md"`                                                                              | 計畫檔案的路徑。注入                                                                                                                                          |
| `allowedPrompts`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | array   | `[{"tool": "Bash", "prompt": "run tests"}]`                                                                        | 已棄用。Claude Code 接受欄位但忽略它。在 v2.1.205 之前，它攜帶 Claude 請求以實施計畫的基於提示的權限                                                          |
| 在 `PostToolUse` 中，`tool_response` 是一個物件，包含 `plan` 和 `filePath` 欄位保留核准的計畫，加上內部狀態旗標。讀取 `tool_response.plan` 以獲取計畫內容，而不是從磁碟重新讀取檔案。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |         |                                                                                                                    |                                                                                                                                                               |

#### PreToolUse 決策控制

`PreToolUse` hooks 可以控制工具呼叫是否進行。與使用頂級 `decision` 欄位的其他 hooks 不同，PreToolUse 在 `hookSpecificOutput` 物件內返回其決策。這提供了更豐富的控制：四個結果（允許、拒絕、詢問或延遲）加上在執行前修改工具輸入的能力。

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `permissionDecision`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `"allow"` 跳過權限提示，除了 [任何模式自動核准的動作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves) 和 `AskUserQuestion` 和 `ExitPlanMode`，需要 [`updatedInput` 與其配對](https://code.claude.com/docs/zh-TW/hooks#allow-with-updatedinput)。`"deny"` 防止工具呼叫。`"ask"` 提示使用者確認。`"defer"` 優雅地退出，以便稍後可以恢復工具。[拒絕和詢問規則](https://code.claude.com/docs/zh-TW/permissions#manage-permissions) 無論 hook 返回什麼都會被評估 |
| `permissionDecisionReason`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 對於 `"allow"` 和 `"ask"`，顯示給使用者但不顯示給 Claude。對於 `"deny"`，顯示給 Claude。對於 `"defer"`，忽略                                                                                                                                                                                                                                                                                                                                                                                   |
| `updatedInput`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 在執行前修改工具的輸入參數。替換整個輸入物件，因此在修改的欄位旁邊包含未變更的欄位。Claude Code 根據您的 hook 返回的輸入評估權限規則和 Bash 命令的 [自動背景資格](https://code.claude.com/docs/zh-TW/tools-reference#background-commands)，而不是 Claude 發送的輸入。與 `"allow"` 結合以自動核准，或與 `"ask"` 結合以向使用者顯示修改的輸入。對於 `"defer"`，忽略                                                                                                                              |
| `additionalContext`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 與工具結果一起新增到 Claude 背景資訊的字串。當 `permissionDecision` 為 `"defer"` 時忽略。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude)                                                                                                                                                                                                                                                                                                      |
| 當多個 PreToolUse hooks 返回不同的決策時，優先順序為 `deny` > `defer` > `ask` > `allow`。 透過退出 2 阻止的 hook 路由方式與 `"deny"` 相同：Claude 看到 stderr 訊息作為拒絕原因。 當 hook 返回 `"ask"` 時，顯示給使用者的權限提示包含一個標籤，識別 hook 來自何處：`[settings]` 對於來自任何設定檔或代理 frontmatter 的 hook，`[plugin:<name>]` 對於外掛的 hook，或 `[skill]` 對於來自 skill frontmatter 的 hook。這幫助使用者理解哪個設定來源要求確認。 Hook 的 `"ask"` 也在 [自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 中強制權限提示：分類器仍然可以拒絕工具呼叫，但無法無聲地核准呼叫。在 v2.1.211 之前，分類器可以核准在 [沙箱](https://code.claude.com/docs/zh-TW/sandboxing) 外執行的 Bash 命令而不顯示 hook 請求的提示；分類器仍然對該命令應用了自己的安全規則，hook `"deny"` 始終被尊重。 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "My reason here",
    "updatedInput": {
      "field_to_modify": "new value"
    },
    "additionalContext": "Current environment: production. Proceed with caution."
  }
}

```

在 [非互動模式](https://code.claude.com/docs/zh-TW/headless) 中使用 `-p` 旗標，Claude Code 僅在執行有 [權限主機](https://code.claude.com/docs/zh-TW/headless#turn-off-permission-prompts-in-unattended-runs) 以接收提示時提供 `AskUserQuestion` 和 `ExitPlanMode`，例如 Agent SDK `canUseTool` 回呼。這些工具需要使用者互動。返回 `permissionDecision: "allow"` 與 `updatedInput` 一起滿足該要求：hook 從 stdin 讀取工具的輸入，透過您自己的 UI 收集答案，並在 `updatedInput` 中返回它，以便工具執行而不提示。單獨返回 `"allow"` 對這些工具不足夠。對於 `AskUserQuestion`，回顯原始 `questions` 陣列並新增一個 [`answers`](https://code.claude.com/docs/zh-TW/hooks#askuserquestion) 物件，將每個問題的文字對應到選定的答案。 自 v2.1.199 起，其伺服器使用 [`_meta["anthropic/requiresUserInteraction"]`](https://code.claude.com/docs/zh-TW/mcp#require-approval-for-a-specific-tool) 標記的 MCP 工具更嚴格：hook 無法使用 `"allow"` 跳過其核准提示，無論是否有 `updatedInput`，因為 Claude Code 無法確認 hook 收集了工具需要的互動。 PreToolUse 之前使用頂級 `decision` 和 `reason` 欄位，但這些對此事件已棄用。改用 `hookSpecificOutput.permissionDecision` 和 `hookSpecificOutput.permissionDecisionReason`。已棄用的值 `"approve"` 和 `"block"` 對應到 `"allow"` 和 `"deny"`。PostToolUse 和 Stop 等其他事件繼續使用頂級 `decision` 和 `reason` 作為其目前格式。

#### 延遲工具呼叫以供稍後使用

`"defer"` 適用於執行 `claude -p` 作為子程序並讀取其 JSON 輸出的整合，例如 Agent SDK 應用程式或建立在 Claude Code 之上的自訂 UI。它讓該呼叫程序在工具呼叫處暫停 Claude，透過其自己的介面收集輸入，並在中斷處恢復。Claude Code 僅在 [非互動模式](https://code.claude.com/docs/zh-TW/headless) 中使用 `-p` 旗標時尊重此值。在互動式工作階段中，它記錄警告並忽略 hook 結果。 `AskUserQuestion` 工具是典型情況：Claude 想詢問使用者某事，但沒有終端來回答。`-p` 執行僅在有 [權限主機](https://code.claude.com/docs/zh-TW/headless#turn-off-permission-prompts-in-unattended-runs) 時提供 `AskUserQuestion`，例如您使用 `--permission-prompt-tool` 傳遞的 MCP 工具，因此使用一個啟動執行。往返工作如下：

1. Claude 呼叫 `AskUserQuestion`。`PreToolUse` hook 觸發。
1. Hook 返回 `permissionDecision: "defer"`。工具不執行。程序以 `stop_reason: "tool_deferred"` 退出，待處理工具呼叫保留在文字記錄中。
1. 呼叫程序從 SDK 結果讀取 `deferred_tool_use`，在其自己的 UI 中呈現問題，並等待答案。
1. 呼叫程序執行 `claude -p --resume <session-id>`，使用相同的權限主機。相同的工具呼叫再次觸發 `PreToolUse`。
1. Hook 返回 `permissionDecision: "allow"`，答案在 `updatedInput` 中。工具執行，Claude 繼續。

`deferred_tool_use` 欄位攜帶工具的 `id`、`name` 和 `input`。`input` 是 Claude 為工具呼叫生成的參數，在執行前捕獲：

```
{
  "type": "result",
  "subtype": "success",
  "stop_reason": "tool_deferred",
  "session_id": "abc123",
  "deferred_tool_use": {
    "id": "toolu_01abc",
    "name": "AskUserQuestion",
    "input": { "questions": [{ "question": "Which framework?", "header": "Framework", "options": [{"label": "React"}, {"label": "Vue"}], "multiSelect": false }] }
  }
}

```

沒有逾時或重試限制。工作階段保留在磁碟上直到您恢復它，受 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 保留掃描約束，預設情況下在 30 天後刪除工作階段檔案，遵循 [保留掃描規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)。如果恢復時答案還未準備好，hook 可以再次返回 `"defer"`，程序以相同方式退出。呼叫程序透過最終從 hook 返回 `"allow"` 或 `"deny"` 來控制何時打破迴圈。 `"defer"` 僅在 Claude 在回合中進行單個工具呼叫時有效。如果 Claude 同時進行多個工具呼叫，`"defer"` 會被忽略並帶有警告，工具透過正常權限流程進行。約束存在是因為恢復只能重新執行一個工具：沒有辦法延遲批次中的一個呼叫而不留下其他未解決。 如果恢復時延遲的工具不再可用，程序以 `stop_reason: "tool_deferred_unavailable"` 和 `is_error: true` 退出，在 hook 觸發之前。這發生在為恢復的工作階段未連接提供工具的 MCP 伺服器時。`deferred_tool_use` 有效負載仍然包含，以便您可以識別哪個工具遺失。 若要在計畫模式中恢復延遲工作階段，請在 `--resume` 時傳遞 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)，以便 Claude Code 可以呈現計畫以供核准。沒有它，Claude Code 不會恢復計畫模式。需要 Claude Code v2.1.246 或更新版本。當您使用 `-p` 恢復時，Claude Code 不會恢復任何其他儲存的權限模式。它在新 `claude -p` 執行會啟動的權限模式中啟動執行，因此如果延遲工作階段使用了一個，請再次傳遞 `--permission-mode` 或 `--dangerously-skip-permissions`。當您使用 `claude --resume <session-id>` 恢復而不使用 `-p` 時，Claude Code 會恢復儲存的權限模式，但 [恢復時的權限模式](https://code.claude.com/docs/zh-TW/sessions#permission-mode-on-resume) 中列出的例外除外。

### PermissionRequest

在 Claude Code 即將要求您許可使用工具時執行。在無法顯示提示的工作階段中，例如 [非互動模式](https://code.claude.com/docs/zh-TW/headless) 中的背景子代理，Claude Code 仍然執行這些 hooks，如果沒有 hook 返回決策，它會拒絕工具呼叫。 使用 [PermissionRequest 決策控制](https://code.claude.com/docs/zh-TW/hooks#permissionrequest-decision-control) 代表使用者允許或拒絕。 當您需要 Claude 要求許可使用工具時的信號時使用此事件。Claude Code 僅在提示等待約六秒後才執行 [Notification](https://code.claude.com/docs/zh-TW/hooks#notification) hook，其中 `permission_prompt` 類型。 Claude Code 不為沙箱命令的 [網路請求](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation) 執行 PermissionRequest hooks。若要獲得該提示的信號，請使用 `permission_prompt` 通知類型。 在工具名稱上匹配，與 PreToolUse 相同的值。

#### PermissionRequest 輸入

PermissionRequest hooks 接收 `tool_name` 和 `tool_input` 欄位，如 PreToolUse hooks，但沒有 `tool_use_id`。對於 MCP 工具，它們也接收 [`mcp_server`](https://code.claude.com/docs/zh-TW/hooks#pretooluse-input) 物件。可選 `permission_suggestions` 陣列包含 Claude Code 為此請求建議的 [權限更新](https://code.claude.com/docs/zh-TW/hooks#permission-update-entries)，例如新增允許規則或更改權限模式。 `permission_suggestions` 陣列不是您看到的選項的確切清單，因為每個權限對話建立自己的選項。某些對話（例如檔案編輯的對話）根本不讀取陣列，並從請求本身衍生其選項。讀取它的對話仍然可以保留一個選項，其建議保留在陣列中，例如當 [`allowManagedPermissionRulesOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedpermissionrulesonly) 隱藏規則保存選項時。它也可以提供陣列中沒有建議項目的選項，例如 [**是的，並切換到自動模式**](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)，它直接更改權限模式而不是透過權限更新。 PreToolUse hooks 在每個工具呼叫之前執行，無論是否需要權限。PermissionRequest hooks 僅在 Claude Code 即將要求您許可時執行，或當它會以其他方式自動拒絕無法提示的呼叫時執行。兩個事件都不對 [`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior) 觸發。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf node_modules",
    "description": "Remove node_modules directory"
  },
  "permission_suggestions": [
    {
      "type": "addRules",
      "rules": [{ "toolName": "Bash", "ruleContent": "rm -rf node_modules" }],
      "behavior": "allow",
      "destination": "localSettings"
    }
  ]
}

```

#### PermissionRequest 決策控制

`PermissionRequest` hooks 可以允許或拒絕權限請求。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您的 hook 指令碼可以返回具有這些事件特定欄位的 `decision` 物件：

| 欄位                                                                                                              | 描述                                                                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `behavior`                                                                                                        | `"allow"` 授予權限，`"deny"` 拒絕。[拒絕和詢問規則](https://code.claude.com/docs/zh-TW/permissions#manage-permissions) 仍然被評估，因此返回 `"allow"` 的 hook 不會覆寫匹配的拒絕規則 |
| `updatedInput`                                                                                                    | 僅對 `"allow"`：在執行前修改工具的輸入參數。替換整個輸入物件，因此在修改的欄位旁邊包含未變更的欄位。修改的輸入會針對拒絕和詢問規則重新評估                                           |
| `updatedPermissions`                                                                                              | 僅對 `"allow"`：[權限更新項目](https://code.claude.com/docs/zh-TW/hooks#permission-update-entries) 陣列以應用，例如新增允許規則或更改工作階段權限模式                                |
| `message`                                                                                                         | 僅對 `"deny"`：告訴 Claude 為什麼權限被拒絕                                                                                                                                          |
| `interrupt`                                                                                                       | 僅對 `"deny"`：如果為 `true`，停止 Claude                                                                                                                                            |
| 退出 2 而不帶 `decision` 物件的 hook 保持權限流程不變，其 stderr 被捨棄。只有 `decision` 物件可以授予或拒絕請求。 |                                                                                                                                                                                      |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}

```

#### 權限更新項目

`updatedPermissions` 輸出欄位和 [`permission_suggestions` 輸入欄位](https://code.claude.com/docs/zh-TW/hooks#permissionrequest-input) 都使用相同的項目物件陣列。每個項目都有一個 `type` 決定其他欄位，以及一個 `destination` 控制變更寫入位置。

| `type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 欄位                               | 效果                                                                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `addRules`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | `rules`、`behavior`、`destination` | 新增權限規則。`rules` 是 `{toolName, ruleContent?}` 物件的陣列。省略 `ruleContent` 以匹配整個工具。`behavior` 為 `"allow"`、`"deny"` 或 `"ask"`                                        |
| `replaceRules`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `rules`、`behavior`、`destination` | 將給定 `behavior` 在 `destination` 的所有規則替換為提供的 `rules`                                                                                                                      |
| `removeRules`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `rules`、`behavior`、`destination` | 移除給定 `behavior` 的匹配規則                                                                                                                                                         |
| `setMode`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `mode`、`destination`              | 更改權限模式。有效模式為 `default`、`auto`、`acceptEdits`、`dontAsk`、`bypassPermissions`、`plan` 和 `manual` 作為 `default` 的別名。`manual` 別名需要 Claude Code v2.1.200 或更新版本 |
| `addDirectories`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | `directories`、`destination`       | 新增工作目錄。`directories` 是路徑字串的陣列                                                                                                                                           |
| `removeDirectories`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | `directories`、`destination`       | 移除工作目錄                                                                                                                                                                           |
| `setMode` 搭配 `bypassPermissions` 僅在您已啟動工作階段時生效，且繞過模式已可用：`--dangerously-skip-permissions`、`--permission-mode bypassPermissions`、`--allow-dangerously-skip-permissions` 或 [使用者、`--settings` 或受管設定](https://code.claude.com/docs/zh-TW/settings-reference#permissions-defaultmode) 中的 `permissions.defaultMode: "bypassPermissions"`。否則更新是無操作。當 [`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/zh-TW/permissions#managed-settings) 禁用模式或工作階段在 [受限模式](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 中啟動時，更新也是無操作。`bypassPermissions` 無論 `destination` 如何都永遠不會作為 `defaultMode` 保留。 |                                    |                                                                                                                                                                                        |
| 每個項目上的 `destination` 欄位決定變更是保留在記憶體中還是保留到設定檔。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                                    |                                                                                                                                                                                        |
| `destination`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 寫入                               |                                                                                                                                                                                        |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | ---                                |                                                                                                                                                                                        |
| `session`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 僅在記憶體中，工作階段結束時捨棄   |                                                                                                                                                                                        |
| `localSettings`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `.claude/settings.local.json`      |                                                                                                                                                                                        |
| `projectSettings`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `.claude/settings.json`            |                                                                                                                                                                                        |
| `userSettings`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `~/.claude/settings.json`          |                                                                                                                                                                                        |
| Hook 可以回顯它接收的 `permission_suggestions` 之一作為其自己的 `updatedPermissions` 輸出。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                    |                                                                                                                                                                                        |

### PostToolUse

在工具成功完成後立即執行。 在工具名稱上匹配，與 PreToolUse 相同的值。 當工具名稱不是正確的篩選器時更廣泛地匹配：

- 若要在任何工具成功完成後執行 hook，省略 `matcher` 或將其設定為 `"*"`。您的 hook 然後可以自己探索變更的內容，例如執行 `git status --porcelain`，它也列出 `git diff` 遺漏的未追蹤檔案。對於失敗的工具呼叫，在 [PostToolUseFailure](https://code.claude.com/docs/zh-TW/hooks#posttoolusefailure) 下新增相同的 hook。
- 若要在特定檔案變更時執行 hook，無論什麼寫入它，請使用 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged)。當 `Bash` 命令或 Claude Code 外的程序重寫相同檔案時，Claude Code 不執行匹配 `Edit|Write` 的 `PostToolUse` hook。

#### PostToolUse 輸入

`PostToolUse` hooks 在工具已成功執行後觸發。輸入包括 `tool_input`（發送給工具的引數）和 `tool_response`（它返回的結果）。兩者的確切架構取決於工具。檔案工具 `tool_input` 路徑以與 [PreToolUse](https://code.claude.com/docs/zh-TW/hooks#pretooluse-input) 相同的格式到達：始終絕對，使用平台的原生分隔符，因此 Windows 上為反斜線。對於 MCP 工具，輸入也攜帶 [`mcp_server`](https://code.claude.com/docs/zh-TW/hooks#pretooluse-input) 物件。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "type": "create"
  },
  "tool_use_id": "toolu_01ABC123...",
  "duration_ms": 12
}

```

| 欄位          | 描述                                                                       |
| ------------- | -------------------------------------------------------------------------- |
| `duration_ms` | 可選。工具執行時間（毫秒）。不包括權限提示和 PreToolUse hooks 中花費的時間 |

#### PostToolUse 決策控制

`PostToolUse` hooks 可以在工具執行後提供回饋給 Claude。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您的 hook 指令碼可以返回這些事件特定欄位：

| 欄位                                                                 | 描述                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `decision`                                                           | `"block"` 在工具結果旁邊新增 `reason`。Claude 仍然看到原始輸出；若要替換它，請使用 `updatedToolOutput`                                                                                                                                                                                                                |
| `reason`                                                             | 當 `decision` 為 `"block"` 時顯示給 Claude 的解釋                                                                                                                                                                                                                                                                     |
| `additionalContext`                                                  | 與工具結果一起新增到 Claude 背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude)                                                                                                                                                                          |
| `classifierContext`                                                  | 關於此呼叫結果的簡短說明，用於 [自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 分類器而不是 Claude。請參閱 [為自動模式分類器註釋結果](https://code.claude.com/docs/zh-TW/hooks#annotate-a-result-for-the-auto-mode-classifier)。需要 Claude Code v2.1.236 或更新版本 |
| `updatedToolOutput`                                                  | 在發送給 Claude 之前用提供的值替換工具的輸出。該值必須符合工具的輸出形狀                                                                                                                                                                                                                                              |
| `updatedMCPToolOutput`                                               | 僅替換 [MCP 工具](https://code.claude.com/docs/zh-TW/hooks#match-mcp-tools) 的輸出。優先使用 `updatedToolOutput`，它適用於所有工具                                                                                                                                                                                    |
| 下面的範例替換 `Bash` 呼叫的輸出。替換值符合 `Bash` 工具的輸出形狀： |                                                                                                                                                                                                                                                                                                                       |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude",
    "updatedToolOutput": {
      "stdout": "[redacted]",
      "stderr": "",
      "interrupted": false,
      "isImage": false
    }
  }
}

```

`updatedToolOutput` 僅更改 Claude 看到的內容。工具已在 hook 觸發時執行，因此任何寫入的檔案、執行的命令或發送的網路請求已生效。遙測（例如 OpenTelemetry 工具跨度和分析事件）也會在 hook 執行前捕獲原始輸出。若要在執行前防止或修改工具呼叫，請改用 [PreToolUse](https://code.claude.com/docs/zh-TW/hooks#pretooluse) hook。替換值必須符合工具的輸出形狀。內建工具返回結構化物件而不是純字串。例如，`Bash` 返回具有 `stdout`、`stderr`、`interrupted` 和 `isImage` 欄位的物件。對於內建工具，不符合工具輸出架構的值會被忽略，使用原始輸出。MCP 工具輸出通過而不進行架構驗證。去除 Claude 需要的錯誤詳細資訊可能導致它在錯誤假設上進行。

#### 為自動模式分類器註釋結果

返回 `classifierContext` 以向 [自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 分類器發送關於工具呼叫結果的簡短說明，而不是向 Claude。分類器 [永遠不會接收工具結果本身](https://code.claude.com/docs/zh-TW/permission-modes#how-the-classifier-evaluates-actions)，因此此欄位是支援的方式，在它審查稍後的動作之前告訴它工具呼叫返回的內容。該欄位需要 Claude Code v2.1.236 或更新版本。 下面的範例告訴分類器查詢的輸出來自何處：

```
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "classifierContext": "This query ran against the staging database, not production."
  }
}

```

分類器給予說明的權重取決於您設定 hook 的位置：

- **在 Claude Code 中設定的 Hooks** ：對於來自設定檔、外掛、skills 和代理 frontmatter 的 hooks，分類器將說明視為未驗證的應用程式提供的背景資訊。說明永遠不會建立使用者意圖，如果它聲稱您核准或請求了某事，分類器會根據您在對話中的自己訊息檢查該聲明
- **進程內 Agent SDK 回呼** ：當應用程式嵌入 Claude Code 將 hook 註冊為 [TypeScript SDK 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/hooks) 並在即時工作階段期間返回說明時，分類器可能會將使用者陳述（在說明中轉達）視為使用者意圖。這樣的陳述可以滿足分類器會接受來自您發送的訊息的同意要求，但它永遠不會解除您自己的訊息也無法解除的阻止。工作階段恢復後，Claude Code 將恢復的說明視為未驗證的背景資訊。當兩個群組的 hooks 註釋相同呼叫時，分類器將組合說明視為未驗證

Claude Code 在傳遞說明時應用這些限制：

- **長度** ：Claude Code 將一個工具呼叫的說明上限設定為 2,000 個字元，並截斷其餘部分。上限在回應該呼叫的每個 hook 中共享
- **僅同步回應** ：Claude Code 忽略 [在背景執行](https://code.claude.com/docs/zh-TW/hooks#run-hooks-in-the-background) 的 hook 回應中的欄位，因為該回應在 Claude Code 記錄工具結果後到達
- **分類器不記錄的呼叫** ：分類器的文字記錄省略唯讀查詢，例如檔案讀取和搜尋。Claude Code 捨棄附加到其中一個呼叫的說明
- **與重寫的互動** ：當說明描述您使用 `updatedToolOutput` 替換的輸出時，在相同的 hook 回應中返回兩個欄位。如果該重寫被拒絕或另一個 hook 的重寫替換它，Claude Code 會捨棄說明。Claude Code 傳遞您返回的說明而不進行重寫，即使另一個 hook 重寫輸出

分類器將您放在 `classifierContext` 中的內容讀取為來自託管工作階段的應用程式的資訊，因此不要將不受信任的工具輸出或第三方文字複製到其中。將說明保持為關於此一個呼叫的簡短聲明，例如關於其來源的事實或使用者關於它的陳述；不要使用欄位傳遞不相關的訊息或事件流。

### PostToolUseFailure

在啟動執行的工具失敗時執行：工具拋出錯誤，或 MCP 工具返回錯誤結果。使用此來記錄失敗、發送警報或向 Claude 提供更正回饋。 在工具名稱上匹配，與 PreToolUse 相同的值。 此事件不對執行前被拒絕的工具呼叫觸發：未知工具名稱、失敗架構或工具特定驗證的輸入，或權限拒絕。驗證拒絕作為 `tool_use_error` 結果返回，在 hooks 執行前發生，因此它們既不觸發 `PreToolUse` 也不觸發此事件。權限拒絕觸發 `PreToolUse` 但不觸發此事件；請參閱 [PermissionDenied](https://code.claude.com/docs/zh-TW/hooks#permissiondenied)。

#### PostToolUseFailure 輸入

PostToolUseFailure hooks 接收與 PostToolUse 相同的 `tool_name` 和 `tool_input` 欄位，以及作為頂級欄位的錯誤資訊。對於 MCP 工具，它們也接收 [`mcp_server`](https://code.claude.com/docs/zh-TW/hooks#pretooluse-input) 物件。例如，失敗的 `npm test` 命令可能傳遞：

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run test suite"
  },
  "tool_use_id": "toolu_01ABC123...",
  "error": "Exit code 1\nError: Cannot find module 'express'",
  "is_interrupt": false,
  "duration_ms": 4187
}

```

| 欄位                                                                                                                                                                                                    | 描述                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `error`                                                                                                                                                                                                 | 描述出錯內容的字串。格式取決於失敗的工具                                                                                      |
| `is_interrupt`                                                                                                                                                                                          | 可選布林值。當失敗作為中止而不是工具報告的錯誤到達 Claude Code 時為 True。取消執行中的工具不觸發此 hook；工具結果攜帶中斷訊息 |
| `duration_ms`                                                                                                                                                                                           | 可選。工具執行時間（毫秒）。不包括權限提示和 PreToolUse hooks 中花費的時間                                                    |
| `error` 字串通常是 Claude 作為失敗工具結果接收的相同文字。其格式因工具和失敗而異。根據 `tool_name`、`is_interrupt` 和第一行 `Exit code N` 鍵入您的 hook；將字串的其餘部分視為顯示文字，而不是穩定格式。 |                                                                                                                               |

- 對於 Bash 和 PowerShell，執行並退出的命令產生第一行 `Exit code N`，然後是命令產生的任何輸出作為一個區塊，其中 stdout 和 stderr 交錯
- 有效負載也可能攜帶裸失敗訊息，沒有退出代碼行，當 Claude Code 無法啟動 shell 程序本身時
- Claude Code 在 `... [N characters truncated] ...` 標記周圍中間截斷長字串，並可以插入自己的行，例如 `Command timed out after 2m 0s`

#### PostToolUseFailure 決策控制

`PostToolUseFailure` hooks 可以在工具失敗後向 Claude 提供背景資訊。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您的 hook 指令碼可以返回這些事件特定欄位：

| 欄位                | 描述                                                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `additionalContext` | 與錯誤一起新增到 Claude 背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude) |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUseFailure",
    "additionalContext": "Additional information about the failure for Claude"
  }
}

```

### PostToolBatch

在批次中的每個工具呼叫都已解決後執行一次，在 Claude Code 發送下一個請求給模型之前。`PostToolUse` 每個工具執行一次，這意味著當 Claude 進行平行工具呼叫時它並發執行。`PostToolBatch` 恰好執行一次，包含完整批次，因此它是注入取決於執行的工具集而不是任何單個工具的背景資訊的正確位置。此事件沒有匹配器。

#### PostToolBatch 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，PostToolBatch hooks 還會接收 `tool_calls`，一個描述批次中每個工具呼叫的陣列：

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolBatch",
  "tool_calls": [
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "/.../ledger/accounts.py"},
      "tool_use_id": "toolu_01...",
      "tool_response": "     1\tfrom __future__ import annotations\n     2\t..."
    },
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "/.../ledger/transactions.py"},
      "tool_use_id": "toolu_02...",
      "tool_response": "     1\tfrom __future__ import annotations\n     2\t..."
    }
  ]
}

```

`tool_response` 包含模型在對應 `tool_result` 區塊中接收的相同內容。該值是序列化字串或內容區塊陣列，完全如工具發出的一樣。對於 `Read`，這意味著行號前綴文字而不是原始檔案內容。回應可能很大，因此僅解析您需要的欄位。 `tool_response` 形狀與 `PostToolUse` 的不同。`PostToolUse` 傳遞工具的結構化 `Output` 物件，例如 `Write` 的 `{filePath: "...", type: "create"}`；`PostToolBatch` 傳遞模型看到的序列化 `tool_result` 內容。

#### PostToolBatch 決策控制

`PostToolBatch` hooks 可以為 Claude 注入背景資訊。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您的 hook 指令碼可以返回這些事件特定欄位：

| 欄位                | 描述                                                                                                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `additionalContext` | 在下一個模型呼叫之前注入一次的背景資訊字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude)，了解傳遞詳細資訊、要放入其中的內容以及恢復的工作階段如何處理過去的值 |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolBatch",
    "additionalContext": "These files are part of the ledger module. Run pytest before marking the task complete."
  }
}

```

返回 `decision: "block"` 或 `continue: false` 在下一個模型呼叫之前停止代理迴圈。阻止訊息來自 JSON `reason` 或 `stopReason`，或來自退出 2 時的 stderr。您在文字記錄中看到它作為警告，它保留在對話中，因此 Claude 在對話繼續時看到它。

### PermissionDenied

在 [自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 拒絕工具呼叫時執行，包括當它拒絕而沒有分類器判決時，因為 [與自動模式分開的安全檢查拒絕了分類器自己的請求](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action) 或其回應未解析。此 hook 僅在自動模式中觸發：當您手動拒絕權限對話、`PreToolUse` hook 阻止呼叫或 `deny` 規則匹配時不執行。使用它來記錄拒絕、調整設定或告訴模型它可能重試工具呼叫。 在工具名稱上匹配，與 PreToolUse 相同的值。

#### PermissionDenied 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，PermissionDenied hooks 還會接收 `tool_name`、`tool_input`、`tool_use_id` 和 `reason`。對於 MCP 工具，它們也接收 [`mcp_server`](https://code.claude.com/docs/zh-TW/hooks#pretooluse-input) 物件。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "auto",
  "hook_event_name": "PermissionDenied",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/build",
    "description": "Clean build directory"
  },
  "tool_use_id": "toolu_01ABC123...",
  "reason": "[Irreversible Local Destruction]"
}

```

| 欄位     | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reason` | 拒絕原因。對於分類器判決，在大多數工作階段中它命名方括號中的匹配規則，例如 `[Data Exfiltration]`；請參閱 [審查拒絕](https://code.claude.com/docs/zh-TW/auto-mode-config#review-denials) 以了解其他形式。對於 [無判決拒絕](https://code.claude.com/docs/zh-TW/hooks#permissiondenied-decision-control)，它以 `Auto mode could not evaluate this action and is blocking it for safety` 開頭。對於因分類器模型不可用而拒絕，它是固定文字 `Classifier unavailable` |

#### PermissionDenied 決策控制

PermissionDenied hooks 可以告訴模型它可能重試被拒絕的工具呼叫。返回一個 JSON 物件，其中 `hookSpecificOutput.retry` 設定為 `true`：

```
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionDenied",
    "retry": true
  }
}

```

當 `retry` 為 `true` 時，Claude Code 向對話新增一條訊息，告訴模型它可能重試工具呼叫。Claude Code 不反轉拒絕本身。如果您的 hook 不返回 JSON 或返回 `retry: false`，拒絕成立，模型接收原始拒絕訊息。 當分類器對動作 [沒有判決](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action) 時，Claude Code 忽略 `retry: true`：其回應未解析，或與自動模式分開的安全檢查拒絕了分類器自己的請求。對於這些拒絕，Claude Code 已經在拒絕訊息中告訴模型是否稍後重試或繼續。

### Notification

在 Claude Code 發送通知時執行。在通知類型上匹配。省略匹配器以對所有通知類型執行 hooks。 即使桌面通知已關閉，您也會接收這些 hook 事件：`preferredNotifChannel` 設定（包括 `notifications_disabled`）僅更改您如何被警報，而不是您的 hook 是否執行。

| 匹配器                                                                                                                                                                                                                                                                                                                                                                                              | 何時觸發                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `permission_prompt`                                                                                                                                                                                                                                                                                                                                                                                 | Claude 需要您核准工具使用或沙箱命令的 [網路請求](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)，提示已等待約六秒                                                                                                                                                                                                                |
| `idle_prompt`                                                                                                                                                                                                                                                                                                                                                                                       | Claude 約 60 秒前完成回應，您自那以後未輸入                                                                                                                                                                                                                                                                                                        |
| `auth_success`                                                                                                                                                                                                                                                                                                                                                                                      | 驗證完成                                                                                                                                                                                                                                                                                                                                           |
| `elicitation_dialog`                                                                                                                                                                                                                                                                                                                                                                                | MCP 伺服器開啟引出表單，您約六秒未輸入                                                                                                                                                                                                                                                                                                             |
| `elicitation_url_dialog`                                                                                                                                                                                                                                                                                                                                                                            | MCP 伺服器要求您開啟瀏覽器 URL，您約六秒未輸入                                                                                                                                                                                                                                                                                                     |
| `elicitation_complete`                                                                                                                                                                                                                                                                                                                                                                              | MCP 伺服器報告 [URL 模式引出](https://code.claude.com/docs/zh-TW/hooks#elicitation-input) 完成                                                                                                                                                                                                                                                     |
| `elicitation_response`                                                                                                                                                                                                                                                                                                                                                                              | MCP 引出回應發送回伺服器                                                                                                                                                                                                                                                                                                                           |
| `agent_needs_input`                                                                                                                                                                                                                                                                                                                                                                                 | 背景工作階段在 [代理檢視](https://code.claude.com/docs/zh-TW/agent-view) 在終端中開啟時開始等待您的輸入，或目前工作階段詢問您 [代理團隊隊友的終端設定問題](https://code.claude.com/docs/zh-TW/agent-teams#choose-a-display-mode)，您約六秒未輸入                                                                                                   |
| `agent_completed`                                                                                                                                                                                                                                                                                                                                                                                   | 背景工作階段完成或失敗。僅在 [代理檢視](https://code.claude.com/docs/zh-TW/agent-view) 在終端中開啟時觸發                                                                                                                                                                                                                                          |
| `quota_auto_resume_fired`                                                                                                                                                                                                                                                                                                                                                                           | Claude Code 在 claude.ai 使用限制暫停後繼續您的任務：在重設時，或更早當您在 Claude Code 中執行某事時，例如新增使用額度、升級計畫或切換模型，使使用可用，搭配 [模型設定例外](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)                                                                                   |
| `quota_auto_resume_stale`                                                                                                                                                                                                                                                                                                                                                                           | claude.ai 使用限制在您的電腦睡眠超過約 30 分鐘時重設。Claude Code 等待您按 `Enter` 而不是繼續。睡眠較短後它繼續並改為觸發 `quota_auto_resume_fired`                                                                                                                                                                                                |
| `quota_auto_resume_disabled`                                                                                                                                                                                                                                                                                                                                                                        | Claude Code 結束其對 claude.ai 使用限制的等待而不繼續您的任務：[`autoContinueAtUsageLimit`](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit) 關閉或重設在 Claude Code 啟動的等待期間移動超過 24 小時，繼續的任務持續命中限制，或繼續在到達模型之前被阻止。當您按 `Esc` 或 `Ctrl+C` 或選擇 **不要自動繼續** 時不觸發 |
| `agent_needs_input` 和 `agent_completed` 類型需要 Claude Code v2.1.198 或更新版本。 `quota_auto_resume_fired`、`quota_auto_resume_stale` 和 `quota_auto_resume_disabled` 類型需要 Claude Code v2.1.234 或更新版本。 在終端工作階段中，沙箱命令的網路請求的 `permission_prompt` 需要 Claude Code v2.1.246 或更新版本。 隊友終端設定問題的 `agent_needs_input` 需要 Claude Code v2.1.248 或更新版本。 |                                                                                                                                                                                                                                                                                                                                                    |
| `permission_prompt`、`idle_prompt`、`elicitation_dialog` 和 `elicitation_url_dialog` 類型與桌面通知共享其計時，因此在終端工作階段中您僅在您似乎遠離終端時看到它們：                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                    |

- 期望 `permission_prompt` 一旦您約六秒未輸入。計時器在權限提示出現時啟動，每次按鍵都會延遲它。若要在 Claude 要求許可使用工具時立即執行 hook，請改用 [PermissionRequest](https://code.claude.com/docs/zh-TW/hooks#permissionrequest)。
- 期望 `idle_prompt` 約 60 秒後 Claude 完成回應，且僅在您自那以後未輸入時。Claude Code 在等待 claude.ai 使用限制重設時不發送 `idle_prompt`。等待結束時，其中一個 `quota_auto_resume_*` 類型改為觸發。
- 期望 `elicitation_dialog` 用於引出表單，或 `elicitation_url_dialog` 用於瀏覽器 URL 請求，一旦您約六秒未輸入。兩者共享與 `permission_prompt` 相同的六秒閘門：計時器在對話出現時啟動，每次按鍵都會延遲它。

在另一個對話在螢幕上時到達的權限請求或引出保持相同的六秒閘門，從請求到達時計時。其通知可以在請求仍在開啟對話後面等待時到達您。 Claude Code 在發送權限請求給 Agent SDK 的 [`canUseTool` 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/user-input) 的工作階段中以不同方式計時 `permission_prompt`，這是 Claude Desktop 和 VS Code 擴充功能託管 Claude Code 的方式：

- 期望 `permission_prompt` 約六秒後 Claude 要求許可。Claude Code 在您輸入時不延遲它。
- 如果您或 [PermissionRequest](https://code.claude.com/docs/zh-TW/hooks#permissionrequest) hook 更早回答，Claude Code 不執行 `permission_prompt`。
- 設定 [`CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS`](https://code.claude.com/docs/zh-TW/env-vars) 為 `1` 以在這些工作階段中關閉 `permission_prompt`。

在 v2.1.233 之前，`permission_prompt` 在這些工作階段中不觸發。 使用單獨的匹配器根據通知類型執行不同的處理程式。此設定在 Claude 需要權限核准時觸發權限特定警報指令碼，在 Claude 閒置時觸發不同的通知：

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/permission-alert.sh"
          }
        ]
      },
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/idle-notification.sh"
          }
        ]
      }
    ]
  }
}

```

#### Notification 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，Notification hooks 還會接收 `message` 搭配通知文字、可選 `title` 和 `notification_type` 指示哪個類型觸發。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Notification",
  "message": "Claude needs your permission",
  "title": "Permission needed",
  "notification_type": "permission_prompt"
}

```

Notification hooks 無法阻止或修改通知。Claude Code 捨棄它們的 `systemMessage` 和 `continue` 欄位，但仍然發出 [`terminalSequence`](https://code.claude.com/docs/zh-TW/hooks#emit-terminal-notifications)，這是桌面通知範例所依賴的。Notification hooks 用於副作用，例如將通知轉發到外部服務。

### SubagentStart

在 Claude 使用 Agent 工具生成子代理時執行，當 Claude [恢復子代理](https://code.claude.com/docs/zh-TW/sub-agents#resume-subagents) 時，以及每次進程內 [代理團隊](https://code.claude.com/docs/zh-TW/agent-teams) 隊友處理新訊息時執行。支援匹配器以按代理類型名稱篩選。對於內建代理，這是代理名稱，例如 `general-purpose`、`Explore` 或 `Plan`。對於 [自訂子代理](https://code.claude.com/docs/zh-TW/sub-agents)，這是代理 frontmatter 中的 `name` 欄位，而不是檔案名稱。 對於由 [外掛](https://code.claude.com/docs/zh-TW/plugins) 提供的子代理，代理類型是外掛範圍識別碼，例如 `my-plugin:reviewer`，而不是裸 frontmatter 名稱。冒號將外掛範圍名稱放在正規表達式路徑上，因此使用 `^` 和 `$` 錨定匹配器以進行精確匹配：`^my-plugin:reviewer$`。

#### SubagentStart 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，SubagentStart hooks 還會接收 `agent_id` 搭配子代理的唯一識別碼和 `agent_type` 搭配匹配器篩選的代理名稱。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SubagentStart",
  "agent_id": "agent-abc123",
  "agent_type": "Explore"
}

```

SubagentStart hooks 無法阻止子代理建立，但它們可以將背景資訊注入到子代理中。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您可以返回：

| 欄位                | 描述                                                                                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `additionalContext` | 在子代理對話開始時、其第一個提示之前新增到子代理背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude) |

```
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Follow security guidelines for this task"
  }
}

```

當 hook 再次為相同子代理執行時，Claude Code 僅在子代理的背景資訊還不包含早期執行副本時注入返回的背景資訊。在啟動時注入的副本保留在位置，保持子代理的 [prompt cache](https://code.claude.com/docs/zh-TW/prompt-caching#subagents-and-the-cache) 完整。在 [自動壓縮](https://code.claude.com/docs/zh-TW/sub-agents#auto-compaction) 捨棄該副本後，Claude Code 在下一次執行時再次注入背景資訊。

### SubagentStop

在 Claude Code 子代理完成回應時執行。在代理類型上匹配，與 SubagentStart 相同的值。

#### SubagentStop 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，SubagentStop hooks 還會接收 `stop_hook_active`、`agent_id`、`agent_type`、`agent_transcript_path` 和 `last_assistant_message`。`agent_type` 欄位是用於匹配器篩選的值。`transcript_path` 是主工作階段的文字記錄，而 `agent_transcript_path` 是子代理自己的文字記錄，儲存在巢狀 `subagents/` 資料夾中。`last_assistant_message` 欄位包含子代理最終回應的文字內容，因此 hooks 可以存取它而不解析文字記錄檔案。 在 Claude Code v2.1.271 或更新版本上，使用 [`SubagentHandback`](https://code.claude.com/docs/zh-TW/tools-reference) 工具執行的子代理在停止之前透過該工具傳遞其報告。`last_assistant_message` 欄位然後保留子代理的結束文字（如果有），這不是傳遞的報告。報告是該呼叫的 `message` 輸入，`PreToolUse` 或 `PostToolUse` hook 在 `SubagentHandback` 上匹配時接收為 `tool_input.message`。 SubagentStop hooks 也接收 [Stop 輸入](https://code.claude.com/docs/zh-TW/hooks#stop-input) 下描述的 `background_tasks` 和 `session_crons` 陣列。兩個陣列的範圍是父工作階段，而不是子代理。

```
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../abc123.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "def456",
  "agent_type": "Explore",
  "agent_transcript_path": "~/.claude/projects/.../abc123/subagents/agent-def456.jsonl",
  "last_assistant_message": "Analysis complete. Found 3 potential issues...",
  "background_tasks": [],
  "session_crons": []
}

```

SubagentStop hooks 使用與 [Stop hooks](https://code.claude.com/docs/zh-TW/hooks#stop-decision-control) 相同的決策控制格式，包括 `hookSpecificOutput.additionalContext` 搭配 `hookEventName` 設定為 `"SubagentStop"`，用於保持子代理執行的非錯誤回饋。返回 `decision: "block"` 搭配 `reason` 保持子代理執行並將 `reason` 作為其下一個指令傳遞給子代理。透過退出 2 阻止的 hook 以相同方式傳遞其 stderr 訊息。若要在子代理返回後將背景資訊注入到父工作階段，請改用 `Agent` 工具上的 [`PostToolUse`](https://code.claude.com/docs/zh-TW/hooks#posttooluse) hook。

### TaskCreated

在透過 `TaskCreate` 工具建立任務時執行。使用此來強制命名慣例、要求任務描述或防止建立某些任務。在 [沒有 Task 工具的工作階段](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability) 中，此事件不觸發。 TaskCreated hooks 不支援匹配器，對每個出現觸發。

#### TaskCreated 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，TaskCreated hooks 還會接收 `task_id`、`task_subject` 和可選的 `task_description`、`teammate_name` 和 `team_name`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "TaskCreated",
  "task_id": "task-001",
  "task_subject": "Implement user authentication",
  "task_description": "Add login and signup endpoints",
  "teammate_name": "implementer",
  "team_name": "session-a1b2c3d4"
}

```

| 欄位               | 描述                                               |
| ------------------ | -------------------------------------------------- |
| `task_id`          | 正在建立的任務的識別碼                             |
| `task_subject`     | 任務的標題                                         |
| `task_description` | 任務的詳細描述。可能不存在                         |
| `teammate_name`    | 建立任務的隊友的名稱。可能不存在                   |
| `team_name`        | 已棄用。工作階段衍生的團隊名稱；將在未來版本中移除 |

#### TaskCreated 決策控制

TaskCreated hook 可以透過兩種方式阻止建立。任一方式，Claude Code 刪除任務並將您的訊息返回給 Claude 作為工具的錯誤。Claude Code 忽略此事件中的 `continue: false`，Claude 繼續工作。

- **退出代碼 2** ：Claude Code 將 stderr 文字返回作為訊息。
- **JSON`{"decision": "block", "reason": "..."}`** ：Claude Code 將 `reason` 返回作為訊息。

此範例阻止主題不遵循所需格式的任務：

```
#!/bin/bash
INPUT=$(cat)
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

if [[ ! "$TASK_SUBJECT" =~ ^\[TICKET-[0-9]+\] ]]; then
  echo "Task subject must start with a ticket number, e.g. '[TICKET-123] Add feature'" >&2
  exit 2
fi

exit 0

```

### TaskCompleted

在任務被標記為完成時執行。這在兩種情況下觸發：當任何代理透過 TaskUpdate 工具明確標記任務為完成時，或當 [代理團隊](https://code.claude.com/docs/zh-TW/agent-teams) 隊友以進行中的任務完成其回合時。使用此來強制完成條件，例如通過測試或 lint 檢查，然後任務才能關閉。 TaskCompleted hooks 不支援匹配器，對每個出現觸發。

#### TaskCompleted 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，TaskCompleted hooks 還會接收 `task_id`、`task_subject` 和可選的 `task_description`、`teammate_name` 和 `team_name`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "TaskCompleted",
  "task_id": "task-001",
  "task_subject": "Implement user authentication",
  "task_description": "Add login and signup endpoints",
  "teammate_name": "implementer",
  "team_name": "session-a1b2c3d4"
}

```

| 欄位               | 描述                                               |
| ------------------ | -------------------------------------------------- |
| `task_id`          | 正在完成的任務的識別碼                             |
| `task_subject`     | 任務的標題                                         |
| `task_description` | 任務的詳細描述。可能不存在                         |
| `teammate_name`    | 完成任務的隊友的名稱。可能不存在                   |
| `team_name`        | 已棄用。工作階段衍生的團隊名稱；將在未來版本中移除 |

#### TaskCompleted 決策控制

TaskCompleted hooks 支援兩種方式來控制任務完成：

- **退出代碼 2** ：任務未被標記為完成，stderr 訊息作為回饋反饋給模型。
- **JSON`{"continue": false, "stopReason": "..."}`** ：當隊友完成其回合觸發事件時，完全停止隊友，匹配 `Stop` hook 行為。`stopReason` 顯示給使用者。當 `TaskUpdate` 工具觸發事件時，Claude Code 忽略 `continue: false`；退出代碼 2 仍然阻止完成。

此範例執行測試並在它們失敗時阻止任務完成：

```
#!/bin/bash
INPUT=$(cat)
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

# Run the test suite
if ! npm test 2>&1; then
  echo "Tests not passing. Fix failing tests before completing: $TASK_SUBJECT" >&2
  exit 2
fi

exit 0

```

### Stop

在主 Claude Code 代理完成回應時執行。如果停止發生是由於使用者中斷，則不執行。API 錯誤改為觸發 [StopFailure](https://code.claude.com/docs/zh-TW/hooks#stopfailure)。 [`/goal`](https://code.claude.com/docs/zh-TW/goal) 命令是工作階段範圍提示型 Stop hook 的內建快捷方式。當您想讓 Claude 在不編寫 hook 設定的情況下朝著條件繼續工作時使用它。

#### Stop 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，Stop hooks 還會接收 `stop_hook_active`、`last_assistant_message`、`background_tasks` 和 `session_crons`。`stop_hook_active` 欄位在 Claude Code 已作為 stop hook 的結果繼續時為 `true`。檢查此值或處理文字記錄以避免在永遠不會解決的條件上阻止。Claude Code 在 8 個連續阻止後覆寫 hook 並結束回合。 `last_assistant_message` 欄位包含 Claude 最終回應的文字內容，因此 hooks 可以存取它而不解析文字記錄檔案。對於作用於剛完成回合的 hooks，例如朗讀或通知 hooks，使用此欄位而不是讀取 `transcript_path`：文字記錄檔案不保證在所有版本上的 Stop 時間包含最終訊息。 `background_tasks` 和 `session_crons` 陣列讓 hooks 區分「工作階段完成」與「工作階段暫停等待背景工作喚醒它」。當任務登錄可到達時兩個陣列都存在，當沒有任何內容在進行中或排程時為空。 `background_tasks` 中的每個項目描述一個進行中的任務並使用這些欄位：

| 欄位                                                                                                       | 描述                                                                                                                                                                                          |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                                                                                       | 任務識別碼                                                                                                                                                                                    |
| `type`                                                                                                     | 友善任務類型標籤，例如 `shell`、`subagent`、`monitor`、`workflow`、`teammate`、`cloud session` 或 `MCP task`。每個標籤識別哪個 Claude Code 功能建立了任務。對於無法識別的類型回退到原始判別式 |
| `status`                                                                                                   | 目前任務狀態                                                                                                                                                                                  |
| `description`                                                                                              | 自由文字描述，上限為 1000 個字元，當剪裁時在字串中帶有 `… [+N chars]` 標記                                                                                                                    |
| `command`                                                                                                  | Shell 命令行，上限為 1000 個字元。僅對 `shell` 任務出現                                                                                                                                       |
| `agent_type`                                                                                               | 子代理類型名稱。僅對 `subagent` 任務出現                                                                                                                                                      |
| `server`                                                                                                   | MCP 伺服器名稱。僅對 `monitor` 和 `MCP task` 任務出現                                                                                                                                         |
| `tool`                                                                                                     | MCP 工具名稱。僅對 `monitor` 和 `MCP task` 任務出現                                                                                                                                           |
| `name`                                                                                                     | 工作流程名稱。僅對 `workflow` 任務出現                                                                                                                                                        |
| `session_crons` 中的每個項目描述一個工作階段範圍排程喚醒，來自 `CronCreate`、`ScheduleWakeup` 和 `/loop`： |                                                                                                                                                                                               |
| 欄位                                                                                                       | 描述                                                                                                                                                                                          |
| ---                                                                                                        | ---                                                                                                                                                                                           |
| `id`                                                                                                       | Cron 任務識別碼                                                                                                                                                                               |
| `schedule`                                                                                                 | Cron 表達式，例如 `0 9 * * 1-5`                                                                                                                                                               |
| `recurring`                                                                                                | 對於一次性喚醒（其排程編碼單個觸發時間）為 `false`，對於在每個匹配上重新觸發的任務為 `true`                                                                                                   |
| `prompt`                                                                                                   | Cron 觸發時提交的提示，上限為 1000 個字元，帶有相同的 `… [+N chars]` 標記                                                                                                                     |
| 此範例顯示一個 Stop 輸入，其中一個進行中的 shell 任務和一個循環 cron：                                     |                                                                                                                                                                                               |

```
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": true,
  "last_assistant_message": "I've completed the refactoring. Here's a summary...",
  "background_tasks": [
    {
      "id": "task-001",
      "type": "shell",
      "status": "running",
      "description": "tail logs",
      "command": "tail -f /var/log/syslog"
    }
  ],
  "session_crons": [
    {
      "id": "cron-001",
      "schedule": "0 9 * * 1-5",
      "recurring": true,
      "prompt": "check the build"
    }
  ]
}

```

#### Stop 決策控制

`Stop` 和 `SubagentStop` hooks 可以控制 Claude 是否繼續。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您的 hook 指令碼可以返回這些事件特定欄位：

| 欄位                                                                                                 | 描述                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `decision`                                                                                           | `"block"` 防止 Claude 停止。省略以允許 Claude 停止                                                                                     |
| `reason`                                                                                             | 當 `decision` 為 `"block"` 時需要。告訴 Claude 為什麼它應該繼續                                                                        |
| `hookSpecificOutput.additionalContext`                                                               | Claude 的非錯誤回饋。對話繼續，以便 Claude 可以作用於它，但與 `decision: "block"` 不同，它在文字記錄中顯示為 hook 回饋而不是 hook 錯誤 |
| 透過退出 2 阻止的 hook 路由方式與 `reason` 相同：Claude 接收 stderr 訊息作為為什麼它應該繼續的解釋。 |                                                                                                                                        |

```
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}

```

當 hook 按設計工作並給予 Claude 指導時使用 `additionalContext`，例如「在完成前執行測試套件」。它透過與 `decision: "block"` 相同的迴圈保護保持對話進行，即 `stop_hook_active` 輸入和 8 個連續繼續上限，但文字記錄將其標籤為 `Stop hook feedback`，不顯示 hook 錯誤通知：

```
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "Please run the test suite before finishing"
  }
}

```

### StopFailure

在回合因 API 錯誤而結束時執行，而不是 [Stop](https://code.claude.com/docs/zh-TW/hooks#stop)。Claude Code 忽略 hook 的輸出和退出代碼，除了 [`terminalSequence`](https://code.claude.com/docs/zh-TW/hooks#emit-terminal-notifications)。使用此來記錄失敗、發送警報或在 Claude 因速率限制、驗證問題或其他 API 錯誤而無法完成回應時採取恢復動作。

#### StopFailure 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，StopFailure hooks 還會接收 `error`、可選 `error_details` 和可選 `last_assistant_message`。`error` 欄位識別錯誤類型並用於匹配器篩選。

| 欄位                     | 描述                                                                                                                                                                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `error`                  | 錯誤類型：`rate_limit`、`overloaded`、`authentication_failed`、`oauth_org_not_allowed`、`account_on_hold`、`billing_error`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens`、`cloud_credential_error` 或 `unknown` |
| `error_details`          | 關於錯誤的其他詳細資訊（如果可用）                                                                                                                                                                                                           |
| `last_assistant_message` | 在對話中顯示的呈現錯誤文字。與 `Stop` 和 `SubagentStop` 不同，其中此欄位保留 Claude 的對話輸出，對於 `StopFailure` 它包含 API 錯誤字串本身，例如 `"API Error: Rate limit reached"`                                                           |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "StopFailure",
  "error": "rate_limit",
  "error_details": "429 Too Many Requests",
  "last_assistant_message": "API Error: Rate limit reached"
}

```

StopFailure hooks 沒有決策控制。它們僅用於通知和記錄目的執行。

### TeammateIdle

在 [代理團隊](https://code.claude.com/docs/zh-TW/agent-teams) 隊友在完成其回合後即將閒置時執行。使用此來強制品質閘門，然後隊友停止工作，例如要求通過 lint 檢查或驗證輸出檔案存在。 TeammateIdle hooks 不支援匹配器，對每個出現觸發。

#### TeammateIdle 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，TeammateIdle hooks 還會接收 `teammate_name` 和 `team_name`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "TeammateIdle",
  "teammate_name": "researcher",
  "team_name": "session-a1b2c3d4"
}

```

| 欄位            | 描述                                               |
| --------------- | -------------------------------------------------- |
| `teammate_name` | 即將閒置的隊友的名稱                               |
| `team_name`     | 已棄用。工作階段衍生的團隊名稱；將在未來版本中移除 |

#### TeammateIdle 決策控制

TeammateIdle hooks 支援兩種方式來控制隊友行為：

- **退出代碼 2** ：隊友接收 stderr 訊息作為回饋並繼續工作而不是閒置。
- **JSON`{"continue": false, "stopReason": "..."}`** ：完全停止隊友，匹配 `Stop` hook 行為。`stopReason` 顯示給使用者。

此範例檢查建置成品存在，然後允許隊友閒置：

```
#!/bin/bash

if [ ! -f "./dist/output.js" ]; then
  echo "Build artifact missing. Run the build before stopping." >&2
  exit 2
fi

exit 0

```

### ConfigChange

在工作階段期間設定檔變更時執行。使用此來稽核設定變更、強制安全原則或阻止對設定檔的未授權修改。 Claude Code 在設定檔、受管原則檔案或 skill 檔案變更時執行 ConfigChange hooks。對於受管原則，它僅在 `managed-settings.json` 或 `managed-settings.d/` 中的檔案變更時執行。它應用 [伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings) 和對 macOS 受管偏好設定或 Windows 登錄原則的變更而不執行。在 WSL 上搭配 [`wslInheritsWindowsSettings`](https://code.claude.com/docs/zh-TW/settings-reference#wslinheritswindowssettings)，它也應用在其原則輪詢上變更的 Windows 端受管設定檔而不執行。 匹配器篩選設定來源：

| 匹配器                                 | 何時觸發                                                      |
| -------------------------------------- | ------------------------------------------------------------- |
| `user_settings`                        | `~/.claude/settings.json` 變更                                |
| `project_settings`                     | `.claude/settings.json` 變更                                  |
| `local_settings`                       | `.claude/settings.local.json` 變更                            |
| `policy_settings`                      | `managed-settings.json` 或 `managed-settings.d/` 中的檔案變更 |
| `skills`                               | `.claude/skills/` 中的 skill 檔案變更                         |
| 此範例記錄所有設定變更以進行安全稽核： |                                                               |

```
{
  "hooks": {
    "ConfigChange": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/audit-config-change.sh",
            "args": []
          }
        ]
      }
    ]
  }
}

```

#### ConfigChange 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，ConfigChange hooks 還會接收 `source` 和可選的 `file_path`。`source` 欄位指示哪個設定類型變更，`file_path` 提供修改的特定檔案的路徑。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "ConfigChange",
  "source": "project_settings",
  "file_path": "/Users/.../my-project/.claude/settings.json"
}

```

#### ConfigChange 決策控制

ConfigChange hooks 可以阻止設定變更生效。使用退出代碼 2 或 JSON `decision` 來防止變更。被阻止時，新設定不會套用到執行中的工作階段。

| 欄位       | 描述                                         |
| ---------- | -------------------------------------------- |
| `decision` | `"block"` 防止設定變更被套用。省略以允許變更 |
| `reason`   | 接受但永遠不顯示                             |

```
{
  "decision": "block",
  "reason": "Configuration changes to project settings require admin approval"
}

```

`policy_settings` 變更無法被阻止。當機器上的受管設定檔變更時，Hooks 仍然對 `policy_settings` 來源觸發，因此您可以使用它們來記錄這些編輯，但任何阻止決策都被忽略。這確保企業受管設定始終生效。當 [伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings) 到達或重新整理時，Claude Code 不執行 `ConfigChange` hooks。 Claude Code 作用於 ConfigChange hook 的 JSON 輸出中的阻止決策，並捨棄 `systemMessage` 和 `continue`。被阻止的變更不向您或 Claude 呈現任何訊息，無論您是否使用 `reason` 或退出 2 時的 stderr 阻止。Claude Code 僅將一行寫入偵錯日誌。

### CwdChanged

在主對話中的 shell 命令變更工作目錄時執行，例如當 Claude 執行 `cd` 命令時。使用此來對目錄變更做出反應：重新載入環境變數、啟動專案特定工具鏈或自動執行設定指令碼。與 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) 配對，用於 [direnv](https://direnv.net/) 等管理每個目錄環境的工具。 CwdChanged hooks 可以存取 [`CLAUDE_ENV_FILE`](https://code.claude.com/docs/zh-TW/hooks#persist-environment-variables)。寫入該檔案的變數會保留到下一個 CwdChanged 事件，當 Claude Code 清除它們時。 CwdChanged 不支援匹配器，對每個出現觸發。

#### CwdChanged 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，CwdChanged hooks 還會接收 `old_cwd` 和 `new_cwd`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project/src",
  "hook_event_name": "CwdChanged",
  "old_cwd": "/Users/my-project",
  "new_cwd": "/Users/my-project/src"
}

```

#### CwdChanged 輸出

除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，CwdChanged hooks 可以返回 `watchPaths` 以動態設定 [FileChanged](https://code.claude.com/docs/zh-TW/hooks#filechanged) 監視的檔案路徑：

| 欄位                                                                                                                                                                                                                          | 描述                                                                                                                              |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `watchPaths`                                                                                                                                                                                                                  | 絕對路徑的陣列。替換目前的動態監視清單。您的 `matcher` 設定中的路徑始終被監視。返回空陣列以清除動態清單，這在進入新目錄時是典型的 |
| CwdChanged hooks 沒有決策控制。它們無法阻止目錄變更。 Claude Code 從其 JSON 輸出讀取 `watchPaths` 和 `systemMessage`，並捨棄 `continue`。在互動式工作階段中，它將 `systemMessage` 顯示為簡短終端通知。訊息不到達 SDK 訊息流。 |                                                                                                                                   |

### DirectoryAdded

在您使用 `/add-dir` 命令在工作階段中期新增工作目錄後執行，或在 SDK 用戶端使用 `register_repo_root` 控制請求新增工作目錄後執行。使用此來準備新增的儲存庫，例如安裝其相依性。 Claude Code 在以下情況下不觸發此事件：

- 您使用 `--add-dir` 啟動旗標傳遞目錄；[SessionStart](https://code.claude.com/docs/zh-TW/hooks#sessionstart) 涵蓋這些目錄
- 您在 `/permissions` Workspace 標籤上新增目錄
- 您新增已是工作目錄或在其內部的目錄

Claude Code 在重新整理沙箱和權限狀態後觸發 DirectoryAdded，因此沙箱工具在您的 hook 執行時已看到新目錄。Hook 命令本身執行未沙箱化。 Claude Code 不等待 hook：新增立即完成，hook 在背景執行，使用 600 秒預設逾時。 匹配器篩選目錄的新增方式：

| 匹配器               | 何時觸發                                             |
| -------------------- | ---------------------------------------------------- |
| `slash_command`      | 您使用 `/add-dir` 新增目錄                           |
| `register_repo_root` | SDK 用戶端使用 `register_repo_root` 控制請求新增目錄 |

#### DirectoryAdded 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，DirectoryAdded hooks 還會接收 `directory` 和 `source`。

| 欄位        | 描述                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------- |
| `directory` | 新增的目錄的絕對路徑                                                                     |
| `source`    | 目錄如何被新增，`/add-dir` 為 `"slash_command"` 或 SDK 控制請求為 `"register_repo_root"` |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "DirectoryAdded",
  "directory": "/Users/my-other-repo",
  "source": "slash_command"
}

```

DirectoryAdded hooks 沒有決策控制。它們無法阻止新增，這在 hook 執行時已完成。Claude Code 從其 JSON 輸出捨棄 `continue` 欄位，並根據來源以不同方式呈現其餘部分：

- `slash_command`：Claude Code 將 hook 的 `systemMessage` 傳遞給 Claude 作為下一個對話回合的背景資訊，而不是向您顯示。失敗 hooks 的計數出現在文字記錄中。完整失敗輸出進入偵錯日誌
- `register_repo_root`：Claude Code 僅將 `systemMessage` 輸出和失敗輸出寫入偵錯日誌

### FileChanged

在監視的檔案在磁碟上變更時執行。Claude Code 使用檔案系統監視器偵測變更，而不是檢查工具呼叫，因此無論什麼變更檔案，它都執行 hook：`Edit` 或 `Write` 工具呼叫、Claude 使用 `Bash` 執行的指令碼，或 Claude Code 外的程序。常見用途是在專案設定檔變更時重新載入環境變數。 此事件的 `matcher` 有兩個角色：

- **建立監視清單** ：值在 `|` 上分割，每個段落註冊為工作目錄中的字面檔案名稱，因此 `".envrc|.env"` 監視恰好這兩個檔案。正規表達式模式在這裡不有用：`^\.env` 之類的值會監視字面名稱為 `^\.env` 的檔案。
- **篩選哪些 hooks 執行** ：當監視的檔案變更時，相同的值使用標準 [匹配器規則](https://code.claude.com/docs/zh-TW/hooks#matcher-patterns) 針對變更檔案的基名篩選哪些 hook 群組執行。

此範例在任何變更後規範化 `data.csv` 中的行結尾，包括 `Bash` 命令或外部指令碼重寫檔案：

```
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": "data.csv",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/normalize-line-endings.sh"
          }
        ]
      }
    ]
  }
}

```

Hook 從 [JSON 輸入](https://code.claude.com/docs/zh-TW/hooks#filechanged-input) 的 `file_path` 欄位讀取變更檔案的絕對路徑，在 stdin 上。其 `grep` 守衛測試 `perl` 移除的相同內容，行尾的 CR，因此規範化後的執行退出而不觸及檔案。較鬆散的守衛迴圈永遠，因為 `perl -i` 重寫檔案即使它替換無內容，Claude Code 在每次重寫後執行 hook。將此指令碼儲存在 `/path/to/normalize-line-endings.sh` 並使其可執行：

```
#!/bin/bash
FILE=$(jq -r .file_path)
if grep -q $'\r$' "$FILE"; then
  perl -pi -e 's/\r$//' "$FILE"
fi

```

若要確認 hook 有效，要求 Claude 使用 `Bash` 命令將 CRLF 行附加到 `data.csv`。Claude Code 執行 hook，檔案以 LF 結尾。 若要監視您無法提前命名的檔案，請從 hook 返回 [`watchPaths`](https://code.claude.com/docs/zh-TW/hooks#filechanged-output) 以動態更新監視清單。Claude Code 僅在某事命名要監視的檔案時啟動監視器，因此使用至少命名一個檔案的 FileChanged 群組播種清單，或使用 [SessionStart](https://code.claude.com/docs/zh-TW/hooks#sessionstart-decision-control) 或 [CwdChanged](https://code.claude.com/docs/zh-TW/hooks#cwdchanged) hook 返回 `watchPaths`。匹配器仍然篩選當監視的檔案變更時哪些 hook 群組執行，因此給處理動態路徑的群組一個省略的匹配器，它匹配每個監視的檔案並不向監視清單新增任何內容。`"*"` 匹配器也匹配每個檔案，但 Claude Code 在監視清單中註冊它，如同任何其他值，作為字面名稱為 `*` 的檔案。 FileChanged hooks 可以存取 [`CLAUDE_ENV_FILE`](https://code.claude.com/docs/zh-TW/hooks#persist-environment-variables)。寫入該檔案的變數會保留到下一個 [CwdChanged](https://code.claude.com/docs/zh-TW/hooks#cwdchanged) 事件，當 Claude Code 清除它們時。

#### FileChanged 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，FileChanged hooks 還會接收 `file_path` 和 `event`。

| 欄位        | 描述                                                                                |
| ----------- | ----------------------------------------------------------------------------------- |
| `file_path` | 變更的檔案的絕對路徑                                                                |
| `event`     | 發生的情況：修改的檔案為 `"change"`、建立的檔案為 `"add"` 或刪除的檔案為 `"unlink"` |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "FileChanged",
  "file_path": "/Users/my-project/.envrc",
  "event": "change"
}

```

#### FileChanged 輸出

除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，FileChanged hooks 可以返回 `watchPaths` 以動態更新監視的檔案路徑：

| 欄位                                                                                                                                                                                                                               | 描述                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `watchPaths`                                                                                                                                                                                                                       | 絕對路徑的陣列。替換目前的動態監視清單。您的 `matcher` 設定中的路徑始終被監視。當您的 hook 指令碼根據變更的檔案探索要監視的其他檔案時使用此 |
| FileChanged hooks 沒有決策控制。它們無法阻止檔案變更發生。 Claude Code 從其 JSON 輸出讀取 `watchPaths` 和 `systemMessage`，並捨棄 `continue`。在互動式工作階段中，它將 `systemMessage` 顯示為簡短終端通知。訊息不到達 SDK 訊息流。 |                                                                                                                                             |

### WorktreeCreate

在建立 worktree 時執行，無論是從 `claude --worktree`、從 [使用 `isolation: "worktree"` 的子代理](https://code.claude.com/docs/zh-TW/sub-agents#choose-the-subagent-scope)，或用於 Claude Code 在其自己的 worktree 中隔離的 [背景工作階段](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)。預設情況下 Claude Code 使用 `git worktree` 建立隔離的工作副本。設定 WorktreeCreate hook 完全替換該預設 git 行為，讓您使用不同的版本控制系統，例如 SVN、Perforce 或 Mercurial。 因為 hook 完全替換預設行為，[`.worktreeinclude`](https://code.claude.com/docs/zh-TW/worktrees#copy-gitignored-files-into-worktrees) 不被處理。如果您需要複製本機設定檔，例如 `.env`，到新 worktree，請在您的 hook 指令碼內執行。 Hook 必須返回建立的 worktree 目錄的路徑。Claude Code 使用此路徑作為隔離工作階段的工作目錄。請參閱 [WorktreeCreate 輸出](https://code.claude.com/docs/zh-TW/hooks#worktreecreate-output)，了解每個 hook 類型如何返回路徑。 Claude Code 作用於 hook 的成功和返回的路徑，並捨棄 `systemMessage` 和 `continue`。 此範例建立 SVN 工作副本並列印路徑供 Claude Code 使用。將儲存庫 URL 替換為您自己的：

```
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'NAME=$(jq -r .name); DIR=\"$HOME/.claude/worktrees/$NAME\"; svn checkout https://svn.example.com/repo/trunk \"$DIR\" >&2 && echo \"$DIR\"'"
          }
        ]
      }
    ]
  }
}

```

Hook 從 stdin 上的 JSON 輸入讀取 worktree `name`，將新副本簽出到新目錄，並列印目錄路徑。最後一行的 `echo` 是 Claude Code 讀取為 worktree 路徑的內容。將任何其他輸出重定向到 stderr，以便它不干擾路徑。

#### WorktreeCreate 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，WorktreeCreate hooks 還會接收 `name` 欄位。這是新 worktree 的 slug 識別碼，由使用者指定或自動生成，例如 `bold-oak-a3f2`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "WorktreeCreate",
  "name": "feature-auth"
}

```

#### WorktreeCreate 輸出

WorktreeCreate hooks 不使用標準允許/阻止決策模型。相反，hook 的成功或失敗決定結果。Hook 必須返回建立的 worktree 目錄的路徑：

- **命令 hooks** (`type: "command"`)：將路徑列印為 stdout 的最後一個非空行。Claude Code 在讀取該行之前去除 ANSI 逸出代碼，因此在您的 `echo` 之前列印的 shell 啟動橫幅被忽略。將任何其他 hook 輸出重定向到 stderr。
- **HTTP hooks** (`type: "http"`)：在回應主體中返回 `{ "hookSpecificOutput": { "hookEventName": "WorktreeCreate", "worktreePath": "/absolute/path" } }`。

如果 hook 失敗或不產生路徑，worktree 建立失敗並出現錯誤。 Claude Code 根據 hook 執行的目錄解決相對路徑，摺疊其中的任何 `.` 或 `..` 段。如果結果路徑不是 Claude Code 可以進入的目錄，工作階段列印命名路徑的錯誤並以代碼 1 退出。 Claude Code 拒絕包含 `.` 或 `..` 段的絕對路徑，以及通過儲存庫根下方的符號連結的任何路徑，因為提交到儲存庫的符號連結可能將 worktree 重定向到其外部。錯誤命名被拒絕的元件。返回不通過儲存庫內符號連結的規範化路徑。在 v2.1.216 之前，worktree 建立遵循 hook 的路徑而不進行此篩選。

### WorktreeRemove

在移除 worktree 時執行。這是 [WorktreeCreate](https://code.claude.com/docs/zh-TW/hooks#worktreecreate) 的清理對應項。事件在以下情況下觸發：

- 您退出 `--worktree` 工作階段並選擇移除它
- 具有 `isolation: "worktree"` 的子代理完成
- 您刪除 [背景工作階段](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)，其 worktree 由 hook 建立

對於基於 git 的 worktrees，Claude Code 使用 `git worktree remove` 自動處理清理。如果您為非 git 版本控制系統設定了 WorktreeCreate hook，請將其與 WorktreeRemove hook 配對以處理清理。沒有它，worktree 目錄保留在磁碟上。 Claude Code 捨棄 WorktreeRemove hook 的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output)，例如 `systemMessage` 和 `continue`。 對於背景工作階段刪除，Claude Code 在執行 hook 之前驗證儲存的 worktree 路徑，並拒絕在儲存庫根下方是符號連結或通過符號連結的路徑。Hook 僅對仍包含檔案的 worktree 執行，當您在 [代理檢視](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes) 中確認刪除時；對於這樣的 worktree，[`claude rm`](https://code.claude.com/docs/zh-TW/agent-view#manage-sessions-from-the-shell) 保持工作階段和 worktree。在 v2.1.216 之前，hook 在儲存的路徑上執行而不進行這些檢查。 Claude Code 將 WorktreeCreate 返回的路徑作為 `worktree_path` 在 hook 輸入中傳遞。此範例讀取該路徑並移除目錄：

```
{
  "hooks": {
    "WorktreeRemove": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'jq -r .worktree_path | xargs rm -rf'"
          }
        ]
      }
    ]
  }
}

```

#### WorktreeRemove 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，WorktreeRemove hooks 還會接收 `worktree_path` 欄位，這是正在移除的 worktree 的絕對路徑。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "WorktreeRemove",
  "worktree_path": "/Users/.../my-project/.claude/worktrees/feature-auth"
}

```

WorktreeRemove hook 的退出代碼決定結果。當 hook 以非零退出且 `worktree_path` 的目錄仍然存在時，移除失敗：

- Worktree 保留在磁碟上，hook 的命令和 stderr 進入 [偵錯日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)。
- 如果您刪除背景工作階段，工作階段也保留。[代理檢視](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes) 中的拒絕訊息報告 hook 如何結束，例如 `exited 1`，引用其 stderr 的開頭，並說明再次刪除工作階段是否移除目錄。

### PreCompact

在 Claude Code 即將執行壓縮操作之前執行。 匹配器值指示壓縮是手動觸發還是自動觸發：

| 匹配器                                                                                                                                                                                                                                                                                                                                                                                                    | 何時觸發                                                                                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `manual`                                                                                                                                                                                                                                                                                                                                                                                                  | `/compact`                                                                                                        |
| `auto`                                                                                                                                                                                                                                                                                                                                                                                                    | 當對話到達 [自動壓縮視窗](https://code.claude.com/docs/zh-TW/model-config#set-the-auto-compact-window) 時自動壓縮 |
| 以代碼 2 退出以阻止壓縮。對於手動 `/compact`，stderr 訊息顯示給使用者。您也可以透過返回 JSON 搭配 `"decision": "block"` 來阻止。 阻止自動壓縮根據何時觸發有不同的效果。如果壓縮在背景資訊限制之前主動觸發，Claude Code 跳過它，對話繼續未壓縮。如果壓縮被觸發以從 API 已返回的背景資訊限制錯誤恢復，基礎錯誤呈現，目前請求失敗。 Claude Code 捨棄 PreCompact hook 的 `systemMessage` 和 `continue` 欄位。 |                                                                                                                   |

#### PreCompact 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，PreCompact hooks 還會接收 `trigger` 和 `custom_instructions`。對於 `manual`，`custom_instructions` 包含使用者傳遞到 `/compact` 的內容，當他們傳遞無內容時為 `null`。對於 `auto`，`custom_instructions` 為 `null`。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "PreCompact",
  "trigger": "manual",
  "custom_instructions": null
}

```

### PostCompact

在 Claude Code 完成壓縮操作後執行。使用此事件對新壓縮狀態做出反應，例如記錄生成的摘要或更新外部狀態。Claude Code 捨棄 PostCompact hook 的 `systemMessage` 和 `continue` 欄位。 與 `PreCompact` 相同的匹配器值適用：

| 匹配器   | 何時觸發                                                                                                            |
| -------- | ------------------------------------------------------------------------------------------------------------------- |
| `manual` | 在 `/compact` 後                                                                                                    |
| `auto`   | 當對話到達 [自動壓縮視窗](https://code.claude.com/docs/zh-TW/model-config#set-the-auto-compact-window) 時自動壓縮後 |

#### PostCompact 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，PostCompact hooks 還會接收 `trigger` 和 `compact_summary`。`compact_summary` 欄位包含壓縮操作生成的對話摘要。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "PostCompact",
  "trigger": "manual",
  "compact_summary": "Summary of the compacted conversation..."
}

```

PostCompact hooks 沒有決策控制。它們無法影響壓縮結果，但可以執行後續任務。

### PreModelSwitch

在 Claude Code 應用您或用戶端請求的模型切換之前執行。使用它來阻止切換、要求確認或在切換發生前顯示成本。 PreModelSwitch 需要 Claude Code v2.1.251 或更新版本。Claude Code 為這些請求執行它：

- `/model <name>` 和 `/model` 選擇器
- `Option+P` 或 `Alt+P` 模型選擇器
- `/config` 中的 Model 設定
- 當那改變工作階段的模型時打開 [快速模式](https://code.claude.com/docs/zh-TW/fast-mode)
- 來自 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#query-object) 主機或 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 的 `set_model` 請求，或 `apply_flag_settings` 請求中的模型變更

Claude Code 不為它自己進行的切換執行 PreModelSwitch hooks，例如 [自動模型回退](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback) 或恢復工作階段時恢復模型。這些變更僅到達 [PostModelSwitch](https://code.claude.com/docs/zh-TW/hooks#postmodelswitch)。 Claude Code 根據工作階段切換到的模型的規範名稱比較匹配器，忽略任何 `[1m]` 後綴。別名（例如 `opus`）、日期模型 ID 和提供者特定 ID（例如 Amazon Bedrock 模型 ID）都匹配它們解決到的一個規範名稱，因此 `claude-opus-5` 涵蓋 Opus 5 的每個拼寫。 當 Claude Code 無法確定目標的規範名稱時，例如僅您的 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway) 知道的自訂模型 ID，它執行每個 PreModelSwitch hook，無論匹配器如何。阻止的 hook 應該檢查其輸入中的 `to_model` 而不是僅依賴匹配器。 將匹配器寫為精確名稱、`|` 分隔清單（例如 `claude-opus-4-6|claude-opus-5`）或正規表達式（例如 `.*opus.*`）。此範例使用精確名稱匹配器並也檢查 hook 輸入中的 `to_model`，因此它拒絕切換到 Opus 4.6，透過以代碼 2 退出，並讓任何其他目標通過：

- macOS/Linux
- Windows (PowerShell)

命令使用 `jq` 檢查 `to_model`：

```
{
  "hooks": {
    "PreModelSwitch": [
      {
        "matcher": "claude-opus-4-6",
        "hooks": [
          {
            "type": "command",
            "command": "jq -e '.to_model | test(\"opus-4-6\")' > /dev/null && { echo 'Opus 4.6 is retired for this project. Use a newer model.' >&2; exit 2; }; exit 0"
          }
        ]
      }
    ]
  }
}

```

註冊一個命令 hook，透過 PowerShell 執行指令碼：

```
{
  "hooks": {
    "PreModelSwitch": [
      {
        "matcher": "claude-opus-4-6",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-opus-46.ps1"
            ]
          }
        ]
      }
    ]
  }
}

```

將此指令碼儲存到您專案中的 `.claude/hooks/block-opus-46.ps1`：

```
$hookInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
if ($hookInput.to_model -match 'opus-4-6') {
  [Console]::Error.WriteLine('Opus 4.6 is retired for this project. Use a newer model.')
  exit 2
}
exit 0

```

若要確認 hook 有效，從執行不同模型的工作階段執行 `/model claude-opus-4-6`。Claude Code 保持目前模型並報告 PreModelSwitch hook 阻止了切換，您的訊息作為原因。

#### PreModelSwitch 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，PreModelSwitch hooks 還會接收此表中的欄位。最後五個描述重新發送對話到新模型的成本，因此 hook 可以在切換發生前顯示該數字。

| 欄位                                                          | 類型             | 描述                                                                                                                                                                                                                       |
| ------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `from_model`                                                  | string           | 切換變更的模型 ID                                                                                                                                                                                                          |
| `to_model`                                                    | string           | 切換變更為的模型 ID。匹配器根據此模型的規範名稱比較                                                                                                                                                                        |
| `requested_model`                                             | string or `null` | 請求命名的模型：別名（例如 `opus`）、完整模型 ID 或當請求為預設模型時 `null`                                                                                                                                               |
| `source`                                                      | string           | 請求來自何處：`/model <name>`、`/config` 中的 Model 設定或打開快速模式的 `"command"`；模型選擇器的 `"picker"`；來自 Agent SDK 主機或 Remote Control 的 `set_model` 請求或 `apply_flag_settings` 請求中的模型變更的 `"sdk"` |
| `context_tokens`                                              | number           | 下一個請求重新發送作為其提示的令牌：主對話中最後回應的輸入、快取讀取、快取建立和輸出令牌結合。第一個回應前為 `0`                                                                                                           |
| `prompt_cache_warm`                                           | boolean          | 目前模型的 prompt cache 是否可能仍然溫暖，意味著切換放棄它                                                                                                                                                                 |
| `cache_ttl`                                                   | string           | [Prompt cache 生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime) Claude Code 為此工作階段請求：`"5m"` 或 `"1h"`                                                                                   |
| `estimated_cache_write_usd`                                   | number           | 在 `cache_ttl` 速率下將 `context_tokens` 寫入 `to_model` 上的 prompt cache 的估計成本（美元），不包括下一個回應                                                                                                            |
| `pricing`                                                     | string           | Claude Code 如何定價 `estimated_cache_write_usd`：當您的組織已設定它們時在您的組織自己的速率下為 `"configured"`、在清單價格下為 `"catalog"`，或當 `to_model` 沒有已知價格且 Claude Code 假設預設速率時為 `"default"`       |
| 此範例顯示在執行 Sonnet 5 的工作階段中 `/model opus` 的輸入： |                  |                                                                                                                                                                                                                            |

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "PreModelSwitch",
  "from_model": "claude-sonnet-5",
  "to_model": "claude-opus-5",
  "requested_model": "opus",
  "source": "command",
  "context_tokens": 182340,
  "prompt_cache_warm": true,
  "cache_ttl": "5m",
  "estimated_cache_write_usd": 1.1396,
  "pricing": "catalog"
}

```

#### PreModelSwitch 決策控制

`PreModelSwitch` hooks 可以取消切換、要求使用者確認或讓它進行。退出代碼 2 或頂級 `decision: "block"` 取消切換。 為了更精細的控制，在 `hookSpecificOutput` 物件中返回 `permissionDecision` 和 `permissionDecisionReason`，如 [PreToolUse](https://code.claude.com/docs/zh-TW/hooks#pretooluse-decision-control) 上。`PreModelSwitch` 接受 `"allow"`、`"deny"` 和 `"ask"`。它不接受 `"defer"`、`updatedInput` 或 `additionalContext`。下表描述兩個欄位：

| 欄位                                                                                                                                                                                                                               | 描述                                                                                                                                                                               |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `permissionDecision`                                                                                                                                                                                                               | `"allow"` 進行並跳過 [Claude Code 在 prompt cache 溫暖時顯示的確認](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)。`"deny"` 取消切換。`"ask"` 提示使用者確認 |
| `permissionDecisionReason`                                                                                                                                                                                                         | 對於 `"deny"`，顯示給使用者作為切換被阻止的原因，或作為 `set_model` 請求的錯誤返回。對於 `"ask"`，在確認提示中顯示。對於 `"allow"` 忽略                                            |
| 僅互動式工作階段中的 `/model` 可以顯示 `"ask"` 提示。在每個其他表面上，包括搭配 `-p` 旗標的非互動模式、`/config` 和 `set_model` 請求，Claude Code 將 `"ask"` 視為拒絕。 此範例要求使用者確認並引用 `context_tokens` 中的令牌計數： |                                                                                                                                                                                    |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreModelSwitch",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Switching now re-sends about 180k tokens to the new model. Continue?"
  }
}

```

當多個 PreModelSwitch hooks 返回不同的決策時，優先順序為 `deny` > `ask` > `allow`。 Claude Code 無論決策如何都顯示您的 hook 返回的任何 `systemMessage`，因此成本報告 hook 可以返回 `{"systemMessage": "..."}` 並退出 0。 在其逾時前未回應的 PreModelSwitch hook 會阻止切換。在 [PreToolUse](https://code.claude.com/docs/zh-TW/hooks#timeouts) 上相比，逾時的命令 hook 讓工具呼叫繼續。此事件的預設逾時為 30 秒。`PreModelSwitch` 僅執行 `command`、`http` 和 `mcp_tool` hooks，因此 `prompt` 和 `agent` 預設不適用。 以 0 或 2 以外的代碼退出且不列印 JSON 決策的 hook 不阻止：Claude Code 顯示其 stderr 並應用切換，如 [其他退出代碼](https://code.claude.com/docs/zh-TW/hooks#other-exit-codes) 下所述。

### PostModelSwitch

在工作階段的模型變更後執行。使用它來給予 Claude 模型特定指導，而不編輯每個 CLAUDE.md，例如僅在某些模型上適用的組織範圍指令。 PostModelSwitch 需要 Claude Code v2.1.251 或更新版本。它無法阻止，因為模型已變更。Claude Code 在這些變更後執行 PostModelSwitch hooks：

- 您或用戶端請求的切換
- [自動模型回退](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)，改變工作階段的模型
- 設定（例如 [`opusplan`](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting)）進入或離開計畫模式
- Claude Code 恢復工作階段時恢復模型

當 [回退模型鏈](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains) 中的模型服務回合時，Claude Code 不執行 PostModelSwitch hooks，因為該替換持續一個回合並保持工作階段的模型不變。 匹配器遵循與 [PreModelSwitch](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 相同的規則：Claude Code 根據工作階段切換到的模型的規範名稱比較它。 此範例在工作階段的模型變更為任何 Opus 模型時新增指導：

```
{
  "hooks": {
    "PostModelSwitch": [
      {
        "matcher": ".*opus.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'On Opus, delegate implementation work to subagents and keep this conversation for planning and review.'"
          }
        ]
      }
    ]
  }
}

```

若要確認 hook 有效，從執行不同模型的工作階段切換到 Opus 模型，例如從 Sonnet 工作階段執行 `/model opus`，然後詢問 Claude 它對目前模型有什麼指導。

#### PostModelSwitch 輸入

PostModelSwitch hooks 接收與 [PreModelSwitch](https://code.claude.com/docs/zh-TW/hooks#premodelswitch-input) 相同的欄位，其中 `hook_event_name` 設定為 `"PostModelSwitch"` 和兩個更多 `source` 值：`"auto"` 用於自動回退或 Claude Code 自己進行的其他變更，`"resume"` 用於恢復工作階段時恢復的模型。 當 `source` 為 `"auto"` 時 `requested_model` 為 `null`。當 `source` 為 `"resume"` 時，它是 Claude Code 恢復的儲存模型設定。

#### PostModelSwitch 決策控制

Claude Code 在下一個切換後的請求中採用您的 hook 的 [純文字 stdout](https://code.claude.com/docs/zh-TW/hooks#exit-code-0) 退出 0，或 JSON 輸出中的 `additionalContext`，並將其傳遞給 Claude。除了所有 hooks 可用的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output) 外，您可以返回：

| 欄位                                                                                                                                                                                 | 描述                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `additionalContext`                                                                                                                                                                  | 與下一個請求一起新增到 Claude 背景資訊的字串。請參閱 [為 Claude 新增背景資訊](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude) |
| 如果 hook 在您發送下一個提示後五秒內未完成，Claude Code 發送該請求而不輸出，並改為將其附加到下一個請求。如果模型在下一個請求之前變更多次，Claude Code 僅傳遞最後切換目標模型的輸出。 |                                                                                                                                                |

### SessionEnd

在 Claude Code 工作階段結束時執行。適用於清理任務、記錄工作階段統計資訊或儲存工作階段狀態。支援匹配器以按退出原因篩選。 `reason` 欄位在 hook 輸入中指示工作階段為什麼結束：

| 原因                          | 描述                                                                         |
| ----------------------------- | ---------------------------------------------------------------------------- |
| `clear`                       | 使用 `/clear` 命令清除工作階段                                               |
| `resume`                      | 透過互動式 `/resume` 切換工作階段                                            |
| `logout`                      | 使用者登出                                                                   |
| `prompt_input_exit`           | 使用者在提示輸入可見時退出                                                   |
| `other`                       | 其他退出原因                                                                 |
| `bypass_permissions_disabled` | 在 v2.1.234 中移除；Claude Code 不發送它。從您的 `SessionEnd` 匹配器中刪除它 |

#### SessionEnd 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，SessionEnd hooks 還會接收指示工作階段為什麼結束的 `reason` 欄位。請參閱上面的 [原因表](https://code.claude.com/docs/zh-TW/hooks#sessionend) 以了解所有值。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SessionEnd",
  "reason": "other"
}

```

SessionEnd hooks 沒有決策控制。它們無法阻止工作階段終止，但可以執行清理任務。Claude Code 捨棄它們的 [JSON 輸出欄位](https://code.claude.com/docs/zh-TW/hooks#json-output)，例如 `systemMessage`。 SessionEnd hooks 的預設逾時為 1.5 秒。它在您退出、執行 `/clear` 或使用互動式 `/resume` 切換工作階段時適用。您可以透過兩種方式給予 hook 更多時間：

- **每個 hook`timeout`** ：在該 hook 的設定中設定 `timeout`。整體預算自動上升以符合您設定檔中最高每個 hook `timeout`，最多 60 秒。如果您以這種方式提高預算，沒有自己 `timeout` 的 hook 仍保持預設。在外掛提供的 hooks 上設定的逾時不提高預算。
- **`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`**：以毫秒設定此環境變數以明確覆寫預算。您設定的值也成為每個沒有自己`timeout` 的 hook 的逾時。

此範例將預算設定為 5 秒：

```
CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS=5000 claude

```

在 v2.1.268 之前，`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` 僅提高整體預算，沒有自己 `timeout` 的 hook 仍在 1.5 秒後被取消。

### Elicitation

在 MCP 伺服器在任務中期請求使用者輸入時執行。預設情況下，Claude Code 為使用者顯示互動式對話以回應。Hooks 可以攔截此請求並以程式設計方式回應，完全跳過對話。 匹配器欄位根據 MCP 伺服器名稱匹配。

#### Elicitation 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，Elicitation hooks 還會接收 `mcp_server_name`、`message` 和可選的 `mode`、`url`、`elicitation_id` 和 `requested_schema` 欄位。 對於表單模式引出，最常見的情況：

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Elicitation",
  "mcp_server_name": "my-mcp-server",
  "message": "Please provide your credentials",
  "mode": "form",
  "requested_schema": {
    "type": "object",
    "properties": {
      "username": { "type": "string", "title": "Username" }
    }
  }
}

```

對於 URL 模式引出，用於基於瀏覽器的驗證：

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Elicitation",
  "mcp_server_name": "my-mcp-server",
  "message": "Please authenticate",
  "mode": "url",
  "url": "https://auth.example.com/login"
}

```

#### Elicitation 輸出

若要以程式設計方式回應而不顯示對話，請返回具有 `hookSpecificOutput` 的 JSON 物件：

```
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": {
      "username": "alice"
    }
  }
}

```

| 欄位                                                                                                                                                                                 | 值                            | 描述                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------------------- |
| `action`                                                                                                                                                                             | `accept`、`decline`、`cancel` | 是否接受、拒絕或取消請求                             |
| `content`                                                                                                                                                                            | object                        | 要提交的表單欄位值。僅在 `action` 為 `accept` 時使用 |
| 退出代碼 2 拒絕引出。Claude Code 不在任何地方顯示您的 stderr 訊息。 Claude Code 作用於 Elicitation hook 的 JSON 輸出中的 `hookSpecificOutput` 並捨棄 `systemMessage` 和 `continue`。 |                               |                                                      |

### ElicitationResult

在使用者回應 MCP 引出後執行。Hooks 可以觀察、修改或阻止回應，然後將其發送回 MCP 伺服器。 匹配器欄位根據 MCP 伺服器名稱匹配。

#### ElicitationResult 輸入

除了 [常見輸入欄位](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 外，ElicitationResult hooks 還會接收 `mcp_server_name`、`action` 和可選的 `mode`、`elicitation_id` 和 `content` 欄位。

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "ElicitationResult",
  "mcp_server_name": "my-mcp-server",
  "action": "accept",
  "content": { "username": "alice" },
  "mode": "form",
  "elicitation_id": "elicit-123"
}

```

#### ElicitationResult 輸出

若要覆寫使用者的回應，請返回具有 `hookSpecificOutput` 的 JSON 物件：

```
{
  "hookSpecificOutput": {
    "hookEventName": "ElicitationResult",
    "action": "decline",
    "content": {}
  }
}

```

| 欄位                                                                                                                                                                                                                   | 值                            | 描述                                               |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | -------------------------------------------------- |
| `action`                                                                                                                                                                                                               | `accept`、`decline`、`cancel` | 覆寫使用者的動作                                   |
| `content`                                                                                                                                                                                                              | object                        | 覆寫表單欄位值。僅在 `action` 為 `accept` 時有意義 |
| 退出代碼 2 阻止回應，將有效動作變更為 `decline`。Claude Code 不在任何地方顯示您的 stderr 訊息。 Claude Code 作用於 ElicitationResult hook 的 JSON 輸出中的 `hookSpecificOutput` 並捨棄 `systemMessage` 和 `continue`。 |                               |                                                    |

## 基於提示的 hooks

除了命令、HTTP 和 MCP tool hooks 外，Claude Code 還支援基於提示的 hooks（`type: "prompt"`），使用 LLM 評估是否允許或阻止操作，以及代理 hooks（`type: "agent"`），生成具有工具存取權限的代理驗證器。並非所有事件都支援每種 hook 類型。 支援所有五種 hook 類型（`command`、`http`、`mcp_tool`、`prompt` 和 `agent`）的事件：

- `PermissionDenied`
- `PermissionRequest`
- `PostToolBatch`
- `PostToolUse`
- `PostToolUseFailure`
- `PreToolUse`
- `Stop`
- `SubagentStop`
- `TaskCompleted`
- `TaskCreated`
- `TeammateIdle`
- `UserPromptExpansion`
- `UserPromptSubmit`

支援 `command`、`http` 和 `mcp_tool` hooks 但不支援 `prompt` 或 `agent` 的事件：

- `ConfigChange`
- `CwdChanged`
- `DirectoryAdded`
- `Elicitation`
- `ElicitationResult`
- `FileChanged`
- `InstructionsLoaded`
- `MessageDisplay`
- `Notification`
- `PostCompact`
- `PostModelSwitch`
- `PreCompact`
- `PreModelSwitch`
- `SessionEnd`
- `StopFailure`
- `SubagentStart`
- `WorktreeCreate`
- `WorktreeRemove`

`SessionStart` 和 `Setup` 支援 `command` 和 `mcp_tool` hooks，而 [MCP tool hook 欄位](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields)描述了它們的 `mcp_tool` hooks 何時執行。它們不支援 `http`、`prompt` 或 `agent` hooks。

### 基於提示的 hooks 如何工作

基於提示的 hooks 不執行 Bash 命令，而是：

1. 將 hook 輸入和您的提示發送到 Claude 模型，預設為 Haiku
1. LLM 以包含決定的結構化 JSON 回應
1. Claude Code 自動處理決定

### 提示 hook 配置

將 `type` 設定為 `"prompt"` 並提供 `prompt` 字串而不是 `command`。使用 `$ARGUMENTS` 佔位符將 hook 的 JSON 輸入資料注入到您的提示文字中。 此 `Stop` hook 詢問 LLM 在允許 Claude 完成之前是否應該停止：

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete."
          }
        ]
      }
    ]
  }
}

```

| 欄位              | 必需 | 描述                                                                                                                                                                                          |
| ----------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`            | 是   | 必須為 `"prompt"`                                                                                                                                                                             |
| `prompt`          | 是   | 要發送到 LLM 的提示文字。使用 `$ARGUMENTS` 作為 hook 輸入 JSON 的佔位符。如果 `$ARGUMENTS` 不存在，輸入 JSON 會附加到提示                                                                     |
| `model`           | 否   | 用於評估的模型。預設為快速模型                                                                                                                                                                |
| `timeout`         | 否   | 逾時（秒）。預設值：30                                                                                                                                                                        |
| `continueOnBlock` | 否   | 在適用的事件上，`true` 將 `ok: false` 原因反饋給 Claude 並繼續而不是結束轉換。預設值：`false`。請參閱[回應架構](https://code.claude.com/docs/zh-TW/hooks#response-schema)以了解每個事件的行為 |

### 回應架構

LLM 必須以包含以下內容的 JSON 回應：

```
{
  "ok": true | false,
  "reason": "Explanation for the decision",
  "impossible": true | false
}

```

| 欄位                                 | 描述                                                                                                                                                                   |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ok`                                 | `true` 允許操作。`false` 時，請參閱下面的每個事件行為                                                                                                                  |
| `reason`                             | 當 `ok` 為 `false` 時必需                                                                                                                                              |
| `impossible`                         | 選用。當模型判斷條件永遠無法滿足時，模型會以 `ok: false` 返回它。在 `Stop` 和 `SubagentStop` 上，Claude Code 會讓轉換結束而不是反饋原因。代理 hooks 和其他事件會忽略它 |
| `ok: false` 時發生的情況取決於事件： |                                                                                                                                                                        |

- `Stop` 和 `SubagentStop`：原因被反饋給 Claude 作為其下一個指令，轉換繼續，除非回應也設定 `impossible: true`，在這種情況下 Claude Code 允許停止，轉換結束
- `PreToolUse`：工具呼叫被拒絕；預設情況下轉換結束，拒絕原因在聊天中顯示為警告行。設定 `continueOnBlock: true` 以改為將原因作為工具錯誤返回給 Claude，使其可以調整並繼續，相當於命令 hook 的 `permissionDecision: "deny"`。在 v2.1.210 之前，拒絕原因被作為工具錯誤返回給 Claude，轉換繼續
- `PostToolUse`：預設情況下轉換結束，原因在聊天中顯示為警告行。設定 `continueOnBlock: true` 以將原因反饋給 Claude 並繼續轉換
- `PostToolBatch`、`UserPromptSubmit` 和 `UserPromptExpansion`：轉換結束，原因顯示為警告行。這些事件在 `decision: "block"` 上結束轉換，無論 `continue` 如何
- `PostToolUseFailure` 和 `TaskCreated`：原因作為工具錯誤返回給 Claude，轉換繼續，無論 `continueOnBlock` 如何
- `TaskCompleted`：當它因為任務在轉換期間被標記為完成而觸發時，原因作為工具錯誤返回給 Claude，轉換繼續，無論 `continueOnBlock` 如何。當它因為隊友停止而觸發時，它的行為類似 `TeammateIdle` 並預設停止隊友
- `TeammateIdle`：預設情況下隊友停止，原因顯示為警告行。設定 `continueOnBlock: true` 以將原因反饋給隊友並保持其工作狀態
- `PermissionRequest`：`ok: false` 沒有效果。要從 hook 拒絕批准，請使用[命令 hook](https://code.claude.com/docs/zh-TW/hooks#command-hook-fields)返回 `hookSpecificOutput.decision.behavior: "deny"`
- `PermissionDenied`：`ok: false` 沒有效果，因為拒絕已經發生。此事件讀取的唯一輸出是 `hookSpecificOutput.retry`，提示和代理 hooks 無法設定。它們在此事件上執行，但其輸出被丟棄。使用[命令 hook](https://code.claude.com/docs/zh-TW/hooks#command-hook-fields)返回 `retry`

如果您需要對任何事件進行更精細的控制，請使用[命令 hook](https://code.claude.com/docs/zh-TW/hooks#command-hook-fields)，其中包含[決定控制](https://code.claude.com/docs/zh-TW/hooks#decision-control)中描述的每個事件欄位。

### 在停止前檢查多個條件

此 `Stop` hook 使用詳細提示在允許 Claude 停止之前檢查三個條件。`SubagentStop` hooks 使用相同的格式來評估 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 是否應該停止。如果模型因為條件尚未滿足而返回 `"ok": false`，Claude 繼續工作，提供的原因作為其下一個指令：

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "You are evaluating whether Claude should stop working. Context: $ARGUMENTS\n\nAnalyze the conversation and determine if:\n1. All user-requested tasks are complete\n2. Any errors need to be addressed\n3. Follow-up work is needed\n\nRespond with JSON: {\"ok\": true} to allow stopping, or {\"ok\": false, \"reason\": \"your explanation\"} to continue working.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}

```

## 基於代理的 hooks

代理 hooks 是實驗性的。行為和配置可能在未來版本中變更。對於生產工作流程，建議使用[命令 hooks](https://code.claude.com/docs/zh-TW/hooks#command-hook-fields)。 基於代理的 hooks（`type: "agent"`）類似於基於提示的 hooks，但具有多輪工具存取。代理 hook 不是單一 LLM 呼叫，而是生成一個可以讀取檔案、搜尋程式碼和檢查程式碼庫以驗證條件的 subagent。代理 hooks 支援與基於提示的 hooks 相同的事件。

### 代理 hooks 如何工作

當代理 hook 觸發時：

1. Claude Code 生成一個 subagent，使用您的提示和 hook 的 JSON 輸入
1. Subagent 可以使用 Read、Grep 和 Glob 等工具進行調查
1. 在最多 50 輪後，subagent 返回結構化的 `{ "ok": true/false }` 決定
1. Claude Code 允許該動作（如果 `ok` 是 `true`）。如果 `ok` 是 `false`，Claude Code 會以與提示 hook 相同的方式處理阻止，該提示 hook 在該事件上具有 `continueOnBlock: true`，如[回應架構](https://code.claude.com/docs/zh-TW/hooks#response-schema)下所列

代理 hooks 在驗證需要檢查實際檔案或測試輸出時很有用，而不僅僅是評估 hook 輸入資料。

### 代理 hook 配置

將 `type` 設定為 `"agent"` 並提供 `prompt` 字串，使用 `$ARGUMENTS` 作為 hook 輸入 JSON 的佔位符。配置欄位與[提示 hooks](https://code.claude.com/docs/zh-TW/hooks#prompt-hook-configuration) 相同，除了代理 hooks 具有更長的預設逾時 60 秒，且沒有 `continueOnBlock` 欄位。 回應架構是 `{ "ok": true }` 允許或 `{ "ok": false, "reason": "..." }` 阻止。在 `ok: false` 時，Claude Code 會以處理[提示 hook 且具有 `continueOnBlock: true`](https://code.claude.com/docs/zh-TW/hooks#response-schema) 的相同方式處理代理 hook；代理 hooks 沒有 `continueOnBlock` 欄位，且不支援提示 hook 的 `impossible` 欄位。 此 `Stop` hook 驗證所有單元測試通過，然後允許 Claude 完成：

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

## 在背景執行 hooks

預設情況下，hooks 會阻止 Claude 的執行，直到它們完成。對於長時間執行的任務，如部署、測試套件或外部 API 呼叫，設定 `"async": true` 以在背景執行 hook，同時 Claude 繼續工作。非同步 hooks 無法阻止或控制 Claude 的行為：回應欄位，如 `decision`、`permissionDecision` 和 `continue` 沒有效果，因為它們會控制的操作已經完成。

### 配置非同步 hook

將 `"async": true` 新增到命令 hook 的配置以在背景執行它而不阻止 Claude。此欄位僅在 `type: "command"` hooks 上可用。 此 hook 在每個 `Write` 工具呼叫後執行測試指令碼。Claude 立即繼續工作，同時 `run-tests.sh` 執行。當指令碼完成時，其輸出在下一個對話輪次上傳遞：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/run-tests.sh",
            "async": true
          }
        ]
      }
    ]
  }
}

```

一旦非同步 hook 在背景執行，Claude Code 不會對其強制執行 `timeout`。Claude Code 仍然會對使用 `asyncRewake` 執行的 hook 強制執行 `timeout`。 Claude Code 只在工作階段執行時傳遞非同步 hook 的結果：

- 在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p` 旗標，Claude Code 會在清理時終止任何仍在執行的非同步 hook，並以 `cancelled` 結果完成它
- 如果你的 hook 工作必須超越 `claude -p` 工作階段，請從它啟動一個完全分離的程序

### 非同步 hooks 如何執行

當非同步 hook 觸發時，Claude Code 啟動 hook 程序並立即繼續，而不等待它完成。Hook 在 stdin 上接收與同步 hook 相同的 JSON 輸入。 背景程序退出後，Claude Code 會在下一個對話輪次將 hook 的 JSON 回應中的 `additionalContext` 和 `systemMessage` 欄位傳遞給 Claude。與同步 hook 的 `systemMessage` 不同，這兩個欄位都不會顯示給你。 Claude Code 驗證該 JSON 回應是否符合與同步 hooks 相同的[輸出結構](https://code.claude.com/docs/zh-TW/hooks#json-output)，並捨棄任何值類型錯誤的欄位，例如不是字串的 `systemMessage`，而不是傳遞它。使用 `--debug` 執行以查看命名每個捨棄欄位的警告。在 v2.1.202 之前，來自非同步 hook 的格式不正確的 JSON 輸出可能會導致工作階段崩潰，每次恢復工作階段時都會重複發生崩潰。 非同步 hook 完成通知預設被抑制。要查看它們，請使用 `Ctrl+O` 啟用詳細模式或使用 `--verbose` 啟動 Claude Code。

### 檔案變更後執行測試

此 hook 在 Claude 寫入檔案時在背景啟動測試套件，然後在測試完成時將結果報告回 Claude。將此指令碼儲存到專案中的 `.claude/hooks/run-tests-async.sh` 並使用 `chmod +x` 使其可執行：

```
#!/bin/bash
# run-tests-async.sh

# 從 stdin 讀取 hook 輸入
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# 僅針對原始檔案執行測試
if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.js ]]; then
  exit 0
fi

# 執行測試並通過 additionalContext 報告結果給 Claude
RESULT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  MSG="Tests passed after editing $FILE_PATH"
else
  MSG="Tests failed after editing $FILE_PATH: $RESULT"
fi
jq -nc --arg msg "$MSG" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'

```

然後將此配置新增到專案根目錄中的 `.claude/settings.json`。`async: true` 旗標讓 Claude 在測試執行時繼續工作：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/run-tests-async.sh",
            "args": [],
            "async": true
          }
        ]
      }
    ]
  }
}

```

### 限制

非同步 hooks 與同步 hooks 相比有額外的限制：

- Hook 輸出在下一個對話輪次上傳遞。如果工作階段閒置，回應會等待直到下一個使用者互動。例外：退出代碼為 2 的 `asyncRewake` hook 即使在工作階段閒置時也會立即喚醒 Claude。
- 每次執行都會建立一個單獨的背景程序。同一非同步 hook 的多次觸發之間沒有去重。

## 安全考慮

### 免責聲明

命令 hooks 以您的完整使用者權限執行 shell 命令。它們可以修改、刪除或存取您的使用者帳戶可以存取的任何檔案。在將任何 hook 命令新增到您的設定之前，請審查並測試它們。

### 工作區信任

Claude Code 在執行任何來自設定檔的 hook 之前會檢查工作區信任。什麼算作受信任取決於工作階段類型：

- **互動式工作階段** ：Claude Code 會保留來自每個設定檔的 hooks，包括您自己的 `~/.claude/settings.json`，直到您接受該資料夾的[工作區信任對話框](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)，或接受其信任延伸到該資料夾的父目錄
- **`-p`或 SDK 工作階段** ：Claude Code 不會顯示對話框，並將該資料夾視為受信任，因此儲存庫 `.claude/settings.json` 中提交的 hooks 會在您從未信任過的資料夾中執行

在您對儲存庫執行 `claude -p` 之前，如果您沒有編寫該儲存庫，請審查其 `.claude/` 設定檔，使用 [`--bare`](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode) 開始，或[為該執行關閉 hooks](https://code.claude.com/docs/zh-TW/hooks#disable-or-remove-hooks)，使用 `--settings '{"disableAllHooks": true}'`。專案子代理中的 Frontmatter hooks 遵循比設定檔 hooks 更嚴格的規則。[在您信任資料夾之前執行的內容](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)按工作階段類型列出每種儲存庫內容。

### 安全最佳實踐

編寫 hooks 時，請記住這些實踐：

- **驗證和清理輸入** ：永遠不要盲目信任輸入資料
- **始終引用 shell 變數** ：使用 `"$VAR"` 而不是 `$VAR`
- **阻止路徑遍歷** ：檢查檔案路徑中的 `..`
- **使用絕對路徑** ：為指令碼指定完整路徑。在 exec 形式中，使用 `${CLAUDE_PROJECT_DIR}` 且路徑不需要引用。在 shell 形式中，將其包裝在雙引號中
- **跳過敏感檔案** ：避免 `.env`、`.git/`、金鑰等

## Windows PowerShell 工具

在 Windows 上，您可以通過在命令 hook 上設定 `"shell": "powershell"` 在 PowerShell 中執行個別 hooks。Claude Code 自動偵測 `pwsh.exe`（PowerShell 7 及更新版本的可執行檔），並回退到 `powershell.exe`（Windows PowerShell 5.1）。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "command": "Write-Host 'File written'"
          }
        ]
      }
    ]
  }
}

```

若要從 PowerShell shell 形式命令參考專案根目錄，請寫入 `${CLAUDE_PROJECT_DIR}` 或 `$env:CLAUDE_PROJECT_DIR`。自 v2.1.198 起，Claude Code 會在 PowerShell shell 形式命令中將 `${CLAUDE_PROJECT_DIR}`、`${CLAUDE_PLUGIN_ROOT}` 和 `${CLAUDE_PLUGIN_DATA}` 佔位符重寫為 PowerShell 的 `${env:NAME}` 形式，無論 hook 是在 `settings.json`、plugin 或 skill 中定義。PowerShell 會在解析後從匯出的環境中解析該值，因此佔位符在雙引號字串內有效，但在單引號字串內無效，因為 PowerShell 永遠不會在單引號字串中展開變數。 在 v2.1.198 之前，此重寫僅適用於 plugin hooks。在較早的版本上，`settings.json` hook 需要 `$env:` 形式或 [exec 形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)，其中 `${CLAUDE_PROJECT_DIR}` 會在每個 `args` 元素中被替換，無論 hook 在何處定義。 不要在 PowerShell hook 中寫入裸露的 `$CLAUDE_PROJECT_DIR` 拼寫。PowerShell 會將其解析為未定義的本機變數，並將其解析為 `$null`，這會導致指令碼路徑沒有其專案根目錄前綴。Claude Code 不會重寫該形式；它會在 [debug log](https://code.claude.com/docs/zh-TW/hooks#debug-hooks) 中記錄警告。 下面的範例顯示了一個 `settings.json` hook，它使用 `$env:` 形式執行專案指令碼，該形式在每個版本上都有效：

```
{
  "type": "command",
  "shell": "powershell",
  "command": "& \"$env:CLAUDE_PROJECT_DIR\\.claude\\hooks\\check.ps1\""
}

```

## 偵錯 hooks

Hook 執行詳細資訊被寫入偵錯日誌檔案。使用 `claude --debug-file <path>` 啟動 Claude Code 以將日誌寫入已知位置，或執行 `claude --debug` 並在 `~/.claude/debug/<session-id>.txt` 讀取日誌。`--debug` 標誌不列印到終端。 例如，在 `Write` 上的 `PostToolUse` hook，其命令列印 `hook-ran` 會產生如下項目：

```
2026-07-19T02:03:24.382Z [DEBUG] Hook output does not start with {, treating as plain text
2026-07-19T02:03:24.382Z [DEBUG] "Hook PostToolUse:Write (PostToolUse) success:\nhook-ran"

```

有關更細粒度的 hook 匹配詳細資訊，設定 `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` 以查看額外的日誌行，例如 hook 匹配器計數和查詢匹配。 有關故障排除常見問題，如 hooks 不觸發、Stop hooks 持續阻擋或配置錯誤，請參閱指南中的 [限制和故障排除](https://code.claude.com/docs/zh-TW/hooks-guide#limitations-and-troubleshooting)。有關涵蓋 `/context`、`/doctor` 和設定優先順序的更廣泛診斷逐步解說，請參閱 [偵錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config)。 是否 Assistant Responses are generated using AI and may contain mistakes.
