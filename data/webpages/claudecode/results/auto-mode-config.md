[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)讓 Claude Code 無需例行權限提示即可執行，方法是透過分類器路由工具呼叫，該分類器會封鎖任何不可逆、破壞性或針對您環境外的操作。拒絕和明確要求規則在分類器之前進行評估，仍然會封鎖或提示。使用 `autoMode` 設定區塊告訴該分類器您的組織信任哪些儲存庫、儲存桶和網域，以便它停止封鎖例行內部操作。 自動模式適用於所有提供者上的所有使用者，包括 Anthropic API、[AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)、Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和已登入的 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)工作階段。如果 Claude Code 報告您的帳戶無法使用自動模式，請檢查[完整要求](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)，其中也涵蓋支援的模型和 Team 及 Enterprise 方案上的組織層級控制。在 v2.1.158 至 v2.1.206 中，Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 Claude 應用程式閘道工作階段上的自動模式需要設定 `CLAUDE_CODE_ENABLE_AUTO_MODE=1`；v2.1.207 移除了該要求。 根據預設，分類器只信任工作目錄和目前儲存庫的已設定遠端。推送到您公司的原始碼控制組織或寫入團隊雲端儲存桶等操作會被封鎖，直到您將它們新增到 `autoMode.environment`。 如需了解工作階段如何進入自動模式以及分類器預設封鎖的內容，請參閱[權限模式頁面上的自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)。此頁面是設定參考。 此頁面涵蓋如何：

