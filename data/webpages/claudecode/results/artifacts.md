成品適用於 Pro、Max、Team 和 Enterprise 方案，並需要使用 [`/login`](https://code.claude.com/docs/zh-TW/setup#authenticate) 登入的工作階段。請參閱[可用性](https://code.claude.com/docs/zh-TW/artifacts#availability)以了解完整的需求集合。 [成品](https://claude.com/features/artifacts)是一個即時互動的網頁，Claude Code 從您的工作階段發佈到 claude.ai 上的私密 URL。您在瀏覽器中開啟它，當工作階段繼續進行時，它會就地更新。當您想讓其他人也看到它時，可以從頁面標題中分享它。

![在 claude.ai/code/artifact 中開啟的成品。檢視器標題顯示成品標題 acme-funnel-fix、一個「分享」按鈕和作者頭像。「分享」選單已開啟，顯示「始終分享最新版本」切換、讀取「分享版本 2」的版本選擇器、「Acme 的所有人」對象選擇器和「複製連結」按鈕。在標題下方，成品頁面顯示兩個並排的行動裝置模型、一個漏斗圖表和一列指標卡片。](https://mintcdn.com/claude-code/kaHIYYMIYMYPxQg9/images/artifacts-viewer.png?fit=max&auto=format&n=kaHIYYMIYMYPxQg9&q=85&s=dbfd671cdb0d15f49f808b9e89778fe1)
> # Image-1
>
> **圖片摘要：**
> Acme 產品頁展示匯出流程版本對照、漏斗圖表、指標卡與分享權限對話框。
>
> **主要元素：**
> 1. 實體: 匯出流程對照圖,行動介面,轉換漏斗圖,分析指標卡,分享權限視窗
> 2. OCR文字:
> acme-funnel-fix
> claude.ai/code/artifact/0d2447a6-6c35-4259-a320-8057c679e2ea
> Share
> 4.2 — Current
> 4.3.1 — P[模糊]
> 9:41
> ✓ Exported to camera...
> full res? Try Pro free
> Export
> Full resolution
> 4032 × 3024 · need[模糊]
> $3.99/mo
> Standard
> 2048 × 1536 · free
> Continue — Go Pro
> Maybe later
> Standard
> 2048 × 1536 · free
> Full resolution
> 4032 × 3024 · Pro
> Export
> Settings remembers your choice
> ① Pro preselected — price is first paint
> ② CTA sells the plan, not the export
> ① Free default restored — no ambush
> ② The ask moves to after success
> The funnel didn't sag — it snapped
> v4.2 — Mar 18
> 33.6%
> 24.1%
> v4.1 n=2.61M · v4.2+ n=5.80M · mix ±0.6pt
> 8.41M
> EDITOR SESSIONS
> ▲ 3.1%
> 76.6%
> CLASSIC APPLY RATE
> ▲ 1.2pt
> 4.99M
> EXPORT TAPS
> ▲ 2.4%
> 27.8%
> EXPORT COMPLETION
> ▼ 9.4pt
> 188.4K
> PRO CONVERSIONS
> ▼ 1.8%
> Last 90 days
> More than half of exports never complete
> Cancels are reflexes
> 68% bail inside three seconds — no scroll, no option tap. The[模糊]
> Always share latest version
> Sharing version 2 (Just now)
> Everyone at Acme
> Copy link
> 3. 主題標籤: 匯出流程,轉換漏斗,版本分析,分享權限,產品分析
>
> **頁面關聯：**
> Acme 產品分析頁，錨點 acme-funnel-fix、Export、Pro
## 何時使用 artifact

當終端文字不是 Claude 產生的內容的合適媒介時，請使用 artifact：輸出內容比逐行閱讀更容易查看和互動。Claude 從您的工作階段可以存取的任何內容建立頁面，包括您的程式碼庫和透過您的[連接工具](https://code.claude.com/docs/zh-TW/mcp)提取的資料，因此頁面可以顯示需要段落才能描述的內容。例如，要求 Claude：

- 透過附註的差異引導審查者查看提取請求
- 從工作階段已提取的資料呈現儀表板
- 並排配置多個設計或實作選項
- 保持在長任務執行時填入的調查時間軸
- 傳送連結給隊友，而不是將輸出貼到 Slack
- 發佈狀態板，每次有人開啟時[透過 MCP 連接器提取新鮮資料](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)

請參閱[您可以建立的內容](https://code.claude.com/docs/zh-TW/artifacts#what-you-can-build)以取得符合這些的提示，以及[使用 MCP 連接器提取即時資料](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)以取得連接器支援的板的提示。

### artifact 不是什麼

artifact 是工作的擷取：一個自包含的頁面，沒有後端，因此無法提供多個路由。對於具有後端的託管內部工具，請改為在您自己的基礎設施上部署它。請參閱[頁面限制](https://code.claude.com/docs/zh-TW/artifacts#page-constraints)以取得完整的限制集合。

## 建立成品

Claude 可能會在輸出適合頁面時自動發佈成品，或者你可以直接要求建立一個。若要要求，請用純文字命名功能或描述你想要的視覺輸出。任何比以文字閱讀更容易看到的東西都是很好的候選，例如帶有內聯註解的差異、圖表或一組選項進行比較。下面的提示是兩個例子；請參閱[你可以建立的內容](https://code.claude.com/docs/zh-TW/artifacts#what-you-can-build)以了解更多模式。

```
建立一個成品，逐步說明此 PR，並在內聯中註解差異。

```

```
建立一個儀表板成品，顯示上週按服務的部署失敗，並在你調查時保持更新。

```

除非你指定位置，否則 Claude 會將頁面寫入專案外臨時目錄中的 HTML 或 Markdown 檔案，然後發佈它。發佈新成品會通過你的工作階段的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)：

- **自動模式** ：分類器會檢查發佈，而不是提示你，因此 Claude 可以在你看不到提示的情況下發佈頁面。你的工作階段開始時使用哪種模式取決於你的方案；請參閱[起始權限模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)。
- **手動和接受編輯模式** ：Claude Code 會要求權限；它可能會說類似 `Claude 想要發佈 deploy-failures.html，將其上傳到 claude.ai（Anthropic 的伺服器）以將頁面「按服務的部署失敗」作為私密頁面託管，直到你分享它`。選擇**是** 以發佈。

在你批准成品一次後，Claude Code 會重新發佈它而不詢問，並在某些情況下再次詢問，包括：

- Claude 為頁面聲明執行時功能，例如[連接器呼叫](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)或[檔案下載](https://code.claude.com/docs/zh-TW/artifacts#offer-a-file-download)
- 你已經[公開分享它](https://code.claude.com/docs/zh-TW/artifacts#share-an-artifact)
- 你已經與特定人員或你的組織分享它，並選擇最新版本作為檢視者看到的版本

在首次發佈後，Claude 會列印 URL，你的瀏覽器會開啟到新頁面。如果你從 claude.ai、Claude Desktop 或 Claude 行動應用程式透過[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)傳送提示，執行工作階段的機器上不會開啟任何標籤。下次 Claude 從你在終端機輸入的提示發佈成品時，瀏覽器會在那裡開啟。隨時按 `Ctrl+]` 以重新開啟工作階段的最新成品。 Claude 會為成品選擇標題和表情符號，兩者都會出現在你在 claude.ai 上的[成品庫](https://code.claude.com/docs/zh-TW/artifacts#share-an-artifact)和共享連結中。Claude 也可以選擇與頁面內容相符的瀏覽器標籤圖示，例如圖表或日曆。如果你想要特定標題、表情符號或標籤圖示，請要求 Claude。 若要停止瀏覽器在發佈新成品時自動開啟，請在你的環境中設定 `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0`。 如果 Claude 回應它無法發佈，或寫入本機 HTML 檔案而沒有連結，則該工具未針對你的工作階段啟用。檢查[可用性](https://code.claude.com/docs/zh-TW/artifacts#availability)要求。

## 更新成品

要求 Claude 修訂頁面，或讓長時間執行的任務在進行時重新發佈。Claude 編輯基礎檔案並重新發佈到相同的 URL。

```
在摘要圖表下方新增按地區的細項分析，並重新發佈。

```

任何開啟該頁面的人都會看到就地更新。每次發佈都會成為一個版本，您可以從頁面標題中的**分享** 控制項選擇檢視者看到的版本。 若要從不同的工作階段更新成品，請提供 Claude 其 URL，或使用 [`/artifacts`](https://code.claude.com/docs/zh-TW/artifacts#find-an-artifact-again) 附加它。如果兩者都沒有，新的工作階段會建立新的成品，而不是更新現有的。

```
使用今天的數字更新 https://claude.ai/code/artifact/5fbea6f3-...。

```

## 再次尋找成品

在 Claude Code 中執行 `/artifacts` 以列出您擁有的每個成品和與您共享的每個成品。選擇一個並按 `o` 在瀏覽器中開啟它，或按 `c` 複製其連結。按 `Enter` 將其附加到目前的工作階段；在 v2.1.216 之前，`Enter` 會在瀏覽器中開啟它。Claude Code 從您的 claude.ai 帳戶讀取清單，因此它在新工作階段中運作，並在 `/clear` 之後運作，當連結已從終端機捲出時。需要 Claude Code v2.1.208 或更新版本。

## 分享成品

新的成品只有你能看到。若要分享，請在瀏覽器中開啟成品，並使用頁面標題中的**分享** 控制項。標題也會連結到你的圖庫 [claude.ai/code/artifacts](https://claude.ai/code/artifacts)，其中列出你建立的每個成品。 你組織中的檢視者可以看到誰發佈了該頁面：在組織內分享的成品上，你的名稱會在標題選單中；在公開成品上，已登入的組織成員檢視者會在頁面標題中看到你的名稱。未登入或來自組織外部的檢視者開啟公開連結時，會看到標籤 `內容由使用者產生且未經驗證。` 而不是你的名稱。 你可以分享給誰取決於你的方案：

- **在組織內** ：在 Team 和 Enterprise 方案上，授予組織中特定人員或所有人的存取權。檢視者以組織成員身分登入 claude.ai 以查看該頁面。
- **公開** ：分享一個連結，網際網路上的任何人都可以開啟，無需 claude.ai 登入。在 Pro 和 Max 方案上，公開連結是分享成品的唯一方式。在 Team 和 Enterprise 方案上，公開分享處於關閉狀態，直到擁有者[為組織啟用它](https://code.claude.com/docs/zh-TW/artifacts#control-public-sharing)。

### 讓某人與你一起編輯

與你分享的人預設為檢視者：他們可以看到你發佈的每個版本，但無法變更頁面。在 Team 和 Enterprise 方案上，你也可以讓某人成為編輯者。在分享對話中，新增一個人並將其角色從**檢視者** 切換為**編輯者** 。 編輯者發佈新版本的方式與你[從另一個工作階段更新成品](https://code.claude.com/docs/zh-TW/artifacts#update-an-artifact)相同：他們提供成品的 URL 給 Claude，或從 [`/artifacts`](https://code.claude.com/docs/zh-TW/artifacts#find-an-artifact-again) 附加它，Claude 會提取目前內容並使用他們的變更重新發佈。所有開啟該頁面的人都會即時看到每個更新。

## 閱讀與您共享的成品

當有人與您共享成品時，您可以讓 Claude 閱讀它：提供 Claude 其 URL，或從 [`/artifacts`](https://code.claude.com/docs/zh-TW/artifacts#find-an-artifact-again) 附加它。 Claude 閱讀他人撰寫的頁面的方式與它使用 [WebFetch](https://code.claude.com/docs/zh-TW/tools-reference#webfetch-tool-behavior) 閱讀網頁的方式相同：它取得所詢問內容的摘要，而不是原始頁面，摘要報告寫入頁面的指示，而不是轉達它們。Claude Code 也會將頁面的完整原始碼儲存到本機檔案，Claude 可以在需要確切內容時開啟該檔案，例如重新發佈成品作為 [編輯器](https://code.claude.com/docs/zh-TW/artifacts#let-someone-edit-with-you)。

## 收集成品上的評論

當您在組織內分享成品時，與您分享的人可以在頁面上留下評論，您可以讓 Claude 讀取這些評論並回覆。您需要 Claude Code v2.1.221 或更新版本以及 Team 或 Enterprise 方案，因為只有您[在組織內分享](https://code.claude.com/docs/zh-TW/artifacts#share-an-artifact)的成品才會接收評論。Claude 在兩種情況下會讀取評論：

- **您要求 Claude 讀取評論** ：提供 Claude 成品的 URL 並要求查看評論。Claude 會列出每個執行緒，並標記可以編輯成品的人發送給它的評論。
- **可以編輯成品的人向 Claude 發送評論** ：在頁面上的執行緒中，他們使用**傳送給 Claude** 發送評論，或在其中提及 `@claude`。無論哪種方式，他們都會啟動該執行緒。

Claude 只能回覆或解決已啟動的執行緒。其他執行緒保持開啟狀態，直到某人在頁面上解決它們。檢視者會看到每個回覆都歸屬於 Claude，透過您。 如果您公開分享成品，檢視者無法對其進行評論：頁面會顯示 `Comments aren't available while this Artifact is shared publicly.` 若要將已有評論執行緒的成品切換為公開連結，請先刪除這些執行緒。 若要自行要求評論，請提供 Claude URL：

```
Read the comments on https://claude.ai/code/artifact/5fbea6f3-... and make the changes the commenters ask for.

```

如果 Claude 告訴您它無法讀取評論，請確認您的版本、您的工作階段和您的功能旗標設定：

- 您執行的是 Claude Code v2.1.221 或更新版本。
- 您不在安裝 Claude Code 或從 v2.1.221 之前的版本升級後的第一個工作階段中。在[安裝或升級後的第一個工作階段](https://code.claude.com/docs/zh-TW/env-vars#first-session-after-an-install-or-upgrade)中，Claude 可能還無法讀取評論；開始新的工作階段並再次詢問。
- 您未關閉功能旗標擷取。

### 讓 Claude 自動回覆評論

在您的工作階段發佈成品後，Claude Code 會在工作階段執行期間監視該成品的評論。當可以編輯成品的人向 Claude 發送評論時，它會立即到達您的工作階段，Claude 可以讀取執行緒並回覆，而無需您詢問。 您需要 Claude Code v2.1.228 或更新版本。如果您關閉了[功能旗標擷取](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)，Claude Code 不會監視評論。 您的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)決定了當發送的評論到達時 Claude 的行為：

- **Claude 自動回覆** ：當您的權限模式允許 Claude 在不詢問您的情況下發佈回覆時，Claude 會讀取執行緒並回覆，並在評論要求變更時編輯成品。您會看到 `Auto-replied to comment thread on Artifact: <name>` 或 `Auto-edited Artifact: <name> in response to a comment thread`。
- **Claude 等待您** ：在計畫模式外，當發佈回覆需要您的批准時，您會看到 `Comments are waiting on Artifact: <name>`。Claude 隨後會要求您批准讀取執行緒，然後再次批准發佈回覆。
- **Claude 在計畫模式中暫停** ：您會看到 `Comments are waiting on Artifact: <name>`，Claude 不會回覆，直到您離開計畫模式並要求它讀取並回覆。

Claude 在處理該成品上的 60 個已發送評論或執行緒啟動後，也會停止自動回覆該成品。您會看到 `Comments are waiting on Artifact: <name>` 一次，當該小時的評論過期時，Claude 會重新開始。 執行 `/tasks` 以查看您的工作階段正在監視的每個成品，列為即時更新任務。您可以透過以下任何方式停止 Claude 自動回覆：

- **在閒置提示字元處按一次 Ctrl+C** ：Claude 暫停回覆您的工作階段正在監視的每個成品。在您發送下一條訊息後，回覆會重新開始。
- **在`/tasks` 中停止任務**：Claude 停止回覆該成品，直到您要求它在那裡恢復回覆。重新發佈成品不會再次開始回覆，當您稍後恢復工作階段時，停止仍然適用。
- **在 3 秒內按兩次`Ctrl+X Ctrl+K`** ：[停止每個執行中背景子代理](https://code.claude.com/docs/zh-TW/interactive-mode#general-controls)的和弦也會停止 Claude 在工作階段的其餘時間內回覆每個成品。要求 Claude 恢復回覆不會撤銷此停止。

如果傳遞評論的服務變得不可用或停止回應，Claude Code 會嘗試重新連接一段時間，然後停止監視您的工作階段正在監視的每個成品。

## 使用 MCP 連接器拉取即時資料

每當有人檢視成品時，成品可以呼叫 [MCP 連接器](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)，因此頁面會顯示目前資料而不是建立該頁面的工作階段所收集的快照。來自成品的連接器呼叫適用於 Pro、Max、Team 和 Enterprise 方案，並需要 Claude Code v2.1.209 或更新版本。在較早的版本上，Claude 會發佈該頁面，其中包含工作階段在建立時收集的任何資料。 若要建立連接器支援的頁面，請在提示中命名連接器和您想要的資料：

```
建立一個顯示我們開放拉取請求的儀表板成品，該成品在頁面載入時透過我的 GitHub 連接器拉取即時清單。

```

Claude 會在發佈時宣告該頁面可能呼叫的連接器，且該頁面無法呼叫該宣告之外的連接器。只有來自您 claude.ai 帳戶的連接器符合資格：Claude 在宣告中命名它們，當有人檢視該頁面時，每個呼叫都會 [透過檢視帳戶自己的連接](https://code.claude.com/docs/zh-TW/artifacts#how-connector-calls-work-for-viewers) 執行到該連接器。您在 Claude Code 中設定的本機 MCP 伺服器（例如來自 `.mcp.json` 的伺服器）可以在 Claude 建立頁面時提供資料，但已發佈的頁面無法呼叫它們。 該頁面在載入時會擷取資料，並可以按間隔重新整理或當檢視者在頁面上使用重新整理控制項時重新整理。回應會快取在檢視者的瀏覽器中，因此重新開啟的頁面會立即從快取的回應呈現，然後使用新鮮結果進行更新。

### 連接器呼叫如何為檢視者運作

當已發佈的頁面呼叫連接器時，該呼叫會使用檢視該頁面的人的帳戶，而不是發佈該頁面的人的帳戶：

- **每個檢視者使用自己的連接器** ：呼叫會透過檢視帳戶的已連接工具進行，因此兩個人開啟相同的儀表板可能會看到不同的資料，取決於他們的帳戶可以存取的內容。該頁面永遠不會看到任何人的認證；claude.ai 代表該頁面進行呼叫。
- **檢視者先核准存取** ：claude.ai 在該頁面的第一個連接器呼叫之前會要求每個檢視者的許可。拒絕的檢視者或尚未連接該頁面使用的連接器的檢視者仍然可以看到該頁面，但沒有其即時區段。
- **動作也使用檢視者的帳戶** ：頁面可以提供控制項，這些控制項會叫用具有副作用的連接器工具，例如發佈訊息或更新問題。該動作會透過選擇該控制項的任何人的帳戶進行。

當您計畫共享連接器支援的頁面時，請要求 Claude 在每個即時區段中包含一個後備訊息，該訊息命名它需要的連接器。缺少連接的檢視者會看到要連接的內容，而不是空白區段。 呼叫連接器的成品無法在任何方案上共享到公開連結。在 Team 和 Enterprise 方案上，您可以將其保持為私密或 [在您的組織內共享](https://code.claude.com/docs/zh-TW/artifacts#share-an-artifact)。在 Pro 和 Max 方案上（其中公開連結是唯一的共享方式），連接器支援的成品會保持為您的私密。

### 頁面對檢視者不顯示即時資料

當連接器支援的頁面呈現但其即時區段對您共享的某人保持空白時，請檢查這些原因：

- **檢視者尚未連接連接器** ：連接器是按帳戶的，因此每個檢視者都需要自己的連接到該頁面呼叫的每個連接器。他們可以在 claude.ai 上的 **Settings > Connectors** 下新增一個，然後重新載入頁面。
- **檢視者拒絕了許可要求** ：拒絕會持續到該頁面載入的其餘部分。重新載入頁面會帶回許可要求。
- **連接器呼叫已針對組織關閉** ：擁有者控制管理設定中的 [**Enable artifact connectors** 切換](https://code.claude.com/docs/zh-TW/artifacts#control-connector-calls-from-artifacts)。
- **頁面呼叫連接器未公開的工具名稱** ：受影響的區段對所有人（包括您）保持空白。當頁面命名閘道式連接器後面的個別工具，而該連接器只公開其自己的少數工具時，就會發生這種情況。要求 Claude 修正頁面呼叫的工具名稱並再次發佈。 當 Claude 發佈頁面且該連接器的工具在您的工作階段中可用時，Claude Code 會檢查頁面宣告的工具名稱與它們的對比，警告 Claude 不符合的名稱，並在沒有任何名稱符合時拒絕發佈。在 v2.1.265 之前，它會在不檢查它們的情況下發佈頁面。

## 提供檔案下載

成品可以向檢視者提供頁面生成的檔案，例如表格的 CSV 匯出或圖表的 PNG。檢視者透過頁面上的下載控制項（例如按鈕）來儲存檔案。檔案下載是 claude.ai 按帳戶啟用的執行時功能，因此 Claude 在建立控制項之前會檢查您的帳戶是否具有此功能。 檢視者無法從普通下載連結或頁面上的指令碼儲存檔案，因為 claude.ai 上的成品檢視器會阻止頁面本身啟動的任何下載，包括指向 `data:` 或 `blob:` URL 的連結。如果頁面具有以這種方式建立的下載按鈕，請要求 Claude 使用下載功能重新建立它們。 若要提供檔案，請在您的提示中要求控制項和檔案格式：

```
Add a button that downloads this table as a CSV file.

```

Claude 將下載功能宣告為發佈的一部分，其方式與[使用 MCP 連接器提取即時資料](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)相同。

## 您可以建立的內容

成品是單個 HTML 頁面，因此您可以用 HTML、CSS 和內聯 JavaScript 表達的任何內容都在範圍內。下面的模式最常出現。

### 逐步查看變更

要求一個頁面，在相關行旁邊呈現差異或設計變更並帶有註解，以便審查者可以在程式碼旁邊閱讀您的推理，而不是從描述中重建它。

```
Make an artifact that walks through this PR. Render the diff with margin annotations and color-code findings by severity.

```

### 比較替代方案

要求在一個頁面上有多個變體，以便您可以相互評估它們。這適用於佈局、複製、API 形狀或實現計劃。

```
Make an artifact with four distinctly different layouts for the settings panel. Vary density and grouping, and lay them out as a grid with a one-line tradeoff under each.

```

### 使用互動控制項進行調整

要求滑塊、切換或輸入欄位綁定到您正在調整的任何內容，以便您可以直接探索值，而不是描述它們。

```
Build an artifact with sliders for the easing curve, duration, and delay so I can try values on this transition. Show the animation live as I move them.

```

### 將結果帶回您的工作階段

成品可以充當輕量級編輯器，用於您隨後交給 Claude 的決定。要求匯出控制項，產生您可以貼到終端的文字，以便與頁面互動的結果流回工作階段，而不是停留在頁面上。

```
Make a triage board artifact with each open issue as a draggable card across Now, Next, Later, and Cut columns. Add a "Copy as prompt" button that gives me the final ordering to paste back here.

```

### 追蹤進行中的工作

要求 Claude 在長任務執行時保持成品最新，以便任何有連結的人都可以跟進，而無需閱讀終端。

```
Turn this migration plan into a checklist artifact. Check items off as you complete them and add a note for anything you skip.

```

## 改進視覺設計

Claude 在建立成品時會應用內建的設計技能，因此頁面會獲得經過深思熟慮的調色盤、排版和版面配置，無需額外提示。該技能也會在選擇自己的設計之前，先查看您專案中是否存在現有的設計系統。設計權杖是您設計系統重複使用的具名顏色、排版和間距值。為了保持成品與您產品品牌的一致性，請將它們記錄在 Claude 可以找到的地方，例如專案的 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory) 或您儲存庫中的主題檔案：

```
## Design system

- Colors: primary #1a4d8f, accent #f59e0b, surface #f8fafc
- Typography: Inter for body, JetBrains Mono for code
- Spacing: 8px scale, 6px border radius

```

Claude 將您的設計系統視為比自己的選擇更高的優先順序，並將您的提示視為比兩者都更高的優先順序。上面的標題和格式是一個範例；任何清晰的顏色、字型和間距清單都可以使用。 對於排版，Claude 可以從 Google Fonts 載入字型，這是成品頁面可以載入的唯一外部字型來源。Claude 會將任何其他字型內嵌為 `@font-face` 資料 URI，並為每個字型提供備用堆疊，因此即使字型無法載入，頁面仍會呈現。若要使用特定字型，請在您的提示或設計系統中命名它。

## 草擬設計畫布

若要模擬 UI、螢幕流程、登陸頁面或海報，而不是建立頁面，請使用簡介執行 `/design`。Claude 會在一個畫布上將設計草擬為美工板，並將畫布發佈為設計成品。簡介會命名您想要繪製的內容：

```
/design a settings screen for a mobile banking app

```

在桌面瀏覽器中開啟已發佈的成品以檢閱美工板。在美工板上選取元素並變更它，您的編輯會自動儲存。您可以將每個美工板匯出為 PNG 或 PDF。 `/design` 需要一個 [成品可用](https://code.claude.com/docs/zh-TW/artifacts#availability) 的工作階段，以及 Claude Code v2.1.265 或更新版本。

## 頁面限制

每個成品是一個獨立的頁面。Claude Code 會將您發佈的檔案包裝在 HTML 文件殼層中，並在嚴格的內容安全政策 (CSP) 下提供服務，這會限制頁面可以執行的操作。

| 限制                                                                                                                                                                                             | 效果                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 外部請求                                                                                                                                                                                         | 頁面可以從 Google Fonts 載入字型，以及從[四個公開 CDN 主機](https://code.claude.com/docs/zh-TW/artifacts#allowlist-the-viewer-domain)載入指令碼：cdnjs、Tailwind 和 jQuery CDN，以及 jsDelivr 上的選定路徑，例如 `/npm/`。CSP 會阻止所有外部影像和所有其他外部指令碼、樣式表和字型，並讓 `fetch`、XHR 和 WebSocket 呼叫只能到達頁面自身的來源和 Google Fonts 主機。因此，Claude 會從這些 CDN 之一載入頁面需要的任何程式庫，內嵌所有其他 CSS 和 JavaScript，並將影像嵌入為資料 URI。[Connector 呼叫](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)會通過 claude.ai 進行，它會自行進行網路呼叫。 |
| 無後端                                                                                                                                                                                           | 成品是靜態頁面。它無法自行驗證檢視者。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 下載                                                                                                                                                                                             | 頁面無法自行啟動下載。為了讓檢視者儲存頁面產生的檔案，Claude 會宣告下載功能。請參閱[提供檔案下載](https://code.claude.com/docs/zh-TW/artifacts#offer-a-file-download)。                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 單一頁面                                                                                                                                                                                         | 相對連結無法解析，因為頁面旁邊沒有部署任何內容。對於多區段內容，Claude 使用頁面內錨點而不是個別檔案。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 來源檔案類型                                                                                                                                                                                     | 發佈的檔案必須是 `.html`、`.htm` 或 `.md`，且必須解碼為 UTF-8，或根據其位元組順序標記解碼為小端 UTF-16。Markdown 檔案會呈現為樣式化的文件頁面，並具有語法醒目提示的程式碼。無法解碼或包含替換字元 `U+FFFD` 的檔案會[被拒絕並顯示要修正的行和列](https://code.claude.com/docs/zh-TW/errors#the-source-file-is-not-valid-utf-8-text)。                                                                                                                                                                                                                                                                                              |
| 呈現大小                                                                                                                                                                                         | 呈現的頁面必須為 16 MiB 或更小。大型嵌入影像通常是發佈因大小而失敗的原因。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 產生成品會像任何其他回應一樣使用輸出權杖，而樣式化頁面比相同內容作為終端文字更耗費權杖。內嵌 CSS、用於互動控制的 JavaScript，尤其是嵌入為資料 URI 的影像，是主要貢獻者。若要減少成品的權杖成本： |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

- 對於圖表，優先使用 SVG 或 HTML 和 CSS，而不是嵌入的光柵影像
- 省略您不需要的互動性
- 讓頁面摘要大型資料集，而不是完整內嵌它們

## 可用性

成品需要下面的每個條件。當不滿足其中一個時，Claude 寫入本地 HTML 檔案或說它無法發佈。

| 要求       | 可用時間                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 方案       | Pro、Max、Team 或 Enterprise。在 Pro 和 Max 方案上，成品僅供您私人使用，不適用管理員管理。在 Team 方案上，成品預設開啟。在 Enterprise 方案上，Owner 在 claude.ai 管理設定中[啟用它們](https://code.claude.com/docs/zh-TW/artifacts#manage-artifacts-for-your-organization)。                                                                                                                                                                |
| 驗證       | 工作階段由 claude.ai 帳戶支援：在 CLI 或桌面應用程式中使用 `/login` 登入。Claude Tag 工作階段透過代理程式的身分登入，因此不需要任何步驟。使用 API 金鑰、[閘道令牌](https://code.claude.com/docs/zh-TW/llm-gateway)或雲端提供者認證的工作階段無法發佈。                                                                                                                                                                                      |
| 模型提供者 | Anthropic API。在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 上不可用。                                                                                                                                                                        |
| 組織政策   | 客戶管理的加密金鑰 (CMEK)、HIPAA 和[零資料保留](https://code.claude.com/docs/zh-TW/zero-data-retention)未為組織啟用。                                                                                                                                                                                                                                                                                                                       |
| 表面       | Claude Code CLI 版本 2.1.183 或更新版本，或 Claude 桌面應用程式版本 1.13576.0 或更新版本。[Claude Tag](https://claude.com/docs/claude-tag/overview) 工作階段在 Claude Tag 和成品都為組織啟用時也可以發佈成品。在 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview)、GitHub Action 和 MCP 伺服器上下文中預設關閉，以及當設定 [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/zh-TW/env-vars) 時。 |

## 停用 artifacts

若要關閉您自己工作階段中的 artifacts，無論您的組織設定為何，請使用以下任一方式：

| 位置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 操作                                                                                                                                               |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`/config`](https://code.claude.com/docs/zh-TW/commands)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 關閉 **Artifacts** 列，這會將 [`"enableArtifact": false`](https://code.claude.com/docs/zh-TW/settings-reference#enableartifact) 寫入您的使用者設定 |
| [設定檔](https://code.claude.com/docs/zh-TW/settings)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 設定 `"enableArtifact": false`。已棄用的 `"disableArtifact": true` 也會關閉 artifacts                                                              |
| [環境變數](https://code.claude.com/docs/zh-TW/env-vars)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 設定 `CLAUDE_CODE_DISABLE_ARTIFACT=1`                                                                                                              |
| [權限規則](https://code.claude.com/docs/zh-TW/permissions)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 將 `Artifact` 新增至 `permissions.deny`                                                                                                            |
| 一旦您在 [`--settings`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 檔案中或使用 `CLAUDE_CODE_DISABLE_ARTIFACT` 關閉 artifacts，或您的管理員在[受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)中關閉它們，就沒有設定檔能將其重新開啟。在 v2.1.242 之前，[優先順序堆疊](https://code.claude.com/docs/zh-TW/settings#settings-precedence)中較高位置的檔案可能會重新開啟 artifacts，即使較低優先順序的檔案設定了 `"enableArtifact": false`。 您也可以在專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中設定 `"enableArtifact": false`，以關閉該專案中工作階段的 artifacts。任一檔案中的 `"enableArtifact": true` 都不會將其重新開啟。在專案和本機設定中接受此金鑰需要 Claude Code v2.1.242 或更新版本。 如果您新增 `WebFetch` deny 或 ask 規則但不含 `domain:` 部分，它不會關閉 artifacts 或阻止 artifact 讀取。[`permissions` 中 `deny` 或 `ask` 內的 `WebFetch(domain:claude.ai)` 規則確實適用於 artifact 讀取](https://code.claude.com/docs/zh-TW/permissions#allow-or-deny-every-fetch)。 |                                                                                                                                                    |

## 為您的組織管理成品

Team 和 Enterprise 方案上的擁有者從 [claude.ai 管理設定](https://claude.ai/admin-settings/claude-code)控制成品。成品內容儲存在 Anthropic 營運的基礎設施上，僅對發佈組織的已驗證成員可見，除非成品是[公開分享](https://code.claude.com/docs/zh-TW/artifacts#control-public-sharing)。

### 啟用或停用成品

要為整個組織啟用或停用成品，請前往 [**設定 > Claude Code > 功能**](https://claude.ai/admin-settings/claude-code)並使用**成品** 切換。在具有角色型存取控制的 Enterprise 方案上，您還可以將成品範圍限制為特定角色：前往 [**設定 > 角色**](https://claude.ai/admin-settings/roles)、編輯角色，並在 **Claude Code** 群組下設定**成品** 許可。

### 控制來自成品的連接器呼叫

[來自成品的連接器呼叫](https://code.claude.com/docs/zh-TW/artifacts#pull-live-data-with-mcp-connectors)有自己的切換，與開啟或關閉成品的**成品** 切換分開。前往 [**設定 > 功能**](https://claude.ai/admin-settings/capabilities)並使用**啟用成品連接器** 切換。同一個切換控制在 claude.ai 對話中建立的成品的連接器呼叫，這就是為什麼它位於**設定 > 功能**而不是**設定 > Claude Code**。

### 控制公開分享

在 Team 和 Enterprise 方案上，公開分享預設為關閉，因此成員只能在組織內分享成品，直到擁有者開啟它。要讓成員將成品發佈到任何人都可以檢視而無需登入的公開連結，請前往**設定 > Claude Code > 功能**並在**成品** 切換下開啟**外部分享** 。將其關閉會阻止透過現有公開連結的存取，而不會變更每個成品的對象；如果您重新啟用它，存取將恢復。

### 設定保留政策

要設定在自動刪除之前保留成品的時間，請前往 [**設定 > 資料和隱私控制**](https://claude.ai/admin-settings/data-privacy-controls)。您可以為仍然是其作者私人的成品和已共享的成品設定單獨的保留期。

### 檢查稽核日誌

發佈、分享和刪除成品各自出現在您組織的稽核日誌中，位於 `claude_artifact_*` 事件類型下，與在 claude.ai 對話中建立的成品使用的相同系列。

### 允許列表檢視器網域

claude.ai 上的檢視器從沙箱化的 `*.claudeusercontent.com` 來源載入每個成品。如果您的組織限制出站網路存取，請將該網域新增到您的允許列表中，以及 `claude.ai`。請參閱[網路存取要求](https://code.claude.com/docs/zh-TW/network-config#network-access-requirements)以了解完整清單。 從 [Google Fonts](https://code.claude.com/docs/zh-TW/artifacts#improve-the-visual-design) 載入字型的成品也會要求 `fonts.googleapis.com` 和 `fonts.gstatic.com`。兩個主機都是選用的。如果您封鎖它們，成品會以備用字型呈現。使用快速拒絕而不是無聲丟棄來封鎖，以便字型要求立即失敗，而不是延遲頁面的首次呈現。 成品也可以從 `cdnjs.cloudflare.com`、`cdn.jsdelivr.net`、`cdn.tailwindcss.com` 和 `code.jquery.com` 載入 JavaScript 程式庫（例如 React 或圖表套件），而不能從任何其他外部主機載入。如果您封鎖這些主機，成品中依賴程式庫的部分將無法運作，與被封鎖的字型不同，被封鎖的程式庫沒有備用方案。在這裡也使用快速拒絕，以便被封鎖的程式庫要求立即失敗，而不是掛起直到逾時。

### 使用 Compliance API 列出和刪除成品

[Compliance API](https://docs.claude.com/en/api/compliance) 提供端點來列出組織的成品、檢索特定版本的內容和刪除成品：

| 方法                                                                                                         | 端點                                                                |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `GET`                                                                                                        | `/v1/compliance/code/artifacts`                                     |
| `GET`                                                                                                        | `/v1/compliance/code/artifacts/{artifact_id}/versions/{version_id}` |
| `DELETE`                                                                                                     | `/v1/compliance/code/artifacts/{artifact_id}`                       |
| 有關請求和回應架構，請參閱 [Compliance API 參考](https://docs.claude.com/en/api/compliance/code/artifacts)。 |                                                                     |

## 相關資源

- 瀏覽與成品配對的[提示模式和工作流程](https://code.claude.com/docs/zh-TW/prompt-library)
- 將您重複使用的成品提示轉變為[技能](https://code.claude.com/docs/zh-TW/skills)，以便您可以將其作為命令呼叫
- [連接 MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)，以便 Claude 可以將資料提取到成品中，同時建置頁面

是否 助手