[Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 提供與 Claude Code 相同的工具、agent 迴圈和上下文管理。它可作為 CLI 用於指令碼和 CI/CD，或作為 [Python](https://code.claude.com/docs/zh-TW/agent-sdk/python) 和 [TypeScript](https://code.claude.com/docs/zh-TW/agent-sdk/typescript) 套件供完整的程式控制。 若要以非互動模式執行 Claude Code，請傳遞 `-p` 和您的提示以及任何 [CLI 選項](https://code.claude.com/docs/zh-TW/cli-reference)：

```
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"

```

本頁涵蓋透過 CLI (`claude -p`) 使用 Agent SDK。如需具有結構化輸出、工具核准回呼和原生訊息物件的 Python 和 TypeScript SDK 套件，請參閱 [完整 Agent SDK 文件](https://code.claude.com/docs/zh-TW/agent-sdk/overview)。

## 基本用法

將 `-p`（或 `--print`）旗標新增至任何 `claude` 命令以非互動方式執行它。並非所有 [CLI 選項](https://code.claude.com/docs/zh-TW/cli-reference) 都適用於 `-p`。Claude Code 拒絕 `--bg`，並在有工作描述時拒絕 `--cloud`，並出現命名衝突的錯誤；`--cloud` 搭配工作階段 ID 和 `-p` 改為 [將訊息加入該雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-follow-ups-from-the-cli) 並結束。您經常搭配 `-p` 使用的選項包括：

- `--continue` 用於 [繼續對話](https://code.claude.com/docs/zh-TW/headless#continue-conversations)
- `--allowedTools` 用於 [自動核准工具](https://code.claude.com/docs/zh-TW/headless#auto-approve-tools)
- `--output-format` 用於 [結構化輸出](https://code.claude.com/docs/zh-TW/headless#get-structured-output)

此範例詢問 Claude 關於您的程式碼庫的問題並列印回應：

```
claude -p "What does the auth module do?"

```

Claude Code 在成功時以代碼 0 結束，在執行失敗時以非零代碼結束，因此您的指令碼可以根據結束狀態進行分支。如果您傳遞無效旗標，Claude Code 會在執行開始前向 stderr 報告錯誤。當執行內發生失敗時，例如缺少驗證，Claude Code 會將失敗列印為 stdout 上的結果。

### 使用裸機模式加快速度

新增 `--bare` 以跳過 hooks、skills、自訂命令、[subagents](https://code.claude.com/docs/zh-TW/sub-agents)、plugins、MCP 伺服器、自動記憶體和 CLAUDE.md 的自動探索來減少啟動時間。沒有它，`claude -p` 會載入互動式工作階段會載入的相同 [上下文](https://code.claude.com/docs/zh-TW/how-claude-code-works#the-context-window)，包括在工作目錄或 `~/.claude` 中設定的任何內容。 裸機模式對於 CI 和指令碼很有用，您需要在每台機器上獲得相同的結果。隊友 `~/.claude` 中的 hook 或專案的 `.mcp.json` 中的 MCP 伺服器不會執行，因為裸機模式永遠不會讀取它們。您使用 `--add-dir` 命名的目錄是部分例外：裸機模式會從其 `.claude/skills/` 資料夾載入 skills，但仍會跳過其 `.claude/commands/` 和 `.claude/agents/` 資料夾。[來自其他目錄的 Skills](https://code.claude.com/docs/zh-TW/skills#skills-from-additional-directories) 涵蓋載入和不載入的內容。 沒有 `--bare`，`-p` 工作階段會執行專案 `.claude/settings.json` 中的 hooks 並連接其 `.mcp.json` 中的伺服器，即使在您從未信任的資料夾中也是如此。`-p` 工作階段不會顯示工作區信任對話方塊和每個伺服器的核准提示。[在您信任資料夾之前執行的內容](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 涵蓋 `-p` 下每種存放庫內容以及如何將其排除在外。 此範例在裸機模式下執行一次性摘要工作，並預先核准 Read 工具，以便呼叫完成而無需許可提示。執行前設定 `ANTHROPIC_API_KEY`，因為裸機模式不使用您的訂閱登入：

```
claude --bare -p "Summarize README.md" --allowedTools "Read"

```

在裸機模式下，Claude Code 永遠不會讀取 OAuth 認證或系統鑰匙圈。對於 Anthropic API，在環境中設定 `ANTHROPIC_API_KEY`，使用在 [Claude Console](https://platform.claude.com) 中建立的金鑰，或在 `--settings` JSON 中提供 `apiKeyHelper`。Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 繼續照常讀取其自己的提供者認證。 在裸機模式下，Claude 可以存取 Bash、檔案讀取和檔案編輯工具。使用旗標傳遞您需要的任何上下文：

| 要載入                                                                     | 使用                                                    |
| -------------------------------------------------------------------------- | ------------------------------------------------------- |
| 系統提示新增                                                               | `--append-system-prompt`, `--append-system-prompt-file` |
| 設定                                                                       | `--settings <file-or-json>`                             |
| MCP 伺服器                                                                 | `--mcp-config <file-or-json>`                           |
| 自訂 agents                                                                | `--agents <json>`                                       |
| 外掛程式                                                                   | `--plugin-dir <path>`, `--plugin-url <url>`             |
| `--bare` 是指令碼和 SDK 呼叫的建議模式，將在未來版本中成為 `-p` 的預設值。 |                                                         |

### 結束時的背景工作

如果 Claude 在 `claude -p` 執行期間啟動 [背景 Bash 工作](https://code.claude.com/docs/zh-TW/tools-reference#bash-tool-behavior)，例如開發伺服器或監視組建，該工作將在 Claude 傳回其最終結果且 stdin 已關閉後約五秒鐘終止。寬限期允許在結果之後立即完成的工作仍然傳遞其輸出。 如果 Claude 啟動背景 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 或工作流程，`claude -p` 改為保持開啟直到該工作完成，因為其結果是最終輸出的一部分。 根據預設，等待在連續閒置等待 10 分鐘後結束，因此卡住的 subagent 或工作流程無法無限期地保持程序開啟。此時 Claude Code 停止仍在執行的任何內容並捨棄其部分結果。若要變更限制，請設定 [`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`](https://code.claude.com/docs/zh-TW/env-vars)，或將其設定為 `0` 以無限制地等待。 如果 Claude 在 `claude -p` 執行期間啟動 [Monitor](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool) 監視，Claude Code 會等待監視直到它逾時或十分鐘上限結束等待，以先發生者為準。在等待期間，Claude 會持續回應監視報告的內容。根據預設，監視在 Claude 啟動它後五分鐘逾時。

### 使用 SIGTERM 停止執行

如果您使用 SIGTERM 停止 `claude -p` 執行，例如使用 `kill` 或從程序監督員，Claude Code 以代碼 143 結束。Claude Code 將進行中的轉換保留為未完成狀態，並為其記錄無結果。若要改為結束轉換，請傳送 SIGINT，或在停止程序前呼叫 Agent SDK 的 `interrupt()`。 在 SIGTERM 上，Claude Code 終止仍在執行的任何 Bash 命令的程序樹。Claude Code 然後執行 [`SessionEnd` hooks](https://code.claude.com/docs/zh-TW/hooks#sessionend) 並結束。結束時，Claude Code 不啟動新工具呼叫、不傳送新模型請求，也不執行除 `SessionEnd` 以外的任何 hook。如果執行在命令中間或在信號到達時等待許可提示的答案，Claude Code 會按如下方式處理該步驟：

- **執行命令** ：Claude Code 在工作階段中將命令記錄為已終止。
- **等待許可提示的答案** ：如果您向程序傳送 SIGTERM，Claude Code 會將提示保留為未回答。如果您的程式透過 Agent SDK 關閉工作階段，SDK 會在傳送任何信號前結束 Claude Code 的輸入，Claude Code 會在輸入結束時立即取消提示。

當您 [繼續工作階段](https://code.claude.com/docs/zh-TW/headless#continue-conversations) 時，Claude Code 繼續 SIGTERM 留下的未完成轉換。

## 範例

這些範例突出了常見的 CLI 模式。如果命令指定了檔案（例如 `auth.py` 或 `build-error.txt`），請替換為您自己專案中的檔案。在 CI 或其他指令碼環境中，添加 [`--bare`](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)，以便 Claude Code 啟動時不載入主機的 hooks、plugins、自動記憶或 `CLAUDE.md`。

### 透過 Claude 傳輸資料

非互動模式讀取 stdin，因此您可以像任何其他命令列工具一樣透過管道傳入資料並重新導向回應。 此範例將建置日誌傳輸到 Claude 並將說明寫入檔案：

```
cat build-error.txt | claude -p 'concisely explain the root cause of this build error' > output.txt

```

使用 `--output-format json` 時，回應承載包括 `total_cost_usd` 和按模型的成本明細，因此指令碼呼叫者可以追蹤每次調用的支出，而無需查詢[使用儀表板](https://code.claude.com/docs/zh-TW/costs)。這兩個數字都是[用戶端估計](https://code.claude.com/docs/zh-TW/agent-sdk/cost-tracking)，可能與您的實際帳單不同。 管道 stdin 的上限為 10MB。如果超過上限，Claude Code 會以清晰的錯誤訊息退出並返回非零狀態。若要處理更大的輸入，請將內容寫入檔案，並在提示中參考檔案路徑，而不是透過管道傳輸。 如果 Claude Code 無法讀取 stdin（例如因為啟動它的程序斷開了其端點），Claude Code 會向 stderr 列印警告並繼續使用命令列中的提示。在 v2.1.211 之前，Windows 上無法讀取的 stdin 會導致工作階段崩潰或無輸出地無聲退出。

### 將 Claude 添加到建置指令碼

您可以在指令碼中包裝非互動呼叫，以將 Claude 用作專案特定的 linter 或審查者。 此 `package.json` 指令碼將針對 `main` 的差異傳輸到 Claude，並要求它報告拼寫錯誤。傳輸差異意味著 Claude 不需要 Bash 權限來讀取它，而轉義的雙引號使指令碼可移植到 Windows：

```
{
  "scripts": {
    "lint:claude": "git diff main | claude -p \"you are a typo linter. for each typo in this diff, report filename:line on one line and the issue on the next. return nothing else.\""
  }
}

```

使用 `npm run lint:claude` 執行它。

### 取得結構化輸出

使用 `--output-format` 控制回應的返回方式：

- `text`（預設）：純文字輸出
- `json`：包含結果、工作階段 ID 和中繼資料的結構化 JSON
- `stream-json`：用於即時串流的換行分隔 JSON

此範例以 JSON 格式返回專案摘要及工作階段中繼資料，文字結果在 `result` 欄位中：

```
claude -p "Summarize this project" --output-format json

```

若要取得符合特定結構描述的輸出，請使用 `--output-format json` 搭配 `--json-schema` 和 [JSON Schema](https://json-schema.org/) 定義。回應包括關於請求的中繼資料（工作階段 ID、使用情況等），結構化輸出在 `structured_output` 欄位中。 此範例從 auth.py 提取函式名稱並將其作為字串陣列返回：

```
claude -p "Extract the main function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'

```

如果值不是有效的 JSON Schema，`claude` 會以 `Error: --json-schema is not a valid JSON Schema` 退出，後面跟著驗證器的診斷。Claude Code 接受使用 `format` 關鍵字的結構描述，例如 `"format": "email"`，但將 `format` 視為註解，不強制執行。在 v2.1.205 之前，Claude Code 無聲地忽略無效的結構描述並返回非結構化文字，並將任何包含 `format` 的結構描述視為無效。 使用 [jq](https://jqlang.org/) 之類的工具來解析回應並提取特定欄位：

```
# Extract the text result
claude -p "Summarize this project" --output-format json | jq -r '.result'

# Extract structured output
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  | jq '.structured_output'

```

### 串流回應

使用 `--output-format stream-json` 搭配 `--verbose` 和 `--include-partial-messages` 以在產生令牌時接收它們。每一行都是代表一個事件的 JSON 物件：

```
claude -p "Explain recursion" --output-format stream-json --verbose --include-partial-messages

```

串流的最後一行是包含最終回應文字、成本和工作階段中繼資料的 `result` 訊息。 如果您的消費者緩慢讀取串流，Claude Code 會等待佇列中的輸出排出後再退出，根據仍在佇列中的數量調整等待時間，上限為 30 秒。在 v2.1.214 之前，退出等待上限約為 2 秒，這可能會截斷大型回應的末尾。 以下範例使用 [jq](https://jqlang.org/) 篩選文字增量並僅顯示串流文字。`-r` 旗標輸出原始字串（無引號），`-j` 不帶換行符連接，因此令牌連續串流：

```
claude -p "Write a poem" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'

```

如需具有回呼和訊息物件的程式化串流，請參閱 Agent SDK 文件中的[即時串流回應](https://code.claude.com/docs/zh-TW/agent-sdk/streaming-output)。

#### 追蹤子代理訊息

來自[子代理](https://code.claude.com/docs/zh-TW/sub-agents)的訊息在串流中顯示為 `assistant` 和 `user` 訊息，其 `parent_tool_use_id` 欄位是產生子代理的工具呼叫的 ID。來自主要對話的訊息在該欄位中帶有 `null`。 來自在[前景](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)中執行的子代理的第一條訊息是 `user` 訊息，帶有驅動它的提示。在該第一條訊息之後，Claude Code 發出：

- **預設情況下** ：子代理的 `tool_use` 和 `tool_result` 區塊。
- **使用[`--forward-subagent-text`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 或 [`CLAUDE_CODE_FORWARD_SUBAGENT_TEXT`](https://code.claude.com/docs/zh-TW/env-vars)**：子代理的文字和思考區塊，因此您可以重建每個子代理的文字記錄。這需要 Claude Code v2.1.211 或更新版本。

當您啟用任一選項時，Claude Code 從[每個巢狀深度的子代理](https://code.claude.com/docs/zh-TW/sub-agents#let-subagents-spawn-their-own-subagents)轉發訊息：當子代理產生自己的子代理時，巢狀子代理的訊息在 `parent_tool_use_id` 中帶有產生它的 Agent 工具呼叫的 ID，因此您可以透過追蹤這些 ID 來重建完整的巢狀樹。在 v2.1.219 之前，來自巢狀子代理的訊息不會出現在串流中。 [在子代理中執行](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)的 Skills 在串流中以相同方式出現：分叉的 skill 的第一條訊息是 `user` 訊息，帶有驅動執行的 skill 內容。如果您啟用任一選項，串流也會帶有分叉的 skill 的文字和思考區塊。在 v2.1.265 之前，只有分叉的 skill 的 `tool_use` 和 `tool_result` 區塊出現在串流中。

#### 處理 API 重試

當 API 請求因可重試的錯誤而失敗時，Claude Code 在重試前發出 `system/api_retry` 事件。在 v2.1.246 或更新版本上，當 `401` 或 `403` 拒絕 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 認證時，Claude Code 無聲地進行前兩次重試，沒有事件，然後從第三次連續重試開始照常發出事件。無聲重試仍計入 `attempt`。您可以使用該事件在自己的介面中顯示重試進度。

| 欄位             | 類型          | 說明                                                                                                                                                                                                                                                                                                   |
| ---------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`           | `"system"`    | 訊息類型                                                                                                                                                                                                                                                                                               |
| `subtype`        | `"api_retry"` | 將此識別為重試事件                                                                                                                                                                                                                                                                                     |
| `attempt`        | 整數          | 目前嘗試次數，從 1 開始                                                                                                                                                                                                                                                                                |
| `max_retries`    | 整數          | 此失敗原因允許的總重試次數，可能少於工作階段範圍的預算                                                                                                                                                                                                                                                 |
| `retry_delay_ms` | 整數          | 下次嘗試前的毫秒數                                                                                                                                                                                                                                                                                     |
| `error_status`   | 整數或 null   | 失敗嘗試的 HTTP 狀態碼，或當嘗試未從 API 獲得 HTTP 回應時為 `null`                                                                                                                                                                                                                                     |
| `no_response`    | 物件，選用    | 僅當失敗的嘗試[未及時獲得回應標頭](https://code.claude.com/docs/zh-TW/errors#no-response-from-api)時出現。`waited_ms` 是該嘗試等待的時間，`retry_wait_ms` 是重試將等待的時間。在這些事件中，`max_retries` 反映此原因通常獲得的一次重試，而不是工作階段範圍的預算。需要 Claude Code v2.1.261 或更新版本 |
| `error`          | 字串          | 錯誤類別：`authentication_failed`、`oauth_org_not_allowed`、`account_on_hold`、`billing_error`、`rate_limit`、`overloaded`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens`、`cloud_credential_error` 或 `unknown`                                                           |
| `uuid`           | 字串          | 唯一事件識別碼                                                                                                                                                                                                                                                                                         |
| `session_id`     | 字串          | 事件所屬的工作階段                                                                                                                                                                                                                                                                                     |

#### 讀取工作階段中繼資料

`system/init` 事件報告工作階段中繼資料，包括模型、工具、MCP 伺服器和載入的 plugins。除非啟動事件在其前面，否則它是串流中的第一個事件：

- `plugin_install` 事件，當設定 [`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](https://code.claude.com/docs/zh-TW/env-vars) 時。
- [`hook_started`、`hook_progress` 和 `hook_response` 事件](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkhookstartedmessage)，當配置的 [`SessionStart`](https://code.claude.com/docs/zh-TW/hooks#sessionstart) 或 [`Setup`](https://code.claude.com/docs/zh-TW/hooks#setup) hook 執行時。這些在 hook 產生時作為串流。Claude Code v2.1.169 至 v2.1.203 在 hook 完成後以一個批次傳遞它們，仍在 `system/init` 之前；v2.1.204 恢復了即時傳遞。

該事件還帶有一個選用的 `capabilities` 字串陣列，命名此 Claude Code 版本實現的協議行為，例如 `interrupt_receipt_v1` 或 `interrupt_cancel_queued_v1`。檢查它以進行功能偵測，而不是比較版本字串，並忽略您不認識的值。該欄位需要 Claude Code v2.1.205 或更新版本，在較早版本中不存在。有關功能清單，請參閱 [`SDKSystemMessage`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdksystemmessage)。

#### 當 plugin 或 MCP 伺服器未載入時使 CI 失敗

使用 `system/init` 事件中的 plugin 欄位來捕捉未載入的 plugin：

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 類型 | 說明                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `plugins`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 陣列 | 成功載入的 plugins，每個都有 `name` 和 `path`                                                                                                                                                                                                                                                                                                    |
| `plugin_errors`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 陣列 | plugin 載入時錯誤，每個都有 `plugin`、`type` 和 `message`。包括不滿足的依賴版本和 `--plugin-dir` 載入失敗，例如遺失的路徑或無效的存檔。受影響的 plugins 被降級並從 `plugins` 中移除。當沒有錯誤時，該鍵被省略                                                                                                                                    |
| 以相同方式使用 MCP 伺服器欄位。當您使用 `-p` 傳遞 [`--mcp-config`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 時，Claude Code 在執行第一個回合前等待仍在等待的伺服器，最多等待 [`MCP_TIMEOUT`](https://code.claude.com/docs/zh-TW/env-vars) 啟動逾時，預設為 30 秒。具有[快取工具清單](https://code.claude.com/docs/zh-TW/agent-sdk/mcp#connection-timing)的遠端伺服器跳過等待，在 `system/init` 中顯示 `pending`，並在其第一次工具呼叫時連接。等待需要 Claude Code v2.1.221 或更新版本。 Claude Code 在啟動時驗證每個 `--mcp-config` 項目，並跳過驗證失敗的項目，例如沒有 `type` 的 `url` 項目。執行繼續並乾淨地退出，因此檢查這些欄位以捕捉未載入的伺服器： |      |                                                                                                                                                                                                                                                                                                                                                  |
| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 類型 | 說明                                                                                                                                                                                                                                                                                                                                             |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | ---  | ---                                                                                                                                                                                                                                                                                                                                              |
| `mcp_servers`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 陣列 | 工作階段中的 MCP 伺服器，每個都有 `name` 和 `status`                                                                                                                                                                                                                                                                                             |
| `mcp_server_errors`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 陣列 | 由配置驗證跳過的 `--mcp-config` 項目，每個都有 `name`、`type` 和 `message`。`type` 是跳過類別，例如 `unknown_type`、`url_missing_type`、`invalid_config` 或 `reserved_name`；將您不認識的值視為通用跳過。受影響的伺服器從 `mcp_servers` 中移除。當沒有錯誤時，該鍵被省略，因此 CI 閘道可以在非空陣列上失敗。需要 Claude Code v2.1.219 或更新版本 |
| 當您在終端中手動執行命令時，Claude Code 也會向 stderr 列印啟動警告，例如 `Warning: 1 MCP server skipped due to invalid config:`，後面跟著每個跳過項目的原因。當您重新導向 stderr 或當 CI 執行器或 SDK 主機等程式捕捉它時，Claude Code 不列印警告，僅在 `mcp_server_errors` 欄位中報告跳過的項目。警告需要 Claude Code v2.1.219 或更新版本。                                                                                                                                                                                                                                                                                                                                    |      |                                                                                                                                                                                                                                                                                                                                                  |

#### 追蹤 plugin 安裝

當設定 [`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](https://code.claude.com/docs/zh-TW/env-vars) 時，Claude Code 在第一個回合前安裝 marketplace plugins 時發出 `system/plugin_install` 事件。使用這些在您自己的 UI 中顯示安裝進度。

| 欄位         | 類型                                                    | 說明                                                                                 |
| ------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `type`       | `"system"`                                              | 訊息類型                                                                             |
| `subtype`    | `"plugin_install"`                                      | 將此識別為 plugin 安裝事件                                                           |
| `status`     | `"started"`、`"installed"`、`"failed"` 或 `"completed"` | `started` 和 `completed` 括住整體安裝；`installed` 和 `failed` 報告個別 marketplaces |
| `name`       | 字串，選用                                              | marketplace 名稱，在 `installed` 和 `failed` 上出現                                  |
| `error`      | 字串，選用                                              | 失敗訊息，在 `failed` 上出現                                                         |
| `uuid`       | 字串                                                    | 唯一事件識別碼                                                                       |
| `session_id` | 字串                                                    | 事件所屬的工作階段                                                                   |

### 自動批准工具

使用 `--allowedTools` 讓 Claude 使用某些工具而無需提示。此範例執行測試套件並修復失敗，允許 Claude 執行 Bash 命令和讀取/編輯檔案而無需請求權限：

```
claude -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit"

```

若要為整個工作階段設定基準而不是列出個別工具，請傳遞[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。對於 `-p`，[內建啟動權限模式](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)在每個計畫上都是 Manual，因此傳遞您想要的權限模式：

- **`auto`**：傳遞`--permission-mode auto` 以讓分類器審查大多數操作，而不是您
- **`dontAsk`**：Claude Code 拒絕每個會提示的呼叫，這對鎖定的 CI 執行很有用。在 Manual 模式中不需要批准的操作仍會執行，例如在您的工作目錄中讀取檔案和[唯讀命令集](https://code.claude.com/docs/zh-TW/permissions#read-only-commands)，以及您的 `--allowedTools` 項目或 `permissions.allow` 規則涵蓋的操作。`AskUserQuestion`、connector 工具[您的組織設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 和標記為 [`requiresUserInteraction`](https://code.claude.com/docs/zh-TW/mcp#require-approval-for-a-specific-tool) 的 MCP 工具即使在允許規則匹配時也被拒絕
- **`acceptEdits`**：Claude 寫入檔案而無需提示，Claude Code 自動批准常見的檔案系統命令，例如`mkdir` 、`touch`、`mv` 和 `cp`。[沒有模式自動批准的操作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)仍然適用。除了唯讀命令集，其他 shell 命令和網路請求仍需要 `--allowedTools` 項目或 `permissions.allow` 規則。請參閱[`acceptEdits` 自動批准的內容](https://code.claude.com/docs/zh-TW/permission-modes#auto-approve-file-edits-with-acceptedits-mode)以取得完整清單

此範例使用 `acceptEdits` 作為基準應用 lint 修復：

```
claude -p "Apply the lint fixes" --permission-mode acceptEdits

```

### 在無人值守執行中關閉權限提示

當沒有人可用於回答權限提示時，傳遞 `--permission-prompts none`，例如在排程工作中。當您的執行有權限主機時，該旗標最重要：具有 [`canUseTool` 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/user-input)的 Agent SDK 應用程式，或您使用 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 傳遞的 MCP 工具。沒有該旗標，您的執行會等待該主機回答每個權限請求。 使用該旗標，您的執行不會查詢主機或等待它。任何會提示的內容都被拒絕，除非 `PermissionRequest` hook 允許它，Claude 被告知沒有人可以批准請求且不應重試它，執行繼續。在沒有主機的 `-p` 執行中，這些請求無論如何都被拒絕，該旗標也告知 Claude 不要重試它們。權限規則、[`PermissionRequest` hooks](https://code.claude.com/docs/zh-TW/hooks#permissionrequest) 和您設定的權限模式仍然首先決定每個呼叫；Claude Code 僅拒絕其他任何內容都無法解決的請求。 此範例在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)中執行無人值守的任務。分類器照常審查每個操作，Claude Code 拒絕任何會回退到提示的內容：

```
claude -p "Update the dependency pins and run the tests" --permission-mode auto --permission-prompts none

```

使用 `--permission-prompts none`，Claude Code 移除需要來自人員的答案的工具，例如 [`AskUserQuestion`](https://code.claude.com/docs/zh-TW/tools-reference#askuserquestion-tool-behavior)，因此 Claude 無法呼叫它們。任何沒有 [`Elicitation` hook](https://code.claude.com/docs/zh-TW/hooks#elicitation) 回答的 [MCP 引出請求](https://code.claude.com/docs/zh-TW/mcp#respond-to-mcp-elicitation-requests)都被取消。 使用 `--output-format stream-json`，拒絕顯示為 `permission_denied` 系統訊息，最終結果訊息在 `permission_denials` 中列出它們。 `--permission-prompts` 旗標需要 Claude Code v2.1.259 或更新版本。較早版本以未知選項錯誤拒絕它。

### 建立提交

此範例審查暫存的變更並建立具有適當訊息的提交：

```
claude -p "Look at my staged changes and create an appropriate commit" \
  --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"

```

`--allowedTools` 旗標使用[權限規則語法](https://code.claude.com/docs/zh-TW/settings-reference#permission-rule-syntax)。尾部的 ` *` 啟用前綴匹配，因此 `Bash(git diff *)` 允許任何以 `git diff` 開頭的命令。空格在 `*` 之前很重要：沒有它，`Bash(git diff*)` 也會匹配 `git diff-index`。 命令支援在 `-p` 模式中有所不同：

- 使用者調用的 [skills](https://code.claude.com/docs/zh-TW/skills) 和自訂命令有效。在提示字串中包含 `/skill-name`，Claude Code 在執行前展開它。
- 僅在終端介面中執行的內建命令，例如 `/login`，不可用。
- `/model`、`/effort`、`/fast`、`/color` 和 `/rename` 接受值作為引數，例如 `/model sonnet`，`/mcp` 不帶引數列印伺服器狀態的文字摘要。這些形式需要 Claude Code v2.1.205 或更新版本，並遵循每個命令的[可用性注意事項](https://code.claude.com/docs/zh-TW/commands#all-commands)。
- 若要變更設定，將 `key=value` 傳遞給 `/config`，例如 `/config thinking=false`。
- `/output-style <style>` 切換[輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)，`/output-style` 單獨列出它們。需要 Claude Code v2.1.269 或更新版本。

### 自訂系統提示

使用 `--append-system-prompt` 添加指示同時保持 Claude Code 的預設行為。此範例將 PR 差異傳輸到 Claude 並指示它審查安全漏洞。將其儲存為 shell 指令碼，例如 `review.sh`：

```
gh pr diff "$1" | claude -p \
  --append-system-prompt "You are a security engineer. Review for vulnerabilities." \
  --output-format json

```

在指令碼中，`"$1"` 代表您在命令列上傳遞的第一個引數。執行 `bash review.sh 123`，shell 將 `"$1"` 替換為 `123`，因此指令碼會擷取 PR 123 的差異。Claude Code 以 JSON 格式列印審查，文字在 `result` 欄位中。 有關更多選項，請參閱[系統提示旗標](https://code.claude.com/docs/zh-TW/cli-reference#system-prompt-flags)，包括 `--system-prompt` 以完全替換預設提示。

### 繼續對話

使用 `--continue` 繼續最近的對話，或使用 `--resume` 搭配工作階段 ID 繼續特定對話。在 Claude Code v2.1.257 或更新版本上，當您傳遞 `--continue` 時，Claude Code 開啟已完成但未仍在執行的[背景工作階段](https://code.claude.com/docs/zh-TW/sessions#resume-a-session)。此範例執行審查，然後傳送後續提示：

```
# First request
claude -p "Review this codebase for performance issues"

# Continue the most recent conversation
claude -p "Now focus on the database queries" --continue
claude -p "Generate a summary of all issues found" --continue

```

如果您執行多個對話，擷取工作階段 ID 以繼續特定對話：

```
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"

```

您可以從不同的目錄執行這兩個命令：Claude Code [按其 ID 找到工作階段](https://code.claude.com/docs/zh-TW/sessions#resume-a-session)在此機器上的任何專案中。在 v2.1.223 之前，Claude Code 僅在目前專案目錄及其 git worktrees 中尋找 ID，因此您必須從同一目錄執行兩個命令。 代替工作階段 ID，您可以將 `--resume` 傳遞工作階段的 `.jsonl` [文字記錄檔案](https://code.claude.com/docs/zh-TW/sessions#where-transcripts-are-stored)的絕對路徑，Claude Code 繼續儲存在該檔案中的對話。

## 後續步驟

- [Agent SDK 快速入門](https://code.claude.com/docs/zh-TW/agent-sdk/quickstart)：使用 Python 或 TypeScript 建立您的第一個 agent
- [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference)：所有 CLI 旗標和選項
- [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions)：在 GitHub 工作流程中使用 Agent SDK
- [GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd)：在 GitLab 管道中使用 Agent SDK

是否 助手
