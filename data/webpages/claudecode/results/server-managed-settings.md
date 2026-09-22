伺服器管理的設定允許組織擁有者透過 claude.ai 主控台中的 [**Admin Settings > Claude Code > Managed settings**](https://claude.ai/admin-settings/claude-code) 集中設定 Claude Code。Claude Code 用戶端在使用者使用符合條件的認證在支援伺服器管理傳遞的平台上進行身份驗證時會自動接收這些設定。請參閱[平台可用性](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)以了解符合條件的認證和平台。 伺服器管理的設定適用於 [Claude for Teams](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=server_settings_teams#team-&-enterprise) 和 [Claude for Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=server_settings_enterprise) 客戶。

## 需求

若要使用伺服器管理的設定，您需要：

- Claude for Teams 或 Claude for Enterprise 方案
- 您的 Claude 組織中的擁有者或主要擁有者角色，以檢視和編輯配置
- 對 `api.anthropic.com` 的網路存取

## 在伺服器管理和端點管理的設定之間選擇

Claude Code 支援兩種集中設定方法。伺服器管理的設定從 Anthropic 的伺服器傳遞設定。[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms) 透過原生作業系統原則 (macOS 受管偏好設定、Windows 登錄) 或受管設定檔直接部署到裝置。

| 方法                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 最適合                                  | 安全模型                                                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------------- |
| **伺服器管理的設定**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 沒有 MDM 的組織，或非受管裝置上的使用者 | Claude Code 在啟動時從 Anthropic 伺服器擷取的設定，並在工作階段期間每小時重新整理 |
| **[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 具有 MDM 或端點管理的組織               | 透過 MDM 設定檔、登錄原則或受管設定檔部署到裝置的設定                             |
| 如果您的裝置已在 MDM 或端點管理解決方案中註冊，端點管理的設定提供更強的安全保證，因為設定檔可以在作業系統層級受到保護，防止使用者修改。端點管理的設定不會到達 [雲端工作階段](https://code.claude.com/docs/zh-TW/model-config#surface-coverage) 在 Anthropic 代管的環境中，因此在網路上使用 Claude Code 的組織也應該設定伺服器管理的設定。[自我代管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) 中的工作階段也會讀取執行器映像中的受管設定檔。下面的 [設定優先順序](https://code.claude.com/docs/zh-TW/server-managed-settings#settings-precedence) 說明該檔案何時適用。 |                                         |                                                                                   |

## 設定伺服器管理的設定

1 開啟管理員主控台 在 claude.ai 主控台中，前往 [**Admin Settings > Claude Code > Managed settings**](https://claude.ai/admin-settings/claude-code)。如果連結將您重新導向至不同的 Admin Settings 頁面，而不是 Claude Code 頁面，表示您的帳戶沒有所需的角色。管理員和其他非擁有者角色無法檢視或編輯受管設定，因此請要求您組織中的擁有者或主要擁有者進行變更。請參閱[存取控制](https://code.claude.com/docs/zh-TW/server-managed-settings#access-control)。 2 定義您的設定 將您的設定新增為 JSON。支援 [`settings.json` 中提供的所有設定](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)，除了限制於作業系統層級原則傳遞的設定外；請參閱[目前的限制](https://code.claude.com/docs/zh-TW/server-managed-settings#current-limitations)以取得該簡短清單。這包括 [hooks](https://code.claude.com/docs/zh-TW/hooks)、[環境變數](https://code.claude.com/docs/zh-TW/env-vars) 和[僅限受管的設定](https://code.claude.com/docs/zh-TW/managed-settings#managed-only-settings)，例如 `allowManagedPermissionRulesOnly`。此範例強制執行權限拒絕清單，防止使用者繞過權限，並將權限規則限制為在受管設定中定義的規則。`Bash(curl *)` 規則符合 `curl` [如 Claude 所寫的](https://code.claude.com/docs/zh-TW/permissions#bash-rule-limits)，而不是 `/usr/bin/curl` 或 `sh -c 'curl …'`；對於不依賴命令文字的網路強制執行，請新增 [`sandbox` 區塊搭配 `allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/sandboxing#configure-the-sandbox-for-your-organization)。

```
{
  "permissions": {
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true
}

```

Hooks 使用與 `settings.json` 中相同的格式。此範例在整個組織中的每次檔案編輯後執行稽核指令碼：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "/usr/local/bin/audit-edit.sh" }
        ]
      }
    ]
  }
}

