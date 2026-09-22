發佈版本 [v2.1.83 → v2.1.85](https://code.claude.com/docs/en/changelog#2-1-83)6 項功能 · 3 月 23–27 日 自動模式研究預覽 自動模式將您的權限提示交給分類器。安全的編輯和命令無需中斷您即可執行；任何破壞性或可疑的操作都會被阻止並顯示。這是批准每個檔案寫入和使用 `—dangerously-skip-permissions` 執行之間的折衷方案。

![Claude Code 提示頁尾顯示黃色的'自動模式開啟 Shift+Tab 切換'指示器](https://mintcdn.com/claude-code/CfffsX01JHFnIKvD/images/whats-new/auto-mode.png?fit=max&auto=format&n=CfffsX01JHFnIKvD&q=85&s=367c9e9d4ba5bc57ec4b935154bf1fbb)
> # Image-1
>
> **圖片摘要：**
> 命令列介面顯示提示輸入區與自動模式狀態，底部標示 Shift+Tab 切換。
>
> **主要元素：**
> 1. 實體: 命令列介面, 提示輸入區, 模式狀態提示, 鍵盤快捷鍵
> 2. OCR文字:
> › Type your prompt...
> » auto mode on (shift+tab to cycle)
> 3. 主題標籤: 命令列介面, 提示詞輸入, 模式切換
>
> **頁面關聯：**
> 命令列介面頁面；錨點：auto mode on
使用 Shift+Tab 切換到自動模式，或將其設定為預設值： ~/.claude/settings.json

```
{
  "permissions": {
    "defaultMode": "auto"
  }
}

```

[權限模式指南](https://code.claude.com/docs/zh-TW/permission-modes) 電腦使用Desktop Claude 現在可以從 Claude Code Desktop 應用程式控制您的實際桌面：開啟原生應用程式、點擊 iOS 模擬器、驅動硬體控制面板，以及驗證螢幕上的變更。預設為關閉，並在每個操作前詢問。最適合用於其他方法無法達到的事項：沒有 API 的應用程式、專有工具、任何只以 GUI 形式存在的東西。

![Claude Desktop 設定，已啟用'電腦使用'切換，顯示允許 Claude 在您允許的應用程式中進行螢幕截圖並控制鍵盤和滑鼠的選項](https://mintcdn.com/claude-code/CfffsX01JHFnIKvD/images/whats-new/computer-use.png?fit=max&auto=format&n=CfffsX01JHFnIKvD&q=85&s=d631de2017edafff463505f8ddbc0f51)
> # Image-2
>
> **圖片摘要：**
> Claude 設定頁顯示電腦操作、應用程式隱藏與拒絕應用程式設定。
>
> **主要元素：**
> 1. 實體: Claude 電腦操作權限,螢幕截圖,鍵盤與滑鼠控制,應用程式隱藏,拒絕應用程式
> 2. OCR文字:
> Chat
> Cowork
> Code
> General
> Account
> Privacy
> Billing
> Usage
> Capabilities
> Connectors
> Claude Code
> Cowork
> Claude will browse and interact with any website in
> Chrome without asking. Applies to new sessions. This
> setting can put your data at risk. Learn more
> Computer use
> Let Claude take screenshots and control your keyboard
> and mouse in apps you allow. Learn more
> Unhide apps when Claude finishes
> Apps hidden during a task are restored when Claude
> stops.
> Denied apps
> Any request Claude makes to access these apps is
> automatically rejected. Claude may still affect them.
> Add app
> LH
> 3. 主題標籤: Claude,Computer use,電腦操作,應用程式權限,隱私設定
>
> **頁面關聯：**
> Claude 設定頁，Computer use 與 Denied apps 權限設定
在設定中啟用它，授予作業系統權限，然後要求 Claude 端對端驗證變更： Claude Code

```
Open the iOS simulator, tap through the onboarding flow, and screenshot each step

```

[電腦使用指南](https://code.claude.com/docs/zh-TW/desktop#let-claude-use-your-computer) PR 自動修復Web 開啟 PR 時翻轉開關並離開。Claude 監視 CI、修復失敗、處理細節，並推送直到變綠。不再需要透過六輪 lint 錯誤來監督 PR。

![Claude Code 網頁 CI 面板顯示已啟用'自動修復'切換，描述為'主動修復 CI 失敗和審查評論'](https://mintcdn.com/claude-code/CfffsX01JHFnIKvD/images/whats-new/auto-fix.png?fit=max&auto=format&n=CfffsX01JHFnIKvD&q=85&s=c62b181c6c5d96929f0b43525f9f3584)
> # Image-3
>
> **圖片摘要：**
> 自動修復與自動合併設定介面，顯示 CI 檢查與審查留言選項。
>
> **主要元素：**
> 1. 實體: 自動修復功能,自動合併功能,持續整合檢查,程式碼審查,AI 助理
> 2. OCR文字: Auto fix
> Proactively fix CI failures and review
> comments. Claude may post comments
> on your behalf
> Auto merge
> Merge once required checks pass.
> +2 -2
> CI
> View PR
> 3. 主題標籤: Auto fix,Auto merge,CI,Pull request
>
> **頁面關聯：**
> Claude 自動修復與 Pull request 設定介面
在 Claude Code 網頁上建立 PR 後，在 CI 面板中切換「自動修復」。 [自動修復提取請求](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests) 文字稿搜尋v2.1.83 在文字稿模式中按 `/` 搜尋您的對話。`n` 和 `N` 逐步瀏覽符合項目。最後有辦法找到 Claude 在 400 條訊息前執行的那個 Bash 命令。 開啟文字稿模式並搜尋： Claude Code

```
Ctrl+O    # open transcript
/migrate  # search for "migrate"
n         # next match
N         # previous match

```

[全螢幕指南](https://code.claude.com/docs/zh-TW/fullscreen#search-and-review-the-conversation) PowerShell 工具previewv2.1.84 Windows 獲得了與 Bash 並行的原生 PowerShell 工具。Claude 可以執行 cmdlet、管道物件，以及使用 Windows 原生路徑，無需透過 Git Bash 翻譯所有內容。 從設定中選擇加入： .claude/settings.json

```
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}

```

[PowerShell 工具文件](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool) 條件式 hooksv2.1.85 Hooks 現在可以使用權限規則語法宣告 `if` 欄位。您的 pre-commit 檢查只會針對 `Bash(git commit *)` 生成，而不是每個 bash 呼叫，減少繁忙工作階段中的程序開銷。 將 hook 限制為僅 git 提交： .claude/settings.json

```
{
  "hooks": {
    "PreToolUse": [{
      "hooks": [{
        "if": "Bash(git commit *)",
        "type": "command",
        "command": ".claude/hooks/lint-staged.sh"
      }]
    }]
  }
}

```

[Hooks 參考](https://code.claude.com/docs/zh-TW/hooks) 其他成果 Plugin `userConfig` 現已公開：在啟用時提示設定、鑰匙圈支援的祕密 貼上的影像插入 `[Image #N]` 晶片，您可以按位置參考 `managed-settings.d/` 分層原則片段的放置目錄 `CwdChanged` 和 `FileChanged` hook 事件用於 direnv 風格的設定 代理程式可以在 frontmatter 中宣告 `initialPrompt` 以自動提交第一個回合 `Ctrl+X Ctrl+E` 開啟您的外部編輯器，符合 readline 在任何回應前中斷會自動恢復您的輸入 `/status` 現在在 Claude 回應時也能運作 深層連結在您偏好的終端中開啟，而不是首次偵測到的 閒置返回提示在離開 75 分鐘以上後執行 `/clear` VS Code：速率限制橫幅、Esc 兩次倒帶選擇器 [v2.1.83–v2.1.85 的完整變更日誌 →](https://code.claude.com/docs/en/changelog#2-1-83) 是否 助手