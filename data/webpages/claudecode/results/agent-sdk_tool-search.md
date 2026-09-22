工具搜尋使您的代理能夠通過動態發現和按需加載來處理數百或數千個工具。代理不是將所有工具定義預先加載到上下文窗口中，而是搜尋您的工具目錄並僅加載它需要的工具。 隨著工具庫的擴展，這種方法解決了兩個挑戰：

- **上下文效率：** 工具定義可能會消耗上下文窗口的大部分（50 個工具可能使用 10-20K 個令牌），留下較少的空間用於實際工作。
- **工具選擇準確性：** 同時加載超過 30-50 個工具時，工具選擇準確性會下降。

## 工具搜尋如何運作

工具搜尋預設為開啟，除了 [設定工具搜尋](https://code.claude.com/docs/zh-TW/agent-sdk/tool-search#configure-tool-search) 中列出的例外情況。 當工具搜尋為啟用時，工具定義會從內容視窗中隱藏。代理程式會收到可用工具的摘要，並在任務需要尚未載入的功能時搜尋相關工具。預設情況下，最多五個最相關的工具會被載入到內容中，並在後續回合中保持可用，直到 SDK 壓縮代理程式發現它們的訊息為止。在該壓縮之後，當代理程式下次需要這些工具時，會再次搜尋它們。 工具搜尋每次 Claude 搜尋工具時都會增加一個額外的往返，但對於大型工具集，這會因每個回合的內容較小而被抵消。對於少於約 10 個工具且其定義能舒適地放入內容視窗的情況，預先載入所有內容通常更快。 有關基礎 API 機制的詳細資訊，請參閱 [API 中的工具搜尋](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)。 Microsoft Foundry [部署在 Azure 上的部署](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options)不支援工具搜尋，這些部署會在伺服器端拒絕它：SDK 會偵測到拒絕，並改為預先載入該部署的工具定義。[`ENABLE_TOOL_SEARCH`](https://code.claude.com/docs/zh-TW/agent-sdk/tool-search#configure-tool-search) 無法覆蓋此設定，因為拒絕來自部署本身。

## 配置工具搜尋

工具搜尋預設為開啟。對於 SDK 的不支援模型清單上的模型，SDK 會預先載入工具定義，而不會有任何 `ENABLE_TOOL_SEARCH` 值覆蓋該行為。在 Google Cloud 的 Agent Platform 上，SDK 會根據模型世代決定：

- **Claude Opus 4.5、Sonnet 4.5、Haiku 4.5 及更高版本** ：工具搜尋預設為開啟。
- **較早的 Agent Platform 模型** ：SDK 會預先載入工具定義，因為其服務堆疊會拒絕所需的 beta 標頭。`ENABLE_TOOL_SEARCH` 無法覆蓋此行為。

在 Claude Code v2.1.221 之前，除非您設置 `ENABLE_TOOL_SEARCH`，否則 SDK 會為 Google Cloud 的 Agent Platform 上的所有模型禁用工具搜尋。 當 `ANTHROPIC_BASE_URL` 指向非第一方主機時，SDK 也會禁用工具搜尋，因為大多數代理不轉發 `tool_reference` 區塊。您可以使用 `ENABLE_TOOL_SEARCH` 環境變數覆蓋該預設值：

| 值                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 行為                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| （未設置）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 工具搜尋已開啟。工具定義被延遲並按需發現。在 Google Cloud 的 Agent Platform 早於 Claude 4.5 世代的模型、非第一方 `ANTHROPIC_BASE_URL` 或在 Azure 上託管的 Microsoft Foundry 部署上回退到預先載入。                                                                                  |
| `true`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 工具搜尋始終開啟，除了在 Azure 上託管的 Microsoft Foundry 部署（其中伺服器端拒絕仍會強制預先載入）和 Google Cloud 的 Agent Platform 早於 Claude 4.5 世代的模型（其中 SDK 會繼續預先載入工具定義）。SDK 會透過代理發送 beta 標頭，在不支援 `tool_reference` 區塊的代理上請求會失敗。 |
| `auto`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 計算工具搜尋可以延遲的工具定義中的令牌，並將總數與模型的上下文視窗進行比較。當總數達到視窗的 10% 時，工具搜尋會啟動。低於此值時，SDK 會預先將每個工具定義載入到上下文中。                                                                                                           |
| `auto:N`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 與 `auto` 相同，但具有自訂百分比。`auto:5` 在這些定義達到上下文視窗的 5% 時啟動。較低的值會更早啟動。                                                                                                                                                                               |
| `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 工具搜尋已關閉。所有工具定義在每個輪次都被載入到上下文中。                                                                                                                                                                                                                          |
| 設置 [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`](https://code.claude.com/docs/zh-TW/env-vars) 會保持工具搜尋關閉。您無法透過自行設置 `ENABLE_TOOL_SEARCH` 來覆蓋它。您的組織可以透過 [managed settings](https://code.claude.com/docs/zh-TW/managed-settings) 在 Claude Code v2.1.227 或更高版本上保持工具搜尋開啟。[停用預發行功能](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#disable-pre-release-capabilities) 涵蓋覆蓋適用的位置以及變數移除的內容。 工具搜尋適用於所有已註冊的工具，無論它們來自遠端 MCP 伺服器還是 [custom SDK MCP servers](https://code.claude.com/docs/zh-TW/agent-sdk/custom-tools)。當您使用 `auto` 時，SDK 會計算工具搜尋可以延遲的每個定義，達到一個組合閾值：來自任何伺服器的每個未標記為 [`alwaysLoad`](https://code.claude.com/docs/zh-TW/mcp#exempt-a-server-from-deferral) 的 MCP 工具，加上按需載入的內建工具。SDK 始終預先載入核心內建工具（例如 Bash、Read 和 Edit），並且不會將其計入閾值。 在 `query()` 上的 `env` 選項中設置該值。在 TypeScript 中，`env` 會取代子程序環境，因此請展開 `...process.env` 以保留繼承的變數。在 Python 中，`env` 會合併到繼承的環境之上。此示例連接到公開許多工具的遠端 MCP 伺服器，使用萬用字元預先批准所有工具，並使用 `auto:5` 以便在工具搜尋可以延遲的定義達到上下文視窗的 5% 時啟動工具搜尋： |                                                                                                                                                                                                                                                                                     |
| TypeScript                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                                                                                                                                                                                                                                                                                     |
| Python                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                     |

```
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({
    prompt: "Find and run the appropriate database query",
    options: {
      mcpServers: {
        "enterprise-tools": {
          // Connect to a remote MCP server
          type: "http",
          url: "https://tools.example.com/mcp"
        }
      },
      allowedTools: ["mcp__enterprise-tools__*"], // Wildcard pre-approves all tools from this server
      env: {
        ...process.env, // env replaces the subprocess environment, so keep inherited variables
        ENABLE_TOOL_SEARCH: "auto:5" // Activate tool search when deferrable definitions reach 5% of context
      }
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
} catch (error) {
  // A single-shot query() throws after yielding an error result
  console.log(`Session ended with an error: ${error}`);
}

```

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "enterprise-tools": {
                "type": "http",
                "url": "https://tools.example.com/mcp",
            }
        },
        allowed_tools=[
            "mcp__enterprise-tools__*"
        ],  # Wildcard pre-approves all tools from this server
        env={
            "ENABLE_TOOL_SEARCH": "auto:5"  # Activate tool search when deferrable definitions reach 5% of context
        },
    )

    try:
        async for message in query(
            prompt="Find and run the appropriate database query",
            options=options,
        ):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)
    except Exception as error:
        # A single-shot query() raises after yielding an error result
        print(f"Session ended with an error: {error}")


