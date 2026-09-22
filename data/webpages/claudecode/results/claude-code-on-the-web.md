雲端工作階段處於研究預覽階段，適用於 Pro、Max 和 Team 使用者，以及具有高級席位或 Chat + Claude Code 席位的 Enterprise 使用者。 雲端工作階段是在雲端基礎設施上執行的 Claude Code 工作階段，而不是在您的機器上執行。預設情況下，它在 Anthropic 管理的基礎設施上執行，或在您的組織的[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)上執行（如果路由到那裡）。工作階段在您關閉筆記型電腦後仍會繼續執行，您可以從任何裝置檢查或控制它。 您可以從以下任何介面啟動雲端工作階段：

- **瀏覽器** ：[claude.ai/code](https://claude.ai/code)，也稱為網頁版 Claude Code
- **行動裝置** ：[Claude 應用程式](https://code.claude.com/docs/zh-TW/mobile)中的 **Code** 標籤
- **桌面應用程式** ：當您[啟動工作階段](https://code.claude.com/docs/zh-TW/desktop#run-long-running-tasks-in-the-cloud)時，選擇 **Cloud** 而不是 **Local**
- **終端** ：[`claude --cloud`](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud)
- **例行工作** ：[排程和觸發的執行](https://code.claude.com/docs/zh-TW/routines)每次都作為雲端工作階段執行

若要讓 Claude 為一項工作啟動並追蹤許多雲端工作階段，請使用[專案](https://code.claude.com/docs/zh-TW/claude-projects)。在您的終端、IDE 或選擇了 **Local** 的桌面應用程式中的工作階段在您自己的機器上執行。若要從您的手機或瀏覽器控制其中一個本機工作階段，請使用[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)。 初次使用雲端工作階段？從[開始使用](https://code.claude.com/docs/zh-TW/web-quickstart)開始，連接您的 GitHub 帳戶並提交您的第一個任務。 本頁涵蓋：

- [雲端環境](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#cloud-environments)：工作階段執行的位置，以及如何配置該位置
- [GitHub 驗證選項](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)：連接 GitHub 的兩種方式
- [在終端和雲端之間移動任務](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#move-tasks-between-terminal-and-cloud)，使用 `--cloud` 和 `--teleport`
- [使用工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#work-with-sessions)：權限模式、檢查、共享、封存、刪除
- [自動修復拉取請求](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)：自動回應 CI 失敗和審查評論
- [安全性和隔離](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#security-and-isolation)：工作階段如何隔離
- [限制](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#limitations)：速率限制和平台限制

## 雲端環境

每個雲端工作階段都在一個[雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)中執行，這是一個已保存的設定，控制網路存取、環境變數和設定指令碼。如果您還沒有環境，上線會設定一個**預設** 環境，具有[**信任** 網路存取](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)，要麼為您建立它，要麼要求您建立它。請參閱[預設環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)，了解在您的計畫上會發生哪種情況，以及當您有多個環境時工作階段如何選擇環境。 相同的環境適用於您啟動雲端工作階段的任何地方：網頁、終端、[Claude Tag](https://claude.com/docs/claude-tag/overview)、[例行工作](https://code.claude.com/docs/zh-TW/routines)，以及行動和 Desktop 應用程式。Claude Tag 頻道工作階段僅使用組織級別環境，要麼是[共享環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)，要麼是[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)。 請參閱[設定雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)以變更環境允許的內容、設定變數或新增設定指令碼，以及[已安裝的工具](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)以了解工作階段在沒有任何設定的情況下包含的內容。

## GitHub 驗證選項

雲端工作階段需要存取您的 GitHub 儲存庫以複製程式碼和推送分支。您可以通過兩種方式授予存取權限：

| 方法                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 運作方式                                                                                  | 工作階段可以存取的儲存庫                                             | 最適合                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **GitHub App**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 在[網頁上線](https://code.claude.com/docs/zh-TW/web-quickstart)期間授權 Claude GitHub App | 任何公開儲存庫，以及安裝了 Claude GitHub App 的私人儲存庫            | 瀏覽器上線；想要[自動修復](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)的團隊 |
| **`/web-setup`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 在您的終端中執行 `/web-setup` 以將您的本機 `gh` CLI 令牌傳送到您的 Claude 帳戶            | 您的 `gh` 令牌可以存取的任何儲存庫，無論是否安裝了 Claude GitHub App | 已經使用 `gh` 的個人開發者                                                                                         |
| 在儲存庫上安裝 Claude GitHub App 也會為其中的提取請求啟用[自動修復](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)。 [專案](https://code.claude.com/docs/zh-TW/claude-projects)中的執行緒需要在它們複製的每個儲存庫上安裝 Claude GitHub App，無論您使用哪種方法連接。請參閱[設定 GitHub 存取](https://code.claude.com/docs/zh-TW/claude-projects#set-up-github-access)。 有關 `/schedule` 如何在建立例行工作之前檢查儲存庫存取，請參閱[儲存庫和分支權限](https://code.claude.com/docs/zh-TW/routines#repositories-and-branch-permissions)。有關 `/web-setup` 的逐步說明，請參閱[從您的終端連接](https://code.claude.com/docs/zh-TW/web-quickstart#connect-from-your-terminal)，包括 `/web-setup` 儲存的內容以及如何移除它。 快速網頁設定是一個組織設定，讓成員使用 `/web-setup` 連接 GitHub，在瀏覽器上線期間跳過 Claude GitHub App 安裝提示，並讓瀏覽器上線為他們建立[**預設** 環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)，而不是顯示環境表單。在 Team 和 Enterprise 計畫上，預設情況下它是關閉的，這會隱藏 `/web-setup`。[擁有者](https://code.claude.com/docs/zh-TW/server-managed-settings#access-control)可以在 [**管理設定 > Claude Code**](https://claude.ai/admin-settings/claude-code) 使用**快速網頁設定** 切換來開啟它。 |                                                                                           |                                                                      |                                                                                                                    |
| 啟用[零資料保留](https://code.claude.com/docs/zh-TW/zero-data-retention)的組織無法使用 `/web-setup` 或其他雲端工作階段功能。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |                                                                                           |                                                                      |                                                                                                                    |

## 在終端和雲端之間移動任務

這些工作流程需要[Claude Code CLI](https://code.claude.com/docs/zh-TW/quickstart)登入到相同的 claude.ai 帳戶。您可以從終端啟動新的雲端工作階段，或將雲端工作階段拉入終端以在本機繼續。雲端工作階段即使在您關閉筆記型電腦後仍會保留，您可以從任何地方（包括 Claude 行動應用程式）監控它們。 從 CLI，工作階段交接是單向的：您可以使用 `--teleport` 將雲端工作階段拉入終端，但無法將現有終端工作階段推送到雲端。`--cloud` 旗標搭配任務描述會為您目前的儲存庫建立新的雲端工作階段；搭配 `-p` 和工作階段 ID 或 claude.ai/code URL 時，它會改為[將訊息排隊到該現有工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-follow-ups-from-the-cli)。[Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop#continue-in-another-surface)提供可將本機工作階段發送到雲端的**在另一個表面繼續** 功能表。

### 從終端到雲端

使用 `--cloud` 旗標從命令列啟動雲端工作階段：

```
claude --cloud "Fix the authentication bug in src/auth/login.ts"

```

這會在 claude.ai 上建立新的雲端工作階段。雲端 VM 複製您目前目錄的 GitHub 遠端，位於您目前的分支，而不是您的本機簽出，因此如果您有本機提交，請先推送。請參閱[不使用 GitHub 發送本機儲存庫](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-local-repositories-without-github)以了解 Claude Code 上傳您的本機儲存庫而不是複製的情況。 `--cloud` 一次適用於單一儲存庫。任務在雲端執行，而您繼續在本機工作。較舊的 `--remote` 拼寫仍然可作為 `--cloud` 的已棄用別名。 當雲端容器啟動時，CLI 會顯示設定步驟的即時檢查清單，例如複製儲存庫和執行您的[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)。它會排隊您在佈建期間輸入的訊息，並在工作階段準備好後發送它們。 `--cloud` 建立雲端工作階段。`--remote-control` 無關：它讓您從 claude.ai 或 Claude 應用程式監控和引導本機 CLI 工作階段。請參閱[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)。 在 claude.ai 或 Claude 行動應用程式上開啟工作階段以檢查進度或直接互動。從那裡，您可以引導 Claude、提供反饋或回答問題，就像任何其他對話一樣。 如果 Claude 提出問題且工作階段閒置，您仍然可以在回來時回答，直到[環境過期](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#environment-expired)，工作階段會從您的回答繼續。

#### 雲端任務的提示

**在本機規劃，在雲端執行** ：對於複雜任務，在規劃模式下啟動 Claude 以協作制定方法，然後將工作發送到雲端：

```
claude --permission-mode plan

```

在規劃模式下，Claude 讀取檔案、執行命令以探索並提出計畫，而不編輯原始程式碼。一旦您對計畫感到滿意，將計畫保存到儲存庫、提交和推送，以便雲端 VM 可以複製它。然後為自主執行啟動雲端工作階段：

```
claude --cloud "Execute the migration plan in docs/migration-plan.md"

```

**並行執行任務** ：每個 `--cloud` 命令建立自己的雲端工作階段，獨立執行。您可以啟動多個任務，它們都會在單獨的工作階段中同時執行：

```
claude --cloud "Fix the flaky test in auth.spec.ts"
claude --cloud "Update the API documentation"
claude --cloud "Refactor the logger to use structured output"

```

當工作階段完成時，您可以從 claude.ai/code 建立 PR，或[傳送](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-cloud-to-terminal)工作階段到終端以繼續工作。

#### 發送沒有 GitHub 的本機儲存庫

當您從未連接到 GitHub 的儲存庫執行 `claude --cloud` 時，或從 Claude GitHub App 未安裝的 github.com 儲存庫執行時，Claude Code 會捆綁您的本機儲存庫並直接上傳到雲端工作階段。即使您使用 `/web-setup` 連接了 GitHub，這也適用。捆綁包括您的完整儲存庫歷史記錄，跨所有分支，加上對追蹤檔案的未提交變更。 在 macOS、Linux 和 WSL 上，Claude Code 會將名稱類似認證或金鑰的檔案的未提交變更排除在上傳之外，並列出它排除的檔案名稱。這涵蓋 `.env` 檔案、Terraform `*.tfvars` 檔案和金鑰檔案，例如 `id_rsa` 和 `*.pem`。工作階段會以每個檔案的已提交版本啟動，或如果沒有已提交的檔案，則不使用該檔案。在連結的 worktree、子模組或類似配置中，Claude Code 會上傳這些變更與其餘部分一起，並列出它上傳的檔案名稱。 若要即使在 Claude Code 會以其他方式從遠端複製時也強制上傳捆綁，請設定 `CCR_FORCE_BUNDLE=1`：

```
CCR_FORCE_BUNDLE=1 claude --cloud "Run the test suite and fix any failures"

```

捆綁的儲存庫必須符合這些限制：

- 目錄必須是至少有一個提交的 git 儲存庫
- 捆綁的儲存庫必須在 100 MB 以下。較大的儲存庫回退到僅捆綁目前分支，然後回退到工作樹的單一壓縮快照，並且僅在快照仍然太大時失敗
- 未追蹤的檔案不包括；在您希望雲端工作階段看到的檔案上執行 `git add`
- 從捆綁建立的工作階段只有在您的 [GitHub 連接](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)對該儲存庫具有推送存取權時，才能推送回 GitHub 遠端

### 從 CLI 發送後續訊息

一旦雲端工作階段執行，無論它在何處執行，都可以從任何您使用 `claude auth login` 登入的機器上的 `claude` CLI 向它發送後續訊息。CLI 使用您的 Anthropic 帳戶認證進行驗證，並且不發送本機工作階段狀態，因此命令不需要從啟動工作階段的機器執行，並且在每個 shell 中都相同，包括 PowerShell。 該命令發佈一條訊息並退出：

```
claude -p "your message" --cloud <session-id>

```

CLI 將訊息排隊到工作階段並退出，不等待回覆。使用它來引導長時間執行的工作階段、在目前工作階段仍在完成時排隊下一步，或從 [CI 指令碼](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing#run-the-test-loop)發送後續訊息。您也可以在 stdin 上管道訊息，而不是作為引數傳遞：`echo "your message" | claude -p --cloud <session-id>`。 對於 `<session-id>`，傳遞裸 ID，例如 `session_...` 或 `cse_...`，或工作階段的 `claude.ai/code/<id>` URL，帶或不帶方案或查詢字串。在 claude.ai/code 的工作階段清單中找到 ID。 `--cloud` 需要 Anthropic 帳戶。當 Claude Code 配置為 Amazon Bedrock、Google Cloud 的 Agent Platform 或其他第三方提供者時，它不可用。僅通過 `ANTHROPIC_BASE_URL` 配置的 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)不算作第三方提供者進行此檢查，但您仍然需要使用 `claude auth login` 登入。您的組織的 `allow_remote_sessions` 政策也必須啟用。擁有者可以在 claude.ai/admin-settings/claude-code 的 Claude Code 管理設定中開啟它。

#### 輸出和錯誤

成功時，命令會列印工作階段 ID 和檢視工作階段的連結：

```
Sent to cloud session.
Session ID: session_01DiUkqY2kzbUbDmW1w96rfi
View: https://claude.ai/code/session_01DiUkqY2kzbUbDmW1w96rfi?from=cli&m=0

```

傳遞 `--output-format json` 以獲得機器可讀的結果：成功時為 `{ok, session_id, url}`，或當發送失敗時為 `{ok: false, session_id, error}`，例如當工作階段遺失或已封存時。配置錯誤（例如不支援的提供者或禁用的組織政策）會列印到 stderr，不使用 JSON。`--output-format stream-json` 不支援 `--cloud <session-id>`。 CLI 會在錯誤前加上 `Error: `。失敗的傳遞會包裝為 `failed to send message to cloud session <id>: <reason>`。

| 訊息                                                                                                                        | 它的意思                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Cloud sessions aren't available with <provider>. They run on Anthropic's infrastructure and require an Anthropic account.` | Claude Code 配置為第三方提供者。訊息會使用您的配置使用的標籤命名提供者，例如 `Amazon Bedrock` 或 `Google Vertex AI`。移除該提供者的配置，例如通過取消設定 `CLAUDE_CODE_USE_BEDROCK`，並使用 Anthropic 帳戶登入（`claude auth login`）。 |
| `Cloud sessions are disabled by your organization's policy. Contact your organization admin to enable them.`                | `allow_remote_sessions` 組織政策已關閉。                                                                                                                                                                                                |
| `Couldn't verify your organization's policy for cloud sessions. Check your network connection and try again.`               | Claude Code 無法取得您的組織政策，因此它拒絕發送，而不是假設雲端工作階段被允許。檢查您的網路連接並重試。                                                                                                                                |
| `Attaching to an existing cloud session is not enabled for your account.`                                                   | 您執行了 `--cloud <session-id>` 而沒有 `-p`。使用 `claude -p "your message" --cloud <session-id>` 發送訊息。                                                                                                                            |
| `Session not found: <id>`                                                                                                   | ID 或 URL 不符合您可以存取的工作階段。根據工作階段的 claude.ai/code URL 檢查它。                                                                                                                                                        |
| `cloud session <id> is archived and cannot accept new messages`                                                             | 工作階段已被封存。改為啟動新工作階段。                                                                                                                                                                                                  |

### 從雲端到終端

使用以下任何方式將雲端工作階段拉入終端：

- **使用`--teleport`** ：從命令列，執行 `claude --teleport` 以進行互動式工作階段選擇器，或執行 `claude --teleport <session-id>` 以直接恢復特定工作階段。如果您有未提交的變更，系統會提示您先隱藏它們。
- **使用`/teleport`** ：在現有 CLI 工作階段內，執行 `/teleport` 或 `/tp` 以開啟相同的工作階段選擇器，而無需重新啟動 Claude Code。
- **從`/tasks`** ：執行 `/tasks` 以查看您的背景工作階段，然後按 `t` 傳送到其中一個。
- **從 claude.ai/code** ：從工作階段功能表選擇**在終端中開啟** 以複製可貼到終端的命令。
- **從雲端工作階段內** ：輸入 `/teleport`，Claude Code 會回覆該工作階段的確切 `claude --teleport <session-id>` 命令，準備好從儲存庫的簽出執行。需要工作階段環境中的 Claude Code v2.1.223 或更新版本。

當您傳送工作階段時，Claude 驗證您在正確的儲存庫中，從雲端工作階段取得並簽出分支，並將完整的對話歷史記錄載入到終端。終端會取得工作階段的自己的副本：那裡的新工作保持本機，不會出現在 claude.ai 上的雲端工作階段或 Claude 行動應用程式中。若要在傳送後繼續從您的電話引導，請在本機工作階段中啟動 [`/remote-control`](https://code.claude.com/docs/zh-TW/remote-control)。 `--teleport` 與 `--resume` 不同。`--resume` 從此機器的本機歷史記錄重新開啟對話，不列出雲端工作階段；`--teleport` 拉取雲端工作階段及其分支。

#### 傳送要求

傳送在恢復工作階段之前檢查這些要求。如果任何要求未滿足，您會看到錯誤或被提示解決問題。

| 要求            | 詳細資訊                                                                                                                                                                                                                                                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 乾淨的 git 狀態 | 您的工作目錄必須沒有未提交的變更。如果需要，傳送會提示您隱藏變更。                                                                                                                                                                                                                                                                   |
| 正確的儲存庫    | 您必須從同一儲存庫的簽出執行 `--teleport`，而不是從 fork。如果您從不同儲存庫的簽出執行它，Claude Code 會顯示一個錯誤，命名工作階段的儲存庫和您的簽出。如果 Claude Code 無法將您的遠端解析為主機名稱，例如 SSH 主機別名（如 `git@work:owner/repo.git`），它會要求您確認，並在遠端的擁有者和儲存庫名稱符合工作階段的儲存庫時接受簽出。 |
| 分支可用        | 雲端工作階段中的分支必須已推送到遠端。傳送會自動取得並簽出它。                                                                                                                                                                                                                                                                       |
| 相同帳戶        | 您必須驗證到雲端工作階段中使用的相同 claude.ai 帳戶。                                                                                                                                                                                                                                                                                |

#### `--teleport` 不可用

傳送需要 claude.ai 訂閱驗證。如果您通過 API 金鑰進行驗證，請執行 `/login` 以改為使用您的 claude.ai 帳戶登入。如果錯誤命名您的提供者，雲端工作階段無法通過第三方提供者使用；請參閱[錯誤表](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#output-and-errors)。如果您已通過 claude.ai 登入且 `--teleport` 仍不可用，您的組織可能已禁用雲端工作階段。

## 使用工作階段

工作階段出現在 claude.ai/code 的側邊欄中。從那裡，您可以檢查變更、與隊友共享、封存完成的工作或永久刪除工作階段。

### 取回已排隊的訊息

如果您在 Claude 工作時發送訊息，該訊息會排隊，直到 Claude 讀取它。若要取回已排隊的訊息，請點擊它上面的 ✕。文字會返回到訊息框，以便您可以編輯它或發送其他內容。 如果 Claude 已經讀取訊息，它會保留在對話中。

### 管理上下文

雲端工作階段支援產生文字輸出的[內建命令](https://code.claude.com/docs/zh-TW/commands)。只在終端介面中執行的命令，例如 `/plugin` 或 `/resume`，無法使用。在雲端工作階段中開啟選擇器或面板的命令行為不同：

- **`/model`、`/effort` 、`/color` 和 `/rename`**：將值作為引數傳遞，例如 `/model sonnet`，而不是開啟終端選擇器或滑塊。引數形式需要工作階段環境中的 Claude Code v2.1.205 或更新版本，並遵循每個命令的[可用性說明](https://code.claude.com/docs/zh-TW/commands#all-commands)：`/effort` 會報告 `Not applied`，而模型的[啟動預設努力保持](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)生效時。
- **`/fast`**：當快速模式在[您的帳戶上可用](https://code.claude.com/docs/zh-TW/fast-mode#requirements)時，為工作階段切換[快速模式](https://code.claude.com/docs/zh-TW/fast-mode#use-fast-mode-in-cloud-sessions)。需要工作階段環境中的 Claude Code v2.1.271 或更新版本。
- **`/config`**：在您的瀏覽器上的 claude.ai/code，開啟您設定的 Claude Code 部分，而不是設定值，命令後的文字（包括`key=value` ）會被忽略。若要變更雲端工作階段的設定，請設定環境上的[環境變數](https://code.claude.com/docs/zh-TW/cloud-environments#set-environment-variables)，或在具有一個儲存庫的工作階段中，將金鑰提交到該儲存庫的 `.claude/settings.json`。[雲端工作階段中的設定](https://code.claude.com/docs/zh-TW/settings#settings-in-cloud-sessions)列出每個工作階段讀取的內容。

對於上下文管理特別：

| 命令                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 在雲端工作階段中有效 | 備註                                                                         |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------- |
| `/compact`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 是                   | 總結對話以釋放上下文。接受可選的焦點指示，如 `/compact keep the test output` |
| `/context`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 是                   | 顯示目前在上下文視窗中的內容                                                 |
| `/clear`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 否                   | 改為從側邊欄啟動新工作階段                                                   |
| 自動壓縮在上下文視窗接近容量時自動執行。雲端工作階段自行設定 [`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`](https://code.claude.com/docs/zh-TW/env-vars)，因此壓縮會在[自動壓縮視窗](https://code.claude.com/docs/zh-TW/model-config#set-the-auto-compact-window)的中途觸發，而不是在視窗填滿時。該值會覆蓋您在[環境變數](https://code.claude.com/docs/zh-TW/cloud-environments#set-environment-variables)中新增的值，因此在那裡新增變數不會變更壓縮觸發的時間。 若要改為變更自動壓縮視窗，請在您的環境變數中設定 [`CLAUDE_CODE_AUTO_COMPACT_WINDOW`](https://code.claude.com/docs/zh-TW/env-vars)，或在未設定變數的工作階段中執行 [`/autocompact`](https://code.claude.com/docs/zh-TW/commands#all-commands)，搭配令牌計數。 [Subagents](https://code.claude.com/docs/zh-TW/sub-agents) 的運作方式與本機相同。Claude 可以使用 Agent 工具生成它們，以將研究或並行工作卸載到單獨的上下文視窗中，保持主對話更輕。在您的儲存庫的 `.claude/agents/` 中定義的 Subagents 會自動選擇。 [Agent teams](https://code.claude.com/docs/zh-TW/agent-teams) 預設關閉，但可以通過將 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 新增到您的[環境變數](https://code.claude.com/docs/zh-TW/cloud-environments#set-environment-variables)來啟用。 |                      |                                                                              |

### 雲端工作階段中的權限模式

您可以從[模式下拉式功能表](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)選擇雲端工作階段的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)，無論是在您建立任務時還是在工作階段執行時。當您重新開啟其 Anthropic 託管[環境已過期](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#environment-expired)的工作階段，或向工作階段發送訊息時，該工作階段的自託管執行器[在閒置時釋放](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#runner-cli-flags)，Claude Code 會在它所在的權限模式中恢復工作階段。

### 檢查變更

每個工作階段顯示一個差異指示器，其中包含新增和移除的行數，例如 `+42 -18`。選擇它以開啟差異檢視、在特定行上留下內聯評論，並使用您的下一條訊息將它們發送給 Claude。 Claude Code 從原始 git blob 內容計算這些差異，包括 Claude 編輯時顯示的每個檔案差異，因此儲存庫中配置的差異驅動器和 `textconv` 篩選器不適用。對於不是工作階段自己簽出之一的儲存庫中的檔案，例如在工作階段期間在工作區內複製的檔案，每個檔案差異會顯示 Claude 的編輯本身，而不是 git 比較。 請參閱[檢查和迭代](https://code.claude.com/docs/zh-TW/web-quickstart#review-and-iterate)以了解完整逐步說明，包括 PR 建立。若要讓 Claude 自動監控 PR 以查找 CI 失敗和審查評論，請參閱[自動修復拉取請求](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)。

### 共享工作階段

若要共享工作階段，請根據下面的帳戶類型切換其可見性。之後，按原樣共享工作階段連結。收件者在開啟連結時看到最新狀態，但他們的檢視不會即時更新。

#### 從 Enterprise 或 Team 帳戶共享

對於 Enterprise 和 Team 帳戶，兩個可見性選項是**私人** 和**Team** 。Team 可見性使工作階段對您的 claude.ai 組織的其他成員可見。[Slack 中的 Claude](https://code.claude.com/docs/zh-TW/slack)工作階段會自動以 Team 可見性共享。 儲存庫存取驗證預設啟用，基於連接到收件者帳戶的 GitHub 帳戶。您帳戶的顯示名稱對所有有存取權限的收件者可見。

#### 從 Max 或 Pro 帳戶共享

對於 Max 和 Pro 帳戶，兩個可見性選項是**私人** 和**公開** 。公開可見性使工作階段對任何登入 claude.ai 的使用者可見。 在共享之前檢查您的工作階段是否包含敏感內容。工作階段可能包含來自私人 GitHub 儲存庫的程式碼和認證。儲存庫存取驗證預設未啟用。 若要要求收件者具有儲存庫存取權限，或從共享工作階段中隱藏您的名稱，請前往 [**設定 > Claude Code > 共享設定**](https://claude.ai/settings/claude-code)。

### 封存工作階段

您可以封存工作階段以保持工作階段清單的組織。封存的工作階段隱藏在預設工作階段清單中，但可以通過篩選封存的工作階段來檢視。 若要封存工作階段，請在側邊欄中將滑鼠懸停在工作階段上，然後選擇封存圖示。

### 刪除工作階段

刪除工作階段會永久移除工作階段及其資料。此操作無法撤銷。您可以通過兩種方式刪除工作階段：

- **從側邊欄** ：篩選封存的工作階段，然後將滑鼠懸停在您要刪除的工作階段上，並選擇刪除圖示
- **從工作階段功能表** ：開啟工作階段，選擇工作階段標題旁的下拉式功能表，然後選擇**刪除**

在刪除工作階段之前，系統會要求您確認。

## 自動修復拉取請求

Claude 可以監視拉取請求並自動回應 CI 失敗和審查評論。Claude 訂閱 PR 上的 GitHub 活動，當檢查失敗或審查者留下評論時，Claude 會調查並推送修復（如果有明確的修復）。 自動修復需要在您的儲存庫上安裝 Claude GitHub App。如果您還沒有，請從 [GitHub App 頁面](https://github.com/apps/claude)安裝它。 根據 PR 來自何處以及您使用的設備，有幾種方式可以開啟自動修復：

- **在 Claude Code 網頁版中建立的 PR** ：開啟工作階段於 claude.ai/code，開啟 CI 狀態欄，並選擇**自動修復**
- **從您的終端** ：在 PR 的分支上執行 [`/autofix-pr`](https://code.claude.com/docs/zh-TW/commands)。Claude Code 使用 `gh` 偵測開啟的 PR，生成網頁工作階段，並在一個步驟中開啟自動修復
- **從行動應用程式** ：告訴 Claude 自動修復 PR，例如「監視此 PR 並修復任何 CI 失敗或審查評論」
- **任何現有 PR** ：將 PR URL 貼到工作階段中並告訴 Claude 自動修復它

自動修復是每個 PR 的切換開關。若要停止監視，請在 claude.ai/code 的工作階段中開啟 CI 狀態欄並清除**自動修復** 切換，或告訴 Claude 停止監視 PR。

### Claude 如何回應 PR 活動

當自動修復處於活動狀態時，Claude 會收到 PR 的 GitHub 事件，包括新的審查評論和 CI 檢查失敗。對於每個事件，Claude 會調查並決定如何進行：

- **明確的修復** ：如果 Claude 對修復有信心且不與早期指示衝突，Claude 會進行變更、推送它，並在工作階段中解釋所做的工作
- **模糊的請求** ：如果審查者的評論可以以多種方式解釋或涉及架構上重要的內容，Claude 會在採取行動前詢問您
- **重複或無操作事件** ：如果事件是重複的或不需要變更，Claude 會在工作階段中記錄它並繼續

GitHub 不會在基礎分支推進並建立合併衝突時發出 webhook，因此自動修復無法自行對衝突做出反應。若要解決衝突，請開啟工作階段並要求 Claude 進行變基。 Claude 可能會在 GitHub 上回覆審查評論執行緒作為解決它們的一部分。這些回覆使用您的 GitHub 帳戶發佈，因此它們會出現在您的使用者名稱下，但每個回覆都標記為來自 Claude Code，以便審查者知道它是由代理編寫的，而不是由您直接編寫的。 如果您的儲存庫使用評論觸發的自動化，例如 Atlantis、Terraform Cloud 或在 `issue_comment` 事件上執行的自訂 GitHub Actions，請注意 Claude 可以代表您回覆，這可能會觸發這些工作流程。在啟用自動修復之前檢查您的儲存庫自動化，並考慮為 PR 評論可以部署基礎設施或執行特權操作的儲存庫禁用自動修復。

## 安全性和隔離

每個雲端工作階段通過多個層與您的機器和其他工作階段分離：

- **隔離的虛擬機器** ：每個工作階段在隔離的 Anthropic 管理的 VM 中執行。您的組織路由到[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)的工作階段改為在您自己的基礎設施上執行，其中隔離是您的部署的責任
- **網路存取控制** ：在 Anthropic 託管的環境中，網路存取預設受限，可以禁用。請參閱[網路存取](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)以了解存取層級、[預設允許的網域](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)，以及不通過允許清單的流量。在自託管環境中，您在自己的網路邊界限制工作階段出口。當以禁用的網路存取執行時，Claude Code 仍然可以與 Anthropic API 通訊，這可能允許資料離開 VM。
- **認證保護** ：在 Anthropic 託管的環境中，git 認證和簽署金鑰保持在沙箱外，代理使用限定認證代表工作階段進行驗證。在自託管環境中，您的部署提供 git 認證；請參閱[配置 git](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git)
- **API 認證** ：在 Pro 和 Max 計畫的 Anthropic 託管環境中，您[新增到雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)的金鑰保持在沙箱外，以相同的方式附加到匹配的請求，在它們離開工作階段後。自託管環境沒有 API 認證，Team 和 Enterprise 計畫還沒有
- **安全分析** ：程式碼在隔離的工作階段環境內進行分析和修改，然後建立 PR

## 故障排除

對於出現在對話中的執行時 API 錯誤，例如 `API Error: 500`、`529 Overloaded`、`429` 或 `Prompt is too long`，請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors)。這些錯誤及其修復與 CLI 和 Desktop 應用程式共享。下面的部分涵蓋特定於雲端工作階段的問題。

### 工作階段建立失敗

如果新工作階段無法啟動，出現 `Session creation failed` 或在佈建時停滯，Claude Code 無法為工作階段分配 VM。

- 檢查 [status.claude.com](https://status.claude.com) 以查找雲端工作階段事件
- 一分鐘後重試，因為容量是按需佈建的
- 確認您的 GitHub 連線可以到達儲存庫，請遵循[連接 GitHub 後沒有儲存庫出現](https://code.claude.com/docs/zh-TW/web-quickstart#no-repositories-appear-after-connecting-github)

### 無法取得組織 UUID

`claude --cloud` 和 `claude --teleport` 需要使用 claude.ai 帳戶登入。如果您使用 API 金鑰進行驗證，或您的儲存帳戶詳細資訊已過期，這些命令會失敗，出現 `Unable to get organization UUID` 或訊息表示 API 金鑰驗證不足。使用 API 金鑰驗證或過期的帳戶詳細資訊，執行 `claude --teleport` 而不使用工作階段 ID 會在工作階段選擇器中顯示 `Error loading Claude Code sessions`，而不是任一訊息，相同的修復適用。 執行 `/login` 以使用您的 claude.ai 帳戶登入，然後重試命令。如果錯誤命名您的提供者，請參閱[錯誤表](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#output-and-errors)：雲端工作階段無法通過第三方提供者使用。

### 遠端控制工作階段已過期或存取被拒絕

`--teleport` 通過與雲端工作階段使用的相同遠端控制工作階段基礎設施連接，因此驗證和工作階段過期錯誤會以遠端控制措辭出現。您可能會看到 `Remote Control session expired` 或 `Access denied`。連接令牌是短期的，並限定於您的帳戶。

- 在本機執行 `/login` 以刷新您的認證，然後重新連接
- 確認您登入到擁有工作階段的相同帳戶
- 如果您看到 `Remote Control may not be available for this organization`，擁有者尚未為您的組織啟用雲端工作階段

### 環境已過期

雲端工作階段在不活動一段時間後停止，工作階段的 VM 被回收。工作階段在等待您批准 [MCP 連接器](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)工具呼叫或登入 MCP 伺服器時計為不活動，並且可以在該等待期間過期。 從 [claude.ai/code](https://claude.ai/code) 重新開啟工作階段以佈建新 VM，並恢復您的對話歷史記錄。在 VM 被回收時仍在執行的背景工作，例如 subagents 和 shell 命令，不會被恢復。

## 限制

在依賴雲端工作階段進行工作流程之前，請考慮這些限制：

- **速率限制** ：雲端工作階段與您帳戶內所有其他 Claude 和 Claude Code 使用共享速率限制。並行執行多個任務會按比例消耗更多速率限制。雲端 VM 沒有單獨的計算費用。
- **儲存庫驗證** ：您只能在驗證到相同帳戶時將雲端工作階段拉入您的終端機
- **平台限制** ：儲存庫複製和拉取請求建立需要 GitHub。自託管 [GitHub Enterprise Server](https://code.claude.com/docs/zh-TW/github-enterprise-server) 執行個體支援 Team 和 Enterprise 計畫。您可以透過設定 `CCR_FORCE_BUNDLE=1`，將 GitLab、Bitbucket 或其他非 GitHub 儲存庫作為[本機捆綁](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-local-repositories-without-github)發送到雲端工作階段，但工作階段無法將結果推送回該遠端
- **組織 IP 允許清單** ：雲端工作階段從 Anthropic 管理的基礎設施而不是您的網路呼叫 Anthropic API，而[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)中的工作階段從您自己的網路呼叫它。如果您的組織啟用了 [IP 允許清單](https://support.claude.com/en/articles/13200993-restrict-access-to-claude-with-ip-allowlisting)，每個 Anthropic 託管的雲端工作階段都會失敗，出現驗證錯誤。這同樣適用於[程式碼審查](https://code.claude.com/docs/zh-TW/code-review)和[例行工作](https://code.claude.com/docs/zh-TW/routines)，在 Anthropic 託管的環境中執行；路由到自託管環境的例行工作從您自己的網路呼叫 API。聯絡 [Anthropic 支援](https://support.claude.com/)以從您的組織的 IP 允許清單中豁免 Anthropic 託管的服務。

## 相關資源

- [雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)：為雲端工作階段配置網路存取、環境變數和設定指令碼
- [專案](https://code.claude.com/docs/zh-TW/claude-projects)：一個對話，Claude 在其中協調您存放庫上的平行雲端工作階段並回報結果
- [Ultrareview](https://code.claude.com/docs/zh-TW/ultrareview)：在雲端沙箱中執行深度多代理程式碼審查
- [例行工作](https://code.claude.com/docs/zh-TW/routines)：自動化按排程、通過 API 呼叫或回應 GitHub 事件的工作
- [Hooks 配置](https://code.claude.com/docs/zh-TW/hooks)：在工作階段生命週期事件執行指令碼
- [所有設定](https://code.claude.com/docs/zh-TW/settings-reference)：所有配置選項
- [安全性](https://code.claude.com/docs/zh-TW/security)：隔離保證和資料處理
- [資料使用](https://code.claude.com/docs/zh-TW/data-usage)：Anthropic 從雲端工作階段保留的內容
- [Claude Tag](https://claude.com/docs/claude-tag/overview)：在 Slack 中由組織管理的 @Claude，在相同的雲端基礎設施上執行

是否 助手
