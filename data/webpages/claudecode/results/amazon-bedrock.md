**Deploying Claude Code across your organization?** Talk to sales about enterprise plans, SSO, and centralized billing. [View plans](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=bedrock_view_plans#plans-business)[Contact sales ](https://claude.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=bedrock_contact_sales)

## 先決條件

在使用 Amazon Bedrock 設定 Claude Code 之前，請確保您具有：

- 已啟用 Amazon Bedrock 存取的 AWS 帳戶
- 在 Amazon Bedrock 中存取所需的 Claude 模型（例如 Claude Sonnet 4.6）
- 已安裝並設定 AWS CLI（選用 - 僅在您沒有其他取得認證機制時才需要）
- 適當的 IAM 權限

若要使用您自己的 Amazon Bedrock 認證登入，請遵循下面的[使用 Amazon Bedrock 登入](https://code.claude.com/docs/zh-TW/amazon-bedrock#sign-in-with-bedrock)。若要在整個團隊中部署 Claude Code，請使用[手動設定](https://code.claude.com/docs/zh-TW/amazon-bedrock#set-up-manually)步驟並在推出前[固定您的模型版本](https://code.claude.com/docs/zh-TW/amazon-bedrock#4-pin-model-versions)。

## 使用 Bedrock 登入

如果您有 AWS 認證資訊，並想透過 Amazon Bedrock 開始使用 Claude Code，登入精靈會引導您完成整個過程。您只需在每個帳戶上完成一次 AWS 端的先決條件；精靈會處理 Claude Code 端的設定。 1 在您的 AWS 帳戶中啟用 Anthropic 模型 在 [Amazon Bedrock 主控台](https://console.aws.amazon.com/bedrock/)中，開啟模型目錄，選擇 Anthropic 模型，並提交使用案例表單。提交後會立即授予存取權限。如需 AWS Organizations 的相關資訊，請參閱[提交使用案例詳細資訊](https://code.claude.com/docs/zh-TW/amazon-bedrock#1-submit-use-case-details)；如需您的角色所需的權限，請參閱 [IAM 設定](https://code.claude.com/docs/zh-TW/amazon-bedrock#iam-configuration)。 2 啟動 Claude Code 並選擇 Amazon Bedrock 執行 `claude`。在登入提示時，選擇**第三方平台** ，然後選擇 **Amazon Bedrock** 。如果您已經登入並看到聊天提示，請執行 `/setup-bedrock` 來開啟精靈。在設定 `CLAUDE_CODE_USE_BEDROCK=1` 之前，Claude Code [會從命令選單中隱藏該命令](https://code.claude.com/docs/zh-TW/commands#how-the-command-menu-matches-what-you-type)；請完整輸入該命令。 3 按照精靈提示進行 選擇您向 AWS 進行身份驗證的方式：從您的 `~/.aws` 目錄偵測到的 AWS 設定檔、Amazon Bedrock API 金鑰、存取金鑰和密鑰，或已在您環境中的認證資訊。精靈會要求您提供區域，驗證您的帳戶可以叫用哪些 Claude 模型，並讓您釘選它們。它會將結果儲存到您的[使用者設定檔](https://code.claude.com/docs/zh-TW/settings)的 `env` 區塊中，因此您不需要自行匯出環境變數。 登入後，您可以隨時執行 `/setup-bedrock` 來重新開啟精靈並變更您的認證資訊、區域或模型釘選。模型釘選步驟會從您目前釘選的模型開始。精靈會寫入 `~/.claude/settings.json`，或在設定 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars#variables) 時寫入 `$CLAUDE_CONFIG_DIR/settings.json`。

## 手動設定

若要透過環境變數而非精靈來設定 Amazon Bedrock（例如在 CI 或指令碼化企業推出中），請按照下列步驟進行。

### 1. 提交使用案例詳細資訊

在您首次叫用 Anthropic 模型之前，請提交使用案例詳細資訊。您每個 AWS 帳戶只需執行一次。

1. 確保您擁有下述所需的 IAM 權限
1. 前往 [Amazon Bedrock 主控台](https://console.aws.amazon.com/bedrock/)
1. 從**模型目錄** 中選取 Anthropic 模型
1. 完成使用案例表單。提交後立即授予存取權限。

如果您使用 AWS Organizations，可以使用 [`PutUseCaseForModelAccess` API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_PutUseCaseForModelAccess.html) 從管理帳戶提交表單一次。此呼叫需要 `bedrock:PutUseCaseForModelAccess` IAM 權限。核准會自動延伸至子帳戶。

### 1. 設定 AWS 認證

Claude Code 使用預設 AWS SDK 認證鏈。使用下列其中一種方法設定您的認證： **選項 A：AWS CLI 設定**

```
aws configure

```

**選項 B：環境變數（存取金鑰）**

```
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_SESSION_TOKEN=your-session-token

```

**選項 C：環境變數（SSO 設定檔）** 在執行這些命令之前，將 `your-profile-name` 替換為您的 AWS 設定檔名稱。

```
aws sso login --profile=your-profile-name

export AWS_PROFILE=your-profile-name

```

Claude Code 從設定檔的 `sso_region` 命名的 IAM Identity Center 區域要求角色認證，這不需要與您執行 Amazon Bedrock 的區域相符。在 v2.1.207 中，Amazon Bedrock 區域覆寫了 `sso_region`，因此設定檔的 IAM Identity Center 執行個體位於不同區域時，驗證失敗並出現 `Session token not found or invalid` 錯誤。 **選項 D：AWS Management Console 認證**

```
aws login

```

[深入瞭解](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html) `aws login`。 **選項 E：Amazon Bedrock API 金鑰**

```
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key

```

Amazon Bedrock API 金鑰提供更簡單的驗證方法，無需完整的 AWS 認證。[深入瞭解 Amazon Bedrock API 金鑰](https://aws.amazon.com/blogs/machine-learning/accelerate-ai-development-with-amazon-bedrock-api-keys/)。

#### 認證快取和解析逾時

Claude Code 解析 AWS 預設認證提供者鏈一次，並將解析的認證保留在記憶體中。它會重複使用這些認證，直到它們過期前五分鐘，或在沒有過期時間時使用一小時，因此 SSO 支援的設定檔大約每個認證生命週期向 IAM Identity Center 要求一次認證。來自 API 的認證錯誤會清除快取，重試會解析新認證。需要 Claude Code v2.1.207 或更新版本。 快取涵蓋上述所有認證選項，除了 Amazon Bedrock API 金鑰（不使用提供者鏈）。若要改為在每個要求上解析鏈，請設定 [`CLAUDE_CODE_SKIP_AWS_CRED_CACHE=1`](https://code.claude.com/docs/zh-TW/env-vars)。 鏈的每次解析在 60 秒後逾時。如果鏈中的步驟停滯，例如等待無法接收的輸入的 `credential_process` 協助程式，要求會失敗並出現 [`AWS default-chain credential resolve timed out`](https://code.claude.com/docs/zh-TW/errors#aws-default-chain-credential-resolve-timed-out)。如果您的鏈執行合法需要更長時間的互動式登入，例如透過 `aws-vault` 之類的包裝程式進行瀏覽器型 SSO 搭配 MFA，請使用 [`CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) 以毫秒為單位提高限制。在 v2.1.207 之前，停滯的認證解析會讓要求無限期等待。 除了使用 Amazon Bedrock API 金鑰進行驗證外，[設定精靈](https://code.claude.com/docs/zh-TW/amazon-bedrock#sign-in-with-bedrock)會對它在驗證您的認證時進行的每個 AWS 呼叫，以及在每個模型檢查之前的認證查詢應用相同的限制。在認證驗證期間，超過限制的檢查會失敗並出現 [`Timed out after 60s waiting for AWS`](https://code.claude.com/docs/zh-TW/errors#bedrock-setup-verification-timed-out-waiting-for-aws)。

#### 進階認證設定

Claude Code 支援 AWS SSO 和公司身分提供者的自動認證重新整理。將這些設定新增至您的 Claude Code 設定檔（請參閱[設定](https://code.claude.com/docs/zh-TW/settings)以了解檔案位置）。 這兩個設定有不同的觸發條件：

- **`awsAuthRefresh`**：僅在 Claude Code 偵測到您的 AWS 認證已過期時執行，可根據其時間戳記在本機偵測，或在 API 傳回認證錯誤時執行，然後使用重新整理的認證重試要求。
- **`awsCredentialExport`**：在工作階段開始和每次認證重新載入時執行，即使 AWS 預設認證提供者鏈中的認證仍然有效。當您的 Amazon Bedrock 帳戶需要與預設提供者鏈會解析的認證不同的跨帳戶認證時，請使用此選項。

在執行 `awsAuthRefresh` 命令之前，Claude Code 會進行 STS `GetCallerIdentity` 呼叫以確認您的認證確實已過期，並在認證仍然有效時略過該命令。Claude Code 透過您的[代理設定](https://code.claude.com/docs/zh-TW/network-config#proxy-configuration)傳送此檢查，遵守 `HTTPS_PROXY` 和 `NO_PROXY`。在 v2.1.239 之前，Claude Code 直接傳送此檢查，並在僅允許透過代理進行出口的網路上在啟動時掛起。

```
{
  "awsAuthRefresh": "aws sso login --profile myprofile",
  "env": {
    "AWS_PROFILE": "myprofile"
  }
}

```

**`awsAuthRefresh`**：用於修改`.aws` 目錄的命令，例如更新認證、SSO 快取或設定檔。命令的輸出會顯示給使用者，但不支援互動式輸入。這適用於瀏覽器型 SSO 流程，其中 CLI 顯示 URL 或代碼，您在瀏覽器中完成驗證。 **`awsCredentialExport`**：僅在無法修改`.aws` 且必須直接傳回認證時使用。輸出會被無聲地擷取，不會顯示給使用者。命令必須以此格式輸出 JSON：

```
{
  "Credentials": {
    "AccessKeyId": "value",
    "SecretAccessKey": "value",
    "SessionToken": "value",
    "Expiration": "2026-01-01T00:00:00Z"
  }
}

```

來自 `aws configure export-credentials --format process` 的平面輸出也被接受，其中相同的金鑰位於頂層而非巢狀在 `Credentials` 下。 `Expiration` 是選用的。當命令傳回有效的 ISO 8601 `Expiration` 時，Claude Code 會快取認證直到該時間前五分鐘。沒有它時，認證會快取一小時。 當您設定 `awsCredentialExport` 而不設定 `awsAuthRefresh` 時，Claude Code 會直接使用匯出的認證，並在啟動時不重新解析 AWS 預設認證提供者鏈。需要 Claude Code v2.1.206 或更新版本。

### 1. 設定 Claude Code

設定下列環境變數以啟用 Amazon Bedrock：

```
# 啟用 Bedrock 整合
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1  # 如果您的 AWS 設定檔已設定區域，則為選用

# 選用：覆寫小型/快速模型的 AWS 區域（Bedrock 和 Mantle）。
# 在 Bedrock 上，沒有設定 ANTHROPIC_DEFAULT_HAIKU_MODEL
# 或已棄用的 ANTHROPIC_SMALL_FAST_MODEL 時無效。
export ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION=us-west-2

# 選用：覆寫 Bedrock 端點 URL 以用於自訂端點或閘道
# export ANTHROPIC_BEDROCK_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com

```

為 Claude Code 啟用 Amazon Bedrock 時，請記住以下事項：

- 您只需設定 `AWS_REGION` 以覆寫您的 AWS 設定檔的區域，或在您的設定檔沒有區域時設定。Claude Code 按此順序解析區域：
  - `AWS_REGION`
  - `AWS_DEFAULT_REGION`
  - 在您的作用中 AWS 設定檔上設定的 `region`，首先從 AWS 共用認證檔案讀取，然後從共用設定檔讀取，符合 AWS SDK 優先順序
  - `us-east-1` 如果來自任何這些來源的值不像區域名稱，Claude Code 會將其視為未設定並繼續按順序進行。例如，Claude Code 將包含斜線、點或空格的值視為未設定。 作用中設定檔是 `AWS_PROFILE`（如果已設定），否則為 `default`。設定 `AWS_SHARED_CREDENTIALS_FILE` 或 `AWS_CONFIG_FILE` 以指向非預設檔案路徑。 執行 `/status` 以查看解析的區域。當區域來自您的 AWS 設定檔或預設後備時，Claude Code 也會在 `/status` 輸出中記錄來源。
- 使用 Amazon Bedrock 時，`/logout` 命令無法使用，因為驗證是透過 AWS 認證處理的。
- WebSearch 工具在 Amazon Bedrock 上無法使用。請參閱 [WebSearch 工具行為](https://code.claude.com/docs/zh-TW/tools-reference#websearch-tool-behavior)。
- 您可以使用設定檔來設定環境變數，例如 `AWS_PROFILE`，您不想洩漏給其他程序。請參閱[設定](https://code.claude.com/docs/zh-TW/settings)以取得更多資訊。

### 1. 釘選模型版本

部署至多個使用者時，請釘選特定模型版本。不釘選時，模型別名（例如 `sonnet` 和 `opus`）會解析為 Claude Code 對 Amazon Bedrock 的內建預設值，這可能落後最新版本，且可能在您的帳戶中尚未提供。Claude Code 在啟動時[回退](https://code.claude.com/docs/zh-TW/amazon-bedrock#startup-model-checks)至較早或較低階層的模型（當預設值無法使用時），但釘選可讓您控制使用者何時移至新模型。 將這些環境變數設定為特定 Amazon Bedrock 模型 ID。 沒有 `ANTHROPIC_DEFAULT_OPUS_MODEL` 時，Amazon Bedrock 上的 `opus` 別名解析為 Opus 5，沒有 `ANTHROPIC_DEFAULT_SONNET_MODEL` 時，`sonnet` 別名解析為 Sonnet 4.5。此範例將每個別名釘選至特定版本：

```
export ANTHROPIC_DEFAULT_OPUS_MODEL='us.anthropic.claude-opus-4-8'
export ANTHROPIC_DEFAULT_SONNET_MODEL='us.anthropic.claude-sonnet-4-6'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'

```

這些 ID 使用 `us.` 跨區域推論設定檔前置詞。如果您使用不同的區域前置詞或應用程式推論設定檔，請相應調整。在 AWS GovCloud 區域中，使用 `us-gov.` 前置詞。 若要保留內建預設模型並僅變更其偏好的前置詞，請改為設定 [`ANTHROPIC_BEDROCK_REGION_PREFIX`](https://code.claude.com/docs/zh-TW/amazon-bedrock#cross-region-inference-profile-prefixes)，而不是釘選。差異顯示在 `opus` 別名解析為的內容中：

| 您設定                                                                                                                                                                                                                                                                                             | `opus` 別名解析為                                                               |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `ANTHROPIC_DEFAULT_OPUS_MODEL='us.anthropic.claude-opus-4-8'`                                                                                                                                                                                                                                      | `us.anthropic.claude-opus-4-8`，您釘選的確切 ID                                 |
| `ANTHROPIC_BEDROCK_REGION_PREFIX=eu`                                                                                                                                                                                                                                                               | `eu.anthropic.claude-opus-5`，具有您偏好前置詞的內建預設值                      |
| 如需目前和舊版模型 ID，請參閱[模型概觀](https://platform.claude.com/docs/en/about-claude/models/overview)。如需釘選環境變數的完整清單，請參閱[模型設定](https://code.claude.com/docs/zh-TW/model-config#pin-models-for-third-party-deployments)。 未設定釘選變數時，Claude Code 使用這些預設模型： |                                                                                 |
| 模型類型                                                                                                                                                                                                                                                                                           | 預設模型                                                                        |
| ---                                                                                                                                                                                                                                                                                                | ---                                                                             |
| 主要模型                                                                                                                                                                                                                                                                                           | Opus 5，例如 `us-*` 區域中的 `us.anthropic.claude-opus-5`                       |
| 小型/快速模型                                                                                                                                                                                                                                                                                      | Sonnet 4.5，例如 `us-*` 區域中的 `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| 背景工作（例如工作階段標題產生）使用小型/快速模型，通常是 Haiku 級模型。在 Amazon Bedrock 上，Claude Code 對背景工作使用預設 Sonnet 模型，因為 Haiku 可能不會在每個帳戶或區域中啟用。兩個選項變更哪個模型執行它們：                                                                                |                                                                                 |

- 當您使用 `--model`、`ANTHROPIC_MODEL` 或 `model` 設定選取主要模型時，背景工作使用該模型。當 Claude Code 在您使用 [`ANTHROPIC_DEFAULT_MODEL`](https://code.claude.com/docs/zh-TW/model-config#set-a-default-model-for-new-sessions) 設定的模型上啟動工作階段時，背景工作也使用該模型。設定 `ANTHROPIC_DEFAULT_OPUS_MODEL` 而不設定 `ANTHROPIC_DEFAULT_SONNET_MODEL` 也算作選項，因為內建 Sonnet 模型可能在引導自己的 Opus 的帳戶中無法啟用。
- 若要對背景工作使用 Haiku，請將 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 設定為您帳戶中可用的模型 ID。

Opus 模型的每個權杖價格高於 Sonnet 模型，因此不釘選主要模型的部署在更新至 v2.1.207 或更新版本後會以 Opus 費率計費。若要將 Sonnet 4.5 保留為主要模型，請將 `ANTHROPIC_MODEL` 設定為其完整模型 ID。使用 `ANTHROPIC_DEFAULT_SONNET_MODEL` 引導預設且不設定 `ANTHROPIC_DEFAULT_OPUS_MODEL` 的部署會將其引導的 Sonnet 模型保留為預設值。 在 v2.1.207 至 v2.1.218 上，Amazon Bedrock 上的主要模型預設為 Opus 4.8，`opus` 別名解析為 Opus 4.8。在 v2.1.207 之前，主要模型預設為 Sonnet 4.5，`opus` 別名解析為 Opus 4.6，背景工作始終使用主要模型。 若要進一步自訂模型，請使用下列其中一種方法：

```
# 使用推論設定檔 ID
export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-6'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'

# 使用應用程式推論設定檔 ARN
export ANTHROPIC_MODEL='arn:aws:bedrock:us-east-2:your-account-id:application-inference-profile/your-model-id'

# 選用：如果需要，停用提示快取
# export DISABLE_PROMPT_CACHING=1

# 選用：要求 1 小時提示快取 TTL 而非 5 分鐘預設值
# export ENABLE_PROMPT_CACHING_1H=1

```

1 小時快取 TTL 的計費費率高於 5 分鐘預設值。請參閱[快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)。若要為您的主要對話和 Claude Code 在其外部進行的要求設定不同的 TTL，請[自行選擇 TTL](https://code.claude.com/docs/zh-TW/prompt-caching#choose-the-ttl-yourself)。 提示快取可能不適用於所有 Amazon Bedrock 區域。如果快取權杖計數保持為零，請檢查 Amazon Bedrock 文件中的[支援的模型、區域和限制](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-models)。

#### 將每個模型版本對應至推論設定檔

`ANTHROPIC_DEFAULT_*_MODEL` 環境變數為每個模型系列設定一個推論設定檔。如果您的組織需要在 `/model` 選擇器中公開同一系列的多個版本，每個都路由至其自己的應用程式推論設定檔 ARN，請改為在您的[設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)中使用 `modelOverrides` 設定。 此範例將四個 Opus 版本對應至不同的 ARN，以便使用者可以在它們之間切換，而無需繞過您組織的推論設定檔：

```
{
  "modelOverrides": {
    "claude-opus-4-7": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-47-prod",
    "claude-opus-4-6": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-46-prod",
    "claude-opus-4-5-20251101": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-45-prod",
    "claude-opus-4-1-20250805": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-41-prod"
  }
}

```

當使用者在 `/model` 中選取其中一個版本時，Claude Code 會使用對應的 ARN 呼叫 Amazon Bedrock。當您透過 `--model` 或 `ANTHROPIC_MODEL` 直接傳遞 Anthropic 模型 ID 時，相同的對應也適用。沒有覆寫的版本會回退至內建 Amazon Bedrock 模型 ID 或在啟動時發現的任何相符推論設定檔。在 v2.1.200 之前，`--model` 和 `ANTHROPIC_MODEL` 值會直接到達 Amazon Bedrock，而不會通過覆寫對應。請參閱[覆寫每個版本的模型 ID](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version) 以了解覆寫如何與 `availableModels` 和其他模型設定互動的詳細資訊。

## 啟動模型檢查

當 Claude Code 配置了 Amazon Bedrock 時，它會驗證其打算使用的模型在您的帳戶中是否可存取。 如果您已釘選的模型版本比 Claude Code 目前的預設版本更舊，且您的帳戶可以呼叫較新的版本，Claude Code 會提示您更新釘選。接受會將新的模型 ID 寫入您的[使用者設定檔](https://code.claude.com/docs/zh-TW/settings)並重新啟動 Claude Code。拒絕會被記住，直到下一次預設版本變更為止。指向[應用程式推論設定檔 ARN](https://code.claude.com/docs/zh-TW/amazon-bedrock#map-each-model-version-to-an-inference-profile) 的釘選會被跳過，因為這些由您的管理員管理。 如果您尚未釘選模型，且目前的預設在您的帳戶中無法使用，Claude Code 會針對目前的工作階段進行回退並顯示通知。它會先嘗試預設模型的較早版本，當預設是 Opus 模型且沒有可用的 Opus 版本時，會回退到預設的 Sonnet 模型。回退不會被保存。在您的 Amazon Bedrock 帳戶中啟用較新的模型，或[釘選一個版本](https://code.claude.com/docs/zh-TW/amazon-bedrock#4-pin-model-versions)以使選擇永久化。 當您在特定的 Sonnet 或 Opus 版本上啟動工作階段時，例如使用 `--model`、`ANTHROPIC_MODEL` 或[`model` 設定](https://code.claude.com/docs/zh-TW/settings-reference#model)，該版本會作為工作階段針對相符 `sonnet` 或 `opus` 別名的釘選預設。Claude Code 會跳過您的模型所取代之內建預設的可用性檢查，並在您設定的模型上啟動，不會有回退通知。 模型別名（例如 `opus`）不會作為釘選，Claude Code 無法識別的模型 ID（例如應用程式推論設定檔 ARN）也不會。

## 跨區域推論設定檔前綴

在 Amazon Bedrock [Invoke API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html) 上，Claude Code 會將其內建預設模型解析為[跨區域推論設定檔](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) ID；若要透過您自己的推論設定檔路由模型版本，請參閱[將每個模型版本對應至推論設定檔](https://code.claude.com/docs/zh-TW/amazon-bedrock#map-each-model-version-to-an-inference-profile)。此表格顯示 Claude Code 針對每個已解析的 AWS 區域所偏好的前綴：

| AWS 區域                                                                                                                                                                                                                                                                                                                                                                                                                                   | 前綴      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| `us-gov-*` (AWS GovCloud)                                                                                                                                                                                                                                                                                                                                                                                                                  | `us-gov.` |
| `us-*`                                                                                                                                                                                                                                                                                                                                                                                                                                     | `us.`     |
| `eu-*`                                                                                                                                                                                                                                                                                                                                                                                                                                     | `eu.`     |
| `ap-*`                                                                                                                                                                                                                                                                                                                                                                                                                                     | `apac.`   |
| 所有其他區域                                                                                                                                                                                                                                                                                                                                                                                                                               | `global.` |
| 設定 `ANTHROPIC_BEDROCK_REGION_PREFIX` 以選擇 Claude Code 優先嘗試的前綴；當 Claude Code 可以檢查設定檔可用性並找不到模型的相符設定檔時，它會按照下方解析順序進行回退。有效值為 `us`、`eu`、`apac`、`jp`、`au` 和 `global`。例如，當您的帳戶已啟用 `global.` 設定檔但 Claude Code 會根據您的 AWS 區域衍生出地理位置特定的設定檔時，請將其設定為 `global`。需要 Claude Code v2.1.224 或更新版本。 此範例透過 `global.` 設定檔路由預設模型： |           |

```
export ANTHROPIC_BEDROCK_REGION_PREFIX=global
# 在 us-* 區域中，主要模型現在解析為
# global.anthropic.claude-opus-5 而不是 us.anthropic.claude-opus-5

```

偏好的前綴是一個偏好設定，而非保證，無論它來自您的區域或來自變數。Claude Code 如何應用它取決於它是否可以檢查您帳戶中的設定檔可用性：

- 當 Claude Code 可以[列出您帳戶中的推論設定檔](https://code.claude.com/docs/zh-TW/amazon-bedrock#iam-configuration)時，它會按照此順序解析每個模型：
  1. 具有您偏好前綴的設定檔。
  1. 任何相符的設定檔，適用於沒有該前綴設定檔的模型。
  1. 具有您偏好前綴的內建模型 ID，適用於完全沒有相符設定檔的模型。Claude Code 在此步驟不檢查可用性即應用此 ID；[啟動模型檢查](https://code.claude.com/docs/zh-TW/amazon-bedrock#startup-model-checks)仍涵蓋工作階段的預設模型。
- 當設定檔探索無法使用時，Claude Code 會應用前綴而不檢查可用性。如果您的帳戶沒有啟用該前綴的推論設定檔，請求會失敗並出現 400 錯誤。

Claude Code 不會重寫您自己設定的 Amazon Bedrock 推論設定檔 ID 或 ARN，或 [`modelOverrides`](https://code.claude.com/docs/zh-TW/amazon-bedrock#map-each-model-version-to-an-inference-profile) 值；Anthropic 格式的模型 ID 會透過[與 `/model` 選擇器相同的對應](https://code.claude.com/docs/zh-TW/amazon-bedrock#map-each-model-version-to-an-inference-profile)進行解析。Claude Code 在兩種情況下也會忽略該變數：

- 在 AWS GovCloud 區域中，Claude Code 一律使用 `us-gov.`，這是在 GovCloud 分割區內路由的唯一前綴。
- 當您設定的值不是有效值之一時，Claude Code 會回退到區域衍生的偏好前綴。

## IAM 設定

建立具有 Claude Code 所需權限的 IAM 政策：

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowModelAndInferenceProfileAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles",
        "bedrock:GetInferenceProfile"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*",
        "arn:aws:bedrock:*:*:foundation-model/*"
      ]
    },
    {
      "Sid": "AllowMarketplaceSubscription",
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:ViewSubscriptions",
        "aws-marketplace:Subscribe"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:CalledViaLast": "bedrock.amazonaws.com"
        }
      }
    }
  ]
}

```

如需更嚴格的權限，您可以將資源限制為特定的推論設定檔 ARN。 `bedrock:GetInferenceProfile` 讓 Claude Code 將[應用程式推論設定檔 ARN](https://code.claude.com/docs/zh-TW/amazon-bedrock#map-each-model-version-to-an-inference-profile) 解析為其支援的基礎模型，用於為該模型選擇正確的請求形狀。 如果權杖缺少此權限，Claude Code 會透過使用替代形狀重試一次來自動復原，因此請求仍會成功，但每個新模型都會增加額外的往返。授予權限可避免重試。這最常適用於 `AWS_BEARER_TOKEN_BEDROCK` 部署，其中權杖的政策通常比完整 IAM 角色更狹隘。 如需詳細資訊，請參閱 [Amazon Bedrock IAM 文件](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)。 為 Claude Code 建立專用的 AWS 帳戶，以簡化成本追蹤和存取控制。

## 1M 權杖內容視窗

Claude Sonnet 5、Opus 4.6 及更新版本，以及 Sonnet 4.6，在 Amazon Bedrock 上支援 [1M 權杖內容視窗](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-window-sizes-by-model)。Sonnet 5 在 Invoke API 和 [Mantle 端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint)上始終以 1M 視窗執行，沒有 `[1m]` 變體可選擇。對於 Invoke API 上的其他模型，當您選取 1M 模型變體時，Claude Code 會自動啟用擴展內容視窗。 [設定精靈](https://code.claude.com/docs/zh-TW/amazon-bedrock#sign-in-with-bedrock)在固定模型時提供 1M 內容選項。若要為手動固定的模型啟用它，請在模型 ID 後附加 `[1m]`。請參閱[為第三方部署固定模型](https://code.claude.com/docs/zh-TW/model-config#pin-models-for-third-party-deployments)以取得詳細資訊。

## 服務層級

[Amazon Bedrock 服務層級](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)可讓您在成本和延遲之間進行權衡。將 `ANTHROPIC_BEDROCK_SERVICE_TIER` 設定為 `default`、`flex` 或 `priority`：

```
export ANTHROPIC_BEDROCK_SERVICE_TIER=priority

```

Claude Code 在每個請求上將此作為 `X-Amzn-Bedrock-Service-Tier` 標頭傳送。層級可用性因模型和區域而異。保留容量使用[佈建輸送量](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) ARN 作為模型 ID，而不是此設定。

## AWS Guardrails

[Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 可讓您為 Claude Code 實施內容篩選。在 [Amazon Bedrock 主控台](https://console.aws.amazon.com/bedrock/)中建立 Guardrail，發佈版本，然後將 Guardrail 標頭新增至您的[設定檔](https://code.claude.com/docs/zh-TW/settings)。如果您使用跨區域推論設定檔，請在 Guardrail 上啟用跨區域推論。 範例設定：

```
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Amzn-Bedrock-GuardrailIdentifier: your-guardrail-id\nX-Amzn-Bedrock-GuardrailVersion: 1"
  }
}

```

如果您的組織改為透過 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 政策傳遞 guardrail 標頭，它們會計為[需要核准的設定](https://code.claude.com/docs/zh-TW/server-managed-settings#environment-variables-and-the-approval-dialog)。

## 使用 Mantle 端點

Mantle 是一個 Amazon Bedrock 端點，透過原生 Anthropic API 形狀而不是 Amazon Bedrock Invoke API 提供 Claude 模型。它使用相同的 [AWS 認證](https://code.claude.com/docs/zh-TW/amazon-bedrock#2-configure-aws-credentials)、[IAM 權限](https://code.claude.com/docs/zh-TW/amazon-bedrock#iam-configuration) 和 [`awsAuthRefresh` 設定](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration)。

### 啟用 Mantle

已設定 AWS 認證後，設定 `CLAUDE_CODE_USE_MANTLE` 以將請求路由到 Mantle 端點：

```
export CLAUDE_CODE_USE_MANTLE=1
export AWS_REGION=us-east-1

```

Claude Code 從 AWS 區域構造端點 URL，並以與[上面的 Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock#3-configure-claude-code) 相同的優先順序解析。若要為自訂端點或閘道覆寫 URL，請設定 `ANTHROPIC_BEDROCK_MANTLE_BASE_URL`。 在 Claude Code 內執行 `/status` 以確認。當 Mantle 處於作用中時，提供者行會顯示 `Amazon Bedrock (Mantle)`。

### 選取 Mantle 模型

Mantle 使用以 `anthropic.` 為前綴且沒有版本尾碼的模型 ID，例如 `anthropic.claude-sonnet-5` 或 `anthropic.claude-haiku-4-5`。您的帳戶可用的模型取決於您的組織已被授予的內容；其他模型 ID 列在來自 AWS 的您的上線材料中。請聯絡您的 AWS 帳戶團隊以要求存取允許清單模型。 使用 `--model` 旗標或 Claude Code 內的 `/model` 設定模型：

```
claude --model anthropic.claude-haiku-4-5

```

### 與 Invoke API 並行執行 Mantle

您在 Mantle 上可用的模型可能不包括您今天使用的每個模型。設定 `CLAUDE_CODE_USE_BEDROCK` 和 `CLAUDE_CODE_USE_MANTLE` 可讓 Claude Code 從同一工作階段呼叫兩個端點。符合 Mantle 格式的模型 ID 會路由到 Mantle，所有其他模型 ID 會進入 Amazon Bedrock Invoke API。

```
export CLAUDE_CODE_USE_BEDROCK=1
export CLAUDE_CODE_USE_MANTLE=1

```

若要在 `/model` 選擇器中顯示 Mantle 模型，請在[設定檔](https://code.claude.com/docs/zh-TW/settings)中的 `availableModels` 中列出其 ID。此設定也會將選擇器限制為列出的項目。列出 `anthropic.claude-haiku-4-5` 會從選擇器中移除裸 `haiku` 別名，因此也請列出版本前綴或您想保持可選的版本的完整 ID。Mantle ID 和 `haiku` 別名會解析為相同的模型系列，因此合併只會保留更具體的項目。請參閱[合併行為](https://code.claude.com/docs/zh-TW/model-config#merge-behavior)：

```
{
  "availableModels": ["opus", "sonnet", "claude-haiku-4-5", "anthropic.claude-haiku-4-5"]
}

```

帶有 `anthropic.` 前綴的項目會新增為自訂選擇器選項並路由到 Mantle。將 `anthropic.claude-haiku-4-5` 替換為您的帳戶已被授予的模型 ID。請參閱[限制模型選擇](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)以了解 `availableModels` 如何與其他模型設定互動。 當兩個提供者都處於作用中時，`/status` 會顯示 `Amazon Bedrock + Amazon Bedrock (Mantle)`。

### 透過閘道路由 Mantle

如果您的組織透過集中式 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)路由模型流量，該閘道在伺服器端注入 AWS 認證，請停用用戶端驗證，以便 Claude Code 傳送沒有 SigV4 簽名或 `x-api-key` 標頭的請求：

```
export CLAUDE_CODE_USE_MANTLE=1
export CLAUDE_CODE_SKIP_MANTLE_AUTH=1
export ANTHROPIC_BEDROCK_MANTLE_BASE_URL=https://your-gateway.example.com

```

### Mantle 環境變數

這些變數特定於 Mantle 端點。請參閱[環境變數](https://code.claude.com/docs/zh-TW/env-vars)以取得完整清單。

| 變數                                    | 目的                                                   |
| --------------------------------------- | ------------------------------------------------------ |
| `CLAUDE_CODE_USE_MANTLE`                | 啟用 Mantle 端點。設定為 `1` 或 `true`。               |
| `ANTHROPIC_BEDROCK_MANTLE_BASE_URL`     | 覆寫預設 Mantle 端點 URL                               |
| `CLAUDE_CODE_SKIP_MANTLE_AUTH`          | 跳過用戶端驗證以進行代理設定                           |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | 覆寫 Haiku 級模型的 AWS 區域（與 Amazon Bedrock 共用） |

## 故障排除

### 使用 SSO 和公司代理的驗證迴圈

如果在使用 AWS SSO 時瀏覽器標籤頻繁開啟，請從您的[設定檔](https://code.claude.com/docs/zh-TW/settings)中移除 `awsAuthRefresh` 設定。這可能發生在公司 VPN 或 TLS 檢查代理中斷 SSO 瀏覽器流程時。Claude Code 將中斷的連線視為驗證失敗，重新執行 `awsAuthRefresh`，並無限迴圈。 如果您的網路環境干擾自動瀏覽器型 SSO 流程，請在啟動 Claude Code 之前手動使用 `aws sso login`，而不是依賴 `awsAuthRefresh`。

### TLS 檢查代理後的憑證錯誤

Claude Code 將您的[CA 憑證存放區](https://code.claude.com/docs/zh-TW/network-config#ca-certificate-store)設定套用至其對 AWS 的請求，包括：

- 模型探索
- 權杖計數
- 解析您的 AWS 認證的 STS 和 SSO 角色認證呼叫
- [設定精靈](https://code.claude.com/docs/zh-TW/amazon-bedrock#sign-in-with-bedrock)的認證驗證和模型檢查

對於這些請求，您的 OS 信任存放區或 `NODE_EXTRA_CA_CERTS` 套件中的公司根憑證不需要 Amazon Bedrock 特定的設定。 在 v2.1.260 之前，Claude Code 僅在這些請求通過已設定的代理時才將您的 CA 設定套用至這些請求，而在直接連線上，它們只信任執行時期的預設憑證存放區。 在 v2.1.261 之前，設定精靈的模型檢查後的認證查詢（使用**使用我環境中已有的認證** 選項）仍然只信任執行時期的預設憑證存放區。在 TLS 檢查代理後面，其根憑證僅在 OS 存放區中，受影響的請求失敗並出現 `unable to get local issuer certificate`，或精靈將模型顯示為 `unreachable`，而推論請求成功。更新至 v2.1.261 或更新版本。

### 區域問題

如果您遇到區域問題：

- 檢查模型可用性：`aws bedrock list-inference-profiles --region your-region`
- 切換至支援的區域：`export AWS_REGION=us-east-1`
- 考慮使用推論設定檔進行跨區域存取

如果您收到「不支援隨需輸送量」的錯誤：

- 將模型指定為[推論設定檔](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) ID

Claude Code 使用 Amazon Bedrock [Invoke API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html)，不支援 Converse API。

### 閘道或代理後的串流錯誤

Amazon Bedrock 以二進位事件串流格式串流 `InvokeModelWithResponseStream` 回應，標頭為 `Content-Type: application/vnd.amazon.eventstream`。Claude Code 和 Amazon Bedrock 之間的閘道或代理必須按照 Amazon Bedrock 傳送的方式轉發回應主體及其標頭，包括 `Content-Type`。 如果閘道將 `Content-Type` 改寫為另一個值，Claude Code 會拒絕回應，並出現以 `Bedrock streaming response has content-type` 開頭的錯誤，命名它收到的值。常見的改寫是 `text/event-stream`，來自將串流重新發出為伺服器發送事件的整合。 如果閘道改為刪除或清空標頭，Claude Code 會假設主體是 Amazon Bedrock 的事件串流並解碼它，因此閘道未修改地傳遞的主體會繼續串流。 如果刪除標頭的閘道也將串流重新發出為伺服器發送事件，Claude Code 無法解碼主體，並在每個回合上回退到較慢的非串流路徑：每個回應只有在完成後才會出現，而不是串流進行。在這種情況下，設定 [`CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_DEFAULT=1`](https://code.claude.com/docs/zh-TW/env-vars)，以便 Claude Code 將主體讀取為伺服器發送事件。 若要修復錯誤或回退，請配置閘道以不修改地轉發 `InvokeModelWithResponseStream` 回應主體及其 `Content-Type` 標頭。 將串流轉換為伺服器發送事件的閘道不再提供 Amazon Bedrock API。如果它也接受 Anthropic Messages API 請求，請使用 `ANTHROPIC_BASE_URL` 而不是 `CLAUDE_CODE_USE_BEDROCK` 將其連線為 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway-connect)。

### /context 中的零權杖計數

`/context` 命令透過將工具架構傳送至 Amazon Bedrock count-tokens API 來計算每個工具群組的權杖。在 Claude Code v2.1.196 之前的版本中，Amazon Bedrock 拒絕了該請求，因為架構包含其 count-tokens API 不接受的欄位，因此每個工具群組都顯示 0 個權杖。分解中的其他列（例如訊息和記憶體檔案）不受影響。 更新至 v2.1.196 或更新版本。

### Mantle 端點錯誤

如果在設定 `CLAUDE_CODE_USE_MANTLE` 後 `/status` 未顯示 `Amazon Bedrock (Mantle)`，則該變數未到達程序。確認它已在您啟動 `claude` 的 shell 中匯出，或在[設定檔](https://code.claude.com/docs/zh-TW/settings)的 `env` 區塊中設定它。 來自 Mantle 端點的 `403`（具有有效認證）表示您的 AWS 帳戶尚未被授予存取您要求的模型的權限。請聯絡您的 AWS 帳戶團隊以要求存取。 命名模型 ID 的 `400` 表示該模型未在 Mantle 上提供。Mantle 有其自己的模型陣容，與標準 Amazon Bedrock 目錄分開，因此推論設定檔 ID（例如 `us.anthropic.claude-sonnet-4-6`）將無法運作。使用 Mantle 格式的 ID，或啟用[兩個端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#run-mantle-alongside-the-invoke-api)，以便 Claude Code 將每個請求路由到模型可用的端點。

## 其他資源

- [Amazon Bedrock 文件](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock 定價](https://aws.amazon.com/bedrock/pricing/)
- [Amazon Bedrock 推論設定檔](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)
- [Amazon Bedrock 權杖燃盡和配額](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)
- [Amazon Bedrock 上的 Claude Code：快速設定指南](https://builder.aws.com/content/2tXkZKrZzlrlu0KfH8gST5Dkppq/claude-code-on-amazon-bedrock-quick-setup-guide)
- [Claude Code 監控實施 (Amazon Bedrock)](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md)

是否 助手
