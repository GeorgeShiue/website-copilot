系統提示詞定義了 Claude 的行為、功能和回應風格。從 `claude_code` 預設開始，適用於 CLI 或類似 IDE 的編碼工具，其中人類監督並引導工作。為具有不同介面、身份或權限模型的代理編寫您自己的提示詞。

## 系統提示詞如何運作

系統提示詞是初始指令集，塑造了 Claude 在整個對話中的行為方式。Agent SDK 有三個起點：

- **最小預設** ：當您在 TypeScript 中未設定 `systemPrompt` 或在 Python 中未設定 `system_prompt` 時，SDK 使用最小提示詞，涵蓋工具呼叫但省略了 `claude_code` 預設的其餘內容，包括其安全和防護指令以及關於工作目錄和環境的上下文。這與 `claude -p` 不同，後者預設使用 Claude Code 系統提示詞。如果您正在從 CLI 遷移並想要相符的行為，請設定 `claude_code` 預設。
- **`claude_code`預設** ：Claude Code CLI 使用的系統提示詞，包含工具使用指令、安全和防護指令，以及關於工作目錄和環境的上下文。在 TypeScript 中設定 `systemPrompt: { type: "preset", preset: "claude_code" }`，或在 Python 中設定 `system_prompt={"type": "preset", "preset": "claude_code"}`，可選擇使用 `append` 在末尾新增您自己的指令。
- **自訂字串** ：您自己撰寫的提示詞。SDK 只會傳送您提供的內容。

### 決定起點

決定因素是您的代理與 Claude Code 的相似程度：一個在儲存庫中運作的編碼代理，有人類監看串流輸出並引導工作。您的產品離該情況越遠，您就越想撰寫自己的提示詞。

| 您正在建置                                                                            | 使用                            | 您會得到                                                                             |
| ------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| 一個 CLI 或類似 IDE 的編碼工具，其中人類監看並引導，而 Claude Code 的預設值是您想要的 | `claude_code` 預設              | Claude Code 提示詞，包括工具指導、安全規則和環境上下文                               |
| 相同類型的工具，加上產品特定的規則，如編碼標準、輸出格式或領域上下文                  | `claude_code` 預設搭配 `append` | 上述所有內容，加上您的指令新增在預設之後。沒有任何內容被移除，所以這是風險最低的自訂 |
| 具有不同表面、身份或權限模型的代理，或非編碼代理                                      | 自訂提示詞字串                  | 僅您撰寫的內容。您負責替換您的代理仍需要的工具指導和安全指令                         |
| 一個薄型工具呼叫迴圈，沒有代理角色，您在使用者提示詞中提供所有行為                    | 無 `systemPrompt` 選項          | 最小預設：工具呼叫支援，沒有其他                                                     |
| 「不同於 Claude Code」通常意味著以下其中之一：                                        |                                 |                                                                                      |

- **不同的表面** ：輸出不是由觸發它的人在終端機中讀取。聊天 UI、結構化輸出消費者和非編碼自動化各自需要一個與其輸出呈現和審查方式相符的提示詞。無人值守的編碼自動化，如修復 lint 錯誤或審查差異的 CI 工作，仍然符合預設，因為工作本身是預設為其編寫的。
- **不同的身份** ：代理不應將自己呈現為 Claude Code。支援機器人、資料分析助手或任何特定領域的代理需要自己的名稱、範圍和角色。
- **不同的權限模型** ：代理自主運作，無需人類批准每一步，或在一組狹隘的資源上運作。Claude Code 的提示詞假設人類在迴圈中，可以存取完整的工具集。
- **非編碼任務** ：Claude Code 提示詞的大部分是編碼指導。對於研究、內容或運營代理，該指導與您實際需要的指令競爭。

