Claude Code 可以透過 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) 連接到數百個外部工具和資料來源，這是一個開源標準，用於 AI 工具整合。MCP servers 讓 Claude Code 能夠存取您的工具、資料庫和 API。 當您發現自己從另一個工具（例如問題追蹤器或監控儀表板）複製資料到聊天中時，請連接一個 server。連接後，Claude 可以直接讀取和操作該系統，而不是根據您貼上的內容進行工作。 如果您是第一次連接 server，請從 [MCP 快速入門](https://code.claude.com/docs/zh-TW/mcp-quickstart) 開始，以取得逐步說明。本頁面是完整參考。

## 使用 MCP 可以做什麼

使用連接的 MCP servers，您可以要求 Claude Code：

- **從問題追蹤器實現功能** ：“新增 JIRA 問題 ENG-4521 中描述的功能，並在 GitHub 上建立 PR。”
- **分析監控資料** ：“檢查 Sentry 和 Statsig，以檢查 ENG-4521 中描述的功能使用情況。”
- **查詢資料庫** ：“根據我們的 PostgreSQL 資料庫，找到 10 個使用功能 ENG-4521 的隨機使用者的電子郵件。”
- **整合設計** ：“根據在 Slack 中發佈的新 Figma 設計更新我們的標準電子郵件範本”
- **自動化工作流程** ：“建立 Gmail 草稿，邀請這 10 個使用者參加關於新功能的回饋會議。”
- **回應外部事件** ：MCP server 也可以充當 [channel](https://code.claude.com/docs/zh-TW/channels)，將訊息推送到您的 session 中，因此當您不在時，Claude 可以回應 Telegram 訊息、Discord 聊天或 webhook 事件。

## 尋找並建立 MCP servers

在 [Anthropic Directory](https://claude.ai/directory) 中瀏覽已審核的連接器。Directory 連接器使用與 Claude Code 相同的 MCP 基礎設施，因此您可以使用 `claude mcp add` 新增任何列在其中的遠端伺服器。 在連接伺服器之前，請驗證您信任每個伺服器。取得外部內容的伺服器可能會使您面臨[提示注入風險](https://code.claude.com/docs/zh-TW/security#protect-against-prompt-injection)。 若要建立您自己的伺服器，請參閱 [MCP server 指南](https://modelcontextprotocol.io/docs/develop/build-server) 以了解協議基礎知識，以及 [Claude 連接器建立文件](https://claude.com/docs/connectors/building) 以了解身份驗證、測試和 Directory 提交。 您也可以使用官方的 [`mcp-server-dev` plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/mcp-server-dev) 讓 Claude 為您建立伺服器。 1 安裝 plugin 在 Claude Code 工作階段中，執行：

```
/plugin install mcp-server-dev@claude-plugins-official

```

如果 Claude Code 報告找不到 marketplace，請先執行 `/plugin marketplace add anthropics/claude-plugins-official`，然後重試安裝。安裝完成後，執行 `/reload-plugins` 以在目前工作階段中啟用它。 2 執行建立 skill

```
/mcp-server-dev:build-mcp-server

```

Claude 會詢問您的使用案例，並建立遠端 HTTP 或本機 stdio 伺服器。

## 安裝 MCP servers

MCP servers 可以根據您的需求以多種方式進行配置：

### 選項 1：新增遠端 HTTP server

HTTP servers 是連接到遠端 MCP servers 的推薦選項。這是雲端服務最廣泛支援的傳輸方式。

```
# 基本語法
claude mcp add --transport http <name> <url>

# 實際範例：連接到 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 使用 Bearer token 的範例
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"

```

當透過 `.mcp.json`、`~/.claude.json` 或 `claude mcp add-json` 中的 JSON 配置 MCP servers 時，`type` 欄位接受 `streamable-http` 作為 `http` 的別名。MCP 規範使用名稱 `streamable-http` 作為此傳輸，因此從 server 文件複製的配置無需修改即可運作。 沒有 `type` 但有 `url` 的 JSON 項目是配置錯誤，因為 Claude Code 將沒有 `type` 的項目讀取為 stdio server。Claude Code 會跳過該 server 並報告 `MCP server "<name>" has a "url" but no "type"; add "type": "http" (or "sse" / "ws") to this entry`。在 v2.1.202 之前，Claude Code 將此配置錯誤報告為 `command: expected string, received undefined`。

### 選項 2：新增遠端 SSE server

SSE (Server-Sent Events) 傳輸已棄用。請改用 HTTP servers（如果可用）。

```
# 基本語法
claude mcp add --transport sse <name> <url>

# 實際範例：連接到 Asana
claude mcp add --transport sse asana https://mcp.asana.com/sse

# 使用驗證標頭的範例
claude mcp add --transport sse private-api https://api.company.com/sse \
  --header "X-API-Key: your-key-here"

```

### 選項 3：新增本機 stdio server

Stdio servers 在您的機器上作為本機程序執行。它們非常適合需要直接系統存取或自訂指令碼的工具。 Claude Code 在生成的 server 環境中設定 `CLAUDE_PROJECT_DIR` 為專案根目錄，因此您的 server 可以解析專案相對路徑，而無需依賴工作目錄。這與 hooks 在其 `CLAUDE_PROJECT_DIR` 變數中接收的目錄相同。從您的 server 程序內部讀取它，例如 Node 中的 `process.env.CLAUDE_PROJECT_DIR` 或 Python 中的 `os.environ["CLAUDE_PROJECT_DIR"]`。 `CLAUDE_PROJECT_DIR` 是穩定的專案根目錄，在 session 中途新增或移除工作目錄時不會變更。限制自身檔案系統存取到一組允許目錄的 server 應該改為實作 MCP `roots/list` 請求。Claude Code 使用 session 的啟動目錄加上您透過 `--add-dir`、`/add-dir` 或 `additionalDirectories` 設定授予的每個[額外工作目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories)來回答 `roots/list`。當該集合變更時，Claude Code 會傳送 `notifications/roots/list_changed`。在 v2.1.203 之前，`roots/list` 只傳回啟動目錄，Claude Code 不會傳送 `notifications/roots/list_changed`。 此變數在 server 的環境中設定，而不是在 Claude Code 自己的環境中，因此在專案或使用者範圍的 `.mcp.json` `command` 或 `args` 中透過 `${VAR}` 擴展參考它需要預設值，例如 `${CLAUDE_PROJECT_DIR:-.}`。Plugin 提供的 MCP 配置直接替換 `${CLAUDE_PROJECT_DIR}`，不需要預設值。

```
# 基本語法
claude mcp add [options] <name> -- <command> [args...]

# 實際範例：新增 Airtable server
claude mcp add --env AIRTABLE_API_KEY=YOUR_KEY --transport stdio airtable \
  -- npx -y airtable-mcp-server

```

**重要：使用`--` 分隔 server 引數**對於 stdio servers，`--` (雙破折號) 將 Claude 自己的選項（例如 `--transport`、`--env` 和 `--scope`）與執行 server 的命令和引數分開。`--` 之後的所有內容都會原封不動地傳遞給 server。例如：

- `claude mcp add --transport stdio myserver -- npx server` → 執行 `npx server`
- `claude mcp add --env KEY=value --transport stdio myserver -- python server.py --port 8080` → 執行 `python server.py --port 8080`，環境中有 `KEY=value`

沒有 `--`，Claude Code 會嘗試解析 server 的旗標（例如上面的 `--port`）作為自己的選項。`--env` 接受多個 `KEY=value` 對。如果 server 名稱直接跟在 `--env` 之後，CLI 會將該名稱讀取為另一對並拒絕它，因此請在 `--env` 和 server 名稱之間放置至少一個其他選項，如上面的範例所示。

### 選項 4：新增遠端 WebSocket server

WebSocket servers 保持持久的雙向連接，適合遠端 MCP servers 主動向 Claude 推送事件。當您的 server 只回應請求時，請改用 HTTP，因為 HTTP 支援 OAuth 和 `claude mcp add --transport` 旗標，而 WebSocket 都不支援。 在 `.mcp.json` 中或使用 `claude mcp add-json` 配置 WebSocket servers：

```
claude mcp add-json events-server \
  '{"type":"ws","url":"wss://mcp.example.com/socket","headers":{"Authorization":"Bearer YOUR_TOKEN"}}'

```

`type: "ws"` 項目接受與 `http` 相同的 `url`、`headers`、`headersHelper`、`timeout` 和 `alwaysLoad` 欄位。驗證僅限標頭，因此在 `headers` 中傳遞靜態 token，或在連接時使用 [`headersHelper`](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication) 生成一個。`claude mcp add --transport` 旗標不接受 `ws`。

### 管理您的 servers

配置後，您可以使用這些命令管理您的 MCP servers：

```
# 列出所有已配置的 servers
claude mcp list

# 取得特定 server 的詳細資訊
claude mcp get github

# 移除 server
claude mcp remove github

# (在 Claude Code 中) 檢查 server 狀態
/mcp

```

來自 `.mcp.json` 的專案範圍 servers 等待您的批准時，會在 `claude mcp list` 中顯示為 `⏸ Pending approval`。執行 `claude` 互動式命令以檢查和批准它們。`claude mcp get <name>` 將待處理的 servers 顯示為 `⏸ Pending approval`，將被拒絕的 servers 顯示為 `✗ Rejected`。 自 v2.1.196 起，`claude mcp list` 和 `claude mcp get` 只從未簽入儲存庫的設定檔案中讀取 `.mcp.json` 批准，直到您透過在其中執行 `claude` 並接受工作區信任對話框來信任工作區。複製的儲存庫無法批准自己的 servers：提交到專案 `.claude/settings.json` 的 [`enableAllProjectMcpServers` 或 `enabledMcpjsonServers`](https://code.claude.com/docs/zh-TW/settings#available-settings) 在不受信任的資料夾中被忽略，server 保持在 `⏸ Pending approval` 而不是被連接和健康檢查。 這些來源的批准仍然適用於不受信任的資料夾：

- 您的使用者 `~/.claude/settings.json`
- 受管設定
- 使用 `--settings` 傳遞的設定

未追蹤的 `.claude/settings.local.json` 中的批准也適用，但僅在您接受該資料夾或其父目錄之一的信任對話框後：Claude Code 執行 git 以檢查檔案是否被追蹤，並且僅在受信任的資料夾中執行該檢查。在您從未信任的資料夾中，檔案的批准會等待信任對話框，除非該資料夾是您自己的配置主目錄：您的主目錄，或您已設定為 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars) 的 `.claude` 的目錄。在 v2.1.207 之前，未追蹤的 `.claude/settings.local.json` 在您從未信任的資料夾中批准了 servers。 任何設定檔案中的 `disabledMcpjsonServers` 項目仍然會拒絕 server。 `/mcp` 面板會在每個已連接的 server 旁邊顯示工具計數，並標記宣告工具功能但未公開任何工具的 servers。 配置為空 `url` 的遠端 server 在 `/mcp`、`claude mcp list` 和 [`/plugin`](https://code.claude.com/docs/zh-TW/plugins) 管理器中顯示為 `not configured`，Claude Code 不會嘗試連接到它。Plugin 可以包含一個佔位符項目，例如此項目，用於您稍後配置的連接器，因此 Claude Code 不會將其報告為錯誤或設定問題。server 在 `/mcp` 中的詳細檢視會讀取 `No URL configured for this server`；設定項目的 `url` 以連接它。在 v2.1.208 之前，Claude Code 將空 `url` 報告為配置問題，並提示重新連接。 如果您的請求需要來自仍在背景連接的 server 的工具，Claude 會在繼續之前等待該 server。啟用 [tool search](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search)（預設啟用）後，等待會在 `ToolSearch` 呼叫內進行。在沒有工具搜尋的配置中，例如 Google Cloud 的 Agent Platform、自訂 `ANTHROPIC_BASE_URL` 或 `ENABLE_TOOL_SEARCH=false`，Claude 會改用 `WaitForMcpServers` 工具。 某些 server 名稱保留供 Claude Code 的內建 servers 使用：`workspace`、`claude-in-chrome`、`computer-use`、`Claude Preview` 和 `Claude Browser`。如果您的配置定義了具有保留名稱的 server，Claude Code 會在載入時跳過它，並顯示警告要求您重新命名它。`claude mcp add` 會以錯誤拒絕保留名稱。 `Claude Preview` 和 `Claude Browser` 都命名了 [Claude Code 桌面應用程式的預覽窗格](https://code.claude.com/docs/zh-TW/desktop#preview-your-app)使用的內建 server。在 v2.1.205 之前，`Claude Browser` 未被保留，因此使用者配置的 server 可以在該名稱下註冊。

### 動態工具更新

Claude Code 支援 MCP `list_changed` 通知，允許 MCP servers 動態更新其可用工具、提示和資源，而無需您斷開連接並重新連接。當 MCP server 傳送 `list_changed` 通知時，Claude Code 會自動重新整理該 server 的可用功能。

### 自動重新連接

如果 HTTP 或 SSE server 在 session 中途斷開連接，Claude Code 會自動以指數退避方式重新連接：最多五次嘗試，從一秒延遲開始，每次加倍。在 `/mcp` 中，server 會顯示為待處理狀態，同時重新連接正在進行中。五次失敗嘗試後，server 被標記為失敗，您可以從 `/mcp` 手動重試。Stdio servers 是本機程序，不會自動重新連接。 相同的退避策略適用於 HTTP 或 SSE server 在啟動時初始連接失敗的情況。自 v2.1.121 起，Claude Code 在暫時性錯誤（例如 5xx 回應、連接被拒絕或逾時）上最多重試初始連接三次，如果仍無法連接，則將 server 標記為失敗。驗證和找不到錯誤不會重試，因為它們需要配置變更才能解決。 當配置的 server 無法連接時，Claude Code 會告訴 Claude 哪個 server 失敗及其連接錯誤，包括在找不到匹配工具的 `ToolSearch` 結果中，因此 Claude 會在其回應中報告連接失敗。需要 [tool search](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search)，預設啟用。在沒有工具搜尋的配置中，例如自訂 `ANTHROPIC_BASE_URL`、`ENABLE_TOOL_SEARCH=false` 或不支援工具搜尋的模型，以及在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上，Claude Code 不會向 Claude 報告失敗的 server 連接。在 v2.1.205 之前，Claude Code 不會將連接錯誤傳遞給 Claude，Claude 可能會回應，就像失敗的 server 的工具從未被配置一樣。 自 v2.1.191 起，在成功連接後執行的功能探索請求（例如 `tools/list`、`prompts/list` 和 `resources/list`）也會在短退避的情況下重試暫時性網路和 server 錯誤最多三次。驗證錯誤、4xx 回應和請求逾時不會重試。

### 使用 channels 推送訊息

MCP server 也可以直接將訊息推送到您的 session 中，以便 Claude 可以回應外部事件，例如 CI 結果、監控警報或聊天訊息。若要啟用此功能，您的 server 宣告 `claude/channel` 功能，並在啟動時使用 `--channels` 旗標選擇加入。請參閱 [Channels](https://code.claude.com/docs/zh-TW/channels) 以使用官方支援的 channel，或 [Channels reference](https://code.claude.com/docs/zh-TW/channels-reference) 以建立您自己的。 提示：

- 使用 `-s` 或 `--scope` 旗標指定配置的儲存位置：
  - `local` (預設)：僅在目前專案中對您可用。較舊版本稱此範圍為 `project`
  - `project`：透過 `.mcp.json` 檔案與專案中的所有人共享
  - `user`：在所有專案中對您可用。較舊版本稱此範圍為 `global`
- 使用 `-e` 或 `--env` 旗標設定環境變數 (例如，`-e KEY=value`)
- `--transport` 和 `--header` 旗標也接受 `-t` 和 `-H` 短形式
- 使用 `MCP_TIMEOUT` 環境變數配置 MCP server 啟動逾時 (例如，`MCP_TIMEOUT=10000 claude` 設定 10 秒逾時)
- 透過在該 server 的 `.mcp.json` 項目中新增 `timeout` 欄位（以毫秒為單位）來設定每個 server 的工具執行逾時，例如 `"timeout": 600000` 表示十分鐘。這只會覆寫該 server 的 `MCP_TOOL_TIMEOUT` 環境變數
- 當 MCP 工具輸出超過 10,000 個 tokens 時，Claude Code 會顯示警告，並預設將輸出限制為 25,000 個 tokens。若要增加此限制，請設定 `MAX_MCP_OUTPUT_TOKENS` 環境變數 (例如，`MAX_MCP_OUTPUT_TOKENS=50000`)；警告閾值是固定的。請參閱 [MCP output limits and warnings](https://code.claude.com/docs/zh-TW/mcp#mcp-output-limits-and-warnings)
- 使用 `/mcp` 向需要 OAuth 2.0 驗證的遠端 servers 進行驗證

每個 server 的 `timeout` 是每個工具呼叫的硬牆鐘限制，來自 server 的進度通知不會延長它。低於 1000 的值會被忽略並落回到 `MCP_TOOL_TIMEOUT`，或在該變數未設定時落回到其預設值約 28 小時。對於 HTTP、SSE 或 [claude.ai connector](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai) server，還有第二個每個請求的計時器，涵蓋每個請求直到 server 的第一個回應位元組。該計時器為 60 秒，除非您設定每個 server 的 `timeout` 或 `MCP_TOOL_TIMEOUT`；將任一設定為 60 秒或更高會將每個請求的計時器提高到該值，較低的值不會縮短它，未設定的 `MCP_TOOL_TIMEOUT` 的 28 小時預設值永遠不會提供給它。Stdio 和 WebSocket servers 沒有每個請求的計時器。在 v2.1.162 之前，低於 1000 的值被調整為一秒。 每個 server 至少 1000 的 `timeout` 也會作為下面所述的閒置逾時的下限：Claude Code 永遠不會因為閒置而在每個 server 的 `timeout` 之前中止該 server 的工具呼叫。需要 Claude Code v2.1.203 或更新版本。 對遠端 MCP server 的工具呼叫如果在閒置視窗內沒有傳送回應和進度通知，會以錯誤中止，而不是等待牆鐘限制。閒置逾時需要 Claude Code v2.1.187 或更新版本。它適用於除 IDE servers 和 SDK 進程內 servers 之外的每種 server 類型。HTTP、SSE、WebSocket 和 [claude.ai connector](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai) servers 的閒置視窗預設為五分鐘，stdio servers 的預設為 30 分鐘。在 v2.1.203 之前，stdio servers 不受閒置逾時限制。 在毫秒中設定 [`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數以變更閒置視窗，或將其設定為 `0` 以停用檢查。

### Plugin 提供的 MCP servers

[Plugins](https://code.claude.com/docs/zh-TW/plugins) 可以捆綁 MCP servers，在啟用 plugin 時自動提供工具和整合。Plugin MCP servers 的工作方式與使用者配置的 servers 相同。 **Plugin MCP servers 的工作方式** ：

- Plugins 在 plugin 根目錄的 `.mcp.json` 中或在 `plugin.json` 中內聯定義 MCP servers
- 啟用 plugin 時，其 MCP servers 會自動啟動
- Plugin MCP 工具與手動配置的 MCP 工具一起出現
- Plugin servers 透過 plugin 安裝進行管理，不是 `/mcp` 命令

**Plugin MCP 配置範例** ： 在 plugin 根目錄的 `.mcp.json` 中：

```
{
  "mcpServers": {
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_URL": "${DB_URL}"
      }
    }
  }
}

```

或在 `plugin.json` 中內聯：

```
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}

```

**Plugin MCP 功能** ：

- **自動生命週期** ：在 session 啟動時，已啟用 plugins 的 servers 會自動連接。如果您在 session 期間啟用或停用 plugin，請執行 `/reload-plugins` 以連接或斷開其 MCP servers
- **路徑佔位符** ：`${CLAUDE_PLUGIN_ROOT}` 解析為 plugin 的安裝目錄，`${CLAUDE_PLUGIN_DATA}` 解析為其[持久狀態](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)目錄，`${CLAUDE_PROJECT_DIR}` 解析為穩定的專案根目錄。替換適用於：
  - `stdio` servers：`command`、`args`、`env`
  - `http`、`sse` 和 `ws` servers：`url`、`headers` 和 `headersHelper`。在 v2.1.195 之前，`headersHelper` 將佔位符作為字面字符串傳遞
- **使用者環境存取** ：存取與手動配置的 servers 相同的環境變數
- **多種傳輸類型** ：支援 stdio、SSE、HTTP 和 WebSocket 傳輸，傳輸支援可能因 server 而異

**檢視 plugin MCP servers** ：

```
# 在 Claude Code 中，查看所有 MCP servers，包括 plugin 的
/mcp

```

Plugin servers 在列表中出現，並有指示器顯示它們來自 plugins。 **Plugin MCP 工具名稱** ： 來自 plugin 捆綁的 MCP server 的工具在其可呼叫名稱中包含 plugin 名稱和 server 金鑰。完整形式是 `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`，其中 `A-Z`、`a-z`、`0-9`、`_` 和 `-` 以外的任何字元都被替換為 `_`。對於在名為 `my-plugin` 的 plugin 中捆綁的 `database-tools` server，`query` 工具可呼叫為：

```
mcp__plugin_my-plugin_database-tools__query

```

在 [permission rules](https://code.claude.com/docs/zh-TW/permissions)、skill 的 `allowed-tools` 列表、[subagent 的 `tools` 欄位](https://code.claude.com/docs/zh-TW/sub-agents#available-tools) 或 [hook matcher](https://code.claude.com/docs/zh-TW/hooks#match-mcp-tools) 中參考工具時，請使用此完整名稱。針對裸 server 金鑰（例如 `mcp__database-tools__.*`）編寫的 hook matcher 永遠不會針對 plugin 捆綁的 server 觸發。 server 本身在範圍名稱 `plugin:<plugin-name>:<server-name>` 下註冊，例如 `plugin:my-plugin:database-tools`。在需要配置的 server 名稱的地方使用該名稱，例如 [`mcp_tool` hook 的 `server` 欄位](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields)。 **Plugin MCP servers 的優點** ：

- **捆綁分發** ：工具和 servers 一起打包
- **自動設定** ：無需手動 MCP 配置
- **團隊一致性** ：安裝 plugin 時，每個人都會獲得相同的工具

請參閱 [plugin 元件參考](https://code.claude.com/docs/zh-TW/plugins-reference#mcp-servers)，了解有關使用 plugins 捆綁 MCP servers 的詳細資訊。

## MCP 安裝範圍

MCP servers 可以在三個不同的範圍級別進行配置。您選擇的範圍控制 server 在哪些專案中載入，以及配置是否與您的團隊共享。管理員也可以透過[受管配置](https://code.claude.com/docs/zh-TW/mcp#managed-mcp-configuration)在企業級別部署 servers。

| 範圍                                                            | 載入位置     | 與團隊共享       | 儲存位置                   |
| --------------------------------------------------------------- | ------------ | ---------------- | -------------------------- |
| [Local](https://code.claude.com/docs/zh-TW/mcp#local-scope)     | 僅目前專案   | 否               | `~/.claude.json`           |
| [Project](https://code.claude.com/docs/zh-TW/mcp#project-scope) | 僅目前專案   | 是，透過版本控制 | 專案根目錄中的 `.mcp.json` |
| [User](https://code.claude.com/docs/zh-TW/mcp#user-scope)       | 您的所有專案 | 否               | `~/.claude.json`           |

### Local scope

Local scope 是預設值。本機範圍的 server 僅在您新增它的專案中載入，並對您保持私密。Claude Code 將其儲存在 `~/.claude.json` 中該專案的路徑下，因此相同的 server 不會出現在您的其他專案中。使用本機範圍進行個人開發 servers、實驗配置或包含您不想在版本控制中的認證的 servers。 MCP servers 的「local scope」術語與一般本機設定不同。MCP 本機範圍的 servers 儲存在 `~/.claude.json` (您的主目錄) 中，而一般本機設定使用 `.claude/settings.local.json` (在專案目錄中)。請參閱 [Settings](https://code.claude.com/docs/zh-TW/settings#settings-files) 了解設定檔案位置的詳細資訊。

```
# 新增本機範圍的 server (預設)
claude mcp add --transport http stripe https://mcp.stripe.com

# 明確指定本機範圍
claude mcp add --transport http stripe --scope local https://mcp.stripe.com

```

當您從 `/path/to/your/project` 執行命令時，該命令會將 server 寫入 `~/.claude.json` 中您目前專案的項目。下面的範例顯示結果：

```
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "stripe": {
          "type": "http",
          "url": "https://mcp.stripe.com"
        }
      }
    }
  }
}

