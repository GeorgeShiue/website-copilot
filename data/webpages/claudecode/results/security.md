## 我們如何處理安全性

### 安全基礎

您的程式碼安全至關重要。Claude Code 以安全為核心進行構建，按照 Anthropic 的全面安全計畫開發。在 [Anthropic Trust Center](https://trust.anthropic.com) 了解更多資訊並存取資源（SOC 2 Type 2 報告、ISO 27001 證書等）。

### 基於權限的架構

在手動模式中，Claude Code 以唯讀權限開始。當 Claude Code 需要編輯檔案、執行測試或執行命令時，它會先詢問您，您可以選擇批准該操作一次或從此允許該操作。 在手動模式中，Claude Code 也會在執行可以修改您系統的 Bash 命令前詢問。它執行內建的一組[唯讀命令](https://code.claude.com/docs/zh-TW/permissions#read-only-commands)（例如 `ls`、`cat` 和 `git status`）無需詢問。您和您的組織可以直接配置這些權限。 在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)中，一個單獨的分類器模型會審查操作而不是您，並阻止它判斷為不安全的操作。[分類器如何評估操作](https://code.claude.com/docs/zh-TW/permission-modes#how-the-classifier-evaluates-actions)列出了 Claude Code 直接批准的操作、它發送給分類器的操作，以及 Claude Code 仍然詢問您的操作。您明確設定的 ask 和 deny 規則仍然適用，您的組織可以[關閉自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)。 工作階段開始時使用的權限模式取決於您的計畫、您啟動它的介面，以及您的設定和您的組織的設定；請參閱[權限模式](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)。 有關詳細的權限配置，請參閱 [Permissions](https://code.claude.com/docs/zh-TW/permissions)。

### 內建保護

為了降低代理系統中的風險：

- **沙箱化 bash 工具** ：[Sandbox](https://code.claude.com/docs/zh-TW/sandboxing) bash 命令具有檔案系統和網路隔離，減少權限提示同時保持安全性。使用 `/sandbox` 進行配置以定義 Claude Code 可以自主工作的邊界
- **工作目錄邊界** ：在手動模式中，Claude Code 只能寫入啟動它的資料夾及其子資料夾，無法在沒有明確權限的情況下修改父目錄中的檔案。在手動模式中，Claude Code 也會在使用 Read、Grep 和 Glob 工具讀取此邊界外的路徑前詢問您。使用[額外目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories)擴展邊界以跳過提示，或使用 [sandbox `denyRead` 規則](https://code.claude.com/docs/zh-TW/sandboxing#filesystem-isolation)限制唯讀 Bash 命令可用的更廣泛讀取存取（這些規則僅在啟用沙箱化時適用）
- **提示疲勞緩解** ：支援按使用者、按程式碼庫或按組織允許列表常用的安全命令
- **Accept Edits 模式** ：自動批准檔案編輯和一組固定的檔案系統 Bash 命令，如 `mkdir`、`touch`、`rm`、`mv`、`cp` 和 `sed`，適用於工作目錄中的路徑。其他 Bash 命令和超出範圍的路徑仍會提示

### 使用者責任

Claude Code 只擁有您授予它的權限。您負責在批准前審查建議的程式碼和命令的安全性。

## 防止提示注入

提示注入是一種技術，攻擊者試圖通過插入惡意文本來覆蓋或操縱 AI 助手的指令。Claude Code 包括針對這些攻擊的多項防護措施：

### 核心保護

- **權限系統** ：在手動模式中，敏感操作需要明確批准
- **上下文感知分析** ：通過分析完整請求來檢測潛在有害的指令
- **輸入淨化** ：通過處理使用者輸入來防止命令注入
- **網路命令批准** ：從網路獲取內容的命令，例如 `curl` 和 `wget`，預設不會自動批准。在手動模式中，它們會像任何其他非唯讀 Bash 命令一樣提示，因此您仍然可以批准一次或添加明確的允許規則，例如 `Bash(curl *)`。若要停止 Claude 執行它們，請將它們添加到 [`permissions.deny`](https://code.claude.com/docs/zh-TW/permissions#tool-specific-permission-rules)。拒絕規則會匹配[如所寫的](https://code.claude.com/docs/zh-TW/permissions#bash-rule-limits)命令；對於不依賴於命令文本的網路強制執行，請參閱[沙箱網路隔離](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)

### 隱私保護

我們實施了多項保護措施來保護您的資料，包括：

- 敏感資訊的有限保留期（請參閱 [Privacy Center](https://privacy.anthropic.com/en/articles/10023548-how-long-do-you-store-my-data) 了解更多）
- 對使用者會話資料的受限存取
- 使用者對資料訓練偏好的控制。消費者使用者可以隨時更改其 [privacy settings](https://claude.ai/settings/privacy)。

有關完整詳情，請查閱我們的 [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms)（適用於 Team、Enterprise 和 API 使用者）或 [Consumer Terms](https://www.anthropic.com/legal/consumer-terms)（適用於 Free、Pro 和 Max 使用者）以及 [Privacy Policy](https://www.anthropic.com/legal/privacy)。

### 額外保護措施

- **網路請求批准** ：在手動模式中，進行網路請求的大多數工具預設需要使用者批准
- **隔離的上下文視窗** ：Web fetch 使用單獨的上下文視窗以避免注入潛在的惡意提示
- **信任驗證** ：首次程式碼庫執行和新的 MCP servers 需要信任驗證
  - 注意：使用 `-p` 旗標以非互動方式執行時，信任驗證被禁用
  - 注意：當您直接在主目錄中啟動 Claude Code 時，信任接受僅在當前會話期間保持，不會寫入磁碟，因此提示在每次啟動時都會重新出現。沒有設定可以持久化它。改為從專案子目錄啟動 Claude Code，其中信任接受按目錄保存
- **命令注入檢測** ：在手動模式中，即使之前已允許列表，可疑的 bash 命令也需要手動批准
- **故障關閉匹配** ：在手動模式中，不匹配的命令預設需要批准
- **自然語言描述** ：複雜的 bash 命令包括使用者理解的說明
- **安全的認證儲存** ：API 金鑰和令牌儲存在可用時的 macOS Keychain 中，並在 Windows 和 Linux 上受檔案權限保護。請參閱 [Credential Management](https://code.claude.com/docs/zh-TW/authentication#credential-management)

**Windows WebDAV 安全風險** ：在 Windows 上執行 Claude Code 時，我們建議不要啟用 WebDAV 或允許 Claude Code 存取可能包含 WebDAV 子目錄的路徑，如 `\\*`。[WebDAV 已被 Microsoft 棄用](<https://learn.microsoft.com/en-us/windows/whats-new/deprecated-features#:~:text=The%20Webclient%20(WebDAV)%20service%20is%20deprecated>)，原因是安全風險。啟用 WebDAV 可能允許 Claude Code 觸發對遠端主機的網路請求，繞過權限系統。 **使用不受信任內容的最佳實踐** ：

1. 在批准前審查建議的命令
1. 避免直接將不受信任的內容傳送給 Claude
1. 驗證對關鍵檔案的建議更改
1. 使用虛擬機器 (VM) 執行指令碼和進行工具呼叫，特別是在與外部網路服務互動時
1. 使用 `/feedback` 報告可疑行為

雖然這些保護措施大大降低了風險，但沒有任何系統完全免疫所有攻擊。在使用任何 AI 工具時，始終保持良好的安全實踐。

## MCP 安全性

Claude Code 允許使用者配置 Model Context Protocol (MCP) servers。允許的 MCP servers 列表在您的原始程式碼中配置，作為 Claude Code 設定的一部分，工程師將其簽入原始碼控制。 我們鼓勵編寫您自己的 MCP servers 或使用來自您信任的提供者的 MCP servers。您能夠為 MCP servers 配置 Claude Code 權限。Anthropic 在將連接器新增至 [Anthropic Directory](https://claude.ai/directory) 之前，會根據其 [列表標準](https://claude.com/docs/connectors/building/review-criteria) 審查連接器，但不會對任何 MCP server 進行安全審計或管理。

## IDE 安全性

有關在 IDE 中執行 Claude Code 的更多資訊，請參閱 [VS Code security and privacy](https://code.claude.com/docs/zh-TW/vs-code#security-and-privacy)。

## 雲端執行安全性

使用 [雲端會話](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 時，會實施額外的安全控制。您的組織路由到 [自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) 的會話在您自己的基礎設施上執行，其中隔離、網路出口和 git 認證是您部署的責任。在 Anthropic 託管的環境中：

- **隔離的虛擬機器** ：每個雲端會話在隔離的、由 Anthropic 管理的 VM 中執行
- **網路存取控制** ：網路存取預設受限，可以配置為禁用或僅允許特定網域
- **認證保護** ：身份驗證通過安全代理進行處理，該代理在沙箱內使用範圍限定的認證，然後轉換為您的實際 GitHub 身份驗證令牌
- **分支限制** ：Git push 操作限制在目前工作分支
- **審計日誌** ：雲端會話中的所有操作都被記錄以用於合規和審計目的
- **自動清理** ：會話 VM 在一段時間無活動後會被回收

有關雲端執行的更多詳情，請參閱 [在雲端使用 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)；若要為雲端會話配置網路存取，請參閱 [設定雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)。 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 會話的工作方式不同：網路介面連接到在您本地機器上執行的 Claude Code 程序。所有程式碼執行和檔案存取保持本地，會話流量通過 TLS 上的 Anthropic API 傳輸；連接時，會話文字記錄會儲存在 Anthropic 伺服器上以跨裝置同步對話，如 [Connection and security](https://code.claude.com/docs/zh-TW/remote-control#connection-and-security) 中所述。不涉及雲端 VM 或沙箱化。連接使用多個短期、範圍狹窄的認證，每個認證限制於特定目的並獨立過期，以限制任何單一洩露認證的影響範圍。

## 安全最佳實踐

### 使用敏感程式碼

- 在批准前審查所有建議的更改
- 為敏感儲存庫使用專案特定的權限設定
- 考慮使用 [dev containers](https://code.claude.com/docs/zh-TW/devcontainer) 以獲得額外隔離
- 使用 `/permissions` 定期審計您的權限設定

### 團隊安全性

- 使用 [managed settings](https://code.claude.com/docs/zh-TW/settings#where-settings-live) 強制執行組織標準
- 通過版本控制共享已批准的權限配置
- 培訓團隊成員了解安全最佳實踐
- 通過 [OpenTelemetry metrics](https://code.claude.com/docs/zh-TW/monitoring-usage) 監控 Claude Code 使用情況
- 使用 [`ConfigChange` hooks](https://code.claude.com/docs/zh-TW/hooks#configchange) 審計或阻止會話期間的設定更改

### 報告安全問題

如果您在 Claude Code 中發現安全漏洞：

1. 不要公開披露
1. 通過我們的 [HackerOne program](https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new) 報告
1. 包括詳細的重現步驟
1. 在公開披露前留出時間讓我們解決問題

## 相關資源

- [Security guidance plugin](https://code.claude.com/docs/zh-TW/security-guidance)：讓 Claude 在會話期間審查並修復其自身程式碼變更中的漏洞
- [`/security-review`](https://code.claude.com/docs/zh-TW/commands#all-commands)：對您目前分支上的變更執行隨選安全檢查
- [Sandbox environments](https://code.claude.com/docs/zh-TW/sandbox-environments)：比較隔離方法並為您的威脅模型選擇一個
- [Sandboxing](https://code.claude.com/docs/zh-TW/sandboxing)：Bash 命令的檔案系統和網路隔離
- [Permissions](https://code.claude.com/docs/zh-TW/permissions)：配置權限和存取控制
- [Monitoring usage](https://code.claude.com/docs/zh-TW/monitoring-usage)：追蹤和審計 Claude Code 活動
- [Development containers](https://code.claude.com/docs/zh-TW/devcontainer)：安全、隔離的環境
- [Anthropic Trust Center](https://trust.anthropic.com)：安全認證和合規性
- [CISO’s guide to agentic AI](https://claude.com/blog/ciso-guide-to-agentic-ai)：安全領導者評估代理式 AI 部署的框架

是否 助手