[比較表](https://code.claude.com/docs/zh-TW/agent-sdk/modifying-system-prompts#compare-the-four-approaches)顯示每種自訂方法保留的內容。

## 自訂代理程式行為

`append` 和自訂提示詞字串各自直接改變系統提示詞，輸出樣式改變 Claude Code 給 Claude 每個回應的指令。CLAUDE.md 採用不同的路徑：SDK 讀取它並將其內容作為專案上下文注入對話中，因此它與您選擇的任何系統提示詞一起塑造行為。[Skills](https://code.claude.com/docs/zh-TW/agent-sdk/skills)、[hooks](https://code.claude.com/docs/zh-TW/agent-sdk/hooks) 和 [permissions](https://code.claude.com/docs/zh-TW/agent-sdk/permissions) 也在系統提示詞之外塑造行為，並在各自的頁面上涵蓋。

### 專案級指令的 CLAUDE.md 檔案

CLAUDE.md 檔案為 Claude 提供持久的專案上下文和指令。SDK 將其內容注入對話中並保持系統提示詞不變，因此它們適用於任何系統提示詞配置。關於在 CLAUDE.md 中放入什麼、放在哪裡以及如何編寫有效的指令，請參閱 [何時新增到 CLAUDE.md](https://code.claude.com/docs/zh-TW/memory#when-to-add-to-claude-md) 和 [Claude 如何記住您的專案](https://code.claude.com/docs/zh-TW/memory) 的其餘部分。本節涵蓋 SDK 特定的內容：CLAUDE.md 如何載入。 當匹配的設定來源已啟用時，SDK 讀取 CLAUDE.md：`'project'` 從工作目錄載入 `CLAUDE.md` 或 `.claude/CLAUDE.md`，`'user'` 載入 `~/.claude/CLAUDE.md`。預設 `query()` 選項啟用兩個來源，因此 CLAUDE.md 會自動載入。如果您在 TypeScript 中明確設定 `settingSources` 或在 Python 中設定 `setting_sources`，請包含您需要的來源。CLAUDE.md 載入由設定來源控制，而不是由 `claude_code` 預設值控制。

#### 使用 SDK 載入 CLAUDE.md

要載入 CLAUDE.md，請設定 `settingSources` 以包含您的 CLAUDE.md 所在的級別。下面的範例載入專案級 CLAUDE.md 以及 `claude_code` 預設值，因此 Claude 同時具有編碼代理程式提示詞和您專案的約定： TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];

for await (const message of query({
  prompt: "Add a new React component for user profiles",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code" // 使用 Claude Code 的系統提示詞
    },
    settingSources: ["project"] // 從專案載入 CLAUDE.md
  }
})) {
  messages.push(message);
}

// 現在 Claude 可以存取您來自 CLAUDE.md 的專案指南

```

```
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions

messages = []


async def main():
    async for message in query(
        prompt="Add a new React component for user profiles",
        options=ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",  # 使用 Claude Code 的系統提示詞
            },
            setting_sources=["project"],  # 從專案載入 CLAUDE.md
        ),
    ):
        messages.append(message)


asyncio.run(main())

# 現在 Claude 可以存取您來自 CLAUDE.md 的專案指南

```

當您執行任一範例時，SDK 會在 Claude 工作時串流訊息：系統初始化訊息、助手訊息、攜帶工具結果的使用者訊息，以及包含會話結果的最終結果訊息。 CLAUDE.md 在專案的所有會話中持續存在，通過 git 與您的團隊共享，並自動發現而無需程式碼變更。如果您傳遞空的 `settingSources` 陣列，則不會載入。

### 輸出樣式用於持久配置

輸出樣式是修改 Claude 角色、語調和輸出格式的已儲存指令集。它們儲存為 markdown 檔案，可以在會話和專案中重複使用。

#### 建立輸出樣式

輸出樣式是一個 markdown 檔案，其 [frontmatter](https://code.claude.com/docs/zh-TW/output-styles#frontmatter) 中有中繼資料，後面跟著提示詞內容。將其儲存到 `~/.claude/output-styles/` 以獲得在每個專案中可用的使用者級樣式，或儲存到您的儲存庫中的 `.claude/output-styles/` 以獲得可以提交並與您的團隊共享的專案級樣式。 自訂輸出樣式會省略 `claude_code` 預設值的軟體工程指令，並使用您自己的指令。要保留它們並在其上分層您的指令，請在 frontmatter 中設定 `keep-coding-instructions: true`。這些指令僅在 Claude Code 的完整系統提示詞中，因此該設定在較短系統提示詞的會話中無效，您可以使用 [`CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT`](https://code.claude.com/docs/zh-TW/env-vars#variables) 來開啟或關閉。當您的代理程式仍在進行軟體工程工作時保留它們。當您完全替換角色時省略它們。 下面的範例定義了程式碼審查角色，該角色保留編碼指令，因為審查程式碼仍然受益於 Claude Code 的安全性和程式碼品質指導。將其儲存為 `~/.claude/output-styles/code-reviewer.md` 以在專案中提供： ~/.claude/output-styles/code-reviewer.md

```
---
name: Code Reviewer
description: Thorough code review assistant
keep-coding-instructions: true
---