```

### Project scope

Project scope 的 servers 透過在專案根目錄中儲存配置在 `.mcp.json` 檔案中來啟用團隊協作。此檔案設計為簽入版本控制，確保所有團隊成員都能存取相同的 MCP 工具和服務。新增 project scope 的 server 時，Claude Code 會自動建立或更新此檔案，使用適當的配置結構。

```
# 新增 project scope 的 server
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp

```

產生的 `.mcp.json` 檔案遵循標準化格式：

```
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}

```

出於安全考慮，Claude Code 在使用來自 `.mcp.json` 檔案的 project scope servers 之前會提示批准。如果您需要重設這些批准選擇，請使用 `claude mcp reset-project-choices` 命令。

### User scope

User scope 的 servers 儲存在 `~/.claude.json` 中，並提供跨專案可存取性，使其在您機器上的所有專案中可用，同時對您的使用者帳戶保持私密。此範圍非常適合個人公用程式 servers、開發工具或您在不同專案中經常使用的服務。

```
# 新增使用者 server
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic

```

### Scope 階層和優先順序

當相同的 server 在多個位置定義時，Claude Code 連接到它一次，使用來自最高優先順序來源的定義。整個 server 項目來自該來源；欄位不會跨範圍合併。

1. Local scope
1. Project scope
1. User scope
1. [Plugin-provided servers](https://code.claude.com/docs/zh-TW/plugins)
1. [claude.ai connectors](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)

三個範圍按名稱符合重複項。Plugins 和 connectors 按端點符合，因此指向與上述 server 相同 URL 或命令的端點被視為重複項。

### `.mcp.json` 中的環境變數擴展

Claude Code 支援 `.mcp.json` 檔案中的環境變數擴展，允許團隊共享配置，同時保持機器特定路徑和 API 金鑰等敏感值的靈活性。 **支援的語法：**

- `${VAR}` - 擴展為環境變數 `VAR` 的值
- `${VAR:-default}` - 如果設定了 `VAR`，則擴展為 `VAR`，否則使用 `default`

**擴展位置：** 環境變數可以在以下位置擴展：

- `command` - server 可執行檔路徑
- `args` - 命令列引數
- `env` - 傳遞給 server 的環境變數
- `url` - 對於 HTTP server 類型
- `headers` - 對於 HTTP server 驗證

**使用變數擴展的範例：**

```
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}

