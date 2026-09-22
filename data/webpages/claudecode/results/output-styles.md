輸出樣式改變 Claude 的回應方式，而不是 Claude 知道什麼。它們設定 Claude 的角色、語氣和輸出格式，適用於每一個回應。當您每次都重新提示相同的語音或格式，或者當您希望 Claude 充當軟體工程師以外的角色時，請使用一個。 自訂輸出樣式將您的指令提供給 Claude，並讓您選擇是否保留 Claude Code 的內建軟體工程指令。當您改變 Claude 的溝通方式但仍在編碼時（例如始終用圖表回答），請保留它們。當 Claude 根本不進行軟體工程時（例如寫作助手或資料分析師），請省略它們。 有關您的專案、慣例或程式碼庫的說明，請改用 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)。

## 內建輸出樣式

Claude Code 的**預設** 輸出樣式是其標準指令集，旨在幫助您有效地完成軟體工程任務。 還有四種額外的內建輸出樣式：

- **Proactive** ：Claude 立即執行，做出合理的假設而不是暫停進行例行決策，並偏好行動而非規劃。這比[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)提供更強的自主執行指導，且無需改變您的權限模式，因此您的權限模式仍會決定哪些工具在不詢問的情況下執行。
- **Concise** ：Claude 以結果開頭，跳過前言和敘述，並預設保持回應簡潔，同時以與預設樣式相同的徹底程度進行工程工作。當您要求解釋或更多詳細資訊時，Claude 會完整回答。Claude 始終保留錯誤報告、安全警告和破壞性操作確認的完整內容。需要 Claude Code v2.1.237 或更新版本。
- **Explanatory** ：在幫助您完成軟體工程任務的同時提供教育性的「Insights」。幫助您理解實現選擇和程式碼庫模式。
- **Learning** ：協作式的邊做邊學模式，Claude 不僅會在編碼時分享「Insights」，還會要求您自己貢獻小的、策略性的程式碼片段。Claude Code 將在您的程式碼中添加 `TODO(human)` 標記供您實現。

## 變更您的輸出樣式

以下列其中一種方式選擇樣式：