- [為推送和提取請求新增人工檢查點](https://code.claude.com/docs/zh-TW/auto-mode-config#add-a-human-checkpoint)，使用 `permissions.ask`
- [選擇在何處設定規則](https://code.claude.com/docs/zh-TW/auto-mode-config#where-the-classifier-reads-configuration)，跨越 CLAUDE.md、使用者設定和受管設定
- [定義受信任的基礎結構](https://code.claude.com/docs/zh-TW/auto-mode-config#define-trusted-infrastructure)，使用 `autoMode.environment`
- [使用 `/auto-mode-setup` 產生環境項目](https://code.claude.com/docs/zh-TW/auto-mode-config#generate-environment-entries)
- [覆蓋封鎖和允許規則](https://code.claude.com/docs/zh-TW/auto-mode-config#override-the-block-and-allow-rules)，當預設值不符合您的管道時
- [從 `/permissions` 編輯規則](https://code.claude.com/docs/zh-TW/auto-mode-config#edit-rules-from-permissions)，無需開啟設定檔
- [使用 `autoMode.classifyAllShell` 透過分類器路由所有 shell 命令](https://code.claude.com/docs/zh-TW/auto-mode-config#route-all-shell-commands-through-the-classifier)
- [使用 `claude auto-mode` 子命令檢查您的有效設定](https://code.claude.com/docs/zh-TW/auto-mode-config#inspect-the-defaults-and-your-effective-config)
- [檢查拒絕](https://code.claude.com/docs/zh-TW/auto-mode-config#review-denials)，以便您知道接下來要新增什麼

## 常見的邊界

自動模式允許推送到您正在使用的儲存庫的任何分支（包括預設分支），並預設建立拉取請求。名稱標記為部署或發佈目標的非預設分支（例如 `production`、`release` 或 `gh-pages`）不受該預設涵蓋：分類器會根據其自身條件判斷推送到該分支，包括作為生產部署。推送的內容仍然會被檢查，因此強制推送、秘密進入提交，或在 CI 或部署管道執行時會將秘密發送到儲存庫外的變更仍然會被阻止。 在 v2.1.211 之前，分類器僅允許推送到您的工作分支、Claude 建立的分支，以及例行推送到預設分支。 如果您想在 Claude 的推送和拉取請求命令之前進行人工檢查點，請新增權限規則：下面的[配方](https://code.claude.com/docs/zh-TW/auto-mode-config#add-a-human-checkpoint)會保持自動模式對所有其他操作開啟。

### 新增人工檢查點

最直接的機制是 [`permissions.ask`](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)。內容範圍的 ask 規則（如下面的規則）在分類器之前進行評估，並且始終強制權限提示，即使在自動模式下也是如此，因為明確的 ask 規則是您要求提示該操作的明確意圖。在您的[設定](https://code.claude.com/docs/zh-TW/settings#where-settings-live)中新增規則：

```
{
  "permissions": {
    "ask": [
      "Bash(git push *)",
      "Bash(gh pr create *)"
    ]
  }
}

```

這些規則符合以 `git push` 或 `gh pr create` 開頭的命令。Claude 以其他方式寫入的推送，例如 `git -C <dir> push` 或 `git -c <key>=<value> push`，[不符合規則](https://code.claude.com/docs/zh-TW/permissions#bash-rule-limits)，因此不會被檢查點。對於檢查完整命令文字的檢查點，請新增 [PreToolUse hook](https://code.claude.com/docs/zh-TW/hooks#pretooluse)。 選擇與邊界需要有多堅定相符的機制：

| 邊界                   | 機制                                       | 自動模式中的行為                                                                                                                                                                   |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 在操作前提示           | `permissions.ask`                          | 始終為符合內容範圍規則（如上面的配方）的命令提示。分類器無法自動批准符合的操作。                                                                                                   |
| 永不執行操作           | `permissions.deny`                         | 在諮詢分類器之前阻止。分類器和使用者意圖都無法覆蓋它。                                                                                                                             |
| 此工作階段的一次性邊界 | 在對話中陳述，例如「在我審查之前不要推送」 | 分類器會阻止符合的操作，但如果[內容壓縮](https://code.claude.com/docs/zh-TW/costs#reduce-token-usage)移除了陳述該邊界的訊息，邊界可能會遺失。使用 ask 或 deny 規則以獲得持久保證。 |

## 分類器讀取設定的位置

分類器讀取與 Claude 本身載入相同的 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory) 內容，因此在您專案的 CLAUDE.md 中的指令（例如「永遠不要強制推送」）會同時引導 Claude 和分類器。請從該處開始了解專案慣例和行為規則。 對於跨專案適用的規則，例如受信任的基礎設施或組織範圍的拒絕規則，請使用 `autoMode` 設定區塊。分類器從以下範圍讀取 `autoMode`：

| 範圍                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 檔案                                                                       | 用途                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- | -------------------------------- |
| 單一開發者                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `~/.claude/settings.json`                                                  | 個人受信任的基礎設施             |
| 組織範圍                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | [受管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings) | 分散給所有開發者的受信任基礎設施 |
| `--settings` 旗標或 Agent SDK                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 內嵌 JSON                                                                  | 自動化的每次調用覆蓋             |
| 分類器不會從 `.claude/settings.json` 或 `.claude/settings.local.json` 中的專案設定讀取 `autoMode`。兩個檔案都位於儲存庫目錄中，因此已簽入的儲存庫或建置步驟可能會注入自己的允許規則。在 v2.1.207 之前，分類器也會讀取 `.claude/settings.local.json`；請將該檔案中的任何 `autoMode` 區塊移至 `~/.claude/settings.json`。排除 `.claude/settings.local.json` 也會關閉儲存庫提交該檔案或本機工具或建置步驟寫入該檔案的情況。 來自每個範圍的項目會被合併。開發者可以使用個人項目擴展 `environment`、`allow`、`soft_deny` 和 `hard_deny`，但無法移除受管理設定提供的項目。由於允許規則在分類器內部充當軟區塊規則的例外，開發者新增的 `allow` 項目可以覆蓋組織的 `soft_deny` 項目：組合是累加的，而不是硬政策邊界。 |                                                                            |                                  |
| 分類器是在[權限系統](https://code.claude.com/docs/zh-TW/permissions)之後執行的第二道閘門。對於無論使用者意圖或分類器設定如何都必須永遠不執行的動作，請在受管理設定中使用 `permissions.deny`，它會在諮詢分類器之前阻止該動作，且無法被覆蓋。                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                            |                                  |

## 定義受信任的基礎設施

對於大多數組織，`autoMode.environment` 是您唯一需要設定的欄位。它告訴分類器哪些儲存庫、儲存桶和網域是受信任的：分類器使用它來決定「外部」的含義，因此任何未列出的目的地都是潛在的資料外洩目標。 自 Claude Code v2.1.198 起，`claude auto-mode defaults` 會列印三種環境項目。v2.1.195 之前的版本只列印前五個信任槽位。

- **Context slots** ：描述您的組織、技術堆疊和安全態勢，以便分類器讀取您的上下文中的其他規則。每個預設為 `None configured` 或保守假設（名稱如下）：
  - **Organization**
  - **Claude Code 的主要用途** ：預設為軟體開發
  - **雲端提供者**
  - **儲存庫可見性** ：除非其遠端主機和名稱另有指示，或分類器讀取的對話中較早的可見性檢查顯示它是公開的，否則儲存庫被假定為私有。分類器讀取您的訊息和 Claude 執行的命令，而不是它們的輸出，因此證據必須是它能讀取的內容，例如您自己的訊息將儲存庫命名為公開；單獨執行 `gh repo view` 的輸出無法到達它。文字記錄證據檢查需要 Claude Code v2.1.200 或更新版本
  - **內部共享 / 程式碼片段託管** ：公開貼上和 gist 服務被視為在信任邊界之外，直到您命名其中一個
  - **組織特定的 CLI**
  - **祕密管理**
  - **CI/CD 部署目標**
  - **網路態勢**
  - **Host containment** ：預設為具有開放網際網路的普通開發人員機器或 CI 執行器。如果 Claude Code 在具有出口允許清單或不得接觸的鄰近項目的容器、VM 或 pod 中執行，請命名允許的主機、雲端中繼資料端點是否應可到達，以及任務使用的雲端專案、叢集或登錄以及使用的身分。在此項目命名該身分之前，分類器[阻止](https://code.claude.com/docs/zh-TW/permission-modes#what-the-classifier-blocks-by-default)主機自身認證的請求。需要 Claude Code v2.1.257 或更新版本
  - **受保護的部署命名空間 / 環境** ：在您命名它們之前，回退到「敏感遠端目標」啟發式
  - **資料保留 / 解密**
- **Trust slots** ：命名分類器視為在您邊界內的內容。槽位為「受信任的儲存庫」、「原始碼控制」、「受信任的內部網域」、「受信任的雲端儲存桶」、「關鍵內部服務」和「內部套件登錄」。儲存庫和原始碼控制項目預設為工作儲存庫及其配置的遠端。其他所有信任槽位預設為 `None configured`，因此在您新增之前，沒有其他內容是受信任的。儲存庫的可見性僅限於機密資料：私有儲存庫是機密資料的可接受目的地，但將儲存庫設為私有永遠不會清除祕密或個人或受信任的資料進入其中，分類器將從工作儲存庫外部移植、重新指向或首次讀取的內容視為不是該儲存庫自己的工作。此範圍設定需要 Claude Code v2.1.203 或更新版本。
- **Sensitivity slots** ：命名保護規則視為高風險的內容。槽位為「敏感資料位置和受眾」、「敏感遠端目標」和「受保護的 IaC 範圍」。每個預設為廣泛的啟發式，例如將任何名稱包含 `prod` 或 `production` 的主機或命名空間視為敏感遠端目標，因此保護規則在您配置任何內容之前就處於活動狀態。在敏感槽位中命名具體目標會使這些規則應用於命名的目標，而不是啟發式。

在 v2.1.211 之前，context slots 還包括一個「預設 / 受保護的分支」項目，該項目將 `main` 和 `master` 視為受保護的，直到您命名其他項目。v2.1.211 移除了它：[推送到您正在處理的儲存庫的任何分支](https://code.claude.com/docs/zh-TW/auto-mode-config#common-boundaries)預設是允許的，因此沒有受保護分支預設值可配置。 若要在預設值旁邊新增您自己的項目，請在陣列中包含字面字串 `"$defaults"`。預設項目會在該位置拼接，因此您的自訂項目可以在它們之前或之後。 以下範例保留預設項目並新增組織的儲存庫、儲存桶、網域和服務。

```
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it",
      "Trusted cloud buckets: s3://acme-build-artifacts, gs://acme-ml-datasets",
      "Trusted internal domains: *.corp.example.com, api.internal.example.com",
      "Key internal services: Jenkins at ci.example.com, Artifactory at artifacts.example.com"
    ]
  }
}

```

儲存您的設定後，執行 `claude auto-mode config` 以[確認有效規則](https://code.claude.com/docs/zh-TW/auto-mode-config#inspect-the-defaults-and-your-effective-config)包含您的項目。 項目是散文，不是正規表達式或工具模式。分類器將它們讀取為自然語言規則。按照您向新工程師描述基礎設施的方式編寫它們。徹底的環境部分涵蓋：

- **Organization** ：您的公司名稱以及 Claude Code 主要用於什麼，例如軟體開發、基礎設施自動化或資料工程
- **Source control** ：您的開發人員推送到的每個 GitHub、GitLab 或 Bitbucket 組織
- **雲端提供者和受信任的儲存桶** ：Claude 應該能夠讀取和寫入的儲存桶名稱或前綴
- **Trusted internal domains** ：您網路內 API、儀表板和服務的主機名稱，例如 `*.internal.example.com`
- **Key internal services** ：CI、構件登錄、內部套件索引、事件工具
- **Internal package registry** ：私有 npm、PyPI 或其他登錄，安裝應該透過它進行，因此繞過它安裝公開登錄的安裝會被阻止
- **Sensitive data locations & audiences**：保存個人資料、機密業務資料、認證、受管制資料或類似敏感資料的儲存桶、資料庫或路徑，以及每個位置中的資料可能與之共享的受眾，以便分類器保護這些位置而不是從內容猜測。Claude Code v2.1.195 至 v2.1.197 將此項目命名為「PII / 受管制資料位置」，僅涵蓋保存個人或受管制資料的位置，沒有受眾維度
- **Sensitive remote targets** ：計為生產環境的命名空間、主機或容器，因此遠端 shell 和埠轉發進入它們需要您的明確批准
- **Protected IaC scopes** ：應用或銷毀應始終需要您命名變更的基礎設施資源
- **Additional context** ：受管制行業限制、多租戶基礎設施或影響分類器應視為風險的合規要求

「Internal package registry」、「Sensitive data locations & audiences」、「Sensitive remote targets」和「Protected IaC scopes」項目需要 Claude Code v2.1.195 或更新版本。較早的版本仍將它們讀取為純上下文，但沒有針對它們的內建規則。 一個有用的起始範本：填入括號中的欄位並移除任何不適用的行。

```
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Organization: {COMPANY_NAME}. Primary use: {PRIMARY_USE_CASE, e.g. software development, infrastructure automation}",
      "Source control: {SOURCE_CONTROL, e.g. GitHub org github.example.com/acme-corp}",
      "Cloud provider(s): {CLOUD_PROVIDERS, e.g. AWS, GCP, Azure}",
      "Trusted cloud buckets: {TRUSTED_BUCKETS, e.g. s3://acme-builds, gs://acme-datasets}",
      "Trusted internal domains: {TRUSTED_DOMAINS, e.g. *.internal.example.com, api.example.com}",
      "Key internal services: {SERVICES, e.g. Jenkins at ci.example.com, Artifactory at artifacts.example.com}",
      "Additional context: {EXTRA, e.g. regulated industry, multi-tenant infrastructure, compliance requirements}"
    ]
  }
}

```

您提供的上下文越具體，分類器就越能區分日常內部操作和資料外洩嘗試。 您不需要一次填入所有內容。合理的推出：從預設值開始，新增您的原始碼控制組織和關鍵內部服務，這可以解決最常見的誤報，例如推送到您自己的儲存庫。接下來新增受信任的網域和雲端儲存桶。當出現阻止時填入其餘部分。

## 使用 `/auto-mode-setup` 產生環境項目

執行 `/auto-mode-setup` 讓 Claude Code 從您的專案和最近在其中的工作階段中草擬 `autoMode.environment` 項目，有時也會草擬[規則項目](https://code.claude.com/docs/zh-TW/auto-mode-config#override-the-block-and-allow-rules)。如果您接受草稿，Claude Code 會將其寫入 `~/.claude/settings.json`。 `/auto-mode-setup` 需要 Pro、Max 或 Team 方案，以及 Claude Code v2.1.228 或更新版本。在原生 Windows 上需要 v2.1.233 或更新版本。您無法在 [Claude Code on the web](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 中執行它。它也需要[功能旗標擷取](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)，所以您無法在已關閉旗標擷取的工作階段中執行它。

### `/auto-mode-setup` 讀取的內容

如果 `~/.claude/settings.json` 已經包含 `autoMode` 項目，Claude Code 會先詢問是否要新增到您的環境清單或取代它，並且無論如何都會保留您撰寫的規則。Claude Code 接著會詢問您如何使用此專案，並在掃描任何內容之前提供兩個選擇性掃描。在掃描中，Claude Code 始終讀取這些來源：

- 此專案的 `CLAUDE.md`、`README.md`、設定檔和 git 遠端
- 您的 `autoMode` 和 `permissions.allow` 設定
- Claude 在您最近在此專案中的工作階段中執行的命令的主機、儲存貯體和命令名稱，絕不是您的訊息

兩個選擇性掃描各新增一個來源：

- 您 shell 歷史記錄中每個命令的第一個字
- 您主目錄下遠端主機和儲存庫名稱

### 檢閱並儲存草稿

Claude Code 在背景掃描，然後向您顯示草稿。您可以整體接受或捨棄它，所以之後編輯 `~/.claude/settings.json` 以調整單個項目。當您接受時，Claude Code 會寫入草稿並將其與您已有的設定協調：

- Claude Code 寫入 `environment` 清單時不包含 `"$defaults"`，因為草稿詳細說明了它保持不變的內建項目
- Claude Code 在草稿新增項目的 `allow`、`soft_deny` 和 `hard_deny` 清單中各包含 `"$defaults"`，除非您已經撰寫了不含它的 `allow` 清單，所以您尚未取代的[內建規則](https://code.claude.com/docs/zh-TW/auto-mode-config#override-the-block-and-allow-rules)仍然有效
- 儲存後，Claude Code 會提供移除 `~/.claude/settings.json` 中自動模式忽略的 `permissions.allow` 規則，例如 `Bash(*)`，或自動核准破壞性命令的規則

然後執行 `claude auto-mode config` 以[查看有效結果](https://code.claude.com/docs/zh-TW/auto-mode-config#inspect-the-defaults-and-your-effective-config)。

### 關閉 `/auto-mode-setup`

一旦自動模式已阻止多個動作，而您仍然沒有 `autoMode.environment` 項目，Claude Code 會在回合結束時顯示標題為「教導自動模式關於您的環境？」的對話框，並提供為您執行 `/auto-mode-setup`。若要停止提供但保留命令，請在該對話框中選擇**不再顯示** 。 若要關閉命令和提供，請將此 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 項目新增到 `~/.claude/settings.json`：

```
{
  "skillOverrides": {
    "auto-mode-setup": "off"
  }
}

```

`/auto-mode-setup` 是內建命令而不是[捆綁技能](https://code.claude.com/docs/zh-TW/skills#bundled-skills)，所以此 `skillOverrides` 項目仍然適用於它，但 [`disableBundledSkills`](https://code.claude.com/docs/zh-TW/settings-reference#disablebundledskills) 不會將其關閉。

## 覆蓋阻止和允許規則

三個額外的欄位讓您取代分類器的內建規則清單：

- `autoMode.hard_deny`：無條件安全邊界
- `autoMode.soft_deny`：使用者意圖可以清除的破壞性操作
- `autoMode.allow`：軟阻止規則的例外

每個都是散文描述的陣列，讀取為自然語言規則。對於在分類器之前執行的工具模式型硬阻止，請使用 [`permissions.deny`](https://code.claude.com/docs/zh-TW/permissions)。 在分類器內，優先順序分為四個層級：

- `hard_deny` 規則無條件阻止。使用者意圖和 `allow` 例外不適用。
- `soft_deny` 規則接著阻止。使用者意圖和 `allow` 例外可以覆蓋這些。
- `allow` 規則然後覆蓋匹配的 `soft_deny` 規則作為例外。
- 明確的使用者意圖覆蓋剩餘的軟阻止：如果使用者的訊息直接且具體地描述 Claude 即將採取的確切操作，分類器允許它，即使 `soft_deny` 規則匹配。

一般請求不算作明確意圖。要求 Claude「清理儲存庫」不授權強制推送，但要求 Claude「強制推送此分支」則授權。 要放寬，當分類器重複標記預設例外不涵蓋的常規模式時，新增到 `allow`。要加強，對於預設值遺漏的特定於您環境的破壞性風險，新增到 `soft_deny`，或對於必須永遠不能跨越的安全邊界，新增到 `hard_deny`。 要保留內建規則同時新增您自己的規則，請在陣列中包含字面字串 `"$defaults"`。預設規則會在該位置拼接，因此您的自訂規則可以在它們之前或之後，並且當內建清單在版本發佈中變更時，您繼續繼承更新。 下列範例在所有四個清單中保留預設值，並將組織特定的規則新增到每個清單。

```
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it"
    ],
    "allow": [
      "$defaults",
      "Deploying to the staging namespace is allowed: staging is isolated from production and resets nightly",
      "Writing to s3://acme-scratch/ is allowed: ephemeral bucket with a 7-day lifecycle policy"
    ],
    "soft_deny": [
      "$defaults",
      "Never run database migrations outside the migrations CLI, even against dev databases",
      "Never modify files under infra/terraform/prod/: production infrastructure changes go through the review workflow"
    ],
    "hard_deny": [
      "$defaults",
      "Never send repository contents to third-party code-review APIs"
    ]
  }
}

```

設定 `environment`、`allow`、`soft_deny` 或 `hard_deny` 中的任何一個而不包含 `"$defaults"` 會取代該部分的整個預設清單。如果您設定沒有 `"$defaults"` 的陣列，您會捨棄該部分的內建規則：

- `soft_deny`：每個內建軟阻止規則，包括強制推送、`curl | bash`、生產部署和自動模式繞過
- `hard_deny`：內建資料外洩規則

每個部分獨立評估，因此單獨設定 `environment` 會保持預設 `allow`、`soft_deny` 和 `hard_deny` 清單完整。 只在您打算完全掌控清單時才省略 `"$defaults"`。要安全地執行此操作，執行 `claude auto-mode defaults` 列印內建規則，將它們複製到您的設定檔案中，然後根據您自己的管道和風險容限檢查每個規則。

## 從 `/permissions` 編輯規則

若要檢視和編輯分類器規則而不開啟設定檔，請執行 [`/permissions`](https://code.claude.com/docs/zh-TW/permissions#manage-permissions) 並選取 **Auto mode** 索引標籤。該索引標籤需要 Claude Code v2.1.246 或更新版本，且僅在 [auto mode 可供您的工作階段使用](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 時才會出現。 該索引標籤列出來自 [分類器讀取的每個範圍](https://code.claude.com/docs/zh-TW/auto-mode-config#where-the-classifier-reads-configuration) 的 `allow`、`soft_deny`、`hard_deny` 和 `environment` 項目，並顯示內建規則是否對每個區段生效。Claude Code 會將來自 [managed settings](https://code.claude.com/docs/zh-TW/server-managed-settings) 或 `--settings` 旗標的項目顯示為唯讀，並將您在該索引標籤上所做的每項變更儲存到 `~/.claude/settings.json`。從該索引標籤您可以：

- 在 `allow`、`soft_deny` 和 `hard_deny` 區段中新增、編輯或刪除規則。當您在某個區段中新增第一個規則時，Claude Code 也會插入 `"$defaults"`，以便 [內建規則](https://code.claude.com/docs/zh-TW/auto-mode-config#override-the-block-and-allow-rules) 保持生效。
- 關閉或重新開啟 `allow`、`soft_deny` 或 `hard_deny` 的內建規則。Claude Code 會透過在您的該區段清單中新增或移除 `"$defaults"` 來記錄該選擇，因此在您可以關閉其內建規則之前，某個區段至少需要您自己的一個規則。
- 在您的編輯器中將 `environment` 項目編輯為一份文件。如果您尚未設定任何 `environment` 項目，Claude Code 會先詢問是否要取代內建環境，然後在完整的內建文字上開啟編輯器。當您儲存時，Claude Code 會將您的 `autoMode.environment` 陣列取代為該文件。包含 `"$defaults"` 行以 [保留內建項目](https://code.claude.com/docs/zh-TW/auto-mode-config#define-trusted-infrastructure)。

## 透過分類器路由所有 shell 命令

根據預設，narrow Bash 和 PowerShell 允許規則（例如 `Bash(npm test)`）在自動模式中保持有效。Claude Code 會在分類器執行前解析它們，除非命令帶有[每個命令允許的網域](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode)。Claude Code 只會暫停授予任意程式碼執行權限的廣泛規則，例如 `Bash(*)` 或萬用字元解釋器，以及每個命名 [`Monitor`](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool) 的規則，因為 Monitor 命令會透過 shell 執行。這表示 narrow 規則仍然可能讓破壞性引數通過而不被分類器看到，例如規則前綴未預期的指令碼路徑或旗標。 將 `autoMode.classifyAllShell` 設定為 `true`，以在自動模式啟用時暫停每個 Bash 和 PowerShell 允許規則，讓分類器評估每個 shell 命令，無論您的允許清單為何。

```
{
  "autoMode": {
    "classifyAllShell": true
  }
}

```

這會用延遲換取涵蓋範圍：允許規則會立即核准的命令現在會等待分類器決定，每個 shell 命令都計為一次分類器呼叫。 此設定僅在自動模式啟用時適用，您的允許規則在其他權限模式中的行為正常。 `autoMode.classifyAllShell` 需要 Claude Code v2.1.193 或更新版本。較早的版本會忽略此金鑰，並繼續將 narrow shell 允許規則帶入自動模式。

## 檢查預設值和您的有效設定

`claude auto-mode` 子命令可幫助您檢查、驗證和重設您的設定。 將內建的 `environment`、`allow`、`soft_deny` 和 `hard_deny` 規則列印為 JSON：

```
claude auto-mode defaults

```

若要讀取一個規則的完整措辭而不需透過 `jq` 管道，請傳遞 `--label` 並加上規則標籤的開頭，例如 `claude auto-mode defaults --label 'Git Destructive'`。比對是對每個規則標籤的不區分大小寫前綴，沒有比對的部分會列印為空列表。需要 Claude Code v2.1.208 或更新版本。 列印分類器實際使用的內容為 JSON，其中您的設定已套用（如果已設定）或使用預設值：

```
claude auto-mode config

```

`defaults` 和 `config` 都會將四個規則列表列印為單一 JSON 物件，每個規則都是散文字串。這是一個截斷的範例：

```
{
  "allow": [
    ...
    "Test Artifacts: Hardcoded test API keys, placeholder credentials in examples, or hardcoding test cases. Placeholder means authored as a placeholder — a file or value copied from a real secret or sensitive path is never a test artifact (see Sensitive-Source Provenance).",
    ...
  ],
  "soft_deny": [
    "Git Destructive [named+specifics — **must name:** the destructive operation and its target]: Force pushing (`git push --force`), deleting remote branches, tags, or releases, or rewriting remote history. Also `git commit --amend` when the commit being rewritten is not the agent's own unpushed work: either no prior `git commit` is visible (HEAD pre-dates the session), or a `git push` of the current branch is visible after the most recent commit (it has been pushed). Clears when the user asked to amend/reword/fixup, or when it is a message-only reword (`--amend -m …`, nothing newly staged) of a commit the agent visibly created this session.",
    ...
  ],
  "hard_deny": [...],
  "environment": [
    ...
    "**Trusted repo**: The git repository the agent started in (its working directory) and its configured remote(s). When the repo's public/private visibility is given — by the Repository visibility entry or the user's own message — use it to scope what is OK to commit or push there: confidential material is fine in a private repo; in a public one, only that repo's own work is — and content ported, repointed, or first read from outside this session's repo is not its own work, whoever directed the port. Visibility scopes confidential material only: secrets and sensitive data (personal & entrusted) are never cleared into any repo by its visibility (see Definitions).",
    ...
  ]
}

```

取得 AI 對您自訂 `allow`、`soft_deny` 和 `hard_deny` 規則的回饋：

```
claude auto-mode critique

```

儲存您的設定後執行 `claude auto-mode config` 以確認有效規則符合您的預期，其中 `"$defaults"` 已展開到位。如果您已撰寫自訂規則，`claude auto-mode critique` 會檢查它們並標記模稜兩可、冗餘或可能導致誤判的項目。 若要捨棄您的自訂設定並回復到內建預設值，請執行重設子命令。它需要 Claude Code v2.1.212 或更新版本，並從您的使用者設定檔案中移除 `autoMode` 部分：

```
claude auto-mode reset

```

該命令會摘要說明它將移除的內容，並在寫入前詢問 `Reset auto mode configuration to defaults?`；傳遞 `--yes` 以略過確認。重設只會變更 `~/.claude/settings.json`：來自[受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)或 `--settings` 旗標的 `autoMode` 規則仍然適用。

## 檢視拒絕

若要檢視並重試自動模式分類器拒絕的動作，請開啟 `/permissions` 並選取 **Recently denied** 標籤，Claude Code 會在此記錄每項拒絕。在被拒絕的動作上按 `r` 以標記為重試：當您結束對話框時，Claude Code 會傳送訊息告知模型可能重試該工具呼叫，並繼續對話。 當分類器對動作[無法做出判決](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)時，因為獨立於自動模式的安全檢查拒絕了分類器自身的請求，或其回應無法解析，Claude Code 會拒絕該動作，但不會在 **Recently denied** 下記錄。連結的錯誤項目涵蓋 Claude 被告知的內容，以及如果您需要執行該動作的方式。

### 使用允許規則、環境項目或重試來修復拒絕

若要查看分類器阻止了什麼，請在對話中找到工具呼叫。如果呼叫顯示為縮短或摺疊成摘要行（例如 `Ran 3 shell commands`），請按 `Ctrl+O` 開啟[文字記錄檢視器](https://code.claude.com/docs/zh-TW/interactive-mode#transcript-viewer)，它會展開該呼叫。 螢幕上另外兩個報告拒絕的位置會省略命令或 URL：輸入框附近的通知（例如 `bash denied by auto mode · [Data Exfiltration] · /permissions`）會提供工具和原因，而 **Recently denied** 標籤會按 Claude 為其撰寫的描述列出 shell 命令。若要以程式設計方式擷取這些拒絕的確切輸入，請新增 [`PermissionDenied` hook](https://code.claude.com/docs/zh-TW/hooks#permissiondenied)，它會將其作為 `tool_input` 接收。 呼叫下方的文字會告訴您是否有任何需要修復的內容。報告分類器本身問題的文字，例如 `is temporarily unavailable` 的模型或分類器錯誤，表示 Claude Code 在沒有分類器最終判決的情況下阻止了呼叫；請參閱[自動模式無法判定動作的安全性](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)以了解該怎麼做。否則，讀取 `Denied by auto mode classifier` 的行加上原因（例如 `[Production Deploy]` 或 `Blocked by classifier`）表示分類器判定呼叫不安全，因此請從呼叫嘗試到達或執行的內容中選擇修復：

- 一個 Claude 在整個任務中需要的目的地，例如套件登錄、內部網域或儲存庫主機：將其新增至 `autoMode.environment`。
- 一個您想要從現在開始無需檢視即可執行的命令：新增 `allow` 規則。
- 一個您確實打算執行的一次性動作：在您的下一則訊息中說明該意圖，並讓 Claude 重試。

您可以從 `/permissions` 對話框的 [**Auto mode** 標籤](https://code.claude.com/docs/zh-TW/auto-mode-config#edit-rules-from-permissions)新增環境項目或 `allow` 規則。 在大多數工作階段中，原因會命名分類器符合的規則，以方括號表示，例如 `[Data Exfiltration]` 或 `[Production Deploy]`，而某些工作階段執行的分類器模型會新增簡短說明。Claude Code 會選取分類器模型，因此您看到的形式不是您可以設定的內容。

### 修復重複拒絕

同一目的地的重複拒絕通常表示分類器缺少背景資訊。將該目的地新增至 `autoMode.environment`，或[執行 `/auto-mode-setup`](https://code.claude.com/docs/zh-TW/auto-mode-config#generate-environment-entries) 讓 Claude Code 草擬項目，然後執行 `claude auto-mode config` 以確認變更已生效。 若要以程式設計方式對拒絕做出反應，請使用 [`PermissionDenied` hook](https://code.claude.com/docs/zh-TW/hooks#permissiondenied)。

## 另請參閱

- [權限模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)：什麼是自動模式、預設情況下它會阻止什麼，以及哪些工作階段會以自動模式啟動
- [受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)：在整個組織中部署 `autoMode` 設定
- [權限](https://code.claude.com/docs/zh-TW/permissions)：在分類器執行前套用的允許、詢問和拒絕規則
- [所有設定](https://code.claude.com/docs/zh-TW/settings-reference#automode)：每個設定鍵，包括 `autoMode`

是否 助手