```

如果未設定必需的環境變數且沒有預設值，Claude Code 會將字面 `${VAR}` 文字保留在值中，並為該 server 報告遺漏變數警告。配置仍會載入，因此請設定變數或新增 `:-default` 後備，以便 server 使用您預期的值啟動。

## 實用範例

### 範例：使用 Sentry 監控錯誤

```
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

```

使用您的 Sentry 帳戶進行驗證：

```
/mcp

```

然後除錯生產問題：

```
過去 24 小時內最常見的錯誤是什麼？

```

```
顯示錯誤 ID abc123 的堆疊追蹤

```

```
哪個部署引入了這些新錯誤？

```

### 範例：連接到 GitHub 進行程式碼審查

GitHub 的遠端 MCP server 使用作為標頭傳遞的 GitHub 個人存取 token 進行驗證。若要取得一個，請開啟您的 [GitHub token 設定](https://github.com/settings/personal-access-tokens)，產生一個新的細粒度 token，具有對您希望 Claude 使用的儲存庫的存取權，然後新增 server：

```
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

```

然後使用 GitHub：

```
審查 PR #456 並建議改進

```

```
為我們剛發現的錯誤建立新問題

```

```
顯示所有指派給我的開放 PRs

```

### 範例：查詢您的 PostgreSQL 資料庫

```
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"

