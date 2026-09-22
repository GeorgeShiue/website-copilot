Claude Code 支援可自訂的鍵盤快捷鍵。執行 `/keybindings` 以在 `~/.claude/keybindings.json` 建立或開啟您的配置檔案。

## 配置檔案

快捷鍵配置檔案是一個包含 `bindings` 陣列的物件。每個區塊指定一個上下文和一個按鍵組合到動作的對應。 快捷鍵檔案的變更會自動偵測並套用，無需重新啟動 Claude Code。

| 欄位                                                                        | 說明                                       |
| --------------------------------------------------------------------------- | ------------------------------------------ |
| `$schema`                                                                   | 選用的 JSON Schema URL，用於編輯器自動完成 |
| `$docs`                                                                     | 選用的文件 URL                             |
| `bindings`                                                                  | 按上下文分組的繫結區塊陣列                 |
| 此範例在聊天上下文中將 `Ctrl+E` 繫結到開啟外部編輯器，並取消繫結 `Ctrl+U`： |                                            |

```
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "$docs": "https://code.claude.com/docs/zh-TW/keybindings",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "ctrl+u": null
      }
    }
  ]
}

```

## 上下文

每個繫結區塊指定一個**上下文** ，其中快捷鍵適用：

| 上下文                                                                         | 說明                                                                             |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `Global`                                                                       | 在應用程式的任何地方適用                                                         |
| `Chat`                                                                         | 主聊天輸入區域                                                                   |
| `Autocomplete`                                                                 | 自動完成選單已開啟                                                               |
| `Settings`                                                                     | 設定選單                                                                         |
| `Confirmation`                                                                 | 權限和確認對話框                                                                 |
| `Tabs`                                                                         | 標籤導覽元件                                                                     |
| `Help`                                                                         | 說明選單可見                                                                     |
| `Transcript`                                                                   | 文字記錄檢視器                                                                   |
| `HistorySearch`                                                                | 歷史記錄搜尋模式 (Ctrl+R)                                                        |
| `Task`                                                                         | 背景工作正在執行                                                                 |
| `ThemePicker`                                                                  | 主題選擇器對話框                                                                 |
| `Attachments`                                                                  | 影像附件導覽在選擇對話框中                                                       |
| `Footer`                                                                       | 頁尾指示器導覽（工作、團隊、差異、成品）                                         |
| `MessageSelector`                                                              | 回溯和摘要對話框訊息選擇                                                         |
| `DiffDialog`                                                                   | 差異檢視器導覽                                                                   |
| `DiffPanel`                                                                    | [差異面板](https://code.claude.com/docs/zh-TW/interactive-mode#diff-panel)已開啟 |
| `ModelPicker`                                                                  | 模型選擇器努力程度                                                               |
| `EffortSlider`                                                                 | 由 `/effort` 開啟的努力程度滑桿                                                  |
| `Select`                                                                       | 通用選擇/清單元件                                                                |
| `Plugin`                                                                       | Plugin 對話框（瀏覽、探索、管理）                                                |
| `Agents`                                                                       | [Agent 檢視](https://code.claude.com/docs/zh-TW/agent-view)（`claude agents`）   |
| `Scroll`                                                                       | 對話滾動和全螢幕模式中的文字選擇                                                 |
| 在 v2.1.205 之前，`/doctor` 診斷螢幕存在 `Doctor` 上下文和 `doctor:fix` 動作。 |                                                                                  |

## 可用動作

動作遵循 `namespace:action` 格式，例如 `chat:submit` 用於傳送訊息，或 `app:toggleTodos` 用於顯示工作清單。每個上下文都有特定的可用動作。

### 應用程式動作

在 `Global` 上下文中可用的動作：

| 動作                   | 預設值   | 說明                                                                                                      |
| ---------------------- | -------- | --------------------------------------------------------------------------------------------------------- |
| `app:interrupt`        | Ctrl+C   | 取消目前操作                                                                                              |
| `app:exit`             | Ctrl+D   | 結束 Claude Code。在 800ms 內按兩次以確認                                                                 |
| `app:redraw`           | (未繫結) | 強制終端機重新繪製                                                                                        |
| `app:toggleTodos`      | Ctrl+T   | 切換 Claude 工作清單的可見性。這不是 [`/tasks`](https://code.claude.com/docs/zh-TW/commands) 背景工作檢視 |
| `app:toggleTranscript` | Ctrl+O   | 切換詳細文字記錄                                                                                          |

### 歷史記錄動作

用於導覽命令歷史記錄的動作：

| 動作               | 預設值 | 說明               |
| ------------------ | ------ | ------------------ |
| `history:search`   | Ctrl+R | 開啟歷史記錄搜尋   |
| `history:previous` | Up     | 上一個歷史記錄項目 |
| `history:next`     | Down   | 下一個歷史記錄項目 |

### 聊天動作

在 `Chat` 上下文中可用的動作：

| 動作                                                                                    | 預設值                             | 說明                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `chat:cancel`                                                                           | Escape                             | 取消目前輸入                                                                                                                                                                                                                                                                   |
| `chat:clearInput`                                                                       | Ctrl+L                             | 強制進行完整螢幕重新繪製，保留輸入和對話。在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen#clear-the-conversation)中，也清除螢幕                                                                                                                                   |
| `chat:clearScreen`                                                                      | Cmd+K                              | 與 `chat:clearInput` 相同。請參閱[清除對話](https://code.claude.com/docs/zh-TW/fullscreen#clear-the-conversation)以了解 Cmd+K 在 iTerm2 和 Terminal.app 上的行為                                                                                                               |
| `chat:killAgents`                                                                       | Ctrl+X Ctrl+K                      | 停止此工作階段中所有執行中的[背景子代理](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)，並關閉此工作階段其餘部分的[成品自動回覆](https://code.claude.com/docs/zh-TW/artifacts#let-claude-reply-to-comments-on-its-own)              |
| `chat:cycleMode`                                                                        | Shift+Tab\*                        | 循環權限模式                                                                                                                                                                                                                                                                   |
| `chat:modelPicker`                                                                      | Meta+P                             | 開啟模型選擇器                                                                                                                                                                                                                                                                 |
| `chat:fastMode`                                                                         | Meta+O                             | 切換快速模式                                                                                                                                                                                                                                                                   |
| `chat:thinkingToggle`                                                                   | Meta+T                             | 切換延伸思考                                                                                                                                                                                                                                                                   |
| `chat:submit`                                                                           | Enter                              | 提交訊息                                                                                                                                                                                                                                                                       |
| `chat:queueSubmit`                                                                      | Ctrl+X Enter                       | 提交訊息，標記為等待其輪次：當 Claude 正在工作時，Claude Code [將其排隊](https://code.claude.com/docs/zh-TW/interactive-mode#queue-messages-while-claude-works)，永遠不會中斷輪次。與 `chat:submit` 不同，即使自動完成建議被醒目提示，它也會提交草稿。需要 v2.1.247 或更新版本 |
| `chat:newline`                                                                          | Ctrl+J                             | 插入換行符而不提交                                                                                                                                                                                                                                                             |
| `chat:undo`                                                                             | Ctrl+\_, Ctrl+Shift+-              | 復原上一個動作                                                                                                                                                                                                                                                                 |
| `chat:externalEditor`                                                                   | Ctrl+G, Ctrl+X Ctrl+E              | 在外部編輯器中開啟。[代理檢視分派輸入](https://code.claude.com/docs/zh-TW/agent-view#keyboard-shortcuts)也遵循此動作的單鍵擊快捷鍵                                                                                                                                             |
| `chat:stash`                                                                            | Ctrl+S                             | 暫存目前提示                                                                                                                                                                                                                                                                   |
| `chat:imagePaste`                                                                       | Ctrl+V (Windows 和 WSL 上為 Alt+V) | 從剪貼簿貼上影像。在 WSL 上，預設會繫結兩個快捷鍵                                                                                                                                                                                                                              |
| \*在沒有 VT 模式的 Windows 上（Node \<24.2.0/\<22.17.0、Bun \<1.2.23），預設為 Meta+M。 |                                    |                                                                                                                                                                                                                                                                                |

### 自動完成動作

在 `Autocomplete` 上下文中可用的動作：

| 動作                    | 預設值 | 說明       |
| ----------------------- | ------ | ---------- |
| `autocomplete:accept`   | Tab    | 接受建議   |
| `autocomplete:dismiss`  | Escape | 關閉選單   |
| `autocomplete:previous` | Up     | 上一個建議 |
| `autocomplete:next`     | Down   | 下一個建議 |

### 確認動作

在 `Confirmation` 上下文中可用的動作：

| 動作                                                                                                                                                                                                                      | 預設值      | 說明                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `confirm:yes`                                                                                                                                                                                                             | Y, Enter    | 確認動作                                                                                                                                                                                                                             |
| `confirm:no`                                                                                                                                                                                                              | N, Escape   | 拒絕動作                                                                                                                                                                                                                             |
| `confirm:previous`                                                                                                                                                                                                        | Up          | 上一個選項                                                                                                                                                                                                                           |
| `confirm:next`                                                                                                                                                                                                            | Down        | 下一個選項                                                                                                                                                                                                                           |
| `confirm:nextField`                                                                                                                                                                                                       | Tab         | 下一個欄位                                                                                                                                                                                                                           |
| `confirm:previousField`                                                                                                                                                                                                   | (未繫結)    | 上一個欄位                                                                                                                                                                                                                           |
| `confirm:toggle`                                                                                                                                                                                                          | Space       | 切換選擇                                                                                                                                                                                                                             |
| `confirm:cycleMode`                                                                                                                                                                                                       | Shift+Tab\* | 循環權限模式。在檔案權限提示上，關閉開啟的[評論欄位](https://code.claude.com/docs/zh-TW/permissions#add-a-comment-when-you-answer-a-permission-prompt)；沒有開啟的欄位時，選擇允許此工作階段其餘部分動作的選項（當提示提供該選項時） |
| \*在沒有 VT 模式的 Windows 上（Node \<24.2.0/\<22.17.0、Bun \<1.2.23），預設為 Meta+M。 在 v2.1.257 之前，`confirm:toggleExplanation` 動作（預設繫結到 `Ctrl+E`）在 Bash 和 PowerShell 權限提示上顯示模型產生的命令說明。 |             |                                                                                                                                                                                                                                      |

### 權限動作

在 `Confirmation` 上下文中可用於權限對話框的動作：

| 動作                     | 預設值   | 說明                                                                              |
| ------------------------ | -------- | --------------------------------------------------------------------------------- |
| `permission:toggleDebug` | (未繫結) | 切換權限偵錯資訊。v2.1.146 中移除了先前的 Ctrl+D 預設值，因為它與 `app:exit` 衝突 |

### 文字記錄動作

在 `Transcript` 上下文中可用的動作：

| 動作                                                                                                                                               | 預設值            | 說明             |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ---------------- |
| `transcript:toggleShowAll`                                                                                                                         | Ctrl+E            | 切換顯示所有內容 |
| `transcript:exit`                                                                                                                                  | q, Ctrl+C, Escape | 結束文字記錄檢視 |
| `transcript:toggleShowAll` 僅適用於經典渲染器；在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中，文字記錄檢視器不提供顯示全部切換。 |                   |                  |

### 歷史記錄搜尋動作

在 `HistorySearch` 上下文中可用的動作：

| 動作                                                                                                                                                                                                                                                                                                                                                                                                                                     | 預設值      | 說明                               |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ---------------------------------- |
| `historySearch:next`                                                                                                                                                                                                                                                                                                                                                                                                                     | Ctrl+R      | 下一個符合項目                     |
| `historySearch:accept`                                                                                                                                                                                                                                                                                                                                                                                                                   | Escape, Tab | 接受選擇                           |
| `historySearch:cancel`                                                                                                                                                                                                                                                                                                                                                                                                                   | Ctrl+C      | 取消搜尋                           |
| `historySearch:execute`                                                                                                                                                                                                                                                                                                                                                                                                                  | Enter       | 執行選定的命令                     |
| `historySearch:cycleScope`                                                                                                                                                                                                                                                                                                                                                                                                               | Ctrl+S      | 循環範圍：工作階段、專案、任何地方 |
| `historySearch:next`、`historySearch:accept`、`historySearch:cancel` 和 `historySearch:execute` 預設值適用於經典渲染器中的內嵌歷史記錄搜尋，它始終搜尋來自所有專案的提示。`historySearch:cycleScope` 僅在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中生效，其中 `Ctrl+R` 開啟搜尋對話框，`Ctrl+S` 循環其範圍。對話框的其他按鍵是固定的，無法重新繫結：`Enter` 或 `Tab` 將醒目提示的符合項目放在提示輸入中，`Esc` 取消。 |             |                                    |

### 工作動作

在 `Task` 上下文中可用的動作：

| 動作              | 預設值                | 說明                                                     |
| ----------------- | --------------------- | -------------------------------------------------------- |
| `task:background` | Ctrl+B, Ctrl+X Ctrl+B | 背景執行目前工作。Ctrl+X Ctrl+B 快捷鍵避免 tmux 前綴衝突 |

### 主題動作

在 `ThemePicker` 上下文中可用的動作：

| 動作                             | 預設值 | 說明             |
| -------------------------------- | ------ | ---------------- |
| `theme:toggleSyntaxHighlighting` | Ctrl+T | 切換語法醒目提示 |

### 說明動作

在 `Help` 上下文中可用的動作：

| 動作           | 預設值 | 說明         |
| -------------- | ------ | ------------ |
| `help:dismiss` | Escape | 關閉說明選單 |

### Tabs 動作

在 `Tabs` 上下文中可用的動作：

| 動作            | 預設值          | 說明       |
| --------------- | --------------- | ---------- |
| `tabs:next`     | Tab, Right      | 下一個標籤 |
| `tabs:previous` | Shift+Tab, Left | 上一個標籤 |

### 附件動作

在 `Attachments` 上下文中可用的動作：

| 動作                   | 預設值            | 說明           |
| ---------------------- | ----------------- | -------------- |
| `attachments:next`     | Right             | 下一個附件     |
| `attachments:previous` | Left              | 上一個附件     |
| `attachments:remove`   | Backspace, Delete | 移除選定的附件 |
| `attachments:exit`     | Down, Escape      | 結束附件導覽   |

### 頁尾動作

在 `Footer` 上下文中可用的動作：

| 動作                    | 預設值            | 說明                                                                                                                                                       |
| ----------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `footer:next`           | Right             | 下一個頁尾項目                                                                                                                                             |
| `footer:previous`       | Left              | 上一個頁尾項目                                                                                                                                             |
| `footer:up`             | Up                | 在頁尾中向上導覽（在頂部取消選擇）                                                                                                                         |
| `footer:down`           | Down              | 在頁尾中向下導覽                                                                                                                                           |
| `footer:openSelected`   | Enter             | 開啟選定的頁尾項目                                                                                                                                         |
| `footer:clearSelection` | Escape            | 清除頁尾選擇                                                                                                                                               |
| `footer:dismiss`        | Backspace, Delete | 從頁尾關閉選定的[成品](https://code.claude.com/docs/zh-TW/artifacts)連結；已發佈的成品本身不受影響。在其他頁尾列上，這些按鍵無效。需要 v2.1.217 或更新版本 |

### 訊息選擇器動作

在 `MessageSelector` 上下文中可用的動作：

| 動作                     | 預設值                                    | 說明             |
| ------------------------ | ----------------------------------------- | ---------------- |
| `messageSelector:up`     | Up, K, Ctrl+P                             | 在清單中向上移動 |
| `messageSelector:down`   | Down, J, Ctrl+N                           | 在清單中向下移動 |
| `messageSelector:top`    | Ctrl+Up, Shift+Up, Meta+Up, Shift+K       | 跳至頂部         |
| `messageSelector:bottom` | Ctrl+Down, Shift+Down, Meta+Down, Shift+J | 跳至底部         |
| `messageSelector:select` | Enter                                     | 選擇訊息         |

### Diff 動作

在 `DiffDialog` 上下文中可用的動作：

| 動作                                                                                                                                                                                                                                                                                                       | 預設值         | 說明                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------- |
| `diff:dismiss`                                                                                                                                                                                                                                                                                             | Escape         | 關閉差異檢視器；從詳細資訊檢視中，返回檔案清單                                                                 |
| `diff:previousSource`                                                                                                                                                                                                                                                                                      | Left           | 上一個差異來源                                                                                                 |
| `diff:nextSource`                                                                                                                                                                                                                                                                                          | Right          | 下一個差異來源                                                                                                 |
| `diff:previousFile`                                                                                                                                                                                                                                                                                        | Up, K          | 檔案清單中的上一個檔案；在詳細資訊檢視中向上滾動一行                                                           |
| `diff:nextFile`                                                                                                                                                                                                                                                                                            | Down, J        | 檔案清單中的下一個檔案；在詳細資訊檢視中向下滾動一行                                                           |
| `diff:viewDetails`                                                                                                                                                                                                                                                                                         | Enter          | 檢視差異詳細資訊                                                                                               |
| `diff:back`                                                                                                                                                                                                                                                                                                | (未繫結)       | 在差異檢視器中返回。Escape 透過 `diff:dismiss` 執行返回動作。v2.1.203 中移除了詳細資訊檢視中先前的 Left 預設值 |
| 差異詳細資訊檢視也會將分頁器風格的按鍵繫結到標準[滾動動作](https://code.claude.com/docs/zh-TW/keybindings#scroll-actions)。這些繫結是 `DiffDialog` 上下文的一部分，僅適用於詳細資訊檢視；[滾動動作](https://code.claude.com/docs/zh-TW/keybindings#scroll-actions)下列出的 `Scroll` 上下文預設值保持不變。 |                |                                                                                                                |
| 動作                                                                                                                                                                                                                                                                                                       | 預設值         | 說明                                                                                                           |
| ---                                                                                                                                                                                                                                                                                                        | ---            | ---                                                                                                            |
| `scroll:pageUp`                                                                                                                                                                                                                                                                                            | PageUp         | 向上滾動視窗高度的一半                                                                                         |
| `scroll:pageDown`                                                                                                                                                                                                                                                                                          | PageDown       | 向下滾動視窗高度的一半                                                                                         |
| `scroll:fullPageUp`                                                                                                                                                                                                                                                                                        | Shift+Space, B | 向上滾動完整視窗高度                                                                                           |
| `scroll:fullPageDown`                                                                                                                                                                                                                                                                                      | Space          | 向下滾動完整視窗高度                                                                                           |
| `scroll:top`                                                                                                                                                                                                                                                                                               | G, Home        | 跳至頂部                                                                                                       |
| `scroll:bottom`                                                                                                                                                                                                                                                                                            | Shift+G, End   | 跳至底部                                                                                                       |

### Diff 面板動作

用於 `/diff` 在全螢幕渲染中開啟的 [diff 面板](https://code.claude.com/docs/zh-TW/interactive-mode#diff-panel) 的動作。`app:cycleDiffBase` 在 `DiffPanel` 上下文中，在面板開啟時有效；其他的在 `Global` 中。面板需要 Claude Code v2.1.260 或更新版本。

| 動作                        | 預設                 | 說明                                             |
| --------------------------- | -------------------- | ------------------------------------------------ |
| `app:toggleReplTab`         | (未繫結)             | 開啟或關閉 diff 面板，與執行 `/diff` 相同        |
| `app:cycleDiffBase`         | Ctrl+X B             | 循環面板的比較基礎：此工作階段、未提交、然後分支 |
| `app:diffFileListUp`        | Ctrl+Up, Meta+Up     | 當面板的檔案清單溢出時向上滾動                   |
| `app:diffFileListDown`      | Ctrl+Down, Meta+Down | 當面板的檔案清單溢出時向下滾動                   |
| `app:toggleDiffNoiseFilter` | (未繫結)             | 在面板中顯示或隱藏測試和產生的檔案               |
| `app:toggleDiffPreSession`  | (未繫結)             | 展開或摺疊此工作階段之前的變更                   |

### 模型選擇器動作

在 `ModelPicker` 上下文中可用的動作：

| 動作                          | 預設值 | 說明                             |
| ----------------------------- | ------ | -------------------------------- |
| `modelPicker:decreaseEffort`  | Left   | 降低努力程度                     |
| `modelPicker:increaseEffort`  | Right  | 提高努力程度                     |
| `modelPicker:thisSessionOnly` | s      | 將醒目提示的模型套用至此工作階段 |

### 努力滑桿動作

在 `EffortSlider` 上下文中可用的動作，當您執行不帶引數的 `/effort` 時開啟的滑桿。滑桿的 Left、Right、Enter 和 Escape 按鍵無法重新繫結。

| 動作                           | 預設 | 說明                                                                                                                            |
| ------------------------------ | ---- | ------------------------------------------------------------------------------------------------------------------------------- |
| `effortSlider:thisSessionOnly` | s    | 將焦點[努力程度](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)套用至此工作階段。需要 v2.1.257 或更新版本 |

### 選擇動作

在 `Select` 上下文中可用的動作：

| 動作                                                                                                                                                                                                                                             | 預設值          | 說明             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- | ---------------- |
| `select:next`                                                                                                                                                                                                                                    | Down, J, Ctrl+N | 下一個選項       |
| `select:previous`                                                                                                                                                                                                                                | Up, K, Ctrl+P   | 上一個選項       |
| `select:pageUp`                                                                                                                                                                                                                                  | PageUp          | 向上移動一頁選項 |
| `select:pageDown`                                                                                                                                                                                                                                | PageDown        | 向下移動一頁選項 |
| `select:first`                                                                                                                                                                                                                                   | Home            | 第一個選項       |
| `select:last`                                                                                                                                                                                                                                    | End             | 最後一個選項     |
| `select:accept`                                                                                                                                                                                                                                  | Enter           | 接受選擇         |
| `select:cancel`                                                                                                                                                                                                                                  | Escape          | 取消選擇         |
| Claude Code 在 `/skills` 選單中套用您的 `select:pageUp`、`select:pageDown`、`select:first` 和 `select:last` 繫結。在大多數其他清單中，例如 `/model` 選擇器，Claude Code 使用 PageUp 和 PageDown 進行分頁，無論您的繫結如何，並忽略 Home 和 End。 |                 |                  |

### Plugin 動作

在 `Plugin` 上下文中可用的動作：

| 動作              | 預設值 | 說明                                                         |
| ----------------- | ------ | ------------------------------------------------------------ |
| `plugin:toggle`   | Space  | 切換 plugin 選擇                                             |
| `plugin:install`  | I      | 安裝選定的 plugins                                           |
| `plugin:favorite` | F      | 將選定的 plugin 標記為最愛，使其在「已安裝」標籤頂部附近排序 |

### 設定動作

在 `Settings` 上下文中可用的動作。`select:accept` 和 `confirm:no` 動作會從[選擇](https://code.claude.com/docs/zh-TW/keybindings#select-actions)和[確認](https://code.claude.com/docs/zh-TW/keybindings#confirmation-actions)上下文中重複使用，具有設定特定的行為：變更會在您變更時立即套用到每個設定，因此 Escape 會關閉面板並儲存您的變更，而不是拒絕。

| 動作              | 預設值       | 說明                             |
| ----------------- | ------------ | -------------------------------- |
| `settings:search` | /            | 進入搜尋模式                     |
| `settings:retry`  | R            | 重試載入使用量資料（發生錯誤時） |
| `select:accept`   | Enter, Space | 變更選定的設定或開啟其子選單     |
| `confirm:no`      | Escape       | 關閉面板。變更已儲存             |

### 代理動作

在 `Agents` 上下文中可用的動作，適用於[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)，使用 `claude agents` 開啟。需要 v2.1.257 或更新版本。

| 動作                                                                                                                                                                                                                                                                                                                                                                                                                                                | 預設   | 說明                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------- |
| `agents:switchView`                                                                                                                                                                                                                                                                                                                                                                                                                                 | Ctrl+S | 在[工作階段分組](https://code.claude.com/docs/zh-TW/agent-view#organize-the-list)之間切換狀態和目錄 |
| `agents:togglePin`                                                                                                                                                                                                                                                                                                                                                                                                                                  | Ctrl+T | [釘選或取消釘選](https://code.claude.com/docs/zh-TW/agent-view#organize-the-list)選定的工作階段     |
| 當代理檢視開啟時，Claude Code 對 `Agents` 上下文繫結的任何按鍵使用 `Agents` 繫結，並忽略同一按鍵上的 `Chat` 或 `Global` 繫結。例如，在代理檢視中按 Ctrl+S 會切換工作階段分組，而不是觸發預設的 `chat:stash`。 分派輸入的外部編輯器快捷鍵不是 `Agents` 動作。代理檢視遵循 `Chat` 上下文的 `chat:externalEditor` 繫結，預設為 Ctrl+G。 繫結在代理檢視中的單鍵擊上觸發，因此繫結到 `chat:externalEditor` 的 Ctrl+X Ctrl+E 快捷鍵不會在那裡開啟編輯器。 |        |                                                                                                     |

### 語音動作

在啟用[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)時，在 `Chat` 上下文中可用的動作：

| 動作               | 預設值 | 說明                                   |
| ------------------ | ------ | -------------------------------------- |
| `voice:pushToTalk` | Space  | 聽寫提示。根據 `/voice` 模式按住或點選 |

### 滾動動作

在啟用[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)時，在 `Scroll` 上下文中可用的動作：

| 動作                        | 預設值               | 說明                                                                              |
| --------------------------- | -------------------- | --------------------------------------------------------------------------------- |
| `scroll:lineUp`             | `wheelup`            | 向上滾動一行。滑鼠滾輪滾動會觸發此動作                                            |
| `scroll:lineDown`           | `wheeldown`          | 向下滾動一行。滑鼠滾輪滾動會觸發此動作                                            |
| `scroll:pageUp`             | PageUp               | 向上滾動視窗高度的一半                                                            |
| `scroll:pageDown`           | PageDown             | 向下滾動視窗高度的一半                                                            |
| `scroll:top`                | Ctrl+Home            | 跳至對話的開始                                                                    |
| `scroll:bottom`             | Ctrl+End             | 跳至最新訊息並重新啟用自動跟隨                                                    |
| `scroll:halfPageUp`         | (未繫結)             | 向上滾動視窗高度的一半。與 `scroll:pageUp` 相同的行為，為 vi 風格的重新繫結提供   |
| `scroll:halfPageDown`       | (未繫結)             | 向下滾動視窗高度的一半。與 `scroll:pageDown` 相同的行為，為 vi 風格的重新繫結提供 |
| `scroll:fullPageUp`         | (未繫結)             | 向上滾動完整視窗高度                                                              |
| `scroll:fullPageDown`       | (未繫結)             | 向下滾動完整視窗高度                                                              |
| `selection:copy`            | Ctrl+Shift+C / Cmd+C | 將選定的文字複製到剪貼簿                                                          |
| `selection:clear`           | (未繫結)             | 清除有效的文字選擇。需要 v2.1.234 或更新版本                                      |
| `selection:extendLeft`      | Shift+Left           | 將有效選擇向左延伸一欄                                                            |
| `selection:extendRight`     | Shift+Right          | 將有效選擇向右延伸一欄                                                            |
| `selection:extendUp`        | Shift+Up             | 將有效選擇向上延伸一列。當選擇到達頂部邊緣時滾動視窗                              |
| `selection:extendDown`      | Shift+Down           | 將有效選擇向下延伸一列。當選擇到達底部邊緣時滾動視窗                              |
| `selection:extendLineStart` | Shift+Home           | 將有效選擇延伸到行的開始                                                          |
| `selection:extendLineEnd`   | Shift+End            | 將有效選擇延伸到行的結尾                                                          |

## 按鍵組合語法

### 修飾鍵

使用 `+` 分隔符搭配修飾鍵：

- `ctrl` 或 `control` - Control 鍵
- `shift` - Shift 鍵
- `alt`、`opt`、`option` 或 `meta` - Windows 和 Linux 上的 Alt 鍵，macOS 上的 Option 鍵
- `cmd`、`command`、`super` 或 `win` - macOS 上的 Command 鍵，Windows 上的 Windows 鍵，Linux 上的 Super 鍵

`cmd` 群組只在報告 Super 修飾鍵的終端機中被偵測，例如支援 Kitty 鍵盤協議或 xterm 的 `modifyOtherKeys` 模式的終端機。大多數終端機不會發送它，因此對於您想在任何地方都能運作的繫結，請使用 `ctrl` 或 `meta`。 例如：

```
ctrl+k          Ctrl + K
shift+tab       Shift + Tab
meta+p          macOS 上的 Option + P，其他地方為 Alt + P
ctrl+shift+c    多個修飾鍵

```

### 大寫字母

Claude Code 不區分大小寫地解析按鍵名稱，因此 `K` 與 `k` 的繫結相同，`ctrl+K` 與 `ctrl+k` 相同。若要繫結 Shift 和一個字母，請寫 `shift+k`。

### 非美式鍵盤配置

即使您的作用中鍵盤配置輸入其他字元，也請將 Ctrl 快捷鍵的按鍵名稱寫成拉丁字元。 Claude Code 如何將您按下的按鍵與繫結相符取決於配置的類型：

- 在西里爾字母等非拉丁配置下，當終端機使用 Kitty 鍵盤協議並報告該位置時，Claude Code 會根據按鍵的美式配置位置來符合 Ctrl 快捷鍵。在這樣的終端機中，使用俄文配置時，按下 Ctrl 和實體 W 鍵會觸發 `ctrl+w`。在不報告位置的終端機中，Claude Code 會符合終端機為按鍵發送的任何內容：ASCII 控制碼會觸發拉丁快捷鍵，而作為西里爾字元到達的按鍵不符合任何繫結
- 在重新排列拉丁字母的配置下，例如 AZERTY，Claude Code 會符合按鍵輸入的字母，因此按下 Ctrl 和標記為 A 的按鍵會觸發 `ctrl+a`

在 v2.1.247 之前，在使用 Kitty 鍵盤協議的終端機（例如 Ghostty、Kitty、WezTerm 和 iTerm2）中，在非拉丁配置下按下 Ctrl 快捷鍵不會觸發其繫結。

### 和弦

和弦是由空格分隔的按鍵組合序列：

```
ctrl+k ctrl+s   按 Ctrl+K，放開，然後按 Ctrl+S

```

在每個按鍵組合的 3 秒內按下下一個。如果您等待更長時間，Claude Code 會取消和弦並顯示簡短通知。

### 特殊鍵

- `escape` 或 `esc` - Escape 鍵
- `enter` 或 `return` - Enter 鍵
- `tab` - Tab 鍵
- `space` - 空格鍵
- `up`、`down`、`left`、`right` - 方向鍵
- `pageup`、`pagedown` - Page Up 和 Page Down 鍵
- `home`、`end` - Home 和 End 鍵
- `backspace`、`delete` - 刪除鍵
- `wheelup`、`wheeldown` - 滑鼠滾輪捲動事件

## 取消繫結預設快捷鍵

將動作設定為 `null` 以取消繫結預設快捷鍵：

```
{
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+s": null
      }
    }
  ]
}

```

這也適用於和弦繫結。取消繫結共享前綴的每個和弦會釋放該前綴以用作單一鍵繫結。任何作用中的內容中的和弦會保留其前綴的保留狀態，因此您必須在定義該和弦的內容中取消繫結每個和弦。 Claude Code 在 `ctrl+x` 前綴上繫結這些預設和弦：`Chat` 中的 `ctrl+x ctrl+k`、`ctrl+x ctrl+e`、`ctrl+x enter`、`ctrl+x ctrl+a` 和 `ctrl+x tab`，`Task` 中的 `ctrl+x ctrl+b`，以及 `DiffPanel` 中的 `ctrl+x b`。`ctrl+x enter` 和弦需要 v2.1.247 或更新版本，而 `ctrl+x b`、`ctrl+x ctrl+a` 和 `ctrl+x tab` 需要 v2.1.260 或更新版本。若要將 `ctrl+x` 本身回收為單一鍵繫結，請取消繫結所有這些：

```
{
  "bindings": [
    {
      "context": "Task",
      "bindings": {
        "ctrl+x ctrl+b": null
      }
    },
    {
      "context": "DiffPanel",
      "bindings": {
        "ctrl+x b": null
      }
    },
    {
      "context": "Chat",
      "bindings": {
        "ctrl+x ctrl+k": null,
        "ctrl+x ctrl+e": null,
        "ctrl+x enter": null,
        "ctrl+x ctrl+a": null,
        "ctrl+x tab": null,
        "ctrl+x": "chat:newline"
      }
    }
  ]
}

```

如果您取消繫結前綴上的某些但不是全部和弦，按下前綴仍會進入和弦等待模式以進行剩餘的繫結。

## 保留的快捷鍵

這些快捷鍵無法重新繫結：

| 快捷鍵    | 原因                                                                                                                                                                                                                                                                         |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ctrl+C    | 硬編碼的中斷/取消                                                                                                                                                                                                                                                            |
| Ctrl+D    | 硬編碼的結束                                                                                                                                                                                                                                                                 |
| Ctrl+M    | Claude Code 始終將其接收為 Enter                                                                                                                                                                                                                                             |
| Ctrl+\[   | Claude Code 始終將其接收為 Escape。在使用 Kitty 鍵盤協議的終端機中，這需要 v2.1.242 或更新版本                                                                                                                                                                               |
| Ctrl+I    | Claude Code 始終將其接收為 Tab                                                                                                                                                                                                                                               |
| Ctrl+H    | 傳送 ASCII 退格位元組。[Claude Code 在 Windows 上如何讀取它](https://code.claude.com/docs/zh-TW/terminal-config#fix-backspace-deleting-a-whole-word-on-windows)取決於您的終端機和 [`CLAUDE_CODE_BS_AS_CTRL_BACKSPACE`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數 |
| Caps Lock | 未傳遞至終端機應用程式                                                                                                                                                                                                                                                       |

## 終端機衝突

某些快捷鍵可能與終端機多工器衝突：

| 快捷鍵 | 衝突                      |
| ------ | ------------------------- |
| Ctrl+B | tmux 前綴（按兩次以傳送） |
| Ctrl+A | GNU screen 前綴           |
| Ctrl+Z | Unix 程序暫停 (SIGTSTP)   |

## Vim 模式互動

啟用 vim 模式時（透過 `/config` → 編輯器模式），快捷鍵和 vim 模式獨立運作：

- **Vim 模式** 在文字輸入層級處理輸入（游標移動、模式、動作）
- **快捷鍵** 在元件層級處理動作（切換待辦事項、提交等）
- vim 模式中的 Escape 鍵從 INSERT 切換到 NORMAL 模式；它不會觸發 `chat:cancel`
- 大多數 Ctrl+鍵快捷鍵通過 vim 模式傳遞到快捷鍵系統
- Vim 鍵無法透過快捷鍵檔案重新對應。若要對應兩鍵 INSERT 模式序列（例如 `jj`）至 Escape，請使用 [`vimInsertModeRemaps`](https://code.claude.com/docs/zh-TW/interactive-mode#remap-insert-mode-key-sequences) 設定
- 在 vim NORMAL 模式中，`?` 顯示說明選單（vim 行為）
- 在 vim NORMAL 模式中，`/` 開啟歷史搜尋，與標準模式中的 Ctrl+R 相同

## 驗證

Claude Code 驗證您的快捷鍵並顯示以下警告：

- 解析錯誤（無效的 JSON 或結構）
- 無效的上下文名稱
- 無效的動作值，例如不是字串或 `null` 的動作
- 未知的動作名稱，例如已註冊動作的拼寫錯誤。Claude Code 會跳過該繫結並保持該按鍵的任何預設繫結有效。在 v2.1.246 之前，具有未知動作名稱的繫結會無聲地停用該按鍵
- 保留快捷鍵衝突
- 同一上下文中的重複繫結

Claude Code 在檔案載入時報告警告，並將每個警告寫入偵錯日誌。使用 [`--debug`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 啟動 Claude Code 以查看詳細資訊。 是否 助手
