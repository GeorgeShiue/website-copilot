雲端會話處於研究預覽階段，適用於 Pro、Max 和 Team 使用者，以及擁有高級席位或 Chat + Claude Code 席位的企業使用者。 雲端會話在雲端基礎設施上執行 Claude Code，而不是在您的機器上，預設由 Anthropic 管理。此快速入門從瀏覽器中的 [claude.ai/code](https://claude.ai/code) 啟動一個會話。您也可以從 Claude 行動應用程式、Desktop 應用程式或終端機使用 `claude --cloud` 啟動一個會話。 您需要一個 GitHub 儲存庫來[開始使用](https://code.claude.com/docs/zh-TW/web-quickstart#connect-github)。Claude 將其複製到隔離的虛擬機器中、進行更改，並為您推送一個分支以供檢查。會話在設備間持續存在，因此您在筆記型電腦上開始的任務可以稍後從手機上檢查。 雲端會話適用於：

- **並行任務** ：同時執行多個獨立任務，每個任務在自己的會話和分支中，無需管理多個 worktrees
- **您本地沒有的儲存庫** ：Claude 在每個會話中新鮮複製儲存庫，因此您無需簽出它
- **不需要頻繁引導的任務** ：提交一個定義明確的任務，做其他事情，並在 Claude 完成時檢查結果
- **代碼問題和探索** ：理解代碼庫或追蹤功能如何實現，無需本地簽出

對於需要您本地設定、工具或環境的工作，在本地執行 Claude Code 或使用 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 更合適。

## 會話如何執行

以下步驟描述 Anthropic 託管的會話。在[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)中，複製和之後的所有操作都在您組織自己的執行器上執行，其中網路邊界、設定和推送行為由操作員配置。當您提交任務時：

1. **複製和準備** ：您的儲存庫被複製到 Anthropic 管理的 VM，並且您的[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)會在配置時執行。
1. **配置網路** ：根據您環境的[存取級別](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)設定網際網路存取。
1. **工作** ：Claude 分析代碼、進行更改、執行測試並檢查其工作。您可以全程觀看和引導，或者離開並在完成時返回。
1. **推送分支** ：當 Claude 達到停止點時，它會將其分支推送到 GitHub。您檢查差異、留下內聯評論、建立 PR 或發送另一條訊息以繼續。

推送分支時會話不會關閉。PR 建立和進一步編輯都在同一對話中進行。

## 比較執行 Claude Code 的方式

Claude Code 在任何地方的行為都相同。改變的是代碼執行的位置以及您的本地設定是否可用：

|                                                                                                                                                                                                                                         | 雲端會話                                                                                                                                | 本地會話                                                                                                                                            | 本地會話搭配 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **代碼執行於**                                                                                                                                                                                                                          | 雲端 VM，預設由 Anthropic 管理                                                                                                          | 您的機器                                                                                                                                            | 您的機器                                                                         |
| **您從以下位置啟動**                                                                                                                                                                                                                    | claude.ai/code、Claude 行動應用程式、選擇 **Cloud** 的 Desktop 應用程式，或 `claude --cloud`                                            | 您的終端、您的 IDE，或選擇 **Local** 的 Desktop 應用程式                                                                                            | 您的終端、VS Code 擴充功能，或 Desktop 應用程式                                  |
| **您從以下位置聊天**                                                                                                                                                                                                                    | claude.ai、行動應用程式，或 Desktop 應用程式                                                                                            | 您啟動它的位置                                                                                                                                      | claude.ai 或行動應用程式，以及您啟動它的位置                                     |
| **使用您的本地設定**                                                                                                                                                                                                                    | 否，僅儲存庫                                                                                                                            | 是                                                                                                                                                  | 是                                                                               |
| **需要 GitHub**                                                                                                                                                                                                                         | 是，或透過 `--cloud` [捆綁本地儲存庫](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-local-repositories-without-github) | 否                                                                                                                                                  | 否                                                                               |
| **如果您斷開連接，保持執行**                                                                                                                                                                                                            | 是                                                                                                                                      | 否                                                                                                                                                  | 當會話在您的機器上保持開啟時                                                     |
| **[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)**                                                                                                                                                                     | 接受編輯、Plan、Auto                                                                                                                    | 終端中的所有模式；請參閱 [切換權限模式](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes) 以了解 IDE 和 Desktop 應用程式 | 來自 claude.ai 和行動應用程式的手動、接受編輯或 Plan                             |
| **網路存取**                                                                                                                                                                                                                            | 每個環境可配置                                                                                                                          | 您機器的網路                                                                                                                                        | 您機器的網路                                                                     |
| 請參閱 [terminal quickstart](https://code.claude.com/docs/zh-TW/quickstart)、[Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop) 或 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 文件以設定本地會話。 |                                                                                                                                         |                                                                                                                                                     |                                                                                  |

## 連接 GitHub

連接 GitHub 是一次性步驟。如果您已經使用 GitHub CLI，您可以[從終端執行此操作](https://code.claude.com/docs/zh-TW/web-quickstart#connect-from-your-terminal)，而不是使用瀏覽器。 在 Team 和 Enterprise 方案上，**使用 GitHub 登入** 步驟僅在您的 Claude 組織的[擁有者](https://code.claude.com/docs/zh-TW/server-managed-settings#access-control)在[**管理設定 > 連接器**](https://claude.ai/admin-settings/connectors)開啟 GitHub 連接器後才有效。在此之前，該步驟會顯示「GitHub 存取權是 Claude Code 網頁版所需」而不是登入按鈕。連接器開啟後，重新載入 [claude.ai/code](https://claude.ai/code) 並從第一步重新開始。第二個切換開關[快速網頁設定](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)位於[**管理設定 > Claude Code**](https://claude.ai/admin-settings/claude-code)，是選用的：開啟時，`/web-setup` 可運作，且上線流程會為成員建立環境。 1 造訪 claude.ai/code 前往 [claude.ai/code](https://claude.ai/code) 並使用您的 claude.ai 帳戶登入。 2 使用 GitHub 登入 登入後，claude.ai/code 會提示您連接 GitHub。按照提示操作，claude.ai/code 會將您導向 GitHub 的授權頁面。核准授權要求，GitHub 會將您返回 claude.ai/code。雲端工作階段可與現有 GitHub 儲存庫搭配使用。若要啟動新專案，請先[在 GitHub 上建立空白儲存庫](https://github.com/new)。透過此連接，工作階段可以複製任何公開儲存庫，但只有在 Claude GitHub App 安裝在私人儲存庫上時，才能在私人儲存庫中工作。[在您想要使用其私人儲存庫的每個 GitHub 帳戶或組織上安裝 Claude GitHub App](https://github.com/apps/claude/installations/new)。在 GitHub 組織上，組織擁有者可能需要核准安裝。安裝應用程式也會啟用[自動修復](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)，讓 Claude 能夠回應這些儲存庫中的 CI 失敗和提取要求審查意見。如果上線流程在此時提示您安裝 Claude GitHub App，而您想稍後再安裝，請按一下**略過** 。 3 設定您的預設環境 [雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)是已儲存的設定，控制 Claude 在工作階段期間具有的網路存取權，以及工作階段啟動時執行的內容。連接 GitHub 後發生的情況取決於您的方案：

- **Pro 和 Max** ：上線流程會為您建立名為**預設** 的環境。
- **Team 和 Enterprise** ：上線流程會顯示**建立您的第一個雲端環境** 表單。保持預填的名稱和網路存取權不變，然後按一下**建立並完成** 以建立**預設** 環境。如果擁有者已開啟[快速網頁設定](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)，上線流程會改為為您建立**預設** 。

**預設** 使用[`信任`網路存取權](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)：工作階段可以存取[常見套件登錄](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)和其他允許清單中的網域，以及透過工作階段網路的其他任何內容都無法存取。請參閱[已安裝的工具](https://code.claude.com/docs/zh-TW/cloud-environments#installed-tools)以了解無需任何設定即可使用的內容。對於第一個專案，**預設** 環境可以按原樣使用。若要變更其網路存取權、新增環境變數或在工作階段啟動前執行[設定指令碼](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts)，請[編輯它或建立其他環境](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)。

### 從您的終端連接

如果您已經使用 GitHub CLI (`gh`)，您可以從終端為雲端工作階段連接 GitHub。這需要 [Claude Code CLI](https://code.claude.com/docs/zh-TW/quickstart)。在 Team 和 Enterprise 方案上，`/web-setup` 僅在擁有者開啟[快速網頁設定](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)後才可用。 當您執行 `/web-setup` 時，Claude Code 會讀取 `gh auth token` 列印的權杖，要求您確認，並將權杖傳送給 Anthropic。Anthropic 會使用您的 claude.ai 帳戶加密儲存它，您的雲端工作階段會使用它進行 GitHub 存取，直到您[移除它](https://code.claude.com/docs/zh-TW/web-quickstart#remove-the-web-setup-token)。您自己啟動的雲端工作階段隨後可以存取該權杖可以存取的任何儲存庫，無需 Claude GitHub App 安裝。[專案](https://code.claude.com/docs/zh-TW/claude-projects#set-up-github-access)中的執行緒仍然需要 Claude GitHub App。 如果您已經在瀏覽器中連接了 GitHub，`/web-setup` 會警告您繼續將會取代您的雲端工作階段的該連接。 啟用[零資料保留](https://code.claude.com/docs/zh-TW/zero-data-retention)的組織無法使用 `/web-setup` 或其他雲端工作階段功能。如果未安裝 GitHub CLI 或未進行驗證，Claude Code 會改為開啟瀏覽器上線流程。 1 使用 GitHub CLI 進行驗證 在您的 shell 中，如果您還沒有驗證 GitHub CLI，請進行驗證：

```
gh auth login

```

2 登入 Claude 在 Claude Code CLI 中，執行 `/login` 以使用您的 claude.ai 帳戶登入。如果您已經使用 claude.ai 帳戶登入，請略過此步驟。使用 API 金鑰進行驗證不計算在內。若要檢查，請執行 `/status` 並確認**登入方法** 列顯示 claude.ai 帳戶。 3 執行 /web-setup 在 Claude Code CLI 中，執行：

```
/web-setup

```

確認提示以將您的 `gh` 權杖傳送到您的 Claude 帳戶。成功時，Claude Code 會列印 `Connected as <your-github-username>` 並在您的瀏覽器中開啟 [claude.ai/code](https://claude.ai/code)。如果您還沒有雲端環境，`/web-setup` 會建立一個具有信任網路存取權且沒有設定指令碼的環境。您可以[稍後編輯環境或新增變數](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)。`/web-setup` 完成後，您可以使用 [`--cloud`](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud) 從終端啟動雲端工作階段，或使用 [`/schedule`](https://code.claude.com/docs/zh-TW/routines) 設定定期工作。

#### 移除 `/web-setup` 權杖

若要從您的 Claude 帳戶移除權杖，請在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 斷開 GitHub 連接。斷開連接會刪除您的雲端工作階段使用的 GitHub 認證，無論它們來自瀏覽器還是 `/web-setup`，因此雲端工作階段會失去 GitHub 存取權，直到您再次連接。您的本機 `gh` 保持登入狀態，權杖在 GitHub 上保持有效。 若要使權杖本身失效，請在 GitHub 上撤銷它。如果您透過瀏覽器登入 `gh`，權杖屬於 GitHub 上[**設定 > 應用程式 > 授權的 OAuth 應用程式**](https://github.com/settings/applications)下的 **GitHub CLI** 項目，撤銷該項目也會在您的機器上將 GitHub CLI 登出。雲端工作階段隨後會失去 GitHub 存取權，直到您再次執行 `gh auth login` 和 `/web-setup`。

## 啟動任務

連接 GitHub 並建立環境後，您就可以提交任務了。 1 選擇儲存庫和分支 從 [claude.ai/code](https://claude.ai/code) 或 Claude 行動應用程式中的 Code 標籤，點擊輸入框下方的儲存庫選擇器，並為 Claude 選擇要在其中工作的儲存庫。每個儲存庫都顯示一個分支選擇器。將其更改為從功能分支而不是預設分支啟動 Claude。您可以新增多個儲存庫以在一個會話中跨它們工作。 2 選擇權限模式 輸入框旁邊的模式下拉菜單顯示會話將在其中執行的模式：

- **Auto** ：分類器會檢查 Claude 的操作，而不是詢問您。當您的組織允許自動模式且選定的模型支援時出現
- **Accept edits** ：Claude 進行更改並推送分支，無需停止以獲得批准
- **Plan** ：Claude 提出方法並等待您批准後再編輯文件

雲端會話不提供 Manual 或 Bypass 權限。請參閱[權限模式完整列表](https://code.claude.com/docs/zh-TW/permission-modes#available-modes)以了解每個模式允許的操作。 3 描述任務並提交 輸入您想要的內容的描述並按 Enter。要具體：

- 命名文件或函數：“新增帶有設定說明的 README” 或 “修復 `tests/test_auth.py` 中失敗的驗證測試” 比 “修復測試” 更好
- 如果您有錯誤輸出，請貼上
- 描述預期行為，而不僅僅是症狀

Claude 複製儲存庫、執行您配置的設定指令碼（如果已配置）並開始工作。每個任務都有自己的會話和自己的分支，因此您無需等待一個完成就可以啟動另一個。

## 預填充會話

您可以透過將查詢參數新增到 [claude.ai/code](https://claude.ai/code) URL 來預填充新會話的提示、儲存庫和環境。使用此功能來建立整合，例如問題追蹤器中的按鈕，該按鈕使用問題描述作為提示打開 Claude Code。

| 參數                                                                | 描述                                                                                                       |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `prompt`                                                            | 要在輸入框中預填充的提示文本。也接受別名 `q`。                                                             |
| `prompt_url`                                                        | 要從中獲取提示文本的 URL，用於太長而無法嵌入查詢字符串的提示。URL 必須允許跨源請求。設定 `prompt` 時忽略。 |
| `repositories`                                                      | 要預選的 `owner/repo` 段的逗號分隔列表。也接受別名 `repo`。                                                |
| `environment`                                                       | [環境](https://code.claude.com/docs/zh-TW/web-quickstart#connect-github)的名稱或 ID 以預選。               |
| 對每個值進行 URL 編碼。下面的範例使用已選擇的提示和儲存庫打開表單： |                                                                                                            |

```
https://claude.ai/code?prompt=Fix%20the%20login%20bug&repositories=acme/webapp

```

## 檢查和迭代

當 Claude 完成時，檢查更改、在特定行上留下反饋，並繼續進行直到差異看起來正確。 1 打開差異檢視 差異指示器顯示整個會話中新增和移除的行，例如 `+42 -18`。選擇它以打開差異檢視，左側有文件列表，右側有更改。差異預設會與其基礎分支進行比較。若要與不同的分支進行比較，請選擇**比較對象** 並選擇一個。 2 留下內聯評論 選擇差異中的任何行，輸入您的反饋，然後按 Enter。評論會排隊直到您發送下一條訊息，然後它們會與其捆綁。Claude 看到「在 `src/auth.ts:47`，不要在這裡捕捉錯誤」以及您的主要指令，因此您無需描述問題所在。 3 建立拉取請求 當差異看起來正確時，選擇差異檢視頂部的**建立 PR** 。您可以將其作為完整 PR、草稿打開，或跳轉到 GitHub 的撰寫頁面，其中包含生成的標題和描述。 4 在 PR 後繼續迭代 會話在建立 PR 後保持活躍。將 CI 失敗輸出或審查者評論貼上到聊天中，並要求 Claude 解決它們。若要讓 Claude 自動監控 PR，請參閱[自動修復拉取請求](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#auto-fix-pull-requests)。

## 設定故障排除

### 連接 GitHub 後沒有儲存庫出現

如果您在瀏覽器中連接了 GitHub，會話可以複製任何公開儲存庫，但私有儲存庫只有在 Claude GitHub App 安裝在擁有它的帳戶或組織上，且安裝的儲存庫存取包括它時才會出現。[安裝 Claude GitHub App](https://github.com/apps/claude/installations/new)，或要求組織擁有者安裝或批准它。 如果您使用 `/web-setup` 連接，會話可以存取您的 `gh` 權杖可以存取的每個儲存庫。在您的 shell 中執行 `gh repo view OWNER/REPO` 以檢查您的 GitHub CLI 登入是否可以看到該儲存庫，如果您自連接以來已切換 `gh` 帳戶，請再次執行 `/web-setup`。

### 頁面只顯示 GitHub 登入按鈕

雲端會話需要連接的 GitHub 帳戶。透過上面的瀏覽器流程連接，或者如果您使用 GitHub CLI，從您的終端執行 `/web-setup`。如果您根本不想連接 GitHub，請參閱 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 以在您自己的機器上執行 Claude Code 並從網頁監控它。

### “不適用於選定的組織”

企業組織可能需要擁有者啟用雲端會話。聯繫您的 Anthropic 帳戶團隊。

### `/web-setup` 說 “Not signed in to Claude”

如果 `/web-setup` 回應 “Not signed in to Claude. Run /login first.”，CLI 沒有有效的 claude.ai 登入。當先前的登入已過期時，也可能發生這種情況。執行 `/login`，使用您的 claude.ai 帳戶登入，然後再次執行 `/web-setup`。

### `/web-setup` 警告您的權杖沒有 `workflow` 範圍

如果 `/web-setup` 說您的 GitHub CLI 權杖沒有 `workflow` 範圍，您可以繼續，但 GitHub 可能會拒絕使用該權杖進行的某些推送，例如更改 GitHub Actions 工作流程檔案的推送。要新增範圍，在您的 shell 中執行 `gh auth refresh -s workflow`，然後再次執行 `/web-setup`。

### `/web-setup` 顯示 “No commands match” 或 “Unknown command”

`/web-setup` 在 Claude Code CLI 內執行，而不是在您的 shell 中。首先啟動 `claude`，然後在提示符處輸入 `/web-setup`。 如果您在 Claude Code 內輸入它並且命令菜單顯示 `No commands match "/web-setup"`，或提交它返回 `Unknown command: /web-setup`，該命令被隱藏是因為未滿足要求。原因通常是您使用 API 金鑰或第三方提供商而不是 claude.ai 訂閱進行驗證。執行 `/login` 以使用您的 claude.ai 帳戶登入。 在 Team 和 Enterprise 方案上，該命令預設是隱藏的：[快速網頁設定切換](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)在擁有者開啟之前是關閉的。當它關閉時，[從瀏覽器連接 GitHub](https://code.claude.com/docs/zh-TW/web-quickstart#connect-github) 代替。 該命令在另外兩種情況下也被隱藏：

- 管理員已為您的組織停用雲端會話。在這種情況下，提交 `/web-setup` 會返回 [`Cloud sessions are disabled by your organization's policy`](https://code.claude.com/docs/zh-TW/errors#cloud-sessions-are-disabled-by-your-organizations-policy)。在 v2.1.268 之前，這種情況也會返回 `Unknown command: /web-setup`。
- 您的 Enterprise 組織已啟用[零資料保留](https://code.claude.com/docs/zh-TW/zero-data-retention)，這使雲端會話不可用。

### 使用 `--cloud` 時出現 “Could not create a cloud environment” 或 “No cloud environment available”

雲端會話功能會在您沒有雲端環境時自動建立預設雲端環境。如果您看到 “Could not create a cloud environment”，自動建立失敗。如果您看到 “No cloud environment available”，您的 CLI 早於自動建立。在任何一種情況下，在 Claude Code CLI 中執行 `/web-setup`，或從 [claude.ai/code](https://claude.ai/code) 的[環境選擇器](https://code.claude.com/docs/zh-TW/cloud-environments#configure-your-environment)新增環境。

### 設定指令碼失敗

設定指令碼以非零狀態退出，這會阻止會話啟動。常見原因：

- 套件安裝失敗，因為登錄不在您的[網路存取級別](https://code.claude.com/docs/zh-TW/cloud-environments#access-levels)中。`Trusted` 涵蓋大多數套件管理器；`None` 阻止它們全部。
- 指令碼引用在新鮮複製中不存在的檔案或路徑。
- 在本地工作的命令在 Ubuntu 上需要不同的調用。

要除錯，在指令碼頂部新增 `set -x` 以查看哪個命令失敗。對於非關鍵命令，附加 `|| true` 以便它們不會阻止會話啟動。

### 新會話在設定期間掛起或逾時

如果新會話在設定指令碼步驟上停滯或在指令碼完成前因通用容器錯誤而失敗，指令碼可能超過了大約五分鐘的時間預算來建立[環境快取](https://code.claude.com/docs/zh-TW/cloud-environments#environment-caching)。繁重的步驟，例如拉取大型 Docker 映像、同步完整依賴樹或下載模型權重，通常會將總數推過限制，特別是當它們一個接一個執行時。 要修復此問題，修剪指令碼以便它可靠地在五分鐘內完成：

- 使用 `&` 和最終 `wait` 並行執行獨立安裝，而不是按順序執行。
- 將最大的下載移出設定指令碼，進入 [SessionStart hook](https://code.claude.com/docs/zh-TW/cloud-environments#setup-scripts-vs-sessionstart-hooks)，在背景中啟動它們，以便會話在它們完成時變得可用。
- 從設定指令碼中移除長重試睡眠，因為停滯的重試迴圈會計入預算。

### 會話在關閉標籤後保持執行

這是設計使然。關閉標籤或導航離開不會停止會話。它在背景中繼續執行，直到 Claude 完成當前任務，然後閒置。從側邊欄，您可以[存檔會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#archive-sessions)以將其從列表中隱藏，或[刪除它](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#delete-sessions)以永久移除它。

## 後續步驟

現在您可以提交和檢查任務，這些頁面涵蓋接下來的內容：從您的終端啟動雲端會話、安排定期工作以及為 Claude 提供常設指令。

- [使用 Claude Code on the web](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)：完整參考，包括將會話傳送到您的終端、會話共享和自動修復提取請求
- [設定雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)：網路存取層級、環境變數和雲端會話的設定指令碼
- [Routines](https://code.claude.com/docs/zh-TW/routines)：按計劃、透過 API 呼叫或回應 GitHub 事件自動化工作
- [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)：為 Claude 提供在每個會話開始時載入的持久指令和上下文
- 安裝 Claude 行動應用程式以用於 [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 或 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 以從您的手機監控會話。從 Claude Code CLI，`/mobile` 顯示 QR 碼以用於 [claude.ai/mobile](https://claude.ai/mobile)，該碼會為您的手機開啟正確的應用程式商店。

是否 助手
