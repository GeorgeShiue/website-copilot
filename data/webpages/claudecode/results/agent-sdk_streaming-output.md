根據預設，Agent SDK 會在 Claude 完成生成每個非空內容區塊（例如文字區塊或工具呼叫）後產生完整的 `AssistantMessage`。若要在文字和工具呼叫生成時接收增量更新，請啟用部分訊息串流。 本頁涵蓋輸出串流（即時接收權杖）。如需輸入模式（如何傳送訊息），請參閱[傳送訊息給代理](https://code.claude.com/docs/zh-TW/agent-sdk/streaming-vs-single-mode)。您也可以[透過 CLI 使用 Agent SDK 串流回應](https://code.claude.com/docs/zh-TW/headless)。

## 啟用串流輸出

若要啟用串流，請在選項中將 `include_partial_messages`（Python）或 `includePartialMessages`（TypeScript）設定為 `true`。這會導致 SDK 產生包含原始 API 事件的 `StreamEvent` 訊息（當它們到達時），以及通常的 `AssistantMessage` 和 `ResultMessage`。 您的程式碼需要：

1. 檢查每個訊息的類型以區分 `StreamEvent` 和其他訊息類型
1. 對於 `StreamEvent`，提取 `event` 欄位並檢查其 `type`
1. 尋找 `content_block_delta` 事件，其中 `delta.type` 是 `text_delta`，其中包含實際的文字區塊

下面的範例啟用串流並在文字區塊到達時列印它們。注意巢狀類型檢查：首先是 `StreamEvent`，然後是 `content_block_delta`，然後是 `text_delta`： Python TypeScript

```
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_response():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Bash", "Read"],
    )

    async for message in query(prompt="List the files in my project", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta.get("text", ""), end="", flush=True)


asyncio.run(stream_response())

```

```
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "List the files in my project",
  options: {
    includePartialMessages: true,
    allowedTools: ["Bash", "Read"]
  }
})) {
  if (message.type === "stream_event") {
    const event = message.event;
    if (event.type === "content_block_delta") {
      if (event.delta.type === "text_delta") {
        process.stdout.write(event.delta.text);
      }
    }
  }
}

```

## StreamEvent 參考

啟用部分訊息時，您會收到包裝在物件中的原始 Claude API 串流事件。該類型在每個 SDK 中有不同的名稱：

- **Python** ：[`StreamEvent`](https://code.claude.com/docs/zh-TW/agent-sdk/python#streamevent)（從 `claude_agent_sdk.types` 匯入）
- **TypeScript** ：[`SDKPartialAssistantMessage`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkpartialassistantmessage)，其中 `type: 'stream_event'`

兩者都包含原始 Claude API 事件，而非累積的文字。您需要自行提取和累積文字差異。 在 Python 中，`parent_tool_use_id` 欄位始終為 `None`，在 TypeScript 中為 `null`。串流事件僅針對主工作階段發出；來自子代理的權杖級差異不會被轉發。若要將輸出歸因於子代理，請使用完整訊息，其中包含 `parent_tool_use_id`。請參閱[偵測子代理叫用](https://code.claude.com/docs/zh-TW/agent-sdk/subagents#detect-subagent-invocation)。 Claude Code 在該回合的第一個非 ping 串流事件上設定 `user_message_uuid`，以及當該回合正在回答的訊息變更時再次設定，條件如 [`user_message_uuid`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#user_message_uuid) 中所述。Python `StreamEvent` 不會公開此欄位。 `event` 欄位包含來自 [Claude API](https://platform.claude.com/docs/en/build-with-claude/streaming#event-types) 的原始串流事件。常見的事件類型包括：

| 事件類型              | 說明                                 |
| --------------------- | ------------------------------------ |
| `message_start`       | 新訊息的開始                         |
| `content_block_start` | 新內容區塊的開始（文字或工具使用）   |
| `content_block_delta` | 內容的增量更新                       |
| `content_block_stop`  | 內容區塊的結束                       |
| `message_delta`       | 訊息層級的更新（停止原因、使用情況） |
| `message_stop`        | 訊息的結束                           |

## 訊息流

Claude Code 在每個非空內容區塊完成時發出一個 `AssistantMessage`，因此包含文字區塊和工具呼叫的回應會產生兩個 `AssistantMessage` 物件。每個物件只攜帶自己的內容區塊，兩者共享相同的訊息 ID，您在 TypeScript 中讀取為 `message.message.id`，在 Python 中讀取為 `message.message_id`。啟用部分訊息後，每個 `AssistantMessage` 在該區塊的 `content_block_stop` 事件之前到達，您會按以下順序接收訊息：

```
StreamEvent (message_start)
StreamEvent (content_block_start) - text block
StreamEvent (content_block_delta) - text chunks...
AssistantMessage - complete text block
StreamEvent (content_block_stop)
StreamEvent (content_block_start) - tool_use block
StreamEvent (content_block_delta) - tool input chunks...
AssistantMessage - complete tool_use block
StreamEvent (content_block_stop)
StreamEvent (message_delta)
StreamEvent (message_stop)
... tool executes ...
... more streaming events for next turn ...
ResultMessage - final result

```

未啟用部分訊息時，您會接收除 `StreamEvent` 外的所有訊息類型。常見類型包括 `SystemMessage`（工作階段初始化）、`AssistantMessage`（完整內容區塊）、`ResultMessage`（最終結果）和一個緊湊邊界訊息，指示何時壓縮了對話歷史記錄（TypeScript 中為 `SDKCompactBoundaryMessage`；Python 中為具有子類型 `"compact_boundary"` 的 `SystemMessage`）。

## 串流工具呼叫

工具呼叫也會增量串流。您可以追蹤工具何時開始、在生成時接收其輸入，以及查看何時完成。下面的範例追蹤目前被呼叫的工具並在串流進來時累積 JSON 輸入。它使用三種事件類型：

- `content_block_start`：工具開始
- `content_block_delta` 搭配 `input_json_delta`：輸入區塊到達
- `content_block_stop`：工具呼叫完成

Python TypeScript

```
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_tool_calls():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash"],
    )

    # Track the current tool and accumulate its input JSON
    current_tool = None
    tool_input = ""

    async for message in query(prompt="Read the README.md file", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                # New tool call is starting
                content_block = event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    current_tool = content_block.get("name")
                    tool_input = ""
                    print(f"Starting tool: {current_tool}")

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "input_json_delta":
                    # Accumulate JSON input as it streams in
                    chunk = delta.get("partial_json", "")
                    tool_input += chunk
                    print(f"  Input chunk: {chunk}")

            elif event_type == "content_block_stop":
                # Tool call complete - show final input
                if current_tool:
                    print(f"Tool {current_tool} called with: {tool_input}")
                    current_tool = None


asyncio.run(stream_tool_calls())

```

```
import { query } from "@anthropic-ai/claude-agent-sdk";

// Track the current tool and accumulate its input JSON
let currentTool: string | null = null;
let toolInput = "";

for await (const message of query({
  prompt: "Read the README.md file",
  options: {
    includePartialMessages: true,
    allowedTools: ["Read", "Bash"]
  }
})) {
  if (message.type === "stream_event") {
    const event = message.event;

    if (event.type === "content_block_start") {
      // New tool call is starting
      if (event.content_block.type === "tool_use") {
        currentTool = event.content_block.name;
        toolInput = "";
        console.log(`Starting tool: ${currentTool}`);
      }
    } else if (event.type === "content_block_delta") {
      if (event.delta.type === "input_json_delta") {
        // Accumulate JSON input as it streams in
        const chunk = event.delta.partial_json;
        toolInput += chunk;
        console.log(`  Input chunk: ${chunk}`);
      }
    } else if (event.type === "content_block_stop") {
      // Tool call complete - show final input
      if (currentTool) {
        console.log(`Tool ${currentTool} called with: ${toolInput}`);
        currentTool = null;
      }
    }
  }
}

```

## 建立串流 UI

此範例將文字和工具串流結合成一個有凝聚力的 UI。它追蹤代理目前是否正在執行工具（使用 `in_tool` 旗標）以顯示狀態指示器，例如在工具執行時顯示 `[Using Read...]`。文字在不在工具中時正常串流，工具完成會觸發「完成」訊息。此模式對於需要在多步驟代理任務期間顯示進度的聊天介面很有用。 Python TypeScript

```
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from claude_agent_sdk.types import StreamEvent
import asyncio
import sys


async def streaming_ui():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash", "Grep"],
    )

    # Track whether we're currently in a tool call
    in_tool = False

    async for message in query(
        prompt="Find all TODO comments in the codebase", options=options
    ):
        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                content_block = event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    # Tool call is starting - show status indicator
                    tool_name = content_block.get("name")
                    print(f"\n[Using {tool_name}...]", end="", flush=True)
                    in_tool = True

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                # Only stream text when not executing a tool
                if delta.get("type") == "text_delta" and not in_tool:
                    sys.stdout.write(delta.get("text", ""))
                    sys.stdout.flush()

            elif event_type == "content_block_stop":
                if in_tool:
                    # Tool call finished
                    print(" done", flush=True)
                    in_tool = False

        elif isinstance(message, ResultMessage):
            # Agent finished all work
            print(f"\n\n--- Complete ---")


asyncio.run(streaming_ui())

```

```
import { query } from "@anthropic-ai/claude-agent-sdk";

// Track whether we're currently in a tool call
let inTool = false;

for await (const message of query({
  prompt: "Find all TODO comments in the codebase",
  options: {
    includePartialMessages: true,
    allowedTools: ["Read", "Bash", "Grep"]
  }
})) {
  if (message.type === "stream_event") {
    const event = message.event;

    if (event.type === "content_block_start") {
      if (event.content_block.type === "tool_use") {
        // Tool call is starting - show status indicator
        process.stdout.write(`\n[Using ${event.content_block.name}...]`);
        inTool = true;
      }
    } else if (event.type === "content_block_delta") {
      // Only stream text when not executing a tool
      if (event.delta.type === "text_delta" && !inTool) {
        process.stdout.write(event.delta.text);
      }
    } else if (event.type === "content_block_stop") {
      if (inTool) {
        // Tool call finished
        console.log(" done");
        inTool = false;
      }
    }
  } else if (message.type === "result") {
    // Agent finished all work
    console.log("\n\n--- Complete ---");
  }
}

```

## 已知限制

- **結構化輸出** ：JSON 結果僅出現在最終 `ResultMessage.structured_output` 中，而不是作為串流增量。如需詳細資訊，請參閱[結構化輸出](https://code.claude.com/docs/zh-TW/agent-sdk/structured-outputs)。

## 後續步驟

現在您可以即時串流文字和工具呼叫，請探索這些相關主題：

- [互動式與一次性查詢](https://code.claude.com/docs/zh-TW/agent-sdk/streaming-vs-single-mode)：為您的使用案例選擇輸入模式
- [結構化輸出](https://code.claude.com/docs/zh-TW/agent-sdk/structured-outputs)：從代理取得類型化的 JSON 回應
- [權限](https://code.claude.com/docs/zh-TW/agent-sdk/permissions)：控制代理可以使用哪些工具

是否 助手