```

因為 hooks 執行 shell 命令，使用者在互動式工作階段中會在 Claude Code 套用它們之前看到[安全核准對話方塊](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)。若要設定 [auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 分類器，使其知道您的組織信任哪些儲存庫、儲存桶和網域，請以相同方式傳遞 `autoMode` 區塊；請參閱[設定 auto mode](https://code.claude.com/docs/zh-TW/auto-mode-config)，了解 `autoMode` 項目如何影響分類器阻止的內容，以及關於 `environment`、`allow`、`soft_deny` 和 `hard_deny` 欄位的重要警告。 3 儲存並部署 儲存您的變更。Claude Code 用戶端在下次啟動或每小時輪詢週期時會接收更新的設定。

### 驗證設定傳遞

若要確認設定正在套用，請要求使用者重新啟動 Claude Code。如果設定包含觸發[安全核准對話方塊](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)的設定，使用者會在 Claude Code 下次擷取設定時看到描述受管設定的提示：在下次啟動時，或在執行中的互動式工作階段中的一小時內。您也可以透過讓使用者執行 `/permissions` 來檢視其有效的權限規則，以驗證受管權限規則是否處於作用中。 若要檢查特定機器上的擷取結果，請讓使用者執行 `claude doctor` 並讀取 `Managed settings (remote)` 行。需要 Claude Code v2.1.248 或更新版本。該行報告以下四個結果之一：

- 已傳遞的設定已載入
- 您的組織未設定伺服器管理的設定
- 擷取失敗，包含原因以及是否仍然套用快取原則
- Claude Code 略過了擷取，包含原因。請參閱[平台可用性](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)以了解略過擷取的提供者和設定

在擷取仍在進行中時，該行會改為報告該狀態。 在執行中的工作階段中，`/status` 在擷取失敗後會顯示相同的行，對於某些略過擷取的原因（例如第三方提供者變數或使用者 shell 中匯出的自訂 `ANTHROPIC_BASE_URL`），也會顯示。

### 存取控制

以下角色可以管理伺服器管理的設定：

- **主要擁有者**
- **擁有者**

限制對受信任人員的存取，因為設定變更會套用到組織中的所有使用者。

### 僅限受管的設定

大多數[設定金鑰](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)可在任何範圍中運作。少數金鑰只能從受管設定中讀取，在放置於使用者或專案設定檔中時無效。請參閱[僅限受管的設定](https://code.claude.com/docs/zh-TW/managed-settings#managed-only-settings)以取得權限和外掛程式控制項，或讀取[所有設定](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)索引的 Scope 欄以取得完整集合。

### 目前的限制

伺服器管理的設定有以下限制：

- 設定統一套用到組織中的所有使用者。尚不支援每個群組的設定。
- 您無法透過伺服器管理的設定分發 [`managed-mcp.json`](https://code.claude.com/docs/zh-TW/managed-mcp) 檔案。改為在該處傳遞 `allowedMcpServers` 和 `deniedMcpServers` 原則金鑰。在 Claude Code v2.1.259 或更新版本上，您也可以透過 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings) 提供遠端伺服器，其僅接受 `http` 和 `sse` 伺服器，且不會以檔案的方式進行獨佔控制。 Claude Code 在其[系統路徑](https://code.claude.com/docs/zh-TW/managed-mcp#exclusive-control-with-managed-mcp-json)部署的 `managed-mcp.json` 與受管設定層級分開讀取，因此當伺服器管理的設定生效時，檔案仍然適用。
- 限制於作業系統層級原則來源的設定，例如 `policyHelper` 和 `wslInheritsWindowsSettings`，不會被接受。改為透過 MDM 或系統 `managed-settings.json` 檔案部署它們。`policyHelper` 以該方式部署時，只有在其來源是在[受管層級內的優先順序](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)下選擇的來源時，才會執行。

## 設定傳遞

### 設定優先順序

伺服器管理的設定和[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)都佔據 Claude Code [設定階層](https://code.claude.com/docs/zh-TW/settings#settings-precedence)中的最高層級。沒有其他設定層級可以覆蓋它們，包括命令列引數，除了[受管設定優先順序的例外](https://code.claude.com/docs/zh-TW/settings#exceptions-to-managed-settings-precedence)。 在受管層級內，Claude Code 預設會使用第一個傳遞至少一個原則金鑰的來源，先檢查伺服器管理的設定，然後是端點管理的設定，除了[接下來涵蓋的例外金鑰](https://code.claude.com/docs/zh-TW/server-managed-settings#per-key-exceptions-across-managed-sources)。[Claude Code 如何合併受管來源](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)有完整的排名、控制金鑰的例外，以及適用於每個來源的選擇加入。 如果選定的來源是 MDM 原則或受管設定檔，其 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 提供受管設定，則該協助程式的輸出會取代該來源，成為該執行的唯一受管設定。當伺服器管理的設定傳遞原則金鑰時，Claude Code 不會查詢在 MDM 或檔案型設定中設定的 `policyHelper`。 如果稍後的擷取發現伺服器管理的設定已移除，Claude Code 會立即執行該協助程式，而不是在下次啟動時執行。[`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 項目涵蓋該執行失敗時會發生什麼。 如果您在管理員主控台中清除伺服器管理的設定，意圖回退到端點管理的 plist 或登錄原則，請注意[快取的設定](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)會在用戶端機器上持續存在，直到下次成功擷取，而[僅在下次啟動時套用](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)的金鑰（例如 `model`）會保持有效，直到每個用戶端重新啟動。執行 `/status` 以查看哪個受管來源處於作用中。

