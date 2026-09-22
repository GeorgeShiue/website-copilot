Plugins 允許您使用可在專案間共享的自訂功能來擴展 Claude Code。通過 Agent SDK，您可以以程式方式從本地目錄加載 plugins，以將功能添加到您的 agent sessions。一個 plugin 可以包括：

- **Skills** ：Claude 自主調用的功能。您也可以使用 `/plugin-name:skill-name` 直接調用 plugin skill。
- **Agents** ：用於特定任務的專門子 agents
- **Hooks** ：響應工具使用和其他事件的事件處理程序
- **MCP servers** ：通過 Model Context Protocol 的外部工具集成

有關 plugin 結構和如何創建 plugins 的完整資訊，請參閱 [Plugins](https://code.claude.com/docs/zh-TW/plugins)。

## 加載 plugins

通過在選項配置中提供本地文件系統路徑來加載 plugins。`type` 字段必須是 `"local"`，這是 SDK 接受的唯一值。SDK 支持從不同位置加載多個 plugins。 若要使用通過 [marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces) 或遠程存儲庫分發的 plugin，請先下載它並提供本地目錄路徑。有關 plugin 需要的目錄佈局，請參閱下面的 [Plugin 結構參考](https://code.claude.com/docs/zh-TW/agent-sdk/plugins#plugin-structure-reference)。 TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello",
  options: {
    plugins: [
      { type: "local", path: "./my-plugin" },
      { type: "local", path: "/absolute/path/to/another-plugin" }
    ]
  }
})) {
  // Plugin commands, agents, and other features are now available
}

```

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Hello",
        options=ClaudeAgentOptions(
            plugins=[
                {"type": "local", "path": "./my-plugin"},
                {"type": "local", "path": "/absolute/path/to/another-plugin"},
            ]
        ),
    ):
        # Plugin commands, agents, and other features are now available
        pass


asyncio.run(main())

```

### 路徑規範

Plugin 路徑可以是：

- **相對路徑** ：相對於 `cwd` 選項解析（例如，`"./plugins/my-plugin"`）
- **絕對路徑** ：完整文件系統路徑（例如，`"/home/user/plugins/my-plugin"`）

路徑應指向 plugin 的根目錄：`skills/`、`agents/`、`hooks/`、`commands/` 或 `.claude-plugin/` 的父目錄。

## 驗證 plugin 安裝

當 plugins 成功加載時，它們會出現在系統初始化消息中。您可以驗證您的 plugins 是否可用： TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello",
  options: {
    plugins: [{ type: "local", path: "./my-plugin" }]
  }
})) {
  if (message.type === "system" && message.subtype === "init") {
    // Check loaded plugins
    console.log("Plugins:", message.plugins);
    // Example: [{ name: "my-plugin", path: "/absolute/path/to/my-plugin" }]

    // Plugin skills appear with the plugin name as a prefix
    console.log("Skills:", message.skills);
    // Example: ["my-plugin:greet"]

    // Plugin commands use the same prefix, and skills appear here too
    console.log("Commands:", message.slash_commands);
    // Example: ["compact", "context", "my-plugin:custom-command", "my-plugin:greet"]
  }
}

```

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage


async def main():
    async for message in query(
        prompt="Hello",
        options=ClaudeAgentOptions(
            plugins=[{"type": "local", "path": "./my-plugin"}]
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            # Check loaded plugins
            print("Plugins:", message.data.get("plugins"))
            # Example: [{"name": "my-plugin", "path": "/absolute/path/to/my-plugin"}]

            # Plugin skills appear with the plugin name as a prefix
            print("Skills:", message.data.get("skills"))
            # Example: ["my-plugin:greet"]

            # Plugin commands use the same prefix, and skills appear here too
            print("Commands:", message.data.get("slash_commands"))
            # Example: ["compact", "context", "my-plugin:custom-command", "my-plugin:greet"]


asyncio.run(main())

```

## 使用 plugin skills

來自 plugins 的 skills 會自動使用 plugin 名稱進行命名空間化，以避免衝突。若要直接調用，請在提示中發送 `/plugin-name:skill-name`。 TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

// Load a plugin with a custom /greet skill
for await (const message of query({
  prompt: "/my-plugin:greet", // Use plugin skill with namespace
  options: {
    plugins: [{ type: "local", path: "./my-plugin" }]
  }
})) {
  // Claude executes the custom greeting skill from the plugin
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}

```

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock


async def main():
    # Load a plugin with a custom /greet skill
    async for message in query(
        prompt="/my-plugin:greet",  # Use plugin skill with namespace
        options=ClaudeAgentOptions(
            plugins=[{"type": "local", "path": "./my-plugin"}]
        ),
    ):
        # Claude executes the custom greeting skill from the plugin
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")


asyncio.run(main())

```

如果您通過 CLI 安裝了 plugin（例如，`/plugin install my-plugin@marketplace`），您仍然可以通過提供其安裝路徑在 SDK 中使用它。檢查 `~/.claude/plugins/` 以查找 CLI 安裝的 plugins。