- **`/output-style`命令** ：執行 `/output-style <style>` 以切換，例如 `/output-style concise`。不帶引數時，該命令會列出您可以選擇的樣式並標記目前的樣式。Claude Code 會將您的選擇儲存到[本地專案層級](https://code.claude.com/docs/zh-TW/settings)的 `.claude/settings.local.json`。 該命令也適用於[非互動模式](https://code.claude.com/docs/zh-TW/headless)和 Agent SDK 工作階段，以及來自行動應用程式或網頁的[遠端控制](https://code.claude.com/docs/zh-TW/remote-control#limitations)，您只能列出和選擇[內建樣式](https://code.claude.com/docs/zh-TW/output-styles#built-in-output-styles)。需要 Claude Code v2.1.269 或更新版本。
- **終端機** ：執行 `/config` 並選擇**輸出樣式** 以從選單中選擇樣式。Claude Code 會將您的選擇儲存到[本地專案層級](https://code.claude.com/docs/zh-TW/settings)的 `.claude/settings.local.json`。
- **VS Code 擴充功能** ：使用 `/` 開啟[命令選單](https://code.claude.com/docs/zh-TW/vs-code#use-the-prompt-box)並選擇**輸出樣式** 以選擇樣式，包括您的自訂樣式。Claude Code 會將您的選擇儲存到 `.claude/settings.local.json`，這是終端機選單寫入的同一個檔案。需要 Claude Code v2.1.257 或更新版本。
- **桌面應用程式** ：在設定檔中設定 `outputStyle` 欄位，例如 `.claude/settings.local.json`，這是終端機選單寫入的檔案。當您在那裡執行 `/config` 時，Claude Code [開啟**設定 > Claude Code**](https://code.claude.com/docs/zh-TW/desktop#what%E2%80%99s-not-available-in-desktop)而不是選單。

若要在不使用選單的情況下設定樣式，請直接編輯設定檔中的 `outputStyle` 欄位：

```
{
  "outputStyle": "Explanatory"
}

```

當您在工作階段中切換樣式時，Claude 會從您的下一則訊息開始使用新樣式。如需了解該第一則訊息在 prompt caching 中的成本，請參閱[變更輸出樣式](https://code.claude.com/docs/zh-TW/prompt-caching#changing-output-style)。在 v2.1.251 之前，新樣式僅在您執行 `/clear` 或開始新工作階段後才會套用。

## 建立自訂輸出樣式

自訂輸出樣式是一個 Markdown 檔案：frontmatter 用於中繼資料，然後是 Claude 的指令。 在 VS Code 擴充功能中，您也可以從[**輸出樣式** 選單](https://code.claude.com/docs/zh-TW/vs-code#use-the-prompt-box)建立檔案，而不是手動編寫。這需要 Claude Code v2.1.261 或更新版本。 1 建立 Markdown 檔案 將其儲存在三個層級之一。檔案名稱成為樣式名稱，除非您在 frontmatter 中設定 `name`。

- 使用者：`~/.claude/output-styles`
- 專案：`.claude/output-styles`
- 受管原則：[受管設定目錄](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)內的 `.claude/output-styles`

專案輸出樣式會從工作目錄和儲存庫根目錄之間的每個 `.claude/output-styles/` 載入。當多個這些巢狀目錄定義同名樣式時，Claude Code 會使用最接近工作目錄的那個。 2 添加 frontmatter 和指令 決定是否保留 Claude Code 的軟體工程指令。如果您改變 Claude 的溝通方式但仍希望它以相同方式編碼，請設定 `keep-coding-instructions: true`。如果 Claude 不會進行軟體工程，請省略它。此範例在保留 Claude 編碼行為的同時，在每個說明前面加上圖表：

```
---
name: Diagrams first
description: Lead every explanation with a diagram
keep-coding-instructions: true
---

When explaining code, architecture, or data flow, start with a Mermaid diagram showing the structure, then explain in prose.

## Diagram conventions

Use `flowchart TD` for control flow and `sequenceDiagram` for request paths. Keep diagrams under 15 nodes.

```

3 切換到您的樣式 在終端機中執行 `/output-style <style>`，或執行 `/config` 並在**輸出樣式** 下選擇您的樣式。Claude 從您的下一則訊息開始使用新樣式。在終端機中，Claude Code 在啟動時讀取樣式檔案，因此如果您在執行工作階段期間建立或編輯樣式檔案，請重新啟動 Claude Code 以套用變更。 [Plugins](https://code.claude.com/docs/zh-TW/plugins-reference) 也可以在 `output-styles/` 目錄中提供輸出樣式。

### Frontmatter

輸出樣式檔案支援這些 frontmatter 欄位：

| Frontmatter                | 用途                                                                                                                                                                        | 預設           |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| `name`                     | 輸出樣式的名稱，如果不是檔案名稱                                                                                                                                            | 繼承自檔案名稱 |
| `description`              | 輸出樣式的描述，在 `/config` 選擇器中顯示                                                                                                                                   | 無             |
| `keep-coding-instructions` | 保留 Claude Code 的內建軟體工程指令                                                                                                                                         | `false`        |
| `force-for-plugin`         | 僅限 Plugin 輸出樣式：在啟用 plugin 時自動應用此樣式，無需要求使用者選擇它。覆蓋使用者的 `outputStyle` 設定。如果多個啟用的 plugin 設定此項，Claude Code 使用第一個載入的。 | `false`        |

## 輸出樣式的工作原理

輸出樣式會改變 Claude Code 提供給 Claude 的指令。

- Claude Code 在每個請求中都會發送作用中樣式的指令。
- 當您[選擇預設以外的樣式](https://code.claude.com/docs/zh-TW/output-styles#change-your-output-style)時，Claude Code 也會在對話期間提醒 Claude 該樣式。
- 自訂輸出樣式排除了 Claude Code 的內建軟體工程指令，例如如何限定變更範圍、編寫註解和驗證工作，除非 `keep-coding-instructions` 設定為 `true`。

輸出樣式適用於主對話和[分支](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)，分支會繼承父項的完整對話和系統提示。其他[子代理會執行自己的系統提示](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup)，因此樣式不會改變它們的回應方式。 Token 使用量取決於樣式。樣式的指令會增加輸入 token，儘管 prompt caching 在工作階段中的第一個請求之後會降低此成本。 內建的 Explanatory 和 Learning 樣式按設計會產生比預設更長的回應，這會增加輸出 token。Concise 樣式則相反，它會指示 Claude 預設保持回應簡潔。對於自訂樣式，輸出 token 使用量取決於您的指令告訴 Claude 要產生什麼。

## 與相關功能的比較

多個功能自訂 Claude Code 的行為方式。輸出樣式變更 Claude Code 的預設指令，並應用於每個回應。其他功能添加指令而不改變預設值，或將其限定於特定任務。

| 功能                                                    | 工作原理                                 | 使用時機                                                                                                               |
| ------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 輸出樣式                                                | 變更 Claude Code 的預設指令              | 您希望每次都有不同的角色、語氣或預設回應格式                                                                           |
| [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)  | 在系統提示之後添加使用者訊息             | Claude 應該始終知道您的專案慣例和程式碼庫上下文                                                                        |
| `--append-system-prompt`                                | 附加到系統提示而不移除任何內容           | 您希望以 [CLI 旗標](https://code.claude.com/docs/zh-TW/cli-reference#system-prompt-flags) 的形式在啟動時進行一次性添加 |
| [Agents](https://code.claude.com/docs/zh-TW/sub-agents) | 使用自己的系統提示、模型和工具運行子代理 | 您希望為專注任務提供單獨作用域的幫助程式                                                                               |
| [Skills](https://code.claude.com/docs/zh-TW/skills)     | 在呼叫或相關時載入特定於任務的指令       | 您有可重複使用的工作流程                                                                                               |

## 相關資源

- [Settings](https://code.claude.com/docs/zh-TW/settings)：`outputStyle` 欄位所在位置以及設定優先順序的工作原理
- [Permission modes](https://code.claude.com/docs/zh-TW/permission-modes)：Proactive 樣式與自動模式的比較方式
- [Plugins](https://code.claude.com/docs/zh-TW/plugins)：與 skills、hooks 和 agents 一起打包和分發輸出樣式
- [Debug your configuration](https://code.claude.com/docs/zh-TW/debug-your-config)：診斷為什麼輸出樣式沒有生效

是否 助手
