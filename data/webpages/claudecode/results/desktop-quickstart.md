桌面應用程式為您提供具有圖形介面的 Claude Code，專為並行執行多個會話而設計：用於管理並行工作的側邊欄、具有整合終端機和檔案編輯器的拖放式佈局、視覺化差異檢查、即時應用程式預覽、GitHub PR 監控與自動合併，以及排程任務。無需終端機。

## [下載 macOS 版本 適用於 Intel 和 Apple Silicon 的通用版本 ](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs)

## [下載 Windows 版本 適用於 x64 處理器 ](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)

## [取得 Claude for Linux (測試版) 適用於 Ubuntu 和 Debian 的 apt 或 .deb ](https://code.claude.com/docs/zh-TW/desktop-linux)

若要使用 Windows ARM64，請下載 [ARM64 安裝程式](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)。在 Linux 上，使用 apt 安裝；請參閱 [Claude Desktop on Linux](https://code.claude.com/docs/zh-TW/desktop-linux)。 Claude Code 需要 [Pro、Max、Team 或 Enterprise 訂閱](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=desktop_quickstart_pricing)。 本頁面將引導您安裝應用程式並開始您的第一個會話。如果您已經設定完成，請參閱 [使用 Claude Code Desktop](https://code.claude.com/docs/zh-TW/desktop) 以取得完整參考。 桌面應用程式有三個標籤：

- **Chat** ：無檔案存取的一般對話，類似於 claude.ai。
- **Cowork** ：一個自主背景代理，在沙箱虛擬機中處理任務，具有自己的環境，可以獨立執行，同時您進行其他工作。裝置上的 Cowork 會話在您的電腦上執行 VM；遠端 Cowork 會話改為在 Anthropic 管理的 VM 上執行。
- **Code** ：具有直接存取本機檔案的互動式編碼助手。根據權限模式，您可以在 Claude 提出每項變更時批准，或在 Claude 進行變更後檢查變更。

Chat 和 Cowork 涵蓋在 [Claude 說明中心](https://support.claude.com/)；安裝和部署桌面應用程式涵蓋在 [Claude Desktop 支援文章](https://support.claude.com/en/collections/16163169-claude-desktop)。本頁面重點關注 **Code** 標籤。

## 安裝

1 安裝並登入 在 macOS 和 Windows 上，從上方連結下載安裝程式並執行它。在 Linux 上，請按照 [Claude Desktop on Linux](https://code.claude.com/docs/zh-TW/desktop-linux) 中的安裝步驟進行。從 macOS 上的應用程式資料夾、Windows 上的開始功能表或 Linux 上的應用程式啟動器啟動 Claude，然後使用您的 Anthropic 帳戶登入。 2 開啟 Code 標籤 點擊頂部中央的 **Code** 標籤。如果點擊 Code 提示您升級，您需要先 [訂閱付費方案](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=desktop_quickstart_upgrade)。如果它提示您線上登入，請完成登入並重新啟動應用程式。如果您看到 403 錯誤，請參閱 [驗證疑難排解](https://code.claude.com/docs/zh-TW/desktop#403-or-authentication-errors-in-the-code-tab)。 桌面應用程式包含 Claude Code。您無需單獨安裝 Node.js 或 CLI。若要從終端機使用 `claude`，請單獨安裝 CLI。請參閱 [開始使用 CLI](https://code.claude.com/docs/zh-TW/quickstart)。

## 開始您的第一個工作階段

開啟 Code 標籤後，選擇一個專案並告訴 Claude 要做什麼。 1 選擇環境和資料夾 選擇 **Local** 以在您的機器上執行 Claude，直接使用您的檔案。點擊 **Select folder** 並選擇您的專案目錄。 從一個您熟悉的小型專案開始。這是最快看到 Claude Code 能做什麼的方式。 您也可以選擇：

- **Cloud** ：在雲端執行工作階段，即使您關閉應用程式也會繼續進行。請參閱 [Use Claude Code in the cloud](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 以了解雲端工作階段的運作方式。
- **SSH** ：透過 SSH 連接到遠端機器，例如您自己的伺服器、雲端虛擬機或開發容器。Desktop 在您第一次連接時會自動在遠端機器上安裝 Claude Code。
- **WSL** （Windows）：在 [WSL 2 distribution](https://code.claude.com/docs/zh-TW/desktop-wsl) 內執行工作階段；Claude Code、工具和 git 在 Linux 端執行，使用原生路徑。

2 選擇模型 從傳送按鈕旁的下拉式選單中選擇模型。請參閱 [models](https://code.claude.com/docs/zh-TW/model-config#available-models) 以比較可用的模型。您稍後可以從相同的下拉式選單變更模型。 3 告訴 Claude 要做什麼 輸入您想要 Claude 做的事：

- `Find a TODO comment and fix it`
- `Add tests for the main function`
- `Create a CLAUDE.md with instructions for this codebase`

[session](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions) 是與 Claude 關於您的程式碼的對話。每個工作階段追蹤其自己的內容和變更。 4 檢視並接受變更 接下來發生的情況取決於傳送按鈕旁選擇器中顯示的 [permission mode](https://code.claude.com/docs/zh-TW/desktop#choose-a-permission-mode)：

- **Auto or Accept edits** ：Claude 套用其檔案變更，並出現指示器（例如 `+12 -1`），以便您可以在 diff 檢視中檢視它們
- **Manual** ：Claude 提議每項變更並等待您的批准後才套用。您的檔案在您接受之前不會被修改，如果您拒絕變更，Claude 會詢問您想如何改為進行

在 Manual 模式中，您會看到：

1. [diff view](https://code.claude.com/docs/zh-TW/desktop#review-changes-with-diff-view) 顯示每個檔案中將確切變更的內容
1. Accept/Reject 按鈕以批准或拒絕每項變更
1. Claude 處理您的請求時的即時更新

## 接下來呢？

您已經完成了第一次編輯。如需了解 Desktop 的完整功能參考，請參閱[使用 Claude Code Desktop](https://code.claude.com/docs/zh-TW/desktop)。以下是一些可以嘗試的事項。 **中斷並調整方向。** 您可以隨時重新導向 Claude。點擊停止按鈕立即中斷，或輸入更正並按 **Enter** 鍵發送，無需停止執行中的操作。無論哪種方式，您都不必等待它完成或重新開始。 **為 Claude 提供更多背景資訊。** 在提示框中輸入 `@filename` 以將特定檔案引入對話，使用附件按鈕附加影像和 PDF，或直接將檔案拖放到提示框中。Claude 擁有的背景資訊越多，結果就越好。請參閱[新增檔案和背景資訊至提示](https://code.claude.com/docs/zh-TW/desktop#add-files-and-context-to-prompts)。 **使用 skills 執行可重複的工作。** 輸入 `/` 或點擊 **+** → **Slash commands** 以瀏覽[內建命令](https://code.claude.com/docs/zh-TW/commands)、[自訂 skills](https://code.claude.com/docs/zh-TW/skills) 和外掛 skills。Skills 是可重複使用的提示，您可以在需要時隨時叫用，例如程式碼審查檢查清單或部署步驟。 **在提交前檢查變更。** Claude 編輯檔案後，會出現 `+12 -1` 指示器。點擊它以開啟[差異檢視](https://code.claude.com/docs/zh-TW/desktop#review-changes-with-diff-view)，逐個檔案檢查修改，並在特定行上留下評論。Claude 會讀取您的評論並進行修訂。點擊**檢查程式碼** 讓 Claude 自行評估差異並留下內嵌建議。 **調整您擁有的控制程度。** 您的[權限模式](https://code.claude.com/docs/zh-TW/desktop#choose-a-permission-mode)設定了 Claude 在不請求批准的情況下可以執行的操作：

- **自動** ：分類器在背景中檢查操作，並阻止有風險的操作，而不是詢問您。
- **手動** ：Claude 在編輯檔案或執行命令前會詢問。
- **接受編輯** ：Claude 自動接受檔案編輯以加快迭代速度。
- **Plan** ：Claude 提出方法而不編輯任何檔案，這在大型重構前很有用。

**新增外掛以獲得更多功能。** 點擊提示框旁的 **+** 按鈕並選擇 **Plugins** 以瀏覽並安裝[外掛](https://code.claude.com/docs/zh-TW/desktop#install-plugins)，這些外掛可新增 skills、agents、MCP 伺服器等。 **整理您的工作區。** 將聊天、差異、終端機、檔案和瀏覽器窗格拖放到您想要的任何版面配置中。使用 **Ctrl+\`** 開啟終端機以在您的工作階段旁執行命令，或點擊檔案路徑以在檔案窗格中開啟它。請參閱[整理您的工作區](https://code.claude.com/docs/zh-TW/desktop#arrange-your-workspace)。 **預覽您的應用程式。** 當您在 desktop 中執行開發伺服器時，您的應用程式會在瀏覽器窗格中開啟，該窗格也可以[開啟外部網站](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)。Claude 可以檢視執行中的應用程式、測試端點、檢查日誌，並根據所看到的內容進行迭代。請參閱[預覽您的應用程式](https://code.claude.com/docs/zh-TW/desktop#preview-your-app)。 **追蹤您的提取請求。** 開啟 PR 後，Claude Code 會監控 CI 檢查結果，並可在所有檢查通過後自動修復失敗或合併 PR。請參閱[監控提取請求狀態](https://code.claude.com/docs/zh-TW/desktop#monitor-pull-request-status)。 **將 Claude 排程執行。** 設定[排程工作](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)以定期自動執行 Claude：每天早上進行程式碼審查、每週進行相依性稽核，或從您連接的工具提取資訊的簡報。 **準備好時進行擴展。** 從側邊欄開啟[平行工作階段](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)以同時處理多個工作，可選擇每個工作都在自己的 Git worktree 中，並開啟[工作窗格](https://code.claude.com/docs/zh-TW/desktop#watch-background-tasks)以監控工作階段正在執行的子代理和背景命令。開啟[側邊聊天](https://code.claude.com/docs/zh-TW/desktop#ask-a-side-question-without-derailing-the-session)以提出問題而不會偏離主線。將[長期執行的工作發送到雲端](https://code.claude.com/docs/zh-TW/desktop#run-long-running-tasks-in-the-cloud)以便即使您關閉應用程式也能繼續執行，或[在網路或 IDE 中繼續工作階段](https://code.claude.com/docs/zh-TW/desktop#continue-in-another-surface)（如果工作耗時超過預期）。[連接外部工具](https://code.claude.com/docs/zh-TW/desktop#extend-claude-code)（例如 GitHub、Slack 和 Linear）以整合您的工作流程。

## 接下來

- [使用 Claude Code Desktop](https://code.claude.com/docs/zh-TW/desktop)：權限模式、平行工作階段、差異檢視、連接器和企業設定
- [從 CLI 遷移過來？](https://code.claude.com/docs/zh-TW/desktop#coming-from-the-cli)：在同一個專案上執行 Desktop 和 CLI，並比較功能、旗標等效項，以及 Desktop 中不可用的功能
- [疑難排解](https://code.claude.com/docs/zh-TW/desktop#troubleshooting)：常見錯誤和設定問題的解決方案
- [最佳實踐](https://code.claude.com/docs/zh-TW/best-practices)：撰寫有效提示詞和充分利用 Claude Code 的提示
- [常見工作流程](https://code.claude.com/docs/zh-TW/common-workflows)：除錯、重構、測試等的教學

是否 助手
