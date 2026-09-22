如果您維護 CLI 或 SDK，並在官方 Anthropic 市場中有外掛程式，您的工具可以提示 Claude Code 使用者安裝該外掛程式。當您的 CLI 偵測到它在 Claude Code 內執行時，會向 stderr 寫入單行標記。Claude Code 讀取該標記，將其從輸出中移除，並向使用者顯示一次性安裝提示。 該協議不需要額外命令，也不會改變您的 CLI 為 Claude Code 外部使用者列印的內容。 本頁面適用於 CLI 和 SDK 維護者。如果您正在尋找安裝外掛程式，請參閱[探索和安裝外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins)。

## 運作方式

Claude Code 為透過 Bash 和 PowerShell 工具執行的每個命令，以及 [hook](https://code.claude.com/docs/zh-TW/hooks) 命令設定 [`CLAUDECODE`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數為 `1`。從 v2.1.172 開始，它也會在這些相同的子程序中將 [`CLAUDE_CODE_CHILD_SESSION`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1`。當您的 CLI 看到其中一個變數時，它會向 stderr 寫入自閉合的 `<claude-code-hint />` 標籤。在 hook 命令中，提示標籤會被移除並忽略。只有 Bash 和 PowerShell 工具輸出會觸發安裝提示。 當 Claude Code 接收到命令輸出時，它會：

1. 掃描提示行並在輸出到達模型之前將其移除
1. 檢查提示是否指向官方 Anthropic 市場中的外掛程式
1. 檢查外掛程式是否尚未安裝且之前未提示過
1. 向使用者顯示安裝提示，其中包含發出提示的命令名稱

Claude Code 永遠不會自動安裝外掛程式。使用者始終需要確認。

## 發出提示

提示提示只會針對列在官方 Anthropic 市場中的外掛程式觸發。在您推出整合之前，請參閱[將您的外掛程式納入官方市場](https://code.claude.com/docs/zh-TW/plugin-hints#get-your-plugin-into-the-official-marketplace)。 在環境變數上設定發出條件，以便標記不太可能在人類直接執行您的 CLI 時出現，然後將標籤寫入 stderr 的單獨一行。選擇要檢查的變數：

- `CLAUDECODE`：在每個 Claude Code 版本上設定，因此可以到達最多的工作階段。它也在 Claude Code 啟動的 tmux 工作階段和 stdio MCP 伺服器子程序中設定，IDE 擴充功能在其整合終端中設定它，人類可能在那裡直接執行您的 CLI。
- `CLAUDE_CODE_CHILD_SESSION`：僅在 Claude Code 本身產生的子程序中設定，例如工具呼叫、hook 命令和[狀態列](https://code.claude.com/docs/zh-TW/statusline)命令，因此標籤通常不會到達人類終端。在工作階段內啟動的長期程序（例如 tmux 伺服器）會捕獲該變數，因此稍後從該程序啟動的 shell 仍會顯示原始標籤。

以下範例在 `CLAUDECODE` 上設定條件以達到最大覆蓋範圍，並為官方市場中名為 `example-cli` 的外掛程式發出提示： Node.js Python Go Shell

```
if (process.env.CLAUDECODE) {
  process.stderr.write(
    '<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />\n',
  )
}

```

```
import os, sys

if os.environ.get("CLAUDECODE"):
    print(
        '<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />',
        file=sys.stderr,
    )

```

```
if os.Getenv("CLAUDECODE") != "" {
    fmt.Fprintln(os.Stderr,
        `<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />`)
}

```

```
if [ -n "$CLAUDECODE" ]; then
  printf '%s\n' '<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />' >&2
fi

```

將 `example-cli` 替換為您在官方市場中的外掛程式名稱。

## 選擇發出位置

您可以控制哪些程式碼路徑發出提示。Claude Code 按外掛程式進行重複資料刪除，因此在每次呼叫時發出沒有缺點。運作良好的接觸點包括：

| 位置             | 為什麼有效                               |
| ---------------- | ---------------------------------------- |
| `--help` 輸出    | Claude 在探索不熟悉的 CLI 時經常執行幫助 |
| 未知子命令錯誤   | 到達 Claude 對您的介面感到困惑的時刻     |
| 登入或驗證成功   | 使用者已經處於設定心態                   |
| 首次執行歡迎訊息 | 自然的入門時刻                           |

## 使用者看到的內容

當提示通過所有檢查時，Claude Code 會顯示如下提示：

```
─────────────────────────────────────────────────────────────
  外掛程式推薦

    example-cli 命令建議安裝外掛程式。

    外掛程式：example-cli
    市場：claude-plugins-official
    example-cli 部署的官方整合

    您想要安裝它嗎？
    ❯ 1. 是的，安裝 example-cli
      2. 否
      3. 否，不再顯示外掛程式安裝提示

─────────────────────────────────────────────────────────────

```

提示會命名產生提示的命令，以便使用者可以發現工具與其推薦的外掛程式之間的不匹配。如果使用者在 30 秒內未回應，Claude Code 會將提示關閉為**否** 。 提示頻率受限，某些工作階段永遠不會提示：

- **每個外掛程式一次** ：顯示提示後，Claude Code 會記錄該外掛程式，無論使用者的答案如何，都不會再次提示。
- **每個工作階段一次** ：在機器上的所有 CLI 中，每個 Claude Code 工作階段最多出現一個提示。
- **僅限主要互動工作階段** ：Claude Code 只會在使用者正在輸入的終端工作階段中顯示提示。Claude Code 永遠不會提示 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 執行的命令，也不會在使用者使用 `-p` 旗標以 [non-interactive mode](https://code.claude.com/docs/zh-TW/headless) 執行 Claude Code 或透過 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 時提示。Claude Code 在所有這些情況下仍會從命令輸出中移除提示行。
- **遙測選擇退出** ：停用分析的工作階段永遠不會顯示提示。這包括設定了 `DISABLE_TELEMETRY` 或 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 的工作階段，以及 Amazon Bedrock 或 Google Cloud 的 Agent Platform 等第三方提供者上的工作階段，其中 [automatic telemetry opt-out](https://code.claude.com/docs/zh-TW/data-usage#default-behaviors-by-api-provider) 適用。

選擇**是的，安裝 example-cli** 會將外掛程式安裝到使用者範圍。選擇**否，不再顯示外掛程式安裝提示** 會為使用者停用所有未來的提示。

## 提示格式

提示是具有三個必需屬性的自閉合標籤。

```
<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />

```

| 屬性                                                                     | 必需 | 描述                                    |
| ------------------------------------------------------------------------ | ---- | --------------------------------------- |
| `v`                                                                      | 是   | 協議版本。`1` 是唯一支援的值            |
| `type`                                                                   | 是   | 提示類型。`plugin` 是唯一支援的值       |
| `value`                                                                  | 是   | `name@marketplace` 形式的外掛程式識別碼 |
| 屬性值可以用雙引號引用或不引用。未引用的值不能包含空格。不支援逸出序列。 |      |                                         |

## 要求

Claude Code 在對提示進行操作之前強制執行兩個條件。未通過任一檢查的提示會被丟棄：

- **自己的行** ：標籤必須佔據自己的行。嵌入在行中間的標籤，例如在日誌陳述式內，會被忽略。允許行上的前導和尾隨空格。
- **官方市場** ：`value` 必須參考 Anthropic 控制的市場中的外掛程式，例如 `claude-plugins-official`。指向其他市場的提示會被無聲地丟棄。

提示行始終會在到達模型之前從輸出中移除，即使版本或類型無法識別，因此標記永遠不會計入代幣使用量。 其餘指導是建議的，但不是強制的。Claude Code 無法觀察您的 CLI 是否遵循它：

- **寫入 stderr** ：stderr 將標籤保留在 shell 管道之外，例如 `example-cli deploy | jq`。Claude Code 掃描兩個流，因此 stdout 也有效。
- **在環境變數上設定條件** ：僅在設定 `CLAUDECODE` 或 `CLAUDE_CODE_CHILD_SESSION` 時發出。請參閱[發出提示](https://code.claude.com/docs/zh-TW/plugin-hints#emit-the-hint)以了解這兩個變數的差異。

## 將您的外掛程式納入官方市場

提示協議僅對列在官方 Anthropic 市場 `claude-plugins-official` 中的外掛程式生效。Anthropic 自行決定策劃該市場，應用程式內提交表單會將外掛程式新增到[社群市場](https://code.claude.com/docs/zh-TW/plugins#submit-your-plugin-to-the-community-marketplace)，提示協議不會檢查該市場。如果您正在與 Anthropic 合作夥伴聯絡人合作，請與他們聯繫以協調官方市場列表。

## 另請參閱

- [建立外掛程式](https://code.claude.com/docs/zh-TW/plugins)：建立您的 CLI 推薦的外掛程式
- [建立和發佈外掛程式市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)：在官方市場外託管外掛程式
- [環境變數](https://code.claude.com/docs/zh-TW/env-vars)：`CLAUDECODE` 和相關變數的完整參考

是否 助手
