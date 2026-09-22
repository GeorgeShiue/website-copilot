自託管環境在 Team 和 Enterprise 方案上處於公開測試版；[可用性和限制](https://code.claude.com/docs/zh-TW/self-hosted-environments#availability-and-limitations)涵蓋啟用路徑。本頁面涵蓋在生產環境中執行執行器群；請參閱[快速入門](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart)以了解您的第一個執行器和工作階段。 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)在您部署在網路內的執行器上執行 Claude Code [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，在生產環境中，這些工作階段代表所有可以向環境分派工作階段的人執行模型導向的程式碼。本頁面適用於將正常運作的環境帶入生產環境的操作員。它按部署順序進行：在連接真實系統之前要鎖定什麼、執行器群需要的出站流量、工作階段如何向您的 Git 主機進行身份驗證、部署配方本身，以及當工作階段出現故障時要檢查什麼。

## 強化您的部署

自託管執行器代表所有可以向其環境分派工作階段的人在您的基礎設施上執行任意的、模型導向的程式碼。這是您 Anthropic 組織的任何成員，以及任何可以在所有者路由到環境的範圍內啟動 [Claude Tag](https://claude.com/docs/claude-tag/overview) 頻道工作階段的人。在將環境連接到生產系統之前，請逐項進行：

- **臨時的、每個工作階段的容器** ：在新鮮容器或 VM 中執行每個執行器程序，該容器或 VM 在程序退出時被銷毀，使用 `--capacity 1` 和預設的 `--drain-grace-sec 0`，以便每個容器恰好服務一個工作階段。在更高的容量或正的清空寬限期下，一個容器服務來自同一[鎖定所有者](https://code.claude.com/docs/zh-TW/self-hosted-environments#key-concepts)的多個工作階段；請參閱[執行器生命週期](https://code.claude.com/docs/zh-TW/self-hosted-environments#runner-lifecycle)。不要在執行器重新啟動之間重複使用檔案系統，除非在刻意的[預熱簽出](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#reuse-a-pre-warmed-checkout)設定中，並且永遠不要跨所有者。
- **映像中沒有廣泛的認證** ：不要包含長期的 SSH 金鑰、雲端提供商認證或授予超過工作階段需要的個人存取令牌。在工作階段期間使用的薄荷認證，例如推送或 API 令牌，從您的[包裝器指令碼](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#wrapper-scripts)按工作階段進行。對於在包裝器執行之前發生的初始複製，使用 [`checkout` 生命週期鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#checkout)或 [`--use-anthropic-git-proxy`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#use-the-anthropic-git-proxy)；請參閱[配置 Git](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git)。
- **將環境祕密保留在執行工作階段的主機之外** ：環境祕密可以註冊執行器並拾取在環境上排隊的任何工作階段。在固定群中，它存在於每個執行器主機上，任何工作階段的程式碼都可以讀取祕密檔案。優先使用[按需執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#on-demand-runners)，其中祕密保留在協調器主機上，該主機永遠不執行使用者程式碼，每個執行器接收單次使用的工作單據，該單據恰好註冊一個執行器。在固定群中，將環境祕密檔案視為可由每個工作階段讀取，並在任何懷疑的工作階段洩露後輪換祕密。
- **預設拒絕網路出站流量** ：在每個環境上限制執行器和工作階段容器的出站流量在您自己的網路邊界；[預設拒絕出站流量](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#default-deny-egress)涵蓋允許什麼以及為什麼。
- **最小權限主機 IAM** ：附加到執行器主機的計算身份，例如執行個體設定檔或節點服務帳戶，應僅授予執行器本身需要的內容。工作階段應通過您的包裝器指令碼而不是繼承主機的身份來獲得自己的認證。
- **阻止工作階段的雲端中繼資料端點** ：將工作階段保留在主機身份之外需要阻止它們對雲端中繼資料端點的存取，子網級出站流量原則不會攔截連結本地中繼資料流量，因此在容器本身中阻止它：
  - IMDSv2，跳數限制為 1
  - GKE Workload Identity，具有中繼資料隱藏
  - 工作階段容器網路命名空間中 `169.254.169.254` 的明確拒絕 該阻止也適用於您的包裝器指令碼和生命週期鉤子，因為它們共享容器。使用[工作階段 JWT](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)對您自己的令牌服務進行身份驗證，通過允許列表出站流量，或使用基於檔案的 Web 身份，例如 Amazon EKS 上的 IAM Roles for Service Accounts (IRSA)。
- **每個執行器的檔案系統隔離** ：每個執行器程序獲得自己的工作目錄，主機上沒有其他程序可以讀取或寫入。使 `--hooks-dir`、包裝器指令碼和主機的 `~/.claude/` 對工作階段唯讀，無論是內置在映像中還是以唯讀方式掛載。
- **分派沒有每個環境的存取控制** ：您 Anthropic 組織的任何成員都可以向其任何環境分派工作階段。如果所有者[將 Claude Tag 頻道路由到環境](https://code.claude.com/docs/zh-TW/cloud-environments#set-the-environment-a-claude-tag-channel-uses)，[Claude Tag 存取設定](https://claude.com/docs/claude-tag/admins/restrict-access#restrict-who-can-use-claude)允許的任何人都可以啟動在那裡執行的頻道工作階段。預設情況下，這是連接的 Slack 工作區中的任何人，無論是否有 Claude 帳戶。將每個執行器主機視為可由所有可以向其分派的人進行程式碼執行，並且只在執行器主機上放置所有這些人都被允許讀取的資料和認證。[`--lock-to-account`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)限制給定主機執行哪個帳戶的工作階段，但它不會縮小誰可以分派到環境中。要使自託管環境成為唯一的選擇器選項，[所有者](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)可以從[**雲端環境** 頁面](https://claude.ai/admin-settings/cloud-environments)隱藏整個組織的 Anthropic 託管環境。
- **強制執行儲存庫設定防護** ：使用 [`--confine-repo-settings`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)選擇防護模式。預設的 `warn` 記錄違規並仍然生成工作階段，`enforce` 拒絕工作階段，`off` 禁用掃描。執行器掃描每個儲存庫的已提交設定以查找：
  - 在該工作階段自己的工作區之外解析的授予：`additionalDirectories` 項目、`permissions.allow` 中的 `Edit`、`Write` 或 `NotebookEdit` 規則，或 `sandbox.filesystem.allowWrite` 或 `allowRead` 項目
  - 非空的 `env` 塊
  - 操作員姿態覆蓋，例如 `sandbox.enabled: false` 防護無論 [`--trust-workspace`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)如何都會執行，並且不涵蓋儲存庫鉤子、`.mcp.json` 或 Bash 規則；請參閱[權限和工具批准](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#permissions-and-tool-approval)以了解這些授予應該在哪裡。

您組織的 IP 允許列表預設不涵蓋自託管執行器流量。不要依賴它作為執行器或工作階段流量的網路控制；改為在您自己的網路邊界應用預設拒絕出站流量，如果您想要為您的組織強制執行 IP 允許列表，請聯繫您的 Anthropic 帳戶團隊。

## 網路要求

執行器及其生成的工作階段子項進行出站連接到以下主機。將工作階段容器出站流量限制為這些主機和工作階段需要到達的特定內部服務；[預設拒絕出站流量](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#default-deny-egress)涵蓋如何以及為什麼。 這些主機始終是必需的：

| 主機                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 連接埠                            | 用途                                                                                                                                                                                                                                                                                                                                                               |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `api.anthropic.com`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 443、HTTPS；WSS 僅用於 SCM 連接器 | 執行器控制平面和工作階段串流、模型推理、功能旗標、產品分析、[JWKS](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)金鑰提取、提交簽名、設定 `--use-anthropic-git-proxy` 時的 Git 代理，以及設定 `--scm-connector-host` 時協調器的 [SCM 連接器](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#scm-connector-flags)隧道 |
| 您的 Git 主機，例如 `github.com` 或您的 GitHub Enterprise 主機                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 443 或 22                         | 複製和推送儲存庫。如果執行器使用 `--use-anthropic-git-proxy`（將 Git 流量路由通過 `api.anthropic.com`）則不需要。                                                                                                                                                                                                                                                  |
| 這些主機是否需要取決於您的配置：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                   |                                                                                                                                                                                                                                                                                                                                                                    |
| 主機                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 連接埠                            | 何時需要                                                                                                                                                                                                                                                                                                                                                           |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | ---                               | ---                                                                                                                                                                                                                                                                                                                                                                |
| `downloads.claude.ai`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 443                               | 在安裝時，當您使用原生安裝程式在主機上安裝或更新 Claude Code 時；`install.sh` 指令碼本身是從 `claude.ai` 提供的。在工作階段執行時，僅當工作階段從官方 Anthropic 市場安裝外掛程式時。                                                                                                                                                                               |
| `storage.googleapis.com`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 443                               | 在工作階段執行時，用於 `/plugin` 中顯示的外掛程式安裝計數和中繼資料。                                                                                                                                                                                                                                                                                              |
| `code.claude.com` 和 `claude.com`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 443                               | 內置 claude-code-guide 代理的文件查詢和工作階段期間預先批准的 WebFetch 請求。阻止這些主機只會影響文件查詢。                                                                                                                                                                                                                                                        |
| `*.frame.claudeusercontent.com`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 443                               | 僅當[工件工具](https://code.claude.com/docs/zh-TW/artifacts#availability)對您組織中的工作階段可用時；預設值因方案而異，根據那裡的可用性表。在執行器上設定 `CLAUDE_CODE_DISABLE_ARTIFACT=1` 以保持工具禁用，無論組織設定如何。                                                                                                                                      |
| `registry.npmjs.org`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 443                               | 當工作階段安裝外掛程式時，用於提取 npm 源外掛程式套件和安裝外掛程式的 Node.js 依賴項，或當 `npx` 啟動的 MCP 伺服器執行時                                                                                                                                                                                                                                           |
| `http-intake.logs.us5.datadoghq.com`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 443                               | Anthropic 操作指標。僅當設定 `CLAUDE_CODE_BYOC_ENABLE_DATADOG=1` 時；在自託管環境中預設關閉。                                                                                                                                                                                                                                                                      |
| `browser-intake-us5-datadoghq.com`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 443                               | Anthropic 錯誤報告上傳，僅在為工作階段帳戶啟用[錯誤報告](https://code.claude.com/docs/zh-TW/data-usage#telemetry-services)時發送。由 `DISABLE_ERROR_REPORTING=1` 或 `DISABLE_TELEMETRY=1` 抑制。                                                                                                                                                                   |
| 執行器不會到達 `statsig.anthropic.com`、`*.sentry.io`、`claude.ai` 或 `platform.claude.com`。這些主機出現在一些較舊的企業網路檢查清單中，但您不需要為執行器或工作階段流量允許列表它們：功能旗標提取進入 `api.anthropic.com`，執行器使用環境祕密而不是互動式 OAuth 進行身份驗證。兩個主機端流確實到達 `claude.ai`，因此從其出站流量允許的主機執行它們，而不是擴大工作階段容器出站流量：單行安裝程式在安裝時從 `claude.ai` 提取 `install.sh`，互動式 `claude auth login`（[引導式設定](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart#set-up-an-environment-and-runner)、`doctor` 的已登入模式和 [CI 分派](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing#authenticate-from-ci)使用）通過 `claude.ai`、`claude.com` 和 `platform.claude.com` 登入。`mcp-proxy.anthropic.com` 也不是必需的：自託管工作階段不使用它，當為您的組織啟用時，將您的組織 claude.ai 連接器傳遞到工作階段通過 `api.anthropic.com` 路由。請參閱 [MCP 伺服器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#mcp-servers)。 |                                   |                                                                                                                                                                                                                                                                                                                                                                    |

### 預設拒絕出站流量

在網路區段或命名空間中部署執行器和工作階段容器，其出站流量限制為[網路要求表](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#network-requirements)中的主機、您的 Git 主機和工作階段需要到達的特定內部服務。該產品無法驗證或強制執行此操作，因此在每個環境上的您自己的網路邊界應用它。工作階段程式碼是模型導向的，可以嘗試連接到任意主機；網路層的預設拒絕出站流量限制這些嘗試可以到達的位置。這無論權限模式如何都適用：預設預先批准的工具集已包括 `Bash`，因此 shell 出站流量在沒有[自動模式](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#permissions-and-tool-approval)的情況下執行而不提示。 有關每個工作階段發出的遙測詳細資訊以及如何關閉它，請參閱[遙測](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#telemetry)。

### 向出站代理進行身份驗證

某些企業出站代理在每個連接上需要 `Proxy-Authorization` 標頭。該標頭中的令牌通常輪換得太快，無法寫入您在 `HTTPS_PROXY` 中設定的代理 URL。像往常一樣將 `HTTPS_PROXY` 或 `HTTP_PROXY` 設定為您的代理 URL，然後設定 `--proxy-authorization-command` 或 `--proxy-authorization-file` 以告訴執行器從何處讀取標頭值。兩個旗標都需要 Claude Code v2.1.238 或更新版本。

#### 選擇 `Proxy-Authorization` 值的來源

選擇與您如何產生 `Proxy-Authorization` 令牌相符的旗標：

- **[`--proxy-authorization-command <command>`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)**：為您按需生成的令牌選擇此項。執行器執行 shell 命令並使用其修剪的 stdout 作為標頭值，例如`Bearer <token>` 。
- **[`--proxy-authorization-file <path>`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)**：為另一個程序在原位輪換的令牌選擇此項。執行器讀取檔案並使用其修剪的內容作為標頭值。

#### 執行器拒絕啟動的配置

每個旗標也有環境變數形式，在[執行器 CLI 旗標參考](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)中列在其旁邊。在執行器聯繫您的代理或控制平面之前，它檢查旗標及其變數，並在三種情況下拒絕啟動：

- **兩個旗標都設定** ：一個旗標加上另一個旗標的環境變數計為設定兩個。
- **沒有代理 URL** ：`HTTPS_PROXY` 和 `HTTP_PROXY` 都不包含 `http://` 或 `https://` URL。執行器以大寫或小寫讀取兩個變數，不查詢 `ALL_PROXY`。
- **任一旗標傳遞給協調器子命令** ：`self-hosted-runner orchestrator` 不接受旗標或其環境變數。改為將旗標傳遞給協調器啟動的每個執行器。

#### 設定代理授權旗標時執行器更改的內容

設定任一旗標後，執行器啟動自己的偵聽器並通過該偵聽器發送來自自己、其生命週期鉤子和其工作階段的代理流量。偵聽器在前往您的代理的途中添加 `Proxy-Authorization` 標頭。

- **偵聽器** ：偵聽器是 `127.0.0.1` 上的轉發代理。執行器在向控制平面註冊之前啟動偵聽器，如果偵聽器無法啟動則在啟動時退出。
- **代理變數** ：執行器重寫您設定的 `HTTPS_PROXY` 和 `HTTP_PROXY` 中的任一個，使其指向偵聽器。該重寫的值到達執行器本身、其生命週期鉤子和它執行的每個工作階段。
- **令牌輪換** ：輪換的令牌無需重新啟動即可生效。對於偵聽器打開到您的代理的每個連接，執行器再次執行您的命令或讀取您的檔案並將結果添加為標頭。
- **工作階段環境** ：工作階段僅通過偵聽器到達您的代理。在每個工作階段的環境中，執行器移除 `ALL_PROXY`、移除您未設定的 `HTTPS_PROXY` 或 `HTTP_PROXY` 的任何拼寫，並將 `NO_PROXY` 固定到執行器自己的值。
- **日誌** ：執行器永遠不會記錄標頭值。

## 配置 Git

執行器管理儲存庫簽出但預設不配置 Git 身份或認證。您控制執行器的映像和程序環境，因此您控制 Git 配置。選擇兩種方法之一：

- **讓執行器配置 Git** ：使用 `--configure-git` 啟動執行器，以使其寫入 Anthropic 託管工作階段使用的相同身份和提交簽名配置
- **在映像中提供 Git 配置** ：自己設定身份和推送認證，例如在您自己的機器人身份下提交

執行器主機上的 Git 版本下限：[`--configure-git`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#let-the-runner-configure-git) SSH 提交簽名需要 Git 2.34 或更新版本，[`--use-anthropic-git-proxy`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#use-the-anthropic-git-proxy) 需要 2.32 或更新版本，從 [`--push-outcome-on-release`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 推送的分支恢復工作階段需要 2.29 或更新版本。如果您省略所有三個並自己管理 Git 身份，Git 2.24 就足夠了。

### 讓執行器配置 Git

使用 `--configure-git` 啟動執行器，或設定 `SELF_HOSTED_RUNNER_CONFIGURE_GIT=1`，以使其在啟動時寫入全域 Git 配置：

- `user.name = Claude` 和 `user.email = noreply@anthropic.com`，與 Anthropic 託管工作階段相符
- SSH 格式提交和標籤簽名，通過執行器管理的填充程式路由，該填充程式使用工作階段自己的認證通過 Anthropic 的簽名服務簽名每個提交。簽名可在 GitHub 上針對 Anthropic 的已發佈 SSH 簽名金鑰進行驗證。
- `push.negotiate = true`，因此 Git 在打包推送之前詢問您的 Git 主機它已經擁有哪些提交。需要 Claude Code v2.1.257 或更新版本。
- `core.hooksPath` 指向執行器管理的鉤子目錄。其 `commit-msg` 和 `prepare-commit-msg` 鉤子為每個提交添加 `Co-authored-by:` 預告片，用於工作階段的建立者，從 [`CCR_SESSION_ACCOUNT_EMAIL`](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#wrapper-scripts) 構建，當該變數未設定時省略。如果您的映像已設定 `core.hooksPath`，執行器保留您的設定，跳過安裝這些鉤子，並列印 `[runner:git]` 警告。

提交簽名需要 Git 2.34 或更新版本；執行器在啟動時檢查並在您的 Git 較舊時以錯誤退出。此旗標不配置推送認證，您仍在映像中提供。

### 在映像中提供 Git 配置

Git 身份對任何提交都是必需的。在您的 Dockerfile 中系統範圍設定它，以便配置無論執行器程序以哪個使用者身份執行都適用：

```
RUN git config --system user.name "Claude" && \
    git config --system user.email "noreply@anthropic.com"

```

沒有身份，`git commit` 失敗並顯示 `Please tell me who you are`，工作階段無法取得進展。您可以改用自己的機器人身份；執行器不會覆蓋這些值。 不要將長期或廣泛範圍的推送認證烘焙到共享執行器映像中：映像中的認證可用於映像執行的每個工作階段，無論誰啟動它。相反，使用工作階段 JWT 從您的[包裝器指令碼](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#wrapper-scripts)按工作階段薄荷短期、最小範圍的令牌，使用從工作階段 JWT 解碼的工作階段建立者的身份。將其與臨時的每個工作階段容器配對，這需要 `--capacity 1`，因此沒有認證超過薄荷它的工作階段；請參閱[強化部分](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)。 如果您必須在映像級別配置推送認證，例如對於唯讀部署金鑰，請盡可能緊密地限制它們：

- SSH 部署金鑰限制為一個儲存庫，帶有 `url.<base>.insteadOf` 重寫
- 返回最小範圍令牌的 `credential.helper`
- `GIT_SSH_COMMAND` 指向狹隘範圍的金鑰

您配置的任何機制都必須無需提示即可工作，因為執行器的內置複製和提取禁用 Git、SSH 和 Git Credential Manager 否則會顯示的提示：

- 執行器設定 `GIT_TERMINAL_PROMPT=0`，因此 Git 不會要求使用者名稱或密碼。
- 執行器使用 `BatchMode=yes` 執行 SSH，附加到您的 `GIT_SSH_COMMAND`（如果您設定了），因此 SSH 不會要求密碼短語或主機確認。
- 執行器設定 `GCM_INTERACTIVE=never`，因此 Git Credential Manager 不會打開登入對話框。
- 執行器清除 `core.askPass`，因此如果您使用 askpass 幫助程式，請改為通過 `GIT_ASKPASS` 環境變數設定它。

如果您的 Git 主機拒絕認證，或您沒有配置認證，執行器會重試幾次，然後失敗儲存庫準備當儲存庫是工作階段推送結果的儲存庫時。對於工作階段僅從中讀取的儲存庫，[Troubleshooting](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#troubleshooting) 涵蓋執行器何時改為跳過它。執行器不會將這些設定傳遞到工作階段的環境中。 如果簽出目錄由與執行器程序不同的 uid 擁有，Git 拒絕對其進行操作；添加 `safe.directory`：

```
RUN git config --system --add safe.directory '*'

```

### 使用 Anthropic Git 代理

使用 `--use-anthropic-git-proxy` 啟動執行器，或設定 `CLAUDE_RUNNER_USE_GIT_PROXY=1`，以使其通過 Anthropic 的 Git 代理複製，使用工作階段自己的短期令牌進行身份驗證。對於普通使用者工作階段，代理使用為工作階段建立者儲存的 GitHub 或 GitHub Enterprise OAuth 令牌；對於機器人和代理工作階段，它使用您的組織的 GitHub App 安裝令牌。無論哪種方式，執行器映像都不需要任何 Git 認證：沒有 SSH 金鑰、沒有認證幫助程式、沒有 `.netrc`。這是 Anthropic 託管環境使用的相同身份驗證路徑。 代理需要 `--capacity 1`，因為代理 URL 是每個工作階段的，Git 2.32 或更新版本，因為較舊的 Git 忽略代理用來隔離工作階段的配置機制。如果任一要求未滿足，執行器拒絕啟動。因為代理從 Anthropic 端提取，您的 Git 主機必須可從 Anthropic 基礎設施到達，與 Anthropic 託管工作階段相同的要求；對於僅在您的網路內可路由的 Git 主機，改用 [`checkout` 生命週期鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#checkout)。每個執行器程序一次處理一個工作階段，因此執行更多副本以實現並行性。啟用代理後，`--git-host-rewrite` 和 `--git-ssh-rewrite` 無效：代理 URL 指向 `api.anthropic.com`，而不是您的 Git 主機。 執行器也會在註冊時向 Anthropic 報告選擇加入，在啟動時列印 `Registering as opted in to Anthropic-managed git (--use-anthropic-git-proxy)`。選擇加入執行器上的每個工作階段隨後使用 Anthropic 管理的 Git 或每個工作階段的代理 URL。當工作階段使用每個工作階段的代理 URL 時，執行器記錄一行 `[runner:warn]` 說明這一點。

### 為私有網路重寫 Git URL

儲存庫 URL 從控制平面作為 HTTPS 到達，帶有您的 Git 主機的主機名；對於 GitHub Enterprise，這是您在 claude.ai 上的 Claude Code 管理設定中為 [GitHub Enterprise 整合](https://code.claude.com/docs/zh-TW/github-enterprise-server)配置的主機名。兩個可重複的旗標在複製之前重寫這些 URL：

- `--git-host-rewrite <from>=<to>`：用於分割視界 DNS，其中 Anthropic 通過外部主機名到達您的 Git 主機，但執行器必須使用內部主機名
- `--git-ssh-rewrite <host>`：用於僅接受 SSH 的 Git 主機，將 `https://<host>/owner/repo` 重寫為 `git@<host>:owner/repo`

主機重寫首先執行，因此如果您需要兩者，請在 `--git-ssh-rewrite` 中列出內部主機名。為了完全控制簽出，使用 [`checkout` 生命週期鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#checkout)。

## 構建執行器映像

Anthropic 不發佈預構建的執行器映像。在 `claude` 二進位檔案周圍構建您自己的，分層您的儲存庫需要的任何工具鏈：語言執行時、編譯器、套件管理器和 [MCP](https://code.claude.com/docs/zh-TW/mcp) 邊車。 下面的配方使用 `--capacity 4`，因此一個容器服務來自同一鎖定所有者的最多四個並發工作階段。這不提供[強化部分](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)中的每個工作階段容器隔離：在將環境連接到生產系統之前，要麼以 `--capacity 1` 執行配方，每個工作階段一個容器，要麼使用[按需執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#on-demand-runners)，它也將環境祕密保留在執行工作階段的主機之外。 此 Dockerfile 是一個最小的起點：

```
FROM debian:bookworm-slim
ARG CLAUDE_CODE_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates openssh-client \
 && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL "https://downloads.claude.ai/claude-code-releases/${CLAUDE_CODE_VERSION:?set with --build-arg CLAUDE_CODE_VERSION}/linux-x64/claude" \
      -o /usr/local/bin/claude && chmod +x /usr/local/bin/claude
RUN git config --system user.name "Claude" \
 && git config --system user.email "noreply@anthropic.com" \
 && git config --system --add safe.directory '*'
ENTRYPOINT ["claude"]

```

如果您的節點是 ARM，將 `linux-x64` 交換為 `linux-arm64`，或在 Alpine 等 musl 基礎映像上交換為 `linux-x64-musl` 或 `linux-arm64-musl`；請參閱 [Alpine Linux 設定](https://code.claude.com/docs/zh-TW/setup#alpine-linux-and-musl-based-distributions)以了解 musl 映像需要的額外套件。URL 是標準 Claude Code 發佈位置，因此您可以根據[二進位檔案完整性和程式碼簽名](https://code.claude.com/docs/zh-TW/setup#binary-integrity-and-code-signing)中描述的發佈的已簽名清單驗證下載的二進位檔案。使用 Claude Code 版本 2.1.224 或更新版本構建映像，然後將其推送到您的登錄檔並在下面的配方中引用它：

```
docker build --build-arg CLAUDE_CODE_VERSION=2.1.224 -t <your-registry>/claude-runner:latest .

```

## 為工作階段調整 CPU 和記憶體大小

為執行器執行的工作階段而不是執行器程序本身調整執行器的容器或主機大小。執行器本身輪詢工作、準備每個工作階段的簽出、執行您的[生命週期鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#lifecycle-hooks)，以及啟動和監督工作階段程序。負載來自工作階段：每個都是 Claude Code 程序加上它啟動的任何內容，例如構建、測試套件、套件安裝和 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)。 對於一個工作階段，從以下值開始，表示為 Kubernetes 請求和限制或您的平台的等效項，並將它們視為起點而不是要求：

- **記憶體** ：請求和限制各 4 GiB，滿足 Claude Code [系統要求](https://code.claude.com/docs/zh-TW/setup#system-requirements)中的 4 GB 最小值。保持兩者相等，以便調度器考慮容器的完整記憶體。當容器達到其記憶體限制時，核心會殺死其中的程序，這可能會結束工作階段中途。
- **CPU** ：2 個 CPU 的請求和 4 個 CPU 的限制，因此工作階段可以在構建期間突發超過請求。核心在其 CPU 限制處限制容器，而不是殺死其中的程序，因此限制處的工作階段執行速度較慢但保持執行。

在 Kubernetes 容器規格中，使用以下 `resources` 塊設定這些起始值：

```
resources:
  requests:
    cpu: "2"
    memory: 4Gi
  limits:
    cpu: "4"
    memory: 4Gi

```

構建和測試通常是工作階段負載中最大和最可變的部分，因此執行您的儲存庫的代表性構建，測量其峰值 CPU 和記憶體，並提高任何在該峰值之上沒有為 Claude Code 程序留下空間的起始值。 執行器使用 `--capacity` 來限制它一次執行多少個工作階段。它不在它們之間分割 CPU 或記憶體，因此執行器上的工作階段共享容器的 CPU 和記憶體。要限制一個工作階段的份額，從您的[包裝器指令碼](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#wrapper-scripts)應用限制。因此，給一個容器什麼取決於它一次服務多少個工作階段：

- **每個執行器一個工作階段** ：給每個容器一個工作階段的值。在 `--capacity 1` 使用此調整大小，[強化部分](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)推薦，以及[按需執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#on-demand-runners)，您在工作流程的 [`spawn-runner` 鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#the-spawn-runner-hook)提交的工作負載上設定值，例如 Kubernetes Job 的 pod 範本。
- **每個執行器多個工作階段** ：在 `--capacity` 高於 1 時，將一個工作階段的值乘以容量，因為最多那麼多工作階段可以在容器中同時執行。[Kubernetes](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#kubernetes) 和 [Docker Compose](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#docker-compose) 配方執行 `--capacity 4`，沒有 CPU 或記憶體限制，因此添加為您執行的容量調整大小的限制。

## Kubernetes

執行器預設在連接埠 8080 上提供 `GET /healthz`，可使用 `--health-port` 配置，因此 Kubernetes 探針無需額外設定即可工作。端點在程序活著時返回 `200`，因此下面的探針檢測死程序，而不是卡住的程序；要捕捉停止輪詢的執行器，請在 [`/metrics`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#prometheus-metrics) 的 `last_poll_age_seconds` 系列上發出警報。下面的 Deployment 從 Kubernetes Secret 掛載環境祕密，將活躍度和就緒探針指向 `/healthz`，並設定 90 秒的終止寬限期。請參閱[關閉時序](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#shutdown-timing)以了解為什麼寬限期很重要。 清單在執行器容器上設定沒有 CPU 或記憶體 `resources`。添加為您執行的容量調整大小的塊，如[為工作階段調整 CPU 和記憶體大小](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#size-cpu-and-memory-for-sessions)所述。

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claude-runner
  namespace: claude-runners
spec:
  replicas: 3
  selector:
    matchLabels:
      app: claude-runner
  template:
    metadata:
      labels:
        app: claude-runner
        app.kubernetes.io/part-of: claude-code-self-hosted-runner
    spec:
      terminationGracePeriodSeconds: 90
      containers:
        - name: runner
          image: <your-registry>/claude-runner:latest
          args:
            - self-hosted-runner
            - --environment-secret-file
            - /etc/claude/environment-secret
            - --capacity
            - "4"
          volumeMounts:
            - name: environment-secret
              mountPath: /etc/claude
              readOnly: true
          ports:
            - name: health
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 30
      volumes:
        - name: environment-secret
          secret:
            secretName: claude-runner-environment-secret

```

上面的 Deployment 位於 `claude-runners` 命名空間中。首先建立命名空間：

```
kubectl create namespace claude-runners

```

從保存您在管理 UI 的[**複製環境金鑰** 步驟](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart#set-up-an-environment-and-runner)中複製的值的本地檔案建立支持 Secret，以便祕密永遠不會出現在您的 shell 歷史記錄中。執行 `(umask 077 && cat > ./environment-secret)`，貼上祕密，按 Enter，然後按 Ctrl-D。然後建立 Secret 並刪除檔案：

```
kubectl create secret generic claude-runner-environment-secret -n claude-runners --from-file=environment-secret=./environment-secret

```

## Docker Compose

下面的 Compose 服務在執行器退出時重新啟動它，涵蓋崩潰和清空後的正常退出。Docker 重新啟動原則重新啟動同一容器及其可寫層，因此執行器以重複使用的檔案系統而不是[強化姿態](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)推薦的新鮮檔案系統回來；為評估使用此配方，對於生產環境，要麼每次執行時重新建立容器，要麼使用執行此操作的協調器。

```
services:
  claude-runner:
    image: <your-registry>/claude-runner:latest
    command:
      - self-hosted-runner
      - --environment-secret-file
      - /run/secrets/environment-secret
      - --capacity
      - "4"
    secrets:
      - environment-secret
    restart: always
    stop_grace_period: 90s

secrets:
  environment-secret:
    file: ./environment-secret

```

## 關閉時序

在 `SIGTERM` 上，執行器停止接受新工作，除非您設定 [`--defer-shutdown-max-min`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#defer-the-drain-past-the-first-signal)，否則等待最多 `--drain-wait-sec`（預設為零）以完成進行中的轉向，終止每個工作階段的程序樹，並執行 [`post-session` 生命週期鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#post-session)。該程序樹包括 Claude 仍在工作階段中執行的命令。 完整清空路徑需要最多 `--session-stop-grace-sec` + `--drain-wait-sec` + `--post-session-hook-timeout-sec`，加上 15 秒的固定程序清理開銷，加上設定 [`--push-outcome-on-release`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 時的 30 秒。在預設值下為 80 秒，執行器在啟動時記錄總計。工作階段在此一個預算下並行清空，因此總計不會隨 `--capacity` 增長。 在預設 `--drain-wait-sec 0` 下，滾動重新啟動中斷進行中的轉向；每個工作階段在另一個執行器上恢復，丟失未推送的工作，如[已知問題](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#additional-limitations)下所述。設定 `--drain-wait-sec`，並提高寬限期以匹配，以讓轉向首先完成。 在整個路徑中，執行器以零容量持續向控制平面進行心跳，因此工作階段租約不會過期並在 `post-session` 鉤子仍在寫出未提交的工作時重新排隊到另一個執行器。心跳在執行器取消註冊之前停止。 在主機停止執行器之前，至少給執行器它在啟動時記錄的總計。您在哪裡設定這取決於您的主機如何停止：

- **使用`SIGTERM` 寬限期**：在 Kubernetes 上設定 `terminationGracePeriodSeconds`，在 Docker Compose 上設定 `stop_grace_period`，或您的協調器的等效項至少為該總計。Kubernetes 預設 30 秒短於執行器的清空路徑，因此 Kubernetes 在執行器完成清空之前停止 pod。
- **使用[`--retire-at`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)** ：在退休時間和主機停止時間之間調整邊距以涵蓋典型轉向、加上[執行器生命週期](https://code.claude.com/docs/zh-TW/self-hosted-environments#runner-lifecycle)描述的背景任務保持、加上該相同總計。在每次啟動時計算退休時間，例如 `date +%s` 加上執行器的預期生命週期。
- **使用[`--defer-shutdown-max-min`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#defer-the-drain-past-the-first-signal)** ：向清空路徑總計添加兩個更多部分。第一個是您配置的分鐘數。第二個是[延遲清空超過第一個信號](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#defer-the-drain-past-the-first-signal)描述的發佈後寬限期，預設值為 75 秒。設定旗標後，執行器也在啟動時列印組合圖形，在清空路徑總計之後。

### 延遲清空超過第一個信號

如果您想要重新啟動的執行器繼續服務它持有的工作階段最多 `n` 分鐘，而不是在第一個信號上清空它們，請設定 [`--defer-shutdown-max-min <n>`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)。在第一個 `SIGTERM` 或 `SIGINT` 上，執行器停止接受新工作並繼續服務它持有的工作階段。它保持輪詢，以便控制平面不會重新排隊這些工作階段。需要 Claude Code v2.1.238 或更新版本。

#### 第一個信號後執行器持有的工作階段會發生什麼

在信號後的前兩個階段中，執行器釋放工作階段，釋放的工作階段在其使用者發送下一條訊息時在新執行器上恢復。從第一個信號開始計數，執行器通過三個階段移動：

- **在前`n` 分鐘內**：執行器正常服務其工作階段並繼續強制執行 `--startup-timeout-min` 和 `--kill-session-after-min`。如果您也設定 [`--release-idle-session-min`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)，執行器釋放任何使用者已閒置該長時間的工作階段；沒有它，閒置工作階段保留在執行器上。
- **當`n` 分鐘用完時**：執行器釋放它仍然持有的每個工作階段，閒置或不閒置。執行器等待中途轉向的轉向結束，並為該轉向的背景任務再等待最多 60 秒，然後釋放該工作階段。
- **當發佈後寬限期用完時** ：執行器清空它仍然持有的任何工作階段，控制平面立即將每個清空的工作階段重新排隊到另一個執行器。發佈後寬限期在 `n` 分鐘用完時開始，預設值為 75 秒。如果您將 `--drain-wait-sec` 設定為 60 秒以上，發佈後寬限期改為 `--drain-wait-sec` 加 15 秒。

在任何階段，執行器在不持有任何工作階段時立即以 0 退出。第二個信號縮短階段：執行器立即清空，就像在沒有 `--defer-shutdown-max-min` 的第一個信號上一樣。一旦清空進行中，下一個信號強制退出執行器。這無論第二個信號還是發佈後寬限期用完啟動清空。

#### 調整停止超時大小

給您的主機停止超時至少三個部分的總和：您配置的 `n` 分鐘、發佈後寬限期和[關閉時序](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#shutdown-timing)描述的完整清空路徑。使用預設設定發佈後寬限期為 75 秒，清空路徑為 80 秒，因此允許 `n` 分鐘加 155 秒。執行器在設定 `--defer-shutdown-max-min` 時在啟動時列印此總和。 如果停止超時在執行器完成之前用完，主機會殺死執行器。它仍然持有的工作階段不會獲得 `post-session` 鉤子。執行器不取消註冊，控制平面約一分鐘後重新排隊工作階段。如果您無法給停止超時該總和，請保留 `--defer-shutdown-max-min` 未設定，以便執行器改為在第一個信號上清空。

### 什麼到達執行中的 post-session 鉤子

`post-session` 鉤子和 Claude 工作階段子項各自在自己的 POSIX 程序組中執行，與執行器的分開，因此停止機制以不同方式到達它們：

- **執行器已在清空時的`SIGTERM`** ：立即強制退出執行器，跳過清空路徑的任何剩餘部分。沒有 [`--defer-shutdown-max-min`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#defer-the-drain-past-the-first-signal)，這是執行器接收的第二個 `SIGTERM`。沒有信號到達中途執行的 `post-session` 鉤子，因此在採用孤兒的裸主機上，它自己完成，但不受監督：其超時預算不再適用，寫入關閉的日誌管道可以用 `SIGPIPE` 殺死它，因此需要在那裡存活強制退出的鉤子應將其自己的輸出重定向到檔案。在此頁面上的容器配方中，執行器是容器的 PID 1，其退出結束容器，在 systemd 的預設 `KillMode=control-group` 下，cgroup 範圍的殺死到達鉤子，如**Cgroup 範圍的殺死** 項所述；在兩者中，將強制退出視為對鉤子致命並改為依賴寬限期。
- **程序組範圍的信號** ，例如包裝器指令碼中的 `kill -- -<pid>`、shell 工作控制或組範圍的看門狗：到達執行器和中途 `checkout` 鉤子子程序，該子程序故意保持組附加，但不是中途執行的 `post-session` 鉤子或工作階段子項。
- **Cgroup 範圍的殺死** ，例如 systemd 的預設 `KillMode=control-group` 或 `terminationGracePeriodSeconds` 過期時 Kubernetes 傳遞到整個容器的 `SIGKILL`：到達所有內容，包括鉤子。程序組隔離不保護這些，這就是為什麼寬限期必須涵蓋完整清空路徑。
- **鉤子自己的超時** ：當鉤子超過 `--post-session-hook-timeout-sec` 時，執行器向鉤子的整個程序組發送 `SIGTERM`，然後 2 秒後發送 `SIGKILL`，因此鉤子分叉的工作者（例如 tar、rsync 或 git）與包裝器 shell 一起終止，而不是作為孤兒存活。執行器的監督在鉤子的 stdio 關閉後結束：重定向其自己的輸出到檔案並超過 `SIGTERM` 階段的工作者超出執行器的範圍。

當清空開始時，以及在強制退出時，執行器記錄仍在執行多少 `post-session` 鉤子，因此您可以區分安靜清空和中途快照的清空。

## 在執行器之間保持基本目錄和容量相同

如果執行器在工作階段中途死亡，伺服器重新排隊工作階段，環境中的另一個執行器拾取它。該執行器從其自己的 `--base-dir` 和 `--capacity` 派生簽出路徑：`--capacity 1` 直接在 `--base-dir` 下簽出，`--capacity` 高於 1 改用每個工作階段的工作樹。當同一環境中的執行器對任一旗標使用不同的值時，恢復的工作階段的工作目錄會更改，代理之前記錄的絕對路徑（在編輯、工具呼叫或其自己的筆記中）指向不再存在的位置。 在環境中的每個執行器上使用相同的 `--base-dir` 和 `--capacity`，並且不要使用每個主機的值，例如執行個體 ID 或主機名。 基本目錄預設為 `/workspace`，除了 [`--base-dir` 參考行](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)記錄的例外。執行器需要對其的寫入存取。在啟動時，在註冊之前，執行器建立目錄並確認它可以寫入它，當它無法時以 `cannot create or write to base directory` 退出。以 root 身份啟動的執行器自己建立預設 `/workspace`。對於非 root 執行器，在啟動執行器之前建立目錄並給執行器的使用者所有權，或將 `--base-dir` 指向該使用者已擁有的目錄。

## 重複使用預熱簽出

對於大型儲存庫，複製可能主導工作階段啟動。在 `--capacity 1` 且沒有 [`checkout` 鉤子](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#checkout) 的情況下，執行器在 `<base-dir>/<repo-owner>/<repo>` 保持每個儲存庫的一個規範複製並在工作階段之間重複使用它：它提取請求的 ref、分離 `HEAD` 並硬重置為它，當變化不多時幾乎是瞬間的。要跳過冷複製，以兩種方式之一提供複製：

- **在映像中複製** ：在該路徑將複製構建到您的執行器映像中。每個新容器然後以預熱複製啟動，而不重複使用磁碟。
- **在持久卷上複製** ：在您使用 [`--lock-to-account`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 預鎖定到一個使用者帳戶的執行器上，將 `--base-dir` 指向持久卷，因此磁碟只服務該帳戶。預鎖定的執行器永遠不會拾取 Claude Tag 頻道工作階段，因此此選項不適用於服務它們的執行器。

重複使用路徑做什麼和不保證什麼：

- **任何複製形狀都有效** ：路徑上的完整、淺或單分支複製按原樣使用。執行器在提取到現有複製時永遠不會傳遞 `--depth`，因此完整預熱保持其完整歷史記錄，淺複製保持淺。`CLAUDE_RUNNER_FETCH_DEPTH`（`full`、`0` 或數字；預設 50）僅控制執行器在不存在複製時進行的冷複製。
- **追蹤的變化重置，未追蹤的檔案持續** ：每個工作階段從硬重置開始，該重置擦除前一個工作階段的追蹤修改，但執行器永遠不執行 `git clean`，因此鎖定所有者的早期工作階段的未追蹤檔案保留在樹中。
- **每工作階段目錄也持續** ：在簽出旁邊，執行器在 `<base-dir>/_sessions/` 下為它執行的每個工作階段建立每工作階段項目。工作階段的 Claude 設定目錄保存對話記錄的本地副本。在它旁邊是工作階段的上傳檔案，當工作階段有任何時。工作階段目錄也坐在那裡：它在工作階段執行時保存任何每工作階段 worktrees 和 `checkout` 鉤子簽出，並保持 Claude 在其中寫入的任何其他內容。 預設情況下，執行器在工作階段結束時將這些留在原地，因此在超越執行器程序的磁碟上它們會累積。每個工作階段都以執行器自己的使用者身份執行，因此該磁碟服務的任何後續工作階段都可以讀取它們。如果您保持持久 `--base-dir`，請為該增長調整卷的大小。相同的適用於任何在相同檔案系統上重新啟動執行器的設定，包括 [Docker Compose 配方](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#docker-compose)。
- **使用`--remove-session-state` ，每工作階段目錄不持續**：使用 [`--remove-session-state`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 啟動執行器，以便在工作階段結束時刪除每個工作階段的每工作階段目錄。刪除是盡力而為：當執行器在其清理執行之前被殺死時，目錄保留。規範複製和工作階段在主機上其他地方寫入的檔案，例如臨時目錄，無論如何都保留。
- **使用 Git 代理，重置變成簽出** ：使用 [`--use-anthropic-git-proxy`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#use-the-anthropic-git-proxy)，執行器在每個工作階段之前清理複製的 `.git/`，保持物件存儲、refs 和淺狀態，但刪除索引，因此每個工作階段支付完整工作樹簽出而不是幾乎瞬間的重置；它仍然永遠不重新複製。子模組預熱在代理下不受支援。
- **長複製不需要解決方法** ：執行器使用 120 秒無進度看門狗和 30 分鐘硬上限限制每個 Git 操作，而不是平面超時，因此保持報告進度的慢冷複製完成。

## 固定版本

每個工作階段的子 Claude Code 程序執行執行器自己的二進位檔案，執行器在它生成的工作階段內關閉自動更新，因此每個工作階段執行您在主機上安裝或構建到映像中的版本。主機級更新在執行器下次啟動時生效。

- **將群保持在一個版本上** ：使用固定版本構建映像，或在裸主機上安裝特定版本並[禁用自動更新](https://code.claude.com/docs/zh-TW/setup#disable-auto-updates)
- **升級** ：安裝較新版本或重建映像，然後重新啟動執行器
- **外掛程式** ：外掛程式市場也不自動更新；在執行器的環境中設定 `FORCE_AUTOUPDATE_PLUGINS=1` 以讓外掛程式自動更新，同時二進位檔案保持固定

## 擴展群

您的協調器決定何時添加或移除執行器。由於[每個執行器一個所有者鎖](https://code.claude.com/docs/zh-TW/self-hosted-environments#runner-lifecycle)，最小副本計數是您期望同時活躍的使用者和 Claude Tag 代理的數量；`--capacity` 控制一個所有者的工作階段內的並行性，而不是跨所有者。 有兩種擴展方法可用：

- **固定群** ：執行靜態執行器副本集並在每個執行器服務的 [Prometheus 指標](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#prometheus-metrics)上擴展
- **按需執行器** ：執行 `claude self-hosted-runner orchestrator` 子命令，它輪詢 Anthropic 以查找沒有可用執行器排隊的工作階段，並調用您的 `spawn-runner` 鉤子為每個工作階段啟動一個。請參閱[按需執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#on-demand-runners)。

## 已知問題和限制

以下是此版本中的限制，其中存在解決方法。

### 連接器流量離開您的網路

Anthropic 從其自己的基礎設施而不是從您的執行器呼叫連接器工具。連接器工具是 claude.ai 連接器，例如 GitHub、Slack 和 Linear。當 Claude 在自託管工作階段中使用連接器時，該流量通過 `api.anthropic.com` 而不是源自您的網路邊界內。 要將連接器保留在自託管工作階段之外，使用 [`allowedMcpServers` 和 `deniedMcpServers` 原則設定](https://code.claude.com/docs/zh-TW/managed-mcp#policy-based-control-with-allowlists-and-denylists)進行篩選。Claude Code 將這些設定應用於 Anthropic 傳遞的連接器以及您從執行器主機播種的伺服器和使用者添加的伺服器，因此如果您為其他伺服器部署允許列表，Claude Code 也會阻止傳遞的連接器。要在 URL 型允許列表旁邊保持連接器可用，添加與傳遞連接器的 Anthropic 代理路徑相符的項目：

- `https://api.anthropic.com/v2/ccr-sessions/*`
- `https://api.anthropic.com/v1/code/sessions/*`
- `https://api.anthropic.com/v1/code/mcp/*`

如果工具流量必須保留在您的網路內，改為在執行器映像上執行等效工具作為本地 MCP 伺服器。請參閱 [MCP 伺服器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#mcp-servers)。

### 某些工作階段不計為閒置

持有永遠不完成的背景任務的工作階段不計為閒置，因此 `--release-idle-session-min` 不會釋放該工作階段的插槽。等待從執行中工具呼叫內部請求的批准的工作階段也不計為閒置。始終將 `--kill-session-after-min` 與其一起設定作為硬後擋，以便沒有工作階段可以無限期地持有插槽。 `--kill-session-after-min` 是失控工作階段的後擋。在 v2.1.260 或更新版本上的執行器上，達到限制的工作階段不會立即終止。執行器給它一個寬限窗口，預設 15 分鐘，您可以使用 [`SELF_HOSTED_RUNNER_MAX_LIFETIME_GRACE_MS`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#environment-variable-only-settings) 更改：

- 如果工作階段等待其使用者，執行器會釋放它。如果其轉向已結束並且它僅持有背景任務，執行器會等待最多 60 秒讓這些任務完成，然後釋放它。當其使用者發送下一條訊息時，工作階段會恢復。
- 如果轉向仍在執行，執行器等待轉向完成，或工作階段下一次等待其使用者，然後釋放它。
- 如果工作階段在寬限窗口結束時仍在執行器上，執行器終止它，任何執行中轉向的工作都會丟失。等待從執行中工具呼叫內部請求的批准的轉向是工作階段超過窗口的一種方式。

釋放的工作階段從新複製恢復，因此它未推送的工作無論如何都消失了；請參閱[恢復的工作階段丟失未推送的工作](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#additional-limitations)。在 v2.1.260 之前，執行器在限制處終止每個工作階段，最多等待寬限窗口以完成執行中的轉向。 將該旗標設定為高於您預期的最長工作階段時間，例如 `--kill-session-after-min 480` 為 8 小時。要從進入閒置的對話中釋放插槽，改用 `--release-idle-session-min`。

### 其他限制

- **恢復的工作階段丟失未推送的工作** ：當工作階段被釋放或其執行器重新啟動，使用者發送另一條訊息時，工作階段在新執行器上恢復，該執行器從其啟動分支再次複製儲存庫，因此工作階段未推送的工作消失。設定 [`--push-outcome-on-release`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 以使執行器在釋放之前進行最佳努力推送工作階段的結果分支，以便恢復的工作階段從這些提交開始；這保留已提交的工作，而不是髒工作樹。在啟用它之前，限制誰可以推送到源遠端上的 `claude/*` refs，例如使用分支規則集：在恢復時，執行器提取先前推送的分支而不驗證誰推送了它，因此任何有權推送到這些 refs 的人都可以將內容放入恢復的工作區。執行器也在恢復時丟棄每個工作階段的配置，意味著工作階段的 Claude 配置目錄和工作階段寫入的任何 shell 狀態；`--push-outcome-on-release` 不涵蓋這些。
- **私有儲存庫無法在工作階段中途添加** ：在自託管執行器上，在工作階段啟動後添加到工作階段的儲存庫不會使用認證複製，因此添加失敗。在建立工作階段時選擇工作階段需要的每個儲存庫。
- **某些連接器不出現在自託管工作階段中** ：您在 claude.ai Settings 中尚未連接的連接器不在自託管工作階段中列出，工作階段不會提示您連接它。首先在 Settings 中連接它，然後啟動新工作階段。將連接器添加到已執行的工作階段也不會使其工具可用於 Claude；啟動新工作階段以拾取新添加的連接器。

### 報告問題

對於自託管環境的問題，請聯繫您的 Anthropic 帳戶團隊。

## 故障排除

為了進行引導式診斷，在執行器主機上執行 doctor 子命令。doctor 子命令啟動互動式 Claude Code 工作階段，附加執行器的日誌和狀態。首先在該主機上使用 `claude auth login` 登入，以便工作階段可以查詢您的環境、其執行器和其排隊的工作階段。沒有該登入，例如當主機使用 API 金鑰進行身份驗證時，它限制為本地健康端點、指標和執行器的日誌，並且僅在您使用 `--log-file` 啟動執行器時讀取日誌。

```
claude self-hosted-runner doctor

```

常見問題：

- **執行器不出現在環境中** ：確認主機可以通過 HTTPS 到達 `api.anthropic.com`，環境祕密是最新的，主機時鐘在真實時間的五分鐘內；更大的偏差導致身份驗證失敗。執行器在身份驗證失敗時記錄 `[runner:fatal]` 及拒絕原因。
- **執行器在啟動時以`cannot create or write to base directory` 退出**：執行器無法建立或寫入 `--base-dir`，預設為 `/workspace`。修復目錄的所有權或將 `--base-dir` 指向可寫路徑，如[在執行器之間保持基本目錄和容量相同](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#keep-the-base-directory-and-capacity-identical-across-runners)中所述。如果執行器改為記錄 `[runner:fatal]` 說基本目錄檢查超時，目錄在掛起的 NFS 或 CSI 掛載上。檢查掛載健康而不是權限。執行器在打開 `--log-file` 之前將這兩個啟動失敗列印到 stderr，因此在終端或您的平台的容器日誌中尋找它們，而不是日誌檔案。在 v2.1.225 之前，執行器在啟動時沒有檢查基本目錄，此配置錯誤在拾取後失敗工作階段。
- **工作階段保持排隊** ：每個線上執行器可能被鎖定到不同的所有者。檢查每個執行器的 `claude_code_self_hosted_runner_locked_account` [指標](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#prometheus-metrics)或其 `[runner:health]` 日誌行的 `locked_account` 欄位以查看誰持有它。兩者僅在執行器被發佈攜帶 `act.email` 聲明的工作階段令牌後顯示所有者的電子郵件，Claude Tag 代理的工作階段永遠不會這樣做。沒有聲明，執行器不發出 `locked_account` 系列並記錄 `locked_account=yes`，這告訴您執行器被鎖定但不知道到哪個所有者。添加副本，或等待現有執行器清空並重新啟動。如果環境使用按需執行器，改為檢查協調器；請參閱[按需執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#on-demand-runners)。
- **工作階段在拾取後立即失敗** ：在 claude.ai/code 中打開工作階段以查看錯誤。最常見的原因是執行器映像中缺少 [Git 認證](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git)和未安裝的構建工具。不可寫的基本目錄在啟動時停止執行器，而不是失敗工作階段。請參閱此清單中的**執行器在啟動時以`cannot create or write to base directory` 退出**項。
- **工作階段無法通過身份驗證出站代理到達網路** ：當您使用 [`--proxy-authorization-command` 或 `--proxy-authorization-file`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#authenticate-to-an-egress-proxy) 設定的來源失敗、在 30 秒後超時或產生空值時，執行器以 `502 Bad Gateway` 回答該連接並記錄原因。執行器在該日誌中編輯命令的 stderr，永遠不記錄標頭值。使用 `--proxy-authorization-command`，自己在主機上執行命令以確認它在 stdout 上列印整個標頭值。如果執行器改為在啟動時以 `could not start the proxy-authorization listener` 退出，它無法打開其環回偵聽器。
- **執行器記錄`Poll failed` 行包含 `rejecting the malformed poll response`**：執行器接收到工作輪詢回應，其主體不是隊列的預期 JSON，最常見的原因是執行器和 `api.anthropic.com` 之間的某些內容（例如攔截代理或強制入口網站）以自己的頁面回答。執行器拒絕回應，在 `claude_code_self_hosted_runner_poll_errors_total` [指標](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#prometheus-metrics)的 `transport` 種類下計數，並在[工作階段生命週期](https://code.claude.com/docs/zh-TW/self-hosted-environments#session-lifecycle)中描述的失敗輪詢時間表上重試。執行器保持服務其活躍工作階段。配置代理以從 `api.anthropic.com` 無更改地傳遞回應。在 v2.1.246 之前，執行器將此類回應讀取為空工作隊列，這可能結束其活躍工作階段或使其退出。
- **工作階段的分支不再存在於遠端** ：對於工作階段僅從中讀取的 Git 來源，執行器跳過該來源並在其餘來源上繼續。對於工作階段推送結果的來源，已刪除的分支（通常因為它被合併並自動刪除）使工作階段失敗，並出現命名儲存庫和分支的錯誤，要求您恢復分支並重試。當跳過會使其沒有儲存庫時，執行器使用相同的錯誤使工作階段失敗。在 v2.1.228 之前，此類工作階段在空目錄中啟動。
- **工作階段啟動時沒有其中一個儲存庫** ：在沒有 [`checkout` hook](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#checkout) 的執行器上，Git 主機可以拒絕執行器對工作階段僅從中讀取的儲存庫的存取檢查。執行器隨後跳過該儲存庫，記錄命名拒絕的 `[runner:warn] could not access context source` 行，並在其餘儲存庫上啟動工作階段。 執行器僅跳過明確的拒絕：主機回答儲存庫未找到，Git 找不到主機的認證，或身份驗證失敗。網路故障、超時或 HTTP `403` 仍然會失敗工作階段啟動，對於工作階段推送結果的儲存庫的拒絕也是如此。執行器仍然會失敗跳過會使其沒有儲存庫的工作階段。使用 [`--use-anthropic-git-proxy`](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#use-the-anthropic-git-proxy)，執行器僅跳過 Git 代理本身拒絕的儲存庫。 存取檢查在每次工作階段在執行器上啟動時再次執行，因此一旦執行器的 Git 身份具有讀取存取權限，下一次啟動會複製儲存庫。在 v2.1.274 之前，這些拒絕中的每一個都失敗了工作階段啟動。
- **工作階段需要幾分鐘才能啟動** ：初始複製通常主導。觀看 `claude_code_self_hosted_runner_session_init_duration_seconds` [指標](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#prometheus-metrics)以確認，並使用[預熱簽出](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#reuse-a-pre-warmed-checkout)或較小的 `CLAUDE_RUNNER_FETCH_DEPTH` 切割複製。
- **輪次以 401 失敗** ：每個工作階段使用執行器從 Anthropic 獲取並通過工作階段的 stdin 輪換的短期 [`CLAUDE_CODE_OAUTH_TOKEN`](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#wrapper-scripts) 來驗證模型呼叫。當輪次以來自模型 API 的 401 或 403 結束時，執行器獲取新令牌並將其傳遞給工作階段。失敗的輪次不會重試。 當獲取失敗時，執行器記錄 `inference_token refresh failed` 行，說明何時會重試，並且只要工作階段運行就會繼續重試。 如果每個呼叫在工作階段約 30 分鐘後開始失敗，包裝指令碼可能已切斷工作階段的 stdin，因此令牌輪換無法到達它；請參閱[保持 stdin 和檔案描述符 3 附加](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#keep-stdin-and-file-descriptor-3-attached)。 在 v2.1.274 之前，執行器在幾次嘗試後停止重試失敗的獲取，並等待下一個排定的獲取。失敗的輪次沒有觸發獲取，因此每個輪次都以 401 失敗，直到下一個排定的獲取。
- **Pod 在清空中途被殺死** ：將 `terminationGracePeriodSeconds` 提高到至少執行器在啟動時記錄的值。請參閱[關閉時序](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#shutdown-timing)。

日誌初始化後，執行器將其生命週期日誌（包括 `[runner:fatal]` 行）寫入 stdout，將調試輸出寫入 stderr，全部作為純文字行而不是 JSON。上面故障排除項中描述的啟動失敗在該點之前列印到 stderr。使用 `--log-file` 捕捉兩個流，這也讓 `self-hosted-runner doctor` 尾隨它們，或使用您的平台的日誌收集。 每個工作階段的子程序寫入單獨的調試日誌。失敗時執行器在 claude.ai/code 中的工作階段旁邊顯示日誌的尾部。除非您使用 [`--remove-session-state`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 啟動執行器，否則它也會在磁碟上保留失敗工作階段的日誌，並在執行器日誌中列印其路徑。

## 下一步

- [自訂工作階段](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration)：包裝器指令碼、生命週期鉤子、按需執行器、MCP 伺服器和權限
- [端到端測試](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing)：在推廣新執行器映像之前從 CI 驗證它
- [參考](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference)：每個 CLI 旗標、環境變數和指標

是否 助手
