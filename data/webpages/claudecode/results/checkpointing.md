Claude Code 會自動追蹤 Claude 在您工作時所做的檔案編輯，讓您可以快速撤銷變更並回溯到先前的狀態，以防任何事情出現偏差。

## Checkpointing 的運作方式

當您與 Claude 合作時，checkpointing 會自動捕捉每次使用者提示開始一個回合前的程式碼狀態。

### 自動追蹤

Claude Code 追蹤由其檔案編輯工具所做的所有變更：

- 每個使用者提示開始一個回合都會建立一個新的 checkpoint
- Claude Code 在一個會話中保留最近 100 個 checkpoint 的檔案快照。捨棄較舊的 checkpoint 會刪除沒有其他 checkpoint 參考的快照檔案，除了每個檔案的第一個快照，VS Code 擴充功能將其用作會話差異的基準。
- Claude Code 將 checkpoints 與對話一起儲存，因此您可以在恢復會話後仍然執行 `/rewind`
- Claude Code 在[保留掃描](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)中刪除會話的檔案快照，預設情況下約在會話最後一次儲存後 30 天。回溯到快照已消失的 checkpoint 可能會失敗，並出現 [`No files were restored`](https://code.claude.com/docs/zh-TW/errors#no-files-were-restored) 錯誤。若要保留快照更久，請設定 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)。

### 回溯和總結

執行 `/rewind`，或在提示輸入為空時按兩次 `Esc`，以開啟回溯選單。 如果提示輸入包含文字，雙 `Esc` 會清除它而不是開啟選單。清除的文字會儲存到您的輸入歷史記錄中，因此在您完成回溯選單後，按 `Up` 可以召回它。 回溯選單列出您在會話期間傳送的每個提示，除了[在回合中途傳送的訊息](https://code.claude.com/docs/zh-TW/checkpointing#messages-sent-mid-turn-not-checkpointed)。選擇您想要操作的點，然後選擇一個動作：

- **恢復程式碼和對話** ：將程式碼和對話都回復到該點
- **恢復對話** ：回溯到該訊息，同時保持目前程式碼
- **恢復程式碼** ：回復檔案變更，同時保持對話
- **從此處總結** ：將此點之後的對話壓縮為摘要，釋放 context window 空間
- **從此處之前總結** ：將此點之前的對話壓縮為摘要，保持後續訊息完整
- **算了** ：返回訊息清單而不進行任何變更

兩個程式碼還原選項只在所選 checkpoint 有追蹤的檔案變更可以回復時出現。如果該點之後沒有捕捉到檔案編輯，選單只會提供**恢復對話** 、總結選項和**算了** 。 恢復對話或選擇「從此處總結」後，所選訊息的原始提示會恢復到輸入欄位中，以便您可以重新傳送或編輯它。 選擇「從此處之前總結」會讓您留在對話末尾，輸入為空。使用任一總結選項，**已總結對話** 標記會出現在對話中被壓縮訊息的位置。

#### 回溯過去已清除的對話

如果您在同一個 Claude Code 程序中較早執行了 `/clear`，回溯選單會在清單頂部顯示一個額外的項目，標記為 `/resume <session-id> (previous session)`。選擇它以恢復在 `/clear` 執行前活躍的對話。該項目在您退出 Claude Code 或恢復不同會話之前可用，並且需要 Claude Code v2.1.191 或更新版本。在較早的版本上，執行 `/resume` 並從清單中選擇前一個會話。

#### 引導摘要

總結不會改變磁碟上的檔案，原始訊息保留在會話記錄中，因此 Claude 仍然可以參考詳細資訊。若要引導摘要的重點，請用方向鍵反白**總結** 選項，並在該列顯示\*\*新增上下文（選用）\*\*的位置輸入指示，然後按 `Enter`。使用其數字鍵選擇選項會立即總結，不需要指示。 總結讓您保持在同一會話中並壓縮上下文，就像有針對性的 `/compact`。若要分支並嘗試不同的方法，同時保持原始會話完整，請改用 [`/branch`](https://code.claude.com/docs/zh-TW/sessions#branch-a-session) 或 `claude --continue --fork-session`。

## 常見使用案例

Checkpoints 在以下情況下特別有用：

- **探索替代方案** ：嘗試不同的實現方法，而不會失去起點
- **從錯誤中恢復** ：快速撤銷引入錯誤或破壞功能的變更
- **迭代功能** ：進行變化實驗，同時知道您可以回復到工作狀態
- **釋放上下文空間** ：從中點開始總結冗長的除錯會話，保持初始指示完整

## 限制

### Bash 命令變更未追蹤

Checkpointing 不追蹤由 Bash 命令修改的檔案。例如，如果 Claude Code 執行：

```
rm file.txt
mv old.txt new.txt
cp source.txt dest.txt

```

這些檔案修改無法透過回溯撤銷。只有透過 Claude 的檔案編輯工具進行的直接檔案編輯才會被追蹤。

### 子代理編輯未復原

[子代理](https://code.claude.com/docs/zh-TW/sub-agents)使用 Claude 的檔案編輯工具進行編輯，但 Claude Code 通常不會在您的會話檢查點中捕捉這些編輯。回溯是否復原這些編輯取決於子代理的執行方式：

- **前景分叉技能** ：[具有 `context: fork` 的技能](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)在前景執行，在您自己的回合期間編輯您的工作樹，因此回溯會照常復原其編輯。設定 `background: false` 以在前景執行分叉；有幾種情況（[列在技能頁面上](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)）無論設定如何都會在那裡執行。
- **任何其他子代理** ：回溯不會復原編輯。使用 git 來還原它們。這包括在背景執行的分叉技能（預設值）和背景 [`/code-review --fix`](https://code.claude.com/docs/zh-TW/code-review) 執行。

### 外部變更未追蹤

Checkpointing 只追蹤在目前會話中已編輯的檔案。您在 Claude Code 外部對檔案所做的手動變更以及來自其他並行會話的編輯通常不會被捕捉，除非它們碰巧修改與目前會話相同的檔案。

### 訊息在回合中途傳送未進行檢查點

當您[在 Claude 工作時排隊的訊息](https://code.claude.com/docs/zh-TW/interactive-mode#queue-messages-while-claude-works)在執行中的回合內到達 Claude 時，它會加入該回合而不是開始新的回合。訊息會出現在對話中，但 Claude Code 不會為其建立檢查點，回溯功能表也不會列出它。Claude Code 作為其自己的回合傳送的排隊訊息會照常獲得檢查點。 若要移除此類訊息，或撤銷 Claude 在其後所做的編輯，請回溯到開始該回合的提示。這會回溯整個回合，包括 Claude 在您的訊息到達之前所做的工作。

### 符號連結和硬連結路徑未復原

Checkpointing 不會回溯符號連結或硬連結檔案。當您從 `/rewind` 功能表中選擇**復原程式碼** 或**復原程式碼和對話** 時，Claude Code 會跳過任何是符號連結或硬連結的追蹤路徑，並顯示 `已復原程式碼，但跳過 N 個檔案`警告。跳過的檔案保持其目前內容。若要撤銷會話對其中一個檔案的變更，請要求 Claude 反轉編輯或自己編輯檔案。dotfile 管理器符號連結到您的專案中的設定檔以及 pnpm 硬連結到位置的檔案都屬於此類別。 若要查看復原跳過的路徑，請在復原前使用 `/debug` 開啟偵錯記錄：`~/.claude/debug/<session-id>.txt` 中的偵錯記錄會列出每個跳過的路徑。如需每個跳過原因和復原步驟，請參閱[錯誤參考中的 skipped-files 項目](https://code.claude.com/docs/zh-TW/errors#restored-the-code-but-skipped-files)。

### 不是版本控制的替代品

Checkpoints 設計用於快速的會話級恢復。對於永久版本歷史和協作，請繼續使用版本控制（例如 Git）進行提交、分支和長期歷史。

## 另請參閱

- [Interactive mode](https://code.claude.com/docs/zh-TW/interactive-mode) - 快捷鍵和會話控制
- [Commands](https://code.claude.com/docs/zh-TW/commands) - 使用 `/rewind` 存取 checkpoints
- [CLI reference](https://code.claude.com/docs/zh-TW/cli-reference) - 命令列選項

是否 助手