## 完整示例

以下是演示 plugin 加載和使用的完整示例： TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";
import { fileURLToPath } from "node:url";

async function runWithPlugin() {
  const pluginPath = fileURLToPath(new URL("./plugins/my-plugin", import.meta.url));

  console.log("Loading plugin from:", pluginPath);

  for await (const message of query({
    prompt: "What custom commands do you have available?",
    options: {
      plugins: [{ type: "local", path: pluginPath }],
      maxTurns: 3
    }
  })) {
    if (message.type === "system" && message.subtype === "init") {
      console.log("Loaded plugins:", message.plugins);
      console.log("Available skills:", message.skills);
      console.log("Available commands:", message.slash_commands);
    }

    if (message.type === "assistant") {
      console.log("Assistant:", message.message.content);
    }
  }
}

runWithPlugin().catch(console.error);

```

```
#!/usr/bin/env python3
"""Example demonstrating how to use plugins with the Agent SDK."""

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    SystemMessage,
    TextBlock,
    query,
)


async def run_with_plugin():
    """Example using a custom plugin."""
    plugin_path = Path(__file__).parent / "plugins" / "my-plugin"

    print(f"Loading plugin from: {plugin_path}")

    options = ClaudeAgentOptions(
        plugins=[{"type": "local", "path": str(plugin_path)}],
        max_turns=3,
    )

    async for message in query(
        prompt="What custom commands do you have available?", options=options
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print(f"Loaded plugins: {message.data.get('plugins')}")
            print(f"Available skills: {message.data.get('skills')}")
            print(f"Available commands: {message.data.get('slash_commands')}")

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Assistant: {block.text}")


if __name__ == "__main__":
    asyncio.run(run_with_plugin())

```

## Plugin 結構參考

Plugin 目錄通常包含 `.claude-plugin/plugin.json` 清單文件。清單是可選的。省略時，Claude Code 會從目錄佈局自動發現組件。目錄可以包括：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin 清單（可選，沒有它也會自動發現組件）
├── skills/                   # Agent Skills（自主調用或通過 /plugin-name:skill-name）
│   └── my-skill/
│       └── SKILL.md
├── commands/                 # Skills 作為平面 .md 文件
│   └── custom-cmd.md
├── agents/                   # 自訂 agents
│   └── specialist.md
├── hooks/                    # 事件處理程序
│   └── hooks.json
└── .mcp.json                # MCP 伺服器定義

```

`commands/` 目錄保存 skills 作為平面 Markdown 文件。對於新 plugins，請使用 `skills/`。Claude Code 支持兩個位置。

## 多個 plugin 來源

結合來自不同位置的 plugins：

```
import * as os from "node:os";
import * as path from "node:path";

plugins: [
  { type: "local", path: "./local-plugin" },
  {
    type: "local",
    path: path.join(os.homedir(), ".claude", "custom-plugins", "shared-plugin")
  }
];

```

SDK 不會展開波浪號路徑，例如 `~/plugins`。如果 plugin 路徑不存在，SDK 會跳過該 plugin，會話會繼續，因此請檢查初始化消息中的 `plugins` 列表以確認每個 plugin 已加載。

## 故障排除

### Plugin 未加載

如果您的 plugin 未出現在初始化消息中：

1. **檢查路徑** ：確保路徑指向 plugin 根目錄，即 `skills/`、`agents/`、`hooks/`、`commands/` 或 `.claude-plugin/` 的父目錄
1. **驗證 plugin.json** ：如果您的 plugin 包含清單，請確保它具有有效的 JSON 語法
1. **檢查文件權限** ：確保 plugin 目錄可讀
1. **確認目錄存在** ：SDK 會跳過不存在的路徑，plugin 不會出現在初始化消息的 `plugins` 列表中

### Skills 未出現

如果 plugin skills 不起作用：

1. **使用命名空間** ：以 `/plugin-name:skill-name` 的方式調用 plugin skills
1. **檢查初始化消息** ：驗證 skill 是否以正確的命名空間出現在 `skills` 列表中
1. **驗證 skill 文件** ：確保每個 skill 在 `skills/` 下的自己的子目錄中都有 `SKILL.md` 文件，例如 `skills/my-skill/SKILL.md`

## 另請參閱

- [Plugins](https://code.claude.com/docs/zh-TW/plugins) - 完整的 plugin 開發指南
- [Plugins reference](https://code.claude.com/docs/zh-TW/plugins-reference) - 技術規範
- [Commands](https://code.claude.com/docs/zh-TW/agent-sdk/skills#dispatch-commands-by-name) - 在 SDK 中分派命令
- [Subagents](https://code.claude.com/docs/zh-TW/agent-sdk/subagents) - 使用專門的 agents
- [Skills](https://code.claude.com/docs/zh-TW/agent-sdk/skills) - 使用 Agent Skills

是否 助手
