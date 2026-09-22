Remote Control 在所有方案上都可用。在 Team 和 Enterprise 上，預設為關閉，直到擁有者在 [Claude Code 管理員設定](https://claude.ai/admin-settings/claude-code)中啟用 Remote Control 切換。 Remote Control 將 [claude.ai/code](https://claude.ai/code) 或 Claude 應用程式（[iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 和 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)）連接到在您機器上執行的 Claude Code 會話。在您的辦公桌開始一項任務，然後從沙發上的手機或另一台電腦上的瀏覽器繼續。 當您在機器上啟動 Remote Control 會話時，Claude 會在整個過程中在本地執行，因此您的程式碼執行和檔案系統存取保持在您的機器上。使用 Remote Control，您可以：

- **遠端使用您的完整本地環境** ：您的檔案系統、[MCP servers](https://code.claude.com/docs/zh-TW/mcp)、工具和專案設定都保持可用，輸入 `@` 會自動完成來自您本地專案的檔案路徑。
- **同時在兩個介面上工作** ：對話和 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 和 [dynamic workflows](https://code.claude.com/docs/zh-TW/workflows) 的進度在所有連接的裝置上保持同步，因此您可以從終端機、瀏覽器和手機交替發送訊息。
- **從您的手機或瀏覽器傳送影像和檔案** ：在 Claude 應用程式或 claude.ai/code 中附加照片或檔案，可以有或沒有標題。Claude 會直接將附加的照片視為您訊息的一部分。Claude Code 會將其他檔案下載到您的機器，並將其作為 `@` 檔案參考傳遞給 Claude。
- **克服中斷** ：如果您的筆記型電腦進入睡眠狀態或網路中斷，當您的機器重新上線時，Claude Code 會自動重新連接。在連接重建時，Claude Code 會將來自 subagents 和工作流程的訊息、權限提示和狀態更新排隊，並在連接恢復後傳遞它們。

與[網頁版 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)（在雲端基礎設施上執行）不同，Remote Control 會話直接在您的機器上執行並與您的本地檔案系統互動。網頁和行動介面只是該本地會話的一個窗口。 本頁涵蓋設定、如何啟動和連接到會話，以及 Remote Control 與網頁版 Claude Code 的比較。

## 需求

在使用 Remote Control 之前，請確認您的環境符合以下條件：

- **訂閱** ：在 Pro、Max、Team 和 Enterprise 方案上可用。不支援 API 金鑰。在 Team 和 Enterprise 上，擁有者必須先在 [Claude Code 管理員設定](https://claude.ai/admin-settings/claude-code)中啟用 Remote Control 切換。
- **驗證** ：執行 `claude` 並使用 `/login` 透過 claude.ai 登入（如果您還沒有登入）。若沒有符合條件的登入，`claude remote-control` 會以錯誤結束，而 `claude --remote-control` 仍會啟動互動式工作階段，並在啟動後不久顯示 Remote Control 失敗通知。
- **API 端點** ：在以下任何設定中都不可用：
  - 您使用 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry。
  - 您將 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 指向 `api.anthropic.com` 以外的主機，例如 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)或代理。取消設定該變數以使用 Remote Control。在 v2.1.196 之前，Claude Code 允許使用自訂 `ANTHROPIC_BASE_URL` 的 Remote Control。
  - 您透過企業 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)登入。
- **功能旗標評估** ：[`DISABLE_TELEMETRY`、`DO_NOT_TRACK`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 和 `DISABLE_GROWTHBOOK`](https://code.claude.com/docs/zh-TW/env-vars) 各自停用 Remote Control 可用性所依賴的功能旗標評估。在您的殼層環境或 [`settings.json` 檔案](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)的 `env` 區塊中設定該變數的任何位置取消設定，以使用 Remote Control。
- **工作區信任** ：在您的專案目錄中至少執行一次 `claude` 以接受工作區信任對話框。啟動信任對話框永遠不會為您的主目錄儲存信任，因此請從專案目錄啟動 Remote Control。

## 啟動 Remote Control 會話

您可以從 CLI 或 VS Code 擴充功能啟動 Remote Control 會話。CLI 提供三種調用模式；VS Code 使用 `/remote-control` 命令。

- 伺服器模式
- 互動式會話
- 從現有會話
- VS Code

在您的專案目錄中，執行：

```
claude remote-control

```

在您接受 Remote Control 的一次性確認之前，`claude remote-control` 會說明它的功能並詢問 `Enable Remote Control? (y/n)` 後才啟動伺服器。回答 `y` 以接受並啟動伺服器。如果您拒絕，Claude Code 會在不啟動伺服器的情況下退出，並在您下次執行該命令時再次詢問。該程序在您的終端機中以伺服器模式保持執行，等待遠端連接。它顯示一個會話 URL，您可以使用該 URL 從[另一個裝置連接](https://code.claude.com/docs/zh-TW/remote-control#connect-from-another-device)，您可以按空格鍵顯示 QR 碼以從手機快速存取。當遠端會話處於活動狀態時，終端機會顯示連接狀態和工具活動。可用的旗標：

| 旗標                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 說明                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--name "My Project"`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 設定自訂會話標題，在 claude.ai/code 的會話清單中可見。                                                                                                                                                                                                                                                                                                                                              |
| `--remote-control-session-name-prefix <prefix>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 未設定明確名稱時自動生成會話名稱的前綴。預設為您機器的主機名稱，產生類似 `myhost-graceful-unicorn` 的名稱。設定 `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` 以獲得相同效果。                                                                                                                                                                                                                        |
| `-c`, `--continue`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 恢復此目錄中最後一個伺服器啟動的會話，而不是建立新會話。請參閱[停止伺服器後恢復會話](https://code.claude.com/docs/zh-TW/remote-control#resume-sessions-after-stopping-the-server)。無法與 `--session-id`、`--spawn`、`--capacity` 或 `--create-session-in-dir` 結合。需要 Claude Code v2.1.200 或更新版本；較早版本會將該旗標拒絕為未知引數。                                                       |
| `--session-id <id>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 按其 ID 恢復一個會話。請參閱[停止伺服器後恢復會話](https://code.claude.com/docs/zh-TW/remote-control#resume-sessions-after-stopping-the-server)。無法與 `--continue`、`--spawn`、`--capacity` 或 `--create-session-in-dir` 結合。需要 Claude Code v2.1.200 或更新版本；較早版本會將該旗標拒絕為未知引數。                                                                                           |
| `--spawn <mode>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 伺服器如何建立會話。                                                                                                                                                                                                                                                                                                                                                                                |
| • `same-dir`（預設）：所有會話共享目前的工作目錄，因此如果編輯相同的檔案可能會衝突。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                     |
| • `worktree`：每個按需會話都會獲得自己的 [git worktree](https://code.claude.com/docs/zh-TW/worktrees)。需要 git 儲存庫。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                     |
| • `session`：單一會話模式。恰好提供一個會話並拒絕其他連接。僅在啟動時設定。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                     |
| 在執行時按 `w` 在 `same-dir` 和 `worktree` 之間切換。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |                                                                                                                                                                                                                                                                                                                                                                                                     |
| `--capacity <N>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 並行會話的最大數量。預設值為 32。不能與 `--spawn=session` 一起使用。                                                                                                                                                                                                                                                                                                                                |
| `--[no-]create-session-in-dir`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 伺服器啟動時在目前目錄中預先建立一個會話，以便您有地方立即輸入。在 `worktree` 模式中，此會話保留在目前目錄中，而按需會話會獲得隔離的 worktrees。預設為開啟。如果您傳遞 `--no-create-session-in-dir` 以不建立任何會話啟動，Claude Code 會在您停止伺服器時封存伺服器的會話，因此沒有任何東西可以[恢復](https://code.claude.com/docs/zh-TW/remote-control#resume-sessions-after-stopping-the-server)。 |
| `--permission-mode <mode>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 為伺服器的會話設定起始[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)，例如 `acceptEdits`。接受 `manual` 作為 `default` 的別名；無法識別的模式會在啟動時停止伺服器並列出有效的模式。                                                                                                                                                                                                |
| `--debug-file <path>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 將偵錯日誌寫入給定的檔案。                                                                                                                                                                                                                                                                                                                                                                          |
| `--verbose`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 顯示詳細的連接和會話日誌。                                                                                                                                                                                                                                                                                                                                                                          |
| `--sandbox` / `--no-sandbox`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 啟用或停用[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)以進行檔案系統和網路隔離。預設為關閉。                                                                                                                                                                                                                                                                                               |
| 在 `remote-control` 之後給予這些旗標。如果您在 `remote-control` 之前傳遞全域 `claude` 旗標，或包裝指令碼新增一個，Claude Code 不會將該旗標帶到伺服器建立的會話中。Claude Code 只在丟棄該旗標已知不會改變這些會話可以執行的操作時才允許該旗標通過，例如 `--verbose` 或 `--model`。對於任何其他旗標，例如 `--settings`，Claude Code [拒絕啟動](https://code.claude.com/docs/zh-TW/errors#not-carried-over-to-the-sessions-remote-control-starts)並命名要移除的旗標。在 v2.1.248 之前，`remote-control` 之前的任何選項都會導致 Claude Code 拒絕其後的旗標，並出現 `unknown option` 錯誤。Claude Code 在列印說明之前檢查 Remote Control 資格，因此當您未使用符合條件的帳戶登入時，`claude remote-control --help` 會傳回錯誤而不是此旗標清單。 |                                                                                                                                                                                                                                                                                                                                                                                                     |
| 要啟動啟用了 Remote Control 的一般互動式 Claude Code 會話，請使用 `--remote-control` 旗標（或 `--rc`）：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                     |

```
claude --remote-control

```

可選地為會話傳遞一個名稱：

```
claude --remote-control "My Project"

```

這為您提供了一個完整的互動式會話在您的終端機中，您也可以從 claude.ai 或 Claude 應用程式控制。與 `claude remote-control`（伺服器模式）不同，您可以在會話也可遠端使用時在本地輸入訊息。 如果您已經在 Claude Code 會話中並想遠端繼續它，請使用 `/remote-control`（或 `/rc`）命令：

```
/remote-control

```

傳遞一個名稱作為引數以設定自訂會話標題：

```
/remote-control My Project

```

這啟動一個 Remote Control 會話，該會話會延續您目前的對話歷史記錄。在您接受 Remote Control 的一次性確認之前，會出現一個對話框，然後 `/remote-control` 才會連接。選擇**啟用 Remote Control** 以接受並連接。如果您選擇**算了** 或按 Esc，Claude Code 不會連接，並在您下次執行 `/remote-control` 時再次詢問。此命令不提供 `--verbose`、`--sandbox` 和 `--no-sandbox` 旗標。 在 [Claude Code VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)中，在提示框中輸入 `/remote-control` 或 `/rc`。

```
/remote-control

```

當 Remote Control 開啟時，Claude Code 在提示框頁尾顯示 **Remote Control** 指示器。會話連接後，點擊指示器直接進入會話，或在 [claude.ai/code](https://claude.ai/code) 的會話清單中找到它。Claude Code 也會在對話中發佈會話 URL。要斷開連接，再次執行 `/remote-control`。與 CLI 不同，VS Code 命令不接受名稱引數或顯示 QR 碼。會話標題是從您的對話歷史記錄或第一個提示衍生的。

### 檢查連接狀態

在互動式會話中，當 Remote Control 連接時，終端機會顯示 `/rc active` 指示器，該指示器連結到 claude.ai 上的會話。當終端機太窄無法容納時，指示器會隱藏。要查看會話 URL 和 QR 碼以從[另一個裝置連接](https://code.claude.com/docs/zh-TW/remote-control#connect-from-another-device)，請再次執行 `/remote-control` 以開啟狀態面板。該面板也可讓您斷開 Remote Control 連接，同時您的本地會話會繼續在終端機中執行。 如果連接在互動式會話中失敗，指示器會變更以顯示失敗，Claude Code 會在通知中顯示原因並將其新增到對話中。執行 `/remote-control` 以重新連接，除非原因說會話在其他地方被接管或結束：

- **另一個連接接管了此會話** ：另一個裝置或 Claude Code 會話現在擁有它。只有在您想從該裝置奪回它時才執行 `/remote-control`。
- **此會話從另一個裝置或應用程式被結束或封存** ：只有在您想要它回來時才執行 `/remote-control`；Claude Code 會重新開啟已封存的會話。
- **伺服器不再報告此會話** ：它可能已從另一個裝置或應用程式中刪除。

### 會話 URL 提醒

當 Remote Control 連接時，Claude Code 會在切換到您的手機或瀏覽器最有幫助時提醒您會話 URL，因此您不必在 `/remote-control` 中尋找連結。提醒會在以下任一時刻出現在提示框上方：

- **長回合** ：當回合執行時間超過伺服器調整的閾值時，Claude Code 會顯示 **Still working** 通知，帶有**從您的手機檢查** 連結，因此您可以從手機或瀏覽器跟蹤回合，而不是在終端機等待。Claude Code 會在回合結束時移除它。
- **重複的權限提示** ：在您在會話中回答多個[權限提示](https://code.claude.com/docs/zh-TW/permissions)後，會出現 **Approve tool calls from your phone** 通知，顯示會話 URL。Claude Code 會在您的下一個回合開始時移除它。

提醒可以出現在任何連接的會話中，包括 Remote Control [自動連接](https://code.claude.com/docs/zh-TW/remote-control#enable-remote-control-for-all-sessions)的會話。它們不會在每次這些條件發生時出現，每個提醒在所有會話中總共只出現幾次。您無法配置或關閉它們；每個都會自動清除。

### 從另一個裝置連接

一旦 Remote Control 會話處於活動狀態，您有幾種方式從另一個裝置連接：

- **開啟會話 URL** 在任何瀏覽器中直接進入 [claude.ai/code](https://claude.ai/code) 上的會話。
- **掃描 QR 碼** 顯示在會話 URL 旁邊，直接在 Claude 應用程式中開啟它。使用 `claude remote-control` 時，按空格鍵切換 QR 碼顯示。
- **開啟[claude.ai/code](https://claude.ai/code) 或 Claude 應用程式**，並在會話清單中按名稱找到會話。在 Claude 行動應用程式中，點擊導航中的**程式碼** 以到達會話清單。Remote Control 會話在線上時顯示帶有綠色狀態點的電腦圖示。

當您連接時，該裝置會顯示會話已在背景執行的任何子代理和工作流程。從該裝置停止其中一個，Claude Code 會停止您機器上的該任務。 遠端會話標題按以下順序選擇：

1. 您傳遞給 `--name`、`--remote-control` 或 `/remote-control` 的名稱
1. 您使用 `/rename` 設定的標題
1. 現有對話歷史記錄中最後一條有意義的訊息
1. 類似 `myhost-graceful-unicorn` 的自動生成名稱，其中 `myhost` 是您機器的主機名稱或您使用 `--remote-control-session-name-prefix` 設定的前綴

如果您沒有設定明確名稱，Claude Code 會在您發送提示後更新標題以反映您的提示。Claude Code 將自動生成的標題與您對話的語言相符，或與 [`language`](https://code.claude.com/docs/zh-TW/settings-reference#language) 設定相符（如果已配置）。 當您從 claude.ai 或 Claude 應用程式重新命名會話時，Claude Code 也會更新在 `claude --resume` 中顯示的本地標題。Claude Code 將相同的重新命名應用於提示欄上顯示的會話名稱，以及當會話[在背景執行](https://code.claude.com/docs/zh-TW/agent-view)時 `claude agents` 清單中顯示的會話名稱。在 v2.1.221 之前，從 claude.ai 的會話清單或 Claude 應用程式中重新命名只會更新標題，CLI 會保留其先前的會話名稱；`/rename`（在 CLI 本身中執行）在任何版本上設定名稱。 如果您還沒有 Claude 應用程式，請在 Claude Code 內使用 `/mobile` 命令顯示 [claude.ai/mobile](https://claude.ai/mobile) 的 QR 碼，該碼會開啟適合您手機的應用程式商店。

### 連接的裝置看到什麼

連接的裝置會在您的終端機中看到對話發生的情況。這些情況超越了普通訊息：

- **壓縮和`/clear`** ：當 Claude Code [壓縮對話](https://code.claude.com/docs/zh-TW/context-window#what-survives-compaction)時，連接的裝置會顯示進度，然後顯示對話被壓縮的位置。當您執行 `/clear` 時，對話也會在連接的裝置上重設。
- **使用`/resume` 切換對話**：連接的裝置不會接收切換到的對話的標題或較早的歷史記錄，但雙向的新訊息會進出您的終端機中開啟的任何對話。要再次從裝置處理原始對話，請在您的終端機中執行 `/resume` 並切換回它。
- **使用`/teleport` 拉取會話**：當您使用 `/teleport` 將[雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-cloud-to-terminal)拉入您的終端機時，連接的裝置不會接收拉取的對話的較早歷史記錄。雙向的新訊息會進出拉取的對話，該對話現在是您的終端機中開啟的對話。
- **來自您其他會話的訊息** ：使用[跨會話訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)，相同的連接會在不同機器上的您自己的會話之間以及來自您的[雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)的訊息，通過 Anthropic 伺服器（如 Remote Control 流量的其餘部分）進行傳遞。[在其他機器上的訊息會話](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-sessions-on-other-machines)涵蓋傳遞規則，[控制入站訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)涵蓋入站控制。需要 Claude Code v2.1.224 或更新版本。
- **您在回合中途發送的提示** ：當您在目前回合結束之前從連接的裝置發送提示時，Claude Code 會將其排隊，並在該回合完成後將其保留在裝置的文字記錄中。
- **您的變更的差異** ：當會話的目錄在 git 儲存庫中時，連接的裝置的差異窗格會顯示您未提交變更的差異。該裝置通過連接請求差異，Claude Code 在您的機器上計算它。當您的工作樹是乾淨的時，Claude Code 改為提供您的分支自從它從預設分支分歧以來的變更。在 v2.1.247 之前，Claude Code 只向由 `claude remote-control` 提供的會話中的連接的裝置報告差異。
- **模型** ：當您從連接的裝置選擇[模型](https://code.claude.com/docs/zh-TW/model-config)時，Claude Code 會在該模型上執行會話。終端機的 `/model` 選擇器、`/status` 和 `/config` 會顯示該模型。需要 Claude Code v2.1.238 或更新版本。
  - 您從裝置的模型控制中選擇的模型只適用於目前會話。當您從裝置向互動式會話發送 `/model <name>` 時，Claude Code 也會為新會話設定您的預設值。
  - 如果您發送 Claude Code 無法識別的名稱，例如預期模型 ID 的顯示名稱，Claude Code [拒絕選擇](https://code.claude.com/docs/zh-TW/errors#model-is-not-a-recognized-model-id)，會話會保留其目前的模型。在 v2.1.260 之前，Claude Code 會儲存來自裝置的模型控制的無法識別的選擇，您的下一條訊息會失敗。
- **努力等級** ：當您從連接的裝置使用 `/effort` 或裝置的努力控制設定[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)時，Claude Code 會將其應用於您機器上的會話，claude.ai/code 會顯示會話正在使用的等級。如果您使用 `CLAUDE_CODE_EFFORT_LEVEL` 固定了一個等級，會話會保留該等級，Claude Code 會拒絕來自努力控制的不同選擇。從努力控制中選擇等級需要您機器上的 Claude Code v2.1.234 或更新版本。
- **連接失敗後重新連接** ：執行 `/remote-control` 以重新連接。如果壓縮重寫了對話或您在此期間使用 `/resume` 切換了對話，Claude Code 會封存它正在使用的伺服器會話，而不是將其留在會話清單中。您仍然可以通過[篩選已封存的會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#archive-sessions)找到它。在裝置仍然連接時切換對話不會封存會話。

### 為所有會話啟用 Remote Control

Remote Control 只在您明確執行 `claude remote-control`、`claude --remote-control` 或 `/remote-control` 時啟動，除非自動連接已開啟。要為每個互動式會話開啟自動連接，請在 Claude Code 內執行 `/config` 並設定**為所有會話啟用 Remote Control** 。切換有三個值：

- **`true`**：當互動式會話啟動時自動連接。
- **`false`**：關閉自動連接，儘管來自[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)的 `true` 會優先，因為 Claude Code 會將選擇儲存到您的使用者設定。專案或本地設定（`.claude/settings.json`、`.claude/settings.local.json`）中的 `false` 會關閉自動連接，即使是受管 `true` 也是如此。
- **`default`**：清除您的選擇並遵循您組織的管理員預設值（如果已設定），否則遵循 Claude Code 的目前預設值。

相同的切換也會出現在 CLI 外：

- **桌面應用程式** ：**設定 > Claude Code > 預設啟用遠端控制**。
- **VS Code 擴充功能** ：[命令選單](https://code.claude.com/docs/zh-TW/vs-code#use-the-prompt-box)的設定部分中的**為所有會話啟用 Remote Control** 。需要 Claude Code v2.1.203 或更新版本。

要改為從設定檔案開啟自動連接，請在您的使用者 `~/.claude/settings.json` 或[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中將 [`remoteControlAtStartup`](https://code.claude.com/docs/zh-TW/settings-reference#remotecontrolatstartup) 設定為 `true`。在專案或本地設定（`.claude/settings.json`、`.claude/settings.local.json`）中，Claude Code 會遵守 `false` 並為該儲存庫關閉自動連接，但會忽略 `true`，因此已簽入的檔案無法為打開儲存庫的每個人開啟 Remote Control。 自動連接使用您自己的 claude.ai 帳戶登入，因此它啟動的會話只會出現在您自己帳戶的 Claude 應用程式中，並且不會授予任何人其他存取權限。 啟用此設定後，每個互動式 Claude Code 程序會註冊一個遠端會話。如果您執行多個實例，每個實例都會獲得自己的遠端會話。要從單個程序執行多個並行會話，請改用[伺服器模式](https://code.claude.com/docs/zh-TW/remote-control#start-a-remote-control-session)。

### 停止伺服器後恢復會話

當您使用 Ctrl+C 停止 `claude remote-control` 時，它正在提供的會話會停止從您的手機或瀏覽器回應。只要您沒有在同一目錄中執行另一個 `claude remote-control` 並且沒有使用 `--no-create-session-in-dir` 啟動此會話，Claude Code 就不會封存它們。要將它們恢復，請在同一目錄中執行以下命令之一：

- **`claude remote-control`**：恢復伺服器正在提供的每個會話。
- **`claude remote-control --continue`**：只恢復伺服器啟動的會話，並在該會話結束時退出。如果此目錄沒有記錄，Claude Code 會使用此儲存庫其他 git worktrees 中最新的記錄。
- **`claude remote-control --session-id <id>`**：只恢復您傳遞的 ID 的會話，並在該會話結束時退出。ID 是會話在 claude.ai/code 的 URL 中`/code/` 和任何 `?` 之間的部分。

這些命令在伺服器停止後約四小時內有效。之後，執行 `claude remote-control` 以啟動新會話。如果您在此期間封存了會話，`--continue` 和 `--session-id` 會在 Claude Code v2.1.228 或更新版本上取消封存它。 要恢復您使用 `claude --remote-control` 或 `/remote-control` 啟動的會話，請使用 `claude --continue` 或 `claude --resume` 恢復對話。Claude Code 是否重新連接以及連接到哪個會話取決於對話的[重新連接記錄](https://code.claude.com/docs/zh-TW/remote-control#resume-outcomes)。 如果您在第一個終端機仍然開啟 Remote Control 時在第二個終端機中恢復對話，Claude Code 會在第二個終端機中列印通知，並改為在那裡關閉 Remote Control，而不是從第一個終端機奪取會話。當 Remote Control 在那裡保持關閉時，該終端機中的 Claude 看不到[您在其他機器上的會話](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)，它們也無法到達它。在第二個終端機中執行 `/remote-control` 以將 Remote Control 移動到它。 當您在啟用了 Remote Control 的 Claude Desktop 或 IDE 擴充功能中恢復對話時，Claude Code 會將其重新附加到現有的 claude.ai 會話，而不是向會話清單新增新會話。

## 連接和安全性

您的本地 Claude Code 會話僅發出出站 HTTPS 請求，永遠不會在您的機器上開啟入站連接埠。當您啟動 Remote Control 時，它會向 Anthropic API 註冊並輪詢工作。當您從另一個裝置連接時，伺服器會透過串流連接在網頁或行動用戶端與您的本地會話之間路由訊息。 所有流量都透過 TLS 上的 Anthropic API 傳輸，與任何 Claude Code 會話相同的傳輸安全性。連接使用多個短期認證，每個認證的範圍限定為單一目的並獨立過期。當 `claude remote-control` 伺服器的註冊認證過期時，伺服器會再次向 Anthropic API 註冊並繼續為其會話提供服務。 Remote Control 連接時，會話記錄（包括您的訊息、Claude 的回應和工具活動）會儲存在 Anthropic 伺服器上。儲存的記錄可讓對話在您的裝置間保持同步，並讓會話在網路中斷後重新連接。執行和檔案系統存取保留在您的機器上，儲存的記錄會根據[資料使用](https://code.claude.com/docs/zh-TW/data-usage)政策保留。 若要完全關閉 Remote Control，請使用 [`disableRemoteControl`](https://code.claude.com/docs/zh-TW/settings-reference#disableremotecontrol) 設定。具有零資料保留等合規要求的組織無法啟用 Remote Control。

## 受信任的裝置

受信任的裝置目前處於測試版。功能和功能可能會隨著體驗的改進而演變。受信任的裝置在 Team 和 Enterprise 方案上可用。預設為關閉，直到擁有者啟用它。 受信任的裝置是一個組織範圍的設定，要求成員在從 claude.ai、Claude 行動應用程式或 Claude Desktop 檢視或控制 Remote Control 會話之前驗證其裝置。它將 Remote Control 存取與已知裝置和最近的驗證相關聯，而不僅僅是已登入的帳戶。 當設定開啟時，與 Remote Control 會話互動需要以下兩項：

- **已註冊的裝置** ：成員用於 Remote Control 的每個瀏覽器、手機或桌面應用程式都會註冊自己的認證。註冊僅在完整登入後不久提供，因此裝置作為真實驗證的一部分加入受信任清單，而不是在背景中無聲地進行。
- **最近的登入** ：成員的登入不超過 18 小時。成員不需要每天登入一次，而是使用 Face ID、Touch ID、Windows Hello 或通行金鑰確認存在。此生物識別步驟立即重新整理會話。

生物識別檢查透過作業系統或瀏覽器在裝置上執行，與通行金鑰登入相同的機制。Anthropic 永遠不會接收或儲存指紋、臉部資料或任何其他生物識別資訊。只有裝置的公鑰和基本中繼資料（例如顯示名稱、平台和註冊時間）會被儲存。 該設定僅適用於 Remote Control。一般 Claude 聊天、終端機中的 Claude Code 和 API 使用不受影響。

### 為您的組織啟用受信任的裝置

擁有者從 Claude Code 管理員主控台啟用該設定。 1 開啟 Claude Code 管理員設定 前往 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)。**需要受信任的裝置** 切換會出現在 Remote Control 設定下方。 2 開啟需要受信任的裝置 該設定適用於組織的每個成員以及在您啟用它後啟動的 Remote Control 會話。在切換開啟之前已經執行的會話不會被追溯保護，並在沒有裝置要求的情況下繼續，直到它們結束。不提供按團隊或按專案的範圍設定。 3 告知成員預期的情況 在啟用該設定後，成員第一次從瀏覽器、手機或桌面應用程式檢視或控制新的 Remote Control 會話時，系統會提示他們註冊該裝置。提前讓他們知道可以避免混淆。

### 成員看到的內容

註冊是每個裝置的一次性步驟。之後，唯一可見的變化是偶爾的生物識別提示。

- **首次在每個裝置上使用** ：成員被要求註冊。如果他們的登入不是最近的，他們首先透過您的一般流程登入，包括 SSO（如果已配置），然後確認註冊。
- **日常使用** ：具有已註冊裝置和最近登入的成員看不到任何提示。當登入超過 18 小時時，下一次 Remote Control 互動會顯示單個 Face ID、Touch ID、Windows Hello 或通行金鑰提示。
- **未註冊的裝置** ：在裝置被註冊之前，無法檢視或控制 Remote Control 會話。該裝置上的一般 Claude 聊天不受影響。
- **沒有平台驗證器** ：沒有 Face ID、Touch ID 或 Windows Hello 的機器上的成員可以使用硬體安全金鑰，或改為再次登入而不是升級。
- **在終端機中** ：執行 Claude Code 的機器在開發人員登入 CLI 時會自動接收自己的認證。終端機中沒有單獨的註冊步驟。

### 管理已註冊的裝置

成員可以從帳戶設定中檢視和撤銷自己的裝置。 開啟 [claude.ai/settings/account](https://claude.ai/settings/account#trusted-devices) 並找到**受信任的裝置** 部分，以查看每個已註冊的裝置及其名稱、平台和註冊日期。移除裝置會立即撤銷其認證，裝置可以在新登入後稍後重新註冊。如果未更新，認證也會自行過期，因此未使用的裝置會自動從受信任清單中刪除。 對於遺失或被盜的裝置，成員從此頁面移除它。如果成員無法登入，管理員可以在管理員主控台中使用**到處登出** 來撤銷該成員的每個會話和已註冊的裝置，之後成員重新註冊他們仍然持有的裝置。

## Remote Control 與雲端會話的比較

Remote Control 和[雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)都使用 claude.ai/code 介面。關鍵區別在於會話執行的位置：Remote Control 在您的機器上執行，因此您的本地 MCP servers、工具和專案設定保持可用。雲端會話在雲端基礎設施上執行，預設由 Anthropic 管理。 當您在本地工作中途並想從另一個裝置繼續時，請使用 Remote Control。當您想在沒有任何本地設定的情況下啟動任務、處理您沒有複製的儲存庫或並行執行多個任務時，請使用雲端會話。

## 行動推播通知

當 Remote Control 處於活動狀態時，Claude 可以向您的手機發送推播通知。 Claude 決定何時推播。它通常在長時間執行的任務完成或需要您的決定以繼續時發送一個。您也可以在提示中請求推播，例如 `notify me when the tests finish`。除了下面的開啟/關閉切換外，沒有按事件配置。 要設定行動推播通知： 1 安裝 Claude 行動應用程式 下載 Claude 應用程式（[iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 或 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)）。 2 使用您的 Claude Code 帳戶登入 使用您在終端機中用於 Claude Code 的相同帳戶和組織。 3 允許通知 接受來自作業系統的通知權限提示。 4 在 Claude Code 中啟用推播 在您的終端機中，執行 `/config` 並啟用**當 Claude 決定時推播** 以取得主動通知、**需要操作時推播** 以取得權限提示和問題，或兩者。 如果通知未送達：

- 如果 `/config` 顯示**未註冊行動裝置** ，請在手機上開啟 Claude 應用程式，以便它可以重新整理其推播令牌。下次 Remote Control 連接時，警告會清除。
- 在 iOS 上，焦點模式和通知摘要可能會抑制或延遲推播。檢查設定 → 通知 → Claude。
- 在 Android 上，激進的電池優化可能會延遲傳遞。在系統設定中將 Claude 應用程式豁免於電池優化。

Claude Code 在您在連接的終端機中輸入或專注時會跳過行動推播通知。自 v2.1.181 起，您可以將 [`CLAUDE_CLIENT_PRESENCE_FILE`](https://code.claude.com/docs/zh-TW/env-vars) 設定為標記檔案路徑，以將其擴展到您在機器上的任何時間，即使在另一個視窗中：當檔案存在時，通知會被跳過。配置螢幕鎖定監聽器或類似工具，以在螢幕解鎖時建立檔案，並在螢幕鎖定時刪除檔案。

## 限制

- **每個互動式程序一個遠端會話** ：在伺服器模式之外，每個 Claude Code 實例一次支援一個遠端會話。使用[伺服器模式](https://code.claude.com/docs/zh-TW/remote-control#start-a-remote-control-session)從單個程序執行多個並行會話。
- **本地程序必須保持執行** ：Remote Control 作為本地程序執行。如果您關閉終端機、退出 VS Code 或以其他方式停止 `claude` 程序，會話會離線，直到您[將其恢復](https://code.claude.com/docs/zh-TW/remote-control#resume-sessions-after-stopping-the-server)。除非 Claude 正在執行任務中，否則 claude.ai 和 Claude 應用程式會在程序退出後幾秒內將會話顯示為離線。若要在您從 SSH 斷開連線後保持遠端機器上的會話執行，請在 `tmux` 或 `screen` 內啟動它。
- **伺服器模式中的已崩潰會話** ：如果由 `claude remote-control` 提供的會話崩潰，請從已連接的裝置向其傳送訊息。Claude Code 會再次提供它。您不必重新啟動伺服器。需要 Claude Code v2.1.238 或更新版本。
- **已連接會話上的 HTTP 403 拒絕** ：一旦互動式會話連接，當您的機器和 Anthropic 伺服器之間的某些內容以 HTTP 403 回應時（在 VPN 或網路變更後可能發生），Claude Code 會重試最多三分鐘。如果拒絕持續更長時間，Claude Code 會斷開連線，原因會指出拒絕的內容：網路邊界，或您自己網路上的代理、VPN 或防火牆。
- **延長的網路中斷** ：如果您的機器處於喚醒狀態但無法到達網路，您接下來的操作取決於模式：
  - **伺服器模式** ：Claude Code 在大約 10 分鐘後放棄，`claude remote-control` 程序退出。再次執行 `claude remote-control` 以啟動新會話。
  - **互動式會話** ：繼續在本地工作。Claude Code 會在中斷期間重試，並在網路恢復時自動重新連接。
- **存在心跳失敗** ：如果互動式會話斷開連線並顯示 `could not reach the Remote Control server for about 30 minutes`，執行 `/remote-control` 以重新連接。Claude Code 只在會話的存在心跳失敗而其餘連接保持正常時才顯示此訊息；它會在大約 30 分鐘內持續重新註冊會話，之後才斷開連線。
- **轉發的對話框過期** ：Claude Code 會保持權限提示和 `AskUserQuestion` 問題開啟，直到您回答。當 Claude Code 將另一種對話框轉發到遠端會話時，例如安全拒絕後顯示的模型選擇提示，預設情況下它會等待五分鐘，然後關閉對話框並繼續使用對話框的無操作預設值。設定 [`dialogExpiry`](https://code.claude.com/docs/zh-TW/settings-reference#dialogexpiry) 以調整或停用截止時間。需要 Claude Code v2.1.224 或更新版本。
- **Fable 使用額度同意提示未被轉發** ：Claude Code 只在會話執行的位置顯示中途 [Fable 使用額度同意提示](https://code.claude.com/docs/zh-TW/model-config#fable-and-usage-credits)，而不是在您的裝置上。當會話在終端機中執行且沒有人在 Claude Code 關閉提示之前回答時，回合結束而不傳送請求；請參閱[確認提示未被回答](https://code.claude.com/docs/zh-TW/errors#the-prompt-to-confirm-went-unanswered)。
- **某些命令僅限本地** ：只在終端機介面中執行的命令，例如 `/plugin` 或 `/resume`，無論您是否傳遞引數，都只能從本地 CLI 使用。以下命令可從行動和網頁使用：
  - 文字輸出命令：`/compact`、`/clear`、`/context`、`/usage`、`/exit`、`/usage-credits`、`/recap` 和 `/reload-plugins`。`/usage-credits` 列印帳單 URL 而不是開啟瀏覽器。`/reload-plugins` 只在會話在互動式終端機中執行時有效；沒有終端機的會話會拒絕它。
  - `/model`、`/effort`、`/fast`、`/color` 和 `/rename`：將值作為引數傳遞，例如 `/model sonnet` 或 `/effort high`。從行動和網頁，`/model` 和 `/effort` 在終端機選擇器或滑桿的位置接受引數。
  - `/mcp`：從行動應用程式，傳回伺服器狀態的文字摘要而不是開啟選擇器。在網頁上，`/mcp` 單獨開啟 [claude.ai 連接器](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)的目錄而不是傳回摘要。`reconnect`、`enable` 和 `disable` [子命令](https://code.claude.com/docs/zh-TW/commands#all-commands)可從兩者使用。與本地 CLI 不同，`/mcp reconnect` 不帶伺服器名稱會重新連接每個已失敗或需要驗證的伺服器。
  - `/config`：從行動應用程式，傳遞 `key=value` 以設定設定，或不帶引數執行以列出您可以設定的金鑰。在網頁上，`/config` 改為開啟您設定的 Claude Code 部分，並忽略命令後的文字。
  - 在 Team 和 Enterprise 上，從行動或網頁執行的 `/usage-credits` 不會傳送[使用額度請求給您的管理員](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription)。傳送需要只在互動式 CLI 中出現的確認，因此命令會告訴您改為在那裡執行它。在 v2.1.211 之前，文字形式會在沒有確認的情況下傳送請求。
  - `/autocompact`，自 v2.1.221 起：將視窗大小作為引數傳遞，例如 `/autocompact 500k`。不帶引數時，它會列印目前的視窗大小作為文字，而不是開啟命令在終端機會話中顯示的對話框。
  - `/advisor`，自 v2.1.260 起：將模型作為引數傳遞，例如 `/advisor opus`，或傳遞 `off` 以關閉顧問。兩種形式都只適用於目前會話，並保持您已儲存的預設值不變。不帶引數時，它會列印目前的顧問作為文字，而不是開啟選擇器。
  - `/output-style`，自 v2.1.269 起：將樣式名稱作為引數傳遞，例如 `/output-style concise`，或不帶引數執行以列出樣式。從行動和網頁，您只能列出和選擇[內建樣式](https://code.claude.com/docs/zh-TW/output-styles#built-in-output-styles)。若要使用[自訂樣式](https://code.claude.com/docs/zh-TW/output-styles#create-a-custom-output-style)，請在會話本身中選擇它。

## 疑難排解

### 「Remote Control 需要 claude.ai 訂閱」

您未使用 claude.ai 帳戶進行驗證，或另一個認證優先於您的登入。此訊息採用以下其中一種形式：

- 已登出，來自 `/remote-control` 或 `--remote-control`：`Remote Control requires a claude.ai subscription.` 或 `/remote-control requires a claude.ai subscription.`
- 已登出，來自 `claude remote-control`：`You must be logged in to use Remote Control. Remote Control is only available with claude.ai subscriptions.`
- 已登入，但正在使用 API 金鑰或令牌：`Remote Control requires claude.ai subscription auth.` 後面跟著正在使用的認證，例如 `ANTHROPIC_API_KEY is set, so this session is using API-key auth`。`apiKeyHelper` 設定和 `ANTHROPIC_AUTH_TOKEN` 的命名方式相同。

執行 `claude auth login` 並選擇 claude.ai 選項。如果訊息名稱為 `ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`，請在設定它的任何地方移除它：您的 shell 環境或[設定檔](https://code.claude.com/docs/zh-TW/settings-reference#env)的 `env` 區塊。如果它名稱為 `apiKeyHelper`，請移除該設定。 在 v2.1.206 之前，在登出時執行 `/remote-control` 會報告 `Unknown command: /remote-control` 而不是此訊息。

### 「Remote Control 需要完整範圍登入令牌」

您使用來自 `claude setup-token` 或 `CLAUDE_CODE_OAUTH_TOKEN` 環境變數的長期令牌進行驗證。這些令牌只能進行模型請求，因此無法建立 Remote Control 會話。執行 `claude auth login` 以改用完整範圍會話令牌進行驗證。

### 「無法確定您的組織以進行 Remote Control 資格檢查」

您的快取帳戶資訊已過期或不完整。執行 `claude auth login` 以重新整理它。

### 「Remote Control 尚未為此帳戶啟用」

Claude Code 檢查了您登入帳戶的 Remote Control 可用性，檢查結果為關閉。通常的原因是快取的權利在方案變更後已過期。執行 `claude auth logout` 然後 `claude auth login` 以重新整理它們，如果您使用的是舊版本，請更新 Claude Code。 執行 `claude doctor` 以查看哪個個別資格檢查失敗。環境變數衝突、無法到達的檢查和您的組織的 Remote Control 設定各自產生自己的訊息，因此此錯誤表示帳戶級別的檢查本身。 在 v2.1.239 之前，此訊息讀作「Remote Control is not yet enabled for your account」。在 v2.1.154 之前，停用功能旗標評估的變數（例如 `DISABLE_TELEMETRY` 或 `DO_NOT_TRACK`）也會產生此訊息；下面的「Remote Control requires feature-flag evaluation」項目涵蓋該配置。

### 「無法驗證 Remote Control 資格」

Claude Code 無法到達功能旗標服務以檢查您的帳戶是否啟用了 Remote Control，通常是因為您離線或代理阻止了請求。一旦您有網路存取權，請重試，或執行 `claude doctor` 以取得詳細資訊。相關訊息「無法驗證您的組織的 Remote Control 政策」具有相同的原因和相同的修復。兩個訊息都在 v2.1.178 中新增。

### 「Remote Control 需要功能旗標評估」

設定了以下其中一個變數：[`DISABLE_TELEMETRY`、`DO_NOT_TRACK`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 或 `DISABLE_GROWTHBOOK`](https://code.claude.com/docs/zh-TW/env-vars)。每一個都停用了 Remote Control 可用性所依賴的功能旗標評估，完整訊息會命名 Claude Code 找到的變數。在設定它的任何地方取消設定該變數，在您的 shell 環境或 [`settings.json` 檔案](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)的 `env` 區塊中。在 2.1.154 之前的版本上，相同的配置會產生「Remote Control is not yet enabled for your account」。

### 「Remote Control 僅在透過 api.anthropic.com 使用 Claude 時可用」

會話未直接與 Anthropic API 通訊，因此沒有 claude.ai 後端可配對。這發生在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上。當 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 指向 `api.anthropic.com` 以外的主機時，例如 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)或代理，即使您使用 claude.ai 登入，也會發生這種情況。在 v2.1.196 之前，Claude Code 對於自訂 `ANTHROPIC_BASE_URL` 不會顯示此訊息。請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors#remote-control-requires-the-anthropic-api)以取得完整的原因清單。 訊息會命名將會話路由遠離 Anthropic API 的內容，例如 `CLAUDE_CODE_USE_BEDROCK` 或自訂 `ANTHROPIC_BASE_URL`。如果您有符合資格的 claude.ai 登入，請取消設定命名的變數，如果您在那裡設定了它，請從[設定](https://code.claude.com/docs/zh-TW/settings)中的 `env` 金鑰移除它，然後重新啟動會話。在 v2.1.219 之前，訊息只是本節標題中的句子，因此在較舊的版本上，請自行檢查您的環境以查找提供者變數，例如 `CLAUDE_CODE_USE_BEDROCK` 和 `CLAUDE_CODE_USE_VERTEX`，以及 `ANTHROPIC_BASE_URL`。

### 「Remote Control 已被您的組織政策停用」

政策阻止 Remote Control，或 Claude Code 無法在此機器上載入您的組織政策，同時保持 Remote Control 關閉。按順序檢查這些原因：

- **錯誤提及`disableRemoteControl`** ：您的 IT 管理員已透過[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)在此裝置上停用 Remote Control，獨立於組織範圍的切換和您如何登入。
- **您的 claude.ai 方案是 Pro 或 Max** ：Claude Code 仍然以較早登入的 Team 或 Enterprise 組織身份登入，因此它檢查該組織的 Remote Control 政策。執行 `/status` 以查看您的登入使用的方案和組織。執行 `claude auth logout` 然後 `claude auth login` 以在您目前的方案下重新登入。
- **組織政策未在此機器上載入** ：執行 `claude doctor` 並閱讀 `Organization policy` 行。如果該行顯示政策未載入，那就是保持 Remote Control 關閉的原因。在 v2.1.261 之前，`claude doctor` 未列印此行。
- **訊息未說聯絡您的組織管理員** ：您的組織具有與 Remote Control 不相容的 HIPAA 配置，`/status` 在其 `Compliance` 行中列出 `HIPAA`。在此狀態下，管理面板的 Remote Control 切換呈灰色，因此 Owner 無法在那裡變更它。聯絡 Anthropic 支援以討論選項。在 v2.1.267 之前，此情況顯示「Remote Control isn’t available for your organization due to its compliance policy」。
- **否則，Owner 尚未為您的組織啟用它** ：Remote Control 在 Team 和 Enterprise 方案上預設為關閉。Owner 可以在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 透過開啟 **Remote Control** 切換來啟用它。此切換是伺服器端組織設定。

### 「Remote credentials fetch failed」

Claude Code 無法從 Anthropic API 獲取短期認證以建立連接。使用 `--verbose` 重新執行以查看完整錯誤：

```
claude remote-control --verbose

```

常見原因：

- 未登入：執行 `claude` 並使用 `/login` 透過您的 claude.ai 帳戶進行驗證。Remote Control 不支援 API 金鑰驗證。
- 網路或代理問題：防火牆或代理可能阻止出站 HTTPS 請求。Remote Control 需要存取埠 443 上的 Anthropic API。
- 會話建立失敗：如果您也看到 `Session creation failed — see debug log`，失敗發生在設定的早期。檢查您的訂閱是否有效。

過期的登入令牌不會導致此錯誤。當 Anthropic API 拒絕已儲存的令牌時，例如因為另一個 Claude Code 程序已經重新整理了它，Claude Code 會重新整理令牌並自動重試。在 v2.1.224 之前，過期的令牌會導致 Remote Control 啟動失敗並顯示此訊息，因此設定為[自動連接](https://code.claude.com/docs/zh-TW/remote-control#enable-remote-control-for-all-sessions)的會話可能在啟動時間歇性失敗。

### 「無法重新連接到您的 Remote Control 會話」

當您使用 `claude --resume` 或 `claude --continue` 繼續對話時，Claude Code 會重新連接到該對話中記錄的 Remote Control 會話。此訊息表示重新連接因可能是暫時性的原因（例如網路中斷或伺服器錯誤）而失敗，因此 Claude Code 無法確認遠端會話是否仍然存在。 執行 `/remote-control` 以重試連接，或使用 `claude --remote-control` 啟動新會話以建立新的 Remote Control 會話。您的本機會話在沒有 Remote Control 的情況下繼續執行。 當您繼續時，您也可以獲得以下其中一個結果，而不是此訊息：

- **伺服器報告記錄的會話已消失，或重新連接記錄命名不同的帳戶** ：Claude Code 按照對話的重新連接記錄所說的進行：
  - **記錄命名您登入的帳戶** ：Claude Code 使用自動生成的名稱啟動替換會話，並將對話的較早訊息排除在外。例如，在您從 claude.ai 或 Claude 應用程式刪除會話後，您會看到這種情況。
  - **記錄命名不同的帳戶** ：Claude Code 啟動新會話，不包含對話的較早訊息，也不顯示訊息，無論記錄的會話是否仍然存在。
  - **記錄未說明哪個帳戶擁有會話，或 Claude Code 無法讀取您的已儲存登入** ：Claude Code 顯示 [`Previous session is unavailable — run /remote-control to start a new one`](https://code.claude.com/docs/zh-TW/remote-control#previous-session-is-unavailable) 而不是此訊息，不啟動任何內容，並從對話中移除記錄。
- **您在繼續之前關閉了 Remote Control** ：除非託管 Claude Code 的應用程式已告訴它該應用程式擁有 claude.ai 會話，否則當您從 CLI 的[狀態面板](https://code.claude.com/docs/zh-TW/remote-control#check-connection-status)、VS Code 擴充功能或基於[代理 SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 的主機關閉 Remote Control 時，Claude Code 會移除重新連接記錄，因此它不會重新連接。當擁有的應用程式關閉它時，Claude Code 會保留記錄並重新連接。
- **此機器上的另一個 Claude Code 仍然有會話** ：您會看到以 `Remote Control not started here` 開頭的通知，Claude Code [在繼續的會話中保持 Remote Control 關閉](https://code.claude.com/docs/zh-TW/remote-control#resume-sessions-after-stopping-the-server)。在那裡執行 `/remote-control` 以移動它。

在 v2.1.232 之前，當伺服器報告記錄的會話已消失時，Claude Code 的回應不同。從 v2.1.227 到 v2.1.231，Claude Code 拒絕啟動替換，即使記錄與您的帳戶相符。在 v2.1.226 及更早版本中，Claude Code 啟動替換，無論記錄是否與您的帳戶相符，在 v2.1.224 到 v2.1.226 中，在該機器上登入的帳戶下建立它，從不是另一個帳戶的，不上傳對話的較早訊息到它。在 v2.1.200 之前，Claude Code 在任何重新連接失敗後建立新會話。

### 「Previous session is unavailable — run /remote-control to start a new one」

Claude Code 無法恢復先前的 Remote Control 會話，並停止而不是自動啟動新會話。在使用 `claude --resume` 或 `claude --continue` 繼續對話後，或在 Claude Code [在斷開連接後自動重新連接](https://code.claude.com/docs/zh-TW/errors#remote-control-couldnt-refresh-your-login)後，您可能會看到此訊息。 執行 `/remote-control` 以在目前登入下啟動新的 Remote Control 會話；您的本機會話在沒有 Remote Control 的情況下繼續執行。相關訊息 `Remote Control could not verify the signed-in account — run /remote-control to reconnect` 具有相同的修復；當登入帳戶在驗證和重新連接之間變更或無法讀取時，Claude Code 會顯示它。如果您在不重新啟動 Claude Code 的情況下在 `Previous session is unavailable` 後執行 `/remote-control`，Claude Code 會將對話的較早訊息排除在新會話之外。 在繼續時，Claude Code [僅在對話的重新連接記錄命名擁有會話的帳戶時才啟動新會話](https://code.claude.com/docs/zh-TW/remote-control#resume-outcomes)，因為伺服器以相同的方式報告您刪除的會話和由另一個帳戶擁有的會話。v2.1.227 之前的 Claude Code 未記錄該帳戶，當 Claude Code 無法讀取您的已儲存登入時，它無法檢查記錄。v2.1.232 之前的 Claude Code 在[不同的情況集](https://code.claude.com/docs/zh-TW/remote-control#reconnect-history)中顯示 `Remote Control could not resume the previous session under the current login — run /remote-control to start fresh`。

### 「Remote Control got an unexpected server response」

Remote Control 伺服器接受了請求，但以此版本的 Claude Code 無法讀取的形式回覆，同時建立遠端會話或擷取其認證。在相同版本上重試會以相同方式失敗。執行 `claude update`，然後執行 `/remote-control` 以重新連接。此訊息在 v2.1.225 中新增。

### 「Your organization requires Trusted Devices for Remote Control, but this device is not enrolled」

您的組織已[啟用受信任的裝置](https://code.claude.com/docs/zh-TW/remote-control#trusted-devices)，此機器尚未註冊。在 Claude Code 中執行 `/login`。註冊作為登入的一部分進行，沒有單獨的註冊命令。

### 「session expired for trusted-device check」

您的登入超過 18 小時。在 Claude Code 中執行 `/login`，或當 claude.ai 或行動應用程式提示您時，使用 Face ID、Touch ID、Windows Hello 或通行金鑰確認。請參閱[受信任的裝置](https://code.claude.com/docs/zh-TW/remote-control#trusted-devices)。

## 選擇正確的方法

Claude Code 提供了多種方式讓您在不在終端機時進行工作。它們在觸發工作的方式、Claude 執行的位置以及您需要設定的程度上有所不同。

|                                                                                         | 觸發                                                                                              | Claude 執行位置                                                                                                                                                                         | 設定                                                                                                                                                                                     | 最適合                                     |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| [Dispatch](https://code.claude.com/docs/zh-TW/desktop#sessions-from-dispatch)           | 從 Claude 行動應用程式傳送任務訊息                                                                | 您的機器 (Desktop)                                                                                                                                                                      | [將行動應用程式與 Desktop 配對](https://support.claude.com/en/articles/13947068)                                                                                                         | 在您不在時委派工作，最少設定               |
| [Remote Control](https://code.claude.com/docs/zh-TW/remote-control)                     | 從 [claude.ai/code](https://claude.ai/code) 或 Claude 行動應用程式驅動執行中的工作階段            | 您的機器 (CLI 或 VS Code)                                                                                                                                                               | 執行 `claude remote-control`                                                                                                                                                             | 從另一個裝置控制進行中的工作               |
| [Channels](https://code.claude.com/docs/zh-TW/channels)                                 | 從聊天應用程式 (如 Telegram 或 Discord) 或您自己的伺服器推送事件                                  | 您的機器 (CLI)                                                                                                                                                                          | [安裝頻道外掛程式](https://code.claude.com/docs/zh-TW/channels#quickstart) 或 [建立您自己的](https://code.claude.com/docs/zh-TW/channels-reference)                                      | 對外部事件 (如 CI 失敗或聊天訊息) 做出反應 |
| [Slack](https://code.claude.com/docs/zh-TW/slack)                                       | 在團隊頻道中提及 `@Claude`                                                                        | Anthropic 雲端                                                                                                                                                                          | [安裝 Slack 應用程式](https://code.claude.com/docs/zh-TW/slack#setting-up-claude-code-in-slack) 並啟用 [網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) | 從團隊聊天進行 PR 和審查                   |
| [Self-hosted environments](https://code.claude.com/docs/zh-TW/self-hosted-environments) | 啟動 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 並選擇您組織的環境 | 您組織的基礎設施                                                                                                                                                                        | [部署執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart)，在 Team 和 Enterprise 方案上                                                                       | 必須在您的網路內執行的雲端工作階段         |
| [Scheduled tasks](https://code.claude.com/docs/zh-TW/scheduled-tasks)                   | 設定排程                                                                                          | [CLI](https://code.claude.com/docs/zh-TW/scheduled-tasks)、[Desktop](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks) 或 [雲端](https://code.claude.com/docs/zh-TW/routines) | 選擇頻率                                                                                                                                                                                 | 定期自動化 (如每日審查)                    |

## 相關資源

- [在雲端使用 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：在雲端執行會話而不是在您的機器上，透過[雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)設定
- [跨會話訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)：讓 Claude 在其他機器或您的[雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)上傳送訊息給您的會話
- [Channels](https://code.claude.com/docs/zh-TW/channels)：將 Telegram、Discord 或 iMessage 轉發到會話中，以便 Claude 在您離開時對訊息做出反應
- [Dispatch](https://code.claude.com/docs/zh-TW/desktop#sessions-from-dispatch)：從您的手機傳送任務訊息，它可以生成 Desktop 會話來處理它
- [驗證](https://code.claude.com/docs/zh-TW/authentication)：設定 `/login` 並管理 claude.ai 的認證
- [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference)：包括 `claude remote-control` 的旗標和命令的完整清單
- [安全性](https://code.claude.com/docs/zh-TW/security)：Remote Control 會話如何適應 Claude Code 安全模型
- [資料使用](https://code.claude.com/docs/zh-TW/data-usage)：在本地、Remote Control 和雲端會話期間透過 Anthropic API 流動的資料

是否 助手
