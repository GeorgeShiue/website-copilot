Agent view（使用 `claude agents` 開啟）是所有背景工作階段的一個螢幕：什麼正在執行、什麼需要您的輸入，以及什麼已完成。分派新工作階段，一目瞭然地查看它們的狀態，而不是滾動瀏覽記錄，並且只在需要時才介入。每個背景工作階段都是一個完整的 Claude Code 對話，在沒有終端連接的情況下持續執行，因此您可以隨時開啟、回覆和離開。 ![終端中的 Agent view：標題顯示 Claude Code v2.1.140、模型、工作目錄和摘要計數。工作階段分組在'需要輸入'、'執行中'和'已完成'下，底部有分派輸入，頁尾有快捷鍵提示。](https://mintcdn.com/claude-code/1B48Qz2Z9hac4SLG/images/agent-view-light.png?fit=max&auto=format&n=1B48Qz2Z9hac4SLG&q=85&s=7a186c96ed47d6700d084d77e786be65)
> # Image-1
>
> **圖片摘要：**
> Claude Code 介面顯示待處理、進行中與已完成的開發任務。
>
> **主要元素：**
> 1. 實體: 程式碼代理介面, 模型版本資訊, API 重試任務, 深色模式設定, GitHub 拉取請求
> 2. OCR文字:
> Claude Code v2.1.140
> Opus 4.7 (1M context) · /Users/jane/code/web-app
> 1 awaiting input · 1 working · 2 completed
>
> Needs input
> ✳ api client retries    Should the API client retry on 429, or surface the error to the caller?    12m
>
> Working
> * dark mode toggle    Editing src/components/Settings.tsx    3m
>
> Completed
> • flaky checkout test    github.com/acme/web-app/pull/142    40m
> • cli flag docs    Updated 4 docs pages with the new CLI flags    1h
>
> › describe a task for a new session
>
> enter to open · space to reply · ctrl+x to delete · ? for shortcuts
> 3. 主題標籤: Claude Code, API 重試, 深色模式, CLI 旗標, Web 應用程式
>
> **頁面關聯：**
> Claude Code 開發任務面板；web-app 專案與 GitHub Pull Request 142

![終端中的 Agent view：標題顯示 Claude Code v2.1.140、模型、工作目錄和摘要計數。工作階段分組在'需要輸入'、'執行中'和'已完成'下，底部有分派輸入，頁尾有快捷鍵提示。](https://mintcdn.com/claude-code/1B48Qz2Z9hac4SLG/images/agent-view-dark.png?fit=max&auto=format&n=1B48Qz2Z9hac4SLG&q=85&s=a5bed7434bae368faea3a8f023b52aa2)
> # Image-2
>
> **圖片摘要：**
> Claude Code 介面按 Needs input、Working、Completed 分列開發任務。
>
> **主要元素：**
> 1. 實體: Claude Code 開發介面,API 重試議題,設定元件,web-app 專案,GitHub 拉取請求
> 2. OCR文字:
> Claude Code v2.1.140
> Opus 4.7 (1M context) · /Users/jane/code/web-app
> 1 awaiting input · 1 working · 2 completed
> Needs input
> ✳ api client retries　Should the API client retry on 429, or surface the error to the caller?　12m
> Working
> ✳ dark mode toggle　Editing src/components/Settings.tsx　3m
> Completed
> • flaky checkout test　github.com/acme/web-app/pull/142　40m
> • cli flag docs　Updated 4 docs pages with the new CLI flags　1h
> › describe a task for a new session
> enter to open · space to reply · ctrl+x to delete · ? for shortcuts
> 3. 主題標籤: API 重試,暗色模式,CLI 旗標,軟體開發,任務佇列
>
> **頁面關聯：**
> Claude Code／web-app 專案／開發任務佇列
當您有多個獨立任務 Claude 可以在不需要您監看每一步的情況下執行時，請使用 agent view。分派一個錯誤修復、一個拉取請求審查和一個不穩定測試調查作為三行，在另一個視窗中繼續工作，並在某一行顯示需要您或有結果時檢查。 當您想在任何代理的工作階段中更直接地工作時，附加到該行以進入完整對話。 若要比較 agent view 與 subagents、agent teams 和 worktrees，請參閱 [平行執行代理](https://code.claude.com/docs/zh-TW/agents)。Agent view 在您的機器上執行工作階段，您分派每一個；若要讓 Claude 從一個對話開始並在雲端追蹤平行工作階段，請參閱 [Projects](https://code.claude.com/docs/zh-TW/claude-projects)。 Agent view 處於研究預覽版本。隨著功能的發展，介面和快捷鍵可能會改變。

## 快速開始

本逐步解說涵蓋核心 agent view 迴圈：分派工作、觀看其列更新（Claude 正在工作）、查看以檢查並回覆，以及附加到完整對話。您分派的工作階段在關閉 agent view 後會繼續執行，因此您可以離開並稍後返回。 1 開啟 agent view 從您的 shell，執行：

```
claude agents

```

如果您尚未接受該目錄的[工作區信任對話](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)，Claude Code 會在 agent view 開啟前顯示它，與 `claude` 顯示的對話相同。接受以儲存工作區的信任並繼續。如果您拒絕，Claude Code 會退出而不開啟 agent view。Agent view 開啟，底部有輸入框，隨著工作階段啟動，表格會填入。隨時按 `Esc` 返回您的 shell；如果您透過背景化工作階段 `←` 開啟了 agent view，`Esc` 會改為返回該對話。您的工作階段在您離開時繼續執行，下次開啟 agent view 時會重新出現。 2 分派工作階段 輸入描述工作的提示並按 `Enter`。新的背景工作階段在該工作上啟動並顯示為一列，顯示它是否正在工作、等待您或已完成。新工作階段使用 agent view 標題中顯示的模型。[它啟動時所在的權限模式](https://code.claude.com/docs/zh-TW/agent-view#permission-mode-model-and-effort)取決於您如何開啟 agent view。您在此輸入的每個提示都會啟動自己的新工作階段。輸入另一個提示並按 `Enter` 會在第一個工作階段旁邊啟動第二個工作階段，而不是向其發送後續訊息。您可以以這種方式並行執行多個工作階段。每個工作階段獨立使用您的訂閱配額，因此在一次分派許多工作階段之前，請參閱[限制](https://code.claude.com/docs/zh-TW/agent-view#limitations)。 3 查看和回覆 使用箭頭鍵選擇一列，然後按 `Space` 開啟查看面板。它顯示工作階段的最新輸出或它正在等待的問題，而不是完整的文字記錄。輸入回覆並按 `Enter` 發送，無需離開 agent view。 4 附加和分離 在一列上按 `Enter` 或 `→` 以在需要完整對話時附加。工作階段接管終端作為完整的互動式 Claude Code 工作階段。在空提示上按 `←` 分離並返回表格。 5 帶入現有工作階段 這個步驟需要一個執行中的工作階段。如果您遵循了之前的步驟，您在此終端中沒有開啟的工作階段，因此請在另一個終端中開啟一個常規 `claude` 工作階段並先向其發送訊息。要將您已開啟的工作階段移入 agent view，在其中執行 `/bg`，或在空提示上按 `←` 以在一個步驟中背景化工作階段並開啟 agent view。在沒有訊息的全新工作階段中，`/bg` 會要求您先發送訊息，而 `←` 可以立即運作。工作階段繼續執行並顯示為一列，與您分派的工作階段並排。 您可以使用 `claude agents` 作為主要進入點而不是 `claude`：從 agent view 分派每個工作，在需要完整對話時附加，然後按 `←` 返回表格。 在常規 `claude` 工作階段內，提示頁尾的 `←` 提示會計算正在等待您的背景 agent 數量，例如 `← 2 agents`，當沒有任何 agent 需要輸入時會返回 `← for agents`。超過 99 的計數顯示為 `99+`。當終端獲得焦點時，計數大約每十秒刷新一次，當焦點返回時立即刷新。當計數移動時以及當 agent 完成時，它會短暫改變顏色，當背景工作階段完成且沒有任何工作階段需要您的輸入時，它會短暫顯示已完成的數量，例如 `← 2 done`。當啟用了 [`prefersReducedMotion` 設定](https://code.claude.com/docs/zh-TW/settings-reference#prefersreducedmotion)時，兩個閃爍都會關閉，並且在[螢幕閱讀器模式](https://code.claude.com/docs/zh-TW/accessibility)中隱藏提示。

## 使用代理檢視監控工作階段

執行 `claude agents` 以開啟代理檢視。它會接管整個終端機，並按狀態列出每個工作階段，已釘選的工作階段和需要您的工作階段位於頂部。每一列顯示工作階段的名稱、目前活動和年齡，年齡從工作階段建立時開始計算；已完成的工作階段的年齡會凍結在執行所花費的時間。 名稱會以該工作階段中由 [`/color`](https://code.claude.com/docs/zh-TW/commands) 設定的顏色著色，包括當您使用 `←` 或 `/background` [背景執行工作階段](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session) 時。 根據預設，清單會顯示您已啟動的每個背景工作階段，跨越所有專案。在一個儲存庫中工作的工作階段和在不同 worktree 中工作的另一個工作階段都會出現在這裡，無論您從哪個目錄開啟代理檢視。若要將清單縮小到一個專案，請傳遞 `--cwd`：

```
claude agents --cwd ~/projects/my-app

```

這只會顯示在該目錄下啟動的工作階段。它仍然會列出已 [移入 worktree](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated) 在 `~/projects/my-app/.claude/worktrees/` 下的工作階段。 您在其他終端機中開啟的互動式工作階段不會出現，直到您 [背景執行它們](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)。[子代理](https://code.claude.com/docs/zh-TW/sub-agents) 和 [隊友](https://code.claude.com/docs/zh-TW/agent-teams) 工作階段產生的不會列為單獨的列。

```
Pinned
  ✽ clawd walk cycle          Drawing the walk-cycle sprite frames          3m

Ready for review
  ∙ jump physics              Opened PR with collision fix                 #2048  2h

Needs input
  ✻ power-up design           double jump or wall climb?                    1m

Working
  ✽ collision detection       Adding swept-AABB checks to CollisionSystem   2m
  ✢ playtest level 3          run 12 · all checkpoints cleared           in 4m

Completed
  ✻ title screen              result: menu, options, and credits done       9m
  ∙ sound effects             result: 14 SFX exported to assets/audio       4h
  … 6 more

```

### 讀取工作階段狀態

每一列開頭的圖示，其顏色和動畫顯示工作階段的狀態：

| 狀態                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 圖示顯示為                                                                                                         | 意義                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Working                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 動畫                                                                                                               | Claude 正在主動執行工具或產生回應                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Needs input                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 黃色                                                                                                               | Claude 正在等待只有您才能提供的內容：問題的答案、權限決定，或只有您才能回答的其他提示，例如 [沙箱](https://code.claude.com/docs/zh-TW/sandboxing) 提示以允許網路主機或 MCP 伺服器的 [輸入請求](https://code.claude.com/docs/zh-TW/mcp#respond-to-mcp-elicitation-requests)。需要附加終端機的命令，例如 `/install-github-app` 或 `/mcp` 設定清單，[也會在此處保留無人值守的工作階段](https://code.claude.com/docs/zh-TW/agent-view#attach-to-a-session) |
| Idle                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 變暗                                                                                                               | 工作階段沒有任何工作要做，已準備好接收您的下一個提示                                                                                                                                                                                                                                                                                                                                                                                                   |
| Completed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 綠色                                                                                                               | 任務成功完成                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Failed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 紅色                                                                                                               | 任務以錯誤結束                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Stopped                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 灰色                                                                                                               | 您使用 `Ctrl+X` 或 `claude stop` 停止了工作階段，[其程序從 Claude Code 外部結束](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)，或 [在背景服務關閉時結束](https://code.claude.com/docs/zh-TW/agent-view#sessions-show-as-failed-after-shutdown)                                                                                                                                                                                |
| 另外，圖示的形狀顯示基礎程序是否正在執行：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 形狀                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 意義                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | ---                                                                                                                |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `✻` 或動畫 `✽`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 工作階段程序處於活動狀態並立即回應                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `∙`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 程序已結束。您仍然可以查看該列，當您回應或附加時，Claude 會從中斷的地方重新啟動                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `✢`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | [`/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks) 工作階段在迭代之間休眠。該列顯示其執行計數和倒數計時 |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 可能出現在列右邊緣的 `#N` 或 `!N` 標籤是指向工作階段的 [拉取請求或合併請求](https://code.claude.com/docs/zh-TW/agent-view#pull-request-status) 的連結，不是狀態圖示的一部分。 終端機標籤標題在代理檢視開啟時顯示等待輸入計數：當工作階段需要輸入時為 `2 awaiting input · claude agents`，或當沒有時為 `claude agents`。 若要從指令碼或其他程式讀取工作階段狀態，請使用 [`claude agents --json`](https://code.claude.com/docs/zh-TW/agent-view#read-session-state-from-a-script)，而不是 `~/.claude/jobs/` 下的檔案。 當代理檢視開啟時，Claude Code 也會透過您設定的 [終端機通知頻道](https://code.claude.com/docs/zh-TW/terminal-config#get-a-terminal-bell-or-notification) 發送通知，當本機背景工作階段開始需要您的輸入、完成或失敗時。在排程上執行的工作階段，例如 [`/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks) 工作階段，只在需要您的輸入時通知。通知使用與 Claude Code 其餘部分相同的 [`preferredNotifChannel` 設定](https://code.claude.com/docs/zh-TW/settings-reference#preferrednotifchannel)，並使用 `agent_needs_input` 或 `agent_completed` 類型觸發 [`Notification` hook](https://code.claude.com/docs/zh-TW/hooks#notification)。 背景工作階段不需要任何開啟的終端機即可繼續工作。單獨的 [監督程序](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process) 執行它們，因此您可以關閉代理檢視、關閉您的 shell，或啟動新的互動式工作階段，您分派的工作會繼續進行。 工作階段狀態透過自動更新和監督程序重新啟動在磁碟上持續存在。當您的機器休眠時，工作階段也會被保留。它們的程序在喚醒時繼續執行，監督程序會重新連接到它們，而不是將時間間隙視為閒置。關閉仍會停止執行中的工作階段；請參閱 [工作階段在關閉後顯示為失敗或停止](https://code.claude.com/docs/zh-TW/agent-view#sessions-show-as-failed-after-shutdown) 以了解如何復原它們。 在機器休眠時正在中途回應的工作階段可能會回來無回應。當您開啟已停止回應的工作階段時，監督程序會重新啟動其程序，工作階段會從中斷的地方繼續中斷的回應。 |                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

### 列摘要

每列中的單行摘要由 [Haiku 級模型](https://code.claude.com/docs/zh-TW/model-config) 產生，因此該列可以告訴您工作階段在做什麼、需要什麼或產生了什麼，而無需開啟文字記錄。當工作階段主動工作時，列文字最多每 15 秒從工作階段自己的最近輸出更新一次，無需發送模型請求，模型在每個回合結束時寫入新摘要。 工作中的列顯示工作階段說它在做什麼，被阻止的列顯示它在問什麼問題。在長回合期間，模型也會每隔幾分鐘重寫摘要，以便繁忙的列不會繼續顯示過時的摘要。摘要文字填滿列的剩餘寬度；開啟 [查看面板](https://code.claude.com/docs/zh-TW/agent-view#peek-and-reply) 以讀取終端機邊緣裁剪的句子。 當清單 [按目錄分組](https://code.claude.com/docs/zh-TW/agent-view#organize-the-list) 時，摘要以工作階段的狀態開頭，作為彩色單詞，例如 `Needs input · double jump or wall climb?`。在預設狀態分組中，群組標題已命名狀態，因此列只顯示摘要。 回合結束摘要和每個中途重寫都是透過您的正常提供者進行的一個簡短 Haiku 級請求，按照與工作階段本身相同的 [資料使用條款](https://code.claude.com/docs/zh-TW/data-usage) 計費和處理。模型重寫之間的 15 秒更新重複使用工作階段自己的輸出，不發送請求。在沒有設定 Haiku 級模型的第三方提供者或閘道上，請求使用工作階段的主要模型；設定 [`ANTHROPIC_DEFAULT_HAIKU_MODEL`](https://code.claude.com/docs/zh-TW/model-config#environment-variables) 以選擇一個。

### 拉取請求狀態

當工作階段 [開啟拉取請求](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated) 時，Claude Code 在列的右邊緣新增標籤，連結到拉取請求：

- Claude Code 將標籤寫為拉取請求的 `#1234` 和 GitLab 合併請求的 `!1234`。
- Claude Code 發出連結，即使它無法偵測超連結支援，例如透過 SSH 或 tmux。設定 [`FORCE_HYPERLINK=0`](https://code.claude.com/docs/zh-TW/env-vars) 以將標籤呈現為純文字。
- 在您向工作階段發送後續內容後，Claude Code 會在列返回即時進度時保留標籤。

在現有拉取請求上工作的工作階段以相同方式連結到它。Claude Code 根據 Claude 執行的命令以不同方式尋找拉取請求：

- 當 Claude 使用 `gh` 編輯、評論、關閉或標記拉取請求為就緒時，Claude Code 連結命令自己的輸出命名的拉取請求。其捕獲的輸出未命名拉取請求的 `gh` 命令不會建立連結；`gh pr merge` 是常見情況，因為它只將其結果列印到互動式終端機。
- 當 Claude 使用 `gh pr checkout` 簽出拉取請求或推送到分支時，Claude Code 使用 `gh pr view` 查詢分支並連結其開啟的拉取請求。
- 當 Claude 推送時拉取請求不需要存在：Claude Code 在同一目錄中執行最多五個稍後的 `git`、`gh`、`glab` 或 `curl` 命令後重試分支查詢，因此在推送後建立的拉取請求，包括 Claude 透過 GitHub REST API 建立的拉取請求，在重試找到時連結。

當工作階段連結到多個拉取請求時，標籤顯示計數，例如 `3 PRs`，按最需要關注的開啟拉取請求著色。開啟 [查看面板](https://code.claude.com/docs/zh-TW/agent-view#peek-and-reply) 以查看它們全部。 拉取請求編號按其狀態著色：

| 顏色                                                                                   | 拉取請求狀態               |
| -------------------------------------------------------------------------------------- | -------------------------- |
| 黃色                                                                                   | 等待檢查或審查，或檢查失敗 |
| 綠色                                                                                   | 檢查通過且沒有審查阻止     |
| 紫色                                                                                   | 已合併                     |
| 灰色                                                                                   | 草稿或已關閉               |
| 對於以拉取請求結束的任務，檢查此標籤以獲得結果：當其編號變為綠色時審查並合併拉取請求。 |                            |

### 查看和回應

在選定的列上按 `Space` 以開啟查看面板。它開啟時顯示列在終端機邊緣截斷的句子，該句子是哪一個取決於工作階段的狀態：

- 等待您的工作階段：它要求的確切問題，在回應輸入上方
- 已完成的工作階段：其結果
- 工作中的工作階段：其完整狀態句子

任何連結到工作階段的拉取請求都會列在下方。對於等待您的工作階段，下方的一行（例如 `waiting 3m`）顯示它已等待多長時間，這是面板中唯一顯示的時間。列右邊緣的年齡是不同的數字：它從工作階段啟動時開始計算。 大多數時候查看面板就足夠了，您不需要開啟完整文字記錄。 在查看面板中輸入回應，然後按 `Enter` 將其發送到該工作階段。當工作階段提出帶有預定義選擇的問題時，查看面板將它們顯示為編號清單，您可以按數字鍵選擇一個。權限提示顯示為描述工作階段想要執行的內容的文字，沒有編號選項。輸入回應以回答它，或附加以使用標準提示回答。對於其他被阻止的工作階段，按 `Tab` 以填充輸入建議的回應，您可以在發送前編輯。在回應前加上 `!` 以改為發送 Bash 命令。 當 [`PermissionRequest`](https://code.claude.com/docs/zh-TW/hooks#permissionrequest) 或 [`PreToolUse`](https://code.claude.com/docs/zh-TW/hooks#pretooluse) hook 返回 Claude Code 無法驗證工作階段要求的呼叫的輸出時，列顯示 hook 事件和 `hook output invalid:` 以及驗證錯誤，然後是待處理請求的文字。對於以其他方式失敗的 hook，列說 hook 失敗。工作階段仍然等待相同的請求。 無法傳遞的回應，因為背景服務無法到達或發送失敗，會被保存並在其程序再次啟動時作為下一個提示發送到工作階段，錯誤訊息說回應已保存。以 `!` 為前綴的回應不會被保存，因為保存的文字會作為純提示而不是 Bash 命令到達工作階段。 啟用 [語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation) 後，在回應輸入聚焦時按住或點擊您的推送通話鍵以聽寫回應而不是輸入。相同的方式適用於代理檢視底部的分派輸入。 使用 `↑` 和 `↓` 查看相鄰工作階段而無需關閉面板，或使用 `→` 附加。

### 附加到工作階段

在選定的列上按 `Enter` 或 `→` 以附加。代理檢視被完整互動式工作階段取代。當您附加時，Claude 發佈您離開時發生的簡短回顧。 附加時，工作階段的行為就像任何其他 Claude Code 工作階段：[命令](https://code.claude.com/docs/zh-TW/commands)、鍵盤快捷鍵和功能都可以工作，除了下面的例外。 附加時，`/install-github-app` 和 [`/mcp`](https://code.claude.com/docs/zh-TW/mcp) 設定清單正常工作，因為終端機上有人可以完成它們的對話。當沒有人附加時，這些命令無法開啟它們的對話，因此工作階段在代理檢視中的 `Needs input` 下出現，列如 `open this session to manage MCP servers`，文字記錄回應說相同的內容。附加並再次執行命令以繼續；當您附加時，需要輸入的列會清除。`/mcp reconnect <server>`、`/mcp enable` 和 `/mcp disable` 無論如何都可以在不附加的情況下工作。 附加的工作階段始終以 [全螢幕模式](https://code.claude.com/docs/zh-TW/fullscreen) 呈現，無論您的 `tui` 設定如何，因為背景工作階段沒有終端機捲軸可附加到。使用 `PgUp`、`PgDn` 或滑鼠滾輪捲動，按 `Ctrl+O` 進入文字記錄模式。您終端機的原生捲動和 tmux 複製模式只顯示目前檢視區，與執行任何全螢幕應用程式時相同。 在空提示上按 `←`，或執行 `/exit`，以分離並返回代理檢視，無論您是從代理檢視開啟工作階段還是從 shell 使用 `claude attach <id>`。 當 [`/btw` 覆蓋層](https://code.claude.com/docs/zh-TW/interactive-mode#side-questions-with-%2Fbtw) 開啟時，`←` 也會分離。需要 Claude Code v2.1.257 或更新版本。仍在回答的側問題在您離開時繼續執行。下次您附加時，覆蓋層會重新開啟它，或使用其答案。 在 Windows 上，如果您在附加後約半秒內按 `←`，Claude Code 會顯示 `Ambiguous ←, press again to detach`，因為在該視窗中終端機可以重新傳遞您附加前的按下。再次按 `←` 以分離。 `Ctrl+Z` 也會分離但會回到您開始的地方：如果您從那裡附加則為代理檢視，或如果您執行 `claude attach` 則為您的 shell。當對話有焦點且不回應 `←` 時使用 `Ctrl+Z`。 `Ctrl+C` 在附加時保持其標準中斷行為：它取消執行中的回應或 `!` shell 命令，而不是分離。在空提示上按 `Ctrl+C` 兩次會分離，與任何工作階段中相同。 分離永遠不會停止背景工作階段：`←`、`Ctrl+Z`、`/exit` 和雙 `Ctrl+C` 或雙 `Ctrl+D` 都會讓它執行。若要從內部結束工作階段，請執行 `/stop`。

#### 在不離開終端機的情況下切換工作階段

在前景執行的工作階段中，您在終端機中啟動的工作階段而不是從代理檢視附加的工作階段，在空提示上按 `←` 會背景執行它並開啟代理檢視，該列已選定，因此您可以在不離開終端機的情況下切換工作階段。相同的單次按下會分離附加的工作階段。 如果您在刪除提示的最後文字或移動提示歷史記錄後立即按 `←`，Claude Code 會要求您確認：第一次按下顯示 `Press ← again to open agents`，或在附加的工作階段中顯示 `Press ← again to go back to agents`，第二次按下切換。 當 `←` 背景執行前景工作階段時，代理檢視在清單上方顯示 `Your conversation moved to the background`，該工作階段的列已選定。從那裡：

- 按 `Enter` 重新開啟對話。
- 按 `Esc` 撤銷切換並返回對話。如果 `Esc` 顯示 `Still starting — try again in a moment`，背景工作階段還沒準備好，所以稍後再按一次 `Esc`。
- 按 `Ctrl+C` 兩次以退出到您的 shell。

當 Claude Code 無法重新開啟對話時，它會退出並列印一個 `claude --resume` 命令來繼續它。 [Claude 的任務清單](https://code.claude.com/docs/zh-TW/interactive-mode#task-list) 隨著對話移動到背景工作階段，因此當您返回該列時檢查清單是完整的。 您按 `←` 的列在使用箭頭鍵或滑鼠移動選擇後也保持粗體、未變暗的名稱，因此您可以判斷您來自哪個工作階段。 如果在您按 `←` 時工具正在執行，Claude Code 會等待最多約十秒鐘讓它完成，然後背景執行，Claude 在背景工作階段中繼續回應。再次按 `←` 以立即背景執行而不是等待。當進行中的工作無法轉移到背景工作階段時，Claude Code 首先顯示 `Background this session?` 對話，與 [`/background`](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session) 相同。 十秒限制在 [前景子代理](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background) Claude 在對話中啟動的仍在執行時不適用。Claude Code 繼續等待以便它們的工作轉移，並在等待時顯示 `Still backgrounding after the current tool` 通知。再次按 `←` 以在不等待的情況下背景執行，這會從頭開始重新啟動這些子代理。Claude Code 不會等待 [動態工作流程](https://code.claude.com/docs/zh-TW/workflows) 正在執行的子代理。當工作流程有子代理執行時，Claude Code 改為顯示 `Background this session?` 對話。 Claude Code 在您的提示輸入中有未發送的文字時不會背景執行工作階段，因為文字會保留在您終端機的輸入框中，不會移動到背景工作階段。如果在 Claude Code 等待背景執行工作階段時輸入到輸入中，它會以 `Backgrounding cancelled — you have unsent text in the input. Send it or clear it, then press ← again.` 取消切換。 按 `←` 會建立工作階段的列，即使對話還沒有訊息，所以 `→` 仍然會返回到它。 您可以使用 `/config` 中的 `leftArrowOpensAgents` 設定關閉此快捷鍵。

### 組織清單

代理檢視分組工作階段，使需要輸入的工作階段位於頂部，`Ready for review` 和 `Needs input` 在 `Working` 和 `Completed` 上方。這些群組名稱不與上面的 [狀態](https://code.claude.com/docs/zh-TW/agent-view#read-session-state) 一一對應：當工作階段有開啟的拉取請求時，它會移動到 `Ready for review`，`Completed` 收集已完成、失敗和停止的工作階段。 按 `Ctrl+S` 改為按目錄分組。您的選擇在執行中持續存在。 在群組內：

- 按 `Ctrl+T` 將工作階段釘選到頂部並 [在閒置時保持其程序執行](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)
- 按 `Shift+↑` 或 `Shift+↓` 重新排序工作階段
- 按 `Ctrl+R` 重新命名工作階段
- 在群組標題上按 `Enter` 以摺疊它

若要從清單中移除工作階段，按 `Ctrl+X` 停止它，然後在兩秒內再次按 `Ctrl+X` 以刪除它。在群組標題上按 `Ctrl+X` 會在確認後刪除該群組中的每個工作階段。 第二次按下會刪除工作階段，即使停止嘗試失敗，例如因為 [背景服務沒有回應](https://code.claude.com/docs/zh-TW/agent-view#agent-view-says-the-background-service-did-not-respond)：確認會再保持活動兩秒，刪除會結束工作階段的程序本身。按 `Esc` 以在不刪除的情況下關閉確認。 除了 [刪除工作階段會移除什麼](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes) 中涵蓋的保留情況外，刪除會從清單中移除工作階段，Claude 為其建立的 worktree 會被移除、保留或保留在原位，取決於您如何刪除以及 worktree 保留的內容。對話文字記錄始終保留在您的本機上，可透過 `claude --resume` 取得。 若要在 Claude Code v2.1.212 或更新版本上恢復工作階段，請在分派輸入中輸入 `/resume`。選擇器開啟，顯示您開啟代理檢視的儲存庫的過去工作階段，最新的優先，包括您從清單中刪除的工作階段；已有列的工作階段不會列出。`↑`/`↓` 移動選擇，`Enter` 將選定的工作階段繼續為背景工作階段，使其作為列重新加入清單，`Esc` 關閉選擇器。 選擇器只在裸 `/resume` 時開啟。有目標、範圍或受限的繼續無法由選擇器提供，因此當以下情況時代理檢視顯示 `attach to a session to run it` 提示：

- `/resume` 命名 id 或搜尋詞
- 檢視以 `--cwd` 為範圍
- 檢視以 [`--safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 啟動
- 檢視以 `--permission-mode` 或 `--settings` 等旗標開啟

不適合螢幕的已完成工作階段會摺疊成 `… N more` 列。失敗和有開啟拉取請求的工作階段始終保持可見。`Completed` 群組填滿即時群組後剩下的垂直空間，在短終端機上標題會壓縮為單一摘要行，以便工作中或需要輸入的工作階段保持可見。

### 篩選工作階段

在分派輸入中輸入以篩選而不是分派：

| 篩選                             | 顯示                                                                              |
| -------------------------------- | --------------------------------------------------------------------------------- |
| `a:<name>`                       | 執行命名代理的工作階段                                                            |
| `s:<state>`                      | 給定狀態中的工作階段，例如 `s:working`。也接受 `s:blocked` 以獲得等待您的所有內容 |
| `#<number>` 或拉取或合併請求 URL | 在該拉取請求或合併請求上工作的工作階段                                            |
| 任何其他 URL                     | 其第一個提示包含該 URL 的工作階段                                                 |

### 鍵盤快捷鍵

在代理檢視中按 `?` 以查看上下文中的每個快捷鍵。下表總結了它們。

| 快捷鍵                                                                                                                                                                                                                                                                                                                                                                                               | 動作                                                                                                                                                                                                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `↑` / `↓`                                                                                                                                                                                                                                                                                                                                                                                            | 在列之間移動                                                                                                                                                                                                                                                                                     |
| `Enter`                                                                                                                                                                                                                                                                                                                                                                                              | 附加到選定的工作階段，或如果輸入中有文字則分派                                                                                                                                                                                                                                                   |
| `Space`                                                                                                                                                                                                                                                                                                                                                                                              | 開啟或關閉選定工作階段的查看面板                                                                                                                                                                                                                                                                 |
| `Shift+Enter`                                                                                                                                                                                                                                                                                                                                                                                        | 在分派輸入中插入新行，[如主提示中所示](https://code.claude.com/docs/zh-TW/terminal-config#enter-multiline-prompts)                                                                                                                                                                               |
| `Ctrl+Enter`                                                                                                                                                                                                                                                                                                                                                                                         | 分派並立即附加，在終端機中 `?` 覆蓋層列出 `ctrl+enter to start and open`                                                                                                                                                                                                                         |
| `→`                                                                                                                                                                                                                                                                                                                                                                                                  | 附加到選定的工作階段                                                                                                                                                                                                                                                                             |
| `Alt+1`..`Alt+9`                                                                                                                                                                                                                                                                                                                                                                                     | 附加到聚焦工作階段目錄中的工作階段 1–9                                                                                                                                                                                                                                                           |
| `Tab`                                                                                                                                                                                                                                                                                                                                                                                                | 在空輸入上，瀏覽所有子代理。否則應用突出顯示的建議                                                                                                                                                                                                                                               |
| `Ctrl+S`                                                                                                                                                                                                                                                                                                                                                                                             | 在狀態和目錄之間切換分組                                                                                                                                                                                                                                                                         |
| `Ctrl+T`                                                                                                                                                                                                                                                                                                                                                                                             | 釘選或取消釘選選定的工作階段                                                                                                                                                                                                                                                                     |
| `Ctrl+R`                                                                                                                                                                                                                                                                                                                                                                                             | 重新命名選定的工作階段                                                                                                                                                                                                                                                                           |
| `Ctrl+G`                                                                                                                                                                                                                                                                                                                                                                                             | 在您的 `$VISUAL` 或 `$EDITOR` 中開啟分派提示                                                                                                                                                                                                                                                     |
| `Ctrl+J`                                                                                                                                                                                                                                                                                                                                                                                             | 在分派輸入中插入新行                                                                                                                                                                                                                                                                             |
| `Ctrl+X`                                                                                                                                                                                                                                                                                                                                                                                             | 停止工作階段；在兩秒內再次按下以刪除它                                                                                                                                                                                                                                                           |
| `Shift+↑` / `Shift+↓`                                                                                                                                                                                                                                                                                                                                                                                | 重新排序選定的工作階段                                                                                                                                                                                                                                                                           |
| `Esc`                                                                                                                                                                                                                                                                                                                                                                                                | 關閉查看面板、清除輸入或退出。當您透過使用 `←` 背景執行工作階段開啟代理檢視時，最終 `Esc` 會返回到該對話而不是退出。啟用 [vim 編輯器模式](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode) 後，在輸入中按 `Esc` 會從 INSERT 切換到 NORMAL 模式並保留您的文字，如主提示中所示 |
| `Ctrl+C`                                                                                                                                                                                                                                                                                                                                                                                             | 清除輸入；按兩次以退出                                                                                                                                                                                                                                                                           |
| `?`                                                                                                                                                                                                                                                                                                                                                                                                  | 顯示所有快捷鍵                                                                                                                                                                                                                                                                                   |
| `Ctrl+S`、`Ctrl+T` 和 `Ctrl+G` 遵循您的 [`keybindings.json`](https://code.claude.com/docs/zh-TW/keybindings)。在 [`Agents` 上下文](https://code.claude.com/docs/zh-TW/keybindings#agents-actions) 中使用 `agents:switchView` 和 `agents:togglePin` 動作重新繫結或取消繫結 `Ctrl+S` 和 `Ctrl+T`，以及透過 `Chat` 上下文的 `chat:externalEditor` 繫結重新繫結 `Ctrl+G`。表中的其他快捷鍵無法重新繫結。 |                                                                                                                                                                                                                                                                                                  |

## 分派新代理

您可以從 agent view 分派新的背景工作階段、將現有互動工作階段發送到背景，或直接從 shell 啟動一個。

### 從 agent view

在 agent view 底部的輸入框中輸入提示，然後按 `Enter` 啟動新的背景工作階段。工作階段從提示自動命名；稍後可以使用 `Ctrl+R` 重命名它。 自動名稱是由 [Haiku-class model](https://code.claude.com/docs/zh-TW/model-config) 撰寫的簡短標籤。工作階段稍後獲得的名稱也會出現在其行上，包括當您在該工作階段中[接受計畫](https://code.claude.com/docs/zh-TW/permission-modes#review-and-approve-a-plan)時工作階段獲得的[生成標題](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions)。 將圖像粘貼到提示中以包含螢幕截圖或圖表與任務。 粘貼的文字超過 800 個字符或超過三行會摺疊為 `[Pasted text #N]` 佔位符，以便輸入保持在一行；完整文字會在您分派時發送。要在分派前檢查或編輯摺疊的文字，請再次粘貼相同的文字，佔位符會展開回輸入框。 前綴或提及提示的部分以控制工作階段如何啟動：

| 輸入                                             | 效果                                                                                                                                                       |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<agent-name> <prompt>`                          | 如果第一個單詞與自訂 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 名稱匹配，該 subagent 以工作階段的主代理身份執行，其 frontmatter 中的配置   |
| `@<agent-name>`                                  | 在提示中的任何地方提及自訂 subagent 以將其作為主代理執行                                                                                                   |
| `@<repo>`                                        | 提及儲存庫以在那裡執行工作階段。請參閱[分派到特定目錄](https://code.claude.com/docs/zh-TW/agent-view#dispatch-to-a-specific-directory)以了解列出哪些儲存庫 |
| `/<command>`                                     | 建議 [skills](https://code.claude.com/docs/zh-TW/skills) 和 [commands](https://code.claude.com/docs/zh-TW/commands) 作為提示分派                           |
| `! <command>`                                    | 執行 shell 命令作為背景工作而不是啟動 Claude 工作階段。該工作顯示為一行，您可以附加到、監視和分離                                                          |
| `#<number>` 或拉取或合併請求 URL                 | 如果工作階段已在該拉取或合併請求上工作，Claude Code 選擇其行而不是分派新工作階段                                                                           |
| 一小組命令在 agent view 本身中執行，而不是分派： |                                                                                                                                                            |

- `/exit` 和 `/quit` 關閉 agent view
- `/logout` 將您登出
- `/model` 設定[分派模型](https://code.claude.com/docs/zh-TW/agent-view#set-the-model)
- `/login` 開啟登入對話框，讓您無需附加到工作階段即可再次登入
- 裸 `/resume` 或其 `/continue` 別名開啟儲存庫過去工作階段的選擇器，以[將其帶回](https://code.claude.com/docs/zh-TW/agent-view#organize-the-list)作為背景工作階段。需要 Claude Code v2.1.212 或更新版本

Skills、您自己的命令和提示擴展內建命令（例如 `/init`）會作為新背景工作階段的第一個提示發送。其他內建命令會顯示 `attach to a session to run it` 提示。您輸入的所有內容都會保留在提示旁邊的輸入框中，以便您可以編輯它。 將重複任務打包為 [skill](https://code.claude.com/docs/zh-TW/skills)可讓您從 agent view 多次啟動相同的工作流程，無需重新輸入提示。 當相同的 `@name` 同時與 subagent 和同級儲存庫匹配時，subagent 優先。不帶 `@` 的第一個單詞形式也適用，因此以與您的 subagent 名稱之一匹配的單詞開頭的提示會分派該 subagent 而不是將該單詞視為純文本。當您想要明確時，請使用 `@` 形式，或以不同的單詞開頭提示以避免匹配。

#### 分派到特定目錄

新工作階段在您開啟 agent view 的目錄中執行。要針對不同的目錄，請使用以下任何方法：

- 在該目錄中開啟 `claude agents`。
- 在父目錄中開啟 `claude agents`，並在提示中使用 `@<repo>` 提及子儲存庫。輸入 `@` 會列出這些目標：
  - 啟動目錄下一級的 Git 儲存庫
  - 您啟動的儲存庫的已註冊 [git worktrees](https://code.claude.com/docs/zh-TW/worktrees)，位於其目錄樹內，例如 Claude 在 `.claude/worktrees/` 下建立的那些，標記有其簽出的分支。使用 `git worktree add ../feature` 等方式在儲存庫外新增的 Worktrees 不會被列出
  - 任何已在列表中有工作階段的目錄 名稱包含空格的目錄不會被列出。
- 從 shell，`cd` 進入目錄並執行 `claude --bg "<prompt>"`。

當 agent view 按目錄分組時，分派會將提示發送到選定行的目錄，因此您可以選擇一個組並在其中分派，無需重新輸入路徑。

### 從工作階段內部

兩個命令將工作從您所在的工作階段移動到背景：`/background` 將當前對話發送到那裡並釋放您的終端，而 `/fork` 在您繼續工作的地方發送一份副本。

#### 將工作階段發送到背景

執行 `/background` 或其別名 `/bg` 將當前對話移動到背景工作階段。傳遞提示，例如 `/bg run the test suite and fix any failures`，以在分派前發送一個額外的指令。如果 Claude 在您執行 `/bg` 時正在回應，回應會在背景工作階段中繼續。 退出仍有背景工作執行的互動工作階段（例如 subagents、背景 shell 命令、工作流程或 [monitors](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool)）會顯示 `Background work is running` 對話而不是立即退出。選擇 `Move to background and exit` 以與 `/background` 相同的方式將工作階段移動到背景並返回您的 shell。當 agent view [關閉](https://code.claude.com/docs/zh-TW/agent-view#turn-off-agent-view)時，不會顯示此選項。 如果背景工作階段列表上已有相同名稱的對話，Claude Code 會為新行的名稱編號，例如 `my-session (2)`，並保持現有行的名稱不變。要重命名新行，請在 agent view 中選擇它並按 `Ctrl+R`。

#### 使用 /fork 複製工作階段

執行 `/fork` 將當前對話複製到新的背景工作階段，同時原始工作階段繼續執行。副本從該點之前的對話中的所有內容開始；請參閱下面的項目符號以了解副本在何處執行。它還帶來了模型、權限模式、努力級別以及您在工作階段期間新增的任何目錄或「不再詢問」權限授予。副本在 agent view 中顯示為其自己的行。 在 fork 之後，兩個對話是獨立的：副本所做的任何事情都不會自動進入原始對話，儘管在啟用[跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)的工作階段中，任一工作階段的 Claude 都可以明確地向另一個發送訊息。 複製工作階段需要 Claude Code v2.1.212 或更新版本；在 v2.1.161 到 v2.1.211 上，`/fork` 啟動[分叉 subagent](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)，現在是 `/subtask`。當[agent view 關閉](https://code.claude.com/docs/zh-TW/agent-view#turn-off-agent-view)時，`/fork` 保持分叉 subagent 行為，`/subtask` 不可用。 傳遞提示，例如 `/fork open a draft pull request with the work so far`，副本立即開始處理它。沒有提示的情況下，副本等待其第一個指令：在 `claude agents` 中選擇其行並按 `Space` 發送一個，或執行 `claude attach <id>`。選定的行在等待時顯示 `space to send it a prompt`。 `/fork` 確認是一行，顯示副本的狀態，例如 `session running`、其 agent-view 行的名稱和其工作階段 ID 用於 `claude attach`。點擊名稱以切換到副本：此工作階段移動到背景，與按 `←` 相同，agent view 開啟副本的工作階段。 除非副本[就地編輯](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)，Claude Code 指示它在進行程式碼更改前建立自己的 worktree。在 git 儲存庫外，只有從 hook 建立的 worktree 移出的副本才會獲得指令；沒有 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/hooks#worktreecreate)，副本就地編輯。從您的 worktree 移出的副本也被告知永遠不要編輯、執行命令或進入該 worktree，無論隔離設定如何。 副本開始的位置取決於當前工作階段執行的位置：

- 像任何分派的工作階段一樣，副本[在編輯檔案前移動到其自己的 worktree](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)。在這種情況下，確認不會提及副本執行的位置。
- 當您的工作階段在啟動後移動到其連結的 [worktree](https://code.claude.com/docs/zh-TW/worktrees) 時，副本開始回到工作階段移動前的位置，除非它[就地編輯](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)，在那裡建立自己的 worktree 進行程式碼更改。當您的 worktree 簽出在一個分支上時，該指令也告訴一個副本，其任務建立在您的工作基礎上，以您的分支為基礎建立其新分支，因為您的分支在您的 worktree 中保持簽出。確認以 `runs in the origin tree` 結尾。
- 當您在已連結 worktree 內啟動工作階段，該儲存庫有主工作樹時，副本開始於該主工作樹，具有相同的 worktree-of-its-own 規則但沒有分支指令。確認也以 `runs in the origin tree` 結尾。
- 在裸儲存庫佈局的 worktree 內啟動的工作階段沒有主工作樹可返回，因此副本保持原位，確認以 `edits this checkout` 結尾。當 worktree 隔離在不在連結 worktree 內的工作階段中[關閉](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)時，也會出現相同的註記，因為副本隨後編輯您打開的檔案。

使用副本不會繼承的啟動標誌啟動的工作階段，例如替換的系統提示或 `--tools` 允許清單，無法分叉；Claude Code 會說明這一點，而不是製作部分副本。從 agent view 分派的工作階段正常分叉：副本使用與其來自的工作階段相同的[代理定義](https://code.claude.com/docs/zh-TW/sub-agents)和附加指令啟動。

#### 背景化時帶來的內容

背景化啟動一個新進程，從保存的對話恢復，進行中的工作會轉移到它：執行中的背景 shell 命令、背景化的 subagents、動態工作流程、您使用 [`/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks) 建立的排定任務，以及 Claude 對[工件註解的自動回覆](https://code.claude.com/docs/zh-TW/artifacts#let-claude-reply-to-comments-on-its-own)都會轉移並在那裡繼續執行。Subagent 與它啟動的所有內容一起移動，因此只有當所有工作都能轉移時它才會轉移。要停止進行中的工作而不是轉移它，請設定 [`CLAUDE_DISABLE_ADOPT=1`](https://code.claude.com/docs/zh-TW/env-vars#variables) 環境變數；Claude Code 隨後會要求您在背景化前確認。 當[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)仍有 subagents 執行時，Claude Code 會在背景化前詢問 `Background this session?` 對話，說明有多少 subagents 會重新啟動。選擇 `Stay` 讓它們先完成。如果您確認，Claude Code 會在背景工作階段中重新執行該執行：仍在執行的 subagents 從頭開始，因此它們迄今為止使用的令牌會再次花費。請參閱[暫停後恢復](https://code.claude.com/docs/zh-TW/workflows#resume-after-a-pause)以了解哪些已完成的 subagents 返回其保存的結果，哪些再次執行。 Claude Code 停止無法轉移的工作，例如執行中的 [monitor](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool)，並停止擁有監視器的背景化 subagent 及其一起。當任何此類工作執行時，Claude Code 會顯示 `Background this session?` 對話，以便您可以在停止前確認。 進入背景後，工作階段可以啟動新的 subagents、monitors 和背景命令，這些命令在稍後分離和重新附加時保持執行。 來自原始啟動的配置標誌會傳遞到背景化工作階段，因此其 MCP servers、settings 和備用模型保持有效：

- `--mcp-config` 和 `--strict-mcp-config`
- `--settings`
- `--add-dir`
- `--plugin-dir`
- `--fallback-model`
- `--allow-dangerously-skip-permissions`

您在工作階段期間使用 [`/add-dir`](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration) 新增的目錄也會轉移。轉移 `--allow-dangerously-skip-permissions` 會在背景化工作階段中保持 `bypassPermissions` 可達，但它不會授予任何新的權限：該模式仍然需要[Permission mode, model, and effort](https://code.claude.com/docs/zh-TW/agent-view#permission-mode-model-and-effort)中所述的一次性互動接受。

### 從您的 shell

傳遞 `--bg` 或其長形式 `--background` 啟動直接進入背景的工作階段：

```
claude --bg "investigate the flaky SettingsChangeDetector test"

```

提示是位置引數，不是 `-p` 值。Claude Code 在建立任何工作階段前拒絕 `--bg` 與 `-p` 或 `--print` 的組合，因為 `--print` 永遠不會啟動 `claude agents` 附加到的互動工作階段。 要執行特定 [subagent](https://code.claude.com/docs/zh-TW/sub-agents)（例如 `code-reviewer`）作為工作階段的主代理，請將 `--bg` 與 `--agent` 結合：

```
claude --agent code-reviewer --bg "address review comments on PR 1234"

```

如果名稱不與任何 subagents 匹配，啟動失敗：Claude Code 列印 `no agent named` 警告，仍然報告工作階段為背景化，但工作階段立即以 `--agent '<name>' not found` 錯誤退出。 當背景化工作階段稍後恢復或重新啟動時，Claude Code 恢復代理及其工具限制；對於其系統提示，請參閱[已恢復對話中的系統提示標誌](https://code.claude.com/docs/zh-TW/cli-reference#system-prompt-flags-in-resumed-conversations)。它首先在工作階段自己的目錄中搜索代理，前提是您已[信任該工作區](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)，因此專案範圍的代理在從另一個目錄恢復工作階段時仍會載入。如果代理不再存在，工作階段會繼續使用預設工具，其文字記錄會以[警告命名代理](https://code.claude.com/docs/zh-TW/errors#session-agent-no-longer-available)開啟。 要在背景中繼續現有對話，請使用 `--resume` 傳遞其完整工作階段 ID：

```
claude --resume 1f0e2c9a-6d0b-4c11-9f39-2a77c1d4e8b5 --bg "pick up where you left off and finish the migration"

```

在 Claude Code v2.1.257 或更新版本上，Claude Code 要麼在相同 ID 下繼續該工作階段，要麼在新 ID 下啟動副本並列印 `note:` 行解釋為什麼它無法就地繼續。當工作階段就地繼續時，`claude agents` 為其顯示一行。 當您將 `--bg` 與 `--continue`、裸 `--resume` 或 `--resume` 與名稱或檔案路徑結合時，Claude Code 總是啟動這樣的副本。新增 `--fork-session` 以故意啟動副本，無需註記。 傳遞 `--name` 以在 agent view 中設定工作階段的顯示名稱，而不是自動生成的名稱：

```
claude --bg --name "flaky-test-fix" "investigate the flaky SettingsChangeDetector test"

```

背景化後，Claude 列印工作階段的短 ID 和管理它的命令。當主機背景工作階段的服務尚未執行時，`--bg` 可能會先列印 `Starting background service…`。當您傳遞 `--name` 時，名稱會出現在短 ID 之後：

```
backgrounded · 7c5dcf5d · flaky-test-fix
  claude agents             list sessions
  claude attach 7c5dcf5d    open in this terminal
  claude logs 7c5dcf5d      show recent output
  claude stop 7c5dcf5d      stop this session

```

#### 執行 shell 命令

要執行 shell 命令作為背景工作而不是 Claude 工作階段，請傳遞 `--exec`。以下示例將 `pytest -x` 作為背景工作執行：

```
claude --bg --exec 'pytest -x'

```

從 agent view，通過在分派輸入的第一個字符中輸入 `!` 分派相同類型的工作：`!` 顯示為前綴，其後的所有內容都是命令，`Enter` 啟動工作。 該命令作為 PTY 支持的工作執行，並在 agent view 中顯示為一行，其最近的輸出行作為其狀態。shell 工作執行命令代替 Claude，因此不調用任何模型，輸出不發送到任何工作階段。 要查看輸出，附加到該行，按 `Space` 以在不附加的情況下查看，或從您的 shell 執行 `claude logs <id>`。捕獲的輸出保留在記憶體中，不寫入磁碟。該行及其輸出在命令退出後約五分鐘自動清理，因此如果您需要結果，請在那之前讀取它。

### 檔案編輯如何隔離

每個背景工作階段，無論是從 agent view、`/bg` 或 `claude --bg` 啟動，都在您的工作目錄中啟動。編輯檔案前，Claude 將工作階段移動到 `.claude/worktrees/` 下的隔離 [git worktree](https://code.claude.com/docs/zh-TW/worktrees)，因此並行工作階段可以讀取相同的檢出，但每個都寫入自己的。一旦工作階段在其 worktree 中，Claude Code [為工作階段和它生成的任何 subagents 強制執行 worktree 隔離](https://code.claude.com/docs/zh-TW/worktrees#how-claude-code-enforces-isolation)。 Claude 在以下情況下跳過 worktree：

- 工作階段已在連結的 git worktree 內，無論 Claude 是在 `.claude/worktrees/` 下建立它，還是您使用 `git worktree add` 在其他地方建立它
- Claude 正在編輯的檔案在連結的 git worktree 內，例如工作階段或其 subagent 使用 `git worktree add` 建立的那個
- 工作目錄不是 git 儲存庫且沒有配置 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/hooks#worktreecreate)
- 寫入在工作目錄外

要為 git worktrees 不實用的儲存庫關閉 worktree 隔離，請將 [`worktree.bgIsolation`](https://code.claude.com/docs/zh-TW/settings-reference#worktree-bgisolation) 設定為 `"none"`。背景工作階段隨後直接編輯您的工作副本，無需先移動到 worktree。將設定新增到專案的 `.claude/settings.json`：

```
{
  "worktree": {
    "bgIsolation": "none"
  }
}

```

在 git 儲存庫外，工作階段直接寫入工作目錄，彼此之間不隔離，因此避免分派編輯相同檔案的並行工作階段。如果您使用不同的版本控制系統，請配置 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control)，Claude 會以與 git 相同的方式隔離編輯。 當 hook 在不是 git 儲存庫的目錄中失敗時，Claude 會跳過該目錄的隔離並就地編輯工作目錄。在 git 儲存庫內，Claude Code 會阻止寫入共享檢出，直到 Claude 將工作階段移動到 worktree。 要找到工作階段的 worktree 路徑，查看工作階段或附加並檢查其工作目錄。 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 背景工作階段生成的會繼承工作階段的工作目錄，因此其檔案編輯會進入工作階段的 worktree 而不是您的工作副本。要給 subagent 其自己的單獨 worktree，請在其 frontmatter 中設定 [`isolation: worktree`](https://code.claude.com/docs/zh-TW/sub-agents#supported-frontmatter-fields) 或在生成它時傳遞 `isolation: "worktree"`。 當背景工作階段在 Claude 進入的 worktree 中進行了程式碼更改時，Claude Code 指示 Claude 在完成前保留工作，因此如果您刪除工作階段及其 worktree，它會存活：

- **提交並推送** ：Claude 無需詢問即可提交，當儲存庫有遠端時推送分支。
- **草稿拉取請求** ：當任務要求時 Claude 開啟一個，[`#N` 標籤](https://code.claude.com/docs/zh-TW/agent-view#pull-request-status)出現在行上。
- **永遠不會** ：推送到 `main` 或 `master`、強制推送和合併。
- **您的 git 指令優先** ：如果任務、`CLAUDE.md` 或[記憶](https://code.claude.com/docs/zh-TW/memory)說您自己處理提交或推送，Claude 將 git 留給您。

編輯未自行隔離的檢出的工作階段在提交或切換分支前仍會詢問。這適用於隔離設定為 `"none"` 時、worktree 移動失敗時，或工作階段在已存在的 worktree 內啟動時。 無論任務如何，Claude 以報告結尾，說明它做了什麼以及工作在哪裡：路徑、分支、拉取請求或答案本身。

#### 刪除工作階段會移除什麼

使用 [agent view](https://code.claude.com/docs/zh-TW/agent-view#organize-the-list) 中的 `Ctrl+X` 兩次或使用 [`claude rm`](https://code.claude.com/docs/zh-TW/agent-view#manage-sessions-from-the-shell) 刪除工作階段。除了下面保留的情況外，工作階段會離開列表。其文字記錄通過 `claude --resume` 保留在您的機器上，移除在監督者重新啟動後存活。 Claude 為工作階段建立的 worktree 會發生什麼：

- Agent view 移除它，包括未提交的更改，因此請先提交您想保留的內容。
- `claude rm` 在它有未提交更改時保留它，以及工作階段行。
- 當另一個執行中的工作階段正在使用或已鎖定 worktree 時，agent view 和 `claude rm` 都不會移除它，再次刪除不會改變這一點。Claude Code 保留 worktree 和工作階段，並命名保留的目錄和原因；在 agent view 中，工作階段的行顯示 `not deleted`。關閉另一個工作階段，然後再次刪除。
- 當您刪除一個 worktree 有 Claude Code 無法確認保存在其他地方的提交的工作階段時，Claude Code 保留 worktree 和工作階段，訊息命名 worktree 的分支以及有多少提交未推送。訊息還提供了兩種前進方式：推送提交，或再次刪除以丟棄它們。 遠端上的提交不會阻止刪除。本地副本上的提交也不會，您的 `origin` 遠端的預設分支，只要該分支在您的主檢出中簽出，儲存庫目錄本身而不是 worktree。 在該拒絕後，您選擇：
  - 要保留提交，推送它們或將它們合併到該預設分支，然後再次刪除工作階段。
  - 要丟棄它們，再次刪除工作階段而不推送：在 agent view 中的其行上按 `Ctrl+X` 兩次，或執行拒絕列印的 `claude rm <id> --discard-unpushed` 命令。這會移除工作階段和 worktree 及其分支，丟棄未推送的提交和任何未提交的更改。 當您再次刪除時，Claude Code 只丟棄拒絕顯示的內容：如果 worktree 自那以後獲得了提交，Claude Code 會再次保留它並顯示更新的狀態。 當另一個已完成工作階段的記錄也命名 worktree 時，它在您再次刪除時保留；推送提交，然後再次刪除。
- git 不再識別的 worktree，例如在 `git worktree prune` 之後，不會阻止刪除。Claude Code 刪除工作階段並將目錄留在磁碟上。
- 當 git 或您的 [`WorktreeRemove` hook](https://code.claude.com/docs/zh-TW/hooks#worktreeremove) 無法移除 worktree 時，Claude Code 保留 worktree 和工作階段，訊息命名原因。對於 hook，訊息說它如何結束，例如 `exited 1`，並引用其 stderr 的開始。訊息還告訴您接下來要做以下哪一個：
  - 再次刪除工作階段以無論如何移除目錄，通過在 agent view 中的其行上按 `Ctrl+X` 兩次或執行 `claude rm` 拒絕列印的 `claude rm <id> --force-remove-worktree <worktree-id>` 命令。Claude Code 只在它可以確認目錄是儲存庫在 `.claude/worktrees/` 下的連結 worktrees 之一，沒有對追蹤檔案的未提交更改、其內沒有嵌套儲存庫且沒有其他工作階段的記錄命名它時才提供此選項。Worktree 的分支保留在儲存庫中。
  - 修復阻礙的內容，例如提交或儲存未提交的更改、關閉使用目錄的任何內容或修復 hook，然後再次刪除工作階段。
  - 自己移除目錄，然後再次刪除工作階段。

您自己建立並在其中啟動工作階段的 worktree 無論如何都會保留在原位。 一個 worktree 目錄不屬於任何 git 儲存庫的工作階段，因為儲存庫被刪除或 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/hooks#worktreecreate) 在其他地方建立了目錄，仍然可以被刪除。當檔案保留在目錄中時：

- Agent view 在丟棄它們前要求相同的 `Ctrl+X` 雙擊。對於 hook 建立的目錄，它執行您的 [`WorktreeRemove` hook](https://code.claude.com/docs/zh-TW/hooks#worktreeremove)，沒有一個它拒絕刪除並保留工作階段。
- `claude rm` 保留工作階段和 worktree，並命名原因。

任一路徑都保留另一個已完成工作階段的記錄命名的目錄。

### 設定模型

agent view 標題中顯示的模型名稱是分派預設值。您從輸入啟動的新工作階段使用此模型，這來自您使用者設定中的 [`model` setting](https://code.claude.com/docs/zh-TW/settings-reference#model)。通過在 [`/model` picker](https://code.claude.com/docs/zh-TW/model-config) 中選擇模型來設定它，或直接編輯設定。 要為整個 agent view 工作階段覆蓋分派預設值，請在開啟 agent view 時傳遞 `--model`。請參閱[Permission mode, model, and effort](https://code.claude.com/docs/zh-TW/agent-view#permission-mode-model-and-effort)。 要從 agent view 內部更改分派預設值，請在分派輸入中輸入 `/model` 後跟模型名稱，然後按 `Enter`。標題會更新以顯示該模型，帶有 `(session)` 標記，之後您分派的工作階段會使用它。輸入 `/model default` 以清除覆蓋並返回分派預設值。此覆蓋會持續到當前 `claude agents` 執行的其餘部分，不會寫入您的設定檔案。以下示例在 Opus 上分派一個工作階段，在 Sonnet 上分派下一個：

```
/model opus
refactor auth
/model sonnet
run the test suite

```

每個背景工作階段可以在不同的模型上執行。要為一個工作階段覆蓋它：

- 從 shell，使用 `claude --bg` 傳遞 `--model`。
- 附加到執行中的工作階段並執行 `/model` 以切換：從選擇器中選擇，或輸入 `/model <name>`，會保存為您的新工作階段預設值，除非您在選擇器中按 `s` 進行僅工作階段切換。如果工作階段被重新生成，僅工作階段切換會持續。
- 分派一個 [subagent](https://code.claude.com/docs/zh-TW/sub-agents)，其 frontmatter 設定 `model` 欄位。

### Permission mode, model, and effort

背景工作階段從它執行的位置和方式取得其設定、提供者、權限模式、模型和努力。下面的小節涵蓋每個來源，以及監督者重新啟動工作階段時持續的內容。

#### Settings and provider

背景工作階段從它執行的目錄讀取其 [settings](https://code.claude.com/docs/zh-TW/settings)，就像您在那裡啟動了 `claude` 一樣。這包括專案設定中的 [`env` values](https://code.claude.com/docs/zh-TW/settings-reference#env)，因此在那裡設定的 `ANTHROPIC_MODEL` 或提供者變數適用於該目錄中的每個背景工作階段。 背景工作階段也使用您分派它的 shell 的 `PATH` 執行，因此它執行的命令找到與您的終端相同的工具。它也保留該 shell 的雲提供者選擇，例如 `CLAUDE_CODE_USE_BEDROCK` 或 `CLAUDE_CODE_USE_VERTEX`，以及其 `ANTHROPIC_DEFAULT_*_MODEL` 別名和任何您在那裡匯出的 [`CLAUDE_CODE_EXTRA_BODY`](https://code.claude.com/docs/zh-TW/env-vars) 覆蓋。

#### LLM gateway

如果您通過 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway) 路由 Claude Code，請將閘道變數放在設定檔案的 `env` 區塊中，而不是在您的 shell 中匯出它們，背景工作階段會與其餘設定一起讀取它們。[在設定檔案中設定](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-in-a-settings-file)顯示區塊以及要使用哪個設定檔案來獲取認證。 如果您只在 shell 中匯出閘道 `ANTHROPIC_BASE_URL`，它只在以下情況下到達背景工作階段，以及您與它匯出的 `ANTHROPIC_CUSTOM_HEADERS` 和認證，只有當[監督者](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)本身從匯出相同閘道的 shell 啟動時，並且只在這些情況下：

- 您使用 `←` 或 `/background` 背景化您自己的工作階段
- 您分派工作階段到您所在的目錄
- 您通過附加或回覆它來喚醒您所在目錄中的停止工作階段

Claude Code 在雲提供者前轉發閘道。如果您分派的 shell 選擇提供者並使用其認證繞過標誌匯出其閘道端點，Claude Code 會在適用於 `ANTHROPIC_BASE_URL` 的條件下轉發端點和標誌對，以及 `ANTHROPIC_CUSTOM_HEADERS`。例如，匯出 `CLAUDE_CODE_USE_VERTEX=1` 與 `ANTHROPIC_VERTEX_BASE_URL` 和 `CLAUDE_CODE_SKIP_VERTEX_AUTH=1`，Claude Code 會轉發該端點和標誌。 Claude Code 只將轉發的閘道應用於該工作階段的執行進程，永遠不會將其寫入磁碟。

#### Permission mode

[permission mode](https://code.claude.com/docs/zh-TW/permissions) 取決於您如何啟動工作階段：

- **使用`/bg` 或 `←` 背景化**：Claude Code 保留工作階段所在的權限模式，因此您切換到 `acceptEdits` 或 `auto` 的工作階段在分離後仍保持該模式
- **從您使用`←` 開啟的 agent view 分派**：目標自己的配置優先，當沒有其他設定時，您來自的工作階段的權限模式適用
- **從 shell 中啟動的`claude agents` 或使用 `claude --bg` 分派**：新工作階段以新 `claude` 工作階段在該目錄中啟動的方式開始，除非您從使用[分派預設值](https://code.claude.com/docs/zh-TW/agent-view#dispatch-defaults)開啟的 agent view 分派它。[工作階段在哪個權限模式中啟動](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)列出順序

對於您從使用 `←` 開啟的 agent view 分派的工作階段，Claude Code 從適用的第一個中取得權限模式：

1. 目標目錄的 [`permissions.defaultMode`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-defaultmode)。兩個來源規則適用：
   - `auto` 和 `bypassPermissions` [只從受管設定、`--settings` 檔案或 `~/.claude/settings.json` 生效](https://code.claude.com/docs/zh-TW/settings-reference#permissions-defaultmode)。
   - Claude Code 拒絕來自專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 的 `defaultMode`，選擇比您來自的工作階段所在的更寬鬆的模式。
1. 您來自的工作階段的權限模式

當 Claude Code 拒絕來源的模式過於寬鬆時，列表中的下一個來源決定。例如，如果您從計畫模式工作階段分派到其簽入設定要求 `acceptEdits` 的目錄，新工作階段以計畫模式啟動。如果您將該 `defaultMode` 移動到 `~/.claude/settings.json`，它無論您來自的工作階段的權限模式如何都適用。 寬鬆度執行計畫，然後手動和 `dontAsk`，然後 `acceptEdits` 和 auto，每個都計為比另一個更寬鬆，然後 `bypassPermissions`。

#### Dispatch defaults

要為您從 agent view 分派的每個工作階段設定預設值，請在開啟它時傳遞 `--permission-mode`、`--model`、`--effort` 或 `--agent` 中的任何一個：

```
claude agents --permission-mode plan --model opus --effort high

```

`--effort` 此處接受與[頂級 `--effort` 標誌](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)相同的值，包括 `ultracode`。 `--agent` 設定 [subagent](https://code.claude.com/docs/zh-TW/sub-agents)，當分派提示未使用 `@name` 或作為第一個單詞命名時使用。如果設定了 [`agent` setting](https://code.claude.com/docs/zh-TW/settings-reference#agent)，則預設為該設定，否則為內建的全能 `claude` 代理。在分派輸入中命名 subagent 會覆蓋兩者。 `claude agents` 也接受 `--dangerously-skip-permissions` 作為 `--permission-mode bypassPermissions` 的簡寫，以及 `--allow-dangerously-skip-permissions` 以在每個分派工作階段的 `Shift+Tab` 循環中提供 `bypassPermissions`，而不是以該模式啟動。兩者都與[頂級 CLI 標誌](https://code.claude.com/docs/zh-TW/cli-reference)相符。 傳遞 `--restricted` 以在[受限模式](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)中啟動您從檢視分派的每個工作階段，就像每個都使用頂級 `--restricted` 標誌啟動一樣。需要 Claude Code v2.1.248 或更新版本。 活動預設值出現在分派輸入下方的頁腳中。 Claude Code 拒絕 `claude --bg --permission-mode bypassPermissions`，直到您通過執行 `claude --dangerously-skip-permissions` 一次互動式接受了繞過免責聲明，因為該模式讓您未監視的工作階段無需批准即可行動。將 `--dangerously-skip-permissions` 或 `--permission-mode bypassPermissions` 傳遞給 `claude agents` 會在您之前未接受時顯示相同的免責聲明，接受會將 `bypassPermissions` 應用於您從檢視啟動的工作階段。傳遞 `--allow-dangerously-skip-permissions` 也會顯示相同的免責聲明，接受會在這些工作階段的 `Shift+Tab` 循環中提供 `bypassPermissions`，而不是以它啟動它們。

#### 重新啟動時持續的內容

您為背景工作階段選擇的權限模式、模型和努力，以及它攜帶的[配置標誌](https://code.claude.com/docs/zh-TW/agent-view#what-carries-over-when-you-background)，在監督者稍後[停止並重新啟動](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)其進程時都會持續。您使用 `claude --bg --dangerously-skip-permissions` 或 `claude --bg --permission-mode bypassPermissions` 啟動的工作階段在該重新啟動後保持 `bypassPermissions`。您使用 `/model` 或 `/effort` 在工作階段中途更改的模型或努力也會被保留。 如果工作階段從您的設定而不是從 `--effort` 或 `/effort` 取得其努力，Claude Code 會在每次為工作階段啟動進程時再次讀取您的設定。因此，當您編輯 `settings.json` 中保存的努力時，更改會到達您使用 `←` 或 `/bg` 背景化的工作階段及其稍後的重新啟動。保存的努力是 [`effortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#effortlevel) 鍵或 [`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings) 條目。 Claude Code 也保留您使用 [`/rename`](https://code.claude.com/docs/zh-TW/commands) 或 `Ctrl+R` 設定的名稱在該重新啟動時，因此您仍然可以執行 [`claude --resume <name>`](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions) 以到達工作階段。 您使用 [`Ctrl+S`](https://code.claude.com/docs/zh-TW/interactive-mode#general-controls) 在附加時儲存的提示也會與工作階段一起保留。在其進程被停止或重新啟動後重新開啟工作階段，`Ctrl+S` 恢復儲存的文字。儲存中的粘貼內容不會在重新啟動後存活。

### Settings, plugins, and MCP servers

Agent view 接受與 `claude` 相同的配置標誌，用於載入 settings、plugins、MCP servers 和額外目錄。Agent view 將 `--settings` 和 `--plugin-dir` 應用於自己，並將每個配置標誌傳遞給您從它分派的工作階段，因此以這種方式載入的 plugin 或 MCP server 在這些工作階段中也可用。

| 標誌                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 效果                                                                                                                                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`--settings <file-or-json>`](https://code.claude.com/docs/zh-TW/settings)                                                                                                                                                                                                                                                                                                                                                                                                                     | 覆蓋 agent view 和分派工作階段的 settings                                                                                                                                                                                        |
| [`--add-dir <path>`](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration)                                                                                                                                                                                                                                                                                                                                                                | 授予對額外目錄的檔案存取權限                                                                                                                                                                                                     |
| [`--plugin-dir <path>`](https://code.claude.com/docs/zh-TW/plugins)                                                                                                                                                                                                                                                                                                                                                                                                                            | 從本地目錄載入 plugin                                                                                                                                                                                                            |
| [`--mcp-config <file-or-json>`](https://code.claude.com/docs/zh-TW/mcp)                                                                                                                                                                                                                                                                                                                                                                                                                        | 從配置檔案或 JSON 字符串載入 MCP servers                                                                                                                                                                                         |
| `--strict-mcp-config`                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 僅使用來自 `--mcp-config` 的 MCP servers，忽略其他 MCP 配置。請參閱[使用 managed-mcp.json 的獨佔控制](https://code.claude.com/docs/zh-TW/managed-mcp#exclusive-control-with-managed-mcp-json)以了解該標誌在受管 MCP 檔案下做什麼 |
| 每個值重複 `--add-dir`、`--plugin-dir` 或 `--mcp-config` 一次。`claude agents` 不支援空格分隔的形式，例如 `--add-dir a b c`。 您可以將 `--settings` 和 `--plugin-dir` 放在 `agents` 之前或之後。將 `--add-dir` 和 `--mcp-config` 保留在 `agents` 之後：如果您將任一個放在 `agents` 之前，[`claude agents --json`](https://code.claude.com/docs/zh-TW/agent-view#manage-sessions-from-the-shell) 會失敗，出現 `unknown option` 錯誤。 以下示例使用 settings 覆蓋和一個額外目錄開啟 agent view： |                                                                                                                                                                                                                                  |

```
claude agents --settings ./ci-settings.json --add-dir ../shared-lib

```

`--settings` 接受檔案路徑或內聯 JSON 字符串。檔案路徑必須指向現有檔案；如果不存在，Claude Code 會以 `Settings file not found` 錯誤退出。

## 從 shell 管理工作階段

每個背景工作階段都有一個短 ID，您可以從 shell 使用。當您使用 `claude --bg` 啟動工作階段時會列印該 ID，每個工作階段的 ID 是其在 `~/.claude/jobs/` 下的目錄名稱。這些命令對於指令碼編寫或當您不想開啟 agent view 時很有用。

| 命令                                                       | 目的                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `claude agents`                                            | 開啟 agent view                                                                                                                                                                                                                                                                                |
| `claude agents --cwd <path>`                               | 開啟 agent view，範圍限定於在 `<path>` 下啟動的工作階段                                                                                                                                                                                                                                        |
| `claude agents --json`                                     | 將工作階段列印為 JSON 陣列並結束。請參閱 [將工作階段列為 JSON](https://code.claude.com/docs/zh-TW/agent-view#list-sessions-as-json)                                                                                                                                                            |
| `claude attach <id>`                                       | 在此終端中附加到工作階段                                                                                                                                                                                                                                                                       |
| `claude logs <id>`                                         | 列印工作階段的最近輸出                                                                                                                                                                                                                                                                         |
| `claude stop <id>`                                         | 停止工作階段。也接受 `claude kill`                                                                                                                                                                                                                                                             |
| `claude respawn <id>`                                      | 重新啟動工作階段（執行中或已停止），例如用於採用更新的 Claude Code 二進位檔案。重新啟動的工作階段會繼續其已儲存的對話；當磁碟上沒有對話時，它會再次執行其原始提示作為新對話                                                                                                                    |
| `claude respawn --all`                                     | 重新啟動每個執行中的工作階段，例如一次將所有工作階段移至更新的 Claude Code 二進位檔案                                                                                                                                                                                                          |
| `claude rm <id>`                                           | 從清單中移除工作階段，以及 Claude 為其建立的 worktree（當安全刪除時）；請參閱 [刪除工作階段會移除什麼](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)。對話記錄會保留在您的本機上，並可透過 `claude --resume` 繼續使用                                         |
| `claude rm <id> --discard-unpushed <commit>@<worktree-id>` | 刪除因未推送提交而拒絕刪除的工作階段，捨棄 worktree 及其分支和提交。傳遞拒絕列印的確切值；請參閱 [刪除工作階段會移除什麼](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)。需要 v2.1.260 或更新版本                                                             |
| `claude rm <id> --force-remove-worktree <worktree-id>`     | 刪除因 git 或 `WorktreeRemove` hook 無法移除其 worktree 而拒絕刪除的工作階段，無論如何刪除 worktree 目錄並在儲存庫中保留其分支。傳遞拒絕列印的確切值；請參閱 [刪除工作階段會移除什麼](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)。需要 v2.1.268 或更新版本 |
| `claude daemon status`                                     | 列印 [supervisor](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process) 的狀態、版本、socket 目錄和 worker 計數                                                                                                                                                                |
| `claude daemon stop --any`                                 | 停止 supervisor 程序及其託管的背景工作階段。傳遞 `--keep-workers` 以保持背景工作階段執行中，以便下一個 supervisor 可以重新連接到它們。下一個 `claude agents` 或 `claude --bg` 會啟動全新的 supervisor                                                                                          |

### 將工作階段列為 JSON

`claude agents --json` 將作用中的工作階段列印為 JSON 陣列並結束：每個即時工作階段，加上仍在執行或被阻止的背景工作階段，即使其程序已結束。新增 `--all` 以同時包含已完成的背景工作階段，並新增 `--cwd <path>` 以將清單限制為在該目錄下啟動的工作階段。 每個項目都描述一個工作階段：

| 欄位                       | 出現時機                    | 說明                                                                                                                                                                                                                                                             |
| -------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cwd`、`kind`、`startedAt` | 一律                        | 工作目錄、`interactive` 或 `background`，以及 Unix 毫秒為單位的開始時間                                                                                                                                                                                          |
| `id`                       | 背景工作階段                | 短 ID，可與 `claude attach`、`claude logs` 和 `claude stop` 搭配使用                                                                                                                                                                                             |
| `state`                    | 背景工作階段                | `working`、`blocked`、`done`、`failed` 或 `stopped` 之一。請參閱 [從指令碼讀取工作階段狀態](https://code.claude.com/docs/zh-TW/agent-view#read-session-state-from-a-script)，了解每個值的含義                                                                    |
| `pid`、`status`            | 程序執行時                  | 程序 ID 和 `busy`、`waiting` 或 `idle` 之一                                                                                                                                                                                                                      |
| `waitingFor`               | 當 `status` 為 `waiting` 時 | 工作階段被阻止的原因：`permission prompt` 表示需要核准、`input needed` 表示 Claude 或 MCP 伺服器的輸入請求、`sandbox request`、`worker request` 或 `dialog open`                                                                                                 |
| `sessionId`、`name`        | 設定時                      | `sessionId` 是完整的工作階段 UUID，可與 [`claude --resume`](https://code.claude.com/docs/zh-TW/sessions) 搭配使用。互動工作階段的 `name` 是其 [預設顯示名稱](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions)，直到您命名工作階段或在其中接受計畫 |

### 從指令碼讀取工作階段狀態

`claude agents --json` 是從 Claude Code 外部讀取工作階段狀態的支援方式，例如從狀態列、排程器或監督背景工作的另一個 Claude 工作階段。輪詢 `claude agents --json --all`，它會持續列出程序已結束的工作階段，並讀取每個項目的 `state`、`status` 和 `waitingFor`。

| `state`                                                                                                                                                                                                                                                                                                                                                                                   | 含義                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `working`                                                                                                                                                                                                                                                                                                                                                                                 | 正在執行一個回合，或工作階段在其自行驅動的工作步驟之間，例如 [`/loop`](https://code.claude.com/docs/zh-TW/scheduled-tasks) 反覆運算或等待 CI。`status` 會告訴您其程序現在是否為 `busy`              |
| `blocked`                                                                                                                                                                                                                                                                                                                                                                                 | 工作階段正在等待您：它提出的問題、權限或沙箱決定、只有您才能清除的錯誤（例如過期的登入），或如果您在沒有提示的情況下啟動它，則為其第一個提示。當等待是即時程序中的開啟提示時，`waitingFor` 會命名它 |
| `done`                                                                                                                                                                                                                                                                                                                                                                                    | 最後一個回合完成了您要求的內容，工作階段已準備好接收您的下一個提示，無論其程序是否仍在執行                                                                                                          |
| `failed`、`stopped`                                                                                                                                                                                                                                                                                                                                                                       | 工作已因錯誤而結束，或工作階段已停止                                                                                                                                                                |
| 完成其回合並等待您下一個指令的工作階段讀取 `done`，而不是 `blocked`。`blocked` 一律表示工作階段在繼續之前需要您提供的內容。 `~/.claude/jobs/<id>/` 下的檔案不是穩定的介面。工作階段或其他程式寫入 `state`、`detail`、`tempo` 或 `needs` 的值會在下次更新時被取代。 如果您想讓工作階段用自己的話報告進度，請讓它寫入自己的檔案，例如在 `$CLAUDE_JOB_DIR/tmp` 下，而不是編輯 `state.json`。 |                                                                                                                                                                                                     |

## 背景工作階段如何被託管

Claude Code 將 agent view 中列出的每個工作階段視為背景工作階段，無論您目前是否連接到它。相比之下，直接執行 `claude` 啟動的工作階段與該終端相關聯，並在終端關閉時結束，除非您[將其發送到背景](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)。 要檢查您在哪種工作階段中，請執行 [`/status`](https://code.claude.com/docs/zh-TW/commands)。`Session kind` 列在背景工作階段中顯示 `background job · attached` 或 `background job · unattended`（取決於是否連接了終端），在任何其他工作階段中顯示 `interactive`。

### 監督程序

監督程序是一個背景服務，執行您的背景工作階段，使其在您關閉 agent view 或終端後繼續工作。Claude Code 在您第一次背景化工作階段或開啟 agent view 時啟動它，您不需要自己管理它。 每個工作階段都是監督程序下的自己的 Claude Code 程序，該程序發生的情況取決於工作階段的狀態：

- **工作中、暫停在權限提示或其他對話框上，或已連接** ：程序保持執行。執行中的子代理、工作流程或監視器計為工作中。
- **已完成或等待您的下一條訊息，且未連接約一小時** ：監督程序停止程序以釋放資源。通過提出問題結束其輪次的工作階段計為等待您的下一條訊息。對話保存在磁碟上，下次您連接或回覆時，工作階段從中斷的地方恢復。使用 `Ctrl+T` 釘選工作階段以保持其程序執行。
- **在監督程序執行時意外退出** ：監督程序重新啟動程序。使用 `←` 或 `/background` 結束您背景化的工作階段（例如使用 `kill`）會將其標記為已停止而不是重新啟動。對於以關閉結束的工作階段，請參閱[工作階段在關閉後顯示為失敗或已停止](https://code.claude.com/docs/zh-TW/agent-view#sessions-show-as-failed-after-shutdown)。
- **自動更新後** ：監督程序重新啟動自身到新版本，並在背景中移動閒置工作階段。正在工作、等待您或已連接的工作階段不會被中斷。

當工作階段的程序停止或重新啟動時，Claude 在其中啟動的背景 shell 命令、動態工作流程和背景子代理會轉移到其下一個程序；執行中的監視器和子代理啟動的 shell 命令會隨程序停止。刪除工作階段會停止它轉移的所有內容。要讓所有內容隨程序停止而不是轉移，請將 [`CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF`](https://code.claude.com/docs/zh-TW/env-vars#variables) 設定為 `1`。 監督程序及其工作階段使用與您的互動工作階段相同的儲存認證進行身份驗證。對於哪些設定和 shell 變數到達工作階段（包括 `PATH`），請參閱[設定和提供者](https://code.claude.com/docs/zh-TW/agent-view#settings-and-provider)。對於閘道端點，請參閱 [LLM 閘道](https://code.claude.com/docs/zh-TW/agent-view#llm-gateway)。

### 狀態存儲位置

工作階段狀態存儲在您的 Claude Code 設定目錄下。如果您設定 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars)，監督程序改用該目錄而不是 `~/.claude`，並作為具有其自己工作階段的單獨實例執行。

| 路徑                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 內容                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `~/.claude/daemon.log`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 監督程序日誌                                                                                                                                                                 |
| `~/.claude/daemon/roster.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 執行中的背景工作階段列表，用於在重新啟動後重新連接                                                                                                                           |
| `~/.claude/jobs/<id>/state.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 在 agent view 中顯示的每個工作階段狀態。通過 [`claude agents --json`](https://code.claude.com/docs/zh-TW/agent-view#read-session-state-from-a-script) 讀取它，而不是解析檔案 |
| `~/.claude/jobs/<id>/tmp/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 每個工作階段的暫存目錄。Claude 的 `Write` 和 `Edit` 呼叫在此處不會提示權限。工作階段刪除時移除                                                                               |
| 每個背景工作階段都設定了 `CLAUDE_JOB_DIR` 環境變數，指向其 `~/.claude/jobs/<id>` 目錄，因此工作階段執行的 shell 命令可以將臨時檔案寫入 `$CLAUDE_JOB_DIR/tmp`，而不會與平行工作階段衝突。 要在不直接讀取檔案的情況下檢查此狀態，請執行 `claude daemon status`。它報告監督程序是否可達、其程序 ID 和版本、socket 目錄，以及有多少背景工作階段處於活動狀態。 該命令也會在執行中的監督程序版本與您叫用的 `claude` 版本不同時發出警告，這會在監督程序尚未重新啟動到新版本的更新後發生。警告會顯示兩個版本，並告訴您執行 `claude daemon stop --any` 以採用新版本。當 Claude Code 安裝為作業系統服務時，建議的命令是 `claude daemon stop`，不帶該旗標。 工作階段在該版本不匹配時保持完整：較舊的 Claude Code 版本更新工作階段的 `state.json` 時會保留它不識別的欄位，並保持工作階段列出。`roster.json` 中的工作階段列表遵循相同規則，因此由較新版本啟動的工作階段保持可達，並在監督程序重新啟動後繼續接受輸入。 |                                                                                                                                                                              |

### 關閉 agent view

要完全關閉背景代理和 agent view，將 `disableAgentView` [設定](https://code.claude.com/docs/zh-TW/settings)設為 `true` 或設定 `CLAUDE_CODE_DISABLE_AGENT_VIEW` 環境變數。管理員可以通過[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)強制執行此操作。

## 故障排除

### `claude agents` 列出子代理而不是開啟代理檢視

如果 `claude agents` 列印計數後跟著您設定的子代理，然後退出，代理檢視在您的環境中不可用。執行 `claude update` 以安裝最新版本。 如果更新後代理檢視仍未開啟，請檢查它是否已被設定或環境變數[關閉](https://code.claude.com/docs/zh-TW/agent-view#turn-off-agent-view)。

### Agent view 開啟時沒有工作階段

在您分派第一個工作階段之前，agent view 會顯示空的區段標題，每個標題下方有描述，以及輸入上方有一行說明，代替工作階段清單。在底部的輸入框中輸入提示並按 `Enter` 以分派您的第一個工作階段。

### 背景化顯示 `Background this session?` 對話

如果按 `←` 將當前工作階段放在背景中，Claude Code 顯示 `Background this session?` 對話，工作階段有進行中的工作無法轉移到背景工作階段、可能會停止、重新啟動或無人看管地執行，Claude Code 在執行任何操作之前會詢問：

- **無法移動的工作** ：工作階段有無法移動到背景工作階段的工作，例如執行中的 [monitor](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool)。對話命名 Claude Code 會停止的工作，並分別計算轉移的任務。
- **具有執行中子代理的工作流程** ：[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)仍有子代理執行。工作流程本身會轉移，但其執行中的子代理會從頭開始重新啟動，對話會說明有多少個。
- **自動成品回覆** ：Claude 正在[自行回覆成品上的評論](https://code.claude.com/docs/zh-TW/artifacts#let-claude-reply-to-comments-on-its-own)。這些回覆會在背景工作階段中繼續，對話會說明。

執行 `/tasks` 以查看正在執行的所有內容，然後確認以無論如何背景化或選擇 `Stay` 讓工作先完成。請參閱[背景化時轉移的內容](https://code.claude.com/docs/zh-TW/agent-view#what-carries-over-when-you-background)以了解哪些工作類型轉移，哪些 Claude Code 停止。

### 提示被拒絕為過短

分派輸入期望任務描述，而不是對話開場白。短於四個字元的提示會被拒絕並顯示 `Too short` 提示，以便隨意按鍵不會啟動工作階段。描述您希望工作階段執行的操作，例如 `investigate the flaky checkout test`。

### 工作階段在關閉後顯示為失敗或停止

關閉或重新啟動您的機器會停止執行中的背景工作階段。等待您輸入的工作階段在您回來時會保留在 `Needs input` 下。對於任何其他執行中的工作階段，agent view 顯示的內容取決於它上次取得進度的時間有多久：

- 在 48 小時內，工作階段顯示為失敗。附加或回覆它，它會從中斷的地方重新啟動。
- 超過 48 小時，例如機器關閉數天後，工作階段顯示為停止，並顯示 `ended while the background service was off`。在該列上按 `Enter`，頁腳會顯示 `Press enter again to resume this session (it ended while the background service was off), or ctrl+x to delete it.` 在同一列上再次按 `Enter` 以恢復其已儲存的對話。回覆或 `claude attach <id>` 會在沒有該頁腳提示的情況下恢復它。

當[文字記錄清理](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)已移除停止工作階段的已儲存對話時，Claude Code 拒絕開啟該列：訊息說沒有要恢復的內容。`claude rm <id>` 刪除該列，除了[保留的情況](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)中描述的情況外，`claude respawn <id>` 會再次執行其原始提示。請參閱[此工作階段的已儲存對話不再在磁碟上](https://code.claude.com/docs/zh-TW/errors#this-sessions-saved-conversation-is-no-longer-on-disk)。 睡眠單獨不會停止工作階段。工作階段在睡眠期間會被保留，監督程序在喚醒時會重新連接到它們。

### 開啟工作階段時顯示對話已開啟

兩個程序無法寫入同一個文字記錄。當停止工作階段的已儲存對話已在另一個執行中的 Claude Code 程序中開啟時，Claude Code 拒絕啟動工作階段的自己的程序。您看到的內容取決於什麼持有對話：

- 您恢復對話的終端，例如使用 `claude --resume` 或 `/resume`：該列顯示 `Open in a terminal`，並提示在那裡繼續，開啟該列會顯示 `Can't open — this session is running in another terminal`。在該終端中繼續，或退出它並再次開啟該列。
- 另一個非互動式 Claude Code 程序，例如同一對話的背景工作階段程序尚未退出：開啟該列會顯示 `This conversation is already open in another running Claude session`。使用該程序，或等待它退出並再次開啟該列。

Claude Code 會儲存您在拒絕嘗試時輸入的回覆，並在工作階段下次啟動時發送它。

### 開啟工作階段時顯示它沒有已儲存的文字記錄

停止工作階段[從另一個對話背景化](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)並在其第一個回覆完成之前停止，沒有要恢復的內容：在該第一個回覆完成之前，對話仍然只存在於它背景化的工作階段中。`claude attach` 拒絕開啟它，顯示 `This session has no saved transcript`。 在 agent view 中，開啟該列會在清單下方顯示 `Press enter again to restart this session fresh`。在同一列上再次按 `Enter` 以使用空對話重新啟動工作階段，或從 shell 執行 `claude respawn <id>`。 原始對話完整無缺；使用 `claude --resume` 恢復它或繼續在其中工作。請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors#this-session-has-no-saved-transcript)以取得詳細資訊。

### 終端主機已死亡或工作階段停止回應

[監督程序](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)在其自己的主機程序中執行每個背景工作階段的終端。當該程序死亡或停止回應時，Claude Code 會顯示原因並提供重新啟動；在兩種情況下，對話都會被儲存，重新啟動會恢復它。[錯誤參考](https://code.claude.com/docs/zh-TW/errors#terminal-host-process-died)引用完整訊息。 Claude Code 永遠不會重新啟動執行[shell 命令](https://code.claude.com/docs/zh-TW/agent-view#run-a-shell-command)的列，來自 `Enter` 或來自 `claude attach`，因為那樣會再次執行命令；該列的訊息和 `claude attach` 都說命令不會再次執行。

#### 終端主機已死亡

在 Linux 和 WSL 上，監督程序每隔幾秒檢查每個主機程序，無論您是否開啟工作階段，並在程序已退出但其與監督程序的連接從未關閉時將工作階段標記為失敗。

- 在 agent view 中，該列顯示 `terminal host process died — press Enter to restart`。在它上面按 `Enter`，Claude Code 會在新的主機程序上重新啟動工作階段。
- 從 shell，`claude attach <id>` 重新啟動已標記為失敗的工作階段。否則它會報告原因並退出，告訴您執行 `claude attach <id>`。

#### 工作階段沒有回應

當監督程序接受開啟但約十秒內沒有輸出到達時，Claude Code 會結束嘗試並提供重新啟動。僅僅停滯的工作階段，例如跨機器睡眠，不會達到此提供：監督程序[在開啟時自行重新啟動](https://code.claude.com/docs/zh-TW/agent-view#read-session-state)。

- 在 agent view 中，頁腳顯示 `Press enter again to restart this session — it isn't responding (its conversation is saved and resumes).` 在同一列上再次按 `Enter`，Claude Code 會停止無回應的程序並重新啟動工作階段；它在沒有第二次按下的情況下不會停止任何內容。
- 從 shell，`claude attach <id>` 報告原因並退出，告訴您執行 `claude stop <id>`，然後 `claude attach <id>`。

### 工作階段在啟動前失敗，並出現 `possibly low memory` 註記

當背景工作階段的程序在完成啟動前退出，且主機記憶體不足時，該列的狀態會命名退出並新增 `possibly low memory — free some up and retry`。 該註記是一個假設，而不是確認的原因。Claude Code 只在程序無聲退出時新增它，沒有寫入錯誤，也沒有被信號停止，且主機在該時刻報告記憶體不足。當程序在退出前確實寫入了錯誤時，該列會改為顯示該錯誤。 釋放機器上的記憶體，然後附加或回覆該列，監督程序會為工作階段啟動新的程序。當記憶體保持不足時，監督程序也會[停止閒置工作階段](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)以自行釋放資源，如果停止其他工作階段沒有釋放任何內容，也會停止閒置釘選工作階段。

### Agent view 表示背景服務未回應

如果附加、查看或 `claude logs` 報告背景服務未回應，監督程序可能已停止回應。停止它並讓下一個 `claude agents` 啟動新的程序。若要在重新啟動期間保持背景工作階段執行，請傳遞 `--keep-workers`：

```
claude daemon stop --any --keep-workers

```

新的監督程序會重新連接到執行中的工作階段。如果沒有 `--keep-workers`，該命令也會結束背景工作階段。`--any` 旗標確認您想要停止按需啟動的監督程序，而不是作為已安裝的服務啟動的程序，這是預設值。 啟動但無法接受連接的監督程序會自行退出並釋放其鎖定，因此下一個 `claude agents` 會啟動新的程序，無需此手動停止。上述步驟適用於執行中的監督程序停止回應的情況。 如果命令改為退出，說記錄的程序無法驗證為監督程序，請檢查報告的程序 ID：如果它是您擁有的監督程序，自行停止它，然後刪除 `~/.claude/daemon.lock`，以便下一個 `claude agents` 啟動新的程序。 在 Windows 上，如果監督程序未回應停止請求，該命令會列印其程序 ID。使用 `taskkill /PID <pid>` 結束該程序以完成復原。當您傳遞 `--keep-workers` 時，背景工作階段仍會被保留。

### 背景分派失敗，出現 `Could not resolve authentication method`

如果背景分派失敗，出現 `Could not resolve authentication method`，而互動式工作階段正常驗證，接收分派的背景工作程序未取得認證。背景工作階段從[監督程序](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)取得其認證，因此此錯誤表示監督程序本身沒有可用的已儲存認證。確認您已執行 `/login` 或設定 API 金鑰，然後停止監督程序：

```
claude daemon stop --any --keep-workers

```

下一個 `claude agents` 或 `claude --bg` 啟動新的監督程序，該程序會讀取您的已儲存認證。如果您使用環境變數（例如 `ANTHROPIC_API_KEY`）而不是 `/login` 進行驗證，請從設定該變數的 shell 執行下一個命令。 請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors#could-not-resolve-authentication-method)以取得完整的原因和修復清單。

### 背景工作階段無法在 macOS 上讀取 Desktop、Documents 或 Downloads

在 macOS 上，背景工作階段主機作為其自己的程序執行，並與您的終端分開請求對受保護資料夾的存取。如果背景工作階段在讀取 `~/Desktop`、`~/Documents`、`~/Downloads` 或其他受保護位置時報告 `Operation not permitted`，請在系統設定中的隱私與安全性 > 檔案和資料夾下授予存取權限，或為該項目啟用完整磁碟存取。 使用原生安裝程式，該項目會顯示為 Claude Code，授予的權限在更新後會保留。使用其他安裝方法（例如 Homebrew 或 npm），該項目會顯示二進位檔路徑，更新後可能需要再次授予。

### 背景工作階段無法在 macOS 上連接到本機網路主機

在 macOS 15 及更新版本上，系統會阻止程序連接到您本機網路上的裝置，直到您授予本機網路權限，因此針對 LAN 位址的命令可能會在背景工作階段中失敗，出現 `connect: no route to host`，即使相同的命令在前景終端中有效。背景工作階段中連接到本機網路位址的第一個命令會觸發 Claude Code 的 macOS 本機網路權限提示。授予一次，這些命令就能像在前景終端中一樣連接到 LAN 主機。

### 工作階段在附加後響應緩慢

當完成或等待您下一個訊息的工作階段在未附加的情況下閒置約一小時時，監督程序會停止其程序以釋放資源。附加會啟動從中斷的地方開始的新程序，並在程序重新啟動時立即切換到工作階段。正在工作、暫停在權限提示或其他對話上，或[釘選](https://code.claude.com/docs/zh-TW/agent-view#organize-the-list)的工作階段不會以這種方式停止，因此使用 `Ctrl+T` 釘選工作階段以保持其回應性。 當程序啟動時，Claude Code 會顯示工作階段文字記錄的尾部，格式化為即時工作階段呈現的方式，包含 markdown、突出顯示的程式碼區塊和工具呼叫作為暗淡列，上方有暗淡提示區域和 `Session is starting` 註記。即時工作階段在準備好時立即取代它。

### `.claude/worktrees/` 正在填滿

在 agent view 中刪除工作階段會移除 Claude 為其建立的 worktree，但[某些刪除會保留 worktree 或在磁碟上留下其目錄](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)，因此剩餘目錄可能會累積。Git 不再識別的目錄不會出現在 `git worktree list` 中，因此請手動移除這些目錄。 在專案目錄中使用 `git worktree list` 列出剩餘條目，並使用 `git worktree remove <path>` 移除每個。請參閱[清理 worktrees](https://code.claude.com/docs/zh-TW/worktrees#clean-up-worktrees)。

## 限制

Agent view 是研究預覽版本，具有以下限制：

- **速率限制適用** ：背景工作階段與互動工作階段一樣消耗您的訂閱使用量，因此並行執行十個代理的使用配額速度快十倍。
- **工作階段是本地的** ：背景工作階段在您的機器上執行。它們在睡眠時保留，但如果機器關閉則停止。
- **Claude 建立的 worktrees 在 agent view 中隨工作階段刪除** ：在刪除在其自己的 worktree 中編輯檔案的工作階段之前，提交變更。[某些刪除會改為保留 worktree](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)。

## 相關資源

如需了解在平行中執行 Claude 的其他方式，以及在您執行的工作階段之間傳遞發現結果，請參閱：

- [在平行中執行代理](https://code.claude.com/docs/zh-TW/agents)：比較 agent view 與 subagents、agent teams 和 worktrees
- [跨工作階段傳訊](https://code.claude.com/docs/zh-TW/cross-session-messaging)：讓您的工作階段相互傳遞發現結果
- [Agent teams](https://code.claude.com/docs/zh-TW/agent-teams)：協調相互傳遞訊息的多個工作階段
- [在雲端使用 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：在受管雲環境中執行工作階段，而不是本地執行
- [Projects](https://code.claude.com/docs/zh-TW/claude-projects)：讓 Claude 從一個對話協調平行雲工作階段，並告訴您哪些需要您

## 版本歷史

Agent view 在研究預覽期間發展迅速。如果您使用較舊的 Claude Code 版本，本頁上的某些行為可能會有所不同；特別是，`claude agents` 會以 `unknown option` 錯誤拒絕它尚不支援的旗標。下表列出了每個旗標和行為何時新增。

| 版本     | 變更                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| v2.1.268 | 當[刪除因 git 或您的 `WorktreeRemove` hook 無法移除 worktree 而被拒絕](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)時，訊息會命名原因，包括 hook 如何結束及其 stderr 的開始。對於位於儲存庫的 `.claude/worktrees/` 下的連結 worktree，沒有對追蹤檔案的未提交變更、其內沒有巢狀儲存庫，且沒有其他工作階段的記錄命名它，再次刪除工作階段會從 agent view 或使用 `claude rm <id> --force-remove-worktree <worktree-id>` 移除目錄。在此版本之前，列只顯示 `worktree could not be removed (WorktreeRemove hook failed)` 或 git 的錯誤，hook 的 stderr 只進入偵錯日誌，再次刪除被以相同方式拒絕。                                                                                            |
| v2.1.268 | 在第一個 `←` 顯示 `Press ← again to open agents` 或在附加的工作階段中 `Press ← again to go back to agents` 後，[至少一秒後到達的第一次按下會切換](https://code.claude.com/docs/zh-TW/agent-view#switch-sessions-without-leaving-the-terminal)，即使中間更快的按下被忽略。在此版本之前，每次被忽略的按下都會重新啟動等待，所以以穩定的速度再次按 `←` 直到您暫停超過一秒才會切換。                                                                                                                                                                                                                                                                                                                                        |
| v2.1.260 | 當您[背景化工作階段](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)時，您的其他工作階段的[代理清單](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)會顯示對話一次，作為其背景工作階段，它們對它的訊息不再到達您移動它的終端。在此版本之前，該終端可能會在對話名稱下列為第二個互動工作階段，在移動前已訊息對話的工作階段會繼續傳遞到該終端。                                                                                                                                                                                                                                                                                                       |
| v2.1.260 | 當[刪除因未推送的提交而被拒絕](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)時，訊息會命名 worktree 的分支及有多少提交未推送，再次刪除工作階段會丟棄 worktree 及其提交。在此版本之前，拒絕只說 `worktree has commits that are not pushed anywhere`，再次刪除被以相同方式拒絕，刪除工作階段需要推送提交或手動移除 worktree。                                                                                                                                                                                                                                                                                                                                                            |
| v2.1.257 | `←` [在 `/btw` 覆蓋層開啟時從附加的工作階段分離](https://code.claude.com/docs/zh-TW/agent-view#attach-to-a-session)，即使在中途回答，覆蓋層會在您下次附加時重新開啟。在此版本之前，覆蓋層開啟時 `←` 不會分離。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| v2.1.257 | 當您執行 [`claude --resume <session-id> --bg`](https://code.claude.com/docs/zh-TW/agent-view#from-your-shell) 時，Claude Code 會在其自己的 ID 下繼續該工作階段，或在新 ID 下啟動副本並列印 `note:` 行說明原因。`--continue`、裸露的 `--resume` 和帶有名稱或路徑的 `--resume` 會啟動具有相同備註的副本。在此版本之前，`--resume` 與 `--bg` 總是在新 ID 下啟動副本且不說任何內容。                                                                                                                                                                                                                                                                                                                                        |
| v2.1.257 | 當您從使用 `←` 開啟的 agent view 分派工作階段時，Claude Code 會在[目標目錄透過 `permissions.defaultMode` 配置的權限模式](https://code.claude.com/docs/zh-TW/agent-view#permission-mode)中啟動它。當目錄未設定一個時，您來自的工作階段的權限模式適用。在此版本之前，分派的工作階段總是在您來自的工作階段的權限模式中啟動，覆蓋它。                                                                                                                                                                                                                                                                                                                                                                                       |
| v2.1.257 | Agent view 中的 `Ctrl+S`、`Ctrl+T` 和 `Ctrl+G` [遵循您的 `keybindings.json`](https://code.claude.com/docs/zh-TW/agent-view#keyboard-shortcuts)：`Ctrl+S` 和 `Ctrl+T` 透過 `Agents` 內容的 `agents:switchView` 和 `agents:togglePin` 動作，以及 `Ctrl+G` 透過 `Chat` 內容的 `chat:externalEditor` 繫結。在此版本之前，agent view 忽略 `keybindings.json`，這些鍵是固定的。                                                                                                                                                                                                                                                                                                                                               |
| v2.1.257 | 啟動[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)會從兩個失敗原因恢復。在 macOS npm 安裝上，自我更新期間的啟動[等待安裝](https://code.claude.com/docs/zh-TW/errors#eacces-when-starting-a-background-session)，而不是執行 npm 在取代二進位檔時放下的預留位置。在 Windows 上，在機器上次啟動前寫入的過時 `daemon.lock`，或其記錄的程序 ID 現在屬於不同程序的，會被取代。在此版本之前，macOS 啟動在安裝視窗期間失敗，出現 `Error: claude native binary not installed.`，Windows 鎖定使每次啟動都失敗，出現 [`exited before it became reachable`](https://code.claude.com/docs/zh-TW/errors#background-service-exited-before-it-became-reachable)，直到您刪除 `~/.claude/daemon.lock`。 |
| v2.1.257 | 當您在另一個 Claude Code 程序下載 npm 更新時開啟或分派背景工作階段時，Claude Code [保持等待最多兩分鐘](https://code.claude.com/docs/zh-TW/errors#eacces-when-starting-a-background-session)，同時安裝執行，然後失敗，說 `Claude Code is being updated by npm on this machine`。在此版本之前，等待在十秒時停止，所以開啟在下載仍在執行時失敗，出現 `Couldn't start the background service`。                                                                                                                                                                                                                                                                                                                             |
| v2.1.257 | 持有[跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)等待您批准的背景工作階段在其 `Needs input` 列上顯示 `approve message from`，帶有寄件者的地址和寄件者聲稱的名稱。在此版本之前，列移到 `Needs input` 但保留其先前的文字，所以 `claude agents` 中沒有任何內容命名等待的訊息或其寄件者。                                                                                                                                                                                                                                                                                                                                                                           |
| v2.1.257 | 在開啟的背景工作階段內使用 `Ctrl+S` 隱藏的提示[與工作階段一起保留](https://code.claude.com/docs/zh-TW/agent-view#what-persists-across-restarts)，所以 `Ctrl+S` 在工作階段的程序停止並再次啟動後恢復它。在此版本之前，隱藏只存在於執行中的程序中，當工作階段閒置足夠長的時間以至於其程序停止時，或當它停止然後重新開啟時會遺失。                                                                                                                                                                                                                                                                                                                                                                                         |
| v2.1.251 | 在尚未[移入 worktree](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated) 的背景工作階段中，Claude 和它生成的子代理可以編輯連結 git worktree 內的檔案。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| v2.1.251 | Claude Code 轉發在您分派的 shell 中匯出的雲端提供者閘道，例如 `ANTHROPIC_VERTEX_BASE_URL` 或 `ANTHROPIC_BEDROCK_BASE_URL` 及其驗證繞過旗標，到[工作階段的工作程序](https://code.claude.com/docs/zh-TW/agent-view#llm-gateway)，條件與 `ANTHROPIC_BASE_URL` 相同。在此版本之前，如果您只透過這樣的閘道背景化或分派，工作階段進行的每個請求都失敗，因為端點和旗標從其環境中被丟棄。                                                                                                                                                                                                                                                                                                                                       |
| v2.1.251 | 當背景工作階段在另一個 Claude Code 程序重新整理[外掛程式市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)時啟動，例如執行[市場自動更新](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)的同級工作階段，Claude Code 保持該市場的外掛程式可用。在此版本之前，這樣的工作階段可能在沒有該市場的任何技能、代理、hooks 和 MCP 伺服器的情況下啟動，並在其整個執行期間保持這樣。                                                                                                                                                                                                                                                                                                        |
| v2.1.248 | [分派輸入](https://code.claude.com/docs/zh-TW/agent-view#keyboard-shortcuts)中的 `Shift+Enter` 插入換行符，符合主提示，`Ctrl+Enter` 在 `?` 覆蓋層列出 `ctrl+enter to start and open` 的終端中立即分派並附加。在此版本之前，`Shift+Enter` 分派並附加。                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| v2.1.248 | [刪除工作階段](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)在 worktree 的提交已在您的 `origin` 遠端預設分支的本機副本上且您的主簽出已簽出該分支時成功；在此版本之前，刪除被拒絕，出現 `has commits that are not pushed anywhere`。                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| v2.1.248 | 使用 `←` 或 `/background` 背景化的工作階段在執行時持有其 worktree 上的 [`git worktree lock`](https://code.claude.com/docs/zh-TW/worktrees#clean-up-subagent-and-background-session-worktrees)；在此版本之前，背景化釋放鎖定，清理或 `git worktree remove` 可以在執行中的工作階段下移除 worktree。                                                                                                                                                                                                                                                                                                                                                                                                                       |
| v2.1.248 | 未等待您輸入且在其最後活動超過 48 小時後被發現已死亡的背景工作階段，例如在機器關閉數天後，[顯示為已停止](https://code.claude.com/docs/zh-TW/agent-view#sessions-show-as-failed-after-shutdown)，出現 `ended while the background service was off`，`Enter` 在它上面會在恢復其已保存的對話前詢問。在此版本之前，這樣的工作階段重新出現為新鮮失敗，排序到列表的頂部，單一 `Enter` 將數週前的對話拉入前景。                                                                                                                                                                                                                                                                                                                |
| v2.1.248 | 開啟已停止列，其對話[您在另一個終端恢復](https://code.claude.com/docs/zh-TW/agent-view#opening-a-session-says-the-conversation-is-already-open)被拒絕，出現 `Can't open — this session is running in another terminal`，列顯示 `Open in a terminal` 而不是在 `Working` 下顯示。在此版本之前，開啟列啟動第二個程序寫入相同的對話。                                                                                                                                                                                                                                                                                                                                                                                       |
| v2.1.248 | 等待權限決定的背景工作階段，同時 `PermissionRequest` 或 `PreToolUse` hook 列印了無效答案[在其列上命名 hook 事件和架構錯誤](https://code.claude.com/docs/zh-TW/agent-view#peek-and-reply)。在此版本之前，列只顯示待決請求。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| v2.1.248 | 在 Windows 上，`claude agents` 在早期程序留下 win32-input-mode 的終端標籤中啟動時回應鍵盤。在此版本之前，Claude Code 沒有解碼這樣的標籤傳送的關鍵記錄。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| v2.1.247 | 在 Linux 和 WSL 上，[其終端主機程序已死亡](https://code.claude.com/docs/zh-TW/agent-view#the-terminal-host-died-or-the-session-stopped-responding)的工作階段在數秒內失敗，出現原因。沒有輸出的開啟在約十秒後結束，出現重新啟動提供，`Enter` 在列上使用其對話重新啟動工作階段；`claude attach <id>` 報告原因並退出。在此版本之前，開啟這樣的工作階段無限期地顯示 `opening… · esc to cancel`，`claude attach <id>` 等待而不報告錯誤。                                                                                                                                                                                                                                                                                     |
| v2.1.246 | 在 npm 安裝上，當[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)在 `npm install -g @anthropic-ai/claude-code` 取代二進位檔時無法啟動時，Claude Code 等待最多十秒以完成安裝並重試，然後報告 [`EACCES: permission denied`](https://code.claude.com/docs/zh-TW/errors#eacces-when-starting-a-background-session)。                                                                                                                                                                                                                                                                                                                                                                        |
| v2.1.246 | 當[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)程序在列印錯誤後死亡時，Claude Code 報告失敗並[引用服務的第一個錯誤行](https://code.claude.com/docs/zh-TW/errors#background-service-exited-before-it-became-reachable)。                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| v2.1.246 | 如果您的機器在[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)啟動時進入睡眠，Claude Code 會重試啟動一次，而不是失敗。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| v2.1.246 | Claude Code 等待約兩分鐘，而不是 45 秒，以便新啟動的[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)活著但接受連接速度緩慢。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| v2.1.246 | [背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)從您的主目錄啟動，所以在 macOS 和 Linux 上已刪除或移動的啟動目錄不再阻止啟動。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| v2.1.246 | `/fork` [複製完整對話](https://code.claude.com/docs/zh-TW/agent-view#copy-the-session-with-%2Ffork)，來自本身作為副本啟動且未記錄新提示的工作階段：您附加到的 `/fork` 副本、在 `←` 或 `/background` 將其移到背景後重新附加的工作階段，或使用 `claude --resume <id> --fork-session` 啟動的工作階段。在此版本之前，如果您在這樣的工作階段中在傳送新提示前執行 `/fork`，Claude Code 列印正常確認但使用空對話啟動副本。使用 `←` 或 `/background` 將這樣的工作階段移到背景以相同方式遺失對話。                                                                                                                                                                                                                               |
| v2.1.246 | 當您開啟您剛分派的工作階段，同時其工作程序仍在啟動時，例如按 `Enter` 在其列上，Claude Code 等待程序然後附加。在此版本之前，如果您在程序仍在啟動時按 `Enter`，Claude Code 可能會停止工作階段，出現 [`Session <id> was stopped while the respawn was in flight`](https://code.claude.com/docs/zh-TW/errors#session-was-stopped-while-the-respawn-was-in-flight)。                                                                                                                                                                                                                                                                                                                                                         |
| v2.1.246 | 當您[背景化](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)命名的工作階段時，Claude Code 列出它一次，當您再次背景化相同的對話時，它對新列的名稱進行編號，例如 `my-session (2)`，現有列保留其名稱。在此版本之前，您按 `←` 的終端可能在 `claude agents --json` 中作為同一名稱下的第二個工作階段出現，如果您再次背景化相同的對話，Claude Code 在相同名稱下新增另一列。                                                                                                                                                                                                                                                                                                                               |
| v2.1.239 | 使用 [vim 編輯器模式](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode)開啟，在 agent view 的輸入中按 `Esc` 從 INSERT 切換到 NORMAL 模式並保留您的文字，符合主提示；在 NORMAL 模式下，輸入中仍有文字，按 `Esc` 清除它，在空輸入上按 `Esc` 退出，如 [`Esc` 快捷鍵](https://code.claude.com/docs/zh-TW/agent-view#keyboard-shortcuts)描述。在此版本之前，`Esc` 清除輸入。                                                                                                                                                                                                                                                                                                                              |
| v2.1.233 | 對於連結到 GitLab 合併請求的工作階段，Claude Code 以 GitLab 的 `!1234` 參考語法寫入列的標籤。您也可以將合併請求的 URL 貼到[分派輸入](https://code.claude.com/docs/zh-TW/agent-view#filter-sessions)中以選擇該工作階段。在此版本之前，標籤呈現為 `#1234`，貼上的合併請求 URL 只在其第一個提示包含 URL 時符合工作階段。                                                                                                                                                                                                                                                                                                                                                                                                   |
| v2.1.227 | [刪除工作階段](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)在另一個活躍 Claude Code 工作階段在該 worktree 目錄內執行時保留工作階段及其 worktree。Agent view 在列上顯示 `not deleted` 及頁尾中的原因，`claude rm` 列印 `kept <id>` 及原因，命名其他工作階段的程序 ID。在此版本之前，刪除工作階段在其他工作階段仍在其中工作時移除 worktree。                                                                                                                                                                                                                                                                                                                                            |
| v2.1.225 | 您未信任的目錄中的 `claude agents` 顯示與 `claude` 在啟動時顯示的相同[工作區信任對話](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)，在 agent view 開啟前。接受會為該工作區保存信任；拒絕會在不開啟 agent view 的情況下退出。在此版本之前，`claude agents` 開啟而不詢問，所以您從它分派的工作階段在您從未被要求信任的目錄中執行。                                                                                                                                                                                                                                                                                                                                             |

列按目錄分組，將滑鼠懸停在列上會突出顯示它，而不改變[分派目標](https://code.claude.com/docs/zh-TW/agent-view#dispatch-to-a-specific-directory)；使用箭頭鍵或點擊選擇列仍會改變目標。在此版本之前，將滑鼠移到另一個專案中的工作階段會無聲地改變下一個分派的工作階段啟動的目錄。 |\
| v2.1.221 | `/status` 顯示 `Session kind` 列：背景工作階段中的 `background job · attached` 或 `background job · unattended`，取決於是否附加了終端，以及任何其他工作階段中的 `interactive`。在此版本之前，`/status` 沒有報告工作階段種類。

`/fork`：Claude Code 指示[副本](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)隔離其工作與原始工作階段的：副本在進行程式碼變更前建立自己的 worktree，遠離原始工作階段的 worktree，當其任務建立在該工作上時基於原始分支的新分支。請參閱連結的部分以了解確切條件。在此版本之前，副本沒有收到隔離指令，可能最終編輯原始工作階段仍在工作的 worktree 或簽出。

使用 [vim 編輯器模式](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode)開啟，在使用 `u` 撤銷提示回到空後立即按 `←` 會詢問與刪除文字或移動提示歷史相同的確認，並僅在第二次按下時切換；在此版本之前按下立即切換。 |\
| v2.1.219 | 使用 [vim 編輯器模式](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode)開啟，在空提示上按 `←` 從 NORMAL 模式以及 INSERT 開啟 agent view，頁尾的 `←` 提示在 NORMAL 模式中顯示；在此版本之前手勢和提示是 INSERT 專用的，在 NORMAL 模式中空提示上的 `←` 不執行任何操作。在 Claude Code 等待背景化工作階段時輸入輸入會取消切換，出現 `Backgrounding cancelled — you have unsent text in the input. Send it or clear it, then press ← again.` 所以輸入的草稿不會遺失。 |\
| v2.1.218 | 在清空提示的刪除後兩秒內或移動提示歷史後按 `←` 顯示 `Press ← again to open agents`，或在附加的工作階段中 `Press ← again to go back to agents`，並僅在至少一秒後的第二次按下時切換；在此版本之前按下立即切換。到達貼上或指令碼輸入內的 `←` 不再觸發切換。使用 `←` 背景化前景工作階段在列上方顯示 `Your conversation moved to the background`，`Esc` 在 agent view 的根部返回該對話，而不是退出到 shell，雙 `Ctrl+C` 保持退出；如果對話無法重新開啟，Claude Code 退出並列印 `claude --resume` 命令。在 Windows 上，在附加後約半秒內按下的 `←` 顯示 `Ambiguous ←, press again to detach` 並在第二次按下時分離。 |\
| v2.1.217 | 工作階段列上的拉取請求徽章呈現為超連結，即使 Claude Code 無法偵測終端超連結支援，例如透過 SSH 或 tmux；設定 [`FORCE_HYPERLINK=0`](https://code.claude.com/docs/zh-TW/env-vars) 以將其呈現為純文字。在此版本之前，未偵測到支援時徽章呈現為純文字。 |\
| v2.1.216 | `/fork`：[確認](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)是一行，顯示副本的狀態、其 agent view 列的名稱及其工作階段 ID 以供 `claude attach`，僅當副本在主工作樹中執行或編輯您開啟的簽出時以 `runs in the origin tree` 或 `edits this checkout` 結尾。點擊名稱會背景化此工作階段並在副本的工作階段中開啟 agent view。確認不再重述副本的繼承權限模式；較早版本列印多行確認，沒有可點擊的名稱。

需要輸入：`/install-github-app` 和 `/mcp` 設定清單，在沒有人附加時執行，在 `Needs input` 下顯示工作階段，帶有命名命令的列，附加並重新執行命令會繼續；從 v2.1.208 到 v2.1.215 它們在該狀態下被直接拒絕。

`--agent` 恢復：恢復或重新啟動[背景化 `--agent` 工作階段](https://code.claude.com/docs/zh-TW/agent-view#from-your-shell)會恢復代理的系統提示和工具限制，在工作階段自己的目錄中搜尋代理，當其工作區被信任時；代理不再存在的工作階段會繼續使用預設工具和系統提示，並以可見警告開啟，而不是無聲地還原為預設代理。

`Ctrl+X`：按兩次會刪除工作階段，即使停止嘗試失敗，而不是失敗的停止取消待決刪除，已刪除的工作階段，其工作程序已死亡，不再在下一次重新整理時重新出現。

Worktree 刪除：其 worktree 目錄不屬於任何 git 儲存庫的工作階段可以被刪除；在此版本之前，每次刪除這樣的工作階段的嘗試都被拒絕。已消失的目錄立即清除。Agent view 雙按移除仍有檔案的目錄，為 hook 建立的目錄執行您的 `WorktreeRemove` hook，除非另一個工作階段的記錄也命名它。`claude rm` 只要檔案仍然存在就保留這樣的目錄。 |\
| v2.1.214 | 使用 `←` 或 `/background` 背景化且閒置時沒有執行任何操作的工作階段會停止其程序，如同任何其他閒置工作階段，而不是保持其程序和背景服務無限期執行。已完成的工作階段可以在背景服務閒置後使用 `claude rm` 或從 agent view 移除，進入 worktree 的工作階段在從不是 git 儲存庫的目錄分派後，例如多儲存庫工作區資料夾，當 worktree 本身屬於 git 儲存庫時可以從 agent view 刪除，因為清理是從 worktree 而不是分派工作階段的目錄解決的；兩次移除在之前的每次嘗試都被拒絕。重新開啟已停止的工作階段會恢復其已保存的對話，即使記錄存儲中的資料夾無法讀取。 |\
| v2.1.213 | `/install-github-app`、[`/mcp`](https://code.claude.com/docs/zh-TW/mcp) 設定清單和 MCP 驗證動作在附加終端時在背景工作階段中工作，僅當沒有人附加時被拒絕，帶有告訴您附加並再次執行命令的訊息；從 v2.1.208 到 v2.1.212 即使附加了終端也被拒絕。 |\
| v2.1.212 | [互動工作階段中的 `/fork`](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session) 將對話複製到顯示為其自己列的新背景工作階段，以它來自的工作階段命名，或對於未命名工作階段的提示分支，以分支提示命名，而原始工作階段保持執行；`/fork` 的較早分支子代理行為移到 `/subtask`。使用[關閉 agent view](https://code.claude.com/docs/zh-TW/agent-view#turn-off-agent-view)，`/fork` 保持分支子代理行為。等待其第一個提示的焦點列顯示 `space to send it a prompt`。`Ctrl+J` 在具有擴展鍵報告的終端上在分派輸入中插入換行符，其中按鍵先前被忽略，`?` 覆蓋層列出快捷鍵。當背景工作階段完成且沒有任何需要您輸入時，互動工作階段中的 `←` 頁尾提示簡要顯示 `N done`。在 agent view 中輸入裸露的 `/resume` 會開啟您開啟 agent view 的儲存庫的過去工作階段的選擇器，包括從列表中刪除的工作階段，選擇一個會將其恢復為背景工作階段；在此版本之前 `/resume` 在 agent view 中不可用，已刪除的工作階段只能透過 `claude --resume` 或互動工作階段中的 `/resume` 到達。目標、範圍和受限形式保留較早版本為每個形式顯示的 `attach to a session to run it` 提示。等待沙箱網路主機提示、MCP 輸入請求或受管設定提示的工作階段在 agent view 和 `claude agents --json` 中顯示為 `Needs input` 而不是 `Working`，Claude 的問題報告 `waitingFor: input needed` 而不是 `permission prompt`。附加到其程序已停止的工作階段會顯示其記錄，格式化為活躍工作階段呈現的方式，而不是原始文字。已停止的工作階段，其記錄在意外位置，透過您已保存記錄的最後手段掃描恢復，開啟沒有已保存記錄的列顯示 `Press enter again to restart this session fresh`，在第二次按下時新鮮重新啟動；v2.1.211 顯示拒絕，沒有辦法從 agent view 重新啟動。 |\
| v2.1.211 | 喚醒已停止的工作階段，透過附加或從其執行的目錄回覆，再次轉發您的 shell 的閘道 `ANTHROPIC_BASE_URL`，條件與新鮮分派相同，所以透過閘道 `ANTHROPIC_AUTH_TOKEN` 驗證的工作階段在閘道上恢復，而不是報告 `Not logged in`。附加到在另一個對話之前背景化的已停止工作階段，在其第一個回應完成前被拒絕，出現 `This session has no saved transcript` 而不是無聲地在相同工作階段 ID 下啟動空白對話；從 agent view 開啟相同列顯示頁尾中的拒絕。從 Claude Code 外部結束 `←` 或 `/background` 工作階段的程序會將其標記為已停止，而不是監督程序重新啟動它，已記錄在磁碟上的停止會被尊重，除非您傳送的回覆仍在等待傳遞，崩潰後重新啟動的工作階段被告知它已重新啟動，重新啟動的 `←` 或 `/background` 工作階段不會恢復超過約一小時的中斷回應。回答或拒絕提示而不是標籤的工作階段命名回覆，例如對於主要是連結的提示，會被丟棄，列保留從提示文字取得的名稱。其 worktree git 不再識別的工作階段刪除成功，在磁碟上留下 worktree 目錄並命名其路徑，而不是每次嘗試都被拒絕。拒絕的刪除在工作階段列上顯示原因，包括 worktree 無法移除時的基礎 git 錯誤，而不是列無聲地重新出現。 |\
| v2.1.210 | `claude attach` 在背景服務啟動或重新連接時等待，而不是失敗，出現 `job not found` 或 `still starting` 錯誤，報告在附加期間完成的工作階段為已退出，並應用在慢速附加期間進行的終端調整大小，當附加完成時。提示頁尾的 `←` 需要輸入計數出現在每個提供者上，包括先前顯示純 `← for agents` 形式的第三方提供者。使用 `←` 背景化工作階段會將 Claude 的任務清單帶到背景工作階段，而不是丟棄它。您按 `←` 的列在選擇移動後保留粗體、未變暗的名稱。`claude agents --effort` 接受 `ultracode` 而不是無聲地丟棄它。 |\
| v2.1.208 | 附加到其程序已停止的工作階段會顯示其記錄的最後一屏，同時程序啟動，而不是只顯示 `Session is starting` 備註。無法傳遞的回覆（因為背景服務無法連線或傳送失敗）會被保存，並在其程序再次啟動時作為工作階段的下一個提示傳送；在此版本之前，背景服務無法連線時遺失的回覆會被丟棄。其自身二進位檔被更新取代的程序仍然可以啟動監督程序，從已安裝的 `claude` 啟動器或磁碟上的最新版本，而不是失敗直到 Claude Code 重新啟動。執行較舊版本的監督程序永遠不會將由較新版本啟動的閒置工作階段重新啟動到其自身較舊的二進位檔。刪除工作階段會移除其 worktree，即使工作階段將 worktree 移到不同的分支，並在 worktree 有未推送到任何地方的提交或另一個工作階段聲稱它時將 worktree 與工作階段列保持在一起，而不是銷毀提交或孤立 worktree。`/install-github-app` 和 `/mcp` 設定清單及其驗證動作在背景工作階段中被拒絕，並顯示命名替代方案的訊息；在 v2.1.208 中，`/model` 選擇器以相同方式被拒絕，輸入的 `/model <name>` 只切換該工作階段，而不是也保存您的預設模型。 |\
| v2.1.207 | 查看面板以列截斷的句子開啟，例如等待您的工作階段的確切問題，並顯示被阻止的工作階段已等待多長時間，作為單一 `waiting 3m` 行，而不是將相同的時間戳記前綴到狀態句子和問題。在分派輸入中再次貼上相同的文字會展開摺疊的 `[Pasted text #N]` 預留位置，而不是新增第二個。按名稱接受計畫的背景工作階段會在其列上顯示該名稱。移入 worktree 的背景工作階段在其程序從 agent view 重新啟動時會保留其對話。 |\
| v2.1.206 | 列摘要填充列的剩餘寬度，並僅在終端的右邊緣截斷，而不是在 64 欄處。監督程序重新啟動到新的 Claude Code 版本後，它會在背景中將剩餘的閒置背景工作階段重新啟動到該版本，而不是每分鐘幾個。使用 `Ctrl+X` 或 `claude rm` 刪除工作階段也會從監督程序的工作階段清單中清除它，因此列在監督程序重新啟動後不再重新出現。在分派 shell 中匯出的 `CLAUDE_CODE_EXTRA_BODY` 請求本體覆蓋到達背景工作階段，而不是被忽略。 |\
| v2.1.205 | 提示頁尾的 `←` 提示在常規 `claude` 工作階段中計算等待您的背景代理，例如 `← 2 agents`。列摘要顯示工作階段自己的單行報告，在 64 欄處截斷，而不是原始工具叫用或 `done/total` 計數；目錄分組列以彩色狀態字開啟。查看面板以完整狀態句子開啟，對於等待您的工作階段，其確切問題顯示在回覆輸入上方。編輯、評論、關閉或使用 `gh` 標記拉取請求為就緒的工作階段會連結到它，不僅是建立或簽出拉取請求的工作階段，推送會連結拉取請求，即使本機分支名稱不符，建立命令的輸出超過內聯限制的拉取請求也會連結。沒有可讀文字的轉向會保留工作階段的先前狀態，而不是將其翻轉回 `Working`。`claude attach` 會等待最多約 60 秒以重新啟動的工作階段，並顯示狀態行說明原因，而不是失敗。 |\
| v2.1.203 | 在分派 shell 中匯出的閘道 `ANTHROPIC_BASE_URL` 會到達從它分派的工作階段進入同一目錄，當監督程序共享該閘道環境時，而不是在保留隨之匯出的 API 金鑰時被丟棄。分派 shell 的 `PATH` 會套用到每個工作階段的工作程序。在子代理執行時按 `←` 會等待它們，而不是在十秒後重新啟動它們。空清單始終顯示區段標題，每個標題下方有描述。在分派輸入中輸入 `@` 也會列出啟動儲存庫的已註冊 git worktrees，這些 worktrees 位於其目錄樹內。從 `effortLevel` 設定繼承的努力會在稍後編輯該設定時跟隨，而不是在分派時固定。開啟其對話已在另一個執行中工作階段中開啟的已停止工作階段會被拒絕並顯示訊息，而不是使列失敗。在 agent view 中不可用的命令會在輸入中保留輸入的文字。在 git 儲存庫外失敗的 `WorktreeCreate` hook 不再阻止工作階段編輯檔案。 |\
| v2.1.202 | 使用 `/rename` 或 `Ctrl+R` 在背景工作階段上設定的名稱在監督程序停止並重新啟動其程序時會保留，而不是還原為工作階段分派時的名稱。 |\
| v2.1.200 | 較舊的 Claude Code 版本在 `roster.json` 中重寫工作階段清單時會保留較新版本寫入的欄位，符合現有的 `state.json` 保證，因此由較新版本啟動的工作階段在監督程序重新啟動後繼續接受輸入。當您開啟已停止回應的工作階段時，監督程序會重新啟動其程序，工作階段會從中斷的地方繼續中斷的回應。Agent view 應用放在 `agents` 後面的 `--plugin-dir` 旗標到其自己的子代理和技能自動完成，在分派輸入中以及分派的工作階段。 |\
| v2.1.199 | 背景工作階段，其程序在低記憶體主機上完成啟動前退出，其列狀態會顯示 `possibly low memory — free some up and retry`，而不是只顯示裸露的退出原因。使用 `←` 或 `/background` 背景化工作階段會將其 `/color` 帶到新列。 |\
| v2.1.198 | Agent view 在背景工作階段需要輸入、完成或失敗時透過 `preferredNotifChannel` 傳送通知，並使用 `agent_needs_input` 或 `agent_completed` 類型觸發 `Notification` hook。`←` 和 `/exit` 在 `claude attach <id>` 內返回 agent view 而不是退出到 shell；`Ctrl+Z` 返回到 shell。隔離其工作在 worktree 中的背景工作階段會提交、推送其自己的隔離分支（絕不是 `main` 或 `master`），並在完成時開啟草稿拉取請求，而不是先詢問。`/login` 在 agent view 中執行並開啟登入對話框。`Background work is running` 退出對話框提供 `Move to background and exit`。退出交付也涵蓋背景子代理，它們在下次喚醒時從其記錄恢復，而不是被報告為失敗。`claude --bg` 與 `-p` 或 `--print` 結合會被拒絕並出現錯誤。背景工作階段主機在首次 LAN 存取時要求 macOS 本機網路權限，而不是失敗，出現 `connect: no route to host`。 |\
| v2.1.196 | 單一 `←` 按下會背景化前景工作階段；較早的版本需要兩次按下，帶有頁尾提示和確認。傳遞給 `claude agents` 的 `--dangerously-skip-permissions` 會顯示繞過免責聲明，而不是被無聲地丟棄。您從未命名的互動工作階段在工作階段清單和 `claude agents --json` 中帶有預設名稱，例如 `my-app-3f`。背景 shell 命令和動態工作流程在工作階段的程序被停止、重新啟動或更新時存活，包括在 Windows 上；設定 `CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF=1` 以關閉交付。在重新啟動時誤讀為空的記錄會被重命名為 `.orphaned-` 後綴，而不是被刪除。 |\
| v2.1.195 | 進行中的工作在您背景化 Windows 上的工作階段時也會轉移；設定 `CLAUDE_DISABLE_ADOPT=1` 以改為停止它。`Completed` 組填充剩餘的垂直空間，標題在短終端上壓縮。較舊的 Claude Code 版本不再丟棄較新工作階段的 `state.json` 欄位或隱藏這些工作階段。附加到已停止的工作階段會立即切換，而不是顯示空白螢幕最多五秒。無法接受連接的監督程序會自行退出並釋放其鎖定。 |\
| v2.1.191 | `claude --bg` 與不符合您任何子代理的 `--agent` 名稱失敗啟動：工作階段立即退出，出現 `--agent '<name>' not found` 錯誤，而不是使用預設代理執行。 |\
| v2.1.174 | 背景工作階段不再繼承閘道端點變數，例如來自監督程序啟動 shell 的 `ANTHROPIC_BASE_URL`；監督程序向預先準備的工作程序提供新的認證快照，修復虛假的 `Could not resolve authentication method` 錯誤。 |\
| v2.1.172 | 分派輸入中的 `/model` 設定工作階段範圍的分派模型覆蓋。 |\
| v2.1.161 | 列摘要顯示平行工作項目的 `done/total` 計數；查看面板命名最長執行的平行工作項目。 |\
| v2.1.157 | `claude agents` 接受 `--agent`；分派的工作階段尊重 `agent` 設定。 |\
| v2.1.145 | 查看面板回覆輸入和分派輸入中支援語音聽寫。 |\
| v2.1.143 | `worktree.bgIsolation` 設定新增；`claude agents` 接受 `--allow-dangerously-skip-permissions`。 |\
| v2.1.142 | `claude agents` 接受 `--permission-mode`、`--model`、`--effort`、`--dangerously-skip-permissions`、`--settings`、`--add-dir`、`--plugin-dir`、`--mcp-config` 和 `--strict-mcp-config`。 |\
| v2.1.141 | `claude agents` 接受 `--cwd` 以將清單範圍限定為一個專案。 |\
| v2.1.139 | Agent view 作為研究預覽版本引入。 |\
是否 助手