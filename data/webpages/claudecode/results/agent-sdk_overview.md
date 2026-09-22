代理是一種應用程式，它通過規劃自己的步驟並呼叫讀取檔案、執行命令或編輯程式碼的工具來完成任務。Agent SDK 提供與 Claude Code 相同的工具、[代理迴圈](https://code.claude.com/docs/zh-TW/agent-sdk/agent-loop)和上下文管理，可在 Python 和 TypeScript 中進行程式設計。

## 將 Agent SDK 與其他 Claude 工具進行比較

Agent SDK、CLI、Client SDK 和 Managed Agents 各自適合不同的需求。使用下表找到符合您正在構建的工具。

| 如果您正在…                                                                                                                                                                                      | 使用                                                                              | 原因                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 構建代理而不自己實現工具迴圈                                                                                                                                                                     | **Agent SDK**                                                                     | 一個在您自己的程序中運行代理迴圈的庫，支援 Python 或 TypeScript。  |
| 進行互動式開發或從終端運行一次性任務                                                                                                                                                             | [**Claude Code CLI**](https://code.claude.com/docs/zh-TW/overview)                | 終端介面，為日常互動使用而構建。                                   |
| 直接呼叫 API 並自己實現工具迴圈                                                                                                                                                                  | [**Client SDK**](https://platform.claude.com/docs/en/api/client-sdks)             | 直接存取 Anthropic API 而不是 Claude Code。您自己實現工具迴圈。    |
| 運行長期運行或非同步代理，無需管理您自己的沙箱或工作階段基礎設施                                                                                                                                 | [**Managed Agents**](https://platform.claude.com/docs/en/managed-agents/overview) | 託管 REST API，是 Agent SDK 的獨立產品。Anthropic 運行代理和沙箱。 |
| SDK 僅作為 Python 和 TypeScript 的庫提供。若要從另一種語言驅動相同的代理迴圈，請[以子程序的形式運行 CLI](https://code.claude.com/docs/zh-TW/headless)，使用 `-p` 旗標和 `--output-format json`。 |                                                                                   |                                                                    |

## 功能

這些 Claude Code 功能可在 SDK 中使用：

| 功能               | 功能說明                                                              | 深入了解                                                                                                                                                                                                                                                                                                                |
| ------------------ | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 內建工具           | 讀取、寫入、編輯檔案、執行命令和搜尋網路                              | [工具參考](https://code.claude.com/docs/zh-TW/tools-reference)                                                                                                                                                                                                                                                          |
| Hooks              | 在代理生命週期的關鍵點執行自訂程式碼                                  | [Hooks](https://code.claude.com/docs/zh-TW/agent-sdk/hooks)                                                                                                                                                                                                                                                             |
| 子代理             | 生成專門的代理來處理集中的子任務                                      | [子代理](https://code.claude.com/docs/zh-TW/agent-sdk/subagents)                                                                                                                                                                                                                                                        |
| MCP                | 透過 Model Context Protocol 連接外部工具和資料來源                    | [MCP](https://code.claude.com/docs/zh-TW/agent-sdk/mcp)                                                                                                                                                                                                                                                                 |
| 權限               | 控制哪些工具自動執行、哪些需要批准                                    |                                                                                                                                                                                                                                                                                                                         |
| 工作階段           | 在多次交換中保持上下文、稍後恢復或分叉                                | [工作階段](https://code.claude.com/docs/zh-TW/agent-sdk/sessions)                                                                                                                                                                                                                                                       |
| Skills、命令和記憶 | 從您的專案的 `.claude/` 和 `~/.claude/` 自動載入，與 Claude Code 相同 | [Skills](https://code.claude.com/docs/zh-TW/agent-sdk/skills)、[命令](https://code.claude.com/docs/zh-TW/agent-sdk/skills#commands-in-agent-sdk-sessions)、[記憶](https://code.claude.com/docs/zh-TW/agent-sdk/modifying-system-prompts)、[設定載入](https://code.claude.com/docs/zh-TW/agent-sdk/claude-code-features) |
| Plugins            | 封裝 skills、代理、hooks 和 MCP 伺服器，並按本機路徑載入              | [Plugins](https://code.claude.com/docs/zh-TW/agent-sdk/plugins)                                                                                                                                                                                                                                                         |

## 開始使用

按照 [快速入門](https://code.claude.com/docs/zh-TW/agent-sdk/quickstart) 安裝 SDK、設定您的 API 金鑰，並建立您的第一個代理，該代理可以找到並修復現有程式碼中的錯誤。 除非事先獲得批准，否則 Anthropic 不允許第三方開發人員為其產品（包括基於 Claude Agent SDK 建立的代理）提供 claude.ai 登入或速率限制。請改用 [快速入門](https://code.claude.com/docs/zh-TW/agent-sdk/quickstart) 中描述的 API 金鑰驗證方法。

## 變更日誌

查看完整的變更日誌以了解 SDK 更新、錯誤修復和新功能：

- **TypeScript SDK** ：[檢視 CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
- **Python SDK** ：[檢視 CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)

## 報告錯誤

如果您遇到 Agent SDK 的錯誤或問題：

- **TypeScript SDK** ：[在 GitHub 上報告問題](https://github.com/anthropics/claude-agent-sdk-typescript/issues)
- **Python SDK** ：[在 GitHub 上報告問題](https://github.com/anthropics/claude-agent-sdk-python/issues)

## 品牌指南

對於整合 Claude Agent SDK 的合作夥伴，使用 Claude 品牌是可選的。在您的產品中引用 Claude 時： **允許：**

- “Claude Agent”（下拉選單的首選）
- “Claude”（當已在標記為”Agents”的選單中時）
- “{YourAgentName} Powered by Claude”（如果您有現有的代理名稱）

**不允許：**

- “Claude Code” 或 “Claude Code Agent”
- Claude Code 品牌的 ASCII 藝術或模仿 Claude Code 的視覺元素

您的產品應保持自己的品牌，不應顯示為 Claude Code 或任何 Anthropic 產品。有關品牌合規性的問題，請聯絡 Anthropic [銷售團隊](https://www.anthropic.com/contact-sales)。

## 許可證和條款

Claude Agent SDK 的使用受 [Anthropic 商業服務條款](https://www.anthropic.com/legal/commercial-terms)管制，包括當您使用它為您自己的客戶和最終使用者提供的產品和服務提供動力時，除非特定元件或依賴項受到該元件 LICENSE 檔案中指示的不同許可證的保護。

## 後續步驟

這些資源涵蓋了使用 Agent SDK 構建的更深入的技術細節和範例專案。

- [快速入門](https://code.claude.com/docs/zh-TW/agent-sdk/quickstart)：構建您的第一個代理，用於尋找和修復錯誤
- [遷移指南](https://code.claude.com/docs/zh-TW/agent-sdk/migration-guide)：從 Claude Code SDK 套件遷移到 Agent SDK
- [代理迴圈](https://code.claude.com/docs/zh-TW/agent-sdk/agent-loop)：Claude 如何規劃、呼叫工具以及決定何時任務完成
- [範例代理](https://github.com/anthropics/claude-agent-sdk-demos)：用於本地開發的示範應用程式
- [TypeScript SDK](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)：完整的 TypeScript API 參考和範例
- [Python SDK](https://code.claude.com/docs/zh-TW/agent-sdk/python)：完整的 Python API 參考和範例
- [Agent harness 設計](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)：Claude Code 團隊如何使用動態工作流程來同時協調許多子代理

是否 助手