You are an expert code reviewer.

For every code submission:
1. Check for bugs and security issues
2. Evaluate performance
3. Suggest improvements
4. Rate code quality (1-10)

```

#### 啟用輸出樣式

建立後，通過以下方式啟用輸出樣式：

- **CLI** ：執行 `/output-style <style>`，例如 `/output-style concise`，或執行 `/config` 並選擇一個。`/output-style` 命令需要 Claude Code v2.1.269 或更新版本。
- **設定** ：在 `.claude/settings.local.json` 中設定 `outputStyle`
- **TypeScript SDK** ：在傳遞給 `query()` 的內聯 `settings` 物件內設定 `outputStyle`，或將 `settings` 指向設定該值的設定檔。`outputStyle` 不是頂級 `Options` 欄位：

```
const options = { settings: { outputStyle: "Explanatory" } };

```

在 Python SDK 中，通過 `settings` 選項設定 `outputStyle`，該選項接受 JSON 字串（例如 `'{"outputStyle": "Explanatory"}'`）或設定該值的設定檔的路徑。 **SDK 使用者注意：** 當您在選項中包含 `settingSources: ['user']` 或 `settingSources: ['project']`（TypeScript）/ `setting_sources=["user"]` 或 `setting_sources=["project"]`（Python）時，輸出樣式會被載入。

### 附加到 `claude_code` 預設值

您可以使用 Claude Code 預設值搭配 `append` 屬性來新增自訂指令，同時保留所有內建功能。 TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];

for await (const message of query({
  prompt: "Help me write a Python function to calculate fibonacci numbers",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "Always include detailed docstrings and type hints in Python code."
    }
  }
})) {
  messages.push(message);
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}

```

```
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

messages = []


async def main():
    async for message in query(
        prompt="Help me write a Python function to calculate fibonacci numbers",
        options=ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": "Always include detailed docstrings and type hints in Python code.",
            }
        ),
    ):
        messages.append(message)
        if isinstance(message, AssistantMessage):
            print(message.content)


asyncio.run(main())

```

#### 改進跨使用者和機器的提示詞快取

預設情況下，使用相同 `claude_code` 預設值和 `append` 文字的兩個會話，如果從不同的工作目錄執行，仍然無法共享提示詞快取項目。這是因為預設值在您的 `append` 文字之前在系統提示詞中嵌入了每個會話的上下文：工作目錄、它是否為 git 儲存庫、平台、活動 shell、OS 版本和自動記憶路徑。該上下文中的任何差異都會產生不同的系統提示詞和快取未命中。CLAUDE.md 內容不會影響系統提示詞快取，因為 SDK 將其注入對話中，而不是系統提示詞。 要使系統提示詞在會話中相同，請在 TypeScript 中設定 `excludeDynamicSections: true`，或在 Python 中設定 `"exclude_dynamic_sections": True`。每個會話的上下文移動到第一個使用者訊息中，只在系統提示詞中保留靜態預設值和您的 `append` 文字，以便相同的配置可以在使用者和機器之間共享快取項目。 `excludeDynamicSections` 需要 `@anthropic-ai/claude-agent-sdk` v0.2.98 或更新版本，或 Python 的 `claude-agent-sdk` v0.1.58 或更新版本。僅在預設物件形式上設定它。SDK 在您傳遞自訂提示詞而不是預設值時會忽略它；要在 TypeScript SDK 中保持自訂提示詞的指令快取，請參閱 [快取自訂提示詞的靜態部分](https://code.claude.com/docs/zh-TW/agent-sdk/modifying-system-prompts#cache-the-static-part-of-a-custom-prompt)。 以下範例將共享 `append` 區塊與 `excludeDynamicSections` 配對，以便從不同目錄執行的代理程式群隊可以重複使用相同的快取系統提示詞： TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Triage the open issues in this repo",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "You operate Acme's internal triage workflow. Label issues by component and severity.",
      excludeDynamicSections: true
    }
  }
})) {
  // ...
}

