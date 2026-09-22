雲端環境適用於 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，該功能目前處於研究預覽階段，適用於 Pro、Max 和 Team 使用者，以及具有 [premium seats 或 Chat + Claude Code seats](https://support.claude.com/en/articles/11845131-use-claude-code-with-your-team-or-enterprise-plan) 的 Enterprise 使用者。 每個 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 都在雲端環境中執行。您可以設定環境以允許或拒絕 [網路存取](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)、[為工作階段設定環境變數](https://code.claude.com/docs/zh-TW/cloud-environments#set-environment-variables)，在 Pro 和 Max 方案上儲存工作階段使用的 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials) 而不會看到它們，以及在 Claude 開始工作前執行 [設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)。 相同的環境適用於您啟動雲端工作階段的任何地方：[Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop)、[Claude 行動應用程式](https://code.claude.com/docs/zh-TW/mobile)、您的瀏覽器在 [claude.ai/code](https://claude.ai/code)、終端機搭配 [`claude --cloud`](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud)、[routines](https://code.claude.com/docs/zh-TW/routines) 和 [Claude Tag](https://claude.com/docs/claude-tag/overview)。這些介面中的每一個也可以路由到 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)。[可用性和限制](https://code.claude.com/docs/zh-TW/self-hosted-environments#availability-and-limitations) 涵蓋當 Claude Tag 工作階段在其中執行時 Claude 尚無法使用的內容。 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段將網頁和行動介面連接到您自己機器上的工作階段，該工作階段使用您機器的網路和檔案，而不是雲端環境。Claude Tag 頻道工作階段僅使用組織層級環境，可以是 [共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments) 或 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)。

## Default 環境

如果您還沒有環境，上線設定會為您設定 **Default** 環境。具體方式取決於您在哪裡上線：

- **CLI 流程（例如`/web-setup` ）**：為您建立 **Default**
- **Pro 和 Max 上的網頁上線設定** ：為您建立 **Default**
- **Team 和 Enterprise 上的網頁上線設定** ：顯示 **Create your first cloud environment** 表單，除非擁有者已開啟[快速網頁設定](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)；保持表單的預設值並點擊 **Create & finish** 以取得相同的 **Default** 環境

**Default** 本身不帶有任何設定：

- [**Trusted** 網路存取](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)：工作階段可以到達套件登錄檔和其他[允許清單中的網域](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)，但無法透過工作階段的網路到達其他任何內容。
- 無其他設定：**Default** 不定義任何環境變數或設定指令碼，因此工作階段只會以[預先安裝的工具](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)開始。

只有 **Default** 可用時，每個工作階段都在其中執行。當您有多個環境時，工作階段會根據介面選擇一個：

- 在桌面應用程式、行動應用程式和 claude.ai/code 上，您自己啟動的工作階段使用[選擇器](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)中顯示的環境。當您尚未選擇時，擁有者設定的[組織預設](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)會填入選擇。[專案](https://code.claude.com/docs/zh-TW/claude-projects#project-settings-reference)中的執行緒改用專案設定中設定的環境。
- 從 CLI，Claude Code 使用您的 [`/remote-env` 選擇](https://code.claude.com/docs/zh-TW/cloud-environments#select-an-environment-from-the-cli)，或在您的清單有一個時回退到 Anthropic 託管的環境，否則回退到您清單中第一個不是橋接環境的環境，即 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 登錄以代表您自己的機器而非雲端環境的項目。對於[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)，在[分派工作階段](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing#run-the-test-loop)時使用其 `ccpool_` ID 傳遞 `--environment <environment-id>` 會覆蓋該調用的 `/remote-env` 選擇和回退。Claude Code 拒絕傳遞給該旗標的 Anthropic 託管 `env_` ID，因此使用 `/remote-env` 來定位這些。該旗標需要 Claude Code v2.1.224 或更新版本。

當預設不夠時，請設定環境：當 Claude 需要到達[預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)之外的網域、需要為其工作階段設定環境變數，或需要在開始工作前安裝相依性時。

## 設定您的環境

在 [claude.ai/code](https://claude.ai/code) 上建立、編輯和封存環境，您可以在 [Web 快速入門](https://code.claude.com/docs/zh-TW/web-quickstart)後或從 [Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop#cloud-sessions)的提示框中存取環境選擇器。您建立的環境是您帳戶的個人環境；由擁有者建立的[共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)會出現在相同的選擇器中。請參閱[已安裝的工具](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)以了解無需任何設定即可使用的工具。 1 開啟環境選擇器 在 [claude.ai/code](https://claude.ai/code) 上，選擇顯示目前環境名稱的雲端圖示，位於訊息框上方的列中。選擇器沒有設定頁面或直接 URL。

![環境選擇器在 claude.ai/code 的訊息框上方開啟。顯示環境名稱「預設」的雲端按鈕位於訊息框上方的列中。開啟的選單列出本機列（僅顯示「下載」和「Desktop」標籤）、雲端區段（其中「預設」環境被選中並顯示核取記號，滑鼠懸停時顯示設定齒輪圖示）、「新增雲端環境」選項，以及「遠端控制」區段（包含設定說明）。](https://mintcdn.com/claude-code/ZFId6l95856c5LSw/images/cloud-environment-selector.png?fit=max&auto=format&n=ZFId6l95856c5LSw&q=85&s=cc2813a5664519eaf5a89d793ce5af26)
> # Image-1
>
> **圖片摘要：**
> Claude 介面顯示本機、雲端環境與遠端控制選項，底部提供儲存庫選擇與任務輸入欄。
>
> **主要元素：**
> 1. 實體: 本機工作區, 雲端環境, 遠端控制, 儲存庫選擇, Opus 5
> 2. OCR文字:
> Local
> Download
> Desktop only
> Cloud
> Default
> Add cloud environment…
> Remote Control
> Set up Remote Control
> Run claude rc on your machine to code from
> here.
> Default
> Select repo...
> Describe a task or ask a question
> Accept edits
> Opus 5
> High
> 3. 主題標籤: 遠端控制, 雲端環境, 程式碼工作區, 儲存庫, Claude
>
> **頁面關聯：**
> Claude 程式碼工作區介面，錨點為 Remote Control、Opus 5
2 新增或編輯環境 選擇**新增雲端環境** ，或將滑鼠懸停在現有環境上，然後選擇右側出現的設定圖示。對話框包括名稱、網路存取層級、環境變數和設定指令碼。當您在 Pro 或 Max 方案上編輯現有的雲端環境時，對話框還包括 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)。

![新增雲端環境對話框。名稱欄位，預留位置為「預設」；網路存取選擇器設定為「信任」，並包含網路政策和存取層級的連結；環境變數框顯示 .env 格式的預留位置文字，並附註值對使用該環境的任何人都可見；設定指令碼框描述為 Bash 指令碼，在新工作階段啟動時執行，在 Claude Code 啟動前執行；以及「取消」和「建立環境」按鈕。](https://mintcdn.com/claude-code/ZFId6l95856c5LSw/images/cloud-environment-dialog.png?fit=max&auto=format&n=ZFId6l95856c5LSw&q=85&s=30d4478b31d1f879f7ee287ddab32505)
> # Image-2
>
> **圖片摘要：**
> New cloud environment 視窗含名稱、網路存取、環境變數與 Bash 腳本設定區。
>
> **主要元素：**
> 1. 實體: 雲端環境建立視窗,網路存取設定,環境變數編輯區,初始化腳本區,建立環境操作
> 2. OCR文字:
> New cloud environment
> Name
> Default
> Network access
> Trusted
> Learn more about our network policy and access levels
> Environment variables
> NODE_ENV=production
> GIT_AUTHOR_NAME=Your Name
> # Multiline values - wrap in quotes
> CONFIG="key1=val1
> key2=val2"
> In .env format. These are visible to anyone using this environment — don’t add
> secrets or credentials.
> Setup script
> #!/bin/bash
> npm install
> Bash script that runs when a new session starts, before Claude Code
> launches.
> Cancel
> Create environment
> 3. 主題標籤: 雲端環境,環境變數,網路存取,初始化腳本,Claude Code
>
> **頁面關聯：**
> Claude Code 雲端環境建立頁；錨點：New cloud environment
### 設定環境變數

環境變數使用 `.env` 格式，每行一個 `KEY=value` 對。純值不需要引號，如果您用匹配的一對引號引用值，引號不會成為值的一部分。引用跨越多行或包含 `#` 的值：在未引用的值中，`#` 開始註解，該行的其餘部分會被捨棄。 以下範例定義三個變數。

```
NODE_ENV=development
LOG_LEVEL=debug
DATABASE_URL=postgres://localhost:5432/myapp

```

每個工作階段在啟動時將環境的值複製一次到普通環境變數中，Claude 執行的任何命令都可以讀取。由於執行中的工作階段不會重新讀取設定，編輯或新增變數會影響您之後啟動的工作階段；已執行的工作階段會保留它們啟動時的值。 雲端工作階段在啟動時也會自行設定一些變數。對於 [`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#manage-context)，工作階段設定的值會覆蓋您在此新增的值，因此在此新增該金鑰沒有效果。 使用該環境的任何人都可以讀取這些值。在 Pro 和 Max 方案上，改為使用 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)來取得代理程式可以附加到請求的金鑰。[永遠不會取得認證的請求](https://code.claude.com/docs/zh-TW/cloud-environments#requests-that-never-get-the-credential)列在那裡。

### 新增 API 認證

API 認證是您儲存在雲端環境上的 API 金鑰或權杖，以便 Claude 可以從環境中的任何工作階段呼叫該 API，而無需查看金鑰。Anthropic 的代理程式會在每個請求離開工作階段的 VM 後，將金鑰新增到您列出的主機的請求中。金鑰永遠不會到達 Claude、它執行的命令或工作階段的環境變數。 API 認證在 Pro 和 Max 方案上可用。它們在 Team 或 Enterprise 方案上尚不可用，因此 **API 認證** 區段不會出現在這些方案的環境對話框中。

#### 需求

其中兩個決定您是否可以新增認證，另外兩個決定代理程式在新增後是否可以使用它：

- **角色** ：您的 claude.ai 組織中的組織管理員角色
  - 在 Team 和 Enterprise 上，擁有者持有它，管理員沒有
  - 在 Pro 和 Max 上，您在自己的組織中持有它
  - 沒有它，您會看到一個註記而不是認證清單，即使在您自己的環境上也是如此。請要求擁有者將認證新增到共用環境並在那裡執行您的工作階段
- **環境類型** ：已存在的 Anthropic 託管雲端環境。[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)沒有 API 認證
- **API 可達性** ：API 接受來自網際網路的連線，因為請求來自 Anthropic 的網路
- **加密金鑰** ：如果您的組織使用客戶管理的加密金鑰，您無法儲存認證

#### 新增認證

您從已存在的環境編輯器一次新增一個認證。新環境的對話框不提供它們。也沒有編輯。若要變更認證的主機或值，請刪除它並再次新增。 1 開啟環境的 API 認證 在 [claude.ai/code](https://claude.ai/code) [開啟環境進行編輯](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)。在**更新雲端環境** 對話框中，在**環境變數** 下方找到 **API 認證** 。您會看到環境上已有的認證，每個都顯示它適用的主機。 2 新增認證 選擇**新增認證** 並填寫表單。保留預設的**認證類型** **Bearer** ，用於在請求標頭中傳輸的 API 金鑰，並填寫這些欄位：

- **名稱** ：認證的標籤，例如 `Internal billing API`
- **允許的網站** ：API 的主機，例如 `api.example.com`。前導 `*.` 符合每個子網域
- **自訂標頭** ：標頭的一列，該標頭攜帶金鑰。該列以 `Authorization` 作為標頭的**名稱** 和 `Bearer` 作為其**前綴** 開始；將金鑰本身貼上為**值** 。對於採用裸值的標頭（如 `X-Api-Key`），變更名稱並清除前綴

對於以其他方式進行身份驗證的 API，請選擇不同的**認證類型** 。清單與 [Claude Tag](https://claude.com/docs/claude-tag/overview)（Team 和 Enterprise 方案的 Slack 整合）為[連線](https://claude.com/docs/claude-tag/admins/add-connections)提供的清單相同。 3 儲存認證 選擇**連線** 。認證出現在清單中，其主機已儲存，無需對話框的**儲存變更** 按鈕。儲存後，您無法再次檢視該值。 若要確認認證有效，請在環境中啟動工作階段並要求 Claude 呼叫 API，例如使用 `curl`。API 的回應就像金鑰在請求中一樣，金鑰不會出現在工作階段的環境變數或任何檔案中。如果清單將認證標記為**未傳送** ，其下方的註記會說明原因和解決方法。兩個主機重疊但不完全相符的認證不會獲得標記，代理程式只會傳送其中一個。

#### 哪些請求會取得認證

當請求的主機符合您在該認證上列出的主機之一時，代理程式會將認證附加到請求。工作階段可以到達這些主機，即使環境的[網路存取層級](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)否則不允許，除了[永遠不會取得認證的主機](https://code.claude.com/docs/zh-TW/cloud-environments#requests-that-never-get-the-credential)。認證適用於在環境中執行的每個工作階段，無論誰啟動它，直到您刪除它。

#### 永遠不會取得認證的請求

代理程式永遠不會將您新增的認證附加到這些請求：

- **GitHub** ：[GitHub 代理程式](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy)改為驗證對 GitHub 的請求，因此您不需要為其提供 API 認證
- **Anthropic API 和公開套件登錄** ：`api.anthropic.com`、`registry.npmjs.org`、`jsr.io`、`npm.jsr.io`、`pypi.org`、`files.pythonhosted.org`、`index.crates.io` 和 `proxy.golang.org`
- **設定指令碼請求** ：Claude Code 在啟動時連線到代理程式，在[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)執行後

### 從 CLI 選擇環境

在您的終端中執行 `/remote-env` 以選擇您從 CLI 建立的雲端工作階段的預設環境，例如 [`claude --cloud`](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud)。該命令開啟現有環境的選擇器，並將您的選擇儲存到[使用者設定](https://code.claude.com/docs/zh-TW/settings#where-settings-live)中的 `remote.defaultEnvironmentId` 金鑰，因此它適用於您機器上的每個專案，直到您變更它，除非在更高優先順序的[設定層](https://code.claude.com/docs/zh-TW/settings#settings-precedence)（例如儲存庫的專案設定）上設定相同的金鑰。 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) ID（形式為 `ccpool_...`）遵循更嚴格的來源規則。請參閱 [`remote.defaultEnvironmentId`](https://code.claude.com/docs/zh-TW/settings-reference#remote-defaultenvironmentid) 以了解 Claude Code 從中接受它的設定層。 `/remote-env` 只設定預設值：它不啟動工作階段，也無法新增或編輯環境。從[環境選擇器](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)管理它們。

### 封存環境

若要封存您自己的環境之一，請開啟它進行編輯並選擇**封存** 。擁有者從管理設定中的**雲端環境** 頁面封存[共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)。您無法刪除環境，只能封存它。 封存會影響新工作階段，而不是執行中的工作階段：

- 已在環境中執行的工作階段會繼續工作。
- 環境從選擇器和 `/remote-env` 中消失，因此您無法為新工作階段選擇它。
- 環境上的 API 認證在其執行中的工作階段中保持附加。在封存前刪除您不再需要的任何認證。
- 沒有新工作階段可以在任何表面上的封存環境中啟動。如果環境是您儲存的 [CLI 預設](https://code.claude.com/docs/zh-TW/cloud-environments#select-an-environment-from-the-cli)，當您的清單有一個時，Claude Code 會在 Anthropic 託管環境中啟動 CLI 雲端工作階段，否則在清單中不是[遠端控制橋接環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)的第一個環境中啟動。任何明確使用環境設定的內容，例如[例行程序](https://code.claude.com/docs/zh-TW/routines#environments-and-network-access)，無法在其中啟動新工作階段。將其指向另一個環境。

### 組織共用環境

在 Team 和 Enterprise 方案上，擁有者可以建立與組織的每個成員共用的雲端環境。相同的角色管理**雲端環境** 管理頁面上的所有其他內容，包括[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)；管理員角色無法開啟該頁面。可以開啟它的完整角色清單是[管理伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings#access-control)的角色清單。 共用環境會在每個成員的[環境選擇器](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)中出現，在**組織** 標題下，位於成員自己的環境之後（在**個人** 標題下），因此團隊可以標準化一個設定，而不是每個成員重新建立它。選擇共用環境的設定圖示會為每個成員（包括擁有者）開啟其設定的唯讀摘要。 擁有者以兩種方式之一將環境提供給組織：

- **建立共用環境** ：使用[管理設定](https://claude.ai/admin-settings)中的**雲端環境** 頁面，這也是擁有者編輯和封存共用環境的地方。每個都有一個名稱、一個[網路存取層級](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)、`.env` 格式的[環境變數](https://code.claude.com/docs/zh-TW/cloud-environments#set-environment-variables)和一個[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)。
- **共用個人環境** ：在環境選擇器中開啟您自己的環境之一進行編輯，然後從**誰可以使用它** 列共用它。環境保留其 ID，因此已使用它的工作階段和例行程序不受影響，每個成員都可以看到它並在其中啟動工作階段。

擁有者在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 分別選擇組織的[預設環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)。 每個成員在共用環境中的工作階段都會讀取其變數，因此不要在其中包含機密。[API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)（為工作階段提供它們無法讀取的金鑰）在 Team 或 Enterprise 方案上尚不可用。

### 設定 Claude Tag 頻道使用的環境

在 [Claude Tag](https://claude.com/docs/claude-tag/overview) 頻道中，Claude 作為您組織的共用身分工作，而不是任何成員，因此頻道工作階段只使用組織級別的環境，即共用環境或[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)。若要為頻道提供不是[預先安裝](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)的工具鏈（例如 .NET），擁有者可以從**雲端環境** admin 頁面建立[共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)，其中包含[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)來安裝它。以兩種方式之一將頻道指向環境：

- 在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 將共用或自託管環境設定為組織的[預設環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)。
- 在 Claude Tag admin 設定中[將其釘選到頻道](https://claude.com/docs/claude-tag/admins/troubleshooting#channel-sessions-use-the-wrong-environment-or-can%E2%80%99t-find-one)。

## 網路存取

每個環境都設定一個網路存取層級，控制其工作階段可以進行的出站連線。預設層級 **Trusted** 允許套件登錄和其他[允許清單中的網域](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)；**Custom** 採用您自己的網域清單。 若要變更環境的網路存取，[開啟它進行編輯](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)並在對話框中使用 **Network access** 選擇器。[共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)在該處以唯讀方式開啟，因此擁有者改為從[管理設定](https://claude.ai/admin-settings)中的 **Cloud environments** 頁面變更其網路存取。開啟選擇器的雲端圖示出現在[Default 環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)下列出的應用程式表面上，以及在[例行編輯器](https://code.claude.com/docs/zh-TW/routines#environments-and-network-access)中；個人環境在您的 claude.ai 帳戶設定中沒有單獨的頁面。 您在工作階段或例行上啟用的 MCP 連接器無需將其主機新增到 **Allowed domains** ，因為連接器流量透過 Anthropic 的伺服器而不是工作階段的網路傳輸。這依賴於[安全性和隔離](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#security-and-isolation)下提到的相同 Anthropic 繫結通道。關閉任何您不需要的連接器，以限制 Claude 可以到達的工具。

### 存取層級

[環境對話框](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)中的 **Network access** 欄位採用以下四個層級之一：

| 層級                                                                                               | 出站連線                                                                                                                          |
| -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **None**                                                                                           | 透過工作階段的網路沒有出站網路存取                                                                                                |
| **Trusted**                                                                                        | 僅限[允許清單中的網域](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)：套件登錄、GitHub、雲端 SDK |
| **Full**                                                                                           | 任何網域                                                                                                                          |
| **Custom**                                                                                         | 您自己的允許清單，可選擇性地包括預設值                                                                                            |
| 無論您選擇哪個層級，工作階段仍然可以到達這些，因為每一個都採用不通過工作階段的網路允許清單的路徑： |                                                                                                                                   |

- GitHub，透過其[單獨的代理](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy)
- 您啟用的 [MCP 連接器](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)，其流量透過 Anthropic 的伺服器傳輸
- 您在環境的 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)上列出的主機，除了[代理跳過的主機](https://code.claude.com/docs/zh-TW/cloud-environments#requests-that-never-get-the-credential)
- Anthropic API，用於 Claude Code 自己的請求，即使在 **None** 時也是如此，如[安全性和隔離](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#security-and-isolation)下所述

### 允許特定網域

若要允許不在 Trusted 清單中的網域，在環境的網路存取設定中選擇 **Custom** ，然後在 **Allowed domains** 欄位中每行列出一個網域。此範例允許內部專案可能需要的三個主機。

```
api.example.com
*.internal.example.com
registry.example.com

```

此環境中的工作階段現在可以到達 `api.example.com`、`internal.example.com` 的任何子網域和 `registry.example.com`，但透過工作階段的網路無法到達其他網域。[GitHub 流量](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy)、[MCP 連接器流量](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)和對環境 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)主機的請求（除了[代理跳過的主機](https://code.claude.com/docs/zh-TW/cloud-environments#requests-that-never-get-the-credential)）不會通過此允許清單。前導 `*.` 符合每個子網域。若要同時保留[Trusted 網域](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)，請勾選 **Also include default list of common package managers** ；不勾選則只允許您列出的內容。 如果您的組織使用[成品](https://code.claude.com/docs/zh-TW/artifacts#availability)，工作階段讀取成品時不需要在清單中包含 `*.frame.claudeusercontent.com`。當清單省略該主機時，Claude Code 會透過工作階段與 Anthropic 的連線讀取成品內容。在兩種情況下將主機保留在允許清單中：

- **此環境中的工作階段開啟另一個組織的公開成品** ：Claude Code 直接從主機擷取這些成品，因此將其新增到此清單。
- **您正在配置本機 CLI 或自託管執行器** ：在該允許清單中保留主機。請參閱[網路存取需求](https://code.claude.com/docs/zh-TW/network-config#network-access-requirements)和自託管[網路需求](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#network-requirements)。

每個環境都有自己的允許網域清單；沒有組織層級的允許清單可供管理員推送到每個成員的環境。[伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings)仍適用於雲端工作階段內，但其中沒有任何設定會將網域新增到環境的網路允許清單。若要為團隊提供一個標準清單，擁有者可以建立一個[組織共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)，具有 **Custom** 網路存取和該清單。

### GitHub 代理

在 Anthropic 託管的環境中，所有 GitHub 操作都通過專用代理，將您的真實 GitHub 認證保留在工作階段的 VM 外，獨立於環境的[存取層級](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)。自託管環境中的工作階段使用您的部署提供的認證進行 git 操作驗證；[配置 git](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git) 涵蓋選項，包括按工作階段鑄造的認證和選擇加入此相同代理。代理提供：

- **Git 認證** ：VM 內的 git 用戶端使用限定範圍的認證，代理驗證並將其交換為您的實際 GitHub 令牌。
- **API 請求** ：來自內建 GitHub 工具的請求，以及來自 [`proxy-injected` 預留位置](https://code.claude.com/docs/zh-TW/cloud-environments#work-with-github-issues-and-pull-requests)下的 `gh` 的請求，會以您的真實認證替換後發出。
- **推送保護** ：`git push` 僅適用於工作階段的目前工作分支；複製、擷取和 PR 操作正常運作。
- **儲存庫範圍** ：GitHub API 和發行資產請求僅到達附加到工作階段的儲存庫，因此從未附加的儲存庫下載發行資產的設定指令碼會收到 403。
- **GraphQL 限制** ：代理僅提供一組固定的 GraphQL 操作用於拉取請求工作流程。代理在 GraphQL 端點上拒絕所有其他內容，並返回 403，說明 `This GraphQL query is not enabled for this session` 並命名 REST 備用方案 `gh api repos/{owner}/{repo}/...`。無論您提供的認證如何，限制都適用於通過代理的每個請求，因此您設定的 `GH_TOKEN` 會收到相同的 403。Claude 無法透過代理到達僅存在於 GraphQL 中的 GitHub API，例如 Projects v2。

來自公開儲存庫的已提交檔案透過 `raw.githubusercontent.com` 到達，改由[安全代理](https://code.claude.com/docs/zh-TW/cloud-environments#security-proxy)處理。該網域在預設[Trusted 清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)中，因此除非環境的[存取層級](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)排除它，否則這些檔案保持可到達。

### 安全代理

Anthropic 託管環境中的雲端工作階段在 HTTP/HTTPS 網路代理後面執行，用於安全和濫用防止目的；在[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#default-deny-egress)中，出站流量改為通過您自己的網路邊界。來自 Anthropic 託管工作階段的所有出站網際網路流量都通過此代理，提供：

- 防止惡意請求
- 速率限制和濫用防止
- 內容篩選以增強安全性
- 所請求主機名稱的 DNS 層級稽核軌跡

## 雲端工作階段中可用的內容

在 Anthropic 託管的環境中，每個工作階段都會取得執行 Ubuntu 24.04 的全新虛擬機器 (VM)（x86_64 架構），無論您自己的作業系統和 CPU 架構為何，您的儲存庫已複製，常見的工具鏈已預先安裝。當相依性提供預先編譯的二進位檔案（例如具有原生擴充功能的 Ruby gems 或預先建置的 Python wheels）時，請使用其 x86_64 Linux 建置以符合 VM。本節涵蓋 Anthropic 託管的預設值、內建 GitHub 工具、如何 [執行測試和服務](https://code.claude.com/docs/zh-TW/cloud-environments#run-tests-start-services-and-add-packages)，以及每個 VM 取得的 [資源限制](https://code.claude.com/docs/zh-TW/cloud-environments#resource-limits)。 您的組織路由到 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) 的工作階段改為在您自己的執行器上執行，搭配您的執行器映像提供的工具。

### 您的設定中帶來的內容

雲端工作階段從您儲存庫的全新複製開始。您提交到儲存庫的任何內容都可用。您只在自己的機器上安裝或設定的任何內容在工作階段中都不可用。您組織的政策透過 [伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings) 分別到達。

|                                                                                                                                                                                                                                                                                                                                             | 在雲端工作階段中可用                                                                                             | 原因                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 您的儲存庫的 `CLAUDE.md`                                                                                                                                                                                                                                                                                                                    | 是                                                                                                               | 複製的一部分                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 您的儲存庫的 `.claude/settings.json` hooks 和權限規則                                                                                                                                                                                                                                                                                       | 是，在具有一個儲存庫的工作階段中                                                                                 | 複製的一部分。具有多個儲存庫的工作階段，包括 [project](https://code.claude.com/docs/zh-TW/claude-projects#what-threads-pick-up-from-your-repositories) 執行緒，在複製上方啟動，不讀取它們                                                                                                                                                                                                                                                                                                                                                              |
| 您的儲存庫的 `.mcp.json` MCP 伺服器                                                                                                                                                                                                                                                                                                         | 是，在具有一個儲存庫的工作階段中                                                                                 | 複製的一部分，從工作階段的工作目錄找到                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 您的儲存庫的 `.claude/rules/`                                                                                                                                                                                                                                                                                                               | 是                                                                                                               | 複製的一部分                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 您的儲存庫的 `.claude/skills/`、`.claude/agents/`、`.claude/commands/`                                                                                                                                                                                                                                                                      | 是                                                                                                               | 複製的一部分                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 在 `.claude/settings.json` 中宣告的 Plugins                                                                                                                                                                                                                                                                                                 | 是                                                                                                               | 在工作階段啟動時從您宣告的 [marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces) 安裝。需要網路存取以到達 marketplace 來源                                                                                                                                                                                                                                                                                                                                                                                                             |
| 您組織的 [伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings)                                                                                                                                                                                                                                                     | 是                                                                                                               | 在工作階段啟動時從 Anthropic 的伺服器擷取。請參閱 [Surface coverage](https://code.claude.com/docs/zh-TW/model-config#surface-coverage) 以了解 `availableModels` 在雲端工作階段中如何強制執行。透過 MDM 或管理設定檔部署到您的裝置的設定不適用，因為工作階段在 Anthropic 管理的 VM 上執行；在 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) 中，工作階段也會讀取執行器映像中的管理設定檔，根據 [Claude Code 如何結合管理來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources) |
| 您的使用者 `~/.claude/CLAUDE.md`                                                                                                                                                                                                                                                                                                            | 否                                                                                                               | 位於您的機器上，不在儲存庫中                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 您的使用者 `~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/commands/`                                                                                                                                                                                                                                                                  | 否                                                                                                               | 位於您的機器上，不在儲存庫中。改為將它們提交到儲存庫的 `.claude/` 目錄。雲端工作階段會自動載入您在 claude.ai 上啟用的技能                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 僅在您的使用者設定中啟用的 Plugins                                                                                                                                                                                                                                                                                                          | 否                                                                                                               | 使用者範圍的 `enabledPlugins` 位於 `~/.claude/settings.json`。改為在儲存庫的 `.claude/settings.json` 中宣告它們，或在您的 claude.ai 帳戶上啟用它們，以便 Claude Code 將它們載入為 [同步的 plugins](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)                                                                                                                                                                                                                                                                                |
| 您使用 `claude mcp add` 在預設本機範圍或使用者範圍新增的 MCP 伺服器                                                                                                                                                                                                                                                                         | 否                                                                                                               | 這些寫入您機器上的 `~/.claude.json`，不是儲存庫。使用 `claude mcp add --scope project` 新增伺服器，該伺服器寫入儲存庫的 [`.mcp.json`](https://code.claude.com/docs/zh-TW/mcp#project-scope)，並提交該檔案。具有一個儲存庫的工作階段會載入它                                                                                                                                                                                                                                                                                                            |
| 您的儲存庫的 `.claude/settings.json` `env` 區塊中的傳輸變數，例如 `NODE_EXTRA_CA_CERTS` 和 [mTLS 用戶端憑證變數](https://code.claude.com/docs/zh-TW/network-config#mtls-authentication)                                                                                                                                                     | 否                                                                                                               | 託管環境管理工作階段的 API 連接，因此 Claude Code 忽略這些金鑰，並在工作階段的偵錯日誌中記錄每個忽略的金鑰                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Claude 呼叫的服務的 API 金鑰和令牌                                                                                                                                                                                                                                                                                                          | 在 Pro 和 Max 方案上，作為 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials) | 您在環境上新增金鑰一次，代理程式代理會將其附加到您列出的主機的請求。代理程式代理 [無法附加](https://code.claude.com/docs/zh-TW/cloud-environments#requests-that-never-get-the-credential) 的金鑰，或任何 Team 或 Enterprise 方案上的金鑰，保留在環境變數中                                                                                                                                                                                                                                                                                             |
| 互動式驗證，例如 AWS SSO                                                                                                                                                                                                                                                                                                                    | 否                                                                                                               | 不支援。SSO 需要無法在雲端工作階段中執行的基於瀏覽器的登入                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 若要在雲端工作階段中提供您自己的設定，請將其提交到儲存庫。 任何使用環境的人都可以讀取其環境變數和設定指令碼。對話框在 **環境變數** 下的注意事項說明了這一點，並警告不要在那裡放置機密。在 Pro 和 Max 方案上，改為儲存代理程式代理可以附加的金鑰作為 [API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)。 |                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

### 已安裝的工具

雲端工作階段預先安裝了常見的語言執行時、建置工具和資料庫。下表按類別總結了包含的內容。

| 類別                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 包含                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Python**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Python 3.x，搭配 pip、poetry、uv、black、mypy、pytest、ruff              |
| **Node.js**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 20、21 和 22，搭配 npm、yarn、pnpm、bun¹、eslint、prettier、chromedriver |
| **Ruby**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 3.1、3.2、3.3，搭配 gem、bundler、rbenv                                  |
| **PHP**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 8.3，搭配 Composer                                                       |
| **Java**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | OpenJDK 21，搭配 Maven 和 Gradle                                         |
| **Go**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Go，搭配模組支援                                                         |
| **Rust**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | rustc 和 cargo                                                           |
| **C/C++**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | GCC、Clang、cmake、ninja、conan                                          |
| **Docker**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | docker、dockerd、docker compose                                          |
| **Databases**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | PostgreSQL 16、Redis 7.0                                                 |
| **Utilities**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | git、gh、jq、yq、ripgrep、tmux、vim、nano                                |
| ¹ Bun 已安裝，但在套件擷取時有已知的 [代理相容性問題](https://code.claude.com/docs/zh-TW/cloud-environments#install-dependencies-with-a-sessionstart-hook)。 若要取得此表中大多數工具的版本，請要求 Claude 在雲端工作階段中執行 `check-tools`。它是安裝在工作階段 VM 上的 shell 命令，不是 slash command；您要求 Claude 是因為 [Claude 為您執行所有 VM 命令](https://code.claude.com/docs/zh-TW/cloud-environments#run-tests-start-services-and-add-packages)。對於它不報告的工具，例如 Ruby、PHP、bun、PostgreSQL 或 Redis，請要求 Claude 執行工具自己的版本命令，例如 `psql --version`。 Node.js 版本安裝在 `/opt/node20`、`/opt/node21` 和 `/opt/node22`，預設情況下 22 在 `PATH` 上。若要使用不同的版本，請要求 Claude 將該版本的 `bin` 目錄（例如 `/opt/node20/bin`）前置到 `PATH`。 此清單之外的工具鏈，例如 .NET SDK，即使其套件登錄在 [預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains) 上也不會預先安裝。使用 [設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts) 安裝它們。 |                                                                          |

### 使用 GitHub 問題和提取請求

雲端工作階段包括內建 GitHub 工具，讓 Claude 無需任何設定即可讀取問題、列出提取請求、擷取差異和發佈評論。這些工具透過 [GitHub 代理](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy) 使用您在 [GitHub 驗證選項](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options) 下設定的任何方法進行驗證，因此您的令牌永遠不會進入容器。 您可以在 [環境設定](https://code.claude.com/docs/zh-TW/cloud-environments#set-environment-variables) 中自己設定 `GH_TOKEN` 或 `GITHUB_TOKEN`，或兩者都不設定，讓 [GitHub 代理](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy) 為您驗證：

- 如果您設定令牌，它會原封不動地傳遞到容器，因此您的指令碼和 GitHub 的 [`gh` CLI](https://cli.github.com) 直接使用它。
- 如果您都不設定，[GitHub 代理](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy) 正在為您的工作階段處理驗證，兩個變數在 Claude 執行的命令中讀取為預留位置字串 `proxy-injected`，代理在出站 GitHub 請求上替換您的真實認證。`gh` 無需您自己的令牌即可工作，但直接讀取 `GITHUB_TOKEN` 的指令碼會取得預留位置，而不是可用的令牌。

您設定的令牌是普通環境變數，因此使用環境的任何人都可以讀取它；代理路徑將認證保留在環境設定和工作階段 VM 之外。 若要檢查哪種情況適用於您的工作階段，請要求 Claude 執行 `echo $GH_TOKEN`。 GitHub 的 [`gh` CLI](https://cli.github.com) 已預先安裝。如果您需要內建工具未涵蓋的 `gh` 命令，例如 `gh release` 或 `gh workflow run`，請要求 Claude 執行它。`gh` 會自動讀取 `GH_TOKEN`，因此您不需要執行 `gh auth login`。

### 將輸出連結回工作階段

每個雲端工作階段在 claude.ai 上都有一個文字記錄 URL，工作階段可以從 `CLAUDE_CODE_REMOTE_SESSION_ID` 環境變數讀取自己的 ID。使用此在 PR 主體、提交訊息、Slack 貼文或產生的報告中放置可追蹤的連結，以便檢閱者可以開啟產生它們的執行。 Claude 在雲端工作階段中建立的提交包括 `Claude-Session: <url>` git 預告片，PR 主體包括工作階段 URL 在其自己的列上。若要省略預告片和 PR 主體連結，請將 [`attribution.sessionUrl`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-sessionurl) 設定為 `false`。 若要在提交或 PR 以外的內容中包含工作階段連結，例如 Claude 發佈的 Slack 訊息或它寫入的報告檔案，請要求 Claude 執行以下命令並使用其輸出。該命令將環境變數值中的 `cse_` 前綴轉換為文字記錄 URL 預期的 `session_` 前綴：

```
echo "https://claude.ai/code/${CLAUDE_CODE_REMOTE_SESSION_ID/#cse_/session_}"

```

### 執行測試、啟動服務和新增套件

您無法進入工作階段 VM 的 shell。Claude 為您執行每個命令，因此請將本節中的工作表述為您提示中的請求。

#### 執行測試

Claude 執行測試作為處理工作的一部分。在您的提示中要求它，例如「修復 `tests/` 中的失敗測試」或「在每次變更後執行 pytest」。隨 [預先安裝的工具鏈](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools) 提供的測試執行器（例如 pytest 和 cargo test）無需額外設定即可工作。您的專案宣告為相依性的執行器（例如 jest）會隨您的相依性一起安裝。

#### 啟動服務

PostgreSQL 和 Redis 已預先安裝但預設不執行。要求 Claude 啟動您需要的任何一個；它執行的命令是：

```
service postgresql start

```

```
service redis-server start

```

Docker 可用於執行容器化服務。要求 Claude 執行 `docker compose up` 以啟動您專案的服務。拉取映像的網路存取遵循您環境的 [存取層級](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)，[Trusted 預設值](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains) 包括 Docker Hub 和其他常見登錄。 如果您的映像很大或拉取速度很慢，請將 `docker compose pull` 或 `docker compose build` 新增到您的 [設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)。[環境快取](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching) 保留拉取的映像，因此每個新工作階段都在磁碟上有它們。快取僅儲存檔案，不儲存執行中的程序，因此 Claude 仍然每個工作階段啟動容器。

#### 新增套件

若要新增未預先安裝的套件，請使用 [設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)。[環境快取](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching) 保留指令碼安裝的內容，因此您在那裡安裝的套件在每個工作階段開始時都可用，無需每次重新安裝。您也可以要求 Claude 在工作階段中期安裝套件，但這些安裝不會帶到其他工作階段。

### 資源限制

Anthropic 託管環境中的雲端工作階段執行時具有可能隨時間變化的近似資源上限：

- 4 vCPU
- 16 GB RAM
- 30 GB 磁碟

VM 可能會停止需要明顯更多記憶體的工作，例如大型建置工作或記憶體密集型測試。對於超出這些限制的工作負載，請使用 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 在您自己的硬體上執行 Claude Code，或在 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) 中執行雲端工作階段，在您的組織操作的計算上。

## 設定指令碼

設定指令碼是一個 Bash 指令碼，在新的雲端工作階段啟動時執行，在 Claude Code 啟動之前執行。使用設定指令碼來安裝相依性、設定工具，或取得工作階段需要但未預先安裝的任何內容。 指令碼以 root 身份在 Ubuntu 24.04 上執行，因此 `apt install` 和大多數語言套件管理員都能運作。 若要新增設定指令碼，請開啟環境設定對話框，並在 **Setup script** 欄位中輸入您的指令碼。 此範例安裝 [ShellCheck](https://www.shellcheck.net/)，這不是預先安裝的。

```
#!/bin/bash
apt update && apt install -y shellcheck

```

### 指令碼需求

設定指令碼有三個限制條件需要考慮：

- **Exit zero** ：如果指令碼以非零狀態結束，工作階段將無法啟動。在非關鍵命令後附加 `|| true`，以便間歇性安裝失敗不會阻止工作階段。
- **在五分鐘內完成** ：將指令碼的總執行時間保持在大約五分鐘以內，以便[環境快取](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching)可以建立。使用 `&` 和 `wait` 並行執行獨立安裝，並將任何無法納入的單一下載移至[SessionStart hook](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts-vs-sessionstart-hooks)，在背景中啟動它。
- **安裝的網路存取** ：套件安裝需要連接到登錄檔。預設的 **Trusted** 層級涵蓋[常見套件登錄檔](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)，包括 npm、PyPI、RubyGems 和 crates.io；使用 **None** 網路存取時，安裝會失敗。

### 環境快取

設定指令碼在您第一次在環境中啟動工作階段時執行。完成後，Anthropic 會快照檔案系統，並將該快照重複用作後續工作階段的起點。新工作階段會以您的相依性、工具和 Docker 映像已在磁碟上開始，並跳過設定指令碼步驟。即使指令碼安裝大型工具鏈或拉取容器映像，這也能保持啟動速度快。 快取是檔案系統快照，因此它會保留設定指令碼寫入磁碟的內容，並丟失任何僅在執行中的內容。您安裝的套件、您拉取的 Docker 映像和您寫入的檔案都會保留。指令碼啟動的資料庫、`docker compose up` 堆疊或任何其他背景程序不會；透過詢問 Claude 或使用 [SessionStart hook](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts-vs-sessionstart-hooks) 在每個工作階段啟動這些。 當您變更環境的設定指令碼或允許的網路主機時，以及當快取在大約七天後達到過期時，設定指令碼會再次執行以重建快取。恢復現有工作階段永遠不會重新執行設定指令碼。 您不需要自己啟用快取或管理快照。

### 設定指令碼與 SessionStart hooks

使用設定指令碼來佈建 VM 本身：未[預先安裝](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)的工具鏈和 CLI 工具。使用 [SessionStart hook](https://code.claude.com/docs/zh-TW/hooks#sessionstart) 進行應在各處執行的專案設定，雲端和本機，例如 `npm install`。 設定指令碼和 SessionStart hooks 在雲端工作階段啟動時按固定順序執行。下表比較您在哪裡設定它們、何時執行以及在哪裡執行。

|                                                                                                                                                                             | 設定指令碼                                                                                                                                                                                      | SessionStart hooks                                                                                                                                                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **您在哪裡設定它們**                                                                                                                                                        | [claude.ai/code](https://claude.ai/code) 的環境對話框，加上[共用環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)的 **Cloud environments** 管理頁面 | [設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)，例如您的儲存庫的 `.claude/settings.json`；請參閱[您的設定中保留的內容](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)，了解哪些檔案到達雲端工作階段 |
| **它們何時執行**                                                                                                                                                            | 在 Claude Code 啟動之前，當存在[快取環境](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching)時跳過                                                                      | 在 Claude Code 啟動後，在每個工作階段（包括已恢復的工作階段）上                                                                                                                                                                                                          |
| **它們在哪裡執行**                                                                                                                                                          | 僅限雲端工作階段                                                                                                                                                                                | 本機和雲端工作階段                                                                                                                                                                                                                                                       |
| 如果您在使用者層級 `~/.claude/settings.json` 中有 SessionStart hooks，不要期望它們在雲端中：使用者層級設定保留在您的機器上。其他 hooks 執行的位置取決於工作階段執行的位置： |                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                          |

- **Anthropic 託管環境** ：Claude Code 執行來自儲存庫和您組織的[伺服器管理設定](https://code.claude.com/docs/zh-TW/server-managed-settings)的 hooks。
- **[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration#permissions-and-tool-approval)** ：Claude Code 也執行操作員從執行器主機的 `~/.claude/` 中植入的 hooks，以及執行器映像的受管設定檔中的 hooks，當該檔案是 Claude Code 應用的[受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)之一時。

### 使用 SessionStart hook 安裝相依性

若要僅在雲端工作階段中安裝相依性，請將 SessionStart hook 與檢查其執行位置的指令碼配對。 首先，將 SessionStart hook 新增至您的儲存庫的 `.claude/settings.json`。此設定告訴 Claude Code 在工作階段啟動或恢復時執行儲存庫中的 `scripts/install_pkgs.sh`：

```
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR\"/scripts/install_pkgs.sh"
          }
        ]
      }
    ]
  }
}

