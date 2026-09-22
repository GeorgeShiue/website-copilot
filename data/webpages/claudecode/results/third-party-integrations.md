組織可以直接通過 Anthropic 或通過雲端提供商部署 Claude Code。本頁面幫助您選擇正確的配置。 **Deploying Claude Code across your organization?** Talk to sales about enterprise plans, SSO, and centralized billing. [View plans](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=third_party_overview_view_plans#plans-business)[Contact sales ](https://claude.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=third_party_overview_contact_sales)

## 比較部署選項

對於大多數組織，Claude for Teams 或 Claude for Enterprise 提供最佳體驗。團隊成員可以通過單一訂閱同時存取 Claude Code 和網頁版 Claude，具有集中計費和無需基礎設施設置的優勢。 **Claude for Teams** 是自助服務，包括協作功能、管理工具和計費管理。最適合需要快速開始的較小團隊。 **Claude for Enterprise** 增加了 SSO 和域名捕獲、基於角色的權限、合規性 API 存取和託管策略設置，用於部署組織範圍的 Claude Code 配置。最適合具有安全和合規性要求的大型組織。 了解更多關於 [Team 計劃](https://support.claude.com/en/articles/9266767-what-is-the-team-plan) 和 [Enterprise 計劃](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan)。 部署選項的比較涵蓋模型推理執行的位置。若要在您的組織運營的計算上執行 [Claude Code 網頁版](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 工作階段，請參閱 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)。 如果您的組織有特定的基礎設施要求，請比較以下選項：

| 功能                                                                                                                                              | Claude for Teams/Enterprise                                       | Anthropic Console                                                                                                        | Amazon Bedrock                                                                            | Claude Platform on AWS                   | Google Cloud’s Agent Platform，前身為 Vertex AI                                        | Microsoft Foundry                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 最適合                                                                                                                                            | 大多數組織（推薦）                                                | 個人開發者                                                                                                               | AWS 原生部署                                                                              | AWS Marketplace 計費搭配 Claude API 功能 | GCP 原生部署                                                                           | Azure 原生部署                                                                                         |
| 計費                                                                                                                                              | **Teams：** $150/座位（Premium）提供 PAYG                         |                                                                                                                          |                                                                                           |                                          |                                                                                        |                                                                                                        |
| **Enterprise：** [聯絡銷售](https://claude.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=third_party_enterprise)           | PAYG                                                              | 通過 AWS 的 PAYG                                                                                                         | 通過 AWS Marketplace 的 PAYG                                                              | 通過 GCP 的 PAYG                         | 通過 Azure 的 PAYG                                                                     |                                                                                                        |
| 地區                                                                                                                                              | 支援的 [國家/地區](https://www.anthropic.com/supported-countries) | 支援的 [國家/地區](https://www.anthropic.com/supported-countries)                                                        | 多個 AWS [地區](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) | 多個 AWS 地區                            | 多個 GCP [地區](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations) | 多個 Azure [地區](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/) |
| Prompt caching                                                                                                                                    | 預設啟用                                                          | 預設啟用                                                                                                                 | 預設啟用                                                                                  | 預設啟用                                 | 預設啟用                                                                               | 預設啟用                                                                                               |
| 身份驗證                                                                                                                                          | claude.ai SSO 或電子郵件                                          | API 金鑰或 [Console 登入（無需 API 金鑰）](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key) | API 金鑰或 AWS 認證                                                                       | API 金鑰或 AWS 認證                      | GCP 認證                                                                               | API 金鑰或 Microsoft Entra ID                                                                          |
| 成本追蹤                                                                                                                                          | 使用儀表板                                                        | 使用儀表板                                                                                                               | AWS Cost Explorer                                                                         | AWS Cost Explorer                        | GCP Billing                                                                            | Azure Cost Management                                                                                  |
| 包括網頁版 Claude                                                                                                                                 | 是                                                                | 否                                                                                                                       | 否                                                                                        | 否                                       | 否                                                                                     | 否                                                                                                     |
| 企業功能                                                                                                                                          | 團隊管理、SSO、使用監控                                           | 無                                                                                                                       | IAM 策略、CloudTrail                                                                      | IAM 策略、CloudTrail                     | IAM 角色、Cloud Audit Logs                                                             | RBAC 策略、Azure Monitor                                                                               |
| 如需了解每個選項上可用功能的逐項細目，請參閱 [功能可用性](https://code.claude.com/docs/zh-TW/feature-availability)。 選擇部署選項以查看設置說明： |                                                                   |                                                                                                                          |                                                                                           |                                          |                                                                                        |                                                                                                        |

- [Claude for Teams 或 Enterprise](https://code.claude.com/docs/zh-TW/authentication#claude-for-teams-or-enterprise)
- [Anthropic Console](https://code.claude.com/docs/zh-TW/authentication#claude-console-authentication)
- [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)，一個自託管閘道，在 Amazon Bedrock、Claude Platform on AWS、Google Cloud’s Agent Platform、Microsoft Foundry 或 Anthropic API 前面添加 IdP 登入
- [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)
- [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)
- [Google Cloud’s Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai)
- [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry)

對於 Amazon Bedrock 和 Google Vertex AI，您也可以執行 `claude` 並在登入提示時選擇 **3rd-party platform** 以啟動互動式設置精靈。

## 配置代理和網關

大多數組織可以直接使用雲端提供商，無需額外配置。但是，如果您的組織有特定的網路或管理要求，您可能需要配置公司代理或 LLM 網關。這些是可以一起使用的不同配置：

- **公司代理** ：通過 HTTP/HTTPS 代理路由流量。如果您的組織要求所有出站流量都通過代理伺服器以進行安全監控、合規性或網路策略執行，請使用此選項。使用 `HTTPS_PROXY` 或 `HTTP_PROXY` 環境變數進行配置。在 [企業網路配置](https://code.claude.com/docs/zh-TW/network-config) 中了解更多。
- **LLM 網關** ：位於 Claude Code 和雲端提供商之間的服務，用於處理身份驗證和路由。如果您需要跨團隊的集中使用追蹤、自訂速率限制或預算，或集中身份驗證管理，請使用此選項。使用 `ANTHROPIC_BASE_URL`、`ANTHROPIC_BEDROCK_BASE_URL`、`ANTHROPIC_AWS_BASE_URL`、`ANTHROPIC_VERTEX_BASE_URL` 或 `ANTHROPIC_FOUNDRY_BASE_URL` 環境變數進行配置。在 [LLM 網關](https://code.claude.com/docs/zh-TW/llm-gateway) 中了解更多。

如需針對每個提供商的環境變數，以透過 LLM 網關路由 Amazon Bedrock、Microsoft Foundry 或 Google Cloud 的 Agent Platform，請參閱 [透過網關路由到雲端提供商](https://code.claude.com/docs/zh-TW/llm-gateway-connect#route-to-a-cloud-provider-through-a-gateway)。在 Claude Code 中執行 `/status` 以驗證工作階段使用的提供商、基礎 URL 和代理。 如果您的組織使用 [客戶管理的加密金鑰](https://platform.claude.com/docs/en/manage-claude/cmek) (CMEK)，並透過 LLM 網關或自訂 `ANTHROPIC_BASE_URL` 路由 Claude Code，CMEK 不適用於這些工作階段上 Claude Code 的操作遙測。若要為每位開發人員關閉遙測，請透過受管設定傳遞 `DISABLE_TELEMETRY`，如 [為您的組織關閉遙測](https://code.claude.com/docs/zh-TW/managed-settings#turn-telemetry-off-for-your-organization) 中所示。

## 組織的最佳實踐

### 投資於文件和記憶

我們強烈建議投資於文件，以便 Claude Code 能夠理解您的程式碼庫。組織可以在多個層級部署 CLAUDE.md 檔案。請參閱[CLAUDE.md 檔案可以存放的位置](https://code.claude.com/docs/zh-TW/memory#choose-where-to-put-claude-md-files)和[如何部署組織範圍的 CLAUDE.md](https://code.claude.com/docs/zh-TW/memory#deploy-organization-wide-claude-md)。

### 簡化部署

如果您有自訂開發環境，我們發現建立「一鍵」安裝 Claude Code 的方式是在組織中推動採用的關鍵。

### 從引導式使用開始

鼓勵新使用者嘗試使用 Claude Code 進行程式碼庫問答，或用於較小的錯誤修復或功能請求。要求 Claude Code 制定計畫。檢查 Claude 的建議，如果偏離軌道，請提供回饋。隨著時間推移，當使用者更好地理解這種新範例時，他們將更有效地讓 Claude Code 以更多代理方式運行。

### 為雲端提供商固定模型版本

如果您透過 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai)、[Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 或 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 進行部署，請使用 `ANTHROPIC_DEFAULT_FABLE_MODEL`、`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL` 和 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 固定特定模型版本。如果不固定，模型別名會解析為 Claude Code 針對該提供商的內建預設值，這可能會滯後於最新版本，且可能尚未在您的帳戶中啟用。固定版本可讓您控制使用者何時移至新模型。請參閱[模型設定](https://code.claude.com/docs/zh-TW/model-config#pin-models-for-third-party-deployments)，瞭解當預設值不可用時每個提供商的做法。

### 設定安全性原則

安全團隊可以設定受管權限，以決定 Claude Code 允許和不允許執行的操作，這些權限無法被本機設定覆寫。[瞭解更多](https://code.claude.com/docs/zh-TW/security)。

### 使用 MCP 進行整合

MCP 是為 Claude Code 提供更多資訊的絕佳方式，例如連接到票證管理系統或錯誤日誌。我們建議由一個中央團隊設定 MCP 伺服器，並將 `.mcp.json` 設定檔簽入程式碼庫，以便所有使用者受益。[瞭解更多](https://code.claude.com/docs/zh-TW/mcp)。

## 後續步驟

選擇部署選項並為您的團隊配置存取權限後：

1. **向您的團隊推出** ：分享安裝說明，並讓團隊成員 [安裝 Claude Code](https://code.claude.com/docs/zh-TW/setup) 並使用其認證進行身份驗證。
1. **設置共享配置** ：在您的存儲庫中建立 [CLAUDE.md 文件](https://code.claude.com/docs/zh-TW/memory)，以幫助 Claude Code 理解您的程式碼庫和編碼標準。
1. **配置權限** ：查看 [安全設置](https://code.claude.com/docs/zh-TW/security)，以定義 Claude Code 在您的環境中可以和不能執行的操作。

是否 助手