### 跨受管來源的個別金鑰例外

三種金鑰是無合併規則的例外：

- **跨來源鎖定金鑰** ：一小組金鑰，例如沙箱允許清單鎖定，[列在受管設定頁面上](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)。當任何管理員控制的受管來源設定它們時，Claude Code 會遵守它們；使用者可寫入的 HKCU 登錄層級被排除。當 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 提供受管設定時，其輸出是這些檢查讀取的唯一來源，除了 [`forceRemoteSettingsRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#forceremotesettingsrefresh)，Claude Code 在啟動時直接從管理員來源讀取它。
- **`env`區塊** ：除了與認證金鑰配對的遙測單位和路由變數（下面涵蓋）外，它會跨管理員控制的來源按金鑰合併。對於每個環境變數，定義它的最高優先順序來源會獲勝，較低的管理員來源會填入較高來源未設定的變數。因此，端點管理的 `env` 項目會在伺服器管理的設定未設定該變數時套用，或在快取的伺服器值[等待伺服器確認時被保留](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)時套用。需要 Claude Code v2.1.223 或更新版本。在 v2.1.223 之前，Claude Code 僅套用選定來源的整個 `env` 區塊。
  - **遙測單位** ：`OTEL_EXPORTER_OTLP_*` 匯出器金鑰、`OTEL_LOG_*` 內容擷取切換、`OTEL_LOGS_EXPORTER` 以及測試版追蹤變數 `ENABLE_BETA_TRACING_DETAILED` 和 `BETA_TRACING_ENDPOINT` 遵循設定任何這些變數的最高來源作為一個單位。傳遞 `otelHeadersHelper` 認證金鑰的來源也會聲稱該單位，但僅在它是選定來源時才會放置這些變數：未被選定但傳遞該金鑰的來源不會貢獻其中任何一個，仍然會阻止較低來源填入它們。無論哪種方式，來自一個來源的匯出器端點永遠無法與來自另一個來源的認證配對。
  - **認證配對的路由** ：將路由變數與選定來源專用認證金鑰（例如 `apiKeyHelper` 或 `otelHeadersHelper`）配對的來源，僅在它贏得該位置時才會貢獻這些路由變數。
- **閘道登入金鑰** ：Claude Code 永遠不會從伺服器管理的設定讀取 [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl) 或 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 的 `"gateway"` 值，因此選擇伺服器管理的設定既不會提供閘道登入，也不會隱藏在 MDM 原則或受管設定檔中設定的登入。[`managedSourcesBehavior` 項目](https://code.claude.com/docs/zh-TW/settings-reference#managedsourcesbehavior)說明機器上的哪個管理員來源提供它們。

### 擷取和快取行為

Claude Code 在啟動時從 Anthropic 的伺服器擷取設定，並在作用中的工作階段期間每小時輪詢一次更新。 透過[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)登入的用戶端會從閘道擷取其設定，並在工作階段開始前等待該擷取，因此下面清單中的擷取不適用於它。[強制執行失敗關閉啟動](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup)涵蓋該擷取失敗時會發生什麼。 **首次啟動而無快取設定：**

- 當開發人員在啟動時登入時（例如在首次執行或 `/logout` 之後），Claude Code 會等待最多五秒鐘以進行擷取，然後才會開啟工作階段。當原則及時到達時，Claude Code 會從第一個畫面強制執行它，並在其上顯示您的 [`companyAnnouncements`](https://code.claude.com/docs/zh-TW/settings-reference#companyannouncements)。當承載需要[安全核准](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)時，Claude Code 會結束等待，並在開發人員核准後套用承載
- 在任何其他啟動中，以及當該五秒鐘等待時間用完時，Claude Code 會在擷取繼續進行時開啟工作階段，因此在設定載入和限制生效之前會經過一個簡短的視窗
- 如果擷取失敗，Claude Code 會在沒有伺服器管理的設定的情況下繼續，並在互動工作階段中警告沒有遠端原則適用；端點管理的設定仍然適用。如果受管來源設定 [`forceRemoteSettingsRefresh`](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup)，Claude Code 會改為結束

**後續啟動並有快取設定：**

- 快取設定在啟動時立即套用，除了快取的 `modelPricing` 和 `managedMcpServers` 值以及 Claude Code 保留的環境變數，直到伺服器確認承載
- 快取的 [`modelPricing`](https://code.claude.com/docs/zh-TW/settings-reference#modelpricing) 在工作階段的擷取確認承載之前不會套用。在那之前，開發人員在 `/usage` 中看到的成本數字和狀態行是列表價格
- 快取的 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 區塊在工作階段的擷取確認承載之前不會套用。Claude Code 會等待最多 30 秒鐘以進行該擷取，然後才會連接 MCP 伺服器。如果擷取失敗或逾時，工作階段會在沒有組織伺服器的情況下啟動，`/status` 會說明這一點，它們會在稍後的擷取確認它們後連接。請參閱[提供的伺服器何時連接](https://code.claude.com/docs/zh-TW/managed-mcp#when-provided-servers-connect)以了解完整行為，包括首次啟動。需要 Claude Code v2.1.259 或更新版本
- Claude Code 在背景擷取新鮮設定
- 快取設定透過網路故障持續存在。如果啟動擷取失敗，Claude Code 會在互動工作階段中警告快取原則正在生效
- 在擷取成功之前，在啟動時保留的值會保持被保留

Claude Code 會在快取的 `env` 區塊中保留多個變數類別，直到伺服器確認該工作階段的承載。這可防止快取的 Proxy、憑證授權單位、端點或認證值重新導向、攔截或重新驗證確認承載的設定擷取。強化只適用於伺服器擷取的設定快取：透過 MDM 或 `managed-settings.json` 部署的[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)不受影響。保留需要 Claude Code v2.1.198 或更新版本；在 v2.1.198 之前，整個快取的 `env` 區塊在啟動時套用。被保留的類別包括：

- Proxy 和 TLS 設定，例如 `HTTPS_PROXY`、`NODE_EXTRA_CA_CERTS` 以及 mTLS 用戶端憑證變數 `CLAUDE_CODE_CLIENT_CERT` 和 `CLAUDE_CODE_CLIENT_KEY`
- API 路由和提供者選擇，包括 `ANTHROPIC_BASE_URL`、提供者選擇變數（例如 `CLAUDE_CODE_USE_BEDROCK` 和 `CLAUDE_CODE_USE_VERTEX`）以及提供者端點 URL（例如 `ANTHROPIC_BEDROCK_BASE_URL`）
- 驗證認證，例如 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 和 `CLAUDE_CODE_OAUTH_TOKEN`
- 設定目錄選擇器 `CLAUDE_CONFIG_DIR`
- 認證來源和設定目錄選擇器，在 Claude Code v2.1.223 或更新版本中：工作負載身分識別聯盟變數（例如 `ANTHROPIC_FEDERATION_RULE_ID` 和 `ANTHROPIC_IDENTITY_TOKEN`）、設定檔和設定目錄選擇器 `ANTHROPIC_PROFILE` 和 `ANTHROPIC_CONFIG_DIR`，以及作業系統目錄變數 `HOME`、`XDG_CONFIG_HOME`、`APPDATA` 和 `USERPROFILE`

Claude Code 僅在啟動時讀取工作負載身分識別聯盟變數以及 `ANTHROPIC_PROFILE` 和 `ANTHROPIC_CONFIG_DIR` 選擇器，因此伺服器傳遞的值不會在擷取成功後切換工作階段的認證來源。若要在 Claude Code v2.1.223 或更新版本上傳遞這些選擇器，請使用[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)，例如 MDM 或 `managed-settings.json`。對於 `CLAUDE_CONFIG_DIR` 和作業系統目錄變數，保留本身就是保護：快取值會保持在環境之外，直到伺服器確認承載。 快取 `env` 區塊中的所有其他金鑰在啟動時套用。一旦伺服器確認承載，並且如果需要[安全核准](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)，您核准它，被保留的變數會在工作階段的其餘時間套用。 如果您的組織需要 Proxy 才能到達 `api.anthropic.com`，保留只會影響伺服器傳遞的 `env` 區塊本身：透過 MDM 或 `managed-settings.json` 在[端點管理的](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms) `env` 區塊中設定的 Proxy、在殼層環境中設定的 Proxy，或在[使用者設定](https://code.claude.com/docs/zh-TW/settings#where-settings-live)中設定的 Proxy 會到達設定擷取。端點管理的來源需要 Claude Code v2.1.223 或更新版本：快取的伺服器管理 Proxy 值會被保留，直到擷取確認它，因此端點管理的值按金鑰填入並到達擷取本身。在 v2.1.223 之前，請使用殼層環境或使用者設定，以便 Proxy 與快取的伺服器承載一起套用。首次啟動沒有快取，因此端點管理的來源、殼層環境或使用者設定仍然是初始擷取的必要條件。 Claude Code 會將大多數設定更新套用到執行中的工作階段，而無需重新啟動。某些更新僅在下次啟動時套用，包括 OpenTelemetry 匯出器設定、`model` 金鑰以及從 `env` 區塊移除變數。

### 傳遞設定中的無效項目

當承載的一部分無法通過結構描述驗證時，Claude Code 會顯示驗證錯誤並套用每個剩餘的有效設定；[受管設定中的無效項目](https://code.claude.com/docs/zh-TW/managed-settings#invalid-entries-in-managed-settings)說明它會捨棄什麼以及哪些金鑰會回退到更嚴格的值。需要 Claude Code v2.1.169 或更新版本。 伺服器管理的傳遞新增這些行為：

- `~/.claude/remote-settings.json` 中的快取會儲存已移除無效項目的已修復承載，除了無效的 `cleanupPeriodDays` 和 `desktopSessionCleanupPeriodDays` 值，它們會保留在快取副本中，永遠不會被套用。
- 當承載中沒有欄位可以被修復，且承載不僅是那些保留金鑰時，Claude Code 會拒絕承載、保留最後接受的快取設定，並將 `Remote settings: Settings validation failed - no fields could be salvaged` 寫入偵錯日誌。設定 `forceRemoteSettingsRefresh` 時，CLI 會改為結束。
- [安全核准對話方塊](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)會評估已修復的承載，因此被移除的無效項目永遠不會被呈現以供核准，也永遠不會執行。

若要偵錯傳遞問題，請執行 `claude --debug-file <path>` 並在日誌中搜尋 `Remote settings`。在將承載變更推出到組織之前，請在測試機器上使用 `claude doctor` 驗證承載變更。

### 強制執行失敗關閉啟動

根據預設，如果遠端設定擷取在啟動時失敗，CLI 會使用上次成功擷取時快取的設定繼續執行，但 [Claude Code 保留的值](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)除外，這些值在擷取成功之前不會套用。在從未擷取過它們的機器上，CLI 會在沒有伺服器管理的設定的情況下繼續，仍然會套用裝置上的任何[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)。 若要停止用戶端在快取或不存在的伺服器管理的設定上啟動，請在您的受管設定中設定 `forceRemoteSettingsRefresh: true`。 透過[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)登入的用戶端會等待啟動擷取，無論您是否設定此設定，並按如下方式處理失敗的擷取：

- 如果閘道以 `401` 回答有人值守的互動啟動，且此設定已關閉，閘道已結束該登入。Claude Code 會列印 [`Cloud gateway session expired — run /login to reconnect.`](https://code.claude.com/docs/zh-TW/errors#cloud-gateway-session-expired)，並開啟未登入閘道的工作階段，直到使用者執行 `/login`。
- 當擷取以任何其他方式失敗，或在除 `claude auth` 子命令之外的任何其他啟動類型中失敗時，用戶端會以錯誤結束。

當此設定在擷取伺服器管理的設定的工作階段中處於作用中時，CLI 會在啟動時阻止，直到遠端設定被新鮮擷取。如果擷取失敗，CLI 會結束而不是在沒有原則的情況下繼續。此設定會自我延續：一旦從伺服器傳遞，它也會在本機快取，以便後續啟動即使在新工作階段的第一次成功擷取之前也會強制執行相同的行為。[不擷取伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)的工作階段會在不等待的情況下啟動。 若要啟用此功能，請將金鑰新增到您的受管設定設定：

```
{
  "forceRemoteSettingsRefresh": true
}

```

您也可以在[端點管理的](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms) MDM 設定檔或系統 `managed-settings.json` 檔案中設定此金鑰，以在首次啟動時強制執行失敗關閉行為，在任何伺服器承載被傳遞之前。在 Claude Code v2.1.191 或更新版本中，此旗標是上述[優先順序規則](https://code.claude.com/docs/zh-TW/server-managed-settings#settings-precedence)的例外：當任何管理員控制的受管來源設定它時，Claude Code 會遵守它，即使快取的伺服器管理承載也存在，因此當伺服器管理的設定存在時，MDM 傳遞的值不會被忽略。 當 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 提供受管設定時，其輸出會取代 Claude Code 在啟動後讀取的金鑰的所有其他受管來源。對於 Claude Code 讀取此金鑰的來源，請參閱[其設定項目](https://code.claude.com/docs/zh-TW/settings-reference#forceremotesettingsrefresh)。`policyHelper` 項目說明 Claude Code 讀取協助程式的來源以及它何時執行。 設定擷取也會傳送 `Cache-Control: no-cache` 標頭，以便中間 HTTP Proxy 不會提供過時的回應。 在啟用此設定之前，請確保您的網路原則允許連線到 `api.anthropic.com`。如果該端點無法到達，CLI 會在啟動時結束，使用者無法啟動 Claude Code。 `claude auth` 子命令（例如 `claude auth login`）不受此檢查限制，也不受閘道啟動結束限制，因此使用者可以在過期認證是設定擷取失敗原因時重新驗證。

### 安全核准對話方塊

某些可能造成安全風險的設定需要明確的使用者核准才能在互動工作階段中套用：

- **Shell 命令設定** ：執行 shell 命令的設定，例如 `apiKeyHelper`、`statusLine` 和 `otelHeadersHelper`
- **沙箱二進位設定** ：`sandbox.bwrapPath`、`sandbox.socatPath` 和 `sandbox.ripgrep`。這些設定中的每一個都指向可執行檔，Claude Code 會執行該可執行檔
- **沙箱網路和隔離設定** ：[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)設定，讓沙箱 Proxy 讀取、重新路由或驗證流量，或削弱沙箱的隔離：`sandbox.network.tlsTerminate`、`sandbox.network.httpProxyPort`、`sandbox.network.socksProxyPort`、`sandbox.credentials`、`sandbox.allowAppleEvents`、`sandbox.enableWeakerNestedSandbox`、`sandbox.enableWeakerNetworkIsolation`、`sandbox.filesystem.disabled`、`sandbox.network.allowAllUnixSockets`、`sandbox.network.allowUnixSockets` 和 `sandbox.network.allowMachLookup`。僅包含 `deny` 規則的 `sandbox.credentials` 區塊不需要核准，因為它會限制沙箱，而不會給 Proxy 認證。在 v2.1.251 之前，Claude Code 會在沒有核准的情況下套用這些設定
- **自訂環境變數** ：傳遞的 `env` 變數，需要使用者核准，例如 Proxy 和基底 URL 變數；請參閱[環境變數和核准對話方塊](https://code.claude.com/docs/zh-TW/server-managed-settings#environment-variables-and-the-approval-dialog)
- **Hook 設定** ：任何 hook 定義

當這些設定存在時，使用者會看到安全對話方塊，說明正在設定的內容。使用者必須核准才能繼續。如果使用者拒絕設定，Claude Code 會結束。 透過 [`claudeMd`](https://code.claude.com/docs/zh-TW/settings-reference#claudemd) 金鑰傳遞的受管 CLAUDE.md 不需要核准，因為它是 Claude 的指示文字，而不是 Claude Code 執行的命令。Claude Code 仍然會檢查 Claude 在遵循這些指示時使用的工具的[權限](https://code.claude.com/docs/zh-TW/permissions)。在 v2.1.260 之前，`claudeMd` 值需要核准。

#### 核准記憶

Claude Code 會在您的設定目錄 `~/.claude` 中記錄您的核准，除非您設定 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars)。它記錄的內容取決於設定擷取使用的認證：

- **由`/login` 或 `claude auth login` 儲存的 claude.ai 登入，或[無金鑰主控台登入](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)**：每個組織一次核准，由最近核准的帳戶持有。
- **[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)登入**：每個閘道一次核准。 如果您登出並重新登入同一個閘道，Claude Code 在需要核准的設定保持不變時不會再次顯示對話方塊。當這些設定變更、您登入不同的閘道，以及當您接受同一閘道的新憑證時，Claude Code 會再次顯示它。 Claude Code 不會為透過純 HTTP 到達的迴圈開發閘道儲存任何核准，因此對話方塊會在每次登入後再次出現。
- **任何其他認證** ，例如 API 金鑰或 `CLAUDE_CODE_OAUTH_TOKEN`：一次核准傳遞的設定，與該設定目錄中設定的快取副本一起保留。當需要核准的設定變更，以及在您執行 `/logout` 或 `claude auth logout` 後（其中任何一個都會刪除快取副本），Claude Code 會再次顯示對話方塊。

`sandbox.credentials` 或 `sandbox.network.tlsTerminate` 的核准也涵蓋這些相同傳遞設定中的 [`sandbox.network.allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 項目，因為兩個設定都作用於該允許清單。當您的管理員新增或移除其中一個項目時，對話方塊會再次出現，即使 `sandbox.network.allowedDomains` 本身不需要核准。 使用已儲存的 claude.ai 登入：

- 如果您登出並重新登入，或切換到另一個組織，稍後返回，Claude Code 在這些設定保持不變時不會再次顯示對話方塊，除非另一個帳戶在同一設定目錄中為該組織核准了它們。
- 如果您使用不同的帳戶登入同一個組織，Claude Code 即使設定保持不變也會再次顯示對話方塊。該帳戶的核准會取代前一個，因此當您切換回去時，Claude Code 會再次顯示對話方塊。

Claude Code 無法總是顯示對話方塊。下面的每個案例都說明當它無法顯示時哪些設定會套用，以及您何時會再次看到對話方塊：

- **無法顯示對話方塊的互動工作階段** ：Claude Code 不會套用傳遞的設定，並保留最後核准的設定。對話方塊會在下一個可以顯示它的工作階段中出現。需要 Claude Code v2.1.211 或更新版本。
- **`claude install`或`claude update`** ：Claude Code 在任何命令期間都不會顯示對話方塊。該命令會使用最後核准的設定執行，對話方塊會在您的下一個互動工作階段中出現。如果 Claude Code 在啟動時等待設定擷取，例如設定 [`forceRemoteSettingsRefresh`](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup) 或在 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)部署上，它會改為在命令期間顯示對話方塊，並且從管道執行的安裝執行會失敗；請參閱[安裝期間的 `Raw mode is not supported`](https://code.claude.com/docs/zh-TW/troubleshoot-install#raw-mode-is-not-supported-during-install)。在 v2.1.246 之前，Claude Code 也嘗試在這些命令期間顯示對話方塊。
- **錯誤在您回答前關閉對話方塊** ：Claude Code 不會套用傳遞的設定，並保留最後核准的設定。它會在下一個可以顯示它的工作階段中再次顯示對話方塊。
- **非互動執行** ，例如 `claude -p` 或 Agent SDK 工作階段：Claude Code 無法顯示對話方塊，因此當傳遞的設定需要核准時，它僅針對該執行套用它們。它不會將它們記錄為已核准或寫入[本機快取](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)，下一個互動工作階段會顯示對話方塊。在使用者在互動工作階段中核准之前，每個非互動執行都會在啟動時再次擷取設定。在 v2.1.207 之前，非互動執行會將設定儲存為已核准，因此後來的互動工作階段永遠不會為它們顯示對話方塊。

#### 環境變數和核准對話方塊

Claude Code 會套用某些傳遞的 `env` 變數，而不會向使用者顯示核准對話方塊，包括：

- 功能和命令切換
- 模型選擇和行為設定，例如 `ANTHROPIC_MODEL`、`DISABLE_PROMPT_CACHING` 和 `CLAUDE_CODE_EFFORT_LEVEL`
- 內容視窗和壓縮設定，例如 `DISABLE_AUTO_COMPACT`
- 終端 UI 和協助工具選項
- 數值限制、預算和逾時

其他傳遞的變數可能需要使用者的核准才能生效；非空 Proxy、基底 URL 或 `OTEL_EXPORTER_OTLP_ENDPOINT` 值總是會。當傳遞的變數需要核准時，對話方塊會命名它，因此使用者會看到原則要求設定的確切內容。在 v2.1.218 之前，Claude Code 套用的變數較少而不詢問使用者，因此 `DISABLE_AUTO_COMPACT` 等設定在任何非空值時都會觸發對話方塊。 Claude Code 根據傳遞的值而不是變數名稱決定四個隱私切換是否需要核准：`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`、`DISABLE_ERROR_REPORTING`、`DISABLE_TELEMETRY` 和 `DO_NOT_TRACK`。`1` 或 `true` 等真值只會關閉追蹤、報告或其他非必要流量，因此 Claude Code 會在不詢問使用者的情況下套用它。對於任何其他非空值，Claude Code 會顯示對話方塊。在 v2.1.218 之前，除了 `DO_NOT_TRACK` 外，所有這些都在任何值時不經核准套用，`DO_NOT_TRACK` 在任何非空值時觸發對話方塊。 Claude Code 也根據傳遞的值決定 [`API_FORCE_IDLE_TIMEOUT`](https://code.claude.com/docs/zh-TW/env-vars) 是否需要核准：真值只會開啟[主體閒置逾時](https://code.claude.com/docs/zh-TW/network-config#streaming-idle-watchdogs)，因此 Claude Code 會在不詢問使用者的情況下套用它。對於任何其他非空值，Claude Code 會顯示對話方塊。在 v2.1.248 之前，任何非空值都會觸發對話方塊。 [`ANTHROPIC_CUSTOM_HEADERS`](https://code.claude.com/docs/zh-TW/env-vars#variables) 是否需要核准也取決於傳遞的值。僅標記請求的標頭（例如 `Accept-Language`）會在沒有對話方塊的情況下套用。命名認證、組織或租戶選擇器、路由或主機覆蓋，或 API 行為標頭（例如 `Authorization`、`X-Api-Key`、`Host`、`anthropic-beta` 或 `X-Amzn-Bedrock-*` 標頭）的行需要核准。命名不是有效 HTTP 標頭權杖的行，或其值包含 HTTP 標頭無法攜帶的字元的行也需要核准。檢查會符合標頭名稱內的單字，所以包含 `client` 和 `version` 的 `X-Client-Version` 也需要核准。在 v2.1.251 之前，任何 `ANTHROPIC_CUSTOM_HEADERS` 值都會在沒有核准的情況下套用。 [`ENABLE_BETA_TRACING_DETAILED`](https://code.claude.com/docs/zh-TW/env-vars#variables) 或 [`OTEL_LOG_RAW_API_BODIES`](https://code.claude.com/docs/zh-TW/env-vars#variables) 的 `0` 或 `false` 等假值會在沒有對話方塊的情況下套用，因為它只會關閉詳細追蹤或原始 API 主體擷取。任何其他非空值都需要核准。

## 平台可用性

伺服器管理的設定需要直接連線到 `api.anthropic.com`。傳遞也需要工作階段使用以下其中一個認證進行驗證：

- Team 或 Enterprise OAuth 登入
- 透過 `CLAUDE_CODE_OAUTH_TOKEN` 提供的 OAuth 權杖
- 直接配置的 API 金鑰
- 一個 `user_oauth` [Anthropic 設定檔](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)，除非設定檔設定了 `base_url` 不同於 Anthropic API。需要 Claude Code v2.1.257 或更新版本。

由 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 指令碼傳回的金鑰和[工作負載身分識別聯盟](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)認證都不會觸發設定擷取。 在 Claude Desktop 應用程式中的 [Cowork](https://claude.com/docs/cowork/overview) 工作階段中，Claude Code 不會從 claude.ai 管理員主控台擷取伺服器管理的設定，即使使用者使用 Team 或 Enterprise 帳戶登入也是如此。[原則適用的位置和時間](https://code.claude.com/docs/zh-TW/managed-settings#where-and-when-a-policy-applies)涵蓋了哪些原則會到達使用者機器上的 Cowork 工作階段和遠端 Cowork 工作階段。 如果您在殼層中匯出 `CLAUDE_CODE_USE_*` 提供者變數或非預設的 `ANTHROPIC_BASE_URL`，Claude Code 會略過您工作階段的設定擷取。[`claude doctor` 和 `/status` 報告略過的擷取及其原因](https://code.claude.com/docs/zh-TW/server-managed-settings#verify-settings-delivery)。 您無法使用伺服器管理的 `env` 區塊清除匯出，因為該區塊是透過匯出所防止的擷取來傳遞的。[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms) `env` 區塊也不會還原擷取：Claude Code 在套用管理的 `env` 區塊之前會檢查合格性，因此端點管理的值會變更工作階段的提供者選擇，但擷取仍會被略過。 若要還原伺服器管理的傳遞，請從殼層移除匯出，或在您的使用者設定 `env` 區塊中將變數設定為 `""`，這會在合格性檢查之前套用。若要在不依賴使用者變更其殼層的情況下強制執行原則，請改為透過端點管理的通道傳遞設定。 對於 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和[AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)部署，自託管的 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)提供等效的遠端管理設定傳遞：閘道登入的用戶端從閘道而不是 `api.anthropic.com` 擷取管理設定。啟動時的失敗語義不同：無法到達閘道的閘道用戶端會以錯誤結束，而不是回退到快取的設定，而每小時的背景重新整理在兩個通道上都是開放失敗的。

## 稽核記錄

設定變更的稽核記錄事件可透過合規性 API 或稽核記錄匯出取得。請聯絡您的 Anthropic 帳戶團隊以取得存取權。 稽核事件包括執行的動作類型、執行動作的帳戶和裝置，以及對先前和新值的參考。

## 安全考量

伺服器管理的設定提供集中式原則強制執行，但它們作為用戶端控制運作，而非安全邊界。在非受管裝置上，使用者不需要管理員或 sudo 存取權就能略過它們。

| 情況                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 行為                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 使用者編輯快取的設定檔                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 篡改的檔案在啟動時套用，但 Claude Code 會[保留某些值](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)直到伺服器確認承載。下次伺服器擷取會還原正確的設定，但[只在下次啟動時套用的金鑰](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)（例如 `model` 或新增至 `env` 區塊的變數）會保持有效，直到重新啟動                                                                                                                                                                                                                                                                                                                                                    |
| 使用者刪除快取的設定檔                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | [首次啟動行為](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)發生                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 使用者執行修改過的 Claude Code 二進位檔                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 能夠執行修改過用戶端的使用者可以略過任何用戶端控制                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 使用者執行較舊的 Claude Code 版本                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 早於伺服器管理設定的版本不會擷取或套用它們                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| API 無法使用                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 如果可用，快取設定會套用，但 Claude Code 會[保留某些值](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)直到擷取成功。沒有快取的情況下，Claude Code 在下次成功擷取之前不會強制執行任何伺服器管理的設定，但仍會在裝置上套用任何[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)。使用 `forceRemoteSettingsRefresh: true` 時，CLI 會結束而不是繼續，但 [`claude auth` 子命令](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup)除外。透過[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)登入的用戶端在啟動時會結束而沒有該設定，具有相同的 `claude auth` 豁免 |
| 使用者使用不同的組織進行身份驗證                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 不會為受管組織外的帳戶傳遞設定                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 使用者設定[第三方模型提供者](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 伺服器管理的設定會被略過。這包括設定 `CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_MANTLE`、`CLAUDE_CODE_USE_VERTEX`、`CLAUDE_CODE_USE_FOUNDRY`、`CLAUDE_CODE_USE_ANTHROPIC_AWS` 或非預設的 `ANTHROPIC_BASE_URL`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 網路流量被攔截或重新導向                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 停用的 TLS 驗證或攔截的流量可以改變用戶端接收的設定                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 若要記錄本機設定檔的編輯，包括 `managed-settings.json`，請使用 [`ConfigChange` hooks](https://code.claude.com/docs/zh-TW/hooks#configchange)。當伺服器管理的設定到達或重新整理時，或當 MDM 設定檔或登錄原則變更時，Claude Code 不會執行它們，且 hook 無法阻止 `policy_settings` 變更。 若要限制使用者可以使用用戶端提供的認證存取的組織，請參閱 Claude 說明中心中的[使用租戶限制強制執行網路層級存取控制](https://support.claude.com/en/articles/13198485-enforce-network-level-access-control-with-tenant-restrictions)。如需更強的強制執行保證，請在已在 MDM 解決方案中註冊的裝置上使用[端點管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)。 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

## 另請參閱

用於管理 Claude Code 設定的相關頁面：

- [所有設定](https://code.claude.com/docs/zh-TW/settings-reference)：每個設定鍵
- [Endpoint-managed settings](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)：由 IT 部門部署到裝置的受管設定
- [Authentication](https://code.claude.com/docs/zh-TW/authentication)：設定使用者對 Claude Code 的存取
- [Security](https://code.claude.com/docs/zh-TW/security)：安全保護措施和最佳實踐

是否 助手
