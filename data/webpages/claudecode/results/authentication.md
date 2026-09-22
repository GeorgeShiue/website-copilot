Claude Code 支援多種驗證方法，具體取決於您的設定。個人使用者可以使用 claude.ai 帳戶登入，而團隊可以使用 Claude for Teams 或 Enterprise、Claude Console 或雲端提供商（如 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry）。

## 登入 Claude Code

[安裝 Claude Code](https://code.claude.com/docs/zh-TW/setup#install-claude-code) 後，在您的終端機中執行 `claude`。首次啟動時，Claude Code 會為您開啟瀏覽器視窗以供登入。如果您已設定 `ANTHROPIC_API_KEY` 環境變數，Claude Code 會略過登入提示，改為要求您核准該金鑰。 如果瀏覽器未自動開啟，請按 `c` 將登入 URL 複製到您的剪貼簿，然後將其貼到您的瀏覽器中。 如果您的瀏覽器在您登入後顯示登入代碼而不是重新導向回來，請將其貼到終端機的 `Paste code here if prompted` 提示符處。這在瀏覽器無法連接到 Claude Code 的本機回呼伺服器時發生，這在 WSL2、SSH 工作階段和容器中很常見。 登入完成時，終端機會顯示 `Login successful`，並提示您按 `Enter` 繼續。 您可以使用以下任何帳戶類型進行驗證：

- **Claude Pro 或 Max 訂閱** ：使用您的 claude.ai 帳戶登入。在 [claude.com/pricing](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=authentication_pro_max) 訂閱。
- **Claude for Teams 或 Enterprise** ：使用您的團隊管理員邀請您的 claude.ai 帳戶登入。
- **Claude Console** ：使用您的 Console 認證登入。您的管理員必須先 [邀請您](https://code.claude.com/docs/zh-TW/authentication#claude-console-authentication)。您可以在有或沒有 [建立 API 金鑰](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key) 的情況下登入。
- **雲端提供商** ：如果您的組織使用 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry)，請在執行 `claude` 之前設定所需的環境變數，或在登入提示符處選擇 **3rd-party platform** ，這會為 Bedrock 和 Vertex AI 啟動互動式設定精靈。不需要瀏覽器登入。
- **雲端閘道** ：如果您的組織執行自託管的 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)，請透過 `/login` 使用公司 SSO 登入。閘道簽發的權杖是工作階段的唯一認證。

