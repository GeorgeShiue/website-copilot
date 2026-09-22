動態工作流程在所有付費方案上可用，具有 Anthropic API 存取權限，以及在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上可用。在 Pro 上，從 `/config` 中的 Dynamic workflows 列啟用它們。 動態工作流程是一個 JavaScript 指令碼，可大規模協調許多[子代理](https://code.claude.com/docs/zh-TW/sub-agents)。Claude 為您描述的任務編寫指令碼，執行時期在背景執行它，同時您的工作階段保持回應。 當任務需要超過一個對話可以協調的代理數量時，或當您想將協調編成可以讀取和重新執行的指令碼時，請使用工作流程。範例包括程式碼庫範圍的錯誤掃描、500 個檔案遷移、需要相互交叉檢查來源的研究問題，以及值得從多個獨立角度起草的困難計畫，然後再提交給其中一個。

## 何時使用工作流程

[子代理](https://code.claude.com/docs/zh-TW/sub-agents)、[技能](https://code.claude.com/docs/zh-TW/skills)、[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)和工作流程都可以執行多步驟任務。區別在於誰掌握計畫：

|                                                                                                                                                                                                                                                                                                                                                                                                                      | 子代理              | 技能                | 代理團隊                   | 工作流程                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------------------- | ------------------------ |
| 它是什麼                                                                                                                                                                                                                                                                                                                                                                                                             | Claude 生成的工作者 | Claude 遵循的指示   | 監督對等工作階段的主導代理 | 執行時期執行的指令碼     |
| 誰決定接下來執行什麼                                                                                                                                                                                                                                                                                                                                                                                                 | Claude，逐輪        | Claude，遵循提示    | 主導代理，逐輪             | 指令碼                   |
| 中間結果在哪裡                                                                                                                                                                                                                                                                                                                                                                                                       | Claude 的上下文視窗 | Claude 的上下文視窗 | 共享任務清單               | 指令碼變數               |
| 什麼是可重複的                                                                                                                                                                                                                                                                                                                                                                                                       | 工作者定義          | 指示                | 團隊定義                   | 協調本身                 |
| 規模                                                                                                                                                                                                                                                                                                                                                                                                                 | 每輪委派的幾項任務  | 與子代理相同        | 少數長時間執行的對等代理   | 每次執行數十到數百個代理 |
| 中斷                                                                                                                                                                                                                                                                                                                                                                                                                 | 重新啟動輪次        | 重新啟動輪次        | 隊友繼續執行               | 在同一工作階段中可恢復   |
| 工作流程將計畫移入程式碼。使用子代理、技能和代理團隊，Claude 是協調者：它逐輪決定接下來要生成或指派什麼，每個結果都進入上下文視窗。工作流程指令碼保存迴圈、分支和中間結果本身，因此 Claude 的上下文只保存最終答案。 將計畫移入程式碼也讓工作流程應用可重複的品質模式，而不僅僅是執行更多代理：它可以讓獨立代理在報告前對彼此的發現進行對抗性審查，或從多個角度起草計畫並相互權衡，因此您獲得比單次通過更可信的結果。 |                     |                     |                            |                          |

## 執行捆綁的工作流程

查看工作流程運作的最快方式是執行 `/deep-research`，[內建工作流程](https://code.claude.com/docs/zh-TW/workflows#bundled-workflows)Claude Code 包含用於跨許多來源調查問題。您將看到代理在背景中完成一組階段，同時您的工作階段保持自由，最後獲得一份報告而不是逐輪記錄。 1 執行工作流程 使用您想調查的問題執行 `/deep-research`。它在多個角度上展開網路搜尋，獲取並交叉檢查它找到的來源，並合成引用的報告。

```
/deep-research What changed in the Node.js permission model between v20 and v22?

```

2 允許工作流程 Claude Code 詢問是否允許工作流程。選擇**是** 以繼續。確切的提示取決於您的權限模式。有關每種模式選項，請參閱[在執行前批准計畫](https://code.claude.com/docs/zh-TW/workflows#approve-the-plan-before-it-runs)。 3 監視進度 執行在背景中啟動。執行 `/workflows`，使用箭頭鍵選擇執行，然後按 Enter 開啟其進度檢視：

```
/workflows

```

檢視顯示每個階段及其代理計數、令牌總計和經過時間。深入任何階段以查看其代理及每個代理發現的內容。有關完整的控制集，請參閱[監視執行](https://code.claude.com/docs/zh-TW/workflows#watch-the-run)。您也可以從輸入框下方的任務面板監視：執行進行時會出現一行進度摘要。按向下箭頭聚焦它，然後按 Enter 展開。 4 閱讀報告 執行完成後，報告進入您的工作階段。它引用每項聲明來自的來源，未通過交叉檢查的聲明已被篩選出去。當驗證代理無法檢查聲明時（例如在速率限制或 API 錯誤之後），報告會將該聲明列為未驗證，而不是計為駁回。 要為您自己的任務執行工作流程，[讓 Claude 編寫一個](https://code.claude.com/docs/zh-TW/workflows#have-claude-write-a-workflow)，一旦執行執行您想要的操作，您可以[儲存它](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)作為您自己的命令。

### 捆綁的工作流程

Claude Code 包含 `/deep-research` 作為內建工作流程：

| 命令                                                                                                                                                                                              | 它做什麼                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/deep-research <question>`                                                                                                                                                                       | 在多個角度上展開網路搜尋問題，獲取並交叉檢查它找到的來源，對每項聲明進行投票，並返回引用的報告，其中未通過交叉檢查的聲明已被篩選出去。需要 [WebSearch 工具](https://code.claude.com/docs/zh-TW/tools-reference#websearch-tool-behavior)可用 |
| `/deep-research` 僅在您叫用時執行。 [您自己儲存的工作流程](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)以相同方式成為命令，並在 `/` 自動完成中與捆綁的命令一起出現。 |                                                                                                                                                                                                                                             |

### 監視執行

工作流程在背景中執行，因此工作階段在代理工作時保持回應。隨時執行 `/workflows` 以列出執行中和已完成的工作流程，然後選擇一個以開啟其進度檢視。 進度檢視顯示每個階段及其代理計數、令牌總計和經過時間。頁腳列出每個動作的鍵：

| 鍵                                                                                                                                                                                                                                                             | 動作                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `↑` / `↓`                                                                                                                                                                                                                                                      | 選擇階段或代理                                                                                       |
| `Enter` 或 `→`                                                                                                                                                                                                                                                 | 深入選定的階段，然後進入代理的詳細資訊。在詳細資訊中，`Enter` 展開或摺疊它                           |
| `Esc` 或 `←`                                                                                                                                                                                                                                                   | 返回一個級別。在 v2.1.203 至 v2.1.205 中，`←` 未步出階段或代理；在這些版本上使用 `Esc`               |
| `j` / `k`                                                                                                                                                                                                                                                      | 當代理詳細資訊溢出時在其中捲動                                                                       |
| `f`                                                                                                                                                                                                                                                            | 按狀態篩選選定階段中的代理清單。再次按以循環                                                         |
| `p`                                                                                                                                                                                                                                                            | 暫停或恢復執行                                                                                       |
| `x`                                                                                                                                                                                                                                                            | 停止選定的代理，或當焦點在執行上時停止整個工作流程                                                   |
| `r`                                                                                                                                                                                                                                                            | 重新啟動選定的執行中代理                                                                             |
| `s`                                                                                                                                                                                                                                                            | [儲存](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)執行的指令碼作為命令 |
| 代理詳細資訊列出代理的提示、其最近的工具呼叫和其結果。每個呼叫顯示其狀態，例如仍在執行或失敗。當代理保持自己的任務清單時，詳細資訊會顯示它，以及每個任務的狀態。 按 `Enter` 展開詳細資訊。提示和結果隨後會完整顯示，每個列出的呼叫會顯示其輸入和其結果的開始。 |                                                                                                      |

## 讓 Claude 編寫工作流程

您可以通過兩種方式讓 Claude 為您的任務編寫工作流程：

- [在您的提示中要求工作流程](https://code.claude.com/docs/zh-TW/workflows#ask-for-a-workflow-in-your-prompt)，使用關鍵字 `ultracode`，Claude 為任務編寫一個。
- [讓 Claude 使用 ultracode 決定](https://code.claude.com/docs/zh-TW/workflows#let-claude-decide-with-ultracode)：設定 `/effort ultracode`，Claude 為工作階段中的每項實質性任務規劃工作流程。

您也可以執行已存在的工作流程命令：[捆綁的工作流程](https://code.claude.com/docs/zh-TW/workflows#bundled-workflows)如 `/deep-research`，或您[儲存的](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)工作流程。

### 在您的提示中要求工作流程

要在不改變工作階段努力級別的情況下將單個任務作為工作流程執行，請在提示中包含關鍵字 `ultracode`。用您自己的話提問，例如「使用工作流程」或「執行工作流程」，也可以：Claude 將直接請求視為相同的選擇加入。

```
ultracode: audit every API endpoint under src/routes/ for missing auth checks

```

Claude Code 在您的輸入中突出顯示該關鍵字，Claude 為任務編寫工作流程指令碼，而不是逐輪完成它。該關鍵字只選擇 Claude 如何組織工作：代理的工具呼叫接收與工作階段中任何其他工具呼叫相同的權限檢查和[沙箱隔離](https://code.claude.com/docs/zh-TW/sandboxing)。 如果執行執行您想要的操作，您可以之後[將其儲存為命令](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)。如果您已經以另一種方式建立了協調器，例如子代理提示的資料夾或一個分散工作的技能，您可以指向 Claude 並要求工作流程執行相同的操作。

#### 忽略或關閉關鍵字

如果您沒有打算啟動工作流程，請在 macOS 上按 `Option+W` 或在 Windows 和 Linux 上按 `Alt+W` 以忽略此提示的突出顯示，或在游標位於突出顯示關鍵字的正後方時按退格鍵。要停止該關鍵字完全觸發，請在 `/config` 中關閉 Ultracode keyword trigger。

#### 關鍵字在何處有效

該關鍵字是一個選擇加入，僅在您自己輸入的提示中有效：在互動式提示、IDE 擴充面板、[Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 用戶端，或在 Agent SDK 應用程式中，該應用程式將您的鍵盤輸入的 [`origin`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#sdkmessageorigin) 標記為 `{ kind: "human" }`。當提示以另一種方式進入工作階段時，它不會啟動工作流程：

- 使用 `-p` 傳遞的提示
- Agent SDK 應用程式發送的提示，未將其標記為人類輸入
- 排程任務提示
- 轉發到對話中的 webhook 負載或拉取請求評論

在 v2.1.210 之前，該關鍵字也從這些路由中的任何一個啟動工作流程，包括轉發到對話中的 webhook 負載或拉取請求評論。

### 讓 Claude 使用 ultracode 決定

Ultracode 是一個 Claude Code 設定，結合 `xhigh` [推理努力](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)與自動工作流程協調。啟用它後，Claude 為每項實質性任務規劃工作流程，而不是等待您要求。

```
/effort ultracode

```

要啟動已啟用 ultracode 的工作階段，請使用 `claude --effort ultracode` 啟動。需要 Claude Code v2.1.203 或更新版本。 要在您選擇模型時啟用它，使用箭頭鍵將 `/model` 選擇器的努力滑塊移動到 `ultracode`。[調整努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)列出啟用 ultracode 的路由。 啟用 ultracode 後，Claude 決定任務何時值得工作流程。單個請求可以變成一系列工作流程：一個用於理解程式碼，一個用於進行更改，一個用於驗證它。這適用於工作階段中的每項任務，因此每個請求使用更多令牌並花費比較低努力級別更長的時間。 `/effort ultracode` 持續當前工作階段；要讓每個工作階段都以它開始，設定 [`ultracode`](https://code.claude.com/docs/zh-TW/settings-reference#ultracode) 設定。當您返回日常工作時，使用 `/effort high` 下降。它在支援 `xhigh` [努力](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)的模型上可用；在其他模型上，`/effort` 功能表不提供它。

### 在執行前批准計畫

在 CLI 中，每次執行提示顯示計畫的階段和這些選項：

- **是，執行它** ：啟動執行
- **是，不再詢問`<name>` 在 `<path>` 中**：啟動，並從現在開始跳過此專案中此工作流程的此提示。Claude Code 在您按名稱執行捆綁、儲存或外掛工作流程時提供此選項，而不是針對 Claude 為當前任務編寫的指令碼。
- **檢視原始指令碼** ：在決定前讀取指令碼
- **否** ：取消

`Ctrl+G` 在您的編輯器中開啟指令碼。`Tab` 讓您在執行啟動前調整提示。 您是否看到此提示取決於您的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)：

| 權限模式                                                                                                                                                                                                                                                                                                                                                      | 何時提示您                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 自動                                                                                                                                                                                                                                                                                                                                                          | 首次啟動。任何**是** 在您的使用者設定中記錄同意，稍後啟動無需提示即可啟動。當 ultracode 啟用時完全跳過 |
| 手動、接受編輯                                                                                                                                                                                                                                                                                                                                                | 每次執行，除非您已為此專案中的該工作流程選擇**是，不再詢問**                                           |
| 繞過權限                                                                                                                                                                                                                                                                                                                                                      | Claude Code 不提示您。執行立即啟動                                                                     |
| `claude -p`、Agent SDK                                                                                                                                                                                                                                                                                                                                        | Claude Code 不提示您                                                                                   |
| 在 `claude -p` 和 Agent SDK 中，Claude Code 永遠不會顯示此提示。它通過與工作階段其餘部分相同的[權限評估](https://code.claude.com/docs/zh-TW/agent-sdk/permissions#how-permissions-are-evaluated)執行 Workflow 工具呼叫，因此拒絕規則、詢問規則和 `dontAsk` 模式適用於啟動，就像它們適用於每個工具呼叫一樣。要讓工作流程在這些執行中啟動，請使用以下其中之一： |                                                                                                        |

- **權限規則** ：您允許規則中的 `Workflow` 批准每個工作流程，`Workflow(<name>)` 按名稱批准一個儲存的工作流程。
- **自動權限模式** ：[分類器](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)審查呼叫並可以批准它。
- **繞過權限模式** ：Claude Code 批准呼叫。
- **`PreToolUse`鉤子** ：為呼叫返回 `allow` 的[鉤子](https://code.claude.com/docs/zh-TW/hooks#pretooluse)批准它。
- **您的主機** ：[`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)批准它，或使用 Agent SDK，[`canUseTool`](https://code.claude.com/docs/zh-TW/agent-sdk/permissions)回呼或[`PermissionRequest` 鉤子](https://code.claude.com/docs/zh-TW/hooks#permissionrequest)批准它。

在桌面應用程式中，批准卡顯示工作流程名稱、階段列表和令牌使用警告，具有**一次** 、**始終** 和**拒絕** 動作。進度檢視出現在背景任務側窗格中。 工作流程生成的子代理使用您的[權限規則](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings)，Claude Code 根據[子代理執行的權限模式](https://code.claude.com/docs/zh-TW/sub-agents#permission-modes)下的規則選擇其權限模式。要在長時間執行時避免提示，請在啟動前將代理需要的工具新增到您的允許規則。

### 儲存工作流程以供重複使用

當 Claude 為您將重複的任務編寫工作流程時，您可以將該執行的指令碼儲存為命令。一個您在每個分支上執行的審查流程然後每次執行相同的協調。 執行 `/workflows`，選擇您想保留的執行，然後按 `s`。在儲存對話中，Tab 在兩個儲存位置之間切換：

- `.claude/workflows/` 在您的專案中：與克隆儲存庫的每個人共享
- `~/.claude/workflows/` 在您的主目錄中：在每個專案中可用，僅對您可見。如果您設定了 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars)，此位置是該路徑下的 `workflows/` 目錄。

儲存對話顯示個人位置的已解析路徑。 按 Enter 儲存。工作流程在未來工作階段中從任一位置作為 `/<name>` 執行。 Claude Code 在寫入前檢查儲存位置是否有符號連結，並顯示錯誤而不是通過一個寫入。它檢查的內容取決於您儲存的位置：

- 專案位置：如果 `.claude`、`.claude/workflows` 或目標檔案是符號連結，Claude Code 拒絕。
- 個人位置：Claude Code 只有在目標檔案本身是符號連結時才拒絕，因此由 dotfiles 工具管理的 `~/.claude` 目錄仍然有效。

在 v2.1.216 之前，Claude Code 跟隨連結，這可能會將檔案放在您選擇的位置之外。 在具有多個 `.claude/` 目錄的 monorepo 中，您可以將工作流程保留在它們適用的套件旁邊。自 v2.1.178 起，儲存到專案位置會寫入您的工作目錄和儲存庫根目錄之間已存在的最接近的 `.claude/workflows/` 目錄，或如果尚不存在則寫入儲存庫根目錄。專案工作流程也從該路徑沿著的每個 `.claude/workflows/` 載入，當多個定義相同名稱時 Claude Code 執行最接近工作目錄的那個。 如果專案工作流程和個人工作流程共享名稱，則執行專案工作流程。

### 在外掛中分發工作流程

要在團隊或儲存庫之間共享工作流程，請將其包含在[外掛](https://code.claude.com/docs/zh-TW/plugins)中。將指令碼放在外掛根目錄的 `workflows/` 目錄中，或使用 [`workflows` 清單欄位](https://code.claude.com/docs/zh-TW/plugins-reference#component-path-fields)指向不同的位置。 外掛工作流程由外掛名稱命名空間。一個名為 `acme-tools` 的外掛，其中包含 `meta.name` 為 `release-audit` 的指令碼，執行為 `/acme-tools:release-audit`。

### 將輸入傳遞給已儲存的工作流程

已儲存的工作流程可以通過 `args` 參數接受輸入。指令碼將其讀取為名為 `args` 的全域變數。使用此功能在調用時提供研究問題、目標路徑清單或配置物件，而不是為每次執行編輯指令碼。 以下提示使用問題編號清單執行已儲存的工作流程：

```
Run /triage-issues on issues 1024, 1025, and 1030

```

Claude 將清單作為結構化資料傳遞，因此指令碼可以直接在 `args` 上呼叫陣列和物件方法，無需先解析它。如果省略 `args`，全域變數在指令碼內為 `undefined`。

## 工作流程提示範例

工作流程最適合當任務大於一個代理可以在上下文中保存的情況，或當相同的步驟需要在許多項目上執行時。下面的提示顯示常見的形狀。每一個都要求 Claude 為該任務編寫並執行工作流程；您不自己編寫指令碼。

### 審計許多檔案以查找相同問題

展開每個檔案一個代理，然後收集並驗證發現。

```
use a workflow to audit every route handler under src/routes/ for missing authentication checks, and adversarially verify each finding before reporting it

```

### 持續修復直到檢查通過

執行檢查器、修復失敗的內容，並重複直到通過或停止進展。

```
use a workflow to run npx tsc --noEmit and keep fixing the reported errors until the type check passes or two rounds in a row make no progress

```

### 並行遷移許多檔案

發現要遷移的檔案，在隔離的副本中轉換每個檔案，以便編輯不衝突，並驗證每個結果。

```
use a workflow to migrate every component under src/components/ from JavaScript to TypeScript, working on each file in its own isolated copy

```

### 審查每個更改的檔案並寫一份摘要

為每個檔案執行審查者，然後將所有發現交給一個代理，該代理對它們進行排名和去重。

```
use a workflow to review every file changed in this PR for correctness issues, then merge the per-file findings into one ranked summary

```

### 跨許多來源研究主題

在變更日誌、問題和文件中展開讀者，然後合成。捆綁的 `/deep-research` 工作流程執行此操作；您也可以描述更狹隘的版本。

```
use a workflow to research how our three competitors handle rate limiting: read their public docs and recent changelog entries in parallel, then compare the approaches

```

### 查找問題直到清單停止增長

持續搜尋並在新輪次發現沒有新內容時停止。

```
use a workflow to find flaky tests in this repo: run the suite repeatedly, record which tests fail intermittently, and stop once two rounds in a row find nothing new

```

### 已儲存的指令碼看起來像什麼

當您[儲存工作流程](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)時，`.claude/workflows/` 中的檔案保存一個 `meta` 塊，後面跟著協調子代理的指令碼主體。您通常不需要編輯它，但這是一個小的形狀，以便您可以識別 Claude 生成的內容：

```
export const meta = {
  name: 'audit-routes',
  description: 'Audit every route handler for missing auth checks',
}

const found = await agent('List every .ts file under src/routes/.', {
  schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } },
})

const audits = await pipeline(found.files, file =>
  agent(`Audit ${file} for missing authentication checks.`, { label: file }),
)

return audits.filter(Boolean)

```

主體是具有頂級 `await` 的純 JavaScript。`agent()` 生成一個子代理，`pipeline()` 為清單中的每個項目執行一個，而 `parallel()` 同時執行一組代理任務並等待所有任務完成。 如果您停止 `agent()` 呼叫中途或它遇到無法恢復的 API 錯誤，該呼叫會解析為 `null`。在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)中，分類器可以在子代理啟動之前阻止 `agent()` 呼叫。被阻止的呼叫會解析為 `null` 並在執行的進度檢視中顯示原因。`pipeline()` 在結果陣列中保留每個 `null`，這就是為什麼範例以 `.filter(Boolean)` 結尾以刪除這些項目。 如果您在 `agent()` 呼叫上傳遞 `schema`，該子代理會傳回與形狀相符的 JSON 而不是散文。Claude Code 在啟動子代理之前檢查架構：當它可以證明架構自相矛盾時，呼叫會失敗並出現錯誤，命名矛盾，子代理永遠不會啟動。它可以證明的一個矛盾是 `additionalProperties: false` 排除的 `required` 鍵。 如果子代理的輸出在五次嘗試後仍然無法通過驗證，呼叫會失敗並出現包含最後驗證失敗的錯誤。若要變更嘗試次數，請設定 [`MAX_STRUCTURED_OUTPUT_RETRIES`](https://code.claude.com/docs/zh-TW/env-vars)。

### 編輯已儲存的指令碼

若要變更[您儲存的工作流程](https://code.claude.com/docs/zh-TW/workflows#save-the-workflow-for-reuse)，請編輯其 `.js` 檔案或要求 Claude 進行變更。在您編輯或要求之前，執行 `/workflow-authoring` [捆綁技能](https://code.claude.com/docs/zh-TW/skills#bundled-skills)以載入 Claude 工作的指令碼編寫參考。該技能需要 Claude Code v2.1.248 或更新版本。 若要在目前工作階段中執行編輯版本，執行 [`/reload-skills`](https://code.claude.com/docs/zh-TW/commands#all-commands) 以重新讀取工作流程目錄，然後再次執行 `/<name>`。 Claude Code 在載入和執行指令碼時對檔案的每個部分應用這些規則：

- **`meta`塊** ：將 `export const meta` 保留為第一個陳述式，並將其保留為具有 `name` 和 `description` 的純物件字面值。如果它包含除字面值以外的任何內容，例如變數、函式呼叫或展開，Claude Code 會從 `/` 自動完成中刪除 `/<name>`。
- **主體** ：除了 `agent()`、`pipeline()` 和 `parallel()` 之外，您可以呼叫 `phase()` 以在進度檢視中將後續代理分組到標題下，呼叫 `log()` 以在階段上方顯示訊息，並讀取 [`args`](https://code.claude.com/docs/zh-TW/workflows#pass-input-to-a-saved-workflow) 全域。如果主體有語法錯誤，Claude Code 會在您執行工作流程時報告它。
- **`phases`**：如果您在`meta` 中列出它們，請為每個項目提供您傳遞給 `phase()` 的確切標題。沒有項目的 `phase()` 標題會獲得自己的進度群組。
- **時間戳記和隨機性** ：Claude Code 使 `Date.now()`、`Math.random()` 和無引數 `new Date()` 在指令碼內拋出，以便[重新啟動的執行](https://code.claude.com/docs/zh-TW/workflows#resume-after-a-pause)重複相同的 `agent()` 呼叫。改為透過 `args` 傳遞時間戳記。

您也可以編輯[單次執行的指令碼](https://code.claude.com/docs/zh-TW/workflows#how-a-workflow-runs)而不是已儲存的副本。[在暫停後繼續](https://code.claude.com/docs/zh-TW/workflows#resume-after-a-pause)涵蓋當您重新啟動編輯的指令碼時哪些代理再次執行。如需 Workflow 工具的輸入，請參閱其在 [Agent SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#workflow)中的項目。

## 工作流程如何執行

工作流程執行時期在隔離環境中執行指令碼，與您的對話分開。中間結果保留在指令碼變數中，而不是進入 Claude 的上下文。 每次執行都會將其指令碼寫入您工作階段目錄下的 `~/.claude/projects/` 中的檔案。執行開始時 Claude 會收到該路徑，因此您可以要求它。您可以開啟該檔案以讀取 Claude 編寫的協調指令碼，將其與先前執行的指令碼進行比較，或編輯它並要求 Claude 從編輯後的版本重新啟動。 Claude 只能從工作階段已允許讀取的指令碼檔案啟動工作流程。若要執行保存在工作目錄外的指令碼，請先使用 [`/add-dir`](https://code.claude.com/docs/zh-TW/permissions#working-directories) 或 [Read 允許規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)新增其目錄。 執行時期在執行進行時追蹤每個代理的結果，這是使執行在同一工作階段中[可恢復](https://code.claude.com/docs/zh-TW/workflows#resume-after-a-pause)的原因。

### 扇出中的提示快取

同一執行中的代理可以讀取彼此的[提示快取](https://code.claude.com/docs/zh-TW/prompt-caching#subagents-and-the-cache)。使用相同模型、努力等級、代理類型、工具、輸出架構和工作目錄執行的兩個代理會建立相同的工具和系統提示前綴，因此在匹配同級代理的回應開始後啟動的代理會在其第一個請求上讀取該同級代理的快取。 工作流程代理的請求不在主對話的[快取 TTL 時段](https://code.claude.com/docs/zh-TW/prompt-caching#which-ttl-each-request-gets)內，因此其快取預設保留五分鐘，包括在 Claude 訂閱上。若要將其保留一小時，請將 [`subagentPromptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#subagentpromptcachettl) 設定為 `1h`。API 以更高的費率計費 1 小時快取寫入。 當扇出同時啟動多個匹配的代理時，Claude Code 會保留除第一個外的所有代理，直到第一個代理的回應開始，然後一起釋放保留的代理，以便它們的第一個請求讀取共享前綴，而不是每個都未快取地處理它。Claude Code 將保留時間上限設定為 [`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`](https://code.claude.com/docs/zh-TW/env-vars) 毫秒，預設為 `5000`。將其設定為 `0` 以停用保留。

### 行為和限制

執行時期應用以下約束：

| 約束                                                                                                                                                                                                                                                                   | 為什麼                                                                                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 無中途使用者輸入                                                                                                                                                                                                                                                       | 執行只會因代理權限提示和[使用量限制等待](https://code.claude.com/docs/zh-TW/workflows#when-a-run-hits-your-usage-limit)而暫停。對於階段之間的簽核，將每個階段作為其自己的工作流程執行 |
| 無來自工作流程本身的直接檔案系統或 shell 存取                                                                                                                                                                                                                          | 代理讀取、寫入和執行命令。指令碼協調代理                                                                                                                                              |
| 無模組載入：包含 `import()` 的指令碼在執行開始前會失敗                                                                                                                                                                                                                 | 指令碼主體是純 JavaScript。將需要程式庫的工作放在代理的任務中                                                                                                                         |
| 最多 16 個並行代理，在 Claude Code 可用 CPU 較少時更少，包括在 CPU 受限的容器內。若要變更限制，請將 [`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`](https://code.claude.com/docs/zh-TW/env-vars#variables) 設定為 1 到 256 的值，這需要 Claude Code v2.1.269 或更新版本 | 限制本地資源使用                                                                                                                                                                      |
| 在扇出中，共享第一個代理提示快取前綴的代理預設在其後最多啟動 5 秒                                                                                                                                                                                                      | 除第一個外的所有代理都讀取[第一個代理快取的前綴](https://code.claude.com/docs/zh-TW/workflows#prompt-caching-in-a-fan-out)，而不是每個都未快取地處理它                                |
| 單一 `parallel()` 或 `pipeline()` 呼叫中最多 4,096 個項目：執行時期會以錯誤拒絕更長的清單                                                                                                                                                                              | 無聲上限會在不告知指令碼的情況下丟棄部分工作負載                                                                                                                                      |
| 每次執行 1,000 個代理                                                                                                                                                                                                                                                  | 防止失控迴圈                                                                                                                                                                          |

## 管理執行

執行啟動後，您從 `/workflows` 檢視或通過展開輸入框下方任務面板中的進度線來管理它。 當您停止執行時，它會保留在任務面板中，而其任何代理的程序仍在執行。如果您再次停止它，Claude Code 會重新向這些程序發送信號。

### 暫停後恢復

從 `/workflows` 恢復暫停的執行，方法是選擇它並按 `p`。對於您停止的執行，要求 Claude 使用相同指令碼重新啟動工作流程。如果已停止執行中的代理尚未退出，Claude Code 會拒絕重新啟動，直到它們退出為止，因此這些代理的第二個副本無法與它們並行執行。 Claude Code 按代理啟動的順序重新執行該執行，每個代理要麼返回其已保存的結果，要麼再次執行：

- **已完成** ：返回其已保存的結果。第一個提示與前次執行不同的代理（因為您編輯了指令碼或較早的代理返回了不同的內容）會再次執行，之後的每個代理也會執行，即使是已完成的代理。
- **停止時仍在執行** ：重新開始。停止整個執行不會將任何代理計為失敗。
- **失敗** ：再次執行，之後啟動的每個代理也會執行，即使是已完成的代理。通過在 [`/workflows`](https://code.claude.com/docs/zh-TW/workflows#watch-the-run) 中選擇代理並按 `x` 來單獨停止一個代理，會將其計為失敗。

最後一種情況意味著中間的失敗會重新執行已完成的工作。如果指令碼按該順序啟動 A、B、C 和 D，並且 B 失敗，重新啟動會從快取返回 A 並再次執行 B、C 和 D。 您可以在同一 Claude Code 工作階段內恢復執行。當您離開工作階段時，執行中的工作流程會發生什麼取決於您如何離開：

- 如果您[將工作階段放在背景](https://code.claude.com/docs/zh-TW/agent-view#what-carries-over-when-you-background)，Claude Code 會在背景工作階段中以相同方式重新執行該執行並繼續它。
- 如果您在工作流程執行時退出 Claude Code 並且[代理檢視已開啟](https://code.claude.com/docs/zh-TW/agent-view#from-inside-a-session)，退出對話框會提供 `Move to background and exit`，它以相同方式帶過該執行。如果您改為選擇 `Exit and stop tasks`，或未提供該選項，執行會隨工作階段停止。Claude Code 將執行的已保存結果保留在 `~/.claude/projects/` 中該工作階段的目錄下，因此您使用 `claude --resume` 恢復的工作階段可以在您要求 Claude 重新啟動工作流程時重新執行它們。在您全新啟動的工作階段中，Claude 沒有較早的執行可重新啟動，並將工作流程作為新執行啟動。

在[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)中，Claude Code 也會將執行的結果與工作階段的對話歷史記錄一起保存，當工作階段的 VM 被回收時，這些結果會保留。當您[重新開啟此類工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#environment-expired)並要求 Claude 重新啟動工作流程時，已完成的代理仍會返回其已保存的結果。 在本地和雲端工作階段中，當 Claude 重新啟動較早的執行並且 Claude Code 根本找不到該執行的已保存結果時，重新啟動會失敗並出現 `nothing to resume` 錯誤，而不是自動啟動執行。要求 Claude 將工作流程作為新執行啟動。

### 當執行達到您的使用限制時

當代理達到您的 claude.ai [使用限制](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)時，執行會暫停而不是該代理失敗：達到限制的代理會等待重設，並且不會啟動新代理。限制重設後不久，等待中的代理會再次執行，執行會自動繼續。需要 Claude Code v2.1.271 或更新版本；在較早版本上，受影響的代理會失敗。 執行等待時，任務面板中的進度線和 [`/workflows`](https://code.claude.com/docs/zh-TW/workflows#watch-the-run) 標題會顯示限制何時重設。 執行只在以下所有情況成立時暫停；當其中一個不成立時，受影響的代理會改為失敗：

- 工作階段是互動式的，並使用 claude.ai 訂閱登入。執行不會在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `claude -p` 或 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 暫停，在[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)中，或在[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)或[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友工作階段中。
- [`autoContinueAtUsageLimit`](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit) 已開啟，這是允許工作階段本身[等待使用限制重設](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)的相同設定。如果您在等待期間關閉它，等待會結束，等待中的代理會失敗。
- 限制在 24 小時內重設。每週限制可能會更晚重設。
- 執行尚未已等待兩次。當它第三次達到限制時，代理會失敗。

### 成本

工作流程生成許多代理，因此單次執行可以使用比在對話中完成相同任務更多的令牌。執行計入您的方案使用量和速率限制。 為了在提交大型任務前評估支出，請先在小片段上執行工作流程：一個目錄而不是整個儲存庫，或一個狹隘的問題而不是廣泛的問題。`/workflows` 檢視顯示每個代理的令牌使用量，隨著執行進行，您可以隨時在那裡停止執行，通常不會丟失已完成的工作。[暫停後恢復](https://code.claude.com/docs/zh-TW/workflows#resume-after-a-pause)涵蓋已停止的執行保留的內容。執行時間的[代理上限](https://code.claude.com/docs/zh-TW/workflows#behavior-and-limits)限制單次執行可以生成多少個代理，這限制了失控指令碼的成本。要保持執行為較少的代理，請選擇 `small`[大小指南](https://code.claude.com/docs/zh-TW/workflows#set-a-size-guideline)。 Claude Code 也會標記異常增長的執行。當工作流程排程超過 25 個代理，或其預計令牌總數超過 150 萬時，輸入框下方任務面板中的進度線會顯示 `Large workflow` 警告。警告指向您可以停止執行的 [`/workflows`](https://code.claude.com/docs/zh-TW/workflows#watch-the-run)。 警告是建議性的：它不會暫停或限制執行。當您看到它時，有兩個設定會改變：

- 如果您自己選擇[大小指南](https://code.claude.com/docs/zh-TW/workflows#set-a-size-guideline)，其代理計數會取代 25 個代理的閾值。內建預設指南將閾值保留在 25。
- 啟用[ultracode](https://code.claude.com/docs/zh-TW/workflows#let-claude-decide-with-ultracode) 的工作階段不會顯示警告，因為啟用 ultracode 已經讓您選擇加入大型執行。

Claude Code 按照它用於子代理的相同[順序選擇每個工作流程代理的模型](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)。指令碼為階段命名的模型在該順序中計為每次調用模型。當沒有其他內容分配模型時，代理在您的工作階段模型上執行。 要控制模型成本：

- 在大型執行前檢查 `/model`，如果您通常為日常工作切換到較小的模型
- 當您描述任務時，要求 Claude 為不需要最強模型的階段使用較小的模型

當您組織的 [`availableModels` 允許清單](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)阻止指令碼為代理請求的模型時，該代理會改為在替代模型上執行，遵循與子代理相同的[替代規則](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)。[`/workflows`](https://code.claude.com/docs/zh-TW/workflows#watch-the-run) 中的執行進度檢視會顯示一個警告，命名請求的和替代的模型。

### 設定大小指南

大小指南告訴 Claude 在編寫動態工作流程時應該針對多少個代理。Claude Code 將指南作為建議而不是上限發送給 Claude，因此呼叫不同規模的提示仍會覆蓋它。需要 Claude Code v2.1.202 或更新版本。 每個值對應一個代理計數：

| 值                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Claude 目標的代理計數                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `unrestricted`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 無指南：Claude 根據任務調整工作流程大小 |
| `small`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 少於 5 個代理                           |
| `medium`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 少於 10 個代理                          |
| `large`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 少於 50 個代理                          |
| 預設值為 `medium`，或當您使用 Claude Code v2.1.271 或更新版本登入 Pro 方案時為 `small`。在您選擇值之前，`/config` 列會將值標記為預設值，工作流程的 `Running in background` 列會命名生效的大小。需要 Claude Code v2.1.219 或更新版本；較早版本預設為 `unrestricted`。 要變更指南，在 `/config` 中為 Dynamic workflow size 設定選擇一個值，或執行 `/config workflowSizeGuideline=small`。在 v2.1.219 及更新版本上，您也可以在任何設定檔中設定 [`workflowSizeGuideline` 鍵](https://code.claude.com/docs/zh-TW/settings-reference#workflowsizeguideline)；該值優先於 `/config`，而當設定檔提供一個時，Claude Code 會隱藏 `/config` 列。 變更在下一個提示時生效。[執行時間代理上限](https://code.claude.com/docs/zh-TW/workflows#behavior-and-limits)仍然適用，無論設定如何。 |                                         |

### 關閉工作流程

工作流程在 CLI、桌面應用程式、IDE 擴充功能、[非互動模式](https://code.claude.com/docs/zh-TW/headless)與 `claude -p` 和 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 中可用。相同的禁用設定適用於每個表面。 要為自己關閉工作流程：

- 在 `/config` 中切換 Dynamic workflows 關閉。在工作階段中持續。
- 在 `~/.claude/settings.json` 中設定 `"disableWorkflows": true`。在工作階段中持續。
- 設定 `CLAUDE_CODE_DISABLE_WORKFLOWS=1`。在啟動時讀取，因此它適用於您設定它的任何位置。

要為整個組織關閉工作流程，在[受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)中設定 `"disableWorkflows": true`，或使用 [Claude Code 管理員設定](https://claude.ai/admin-settings/claude-code)頁面上的切換。 禁用工作流程時，捆綁的工作流程命令和 `/workflow-authoring` 技能不可用，`ultracode` 關鍵字不再觸發執行，`ultracode` 從 `/effort` 功能表中移除。

## 相關資源

- [並行執行代理](https://code.claude.com/docs/zh-TW/agents)：比較子代理、代理檢視、代理團隊和工作流程
- [建立自訂子代理](https://code.claude.com/docs/zh-TW/sub-agents)：工作流程協調的工作者原始類型
- [管理成本](https://code.claude.com/docs/zh-TW/costs)：多代理執行如何計入使用限制

是否 助手
