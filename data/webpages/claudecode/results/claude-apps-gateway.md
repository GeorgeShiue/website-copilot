Claude 應用程式閘道是為必須或偏好透過自己的雲端提供商路由推論的組織而設計的，例如為了滿足[資料駐留](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#compliance-posture)要求。如果您沒有此要求，並且想要存取其他功能，例如 SCIM 佈建或 Claude Code 網頁和行動版本，Claude Enterprise 可能更適合。請參閱[功能可用性](https://code.claude.com/docs/zh-TW/feature-availability)頁面，以取得所有部署方法的完整比較。 Claude 應用程式閘道是一個自託管服務，位於開發人員的 Claude Code 用戶端和模型提供商之間。開發人員使用您的企業身份提供商 (IdP) 登入，而不是持有 API 金鑰或雲端認證。閘道持有上游認證，按 IdP 群組強制執行模型存取和[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)，並將使用情況遙測轉發到您自己的可觀測性堆疊。 它包含在 `claude` 二進位檔中，因此在筆記型電腦上執行 Claude Code 的相同可執行檔可以使用 `claude gateway --config gateway.yaml` 執行閘道伺服器。 本頁涵蓋：

- [為什麼使用 Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway#why-claude-apps-gateway)、它相比自行執行增加了什麼，以及何時其他解決方案更合適
- 一個[快速入門](https://code.claude.com/docs/zh-TW/claude-apps-gateway#quickstart)，包含[先決條件](https://code.claude.com/docs/zh-TW/claude-apps-gateway#prerequisites)，可將閘道從零開始設定為已登入的開發人員
- [連接開發人員](https://code.claude.com/docs/zh-TW/claude-apps-gateway#connect-developers)，包括透過受管設定設定閘道 URL
- [可用性和限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway#availability-and-limitations)，涵蓋哪些 Claude Code 功能可透過閘道運作，以及伺服器支援什麼

相關頁面會更深入地介紹。[配置參考](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config)涵蓋快速入門寫入的 YAML 檔案中的每個選項，[部署指南](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy)涵蓋每個 IdP 的設定、Kubernetes 和 Cloud Run 部署，以及操作。

## 為什麼使用 Claude 應用程式閘道

[閘道概述](https://code.claude.com/docs/zh-TW/gateways)涵蓋閘道的功能以及為什麼要執行一個。Claude 應用程式閘道是 Anthropic 自己的閘道，內建於 `claude` 二進位檔中，並與每個 Claude Code 版本一起測試，因此它轉發 Claude Code 發送的標頭和請求欄位，無需操作員維護單獨的允許清單。部署後，它為您提供：

- **認證** ：上游 API 金鑰或雲端認證僅存在於您的基礎設施中。開發人員使用公司 SSO 進行身份驗證並接收短期的持有人令牌，因此離職發生在您的 IdP 中。取消佈建使用者，其閘道存取在會話生命週期內過期，預設為一小時。
- **存取控制** ：您的 IdP 群組對應到模型允許清單和[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)原則。閘道在伺服器端強制執行模型存取，拒絕非授予模型的請求，並選擇每個群組的受管設定原則，CLI 在[受管設定層級](https://code.claude.com/docs/zh-TW/settings#settings-precedence)應用該原則。不同的團隊獲得不同的模型、工具和權限，開發人員無法覆蓋其原則鎖定的內容。
- **設定傳遞** ：閘道本身將受管設定傳遞給已登入的用戶端，取代來自 claude.ai 管理員主控台的[伺服器管理設定](https://code.claude.com/docs/zh-TW/server-managed-settings)。
- **遙測** ：每個配置的目的地接收[OpenTelemetry Protocol (OTLP) 指標](https://code.claude.com/docs/zh-TW/monitoring-usage)，預設包含令牌計數、模型、使用者身份和延遲，日誌和追蹤作為按目的地的選擇加入。
- **上游路由** ：用戶端向閘道說 Anthropic Messages API，閘道為每個上游進行轉換，無論是 Amazon Bedrock、[AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)、Google Cloud 的 Agent Platform、Microsoft Foundry 或 Anthropic API，並在它們之間進行故障轉移。您可以更改區域、提供商或故障轉移順序，而開發人員無需注意或重新配置。

![圖表顯示 Claude Code 用戶端和 Claude Desktop 的 Chat、Cowork 和 Code 標籤透過 HTTPS 和持有人令牌連接到您基礎設施內的自託管 Claude 應用程式閘道，該閘道針對您的 IdP 簽署使用者，在 PostgreSQL 中儲存身份驗證狀態，將遙測轉發到您的 OTLP 收集器，並將推理轉發到 Amazon Bedrock、AWS 上的 Claude Platform、Google Cloud、Microsoft Foundry 或 Anthropic API](https://mintcdn.com/claude-code/VbyXug8hBU9UK6oT/images/claude-gateway-architecture.svg?fit=max&auto=format&n=VbyXug8hBU9UK6oT&q=85&s=9e4f1190fc56718144190a3db61c63af)
閘道自己的資料平面不會向 Anthropic 基礎設施發送任何內容，除非 Anthropic API 是配置的上游。您控制遙測、稽核日誌、受管設定和開發人員的 IdP 身份去向，閘道不會將它們中的任何一個發送給 Anthropic。對於其餘流量，CLI 程序可以發送什麼以及如何關閉它，請參閱[合規性態勢](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#compliance-posture)。 有關哪些 Claude Code 功能可透過閘道運作以及伺服器本身支援什麼，請參閱下面的[可用性和限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway#availability-and-limitations)。有關成本、繞過、執行多個閘道和無伺服器平台等決策，請參閱[部署指南](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#deployment)。

### 其他閘道實現

如果您已經執行滿足您需求的 LLM 閘道或 API 閘道，請繼續使用它；[其他 LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)涵蓋針對它配置 Claude Code。 [閘道相容性指南](https://code.claude.com/docs/zh-TW/llm-gateway-protocol)記錄了 Claude Code 期望從任何閘道的內容：它呼叫的端點、要轉發的標頭和正文欄位，以及當它們被剝離時停止運作的內容。執行中的 Claude 應用程式閘道也在 `GET /protocol` 提供其自己的協議參考，其中描述了它向 Claude Code 用戶端公開的端點：SSO 登入、推理、受管設定傳遞、模型探索和遙測。使用 `curl https://claude-gateway.internal.example.com/protocol` 從任何部署的閘道（例如下面[快速入門](https://code.claude.com/docs/zh-TW/claude-apps-gateway#quickstart)產生的閘道）獲取它。協議的重大變更會提前宣佈，但不保證無限期的向後相容性。

## 快速入門

此快速入門走最小路徑：在您的 IdP 中註冊 OAuth 用戶端，寫入 `gateway.yaml`，使用 Docker Compose 與 Postgres 一起執行閘道，並驗證端到端登入。它使用 Amazon Bedrock 上游；Claude Platform on AWS、Google Cloud 的 Agent Platform、Microsoft Foundry 和 Anthropic API 同樣受支援，只需如[配置參考](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)所示交換 `upstreams` 區塊。最後，您有一個開發人員可以 `/login` 的閘道。 **在您的私有網路上部署。** Claude Code 只連接到地址為私有的閘道。這是一個安全防護，因為受信任的閘道可以推送在開發人員機器上執行命令的設定。將閘道放在內部負載平衡器或 VPN 後面，並給它一個只解析為私有 IP 的主機名。如果您的內部網路是從您的組織擁有的公開 IPv4 空間編號的，請參閱[允許閘道在您擁有的公開地址空間上](https://code.claude.com/docs/zh-TW/claude-apps-gateway#allow-a-gateway-on-public-address-space-you-own)。

### 先決條件

在開始之前，請準備好以下內容：

| 您需要                           | 詳細資訊                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code v2.1.195 或更新版本  | `claude gateway` 子命令和閘道登入流程在 v2.1.195 中發布。較早的公開版本不包含它們。執行閘道伺服器的機器和每個開發人員的機器都必須是 v2.1.195 或更新版本；執行 `claude update` 以取得最新版本。[Claude Platform on AWS 上游](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-platform-on-aws)在閘道伺服器上需要 Claude Code v2.1.198 或更新版本。                                                                                                                                                                                                                                                                                         |
| OpenID Connect (OIDC) 身份提供商 | Okta、Microsoft Entra ID、Google Workspace、Keycloak 或 Dex，或任何其他符合 OIDC 的 IdP，例如 PingFederate。閘道針對它執行標準 OIDC 發現和授權碼流程。不支援 SAML 和 LDAP。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| PostgreSQL 14 或更新版本         | 支援裝置登入流程，其中瀏覽器回呼寫入，輪詢 CLI 讀取，加上速率限制計數器。任何受管 Postgres 都可以，包括最小層級。在未配置支出限制的情況下，閘道儲存幾 KB 的短期身份驗證狀態；使用[支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)，它還持有應備份的耐久支出、稽核和身份表。建議透過 `?sslmode=require` 使用 TLS。                                                                                                                                                                                                                                                                                                              |
| 模型上游                         | Amazon Bedrock 認證、Claude Platform on AWS 認證、Google Cloud 認證、Microsoft Foundry 資源或 Anthropic API 金鑰。支援多個上游和故障轉移。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| HTTPS                            | 閘道必須可從開發人員筆記型電腦和用於登入的任何瀏覽器透過 `https://` 到達；閘道在同一監聽器上提供裝置驗證頁面。透過 `listen.tls` 提供 TLS 憑證，或在 TLS 終止入口後執行並設定 `listen.public_url` 為外部來源（兩種情況下都是如此）。純 `http://` 來源僅在閘道主機為環回時接受：`localhost`、`127.0.0.1` 或 `::1`。                                                                                                                                                                                                                                                                                                                                             |
| 私有網路地址                     | 在 `/login` 處，Claude Code 要求閘道的主機名或 IP 地址僅解析為私有地址：RFC 1918、連結本地、CGNAT `100.64.0.0/10`、IPv6 ULA `fc00::/7` 或環回。對於您託管的閘道，任何公開地址都會被拒絕；請參閱部署指南中的[威脅模型](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#threat-model-summary)。如果開發人員機器透過公司代理路由 HTTPS，登入還要求代理主機解析為私有地址；如果不是，將閘道主機新增到 `NO_PROXY`，以便 CLI 直接連接。如果您的內部網路是從您的組織擁有的公開 IPv4 空間編號的，[宣告這些區塊](https://code.claude.com/docs/zh-TW/claude-apps-gateway#allow-a-gateway-on-public-address-space-you-own)，以便 `/login` 接受那裡的閘道。 |
| Linux 執行時                     | 閘道伺服器僅在原生 Linux 二進位檔上執行。macOS 適用於本地開發。Windows 不支援作為伺服器平台。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

### 步驟

1 在您的 IdP 中註冊 OAuth 用戶端 首先決定閘道的主機名，因為重定向 URI 必須與其匹配。建立新的 OIDC Web 應用程式，並將重定向 URI 設定為 `https://claude-gateway.<your-domain>/oauth/callback`，其中主機是您在步驟 3 中設定為 [`listen.public_url`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#listen) 的相同值。記下 `client_id` 和 `client_secret`。每個 IdP 的說明在[身份提供商設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#identity-provider-setup)中。 2 佈建 PostgreSQL 資料庫 任何 Postgres 14 或更新版本都可以，包括最小受管層級。閘道在啟動時執行自己的架構遷移，因此資料庫角色需要建立和更改表的權限；請參閱 [`store`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#store)。 3 寫入 gateway.yaml 機密透過 `${ENV_VAR}` 擴展讀取，因此檔案本身可以存在於版本控制中。使用在您的網路上解析為私有 IP 的 `public_url` 主機名，因為 `/login` 拒絕公開地址。最小配置有五個部分，其他每個欄位都有預設值： gateway.yaml

```
listen:
  host: 0.0.0.0
  port: 8080
  # 除非主機是環回地址，否則為必需。用於 IdP
  # redirect_uri 和發現文件。
  public_url: https://claude-gateway.internal.example.com

oidc:
  issuer: https://login.example.com        # 必須提供 /.well-known/openid-configuration
  client_id: 0oa1example2
  client_secret: ${OIDC_CLIENT_SECRET}
  allowed_email_domains: [example.com]        # 拒絕組織外的 id_tokens
  userinfo_fallback: true                  # 對於 id_token 省略電子郵件/群組的 IdP；否則無害

session:
  jwt_secret: ${GATEWAY_JWT_SECRET}        # openssl rand -base64 32
  ttl_hours: 1                             # 也限制 IdP 取消佈建時的撤銷延遲

store:
  postgres_url: ${GATEWAY_POSTGRES_URL}    # 為受管 Postgres 新增 ?sslmode=require

upstreams:
  - provider: bedrock
    region: us-east-1
    auth: {} # 空：AWS 預設認證鏈
# (IRSA、EC2/ECS 任務角色、環境變數、~/.aws)

# 模型會自動按上游轉換。內建目錄
# 將 claude-opus-4-8 對應到 us.anthropic.claude-opus-4-8 等，適用於每個
# Bedrock 支援的 Claude 模型。設定為 false 並新增 `models:` 清單以
# 僅公開特定模型。
auto_include_builtin_models: true

```

此配置足以使用預設 Amazon Bedrock 模型目錄進行有效的登入迴圈。執行後，透過 [`managed.policies`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed) 新增按群組 RBAC 和受管設定、透過 [`telemetry`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry) 的遙測扇出，以及多上游故障轉移、佈建輸送量 ARN 或非美國區域，透過 [`models`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models)。 Amazon Bedrock 上游需要一個 AWS 主體，具有 `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream` 在 `inference-profile/us.anthropic.*` ARN 和基礎 `foundation-model/anthropic.*` ARN 上。它也需要 Anthropic 的一次性使用案例表單從 Bedrock 主控台的模型目錄提交給帳戶。透過 EKS 上的 IRSA、ECS 任務角色或 EC2 執行個體設定檔提供認證，而不是靜態金鑰。[`upstreams` 參考](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)具有完整的 IAM 詳細資訊、跨雲認證矩陣和其他提供商的 `auth` 區塊。 4 執行它 圍繞滿足[映像要求](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#container-image)的 `claude` 二進位檔建立容器映像，然後與 Postgres 一起執行它。Compose 檔案將映像參考為 `registry.example.com/claude-gateway:2.1.198`；替換您自己的登錄和映像標籤： docker-compose.yaml

```
services:
  gateway:
    image: registry.example.com/claude-gateway:2.1.198
    ports: ["8080:8080"]
    volumes: ["./gateway.yaml:/etc/claude/gateway.yaml:ro"]
    environment:
      OIDC_CLIENT_SECRET: ${OIDC_CLIENT_SECRET}
      GATEWAY_JWT_SECRET: ${GATEWAY_JWT_SECRET}
      GATEWAY_POSTGRES_URL: postgres://gw:pw@postgres/gateway
      # AWS 認證：在生產中，省略這些並使用執行個體
      # 角色。對於本地 Compose 測試，傳遞您自己的：
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_SESSION_TOKEN: ${AWS_SESSION_TOKEN}
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    image: postgres:16-alpine
    environment: { POSTGRES_USER: gw, POSTGRES_PASSWORD: pw, POSTGRES_DB: gateway }
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gw"]
      interval: 5s
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes: { pgdata: }

```

閘道是一個單一 Linux 二進位檔，讀取配置，連接到 Postgres 並應用其架構遷移，針對您的 IdP 執行 OIDC 發現，建立上游用戶端，並開始監聽。啟動對配置、Postgres 連接（5 秒超時）、OIDC 發現和上游用戶端構造是失敗關閉的。如果其中任何一個無法到達或配置錯誤，閘道會以錯誤退出，而不是以降級狀態提供流量。成功啟動不驗證推理路徑，因為 Amazon Bedrock 和 Google Cloud 的 Agent Platform 執行個體認證在第一個請求時解析，而不是在啟動時。監視 stderr 以了解啟動序列。日誌行使用格式 `[gateway] <timestamp> <level> <message>`，稽核事件是帶有 `evt` 欄位的單行 JSON，啟動橫幅（下面省略）在遷移和監聽行之間列印。新資料庫為每個架構遷移列印一個 `migration N applied` 行；已遷移的資料庫不列印任何行。您應該按順序看到：

```
{"ts":"2026-06-10T17:03:21.114Z","evt":"config.load","path":"/etc/claude/gateway.yaml","sha256":"…"}
[gateway] 2026-06-10T17:03:21.395Z info waiting for migration lock (another replica may be migrating; check pg_locks for key 6775156 if this persists)
[gateway] 2026-06-10T17:03:21.408Z info migration 1 applied
…
[gateway] 2026-06-10T17:03:21.431Z info migration 6 applied
[gateway] 2026-06-10T17:03:21.512Z info claude gateway listening on http://0.0.0.0:8080

```

閘道也會記錄一個警告，`access_control.allow_cidrs` 為空。這在這裡是預期的，因為在您設定允許清單之前，沒有任何東西限制閘道提供的用戶端地址。[`access_control` 參考](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#http-tuning)具有建議的範圍。如果啟動在 `claude gateway listening on` 行之前退出，stderr 的最後一行命名問題：

- 無法到達的 Postgres
- 沒有 DDL 權限的 Postgres 角色
- 無法到達或無效的 OIDC 發現文件
- 配置架構違規，帶有違規欄位路徑

修復它並重新啟動。如果您已經有 TLS 終止入口，請跳過 Compose 並直接使用 `claude gateway --config gateway.yaml` 執行二進位檔。將 `public_url` 設定為入口來源，並將 `listen` 綁定到環回或叢集內部地址。 5 驗證身份驗證表面 三個檢查確認閘道可以在將其交給開發人員之前驗證真實使用者。示例使用閘道的公開 URL；對於沒有入口的本地 Compose 設定，在前兩個檢查中替換 `http://localhost:8080`。第三個檢查開啟 `verification_uri_complete`，它從 `public_url` 建立，因此對於本地 Compose，在 `gateway.yaml` 中設定 `public_url: http://localhost:8080`，並在步驟 1 的 OAuth 用戶端上新增 `http://localhost:8080/oauth/callback` 作為第二個重定向 URI，因為閘道從 `public_url` 建立 IdP `redirect_uri`。驗證連結然後在您的本地瀏覽器中開啟。在 Windows PowerShell 中，執行 `curl.exe`；裸 `curl` 是 `Invoke-WebRequest` 的別名，拒絕這些標誌。首先，獲取發現文件，確認閘道已啟動、配置有效且所有啟動檢查已通過：

```
curl -s https://claude-gateway.internal.example.com/.well-known/oauth-authorization-server | jq

```

```
{
  "issuer": "https://claude-gateway.internal.example.com",
  "device_authorization_endpoint": "…/oauth/device_authorization",
  "token_endpoint": "…/oauth/token",
  "grant_types_supported": ["urn:ietf:params:oauth:grant-type:device_code", "refresh_token"]
}

```

回應包括其他欄位，例如 `response_types_supported` 和 `scopes_supported`。其次，請求裝置授權，確認裝置登入流程有效且 Postgres 可到達且可寫：

```
curl -s -X POST https://claude-gateway.internal.example.com/oauth/device_authorization | jq

```

```
{
  "device_code": "…",
  "user_code": "WDJB-MJHT",
  "verification_uri": "https://claude-gateway.internal.example.com/device",
  "verification_uri_complete": "https://claude-gateway.internal.example.com/device?user_code=WDJB-MJHT",
  "expires_in": 600,
  "interval": 5
}

```

第三，透過在瀏覽器中開啟 `verification_uri_complete` 並確認代碼來測試瀏覽器部分。您應該被重定向到您的 IdP 的登入頁面，登入後，返回閘道並顯示已登入確認。使用第一個失敗的檢查來定位問題：

- **第一個檢查失敗** ：啟動未完成；檢查 stderr
- **第二個檢查失敗** ：Postgres 無法從閘道到達或角色無法寫入；檢查連接字串和授予
- **第三個檢查無法到達 IdP** ：檢查 IdP 的重定向 URI 是否完全符合 `https://<gateway>/oauth/callback`
- **第三個檢查到達 IdP 但以錯誤反彈** ：讀取閘道的稽核日誌，它記錄每個身份驗證拒絕及其原因，例如 `email domain not allowed`

6 登入開發人員 最後一步發生在開發人員機器上，而不是伺服器上。在該機器的[受管設定檔](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)中將 `forceLoginMethod` 設定為 `"gateway"` 並將 `forceLoginGatewayUrl` 設定為您的閘道的 `public_url`，然後執行 `/login`，在**雲端閘道** 螢幕上按 Enter，並完成瀏覽器登入。下面的[設定閘道 URL](https://code.claude.com/docs/zh-TW/claude-apps-gateway#set-the-gateway-url) 涵蓋大規模分發兩個金鑰。

## 連接開發人員

開發人員從自己的筆記型電腦使用一次瀏覽器登入進行連接，使用他們的公司工作帳戶。他們不需要 claude.ai 帳戶、API 金鑰或訂閱，因為對模型的請求透過使用組織上游認證的閘道進行。連接由您透過 MDM 推送的[用戶端側受管設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#client-side-managed-settings)驅動，因此開發人員端沒有手動設定；本節涵蓋管理員配置的內容。 CLI 在首次連接時對閘道的 TLS 葉憑證進行指紋識別，並按主機名固定它。它在登入期間、無聲會話重新整理期間和受管設定擷取期間再次檢查該固定，而推論請求使用標準 TLS 驗證而不使用固定。透過 HTTPS Proxy 路由的請求會跳過固定檢查，因此將閘道主機新增至 `NO_PROXY` 以保持它們直接。 發佈預期的 SHA-256 指紋以及閘道 URL，以便開發人員有可比較的內容。`/login` 提示顯示指紋的前 16 個字元作為小寫十六進位，無冒號。若要從憑證檔案以該形式列印完整指紋，請執行：

```
openssl x509 -noout -fingerprint -sha256 -in cert.pem | cut -d= -f2 | tr -d : | tr 'A-F' 'a-f'

```

當憑證輪換時，每個開發人員都會再次看到信任提示，因此將輪換視為計劃事件並重新發佈指紋。如果您的閘道原則包含[需要批准的設定](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)，開發人員在接受新憑證後也會再次看到該批准對話，因為 Claude Code 會將[批准記憶](https://code.claude.com/docs/zh-TW/server-managed-settings#approval-memory)金鑰設定為固定的憑證。 開發人員登入後，[模型選擇器](https://code.claude.com/docs/zh-TW/model-config)顯示其 `availableModels` 允許清單中的模型。受管設定在啟動時應用並每小時重新整理一次，遙測路由到您的收集器。 會話在 `ttl_hours` 過期前無聲重新整理。當 IdP 取消佈建後重新整理失敗時，Claude Code 會提示開發人員再次登入。

### 設定閘道 URL

三個金鑰進入您透過 MDM 或直接在磁碟上部署的每個 OS [受管設定檔](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)。`forceLoginMethod` 和 `forceLoginGatewayUrl` 在**雲端閘道** 螢幕上直接開啟 `/login`，URL 已填入，而 `parentSettingsBehavior: "merge"` 讓 Claude Desktop 將閘道的出口允許清單傳遞給它啟動的 Claude Code 會話，詳見[將原則傳遞給 Claude Desktop 會話](https://code.claude.com/docs/zh-TW/claude-apps-gateway#deliver-policy-to-claude-desktop-sessions)：

```
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com",
  "parentSettingsBehavior": "merge"
}

```

開發人員按 Enter 進行連接。[首次連接 TLS 指紋提示](https://code.claude.com/docs/zh-TW/claude-apps-gateway#connect-developers)仍然出現。一旦檔案在機器上，未完成閘道登入的開發人員會看到[管理員原則要求雲端閘道登入](https://code.claude.com/docs/zh-TW/errors#administrator-policy-requires-a-cloud-gateway-sign-in)下所述的其中一則訊息。透過環境變數（例如 `CLAUDE_CODE_USE_BEDROCK`）選擇雲端提供商的開發人員不需要閘道登入。 開發人員無法手動設定此項。登入選擇器中沒有閘道選項，`forceLoginGatewayUrl` 在開發人員自己的設定檔中被忽略。`forceLoginMethod` 單獨，沒有 URL，將開發人員留在「聯絡您的 IT 管理員」訊息處。登入金鑰應該在您推送到機器的檔案中，而不是在閘道的 `managed.policies[].cli` 區塊中，該區塊僅到達已連接的用戶端。

### 允許公開位址空間上的閘道

某些組織從他們擁有的公開 IPv4 區塊（例如電信業者自己的位址空間或舊版 `/8`）對其內部網路進行編號，因此他們的閘道無法擁有私人位址。在 `gatewayInternalNetworks` 受管設定中列出這些區塊。`/login` 然後在開發人員的機器從同一區塊內的位址連接到它時，接受位於列出區塊內的閘道。這需要開發人員機器上的 Claude Code v2.1.268 或更新版本；較早的版本忽略該金鑰並應用私人位址規則。 `gatewayInternalNetworks` 適用於恰好從公開位址空間編號的內部網路。它不會使將閘道暴露到網際網路變得安全：受信任的閘道可以推送在開發人員機器上執行命令的設定。使用您的防火牆或負載平衡器規則將閘道保持在網路外無法到達。將閘道的 [`access_control.allow_cidrs`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#http-tuning) 設定為您在此宣告的相同區塊，以便閘道本身拒絕來自其他任何地方的用戶端。在負載平衡器或入口後面，也將 `listen.trusted_proxies` 設定為該前端，因為閘道否則會根據前端自己的位址而不是開發人員的位址來匹配 `allow_cidrs`。 將金鑰新增至與登入金鑰相同的受管設定來源：受管設定檔、MDM 設定檔或登錄原則。Claude Code 在使用者、專案和伺服器受管設定中忽略它。 此範例宣告一個區塊。將 `203.0.113.0/24` 替換為您自己的區塊。它是文件範圍，Claude Code 拒絕這些。

```
{
  "gatewayInternalNetworks": ["203.0.113.0/24"]
}

```

Claude Code 在 `/login` 驗證清單，然後才聯絡任何閘道：

- 每個項目是一個 IPv4 區塊，寫成其第一個位址和 `/8` 到 `/32` 的前綴。
- 清單最多包含四個區塊，沒有兩個重疊。
- 沒有區塊與私人位址空間重疊：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`、`127.0.0.0/8`、`169.254.0.0/16` 和 `100.64.0.0/10`。`/login` 已經在沒有此金鑰的情況下接受那裡的閘道。
- 沒有區塊與永遠不是組織網路的空間重疊：`198.18.0.0/15` 和 `192.0.0.0/24`，VPN 和 NAT64 用戶端將其作為本地位址；文件範圍 `192.0.2.0/24`、`198.51.100.0/24` 和 `203.0.113.0/24`；以及保留範圍 `0.0.0.0/8`、`192.88.99.0/24` 和多播 `224.0.0.0/4`。您可以在 `240.0.0.0/4` 內宣告區塊，某些大型網路將其用作內部單播空間。

來自 `managed-settings.json` 及其 `managed-settings.d/` 插入檔案的區塊合併為一個清單，這些限制適用於合併清單。若要縮小區塊，請替換其項目而不是在插入中新增第二個重疊的；`/login` 拒絕重疊。 如果項目違反規則，或值不是字串清單，Claude Code 在該機器上拒絕每個新的閘道登入並在訊息中命名問題。登入到私人位址上的閘道也會失敗，現有登入保持有效。在部署前在一台機器上嘗試該值。Claude Code 也在它報告的[無效受管設定](https://code.claude.com/docs/zh-TW/managed-settings#keys-that-fail-closed)中列出錯誤類型的值。 使用有效清單，`/login` 對位址位於列出區塊內的閘道應用三個檢查：

- 閘道主機名解析到的每個位址都位於該一個區塊內。Claude Code 拒絕也在其外有記錄的名稱，包括私人和 IPv6 位址。
- 開發人員的機器從同一區塊內連接。Claude Code 拒絕 NAT 後面、容器或 WSL2 內或其位址池位於區塊外的 VPN 上的機器，並命名機器連接的位址。
- 連接是直接的。如果 `HTTPS_PROXY` 適用於閘道主機，`/login` 拒絕並命名要新增的 `NO_PROXY` 項目。

當所有三個通過時，[信任提示](https://code.claude.com/docs/zh-TW/claude-apps-gateway#connect-developers)新增一行命名機器的位址、閘道的位址和包含兩者的宣告區塊。 該金鑰對其他閘道不改變任何內容：登入到私人位址上的閘道像以前一樣有效，登入到每個列出區塊外的公開位址上的閘道像以前一樣被拒絕。 宣告的區塊縮小誰可以登入但不證明機器在哪裡，因此僅宣告您的組織控制的位址空間。與其他租戶共享的區塊（例如雲端提供商的公開範圍）讓其中的任何人通過相同的檢查。

### 將原則傳遞給 Claude Desktop 會話

Claude Desktop 在嵌入式 Claude Code 會話上執行其 Cowork 和 Code 標籤，以及當您啟用它時的 Chat 標籤，並透過閘道傳送其模型請求。它將原則傳遞給每個會話，從閘道在 `/user/bootstrap` 提供的配置建立：模型允許清單、禁用的工具，以及從匹配原則的 `cli` 區塊衍生的出口允許清單，加上[`desktop` 覆蓋](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay)。 其他 `cli` 金鑰，例如 hooks、`env` 和範圍權限規則（如 `Bash(npm *)`），僅到達透過 `/login` 登入的用戶端。Claude Desktop 從其自己的受管配置讀取閘道 URL，並使用其自己的流程登入，與[設定閘道 URL](https://code.claude.com/docs/zh-TW/claude-apps-gateway#set-the-gateway-url) 中的 `forceLoginMethod` 和 `forceLoginGatewayUrl` 金鑰分開。 由啟動程序傳遞的設定是父設定。Claude Code 在任何具有管理員部署的受管來源的機器上忽略父設定，除非[傳遞原則的來源](https://code.claude.com/docs/zh-TW/managed-settings#which-managed-source-claude-code-uses)設定 `parentSettingsBehavior: "merge"`。

#### 哪些機器需要選擇加入

僅執行 Claude Desktop 的機器需要它。Claude Desktop 將模型清單和禁用工具清單應用於嵌入式會話本身，但出口允許清單僅作為父設定到達它們，形式為 `WebFetch` 網域規則和沙箱網路規則。沒有選擇加入，這些會話執行時沒有出口限制，沒有任何警告。閘道仍然拒絕原則不授予的模型的推論請求。 開發人員透過 `/login` 登入的機器不需要它；每個 Claude Code 會話從閘道擷取其原則。 其[`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper)提供受管設定的機隊無法使用它：Claude Code 在這些機隊上永遠不會合併父設定，因為它僅從助手的輸出讀取受管設定。

#### 設定選擇加入

從[設定閘道 URL](https://code.claude.com/docs/zh-TW/claude-apps-gateway#set-the-gateway-url) 部署受管設定片段，將其鏡像到任何優先於檔案的用戶端側來源，然後驗證。 1 在受管設定檔中部署選擇加入 上面的[片段](https://code.claude.com/docs/zh-TW/claude-apps-gateway#set-the-gateway-url)已經包含 `parentSettingsBehavior: "merge"`，因此您推送到機器的檔案攜帶它。 2 將片段鏡像到任何優先於檔案的來源 Claude Code 僅從[選定的來源](https://code.claude.com/docs/zh-TW/managed-settings#which-managed-source-claude-code-uses)讀取 `parentSettingsBehavior`。將任何原則金鑰新增至來源可以使該來源成為選定的來源，因此在用戶端側來源中，鏡像整個片段而不僅僅是 `parentSettingsBehavior`。[用戶端側受管設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#client-side-managed-settings)涵蓋透過群組原則或配置設定檔傳遞原則的機隊。macOS 上的受管偏好設定 plist 或 Windows 上的 HKLM 原則優先於 `managed-settings.json` 檔案，閘道自己的遠端受管設定優先於兩者，因此在登入閘道的機器上，也在閘道原則的 [`cli` 區塊](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)中設定 `parentSettingsBehavior`。 3 檢查選定的來源 在僅執行 Claude Desktop 的機器上，呼叫 Agent SDK 的 [`resolveSettings()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#resolvesettings) 並在其 `sources` 清單中的 `managed` 項目上讀取 `policyOrigin`。該值命名選定的用戶端側來源，`plist`、`hklm` 或 `file`，這是必須攜帶片段的來源。Claude Desktop 的嵌入式會話不擷取閘道原則，因此閘道的 `cli` 區塊永遠不會計為它們的選定來源。

### 限制父設定

一旦您部署 `parentSettingsBehavior: "merge"`，任何啟動 Claude Code 的主機程序都可以提供父設定，不僅是 Claude Desktop，還有 Agent SDK 應用程式或 IDE 擴充功能。 Claude Code 根據限制性金鑰的允許清單篩選父設定，但某些允許的金鑰可以授予存取權而不是限制它。除非您設定 `allowManaged*Only` 鎖定，主機提供的權限允許規則和沙箱允許清單仍然適用。您的原則的拒絕和詢問規則無論如何都保持有效；[它們在任何允許規則之前進行評估](https://code.claude.com/docs/zh-TW/permissions#manage-permissions)。 Claude Code 以剝離形式轉發父提供的 [`sandbox.credentials`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials) 項目：

- **`deny`項目** ：僅使用其 `path` 或 `name` 和模式轉發。
- **具有[`mode: mask`](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files) 的檔案項目**：轉發為僅限哨兵，作為整個檔案遮罩，其 `injectHosts` 是空清單，因此代理在任何平台上永遠不會用真實值替換父提供的項目。所有結構化遮罩欄位也被刪除，因此父提供的擷取模式無法取代另一個來源為相同路徑設定的更嚴格遮罩。
- **具有`mode: mask` 的 `envVars` 項目**：不轉發。`deny` 是父通道可以透過 `envVars` 項目表達的唯一限制。
- **[`awsPairs`和`sigv4`](https://code.claude.com/docs/zh-TW/sandboxing#re-sign-aws-requests)** ：轉發限制專用。從 `sigv4`，僅保留 `deny` 值，定義 `sigv4` 區塊的父會將所有三種請求形式 `streaming`、`presigned` 和 `sigv4a` 固定為 `deny`。`awsPairs` 對永遠不會以可重新簽署的形式轉發；命名其中一個常規 AWS 變數的對被替換為保持 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY` 和 `AWS_SESSION_TOKEN` 自動配對被抑制的惰性項目。

#### 部署鎖定

為了保持父設定盡可能接近限制專用，如篩選器支援的那樣，將所有五個 `allowManaged*Only` 鎖定和它們管理的允許清單新增至與合併選擇加入相同的來源：

```
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com",
  "parentSettingsBehavior": "merge",
  "allowManagedPermissionRulesOnly": true,
  "allowManagedMcpServersOnly": true,
  "allowManagedHooksOnly": true,
  "allowedMcpServers": [{ "serverUrl": "https://mcp.internal.example.com/*" }],
  "sandbox": {
    "network": {
      "allowManagedDomainsOnly": true,
      "allowedDomains": ["github.com", "*.npmjs.org"]
    },
    "filesystem": {
      "allowManagedReadPathsOnly": true,
      "denyRead": ["~/"],
      "allowRead": ["~/projects"]
    }
  }
}

```

OS 原則（例如 HKLM 登錄原則或受管偏好設定 plist）優先於此檔案，因此透過它而不是檔案傳遞整個片段。閘道的遠端受管設定優先於 OS 原則和檔案來源，但僅到達已連接的用戶端。將鎖定、允許清單和合併選擇加入鏡像到原則的 [`cli` 區塊](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)中，並保持此檔案部署，因為永遠不連接的機器（包括僅執行 Claude Desktop 的機器）僅從檔案獲取其原則。

#### 跨來源的鎖定行為

設定一個鎖定不會限制其他鎖定；每個金鑰都記錄在[設定參考](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)中。 從低於獲勝者的管理員來源，兩個沙箱鎖定仍然適用，`allowManagedPermissionRulesOnly` 仍然阻止父提供的允許規則和 `additionalDirectories`。在 Claude Code v2.1.273 或更新版本上，MCP 伺服器鎖定也從低於獲勝者的來源應用，當它開啟時，受管 `allowedMcpServers` 清單來自設定一個的最高優先級管理員來源。 hooks 鎖定和 `allowManagedPermissionRulesOnly` 對開發人員自己規則的影響預設需要獲勝的來源；在[Claude Code 如何合併受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)中的 `managedSourcesBehavior` 合併選擇加入下，Claude Code 應用任何來源為每個鎖定設定的最嚴格值。在 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 機隊上，鎖定僅從助手的輸出讀取。 每個鎖定使 Claude Code 忽略開發人員自己的該設定項目，因此在鎖定旁邊包含您組織的允許清單：

- **網路網域** ：使用空受管網域清單鎖定會阻止所有沙箱出站流量。
- **MCP 伺服器** ：使用沒有任何管理員來源或父提供的設定中的 `allowedMcpServers` 的鎖定會載入 `deniedMcpServers` 不阻止的每個伺服器。
- **讀取路徑** ：`allowRead` 項目僅重新允許 `denyRead` 區域內的路徑，因此將它們與受管 `denyRead` 配對。

#### 鎖定不涵蓋的設定

四個父提供的設定即使設定了所有五個鎖定也會通過篩選器。在預設首次獲勝設定下，阻止父項的管理員值是最高優先級管理員來源中的值，除了 `allowedMcpServers` 當[MCP 伺服器鎖定](https://code.claude.com/docs/zh-TW/claude-apps-gateway#lock-behavior-across-sources)開啟時。在 `managedSourcesBehavior` 合併選擇加入下，[Claude Code 如何合併受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)說明哪個來源的值改為適用。

- **`forceLoginOrgUUID`**：當最高優先級管理員來源未設定組織 UUID 時，Claude Code 會接受父提供的值。閘道登入不檢查此金鑰，因此它僅對也使用第一方 Anthropic 登入的機隊重要。最高優先級管理員來源中的組織 UUID 會阻止父項的值，是 Claude Code 強制執行的值，因此在那裡設定`forceLoginOrgUUID` 。
- **`allowedMcpServers`**：當沒有管理員清單生效時，Claude Code 會接受父提供的允許清單。`allowManagedMcpServersOnly` 不會阻止它，因為鎖定強制執行無論哪個清單獲勝作為受管值，包括當沒有管理員來源提供清單時的父提供清單。最高優先級管理員來源中的清單會阻止父項的並是 Claude Code 強制執行的清單，因此在那裡設定 `allowedMcpServers`，在鎖定旁邊。在 v2.1.223 之前，任何管理員來源中任一金鑰的值都會阻止父項的。
- **`availableModels`**：當獲勝的受管來源未設定模型清單時，Claude Code 會接受父提供的模型清單。如果您的機隊限制模型，在獲勝的來源中設定`availableModels` 。
- **`strictPluginOnlyCustomization`**：此金鑰無論任何鎖定都通過篩選器，它使 Claude Code 忽略開發人員自己的自訂，包括保護性 hooks。沒有鎖定阻止它。

### 連接 Claude Desktop

[Claude Desktop](https://code.claude.com/docs/zh-TW/desktop)透過不同的 MDM 金鑰連接到相同的閘道：在 Claude Desktop 的[受管配置](https://claude.com/docs/third-party/claude-desktop/configuration)中將 `bootstrapUrl` 設定為 `<listen.public_url>/user/bootstrap`，並使用 `desktop` 金鑰選擇加入使用者的原則。[Claude Desktop 覆蓋](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay)涵蓋兩個部分。需要閘道伺服器上的 Claude Code v2.1.203 或更新版本。 Claude Desktop 透過閘道的身份提供者使用相同的瀏覽器 SSO 步驟簽署開發人員，然後從閘道而不是從 Anthropic 擷取其配置。模型存取和原則遵循與 CLI 相同的每個群組規則。同時使用 CLI 和 Claude Desktop 的開發人員分別登入每個；閘道會話不在它們之間共享。 連接後，Claude Desktop 從每個啟用的標籤透過閘道傳送模型請求。它預設顯示 Cowork 和 Code 標籤。若要同時啟用 Chat 標籤，在 Claude Desktop 的[受管配置](https://claude.com/docs/third-party/claude-desktop/configuration)中將 `chatTabEnabled` 設定為 `true`，或在執行 Claude Code v2.1.227 或更新版本的閘道上的原則的 [`desktop` 區塊](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay)中。

### CI 管道和遠端機器

沒有無人值守管道的服務令牌流程。閘道登入始終執行瀏覽器裝置流程，因此沒有開發人員批准登入的 CI 作業無法進行身份驗證；針對您的提供商直接配置這些。 開發人員登入後，該機器上的每個 Claude Code 會話都使用閘道會話，包括非互動式 `claude -p` 執行和由 Agent SDK 啟動的會話。Claude Code 將[閘道原則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)應用於每個會話。 裝置流程將輪詢 CLI 與批准瀏覽器分開，因此沒有顯示的遠端開發框仍然有效：開發人員透過 SSH 在遠端機器上執行 `/login`，並在其筆記型電腦上的瀏覽器中開啟驗證連結。

### 在開發人員上強制執行的內容

這些保證適用於每個透過 `/login` 登入的會話。Claude Desktop 啟動的嵌入式會話按[將原則傳遞給 Claude Desktop 會話](https://code.claude.com/docs/zh-TW/claude-apps-gateway#deliver-policy-to-claude-desktop-sessions)中所述獲取其原則，遙測項目說明其匯出的去向。

- **模型存取** ：對於原則不授予的模型的請求返回 400，`/model` 選擇器被篩選為原則的 `availableModels` 允許清單。在原則中設定 [`enforceAvailableModels: true`](https://code.claude.com/docs/zh-TW/model-config#default-model-behavior)，以便預設選項解析為 `availableModels` 內的模型，而不是 Claude Code 的內建預設值；沒有它，預設保持可選擇，如果該模型未被授予，則在請求時被拒絕。
- **遙測目的地** ：在透過 `/login` 登入的會話中，CLI 將其 OTLP/HTTP 匯出傳送到閘道，而不是本地設定的 `OTEL_EXPORTER_OTLP_ENDPOINT`，除非原則[將您的收集器命名為端點](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#export-directly-to-your-collector)。閘道將它接收的匯出轉發到 [`telemetry.forward_to`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry) 中的目的地。
  - 在[Claude Desktop 啟動](https://code.claude.com/docs/zh-TW/claude-apps-gateway#connect-claude-desktop)的嵌入式會話中，CLI 將其匯出傳送到配置的 `OTEL_EXPORTER_OTLP_ENDPOINT`。CLI 僅當該端點指向閘道本身時才將閘道會話令牌附加到這些匯出。
  - 沒有為信號配置目的地時，閘道接受並丟棄它。
  - 如果您已經直接收集 Claude Code 遙測，將您的收集器新增為 `forward_to` 目的地，或在原則中命名它以跳過轉發。
- **認證** ：閘道令牌是會話的唯一認證。[Anthropic 設定檔](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)和任何較早的 claude.ai 登入在登入時被忽略，因此開發人員不需要先登出 claude.ai。對於配置的 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 認證，請參閱[管理員原則要求雲端閘道登入](https://code.claude.com/docs/zh-TW/errors#administrator-policy-requires-a-cloud-gateway-sign-in)。
- **受管設定** ：鎖定的金鑰無法在本地覆蓋。CLI 在啟動時應用原則，並在每個每小時輪詢時應用變更，除了[僅在下次啟動時應用的變更](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)。
- **閘道無法到達時啟動** ：已登入的會話在啟動時約 10 秒後以錯誤退出，而不是在沒有其設定的情況下啟動。
- **閘道結束會話後啟動** ：請參閱[強制執行故障關閉啟動](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup)，了解哪些啟動在登出閘道的情況下開啟，哪些在閘道以 `401` 回答時退出。
- **取消佈建** ：其使用者在 IdP 中被禁用的會話在下一次刷新失敗時在 `ttl_hours` 內過期。

### 組織可以看到什麼

使用情況遙測攜帶開發人員的身份、令牌計數、模型和延遲到組織的收集器。閘道不記錄或儲存提示或完成內容。是否收集更豐富的遙測（例如日誌和追蹤），可能包括命令和檔案路徑，是組織的[按目的地選擇](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry)。

## 可用性和限制

該表涵蓋當開發人員透過閘道連接時哪些 Claude Code 功能有效，以及閘道伺服器本身支援什麼。如果不支援某些內容，「備註」欄提供替代方案。 閘道傳遞 CLI 發送到每個上游的 [`anthropic-beta`](https://platform.claude.com/docs/en/api/beta-headers) 值，因此操作員不維護測試版允許清單。對於 Amazon Bedrock（忽略標頭），閘道將值移到請求正文的 `anthropic_beta` 欄位；其他上游接收按發送方式發送的標頭。

| 功能                                                                                                            | 狀態                 | 備註                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 推理轉發 (Amazon Bedrock、Claude Platform on AWS、Google Cloud 的 Agent Platform、Microsoft Foundry、Anthropic) | 可用                 | 具有按上游模型轉換和故障轉移。Amazon Bedrock 上游使用 `bedrock-runtime` 端點和 AWS 預設認證鏈；Amazon Bedrock [Mantle 端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint)不是支援的上游。[Claude Platform on AWS 上游](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-platform-on-aws)需要閘道伺服器上的 Claude Code v2.1.198 或更新版本。                                                                       |
| 按 IdP 群組的模型存取和受管設定                                                                                 | 可用                 | 模型存取在伺服器端強制執行；受管設定按 IdP 群組傳遞，由 CLI 在[受管設定層級](https://code.claude.com/docs/zh-TW/settings#settings-precedence)應用                                                                                                                                                                                                                                                                                                                   |
| Claude Desktop                                                                                                  | 可用（需要選擇加入） | 閘道在 `/user/bootstrap` 提供 Claude Desktop 的設定，一旦原則[使用 `desktop` 金鑰選擇加入](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay)，Claude Desktop 從其 Cowork 和 Code 標籤以及從 Chat 標籤（當您啟用它時）發送模型請求透過閘道。若要開啟 Chat 標籤，請參閱[連接 Claude Desktop](https://code.claude.com/docs/zh-TW/claude-apps-gateway#connect-claude-desktop)。需要閘道伺服器上的 Claude Code v2.1.203 或更新版本。 |
| 遙測扇出 (OTLP/HTTP)                                                                                            | 可用                 | 按匯出標識戳記；protobuf 和 JSON 編碼                                                                                                                                                                                                                                                                                                                                                                                                                               |
| OIDC 身份提供者                                                                                                 | 可用                 | 任何符合 OIDC 的 IdP；閘道執行標準 OIDC 探索和授權碼流程。請參閱[身份提供者設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#identity-provider-setup)以了解各 IdP 的配置                                                                                                                                                                                                                                                                          |
| 按使用者和按群組支出限制                                                                                        | 可用                 | 請參閱[支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)                                                                                                                                                                                                                                                                                                                                                                               |
| 伺服器端網路搜尋                                                                                                | 不可用               | CLI 無法看到閘道路由到的上游提供商，因此無法驗證網路搜尋支援並在閘道會話上禁用 WebSearch                                                                                                                                                                                                                                                                                                                                                                            |
| [Remote Control](https://code.claude.com/docs/zh-TW/remote-control)                                             | 不可用               | CLI 顯示[命名閘道的錯誤](https://code.claude.com/docs/zh-TW/errors#remote-control-requires-the-anthropic-api)                                                                                                                                                                                                                                                                                                                                                       |
| [`/design-sync`](https://code.claude.com/docs/zh-TW/commands#all-commands) 和 `/design-login`                   | 不可用               | 兩者都需要 claude.ai，CLI 在閘道會話上不聯絡，因此兩個命令都不會出現                                                                                                                                                                                                                                                                                                                                                                                                |
| 需要功能旗標擷取的功能，例如 `/import` 和 `claude import`                                                       | 不可用               | CLI 在閘道會話上跳過旗標擷取。[需要功能旗標擷取的功能](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)列出關閉的內容                                                                                                                                                                                                                                                                                                          |
| 標準提示快取                                                                                                    | 可用                 | 閘道將 `cache_control` 斷點轉發到每個上游。[快取位置](https://code.claude.com/docs/zh-TW/prompt-caching#where-the-cache-lives)涵蓋 CLI 標記的區塊，包括它在對話中途附加的系統內容                                                                                                                                                                                                                                                                                   |
| 1 小時快取 TTL                                                                                                  | 不可用               | CLI 在閘道會話上省略擴展快取 TTL 測試版，因為並非閘道可以路由到的每個上游都支援 1 小時 TTL，因此透過閘道的提示快取使用 5 分鐘 TTL；請參閱上面的測試版標頭備註                                                                                                                                                                                                                                                                                                       |
| 自動模式                                                                                                        | 可用                 | 遵循[第三方提供商規則](https://code.claude.com/docs/zh-TW/permission-modes#enable-auto-mode-on-bedrock-agent-platform-or-foundry)：只有第三方提供商上符合條件的模型可以使用它。在 v2.1.207 之前，閘道會話上的自動模式需要設定 `CLAUDE_CODE_ENABLE_AUTO_MODE=1`，可透過受管原則 `env` 區塊傳遞                                                                                                                                                                       |
| 僅限第一方的最佳化，例如全域快取範圍和令牌高效工具                                                              | 不可用               | CLI 在閘道會話上不啟用它們；請參閱上面的測試版標頭備註                                                                                                                                                                                                                                                                                                                                                                                                              |
| OTLP/gRPC                                                                                                       | 不支援               | 僅 OTLP over HTTP                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| SAML、LDAP 和其他非 OIDC 身份驗證                                                                               | 不支援               | 僅 OIDC。如果需要，使用 OIDC 橋接                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 多租戶（多個 OIDC 發行者）                                                                                      | 不支援               | 每個閘道一個發行者。執行單獨的執行個體                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Windows 伺服器                                                                                                  | 不支援               | 在 Linux 上部署。僅本地開發的 macOS                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Helm chart                                                                                                      | 不可用               | 閘道作為標準無狀態 Deployment 執行；請參閱[部署指南](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#kubernetes)                                                                                                                                                                                                                                                                                                                                      |
| 管理員 UI                                                                                                       | 不可用               | 設定是 YAML 檔案；重新部署以更改它                                                                                                                                                                                                                                                                                                                                                                                                                                  |

## 後續步驟

快速入門讓您在 Docker Compose 下執行最小配置。要進一步進行：

- 擴展 `gateway.yaml` 超越最小配置，例如新增按群組 RBAC、多上游故障轉移或遙測目的地。[配置參考](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config)涵蓋每個選項。
- 從 Compose 移動到 Kubernetes 或 Cloud Run 上的生產部署，正確設定您的 IdP，並檢查安全模型。[部署和操作指南](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy)涵蓋每個 IdP 的設定、容器映像要求、健康探針和故障排除。
- 對個別開發人員或群組設定支出上限，以便失控的工作負載無法消耗您的整個承諾。[支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)涵蓋管理員 API 以及強制執行的工作方式。
- 有關 AWS 上的完整實踐示例，包括 ECS Fargate 或 EKS、Amazon RDS 和 Secrets Manager，請參閱[在 AWS 上部署](https://code.claude.com/docs/zh-TW/claude-apps-gateway-on-aws)。
- 有關 Google Cloud 上的完整實踐示例，包括 Cloud Run、Cloud SQL 和 Secret Manager，請參閱[在 Google Cloud 上部署](https://code.claude.com/docs/zh-TW/claude-apps-gateway-on-gcp)。

是否 助手
