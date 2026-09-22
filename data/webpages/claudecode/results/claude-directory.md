Claude Code 從您的專案目錄和主目錄中的 `~/.claude` 讀取指令、設定、skills、subagents 和記憶。將專案檔案提交到 git 以與您的團隊共享；`~/.claude` 中的檔案是個人設定，適用於您的所有專案。 在 Windows 上，`~/.claude` 解析為 `%USERPROFILE%\.claude`。如果您設定了 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars)，此頁面上的每個 `~/.claude` 路徑都會改為位於該目錄下。 大多數使用者只編輯 `CLAUDE.md` 和 `settings.json`。如果您的儲存庫已經有一個 `AGENTS.md` 供其他編碼代理使用，Claude Code [可以自行讀取](https://code.claude.com/docs/zh-TW/memory#agents-md)或與 `CLAUDE.md` 一起讀取。目錄的其餘部分是可選的：根據需要新增 skills、rules 或 subagents。

## 探索目錄

點擊樹中的檔案以查看每個檔案的功能、何時載入以及範例。 The interactive explorer works best on a larger screen. See the [file reference table](https://code.claude.com/docs/zh-TW/claude-directory#file-reference) below, or show the explorer anyway. ProjectGlobal (~/)⊞⛶ CLAUDE.md {}.mcp.json .worktreeinclude ▾.claude/ {}settings.json {}settings.local.json ▾rules/ testing.md api-design.md ▾skills/ ▾security-review/ SKILL.md checklist.md ▾commands/ fix-issue.md ▸output-styles/ ▾agents/ code-reviewer.md ▸workflows/ ▾agent-memory/ ▾<agent-name>/ MEMORY.md CLAUDE.md selected your-project / CLAUDE.md CLAUDE.md Project instructions Claude reads every session committed When it loads Loaded into context at the start of every session Project-specific instructions that shape how Claude works in this repository. Put your conventions, common commands, and architectural context here so Claude operates with the same assumptions your team does. Tips ●Target under 200 lines. Longer files still load in full but may reduce adherence ●CLAUDE.md loads into every session. If something only matters for specific tasks, move it to a [skill](https://code.claude.com/docs/en/skills) or a path-scoped [rule](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/) so it loads only when needed ●List the commands you run most, like build, test, and format, so Claude knows them without you spelling them out each time ●Run `/memory` to open and edit CLAUDE.md from within a session ●Also works at `.claude/CLAUDE.md` if you prefer to keep the project root clean ●If your repo already has an `AGENTS.md` for other coding agents, Claude Code [can read that](https://code.claude.com/docs/en/memory#agents-md) on its own or alongside CLAUDE.md This example is for a TypeScript and React project. It lists the build and test commands, the framework conventions Claude should follow, and project-specific rules like export style and file layout. CLAUDE.mdCopy

```
# Project conventions

## Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

## Stack
- TypeScript with strict mode
- React 19, functional components only

## Rules
- Named exports, never default exports
- Tests live next to source: `foo.ts` -> `foo.test.ts`
- All API routes return `{ data, error }` shape
```

[Full docs →](https://code.claude.com/docs/en/memory)

## 未顯示的內容

探索器涵蓋您編寫和編輯的檔案。一些相關檔案位於其他位置：

| 檔案                                                                                                                                                                                                  | 位置                              | 用途                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `managed-settings.json`                                                                                                                                                                               | 系統層級，因作業系統而異          | 企業強制執行的設定，您無法覆寫，除了[狹隘的例外](https://code.claude.com/docs/zh-TW/settings#security-keys-where-the-stricter-value-applies)。請參閱[檔案儲存位置](https://code.claude.com/docs/zh-TW/managed-settings#deploy-a-managed-settings-file)和[Claude Code 使用的受管來源](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)。                                                                                                                                                                                                                                                                              |
| `CLAUDE.local.md`                                                                                                                                                                                     | 專案根目錄                        | 此專案的私人偏好設定，與 CLAUDE.md 一起載入。手動建立並將其新增至 `.gitignore`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `AGENTS.md`                                                                                                                                                                                           | 專案根目錄、`.claude/` 或任何目錄 | 您為 AI 編碼代理撰寫的專案指示。Claude Code 可以[自行載入](https://code.claude.com/docs/zh-TW/memory#agents-md)或與 `CLAUDE.md` 一起載入。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 已安裝的 plugins                                                                                                                                                                                      | `~/.claude/plugins`               | 複製的市集、已安裝的 plugin 版本和各 plugin 資料，由 `claude plugin` 命令管理。對於從市集[`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)以連結模式安裝的 plugin，Claude Code 在此儲存連結而非副本，plugin 的檔案保留在命令列印的目錄中。`command` 來源需要 Claude Code v2.1.229 或更新版本。本地目錄市集中以相對路徑列出的 plugin 也會[就地載入](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)其來源目錄，而不是從快取副本載入。請參閱 [plugin 快取](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)以了解孤立版本如何被清理。 |
| `~/.claude` 也保存 Claude Code 在您工作時寫入的資料：文字記錄、提示歷史記錄、檔案快照、快取和日誌。請參閱下方的[應用程式資料](https://code.claude.com/docs/zh-TW/claude-directory#application-data)。 |                                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

## 選擇正確的檔案

不同類型的自訂設定位於不同的檔案中。使用此表格找到變更應該位於何處。

| 您想要                              | 編輯                                     | 範圍       | 參考                                                                                                             |
| ----------------------------------- | ---------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------- |
| 為 Claude 提供專案上下文和慣例      | `CLAUDE.md`                              | 專案或全域 | [Memory](https://code.claude.com/docs/zh-TW/memory)                                                              |
| 允許或阻止特定工具呼叫              | `settings.json` `permissions` 或 `hooks` | 專案或全域 | [Permissions](https://code.claude.com/docs/zh-TW/permissions)、[Hooks](https://code.claude.com/docs/zh-TW/hooks) |
| 在工具呼叫之前或之後執行指令碼      | `settings.json` `hooks`                  | 專案或全域 | [Hooks](https://code.claude.com/docs/zh-TW/hooks)                                                                |
| 為工作階段設定環境變數              | `settings.json` `env`                    | 專案或全域 | [Settings](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)                                   |
| 將個人覆蓋保留在 git 之外           | `settings.local.json`                    | 僅專案     | [Settings scopes](https://code.claude.com/docs/zh-TW/settings#where-settings-live)                               |
| 新增您使用 `/name` 叫用的提示或功能 | `skills/<name>/SKILL.md`                 | 專案或全域 | [Skills](https://code.claude.com/docs/zh-TW/skills)                                                              |
| 定義具有自己工具的專門 subagent     | `agents/*.md`                            | 專案或全域 | [Subagents](https://code.claude.com/docs/zh-TW/sub-agents)                                                       |
| 透過指令碼協調許多 subagent         | `workflows/*.js`                         | 專案或全域 | [Dynamic workflows](https://code.claude.com/docs/zh-TW/workflows)                                                |
| 透過 MCP 連接外部工具               | `.mcp.json`                              | 僅專案     | [MCP](https://code.claude.com/docs/zh-TW/mcp)                                                                    |
| 變更 Claude 格式化回應的方式        | `output-styles/*.md`                     | 專案或全域 | [Output styles](https://code.claude.com/docs/zh-TW/output-styles)                                                |

## 檔案參考

此表列出探索器涵蓋的每個檔案。專案範圍的檔案位於您的儲存庫中的 `.claude/` 下（或 `CLAUDE.md`、`.mcp.json` 和 `.worktreeinclude` 的根目錄）。全域範圍的檔案位於 `~/.claude/` 中，適用於所有專案。 有幾件事可以覆蓋您在這些檔案中放入的內容：

- 您的組織部署的[受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)優先於所有內容，除了[設定優先順序下的例外](https://code.claude.com/docs/zh-TW/settings#exceptions-to-managed-settings-precedence)
- CLI 旗標（如 `--permission-mode` 或 `--settings`）會覆蓋該工作階段的 `settings.json`
- 某些環境變數優先於其等效設定，但這會有所不同：檢查[環境變數參考](https://code.claude.com/docs/zh-TW/env-vars)以了解每個變數

請參閱[設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)以了解完整順序。 點擊檔案名稱以在上方的探索器中開啟該節點。

| 檔案                                                                                                   | 範圍       | 提交 | 功能                                                                                   | 參考                                                                                           |
| ------------------------------------------------------------------------------------------------------ | ---------- | ---- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`CLAUDE.md`](https://code.claude.com/docs/zh-TW/claude-directory#ce-claude-md)                        | 專案和全域 | ✓    | 每個工作階段載入的指令                                                                 | [Memory](https://code.claude.com/docs/zh-TW/memory)                                            |
| [`rules/*.md`](https://code.claude.com/docs/zh-TW/claude-directory#ce-rules)                           | 專案和全域 | ✓    | 主題範圍的指令，可選擇路徑限制                                                         | [Rules](https://code.claude.com/docs/zh-TW/memory#organize-rules-with-claude/rules/)           |
| [`settings.json`](https://code.claude.com/docs/zh-TW/claude-directory#ce-settings-json)                | 專案和全域 | ✓    | 權限、hooks、環境變數、模型預設值                                                      | [Settings](https://code.claude.com/docs/zh-TW/settings)                                        |
| [`settings.local.json`](https://code.claude.com/docs/zh-TW/claude-directory#ce-settings-local-json)    | 僅專案     |      | 您的個人覆蓋，當 Claude Code 將設定儲存到其中時會自動 gitignored                       | [Settings scopes](https://code.claude.com/docs/zh-TW/settings#where-settings-live)             |
| [`.mcp.json`](https://code.claude.com/docs/zh-TW/claude-directory#ce-mcp-json)                         | 僅專案     | ✓    | 團隊共享的 MCP 伺服器                                                                  | [MCP scopes](https://code.claude.com/docs/zh-TW/mcp#mcp-installation-scopes)                   |
| [`.worktreeinclude`](https://code.claude.com/docs/zh-TW/claude-directory#ce-worktreeinclude)           | 僅專案     | ✓    | Gitignored 檔案以複製到新的 worktrees                                                  | [Worktrees](https://code.claude.com/docs/zh-TW/worktrees#copy-gitignored-files-into-worktrees) |
| [`skills/<name>/SKILL.md`](https://code.claude.com/docs/zh-TW/claude-directory#ce-skills)              | 專案和全域 | ✓    | 可重複使用的提示，使用 `/name` 叫用或自動叫用                                          | [Skills](https://code.claude.com/docs/zh-TW/skills)                                            |
| [`commands/*.md`](https://code.claude.com/docs/zh-TW/claude-directory#ce-commands)                     | 專案和全域 | ✓    | 單檔案提示；與 skills 相同的機制                                                       | [Skills](https://code.claude.com/docs/zh-TW/skills)                                            |
| [`output-styles/*.md`](https://code.claude.com/docs/zh-TW/claude-directory#ce-output-styles)           | 專案和全域 | ✓    | 自訂指令集，調整 Claude 的工作方式                                                     | [Output styles](https://code.claude.com/docs/zh-TW/output-styles)                              |
| [`agents/*.md`](https://code.claude.com/docs/zh-TW/claude-directory#ce-agents)                         | 專案和全域 | ✓    | Subagent 定義及其自己的提示和工具                                                      | [Subagents](https://code.claude.com/docs/zh-TW/sub-agents)                                     |
| [`workflows/*.js`](https://code.claude.com/docs/zh-TW/claude-directory#ce-workflows)                   | 專案和全域 | ✓    | Claude 撰寫並從 `/workflows` 儲存的動態工作流程指令碼；每個檔案都會變成 `/<name>` 命令 | [Dynamic workflows](https://code.claude.com/docs/zh-TW/workflows)                              |
| [`agent-memory/<name>/`](https://code.claude.com/docs/zh-TW/claude-directory#ce-agent-memory)          | 專案和全域 | ✓    | Subagents 的持久記憶                                                                   | [Persistent memory](https://code.claude.com/docs/zh-TW/sub-agents#enable-persistent-memory)    |
| [`~/.claude.json`](https://code.claude.com/docs/zh-TW/claude-directory#ce-claude-json)                 | 僅全域     |      | 應用程式狀態、OAuth、UI 切換、個人 MCP 伺服器                                          | [Global config](https://code.claude.com/docs/zh-TW/settings-reference#global-config-settings)  |
| [`projects/<project>/memory/`](https://code.claude.com/docs/zh-TW/claude-directory#ce-global-projects) | 僅全域     |      | 自動記憶：Claude 在工作階段間對自己的筆記                                              | [Auto memory](https://code.claude.com/docs/zh-TW/memory#auto-memory)                           |
| [`keybindings.json`](https://code.claude.com/docs/zh-TW/claude-directory#ce-keybindings)               | 僅全域     |      | 自訂快捷鍵                                                                             | [Keybindings](https://code.claude.com/docs/zh-TW/keybindings)                                  |
| [`themes/*.json`](https://code.claude.com/docs/zh-TW/claude-directory#ce-themes)                       | 僅全域     |      | 自訂色彩主題                                                                           | [Custom themes](https://code.claude.com/docs/zh-TW/terminal-config#create-a-custom-theme)      |

## 疑難排解設定

如果設定、hook 或檔案未生效，請參閱[偵錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config)以取得檢查命令和症狀優先查詢表。

## 應用程式資料

除了您編寫的設定外，`~/.claude` 還保存 Claude Code 在工作階段期間寫入的資料。這些檔案是純文字。任何通過工具的內容都會在磁碟上的文字記錄中結束：檔案內容、命令輸出、貼上的文字。

### 自動清理

Claude Code 會刪除下列路徑中的檔案，一旦它們的年齡超過 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)，只要它能安全地確定保留期間。預設值為 30 天，最小值為 1；設定 `0` 會因驗證錯誤而失敗。相同的年齡截止值也適用於[孤立 worktrees](https://code.claude.com/docs/zh-TW/worktrees#clean-up-subagent-and-background-session-worktrees) 的自動移除。

| `~/.claude/` 下的路徑                                                                                                           | 內容                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `projects/<project>/<session>.jsonl`                                                                                            | 完整對話文字記錄：每條訊息、工具呼叫和工具結果                                                                                                                                                                                                                                                                |
| `projects/<project>/<session>.orphaned-<timestamp>-<suffix>.jsonl`、`projects/<project>/<session>.jsonl.superseded-<timestamp>` | Claude Code 為工作階段設置的先前文字記錄，而不是覆蓋或刪除它。它不會出現在工作階段選擇器中                                                                                                                                                                                                                    |
| `projects/<project>/<session>/subagents/`                                                                                       | [Subagent](https://code.claude.com/docs/zh-TW/sub-agents) 對話文字記錄，當父工作階段文字記錄過期時一起移除                                                                                                                                                                                                    |
| `projects/<project>/<session>/tool-results/`                                                                                    | 溢出到單獨檔案的大型工具輸出                                                                                                                                                                                                                                                                                  |
| `file-history/<session>/`                                                                                                       | Claude 變更的檔案的編輯前快照，用於[檢查點還原](https://code.claude.com/docs/zh-TW/checkpointing)。保存 100 個最近檢查點的快照；沒有保留檢查點參考的快照檔案會被刪除，除了每個檔案的第一個快照                                                                                                                |
| `plans/`                                                                                                                        | 在 [Plan Mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 期間寫入的計畫檔案                                                                                                                                                                                 |
| `debug/`                                                                                                                        | 每個工作階段的偵錯日誌，在啟用偵錯日誌時寫入，例如當您使用 [`--debug`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 啟動或執行 `/debug` 時                                                                                                                                                     |
| `paste-cache/`                                                                                                                  | 大型貼上的內容                                                                                                                                                                                                                                                                                                |
| `image-cache/<session>/`                                                                                                        | 附加的影像。在每次掃描時，Claude Code 會移除所有其他工作階段的目錄，無論其年齡如何。                                                                                                                                                                                                                          |
| `uploads/<session>/`                                                                                                            | 您從網路或行動應用程式附加的檔案，以及從行動應用程式附加的照片，當傳訊給 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段時。附加到 [cloud session](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 的檔案會改為保存在該工作階段自己的雲端環境中，而不是在您的機器上。 |
| `session-env/`                                                                                                                  | 每個工作階段的環境中繼資料                                                                                                                                                                                                                                                                                    |
| `tasks/`                                                                                                                        | 由 task tools 寫入的任務清單，每個清單一個目錄                                                                                                                                                                                                                                                                |
| `shell-snapshots/`                                                                                                              | 在啟動時擷取的別名、函式和 shell 選項，由 [Bash tool](https://code.claude.com/docs/zh-TW/tools-reference#bash-tool-behavior) 應用於每個命令。在正常退出時移除。掃描會清除任何在當機後遺留的檔案。                                                                                                             |
| `backups/`                                                                                                                      | `~/.claude.json` 的較早版本，在 Claude Code 重寫檔案時複製。Claude Code 保留五個最新的版本，加上它無法解析的任何版本的副本。                                                                                                                                                                                  |
| `feedback-bundles/`                                                                                                             | 由 `/feedback` 在第三方提供者上寫入的已編輯文字記錄存檔，或在未設定 Anthropic 認證時寫入，用於傳送到您的 Anthropic 帳戶團隊                                                                                                                                                                                   |
| `feedback/drafts/`                                                                                                              | 排隊的 [Claude 起草的回饋](https://code.claude.com/docs/zh-TW/tools-reference#sendfeedback-tool-behavior)，等待您在 `/feedback` 中審查。在 `cleanupPeriodDays` 或 30 天後掃描，以較短者為準。當佇列達到其 10 份草稿限制時，Claude Code 會刪除最舊的草稿以騰出空間。                                           |
| `usage-data/`                                                                                                                   | 由 [`/insights`](https://code.claude.com/docs/zh-TW/costs#analyze-your-usage-patterns) 寫入的 `report.html` 和時間戳記報告副本，加上用於建立它們的快取每個工作階段分析資料                                                                                                                                    |
| `skills/.trash/`、`plugins/.trash/`                                                                                             | 從 claude.ai 同步的 [Skills](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave) 和 [plugins](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)，Claude Code 已移除。移動到此處而不是刪除，以便您可以復原檔案                                                              |
| `todos/`、`statsig/`、`logs/`                                                                                                   | 舊版本的舊版目錄。不再寫入。掃描會移除其內容，然後移除空目錄。                                                                                                                                                                                                                                                |
| `sessions/` 中的工作階段檔案、自動記憶，以及 Claude Desktop 和 Cowork 文字記錄各自遵循自己的保留規則：                          |                                                                                                                                                                                                                                                                                                               |

- **`sessions/`**：保存每個執行中工作階段的一個小檔案，用於偵測並行工作階段和當機。它不是基於年齡的掃描的一部分：Claude Code 在其工作階段退出時移除每個檔案，並在下次啟動時清除當機遺留物。
- **自動記憶** ：掃描不會刪除專案 [auto memory](https://code.claude.com/docs/zh-TW/memory#auto-memory) 目錄 `projects/<project>/memory/` 中的記憶檔案。Claude Code 只有在該目錄在整個保留期間都為空時才會移除它。在 v2.1.228 之前，掃描會將記憶目錄內的資料夾視為工作階段資料，並可能刪除其下的舊檔案。
- **Claude Desktop 和 Cowork 文字記錄** ：Claude Code 保留您在 Claude Desktop 或 Cowork 中啟動或最近繼續的工作階段的文字記錄，無論其年齡如何。若要為這些文字記錄設定年齡限制，請設定 [`desktopSessionCleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#desktopsessioncleanupperioddays)。當 [managed settings](https://code.claude.com/docs/zh-TW/managed-settings) 設定 `cleanupPeriodDays` 時，Claude Code 會改為在該期間後刪除這些文字記錄。需要 Claude Code v2.1.248 或更新版本；較早的版本會在 `cleanupPeriodDays` 後刪除它們。

Claude Code 在這些情況下會完全跳過掃描：

- **Bare mode** ：當您使用 [`--bare`](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode) 執行 `claude -p` 時，Claude Code 不會在該工作階段中執行掃描。
- **暫停掃描** ：如果 Claude Code 無法安全地確定保留期間，它會暫停保留清理掃描；[`retention_sweep` 事件](https://code.claude.com/docs/zh-TW/monitoring-usage#retention-sweep-event)列出每個暫停它的設定。當原因是無法讀取或解析的設定檔案，或 `cleanupPeriodDays` 或 `desktopSessionCleanupPeriodDays` 明確設定的設定錯誤時，Claude Code 也會在 `/status` 中顯示警告，直到您修正設定錯誤。當 [managed settings](https://code.claude.com/docs/zh-TW/server-managed-settings) 提供 `cleanupPeriodDays` 時，Claude Code 會在任一情況下以受管值執行掃描。

### 保留直到您刪除它們

保留清理掃描不會移除下列路徑。Claude Code 會保留它們直到您刪除它們，除了兩個在您登出時刪除的快取。

| `~/.claude/` 下的路徑                                                          | 內容                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `history.jsonl`                                                                | 您輸入的每個提示，帶有時間戳記和專案路徑。用於向上箭頭回憶、`Ctrl+R` 歷史搜尋和 `!` shell 命令完成。                                                                                                                                                                                                                                                         |
| `stats-cache.json`                                                             | 由 `/usage` 顯示的彙總權杖和成本計數                                                                                                                                                                                                                                                                                                                         |
| `remote-settings.json`                                                         | 您組織的 [server-managed settings](https://code.claude.com/docs/zh-TW/server-managed-settings) 的快取副本，或當您的組織未設定任何內容時為 `{}`。只有在工作階段 [fetches them](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability) 時才會出現。Claude Code 在啟動時和工作階段期間每小時檢查更新。Claude Code 在您登出時刪除它。 |
| `cache/changelog.md`                                                           | Claude Code 變更日誌的快取副本，由 `/release-notes` 顯示。在背景中重新整理。                                                                                                                                                                                                                                                                                 |
| `policy-limits.json`                                                           | 您組織的快取功能原則設定。只有某些帳戶類型才會出現。自動重新整理。Claude Code 在您登出時刪除它。                                                                                                                                                                                                                                                             |
| 其他檔案會根據您使用的功能而出現。快取和鎖定檔案可安全刪除。保留這些狀態檔案： |                                                                                                                                                                                                                                                                                                                                                              |

- `.credentials.json`：您的 [login credentials](https://code.claude.com/docs/zh-TW/authentication#credential-management)
- `agent-memory/`：[subagent memory](https://code.claude.com/docs/zh-TW/sub-agents#enable-persistent-memory)
- `jobs/` 和 `daemon/`：[background session](https://code.claude.com/docs/zh-TW/agent-view#where-state-is-stored) 狀態

### 純文字儲存

文字記錄和歷史記錄在靜止時未加密。作業系統檔案權限是唯一的保護。如果工具讀取 `.env` 檔案或命令列印認證，該值會寫入 `projects/<project>/<session>.jsonl`。若要減少暴露：

- 降低 `cleanupPeriodDays` 以縮短 Claude Code 保留文字記錄的時間
- 設定 [`desktopSessionCleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#desktopsessioncleanupperioddays) 以給予 Claude Desktop 和 Cowork 文字記錄年齡限制
- 設定 [`CLAUDE_CODE_SKIP_PROMPT_HISTORY`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數以跳過在任何模式中寫入文字記錄和提示歷史記錄。在非互動模式中，您可以改為在 `-p` 旁邊傳遞 `--no-session-persistence`，或在 TypeScript Agent SDK 中設定 `persistSession: false`；Python SDK 沒有等效選項。
- 使用[權限規則](https://code.claude.com/docs/zh-TW/permissions)拒絕讀取認證檔案

### 清除本機資料

執行 `claude project purge` 以刪除 Claude Code 為一個專案保存的狀態。它會刪除：

- `projects/` 下的文字記錄和自動記憶
- 每個工作階段的 `tasks/`、`debug/` 和 `file-history/` 項目
- `history.jsonl` 中的匹配提示行
- 專案在 `~/.claude.json` 中的項目

該命令會列印完整的刪除計畫，並在移除任何內容之前要求確認。 下列範例使用 `~/work/my-repo` 作為佔位符。將其替換為您的專案路徑。如果沒有狀態與路徑相符，該命令會列印錯誤並以狀態 1 退出。 預覽計畫而不刪除任何內容：

```
claude project purge ~/work/my-repo --dry-run

```

計畫列出每個匹配項目及其包含的原因：

```
Purge plan for /home/user/work/my-repo:

  dir:    /home/user/.claude/projects/-home-user-work-my-repo
           project transcripts (.jsonl) and memory/
  config: projects["/home/user/work/my-repo"]
           project entry in ~/.claude.json (trust, history, MCP servers)
  filter: /home/user/.claude/history.jsonl
           12 prompt(s) typed in this project

shell-snapshots/ are not project-scoped and will not be touched
backups/ may still contain this project entry in old .claude.json snapshots (/home/user/.claude/backups); at most 5 are kept and they rotate out automatically
Dry run: 3 item(s) would be deleted.

```

透過單一確認提示刪除：

```
claude project purge ~/work/my-repo

```

該命令會列印相同的計畫，然後詢問 `Delete 3 item(s) for /home/user/work/my-repo? This cannot be undone. [y/N]`，只有在您回答 `y` 時才會刪除。 省略路徑以從互動式清單中選擇專案。 跳過確認提示以在指令碼中使用：

```
claude project purge ~/work/my-repo --yes

```

傳遞 `--all` 而不是路徑以一次清除所有專案的狀態，這會直接刪除 `history.jsonl` 而不是篩選它。傳遞 `-i` 以逐項逐步執行刪除計畫。 該命令會單獨保留 `shell-snapshots/` 和 `backups/`，因為這些不是專案範圍的，並在計畫輸出中警告它們。 您也可以手動刪除上述任何應用程式資料路徑，除了 [state files to keep](https://code.claude.com/docs/zh-TW/claude-directory#state-files-to-keep)。新工作階段不受影響。下表顯示您對過去工作階段失去的內容。

| 刪除                                                                                                                                           | 您失去                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `~/.claude/projects/`                                                                                                                          | 過去工作階段的繼續、繼續和倒帶，以及每個專案的自動記憶                                                                                                                                                       |
| `~/.claude/history.jsonl`                                                                                                                      | 向上箭頭提示回憶、`Ctrl+R` 歷史搜尋和 `!` shell 命令完成                                                                                                                                                     |
| `~/.claude/paste-cache/`                                                                                                                       | 回憶提示中的貼上文字；請參閱 [paste large content](https://code.claude.com/docs/zh-TW/terminal-config#paste-large-content)                                                                                   |
| `~/.claude/uploads/`                                                                                                                           | 過去 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段按路徑參考的附件                                                                                                            |
| `~/.claude/file-history/`                                                                                                                      | 過去工作階段的檢查點還原                                                                                                                                                                                     |
| `~/.claude/stats-cache.json`                                                                                                                   | 由 `/usage` 顯示的歷史總計                                                                                                                                                                                   |
| `~/.claude/usage-data/`                                                                                                                        | 過去的 [`/insights`](https://code.claude.com/docs/zh-TW/costs#analyze-your-usage-patterns) 報告和用於建立它們的快取分析資料                                                                                  |
| `~/.claude/feedback-bundles/`                                                                                                                  | 您尚未傳送給 Anthropic 帳戶團隊的回饋和錯誤報告存檔                                                                                                                                                          |
| `~/.claude/feedback/drafts/`                                                                                                                   | 您尚未傳送的 [Claude 起草的回饋](https://code.claude.com/docs/zh-TW/tools-reference#sendfeedback-tool-behavior)                                                                                              |
| `~/.claude/remote-settings.json`                                                                                                               | 無。在下次啟動時重新擷取。                                                                                                                                                                                   |
| `~/.claude/cache/changelog.md`                                                                                                                 | 無。在背景中重新整理。                                                                                                                                                                                       |
| `~/.claude/policy-limits.json`                                                                                                                 | 無。自動重新整理。                                                                                                                                                                                           |
| `~/.claude/tasks/`                                                                                                                             | 繼續的工作階段會拾取的任務清單                                                                                                                                                                               |
| `~/.claude/skills/.trash/`、`~/.claude/plugins/.trash/`                                                                                        | 復原 [synced skills](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave) 和 [synced plugins](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins) 的機會，Claude Code 已移除 |
| `~/.claude/debug/`、`~/.claude/plans/`、`~/.claude/image-cache/`、`~/.claude/session-env/`、`~/.claude/shell-snapshots/`、`~/.claude/backups/` | 沒有面向使用者的內容                                                                                                                                                                                         |
| `~/.claude/todos/`、`~/.claude/statsig/`、`~/.claude/logs/`                                                                                    | 無。舊版目錄不由目前版本寫入。                                                                                                                                                                               |
| 不要刪除 `~/.claude.json`、`~/.claude/settings.json` 或 `~/.claude/plugins/`：這些保存您的驗證、偏好設定和已安裝的 plugins。                   |                                                                                                                                                                                                              |

## 相關資源

- [管理 Claude 的記憶](https://code.claude.com/docs/zh-TW/memory)：寫入和組織 CLAUDE.md、rules 和自動記憶
- [設定設定](https://code.claude.com/docs/zh-TW/settings)：設定權限、hooks、環境變數和模型預設值
- [建立 skills](https://code.claude.com/docs/zh-TW/skills)：建立可重複使用的提示和工作流程
- [設定 subagents](https://code.claude.com/docs/zh-TW/sub-agents)：定義具有自己上下文的專門代理

是否 助手