```

`matcher` 將 hook 限制為 `startup` 和 `resume` 事件，`$CLAUDE_PROJECT_DIR` 解析為儲存庫根目錄，因此 hook 無論工作階段的工作目錄如何都能找到指令碼。 接下來，在 `scripts/install_pkgs.sh` 建立指令碼。它在雲端外立即結束，然後安裝您的相依性：

```
#!/bin/bash

if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

npm install
pip install -r requirements.txt
exit 0

```

`CLAUDE_CODE_REMOTE` 檢查是將安裝限制在雲端工作階段的原因：工作階段 VM 的環境將該變數設為 `true`，本機上永遠不會是 `true`，因此在您的筆記型電腦上，指令碼在安裝任何內容之前結束。 這兩個檔案一起為每個雲端工作階段在啟動時提供新鮮的 `npm install` 和 `pip install`，同時保持本機工作階段不受影響。

#### 雲端工作階段中的限制

SessionStart hooks 在雲端中的行為與本機相同，但有以下注意事項：

- **每個工作階段一個儲存庫** ：具有多個儲存庫的工作階段不會從任何儲存庫的 `.claude/settings.json` 載入 hooks，因此您在其中定義的 SessionStart hook 不會執行。使用[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)為這些工作階段安裝相依性。
- **無雲端專用範圍** ：hooks 在本機和雲端工作階段中執行。若要跳過本機執行，請檢查 `CLAUDE_CODE_REMOTE` 環境變數是否為 `true`，如[相依性安裝指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#install-dependencies-with-a-sessionstart-hook)所示。
- **需要網路存取** ：安裝命令需要連接到套件登錄檔。如果您的環境使用 **None** 網路存取，這些 hooks 會失敗。**Trusted** 下的[預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)涵蓋 npm、PyPI、RubyGems 和 crates.io。
- **Proxy 相容性** ：在 Anthropic 託管環境中，所有出站流量都通過[安全 proxy](https://code.claude.com/docs/zh-TW/cloud-environments#security-proxy)，某些套件管理員無法與此 proxy 正確搭配運作；Bun 是一個已知的範例。在[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#default-deny-egress)中，出站流量通過您自己的網路邊界。
- **增加啟動延遲** ：hooks 在每次工作階段啟動或恢復時執行，不同於設定指令碼，設定指令碼受益於[環境快取](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching)。透過在重新安裝之前檢查相依性是否已存在來保持安裝指令碼快速。

若要自訂基礎映像，請使用設定指令碼在[提供的映像](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)上安裝您需要的內容，或使用 `docker compose` 作為 Claude 旁邊的容器執行您自己的映像。目前不支援完全取代基礎映像。

## 預設允許的網域

使用 **Trusted** 網路存取，工作階段預設可以到達以下網域。標記為 `*` 的網域表示萬用字元子網域符合，因此 `*.gcr.io` 允許 `gcr.io` 的任何子網域。 Anthropic 服務

- api.anthropic.com
- docs.claude.com
- platform.claude.com
- code.claude.com
- claude.ai

版本控制

- github.com
- [www.github.com](http://www.github.com)
- api.github.com
- npm.pkg.github.com
- raw.githubusercontent.com
- pkg-npm.githubusercontent.com
- objects.githubusercontent.com
- release-assets.githubusercontent.com
- codeload.github.com
- avatars.githubusercontent.com
- camo.githubusercontent.com
- gist.github.com
- gitlab.com
- [www.gitlab.com](http://www.gitlab.com)
- registry.gitlab.com
- bitbucket.org
- [www.bitbucket.org](http://www.bitbucket.org)
- api.bitbucket.org

容器登錄

- registry-1.docker.io
- auth.docker.io
- index.docker.io
- hub.docker.com
- [www.docker.com](http://www.docker.com)
- production.cloudflare.docker.com
- download.docker.com
- gcr.io
- \*.gcr.io
- ghcr.io
- mcr.microsoft.com
- \*.data.mcr.microsoft.com
- public.ecr.aws

雲端平台

- cloud.google.com
- accounts.google.com
- gcloud.google.com
- \*.googleapis.com
- storage.googleapis.com
- compute.googleapis.com
- container.googleapis.com
- azure.com
- portal.azure.com
- microsoft.com
- [www.microsoft.com](http://www.microsoft.com)
- \*.microsoftonline.com
- packages.microsoft.com
- dotnet.microsoft.com
- dot.net
- visualstudio.com
- dev.azure.com
- \*.amazonaws.com
- \*.api.aws
- oracle.com
- [www.oracle.com](http://www.oracle.com)
- java.com
- [www.java.com](http://www.java.com)
- java.net
- [www.java.net](http://www.java.net)
- download.oracle.com
- yum.oracle.com
- \*.r2.cloudflarestorage.com

JavaScript 和 Node 套件管理員

- registry.npmjs.org
- [www.npmjs.com](http://www.npmjs.com)
- [www.npmjs.org](http://www.npmjs.org)
- npmjs.com
- npmjs.org
- yarnpkg.com
- registry.yarnpkg.com
- jsr.io
- npm.jsr.io

Python 套件管理員

- pypi.org
- [www.pypi.org](http://www.pypi.org)
- files.pythonhosted.org
- pythonhosted.org
- test.pypi.org
- pypi.python.org
- pypa.io
- [www.pypa.io](http://www.pypa.io)

Ruby 套件管理員

- rubygems.org
- [www.rubygems.org](http://www.rubygems.org)
- api.rubygems.org
- index.rubygems.org
- ruby-lang.org
- [www.ruby-lang.org](http://www.ruby-lang.org)
- rubyforge.org
- [www.rubyforge.org](http://www.rubyforge.org)
- rubyonrails.org
- [www.rubyonrails.org](http://www.rubyonrails.org)
- rvm.io
- get.rvm.io

Rust 套件管理員

- crates.io
- [www.crates.io](http://www.crates.io)
- index.crates.io
- static.crates.io
- rustup.rs
- static.rust-lang.org
- [www.rust-lang.org](http://www.rust-lang.org)

Go 套件管理員

- proxy.golang.org
- sum.golang.org
- index.golang.org
- golang.org
- [www.golang.org](http://www.golang.org)
- goproxy.io
- pkg.go.dev

JVM 套件管理員

- maven.org
- repo.maven.org
- central.maven.org
- repo1.maven.org
- repo.maven.apache.org
- maven.google.com
- jcenter.bintray.com
- gradle.org
- [www.gradle.org](http://www.gradle.org)
- services.gradle.org
- plugins.gradle.org
- plugins-artifacts.gradle.org
- kotlinlang.org
- [www.kotlinlang.org](http://www.kotlinlang.org)
- spring.io
- repo.spring.io

其他套件管理員

- packagist.org (PHP Composer)
- [www.packagist.org](http://www.packagist.org)
- repo.packagist.org
- nuget.org (.NET NuGet)
- [www.nuget.org](http://www.nuget.org)
- api.nuget.org
- pub.dev (Dart/Flutter)
- api.pub.dev
- hex.pm (Elixir/Erlang)
- [www.hex.pm](http://www.hex.pm)
- cpan.org (Perl CPAN)
- [www.cpan.org](http://www.cpan.org)
- metacpan.org
- [www.metacpan.org](http://www.metacpan.org)
- api.metacpan.org
- cocoapods.org (iOS/macOS)
- [www.cocoapods.org](http://www.cocoapods.org)
- cdn.cocoapods.org
- haskell.org
- [www.haskell.org](http://www.haskell.org)
- hackage.haskell.org
- swift.org
- [www.swift.org](http://www.swift.org)

Linux 發行版

- archive.ubuntu.com
- security.ubuntu.com
- ubuntu.com
- [www.ubuntu.com](http://www.ubuntu.com)
- \*.ubuntu.com
- ppa.launchpad.net
- launchpad.net
- [www.launchpad.net](http://www.launchpad.net)
- \*.nixos.org

開發工具和平台

- dl.k8s.io (Kubernetes)
- pkgs.k8s.io
- k8s.io
- [www.k8s.io](http://www.k8s.io)
- releases.hashicorp.com (HashiCorp)
- apt.releases.hashicorp.com
- rpm.releases.hashicorp.com
- archive.releases.hashicorp.com
- hashicorp.com
- [www.hashicorp.com](http://www.hashicorp.com)
- repo.anaconda.com (Anaconda/Conda)
- conda.anaconda.org
- anaconda.org
- [www.anaconda.com](http://www.anaconda.com)
- anaconda.com
- continuum.io
- apache.org (Apache)
- [www.apache.org](http://www.apache.org)
- archive.apache.org
- downloads.apache.org
- eclipse.org (Eclipse)
- [www.eclipse.org](http://www.eclipse.org)
- download.eclipse.org
- nodejs.org (Node.js)
- [www.nodejs.org](http://www.nodejs.org)
- developer.apple.com
- developer.android.com
- pkg.stainless.com
- binaries.prisma.sh

雲端服務和監控

- http-intake.logs.datadoghq.com
- \*.datadoghq.com
- \*.datadoghq.eu
- api.honeycomb.io

內容傳遞和鏡像

- sourceforge.net
- \*.sourceforge.net
- packagecloud.io
- \*.packagecloud.io
- fonts.googleapis.com
- fonts.gstatic.com

架構和設定

- json-schema.org
- [www.json-schema.org](http://www.json-schema.org)
- json.schemastore.org
- [www.schemastore.org](http://www.schemastore.org)

Model Context Protocol

- \*.modelcontextprotocol.io

## 相關資源

- [Cloud sessions reference](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：啟動、管理和共用雲端工作階段
- [Cloud sessions quickstart](https://code.claude.com/docs/zh-TW/web-quickstart)：連接 GitHub 並啟動您的第一個雲端工作階段
- [Claude Tag](https://claude.com/docs/claude-tag/overview)：Claude 從 Slack 啟動的工作階段在相同的環境中執行
- [Routines](https://code.claude.com/docs/zh-TW/routines)：排程執行使用相同的環境和網路存取層級
- [Remote Control](https://code.claude.com/docs/zh-TW/remote-control)：改為在您自己的機器的網路和檔案上執行工作階段
- [Self-hosted environments](https://code.claude.com/docs/zh-TW/self-hosted-environments)：在您組織自己的基礎設施上執行雲端工作階段
- [SessionStart hooks](https://code.claude.com/docs/zh-TW/hooks#sessionstart)：儲存庫提交的設定，在本機和雲端工作階段中執行
- [Server-managed settings](https://code.claude.com/docs/zh-TW/server-managed-settings)：到達雲端工作階段的組織政策

是否 助手