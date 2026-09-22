Agent teams 是實驗性功能，預設為停用。透過在 [settings.json](https://code.claude.com/docs/zh-TW/settings) 或環境中設定 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 來啟用。若沒有該變數，工作階段啟動時不會設定任何團隊、不會寫入團隊目錄，Claude 也不會生成或提議隊友。Agent teams 在工作階段恢復、任務協調和關閉行為方面有[已知限制](https://code.claude.com/docs/zh-TW/agent-teams#limitations)。 Agent teams 讓您協調多個 Claude Code 實例一起工作。一個工作階段充當團隊主管，協調工作、分配任務並綜合結果。隊友獨立工作，各自在自己的 context window 中，並直接相互溝通。您也可以直接與任何隊友互動，無需透過主管。 在設定團隊之前，請檢查是否有更輕量的選項可以完成工作。[Subagents](https://code.claude.com/docs/zh-TW/sub-agents) 在單個工作階段內運行，透過[跨工作階段訊息傳遞](https://code.claude.com/docs/zh-TW/cross-session-messaging)，Claude 可以在您自己執行的工作階段之間傳遞發現。 本頁描述的是 v2.1.178 版本的 agent teams。設定 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 後，生成隊友不再需要設定步驟，工作階段退出時會自動清理。在 v2.1.178 之前，您需要要求 Claude 先建立並命名團隊，Claude 使用 `TeamCreate` 和 `TeamDelete` 工具來設定和移除它。這兩個工具已不存在。Agent 工具上的 `team_name` 輸入被接受但被忽略，`TaskCreated`、`TaskCompleted` 和 `TeammateIdle` [hook payloads](https://code.claude.com/docs/zh-TW/hooks#taskcreated) 中的 `team_name` 欄位帶有工作階段衍生的名稱，已被棄用。

## 何時使用 agent teams

Agent teams 最適合用於並行探索能增加真實價值的任務。請參閱[使用案例範例](https://code.claude.com/docs/zh-TW/agent-teams#use-case-examples)以了解完整情景。最強的使用案例是：

- **研究和審查** ：多個隊友可以同時調查問題的不同方面，然後分享並質疑彼此的發現
- **新模組或功能** ：隊友可以各自擁有一個獨立部分，不會相互干擾
- **使用競爭假設進行除錯** ：隊友並行測試不同的理論，更快地收斂到答案
- **跨層協調** ：跨越前端、後端和測試的變更，各由不同的隊友負責

Agent teams 增加了協調開銷，並使用的 tokens 遠多於單個工作階段。當隊友可以獨立運作時，它們效果最佳。對於順序任務、相同檔案編輯或具有許多依賴關係的工作，單個工作階段或 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 更有效。

### 與 subagents 比較

Agent teams 和 [subagents](https://code.claude.com/docs/zh-TW/sub-agents) 都讓您並行化工作，但它們的運作方式不同。對於傳遞訊息給彼此但沒有團隊的獨立工作階段，請參閱[跨工作階段訊息傳遞](https://code.claude.com/docs/zh-TW/cross-session-messaging)。

![比較 subagent 和 agent team 架構的圖表。Subagents 由主代理生成、執行工作並報告結果。Agent teams 透過共享任務列表進行協調，隊友彼此直接溝通。](https://mintcdn.com/claude-code/nsvRFSDNfpSU5nT7/images/subagents-vs-agent-teams-light.png?fit=max&auto=format&n=nsvRFSDNfpSU5nT7&q=85&s=2f8db9b4f3705dd3ab931fbe2d96e42a)
> # Image-1
>
> **圖片摘要：**
> Subagents 與 Agent Teams 的代理分工、任務協作及回報流程圖。
>
> **主要元素：**
> 1. 實體: 多代理工作流, 主代理協調, 子代理分工, 共用任務清單, 團隊成員
> 2. OCR文字:
> Subagents
> Agent Teams
>
> Main Agent
> Spawn Subagent
> Subagent
> Work
> Result
> Report
> Spawn Subagent
> Subagent
> Work
> Result
> Spawn Subagent
> Subagent
> Work
> Result
>
> Main Agent Team Lead
> Spawn Team &
> Assign Tasks
> Shared Task List
> Communicate
> & Claim Tasks
> Teammate
> Work
> Communicate
> & Claim Tasks
> Teammate
> Work
> Communicate
> & Claim Tasks
> Teammate
> Work
> Communicate
> 3. 主題標籤: 多代理系統, 子代理, 代理團隊, 任務分派, 協作流程
>
> **頁面關聯：**
> Subagents 與 Agent Teams 的代理架構比較圖。

![比較 subagent 和 agent team 架構的圖表。Subagents 由主代理生成、執行工作並報告結果。Agent teams 透過共享任務列表進行協調，隊友彼此直接溝通。](https://mintcdn.com/claude-code/nsvRFSDNfpSU5nT7/images/subagents-vs-agent-teams-dark.png?fit=max&auto=format&n=nsvRFSDNfpSU5nT7&q=85&s=d573a037540f2ada6a9ae7d8285b46fd)
> # Image-2
>
> **圖片摘要：**
> Subagents與Agent Teams流程圖：Main Agent分派子代理或團隊，串接工作、通訊與結果。
>
> **主要元素：**
> 1. 實體: Main Agent, Subagent, Agent Teams, Shared Task List, Teammate
> 2. OCR文字:
> Subagents
> Agent Teams
> Main Agent
> Spawn Subagent
> Spawn Subagent
> Spawn Subagent
> Subagent
> Subagent
> Subagent
> Work
> Work
> Work
> Result
> Result
> Result
> Report
> Main Agent (Team Lead)
> Spawn Team & Assign Tasks
> Shared Task List
> Communicate
> & Claim Tasks
> Communicate
> & Claim Tasks
> Communicate
> & Claim Tasks
> Teammate
> Teammate
> Teammate
> Work
> Work
> Work
> Communicate
> Communicate
> Communicate
> 3. 主題標籤: Subagents, Agent Teams, task assignment, task list, team communication
>
> **頁面關聯：**
> Agent Teams與Subagents架構流程圖，錨點為Main Agent
Subagents 只向主代理報告結果。在 agent teams 中，隊友共享任務列表、認領工作並直接相互溝通。

|                                                                                                                      | Subagents                                                                                                                                     | Agent teams                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Context**                                                                                                          | 自己的 context window；結果返回給呼叫者                                                                                                       | 自己的 context window；完全獨立                                                                                                             |
| **溝通**                                                                                                             | 將結果返回給呼叫者。Claude 在生成時命名的 Subagents 也可以[彼此訊息傳遞](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup) | 隊友直接相互訊息傳遞                                                                                                                        |
| **協調**                                                                                                             | 主代理管理所有工作                                                                                                                            | 透過訊息進行自我協調，加上具有 [Task tools 的代理](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability)的共享任務列表 |
| **最適合**                                                                                                           | 只有結果重要的專注任務                                                                                                                        | 需要討論和協作的複雜工作                                                                                                                    |
| **Token 成本**                                                                                                       | 較低：結果摘要返回到主 context                                                                                                                | 較高：每個隊友是一個獨立的 Claude 實例                                                                                                      |
| 當您需要快速、專注的工作人員報告結果時，使用 subagents。當隊友需要分享發現、相互質疑並自行協調時，使用 agent teams。 |                                                                                                                                               |                                                                                                                                             |

## 啟用 agent teams

Agent teams 預設為停用。透過將 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 環境變數設定為 `1`，在您的 shell 環境或透過 [settings.json](https://code.claude.com/docs/zh-TW/settings) 來啟用： settings.json

```
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}

```

啟用 agent teams 也會改變普通的委派。Claude 可能會[自行命名一個 subagent](https://code.claude.com/docs/zh-TW/sub-agents#subagent-names)，而當 agent teams 啟用時，Claude 命名的 subagent 會作為隊友啟動，因此即使您沒有要求，團隊也可能形成。如需更多資訊，請參閱[Claude 如何啟動 agent teams](https://code.claude.com/docs/zh-TW/agent-teams#how-claude-starts-agent-teams)；若要關閉此行為，請參閱 [Claude 生成隊友而非 subagents](https://code.claude.com/docs/zh-TW/agent-teams#claude-spawns-teammates-instead-of-subagents)。 生成隊友也需要互動式工作階段。在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p` 旗標，包括 Agent SDK 工作階段，Claude 不會生成隊友，即使啟用了 agent teams，Claude 命名的 subagent 也會作為普通的 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 執行。

## 啟動您的第一個 agent team

啟用 agent teams 後，用自然語言描述您想要的任務和隊友。Claude 會生成他們並根據您的提示協調工作。 此範例效果很好，因為三個角色是獨立的，可以在不相互等待的情況下探索問題：

```
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Spawn three teammates to explore this from different angles:
one on UX, one on technical architecture, one playing devil's advocate.

```

從那裡，Claude 會建立一個[共享任務列表](https://code.claude.com/docs/zh-TW/interactive-mode#task-list)，在[具有 Task 工具的工作階段](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability)中，為每個觀點生成隊友，讓他們探索問題，並在完成時綜合發現。 Claude 有時可能會使用[子 agent](https://code.claude.com/docs/zh-TW/sub-agents)而不是建立 team。子 agent 會出現在與隊友相同的 agent 面板中，因此單獨的面板不會確認 team 已形成。如果 Claude 生成了子 agent，請再次詢問並明確要求 agent team。 主管的終端在提示輸入下方的 agent 面板中列出隊友。從面板中：

- **向上和向下箭頭** ：選擇隊友
- **Enter** ：開啟所選隊友的記錄並直接向其傳送訊息
- **Escape** ：清除選擇。當您檢視隊友的記錄時，Escape 會中斷該隊友的目前回合

自 v2.1.199 起，當任何隊友或子 agent 仍在工作時，閒置隊友的列會保留在面板中，因此您可以選擇它來檢視其記錄或向其分配更多工作。一旦面板中的每個 agent 都閒置，閒置列會在 30 秒後隱藏，並在隊友的下一個回合時重新出現；隊友在隱藏時仍保持執行狀態且可定址。在 v2.1.181 至 v2.1.198 中，閒置列在其自己的回合結束後 30 秒隱藏，即使其他隊友仍在工作；v2.1.181 之前的版本不會隱藏閒置列。 當超過三個隊友同時閒置時，前三個之外的列會摺疊成單一列，計算摺疊的隊友，例如當五個閒置時顯示 `2 idle agents`。選擇它並按 Enter 以展開摺疊的列，或按 Esc 以再次摺疊它們。工作中的隊友、失敗的隊友和您正在檢視的隊友始終保持自己的列。 如果您希望每個隊友都在自己的分割窗格中，請參閱[選擇顯示模式](https://code.claude.com/docs/zh-TW/agent-teams#choose-a-display-mode)。

## 控制您的 agent team

用自然語言告訴主管您想要什麼。它根據您的指示處理團隊協調、任務分配和委派。

### 選擇顯示模式

Agent teams 支援兩種顯示模式：

- **In-process** ：所有隊友在您的主終端內運行。使用上下箭頭鍵在 agent 面板中選擇隊友，然後按 Enter 鍵查看它並輸入以直接向它傳送訊息。在任何終端中工作，無需額外設定。
- **Split panes** ：每個隊友都有自己的窗格。您可以同時看到所有人的輸出並點擊窗格直接互動。需要 tmux 或 iTerm2。

`tmux` 在某些作業系統上有已知限制，傳統上在 macOS 上效果最佳。在 iTerm2 中使用 `tmux -CC` 是進入 `tmux` 的建議入口點。 預設值是 `"in-process"`。設定 `"auto"` 以在您已在 tmux 工作階段內運行或您的終端是已安裝 `it2` CLI 的 iTerm2 時啟用分割窗格，否則回退到 in-process。`"tmux"` 設定啟用分割窗格模式，並根據您的終端自動偵測是否使用 tmux 或 iTerm2。 自 v2.1.186 起，設定 `"iterm2"` 以明確使用 iTerm2 原生分割窗格。此模式需要 [`it2` CLI](https://github.com/mkusaka/it2)，如果 `it2` 遺失，會顯示帶有安裝命令的錯誤。當您的終端是 iTerm2 且 tmux 可作為備用方案時，在 `"auto"` 或 `"tmux"` 下會出現提供安裝 `it2` 或切換到 tmux 的設定提示。 若要覆蓋預設值，請在 `~/.claude/settings.json` 中設定 [`teammateMode`](https://code.claude.com/docs/zh-TW/settings-reference#teammatemode)：

```
{
  "teammateMode": "auto"
}

```

若要為單個工作階段設定模式，請將其作為旗標傳遞：

```
claude --teammate-mode auto

```

`--teammate-mode` 旗標是實驗性的，不會出現在 `claude --help` 中。 分割窗格模式需要 [tmux](https://github.com/tmux/tmux/wiki) 或 iTerm2 搭配 [`it2` CLI](https://github.com/mkusaka/it2)。若要手動安裝：

- **tmux** ：透過您系統的套件管理器安裝。請參閱 [tmux wiki](https://github.com/tmux/tmux/wiki/Installing) 以了解平台特定的指示。
- **iTerm2** ：安裝 [`it2` CLI](https://github.com/mkusaka/it2)，然後在 **iTerm2 → Settings → General → Magic → Enable Python API** 中啟用 Python API。

### 指定隊友和模型

Claude 根據您的任務決定要生成的隊友數量，或者您可以指定您想要的確切內容：

```
Spawn 4 teammates to refactor these modules in parallel. Use Sonnet for
each teammate.

```

Claude Code 從以下第一個適用的來源為每個隊友選擇模型：

1. 您的生成提示為該隊友命名的模型。
1. 對於從[子 agent 定義](https://code.claude.com/docs/zh-TW/agent-teams#use-subagent-definitions-for-teammates)生成的隊友，定義的 `model`，其中 `inherit` 選擇主管的模型。
1. [`CLAUDE_CODE_SUBAGENT_MODEL`](https://code.claude.com/docs/zh-TW/model-config#environment-variables)，當它設定為 `inherit` 以外的任何值時。
1. 主管的目前模型。

如果您設定 [`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`](https://code.claude.com/docs/zh-TW/sub-agents#run-every-subagent-on-one-model)，前兩個來源不適用。當 `CLAUDE_CODE_SUBAGENT_MODEL` 設定為 `inherit` 以外的任何值時，Claude Code 從該環境變數為每個隊友選擇模型，否則從主管的目前模型選擇。需要 Claude Code v2.1.257 或更新版本。 在 v2.1.251 之前，`CLAUDE_CODE_SUBAGENT_MODEL` 在此順序中排在第一位。 `teammateDefaultModel` 在 v2.1.234 中被移除；Claude Code 忽略任何遺留值。改為在您的提示中命名模型。 Claude Code 根據您組織的 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 允許清單檢查為隊友選擇的模型。當允許清單阻止某個值時，Claude Code 會替換另一個模型：

- **家族別名，例如`opus`** ：在 Anthropic API 和 AWS 上的 Claude Platform 上，Claude Code 在允許清單允許的該家族的最新版本上運行隊友。在具有提供者特定模型 ID 的提供者上，其中[替換不運行](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)，被阻止的別名會根據下一個項目符號像任何其他被阻止的值一樣回退
- **任何其他被阻止的值，包括提供者特定模型 ID 提供者上的家族別名，或其家族沒有允許版本的別名** ：Claude Code 在主管的模型上運行隊友。如果您設定 `CLAUDE_CODE_SUBAGENT_MODEL`，Claude Code 會先嘗試該模型，遵循相同的規則

隊友繼承主管的[努力程度](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。在分割窗格模式中，這從 v2.1.186 開始適用；較早的版本未將主管的工作階段努力傳遞給分割窗格隊友。

### 讓隊友在實施前進行計畫

對於複雜或有風險的任務，您可以讓隊友在實施前進行計畫。當主管在 [plan mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 中時，Claude 生成的隊友在唯讀計畫模式下工作，直到其計畫準備好。首先將主管切換到計畫模式，然後要求隊友：

```
Spawn an architect teammate to refactor the authentication module.

```

當隊友完成計畫時，它向主管發送計畫批准請求。Claude Code 在主管的工作階段中批准計畫，一旦請求到達，無需主管審查。隊友的編輯和命令仍然會通過[權限](https://code.claude.com/docs/zh-TW/agent-teams#permissions)中描述的權限提示。一旦批准，隊友退出計畫模式並開始實施。

### 直接與隊友交談

每個隊友都是一個完整、獨立的 Claude Code 工作階段。您可以直接向任何隊友傳送訊息，以提供額外指示、提出後續問題或重新定向其方法。

- **In-process 模式** ：使用上下箭頭鍵在 agent 面板中選擇隊友，然後按 Enter 鍵查看其工作階段並輸入以傳送訊息。在選定的隊友上按 `x` 以停止它。按 Ctrl+T 切換任務列表。
- **Split-pane 模式** ：點擊隊友的窗格以直接與其工作階段互動。每個隊友都有自己終端的完整檢視。

當您正在查看 in-process 隊友時，純文字和 [skills](https://code.claude.com/docs/zh-TW/skills) 會傳送給該隊友，但內建命令仍在主管的工作階段中運行。 隊友的模型和快速模式在它生成時是固定的，因此 `/model` 和 `/fast` 只會變更主管的設定。自 v2.1.199 起，在查看隊友時輸入任一命令會顯示通知，表示變更適用於主管；較早的版本會將其應用於主管而不提示。`/effort` 仍適用於所查看隊友的後續回合，因為隊友遵循主管的[努力程度](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。

### 分配和認領任務

共享任務列表協調整個團隊的工作。主管建立任務，隊友完成它們。任務有三種狀態：待處理、進行中和已完成。任務也可以依賴其他任務：具有未解決依賴關係的待處理任務在這些依賴關係完成之前無法被認領。 [沒有 Task 工具](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability)的 Agents 改為透過訊息而非共享任務列表進行協調。 主管可以明確分配任務，或隊友可以自行認領：

- **主管分配** ：告訴主管將哪個任務分配給哪個隊友
- **自行認領** ：完成任務後，隊友自行選擇下一個未分配、未阻止的任務

任務認領使用檔案鎖定來防止多個隊友同時嘗試認領同一任務時的競爭條件。

### 關閉隊友

若要優雅地結束隊友的工作階段，請按名稱引用它。例如，使用名為 researcher 的隊友：

```
Ask the researcher teammate to shut down

```

主管發送關閉請求。隊友可以批准並優雅地退出，或拒絕並提供解釋。 團隊的共享目錄在工作階段結束時會自動清理，因此沒有單獨的清理步驟。請參閱[架構](https://code.claude.com/docs/zh-TW/agent-teams#architecture)以了解哪些目錄被移除以及哪些目錄為已恢復的工作階段保留。

### 使用 hooks 強制執行品質閘門

使用 [hooks](https://code.claude.com/docs/zh-TW/hooks) 在隊友完成工作或任務建立或完成時強制執行規則：

- [`TeammateIdle`](https://code.claude.com/docs/zh-TW/hooks#teammateidle)：當隊友即將閒置時運行。以代碼 2 退出以發送反饋並保持隊友工作。
- [`TaskCreated`](https://code.claude.com/docs/zh-TW/hooks#taskcreated)：當任務正在建立時運行。以代碼 2 退出以防止建立並發送反饋。
- [`TaskCompleted`](https://code.claude.com/docs/zh-TW/hooks#taskcompleted)：當任務被標記為完成時運行。以代碼 2 退出以防止完成並發送反饋。

## Agent teams 如何工作

本節涵蓋 agent teams 背後的架構和機制。如果您想開始使用它們，請參閱上面的[控制您的 agent team](https://code.claude.com/docs/zh-TW/agent-teams#control-your-agent-team)。

### Claude 如何啟動 agent teams

若要啟動一個團隊，請向 Claude 要求隊友。當 Claude 在啟用 agent teams 時呼叫 [Agent tool](https://code.claude.com/docs/zh-TW/tools-reference) 並帶有 [`name`](https://code.claude.com/docs/zh-TW/sub-agents#subagent-names) 時，Claude 會啟動一個隊友，除非該呼叫是[分支](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)或在呼叫本身上傳遞 `isolation`。Claude Code 不會要求您確認啟動。 Claude 也會自行命名普通 subagents，以便稍後可以向它們傳送訊息。這些呼叫遵循相同的規則，因此即使您沒有要求，團隊也可能形成。如果您想要 subagents，請[關閉 agent teams](https://code.claude.com/docs/zh-TW/agent-teams#claude-spawns-teammates-instead-of-subagents)。

### 架構

Agent team 由以下部分組成：

| 元件                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 角色                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| **Team lead**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 生成隊友並協調工作的主要 Claude Code 工作階段 |
| **Teammates**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 各自處理分配任務的獨立 Claude Code 實例       |
| **Task list**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 隊友認領和完成的共享工作項目列表              |
| **Mailbox**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 代理之間通訊的訊息系統                        |
| 每個代理的 mailbox 是位於 `~/.claude/teams/{team-name}/inboxes/{agent-name}.json` 的 JSON 檔案。Claude Code 在讀取 mailbox 檔案時驗證每個條目。不符合訊息格式的條目會被報告為錯誤並從檔案中移除；有效的訊息仍會被傳遞。在 v2.1.207 之前，單個格式錯誤的 mailbox 條目會導致每秒重複出現錯誤，並阻止該 mailbox 的傳遞，直到您手動刪除檔案。 Claude Code 只在寫入收件人 mailbox 檔案成功時才報告訊息已發送，無論訊息是純文字還是結構化協議訊息（例如計畫批准或關閉請求）。當寫入失敗時（例如因為磁碟已滿或 mailbox 目錄不可寫），發送代理會收到錯誤，且不會發送任何內容。請參閱[無法寫入隊友的收件匣](https://code.claude.com/docs/zh-TW/errors#failed-to-write-to-a-teammate-inbox)以了解錯誤訊息和復原步驟。 Claude Code 自動管理任務依賴關係：當隊友完成其他任務依賴的任務時，被阻止的任務會自動解除阻止，無需您採取任何行動。 團隊和任務存儲在本地，名稱來自工作階段衍生的名稱。名稱是 `session-` 後跟工作階段 ID 的前八個字元： |                                               |

- **Team config** ：`~/.claude/teams/{team-name}/config.json`
- **Task list** ：`~/.claude/tasks/{team-name}/`

Claude Code 在工作階段啟動時自動生成這兩者，並在隊友加入、閒置或離開時更新它們。團隊配置目錄在工作階段結束時被移除。任務列表目錄在本地保留，永遠不會上傳，因此恢復的工作階段會保留其任務。保留期由您已經控制的相同 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 管理，用於工作階段記錄，遵循[保留掃描規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)。 團隊配置保存運行時狀態，例如工作階段 ID 和 tmux 窗格 ID，因此不要手動編輯或預先編寫它：您的變更會在下次狀態更新時被覆蓋。 若要定義可重複使用的隊友角色，請改用 [subagent 定義](https://code.claude.com/docs/zh-TW/agent-teams#use-subagent-definitions-for-teammates)。 團隊配置包含一個 `members` 陣列，其中包含每個成員的名稱和代理 ID。主管的條目始終帶有代理類型 `team-lead`。隊友的條目帶有主管在生成它時命名的任何代理類型，無論是[內建類型](https://code.claude.com/docs/zh-TW/sub-agents#built-in-subagents)還是 [subagent 定義](https://code.claude.com/docs/zh-TW/agent-teams#use-subagent-definitions-for-teammates)，當主管未命名任何類型時則省略該欄位。隊友可以讀取此檔案以發現其他團隊成員。 沒有專案級別的團隊配置等效項。您專案目錄中的 `.claude/teams/teams.json` 之類的檔案不被識別為配置；Claude 將其視為普通檔案。

### 為隊友使用 subagent 定義

在任一顯示模式中生成隊友時，您可以參考來自專案、使用者或受管 [subagent 範圍](https://code.claude.com/docs/zh-TW/sub-agents#choose-the-subagent-scope)的 [subagent](https://code.claude.com/docs/zh-TW/sub-agents) 類型。這讓您定義一個角色一次，例如安全審查者或測試執行者，並將其同時重複使用為委派的 subagent 和 agent team 隊友。 若要使用 subagent 定義，在要求 Claude 生成隊友時按名稱提及它：

```
Spawn a teammate using the security-reviewer agent type to audit the auth module.

```

Claude Code 讀取您命名的 subagent 定義，並將其以下部分應用於隊友。當某個部分取決於隊友的[顯示模式](https://code.claude.com/docs/zh-TW/agent-teams#choose-a-display-mode)時，該條目會說明：

- **`tools`**：Claude Code 將隊友限制為定義的`tools` 列表中的工具。對於進程內隊友，Claude Code 會將 `SendMessage` 添加到該列表，在[具有 Task tools 的工作階段](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability)中，它還會添加 `TaskCreate`、`TaskGet`、`TaskList` 和 `TaskUpdate`。
- **`model`**：當您的生成提示未命名模型時，Claude Code 在任一顯示模式中使用定義的`model` 。請參閱[Claude Code 如何選擇隊友的模型](https://code.claude.com/docs/zh-TW/agent-teams#specify-teammates-and-models)。
- **Body** ：對於進程內隊友，Claude Code 將定義的 body 附加到其預設系統提示中作為額外指示。對於分割窗格隊友，Claude Code 使用 body 代替其預設系統提示。
- **`skills`**：Claude Code 在任一顯示模式中都不會將定義的`skills` 應用於隊友。隊友從您的專案和使用者設定中載入 skills。
- **`mcpServers`**：對於分割窗格隊友，Claude Code 在[該欄位的規則](https://code.claude.com/docs/zh-TW/sub-agents#scope-mcp-servers-to-a-subagent)下應用定義的 `mcpServers`，這些規則涵蓋使用 `--agent` 啟動的工作階段。進程內隊友忽略該欄位，並從您的專案和使用者設定中載入 MCP servers。

當 Claude 向不再運行的進程內隊友傳送訊息時，Claude Code 會在同一工作階段中將其恢復，復原為其保存的任何對話，並將訊息作為其下一個提示給予它。在您恢復工作階段後，隊友不會以這種方式被恢復，根據[恢復限制](https://code.claude.com/docs/zh-TW/agent-teams#limitations)。 對於它恢復的隊友，Claude Code 只有在您[信任代理檔案所在的資料夾](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)時，才會重新應用來自專案的 `.claude/agents/` 目錄或 `--add-dir` 目錄的定義。信任父資料夾不算。在那之前，隊友會恢復時不帶定義的任何工具或指示，只保留 Claude Code 添加到每個進程內隊友的工具。請參閱[隊友的代理定義未被復原](https://code.claude.com/docs/zh-TW/errors#teammate-agent-definition-not-restored)以了解通知文本。

### 權限

隊友開始時具有主管的權限模式，除了 [`dontAsk` 模式](https://code.claude.com/docs/zh-TW/permission-modes#allow-only-pre-approved-tools-with-dontask-mode)，他們不會繼承。如果主管使用 `--dangerously-skip-permissions` 運行，所有隊友也會這樣做。生成後，您可以更改個別隊友的權限模式，但在生成時無法設定每個隊友的權限模式。 隊友權限提示會出現在主管工作階段中，因此請在那裡自己批准它們。[Plan approval](https://code.claude.com/docs/zh-TW/agent-teams#have-teammates-plan-before-implementing) 是設計的例外：主管工作階段會授予隊友 plan approvals，無需向您發出單獨的提示。

#### 代理之間的訊息

當一個代理透過 `SendMessage` 向另一個代理發送訊息時，Claude Code 會告訴接收代理該訊息來自另一個 Claude 工作階段，而不是來自您。隊友無法批准權限提示或代表您提供同意，被拒絕某項操作的隊友無法將其轉發給另一個隊友以繞過檢查。相同的規則適用於來自[您其他 Claude Code 工作階段](https://code.claude.com/docs/zh-TW/cross-session-messaging#how-a-session-treats-an-incoming-message)的訊息，完全在團隊之外。 在 [auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 中，分類器對代理之間的訊息應用兩項檢查：

- 它將從另一個代理轉發的批准聲明視為不受信任的輸入，而不是來自您的確認。
- 它在 Claude Code 傳遞訊息之前審查每條訊息，無論是純訊息還是結構化協議訊息（例如關閉請求或計畫批准回應）。它阻止的訊息永遠不會到達收件人。

### Context 和通訊

每個隊友都有自己的 context window。生成時，隊友載入與常規工作階段相同的專案 context：CLAUDE.md、MCP servers 和 skills。它還接收來自主管的生成提示。主管的對話歷史不會延續。 **隊友如何分享資訊：**

- **自動訊息傳遞** ：當隊友發送訊息時，它們會自動傳遞給收件人。主管不需要輪詢更新。
- **閒置通知** ：當隊友完成並停止時，它會自動通知主管並在通知中包含其最終答案。隊友的回合因 API 錯誤而結束時會通知主管它失敗並包含錯誤文本。
- **共享任務列表** ：[具有 Task tools 的代理](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability)可以看到任務狀態並認領可用工作。
- **隊友訊息傳遞** ：按名稱向一個特定隊友發送訊息。若要聯繫所有人，請為每個收件人發送一條訊息。

主管在生成隊友時為其分配名稱，任何隊友都可以按該名稱向任何其他隊友傳送訊息。若要獲得可在稍後提示中參考的可預測名稱，請在您的生成指示中告訴主管如何稱呼每個隊友。

### Token 使用

Agent teams 使用的 tokens 遠多於單個工作階段。每個隊友都有自己的 context window，token 使用量隨活躍隊友數量而增加。對於研究、審查和新功能工作，額外的 tokens 通常是值得的。對於日常任務，單個工作階段更具成本效益。請參閱 [agent team token 成本](https://code.claude.com/docs/zh-TW/costs#agent-team-token-costs)以了解使用指南。 進程內隊友的請求落在主對話的 [cache TTL bucket](https://code.claude.com/docs/zh-TW/prompt-caching#which-ttl-each-request-gets) 之外，因此其快取在 Claude 訂閱上預設保留五分鐘。若要將其保留一小時，請將 [`subagentPromptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#subagentpromptcachettl) 設定為 `1h`。API 以更高的費率計費 1 小時快取寫入。

## 使用案例範例

這些範例展示了 agent teams 如何處理並行探索增加價值的任務。

### 運行並行程式碼審查

單個審查者傾向於一次專注於一種類型的問題。將審查標準分成獨立領域意味著安全性、效能和測試覆蓋都同時獲得徹底的關注。提示為每個隊友分配一個不同的視角，以便他們不重疊：

```
Spawn three teammates to review PR #142:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.

```

每個審查者從相同的 PR 工作，但應用不同的篩選器。主管在他們完成後綜合所有三個的發現。

### 使用競爭假設進行調查

當根本原因不清楚時，單個代理傾向於找到一個看似合理的解釋並停止尋找。提示透過使隊友明確對抗來對抗這一點：每個隊友的工作不僅是調查自己的理論，還要質疑其他隊友的理論。

```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.

```

辯論結構是這裡的關鍵機制。順序調查受到錨定的影響：一旦探索了一個理論，後續調查就會偏向於它。 有多個獨立調查人員積極嘗試相互反駁，倖存的理論更有可能是實際的根本原因。

## 最佳實踐

### 給隊友足夠的 context

隊友自動載入專案 context，包括 CLAUDE.md、MCP servers 和 skills，但他們不繼承主管的對話歷史。請參閱[Context 和通訊](https://code.claude.com/docs/zh-TW/agent-teams#context-and-communication)以了解詳情。在生成提示中包含任務特定的詳情：

```
Spawn a security reviewer teammate with the prompt: "Review the authentication module
at src/auth/ for security vulnerabilities. Focus on token handling, session
management, and input validation. The app uses JWT tokens stored in
httpOnly cookies. Report any issues with severity ratings."

```

### 選擇適當的團隊規模

隊友數量沒有硬性限制，但實際限制適用：

- **Token 成本線性增加** ：每個隊友都有自己的 context window 並獨立消耗 tokens。請參閱 [agent team token 成本](https://code.claude.com/docs/zh-TW/costs#agent-team-token-costs)以了解詳情。
- **協調開銷增加** ：更多隊友意味著更多通訊、任務協調和潛在衝突
- **收益遞減** ：超過一定點後，額外的隊友不會按比例加快工作

對於大多數工作流程，從 3-5 個隊友開始。這平衡了並行工作與可管理的協調。如果您有 15 個獨立任務，3 個隊友是一個很好的起點。 只有當工作真正受益於隊友同時工作時才擴展。三個專注的隊友通常優於五個分散的隊友。

### 適當調整任務大小

- **太小** ：協調開銷超過收益
- **太大** ：隊友工作時間過長而沒有檢查點，增加浪費努力的風險
- **恰到好處** ：自包含的單位，產生清晰的可交付成果，例如函數、測試檔案或審查

主管將工作分解為任務並自動分配給隊友。如果它沒有建立足夠的任務，要求它將工作分成更小的部分。每個隊友有 5-6 個任務可以保持每個人的生產力，並讓主管在有人卡住時重新分配工作。

### 等待隊友完成

有時主管開始自己實施任務，而不是等待隊友。如果您注意到這一點：

```
Wait for your teammates to complete their tasks before proceeding

```

### 從研究和審查開始

如果您是 agent teams 的新手，請從具有清晰邊界且不需要編寫程式碼的任務開始：審查 PR、研究庫或調查錯誤。這些任務展示了並行探索的價值，而不會帶來並行實施所帶來的協調挑戰。

### 避免檔案衝突

兩個隊友編輯同一檔案會導致覆蓋。分解工作，使每個隊友擁有不同的檔案集。

### 監控和引導

檢查隊友的進度，重新定向不起作用的方法，並在發現時綜合發現。讓團隊無人值守運行太長時間會增加浪費努力的風險。

## 故障排除

### 隊友未出現

如果在您要求 Claude 建立隊友後隊友未出現：

- 在 in-process 模式中，隊友會出現在提示輸入下方的代理面板中。使用上下箭頭鍵選擇一個，然後按 Enter 鍵查看它。
- 閒置後消失的隊友列已被隱藏，而非停止。閒置列在整個面板閒置 30 秒後隱藏，並在隊友的下一輪時重新出現。當超過三個隊友閒置時，其多餘列會摺疊成單一的 `N idle agents` 列，按 Enter 鍵可展開。按名稱向隊友發送訊息以將隱藏列恢復。
- 檢查您給 Claude 的任務是否足夠複雜以保證建立團隊。Claude 根據任務決定是否生成隊友。
- 如果您明確要求分割窗格，請確保 tmux 已安裝並在您的 PATH 中可用：

```
which tmux

```

- 對於 iTerm2，驗證 `it2` CLI 已安裝且 Python API 在 iTerm2 偏好設定中啟用。

### Claude 生成隊友而非子代理

當代理團隊啟用時，Claude 在主管工作階段中命名的子代理會作為隊友啟動。Claude [可以自行命名子代理](https://code.claude.com/docs/zh-TW/agent-teams#how-claude-starts-agent-teams)，因此這可能在您從未將其視為團隊工作的委派期間發生。 若要讓命名的子代理再次作為子代理啟動，請將 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 設定為 `0` 以關閉代理團隊： settings.json

```
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "0"
  }
}

```

您不需要啟動新工作階段：Claude Code 在您儲存時會將設定檔 `env` 值重新套用到執行中的工作階段，並在 Claude 每次生成子代理時重新讀取該變數，因此 Claude 命名的下一個子代理會作為子代理啟動。 在您的使用者 `settings.json` 中將變數設定為 `0` 會覆蓋 shell 匯出。其他設定來源仍可啟用代理團隊：

- **更高優先順序的設定檔** ：專案設定、本機設定和 `--settings` 承載會在使用者設定之後套用，因此任何其中設定變數為 `1` 的 `env` 項目會獲勝。請參閱 [設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)。
- **受管設定** ：[受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings) 會在所有其他來源之後套用。如果您的組織在該處啟用代理團隊，請要求您的管理員變更受管值。

變更後，Claude 可能仍會命名子代理，且該名稱會繼續作為 [`SendMessage` 位址](https://code.claude.com/docs/zh-TW/sub-agents#resume-subagents)運作。Claude 會在每個子代理完成時接收其結果。

### 過多權限提示

隊友權限請求冒泡到主管，這可能會造成摩擦。在生成隊友之前在 [permission settings](https://code.claude.com/docs/zh-TW/permissions) 中預批准常見操作以減少中斷。

### 代理提前停止

隊友可能在遇到錯誤後停止，而不是恢復。通過在 in-process 模式中選擇代理面板中的隊友並按 Enter 鍵，或在分割模式中點擊窗格來檢查其輸出，然後：

- 直接給他們額外的指示
- 生成替換隊友以繼續工作

來自主管或另一隊友的訊息會喚醒正在等待重試失敗 API 請求的 in-process 隊友，因此它會立即重試，而不是等待完整的重試延遲。 主管也可能提前停止，在所有任務實際完成之前決定團隊已完成。如果發生這種情況，告訴它繼續。

### 孤立的 tmux 工作階段

如果 tmux 工作階段在 Claude Code 工作階段結束後仍然存在，它可能未被完全清理。列出工作階段並殺死由團隊建立的工作階段：

```
tmux ls
tmux kill-session -t <session-name>

```

## 限制

Agent teams 是實驗性的。要注意的目前限制：

- **沒有 in-process 隊友的工作階段恢復** ：`/resume` 和 `/rewind` 不會恢復 in-process 隊友。恢復工作階段後，主管可能會嘗試向不再存在的隊友傳送訊息。如果發生這種情況，告訴主管生成新隊友。
- **任務狀態可能滯後** ：隊友有時無法將任務標記為已完成，這會阻止依賴任務。如果任務似乎卡住，請檢查工作是否實際完成並手動更新任務狀態或告訴主管推動隊友。
- **關閉可能很慢** ：隊友在關閉前完成其目前請求或工具呼叫，這可能需要時間。
- **每個工作階段一個團隊** ：一個工作階段恰好有一個團隊，範圍限於該工作階段。您無法建立其他具名團隊或在工作階段之間共享團隊。
- **沒有嵌套團隊** ：隊友無法生成自己的隊友。只有主管可以管理團隊。
- **沒有來自 in-process 隊友的背景子代理** ：in-process 隊友自己的子代理在前景中執行，因為隊友的背景工作無法超越主管的程序。Claude Code 在隊友生成定義設定 `background: true` 的子代理時會傳回錯誤。隊友的 `run_in_background: true` 請求也會失敗，可能傳回錯誤或在前景中無聲執行，如 [Claude Code 如何選擇前景或背景](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background) 中所述。從主要對話啟動的子代理遵循[背景預設](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)。
- **主管是固定的** ：主要工作階段在其生命週期內是主管。您無法將隊友提升為主管或轉移領導權。
- **權限在生成時設定** ：隊友開始時具有 [權限](https://code.claude.com/docs/zh-TW/agent-teams#permissions) 下所述的權限模式。您可以在生成後更改個別隊友的權限模式，但在生成時無法設定每個隊友的權限模式。
- **分割窗格需要 tmux 或 iTerm2** ：預設 in-process 模式在任何終端中工作。VS Code 的整合終端、Windows Terminal 或 Ghostty 不支援分割窗格模式。

## 後續步驟

探索並行工作和委派的相關方法：

- **輕量級委派** ：[subagents](https://code.claude.com/docs/zh-TW/sub-agents) 在您的工作階段內為研究或驗證生成幫助代理，更適合不需要代理間協調的任務
- **您自己的工作階段之間的訊息傳遞** ：[cross-session messaging](https://code.claude.com/docs/zh-TW/cross-session-messaging) 讓 Claude 在您自己運行的工作階段之間傳遞發現結果
- **手動並行工作階段** ：[Git worktrees](https://code.claude.com/docs/zh-TW/worktrees) 讓您自己運行多個 Claude Code 工作階段，無需自動化團隊協調

是否 助手