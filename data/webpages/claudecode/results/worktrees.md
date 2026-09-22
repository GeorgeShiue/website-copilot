[git worktree](https://git-scm.com/docs/git-worktree) 是一個獨立的工作目錄，具有自己的檔案和分支，但與主要檢出共享相同的儲存庫歷史記錄和遠端。在自己的 worktree 中執行每個 Claude Code 會話意味著一個會話中的編輯永遠不會觸及另一個會話中的檔案，因此一個會話可以建置功能，而第二個會話可以修復錯誤。 Worktrees 需要 git 儲存庫；對於其他版本控制系統，請[配置 hooks 以取代 git 邏輯](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control)。在[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)中，當您啟動會話時選擇 **worktree** 選項，為其提供自己的 worktree。 Worktrees 是執行 Claude 平行處理的幾種方式之一。它們隔離檔案編輯。[子代理](https://code.claude.com/docs/zh-TW/sub-agents)在一個會話內分割工作，[跨會話訊息傳遞](https://code.claude.com/docs/zh-TW/cross-session-messaging)讓 Claude 在您的 worktrees 中的會話之間傳遞發現。請參閱[平行執行代理](https://code.claude.com/docs/zh-TW/agents)以比較這些方法，或跳到[使用 worktrees 隔離子代理](https://code.claude.com/docs/zh-TW/worktrees#isolate-subagents-with-worktrees)以同時使用 worktrees 和子代理。 大多數會話只需要前兩個部分：[在 worktree 中啟動 Claude](https://code.claude.com/docs/zh-TW/worktrees#start-claude-in-a-worktree)，然後[退出時清理](https://code.claude.com/docs/zh-TW/worktrees#clean-up-worktrees)。當您需要[恢復會話](https://code.claude.com/docs/zh-TW/worktrees#resume-a-worktree-session)、[變更 worktrees 的建立方式](https://code.claude.com/docs/zh-TW/worktrees#customize-worktree-creation)或[除錯失敗](https://code.claude.com/docs/zh-TW/worktrees#troubleshooting)時，請返回頁面的其餘部分。

## 在 worktree 中啟動 Claude

傳遞 `--worktree` 或 `-w` 以及名稱來建立隔離的 worktree 並在其中啟動 Claude。預設情況下，worktree 在您的儲存庫根目錄下的 `.claude/worktrees/<name>/` 下建立，在名為 `worktree-<name>` 的新分支上：

```
claude --worktree feature-auth

```

在另一個終端中使用不同的名稱再次執行該命令以啟動第二個隔離的會話。如果您省略名稱，Claude 會生成一個名稱，例如 `bright-running-fox`。 互動式執行需要[工作區信任](https://code.claude.com/docs/zh-TW/security)：如果您之前未在該目錄中執行過 Claude，請在那裡執行一次 `claude` 以接受信任對話，或 `--worktree` 會以錯誤退出並提示您執行此操作。使用 `-p` 的非互動式執行會跳過信任檢查，因此 `claude -p --worktree` 會在沒有信任檢查的情況下進行。 將 `.claude/worktrees/` 新增到您的 `.gitignore`，以便 worktree 內容不會在您的主要檢出中顯示為未追蹤的檔案。

### 設定 worktree 環境

Worktree 是一個新的檢出，因此請在那裡初始化您的開發環境：要求 Claude 安裝依賴項，或在 `.claude/worktrees/` 下的 worktree 目錄中自己執行您的專案設定。要自動將 gitignored 檔案（例如 `.env`）帶入每個新 worktree，請新增[`.worktreeinclude` 檔案](https://code.claude.com/docs/zh-TW/worktrees#copy-gitignored-files-into-worktrees)。

### 要求 Claude 建立 worktree

您也可以在會話期間要求 Claude「在 worktree 中工作」，它會使用 [`EnterWorktree`](https://code.claude.com/docs/zh-TW/tools-reference) 工具建立一個。進入 worktree 後，Claude 可以透過呼叫 `EnterWorktree` 並指定目標路徑，直接切換到 `.claude/worktrees/` 下的另一個 worktree；前一個 worktree 保持在磁碟上未被觸及。 當 Claude 進入儲存庫的 `.claude/worktrees/` 目錄外的路徑時，Claude Code 會先要求您的批准，因為該移動會將會話的工作目錄、寫入存取權限和專案配置（例如 `CLAUDE.md` 和設定）帶到該位置。`EnterWorktree` [權限規則](https://code.claude.com/docs/zh-TW/permissions)或選擇「不再詢問」不會抑制此提示；只有 `bypassPermissions` 模式會跳過它。在 v2.1.206 之前，Claude 可以進入任何現有的 worktree 路徑而無需詢問。 **Hook 路徑不跟隨 worktree。** 在 Claude 進入 worktree 後，Claude Code 會在您的 [hooks](https://code.claude.com/docs/zh-TW/hooks#reference-scripts-by-path) 中保持 `${CLAUDE_PROJECT_DIR}` 不變，並以不同的方式將 worktree 路徑傳遞給它們：

- **`${CLAUDE_PROJECT_DIR}`保持不變** ：它仍然指向會話啟動的專案根目錄，因此 hook 命令（例如 `${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh`）仍然在主要檢出中執行指令碼。
- **`cwd`跟隨 Claude** ：hook 的[輸入 JSON](https://code.claude.com/docs/zh-TW/hooks#common-input-fields) 中的 `cwd` 欄位是 worktree 根目錄，當 Claude 執行 `cd` 時它會再次移動。當 hook 需要 worktree 路徑時，請讀取它。

## 清理 worktrees

當您退出互動式 worktree 會話時，Claude 會檢查 worktree 是否有移除會刪除的工作：已變更或未追蹤的檔案，以及新提交。

- **worktree 是乾淨的** ：對於未命名的會話，Claude 會自動移除 worktree 及其分支。[已命名](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions)的會話會先提示您，以便您可以保留 worktree 供稍後使用
- **worktree 中有工作** ：Claude 會提示您保留或移除 worktree。保留會保留目錄和分支，以便您稍後可以返回。移除會刪除 worktree 目錄及其分支，以及其中的所有工作

使用 `-p` 的非互動式執行沒有退出提示，因此 Claude 不會清理它們的 worktrees，Claude Code 會在建立時對每個 worktree 保留它所取得的鎖定，直到稍後會話的[陳舊鎖定掃描](https://code.claude.com/docs/zh-TW/worktrees#clean-up-subagent-and-background-session-worktrees)釋放它。要移除一個，請執行 `git worktree remove`；如果 git 拒絕因為 worktree 被鎖定，請先在其上執行 `git worktree unlock`。 在 Windows 上，移除 worktree 不會刪除其外的檔案。如果 worktree 內的資料夾是指向其他地方的連結（例如 NTFS 連接點或目錄符號連結），Claude Code 只會刪除連結並保留它指向的資料夾。在 v2.1.205 之前，移除具有嵌套在子目錄中的連結的 worktree 可能會刪除它指向的資料夾。

## 恢復 worktree 會話

當您恢復在 worktree 內的會話時，Claude Code 會將會話返回到該 worktree。這適用於互動式恢復、[非互動式模式](https://code.claude.com/docs/zh-TW/headless)中的 `--continue` 和 `--resume`（使用 `-p`）以及 Agent SDK。回到 worktree 內，Claude 仍然可以使用 [`ExitWorktree`](https://code.claude.com/docs/zh-TW/tools-reference) 工具退出它。 在將會話返回到其 worktree 之前，Claude Code 會驗證 worktree 仍然是與主要檢出分開的檢出，並拒絕重新進入未通過檢查的 worktree。對於 git worktree，檢查會讀取其 git 中繼資料。沒有 git 中繼資料的 worktree（例如 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control) 建立的 worktree）可以通過檢查；Claude Code 仍然拒絕的情況列在[Claude Code 拒絕使用 worktree](https://code.claude.com/docs/zh-TW/worktrees#claude-code-refuses-to-use-a-worktree) 下及其恢復。有關訊息和如何從每個訊息恢復，請參閱[會話在其 worktree 外恢復](https://code.claude.com/docs/zh-TW/worktrees#the-session-resumes-outside-its-worktree)。 您從何處啟動以及如何恢復會改變 Claude Code 重新進入的內容：

- **啟動目錄** ：從主要檢出或儲存庫的另一個目錄恢復。Claude Code 會重新進入它使用 git 在 `.claude/worktrees/` 下建立的 worktree，即使您從其內部啟動。當您從任何其他 worktree 內部啟動時，Claude Code 只有在能夠從那裡為其擔保時才會重新進入它：一個是其自己的儲存庫的 worktree、一個沒有 git 中繼資料的 worktree，或從您使用 `git worktree add` 建立的 worktree 的子目錄啟動會拒絕，因此請從主要檢出啟動這些。
- **`--fork-session`**：分叉的會話在您啟動 Claude 的目錄中啟動，Claude Code 會保持原始會話的 worktree 不變。
- **已刪除的 worktree** ：如果 worktree 目錄不再存在，Claude Code 會在您啟動 Claude 的目錄中恢復會話。它會告訴您 worktree 已消失並清除會話的 worktree 繫結。

在 v2.1.212 之前，非互動式恢復停留在啟動目錄中，`ExitWorktree` 報告沒有活動的 worktree 會話可退出。 當 Claude 進入或退出 Claude Code 使用 git 建立的 worktree 時，記錄會跟隨：Claude Code 會在會話的新工作目錄下記錄會話，與 [`/cd`](https://code.claude.com/docs/zh-TW/commands) 的方式相同，因此 `/desktop` 和 `--resume` 會在那裡找到它。退出會以相同的方式將其移回。由 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control) 建立的 worktree 會在啟動目錄保留其記錄。需要 Claude Code v2.1.198 或更新版本。

## Claude Code 如何強制隔離

當會話在 worktree 中隔離時，Claude Code 會阻止下面檢查定義的工具呼叫。無論您是使用 `--worktree` 啟動會話、Claude 使用 `EnterWorktree` 進入 worktree，還是恢復 worktree 會話，相同的規則都適用。 相同的強制執行涵蓋 Claude 從隔離會話衍生的每個子代理。它適用於會話是互動式還是在[背景](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)中執行。[在自己的 worktree 中執行的子代理](https://code.claude.com/docs/zh-TW/worktrees#isolate-subagents-with-worktrees)執行相同的檢查。它們的版本歷史記錄在[寫入子代理檔案](https://code.claude.com/docs/zh-TW/sub-agents#write-subagent-files)下。 Claude Code 應用四個檢查：

- **檔案編輯** ：Claude Code 會阻止針對主要檢出中的路徑的 `Edit`、`Write` 或 `NotebookEdit`。
- **命令工作目錄** ：Claude Code 會阻止其工作目錄解析為主要檢出的 Bash、PowerShell 或 Monitor 命令，或其工作目錄無法驗證保持在其外的命令。
- **Git 重定向** ：Claude Code 會阻止將 git 重定向到主要檢出的 Bash 或 Monitor 命令。重定向可以透過 `git -C`、`--git-dir`、`GIT_DIR` 或 `GIT_WORK_TREE` 變數，或在執行 git 之前 `cd` 到主要檢出。
- **命令形狀** ：當 Claude Code 無法從命令文字驗證命令執行的任何 git 保持在 worktree 內時，Claude Code 會阻止 Bash 或 Monitor 命令，例如當命令名稱在執行時計算或語法無法解析時。Claude Code 會告訴 Claude 如何重寫被拒絕的命令，例如將其分割成純粹的、獨立的命令。您無法關閉此檢查。

檢查適用於您啟動 Claude Code 的儲存庫。它們也涵蓋連結 worktree 連結自的主要檢出。對於 PowerShell 命令，Claude Code 只應用工作目錄檢查。 Claude 將每次拒絕視為命名 worktree 並說明如何進行的工具錯誤。

## 使用 worktrees 隔離子代理

子代理可以在自己的 worktrees 中執行，以便平行編輯不會衝突。要求 Claude「為您的代理使用 worktrees」，或通過將 `isolation: worktree` 新增到其 frontmatter 在[自訂子代理](https://code.claude.com/docs/zh-TW/sub-agents#supported-frontmatter-fields)上永久設定它。 `.claude/agents/` 中的此子代理始終在自己的 worktree 中執行：

```
---
name: refactorer
description: Applies mechanical refactors across many files
isolation: worktree
---

Apply the requested refactor across every affected file, then run the tests
and report the results.

```

每個子代理都會獲得一個臨時 worktree，當子代理完成而沒有變更時 Claude Code 會自動移除；具有變更的 worktree 會保留在磁碟上，直到下面的[定期掃描](https://code.claude.com/docs/zh-TW/worktrees#clean-up-subagent-and-background-session-worktrees)可以在不丟失工作的情況下移除它。 子代理 worktrees 使用與 `--worktree` 相同的[基礎分支](https://code.claude.com/docs/zh-TW/worktrees#choose-the-base-branch)，因此它們從您的儲存庫的預設分支分支，除非 `worktree.baseRef` 設定為 `"head"`。

### 清理子代理和背景會話 worktrees

Claude Code 執行定期掃描，移除 Claude 為子代理和[背景會話](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)建立的 worktrees，一旦它們超過您的 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 設定，遵循[保留掃描規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)。 當您[背景](https://code.claude.com/docs/zh-TW/agent-view#send-the-session-to-the-background)一個 `--worktree` 會話時，其 worktree 會變成背景會話 worktree，掃描可以移除。掃描在這些情況下保留 worktree：

- worktree 仍然保留工作：已變更或未追蹤的檔案，或未推送的提交。
- Claude Code 無法確定儲存庫配置定義的篩選驅動程式，或在儲存庫配置中找到它無法關閉的設定，在[四個也阻止 worktree 建立的情況](https://code.claude.com/docs/zh-TW/worktrees#git-lfs-content-is-missing-from-a-worktree-claude-code-created)中的任何一個適用。
- worktree 屬於您未背景的 `--worktree` 會話，無論其年齡如何。
- 您自己使用 `git worktree add` 建立了 worktree，即使您隨後在其中執行了 `--worktree <name>` 會話並背景了該會話。

Claude Code 會將標記寫入它使用 git 建立的每個 worktree 的 git 中繼資料中，掃描會保留任何沒有標記的 worktree，包括 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control) 建立的 worktree。在 v2.1.246 之前，掃描沒有檢查標記，當舊的背景會話記錄指向它時，可能會移除您自己建立的 worktree。 當代理正在執行時，Claude Code 會在其 worktree 上執行 `git worktree lock`，以便並行清理無法將其移除，並在代理完成時釋放鎖定。Claude Code 對為背景會話建立的 worktree 執行相同的鎖定，同時會話執行，因此掃描會保留 worktree 並且 `git worktree remove` 拒絕移除它。 掃描也會釋放 Claude Code 為其程序已退出的會話設定的鎖定，因此被殺死的背景會話不會永久鎖定其 worktree。掃描永遠不會釋放您自己使用 `git worktree lock` 設定的鎖定。在 v2.1.210 之前，被殺死的會話留下的鎖定會保留在原位，直到您執行 `git worktree unlock`。 要清理掃描保留的 worktree，請執行 `git worktree remove`，如果 worktree 有未提交的變更或未追蹤的檔案，請新增 `--force`。如果 git 拒絕因為 worktree 被鎖定，請先在其上執行 `git worktree unlock`。

## 自訂 worktree 建立

Claude Code 的 worktree 建立預設值涵蓋大多數會話：它在 `.claude/worktrees/` 下建立它們，從您的儲存庫的預設分支分支它們，並只檢出追蹤的檔案。本部分中的選項會變更這些預設值。

### 選擇基礎分支

新 worktrees 從儲存庫的預設分支分支，因此大多數會話不需要此設定。在[設定](https://code.claude.com/docs/zh-TW/settings-reference#worktree)中設定 `worktree.baseRef` 以改為從您目前的工作分支。該設定接受兩個值：

- `"fresh"`（預設）：從遠端上的儲存庫預設分支（通常是 `main`）分支，因此 worktree 從與遠端相符的乾淨樹開始。
- `"head"`：從您目前的本地 `HEAD` 分支，因此 worktree 帶有您未推送的提交和功能分支狀態。當隔離需要在進行中的工作上操作的子代理時，請使用此選項。在 worktree 內，`"head"` 解析為該 worktree 的 `HEAD`，而不是主要檢出的。

您無法將 `worktree.baseRef` 設定為分支名稱。要從特定的現有分支啟動 worktree，請[直接使用 git 建立它](https://code.claude.com/docs/zh-TW/worktrees#manage-worktrees-manually)。 對於 `"fresh"` 基礎，Claude Code 會保持 `origin/HEAD` 最新：當儲存庫在過去 24 小時內未被提取時，它會提取預設分支（上限為五秒），如果提取失敗，則使用本地快取的參考。如果未配置遠端，或 `origin/HEAD` 未在本地快取且無法提取，worktree 會回退到您目前的本地 `HEAD`。在 v2.1.208 之前，新 worktree 使用已在本地快取的任何 `origin/HEAD`。 此範例使每個新 worktree 從您目前的工作分支：

```
{
  "worktree": {
    "baseRef": "head"
  }
}

```

### 從拉取請求分支

要從特定的拉取請求或合併請求分支，傳遞 `--worktree` 編號前綴為 `#`、GitHub 拉取請求 URL 或 GitLab 合併請求 URL，例如 `https://gitlab.com/group/repo/-/merge_requests/123`。Claude Code 從 `origin` 提取該變更的頭部提交並在 `.claude/worktrees/pr-<number>` 建立 worktree。引用該引數，以便您的 shell 不會將 `#` 視為註解的開始：

```
claude --worktree "#1234"

```

Claude Code 只從 URL 讀取編號。它始終從您的儲存庫的 `origin` 遠端提取，並按 `origin` 的主機選擇提取路徑：

- **github.com** ：提取 `pull/<number>/head`
- **gitlab.com** ：提取 `merge-requests/<number>/head`
- **GitHub Enterprise、自管理 GitLab 或任何其他主機** ：先嘗試 `pull/<number>/head`，然後 `merge-requests/<number>/head`

在 v2.1.233 之前，Claude Code 只接受 `#<number>` 和 GitHub 風格的拉取請求 URL 用於 `--worktree`，並始終提取 `pull/<number>/head`。

### 將 gitignored 檔案複製到 worktrees

Worktree 是一個新的檢出，因此來自您主要儲存庫的未追蹤檔案（例如 `.env` 或 `.env.local`）不存在。要在 Claude 建立 worktree 時自動複製它們，請將 `.worktreeinclude` 檔案新增到您的專案根目錄。 該檔案使用 `.gitignore` 語法。只有符合模式且也被 gitignored 的檔案才會被複製，因此追蹤的檔案永遠不會被重複。 如果您寫一個以 `**/` 開頭的模式，並且您想要的檔案在一個整體被 gitignored 的目錄內，Claude Code 只有在該目錄本身符合模式時，或當 `**/` 之後的第一個名稱是目錄路徑中的名稱之一時，才會複製它們。例如，如果您寫 `**/.claude/skills/*.md`，該第一個名稱是 `.claude`，因此 Claude Code 會從被忽略的 `.claude/` 目錄複製符合的檔案。要從 `**/` 模式無法到達的被忽略目錄複製檔案，請在模式中命名該目錄：寫 `vendor/**/config.json` 而不是 `**/config.json`。在 v2.1.239 之前，Claude Code 只有在目錄本身符合模式時，才會為 `**/` 模式複製出完全被忽略的目錄中的檔案。 此 `.worktreeinclude` 將兩個環境檔案和一個秘密配置複製到每個新 worktree： .worktreeinclude

```
.env
.env.local
config/secrets.json

```

這適用於 Claude Code 使用 git 建立的每個 worktree：`--worktree` worktrees、[子代理 worktrees](https://code.claude.com/docs/zh-TW/worktrees#isolate-subagents-with-worktrees) 和[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)中的平行會話。使用 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control)，在 hook 指令碼內複製檔案。

### 重複使用 worktree 名稱

傳遞 `--worktree` 一個其目錄已存在的名稱會開啟該現有 worktree，而不是建立新的。 使用預設 `"fresh"` [基礎](https://code.claude.com/docs/zh-TW/worktrees#choose-the-base-branch)，當以下所有條件都成立時，重新開啟的 worktree 會重設為儲存庫的預設分支，而不是在其舊的頂端繼續：

- 它沒有未提交的變更或未追蹤的檔案。
- 它仍在 Claude Code 為其建立的分支上。
- 它沒有自己的提交，或其拉取請求或合併請求已合併且其遠端分支已刪除。

Claude Code 僅從 git 狀態檢測合併的情況：worktree 推送到的遠端分支不再存在，worktree 中的每個提交都已在預設分支上。 在所有其他情況下，Claude Code 會在其舊的頂端重新開啟 worktree：

- worktree 未通過任何條件。
- Claude Code 無法驗證 worktree 的狀態。
- `worktree.baseRef` 是 `"head"`。
- 名稱是拉取請求或合併請求參考。

在 v2.1.208 之前，當您重複使用名稱時，Claude Code 始終在其舊的頂端重新開啟舊 worktree。

### 使用 hook 取代 worktree 建立

配置 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/hooks#worktreecreate) 以完全取代預設的 `git worktree` 邏輯，包括將 worktrees 放在 `.claude/worktrees/` 以外的地方。有關完整範例，請參閱[非 git 版本控制](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control)。

## Worktrees 與主要檢出共享的內容

Worktree 獲得自己的檔案和分支，但它與儲存庫的 `.git` 目錄、專案範圍外掛程式和已儲存的權限批准共享主要檢出：

- **儲存庫的`.git` 目錄**：worktree 中的 git 命令寫入主儲存庫的共享 `.git` 目錄，[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing#filesystem-isolation)允許這些寫入，因此 `git commit` 等命令可以從啟用沙箱的 worktree 內部工作。
- **外掛程式** ：從主要檢出在[專案範圍](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-installation-scopes)安裝的外掛程式也會在同一儲存庫的 worktrees 中載入，因此您不需要為每個 worktree 重新安裝它們。需要 Claude Code v2.1.200 或更新版本。
- **權限批准** ：在 worktree 會話中為 Bash 命令選擇「是，不再詢問」會將規則儲存到主要檢出的 `.claude/settings.local.json`，因此它適用於主要檢出和儲存庫的每個其他 worktree，並在 worktree 移除後存活。在 Windows 和 Claude Code [不使用儲存庫根目錄](https://code.claude.com/docs/zh-TW/settings#where-claude-code-looks-for-each-file)的其他情況下，規則會保留在該 worktree 中。在 v2.1.211 之前，在 worktree 中授予的批准被儲存在該 worktree 內，不適用於其他地方，並在 worktree 移除時丟失。請參閱[批准的儲存位置](https://code.claude.com/docs/zh-TW/permissions#permission-system)。

所有三個都適用於您是使用 `--worktree`、使用 `git worktree add` 還是透過[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)建立 worktree。

## 手動管理 worktrees

當您需要檢出特定的現有分支或將 worktree 放在儲存庫外時，直接使用 Git 建立 worktrees。 在新分支上建立 worktree：

```
git worktree add ../project-feature-a -b feature-a

```

從現有分支建立 worktree，將 `fix-issue-456` 替換為儲存庫中已存在的分支：

```
git worktree add ../project-bugfix fix-issue-456

```

在 worktree 中啟動 Claude：

```
cd ../project-feature-a
claude

```

列出您的 worktrees：

```
git worktree list

```

完成後移除一個：

```
git worktree remove ../project-feature-a

```

有關完整的命令參考，請參閱 [Git worktree 文件](https://git-scm.com/docs/git-worktree)。

## 非 git 版本控制

Worktree 隔離預設使用 git。對於 SVN、Perforce、Mercurial 或其他系統，請配置 [`WorktreeCreate` 和 `WorktreeRemove` hooks](https://code.claude.com/docs/zh-TW/hooks#worktreecreate) 以提供自訂建立和清理邏輯。因為 hook 取代了預設的 git 行為，當您使用 `--worktree` 時，[`.worktreeinclude`](https://code.claude.com/docs/zh-TW/worktrees#copy-gitignored-files-into-worktrees) 不會被處理。改為在您的 hook 指令碼內複製任何本地配置檔案。 此 `WorktreeCreate` hook 從 stdin 使用 `jq` 讀取 worktree 名稱，檢出新的 SVN 工作副本，並列印目錄路徑，以便 Claude Code 可以將其用作會話的工作目錄。將配置新增到您的 [`settings.json`](https://code.claude.com/docs/zh-TW/settings#where-settings-live)：

```
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'NAME=$(jq -r .name); DIR=\"$HOME/.claude/worktrees/$NAME\"; svn checkout https://svn.example.com/repo/trunk \"$DIR\" >&2 && echo \"$DIR\"'"
          }
        ]
      }
    ]
  }
}

```

將其與 `WorktreeRemove` hook 配對以在會話結束時進行清理。有關輸入架構和移除範例，請參閱 [hooks 參考](https://code.claude.com/docs/zh-TW/hooks#worktreecreate)。

## 疑難排解

當 Claude Code 建立 worktree、在啟動時進入一個或將恢復的會話返回到一個時，它會報告以下錯誤。

### Claude Code 無法在啟動時進入 worktree

當 Claude Code 無法在啟動時進入 worktree 目錄時，它會列印一個命名該路徑的錯誤並以代碼 1 退出。當 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/hooks#worktreecreate) 列印它建立的目錄以外的內容，或在設定後刪除目錄時，可能會發生這種情況。

### Worktree 建立在符號連結路徑上失敗

當 `.claude`、`.claude/worktrees` 或 worktree 目錄本身是符號連結時，Claude Code 拒絕建立 worktree，錯誤會命名符號連結路徑。移除符號連結並重試。在 v2.1.212 之前，如果儲存庫已在其中一個路徑上包含已提交的符號連結，worktree 建立會跟隨它，並可能在儲存庫外建立檔案。

### Git LFS 檔案是 Claude Code 建立的 worktree 中的指標檔案

如果您使用 `git lfs install --local` 設定 [Git LFS](https://git-lfs.com)，Claude Code 建立的 worktree 包含 LFS 指標檔案而不是真實檔案。`--local` 旗標將 LFS 篩選寫入儲存庫自己的 `.git/config` 而不是您的全域 git 配置。純粹的 `git lfs install` 寫入您的全域配置，不受影響。相同的適用於儲存庫自己的配置中定義的任何其他[篩選驅動程式](https://git-scm.com/docs/gitattributes)。 Claude Code 在建立 worktree 時會跳過儲存庫自己的篩選驅動程式，因為篩選驅動程式是 shell 命令，任何可以寫入儲存庫的東西（包括 Claude）都可能在那裡放置一個。在 v2.1.247 之前，Claude Code 在 worktree 建立期間執行這些驅動程式。 要獲取真實檔案，請在 worktree 內執行 `git lfs pull`。 在四個罕見的情況下，Claude Code 無法判斷儲存庫的設定定義的篩選驅動程式，或找到它無法關閉的設定，因此根本不建立 worktree。將錯誤與其修復相符：

- **`Could not read the repository git config to neutralize filter drivers`**：Claude Code 無法讀取儲存庫的`.git/config` ，例如因為其權限。修復該問題並重試。
- **`The repository git config defines a filter driver whose name cannot be neutralized (contains "=" or a newline)`**：在`.git/config` 中重新命名或移除該篩選驅動程式並重試。
- **`The repository git config has a conditional include (includeIf)`**：將`includeIf` 在 `.git/config` 中拉入的設定直接移動到該檔案中，移除 `includeIf`，然後重試。您全域 git 配置中的 `includeIf` 不會觸發此問題。
- **`Git was not run: the repository's own git config sets <key>`**：訊息命名一個指向 Git LFS 執行程式的金鑰，例如`lfs.customtransfer.<name>.path` 或 `lfs.standalonetransferagent`。如果該設定是您的，將其移動到您的全域 git 設定。如果您不認識它，請從儲存庫的 git 設定中移除它，因為您不信任的工具或檢出可能已寫入它。金鑰從儲存庫的設定中消失後重試。

### Claude Code 拒絕使用 worktree

以 `Refusing to use <path> as an isolation worktree` 開頭的錯誤意味著 Claude Code 在採用它作為會話或子代理的隔離檢出之前檢查了目錄的 git 身份，並拒絕了它。檢查會執行，無論 Claude Code 是建立 worktree、進入現有的還是重複使用早期執行中的。 在大多數情況下，訊息的其餘部分說目錄的 git 中繼資料解析為主要檢出：例如，其 `.git` 檔案指向主儲存庫自己的 `.git` 目錄，或 git 透過 `core.worktree` 重定向將其工作樹解析為主要檢出。從這樣的目錄，普通的 git 命令（例如 `git reset --hard`）會作用於主要檢出而不是 worktree。Claude Code 也會在目錄有無法讀取的 `.git` 項目時拒絕，而不是假設 worktree 是安全的。 沒有任何 git 中繼資料的目錄（例如您的 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control) 建立的目錄）只有在沒有 git 儲存庫包含它時才會通過檢查。如果 hook 在儲存庫內建立目錄，git 會將其解析為該儲存庫的檢出，Claude Code 會以 `git resolves its working tree to` 訊息拒絕它，因此讓 hook 在任何儲存庫外建立其目錄。 Claude Code 會保留被拒絕的目錄，因為它可能保留工作。將訊息與其恢復相符，無論它跟隨 `Refusing to use <path>` 還是出現在[恢復訊息](https://code.claude.com/docs/zh-TW/worktrees#the-session-resumes-outside-its-worktree)中；某些結尾僅在恢復訊息中出現：

- **說`launch from the parent checkout` 或 `Run the resume from the project checkout`**：您從 worktree 內部啟動了 Claude Code。改為從主要檢出啟動；worktree 不需要重新建立。
- **說`it cannot be resumed or re-entered`** ：此會話中沒有任何東西從您啟動的地方為 worktree 擔保。重新建立它；目錄及其工作保留在磁碟上以供手動恢復，當 worktree 有父檢出時，從那裡恢復也有效。
- **說`it contains the protected checkout`** ：被拒絕的目錄是您主要檢出的父目錄，例如您的主目錄。不要刪除它。變更 worktree 路徑，例如您的 `WorktreeCreate` hook 返回的路徑或 `EnterWorktree` 目標，以便 worktree 不包含檢出。
- **說`the protected checkout <path> has a .git entry that could not be examined` 或 `has git metadata that could not be resolved`**：問題是主要檢出的 git 中繼資料，而不是 worktree 的。不要刪除 worktree，忽略訊息的尾部建議重新建立它，這不適用於這兩個結尾。修復主要檢出，例如權限問題或 git 在其 `.git` 上的 `dubious ownership` 拒絕，然後重試。
- **說`its recorded path has a network spelling`** ：Claude Code 永遠不會恢復到網路路徑上的 worktree。在本地路徑重新建立 worktree。
- **任何其他結尾** ：訊息命名問題及其修復，例如移除 `core.worktree` 重定向或重新建立 worktree；遵循它。在刪除訊息說其 git 身份無法驗證的目錄之前，首先解決命名的原因，例如 worktree 路徑中的符號連結或 git 本身無法執行，因為目錄可能是健康的。當您確實重新建立時，從舊目錄中搶救您需要的任何變更；它保留在磁碟上。

### 會話在其 worktree 外恢復

當您互動式恢復會話且 Claude Code 無法將其返回到其 worktree 時，Claude Code 會使用以下訊息之一說明。當 Claude Code 清除 worktree 繫結時，它會在會話記錄中記錄清除。如果您[抑制記錄寫入](https://code.claude.com/docs/zh-TW/sessions#where-transcripts-are-stored)，訊息改為說無法清除繫結，Claude Code 將在稍後恢復時重新檢查 worktree。

| 訊息開頭                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 發生了什麼以及該怎麼辦                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Your worktree <path> no longer exists`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | worktree 目錄已被移除。會話在目前目錄中繼續，沒有隔離，Claude Code 清除 worktree 繫結。無需採取行動。                                                                                                                                                                                                                                               |
| `Could not verify your worktree <path> this time`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Claude Code 無法驗證 worktree，通常是出於暫時原因；繫結被保留，會話在目前目錄中繼續，沒有隔離。再次恢復以重試；如果它持續發生，在新會話中進入 worktree 並將拒絕訊息與[Claude Code 拒絕使用 worktree](https://code.claude.com/docs/zh-TW/worktrees#claude-code-refuses-to-use-a-worktree) 下的相符，它可以命名主要檢出的中繼資料而不是 worktree 的。 |
| `Did not re-enter your worktree <path>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Claude Code 拒絕 worktree 繫結為不安全；它清除繫結，會話繼續沒有隔離。訊息包括特定拒絕：在[Claude Code 拒絕使用 worktree](https://code.claude.com/docs/zh-TW/worktrees#claude-code-refuses-to-use-a-worktree) 下相符，因為修復對某些拒絕是重新建立，對其他拒絕是路徑變更。                                                                          |
| `Could not re-enter your worktree <path>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Claude Code 無法從您啟動的地方為 worktree 擔保，最常見的是因為您從其內部啟動；繫結被保留。訊息的其餘部分命名修復；在[Claude Code 拒絕使用 worktree](https://code.claude.com/docs/zh-TW/worktrees#claude-code-refuses-to-use-a-worktree) 下相符。                                                                                                    |
| 在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p`，以及 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/sessions) 執行的恢復，Claude Code 會停止恢復，除了消失的 worktree 外，每次拒絕都會在 stderr 上出現錯誤，而不是繼續沒有隔離。 使用 `--output-format stream-json`，拒絕也會在 stdout 上作為 `result` 訊息到達，子類型 `error_during_execution`，其 `errors` 陣列帶有相同的文字，因此 Agent SDK 應用程式會收到原因而不僅僅是非零退出。在 v2.1.260 之前，worktree 恢復拒絕沒有產生 `result` 訊息。 訊息採用與表中互動式訊息不同的形狀： |                                                                                                                                                                                                                                                                                                                                                     |

- `Error: cannot resume into worktree <path>: ...This session was not started.` 對於表顯示為 `Did not re-enter` 的拒絕。Claude Code 在退出前清除 worktree 繫結，錯誤說明了這一點；下次您恢復對話時，會話在目前目錄中繼續，沒有 worktree 隔離。在 v2.1.260 之前，Claude Code 沒有寫入清除的繫結，因此同一恢復的每次重試都以相同的錯誤失敗。 如果您[抑制記錄寫入](https://code.claude.com/docs/zh-TW/sessions#where-transcripts-are-stored)，清除無法被儲存。錯誤然後說相同的命令將再次被拒絕，並命名 `--fork-session` 和啟動新對話作為在沒有 worktree 的情況下繼續的方式。
- `Error: could not verify worktree <path> for this resume, so the resume was aborted...` 對於 `Could not verify`
- `Error: ...The worktree binding is kept.` 對於 `Could not re-enter`
- `Notice: the worktree <path> for this session no longer exists...` 對於消失的 worktree；Claude Code 列印它並繼續會話，如互動式恢復所做的

嵌入在每個錯誤中的拒絕結尾與互動式通知共享，因此它仍然與[Claude Code 拒絕使用 worktree](https://code.claude.com/docs/zh-TW/worktrees#claude-code-refuses-to-use-a-worktree) 下的其項目相符。 在 stream-json 結果中，[`startup_failure_reason`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#startup_failure_reason) 對於 `could not verify worktree` 錯誤是 `worktree_unverified`，對於 `cannot resume into worktree` 和 `The worktree binding is kept` 錯誤是 `worktree_resume_refused`。應用程式可以在其上分支，而不是匹配錯誤文字。在 v2.1.274 之前，結果沒有 `startup_failure_reason` 欄位。

## 另請參閱

Worktrees 處理檔案隔離。下面的相關頁面涵蓋將工作委派到這些隔離的檢出中、在它們之間傳遞發現以及在您建立的會話之間切換：

- [子代理](https://code.claude.com/docs/zh-TW/sub-agents)：在會話內將工作委派給隔離的代理
- [跨會話訊息傳遞](https://code.claude.com/docs/zh-TW/cross-session-messaging)：讓您的 worktrees 中的會話相互傳遞發現
- [代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)：自動協調多個 Claude 會話
- [管理會話](https://code.claude.com/docs/zh-TW/sessions)：命名、恢復和在對話之間切換
- [桌面平行會話](https://code.claude.com/docs/zh-TW/desktop#work-in-parallel-with-sessions)：桌面應用程式中由 worktree 支援的會話

是否 助手
