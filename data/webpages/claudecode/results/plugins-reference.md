想要安裝 plugins？請參閱 [探索和安裝 plugins](https://code.claude.com/docs/zh-TW/discover-plugins)。如需建立 plugins，請參閱 [Plugins](https://code.claude.com/docs/zh-TW/plugins)。如需發佈 plugins，請參閱 [Plugin 市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)。 **plugin** 是一個自包含的目錄，包含擴展 Claude Code 功能的元件。Plugin 元件包括 skills、agents、hooks、MCP servers、LSP servers 和 monitors。

## Plugin 元件參考

### Skills

Plugins 會將 skills 新增至 Claude Code，建立 `/name` 快捷方式供您或 Claude 叫用。 **位置** ：plugin 根目錄中的 `skills/` 或 `commands/` 目錄，或 plugin 根目錄中的單一 `SKILL.md` 檔案 **檔案格式** ：Skills 是包含 `SKILL.md` 的目錄；commands 是簡單的 markdown 檔案 **Skill 結構** ：

```
skills/
├── pdf-processor/
│   ├── SKILL.md
│   ├── reference.md (optional)
│   └── scripts/ (optional)
└── code-reviewer/
    └── SKILL.md

```

當 plugin 安裝時，Skills 和 commands 會自動被發現。 如果 plugin 沒有 `skills/` 目錄且沒有 `skills` manifest 欄位，plugin 根目錄中的 `SKILL.md` 會被載入為單一 skill。設定 frontmatter `name` 欄位以控制 skill 的叫用名稱。沒有設定的話，Claude Code 會回退到安裝目錄名稱。對於 [複製到快取中](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution) 的 plugin，該名稱是一個在每次更新時都會改變的版本字串。對於提供多個 skills 的 plugins，請使用上面所示的 `skills/` 目錄配置。 在 plugin skills 和 commands 中，Boolean frontmatter 欄位（例如 `disable-model-invocation`）接受 `yes`、`no`、`on`、`off`、`1` 和 `0`（任何字母大小寫），以及 `true` 和 `false`。在 v2.1.218 之前，Claude Code 只識別 `true` 和 `false`。 如需完整詳細資訊，請參閱 [Skills](https://code.claude.com/docs/zh-TW/skills)。

### Agents

Plugins 可以提供專門的子代理程式來執行特定任務，Claude 可以在適當時自動叫用。 **位置** ：plugin 根目錄中的 `agents/` 目錄 **檔案格式** ：描述代理程式功能的 Markdown 檔案 **Agent 結構** ：

```
---
name: agent-name
description: What this agent specializes in and when Claude should invoke it
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
---

Detailed system prompt for the agent describing its role, expertise, and behavior.

```

Plugin agents 支援 `name`、`description`、`model`、`effort`、`maxTurns`、`tools`、`disallowedTools`、`skills`、`memory`、`background`、[`omitClaudeMd`](https://code.claude.com/docs/zh-TW/sub-agents#supported-frontmatter-fields) 和 `isolation` frontmatter 欄位。唯一有效的 `isolation` 值是 `"worktree"`。基於安全考量，plugin 提供的 agents 不支援 `hooks`、`mcpServers` 和 `permissionMode`。 Claude Code 會載入 plugin agent，即使其 frontmatter 沒有 `name` 或無法解析：

- 沒有 `name`：Claude Code 會根據檔案名稱為 agent 命名，所以名為 `my-plugin` 的 plugin 中的 `agents/reviewer.md` 會載入為 `my-plugin:reviewer`
- 無法解析的 Frontmatter：Claude Code 會根據檔案名稱為 agent 命名，使用 `Agent from my-plugin plugin` 作為其描述，並忽略檔案中的每個欄位

相比之下，Claude Code 會跳過其 frontmatter 沒有 `name` 或無法解析的專案、使用者或受管理的 agent 檔案。 若要找到 plugin 預設 `agents/` 目錄中 frontmatter 無法解析的檔案，請執行 `claude plugin validate`。您傳遞的路徑取決於 plugin 是否有 manifest，兩個範例都使用 `./my-plugin` 作為 plugin 目錄：

- 具有 manifest 的 plugin：`claude plugin validate ./my-plugin`
- 沒有 manifest 的 plugin：`claude plugin validate ./my-plugin/agents`。需要 Claude Code v2.1.233 或更新版本。

Agents 會在 [@-mention 類型提前](https://code.claude.com/docs/zh-TW/sub-agents#invoke-subagents-explicitly) 中以其範圍名稱（例如 `my-plugin:code-reviewer`）出現，一旦 plugin 被啟用。 如需完整詳細資訊，請參閱 [Subagents](https://code.claude.com/docs/zh-TW/sub-agents)。

### Hooks

Plugins 可以提供事件處理程式，自動回應 Claude Code 事件。 **位置** ：plugin 根目錄中的 `hooks/hooks.json`，或 plugin.json 中的內聯 **格式** ：具有事件匹配器和動作的 JSON 設定 `hooks/hooks.json` 可以攜帶頂層 `$schema` 金鑰，該金鑰命名 JSON Schema URL 以供編輯器自動完成和驗證。Claude Code 在載入時會忽略該金鑰。 **Hook 設定** ：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}

```

Plugin hooks 回應與 [使用者定義的 hooks](https://code.claude.com/docs/zh-TW/hooks) 相同的生命週期事件：

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
| **Hook 類型** ：      |                                                                                                                                                                                 |

- `command`：執行 shell 命令或指令碼
- `http`：將事件 JSON 作為 POST 請求傳送到 URL
- `mcp_tool`：在已設定的 [MCP server](https://code.claude.com/docs/zh-TW/mcp) 上呼叫工具
- `prompt`：使用 LLM 評估提示（使用 `$ARGUMENTS` 預留位置作為內容）
- `agent`：執行具有工具的代理程式驗證器以進行複雜驗證任務

針對 plugin 自己的 [bundled MCP server](https://code.claude.com/docs/zh-TW/plugins-reference#mcp-servers) 的 Hooks 必須使用其範圍名稱。工具匹配器和 `if` 欄位採用範圍工具名稱 `mcp__plugin_<plugin-name>_<server-name>__<tool>`，而 `mcp_tool` hook 的 `server` 欄位採用 `plugin:<plugin-name>:<server-name>`。針對裸伺服器金鑰編寫的匹配器永遠不會觸發。請參閱 [Match MCP tools](https://code.claude.com/docs/zh-TW/hooks#match-mcp-tools) 和 [Plugin-provided MCP servers](https://code.claude.com/docs/zh-TW/mcp#plugin-provided-mcp-servers)。

### MCP servers

Plugins 可以捆綁 Model Context Protocol (MCP) 伺服器，以將 Claude Code 與外部工具和服務連接。 **位置** ：plugin 根目錄中的 `.mcp.json`，或 plugin.json 中的內聯 **格式** ：標準 MCP 伺服器設定 **MCP 伺服器設定** ：

```
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data"
      }
    },
    "plugin-api-client": {
      "command": "npx",
      "args": ["@company/mcp-server", "--plugin-mode"]
    }
  }
}

```

**整合行為** ：

- Plugin MCP 伺服器在 plugin 啟用時自動啟動
- 伺服器在 Claude 的工具組中顯示為標準 MCP 工具
- Plugin 伺服器可以獨立於使用者 MCP 伺服器進行設定
- 如果您在工作階段中執行 [`/reload-plugins`](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)，Claude Code 會保持其設定未變更的伺服器的即時連接

### LSP servers

尋找使用 LSP plugins？從官方 marketplace 安裝它們：在 `/plugin` Discover 標籤中搜尋「lsp」。本節記錄如何為官方 marketplace 未涵蓋的語言建立 LSP plugins。 Plugins 可以提供 [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) (LSP) 伺服器，以在處理您的程式碼庫時為 Claude 提供 [即時程式碼智慧](https://code.claude.com/docs/zh-TW/discover-plugins#code-intelligence)。 **位置** ：plugin 根目錄中的 `.lsp.json`，或 `plugin.json` 中的內聯 **格式** ：將語言伺服器名稱對應到其設定的 JSON 設定 **`.lsp.json`檔案格式** ：

```
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}

```

**在`plugin.json` 中內聯**：

```
{
  "name": "my-plugin",
  "lspServers": {
    "go": {
      "command": "gopls",
      "args": ["serve"],
      "extensionToLanguage": {
        ".go": "go"
      }
    }
  }
}

```

**必需欄位：**

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 描述                                                                                                                              |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 要執行的 LSP 二進位檔（必須在 PATH 中）                                                                                           |
| `extensionToLanguage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 將檔案副檔名對應到語言識別碼                                                                                                      |
| **選用欄位：**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                                                                                   |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 描述                                                                                                                              |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ---                                                                                                                               |
| `args`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | LSP 伺服器的命令列引數                                                                                                            |
| `transport`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 通訊傳輸：`stdio`（預設）或 `socket`。Claude Code 接受 `socket` 但在 stdio 上執行每個伺服器，因此 stdout 協定規則適用於所有伺服器 |
| `env`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 啟動伺服器時要設定的環境變數                                                                                                      |
| `initializationOptions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 在初始化期間傳遞給伺服器的選項                                                                                                    |
| `settings`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 透過 `workspace/didChangeConfiguration` 傳遞的設定                                                                                |
| `workspaceFolder`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 伺服器的工作區資料夾路徑                                                                                                          |
| `startupTimeout`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 等待伺服器啟動的最長時間（毫秒）                                                                                                  |
| `shutdownTimeout`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 等待正常關閉的最長時間（毫秒）。當逾時時間過去時，Claude Code 會終止伺服器程序。未設定時，不適用逾時                              |
| `restartOnCrash`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 伺服器當機後是否重新啟動。預設為 `true`。設定為 `false` 以保持當機的伺服器停止而不是重新啟動                                      |
| `maxRestarts`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 放棄前的最大重新啟動嘗試次數                                                                                                      |
| `diagnostics`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 編輯後是否將診斷推送到 Claude 的內容中（預設 `true`）。設定為 `false` 以保持程式碼導覽但抑制自動診斷注入                          |
| `restartOnCrash` 和 `shutdownTimeout` 需要 Claude Code v2.1.205 或更新版本。在 v2.1.205 之前，設定結構描述接受兩個選項，但設定其中任一個會導致 Claude Code 在啟動時完全跳過該 LSP 伺服器，原因只在 `claude --debug` 輸出中可見。 **同一副檔名的多個伺服器** ：當多個已啟用的 LSP 伺服器在 `extensionToLanguage` 中宣告相同的檔案副檔名時，無論伺服器來自一個 plugin 還是來自不同的 plugins，第一個註冊的伺服器會處理具有該副檔名的檔案，其他伺服器永遠不會啟動。`/plugin` 介面會顯示一個警告，命名其伺服器為作用中的 plugin。 **無法初始化的伺服器** ：Claude Code 會跳過其設定無效的伺服器，例如缺少 `command` 或 `extensionToLanguage` 的伺服器，其他已設定的伺服器仍會啟動。執行 `claude --debug` 以查看伺服器被跳過的原因。 被跳過的伺服器不會宣告其檔案副檔名，因此宣告相同副檔名的另一個有效伺服器（來自相同或不同的 plugin）仍會處理這些檔案。 **將日誌輸出傳送到 stderr，而不是 stdout** ：Claude Code 將伺服器的 stdout 讀取為協定訊息，並接受最多 64 KiB 的訊息標頭和最多 32 MiB 的訊息本文。Claude Code 會斷開超過任一限制或將非協定輸出寫入 stdout 的伺服器，並將斷開連接計為 `restartOnCrash` 和 `maxRestarts` 的當機。當您使用 `--debug` 執行時，Claude Code 會將命名原因的錯誤寫入偵錯日誌。 |                                                                                                                                   |
| **您必須單獨安裝語言伺服器二進位檔。** LSP plugins 設定 Claude Code 如何連接到語言伺服器，但它們不包括伺服器本身。如果您在 `/plugin` Errors 標籤中看到 `Executable not found in $PATH`，請為您的語言安裝所需的二進位檔。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                   |
| **可用的 LSP plugins：**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                   |
| Plugin                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 語言伺服器                                                                                                                        |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ---                                                                                                                               |
| `pyright-lsp`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Pyright (Python)                                                                                                                  |
| `typescript-lsp`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | TypeScript Language Server                                                                                                        |
| `rust-analyzer-lsp`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | rust-analyzer                                                                                                                     |
| 先安裝語言伺服器，然後從 marketplace 安裝 plugin。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                   |

### Monitors

Plugins 可以宣告背景監視器，Claude Code 在 plugin 啟用時自動啟動。每個監視器在工作階段的生命週期內執行 shell 命令，並將每個 stdout 行傳遞給 Claude 作為通知，因此 Claude 可以對日誌項目、狀態變更或輪詢事件做出反應，而無需被要求自己啟動監視。 Plugin monitors 使用與 [Monitor tool](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool) 相同的機制，並共享其可用性限制。它們僅在互動式 CLI 工作階段中執行，以與 [hooks](https://code.claude.com/docs/zh-TW/plugins-reference#hooks) 相同的信任層級在未沙箱化的環境中執行，並在 Monitor tool 不可用的主機上被跳過。 **位置** ：plugin 根目錄中的 `monitors/monitors.json`，或 plugin.json 中的內聯 **格式** ：監視器項目的 JSON 陣列 以下 `monitors/monitors.json` 監視部署狀態端點和本機錯誤日誌：

```
[
  {
    "name": "deploy-status",
    "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/poll-deploy.sh",
    "description": "Deployment status changes"
  },
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log",
    "when": "on-skill-invoke:debug"
  }
]

