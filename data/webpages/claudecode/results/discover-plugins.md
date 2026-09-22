外掛程式透過技能、代理、hooks 和 MCP servers 擴展 Claude Code。外掛程式市場是幫助您探索和安裝這些擴展的目錄，無需自己構建它們。 您也可以在 claude.ai 上啟用外掛程式，供自己或透過您的組織使用。Claude Code 會將這些外掛程式同步到您的工作階段中，無需市場安裝，如[從 claude.ai 同步的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)所述。 想要建立和分發您自己的市場？請參閱[建立和分發外掛程式市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)。

## 市場如何運作

市場是他人建立和共享的外掛程式目錄。使用市場是一個兩步流程： 1 新增市場 這會向 Claude Code 註冊目錄，以便您可以瀏覽可用內容。尚未安裝任何外掛程式。 2 安裝個別外掛程式 瀏覽目錄並安裝您想要的外掛程式。

## 官方 Anthropic 市場

Claude Code 在您第一次以互動方式啟動它時會自動新增官方 Anthropic 市場 (`claude-plugins-official`)。如果 Claude Code 無法新增它，例如因為您的網路阻止下載或[市場政策](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)阻止了之前的嘗試，請使用 `/plugin marketplace add anthropics/claude-plugins-official` 自行新增。 若要瀏覽可用內容，請執行 `/plugin` 並前往 **Discover** 標籤，或在 [claude.com/plugins](https://claude.com/plugins) 查看目錄。 若要從官方市場安裝外掛程式，請使用 `/plugin install <name>@claude-plugins-official`。例如，若要安裝 GitHub 整合：

```
/plugin install github@claude-plugins-official

```

`/plugin` 在終端 CLI 中開啟互動式面板。如果 Claude 回覆在此環境中無法使用 `/plugin`，請使用 Claude 桌面應用程式中的[外掛程式瀏覽器](https://code.claude.com/docs/zh-TW/desktop#install-plugins)，或在雲端工作階段的 `.claude/settings.json` 中的 [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 下宣告外掛程式。 如果安裝失敗，請符合 Claude Code 報告的訊息：

- `Marketplace "claude-plugins-official" not found`：使用 `/plugin marketplace add anthropics/claude-plugins-official` 新增市場，然後重試安裝。
- 外掛程式[在市場中找不到](https://code.claude.com/docs/zh-TW/discover-plugins#install-plugins)：檢查外掛程式名稱。

官方市場由 Anthropic 維護，包含由 Anthropic 自行決定。應用內提交表單會將外掛程式新增到[社群市場](https://code.claude.com/docs/zh-TW/discover-plugins#community-marketplace)，而不是官方市場。若要獨立分發外掛程式，請[建立您自己的市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)並與使用者共享。 官方市場包括多個外掛程式類別：

### 程式碼智能

程式碼智能外掛程式啟用 Claude Code 的內建 LSP 工具，使 Claude 能夠跳轉到定義、尋找參考資料，並在編輯後立即查看類型錯誤。這些外掛程式配置[語言伺服器協議](https://microsoft.github.io/language-server-protocol/)連接，這是為 VS Code 程式碼智能提供動力的相同技術。在[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)中，Claude Code 不會啟動外掛程式語言伺服器，因此 Claude 在那裡無法取得 LSP 工具。 在使用這些外掛程式之前，請從下表安裝語言伺服器二進位檔；外掛程式不會為您安裝它。如果您已經安裝了語言伺服器，當您開啟專案時，Claude 可能會提示您安裝相應的外掛程式。

| 語言                                                                                                                                                                                                        | 外掛程式            | 所需的二進位檔               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------- |
| C/C++                                                                                                                                                                                                       | `clangd-lsp`        | `clangd`                     |
| C#                                                                                                                                                                                                          | `csharp-lsp`        | `csharp-ls`                  |
| Go                                                                                                                                                                                                          | `gopls-lsp`         | `gopls`                      |
| Java                                                                                                                                                                                                        | `jdtls-lsp`         | `jdtls`                      |
| Kotlin                                                                                                                                                                                                      | `kotlin-lsp`        | `kotlin-language-server`     |
| Lua                                                                                                                                                                                                         | `lua-lsp`           | `lua-language-server`        |
| PHP                                                                                                                                                                                                         | `php-lsp`           | `intelephense`               |
| Python                                                                                                                                                                                                      | `pyright-lsp`       | `pyright-langserver`         |
| Rust                                                                                                                                                                                                        | `rust-analyzer-lsp` | `rust-analyzer`              |
| Swift                                                                                                                                                                                                       | `swift-lsp`         | `sourcekit-lsp`              |
| TypeScript                                                                                                                                                                                                  | `typescript-lsp`    | `typescript-language-server` |
| 您也可以[為其他語言建立您自己的 LSP 外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#lsp-servers)。                                                                                           |                     |                              |
| 如果在安裝外掛程式後在 `/plugin` Errors 標籤中看到 `Executable not found in $PATH`，請從[程式碼智能](https://code.claude.com/docs/zh-TW/discover-plugins#code-intelligence)表安裝該外掛程式所需的二進位檔。 |                     |                              |

#### Claude 從程式碼智能外掛程式獲得的功能

安裝程式碼智能外掛程式並且其語言伺服器二進位檔可用後，Claude 獲得兩項功能：

- **自動診斷** ：在 Claude 進行每次檔案編輯後，語言伺服器報告錯誤和警告，因此 Claude 看到類型錯誤、遺漏的匯入和語法問題，無需執行編譯器或 linter。如果 Claude 引入錯誤，它會注意到並在同一輪中修復它。
- **程式碼導航** ：Claude 可以使用語言伺服器跳轉到定義、尋找參考資料、懸停時取得類型資訊、列出符號、尋找實現和追蹤呼叫層次結構。這些操作為 Claude 提供比基於 grep 的搜尋更精確的導航，儘管可用性可能因語言和環境而異。

您不需要超出安裝外掛程式的任何配置來配置診斷。若要自行讀取它們，當 Claude Code 顯示指示器（例如 **Found 3 new diagnostic issues in 2 files** ）時，請按 **Ctrl+O** 。 如果您遇到問題，請參閱[程式碼智能故障排除](https://code.claude.com/docs/zh-TW/discover-plugins#code-intelligence-issues)。

### 外部整合

這些外掛程式捆綁預先配置的 [MCP servers](https://code.claude.com/docs/zh-TW/mcp)，以便您可以連接 Claude 到外部服務，無需手動設定：

- **原始碼控制** ：`github`、`gitlab`
- **專案管理** ：`atlassian`（Jira/Confluence）、`asana`、`linear`、`notion`
- **設計** ：`figma`
- **基礎設施** ：`vercel`、`firebase`、`supabase`
- **通訊** ：`slack`
- **監控** ：`sentry`

### 自動安全審查

`security-guidance` 外掛程式審查 Claude 進行的每項變更是否存在常見漏洞，並指示 Claude 在同一工作階段中修復發現的問題。請參閱[在 Claude 編寫程式碼時捕捉安全問題](https://code.claude.com/docs/zh-TW/security-guidance)以了解它檢查的內容以及如何新增專案特定的規則。

### 開發工作流程

為常見開發任務新增技能和代理的外掛程式：

- **commit-commands** ：Git 提交工作流程，包括提交、推送和 PR 建立
- **pr-review-toolkit** ：用於審查拉取請求的專門代理
- **agent-sdk-dev** ：使用 Claude Agent SDK 構建的工具
- **plugin-dev** ：建立您自己的外掛程式的工具組

### 輸出樣式

自訂 Claude 的回應方式：

- **explanatory-output-style** ：關於實現選擇的教育見解
- **learning-output-style** ：用於技能建立的互動式學習模式

## 社群市場

位於 [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) 的社群市場託管已通過 Anthropic 自動驗證和安全篩選的第三方外掛程式。每個外掛程式都固定到目錄中的特定提交 SHA。與官方市場不同，您需要手動新增它：

```
/plugin marketplace add anthropics/claude-plugins-community

```

然後使用 `claude-community` 市場名稱從中安裝外掛程式：

```
/plugin install <plugin-name>@claude-community

```

若要將您自己的外掛程式提交到社群市場，請參閱建立外掛程式指南中的[將您的外掛程式提交到社群市場](https://code.claude.com/docs/zh-TW/plugins#submit-your-plugin-to-the-community-marketplace)。

## 試試看：新增演示市場

Anthropic 也維護一個[演示外掛程式市場](https://github.com/anthropics/claude-code/tree/main/plugins)（`claude-code-plugins`），其中包含展示外掛程式系統可能性的範例外掛程式。與官方市場不同，您需要手動新增此市場。 1 新增市場 在 Claude Code 中，為 `anthropics/claude-code` 市場執行 `plugin marketplace add` 命令：

```
/plugin marketplace add anthropics/claude-code

```

這會下載市場目錄並使其外掛程式可供您使用。 2 瀏覽可用外掛程式 執行 `/plugin` 以開啟外掛程式管理器。這會開啟一個標籤式介面，您可以使用 **Tab** 或 **Shift+Tab** 向後循環瀏覽：

- **Discover** ：從所有市場瀏覽可用外掛程式
- **Installed** ：檢視和管理已安裝的外掛程式
- **Marketplaces** ：新增、移除或更新已新增的市場
- **Errors** ：檢視任何外掛程式載入錯誤
- **Stats** ：查看[您每個 skills 在內容中的成本以及使用頻率](https://code.claude.com/docs/zh-TW/skills#find-unused-skills)，在有 `/skill-doctor` 可用的工作階段中

前往 **Discover** 標籤以查看您剛新增的市場中的外掛程式。當您的管理員已透過 [`pluginSuggestionMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#pluginsuggestionmarketplaces) 受管設定將市場加入允許清單時，標記為與您目前工作目錄相關的外掛程式會釘在頂部，並帶有 **suggested for this directory** 標籤。 3 安裝外掛程式 選擇外掛程式以檢視其詳細資訊。詳細資訊窗格會顯示外掛程式包含的內容及其成本：

- **Context cost** 估計，讓您可以查看外掛程式每回合會為您的[內容視窗](https://code.claude.com/docs/zh-TW/features-overview#understand-context-costs)新增多少個 token
- 外掛程式的 **Last updated** 日期
- **Will install** 區段，列出外掛程式的命令、代理程式、skills、hooks 和 MCP 及 LSP 伺服器，讓您可以在安裝前檢視它新增的確切內容

並非每個外掛程式都提供這些欄位背後的資料。對於來自本機或自訂市場的外掛程式，您可能看不到 **Context cost** 和 **Last updated** 列，**Will install** 區段可能會改為顯示 **Components will be discovered at installation** 。選擇安裝範圍：

- **User scope** ：在所有專案中為自己安裝
- **Project scope** ：為此儲存庫上的所有協作者安裝
- **Local scope** ：僅在此儲存庫中為自己安裝

例如，選擇 **commit-commands** （新增 git 工作流程 skills 的外掛程式）並將其安裝到您的使用者範圍。您也可以直接從命令列開始安裝：

```
/plugin install commit-commands@claude-code-plugins

```

請參閱[設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)以深入瞭解範圍。 4 使用您的新外掛程式 如果安裝摘要報告 `Run /reload-plugins to activate.`，Claude Code 會為您執行該重新載入。如果重新載入警告您的下一則訊息會重新讀取對話，請執行 `/reload-plugins --force` 以啟用外掛程式。外掛程式 skills 由外掛程式名稱命名空間，因此 **commit-commands** 提供 `/commit-commands:commit` 之類的 skills。透過對檔案進行變更並執行以下命令來試試看：

```
/commit-commands:commit

```

這會暫存您的變更、產生提交訊息並建立提交。每個外掛程式的工作方式不同。檢查 **Discover** 標籤中的外掛程式詳細資訊以查看它提供的命令和 skills，或造訪其首頁以取得使用指導。

## 新增市場

使用 `/plugin marketplace add` 命令從不同來源新增市場。 **快捷方式** ：您可以使用 `/plugin market` 代替 `/plugin marketplace`，以及 `rm` 代替 `remove`。

- **GitHub 儲存庫** ：`owner/repo` 格式，例如 `anthropics/claude-code`
- **Git URL** ：任何 git 儲存庫 URL，包括 GitLab、Bitbucket 和自託管伺服器
- **本機路徑** ：目錄或 `marketplace.json` 檔案的直接路徑
- **遠端 URL** ：託管 `marketplace.json` 檔案的直接 URL
- **claude.ai** ：託管在 claude.ai 上的市場（適用於您的帳戶），例如您組織的外掛程式庫，您可以[從 **Marketplaces** 標籤或您的 shell 按名稱新增](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai)，而不是按來源新增

### 從 GitHub 新增

使用 `owner/repo` 格式新增包含 `.claude-plugin/marketplace.json` 檔案的 GitHub 儲存庫，其中 `owner` 是 GitHub 使用者名稱或組織，`repo` 是儲存庫名稱。 例如，`anthropics/claude-code` 指的是由 `anthropics` 擁有的 `claude-code` 儲存庫：

```
/plugin marketplace add anthropics/claude-code

```

### 從其他 Git 主機新增

透過提供完整 URL 新增 git 市場儲存庫。對於 `https://` URL，是否包含 `.git` 後綴取決於主機：

- **`github.com`和`gitlab.com`** ：Claude Code 可識別帶有或不帶 `.git` 後綴的儲存庫 URL，並複製它。新增不帶後綴的 `gitlab.com` URL 需要 Claude Code v2.1.232 或更新版本。在 v2.1.232 之前，Claude Code 將其視為託管 `marketplace.json` 檔案的直接連結。
- **Azure DevOps** ：省略後綴。Claude Code 複製任何路徑包含 `/_git/` 的 URL。如果您在 `/_git/` 路徑後面附加 `.git`，複製會失敗。
- **所有其他主機，包括自託管 GitLab 伺服器** ：包含 `.git` 後綴，以便 Claude Code 複製儲存庫，而不是將 URL 視為託管 `marketplace.json` 檔案的直接連結。對於複製 URL 不帶後綴的主機（例如 AWS CodeCommit），請改為在 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 中新增市場作為 git 項目。Claude Code 複製 git 項目時，無論其 URL 是否以 `.git` 結尾。

Claude Code 也複製具有巢狀子群組的 `gitlab.com` URL，例如 `https://gitlab.com/group/subgroup/project`。 包含 `https://` 前綴。Claude Code v2.1.196 及更新版本會拒絕沒有前綴的主機，例如 `gitlab.com/company/plugins.git`，視其為無效的 GitHub `owner/repo` 簡寫，錯誤訊息會告訴您新增前綴。較早的版本會將其誤讀為 GitHub 儲存庫路徑，並在複製時失敗。 使用 HTTPS：

```
/plugin marketplace add https://gitlab.com/company/plugins.git

```

使用 SSH：

```
/plugin marketplace add git@gitlab.com:company/plugins.git

```

Claude Code 複製 SSH 位址時，無論是否以 `.git` 結尾。 若要新增特定分支或標籤，請在 `#` 後面附加 ref：

```
/plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0

```

### 從本機路徑新增

新增包含 `.claude-plugin/marketplace.json` 檔案的本機目錄：

```
/plugin marketplace add ./my-marketplace

```

您也可以新增 `marketplace.json` 檔案的直接路徑：

```
/plugin marketplace add ./path/to/marketplace.json

```

### 從遠端 URL 新增

透過 URL 新增遠端 `marketplace.json` 檔案：

```
/plugin marketplace add https://example.com/marketplace.json

```

與基於 Git 的市場相比，基於 URL 的市場有一些限制。如果從基於 URL 的市場安裝外掛程式失敗，請參閱[故障排除](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugins-with-relative-paths-fail-in-url-based-marketplaces)。

### 從 claude.ai 新增

在[外掛程式從您的 claude.ai 帳戶同步](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)的終端機工作階段中，claude.ai 也可以為您列出市場，例如您組織的外掛程式庫和您自己的 claude.ai 上傳。`claude plugin marketplace list` 會在 `From claude.ai:` 區段中列印它們，而 `/plugin` **Marketplaces** 標籤也會列出它們。在那裡選擇一個以新增它。從 claude.ai 新增市場需要 Claude Code v2.1.273 或更新版本。 若要從您的 shell 新增一個，請執行 `claude plugin marketplace add` 並使用 `--claudeai` 旗標和列表中顯示的名稱：

```
claude plugin marketplace add --claudeai claudeai-organization-library

```

Claude Code 會在以 `claudeai-` 開頭的本機名稱下註冊市場，該名稱衍生自 claude.ai 列出的名稱：列為「Organization library」的市場會註冊為 `claudeai-organization-library`。使用該名稱安裝其外掛程式，例如使用 `claude plugin install <plugin>@claudeai-organization-library`。 如果您登出或使用不同帳戶登入，市場會保持設定但不顯示任何外掛程式，而您已從中安裝的外掛程式會繼續載入。 `From claude.ai:` 區段也可以列出透過 claude.ai 共享的基於 git 的市場。您可以使用普通的 `marketplace add` 命令新增這些市場，使用列表列印的來源。

## 安裝外掛程式

新增市場後，您可以按名稱安裝外掛程式。對於您尚未新增的市場，您可以改為[在一個命令中新增並安裝](https://code.claude.com/docs/zh-TW/discover-plugins#add-a-marketplace-and-install-in-one-command)。 若要按名稱安裝：

```
/plugin install plugin-name@marketplace-name

```

該命令會開啟該外掛程式的詳細資訊，您可以在其中選擇[安裝範圍](https://code.claude.com/docs/zh-TW/settings#where-settings-live)。當您執行 `/plugin`、前往 **Discover** 標籤，並在外掛程式上按 **Enter** 時，您會看到相同的選項：

- **User scope** ：在所有專案中為自己安裝
- **Project scope** ：為此儲存庫上的所有協作者安裝，這會將外掛程式新增到 `.claude/settings.json`
- **Local scope** ：僅在此儲存庫中為自己安裝，不與協作者共享

若要在沒有互動式步驟的情況下安裝，請使用 [`claude plugin install`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-install) shell 命令，該命令預設安裝到使用者範圍，除非您傳遞 `--scope`。對於具有[`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-the-command)的外掛程式，傳遞 `--yes` 以接受它顯示的命令。 您也可能看到具有 **managed** 範圍的外掛程式。這些是由管理員透過[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)安裝的，無法修改。 Claude Code 在其本地市場目錄副本中查詢外掛程式。您命名外掛程式的方式控制 Claude Code 是否先重新整理該副本：

- **使用市場名稱** ：當您安裝 `plugin-name@marketplace-name` 時，在工作階段中或使用 `claude plugin install` 時，Claude Code 會在查詢前重新整理該市場。即使您關閉了市場的[自動更新](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)或設定了 `DISABLE_AUTOUPDATER`，Claude Code 也會執行重新整理。在 v2.1.232 之前，Claude Code 在查詢前不會重新整理市場。Claude Code 在以下情況下會跳過此重新整理：
  - 市場未[從 GitHub、其他 Git 主機或遠端 URL 新增](https://code.claude.com/docs/zh-TW/discover-plugins#add-marketplaces)。
  - [種子目錄](https://code.claude.com/docs/zh-TW/plugin-marketplaces#pre-populate-plugins-for-containers)提供市場。
  - Claude Code 在過去 30 秒內重新整理了市場。
  - 您設定了 [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/zh-TW/env-vars)。
  - [受管設定](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)阻止市場，在這種情況下 Claude Code 也會拒絕安裝。
- **僅外掛程式名稱** ：當您在工作階段中執行 `/plugin install plugin-name` 時，Claude Code 只會重新整理它也在[背景更新](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)的市場，且僅在查詢失敗後。當您執行 `claude plugin install plugin-name` 時，Claude Code 會讀取快取的目錄而不重新整理。若要安裝在上次重新整理後發佈的外掛程式，請在工作階段中執行 `/plugin marketplace update <marketplace-name>` 或在您的 shell 中執行 [`claude plugin marketplace update <marketplace-name>`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-marketplace-update)，然後重試安裝。

如果命名安裝前的重新整理失敗，例如因為您離線，Claude Code 仍會在快取目錄中查詢外掛程式。`claude plugin install` 在其成功訊息中報告 `marketplace not refreshed`，而 `/plugin install` 在外掛程式詳細資訊上方或其找不到訊息中顯示失敗。 當您從 `/plugin` 介面安裝時，安裝摘要會告訴您外掛程式在您目前工作階段中是否為作用中：

- `Plugin is now active.`：Claude Code 在安裝過程中啟動了外掛程式。
- `Run /reload-plugins to activate.`：外掛程式尚未作用中，因為啟動它會[使提示快取失效](https://code.claude.com/docs/zh-TW/prompt-caching#enabling-or-disabling-a-plugin)或因為啟動嘗試失敗。Claude Code 接著會為您執行 `/reload-plugins`。如果該重新載入警告提示快取，請執行 `/reload-plugins --force` 以[在不重新啟動的情況下啟動外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)。
- 如果外掛程式無法載入，摘要會報告失敗，而 `/plugin` **Errors** 標籤會顯示詳細資訊。

在 v2.1.221 之前，在您執行 `/reload-plugins` 或重新啟動之前，沒有安裝在目前工作階段中生效。 `claude plugin install` shell 命令不在工作階段中執行，因此 Claude Code 會在您下次啟動 Claude Code 時或在已開啟的工作階段中執行 `/reload-plugins` 時載入它安裝的外掛程式。 在安裝外掛程式之前，請確保您信任它。Anthropic 不控制外掛程式中包含的 MCP servers、檔案或其他軟體，也無法驗證它們是否按預期工作。檢查每個外掛程式的首頁以獲取更多資訊。

### 在一個命令中新增市場並安裝

若要從您尚未新增的市場安裝外掛程式，請使用 `--marketplace` 命名市場來源。需要 Claude Code v2.1.275 或更新版本。

```
/plugin install quality-review-plugin --marketplace your-org/plugins

```

來源採用[與 `/plugin marketplace add` 相同的形式](https://code.claude.com/docs/zh-TW/discover-plugins#add-marketplaces)，例如 GitHub `owner/repo`、git URL 或本地路徑，除了它不能包含空格。給出外掛程式名稱時不帶 `@marketplace` 後綴。 如果您尚未新增該市場，Claude Code 會顯示它解析的來源，並要求您在新增前確認。拒絕會取消安裝並不新增任何內容。市場新增後，外掛程式的詳細資訊會開啟，您可以選擇[安裝範圍](https://code.claude.com/docs/zh-TW/settings#where-settings-live)。

## 管理已安裝的外掛程式

執行 `/plugin` 並前往 **Installed** 標籤以檢視、啟用、停用或解除安裝外掛程式。清單按範圍分組，並排序以便您首先看到問題：具有載入錯誤或未解決依賴項的外掛程式出現在頂部，然後是您的最愛，停用的外掛程式摺疊在底部的摺疊標題後面。 從清單中，您可以：

- 按 `f` 以將選定的外掛程式加入最愛或取消加入最愛
- 輸入以按外掛程式名稱或描述篩選
- 按 Enter 以開啟外掛程式的詳細檢視並啟用、停用或解除安裝它

Claude Code 也會在 **Installed** 標籤中列出[從您的 claude.ai 帳戶同步的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)，其來源為 `synced`。除非您的組織將其標記為必需，否則您可以在那裡啟用或停用一個。若要移除一個，請在 claude.ai 上將其關閉。同步的外掛程式會出現在 Claude Code v2.1.273 或更新版本的終端工作階段中。 當您解除安裝專案的 `.claude/settings.json` 啟用的外掛程式時，Claude Code 會詢問您指的是哪個範圍：僅為您停用它，這會將覆寫寫入您的 `.claude/settings.local.json` 並為專案保留已安裝的外掛程式，或為所有人解除安裝它，這會將其從共用的 `.claude/settings.json` 中移除。 詳細檢視會顯示外掛程式貢獻的元件：commands、skills、agents、hooks、MCP servers 和 LSP servers。相同的清單也可從命令列透過 `claude plugin details` 取得。 Claude Code 也會在 **Installed** 標籤中的 **Not used recently** 標題下列出您自己安裝但至少兩週內未使用且跨越至少 10 個工作階段的 marketplace 外掛程式。詳細檢視會為每個外掛程式顯示 **Last used** 行。使用這些功能來找出您不再使用但仍在增加啟動和內容成本的外掛程式，然後停用或解除安裝它們。 兩種外掛程式永遠不會列為未使用：

- 您的組織管理的外掛程式或您使用 `--plugin-dir` 載入的外掛程式
- 貢獻 theme、output style、monitor 或 workflow 的外掛程式，因為這些外掛程式提供價值而無需追蹤叫用

當您的組織使用 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces) 限制 marketplaces 時，**Not used recently** 標題和 **Last used** 行都會隱藏。 外掛程式的 [language server](https://code.claude.com/docs/zh-TW/plugins#add-lsp-servers-to-your-plugin) 在提供診斷或回答程式碼導覽請求時計為已使用，因此其伺服器在您的工作階段中處於活動狀態的 LSP 外掛程式不會列為未使用。在 v2.1.203 之前，無法將語言伺服器活動計為使用，因此貢獻 LSP 伺服器的外掛程式完全豁免於該群組，與 theme 和 output style 外掛程式的方式相同。 在計算語言伺服器活動的版本上的第一個工作階段也會重設每個尚未記錄任何使用的 LSP 外掛程式的使用記錄，因此 Claude Code 不會根據在其伺服器活動被追蹤之前記錄的資料將您較早安裝的外掛程式判斷為未使用。 當您安裝聲明依賴項的外掛程式時，安裝輸出會列出哪些依賴項與其一起自動安裝。 您也可以使用直接命令管理外掛程式：

- 當您執行 `/plugin disable`、`/plugin enable` 或 `/plugin uninstall` 時，Claude Code 會開啟外掛程式面板以套用變更並保持其開啟。按 **Esc** 以在輸入另一個命令之前關閉面板。[在不重新啟動的情況下套用外掛程式變更](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)說明變更在您的工作階段中何時生效。
- 對於指令碼編寫，請改用 `claude plugin` shell 命令，這些命令不會開啟面板。

列出已安裝的外掛程式而不開啟選單：

```
/plugin list

```

傳遞 `--enabled` 或 `--disabled` 以僅顯示處於該狀態的外掛程式。 停用外掛程式而不解除安裝：

```
/plugin disable plugin-name@marketplace-name

```

重新啟用已停用的外掛程式：

```
/plugin enable plugin-name@marketplace-name

```

在這些識別碼中，`plugin-name` 是 [marketplace 項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-entries) 中外掛程式的 `name`，可能與外掛程式自身 `plugin.json` 中的 `name` 不同。 自 Claude Code v2.1.195 起，`/plugin` 介面中的 **Enable** 和 **Disable** 適用於其兩個名稱不同的外掛程式，`/plugin enable` 和 `/plugin disable` 接受任一名稱。當您在較早版本中停用此類外掛程式時，Claude Code 會報告 `already disabled` 並保持其啟用狀態。 完全移除外掛程式：

```
/plugin uninstall plugin-name@marketplace-name

```

`--scope` 選項可讓您使用 CLI 命令針對特定範圍：

```
claude plugin install formatter@your-org --scope project
claude plugin uninstall formatter@your-org --scope project

```

### 在不重新啟動的情況下套用外掛程式變更

當您關閉 `/plugin` 選單時，Claude Code 會為您執行 `/reload-plugins` 以套用您在其中所做的變更，例如安裝、啟用、停用和解除安裝外掛程式。如果重新載入會[使提示快取失效](https://code.claude.com/docs/zh-TW/prompt-caching#enabling-or-disabling-a-plugin)，它會發出警告並改為保留變更待處理；執行 `/reload-plugins --force` 以無論如何套用它們。如果 Claude 在您關閉選單時仍在回應，重新載入會在回應完成後執行。 對於在選單外發生的外掛程式變更，請自行執行 `/reload-plugins`。這些變更包括：

- 您在另一個終端中執行的 `claude plugin` 命令
- 您在開發時使用 [`--plugin-dir`](https://code.claude.com/docs/zh-TW/plugins#test-your-plugins-locally) 載入的外掛程式編輯
- 外掛程式[自動更新](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)，其通知要求您重新載入
- [從您的 claude.ai 帳戶同步](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)，已新增、更新或移除外掛程式並顯示要求您重新載入的通知
- [`--plugin-dir` 資料夾](https://code.claude.com/docs/zh-TW/plugins#test-your-plugins-locally)中的變更，Claude Code 保留該變更是因為套用它會使提示快取失效

在 v2.1.268 之前，您在選單中啟用、停用或解除安裝的外掛程式，以及在安裝期間未啟動的安裝，會保持待處理狀態，直到您執行 `/reload-plugins`。 `/reload-plugins` 也在沒有互動式終端的工作階段中執行，例如桌面應用程式、Agent SDK 和[非互動模式](https://code.claude.com/docs/zh-TW/headless)（使用 `-p`）。需要 Claude Code v2.1.260 或更新版本。在這些工作階段中適用兩個限制：

- 命令僅在您直接將其輸入到工作階段時執行，例如在 `-p` 提示或桌面應用程式的提示框中。當您改為透過遠端連線傳送它時，例如 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 或轉接的聊天訊息，命令會拒絕而不重新載入任何內容。
- 重新載入不會連線或斷開外掛程式 MCP servers。這些變更會在您的下一個工作階段中生效。

Claude Code 重新載入所有活動外掛程式，並顯示外掛程式、skills、agents、hooks、外掛程式 MCP servers 和外掛程式 LSP servers 的計數，在沒有互動式終端的工作階段中省略外掛程式 MCP server 計數。在 skills 計數中，Claude Code 包括外掛程式提供的每個 skill：其 `commands/` 項目和 `SKILL.md` skills。在 v2.1.246 之前，Claude Code 僅計算 `commands/` 項目，因此它可以重新載入外掛程式的 `SKILL.md` skills 並仍然在摘要中報告 `0 skills`。 重新載入在下一個請求時會產生令牌成本：新載入的元件會在附加到對話的內容中宣佈自己，而現有歷史記錄仍然從提示快取讀取。提供 MCP servers 的外掛程式在其工具未被 [tool search](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search) 延遲時成本更高：該變更會使快取失效，下一個請求會重新讀取整個對話。請參閱[啟用或停用外掛程式](https://code.claude.com/docs/zh-TW/prompt-caching#enabling-or-disabling-a-plugin)以取得詳細資訊。

## 管理市場

您可以透過互動式 `/plugin` 介面或使用 CLI 命令管理市場。

### 使用互動式介面

執行 `/plugin` 並前往 **Marketplaces** 標籤以：

- 檢視所有已新增的市場及其來源和狀態
- 新增新市場
- 更新市場清單以取得最新外掛程式
- 移除您不再需要的市場

### 使用 CLI 命令

您也可以使用直接命令管理市場。 列出所有已配置的市場：

```
/plugin marketplace list

```

從市場重新整理外掛程式清單：

```
/plugin marketplace update marketplace-name

```

移除市場：

```
/plugin marketplace remove marketplace-name

```

移除市場將解除安裝您從中安裝的任何外掛程式。

### 配置自動更新

Claude Code 可以在啟動後自動在背景更新市場及其已安裝的外掛程式。為市場啟用自動更新後，Claude Code 會重新整理市場資料並將已安裝的外掛程式更新到其磁碟上的最新版本。 Claude Code 會在您的工作階段開始後檢查市場和外掛程式更新，並隨機延遲最多十分鐘，因此執行中的工作階段會繼續使用它在啟動時載入的版本。如果任何外掛程式已更新，您將看到提示您執行 `/reload-plugins` 的通知，或新版本會在您下次啟動時載入。 自動更新也會排除其市場項目宣告 `headersHelper` 的外掛程式：Claude Code [既不執行命令也不下載該路徑上的封存](https://code.claude.com/docs/zh-TW/plugin-marketplaces#installs-and-updates-that-refuse-the-command-instead-of-asking)；該部分說明 Claude Code 何時在 `/plugin` Errors 標籤中列出外掛程式，以便您可以從其自己的檢視中更新它。 Claude Code 更新具有[`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)的外掛程式，其節奏與市場自動更新設定和 `DISABLE_AUTOUPDATER` 分開。相反，它[每個工作階段重新執行一次命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#when-claude-code-re-runs-the-command)，並在其[雜湊](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)已變更時將輸出安裝為新的外掛程式版本。 透過 UI 為個別市場切換自動更新：

1. 執行 `/plugin` 以開啟外掛程式管理器
1. 選擇 **Marketplaces**
1. 從清單中選擇市場
1. 選擇 **Enable auto-update** 或 **Disable auto-update**

`claude-plugins-official`、大多數其他官方 Anthropic 市場，以及[從 claude.ai 新增的市場](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai)預設啟用自動更新。其他第三方市場和本機開發市場預設停用自動更新。 管理員也可以在受管設定中的每個 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 項目上設定 `"autoUpdate": true`，以為組織市場啟用自動更新，而無需每個使用者都切換它。 若要停用 Claude Code 和從市場取得的外掛程式的自動更新，請設定 `DISABLE_AUTOUPDATER` 環境變數。具有[`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)的外掛程式遵循其自己的每個工作階段一次重新解析。如需詳細資訊，請參閱[自動更新](https://code.claude.com/docs/zh-TW/setup#auto-updates)。 若要在停用 Claude Code 自動更新的同時保持外掛程式自動更新啟用，請設定 `FORCE_AUTOUPDATE_PLUGINS=1` 以及 `DISABLE_AUTOUPDATER`：

```
export DISABLE_AUTOUPDATER=1
export FORCE_AUTOUPDATE_PLUGINS=1

```

## 配置團隊市場

團隊管理員可以透過將市場配置新增到 `.claude/settings.json` 來為專案設定自動市場安裝。當團隊成員[信任儲存庫資料夾](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)後，Claude Code 會自動新增這些市場，無需進一步提示。 自 Claude Code v2.1.195 起，新增市場不會安裝來自外部來源的外掛程式，在任何載入外掛程式的路徑上都是如此。只有專案的 `.claude/settings.json` 啟用的外掛程式，且來自外部來源（例如 GitHub 儲存庫或 npm 套件），在團隊成員安裝之前不會載入。在此之前，Claude Code 會將外掛程式報告為未安裝，並顯示要執行的 `claude plugin install` 命令。 將 `extraKnownMarketplaces` 新增到您的專案的 `.claude/settings.json`：

```
{
  "extraKnownMarketplaces": {
    "my-team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  }
}

```

如需完整配置選項（包括 `extraKnownMarketplaces` 和 `enabledPlugins`），請參閱[外掛程式設定](https://code.claude.com/docs/zh-TW/settings-reference#plugin-settings)。

## 安全性

外掛程式和市場是高度受信任的元件，可以使用您的使用者權限在您的機器上執行任意程式碼。僅從您信任的來源安裝外掛程式和新增市場。組織可以使用[受管市場限制](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)限制使用者可以新增的市場。

## 故障排除

### /plugin 命令無法識別

如果您看到「未知命令」或 `/plugin` 命令未出現：

1. **檢查您的版本** ：執行 `claude --version` 以查看已安裝的內容。
1. **更新 Claude Code** ：
   - **Homebrew** ：`brew upgrade claude-code`，或如果您安裝了該 cask，執行 `brew upgrade claude-code@latest`
   - **npm** ：`npm install -g @anthropic-ai/claude-code@latest`
   - **原生安裝程式** ：從[設定](https://code.claude.com/docs/zh-TW/setup)重新執行安裝命令
1. **重新啟動 Claude Code** ：更新後，重新啟動您的終端機並再次執行 `claude`。

### 常見問題

如果 plugin skills 未出現，使用 `rm -rf ~/.claude/plugins/cache` 清除快取，重新啟動 Claude Code，然後重新安裝 plugin。 如需詳細的故障排除和解決方案，請參閱市場指南中的[故障排除](https://code.claude.com/docs/zh-TW/plugin-marketplaces#troubleshooting)。如需偵錯工具，請參閱[偵錯和開發工具](https://code.claude.com/docs/zh-TW/plugins-reference#debugging-and-development-tools)。

### 程式碼智能問題

- **語言伺服器未啟動** ：驗證二進位檔已安裝且在您的 `$PATH` 中可用。檢查 `/plugin` Errors 標籤以獲取詳細資訊。
- **高記憶體使用量** ：`rust-analyzer` 和 `pyright` 等語言伺服器在大型專案上可能會消耗大量記憶體。如果您遇到記憶體問題，請使用 `/plugin disable <plugin-name>` 停用外掛程式，並改為依賴 Claude 的內建搜尋工具。
- **monorepos 中的誤報診斷** ：如果工作區配置不正確，語言伺服器可能會報告內部套件的未解決匯入錯誤。這些不會影響 Claude 編輯程式碼的能力。

## 後續步驟

- **構建您自己的外掛程式** ：請參閱[外掛程式](https://code.claude.com/docs/zh-TW/plugins)以建立技能、代理和 hooks
- **建立市場** ：請參閱[建立外掛程式市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)以將外掛程式分發給您的團隊或社群
- **技術參考** ：請參閱[外掛程式參考](https://code.claude.com/docs/zh-TW/plugins-reference)以取得完整規格

是否 助手
