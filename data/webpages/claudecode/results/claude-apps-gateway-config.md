Claude 應用程式閘道部署由一個 YAML 檔案設定，按慣例稱為 `gateway.yaml`。該檔案定義閘道執行的所有操作：它在哪裡監聽、開發人員如何登入、推論去往何處，以及哪些原則和遙測適用。本頁是該檔案中每個選項的參考資料。若要撰寫您的第一個，請從[快速入門](https://code.claude.com/docs/zh-TW/claude-apps-gateway#quickstart)開始，它會建立最小的工作設定並執行它；一旦您有了滿意的設定，[部署指南](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy)涵蓋將其容器化並在 Kubernetes、Cloud Run 或您自己的平台上託管。 閘道在啟動時使用 `claude gateway --config /path/to/gateway.yaml` 讀取該檔案一次。每個選項都在啟動時根據架構進行驗證，因此格式不正確的設定會在啟動時失敗，並出現欄位級錯誤，而不是在首次使用時失敗。 本頁末尾的[完整範例](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#complete-example)涵蓋每個部分。

## 檔案結構

五個部分是[必需的](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#required-sections)。其他所有部分都是[選擇性的](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#optional-sections)，省略的部分會採用其預設值。未知的鍵會導致啟動失敗，因此打字錯誤會顯示為具名錯誤，而不是被無聲地忽略的設定。 **必需部分：**

- [`listen`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#listen)：繫結位址、公開 URL、TLS 終止
- [`oidc`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#oidc)：您的身分識別提供者 (IdP)，包括簽發者、用戶端、宣告對應，以及誰可以登入
- [`session`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#session)：閘道器鑄造的持有人令牌，包括祕密和生命週期
- [`store`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#store)：PostgreSQL，用於裝置授權和速率限制計數器
- [`upstreams`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)：推論的去向，無論是 Anthropic、Amazon Bedrock、AWS 上的 Claude Platform、Google Cloud 的 Agent Platform，還是 Microsoft Foundry

**選擇性部分：**

- [`admin`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin)：Admin API 驗證和支出限制的保留期
- [`enforcement`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#enforcement)：支出限制失敗開放或失敗關閉行為
- [`pricing`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#pricing)：合約費率以及支出計量和開發人員看到的成本數字的乘數
- [`models`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models) 和 `auto_include_builtin_models`：管理員策劃的模型清單和每個上游的 ID
- [`managed`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)：按 IdP 群組的受管設定原則
- [`telemetry`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry)：OTLP 轉發到您的可觀測性堆疊
- [`access_control`、`limits`、`timeouts`、`rate_limits`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#http-tuning)：IP 允許/拒絕、請求大小上限、上游首位元組時間，以及每個 IP 的登入限制

## 祕密擴展

不要直接在 `gateway.yaml` 中寫入祕密，例如 `client_secret`、`jwt_secret` 或 `postgres_url`。使用下列其中一種形式參考它們，閘道會在啟動時從環境變數或檔案解析該值：

| 形式            | 解析為                                                                                                                                                                         | 用於                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| `${VAR}`        | 環境變數 `VAR`。如果未定義，啟動失敗。                                                                                                                                         | 容器環境變數、透過環境注入的 AWS Secrets Manager |
| `${file:/path}` | 該絕對路徑處檔案的內容，已修剪。參考必須是欄位的整個值：不同於 `${VAR}`，它不會在較長的字串內展開，因此對於資料庫密碼，請設定 `store.password` 而不是將其嵌入 `postgres_url`。 | Kubernetes Secret 卷掛載、Vault Agent、SOPS      |

## 必需部分

### `listen`

`listen` 區塊控制閘道服務的位置：繫結位址和連接埠、外部可見的來源，以及選用的 TLS 終止。

| 欄位                   | 必需               | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `host`                 | 否                 | 繫結位址。預設 `0.0.0.0`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `port`                 | 否                 | 繫結連接埠。預設 `8080`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `public_url`           | 除非 `host` 是環回 | 外部可見的 `https://` 來源，用於建立 IdP `redirect_uri` 和發現中繼資料。在 `host` 不是環回位址時為必需，無論 TLS 是在代理（例如 ALB、Ingress 或 Cloud Run）還是在閘道本身透過 `tls` 終止，因為閘道永遠不會從 `X-Forwarded-*` 標頭衍生自己的來源；它們是用戶端可欺騙的。沒有它啟動會失敗。下面的 `trusted_proxies` 僅控制用戶端 IP 解析。啟用[遙測](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry)時也是必需的，因為閘道從此 URL 建立它推送給用戶端的 OTLP 端點。 |
| `tls.cert` / `tls.key` | 否                 | 如果閘道自己終止 TLS，則為 PEM 路徑                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `trusted_proxies`      | 否                 | 閘道前面的負載平衡器的 CIDR 或 IP。設定時，閘道僅信任來自這些對等方的 `X-Forwarded-For`，並記錄真實用戶端 IP 以進行每 IP 速率限制和稽核。等同於 nginx `set_real_ip_from`。`X-Forwarded-For` 項目寫成 `ipv4:port` 或 `[ipv6]:port`（如某些負載平衡器所做），會以連接埠被刪除的方式讀取。附加連接埠且沒有括號的 IPv6 位址可能被讀取為不同位址或根本不被讀取，因此在任何寫入該形式的代理上關閉連接埠選項。                                                                                    |

### `oidc`

`oidc` 區塊將閘道連接到您的身分識別提供者，並決定誰可以登入。它命名簽發者和 OAuth 用戶端、對應攜帶電子郵件和群組的宣告，並按電子郵件網域或群組限制登入。 OpenID Connect (OIDC) 是閘道與您的身分識別提供者一起使用的 SSO 協定；請參閱[身分識別提供者設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#identity-provider-setup)以了解在 IdP 端註冊的內容。

| 欄位                            | 必需 | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `issuer`                        | 是   | OIDC 發現基礎。必須在 `/.well-known/openid-configuration` 提供發現。在生產環境中使用 HTTPS；閘道接受 `http://` 簽發者。環回簽發者（例如 `http://localhost:8081`）會被[SSRF 防護](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#threat-model-summary)拒絕，除非在閘道的環境中設定了 `CLAUDE_GATEWAY_ALLOW_LOOPBACK=1`。                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `client_id` / `client_secret`   | 是   | 來自您的 OAuth 用戶端註冊                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `allowed_email_domains`         | 否   | 拒絕 `email` 宣告不在這些網域之一中的 id_token，不區分大小寫。針對多租戶 IdP 誤設定的深度防禦。獨立於此設定，`email_verified` 宣告明確為 `false` 的 id_token 始終被拒絕。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `allowed_groups`                | 否   | 限制登入為這些 IdP 群組的成員，與 `groups_claim` 相符。允許電子郵件網域中但不在這些群組中的使用者被拒絕。需要 IdP 發出群組宣告。匹配是針對該宣告中值的精確、區分大小寫的字串比較，閘道不展開嵌套群組：若要允許子群組的成員，請在此列出子群組或設定 IdP 以發出扁平化成員資格。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `groups_claim`                  | 否   | 哪個 id_token 宣告攜帶群組成員資格。預設 `groups`。Microsoft Entra 在 `roles` 下發出應用程式角色。接受平面鍵或 RFC 6901 JSON 指標，例如 `/resource_access/gateway/roles` 用於嵌套宣告。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `google_groups`                 | 否   | 透過 Google Workspace Admin SDK Directory API 查詢已登入使用者的群組，因為 Google 的 id_token 不攜帶群組宣告。將 `service_account_json_path` 設定為具有 `https://www.googleapis.com/auth/admin.directory.group.readonly` 範圍的網域範圍委派的服務帳戶金鑰檔案，並將 `admin_email` 設定為服務帳戶模擬的 Workspace 管理員；Directory API 需要真實的管理員主體。每個使用者的群組電子郵件地址成為其群組宣告，因此 `allowed_groups` 和 `managed.policies.match.groups` 與群組電子郵件相符。                                                                                                                                                                                                                                                                                  |
| `email_claim`                   | 否   | 哪個 id_token 宣告攜帶使用者的電子郵件。預設 `email`。某些 IdP（例如 ADFS 和 Entra B2C）改為發出 `upn` 或 `preferred_username`。接受平面鍵、JSON 指標或後備鍵清單，其中使用第一個存在的鍵。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `scopes`                        | 否   | 閘道請求的 OIDC 範圍的完整覆蓋。預設 `[openid, profile, email, offline_access]`。當您的 IdP 拒絕它不識別的範圍或需要自訂範圍來發出群組或電子郵件時設定。必須包含 `openid`。刪除 `offline_access` 會停用重新整理令牌，因此開發人員每 `session.ttl_hours` 重新執行瀏覽器登入。請參閱[身分識別提供者設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#identity-provider-setup)以了解每個 IdP 範圍配方，例如 Google 的重新整理令牌流程。                                                                                                                                                                                                                                                                                                                  |
| `scope_on_refresh`              | 否   | 當閘道交換重新整理令牌時，也傳送 `scope`，具有與登入請求相同的清單。預設 `false`：重新整理請求省略 `scope`。大多數 IdP 在每次重新整理時返回 id_token，不需要這個。當您的 IdP 僅在再次要求 `openid` 時才在重新整理時返回 id_token 時設定 `true`，Okta 為其重新整理授權記錄了這一點。沒有 id_token，每次重新整理都取決於 IdP 的 userinfo 端點接受重新整理的存取令牌。如果您在登入或匹配原則上閘控群組，且您的 IdP 的重新整理時間 id_token 省略它們，也設定 `userinfo_fallback: true`，以便閘道從 userinfo 端點填補它們。授予的範圍少於請求的 IdP 可以使用 `invalid_scope` 拒絕重新整理，包括現有工作階段（如果您在此開啟時將項目新增到 `scopes`）。如果在設定後重新整理開始在 `token_endpoint` 失敗，請取消設定金鑰。需要閘道伺服器上的 Claude Code v2.1.260 或更新版本。 |
| `extra_auth_params`             | 否   | 附加到 IdP 授權請求的額外查詢參數，逐字。這是 IdP 特定行為的覆蓋機制，例如 Google 重新整理令牌的 `access_type: offline`、某些 Entra 租戶的 `domain_hint` 或逐步提升流程的 `acr_values`。無法覆蓋閘道管理的協定參數：`state`、`nonce`、`redirect_uri`、PKCE、`scope`、`response_type`、`response_mode` 和 `client_id`。                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `userinfo_fallback`             | 否   | 當 id_token 省略電子郵件或群組時，從 `/userinfo` 擷取它們。Keycloak 輕量級存取令牌、Okta 組織伺服器和 ADFS 最小令牌需要。id_token 保持權威；userinfo 僅填補空白。預設 `false`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `use_pkce`                      | 否   | 在授權請求上傳送 PKCE (S256) 挑戰。預設 `true`。僅當您的 IdP 為此機密用戶端拒絕 PKCE 時設定 `false`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `clock_skew_seconds`            | 否   | 驗證 id_token 時間宣告時容許時鐘漂移。預設 `0`，這是嚴格的。如果您在登入後立即看到「令牌已過期/尚未有效」錯誤，請提高以應對主機/IdP 時鐘偏差。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `token_endpoint_auth_method`    | 否   | 覆蓋令牌端點驗證方法。接受 `client_secret_basic` 或 `client_secret_post`。預設自動協商。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `id_token_signed_response_alg`  | 否   | 預期的 id_token 簽署演算法。預設 `RS256`。為使用 ES256、PS256 或 EdDSA 簽署的 IdP 設定。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `additional_authorized_parties` | 否   | 除了 `client_id` 之外要接受的額外 `azp` 值，用於 Keycloak 代理和令牌交換流程                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `discovery_url`                 | 否   | 從此 URL 擷取發現文件，而不是從 `issuer` 衍生，用於代理後面重寫簽發者主機的 IdP。路徑必須包含 `/.well-known/`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `use_proxy`                     | 否   | 透過 `HTTPS_PROXY` 或 `HTTP_PROXY` 中的轉發代理傳送閘道自己的 IdP 請求，遵守 `NO_PROXY`。未設定或 `false`，這些請求直接進行。需要 v2.1.227 或更新版本；請參閱下面的[透過轉發代理的 IdP 請求](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#idp-requests-through-a-forward-proxy)。                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `form_action_origins`           | 否   | `/device` 頁面的 `Content-Security-Policy: form-action` 指令的其他來源。閘道已允許 `'self'` 和發現的 `authorization_endpoint` 來源，但 Chrome 對整個重新導向鏈強制執行 `form-action`。如果您的 IdP 透過第二個主機重新導向，例如 Azure AD 聯合到 ADFS、中樞輪輻 Okta 或公司 SSO 攔截器，列出授權請求可能重新導向的每個來源。                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `ca_cert_pem`                   | 否   | PEM 編碼的 CA 憑證本身，而不是檔案的路徑。它替換 IdP 請求的系統信任存放區。若要載入掛載的檔案，請寫入 `${file:/etc/gateway/idp-ca.pem}`。用於公司 PKI 後面的 Keycloak 或 Dex。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

#### 透過轉發代理的 IdP 請求

推論上游在每個版本上都遵守 `HTTPS_PROXY` 和 `HTTP_PROXY`。閘道自己對 IdP、發現、JWKS、令牌和 userinfo 的請求直接進行，除非您設定 `oidc.use_proxy: true`，這需要 v2.1.227 或更新版本。當代理變數被設定、`use_proxy` 未設定且簽發者未被 `NO_PROXY` 涵蓋時，閘道保持這些請求直接並在啟動時記錄通知，要求您選擇；`use_proxy: false` 保持它們直接並沉默通知。 使用 `use_proxy: true`，Pod 自己解析每個 IdP 端點的主機名稱，並要求代理 `CONNECT` 到解析的 IP 位址，因此代理必須接受 `CONNECT` 到發現文件命名的每個主機的 IP 位址，而不僅僅是簽發者。使用 `http://` 代理 URL。`ca_cert_pem` 和[SSRF 防護](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#threat-model-summary)也適用於代理路徑。

### `session`

`session` 區塊塑造閘道在登入後鑄造的持有人令牌：簽署它們的祕密和它們的生命週期。

| 欄位         | 必需 | 說明                                                                                                                                                                                                                                                                                                               |
| ------------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `jwt_secret` | 是   | 至少 32 位元組的熵，例如來自 `openssl rand -base64 32`。簽署閘道的 HS256 持有人令牌。接受單一字串或用於輪換的陣列：索引 0 簽署，所有項目驗證。若要輪換，前置新祕密，等待 `ttl_hours`，然後刪除舊祕密。                                                                                                             |
| `ttl_hours`  | 否   | 閘道持有人令牌生命週期。預設 `1`。當 IdP 發出重新整理令牌時，CLI 在過期前無聲地重新整理。較短的生命週期會更快地取消佈建；較長的生命週期會減少 IdP 往返次數。如果您的 IdP 因為 `offline_access` 不可用而無法發出重新整理令牌，則沒有無聲重新整理，因此將其提高到 `8` 或 `12` 以避免每小時將開發人員送回瀏覽器登入。 |

### `store`

`store` 區塊將閘道指向其 PostgreSQL 資料庫，該資料庫保存裝置授權和速率限制計數器。

| 欄位                                                                                                                                        | 必需 | 說明                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `postgres_url`                                                                                                                              | 是   | `postgres://` 或 `postgresql://` URL。必需：裝置授權會合點，瀏覽器回呼寫入且輪詢 CLI 讀取，需要跨副本狀態。閘道在啟動時執行自己的架構遷移，並在升級時執行，因此角色需要在目標架構上建立和更改表的權限。請參閱[升級](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#upgrades)和 [Postgres](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#postgres)。 |
| `username`                                                                                                                                  | 否   | 覆蓋 `postgres_url` 中的使用者                                                                                                                                                                                                                                                                                                                                                     |
| `password`                                                                                                                                  | 否   | 資料庫認證。在此設定它而不是在 `postgres_url` 中，以便認證保持在 URL 之外。接受任何字元並優先於 URL 認證。                                                                                                                                                                                                                                                                         |
| `max_connections`                                                                                                                           | 否   | 每個副本的 Postgres 連線池大小。預設 `5`，這是保守的且對共享資料庫友善。啟用[支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin)後，熱路徑每個推論請求執行幾個操作，因此在負載下為專用資料庫提高它，並保持副本 × 此值低於資料庫的 `max_connections`。                                                                                                   |
| 對於本地開發，將 `postgres_url` 指向一次性 Postgres 容器，例如 `docker run --rm -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres`。 |      |                                                                                                                                                                                                                                                                                                                                                                                    |

### `upstreams`

`upstreams` 是一個有序清單。閘道將推論轉發到解析所請求模型的第一個上游。 在 `5xx`、`429`、`401`、`403`、`404` 或逾時時，它會故障轉移到下一個；其他 `4xx` 不會，因為這些錯誤可歸因於請求而不是上游。`401` 或 `403` 表示閘道自己的認證對該上游失敗。`404` 表示該上游不服務所請求的模型，因此清單中稍後的上游仍然可以。 如果您在上游上設定 `forward_user_identity: true`，它返回給攜帶開發人員電子郵件的請求的 `429` 不會故障轉移。請參閱[每個使用者限制拒絕如何到達開發人員](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#per-user-identity-headers-for-a-proxy-you-run)。 故障轉移於 `404` 需要閘道 v2.1.198 或更新版本。較早的版本即使清單中稍後的上游服務該模型，也會將第一個 `404` 返回給用戶端。 相同提供者的多個上游必須設定不同的 `name:`。 Amazon Bedrock、Claude Platform on AWS、Google Cloud 的 Agent Platform 和 Microsoft Foundry 用戶端在啟動時建立一次，其 SDK 在內部重新整理認證，因此輪換雲認證不需要重新啟動。靜態 Anthropic API 金鑰和持有人在啟動時讀取；請參閱 [Anthropic API](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#anthropic-api)。

#### 上游錯誤訊息

閘道返回一個上游的錯誤回應，或其自己的 `502`，取決於上游如何回答：

- **上游返回閘道不[故障轉移](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#multiple-upstreams)的狀態**：該上游的回應。閘道不嘗試進一步的上游。
- **閘道嘗試的每個上游都以閘道[故障轉移](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#multiple-upstreams)的方式失敗**：最後一個 `429`。當沒有返回 `429` 時，閘道優先選擇，按順序，最後一個 `401` 或 `403`、最後一個 `404` 和最後一個 `501`。當沒有返回任何這些時，閘道自己的 `502`，`all upstreams failed (N attempted)`，其中 N 計算 [`upstreams`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams) 中的每個項目，包括閘道跳過的項目，因為它們不服務所請求的模型。

當閘道返回上游的回應時，它保持上游的狀態碼。它是否保持上游的訊息取決於提供者。Anthropic API 上游的錯誤正文未更改地到達開發人員。 Amazon Bedrock、Claude Platform on AWS、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上游可以在其錯誤文字中命名您的帳戶 ID、角色 ARN 和專案 ID。閘道在[操作日誌](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#logs)中記錄該完整文字。開發人員從這些上游看到的內容取決於拒絕：

- Anthropic 標準錯誤信封中的 `400` 或 `413`：上游自己的訊息，例如 `prompt is too long`。Claude Platform on AWS、Agent Platform 和 Microsoft Foundry 為模型 API 拒絕返回此信封。
- 提供者自己形狀中的 `400` 或 `413`：`capability_rejected:` 令牌。當閘道無法分類拒絕時，`400` 上的 `upstream rejected the request` 或 `413` 上的 `request too large for this upstream`。
- 任何其他狀態：通用的每狀態副本，例如 `429` 上的 `upstream rate limit exceeded`。

例如，閘道將 Amazon Bedrock 的 `Input is too long for requested model.` 替換為 `capability_rejected: prompt_too_long`。Claude Code [自動壓縮](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)該令牌，就像它對 `prompt is too long` 所做的那樣。 保持雲上游的 `400` 或 `413` 訊息，或將其替換為 `capability_rejected:` 令牌，需要閘道 v2.1.233 或更新版本。

#### Anthropic API

最小的 Anthropic 上游是來自 [Claude Console](https://platform.claude.com) 的 API 金鑰：

```
upstreams:
  - provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}
    # 或 OAuth 持有人（例如工作負載身分識別聯合交換的令牌）：
    #   oauth_token: ${file:/var/run/secrets/anthropic-oauth-token}
    # base_url: https://api.anthropic.com   # 預設；覆蓋以使用轉發代理

```

兩種認證形式在它們傳送的標頭中有所不同：

- **`api_key`**：傳送`x-api-key` 。在 Claude Console 中輪換它並更新環境變數。
- **`oauth_token`**：傳送`Authorization: Bearer` 。當您的組織發出短期令牌而不是長期 API 金鑰時使用持有人形式。持有人在啟動時讀取一次，因此透過重新掛載祕密和重新啟動來重新整理。

除了靜態金鑰或持有人，您可以使用工作負載身分識別聯合。按照[工作負載身分識別聯合指南](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)建立聯合規則，然後將您的工作負載的 OIDC JWT 掛載為檔案，例如 Kubernetes 投影服務帳戶令牌或 CI 平台的 id-token。閘道將 JWT 交換為短期持有人並自動重新整理它。令牌檔案在每次交換時重新讀取，因此輪換的投影令牌無需重新啟動即可被拾取。

```
upstreams:
  - provider: anthropic
    auth:
      federation_rule_id: ${ANTHROPIC_FEDERATION_RULE_ID}
      organization_id: ${ANTHROPIC_ORGANIZATION_ID}
      identity_token_file: /var/run/secrets/anthropic/id-token
      # workspace_id: wrkspc_...       # 如果規則涵蓋 >1 個工作區，則為必需
      # service_account_id: svac_...   # 選用的預期目標檢查

```

您可以將 `provider: anthropic` 上游的 `base_url` 指向您執行的代理，而不是 Anthropic API。若要告訴該代理哪個開發人員傳送了每個請求，請在該上游上設定 `forward_user_identity: true`。代理然後可以按開發人員歸因支出。需要在閘道伺服器上執行 Claude Code v2.1.233 或更新版本。 例如，對於 `upstream-gateway.internal.example.com` 的代理：

```
upstreams:
  - provider: anthropic
    base_url: https://upstream-gateway.internal.example.com
    auth:
      api_key: ${PROXY_KEY}
    forward_user_identity: true        # 預設 false

```

閘道將這些標頭新增到它轉發到該上游的每個請求。

| 標頭                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 值                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `x-litellm-end-user-id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 開發人員的電子郵件，當 IdP 提供時。          |
| `x-claude-gateway-user-id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 開發人員的 IdP 主體，來自令牌的 `sub` 宣告。 |
| `x-claude-gateway-user-email`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 開發人員的電子郵件，當 IdP 提供時。          |
| 當 IdP 令牌不攜帶電子郵件時，閘道僅傳送 `x-claude-gateway-user-id` 並省略兩個電子郵件標頭。如果您的 IdP 將電子郵件放在不同的宣告中，請將 [`oidc.email_claim`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#oidc) 設定為該宣告。 當您的代理答覆攜帶開發人員電子郵件的請求的 `429` 時，閘道將該回應原樣返回給開發人員，而不是故障轉移到下一個上游，因此您的代理的每個使用者預算或速率限制保持。代理的其他回應遵循普通[故障轉移規則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)。如果開發人員的 IdP 令牌不攜帶電子郵件，閘道轉發其請求而不帶電子郵件標頭，因此對其中一個請求的 `429` 計為上游容量並故障轉移。在閘道伺服器上的 v2.1.267 之前，每個 `429` 都故障轉移。 僅在 `base_url` 是您操作的代理的上游上設定 `forward_user_identity`。閘道將開發人員電子郵件傳送到該 `base_url` 命名的任何伺服器。如果 `base_url` 是 Anthropic API（預設），閘道拒絕啟動。 |                                              |

#### Amazon Bedrock

對於閘道替換或前置的用戶端 Bedrock 部署，請參閱 [Claude Code on Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)。閘道端上游：

```
upstreams:
  - provider: bedrock
    region: us-east-1
    auth: {}                           # 首選：AWS 預設認證鏈
    # 或明確認證：
    # auth:
    #   aws_access_key_id: ${AWS_AKID}
    #   aws_secret_access_key: ${AWS_SK}
    #   aws_session_token: ${AWS_ST}
    # 或 Bedrock API 持有人令牌：
    # auth:
    #   aws_bearer_token: ${AWS_BEARER_TOKEN}
    # 覆蓋 bedrock-runtime 端點以進行 FIPS 或 VPC 端點部署：
    # base_url: https://bedrock-runtime-fips.us-east-1.amazonaws.com

```

空的 `auth` 區塊使用 AWS SDK 的預設認證鏈：環境變數、`~/.aws/credentials`、ECS 任務角色、EC2 執行個體中繼資料或 EKS 上的 IRSA。在生產環境中，給予閘道 Pod 一個 IAM 角色，而不是在容器映像中嵌入靜態金鑰。 明確認證必須完整：當 `aws_access_key_id` 和 `aws_secret_access_key` 未一起設定時，或當 `aws_session_token` 在沒有它們的情況下設定時，閘道在啟動時失敗。在 v2.1.207 之前，部分 `auth:` 區塊通過驗證。

| 設定         | 方式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IAM 權限     | 授予閘道的主體 `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream` 在推論設定檔 ARN 和基礎基礎模型 ARN 上。對於美國地區的內建目錄：`arn:aws:bedrock:<region>:<account>:inference-profile/us.anthropic.*` 和 `arn:aws:bedrock:*::foundation-model/anthropic.*`。也授予基礎模型 ARN 上的 `bedrock:CountTokens`。閘道使用它（免費）來計算用戶端放棄的請求的輸入令牌，因此[支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin)保持準確。沒有它，閘道會回退到該計數的一令牌 Bedrock 請求。 |
| 模型存取     | Amazon Bedrock 在商業地區預設啟用模型存取。剩餘的帳戶級閘控是 Anthropic 的一次性使用案例表單：如果您的 AWS 帳戶中沒有人提交過，請開啟 Amazon Bedrock 主控台，從模型目錄中選擇 Anthropic 模型，並完成表單。請參閱[提交使用案例詳細資訊](https://code.claude.com/docs/zh-TW/amazon-bedrock#1-submit-use-case-details)以了解 AWS Organizations 表單和提交者需要的權限。                                                                                                                                                          |
| EKS (IRSA)   | 建立具有上述原則和針對您叢集的 OIDC 提供者的信任原則的 IAM 角色，範圍限於閘道的服務帳戶。使用 `eks.amazonaws.com/role-arn: arn:aws:iam::<acct>:role/claude-gateway` 註釋服務帳戶。`auth: {}` 會拾取它。                                                                                                                                                                                                                                                                                                                       |
| ECS / EC2    | 將 IAM 角色附加到任務定義或執行個體設定檔。`auth: {}` 會拾取它。                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 其他任何地方 | 透過 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY` 和 `AWS_SESSION_TOKEN` 環境變數傳遞認證，或在 `auth:` 中使用 `${VAR}` 擴展明確設定它們                                                                                                                                                                                                                                                                                                                                                                                      |
| 地區         | `region:` 是 API 端點地區。跨地區推論設定檔無論您選擇哪一個，都會跨地理位置 (US、EU、APAC) 路由。對於非美國地區或佈建輸送量 ARN，新增具有正確每上游 ID 的 [`models:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models) 區塊。                                                                                                                                                                                                                                                                            |

#### Claude Platform on AWS

Claude Platform on AWS 在 `aws-external-anthropic.<region>.api.aws` 的 AWS 基礎設施上服務第一方 Anthropic API。它使用第一方模型 ID，按原樣接受 `anthropic-beta` 標頭，並服務 `count_tokens`，因此 Bedrock 特定的轉譯都不適用。`anthropicAws` 提供者需要 Claude Code v2.1.198 或更新版本；較早的閘道版本在啟動時拒絕它。 對於相同平台的用戶端部署，請參閱 [Claude Code on Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)。閘道端上游：

```
upstreams:
  - provider: anthropicAws
    region: us-east-1
    workspace_id: wrkspc_...
    auth:
      api_key: ${ANTHROPIC_AWS_API_KEY}   # 作為 x-api-key 傳送
    # 或透過 AWS 預設認證鏈的 SigV4：
    # auth: {}
    # 或明確的 SigV4 認證：
    # auth:
    #   aws_access_key_id: ${AWS_ACCESS_KEY_ID}
    #   aws_secret_access_key: ${AWS_SECRET_ACCESS_KEY}
    # 覆蓋衍生的端點：
    # base_url: https://aws-external-anthropic.us-east-1.api.aws

```

該平台在與 Amazon Bedrock 不同的 AWS 帳戶中執行，並為其自己的服務名稱 `aws-external-anthropic` 簽署 SigV4 請求，因此 Bedrock 範圍的 IAM 角色不授權它。`auth.api_key` 中的 API 金鑰在同時設定 SigV4 認證時優先。空的 `auth` 區塊使用 AWS SDK 的預設認證鏈，與 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#amazon-bedrock) 上游使用的相同鏈。

| 欄位                                                                                                                                                                                                             | 必需 | 說明                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------ |
| `region`                                                                                                                                                                                                         | 是   | AWS 地區，小寫字母、數字和連字號。閘道將端點衍生為 `https://aws-external-anthropic.<region>.api.aws`。 |
| `workspace_id`                                                                                                                                                                                                   | 是   | 在每個請求上傳送為標頭；平台需要它                                                                     |
| `auth.api_key`                                                                                                                                                                                                   | 否   | 平台的 API 金鑰，作為 `x-api-key` 傳送。不是持有人令牌：兩種驗證模式是 API 金鑰或 SigV4。              |
| `auth.aws_access_key_id` / `auth.aws_secret_access_key`                                                                                                                                                          | 否   | 明確的 SigV4 認證。設定其中一個而不設定另一個在啟動時失敗。`auth.aws_session_token` 與它們一起被接受。 |
| `base_url`                                                                                                                                                                                                       | 否   | 覆蓋衍生的端點                                                                                         |
| 因為平台解析第一方模型 ID，內建目錄無需 [`models:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models) 區塊即可路由到它。當您策劃 `models:` 清單時，使用第一方 ID 鍵入 `anthropicAws:` 項目。 |      |                                                                                                        |

#### Google Cloud Agent Platform

對於等效的用戶端設定，請參閱 [Claude Code on Google Cloud](https://code.claude.com/docs/zh-TW/google-vertex-ai)。閘道端上游：

```
upstreams:
  - provider: vertex
    region: us-east5
    project_id: example-prod
    auth: {}                           # 首選：應用程式預設認證
    # 或服務帳戶金鑰檔案：
    # auth: { service_account_json: /secrets/sa.json }
    # 覆蓋 aiplatform 端點以進行私人服務連線：
    # base_url: https://us-east5-aiplatform.p.googleapis.com

```

空的 `auth` 區塊使用應用程式預設認證：`GOOGLE_APPLICATION_CREDENTIALS`、GCE 中繼資料或 GKE 工作負載身分識別。支援服務帳戶 JSON 金鑰檔案但不建議；使用工作負載身分識別或將服務帳戶附加到 GCE 或 Cloud Run 執行個體。 設定 `region: global` 以使用 [Agent Platform 的全域端點](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)而不是區域端點。Google 然後將每個請求路由到可用的地區，因此您不追蹤每個地區的模型可用性。設定特定地區會將每個請求固定到它。

| 設定                   | 方式                                                                                                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IAM 權限               | 授予閘道的服務帳戶在專案上的 `roles/aiplatform.user`，或具有 `aiplatform.endpoints.predict` 的自訂角色。啟用 Agent Platform API (`aiplatform.googleapis.com`)。         |
| 模型存取               | 在 Model Garden 中，為您的專案啟用 Claude 模型。它們發佈到特定地區；檢查模型卡以了解支援的地區。                                                                        |
| GKE (工作負載身分識別) | 將 GCP 服務帳戶繫結到閘道的 Kubernetes 服務帳戶，並使用 `iam.gke.io/gcp-service-account: claude-gateway@<proj>.iam.gserviceaccount.com` 註釋 KSA。`auth: {}` 會拾取它。 |
| Cloud Run / GCE        | 將服務的服務帳戶設定為具有 `roles/aiplatform.user` 的帳戶。`auth: {}` 會拾取它。                                                                                        |
| 其他任何地方           | `auth: { service_account_json: /secrets/sa.json }`，JSON 金鑰檔案的路徑，掛載為祕密。該欄位採用檔案路徑，而不是金鑰內容，因此不涉及 `${file:…}` 擴展。                  |

#### Microsoft Foundry

對於用戶端 Foundry 部署，請參閱 [Claude Code on Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry)。閘道端上游：

```
upstreams:
  - provider: foundry
    resource: example-foundry              # https://example-foundry.services.ai.azure.com
    auth: { use_azure_ad: true }        # 首選：DefaultAzureCredential / 受管身分識別
    # 或 API 金鑰：
    # auth:
    #   api_key: ${FOUNDRY_API_KEY}

```

`use_azure_ad: true` 透過 `DefaultAzureCredential` 解析：AKS、ACI 或 App Service 上的受管身分識別；Azure CLI；或環境認證。API 金鑰有效但是專案範圍的，不會自動輪換。Foundry 的端點衍生自 `resource:`；設定選用的 `base_url` 以覆蓋它以進行主權雲，例如 Azure Government。

| 設定                   | 方式                                                                                                                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| RBAC                   | 授予閘道的身分識別在 Foundry 資源上的 `Azure AI User` 或 `Cognitive Services User`                                                                                                   |
| 部署                   | Foundry 使用管理員選擇的部署名稱，而不是規範模型 ID。新增 [`models:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models) 區塊，將每個規範 ID 對應到您的部署名稱。 |
| AKS (工作負載身分識別) | 將使用者指派的受管身分識別與叢集的 OIDC 簽發者聯合，並將其繫結到閘道的服務帳戶。`use_azure_ad: true` 透過 `WorkloadIdentityCredential` 拾取它。                                      |
| ACI / App Service      | 在資源上啟用系統指派或使用者指派的受管身分識別。`use_azure_ad: true` 會拾取它。                                                                                                      |
| 其他任何地方           | `auth: { api_key: "${FOUNDRY_API_KEY}" }`。在 `{ }` 內引用 `${…}`。                                                                                                                  |

#### 多個上游

相同的提供者可以出現多次，具有不同的 `name:`。這涵蓋不同的地區、透過不同認證鏈的不同帳戶、佈建輸送量與隨需，以及跨提供者故障轉移。 閘道按順序嘗試上游。`5xx`、`429`、`401`、`403`、`404`、逾時和遺漏端點 (`501`) 故障轉移；其他 `4xx` 不會。 `429` 是每個上游容量，因此佈建輸送量 (PT) 耗盡會故障轉移到隨需。如果您在上游上設定 [`forward_user_identity: true`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#per-user-identity-headers-for-a-proxy-you-run)，攜帶開發人員電子郵件的請求的 `429` 是每個使用者拒絕，而不是故障轉移。 `404` 是每個上游模型可用性，因此未啟用模型的上游不會阻止清單中稍後服務它的上游。無法解析所請求模型的上游會被跳過，無需網路往返。 此範例首先路由佈建輸送量 Bedrock 配額，溢出到隨需和第二個帳戶，最後故障轉移到 Anthropic API：

```
upstreams:
  # 主要：您主區域中的佈建輸送量。
  - name: bedrock-pt
    provider: bedrock
    region: us-east-1
    auth: {}
  # 溢出：隨需跨地區。
  - name: bedrock-od
    provider: bedrock
    region: us-west-2
    auth: {}
  # 不同帳戶：透過假設角色認證的單獨 Bedrock 配額。
  - name: bedrock-acct2
    provider: bedrock
    region: us-east-1
    auth:
      aws_access_key_id: ${ACCT2_AKID}
      aws_secret_access_key: ${ACCT2_SK}
  # 最後手段：直接 Anthropic API。
  - name: anthropic-fallback
    provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}

# 每個上游模型 ID 以上游的 `name:` 為鍵。
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    upstream_model:
      bedrock-pt: arn:aws:bedrock:us-east-1:111111111111:provisioned-model/abcdef
      bedrock-od: us.anthropic.claude-opus-4-8
      bedrock-acct2: us.anthropic.claude-opus-4-8
      anthropic-fallback: claude-opus-4-8

```

| 槓桿                                                                                                                                                                                           | 方式                                                                                                                                                                                                                                                                                                                                                               |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 不同地區                                                                                                                                                                                       | 每個地區一個 Bedrock 上游，每個都有自己的 `region:`。使用 [`auto_include_builtin_models: true`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models)，跨地區推論設定檔會自動路由；對於地區固定部署，使用 `models:` 區塊。                                                                                                                         |
| 不同帳戶                                                                                                                                                                                       | 每個帳戶一個 Bedrock 上游，每個在 `auth:` 中都有自己的認證。預設鏈 (`auth: {}`) 使用 Pod 的身分識別；對於第二個帳戶，設定明確認證或持有人令牌。                                                                                                                                                                                                                    |
| 佈建輸送量                                                                                                                                                                                     | 將模型對應到該上游名稱的 `models:` 中的佈建輸送量 ARN。其他上游保持隨需 ID，因此 PT 容量在故障轉移前耗盡。                                                                                                                                                                                                                                                         |
| VPC / FIPS 端點                                                                                                                                                                                | 在上游上設定 `base_url:` 為您的 VPC 端點或 FIPS 端點 URL                                                                                                                                                                                                                                                                                                           |
| 模型範圍路由                                                                                                                                                                                   | 只有自訂模型 `id`（不是內建 Claude 模型）會跳過其 `upstream_model:` 對應中不存在的上游。閘道按順序嘗試每個上游上的內建模型，並在對應中沒有項目時使用提供者的預設 ID，因此對於內建模型，對應改變上游接收的 ID 而不是是否嘗試它；拒絕 ID 的上游遵循與任何其他上游錯誤相同的[故障轉移規則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)。 |
| 在雲提供者之間或直接 Anthropic API 之間故障轉移會改變哪些協議、地理位置和其他條款管理請求。 CLI 對閘道應用相同的功能閘控，無論哪個上游服務給定請求，因此故障轉移不會傳送上游會拒絕的正文欄位。 |                                                                                                                                                                                                                                                                                                                                                                    |

## 選用區段

### `admin`

選用。啟用 `/v1/organizations/spend_limits`，其鏡像 Anthropic 的公開 Admin API，以及在 `/v1/messages` 上的每位開發者支出強制執行。請參閱[支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)以了解上限如何設定和強制執行；本區段涵蓋啟用該功能並調整它的 `gateway.yaml` 金鑰。

```
admin:
  # 用於 admin 端點的具名靜態 API 金鑰，以 x-api-key 形式傳送。
  # id 在稽核日誌中顯示為 admin-key:<id>，因此每個金鑰都
  # 可追蹤。陣列用於輪換：新增新金鑰、滾動用戶端、
  # 移除舊金鑰。
  write_keys:
    - { id: terraform, key: "${GATEWAY_ADMIN_WRITE_KEY_TF}" }
    - { id: ci,        key: "${GATEWAY_ADMIN_WRITE_KEY_CI}" }
  read_keys:
    - { id: reporting, key: "${GATEWAY_ADMIN_READ_KEY}" }
  # IdP 群組透過一般 gateway JWT（無 API 金鑰）授予完整 admin 存取權。
  admin_groups: [platform-finops]
  blocked_message: request an increase at https://go.example.com/claude-limits

```

| 欄位                      | 必要 | 說明                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write_keys`              | 否   | `{id, key}` 的陣列。符合其中一個的 `x-api-key` 可以列出、設定和刪除支出限制。金鑰值必須至少 32 個字元；`id` 在 `read_keys` 和 `write_keys` 中必須唯一。                                                                                                                                                                                                    |
| `read_keys`               | 否   | `{id, key}` 的陣列。唯讀：每個 `GET` 端點，包括列出上限、按 ID 擷取一個，以及讀取 [`/effective`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits#%2Feffective) 和 [`/audit`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits#%2Faudit)。                                                                           |
| `admin_groups`            | 否   | IdP 群組名稱。gateway JWT 的 `groups` 宣告包含其中一個的具有完整 admin 存取權（讀取和寫入），並稽核為 `oidc:<sub>`。將此用於人類 admin；將 API 金鑰用於機器。此清單中的空項目會在啟動時停止 gateway。請參閱[在啟動時停止 gateway 的匹配器值](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#matcher-values-that-stop-the-gateway-at-boot)。 |
| `blocked_message`         | 否   | 逐字附加到被阻止的開發者看到的 `429 billing_error`。寫入完整指示，例如 URL 或 Slack 頻道。未設定時，gateway 只傳送預設訊息。請參閱[強制執行如何運作](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits#how-enforcement-works)。                                                                                                          |
| `audit_retention_days`    | 否   | 預設 `365`。較舊的 `admin_audit` 列會被清除。                                                                                                                                                                                                                                                                                                              |
| `spend_retention_months`  | 否   | 預設 `13`。超過此時間的 `spend` 計數器列會被清除。預設值保留整整一年加上當月的部分月份，用於年度比較報告。                                                                                                                                                                                                                                                 |
| `identity_retention_days` | 否   | 預設 `90`。`principal_emails` 列的最後一次看到 TTL，其中保存每位開發者的電子郵件、顯示名稱和群組（PII）。刻意比支出保留期短，因此已取消佈建的身分會在其匿名支出計數器保留時過期。                                                                                                                                                                          |
| `group_limit_mode`        | 否   | `min`（預設）或 `max`。當開發者在多個具有上限的群組中時，`min` 強制執行最嚴格的，`max` 強制執行最寬鬆的。由強制執行和 `/effective` 使用。                                                                                                                                                                                                                  |

### `enforcement`

`enforcement` 區塊控制當存放區不可用時支出限制檢查的行為。

| 欄位                   | 必要 | 說明                                                                                                                                                                                                                                                                                                                                                               |
| ---------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fail_closed_on_error` | 否   | 預設 `false`。支出強制執行在 Postgres 中斷時失敗開放，因此推論保持運作。設定為 `true` 以失敗關閉：超過上限的開發者被阻止，但如果存放區無法到達，所有人也都被阻止。需要 [`admin:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin) 區塊：支出強制執行只在設定 `admin` 時執行，如果您在沒有 `admin` 的情況下設定此 `true`，gateway 會拒絕啟動。 |

### `pricing`

`pricing` 區塊告訴支出計量器要收費的金額而不是 USD 清單價格，因此上限和 [`/effective`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits#%2Feffective) 反映您的合約費率。金額保持為 USD，並保持為估計值，而非發票。兩個先決條件：

- gateway 伺服器上的 Claude Code v2.1.227 或更新版本。較早版本在啟動時拒絕未知金鑰。
- [`admin:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin) 區塊或在 v2.1.268 或更新版本中，具有至少一個原則的 [`managed:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed) 區塊。gateway 會拒絕在設定 `pricing` 且沒有任何區塊的情況下啟動，因為沒有任何東西會讀取它。

```
pricing:
  multiplier: 0.85
  overrides:
    - upstream: bedrock-eu
      model: claude-sonnet-4-6
      input: 3.30
      output: 16.50
      cache_read: 0.33
      cache_write: 4.125

```

| 欄位                   | 必要 | 說明                                                                                                                                                                                                                         |
| ---------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `multiplier`           | 否   | 預設 `1`。計量器將每個計量金額乘以此值，無論是清單定價還是覆蓋，因此 `0.85` 計費 85% 的價格。必須大於 0 且最多 10，值大於 1 是[標記價格上升](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#mark-prices-up)。 |
| `overrides`            | 否   | `{upstream, model, input, output, cache_read, cache_write}` 的列，單位為 USD 每百萬個 token。所有四個費率都是必要的。每個必須大於 0 且最多 10000。                                                                           |
| 計量器如何匹配覆蓋列： |      |                                                                                                                                                                                                                              |

- 列替換 `upstream`（[`upstreams[].name`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)）為 `model` 提供的請求的清單價格。這包括更高的[快速模式](https://code.claude.com/docs/zh-TW/fast-mode#understand-the-cost-tradeoff)費率，因此快速和標準請求以相同的四個費率計量。
- 內建 ID（例如 `claude-sonnet-4-6`）匹配方式類似 [`models[].id`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models)，涵蓋計量器定價為該模型的每個日期形式、區域 Amazon Bedrock 形式或 Google Cloud 的 Agent Platform 形式。任何其他字串（例如別名或推論設定檔 ARN）匹配用戶端傳送的 ID 或上游傳送的字串，不區分大小寫。
- 列重疊時，計量器選擇最具體的列而不是第一列：其 `model` 是上游傳送的確切模型字串的列，然後是匹配用戶端傳送的確切 ID 的列，然後是命名內建模型的列。
- 未知的上游名稱會導致啟動失敗，兩個列針對一個上游命名相同模型也會導致啟動失敗，包括一個內建模型的兩個拼寫。gateway 在啟動時警告沒有可請求模型可以使用的列。
- Web 搜尋請求保持在 $0.01 清單價格；乘數仍適用於它們。

對於每個區域費率，為每個區域提供自己的具名上游和每個上游一列。

#### 標記價格上升

使用 gateway 伺服器上的 v2.1.271 或更新版本，您可以將 `multiplier` 設定為大於 1，最多 10，以計量超過提供者收費的金額，例如內部退款費率。此範例以 120% 的價格計量每個請求：

```
pricing:
  multiplier: 1.2

```

使用 [`admin:`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin) 區塊，標記也適用於支出限制。計量器計數 120% 的價格，因此開發者更快達到其上限。gateway 在啟動時記錄警告，說明這一點。 乘數不會改變上游提供者對請求的收費。 如果 gateway 也[將費率傳送給已登入的用戶端](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#send-the-rates-to-signed-in-clients)，開發者需要 Claude Code v2.1.271 或更新版本才能看到標記。較早的用戶端忽略大於 1 的 `multiplier` 並顯示不含標記的成本。 早於 v2.1.271 的 gateway 伺服器會在您設定大於 1 的 `multiplier` 時拒絕啟動。

#### 將費率傳送給已登入的用戶端

使用 gateway 伺服器上的 v2.1.268 或更新版本，gateway 也將 `pricing` 中的費率放入它提供的 [`managed`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed) 原則中，作為 [`modelPricing`](https://code.claude.com/docs/zh-TW/settings-reference#modelpricing) 受管設定。由原則匹配的開發者隨後在 `/usage`、狀態列和 OpenTelemetry 中看到為提供每個模型 ID 的第一個上游的 `pricing` 費率。不符合任何原則的開發者不會收到受管設定，因此其數字保持在清單價格。用戶端在 Claude Code v2.1.242 或更新版本中應用設定。

- gateway 新增的內容：除非原則的 `cli` 區塊已設定 `modelPricing`，gateway 新增 `multiplier` 和用戶端可以請求的每個模型 ID 的第一個提供該 ID 的上游的覆蓋列。只有容錯移轉上游收費的費率保持在 gateway 上。
- 選擇一個原則退出：在該原則的 `cli` 區塊中將 `modelPricing` 設定為 `{}`，其開發者保持在清單價格。
- 保留原則自己的費率：其 `cli` 區塊使用自己的 `multiplier` 或 `overrides` 設定 `modelPricing` 的原則保留該 `modelPricing` 完整，gateway 不新增自己的費率到它。

### `models`

`models` 區塊是選用的 admin 策劃模型清單，在 `/v1/models` 提供並用於按上游轉譯模型 ID。對於非美國 Amazon Bedrock 區域、Amazon Bedrock 佈建輸送量 ARN 和 Microsoft Foundry 部署名稱是必要的。

```
auto_include_builtin_models: true   # false: expose only the list below
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    # description: optional text shown in clients that surface it
    upstream_model:
      anthropic: claude-opus-4-8
      bedrock: us.anthropic.claude-opus-4-8   # or an inference-profile ARN
      foundry: your-opus-deployment-name

```

`upstream_model` 下的每個金鑰必須符合已設定上游的 `name`，預設為提供者名稱。不符合任何上游的金鑰會導致啟動失敗，因此省略您不使用的提供者的列。

### `managed`

`managed` 區塊定義基於 IdP 群組或電子郵件網域的角色型存取原則。原則按順序評估；選擇第一個匹配，然後合併到 `match: {}` 全部捕捉基礎。它們按使用者在 `GET /managed/settings` 提供，具有 ETag/304 快取。

```
managed:
  policies:
    # Specific groups first.
    - match: { groups: [eng-contractors] }
      cli:
        availableModels: [claude-sonnet-4-6]
        permissions: { deny: ["WebFetch", "WebSearch"] }
    # Default catch-all last: matches everyone who authenticated.
    - match: {}
      cli:
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]

```

`match: {}` 全部捕捉，按慣例列在最後，被視為基礎層。每個其他原則從全部捕捉繼承它未設定的任何金鑰，因此每個角色項目只需列出與組織預設不同的內容。合併規則取決於金鑰類型：

- **允許清單** ：`availableModels` 和 `permissions.allow`。特定原則的清單完全替換基礎的。
- **拒絕清單和 hook 陣列** ：`permissions.deny`、`permissions.ask`、`disabledMcpjsonServers`、`deniedMcpServers`、`blockedMarketplaces` 和每個 `hooks` 事件類型陣列。這些取基礎和原則的聯集，因此組織範圍的拒絕或稽核 hook 不會被每個角色覆蓋意外丟棄。
- **記錄類型金鑰** ：`env`、`modelOverrides` 和 `skillOverrides`。這些淺合併，因此每個角色 `env` 區塊覆蓋它設定的金鑰並從基礎繼承其餘的。

`availableModels` 也在 `/v1/messages` 伺服器端強制執行，因此被拒絕的模型返回 `400`，無論用戶端傳送什麼。 gateway 在轉發請求之前驗證 `model` 值本身，因此格式不正確的值永遠不會到達上游。它在兩種情況下以 `400` 拒絕請求：

- 當值缺失或為空時，gateway 以訊息 `model is required` 拒絕請求。該檢查需要執行 Claude Code v2.1.228 或更新版本的 gateway。
- 當值存在但不是字串時，gateway 以訊息 `model must be a string` 拒絕請求。需要執行 Claude Code v2.1.221 或更新版本的 gateway。

| 匹配器                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 行為                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `match: {}`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 匹配每個已驗證的使用者。從其中一個開始，稍後在其上方新增群組範圍的原則。                         |
| `match: { groups: [a, b] }`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 如果 JWT 的 `groups` 宣告包含任何列出的群組，則匹配。區分大小寫：群組必須符合 IdP 的確切大小寫。 |
| `match: { email_domain: example.com }`                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 匹配 JWT 的 `email` 宣告中最後一個 `@` 之後的部分，不區分大小寫。每個原則接受一個網域。          |
| `match: { groups: [a], email_domain: example.com }`                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 兩個條件都必須匹配                                                                               |
| 不符合任何原則的已驗證使用者獲得 gateway 的預設值，這意味著目錄中的每個模型和沒有受管設定。如果您想要保證的預設原則，請在最後新增 `match: {}` 全部捕捉。                                                                                                                                                                                                                                                                                                                                                     |                                                                                                  |
| gateway 保留沒有自己的使用者目錄。它從使用者的 IdP 令牌授權每個請求，從令牌的 `groups` 宣告讀取群組成員資格並針對它評估原則。沒有名冊可列舉，沒有帳戶可預先建立，因此沒有 SCIM 端點，因為沒有東西可供 SCIM 同步到。在真實來源（您的 IdP 的原生 SCIM 佈建或專用身分治理平台）執行使用者和群組生命週期管理。那裡管理的成員資格和取消佈建透過令牌自動流入 gateway。如果您想要 Claude 帳戶本身的 SCIM 佈建，那是[Claude for Enterprise](https://code.claude.com/docs/zh-TW/admin-setup) 功能。兩個傳播時鐘適用： |                                                                                                  |

- **原則內容** ：編輯原則並重新部署在連接的用戶端的下一個受管設定輪詢時到達，在一小時內，除了[只在下一次啟動時適用的變更](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)
- **群組成員資格** ：變更使用者的群組成員資格變更哪個原則匹配他們。這在下一個工作階段重新鑄造時生效，意味著下一個無聲重新整理，受 `session.ttl_hours` 限制。

#### 在啟動時停止 gateway 的匹配器值

在啟動時，gateway 檢查每個原則的 `match` 區塊和 [`admin_groups`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#admin) 清單。這些值中的任何一個都會停止 gateway，並出現命名該欄位的錯誤：

- 空的 `groups` 清單
- `groups` 或 `admin_groups` 中的空項目
- 空的 `email_domain`
- 包含 `@`、空白或逗號的 `email_domain`。gateway 修剪值並在此檢查之前移除一個前導 `@`。寫入一個裸網域，例如 `example.com`。

在 v2.1.232 之前，gateway 以這些值啟動。每個值有此效果：

- 空的 `email_domain`：gateway 跳過網域檢查，因此具有空 `email_domain` 和沒有 `groups` 清單的原則匹配每個已驗證的使用者
- 空的 `groups` 清單：原則不匹配任何人
- 包含 `@`、空白或逗號的 `email_domain`：原則不匹配任何人
- `groups` 或 `admin_groups` 中的空項目：項目只在該使用者的 IdP `groups` 宣告也包含空項目時匹配使用者。在 `admin_groups` 中，該匹配授予 admin 存取權。如果您的 `admin_groups` 清單從未包含空項目，沒有人以此方式獲得 admin 存取權。

#### `cli` 中的內容

每個 `cli` 值是完整的 Claude Code `managed-settings.json` 文件，與您透過 MDM 或 `/etc/claude-code/managed-settings.json` 部署的相同架構，在此表示為 YAML。CLI 在受管層級應用傳遞的文件，在使用者和專案設定之上，代替伺服器受管設定。因此它忽略[限制於 OS 層級原則來源](https://code.claude.com/docs/zh-TW/server-managed-settings#current-limitations)的設定，例如 `policyHelper` 和 `wslInheritsWindowsSettings`。 gateway 在啟動時針對 CLI 的設定架構驗證每個文件，因此無法識別的頂層金鑰會導致啟動失敗，並出現命名每個違規金鑰的錯誤。架構的刻意開放部分仍接受任意值，因為較新的用戶端可能識別 gateway 的架構不識別的項目。這些開放金鑰包括 `env`、`pluginConfigs` 和 `permissions` 下的巢狀金鑰。 因為驗證使用與 gateway 已安裝版本捆綁的架構，將較新 Claude Code 版本引入的頂層設定金鑰放入受管設定需要先升級 gateway。在將新原則推出給所有用戶端之前，先在一個用戶端上進行煙霧測試。 完整金鑰參考在[Claude Code 設定](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)中。運營者首先尋求的金鑰：

```
managed:
  policies:
    - match: {}
      cli:
        # Model access (also enforced server-side at /v1/messages)
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]

        # Permission policy
        permissions:
          deny:
            - "WebFetch"
            - "Read(./.env)"
            - "Read(./secrets/**)"
          disableBypassPermissionsMode: disable   # blocks --dangerously-skip-permissions
        allowManagedPermissionRulesOnly: true     # ignore user/project permission rules

        # Environment pushed into the CLI process. DISABLE_UPDATES blocks
        # background and manual updates; DISABLE_AUTOUPDATER stops only
        # background updates.
        env:
          DISABLE_UPDATES: "1"                    # pin versions via your own distribution

        # Org-wide hooks. Hook commands run on developer machines, not the
        # gateway, so the path must exist on every client OS in the policy.
        hooks:
          PostToolUse:
            - matcher: "Edit|Write"
              hooks:
                - { type: command, command: /usr/local/bin/audit-edit.sh }

```

| 金鑰                                                                                   | 由以下強制執行 | 效果                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `availableModels`                                                                      | Gateway + CLI  | 模型允許清單。也在 `/v1/messages` 檢查，因此修補的用戶端無法繞過它。                                                                                                                                                                                                                                                                                                                      |
| `permissions.allow` / `.deny`                                                          | CLI            | 工具和命令規則。請參閱[權限](https://code.claude.com/docs/zh-TW/permissions)。                                                                                                                                                                                                                                                                                                            |
| `permissions.disableBypassPermissionsMode`                                             | CLI            | 設定為 `disable` 以阻止 [`bypassPermissions`](https://code.claude.com/docs/zh-TW/permission-modes#skip-all-checks-with-bypasspermissions-mode)，跳過權限提示的模式，以及 `--dangerously-skip-permissions` 旗標                                                                                                                                                                            |
| `allowManagedPermissionRulesOnly`                                                      | CLI            | 當 `true` 時，受管設定成為權限規則的唯一設定來源。[`allowManagedPermissionRulesOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedpermissionrulesonly) 項目列出 Claude Code 隨後忽略的每個來源。                                                                                                                                                                    |
| `env`                                                                                  | CLI            | 合併到 CLI 程序的環境變數。用於遙測、自動更新和模型名稱覆蓋。                                                                                                                                                                                                                                                                                                                             |
| `hooks`                                                                                | CLI            | 組織範圍的 [hooks](https://code.claude.com/docs/zh-TW/hooks)                                                                                                                                                                                                                                                                                                                              |
| `managedMcpServers`                                                                    | CLI            | 遠端 MCP 伺服器[提供給每個匹配的開發者](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings)以及他們自己新增的伺服器，`http` 和 `sse` 只。請參閱[原則中的 MCP 伺服器](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#mcp-servers-in-a-policy)。需要 gateway 伺服器和用戶端上的 Claude Code v2.1.259 或更新版本。較早的用戶端忽略金鑰。 |
| 因為這些設定透過網路到達，CLI 在應用下列列出的設定之前向每位開發者顯示安全核准對話框： |                |                                                                                                                                                                                                                                                                                                                                                                                           |

- `hooks`
- 需要開發者核准的 `env` 變數，例如代理和基礎 URL 變數
- 殼層執行設定，例如 `apiKeyHelper` 和 `statusLine`
- 沙箱二進位設定 `sandbox.bwrapPath`、`sandbox.socatPath` 和 `sandbox.ripgrep`
- 攔截流量、注入認證或削弱隔離的沙箱設定，例如 `sandbox.network.tlsTerminate` 和代理連接埠設定。[安全核准對話框](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)列出所有。

[核准記憶](https://code.claude.com/docs/zh-TW/server-managed-settings#approval-memory)涵蓋核准持續多長時間以及何時再次出現對話框。 Claude Code 應用某些傳遞的 `env` 變數而不向開發者顯示核准對話框，例如模型選擇設定和數值限制。其他傳遞的變數可能需要開發者的核准才能生效；非空代理、基礎 URL 或 `OTEL_EXPORTER_OTLP_ENDPOINT` 值總是如此。當傳遞的變數需要核准時，對話框命名它。 [環境變數和核准對話框](https://code.claude.com/docs/zh-TW/server-managed-settings#environment-variables-and-the-approval-dialog)有詳細資訊，包括四個隱私切換，其傳遞值決定它們是否需要核准。在 v2.1.218 之前，Claude Code 應用較少的變數而不詢問開發者，因此更多傳遞的變數觸發對話框。 gateway 的[遙測](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry)設定推送 `OTEL_EXPORTER_OTLP_ENDPOINT`，因此設定 `telemetry.forward_to` 在每個互動式用戶端上觸發對話框。對話框保護開發者的機器免受受損或敵對 gateway 的影響，而不是保護組織免受開發者的影響。 具有 `-p` 旗標的非互動式執行無法顯示對話框。它僅針對該執行應用推送的設定，不將其記錄為已核准，因此開發者的下一個互動式工作階段仍會顯示它們的對話框。在 v2.1.207 之前，非互動式執行將設定儲存為已核准，沒有後來的互動式工作階段顯示它們的對話框。 如果開發者拒絕，Claude Code 會退出該工作階段而不是應用原則。當您推送新 hook 或任何觸發對話框的 env 變數到廣泛原則時，Claude Code 因此向每個匹配的開發者顯示對話框。它在執行中的工作階段上在下一個每小時輪詢時顯示對話框，否則在開發者的下一次啟動時顯示。 `cli` 金鑰在較早版本中命名為 `settings`。該拼寫仍被接受為別名，但新部署應使用 `cli`。

#### 原則中的 MCP 伺服器

要向原則匹配的 Claude Code 用戶端提供 MCP 伺服器，在該原則的 `cli` 區塊中設定 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings)。您需要 gateway 伺服器和用戶端上的 Claude Code v2.1.259 或更新版本。 gateway 在啟動時使用[Claude Code 在用戶端應用的相同規則](https://code.claude.com/docs/zh-TW/managed-mcp#what-an-entry-can-contain)檢查每個項目，如果項目未通過檢查，gateway 會拒絕啟動並命名項目。 如果您在 `gateway.yaml` 中寫入 `${VAR}` 參考，gateway 在啟動時透過[秘密擴展](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#secret-expansion)從其環境解析它，然後執行項目檢查，因此每個匹配的用戶端接收字面值並可以讀取它。[提供伺服器的標頭指導](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings)適用於擴展值。 gateway 拒絕 `cli` 區塊中的 `.mcp.json` 拼寫 `mcpServers`，其啟動錯誤命名 `managedMcpServers` 為要使用的金鑰。在 v2.1.259 之前，gateway 拒絕 `cli` 區塊中的任何 MCP 伺服器定義。

#### Claude Desktop 覆蓋

如果您的組織也部署[Claude Desktop](https://code.claude.com/docs/zh-TW/desktop)，相同的 gateway 為兩個用戶端提供服務。在 Claude Desktop 的[受管設定](https://claude.com/docs/third-party/claude-desktop/configuration)中指向 `bootstrapUrl` 到 `<listen.public_url>/user/bootstrap`。Claude Desktop 從該 URL 衍生 OAuth 簽發者，針對此 gateway 執行相同的裝置代碼登入，並從回應擷取其設定。 需要 gateway 伺服器上的 Claude Code v2.1.203 或更新版本，以及明確的選擇加入：除非匹配使用者的原則帶有 `desktop` 金鑰，否則 `/user/bootstrap` 返回 404。空的 `desktop: {}` 選擇加入原則，`match: {}` 基礎層上的 `desktop` 金鑰選擇加入繼承它的每個原則。稽核日誌將每個請求記錄為 `desktop_bootstrap.serve` 或 `desktop_bootstrap.denied`。 gateway 從匹配原則的 `cli` 區塊和頂層 gateway 設定衍生大部分回應：

- 模型清單，來自 `availableModels`
- 已停用的工具，來自裸工具名稱 `permissions.deny` 項目。如果您在原則的 `desktop` 區塊中設定 `disabledBuiltinTools`，gateway 提供您的值和衍生清單的聯集，因此您可以透過此方式停用更多工具，但無法重新啟用您透過 `permissions.deny` 停用的工具
- 出口允許清單，來自 `sandbox.network.allowedDomains`。如果您在原則的 `desktop` 區塊中設定 `coworkEgressAllowedHosts`，gateway 使用該值而不是衍生清單
- 指向 gateway 本身的 OTLP 端點，以及已登入使用者的身分屬性。gateway 轉發它在該端點接收的匯出到您的 `forward_to` 目的地。當您同時設定 [`telemetry.forward_to`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry) 和 `listen.public_url` 時，它包括端點和屬性。 Claude Desktop 以一種編碼匯出每個信號：`http/protobuf`，或當您在原則的 `env` 中設定 `OTEL_EXPORTER_OTLP_PROTOCOL` 或其每個信號變體為 `http/json` 時為 `http/json`。在 gateway 伺服器上的 Claude Code v2.1.261 之前，回應設定 `http/json` 無論如何，因此只接受 protobuf 的收集器拒絕 Claude Desktop 的匯出

要在原則的 `desktop` 區塊中設定 `disabledBuiltinTools`、`coworkEgressAllowedHosts` 或 Claude Desktop 自己的 `managedMcpServers` 設定，您需要 gateway 伺服器上的 Claude Code v2.1.232 或更新版本。Claude Desktop 的 `managedMcpServers` 採用陣列值而不是物件。 gateway 省略沒有 Claude Desktop 等效項的金鑰，例如 `hooks` 和範圍權限規則（如 `Bash(npm *)`），來自啟動回應。 在 `cli` 旁邊新增選用的 `desktop` 區塊以直接設定 Claude Desktop 設定。從 Claude Desktop 的[受管設定參考](https://claude.com/docs/third-party/claude-desktop/configuration)寫入設定為平面金鑰名稱。省略 Claude Desktop 只從 MDM 或本機檔案讀取的金鑰，例如 `bootstrapUrl`；gateway 在啟動時拒絕它們。在 v2.1.232 之前，gateway 接受固定的 11 個功能閘道金鑰清單，例如 `chatTabEnabled` 和 `disableAutoUpdates`，並在啟動時拒絕每個其他金鑰。在 v2.1.227 之前，gateway 也在啟動時拒絕 `chatTabEnabled` 和 `chatAdvancedFileAnalysisEnabled`。

```
managed:
  policies:
    - match: { groups: [eng-contractors] }
      cli:
        availableModels: [claude-sonnet-4-6]
      desktop:
        isLocalDevMcpEnabled: false
        disableAutoUpdates: true
        banner: { text: "Contractor build: internal use only" }

```

每個金鑰都是選用的；Claude Desktop 為您省略的任何金鑰應用自己的預設值。gateway 在啟動時針對 Claude Desktop 本身使用的設定架構驗證每個 `desktop` 區塊，因此錯誤會在 gateway 啟動時作為命名金鑰的錯誤出現，而不是到達每個連接的桌面。當區塊包含以下內容時，gateway 在啟動時失敗：

- 未知金鑰
- 已識別的金鑰，其值 Claude Desktop 會拒絕或無聲丟棄，例如空值或巢狀項目內的拼寫錯誤的子金鑰。在 v2.1.260 之前，gateway 無聲丟棄 `managedMcpServers` 或 `orgPluginSettings` 項目的巢狀物件內的拼寫錯誤欄位，而不是在啟動時失敗。
- gateway 自己計算的金鑰：推論連接、模型清單和 OTLP 轉發。透過 [`upstreams`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstreams)、[`models`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#models) 和 [`telemetry`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry) 區塊的 `forward_to` 設定這些。
- 目前金鑰的舊版別名。在啟動錯誤中，gateway 命名規範金鑰以寫入。

如果您使用已棄用的值或項目形狀，例如沒有 `transport` 的 `managedMcpServers` 項目，gateway 啟動並記錄命名替換的警告。 gateway 針對與 `cli` 區塊相同的已安裝版本捆綁的架構驗證 `desktop` 區塊。要傳遞由較新 Claude Desktop 版本引入的設定，請先升級 gateway。例如，`userPluginMarketplacesEnabled` 和 `userPluginUploadsEnabled` 需要 gateway 伺服器上的 Claude Code v2.1.260 或更新版本以及成員機器上的 Claude Desktop 1.37937.0 或更新版本。 如果您在原則的 `desktop` 區塊中設定 `orgPluginSettings`，gateway 以 Claude Desktop 1.15200.0 及更新版本讀取的陣列形式提供它。較舊的桌面忽略陣列並強制執行沒有外掛工具原則，因此在依賴它之前將成員更新到 1.15200.0 或更新版本。 gateway 從原則的 `desktop` 區塊未設定的金鑰填入 `match: {}` 全部捕捉的 `desktop` 區塊，與它填入原則的 `cli` 區塊的方式相同。如果您在基礎和角色原則中都設定 `disabledBuiltinTools` 或 `builtinToolPolicy`，gateway 保留基礎的限制：

- `disabledBuiltinTools`：gateway 使用基礎清單和原則清單的聯集
- `builtinToolPolicy`：如果您在基礎中將工具設定為 `allow` 以外的值，gateway 保留該值，即使您在角色原則中為相同工具設定 `allow`

對於每個其他金鑰，如果您在角色原則中設定它，gateway 使用角色原則的值。gateway 完整替換陣列或巢狀物件（例如 `banner`），因此如果您在角色原則中設定 `banner.text`，gateway 丟棄基礎的 `banner.backgroundColor`。 如果您不部署 Claude Desktop，請完全從您的原則中省略 `desktop`；gateway 隨後從 `/user/bootstrap` 為每個使用者返回 404。

#### 與其他受管來源的優先順序

如果裝置也有 MDM 傳遞的原則或本機 `managed-settings.json`，gateway 傳遞的設定排名第一。[受管層級內的優先順序](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)在受管設定頁面上說明本機來源何時適用，並有[Claude Code 從每個 admin 來源讀取的金鑰](https://code.claude.com/docs/zh-TW/managed-settings#keys-read-from-every-admin-source)，無論它選擇哪個來源，例如沙箱鎖定金鑰、`forceRemoteSettingsRefresh` 和每個變數 `env` 合併。在 MDM 設定檔或受管設定檔案中設定的 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 只在 gateway 不傳遞設定時執行；項目說明其輸出替換什麼。 嵌入主機（例如[Claude Desktop](https://code.claude.com/docs/zh-TW/desktop)）可以透過 SDK `managedSettings` 選項提供原則。[來自嵌入主機的父設定](https://code.claude.com/docs/zh-TW/managed-settings#parent-settings-from-embedding-hosts)說明 Claude Code 何時應用它，以及[限制父設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway#restrict-parent-settings)列出哪些允許方向設定仍在沒有 `allowManaged*Only` 鎖定的情況下適用。 gateway 原則適用於機器上的每個 Claude Code 呼叫，包括非互動式 `claude -p` 執行和由 Agent SDK 衍生的工作階段。如果 gateway 在啟動時無法到達，已登入的工作階段會以錯誤退出，而不是在沒有其原則的情況下執行。

### `telemetry`

CLI 將指標、日誌和（啟用時）追蹤傳送到 gateway，gateway 逐字轉發它們到每個已設定的目的地。匯出使用 OpenTelemetry Protocol (OTLP) over HTTP。要跳過轉發並讓工作階段直接匯出到您的收集器，[在原則中命名收集器](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#export-directly-to-your-collector)。請參閱[監控使用](https://code.claude.com/docs/zh-TW/monitoring-usage)以了解 CLI 發出的指標和事件。 CLI 使用已驗證使用者的身分（從 gateway 簽發的 JWT 讀取）為每個匯出加上時間戳：`user.id`、`user.email` 和 `user.groups` 屬性。每位開發者的成本和使用歸因因此無需開發者端設定即可運作。 [Claude Desktop](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay) 和透過 gateway 登入的 Cowork 工作階段使用 `user.email` 和 `user.groups` 以及 `enduser.id` 為其遙測加上時間戳，因此您可以使用一個 `user.email` 或 `user.groups` 查詢涵蓋終端、Desktop 和 Cowork 使用。`user.groups` 是逗號分隔的 IdP 群組清單。 與來自 Claude Code 的所有 OpenTelemetry 資料一樣，這些屬性只進入您的組織設定的目的地，永遠不進入 Anthropic。 如果使用者的群組清單在百分比編碼後超過 255 個字元，或群組名稱包含逗號或等號，gateway 會從該使用者的 Desktop 和 Cowork 遙測中省略 `user.groups`，而不是截斷它。該使用者的終端工作階段仍帶有完整清單。 您需要 gateway 伺服器上的 Claude Code v2.1.265 或更新版本，以在 Desktop 和 Cowork 遙測上使用 `user.email` 和 `user.groups`，以及每位開發者機器上的 Claude Desktop 1.24012 或更新版本，以使用 `user.groups`。

```
telemetry:
  forward_to:
    - url: https://otel-collector.internal.example.com
      headers:
        Authorization: ${OTLP_TOKEN}
      # Per-signal opt-in. Default: metrics only.
      metrics: true
      logs: false
      traces: false
    - url: https://api.datadoghq.com/api/v2/otlp
      headers:
        DD-API-KEY: ${DD_API_KEY}

```

每個目的地獨立選擇加入 `metrics`、`logs` 和 `traces`，預設為僅指標。信號在敏感性上有所不同：

- **指標** ：彙總計數器，例如 token 計數、請求計數和延遲
- **日誌和追蹤** ：可以帶有完整 Bash 命令、工具輸入和檔案路徑，涵蓋 Claude Code 在開發者機器上執行的任何操作

僅在具有該資料保證的存取控制和保留原則的目的地啟用日誌和追蹤。 每個 `forward_to` URL 必須使用 `https://`，但有一個例外，適用於 gateway 自己的迴路介面上的收集器：

- `http://localhost:<port>` 通過設定驗證，但[SSRF 防護](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#threat-model-summary)使用 `ECONNREFUSED_SSRF` 阻止每個匯出，除非您在 gateway 的環境中設定 `CLAUDE_GATEWAY_ALLOW_LOOPBACK=1`
- `http://127.0.0.1:<port>` 或 `http://[::1]:<port>` 在未設定該變數的情況下啟動失敗

對於叢集內收集器，在其自己的內部位址上公開 HTTPS，或以設定變數的方式將其作為邊車執行。 遙測在 CLI 中預設關閉。當您同時設定 `telemetry.forward_to` 和 `listen.public_url` 時，gateway 透過 `/managed/settings` 推送六個環境變數來為連接的用戶端開啟它：

- `CLAUDE_CODE_ENABLE_TELEMETRY=1`
- `OTEL_METRICS_EXPORTER`、`OTEL_LOGS_EXPORTER` 和 `OTEL_TRACES_EXPORTER`，如果至少一個 `forward_to` 目的地啟用該信號，則每個設定為 `otlp`，否則設定為 `none`
- `OTEL_EXPORTER_OTLP_ENDPOINT=<public_url>`
- `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`

在 gateway 伺服器上的 Claude Code v2.1.265 之前，gateway 將所有三個匯出器選擇器推送為 `otlp`，包括沒有目的地選擇加入的信號。 推送的端點是從公開 URL 建立的，因此指標和日誌不需要開發者或原則的 OTEL 設定。 透過 `/login` 登入的開發者無法使用自己的 OTEL 設定重新導向匯出：

- **本機設定的變數** ：Claude Code 在受管層級應用推送的變數，因此每個變數覆蓋開發者為其本機設定的值。
- **本機設定的端點** ：啟用 OTLP/HTTP 匯出時，CLI 忽略任何本機設定的端點，無論 gateway 是否推送了遙測變數。其匯出進入 gateway，除非原則[將您的收集器命名為端點](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#export-directly-to-your-collector)。

沒有信號的 `forward_to` 目的地，gateway 接受並丟棄它。如果開發者已經將 Claude Code 遙測匯出到您的其中一個收集器，將其新增為 `forward_to` 目的地，如果他們匯出這些，則啟用日誌或追蹤，以便在他們登入後繼續接收其資料。要改為跳過轉發，[在原則中命名收集器](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#export-directly-to-your-collector)。 [追蹤](https://code.claude.com/docs/zh-TW/monitoring-usage#traces-beta)也需要每個用戶端上的 `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`。在受管原則的 `env` 區塊中設定它，因為 gateway 不推送它。開發者在已推送端點觸發的相同[安全核准對話框](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)中核准它。 僅在您想要追蹤的群組的原則中將其設定為 `1`。不設定它的原則從您的 `match: {}` 全部捕捉原則繼承值（如果該原則設定一個），根據[合併規則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)。要防止群組的用戶端傳送追蹤，即使開發者在本機設定變數，請在該群組的原則中將其設定為 `0`。 protobuf 和 JSON OTLP 編碼都被轉發，任何 OpenTelemetry 相容後端都可作為目的地。

#### 直接匯出到您的收集器

要讓透過 `/login` 登入的工作階段直接將遙測傳送到您的收集器而不是透過轉發，在[受管原則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)的 `env` 區塊中將 `OTEL_EXPORTER_OTLP_ENDPOINT` 設定為收集器的 `https://` 基礎 URL。Claude Code 將 `/v1/metrics`、`/v1/logs` 或 `/v1/traces` 附加到您設定的 URL，例如 `https://otel-collector.example.com:4318`，並透過 OTLP/HTTP 在那裡匯出每個信號。需要每位開發者機器上的 Claude Code v2.1.265 或更新版本。較早的用戶端透過轉發匯出。 要向收集器驗證，在相同的 `env` 區塊中設定 `OTEL_EXPORTER_OTLP_HEADERS`。工作階段永遠不會將開發者的 gateway 工作階段令牌傳送到以此方式命名的收集器。 當您在原則中新增或變更此端點時，Claude Code 在[安全核准對話框](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)中要求每位開發者核准它，然後才在互動式工作階段中應用它。 Claude Code 在匯出信號之前檢查端點，並在檢查失敗時將該信號保留在轉發上。檢查包括：

- 端點來自 gateway 本身。如果您在 MDM 設定檔或本機 `managed-settings.json` 中設定相同變數，匯出保留在轉發上。
- URL 使用 `https://`，或 `http://` 到迴路位址
- URL 解析為以 `/v1/<signal>` 結尾的路徑，沒有查詢或片段。Claude Code 從通用變數自己建立該路徑。它使用每個信號變數（例如 `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`）如寫入，因此在那裡包括完整路徑。
- URL 不是 gateway 自己的主機。指向 gateway 的端點保留轉發路徑及其工作階段令牌。
- 您和開發者都未在任何設定來源中設定 [`otelHeadersHelper`](https://code.claude.com/docs/zh-TW/settings-reference#otelheadershelper)。設定了助手，每個信號保留在轉發上。

您命名的端點只改變匯出的去向。您仍然使用 `OTEL_*_EXPORTER` 選擇器選擇哪些信號匯出。 端點本身不開啟匯出，因此也設定執行此操作的變數，除非 gateway 已推送它們：

- 如果 gateway 已[推送遙測變數](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#telemetry)，它們涵蓋啟用、選擇器和協定，您的明確端點覆蓋推送的 `<public_url>` 值。僅針對沒有 `forward_to` 目的地啟用的信號自己設定 `OTEL_*_EXPORTER` 選擇器為 `otlp`。
- 如果它沒有，也設定 `CLAUDE_CODE_ENABLE_TELEMETRY=1`、`OTEL_*_EXPORTER` 選擇器和 `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`。

當開發者登出或登入不同的 gateway 時，對收集器的匯出停止，Claude Code 丟棄每個剩餘批次，而不是晚期傳送它。

#### 當目的地失敗時

gateway 不緩衝、重試或儲存遙測，因此未到達目的地的匯出被丟棄，而不是晚期傳遞。每個目的地獨立成功或失敗，匯出用戶端無論如何都收到成功回應，因此失敗的傳遞只出現在 gateway 的日誌中。 在五次連續失敗傳遞到目的地後，gateway 在 30 秒的拉伸中暫停轉發到它，記錄每次暫停，直到傳遞成功。任何錯誤回應、逾時或連接錯誤都計為失敗傳遞，除了 `400`、`413`、`415`、`422` 和 `431`，這意味著收集器拒絕該匯出的承載為格式不正確或太大。 被拒絕的承載既不推進也不重設失敗計數：gateway 繼續轉發到目的地並記錄警告，命名它和狀態，在目的地的第一次拒絕和之後每一百次。

### HTTP 調整

四個選用的頂層區塊 `access_control`、`limits`、`timeouts` 和 `rate_limits` 調整 HTTP 表面。預設值適合大多數部署。

| 區塊                                                                                                                                                                                                                                                                                                                                               | 金鑰                                           | 預設     | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access_control`                                                                                                                                                                                                                                                                                                                                   | `allow_cidrs` / `deny_cidrs`                   | 空       | 按用戶端位址的入站 IP 允許/拒絕，在 `trusted_proxies` 解析後。`deny_cidrs` 首先檢查；符合它的用戶端被拒絕，即使 `allow_cidrs` 也匹配。如果 `allow_cidrs` 非空，gateway 是預設拒絕。`/healthz` 和 `/readyz` 豁免於 `allow_cidrs`。當受信任代理傳送不是 IP 位址的 `X-Forwarded-For` 項目時，真實用戶端未知，gateway 記錄一次警告，命名要檢查的內容。列表適用於請求的地方，它以 `403` 和稽核原因 `xff_unparseable` 拒絕它。列表都不適用的地方，它提供請求並使用代理自己的位址作為用戶端 IP，用於每 IP 速率限制和稽核。 |
| `limits`                                                                                                                                                                                                                                                                                                                                           | `max_request_bytes`                            | 32 MiB   | 最大入站請求本體；超大小請求在本體被緩衝之前獲得 `413`。為大型檔案或影像請求提高。                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `limits`                                                                                                                                                                                                                                                                                                                                           | `max_request_header_bytes`                     | 未設定   | 設定時，超大小標頭返回 `431`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `limits`                                                                                                                                                                                                                                                                                                                                           | `max_url_length`                               | 未設定   | 設定時，過長 URL 返回 `414`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `timeouts`                                                                                                                                                                                                                                                                                                                                         | `upstream_ttfb_ms`                             | 120000   | 等待上游回應標頭（首位元組時間）的最大時間。回應本體隨後以無牆鐘上限流式傳輸。適用於直接 Anthropic 上游路徑；每個其他提供者受其提供者 SDK 自己的逾時限制。                                                                                                                                                                                                                                                                                                                                                          |
| `rate_limits`                                                                                                                                                                                                                                                                                                                                      | `device_authorization.max` / `.window_seconds` | 30 / 600 | 未驗證裝置授權端點上的每 IP 速率限制。為共享出口 IP 或 NAT 後面的大型組織提高。這些限制僅適用於裝置授予登入流程，不適用於 `/v1/messages` 推論。請參閱[使用者代碼暴力破解抵抗](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#user-code-brute-force-resistance)。                                                                                                                                                                                                                                     |
| `rate_limits`                                                                                                                                                                                                                                                                                                                                      | `device_verify.max` / `.window_seconds`        | 10 / 600 | 在 `/device` 上 `user_code` 提交的每 IP 速率限制                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 如果您將兩個 `access_control` 清單都留空（這是預設值），gateway 為任何用戶端位址提供服務，因此只有您的網路限制誰可以到達它。這很重要，因為 gateway 可以推送[受管設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)，在開發者機器上執行命令。 當 `allow_cidrs` 為空時，gateway 在兩個地方警告，不改變它如何回答任何請求： |                                                |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

- **在啟動時** ：操作日誌中的警告建議僅允許私有範圍 `10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`、`100.64.0.0/10`、`127.0.0.0/8`、`::1/128` 和 `fc00::/7`，加上開發者連接的任何其他內部範圍。如果您將 gateway 綁定到迴路位址並設定 `trusted_proxies` 和 `public_url` 都不設定，如本機開發，警告不出現。
- **在執行時** ：第一次請求從位址外的範圍到達時，gateway 記錄警告並發出 [`access.public_client` 稽核事件](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#logs)，帶有用戶端 IP。兩者每個程序發生一次。連結本機位址 `169.254.0.0/16` 和 `fe80::/10` 不計為公開。gateway 在此檢查執行之前回答 `/healthz` 和 `/readyz`，因此來自公開範圍的健康探測不觸發它。

兩個信號都使用用戶端位址，因為 gateway 解析它。如果負載平衡器、連接埠轉發或隧道轉發流量且未列在 `listen.trusted_proxies` 中，gateway 看到轉發的位址，通常是私有的，因此既不是執行時警告也不是私有允許清單捕捉透過它轉發的流量。 在這樣的前端後面，首先設定 [`listen.trusted_proxies`](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#listen)，以便 gateway 看到真實用戶端位址，並無論如何保持 gateway 和其前面的所有東西無法從公開網際網路到達。

## 完整範例

此完整參考設定涵蓋每個核心部分；[HTTP 調整區塊](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#http-tuning)保持其預設值。複製它，刪除您不需要的內容，並填入您的值。[快速入門](https://code.claude.com/docs/zh-TW/claude-apps-gateway#quickstart)中的設定是此的最小版本。 gateway.yaml

```
# 執行方式：
#   claude gateway --config gateway.yaml
# # 操作日誌詳細程度由 CLAUDE_GATEWAY_LOG_LEVEL
# 環境變數控制（debug | info | warn | error；預設 info）。debug
# 也會記錄每個 id_token 中的宣告名稱，用於 groups_claim 診斷。
# 它不影響稽核事件，始終發出。

listen:
  host: 0.0.0.0
  port: 8080
  public_url: https://claude-gateway.internal.example.com
  # 在 TLS 終止入口後面執行時省略 tls 區塊。
  # tls:
  #   cert: /certs/gateway.crt
  #   key: /certs/gateway.key
  # trusted_proxies:
  #   - 10.0.0.0/8

oidc:
  issuer: https://example.okta.com
  client_id: 0oa1example2
  client_secret: ${OIDC_CLIENT_SECRET}
  allowed_email_domains:
    - example.com
  # 當簽發者是 Okta 組織伺服器時需要，其 id_tokens
  # 可以省略電子郵件和群組；閘道從 /userinfo 填充它們。
  userinfo_fallback: true
  # allowed_groups: [claude-code-users]
  # Okta 僅在請求 `groups` 範圍且
  # 應用程式的群組宣告篩選允許它們時發出群組。下面的承包商原則
  # 符合群組，因此此處請求範圍。
  scopes: [openid, profile, email, offline_access, groups]
  # extra_auth_params: { access_type: offline, prompt: consent }  # Google
  # groups_claim: groups          # Entra 應用程式角色：使用 `roles`
  # email_claim: email

session:
  jwt_secret: ${GATEWAY_JWT_SECRET}   # openssl rand -base64 32
  # ttl_hours: 1

store:
  postgres_url: ${GATEWAY_POSTGRES_URL}
  # max_connections: 5

# 啟用 /v1/organizations/spend_limits（鏡像 Anthropic Admin API）
# 和 /v1/messages 上的每個開發人員支出強制執行。省略以停用。
# 上限本身透過 admin API 設定，而不是此處。
# admin:
#   write_keys:
#     - { id: terraform, key: "${GATEWAY_ADMIN_WRITE_KEY_TF}" }
#   read_keys:
#     - { id: reporting, key: "${GATEWAY_ADMIN_READ_KEY}" }
#   admin_groups: [platform-finops]
#   blocked_message: request an increase at https://go.example.com/claude-limits
#   # audit_retention_days: 365
#   # spend_retention_months: 13
#   # identity_retention_days: 90
#   # group_limit_mode: min

# enforcement:
#   fail_closed_on_error: false

# 以合約費率而非美元標價計費。需要 admin: 或
# managed: 原則。使用 managed:，相同費率也會傳送給已登入的用戶端。
# 下面的費率是佔位符，不是真實合約價格。
# pricing:
#   multiplier: 0.85
#   overrides:
#     - { upstream: anthropic, model: claude-sonnet-4-6, input: 3.30, output: 16.50, cache_read: 0.33, cache_write: 4.125 }

upstreams:
  - provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}

  # - provider: bedrock
  #   region: us-east-1
  #   auth: {}

  # - provider: anthropicAws
  #   region: us-east-1
  #   workspace_id: wrkspc_...
  #   auth:
  #     api_key: ${ANTHROPIC_AWS_API_KEY}

  # - provider: vertex
  #   region: us-east5
  #   project_id: example-prod
  #   auth: {}

  # - provider: foundry
  #   resource: example-foundry
  #   auth: { use_azure_ad: true }

auto_include_builtin_models: true
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    upstream_model:
      anthropic: claude-opus-4-8
      # bedrock: us.anthropic.claude-opus-4-8
      # anthropicAws: claude-opus-4-8
      # vertex: claude-opus-4-8
      # foundry: <your-opus-deployment-name>
  - id: claude-sonnet-4-6
    label: Claude Sonnet 4.6
    upstream_model:
      anthropic: claude-sonnet-4-6
  - id: claude-haiku-4-5
    label: Claude Haiku 4.5
    upstream_model:
      anthropic: claude-haiku-4-5

managed:
  policies:
    - match: { groups: [contractors] }
      cli:
        availableModels: [claude-haiku-4-5]
        # 將預設選擇器選項限制為 availableModels 而不是
        # 層級預設，因此承包商不會在預設上獲得 400。
        enforceAvailableModels: true
        # allow 自動批准這些工具；它不阻止其餘的。
        # 新增 deny 規則以限制工具。
        permissions: { allow: [Read, Grep] }
    - match: {}
      cli:
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]
        permissions:
          allow: [Read, Grep, Bash, Edit]
          deny: ["WebFetch"]
        env: { HTTP_PROXY: http://proxy.example.com:8080 }

telemetry:
  forward_to:
    - url: https://otel.internal.example.com:4318
      headers:
        Authorization: Bearer ${OTEL_TOKEN}

```

## 用戶端受管設定

上面的所有內容設定閘道伺服器。將開發人員機器指向它在每個裝置上單獨設定，透過 Claude Code 的[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)。閘道無法自己推送登入鍵，因為它們是告訴用戶端閘道在哪裡的內容。 對於 CLI，在每個 OS 的 `managed-settings.json` 中設定這些鍵。這兩個登入鍵將每個開發人員的 `/login` 路由到您的閘道：

```
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com",
  "parentSettingsBehavior": "merge"
}

```

`parentSettingsBehavior: "merge"` 保持 Claude Desktop 將出站允許清單傳遞到其嵌入式 Claude Code 工作階段的功能；[將原則傳遞到 Claude Desktop 工作階段](https://code.claude.com/docs/zh-TW/claude-apps-gateway#deliver-policy-to-claude-desktop-sessions)說明了機制以及選擇加入必須位於何處。 將 `managed-settings.json` 檔案部署到每個裝置，通常透過您的 MDM 平台。檔案路徑因平台而異。請參閱[每個機制儲存原則的位置](https://code.claude.com/docs/zh-TW/managed-settings#where-each-mechanism-stores-the-policy)。 根據預設，Windows 上的登錄原則或 macOS 上的受管偏好設定 plist 會取代 `managed-settings.json` 檔案，而不是與其合併，除了[上面的例外鍵和跨來源檢查](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#precedence-with-other-managed-sources)。此程式碼片段中的所有三個鍵都遵循最高優先順序來源規則，因此透過群組原則或設定檔傳遞原則的機隊必須改為在該機制中放置全部三個。 對於 Claude Desktop，在 Claude Desktop 自己的[受管設定](https://claude.com/docs/third-party/claude-desktop/configuration)中設定 `bootstrapUrl` 鍵為 `<listen.public_url>/user/bootstrap`。登入流程和每個群組原則在原則透過 `desktop` 鍵在伺服器端選擇加入後，與 CLI 的相符；沒有選擇加入，`/user/bootstrap` 會傳回 404。請參閱[Claude Desktop 覆蓋層](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay)以了解伺服器端部分。 Claude Code 僅從機器上的受管來源尊重 [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl)、[`gatewayInternalNetworks`](https://code.claude.com/docs/zh-TW/settings-reference#gatewayinternalnetworks) 和 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 的 `"gateway"` 值：`managed-settings.json`、macOS plist 或 Windows HKLM 登錄，或原則協助程式。開發人員在自己的 `~/.claude/settings.json` 中設定它們無效，在閘道承載中設定它們也無效。

## 相關

- [Claude 應用程式閘道概述](https://code.claude.com/docs/zh-TW/claude-apps-gateway)：快速入門和開發人員連接
- [部署指南](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy)：IdP 設定、容器映像、Kubernetes 和 Cloud Run，以及操作
- [支出限制](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)：每個開發人員上限和 Admin API

是否 助手