管理員可以指示開發人員使用哪種登入方法，並要求 claude.ai 登入屬於特定組織；請參閱 [限制登入到您的組織](https://code.claude.com/docs/zh-TW/authentication#restrict-login-to-your-organization)。 若要登出並重新驗證，請在 Claude Code 提示符處輸入 `/logout`。登出也會重設您的首次啟動設定狀態，因此下次您執行 `claude` 時，它會再次引導您完成登入和設定。 如果您在登入時遇到問題，請參閱 [驗證疑難排解](https://code.claude.com/docs/zh-TW/troubleshoot-install#login-and-authentication)。

## 設定團隊驗證

對於團隊和組織，您可以透過以下方式之一配置 Claude Code 存取：

- [Claude for Teams 或 Enterprise](https://code.claude.com/docs/zh-TW/authentication#claude-for-teams-or-enterprise)，建議用於大多數團隊
- [Claude Console](https://code.claude.com/docs/zh-TW/authentication#claude-console-authentication)
- [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway)，一個自託管閘道，使用您的 IdP 簽署開發人員，並將推論路由到您配置的雲端提供商
- [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)
- [Google Cloud’s Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai)
- [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry)

### Claude for Teams 或 Enterprise

[Claude for Teams](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=authentication_teams#team-&-enterprise) 和 [Claude for Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=authentication_enterprise) 為使用 Claude Code 的組織提供最佳體驗。團隊成員可以存取 Claude Code 和網頁版 Claude，並具有集中式帳單和團隊管理。

- **Claude for Teams** ：自助服務方案，具有協作功能、管理工具和帳單管理。最適合較小的團隊。
- **Claude for Enterprise** ：新增 SSO、網域擷取、角色型權限、合規性 API 和受管原則設定，用於組織範圍的 Claude Code 配置。最適合具有安全性和合規性要求的大型組織。

1 訂閱 訂閱 [Claude for Teams](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=authentication_teams_step#team-&-enterprise) 或聯絡銷售部門以取得 [Claude for Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=authentication_enterprise_step)。 2 邀請團隊成員 從管理儀表板邀請團隊成員。 3 安裝並登入 團隊成員安裝 Claude Code 並使用其 claude.ai 帳戶登入。

### Claude Console 驗證

對於偏好基於 API 的帳單的組織，您可以透過 Claude Console 設定存取。 1 建立或使用 Console 帳戶 使用您現有的 Claude Console 帳戶或建立新帳戶。 2 新增使用者 您可以透過以下任一方法新增使用者：

- 從 Console 內大量邀請使用者：Settings -> Members -> Invite
- [設定 SSO](https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso)

3 指派角色 邀請使用者時，指派以下其中一個角色：

- **Claude Code** 角色：使用者只能建立 Claude Code API 金鑰
- **Developer** 角色：使用者可以建立任何類型的 API 金鑰

4 使用者完成設定 每個受邀使用者需要：

- 接受 Console 邀請
- [檢查系統要求](https://code.claude.com/docs/zh-TW/setup#system-requirements)
- [安裝 Claude Code](https://code.claude.com/docs/zh-TW/setup#install-claude-code)
- 使用 Console 帳戶認證登入

#### 不使用 API 金鑰登入

您可以不建立 API 金鑰而登入 Console 帳戶，即使您的組織不允許開發人員建立 API 金鑰。在 `/login` 提示時選擇 Anthropic Console 帳戶，Claude Code 會詢問您想如何登入。需要 Claude Code v2.1.242 或更新版本。兩種路由都會在瀏覽器中將您登入 Console，但在 Claude Code 之後儲存的內容不同：

- **使用您的 Console 帳戶登入** ，標記為 `(recommended)`：Claude Code 保留該登入的 OAuth 權杖，並將其儲存為 [Anthropic 設定檔](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)。它不建立 API 金鑰
- **建立 API 金鑰** ，標記為 `(legacy)`：Claude Code 為您建立 Console API 金鑰，並將其與您的其他認證一起儲存

實際上，設定檔儲存 OAuth 登入，而 API 金鑰是靜態認證：Claude Code 會自動重新整理設定檔的登入，當重新整理失敗時，請求會失敗並顯示 [Anthropic 設定檔登入已過期](https://code.claude.com/docs/zh-TW/errors#anthropic-profile-login-expired)，直到您再次登入。 您不會在每台機器上都獲得選擇。Claude Code 在以下情況下會在不詢問的情況下建立 API 金鑰：

- 您針對雲端提供商執行，例如 [Amazon Bedrock、Google Cloud’s Agent Platform 或 Microsoft Foundry](https://code.claude.com/docs/zh-TW/third-party-integrations) 或 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)
- 任何設定檔設定 [`forceLoginOrgUUID`](https://code.claude.com/docs/zh-TW/authentication#restrict-login-to-your-organization)，或將 `forceLoginMethod` 設定為 `"claudeai"` 或 `"console"`
- 您機器上存在受管設定來源（例如受管設定檔、MDM 設定檔或快取的伺服器受管設定），但 Claude Code [無法讀取它](https://code.claude.com/docs/zh-TW/managed-settings#invalid-entries-in-managed-settings)，且沒有其他受管來源提供原則

在不使用金鑰登入之前，請取消設定 `ANTHROPIC_API_KEY`。由 Claude Code 自己的 Console 登入或由 Claude Platform CLI 的 `ant auth login` 寫入的設定檔是相同類型的認證，因此再次登入會取代它。 在不使用金鑰登入後，您有一個設定檔而不是儲存的 API 金鑰：

- **它寫入的設定檔** ：Claude Code 寫入由 `ANTHROPIC_PROFILE` 命名的設定檔、您的作用中設定檔或 `default`。如果該設定檔是聯盟設定檔，Claude Code 會拒絕登入而不是覆寫它
- **它簽出的內容** ：Claude Code 簽出儲存在機器上的任何 claude.ai 登入
- **如何復原它** ：執行 `/logout`，它會移除並撤銷此登入寫入的認證

如果您的組織使用 [伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)，它們會在 Claude Code v2.1.257 或更新版本上套用到此登入。 有關設定檔的所有其他內容都適用於此登入，包括它在您其他認證中的排名、您在 `/status` 中獲得的 `Profile` 列，以及需要 claude.ai 登入的功能。請參閱 [Anthropic 設定檔和聯盟認證](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)。

### 雲端提供商驗證

對於使用 Amazon Bedrock、Google Cloud’s Agent Platform 或 Microsoft Foundry 的團隊： 1 遵循提供商設定 遵循 [Amazon Bedrock 文件](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud’s Agent Platform 文件](https://code.claude.com/docs/zh-TW/google-vertex-ai) 或 [Microsoft Foundry 文件](https://code.claude.com/docs/zh-TW/microsoft-foundry)。 2 分發配置 將環境變數和產生雲端認證的說明分發給您的使用者。深入瞭解如何 [在此管理配置](https://code.claude.com/docs/zh-TW/settings)。 3 安裝 Claude Code 使用者可以 [安裝 Claude Code](https://code.claude.com/docs/zh-TW/setup#install-claude-code)。

### 限制登入到您的組織

若要要求開發人員的 claude.ai 登入屬於特定的 Anthropic 組織，請在 [受管設定](https://code.claude.com/docs/zh-TW/managed-settings) 中設定 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 和 [`forceLoginOrgUUID`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginorguuid)。將 `forceLoginOrgUUID` 設定為您的組織 ID，該 ID 顯示在 [claude.ai 管理設定](https://claude.ai/admin-settings/organization) 中，適用於 Claude for Teams 或 Enterprise 組織。Claude Code 會針對任何其他組織的 claude.ai 登入報告錯誤，如果使用中的 claude.ai 認證屬於未列出的組織，則在啟動時退出。 對於 Claude Console 登入，Claude Code 使用 `forceLoginOrgUUID` 在您將其設定為單一 Console 組織 ID 時在 Console 登入頁面上預先選擇組織，該 ID 顯示在 [platform.claude.com/settings/organization](https://platform.claude.com/settings/organization)。它不檢查產生的 Console 認證屬於哪個組織，無論是在登入時還是在啟動時，使用 Console 帳戶登入的開發人員在您部署金鑰之前會保持登入狀態。 如果您在任何設定檔中設定 `forceLoginOrgUUID`，Claude Code 會停止在該檔案適用的工作階段中提供 [無金鑰 Console 登入](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)，並改為建立 API 金鑰。若要將開發人員導向 claude.ai 登入，請將 `forceLoginMethod` 設定為 `"claudeai"`。 開發人員可以從多個路徑登入：終端機 `/login` 流程、[VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)、Agent SDK、`claude setup-token`、`/install-github-app` 和 [閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 登入，適用於透過雲端閘道路由的組織。在 Claude Code v2.1.212 或更新版本上，每個路徑都套用 `forceLoginMethod`；在 v2.1.212 之前，只有終端機登入套用任一金鑰。在終端機的互動式登入畫面上，透過 `/login` 或首次執行上線到達，Claude Code 預先選擇 `claudeai` 或 `console` 方法而不強制執行，因此即使 `forceLoginMethod` 設定為 `"claudeai"`，開發人員仍然可以在那裡完成 Console 登入。路徑在 `forceLoginOrgUUID` 上有所不同：

- **終端機、VS Code 擴充功能和 Agent SDK 登入** ：驗證 claude.ai 帳戶登入的 `forceLoginOrgUUID`
- **`claude setup-token`和`/install-github-app`** ：僅強制執行 `forceLoginMethod`，因此它們可以在不同的組織中鑄造權杖
- **[閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 登入**：由 `forceLoginMethod: "gateway"` 選擇而不是受其限制，並且不針對 Anthropic 組織進行驗證，因此 `forceLoginOrgUUID` 不適用；使用您的閘道身分提供者來限制存取

透過您的裝置管理工具部署金鑰。[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings) 只能到達已驗證到您的組織的帳戶，因此它們無法重新導向開發人員的首次登入。如果您的組織也分發伺服器受管設定，請在兩個位置設定金鑰：受管設定來源 [不會合併](https://code.claude.com/docs/zh-TW/server-managed-settings#settings-precedence)，快取的伺服器受管設定會取代裝置受管檔案，除了幾個 [各受管來源的個別金鑰例外](https://code.claude.com/docs/zh-TW/server-managed-settings#per-key-exceptions-across-managed-sources)。`forceLoginOrgUUID` 和 `forceLoginMethod` 的 `"claudeai"` 和 `"console"` 值不在這些例外中，因此請將它們保留在兩個位置。 金鑰也決定不使用登入認證的工作階段是否可以啟動。請參閱設定參考中的 [`forceLoginOrgUUID`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginorguuid) 以了解完整行為。

- **`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper`**：在啟動時被阻止，因為無法驗證環境認證的組織成員資格
- **雲端提供商工作階段，例如 Amazon Bedrock** ：未被阻止，因為它們針對您的雲端提供商進行驗證。透過您的雲端 IAM 原則限制這些
- **[Anthropic 設定檔或聯盟認證](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)** ：未被阻止，金鑰不檢查設定檔屬於哪個組織

## 認證管理

Claude Code 安全地管理您的驗證認證：

- **儲存位置** ：
  - 在 macOS 上，認證儲存在加密的 macOS Keychain 中。當 Keychain 拒絕寫入時，例如在 SSH 工作階段中被鎖定時，Claude Code 會改為將您的登入儲存在 `~/.claude/.credentials.json` 中，檔案模式為 `0600`，這與它在 Linux 上使用的儲存方式相同。使用建立 API 金鑰的 Console 登入會失敗，直到 Keychain 可寫入。若要將您的登入移回 Keychain，請遵循[復原步驟](https://code.claude.com/docs/zh-TW/troubleshoot-install#not-logged-in-or-token-expired)。
  - 在 Linux 上，認證儲存在 `~/.claude/.credentials.json` 中，檔案模式為 `0600`。
  - 在 Windows 上，認證儲存在 `%USERPROFILE%\.claude\.credentials.json` 中，並繼承您的使用者設定檔目錄的存取控制，預設情況下將檔案限制為您的使用者帳戶。
  - 如果您設定了 `CLAUDE_CONFIG_DIR` 環境變數，Claude Code 會將 `.credentials.json` 檔案保存在該目錄下，包括 macOS 後備寫入的檔案，並將 macOS Keychain 項目也鍵入該目錄，因此具有不同 `CLAUDE_CONFIG_DIR` 的工作階段會讀取不同的項目。
  - Claude Code 透過 `/login` 和 `/logout` 管理 `.credentials.json`。若要透過自訂 API 端點路由請求，請改為設定 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數。
- **支援的驗證類型** ：claude.ai 認證、Claude API 認證、Microsoft Foundry Auth、Bedrock Auth、Vertex Auth、Anthropic 設定檔和 [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) 認證，以及 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 工作階段令牌。
- **自訂認證指令碼** ：設定 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 設定以執行傳回 API 金鑰的 shell 指令碼。
- **重新整理間隔** ：Claude Code 預設在五分鐘後重新執行 `apiKeyHelper`。設定 `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` 環境變數以自訂重新整理間隔。請參閱 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 以了解 Claude Code 重新執行協助程式的其他情況。
- **緩慢協助程式通知** ：如果 `apiKeyHelper` 花費超過 10 秒的時間傳回金鑰，Claude Code 會在提示符列中顯示警告通知，顯示經過的時間。如果您經常看到此通知，請檢查您的認證指令碼是否可以最佳化。
- **協助程式失敗** ：當指令碼以錯誤結束、逾時或不列印任何內容時，請求在三次嘗試內失敗，並顯示 [`Your apiKeyHelper script is failing`](https://code.claude.com/docs/zh-TW/errors#your-apikeyhelper-script-is-failing)。在 v2.1.208 之前，協助程式失敗會在大約十次無聲重試後顯示為通用 401。

`apiKeyHelper`、`ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 適用於 CLI 和包裝它的介面，包括 VS Code 擴充功能、Agent SDK 和 GitHub Actions。Claude Desktop 和雲端工作階段不會呼叫 `apiKeyHelper` 或讀取這些環境變數：它們使用 OAuth，除了執行[第三方推論配置](https://code.claude.com/docs/zh-TW/llm-gateway-connect#desktop-app)的桌面工作階段外，該工作階段使用該配置的認證進行驗證。

### 續約即將過期的登入

當您使用 `/login` 建立的登入在三天內即將過期時，Claude Code 會在啟動時顯示警告：`Your login expires in 3 days · run /login to renew`。需要 Claude Code v2.1.203 或更新版本。在 v2.1.217 之前，警告會在五天後出現。 執行 `/login` 以續約。警告僅供參考，永遠不會阻止請求：驗證會持續運作，直到登入實際過期。登入生命週期本身保持不變；提前警告是 v2.1.203 新增的功能。 一旦儲存的登入過期且無法重新整理，每個模型請求都會失敗，並顯示 [`Login expired · Please run /login`](https://code.claude.com/docs/zh-TW/errors#login-expired)，直到您再次登入。在 v2.1.206 之前，Claude Code 會將過期的登入報告為模型錯誤。 您可以在請求失敗之前檢查此狀態：[`/status`](https://code.claude.com/docs/zh-TW/commands) 顯示 `Login` 列讀取 `Expired — log in again`，加上它為過期登入儲存的組織和電子郵件。該列僅在儲存的 claude.ai 或 Claude Console 登入是有效認證時出現。該列需要 Claude Code v2.1.210 或更新版本。 警告僅在 claude.ai 或 Claude Console 登入是有效認證時出現，而不是在雲端提供商、`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 提供認證時出現。 對於執行無人值守的工作階段，提前續約最為重要。在[代理檢視中的背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)或[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)工作階段一旦超過登入生命週期，一旦認證過期就會停止進行，在您再次登入之前無法復原。

### 驗證優先順序

當存在多個認證時，Claude Code 按此順序選擇一個：

1. 雲端提供商認證，當設定了 `CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_VERTEX` 或 `CLAUDE_CODE_USE_FOUNDRY` 時。請參閱[第三方整合](https://code.claude.com/docs/zh-TW/third-party-integrations)以取得設定。
1. `ANTHROPIC_AUTH_TOKEN` 環境變數。作為 `Authorization: Bearer` 標頭傳送。當透過[LLM 閘道或代理](https://code.claude.com/docs/zh-TW/llm-gateway)路由時使用此選項，該閘道或代理使用持有人令牌而不是 Anthropic API 金鑰進行驗證。
1. `ANTHROPIC_API_KEY` 環境變數。作為 `X-Api-Key` 標頭傳送。用於直接 Anthropic API 存取，使用來自 [Claude Console](https://platform.claude.com) 的金鑰。在互動模式下，系統會提示您一次以核准或拒絕金鑰，您的選擇會被記住。若要稍後變更，請使用 `/config` 中的「使用自訂 API 金鑰」切換。該切換僅在 `ANTHROPIC_API_KEY` 在您的環境中設定時出現。在非互動模式 (`-p`) 中，當金鑰存在時始終使用該金鑰。
1. [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 指令碼輸出。用於動態或輪換認證，例如從保管庫擷取的短期令牌。
1. `CLAUDE_CODE_OAUTH_TOKEN` 環境變數。由 [`claude setup-token`](https://code.claude.com/docs/zh-TW/authentication#generate-a-long-lived-token) 產生的長期 OAuth 令牌。用於 CI 管道和指令碼，其中瀏覽器登入不可用。如果您在設定變數時執行 `/login`，Claude Code 會將目前工作階段切換到新登入，但會在每個新工作階段中再次讀取變數，直到您從 shell 設定檔或[設定檔](https://code.claude.com/docs/zh-TW/settings)的 `env` 區塊中移除它。
1. Anthropic 設定檔和聯盟認證，`ant` CLI 和 Workload Identity Federation 使用的認證。`ant auth login` 寫入的設定檔僅在您在 `ANTHROPIC_PROFILE` 中命名它時才排名在此處；否則它排名在 `/login` 下方。請參閱 [Anthropic 設定檔和聯盟認證](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)。
1. 來自 `/login` 的訂閱 OAuth 認證。這是 Claude Pro、Max、Team 和 Enterprise 使用者的預設值。

已簽署的 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 工作階段位於此清單之外：它是一個提供商選擇，如 Amazon Bedrock 或 Google Cloud 的 Agent Platform，並且優先於它們。當閘道工作階段存在時，CLI 使用閘道令牌進行驗證，即使設定了 `CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_VERTEX` 或 `CLAUDE_CODE_USE_FOUNDRY`，上面的持有人令牌、API 金鑰、`apiKeyHelper` 和設定檔等認證來源也不會被使用。 如果您機器的[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)將 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 設定為 `"gateway"` 或設定 [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl)，且您未透過 `CLAUDE_CODE_USE_BEDROCK` 或 `CLAUDE_CODE_USE_VERTEX` 等變數選擇雲端提供商，您的工作階段僅使用閘道登入。Claude Code 會跳過其他認證來源，並要求您使用 `/login` 登入。請參閱[系統管理員原則需要雲端閘道登入](https://code.claude.com/docs/zh-TW/errors#administrator-policy-requires-a-cloud-gateway-sign-in)以了解您在每個剩餘認證中看到的內容。在 v2.1.261 之前，或在僅設定 `forceLoginGatewayUrl` 的機器上在 v2.1.265 之前，Claude Code 會在這些機器上使用剩餘的已儲存登入，直到您登入閘道。 如果您有有效的 Claude 訂閱，但您的環境中也設定了 `ANTHROPIC_API_KEY`，則 API 金鑰在核准後優先。如果金鑰屬於已停用或過期的組織，這可能會導致驗證失敗。 執行 `unset ANTHROPIC_API_KEY` 以回退到您的訂閱，並檢查 `/status` 以確認哪種方法處於活動狀態。當登入和 API 金鑰都已設定時，`/status` 會標記未使用的認證。 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)始終使用您的訂閱認證。如果您在雲端環境中設定 `ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`，它不會覆蓋您的訂閱認證。

#### Anthropic 設定檔和聯盟認證

設定檔是您的 [Anthropic 設定目錄](https://platform.claude.com/docs/en/manage-claude/wif-reference#configuration-directory)中的具名認證設定檔，在 macOS 和 Linux 上預設為 `~/.config/anthropic`，在 Windows 上為 `%APPDATA%\Anthropic`。當您為 [Workload Identity Federation (WIF)](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) 設定設定檔時，其驗證模式為 `oidc_federation`，或當 [`ant auth login`](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/authentication) 寫入它或您[在沒有 API 金鑰的情況下登入 Console 帳戶](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)時為 `user_oauth`。 Claude Code 不會在[裸模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)、Claude Desktop 或雲端工作階段中讀取設定檔或聯盟變數。在這些工作階段中，`/status` 不顯示 `Profile` 列。 Claude Code 按此順序檢查三個來源，並在第一個設定的來源處停止。該表格顯示設定每個來源的內容以及它相對於您的 `/login` 認證的排名。

| 來源                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 設定者                                                                                                                                           | 相對於 `/login` 的排名                                                                            |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| 具名設定檔                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `ANTHROPIC_PROFILE`                                                                                                                              | 上方，無論設定檔具有什麼驗證模式                                                                  |
| 聯盟變數                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `ANTHROPIC_FEDERATION_RULE_ID` 和 `ANTHROPIC_ORGANIZATION_ID`，兩者都設定                                                                        | 上方                                                                                              |
| 有效設定檔                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 您設定目錄中的 [`active_config` 檔案](https://platform.claude.com/docs/en/manage-claude/wif-reference#active-profile)，或名為 `default` 的設定檔 | 當其驗證模式為 `oidc_federation` 時上方；當其驗證模式為 `user_oauth` 時在有效的 `/login` 認證下方 |
| `user_oauth` 規則會防止遺留的 `ant auth login` 設定檔將您的請求移出您使用 `/login` 登入的帳戶。對於聯盟變數，Claude Code 在交換您的身份令牌時也會讀取 [WIF 參考](https://platform.claude.com/docs/en/manage-claude/wif-reference#environment-variables)中的其他變數，例如 `ANTHROPIC_IDENTITY_TOKEN_FILE`。對於設定檔檔案格式，請參閱 [WIF 參考](https://platform.claude.com/docs/en/manage-claude/wif-reference#profile-configuration-file)。 若要確認 Claude Code 選擇了哪個來源，請執行 `/status`。`Profile` 列會命名來源以代替 `Login method` 列，當設定檔是使用中的認證時，`Organization` 和 `Email` 列會顯示其帳戶。 如果您使用 `--debug` 啟動 Claude Code，它也會將 `Using Anthropic profile auth` 行與來源名稱寫入 `~/.claude/debug/<session-id>.txt` 的偵錯日誌。當 Claude Code 因為您有有效的 `/login` 認證而跳過 `user_oauth` 有效設定檔時，它會向偵錯日誌寫入警告，說它改用 claude.ai 登入。 當 `user_oauth` 設定檔的登入已過期且 Claude Code 無法重新整理它時，請求會失敗，並顯示 [Anthropic profile login expired](https://code.claude.com/docs/zh-TW/errors#anthropic-profile-login-expired)。 需要您的 claude.ai 登入的功能，例如 [claude.ai connectors](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai) 和 [`/schedule`](https://code.claude.com/docs/zh-TW/routines)，在選擇這些來源之一時不可用。若要停止 Claude Code 選擇來源： |                                                                                                                                                  |                                                                                                   |

- **具名設定檔或聯盟變數** ：取消設定 `ANTHROPIC_PROFILE`，或取消設定任一聯盟變數
- **有效設定檔** ：對於您透過[在沒有 API 金鑰的情況下登入 Console 帳戶](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)寫入其目前認證的 `user_oauth` 設定檔執行 `/logout`，對於 `ant auth login` 寫入其目前認證的設定檔執行 `ant auth logout`，或對於任一驗證模式從您設定目錄中的 `configs/` 刪除設定檔的檔案

### 產生長期令牌

對於 CI 管道、指令碼或其他互動式瀏覽器登入不可用的環境，使用 `claude setup-token` 產生一年期 OAuth 令牌：

```
claude setup-token

```

該命令會開啟與 `/login` 相同的瀏覽器授權流程，在您在瀏覽器中核准存取後，令牌會列印到終端機。它不會將令牌儲存在任何地方；複製它並將其設定為您想要驗證的任何地方的 `CLAUDE_CODE_OAUTH_TOKEN` 環境變數：

```
export CLAUDE_CODE_OAUTH_TOKEN=your-token

```

此令牌使用您的 Claude 訂閱進行驗證，需要 Pro、Max、Team 或 Enterprise 方案。它只能進行模型請求，因此無法建立 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段或擷取 [claude.ai connectors](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)。您在本地設定的 MCP 伺服器仍然有效。 [裸模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)不讀取 `CLAUDE_CODE_OAUTH_TOKEN`。如果您的指令碼傳遞 `--bare`，請改用 `ANTHROPIC_API_KEY` 或 `apiKeyHelper` 進行驗證。 是否 助手
