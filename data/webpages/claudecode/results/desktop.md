Claude Desktop 應用程式有三個標籤：**Chat** 用於對話、**Cowork** 用於 [Dispatch 和更長的代理工作](https://claude.com/product/cowork)，以及 **Code** 用於軟體開發。本頁面是 Code 標籤的參考。

## [下載 macOS 版本 適用於 Intel 和 Apple Silicon 的通用版本 ](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs)

## [下載 Windows 版本 適用於 x64 處理器 ](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)

## [取得 Claude for Linux (測試版) 適用於 Ubuntu 和 Debian 的 apt 或 .deb ](https://code.claude.com/docs/zh-TW/desktop-linux)

若要使用 Windows ARM64，請下載 [ARM64 安裝程式](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)。在 Linux 上，使用 apt 安裝；請參閱 [Claude Desktop on Linux](https://code.claude.com/docs/zh-TW/desktop-linux)。 安裝後，啟動 Claude，登入，然後點擊 **Code** 標籤。如需您第一個會話的逐步說明，請參閱[快速入門指南](https://code.claude.com/docs/zh-TW/desktop-quickstart)。 在 Code 標籤中，每個對話都是一個**會話** ：它有自己的聊天歷史記錄和專案資料夾，獨立於任何其他會話。側邊欄列出您的會話，並讓您並行執行多個會話。在會話中，您可以：

- [使用差異檢查檢查和評論變更](https://code.claude.com/docs/zh-TW/desktop#review-changes-with-diff-view)，然後[透過 CI 監控產生的 PR](https://code.claude.com/docs/zh-TW/desktop#monitor-pull-request-status)
- [在瀏覽器窗格中預覽您執行的應用程式](https://code.claude.com/docs/zh-TW/desktop#preview-your-app)，同時 Claude 驗證其自己的變更，並[在其旁邊開啟外部網站](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)
- [在 iOS Simulator 窗格中觀看 Claude 執行和測試您的 iOS 應用程式](https://code.claude.com/docs/zh-TW/desktop-ios-simulator)
- [排列窗格](https://code.claude.com/docs/zh-TW/desktop#arrange-your-workspace)，將聊天、差異、瀏覽器、終端機和檔案編輯器並排放置
- 提出[側邊問題](https://code.claude.com/docs/zh-TW/desktop#ask-a-side-question-without-derailing-the-session)，使用會話的內容而不會偏離主題
- 讓 Claude [檢查、訊息或封存您的其他會話](https://code.claude.com/docs/zh-TW/desktop#work-across-sessions)
- [連接外部工具](https://code.claude.com/docs/zh-TW/desktop#connect-external-tools)，例如 GitHub、Slack 和 Linear
- 讓 Claude [開啟應用程式並控制您的螢幕](https://code.claude.com/docs/zh-TW/desktop#let-claude-use-your-computer)
- 在您的機器上、[雲端](https://code.claude.com/docs/zh-TW/desktop#run-long-running-tasks-in-the-cloud)或 [SSH](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions) 上執行

如需[排程定期工作](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)、[快捷鍵](https://code.claude.com/docs/zh-TW/desktop#keyboard-shortcuts)或[從您的手機傳送任務](https://code.claude.com/docs/zh-TW/desktop#sessions-from-dispatch)，請參閱連結的頁面和章節。如果您已經使用基於終端機的 CLI，請參閱 [CLI 比較](https://code.claude.com/docs/zh-TW/desktop#coming-from-the-cli)以了解哪些內容可以轉移。

## 開始會話

在發送第一條訊息之前，在提示區域中配置四項內容：

- **環境** ：選擇 Claude 執行的位置。選擇 **Local** 用於您的機器、**Cloud** 用於[雲端會話](https://code.claude.com/docs/zh-TW/desktop#cloud-sessions)（在您關閉應用程式後仍會繼續），[**SSH 連線**](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions)用於您管理的遠端機器，或在 Windows 上選擇 [**WSL 發行版**](https://code.claude.com/docs/zh-TW/desktop-wsl)。請參閱[環境配置](https://code.claude.com/docs/zh-TW/desktop#environment-configuration)。
- **專案資料夾** ：選擇 Claude 工作的資料夾或儲存庫。對於雲端會話，您可以新增[多個儲存庫](https://code.claude.com/docs/zh-TW/desktop#run-long-running-tasks-in-the-cloud)。
- **模型** ：從傳送按鈕旁的下拉式選單中選擇[模型](https://code.claude.com/docs/zh-TW/model-config#available-models)。您可以在會話期間變更此設定。
- **權限模式** ：從[模式選擇器](https://code.claude.com/docs/zh-TW/desktop#choose-a-permission-mode)中選擇 Claude 擁有多少自主權。您可以在會話期間變更此設定。

輸入您的任務並按 **Enter** 開始。每個會話都會追蹤自己的上下文並獨立進行變更。

## 使用程式碼

提供 Claude 正確的背景資訊、控制它自主執行的程度，並檢查它所做的變更。

### 使用提示框

輸入您想讓 Claude 執行的操作，然後按 **Enter** 鍵傳送。Claude 會讀取您的專案檔案、進行變更，並根據您的[權限模式](https://code.claude.com/docs/zh-TW/desktop#choose-a-permission-mode)執行命令。您可以隨時重新導向 Claude：點擊停止按鈕立即中斷，或輸入更正並按 **Enter** 鍵傳送，無需停止執行中的操作。Claude 會在目前操作完成後立即讀取更正，並在下一步之前進行調整。 提示框旁的 **+** 按鈕可讓您存取檔案附件、[skills](https://code.claude.com/docs/zh-TW/desktop#use-skills)、[connectors](https://code.claude.com/docs/zh-TW/desktop#connect-external-tools) 和 [plugins](https://code.claude.com/docs/zh-TW/desktop#install-plugins)。

### 將檔案和背景資訊新增至提示

提示框支援兩種方式來引入外部背景資訊：

- **@mention 檔案** ：輸入 `@` 後跟檔案名稱，將檔案新增至對話背景資訊。Claude 隨後可以讀取並參考該檔案。@mention 在雲端或 WSL 工作階段中不可用。
- **附加檔案** ：使用附件按鈕將影像、PDF 和其他檔案附加到您的提示，或直接將檔案拖放到提示中。這對於分享錯誤的螢幕截圖、設計模型或參考文件很有用。

### 選擇權限模式

權限模式控制 Claude 在工作階段期間的自主程度：它是否在編輯檔案、執行命令或兩者之前詢問。您可以隨時使用傳送按鈕旁的模式選擇器切換權限模式。若要自行核准每項變更，請切換至「手動」。 若要為新的本機工作階段設定預設模式，請將 `permissions.defaultMode` 新增至您的[設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)。桌面應用程式讀取與 CLI 相同的設定檔。您在選擇器中選擇的模式會記住每個資料夾，並優先於該資料夾的 `defaultMode`，但 Plan 除外，它僅適用於目前工作階段。

| 模式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 設定鍵              | 行為                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **手動**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `default`           | Claude 在編輯檔案或執行命令之前詢問。您會看到差異，並可以接受或拒絕每項變更。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **接受編輯**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `acceptEdits`       | Claude 自動接受檔案編輯和常見的檔案系統命令，例如 `mkdir`、`touch` 和 `mv`，但在執行其他終端命令之前仍會詢問。當您信任檔案變更並想要更快速的迭代時，請使用此選項。                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Plan**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `plan`              | Claude 讀取檔案並執行命令以進行探索，然後提出計畫而不編輯您的原始程式碼。適合複雜的工作，您想先檢查方法。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **自動**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | `auto`              | Claude 執行所有操作，並進行背景安全檢查以驗證與您的請求的一致性。減少權限提示，同時保持監督。當[自動模式可用](https://code.claude.com/docs/zh-TW/desktop#auto-mode-availability)時出現；沒有單獨的設定切換。                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **略過權限**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `bypassPermissions` | Claude 執行時不會出現權限提示，除了[任何模式都不會自動核准的操作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)、當 Claude [在外部網站上執行操作](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)時的安全分類器，或桌面操作（Claude 始終先詢問），例如[封存工作階段](https://code.claude.com/docs/zh-TW/desktop#work-across-sessions)。相當於 CLI 中的 `--dangerously-skip-permissions`。在 Pro 和 Max 方案上，在您的設定 → Claude Code 中的「允許略過權限模式」下啟用它；在 Team 和 Enterprise 方案上沒有設定切換，組織政策會控制它。僅在沙箱容器或虛擬機中使用此選項。 |
| Code 標籤的早期版本將這些模式標記為「詢問權限」、「自動接受編輯」和「Plan 模式」。 `dontAsk` 權限模式僅在 [CLI](https://code.claude.com/docs/zh-TW/permission-modes#allow-only-pre-approved-tools-with-dontask-mode) 中可用。 自動模式適用於 Anthropic API 上的所有使用者，需要 Claude Opus 4.6 或更新版本、Sonnet 4.6 或更新版本，或 [Fable 模型](https://code.claude.com/docs/zh-TW/model-config#work-with-fable)。組織管理員可以使用[受管設定](https://code.claude.com/docs/zh-TW/desktop#managed-settings)中的 `disableAutoMode` 鍵關閉自動模式。 在將 Desktop 路由到 Google Cloud 的 Agent Platform 的 Enterprise 部署中，自動模式也預設可用；請參閱 [Bedrock、Agent Platform 或 Foundry 上的自動模式](https://code.claude.com/docs/zh-TW/permission-modes#enable-auto-mode-on-bedrock-agent-platform-or-foundry)以了解支援的模型。 |                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 在 Plan 中開始複雜的工作，讓 Claude 在進行變更之前規劃方法。一旦您核准計畫，切換至「接受編輯」或「手動」以執行它。請參閱[先探索，然後計畫，然後編碼](https://code.claude.com/docs/zh-TW/best-practices#explore-first-then-plan-then-code)以了解更多有關此工作流程的資訊。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 雲端工作階段支援「接受編輯」、「Plan」和「自動」。「接受編輯」對應於 `default` 模式：雲端工作階段預先核准檔案編輯，因此選擇器顯示「接受編輯」而不是「手動」。「略過權限」在雲端工作階段中不可用，包括[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)中的工作階段。 Enterprise 管理員可以限制哪些權限模式可用。請參閱[企業設定](https://code.claude.com/docs/zh-TW/desktop#enterprise-configuration)以了解詳細資訊。                                                                                                                                                                                                                                                                                                                                                                                            |                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

### 預覽您的應用程式

Claude 可以啟動開發伺服器並在「瀏覽器」窗格中開啟它以驗證其變更。這適用於前端網路應用程式以及後端伺服器：Claude 可以測試 API 端點、檢視伺服器日誌，並對它發現的問題進行迭代。在大多數情況下，Claude 在編輯專案檔案後會自動啟動伺服器。您也可以隨時要求 Claude 進行預覽。預設情況下，Claude [自動驗證](https://code.claude.com/docs/zh-TW/desktop#auto-verify-changes)每次編輯後的變更。 「瀏覽器」窗格也可以從您的專案中開啟靜態 HTML 檔案、PDF、影片和影片。在聊天中點擊 HTML、PDF、影像或影片路徑以在那裡開啟它。 從「瀏覽器」窗格，您可以：

- 直接在「瀏覽器」窗格中與執行中的應用程式互動
- 觀看 Claude 自動驗證其自身的變更：它會擷取螢幕截圖、檢查 DOM、點擊元素、填寫表單，並修復它發現的問題
- 從工作階段工具列中的伺服器下拉式選單啟動或停止伺服器
- 通過在下拉式選單中選擇**保留工作階段** ，在伺服器重新啟動時保留 Cookie 和本機儲存，因此您在開發期間不必重新登入
- 編輯伺服器設定或一次停止所有伺服器

Claude 根據您的專案建立初始伺服器設定。如果您的應用程式使用自訂開發命令，請編輯 `.claude/launch.json` 以符合您的設定。請參閱[設定預覽伺服器](https://code.claude.com/docs/zh-TW/desktop#configure-preview-servers)以了解完整參考。 若要清除已儲存的工作階段資料，或完全關閉「瀏覽器」，請使用「設定」→「Claude Code」中的切換。

### 瀏覽外部網站

「瀏覽器」窗格是一個標籤式瀏覽器，因此您可以在執行中的應用程式旁邊開啟文件、問題追蹤器或任何其他網站。若要開啟「瀏覽器」，請在 macOS 上按 **Cmd+Shift+B** ，或在 Windows 上按 **Ctrl+Shift+B** ，或從**檢視** 選單中選擇它。當您點擊聊天中的外部連結時，選擇器會提供**在應用程式中開啟** 以使用「瀏覽器」窗格或**預設瀏覽器** 以使用您自己的；在 macOS 上按 **Cmd** 點擊或在 Windows 上按 **Ctrl** 點擊直接在您的系統瀏覽器中開啟連結。您可以登入窗格中的網站，包括彈出式登入流程，例如 Google OAuth。 Claude 可以使用與[驗證您的應用程式](https://code.claude.com/docs/zh-TW/desktop#preview-your-app)相同的工具讀取和互動外部頁面，並進行兩項額外的安全檢查：

- 安全分類器在每個權限模式中檢查 Claude 在外部頁面上的寫入操作，例如點擊和輸入。這些是[自動模式](https://code.claude.com/docs/zh-TW/desktop#choose-a-permission-mode)使用的相同分類器，當它們標記操作時，您會獲得權限提示，無論模式如何。
- 在「自動」和「略過權限」以外的權限模式中，在 Claude 導航到新網站之前也會應用網域允許清單檢查。

#### 核准 Claude 在網站上的操作

Claude 首次在外部網站上執行操作時，會出現權限卡，Claude 會等待您的選擇：**允許一次** 、**始終允許** 或**拒絕** 。**允許一次** 核准操作而不儲存任何內容。**始終允許** 在您的裝置上儲存該網站的核准，您可以在「設定」中撤銷它。每個網站都需要自己的核准，包括子網域。您的本機開發伺服器和專案檔案不需要核准，因此[自動驗證](https://code.claude.com/docs/zh-TW/desktop#auto-verify-changes)可以繼續進行而不會出現提示。 即使在已核准的網站上，Claude 也不會在沒有您的輸入的情況下購買商品、建立帳戶或繞過 CAPTCHA。在「瀏覽器」窗格中瀏覽使用與 [Chrome 中的 Claude 擴充功能](https://code.claude.com/docs/zh-TW/chrome)相同的安全模型。請參閱[安全地使用 Chrome 中的 Claude](https://support.claude.com/en/articles/12902428-using-claude-in-chrome-safely)以了解 Claude 如何處理敏感網站和危險操作。

#### 在「瀏覽器」和 Chrome 擴充功能之間選擇

「瀏覽器」窗格使用乾淨的瀏覽器設定檔，與您的個人瀏覽器分開，沒有您儲存的登入或歷史記錄。使用它來建立和測試您的應用程式，以及不需要您的身份的網站。當您想讓 Claude 在您的已登入工作階段中充當您時，請改用 [Chrome 中的 Claude 擴充功能](https://code.claude.com/docs/zh-TW/chrome)，它會共享您的瀏覽器的登入狀態。

#### 限制您的組織的外部瀏覽

「瀏覽器」遵循與 Claude in Chrome 擴充功能相同的[網站允許清單和封鎖清單控制](https://support.claude.com/en/articles/13065128-claude-in-chrome-admin-controls)。如果您的組織已為擴充功能設定了這些清單，「瀏覽器」會自動尊重它們。管理員也可以使用 [`browserExternalPageTools` 受管設定](https://code.claude.com/docs/zh-TW/desktop#managed-settings)關閉 Claude 在外部頁面上的工具。停用工具後，使用者仍然可以導航到外部網站；Claude 的工具無法讀取或對其進行操作。 若要完全關閉外部瀏覽，請將 [`disableBrowserExternalNavigation` 受管設定](https://code.claude.com/docs/zh-TW/desktop#managed-settings)設定為 `true`。這會阻止「瀏覽器」中的所有外部導航，包括您的組織允許清單上的網站；localhost 開發伺服器和檔案預覽保持運作。使用 `browserExternalPageTools` 讓使用者繼續瀏覽外部網站而不使用 Claude 的工具，並使用 `disableBrowserExternalNavigation` 為使用者和 Claude 阻止外部網站。

### 使用差異檢視檢查變更

Claude 對您的程式碼進行變更後，差異檢視可讓您在建立提取請求之前逐個檔案檢查修改。 當 Claude 變更檔案時，會出現差異統計指示器，顯示新增和移除的行數，例如 `+12 -1`。點擊此指示器以開啟差異檢視器，它在左側顯示檔案清單，在右側顯示每個檔案的變更。 若要對特定行進行評論，請點擊差異中的任何行以開啟評論框。輸入您的意見反應並按 **Enter** 鍵以新增評論。在多行新增評論後，一次提交所有評論：

- **macOS** ：按 **Cmd+Enter**
- **Windows** ：按 **Ctrl+Enter**

Claude 會讀取您的評論並進行要求的變更，這些變更會顯示為您可以檢查的新差異。

### 檢查您的程式碼

在差異檢視中，點擊右上角工具列中的**檢查程式碼** 以要求 Claude 在您提交之前評估變更。Claude 會檢查目前的差異並直接在差異檢視中留下評論。您可以回應任何評論或要求 Claude 進行修訂。 檢查著重於高信號問題：編譯錯誤、明確的邏輯錯誤、安全漏洞和明顯的錯誤。它不會標記樣式、格式、預先存在的問題或 linter 會捕捉的任何內容。

### 監控提取請求狀態

開啟提取請求後，CI 狀態列會出現在工作階段中。Claude Code 使用 GitHub CLI 輪詢檢查結果並顯示失敗。

- **自動修復** ：啟用後，Claude 會自動嘗試通過讀取失敗輸出並進行迭代來修復失敗的 CI 檢查。
- **自動合併** ：啟用後，Claude 會在所有檢查通過後合併 PR。合併方法是壓縮。首先在您的 [GitHub 儲存庫設定](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository)中啟用自動合併；沒有它，Claude 無法合併 PR。

使用 CI 狀態列中的**自動修復** 和**自動合併** 切換以啟用任一選項。Claude Code 也會在 CI 完成時傳送桌面通知。若要在 PR 合併或關閉後自動封存工作階段，請在「設定」→「Claude Code」中開啟[自動封存](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)。 PR 監控需要在您的機器上安裝並驗證 [GitHub CLI (`gh`)](https://cli.github.com/)。如果未安裝 `gh`，Desktop 會在您首次嘗試建立 PR 時提示您安裝它。

## 安排您的工作區

Code 標籤是圍繞您可以以任何佈局排列的窗格構建的：聊天、差異、瀏覽器、終端機、檔案、plan、tasks 和 subagent，以及 macOS 上的 [iOS Simulator](https://code.claude.com/docs/zh-TW/desktop-ios-simulator)。透過其標題拖動窗格以重新定位它，或拖動窗格邊緣以調整其大小。在 macOS 上按 \**Cmd+\** 或在 Windows 上按 \**Ctrl+\** 以關閉焦點窗格。從會話工具列中的 **Views** 選單開啟其他窗格。 若要跨螢幕工作，將窗格（例如差異或終端機）彈出到其自己的視窗中，完成後將其停靠回來。Claude 會在主視窗中繼續工作。 本節中的窗格佈局、終端機、檔案編輯器和檢視模式需要 Claude Desktop v1.2581.0 或更新版本。在 macOS 上開啟 **Claude → Check for Updates** 或在 Windows 上開啟 **Help → Check for Updates** 以更新。

### 在終端機中執行命令

整合終端機讓您在會話旁執行命令，而無需切換到另一個應用程式。從 **Views** 選單開啟它，或在 macOS 或 Windows 上按 \*\*Ctrl+`** 。終端機在您會話的工作目錄中開啟，並與 Claude 共用相同的環境，因此 `npm test`或`git status\` 等命令會看到 Claude 正在編輯的相同檔案。若要開啟第二個終端機標籤，請點擊終端機窗格標題中的 **+** 或右鍵點擊聊天中的資料夾以選擇 **Open in terminal** 。終端機僅在本機會話中可用。

### 開啟和編輯檔案

點擊聊天或差異檢視器中的檔案路徑以在檔案窗格中開啟它。HTML、PDF、影像和影片路徑改為在[瀏覽器窗格](https://code.claude.com/docs/zh-TW/desktop#preview-your-app)中開啟。進行現場編輯並點擊 **Save** 以寫回。如果自您開啟檔案以來檔案在磁碟上已變更，窗格會警告您並讓您覆蓋或放棄。點擊 **Discard** 以還原您的編輯，或點擊窗格標題中的路徑以複製絕對路徑。 檔案窗格在本機和 SSH 會話中可用。對於雲端會話，要求 Claude 進行變更。

### 在其他應用程式中開啟檔案

右鍵點擊聊天、差異檢視器或檔案窗格中的任何檔案路徑以開啟上下文選單：

- **Attach as context** ：將檔案新增到您的下一個提示
- **Open in** ：在已安裝的編輯器（如 VS Code、Cursor 或 Zed）中開啟檔案
- **Show in Finder** （在 macOS 上），**Show in Explorer** （在 Windows 上）：開啟包含資料夾
- **Copy path** ：將絕對路徑複製到您的剪貼簿

### 切換檢視模式

檢視模式控制聊天記錄中顯示多少詳細資訊。從傳送按鈕旁的 **Transcript view** 下拉式選單切換模式，或在 macOS 或 Windows 上按 **Ctrl+O** 以循環瀏覽它們。Thinking 模式僅在 Claude 在您正在檢視的會話中產生思考後才會出現在下拉式選單中。

| 模式                                                                                                                                                                                                                | 它顯示什麼                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **Normal**                                                                                                                                                                                                          | 工具呼叫摺疊成摘要，具有完整文字回應                              |
| **Thinking**                                                                                                                                                                                                        | 工具呼叫摺疊成摘要，加上 Claude 的思考                            |
| **Verbose**                                                                                                                                                                                                         | Claude 採取的每個工具呼叫、檔案讀取和中間步驟，加上 Claude 的思考 |
| 使用 Thinking 來追蹤 Claude 的推理，工具呼叫仍然摺疊。在調試 Claude 為什麼採取特定操作時使用 Verbose。Claude Desktop 1.46388.1 之前的版本也列出 Summary 模式，而仍設定為 Summary 的會話在您更新後會以 Normal 開啟。 |                                                                   |

### 快捷鍵

在 macOS 上按 **Cmd+/** 或在 Windows 上按 **Ctrl+/** 以查看 Code 標籤中可用的所有快捷鍵。在 Windows 上，對下面的快捷鍵使用 **Ctrl** 代替 **Cmd** 。會話循環、終端機切換和檢視模式切換在每個平台上都使用 **Ctrl** 。

| 快捷鍵                                                                                                                                                                                      | 操作                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `Cmd` `/`                                                                                                                                                                                   | 顯示快捷鍵             |
| `Cmd` `N`                                                                                                                                                                                   | 新會話                 |
| `Cmd` `W`                                                                                                                                                                                   | 關閉會話               |
| `Ctrl` `Tab` / `Ctrl` `Shift` `Tab`                                                                                                                                                         | 下一個或上一個會話     |
| `Cmd` `Shift` `]` / `Cmd` `Shift` `[`                                                                                                                                                       | 下一個或上一個會話     |
| `Esc`                                                                                                                                                                                       | 停止 Claude 的回應     |
| `Cmd` `Shift` `D`                                                                                                                                                                           | 切換差異窗格           |
| `Cmd` `Shift` `B`                                                                                                                                                                           | 切換瀏覽器窗格         |
| `Cmd` `Shift` `S`                                                                                                                                                                           | 在瀏覽器中選擇元素     |
| `Ctrl` \`\`\`                                                                                                                                                                               | 切換終端機窗格         |
| `Cmd` `\`                                                                                                                                                                                   | 關閉焦點窗格           |
| `Cmd` `;`                                                                                                                                                                                   | 開啟側邊聊天           |
| `Ctrl` `O`                                                                                                                                                                                  | 循環檢視模式           |
| `Cmd` `Shift` `M`                                                                                                                                                                           | 開啟權限模式選單       |
| `Cmd` `Shift` `I`                                                                                                                                                                           | 開啟模型選單           |
| `Cmd` `Shift` `E`                                                                                                                                                                           | 開啟工作量選單         |
| `1`–`9`                                                                                                                                                                                     | 在開啟的選單中選擇項目 |
| 這些快捷鍵僅適用於 Code 標籤。終端機型 [interactive mode 快捷鍵](https://code.claude.com/docs/zh-TW/interactive-mode#keyboard-shortcuts)（如 `Shift+Tab` 以循環權限模式）不適用於 Desktop。 |                        |

### 檢查使用情況

點擊模型選擇器旁的使用情況環以查看您目前的上下文視窗使用情況和您計畫在該期間的使用情況。上下文使用情況是按會話的；計畫使用情況在您所有 Claude Code 介面中共用。

## 讓 Claude 使用您的電腦

電腦使用讓 Claude 開啟您的應用程式、控制您的螢幕，並以您的方式直接在您的機器上工作。要求 Claude 與沒有 CLI 的桌面工具互動，或自動化只能透過 GUI 運作的內容。對於執行和測試 iOS 應用程式，Desktop 會開啟專用的 [iOS Simulator 窗格](https://code.claude.com/docs/zh-TW/desktop-ios-simulator)，而不是控制您的螢幕；該窗格無需啟用電腦使用即可運作。 電腦使用是 macOS 和 Windows 上的研究預覽版，需要 Pro 或 Max 計畫。它在 Team 或 Enterprise 計畫上不可用。Claude Desktop 應用程式必須執行。 電腦使用預設為關閉。[在設定中啟用它](https://code.claude.com/docs/zh-TW/desktop#enable-computer-use)，然後 Claude 才能控制您的螢幕。在 macOS 上，您還需要授予協助工具和螢幕錄製權限。 在 macOS 上，電腦使用也可以在背景執行：Claude 在您批准的應用程式中工作，同時您繼續工作。 與[沙箱化 Bash 工具](https://code.claude.com/docs/zh-TW/sandboxing)不同，電腦使用在您的實際桌面上執行，可以存取您批准的任何內容。Claude 會檢查每個操作並標記螢幕上內容的潛在提示注入，但信任邊界不同。有關最佳實踐，請參閱[電腦使用安全指南](https://support.claude.com/en/articles/14128542)。

### 何時應用電腦使用

Claude 有多種方式與應用程式或服務互動，電腦使用是最廣泛和最慢的。它首先嘗試最精確的工具：

- 如果您有服務的[連接器](https://code.claude.com/docs/zh-TW/desktop#connect-external-tools)，Claude 會使用連接器。
- 如果任務是 shell 命令，Claude 會使用 Bash。
- 如果任務是瀏覽器工作且您已設定[Chrome 中的 Claude](https://code.claude.com/docs/zh-TW/chrome)，Claude 會使用它。
- 如果任務是執行或測試 iOS 應用程式，Claude 會使用 [iOS Simulator 窗格](https://code.claude.com/docs/zh-TW/desktop-ios-simulator)，它不使用螢幕控制。
- 如果以上都不適用，Claude 會使用電腦使用。

[每個應用程式的存取層級](https://code.claude.com/docs/zh-TW/desktop#app-permissions)強化了這一點：瀏覽器限制為僅檢視，終端機和 IDE 限制為僅點擊，引導 Claude 使用專用工具，即使電腦使用處於活動狀態。螢幕控制保留給其他工具無法到達的內容，例如原生應用程式、硬體控制面板或沒有 API 的專有工具。

### 啟用電腦使用

電腦使用預設為關閉。如果您要求 Claude 執行需要它的操作而它處於關閉狀態，Claude 會告訴您如果在設定中啟用電腦使用，它可以執行該任務。 1 更新桌面應用程式 確保您有最新版本的 Claude Desktop。在 macOS 和 Windows 上，在 [claude.com/download](https://claude.com/download) 下載或更新；在 Linux 上，透過您的套件管理員更新（[說明](https://code.claude.com/docs/zh-TW/desktop-linux)）。然後重新啟動應用程式。 2 開啟切換 在桌面應用程式中，前往 **Settings > General**（在 **Desktop app** 下）。找到 **Computer use** 切換並開啟它。在 Windows 上，切換立即生效，設定完成。在 macOS 上，繼續下一步。如果您看不到切換，請確認您在 macOS 或 Windows 上使用 Pro 或 Max 計畫，然後更新並重新啟動應用程式。 3 授予 macOS 權限 在 macOS 上，在切換生效之前授予兩個系統權限：

- **Accessibility** ：讓 Claude 點擊、輸入和滾動
- **Screen Recording** ：讓 Claude 看到您螢幕上的內容

「設定」頁面顯示每個權限的目前狀態。如果任一被拒絕，點擊徽章以開啟相關的「系統設定」窗格。

### 應用程式權限

Claude 第一次需要使用應用程式時，會在您的會話中出現提示。點擊 **Allow for this session** 或 **Deny** 。批准在目前會話中持續，或在 [Dispatch 產生的會話](https://code.claude.com/docs/zh-TW/desktop#sessions-from-dispatch)中持續 30 分鐘。 提示也顯示 Claude 對該應用程式獲得的控制級別。這些層級由應用程式類別固定，無法變更：

| 層級                                                                                                                                                                                                             | Claude 可以執行的操作              | 適用於           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ---------------- |
| 僅檢視                                                                                                                                                                                                           | 在螢幕截圖中查看應用程式           | 瀏覽器、交易平台 |
| 僅點擊                                                                                                                                                                                                           | 點擊和滾動，但不能輸入或使用快捷鍵 | 終端機、IDE      |
| 完全控制                                                                                                                                                                                                         | 點擊、輸入、拖動和使用快捷鍵       | 其他所有內容     |
| 具有廣泛影響力的應用程式（如終端機、Finder 或檔案總管，以及「系統設定」或「設定」）在提示中顯示額外警告，以便您知道批准它們會授予什麼。 您可以在 **Settings > General**（在 **Desktop app** 下）中配置兩個設定： |                                    |                  |

- **Denied apps** ：在此處新增應用程式以拒絕它們而不提示。Claude 可能仍會透過允許應用程式中的操作間接影響被拒絕的應用程式，但它無法直接與被拒絕的應用程式互動。
- **Unhide apps when Claude finishes** ：當電腦使用未在背景執行時，Claude 工作時會隱藏您的其他視窗，以便它僅與批准的應用程式互動。當 Claude 完成時，隱藏的視窗會被恢復，除非您關閉此設定。

## 管理會話

每個會話都是一個獨立的對話，具有自己的上下文和變更。您可以並行執行多個會話、分支出側邊聊天、讓 Claude 檢查並傳送訊息到您的其他會話、將工作傳送到雲端，或讓 Dispatch 從您的手機為您啟動會話。

### 使用會話並行工作

點擊側邊欄中的 **+ New session** ，或在 macOS 上按 **Cmd+N** 或在 Windows 上按 **Ctrl+N** ，以並行處理多個任務。按 **Ctrl+Tab** 和 **Ctrl+Shift+Tab** 以循環瀏覽側邊欄中的會話。對於 Git 儲存庫，選擇分支名稱旁邊的 **worktree** 選項，以使用 [Git worktrees](https://code.claude.com/docs/zh-TW/worktrees) 為會話提供自己的隔離專案副本，因此一個會話中的變更不會影響其他會話，直到您提交它們。 若要同時檢視兩個會話，請在 macOS 上按住 **Cmd** 或在 Windows 上按住 **Ctrl** ，然後點擊側邊欄中的會話。會話會在您已開啟的會話旁邊的第二個窗格中開啟。當分割處於活動狀態時，點擊另一個側邊欄會話會取代具有焦點的窗格。在 macOS 上按 \**Cmd+\** 或在 Windows 上按 \**Ctrl+\** 以關閉焦點窗格並返回單一會話。 Worktrees 預設儲存在 `<project-root>/.claude/worktrees/` 中。您可以在「設定」→「Claude Code」下的「Worktree location」中將其變更為自訂目錄。您也可以設定一個分支前綴，該前綴會被加在每個 worktree 分支名稱前面，這對於保持 Claude 建立的分支井然有序很有用。若要在完成後移除 worktree，請將滑鼠懸停在側邊欄中的會話上，然後點擊存檔圖示。若要在 PR 合併或關閉後自動存檔會話，請在「設定」→「Claude Code」中開啟 **Auto-archive after PR merge or close** 。自動存檔僅適用於已完成執行的本機會話。 若要在新 worktrees 中包含 gitignored 檔案（如 `.env`），請在您的專案根目錄中建立 [`.worktreeinclude` 檔案](https://code.claude.com/docs/zh-TW/worktrees#copy-gitignored-files-into-worktrees)。 會話隔離需要 [Git](https://git-scm.com/downloads)。大多數 Mac 預設包含 Git。在終端機中執行 `git --version` 進行檢查；如果它列印版本號，表示已安裝 Git。如果您遇到 Git 錯誤，請在 [Cowork 標籤](https://claude.com/product/cowork) 中詢問 Claude 以幫助排除您的設定問題。 使用側邊欄頂部的控制項按狀態、專案或環境篩選會話，並按專案分組會話。若要重新命名會話，請點擊活動會話頂部工具列中的會話標題。 若要檢查上下文使用情況，請參閱[檢查使用情況](https://code.claude.com/docs/zh-TW/desktop#check-usage)。當上下文填滿時，Claude 會自動總結對話並繼續工作。您也可以輸入 `/compact` 來更早觸發總結並釋放上下文空間。有關壓縮如何運作的詳細資訊，請參閱[上下文視窗](https://code.claude.com/docs/zh-TW/how-claude-code-works#the-context-window)。 桌面應用程式會在 Code 會話完成任務且您目前未檢視該會話時傳送作業系統通知。對於屬於[專案](https://code.claude.com/docs/zh-TW/claude-projects#see-what-needs-you-in-overview)的會話，您會改為收到專案的通知。

### 在不偏離會話的情況下詢問側邊問題

側邊聊天讓您詢問 Claude 一個使用您會話上下文的問題，但不會將任何內容新增回主對話。當您想要理解一段程式碼、檢查假設或探索想法而不引導會話偏離時，請使用它。 在 macOS 上按 **Cmd+;** 或在 Windows 上按 **Ctrl+;** 以開啟側邊聊天，或在提示框中輸入 `/btw`。側邊聊天可以讀取主執行緒中到該點為止的所有內容。完成後，關閉側邊聊天並在您離開的地方繼續主會話。 側邊聊天在本機、SSH 和 WSL 會話中可用。桌面應用程式不會將側邊聊天儲存到磁碟，因此您在關閉應用程式後無法返回到一個。

### 觀看背景任務

任務窗格顯示在目前會話內執行的背景工作：子代理、背景 shell 命令和[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)。從 **Views** 選單開啟它或將其拖入您的佈局。 點擊任何項目以在子代理窗格中查看其輸出或停止它。若要查看其他會話正在執行的操作，請使用[側邊欄](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)，或詢問 Claude [為您檢查它們](https://code.claude.com/docs/zh-TW/desktop#work-across-sessions)。

### 跨會話工作

Claude 可以列出您的其他 Code 標籤會話、讀取每個會話一直在執行的操作，以及在它們之間傳送訊息。以純文字詢問：「哪個會話涉及了身份驗證重構？」、「API 會話得出了什麼結論？」或「告訴付款會話架構已變更」。您也可以詢問 Claude 重新命名或存檔會話。Claude 存檔會話的方式與側邊欄的存檔圖示相同，因此詢問它清理 PR 已合併的會話。 透過此介面，Claude 只能看到桌面應用程式本身執行的會話：本機、[SSH](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions) 和 Code 標籤中的 [WSL](https://code.claude.com/docs/zh-TW/desktop-wsl) 會話。Claude 看不到雲端會話，或您從終端機 CLI 或 VS Code 擴充功能啟動的會話，即使在同一專案的 worktrees 中也是如此，因此有九個終端機 worktrees 開啟和兩個桌面會話時，Claude 在其中一個回答會報告另一個桌面會話。Claude 永遠不會列出您詢問的會話。預設情況下，它會看到 20 個最近活躍的會話，並跳過已存檔的會話，除非您要求它們。[跨會話傳訊](https://code.claude.com/docs/zh-TW/cross-session-messaging)另外讓 Claude 傳送訊息到[您的其他 Claude Code 會話](https://code.claude.com/docs/zh-TW/cross-session-messaging#see-which-sessions-claude-can-reach)，包括終端機會話。 當 Claude 透過此介面傳送訊息到另一個會話時，Claude Code 會在那裡將其顯示為一張卡片，標籤為傳送會話的標題和返回連結，因此您總是可以看到訊息來自何處。如果接收會話正在執行任務中，Claude Code 會保留訊息，Claude 會在目前工作完成後讀取它。接收 Claude 可以回覆，Claude Code 會透過此介面傳遞回覆。Claude 無法傳遞到已存檔的會話，並會在訊息未通過時告訴您。 Claude Code 在會話間應用四個安全行為：

- 在存檔任何會話之前，Claude 會先詢問您。您會在每個權限模式中看到批准卡片，包括自動和略過權限。
- 透過此介面，Claude 無法從沒有人監視的會話（例如排程任務執行）傳送跨會話訊息，也無法傳遞訊息到一個。
- Claude Code 會根據接收會話的[入站控制](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)檢查來自此介面的每條訊息，即使接收會話本身沒有[跨會話傳訊](https://code.claude.com/docs/zh-TW/cross-session-messaging#availability)。如果您在接收會話中將 [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound) 設定為 `refuse`，Claude Code 會丟棄來自此介面的訊息。Claude Code 會向 Claude 桌面應用程式報告拒絕。在 v2.1.234 之前，Claude Code 會丟棄來自此介面到沒有跨會話傳訊的接收會話的每條訊息。
- Claude Code 引用每條傳入訊息並將其歸因於傳送它的會話，Claude 在對其進行操作時仍然遵循接收會話自己的權限設定。

Claude 也可以建議新會話。當它注意到值得修復但超出目前任務範圍的內容時，它會在聊天中提供工作作為任務晶片。點擊晶片以在具有自己 worktree 的新會話中啟動該工作；Claude 會不中斷地繼續您的目前會話。

### 在雲端執行長時間執行的任務

對於大型重構、測試套件、遷移或其他長時間執行的任務，在開始會話時選擇 **Cloud** 而不是 **Local** 。雲端會話預設在 Anthropic 管理的基礎設施上執行，即使您關閉應用程式或關閉電腦，也會繼續執行。隨時檢查以查看進度或引導 Claude 朝不同方向發展。您也可以從 [claude.ai/code](https://claude.ai/code) 或 [Claude 行動應用程式](https://code.claude.com/docs/zh-TW/mobile)監控雲端會話。 雲端會話也支援多個儲存庫。選擇雲端環境後，點擊所選儲存庫旁邊的 **+** 按鈕，將其他儲存庫新增到會話。每個儲存庫都有自己的分支選擇器。這對於跨越多個程式碼庫的任務很有用，例如更新共用程式庫及其使用者。 有關雲端會話如何運作的更多資訊，請參閱[在網路上使用 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)。當一項工作需要許多雲端會話時，請在側邊欄中選擇 **Projects** 以建立[專案](https://code.claude.com/docs/zh-TW/claude-projects)，Claude 會從一個對話中為您啟動並追蹤會話。

### 在另一個介面中繼續

**Continue in** 選單可從會話工具列右下角的 VS Code 圖示存取，可讓您將會話移至另一個介面：

- **Claude Code on the Web** ：將您的本機會話傳送到雲端繼續執行。Desktop 推送您的分支、產生對話摘要，並使用完整上下文建立新的雲端會話。然後您可以選擇存檔本機會話或保留它。這需要乾淨的工作樹，不適用於 SSH 會話。
- **Your IDE** ：在目前工作目錄的支援 IDE 中開啟您的專案。

### 來自 Dispatch 的會話

[Dispatch](https://support.claude.com/en/articles/13947068) 是與 Claude 的持久對話，存在於 [Cowork](https://claude.com/product/cowork) 標籤中。您向 Dispatch 傳送任務，它決定如何處理它。 任務可以透過兩種方式成為 Code 會話：您直接要求一個，例如「開啟 Claude Code 會話並修復登入錯誤」，或 Dispatch 決定任務是開發工作並自行產生一個。通常路由到 Code 的任務包括修復錯誤、更新相依性、執行測試或開啟提取請求。研究、文件編輯和試算表工作保留在 Cowork 中。 無論哪種方式，Code 會話都會在 Code 標籤的側邊欄中出現，帶有 **Dispatch** 徽章。當它完成或需要您的批准時，您會在手機上收到推送通知。 如果您已[啟用電腦使用](https://code.claude.com/docs/zh-TW/desktop#let-claude-use-your-computer)，Dispatch 產生的 Code 會話也可以使用它。這些會話中的應用程式批准在 30 分鐘後過期並重新提示，而不是像常規 Code 會話那樣持續整個會話。 有關設定、配對和 Dispatch 設定，請參閱 [Dispatch 幫助文章](https://support.claude.com/en/articles/13947068)。Dispatch 需要 Pro 或 Max 計畫，在 Team 或 Enterprise 計畫上不可用。 Dispatch 是當您遠離終端機時與 Claude 合作的多種方式之一。如需與其他選項的比較，請參閱[平台和整合](https://code.claude.com/docs/zh-TW/platforms#work-when-you-are-away-from-your-terminal)。

## 擴展 Claude Code

連接外部服務、新增可重複使用的工作流程、自訂 Claude 的行為，並配置預覽伺服器。若要在一個地方管理連接器、skills 和 plugins，請點擊側邊欄中的 **Customize** 。[Cowork](https://claude.com/product/cowork) 標籤在桌面應用程式中從此 Customize 配置取得其 skills、plugins 和連接器，該配置透過您的 claude.ai 帳戶同步，而不是從 CLI 的 `~/.claude` 目錄。 Claude Code 也會在您使用相同帳戶登入的終端機會話中載入為您的 claude.ai 帳戶啟用的 skills 和 plugins。請參閱 [Skills synced from claude.ai](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave) 和 [Plugins synced from claude.ai](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)。

### 連接外部工具

對於本機和 [SSH](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions) 會話，點擊提示框旁的 **+** 按鈕，然後選擇 **Connectors** 以新增 Google Calendar、Slack、GitHub、Linear、Notion 等整合。您可以在會話之前或期間新增連接器。**+** 按鈕在雲端或 WSL 會話中不可用，但 [routines](https://code.claude.com/docs/zh-TW/routines) 在 routine 建立時配置連接器。 若要管理或斷開連接器，請在桌面應用程式中前往「設定」→「Connectors」，或從提示框中的「Connectors」選單中選擇 **Manage connectors** 。 連接後，Claude 可以讀取您的日曆、傳送訊息、建立問題，並直接與您的工具互動。您可以詢問 Claude 在您的會話中配置了哪些連接器。 連接器是 [MCP servers](https://code.claude.com/docs/zh-TW/mcp)，具有圖形設定流程。使用它們可以快速與支援的服務整合。對於「Connectors」中未列出的整合，透過 [settings files](https://code.claude.com/docs/zh-TW/mcp#installing-mcp-servers) 手動新增 MCP servers。您也可以 [create custom connectors](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp)。

### 使用 skills

[Skills](https://code.claude.com/docs/zh-TW/skills) 擴展 Claude 可以執行的操作。Claude 在相關時自動載入它們，或者您可以直接呼叫一個：在提示框中輸入 `/` 或點擊 **+** 按鈕並選擇 **Slash commands** 以瀏覽可用的內容。這包括 [built-in commands](https://code.claude.com/docs/zh-TW/commands)、您的 [custom skills](https://code.claude.com/docs/zh-TW/skills#create-your-first-skill)、來自您程式碼庫的專案 skills，以及來自任何 [installed plugins](https://code.claude.com/docs/zh-TW/plugins) 的 skills。選擇一個，它會在輸入欄位中突出顯示。在其後輸入您的任務並照常傳送。 您可以在 Claude 正在工作時傳送命令，就像任何其他訊息一樣，會話在回合完成後會回到閒置狀態。在 v2.1.206 之前，在回合中途傳送的命令可能會導致會話顯示為執行中，而您之後傳送的訊息未被傳遞。 本機會話從 `~/.claude/skills/` 載入您的個人 skills。[SSH](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions) 會話從遠端主機的主目錄讀取 `~/.claude/skills/`，而不是從您的機器。 本機和雲端會話也會載入為您的 claude.ai 帳戶啟用的 skills。雲端會話改為載入它們，而不是 `~/.claude/skills/`，如 [Skills in Cowork and cloud sessions](https://code.claude.com/docs/zh-TW/skills#skills-in-cowork-and-cloud-sessions) 所述。

### 安裝 plugins

[Plugins](https://code.claude.com/docs/zh-TW/plugins) 是可重複使用的套件，可將 skills、agents、hooks、MCP servers 和 LSP 配置新增到 Claude Code。您可以從桌面應用程式安裝 plugins，而無需使用終端機。 對於本機和 [SSH](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions) 會話，點擊提示框旁的 **+** 按鈕，然後選擇 **Plugins** 以查看您已安裝的 plugins 及其 skills。若要新增 plugin，從子選單中選擇 **Add plugin** 以開啟 plugin 瀏覽器，它顯示來自您配置的 [marketplaces](https://code.claude.com/docs/zh-TW/plugin-marketplaces)（包括官方 Anthropic 市場）的可用 plugins。選擇 **Manage plugins** 以啟用、停用或解除安裝 plugins。 您可以將 plugins 限定於您的使用者帳戶、特定專案或僅本機。如果您的組織集中管理 plugins，這些 plugins 在桌面會話中的可用方式與在 CLI 中相同。 plugin 瀏覽器在雲端會話中不可用，而且您從桌面應用程式安裝的 plugins 不適用於雲端會話。若要在雲端會話中使用 plugin，請在儲存庫的 `.claude/settings.json` 中的 [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 下宣告它，以便 Claude Code [在會話開始時安裝它](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)，或為您的 claude.ai 帳戶啟用它，以便 Claude Code 將其載入為 [synced plugin](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)。Plugins 在 WSL 會話中不可用。有關完整的 plugin 參考（包括建立您自己的 plugins），請參閱 [plugins](https://code.claude.com/docs/zh-TW/plugins)。

### 配置預覽伺服器

Claude 會自動偵測您的開發伺服器設定，並將配置儲存在您開始會話時選擇的資料夾根目錄中的 `.claude/launch.json`。Preview 使用此資料夾作為其工作目錄，因此如果您選擇了父資料夾，具有自己開發伺服器的子資料夾將不會自動偵測。若要使用子資料夾的伺服器，請直接在該資料夾中開始會話，或手動新增配置。 若要自訂伺服器的啟動方式，例如使用 `yarn dev` 而不是 `npm run dev` 或變更連接埠，請手動編輯檔案或點擊伺服器下拉式選單中的 **Edit configuration** 以在您的程式碼編輯器中開啟它。該檔案支援帶註解的 JSON。

```
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "my-app",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 3000
    }
  ]
}

```

您可以定義多個配置以從同一專案執行不同的伺服器，例如前端和 API。請參閱下面的 [examples](https://code.claude.com/docs/zh-TW/desktop#examples)。

#### 自動驗證變更

啟用 `autoVerify` 時，Claude 會在編輯檔案後自動驗證程式碼變更。它會擷取螢幕截圖、檢查錯誤，並在完成回應之前確認變更有效。 自動驗證預設為開啟。透過將 `"autoVerify": false` 新增到 `.claude/launch.json`，或從伺服器下拉式選單切換它，按專案停用它。

```
{
  "version": "0.0.1",
  "autoVerify": false,
  "configurations": [
    {
      "name": "my-app",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 3000
    }
  ]
}

```

停用後，預覽工具仍然可用，您可以隨時要求 Claude 進行驗證。自動驗證使其在每次編輯後自動進行。

#### 配置欄位

`configurations` 陣列中的每個項目接受以下欄位：

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 類型     | 描述                                                                                                                                                                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | string   | 此伺服器的唯一識別碼                                                                                                                                                                                                                                    |
| `runtimeExecutable`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | string   | 要執行的命令，例如 `npm`、`yarn` 或 `node`                                                                                                                                                                                                              |
| `runtimeArgs`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | string[] | 傳遞給 `runtimeExecutable` 的引數，例如 `["run", "dev"]`                                                                                                                                                                                                |
| `port`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | number   | 您的伺服器監聽的連接埠。預設為 3000                                                                                                                                                                                                                     |
| `cwd`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | string   | 相對於您的專案根目錄的工作目錄。預設為專案根目錄。使用 `${workspaceFolder}` 明確參考專案根目錄                                                                                                                                                          |
| `env`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | object   | 其他環境變數作為鍵值對，例如 `{ "NODE_ENV": "development" }`。不要在此處放置機密，因為此檔案會提交到您的儲存庫。若要將機密傳遞到您的開發伺服器，請在 [local environment editor](https://code.claude.com/docs/zh-TW/desktop#local-sessions) 中設定它們。 |
| `autoPort`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | boolean  | 如何處理連接埠衝突。請參閱 [Port conflicts](https://code.claude.com/docs/zh-TW/desktop#port-conflicts)                                                                                                                                                  |
| `program`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | string   | 使用 `node` 執行的指令碼。請參閱 [when to use `program` vs `runtimeExecutable`](https://code.claude.com/docs/zh-TW/desktop#when-to-use-program-vs-runtimeexecutable)                                                                                    |
| `args`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | string[] | 傳遞給 `program` 的引數。僅在設定 `program` 時使用                                                                                                                                                                                                      |
| `url`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | string   | preview 開啟的位址，而不是 `http://localhost:<port>`。請參閱 [open the preview at a specific URL](https://code.claude.com/docs/zh-TW/desktop#open-the-preview-at-a-specific-url)                                                                        |
| 使用 `runtimeExecutable` 搭配 `runtimeArgs` 透過套件管理器啟動開發伺服器。例如，`"runtimeExecutable": "npm"` 搭配 `"runtimeArgs": ["run", "dev"]` 執行 `npm run dev`。 當您有想要直接使用 `node` 執行的獨立指令碼時，使用 `program`。例如，`"program": "server.js"` 執行 `node server.js`。使用 `args` 傳遞其他標誌。 根據預設，preview 開啟 `http://localhost:<port>`。當您的伺服器需要不同的位址時，設定 `url`。常見情況是需要本機 HTTPS 的伺服器、使用 `*.localhost` 子網域的應用程式，以及透過重新導向登入您的應用程式。 |          |                                                                                                                                                                                                                                                         |

```
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "my-app",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 8443,
      "url": "https://localhost:8443"
    }
  ]
}

```

Localhost 位址直接開啟，完全像預設連接埠位址一樣。這包括 `localhost`、任何 `*.localhost` 子網域、`127.0.0.1` 和 `::1`。基於安全考量，localhost `url` 必須只是您伺服器的來源 — 沒有路徑或查詢，且連接埠必須符合項目的連接埠。若要顯示特定頁面，請在 preview 開啟後要求 Claude 導覽到該處。具有路徑、查詢或不符合連接埠的 localhost `url` 會報告為配置錯誤，該錯誤會命名 url 並顯示修正。 對於任何其他位址，Desktop 會在 preview 首次開啟它時要求您的許可，就像您在 preview 中瀏覽到新網站時一樣。外部位址可能包括路徑。選擇 **Always allow** 以在未來跳過該網站的提示。限制 preview 中外部網站的組織原則仍然適用。 若要預覽您已經自己執行的伺服器，請設定 `url` 而不設定命令。Claude 會將 preview 附加到您執行中的伺服器，而不是啟動一個：

```
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "my-app",
      "url": "https://app.localhost:3000"
    }
  ]
}

```

`url` 必須是 `http` 或 `https`，且不得包含使用者名稱或密碼。

#### 連接埠衝突

`autoPort` 欄位控制當您偏好的連接埠已在使用時會發生什麼：

- **`true`**：Claude 自動尋找並使用空閒連接埠。適合大多數開發伺服器。
- **`false`**：Claude 失敗並出現錯誤。當您的伺服器必須使用特定連接埠時使用此選項，例如 OAuth 回呼或 CORS 允許清單。
- **未設定（預設）** ：Claude 詢問伺服器是否需要該確切連接埠，然後儲存您的答案。

當 Claude 選擇不同的連接埠時，它會透過 `PORT` 環境變數將指派的連接埠傳遞給您的伺服器。

#### 範例

這些配置顯示不同專案類型的常見設定：

- Next.js
- Multiple servers
- Node.js script

此配置使用 Yarn 在連接埠 3000 上執行 Next.js 應用程式：

```
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "web",
      "runtimeExecutable": "yarn",
      "runtimeArgs": ["dev"],
      "port": 3000
    }
  ]
}

```

對於具有前端和 API 伺服器的 monorepo，定義多個配置。前端使用 `autoPort: true`，因此如果 3000 被佔用，它會選擇空閒連接埠，而 API 伺服器需要確切的連接埠 8080：

```
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "frontend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "cwd": "apps/web",
      "port": 3000,
      "autoPort": true
    },
    {
      "name": "api",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "start"],
      "cwd": "server",
      "port": 8080,
      "env": { "NODE_ENV": "development" },
      "autoPort": false
    }
  ]
}

```

若要直接執行 Node.js 指令碼而不是使用套件管理器命令，請使用 `program` 欄位：

```
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "server",
      "program": "server.js",
      "args": ["--verbose"],
      "port": 4000
    }
  ]
}

```

## 環境配置

您在[開始會話](https://code.claude.com/docs/zh-TW/desktop#start-a-session)時選擇的環境決定了 Claude 執行的位置以及您如何連接：

- **Local** ：在您的機器上執行，直接存取您的檔案
- **Cloud** ：在 Anthropic 管理的基礎設施上執行。即使您關閉應用程式，會話也會繼續。
- **SSH** ：在您透過 SSH 連接的遠端機器上執行，例如您自己的伺服器、雲端虛擬機器或開發容器
- **WSL** (Windows)：在您機器上的 [WSL 2 發行版](https://code.claude.com/docs/zh-TW/desktop-wsl)內執行，使用其 Linux 工具鏈和原生路徑

### 本機會話

桌面應用程式並不總是繼承您的完整 shell 環境。在 macOS 上，當您從 Dock 或 Finder 啟動應用程式時，它會讀取您的 shell 設定檔（如 `~/.zshrc` 或 `~/.bashrc`）以提取 `PATH` 和一組固定的 Claude Code 變數，但您在那裡匯出的其他變數不會被拾取。在 Windows 上，應用程式繼承使用者和系統環境變數，但不讀取 PowerShell 設定檔。 若要在任何平台上為本機會話和開發伺服器設定環境變數，請在提示框中開啟環境下拉式選單，將滑鼠懸停在 **Local** 上，然後點擊齒輪圖示以開啟本機環境編輯器。您在此處儲存的變數會在您的機器上加密儲存，並適用於您啟動的每個本機會話和預覽伺服器。您也可以將變數新增到 `~/.claude/settings.json` 檔案中的 `env` 金鑰，儘管這些僅到達 Claude 會話而不是開發伺服器。有關支援的變數的完整清單，請參閱[環境變數](https://code.claude.com/docs/zh-TW/env-vars)。 [Extended thinking](https://code.claude.com/docs/zh-TW/model-config#extended-thinking) 預設啟用，這改進了複雜推理任務的效能，但使用額外的 tokens。在 Anthropic API 上，在本機環境編輯器中將 `MAX_THINKING_TOKENS` 設定為 `0` 以關閉思考；這對 Fable 模型沒有影響，Fable 模型始終使用 extended thinking。在 Anthropic API 上關閉思考後，Claude Code 會傳送 effort `high` 而不是更高的級別給它知道[不接受該組合](https://code.claude.com/docs/zh-TW/errors#effort-isnt-available-with-thinking-turned-off)的模型，例如 Opus 5。 在具有[自適應推理](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)的模型上，除了 `0` 以外的 `MAX_THINKING_TOKENS` 值會被忽略，因為自適應推理控制思考深度。在 Opus 4.6 和 Sonnet 4.6 上，將 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` 設定為 `1` 以使用固定思考預算；Fable 模型、Sonnet 5 和 Opus 4.7 及更新版本始終使用自適應推理，沒有固定預算模式。

#### 受管設備上的本機會話

您的管理員可以使用 [`disableDesktopLocalSessions` 受管設定](https://code.claude.com/docs/zh-TW/desktop#managed-settings)關閉本機會話。當他們這樣做時，**Local** 會保留在環境下拉式選單中，但會呈灰色且無法選擇，並顯示工具提示說您的組織已關閉它，在 Windows 上，[WSL](https://code.claude.com/docs/zh-TW/desktop-wsl) 項目（其在受管設備上的可用性[由單獨管理](https://code.claude.com/docs/zh-TW/admin-setup#wsl-sessions-in-claude-code-desktop)）也會以相同方式呈灰色。新會話預設為第一個 SSH 連線（如果已配置），如果您嘗試繼續現有會話，Desktop 會顯示一條訊息，說明此設備上不提供本機會話。改為選擇 [SSH](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions) 或 [Cloud](https://code.claude.com/docs/zh-TW/desktop#cloud-sessions) 環境，或聯絡您的 IT 團隊。

### 雲端會話

雲端會話即使您關閉應用程式也會在背景繼續。使用情況計入您的[訂閱計畫限制](https://code.claude.com/docs/zh-TW/costs)，沒有單獨的計算費用。 您可以建立具有不同網路存取級別和環境變數的自訂雲端環境。在開始雲端會話時，開啟提示框中的環境下拉式選單以管理它們：

- **Add an environment** ：選擇 **Add cloud environment**
- **Edit or archive one of your own environments** ：將滑鼠懸停在它上面並點擊齒輪圖示

有關配置網路存取和環境變數的詳細資訊，請參閱[配置雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)。

### SSH 會話

SSH 會話可讓您在遠端機器上執行 Claude Code，同時使用桌面應用程式作為您的介面。這對於使用存在於雲端虛擬機器、開發容器或具有特定硬體或相依性的伺服器上的程式碼庫很有用。 若要新增 SSH 連線，請在開始會話前點擊環境下拉式選單，然後選擇 **+ Add SSH connection** 。對話框要求：

- **Name** ：此連線的友善標籤
- **SSH Host** ：`user@hostname` 或在 `~/.ssh/config` 中定義的主機
- **SSH Port** ：如果留空則預設為 22，或使用您的 SSH 配置中的連接埠
- **Identity File** ：您的私鑰的路徑，例如 `~/.ssh/id_rsa`。留空以使用預設金鑰或您的 SSH 配置。

新增後，連線會出現在環境下拉式選單中。選擇它以在該機器上啟動會話。Claude 在遠端機器上執行，可存取其檔案和工具。 遠端機器必須執行 Linux 或 macOS。桌面應用程式會在您第一次連接時自動在遠端機器上安裝 Claude Code。連接後，SSH 會話支援權限模式、連接器、plugins 和 MCP servers。

#### 為您的團隊預先配置 SSH 連線

管理員可以透過將 `sshConfigs` 新增到[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)檔案來將 SSH 連線分發給團隊成員。以這種方式定義的連線會自動出現在每個使用者的環境下拉式選單中，並顯示為受管，因此使用者可以選擇它們，但無法在應用程式中編輯或刪除它們。 以下範例預先配置了一個單一連線：

```
{
  "sshConfigs": [
    {
      "id": "shared-dev-vm",
      "name": "Shared Dev VM",
      "sshHost": "user@dev.example.com",
      "sshPort": 22,
      "sshIdentityFile": "~/.ssh/id_ed25519"
    }
  ]
}

```

每個項目都需要 `id`、`name` 和 `sshHost`。`sshPort` 和 `sshIdentityFile` 欄位是選用的。使用者也可以將 `sshConfigs` 新增到他們自己的 `~/.claude/settings.json`，這是透過對話框新增的連線的儲存位置。

#### 限制使用者可以連接的 SSH 主機

管理員可以透過將 `sshHostAllowlist` 新增到[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)檔案來限制 Desktop 的 SSH 會話到已核准的主機集合。設定後，使用者只能連接到其解析的主機名稱與其中一個模式相符的主機。將其設定為空陣列以完全停用 SSH 會話。 以下範例允許連接到 `devboxes.example.com` 下的任何主機以及單一命名的堡壘主機：

```
{
  "sshHostAllowlist": ["*.devboxes.example.com", "bastion.example.com"]
}

```

模式不區分大小寫。`*` 符合任何主機，`*.example.com` 符合 `example.com` 和任何子網域。其他任何內容都是精確符合。檢查會針對透過 `ssh -G` 進行 `~/.ssh/config` 解析後的主機名稱執行，因此允許 `Host` 別名和 `ProxyCommand`/`ProxyJump` 項目，只要解析的 `HostName` 相符即可。 `sshHostAllowlist` 僅從受管設定讀取；使用者或專案設定中的值會被忽略。只有 Claude Desktop 應用程式遵守此設定；Claude Code CLI 和 IDE 擴充功能不讀取它，它也不限制透過 Bash 工具執行的 `ssh` 命令。它控制 Desktop 應用程式連接的主機，而不是網路出口，因此如果您需要硬邊界，請將其與您組織的網路或零信任控制配對。

## 企業配置

Teams 或 Enterprise 計畫上的組織可以透過管理員主控台控制、受管設定檔案和裝置管理原則來管理桌面應用程式行為。

### 管理員主控台控制

這些設定透過[管理員設定主控台](https://claude.ai/admin-settings/claude-code)配置：

- **Desktop 中的 Code** ：控制您組織中的使用者是否可以在桌面應用程式中存取 Claude Code
- **網路上的 Code** ：為您的組織啟用或停用[網路會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)
- **遠端控制** ：為您的組織啟用或停用[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)
- **停用略過權限模式** ：防止您組織中的使用者啟用略過權限模式

### 受管設定

受管設定會覆蓋專案和使用者設定，並在 Desktop 中的 Claude Code 會話時套用。您可以在您組織的[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)檔案中設定這些金鑰，或透過管理員主控台遠端推送它們。

| 金鑰                                                                                                                                                                                                                                                                                                                   | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `permissions.disableBypassPermissionsMode`                                                                                                                                                                                                                                                                             | 設定為 `"disable"` 以防止使用者啟用略過權限模式。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `disableAutoMode`                                                                                                                                                                                                                                                                                                      | 設定為 `"disable"` 以從模式選擇器中移除 [Auto](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 模式。也在 `permissions` 下接受。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `autoMode`                                                                                                                                                                                                                                                                                                             | 自訂 auto 模式分類器在您的組織中信任和阻止的內容。請參閱[配置 auto 模式](https://code.claude.com/docs/zh-TW/auto-mode-config)。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `browserExternalPageTools`                                                                                                                                                                                                                                                                                             | 設定為 `"disabled"` 以防止 Claude 使用工具來讀取或作用於[瀏覽器窗格](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)中的外部頁面。使用者仍然可以自行瀏覽外部網站，本機開發伺服器預覽不受影響。                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `disableMobileSimulatorTools`                                                                                                                                                                                                                                                                                          | 設定為 `true` 以阻止 Claude 在 [iOS Simulator 窗格](https://code.claude.com/docs/zh-TW/desktop-ios-simulator#turn-off-simulator-access)中控制和擷取裝置的工具。該窗格仍可供使用者自己的點擊使用；只有 Claude 的存取被移除。該值必須是 JSON 布林值 `true`；字串 `"true"` 會被忽略。                                                                                                                                                                                                                                                                                                                                                                                               |
| `disableBrowserExternalNavigation`                                                                                                                                                                                                                                                                                     | 設定為 `true` 以完全關閉[瀏覽器窗格](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)中的外部瀏覽。使用者和 Claude 都無法瀏覽外部網站，localhost 開發伺服器預覽不受影響。該值必須是 JSON 布林值 `true`；字串 `"true"` 會被忽略。                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `sshConfigs`                                                                                                                                                                                                                                                                                                           | 預先配置[SSH 連線](https://code.claude.com/docs/zh-TW/desktop#pre-configure-ssh-connections-for-your-team)，在環境下拉式選單中顯示。使用者無法編輯或刪除受管連線。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `sshHostAllowlist`                                                                                                                                                                                                                                                                                                     | 限制 [SSH 會話](https://code.claude.com/docs/zh-TW/desktop#restrict-which-ssh-hosts-users-can-connect-to)連線到已解析主機名稱符合這些模式之一的主機。空陣列會停用 SSH 會話。僅從受管設定讀取。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `disableDesktopLocalSessions`                                                                                                                                                                                                                                                                                          | 設定為 `true` 以關閉[在裝置上執行的 Code 會話](https://code.claude.com/docs/zh-TW/desktop#local-sessions-on-managed-devices)，只保留 SSH 會話到其他主機和雲端會話。該值必須是 JSON 布林值 `true`。僅從受管設定讀取。需要 Claude Desktop v1.37937.0 或更新版本。                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `managedMcpServers`                                                                                                                                                                                                                                                                                                    | 將 MCP 伺服器配置推送到所有使用者。僅在第三方 (3P) Desktop 部署中可用。在每個項目中，設定 `"http"`、`"sse"` 或 `"stdio"` 的傳輸、連線詳細資訊，以及可選的 `toolPolicy` 對應，限制該伺服器中使用者可以叫用的工具。透過受管設定檔案、MDM 或 Claude apps gateway 原則的 [`desktop` 區塊](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#claude-desktop-overlay)傳遞，因為第三方部署不會收到管理員主控台設定。若要透過閘道傳遞，您需要閘道伺服器上的 Claude Code v2.1.232 或更新版本。這是桌面應用程式自己的金鑰；Claude Code 讀取自己的[同名受管設定](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings)，具有不同的項目形狀。 |
| 哪些受管設定到達 Desktop 會話取決於該會話執行的位置。模型限制（例如 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)）在 Desktop 的 Claude Code 會話中的強制方式與終端 CLI 相同；請參閱[表面涵蓋範圍](https://code.claude.com/docs/zh-TW/model-config#surface-coverage)。 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

- **此機器上的本機會話** ：部署到磁碟的受管設定檔案適用。透過管理員主控台推送的遠端受管設定在會話使用[符合條件的登入或金鑰](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)向 Anthropic 的 API 進行驗證時也會到達這些會話，遵循與終端 CLI 相同的[設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)。
- **[雲端會話](https://code.claude.com/docs/zh-TW/desktop#cloud-sessions)** ：接收[伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings)；裝置部署的檔案無法到達它們，因為它們在 Anthropic 管理的 VM 上執行。路由到[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)的會話也讀取執行器映像中的受管設定檔案。[Claude Code 如何結合受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)說明該檔案何時適用。
- **[SSH 會話](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions)** ：會話從遠端主機讀取受管設定檔案。Desktop 本身從本機機器的受管設定讀取 `sshConfigs`、`sshHostAllowlist` 和 `disableDesktopLocalSessions`。
- **[Cowork](https://claude.com/docs/cowork/overview) 會話**：在此機器上的 Cowork 會話中，Claude Code 永遠不會擷取管理員主控台設定，即使使用者使用 Team 或 Enterprise 帳戶登入，並讀取部署到機器的原則，除非您的 Claude Desktop 配置設定 `requireCoworkFullVmSandbox`。遠端 Cowork 會話都不會接收。請參閱[原則適用的位置和時間](https://code.claude.com/docs/zh-TW/managed-settings#where-and-when-a-policy-applies)以了解哪些裝置檔案到達 Cowork，以及[MCP 權限規則](https://code.claude.com/docs/zh-TW/permissions#mcp)以了解 `Bash` 和 `WebFetch` 規則如何適用於 Cowork 的工具。

在本機和 SSH 會話中，桌面應用程式直接將每個使用者連線的 claude.ai 連接器傳遞給 Claude Code。無論您使用哪個設定來源或檔案位置，都沒有 MCP 設定或 `managed-mcp.json` 到達這些連接器。若要在這些會話中阻止連接器的工具，請使用您組織的[連接器工具控制](https://code.claude.com/docs/zh-TW/mcp#organization-controls-on-connector-tools)。[連接器如何到達 Claude Code](https://code.claude.com/docs/zh-TW/mcp#how-connectors-reach-claude-code)顯示哪些設定在每種會話中管理連接器。 `permissions.disableBypassPermissionsMode` 和 `disableAutoMode` 也在使用者和專案設定中運作，但將它們放在受管設定中可防止使用者覆蓋它們。 有關只有受管來源可以設定的權限、外掛程式和傳遞金鑰，請參閱[只有受管設定可以設定的金鑰](https://code.claude.com/docs/zh-TW/managed-settings#managed-only-settings)。

### 裝置管理原則

IT 團隊可以透過 macOS 上的 MDM 或 Windows 上的群組原則來管理桌面應用程式。可用的原則包括啟用或停用 Claude Code 功能、控制自動更新和設定自訂部署 URL。

- **macOS** ：使用 Jamf 或 Kandji 等工具透過 `com.anthropic.claudefordesktop` 偏好設定網域配置
- **Windows** ：透過 `SOFTWARE\Policies\Claude` 的登錄配置

### 網路存取需求

Desktop 從 Anthropic CDN 主機載入其應用程式程式碼和使用者內容。

```
anthropic.com
*.anthropic.com
claude.ai
*.claude.ai
claude.com
*.claude.com
claude.app
*.claude.app
*.claudeusercontent.com
*.claudemcpcontent.com

```

流量在連接埠 443 上使用 HTTPS，除非您為 [OTLP](https://code.claude.com/docs/zh-TW/monitoring-usage)、LLM 閘道或 MCP 伺服器配置自訂連接埠。 對於代理伺服器、自訂憑證授權單位、mTLS 和獨立 CLI 需要的網域，請參閱[網路配置](https://code.claude.com/docs/zh-TW/network-config)。 若要減少防火牆萬用字元的數量，請改為允許這些 Anthropic 主機。某些子網域是動態產生的，必須保持為萬用字元。

```
anthropic.com
api.anthropic.com
a-api.anthropic.com
a-cdn.anthropic.com
s-cdn.anthropic.com
assets-proxy.anthropic.com
claude.ai
a.claude.ai
a-cdn.claude.ai
assets.claude.ai
downloads.claude.ai
*.livepreview.claude.ai
claude.com
platform.claude.com
*.livepreview.claude.app
*.claudeusercontent.com
*.claudemcpcontent.com

```

如果您的組織已[啟用 IP 允許清單](https://support.claude.com/en/articles/13200993-restrict-access-to-claude-with-ip-allowlisting)用於 Claude，請透過與 `claude.ai` 和 `api.anthropic.com` 相同的代理出口路由 `bridge.claudeusercontent.com`。如果您無法以這種方式路由它，請將您的代理用於該主機的出口位址新增到您組織的 IP 允許清單，但僅當該位址專用於您的組織時：共用代理出口範圍也允許代理廠商的其他客戶。 Anthropic 使用它們到達的位址檢查與該主機的連線是否符合您組織的 IP 允許清單。如果您的代理透過不在該允許清單上的位址為其傳送流量，Chrome 中的 Claude 和透過橋接連線的其他功能會停止運作，而應用程式的其餘部分會繼續運作。 從 [Google Fonts](https://code.claude.com/docs/zh-TW/artifacts#improve-the-visual-design) 載入字體的[成品](https://code.claude.com/docs/zh-TW/artifacts)也會要求 `fonts.googleapis.com` 和 `fonts.gstatic.com`。兩個主機都是選用的。如果您阻止它們，成品會以備用字體呈現。使用快速拒絕而不是無聲丟棄來阻止，以便字體要求立即失敗，而不是延遲頁面的首次呈現。 成品也可以從 `cdnjs.cloudflare.com`、`cdn.jsdelivr.net`、`cdn.tailwindcss.com` 和 `code.jquery.com` 載入 JavaScript 程式庫（例如 React 或圖表套件），而不是從任何其他外部主機。如果您阻止這些主機，成品中依賴程式庫的部分無法運作，與阻止的字體不同，阻止的程式庫沒有備用方案。也在這裡使用快速拒絕，以便阻止的程式庫要求立即失敗，而不是掛起直到逾時。

### 驗證和 SSO

企業組織可以要求所有使用者進行 SSO。有關計畫級別的詳細資訊，請參閱[驗證](https://code.claude.com/docs/zh-TW/authentication)，以及有關 SAML 配置，請參閱[設定 SSO](https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso)；OIDC 設定涵蓋在 [Claude Enterprise Administrator Guide](https://claude.com/resources/tutorials/claude-enterprise-administrator-guide) 中。

### 資料處理

Claude Code 在本機會話中本機處理您的程式碼，或在雲端會話中在 Anthropic 管理的基礎設施上處理，除非您的組織將它們路由到[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)。雲端會話（包括在自託管環境中）將對話和程式碼上下文傳送到 Anthropic 的 API 進行處理；本機和 SSH 會話將它們傳送到您的部署配置的任何[模型提供者](https://code.claude.com/docs/zh-TW/desktop#feature-comparison)，預設為 Anthropic 的 API。有關資料保留、隱私和合規性的詳細資訊，請參閱[資料處理](https://code.claude.com/docs/zh-TW/data-usage)。

### 部署

Desktop 可以透過企業部署工具分發：

- **macOS** ：透過 MDM（例如 Jamf 或 Kandji）使用 `.dmg` 安裝程式分發
- **Windows** ：透過 MSIX 套件部署。有關企業部署選項（包括無聲安裝），請參閱[為 Windows 部署 Claude Desktop](https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows)

有關防火牆中要允許清單的網域，請參閱上面的[網路存取需求](https://code.claude.com/docs/zh-TW/desktop#network-access-requirements)。有關代理設定、自訂憑證授權單位和 LLM 閘道，請參閱[網路配置](https://code.claude.com/docs/zh-TW/network-config)。 有關完整的企業配置參考，請參閱[企業配置指南](https://support.claude.com/en/articles/12622667-enterprise-configuration)。

## 來自 CLI？

如果您已經使用 Claude Code CLI，Desktop 執行相同的基礎引擎，具有圖形介面。您可以在同一機器上同時執行兩者，甚至在同一專案上執行。每個都維護單獨的會話清單，您可以將 CLI 會話帶入 Desktop。它們透過 CLAUDE.md 檔案共用設定和專案記憶。 若要將 CLI 會話移至 Desktop，請在終端機中執行 `/desktop`。Claude 儲存您的會話並在桌面應用程式中開啟它，然後退出 CLI。此命令在 macOS 和 x64 Windows 上可用，當您使用 Claude 訂閱登入時。它不適用於 API 金鑰驗證或 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry。 若要從 Desktop 內部取得 CLI 會話，請在提示框中輸入 `/resume`。Desktop 列出您從 CLI 啟動的會話，您可以按標題、資料夾或分支搜尋它們，並預覽每個會話停止的位置。選擇一個會話，它會在應用程式中繼續進行，具有完整的對話和內容。 何時使用 Desktop 與 CLI：當您想要在一個視窗中管理並行會話、並排排列窗格或視覺化檢查變更時，使用 Desktop。當您需要指令碼、自動化或偏好終端機工作流程時，使用 CLI。

### CLI 標誌等效項

此表顯示常見 CLI 標誌的桌面應用程式等效項。未列出的標誌沒有桌面等效項，因為它們是為指令碼或自動化設計的。

| CLI                                   | Desktop 等效項                                                                                                                            |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `--model sonnet`                      | 傳送按鈕旁的模型下拉式選單                                                                                                                |
| `--resume`, `--continue`              | 點擊側邊欄中的會話，或在提示框中輸入 `/resume` 以取得您從 CLI 啟動的會話                                                                  |
| `--permission-mode`                   | 傳送按鈕旁的模式選擇器                                                                                                                    |
| `--dangerously-skip-permissions`      | 略過權限模式。在 Pro 和 Max 方案上，在「設定」→「Claude Code」→「允許略過權限模式」中啟用它；在 Team 和 Enterprise 方案上，組織政策控制它 |
| `--add-dir`                           | 在雲端會話中使用 **+** 按鈕新增多個儲存庫                                                                                                 |
| `--allowedTools`, `--disallowedTools` | 沒有各別會話等效項。[設定檔案](https://code.claude.com/docs/zh-TW/settings)中的權限規則仍然適用。                                         |
| `--verbose`                           | [Verbose 檢視模式](https://code.claude.com/docs/zh-TW/desktop#switch-view-modes)在 Transcript 檢視下拉式選單中                            |
| `--print`, `--output-format`          | 不可用。Desktop 僅限互動。                                                                                                                |
| `ANTHROPIC_MODEL` 環境變數            | 傳送按鈕旁的模型下拉式選單                                                                                                                |
| `MAX_THINKING_TOKENS` 環境變數        | 在本機環境編輯器中設定。請參閱[環境配置](https://code.claude.com/docs/zh-TW/desktop#environment-configuration)。                          |

### 共用設定

Desktop 和 CLI 讀取相同的設定檔案，因此您的設定會轉移：

- **[CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)** 和 `CLAUDE.local.md` 檔案在您的專案中由兩者使用
- **[MCP servers](https://code.claude.com/docs/zh-TW/mcp)** 在 `~/.claude.json` 或 `.mcp.json` 中設定的在兩者中都有效
- **[Hooks](https://code.claude.com/docs/zh-TW/hooks)** 和 **[skills](https://code.claude.com/docs/zh-TW/skills)** 在設定中定義的適用於兩者
- **[Settings](https://code.claude.com/docs/zh-TW/settings)** 在 `~/.claude.json` 和 `~/.claude/settings.json` 中是共用的。`settings.json` 中的權限規則、允許的工具和其他設定適用於 Desktop 會話。
- **Models** ：相同的[模型](https://code.claude.com/docs/zh-TW/model-config#available-models)在兩者中都可用。在 Desktop 中，從傳送按鈕旁的下拉式選單中選擇模型。您可以在會話期間從相同的下拉式選單變更模型。

#### Claude Desktop 聊天應用程式中的 MCP servers

Desktop 應用程式從 `claude_desktop_config.json` 將 MCP servers 載入到本機 Code 標籤會話中，以及來自 `~/.claude.json` 和 `.mcp.json` 的伺服器。在 `claude_desktop_config.json` 中定義的伺服器在 Desktop 聊天表面和本機 Code 標籤會話中都可用。 如果您在 `claude_desktop_config.json` 和 `~/.claude.json` 或 `.mcp.json` 中定義相同的伺服器名稱，本機會話中的 Code 標籤連接一次並使用 `claude_desktop_config.json` 定義。 應用程式也會將 `~/.claude.json` 中的 stdio 伺服器重新傳遞到本機會話中的嵌入式 CLI。當 `~/.claude.json`（使用者範圍）和 `.mcp.json` 的頂層定義相同的 stdio 伺服器名稱時，Code 標籤使用 `~/.claude.json` 定義，偏離 CLI [範圍階層](https://code.claude.com/docs/zh-TW/mcp#scope-hierarchy-and-precedence)。 獨立 CLI 不讀取 `claude_desktop_config.json`。在 macOS 和 WSL 上，執行 `claude mcp add-from-claude-desktop` 將這些伺服器複製到 `~/.claude.json`。請參閱[從 Claude Desktop 匯入 MCP servers](https://code.claude.com/docs/zh-TW/mcp#import-mcp-servers-from-claude-desktop)以了解匯入流程和範圍選項。

### 功能比較

此表比較 CLI 和 Desktop 之間的核心功能。有關 CLI 標誌的完整清單，請參閱 [CLI 參考](https://code.claude.com/docs/zh-TW/cli-reference)。

| 功能                                                                        | CLI                                                                                                                     | Desktop                                                                                                                                                                                                                                                                                                                                                 |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 權限模式                                                                    | 所有模式，包括 `dontAsk`                                                                                                | Manual、Accept edits、Plan 和 Auto。Bypass permissions 在模式選擇器中出現，一旦啟用：在 Pro 和 Max 方案上透過「設定」切換，或在 Team 和 Enterprise 方案上透過組織政策                                                                                                                                                                                   |
| [第三方提供者](https://code.claude.com/docs/zh-TW/third-party-integrations) | Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry                                                       | Anthropic 的 API 預設。若要進行閘道路由，請參閱[將桌面應用程式連接到閘道](https://code.claude.com/docs/zh-TW/llm-gateway-connect#desktop-app)。若要在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或自託管 LLM 閘道上執行 Code 標籤，請參閱 [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)。 |
| [MCP servers](https://code.claude.com/docs/zh-TW/mcp)                       | 在設定檔案中設定                                                                                                        | 本機和 SSH 會話的連接器 UI，或設定檔案                                                                                                                                                                                                                                                                                                                  |
| [Plugins](https://code.claude.com/docs/zh-TW/plugins)                       | `/plugin` 命令                                                                                                          | Plugin 管理器 UI                                                                                                                                                                                                                                                                                                                                        |
| @mention 檔案                                                               | 文字型                                                                                                                  | 具有自動完成；本機和 SSH 會話僅                                                                                                                                                                                                                                                                                                                         |
| 檔案附件                                                                    | 不可用                                                                                                                  | 影像、PDF                                                                                                                                                                                                                                                                                                                                               |
| 會話隔離                                                                    | [`--worktree`](https://code.claude.com/docs/zh-TW/cli-reference) 標誌                                                   | 啟動會話時的 **worktree** 選項                                                                                                                                                                                                                                                                                                                          |
| 多個會話                                                                    | 單獨的終端機                                                                                                            | 側邊欄標籤                                                                                                                                                                                                                                                                                                                                              |
| 定期任務                                                                    | Cron 工作、CI 管道                                                                                                      | [排程任務](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)                                                                                                                                                                                                                                                                                  |
| 電腦使用                                                                    | [透過 `/mcp` 在 macOS 上啟用](https://code.claude.com/docs/zh-TW/computer-use)                                          | [應用程式和螢幕控制](https://code.claude.com/docs/zh-TW/desktop#let-claude-use-your-computer)在 macOS 和 Windows 上                                                                                                                                                                                                                                     |
| iOS 模擬器                                                                  | 透過[電腦使用](https://code.claude.com/docs/zh-TW/computer-use#test-a-simulator-flow)驅動模擬器                         | [iOS Simulator 窗格](https://code.claude.com/docs/zh-TW/desktop-ios-simulator)自動開啟                                                                                                                                                                                                                                                                  |
| Dispatch 整合                                                               | 不可用                                                                                                                  | [Dispatch 會話](https://code.claude.com/docs/zh-TW/desktop#sessions-from-dispatch)在側邊欄中                                                                                                                                                                                                                                                            |
| 指令碼和自動化                                                              | [`--print`](https://code.claude.com/docs/zh-TW/cli-reference)、[Agent SDK](https://code.claude.com/docs/zh-TW/headless) | 不可用                                                                                                                                                                                                                                                                                                                                                  |

### Desktop 中不可用的內容

以下功能在 Desktop 中不可用，除非另有說明：

- **第三方提供者** ：Desktop 預設連接到 Anthropic 的 API。若要透過閘道路由 Desktop，或在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或自託管 LLM 閘道上執行 Code 標籤，請遵循[第三方提供者列](https://code.claude.com/docs/zh-TW/desktop#feature-comparison)中的連結。
- **Linux (beta)** ：Linux 桌面應用程式中尚未提供電腦使用。請參閱 [Claude Desktop on Linux](https://code.claude.com/docs/zh-TW/desktop-linux)。
- **內嵌程式碼建議** ：Desktop 不提供自動完成樣式的建議。它透過對話提示和明確的程式碼變更進行工作。
- **Agent teams** ：協調的團隊，其中 Claude 作為團隊主管從共用任務清單中指派任務給隊友，在 [CLI](https://code.claude.com/docs/zh-TW/agent-teams) 中可用，不在 Desktop 中。若要在一個會話內進行多代理工作，請使用 [dynamic workflows](https://code.claude.com/docs/zh-TW/workflows)，它們在 Desktop 中執行；Claude 也可以[直接傳遞訊息和管理您的其他會話](https://code.claude.com/docs/zh-TW/desktop#work-across-sessions)。
- **Terminal-dialog 命令** ：在終端機中開啟互動式面板的內建命令，在 Code 標籤中的行為不同。直接編輯[設定檔案](https://code.claude.com/docs/zh-TW/settings)以管理權限規則和設定，或從獨立 CLI 執行命令。
  - 沒有引數形式的命令，例如 `/permissions`，回覆 `isn't available in this environment`。
  - `/config` 開啟「設定」→「Claude Code」。命令後的文字被忽略，因此 `/config theme=dark` 不會設定主題。

## 疑難排解

下面的部分涵蓋桌面應用程式特定的問題。對於出現在聊天中的執行時 API 錯誤，例如 `API Error: 500`、`529 Overloaded`、`429` 或 `Prompt is too long`，請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors)。這些錯誤及其修復在 CLI、Desktop 和網路中是相同的。

### 檢查您的版本

若要查看您執行的桌面應用程式版本：

- **macOS** ：點擊選單列中的 **Claude** ，然後點擊 **About Claude**
- **Windows** ：點擊 **Help** ，然後點擊 **About**

點擊版本號以將其複製到您的剪貼簿。

### Code 標籤中的 403 或驗證錯誤

如果在使用 Code 標籤時看到 `Error 403: Forbidden` 或其他驗證失敗：

1. 從應用程式選單登出並重新登入。這是最常見的修復。
1. 驗證您有有效的付費訂閱：Pro、Max、Team 或 Enterprise。
1. 如果 CLI 有效但 Desktop 無效，完全退出桌面應用程式（不只是關閉視窗），然後重新開啟並登入。
1. 檢查您的網際網路連線和代理設定。

### 啟動時螢幕空白或卡住

如果應用程式開啟但顯示空白或無反應的螢幕：

1. 重新啟動應用程式。
1. 檢查待處理的更新。在 macOS 和 Windows 上，應用程式在啟動時自動更新；在 Linux 上，透過 apt 更新，如 [Claude Desktop on Linux](https://code.claude.com/docs/zh-TW/desktop-linux) 中所述。
1. 在受管理的網路上，確認您的防火牆允許[網路存取要求](https://code.claude.com/docs/zh-TW/desktop#network-access-requirements)中的 CDN 主機。
1. 在 Windows 上，檢查「事件檢視器」中的 **Windows 日誌 → 應用程式** 下的當機日誌。

### 「無法載入會話」

如果您看到 `Failed to load session`，選定的資料夾可能不再存在、Git 儲存庫可能需要未安裝的 Git LFS，或檔案權限可能阻止存取。嘗試選擇不同的資料夾或重新啟動應用程式。

### 會話找不到已安裝的工具

如果 Claude 找不到 `npm`、`node` 或其他 CLI 命令等工具，請驗證工具在您的常規終端機中有效、檢查您的 shell 設定檔是否正確設定 PATH，並重新啟動桌面應用程式以重新載入環境變數。

### Git 和 Git LFS 錯誤

在其自己的 worktree 中執行的會話需要 Git。如果您看到「Git is required」，請安裝 [Git](https://git-scm.com/downloads)，或在 Windows 上安裝 [Git for Windows](https://git-scm.com/downloads/win)，然後重新嘗試。在 Windows 上，1.49585.0 之前的 Claude Desktop 版本在啟動任何本機會話之前要求 Git；如果您看到該提示且未使用 worktrees，請更新應用程式。 如果您看到「Git LFS is required by this repository but is not installed」，請從 [git-lfs.com](https://git-lfs.com/) 安裝 Git LFS，執行 `git lfs install`，然後重新啟動應用程式。

### Windows 上的 MCP servers 無法運作

如果 MCP server 切換沒有回應或伺服器在 Windows 上無法連接，請檢查伺服器是否在您的設定中正確配置、重新啟動應用程式、驗證伺服器程序在工作管理員中執行，並檢查伺服器日誌以查看連線錯誤。

### 應用程式無法退出

- **macOS** ：按 Cmd+Q。如果應用程式沒有回應，使用 Cmd+Option+Esc 強制退出，選擇 Claude，然後點擊「強制退出」。
- **Windows** ：使用 Ctrl+Shift+Esc 的工作管理員來結束 Claude 程序。

### Windows 特定問題

- **安裝後 PATH 未更新** ：開啟新的終端機視窗。PATH 更新僅適用於新的終端機會話。
- **並行安裝錯誤** ：如果您看到有關另一個安裝進行中的錯誤，但實際上沒有，請嘗試以管理員身份執行安裝程式。

### 在 CLI 中開啟時「分支尚不存在」

遠端會話可以建立在您的本機機器上不存在的分支。點擊會話工具列中的分支名稱以複製它，然後在本機提取它：

```
git fetch origin <branch-name>
git checkout <branch-name>

```

### 仍然卡住？

- 在桌面應用程式中開啟「Help → Get Support」，或直接造訪 [Claude 支援中心](https://support.claude.com/)
- 對於在獨立 `claude` CLI 中也會重現的問題，請在 [GitHub Issues](https://github.com/anthropics/claude-code/issues) 上搜尋或提交錯誤

提交問題時，請包括您的桌面應用程式版本、您的作業系統、確切的錯誤訊息和相關日誌。在 macOS 上，檢查 Console.app。在 Windows 上，檢查「事件檢視器 → Windows 日誌 → 應用程式」。檢查日誌摘錄後再將其發佈到公開問題；它們可能包括來自您環境的檔案路徑和其他詳細資訊。 是否 助手