```

然後自然地查詢您的資料庫：

```
本月我們的總收入是多少？

```

```
顯示 orders 表的架構

```

```
找到 90 天內未進行購買的客戶

```

## 使用遠端 MCP servers 進行驗證

許多雲端 MCP servers 需要驗證。Claude Code 支援 OAuth 2.0 以進行安全連接。 Claude Code 會在 server 以 `401 Unauthorized` 或 `403 Forbidden` 回應時，將遠端 server 標記為需要驗證。任一狀態碼都會在 `/mcp` 中標記 server，以便您可以完成 OAuth 流程。 當對您已登入的 OAuth server 的請求傳回 `401 Unauthorized` 時，Claude Code 會重新整理儲存的 token、重新連接，並重試請求一次。只有在該重試也失敗時，它才會在 `/mcp` 中標記 server。在 v2.1.206 之前，因為暫時性原因 (例如網路錯誤) 而失敗的 token 重新整理會將 OAuth server 標記為在整個 session 期間需要驗證，即使其重新整理 token 仍然有效。 從 v2.1.195 開始，當 token 重新整理失敗，因為 server 拒絕儲存的重新整理 token 時，Claude Code 會立即顯示指向 `/mcp` 的通知。連接的 server 的功能表會提供「重新驗證」選項，因此您可以在下一個工具呼叫失敗之前重新登入。 傳回指向其授權 server 的 `WWW-Authenticate` 標頭的自訂 server 會獲得與任何其他遠端 server 相同的自動探索。 從 v2.1.193 開始，Claude Code 也會在啟動時顯示通知，當一個或多個已配置的 servers 需要驗證時，因此您不必開啟 `/mcp` 來探索哪些 servers 需要登入。 在非互動模式中，沒有 `/mcp` 面板，因此 Claude Code 無法為您執行 OAuth 流程。從 v2.1.196 開始，當已配置的 server 在 `claude -p` 或啟用[工具搜尋](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search)的 Agent SDK 執行期間需要驗證時 (這是預設值)，Claude Code 會告訴 Claude 該 server 的工具不可用，直到您授權它。Claude 可以命名需要登入的 server，而不是回應為好像 server 未配置。從使用 `/mcp` 或 `claude mcp login <name>` 的互動 session 完成登入。 如果您為 server 配置了 `headers.Authorization`，而 server 拒絕該標頭，Claude Code 會將連接報告為失敗，而不是回退到 OAuth。檢查 token 對 MCP 端點是否有效，或移除標頭以使用 OAuth 流程。 1 新增需要驗證的 server 例如：

```
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

```

2 在 Claude Code 中使用 /mcp 命令 在 Claude Code 中，使用命令：

```
/mcp

```

然後按照瀏覽器中的步驟登入。 提示：

- 驗證 tokens 安全儲存並自動重新整理
- 使用 `/mcp` 功能表中的「Clear authentication」撤銷存取權
- 如果瀏覽器未自動開啟，請複製提供的 URL 並手動開啟
- 如果瀏覽器重新導向在驗證後失敗並出現連接錯誤，請將瀏覽器位址列中的完整回呼 URL 貼到 Claude Code 中出現的 URL 提示中
- OAuth 驗證適用於 HTTP servers

### 從命令列進行驗證

從 v2.1.186 開始，`claude mcp login <name>` 直接從您的 shell 執行已配置 server 的 OAuth 流程，因此您不需要在 session 內開啟 `/mcp` 面板。

```
claude mcp login sentry

```

若要稍後清除儲存的認證，請執行 `claude mcp logout <name>`。 從 v2.1.191 開始，該命令會偵測何時沒有本機瀏覽器可用，例如在 SSH session 期間或在沒有顯示伺服器的 Linux 上，並列印授權 URL 而不是嘗試開啟瀏覽器。在您的本機機器上開啟 URL，然後將瀏覽器位址列中的完整重新導向 URL 貼回提示處。該命令需要互動式終端以進行貼上步驟，因此請使用 `ssh -t` 連接。傳遞 `--no-browser` 以強制 URL 提示，即使偵測到本機瀏覽器。

```
claude mcp login sentry --no-browser

