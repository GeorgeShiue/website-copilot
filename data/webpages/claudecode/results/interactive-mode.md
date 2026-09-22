## 快捷鍵

快捷鍵可能因平台和終端而異。在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中，在文字記錄檢視器中按 `?` 以查看可用的快捷鍵。**macOS 使用者** ：Option/Alt 鍵快捷鍵（`Alt+B`、`Alt+F`、`Alt+D`、`Alt+Y`、`Alt+P`）需要在您的終端中將 Option 設定為 Meta。請參閱[在 macOS 上啟用 Option 鍵快捷鍵](https://code.claude.com/docs/zh-TW/terminal-config#enable-option-key-shortcuts-on-macos)以了解每個終端中的設定。

### 一般控制

| 快捷鍵                                                                             | 說明                                                                                                                                                                                                                                                                                     | 內容                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Ctrl+C`                                                                           | 中斷或清除輸入                                                                                                                                                                                                                                                                           | 中斷執行中的操作。如果沒有任何操作執行中，第一次按下會清除提示輸入，第二次按下會退出 Claude Code                                                                                                                                                                                                                                                                                                                                                                                  |
| `Ctrl+X Ctrl+K`                                                                    | 停止此工作階段中所有執行中的[背景子代理](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)，並關閉[成品自動回覆](https://code.claude.com/docs/zh-TW/artifacts#let-claude-reply-to-comments-on-its-own)以供其餘工作階段使用。在 3 秒內按兩次以確認 | 子代理控制                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `Ctrl+D`                                                                           | 退出 Claude Code 工作階段                                                                                                                                                                                                                                                                | 第一次按下會顯示確認提示，第二次在 800ms 內按下會退出。當提示有文字時，`Ctrl+D` 會刪除游標後的字元                                                                                                                                                                                                                                                                                                                                                                                |
| `Ctrl+G` 或 `Ctrl+X Ctrl+E`                                                        | 在預設文字編輯器中開啟                                                                                                                                                                                                                                                                   | 在您的預設文字編輯器中編輯您的提示或自訂回應。`Ctrl+X Ctrl+E` 是 readline 原生繫結。在 `/config` 中開啟**在外部編輯器中顯示最後回應** 以在您的提示上方將 Claude 的先前回覆作為 `#` 註解內容前置；Claude Code 會在您儲存時移除註解區塊                                                                                                                                                                                                                                             |
| `Ctrl+L`                                                                           | 重繪或清除螢幕                                                                                                                                                                                                                                                                           | 強制完整終端重繪，保留輸入和對話歷史記錄。如果顯示變得混亂或部分空白，請使用此選項來復原。在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen#clear-the-conversation)中，它也會清除螢幕，您可以向上捲動以查看較早的訊息                                                                                                                                                                                                                                                  |
| `Ctrl+O`                                                                           | 切換文字記錄檢視器                                                                                                                                                                                                                                                                       | 顯示詳細的工具使用情況和執行情況，每個助手訊息上都有時間戳記和使用的模型。也會展開預設摺疊的行，例如 MCP 呼叫，顯示為單一 `Called slack 3 times` 行，以及[來自您其他工作階段的訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#what-a-message-looks-like)，顯示為單行 `Message from @<sender>` 預覽                                                                                                                                                               |
| `Ctrl+R`                                                                           | 反向搜尋命令歷史記錄                                                                                                                                                                                                                                                                     | 以互動方式搜尋先前的命令                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Ctrl+V` 或 `Cmd+V`（iTerm2）或 `Alt+V`（Windows 和 WSL）                          | 從剪貼簿貼上影像                                                                                                                                                                                                                                                                         | 在游標處插入 `[Image #N]` 晶片，以便您可以在提示中按位置參考它。在 WSL 上，`Ctrl+V` 和 `Alt+V` 都已繫結；如果您的終端攔截 `Ctrl+V`，請使用 `Alt+V`                                                                                                                                                                                                                                                                                                                                |
| `Ctrl+B`                                                                           | 背景執行工作                                                                                                                                                                                                                                                                             | 將 Bash 命令和代理放在背景中。Tmux 使用者按兩次                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `Ctrl+T`                                                                           | 切換 Claude 的工作清單                                                                                                                                                                                                                                                                   | 在狀態區域中顯示或隱藏 [Claude 的待辦事項清單](https://code.claude.com/docs/zh-TW/interactive-mode#task-list)。這不是背景工作檢視；使用 [`/tasks`](https://code.claude.com/docs/zh-TW/commands) 以查看執行中的 shell 和子代理                                                                                                                                                                                                                                                     |
| `Ctrl+S`                                                                           | 隱藏或復原提示                                                                                                                                                                                                                                                                           | 輸入中有文字時，隱藏它並清除提示。在空提示上再次按下時，復原隱藏的文字、游標位置和貼上的內容                                                                                                                                                                                                                                                                                                                                                                                      |
| `Ctrl+Z`                                                                           | 暫停 Claude Code                                                                                                                                                                                                                                                                         | 僅限 Unix。將程序暫停到您的 shell；執行 `fg` 以繼續                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `Left/Right arrows`                                                                | 在對話框標籤之間循環                                                                                                                                                                                                                                                                     | 在權限對話框和功能表中的標籤之間導覽                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `Tab`                                                                              | 接受自動完成建議，或在權限答案中新增註解                                                                                                                                                                                                                                                 | 當自動完成建議在提示輸入中顯示時，接受選定的建議。在大多數權限提示上，當**是** 或**否** 獲得焦點時，會在該選項上開啟註解欄位，再次按下會關閉欄位。請參閱[在您回答權限提示時新增註解](https://code.claude.com/docs/zh-TW/permissions#add-a-comment-when-you-answer-a-permission-prompt)                                                                                                                                                                                            |
| `Up/Down arrows` 或 `Ctrl+P`/`Ctrl+N`                                              | 移動游標或導覽命令歷史記錄                                                                                                                                                                                                                                                               | 當輸入跨越多個視覺行時（無論是換行還是多行），首先在提示內移動游標。一旦游標在第一行或最後一行視覺行上，再次按下會導覽命令歷史記錄。當您有訊息排隊時，從第一行按 `Up` 會改為[取回您排隊的內容](https://code.claude.com/docs/zh-TW/interactive-mode#take-back-what-you-queued)                                                                                                                                                                                                     |
| `Esc`                                                                              | 中斷 Claude 或關閉對話框                                                                                                                                                                                                                                                                 | 停止目前的回應或工具呼叫中途，以便您可以重新導向。Claude 會保留迄今為止完成的工作。如果您有[訊息排隊](https://code.claude.com/docs/zh-TW/interactive-mode#queue-messages-while-claude-works)，Claude Code 會在下一步傳送它們。當對話框開啟時，`Esc` 會關閉對話框。在權限提示上，`Esc` 會拒絕該操作，與[**否** （不含註解）](https://code.claude.com/docs/zh-TW/permissions#add-a-comment-when-you-answer-a-permission-prompt)相同                                                 |
| `Esc` + `Esc`                                                                      | 清除輸入草稿或回溯                                                                                                                                                                                                                                                                       | 當提示輸入包含文字時，雙 `Esc` 會清除它並將草稿儲存到歷史記錄，以便 `Up` 可以回憶它。當輸入為空時，雙 `Esc` 會開啟[回溯功能表](https://code.claude.com/docs/zh-TW/checkpointing)以從先前的時間點復原或摘要程式碼和對話                                                                                                                                                                                                                                                            |
| `Shift+Tab` 或 `Alt+M`（當 Node 或 Bun 執行時間未啟用 VT 輸入模式時在 Windows 上） | 循環權限模式                                                                                                                                                                                                                                                                             | 循環通過 `default`（在模式指示器中標記為 Manual）、`acceptEdits`、`plan` 和（如果可用）`bypassPermissions`，然後是 `auto`。從 `auto`，第一次按下會切換到 `default`。請參閱[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。在檔案權限提示上，相同的鍵會關閉開啟的[註解欄位](https://code.claude.com/docs/zh-TW/permissions#add-a-comment-when-you-answer-a-permission-prompt)。沒有開啟欄位時，它會選擇允許該操作以供工作階段其餘部分的選項（當提示提供該選項時） |
| `Option+P`（macOS）或 `Alt+P`（Windows/Linux）                                     | 切換模型                                                                                                                                                                                                                                                                                 | 切換模型而不清除您的提示                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Option+T`（macOS）或 `Alt+T`（Windows/Linux）                                     | 切換延伸思考                                                                                                                                                                                                                                                                             | 啟用或停用延伸思考模式。對 Fable 5.1 或 Fable 5 沒有影響，它們始終使用延伸思考。在 macOS 上無需設定 Option 為 Meta 即可運作                                                                                                                                                                                                                                                                                                                                                       |
| `Option+O`（macOS）或 `Alt+O`（Windows/Linux）                                     | 切換快速模式                                                                                                                                                                                                                                                                             | 啟用或停用[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)                                                                                                                                                                                                                                                                                                                                                                                                                |

### 文字編輯

| 快捷鍵                      | 說明                   | 內容                                                                                                                                                                                                |
| --------------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Ctrl+A`                    | 將游標移至目前行的開始 | 在多行輸入中，移至目前邏輯行的開始                                                                                                                                                                  |
| `Ctrl+E`                    | 將游標移至目前行的結尾 | 在多行輸入中，移至目前邏輯行的結尾                                                                                                                                                                  |
| `Ctrl+K`                    | 刪除到行尾             | 儲存已刪除的文字以供貼上                                                                                                                                                                            |
| `Ctrl+U`                    | 從游標刪除到行開始     | 儲存已刪除的文字以供貼上。重複以清除多行輸入中的行。在 macOS 上，包括 iTerm2 和 Terminal.app 的終端模擬器會將 `Cmd+Backspace` 對應到此快捷鍵                                                        |
| `Ctrl+W`                    | 刪除回到先前的空白     | 儲存已刪除的文字以供貼上。一次按下會移除整個路徑或 `--flag=value`。若要僅刪除先前的單字，請在 macOS 上按 `Option+Delete` 或在 Windows 上按 `Ctrl+Backspace`                                         |
| `Ctrl+Y`                    | 貼上已刪除的文字       | 貼上您最後使用單字或行刪除快捷鍵（例如 `Ctrl+K`、`Ctrl+U` 或 `Ctrl+W`）刪除的文字                                                                                                                   |
| `Alt+Y`（在 `Ctrl+Y` 之後） | 循環貼上歷史記錄       | 貼上後，循環通過先前刪除的文字。在 macOS 上需要[Option 為 Meta](https://code.claude.com/docs/zh-TW/interactive-mode#keyboard-shortcuts)                                                             |
| `Alt+B`                     | 將游標向後移動一個單字 | 單字導覽。在 macOS 上需要[Option 為 Meta](https://code.claude.com/docs/zh-TW/interactive-mode#keyboard-shortcuts)                                                                                   |
| `Alt+F`                     | 將游標向前移動一個單字 | 移至目前單字的結尾，或當游標在單字之間時移至下一個單字的結尾。在 macOS 上需要[Option 為 Meta](https://code.claude.com/docs/zh-TW/interactive-mode#keyboard-shortcuts)                               |
| `Alt+D`                     | 刪除到單字結尾         | 刪除到目前單字的結尾，或當游標在單字之間時刪除到下一個單字的結尾。儲存已刪除的文字以供貼上。在 macOS 上需要[Option 為 Meta](https://code.claude.com/docs/zh-TW/interactive-mode#keyboard-shortcuts) |
| `Ctrl+_` 或 `Ctrl+Shift+-`  | 復原最後的輸入編輯     | 復原先前的輸入文字和游標位置                                                                                                                                                                        |

### 編輯快捷鍵中的單字邊界

單字快捷鍵 `Alt+B`、`Alt+F`、`Alt+D`、`Option+Delete` 和 `Ctrl+Backspace` 將單字視為字母和數字的執行，因此標點符號（例如 `_`、`.` 和 `/`）會分隔單字。在提示中有 `src/utils/foo.ts` 時，重複按 `Alt+B` 會在 `ts`、`foo`、`utils` 和 `src` 的開始處停止。 `Ctrl+W` 不同：它忽略標點符號並刪除回到先前的空白，因此一次按下會移除所有 `src/utils/foo.ts`。 在沒有空格的文字中（例如中文或日文），單字快捷鍵仍然一次移動或刪除一個單字。 這些 readline 慣例適用於 Claude Code v2.1.261 及更新版本。在較早版本中開啟它們的 [`keybindingFlavor`](https://code.claude.com/docs/zh-TW/settings-reference#keybindingflavor) 設定已被棄用，沒有任何影響。 您無法在[快捷鍵設定檔](https://code.claude.com/docs/zh-TW/keybindings)中重新對應這些快捷鍵，該檔案沒有這些快捷鍵的操作。

### 主題和顯示

| 快捷鍵   | 說明                         | 內容                                                                         |
| -------- | ---------------------------- | ---------------------------------------------------------------------------- |
| `Ctrl+T` | 切換程式碼區塊的語法醒目提示 | 僅在 `/theme` 選擇器功能表內運作。控制 Claude 回應中的程式碼是否使用語法著色 |

### 多行輸入

| 方法        | 快捷鍵         | 內容                                                                                                                                                                                              |
| ----------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 快速逃脫    | `\` + `Enter`  | 在所有終端中運作                                                                                                                                                                                  |
| Option 鍵   | `Option+Enter` | 在 macOS 上啟用[Option 為 Meta](https://code.claude.com/docs/zh-TW/terminal-config#enable-option-key-shortcuts-on-macos)後                                                                        |
| Shift+Enter | `Shift+Enter`  | 在 iTerm2、WezTerm、Ghostty、Kitty、Warp、Apple Terminal、Windows Terminal 中原生。對於其他終端，請參閱[輸入多行提示](https://code.claude.com/docs/zh-TW/terminal-config#enter-multiline-prompts) |
| 控制序列    | `Ctrl+J`       | 在任何終端中無需設定即可運作                                                                                                                                                                      |
| 貼上模式    | 直接貼上       | 對於程式碼區塊、日誌                                                                                                                                                                              |

### 快速命令

| 快捷鍵         | 說明               | 備註                                                                                                                                                                                                                                                                                                                |
| -------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/` 在開始     | 命令或技能         | 請參閱[命令](https://code.claude.com/docs/zh-TW/interactive-mode#commands)和[技能](https://code.claude.com/docs/zh-TW/skills)                                                                                                                                                                                       |
| `!` 在開始     | Shell 模式         | 直接執行命令，將其輸出新增到工作階段，並讓 Claude 回應它                                                                                                                                                                                                                                                            |
| `@`            | 檔案路徑提及       | 觸發檔案路徑自動完成。在具有[跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#message-another-session)的工作階段中，當您在 `@` 後輸入至少一個字母時，Claude Code 也會建議您在此機器上的其他即時工作階段，以便您可以告訴 Claude 訊息您選擇的工作階段。需要 Claude Code v2.1.232 或更新版本 |
| `:`            | 表情符號速記代碼   | 輸入完整的 `:name:` 以插入表情符號，或輸入兩個或更多字元以取得建議。請參閱[表情符號速記代碼](https://code.claude.com/docs/zh-TW/interactive-mode#emoji-shortcodes)。需要 Claude Code v2.1.217 或更新版本                                                                                                            |
| `?` 在空輸入上 | 切換快捷鍵說明面板 | 當輸入已包含文字時輸入 `?` 會插入字元                                                                                                                                                                                                                                                                               |

### 文字記錄檢視器

當文字記錄檢視器開啟時（使用 `Ctrl+O` 切換），這些快捷鍵可用。執行不帶引數的 `/tui` 以檢查哪個渲染器處於作用中。`Ctrl+E` 可以通過 [`transcript:toggleShowAll`](https://code.claude.com/docs/zh-TW/keybindings) 重新繫結。

| 快捷鍵               | 說明                                                                                                                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `?`                  | 切換鍵盤快捷鍵說明面板。需要[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)                                                                                                     |
| `{` / `}`            | 跳到先前或下一個使用者提示，如 vim 段落動作。需要[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)                                                                                |
| `Ctrl+E`             | 切換顯示所有內容。僅在傳統渲染器中可用，不在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中                                                                                   |
| `[`                  | 將完整對話寫入您終端的原生捲動回溯，以便 `Cmd+F`、tmux 複製模式和其他原生工具可以搜尋它。需要[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen#search-and-review-the-conversation) |
| `v`                  | 將對話寫入臨時檔案並在 `$VISUAL` 或 `$EDITOR` 中開啟它。需要[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)                                                                     |
| `q`、`Ctrl+C`、`Esc` | 退出文字記錄檢視。所有三個都可以通過 [`transcript:exit`](https://code.claude.com/docs/zh-TW/keybindings) 重新繫結                                                                           |

### 語音輸入

| 快捷鍵             | 說明     | 備註                                                                                                                                                                                                              |
| ------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 按住或點選 `Space` | 語音聽寫 | 需要啟用[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)。按住以錄製，或執行 `/voice tap` 以進行點選切換。[可重新繫結](https://code.claude.com/docs/zh-TW/voice-dictation#rebind-the-dictation-key) |

## 指令

在 Claude Code 中輸入 `/` 以查看可用的指令，或輸入 `/` 後跟任何字母來篩選。`/` 選單列出內建指令、捆綁和使用者撰寫的 [skills](https://code.claude.com/docs/zh-TW/skills)，以及由 [plugins](https://code.claude.com/docs/zh-TW/plugins) 和 [MCP servers](https://code.claude.com/docs/zh-TW/mcp#use-mcp-prompts-as-commands) 貢獻的指令。並非所有內建指令對每個使用者都可見，因為某些指令取決於您的平台或方案，而且 [某些可用指令在設計上隱藏在選單之外](https://code.claude.com/docs/zh-TW/commands#how-the-command-menu-matches-what-you-type)，當您輸入其完整名稱時會執行。 在 [全螢幕呈現](https://code.claude.com/docs/zh-TW/fullscreen#use-the-mouse) 中，`/` 指令和 `@` 檔案建議清單也會回應滑鼠：懸停會反白一列，點擊會接受它。 請參閱 [指令參考](https://code.claude.com/docs/zh-TW/commands) 以取得 Claude Code 中包含的完整指令清單。

### 在提示中途完成指令

指令完成也適用於提示的中途：在空格後輸入 `/`，然後輸入名稱的前幾個字母，如 `run the tests, then /com`。只有名稱以這些字母開頭的指令才會符合，因此檔案路徑（例如 `/tmp/notes.md`）不會保持清單開啟。Claude Code 只有在指令 [開始您的訊息](https://code.claude.com/docs/zh-TW/commands) 時才會自行執行指令。

- **在[全螢幕呈現](https://code.claude.com/docs/zh-TW/fullscreen) 中**：當您輸入時，符合項會以清單形式開啟，沒有反白的列，因此 `Enter` 仍會按輸入的方式傳送您的提示。按 `Tab` 以插入最上面的符合項，或使用方向鍵和 `Enter` 選擇一列。
- **在全螢幕外** ：最上面符合項的其餘部分會在您的游標處顯示為幽靈文字，當有更多指令符合時會顯示計數（例如 `+2`）。按 `Tab` 以插入唯一的符合項，或在有多個符合項時開啟清單，然後使用方向鍵和 `Enter` 選擇一列。

在兩個呈現器中，在裸露的中途 `/` 上按 `Tab` 以列出每個指令。 外掛 skill 也會在其裸露名稱上符合，因此 `/deploy` 會找到名為 `myplugin:deploy-app` 的 skill。當您插入符合項時，Claude Code 會寫入完整的 `/myplugin:deploy-app`。

## Vim 編輯器模式

透過 `/config` → Editor mode 啟用 vim 風格的編輯。 Claude Code 會在您使用 `Ctrl+O` 切換[文字記錄檢視器](https://code.claude.com/docs/zh-TW/interactive-mode#transcript-viewer)或開啟和關閉面板（例如 `/config`）時保留您的 vim 模式和游標位置。如果您在 NORMAL 模式下離開提示，當您返回時它仍然處於 NORMAL 模式，游標位置與您離開時相同。

### 模式切換

| 命令              | 動作                                                                               | 來自模式       |
| ----------------- | ---------------------------------------------------------------------------------- | -------------- |
| `Esc` 或 `Ctrl+[` | 進入 NORMAL 模式。在使用 Kitty 鍵盤協議的終端中，`Ctrl+[` 需要 v2.1.242 或更新版本 | INSERT、VISUAL |
| `i`               | 在游標前插入                                                                       | NORMAL         |
| `I`               | 在行首插入                                                                         | NORMAL         |
| `a`               | 在游標後插入                                                                       | NORMAL         |
| `A`               | 在行尾插入                                                                         | NORMAL         |
| `o`               | 在下方開啟新行                                                                     | NORMAL         |
| `O`               | 在上方開啟新行                                                                     | NORMAL         |
| `v`               | 開始字元式視覺選擇                                                                 | NORMAL         |
| `V`               | 開始行式視覺選擇                                                                   | NORMAL         |

### 重新對應 INSERT 模式快捷鍵序列

[`vimInsertModeRemaps`](https://code.claude.com/docs/zh-TW/settings-reference#viminsertmoderemaps) 設定會將兩個按鍵的 INSERT 模式序列對應到 Escape，因此像 `jj` 這樣的對應會讓您返回 NORMAL 模式。需要 Claude Code v2.1.208 或更新版本。 以下 `~/.claude/settings.json` 範例會開啟 vim 模式並將 `jj` 對應到 Escape：

```
{
  "editorMode": "vim",
  "vimInsertModeRemaps": { "jj": "<Esc>" }
}

```

每個鍵恰好是按順序輸入的兩個可列印字元，而 `"<Esc>"` 是唯一支援的目標。具有不同長度或目標的項目會被忽略。 輸入序列的第一個字元會正常插入。在一秒內按下第二個字元會移除該待處理字元並切換到 NORMAL 模式，在您的輸入中不留下任何字元。在一秒的時間窗口之後，或如果按下不同的按鍵，兩個字元都會保留為字面文字，因此您仍然可以透過在兩個按鍵之間暫停來輸入包含該序列的單字。 Claude Code 只會從您的使用者設定檔、`--settings` 旗標和[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)讀取此設定。專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的項目會被忽略，因此簽出的儲存庫無法重新對應您的快捷鍵。

### 導覽（NORMAL 模式）

| 命令                                                                                                                                                                                                                                                                                           | 動作                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `h`/`j`/`k`/`l`                                                                                                                                                                                                                                                                                | 向左/向下/向上/向右移動                                                                                 |
| `Space`                                                                                                                                                                                                                                                                                        | 向右移動                                                                                                |
| `w`                                                                                                                                                                                                                                                                                            | 下一個單字                                                                                              |
| `e`                                                                                                                                                                                                                                                                                            | 單字結尾                                                                                                |
| `b`                                                                                                                                                                                                                                                                                            | 上一個單字                                                                                              |
| `0`                                                                                                                                                                                                                                                                                            | 行首                                                                                                    |
| `$`                                                                                                                                                                                                                                                                                            | 行尾                                                                                                    |
| `^`                                                                                                                                                                                                                                                                                            | 第一個非空白字元                                                                                        |
| `gg`                                                                                                                                                                                                                                                                                           | 輸入開始                                                                                                |
| `G`                                                                                                                                                                                                                                                                                            | 輸入結尾                                                                                                |
| `f{char}`                                                                                                                                                                                                                                                                                      | 跳到下一個字元出現位置                                                                                  |
| `F{char}`                                                                                                                                                                                                                                                                                      | 跳到上一個字元出現位置                                                                                  |
| `t{char}`                                                                                                                                                                                                                                                                                      | 跳到下一個字元出現位置之前                                                                              |
| `T{char}`                                                                                                                                                                                                                                                                                      | 跳到上一個字元出現位置之後                                                                              |
| `;`                                                                                                                                                                                                                                                                                            | 重複上一個 f/F/t/T 動作                                                                                 |
| `,`                                                                                                                                                                                                                                                                                            | 反向重複上一個 f/F/t/T 動作                                                                             |
| `/`                                                                                                                                                                                                                                                                                            | 開啟反向歷史搜尋，與 `Ctrl+R` 相同。空搜尋提示會顯示提示：按 `Esc` 然後 `i` 然後 `/` 以改為開啟命令選單 |
| 在 vim NORMAL 模式中，如果游標位於輸入的開始或結尾且無法進一步移動，`j`/`k` 和 `↑`/`↓` 會改為導覽命令歷史。在空提示上按 `←` 也會從 NORMAL 模式和 INSERT 模式開啟[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)；在 v2.1.219 之前，在空提示上按 `←` 在 NORMAL 模式中不執行任何操作。 |                                                                                                         |

### 編輯（NORMAL 模式）

| 命令                  | 動作                                                                               |
| --------------------- | ---------------------------------------------------------------------------------- |
| `x`                   | 刪除字元                                                                           |
| `dd`                  | 刪除行                                                                             |
| `D`                   | 刪除到行尾                                                                         |
| `dw`/`de`/`db`        | 刪除單字/到結尾/向後                                                               |
| `df{char}`/`dt{char}` | 刪除到並包括，或刪除到下一個字元出現位置之前                                       |
| `cc`                  | 變更行                                                                             |
| `C`                   | 變更到行尾                                                                         |
| `cw`/`ce`/`cb`        | 變更單字/到結尾/向後                                                               |
| `s`                   | 替換字元：刪除游標下的字元並進入 INSERT 模式。需要 Claude Code v2.1.211 或更新版本 |
| `S`                   | 替換行：清除行並進入 INSERT 模式。需要 Claude Code v2.1.211 或更新版本             |
| `yy`/`Y`              | 複製行                                                                             |
| `yw`/`ye`/`yb`        | 複製單字/到結尾/向後                                                               |
| `p`                   | 在游標後貼上                                                                       |
| `P`                   | 在游標前貼上                                                                       |
| `>>`                  | 縮排行                                                                             |
| `<<`                  | 取消縮排行                                                                         |
| `J`                   | 合併行                                                                             |
| `u`                   | 復原                                                                               |
| `.`                   | 重複上一個變更                                                                     |

### 文字物件（NORMAL 模式）

文字物件可與運算子（例如 `d`、`c` 和 `y`）搭配使用：

| 命令      | 動作                       |
| --------- | -------------------------- |
| `iw`/`aw` | 內部/周圍單字              |
| `iW`/`aW` | 內部/周圍 WORD（空白分隔） |
| `i"`/`a"` | 內部/周圍雙引號            |
| `i'`/`a'` | 內部/周圍單引號            |
| `i(`/`a(` | 內部/周圍括號              |
| `i[`/`a[` | 內部/周圍方括號            |
| `i{`/`a{` | 內部/周圍大括號            |

### 視覺模式

按 `v` 進行字元式選擇或按 `V` 進行行式選擇。動作會延伸選擇，運算子會直接作用於它。

| 命令                                   | 動作                            |
| -------------------------------------- | ------------------------------- |
| `d`/`x`                                | 刪除選擇                        |
| `y`                                    | 複製選擇                        |
| `c`/`s`                                | 變更選擇                        |
| `p`                                    | 用暫存器內容取代選擇            |
| `r{char}`                              | 將每個選定的字元取代為 `{char}` |
| `~`/`u`/`U`                            | 切換、小寫或大寫選擇            |
| `>`/`<`                                | 縮排或取消縮排選定的行          |
| `J`                                    | 合併選定的行                    |
| `o`                                    | 交換游標和錨點                  |
| `iw`/`aw`/`i"`/…                       | 選擇文字物件                    |
| `v`/`V`                                | 在字元式和行式之間切換，或退出  |
| 不支援使用 `Ctrl+V` 的區塊式視覺模式。 |                                 |

## 命令歷史

Claude Code 會保留您輸入的提示詞歷史，並且向上箭頭可以回憶同一專案過去工作階段的提示詞：

- 輸入歷史按工作目錄儲存
- 執行 `/clear` 會開始新的工作階段：回憶時會先列出新工作階段的提示詞，然後是較早工作階段的提示詞。前一個工作階段的對話會被保留，可以繼續進行。
- 連續提交相同的提示詞兩次只會記錄一個歷史項目，因此按向上箭頭會跳到前一個不同的提示詞
- 當您回憶包含貼上文字的提示詞時，Claude Code 會在您重新提交時再次傳送完整的貼上內容。如果內容已被[自動清理](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)，Claude Code 不會傳送字面上的 `[Pasted text #N]` 字串；請參閱[貼上大型內容](https://code.claude.com/docs/zh-TW/terminal-config#paste-large-content)以了解提示詞會發生什麼情況
- 使用 `!` 的歷史展開預設為停用

### 使用 Ctrl+R 進行反向搜尋

按 `Ctrl+R` 以互動方式搜尋您的命令歷史。在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中，`Ctrl+R` 會開啟搜尋對話框：輸入以篩選、按 `Up` 和 `Down` 在符合項目中移動，以及按 `Ctrl+S` 循環切換範圍（此工作階段、此專案和所有專案）。按 `Enter` 或 `Tab` 將符合項目放在提示詞輸入中，或按 `Esc` 取消。下面的步驟說明傳統渲染器的內嵌搜尋：

1. **開始搜尋** ：按 `Ctrl+R` 啟動反向歷史搜尋
1. **輸入查詢** ：輸入要在先前命令中搜尋的文字。搜尋詞在符合結果中會被反白顯示
1. **導覽符合項目** ：再次按 `Ctrl+R` 循環瀏覽較舊的符合項目
1. **搜尋範圍** ：內嵌搜尋始終搜尋來自所有專案的提示詞
1. **接受符合項目** ：
   - 按 `Tab` 或 `Esc` 接受目前的符合項目並繼續編輯
   - 按 `Enter` 接受並立即執行命令
1. **取消搜尋** ：
   - 按 `Ctrl+C` 取消並還原您的原始輸入
   - 在空搜尋上按 `Backspace` 取消

內嵌搜尋會掃描您的完整提示詞歷史（最新優先），並將重複項目摺疊到最新出現的位置。全螢幕對話框會在選定的範圍內搜尋您的整個提示詞歷史（最新優先），並將重複項目摺疊到最新出現的位置：最近的提示詞會立即出現，而較舊提示詞的符合項目會在 Claude Code 載入其餘部分時填入。符合的提示詞會顯示搜尋詞反白顯示，因此您可以找到並重複使用先前的輸入。 接受符合項目或取消搜尋會立即生效，即使 Claude Code 仍在載入歷史。

## 背景 Bash 命令

Claude Code 支援在背景執行 Bash 命令，讓您可以在長時間執行的程序進行時繼續工作。

### 背景執行的運作方式

當 Claude Code 在背景執行命令時，它會非同步執行該命令並立即傳回背景工作 ID。Claude Code 可以在命令繼續在背景執行時回應新的提示。 若要在背景執行命令，您可以：

- 提示 Claude Code 在背景執行命令
- 按 `Ctrl+B` 將一般 Bash 工具叫用移至背景。Tmux 使用者必須按 `Ctrl+B` 兩次，因為 tmux 的前置鍵。

**主要功能：**

- 輸出會寫入檔案，Claude 可以使用 Read 工具擷取它
- 背景工作具有唯一的 ID，用於追蹤和輸出擷取
- 當 Claude Code 結束時，背景工作會自動清理。在 macOS 和 Linux 上，當您從 [`/tasks`](https://code.claude.com/docs/zh-TW/commands) 停止背景工作或 Claude Code 在結束時停止它時，從工作的 shell 分離的程序（例如在 `setsid` 或 `timeout` 下啟動的程序）也會停止
- 如果您將工作階段放在背景而不是結束它，您的背景工作會繼續在背景工作階段中執行。請參閱[將執行中的工作階段放在背景](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)
- 如果輸出超過 5GB，背景工作會自動終止，stderr 中會有說明原因的備註
- 在 macOS 和 Linux 上，當作業系統發出記憶體壓力信號時，Claude Code 會終止執行中的背景工作，前提是工作階段已閒置至少 30 分鐘且沒有執行任何轉向或子代理。將 [`CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 以關閉此功能。需要 Claude Code v2.1.193 或更新版本
- 由[子代理](https://code.claude.com/docs/zh-TW/sub-agents)擁有的背景命令沒有時間限制，除非由在前景執行的子代理擁有的命令在該子代理給出最終回應時結束；請參閱工具參考中的[背景命令](https://code.claude.com/docs/zh-TW/tools-reference#background-commands)。在 v2.1.218 之前，記憶體壓力回收和先前的子代理命令 60 分鐘限制都不涵蓋使用 `Ctrl+B` 移至背景的命令

若要停用所有背景工作功能，請將 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` 環境變數設定為 `1`。詳細資訊請參閱[環境變數](https://code.claude.com/docs/zh-TW/env-vars)。 **常見的背景命令：**

- 建置工具（webpack、vite、make）
- 套件管理員（npm、yarn、pnpm）
- 測試執行器（jest、pytest）
- 開發伺服器
- 長時間執行的程序（docker、terraform）

### 使用 `!` 前置詞的 Shell 模式

透過在輸入前加上 `!` 直接執行 shell 命令，無需透過 Claude：

```
! npm test
! git status
! ls -la

```

Shell 模式：

- 將命令及其輸出新增至對話內容
- 顯示即時進度和輸出
- 支援相同的 `Ctrl+B` 背景執行，用於長時間執行的命令
- 不需要 Claude 解釋或核准命令
- 支援歷史記錄型自動完成：輸入部分命令並按 `Tab` 以從目前專案中的先前 `!` 命令完成
- 自 v2.1.193 起在所有平台上支援即時檔案路徑自動完成：輸入包含正斜線的權杖（例如 `./src/` 或 `~/`）以查看相符檔案和目錄的下拉式清單，然後按 `Tab` 以接受。在 Windows 上也使用正斜線；下拉式清單由 `/` 觸發，而不是 `\`
- 在空提示上按 `Escape`、`Backspace` 或 `Ctrl+U` 結束
- 將以 `!` 開頭的文字貼到空提示中會自動進入 shell 模式，符合輸入的 `!` 行為

除非您的工作階段是[嚴格沙箱模式](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch)下列出的其中一個，否則您在 shell 模式中輸入的命令會在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)外執行，即使您已啟用沙箱，因為沙箱適用於 Claude 執行的命令。 一旦命令輸出進入文字記錄，Claude 會自動回應，因此您可以執行 `! npm test` 並取得失敗的說明，無需第二個提示。回應成本與傳送一般提示相同。若要還原先前的行為（其中輸出會新增至內容而不回應），請在 `settings.json` 中將 [`respondToBashCommands`](https://code.claude.com/docs/zh-TW/settings-reference#respondtobashcommands) 設定為 `false`。在 v2.1.186 之前，shell 模式始終將輸出新增至內容而不回應。

## 在 Claude 工作時排隊傳送訊息

在 Claude 工作時輸入訊息並按 `Enter`。Claude Code 會將訊息排隊而不是中斷該輪次，並在輸入框上方列出排隊的項目，直到傳送為止。您可以用相同的方式排隊 `!` [shell 命令](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)和大多數 [commands](https://code.claude.com/docs/zh-TW/commands)，除了 `/status` 等 Claude Code 會在您傳送時立即執行的命令。

### Claude Code 何時傳送您排隊的內容

排隊項目何時到達 Claude 取決於您排隊的內容。

- 訊息：如果您在 Claude 執行工具呼叫時排隊訊息，Claude Code 會在這些工具呼叫完成後立即將其傳遞給 Claude，在同一輪次內。當輪次結束時仍有訊息排隊，Claude Code 只會傳送最舊的訊息作為下一輪次。其餘的保持排隊狀態並遵循相同規則：Claude Code 會在該輪次的工具呼叫完成時將其傳遞給 Claude，或在下一輪次傳送下一個最舊的訊息
- 命令和 shell 命令：Claude Code 會保留它們直到輪次結束，然後逐個執行

按 `Esc` 以中斷輪次。Claude Code 會保留您排隊的內容並立即傳送。 Claude Code 會在您傳送某些命令時立即執行它們，而不是排隊，其中包括 `/model`、`/effort` 和 `/fast`。這三個命令各自改變一個設定：模型、努力等級或快速模式。Claude Code 是否將新設定應用於 Claude 已在進行的輪次，或僅從您的下一輪次開始，因命令而異：

- [`/model`](https://code.claude.com/docs/zh-TW/model-config#setting-your-model)：一旦您確認 [cache warning](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)（如果 Claude Code 顯示的話），Claude Code 會將您的變更應用於該輪次中它進行的下一個請求
- [`/effort`](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)：一旦您確認 [cache warning](https://code.claude.com/docs/zh-TW/prompt-caching#changing-effort-level)（如果 Claude Code 顯示的話），Claude Code 會將您的變更應用於該輪次中它進行的下一個請求
- [`/fast`](https://code.claude.com/docs/zh-TW/fast-mode#toggle-fast-mode)：Claude Code 保留輪次開始時活躍的快速模式設定，因此您的速度變更從您的下一輪次開始應用。如果您目前的模型不支援快速模式，開啟它也會 [切換您的模型](https://code.claude.com/docs/zh-TW/prompt-caching#turning-on-fast-mode)，Claude Code 會從該輪次中的下一個請求使用新模型

### 取回您排隊的內容

從輸入框的第一行按 `Up` 以取回排隊的訊息和命令。Claude Code 會將它們從隊列中移除並放入輸入框，每行一個，位於您已輸入的任何文字之前。編輯文字並按 `Enter` 以將其作為一個項目再次排隊，或清除輸入框以捨棄它。 Claude Code 只有在輸入框為空且您沒有其他排隊項目時才會取回排隊的 shell 命令，並在執行時將輸入框切換到 shell 模式。否則它會將它們保留在隊列中，以其 `!` 前綴列出，並在輪次結束後執行它們。

## 提示建議

當您首次開啟工作階段時，Claude Code 會在提示輸入中顯示一個灰色的範例命令，以幫助您開始。它從您專案的 git 歷史記錄中選擇此範例，因此該範例反映了您最近正在處理的檔案。 Claude 回應後，Claude Code 可以根據您的對話歷史記錄建議您的下一個提示，例如多部分請求的後續步驟或工作流程的自然延續。

- 按 `Tab` 或 `Right arrow` 將建議放入提示輸入中，然後按 `Enter` 提交
- 開始輸入以關閉它

Claude Code 使用背景請求產生每個這些下一個提示建議，該請求會重複使用對話的提示快取，因此額外成本最少。

### 當 Claude Code 跳過建議時

在互動模式中，Claude Code 預設會關閉提示建議，並在 `/config` 中隱藏 **Prompt suggestions** 切換，該切換位於[不會擷取功能旗標的工作階段](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)中，例如第三方提供者上的工作階段或透過 Claude 應用程式閘道的工作階段，以及在[安裝或升級後的第一個工作階段](https://code.claude.com/docs/zh-TW/env-vars#first-session-after-an-install-or-upgrade)中，其旗標尚未到達。 Claude Code 也會在多種情況下跳過個別建議，包括：

- 提示快取為冷狀態，以避免不必要的成本
- 在對話的第一輪之後，在某些工作階段中
- 前一個回應以錯誤結束
- 當您處於 Plan Mode 時
- 您的帳戶接近或已達到使用限制。若要在達到限制之前保持建議開啟，請將 [`CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `true`。在 v2.1.238 之前，即使將變數設定為 `true`，Claude Code 也會在接近限制時跳過建議
- 在[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)中，預設情況下在隊友的工作階段中。主導者的工作階段會顯示建議

在列印模式中，Claude Code 預設不會產生建議。使用 [`--prompt-suggestions`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 搭配 `-p "<prompt>" --output-format stream-json --verbose` 讓 Claude Code 在每個產生建議的輪次後發出 `prompt_suggestion` 訊息。產生器在此也會跳過非常短的對話和冷提示快取，因此單一短 `-p` 查詢可能不會發出任何建議。

### 關閉提示建議

若要完全停用提示建議，請使用以下任一方法：

- 在 `/config` 中關閉 **Prompt suggestions**
- 在您的設定檔中將 [`promptSuggestionEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#promptsuggestionenabled) 設定為 `false`
- 將 [`CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數設定為 `false`，其優先於設定：

```
export CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false

```

若要在整個組織中關閉提示建議，請在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中將 `promptSuggestionEnabled` 設定為 `false`。同時在受管 [`env`](https://code.claude.com/docs/zh-TW/settings-reference#env) 金鑰下將 `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` 設定為 `false`，以便使用者無法使用自己的環境變數重新啟用它們。

## Emoji 快捷代碼

在提示輸入中輸入 `:` 後跟 emoji 快捷代碼以插入 emoji。需要 Claude Code v2.1.217 或更新版本。

- 輸入完整的快捷代碼，例如 `:heart:`，Claude Code 會在您輸入結尾的 `:` 時立即將其替換為 ❤️
- 輸入 `:` 加上至少兩個字元的名稱，例如 `:hea`，以開啟建議彈出視窗，然後按 `Tab` 或 `Enter` 以插入突出顯示的 emoji

快捷代碼必須在輸入的開始或空格後開始，因此單字或 URL 內的 `:` 不會開啟建議。 若要關閉此功能，請在 `settings.json` 中將 [`emojiCompletionEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#emojicompletionenabled) 設定為 `false`。這會停用建議彈出視窗和內嵌替換。

## 在輸入時檢查拼寫

Claude Code 可以在您輸入時在提示輸入框中為拼寫錯誤的單詞加上底線。它只檢查輸入框中的文字，從不檢查 Claude 的回覆或您的檔案。它也不會在輸入框處於[殼層模式](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)、`Ctrl+R` 歷史記錄搜尋或[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)時檢查任何內容。 拼寫檢查預設為關閉，Claude Code 在[螢幕閱讀器模式](https://code.claude.com/docs/zh-TW/accessibility)中不檢查任何內容。需要 Claude Code v2.1.235 或更新版本。

### 先決條件

- 安裝 [aspell](https://github.com/GNUAspell/aspell)、[hunspell](https://github.com/hunspell/hunspell) 或 [ispell](https://en.wikipedia.org/wiki/Ispell)，並確保它在您的 `PATH` 上。Claude Code 在每個平台上執行它找到的前三個中的第一個，包括套件管理員在 Windows 上安裝的 `.cmd` shim。
- 若要檢查程式是否在您的 `PATH` 上，請在您的終端機中執行 `aspell --version`、`hunspell --version` 或 `ispell -v`。「command not found」錯誤表示它還不在您的 `PATH` 上。

### 開啟或關閉拼寫檢查

Claude Code 從三個地方讀取 [`spellcheck`](https://code.claude.com/docs/zh-TW/settings-reference#spellcheck) 設定，並在專案的 `.claude/settings.json` 和 `.claude/settings.local.json` 中忽略它。從您使用的任何一個地方開啟它：

- 使用者設定
- 命令列
- 受管設定

將 `spellcheck` 新增到 `~/.claude/settings.json`。它適用於您開啟的每個專案，就像您的其他[使用者設定](https://code.claude.com/docs/zh-TW/settings#where-settings-live)一樣：

```
{
  "spellcheck": { "enabled": true }
}

```

將 `spellcheck` 儲存在 JSON 檔案中，例如 `spellcheck.json`：

```
{
  "spellcheck": { "enabled": true }
}

```

然後將檔案傳遞給 `--settings`。它僅適用於該工作階段：

```
claude --settings spellcheck.json

```

將 `spellcheck` 新增到您組織的[受管設定來源](https://code.claude.com/docs/zh-TW/permissions#managed-settings)之一。它適用於接收這些設定的每個使用者，他們無法將其關閉：

```
{
  "spellcheck": { "enabled": true }
}

```

若要檢查拼寫檢查是否開啟，請輸入一個拼寫錯誤的單詞和一個空格。Claude Code 會為該單詞加上底線。如果沒有，請參閱[當 Claude Code 不加任何底線時](https://code.claude.com/docs/zh-TW/interactive-mode#when-claude-code-underlines-nothing)。若要再次關閉拼寫檢查，請在同一位置將 `enabled` 設定為 `false`，或移除 `spellcheck`。 若要選擇 Claude Code 執行的三個程式中的哪一個、它使用的字典或底線顏色，請在同一位置在 `enabled` 旁邊新增以下任何欄位：

- `checker`：`aspell`、`hunspell` 或 `ispell`。Claude Code 不會從您命名的檢查器回退，並將任何其他值視為 `auto`。
- `language`：您的檢查器形式中的字典名稱，例如 `en_GB`。Claude Code 忽略任何不是純字典名稱的值，例如路徑或包含空格的名稱，檢查器使用其預設字典。
- `color`：顏色名稱，例如 `yellow`，或 `#rrggbb`、`#rgb`、`rgb(r,g,b)`、`ansi256(n)` 或 `ansi:<name>` 值。Claude Code 預設使用您主題的錯誤顏色，對於任何它無法識別的值也是如此。

例如，此 `spellcheck` 設定使用其 `en_GB` 字典執行 hunspell，並以黃色為單詞加上底線。它在 `~/.claude/settings.json`、您傳遞給 `--settings` 的檔案和受管設定中的工作方式相同：

```
{
  "spellcheck": {
    "enabled": true,
    "checker": "hunspell",
    "language": "en_GB",
    "color": "yellow"
  }
}

```

如果三個地方中有多個具有 `spellcheck` 設定，Claude Code 只使用其中一個：受管設定優先，然後是 `--settings`，然後是使用者設定。它不會合併來自兩個地方的欄位。例如，當 `--settings` 設定 `spellcheck` 時，您使用者設定中的 `language` 無效。

### Claude Code 加底線的內容

在您暫停輸入後不久，Claude Code 會為字典不知道的單詞加上底線。它在您仍在輸入時不理會該單詞，直到您超過它，並且它永遠不會改變您的文字。它也會跳過看起來像程式碼的文字：

- 命令，例如 `/help`、`@` 提及、URL、檔案路徑和旗標，例如 `--verbose`
- 包含數字、底線或第一個字母後大寫字母的單詞，以及反引號中的文字

Claude Code 也會跳過中文、日文、韓文、泰文、寮文、高棉文和緬甸文文字。 Claude Code 沒有自己的單詞列表：當您的檢查器說某個單詞拼寫錯誤時，它就是拼寫錯誤。若要停止 Claude Code 為某個單詞加底線，請按照檢查器自己的文件將該單詞新增到您的檢查器的個人字典。Claude Code 在您重新啟動它後會選取新單詞。

### 當 Claude Code 不加任何底線時

當 Claude Code 無法保持檢查器執行時，它不加任何底線：

- 未安裝檢查器，或您在 `checker` 中命名的檢查器遺失
- 檢查器在啟動時或工作階段稍後連續失敗兩次。Claude Code 在第一次失敗後重新啟動它，在第二次失敗後停止檢查，直到您重新啟動 Claude Code
- 檢查器花費超過 15 秒來回答三次。每次，Claude Code 都會將它等待的單詞保留為未標記；在第三次之後，它停止檢查，直到您重新啟動 Claude Code

若要找出發生了哪一種情況，請使用 `claude --debug` 啟動拼寫檢查並輸入一個單詞。然後在 `~/.claude/debug/<session-id>.txt` 的偵錯日誌中查找 `[spellcheck]` 行。一行命名 Claude Code 啟動的程式，或列出它查找但未找到的程式。稍後的行說明它停止的原因。那裡的缺少字典錯誤表示檢查器沒有您的 `language` 值的字典，或當 `language` 未設定時沒有預設字典。安裝一個，或將 `language` 設定為您擁有的字典。

## 使用 /diff 檢視變更

執行 `/diff` 以在不離開 Claude Code 的情況下查看工作樹中的變更。您可以看到 Claude 迄今為止所做的編輯，以及任何您尚未提交的其他內容。 在 `/diff` 從 git 讀取的變更中，子模組會顯示為單一項目，且僅當其指向的提交發生變更時才會出現；對子模組內檔案的編輯不會在此處顯示。 在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中，`/diff` 會在對話旁邊開啟[差異面板](https://code.claude.com/docs/zh-TW/interactive-mode#diff-panel)，該面板會保持開啟並在您繼續工作時更新。在經典渲染器中，`/diff` 會在提示的位置開啟[差異檢視器](https://code.claude.com/docs/zh-TW/interactive-mode#diff-viewer)，您在閱讀完後將其關閉。

### 差異面板

差異面板列出已變更的檔案及其新增和移除的行數，並在列表下方顯示每個檔案的差異。Claude Code 會在 Claude 編輯檔案或執行 shell 命令時重新整理它。若要關閉它，請再次執行 `/diff` 或按一下其標題中的 `✕`。 若要使用該面板，您需要：

- [全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)
- 一個 git 儲存庫
- 寬度至少為 110 欄的終端機
- Claude Code v2.1.260 或更新版本

當面板無法開啟時，`/diff` 會改為開啟差異檢視器或告訴您原因。 一旦 Claude 開始編輯檔案，如果您的終端機寬度至少為 144 欄，該面板也會自動開啟。在您自己使用 `/diff` 開啟它後，後續工作階段會在 Claude 在任何足夠寬的終端機中編輯檔案時立即開啟它。關閉面板後，它會保持關閉狀態，在此工作階段和後續工作階段中，直到您再次執行 `/diff`。 當面板開啟時，您可以：

- **跳至檔案** ：按一下列表中的其列。使用滑鼠滾輪捲動面板。當檔案列表本身太長而無法容納時，使用 `Alt+Up` 和 `Alt+Down` 或 `Ctrl+Up` 和 `Ctrl+Down` 捲動它。
- **詢問 Claude 有關特定行的問題** ：在面板中使用滑鼠選取它們。Claude Code 會將選取項目附加到您的下一個提示，並在您傳送提示之前在輸入旁邊顯示行數。
  - 若要在不包含選取項目的情況下傳送提示，請將游標移至行數指示器之後，然後按 `Backspace` 將其刪除。需要 Claude Code v2.1.271 或更新版本。
- **顯示面板遺漏的檔案** ：列表會跳過測試檔案和產生的檔案，並將此工作階段之前的變更摺疊為底部的一行。按一下任一計數行以展開它。
- **變更面板比較的對象** ：按 `Ctrl+X B` 以在此工作階段的變更、您的未提交變更作為一個列表，以及自您的分支從預設分支分割以來的所有內容之間循環。Claude Code 會記住每個專案的選擇。

若要將快捷鍵繫結到這些動作，請參閱[差異面板動作](https://code.claude.com/docs/zh-TW/keybindings#diff-panel-actions)。

### 差異檢視器

差異檢視器會取代提示，直到您關閉它。其**目前** 檢視會顯示您來自 git 的未提交變更，或者，當沒有變更時，您的分支在預設分支之上新增的內容。檢視器也有一個轉換檢視，用於 Claude 編輯檔案後的每個提示，僅顯示這些編輯。Claude Code 從 Claude 的檔案編輯而非 git 建立轉換檢視，因此 Claude 透過 shell 命令進行的變更僅出現在「目前」下。 在檢視器中使用這些快捷鍵：

- **左和右** ：在「目前」和轉換檢視之間移動。
- **上和下** ：選取檔案。
- **Enter** ：開啟所選檔案的差異。使用上和下或 PageUp 和 PageDown 捲動它。
- **Esc** ：從檔案的差異返回到列表，或從列表關閉檢視器。

若要重新繫結這些快捷鍵，請參閱[差異動作](https://code.claude.com/docs/zh-TW/keybindings#diff-actions)。

## 使用 /btw 提出附帶問題

使用 `/btw` 提出關於您目前工作的問題，而不將其新增至對話歷史記錄。

```
/btw what was the name of that config file again?

```

Claude 會根據對話中已有的內容來回答附帶問題：您的訊息、它的回覆，以及它蒐集的工具結果。您可以詢問 Claude 已經讀過的程式碼、它之前做出的決定，或工作階段中的任何其他內容。較晚的附帶問題也會看到您之前的附帶問題：Claude Code 會在每次提問時重新播放最新的 20 次交換，直到您清除它們為止。問題和答案永遠不會進入對話歷史記錄。在終端機中，它們會出現在可關閉的覆蓋層中。終端機會將執行緒保留在記憶體中：按 `x` 清除較早的交換，當您退出 Claude Code 時，它就會消失。 在 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code#use-the-prompt-box)的聊天面板中，`/btw` 會開啟一個面板，而不是本節所述的覆蓋層，您可以直接在面板中提出後續問題。該面板的執行緒在視窗重新載入後仍會保留，遵循該頁面所述的保留排程。您需要 v2.1.227 或更新版本的擴充功能。較早的擴充功能版本不提供 `/btw`。

- **Claude 工作時可用** ：即使 Claude 正在處理回應時，您也可以執行 `/btw`。附帶問題會獨立執行，不會中斷主要回合。它會看到目前為止對話中的所有內容，除了 Claude 仍在撰寫的回覆。
- **無工具存取** ：附帶問題只能根據已在內容中的內容來回答。Claude 在回答附帶問題時無法讀取檔案、執行命令或搜尋。如果 Claude 無論如何都將工具呼叫寫成文字，答案會以一個說明沒有任何內容被執行的備註結尾。
- **單一回應** ：覆蓋層中沒有後續回合。若要繼續執行緒，請提出另一個 `/btw` 問題。若要在本機工作階段中繼續使用完整工具存取，請按 `f` 將此問題和答案分支到[背景子代理](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)。
- **低成本** ：當對話的[提示快取](https://code.claude.com/docs/zh-TW/prompt-caching)處於熱狀態時，附帶問題的成本只是答案本身之外的少量成本。

您最新的五個較早附帶問題會以暗淡的清單形式出現在目前答案上方，並顯示任何較舊問題的計數。它們會保持在對話歷史記錄之外。 若要在關閉覆蓋層後返回，請執行不帶問題的 `/btw`。覆蓋層會在您最近的交換上重新開啟。在 v2.1.212 之前，不帶問題的 `/btw` 會改為列印使用訊息。 答案出現後，覆蓋層會接受這些按鍵。

| 按鍵                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 動作                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Space`、`Enter`、`Escape`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 關閉答案並返回提示                                                                                                                                                                                                                                                                                                         |
| `Up` / `Down`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 捲動答案                                                                                                                                                                                                                                                                                                                   |
| `Shift+Left` / `Shift+Right`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 在此答案和您較早的 `/btw` 答案之間步進。`Shift+Left` 移至較舊的答案，`Shift+Right` 返回目前的答案。`[` 和 `]` 執行相同操作，適用於不報告 `Shift` 與箭頭鍵的終端機。`Tab` / `Shift+Tab` 在相同答案之間循環。需要 Claude Code v2.1.257 或更新版本。在 v2.1.187 和 v2.1.256 之間，按鍵是純 `Left` / `Right`                   |
| `c`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 將答案複製到您的剪貼簿作為原始 Markdown。使用此方法而不是滑鼠選取，後者會擷取硬換行的終端機呈現，而不是原始文字                                                                                                                                                                                                            |
| `f`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 啟動[分支子代理](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)，它繼承父對話加上此問題和答案，以便它可以繼續使用完整工具存取。您保持在目前工作階段中，並在[提示下方的面板](https://code.claude.com/docs/zh-TW/sub-agents#observe-and-steer-running-forks)中找到分支。僅在本機工作階段中可用 |
| `x`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 清除目前答案上方顯示的較早 `/btw` 交換清單                                                                                                                                                                                                                                                                                 |
| 在附加的[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view#attach-to-a-session)中，`Left` 會分離並將您返回代理檢視，即使答案仍在送達中。附帶問題會在您離開時繼續執行。下次您附加到工作階段時，覆蓋層會使用附帶問題或其答案重新開啟。在 v2.1.257 之前，`Left` 在那裡不會分離。 `/btw` 會看到您的完整對話，但沒有工具。[子代理](https://code.claude.com/docs/zh-TW/sub-agents)有工具，並從它接收的提示開始，或者對於[分支](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)，從此對話的副本開始。使用 `/btw` 詢問 Claude 已從此工作階段了解的內容；使用子代理來發現新的內容。 |                                                                                                                                                                                                                                                                                                                            |

## 工作清單

工作清單是 Claude 的待辦事項檢查清單：Claude 建立的項目，用於規劃多步驟工作，並顯示待處理、進行中或已完成的指示器。它與背景工作檢視分開。若要查看執行中的 shell 和子代理，請改用 [`/tasks`](https://code.claude.com/docs/zh-TW/commands)。 此清單僅在具有工作追蹤工具的工作階段中填充，Claude Code 預設在 [Claude 3.x 模型、Opus 4 至 4.7、Sonnet 4 至 4.6 及 Haiku 4.5](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability) 上提供。在任何其他模型上，包括 Claude Code 無法識別的模型 ID，除非您使用 `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` 或 [工作工具可用性](https://code.claude.com/docs/zh-TW/tools-reference#task-tool-availability) 下的其他方式選擇加入，否則清單保持空白。當工作階段具有這些工具時，工作清單的運作方式如下：

- 按 `Ctrl+T` 切換工作清單檢視。顯示一次最多五個工作。當 Claude 尚未建立任何檢查清單項目時，切換沒有可見效果，因為沒有任何內容可顯示
- 如果您保持清單展開，Claude Code 會在下次啟動仍有工作的工作階段時（例如使用 `--resume` 或 `--continue`）還原展開檢視。當工作清單為空時，Claude Code 會以摺疊狀態啟動它
- 若要查看所有工作或清除它們，直接詢問 Claude：「show me all tasks」或「clear all tasks」
- 工作在內容壓縮過程中保持不變，幫助 Claude 在較大的專案上保持組織
- 若要在工作階段之間共享工作清單，請設定 `CLAUDE_CODE_TASK_LIST_ID` 以使用 `~/.claude/tasks/` 中的具名目錄：`CLAUDE_CODE_TASK_LIST_ID=my-project claude`

## 工作階段摘要

當您離開終端機後返回時，Claude Code 會顯示工作階段迄今為止發生情況的單行摘要。摘要會在背景中生成，一旦自上次完成的回合已經過至少三分鐘且終端機未獲得焦點，摘要就會準備好供您切換回來時使用。摘要只會在工作階段至少有三個回合後出現，且永遠不會連續出現兩次。 執行 `/recap` 以按需生成摘要。Claude Code 將自動摘要和 `/recap` 輸出都限制在 400 個字元。若要關閉自動摘要，請開啟 `/config` 並關閉**工作階段摘要** 。 工作階段摘要在所有方案和提供者上預設為開啟。摘要在非互動模式中始終被跳過。

## 等待使用量限制重設

當 claude.ai [使用量限制](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-session-limit) 在任務中途停止 Claude 時，Claude Code 會在開啟的工作階段中等待，並在限制重設後自動繼續該任務。在使用 claude.ai 訂閱登入的互動式工作階段中，自動繼續預設為開啟。需要 Claude Code v2.1.234 或更新版本。 Claude Code 等待時，工作階段底部的一行會顯示何時繼續：

```
Usage limit reached · continuing automatically at 3:45pm · esc to cancel

```

保持工作階段開啟。接下來發生的情況取決於等待如何結束：

- **在重設時** ：該行顯示 `continuing shortly`，然後 `Usage limit reset · continuing automatically`，Claude Code 會向 Claude 傳送一個固定提示，以便從停止的地方繼續任務。它不會重新傳送您的最後一條訊息。
- **在您的電腦睡眠後** ：如果睡眠超過約 30 分鐘，且限制在睡眠期間重設，該行會顯示 `Your usage limit has reset · press enter to continue`。按 `Enter` 繼續。睡眠時間較短後，Claude Code 會自動繼續。
- **提前** ：當您使用 `/usage-credits` 完成新增 [使用額度](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription)、在 `/upgrade` 後重新登入，或在等待期間使用 `/model` 切換模型時，Claude Code 會檢查使用量是否再次可用，如果可用則立即繼續。它不會在您在瀏覽器中自行進行的升級或購買後檢查。在 [`opusplan`](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting) 和其他在不同模型上執行計畫模式的模型設定下，Claude Code 會改為等待重設。

繼續的任務會像任何其他回合一樣執行。Claude Code 仍會照常要求 [權限](https://code.claude.com/docs/zh-TW/permissions)，因此任務可能會在您不在時在提示處停止。如果再次達到限制，Claude Code 最多會自動重新啟動等待兩次，然後停止並顯示 `Automatic continue stopped after repeated usage-limit hits · /rate-limit-options to try again`。

### 取消等待

在空提示處按 `Esc`，或在該行顯示時按 `Ctrl+C`，或執行 [`/rate-limit-options`](https://code.claude.com/docs/zh-TW/commands#all-commands) 並選擇 **Don’t continue automatically** 。Claude Code 會確認一行以 `Automatic continue cancelled` 開頭的訊息。 取消後，在您傳送提示或再次從 `/rate-limit-options` 選擇以 **Wait here, then continue automatically** 開頭的列之前，不會有任何內容繼續。Claude Code 不會在該重設視窗中自行再次啟動等待；下一個重設視窗會重新開始。 等待也會在以下情況下結束而不繼續任務：

- **您傳送提示** ：Claude Code 會執行您的提示而不是等待。
- **您退出 Claude Code** ：當您繼續工作階段時，等待不會重新啟動。
- **對話轉手** ：您使用 `/login` 切換帳戶、清除或倒帶對話、`/resume` 另一個工作階段、使用 `/teleport` 拉取一個、使用 `/tui` 重新啟動，或將工作階段交給 Claude Desktop、背景工作階段或雲端。
- **設定關閉，或重設超過 24 小時** ：這只會結束 Claude Code 自行啟動的等待。您從 `/rate-limit-options` 選擇的等待會繼續倒數。
- **繼續被阻止** ：一個 [`UserPromptSubmit` hook](https://code.claude.com/docs/zh-TW/hooks#userpromptsubmit) 阻止繼續提示，或在到達模型之前失敗，會結束等待。Claude Code 會告訴您繼續未執行。傳送提示以繼續。

### 自行啟動等待

Claude Code 在以下情況下不會自行啟動等待：

- **遠端控制和代理團隊隊友工作階段** ：該終端上的人仍然可以啟動一個。
- **重設超過 24 小時** ：每週限制可能在數天後重設。
- **您執行該系列外的模型時的 Opus 或 Sonnet 限制** ：您的下一回合可能不會達到該限制。[`opusplan`](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting) 和其他在受限系列上執行計畫模式的模型設定不會獲得此例外。

在這些情況下，以及每當自動繼續關閉時，當您在自己的終端達到限制時，Claude Code 會在每個重設視窗中開啟一次使用量限制選項菜單。選擇以 **Wait here, then continue automatically** 開頭的列以啟動等待。在 [遠端控制](https://code.claude.com/docs/zh-TW/remote-control) 或 [代理團隊](https://code.claude.com/docs/zh-TW/agent-teams) 隊友工作階段中，自行執行 `/rate-limit-options` 以開啟菜單。 Claude Code 在以下情況下根本不提供等待：

- **背景工作階段和`-p` 執行**：菜單列不可用。
- **API 金鑰、雲端提供者和按使用量計費** ：那裡的使用量按請求計量，因此沒有重設可等待。
- **沒有已儲存 claude.ai 登入的[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway#subscriptions-and-gateways)**：Claude Code 只在已儲存的 claude.ai 登入是作用中認證時提供等待。

### 關閉自動繼續

在 `/config` 中，關閉 **Continue automatically at usage limit** ，或在您的使用者設定中將 [`autoContinueAtUsageLimit`](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit) 設定為 `false`。`/config autoContinueAtUsageLimit=false` 也有效，包括使用 `-p`，但 `key=value` 形式無法將其重新開啟，因為該設定授予無人值守執行。Claude Code 為此金鑰讀取的設定檔在 [設定參考](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit) 中。

## PR 審查狀態

在具有開放拉取請求的分支上工作時，Claude Code 會在頁腳中顯示可點擊的 PR 連結，例如「PR #446」。該連結具有彩色底線，指示審查狀態：

- 綠色：已批准
- 黃色：待審查
- 紅色：要求變更
- 灰色：草稿

拉取請求合併或關閉後，徽章會消失。 `Cmd+click`（macOS）或 `Ctrl+click`（Windows/Linux）該連結以在瀏覽器中開啟拉取請求。 狀態會在 `git push` 或更改拉取請求的 `gh pr` 命令（例如 `gh pr create` 或 `gh pr merge`）在工作階段中成功後立即重新整理。 Claude Code 會將徽章呈現為超連結，即使它無法在您的終端中偵測到超連結支援，這在 SSH 或 tmux 中很常見。設定 [`FORCE_HYPERLINK=0`](https://code.claude.com/docs/zh-TW/env-vars) 以將徽章呈現為純文字。 當您設定 [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/zh-TW/env-vars) 時，Claude Code 不會檢查拉取請求或合併請求狀態。 GitHub 儲存庫的 PR 狀態需要 GitHub 權杖。Claude Code 根據遠端的主機尋找一個：

- **github.com** ：`GH_TOKEN` 或 `GITHUB_TOKEN`，或由 `gh auth login` 儲存的權杖。沒有權杖時，當未安裝 `gh` CLI 時，頁腳會顯示 `install gh for PR status`，或當已安裝時顯示 `gh auth login for PR status`
- **設定為`GH_HOST` 的 GitHub Enterprise 主機**：`GH_ENTERPRISE_TOKEN` 或 `GITHUB_ENTERPRISE_TOKEN`，或由 `gh auth login --hostname <host>` 儲存的權杖。沒有權杖時，頁腳會顯示相同的提示
- **任何其他 GitHub 主機** ：由 `gh auth login --hostname <host>` 儲存的權杖。沒有權杖時，Claude Code 不會顯示徽章和提示

### GitLab 合併請求

當您在具有開放 GitLab 合併請求的分支上工作時，Claude Code 會在頁腳位置顯示可點擊的 `MR !N` 徽章，該位置通常保留給 GitHub PR 連結。`!N` 是 GitLab 自己的合併請求編號 N 的參考語法。彩色底線顯示合併請求的狀態：

- 綠色：GitLab 報告合併請求可合併
- 黃色：任何其他開放狀態
- 灰色：草稿

合併請求合併或關閉後，徽章會消失。 它會在 `git push` 或更改合併請求的 `glab mr` 命令（例如 `glab mr create` 或 `glab mr merge`）在工作階段中成功後立即重新整理。 若要取得徽章，您需要：

- Claude Code v2.1.234 或更新版本
- 指向您的 GitLab 主機的儲存庫遠端，可以是 gitlab.com 或自管理執行個體
- 您 `PATH` 上的 [`glab` CLI](https://gitlab.com/gitlab-org/cli)，已使用 `glab auth login` 進行驗證

Claude Code 在檢查狀態時會忽略 `glab` 的權杖環境變數（例如 `GITLAB_TOKEN`），因此您無法從單獨匯出的權杖取得徽章。Claude Code 也會在每個工作階段中尋找 `glab` 及其登入一次，因此在安裝 `glab` 或執行 `glab auth login` 後請重新啟動 Claude Code。

## 問題參考連結

當 Claude 提及問題時使用 `owner/repo#123` 的格式，只要您的終端機支援超連結，您就可以點擊該參考來開啟它。如果 Claude Code 未偵測到您的終端機支援超連結，請將 [`FORCE_HYPERLINK`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 以開啟連結，或設定為 `0` 以保持參考為純文字。 您只能取得兩部分 `owner/repo#123` 格式的連結。以下這些會保持為純文字：

- 單獨的 `#123`
- 巢狀的 GitLab 路徑，例如 `group/subgroup/project#123`
- 程式碼跨度或程式碼區塊內的任何參考

Claude Code 會根據從您的 git remote 識別出的儲存庫主機來建立連結，而不是根據參考所命名的儲存庫：

| 您的儲存庫主機                                           | `owner/repo#123` 連結到                      |
| -------------------------------------------------------- | -------------------------------------------- |
| github.com、GitHub Enterprise 主機或下方未列出的任何主機 | `https://<host>/owner/repo/issues/123`       |
| gitlab.com                                               | `https://gitlab.com/owner/repo/-/issues/123` |
| bitbucket.org、codeberg.org 或 gitea.com                 | 無連結；參考保持為純文字                     |

## 另請參閱

- [Skills](https://code.claude.com/docs/zh-TW/skills) - 自訂提示和工作流程
- [Checkpointing](https://code.claude.com/docs/zh-TW/checkpointing) - 回溯 Claude 的編輯並恢復先前的狀態
- [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference) - 命令列旗標和選項
- [設定](https://code.claude.com/docs/zh-TW/settings) - 配置選項
- [記憶體管理](https://code.claude.com/docs/zh-TW/memory) - 管理 CLAUDE.md 檔案

是否 助手
