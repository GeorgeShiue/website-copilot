自託管環境在 Team 和 Enterprise 方案上處於公開測試版；[擁有者](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)可以在[**雲端環境** 管理頁面](https://claude.ai/admin-settings/cloud-environments)上開啟**允許自託管環境** 來啟用它們。本頁面假設您已有一個可運作的執行器；請參閱[快速入門](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart)以了解設定，以及[部署到生產環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy)以了解艦隊配方。 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)在您自己的基礎設施上執行 Claude Code [雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，由您部署的執行器程序執行。在沒有設定的情況下，該執行器會複製會話的儲存庫、生成 Claude Code，然後進行清理。本頁面適用於操作執行器的平台工程師：它涵蓋了當預設值不適用時的擴展點，從每個會話的認證佈建到完全替換簽出。包裝指令碼和掛鉤在執行器主機上作為可執行檔案執行，該主機是 Linux 或 macOS，本頁面上的範例假設使用 POSIX shell。 本頁面上的一些掛鉤環境變數仍然使用 `pool`，例如 `CLAUDE_RUNNER_POOL_ID`；CLI 旗標和環境變數名稱使用 `environment`，例如 `--environment-secret-file`。

## 包裝指令碼

當每個會話需要執行器無法自行完成的設定時，請使用包裝指令碼：佈建限定於會話建立者的短期認證、匯出環境特定的祕密、準備語言工具鏈，或在子程序周圍應用資源限制。執行器每個會話啟動一次您的包裝指令碼，而不是 Claude Code 二進位檔案。透過 `exec` 進入 `$CLAUDE_RUNNER_CLAUDE_BIN`（執行器自己的二進位檔案）來結束包裝指令碼，以便訊號和結束代碼正確傳播。 在啟動執行器時，將 `--exec-path` 或 `SELF_HOSTED_RUNNER_EXEC_PATH` 指向包裝指令碼：

```
claude self-hosted-runner --environment-secret-file /etc/claude/environment-secret --exec-path /etc/claude/session-wrapper.sh

```

執行器在包裝指令碼的環境中設定以下內容：

| 變數                                                                                                                                                        | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE_CODE_SESSION_ACCESS_TOKEN`                                                                                                                          | 會話 JWT，前綴為 `sk-ant-cc-`。其 `act` 聲明識別會話建立者，包含建立者的電子郵件和上游身份提供者主體（如果建立表面記錄了它們）。該值是生成時的權杖；重新整理會透過子程序的 stdin 到達，因此包裝指令碼只會看到初始值。請參閱[驗證會話身份](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)。                                                                                                                                                                                                                                                                |
| `CCR_SESSION_ACCOUNT_EMAIL`                                                                                                                                 | 會話建立者的電子郵件，由執行器從權杖的 `act.email` 聲明中預先提取，無需簽名驗證。適合用於標籤，例如提交預告片。當電子郵件限制認證發行時，驗證權杖並從中讀取聲明；請參閱[佈建限定於會話建立者的認證](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#provision-credentials-scoped-to-the-session-creator)。當權杖不包含建立者電子郵件時未設定。視為個人可識別資訊。                                                                                                                                                                                     |
| `CLAUDE_RUNNER_CLIENT_PLATFORM`                                                                                                                             | 建立會話的用戶端表面，例如 `web_claude_ai`、`desktop_app`、`ios`、`claude_code_cli` 或 `scheduled_trigger`。Anthropic 在會話建立時記錄該值一次，因此包裝指令碼和每個生命週期掛鉤都會看到相同的值。僅將其用於採用分析和標籤，不用作授權訊號。當會話沒有記錄或識別的表面時未設定，因此在 `set -u` 下將其參考為 `${CLAUDE_RUNNER_CLIENT_PLATFORM:-}`。需要 Claude Code v2.1.229 或更新版本。                                                                                                                                                                                        |
| `CLAUDE_RUNNER_CLAUDE_BIN`                                                                                                                                  | 執行器自己的 Claude Code 二進位檔案的絕對路徑。以 `exec "$CLAUDE_RUNNER_CLAUDE_BIN" "$@"` 結束您的包裝指令碼，以移交給固定的二進位檔案，而無需硬編碼安裝路徑。                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `CLAUDE_CODE_REMOTE_SESSION_ID`                                                                                                                             | 標記形式為 `cse_...` 的會話 ID。這是[生命週期掛鉤](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#lifecycle-hooks)以 `CLAUDE_RUNNER_SESSION_ID`（`session_...` 形式）看到的相同會話；UUID 變數在兩者之間匹配，將 `cse_` 前綴替換為 `session_` 會產生會話 URL 中顯示的 ID。                                                                                                                                                                                                                                                                            |
| `CLAUDE_CODE_REMOTE_SESSION_UUID`                                                                                                                           | 規範 UUID 形式的相同會話 ID，適用於以 UUID 為鍵的系統。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `CLAUDE_SESSION_INGRESS_TOKEN_FILE`                                                                                                                         | 保存目前會話 JWT 的每個會話檔案的絕對路徑，在權杖重新整理時保持最新。Shell 子程序在下載使用者新增到會話的附件時從中讀取其 `Authorization` 標頭。`exec` 會自動保留該變數；重建子程序環境的包裝指令碼必須帶上該變數，否則附件下載會無聲地停止工作。                                                                                                                                                                                                                                                                                                                                |
| `CLAUDE_CONFIG_DIR`                                                                                                                                         | 每個會話的 Claude 設定目錄，在會話開始時從執行器在啟動時擷取的執行器主機設定快照中寫入；請參閱[權限和工具核准](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#permissions-and-tool-approval)。此處的寫入隔離到此會話。會話結束後，該目錄保留在 `<base-dir>/_sessions/` 下，除非您使用 [`--remove-session-state`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 啟動執行器；請參閱[重複使用預先準備的簽出](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#reuse-a-pre-warmed-checkout)。 |
| `ANTHROPIC_BASE_URL`                                                                                                                                        | 子程序將使用的 API 基礎 URL，由控制平面按會話傳遞，通常為 `https://api.anthropic.com`。不要覆蓋它：會話的推理認證是 Anthropic 發行的 OAuth 權杖，其他提供者不接受，因此自託管環境中的推理無法路由到其他地方。                                                                                                                                                                                                                                                                                                                                                                    |
| `CLAUDE_CODE_OAUTH_TOKEN`                                                                                                                                   | 子程序用於模型推理的短期 OAuth 存取權杖，限定於模型推理和檔案上傳，生命週期約為 30 分鐘。執行器在過期前重新鑄造它，並透過子程序的 stdin 傳遞輪換，因此不[保持 stdin 連接](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#keep-stdin-and-file-descriptor-3-attached)的包裝指令碼只會看到初始值。不要依賴您的組織 IP 允許清單來限制此權杖的使用：將其視為持有人認證，如果洩露，大約 30 分鐘內仍可使用，不要記錄它、將其寫入磁碟或在會話容器外轉發它。                                                                                                   |
| 包裝指令碼也會繼承子程序的其餘受管環境，包括任何伺服器提供的環境變數。`exec` 會自動傳播所有內容；如果您的包裝指令碼以另一種方式生成子程序，請轉發完整環境。 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

### 保持 stdin 和檔案描述符 3 連接

子程序的 stdin 是執行器的控制通道。權杖輪換和會話結束訊號會在其上到達。執行器也會在檔案描述符 3 上開啟一個管道，並從中讀取子程序的活動訊號以驅動閒置和啟動逾時。純 `exec "$CLAUDE_RUNNER_CLAUDE_BIN" "$@"` 會自動保留兩者。 如果您的包裝指令碼使用裸 `&` 在背景中執行子程序，它會切斷子程序的 stdin：會話看起來健康，直到初始 OAuth 權杖的大約 30 分鐘生命週期過期，然後每個 API 呼叫都會失敗，並出現 `401 authentication_error`。如果您的包裝指令碼必須在背景中執行子程序，例如保持拆卸陷阱活著，請在檔案描述符 4 或更高版本上儲存 stdin，並明確重新連接它：

```
exec 4<&0
"$CLAUDE_RUNNER_CLAUDE_BIN" "$@" <&4 4<&- &
CHILD=$!
trap 'teardown' EXIT
wait "$CHILD"

```

不要在包裝指令碼中關閉或重複使用檔案描述符 3。重定向子程序的 stdout 和 stderr 是可以的。

### 佈建限定於會話建立者的認證

使用 `decode-token` 子命令從會話 JWT 讀取聲明。它從引數、`CLAUDE_CODE_SESSION_ACCESS_TOKEN` 或 stdin 讀取權杖，按該順序；請參閱[驗證會話內的權杖](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity#verify-the-token-inside-the-session)以了解它檢查的內容。下面的範例解碼建立者身份，將其交換為短期 AWS 認證，並執行進入 Claude Code：

```
#!/bin/bash
# Key on the stable Anthropic user ID and require a human creator.
CREATOR_SUB=$("$CLAUDE_RUNNER_CLAUDE_BIN" self-hosted-runner decode-token \
  | jq -re '.act.sub // "" | select(startswith("user:"))') \
  || { echo "decode-token: verification failed or no human creator" >&2; exit 1; }

creds=$(your-sts-helper assume-role --subject "$CREATOR_SUB") \
  || { echo "credential exchange failed" >&2; exit 1; }
eval "$creds"

exec "$CLAUDE_RUNNER_CLAUDE_BIN" "$@"

```

在提取的聲明限制授權決定時，使用 `jq -re` 而不是 `jq -r`，以便缺少的聲明以非零狀態退出，而不是將字面字串 `null` 傳遞到下游。由組織服務身份（例如機器人和代理會話）建立的會話帶有 `agent:` 主體而不是 `user:`，因此此範例拒絕它們；如果您的環境提供這些會話，請明確決定包裝指令碼是否為它們回退到預設認證，而不是退出。當您的認證交換需要 SSO 主體或電子郵件時，讀取 `.act.attested_by.sub` 或 `.act.email` 並處理它們的缺失：權杖只在建立表面記錄它們時才帶有它們，[CLI 分派的會話](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing#run-the-test-loop)可能兩者都缺少。有關完整的聲明參考和來自執行器外部服務的驗證，請參閱[驗證會話身份](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)。

## 生命週期掛鉤

生命週期掛鉤用您自己的指令碼替換執行器每個會話管道的階段。使用 `--hooks-dir <path>` 或 `SELF_HOSTED_RUNNER_HOOKS_DIR` 將執行器指向掛鉤目錄。執行器尋找具有眾所周知名稱的可執行檔案；任何不存在的掛鉤都會回退到內建行為，因此您只需編寫所需的掛鉤。掛鉤以執行器自己的權限執行，會話子程序共享該 UID，因此請將掛鉤目錄掛載為唯讀，或將其烘焙到映像中，以便會話代碼無法修改它；請參閱[強化部分](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)。 這些掛鉤不同於[Claude Code 掛鉤](https://code.claude.com/docs/zh-TW/hooks)，後者在會話內執行；生命週期掛鉤在執行器上執行，圍繞會話。

### checkout

每個儲存庫執行一次，代替執行器的內建複製和擷取。使用掛鉤從讀取通過鏡像複製、從存檔植入工作樹，或應用每個會話的 git 驗證。執行器設定：

| 變數                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 說明                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `CLAUDE_RUNNER_REPO_URL`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 要複製的儲存庫 URL，在應用任何 `--git-host-rewrite` 和 `--git-ssh-rewrite` 之後                          |
| `CLAUDE_RUNNER_REPO_REF`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 要簽出的修訂版本：分支、標籤或提交 SHA，如會話要求的那樣。空表示儲存庫的預設分支。                       |
| `CLAUDE_RUNNER_CHECKOUT_PATH`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 工作樹必須留下的絕對路徑                                                                                 |
| `CLAUDE_RUNNER_SESSION_ID`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 標記形式為 `session_...` 的會話 ID，用於記錄和相關性                                                     |
| `CLAUDE_RUNNER_SESSION_UUID`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 規範 UUID 形式的相同會話 ID                                                                              |
| `CLAUDE_RUNNER_API_BASE_URL`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 用於會話範圍呼叫的 Anthropic API 基礎 URL                                                                |
| `CLAUDE_RUNNER_CLIENT_PLATFORM`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 建立會話的用戶端表面，例如 `web_claude_ai`、`desktop_app` 或 `ios`。當會話沒有記錄或識別的表面時未設定。 |
| `CLAUDE_CODE_SESSION_ACCESS_TOKEN`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 會話存取權杖，用於會話範圍的 API 呼叫                                                                    |
| 指令碼必須在 `CLAUDE_RUNNER_CHECKOUT_PATH` 留下一個工作樹，簽出在要求的修訂版本。分離的 HEAD 是可以的；執行器在頂部建立會話的工作分支。執行器之後驗證路徑包含 `.git`；如果您的掛鉤具體化非 git 來源（例如 Perforce 或解包的 tarball），請在執行器的環境中設定 `CLAUDE_RUNNER_SKIP_GIT_VERIFY=1` 以跳過該檢查。基於 Git 的流程（例如工作分支建立和推送結果）需要 git 簽出，因此使用 [`post-session` 掛鉤](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#post-session)從非 git 樹匯出結果。 執行器不會將 git 認證傳遞給掛鉤。相反，從會話的身份鑄造每個會話的複製認證：根據[驗證來自您的服務的權杖](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity#verify-the-token-from-your-service)中所述，使用標準 JWT 庫針對 `CLAUDE_RUNNER_API_BASE_URL` 下的 JWKS 端點驗證 `CLAUDE_CODE_SESSION_ACCESS_TOKEN`，然後讓您的認證服務為權杖的 `act` 聲明中的身份發行短期複製認證。`CLAUDE_RUNNER_CLAUDE_BIN` 未在簽出掛鉤環境中設定，因此 `decode-token` 子命令在此不可用。回退到主機已有的任何 git 驗證（例如 SSH 代理、認證助手或 `.netrc`）也是一個選項。 當掛鉤以非零狀態退出，或以 0 退出而沒有在後面留下可用的簽出時，執行器執行的操作取決於儲存庫： |                                                                                                          |

- **會話推送結果的儲存庫** ：執行器失敗會話，在非零退出時將指令碼的 stderr 尾部呈現給使用者。
- **會話只從中讀取的儲存庫** ，例如新增到執行中會話的儲存庫：執行器記錄帶有失敗詳細資訊的 `[runner:warn]` 行，向會話發佈 `Skipped` 步驟，移除掛鉤在簽出路徑留下的任何內容，並繼續處理其餘儲存庫。當執行器無法立即移除路徑時，它會在會話結束時重試移除。如果跳過使會話完全沒有儲存庫，執行器仍然會失敗會話。

在 v2.1.228 之前，執行器在任何儲存庫的掛鉤失敗時失敗會話，因此掛鉤無法提供的唯讀儲存庫在會話在每個新執行器上恢復時再次失敗會話。 執行器在會話結束後移除簽出路徑。

### post-session

在 Claude Code 子程序退出後、執行器拆卸工作區之前，每個會話執行一次。此掛鉤是您保存未提交工作的唯一機會：在 `--capacity` 高於 1 時，執行器在掛鉤返回後立即刪除每個會話的工作樹，在 `--capacity 1` 時重複使用的[規範複製](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#reuse-a-pre-warmed-checkout)在下一個會話開始時硬重設，因此未提交的追蹤變更在任何一條路徑上都不會存活。典型用途是推送未提交變更的快照分支、存檔日誌或向您自己的系統發出會話結束事件。 掛鉤在每個會話結束時觸發，其中生成了子程序，無論原因如何；下面的 `CLAUDE_RUNNER_EXIT_REASON` 值列舉了這些情況。當執行器突然終止時（例如 VM 搶佔或電源故障）無法觸發；如果您需要針對突然終止的保證，請改為使用 Claude Code `PostToolUse` 掛鉤從會話內定期快照。執行器設定：

| 變數                                         | 說明                                                                                                                                           |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE_RUNNER_SESSION_ID`                   | 標記形式為 `session_...` 的會話 ID                                                                                                             |
| `CLAUDE_RUNNER_SESSION_UUID`                 | 規範 UUID 形式的相同會話 ID                                                                                                                    |
| `CLAUDE_RUNNER_EXIT_REASON`                  | 會話如何結束；請參閱表格下方的值                                                                                                               |
| `CLAUDE_RUNNER_WORKSPACE_PATHS`              | 會話工作樹的冒號分隔絕對路徑。零儲存庫會話為空。                                                                                               |
| `CLAUDE_RUNNER_DEBUG_LOG_PATH`               | 會話的偵錯日誌的路徑，在掛鉤執行時仍在磁碟上                                                                                                   |
| `CLAUDE_RUNNER_API_BASE_URL`                 | 用於會話範圍呼叫的 Anthropic API 基礎 URL                                                                                                      |
| `CLAUDE_RUNNER_CLIENT_PLATFORM`              | 建立會話的用戶端表面，例如 `web_claude_ai`、`desktop_app` 或 `ios`。當會話沒有記錄或識別的表面時未設定。需要 Claude Code v2.1.229 或更新版本。 |
| `CLAUDE_CODE_SESSION_ACCESS_TOKEN`           | 會話存取權杖，用於會話範圍的 API 呼叫                                                                                                          |
| `CLAUDE_RUNNER_EXIT_REASON` 採用四個值之一： |                                                                                                                                                |

- `completed`：會話乾淨地結束。Claude Code 程序正常退出，或會話在仍在執行時被存檔或刪除。
- `failed`：Claude Code 程序崩潰，或在它啟動後設定失敗。
- `interrupted`：執行器停止了會話。它釋放會話以釋放插槽、會話在啟動時逾時、伺服器將會話移出此執行器、執行器正在排水，或會話超過其 [`--kill-session-after-min`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 限制。
- `abandoned`：保留給另一個執行器聲稱的會話。掛鉤目前在該情況下不觸發。

[會話生命週期計數器](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#session-lifecycle-counter-semantics)將釋放、啟動逾時和伺服器移動計為 `completed` 而不是 `interrupted`，因為執行器乾淨地交回了插槽。如果您將掛鉤收據與計數器進行比較，請預期該差異。 掛鉤的結束狀態永遠不會影響會話結果；失敗被記錄並忽略。執行器在每個會話結束（包括執行器關閉）時等待最多 `--post-session-hook-timeout-sec`（預設 60 秒）。此範例將未提交的工作保存到救援分支：

```
#!/usr/bin/env bash
set -u
IFS=':'
# Pin config the session could have planted in the checkout's .git/config:
# -c overrides beat repo-local settings, blocking session-written fsmonitor,
# hook-path, and gpg-program config from executing code with the hook's
# privileges. Repo-local credential.helper, core.sshCommand, and pushurl
# still apply; if the hook holds credentials the session didn't, pin the
# push URL and helper too (see the note below the script).
g() { git -c core.fsmonitor=false -c core.hooksPath=/dev/null \
        -c commit.gpgsign=false "$@"; }
for ws in $CLAUDE_RUNNER_WORKSPACE_PATHS; do
  cd "$ws" 2>/dev/null || continue
  [ -z "$(g status --porcelain 2>/dev/null)" ] && continue
  g add -A
  g commit -q -m "runner snapshot: $CLAUDE_RUNNER_SESSION_ID ($CLAUDE_RUNNER_EXIT_REASON)" || continue
  g push -q origin "HEAD:refs/heads/rescue/$CLAUDE_RUNNER_SESSION_ID" || true
done

```

掛鉤使用執行器主機自己環境中可用的任何 git 認證進行推送。在[映像中無認證的姿態](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git)下，包括內建複製通過 Anthropic git 代理時，沒有任何認證，因此在推送前在掛鉤內鑄造短期推送認證：將掛鉤在 `CLAUDE_CODE_SESSION_ACCESS_TOKEN` 中接收的會話權杖與您自己的權杖服務交換，如[驗證會話身份](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)所述進行驗證。當掛鉤持有會話沒有的認證時，也要固定它推送的位置：將 `origin` 替換為操作員提供的 URL，並傳遞 `-c credential.helper=` 加上您自己的助手，以便會話寫入的儲存庫本地設定無法重定向經過認證的推送。

#### 執行器釋放會話時的掛鉤計時

已釋放的會話可以在另一個執行器上恢復。在 v2.1.236 或更新版本的執行器上，會話在釋放時執行的操作決定了它是否可以在此掛鉤完成之前在另一個執行器上恢復：

- **在轉換後閒置，或在啟動時逾時** ：執行器停止子程序並執行此掛鉤至完成。只有這樣它才會釋放會話。在掛鉤執行時發送的使用者訊息無法在掛鉤完成之前在另一個執行器上恢復會話。
- **等待使用者回答提示，例如權限提示** ：執行器首先釋放會話，然後執行此掛鉤。在掛鉤執行時發送的使用者訊息可以在掛鉤完成之前在另一個執行器上恢復會話。

這適用於執行器釋放會話的任何時間：在閒置逾時、在 [`--retire-at`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 時間，以及 在 v2.1.260 或更新版本的執行器上，在會話的 [`--kill-session-after-min`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 限制。轉換已結束且僅持有背景任務的會話在此計為閒置。在 v2.1.236 之前，執行器在兩種情況下都首先釋放會話，然後執行此掛鉤。 在 `SIGTERM` 排水期間，執行器持有會話租約直到掛鉤完成；請參閱[關閉計時](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#shutdown-timing)。

### command

在簽出後每個會話執行一次，代替內建的子程序生成。掛鉤接收與[包裝指令碼](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#wrapper-scripts)相同的環境，應該以相同的方式 `exec` 進入 `"$CLAUDE_RUNNER_CLAUDE_BIN"`。使用 `command` 掛鉤將所有自訂保留在一個掛鉤目錄中；當包裝指令碼在其他地方時使用 `--exec-path`。如果也設定了 `--exec-path`，旗標優先，`command` 掛鉤被忽略。 始終 `exec` 執行器自己的二進位檔案，而不是 PATH 解析的 `claude`；否則您會破壞[版本固定](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#pin-the-version)。

## 隨需啟動的執行器

您可以不使用固定的執行器群組，而是每個工作階段啟動一個執行器。協調器是一個獨立的、無狀態的子命令，它會輪詢 Anthropic 以取得啟動請求，每個沒有可用執行器的已排隊工作階段一個請求，並為每個請求執行您的 `spawn-runner` hook。您的 hook 會將工作負載提交到您的平台：Kubernetes Job、EC2 執行個體、Nomad dispatch。 隨需啟動的執行器改善了認證衛生。在固定群組上，環境祕密存在於每個執行器主機上，這與執行使用者工作階段的主機相同。使用協調器，環境祕密只保留在協調器主機上，該主機永遠不會執行使用者程式碼；每個啟動的執行器都會收到一個一次性工作單，它只註冊一個執行器，然後過期。 若要啟動協調器，請傳遞環境祕密和包含可執行 `spawn-runner` 指令碼的 hooks 目錄：

```
claude self-hosted-runner orchestrator \
  --environment-secret-file /etc/claude/environment-secret \
  --hooks-dir /etc/claude/hooks

```

協調器在輪詢之間不保留任何狀態，因此您可以針對同一環境執行兩個或多個副本以實現可用性。每個啟動請求由伺服器端的恰好一個副本聲稱。所有副本必須使用相同的 `--expected-spawn-seconds` 值；請參閱 [hook 合約](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#the-spawn-runner-hook)。

### spawn-runner hook

協調器為每個啟動請求執行一次 `${hooks-dir}/spawn-runner`。hook 必須非同步提交工作，不等待執行器啟動，並在 `--hook-timeout` 內返回，預設為 60 秒。hook 接收：

| 變數                                         | 說明                                                                                                                                                                                                                                                         |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CLAUDE_RUNNER_WORK_ORDER_FILE`              | 包含已簽署工作單 JWT 的暫存檔案路徑，新執行器使用此 JWT 進行註冊。hook 退出後刪除。不要記錄檔案的內容。                                                                                                                                                      |
| `CLAUDE_RUNNER_ORDER_ID`                     | 不透明的冪等性金鑰，每個啟動請求唯一，對 Kubernetes 資源名稱安全。將其用作您的佈建程式的去重金鑰。                                                                                                                                                           |
| `CLAUDE_RUNNER_SESSION_ID`                   | 此請求所針對的工作階段。對於預熱請求為空，預熱請求會在設定 [`--min-idle`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#orchestrator-cli-flags) 時在任何特定工作階段之前啟動待命執行器，因此不要假設變數已設定。                     |
| `CLAUDE_RUNNER_SESSION_UUID`                 | 相同的工作階段 ID，採用規範 UUID 形式。對於預熱請求為空。                                                                                                                                                                                                    |
| `CLAUDE_RUNNER_ATTEMPT`                      | 此工作階段已有多少個啟動請求。對於預熱請求為 `0`。                                                                                                                                                                                                           |
| `CLAUDE_RUNNER_ORDER_SERVER_TIME`            | 來自輪詢回應的 HTTP `Date` 標頭的伺服器時間。當 hook 驗證工作單 JWT 的 `exp` 時，請與此值進行比較，而不是本地時鐘，以容許時間偏差。當閘道省略標頭時為空。                                                                                                    |
| `CLAUDE_RUNNER_POOL_ID`                      | 新執行器應加入的環境的 ID，採用 `ccpool_...` 形式                                                                                                                                                                                                            |
| `CLAUDE_RUNNER_ACCOUNT_ID`                   | 排隊工作階段的帳戶的標記 ID，用於按帳戶路由、配額或退款。不可用時為空，Claude Tag 頻道工作階段始終為空，這些工作階段沒有帳戶排隊。                                                                                                                           |
| `CLAUDE_RUNNER_ACCOUNT_EMAIL`                | 排隊工作階段的帳戶的電子郵件。不可用時為空。將電子郵件視為個人可識別資訊，不要記錄它。                                                                                                                                                                       |
| `CLAUDE_RUNNER_PRIMARY_REPO_URL`             | 工作階段的第一個 git 來源的 URL，用於路由到預先準備了該儲存庫的執行器。工作階段沒有 git 來源時為空。                                                                                                                                                         |
| `CLAUDE_RUNNER_PRIMARY_REPO_REVISION`        | 工作階段的第一個 git 來源的修訂版本：分支、SHA 或標籤。未指定時為空。                                                                                                                                                                                        |
| `CLAUDE_RUNNER_REPO_SOURCES`                 | 所有工作階段的 git 來源的 `{url, revision}` 的 JSON 陣列，用於在次要儲存庫上路由的 hook。沒有來源時為空。                                                                                                                                                    |
| `CLAUDE_RUNNER_CORRELATION_ID`               | 在工作階段建立時提供的相關 ID，回顯以便 hook 可以將此工作單對應到建立工作階段的請求。工作階段沒有時為空。                                                                                                                                                    |
| `CLAUDE_RUNNER_CLIENT_PLATFORM`              | 建立工作階段的用戶端表面，例如 `web_claude_ai`、`desktop_app`、`ios` 或 `scheduled_trigger`，用於採用分析。當工作階段沒有記錄或識別的表面時未設定，對於預熱請求也未設定；使用 `[ -n "${CLAUDE_RUNNER_CLIENT_PLATFORM:-}" ]` 檢查它，在 `set -u` 下保持安全。 |
| 啟動的執行器使用工作單代替環境祕密進行註冊： |                                                                                                                                                                                                                                                              |

- **使用工作單啟動它** ：將 [`--environment-secret-file`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 指向包含工作單 JWT 的檔案，或將 `SELF_HOSTED_RUNNER_ENVIRONMENT_SECRET` 設定為 JWT 值。
- **在 hook 退出前複製 JWT** ：協調器在 hook 退出後刪除工作單檔案，因此將 JWT 複製到您提交的工作負載中，例如啟動的 Job 上的 Kubernetes Secret，而不是透過檔案路徑。
- **在啟動的執行器上使用`--capacity 1`** ：工作階段綁定的工作單恰好註冊一個綁定到該工作階段的執行器，因此更高的容量會新增永遠不會接收工作的插槽，執行器在啟動時會記錄警告。
- **預熱工作單註冊未綁定** ：待命執行器未綁定到工作階段，並像固定群組執行器一樣聲稱已排隊的工作。

合約有四個佈建程式無關的規則：

1. **在`CLAUDE_RUNNER_ORDER_ID` 上保持冪等性。** 重新傳遞相同的請求最多必須啟動一個執行器。從 ID 衍生確定性資源名稱，並讓您的平台拒絕重複項。
1. **不要重試工作負載。** 一個訂單 ID 最多意味著建立一個工作負載。如果執行器永遠不註冊，Anthropic 會在 `--expected-spawn-seconds` 後使用新的訂單 ID 重新請求。
1. **使用退出代碼合約。** 退出 0 表示已提交。退出 1 表示可重試的失敗；工作階段退避並被重新提供。退出 2 或更高表示不可重試；工作階段被阻止再次啟動，直到 [Owner](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments) 在環境的 **Activity** 標籤中選擇 **Retry** 。在非零退出時，hook 的 stderr 的尾部會作為失敗原因出現在那裡，因此將可操作的錯誤寫入 stderr，永遠不要寫入祕密。對於預熱請求，沒有工作階段失敗：協調器只在本地記錄非零退出，伺服器在租約後重新請求啟動。
1. **將`--expected-spawn-seconds` 設定為至少您的 p99 啟動時間。** 這是伺服器端租約。所有協調器副本必須使用相同的值。

hook 寫入 stdout 或 stderr 的所有內容都會出現在協調器的日誌中，認證會自動編輯。如果工作階段保持排隊，請檢查協調器的 `/healthz` 主體以取得佇列計數，然後在 [**Cloud environments** 管理頁面](https://claude.ai/admin-settings/cloud-environments) 上開啟您環境的 **Activity** 標籤：在那裡展開失敗的工作階段以查看其啟動錯誤，並選擇 **Retry** 以重新請求它。

## MCP 伺服器

要在每個會話中提供 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)，請在映像構建時使用與桌面安裝上使用的相同 `claude mcp add` 命令添加它們。如果您的執行器是裸程序而不是容器，請在主機上以執行器的使用者身份執行相同的命令，然後重新啟動執行器：它在啟動時讀取主機設定一次。`--scope user` 旗標是必需的；預設本地範圍寫入執行器不植入會話的每個目錄鍵下。例如，在您的 Dockerfile 中：

```
RUN claude mcp add --scope user sidecar -- /usr/local/bin/mcp-sidecar
RUN claude mcp add --scope user --transport http internal http://mcp-gateway.svc.cluster.local:8080

```

執行器在啟動時快照主機的設定一次。快照從主機的 `.claude.json` 擷取 `mcpServers` 鍵，該鍵位於 `~/.claude/` 旁邊而不是內部，執行器僅將該鍵植入每個會話的隔離設定；帳戶狀態和專案歷史被丟棄。要確認伺服器到達會話，請在環境上啟動會話並要求 Claude 列出其 MCP 工具；執行器也會為任何擷取的條目記錄啟動警告，其 `type` 它無法識別並丟棄該條目，因此您可以看到為什麼該伺服器在會話中缺失。當設定 `SELF_HOSTED_RUNNER_HOST_CONFIG_DIR` 時，執行器改為從該目錄讀取 `.claude.json`，因此將變數指向空目錄也會禁用 MCP 植入。 Claude Code 也從其他來源載入 MCP 伺服器：

- 企業範圍[受管 MCP 檔案](https://code.claude.com/docs/zh-TW/managed-mcp)在其標準系統路徑：Linux 執行器主機上的 `/etc/claude-code/managed-mcp.json`，macOS 主機上的 `/Library/Application Support/ClaudeCode/managed-mcp.json`。將其用於鎖定的艦隊，其中只有管理員列出的伺服器可能載入。請參閱[使用 managed-mcp.json 的獨佔控制](https://code.claude.com/docs/zh-TW/managed-mcp#exclusive-control-with-managed-mcp-json)以了解優先順序規則。當此檔案在執行器主機上時，Claude Code 跳過 Anthropic 的控制平面傳遞給會話的 MCP 伺服器，包括 claude.ai 連接器，並在會話子程序的 stderr 上命名它們，執行器在 `debug` 日誌級別記錄。在 v2.1.229 之前，這些會話在啟動時以 `You cannot dynamically configure MCP servers when an enterprise MCP config is present` 退出。
- 執行器主機上[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中的 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 鍵：提供 HTTP 和 SSE 伺服器而不取得獨佔控制，因此來自其他來源的伺服器仍然載入。需要 Claude Code v2.1.259 或更新版本。
- `<repo>/.mcp.json`：專案範圍。將檔案提交到儲存庫；其伺服器在雲端會話中自動核准。

當為您的組織啟用連接器傳遞時，Anthropic 的控制平面將您在 claude.ai 上設定的連接器傳遞給透過伺服器提供的 MCP 設定路由的互動建立的會話，通過 `api.anthropic.com`。以程式設計方式建立的會話（例如 [CLI 分派](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing#run-the-test-loop)）不接收連接器傳遞；改為透過本部分列出的其他來源之一為它們提供 MCP 伺服器。子程序的 OAuth 權杖不帶有直接擷取連接器的範圍，因此子程序不會自行嘗試該擷取；傳遞是伺服器驅動的。 `settings.json` 不帶有 MCP 伺服器定義，設定架構中沒有頂級 `mcpServers` 欄位。在受管設定中，使用 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 鍵提供伺服器。 會話繼承執行器的環境，因此在那裡設定 [`ENABLE_TOOL_SEARCH`](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search) 以控制執行器生成的每個會話的 MCP 工具搜尋；MCP 頁面涵蓋了這些值。

## 提示會話推送其工作

Anthropic 託管的會話執行 [`Stop` 掛鉤](https://code.claude.com/docs/zh-TW/hooks#stop)，Claude Code 掛鉤在 Claude 完成回應時執行，提示 Claude 提交並推送其工作。執行器不安裝一個。沒有它，以未提交變更結束的會話只在執行器的磁碟上留下該工作，claude.ai/code 中的**建立 PR** 按鈕保持非活動狀態，直到分支存在於遠端。 下面的參考實現有兩個部分。將設定塊合併到執行器主機上的 `~/.claude/settings.json` 中，執行器將其植入每個會話，並將指令碼保存為執行器主機上的 `~/.claude/hooks/stop-hook-nudge.sh` 並使其可執行：

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "timeout": 10,
            "command": "\"$CLAUDE_CONFIG_DIR/hooks/stop-hook-nudge.sh\""
          }
        ]
      }
    ]
  }
}

```

```
#!/bin/sh
# Stop-hook reference implementation for self-hosted runners.
# # Nudges Claude once per turn if the project directory has uncommitted
# changes OR unpushed commits, so work isn't lost when an idle session
# is released and so the "Create PR" button on claude.ai/code lights up.
# # Runner-level (no repo changes): drop this file at ~/.claude/hooks/ on
# the runner host and merge the accompanying Stop-hook settings block
# into ~/.claude/settings.json — the runner seeds both into every session.
# Repo-level alternative: commit to <repo>/.claude/hooks/ and change the
# settings.json command path to $CLAUDE_PROJECT_DIR/.claude/hooks/.
# # stdin: hook JSON payload (see https://code.claude.com/docs/en/hooks)
# stdout: {"decision":"block","reason":"..."} to nudge, or nothing to allow stop.

# Re-entry guard: the harness sets stop_hook_active=true when re-invoking
# the Stop hook after a block. Bail so we only nudge once per turn. The
# harness emits compact JSON (no space after the colon), which this
# pattern relies on; use jq if you need a whitespace-tolerant check.
in=$(cat)
case "$in" in *'"stop_hook_active":true'*) exit 0 ;; esac

d="$CLAUDE_PROJECT_DIR"

# Not a git repo → nothing to nudge.
git -C "$d" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# No remote → "push to the remote" is unsatisfiable; bail.
[ -z "$(git -C "$d" remote 2>/dev/null)" ] && exit 0

# Uncommitted changes (staged, unstaged, or untracked). Exclude .claude/
# entirely — operator-seeded settings and CLI-written runtime state
# (scheduler lock, worktrees, routine state) live there and neither is
# "uncommitted work" the model needs to push.
s=$(git -C "$d" status --porcelain -- . ':(exclude).claude/' 2>/dev/null)
if [ -n "$s" ]; then
  printf '{"decision":"block","reason":"There are uncommitted changes in the repository. Please commit and push these changes to the remote branch."}'
  exit 0
fi

# Unpushed commits. Count commits on HEAD not reachable from any
# remote-tracking ref or FETCH_HEAD. This works uniformly for:
#   - init+fetch checkouts (runner default: only FETCH_HEAD exists)
#   - clone-based checkouts (origin/* exist)
#   - the runner default: the child starts on the session's outcome
#     branch, which the runner creates after checkout
#   - detached HEAD, when a custom setup skips that branch creation
# With no reference point at all (never fetched), stay silent rather
# than false-positive on a read-only turn.
base=""
git -C "$d" rev-parse --verify -q FETCH_HEAD >/dev/null && base="FETCH_HEAD"
if [ -z "$base" ] && [ -z "$(git -C "$d" for-each-ref --count=1 refs/remotes/origin 2>/dev/null)" ]; then
  exit 0
fi
# shellcheck disable=SC2086  # $base is either "" or "FETCH_HEAD", intentional word-split
unpushed=$(git -C "$d" rev-list HEAD --not $base --remotes=origin --count 2>/dev/null) || unpushed=0
if [ "$unpushed" -gt 0 ]; then
  branch=$(git -C "$d" symbolic-ref --short -q HEAD)
  if [ -n "$branch" ]; then
    # $branch is attacker-influenced — git-check-ref-format(1) allows `"`
    # in ref names. `\` is forbidden (rule 10) but escaped anyway as cheap
    # defense-in-depth.
    # Escape JSON metacharacters before interpolating into the hand-built
    # payload so a branch like x","continue":false can't inject keys into
    # the hook-output JSON the harness parses. $unpushed is safe — the
    # -gt guard above rejects anything that isn't a plain integer.
    branch_esc=$(printf '%s' "$branch" | sed 's/\\/\\\\/g; s/"/\\"/g')
    printf '{"decision":"block","reason":"There are %s unpushed commit(s) on branch '\''%s'\''. Please push these changes to the remote repository."}' "$unpushed" "$branch_esc"
  else
    printf '{"decision":"block","reason":"There are %s unpushed commit(s) on a detached HEAD. Please create a branch and push it to the remote repository."}' "$unpushed"
  fi
  exit 0
fi

exit 0

```

掛鉤在會話結束前提示 Claude 提交並推送，當目錄不是 git 儲存庫或沒有遠端時保持沉默。

## 權限和工具核准

自託管會話沒有連接的終端，因此未回答的權限提示會延遲轉換，直到使用者在 UI 中回應。Anthropic 的控制平面使用工作負載發送每個會話的工具清單和權限規則；預設設定預先核准常規工具呼叫（包括 `Bash`），雲端會話[預先核准檔案編輯，無論模式如何](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)。沒有任何東西預先核准的呼叫會透過會話 UI 提示。 僅在環境的會話容器執行[預設拒絕網路出口](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#default-deny-egress)和[強化部分](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)中其餘部分的環境上固定自動模式。常規工具呼叫（包括 `Bash` 網路請求）在預設預先核准的工具集和自動模式中都無需人工干預執行，因此網路邊界是限制這些呼叫可以到達的位置。 要無論控制平面發送什麼都將提示保持在最低限度，請從您的包裝指令碼或 [`command` 掛鉤](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#command)固定[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)。自動模式讓會話無需常規權限提示執行：單獨的分類器模型在它們執行前審查操作並阻止它拒絕的操作，明確的詢問規則仍然強制提示；權限模式頁面涵蓋分類器檢查的內容。執行器在呼叫包裝指令碼前附加伺服器計算的旗標，對於單值旗標（例如 `--permission-mode`），解析器尊重最後出現的旗標，因此您在 `"$@"` 後附加的旗標覆蓋伺服器發送的值：

```
#!/bin/bash
exec "$CLAUDE_RUNNER_CLAUDE_BIN" "$@" --permission-mode auto

```

要改為預先核准特定工具，請附加 `--allowed-tools` 和您的規則，例如 `--allowed-tools "Bash(bazel *) Bash(yarn *) mcp__internal__*"`。列表旗標（例如 `--allowed-tools` 和 `--disallowed-tools`）在出現時累積而不是覆蓋，因此您的規則應用在控制平面發送的任何規則之上。要縮小，請附加 `--disallowed-tools`，即使另一個規則允許工具也會拒絕工具。

### 如何組合每個會話的設定

執行器為每個會話提供自己的設定目錄，從執行器在啟動時擷取的主機 `~/.claude/` 的記憶體內快照植入：`settings.json`、`CLAUDE.md`、掛鉤、代理、命令和技能在您的執行器映像中應用於每個會話作為使用者級基線。因為快照在啟動時進行，執行中主機上的設定變更僅在執行器重新啟動後生效。設定 `SELF_HOSTED_RUNNER_HOST_CONFIG_DIR` 以從不同路徑植入，或將其指向空目錄以禁用植入。 儲存庫提交的 `.claude/settings.json` 作為專案設定分層。會話也從執行器映像中的標準系統路徑讀取 [`managed-settings.json`](https://code.claude.com/docs/zh-TW/settings#where-settings-live)。其鍵是否與[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)一起應用遵循 [Claude Code 如何組合受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)：預設情況下，當您的組織傳遞任何伺服器受管鍵時，會話忽略執行器映像的檔案，除了 [Claude Code 從每個管理來源讀取的鍵](https://code.claude.com/docs/zh-TW/managed-settings#keys-read-from-every-admin-source)，例如 `env` 塊、沙箱鎖、沙箱二進位路徑和 `forceRemoteSettingsRefresh`。請參閱[設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)。 當 Anthropic 的控制平面為會話提供 [Claude Code 掛鉤](https://code.claude.com/docs/zh-TW/hooks)時，執行器將它們安裝在旁邊，而不是在您自己的設定上。需要 Claude Code v2.1.229 或更新版本。

- **它們著陸的位置** ：執行器將每個提供的掛鉤指令碼寫入會話設定目錄的保留 `hooks/.ccr-launcher/` 子目錄，並在單獨的設定檔案中註冊指令碼，該檔案使用 `--settings` 傳遞給會話，保留植入的 `settings.json` 和您自己的指令碼在 `hooks/<name>` 不變。執行器為每個會話重建保留子目錄，不將主機內容在 `~/.claude/hooks/.ccr-launcher/` 植入會話。
- **誰編寫它們** ：控制平面從其自己部署中的固定常數填充指令碼，永遠不從每個會話或第三方輸入。
- **什麼仍然管理它們** ：透過 `--settings` 傳遞的掛鉤進入普通合併掛鉤設定，而不是受管層，因此您的受管設定仍然適用。`disableAllHooks` 禁用它們，它們不在 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly) 保持載入的類別中。

### 儲存庫提交的權限規則

不要在儲存庫提交的 `permissions.allow` 中放置裸 `"Edit"`、`"Write"` 或 `"NotebookEdit"` 條目。裸檔案工具規則匹配工具，無論路徑如何，授予主機上任何地方的寫入，而不僅僅是工作區，因此執行器的寫入範圍限制保護標誌會話；使用 [`--confine-repo-settings enforce`](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags) 它拒絕生成會話而不是記錄並繼續。請參閱[強化部分](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#harden-your-deployment)。 儲存庫根本不需要檔案工具規則：雲端會話[預先核准檔案編輯，無論模式如何](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)。如果您確實提交規則，請將其限定於工作區，例如 `"Edit(/**)"`；單個前導斜杠相對於專案根目錄，這是會話的工作區。裸檔案工具規則在操作員的主機級 `settings.json` 中很好，因為該檔案不是儲存庫提交的。 `defaultMode` 為 `auto` 僅從映像寬或使用者級設定檔案中尊重，因此簽出的儲存庫無法授予自己自動模式。有關雲端會話接受的模式和完整規則語法，請參閱[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。

## 接下來

- [參考](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference)：每個 CLI 旗標、環境變數和度量
- [驗證會話身份](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)：驗證來自執行器外部服務的會話權杖

是否 助手
