Claude Agent SDK 提供權限控制來管理 Claude 如何使用工具。使用權限模式和規則來定義自動允許的內容，以及使用 [`canUseTool` callback](https://code.claude.com/docs/zh-TW/agent-sdk/user-input) 來在執行時處理其他所有情況。

## 權限如何被評估

當 Claude 請求一個工具時，SDK 按照以下順序檢查權限： 1 Hooks 首先執行 [hooks](https://code.claude.com/docs/zh-TW/agent-sdk/hooks)。Hook 可以直接拒絕呼叫或將其傳遞下去。返回 `allow` 的 hook 不會跳過下面的拒絕和詢問規則；無論 hook 結果如何，這些規則都會被評估。`PreToolUse` hook allow 也無法批准針對 [關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths) 的 `rm` 或 `rmdir` 移除。 2 拒絕規則 檢查 `deny` 規則（來自 `disallowed_tools` 和 [settings.json](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings)）。如果拒絕規則匹配，工具會被阻止，即使在 `bypassPermissions` 模式下也是如此。裸名稱拒絕規則（如 `Bash`）會在此評估開始前將工具從 Claude 的上下文中移除，因此只有作用域規則（如 `Bash(rm *)`）會在此步驟中被檢查。 3 詢問規則 檢查來自 [settings.json](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings) 的 `ask` 規則。如果詢問規則匹配，呼叫會傳遞到您的 [`canUseTool` 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/user-input) 以進行確認，即使在 `bypassPermissions` 模式下也是如此。需要使用者互動的工具行為相同：`AskUserQuestion` 和 MCP 工具（其伺服器設定了 [`_meta["anthropic/requiresUserInteraction"]`](https://code.claude.com/docs/zh-TW/mcp#require-approval-for-a-specific-tool)）總是傳遞到回呼，即使當 allow 規則匹配時也是如此。在 `dontAsk` 模式下，兩種情況都會被拒絕，因為該模式永遠不會提示。MCP 註解需要 Claude Code v2.1.199 或更新版本。您的組織設定為 `ask` 的 [claude.ai connector](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 工具也會在此步驟離開流程。每個呼叫都會傳遞到回呼，即使在 `bypassPermissions` 模式下，即使當 allow 規則匹配時也是如此。回呼會收到原因 `Your organization requires approval for this tool`。在 `dontAsk` 模式下，呼叫會被拒絕，因為該模式永遠不會提示。 4 權限模式 應用活躍的 [權限模式](https://code.claude.com/docs/zh-TW/agent-sdk/permissions#permission-modes)：

- 在 `bypassPermissions` 模式下，Claude Code 批准到達此步驟的所有內容，除了針對 [關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths) 的 `rm` 和 `rmdir` 移除，這些會傳遞下去。
- 在 `acceptEdits` 模式下，Claude Code 批准 [接受編輯模式](https://code.claude.com/docs/zh-TW/agent-sdk/permissions#accept-edits-mode-acceptedits) 下列出的檔案操作。
- 在 `plan` 模式下，Claude Code 將檔案編輯和 shell 寫入工具發送到您的 `canUseTool` 回呼，無論 allow 規則如何，因此在規劃時寫入操作無法自動批准。
- 在其他模式下，請求會傳遞下去。

5 允許規則 檢查 `allow` 規則（來自 `allowed_tools` 和 settings.json）。如果規則匹配，工具會被批准。工具自行批准的呼叫也會在此步驟解決，無需規則：例如在您的工作目錄內的檔案讀取或 [唯讀 Bash 命令](https://code.claude.com/docs/zh-TW/permissions#read-only-commands)。針對 [關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths) 的 `rm` 和 `rmdir` 移除永遠不會被 allow 規則批准：它們在提示的模式下到達您的回呼，在 Claude Code v2.1.218 或更新版本的 `auto` 模式下進入 [分類器](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)，並在 `dontAsk` 模式下被拒絕。 6 canUseTool 回呼 如果上述任何步驟都未解決，請呼叫您的 [`canUseTool` 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/user-input) 以獲得決定。在 `dontAsk` 模式下，此步驟會被跳過，工具會被拒絕。在 TypeScript SDK 中，如果您設定了 [`permissionPrompts: 'none'`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options)，您的回呼在此步驟不會被呼叫。[`PermissionRequest` hook](https://code.claude.com/docs/zh-TW/hooks#permissionrequest) 仍然有機會決定，如果它不決定，Claude Code 會拒絕呼叫。此選項需要 Claude Code v2.1.259 或更新版本。

![六步權限評估流程的圖表，與上述步驟相符：工具請求通過 hooks、拒絕規則、詢問規則、權限模式、允許規則和 canUseTool。Hooks、拒絕規則和 canUseTool 可以路由到被阻止；權限模式繞過、允許規則和 canUseTool 可以路由到執行；詢問規則路由到 canUseTool。](https://mintcdn.com/claude-code/jYgs7qigNjO1Badj/images/agent-sdk/permissions-flow.svg?fit=max&auto=format&n=jYgs7qigNjO1Badj&q=85&s=c771ad9085b1277d3708027a49c744bc)

![六步權限評估流程的圖表，與上述步驟相符：工具請求通過 hooks、拒絕規則、詢問規則、權限模式、允許規則和 canUseTool。Hooks、拒絕規則和 canUseTool 可以路由到被阻止；權限模式繞過、允許規則和 canUseTool 可以路由到執行；詢問規則路由到 canUseTool。](https://mintcdn.com/claude-code/_xqph1dUOslCOwsj/images/agent-sdk/permissions-flow-dark.svg?fit=max&auto=format&n=_xqph1dUOslCOwsj&q=85&s=e53a91e9059cbf51852b7cedb4dd4251)
如果您在 TypeScript SDK 期望評估順序在諮詢回呼之前自動批准呼叫的設定中傳遞 `canUseTool` 回呼，SDK 會在構造查詢時發出一次 Node.js 程序警告。警告的代碼是 `CLAUDE_SDK_CAN_USE_TOOL_SHADOWED`。兩個設定會觸發它：

- `permissionMode: 'bypassPermissions'`，它自動批准到達權限模式步驟的每個呼叫，除了 [任何模式都不自動批准的操作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)
- 每個裸 `allowedTools` 條目，例如 `"Read"`，它在諮詢回呼之前自動批准整個工具，除了 [任何模式都不自動批准的操作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)

具有指定符的條目（如 `Bash(ls *)`）和 `acceptEdits` 模式不會觸發它，來自設定檔的 allow 規則對檢查不可見。 使用 `process.on('warning', ...)` 進行監聽並匹配代碼以記錄或抑制它。要無論模式和規則如何都控制每個工具呼叫，請改用 [`PreToolUse` hook](https://code.claude.com/docs/zh-TW/agent-sdk/hooks)。 此頁面重點關注 **allow 和 deny 規則** 以及 **權限模式** 。對於其他步驟：

- **Hooks：** 執行自訂程式碼以允許、拒絕或修改工具請求。請參閱 [使用 hooks 控制執行](https://code.claude.com/docs/zh-TW/agent-sdk/hooks)。
- **canUseTool 回呼：** 在執行時提示使用者批准，當沒有較早的步驟解決呼叫時。請參閱 [處理批准和使用者輸入](https://code.claude.com/docs/zh-TW/agent-sdk/user-input)。

## 允許和拒絕規則

`allowed_tools` 和 `disallowed_tools`（TypeScript：`allowedTools` / `disallowedTools`）在上述評估流程中新增允許和拒絕規則清單的項目。如果您在 `allowed_tools` 中命名其中一個[任務追蹤工具](https://code.claude.com/docs/zh-TW/agent-sdk/todo-tracking#model-availability)，Claude Code 也會選擇加入該工作階段。任何未列在 `allowed_tools` 中的其他工具仍可供 Claude 使用，對其進行的需要批准的呼叫會進入權限模式。拒絕規則的行為取決於它們是命名工具還是在工具內限定模式。

| 選項                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 效果                                                                                                                                                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `allowed_tools=["Read", "Grep"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | `Read` 和 `Grep` 會自動批准。此處未列出的其他工具仍然存在，對它們進行的需要批准的呼叫會進入權限模式和 `canUseTool`。                                                                                                 |
| `disallowed_tools=["Bash"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `Bash` 工具定義會從請求中移除。Claude 看不到該工具，無法嘗試使用它。                                                                                                                                                 |
| `disallowed_tools=["Bash(rm *)"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | `Bash` 保持可用。符合 `rm *` [如所寫](https://code.claude.com/docs/zh-TW/permissions#bash-rule-limits)的呼叫在每個權限模式中都會被拒絕，包括 `bypassPermissions`。其他 `Bash` 呼叫（包括 `/bin/rm`）會進入權限模式。 |
| `disallowed_tools=["*"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 每個工具定義都會從請求中移除。拒絕規則支援工具名稱萬用字元：`"*"` 符合每個工具，`"mcp__*"` 符合所有伺服器上的每個 MCP 工具。                                                                                         |
| 允許規則僅在字面 `mcp__<server>__` 前綴之後接受工具名稱萬用字元。伺服器段必須無萬用字元，以便規則命名您設定的特定伺服器：`mcp__puppeteer__*` 符合來自 `puppeteer` 伺服器的每個工具，`mcp__github__get_*` 符合其 `get_` 工具。未錨定的項目（如 `allowed_tools=["*"]` 或 `allowed_tools=["mcp__*"]`）會被忽略並顯示啟動警告，不會自動批准任何內容。 `Read` 和 `Edit` 的限定規則採用路徑模式。`Edit(path)` 規則管理所有寫入檔案的內建工具，包括 `Write` 和 `NotebookEdit`；`Write(path)` 規則永遠不會被檔案權限檢查符合。 使用 `//path` 表示絕對檔案系統路徑：`Edit(//secrets/**)` 的拒絕規則會阻止在磁碟上 `/secrets` 下任何位置的寫入。使用單個前導斜線時，`Edit(/secrets/**)` 會在規則的來源處錨定。對於透過 `allowed_tools` 或 `disallowed_tools` 傳遞的規則，這表示工作階段的工作目錄，因此規則不會阻止磁碟上的 `/secrets`。請參閱[讀取和編輯規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)以了解四種錨定形式以及來自設定檔的規則如何解析。                                                                                                                                                                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                      |
| **自動批准的工具永遠不會到達`canUseTool` 。** 在任何較早步驟中批准的工具呼叫，透過 `acceptEdits` 或 `bypassPermissions`，或透過允許規則，會跳過您的 `canUseTool` 回呼，因此您在那裡放置的權限檢查會被該工具無聲地繞過。`AskUserQuestion`、標記為 [`_meta["anthropic/requiresUserInteraction"]`](https://code.claude.com/docs/zh-TW/mcp#require-approval-for-a-specific-tool) 的 MCP 工具、連接器工具[您的組織設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools)，以及 `rm` 和 `rmdir` 移除針對[關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths)的移除仍會到達回呼，即使允許規則符合也是如此。在 `auto` 模式中，關鍵路徑移除會進入[分類器](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)而不是回呼，而上面列出的其他呼叫仍會到達它；分類器路由需要 Claude Code v2.1.218 或更新版本。在 `dontAsk` 模式中，這些呼叫會被拒絕，不會呼叫回呼。涵蓋範圍取決於項目的形式：像 `Read` 或 `mcp__github__get_issue` 這樣的裸名稱會自動批准對該工具的每個呼叫，除了上述例外情況，而像 `Bash(npm test *)` 這樣的限定規則只會自動批准符合的呼叫，其他需要批准的 `Bash` 呼叫仍會進入回呼。對於必須在每個工具呼叫上執行的檢查，請使用 [`PreToolUse` hook](https://code.claude.com/docs/zh-TW/agent-sdk/hooks)：hook 在每個其他步驟之前執行，hook 拒絕即使在 `bypassPermissions` 模式中也適用。 |                                                                                                                                                                                                                      |
| 對於鎖定的代理，將 `allowedTools` 與 `permissionMode: "dontAsk"` 配對：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                                                                                                                                                                                                                      |

```
const options = {
  allowedTools: ["Read", "Glob", "Grep"],
  permissionMode: "dontAsk"
};

```

列出的工具會被批准，除了[任何模式都不自動批准的動作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)，以及每個其他會提示的呼叫都會被拒絕。在 `default` 模式中不需要批准的呼叫會執行，無論您是否列出它們，例如[唯讀 Bash 命令](https://code.claude.com/docs/zh-TW/permissions#read-only-commands)、不在執行前詢問的工具（如 `Agent`），以及工作目錄內的檔案讀取。要將工具完全置於 Claude 的範圍之外，請將其裸名稱新增到 `disallowedTools`。 **`allowed_tools`不限制`bypassPermissions` 。** `allowed_tools` 預先批准您列出的工具。其他未列出的工具不符合任何允許規則，會進入權限模式，其中 `bypassPermissions` 會批准它們。將 `allowed_tools=["Read"]` 與 `permission_mode="bypassPermissions"` 一起設定仍會批准每個工具，包括 `Bash`、`Write` 和 `Edit`。如果您需要 `bypassPermissions` 但想要阻止特定工具，請使用 `disallowed_tools`。 您也可以在 `.claude/settings.json` 中以宣告方式設定允許、拒絕和詢問規則。當啟用 `project` 設定來源時會讀取這些規則，預設 `query()` 選項就是這樣。如果您明確設定 `setting_sources`（TypeScript：`settingSources`），請包含 `"project"` 以便它們適用。請參閱[權限設定](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings)以了解規則語法。

## 權限模式

權限模式提供對 Claude 如何使用工具的全域控制。您可以在呼叫 `query()` 時設定權限模式，或在串流工作階段期間動態變更它。

### 可用模式

SDK 支援這些權限模式：

| 模式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 說明             | 工具行為                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `default`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 標準權限行為     | 無模式型自動核准；需要核准且不符合任何允許規則的呼叫會觸發您的 `canUseTool` 回呼                                                                                                                                                                                                                                                                                                                                                                   |
| `dontAsk`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 拒絕而非提示     | 任何原本會提示的呼叫都會被拒絕。由 `allowed_tools` 或規則核准的呼叫會執行，在 `default` 模式中不需要核准的呼叫也會執行；您的組織[設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 的連接器工具和需要使用者互動的工具會被拒絕，即使您已預先核准它們，針對[關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths)的 `rm` 和 `rmdir` 移除也會被拒絕。`canUseTool` 永遠不會被呼叫 |
| `acceptEdits`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 自動接受檔案編輯 | 檔案編輯和[檔案系統操作](https://code.claude.com/docs/zh-TW/agent-sdk/permissions#accept-edits-mode-acceptedits)（`mkdir`、`rm`、`mv` 等）會自動被核准                                                                                                                                                                                                                                                                                             |
| `bypassPermissions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 略過權限檢查     | 工具執行時不會出現權限提示，除了[沒有任何模式自動核准的動作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)。請謹慎使用                                                                                                                                                                                                                                                                                        |
| `plan`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 規劃模式         | Claude 在不編輯您的原始檔案的情況下探索和規劃；檔案編輯永遠不會自動被核准，並透過您的 `canUseTool` 回呼提示                                                                                                                                                                                                                                                                                                                                        |
| `auto`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 模型分類核准     | 模型分類器核准或拒絕權限提示。請參閱 [Auto 模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)以了解可用性                                                                                                                                                                                                                                                                                                 |
| **子代理繼承：** 子代理在父工作階段的權限模式中執行，除非您在其 [`AgentDefinition`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#agentdefinition) 上設定 `permissionMode`，且父工作階段處於 `default`、`dontAsk` 或 `plan` 模式。即使如此，Claude Code 也永遠不會套用 `"bypassPermissions"` 值。子代理只有在父工作階段本身處於 `bypassPermissions` 模式時，才會在該模式中執行。`bypassPermissions` 例外需要 Claude Code v2.1.267 或更新版本。子代理可能具有不同的系統提示和比您的主代理更少受限的行為，因此繼承 `bypassPermissions` 會授予它們完整的自主系統存取權。[沒有任何模式自動核准的動作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)仍然適用。 |                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

### 設定權限模式

您可以在開始查詢時設定一次權限模式，或在工作階段進行中動態變更它。

- 在查詢時
- 在串流期間

在建立查詢時傳遞 `permission_mode`（Python）或 `permissionMode`（TypeScript）。此模式適用於整個工作階段，除非動態變更。 Python TypeScript

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Help me refactor this code",
        options=ClaudeAgentOptions(
            permission_mode="default",  # Set the mode here
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())

```

```
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  for await (const message of query({
    prompt: "Help me refactor this code",
    options: {
      permissionMode: "default" // Set the mode here
    }
  })) {
    if ("result" in message) {
      console.log(message.result);
    }
  }
}

main();

```

呼叫 `set_permission_mode()`（Python）或 `setPermissionMode()`（TypeScript）以在工作階段中途變更模式。新模式會立即對所有後續工具請求生效。這讓您可以從限制性開始，並隨著信任建立而放寬權限，例如在檢閱 Claude 的初始方法後切換到 `acceptEdits`。 Python TypeScript

```
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def main():
    async with ClaudeSDKClient(
        options=ClaudeAgentOptions(
            permission_mode="default",  # Start in default mode
        )
    ) as client:
        await client.query("Help me refactor this code")

        # Change mode dynamically mid-session
        await client.set_permission_mode("acceptEdits")

        # Process messages with the new permission mode
        async for message in client.receive_response():
            if hasattr(message, "result"):
                print(message.result)


asyncio.run(main())

```

```
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  const q = query({
    prompt: "Help me refactor this code",
    options: {
      permissionMode: "default" // Start in default mode
    }
  });

  // Change mode dynamically mid-session
  await q.setPermissionMode("acceptEdits");

  // Process messages with the new permission mode
  for await (const message of q) {
    if ("result" in message) {
      console.log(message.result);
    }
  }
}

main();

```

### 模式詳細資訊

#### 接受編輯模式（`acceptEdits`）

自動核准檔案操作，讓 Claude 可以編輯程式碼而不會提示。其他工具（例如不是檔案系統操作的 Bash 命令）仍然需要正常權限。 **自動核准的操作：**

- 檔案編輯（Edit、Write 工具）
- 檔案系統命令：`mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`

兩者都只適用於工作目錄或 `additionalDirectories` 內的路徑。在 `acceptEdits` 模式中，當 Claude 執行以下操作時，Claude Code 不會自動核准請求：

- 在該範圍外的路徑上工作
- 寫入受保護的路徑
- 使用 `rm` 或 `rmdir` 移除[關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths)

**使用時機：** 您信任 Claude 的編輯並想要更快的迭代，例如在原型設計期間或在隔離目錄中工作時。

#### 不要詢問模式（`dontAsk`）

將任何權限提示轉換為拒絕，而不呼叫 `canUseTool`。由 `allowed_tools`、`settings.json` 允許規則或鉤子預先核准的工具會正常執行，在 `default` 模式中不需要核准的呼叫也會執行，例如在您的工作目錄內的檔案讀取和對 `Agent` 的呼叫。您的組織[設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 的連接器工具、需要使用者互動的工具，以及針對[關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths)的 `rm` 和 `rmdir` 移除即使符合允許規則也會被拒絕。`PreToolUse` 鉤子允許也不會清除關鍵路徑移除。 **使用時機：** 您想要為無頭代理提供固定、明確的工具表面，並偏好硬拒絕而非無聲依賴 `canUseTool` 不存在。

#### 略過權限模式（`bypassPermissions`）

自動核准工具使用而不提示，除了下面警告中列出的情況。鉤子仍然執行，如果需要可以阻止操作。 請極其謹慎使用。Claude 在此模式中具有完整的系統存取權。僅在您信任所有可能操作的受控環境中使用。`allowed_tools` 不會限制此模式。每個工具都會被核准，而不僅僅是您列出的工具。這些控制仍然適用：

- 拒絕規則、明確的 `ask` 規則和鉤子在模式檢查之前被評估，仍然可以阻止工具。
- 您的組織[設定為 `ask`](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools) 的連接器工具、需要使用者互動的工具，以及針對[關鍵路徑](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths)的 `rm` 和 `rmdir` 移除仍然會進入您的 `canUseTool` 回呼。
- [跨工作階段訊息保護措施](https://code.claude.com/docs/zh-TW/permission-modes#skip-all-checks-with-bypasspermissions-mode)仍然適用。

#### 規劃模式（`plan`）

Claude 探索程式碼庫並產生計畫，而不編輯您的原始檔案。唯讀工具的執行方式與在 `default` 權限模式中相同。 在規劃模式中，檔案編輯永遠不會自動被核准，即使符合允許規則。它們會改為透過您的 `canUseTool` 回呼提示。在 Claude Code v2.1.212 或更新版本上，修改檔案的 shell 命令（例如 `touch` 和 `rm`）會以相同方式到達您的 `canUseTool` 回呼。 如果您在 `permissionMode: 'plan'` 旁邊設定 `allowDangerouslySkipPermissions: true`，檔案編輯和修改檔案的 shell 命令仍然會到達您的 `canUseTool` 回呼。此選項讓您稍後可以使用 `setPermissionMode()` 切換到 `bypassPermissions`。 Claude 可能會使用 `AskUserQuestion` 在最終確定計畫之前澄清需求。請參閱[處理核准和使用者輸入](https://code.claude.com/docs/zh-TW/agent-sdk/user-input#handle-clarifying-questions)以處理這些提示。 **使用時機：** 您想要 Claude 提議變更而不執行它們，例如在程式碼審查期間或當您需要在進行變更之前核准變更時。

## 相關資源

如需了解權限評估流程中的其他步驟：

- [處理核准和使用者輸入](https://code.claude.com/docs/zh-TW/agent-sdk/user-input)：互動式核准提示和澄清問題
- [Hooks 指南](https://code.claude.com/docs/zh-TW/agent-sdk/hooks)：在代理程式生命週期中的關鍵點執行自訂程式碼
- [權限規則](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings)：`settings.json` 中的宣告式允許/拒絕規則

是否 助手
