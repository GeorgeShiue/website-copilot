排程任務讓 Claude 按間隔自動重新執行提示。使用它們來輪詢部署、監督 PR、檢查長時間執行的建置，或在工作階段稍後提醒自己執行某些操作。若要改為對事件發生時做出反應而不是輪詢，請參閱 [Channels](https://code.claude.com/docs/zh-TW/channels)：您的 CI 可以直接將失敗推送到工作階段中。若要保持工作階段逐輪執行直到符合條件而不是按間隔執行，請參閱 [`/goal`](https://code.claude.com/docs/zh-TW/goal)。 任務的範圍限於工作階段：它們存在於目前的對話中，當您啟動新的對話時就會停止。使用 `--resume` 或 `--continue` 繼續會恢復任何尚未[過期](https://code.claude.com/docs/zh-TW/scheduled-tasks#seven-day-expiry)的任務，除了[限制](https://code.claude.com/docs/zh-TW/scheduled-tasks#limitations)下列出的任務。對於獨立於任何工作階段而存在的排程，請使用 [Routines](https://code.claude.com/docs/zh-TW/routines) 在雲端建立例行程序、設定 [Desktop 排程任務](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)，或使用 [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions)。

## 比較排程選項

Claude Code 提供三種方式來排程定期或一次性的工作：

|                                                                                                                                                                        | [Cloud](https://code.claude.com/docs/zh-TW/routines) | [Desktop](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks) | [`/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks)                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 執行位置                                                                                                                                                               | Cloud，預設由 Anthropic 管理                         | 您的機器                                                              | 您的機器                                                                                       |
| 需要機器開啟                                                                                                                                                           | 否                                                   | 是                                                                    | 是                                                                                             |
| 需要開啟的工作階段                                                                                                                                                     | 否                                                   | 否                                                                    | 是                                                                                             |
| 跨重新啟動持續存在                                                                                                                                                     | 是                                                   | 是                                                                    | 在 `--resume` 上復原，有[例外](https://code.claude.com/docs/zh-TW/scheduled-tasks#limitations) |
| 存取本機檔案                                                                                                                                                           | 否（全新複製）                                       | 是                                                                    | 是                                                                                             |
| MCP 伺服器                                                                                                                                                             | 每個工作配置的連接器                                 | [設定檔](https://code.claude.com/docs/zh-TW/mcp)和連接器              | 繼承自工作階段                                                                                 |
| 權限提示                                                                                                                                                               | 否（自主執行）                                       | 每個工作可設定                                                        | 繼承自工作階段                                                                                 |
| 可自訂排程                                                                                                                                                             | 透過 CLI 中的 `/schedule`                            | 是                                                                    | 是                                                                                             |
| 最小間隔                                                                                                                                                               | 1 小時                                               | 1 分鐘                                                                | 1 分鐘                                                                                         |
| 使用**雲端工作** 來執行應該在沒有您的機器的情況下可靠執行的工作。當您需要存取本機檔案和工具時，使用**Desktop 工作** 。使用 \*\*`/loop`\*\*進行工作階段期間的快速輪詢。 |                                                      |                                                                       |                                                                                                |

## 使用 /loop 重複執行提示

`/loop` [bundled skill](https://code.claude.com/docs/zh-TW/commands) 是在工作階段保持開啟的情況下重複執行提示的最快方式。間隔和提示都是選用的，您提供的內容決定了迴圈的行為方式。

| 您提供的內容                                                                                                                                                                                                                                                                  | 範例                        | 發生的情況                                                                                                                               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 間隔和提示                                                                                                                                                                                                                                                                    | `/loop 5m check the deploy` | 您的提示在[固定排程](https://code.claude.com/docs/zh-TW/scheduled-tasks#run-on-a-fixed-interval)上執行                                   |
| 僅提示                                                                                                                                                                                                                                                                        | `/loop check the deploy`    | 您的提示在 [Claude 選擇的間隔](https://code.claude.com/docs/zh-TW/scheduled-tasks#let-claude-choose-the-interval)上執行，每次迭代        |
| 僅間隔或無                                                                                                                                                                                                                                                                    | `/loop`                     | [內建維護提示](https://code.claude.com/docs/zh-TW/scheduled-tasks#run-the-built-in-maintenance-prompt)執行，或您的 `loop.md`（如果存在） |
| 您也可以傳遞一個 skill 作為提示，例如 `/loop 20m /review-pr 1234`，以在每次迭代時重新執行該 skill。排程的執行只會執行 Claude [允許自行叫用](https://code.claude.com/docs/zh-TW/skills#control-who-invokes-a-skill)的 skill。以下內容會以純文字形式傳達給 Claude，而不是執行： |                             |                                                                                                                                          |

- 內建命令，例如 `/permissions`、`/model` 或 `/clear`
- 標記為 [`disable-model-invocation: true`](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference) 的 skill，包括 bundled `/verify` skill
- 由 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 設定或 `Skill` [deny rule](https://code.claude.com/docs/zh-TW/skills#restrict-claude%E2%80%99s-skill-access) 從 Claude 隱藏的 skill
- [MCP prompts](https://code.claude.com/docs/zh-TW/mcp#use-mcp-prompts-as-commands)，例如 `/mcp__github__list_prs`

### 在固定間隔上執行

當您提供間隔時，Claude 會將其轉換為 cron 表達式、排程工作，並確認頻率和工作 ID。

```
/loop 5m check if the deployment finished and tell me what happened

```

間隔可以作為裸令牌（如 `30m`）在提示前面，或作為子句（如 `every 2 hours`）在後面。支援的單位為 `s`（秒）、`m`（分鐘）、`h`（小時）和 `d`（天）。 秒數會四捨五入到最近的分鐘，因為 cron 的粒度為一分鐘。不能均勻分割其單位的間隔（例如 `7m` 或 `90m`）會四捨五入到最近的整潔間隔，Claude 會告訴您它選擇了什麼。

### 讓 Claude 選擇間隔

當您省略間隔時，Claude 會動態選擇一個，而不是在固定的 cron 排程上執行。在每次迭代後，它會根據觀察到的情況選擇一個介於一分鐘到一小時之間的延遲：在建置完成或 PR 活躍時短暫等待，當沒有待處理項目時較長等待。選擇的延遲和原因會在每次迭代結束時列印。 下面的範例檢查 CI 和審查評論，Claude 在 PR 變得安靜後在迭代之間等待更長時間：

```
/loop check whether CI passed and address any review comments

```

在[提供 Monitor 工具](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool)的工作階段中，當您要求動態 `/loop` 排程時，Claude 可能會直接使用它。Monitor 執行背景指令碼並串流回每個輸出行，這完全避免了輪詢，通常比在間隔上重新執行提示更具令牌效率和回應性。 動態排程的迴圈會像任何其他任務一樣出現在您的[排程任務清單](https://code.claude.com/docs/zh-TW/scheduled-tasks#manage-scheduled-tasks)中，因此您可以以相同的方式列出或取消它。[抖動規則](https://code.claude.com/docs/zh-TW/scheduled-tasks#jitter)不適用於它，但[七天過期](https://code.claude.com/docs/zh-TW/scheduled-tasks#seven-day-expiry)適用。 動態選擇的間隔和[內建維護提示](https://code.claude.com/docs/zh-TW/scheduled-tasks#run-the-built-in-maintenance-prompt)在每個提供者上都有效，並且[功能旗標擷取](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)已關閉。在 Amazon Bedrock、Claude Platform on AWS、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上，或擷取已關閉時，兩者都需要 Claude Code v2.1.248 或更新版本。在這些情況下，在較早版本上，沒有間隔的提示會在固定的 10 分鐘排程上執行，沒有提示的 `/loop` 會列印使用訊息。

### 執行內建維護提示

當您省略提示時，Claude 會使用內建維護提示而不是您提供的提示。在每次迭代上，它會按順序進行以下操作：

- 繼續對話中任何未完成的工作
- 照顧目前分支的拉取請求：審查評論、失敗的 CI 執行、合併衝突
- 執行清理通過，例如當沒有其他待處理項目時的錯誤搜尋或簡化

Claude 不會在該範圍之外啟動新的計畫，不可逆的操作（例如推送或刪除）只在它們繼續文字記錄已授權的內容時進行。

```
/loop

```

裸 `/loop` 在[動態選擇的間隔](https://code.claude.com/docs/zh-TW/scheduled-tasks#let-claude-choose-the-interval)上執行此提示。新增間隔（例如 `/loop 15m`）以改為在固定排程上執行它。若要用您自己的預設值替換內建提示，請參閱[使用 loop.md 自訂預設提示](https://code.claude.com/docs/zh-TW/scheduled-tasks#customize-the-default-prompt-with-loop-md)。

### 使用 loop.md 自訂預設提示

建立 `loop.md` 檔案以用您自己的指示替換[內建維護提示](https://code.claude.com/docs/zh-TW/scheduled-tasks#run-the-built-in-maintenance-prompt)。它為裸 `/loop` 定義單一預設提示，而不是單獨排程任務的清單，並且每當您在命令行上提供提示時 Claude Code 都會忽略它。若要在其旁邊排程其他提示，請使用 `/loop <prompt>` 或[直接要求 Claude](https://code.claude.com/docs/zh-TW/scheduled-tasks#manage-scheduled-tasks)。 Claude 在兩個位置尋找檔案，並使用它找到的第一個。

| 路徑                                                                                                   | 範圍                                     |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------- |
| `.claude/loop.md`                                                                                      | 專案層級。當兩個檔案都存在時優先。       |
| `~/.claude/loop.md`                                                                                    | 使用者層級。適用於任何未定義自己的專案。 |
| 該檔案是純 Markdown，沒有必需的結構。將其寫成您直接輸入 `/loop` 提示的方式。以下範例保持發行分支健康： |                                          |
| .claude/loop.md                                                                                        |                                          |

```
Check the `release/next` PR. If CI is red, pull the failing job log,
diagnose, and push a minimal fix. If new review comments have arrived,
address each one and resolve the thread. If everything is green and
quiet, say so in one line.

```

對 `loop.md` 的編輯在下次迭代時生效，因此您可以在迴圈執行時精煉指示。當任一位置都不存在 `loop.md` 時，迴圈會回退到內建維護提示。保持檔案簡潔：超過 25,000 位元組的內容會被截斷。

### 停止迴圈

若要在[自我調整 `/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks#let-claude-choose-the-interval) 等待下一次迭代時停止它，請按 `Esc`。這會清除待處理的喚醒，使迴圈不會再次執行。您透過[直接要求 Claude](https://code.claude.com/docs/zh-TW/scheduled-tasks#manage-scheduled-tasks) 排程的任務不受 `Esc` 影響，會保留在原位，直到您刪除它們。 在[自我調整模式](https://code.claude.com/docs/zh-TW/scheduled-tasks#let-claude-choose-the-interval)中，Claude 也可以在任務完成後自行結束迴圈。Claude 呼叫 [`ScheduleWakeup` tool](https://code.claude.com/docs/zh-TW/tools-reference)，其中 `stop: true`，這會立即取消待處理的喚醒。如果迭代結束時既未重新排程也未停止，Claude Code 會排程一個大約 20 分鐘後的備用喚醒，並在該迭代也不重新排程時結束迴圈。 固定間隔上的迴圈會持續執行，直到您[像任何其他排程任務一樣取消它們](https://code.claude.com/docs/zh-TW/scheduled-tasks#manage-scheduled-tasks)或[七天過去](https://code.claude.com/docs/zh-TW/scheduled-tasks#seven-day-expiry)。

## 設定一次性提醒

對於一次性提醒，請用自然語言描述您想要的內容，而不是使用 `/loop`。Claude 會排程一個執行後自動刪除的單次執行任務。

```
remind me at 3pm to push the release branch

```

```
in 45 minutes, check whether the integration tests passed

```

Claude 會使用 cron 表達式將執行時間固定到特定的分鐘和小時，並確認何時執行。

## 管理排程任務

用自然語言要求 Claude 列出或取消任務，或直接參考基礎工具。

```
what scheduled tasks do I have?

```

```
cancel the deploy check job

```

這些是 Claude 使用的基礎工具：

| 工具                                                                                                      | 用途                                                                        |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `CronCreate`                                                                                              | 排程新任務。接受 5 欄位 cron 表達式、要執行的提示，以及是否重複或執行一次。 |
| `CronList`                                                                                                | 列出所有排程任務及其 ID、排程和提示。                                       |
| `CronDelete`                                                                                              | 按 ID 取消任務。                                                            |
| 每個排程任務都有一個 8 字元的 ID，您可以傳遞給 `CronDelete`。一個工作階段最多可以同時保存 50 個排程任務。 |                                                                             |

## 排程任務如何執行

排程器每秒檢查一次到期的任務，並以低優先級將其加入佇列。排程的提示在您的回合之間執行，而不是在 Claude 正在回應時執行。如果 Claude 在任務到期時忙碌，提示會等到目前回合結束。 所有時間都以您的本地時區解釋。cron 表達式（例如 `0 9 * * *`）表示您執行 Claude Code 的任何地方的上午 9 點，而不是 UTC。

### 抖動

為了避免每個工作階段在同一牆上時刻點擊 API，排程器會為執行時間添加一個確定性偏移：

- 重複執行的任務最多在排程時間後 30 分鐘執行（或對於執行頻率超過每小時的任務，最多為間隔的一半）。為 `:00` 排程的每小時工作可能在 `:00` 到 `:30` 之間的任何時間執行。
- 為整點或半點排程的一次性任務最多提前執行 90 秒。

偏移是從任務 ID 衍生的，所以相同的任務總是獲得相同的偏移。如果精確計時很重要，請選擇不是 `:00` 或 `:30` 的分鐘，例如 `3 9 * * *` 而不是 `0 9 * * *`，一次性抖動將不適用。

### 七天過期

重複執行的任務在建立後 7 天自動過期。任務最後執行一次，然後刪除自己。這限制了被遺忘的迴圈可以執行多長時間。如果您需要重複執行的任務持續更長時間，請在過期前取消並重新建立它，或使用 [Routines](https://code.claude.com/docs/zh-TW/routines) 或 [Desktop 排程任務](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks) 進行持久排程。

## Cron 表達式參考

`CronCreate` 接受標準 5 欄位 cron 表達式：`minute hour day-of-month month day-of-week`。所有欄位都支援萬用字元 (`*`)、單一值 (`5`)、步驟 (`*/15`)、範圍 (`1-5`) 和逗號分隔的清單 (`1,15,30`)。

| 範例                                                                                                                                                                                                              | 含義                            |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `*/5 * * * *`                                                                                                                                                                                                     | 每 5 分鐘                       |
| `0 * * * *`                                                                                                                                                                                                       | 每小時整點                      |
| `7 * * * *`                                                                                                                                                                                                       | 每小時的第 7 分鐘               |
| `0 9 * * *`                                                                                                                                                                                                       | 每天上午 9 點（本地時間）       |
| `0 9 * * 1-5`                                                                                                                                                                                                     | 工作日上午 9 點（本地時間）     |
| `30 14 15 3 *`                                                                                                                                                                                                    | 3 月 15 日下午 2:30（本地時間） |
| 星期幾使用 `0` 或 `7` 表示星期日，`6` 表示星期六。不支援擴展語法，例如 `L`、`W`、`?` 和名稱別名，例如 `MON` 或 `JAN`。 當月份日期和星期幾都受到限制時，如果任一欄位匹配，日期就匹配。這遵循標準 vixie-cron 語義。 |                                 |

## 停用排程任務

在您的環境中設定 `CLAUDE_CODE_DISABLE_CRON=1` 以完全停用排程器。cron 工具和 `/loop` 變得不可用，任何已排程的任務都停止執行。請參閱 [環境變數](https://code.claude.com/docs/zh-TW/env-vars) 以取得完整的停用標誌清單。

## 限制

工作階段範圍的排程有固有的限制：

- 任務只在 Claude Code 執行且閒置時執行。關閉終端或讓工作階段退出會停止它們執行。[將工作階段放在背景執行](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)會將 `/loop` 任務帶到背景工作階段，該工作階段會持續執行而無需終端。
- 沒有錯過執行的追趕。如果任務的排程時間在 Claude 忙於長時間執行的請求時經過，它會在 Claude 變為閒置時執行一次，而不是每個錯過的間隔執行一次。
- 啟動新的對話會清除所有工作階段範圍的任務。當您使用 `claude --resume` 或 `claude --continue` 繼續工作階段時，Claude Code 會復原使用 `CronCreate` 排程的任務，除了已[過期](https://code.claude.com/docs/zh-TW/scheduled-tasks#seven-day-expiry)的重複執行任務和排程時間已經過去的一次性任務。自我調整的 `/loop`（[不會被復原](https://code.claude.com/docs/zh-TW/scheduled-tasks#let-claude-choose-the-interval)），因此請再次執行 `/loop` 以重新啟動它。背景 Bash 和監視任務在繼續時永遠不會被復原。
- 當[功能旗標擷取關閉](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)時，Claude Code 會將您要求跨工作階段保留的任務儲存在專案的 `.claude/scheduled_tasks.json` 檔案中。當 `.claude` 目錄或該檔案是符號連結時，Claude Code 會傳回錯誤，而不是排程任務。已儲存的任務只在您建立它的專案資料夾中執行。如果您將檔案複製到另一個資料夾（例如新的 worktree），該處的工作階段會列出複製的任務，但不會執行它們，因此請在該資料夾中再次建立任務。

對於需要無人值守執行的 cron 驅動自動化：

- [Routines](https://code.claude.com/docs/zh-TW/routines)：在雲端按排程執行、透過 API 呼叫或在 GitHub 事件上執行
- [GitHub Actions](https://code.claude.com/docs/zh-TW/github-actions)：在 CI 中使用 `schedule` 觸發器
- [Desktop 排程任務](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)：在您的機器上本地執行

是否 助手
