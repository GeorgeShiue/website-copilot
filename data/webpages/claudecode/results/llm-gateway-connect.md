[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)是您的組織在 Claude Code 和模型提供者之間運行的代理。當您的組織使用閘道時，Claude Code 使用您的組織簽發的認證向閘道進行身份驗證，而不是使用您個人的 claude.ai 登入。 本頁面適用於通過其組織運行的閘道運行 Claude Code 的開發人員。它涵蓋兩個路徑：[檢查您的管理員是否已為您配置它](https://code.claude.com/docs/zh-TW/llm-gateway-connect#check-for-an-existing-configuration)，以及[在他們未配置時自行配置](https://code.claude.com/docs/zh-TW/llm-gateway-connect#configure-claude-code-yourself)。

- 要為您的組織部署閘道，請參閱[推出 LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway-rollout)
- 有關 Claude Code 發送到閘道的內容，請參閱[閘道相容性指南](https://code.claude.com/docs/zh-TW/llm-gateway-protocol)

## 檢查現有配置

管理員可以通過[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)、裝置管理或 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#rotate-credentials-with-apikeyhelper) 分發閘道地址和認證，因此 Claude Code 在啟動時會自動獲取它們，無需您進行任何設定。要檢查您的組織是否已執行此操作： 1 啟動 Claude Code 執行 `claude`。如果它打開登入畫面而不是會話，則未分發閘道認證；[自行配置](https://code.claude.com/docs/zh-TW/llm-gateway-connect#configure-claude-code-yourself)如下。 2 檢查狀態標籤 如果 Claude Code 啟動了會話而未顯示登入畫面，執行 `/status`，打開**狀態** 標籤，並檢查兩行：

- `Anthropic base URL`：此行僅在設定了閘道地址時出現。如果不存在，Claude Code 未指向閘道；[自行配置](https://code.claude.com/docs/zh-TW/llm-gateway-connect#configure-claude-code-yourself)如下。
- `Auth token` 或 `API key`：命名 `ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY` 或 `apiKeyHelper` 的行確認閘道認證處於活動狀態。命名 claude.ai 帳戶的 `Login method` 行表示認證未被分發；[自行設定](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)。

3 發送測試訊息 關閉 `/status` 選單並在 Claude Code 中發送任何提示。來自 Claude 的正常回應（無錯誤）確認閘道連接有效。 如果 `/status` 選單中的兩行看起來都正確，但向 Claude 發送的訊息失敗，請參閱[故障排除表](https://code.claude.com/docs/zh-TW/llm-gateway-connect#troubleshoot-gateway-errors)。

## 自行配置 Claude Code

要自行為閘道配置 Claude Code，您需要從閘道團隊獲得：

- 閘道的基礎 URL
- 認證：金鑰或令牌字符串，或獲取認證的命令
  - 如果您的閘道團隊未說明認證的類型，下面的[認證變數部分](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)涵蓋了要嘗試的內容

下面的部分按順序涵蓋配置：

- [設定認證變數](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)和[設定基礎 URL](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-base-url-and-credential)：每個閘道連接需要的兩個變數
- [驗證連接](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)：在保存任何內容之前確認它有效
- [配置每個介面](https://code.claude.com/docs/zh-TW/llm-gateway-connect#configure-each-surface)：如果您使用除 Claude Code CLI 之外的介面（例如 VS Code），請查看如何使用閘道認證配置它
- [其他配置](https://code.claude.com/docs/zh-TW/llm-gateway-connect#additional-configuration)：某些閘道除了基礎 URL 和認證之外還需要的變數，例如自訂標頭、認證幫助程式、模型發現、提供者格式的基礎 URL 或關閉閘道路徑外的流量。僅在您的管理員命名它們或您的網路限制出站流量時設定這些

### 設定認證變數

要向閘道驗證 Claude Code，請在環境變數中設定您的認證。哪個變數取決於您的閘道團隊告訴您的內容：

| 在以下位置設定認證                                                                                                                                                                  | 使用時機                                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `ANTHROPIC_AUTH_TOKEN`                                                                                                                                                              | 您的閘道團隊說「bearer token」或「Authorization header」 |
| `ANTHROPIC_API_KEY`                                                                                                                                                                 | 您的閘道團隊說「API key」或「x-api-key」                 |
| [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#rotate-credentials-with-apikeyhelper)                                                                       | 認證輪換或來自保管庫                                     |
| 如果您未被告知是哪種類型，請使用 `ANTHROPIC_AUTH_TOKEN`；下面的[驗證請求](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)顯示如何判斷您是否需要切換。 |                                                          |

### 設定基礎 URL 和認證

將閘道的基礎 URL 和您上面選擇的認證變數設定為環境變數。示例使用 `ANTHROPIC_AUTH_TOKEN`；如果那是[您選擇的變數](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)，請將其替換為 `ANTHROPIC_API_KEY`。您可以在[您的 shell 中](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-as-shell-environment-variables)設定它們（持續一個終端會話），或在 [Claude Code 設定檔案中](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-in-a-settings-file)設定它們（在 Claude Code 運行的任何地方持續）。 對於您的第一次連接，從 shell 匯出開始，並在將值移動到設定檔案之前執行[驗證請求](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)。

#### 設定為 shell 環境變數

將值替換為您的閘道團隊提供的值：

- Bash or Zsh
- PowerShell

```
export ANTHROPIC_BASE_URL=https://llm-gateway.example.com
export ANTHROPIC_AUTH_TOKEN=sk-gateway-key

```

```
$env:ANTHROPIC_BASE_URL = "https://llm-gateway.example.com"
$env:ANTHROPIC_AUTH_TOKEN = "sk-gateway-key"

```

Shell 匯出僅適用於該終端會話和從它啟動的程式。從 dock 或開始功能表啟動的編輯器將看不到它們。要使它們在新終端中持續，請將相同的行添加到您的 shell 配置檔案，例如 `~/.zshrc`、`~/.bashrc` 或您的 PowerShell `$PROFILE`。 如果您只在 shell 中匯出閘道，它不會可靠地到達由[監督程式](https://code.claude.com/docs/zh-TW/agent-view#how-background-sessions-are-hosted)託管的背景代理；請參閱[每個背景會話如何獲取其閘道](https://code.claude.com/docs/zh-TW/agent-view#llm-gateway)。對於背景代理必須始終路由的任何閘道，請使用設定檔案。

#### 在設定檔案中設定

要使配置在 Claude Code 運行的任何地方應用，包括[背景代理](https://code.claude.com/docs/zh-TW/agent-view#how-background-sessions-are-hosted)，請在[設定檔案](https://code.claude.com/docs/zh-TW/settings)的 `env` 區塊中設定變數，而不是依賴您的 shell。設定檔案有不同的範圍：

- `~/.claude/settings.json` 適用於您的所有專案。在 Windows 上，路徑是 `%USERPROFILE%\.claude\settings.json`
- `.claude/settings.local.json` 適用於一個專案。Claude Code 在建立檔案時將其添加到您的全域 gitignore；如果您自己建立它或讓 Claude 寫入它，請先手動將其添加到 gitignore，以免您不小心提交您的認證

不要將認證放在專案的 `.claude/settings.json` 中。該檔案已提交並與克隆存儲庫的所有人共享。 `env` 區塊在任一檔案中看起來都相同：

```
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-gateway-key"
  }
}

```

當 shell 匯出和設定檔案 `env` 區塊都設定相同的變數時，設定檔案值適用。執行 `/status` 以查看 Claude Code 使用的基礎 URL 和認證來源。

### 驗證連接

使用在 shell 中匯出的變數，向閘道直接發送一個單令牌請求。這在您打開 Claude Code 之前確認 URL 和認證有效，因此失敗指向閘道而不是您的配置。下面的命令讀取 shell 變數，因此即使您也將值放在設定檔案中，它們也需要[shell 匯出](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-as-shell-environment-variables)。

- Bash or Zsh
- PowerShell

```
curl -X POST "$ANTHROPIC_BASE_URL/v1/messages" \
  -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'

```

```
Invoke-RestMethod -Method Post -Uri "$env:ANTHROPIC_BASE_URL/v1/messages" `
  -Headers @{ "Authorization" = "Bearer $env:ANTHROPIC_AUTH_TOKEN"; "anthropic-version" = "2023-06-01" } `
  -ContentType "application/json" `
  -Body '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'

```

如果您的閘道期望 `x-api-key` 標頭中的金鑰，請在 Bash 命令中將 `Authorization` 標頭替換為 `x-api-key: $ANTHROPIC_API_KEY`，或在 PowerShell 命令中將 `"Authorization"` 雜湊表項目替換為 `"x-api-key" = "$env:ANTHROPIC_API_KEY"`。 以 `{"id":"msg_` 開頭並包含 `"content":[...]` 欄位的 JSON 回應表示閘道可達且認證有效。命名未知模型的錯誤仍然證明 URL 和認證有效，因為閘道在拒絕模型名稱之前驗證了請求；您不需要為此測試找到您的閘道提供的模型。`401` 表示認證被拒絕：如果您猜測了變數，請切換到另一個並重新匯出。

#### 在 Claude Code 中確認

從同一 shell 啟動 `claude`，以便它繼承匯出，發送訊息，並執行 `/status`。 在**狀態** 標籤上，`Anthropic base URL` 行應顯示您的閘道地址，這確認請求正在路由到那裡；如果該行不存在，變數未到達會話。命名您設定的變數的 `Auth token` 或 `API key` 行確認閘道認證處於活動狀態，而不是已保存的 claude.ai 登入。 如果訊息失敗或 `/status` 未顯示閘道 URL，請參閱下面的[故障排除表](https://code.claude.com/docs/zh-TW/llm-gateway-connect#troubleshoot-gateway-errors)。

### 認證變數如何映射到標頭

每個變數在不同的 HTTP 標頭中發送認證：`ANTHROPIC_AUTH_TOKEN` 在 `Authorization: Bearer` 中，`ANTHROPIC_API_KEY` 在 `x-api-key` 中，`apiKeyHelper` 在兩者中。錯誤變數中的認證到達閘道時位於它不讀取的標頭中，請求失敗並返回 `401`。如果驗證請求返回 `401`，請切換到另一個變數並重試。

### 與現有登入的衝突

閘道認證變數優先於已保存的 claude.ai 登入或 Console 金鑰。您的 claude.ai 登入在設定變數時保持已保存且未使用；取消設定變數，Claude Code 會回到它。使用 `ANTHROPIC_AUTH_TOKEN` 時，變數立即優先。使用 `ANTHROPIC_API_KEY` 時，您在互動模式下被提示一次以批准金鑰，然後它接管。 執行 `/status` 以確認哪個認證來源處於活動狀態。如果啟動顯示命名兩個來源的身份驗證衝突警告，請參閱[故障排除表](https://code.claude.com/docs/zh-TW/llm-gateway-connect#troubleshoot-gateway-errors)的第一行以了解要刪除哪一個。要清除已保存的登入，以便只有閘道認證保留，請執行 `/logout`。

## 配置每個介面

CLI 讀取上面的環境變數和設定檔案。其他介面是 VS Code 擴充功能、桌面應用程式、GitHub Actions、Agent SDK 和雲端介面（例如 Slack 和網頁）；下面的部分涵蓋這些設定是否到達每一個。

### VS Code 擴充功能

在 VS Code 自己的使用者設定中的 `claudeCode.environmentVariables` 中為 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)設定閘道變數，使用**偏好設定：開啟使用者設定 (JSON)** 命令打開。擴充功能在啟動前檢查此設定中的認證，因此這是閘道認證的可靠位置；`~/.claude/settings.json` 中的值到達生成的程序但不到達擴充功能自己的登入檢查。

```
{
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "https://llm-gateway.example.com" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "sk-gateway-key" }
  ]
}

```

### 桌面應用程式

桌面應用程式從其[第三方推論配置](https://claude.com/docs/third-party/claude-desktop/gateway)讀取閘道路由，而不是從 `ANTHROPIC_BASE_URL` 或 `settings.json`。該配置可以來自您的組織或來自應用程式本身的表單：

- **由管理員分發** ：如果您的組織已[部署配置](https://code.claude.com/docs/zh-TW/llm-gateway-rollout#distribute-through-managed-settings)，桌面應用程式通過閘道路由，無需您進行任何設定
- **本地配置** ：對於沒有管理員分發配置的裝置，打開說明 → 疑難排解 → 啟用開發人員模式，這會使用開發人員功能表重新啟動應用程式。然後打開開發人員 → 配置第三方推論並輸入您的閘道基礎 URL。管理員分發的配置優先，並使此表單為唯讀

啟用閘道配置後，桌面應用程式僅在您的本機上運行會話：環境選擇器不提供 SSH 會話或 Anthropic 託管的雲端環境，[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)不可用。若要通過閘道在遠端主機上使用 Claude Code，請在該主機上運行 CLI，並在那裡設定[`ANTHROPIC_BASE_URL` 和閘道認證](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-base-url-and-credential)。 如果桌面應用程式顯示 `Gateway was unreachable`，應用程式在啟動時無法到達配置的基礎 URL；使用上面的 [curl 測試](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)檢查 URL 和網路路徑。

### GitHub Actions

[Claude Code GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 從工作流程的 `env` 區塊讀取 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_CUSTOM_HEADERS`。將認證作為操作的 `anthropic_api_key` 輸入傳遞；操作將其設定為 `ANTHROPIC_API_KEY`，因此它到達 `x-api-key` 標頭中的閘道。 對於 `x-api-key` 閘道，在 `env` 中設定基礎 URL 並將閘道金鑰作為輸入傳遞：

```
env:
  ANTHROPIC_BASE_URL: https://llm-gateway.example.com

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.GATEWAY_API_KEY }}

```

對於 bearer 令牌閘道，將相同的密鑰作為 `anthropic_api_key` 輸入和工作流程 `env` 區塊中的 `ANTHROPIC_AUTH_TOKEN` 傳遞。操作在啟動 Claude Code 之前需要 `anthropic_api_key`、`CLAUDE_CODE_OAUTH_TOKEN` 或工作負載身份聯合，並且它不讀取 `ANTHROPIC_AUTH_TOKEN`，因此輸入只是為了滿足該啟動檢查。env 變數是將金鑰放在閘道讀取的 `Authorization` 標頭中的原因；`x-api-key` 中的副本被忽略：

```
env:
  ANTHROPIC_BASE_URL: https://llm-gateway.example.com
  ANTHROPIC_AUTH_TOKEN: ${{ secrets.GATEWAY_API_KEY }}

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.GATEWAY_API_KEY }}

```

有關操作的其他身份驗證選項，包括 `CLAUDE_CODE_OAUTH_TOKEN` 和工作負載身份聯合，請參閱 [Claude Code GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 和操作的 [README](https://github.com/anthropics/claude-code-action#readme)。

### Agent SDK

[Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 沒有閘道特定的選項；它將環境變數傳遞給它生成的 Claude Code 程序。每個 SDK 接受一個 `env` 選項，用於設定生成的程序的環境，TypeScript 和 Python SDK 以不同的方式處理它：

- TypeScript：生成的程序預設繼承父環境，但設定 `options.env` 會完全替換環境。將 `process.env` 擴展到其中以保留您的閘道變數。
- Python：`ClaudeAgentOptions(env=...)` 合併到繼承的環境之上，因此在父程序中設定的閘道變數無需擴展即可通過。

TypeScript Python

```
const result = query({
  prompt: "...",
  options: {
    env: {
      ...process.env,
      ANTHROPIC_BASE_URL: "https://llm-gateway.example.com",
      ANTHROPIC_AUTH_TOKEN: process.env.GATEWAY_KEY,
    },
  },
})

```

```
options = ClaudeAgentOptions(
    env={
        "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
        "ANTHROPIC_AUTH_TOKEN": os.environ["GATEWAY_KEY"],
    }
)

```

### Slack、雲端會話和遠端控制

[Slack 中的 Claude Code](https://code.claude.com/docs/zh-TW/slack) 和[雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)始終使用 Anthropic 的 API；它們不是閘道部署的一部分。在雲端會話的環境配置中設定的閘道變數不適用。如果您的流量必須保留在閘道上，請不要為這些使用者啟用這些介面。 [遠端控制](https://code.claude.com/docs/zh-TW/remote-control)和[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)都依賴於 claude.ai 身份：遠端控制將實時會話與您的帳戶配對，語音聽寫到達 claude.ai 轉錄端點。當 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 處於活動狀態時，它們不可用。遠端控制在 `ANTHROPIC_BASE_URL` 指向非 Anthropic 主機時也被禁用，因此僅使用 claude.ai 登入本身是不夠的。在 v2.1.196 之前，非 Anthropic 基礎 URL 沒有阻止遠端控制。 若要還原任一功能，請使用 claude.ai 登入並取消設定該功能檢查的閘道變數。`claude doctor` 的遠端控制部分命名目前阻止遠端控制的內容。

- 語音聽寫：取消設定閘道認證
- 遠端控制：取消設定閘道認證和 `ANTHROPIC_BASE_URL`

## 其他配置

這些設定涵蓋超出基礎 URL 和認證的情況。僅在您的管理員的說明、您的網路的出站規則或[故障排除表](https://code.claude.com/docs/zh-TW/llm-gateway-connect#troubleshoot-gateway-errors)要求時設定它們。

### 發送其他標頭

某些閘道使用除認證外的自訂標頭路由或標記請求，例如租戶識別碼或路由金鑰。要發送一個，請設定 [`ANTHROPIC_CUSTOM_HEADERS`](https://code.claude.com/docs/zh-TW/env-vars)，每行一個 `Name: Value` 對。下面的示例添加了一個名為 `X-Org-Route` 的路由標頭：

- Bash or Zsh
- PowerShell

```
export ANTHROPIC_CUSTOM_HEADERS="X-Org-Route: prod"

```

```
$env:ANTHROPIC_CUSTOM_HEADERS = "X-Org-Route: prod"

```

您也可以在設定檔案的 `env` 區塊中設定 `ANTHROPIC_CUSTOM_HEADERS`。在那裡使用 `\n` 在對之間，因為 JSON 字符串不能跨越多行：

```
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Org-Route: prod\nX-Tenant: example"
  }
}

```

像這樣的路由和租戶標頭名稱計為[需要批准的標頭](https://code.claude.com/docs/zh-TW/server-managed-settings#environment-variables-and-the-approval-dialog)。當標頭來自專案設定檔案時，Claude Code 會根據[它應用 `env` 值的規則](https://code.claude.com/docs/zh-TW/settings-reference#when-claude-code-applies-env-values)應用它們。

### 將閘道模型添加到模型選擇器

啟用模型發現後，Claude Code 在啟動時查詢閘道以獲取其模型列表，並將這些名稱添加到 `/model` 選擇器以及內置項目。如果您或您的管理員在 [`modelPicker`](https://code.claude.com/docs/zh-TW/settings-reference#modelpicker) 陣列中設定 `replaceBuiltInOptions`，Claude Code 也會隱藏發現的名稱。它為會話已在使用的模型保留一行。 如果您的閘道提供不在 Claude Code 內置列表中的模型名稱，並且您想從選擇器中選擇它們，請啟用它。如果內置模型是您使用的，您不需要發現；您的管理員也可能已通過受管設定啟用它。 要啟用它，請在您的 shell 或 `~/.claude/settings.json` 的 `env` 區塊中設定 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`。 發現的模型顯示為其他 `/model` 項目。每個項目顯示您的閘道為模型提供的描述，或在它不提供描述時顯示 `From gateway`。 要確認發現已執行，請啟動 `claude --debug` 並在 `~/.claude/debug/<session-id>.txt` 的偵錯日誌中查找 `[gatewayDiscovery]` 行。第一次發現成功時，Claude Code 會記錄它緩存了多少模型，並且僅在閘道的列表更改時才再次記錄。`404`、超時或重定向也會出現在那裡。有關發現何時執行、它過濾什麼以及閘道提供的回應格式，請參閱[模型發現參考](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#model-discovery)。

### 使用 apiKeyHelper 輪換認證

`apiKeyHelper` 是 Claude Code 運行以獲取您的閘道認證的命令，而不是從靜態環境變數讀取它。 當認證按計劃過期、來自保管庫或 SSO 命令，或您的管理員告訴您配置一個時，使用幫助程式。如果您的認證是您設定一次的固定字符串，[認證變數](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)就是您需要的全部，您可以跳過本部分。 幫助程式是任何將當前認證列印到 stdout 的 shell 命令。Claude Code 通過您的系統 shell 運行它，因此在 Windows 上它可以是可執行檔案或 PowerShell 調用。編寫指令碼，使其可執行，並從您的[設定檔案](https://code.claude.com/docs/zh-TW/settings)中的 `apiKeyHelper` 參考它：

- Bash or Zsh
- PowerShell

例如，從保管庫讀取的指令碼：

```
#!/bin/bash
vault kv get -field=api_key secret/llm-gateway/claude-code

```

在 `~/.claude/settings.json` 中參考其路徑：

```
{
  "apiKeyHelper": "~/bin/get-gateway-key.sh"
}

```

例如，從保管庫讀取的指令碼：

```
vault kv get -field=api_key secret/llm-gateway/claude-code

```

在 `%USERPROFILE%\.claude\settings.json` 中參考 PowerShell 調用，轉義 JSON 字符串中的反斜杠：

```
{
  "apiKeyHelper": "powershell -NoProfile -File C:\\scripts\\get-gateway-key.ps1"
}

```

Claude Code 預設將幫助程式的輸出緩存五分鐘，並在緩存生命週期過期後重新運行幫助程式。要更改生命週期，請以毫秒為單位設定 `CLAUDE_CODE_API_KEY_HELPER_TTL_MS`，例如 `CLAUDE_CODE_API_KEY_HELPER_TTL_MS=900000` 表示 15 分鐘。在 Claude Code v2.1.227 或更高版本上，與金鑰一起列印的橫幅或日誌行會使[幫助程式失敗](https://code.claude.com/docs/zh-TW/errors#your-apikeyhelper-script-is-failing)。 請參閱 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 以了解 Claude Code 重新運行幫助程式的其他情況。 幫助程式的值在 `Authorization` 和 `x-api-key` 標頭中都發送，因此無論您的閘道讀取哪個標頭都有效。

### 關閉閘道路徑外的流量

閘道承載模型請求，但 Claude Code 也會向閘道路徑外發送非必要的背景流量，發送到 Anthropic 和第三方服務（如 GitHub）：版本檢查、遙測、發行說明和類似請求。在只允許出站到閘道的網路上，這些請求會失敗，並且可能在您的出站監控中顯示為被阻止的連接。 Claude Code 僅在請求前往認證所屬的主機時，才會將認證附加到遙測或使用量指標請求。當 `ANTHROPIC_BASE_URL` 指向閘道時，Claude Code 會將其遙測事件發送到 Anthropic，而不使用您的閘道認證。當[認證變數](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)或 `apiKeyHelper` 也處於活動狀態時，Claude Code 不會向 Console [分析儀表板](https://code.claude.com/docs/zh-TW/analytics#access-analytics-for-api-customers)報告使用量指標。在 v2.1.246 之前，Claude Code 可能會將閘道認證附加到發往 Anthropic 主機的遙測和使用量指標請求；模型請求始終使用閘道期望的認證前往閘道。 要關閉該流量，請在與閘道變數相同的 shell 導出或設定檔案 `env` 區塊中設定 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`：

- Bash or Zsh
- PowerShell

```
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

```

```
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"

```

設定變數具有以下效果和限制：

- 它禁用自動更新，因此請計劃另一個更新路徑，例如您的套件管理器或受管分發。
- 它抑制[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)可用性檢查。除非之前的檢查已在機器上啟用快速模式，否則 `/fast` 報告快速模式不可用。
- 它不影響[閘道模型發現](https://code.claude.com/docs/zh-TW/llm-gateway-connect#add-gateway-models-to-the-model-picker)，它僅查詢您的閘道。在 v2.1.257 之前，該變數也停止了發現的刷新，因此選擇器保留了之前緩存的列表。
- WebFetch 工具的[域安全檢查](https://code.claude.com/docs/zh-TW/data-usage#webfetch-domain-safety-check)不受影響，仍會呼叫 `api.anthropic.com`。如果您的網路阻止該主機，請在[設定](https://code.claude.com/docs/zh-TW/settings)中使用 `skipWebFetchPreflight: true` 單獨關閉它。
- 對於每個遙測流和控制它的變數，請參閱[遙測服務](https://code.claude.com/docs/zh-TW/data-usage#telemetry-services)。

### 通過閘道路由到雲端提供者

這些配置使用提供者特定的基礎 URL 變數代替 `ANTHROPIC_BASE_URL` 將 Claude Code 指向通過閘道的雲端提供者。Amazon Bedrock 和 Google Cloud 的 Agent Platform 閘道接受這些提供者的本機請求格式；Microsoft Foundry 和 AWS 上的 Claude Platform 閘道接受 Anthropic Messages 格式。在 Amazon Bedrock 和 Google Cloud 的 Agent Platform 路由上，Claude Code 也會將它發送的 beta 標頭和請求欄位限制為該提供者接受的集合。有關您的閘道在每個路由上接收的內容，請參閱[閘道相容性指南](https://code.claude.com/docs/zh-TW/llm-gateway-protocol)。 僅在您的閘道團隊特別命名 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或 AWS 上的 Claude Platform 時使用一個。如果上面的[驗證請求](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)返回 JSON，您可以跳過本部分。 為您的閘道團隊命名的提供者設定區塊。Amazon Bedrock、Google Cloud 的 Agent Platform 和 AWS 上的 Claude Platform 區塊中的跳過身份驗證變數告訴 Claude Code 不要使用雲端提供者的認證簽署請求，因為閘道持有這些。如果閘道也需要自己的令牌，您放置它的位置取決於提供者：

- **Amazon Bedrock、Google Cloud 的 Agent Platform 或 AWS 上的 Claude Platform** ：在區塊後添加 `ANTHROPIC_AUTH_TOKEN`。Claude Code 將其作為 `Authorization: Bearer` 標頭發送到閘道。對於不同方案或標頭中的認證，請改用 [`ANTHROPIC_CUSTOM_HEADERS`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#send-additional-headers)。無論如何都保持跳過身份驗證變數設定，因為沒有它，Claude Code 會移除 `ANTHROPIC_AUTH_TOKEN`、[`apiKeyHelper`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#rotate-credentials-with-apikeyhelper) 或 `ANTHROPIC_CUSTOM_HEADERS` 會添加的任何 `Authorization` 標頭。
- **Microsoft Foundry** ：使用 `ANTHROPIC_FOUNDRY_API_KEY`，如[其區塊](https://code.claude.com/docs/zh-TW/llm-gateway-connect#microsoft-foundry)所示

#### Amazon Bedrock

當閘道發出自己的認證時，將 `AWS_BEARER_TOKEN_BEDROCK` 保留為未設定。如果您設定它，Claude Code 會將該 [Amazon Bedrock API 金鑰](https://code.claude.com/docs/zh-TW/amazon-bedrock#2-configure-aws-credentials)作為 `Authorization` 標頭發送，而不是您的閘道令牌，即使設定了 `CLAUDE_CODE_SKIP_BEDROCK_AUTH`。

- Bash or Zsh
- PowerShell

```
export ANTHROPIC_BEDROCK_BASE_URL=https://llm-gateway.example.com/bedrock
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1
export CLAUDE_CODE_USE_BEDROCK=1

```

```
$env:ANTHROPIC_BEDROCK_BASE_URL = "https://llm-gateway.example.com/bedrock"
$env:CLAUDE_CODE_SKIP_BEDROCK_AUTH = "1"
$env:CLAUDE_CODE_USE_BEDROCK = "1"

```

#### Google Cloud 的 Agent Platform

將專案 ID 和區域替換為您自己的值。Claude Code 在它發送到閘道的每個請求的路徑中包含兩者：

- Bash or Zsh
- PowerShell

```
export ANTHROPIC_VERTEX_BASE_URL=https://llm-gateway.example.com/vertex
export ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5

```

```
$env:ANTHROPIC_VERTEX_BASE_URL = "https://llm-gateway.example.com/vertex"
$env:ANTHROPIC_VERTEX_PROJECT_ID = "your-gcp-project-id"
$env:CLAUDE_CODE_SKIP_VERTEX_AUTH = "1"
$env:CLAUDE_CODE_USE_VERTEX = "1"
$env:CLOUD_ML_REGION = "us-east5"

```

該區塊涵蓋路由和身份驗證。來自 [Agent Platform 設定](https://code.claude.com/docs/zh-TW/google-vertex-ai#4-configure-claude-code)的區域覆蓋和模型固定也通過閘道應用：

- **每個模型的區域** ：如果您的閘道從 `CLOUD_ML_REGION` 以外的區域提供某些模型，請為每個設定匹配的 `VERTEX_REGION_CLAUDE_*` 變數，例如 `VERTEX_REGION_CLAUDE_4_6_SONNET=europe-west1`。[環境變數參考](https://code.claude.com/docs/zh-TW/env-vars)列出了確切的名稱。
- **模型版本** ：如 [Pin model versions](https://code.claude.com/docs/zh-TW/google-vertex-ai#5-pin-model-versions) 中所示，固定 `ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL` 和 `ANTHROPIC_DEFAULT_HAIKU_MODEL`。設定 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 也會將背景任務（如會話標題）移動到該模型，該部分解釋了哪個模型在其他情況下運行它們。
- **模型功能** ：如果您固定您的 Claude Code 版本不識別的模型 ID，功能（如努力級別或擴展思考）可能在其上保持禁用。使用 [`ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES`](https://code.claude.com/docs/zh-TW/model-config#customize-pinned-model-display-and-capabilities) 及其 Sonnet 和 Haiku 對應項聲明模型支持的內容。

#### Microsoft Foundry

將閘道的認證放在 `ANTHROPIC_FOUNDRY_API_KEY` 中；它作為 `x-api-key` 標頭發送到閘道。期望持有人令牌的閘道可以改用 [`ANTHROPIC_FOUNDRY_AUTH_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars)。Claude Code 將該值作為 `Authorization: Bearer` 標頭發送，當兩者都設定時，它優先於 `ANTHROPIC_FOUNDRY_API_KEY`。需要 Claude Code v2.1.203 或更高版本。 對於注入自己的 `Authorization` 標頭的閘道，設定 `CLAUDE_CODE_SKIP_FOUNDRY_AUTH=1` 並將兩個認證變數都保留為未設定。Claude Code 然後發送沒有 Azure 認證的請求，並保留您提供的 `Authorization` 標頭，例如通過 `ANTHROPIC_CUSTOM_HEADERS`。在 v2.1.203 之前，`CLAUDE_CODE_SKIP_FOUNDRY_AUTH` 沒有 API 金鑰使 Microsoft Foundry 客戶端無法發送請求。

- Bash or Zsh
- PowerShell

```
export ANTHROPIC_FOUNDRY_BASE_URL=https://llm-gateway.example.com/foundry
export ANTHROPIC_FOUNDRY_API_KEY=sk-gateway-key
export CLAUDE_CODE_USE_FOUNDRY=1

```

```
$env:ANTHROPIC_FOUNDRY_BASE_URL = "https://llm-gateway.example.com/foundry"
$env:ANTHROPIC_FOUNDRY_API_KEY = "sk-gateway-key"
$env:CLAUDE_CODE_USE_FOUNDRY = "1"

```

#### AWS 上的 Claude Platform

有關工作區 ID，請參閱 [AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)。

- Bash or Zsh
- PowerShell

```
export ANTHROPIC_AWS_BASE_URL=https://llm-gateway.example.com/anthropic-aws
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1

```

```
$env:ANTHROPIC_AWS_BASE_URL = "https://llm-gateway.example.com/anthropic-aws"
$env:ANTHROPIC_AWS_WORKSPACE_ID = "wrkspc_01ABCDEFGHIJKLMN"
$env:CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH = "1"
$env:CLAUDE_CODE_USE_ANTHROPIC_AWS = "1"

```

#### 確認提供者路由

從您設定區塊的 shell 啟動 `claude` 並運行 `/status`。使用 Amazon Bedrock 區塊，**Status** 標籤顯示如下行：

```
API provider: Amazon Bedrock
Bedrock base URL: https://llm-gateway.example.com/bedrock
AWS auth skipped

```

其他區塊在其提供者的名稱下產生相同的行，例如 Google Cloud 的 Agent Platform 的 `Vertex base URL` 和 `GCP auth skipped`；Microsoft Foundry 區塊僅在您設定 `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` 時顯示身份驗證跳過行。如果您也通過公司代理路由，`Proxy` 行顯示代理 URL。如果基礎 URL 行缺失，該變數未到達會話。

## 故障排除閘道錯誤

這些是通過閘道運行 Claude Code 時最常見的錯誤，包括閘道端的原因和修復：

| 錯誤                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 原因                                                                                                                                                                                                                                                                                        | 修復                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 啟動警告命名兩個認證來源並以 `auth may not work as expected` 結尾。較舊的版本顯示 `Auth conflict: Both a token (SOURCE) and an API key (SOURCE) are set` 代替。                                                                                                                                                                                                                                                                                                       | 閘道認證和已保存的登入都處於活動狀態；變數用於請求，但過時的登入可能導致意外的身份驗證行為                                                                                                                                                                                                  | 取消設定變數以使用已保存的登入，或執行 `/logout` 以使用閘道認證                                                                                                                                                                                                                                                |
| `401` 錯誤命名無效或無法識別的令牌                                                                                                                                                                                                                                                                                                                                                                                                                                    | 認證不是閘道簽發的，或它位於閘道不讀取的標頭中                                                                                                                                                                                                                                              | 確認變數與[認證表](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-credential-variable)中的認證類型匹配，並在閘道處重新生成金鑰（如果已撤銷）                                                                                                                                                   |
| `Your apiKeyHelper script is failing`，或在非互動模式下 stderr 上的 `apiKeyHelper failed:`                                                                                                                                                                                                                                                                                                                                                                            | [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 設定中的命令未產生可用的金鑰，因此請求帶有預留位置金鑰                                                                                                                                                 | 直接執行命令以查看失敗原因，並在認證提供者報告過期會話時重新驗證；請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors#your-apikeyhelper-script-is-failing)                                                                                                                                              |
| 當沒有任何東西在地址應答時 `Connection refused — a firewall or proxy may be blocking it (ConnectionRefused)`，或當主機名無法解析時 `Can't reach the API server — check your internet or DNS (ENOTFOUND)`，通常在 Claude Code [使用退避重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)時無聲暫停後。括號中的代碼會有所不同；[Unable to connect to API](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api) 涵蓋代碼拼寫和較早的措辭 | 沒有任何東西在基礎 URL 應答：地址錯誤，或 VPN 或防火牆阻止了到閘道的路徑                                                                                                                                                                                                                    | 執行上面的 [curl 測試](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)，它立即以相同的原因失敗，並與您的閘道團隊確認 URL 和網路路徑                                                                                                                                              |
| `API returned an empty or malformed response (HTTP 200)`                                                                                                                                                                                                                                                                                                                                                                                                              | 閘道或中間代理返回了非 API 回應，通常是 HTML 錯誤或登入頁面                                                                                                                                                                                                                                 | 使用上面的 [curl 請求](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)測試；修復返回非 Claude API 回應的閘道路由。[錯誤參考](https://code.claude.com/docs/zh-TW/errors#api-returned-an-empty-or-malformed-response)解釋了訊息報告的詳細資訊                                      |
| `400` 錯誤命名 `context_management`、`Extra inputs are not permitted` 或其他無法識別的欄位                                                                                                                                                                                                                                                                                                                                                                            | 閘道將請求轉發到上游，該上游拒絕 Claude Code 發送到 Anthropic 格式端點的欄位                                                                                                                                                                                                                | 設定 `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`，它抑制大多數預發佈欄位；請參閱[功能傳遞](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#feature-pass-through)。某些 beta 不受此標誌限制；對於那些，設定匹配的 `CLAUDE_CODE_USE_*` 提供者變數，以便 Claude Code 僅發送該提供者接受的內容              |
| `400` 錯誤命名 `thinking` 或 `adaptive`，例如 `Input tag 'adaptive' found`                                                                                                                                                                                                                                                                                                                                                                                            | 上游模型構建不接受自適應推理，Claude Code 為 Claude 4.6 及更高版本的模型請求                                                                                                                                                                                                                | 升級閘道的上游。在 Opus 4.6 和 Sonnet 4.6 上，`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` 改為有效。[模型配置](https://code.claude.com/docs/zh-TW/model-config)功能變數僅適用於提供者配置（例如 `CLAUDE_CODE_USE_BEDROCK` 和 `CLAUDE_CODE_USE_VERTEX`），不在 `ANTHROPIC_BASE_URL` 閘道後面                      |
| `400` 錯誤陳述閘道自己的詞語中的上下文或令牌限制，例如 `ContextWindowExceededError` 或 `prompt token count of N exceeds the limit of M`                                                                                                                                                                                                                                                                                                                               | 閘道強制執行比模型的本機視窗更小的上下文，並重寫上游錯誤，因此 Claude Code 不會將其識別為[過長錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)，並且不會自動壓縮和重試                                                                                                   | 執行 `/compact` 以恢復會話。要防止它，請將 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 設定為閘道的限制；Claude Code 將該值限制在至少 100,000 令牌和最多模型的上下文視窗，因此您無法匹配低於 100,000 的閘道限制，`/compact` 在那裡仍然是恢復。還要將 `CLAUDE_CODE_MAX_OUTPUT_TOKENS` 設定為低於閘道模型的輸出限制        |
| `400` 錯誤在每個請求上，在閘道自己的詞語中拒絕工具的輸入架構或其 `pattern`，在 Claude Code v2.1.265 至 v2.1.267 上                                                                                                                                                                                                                                                                                                                                                    | 在這些版本上的逐步推出中，[Artifact 工具](https://code.claude.com/docs/zh-TW/artifacts#availability)架構帶有包含 `\p{...}` Unicode 字元類的正規表達式。Anthropic API 接受它，但檢查每個工具架構的 `pattern` 的閘道或上游使用自己的正規表達式引擎會拒絕整個請求                              | 更新到 v2.1.268 或更高版本，不發送正規表達式。在受影響的版本上，[關閉 artifacts](https://code.claude.com/docs/zh-TW/artifacts#disable-artifacts)，這會從請求中移除工具及其架構                                                                                                                                 |
| 模型缺失於 `/model` 選擇器                                                                                                                                                                                                                                                                                                                                                                                                                                            | 閘道模型名稱不在 Claude Code 的內置列表中，或 Claude Code 顯示替換內置選項的 [`modelPicker`](https://code.claude.com/docs/zh-TW/settings-reference#modelpicker) 陣容                                                                                                                        | 啟用[閘道模型發現](https://code.claude.com/docs/zh-TW/llm-gateway-connect#add-gateway-models-to-the-model-picker)或使用[模型配置](https://code.claude.com/docs/zh-TW/model-config)變數添加名稱。如果 Claude Code 顯示替換 `modelPicker` 陣容，請將閘道模型添加到其中，或在受管設定提供時要求您的管理員添加它們 |
| `/fast` 報告 `Fast mode unavailable due to network connectivity issues`，而推理請求有效                                                                                                                                                                                                                                                                                                                                                                               | [快速模式](https://code.claude.com/docs/zh-TW/fast-mode)可用性檢查直接進入 `api.anthropic.com`，不遵循 `ANTHROPIC_BASE_URL`，因此阻止的直接出站會導致檢查失敗。當檢查呈現來自 `ANTHROPIC_API_KEY` 或 `apiKeyHelper` 的閘道簽發的金鑰，而 Anthropic 拒絕它時，在開放網路上也會出現相同的訊息 | 如果出站被阻止，請將 `api.anthropic.com` 列入白名單，或設定跳過變數；對於被拒絕的閘道金鑰，只有跳過變數有幫助。請參閱[在代理和 LLM 閘道後面使用快速模式](https://code.claude.com/docs/zh-TW/fast-mode#use-fast-mode-behind-proxies-and-llm-gateways)                                                           |
| `/fast` 在使用 `ANTHROPIC_AUTH_TOKEN` 驗證的會話中報告 `Fast mode has been disabled by your organization`，儘管組織已啟用快速模式                                                                                                                                                                                                                                                                                                                                     | 可用性檢查需要 claude.ai 登入或 Anthropic API 金鑰；僅使用持有人令牌，Claude Code 會將快速模式視為已禁用，而不發送檢查                                                                                                                                                                      | 設定 `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1`；請參閱[在代理和 LLM 閘道後面使用快速模式](https://code.claude.com/docs/zh-TW/fast-mode#use-fast-mode-behind-proxies-and-llm-gateways)                                                                                                                           |
| Claude Code 要求您登入，儘管 [curl 測試](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)成功                                                                                                                                                                                                                                                                                                                                            | CLI 沒有自己的認證：可達的基礎 URL 不是一個，在互動會話中，專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的 `env` 區塊僅在首次執行嚮導和[信任提示](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)後應用                            | 在 Claude Code 在首次執行設定之前讀取的位置設定 `ANTHROPIC_AUTH_TOKEN`：shell 匯出、`~/.claude/settings.json` 中的 `env` 區塊或受管設定                                                                                                                                                                        |
| `ANTHROPIC_API_KEY` 已設定但被忽略，無提示                                                                                                                                                                                                                                                                                                                                                                                                                            | 金鑰在互動會話中需要一次性批准，之前拒絕的金鑰被忽略而不再詢問                                                                                                                                                                                                                              | 使用 `Use custom API key` 選項在 `/config` 下啟用它                                                                                                                                                                                                                                                            |
| `This machine's managed settings require a first-party login`                                                                                                                                                                                                                                                                                                                                                                                                         | 受管設定包括 `forceLoginMethod` 或 `forceLoginOrgUUID`，不能與 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 共存                                                                                                                                                           | 您的管理員必須從受管設定中移除 `forceLoginMethod` 和 `forceLoginOrgUUID` 以使用閘道認證，或移除閘道認證以使用第一方登入。兩者無法結合                                                                                                                                                                          |
| `403` 帶有 HTML 正文，例如 `403 Forbidden`，當閘道自己的日誌顯示未收到請求時                                                                                                                                                                                                                                                                                                                                                                                          | 閘道前面的網頁應用程式防火牆或反向代理在到達閘道之前阻止了請求正文。Claude Code 提示包括 XML 樣式標籤和與跨站點指令碼正文規則匹配的原始程式碼，因此短 curl 測試通過而實際會話不通過                                                                                                         | 豁免閘道的 `/v1/messages` 路徑免受請求正文檢查。在 AWS WAF 上，這是 `CrossSiteScripting_Body` 受管規則；在帶有 ModSecurity 的 nginx 上，它是等效的 OWASP CRS 正文規則                                                                                                                                          |
| 憑證或 TLS 錯誤，例如 `SSL certificate verification failed` 或 `Self-signed certificate detected`，當 [curl 測試](https://code.claude.com/docs/zh-TW/llm-gateway-connect#verify-the-connection)成功時                                                                                                                                                                                                                                                                 | Claude Code 的執行時不信任 `curl` 使用的相同憑證授權。在公司 TLS 檢查代理後面很常見                                                                                                                                                                                                         | 將 `NODE_EXTRA_CA_CERTS` 設定為 CA 束路徑；請參閱 [CA 憑證存儲](https://code.claude.com/docs/zh-TW/network-config#ca-certificate-store)                                                                                                                                                                        |
| 如果 Claude Code 在移除閘道配置後重複提示您登入，原因通常是認證存儲而不是閘道；請參閱[身份驗證錯誤](https://code.claude.com/docs/zh-TW/errors#authentication-errors)。                                                                                                                                                                                                                                                                                                |                                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                                                                |

## 相關資源

- [LLM 閘道概述](https://code.claude.com/docs/zh-TW/llm-gateway)：什麼是閘道以及它如何與 claude.ai 訂閱互動
- [為您的組織推出 LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway-rollout)：部署和分發閘道配置的面向管理員的檢查清單
- [閘道協議參考](https://code.claude.com/docs/zh-TW/llm-gateway-protocol)：Claude Code 發送到閘道的內容，包括閘道必須轉發的標頭和欄位
- [設定](https://code.claude.com/docs/zh-TW/settings)：設定檔案的位置以及如何讀取 `env` 區塊
- [身份驗證](https://code.claude.com/docs/zh-TW/authentication)：認證變數、`apiKeyHelper` 和 OAuth 登入如何互動

是否 助手
