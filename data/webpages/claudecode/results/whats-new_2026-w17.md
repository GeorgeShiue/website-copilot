版本 [v2.1.114 → v2.1.119](https://code.claude.com/docs/en/changelog#2-1-114)4 項功能 · 4 月 20–24 日 /ultrareview研究預覽版 現已推出公開研究預覽版。Ultrareview 在雲端針對您的分支或 PR 運行一群漏洞獵捕代理，發現結果會自動回傳到 CLI 或桌面應用。在合併關鍵變更（例如身份驗證或資料遷移）之前執行此操作。 檢查您目前所在的分支： Claude Code

```
> /ultrareview

```

或指向 PR： Claude Code

```
> /ultrareview 1234

```

[Ultrareview 指南](https://code.claude.com/docs/zh-TW/ultrareview) 會話摘要CLI 將焦點轉移到其他地方，然後返回會話時，會看到一行摘要說明您離開期間發生的情況。在同時運行多個 Claude 會話時，有助於保持工作流程順暢。 按需生成摘要，或從 `/config` 關閉自動摘要： Claude Code

```
> /recap

```

[互動模式：會話摘要](https://code.claude.com/docs/zh-TW/interactive-mode#session-recap) 自訂主題v2.1.118 從 `/theme` 構建和切換命名色彩主題，或在 `~/.claude/themes/` 中手動編輯 JSON 檔案。每個主題選擇一個基礎預設，並僅覆蓋您關心的令牌。插件也可以提供主題。 開啟主題選擇器並建立新主題： Claude Code

```
> /theme

```

[終端設定：建立自訂主題](https://code.claude.com/docs/zh-TW/terminal-config#create-a-custom-theme) 網頁版 Claude Codeweb [claude.ai/code](https://claude.ai/code) 的新外觀與重新設計的桌面應用相符：會話側邊欄、拖放佈局和更新的例行工作檢視。關鍵部分已重新構建，以提供更快的回應速度和更可靠的體驗。

![網頁版 Claude Code 重新設計概覽：新 UI、速度和可靠性、跨網頁、行動和 CLI 工作](https://mintcdn.com/claude-code/FTi4SBJ9YRs7d-5X/images/whats-new/web-redesign.jpeg?fit=max&auto=format&n=FTi4SBJ9YRs7d-5X&q=85&s=a2aca1b49e295b7337f5779038db8e2c)
> # Image-1
>
> **圖片摘要：**
> Claude Code 網頁版更新頁列出新介面、速度可靠性及跨平台工作三項內容。
>
> **主要元素：**
> 1. 實體: Claude Code產品, 網頁程式開發, 使用者介面, 速度與可靠性, 跨平台工作
> 2. OCR文字: What's new in
> Claude Code on the web
> 1/
> New UI
> 2/
> Speed and reliability
> 3/
> Work across web, mobile, & CLI
> claude.ai/code
> 3. 主題標籤: Claude Code, 網頁開發, 使用者介面, 速度與可靠性, 跨平台工作
>
> **頁面關聯：**
> Claude Code 更新頁，錨點 claude.ai/code
[網頁版 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 其他亮點 [Vim 視覺模式](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode)：在提示輸入中按 `v` 進行字元選擇或按 `V` 進行行選擇，並提供運算子和視覺回饋 Hooks 現在可以透過 [`type: “mcp_tool”`](https://code.claude.com/docs/zh-TW/hooks#mcp-tool-hook-fields) 直接呼叫 MCP 工具，因此 hook 可以連接到已連接的伺服器，而無需生成進程 `/cost` 和 `/stats` 已合併到 [`/usage`](https://code.claude.com/docs/zh-TW/commands)；舊名稱仍可作為打字快捷方式使用，以開啟相關標籤 `/config` 變更（主題、編輯器模式、詳細資訊等）現在會保存到 `~/.claude/settings.json`，並遵循與其他 [設定](https://code.claude.com/docs/zh-TW/settings) 相同的專案/本機/原則優先順序 [分叉的子代理](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)可以在外部構建上啟用，使用 `CLAUDE_CODE_FORK_SUBAGENT=1`：分叉會繼承您的完整對話內容，而不是從頭開始 Pro 和 Max 訂閱者在 Opus 4.6 和 Sonnet 4.6 上的預設 [努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level) 現在是 `high`（之前是 `medium`） 原生 macOS 和 Linux 構建用嵌入式 `bfs` 和 `ugrep`（可透過 Bash 使用）取代 `Glob` 和 `Grep` 工具，以加快搜尋速度，無需單獨的工具往返 `—from-pr` 現在除了接受 github.com 外，還接受 GitLab 合併請求、Bitbucket 拉取請求和 GitHub Enterprise PR URL 自動模式：在 [`autoMode.allow`、`soft_deny` 或 `environment`](https://code.claude.com/docs/zh-TW/auto-mode-config) 中包含 `“$defaults”`，以在內建清單旁邊新增自訂規則，而不是取代它 新的 [`claude plugin tag`](https://code.claude.com/docs/zh-TW/plugin-dependencies#tag-plugin-releases-for-version-resolution) 命令為插件建立版本驗證的發佈 git 標籤 Opus 4.7 會話現在針對模型的原生 1M 內容視窗進行計算，修復了膨脹的 `/context` 百分比和過早的自動壓縮 `/resume` 在大型會話上的速度提高了 67%，現在在重新讀取之前提供摘要陳舊的大型會話的選項 [v2.1.114–v2.1.119 的完整變更日誌 →](https://code.claude.com/docs/en/changelog#2-1-114) 是否 助手