```

```
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Triage the open issues in this repo",
        options=ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": "You operate Acme's internal triage workflow. Label issues by component and severity.",
                "exclude_dynamic_sections": True,
            },
        ),
    ):
        ...


asyncio.run(main())

```

**權衡：** 工作目錄、git 儲存庫旗標、平台、活動 shell、OS 版本和自動記憶路徑仍然會到達 Claude，但作為第一個使用者訊息的一部分，而不是系統提示詞。使用者訊息中的指令比系統提示詞中的相同文字的權重略低，所以 Claude 在推理目前目錄或自動記憶路徑時可能會較少依賴它們。當跨會話快取重複使用比最大化權威環境上下文更重要時，請啟用此選項。 對於非互動式 CLI 模式中的等效旗標，請參閱 [`--exclude-dynamic-system-prompt-sections`](https://code.claude.com/docs/zh-TW/cli-reference)。

### 自訂系統提示詞

您可以提供自訂字串作為 `systemPrompt` 以完全用您自己的指令替換預設值。 TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

const customPrompt = `You are a Python coding specialist.
Follow these guidelines:
- Write clean, well-documented code
- Use type hints for all functions
- Include comprehensive docstrings
- Prefer functional programming patterns when appropriate
- Always explain your code choices`;

const messages = [];

for await (const message of query({
  prompt: "Create a data processing pipeline",
  options: {
    systemPrompt: customPrompt
  }
})) {
  messages.push(message);
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}

```

```
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

custom_prompt = """You are a Python coding specialist.
Follow these guidelines:
- Write clean, well-documented code
- Use type hints for all functions
- Include comprehensive docstrings
- Prefer functional programming patterns when appropriate
- Always explain your code choices"""

messages = []


async def main():
    async for message in query(
        prompt="Create a data processing pipeline",
        options=ClaudeAgentOptions(system_prompt=custom_prompt),
    ):
        messages.append(message)
        if isinstance(message, AssistantMessage):
            print(message.content)


asyncio.run(main())

```