```

### 使用固定的 OAuth 回呼連接埠

某些 MCP servers 需要預先註冊的特定重新導向 URI。根據預設，Claude Code 為 OAuth 回呼選擇隨機可用連接埠。使用 `--callback-port` 固定連接埠，使其符合 `http://localhost:PORT/callback` 形式的預先註冊重新導向 URI。 您可以單獨使用 `--callback-port` (使用動態用戶端註冊) 或與 `--client-id` 一起使用 (使用預先配置的認證)。

```
# 使用動態用戶端註冊的固定回呼連接埠
claude mcp add --transport http \
  --callback-port 8080 \
  my-server https://mcp.example.com/mcp

```

### 使用預先配置的 OAuth 認證

某些 MCP servers 不支援透過 Dynamic Client Registration 進行自動 OAuth 設定。如果您看到類似「Incompatible auth server: does not support dynamic client registration」的錯誤，server 需要預先配置的認證。Claude Code 也支援使用 Client ID Metadata Document (CIMD) 而不是 Dynamic Client Registration 的 servers，並自動探索這些。如果自動探索失敗，請先透過 server 的開發人員入口網站註冊 OAuth 應用程式，然後在新增 server 時提供認證。 1 使用 server 註冊 OAuth 應用程式 透過 server 的開發人員入口網站建立應用程式，並記下您的用戶端 ID 和用戶端密碼。許多 servers 也需要重新導向 URI。如果是這樣，請選擇一個連接埠並以 `http://localhost:PORT/callback` 的格式註冊重新導向 URI。在下一步中使用該相同連接埠搭配 `--callback-port`。 2 使用您的認證新增 server 選擇以下方法之一。用於 `--callback-port` 的連接埠可以是任何可用的連接埠。它只需要符合您在上一步中註冊的重新導向 URI。

- claude mcp add
- claude mcp add-json
- claude mcp add-json (僅回呼連接埠)
- CI / env var

使用 `--client-id` 傳遞您應用程式的用戶端 ID。`--client-secret` 旗標會提示輸入帶有遮罩輸入的密碼：

```
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp

```

在 JSON 配置中包含 `oauth` 物件，並將 `--client-secret` 作為單獨的旗標傳遞：

```
claude mcp add-json my-server \
  '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"clientId":"your-client-id","callbackPort":8080}}' \
  --client-secret

```

使用 `--callback-port` 而不使用用戶端 ID 來固定連接埠，同時使用動態用戶端註冊：

```
claude mcp add-json my-server \
  '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"callbackPort":8080}}'

```

透過環境變數設定密碼以跳過互動式提示：

```
MCP_CLIENT_SECRET=your-secret claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp

```

3 在 Claude Code 中進行驗證 在 Claude Code 中執行 `/mcp` 並按照瀏覽器登入流程。 提示：

- 用戶端密碼安全地儲存在您的系統鑰匙圈 (macOS) 或認證檔案中，而不是在您的配置中
- 如果 server 使用沒有密碼的公開 OAuth 用戶端，請僅使用 `--client-id` 而不使用 `--client-secret`
- `--callback-port` 可以與或不與 `--client-id` 一起使用
- 這些旗標僅適用於 HTTP 和 SSE 傳輸。它們對 stdio servers 沒有影響
- 使用 `claude mcp get <name>` 驗證為 server 配置了 OAuth 認證

### 覆蓋 OAuth 中繼資料探索

指向 Claude Code 特定的 OAuth 授權 server 中繼資料 URL 以繞過預設探索鏈。當 MCP server 的標準端點出錯時，或當您想要透過內部代理路由探索時，設定 `authServerMetadataUrl`。根據預設，Claude Code 首先檢查 RFC 9728 Protected Resource Metadata at `/.well-known/oauth-protected-resource`，然後回退到 RFC 8414 authorization server metadata at `/.well-known/oauth-authorization-server`。 在 `.mcp.json` 中 server 配置的 `oauth` 物件中設定 `authServerMetadataUrl`：

```
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "authServerMetadataUrl": "https://auth.example.com/.well-known/openid-configuration"
      }
    }
  }
}

```

URL 必須使用 `https://`。中繼資料 URL 的 `scopes_supported` 會覆蓋上游 server 宣傳的範圍。

### 限制 OAuth 範圍

設定 `oauth.scopes` 以固定 Claude Code 在授權流程中要求的範圍。這是限制 MCP server 到安全團隊批准的子集的支援方式，當上游授權 server 宣傳的範圍超過您想要授予的範圍時。該值是單個空格分隔的字串，符合 RFC 6749 §3.3 中的 `scope` 參數格式。

```
{
  "mcpServers": {
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp",
      "oauth": {
        "scopes": "channels:read chat:write search:read"
      }
    }
  }
}

```

`oauth.scopes` 優先於 `authServerMetadataUrl` 和 server 在 `/.well-known` 發現的範圍。保持未設定以讓 MCP server 決定要求的範圍集。 從 v2.1.196 開始，當未設定 `oauth.scopes` 時，Claude Code 會要求 server 的 `WWW-Authenticate` 標頭或其受保護資源中繼資料提供的範圍，當兩者都未提供時不傳送 `scope` 參數。它不再要求自動探索的授權 server 中繼資料中的完整 `scopes_supported` 目錄。要求該目錄使得宣傳僅限管理員或範本範圍的身分提供者以 `invalid_scope` 錯誤拒絕授權要求。從配置的 `authServerMetadataUrl` 擷取的中繼資料仍然提供其 `scopes_supported` 作為要求的範圍。 如果授權 server 在 `scopes_supported` 中宣傳 `offline_access`，Claude Code 會將其附加到固定範圍，以便可以在沒有新瀏覽器登入的情況下重新整理存取 token。 如果 server 稍後為工具呼叫傳回 403 `insufficient_scope`，Claude Code 會使用相同的固定範圍重新驗證。當您需要的工具需要固定範圍外的範圍時，擴展 `oauth.scopes`。

### 使用動態標頭進行自訂驗證

如果您的 MCP server 使用 OAuth 以外的驗證方案 (例如 Kerberos、短期 tokens 或內部 SSO)，請使用 `headersHelper` 在連接時產生請求標頭。Claude Code 執行命令並將其輸出合併到連接標頭中。

```
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}

```

命令也可以內聯：

```
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "echo '{\"Authorization\": \"Bearer '\"$(get-token)\"'\"}'"
    }
  }
}

```

**需求：**

- 命令必須將字串鍵值對的 JSON 物件寫入 stdout
- 命令在 shell 中執行，逾時時間為 10 秒，從 session 的目前工作目錄執行。使用絕對路徑或 `PATH` 上的命令來執行指令碼
- 動態標頭會覆蓋任何具有相同名稱的靜態 `headers`

helper 在每次連接時執行 (在 session 啟動和重新連接時)。沒有快取，因此您的指令碼負責任何 token 重複使用。 從 v2.1.193 開始，如果工具呼叫傳回 `401 Unauthorized` 或 `403 Forbidden`，Claude Code 會自動重新執行 helper、使用新標頭重新連接，並重試呼叫一次。Claude Code 只有在該重試也失敗時，才會在 `/mcp` 中將 server 標記為需要驗證。 Claude Code 在執行 helper 時設定這些環境變數：

