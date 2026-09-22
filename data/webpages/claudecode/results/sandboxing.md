Bash 沙箱讓 Claude 執行大多數 shell 命令，而無需停下來請求權限。與其批准每個命令，您可以定義命令可以接觸哪些檔案和網路域，作業系統會為每個 Bash、PowerShell 或 Monitor 命令及其子流程強制執行該邊界。 若要比較其他隔離方法，例如開發容器、自訂容器和虛擬機，請參閱 [Sandbox environments](https://code.claude.com/docs/zh-TW/sandbox-environments)。若要減少 Bash 以外工具的權限提示，請參閱 [permission modes](https://code.claude.com/docs/zh-TW/permission-modes)。

## 開始使用

沙箱內建於 Claude Code 中，在 macOS、Linux 和 WSL2 上執行。不支援原生 Windows。在 Windows 上，在 WSL2 發行版內執行 Claude Code。 在 macOS 上，無需安裝任何內容：沙箱化使用內建的 Seatbelt 框架。在 Linux 和 WSL2 上，沙箱依賴於兩個套件，詳見 [Set up Linux and WSL2](https://code.claude.com/docs/zh-TW/sandboxing#set-up-linux-and-wsl2)。即使您還沒有安裝它們，您也可以從 `/sandbox` 開始，因為其面板會顯示是否缺少任何內容。 1 執行 /sandbox 啟動 Claude Code 工作階段並執行 `/sandbox` 命令：

```
/sandbox

```

這會開啟沙箱面板，有三個標籤，以及當可選的 seccomp 過濾器缺失時 Linux 上的 Dependencies 標籤：

- **Mode** ：選擇沙箱化命令的批准方式，詳見下一步
- **Overrides** ：選擇在沙箱下失敗的命令是否可以回退到執行未沙箱化。這是 [`allowUnsandboxedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-allowunsandboxedcommands) 設定
- **Config** ：檢視已解析的沙箱設定

如果面板只顯示 Dependencies 標籤，則缺少必需的套件。按照 [Set up Linux and WSL2](https://code.claude.com/docs/zh-TW/sandboxing#set-up-linux-and-wsl2) 中的說明安裝它，重新啟動 Claude Code，然後再次執行 `/sandbox`。 2 選擇一個模式 在 Mode 標籤上，選擇自動允許或常規權限。自動允許在不提示的情況下執行沙箱化命令，常規權限即使命令沙箱化也保持常規權限提示。請參閱 [Sandbox modes](https://code.claude.com/docs/zh-TW/sandboxing#sandbox-modes) 了解在自動允許模式中仍然提示的命令。 3 執行 Bash 命令 要求 Claude 執行命令，例如構建或測試套件。預設情況下，沙箱內的命令可以寫入工作目錄、工作階段暫存目錄，以及任何您使用 `--add-dir`、`/add-dir` 或 `permissions.additionalDirectories` [新增的目錄](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration)。命令首次需要新的網路域時，Claude Code 會提示批准；在 [auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 中，Claude 改為在命令本身上命名該命令需要的主機 [on the command itself](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode)，供分類器與其一起檢查。無法沙箱化執行的命令會回退到常規權限流程。Claude Code 將其權限提示標題為「Bash command (unsandboxed)」而不是「Bash command」，因此您可以判斷哪些命令在沙箱外執行。若要擴大或縮小沙箱允許的內容，請參閱 [Configure sandboxing](https://code.claude.com/docs/zh-TW/sandboxing#configure-sandboxing)。如果沙箱化命令在容器內因 `Operation not permitted` 失敗，請參閱 [Troubleshooting](https://code.claude.com/docs/zh-TW/sandboxing#troubleshooting) 下的 Bubblewrap 項目。 在面板中選擇模式時，Claude Code 會將其儲存到您專案的本地設定 `.claude/settings.local.json`，這適用於目前專案。Claude Code 在那裡儲存設定時會將該檔案新增到您的全域 gitignore。若要在所有專案中啟用沙箱，請在 `~/.claude/settings.json` 的使用者設定中將 [`sandbox.enabled`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-enabled) 設定為 `true`。若要為組織中的每個開發人員強制執行沙箱化，請使用 [managed settings](https://code.claude.com/docs/zh-TW/sandboxing#enforce-sandboxing-with-managed-settings)。 若要在一個工作階段中變更沙箱而不寫入設定檔，請使用 [`--settings`](https://code.claude.com/docs/zh-TW/settings#change-a-setting-for-one-session) 啟動 Claude Code。例如，此命令啟動一個沙箱化工作階段，其中 Claude 無法在沙箱外重試被阻止的命令：

```
claude --settings '{"sandbox": {"enabled": true, "allowUnsandboxedCommands": false}}'

```

預設情況下，如果沙箱因缺少依賴項或不支援的平台而無法啟動，Claude Code 會顯示警告並在沒有沙箱化的情況下執行命令。若要改為將其設為硬失敗，請將 [`sandbox.failIfUnavailable`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-failifunavailable) 設定為 `true`。這適用於需要沙箱化作為安全閘道的受管部署。

### 設定 Linux 和 WSL2

在 Linux 和 WSL2 上，沙箱依賴於兩個套件：

- [`bubblewrap`](https://github.com/containers/bubblewrap)：無特權沙箱化工具，強制執行檔案系統隔離
- [`socat`](http://www.dest-unreach.org/socat/)：用於通過沙箱代理路由網路流量的中繼

使用您發行版的套件管理器安裝它們：

- Ubuntu/Debian
- Fedora

```
sudo apt-get install bubblewrap socat

```

```
sudo dnf install bubblewrap socat

```

當依賴項缺失時，`/sandbox` 中的 Dependencies 標籤會列出您的平台缺少 `ripgrep`、`bubblewrap`、`socat` 和 seccomp 過濾器中的哪些。如果在安裝並重新啟動 Claude Code 後沒有看到該標籤，則所有依賴項都已存在。 Ripgrep 與原生 Claude Code 二進位檔案一起打包。seccomp 過濾器是可選的，增加 Unix 域套接字阻止。如果缺少，請使用 `npm install -g @anthropic-ai/sandbox-runtime` 安裝它。 當缺少必需的依賴項時，Dependencies 標籤是唯一顯示的標籤，直到您安裝它。當只有可選的 seccomp 過濾器缺失時，Dependencies 標籤會與其他標籤一起出現。依賴項檢查在啟動時執行，因此在安裝套件後重新啟動 Claude Code，以便 `/sandbox` 檢測到它們。 Ubuntu 24.04 及更新版本：允許 bubblewrap 建立使用者命名空間 在 Ubuntu 24.04 及更新版本上，預設 AppArmor 策略防止 bubblewrap 建立隔離所需的使用者命名空間。若要檢查您的環境（包括 WSL2 內）是否強制執行此限制，請執行 `sysctl kernel.apparmor_restrict_unprivileged_userns`。如果命令傳回 `0`，請跳過此步驟。如果列印 `No such file or directory` 錯誤，金鑰不存在，您可以跳過此步驟。如果傳回 `1`，請新增授予 `bwrap` 此功能的 AppArmor 設定檔：

```
sudo tee /etc/apparmor.d/bwrap > /dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
EOF

```

該設定檔僅適用於 `bwrap` 本身，不適用於在沙箱內執行的命令。重新載入 AppArmor 以應用它：

```
sudo systemctl reload apparmor

```

WSL2 注意事項 使用 PowerShell 中的 `wsl -l -v` 檢查您的 WSL 版本。如果您看到 `Sandboxing requires WSL2`，您的發行版執行的是 WSL1。將其升級到 WSL2 或在沒有沙箱化的情況下執行 Claude Code。在 WSL2 上，WSL 將 Windows 二進位檔案（例如 `cmd.exe`、`powershell.exe` 或 `/mnt/c/` 下的任何內容）的啟動交給 Windows 主機，通過 Unix 套接字進行，因此沙箱化命令是否可以啟動一個取決於沙箱的 [Unix-socket settings](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowunixsockets)：可選的 seccomp 過濾器必須安裝才能首先阻止套接字。若要允許這些啟動，請設定 `allowAllUnixSockets`；若要將它們完全排除在沙箱外，請將命令新增到 [`excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands)。

### 沙箱模式

Claude Code 提供兩種沙箱模式。在兩種模式中，沙箱強制執行相同的檔案系統和網路限制；區別僅在於沙箱化命令是自動批准還是需要明確權限。

#### 自動允許模式

當命令可以沙箱化時，Claude Code 在沙箱內執行它並自動批准，無需詢問您的權限。無法沙箱化的命令（例如需要存取非允許主機的網路存取的命令）會回退到常規權限流程，其中 Claude Code 檢查您的 [permission rules](https://code.claude.com/docs/zh-TW/permissions) 並限制這些規則不允許的任何命令，在 Manual 模式中提示。 即使在自動允許模式中，以下仍然適用：

- 明確的 [deny rules](https://code.claude.com/docs/zh-TW/permissions) 始終被尊重
- 針對 [critical path](https://code.claude.com/docs/zh-TW/permission-modes#critical-paths) 的 `rm` 或 `rmdir` 命令仍然會通過常規權限流程
- 內容範圍的 [ask rules](https://code.claude.com/docs/zh-TW/permissions)（例如 `Bash(git push *)`）仍然會強制提示，即使是沙箱化命令
- 裸 `Bash` ask 規則，或等效的 `Bash(*)` 形式，對於執行沙箱化的命令會被跳過；它仍然適用於回退到常規權限流程的命令。在 [plan mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 中，規則不會被跳過：它對沙箱化命令也會提示，包括唯讀命令。在 v2.1.212 之前，跳過也適用於 plan mode

自動允許模式獨立於您的權限模式設定工作，但有一個例外：[plan mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 和在 auto mode 中，針對帶有 [per-command allowed domains](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode) 的命令。即使您不在「接受編輯」模式中，當啟用自動允許時，沙箱化 Bash 命令也會自動執行。這意味著在沙箱邊界內修改檔案的 Bash 命令將執行而不提示，即使在 Manual 模式中，檔案編輯工具會提示。在 plan mode 中，自動允許不會擴大批准；請參閱 [plan mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 了解 Claude Code 在您計劃時如何限制命令。在 v2.1.212 之前，自動允許在 plan mode 中也無需提示執行沙箱化命令。

#### 常規權限模式

所有 Bash 命令都通過常規權限流程進行，即使沙箱化也是如此。這提供了更多控制，但需要更多批准。

#### 未沙箱化重試逃生艙

某些命令根本無法在沙箱內執行，例如與其不相容的工具或需要您未允許的主機的工具。Claude Code 在被阻止命令的結果中報告沙箱違規，命名沙箱拒絕的路徑或主機，因此 Claude 看到沙箱阻止了什麼。與其讓任務失敗或要求您關閉沙箱化，Claude Code 包含一個逃生艙：Claude 分析違規，可能使用 `dangerouslyDisableSandbox` 參數重試命令。 重試的命令在沙箱外執行，因此通過常規權限流程進行。在 Manual 模式中您會獲得確認提示。在 [auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 中，分類器評估基礎命令。當 [`permissions.blockReadsOutsideWorkingDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-blockreadsoutsideworkingdirectories) 開啟時，需要批准才能在沙箱外執行的重試會提示您。若要在 auto mode 中即使在每次未沙箱化重試時也被提示，請新增 [ask rule](https://code.claude.com/docs/zh-TW/permissions#match-by-input-parameter) 用於 `Bash(dangerouslyDisableSandbox:true)`。 您可以通過在 [sandbox settings](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-settings) 中設定 `"allowUnsandboxedCommands": false` 來禁用此逃生艙。禁用逃生艙後，Claude Code 會忽略 `dangerouslyDisableSandbox` 參數，Claude 執行的每個命令都必須沙箱化執行，除非您已在 `excludedCommands` 中列出它。`/sandbox` **Overrides** 標籤將此設定顯示為 **Strict sandbox mode** 。 嚴格沙箱模式適用於 Claude 執行的命令。您在 [`!` shell-mode prompt](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix) 自己輸入的命令在沙箱外執行，除非工作階段是以下之一：

- **[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)** ：嚴格沙箱模式也涵蓋 shell-mode 命令
- **已設定[`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/zh-TW/env-vars#variables) 的 Linux 工作階段**：每個命令都沙箱化執行，包括 shell-mode 命令

在 v2.1.260 之前，嚴格沙箱模式在每個工作階段中沙箱化 shell-mode 命令。

#### 暫存目錄

工作階段暫存目錄在沙箱內預設可寫，與工作目錄一起。除非您 [disable filesystem isolation](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，Claude Code 為沙箱化命令設定 `$TMPDIR` 為此目錄，因此寫入暫存檔案的工具無需額外配置即可工作。未沙箱化命令繼承您的 shell 的 `$TMPDIR` 不變，因此當檔案系統隔離開啟時，沙箱化和未沙箱化命令將 `$TMPDIR` 解析為不同的目錄。若要在兩者之間傳遞暫存檔案，請改為在工作目錄下寫入它們。

## 設定沙箱化

通過您的 `settings.json` 檔案自訂沙箱行為。請參閱 [Settings](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-settings) 以了解完整的設定參考。 預設情況下，沙箱化命令可以寫入目前工作目錄、工作階段暫存目錄，以及任何[您已新增](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration)的目錄（使用 `--add-dir`、`/add-dir` 或 `permissions.additionalDirectories`）。如果子流程命令（如 `kubectl`、`terraform` 或 `npm`）需要寫入這些目錄外，請使用 `sandbox.filesystem.allowWrite` 授予對特定路徑的存取：

```
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "allowWrite": ["~/.kube", "/tmp/build"]
    }
  }
}

```

這些路徑在作業系統級別強制執行，因此在沙箱內執行的所有命令（包括其子流程）都尊重它們。當工具需要對特定位置的寫入存取時，這是推薦的方法，而不是使用 `excludedCommands` 將工具排除在沙箱外。 當在多個 [settings scopes](https://code.claude.com/docs/zh-TW/settings#settings-precedence) 中定義相同的檔案系統陣列時，Claude Code 會合併它們，組合來自每個範圍的路徑，而不是用另一個範圍的陣列替換一個範圍的陣列。 如果您在 CLI 上使用 [`--setting-sources`](https://code.claude.com/docs/zh-TW/cli-reference) 或在 Agent SDK 中使用 [`settingSources`](https://code.claude.com/docs/zh-TW/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources) 排除來源，Claude Code 會在建立沙箱設定時忽略其 `sandbox.filesystem` 項目、其 `Edit` 權限規則和其 `Read` 拒絕規則。需要 Claude Code v2.1.246 或更新版本。 當您在工作階段期間編輯這些檔案系統清單時，Claude Code [將變更套用到執行中的工作階段](https://code.claude.com/docs/zh-TW/settings#when-edits-take-effect)，因此下一個沙箱化命令在新路徑下執行。 路徑前綴控制路徑的解析方式：

| 前綴                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 含義                                                                                                                                                                                | 範例                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 從檔案系統根目錄的絕對路徑                                                                                                                                                          | `/tmp/build` 保持 `/tmp/build`                                         |
| `~/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 相對於主目錄                                                                                                                                                                        | `~/.kube` 變成 `$HOME/.kube`                                           |
| `./` 或無前綴                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 相對於專案設定的專案根目錄，或相對於 `~/.claude` 的使用者設定                                                                                                                       | `.claude/settings.json` 中的 `./output` 解析為 `<project-root>/output` |
| 此語法與 [Read and Edit permission rules](https://code.claude.com/docs/zh-TW/permissions#read-and-edit) 不同，後者使用 `//path` 表示絕對路徑，`/path` 表示專案相對路徑。沙箱檔案系統路徑使用標準慣例：`/tmp/build` 是絕對路徑。如需了解 Claude Code 如何處理這些路徑中的尾部斜線或萬用字元，請參閱 [Sandbox path prefixes](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)。 您也可以使用 `sandbox.filesystem.denyWrite` 和 `sandbox.filesystem.denyRead` 拒絕寫入或讀取存取，並使用 `sandbox.filesystem.allowRead` 重新允許被拒絕區域內的特定路徑。當讀取規則重疊時，更具體的路徑優先： |                                                                                                                                                                                     |                                                                        |
| 範例規則                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 結果                                                                                                                                                                                |                                                                        |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | ---                                                                                                                                                                                 |                                                                        |
| `"denyRead": ["~/"]` 搭配 `"allowRead": ["~/projects"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | `~/projects` 可讀，主目錄的其餘部分保持被阻止。較窄的允許重新開啟被拒絕區域的該部分                                                                                                 |                                                                        |
| `"allowRead": ["~/"]` 搭配 `"denyRead": ["~/.env"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `~/.env` 保持被阻止，主目錄的其餘部分可讀。精確的拒絕在更寬的允許內保持有效，因此廣泛的允許無法無聲地重新暴露機密                                                                   |                                                                        |
| `"allowRead": ["~/"]` 搭配 `"denyRead": ["~/**/.env"]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 主目錄下的每個 `.env` 保持被阻止，其餘部分可讀。[萬用字元拒絕](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)在更寬的允許內保持有效，就像精確路徑一樣 |                                                                        |
| 下面的範例阻止從整個主目錄讀取，同時仍允許從目前專案讀取。將其放在您的專案的 `.claude/settings.json` 中，因為相對路徑 `.` 僅在配置位於專案設定中時才解析為專案根目錄：                                                                                                                                                                                                                                                                                                                                                                                                                                                |                                                                                                                                                                                     |                                                                        |

```
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["."]
    }
  }
}

```

如果您將相同的配置放在 `~/.claude/settings.json` 中，`.` 將解析為 `~/.claude`，專案檔案將保持被 `denyRead` 規則阻止。 若要拒絕沙箱化命令讀取主目錄和掛載磁碟區的存取，同時保持工作目錄可讀，請改為設定 [`permissions.blockReadsOutsideWorkingDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-blockreadsoutsideworkingdirectories)，而不是編寫路徑規則。

### 停用檔案系統隔離

設定 `sandbox.filesystem.disabled` 為 `true` 以跳過檔案系統隔離，同時保持網路隔離。下面的範例關閉檔案系統隔離，同時保持網路網域的允許清單：

```
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "disabled": true
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}

```

沙箱有兩個獨立的層：[檔案系統隔離](https://code.claude.com/docs/zh-TW/sandboxing#filesystem-isolation)控制沙箱化命令可以讀取和寫入哪些路徑，[網路隔離](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)控制它們可以到達哪些網域。關閉檔案系統層後，沙箱化命令獲得對主機檔案系統的無限制讀取和寫入存取，同時其網路出站流量仍限制在您允許的網域。當您沙箱化以控制命令連接的位置而不是它們寫入的內容時，請關閉該層。 該設定預設為關閉，並適用於沙箱執行的平台：macOS、Linux 和 WSL2。需要 Claude Code v2.1.216 或更新版本。 關閉檔案系統隔離且命令自動允許時，沙箱化命令可以寫入稍後命令執行或讀取的檔案，例如 shell 啟動檔案、`$PATH` 上的可執行檔或 `~/.claude/settings.json`，並使用它們在下一次執行時擴大自己的存取。僅當您信任工作負載不會升級自己的存取時，才將 `filesystem.disabled` 設定為 `true`。使用 [`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/sandboxing#keep-developers-from-widening-the-policy) 鎖定網路網域會縮小風險，但不會消除它，因為該鎖定僅適用於在沙箱內執行的命令。

#### 哪些設定可以停用它

因為關閉檔案系統隔離會擴大沙箱化命令可以執行的操作，Claude Code 僅從這些設定來源尊重 `filesystem.disabled`：

- 使用者設定、受管設定和 `--settings` CLI 旗標可以設定它。`.claude/settings.json` 和 `.claude/settings.local.json` 中的專案設定不能，因此簽出的專案無法關閉檔案系統隔離。
- 當受管設定配置 `sandbox.filesystem` 時，或列出任何 `sandbox.credentials.files` 項目且 `"mode": "deny"` 時，僅受管設定可以設定該鍵。這保持管理員部署的檔案系統限制有效；若要放鬆此類部署，請在受管設定中設定 `"disabled": true`。
- 當設定 [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/zh-TW/env-vars) 時，Claude Code 會忽略來自每個來源（包括受管設定）的 `filesystem.disabled`，並保持檔案系統隔離開啟。

受管 `credentials.files` 項目是否固定 `filesystem.disabled`（將鍵鎖定到受管設定，以便開發人員無法關閉檔案系統隔離）取決於項目的 `mode` 和沙箱啟動時項目發生的情況：

| 受管項目                                                                                                                                                                                   | 固定 `filesystem.disabled` | 隔離關閉時保護檔案的內容                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `"mode": "deny"`                                                                                                                                                                           | 是                         | 無：讀取區塊是檔案系統層的一部分                                                                                                              |
| `"mode": "mask"`，應用為遮罩                                                                                                                                                               | 否                         | 遮罩本身：Linux 和 WSL2 上的[哨兵複本和代理](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)，macOS 上沙箱自己的讀取規則 |
| `"mode": "mask"`，[在設定時回退到 `deny`](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)                                                                             | 否                         | 無，與 `deny` 相同。將無法遮罩的路徑（例如目錄）列為明確的 `deny` 項目，這會固定該鍵                                                          |
| `"mode": "mask"`，[由驗證降級為 `deny`](https://code.claude.com/docs/zh-TW/managed-settings#invalid-entries-in-managed-settings)                                                           | 是，如同明確的 `deny`      | 無，與 `deny` 相同                                                                                                                            |
| 回退發生在沙箱啟動時，在 Claude Code 已讀取設定之後，固定檢查執行，因此回退項目永遠不會固定。驗證在設定載入時將無效項目重寫為 `deny`，因此降級項目的固定方式與您編寫為 `deny` 的項目相同。 |                            |                                                                                                                                               |

#### 檔案系統隔離關閉時的變更

設定 `filesystem.disabled` 會解除檔案系統層本身強制執行的保護。其他層強制執行的保護繼續適用：

| 保護                                                                                                                              | 檔案系統隔離關閉時                                                                                                                                          |
| --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `filesystem.denyRead` 和 [`credentials.files`](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) `deny` 讀取區塊 | 未強制執行。檔案系統層應用兩者                                                                                                                              |
| `credentials.envVars` `deny` 和 `mask` 項目                                                                                       | 強制執行。環境變數清理獨立於檔案系統層                                                                                                                      |
| [`credentials.files` `mask` 項目](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)應用為遮罩                  | 強制執行：遮罩獨立於檔案系統層。[回退到 `deny`](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files) 的項目未強制執行，如同任何 `deny` 項目 |
| 另外兩件事會改變：                                                                                                                |                                                                                                                                                             |

- 沙箱化命令繼承您的 shell 的 `$TMPDIR` 而不是工作階段暫存目錄，因為每個暫存目錄都是可寫的，Claude Code 不再將命令重定向到工作階段目錄。 在 Linux 上，變數通常在父 shell 中未設定，因此它可以在沙箱化命令內展開為空；Claude Code 告訴 Claude 通過其 Bash 工具指導使用 `mktemp -d` 建立暫存目錄，而不是依賴 `$TMPDIR`。
- [`autoAllowBashIfSandboxed`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-autoallowbashifsandboxed) 仍預設為 `true`，因此沙箱化命令繼續執行而不提示。設定為 `false` 以提示沙箱化命令。

### 保護認證

`sandbox.credentials` 設定宣告要保護、不讓沙箱化命令存取的認證檔案和環境變數。每個項目命名一個檔案路徑或環境變數和一個 `mode`。專用的 `credentials` 區塊將認證規則分組在一起，並與一般檔案系統規則分開。需要 Claude Code v2.1.187 或更新版本。 對於 `"mode": "deny"` 的項目，檔案路徑在沙箱內被拒絕讀取，與 `filesystem.denyRead` 應用的限制相同，環境變數在每個沙箱化命令執行前被取消設定。檔案保護是檔案系統層的一部分，因此如果您[停用檔案系統隔離](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，它不適用；環境變數保護仍然適用。 下面的範例阻止讀取 AWS 認證檔案和 SSH 目錄，並從沙箱化命令的環境中移除 `GITHUB_TOKEN` 和 `NPM_TOKEN`：

```
{
  "sandbox": {
    "enabled": true,
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.ssh", "mode": "deny" }
      ],
      "envVars": [
        { "name": "GITHUB_TOKEN", "mode": "deny" },
        { "name": "NPM_TOKEN", "mode": "deny" }
      ]
    }
  }
}

```

環境變數項目和檔案項目也接受 `"mode": "mask"`，如下所述 [Mask credentials](https://code.claude.com/docs/zh-TW/sandboxing#mask-credentials)。 檔案路徑遵循與 `sandbox.filesystem.*` 設定相同的 [prefix rules](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)。 Claude Code 合併來自工作階段載入的每個 [settings scope](https://code.claude.com/docs/zh-TW/settings#settings-precedence) 的 `deny` 項目。`deny` 項目只會縮小存取，因此任何範圍都可以新增一個，但沒有任何範圍可以移除另一個範圍新增的項目。 當您[排除設定來源](https://code.claude.com/docs/zh-TW/sandboxing#configure-sandboxing)時：

- **專案或本機設定** ：Claude Code 不應用其任何 `credentials` 項目。需要 Claude Code v2.1.246 或更新版本。
- **使用者設定** ：Claude Code 仍應用 `~/.claude/settings.json` 中的 `deny` 項目，並保持其[檔案 `mask` 項目](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)作為限制，但放棄其[環境變數 `mask` 項目](https://code.claude.com/docs/zh-TW/sandboxing#mask-environment-variables)。

沒有內建的認證拒絕清單，因此只有您列出的檔案和變數被限制。 `sandbox.credentials` 僅影響沙箱化 Bash 命令。若要從所有子流程中移除認證，無論沙箱化如何，請設定 [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/zh-TW/env-vars)。

### 遮罩認證

遮罩比 [Protect credentials](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) 下的 `deny` 項目更進一步。Claude Code 不是阻止認證，而是向沙箱化命令顯示佔位符（哨兵），[沙箱代理](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)在出站請求到您允許的主機時交換真實值。對於檔案，替換是 Linux 和 WSL2 行為；[macOS 改為阻止檔案](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)。

#### 遮罩環境變數

`"mode": "mask"` 保護認證同時保持使用它進行身份驗證的工具正常工作。`deny` 完全移除變數，這也會破壞需要它的工具，例如 `gh` 或 `npm`。需要 Claude Code v2.1.199 或更新版本。 使用 `mask`，沙箱化命令看到的是每個工作階段的哨兵值而不是真實值。每個 `mask` 項目可以列出 `injectHosts`，真實值被允許到達的主機。當請求離開沙箱前往其中之一時，[沙箱代理](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)將哨兵替換為真實值。命令和它記錄的任何內容都不會持有真實認證，但其請求仍然進行身份驗證。 代理在請求內容中替換認證，因此它必須看到它們。設定 [`network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate) 以便代理自己終止 TLS。 沒有它，遮罩會失敗而不暴露任何內容：命令仍然只看到哨兵值，但哨兵值不變地到達伺服器，身份驗證失敗。Claude Code 在啟動時報告此配置錯誤。 替換涵蓋標頭和請求主體。使用從認證衍生的簽名進行身份驗證的請求，而不是認證本身，需要在代理處重新簽名；[Re-sign AWS requests](https://code.claude.com/docs/zh-TW/sandboxing#re-sign-aws-requests) 涵蓋 AWS 如何工作。 代理僅在 [domain allowlist](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation) 允許的連接上注入，因此每個 `injectHosts` 目的地也必須通過 `network.allowedDomains` 可達。 下面的範例遮罩兩個令牌。`GH_TOKEN` 僅在對 `api.github.com` 的請求上被替換，而 `NPM_TOKEN` 沒有 `injectHosts` 並在對 `network.allowedDomains` 中每個主機的請求上被替換。

```
{
  "sandbox": {
    "enabled": true,
    "network": {
      "tlsTerminate": {},
      "allowedDomains": ["*.github.com", "registry.npmjs.org"]
    },
    "credentials": {
      "envVars": [
        { "name": "GH_TOKEN", "mode": "mask", "injectHosts": ["api.github.com"] },
        { "name": "NPM_TOKEN", "mode": "mask" }
      ]
    }
  }
}

```

在兩個清單中以不同方式拼寫 IPv6 目的地，因為每個清單都有自己的匹配器：

- **`network.allowedDomains`**：[括號形式網域清單使用](https://code.claude.com/docs/zh-TW/sandboxing#ipv6-addresses-in-domain-lists)，例如 `"[::1]"`。代理檢查此清單以允許連接。
- **`injectHosts`**：其規範壓縮形式中的裸地址，例如`"::1"` 或 `"2001:db8::1"`。代理將每個項目與連接的裸目的地地址進行匹配，忽略連接埠，因此括號、區域 ID 或不同壓縮拼寫永遠不會匹配，代理永遠不會在那裡注入認證。

`claude doctor` 標記 `injectHosts` 項目，這些項目永遠無法與警告 `Sandbox credential injectHosts entries can never match their destination` 匹配。此檢查需要 Claude Code v2.1.229 或更新版本。 與 `deny` 不同，遮罩授權代理將您的真實認證發送到列出的主機，因此 Claude Code 僅從您或您的管理員控制的設定中尊重它：使用者設定、受管設定和 `--settings` CLI 旗標。Claude Code 忽略儲存庫的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的 `mask` 項目。在這些檔案中，它也忽略 `network.tlsTerminate` 和 [`credentials.allowPlaintextInject`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-allowplaintextinject)，允許代理將認證注入未加密請求的設定。如果您[排除使用者設定](https://code.claude.com/docs/zh-TW/sandboxing#configure-sandboxing)，Claude Code 也會放棄 `~/.claude/settings.json` 中的環境變數 `mask` 項目。 當您的管理員通過伺服器受管設定傳遞 `mask` 項目、`network.tlsTerminate` 或 `credentials.allowPlaintextInject` 時，它們計為[需要批准的設定](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)。 當相同的變數在任何範圍中以 `deny` 列出時，`deny` 優先。 遮罩預設替換變數的整個值，適合裸令牌。可選項目欄位（需要 Claude Code v2.1.224 或更新版本）處理具有結構的值：

- `extract`：Claude Code 在整個值上應用的正規表達式，僅替換每個匹配的第 1 組捕獲的文字，因此解析值的工具（例如 `DATABASE_URL` 連接字串）在沙箱內仍然有效。模式必須包含至少一個捕獲組。
- `onExtractNoMatch` 控制模式匹配無內容時發生的情況：
  - `warn`（預設）警告並無遮罩地傳遞變數
  - `deny` 在沙箱內取消設定變數
  - `error` 停止沙箱設定，直到您修復配置
- `decode: "jwt"`：用於保存 JSON Web Token (JWT) 的變數。Claude Code 驗證值是 JWT 並將其替換為結構上有效的假令牌，因此沙箱內解碼令牌的程式碼繼續工作。新增 `maskClaims` 以列出要個別遮罩的頂級承載聲明，而不是替換整個令牌；其他聲明保持可讀。當值未驗證為 JWT 或沒有列出的聲明匹配時，Claude Code 無遮罩地傳遞變數並發出警告。`decode` 無法與 `extract` 結合。

請參閱[設定參考中的 `credentials.envVars[]` 列](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-settings)以了解完整欄位清單。

#### 重新簽署 AWS 請求

AWS 請求在請求內容上攜帶 SigV4 簽名，因此一起遮罩 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY`。代理通過存取鍵的哨兵檢測 SigV4 請求，並在替換真實值後重新簽署它。僅遮罩機密會留下用佔位符簽署的請求，代理無法檢測，因此它們在 AWS 處失敗；Claude Code 在啟動時警告此情況，但在僅遮罩存取鍵 ID 時不警告。代理無法重新簽署的檢測到的請求（例如缺少其 `x-amz-date` 標頭的請求）失敗並出現代理錯誤，而不是到達伺服器並帶有損壞的簽名。 當您遮罩其整個值時，Claude Code 自動將常規 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY` 和 `AWS_SESSION_TOKEN` 變數連結到一個認證中。如果您的 AWS 認證位於具有其他名稱的變數中，請使用 [`credentials.awsPairs`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-awspairs) 自己分組它們，需要 Claude Code v2.1.224 或更新版本。此範例將配對新增到已遮罩 `MY_KEY_ID`、`MY_SECRET_KEY` 和 `MY_SESSION_TOKEN` 整個值的配置中，如上面的[遮罩配置](https://code.claude.com/docs/zh-TW/sandboxing#mask-environment-variables)所示：

```
{
  "sandbox": {
    "credentials": {
      "awsPairs": [
        {
          "accessKeyIdVar": "MY_KEY_ID",
          "secretAccessKeyVar": "MY_SECRET_KEY",
          "sessionTokenVar": "MY_SESSION_TOKEN"
        }
      ]
    }
  }
}

```

每個項目遵循這些規則：

- `accessKeyIdVar` 和 `secretAccessKeyVar` 命名保存存取鍵 ID 和機密鍵的遮罩 `envVars` 項目。可選的 `sessionTokenVar` 命名保存臨時認證工作階段令牌的項目；設定時，代理在重新簽署的請求上發送真實令牌作為 `x-amz-security-token`。
- 每個命名的變數必須是遮罩其整個值的 `mask` 項目，沒有 `extract` 或 `decode`。
- 代理在存取鍵 ID 項目的 `injectHosts` 中列出的主機上重新簽署請求。
- 在配對中命名任何常規變數會替換自動配對。

如同 `mask` 項目，`awsPairs` 僅從使用者設定、受管設定和 `--settings` CLI 旗標尊重。 三種 AWS 請求形式攜帶代理無法重新計算的簽名。當此類請求使用遮罩配對的佔位符簽署時，代理失敗它而不是轉發損壞的簽名；使用未遮罩認證簽署的請求永遠不受影響。[`credentials.sigv4`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-sigv4) 設定（需要 Claude Code v2.1.224 或更新版本）放鬆每種形式：將形式的鍵設定為 `passthrough` 轉發帶有其佔位符衍生簽名的請求，因此呼叫工具接收 AWS 自己的拒絕回應而不是代理錯誤。如同 `awsPairs`，`sigv4` 僅從使用者設定、受管設定和 `--settings` CLI 旗標尊重。

| 請求形式             | `sigv4` 鍵  | 代理無法重新簽署的原因                               |
| -------------------- | ----------- | ---------------------------------------------------- |
| aws-chunked 串流上傳 | `streaming` | 每個區塊簽名鏈接到種子簽名，因此重新簽署需要重寫主體 |
| 預簽署 URL           | `presigned` | 簽名位於 URL 本身，沒有 `Authorization` 標頭         |
| SigV4A 非對稱簽名    | `sigv4a`    | 沒有共用鍵 HMAC 可重新計算                           |

#### 遮罩認證檔案

檔案項目也接受 `"mode": "mask"`，需要 Claude Code v2.1.221 或更新版本。沙箱化命令看到的內容取決於平台：

- **Linux 和 WSL2** ：沙箱化命令讀取檔案的哨兵複本，一個機密被替換為佔位符值的替代品，[沙箱代理](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)在出站時替換真實值。
- **macOS** ：沙箱化命令無法讀取列出的檔案。Claude Code 不建立哨兵複本，不在出站時替換任何內容，因此使用檔案進行身份驗證的工具在沙箱內不工作，與 `deny` 相同的效果。與 `deny` 項目不同，讀取區塊即使在您[停用檔案系統隔離](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)時也保持有效。

在每個平台上，Claude Code 應用 [`network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate) 要求和 `injectHosts` 的方式與[遮罩環境變數](https://code.claude.com/docs/zh-TW/sandboxing#mask-environment-variables)相同，並以相同方式忽略儲存庫設定。如果您[排除使用者設定](https://code.claude.com/docs/zh-TW/sandboxing#configure-sandboxing)，Claude Code 保持 `~/.claude/settings.json` 中的檔案 `mask` 項目作為限制，但項目不再授權代理替換真實值。 下面的範例遮罩儲存在 `~/.config/gh/hosts.yml` 中的 GitHub 令牌；`extract` 模式（如下所述）告訴 Claude Code 檔案的哪個部分是機密。在 Linux 和 WSL2 上，讀取檔案的沙箱化命令獲得令牌位置的哨兵，代理在對 `api.github.com` 的請求上替換真實令牌：

```
{
  "sandbox": {
    "enabled": true,
    "network": {
      "tlsTerminate": {},
      "allowedDomains": ["*.github.com"]
    },
    "credentials": {
      "files": [
        {
          "path": "~/.config/gh/hosts.yml",
          "mode": "mask",
          "extract": "oauth_token:\\s*(\\S+)",
          "injectHosts": ["api.github.com"]
        }
      ]
    }
  }
}

```

若要確認遮罩有效，請要求 Claude 在沙箱化命令中執行 `cat ~/.config/gh/hosts.yml`：在 Linux 和 WSL2 上，輸出顯示令牌位置的哨兵值，在 macOS 上，讀取失敗。 在 Linux 和 WSL2 上，`extract` 模式是保持 `hosts.yml` 其餘部分可讀的內容。Claude Code 在整個檔案上應用正規表達式，僅替換每個匹配的第 1 組捕獲的文字，因此 `gh` 仍然解析其配置，僅令牌是佔位符。對任何工具解析的結構化檔案使用 `extract`，例如 `.netrc`、JSON 或 YAML；模式必須包含至少一個捕獲組。沒有 `extract`，Claude Code 將整個檔案內容替換為一個哨兵值，適合保存單個裸機密且沒有其他內容的檔案。 對於保存 JSON Web Token (JWT) 的檔案，設定 `decode: "jwt"` 而不是或與 `extract` 一起。`decode` 需要 Claude Code v2.1.224 或更新版本。Claude Code 使用內建模式或您的 `extract` 模式（設定時）找到 JWT 候選項，驗證每個候選項是 JWT，並將其替換為結構上有效的假令牌，因此在沙箱內解碼令牌的程式碼繼續工作。新增 `maskClaims` 以僅遮罩每個驗證令牌內的命名頂級承載聲明，並保持其他聲明可讀。當沒有候選項驗證或沒有命名聲明匹配時，下面的 `onExtractNoMatch` 欄位控制結果，就像模式匹配無內容時一樣。 兩個可選欄位精化匹配行為。兩者僅在 `mode` 為 `mask` 且 `extract` 或 `decode` 設定時適用。在 macOS 上，當檔案系統隔離開啟時，Claude Code 應用 `mask` 項目作為 `deny`，在模式執行前，因此這些欄位和下面的無匹配結果僅在[檔案系統隔離關閉](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)時在那裡生效：

- `onExtractNoMatch` 控制匹配在檔案中找不到要遮罩的內容時發生的情況：
  - `warn`（預設）警告並跳過項目，因此沙箱化命令可以無遮罩地讀取真實檔案。預設適合可能合法不存在的認證；如果機密可能存在但模式可能遺漏它，使用 `deny`
  - `deny` 使檔案無法讀取
  - `error` 停止沙箱設定，直到您修復配置 每當讀取區塊不會被強制執行時，Claude Code 將 `deny` 視為 `error`：當您[停用檔案系統隔離](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)時，以及當任何設定來源的 `filesystem.allowRead` 項目重新開啟檔案的路徑時。
- `maskDuplicates` 也替換每個遮罩認證值的逐字複本，一個 `extract` 捕獲或 `decode` 驗證的令牌，在匹配跨度外找到，用於在匹配無法到達的地方重複的機密。它匹配原始子字串，因此短或常見值會被替換到處出現；為長、高熵機密保留它。預設：false。

`mask` 適用於單個檔案，因此個別列出每個認證檔案。Claude Code 回退到 `deny` 用於無法安全遮罩的 `mask` 項目：目錄路徑、glob 模式、大於 8 MiB 的檔案或非 UTF-8 文字檔案。改為將目錄編寫為明確的 `deny` 項目；[哪些設定可以停用它](https://code.claude.com/docs/zh-TW/sandboxing#which-settings-can-disable-it)下的表格涵蓋每種形式是否固定 `filesystem.disabled` 以及它在檔案系統隔離關閉時的行為。

## 沙箱隔離的運作方式

### 檔案系統隔離

沙箱化的 Bash 工具將檔案系統存取限制在特定目錄：

- **預設寫入行為** ：對目前工作目錄及其子目錄、任何使用 `--add-dir`、`/add-dir` 或 [`permissions.additionalDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-additionaldirectories) 新增的目錄，以及 `$TMPDIR` 指向的工作階段暫存目錄具有讀寫存取權限
- **預設讀取行為** ：對整個電腦具有讀取存取權限，除了某些被拒絕的目錄。請注意，此預設仍允許讀取認證檔案，例如 `~/.aws/credentials` 和 `~/.ssh/`。使用 [`sandbox.credentials`](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) 來阻止讀取這些檔案並取消設定祕密環境變數，或將路徑新增至 `denyRead`。
- **被阻止的存取** ：無法修改工作目錄、新增的目錄和工作階段暫存目錄外的檔案，除非有明確的權限，包括 shell 設定檔案（例如 `~/.bashrc`）和 `/bin/` 中的系統二進位檔
- **Git worktrees** ：當工作目錄是[連結的 git worktree](https://code.claude.com/docs/zh-TW/worktrees) 時，沙箱也允許寫入主儲存庫的共用 `.git` 目錄，以便 `git commit` 等命令可以更新參考和索引。對該目錄內的 `hooks/` 和 `config` 的寫入仍被拒絕。
- **可設定** ：透過設定定義自訂允許和拒絕的路徑

若要完全跳過檔案系統隔離，同時保持網路隔離，請設定 [`sandbox.filesystem.disabled`](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)。

### 受保護的路徑

在沙箱化命令可以寫入的目錄內，沙箱仍然拒絕寫入 Claude Code 載入設定和程式碼的檔案。可以編輯這些檔案的命令可能會授予自己權限，或新增 Claude Code 在沙箱外執行的 hook 或 MCP 伺服器。權限系統有自己的[受保護路徑](https://code.claude.com/docs/zh-TW/permission-modes#protected-paths)，控制 Claude Code 在工具執行前批准的內容；沙箱的清單適用於已在執行的命令。它涵蓋四組路徑：

- **在您的工作目錄及其上方的目錄中** ：`.claude` 設定檔案、`.claude/skills`、`.claude/agents`、`.claude/commands` 和 `.claude/hooks` 目錄、`.mcp.json`，以及 Claude Code 自行執行的檔案，例如 `.claude/workflows` 和 `.claude/scheduled_tasks.json`
- **僅在您的工作目錄中** ：shell 啟動檔案，例如 `.bashrc` 和 `.zshrc`、`.gitconfig`、`.vscode` 和 `.idea` 目錄，以及 `.git` 內的 `hooks` 和 `config`
- **會將您的工作目錄轉變為裸 git 儲存庫的檔案** ：頂層的 `HEAD`、`objects` 和 `refs`，加上 `HEAD` 旁邊的 `config` 和 `hooks`。即使沒有 `HEAD`，名為 `config` 的檔案也被拒絕。在 Linux 和 WSL2 上，當沙箱化命令執行時，沙箱會刪除出現的頂層 `HEAD` 檔案或 `objects` 或 `refs` 目錄
- **在`~/.claude` 中，或 `CLAUDE_CONFIG_DIR` 指向的目錄中**：其大部分內容，加上 `~/.claude.json` 和 `.credentials.json` 認證存放區

如果在工作階段期間在受保護設定檔案的路徑出現符號連結，沙箱也會拒絕寫入它指向的檔案，從下一個命令開始。 無法豁免這些路徑之一：涵蓋該路徑的 `allowWrite` 項目或 `Edit` 允許規則不會解除保護。關閉保護的唯一方法是 [`filesystem.disabled`](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，它會關閉每個路徑的檔案系統隔離。若要查看為您的機器解析的大部分這些路徑，請執行 `/sandbox` 並開啟 **Config** 標籤，該標籤在 **Denied within allowed** 下列出它們，混合您自己的 `denyWrite` 項目。 如果 `git merge` 或 `git checkout` 在這些路徑之一上失敗並出現 `unable to unlink old`，請參閱[疑難排解](https://code.claude.com/docs/zh-TW/sandboxing#troubleshooting)。

### 網路隔離

網路存取透過在沙箱外執行的代理伺服器進行控制：

- **網域限制** ：Claude Code 預設不預先允許任何網域。命令首次需要新網域時，Claude Code 會提示批准；在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)中，Claude 改為在命令本身上命名命令需要的主機，根據[每個命令允許的網域](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode)。
- **批准選擇** ：如果您在提示時選擇「是」，Claude Code 會在目前工作階段的其餘時間允許該主機，並且不會再次提示稍後連線到同一主機。如果您選擇「是，以後不要再問」，Claude Code 會將 `WebFetch(domain:...)` 允許規則儲存到您的[本機設定](https://code.claude.com/docs/zh-TW/permissions#permission-system)，以便該主機在未來工作階段中保持允許。
- **預先允許的網域** ：使用 [`allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 預先允許網域以完全避免提示。Claude Code 也預先允許來自 `WebFetch(domain:...)` 允許規則的網域，如[權限規則](https://code.claude.com/docs/zh-TW/sandboxing#permission-rules)中所述。
- **嚴格允許清單** ：如果您在使用者、受管理或 CLI `--settings` 設定中將 [`strictAllowlist`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-strictallowlist) 設定為 `true`，Claude Code 會拒絕沙箱化命令存取允許清單外的任何主機，而不是提示。允許清單與沙箱以其他方式提示的清單相同：`allowedDomains` 加上來自 `WebFetch(domain:...)` 允許規則的網域，或當設定 `allowManagedDomainsOnly` 時僅受管理設定項目。Claude Code 僅對沙箱化命令強制執行此操作；進程內工具（例如 `WebFetch`）仍遵循其[權限規則](https://code.claude.com/docs/zh-TW/sandboxing#permission-rules)。在儲存庫的 `.claude/settings.json` 或 `.claude/settings.local.json` 中設定它沒有效果。需要 Claude Code v2.1.219 或更新版本。
- **受管理的鎖定** ：如果在受管理設定中設定了 [`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly)，非允許的網域會自動被阻止而不是提示，並且僅受管理設定中的 `allowedDomains` 和 `WebFetch(domain:...)` 允許規則被接受。
- **公司代理** ：當您的網路要求出站流量通過公司代理時，請在設定的 `env` 區塊中設定 `HTTPS_PROXY`、`HTTP_PROXY` 和 `NO_PROXY`，如[代理設定](https://code.claude.com/docs/zh-TW/network-config#proxy-configuration)所述，以便[背景代理](https://code.claude.com/docs/zh-TW/network-config#set-network-variables-in-settings-not-the-shell)也能取得它們，或在您啟動 Claude Code 的環境中設定。Claude Code 強制執行網域允許清單，然後透過該上游代理隧道允許的連線。
- **自訂代理支援** ：進階使用者可以在出站流量上實施自訂規則
- **全面涵蓋** ：限制適用於命令產生的所有指令碼、程式和子程序

在 `WebFetch(domain:...)` 規則中，沙箱接受兩種萬用字元形式：前導 `*.`（例如 `*.example.com`）和裸 `*`。裸 `*` 形式需要 Claude Code v2.1.186 或更新版本。任何其他位置的萬用字元（例如 `WebFetch(domain:example.*)`）仍會符合擷取但對沙箱化命令沒有效果。 內建代理根據請求的主機名稱強制執行允許清單，預設情況下不會終止或檢查 TLS 流量。實驗性 [`network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate) 設定（在 Claude Code v2.1.199 及更新版本中可用）使內建代理自行終止 TLS，這是 [`mask` 認證項目](https://code.claude.com/docs/zh-TW/sandboxing#mask-credentials)所需的。有關預設值的含義，請參閱[安全限制](https://code.claude.com/docs/zh-TW/sandboxing#security-limitations)，如果您的威脅模型需要 TLS 檢查，請參閱[自訂代理設定](https://code.claude.com/docs/zh-TW/sandboxing#custom-proxy-configuration)。

#### 自動模式中的每個命令允許的網域

在啟用沙箱的[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)中，Claude 在命令本身上命名命令需要的主機，而不是為每個連線觸發網路批准。在沙箱中執行的每個 Bash、PowerShell 或[監視器](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool)命令都可以攜帶超出沙箱允許清單的主機清單：網域（例如 `registry.npmjs.org`）、萬用字元（例如 `*.pythonhosted.org`）或 IP 位址，每個都帶有可選的 `:port`。分類器將主機與命令一起審查。需要 Claude Code v2.1.271 或更新版本。 批准的清單僅為該一個命令開啟這些主機，只要它執行。沒有任何內容被新增到您的工作階段允許的主機或您的設定；下一個命令命名其自己的主機。 攜帶主機的命令會進入分類器，而不是由權限規則或沙箱的[自動允許模式](https://code.claude.com/docs/zh-TW/sandboxing#sandbox-modes)批准。如果[詢問規則](https://code.claude.com/docs/zh-TW/permissions#manage-permissions)強制提示命令，您終端中的權限對話會在其旁邊列出主機，在那裡批准涵蓋兩者。 每個命令清單僅擴大沙箱預設拒絕的內容。[`deniedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-denieddomains) 項目仍會阻止。當 [`strictAllowlist`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-strictallowlist) 或 [`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly) 鎖定允許清單時，Claude Code 拒絕每個命令清單。 當每個命令清單適用時，Claude Code 拒絕連線到沒有批准命令列出的主機，沒有提示或分類器檢查。拒絕在命令的結果中命名主機，Claude 使用新增的主機重新執行命令。

#### 網域清單中的 IPv6 位址

沙箱的網域清單是 `allowedDomains`、`deniedDomains` 和提供它們的 `WebFetch(domain:...)` 規則。若要符合其中任何一個中的 IPv6 位址，請在括號中寫入文字：`"[::1]"` 符合該位址在每個連接埠上，`"[::1]:443"` 僅在連接埠 443 上符合它。將連接埠寫成 1 到 65535 之間的數字，不帶前導零。括號形式需要 Claude Code v2.1.229 或更新版本。在 v2.1.229 之前，當未括號項目最後一個冒號後的文字是連接埠號時，Claude Code 將其讀為一個，所以 `::1:443` 命名位址 `::1` 在連接埠 443 上。 當您在 IPv6 位址的網路批准提示中選擇「是，以後不要再問」時，Claude Code 會使用括號的位址儲存 `WebFetch(domain:...)` 規則，以便規則在未來工作階段中保持符合位址。 帶有兩個或更多冒號的未括號項目是模稜兩可的：`::1:443` 既是完整的 IPv6 位址，也是位址後跟連接埠。Claude Code 保守地強制執行模稜兩可的拼寫，而不是猜測您的意思是哪個讀法：

- **拒絕清單** ：Claude Code 拒絕項目解析為的每個讀法，所以無論您的意思是哪個讀法都被阻止。對於沒有可解析讀法的項目，Claude Code 不阻止任何內容。
- **允許清單** ：Claude Code 永遠不允許超過您寫的內容。當該讀法乾淨地解析時，它會將模稜兩可的項目重寫為其主機和連接埠讀法，並可能完全刪除項目，而不是擴大允許清單。

在您的終端中執行 `claude doctor` 以找到受影響的項目：`Sandbox network domain entries have unreliable spellings` 警告命名最多三個並計算其餘的。將每個重寫為括號形式以清除警告。警告也命名拼寫不可靠的項目，原因包括 `@`、路徑或查詢字元，或括號內的萬用字元。

### 作業系統層級強制執行

沙箱化的 Bash 工具使用作業系統安全原語：

- **macOS** ：使用 Seatbelt 進行沙箱強制執行
- **Linux** ：使用 [bubblewrap](https://github.com/containers/bubblewrap) 進行隔離
- **WSL2** ：使用 bubblewrap，與 Linux 相同

不支援 WSL1，因為 bubblewrap 需要僅在 WSL2 中可用的核心功能。 這些相同的原語可作為獨立的 [`@anthropic-ai/sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) 套件使用，[沙箱環境](https://code.claude.com/docs/zh-TW/sandbox-environments#sandbox-runtime)頁面涵蓋作為包裝整個 Claude Code 程序的單獨方法。

## 沙箱隔離如何與權限和權限模式相關

沙箱隔離、[權限規則](https://code.claude.com/docs/zh-TW/permissions)和[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)是互補的層級。下面的章節涵蓋沙箱隔離如何與每一個互動。

### 權限規則

權限規則和沙箱隔離控制不同的事項：

- **權限規則** 控制 Claude Code 可以使用哪些工具，並在任何工具執行前進行評估。它們適用於每個工具：Bash、Read、Edit、WebFetch、MCP 和其他工具，除了拒絕或詢問規則無法阻止 [`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior)，而其他任何工具仍然存在。
- **沙箱隔離** 提供作業系統層級的強制執行，限制 shell 命令在檔案系統和網路層級可以存取的內容。它僅適用於 Bash、PowerShell 和 [Monitor](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool) 命令及其子程序。

這兩個層級在強制執行方式上也有所不同。Claude Code 在命令執行前根據命令字串評估權限決定，在自動模式下，還會根據單獨分類器對命令是否安全的判斷。作業系統在執行中的程序上強制執行沙箱邊界，因此無論模型選擇執行什麼，即使允許的命令執行的操作超出其名稱所示，它都會保持有效。 檔案系統和網路限制通過沙箱設定和權限規則進行配置：

| 設定或規則                                                                                                                                                                                                                                                       | 功能                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `sandbox.filesystem.allowWrite`                                                                                                                                                                                                                                  | 授予子程序對工作目錄外路徑的寫入存取權限                                    |
| `sandbox.filesystem.denyWrite` 和 `sandbox.filesystem.denyRead`                                                                                                                                                                                                  | 阻止子程序存取特定路徑                                                      |
| `sandbox.filesystem.allowRead`                                                                                                                                                                                                                                   | 重新允許讀取 `denyRead` 區域內的特定路徑                                    |
| [`sandbox.filesystem.disabled`](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)                                                                                                                                                      | 完全關閉檔案系統層級，同時保持網路隔離                                      |
| `Edit` 允許規則                                                                                                                                                                                                                                                  | 授予對特定路徑的寫入存取權限，與 `sandbox.filesystem.allowWrite` 的方式相同 |
| `Read` 和 `Edit` 拒絕規則                                                                                                                                                                                                                                        | 阻止存取特定檔案或目錄                                                      |
| `WebFetch(domain:...)` 允許和拒絕規則                                                                                                                                                                                                                            | 控制網域存取                                                                |
| 沙箱 `allowedDomains`                                                                                                                                                                                                                                            | 控制 Bash 命令可以到達哪些網域                                              |
| 沙箱 `deniedDomains`                                                                                                                                                                                                                                             | 阻止特定網域，即使更廣泛的 `allowedDomains` 萬用字元原本會允許它們          |
| 來自沙箱設定和權限規則的路徑和網域會合併到最終的沙箱配置中。 [claude-code 儲存庫的範例目錄](https://github.com/anthropics/claude-code/tree/main/examples/settings)包含常見部署場景的入門設定配置，包括沙箱特定的範例。使用這些作為起點，並根據您的需求進行調整。 |                                                                             |

### 權限模式

`/sandbox` 不是[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。權限模式決定工具呼叫是否執行以及是否先提示您，而沙箱限制 Bash 命令執行後可以存取的內容。它們在控制的內容和替代每個動作提示的內容上有所不同：

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 控制的內容                    | 替代提示的內容                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/sandbox`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Bash 命令執行後可以存取的內容 | 沙箱邊界本身，在[自動允許模式](https://code.claude.com/docs/zh-TW/sandboxing#sandbox-modes)中                                                                                                                        |
| [自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 每個工具呼叫是否執行          | 檢查動作的分類器                                                                                                                                                                                                     |
| `--dangerously-skip-permissions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 每個工具呼叫是否執行          | 無。[受保護路徑](https://code.claude.com/docs/zh-TW/permission-modes#protected-paths)檢查也會被跳過；[模式自動核准的動作](https://code.claude.com/docs/zh-TW/permission-modes#actions-no-mode-auto-approves)仍然適用 |
| 沙箱的[自動允許模式](https://code.claude.com/docs/zh-TW/sandboxing#sandbox-modes)與[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)分開：自動允許因為沙箱邊界包含它們而核准 Bash 命令，而自動模式使用分類器檢查動作。這兩者獨立運作，可以結合使用，但[沙箱模式](https://code.claude.com/docs/zh-TW/sandboxing#sandbox-modes)下列出的例外情況除外。若要為無人值守執行選擇隔離邊界，請參閱[沙箱環境](https://code.claude.com/docs/zh-TW/sandbox-environments#how-isolation-relates-to-permission-modes)。如需常見權限模式和沙箱配對的表格以及啟動每個配對的旗標，請參閱[常見設定](https://code.claude.com/docs/zh-TW/permission-modes#common-setups)。 |                               |                                                                                                                                                                                                                      |

## 為您的組織設定沙箱

管理員可以為每個使用者要求沙箱化，防止開發人員擴大策略，並通過公司代理路由沙箱流量。

### 使用受管設定強制執行沙箱化

若要為每個開發人員要求沙箱，通過 [managed settings](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms) 傳遞 `sandbox` 金鑰，可以是由您的 MDM 管理的檔案，也可以是通過 claude.ai 上的 [server-managed settings](https://code.claude.com/docs/zh-TW/server-managed-settings)。 以下受管設定配置啟用沙箱，如果沙箱無法初始化則拒絕啟動 Claude Code，並防止模型在沙箱外重試命令：

```
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  }
}

```

超過 `enabled` 的兩個金鑰控制沙箱無法執行命令時會發生什麼：

- **`failIfUnavailable`**：缺少的依賴項（例如 Linux 上的 bubblewrap）會阻止 Claude Code 啟動，而不是顯示警告並回退到未沙箱化執行
- **`allowUnsandboxedCommands: false`**：Claude Code 忽略`dangerouslyDisableSandbox` 逃生艙，因此在沙箱下失敗的命令無法在其外重試

值得考慮與它們一起的兩個補充。為任何必須在沒有隔離的情況下執行的組織批准的工具新增 `excludedCommands`。為認證目錄（例如 `~/.aws` 和 `~/.ssh`）和祕密環境變數新增 [`sandbox.credentials`](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) 項目，因為預設讀取策略仍允許這些。 此配置沙箱化 Claude 執行的命令。開發人員仍然可以在 [`!` shell 模式提示](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)輸入命令並在沙箱外執行它，具有他們在 Claude Code 外任何終端中已有的相同存取權限。請參閱 [The unsandboxed retry escape hatch](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch) 以了解輸入的命令在沙箱中執行的工作階段。 沙箱不在原生 Windows 上執行，因此如果您的機隊包括 Windows 主機，請將此配置限制在 macOS 和 Linux，或讓這些使用者在 WSL2 或容器內執行 Claude Code。

### 防止開發人員擴大策略

對於布林金鑰（例如 `enabled` 和 `failIfUnavailable`），Claude Code 使用受管值並忽略開發人員在本地設定的任何內容。對於陣列金鑰（例如 `excludedCommands` 和 `allowRead`），Claude Code 合併來自工作階段載入的每個範圍的項目，因此開發人員可以附加擴大策略的項目。 在受管設定中將 `allowManagedReadPathsOnly` 設定為 `true`，以便只有來自受管設定的 `allowRead` 項目被尊重。這防止開發人員擴大讀取存取超過組織批准的路徑。若要以相同方式將網路域鎖定到受管值，請設定 [`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly)。 當受管設定配置 `sandbox.filesystem` 或列出任何具有 `"mode": "deny"` 的 `sandbox.credentials.files` 項目時，只有受管設定可以設定 [`filesystem.disabled`](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，因此開發人員無法關閉管理員部署的檔案系統限制。`mask` 項目是否固定金鑰取決於它如何解析；[Which settings can disable it](https://code.claude.com/docs/zh-TW/sandboxing#which-settings-can-disable-it) 下的表格涵蓋四種情況。 `excludedCommands` 沒有等效的受管專用鎖定，因此開發人員總是可以附加在沙箱外執行其他命令的項目。保持受管清單狹窄。

### 自訂代理配置

對於需要進階網路安全的組織，您可以實施自訂代理以：

- 解密和檢查 HTTPS 流量
- 應用自訂過濾規則
- 記錄所有網路請求
- 與現有安全基礎設施整合

若要將 Claude Code 指向您的代理，請在 [sandbox settings](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-settings) 中設定代理連接埠：

```
{
  "sandbox": {
    "network": {
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    }
  }
}

```

## 故障排除

某些命令在沙箱內失敗，即使它們在沙箱外工作。下面的修復涵蓋最常見的情況。

- **命令因主機不允許錯誤而失敗** ：許多 CLI 工具需要到達特定主機。在提示時授予權限會將主機新增到您的允許清單，以便工具在將來在沙箱內執行。
- **`jest`掛起或失敗** ：`watchman` 與沙箱不相容。改為執行 `jest --no-watchman`。
- **Go 型 CLI 在 macOS 上 TLS 驗證失敗** ：`gh`、`gcloud` 和 `terraform` 等工具在 Seatbelt 下可能無法進行 TLS 驗證。在 `excludedCommands` 中列出這些工具以在沙箱外執行它們。如果您使用 `httpProxyPort` 與 MITM 代理和自訂 CA，請改為將 [`enableWeakerNetworkIsolation`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-enableweakernetworkisolation) 設定為 `true`。
- **`open`、`osascript` 或瀏覽器型驗證流程在 macOS 上因錯誤 `-600` 而失敗**：沙箱預設會阻止 Apple Events。在您的使用者、受管理或 CLI 設定中將 [`allowAppleEvents`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-allowappleevents) 設定為 `true` 以允許它們。專案設定會被忽略此金鑰。啟用它會移除程式碼執行隔離，因為沙箱化命令之後可以啟動其他應用程式而不進行沙箱化，無需使用者提示，並向執行中的應用程式傳送 AppleScript 命令，受限於 macOS 自動化同意提示 (TCC)。或者，將命令新增到 `excludedCommands` 以在沙箱外執行它。
- **`docker`命令失敗** ：`docker` 與沙箱不相容。將 `docker *` 新增到 `excludedCommands` 以在沙箱外執行它。
- **`pbcopy`、`xclip` 或 `wl-copy` 不會更新剪貼簿**：這些剪貼簿公用程式可能無法從沙箱內到達系統剪貼簿，在這種情況下，傳送給它們的文字不會到達。若要將 Claude 的輸出放在您的剪貼簿上，請要求 Claude 在其回應中列印它，然後執行 [`/copy`](https://code.claude.com/docs/zh-TW/commands)，它從 Claude Code 程序而不是從沙箱化命令寫入剪貼簿。或者，將 `pbcopy *`、`wl-copy *` 或 `xclip *` 新增到 `excludedCommands` 以在沙箱外執行命令。
- **git 命令因`unable to unlink old` 而失敗**：`git merge`、`git checkout` 和類似命令在需要取代沙箱拒絕寫入的檔案時以這種方式失敗，無論該檔案是在 [受保護路徑](https://code.claude.com/docs/zh-TW/sandboxing#protected-paths) 下（例如 `.claude/skills`）、在您的 `denyWrite` 項目之一下，還是完全在沙箱允許命令寫入的目錄之外。在 Linux 和 WSL2 上，錯誤以 `Read-only file system` 結尾。 失敗後，Claude 可能會 [提供在沙箱外重新執行命令](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch)；批准該重試，或在另一個終端中自己執行 git 命令。如果您已將 `allowUnsandboxedCommands` 設定為 `false`，Claude 無法提供重試，因此請自己執行命令。如果相同的 git 命令經常失敗，請將其新增到 [`excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands)。
- **Bubblewrap 在容器內啟動失敗** ：在無特權容器中，bubblewrap 無法掛載新的 `/proc` 檔案系統，因此沙箱化命令失敗，出現 `bwrap` 錯誤，例如 `Can't mount proc on /newroot/proc: Operation not permitted`。將 [`enableWeakerNestedSandbox`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-enableweakernestedsandbox) 設定為 `true`，以便內部沙箱綁定掛載容器的現有 `/proc`。僅在外部容器已提供您需要的隔離邊界時使用此設定，因為它向沙箱化命令公開程序資訊，新的 `/proc` 掛載會隱藏。
- **0 位元組唯讀檔案出現在`.claude` 設定路徑，且「是，不要再問」不會儲存**：在 Linux 和 WSL2 上，沙箱在沙箱化命令執行時透過在該處建立 0 位元組唯讀預留位置來保持對尚不存在的檔案的寫入拒絕。沙箱在之後移除預留位置。如果在該清理執行之前會話被終止，例如透過 SIGKILL，預留位置會保留下來。稍後的會話在每次啟動時再次將它們綁定為唯讀，因此設定寫入（例如儲存權限選擇）在其中一個位置失敗。 執行 `claude doctor` 以列出剩餘的預留位置檔案。[`Stale sandbox mask files left by a killed session`](https://code.claude.com/docs/zh-TW/errors#stale-sandbox-mask-files-left-by-a-killed-session) 警告命名最多三個，並計算其餘的。在該專案中沒有其他 Claude Code 會話執行時，使用 `rm` 刪除每個檔案。在 v2.1.257 之前，Claude Code 留下相同的預留位置而不標記它們。
- **`--dangerously-skip-permissions`以 root 身份失敗** ：在 Linux 和 macOS 上以 root 身份或透過 sudo 執行時，此旗標被阻止，因為 root 存取加上沒有權限提示可以修改系統上的任何檔案或服務。檢查在識別的沙箱內自動跳過。若要在容器中自主執行，請使用 [dev container](https://code.claude.com/docs/zh-TW/devcontainer) 配置，它以非 root 使用者身份執行 Claude Code。

## 限制

沙箱化減少風險，但不是完整的隔離邊界。在依賴它作為硬安全控制之前，請檢查下面的限制。

### 安全限制

- **網路過濾** ：沙箱限制流程可以連接的域名。預設情況下，內建代理不終止或檢查出站流量上的 TLS，因此加密連接的內容不被檢查。實驗性的 [`network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate) 設定在代理處終止 TLS 以進行 [`mask` 認證替換](https://code.claude.com/docs/zh-TW/sandboxing#mask-credentials)，但不添加內容過濾。您負責確保只有受信任的域名在您的策略中被允許。

允許廣泛域名（例如 `github.com`）可能會為資料洩露建立路徑。因為代理根據用戶端提供的主機名進行允許決定而不檢查 TLS，在沙箱內執行的程式碼可能可以使用 [domain fronting](https://en.wikipedia.org/wiki/Domain_fronting) 或類似技術到達允許清單外的主機。如果您的威脅模型需要更強的保證，請配置 [custom proxy](https://code.claude.com/docs/zh-TW/sandboxing#custom-proxy-configuration)，它終止 TLS 並檢查流量，並在沙箱內安裝其 CA 憑證。更強的 TLS 感知網路隔離是一個活躍的開發領域。

- **通過 Unix 套接字的特權提升** ：`allowUnixSockets` 配置可能會無意中授予對系統服務的存取，這可能導致沙箱繞過。例如，允許存取 `/var/run/docker.sock` 有效地通過 Docker 套接字授予對主機系統的存取。仔細考慮您通過沙箱允許的任何 Unix 套接字。
- **檔案系統權限提升** ：過於寬泛的檔案系統寫入權限可能導致特權提升攻擊。允許寫入包含 `$PATH` 中可執行檔案的目錄、系統配置目錄或使用者 shell 配置檔案（例如 `.bashrc` 或 `.zshrc`）可能導致當其他使用者或系統流程存取這些檔案時在不同安全上下文中執行程式碼。
- **Linux 沙箱強度** ：Linux 實現提供強大的檔案系統和網路隔離，但包含一個 `enableWeakerNestedSandbox` 模式，使其能夠在 Docker 環境中工作而無需特權命名空間，或在 Linux 主機上禁用無特權使用者命名空間的情況下。此選項大大削弱了安全性，應僅在其他隔離被強制執行時使用。
- **macOS 上的 Apple Events** ：macOS 沙箱預設阻止 Apple Events。`allowAppleEvents` 設定解除此限制，使 `open` 和 `osascript` 等工具能夠運作，但它移除了程式碼執行隔離：沙箱化命令可以啟動其他應用程式而不進行沙箱化，無需使用者提示，並可以向執行中的應用程式傳送 AppleScript 命令，受限於每個應用程式的 macOS 自動化同意提示 (TCC)。它僅從使用者、受管或 CLI 設定中被接受。專案設定無法啟用它。

### 平台和工具相容性

- **平台支援** ：支援 macOS、Linux 和 WSL2。不支援 WSL1 和原生 Windows。
- **效能開銷** ：最小，但某些檔案系統操作可能稍慢。
- **工具相容性** ：某些需要特定系統存取模式的工具可能需要配置調整，或可能需要在沙箱外執行。

### 範圍

沙箱隔離 Bash 子流程。其他工具在不同的邊界下運作：

- **內建檔案工具** ：Read、Edit 和 Write 直接使用權限系統，而不是通過沙箱執行。請參閱 [permissions](https://code.claude.com/docs/zh-TW/permissions)。
- **電腦使用** ：當 Claude 打開應用程式並控制您的螢幕時，它在您的實際桌面上執行，而不是在隔離環境中。每個應用程式的權限提示控制每個應用程式。請參閱 [CLI 中的電腦使用](https://code.claude.com/docs/zh-TW/computer-use) 或 [Desktop 中的電腦使用](https://code.claude.com/docs/zh-TW/desktop#let-claude-use-your-computer)。
- **環境變數** ：沙箱化 Bash 命令預設繼承父流程環境，包括在那裡設定的任何認證。使用 [`sandbox.credentials`](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) 為沙箱化命令取消設定或遮罩特定變數，或設定 [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/zh-TW/env-vars) 以從所有子流程中去除認證。
- **子代理** ：[subagents](https://code.claude.com/docs/zh-TW/sub-agents) 在與父工作階段相同的流程中執行，並使用相同的沙箱配置。當在父工作階段中啟用沙箱化時，子代理內的 Bash 命令被沙箱化。

有效的沙箱化需要同時進行檔案系統和網路隔離。沒有網路隔離，受損的代理可能會洩露敏感檔案，如 SSH 金鑰。沒有檔案系統隔離，無論是來自寬鬆的策略還是來自 [disabling the filesystem layer](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，受損的代理可能會後門系統資源以獲得網路存取。當您擴大預設值時，檢查 `allowWrite` 路徑、廣泛的 `allowedDomains` 項目或 `excludedCommands` 例外是否不會撤銷另一側的限制。

## 另請參閱

- [Sandbox environments](https://code.claude.com/docs/zh-TW/sandbox-environments)：比較內建沙箱與開發容器、容器和虛擬機
- [Security](https://code.claude.com/docs/zh-TW/security)：全面的安全功能和最佳實踐
- [Permissions](https://code.claude.com/docs/zh-TW/permissions)：權限配置和存取控制
- [All settings](https://code.claude.com/docs/zh-TW/settings-reference)：每個設定鍵
- [CLI reference](https://code.claude.com/docs/zh-TW/cli-reference)：命令列選項

是否 助手
