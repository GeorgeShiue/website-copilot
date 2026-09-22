Claude Security plugin 在 Claude Code 工作階段內執行程式碼庫的多代理漏洞掃描。一個 Claude 代理團隊會對您的架構進行對應、建立威脅模型、搜尋漏洞，並在撰寫報告前獨立檢查每項發現。使用此 plugin 掃描整個儲存庫或[僅掃描一組變更](https://code.claude.com/docs/zh-TW/claude-security#scan-only-your-changes)，例如分支的差異、pull request 的差異或單一提交，然後將您選擇的發現轉換為您可以自行檢查和應用的修補程式。 此 plugin 在您的工作階段中本地執行，使用您在 Claude Code 中可以存取的任何模型，每次掃描都會計入您方案的使用限制。如果您想要一個監控您儲存庫的受管服務，或想要在 [Claude Mythos 5](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) 上執行掃描，請參閱 [Claude Security](https://claude.com/product/claude-security) 產品，該產品在企業方案上提供。此 plugin 可以存取受管產品無法存取的程式碼，例如託管在 GitLab 或 Bitbucket 上的儲存庫，或在不允許入站連線的網路上的儲存庫。 此 plugin 也不同於 Claude Code 中已有的檢查工具：[security guidance plugin](https://code.claude.com/docs/zh-TW/security-guidance) 在 Claude 撰寫程式碼時檢查程式碼，[`/security-review`](https://code.claude.com/docs/zh-TW/commands#all-commands) 對您的分支執行單一掃描，而 [Code Review](https://code.claude.com/docs/zh-TW/code-review) 檢查 pull request。如需了解這些層級如何堆疊，請參閱 [此 plugin 如何與其他安全工具配合](https://code.claude.com/docs/zh-TW/claude-security#how-the-plugin-fits-with-other-security-tools)。

## 先決條件

若要執行此外掛程式，您需要：

- 付費方案，用於掃描用來協調其代理的[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)。在 Pro 上，從 `/config` 中的「動態工作流程」列啟用它們。
- Python 3.9 或更新版本，在您的 `PATH` 上可用為 `python3`。使用 `python3 --version` 檢查。此外掛程式的工具僅使用 Python 標準程式庫，因此不會安裝任何內容。
- Linux、macOS 或 Windows。
- Git，用於變更掃描和將發現轉換為修補程式；這些工作不支援其他版本控制系統。完整掃描在任何目錄中都有效，無論是否有版本控制。

## 安裝外掛程式

在 Claude Code 工作階段中，從[官方 Anthropic 市集](https://code.claude.com/docs/zh-TW/discover-plugins#official-anthropic-marketplace)安裝：

```
/plugin install claude-security@claude-plugins-official

```

該命令會開啟外掛程式的詳細資訊，您可以在其中選擇[安裝範圍](https://code.claude.com/docs/zh-TW/discover-plugins#install-plugins)以開始安裝。 如果安裝失敗，修復方法取決於 Claude Code 報告的訊息：

- 如果它報告 `Marketplace "claude-plugins-official" not found`，使用 `/plugin marketplace add anthropics/claude-plugins-official` 新增市集，然後重試安裝。
- 如果它報告[在市集中找不到外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins#install-plugins)，檢查外掛程式名稱是否有拼寫錯誤。

檢查安裝摘要。如果它報告 `Run /reload-plugins to activate.`，請參閱[在不重新啟動的情況下套用外掛程式變更](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)以在您目前的工作階段中啟用外掛程式。 外掛程式啟用後，您已準備好[掃描和修復您的程式碼庫](https://code.claude.com/docs/zh-TW/claude-security#scan-and-fix-your-codebase)。

### 解除安裝外掛程式

若要移除外掛程式，從 `/plugin` 功能表解除安裝它，或在您的終端中執行 `claude plugin uninstall claude-security`。

## 掃描和修復您的程式碼庫

此外掛程式新增一個命令 `/claude-security`，它開啟其三個工作的功能表：掃描程式碼庫、掃描一組變更和建議修補程式。快樂路徑執行完整掃描，然後將其發現轉換為修補程式： 1 開啟 Claude Security 功能表 執行 `/claude-security` 並選擇 **Scan codebase** 。 2 選擇要掃描的內容 外掛程式首先讀取您的儲存庫，然後提供整個儲存庫或聚焦區域，每個選項都說明檔案計數和相對成本。選擇整個儲存庫，或回答「我不知道」，外掛程式會為您的儲存庫大小選擇合理的預設值。 3 確認執行 掃描可能需要一段時間，可能使用大量令牌，並需要 Claude Code 在完成時保持開啟。在您確認之前，不會執行任何操作。 4 讀取報告 掃描執行時，它會在每個階段開始時報告，詳細資訊可在 [`/workflows`](https://code.claude.com/docs/zh-TW/workflows) 下取得。結果進入您儲存庫中的時間戳記目錄，如[讀取掃描結果](https://code.claude.com/docs/zh-TW/claude-security#read-the-scan-results)中所述。 5 將發現轉換為修補程式 再次執行 `/claude-security` 並選擇 **Suggest patches** ，然後選擇要解決的發現。已檢查的修補程式進入報告的 `patches/` 資料夾；[修復發現](https://code.claude.com/docs/zh-TW/claude-security#fix-findings)涵蓋每個修補程式的建立和檢查方式。 6 應用您接受的修補程式 從您的 shell 使用 `git apply` 應用每個修補程式，在其自己的 pull request 中。修補程式永遠不會自動應用。 您不必從功能表開始：直接要求工作，作為命令的引數，例如 `/claude-security scan my branch`，或以純文字形式，例如「scan commit abc1234」。此外掛程式在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes)中效果最佳，這讓掃描的代理在每一步都無需權限提示即可進行。

### 僅掃描您的變更

當您的分支有其基礎沒有的提交時，`/claude-security` 功能表會提供僅掃描該差異的選項，以便您可以在合併前檢查分支。您也可以掃描您的一個開啟 pull request，或通過要求它來掃描單一提交，例如「scan commit abc1234」。僅掃描已提交的變更：首先提交或 stash 進行中的編輯，或執行完整掃描，它會讀取工作樹。 變更掃描需要 git 儲存庫；未版本控制目錄的完整掃描仍然有效。尋找您的開啟 pull request 是唯一到達網路的步驟，僅當您的工作階段已有權限執行 GitHub CLI 且 `gh` 已登入時才提供。

### 限制大型儲存庫的範圍

在大型儲存庫上，一次掃描一個區域而不是整個樹。選擇外掛程式提供的聚焦範圍之一，例如您的 API 層或您的驗證程式碼，執行會根據您選擇的內容調整大小。報告的涵蓋範圍部分說明檢查了什麼和未檢查什麼。隨時在不同區域執行另一次掃描。

### 讀取掃描結果

每次掃描都會將其結果寫入您儲存庫中的時間戳記 `CLAUDE-SECURITY-<timestamp>/` 目錄：

- **`CLAUDE-SECURITY-RESULTS.md`**：報告，包含每項發現的 ID，例如`F1` ，加上其影響、利用情景、嚴重性、信心和建議
- **`CLAUDE-SECURITY-RESULTS.jsonl`**：相同的發現以機器可讀形式，每行一個 JSON 物件
- **`CLAUDE-SECURITY-RESULTS.sarif`**：相同的發現作為[SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) 日誌，用於 GitHub 程式碼掃描和任何其他讀取標準的工具。掃描將發現分類在其 [CWE](https://cwe.mitre.org/) 弱點類別下
- **`CLAUDE-SECURITY-REVISION-<commit>.json`**：修訂戳記，記錄掃描了哪個提交、付出了多少努力、未提交的變更是否是掃描樹的一部分，以及執行的驗證程度如何，因此報告始終與其描述的程式碼相關聯。版本控制外的掃描在提交位置戳記`UNVERSIONED`

該目錄是掃描對您簽出的唯一變更，它帶有自己的 `.gitignore`，因此隨意的 `git add` 永遠不會將報告掃入提交。若要在歷史記錄中保留報告以進行稽核追蹤，刪除該一個 `.gitignore` 檔案並像任何其他檔案一樣提交目錄。 發現僅在獨立驗證代理分析它們後才出現在報告中，這使報告簡短且值得閱讀。掃描是非確定性的：同一程式碼的兩次掃描可能會發現不同的發現。定期執行掃描，並使用修訂戳記將每份報告歸因於它涵蓋的確切程式碼和設定。

## 修復發現

通過從 `/claude-security` 功能表選擇 **Suggest patches** 開始修復流程，或以純文字形式要求，例如「fix finding F3」，然後選擇要解決的報告中的發現。修補程式是針對已提交的程式碼建立的，報告必須仍然描述您擁有的程式碼：其程式碼已更改的發現會被跳過並附帶說明，外掛程式會提供新鮮掃描而不是從陳舊報告進行修補。每個修補程式都是在您儲存庫的暫存副本中起草的，因此您的原始檔案保持未觸及狀態，直到您自己應用修補程式。 在交付前，每個修補程式都由獨立於撰寫它的代理的代理檢查，當程式碼有測試時它會針對變更執行您的專案測試，並自行讀取差異以查看它可能引入的任何新內容。修補程式僅在該檢查可以保證變更解決了一項發現、不引入新漏洞且以其他方式保持行為不變時才被撰寫。當它無法保證全部三項時，您會得到一個簡短的說明而不是修補程式。

### 修補程式永遠不會自動應用

應用修補程式始終是您的決定。修補程式進入報告的 `patches/` 資料夾，每個發現一個 `F<n>.patch`，旁邊有說明變更的說明。從您的 shell 應用一個，或要求 Claude 應用它並開啟 pull request：

```
git apply CLAUDE-SECURITY-<timestamp>/patches/F1.patch

```

當修補的程式碼沒有測試時，修補程式的說明會說明這一點，因此您知道其檢查在沒有測試通過的情況下執行。在其自己的 pull request 中應用每個修補程式，以便可以獨立檢查和測試。

## 此外掛程式如何與其他安全工具配合

Claude Security 外掛程式是深度掃描層，在防禦深度堆疊中，與 [security guidance 外掛程式](https://code.claude.com/docs/zh-TW/security-guidance)、[`/security-review`](https://code.claude.com/docs/zh-TW/commands#all-commands)、[Code Review](https://code.claude.com/docs/zh-TW/code-review)、受管 [Claude Security](https://claude.com/product/claude-security) 產品和您現有的掃描器一起：

| 階段                                                                                                                                                               | 工具                                                                                   | 涵蓋內容                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 在工作階段中                                                                                                                                                       | [Security guidance 外掛程式](https://code.claude.com/docs/zh-TW/security-guidance)     | Claude 撰寫的程式碼中的常見漏洞，在同一工作階段中修復  |
| 按需，單一掃描                                                                                                                                                     | [`/security-review`](https://code.claude.com/docs/zh-TW/commands#all-commands)         | 目前分支上的一次性安全掃描                             |
| 按需，深度掃描                                                                                                                                                     | Claude Security 外掛程式                                                               | 儲存庫或差異的多代理掃描，具有獨立檢查的發現和修補程式 |
| 在 pull request 上                                                                                                                                                 | [Code Review](https://code.claude.com/docs/zh-TW/code-review)，Team 和 Enterprise 方案 | 具有完整程式碼庫上下文的多代理正確性和安全檢查         |
| 受管                                                                                                                                                               | [Claude Security](https://claude.com/product/claude-security)，Enterprise 方案         | 監控連接儲存庫的託管掃描                               |
| 在 CI 中                                                                                                                                                           | 您現有的靜態分析和依賴掃描器                                                           | 特定語言規則、供應鏈檢查和政策執行                     |
| 此外掛程式不會取代您現有的原始碼安全工具。與靜態分析、依賴掃描和程式碼檢查一起執行它：它以人類安全研究人員的方式推理您的程式碼，這補充了這些工具提供的確定性檢查。 |                                                                                        |                                                        |

## 疑難排解

**`/claude-security`功能表開啟時出現 Python 警告。** 此外掛程式需要 `python3` 3.9 或更新版本在您的 `PATH` 上。當它根本找不到 `python3` 時，功能表會警告在安裝一個之前 Claude Security 無法工作；當您 `PATH` 上的第一個 `python3` 較舊時，警告會命名它找到的版本。安裝 Python 3，或在您的 `PATH` 上放置較新的 `python3`，然後開始新工作階段。 **在 Fable 模型上掃描時，您可能會看到「safeguards flagged this message」通知。** 訊息會命名模型，例如「Fable 5.1’s safeguards flagged this message」。Fable 的網路安全安全分類器會標記某些請求，Claude Code 會通過[自動模型回退](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)在 Opus 模型上重新執行標記的請求。這是預期的，掃描應該仍然成功完成。

## 相關資源

若要深入了解此頁面涉及的部分：

- [Security guidance 外掛程式](https://code.claude.com/docs/zh-TW/security-guidance)：在同一工作階段中 Claude 撰寫程式碼時捕捉問題
- [Code Review](https://code.claude.com/docs/zh-TW/code-review)：設定 PR 時間多代理檢查
- [Claude Security](https://claude.com/product/claude-security)：監控連接儲存庫的受管服務
- [Claude Code 安全](https://code.claude.com/docs/zh-TW/security)：Claude Code 如何處理信任、權限和保護措施
- [探索和安裝外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins#official-anthropic-marketplace)：瀏覽其他官方外掛程式

是否 助手