| 變數                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 值                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE_CODE_MCP_SERVER_NAME`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | MCP server 的名稱                                                                                                    |
| `CLAUDE_CODE_MCP_SERVER_URL`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | MCP server 的 URL                                                                                                    |
| `CLAUDE_PLUGIN_ROOT`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 外掛程式的根目錄。僅當[外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#mcp-servers)提供 server 時設定 |
| 使用這些來編寫為多個 MCP servers 服務的單一 helper 指令碼。 對於外掛程式提供的 server，helper 也會在其工作目錄設定為外掛程式根目錄的情況下執行，因此相對 `headersHelper` 路徑會在外掛程式目錄內解析，而不是針對 session 的工作目錄。需要 Claude Code v2.1.195 或更新版本。 外掛程式提供的 `headersHelper` 無法參考外掛程式的 [`${user_config.*}`](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration) 值，因為命令透過 shell 執行。Claude Code 會報告 server 為配置錯誤，並顯示[錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config)，且不會替換該值。改為將 `${user_config.KEY}` 放在 server 的 `headers` 欄位中，該欄位不會進行 shell 解析，或讓 helper 指令碼從其自己的環境或配置檔案中讀取該值。在 v2.1.207 之前，`headersHelper` 替換了 `${user_config.*}` 值。 |                                                                                                                      |
| `headersHelper` 執行任意 shell 命令。在專案或本機範圍定義時，它僅在您接受工作區信任對話框後執行。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                                                                                                      |

## 從 JSON 配置新增 MCP servers

如果您有 MCP server 的 JSON 配置，您可以直接新增它： 1 從 JSON 新增 MCP server

```
# 基本語法
claude mcp add-json <name> '<json>'

# 範例：使用 JSON 配置新增 HTTP server
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# 範例：使用 JSON 配置新增 stdio server
claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'

# 範例：使用預先配置的 OAuth 認證新增 HTTP server
claude mcp add-json my-server '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"clientId":"your-client-id","callbackPort":8080}}' --client-secret

```

2 驗證 server 已新增

```
claude mcp get weather-api

```

提示：

- 確保 JSON 在您的 shell 中正確逸出
- JSON 必須符合 MCP server 配置架構
- 您可以使用 `--scope user` 將 server 新增到您的使用者配置，而不是專案特定的配置

## 從 Claude Desktop 匯入 MCP servers

如果您已在 Claude Desktop 中配置了 MCP servers，您可以匯入它們： 1 從 Claude Desktop 匯入 servers

```
# 基本語法
claude mcp add-from-claude-desktop

```

2 選擇要匯入的 servers 執行命令後，您會看到一個互動式對話框，允許您選擇要匯入的 servers。 3 驗證 servers 已匯入

```
claude mcp list

```

透過 `claude mcp` 命令新增的伺服器名稱只能包含字母、數字、連字號和底線。Claude Desktop 不會套用該限制，因此名稱包含任何其他字元（例如空格）的 Claude Desktop 伺服器無法匯入。匯入會報告它拒絕的每個名稱，並仍會匯入您選擇的其他伺服器。在 v2.1.205 之前，第一個無效名稱會停止匯入，且不會新增任何選定的伺服器。 提示：

- 此功能僅適用於 macOS 和 Windows Subsystem for Linux (WSL)
- 它從這些平台上的標準位置讀取 Claude Desktop 配置檔案
- 使用 `--scope user` 旗標將 servers 新增到您的使用者配置
- 匯入的 servers 將具有與 Claude Desktop 中相同的名稱（當名稱只包含字母、數字、連字號和底線時）。Claude Code 會報告名稱包含任何其他字元的伺服器並跳過它
- 如果已存在相同名稱的 servers，它們將獲得數字尾碼（例如，`server_1`）

## 使用來自 claude.ai 的 MCP servers

如果您已使用 [claude.ai](https://claude.ai) 帳戶登入 Claude Code，您在 claude.ai 中新增的 MCP servers（稱為 [connectors](https://claude.com/docs/connectors)）會自動在 Claude Code 中可用： 1 在 claude.ai 中配置 MCP servers 在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 新增 servers。在 Team 和 Enterprise 計畫上，只有管理員可以新增 servers。 2 驗證 MCP server 在 claude.ai 中完成任何必需的驗證步驟。 3 在 Claude Code 中檢視和管理 servers 在 Claude Code 中，使用命令：

```
/mcp

```

Claude.ai servers 在列表中出現，並有指示器顯示它們來自 claude.ai。 從 v2.1.161 開始，您從未登入過的 connectors 會在 claude.ai 部分末尾的 `Show unused connectors` 列後面摺疊，因此組織佈建的列表不會填滿面板。選擇該列以展開它們。您之前登入過的 connector 即使目前需要重新驗證，也會保持可見。 Claude.ai connectors 只有在您的活躍[驗證方法](https://code.claude.com/docs/zh-TW/authentication#authentication-precedence)是您的 claude.ai 訂閱時才會被取得。當 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`apiKeyHelper` 或第三方提供者（例如 Amazon Bedrock 或 Google Cloud 的 Agent Platform）處於活躍狀態時，它們不會被載入，即使您之前執行過 `/login`。如果 `/mcp` 沒有列出您新增的 connector，請執行 `/status` 以確認哪個驗證方法處於活躍狀態，取消設定該環境變數或移除 `apiKeyHelper` 設定，然後執行 `/login` 以選擇您的 claude.ai 帳戶。 您在 Claude Code 中新增的 server 優先於指向相同 URL 的 claude.ai connector。發生這種情況時，`/mcp` 會將 connector 列為隱藏，並顯示如何移除重複項（如果您寧願使用 connector）。 某些 Anthropic 託管的 connectors（例如 Microsoft 365、Gmail 和 Google Calendar）不支援來自 Claude Code 的本機 OAuth，因為上游身分識別提供者只接受 claude.ai 註冊的重新導向 URL。從 v2.1.162 開始，在 `/mcp` 中驗證其中一個主機會顯示一條訊息，指導您改為在 claude.ai 上的設定 → Connectors 中連接它。連接後，connector 會自動出現在 Claude Code 中。

### 組織對 connector 工具的控制

您的組織可以在 [claude.ai connectors](https://claude.com/docs/connectors) 上設定每個工具的控制。Claude Code 在啟動時讀取這些設定並在本機強制執行。執行 `/mcp` 以查看哪個設定適用於 connector 上的每個工具。

- **工具設定為`ask`** ：Claude Code 會在每次呼叫時提示，原因為 `Your organization requires approval for this tool`。即使在 `acceptEdits`、`auto` 和 `bypassPermissions` [權限模式](https://code.claude.com/docs/zh-TW/permissions#permission-modes)中，提示也會出現，並且永遠不會提供記住您選擇的選項。符合該工具的[允許規則](https://code.claude.com/docs/zh-TW/permissions)也不會跳過提示。在 `dontAsk` 模式中（永遠不提示），Claude Code 會改為拒絕呼叫。
- **工具設定為`blocked`** ：Claude Code 在 Claude 看到之前會過濾掉該工具，因此它永遠不會出現在工具列表中。

強制執行這些控制需要 Claude Code v2.1.129 或更新版本。較早的版本會忽略設定並應用標準權限流程。

### 停用 claude.ai connectors

若要在 Claude Code 中停用 claude.ai MCP servers，請將 [`disableClaudeAiConnectors`](https://code.claude.com/docs/zh-TW/settings#available-settings) 設定為 `true`（在任何設定範圍中）：

```
{
  "disableClaudeAiConnectors": true
}

```

此設定使用任何來源為真的語義：任何設定來源中的 `true` 優先。已簽入的專案 `.claude/settings.json` 可以選擇退出雲端 connectors，但專案層級的 `false` 無法重新啟用使用者或政策層級 `true` 已停用的 connectors。透過 `--mcp-config` 明確傳遞的 servers 不受影響。 您也可以將 `ENABLE_CLAUDEAI_MCP_SERVERS` 環境變數設定為 `false`，這對目前的 shell 工作階段有相同的效果：

```
ENABLE_CLAUDEAI_MCP_SERVERS=false claude

```

若要阻止個別 claude.ai connectors 而不是全部，請按名稱或 URL 模式將它們新增至 [`deniedMcpServers`](https://code.claude.com/docs/zh-TW/managed-mcp)。例如，`serverName` 項目 `"claude.ai Slack"` 會阻止 Slack connector。若要僅針對目前專案切換 connector 的開啟或關閉，請使用 `/mcp` 面板。 這些用戶端設定管理本機 Claude Code 工作階段。在 [Claude Code on the web](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 工作階段中，claude.ai connectors 由遠端主機佈建，並作為明確的 `--mcp-config` 項目到達，因此 `disableClaudeAiConnectors` 不適用於此處。Connector URL 也會透過工作階段代理重寫，因此針對廠商 URL 的 `deniedMcpServers` `serverUrl` 模式將不會符合。從您的 claude.ai 組織設定管理雲端工作階段可以使用哪些 connectors。

## 使用 Claude Code 作為 MCP server

您可以使用 Claude Code 本身作為其他應用程式可以連接到的 MCP server：

```
# 啟動 Claude 作為 stdio MCP server
claude mcp serve

