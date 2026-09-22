這是一個提示詞庫，可複製貼上到 Claude Code 中。使用它來探索您未曾嘗試過的工作方式，或當您不確定從何開始時使用。 這些提示詞來自各種 Anthropic 指南，包括[常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)、[最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)和[Anthropic 團隊如何使用 Claude Code](https://claude.com/blog/how-anthropic-teams-use-claude-code)。它們是起點而非腳本。在任何提示詞下打開**為什麼這有效** 以查看其背後的模式，這樣您可以編寫自己的提示詞。 ★ 從這裡開始理解計畫原型建置測試重構審查引導除錯Git發佈資料自動化產品設計文件行銷安全待命清除5 提示詞 五個首先嘗試的提示詞 在新儲存庫中定位從這裡開始 · 1`give me an overview of this codebase: architecture, key directories, and how the pieces connect` 找到某事發生的位置從這裡開始 · 2`where do we validate uploaded file types?` 尋找並修復失敗的測試從這裡開始 · 3`the UserAuth test is failing, find out why and fix it` 編寫測試、執行測試、修復失敗從這裡開始 · 4`write tests for app/parsers/feed.py, run them, and fix any failures` 在提交前審查您的變更從這裡開始 · 5`review my uncommitted changes and flag anything that looks risky before I commit` 顯示全部 52 個提示詞 →

## 這些提示詞有效的原因

上述提示詞共享一些模式。識別它們有助於您將此處的任何提示詞調整為您自己的任務。 **描述結果，而不是步驟。** 說出您想要的內容，讓 Claude 找到檔案。下面的提示詞無需命名單個檔案路徑即可運作。

```
add rate limiting to the public API and make sure existing tests still pass

```

**給它一種檢查自己工作的方式。** 在同一提示詞中要求執行、測試、比較或驗證，以便 Claude 進行迭代，而不是在一次嘗試後停止。若要檢查完成的變更與執行中的應用程式，請執行 [`/verify`](https://code.claude.com/docs/zh-TW/skills#run-and-verify-your-app)。

```
write the migration, run it against the dev database, and confirm the schema matches

```

**指向參考。** 命名現有檔案、測試或模式以符合，以便新程式碼與您已有的內容一致。

```
add a settings page that follows the same layout as the profile page

```

**說明可測量的目標。** 當目標是效能或涵蓋範圍時，提供指標和閾值，以便完成是明確的。

```
get the bundle size under 200KB and show me what you removed

```

**給它工件。** 直接在提示詞中貼上錯誤、日誌、螢幕截圖和計畫輸出，或輸入 `@` 以參考檔案。Claude 讀取來源而不是您對它的描述。

```
why is the build failing? @build.log

```

**說出您想要答案的方式。** 命名格式、長度或受眾，以便解釋適合您使用它的方式。若要為每個回應設定預設格式，請設定 [輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)。

```
explain how the payment retry logic works as an HTML page with a diagram, then open it in my browser

```

如需每個模式的詳細資訊，請參閱[最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)。

## 這些來自何處

這些提示詞基於已發佈的 Anthropic 資源中的模式。每張卡片都連結到其來源：

- [常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)：核心任務的逐步指南
- [最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)：提示詞模式和專案設定
- [Anthropic 團隊如何使用 Claude Code](https://claude.com/blog/how-anthropic-teams-use-claude-code)：來自工程、產品、設計和資料團隊的真實工作流程，深入探討[法律](https://claude.com/blog/how-anthropic-uses-claude-legal)、[行銷](https://claude.com/blog/how-anthropic-uses-claude-marketing)和[網路安全](https://claude.com/blog/how-anthropic-uses-claude-cybersecurity)
- [擴展代理編碼指南](https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf)：企業採用指南

如需這些模式的影片演練，請參閱 Anthropic Academy 上的免費 [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action) 課程。

## 相關資源

此頁面上的提示詞是起點。一旦一個對您的專案有效，下一步是使其可重複：將其儲存為 [技能](https://code.claude.com/docs/zh-TW/skills)，以便您的團隊中的任何人都可以將其作為 `/command` 執行，並在 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory) 中記錄 Claude 學到的慣例，以便每個工作階段都以該背景開始，而不是 Claude 重新學習它。對於更大或更危險的變更，[計畫模式](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode)在任何編輯發生前顯示檔案清單。 如果您在整個團隊中引入 Claude Code，請參閱[管理](https://code.claude.com/docs/zh-TW/admin-setup)以了解受管設定和政策，以及[成本和使用](https://code.claude.com/docs/zh-TW/costs)以了解此工作在您的計畫上如何計費。 是否 助手
