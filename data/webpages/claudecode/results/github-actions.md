[Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action) 是一個 GitHub Action，在您的儲存庫工作流程中執行 Claude Code。在 pull request 或議題評論中提及 `@claude`，讓 Claude 分析程式碼、實現變更並推送提交。您也可以給 Claude Code GitHub Action 一個提示，在任何 GitHub 事件上自動執行。使用它將議題轉換為 pull request、從評論修復錯誤，或自動化重複性任務。 有多個產品共享 Claude Code 名稱。本頁涵蓋 `claude-code-action` 工作流程整合，您可以使用儲存庫中的工作流程檔案進行設定。如需相關產品，請參閱：

- [Code Review](https://code.claude.com/docs/zh-TW/code-review)：在每個 pull request 上自動審查，無需編寫工作流程
- [Claude Code in the cloud](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：在雲端基礎設施上執行的 Claude Code 工作階段，而不是在您的機器上
- [Claude Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview)：GitHub Actions 外的自訂自動化。Claude Code GitHub Action 建立在 SDK 之上
- [GitHub Enterprise Server](https://code.claude.com/docs/zh-TW/github-enterprise-server)：具有自託管 GitHub 的 Claude Code

## 設定

您可以透過以下兩種方式之一設定 Claude Code GitHub Action：

- **快速設定** ：從 Claude Code 執行 `/install-github-app`。Claude Code 安裝 GitHub App、新增您的身份驗證密鑰，並為您準備工作流程 pull request
- **手動設定** ：安裝應用程式、新增密鑰，並自己將工作流程檔案複製到您的儲存庫。當您不在本地執行 Claude Code、命令失敗或您想完全控制工作流程檔案時，請使用此路徑

對於任一路徑，您需要對儲存庫具有管理員存取權限。

### 快速設定

`/install-github-app` 僅適用於 github.com 儲存庫。如果您的儲存庫的 git 遠端在 gitlab.com 或 bitbucket.org 上，該命令會列印通知並退出，而不是開始設定。若要從 GitLab 管道執行 Claude Code，請參閱 [Claude Code GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd)。 在開始之前，安裝 [GitHub CLI](https://cli.github.com) 並使用 `gh auth login` 進行身份驗證。Claude Code 會檢查它並在缺少時警告您。 在您想要連接的儲存庫中開啟 `claude`，執行 `/install-github-app`，並按照提示進行。Claude Code 安裝 Claude GitHub App，然後為工作流程設定身份驗證密鑰：

- 如果 Claude Code 已經有 API 金鑰，它會重複使用該金鑰，並提供保留儲存庫現有 `ANTHROPIC_API_KEY` 密鑰的選項（如果已設定）
- 否則，選擇使用您的 Claude 訂閱建立長期令牌或貼上 API 金鑰

Claude Code 將認證儲存為儲存庫密鑰，API 金鑰命名為 `ANTHROPIC_API_KEY`，或訂閱令牌命名為 `CLAUDE_CODE_OAUTH_TOKEN`。 Claude Code 然後推送包含您選擇的工作流程檔案的分支，已設定為使用該密鑰，並在您的瀏覽器中開啟 GitHub，準備建立 pull request。建立並合併該 pull request，`@claude` 就可以在儲存庫中工作。 如果您選擇審查工作流程，Claude 會在 pull request 本身上發佈每個審查，作為它發現的每個問題的內聯評論，或在未發現任何問題時作為一個摘要評論。Claude 會跳過某些 pull request，例如草稿。[審查工作流程範例](https://code.claude.com/docs/zh-TW/github-actions#run-a-skill)使用相同的技能並列出它們。在 v2.1.229 之前，Claude 只將其審查寫入工作流程執行日誌。 若要更新較早版本生成的審查工作流程，請執行以下操作之一：

- 再次執行 `/install-github-app`。當儲存庫已經有 `claude.yml` 時，選擇**使用最新版本更新工作流程檔案** 。Claude Code 將新的工作流程檔案副本推送到新分支並開啟 pull request，與首次安裝相同。
- 自己將 `--comment` 引數和 [審查工作流程範例](https://code.claude.com/docs/zh-TW/github-actions#run-a-skill)中的 `claude_args` 行新增到簽入的檔案，這會保留您對其所做的任何其他編輯。

安裝 GitHub App 後，Claude Code 會詢問是否繼續進行 GitHub Actions 設定。選擇**暫時跳過** 以僅安裝 GitHub App。稍後再次執行 `/install-github-app` 以完成工作流程和密鑰步驟。在 v2.1.187 之前，Claude Code 直接進行工作流程選擇。

- 安裝 GitHub App 時，您授予它多個權限。有關完整集合，請參閱 [GitHub App 權限](https://code.claude.com/docs/zh-TW/github-actions#github-app-permissions)
- 快速設定適用於 Claude API 和 Claude 訂閱。如果您使用 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry，請參閱[使用 Claude Code GitHub Actions 與雲端提供者](https://code.claude.com/docs/zh-TW/github-actions-cloud-providers)

### 手動設定

若要在不執行 `/install-github-app` 的情況下設定 Claude Code GitHub Action，請安裝應用程式、新增密鑰並自己複製工作流程檔案： 1 安裝 Claude GitHub App 將 [Claude GitHub App](https://github.com/apps/claude) 安裝到您的儲存庫。Claude Code GitHub Action 依賴應用程式的三個權限：

- **Contents** ：讀取和寫入，以便 Claude 可以修改儲存庫檔案
- **Issues** ：讀取和寫入，以便 Claude 可以回應議題
- **Pull requests** ：讀取和寫入，以便 Claude 可以建立 PR 並推送變更

在安裝期間，您也授予其他 Claude 功能使用的權限。有關完整集合，請參閱 [GitHub App 權限](https://code.claude.com/docs/zh-TW/github-actions#github-app-permissions)。 2 新增身份驗證密鑰 根據您的身份驗證方式，將以下密鑰之一新增到您的儲存庫。請參閱 GitHub 的[在 GitHub Actions 中使用密鑰](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)指南。

- `ANTHROPIC_API_KEY`：來自 [Claude Console](https://platform.claude.com) 的 Claude API 金鑰
- `CLAUDE_CODE_OAUTH_TOKEN`：使用您的 Claude 訂閱進行身份驗證的 OAuth 令牌，在 Pro、Max、Team 和 Enterprise 計劃上可用。透過在本地執行 `claude setup-token` 生成一個。請參閱[生成長期令牌](https://code.claude.com/docs/zh-TW/authentication#generate-a-long-lived-token)

在工作流程檔案中，將密鑰傳遞給匹配的輸入：API 金鑰為 `anthropic_api_key`，或 OAuth 令牌為 `claude_code_oauth_token`。 3 複製工作流程檔案 將 [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) 複製到您的儲存庫的 `.github/workflows/` 目錄。該檔案是一個工作流程，而不僅僅是一個範例。按照提交，Claude 在有人在議題或 pull request 中提及 `@claude` 時回應，使用 `ANTHROPIC_API_KEY` 密鑰進行身份驗證。如果您改為新增了 `CLAUDE_CODE_OAUTH_TOKEN`，請將工作流程的 `anthropic_api_key` 行變更為 `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`。 設定後，透過在議題或 PR 評論中標記 `@claude` 來測試 Claude Code GitHub Action。

### 為組織設定

使用快速設定或手動設定，您一次設定一個儲存庫。若要在整個組織中推出 Claude Code GitHub Action：

- 在組織級別安裝 [Claude GitHub App](https://github.com/apps/claude) 一次，選擇所有儲存庫或選定清單
- 將身份驗證密鑰儲存為組織級別的 Actions 密鑰，以便每個儲存庫不需要自己的副本
- 將工作流程檔案新增到應該執行 Claude Code GitHub Action 的每個儲存庫，或將工作定義一次作為[可重複使用的工作流程](https://docs.github.com/en/actions/using-workflows/reusing-workflows)，每個儲存庫都會呼叫

對於跨儲存庫共享的密鑰，使用來自 [Claude Console](https://platform.claude.com) 的 API 金鑰進行身份驗證，而不是 OAuth 令牌，因為 OAuth 令牌與執行 `claude setup-token` 的人的訂閱相關聯。 若要完全避免儲存長期密鑰，請透過工作負載身份聯盟進行身份驗證，其中 Claude Code GitHub Action 將工作流程的 GitHub OpenID Connect (OIDC) 令牌交換為透過 Claude Console 服務帳戶的 Claude API 存取。設定這些輸入：

- `anthropic_federation_rule_id`：聯盟規則 ID，`fdrl_...`
- `anthropic_organization_id`：您的 Anthropic 組織 ID
- `anthropic_service_account_id`：服務帳戶 ID，`svac_...`。可選，因為您在 Console 中建立的聯盟規則已經針對服務帳戶
- `anthropic_workspace_id`：工作區 ID，`wrkspc_...`。當聯盟規則針對單個工作區時可選

授予工作流程 `id-token: write` 權限，Claude Code GitHub Action 需要它進行聯盟交換，即使您傳遞自己的 `github_token`。有關 Console 端設定，請參閱 [Claude Code GitHub Action 的設定指南](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md)。 如需安全審查中的資料處理和保留問題，請參閱[資料使用](https://code.claude.com/docs/zh-TW/data-usage)和[安全性](https://code.claude.com/docs/zh-TW/security)。

### 解除安裝

若要移除 Claude Code GitHub Action，請撤銷適用於您的安裝的每個設定部分：

- **工作流程檔案** ：從 `.github/workflows/` 中刪除使用 `anthropics/claude-code-action` 的工作流程。如果您使用了快速設定，請查找 `claude.yml`，如果您選擇了審查工作流程，請查找 `claude-code-review.yml`。刪除工作流程後，Claude Code GitHub Action 不再執行
- **密鑰** ：從儲存庫中刪除 `ANTHROPIC_API_KEY` 或 `CLAUDE_CODE_OAUTH_TOKEN` 密鑰，以及從組織級別的 Actions 密鑰（如果您[跨儲存庫共享它](https://code.claude.com/docs/zh-TW/github-actions#set-up-for-an-organization)）。如果您刪除密鑰，它持有的認證保持有效。若要完全停用 API 金鑰，也請在 [Claude Console](https://platform.claude.com) 中刪除金鑰
- **GitHub App** ：在您的儲存庫或組織設定中的 GitHub Apps 下解除安裝 Claude GitHub App，但僅當您不將其用於另一個 Claude 功能（例如 Code Review 或 web 自動修復）時

如果您設定了[雲端提供者](https://code.claude.com/docs/zh-TW/github-actions-cloud-providers)，也請刪除提供者密鑰，例如 `AWS_ROLE_TO_ASSUME`、`GCP_*` 密鑰或 `AZURE_*` 密鑰，並解除安裝自訂 GitHub App 及其 `APP_ID` 和 `APP_PRIVATE_KEY` 密鑰。

### GitHub App 權限

[Claude GitHub App](https://github.com/apps/claude) 由與 GitHub 整合的每個 Claude 功能共享，包括 Claude Code GitHub Action、[Code Review](https://code.claude.com/docs/zh-TW/code-review) 和 [Claude Code on the web 上的自動修復](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)。GitHub App 有一個涵蓋其所有功能的單一權限集，因此該集包括 Claude Code GitHub Action 不使用的某些權限。 安裝應用程式時，您授予以下權限：

| 權限                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 存取       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Actions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 讀取和寫入 |
| Checks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 讀取和寫入 |
| Contents                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 讀取和寫入 |
| Discussions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 讀取和寫入 |
| Issues                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 讀取和寫入 |
| Members                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 讀取       |
| Metadata                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 讀取       |
| Pull requests                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 讀取和寫入 |
| Repository hooks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 讀取和寫入 |
| Statuses                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 讀取       |
| Workflows                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 讀取和寫入 |
| 權限集也可以在使用它的功能之前變更。當應用程式請求它之前沒有的權限時，GitHub 會提示帳戶擁有者批准它，組織安裝的組織擁有者，安裝保持其舊權限直到他們這樣做。例如，當 Actions 存取從讀取變更為寫入時，應用程式可以重新執行工作流程而不僅查看執行和日誌，因此 GitHub 要求擁有者批准變更。 安裝應用程式時，您接受其完整權限集。GitHub 不允許您接受子集。如果您的組織僅需要 Claude Code GitHub Action 使用的權限，請按照 [Claude Code GitHub Action 的設定指南](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md)建立具有 Contents、Issues 和 Pull requests 的自訂 GitHub App。自訂應用程式僅涵蓋 Claude Code GitHub Action。Code Review 和 web 自動修復仍需要官方應用程式。 有關 Claude Code GitHub Action 如何限制 Claude 對這些權限的操作的詳細資訊，請參閱[安全性文件](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)。 |            |

## 互動和自動化模式

Claude Code GitHub Action 從您的工作流程設定中偵測如何執行：

- **互動模式** ：當工作流程不提供 `prompt` 輸入時，Claude 等待觸發短語 `@claude`（預設），在議題或 pull request 評論、pull request 審查或新開啟議題的正文或標題中，然後回應該請求。進度和結果顯示為觸發議題或 PR 上的評論。
- **自動化模式** ：當工作流程提供 `prompt` 輸入時，Claude 執行而不等待提及，僅受[誰可以觸發執行](https://code.claude.com/docs/zh-TW/github-actions#who-can-trigger-runs)的檢查限制。預設情況下，結果顯示在工作流程執行日誌中，而不是評論。Claude 可以在提示指導它並且它有可以發佈的工具時發佈到議題或 pull request，如[程式碼審查範例](https://code.claude.com/docs/zh-TW/github-actions#run-a-skill)中所示。

### 誰可以觸發執行

在兩種模式中，Claude Code GitHub Action 在 Claude 開始之前對觸發執行者執行兩個檢查，當任一檢查拒絕它時執行失敗：

- **寫入存取** ：在議題和 pull request 事件上，觸發使用者必須對儲存庫具有寫入存取權限。若要允許沒有寫入存取權限的特定使用者，請設定 `allowed_non_write_users` 並傳遞您自己的 `github_token` 輸入。沒有使用者撰寫的事件（例如 `schedule` 觸發器）會跳過此檢查。
- **人類執行者** ：在每個事件上，Claude Code GitHub Action 拒絕機器人執行者，除非您在 `allowed_bots` 中列出它，這可以防止機器人在迴圈中觸發 Claude。此檢查也適用於排程執行，GitHub 將其歸因於儲存庫使用者，通常是最後變更工作流程 `cron` 排程的使用者。如果該使用者是機器人，請在 `allowed_bots` 中列出它。

## 範例使用案例

[examples 目錄](https://github.com/anthropics/claude-code-action/tree/main/examples)包含適用於不同情境的現成工作流程。 本頁上的範例顯示 API 金鑰身份驗證。如果您使用 Claude 訂閱進行身份驗證，請將任何範例中的 `anthropic_api_key` 行替換為 `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`。

### 回應 @claude 提及

此工作流程在互動模式下執行 Claude Code GitHub Action，因此每當有人在議題或 PR 評論中提及 `@claude` 時，Claude 都會回應。

```
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

```

此工作流程中不是樣板的部分：

- `id-token: write`：Claude Code GitHub Action 的預設 GitHub App 身份驗證所需
- `actions: read`：讓 Claude 讀取 PR 上的 CI 結果
- `actions/checkout`：給 Claude 儲存庫的本地副本以在其中工作
- `if`：防止執行器在不提及 `@claude` 的評論上啟動。Claude Code GitHub Action 也在回應之前檢查觸發短語本身

工作流程就位後，在任何議題或 PR 評論中提及 `@claude` 並提出請求：

```
@claude implement this feature based on the issue description
@claude how should I implement user authentication for this endpoint?
@claude fix the TypeError in the user dashboard component

```

Claude 在同一議題或 PR 上的評論中回應並在工作時更新它。

### 執行技能

`prompt` 輸入接受[技能](https://code.claude.com/docs/zh-TW/skills)調用以及純文字：

- 對於儲存庫的 `.claude/skills/` 目錄中的技能，在 `anthropics/claude-code-action` 步驟之前執行 `actions/checkout`，以便技能檔案在執行器上可用，然後將 `/skill-name` 作為 `prompt` 傳遞。
- 對於打包在[外掛程式](https://code.claude.com/docs/zh-TW/plugins)中的技能，使用 `plugin_marketplaces` 和 `plugins` 輸入安裝外掛程式，然後將命名空間 `/plugin-name:skill-name` 作為 `prompt` 傳遞。`plugins` 輸入採用 `plugin-name@marketplace-name`，其中市場名稱來自市場自己的清單，而不是其儲存庫 URL。

以下工作流程安裝 `code-review` 外掛程式，並在 pull request 開啟、更新、重新開啟或標記為準備審查時執行其技能。它執行與快速設定中的審查工作流程相同的外掛程式。當您想控制提示、模型和觸發器本身時，使用這樣的工作流程。如需自動審查而無需維護工作流程檔案，請參閱 [Code Review](https://code.claude.com/docs/zh-TW/code-review)。在公開儲存庫上，GitHub 從 fork pull request 觸發的執行中扣留密鑰，因此審查僅在來自同一儲存庫中分支的 pull request 上執行。

```
name: Code Review
on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          plugin_marketplaces: "https://github.com/anthropics/claude-code.git"
          plugins: "code-review@claude-code-plugins"
          prompt: "/code-review:code-review --comment ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
          claude_args: '--allowedTools "mcp__github_inline_comment__create_inline_comment"'

```

此工作流程中的兩行控制審查的去向：

- **`--comment`**：Claude 在 pull request 上發佈其審查，作為它發現的每個問題的內聯評論，或在未發現任何問題時作為一個摘要評論。沒有它，Claude 不發佈任何內容，您在工作流程執行日誌中讀取發現。
- **`claude_args`**：即使技能自己的`allowed-tools` frontmatter 命名相同的工具，也要保留此行，因為 Claude Code GitHub Action 僅在 `claude_args` 中的 `--allowedTools` 命名它時才啟動發佈內聯評論的 MCP 伺服器。

Claude 跳過草稿和已關閉的 pull request、它判斷不需要審查的 pull request（例如自動化或瑣碎的），以及已經有來自 Claude 的評論的 pull request。

### 按排程執行

使用 `prompt` 輸入，Claude Code GitHub Action 在任何 GitHub 事件上以自動化模式執行，包括 cron 排程。對於純文字提示，Claude 沒有 shell 或 GitHub API 存取，直到您授予提示需要的工具，使用 `claude_args` 中的 `--allowedTools` 或 `settings` 輸入中的 [`permissions.allow` 規則](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)。如果您改為調用技能，Claude 可以使用其 [`allowed-tools` frontmatter](https://code.claude.com/docs/zh-TW/skills#pre-approve-tools-for-a-skill) 授予的工具。GitHub 僅從預設分支執行排程工作流程，在公開儲存庫中，在 60 天無儲存庫活動後禁用排程。 此工作流程在每天 09:00 UTC 在工作流程執行日誌中生成報告。其 `claude_args` 行[傳遞 CLI 引數](https://code.claude.com/docs/zh-TW/github-actions#pass-cli-arguments)，選擇模型並允許兩個 GitHub MCP 工具。Claude 透過這些工具使用 GitHub API 讀取提交和議題，因此您可以省略簽出步驟：

```
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: read
      id-token: write
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: |
            --model claude-opus-4-8
            --allowedTools "mcp__github__list_commits,mcp__github__list_issues"

```

## 最佳實踐

### 在 CLAUDE.md 中定義專案標準

在您的儲存庫根目錄建立 `CLAUDE.md` 檔案，以定義程式碼風格指南、審查標準、專案特定規則和偏好的模式。Claude 在建立 PR 和回應請求時遵循這些指南。有關詳細資訊，請參閱[記憶體文件](https://code.claude.com/docs/zh-TW/memory)。

### 保護您的認證

永遠不要直接將 API 金鑰或 OAuth 令牌提交到您的儲存庫。始終將它們儲存為 GitHub Secrets 並在工作流程中參考它們，例如 `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`。 僅授予工作流程它需要的權限，並在合併前審查 Claude 的變更。 如需包括權限和身份驗證的全面安全指導，請參閱 [Claude Code Action 安全性文件](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)。

### 管理成本

每次執行消耗兩種資源：

- **GitHub Actions 分鐘** ：Claude Code GitHub Action 在 GitHub 託管的執行器上執行，這會消耗您的 GitHub Actions 分鐘。有關定價和分鐘限制，請參閱 [GitHub 的計費文件](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions)。
- **API 令牌** ：每次互動根據提示和回應的長度、任務複雜性和程式碼庫大小消耗令牌。有關目前令牌費率，請參閱 [Claude 的定價頁面](https://claude.com/platform/api)。如果您使用 OAuth 令牌進行身份驗證，執行會使用您的 Claude 訂閱，而不是 API 計費。

您可以透過給 Claude 更清晰的上下文並限制每次執行可以做多少工作來降低兩種成本：

- 編寫特定的 `@claude` 請求，以便 Claude 需要更少的輪次完成
- 使用議題範本提前提供上下文
- 保持您的 `CLAUDE.md` 簡潔，因為 Claude 在每次執行時讀取它
- 在 `claude_args` 中設定 `--max-turns` 以限制迭代
- 設定工作流程級別的逾時以避免失控的工作
- 使用 GitHub 的並行控制來限制平行執行

如需跨組織的使用情況追蹤，請參閱[分析儀表板](https://code.claude.com/docs/zh-TW/analytics)和[監控](https://code.claude.com/docs/zh-TW/monitoring-usage)。如需使用情況的測量和計費方式，請參閱[成本](https://code.claude.com/docs/zh-TW/costs)。

## 使用雲端提供者

預設情況下，Claude Code GitHub Action 使用您的 API 金鑰或 OAuth 令牌直接呼叫 Claude API。若要改為透過您自己的雲端帳戶路由推理，請設定您的提供者的輸入並按照[使用 Claude Code GitHub Actions 與雲端提供者](https://code.claude.com/docs/zh-TW/github-actions-cloud-providers)：

- **Amazon Bedrock** ：`use_bedrock: "true"`
- **Google Cloud 的 Agent Platform** ：`use_vertex: "true"`
- **Microsoft Foundry** ：`use_foundry: "true"`

使用所有三個提供者，您透過 OIDC 身份聯盟進行身份驗證，而不是 Claude API 金鑰，因此您不在儲存庫中儲存靜態雲端認證。

## 故障排除

### Claude 不回應 @claude 命令

- 驗證 GitHub App 是否安裝在儲存庫上
- 檢查儲存庫是否啟用了工作流程
- 確保您的 API 金鑰或 OAuth 令牌在儲存庫密鑰中設定
- 確認評論包含 `@claude` 作為完整單詞，而不是 `/claude` 或 `@claude-bot`
- 確認評論使用者對儲存庫具有寫入存取權限。有關例外，請參閱[誰可以觸發執行](https://code.claude.com/docs/zh-TW/github-actions#who-can-trigger-runs)

### CI 不在 Claude 的提交上執行

- GitHub 不在使用預設 `GITHUB_TOKEN` 進行的提交上觸發工作流程。如果您將 `github_token: ${{ secrets.GITHUB_TOKEN }}` 傳遞給 Claude Code GitHub Action，請移除它，以便它作為 Claude GitHub App 進行身份驗證，或改為傳遞自訂應用程式令牌
- 檢查您的 CI 工作流程的觸發器是否包括 Claude 的推送產生的事件，例如 `push` 或 `pull_request`

### 身份驗證錯誤

- 透過在本地使用 `claude` 測試 API 金鑰或 OAuth 令牌來確認它有效，然後再偵錯工作流程
- 對於 Bedrock、Agent Platform 和 Foundry，請參閱雲端提供者頁面的[故障排除部分](https://code.claude.com/docs/zh-TW/github-actions-cloud-providers#troubleshooting)

如需更多解決方案，請參閱 Claude Code GitHub Action 的 [FAQ](https://github.com/anthropics/claude-code-action/blob/main/docs/faq.md)。

## 進階設定

### Action 參數

這些是最常用的輸入。每個都對應於 `anthropics/claude-code-action` 步驟中的 `with:` 金鑰。

| 參數                                                                                                                                               | 描述                                                                                                                                                                                                    | 必需                                                                                                                                                                                                |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`                                                                                                                                           | Claude 的指令，作為純文字或[技能](https://code.claude.com/docs/zh-TW/skills)調用。省略時，Claude 改為回應[觸發短語](https://code.claude.com/docs/zh-TW/github-actions#interactive-and-automation-modes) | 否                                                                                                                                                                                                  |
| `claude_args`                                                                                                                                      | 傳遞給 Claude Code 的 CLI 引數                                                                                                                                                                          | 否                                                                                                                                                                                                  |
| `anthropic_api_key`                                                                                                                                | Claude API 金鑰                                                                                                                                                                                         | 對於 Claude API，除非您使用 `claude_code_oauth_token` 或[工作負載身份聯盟](https://code.claude.com/docs/zh-TW/github-actions#set-up-for-an-organization)。不用於 Bedrock、Agent Platform 或 Foundry |
| `claude_code_oauth_token`                                                                                                                          | 用於使用 Claude 訂閱進行身份驗證的 OAuth 令牌，使用 `claude setup-token` 生成                                                                                                                           | 否                                                                                                                                                                                                  |
| `github_token`                                                                                                                                     | 用於 GitHub 操作的令牌。省略時，Claude Code GitHub Action 作為 Claude GitHub App 進行身份驗證                                                                                                           | 否                                                                                                                                                                                                  |
| `plugin_marketplaces`                                                                                                                              | 以換行符分隔的外掛程式市場 Git URL 清單                                                                                                                                                                 | 否                                                                                                                                                                                                  |
| `plugins`                                                                                                                                          | 以換行符分隔的要在執行前安裝的外掛程式名稱清單                                                                                                                                                          | 否                                                                                                                                                                                                  |
| `settings`                                                                                                                                         | Claude Code 設定，作為 JSON 字串或設定 JSON 檔案的路徑                                                                                                                                                  | 否                                                                                                                                                                                                  |
| `trigger_phrase`                                                                                                                                   | Claude 回應的觸發短語。預設：`@claude`                                                                                                                                                                  | 否                                                                                                                                                                                                  |
| `use_bedrock`                                                                                                                                      | 使用 Amazon Bedrock 而不是 Claude API                                                                                                                                                                   | 否                                                                                                                                                                                                  |
| `use_vertex`                                                                                                                                       | 使用 Google Cloud 的 Agent Platform 而不是 Claude API                                                                                                                                                   | 否                                                                                                                                                                                                  |
| `use_foundry`                                                                                                                                      | 使用 Microsoft Foundry 而不是 Claude API                                                                                                                                                                | 否                                                                                                                                                                                                  |
| 如需完整輸入清單，請參閱 Claude Code GitHub Action 的[設定參考](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md#inputs)。 |                                                                                                                                                                                                         |                                                                                                                                                                                                     |

### 傳遞 CLI 引數

`claude_args` 參數接受任何 [Claude Code CLI 引數](https://code.claude.com/docs/zh-TW/cli-reference)：

```
claude_args: "--max-turns 5 --model claude-sonnet-5 --mcp-config /path/to/config.json"

```

常見引數：

- `--max-turns`：限制對話輪數
- `--model`：要使用的模型，例如 `claude-sonnet-5`。沒有此引數，Claude Code GitHub Action 使用 Claude Code [預設模型](https://code.claude.com/docs/zh-TW/model-config)
- `--mcp-config`：[MCP 設定](https://code.claude.com/docs/zh-TW/mcp)的路徑
- `--allowedTools`：允許的工具的逗號分隔清單。`--allowed-tools` 別名也可以使用
- `--debug`：啟用偵錯輸出

## 從 Beta 升級

如果您的工作流程仍然參考 `anthropics/claude-code-action@beta`，請將它們更新為 v1：

1. 在 `uses` 行中將 `@beta` 變更為 `@v1`
1. 移除 `mode` 輸入，因為 Claude Code GitHub Action 現在[自動偵測模式](https://code.claude.com/docs/zh-TW/github-actions#interactive-and-automation-modes)
1. 將 `direct_prompt` 替換為 `prompt`
1. 將 CLI 選項（例如 `max_turns` 和 `model`）移動到 `claude_args`。`custom_instructions` 沒有同名標誌，變成 `--append-system-prompt`

如需完整的輸入對應和前後範例，請參閱[遷移指南](https://github.com/anthropics/claude-code-action/blob/main/docs/migration-guide.md)。

## 接下來

- [使用 Claude Code GitHub Actions 與雲端提供者](https://code.claude.com/docs/zh-TW/github-actions-cloud-providers)：透過 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 路由推理
- [設定參考](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md#inputs)：完整的 action 輸入清單
- [Examples 目錄](https://github.com/anthropics/claude-code-action/tree/main/examples)：更多情境的現成工作流程
- [Code Review](https://code.claude.com/docs/zh-TW/code-review)：自動 pull request 審查，無需維護工作流程檔案

是否 助手