```

您可以透過將此配置新增到 claude_desktop_config.json 在 Claude Desktop 中使用它：

```
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}

```

**配置可執行檔路徑** ：`command` 欄位必須參考 Claude Code 可執行檔。如果 `claude` 命令不在您的系統 PATH 中，您需要指定可執行檔的完整路徑。若要找到完整路徑：

```
which claude

```

然後在您的配置中使用完整路徑：

```
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "/full/path/to/claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}

```

沒有正確的可執行檔路徑，您會遇到類似 `spawn claude ENOENT` 的錯誤。 提示：

- server 提供對 Claude 工具 (如 View、Edit、LS 等) 的存取
- 在 Claude Desktop 中，嘗試要求 Claude 讀取目錄中的檔案、進行編輯等。
- 請注意，此 MCP server 僅將 Claude Code 的工具公開給您的 MCP 用戶端，因此您自己的用戶端負責為個別工具呼叫實現使用者確認。

## MCP 輸出限制和警告

當 MCP 工具產生大型輸出時，Claude Code 可幫助管理 token 使用情況，以防止淹沒您的對話內容：

- **輸出警告閾值** ：當任何 MCP 工具輸出超過 10,000 個 tokens 時，Claude Code 會顯示警告
- **可配置限制** ：您可以使用 `MAX_MCP_OUTPUT_TOKENS` 環境變數調整最大允許的 MCP 輸出 tokens
- **預設限制** ：預設最大值為 25,000 個 tokens
- **範圍** ：環境變數適用於未宣告自己限制的工具。設定 [`anthropic/maxResultSizeChars`](https://code.claude.com/docs/zh-TW/mcp#raise-the-limit-for-a-specific-tool) 的工具使用該值代替文字內容，無論 `MAX_MCP_OUTPUT_TOKENS` 設定為什麼。傳回影像資料的工具仍受 `MAX_MCP_OUTPUT_TOKENS` 限制

若要增加產生大型輸出的工具的限制：

```
export MAX_MCP_OUTPUT_TOKENS=50000
claude

```

這在使用以下 MCP servers 時特別有用：

- 查詢大型資料集或資料庫
- 產生詳細報告或文件
- 處理廣泛的日誌檔案或除錯資訊

### 提高特定工具的限制

如果您正在建立 MCP server，您可以透過在工具的 `tools/list` 回應項目中設定 `_meta["anthropic/maxResultSizeChars"]` 來允許個別工具傳回超過預設持久化到磁碟閾值的結果。Claude Code 將該工具的閾值提高到註解值，最高為 500,000 個字元的硬上限。 這對於傳回本質上很大但必要的輸出的工具很有用，例如資料庫架構或完整檔案樹。沒有註解，超過預設閾值的結果會持久化到磁碟，並在對話中被檔案參考取代。

```
{
  "name": "get_schema",
  "description": "Returns the full database schema",
  "_meta": {
    "anthropic/maxResultSizeChars": 200000
  }
}

```

對於文字內容，註解獨立於 `MAX_MCP_OUTPUT_TOKENS` 應用，因此使用者無需提高環境變數來使用宣告它的工具。傳回影像資料的工具仍受 token 限制。 如果您經常遇到特定 MCP servers 的輸出警告，請考慮增加 `MAX_MCP_OUTPUT_TOKENS` 限制。您也可以要求 server 作者新增 `anthropic/maxResultSizeChars` 註解或分頁其回應。註解對傳回影像內容的工具沒有影響；對於這些，提高 `MAX_MCP_OUTPUT_TOKENS` 是唯一的選項。

## 具有根層級組合器的工具輸入架構

某些 MCP servers 將工具的輸入架構宣告為 JSON Schema 聯合，在架構的頂層具有 `anyOf`、`oneOf` 或 `allOf`。Claude API 不接受這些關鍵字在架構根目錄。它接受在 `properties` 內嵌套的組合器，Claude Code 會原封不動地傳送。 從 Claude Code v2.1.195 開始，具有根層級組合器的工具保持可用。在將工具傳送到 API 之前，Claude Code 會將架構平坦化為單個物件，並在工具的描述前面加上一句話，告訴 Claude 哪些參數組屬於一起：

- `allOf`：來自每個分支的屬性被合併，每個分支的 `required` 列表仍然適用
- `anyOf` 和 `oneOf`：來自每個分支的屬性被合併，每個分支的 `required` 列表在工具描述中描述，而不是由架構強制執行

您的 server 會接收 Claude 選擇的任何引數，因此請繼續在伺服器端驗證組合。 當 Claude Code 無法產生 API 接受的架構，或在不接收啟用重寫的遠端配置的部署上時（例如離線機器），它會跳過該工具，在 server 的日誌中記錄原因，並保持 server 的其他工具可用。早於 v2.1.195 的版本會跳過輸入架構具有根層級 `anyOf`、`oneOf` 或 `allOf` 的每個工具。

## 要求特定工具的批准

如果您正在建立 MCP server，您可以透過在工具的 `tools/list` 回應項目中將 `_meta["anthropic/requiresUserInteraction"]` 設定為 `true` 來標記工具為在每次呼叫時需要明確批准。該值必須是 JSON 布林值 `true`；任何其他值都會被忽略。 Claude Code 在每次呼叫時顯示該工具的權限提示，即使在 `acceptEdits`、`auto` 和 `bypassPermissions` [permission modes](https://code.claude.com/docs/zh-TW/permissions#permission-modes) 中，並且不提供「不再詢問」選項。[Allow rules](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax) 符合該工具的也不會跳過提示。在 `dontAsk` 模式中（從不提示），Claude Code 會改為拒絕呼叫。 提示必須到達一個人。在非互動模式下使用 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)，來自提示工具的 `allow` 結果對於標記的工具會轉換為拒絕，訊息為 `MCP tool requires user interaction; not supported via --permission-prompt-tool`。Agent SDK 的 [`canUseTool` 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/permissions) 確實會接收這些呼叫並可以批准它們，因為 SDK 主機應該向使用者顯示它們。 將此用於其權限提示本身就是重點的工具，例如同意或存取授予步驟，其中自動批准意味著沒有人類曾經同意。來自同一 server 的其他工具保持其正常權限行為。 以下 `tools/list` 項目將一個工具標記為始終需要批准。

```
{
  "name": "grant_access",
  "description": "Requests access to a protected resource",
  "_meta": {
    "anthropic/requiresUserInteraction": true
  }
}

```

`anthropic/requiresUserInteraction` 註解需要 Claude Code v2.1.199 或更新版本。較早的版本會忽略它並應用標準權限流程。 當 session 連接到 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 或 SDK 主機時，Claude Code 會將權限請求標記為需要使用者互動，因此用戶端會向您顯示工具的權限提示，而不是單點擊批准操作。

## 回應 MCP 引發請求

MCP servers 可以使用引發在任務中途要求您提供結構化輸入。當 server 需要無法自行取得的資訊時，Claude Code 會顯示互動式對話框並將您的回應傳回給 server。您無需進行任何配置：當 server 要求時，引發對話框會自動出現。 Servers 可以透過兩種方式要求輸入：

- **表單模式** ：Claude Code 顯示一個對話框，其中包含 server 定義的表單欄位 (例如，使用者名稱和密碼提示)。填入欄位並提交。
- **URL 模式** ：Claude Code 開啟瀏覽器 URL 以進行驗證或批准。在瀏覽器中完成流程，然後在 CLI 中確認。

若要自動回應引發請求而不顯示對話框，請使用 [`Elicitation` hook](https://code.claude.com/docs/zh-TW/hooks#elicitation)。 如果您正在建立使用引發的 MCP server，請參閱 [MCP 引發規格](https://modelcontextprotocol.io/docs/learn/client-concepts#elicitation)，了解協議詳細資訊和架構範例。

## 使用 MCP 資源

MCP servers 可以公開資源，您可以使用 @ 提及來參考，類似於您參考檔案的方式。

### 參考 MCP 資源

1 列出可用資源 在您的提示中輸入 `@` 以查看所有連接的 MCP servers 中的可用資源。資源與檔案一起出現在自動完成功能表中。 2 參考特定資源 使用格式 `@server:protocol://resource/path` 來參考資源：

