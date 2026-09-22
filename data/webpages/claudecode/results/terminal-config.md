Claude Code 可在任何終端機中無需設定即可運作。此頁面適用於當某些特定功能的行為不符合您的預期時。在下方找到您的症狀。如果一切已經感覺正確，您不需要此頁面。

- [Shift+Enter 提交而非插入新行](https://code.claude.com/docs/zh-TW/terminal-config#enter-multiline-prompts)
- [macOS 上的 Option 鍵快捷鍵無法運作](https://code.claude.com/docs/zh-TW/terminal-config#enable-option-key-shortcuts-on-macos)
- [Claude 完成時沒有聲音或警示](https://code.claude.com/docs/zh-TW/terminal-config#get-a-terminal-bell-or-notification)
- [您在 tmux 內執行 Claude Code](https://code.claude.com/docs/zh-TW/terminal-config#configure-tmux)
- [Windows 上的 Backspace 刪除整個單字](https://code.claude.com/docs/zh-TW/terminal-config#fix-backspace-deleting-a-whole-word-on-windows)
- [顯示閃爍或回捲跳躍](https://code.claude.com/docs/zh-TW/terminal-config#switch-to-fullscreen-rendering)
- [您想在提示中使用 Vim 快捷鍵](https://code.claude.com/docs/zh-TW/terminal-config#edit-prompts-with-vim-keybindings)

此頁面是關於讓您的終端機向 Claude Code 傳送正確的訊號。若要變更 Claude Code 本身回應的快捷鍵，請改為參閱 [快捷鍵](https://code.claude.com/docs/zh-TW/keybindings)。

## 輸入多行提示

按 Enter 鍵提交您的訊息。若要在不提交的情況下新增換行符，請按 Ctrl+J，或輸入 `\` 然後按 Enter。兩種方法在每個終端機上都可以使用，無需設定。 在大多數終端機中，您也可以按 Shift+Enter，但支援情況因終端機模擬器而異：

| 終端機                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Shift+Enter 用於換行                                   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Ghostty、Kitty、iTerm2、WezTerm、Warp、Apple Terminal、Windows Terminal                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 無需設定即可使用                                       |
| 支援 kitty 鍵盤協議的其他終端機，例如 foot 和 Alacritty 0.16 或更新版本                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 無需設定即可使用。需要 Claude Code v2.1.269 或更新版本 |
| VS Code、Cursor、Devin Desktop、Alacritty 0.16 之前的版本、Zed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 執行一次 `/terminal-setup`                             |
| gnome-terminal、JetBrains IDE（例如 PyCharm 和 Android Studio）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 不可用；使用 Ctrl+J 或 `\` 然後 Enter                  |
| 對於 VS Code、Cursor、Devin Desktop、Alacritty 0.16 之前的版本和 Zed，`/terminal-setup` 會將 Shift+Enter 快捷鍵寫入終端機的設定檔。在首次執行時，您會看到確認訊息，例如 `Installed VSCode terminal Shift+Enter key binding`。現有的快捷鍵設定會保留；如果您看到類似 `VSCode terminal Shift+Enter key binding already configured` 的訊息，表示未進行任何變更。請直接在主機終端機中執行 `/terminal-setup`，而不是在 tmux 或 screen 內執行，因為它需要寫入主機終端機的設定。 在 VS Code、Cursor 和 Devin Desktop 中，`/terminal-setup` 也會更新兩個編輯器設定：它將 `terminal.integrated.gpuAcceleration` 設定為 `"off"` 以防止整合終端機中的文字亂碼，並設定 `terminal.integrated.mouseWheelScrollSensitivity` 以在[全螢幕模式](https://code.claude.com/docs/zh-TW/fullscreen)中實現更平順的捲動。若要復原 GPU 加速變更，請將其設回 `"auto"` 並重新載入編輯器視窗。 在 Zed 中，`/terminal-setup` 會就地更新您的 `keymap.json`： |                                                        |

- 如果 keymap 已有快捷鍵設定，且其中沒有 Terminal `shift-enter`，Claude Code 會先將其備份到同一目錄中的副本（例如 `keymap.json.1a2b3c4d.bak`），然後將 Shift+Enter 快捷鍵合併到您的 keymap 中，保留您的其他快捷鍵和註解
- 如果 Claude Code 無法讀取或解析 keymap、無法備份，或無法驗證合併結果，它會[保持檔案不變並列印快捷鍵區塊供您自行新增](https://code.claude.com/docs/zh-TW/errors#terminal-setup-left-your-zed-keymap-unchanged)

如果您在 tmux 內執行，即使外部終端機支援，Shift+Enter 也需要下方的 [tmux 設定](https://code.claude.com/docs/zh-TW/terminal-config#configure-tmux)。 若要將換行符綁定到不同的按鍵，或交換行為使 Enter 插入換行符而 Shift+Enter 提交，請在您的[快捷鍵檔案](https://code.claude.com/docs/zh-TW/keybindings)中對應 `chat:newline` 和 `chat:submit` 動作。

## 在 macOS 上啟用 Option 鍵快捷鍵

某些 Claude Code 快捷鍵使用 Option 鍵，例如 Option+Enter 用於換行或 Option+P 用於切換模型。在 macOS 上，大多數終端機預設不會將 Option 作為修飾鍵發送，因此這些快捷鍵在啟用之前不會執行任何操作。終端機的此設定通常標記為「使用 Option 作為 Meta 鍵」；Meta 是現在標記為 Option 或 Alt 的鍵的歷史 Unix 名稱。

- Apple Terminal
- iTerm2
- VS Code

開啟「設定」→「描述檔」→「鍵盤」，並勾選「使用 Option 作為 Meta 鍵」。如果您接受了 Claude Code 的首次執行終端機設定提示，這已經完成。該提示會為您執行 `/terminal-setup`，它會啟用 Option 作為 Meta 並在您的 Apple Terminal 描述檔中關閉可聽見的鈴聲。在[螢幕閱讀器模式](https://code.claude.com/docs/zh-TW/accessibility)中，`/terminal-setup` 保持鈴聲設定不變，以便終端機鈴聲保持可聽見。在 v2.1.211 之前，`/terminal-setup` 即使在螢幕閱讀器模式中也會關閉鈴聲。如果較早的執行關閉了鈴聲，請在「設定」→「描述檔」→「進階」→「可聽見的鈴聲」下重新開啟。 開啟「設定」→「描述檔」→「按鍵」→「一般」，並將「左 Option 鍵」和「右 Option 鍵」設定為「Esc+」。在 iTerm2 中執行 `/terminal-setup` 會在「設定」→「一般」→「選取」下啟用「終端機中的應用程式可以存取剪貼簿」，以便 `/copy` 命令可以寫入您的系統剪貼簿。該命令即使在 tmux 內執行時也能偵測 iTerm2。重新啟動 iTerm2 以使變更生效。 將 `"terminal.integrated.macOptionIsMeta": true` 新增至您的 VS Code 設定。 對於 Ghostty、Kitty 和其他終端機，請在終端機的設定檔中尋找 Option-as-Alt 或 Option-as-Meta 設定。

## 取得終端機鈴聲或通知

當 Claude 完成任務或暫停以等待權限提示，且您似乎不在終端機前時，它會觸發通知事件。請參閱[各通知類型何時觸發](https://code.claude.com/docs/zh-TW/hooks#notification)以了解確切的時機。將此顯示為終端機鈴聲或桌面通知可讓您在長時間任務執行時切換到其他工作。 根據預設，Claude Code 僅在 Ghostty、Kitty 和 iTerm2 中傳送桌面通知。在其他終端機中，將 [`preferredNotifChannel`](https://code.claude.com/docs/zh-TW/settings-reference#preferrednotifchannel) 設定為 `"terminal_bell"` 以改為響起終端機鈴聲，或設定[通知 hook](https://code.claude.com/docs/zh-TW/terminal-config#play-a-sound-with-a-notification-hook) 以取得自訂音效或命令。下列設定項目會開啟終端機鈴聲： ~/.claude/settings.json

```
{
  "preferredNotifChannel": "terminal_bell"
}

```

桌面通知透過 SSH 到達您的本機，因此遠端工作階段仍可提醒您。Ghostty 和 Kitty 會將其轉發到您的作業系統通知中心，無需進一步設定。iTerm2 需要您啟用轉發： 1 開啟 iTerm2 通知設定 前往 Settings → Profiles → Terminal。 2 啟用警示 勾選「Notification Center Alerts」，然後按一下「Filter Alerts」並啟用「Send escape sequence-generated alerts」。 如果通知仍未出現，請確認您的終端機應用程式在作業系統設定中具有通知權限，且如果您在 tmux 內執行，請[啟用傳遞](https://code.claude.com/docs/zh-TW/terminal-config#configure-tmux)。

### 使用通知 hook 播放音效

在任何終端機中，您可以設定[通知 hook](https://code.claude.com/docs/zh-TW/hooks-guide#get-notified-when-claude-needs-input) 以在 Claude 需要您注意時播放音效或執行自訂命令。Hook 與內建通知一起執行，而不是取代它，因此不會收到桌面通知的終端機（例如 Warp 或 VS Code 整合終端機）可以使用 hook 或改為將 `preferredNotifChannel` 設定為 `"terminal_bell"`。 下列範例在 macOS 上播放系統音效。連結的指南包含 macOS、Linux 和 Windows 的桌面通知命令。 ~/.claude/settings.json

```
{
  "hooks": {
    "Notification": [
      {
        "hooks": [{ "type": "command", "command": "afplay /System/Library/Sounds/Glass.aiff" }]
      }
    ]
  }
}

```

## 設定 tmux

當 Claude Code 在 tmux 內執行時，預設會發生兩個問題：Shift+Enter 會提交而不是插入新行，且桌面通知和[進度列](https://code.claude.com/docs/zh-TW/settings-reference#terminalprogressbarenabled)永遠無法到達外層終端。將這些行新增到 `~/.tmux.conf`，然後執行 `tmux source-file ~/.tmux.conf` 以將其套用到執行中的伺服器： ~/.tmux.conf

```
set -g allow-passthrough on
set -s extended-keys on
set -as terminal-features 'xterm*:extkeys'

```

`allow-passthrough` 行讓通知和進度更新到達外層終端，而不是被 tmux 吞沒。`extended-keys` 行讓 tmux 區分 Shift+Enter 和純 Enter，以便換行快捷鍵能夠運作。

## 修復 Windows 上 Backspace 刪除整個單詞的問題

在 Windows 上，Claude Code 將到達的 Backspace 讀取為 `^H` 時會將其解釋為 Ctrl+Backspace，這會[刪除前一個單詞](https://code.claude.com/docs/zh-TW/interactive-mode#text-editing)，除非 `TERM_PROGRAM` 是 `mintty` 或 `TERM` 是 `cygwin`。在 macOS 和 Linux 上，Claude Code 將其讀取為純 Backspace。 如果每次按下 Backspace 都會刪除整個單詞，表示您的終端機為純 Backspace 發送 `^H`。設定 [`CLAUDE_CODE_BS_AS_CTRL_BACKSPACE=0`](https://code.claude.com/docs/zh-TW/env-vars)。Backspace 和 Ctrl+H 隨後將各刪除一個字元。如果在 macOS 或 Linux 上 Ctrl+Backspace 只刪除一個字元，因為您的終端機為其發送 `^H`，請改為將變數設定為 `1`。

## 配對色彩主題

使用 `/theme` 指令，或在 `/config` 中的主題選擇器，選擇與您的終端機相符的 Claude Code 主題。選擇自動選項會偵測您終端機的淺色或深色背景，因此主題會在您的終端機跟隨作業系統外觀變更時隨之改變。Claude Code 不會控制終端機本身的色彩配置，該配置由終端機應用程式設定。 若要自訂介面底部顯示的內容，請設定一個[自訂狀態列](https://code.claude.com/docs/zh-TW/statusline)，顯示目前的模型、工作目錄、Git 分支或其他內容。

### 建立自訂主題

除了內建預設值外，`/theme` 會列出您已定義的任何自訂主題，以及由已安裝的[外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#themes)貢獻的任何主題。選擇清單末尾的\*\*新增自訂主題…\*\*以互動方式建立一個：您命名主題，然後選擇要覆寫的個別色彩權杖。當自訂主題被反白顯示時，按 `Ctrl+E` 以編輯它。 每個自訂主題都是 `~/.claude/themes/` 中的 JSON 檔案。不含 `.json` 副檔名的檔案名稱是主題的 slug，選擇主題會將 `custom:<slug>` 儲存為您的主題偏好設定。該檔案有三個選用欄位：

| 欄位                                                                                                                                                                                                                                                                                                 | 類型   | 說明                                                                                                                     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------ |
| `name`                                                                                                                                                                                                                                                                                               | string | 在 `/theme` 中顯示的標籤。預設為檔案名稱 slug                                                                            |
| `base`                                                                                                                                                                                                                                                                                               | string | 主題開始的內建預設值：`dark`、`light`、`dark-daltonized`、`light-daltonized`、`dark-ansi` 或 `light-ansi`。預設為 `dark` |
| `overrides`                                                                                                                                                                                                                                                                                          | object | 色彩權杖名稱到色彩值的對應。此處未列出的權杖會回退到基礎預設值                                                           |
| 色彩值接受 `#rrggbb`、`#rgb`、`rgb(r,g,b)`、`ansi256(n)` 或 `ansi:<name>`，其中 `<name>` 是 16 個標準 ANSI 色彩名稱之一，例如 `red` 或 `cyanBright`。未知的權杖和無效的色彩值會被忽略，因此打字錯誤無法破壞轉譯。 以下範例定義了一個保留深色預設值但重新著色提示符號重點、錯誤文字和成功文字的主題： |        |                                                                                                                          |
| ~/.claude/themes/dracula.json                                                                                                                                                                                                                                                                        |        |                                                                                                                          |

```
{
  "name": "Dracula",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "error": "#ff5555",
    "success": "#50fa7b"
  }
}

```

Claude Code 監視 `~/.claude/themes/` 並在檔案被新增或變更時重新載入，因此在您的編輯器中所做的編輯會在執行中的工作階段中套用，無需重新啟動。如果 Claude Code 啟動時 `~/.claude/themes/` 資料夾本身不存在，請在建立第一個主題檔案後重新啟動一次。之後，變更會在無需重新啟動的情況下套用。 下面的參考涵蓋了您可以在 `overrides` 中設定的權杖。`/theme` 中的互動式編輯器顯示相同的權杖，並提供即時預覽，加上一些單一用途的重點，例如此處省略的上線畫面色彩。 色彩權杖參考 以下範例結合了下列幾個群組中的權杖：品牌重點、計畫模式邊框、差異背景和訊息背景。 ~/.claude/themes/midnight.json

```
{
  "name": "Midnight",
  "base": "dark",
  "overrides": {
    "claude": "#a78bfa",
    "planMode": "#38bdf8",
    "diffAdded": "#14532d",
    "diffRemoved": "#7f1d1d",
    "userMessageBackground": "#1e1b4b"
  }
}

```

#### 文字和重點色彩

控制整個介面中使用的主要品牌重點和前景文字陰影。

| 權杖          | 控制項                                   |
| ------------- | ---------------------------------------- |
| `claude`      | 主要品牌重點，用於微調器和助理標籤       |
| `text`        | 預設前景文字                             |
| `inverseText` | 繪製在彩色背景上的文字，例如狀態徽章     |
| `inactive`    | 次要文字，例如提示、時間戳記和停用的項目 |
| `subtle`      | 淡色邊框和去強調的次要文字               |
| `suggestion`  | 自動完成建議和選擇器中的選擇反白顯示     |
| `permission`  | 對話方塊邊框，包括權限提示和選擇器       |
| `remember`    | 記憶和 `CLAUDE.md` 指示器                |

#### 狀態色彩

在訊息和指示器中發出成功、失敗和警告狀態的信號。

| 權杖      | 控制項                       |
| --------- | ---------------------------- |
| `success` | 成功訊息和通過的檢查         |
| `error`   | 錯誤訊息和失敗               |
| `warning` | 警告、注意訊息和自動模式邊框 |
| `merged`  | 合併的提取要求狀態           |

#### 輸入方塊和模式指示器

設定輸入方塊邊框色彩和在權限模式或指示器啟用時顯示的重點。

| 權杖           | 控制項                                                                                                                                                                              |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `promptBorder` | 手動模式中的輸入方塊邊框                                                                                                                                                            |
| `planMode`     | Plan Mode 重點和邊框                                                                                                                                                                |
| `autoAccept`   | 接受編輯模式重點和邊框                                                                                                                                                              |
| `bashBorder`   | 輸入 `!` shell 指令時的輸入方塊邊框                                                                                                                                                 |
| `ide`          | IDE 連線指示器                                                                                                                                                                      |
| `fastMode`     | 快速模式指示器                                                                                                                                                                      |
| `effortUltra`  | 啟用 [ultracode](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level) 時輸入方塊邊框上的 `ultracode` 標籤。您對此色彩的覆寫在 Claude Code v2.1.239 或更新版本上生效 |

#### 差異轉譯

在檔案編輯和審查中著色新增和移除的程式碼。

| 權杖                | 控制項                                   |
| ------------------- | ---------------------------------------- |
| `diffAdded`         | 新增行的背景                             |
| `diffRemoved`       | 移除行的背景                             |
| `diffAddedDimmed`   | 您拒絕編輯後顯示的淡化差異中新增行的背景 |
| `diffRemovedDimmed` | 您拒絕編輯後顯示的淡化差異中移除行的背景 |
| `diffAddedWord`     | 新增行內的字級反白顯示                   |
| `diffRemovedWord`   | 移除行內的字級反白顯示                   |

#### 全螢幕模式

Claude Code 在預設和全螢幕轉譯器中繪製 `userMessageBackground`、`bashMessageBackgroundColor` 和 `memoryBackgroundColor`。它僅在[全螢幕轉譯模式](https://code.claude.com/docs/zh-TW/fullscreen)中使用 `userMessageBackgroundHover` 和 `selectionBg`。

| 權杖                         | 控制項                                  |
| ---------------------------- | --------------------------------------- |
| `userMessageBackground`      | 文字記錄中您的訊息後面的背景            |
| `userMessageBackgroundHover` | 訊息被懸停或展開時後面的背景            |
| `bashMessageBackgroundColor` | 文字記錄中 `!` shell 指令項目後面的背景 |
| `memoryBackgroundColor`      | 文字記錄中 `#` 記憶項目後面的背景       |
| `selectionBg`                | 使用滑鼠選取的文字背景                  |

#### 使用量計量和說話者標籤

調整在 `/usage` 檢視中顯示的列，以及區分您的訊息和 Claude 訊息的標籤。

| 權杖               | 控制項                         |
| ------------------ | ------------------------------ |
| `rate_limit_fill`  | 使用量計量的填充部分           |
| `rate_limit_empty` | 使用量計量的未填充部分         |
| `briefLabelYou`    | 您訊息上 `You` 標籤的色彩      |
| `briefLabelClaude` | 助理訊息上 `Claude` 標籤的色彩 |

#### 微光變體和子代理色彩

幾個權杖有配對的微光變體，提供微調器動畫漸層中使用的較淺色彩。如果動畫看起來不相符，請與其基礎權杖一起覆寫微光。

- `claude` 和 `claudeShimmer`
- `warning` 和 `warningShimmer`
- `permission` 和 `permissionShimmer`
- `promptBorder` 和 `promptBorderShimmer`
- `inactive` 和 `inactiveShimmer`
- `fastMode` 和 `fastModeShimmer`

每個[子代理](https://code.claude.com/docs/zh-TW/sub-agents)和平行工作都以八個命名色彩之一顯示，以便您可以在文字記錄中區分它們。權杖名稱遵循 `<color>_FOR_SUBAGENTS_ONLY` 的模式，其中 `<color>` 是 `red`、`blue`、`green`、`yellow`、`purple`、`orange`、`pink` 或 `cyan`。覆寫這些以變更每個命名色彩的外觀。例如，定義中具有 `color: blue` 的子代理使用 `blue_FOR_SUBAGENTS_ONLY` 值繪製。Claude Code 在提示輸入中使用七色彩虹漸層轉譯 [`ultrathink`](https://code.claude.com/docs/zh-TW/model-config#use-ultrathink-for-one-off-deep-reasoning) 關鍵字。權杖名稱遵循 `rainbow_<color>` 和 `rainbow_<color>_shimmer` 的模式，其中 `<color>` 是 `red`、`orange`、`yellow`、`green`、`blue`、`indigo` 或 `violet`。

## 切換至全螢幕渲染

在[螢幕閱讀器模式](https://code.claude.com/docs/zh-TW/accessibility)中，本節不適用。Claude Code 始終呈現為純文字滾動，除非在附加的[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)中，如果您在任何其他工作階段中執行 `/tui fullscreen`，Claude Code 會列印說明而不是切換。 如果顯示閃爍或在 Claude 工作時捲動位置跳動，請切換至[全螢幕渲染模式](https://code.claude.com/docs/zh-TW/fullscreen)。在此模式中，您可以使用滑鼠或 PageUp 在 Claude Code 內捲動，而不是使用終端機的原生捲回；請參閱[全螢幕頁面](https://code.claude.com/docs/zh-TW/fullscreen#search-and-review-the-conversation)以了解如何搜尋和複製。 如果閃爍是唯一的問題，且您的終端機支援同步輸出但未被自動偵測，例如 Emacs `eat`，請設定 [`CLAUDE_CODE_FORCE_SYNC_OUTPUT=1`](https://code.claude.com/docs/zh-TW/env-vars) 以停止閃爍而不改變渲染器。 執行 `/tui fullscreen` 以切換並儲存偏好設定。您的對話會完整重新啟動，未來的工作階段將以全螢幕啟動，除非[全螢幕啟動失敗](https://code.claude.com/docs/zh-TW/fullscreen#fullscreen-renderer-didnt-finish-starting)。您也可以在啟動 Claude Code 之前設定 `CLAUDE_CODE_NO_FLICKER` 環境變數： Bash and Zsh PowerShell ~/.claude/settings.json

```
CLAUDE_CODE_NO_FLICKER=1 claude

```

```
$env:CLAUDE_CODE_NO_FLICKER = "1"; claude

```

```
{
  "env": {
    "CLAUDE_CODE_NO_FLICKER": "1"
  }
}

```

## 貼上大型內容

當您貼上超過 800 個字元或超過三行的內容到提示時，Claude Code 會將輸入摺疊為預留位置，例如 `[Pasted text #1 +120 lines]`，以保持輸入框可用。在短於 12 列的終端視窗中，行限制會降低，因此 Claude Code 在 11 列時會摺疊三行貼上，在 10 列或更少列時會摺疊任何多行貼上。Claude Code 在您提交時仍會傳送完整內容。 當您使用字詞或行快捷鍵（例如 `Ctrl+W` 或 `Ctrl+K`）刪除，或透過 `f`/`t` 動作（例如 `df]`）使用 vim 刪除，且刪除範圍到達預留位置內部時，Claude Code 會完全移除預留位置。您可以貼上刪除的內容來復原它，在字詞或行快捷鍵後使用 [`Ctrl+Y`](https://code.claude.com/docs/zh-TW/interactive-mode#text-editing)，或在 vim 刪除後使用 [`p` 在 NORMAL 模式中](https://code.claude.com/docs/zh-TW/interactive-mode#editing-normal-mode)。 Claude Code 將摺疊的內容保留在 `~/.claude/paste-cache/` 下，因此當您從[命令歷史](https://code.claude.com/docs/zh-TW/interactive-mode#command-history)回想提示並重新提交時，Claude Code 會再次傳送完整貼上的內容，包括在稍後的工作階段中，直到保留掃描移除快取檔案。 Claude Code 刪除早於 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 的快取檔案，遵循[保留掃描規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)，因此回想的提示可能參考不再存在的貼上文字。當您提交這樣的提示時，Claude Code 永遠不會傳送字面上的 `[Pasted text #N]` 字串，並顯示通知命名遺失的貼上：

- 在有剩�文字的純提示中，Claude Code 移除預留位置並傳送剩餘文字。
- 在[殼層模式](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)命令或 `/` 命令中，移除會改變執行的內容，以及在任何提示中移除留下空白時，Claude Code 取消提交並在輸入中保留原始文字，預留位置仍在其中。刪除預留位置或編輯命令，然後重新提交。

VS Code 整合終端可能會在非常大的貼上到達 Claude Code 之前從中丟棄字元，因此在那裡偏好檔案型工作流程。對於非常大的輸入（例如整個檔案或長日誌），將內容寫入檔案並要求 Claude 讀取它，而不是貼上。這保持對話記錄可讀，並讓 Claude 在稍後的回合中按路徑參考檔案。

## 使用 Vim 快捷鍵編輯提示詞

Claude Code 包含用於提示詞輸入的 Vim 風格編輯模式。透過 `/config` → Editor mode 啟用它，或在 `~/.claude/settings.json` 中將 [`editorMode`](https://code.claude.com/docs/zh-TW/settings-reference#editormode) 設定為 `"vim"`。將 Editor mode 設回 `normal` 以關閉它。 Vim 模式支援 NORMAL 和 VISUAL 模式動作和運算子的子集，例如 `hjkl` 導航、`v`/`V` 選擇，以及 `d`/`c`/`y` 搭配文字物件。請參閱 [Vim 編輯器模式參考](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode) 以取得完整的快捷鍵表。 Vim 動作無法透過快捷鍵檔案重新對應。若要將兩個按鍵的 INSERT 模式序列（例如 `jj`）對應到 Escape，請在使用者設定中設定 [`vimInsertModeRemaps`](https://code.claude.com/docs/zh-TW/interactive-mode#remap-insert-mode-key-sequences)。 在 INSERT 模式中按 Enter 仍會提交您的提示詞，不同於標準 Vim。在 NORMAL 模式中使用 `o` 或 `O`，或按 Ctrl+J，以插入新行。

## 相關資源

- [互動模式](https://code.claude.com/docs/zh-TW/interactive-mode)：完整鍵盤快捷鍵參考和 Vim 快捷鍵表
- [快捷鍵](https://code.claude.com/docs/zh-TW/keybindings)：重新對應任何 Claude Code 快捷鍵，包括 Enter 和 Shift+Enter
- [全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)：全螢幕模式中捲動、搜尋和複製的詳細資訊
- [Hooks 指南](https://code.claude.com/docs/zh-TW/hooks-guide)：Linux 和 Windows 的更多通知 hook 範例
- [疑難排解](https://code.claude.com/docs/zh-TW/troubleshooting)：終端機配置外部問題的修復

是否 助手