```

若要內聯宣告監視器，請在 `plugin.json` 中將 `experimental.monitors` 設定為相同的陣列。若要從非預設路徑載入，請將 `experimental.monitors` 設定為相對路徑字串，例如 `"./config/monitors.json"`。Monitors 是 [experimental component](https://code.claude.com/docs/zh-TW/plugins-reference#experimental-components)。 **必需欄位：**

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 描述                                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 在 plugin 中唯一的識別碼。防止 plugin 重新載入或再次叫用 skill 時的重複程序                                                                                       |
| `command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 在工作階段工作目錄中作為持久背景程序執行的 shell 命令                                                                                                             |
| `description`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 正在監視的內容的簡短摘要。顯示在工作面板和通知摘要中                                                                                                              |
| **選用欄位：**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                                                                                                                   |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 描述                                                                                                                                                              |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | ---                                                                                                                                                               |
| `when`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 控制監視器何時啟動。`"always"` 在工作階段啟動和 plugin 重新載入時啟動它，是預設值。`"on-skill-invoke:<skill-name>"` 在此 plugin 中的命名 skill 首次被分派時啟動它 |
| `command` 值支援 [路徑替換](https://code.claude.com/docs/zh-TW/plugins-reference#environment-variables) `${CLAUDE_PLUGIN_ROOT}`、`${CLAUDE_PLUGIN_DATA}` 和 `${CLAUDE_PROJECT_DIR}`，加上環境中的任何 `${ENV_VAR}`。如果指令碼需要從 plugin 自己的目錄執行，請在命令前加上 `cd "${CLAUDE_PLUGIN_ROOT}" && `。 Monitor `command` 無法參考 [`${user_config.*}`](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration) 值。命令透過 shell 執行，因此 Claude Code 會以 [error](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config) 拒絕監視器，而不是替換值。Monitor 程序不會接收 `CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數，因此讓監視器指令碼從它擁有的設定檔讀取值。 如果您在工作階段中停用 plugin，Claude Code 不會停止已在執行的監視器；它們在工作階段結束時停止。 |                                                                                                                                                                   |

### Themes

Plugins 可以提供顏色主題，這些主題在 `/theme` 中與內建預設值和使用者的本機主題一起出現。主題是 `themes/` 中的 JSON 檔案，具有 `base` 預設值和稀疏的 `overrides` 顏色權杖對應。Themes 是 [experimental component](https://code.claude.com/docs/zh-TW/plugins-reference#experimental-components)。

```
{
  "name": "Dracula",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "error": "#ff5555",
    "success": "#50fa7b"
  }
}

```

當使用者選擇 plugin 主題時，Claude Code 會在其設定中儲存 `custom:<plugin-name>:<slug>`。Plugin 主題是唯讀的：當使用者在 `/theme` 中按下 `Ctrl+E` 時，Claude Code 會將其複製到 `~/.claude/themes/` 中，以便他們可以編輯副本。

______________________________________________________________________

## Plugin 安裝範圍

當您安裝 plugin 時，您可以選擇一個**範圍** ，決定 plugin 在何處可用以及誰可以使用它：

| 範圍                                                                                                                                                                                                                                                                                          | 設定檔                                                                  | 使用案例                                                            |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `user`                                                                                                                                                                                                                                                                                        | `~/.claude/settings.json`                                               | 個人 plugin，可在所有專案中使用（預設）                             |
| `project`                                                                                                                                                                                                                                                                                     | `.claude/settings.json`                                                 | 透過版本控制共享的團隊 plugin                                       |
| `local`                                                                                                                                                                                                                                                                                       | `.claude/settings.local.json`                                           | 專案特定的 plugin，當 Claude Code 將設定儲存到其中時會被 gitignored |
| `managed`                                                                                                                                                                                                                                                                                     | [Managed settings](https://code.claude.com/docs/zh-TW/managed-settings) | 受管理的 plugin（唯讀，僅更新）                                     |
| Plugin 使用與其他 Claude Code 設定相同的範圍系統。如需安裝說明和範圍旗標，請參閱 [Install plugins](https://code.claude.com/docs/zh-TW/discover-plugins#install-plugins)。如需範圍的完整說明，請參閱 [Configuration scopes](https://code.claude.com/docs/zh-TW/settings#where-settings-live)。 |                                                                         |                                                                     |

______________________________________________________________________

## Skills-directory plugins

任何 skills 目錄下的資料夾，如果包含 `.claude-plugin/plugin.json` 清單，就會在下一個工作階段中以 `<name>@skills-dir` 的名稱載入為 plugin，無需市集且無需安裝步驟。使用 [`plugin init`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-init) 來建立一個。與複製的市集安裝不同，plugin 是在原地被發現而不是被複製到 plugin 快取中。 skills 目錄樹支援三種不同的東西：

| 你擁有的                                      | 它是什麼                                                               |
| --------------------------------------------- | ---------------------------------------------------------------------- |
| `<skills-dir>/foo/SKILL.md` 且沒有清單        | 一個名為 `foo` 的純 [skill](https://code.claude.com/docs/zh-TW/skills) |
| `<skills-dir>/foo/.claude-plugin/plugin.json` | 一個 plugin `foo@skills-dir`，可以捆綁自己的 skills、agents、hooks 等  |
| `<plugin>/skills/bar/SKILL.md`                | 一個 skill `bar` 打包在 plugin 內                                      |

### 選擇 plugin 從何處載入

| Skills 目錄                                                                                                                                                                                                                                               | 範圍 | 載入                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `~/.claude/skills/`                                                                                                                                                                                                                                       | 個人 | 在每個專案中，因為該位置只屬於你                                                                                                       |
| `<cwd>/.claude/skills/`                                                                                                                                                                                                                                   | 專案 | 只有在你接受該資料夾的工作區 [信任對話](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 後才會載入 |
| 專案範圍的 plugin 被簽入到儲存庫中，並到達每個複製它的協作者。因為該內容來自儲存庫而不是來自你，它只有在與 `.claude/settings.json` 中的專案允許規則相同的信任閘道後才會載入，所以信任父資料夾或使用 `-p` 執行是不夠的，執行程式碼的元件會受到進一步限制： |      |                                                                                                                                        |

- 它宣告的 MCP 伺服器會經過與專案 `.mcp.json` 相同的 [每個伺服器批准](https://code.claude.com/docs/zh-TW/mcp)
- LSP 伺服器只有在你信任工作區後才會啟動
- [背景監視器](https://code.claude.com/docs/zh-TW/plugins-reference#monitors) 不會載入

個人範圍的 plugins 沒有這些限制。 專案範圍的 `@skills-dir` plugins 只從工作階段的 [主要工作目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories) 的 `.claude/skills/` 載入。它們不會像純 skills 和命令那樣 [向上走到儲存庫根目錄](https://code.claude.com/docs/zh-TW/skills#discovery-from-parent-and-nested-directories)，所以從子目錄啟動會錯過位於儲存庫根目錄的 plugin。從儲存庫根目錄啟動，或在 v2.1.246 或更新版本上 [使用 `/cd` 將工作階段移到那裡](https://code.claude.com/docs/zh-TW/permissions#move-the-session-to-another-directory)。

### 編輯、重新載入和停用 skills-directory plugin

你對 skill 的 `SKILL.md` 所做的更改會立即在目前工作階段中生效。對 plugin 的其他元件（例如 `hooks/`、`.mcp.json`、`agents/` 和 `output-styles/`）的更改則不會。執行 `/reload-plugins` 或重新啟動 Claude Code 來取得這些更改。請參閱 [Live change detection](https://code.claude.com/docs/zh-TW/skills#live-change-detection)。 要停止載入 skills-directory plugin，請刪除其資料夾或按名稱停用它。沒有 `uninstall` 步驟，因為沒有從市集安裝任何東西。

```
claude plugin disable my-tool@skills-dir

```

______________________________________________________________________

## 從 claude.ai 同步的外掛程式

Claude Code 會載入為您的 claude.ai 帳戶啟用的外掛程式，包括您的組織為其成員開啟的外掛程式，以及您從 marketplace 安裝的外掛程式。它會將每個外掛程式下載到 `~/.claude/plugins/synced/` 中，並將其載入為 `<name>@synced`，沒有 marketplace 也沒有安裝記錄。同步的外掛程式執行時具有與您安裝的 marketplace 外掛程式相同的信任等級：其 skills、agents、hooks、MCP 伺服器和 LSP 伺服器都會載入。 Claude Code 同步這些外掛程式的位置取決於工作階段：

- 在 [Cowork](https://claude.com/product/cowork) 和[雲端工作階段](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)中，Claude Code 會在工作階段啟動時將它們下載到工作階段自身的環境中。在 v2.1.239 之前，Claude Code 將這些外掛程式載入為 `<name>@inline`，這是 `--plugin-dir` 外掛程式使用的身分。
- 在您使用 claude.ai 帳戶登入的終端機工作階段中，Claude Code 每次啟動時會檢查您的帳戶一次，然後在背景中下載新的和更新的外掛程式，並移除您或您的組織關閉的外掛程式。終端機工作階段中的同步需要 Claude Code v2.1.273 或更新版本。

啟動檢查在背景中執行，因此可以在您的工作階段啟動後完成。當它在互動式工作階段中新增、更新或移除同步的外掛程式時，Claude Code 會顯示 `Plugins changed. Run /reload-plugins to activate.` 執行 [`/reload-plugins`](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting) 以在該工作階段中載入變更，或留待下次啟動 Claude Code 時再進行。如果您在工作階段執行時在 claude.ai 上啟用外掛程式，Claude Code 會在下次啟動時下載它。 終端機工作階段中的外掛程式同步在與[從 claude.ai 同步的 skills](https://code.claude.com/docs/zh-TW/skills#where-synced-skills-load)相同的登入條件下執行。它還需要授予 Claude Code 存取您帳戶外掛程式的登入。 來自較早版本 Claude Code 的登入會在 Claude Code 在背景中更新該登入時（通常在幾小時內）或在您再次執行 `/login` 時立即取得外掛程式存取權限。外掛程式同步會在您之後下次啟動 Claude Code 時開始。 `claude plugin list` 會在 `Synced from claude.ai` 標題下顯示同步的外掛程式，而 `/plugin` **Installed** 標籤會列出它們，並以 `synced` 作為其來源。使用 `claude plugin list` 列印的 `<name>@synced` ID 來管理同步的外掛程式：

- **關閉其中一個** ：執行 `claude plugin disable <name>@synced`，或從 `/plugin` **Installed** 標籤中停用它。Claude Code 會將選擇儲存為您使用者層級 [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 中的 `"<name>@synced": false`。若要重新開啟外掛程式，請執行 `claude plugin enable <name>@synced`。
- **在任何地方都排除其中一個** ：[為您的 claude.ai 帳戶關閉外掛程式](https://code.claude.com/docs/zh-TW/desktop#extend-claude-code)。若要在每個環境中將其排除在一個專案之外，請在該專案已提交的 `.claude/settings.json` 中的 `enabledPlugins` 下設定 `"<name>@synced": false`。
- **在 claude.ai 上管理外掛程式本身** ：`claude plugin install`、`update` 和 `uninstall` 不適用於同步的外掛程式。Claude Code 會在下次同步時下載外掛程式的更新。若要移除一個，請為您的 claude.ai 帳戶關閉外掛程式，Claude Code 會在下次同步時將其移除。
- **停止在機器上同步** ：在您的使用者設定中將 [`syncClaudeAiPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#syncclaudeaiplugins) 設定為 `false`。Claude Code 會停止下載，下次啟動時會將已同步的外掛程式移動到 `~/.claude/plugins/.trash/`，並不再載入它們。您的組織可以在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中設定相同的金鑰，或在 claude.ai 上關閉 Skills，這也會停止外掛程式同步。

您無法關閉您的組織在 claude.ai 上標記為必需的外掛程式。Claude Code 會載入它，即使您之前停用了它，而 `claude plugin disable` 會拒絕並顯示 `Plugin "<name>@synced" is required by your organization and can't be disabled here. Contact your admin to change it.` 在 `claude plugin list` 中，這些外掛程式會標記為 `required by your org`。 當來自任何其他來源的已啟用外掛程式與同步外掛程式的名稱相符時，Claude Code 會載入該外掛程式並報告同步副本未被載入。其他來源包括 marketplace 安裝、[skills 目錄外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)、`--plugin-dir` 外掛程式和內建於 Claude Code 的外掛程式。若要改用 claude.ai 副本，請停用您自己的副本。在 v2.1.239 之前，Claude Code 會載入同步副本而不是同名的 marketplace 安裝。

______________________________________________________________________

## Plugin 資訊清單架構

`.claude-plugin/plugin.json` 檔案定義了您的 plugin 的中繼資料和設定。 資訊清單是選用的。如果省略，Claude Code 會在[預設位置](https://code.claude.com/docs/zh-TW/plugins-reference#file-locations-reference)自動探索元件，並從目錄名稱衍生 plugin 名稱。當您需要提供中繼資料或自訂元件路徑時，請使用資訊清單。

### 完整架構

```
{
  "name": "plugin-name",
  "displayName": "Plugin Name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "metadata": { "catalogId": "cat-123", "tier": "pro" },
  "skills": "./custom/skills/",
  "commands": ["./custom/commands/special.md"],
  "agents": ["./custom/agents/reviewer.md"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json",
  "experimental": {
    "themes": "./themes/",
    "monitors": "./monitors.json",
    "evals": "quality/evals"
  },
  "dependencies": [
    "helper-lib",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}

```

### 必要欄位

如果您包含資訊清單，`name` 是唯一必要的欄位。

| 欄位                                                                                                                                   | 類型   | 說明                                                                                                                                                                                                                                      | 範例                 |
| -------------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `name`                                                                                                                                 | string | 唯一識別碼，採用 kebab-case，不含空格、控制字元或雙向格式化字元。當[市集項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-entries)以不同名稱列出 plugin 時，市集項目名稱是 `enabledPlugins` 金鑰和 `/plugin` 使用的名稱 | `"deployment-tools"` |
| 此名稱用於元件命名空間。例如，在 UI 中，名稱為 `plugin-dev` 的 plugin 的代理程式 `agent-creator` 將顯示為 `plugin-dev:agent-creator`。 |        |                                                                                                                                                                                                                                           |                      |

### 無法識別的欄位

Claude Code 會忽略它無法識別的頂層欄位。您可以在 `plugin.json` 中保留來自另一個生態系統的中繼資料，plugin 仍會載入。這使得維護一個資訊清單變得實用，該資訊清單可同時用作 VS Code 或 Cursor 擴充功能資訊清單、npm `package.json` 或 MCPB/DXT 套件資訊清單。 `claude plugin validate` 會將無法識別的欄位報告為警告，而非錯誤。如果欄位與已識別的欄位相差一或兩個字元，警告會建議可能的預期名稱。只有無法識別欄位警告的 plugin 仍會通過驗證並在執行時載入。 Claude Code 如何處理已識別欄位但值類型錯誤的情況取決於該欄位：

- **大多數欄位** ：plugin 無法載入。例如，`keywords` 值為字串而非陣列是載入錯誤，`claude plugin validate` 會將其報告為錯誤。
- **`experimental`和`metadata`** ：Claude Code 會忽略非物件值，`claude plugin validate` 會報告警告。

傳遞 `--strict` 以將警告視為錯誤。在 CI 中使用它來在發佈前捕捉拼寫錯誤的欄位名稱或來自另一個工具資訊清單的遺留欄位，即使 plugin 在執行時會載入。

```
claude plugin validate ./my-plugin --strict

```

### 中繼資料欄位

| 欄位             | 類型    | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 範例                                                              |
| ---------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `$schema`        | string  | JSON Schema URL，用於編輯器自動完成和驗證。Claude Code 在載入時會忽略此欄位。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `"https://json.schemastore.org/claude-code-plugin-manifest.json"` |
| `displayName`    | string  | 在 `/plugin` 選擇器和其他 UI 表面中顯示的人類可讀名稱。對於市集安裝的 plugin，[市集項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#optional-plugin-fields)上的 `displayName` 優先於此值。當兩個位置都未設定顯示名稱時，使用者會看到 `name`。與 `name` 不同，可包含空格和任何大小寫。不用於命名空間或查詢。                                                                                                                                                                                                                                                   | `"Deployment Tools"`                                              |
| `version`        | string  | 選用。語義版本。設定此項會將 plugin 固定到該版本字串，因此使用者只有在您提升版本時才會收到更新，除了[`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)或[載入中的 plugin](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution) 外；請參閱[版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)。如果也在市集項目中設定，`plugin.json` 優先。如果省略，版本來自[版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)中的下一個來源。 | `"2.1.0"`                                                         |
| `description`    | string  | plugin 用途的簡短說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `"Deployment automation tools"`                                   |
| `author`         | object  | 作者資訊                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | `{"name": "Dev Team", "email": "dev@company.com"}`                |
| `homepage`       | string  | 文件 URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | `"https://docs.example.com"`                                      |
| `repository`     | string  | 原始碼 URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `"https://github.com/user/plugin"`                                |
| `license`        | string  | 授權識別碼                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `"MIT"`、`"Apache-2.0"`                                           |
| `keywords`       | array   | 探索標籤                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | `["deployment", "ci-cd"]`                                         |
| `metadata`       | object  | 自由格式物件，用於您自己的資料，例如權利或目錄欄位。Claude Code 不會讀取它，因此值永遠不會影響 plugin 行為。Claude Code 會忽略非物件值，`claude plugin validate` 會將其報告為警告。在 v2.1.222 之前，Claude Code 將金鑰視為[無法識別的欄位](https://code.claude.com/docs/zh-TW/plugins-reference#unrecognized-fields)。                                                                                                                                                                                                                                                   | `{"catalogId": "cat-123"}`                                        |
| `defaultEnabled` | boolean | 當使用者未設定時，plugin 是否以啟用狀態開始。預設為 `true`。請參閱[預設啟用](https://code.claude.com/docs/zh-TW/plugins-reference#default-enablement)。                                                                                                                                                                                                                                                                                                                                                                                                                   | `false`                                                           |

### 預設啟用

在 `plugin.json` 中設定 `defaultEnabled: false` 以發佈已停用安裝的 plugin。使用者可使用 `claude plugin enable <plugin>` 或 `/plugin` 介面將其開啟。對於新增成本或使用者應選擇加入的 plugin（例如連接到外部服務的 plugin），請使用此選項。 `defaultEnabled` 是當沒有其他因素決定 plugin 狀態時的後備選項。使用者的設定和相依性要求優先於它：

- **使用者的設定** ：任何設定範圍中 `enabledPlugins` 中的 plugin 項目。一旦寫入，它會在 plugin 更新和重新安裝中持續存在，因此在後續版本中變更 `defaultEnabled` 不會翻轉現有使用者。
- **相依性要求** ：當 plugin 由另一個啟用的 plugin 所需時，Claude Code 會在安裝或啟用時為其寫入 `true`。這給了它明確的設定，因此它自己的預設不再適用。請參閱[啟用或停用具有相依性的 plugin](https://code.claude.com/docs/zh-TW/plugin-dependencies#enable-or-disable-a-plugin-with-dependencies)。

相同欄位也可以出現在 plugin 的市集項目中，其優先於 `plugin.json` 中的值。請參閱[選用 plugin 欄位](https://code.claude.com/docs/zh-TW/plugin-marketplaces#optional-plugin-fields)。

### 元件路徑欄位

| 欄位                    | 類型   | 說明                                                                                                                                            | 範例                                                                                                                                                                                                    |
| ----------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `skills`                | string | array                                                                                                                                           | 包含 `<name>/SKILL.md` 的自訂 skill 目錄。新增至預設 `skills/` 掃描。請參閱[路徑行為規則](https://code.claude.com/docs/zh-TW/plugins-reference#path-behavior-rules)以了解市集根目錄例外                 |
| `commands`              | string | array                                                                                                                                           | 自訂平面 `.md` skill 檔案或目錄（取代預設 `commands/`）                                                                                                                                                 |
| `agents`                | string | array                                                                                                                                           | 自訂代理程式檔案（取代預設 `agents/`）                                                                                                                                                                  |
| `workflows`             | string | array                                                                                                                                           | 自訂[工作流程](https://code.claude.com/docs/zh-TW/workflows)指令檔案或目錄（取代預設 `workflows/`）                                                                                                     |
| `hooks`                 | string | array                                                                                                                                           | object                                                                                                                                                                                                  |
| `mcpServers`            | string | array                                                                                                                                           | object                                                                                                                                                                                                  |
| `outputStyles`          | string | array                                                                                                                                           | 自訂輸出樣式檔案/目錄（取代預設 `output-styles/`）                                                                                                                                                      |
| `lspServers`            | string | array                                                                                                                                           | object                                                                                                                                                                                                  |
| `experimental.themes`   | string | array                                                                                                                                           | 色彩主題檔案/目錄（取代預設 `themes/`）。請參閱[主題](https://code.claude.com/docs/zh-TW/plugins-reference#themes)                                                                                      |
| `experimental.monitors` | string | array                                                                                                                                           | 當 plugin 啟用時自動啟動的背景 [Monitor](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool) 設定。請參閱[監視器](https://code.claude.com/docs/zh-TW/plugins-reference#monitors)           |
| `experimental.evals`    | string | array                                                                                                                                           | plugin 根目錄下的目錄，用於保存 plugin 的[評估案例](https://code.claude.com/docs/zh-TW/plugin-evals#use-a-different-eval-directory)，當它不是預設 `evals/` 時。`claude plugin eval --eval-dir` 會覆寫它 |
| `userConfig`            | object | 在啟用時提示的使用者可設定值。請參閱[使用者設定](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration)                       |                                                                                                                                                                                                         |
| `channels`              | array  | 訊息注入的頻道宣告（Telegram、Slack、Discord 樣式）。請參閱[頻道](https://code.claude.com/docs/zh-TW/plugins-reference#channels)                |                                                                                                                                                                                                         |
| `dependencies`          | array  | 此 plugin 所需的其他 plugin，可選擇使用 semver 版本限制。請參閱[限制 plugin 相依性版本](https://code.claude.com/docs/zh-TW/plugin-dependencies) | `[{ "name": "secrets-vault", "version": "~2.1.0" }]`                                                                                                                                                    |

### 實驗性元件

`experimental` 金鑰下的元件 `themes` 和 `monitors` 具有資訊清單架構，該架構可能在版本之間變更，同時它們穩定。您宣告它們的位置是一個單獨的遷移：頂層仍然有效，`claude plugin validate` 發出警告，未來版本將需要 `experimental.*`。

### 使用者設定

`userConfig` 欄位宣告當 plugin 啟用時 Claude Code 提示使用者的值。使用此選項而不是要求使用者手動編輯 `settings.json`。

```
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    }
  }
}

```

金鑰必須是有效的識別碼。每個選項支援這些欄位：

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 必要                                                                                                                                            | 說明                                                                                                |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 是                                                                                                                                              | `string`、`number`、`boolean`、`directory` 或 `file` 之一                                           |
| `title`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 是                                                                                                                                              | 在設定對話方塊中顯示的標籤                                                                          |
| `description`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 是                                                                                                                                              | 在欄位下方顯示的說明文字                                                                            |
| `sensitive`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 否                                                                                                                                              | 如果為 `true`，會遮罩輸入並將值儲存在安全儲存中，而不是 `settings.json`                             |
| `required`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 否                                                                                                                                              | 如果為 `true`，當欄位為空時驗證失敗                                                                 |
| `default`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 否                                                                                                                                              | 當使用者未提供任何內容時使用的值                                                                    |
| `options`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 否                                                                                                                                              | 對於 `string` 類型，欄位接受的值，在 `/config` 中顯示為選擇器。需要 Claude Code v2.1.271 或更新版本 |
| `multiple`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 否                                                                                                                                              | 對於 `string` 類型，允許字串陣列                                                                    |
| `min` / `max`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 否                                                                                                                                              | `number` 類型的界限                                                                                 |
| 除了 `sensitive` 欄位和 `multiple` 清單外，每個啟用 plugin 的每個欄位也會在 `/config` 面板中顯示為一列。這些列需要 Claude Code v2.1.269 或更新版本。 每個值都可用於在 MCP 和 LSP 伺服器設定以及 hook 命令中替換為 `${user_config.KEY}`。非敏感值也可以在 skill 和代理程式內容中替換。所有值都會匯出到 hook 程序作為 `CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數，其中 `<KEY>` 是選項金鑰的大寫版本。 在 shell 中執行的欄位會拒絕 `${user_config.*}`：將設定的值替換到 shell 命令中會讓 shell 執行該值包含的任何內容，因此元件會失敗並出現[錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config)。每個被拒絕的欄位都有一個替代方式來傳遞值： |                                                                                                                                                 |                                                                                                     |
| 被拒絕的欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 如何傳遞值                                                                                                                                      |                                                                                                     |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | ---                                                                                                                                             |                                                                                                     |
| Shell 形式 hook 命令                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 使用[執行形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)搭配 `args`，或從 hook 的環境讀取 `CLAUDE_PLUGIN_OPTION_<KEY>` |                                                                                                     |
| [Monitor](https://code.claude.com/docs/zh-TW/plugins-reference#monitors) 命令                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 從指令碼中的設定檔讀取值                                                                                                                        |                                                                                                     |
| MCP [`headersHelper`](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 從指令碼中的設定檔讀取值                                                                                                                        |                                                                                                     |
| 在 v2.1.207 之前，這些欄位替換了 `${user_config.KEY}` 值；更新依賴此功能的 plugin。 非敏感值儲存在您的使用者 `settings.json` 中的 [`pluginConfigs`](https://code.claude.com/docs/zh-TW/settings-reference#pluginconfigs) 金鑰下，作為 `pluginConfigs[<plugin-id>].options`。 在 macOS 上，Claude Code 將敏感值儲存在 macOS Keychain 中，當 Keychain 拒絕寫入時回退到 `~/.claude/.credentials.json`。在沒有支援的 keychain 的平台上，它將它們儲存在 `~/.claude/.credentials.json` 中。Keychain 儲存與 OAuth 令牌共享，總限制約為 2 KB，因此請保持敏感值較小。 Claude Code 只從三個設定來源讀取所有 `pluginConfigs` 值：                                                 |                                                                                                                                                 |                                                                                                     |

- **使用者設定** ：`~/.claude/settings.json`，啟用時提示寫入的檔案
- **`--settings`**：CLI 旗標或 SDK 內嵌設定
- **受管設定** ：[組織控制的原則](https://code.claude.com/docs/zh-TW/permissions#managed-settings)

當多個來源設定相同金鑰時，受管設定優先，然後是 `--settings`，然後是使用者設定。您可以從此清單中移除的唯一來源是使用者設定：傳遞 [`--setting-sources`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 而不包含 `user`，Claude Code 會跳過它們。受管設定和 `--settings` 保持您傳遞的任何內容。SDK 的 [`settingSources`](https://code.claude.com/docs/zh-TW/agent-sdk/claude-code-features#what-settingsources-does-not-control) 選項設定相同的清單。 專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的項目會被忽略。兩個檔案都位於工作區中，因此複製的儲存庫可以在那裡提供值，這些值會流入 plugin hook 命令、MCP 伺服器設定、LSP 命令和監視器命令。在 v2.1.207 之前，這些項目被讀取。限制特定於 `pluginConfigs`：[`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 仍然遵守專案和本機設定。

### 頻道

`channels` 欄位讓 plugin 宣告一個或多個訊息頻道，將內容注入對話中。每個頻道繫結到 plugin 提供的 MCP 伺服器。

```
{
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": {
          "type": "string",
          "title": "Bot token",
          "description": "Telegram bot token",
          "sensitive": true
        },
        "owner_id": {
          "type": "string",
          "title": "Owner ID",
          "description": "Your Telegram user ID"
        }
      }
    }
  ]
}

```

`server` 欄位是必要的，必須符合 plugin 的 `mcpServers` 中的金鑰。選用的每個頻道 `userConfig` 使用與頂層欄位相同的架構，讓 plugin 在啟用時提示 bot 令牌或擁有者 ID。

### 路徑行為規則

自訂路徑是取代還是擴展 plugin 的預設目錄取決於欄位：

- **取代預設** ：`commands`、`agents`、`workflows`、`outputStyles`、`experimental.themes`、`experimental.monitors`。例如，當資訊清單指定 `commands` 時，預設 `commands/` 目錄不會被掃描。若要保留預設並新增更多，請明確列出：`"commands": ["./commands/", "./extras/"]`
- **新增至預設** ：`skills`。預設 `skills/` 目錄始終被掃描，`skills` 中列出的目錄與其一起載入。例外：對於[其 `source` 解析為市集根目錄的市集項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#advanced-plugin-entries)，宣告特定子目錄會取代預設 `skills/` 掃描
- **自己的合併規則** ：[hooks](https://code.claude.com/docs/zh-TW/plugins-reference#hooks)、[MCP 伺服器](https://code.claude.com/docs/zh-TW/plugins-reference#mcp-servers) 和 [LSP 伺服器](https://code.claude.com/docs/zh-TW/plugins-reference#lsp-servers)。請參閱每個部分以了解多個來源如何結合

當 plugin 同時具有預設資料夾和相符的資訊清單金鑰時，Claude Code 會在 `claude plugin list` 和 `/plugin` 詳細檢視中警告被忽略的資料夾。plugin 仍會使用資訊清單路徑載入。當資訊清單金鑰指向預設資料夾時，Claude Code 不會警告，例如 `"commands": ["./commands/deploy.md"]`，因為該路徑明確命名資料夾。 對於所有路徑欄位：

- 所有路徑必須相對於 plugin 根目錄並以 `./` 開頭，除了 `skills` 欄位也接受 `"."`
  - `"."` 和 `"./"` 都表示 plugin 根目錄本身
  - 在 v2.1.221 之前，`"."` 無法通過資訊清單驗證，plugin 無法載入，因此使用 `"./"` 以支援較早版本
- 來自自訂路徑的元件使用相同的命名和命名空間規則
- 多個路徑可以指定為陣列
- skill 路徑可以指向直接包含 `SKILL.md` 的目錄，例如 `"skills": ["."]` 用於 plugin 根目錄
  - Claude Code 從 `SKILL.md` 中的前置事項 `name` 欄位取得 skill 的呼叫名稱，因此無論安裝目錄名稱如何，名稱保持穩定
  - 如果前置事項中未設定 `name`，Claude Code 會回退到目錄基底名稱

具有根目錄中 `SKILL.md`、沒有 `skills/` 子目錄且沒有 `skills` 資訊清單欄位的 plugin 會自動載入為單一 skill plugin。您不需要為此配置在 `plugin.json` 中設定 `"skills": ["./"]`。 **路徑範例** ：

```
{
  "commands": [
    "./specialized/deploy.md",
    "./utilities/batch-process.md"
  ],
  "agents": [
    "./custom-agents/reviewer.md",
    "./custom-agents/tester.md"
  ]
}

```

### 環境變數

Claude Code 提供三個變數用於參考路徑：

| 變數                                                                                                                                                                                                                                                                                                       | 解析為                                                                                                                             | 用途                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `${CLAUDE_PLUGIN_ROOT}`                                                                                                                                                                                                                                                                                    | plugin 安裝目錄的絕對路徑                                                                                                          | 與 plugin 捆綁的指令碼、二進位檔案和設定檔                                 |
| `${CLAUDE_PLUGIN_DATA}`                                                                                                                                                                                                                                                                                    | [持續目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)，在首次參考時建立，在 plugin 更新中存活 | 已安裝的相依性，例如 `node_modules` 或 Python 虛擬環境、產生的程式碼和快取 |
| `${CLAUDE_PROJECT_DIR}`                                                                                                                                                                                                                                                                                    | 專案根目錄                                                                                                                         | 專案本機指令碼和設定檔                                                     |
| 所有三個都匯出為環境變數到 hook 程序以及 MCP 和 LSP 伺服器子程序。它們不存在於 Claude 透過 Bash 工具執行的命令環境中，無論是在主工作階段或子代理中。在 plugin 內容中，寫入預留位置，Claude Code 會在載入內容時內嵌替換路徑。哪些欄位內嵌替換它們取決於 plugin 元件：                                       |                                                                                                                                    |                                                                            |
| Plugin 元件                                                                                                                                                                                                                                                                                                | 預留位置解析的欄位                                                                                                                 |                                                                            |
| ---                                                                                                                                                                                                                                                                                                        | ---                                                                                                                                |                                                                            |
| Skill 和代理程式內容                                                                                                                                                                                                                                                                                       | 預留位置出現的任何位置                                                                                                             |                                                                            |
| Hook 和監視器命令                                                                                                                                                                                                                                                                                          | 預留位置出現的任何位置                                                                                                             |                                                                            |
| MCP `stdio` 伺服器                                                                                                                                                                                                                                                                                         | `command`、`args`、`env`                                                                                                           |                                                                            |
| MCP `http`、`sse`、`ws` 伺服器                                                                                                                                                                                                                                                                             | `url`、`headers`、`headersHelper`                                                                                                  |                                                                            |
| LSP 伺服器                                                                                                                                                                                                                                                                                                 | `command`、`args`、`env`、`workspaceFolder`                                                                                        |                                                                            |
| 在 hook 命令中，使用[執行形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form)搭配 `args`，以便每個路徑作為一個引數傳遞，無需引號。在 shell 形式 hook 和監視器命令中，用雙引號包裝變數，如 `"${CLAUDE_PROJECT_DIR}/scripts/server.sh"`。此 shell 形式 hook 執行與 plugin 捆綁的指令碼： |                                                                                                                                    |                                                                            |

```
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/process.sh"
          }
        ]
      }
    ]
  }
}

```

對於複製的 plugin，`${CLAUDE_PLUGIN_ROOT}` 在 plugin 更新時變更。前一個版本的目錄在更新後的寬限期內保留在磁碟上，但將其視為暫時的，不要在那裡寫入狀態。請參閱 [plugin 快取](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)以了解哪些 plugin 被複製以及清理語義。 當複製的 plugin 在工作階段中期更新時，hook 命令、監視器、MCP 伺服器和 LSP 伺服器繼續使用前一個版本的路徑。執行 `/reload-plugins` 以將 hook、MCP 伺服器和 LSP 伺服器切換到新路徑；監視器需要工作階段重新啟動。在沒有互動式終端的工作階段中，重新載入會將 plugin MCP 伺服器保留在舊路徑上，直到下一個工作階段。 對於具有 `command` 來源的 plugin，Claude Code [可以重新載入 plugin 本身](https://code.claude.com/docs/zh-TW/plugin-marketplaces#when-claude-code-re-runs-the-command)。 MCP 伺服器也可以呼叫 `roots/list` 要求以在執行時讀取工作階段的工作目錄。請參閱 [`roots/list` 傳回的內容以及 Claude Code 何時通知伺服器變更](https://code.claude.com/docs/zh-TW/mcp#option-3-add-a-local-stdio-server)。

#### 持續資料目錄

`${CLAUDE_PLUGIN_DATA}` 目錄解析為 `~/.claude/plugins/data/{id}/`，其中 `{id}` 是 plugin 識別碼，其中 `a-z`、`A-Z`、`0-9`、`_` 和 `-` 以外的字元被替換為 `-`。對於安裝為 `formatter@my-marketplace` 的 plugin，目錄是 `~/.claude/plugins/data/formatter-my-marketplace/`。 常見用途是一次安裝語言相依性並在工作階段和 plugin 更新中重複使用它們。將其用於 Python 相依性、使用 Yarn 或 pnpm 鎖定的相依性，以及其生命週期指令碼必須執行的套件。對於市集安裝的 plugin，您可能根本不需要它：Claude Code 在快取 plugin 時會自動安裝符合條件的 [Node.js 套件相依性](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)。 因為資料目錄的壽命超過任何單一 plugin 版本，單獨檢查目錄存在無法偵測當更新變更 plugin 的相依性資訊清單時。建議的模式是比較捆綁的資訊清單與資料目錄中的副本，並在它們不同時重新安裝。 此 `SessionStart` hook 在首次執行時安裝 `node_modules`，並在 plugin 更新包含變更的 `package.json` 時再次安裝：

```
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
          }
        ]
      }
    ]
  }
}

```

`diff` 在儲存的副本遺失或與捆綁的副本不同時以非零值退出，涵蓋首次執行和相依性變更更新。如果 `npm install` 失敗，尾部 `rm` 會移除複製的資訊清單，以便下一個工作階段重試。 捆綁在 `${CLAUDE_PLUGIN_ROOT}` 中的指令碼可以針對持續的 `node_modules` 執行：

```
{
  "mcpServers": {
    "routines": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"],
      "env": {
        "NODE_PATH": "${CLAUDE_PLUGIN_DATA}/node_modules"
      }
    }
  }
}

```

當您從最後一個安裝 plugin 的範圍卸載 plugin 時，資料目錄會自動刪除。`/plugin` 介面顯示目錄大小並在刪除前提示。CLI 預設刪除；傳遞 [`--keep-data`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-uninstall) 以保留它。

______________________________________________________________________

## Plugin 快取和檔案解析

Plugin 可以透過以下三種方式指定：

- 透過 `claude --plugin-dir` 或 `claude --plugin-url`，在工作階段期間使用。
- 透過市集安裝，供未來的工作階段使用。
- 透過您的 claude.ai 帳戶，[同步](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)到 `~/.claude/plugins/synced/`。

基於安全性和驗證目的，Claude Code 會將_市集\_ plugin 複製到使用者的本機 **plugin 快取** （`~/.claude/plugins/cache`），除非 plugin 就地載入。[連結模式中的 `command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode)會透過快取項目中的連結就地載入。[市集中的相對路徑來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths)從本機目錄新增的市集會就地從市集資料夾載入。 對於從本機目錄市集就地載入的 plugin，您對來源目錄的編輯會在下一個工作階段開始或 `/reload-plugins` 時生效。您不需要版本更新。Plugin 的 hook 程序和 MCP 和 LSP 伺服器會收到指向來源目錄的 `CLAUDE_PLUGIN_ROOT`。Claude Code 不會將 plugin 的 [Node.js 套件相依性](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)安裝到來源目錄中。請自行安裝它們，或從 hook 安裝到[持久資料目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)。 對於複製的 plugin，每個已安裝的版本都是快取中的單獨目錄，按市集和 plugin 分組，並以已解析的版本命名，具有自己的 plugin 檔案副本和 [Node.js 套件相依性](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)。從[發行標籤](https://code.claude.com/docs/zh-TW/plugin-dependencies#tag-plugin-releases-for-version-resolution)解析的相依性會取得帶有 commit-SHA 後綴的目錄名稱。 當您更新或解除安裝 plugin 時，Claude Code 會將先前的版本目錄標記為孤立，並在大約 14 天後的背景掃描中將其移除。寬限期讓已載入舊版本的並行 Claude Code 工作階段繼續執行而不會出現錯誤。Claude Code 只在至少安裝了一個 plugin 時執行掃描；在您解除安裝最後一個 plugin 後，孤立目錄會保留在磁碟上，直到您再次安裝 plugin。 Claude Code 只在 plugin 或市集資料夾不再包含任何目錄或符號連結時，才會將它從快取中移除。如果您將開發簽出符號連結到快取中作為 plugin 的版本項目，Claude Code 永遠不會將連結標記為孤立，也永遠不會移除它或包含它的資料夾。Claude Code 也永遠不會在連結的簽出中寫入其版本追蹤檔案。 Claude 的 Glob 和 Grep 工具在搜尋期間會跳過孤立的版本目錄，因此檔案結果不包括過時的 plugin 程式碼。

### Node.js 套件相依性

當 Claude Code 將 plugin 複製到快取時，它也會在那裡安裝 plugin 的 Node.js 套件相依性，以便 plugin 的 hooks 和 MCP 伺服器可以載入它們。本節涵蓋 plugin 在其自己的 `package.json` 中宣告的 npm 和 Bun 套件。對於依賴其他 plugin 的 plugin，請參閱 [plugin 相依性版本](https://code.claude.com/docs/zh-TW/plugin-dependencies)。 Claude Code 在每次建立複製版本目錄時都會在其中執行安裝：當您安裝 plugin 時、當 Claude Code 將 plugin 更新為新版本時，以及在工作階段開始時（當已啟用的 plugin 尚未快取時），例如在新機器上。只有當 plugin 的根目錄同時包含 `package.json` 和支援的鎖定檔案時，安裝才會執行：

| 鎖定檔案                                                                                                                                                                                                       | 命令                                             |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `bun.lock` 或 `bun.lockb`                                                                                                                                                                                      | `bun install --frozen-lockfile --ignore-scripts` |
| `npm-shrinkwrap.json` 或 `package-lock.json`                                                                                                                                                                   | `npm ci --ignore-scripts`                        |
| 如果 plugin 包含多個這些鎖定檔案，Claude Code 會使用第一個符合項，按順序檢查：`bun.lock`、`bun.lockb`、`npm-shrinkwrap.json`、`package-lock.json`。 Claude Code 在兩種情況下會跳過安裝，各有其自己的修正方式： |                                                  |

- 如果您的 plugin 只附帶 `yarn.lock` 或 `pnpm-lock.yaml`，請將其替換為 npm 鎖定檔案。
- 如果 `bunfig.toml` 位於 bun 鎖定檔案旁邊，請移除 `bunfig.toml`，或將 bun 鎖定檔案替換為 npm 鎖定檔案。

提供 npm 鎖定檔案以獲得最廣泛的覆蓋。Claude Code 從使用者的 PATH 執行符合的鎖定檔案的套件管理員，如果遺失，不會回退到其他鎖定檔案。對於透過 npm 來源分發的 plugin，請使用 `npm-shrinkwrap.json`；npm 會從已發佈的套件中排除 `package-lock.json`。 Claude Code 限制此相依性安裝，使得 plugin 或其套件中的任何程式碼在安裝期間都不會執行，並限制其執行時間：

- **凍結解析：** Bun 和 npm 安裝鎖定檔案精確指定的內容，當 `package.json` 和鎖定檔案不一致時，會失敗而不是重新解析版本。
- **無生命週期指令碼：** `--ignore-scripts` 防止 `preinstall`、`install` 和 `postinstall` 指令碼執行，因此在這些指令碼中建置原生模組的相依性會下載但在此安裝期間不會編譯。
- **60 秒逾時：** Claude Code 會停止執行時間超過此時間的安裝，並將其視為失敗。

Claude Code 在此相依性安裝之前會提取 npm 來源 plugin，並且套件本身的任何安裝指令碼都不會在提取期間執行。請參閱 [npm 套件](https://code.claude.com/docs/zh-TW/plugin-marketplaces#npm-packages)。 失敗或跳過的安裝永遠不會阻止 plugin。當安裝失敗或 Claude Code 跳過 yarn 或 pnpm 鎖定檔案或旁邊有 `bunfig.toml` 的 bun 鎖定檔案時，它會在[偵錯輸出](https://code.claude.com/docs/zh-TW/plugins-reference#debugging-commands)中將原因記錄為警告。具有 `package.json` 且沒有鎖定檔案的 plugin 會被跳過，不會有日誌項目。逾時的安裝可能會在快取副本中留下部分 `node_modules` 樹。 您無法關閉自動安裝；沒有設定或環境變數可以停用它。在受限網路中，請參閱[網路存取需求](https://code.claude.com/docs/zh-TW/network-config#network-access-requirements)以了解要允許的主機。 對於自動安裝無法提供的相依性，例如需要其生命週期指令碼來建置的套件、Python 相依性或使用 Yarn 或 pnpm 鎖定的 plugin，請從 hook 將其安裝到[持久資料目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)。

### 路徑遍歷限制

Claude Code 不允許 plugin 參考其自己目錄外的檔案。它會拒絕解析到 plugin 根目錄外的元件路徑，無論路徑是在 `plugin.json` 中宣告還是在[市集項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-entries)中宣告。這涵蓋指向 plugin 外部的路徑（如寫入的），例如 `../shared-utils`，以及導向 plugin 外部的符號連結，除了[市集內的連結](https://code.claude.com/docs/zh-TW/plugins-reference#share-files-within-a-marketplace-with-symlinks)。 在 macOS 和 Linux 上，Claude Code 也會拒絕包含反斜線的元件路徑，即使路徑保留在 plugin 內。因此，使用反斜線路徑宣告的元件只在 Windows 上載入。使用正斜線編寫元件路徑，例如 `./commands/deploy.md`。 當 Claude Code 拒絕路徑時，它會報告 [`path escapes plugin directory`](https://code.claude.com/docs/zh-TW/errors#path-escapes-plugin-directory) 錯誤，並在沒有該元件的情況下載入 plugin。 Claude Code 在安裝 plugin 時也不會將 plugin 目錄外的檔案複製到快取中，因此當複製的 plugin 內的指令碼讀取 plugin 根目錄上方的路徑時，它也找不到這些檔案。

### 使用符號連結在市集內共享檔案

如果您的 plugin 需要與同一市集的其他部分共享檔案，您可以在 plugin 目錄內建立符號連結。當 plugin 複製到快取時符號連結的處理方式取決於其目標的解析位置：

- **在 plugin 自己的目錄內：** 符號連結在快取中保留為相對符號連結，因此在執行時它會繼續解析到複製的目標。
- **在同一市集內的其他位置：** 符號連結被取消參考。目標的內容被複製到快取中以取代它。這讓中繼 plugin 的 `skills/` 目錄可以連結到市集中其他 plugin 定義的技能。
- **在市集外：** 符號連結因安全性而被跳過。這防止 plugin 將任意主機檔案（例如系統路徑）拉入快取。

對於使用 `--plugin-dir` 安裝的 plugin、來自本機路徑的 plugin，或來自複製模式中的 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode)的 plugin，只有解析到 plugin 自己目錄內的符號連結會被保留。所有其他連結都會被跳過。 以下命令會建立從市集 plugin 內部到由同級 plugin 定義的共享技能的連結。在 Windows 上，從提升的命令提示字元使用 `mklink /D` 或啟用開發人員模式：

```
ln -s ../../shared-plugin/skills/foo ./skills/foo

```

______________________________________________________________________

## Plugin 目錄結構

### 標準 plugin 配置

一個完整的 plugin 遵循此結構：

```
enterprise-plugin/
├── .claude-plugin/           # 中繼資料目錄（選用）
│   └── plugin.json             # plugin 資訊清單
├── skills/                   # Skills
│   ├── code-reviewer/
│   │   └── SKILL.md
│   └── pdf-processor/
│       ├── SKILL.md
│       └── scripts/
├── commands/                 # Skills 作為平面 .md 檔案
│   ├── status.md
│   └── logs.md
├── agents/                   # Subagent 定義
│   ├── security-reviewer.md
│   ├── performance-tester.md
│   └── compliance-checker.md
├── workflows/                # Workflow 指令碼
│   └── release-audit.js
├── output-styles/            # 輸出樣式定義
│   └── terse.md
├── themes/                   # 色彩主題定義
│   └── dracula.json
├── monitors/                 # 背景監視器設定
│   └── monitors.json
├── hooks/                    # Hook 設定
│   ├── hooks.json           # 主要 hook 設定
│   └── security-hooks.json  # 其他 hooks
├── bin/                      # Plugin 可執行檔新增至 PATH
│   └── my-tool               # 在 Bash tool 中可作為裸命令叫用
├── settings.json            # Plugin 的預設設定
├── .mcp.json                # MCP 伺服器定義
├── .lsp.json                # LSP 伺服器設定
├── scripts/                 # Hook 和公用程式指令碼
│   ├── security-scan.sh
│   ├── format-code.py
│   └── deploy.js
├── LICENSE                  # 授權檔案
└── CHANGELOG.md             # 版本歷史

```

`.claude-plugin/` 目錄包含 `plugin.json` 檔案。所有其他目錄（commands/、agents/、skills/、workflows/、output-styles/、themes/、monitors/、hooks/）必須位於 plugin 根目錄，而不是在 `.claude-plugin/` 內。 Plugin 根目錄的 `CLAUDE.md` 檔案不會作為專案內容載入。Plugins 透過 skills、agents 和 hooks 而非 CLAUDE.md 來貢獻內容。若要提供載入至 Claude 內容的指示，請將其放在 [skill](https://code.claude.com/docs/zh-TW/plugins-reference#skills) 中。

### 檔案位置參考

| 元件           | 預設位置                     | 用途                                                                                                                                                                                                                                              |
| -------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **資訊清單**   | `.claude-plugin/plugin.json` | Plugin 中繼資料和設定（選用）                                                                                                                                                                                                                     |
| **Skills**     | `skills/`                    | 具有 `<name>/SKILL.md` 結構的 Skills                                                                                                                                                                                                              |
| **Commands**   | `commands/`                  | Skills 作為平面 Markdown 檔案。新 plugins 請使用 `skills/`                                                                                                                                                                                        |
| **Agents**     | `agents/`                    | Subagent Markdown 檔案                                                                                                                                                                                                                            |
| **Workflows**  | `workflows/`                 | [Workflow](https://code.claude.com/docs/zh-TW/workflows) 指令碼檔案                                                                                                                                                                               |
| **輸出樣式**   | `output-styles/`             | 輸出樣式定義                                                                                                                                                                                                                                      |
| **主題**       | `themes/`                    | 色彩主題定義                                                                                                                                                                                                                                      |
| **Hooks**      | `hooks/hooks.json`           | Hook 設定                                                                                                                                                                                                                                         |
| **MCP 伺服器** | `.mcp.json`                  | MCP 伺服器定義                                                                                                                                                                                                                                    |
| **LSP 伺服器** | `.lsp.json`                  | 語言伺服器設定                                                                                                                                                                                                                                    |
| **監視器**     | `monitors/monitors.json`     | 背景監視器設定                                                                                                                                                                                                                                    |
| **可執行檔**   | `bin/`                       | 新增至 Bash tool 的 `PATH` 的可執行檔，在 plugin 啟用時可作為裸命令叫用。您無法在透過 claude.ai 組織設定 [分發的 plugin 中包含此目錄](https://code.claude.com/docs/zh-TW/plugin-marketplaces#keep-executables-out-of-the-top-level-bin-directory) |
| **設定**       | `settings.json`              | Plugin 啟用時套用的預設設定。僅支援 [`agent`](https://code.claude.com/docs/zh-TW/sub-agents) 和 [`subagentStatusLine`](https://code.claude.com/docs/zh-TW/statusline#subagent-status-lines) 鍵                                                    |

______________________________________________________________________

## CLI 命令參考

Claude Code 提供 CLI 命令用於非互動式外掛程式管理，適用於指令碼和自動化。

### plugin init

在 `~/.claude/skills/<name>/` 處建立新外掛程式的框架。在下一個 Claude Code 工作階段中，它會自動載入為 `<name>@skills-dir`，並在 `/plugin` 和 `claude plugin list` 中出現，無需安裝步驟。 請參閱[技能目錄外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)以了解範圍和信任要求。

```
claude plugin init <name> [options]

```

該命令接受這些引數：

- `<name>`：外掛程式名稱。成為技能命名空間和 `~/.claude/skills/` 下的目錄名稱，因此不能包含空格或路徑分隔符。

該命令接受這些選項：

| 選項                                                                                                                                                                                                                                                                                                                                                    | 說明                                                                                                                                      | 預設值                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `--description <text>`                                                                                                                                                                                                                                                                                                                                  | 資訊清單說明                                                                                                                              |                         |
| `--author <name>`                                                                                                                                                                                                                                                                                                                                       | 作者名稱                                                                                                                                  | `git config user.name`  |
| `--author-email <email>`                                                                                                                                                                                                                                                                                                                                | 作者電子郵件                                                                                                                              | `git config user.email` |
| `--with <components...>`                                                                                                                                                                                                                                                                                                                                | 同時建立元件資料夾的框架。有效值：`skills`、`agents`、`hooks`、`mcp`、`lsp`、`output-style`、`channel`                                    |                         |
| `-f, --force`                                                                                                                                                                                                                                                                                                                                           | 覆寫目標處現有的 `.claude-plugin/`                                                                                                        |                         |
| `-h, --help`                                                                                                                                                                                                                                                                                                                                            | 顯示命令說明                                                                                                                              |                         |
| `claude plugin new` 是此命令的別名。 每個 `--with` 值都會為該元件新增一個入門檔案，準備好編輯：                                                                                                                                                                                                                                                         |                                                                                                                                           |                         |
| 元件                                                                                                                                                                                                                                                                                                                                                    | 建立的內容                                                                                                                                |                         |
| ---                                                                                                                                                                                                                                                                                                                                                     | ---                                                                                                                                       |                         |
| `skills`                                                                                                                                                                                                                                                                                                                                                | 一個額外的命名空間 `<name>:example` 技能，與預設技能並列                                                                                  |                         |
| `agents`                                                                                                                                                                                                                                                                                                                                                | 一個 `agents/` 子代理定義                                                                                                                 |                         |
| `hooks`                                                                                                                                                                                                                                                                                                                                                 | 一個 `hooks/hooks.json`，包含範例事件處理程式                                                                                             |                         |
| `mcp`                                                                                                                                                                                                                                                                                                                                                   | 一個 `.mcp.json`，包含 HTTP 和 stdio 伺服器範例                                                                                           |                         |
| `lsp`                                                                                                                                                                                                                                                                                                                                                   | 一個 `.lsp.json` 語言伺服器範例                                                                                                           |                         |
| `output-style`                                                                                                                                                                                                                                                                                                                                          | 一個 `output-styles/<name>.md`，在外掛程式啟用時自動套用                                                                                  |                         |
| `channel`                                                                                                                                                                                                                                                                                                                                               | 一個基於 MCP 的[頻道](https://code.claude.com/docs/zh-TW/channels)：一個 stdio 伺服器 (`server.ts`)、其 `.mcp.json` 和一個 `package.json` |                         |
| 建立框架的外掛程式使用 `@skills-dir` 來源，而不是市集。管理員可以使用 `strictKnownMarketplaces` 或在[受管設定](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)中新增 `{"source": "skills-dir"}` 至 `blockedMarketplaces` 來封鎖此來源。當被封鎖時，`plugin init` 會在寫入前失敗。 這些範例顯示常見的叫用方式： |                                                                                                                                           |                         |

```
# 建立最小外掛程式的框架
claude plugin init my-helper

# 使用技能和掛鉤資料夾建立框架
claude plugin init my-helper --with skills hooks

# 覆寫現有框架
claude plugin init my-helper --force

```

### plugin install

從可用市集安裝外掛程式。

```
claude plugin install <plugin> [options]

```

該命令接受這些引數：

- `<plugin>`：外掛程式名稱或 `plugin-name@marketplace-name` 以指定特定市集

該命令接受這些選項：

| 選項                                                                                                                                                                                                                                                                                                  | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 預設值 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `-s, --scope <scope>`                                                                                                                                                                                                                                                                                 | 安裝範圍：`user`、`project` 或 `local`                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `user` |
| `--config <key=value>`                                                                                                                                                                                                                                                                                | 設定外掛程式資訊清單中宣告的 [`userConfig`](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration) 選項。重複此旗標以設定多個選項                                                                                                                                                                                                                                                                                                                                                             |        |
| `-y, --yes`                                                                                                                                                                                                                                                                                           | 接受外掛程式市集宣告的命令，無需確認提示：產生具有 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)的外掛程式的命令，或驗證封存下載的 [`headersHelper`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#authenticate-archive-downloads)。接受 `headersHelper` 需要 Claude Code v2.1.238 或更新版本。Claude Code 仍會先列印命令。當 stdin 或 stdout 不是 TTY 時為必需，除非您傳遞 `--accept-command`。在 Claude Code 工作階段內無效，因此請從您自己的終端執行命令 |        |
| `--accept-command <sha256>`                                                                                                                                                                                                                                                                           | 接受市集宣告的命令，其 `sha256` 先前的 [`--json` 執行](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result)在 `shownCommand` 中報告，以取代 `-y`。接受計數適用於完全相同的命令、外掛程式和市集目錄。如果自命令顯示以來任何一個已變更，包括透過執行本身的市集重新整理，Claude Code 不會接受摘要並再次顯示命令。無法與 `-y` 結合。在 Claude Code 工作階段內無效，因此請從您自己的終端執行命令。需要 Claude Code v2.1.271 或更新版本                                                           |        |
| `--json`                                                                                                                                                                                                                                                                                              | 將結果列印為 stdout 最後一行的一個 JSON 物件，供指令碼使用。請參閱 [JSON 結果格式](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result)。需要 Claude Code v2.1.268 或更新版本                                                                                                                                                                                                                                                                                                               |        |
| `-h, --help`                                                                                                                                                                                                                                                                                          | 顯示命令說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |        |
| 範圍決定已安裝外掛程式新增至哪個設定檔。例如，`--scope project` 會寫入 .claude/settings.json 中的 `enabledPlugins`，使外掛程式可供複製專案存放庫的所有人使用。 使用 `--json` 時，stdout 的最後一行是一個 JSON 物件。只解析該行，因為 Claude Code 會在其前面列印市集宣告的任何命令。三個欄位始終存在： |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |        |

- `command`：執行的子命令，例如 `install`
- `outcome`：`ok` 或 `failed`
- `message`：結果的人類可讀說明

其他欄位，例如 `pluginId`、`scope` 和 `failureCode`，僅在適用時出現。`plugin uninstall`、`plugin update`、`plugin enable` 和 `plugin disable` 上的 `--json` 選項會列印具有該子命令自己欄位的相同物件。使用錯誤（例如無效的 `--scope`）不會列印結果行，並以 stderr 上的原因退出 1。 當執行顯示市集宣告的命令且不執行它時，`failed` 結果也會攜帶一個 `shownCommand` 物件，其欄位包括顯示的命令、它所屬的外掛程式和命令的 `sha256`。若要接受完全相同的命令，請使用該 `sha256` 作為 `--accept-command` 重新執行。需要 Claude Code v2.1.271 或更新版本。 如果 `shownCommand.acceptCommandMatched` 是 `false`，您傳遞的摘要與現在顯示的命令不符。在傳遞其 `sha256` 之前，向某人顯示該命令。 這些範例顯示常見的叫用方式：

```
# 安裝至使用者範圍（預設）
claude plugin install formatter@my-marketplace

# 安裝至專案範圍（與團隊共享）
claude plugin install formatter@my-marketplace --scope project

# 安裝至本機範圍（不與團隊共享）
claude plugin install formatter@my-marketplace --scope local

```

### plugin uninstall

移除已安裝的外掛程式。

```
claude plugin uninstall <plugin> [options]

```

該命令接受這些引數：

- `<plugin>`：外掛程式名稱或 `plugin-name@marketplace-name`

該命令接受這些選項：

| 選項                                                                                                                                                                                                       | 說明                                                                                                                                                                                                                      | 預設值 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `-s, --scope <scope>`                                                                                                                                                                                      | 從範圍解除安裝：`user`、`project` 或 `local`                                                                                                                                                                              | `user` |
| `--keep-data`                                                                                                                                                                                              | 保留外掛程式的[持久資料目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)                                                                                                              |        |
| `--prune`                                                                                                                                                                                                  | 同時移除其他外掛程式不再需要的自動安裝相依性。請參閱 [plugin prune](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-prune)                                                                                    |        |
| `-y, --yes`                                                                                                                                                                                                | 跳過 `--prune` 確認提示。當 stdin 或 stdout 不是 TTY 時為必需                                                                                                                                                             |        |
| `--json`                                                                                                                                                                                                   | 將結果列印為 stdout 最後一行的一個 JSON 物件，格式與 [`plugin install --json`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result) 相同。無法與 `--prune` 結合。需要 Claude Code v2.1.268 或更新版本 |        |
| `-h, --help`                                                                                                                                                                                               | 顯示命令說明                                                                                                                                                                                                              |        |
| `claude plugin remove` 和 `claude plugin rm` 是此命令的別名。 根據預設，從最後剩餘的範圍解除安裝也會刪除外掛程式的 `${CLAUDE_PLUGIN_DATA}` 目錄。使用 `--keep-data` 保留它，例如在測試新版本後重新安裝時。 |                                                                                                                                                                                                                           |        |
| 當來自不同市集的已安裝外掛程式共享名稱時，`plugin-name@marketplace-name` 形式只會解除安裝來自指定市集的外掛程式。在 v2.1.212 之前，合格形式可能會符合並解除安裝來自不同市集的同名外掛程式。                |                                                                                                                                                                                                                           |        |

### plugin prune

移除不再由任何已安裝外掛程式需要的自動安裝外掛程式相依性。Claude Code 為滿足另一個外掛程式的 [`dependencies`](https://code.claude.com/docs/zh-TW/plugin-dependencies) 欄位而拉入的相依性會被移除；您直接安裝的外掛程式永遠不會被觸及。

```
claude plugin prune [options]

```

該命令接受這些選項：

| 選項                                                                                                                                                                                    | 說明                                               | 預設值 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------ |
| `-s, --scope <scope>`                                                                                                                                                                   | 在範圍進行清理：`user`、`project` 或 `local`       | `user` |
| `--dry-run`                                                                                                                                                                             | 列出將被移除的內容，但不實際移除                   |        |
| `-y, --yes`                                                                                                                                                                             | 跳過確認提示。當 stdin 或 stdout 不是 TTY 時為必需 |        |
| `-h, --help`                                                                                                                                                                            | 顯示命令說明                                       |        |
| `claude plugin autoremove` 是此命令的別名。 該命令列出孤立的相依性，並在移除前要求確認。若要在一個步驟中移除外掛程式並清理其相依性，請執行 `claude plugin uninstall <plugin> --prune`。 |                                                    |        |

### plugin enable

啟用已停用的外掛程式。當目標從市集安裝並宣告[相依性](https://code.claude.com/docs/zh-TW/plugin-dependencies)時，Claude Code 會在相同範圍內以遞移方式啟用它們。該命令在[啟用或停用具有相依性的外掛程式](https://code.claude.com/docs/zh-TW/plugin-dependencies#enable-or-disable-a-plugin-with-dependencies)列出的條件下失敗。

```
claude plugin enable <plugin> [options]

```

該命令接受這些引數：

- `<plugin>`：外掛程式名稱、`plugin-name@marketplace-name` 或 `plugin-name@synced` 用於[從 claude.ai 同步的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)

該命令接受這些選項：

| 選項                  | 說明                                                                                                                                                                                               | 預設值   |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `-s, --scope <scope>` | 要啟用的範圍：`user`、`project` 或 `local`。省略時，Claude Code 會偵測安裝外掛程式的範圍                                                                                                           | 自動偵測 |
| `--json`              | 將結果列印為 stdout 最後一行的一個 JSON 物件，格式與 [`plugin install --json`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result) 相同。需要 Claude Code v2.1.268 或更新版本 |          |
| `-h, --help`          | 顯示命令說明                                                                                                                                                                                       |          |

### plugin disable

停用外掛程式而不解除安裝它。 當目標從市集安裝時，如果另一個已啟用的外掛程式[依賴](https://code.claude.com/docs/zh-TW/plugin-dependencies#enable-or-disable-a-plugin-with-dependencies)它，該命令會失敗。錯誤訊息包含一個鏈式命令，可先停用每個依賴它的外掛程式。 對於您的組織需要的[同步外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)，該命令會失敗且不會儲存任何內容。

```
claude plugin disable [plugin] [options]

```

該命令接受這些引數：

- `[plugin]`：外掛程式名稱、`plugin-name@marketplace-name` 或 `plugin-name@synced` 用於[從 claude.ai 同步的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)。使用 `--all` 時為選用。

該命令接受這些選項：

| 選項                  | 說明                                                                                                                                                                                               | 預設值   |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `-a, --all`           | 停用所有已啟用的外掛程式。無法與 `--scope` 結合                                                                                                                                                    |          |
| `-s, --scope <scope>` | 要停用的範圍：`user`、`project` 或 `local`。省略時，Claude Code 會偵測安裝外掛程式的範圍                                                                                                           | 自動偵測 |
| `--json`              | 將結果列印為 stdout 最後一行的一個 JSON 物件，格式與 [`plugin install --json`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result) 相同。需要 Claude Code v2.1.268 或更新版本 |          |
| `-h, --help`          | 顯示命令說明                                                                                                                                                                                       |          |

### plugin update

將外掛程式更新至最新版本。

```
claude plugin update <plugin> [options]

```

該命令接受這些引數：

- `<plugin>`：外掛程式名稱或 `plugin-name@marketplace-name`

該命令接受這些選項：

| 選項                                                                                                                                                                                                                                                 | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 預設值 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `-s, --scope <scope>`                                                                                                                                                                                                                                | 要更新的範圍：`user`、`project`、`local` 或 `managed`                                                                                                                                                                                                                                                                                                                                                                                                                                                           | `user` |
| `-y, --yes`                                                                                                                                                                                                                                          | 接受外掛程式市集宣告的命令，無需確認提示：產生具有 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)的外掛程式的命令，或驗證封存下載的 [`headersHelper`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#authenticate-archive-downloads)。接受 `headersHelper` 需要 Claude Code v2.1.238 或更新版本。Claude Code 仍會先列印命令。當 stdin 或 stdout 不是 TTY 時為必需，除非您傳遞 `--accept-command`。在 Claude Code 工作階段內無效，因此請從您自己的終端執行命令 |        |
| `--accept-command <sha256>`                                                                                                                                                                                                                          | 接受市集宣告的命令，其 `sha256` 先前的 [`--json` 執行](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result)在 `shownCommand` 中報告，以取代 `-y`。接受計數適用於完全相同的命令、外掛程式和市集目錄。如果自命令顯示以來任何一個已變更，包括透過執行本身的市集重新整理，Claude Code 不會接受摘要並再次顯示命令。無法與 `-y` 結合。在 Claude Code 工作階段內無效，因此請從您自己的終端執行命令。需要 Claude Code v2.1.271 或更新版本                                                           |        |
| `--json`                                                                                                                                                                                                                                             | 將結果列印為 stdout 最後一行的一個 JSON 物件，格式與 [`plugin install --json`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-json-result) 相同。需要 Claude Code v2.1.268 或更新版本                                                                                                                                                                                                                                                                                                              |        |
| `-h, --help`                                                                                                                                                                                                                                         | 顯示命令說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |        |
| Claude Code 根據您已安裝的外掛程式解析裸外掛程式名稱。當來自不同市集的已安裝外掛程式共享名稱時，Claude Code 會拒絕更新並列出要執行的合格 `plugin-name@marketplace-name` 命令。在 v2.1.246 之前，Claude Code 只接受合格形式，並將裸名稱拒絕為未找到。 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |        |

______________________________________________________________________

### plugin list

列出已安裝的外掛程式及其版本、來源市集和啟用狀態。

```
claude plugin list [options]

```

該命令接受這些選項：

| 選項                                                                                    | 說明                                                                                                                                                                                                                                              | 預設值 |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `--json`                                                                                | 輸出為 JSON。具有載入問題或編寫警告的外掛程式列會攜帶 `errors` 或 `notes` 字串陣列。在 Claude Code v2.1.268 或更新版本上，平行的 `errorDetails` 和 `noteDetails` 陣列會提供每個項目的診斷 `type` 和它所指的名稱，例如外掛程式、市集、伺服器或檔案 |        |
| `--available`                                                                           | 包含市集中的可用外掛程式。需要 `--json`                                                                                                                                                                                                           |        |
| `-h, --help`                                                                            | 顯示命令說明                                                                                                                                                                                                                                      |        |
| 在互動式工作階段中，`/plugin list` 會列印類似的列表內容，但它只涵蓋市集安裝的外掛程式： |                                                                                                                                                                                                                                                   |        |

- 從技能目錄載入的外掛程式會在 `/plugin` 介面和 `claude plugin list` 中出現，但不會在內嵌 `/plugin list` 輸出中出現。
- [從 claude.ai 同步的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)會在 Claude Code v2.1.239 或更新版本上的 `claude plugin list` 中出現，並在 `/plugin` 介面中出現，但不會在內嵌 `/plugin list` 輸出中出現。
- 使用 `--plugin-dir` 或 `--plugin-url` 為工作階段載入的外掛程式會在 `/plugin` 介面中出現，並且在相同旗標位於子命令前時才會在 `claude plugin list` 中出現，如 `claude --plugin-dir <dir> plugin list`。只有旗標名稱會指出它們的位置，因此裸 `claude plugin list` 無法找到它們，不同於同步外掛程式和技能目錄外掛程式，Claude Code 會掃描其固定目錄。

互動式形式接受 `--enabled` 或 `--disabled` 以僅顯示該狀態中的外掛程式，並接受 `ls` 作為 `list` 的簡寫。

### plugin details

顯示外掛程式的元件清單和預計權杖成本。輸出列出外掛程式貢獻的所有元件，分組為技能、代理、掛鉤、MCP 伺服器和 LSP 伺服器，以及它為每個工作階段新增多少權杖的估計。技能群組包括 `skills/` 和 `commands/` 項目。

```
claude plugin details <name>

```

該命令接受這些引數：

- `<name>`：外掛程式名稱或 `plugin-name@marketplace-name`

該命令接受這些選項：

| 選項                             | 說明         | 預設值 |
| -------------------------------- | ------------ | ------ |
| `-h, --help`                     | 顯示命令說明 |        |
| 輸出為每個元件顯示兩個成本數字： |              |        |

- **Always-on：** 外掛程式的列表文字（例如技能說明、代理說明和命令名稱）無論任何元件是否觸發，都會新增至每個工作階段的權杖。
- **On-invoke：** 元件觸發時的成本。按元件顯示，而不是外掛程式總計，因為典型工作階段只會叫用元件的子集。

此範例顯示具有兩個技能的外掛程式的輸出外觀：

```
dependency-guard 1.2.0
  Dependency analysis for Claude Code sessions
  Source: dependency-guard@example-marketplace

Component inventory
  Skills (2)  scan-dependencies, review-changes
  Agents (0)
  Hooks (1)  SessionStart  (harness-only — no model context cost)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~180 tok   added to every session

Per-component (rounded)
  component            always-on  on-invoke
  scan-dependencies        ~100      ~2400
  review-changes            ~80      ~1800

  On-invoke cost is paid each time a skill or agent fires.
  Token counts are estimates and may differ from actual usage.

```

always-on 總計是透過您的作用中模型的 `count_tokens` API 計算的。按元件的數字按比例從該總計縮放。如果 API 無法到達，該命令會回退至基於字元的估計。

### plugin validate

在發佈前檢查外掛程式或市集是否有語法和結構描述錯誤。 當驗證通過時命令退出 0，失敗時退出 1，驗證執行本身失敗時退出 2，例如當您傳遞的路徑無法讀取時。

```
claude plugin validate <path> [options]

```

該命令接受這些引數：

- `<path>`：外掛程式目錄或市集目錄的路徑。請參閱[驗證沒有資訊清單的外掛程式或目錄](https://code.claude.com/docs/zh-TW/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest)以了解外掛程式執行涵蓋的檔案。

該命令接受這些選項：

| 選項                                                                                     | 說明                                                                                                                                                                 | 預設值 |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `--strict`                                                                               | 將警告視為錯誤，並在警告時退出 1。在 CI 中使用以捕捉執行時容許的問題，例如[無法識別的欄位](https://code.claude.com/docs/zh-TW/plugins-reference#unrecognized-fields) |        |
| `--json`                                                                                 | 將驗證報告輸出為一個 JSON 物件，具有相同的退出代碼。需要 Claude Code v2.1.259 或更新版本                                                                             |        |
| `-h, --help`                                                                             | 顯示命令說明                                                                                                                                                         |        |
| 使用 `--json` 時，Claude Code 會將報告寫入 stdout 作為一個 JSON 物件，具有這些頂層欄位： |                                                                                                                                                                      |        |

- `success`：退出代碼給出的相同判決
- `strict`：執行是否將警告視為錯誤
- `target`：Claude Code 驗證的已解析路徑
- `manifest`：資訊清單本身的結果，或 `null` 用於[沒有資訊清單的執行](https://code.claude.com/docs/zh-TW/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest)
- `contents`：按檔案結果，每個命名其 `file` 並攜帶 `errors`、`warnings` 和 `notes` 陣列

退出 2 時，該命令不會向 stdout 寫入任何內容；錯誤訊息會進入 stderr。 在互動式工作階段中，`/plugin validate <path>` 會內嵌執行相同的檢查。

### plugin eval

執行外掛程式的[評估案例](https://code.claude.com/docs/zh-TW/plugin-evals)並報告評分結果。需要 Claude Code v2.1.269 或更新版本。每個案例都是一個提示加評分者；Claude Code 在隔離的工作階段中執行它多次，只載入目標外掛程式，預設情況下也不載入外掛程式，以便報告顯示差異。請參閱[使用評估測試外掛程式](https://code.claude.com/docs/zh-TW/plugin-evals)以了解案例格式、評分者、結果和 CI 使用。

```
claude plugin eval [target] [options]

```

選用的 `target` 是外掛程式目錄、單個 `prompt.md` 或 `case.yaml` 檔案、已安裝的外掛程式作為 `name` 或 `name@marketplace`，或 `name@skills-dir`，預設為目前目錄。將其放在 `--tag`、`--allow-tools` 和 `--json` 之前。 此表列出大多數執行使用的選項。執行 `claude plugin eval --help` 以取得完整集合，包括 `--case`、`--tag`、`--output-dir`、`--report`、`--allow-real-servers`、`--keep-temp` 和 `--verbose`。

| 選項                                                                                                                                                                                                                                      | 說明                                                                                                                                                                        | 預設值                                                                            |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `--runs <n>`                                                                                                                                                                                                                              | 每個案例每個臂的執行次數                                                                                                                                                    | 每個案例的 `runs`，否則 3                                                         |
| `-j, --concurrency <n>`                                                                                                                                                                                                                   | 同時執行的代理工作階段，1 到 8。它們共享您的速率限制                                                                                                                        | `1`                                                                               |
| `--model <model>`                                                                                                                                                                                                                         | 受測代理的模型                                                                                                                                                              | 每個案例的 `model`，否則 `ANTHROPIC_MODEL`（如果設定），否則 Claude Code 的預設值 |
| `--judge-model <model>`                                                                                                                                                                                                                   | `llm` 和 `baseline` 評分者的模型                                                                                                                                            | 一個小型快速模型                                                                  |
| `--ablation <mode>`                                                                                                                                                                                                                       | `none` 或 `with-without`。請參閱[與無外掛程式基線比較](https://code.claude.com/docs/zh-TW/plugin-evals#compare-against-a-no-plugin-baseline)                                | 當外掛程式解析時為 `with-without`，否則為 `none`                                  |
| `--threshold <0..1>`                                                                                                                                                                                                                      | 如果任何案例評分低於此值，退出 1                                                                                                                                            | `1.0`                                                                             |
| `--max-cost-usd <usd>`                                                                                                                                                                                                                    | 一旦支出達到此值，停止下一次執行，退出 2，並報告部分結果                                                                                                                    | 無上限                                                                            |
| `--allow-tools <tools...>`                                                                                                                                                                                                                | 授予超過唯讀集合的工具，例如 `Bash`、`Write`、`Edit` 或 `"mcp__plugin_<plugin>_<server>__*"`。請參閱[授予工具](https://code.claude.com/docs/zh-TW/plugin-evals#grant-tools) |                                                                                   |
| `--scaffold`                                                                                                                                                                                                                              | 執行每個案例的 [`scaffold_script`](https://code.claude.com/docs/zh-TW/plugin-evals#add-setup-or-history-with-case-yaml)                                                     | 關閉                                                                              |
| `--trust-plugin`                                                                                                                                                                                                                          | 跳過首次執行信任提示，用於 CI。請參閱[執行可以存取的內容](https://code.claude.com/docs/zh-TW/plugin-evals#security)                                                         | 關閉                                                                              |
| `--mocks <mode>`                                                                                                                                                                                                                          | `record` 或 `off`。請參閱[模擬 MCP 伺服器](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers)                                                                | `record`                                                                          |
| `--eval-dir <dir>`                                                                                                                                                                                                                        | 保存案例的外掛程式下方的目錄                                                                                                                                                | 資訊清單的 `experimental.evals`，否則 `evals`                                     |
| `--json [path]`                                                                                                                                                                                                                           | 將[結果文件](https://code.claude.com/docs/zh-TW/plugin-evals#json-result)列印至 stdout，或將其寫入 `.json` 路徑                                                             |                                                                                   |
| `--no-publish`                                                                                                                                                                                                                            | 保持 HTML 報告本機                                                                                                                                                          |                                                                                   |
| `-h, --help`                                                                                                                                                                                                                              | 顯示命令說明                                                                                                                                                                |                                                                                   |
| 當每個案例都符合閾值時，命令退出 0，在失敗案例、載入錯誤或不受信任的外掛程式目錄時退出 1，在部分執行時退出 2，中斷時退出 130，終止時退出 143。請參閱[在 CI 中執行評估](https://code.claude.com/docs/zh-TW/plugin-evals#run-evals-in-ci)。 |                                                                                                                                                                             |                                                                                   |

### plugin eval init

為目前目錄中的外掛程式建立評估套件。需要 Claude Code v2.1.269 或更新版本。在終端中，這會啟動一個編寫訪談，讀取外掛程式、提議案例和評分者、試驗它們，並寫入檔案。使用 `--bare` 或沒有終端時，它會改為寫入一個空白的單案例範本。從互動式 Claude Code 工作階段內執行時，它會列印該工作階段要遵循的訪談說明，而不是寫入範本。請參閱[建立您的第一個評估套件](https://code.claude.com/docs/zh-TW/plugin-evals#create-your-first-eval-suite)。

```
claude plugin eval init [name] [options]

```

選用的 `name` 是案例名稱：訪談不需要一個，而 `--bare` 和無終端範本路徑需要一個。它接受這些選項：

| 選項                | 說明                                                          | 預設值                                        |
| ------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| `--bare`            | 改為為 `<name>` 寫入空白 `prompt.md` 和 `graders/criteria.md` |                                               |
| `-i, --interactive` | 需要訪談。沒有終端時失敗，而不是寫入範本                      |                                               |
| `--eval-dir <dir>`  | 目前目錄下方寫入案例的目錄                                    | 資訊清單的 `experimental.evals`，否則 `evals` |
| `-h, --help`        | 顯示命令說明                                                  |                                               |

### plugin tag

為外掛程式建立發行 git 標籤。根據預設，該命令會標籤目前目錄中的外掛程式；傳遞路徑以標籤其他位置的外掛程式。請參閱[標籤外掛程式發行](https://code.claude.com/docs/zh-TW/plugin-dependencies#tag-plugin-releases-for-version-resolution)。

```
claude plugin tag [path] [options]

```

該命令接受這些引數：

- `[path]`：外掛程式目錄的路徑。預設為目前目錄。

該命令接受這些選項：

| 選項                  | 說明                                       | 預設值   |
| --------------------- | ------------------------------------------ | -------- |
| `--push`              | 建立標籤後將其推送至遠端                   |          |
| `--dry-run`           | 列印將被標籤的內容，但不建立標籤           |          |
| `-f, --force`         | 即使工作樹髒污或標籤已存在，也建立標籤     |          |
| `-m, --message <msg>` | 標籤註解訊息。使用 `%s` 作為版本的預留位置 |          |
| `--remote <name>`     | 使用 `--push` 推送至的遠端                 | `origin` |
| `-h, --help`          | 顯示命令說明                               |          |

______________________________________________________________________

## 除錯和開發工具

### 除錯命令

使用 `claude --debug` 查看外掛程式載入詳細資訊： 這會顯示：

- 正在載入哪些外掛程式
- 外掛程式清單中的任何錯誤
- Skill、agent 和 hook 註冊
- MCP 伺服器初始化

### 常見問題

| 問題                                | 原因                         | 解決方案                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 外掛程式未載入                      | 無效的 `plugin.json`         | 執行 `claude plugin validate ./my-plugin` 或 `/plugin validate ./my-plugin`，其中 `./my-plugin` 是您的外掛程式目錄，以檢查 `plugin.json`、`hooks/hooks.json` 以及外掛程式預設目錄中的 skills、agents 和 commands 的前置資訊是否有語法和結構描述錯誤。請參閱[驗證外掛程式或沒有清單的目錄](https://code.claude.com/docs/zh-TW/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest)以了解執行涵蓋的內容 |
| Skills 未出現                       | 目錄結構錯誤                 | 確保 `skills/` 或 `commands/` 位於外掛程式根目錄，而不是在 `.claude-plugin/` 內                                                                                                                                                                                                                                                                                                                                           |
| Hooks 未觸發                        | 指令碼不可執行               | 執行 `chmod +x script.sh`                                                                                                                                                                                                                                                                                                                                                                                                 |
| MCP 伺服器失敗                      | 缺少 `${CLAUDE_PLUGIN_ROOT}` | 對所有外掛程式路徑使用變數                                                                                                                                                                                                                                                                                                                                                                                                |
| 路徑錯誤                            | 使用了絕對路徑               | 使路徑相對，以 `./` 開頭；請參閱[路徑行為規則](https://code.claude.com/docs/zh-TW/plugins-reference#path-behavior-rules)，其中涵蓋了 `skills` 欄位的 `"."` 例外                                                                                                                                                                                                                                                           |
| LSP `Executable not found in $PATH` | 語言伺服器未安裝             | 安裝二進位檔案（例如，`npm install -g typescript-language-server typescript`）                                                                                                                                                                                                                                                                                                                                            |

### 範例錯誤訊息

**清單驗證錯誤** ：

- `Invalid JSON syntax: Unexpected token } in JSON at position 142`：檢查是否缺少逗號、多餘逗號或未加引號的字串
- `Plugin <name> has an invalid manifest file at .claude-plugin/plugin.json. Validation errors: name: Invalid input: expected string, received undefined`：缺少必需欄位
- `Plugin <name> has a corrupt manifest file at .claude-plugin/plugin.json. JSON parse error: ...`：JSON 語法錯誤。在 v2.1.246 之前，Claude Code 也會針對以位元組順序標記 (BOM) 儲存為 UTF-8 的 `plugin.json` 產生此錯誤，即使 JSON 在其他方面有效。

**外掛程式載入錯誤** ：

- `Warning: No commands found in plugin my-plugin custom directory: ./cmds. Expected .md files or SKILL.md in subdirectories.`：命令路徑存在但不包含有效的命令檔案
- `Plugin directory not found at path: ./plugins/my-plugin. Check that the marketplace entry has the correct path.`：marketplace.json 中的 `source` 路徑指向不存在的目錄
- `Plugin my-plugin has conflicting manifests: both plugin.json and marketplace entry specify components.`：移除重複的元件定義或移除 marketplace 項目中的 `strict: false`

### Hook 除錯

**Hook 指令碼未執行** ：

1. 檢查指令碼是否可執行：`chmod +x ./scripts/your-script.sh`
1. 驗證 shebang 行：第一行應為 `#!/bin/bash` 或 `#!/usr/bin/env bash`
1. 檢查路徑是否使用 `${CLAUDE_PLUGIN_ROOT}`：`"command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/your-script.sh"`
1. 手動測試指令碼：`./scripts/your-script.sh`

**Hook 未在預期事件上觸發** ：

1. 驗證事件名稱正確（區分大小寫）：`PostToolUse`，而不是 `postToolUse`
1. 檢查匹配器模式是否與您的工具相符：`"matcher": "Write|Edit"` 用於檔案操作
1. 確認 hook 類型有效：`command`、`http`、`mcp_tool`、`prompt` 或 `agent`

### MCP 伺服器除錯

**伺服器未啟動** ：

1. 檢查命令是否存在且可執行
1. 驗證所有路徑都使用 `${CLAUDE_PLUGIN_ROOT}` 變數
1. 檢查 MCP 伺服器日誌：`claude --debug` 顯示初始化錯誤
1. 在 Claude Code 外手動測試伺服器

**伺服器工具未出現** ：

1. 確保伺服器在 `.mcp.json` 或 `plugin.json` 中正確設定
1. 驗證伺服器正確實作 MCP 協定
1. 檢查除錯輸出中的連線逾時

### 目錄結構錯誤

**症狀** ：外掛程式載入但元件（skills、agents、hooks）遺失。 **正確結構** ：元件必須位於外掛程式根目錄，而不是在 `.claude-plugin/` 內。只有 `plugin.json` 屬於 `.claude-plugin/`。 **除錯檢查清單** ：

1. 執行 `claude --debug` 並查找「loading plugin」訊息
1. 檢查每個元件目錄是否列在除錯輸出中
1. 驗證檔案權限允許讀取外掛程式檔案

______________________________________________________________________

## 發佈和版本管理參考

### 版本管理

Claude Code 使用外掛程式的版本作為快取金鑰，以判斷是否有可用的更新。當您執行 `/plugin update` 或自動更新觸發時，Claude Code 會計算目前版本，如果與已安裝的版本相符，則跳過更新。從[本機目錄市集](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)載入的外掛程式會在每次工作階段開始時載入其目前的來源檔案，無論其版本字串說什麼。 對於除了 `command` 以外的每種來源類型，Claude Code 會從以下第一個已設定的項目解析版本：

1. 外掛程式 `plugin.json` 中的 `version` 欄位
1. 外掛程式在 `marketplace.json` 中的市集項目中的 `version` 欄位
1. 外掛程式來源的 git 提交 SHA，適用於 git 託管市集中的 `github`、`url`、`git-subdir` 和相對路徑來源
1. SHA-256 摘要，適用於 [`archive` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#zip-archives)：市集項目中的 `sha256` 釘選，或當您未設定釘選時下載檔案的摘要。Claude Code 將其縮短為前 12 個字元
1. `unknown`，適用於 `npm` 來源或不在 git 儲存庫內的本機目錄。Claude Code 不會從包含安裝路徑的儲存庫（例如 git 管理的 `~/.claude`）中取得版本

對於 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)，Claude Code 始終從命令產生的內容衍生版本：單獨的 12 字元內容雜湊，或在設定了一個時附加到 `plugin.json` 版本作為 `<version>-<hash>`。Claude Code 會忽略命令來源的市集項目 `version` 欄位。因此，命令的雜湊輸出變更會產生新版本，即使編寫的版本字串保持不變。在[連結模式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode)中，雜湊涵蓋列印目錄的實際路徑及其頂層項目，而不是檔案內容。 對於這些來源類型，這為您提供了三種方式來版本化外掛程式：

| 方法                                                                                                                                                                                      | 如何操作                                                                                                                                | 更新行為                                                                                                                                                                                                                                           | 最適合                                              |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **明確版本**                                                                                                                                                                              | 在 `plugin.json` 中設定 `"version": "2.1.0"`                                                                                            | 使用者只有在您更新此欄位時才會獲得更新。推送新提交而不更新它沒有效果，`/plugin update` 會報告「已是最新版本」。對於[本機載入](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)的外掛程式，新內容仍會載入。 | 具有穩定發佈週期的已發佈外掛程式                    |
| **提交 SHA 版本**                                                                                                                                                                         | 從 `plugin.json` 和市集項目中省略 `version`                                                                                             | 每當來源的已解析提交變更時，使用者都會獲得更新                                                                                                                                                                                                     | 正在積極開發中的內部或團隊外掛程式                  |
| **摘要版本**                                                                                                                                                                              | 使用 [`archive` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#zip-archives)並從 `plugin.json` 和市集項目中省略 `version` | 使用 `sha256` 釘選時，使用者在您變更釘選時獲得更新。沒有釘選時，使用者在託管 zip 檔案的位元組變更時獲得更新                                                                                                                                        | 作為 zip 檔案發佈到靜態伺服器或成品儲存庫的外掛程式 |
| 如果您使用明確版本，請遵循[語義版本控制](https://semver.org)（`MAJOR.MINOR.PATCH`）：針對重大變更更新 MAJOR，針對新功能更新 MINOR，針對錯誤修正更新 PATCH。在 `CHANGELOG.md` 中記錄變更。 |                                                                                                                                         |                                                                                                                                                                                                                                                    |                                                     |

______________________________________________________________________

## 另請參閱

- [Plugins](https://code.claude.com/docs/zh-TW/plugins) - 教學和實際使用
- [Plugin marketplaces](https://code.claude.com/docs/zh-TW/plugin-marketplaces) - 建立和管理 marketplaces
- [Skills](https://code.claude.com/docs/zh-TW/skills) - Skill 開發詳細資訊
- [Subagents](https://code.claude.com/docs/zh-TW/sub-agents) - Agent 設定和功能
- [Hooks](https://code.claude.com/docs/zh-TW/hooks) - 事件處理和自動化
- [MCP](https://code.claude.com/docs/zh-TW/mcp) - 外部工具整合
- [Settings](https://code.claude.com/docs/zh-TW/settings) - Plugins 的設定選項

是否 助手