```
Can you analyze @github:issue://123 and suggest a fix?

```

```
Please review the API documentation at @docs:file://api/authentication

```

3 多個資源參考 您可以在單個提示中參考多個資源：

```
Compare @postgres:schema://users with @docs:file://database/user-model

```

提示：

- 資源在參考時會自動取得並作為附件包含
- 資源路徑在 @ 提及自動完成中可進行模糊搜尋
- Claude Code 在 servers 支援時自動提供列出和讀取 MCP 資源的工具
- 資源可以包含 MCP server 提供的任何類型的內容 (文字、JSON、結構化資料等)

## 使用 MCP Tool Search 進行擴展

Tool search 透過延遲工具定義直到 Claude 需要它們來保持 MCP 內容使用低。只有工具名稱和伺服器指示在 session 啟動時載入，因此新增更多 MCP servers 對您的內容視窗的影響最小。Claude Code 不會對每個伺服器施加固定的工具上限；實際限制是您的內容視窗預算。

### 工作原理

Tool search 預設啟用。MCP 工具被延遲而不是預先載入到內容中，Claude 使用搜尋工具在任務需要時探索相關的工具。只有 Claude 實際使用的工具才會進入內容。從您的角度來看，MCP 工具的工作方式完全相同。 如果您偏好基於閾值的載入，請設定 `ENABLE_TOOL_SEARCH=auto` 以在工具適合內容視窗的 10% 內時預先載入架構，並僅延遲溢出。請參閱 [配置 tool search](https://code.claude.com/docs/zh-TW/mcp#configure-tool-search) 了解所有選項。

### 對於 MCP server 作者

如果您正在建立 MCP server，啟用 Tool Search 時 server 指示欄位會變得更有用。Server 指示可幫助 Claude 了解何時搜尋您的工具，類似於 [skills](https://code.claude.com/docs/zh-TW/skills) 的工作方式。 新增清晰、描述性的 server 指示，說明：

- 您的工具處理的任務類別
- Claude 應何時搜尋您的工具
- 您的 server 提供的關鍵功能

Claude Code 將工具描述和 server 指示截斷為每個 2KB。保持簡潔以避免截斷，並將關鍵詳細資訊放在開始處。

### 配置 tool search

Tool search 預設啟用：MCP 工具被延遲並按需探索。Claude Code 在 Google Cloud 的 Agent Platform 上預設停用它。當 `ANTHROPIC_BASE_URL` 指向非第一方主機時，它也被停用，因為大多數代理不轉發 `tool_reference` 區塊。設定 `ENABLE_TOOL_SEARCH` 明確以覆蓋任一回退。 設定 [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`](https://code.claude.com/docs/zh-TW/env-vars) 保持 tool search 關閉，且 `ENABLE_TOOL_SEARCH` 無法覆蓋它。該變數會移除 `defer_loading` 工具定義和 `tool_reference` 內容區塊所需的 beta 標頭。 Tool search 需要支援 `tool_reference` 區塊的模型：Claude Sonnet 4.5、Claude Haiku 4.5、Claude Opus 4.5 及更新版本。請參閱 [API 文件中的模型相容性](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#model-compatibility) 以取得目前清單。在 Google Cloud 的 Agent Platform 上，tool search 支援 Claude Sonnet 4.5 及更新版本和 Claude Opus 4.5 及更新版本。 使用 `ENABLE_TOOL_SEARCH` 環境變數控制 tool search 行為：

| 值       | 行為                                                                                                                                                                                                                              |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| (未設定) | 所有 MCP 工具被延遲並按需載入。在 Google Cloud 的 Agent Platform 上或當 `ANTHROPIC_BASE_URL` 是非第一方主機時回退到預先載入                                                                                                       |
| `true`   | 所有 MCP 工具被延遲。Claude Code 即使在 Google Cloud 的 Agent Platform 上和透過代理也會傳送 beta 標頭。在 Google Cloud 的 Agent Platform 模型早於 Sonnet 4.5 或 Opus 4.5 上，或在不支援 `tool_reference` 區塊的代理上，請求會失敗 |
| `auto`   | 閾值模式：如果工具適合內容視窗的 10% 內，則預先載入，否則延遲                                                                                                                                                                     |
| `auto:N` | 閾值模式，具有自訂百分比，其中 `N` 是 0-100。例如，`auto:5` 表示 5%                                                                                                                                                               |
| `false`  | 所有 MCP 工具預先載入，無延遲                                                                                                                                                                                                     |

```
# 使用自訂 5% 閾值
ENABLE_TOOL_SEARCH=auto:5 claude

# 完全停用 tool search
ENABLE_TOOL_SEARCH=false claude

```

或在您的 [settings.json `env` 欄位](https://code.claude.com/docs/zh-TW/settings#available-settings) 中設定值。 您也可以特別停用 `ToolSearch` 工具：

```
{
  "permissions": {
    "deny": ["ToolSearch"]
  }
}

```

### 豁免伺服器延遲

如果伺服器的工具應始終對 Claude 可見而無需搜尋步驟，請在該伺服器的配置中將 `alwaysLoad` 設定為 `true`。該伺服器的每個工具隨後都會在 session 啟動時載入到內容中，無論 `ENABLE_TOOL_SEARCH` 設定如何。對於 Claude 在每個回合都需要的少量工具，請使用此選項，因為每個預先載入的工具會消耗內容，否則這些內容將可用於您的對話。 以下 `.mcp.json` 項目豁免一個 HTTP 伺服器，同時保持其他伺服器延遲：

```
{
  "mcpServers": {
    "core-tools": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "alwaysLoad": true
    }
  }
}

```

`alwaysLoad` 欄位在所有伺服器類型上可用，需要 Claude Code v2.1.121 或更新版本。MCP 伺服器也可以透過在工具的 `_meta` 物件中包含 `"anthropic/alwaysLoad": true` 來標記個別工具為始終載入，這對該工具只有相同的效果。 設定 `alwaysLoad: true` 也會阻止啟動直到伺服器連線，上限為標準 5 秒連線逾時。即使 MCP 啟動在其他方面[預設為非阻塞](https://code.claude.com/docs/zh-TW/env-vars)，這也適用，因為工具必須在建立第一個提示時存在。其他伺服器繼續在背景中連線。

## 使用 MCP 提示作為命令

MCP servers 可以公開提示，這些提示在 Claude Code 中變成可用的命令。

### 執行 MCP 提示

1 探索可用提示 輸入 `/` 以查看所有可用命令，包括來自 MCP servers 的命令。MCP 提示以 `/mcp__servername__promptname` 的格式出現。 2 執行沒有引數的提示

```
/mcp__github__list_prs

```

3 執行帶有引數的提示 許多提示接受引數。在命令後以空格分隔的方式傳遞它們：

```
/mcp__github__pr_review 456

```

```
/mcp__jira__create_issue "Bug in login flow" high

```

提示：

- MCP 提示從連接的 servers 動態探索
- 引數根據提示的定義參數進行解析
- 提示結果直接注入到對話中
- Server 和提示名稱已標準化，空格變成底線

## 受管理的 MCP 配置

對於需要對使用者可以連接的 MCP servers 進行集中控制的組織，請參閱 [受管理的 MCP 配置](https://code.claude.com/docs/zh-TW/managed-mcp)。它涵蓋使用 `managed-mcp.json` 部署固定的 server 集合、使用 `allowedMcpServers` 和 `deniedMcpServers` 限制 servers，以及當 server 被阻止時使用者看到的內容。 是否 助手