asyncio.run(main())

```

若要執行此示例，請將 `https://tools.example.com/mcp` 替換為您自己的 MCP 伺服器的 URL。成功時，結果文字會列印到主控台。 因為這是單次 `query()` 呼叫，SDK 會在產生錯誤結果後引發，所以此示例會將迴圈包裝在 try 區塊中。若要查看執行失敗的原因，請檢查結果訊息的 `subtype`（例如 `error_during_execution`）在迴圈內。如需有關結果訊息的詳細資訊，請參閱 [Handle the result](https://code.claude.com/docs/zh-TW/agent-sdk/agent-loop#handle-the-result)。

## 優化工具發現

搜尋機制將查詢與工具名稱和描述進行匹配。`search_slack_messages` 之類的名稱比 `query_slack` 適用於更廣泛的請求。具有特定關鍵字的描述（「按關鍵字、頻道或日期範圍搜尋 Slack 消息」）比通用描述（「查詢 Slack」）匹配更多查詢。 您也可以添加一個系統提示部分，列出可用的工具類別。這為代理提供了有關可搜尋的工具類型的上下文。通過 TypeScript 中的 `systemPrompt` 選項或 Python 中的 `system_prompt` 傳遞文本，使用 `claude_code` 預設搭配 `append`，這會將您的文本添加到預設的提示中，而不是替換它： TypeScript Python

```
options: {
  systemPrompt: {
    type: "preset",
    preset: "claude_code",
    append: "You can search for tools to interact with Slack, GitHub, and Jira."
  }
}

```

```
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": "You can search for tools to interact with Slack, GitHub, and Jira.",
    }
)

```

如需完整的系統提示選項集合，請參閱[修改系統提示](https://code.claude.com/docs/zh-TW/agent-sdk/modifying-system-prompts)。

## 限制

- **最大工具數：** 您的目錄中有 10,000 個工具
- **搜尋結果：** 預設情況下每次搜尋返回最多五個最相關的工具
- **模型支援：** Claude Sonnet 4.5、Claude Haiku 4.5、Claude Opus 4.5 及更新版本；請參閱 [API 文件中的模型相容性](https://platform.claude.com/docs/zh-TW/agents-and-tools/tool-use/tool-search-tool#model-compatibility)以取得目前清單。Google Cloud 的 Agent Platform 上也適用相同的最低要求。

## 相關文件

- [API 中的工具搜尋](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)：工具搜尋的完整 API 文件，包括自訂實作
- [連接 MCP 伺服器](https://code.claude.com/docs/zh-TW/agent-sdk/mcp)：透過 MCP 伺服器連接外部工具
- [自訂工具](https://code.claude.com/docs/zh-TW/agent-sdk/custom-tools)：使用 SDK MCP 伺服器建立您自己的工具
- [TypeScript SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)：完整 API 參考
- [Python SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/python)：完整 API 參考

是否 助手
