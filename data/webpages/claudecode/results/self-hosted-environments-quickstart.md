自託管環境在 Team 和 Enterprise 方案上處於公開測試版；[可用性和限制](https://code.claude.com/docs/zh-TW/self-hosted-environments#availability-and-limitations)涵蓋啟用路徑。本頁面讓您的第一個工作階段執行；請參閱[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)了解它們是什麼，以及[部署到生產環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy)以進行強化和艦隊配方。 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)在您的組織運營的基礎設施上執行 Claude Code [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，由您部署的執行器程序執行。本快速入門設定您的第一個環境，這是最小的可行設定：單一主機上的一個執行器，執行一個測試工作階段。有兩個步驟：[建立環境、啟動執行器並將工作階段路由到該環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart#set-up-an-environment-and-runner)，然後[從您的終端傳送後續訊息到執行中的工作階段](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart#send-a-follow-up-message-to-a-running-session)。您將在兩個介面之間移動：claude.ai 用於建立環境、檢查其狀態和路由工作階段，以及主機上的終端用於執行器執行的所有操作。 完成後，您將在[**雲端環境** 管理頁面](https://claude.ai/admin-settings/cloud-environments)上擁有一個環境、一個輪詢工作的執行器，以及在您的主機上執行的工作階段。在連接真實存放庫或內部系統之前，請完成[部署到生產環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy)，其中涵蓋安全態勢、出口控制、git 認證和編排。

## 先決條件

### 組織和角色

claude.ai 端需要：

- **允許自託管環境** 由[擁有者](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)在[**雲端環境** 管理頁面](https://claude.ai/admin-settings/cloud-environments)上開啟；在開啟之前，**新增** 按鈕不會出現。如果您不持有該角色，持有該角色的人可以建立環境並將其密鑰交給您；本頁面上的執行器和終端步驟不需要 claude.ai 角色，而在步驟檢查管理 UI 中的狀態時，執行器自己的日誌行會給您相同的信號。
- 您的組織的 [GitHub 連接](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)，以便開發人員在啟動工作階段時可以選擇存放庫。

### 主機和網路

執行器主機需要：

- 具有到 `api.anthropic.com` 的出站 HTTPS、到 `claude.ai` 和下面安裝步驟重定向到的下載主機，以及到您的 git 主機以進行複製的 Linux 或 macOS 主機或容器；[網路需求表](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#network-requirements)有完整清單。Windows 不支援作為執行器主機；改為在 Linux 容器中執行執行器。開發人員工作站不受影響，因為工作階段從瀏覽器中的 claude.ai 啟動。
- 與實時同步的時鐘，例如使用 NTP。當時鐘偏差超過五分鐘時，驗證失敗；請參閱[疑難排解](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#troubleshooting)。

### 執行器主機上的軟體

在啟動之前在主機上安裝：

- **Claude Code v2.1.224 或更新版本** ，使用任何[標準安裝方法](https://code.claude.com/docs/zh-TW/setup)。執行器是標準 `claude` 二進位檔的一部分，較早版本無法識別 `self-hosted-runner` 子命令。原生安裝程式的預設 `latest` 頻道在發佈後立即提供每個版本；`stable` 頻道、Homebrew `claude-code` cask 和穩定 apt、dnf 和 apk 存放庫延遲約一週。若要固定您的艦隊執行的確切版本，請參閱[安裝特定版本](https://code.claude.com/docs/zh-TW/setup#install-a-specific-version)。對於容器映像，請參閱[部署到生產環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#build-the-runner-image)中的 Dockerfile。
- **Git 2.24 或更新版本** 。部署頁面上的某些 git 選項需要較新的版本；[設定 git](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git)說明每個下限。

確認主機已準備好：

```
claude self-hosted-runner --help

```

準備好的主機會列印執行器的使用文字，列出 `--environment-secret-file` 等旗標。在 2.1.224 之前的版本上，該命令會改為列印一般 `claude --help` 輸出；使用 `claude update` 升級或從 `latest` 頻道重新安裝。

## 設定環境和執行器

Claude Code 包含引導式設定：一個互動式 Claude Code 工作階段，引導您在管理 UI 中建立環境、使用您保存的密鑰檔案啟動本機執行器、確認執行器註冊，並將速查表寫入 `./runner-setup/CHEAT-SHEET.md`。在您已使用持有擁有者角色的帳戶使用 `claude auth login` 登入的機器上執行它；它不適用於 API 金鑰或第三方模型提供者。在無法進行互動式工作階段的主機上，改為使用下面的手動步驟。首先確認[版本檢查](https://code.claude.com/docs/zh-TW/self-hosted-environments-quickstart#software-on-the-runner-host)已通過：在 2.1.224 之前的版本上，此命令會啟動一個普通的 Claude 工作階段，將這些詞作為提示，而不是引導式設定。若要啟動引導式設定，請執行設定子命令並按照提示進行：

```
claude self-hosted-runner setup

```

若要改為手動設定： 1 建立環境 前往管理設定中的[**雲端環境** 頁面](https://claude.ai/admin-settings/cloud-environments)。在**自託管環境** 下，選擇**新增** ，命名環境，然後選擇**建立** 。在精靈的第二步，選擇**複製環境金鑰** 以複製環境密鑰，管理 UI 將其標記為環境金鑰。claude.ai 只顯示一次密鑰，您之後無法檢索它；它在建立後 365 天過期。環境的 `ccpool_...` ID 在其詳細對話方塊中保持可見；您需要它用於[令牌驗證](https://code.claude.com/docs/zh-TW/self-hosted-environments-identity)中的 `aud` 檢查，以及用於從 CI [分派測試工作階段](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing#run-the-test-loop)。如果您遺失密鑰或需要輪換它，請從環境的**設定** 標籤建立新密鑰，將新密鑰推出到您的執行器，然後撤銷舊密鑰。持有已撤銷密鑰的執行器在下一次驗證輪詢時失敗並退出，記錄 `poll auth failed`，您的編排器使用新密鑰重新啟動它們。 2 啟動執行器 建立密鑰目錄。此步驟和下一步需要 root 用於 `/etc/claude` 路徑；執行器程序可以讀取的任何路徑都有效，因此如果您使用不同的路徑，請一起調整兩個命令和 `--environment-secret-file` 值。

```
mkdir -p /etc/claude

```

將環境密鑰寫入檔案。下面的命令從您的終端讀取，以便密鑰保持在 shell 歷史記錄之外：貼上您複製的值，按 Enter，然後按 Ctrl-D，子 shell 的 `umask` 使檔案只能由其擁有者讀取。

```
(umask 077 && cat > /etc/claude/environment-secret)

```

選擇基本目錄，將下面執行器命令中的 `<writable-dir>` 替換為執行器可以寫入或建立的絕對路徑。執行器在啟動時建立目錄，然後簽出存放庫並在其下建立每個工作階段的目錄。沒有 `--base-dir`，它使用 `/workspace`，這只在該目錄已存在且可寫或您以 root 身份啟動執行器時有效。如果執行器無法建立或寫入路徑，它在啟動時會以命名目錄的錯誤退出，而不是註冊。請參閱[疑難排解](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#troubleshooting)。然後使用 `--environment-secret-file` 和 `--base-dir` 啟動執行器。執行器向您的環境註冊並開始輪詢工作。如果執行器退出，請手動重新啟動它。生產部署在編排器下執行執行器，該編排器重新啟動已退出的執行器，通常每次重新啟動時使用新的檔案系統；[重複使用預先準備的簽出](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#reuse-a-pre-warmed-checkout)涵蓋支援的持久磁碟設定。

```
claude self-hosted-runner --environment-secret-file '/etc/claude/environment-secret' --base-dir '<writable-dir>'

```

3 驗證執行器出現 返回[**雲端環境** 頁面](https://claude.ai/admin-settings/cloud-environments)。您的環境狀態在執行器啟動後幾秒內從**未部署執行器** 變更為**健康** ；開啟環境並選擇**活動** 以查看執行器本身。 4 將工作階段路由到環境 在 claude.ai/code 啟動工作階段，並從環境選擇器中選擇您的環境，其中自託管環境與 Anthropic 託管的環境並排出現。執行器使用主機已有的任何 git 認證進行複製，因此選擇此主機已可以複製的存放庫，或公開存放庫；生產中私有存放庫的認證選項在[設定 git](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#configure-git)。下一個可用的執行器會拾取佇列中的工作階段，並記錄 `Picked up session <session-id>` 以及其活動計數和容量，因此您可以從執行器自己的輸出確認哪個主機接收了工作階段。在 [claude.ai/code](https://claude.ai/code) 觀看工作階段工作並閱讀 Claude 的回覆。如果工作階段保持佇列狀態，請參閱[疑難排解](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy#troubleshooting)。 執行器在其活動工作階段完成後按設計退出；請參閱[執行器生命週期](https://code.claude.com/docs/zh-TW/self-hosted-environments#runner-lifecycle)。對於生產環境，在編排器下部署它，該編排器在退出時重新啟動它。請參閱[部署到生產環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy)。

## 傳送後續訊息到執行中的工作階段

一旦工作階段在您的環境上執行，從任何您使用 `claude auth login` 登入的機器上的 `claude` CLI 傳送後續訊息；該命令不需要從啟動工作階段的機器執行。該命令發佈一條訊息：

```
claude -p "your message" --cloud <session-id>

```

對於 `<session-id>`，傳遞裸 `session_...` 或 `cse_...` ID 或工作階段的 claude.ai/code URL。成功傳送會列印 `Sent to cloud session.` 以及工作階段 ID 和檢視連結。接受的 ID 形式、JSON 輸出、帳戶和原則需求，以及錯誤參考在[從 CLI 傳送後續訊息](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#send-follow-ups-from-the-cli)上，因為該命令對 Anthropic 託管的工作階段的工作方式相同。

## 接下來的步驟

- [部署到生產環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-deploy)：強化部署、控制出口、設定 git 認證，並在 Kubernetes 或 Compose 下執行艦隊
- [自訂工作階段](https://code.claude.com/docs/zh-TW/self-hosted-environments-configuration)：包裝器指令碼、生命週期掛鉤、隨需執行器、MCP 伺服器和權限
- [端到端測試](https://code.claude.com/docs/zh-TW/self-hosted-environments-testing)：一個 CI 煙霧測試，分派工作階段並讀取 Claude 的回覆

是否 助手
