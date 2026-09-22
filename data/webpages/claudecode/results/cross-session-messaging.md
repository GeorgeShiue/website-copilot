跨工作階段訊息傳送需要 macOS 和 Linux 上的 Claude Code v2.1.224 或更新版本，包括 WSL 2 內的 Linux。在原生 Windows 上，需要 Claude Code v2.1.234 或更新版本。當工作階段符合要求時，訊息傳送功能預設為開啟，無需啟用。請參閱[可用性](https://code.claude.com/docs/zh-TW/cross-session-messaging#availability)以了解提供者要求以及如何確認工作階段具有此功能。 跨工作階段訊息傳送讓 Claude 從您的一個 Claude Code 工作階段傳遞訊息至另一個工作階段。當一個工作階段中的變更破壞了另一個工作階段正在建立的內容時，Claude 可以在您注意到之前警告該工作階段。當一個工作階段解決了另一個工作階段被阻止的問題時，Claude 可以跨工作階段傳送答案。 訊息是一個 Claude 寫給另一個 Claude 的文字片段，絕不包括寄件者的對話歷史記錄或檔案。若要移動整個對話或其內容，請[復原工作階段](https://code.claude.com/docs/zh-TW/sessions#resume-a-session)。 Claude 使用兩個工具來實現此功能：`ListAgents` 用於探索它可以到達的代理程式，以及 `SendMessage` 用於按名稱將訊息傳遞給其中一個代理程式。使用相同的 `SendMessage` 工具，Claude 也可以在單一工作階段或團隊內訊息傳送至[子代理程式](https://code.claude.com/docs/zh-TW/sub-agents#resume-subagents)和[代理程式團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友。本頁涵蓋您獨立工作階段之間的訊息。

## 何時使用跨工作階段訊息傳送

當您的一個工作階段有另一個工作階段在任務中期需要的內容時，使用訊息傳送。Claude 可以在看到需要時自動傳送訊息，例如在進行影響另一個工作階段正在進行的工作的變更後，或者您可以要求它傳送一個。常見的情況：

- **移交發現** ：當一個工作階段發現破壞性變更或做出決定時，Claude 為在受影響區域工作的工作階段總結它，而不是您在那裡重新解釋它。
- **協調平行 worktrees** ：當工作階段在單獨的 [worktrees](https://code.claude.com/docs/zh-TW/worktrees) 中處理同一個儲存庫時，Claude 可以告訴其他工作階段已合併的內容。
- **從長時間執行的工作獲取狀態** ：讓遷移或測試執行回報給您正在監視的工作階段，或從那裡自己要求它。如果該工作階段在此機器上，Claude 也可以[在它下次閒置或退出時要求一個通知](https://code.claude.com/docs/zh-TW/cross-session-messaging#get-a-notice-when-another-session-goes-idle)。
- **跨機器訊息傳送** ：到達您在另一台機器或網路上的一個工作階段。

在您自己啟動和引導的獨立工作階段之間使用訊息傳送。Claude Code 為運行或到達多個工作階段的其他每種方式都有專用功能，因此請使用為您正在做的事情而建立的功能：

- 若要在另一個終端機中繼續一個對話，或與新工作階段共享其內容，請[恢復工作階段](https://code.claude.com/docs/zh-TW/sessions#resume-a-session)
- 對於 Claude 生成和監督的協調團隊工作階段，請使用[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)
- 若要從一個地方監視和引導許多工作階段，請使用[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)
- 若要從您的手機或另一台裝置自己引導工作階段，而不是讓工作階段互相訊息傳送，請使用[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)
- 若要將外部事件（例如 CI 結果或聊天訊息）推送到工作階段中，請使用[頻道](https://code.claude.com/docs/zh-TW/channels)

## 訊息傳送至另一個工作階段

當您的一個工作階段學到另一個工作階段需要的內容（例如發現、狀態或決定）時，Claude 會傳遞它，而不是您在終端機之間複製貼上。Claude 使用 `ListAgents` 發現目標並使用 `SendMessage` 傳送，因此您永遠不會自己呼叫任一工具。Claude 可以決定在未被要求的情況下傳送訊息，您也可以提示傳送一個。 若要自己提示，告訴 Claude 您希望另一個工作階段知道或做什麼。此範例是您輸入的提示，不是 Claude 傳送的訊息：

```
詢問在我的另一個終端機中執行的工作階段遷移是否完成

```

Claude 自己寫實際訊息，因此您的提示可以將內容留給 Claude。此提示要求摘要而不指定其措辭，Claude 傳送的內容會有所不同：

```
向處理付款 API 的工作階段解釋我們剛剛做了什麼

```

若要自己命名目標，在您的提示中提及工作階段：輸入 `@` 後跟工作階段名稱的前幾個字母，然後從預先輸入中選擇工作階段，與您[@-提及子代理](https://code.claude.com/docs/zh-TW/sub-agents#invoke-subagents-explicitly)的方式相同。需要 Claude Code v2.1.232 或更新版本。Claude Code 插入提及，例如 `@api-worker`，並告訴 Claude 它命名的工作階段，因此 Claude 可以訊息傳送至該工作階段而無需先列出您的工作階段。此提示使用提及命名目標：

```
讓 @api-worker 知道架構遷移已完成

```

預先輸入列出您在此機器上的其他即時工作階段。兩種情況需要超過名稱的前幾個字母：

- **超出此機器的工作階段** ：雲端或遠端控制工作階段僅在 Claude 列出或訊息傳送至您超出此機器的工作階段後才出現在預先輸入中，因此請先要求 Claude 列出它們。
- **名稱包含空格或字母、數字、連字號和底線以外的其他字元** ：在雙引號中輸入它，例如 `@"release notes"`。當您從預先輸入中選擇工作階段時，Claude Code 會為您插入引號。

您也可以在沒有選擇器的情況下輸入提及。當多個即時工作階段回應提及的名稱時，Claude 會在傳送前要求您指定您的意思。 有關 Claude 寫的訊息在到達時的外觀，包括其中一個範例，請參閱[訊息的外觀](https://code.claude.com/docs/zh-TW/cross-session-messaging#what-a-message-looks-like)。

### 訊息傳遞

接收 Claude 在活躍回合期間的工具呼叫之間讀取訊息，因此執行中的工具永遠不會被中斷。當接收工作階段閒置時，Claude Code 使用訊息啟動新回合。 來自另一個工作階段的訊息作為純文字到達。如果它使用 `@` 提及檔案或 [MCP 資源](https://code.claude.com/docs/zh-TW/mcp#use-mcp-resources)，Claude 會看到如寫入的提及，Claude Code 不會附加任何內容，無論訊息是啟動新回合還是在一個回合期間到達。Claude 仍然可以使用自己的工具在接收機器上開啟提及的路徑，受該工作階段的權限限制。在 v2.1.251 之前，啟動新回合的訊息中的 `@` 提及會在接收端附加檔案或 MCP 資源。 Claude Code 在以下情況下拒絕訊息：

- 訊息[超過大小上限](https://code.claude.com/docs/zh-TW/cross-session-messaging#limitations)。Claude Code 在傳送工作階段中拒絕它，在它離開之前。
- 對此機器上工作階段的快速突發已達到[該工作階段的收件匣接受](https://code.claude.com/docs/zh-TW/cross-session-messaging#limitations)的內容。Claude Code 拒絕進一步訊息傳送至該工作階段。
- 此機器上的回覆目標未通過安全檢查，例如符號連結目標或不是預期程序的端點。[拒絕傳送跨工作階段訊息](https://code.claude.com/docs/zh-TW/errors#refusing-to-send-a-cross-session-message)列出這些檢查。
- Claude 將訊息定址到此工作階段自己的名稱，如[查看 Claude 可以到達的工作階段](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)下所述。

接收工作階段根據其自己的[入站控制](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)檢查每條到達的訊息，檢查以三種結果之一結束：

- **已傳遞** ：Claude Code 將訊息傳遞給接收 Claude。
- **已保留** ：Claude Code 將訊息擱置未傳遞。保留的訊息僅在您批准它或稍後的模式或設定變更允許它時才到達 Claude。
- **已拒絕** ：Claude Code 在未傳遞的情況下丟棄訊息。

一旦傳遞，訊息計入[使用量](https://code.claude.com/docs/zh-TW/costs)，如同您輸入的提示，接收 Claude 可以以相同方式回覆寄件者，除了[單向跨機器情況](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-sessions-on-other-machines)。 權限邊界保持每個工作階段。Claude 被指示永遠不要要求另一個工作階段執行在其自己的工作階段中被拒絕或阻止的操作，或其自己的權限設定會阻止的操作，並將該工作路由回您。在接收端，[接收工作階段自己的權限提示和規則仍然適用](https://code.claude.com/docs/zh-TW/cross-session-messaging#how-a-session-treats-an-incoming-message)於訊息要求的任何內容。

### 在另一個工作階段閒置時獲取通知

Claude 可以要求您在此機器上的一個工作階段在該工作階段下次閒置或退出時傳回一個通知。閒置在此表示工作階段完成了一個回合，沒有任何排隊。當您在另一個工作階段中等待長時間任務並想在完成時聽到而不是檢查時使用它。需要兩個工作階段中的 Claude Code v2.1.236 或更新版本。

#### 要求通知

告訴 Claude 您在等待什麼。此提示要求來自遷移工作階段的通知：

```
告訴我遷移工作階段何時完成它正在進行的工作

```

Claude 使用 `SendMessage` 工具的 `notify_when_idle` 輸入訂閱，要麼附加到它正在傳送的訊息，要麼自己訂閱。自己訂閱時，Claude Code 訂閱而不在監視工作階段中啟動回合或花費代幣，如果該工作階段已經閒置，則立即傳送通知。附加到訊息時，Claude Code 先傳遞訊息，稍後傳送通知。

#### 每個工作階段顯示什麼

監視工作階段顯示一行，說另一個程序要求在工作階段下次閒置時被告知。要求工作階段顯示通知作為命名監視工作階段的一行。該行可以包括該工作階段回合完成的時間和該回合的單行狀態。如果要求工作階段閒置，Claude Code 使用通知啟動新回合。

#### 限制

通知是一次性的：Claude Code 從監視工作階段傳送一次，兩個工作階段都不輪詢另一個。如果在 12 小時內沒有通知到達，Claude Code 會丟棄訂閱並告訴 Claude，因此它不會繼續等待。 每一側的[入站控制](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)適用於通知，如同訊息：

- **任一側的`refuse`** ：沒有任何內容到達。監視工作階段在未記錄或回答的情況下丟棄請求，因此訂閱在 12 小時後未回答而過期，具有 `refuse` 的要求工作階段永遠不會訂閱。
- **任一側的`hold`** ：通知到達時內容較少。監視工作階段省略單行狀態，要求工作階段在您的文字記錄中顯示通知而不將其傳遞給 Claude。

只有您主要對話中的 Claude 可以訂閱，並且只能訂閱此機器上的您的工作階段。當子代理或代理團隊隊友設定 `notify_when_idle` 時，Claude Code 不進行訂閱並告訴它。當 Claude 要求來自任何其他代理（例如隊友、子代理或超出此機器的工作階段）的通知時，Claude Code 拒絕整個呼叫，包括附加到它的任何訊息，並向 Claude 報告拒絕，以便它可以在沒有請求的情況下重新傳送訊息。

### 查看 Claude 可以到達的工作階段

Claude 自己找到訊息的目標，因此您不需要在要求它傳送之前執行任何操作。若要自己查看 Claude 可以到達的工作階段，請執行 `/list-agents` 命令。第一行（如果存在）是此工作階段自己的名稱，您的其他工作階段用來訊息傳送至它的名稱。下面的行是 Claude 可以到達的工作階段：

- **子代理** ：在目前工作階段內執行的代理。
- **隊友** ：此工作階段自己的[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友。在 v2.1.239 之前，隊友沒有出現在列表中，儘管 Claude 已經可以按名稱訊息傳送至他們。
- **您的其他本地工作階段** ：在同一台機器上執行的 Claude Code 工作階段，包括[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)。工作階段僅在綁定[收件匣通訊端](https://code.claude.com/docs/zh-TW/cross-session-messaging#the-sessions-inbox-socket)時出現。
- **您的雲端工作階段** ：在此工作階段連接到[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)時顯示的[網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)工作階段。Claude Code 在列表中將它們標記為 `cloud`。
- **您在其他機器上的遠端控制工作階段** ：在此工作階段連接到[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)時顯示，並標記為 `Remote Control`。Claude Code 將遠端控制連接已斷開的工作階段的狀態顯示為 `offline`。

此工作階段不是其中一行。如果 Claude 將訊息定址到此工作階段自己的名稱，Claude Code 拒絕它並告訴 Claude 目標是目前工作階段。在 v2.1.239 之前，列表沒有顯示此工作階段的名稱，Claude Code 報告發送給它的訊息為它找不到的代理。 當此工作階段連接到[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)時，Claude Code 從 `/list-agents` 輸出中隱藏您本地工作階段的某些詳細資訊，而不改變 Claude 自己在尋找要訊息傳送的工作階段時看到的內容：

- **工作目錄** ：它省略每個本地工作階段的工作目錄。
- **工作階段名稱** ：它省略任何它無法歸因於某人的工作階段名稱，因此沒有名稱的行讀作 `(unnamed session)`。
- **第一行** ：它省略帶有此工作階段自己名稱的行，除非您在此終端機上輸入該名稱，使用 `--name` 或使用 `/rename`，自從您啟動或最後恢復工作階段以來。

當輸出列出任何內容時，它以說明詳細資訊被隱藏的注釋結束。在工作階段自己的鍵盤上執行 `/rename` 後跟未使用的名稱會給該工作階段一個出現在輸出中的名稱。 Claude Code 首先讀取您的雲端和遠端控制工作階段列表，並在每個列表後停止有限數量的頁面。如果您的帳戶有超過適合的那些工作階段，Claude Code 不會列出較舊的工作階段，Claude 無法按名稱訊息傳送至它們。當發生這種情況時，Claude Code 在列表中說明，Claude 在傳送訊息時看到相同的注釋。 Claude 按名稱定址超出此機器的工作階段，與本地工作階段相同。請參閱[訊息傳送至其他機器上的工作階段](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-sessions-on-other-machines)以了解這些訊息如何傳遞。 工作階段回應您使用 [`/rename`](https://code.claude.com/docs/zh-TW/commands) 命令或 [`--name`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 旗標設定的名稱。當您不設定一個時，Claude Code 自己命名工作階段。對於互動式工作階段，這是[執行工作階段列表](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions)中顯示的名稱。 當您重新命名工作階段時，Claude Code 也會更新您的其他工作階段用來查詢工作階段名稱的共享記錄。如果它無法更新該記錄，它會在 `/rename` 輸出中警告您其他工作階段可能仍然顯示舊名稱。使用 [`--debug`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 執行工作階段，Claude Code 會記錄失敗更新的原因。 當您重新命名工作階段或啟動或恢復互動式工作階段時，使用此機器上另一個即時工作階段已經使用的名稱，Claude Code 將名稱留給已經擁有它的工作階段，並[將您的重新命名為變體](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions)。工作階段可以共享名稱，例如當其中一個執行較早版本的 Claude Code 或共享名稱是 Claude Code 生成的名稱時。除非此工作階段連接到遠端控制，Claude Code 在 `/list-agents` 輸出中顯示每個本地工作階段的工作目錄，因此當它們在不同目錄中執行時，您可以區分同名工作階段。Claude 根據有多少個即時工作階段回應名稱，以兩種方式之一定址訊息：

- **一個工作階段回應名稱** ：Claude Code 僅在名稱上傳遞訊息。
- **多個工作階段共享名稱，或 Claude Code 無法檢查您的工作階段執行的所有地方** ：Claude 為其列表的每一行添加短識別符，並在地址中使用識別符。

### 訊息傳送至其他機器上的工作階段

訊息如何傳遞，以及它是否通過 Anthropic 伺服器，取決於目標工作階段執行的位置：

| 其他工作階段執行的位置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 訊息如何傳遞                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| 在此機器上                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 在 macOS 和 Linux 上通過每個工作階段的通訊端，或在原生 Windows 上通過每個工作階段的具名管道，永遠不通過 Anthropic 伺服器 |
| 在您的另一台機器上                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 通過 Anthropic 伺服器，通過該機器的[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)連接到達                 |
| 在[網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 通過 Anthropic 伺服器，直接到雲端工作階段                                                                                |
| 與您另一台機器上的工作階段開始對話需要 Claude Code v2.1.225 或更新版本以及出現在[列表](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)中的目標。在 v2.1.225 之前，Claude 只能回覆從一個到達的訊息。 您可以訊息傳送至在[列表](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)中顯示為 `offline` 的工作階段，其遠端控制連接已斷開的工作階段。傳送通過，但訊息僅在該工作階段的機器重新連接後到達。Claude 在傳送時被告知這一點。 相同機器傳遞在啟用該功能的任何地方都有效。每個工作階段在磁碟上的檔案中註冊自己。當 Claude 列出或訊息傳送至您的本地工作階段時，Claude Code 讀取這些檔案以找到工作階段，因此兩個工作階段只有在能夠看到相同檔案時才能相互到達。 容器有自己的檔案系統，因此容器內的工作階段和主機上的工作階段無法相互到達。同一容器內的兩個工作階段仍然可以訊息傳送至彼此，包括在[自託管執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments)上。WSL 2 內的工作階段和同一台電腦上的原生 Windows 工作階段也無法相互到達，因為它們在不同的主目錄下註冊並在不同的通訊端類型上監聽。 當此工作階段連接到遠端控制時，當您訊息傳送至您另一台機器上的工作階段時，Claude Code 在該工作階段的對話中顯示訊息，在此工作階段的遠端控制名稱下。該機器上的 Claude 可以回覆該名稱。例如，當此工作階段作為 `laptop-graceful-unicorn` 連接到遠端控制並且您訊息傳送至您的桌面時，您在桌面工作階段中看到 `laptop-graceful-unicorn` 下的訊息。 如果此工作階段在 Claude 傳送至超出此機器的工作階段時未連接到遠端控制，訊息仍然通過，但沒有[回覆地址](https://code.claude.com/docs/zh-TW/cross-session-messaging#what-a-message-looks-like)，因此接收 Claude 無法回答它。Claude 在傳送時被告知這一點。 若要在任何訊息超出此機器之前要求您的批准，請設定 [`isolatePeerMachines`](https://code.claude.com/docs/zh-TW/cross-session-messaging#require-approval-for-cross-machine-messages)。 |                                                                                                                          |

## 工作階段如何處理傳入的訊息

當工作階段 A 傳訊息給工作階段 B 時，Claude Code 會告訴 B 的 Claude 該訊息來自另一個工作階段，而不是來自您，並限制訊息可以執行的操作：

- **無法批准任何事項** ：來自另一個工作階段的訊息永遠不會被視為您的同意，因此無法代表您回答待處理的權限提示。
- **無法變更設定** ：Claude Code 指示接收端的 Claude 永遠不要變更權限設定、`CLAUDE.md` 或其他設定，因為另一個工作階段要求。
- **命令不執行** ：訊息文字中的命令（例如 `/compact`）會以純文字形式送達。Claude Code 永遠不會執行它。
- **權限提示仍會觸發** ：如果根據訊息採取行動需要接收工作階段沒有的權限，您會看到與任何其他工作相同的提示。

### 訊息看起來的樣子

當訊息送達時，Claude Code 會在對話中將其顯示為暗淡的單行預覽，預覽行在之後會保留在對話中。預覽會顯示寄件者的名稱和訊息的第一行，當很長時會用 `…` 截斷，例如 `› Message from @api-worker: Schema migration finished (ctrl+o to expand)`。在 v2.1.247 之前，Claude Code 會完整顯示送達的訊息，而不是預覽。 以下任一方式都可以顯示完整文字：

- 按 `Ctrl+O` 開啟[文字記錄檢視器](https://code.claude.com/docs/zh-TW/interactive-mode#transcript-viewer)，並在寄件者的工作階段名稱下閱讀完整文字。
- 在以 [`--verbose`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 啟動的工作階段中，Claude Code 會顯示完整文字而不是預覽。

預覽只會縮短您看到的內容。無論您是否展開它，Claude 都會讀取完整訊息。 Claude 會收到訊息，其中包含寄件者的名稱和回覆地址，除了[單向跨機器訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-sessions-on-other-machines)，它不包含回覆地址。除了名稱和回覆地址外，接收端的 Claude 會取得訊息的文字，永遠不會取得寄件者的對話歷史記錄或檔案。[訊息傳遞](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-delivery)涵蓋文字中的 `@` 提及。 [子代理](https://code.claude.com/docs/zh-TW/sub-agents)撰寫的訊息會以傳送工作階段的名稱送達，訊息文字中會識別子代理。對它的回覆會到達該工作階段的主要對話，而不是子代理。 這個範例是一個 Claude 寫給另一個的訊息，當您展開它時，其完整文字如下所示：

```
Schema migration finished
The new column is tenant_id, and rebasing on main is safe now.

```

### 控制傳入訊息

設定 [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound) 以選擇工作階段對來自您其他工作階段的訊息執行的操作：

| 值                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 行為                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accept`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Claude Code 將每條訊息傳遞給 Claude                                                                                                                                                          |
| `hold`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Claude Code 為每條訊息顯示通知，不傳遞它。如果稍後應用 `accept`，根據[優先順序規則](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound)，Claude Code 會釋放保留的訊息 |
| `refuse`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Claude Code 丟棄每條訊息，不傳遞它                                                                                                                                                           |
| 除了編輯設定檔外，您可以在 `/config` 列中選擇**來自您其他工作階段的訊息** 的值。Claude Code 會將您選擇的值寫入您的使用者設定。該列需要 Claude Code v2.1.232 或更新版本，當受管設定或 `--settings` 旗標設定金鑰時不會出現，因為使用者設定值在那時不適用。Claude Code 拒絕此金鑰的 `/config crossSessionInbound=value` 簡寫。 若要查看適用的值，請遵循[設定參考](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound)中的 `crossSessionInbound` 優先順序規則。當沒有值適用時，Claude Code 會根據兩個工作階段的權限模式決定每條訊息。它將[略過權限提示](https://code.claude.com/docs/zh-TW/permission-modes#skip-all-checks-with-bypasspermissions-mode)的工作階段分組為一個類別，將所有其他工作階段分組為另一個類別。Plan Mode 在具有可用的略過權限的工作階段中計為略過，[auto](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)、`acceptEdits` 和 `dontAsk` 計為提示： |                                                                                                                                                                                              |

- **接收工作階段提示權限** ：Claude Code 傳遞每條訊息。只有當傳送工作階段識別自己為略過權限提示時，它才會保留一條訊息以供您批准。
- **接收工作階段略過權限提示** ：Claude Code 保留每條訊息以供您批准。只有當傳送工作階段識別自己也略過時，它才會傳遞一條訊息。

當預設保留訊息時，Claude Code 會在接收工作階段中開啟批准對話框。對話框顯示寄件者和預覽：

- **批准** 會將該訊息傳遞給 Claude。
- **拒絕** 或關閉對話框會丟棄它。
- 當對話框在 [`dialogExpiry`](https://code.claude.com/docs/zh-TW/settings-reference#dialogexpiry) 截止時間後仍未回答時，Claude Code 會關閉它並丟棄訊息。截止時間預設為五分鐘。
- 當沒有終端連接到[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)時，Claude Code 會將對話框保持在截止時間之後。連接後，如果對話框在完整截止時間內仍未回答，Claude Code 會關閉它並丟棄訊息。
- 如果此工作階段的權限模式類別在保留訊息時變更，Claude Code 會重新應用傳入規則，傳遞它們現在接受的訊息，並顯示通知。
- 如果設定變更使 `refuse` 在保留訊息時適用，Claude Code 會丟棄每條保留的訊息，並向它可以到達的每個寄件者報告拒絕。

當寄件者是同一機器上的工作階段時，Claude Code 會在接收端保留訊息時在那裡傳送通知給它，以及在接收端稍後傳遞、拒絕或過期時傳送後續通知。通知會到達傳送端的 Claude，因此它知道不要繼續等待另一個工作階段尚未讀取的訊息。 在互動式傳送工作階段中，通知會出現在文字記錄中。[`claude -p`](https://code.claude.com/docs/zh-TW/headless) 寄件者會在[串流輸出](https://code.claude.com/docs/zh-TW/headless#stream-responses)中以[資訊性 `system` 訊息](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkinformationalmessage)的形式接收它。發送給 `claude -p` 寄件者的通知需要 Claude Code v2.1.271 或更新版本。 如果接收端拒絕訊息，寄件者的通知會說接收端不接受跨工作階段訊息，並告訴寄件者的 Claude 不要等待或重新傳送。 Claude Code 最多保留 100 條訊息，與傳遞佇列分開，超過該數量會丟棄最舊的訊息。

### 非互動式工作階段

Claude Code 為 [`claude -p`](https://code.claude.com/docs/zh-TW/headless) 工作階段綁定收件匣套接字，就像互動式工作階段一樣，因此長時間執行的 `-p` 背景工作程式可以接收訊息並出現在列表中。當您以[裸機模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)啟動工作階段時，Claude Code 不會綁定套接字，因此該工作階段無法接收訊息，也不會出現在代理列表中。 `-p` 工作階段無法顯示批准對話框。當[傳入預設](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)在那裡保留訊息時，Claude Code 會為其保留相同的 [`dialogExpiry`](https://code.claude.com/docs/zh-TW/settings-reference#dialogexpiry) 截止時間，預設為五分鐘：

- **在截止時間之前** ：如果模式或設定變更允許訊息，Claude Code 會傳遞它。
- **在截止時間之後** ：Claude Code 會丟棄訊息，並向它可以到達的寄件者報告為已過期。

將 `dialogExpiry` 設定為 `"never"` 以在工作階段結束前保留預設保留的訊息。由明確 `hold` 設定保留的訊息不會過期；Claude Code 只有在稍後應用 `accept` 時才會傳遞它。 當工作階段結束且仍有訊息被保留時，Claude Code 會向它可以到達的每個寄件者報告它們為已過期。在 v2.1.225 之前，`-p` 工作階段中沒有截止時間：保留的訊息會保持保留狀態，除非在執行期間進行權限模式變更會傳遞它，而以保留訊息結束的工作階段不會向其寄件者報告任何內容。 若要讓 `-p` 背景工作程式無人值守地接收訊息，請使用 `--settings` 值中設定為 `accept` 的 `crossSessionInbound` 啟動它。您使用者設定中的 `accept` 也有效，但適用於您執行的每個工作階段。

### 工作階段的收件匣套接字

當您預期的工作階段不在代理列表中、當您想要指令碼或 hook 發佈到工作階段中，或當沙箱化命令無法到達套接字時，請閱讀本節。 Claude Code 為啟用跨工作階段訊息的每個工作階段綁定收件匣套接字，其中機器上的其他工作階段傳遞訊息。套接字是 macOS 和 Linux 上的 Unix 網域套接字（包括 WSL 2 內的 Linux），以及原生 Windows 上的具名管道。有關哪些工作階段類型綁定一個，請參閱[非互動式工作階段](https://code.claude.com/docs/zh-TW/cross-session-messaging#non-interactive-sessions)。 您可以在兩個位置找到套接字的路徑：

- `/status` 在 `Peer address` 列中顯示它。路徑前綴為 `uds:`。
- Claude Code 將其匯出到[hooks](https://code.claude.com/docs/zh-TW/hooks) 和 Bash 命令作為 [`CLAUDE_CODE_MESSAGING_SOCKET`](https://code.claude.com/docs/zh-TW/env-vars#variables) 環境變數：
  - 在以訊息開啟啟動的工作階段中，Claude Code 在任何 hook 執行前匯出變數，包括 `SessionStart`。
  - 每個工作階段匯出其自己的套接字，永遠不會匯出從父工作階段繼承的套接字。

在 macOS 和 Linux 上，Claude Code 將套接字限制為您的作業系統使用者。在原生 Windows 上，它改為要求每個連線首先使用只有您的作業系統使用者可以讀取的金鑰進行驗證。無論哪種方式，在共享機器上，另一個使用者的工作階段無法傳遞到它。 在 macOS 和 Linux 上，Claude Code 也拒絕在無法接受的目錄中建立套接字，例如另一個使用者擁有的目錄，並改為使用私人的每使用者目錄 `/tmp/cc-socks-<uid>`。當它無法接受任何目錄時，工作階段會在沒有收件匣的情況下執行：Claude Code 會顯示通知，`/status` 在其 `Peer address` 列中顯示 `unavailable` 和原因，[`--debug`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 日誌會記錄完整拒絕。 除了套接字的路徑外，Claude Code 還會匯出每個工作階段的權杖作為 [`CLAUDE_CODE_MESSAGING_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars#variables)。發佈到其自己工作階段套接字的指令碼可以發送 `{"type":"auth","token":"<token>"}` 作為其連線的第一行，其中 `<token>` 是 `CLAUDE_CODE_MESSAGING_TOKEN` 的值。Claude Code 是否需要該行取決於平台：

- **macOS 和 Linux，包括 WSL 2** ：該行是選擇性的。Claude Code 接受有或沒有它的連線。
- **原生 Windows** ：該行是必需的。Claude Code 會關閉任何第一行不是有效驗證行的連線，並且不會從該連線傳遞任何內容。

只有在您要發佈的訊息準備好時才開啟連線。Claude Code 會關閉在 30 秒內未發送完整行的連線，因此請先擷取緩慢命令的輸出，然後開啟連線以發送它。 下面的[自有子訊息規則](https://code.claude.com/docs/zh-TW/cross-session-messaging#own-child-messages)說明 Claude Code 何時查詢權杖以及它如何處理無法驗證的訊息。 Claude Code 會透過與任何其他對等訊息相同的[傳入控制](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)執行到達套接字的訊息，但有一個例外和一個先決條件：

- **自有子訊息** ：當沒有 `crossSessionInbound` 值適用時，Claude Code 會傳遞它驗證來自工作階段自己的子程序的訊息，例如 hook 或 Bash 命令發佈回其自己工作階段的套接字。
  - 在 Linux 上（包括 WSL 2 內），Claude Code 即使對於已經退出的子程序也可以透過程序證據進行驗證。在 macOS 上，它只能在發佈程序仍在執行時以這種方式驗證，在 Claude Code 作為程序 ID 1 執行的容器中，它根本沒有程序證據。在原生 Windows 上也沒有。
  - 在 macOS 上發佈程序已退出後，以及在 Claude Code 作為程序 ID 1 執行的容器中，該程序證據遺失，Claude Code 改為驗證在開啟其連線的驗證行中發送工作階段匯出的 [`CLAUDE_CODE_MESSAGING_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars#variables) 的子程序。在原生 Windows 上，該權杖是 Claude Code 驗證自有子訊息的唯一方式。
  - 當 Claude Code 無法以任何方式驗證時，它會將訊息視為任何其他不聲稱權限類別的訊息，因此略過權限提示的工作階段會為您的批准保留它。
- **沙箱化工作階段** ：使用沙箱的 Unix 套接字設定 [`sandbox.network.allowAllUnixSockets` 和 `sandbox.network.allowUnixSockets`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-settings) 控制 Bash 命令是否可以從[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)內到達套接字。

## 限制跨工作階段訊息傳送

除了每條訊息的預設值，您可以以兩種方式縮小訊息傳送。在任何訊息離開機器之前要求您的批准，或為工作階段或組織關閉訊息傳送。

### 要求批准跨機器訊息

設定 [`isolatePeerMachines`](https://code.claude.com/docs/zh-TW/settings-reference#isolatepeermachines) 為 `true` 以要求您的明確批准，在任何 `SendMessage` 到達超出此機器的工作階段之前：

```
{
  "isolatePeerMachines": true
}

```

設定此項後，Claude Code 在 Claude 的訊息到達超出此機器的工作階段之前要求您的批准，即使在 `bypassPermissions` 模式中，它跳過普通權限提示。任何設定範圍中的 `true` 適用，因此簽入的專案檔案可以打開要求但不能關閉。Claude Code 不提示同一台機器上工作階段之間的訊息。

### 關閉跨工作階段訊息傳送

接收和傳送是分開的控制，因此關閉您需要的任一方向，或兩者。使用 `crossSessionInbound` 用於到達的訊息，以及權限規則用於 Claude 可以傳送或列出的內容：

- **停止接收** ：設定 `crossSessionInbound` 為 `refuse`，Claude Code 在未傳遞的情況下丟棄入站對等訊息。從專案或本地設定，`refuse` 適用於每個其他來源，從您的使用者設定，它適用，除非受管設定或 `--settings` 旗標設定值。
- **停止傳送和列出** ：新增[權限拒絕規則](https://code.claude.com/docs/zh-TW/permissions#tool-specific-permission-rules)命名 `SendMessage` 和 `ListAgents`。兩者都採用沒有指定符的裸工具名稱。

管理員可以在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中為組織關閉兩側，結合拒絕規則與 `refuse`：

```
{
  "permissions": {
    "deny": ["SendMessage", "ListAgents"]
  },
  "crossSessionInbound": "refuse"
}

```

設定此項後，Claude Code 仍然為每個工作階段綁定收件匣通訊端，但丟棄到達它的每條訊息而不向 Claude 傳遞任何內容。拒絕 `SendMessage` 也移除訊息傳送至子代理和代理團隊隊友，因為相同工具服務兩者。拒絕工作階段在其自己的 `/status` 或同一台機器上其他工作階段的列表中顯示無可見變更，因此若要確認它，請檢查適用於該工作階段的設定檔而不是其狀態。

## 可用性

跨工作階段訊息傳送需要 macOS、Linux 和 WSL 2 上的 Claude Code v2.1.224 或更新版本，以及原生 Windows 上的 v2.1.234 或更新版本。可用性以及 Claude 可以訊息傳送的工作階段也取決於您的作業系統、提供者和設定：

- **作業系統** ：在 macOS、Windows 和 Linux 上可用，包括 WSL 2 內的 Linux。
- **此機器上的工作階段** ：在每個提供者上可用，包括 Amazon Bedrock、Claude Platform on AWS、Google Cloud 的 Agent Platform 和 Microsoft Foundry，以及在執行時[功能旗標擷取](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)關閉的工作階段。在這些提供者上，以及旗標擷取關閉時，相同機器訊息傳送需要 Claude Code v2.1.248 或更新版本。Claude Code 通過您機器上的[每個工作階段通訊端](https://code.claude.com/docs/zh-TW/cross-session-messaging#the-sessions-inbox-socket)傳遞這些訊息，永遠不通過 Anthropic 伺服器。 若要停止工作階段接收它們，請設定 [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/cross-session-messaging#turn-off-cross-session-messaging) 為 `refuse`。
- **超出此機器的工作階段** ：Claude 從連接到遠端控制的工作階段找到您的[網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 工作階段和您在其他機器上的工作階段，這需要 claude.ai 登入作為此工作階段的活躍驗證以及其他[遠端控制要求](https://code.claude.com/docs/zh-TW/remote-control#requirements)。Claude 無法使用 API 金鑰或在 Amazon Bedrock、Claude Platform on AWS、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上找到這些工作階段。

若要檢查工作階段，輸入 `/list-agents`，也可用作 `/peers`。結果將沒有該功能的工作階段與某些較窄的東西阻止訊息的工作階段分開，例如缺少 `SendMessage` 工具或拒絕的傳送：

- **`/list-agents`無法識別** ：工作階段沒有跨工作階段訊息傳送。通過上面的要求進行工作，從 `claude --version` 開始以了解版本要求。
- **`/list-agents`有效但傳送未到達** ：訊息傳送已啟用，某些較窄的東西適用：
  - **拒絕規則** ：[權限拒絕規則](https://code.claude.com/docs/zh-TW/cross-session-messaging#turn-off-cross-session-messaging)移除 `SendMessage` 和 `ListAgents` 工具。
  - **入站控制** ：[接收工作階段的入站控制](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)可以保留或丟棄您傳送給它的內容。
  - **雲端工作階段缺失** ：雲端工作階段僅在此工作階段連接到[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)時出現。
  - **其他機器工作階段缺失** ：您另一台機器上的工作階段僅在它執行[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)並且此工作階段也連接時出現。
  - **其他機器工作階段`offline`** ：訊息傳送至列為 `offline` 的工作階段通過，但[僅在該工作階段的機器重新連接後到達](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-sessions-on-other-machines)。
  - **較舊的雲端或其他機器工作階段缺失** ：Claude Code [首先讀取這些工作階段列表，並在有限數量的頁面後停止](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)，因此 Claude 無法按名稱訊息傳送至超過它們的工作階段。
  - **啟動對話** ：[訊息傳送至其他機器上的工作階段](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-sessions-on-other-machines)涵蓋與超出此機器的工作階段啟動對話。

在具有訊息傳送的工作階段中，`/status` 也顯示 `Peer address` 行，帶有工作階段自己的收件匣地址，或 `unavailable` 和原因，當 Claude Code [無法設定收件匣](https://code.claude.com/docs/zh-TW/cross-session-messaging#the-sessions-inbox-socket)時。

## 限制

此處的限制是訊息傳送頻道本身的屬性，在該功能執行的任何地方適用。有關平台和提供者差距，請改為參閱[可用性](https://code.claude.com/docs/zh-TW/cross-session-messaging#availability)。

- **純文字只** ：Claude 僅跨工作階段傳送純文字。結構化[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)協議訊息保留在團隊內。
- **相同機器訊息大小有上限** ：Claude Code 拒絕訊息到此機器上的工作階段，一旦其序列化形式超過約一百萬個字元。拒絕[命名確切大小](https://code.claude.com/docs/zh-TW/errors#message-too-large-for-cross-session-delivery)。沒有任何內容到達接收工作階段。
- **對一個工作階段的快速突發在寄件者處被拒絕** ：一旦對此機器上工作階段的快速訊息突發達到該工作階段的收件匣接受的內容，Claude Code 拒絕傳送工作階段中的進一步傳送。[拒絕命名突發](https://code.claude.com/docs/zh-TW/errors#too-many-messages-to-this-session-just-now)並告訴 Claude 將其餘部分批處理為一條訊息或等待。在 v2.1.236 之前，Claude Code 報告這些傳送為已傳送，而接收工作階段丟棄它們。
- **訊息迴圈被限制** ：在接收工作階段中，Claude Code 速率限制每個寄件者的重複訊息，丟棄在短時間窗口內到達的相同重複，並最多為 Claude 讀取排隊 50 條接受的訊息。因此，兩個工作階段之間的訊息迴圈自行停止。當速率限制、重複檢查或佇列上限丟棄來自此機器上互動式工作階段的訊息時，Claude Code 告訴該工作階段哪一個丟棄了它，並告訴其 Claude 不要立即重新傳送。

## 相關資源

- [子代理](https://code.claude.com/docs/zh-TW/sub-agents#resume-subagents)和[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams#messages-between-agents)：單一工作階段或團隊內的訊息傳送
- [背景代理](https://code.claude.com/docs/zh-TW/agent-view)：分派和監視您可能訊息傳送的平行工作階段
- [遠端控制](https://code.claude.com/docs/zh-TW/remote-control)：連接此工作階段以到達您在其他機器上的工作階段
- [設定](https://code.claude.com/docs/zh-TW/settings-reference#all-settings)：`crossSessionInbound`、`isolatePeerMachines` 和 `dialogExpiry`
- [權限模式](https://code.claude.com/docs/zh-TW/permission-modes)：入站預設的兩個類別背後的模式
- [工具參考](https://code.claude.com/docs/zh-TW/tools-reference)：工具表中的 `ListAgents` 和 `SendMessage` 行
- [平行執行代理](https://code.claude.com/docs/zh-TW/agents)：比較 Claude Code 執行多個代理的方式

是否 助手
