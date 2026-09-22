版本 [v2.1.139 → v2.1.142](https://code.claude.com/docs/en/changelog#2-1-139)3 項功能 · 5 月 11–15 Agent viewresearch preview `claude agents` 為每個 Claude Code 工作階段開啟一個螢幕：什麼正在執行、什麼在等待您的輸入，以及什麼已完成。分派一個錯誤修復、一個拉取請求審查和一個不穩定測試調查作為三行，在另一個視窗中繼續工作，只在一行需要您時才介入。附加到任何一行以進入其完整對話，然後按 `←` 返回列表。每個背景工作階段在沒有終端連接的情況下繼續執行。 從您的 shell 開啟儀表板： terminal

```
claude agents

```

[Agent view](https://code.claude.com/docs/zh-TW/agent-view) /goalv2.1.139 設定完成條件，Claude 會在多個回合中持續朝著它工作，無需您提示每一步。在每個回合之後，一個快速模型檢查條件是否成立；如果不成立，Claude 會開始另一個回合，而不是將控制權交回。適用於具有可驗證終止狀態的大量工作，例如遷移模組直到每個呼叫位置都編譯並通過測試。目標在條件滿足後清除，並在互動、`-p` 和 Remote Control 中工作。 設定目標並讓 Claude 執行直到它成立： Claude Code

```
> /goal all tests in test/auth pass and the lint step is clean

```

[Goals](https://code.claude.com/docs/zh-TW/goal) Fast mode on Opus 4.7research preview `/fast` 現在預設在 Opus 4.7 上執行，而不是 Opus 4.6。快速模式是高速 Opus 配置：相同的模型品質，速度約快 2.5 倍，但每個 token 成本更高，適用於快速迭代和即時除錯。定價保持不變，為 30/30/30/150 per MTok，與 Opus 4.6 快速模式相同。要將快速模式固定到 Opus 4.6，請設定 `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1`。

![Claude Code 模型選擇器顯示 Opus 4.7 Fast 1M 作為預設值，並啟用了 Fast 切換](https://mintcdn.com/claude-code/ITvjicPxe1SM3GX7/images/whats-new/fast-mode-opus-47.png?fit=max&auto=format&n=ITvjicPxe1SM3GX7&q=85&s=6b6d92f7748ce5328a1ee9a269fb1a87)
> # Image-1
>
> **圖片摘要：**
> 像素橘色動物戴紫色帽子，位於 Models 模型選單上方；選單列出四個模型與 Fast 開關。
>
> **主要元素：**
> 1. 實體: 像素橘色動物, 紫色尖帽, 模型選單, 模型清單, Fast 開關
> 2. OCR文字:
> Models
> ⇧ ⌘ |
> Opus 4.7 Fast 1M · Default ✓
> Opus 4.7 1M 1
> Opus 4.6 2
> Sonnet 4.6 3
> Sonnet 4.6 1M 4
> Fast
> 3. 主題標籤: 模型選擇, Opus, Sonnet, Fast
>
> **頁面關聯：**
> Models 模型選單，包含 Opus 與 Sonnet 模型清單
切換快速模式，現在在 Opus 4.7 上執行： Claude Code

```
> /fast

```

[Fast mode on Opus 4.7](https://code.claude.com/docs/zh-TW/fast-mode#understand-the-cost-tradeoff) 其他成果 `claude agents` 獲得了分派標誌（`—add-dir`、`—settings`、`—mcp-config`、`—plugin-dir`、`—permission-mode`、`—model`、`—effort`、`—dangerously-skip-permissions`）來配置背景工作階段，`claude agents —cwd <path>` 將工作階段列表限制在一個目錄 新的 hook `args: string[]` exec 形式直接生成命令而不使用 shell，因此路徑佔位符永遠不需要引用 新的 `continueOnBlock` 配置選項用於 `PostToolUse` hooks，將 hook 的拒絕原因反饋給 Claude 並繼續回合，而不是結束它 hook JSON 輸出中的新 `terminalSequence` 欄位讓 hooks 發出桌面通知、視窗標題和鈴聲，無需控制終端 Rewind 菜單新增了「在此處總結」以壓縮較早的上下文，同時保持最近的回合完整 當設定 `ANTHROPIC_API_KEY`、`apiKeyHelper` 或 `ANTHROPIC_AUTH_TOKEN` 時，Remote Control、`/schedule`、Claude.ai MCP 連接器和通知偏好設定現在被禁用，即使與 Claude.ai 登入並行；取消設定 API 金鑰以使用這些功能 MCP stdio 伺服器現在在其環境中接收 `CLAUDE_PROJECT_DIR`，與 hooks 相符，plugin 配置可以在命令中參考 `${CLAUDE_PROJECT_DIR}` `claude plugin details <name>` 顯示 plugin 的元件清單和預計的每個工作階段 token 成本，`/plugin` 詳細資訊窗格現在也列出 plugin 提供的 LSP 伺服器 具有根級 `SKILL.md` 且沒有 `skills/` 子目錄的 Plugins 現在被呈現為一個 skill `/feedback` 現在可以包含過去 24 小時或 7 天內的最近工作階段，用於跨越超過當前工作階段的問題 Agent tool `subagent_type` 現在不區分大小寫和分隔符地匹配，因此 `“Code Reviewer”` 解析為 `code-reviewer` [v2.1.139–v2.1.142 的完整變更日誌 →](https://code.claude.com/docs/en/changelog#2-1-139) 是否 助手