在 Python 中，使用 `system_prompt={"type": "file", "path": "..."}` 而不是將其作為字串傳遞，從檔案載入大型自訂提示詞。Python SDK 將字串提示詞作為一個命令列引數傳遞給 CLI 子程序，因此超過 OS 引數長度限制的提示詞在任何 API 請求發送之前在程序生成時失敗。在 Linux 上，錯誤是 `Argument list too long`。請參閱 [`SystemPromptFile`](https://code.claude.com/docs/zh-TW/agent-sdk/python#systempromptfile) 以了解平台閾值和 Windows 行為。

#### 快取自訂提示詞的靜態部分

在 TypeScript SDK 中，您可以將自訂提示詞作為字串陣列而不是一個字串傳遞，在靜態部分和其餘部分之間使用 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 標記。當您的提示詞結合每個請求上相同的指令與每個請求變更的上下文（例如代理程式正在處理的客戶或票證）時，請使用此方法。當您將兩個部分作為一個字串傳遞時，對每個請求部分的變更會改變整個系統提示詞，因此靜態指令也會錯過快取。此形式在 Python SDK 中不可用；[`ClaudeAgentOptions`](https://code.claude.com/docs/zh-TW/agent-sdk/python#claudeagentoptions) 列出 `system_prompt` 接受的形式。 SDK 僅在直接呼叫 Claude API 或在 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 上執行時分割提示詞。在所有其他配置中，例如 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway-connect)，以及每當您設定 [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#disable-pre-release-capabilities) 時，SDK 會將整個提示詞作為一個區塊發送，與傳遞一個字串相同。 要分割提示詞，請從 `@anthropic-ai/claude-agent-sdk` 匯入 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 並將其作為兩個部分之間的自己的陣列元素傳遞。SDK 將標記之前的字串作為一個文字區塊發送，將標記之後的字串作為第二個區塊發送，每個都有自己的快取斷點。在下面的範例中，支援代理程式從檔案載入其分類指令，並在每個請求上接收一張票證的詳細資訊，因此指令保持快取而票證詳細資訊變更： TypeScript

```
import { readFile } from "node:fs/promises";
import { query, SYSTEM_PROMPT_DYNAMIC_BOUNDARY } from "@anthropic-ai/claude-agent-sdk";

// 在每個請求上相同
const instructions = await readFile("triage-instructions.md", "utf8");
// 在每個請求上不同
const ticketContext = "Customer plan: Enterprise. Other open tickets from this customer: 3.";

for await (const message of query({
  prompt: "Triage ticket 4821",
  options: {
    systemPrompt: [instructions, SYSTEM_PROMPT_DYNAMIC_BOUNDARY, ticketContext]
  }
})) {
  // ...
}

```

[追蹤快取令牌](https://code.claude.com/docs/zh-TW/agent-sdk/cost-tracking#track-cache-tokens) 描述每個結果訊息上的 `cache_creation_input_tokens` 和 `cache_read_input_tokens` 欄位。 SDK 從陣列組合區塊如下：

- SDK 在標記的每一側的字串之間用空行連接它們並移除標記本身，因此標記文字不會到達 Claude。
- 如果您多次包含標記，第一個是分割，SDK 移除其他的。
- 如果您省略標記，SDK 將所有字串連接到一個區塊中，與傳遞一個字串相同。

### 變更現有會話的提示詞

預設情況下，如果您在使用 `resume` 或 `continue` 返回會話時傳遞不同的 `append` 或自訂提示詞，Claude 在下一個回合中看不到它。Claude Code 在會話的第一個請求時記錄系統提示詞，並在會話被壓縮之前重複使用該記錄。新文字在壓縮後或在新會話中生效。

#### 在會話中更新 Claude 的指令

如果您在系統提示詞中放入的指令需要在會話執行時變更，例如因為您的使用者將代理程式切換到唯讀模式或在您的應用程式中編輯其配置，請在對話中發送新指令，而不是變更 `systemPrompt`：

- **在您的下一個訊息中** ：在您發送的下一個使用者訊息中包含新指令。
- **從 hook** ：從 `UserPromptSubmit` 或 `PostToolUse` [hook 回呼](https://code.claude.com/docs/zh-TW/agent-sdk/hooks#outputs) 傳回 [`additionalContext`](https://code.claude.com/docs/zh-TW/hooks#add-context-for-claude)，寫成事實陳述，例如「工作區現在是唯讀的」。SDK 在 hook 觸發的位置將文字插入對話中，因此記錄的提示詞保持不變。

#### 在您迭代措辭時關閉記錄

當您迭代提示詞措辭並希望每個編輯都到達您恢復的會話時，在系統提示詞的物件形式上設定 `snapshot` 為 false。Claude Code 然後在每個請求上重建提示詞。該欄位在 TypeScript 中的 [`systemPrompt`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options) 的預設值和自訂形式上可用，在 Python 中的 [`system_prompt`](https://code.claude.com/docs/zh-TW/agent-sdk/python#systempromptpreset) 上可用，並需要 `@anthropic-ai/claude-agent-sdk` v0.3.257 或更新版本，或 `claude-agent-sdk` v0.2.153 或更新版本。 在生產環境中保持記錄開啟。關閉記錄時，恢復的會話上的不同 `append` 或自訂提示詞在下一個回合中到達 Claude，該請求無法重複使用會話的 [提示詞快取](https://code.claude.com/docs/zh-TW/prompt-caching#how-the-cache-is-organized)。在 API 強制執行 [保留思考](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking) 的地方，Claude 也會失去其早期回合的思考。 在 [雲端會話](https://code.claude.com/docs/zh-TW/cloud-environments) 之外，如果您通過 `extraArgs` 傳遞 `--bare` 或設定 `CLAUDE_CODE_SIMPLE=1` 在 [裸模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode) 中啟動 Claude Code，記錄保持關閉，除非您設定 `snapshot: true`。 預設情況下記錄 `append` 或自訂提示詞需要 Claude Code v2.1.265 或更新版本，TypeScript Agent SDK 從 v0.3.265 開始捆綁，Python Agent SDK 從 v0.2.153 開始捆綁。在 Claude Code v2.1.268 之前，不 [擷取功能旗標](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching) 的會話，包括 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上的會話，在每個請求上重建提示詞，`snapshot` 無效。

## 比較四種方法

四種自訂方法在位置、共享方式和從 `claude_code` 預設保留的內容方面有所不同。

| 功能                                                                                                                                                                                                                                                                                   | CLAUDE.md    | 輸出樣式       | `systemPrompt` 附加 | 自訂 `systemPrompt` |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | -------------- | ------------------- | ------------------- |
| **持久性**                                                                                                                                                                                                                                                                             | 每個專案檔案 | 儲存為檔案     | 僅限會話            | 僅限會話            |
| **可重複使用性**                                                                                                                                                                                                                                                                       | 每個專案     | 跨專案         | 程式碼重複          | 程式碼重複          |
| **管理**                                                                                                                                                                                                                                                                               | 在檔案系統上 | CLI + 檔案     | 在程式碼中          | 在程式碼中          |
| **預設工具**                                                                                                                                                                                                                                                                           | 保留         | 保留           | 保留                | 遺失（除非包含）    |
| **內建安全**                                                                                                                                                                                                                                                                           | 維持         | 維持           | 維持                | 必須新增            |
| **環境上下文**                                                                                                                                                                                                                                                                         | 自動         | 自動           | 自動                | 必須提供            |
| **自訂程度**                                                                                                                                                                                                                                                                           | 僅新增       | 替換或擴展預設 | 僅新增              | 完全控制            |
| **版本控制**                                                                                                                                                                                                                                                                           | 與專案一起   | 是             | 與程式碼一起        | 與程式碼一起        |
| **範圍**                                                                                                                                                                                                                                                                               | 專案特定     | 使用者或專案   | 程式碼會話          | 程式碼會話          |
| 「附加」是指在 TypeScript 中使用 `systemPrompt: { type: "preset", preset: "claude_code", append: "..." }`，或在 Python 中使用 `system_prompt={"type": "preset", "preset": "claude_code", "append": "..."}`。CLAUDE.md 不會變更系統提示本身：SDK 會將其內容作為專案上下文注入到對話中。 |              |                |                     |                     |

## 組合方法

這些方法可以組合使用。持久輸出樣式或 CLAUDE.md 設定長期行為，而 `append` 在不觸及已儲存設定的情況下，在頂層疊加工作階段特定的指令。

### 將輸出樣式與工作階段特定的新增項目組合

下面的範例假設已經啟用 Code Reviewer 輸出樣式。`append` 區塊在角色上疊加工作階段特定的焦點領域，因此單一審查工作階段可以優先考慮 OAuth 和權杖儲存，而無需變更已儲存的輸出樣式： TypeScript Python

```
import { query } from "@anthropic-ai/claude-agent-sdk";

// Assuming "Code Reviewer" output style is active (via /config or settings)
// Add session-specific focus areas
const messages = [];

for await (const message of query({
  prompt: "Review this authentication module",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: `
        For this review, prioritize:
        - OAuth 2.0 compliance
        - Token storage security
        - Session management
      `
    }
  }
})) {
  messages.push(message);
}

```

```
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions

# Assuming "Code Reviewer" output style is active (via /config or settings)
# Add session-specific focus areas
messages = []


async def main():
    async for message in query(
        prompt="Review this authentication module",
        options=ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": """
                For this review, prioritize:
                - OAuth 2.0 compliance
                - Token storage security
                - Session management
                """,
            }
        ),
    ):
        messages.append(message)


asyncio.run(main())

```

## 另請參閱

- [輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)：為 CLI 建立、管理和分享輸出樣式，包括檔案格式和儲存位置
- [Claude 如何記住您的專案](https://code.claude.com/docs/zh-TW/memory)：CLAUDE.md 中應放入的內容、放置位置，以及如何撰寫有效的專案指示
- [TypeScript SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)：完整的 `Options` 類型，包括 `systemPrompt`、`settingSources` 和 `settings`
- [Python SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/python)：完整的 `ClaudeAgentOptions` 類型，包括 `system_prompt` 和 `setting_sources`
- [設定](https://code.claude.com/docs/zh-TW/settings)：`settings.json` 參考，包括輸出樣式和其他配置的儲存位置

是否 助手
