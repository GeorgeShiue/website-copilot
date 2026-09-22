例行程序處於研究預覽階段。行為、限制和 API 表面可能會變更。 例行程序是一個已保存的 Claude Code 設定：一個提示、一個或多個存儲庫，以及一組 [connectors](https://code.claude.com/docs/zh-TW/mcp)，打包一次並自動運行。例行程序在 Anthropic 管理的雲端基礎設施上執行，或在您組織的 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) 上執行（當路由到該處時），因此當您的筆記本電腦關閉時它們仍會繼續運行。 每個例行程序可以附加一個或多個觸發器：

- **排程** ：按照每小時、每晚或每週等定期節奏運行，或在特定的未來時間運行一次
- **API** ：通過向每個例行程序端點發送帶有持有人令牌的 HTTP POST 來按需觸發
- **GitHub** ：自動回應存儲庫事件，例如拉取請求或發佈

單個例行程序可以組合觸發器。例如，PR 審查例行程序可以每晚運行、從部署腳本觸發，也可以對每個新 PR 做出反應。 例行程序在 Pro、Max、Team 和 Enterprise 計劃上可用。在 [claude.ai/code/routines](https://claude.ai/code/routines) 創建和管理它們，或使用 CLI 中的 `/schedule` 命令。 Team 和 Enterprise 擁有者可以在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 的例行程序切換中為所有成員禁用例行程序。禁用後，現有例行程序停止運行，成員無法創建新的。 本頁涵蓋創建例行程序、設定每種觸發器類型、管理運行以及使用限制如何應用。

## 示例用例

每個示例將觸發器類型與例行程序適合的工作類型配對：無人值守、可重複且與明確結果相關。 **待辦事項維護。** 排程觸發器每個工作日晚上針對您的問題追蹤器通過 connector 運行。例行程序讀取自上次運行以來打開的問題、應用標籤、根據引用的代碼區域分配所有者，並將摘要發佈到 Slack，以便團隊以整理好的隊列開始新的一天。 **警報分類。** 您的監控工具在錯誤閾值被超過時調用例行程序的 API 端點，將警報正文作為 `text` 傳遞。例行程序的提示告訴 Claude 調查警報中的火警負載，因此它提取堆棧追蹤、將其與存儲庫中的最近提交相關聯，並打開一個帶有建議修復和返回警報鏈接的草稿拉取請求。值班人員審查 PR 而不是從空白終端開始。 **定製代碼審查。** GitHub 觸發器在 `pull_request.opened` 上運行。例行程序應用您團隊自己的審查檢查清單，為安全性、性能和風格問題留下內聯評論，並添加摘要評論，以便人工審查者可以專注於設計而不是機械檢查。 **部署驗證。** 您的 CD 管道在每次生產部署後調用例行程序的 API 端點。例行程序針對新構建運行煙霧測試、掃描錯誤日誌以查找回歸，並在部署窗口關閉前向發佈頻道發佈是否可以部署。 **文件漂移。** 排程觸發器每週運行。例行程序掃描自上次運行以來合併的 PR、標記引用已更改 API 的文件，並針對文件存儲庫打開更新 PR 供編輯者審查。 **庫移植。** GitHub 觸發器在 `pull_request.closed` 上運行，篩選為一個 SDK 存儲庫中的合併 PR。例行程序將更改移植到另一種語言的並行 SDK，並打開匹配的 PR，使兩個庫保持同步，而無需人工重新實現每個更改。

## 建立例行工作

在 [claude.ai/code/routines](https://claude.ai/code/routines) 網頁、桌面應用程式或 CLI 中建立例行工作。這三個介面都會寫入同一個雲端帳戶，因此您在其中一個介面建立的例行工作會立即出現在其他介面中。在桌面應用程式的 **Code** 標籤中，按一下側邊欄或側邊欄的 **More** 選單中的 **Routines** ，然後按 **New routine** ，並選擇 **Cloud** ；選擇 **Local** 則會建立 [Desktop scheduled task](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)，它在您的機器上執行，而不是在雲端執行。 建立表單會設定例行工作的提示詞、儲存庫、環境、連接器和觸發器。 例行工作以完整的 Claude Code 雲端工作階段自主執行：沒有權限模式選擇器，工作階段執行 shell 命令、使用 [skills](https://code.claude.com/docs/zh-TW/skills) 提交到複製的儲存庫，並呼叫您包含的任何連接器，所有這些都無需停止以尋求批准，除了某些 [artifact](https://code.claude.com/docs/zh-TW/artifacts) 動作。 例行工作可以存取的內容由您選擇的儲存庫、[環境](https://code.claude.com/docs/zh-TW/cloud-environments)的網路存取和變數，以及您包含的連接器決定。將這些範圍限制在例行工作實際需要的內容。 當例行工作的排程或 **Run now** 啟動執行時，Claude 只有在以下所有條件都成立時，才會重新發佈現有的 artifact 而不詢問：

- 您可以編輯該 artifact，且它屬於您自己的組織
- 該 artifact 未公開共享，且未與特定人員或您的組織共享，且未選擇最新版本作為檢視者看到的版本
- 發佈只包含頁面，沒有支援檔案或任何其他新增內容，且不會強制覆蓋較新的版本
- 該頁面不包含超出頁面範圍的授權，例如 [connector calls](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)

在所有其他情況下，包括發佈新的 artifact，Claude 會先詢問。當例行工作的工作是保持頁面最新時，請給它一個您已經發佈的 artifact。 例行工作屬於您的個人 claude.ai 帳戶。它們不與隊友共享，並且計入您帳戶的每日執行配額。例行工作透過您連接的 GitHub 身分或連接器執行的任何操作都會顯示為您：提交和拉取請求會帶有您的 GitHub 使用者，Slack 訊息、Linear 票證或其他連接器動作會使用您為這些服務連接的帳戶。

### 從網頁建立

1 開啟建立表單 造訪 [claude.ai/code/routines](https://claude.ai/code/routines) 並按一下 **New routine** 。 2 命名例行工作並撰寫提示詞 為例行工作提供描述性名稱，並撰寫 Claude 每次執行的提示詞。提示詞是最重要的部分：例行工作自主執行，因此提示詞必須是自包含的，並明確說明要做什麼以及成功的樣子。當觸發器觸發時，工作階段會收到例行工作的已儲存提示詞作為其指派的任務並執行它，而不是將其視為在對話中途到達的不受信任的內容。觸發器只證明提示詞是由您帳戶上的授權工作階段提前儲存的，因此觸發的提示詞不是即時使用者輸入，無法作為執行期間動作的批准或同意。工作階段在執行期間擷取的內容保持其正常處理。在 v2.1.213 之前，工作階段收到相同的提示詞，框架為不受信任的背景通知，可能拒絕對其採取行動。提示詞輸入包括模型選擇器。Claude 在每次執行時使用選定的模型。 3 選擇儲存庫 為 Claude 新增一個或多個 GitHub 儲存庫以在其中工作。每個儲存庫在執行開始時被複製，從預設分支開始。Claude 為其變更建立 `claude/` 前綴的分支。 4 選擇環境 為例行工作選擇 [cloud environment](https://code.claude.com/docs/zh-TW/cloud-environments)。環境控制雲端工作階段可以存取的內容：

- **Network access** ：設定每次執行期間可用的網際網路存取級別
- **Environment variables** ：提供 Claude 在每次執行期間可以使用的值。它們 [對使用該環境的任何人都可見](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)，因此在 Pro 和 Max 方案上，將 Claude 在執行期間呼叫的 API 的金鑰儲存為 [API credentials](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)。該部分也列出了永遠不會獲得認證的請求
- **Setup script** ：安裝例行工作需要的相依性和工具。結果是 [cached](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching)，因此指令碼不會在每個工作階段上重新執行

提供了 **Default** 環境，具有 **Trusted** 網路存取，它只允許 [default allowlist](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains) 的套件登錄、雲端提供者 API、容器登錄和常見開發網域透過工作階段的網路。您新增到例行工作的連接器透過 Anthropic 的伺服器存取其服務，因此不需要更改允許清單。如果您的例行工作需要直接存取您自己的服務或該清單外的網域，請在執行前編輯環境的 [network access](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)。若要使用單獨的環境，請先 [create one](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)。 5 選擇觸發器 在 **Select a trigger** 下，選擇例行工作的啟動方式。您可以選擇一個觸發器類型或組合多個。

- Schedule
- GitHub event
- API

為定期執行選擇預設頻率，或在特定時間戳記排程單次一次性執行。請參閱 [Add a schedule trigger](https://code.claude.com/docs/zh-TW/routines#add-a-schedule-trigger) 以了解時區處理、交錯、自訂 cron 間隔和一次性執行。 選擇儲存庫、要反應的事件和選擇性篩選器。請參閱 [Add a GitHub trigger](https://code.claude.com/docs/zh-TW/routines#add-a-github-trigger) 以取得支援事件和篩選欄位的完整清單。 在此選擇 **API** ，然後儲存例行工作。URL 和權杖在儲存例行工作後產生，因為它們取決於例行工作 ID。請參閱 [Add an API trigger](https://code.claude.com/docs/zh-TW/routines#add-an-api-trigger) 以複製 URL 並產生權杖。 6 檢查連接器 在表單底部的 **Connectors** 下，預設包括您所有連接的 [MCP connectors](https://code.claude.com/docs/zh-TW/mcp)。移除例行工作不需要的任何連接器：Claude 可以使用包含連接器的每個工具，包括寫入，而無需在執行期間要求權限。 7 建立例行工作 按一下 **Create** 。例行工作出現在清單中，並在下次其觸發器之一符合時執行。若要立即啟動執行，請按一下例行工作詳細資料頁面上的 **Run now** 。每次執行都會在您的其他工作階段旁邊建立新的工作階段，您可以在其中查看 Claude 執行的操作、檢查變更並建立拉取請求。

### 從 CLI 建立

在任何工作階段中執行 `/schedule` 以對話方式建立排程例行工作。您也可以直接傳遞描述，用於定期例行工作，例如 `/schedule daily PR review at 9am` 或一次性例行工作，例如 `/schedule clean up feature flag in one week`。Claude 會逐步執行網頁表單收集的相同資訊，然後將例行工作儲存到您的帳戶。該命令也可在別名 `/routines` 下使用。 成功的開始看起來像一次對話：Claude 在儲存前詢問有關排程、儲存庫和提示詞的後續問題。如果 Claude 改為回覆您需要驗證或無法連接到您的遠端 claude.ai 帳戶，則未建立例行工作；請參閱 [Troubleshooting](https://code.claude.com/docs/zh-TW/routines#troubleshooting)。 CLI 中的 `/schedule` 建立排程例行工作。若要新增 API 觸發器，請在 [claude.ai/code/routines](https://claude.ai/code/routines) 網頁上編輯例行工作。您可以從網頁或 CLI 新增 [GitHub trigger](https://code.claude.com/docs/zh-TW/routines#add-a-github-trigger)。CLI 路徑需要 Claude Code v2.1.225 或更新版本。 沒有排程觸發器的例行工作，例如僅由 API 呼叫或 GitHub 事件啟動的例行工作，沒有下次執行時間，當 Claude 儲存或更新它時，CLI 不會顯示任何時間。在 v2.1.211 之前，CLI 為這些例行工作報告了第 1 年的下次執行時間。

## 設定觸發條件

當其中一個觸發條件符合時，例行工作就會啟動。您可以將任何組合的排程、API 和 GitHub 觸發條件附加到同一個例行工作，並可以隨時從例行工作編輯表單的 **Select a trigger** 部分新增或移除它們。

### 新增排程觸發條件

排程觸發條件會按照循環週期執行例行工作，或在特定的未來時間執行一次。在 **Select a trigger** 部分選擇預設頻率：每小時、每天、工作日或每週。時間以您的本地時區輸入並自動轉換，因此無論雲端基礎設施位於何處，例行工作都會在該掛鐘時間執行。 執行可能會在排程時間之後幾分鐘開始，原因是錯開。每個例行工作的偏移量是一致的。 對於自訂間隔（例如每兩小時或每月的第一天），請在表單中選擇最接近的預設，然後在 CLI 中執行 `/schedule update` 以設定特定的 cron 表達式。最小間隔是一小時；執行頻率更高的表達式會被拒絕。

#### 排程一次性執行

一次性排程會在特定時間戳記時單次執行例行工作。使用它來提醒自己本週稍後、在推出完成後開啟清理 PR，或在上游變更到達時啟動後續工作。例行工作執行後，它會自動停用，網頁 UI 會將其標記為 **Ran** 。若要再次執行，請編輯例行工作並設定新的一次性時間。 從 CLI 透過自然語言描述時間來建立一次性執行。Claude 會根據目前時間解析該短語，並在儲存前確認絕對時間戳記。

```
/schedule tomorrow at 9am, summarize yesterday's merged PRs

```

```
/schedule in 2 weeks, open a cleanup PR that removes the feature flag

```

與循環排程相同的本地到 UTC 轉換適用於一次性時間戳記。 一次性執行不計入每日例行工作執行上限。詳見 [Usage and limits](https://code.claude.com/docs/zh-TW/routines#usage-and-limits)。

### 新增 API 觸發條件

API 觸發條件為例行工作提供專用的 HTTP 端點。使用例行工作的持有人令牌 POST 到端點會啟動新的工作階段並傳回工作階段 URL。使用此功能將 Claude Code 整合到警報系統、部署管道、內部工具或任何可以進行已驗證 HTTP 請求的地方。 API 觸發條件從網頁新增到現有例行工作。CLI 目前無法建立或撤銷令牌。 1 Open the routine for editing 前往 [claude.ai/code/routines](https://claude.ai/code/routines)，點擊您想透過 API 觸發的例行工作，然後開啟例行工作名稱旁邊的選單並選擇 **Edit** 。 2 Add an API trigger 捲動到 **Instructions** 方塊下方的 **Select a trigger** 部分，點擊 **Add another trigger** ，然後選擇 **API** 。 3 Copy the URL and generate a token 模式視窗會顯示此例行工作的 URL 以及範例 curl 命令。複製 URL，然後點擊 **Generate token** 並立即複製令牌。令牌只會顯示一次，之後無法擷取，因此請將其儲存在安全的地方，例如您的警報工具的祕密存放區。 4 Call the endpoint 當您 POST 到 URL 時，在 `Authorization: Bearer` 標頭中傳送令牌。下方的 [Trigger a routine](https://code.claude.com/docs/zh-TW/routines#trigger-a-routine) 部分顯示完整範例。 每個例行工作都有自己的令牌，範圍限制為僅觸發該例行工作。若要輪換或撤銷它，請返回相同的模式視窗並點擊 **Regenerate** 或 **Revoke** 。

#### 觸發例行工作

將 POST 請求傳送到 `/fire` 端點，並在 `Authorization` 標頭中包含持有人令牌。請求本文接受選用的 `text` 欄位，用於執行特定的內容，例如警報本文或失敗的日誌，與例行工作的已儲存提示一起傳遞給例行工作。該值是自由格式文字，不會被解析：如果您傳送 JSON 或其他結構化承載，例行工作會將其作為字面字串接收。 `text` 值不會作為裸訊息到達例行工作。它會到達並包裝在 `<routine-fire-payload>` 區塊中，該區塊將其標記為不受信任的資料，並告訴 Claude 除非例行工作自己的提示說明，否則不要遵循其中的指示。與網頁 UI 中的 **Run now** 提供的文字相同的包裝也適用。 這表示例行工作的已儲存提示必須選擇對觸發文字採取行動：編寫提示以明確參考承載，例如「調查例行工作觸發承載區塊中描述的警報」，或例行工作將文字視為惰性內容。任何持有持有人令牌的人都可以傳送 `text`，因此包裝使得來自洩露令牌的觸發文字到達時被標記為不受信任的資料，而不是作為對您例行工作的直接指示。 下面的範例從 shell 觸發例行工作。顯示的例行工作 ID 和令牌是預留位置：將其替換為您在 [adding the API trigger](https://code.claude.com/docs/zh-TW/routines#add-an-api-trigger) 時複製的 URL 和令牌，否則請求會失敗並出現 `401` 驗證錯誤：

```
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_01ABCDEFGHJKLMNOPQRSTUVW/fire \
  -H "Authorization: Bearer sk-ant-oat01-xxxxx" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'

```

成功的請求會傳回包含新工作階段 ID 和 URL 的 JSON 本文：

```
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}

```

在瀏覽器中開啟工作階段 URL 以即時觀看執行、檢閱變更或手動繼續對話。 `/fire` 端點在 `experimental-cc-routine-2026-04-01` 測試版標頭下發佈。在功能處於研究預覽期間，請求和回應形狀、速率限制和令牌語義可能會變更。破壞性變更會在新的日期測試版標頭版本後發佈，最近的兩個先前標頭版本會繼續運作，以便呼叫者有時間進行遷移。

#### API 參考

如需完整的 API 參考，包括所有錯誤回應、驗證規則和欄位限制，請參閱 Claude Platform 文件中的 [Trigger a routine via API](https://platform.claude.com/docs/en/api/claude-code/routines-fire)。 `/fire` 端點僅適用於 claude.ai 使用者，不是 Claude Platform API 表面的一部分。

### 新增 GitHub 觸發條件

GitHub 觸發條件會在連線存放庫上發生符合的事件時自動啟動新的工作階段。Claude Code 不會跨事件重複使用工作階段，因此兩個 PR 更新會產生兩個獨立的工作階段。 在研究預覽期間，GitHub webhook 事件受到每個例行工作和每個帳戶的每小時上限限制。超過限制的事件會被捨棄，直到時間視窗重設。在 [claude.ai/code/routines](https://claude.ai/code/routines) 查看您目前的限制。 Claude GitHub App 必須安裝在您想訂閱的存放庫上，無論您從哪個表面設定觸發條件。

- 從網頁 UI 設定 GitHub 觸發條件，當應用程式遺失時會提示您安裝它。按照下面的步驟在網頁上設定一個。
- 從 CLI，先從 [GitHub App page](https://github.com/apps/claude) 安裝應用程式，然後要求 Claude 將 GitHub 觸發條件附加到現有例行工作，例如 `/schedule add a GitHub trigger to my nightly review for pull requests opened in acme/webapp`。CLI 路徑需要 Claude Code v2.1.225 或更新版本。當 Claude 新增觸發條件時，它會回覆觸發條件觸發的例行工作的連結。

1 Open the routine for editing 前往 [claude.ai/code/routines](https://claude.ai/code/routines)，點擊例行工作，然後開啟例行工作名稱旁邊的選單並選擇 **Edit** 。 2 Add a GitHub event trigger 捲動到 **Select a trigger** 部分，點擊 **Add another trigger** ，然後選擇 **GitHub event** 。 在 CLI 中執行 `/web-setup` 會授予用於複製的存放庫存取權限，但不會安裝 Claude GitHub App，也不會啟用 webhook 傳遞。 3 Configure the trigger 選擇存放庫，從 [supported events](https://code.claude.com/docs/zh-TW/routines#supported-events) 清單中選擇事件，並選擇性地新增篩選條件。儲存觸發條件。

#### 支援的事件

GitHub 觸發條件可以訂閱以下任一事件類別。在每個類別中，您可以選擇特定的動作，例如 `pull_request.opened`，或對類別中的所有動作做出反應。

| Event        | Triggers when                                          |
| ------------ | ------------------------------------------------------ |
| Pull request | 當 PR 被開啟、關閉、指派、標記、同步或以其他方式更新時 |
| Release      | 當發行版本被建立、發佈、編輯或刪除時                   |

#### 篩選提取請求

使用篩選條件來縮小哪些提取請求啟動新的工作階段。所有篩選條件都必須符合才能觸發例行工作。可用的篩選欄位為：

| Filter                                                                                                                                                                                                                                                                                                                                                                        | Matches                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| Author                                                                                                                                                                                                                                                                                                                                                                        | PR 作者的 GitHub 使用者名稱 |
| Title                                                                                                                                                                                                                                                                                                                                                                         | PR 標題文字                 |
| Body                                                                                                                                                                                                                                                                                                                                                                          | PR 描述文字                 |
| Base branch                                                                                                                                                                                                                                                                                                                                                                   | PR 目標的分支               |
| Head branch                                                                                                                                                                                                                                                                                                                                                                   | PR 來自的分支               |
| Labels                                                                                                                                                                                                                                                                                                                                                                        | 套用到 PR 的標籤            |
| Is draft                                                                                                                                                                                                                                                                                                                                                                      | PR 是否處於草稿狀態         |
| Is merged                                                                                                                                                                                                                                                                                                                                                                     | PR 是否已合併               |
| 每個篩選條件將欄位與運算子配對：等於、包含、開頭為、是其中之一、不是其中之一或符合 regex。 `matches regex` 運算子測試整個欄位值，而不是其中的子字串。若要符合任何包含 `hotfix` 的標題，請寫入 `.*hotfix.*`。沒有周圍的 `.*`，篩選條件只符合完全是 `hotfix` 且前後沒有任何內容的標題。對於不使用 regex 語法的字面子字串符合，請改用 `contains` 運算子。 一些篩選條件組合範例： |                             |

- **Auth module review** ：基礎分支 `main`，頭部分支包含 `auth-provider`。將任何涉及驗證的 PR 傳送給專注的審查者。
- **Ready-for-review only** ：is draft 是 `false`。跳過草稿，以便例行工作僅在 PR 準備好進行審查時執行。
- **Label-gated backport** ：標籤包括 `needs-backport`。僅當維護者標記 PR 時才觸發移植到另一個分支的例行工作。

## 管理例行程序

點擊列表中的例行程序以打開其詳細資訊頁面。詳細資訊頁面顯示例行程序的存儲庫、connectors、提示、排程、API 令牌、GitHub 觸發器和過去運行的列表。

### 查看和交互運行

點擊任何運行以將其作為完整會話打開。從那裡您可以看到 Claude 做了什麼、審查更改、建立拉取請求或繼續對話。每個運行會話的工作方式與任何其他會話相同：使用會話標題旁邊的下拉菜單重新命名、存檔或刪除它。 運行列表中的綠色狀態表示會話已啟動並退出，沒有基礎設施錯誤。這並不意味著您提示中的任務成功。打開運行以讀取記錄並確認 Claude 實際上做了什麼。被阻止的網路請求、缺失的 connector 工具和任務級別的失敗都會在那裡顯示，而不是在狀態指示器中。

### 編輯和控制例行程序

從例行程序詳細資訊頁面，您可以：

- 點擊 **Run now** 立即開始運行，無需等待下一個排程時間。您可以選擇性地提供運行特定的文字，該文字以與 API 觸發器的 `text` 欄位相同的方式到達例行程序。
- 使用頁面頂部的開/關切換暫停或恢復排程。暫停的例行程序保留其設定但不運行，直到您重新啟用它們。
- 打開例行程序名稱旁邊的菜單並選擇 **Edit** 以變更名稱、提示、存儲庫、環境、connectors 或例行程序的任何觸發器。**Select a trigger** 部分是您新增或移除排程、API 令牌和 GitHub 事件觸發器的地方。
- 打開相同的菜單並選擇 **Delete** 以刪除例行程序。

### 從 CLI 管理例行程序

CLI 支援管理現有的例行程序。執行 `/schedule list` 以查看所有例行程序，執行 `/schedule update` 以變更一個，或執行 `/schedule run` 以立即觸發它。 您也可以詢問例行程序的運行歷史記錄，例如 `/schedule why did my nightly review do nothing this morning?`。Claude 列出例行程序的最近運行及其狀態和 [在網路上打開每個運行](https://code.claude.com/docs/zh-TW/routines#view-and-interact-with-runs) 的連結，並讀取運行的日誌以解釋發生了什麼，包括工具錯誤、權限拒絕和最終結果。需要 Claude Code v2.1.227 或更新版本。

### 存儲庫和分支權限

例行程序需要 GitHub 存取權限來複製存儲庫。當您使用 `/schedule` 從 CLI 建立例行程序時，Claude 檢查您的帳戶是否具有您執行它的存儲庫的 GitHub 存取權限，如果沒有，則新增一個設定注記，說明如何授予它。請參閱 [GitHub authentication options](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options) 以了解授予存取權限的兩種方式。 如果您的 GitHub 連線在運行到期時遺失或過期，例行程序會跳過運行，最多 72 小時。在該時間窗口內重新連接 GitHub，例行程序會自動恢復。72 小時後仍未連接，例行程序會關閉，您在重新連接 GitHub 後將其重新打開。 您新增的每個存儲庫在每次運行時都會被複製。Claude 從存儲庫的預設分支開始，除非您的提示另有指定。 Claude 將其工作推送到以 `claude/` 為前綴的分支，這些分支始終被接受。當您的提示指示 Claude 推送到另一個分支時，Claude Code 會先檢查推送，如果以下任何情況為真，則拒絕它：

- 該分支在 GitHub 上受保護
- 其他人有一個來自該分支的開放拉取請求
- 該分支包含由您以外的人編寫的提交

### Connectors

例行程序可以使用您連接的 MCP connectors 在每次運行期間讀取和寫入外部服務。例如，分類支援請求的例行程序可能從 Slack 頻道讀取並在 Linear 中建立問題。 Connectors 是您帳戶上的 [claude.ai integrations](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)。您在 CLI 中使用 `claude mcp add` 本地新增的 MCP 伺服器儲存在您的機器上而不是您的 claude.ai 帳戶上，因此它們不會出現在 connectors 列表中。要在例行程序中使用其中一個伺服器，請在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 新增它作為 connector，或在已提交的 [`.mcp.json`](https://code.claude.com/docs/zh-TW/mcp#project-scope) 中宣告它，以便它是複製存儲庫的一部分。 當您建立例行程序時，預設情況下包括您所有目前連接的 connectors。移除任何不需要的以限制 Claude 在運行期間可以存取的工具。您也可以直接從例行程序表單新增 connectors。 要在例行程序表單外管理或新增 connectors，請造訪 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 或在 CLI 中使用 `/schedule update`。

### 環境和網路存取

每個例行程序使用 [cloud environment](https://code.claude.com/docs/zh-TW/cloud-environments) 來控制網路存取、環境變數和設定指令碼。例行程序在每次運行時繼承環境的網路策略。 **Default** 環境使用 **Trusted** 網路存取，它只允許 [預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains) 通過會話的網路。對該路徑上允許清單外的主機的請求失敗，返回 `403` 和 `x-deny-reason: host_not_allowed`。MCP connector 流量通過 Anthropic 的伺服器路由，而不是該路徑，因此您新增到例行程序的 connectors 無需將其主機新增到 **Allowed domains** 即可工作。移除您不需要的任何 connectors，詳見 [Connectors](https://code.claude.com/docs/zh-TW/routines#connectors)。 要允許其他網域上的一個您自己的環境，請遵循這些步驟。[organization-shared environment](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments) 在此處打開為唯讀，因此所有者從 [admin settings](https://claude.ai/admin-settings) 中的 **Cloud environments** 頁面變更其網路存取。 1 打開例行程序進行編輯 在例行程序的詳細資訊頁面上，打開例行程序名稱旁邊的菜單並選擇 **Edit** 。 2 打開環境選擇器 在 **Instructions** 框下方，選擇顯示您環境名稱的雲圖標，例如 **Default** 。 3 打開環境設定 將滑鼠懸停在列表中的環境上，然後點擊右側出現的設定圖標。 4 變更網路存取級別 在 **Update cloud environment** 對話框中，將 **Network access** 變更為 **Custom** 並在 **Allowed domains** 中輸入您的網域。勾選 **Also include default list of common package managers** 以在自訂網域旁邊保留 [預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)。選擇 **Full** 以獲得不受限制的存取。 5 儲存 點擊 **Save changes** 。新策略從下一次運行開始應用。 請參閱 [Network access](https://code.claude.com/docs/zh-TW/cloud-environments#network-access) 以了解存取級別和預設允許清單的詳細資訊。

## 使用和限制

例行程序以與互動式會話相同的方式消耗訂閱使用量。除了標準訂閱限制外，例行程序還有每個帳戶每天可以啟動多少次運行的每日上限。在 [claude.ai/code/routines](https://claude.ai/code/routines) 或 [claude.ai/settings/usage](https://claude.ai/settings/usage) 查看您目前的消耗和剩餘的每日例行程序運行。 當例行程序達到每日上限或您的訂閱使用限制時，啟用了使用額度的組織可以繼續在計量超額上運行例行程序。沒有使用額度，額外運行會被拒絕，直到時間窗口重置。在 [claude.ai/settings/usage](https://claude.ai/settings/usage) 啟用使用額度。在 Team 和 Enterprise 方案上，管理員在 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 為組織啟用使用額度。 一次性運行不計入每日例行程序運行上限。它們像任何其他會話一樣消耗您的常規訂閱使用量。 當您的訂閱暫停時，您的例行程序會被暫停並且不會運行。一旦您的訂閱再次啟用，請將它們重新開啟。

## 故障排除

### `/schedule` 返回「Unknown command」

當不滿足其中一項要求時，CLI 會隱藏 `/schedule`：命令菜單在您輸入時會顯示 `No commands match "/schedule"`，提交時會返回 `Unknown command: /schedule`，除了以下注明不同答案的情況外。 原因通常是以下之一：

- 您使用 Console API 金鑰、[Anthropic 設定檔或聯盟認證](https://code.claude.com/docs/zh-TW/authentication#anthropic-profiles-and-federation-credentials)，或雲端提供商（例如 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry）進行身份驗證。`/schedule` 需要 claude.ai 訂閱登入。使用 Console API 金鑰或設定檔時，且啟用功能旗標擷取，提交 `/schedule` 會改為顯示 `/schedule is available with Claude for Enterprise — ask your admin about migrating from API-key access`。使用雲端提供商登入時，您仍會看到 `Unknown command: /schedule`。如果在您的 shell 中設定了 `ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`，或在 `settings.json` 中設定了 `apiKeyHelper`，請先移除它，因為這些設定優先於 claude.ai 登入。設定檔或聯盟認證也會優先，因此請同時關閉該設定
- 您完全登出，沒有 API 金鑰或其他認證。啟用功能旗標擷取時，提交 `/schedule` 會顯示 `/schedule requires a claude.ai subscription. Run /login to sign in with your claude.ai account.` 在 v2.1.268 之前，登出的工作階段會顯示與 Console API 金鑰相同的 Claude for Enterprise 訊息
- 您在雲端工作階段中，提交 `/schedule` 會回答該命令在該環境中不可用。改為從 [web UI](https://claude.ai/code/routines) 管理例行程序
- 您的組織政策停用了[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，例行程序在其上執行。在此情況下，提交 `/schedule` 會回答 [`Cloud sessions are disabled by your organization's policy`](https://code.claude.com/docs/zh-TW/errors#cloud-sessions-are-disabled-by-your-organizations-policy)。在 v2.1.268 之前，它返回 `Unknown command: /schedule`
- Owner 為您的 Team 或 Enterprise 組織[關閉了例行程序](https://code.claude.com/docs/zh-TW/routines#routines-are-disabled-by-your-organizations-policy)。在 v2.1.227 之前，命令在此情況下仍會出現，而 claude.ai 會在 Claude 嘗試建立或執行例行程序時拒絕它

除非您的組織政策停用了例行程序或雲端工作階段，否則無論 CLI 如何配置，您都可以在 [claude.ai/code/routines](https://claude.ai/code/routines) 建立和管理例行程序。

### 「例行程序已被您的組織政策禁用」

您的 Team 或 Enterprise 組織中的 Owner 可能已在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 關閉了 **Routines** 切換。在 Claude Code v2.1.227 或更新版本上，相同的切換也會在 CLI 中隱藏 `/schedule`。這是一個伺服器端組織設定，因此無法從您的本地設定中覆蓋。請聯繫 Owner 為您的組織啟用例行程序。

## 相關資源

- [`/loop` 和會話內排程](https://code.claude.com/docs/zh-TW/scheduled-tasks)：在打開的 CLI 會話中排程本地任務
- [Desktop scheduled tasks](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)：在您的機器上運行的本地排程任務，可以訪問本地檔案
- [Cloud environments](https://code.claude.com/docs/zh-TW/cloud-environments)：為雲會話配置網路存取、環境變數和設定指令碼
- [Projects](https://code.claude.com/docs/zh-TW/claude-projects)：Claude 在平行雲會話中協調的進行中工作；從專案建立的例行工作會出現在其 **Routines** 標籤上
- [MCP connectors](https://code.claude.com/docs/zh-TW/mcp)：連接外部服務，如 Slack、Linear 和 Google Drive
- [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions)：在存儲庫事件上在您的 CI 管道中運行 Claude

是否 助手
