Code Review 處於研究預覽階段，適用於 [Team 和 Enterprise](https://claude.ai/admin-settings/claude-code) 訂閱。對於啟用了 [Zero Data Retention](https://code.claude.com/docs/zh-TW/zero-data-retention) 的組織，此功能不可用。在其他方案上，您仍然可以使用 `/code-review` 命令[在本地審查差異](https://code.claude.com/docs/zh-TW/code-review#review-a-diff-locally)。 Code Review 分析您的 GitHub pull request，並在發現問題的程式碼行上發佈內聯評論。一群專門的代理在您完整程式碼庫的背景下檢查程式碼變更，尋找邏輯錯誤、安全漏洞、破損的邊界情況和細微的迴歸。 發現結果按嚴重程度標記，不會批准或阻止您的 PR，因此現有的審查工作流程保持不變。您可以通過在存儲庫中添加 `CLAUDE.md` 或 `REVIEW.md` 文件來調整 Claude 標記的內容。 要在您自己的 CI 基礎設施中運行 Claude 而不是此託管服務，請參閱 [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions) 或 [GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd)。對於自託管 GitHub 實例上的存儲庫，請參閱 [GitHub Enterprise Server](https://code.claude.com/docs/zh-TW/github-enterprise-server)。 本頁涵蓋：

- [審查如何運作](https://code.claude.com/docs/zh-TW/code-review#how-reviews-work)
- [手動觸發審查](https://code.claude.com/docs/zh-TW/code-review#manually-trigger-reviews)，使用 `@claude review` 和 `@claude review always`
- [自訂審查](https://code.claude.com/docs/zh-TW/code-review#customize-reviews)，使用 `CLAUDE.md` 和 `REVIEW.md`
- [故障排除](https://code.claude.com/docs/zh-TW/code-review#troubleshooting)失敗的運行和缺失的評論
- [在本地審查差異](https://code.claude.com/docs/zh-TW/code-review#review-a-diff-locally)，使用 `/code-review` 命令

## 程式碼審查的運作方式

一旦擁有者為您的組織[啟用程式碼審查](https://code.claude.com/docs/zh-TW/code-review#set-up-code-review)，審查會在 PR 開啟時、每次推送時或手動請求時觸發，具體取決於儲存庫的設定行為。在任何模式下，評論 `@claude review` 會[在 PR 上啟動審查](https://code.claude.com/docs/zh-TW/code-review#manually-trigger-reviews)。 當審查執行時，多個代理會在 Anthropic 基礎設施上並行分析差異和周圍程式碼。每個代理會尋找不同類別的問題，然後驗證步驟會根據實際程式碼行為檢查候選項，以過濾掉誤判。結果會被去重、按嚴重程度排名，並作為內聯評論發佈在發現問題的特定行上，並在審查正文中提供摘要。如果未發現任何問題，程式碼審查會更新 GitHub 檢查執行以顯示未檢測到任何問題。Claude 也可能在 PR 上發佈簡短的確認評論。 審查的成本隨著 PR 的大小和複雜性而擴展，平均在 20 分鐘內完成。擁有者可以透過[分析儀表板](https://code.claude.com/docs/zh-TW/code-review#view-usage)監控審查活動和支出。

### 嚴重程度級別

每個發現都標記有嚴重程度級別：

| 標記                                                                                           | 嚴重程度 | 含義                                 |
| ---------------------------------------------------------------------------------------------- | -------- | ------------------------------------ |
| 🔴                                                                                             | 重要     | 應在合併前修復的錯誤                 |
| 🟡                                                                                             | 細節     | 輕微問題，值得修復但不會阻止         |
| 🟣                                                                                             | 預先存在 | 程式碼庫中存在但未由此 PR 引入的錯誤 |
| 發現包括可摺疊的擴展推理部分，您可以展開以了解 Claude 為什麼標記該問題以及它如何驗證了該問題。 |          |                                      |

### 對發現進行評分和回覆

Claude 的每條審查評論都已附加 👍 和 👎，因此兩個按鈕都會在 GitHub UI 中出現，以便一鍵評分。如果發現有用，請點擊 👍；如果發現錯誤或雜亂，請點擊 👎。Anthropic 在 PR 合併後收集反應計數，並使用它們來調整審查者。反應不會觸發重新審查或更改 PR 上的任何內容。 回覆內聯評論不會提示 Claude 回應或更新 PR。要對發現採取行動，請修復程式碼並推送。如果 PR 訂閱了推送觸發的審查，下一次執行會在問題修復時解決執行緒。要在不推送的情況下請求新審查，請將 `@claude review` 評論為[頂級 PR 評論](https://code.claude.com/docs/zh-TW/code-review#manually-trigger-reviews)。 要在不進行程式碼變更的情況下關閉發現，請解決其執行緒；回覆不會關閉它。

### 檢查執行輸出

除了內聯審查評論外，每次審查都會填充與您的 CI 檢查一起出現的 **Claude Code Review** 檢查執行。展開其 **Details** 連結以在一個地方查看每個發現的摘要，按嚴重程度排序：

| 嚴重程度                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 檔案:行                                                                                                                                             | 問題                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 🔴 重要                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `src/auth/session.ts:142`                                                                                                                           | 令牌重新整理與登出競爭，導致過時的工作階段保持活躍 |
| 🟡 細節                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `src/auth/session.ts:88`                                                                                                                            | `parseExpiry` 在格式錯誤的輸入上無聲地返回 0       |
| 每個發現也會在 **Files changed** 標籤中顯示為註解，直接標記在相關的差異行上。重要發現以紅色標記呈現，細節以黃色警告呈現，預先存在的錯誤以灰色通知呈現。註解和嚴重程度表獨立於內聯審查評論寫入檢查執行，因此即使 GitHub 在移動的行上拒絕內聯評論，它們仍然可用。 檢查執行始終以中立結論完成，因此它永遠不會透過分支保護規則阻止合併。如果您想根據程式碼審查發現來限制合併，請從檢查執行輸出中讀取嚴重程度細目。Details 文字的最後一行是機器可讀的評論，您的工作流程可以使用 `gh` 和 jq 進行解析。要找到檢查執行 ID，請使用 \`gh api repos/OWNER/REPO/commits/<commit-sha>/check-runs --jq '.check_runs[] | {id, name}'`列出提交的檢查執行，並取`Claude Code Review`執行的`id`。將 `OWNER`、`REPO`和`CHECK_RUN_ID\` 替換為您的儲存庫擁有者、儲存庫名稱和該 ID： |                                                    |

```
gh api repos/OWNER/REPO/check-runs/CHECK_RUN_ID \
  --jq '.output.text | split("bughunter-severity: ")[1] | split(" -->")[0] | fromjson'

```

這會傳回一個 JSON 物件，其中包含每個嚴重程度的計數，例如 `{"normal": 2, "nit": 1, "pre_existing": 0}`。`normal` 鍵保存重要發現的計數；非零值表示 Claude 發現了至少一個值得在合併前修復的錯誤。

### 程式碼審查檢查的內容

預設情況下，程式碼審查專注於正確性：會破壞生產的錯誤，而不是格式設定偏好或缺少的測試涵蓋範圍。您可以透過[新增指導檔案](https://code.claude.com/docs/zh-TW/code-review#customize-reviews)到您的儲存庫來擴展它檢查的內容。

## 設定 Code Review

管理員為組織啟用 Code Review 一次，並選擇要包含的存儲庫。 1 開啟 Claude Code 管理員設定 前往 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 並找到 Code Review 部分。您需要對 Claude 組織的管理員或主要管理員角色，以及在 GitHub 組織中安裝 GitHub Apps 的權限。 2 開始設定 點擊 **Setup** 。這開始 GitHub App 安裝流程。 3 安裝 Claude GitHub App 按照提示安裝 Claude GitHub App：選擇擁有您想要審查的存儲庫的 GitHub 組織，選擇應用可以存取的存儲庫，並批准請求的權限。若要審查 pull request，Claude 會透過應用的讀取存取權限讀取您的存儲庫內容，並透過其對 pull request 和檢查的寫入存取權限發佈評論和 [檢查運行](https://code.claude.com/docs/zh-TW/code-review#check-run-output)。在安裝期間，您授予由其他 Claude 功能（例如 [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions)）共享的更廣泛權限集；請參閱 [GitHub App 權限](https://code.claude.com/docs/zh-TW/github-actions#github-app-permissions) 以取得完整清單。 4 選擇存儲庫 選擇要為 Code Review 啟用的存儲庫。如果您看不到存儲庫，請確保您在安裝期間給予 Claude GitHub App 存取權限。您可以稍後添加更多存儲庫。 5 設定每個存儲庫的審查觸發器 設定完成後，Code Review 部分在表格中顯示您的存儲庫。對於每個存儲庫，使用 **Review Behavior** 下拉菜單選擇何時運行審查：

- **Once after PR creation** ：當 PR 開啟或標記為準備審查時，審查運行一次
- **After every push** ：在每次推送到 PR 分支時運行審查，在 PR 演變時捕捉新問題，並在您修復標記的問題時自動解決線程
- **Manual** ：開啟或推送到 PR 不會開始審查；評論 [`@claude review`](https://code.claude.com/docs/zh-TW/code-review#manually-trigger-reviews) 以請求審查，或 `@claude review always` 以同時訂閱 PR 以進行後續推送的審查

無論您選擇哪個選項，Claude 只有在有人評論 `@claude review` 時才會審查 [來自分支的 pull request](https://code.claude.com/docs/zh-TW/code-review#review-pull-requests-from-forks)。每次推送時審查運行最多的審查並花費最多。手動模式對於高流量存儲庫很有用，您想選擇特定 PR 進行審查，或者只在 PR 準備好時才開始審查您的 PR。 存儲庫表還顯示每個存儲庫基於最近活動的平均審查成本。使用行操作菜單按存儲庫打開或關閉 Code Review，或完全移除存儲庫。 要驗證設定，請開啟測試 PR。如果您選擇了自動觸發器，名為 **Claude Code Review** 的檢查運行會在幾分鐘內出現。如果您選擇了手動，在 PR 上評論 `@claude review` 以開始第一次審查。如果沒有檢查運行出現，請確認存儲庫列在您的管理員設定中，並且 Claude GitHub App 有權存取它。

## 手動觸發審查

評論命令可按需啟動審查。無論儲存庫的設定觸發器如何，它們都能運作，因此您可以使用它們在手動模式下選擇特定 PR 進行審查，或在其他模式下獲得立即重新審查。

| 命令                                                                                                                                                                                                        | 功能                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `@claude review`                                                                                                                                                                                            | 啟動單次審查，不訂閱 PR 以進行未來推送         |
| `@claude review always`                                                                                                                                                                                     | 啟動審查並訂閱 PR 以進行後續推送觸發的審查     |
| `@claude review once`                                                                                                                                                                                       | 與 `@claude review` 相同：啟動單次審查，不訂閱 |
| 當您希望每次後續推送到 PR 都啟動新的審查時，請使用 `@claude review always`，例如在設定為手動模式的儲存庫中的高優先級 PR 上。由於裸命令不訂閱 PR，您可以請求一次性的第二意見，而不改變後續推送是否觸發審查。 |                                                |
| 在 2026 年 7 月更新之前，`@claude review` 訂閱了 PR 以進行推送觸發的審查。如果您依賴該行為，請改為評論 `@claude review always`。`@claude review once` 仍然有效，其行為與裸命令相同。                        |                                                |
| 若要這些命令中的任何一個觸發審查：                                                                                                                                                                          |                                                |

- 將其作為頂層 PR 評論發佈，而不是在差異行上的內嵌評論
- 將命令放在評論的開頭，`once` 或 `always` 與命令的其餘部分在同一行
- 您必須對儲存庫具有寫入、維護或管理員權限
- PR 必須是開啟的

如果儲存庫屬於組織，且您在該組織中的成員身份是私密的（這是 GitHub 的預設設定），GitHub 不會將您識別為 Claude 的成員。Claude 可能仍會以 👀 回應您的評論，但除非您被直接新增到儲存庫作為協作者，否則它不會啟動審查，即使團隊或組織的基本權限給予您寫入存取權。若要修正此問題，[公開您的組織成員身份](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-membership-in-organizations/publicizing-or-hiding-organization-membership)或要求儲存庫管理員將您新增到儲存庫作為協作者。 與自動觸發器不同，手動觸發器在草稿 PR 上運作，因為明確的請求表示您希望立即進行審查，無論草稿狀態如何。 如果該 PR 上已有審查正在進行，請求將排隊等待進行中的審查完成。您可以透過 PR 上的檢查執行來監控進度。

### 審查來自複製儲存庫的拉取請求

Claude 不會自動審查來自複製儲存庫的拉取請求，無論儲存庫的**審查行為** 設定如何。若要啟動一個，請在拉取請求上評論 `@claude review`。[評論命令的要求](https://code.claude.com/docs/zh-TW/code-review#manually-trigger-reviews)仍然適用，您需要的寫入存取權是針對基礎儲存庫，而不是複製儲存庫。 若要獲得複製儲存庫拉取請求的另一次審查，請發佈新的 `@claude review` 評論。`@claude review always` 也有效，但不會訂閱拉取請求以進行後續推送上的審查。除了評論命令外，沒有其他方式可以在複製儲存庫拉取請求上啟動審查：

- 在檢查執行上點擊**重新執行** 不會啟動審查
- 推送新提交不會啟動審查，即使在設定為**每次推送後** 的儲存庫中也不會

## 自訂審查

Code Review 從您的儲存庫讀取兩個檔案來指導它標記的內容。它們在影響審查的強度上有所不同：

- **`CLAUDE.md`**：Claude Code 用於所有任務（不僅是審查）的共享專案指示。Code Review 將其作為專案背景讀取，並將新引入的違規標記為 nit。
- **`REVIEW.md`**：僅用於審查的指示，提供給尋找和驗證發現的代理，並由排名和報告發現的代理查詢。使用它來說明您的團隊想要標記什麼、以什麼嚴重程度標記，以及如何報告發現。

### CLAUDE.md

Code Review 讀取您儲存庫的 `CLAUDE.md` 檔案，並將新引入的違規視為[nit 級別](https://code.claude.com/docs/zh-TW/code-review#severity-levels)的發現。這是雙向工作的：如果您的 PR 以使 `CLAUDE.md` 陳述過時的方式更改程式碼，Claude 會標記文件需要更新。 Claude 在目錄階層的每個級別讀取 `CLAUDE.md` 檔案，因此子目錄的 `CLAUDE.md` 中的規則僅適用於該路徑下的檔案。有關 `CLAUDE.md` 如何運作的更多資訊，請參閱[記憶文件](https://code.claude.com/docs/zh-TW/memory)。 對於您不想應用於一般 Claude Code 工作階段的審查特定指導，請改用 [`REVIEW.md`](https://code.claude.com/docs/zh-TW/code-review#review-md)。

### REVIEW.md

`REVIEW.md` 是位於您儲存庫根目錄的檔案，可將 Code Review 調整為適合您的儲存庫。審查管道中尋找和驗證發現的代理會收到其內容作為您儲存庫的審查指示，以及 Code Review 的預設審查指導，排名和報告發現的代理在確定嚴重程度和撰寫審查之前會查詢它。 將您想要強制執行的規則直接放在 `REVIEW.md` 中。

#### 您可以調整的內容

`REVIEW.md` 是自由格式的 markdown，因此任何您可以表達為審查指示的內容都在範圍內。下面的模式在實踐中影響最大。 **嚴重程度** ：重新定義 🔴 Important 對您的儲存庫的含義。預設校準針對生產程式碼；文件儲存庫、設定儲存庫或原型可能需要更狹隘的定義。明確說明哪些發現類別是 Important，哪些最多是 Nit。您也可以朝另一個方向升級，例如將任何 `CLAUDE.md` 違規視為 Important，而不是預設的 nit。 **Nit 數量** ：限制單個審查發佈的 🟡 Nit 評論數量。散文和設定檔案可以永遠被打磨。像「最多報告五個 nit，在摘要中提及其餘的計數」這樣的上限可以保持審查的可操作性。 **跳過規則** ：列出 Claude 應該不發佈任何發現的路徑、分支模式和發現類別。常見的候選項是生成的程式碼、lockfile、供應商依賴項和機器編寫的分支，以及您的 CI 已經強制執行的任何內容，如 linting 或拼寫檢查。對於值得進行某些審查但不需要完全審查的路徑，設定更高的標準，而不是完全跳過：「在 `scripts/` 中，僅在接近確定且嚴重時報告。」 **儲存庫特定檢查** ：新增您想在每個 PR 上標記的規則，例如「新 API 路由必須有整合測試。」因為 `REVIEW.md` 直接到達每個發現和驗證代理，這些比長 `CLAUDE.md` 中的相同規則更可靠地著陸。 **驗證標準** ：在發佈發現類別之前需要證據。例如，「行為聲明需要來源中的 `file:line` 引用，而不是從命名推斷」會減少虛假正面，否則會使作者往返一次。 **重新審查收斂** ：告訴 Claude 當 PR 已經被審查時如何表現。像「在第一次審查後，抑制新的 nit 並僅發佈 Important 發現」這樣的規則會阻止單行修復因風格而到達第七輪。 **摘要形狀** ：要求審查正文以單行計數開頭，例如 `2 factual, 4 style`，並在情況如此時以「no factual issues」開頭。作者想在詳細資訊之前了解工作的形狀。

#### 範例

此 `REVIEW.md` 為後端服務重新校準嚴重程度、限制 nit、跳過生成的檔案，並新增儲存庫特定檢查。

```
# Review instructions

## What Important means here

Reserve Important for findings that would break behavior, leak data,
or block a rollback: incorrect logic, unscoped database queries, PII
in logs or error messages, and migrations that aren't backward
compatible. Style, naming, and refactoring suggestions are Nit at
most.

## Cap the nits

Report at most five Nits per review. If you found more, say "plus N
similar items" in the summary instead of posting them inline. If
everything you found is a Nit, lead the summary with "No blocking
issues."

## Do not report

- Anything CI already enforces: lint, formatting, type errors
- Generated files under `src/gen/` and any `*.lock` file
- Test-only code that intentionally violates production rules

## Always check

- New API routes have an integration test
- Log lines don't include email addresses, user IDs, or request bodies
- Database queries are scoped to the caller's tenant

```

#### 保持專注

長度是有代價的：冗長的 `REVIEW.md` 會削弱最重要的規則。將其保持為改變審查行為的指示，並將一般專案背景留在 `CLAUDE.md` 中。

## 查看使用情況

前往 [claude.ai/analytics/code-review](https://claude.ai/analytics/code-review) 查看整個組織的 Code Review 活動。儀表板顯示：

| 部分                                                                                | 它顯示什麼                                     |
| ----------------------------------------------------------------------------------- | ---------------------------------------------- |
| PRs reviewed                                                                        | 在選定時間範圍內審查的 pull request 的每日計數 |
| Cost weekly                                                                         | Code Review 的每週支出                         |
| Feedback                                                                            | 因開發人員解決問題而自動解決的審查評論計數     |
| Repository breakdown                                                                | 每個存儲庫審查的 PR 計數和解決的評論           |
| 儀表板成本數字是用於監控活動的估計。如需發票準確的支出，請參閱您的 Anthropic 帳單。 |                                                |

## 定價

Code Review 根據 token 使用量計費。每次審查平均成本為 $15-25，根據 PR 大小、程式碼庫複雜性和需要驗證的問題數量而變化。Code Review 使用量透過[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)單獨計費，不計入您方案的包含使用量。 您選擇的審查觸發器會影響總成本：

- **PR 建立後一次** ：每個 PR 執行一次
- **每次推送後** ：在每次推送時執行，成本乘以推送次數
- **手動** ：在開啟或推送時不執行審查，因此成本僅來自有人要求的審查

在 PR 建立後一次或手動模式中，評論 `@claude review always` [將 PR 選入推送觸發的審查](https://code.claude.com/docs/zh-TW/code-review#manually-trigger-reviews)，因此在該評論後每次推送都會產生額外成本。在每次推送後模式中，推送已經觸發審查，因此訂閱不會改變每次推送的成本。評論 `@claude review` 會執行單次審查，無需訂閱未來的推送。Claude 只在有人評論 `@claude review` 時才審查[來自分支的提取請求](https://code.claude.com/docs/zh-TW/code-review#review-pull-requests-from-forks)，因此分支提取請求在任何模式下都不會產生每次推送的成本。 無論您的組織是否使用 Amazon Bedrock 或 Google Cloud 的 Agent Platform 來處理其他 Claude Code 功能，成本都會出現在您的 Anthropic 帳單上。若要為 Code Review 設定每月支出上限，請前往 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 並為 Claude Code Review 服務設定限制。 透過[分析](https://code.claude.com/docs/zh-TW/code-review#view-usage)中的每週成本圖表或管理員設定中的每個儲存庫平均成本欄位監控支出。

## 故障排除

審查運行是盡力而為的。失敗的運行永遠不會阻止您的 PR，但它也不會自動重試。本部分涵蓋如何從失敗的運行中恢復，以及在檢查運行報告您找不到的問題時在哪裡查看。

### 重新觸發失敗或超時的審查

當審查基礎設施遇到內部錯誤或超過其時間限制時，檢查運行完成，標題為 **Code review encountered an error** 或 **Code review timed out** 。結論仍然是中立的，因此沒有任何東西阻止您的合併，但沒有發現被發佈。 要再次運行審查，在 PR 上評論 `@claude review`。這啟動一個新的審查，不訂閱 PR 以進行未來推送。如果 PR 不是[來自分支](https://code.claude.com/docs/zh-TW/code-review#review-pull-requests-from-forks)，您可以改為在 GitHub 的 Checks 標籤中的 **Claude Code Review** 檢查上點擊 **Re-run** 。重新運行也會啟動一個新的審查，不訂閱 PR。

### 審查未運行，PR 顯示支出上限消息

當您的組織的月度支出上限達到時，Code Review 在 PR 上發佈單個評論，解釋審查被跳過。審查在下一個計費期開始時自動恢復，或當管理員在 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 提高上限時立即恢復。

### 查找未顯示為內聯評論的問題

如果檢查運行標題說發現了問題，但您在差異上看不到內聯審查評論，請在這些其他位置查看發現的位置：

- **Check run Details** ：在 Checks 標籤中的 Claude Code Review 檢查旁邊點擊 **Details** 。嚴重程度表列出每個發現及其文件、行和摘要，無論內聯評論是否被接受。
- **Files changed annotations** ：在 PR 上打開 **Files changed** 標籤。發現呈現為直接附加到差異行的註釋，與審查評論分開。
- **Review body** ：如果您在審查運行時推送到 PR，某些發現可能引用當前差異中不再存在的行。這些出現在審查正文文本中的 **Additional findings** 標題下，而不是作為內聯評論。

## 在本地審查差異

[`/code-review` 命令](https://code.claude.com/docs/zh-TW/commands)在您的終端中審查差異，無需安裝 GitHub App。它報告正確性錯誤和重用、簡化和效率清理。 `/review` 是 `/code-review` 的別名；在 v2.1.223 之前，它是一個單獨的命令，對 GitHub pull request 執行單次通過、唯讀審查。 1 執行 /code-review 從您正在工作的工作階段中，執行命令：

```
/code-review

```

它審查您分支相對於其上游的提交，加上任何未提交的變更，因此它需要在分支或工作樹中有工作才能有內容可報告。若要審查其他內容，請傳遞目標：檔案路徑、PR 編號、分支名稱或參考範圍，例如 `main...my-feature`。您也可以新增旗標：

- `--fix`：在審查後將發現結果應用到您的工作樹
- `--comment`：將發現結果作為內聯評論發佈在 GitHub pull request 上，或作為單一備註發佈在 GitLab merge request 上
- `--post`：在 `github.com` pull request 的 `ultra` 雲審查上，在啟動對話框中預先選擇將完成的發現結果發佈到 PR；請參閱[將發現結果發佈到 pull request](https://code.claude.com/docs/zh-TW/ultrareview#post-findings-to-the-pull-request)。需要 Claude Code v2.1.227 或更新版本

當您為 GitLab merge request 傳遞 `--comment` 時，Claude Code 透過 GitLab 的 `glab` CLI 發佈發現結果。需要 Claude Code v2.1.257 或更新版本。當 `glab` 未安裝時，Claude 會改為在終端中列印發現結果。將 merge request 作為其 URL 或 `!123` 參考傳遞。Claude Code 僅當簽出的來源在 `gitlab.com` 上時，才將裸數字或分支名稱視為 merge request。在自管理的 GitLab 執行個體上，傳遞 URL 或 `!123` 形式。 2 繼續工作 審查作為具有自己內容視窗的背景[子代理](https://code.claude.com/docs/zh-TW/sub-agents)執行，因此它不會填滿您的對話。發現結果在審查完成時到達您的對話。 3 根據發現結果採取行動 要求 Claude 修復審查發現的內容。如果您傳遞了 `--fix` 或 `--comment`，審查已經應用或發佈了其發現結果。 Claude 在這兩個執行中都將發現結果報告為回覆中的文字，即使主應用程式要求發現結果清單：

- 在終端工作階段中，其中 `/code-review` 作為[分叉子代理](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)執行審查
- 在具有文字或 JSON 輸出的 `-p` 執行中

在要求發現結果清單的主應用程式中，例如[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop)，Claude 透過 [`ReportFindings` 工具](https://code.claude.com/docs/zh-TW/tools-reference)報告審查的發現結果。Claude Code 將報告呈現為發現結果清單，每個項目顯示檔案位置、單句摘要和類別標籤，例如當發現結果包含時的 `correctness`。主應用程式要求適用於每個努力級別，需要 Claude Code v2.1.218 或更新版本。 當 Claude 稍後在工作階段中修復報告的發現結果時，它會再次報告它們，Claude Code 會將更新的發現結果清單中的每個發現結果標記為已修復、已跳過或無需變更。

### 審查讀取和編輯的內容

審查遵循您的 `CLAUDE.md`，就像任何 Claude Code 工作階段一樣，但它不讀取 [`REVIEW.md`](https://code.claude.com/docs/zh-TW/code-review#review-md)。背景審查在您工作階段的[檢查點](https://code.claude.com/docs/zh-TW/checkpointing#subagent-edits-not-restored)之外應用其 `--fix` 編輯，因此 `/rewind` 不會撤銷它們；使用 git 來還原它們。當審查[在前景中執行](https://code.claude.com/docs/zh-TW/code-review#run-in-the-foreground)時，它在您自己的回合期間編輯您的工作樹，因此 `/rewind` 照常還原其編輯。

### 調整努力和引數

傳遞[努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)以權衡覆蓋範圍和信心。在 `low` 和 `medium` 時，審查僅報告它最有信心的發現結果，因此您看到的誤報較少；`high` 到 `max` 擴大覆蓋範圍，可能包括審查不太確定的發現結果。 當您未輸入級別時，審查會重用您上次輸入的 `low` 到 `max` 級別，即使在較早的工作階段中，Claude Code 會顯示通知，例如 `重用 high 努力，您上次輸入的級別`。輸入級別，例如 `/code-review high`，以變更稍後執行重用的內容；您在非互動式 `-p` 執行中傳遞的級別不會更新它。`ultra` 既不更新也不使用記住的級別。如果您從未輸入過級別，審查會使用工作階段的當前努力。在 v2.1.223 之前，沒有級別的 `/code-review` 始終使用工作階段的當前努力。 在努力級別和旗標之後，Claude Code 以以下兩種方式之一讀取該行的其餘部分：

- **不使用`ultra`** ：左邊的所有內容都是審查目標，即使它以另一個命令名稱開頭。`/code-review /fix-issue 123` 以 `/fix-issue 123` 作為目標文字進行審查，而不是將 `/fix-issue` 作為第二個[堆疊技能](https://code.claude.com/docs/zh-TW/skills#pass-arguments-to-skills)載入。在 v2.1.218 之前，堆疊在 `/code-review` 之後的命令會展開為其自己的技能。
- **使用`ultra`** ：Claude Code 將單個單詞讀取為基礎分支或 PR 編號，並將不命名分支或 PR 的較長文字轉換為[附加到審查的備註](https://code.claude.com/docs/zh-TW/ultrareview#pass-a-request-in-plain-words)。`/code-review ultra check my auth changes` 審查您的當前分支，Claude 將發現結果與您的備註相關聯。

### 在前景中執行

審查預設在背景中執行；在 v2.1.218 之前，它在您的對話中執行。在以下情況下，它改為在前景中執行：

- 您在較早的審查仍在進行時再次執行 `/code-review`
- 您以非互動式模式執行它，使用 `-p` 旗標或 Agent SDK；Claude Code 等待審查並在回應中包含發現結果，除了 `ultra`，它[啟動雲審查而不等待](https://code.claude.com/docs/zh-TW/code-review#escalate-to-ultrareview)
- 您將 [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1`，這也會關閉所有其他背景工作功能

### 讓 Claude 開始審查

Claude 可以自行開始 `/code-review`。要求它以純文字審查您的變更，它可以執行技能而無需您輸入命令，[排程工作](https://code.claude.com/docs/zh-TW/scheduled-tasks)以 `/code-review` 作為其提示執行審查。 排程工作永遠不會啟動[雲審查](https://code.claude.com/docs/zh-TW/code-review#escalate-to-ultrareview)，因此排程 `/code-review` 時不使用 `ultra` 引數。 若要在保持 `/code-review` 可供您輸入的同時停止 Claude 和排程工作開始審查，請將 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 項目新增到[設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)，例如 `~/.claude/settings.json`：

```
{
  "skillOverrides": {
    "code-review": "user-invocable-only"
  }
}

```

在 v2.1.246 之前，Claude 僅在從 Anthropic 擷取的功能旗標開啟它的地方自行開始 `/code-review`。在[不擷取功能旗標的工作階段](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)中，`/code-review` 僅在您輸入時執行，排程的 `/code-review` 作為純文字到達 Claude。

### 升級到 ultrareview

`/code-review ultra --fix` 在雲中執行更深入的 [ultrareview](https://code.claude.com/docs/zh-TW/ultrareview)，然後在它們回到您的工作階段時將其發現結果應用到您的工作樹。 Ultrareview 使用其自己的範圍：您的當前分支相對於儲存庫的預設分支，加上工作樹中的任何未提交和已暫存變更。對於命名為認證或金鑰的檔案（例如 `.env` 和 `*.tfvars` 檔案），Claude Code 遵循[將本地儲存庫上傳到雲工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-local-repositories-without-github)的規則。傳遞分支名稱，例如 `/code-review ultra develop`，以與不同的基礎進行比較。 當目標是 `github.com` pull request 時，您可以讓 Claude[將完成的發現結果發佈到 PR](https://code.claude.com/docs/zh-TW/ultrareview#post-findings-to-the-pull-request)作為來自您 GitHub 帳戶的評論。需要 Claude Code v2.1.227 或更新版本。 Ultrareview 需要使用 claude.ai 帳戶進行身份驗證，在 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 上不可用，或對於啟用了零資料保留的組織不可用。當 ultrareview 不可用時，`/code-review ultra` 會在您的工作階段中執行本地審查。 若要從指令碼或 CI 開始雲審查，請執行 `claude -p '/code-review ultra'`。Claude Code 啟動審查並列印用於追蹤它的連結。需要 Claude Code v2.1.218 或更新版本。 當審查會計費[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)時，Claude Code 在啟動前停止，因為計費確認需要互動式工作階段。改為執行 [`claude ultrareview` 子命令](https://code.claude.com/docs/zh-TW/ultrareview#run-ultrareview-non-interactively)；透過執行它，您同意該費用。 該命令在 v2.1.147 之前被命名為 `/simplify`，當時它預設應用修復。`/simplify` 執行單獨的僅清理審查，該審查應用修復而不尋找錯誤。如果您編寫了 `/simplify` 用於尋找錯誤，請切換到 `/code-review --fix`。

## 相關資源

- [Commands](https://code.claude.com/docs/zh-TW/commands)：在本地 Claude Code 工作階段中運行 `/code-review` 以在推送前檢查差異
- [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions)：在您自己的 GitHub Actions 工作流中運行 Claude，以實現超越程式碼審查的自訂自動化
- [GitLab CI/CD](https://code.claude.com/docs/zh-TW/gitlab-ci-cd)：GitLab 管道的自託管 Claude 集成
- [Memory](https://code.claude.com/docs/zh-TW/memory)：`CLAUDE.md` 文件如何在 Claude Code 中工作
- [Analytics](https://code.claude.com/docs/zh-TW/analytics)：追蹤超越程式碼審查的 Claude Code 使用情況
- [How Anthropic secures its AI-native software development lifecycle](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle)：自動化審查如何作為 Anthropic 安全開發流程的一層

是否 助手
