Hooks 是回調函數，在代理事件發生時執行您的程式碼，例如工具被呼叫、會話啟動或執行停止。使用 hooks，您可以：

- **阻止危險操作** 在執行前，例如破壞性的 shell 命令或未授權的檔案存取
- **記錄和審計** 每個工具呼叫以進行合規性、除錯或分析
- **轉換輸入和輸出** 以清理資料、注入認證或重定向檔案路徑
- **要求人工批准** 敏感操作，例如資料庫寫入或 API 呼叫
- **追蹤會話生命週期** 以管理狀態、清理資源或傳送通知

## Hooks 如何工作

1 事件觸發 代理執行期間發生某事，SDK 觸發事件：工具即將被呼叫（`PreToolUse`）、工具返回結果（`PostToolUse`）、子代理啟動或停止、代理空閒或執行完成。請參閱[完整事件列表](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#available-hooks)。 2 SDK 收集已註冊的 hooks SDK 檢查為該事件類型註冊的 hooks。這包括您在 `options.hooks` 中傳遞的回調 hooks 和來自設定檔案的 shell 命令 hooks，當相應的 [`settingSources`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#settingsource) 或 [`setting_sources`](https://code.claude.com/docs/zh-TW/agent-sdk/python#settingsource) 項目啟用時（預設 `query()` 選項就是這樣）。 3 匹配器篩選哪些 hooks 執行 如果 hook 有 [`matcher`](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#matchers) 模式（例如 `"Write|Edit"`），SDK 會針對事件的目標（例如工具名稱）測試它。沒有匹配器的 hooks 會針對該類型的每個事件執行。 4 回調函數執行 每個匹配的 hook 的[回調函數](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#callback-functions)接收有關正在發生的事情的輸入：工具名稱、其參數、會話 ID 和其他事件特定的詳細資訊。 5 您的回調返回決定 執行任何操作（記錄、API 呼叫、驗證）後，您的回調返回[輸出物件](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#outputs)，告訴代理該做什麼：允許操作、阻止它、修改輸入或將上下文注入對話。 以下範例將這些步驟組合在一起。它註冊一個 `PreToolUse` hook（步驟 1），帶有 `"Write|Edit"` 匹配器（步驟 3），因此回調只針對檔案寫入工具觸發。觸發時，回調接收工具的輸入（步驟 4），檢查檔案路徑是否針對 `.env` 檔案，並返回 `permissionDecision: "deny"` 以阻止操作（步驟 5）： Python TypeScript

```
import asyncio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
)


# 定義一個接收工具呼叫詳細資訊的 hook 回調
async def protect_env_files(input_data, tool_use_id, context):
    # 從工具的輸入參數中提取檔案路徑
    file_path = input_data["tool_input"].get("file_path", "")
    file_name = file_path.split("/")[-1]

    # 如果針對 .env 檔案，阻止操作
    if file_name == ".env":
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }

    # 返回空物件以允許操作
    return {}


async def main():
    options = ClaudeAgentOptions(
        hooks={
            # 為 PreToolUse 事件註冊 hook
            # 匹配器篩選為僅 Write 和 Edit 工具呼叫
            "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]
        }
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("建立一個 .env 檔案，包含標準本地開發資料庫設定")
        async for message in client.receive_response():
            # 篩選助手和結果訊息
            if isinstance(message, (AssistantMessage, ResultMessage)):
                print(message)


asyncio.run(main())

```

```
import { query, HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

// 使用 HookCallback 類型定義 hook 回調
const protectEnvFiles: HookCallback = async (input, toolUseID, { signal }) => {
  // 將輸入轉換為特定 hook 類型以確保類型安全
  const preInput = input as PreToolUseHookInput;

  // 轉換 tool_input 以存取其屬性（在 SDK 中類型為 unknown）
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;
  const fileName = filePath?.split("/").pop();

  // 如果針對 .env 檔案，阻止操作
  if (fileName === ".env") {
    return {
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "deny",
        permissionDecisionReason: "Cannot modify .env files"
      }
    };
  }

  // 返回空物件以允許操作
  return {};
};

for await (const message of query({
  prompt: "建立一個 .env 檔案，包含標準本地開發資料庫設定",
  options: {
    hooks: {
      // 為 PreToolUse 事件註冊 hook
      // 匹配器篩選為僅 Write 和 Edit 工具呼叫
      PreToolUse: [{ matcher: "Write|Edit", hooks: [protectEnvFiles] }]
    }
  }
})) {
  // 篩選助手和結果訊息
  if (message.type === "assistant" || message.type === "result") {
    console.log(message);
  }
}

```

當您執行任一指令碼時，Claude 嘗試建立 `.env` 檔案，hook 拒絕工具呼叫，Claude 的最終回應說明它無法建立 `.env` 檔案。

## 可用的 hooks

SDK 為代理執行的不同階段提供 hooks。某些 hooks 在兩個 SDK 中都可用，而其他則僅限 TypeScript。

| Hook 事件                                                                             | Python SDK | TypeScript SDK | 觸發條件                                                                                  | 使用案例範例                                                                                                                                                         |
| ------------------------------------------------------------------------------------- | ---------- | -------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PreToolUse`                                                                          | 是         | 是             | 工具呼叫請求（可以阻止或修改）                                                            | 阻止危險的 shell 命令                                                                                                                                                |
| `PostToolUse`                                                                         | 是         | 是             | 工具執行結果                                                                              | 將所有檔案變更記錄到審計追蹤                                                                                                                                         |
| `PostToolUseFailure`                                                                  | 是         | 是             | 工具執行失敗                                                                              | 處理或記錄工具錯誤                                                                                                                                                   |
| `PostToolBatch`                                                                       | 否         | 是             | 一整批工具呼叫解決，每批一次，在下一個模型呼叫之前                                        | 為整個批次注入約定                                                                                                                                                   |
| `UserPromptSubmit`                                                                    | 是         | 是             | 使用者提示提交                                                                            | 將額外上下文注入提示                                                                                                                                                 |
| [`UserPromptExpansion`](https://code.claude.com/docs/zh-TW/hooks#userpromptexpansion) | 否         | 是             | 使用者輸入的命令或 MCP 提示在到達 Claude 之前擴展為提示。當 Claude 自己呼叫技能時不會觸發 | 阻止命令直接呼叫或在輸入技能時新增上下文                                                                                                                             |
| `MessageDisplay`                                                                      | 否         | 是             | 助手訊息包含文字完成，每則訊息一次，包含完整訊息文字                                      | 編輯或重新格式化顯示的文字，不改變記錄                                                                                                                               |
| `Stop`                                                                                | 是         | 是             | 代理執行停止                                                                              | 在退出前保存會話狀態                                                                                                                                                 |
| `StopFailure`                                                                         | 否         | 是             | 回合以 API 錯誤結束，而不是正常停止                                                       | 記錄失敗或傳送警示                                                                                                                                                   |
| `SubagentStart`                                                                       | 是         | 是             | 子代理初始化                                                                              | 追蹤平行任務生成                                                                                                                                                     |
| `SubagentStop`                                                                        | 是         | 是             | 子代理完成                                                                                | 聚合來自平行任務的結果                                                                                                                                               |
| `PreCompact`                                                                          | 是         | 是             | 對話壓縮請求                                                                              | 在摘要前存檔完整記錄                                                                                                                                                 |
| `PostCompact`                                                                         | 否         | 是             | 對話壓縮完成                                                                              | 記錄生成的摘要                                                                                                                                                       |
| [`PreModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#premodelswitch)           | 否         | 是             | 請求的模型切換，在發生之前（可以阻止）                                                    | 阻止切換到特定模型                                                                                                                                                   |
| [`PostModelSwitch`](https://code.claude.com/docs/zh-TW/hooks#postmodelswitch)         | 否         | 是             | 會話的模型變更，包括自動回退                                                              | 為新模型提供 Claude 模型特定的指導                                                                                                                                   |
| `PermissionRequest`                                                                   | 是         | 是             | 工具呼叫需要權限決定                                                                      | 自訂權限處理                                                                                                                                                         |
| `PermissionDenied`                                                                    | 否         | 是             | 自動模式拒絕工具呼叫，包括沒有分類器判決的拒絕                                            | 記錄拒絕，或告訴模型它可能重試；Claude Code 對沒有判決的拒絕忽略 `retry: true`。請參閱 [PermissionDenied](https://code.claude.com/docs/zh-TW/hooks#permissiondenied) |
| `SessionStart`                                                                        | 否         | 是             | 會話初始化                                                                                | 初始化記錄和遙測                                                                                                                                                     |
| `SessionEnd`                                                                          | 否         | 是             | 會話終止                                                                                  | 清理臨時資源                                                                                                                                                         |
| `Notification`                                                                        | 是         | 是             | 代理狀態訊息                                                                              | 將代理狀態更新傳送到 Slack 或 PagerDuty                                                                                                                              |
| `Setup`                                                                               | 否         | 是             | 會話設定/維護                                                                             | 執行初始化任務                                                                                                                                                       |
| `TeammateIdle`                                                                        | 否         | 是             | 隊友變為空閒                                                                              | 重新分配工作或通知                                                                                                                                                   |
| `TaskCreated`                                                                         | 否         | 是             | 透過 `TaskCreate` 工具建立任務                                                            | 強制執行任務命名約定                                                                                                                                                 |
| [`TaskCompleted`](https://code.claude.com/docs/zh-TW/hooks#taskcompleted)             | 否         | 是             | 任務標記為已完成                                                                          | 在任務關閉前要求通過測試                                                                                                                                             |
| `Elicitation`                                                                         | 否         | 是             | MCP 伺服器在任務中途請求使用者輸入                                                        | 以程式設計方式回應 MCP 輸入請求                                                                                                                                      |
| `ElicitationResult`                                                                   | 否         | 是             | 使用者回應 MCP 引出                                                                       | 在回應返回伺服器之前修改或阻止回應                                                                                                                                   |
| `ConfigChange`                                                                        | 否         | 是             | 設定檔案變更                                                                              | 動態重新載入設定                                                                                                                                                     |
| `InstructionsLoaded`                                                                  | 否         | 是             | `CLAUDE.md` 或規則檔案載入到上下文中                                                      | 審計哪些指令檔案載入                                                                                                                                                 |
| `WorktreeCreate`                                                                      | 否         | 是             | Git worktree 已建立                                                                       | 追蹤隔離的工作區                                                                                                                                                     |
| `WorktreeRemove`                                                                      | 否         | 是             | Git worktree 已移除                                                                       | 清理工作區資源                                                                                                                                                       |
| `CwdChanged`                                                                          | 否         | 是             | 會話期間工作目錄變更                                                                      | 按目錄重新載入環境變數                                                                                                                                               |
| `FileChanged`                                                                         | 否         | 是             | 監視的檔案被修改、建立或刪除                                                              | 當專案檔案變更時重新載入設定                                                                                                                                         |
| `DirectoryAdded`                                                                      | 否         | 是             | 會話期間新增工作目錄                                                                      | 為中途新增的儲存庫安裝相依性                                                                                                                                         |

## 配置 hooks

要配置 hook，請在代理選項的 `hooks` 欄位中傳遞它（Python 中的 `ClaudeAgentOptions`，TypeScript 中的 `options` 物件）。此程式碼片段假設您已經定義了 hook 回調，例如上面範例中 Python 的 `protect_env_files` 或 TypeScript 的 `protectEnvFiles`： Python TypeScript

```
options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_callback])]}
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Your prompt")
    async for message in client.receive_response():
        print(message)

```

```
for await (const message of query({
  prompt: "Your prompt",
  options: {
    hooks: {
      PreToolUse: [{ matcher: "Bash", hooks: [myCallback] }]
    }
  }
})) {
  console.log(message);
}

```

`hooks` 選項是一個字典（Python）或物件（TypeScript），其中：

- **鍵** ：[hook 事件名稱](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#available-hooks)，例如 `'PreToolUse'`、`'PostToolUse'` 和 `'Stop'`
- **值** ：[匹配器](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#matchers)的陣列，每個都包含可選的篩選模式和您的[回調函數](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#callback-functions)

### 匹配器

使用匹配器篩選您的回調何時觸發。`matcher` 欄位根據 hook 事件類型匹配不同的值。例如，工具型 hooks 匹配工具名稱，而 `Notification` hooks 匹配通知類型。 SDK 匹配器遵循與[設定檔案中的匹配器](https://code.claude.com/docs/zh-TW/hooks#matcher-patterns)相同的規則。該部分記錄了精確字串和正規表達式評估路徑、其版本要求，以及每個事件類型的匹配器值。

| 選項                                                                                                                                                                          | 類型             | 預設值      | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `matcher`                                                                                                                                                                     | `string`         | `undefined` | 針對事件的篩選欄位匹配的模式，遵循[設定檔案中匹配器的規則](https://code.claude.com/docs/zh-TW/hooks#matcher-patterns)。對於工具 hooks，這是工具名稱。內建工具包括 `Bash`、`Read`、`Write`、`Edit`、`Glob`、`Grep`、`WebFetch`、`Agent` 等（請參閱[工具輸入類型](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#tool-input-types)以取得完整列表）。MCP 工具使用模式 `mcp__<server>__<action>`，其中 `<server>` 是您在 `mcpServers` 配置中使用的鍵。 |
| `hooks`                                                                                                                                                                       | `HookCallback[]` | -           | 必需。當模式匹配時執行的回調函數陣列                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `timeout`                                                                                                                                                                     | `number`         | `undefined` | 超時時間（秒）。省略時，Claude Code 會應用[事件的預設超時](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#hook-timeout)。您的 SDK 回調遵循 `command` hook 預設值                                                                                                                                                                                                                                                                                        |
| 盡可能使用 `matcher` 模式來針對特定工具。帶有 `'Bash'` 的匹配器只針對 Bash 命令執行，而省略模式會針對事件的每次出現執行您的回調。故意省略它以記錄您的會話進行的每個工具呼叫。 |                  |             |                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

### 回調函數

#### 輸入

每個 hook 回調接收三個參數：

- **輸入資料：** 一個包含事件詳細資訊的類型物件。每個 hook 類型都有自己的輸入形狀。例如，`PreToolUseHookInput` 包括 `tool_name` 和 `tool_input`，而 `NotificationHookInput` 包括 `message`。請參閱 [TypeScript](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#hookinput) 和 [Python](https://code.claude.com/docs/zh-TW/agent-sdk/python#hookinput) SDK 參考中的完整類型定義。
  - 所有 hook 輸入共享 `session_id`、`cwd` 和 `hook_event_name`。
  - 當 hook 在子代理內觸發時，`agent_id` 和 `agent_type` 會被填充。在 TypeScript 中，這些在基本 hook 輸入上，可供所有 hook 類型使用。在 Python 中，它們是 `PreToolUse`、`PostToolUse`、`PostToolUseFailure` 和 `PermissionRequest` 上的可選欄位，以及 `SubagentStart` 和 `SubagentStop` 上的必需欄位。
- **工具使用 ID** （`str | None` / `string | undefined`）：關聯同一工具呼叫的 `PreToolUse` 和 `PostToolUse` 事件。
- **上下文：** 在 TypeScript 中，包含用於取消的 `signal` 屬性（`AbortSignal`）。在 Python 中，此參數保留供將來使用。

#### 輸出

您的回調返回一個具有兩類欄位的物件：

- **頂級欄位** 在每個事件上被接受：`systemMessage` 向使用者顯示訊息，`continue`（Python 中的 `continue_`）決定此 hook 後代理是否繼續執行。某些事件會捨棄它們或將它們傳遞到其他地方。每個[事件的部分](https://code.claude.com/docs/zh-TW/hooks#hook-events)在 hooks 頁面上說明它們的位置。
- \*\*`hookSpecificOutput`\*\*控制目前操作。內部的欄位取決於 hook 事件類型：
  - 對於 `PreToolUse` hooks，這是您設定 `permissionDecision`（`"allow"`、`"deny"`、`"ask"` 或 `"defer"`）、`permissionDecisionReason` 和 `updatedInput` 的地方。如果您返回 `"defer"`，查詢會結束，以便您可以[稍後繼續](https://code.claude.com/docs/zh-TW/hooks#defer-a-tool-call-for-later)。
  - 對於 `PostToolUse` hooks，您可以設定 `additionalContext` 以將資訊附加到工具結果。要在 Claude 看到之前替換工具的輸出，請設定 `updatedToolOutput`，這適用於兩個 SDK 中的任何工具。較舊的 `updatedMCPToolOutput` 欄位僅替換 MCP 工具輸出，已被棄用。
  - 在 TypeScript SDK 中，`PostToolUse` 回調也可以返回 `classifierContext`，這是關於工具呼叫結果的簡短說明，用於[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)權限分類器。因為您的回調在您應用程式自己的程序中執行，分類器可能會將您在說明中轉達的使用者陳述視為使用者意圖。該欄位需要 TypeScript Agent SDK v0.3.236 或更新版本。[為自動模式分類器註解結果](https://code.claude.com/docs/zh-TW/hooks#annotate-a-result-for-the-auto-mode-classifier)涵蓋長度上限、僅同步規則，以及不要在說明中放入的內容。

返回 `{}` 以允許操作而不進行變更。SDK 回調 hooks 使用與 [Claude Code shell 命令 hooks](https://code.claude.com/docs/zh-TW/hooks#json-output) 相同的 JSON 輸出格式，其記錄每個欄位和事件特定選項。對於 SDK 類型定義，請參閱 [TypeScript](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#synchookjsonoutput) 和 [Python](https://code.claude.com/docs/zh-TW/agent-sdk/python#synchookjsonoutput) SDK 參考。 當多個 hooks 或權限規則適用時，`deny` 優先於 `defer`，`defer` 優先於 `ask`，`ask` 優先於 `allow`。如果任何 hook 返回 `deny`，操作將被阻止，無論其他 hooks 如何。

#### 非同步輸出

預設情況下，代理在您的 hook 返回前等待。如果您的 hook 執行副作用，例如記錄或傳送 webhook，並且不需要影響代理的行為，您可以改為返回非同步輸出。這告訴代理立即繼續，無需等待 hook 完成。在此程式碼片段中，Python 中的 `send_to_logging_service` 和 TypeScript 中的 `sendToLoggingService` 代表您定義的任何記錄函數： Python TypeScript

```
async def async_hook(input_data, tool_use_id, context):
    # 啟動背景任務，然後立即返回
    asyncio.create_task(send_to_logging_service(input_data))
    return {"async_": True, "asyncTimeout": 30000}

```

```
const asyncHook: HookCallback = async (input, toolUseID, { signal }) => {
  // 啟動背景任務，然後立即返回
  sendToLoggingService(input).catch(console.error);
  return { async: true, asyncTimeout: 30000 };
};

```

| 欄位                                                                                                     | 類型     | 描述                                                                                 |
| -------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------ |
| `async`                                                                                                  | `true`   | 表示非同步模式。代理無需等待即可繼續。在 Python 中，使用 `async_` 以避免保留關鍵字。 |
| `asyncTimeout`                                                                                           | `number` | 背景操作的可選超時時間（毫秒）                                                       |
| 非同步輸出無法阻止、修改或將上下文注入操作，因為代理已經繼續。僅將它們用於副作用，例如記錄、指標或通知。 |          |                                                                                      |

## 範例

本節中的幾個範例僅顯示回調函數。若要執行其中一個，請在您的選項的 `hooks` 欄位中的匹配事件下註冊回調，如 [設定 hooks](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#configure-hooks) 中所示。

### 修改工具輸入

此範例攔截 Write 工具呼叫並重寫 `file_path` 參數以預先加上 `/sandbox`，將所有檔案寫入重定向到沙箱目錄。回調返回帶有修改路徑的 `updatedInput` 和 `permissionDecision: 'allow'` 以自動批准重寫的操作： Python TypeScript

```
async def redirect_to_sandbox(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    if input_data["tool_name"] == "Write":
        original_path = input_data["tool_input"].get("file_path", "")
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "updatedInput": {
                    **input_data["tool_input"],
                    "file_path": f"/sandbox{original_path}",
                },
            }
        }
    return {}

```

```
const redirectToSandbox: HookCallback = async (input, toolUseID, { signal }) => {
  if (input.hook_event_name !== "PreToolUse") return {};

  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  if (preInput.tool_name === "Write") {
    const originalPath = toolInput.file_path as string;
    return {
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "allow",
        updatedInput: {
          ...toolInput,
          file_path: `/sandbox${originalPath}`
        }
      }
    };
  }
  return {};
};

```

將 `updatedInput` 與 `permissionDecision: 'allow'` 配對以自動批准修改的輸入，或使用 `permissionDecision: 'ask'` 以將其顯示給使用者。如果您省略 `permissionDecision`，修改的輸入仍然適用並流經正常的權限評估。使用 `'defer'` 時，`updatedInput` 會被忽略。始終返回新物件，而不是改變原始 `tool_input`。 若要確認重定向，請將前綴設定為您可以寫入的路徑，例如 `./sandbox` 或 `/tmp/sandbox`（macOS 不允許建立根層級的 `/sandbox` 目錄），然後要求代理寫入檔案：Write 工具在訊息流中的結果會顯示帶有您的沙箱前綴的路徑，而不是 Claude 要求的路徑。

### 新增上下文並阻止工具

此範例阻止寫入 `/etc` 目錄並向模型和使用者解釋原因：

- `permissionDecision: 'deny'` 停止工具呼叫。
- `permissionDecisionReason` 告訴模型原因，以便它避免重試。
- `systemMessage` 向使用者顯示發生了什麼。

Python TypeScript

```
async def block_etc_writes(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")

    if file_path.startswith("/etc"):
        return {
            # 頂級欄位：顯示給使用者的訊息
            "systemMessage": "Remember: system directories like /etc are protected.",
            # hookSpecificOutput：阻止操作
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Writing to /etc is not allowed",
            },
        }
    return {}

```

```
const blockEtcWrites: HookCallback = async (input, toolUseID, { signal }) => {
  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;

  if (filePath?.startsWith("/etc")) {
    return {
      // 頂級欄位：顯示給使用者的訊息
      systemMessage: "Remember: system directories like /etc are protected.",
      // hookSpecificOutput：阻止操作
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "deny",
        permissionDecisionReason: "Writing to /etc is not allowed"
      }
    };
  }
  return {};
};

```

### 自動批准特定工具

預設情況下，代理可能在使用某些工具前提示權限。此範例通過返回 `permissionDecision: 'allow'` 自動批准唯讀檔案系統工具（Read、Glob、Grep），讓它們無需使用者確認即可執行，同時讓所有其他工具受到正常權限檢查： Python TypeScript

```
async def auto_approve_read_only(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    read_only_tools = ["Read", "Glob", "Grep"]
    if input_data["tool_name"] in read_only_tools:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "permissionDecisionReason": "Read-only tool auto-approved",
            }
        }
    return {}

```

```
const autoApproveReadOnly: HookCallback = async (input, toolUseID, { signal }) => {
  if (input.hook_event_name !== "PreToolUse") return {};

  const preInput = input as PreToolUseHookInput;
  const readOnlyTools = ["Read", "Glob", "Grep"];
  if (readOnlyTools.includes(preInput.tool_name)) {
    return {
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "allow",
        permissionDecisionReason: "Read-only tool auto-approved"
      }
    };
  }
  return {};
};

```

### 註冊多個 hooks

當事件觸發時，所有匹配的 hooks 並行執行。對於權限決定，最嚴格的結果獲勝：單個 `deny` 會阻止工具呼叫，無論其他 hooks 返回什麼。由於完成順序是不確定的，請編寫每個 hook 以獨立行動，而不是依賴另一個 hook 已執行。 下面的範例為每個工具呼叫註冊三個獨立檢查： Python TypeScript

```
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[authorization_check]),
            HookMatcher(hooks=[input_validator]),
            HookMatcher(hooks=[audit_logger]),
        ]
    }
)

```

```
const options = {
  hooks: {
    PreToolUse: [
      { hooks: [authorizationCheck] },
      { hooks: [inputValidator] },
      { hooks: [auditLogger] }
    ]
  }
};

```

### 使用多工具匹配器篩選

使用多工具匹配器在相關工具間共享一個回調。此範例註冊三個具有不同範圍的匹配器：

- 管道分隔的精確列表（`Write|Edit|NotebookEdit`）僅針對檔案修改工具觸發 `file_security_hook`。
- 正規表達式（`^mcp__`）針對任何名稱以 `mcp__` 開頭的 MCP 工具觸發 `mcp_audit_hook`。
- 省略的匹配器針對每個工具呼叫（無論名稱如何）觸發 `global_logger`。

Python TypeScript

```
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            # 匹配檔案修改工具
            HookMatcher(matcher="Write|Edit|NotebookEdit", hooks=[file_security_hook]),
            # 匹配所有 MCP 工具
            HookMatcher(matcher="^mcp__", hooks=[mcp_audit_hook]),
            # 匹配所有內容（無匹配器）
            HookMatcher(hooks=[global_logger]),
        ]
    }
)

```

```
const options = {
  hooks: {
    PreToolUse: [
      // 匹配檔案修改工具
      { matcher: "Write|Edit|NotebookEdit", hooks: [fileSecurityHook] },

      // 匹配所有 MCP 工具
      { matcher: "^mcp__", hooks: [mcpAuditHook] },

      // 匹配所有內容（無匹配器）
      { hooks: [globalLogger] }
    ]
  }
};

```

### 追蹤子代理活動

使用 `SubagentStop` hooks 監控子代理何時完成其工作。請參閱 [TypeScript](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#hookinput) 和 [Python](https://code.claude.com/docs/zh-TW/agent-sdk/python#hookinput) SDK 參考中的完整輸入類型。此範例在每次子代理完成時記錄摘要： Python TypeScript

```
async def subagent_tracker(input_data, tool_use_id, context):
    # 子代理完成時記錄子代理詳細資訊
    print(f"[SUBAGENT] Completed: {input_data['agent_id']}")
    print(f"  Transcript: {input_data['agent_transcript_path']}")
    print(f"  Tool use ID: {tool_use_id}")
    print(f"  Stop hook active: {input_data.get('stop_hook_active')}")
    return {}


options = ClaudeAgentOptions(
    hooks={"SubagentStop": [HookMatcher(hooks=[subagent_tracker])]}
)

```

```
import { HookCallback, SubagentStopHookInput } from "@anthropic-ai/claude-agent-sdk";

const subagentTracker: HookCallback = async (input, toolUseID, { signal }) => {
  // 轉換為 SubagentStopHookInput 以存取子代理特定欄位
  const subInput = input as SubagentStopHookInput;

  // 子代理完成時記錄子代理詳細資訊
  console.log(`[SUBAGENT] Completed: ${subInput.agent_id}`);
  console.log(`  Transcript: ${subInput.agent_transcript_path}`);
  console.log(`  Tool use ID: ${toolUseID}`);
  console.log(`  Stop hook active: ${subInput.stop_hook_active}`);
  return {};
};

const options = {
  hooks: {
    SubagentStop: [{ hooks: [subagentTracker] }]
  }
};

```

### 從 hooks 發出 HTTP 請求

Hooks 可以執行非同步操作，例如 HTTP 請求。在您的 hook 內捕捉錯誤，而不是讓它們傳播。 此範例在每個工具完成後傳送 webhook，記錄哪個工具執行以及何時執行。hook 捕捉來自失敗 webhook 的錯誤： Python TypeScript

```
import asyncio
import json
import urllib.request
from datetime import datetime


def _send_webhook(tool_name):
    """同步幫助程式，將工具使用資料 POST 到外部 webhook。"""
    data = json.dumps(
        {
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.example.com/webhook",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req)


async def webhook_notifier(input_data, tool_use_id, context):
    # 僅在工具完成後觸發（PostToolUse），而不是之前
    if input_data["hook_event_name"] != "PostToolUse":
        return {}

    try:
        # 在執行緒中執行阻止 HTTP 呼叫以避免阻止事件迴圈
        await asyncio.to_thread(_send_webhook, input_data["tool_name"])
    except Exception as e:
        # 記錄錯誤但不引發
        print(f"Webhook request failed: {e}")

    return {}

```

```
import { query, HookCallback, PostToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

const webhookNotifier: HookCallback = async (input, toolUseID, { signal }) => {
  // 僅在工具完成後觸發（PostToolUse），而不是之前
  if (input.hook_event_name !== "PostToolUse") return {};

  try {
    await fetch("https://api.example.com/webhook", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tool: (input as PostToolUseHookInput).tool_name,
        timestamp: new Date().toISOString()
      }),
      // 傳遞 signal 以便在 hook 超時時取消請求
      signal
    });
  } catch (error) {
    // 分別處理取消和其他錯誤
    if (error instanceof Error && error.name === "AbortError") {
      console.log("Webhook request cancelled");
    }
    // 不重新拋出
  }

  return {};
};

// 註冊為 PostToolUse hook
for await (const message of query({
  prompt: "Refactor the auth module",
  options: {
    hooks: {
      PostToolUse: [{ hooks: [webhookNotifier] }]
    }
  }
})) {
  console.log(message);
}

```

若要確認 hook 觸發，請將 webhook URL 指向您可以監視的端點並傳送使用工具的提示：hook 會在每個工具完成後傳送帶有工具名稱和時間戳記的 POST。

### 將通知轉發到 Slack

使用 `Notification` hooks 接收來自代理的系統通知並將其轉發到外部服務。在 SDK 工作階段中，Claude Code 為以下通知類型執行此 hook：

- [`permission_prompt`](https://code.claude.com/docs/zh-TW/hooks#notification) 一旦權限請求在您的 [`canUseTool` 回調](https://code.claude.com/docs/zh-TW/agent-sdk/user-input) 上等待約六秒。需要 TypeScript Agent SDK v0.3.233 或更新版本，或 Python Agent SDK v0.2.139 或更新版本
- `elicitation_complete` 和 `elicitation_response` 用於使用者提示引導流程

Claude Code 從 SDK 工作階段不執行的互動式 UI 發出其他類型，例如 `idle_prompt`、`auth_success` 和 `elicitation_dialog`。 每個通知都包括帶有人類可讀描述的 `message` 欄位，以及可選的 `title`。 此範例將每個通知轉發到 Slack 頻道。它需要 [Slack 傳入 webhook URL](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/)，您可以通過將應用程式新增到 Slack 工作區並啟用傳入 webhooks 來建立： Python TypeScript

```
import asyncio
import json
import urllib.request

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher


def _send_slack_notification(message):
    """同步幫助程式，通過傳入 webhook 將訊息傳送到 Slack。"""
    data = json.dumps({"text": f"Agent status: {message}"}).encode()
    req = urllib.request.Request(
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req)


async def notification_handler(input_data, tool_use_id, context):
    try:
        # 在執行緒中執行阻止 HTTP 呼叫以避免阻止事件迴圈
        await asyncio.to_thread(_send_slack_notification, input_data.get("message", ""))
    except Exception as e:
        print(f"Failed to send notification: {e}")

    # 返回空物件。通知 hooks 不修改代理行為
    return {}


async def main():
    options = ClaudeAgentOptions(
        hooks={
            # 為通知事件註冊 hook（不需要匹配器）
            "Notification": [HookMatcher(hooks=[notification_handler])],
        },
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Analyze this codebase")
        async for message in client.receive_response():
            print(message)


asyncio.run(main())

```

```
import { query, HookCallback, NotificationHookInput } from "@anthropic-ai/claude-agent-sdk";

// 定義一個將通知傳送到 Slack 的 hook 回調
const notificationHandler: HookCallback = async (input, toolUseID, { signal }) => {
  // 轉換為 NotificationHookInput 以存取訊息欄位
  const notification = input as NotificationHookInput;

  try {
    // POST 通知訊息到 Slack 傳入 webhook
    await fetch("https://hooks.slack.com/services/YOUR/WEBHOOK/URL", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: `Agent status: ${notification.message}`
      }),
      // 傳遞 signal 以便在 hook 超時時取消請求
      signal
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      console.log("Notification cancelled");
    } else {
      console.error("Failed to send notification:", error);
    }
  }

  // 返回空物件。通知 hooks 不修改代理行為
  return {};
};

// 為通知事件註冊 hook（不需要匹配器）
for await (const message of query({
  prompt: "Analyze this codebase",
  options: {
    hooks: {
      Notification: [{ hooks: [notificationHandler] }]
    }
  }
})) {
  console.log(message);
}

```

當 `Notification` 事件觸發時，hook 會將通知的 `message`（前綴為 `Agent status:`）發佈到您的 webhook 目標的頻道。

## 修復常見問題

### Hook 未觸發

- 驗證 hook 事件名稱正確且區分大小寫（`PreToolUse`，而不是 `preToolUse`）
- 檢查您的匹配器模式是否與工具名稱完全匹配
- 確保 hook 在 `options.hooks` 中的正確事件類型下
- 對於支援匹配器的非工具 hooks，如 `Notification` 和 `SubagentStop`，匹配器匹配不同的欄位，而 `Stop` 完全忽略匹配器（請參閱[匹配器模式](https://code.claude.com/docs/zh-TW/hooks#matcher-patterns)）
- 當代理達到 [`max_turns`](https://code.claude.com/docs/zh-TW/agent-sdk/python#claudeagentoptions) 限制時，hooks 可能不會觸發，因為會話在 hooks 可以執行前結束

### 匹配器未按預期篩選

匹配器只匹配工具名稱，不匹配檔案路徑或其他參數。要按檔案路徑篩選，請在您的 hook 內檢查 `tool_input.file_path`：

```
const myHook: HookCallback = async (input, toolUseID, { signal }) => {
  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;
  if (!filePath?.endsWith(".md")) return {}; // 跳過非 markdown 檔案
  // 處理 markdown 檔案...
  return {};
};

```

### Hook 超時

Claude Code 以超時時間執行每個回調，您可以在其 `HookMatcher` 上使用 `timeout` 欄位以秒為單位設定。當您未設定時，Claude Code 使用事件的預設值：大多數事件為 600 秒，`UserPromptSubmit`、`PreModelSwitch` 和 `PostModelSwitch` 為 30 秒，`MessageDisplay` 為 10 秒。Claude Code 在關閉期間執行 `SessionEnd` 回調，使用較短的 [SessionEnd 超時預算](https://code.claude.com/docs/zh-TW/hooks#sessionend-input)，預設為 1.5 秒。 當回調超過其超時時間時，Claude Code 取消它並捨棄其輸出，會話繼續而不是掛起。接下來發生的情況取決於事件：

- `PreToolUse`：Claude Code 不執行工具呼叫，Claude 收到工具結果，說明 hook 未在超時前回應，轉換繼續。如果另一個 `PreToolUse` hook 返回明確拒絕，Claude 改為收到該拒絕而不是超時錯誤。在 v2.1.210 之前，Claude Code 將超時報告給 Claude 作為使用者拒絕，這使無人值守會話停止並等待輸入。
- `PostToolUse` 和 `PostToolUseFailure`：Claude Code 保留工具結果，轉換繼續。
- `UserPromptSubmit` 和 [`UserPromptExpansion`](https://code.claude.com/docs/zh-TW/hooks#userpromptexpansion)：Claude Code 以命名 hook 和超時的訊息阻止提示，會話繼續。因為這些事件上的回調可以充當政策閘門，Claude Code 永遠不會讓超時的提示通過未篩選。在 v2.1.208 之前，當這些事件上的回調超時時，Claude Code 以 `error_during_execution` 結束查詢。
- `Stop` 和 `SubagentStop`：超時的回調計為不返回任何決定。代理或子代理停止，如同該回調已允許它，而您其他 hooks 在事件上的決定仍然適用。在 Claude Code v2.1.273 之前，超時的 `Stop` 或 `SubagentStop` 回調計為失敗的 hook 執行，Claude Code 捨棄您其他 hooks 在事件上的決定。
- `SessionStart`：超時的回調計為不返回任何輸出，會話繼續，使用您其他 `SessionStart` hooks 的輸出。
- `PreModelSwitch`：Claude Code 阻止模型切換。未回答的 hook 尚未批准切換。
- 其他事件，如 `Notification`、`PreCompact` 和 `PostModelSwitch`：Claude Code 記錄失敗並繼續。

主會話中 `Stop` 或 `SessionStart` 回調首次超時時，Claude Code 也會新增 [`SDKInformationalMessage`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkinformationalmessage) 到訊息流，說明驅動會話的應用程式未回應。稍後的超時在您的應用程式保持無回應時不會重複該訊息。 如果您在回調待處理時中斷查詢，Claude Code 取消待處理的工具呼叫。在 v2.1.208 之前，如果您在待處理的 `PreToolUse` 回調期間中斷，工具呼叫仍可能繼續進行。 如果您的回調需要更多時間，請在其 `HookMatcher` 上設定更高的 `timeout`。在 TypeScript 中，使用第三個回調參數中的 `AbortSignal` 以在超時觸發時優雅地處理取消。

### 工具意外被阻止

- 檢查所有 `PreToolUse` hooks 是否返回 `permissionDecision: 'deny'`
- 將記錄新增到您的 hooks 以查看它們返回的 `permissionDecisionReason`
- 驗證匹配器模式不會太寬泛：空匹配器匹配所有工具

### 修改的輸入未應用

- 確保 `updatedInput` 在 `hookSpecificOutput` 內，而不是在頂級：

```
return {
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "allow",
    updatedInput: { command: "new command" }
  }
};

```

- 不要將 `updatedInput` 與 `permissionDecision: 'defer'` 配對，這會捨棄修改的輸入。省略 `permissionDecision` 是可以的：修改的輸入仍通過正常權限評估應用。您也可以返回 `'allow'` 以自動批准修改的輸入或 `'ask'` 以向使用者顯示以供批准
- 在 `hookSpecificOutput` 中包括 `hookEventName` 以識別輸出適用於哪個 hook 類型

### Python 中不可用會話 hooks

`SessionStart` 和 `SessionEnd` 可以在 TypeScript 中註冊為 SDK 回調 hooks，但在 Python SDK 中不可用，因為其 `HookEvent` 類型省略它們。在 Python 中，它們僅作為[shell 命令 hooks](https://code.claude.com/docs/zh-TW/hooks#hook-events)在設定檔案中定義，例如 `.claude/settings.json`。要從您的 SDK 應用程式載入 shell 命令 hooks，請使用 [`setting_sources`](https://code.claude.com/docs/zh-TW/agent-sdk/python#settingsource) 或 [`settingSources`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#settingsource) 包括適當的設定來源： Python TypeScript

```
options = ClaudeAgentOptions(
    setting_sources=["project"],  # 載入 .claude/settings.json 包括 hooks
)

```

```
const options = {
  settingSources: ["project"] // 載入 .claude/settings.json 包括 hooks
};

```

要改為執行初始化邏輯作為 Python SDK 回調，請使用 `client.receive_response()` 的第一條訊息作為您的觸發器。

### 子代理權限提示倍增

生成多個子代理時，每個子代理可能會分別請求其自身工具呼叫的權限。要避免重複提示，請使用 `PreToolUse` hooks 自動批准特定工具，或配置權限規則，子代理[從父對話繼承](https://code.claude.com/docs/zh-TW/sub-agents#permission-modes)。

### 子代理的遞迴 hook 迴圈

生成子代理的 `UserPromptSubmit` hook 如果這些子代理觸發相同的 hook，可能會建立無限迴圈。要防止這種情況：

- 使用共享變數或會話狀態來追蹤您是否已在子代理內
- 將 hooks 範圍限制為僅針對頂級代理會話執行

### systemMessage 未出現在輸出中

`systemMessage` 欄位向使用者顯示訊息，而不是模型。在 Claude Code v2.1.227 或更新版本上，hook 的 `systemMessage` 可以在訊息流中呈現為 [`SDKInformationalMessage`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkinformationalmessage)。它是否呈現取決於事件。每個[事件的部分](https://code.claude.com/docs/zh-TW/hooks#hook-events)在 hooks 頁面上說明輸出如何呈現。要改為將上下文傳遞給模型，請返回 [`additionalContext`](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude)。 在 v2.1.227 之前，SDK 僅針對 `SessionStart` 和 `Setup` hooks 在訊息流中呈現 hook 輸出。對於任何其他事件，輸出僅出現在 [`includeHookEvents`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options)（Python 中的 `include_hook_events`）新增的生命週期事件中。該選項的條目涵蓋每個 hook 事件產生的生命週期事件。 如果您需要可靠地將 hook 決定呈現給您的應用程式，請分別記錄它們或使用專用輸出頻道。

## 相關資源

- [Claude Code hooks 參考](https://code.claude.com/docs/zh-TW/hooks)：完整的 JSON 輸入/輸出架構、事件文件和匹配器模式
- [Claude Code hooks 指南](https://code.claude.com/docs/zh-TW/hooks-guide)：shell 命令 hook 範例和逐步解說
- [TypeScript SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)：hook 類型、輸入/輸出定義和配置選項
- [Python SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/python)：hook 類型、輸入/輸出定義和配置選項
- [權限](https://code.claude.com/docs/zh-TW/agent-sdk/permissions)：控制您的代理可以做什麼
- [自訂工具](https://code.claude.com/docs/zh-TW/agent-sdk/custom-tools)：建立工具以擴展代理功能

是否 助手
