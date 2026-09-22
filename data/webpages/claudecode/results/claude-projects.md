Projects 在 Pro 和 Max 方案上處於公開測試版，並逐步推出，首先針對已使用 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 且在 claude.ai 聊天或 Cowork 中沒有現有專案的帳戶。目前在 Team 或 Enterprise 方案上還不可用。如果 **Projects** 沒有出現在 [claude.ai/code](https://claude.ai/code) 的側邊欄中或 [桌面應用程式](https://code.claude.com/docs/zh-TW/desktop) 的 Code 標籤中，表示推出尚未到達您的帳戶，您可以 [加入等候清單](https://claude.com/form/projects)。[平行執行代理](https://code.claude.com/docs/zh-TW/agents) 列出了您在此期間可以使用的內容。 專案是一個進行中的對話，Claude 在其中為您協調一系列相關工作。您告訴它需要做什麼，它會為每個任務啟動一個執行緒。每個執行緒都是一個 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：Claude Code 在雲端而不是在您的機器上執行。執行緒平行執行，並在您關閉筆記型電腦後繼續進行，您可以從您的手機檢查它們並引導它們。 沒有專案的情況下，執行多個工作階段意味著自己進行協調：您決定每個工作階段要處理什麼，在每個工作階段的開始重複相同的背景資訊，並檢查哪個已完成或需要答案。使用專案，您可以改為：

- **將工作發送到一個地方** ：每當出現時，將錯誤報告、堆疊追蹤或任務清單貼到對話中。Claude 為每個工作片段啟動一個執行緒，或將其傳遞給已在該區域工作的執行緒，並就地回答快速問題。
- **設定一次背景資訊** ：每個新執行緒都以專案的儲存庫、指示和記憶開始，因此您陳述一次的規則（例如要針對的分支）會到達所有執行緒。
- **離開並返回已完成的工作** ：當您一小時後或第二天早上回來時，**Overview** 窗格會顯示哪些執行緒已完成、哪些提取請求已準備好供審查，以及哪個執行緒正在等待您的答案。

如果您已經知道希望專案執行的工作，請直接前往 [建立專案](https://code.claude.com/docs/zh-TW/claude-projects#create-a-project)。

## 何時使用 project

當工作有一個超越單個工作階段的目標並持續產生任務時，創建 project 是值得的。這些類型的工作非常適合 project：

- **跨多個儲存庫的一個目標** ：“將每個服務升級到新的 lint 配置。” Claude 可以為每個儲存庫執行一個執行緒，每個都有自己的提取請求，[**Overview** 窗格](https://code.claude.com/docs/zh-TW/claude-projects#see-what-needs-you-in-overview) 會顯示哪些已準備好供審查。
- **您持續提供的區域** ：一個服務的錯誤、堆疊追蹤和審查請求，在到達您時貼到對話中。您告訴 Claude 在一個修復後要記住的陷阱在 [project 記憶](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context) 中供下一個使用。
- **比工作階段更大的構建或遷移** ：“構建 `docs/spec.md` 描述的內容”或”將應用程式從已棄用的 ORM 移出。” 工作分成執行緒，每個執行緒處理一部分，您要求 Claude 早期記住的決定會到達後來的執行緒，您在構建期間發現的規格變更和錯誤進入相同的對話。
- **不是程式碼的工作** ：一個合約資料夾或支援票證匯出，您不斷回來提出新問題，例如”在這些票證中找到十個最常見的整合錯誤。” 上傳文件而不是添加儲存庫，執行緒會在 project 的 [**Library** 標籤](https://code.claude.com/docs/zh-TW/claude-projects#see-what-needs-you-in-overview) 上將每個寫作作為檔案提供。

在任何一個中，您都可以發送一批任務，告訴 Claude 在不要求您確認的情況下開始，離開，並在您回來時在 [**等待您**](https://code.claude.com/docs/zh-TW/claude-projects#see-what-needs-you-in-overview) 下找到需要您的執行緒，或要求 Claude 將部分工作放在時間表上作為 [routine](https://code.claude.com/docs/zh-TW/routines)。如果這是您的情況，[建立 project](https://code.claude.com/docs/zh-TW/claude-projects#create-a-project)。

### 何時其他方式更合適

執行緒在 GitHub 儲存庫以及您上傳到 project 的檔案、資料夾和 Google Drive 資料夾上工作，而不是在僅存在於您機器上的檔案或工具上。在這些情況下，其他方式更合適：

- **一個適合工作階段的任務** ：“修復不穩定的登入測試。” 自己啟動 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)。
- **需要只有您的機器才能到達的工具或服務的工作** ：本地資料庫、設備模擬器、您 VPN 後面的 API。使用本地工作階段，或 [代理檢視](https://code.claude.com/docs/zh-TW/agent-view) 同時執行多個。如果工作只需要本地檔案，請改為將它們上傳到 project。
- **一個按時間表重複的任務，周圍沒有對話** ：“每週一發佈依賴報告。” 自己建立 [routine](https://code.claude.com/docs/zh-TW/routines)。
- **多個人在 Slack 頻道中給 Claude 工作並一起引導它** ：請參閱 [Claude Tag](https://claude.com/docs/claude-tag/overview)。

Project 使用與您其他 Claude Code 工作階段相同的方案限制，並更快地使用它們。[使用和成本](https://code.claude.com/docs/zh-TW/claude-projects#usage-and-cost) 涵蓋了什麼使用您的方案以及如何降低它。

## Project 如何組織

Project 是一個協調對話加上它啟動的執行緒來完成工作。這些是它的部分：

- **project 對話** ：一個長期執行的工作階段，Claude 充當協調者。它接收您發送的內容，決定什麼成為執行緒，並跟蹤它啟動的每個執行緒。它看到執行緒報告回來的內容，而不是它們採取的每一步。
- **執行緒** ：工作者。每個都是一個單獨的 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，有自己的上下文視窗，在自己的分支上完成一項工作，在工作需要時打開提取請求，並在完成時報告回對話。
- **每個執行緒開始時的內容** ：
  - project 的儲存庫和檔案，加上其 [指示和記憶](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context)
  - `CLAUDE.md`、skills 和 [project 每個儲存庫](https://code.claude.com/docs/zh-TW/claude-projects#what-threads-pick-up-from-your-repositories) 中的 plugins，以及在有一個儲存庫的 project 中，該儲存庫的權限規則和 hooks
  - 您 claude.ai 帳戶上的 [connectors](https://code.claude.com/docs/zh-TW/claude-projects#get-skills-plugins-connectors-and-tools-into-threads)
  - 一個 [雲端環境](https://code.claude.com/docs/zh-TW/claude-projects#choose-an-environment-for-threads)，設定其網路存取、環境變數、API 認證和已安裝的工具
- **Overview 窗格** ：您在其中 [一次看到所有執行緒](https://code.claude.com/docs/zh-TW/claude-projects#see-what-needs-you-in-overview) 以及其中哪些需要您。其他標籤是 **Library** 用於您添加的檔案和執行緒產生的檔案，**Pull requests** 用於執行緒開啟的提取請求，**Routines** 用於 project 中的排程工作。

執行緒不會從您自己機器上的 Claude Code 設定中選擇任何內容。[將 skills、plugins、connectors 和工具放入執行緒](https://code.claude.com/docs/zh-TW/claude-projects#get-skills-plugins-connectors-and-tools-into-threads) 涵蓋了如何給予它們否則會缺少的內容。 以下是這些部分如何連接的方式，從您通過對話到執行工作的執行緒，**Overview** 跟蹤其狀態：

![Project 的圖表。您在 project 對話中寫入，Claude 回答或啟動執行緒。每個執行緒是在自己的分支和提取請求上工作的雲端工作階段。Overview 窗格按狀態列出執行緒，例如準備好供審查、等待您和工作中。](https://mintcdn.com/claude-code/e8CLbxM17eD7cAiv/images/claude-projects-overview.svg?fit=max&auto=format&n=e8CLbxM17eD7cAiv&q=85&s=dbf446f69f0bbdb9961d21af207cb93b)

![Project 的圖表。您在 project 對話中寫入，Claude 回答或啟動執行緒。每個執行緒是在自己的分支和提取請求上工作的雲端工作階段。Overview 窗格按狀態列出執行緒，例如準備好供審查、等待您和工作中。](https://mintcdn.com/claude-code/e8CLbxM17eD7cAiv/images/claude-projects-overview-dark.svg?fit=max&auto=format&n=e8CLbxM17eD7cAiv&q=85&s=549a5ba9fea8433729babc37a1f6e9c8)
## 建立 project

您在 [claude.ai/code](https://claude.ai/code)、桌面應用程式的 Code 標籤中，或在 Claude 行動應用程式中建立和使用 projects，適用於 [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 和 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)。在瀏覽器和桌面應用程式中，有兩種方式開始 project：

- **從頭開始** ，當您知道想要 Claude 執行的工作流時：打開 **New project** 對話框並命名它。[從頭開始啟動新 project](https://code.claude.com/docs/zh-TW/claude-projects#start-a-new-project-from-scratch) 會逐步介紹該對話框。
- **從已在執行工作的雲端工作階段** ：從該工作階段的功能表中選擇 **Continue as a project** ，Claude 從工作階段正在執行的內容提議 project 的設定。請參閱 [從現有雲端工作階段開始](https://code.claude.com/docs/zh-TW/claude-projects#start-from-an-existing-cloud-session)。

無論哪種方式，[首先檢查先決條件](https://code.claude.com/docs/zh-TW/claude-projects#check-the-prerequisites)。

### 檢查先決條件

在建立 project 之前，檢查您的方案、GitHub 設定以及工作需要到達的內容：

- **方案** ：您在 Pro 或 Max 上，**Projects** 在您的側邊欄中顯示。
- **GitHub，如果 project 將在程式碼上工作** ：您的程式碼在 github.com 上而不是 GitHub Enterprise Server、GitLab 或 Bitbucket 上，您連接的 GitHub 帳戶對其有推送存取權，Claude GitHub App 已安裝在其上。如果您使用 [`/web-setup`](https://code.claude.com/docs/zh-TW/web-quickstart#connect-from-your-terminal) 連接了 GitHub，該令牌讓您的其他雲端工作階段到達儲存庫，但對於需要 Claude GitHub App 的 project 執行緒來說還不夠。[設定 GitHub 存取](https://code.claude.com/docs/zh-TW/claude-projects#set-up-github-access) 有步驟。
- **網路、認證和工具** ：這些來自 project 的 [雲端環境](https://code.claude.com/docs/zh-TW/claude-projects#choose-an-environment-for-threads)。預設環境已經到達 [常見套件登錄](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)，因此只有在工作需要其他網域、秘密或未預先安裝的工具時才檢查此項。如果工作需要 MCP 伺服器，檢查它是否在您的 [claude.ai connectors](https://claude.ai/customize/connectors) 中顯示為已連接。

### 從頭開始啟動新 project

從頭開始啟動 project 意味著打開 **New project** 對話框、命名工作流，以及可選地給予它一個目標和它工作的儲存庫和檔案。只有名稱是必需的，因此您可以先建立 project，然後在工作進行時填入其餘部分。 1 打開 Projects 在 [claude.ai/code](https://claude.ai/code) 或桌面應用程式的 Code 標籤中，在左側邊欄中選擇 **Projects** ，然後選擇 **New project** 。在瀏覽器中，您也可以直接前往 [claude.ai/code/projects/browse](https://claude.ai/code/projects/browse)。 2 填入 New project 對話框 將 project 的範圍限制在一個您將持續添加的工作流，例如保持一個 API 在其延遲目標下所需的一切。[何時使用 project](https://code.claude.com/docs/zh-TW/claude-projects#when-to-use-a-project) 有更多範例。然後填入對話框的欄位：

- **Name** ：project 在 **Projects** 清單中的顯示方式。
- **Goal** （可選）：您試圖完成的一行內容，例如「將 p95 API 延遲保持在 200 毫秒以下」。對話中的 Claude 朝著它工作。沒有目標，Claude 從您發送的任務工作，您可以稍後在 **Project settings > General** 中添加目標。
- **Context** （可選）：此 project 工作的 GitHub 儲存庫，加上執行緒應該讀取的任何檔案、資料夾或 Google Drive 資料夾。為每個點擊 **Add** 。添加大多數任務需要的儲存庫而不是工作可能接觸的每一個；[決定要添加哪些儲存庫](https://code.claude.com/docs/zh-TW/claude-projects#decide-which-repositories-to-add) 涵蓋了選擇，您可以稍後在 **Project settings > Environment** 中添加更多。

執行緒應該如何工作的常設規則進入 [project 指示](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context)，您在 project 存在後設定。 3 建立 project 點擊 **Create project** 。project 的對話打開，底部有一個訊息框，您可以在其中描述 Claude 的工作。在您的第一個 project 上，除非您先發送訊息，否則 Claude 在建立 project 後會自己進行一次轉換。該轉換使用您的方案。在其中，Claude 可能會：

- 啟動一個執行緒，探索儲存庫而不改變任何內容，並提議後續步驟，如果 project 有它可以讀取的儲存庫。
- 發佈從您最近的雲端工作階段中提取的 **Setup recommendations** ：要添加的儲存庫、要建立的 routines 和它可以啟動的執行緒。每個推薦的儲存庫和 routine 都預設開啟。關閉您不想要的，然後點擊 **Update setup** 添加其餘部分，或忽略建議並自己描述工作。

project 現在在側邊欄的 **Projects** 下列出，其對話已打開。[您的第一批](https://code.claude.com/docs/zh-TW/claude-projects#your-first-batch) 涵蓋了在您發送工作之前要設定的內容。

### 從現有雲端工作階段開始

如果您已經有一個雲端工作階段在執行屬於 project 的工作，請打開側邊欄中工作階段的功能表，然後選擇 **Continue as a project** 或 **Move to project** ：

- **Continue as a project** 建立一個以工作階段命名的新 project 並打開它。Claude 讀取工作階段並在對話中發佈 **Setup recommendations** 供您確認。原始工作階段保留在您的工作階段清單中，如果它在轉換中途，它會繼續執行，因此如果您不想兩者同時工作，請自己停止它。如果您改為使用可能出現在雲端工作階段訊息框上方的 **Set up project** 橫幅，結果是相同的，除了工作階段的執行轉換在 project 打開後停止。
- **Move to project** 將工作階段的工作帶入現有 project。它在該 project 的對話中發佈一條訊息，要求 Claude 讀取工作階段並從它停止的地方繼續，新工作在 project 自己的執行緒中繼續。原始工作階段保留在您的工作階段清單中，未改變。

### 設定 GitHub 存取

大多數 GitHub 設定每次發生一次，而不是每個 project。您連接一次 GitHub 帳戶到 Claude，Claude GitHub App 每個儲存庫安裝一次，或如果您給予它所有儲存庫，則為整個 GitHub 組織安裝一次。當您添加 Claude GitHub App 尚未涵蓋的儲存庫或在強制執行 SSO 的 GitHub 組織中的儲存庫時，您會回到這些步驟。 1 連接您的 GitHub 帳戶 如果您之前未使用過 claude.ai/code，您的第一次訪問會引導您連接 GitHub；請參閱 [連接 GitHub](https://code.claude.com/docs/zh-TW/web-quickstart#connect-github)。否則使用其中一個 [GitHub 驗證選項](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)。 2 在 project 的儲存庫上安裝 Claude GitHub App 安裝 [Claude GitHub App](https://github.com/apps/claude) 並授予它 project 將使用的儲存庫。在由 GitHub 組織擁有的儲存庫上，只有組織所有者才能完成安裝；如果您不是，GitHub 會向所有者發送安裝請求，project 在他們批准之前無法使用儲存庫。 3 為強制執行 SSO 的組織授權 SSO 如果 GitHub 組織強制執行 SAML SSO，重新連接 GitHub 並為該組織授權 Claude 應用程式。在您這樣做之前，該組織的私有儲存庫不會出現在 **New project** 對話框或 **Project settings > Environment** 中。 當這些步驟之一未完成時，**New project** 對話框和 project 頁面會命名缺失的步驟並連結到您完成它的地方。在那裡完成該步驟，然後如果對話框提供它，點擊 **Check again** 。如果儲存庫之後仍然缺失清單，請在 GitHub 上打開 Claude GitHub App 的安裝，在 [github.com/settings/installations](https://github.com/settings/installations) 用於個人帳戶，並確認儲存庫在 **Repository access** 下列出。對於執行緒或 project 在存取仍然錯誤時報告的錯誤訊息，請參閱 [儲存庫存取錯誤](https://code.claude.com/docs/zh-TW/claude-projects#repository-access-errors)。

## 在 project 中工作

通過 project 對話給 Claude 工作：一次一個任務或一次多個，加上更新和鬆散的想法。Claude 路由每條訊息，執行緒執行工作並報告回。

### 您的第一批

在您向新 project 發送一批工作之前，設定它，以便第一個執行緒以您想要的方式回來：

1. [寫 project 指示](https://code.claude.com/docs/zh-TW/claude-projects#write-project-instructions)：每個執行緒開始的簡報，例如要針對的分支、執行緒如何檢查其工作，以及什麼需要您的同意。
1. 發送一個真實工作的小片段，或啟動 Claude 建議的其中一個執行緒（如果它提供了任何），並在它完成時打開執行緒，以查看它如何報告回以及它在分支上做了什麼。如果它假設了錯誤的內容或無法到達它需要的內容，[執行緒猜測或停滯而不是詢問](https://code.claude.com/docs/zh-TW/claude-projects#threads-guessed-or-stalled-instead-of-asking) 涵蓋了在哪裡修復。
1. 檢查 **Project settings > General** 中的 **Thread model** 和 **Thread effort** 。新 project 在高努力下在 Opus 上執行每個執行緒，這最快地使用您的方案；[選擇模型並讓 Claude 管理上下文](https://code.claude.com/docs/zh-TW/claude-projects#choose-models-and-let-claude-manage-context) 涵蓋了替代方案。
1. 要求 Claude [在啟動執行緒之前提議執行緒並一次執行幾個](https://code.claude.com/docs/zh-TW/claude-projects#tune-how-claude-runs-a-project)，並在幾個執行緒以您想要的方式回來後放棄這些限制。

### 發送工作並讀取結果

Claude 決定您在對話中發送的每條訊息去向：

- 快速問題通常在對話中得到回答。
- 新工作進入新執行緒或已在該區域工作的執行緒，Claude 告訴您哪個。每個新執行緒在您的訊息下顯示為卡片：一個帶有執行緒標題和狀態的框，您點擊打開執行緒。
- 一條訊息中的多個不相關任務成為單獨的執行緒。

如果 Claude 路由的內容與您想要的不同，請說出來。[調整 Claude 執行 project 的方式](https://code.claude.com/docs/zh-TW/claude-projects#tune-how-claude-runs-a-project) 列出了您可以告訴它的內容，例如為後續工作重用現有執行緒或就地回答而不是啟動執行緒。 執行緒的完整結果保留在執行緒中，您打開對話中的卡片來讀取它們。執行緒產生的檔案也在 **Overview** 中的 **Library** 標籤上。 有時 Claude 在 **Suggested threads** 清單中提議執行緒而不是啟動它們。點擊建議上的箭頭啟動該執行緒。當列出多個時，清單下的按鈕啟動所有這些。

### 審查執行緒的提取請求

當執行緒更改程式碼時，除非您另外告訴它，否則它會執行以下操作：

- **Branch** ：在新分支上工作，從儲存庫的預設分支開始。
- **Pull request** ：當您要求時打開一個，並可以為錯誤修復或另一個具體變更自己打開一個。
- **打開後** ：使用 [auto-fix](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests) 打開監視提取請求，無論 auto-fix 是否對您的其他雲端工作階段打開。它在 CI 失敗時推送修復，解決審查評論，並在檢查通過且提取請求準備好供您審查時在執行緒中回覆。

當執行緒推送了分支或打開了提取請求時，其在對話中的卡片可以顯示下一步的按鈕：

- **Resolve conflicts** 、**Fix CI** 、**Address comments** 和 **Merge it** 將該指示作為來自您的訊息發送到執行緒，因此您可以自己提示執行緒而不是等待它對提取請求做出反應。
- **Review PR** 在 GitHub 上打開提取請求。
- **Create PR** 出現在閒置執行緒已推送分支但尚未打開提取請求時。點擊它會直接從該分支建立提取請求，而不是向執行緒發送打開提取請求的指示。

要更改執行緒何時打開提取請求，例如僅在您要求時，或它們從哪個分支開始，請在任務或 [project 指示](https://code.claude.com/docs/zh-TW/claude-projects#write-project-instructions) 中說出來。

### 在 Overview 中查看需要您的內容

**Overview** 窗格在對話旁邊跟蹤 project 的執行緒。它在您第一次打開新 project 時已經打開。project 標題中的 **Overview** 按鈕關閉並重新打開它，並在執行緒等待您時顯示一個點。 在桌面應用程式中，當 Claude 在對話中發佈、執行緒遇到錯誤或執行緒需要您的輸入時，您還會收到桌面通知，因此您不必保持 project 打開來找出。要在每次執行緒完成轉換時也收到一個，或為 project 關閉它們，請在 project 的側邊欄功能表中選擇 **Notifications** 。這些通知僅限桌面：在瀏覽器中，檢查 **Overview** 按鈕上的點。 窗格的 **Threads** 標籤按狀態對執行緒進行分組：

| 群組                                                                                                                                                                                                                       | 其中的內容                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ready for review**                                                                                                                                                                                                       | 提取請求已打開並等待審查的執行緒                                                                                                                     |
| **Waiting on you**                                                                                                                                                                                                         | 需要您回覆或批准的執行緒，或失敗的執行緒                                                                                                             |
| **Working**                                                                                                                                                                                                                | 仍在執行的執行緒                                                                                                                                     |
| **Landing**                                                                                                                                                                                                                | 提取請求已批准或排隊合併的執行緒                                                                                                                     |
| **Idle**                                                                                                                                                                                                                   | 已完成且不等待任何內容的執行緒                                                                                                                       |
| **Resolved**                                                                                                                                                                                                               | 標記為完成的執行緒：由您從執行緒的功能表中，由 Claude 在您採取最後一步後（例如合併其提取請求），或在一週無活動後自動。您可以從相同功能表重新打開一個 |
| 窗格的其他標籤是 **Library** 用於您添加的檔案和資料夾以及執行緒產生的檔案，**Pull requests** 一旦執行緒打開任何，以及 **Routines** 用於 [routines](https://code.claude.com/docs/zh-TW/routines) Claude 從此 project 設定。 |                                                                                                                                                      |

### 當您需要控制時打開執行緒

點擊對話中執行緒的卡片或 **Overview** 中的其行，在 Overview 窗格中打開其記錄。從那裡您可以：

- 逐步讀取 Claude 所做的內容。
- 通過在執行緒自己的訊息框中寫入來引導任務。那裡的訊息直接進入該執行緒，而 project 對話中的後續工作只有在 Claude 將後續工作與該執行緒匹配時才會到達它。
- 回答執行緒正在等待的權限提示。
- 使用 **Stop** 中斷執行緒，它在執行緒工作時替換發送按鈕，或按 Esc。

### 選擇模型並讓 Claude 管理上下文

在 **Project settings > General** 中設定模型和努力。新 project 在高 [effort](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level) 下為執行緒和低努力下為對話在任何地方執行 Opus：

- **Thread model** 和 **Thread effort** 適用於執行緒。要為一個任務使用不同的模型，在任務中要求它；對於已在執行的執行緒，使用該執行緒的模型選擇器。
- **Coordinator model** 和 **Coordinator effort** 適用於 project 對話中的 Claude。

您不在 project 中管理上下文視窗。執行緒自動壓縮，對話從最近的訊息、最近的執行緒和 project 記憶而不是其完整歷史工作，因此它只要 project 執行就繼續。將任何必須永遠不被丟棄的內容放在 [project 記憶](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context) 中。如果一個執行緒超出其上下文，它會顯示 [Claude 在此轉換上用完了上下文](https://code.claude.com/docs/zh-TW/claude-projects#context-limit)。

### 調整 Claude 執行 project 的方式

在對話中告訴 Claude 一次執行多少執行緒、何時發佈更新以及何時打開提取請求。如果 Claude 以您不想要的方式協調，請說出來。例如，您可以說：

- “提議執行緒並在啟動之前等待我的同意”或”立即啟動這些而不要求我確認”
- “一次最多執行兩個執行緒”或”為同一區域的後續工作重用現有執行緒”
- “發佈更短的更新”或”僅在某些完成或被阻止時發佈”
- “給我每個執行緒的狀態更新”
- “用較小的模型執行此任務”
- “在我看到計劃之前不要打開提取請求”
- “告訴我這些儲存庫中的問題，不要修復任何內容”，當您想在任何內容成為執行緒之前查看發現時
- “改為在這裡回答”，當 Claude 為您打算作為快速問題的內容啟動執行緒時

Claude 自動將這些偏好保存到 [project 記憶](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context)，並在後來的執行緒中遵循它們。它們是 Claude 遵守的指示，而不是強制執行的設定，因此您以這種方式給出的執行緒限制不是硬上限。當您想要它精確措辭並從一開始應用於每個執行緒時，將一個添加到 project 指示。

### 解除等待批准的執行緒

當執行緒的模型支援時，執行緒在 [auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 中執行，因此大多數工具呼叫執行而不詢問您。當執行緒需要您的批准時，提示在該執行緒內，執行緒等待直到您在那裡回答。在 project 對話中告訴 Claude 繼續不會到達它。 每個批准涵蓋該提示，或如果您選擇更廣泛的選項，則涵蓋該執行緒的其餘部分。要讓每個執行緒執行某些命令而不詢問，或阻止某些，請將 [permission rules](https://code.claude.com/docs/zh-TW/permissions) 添加到儲存庫的 `.claude/settings.json`。執行緒僅在有一個儲存庫的 project 中應用它們；請參閱 [執行緒從您的儲存庫中選擇什麼](https://code.claude.com/docs/zh-TW/claude-projects#what-threads-pick-up-from-your-repositories)。

## 為專案提供常設背景

專案記憶、專案指示，以及專案的儲存庫、檔案和環境會跨執行緒攜帶背景。您設定每一個一次，它就會套用到每個新執行緒。

| 背景                                                                                                                                                                                                                                                                                                                                                                                                               | 它攜帶什麼                                                                                                                                                                              | 您如何設定它                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 專案記憶                                                                                                                                                                                                                                                                                                                                                                                                           | Claude 保留的關於專案的筆記，例如需求、決策和陷阱，儲存為檔案。每個執行緒在啟動時讀取索引檔案 `MEMORY.md`，並在需要時開啟其他檔案                                                       | 在專案對話或任何執行緒中要求 Claude 記住一項需求、決策或陷阱，或忘記一項。在**專案設定 > 記憶**中讀取、編輯和刪除檔案                 |
| 專案指示                                                                                                                                                                                                                                                                                                                                                                                                           | 傳送到每個新執行緒和專案對話中的 Claude 的文字，最多 16,000 個字元。[寫入專案指示](https://code.claude.com/docs/zh-TW/claude-projects#write-project-instructions)涵蓋要在其中放入的內容 | **專案設定 > 記憶 > 專案指示**，或要求 Claude 變更指示                                                                                |
| 儲存庫、檔案和環境                                                                                                                                                                                                                                                                                                                                                                                                 | 每個執行緒複製的儲存庫、每個執行緒可以在 `/mnt/project-files` 下讀取的資料夾和檔案，以及執行緒執行所在的雲端環境                                                                        | 儲存庫和環境在**專案設定 > 環境**中，或在對話中要求 Claude 將儲存庫新增到專案。檔案和資料夾來自**概覽** 中**程式庫** 標籤上的**新增** |
| **專案設定 > 記憶**在**自動記憶** 下列出這些檔案，因為 Claude 在專案中工作時自己寫入它們。它們與 Claude Code 在您的機器上保留的[自動記憶](https://code.claude.com/docs/zh-TW/memory)分開，儘管兩者都使用 `MEMORY.md` 索引。專案記憶也與專案儲存庫中的 `CLAUDE.md` 檔案分開。每個執行緒在啟動時仍然從其複製讀取這些 `CLAUDE.md` 檔案，因此將關於儲存庫的指示放在其 `CLAUDE.md` 中，將關於專案的筆記放在專案記憶中。 |                                                                                                                                                                                         |                                                                                                                                       |

### 寫入專案指示

專案指示是每個新執行緒開始的簡報。按一下專案標題中的齒輪圖示以開啟**專案設定** ，然後前往**記憶 > 專案指示**。有用的簡報涵蓋：

- 專案的用途
- 工作發生的位置：哪些儲存庫、從哪個分支開始、如何命名提取請求
- 執行緒在完成工作前如何檢查自己的工作
- 當它需要的東西遺失時該怎麼辦
- 什麼需要您的事先同意

例如：

```
此專案將付款 API 的 p95 延遲保持在 200 毫秒以下：分析、查詢和快取修復，以及隨之而來的依賴項升級，在 payments-api 儲存庫中。

- 從 main 分支建立分支，每個執行緒開啟一個草稿提取請求。
- 在您完成工作前，執行 `make test` 和 `make lint`，並在最終訊息中貼上摘要行。
- 如果您無法到達所需的東西，例如儲存庫、祕密、API 或連接器，請在第一條訊息中確切說明遺失的內容並停止。不要替代、模擬或猜測。
- 不要在沒有在執行緒中詢問我的情況下合併、強制推送或變更 CI 設定。

```

關於一個儲存庫的規則，例如其建置命令，屬於該儲存庫的 `CLAUDE.md`，每個執行緒在儲存庫是專案的一部分時讀取。一旦工作開始，當您更正執行緒時，也要告訴 Claude 記住更正：它進入[專案記憶](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context)，稍後的執行緒開始時會有它。

### 決定要新增哪些儲存庫

您新增到專案的儲存庫在每個執行緒中都帶有其中的所有內容、其程式碼、`CLAUDE.md` 和技能。您不新增的儲存庫仍在範圍內：執行緒在其任務需要時可以將其新增到自己。大多數專案同時使用兩者：

- **將其新增到專案** ，在**新專案** 對話中、在**專案設定 > 環境**中，或通過在對話中要求 Claude 將其新增到專案。從那時起，每個執行緒都會複製它並開始使用其 `CLAUDE.md` 和技能，無論任務是否涉及它。從一個儲存庫轉到多個儲存庫也會改變執行緒從每個儲存庫的 `.claude/settings.json` 中取得的內容；請參閱[執行緒從您的儲存庫中取得什麼](https://code.claude.com/docs/zh-TW/claude-projects#what-threads-pick-up-from-your-repositories)。
- **不要新增它，讓執行緒在需要時自行新增。** 其任務需要專案沒有的儲存庫的執行緒可以將其新增到自己，執行緒中的筆記表示它僅被新增到此執行緒。複製發生在任務進行中途，因此該儲存庫的 `CLAUDE.md` 和技能在執行緒啟動時不存在。下一個執行緒再次啟動時沒有它。執行緒新增的儲存庫需要與專案儲存庫相同的[先決條件](https://code.claude.com/docs/zh-TW/claude-projects#check-the-prerequisites)：在其上安裝的 Claude GitHub App 和來自您的 GitHub 帳戶的推送存取。

專案根本不需要儲存庫。其執行緒仍然可以進行研究、寫入文件，以及在自己的沙箱中寫入和執行程式碼，並將檔案傳遞到**程式庫** 標籤。那裡的執行緒也可以在任務需要時將儲存庫新增到自己。 一旦專案有了儲存庫，Claude 只能從專案已經使用的 GitHub 擁有者新增儲存庫，無論它是將其新增到專案還是執行緒將其新增到自己。要引入來自不同擁有者的儲存庫，請在**專案設定 > 環境**中自己新增它。 對於跨越許多儲存庫的專案，例如一個具有伺服器、網路、行動和桌面程式碼的功能，新增幾乎每個任務都涉及的一個或兩個儲存庫，並在[專案指示](https://code.claude.com/docs/zh-TW/claude-projects#write-project-instructions)中命名其他儲存庫，以便 Claude 知道其餘程式碼的位置。執行緒然後開始很小，只為需要它們的任務拉入其他儲存庫。

### 執行緒從您的儲存庫中取得什麼

每個執行緒複製專案中的每個儲存庫，並從所有儲存庫載入 `CLAUDE.md`、技能和外掛程式。權限規則、hooks 和 `env` 僅來自執行緒啟動所在目錄中的 `.claude/settings.json`：當專案有一個時在儲存庫內，當它有多個時在複製上方，其中沒有儲存庫的檔案被讀取用於它們。

| 在每個儲存庫中                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 一個儲存庫                                                                                                                                   | 多個儲存庫                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `CLAUDE.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 在執行緒啟動時載入                                                                                                                           | 在執行緒啟動時從每個儲存庫載入                                                                    |
| `.claude/` 下的技能、代理和命令                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 已載入                                                                                                                                       | 從每個儲存庫載入                                                                                  |
| 在 `.claude/settings.json` 中啟用的外掛程式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 已載入                                                                                                                                       | 從每個儲存庫載入。如果兩個儲存庫對外掛程式意見不一致，請在**專案設定 > 外掛程式**中設定它，這優先 |
| 在 `.claude/settings.json` 中定義的權限規則、hooks 和 `env`                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 套用到執行緒，除了[沒有雲端工作階段遵守](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)的 `env` 鍵 | 不套用                                                                                            |
| 在具有多個儲存庫的專案中，每個複製都附加到執行緒作為[其他目錄](https://code.claude.com/docs/zh-TW/memory#load-from-additional-directories)，啟用了 `CLAUDE.md` 載入，這就是為什麼每個儲存庫的 `CLAUDE.md` 和技能在啟動時載入，儘管執行緒在它們上方啟動。在任何一種情況下，啟用的外掛程式提供的 hooks 仍然執行，因為外掛程式從每個儲存庫載入。在具有多個儲存庫的專案中，將常設規則放在專案指示中，並通過[雲端環境](https://code.claude.com/docs/zh-TW/claude-projects#choose-an-environment-for-threads)為執行緒提供環境變數。 |                                                                                                                                              |                                                                                                   |

### 為執行緒選擇環境

每個新執行緒在專案的[雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)中啟動。環境設定執行緒可以到達哪些網域、它們有哪些環境變數、哪些 API 認證被新增到它們的請求，以及設定指令碼在 Claude 啟動前安裝什麼。執行緒使用預設的 Anthropic 託管環境，直到您在**專案設定 > 環境**中選擇一個。 如果執行緒需要到達內部 API 或私有套件登錄，或需要您的機器通常持有的令牌，請變更環境而不是專案：請參閱[網路存取](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)、[新增 API 認證](https://code.claude.com/docs/zh-TW/cloud-environments#add-api-credentials)和[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)。

### 將技能、外掛程式、連接器和工具引入執行緒

執行緒是雲端工作階段，因此它們沒有僅在您的機器上安裝的技能、MCP 伺服器、外掛程式和工具。要使這些中的每一個對執行緒可用：

- 技能、子代理和命令：將它們提交到您新增到專案的儲存庫，例如 `.claude/skills/<skill-name>/SKILL.md` 中的技能。每個執行緒複製專案中的每個儲存庫，並從每個儲存庫載入 `.claude/skills/`、`.claude/agents/` 和 `.claude/commands/`，因此提交到一個儲存庫的技能在每個新執行緒中可用。執行緒也載入您為 claude.ai 帳戶啟用的技能。
- 外掛程式：在**專案設定 > 外掛程式**中新增它們；它們載入到每個新執行緒。儲存庫在其 `.claude/settings.json` 中宣告的外掛程式也載入；請參閱[什麼從您的設定中攜帶](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)。
- MCP 伺服器：執行緒從您的 claude.ai 帳戶上的連接器獲取其 MCP 工具，這些是您在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 或通過**專案設定 > 環境**中的**管理連接器** 連結連接一次的 MCP 伺服器。每個執行緒可以使用所有它們，無需每個專案的設定。專案對話本身沒有連接器，因此將需要連接器的工作作為執行緒的任務傳送。在具有一個儲存庫的專案中，執行緒也從該儲存庫的 [`.mcp.json`](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup) 載入 MCP 伺服器。[連接器如何到達 Claude Code](https://code.claude.com/docs/zh-TW/mcp#how-connectors-reach-claude-code) 列出雲端工作階段的規則和關閉連接器的設定。
- 命令列工具和套件：在環境的[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)中安裝它們。

要查看執行中的執行緒在 claude.ai/code 有哪些連接器，請開啟執行緒並從其訊息框旁邊的 **+** 功能表中選擇**連接器** 。關閉連接器會將其從該執行緒中移除，並將其儲存為您的帳戶預設值，因此新執行緒和 claude.ai 聊天在您重新開啟它之前開始時沒有它。執行緒在您傳送給它的下一條訊息後取得您新增或重新連接的連接器。

## Project 設定參考

您在 claude.ai/code 或桌面應用程式中更改 project 設定，而不是在 `settings.json` 中。從 project 側邊欄功能表中的 **Settings** 或 project 標題中的齒輪圖示打開 **Project settings** 。 設定在您更改時保存；您正在編輯的文本欄位，例如目標或指示，顯示 **Save changes** 和 **Discard** ，直到您離開它。對指示、儲存庫、plugins 和 **Project settings** 中環境的更改到達新執行緒，而不是已在執行的執行緒。

| 設定                   | 部分        | 它控制什麼                                                                                                                                        |
| ---------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 名稱、圖示和目標       | General     | project 在側邊欄中的名稱和圖示，以及其一行目標                                                                                                    |
| Coordinator 模型和努力 | General     | project 對話中 Claude 的模型和 [努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)                                    |
| Thread 模型和努力      | General     | 執行緒的模型和努力級別                                                                                                                            |
| Project 指示           | Memory      | [常設規則](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context) 每個新執行緒接收                                   |
| Project 儲存庫         | Environment | 新執行緒克隆的儲存庫                                                                                                                              |
| 雲端環境               | Environment | 新執行緒執行的 [雲端環境](https://code.claude.com/docs/zh-TW/claude-projects#choose-an-environment-for-threads)                                   |
| Connectors             | Environment | 管理 claude.ai connectors 執行緒獲取的連結                                                                                                        |
| Plugins                | Plugins     | 加載到每個新執行緒中的 plugins                                                                                                                    |
| Usage                  | Usage       | 按執行緒和模型的 [令牌使用](https://code.claude.com/docs/zh-TW/claude-projects#usage-and-cost)                                                    |
| Memory                 | Memory      | project 的 [記憶檔案](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context)                                         |
| Restart Claude         | General     | 當 [Claude 在那裡停止回應](https://code.claude.com/docs/zh-TW/claude-projects#claude-hasnt-responded) 時重新啟動 project 對話                     |
| Pause、Archive、Delete | General     | 停止、隱藏或移除 project；請參閱 [暫停、存檔或刪除 project](https://code.claude.com/docs/zh-TW/claude-projects#pause-archive-or-delete-a-project) |

### 暫停、存檔或刪除 project

所有三個控制都在 **Project settings > General** 的底部：

- **Pause** ：立即停止所有內容。每個執行中的執行緒和對話都被中斷，沒有新執行緒啟動，routines 不執行，project 在您恢復它之前不接受訊息。點擊相同位置或 project 訊息框上方的橫幅中的 **Resume** ；暫停的執行緒在您之後發送訊息時繼續。
- **Archive** ：從側邊欄隱藏 project 並存檔其執行緒，這停止任何執行中或監視提取請求的執行緒。project 存檔時，project 中的 routines 不執行。要帶回 project，從 Projects 頁面打開它並點擊 **Unarchive** 。其執行緒保持存檔，直到您從工作階段清單中單獨取消存檔它們。
- **Delete** ：永久移除 project 及其執行緒、其記憶和其檔案，並關閉 project 的 routines。這無法撤銷。執行緒推送到 GitHub 的分支和提取請求不受影響。

## 使用和成本

Project 使用計入與您其他 Claude Code 工作階段相同的 [方案限制](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-session-limit)，project 無法自己超過這些限制。 到達您方案限制的執行緒等待並在限制重置時自己繼續，因此您留下執行的工作在您的下一個使用視窗中開始使用，無需來自您的訊息。[執行緒達到使用限制](https://code.claude.com/docs/zh-TW/claude-projects#usage-limit-reached) 涵蓋了您看到的內容、如何停止它，以及不等待的一種情況。 工作僅在您為帳戶打開 [使用信用](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription) 時才超過您的方案限制。執行緒無法為您打開它們。

### 什麼使用您的方案

Project 比單個工作階段更快地使用您的限制，特別是在 Pro 方案上，您應該期望在執行一個的日子裡更快到達您的限制。project 的這些部分使用您的方案：

- **執行中的執行緒** ：每個都是一個完整的工作階段，多個可以同時執行。沒有固定數字；Claude 啟動工作需要的數量，您 [要求](https://code.claude.com/docs/zh-TW/claude-projects#tune-how-claude-runs-a-project) 的限制是偏好而不是上限。強制執行的限制是每天跨您的 projects 200 個新執行緒。
- **對話** ：Claude 使用自己的令牌讀取執行緒報告的內容並決定下一步做什麼。
- **執行緒監視提取請求** ：空閒執行緒在 CI 失敗或審查評論到達其提取請求時喚醒並再次使用您的方案。要停止它，在執行緒中要求它停止監視提取請求。

沒有執行中的執行緒、沒有監視的提取請求和沒有新訊息的 project 在它閒置時不使用您的方案，存檔的 project 也不使用。

### 查看並減少 project 的使用

在 **Project settings** 中打開 **Usage** 以查看按執行緒和模型的令牌使用，以及多少進入 project 對話。要降低它：

- 路由到已閒置超過 [快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)（Pro 和 Max 在您方案限制內為一小時）的執行緒的後續工作在執行任何操作之前重新讀取該執行緒的整個對話。對於新工作，要求 Claude 啟動新執行緒可以使用比復興大型舊執行緒更少。
- 對於不需要最大模型的工作，[為執行緒、對話或兩者選擇較小的模型或較低的努力級別](https://code.claude.com/docs/zh-TW/claude-projects#choose-models-and-let-claude-manage-context)。
- 要求 Claude 在 project 對話中一次執行更少的執行緒，或自己回答小問題而不是啟動執行緒。

## Projects 與其他 Claude Code 功能的關係

幾個 Claude Code 功能讓多個工作階段同時工作，因此平行執行工作本身不是 project 的用途。在 project 中，Claude 啟動並跟蹤工作階段而不是您，每個都從相同的儲存庫、指示和記憶開始，工作在雲端中只要它持續就存在。以下是每個相鄰功能如何連接到 project：

- **Claude Tag** ：[Claude Tag](https://claude.com/docs/claude-tag/overview) 是您團隊 Slack 頻道中的 Claude，在 Team 和 Enterprise 方案上。頻道中的任何人都可以給它工作，頻道中的每個人都看到並引導它，它使用管理員為該頻道設定的連接。project 是您的：您是唯一給它工作或看到其執行緒的人，它使用您自己的 GitHub 存取和 connectors，它在 Pro 和 Max 上。[Claude Tag 與 Cowork 和 Claude Code 的不同之處](https://claude.com/docs/claude-tag/concepts/how-it-works#how-claude-tag-differs-from-cowork-and-claude-code) 有並排比較。
- **雲端工作階段** ：每個執行緒是一個 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，由 Claude 而不是您啟動和跟蹤。您自己啟動的雲端工作階段可以通過 [**Continue as a project** 或 **Move to project**](https://code.claude.com/docs/zh-TW/claude-projects#start-from-an-existing-cloud-session) 成為 project 或提供一個。
- **Routines** ：當您在 project 中要求排程工作時，Claude 建立一個 [routine](https://code.claude.com/docs/zh-TW/routines)，在該 project 中作為執行緒執行，並出現在其 **Routines** 標籤上。您在 project 外建立的 Routines 保持自己工作。
- **本地工作階段和代理檢視** ：您終端、IDE 或桌面應用程式本地環境中的工作階段在您的機器上執行，無法成為 project 的一部分。[代理檢視](https://code.claude.com/docs/zh-TW/agent-view) 是用於跟蹤多個那些本地工作階段的螢幕；它沒有協調者。
- **Worktrees** ：[worktree](https://code.claude.com/docs/zh-TW/worktrees) 給每個本地工作階段其自己的儲存庫工作副本，因此您機器上的平行工作階段不會相互覆蓋。執行緒不需要它們：每個執行緒將其儲存庫克隆到其自己的雲端沙箱中，並在自己的分支上工作。
- **代理團隊** ：[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams) 是一個工作階段，為單個任務啟動隊友工作階段，在您的機器上或在雲端工作階段內，並以該任務結束。
- **claude.ai 聊天和 Cowork 中的 Projects** ：[早期 Projects 體驗](https://support.claude.com/en/articles/9517075-what-are-projects)，它對話和參考檔案進行分組，沒有執行緒或協調者。那些 projects 保持今天的工作方式，直到重新設計的體驗到達它們。

[平行執行代理](https://code.claude.com/docs/zh-TW/agents) 並排比較這些選項。

## 限制

- Projects 在 claude.ai/code、桌面應用程式和 Claude 行動應用程式中可用，不在終端 CLI 或通過 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 中。CLI 的 [`claude project`](https://code.claude.com/docs/zh-TW/cli-reference) 命令，它管理目錄的本地 Claude Code 狀態，是無關的。
- Project 執行緒是 [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，Anthropic 作為模型提供者。[安全](https://code.claude.com/docs/zh-TW/security) 和 [資料使用](https://code.claude.com/docs/zh-TW/data-usage) 涵蓋了雲端工作階段如何隔離以及保留什麼。
- 本地工作階段無法成為 project 的一部分。
- 執行緒的沙箱在轉換之間暫停，並在執行緒繼續時恢復。如果沙箱無法恢復，執行緒從新克隆繼續，因此未提交的變更可能會丟失。在長任務上，要求 Claude 提交並推送進行中的工作。
- project 屬於一個使用者。您無法與另一個使用者共享 project 或其執行緒，執行緒記錄沒有其他雲端工作階段具有的共享選項。在測試版期間，projects 沒有組織級控制。
- 執行緒屬於啟動它的一個 project。您無法將執行緒移動或複製到另一個 project，或將其移出以獨立存在。[**Move to project**](https://code.claude.com/docs/zh-TW/claude-projects#start-from-an-existing-cloud-session) 僅以另一種方式進行：它將雲端工作階段的工作帶入 project。

## 故障排除

對於 **New project** 對話框中的 GitHub 設定提示，請參閱 [設定 GitHub 存取](https://code.claude.com/docs/zh-TW/claude-projects#set-up-github-access)。

### 執行緒看起來卡住了

Claude 不發佈執行緒採取的每一步，因此顯示為執行中且 project 對話中沒有新訊息的執行緒通常仍在工作。新執行緒也在 Claude 開始之前配置其 [雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)，因此其第一次更新需要片刻。打開執行緒讀取其記錄。如果執行緒正在等待權限提示，在那裡回答它。

### 執行緒猜測或停滯而不是詢問

當多個執行緒回來假設了錯誤的內容、解決了缺失的存取或停止了「被阻止」，原因通常是 project 設定中的相同間隙，而不是每個任務的問題。在修復任何內容之前排序哪些執行緒是健全的：

1. 在對話中要求 Claude：「對於每個打開的執行緒，列出您要求它做什麼、它假設或無法到達的內容，以及它正在等待什麼。」Claude 讀取每個執行緒並在對話中回答。
1. 對於從錯誤假設開始的執行緒，從 **Overview** 打開執行緒並從其功能表標記為已解決，或在其訊息框中告訴它改為做什麼。其分支和任何提取請求保留在 GitHub 上，直到您刪除它們。
1. 在 [project 指示](https://code.claude.com/docs/zh-TW/claude-projects#give-a-project-standing-context) 或 [環境](https://code.claude.com/docs/zh-TW/claude-projects#choose-an-environment-for-threads) 中修復間隙一次，然後在再次發送其餘工作作為新執行緒之前發送一個執行緒。

### Claude 還沒有回應

當 Claude 執行但其回覆未到達 project 時，project 對話顯示「Claude hasn’t responded」橫幅。點擊橫幅上的 **Restart Claude** ，或前往 **Project settings > General** 並在 **Restart Claude** 行中點擊 **Restart** 。Claude 重新連接到對話；它正在寫的任何回覆都丟失，執行緒不受影響。

### 儲存庫存取錯誤

三條訊息意味著執行緒或 project 無法到達其儲存庫之一。project 執行緒需要 [GitHub 先決條件](https://code.claude.com/docs/zh-TW/claude-projects#check-the-prerequisites)，即使您的其他雲端工作階段克隆相同儲存庫而沒有麻煩。

- **「Couldn’t start the session — Claude doesn’t have GitHub access to this project’s repository」** ，在執行緒啟動之前報告，當 Claude GitHub App 未安裝在該儲存庫上、已暫停或未連結到您連接的 GitHub 帳戶時。
- **「Unable to access your repository」** ，由執行緒報告，當其克隆失敗時：GitHub 拒絕克隆、在 project 具有的名稱下找不到儲存庫，或執行緒被要求啟動的分支不存在。
- **「Claude can’t access」** 儲存庫，在您在 **New project** 對話框或 **Project settings** 中保存儲存庫時顯示。訊息繼續帶有安裝連結和重新連接連結。如果 Claude GitHub App 不在該儲存庫上，使用安裝連結，如果它是，使用重新連接連結，因為 GitHub App 可以在 GitHub 上安裝而不連結到您連接到 Claude 的帳戶。如果訊息說 GitHub App 已暫停或不包括此儲存庫，請遵循其連結到 GitHub 以修復它。

要修復任何一個，點擊訊息提供的按鈕，例如 **Install GitHub App** 或 **Select repositories on GitHub** ，然後 **Check again** 。當塊在 GitHub 組織一側時，例如尚未批准應用程式的所有者或排除 Claude 的 IP 允許清單，訊息改為顯示 **See how to fix** 連結。如果沒有按鈕，請遵循 [設定 GitHub 存取](https://code.claude.com/docs/zh-TW/claude-projects#set-up-github-access)，然後發送另一條訊息重試。

### 執行緒達到使用限制

當執行緒或 project 對話達到您方案的五小時或每週限制時，它自己保持重試並在限制重置時繼續。在它等待時，執行緒顯示 **Service is busy** ，帶有「Claude is still retrying and will continue automatically。」您不需要做任何事情讓工作繼續。如果您寧願它不使用您的下一個使用視窗，點擊執行緒中的 **Stop** ，或 [暫停 project](https://code.claude.com/docs/zh-TW/claude-projects#pause-archive-or-delete-a-project) 以保持每個執行緒。routine 啟動的執行緒不等待：其轉換停止，帶有限制錯誤，您在限制重置後發送它訊息。 [使用限制錯誤](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-session-limit) 解釋了限制以及何時重置。

### 需要額外的使用信用

執行緒或 project 對話發出了您的方案僅使用使用信用涵蓋的請求，例如對您的方案不包括的模型或上下文大小的請求，並且使用信用未為您的帳戶打開。[將使用信用添加到您的訂閱](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription) 涵蓋了誰可以在每個方案上打開或購買它們。一旦信用可用，發送另一條訊息重試。

### 其他訊息

這些訊息命名它們自己的原因。表格為每個提供下一步。

| 訊息                                                                                               | 要做什麼                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 「Unable to connect to repository」，帶有「Claude couldn’t reach GitHub to fetch your repository」 | 等待片刻，然後發送另一條訊息重試                                                                                                                                                  |
| 「Unable to connect to repository」，帶有「Claude couldn’t access your repository or environment」 | 您的 GitHub 帳戶需要對儲存庫的推送存取，環境必須仍然存在。在 **Project settings > Environment** 中檢查兩者，然後重試                                                              |
| 「Couldn’t show the setup proposal」                                                               | 您打開的應用程式比 Claude 發送的 **Setup recommendations** 更舊。刷新頁面或重新啟動桌面應用程式，或要求 Claude 再次提議設定                                                       |
| 「The project’s environment was removed」                                                          | 在 **Project settings > Environment** 中選擇不同的環境；更改適用於新執行緒                                                                                                        |
| 「Setup script failed」                                                                            | 點擊錯誤上的 **Edit setup script** ，在環境中修復指令碼，然後發送另一條訊息。[設定指令碼失敗](https://code.claude.com/docs/zh-TW/web-quickstart#setup-script-failed) 列出常見原因 |
| 「Claude ran out of context on this turn」                                                         | 執行緒填滿了其上下文視窗。如果訊息說執行緒在新工作階段中繼續，它自己進行；否則在 project 對話中要求 Claude 為剩餘工作啟動新執行緒                                                 |
| 「Reached the turn limit」                                                                         | 執行緒達到了 [`CLAUDE_CODE_MAX_TURNS`](https://code.claude.com/docs/zh-TW/env-vars) 設定的代理轉換上限。發送另一條訊息繼續，或在設定它的地方提高或移除該變數                      |

## 相關資源

- [在雲端使用 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：每個執行緒後面的雲端工作階段如何工作，包括 GitHub 存取選項和提取請求上的 auto-fix
- [配置雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)：更改執行緒可以在網路上到達的內容、給予它們環境變數和 API 認證，以及使用設定指令碼安裝工具
- [使用 routines 自動化工作](https://code.claude.com/docs/zh-TW/routines)：routines 的時間表、觸發器和管理，包括 Claude 從 project 建立的
- [使用代理檢視管理多個代理](https://code.claude.com/docs/zh-TW/agent-view)：當工作需要只有您的機器才能到達的工具或服務時，在您自己的機器上執行和跟蹤多個工作階段
- [Projects 重新設計：從資料夾到對話](https://claude.com/blog/projects-redesigned)：啟動公告，帶有使 project 成為與 Claude 對話的思考

是否 助手
