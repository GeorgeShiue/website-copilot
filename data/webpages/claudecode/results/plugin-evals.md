`claude plugin eval` 針對一套測試案例執行您的 [plugin](https://code.claude.com/docs/zh-TW/plugins)，並對結果進行評分。每個案例都是一個真實的提示加上一個或多個評分器。評分器是對 Claude 產生的內容進行的通過/失敗檢查，例如對回覆的正規表達式、是否呼叫了特定工具，或由第二個模型判斷回覆的評分標準。 您不必手動編寫測試套件；`claude plugin eval init` 會詢問您有關 plugin 的問題，提議案例和評分器，嘗試它們，並編寫檔案。您也可以要求 Claude 從已開啟的工作階段中執行相同操作。 使用 evals 來測量您的 plugin 可靠地引導 Claude 達到正確結果的程度，在您變更 plugin 或新模型發佈時捕捉迴歸，以及查看與沒有 plugin 相比 plugin 的貢獻。 本頁面適用於擁有可運作 plugin 並想測試其行為的 plugin 和 skill 作者，以及在 CI 中把關 plugin 變更的團隊。其案例格式與 [skill-creator plugin](https://code.claude.com/docs/zh-TW/skills#run-evals-with-skill-creator) 使用的 `evals/evals.json` 檔案分開。若要建立 plugin，請參閱 [Create plugins](https://code.claude.com/docs/zh-TW/plugins)；若要檢查 plugin 的檔案是否存在語法和架構錯誤而不是其行為，請使用 [`claude plugin validate`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-validate)。 每次 eval 執行和每個評判評分器都是您帳戶上的真實模型呼叫，計入您的方案使用量或 API 帳單，因此請先檢查 [requirements](https://code.claude.com/docs/zh-TW/plugin-evals#requirements)。然後 [create your first eval suite](https://code.claude.com/docs/zh-TW/plugin-evals#create-your-first-eval-suite)，或如果您已經有一個，請前往 [Run evals in CI](https://code.claude.com/docs/zh-TW/plugin-evals#run-evals-in-ci)。

## Requirements

若要執行 plugin evals，您需要：

- Claude Code v2.1.269 或更新版本。執行 `claude --version` 檢查，執行 `claude update` 升級。
- 具有 `plugin.json` 或 `.claude-plugin/plugin.json` 資訊清單的 plugin 目錄，或 [skills-directory plugin](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)。
- 與您的正常 Claude Code 工作階段相同的驗證和模型提供者。Eval 執行、評判評分器和 `claude plugin eval init` 使用您的認證呼叫模型，因此它們計入您的方案使用量限制或 API 帳單。當命令報告成本時，該數字是這些呼叫的 [list-price estimate](https://code.claude.com/docs/zh-TW/costs)。

## Eval 執行的運作方式

Eval 套件位於 plugin 內名為 `evals/` 的目錄中，其佈局如 [Write and refine cases](https://code.claude.com/docs/zh-TW/plugin-evals#write-and-refine-cases) 所示。每個案例都是其自己的子目錄，包含 [prompt](https://code.claude.com/docs/zh-TW/plugin-evals#set-run-limits-and-tools-in-prompt-md) 和一個或多個 [graders](https://code.claude.com/docs/zh-TW/plugin-evals#grade-the-result)。提示是使用您的 plugin 的人可能輸入的內容，例如其中一個 skills 應該處理的請求。

### 執行中發生的情況

對於案例的每次執行，Claude Code 啟動一個新的、[isolated](https://code.claude.com/docs/zh-TW/plugin-evals#how-runs-are-isolated) [non-interactive session](https://code.claude.com/docs/zh-TW/headless)，僅載入您的 plugin，發送提示，並讓 Claude 工作直到完成或達到案例的轉數或時間限制。然後每個評分器檢查最終回覆、完整文字記錄或 Claude 建立的檔案，並通過或失敗。

### 案例如何評分

非確定性代理的一次執行告訴您很少，所以每個案例預設執行三次。執行的分數是其通過的評分器的比例，如果您設定權重則加權，案例的分數是其執行的平均值。當案例的分數達到 [`--threshold`](https://code.claude.com/docs/zh-TW/plugin-evals#command-options)（預設為 1.0）時，案例通過。在模型呼叫中，套件大約進行案例 × 執行代理執行與 plugin，以及同樣多的 [no-plugin baseline](https://code.claude.com/docs/zh-TW/plugin-evals#the-no-plugin-baseline)，加上每個 `llm` 或 `baseline` 評分器每次執行三個短評判呼叫。

### No-plugin 基準線

高分本身並不能告訴您 plugin 是否有幫助，因為 Claude 可能在沒有它的情況下做得同樣好。為了區分兩者，預設情況下每個案例的執行會在沒有載入 plugin 的情況下重複，您會獲得兩個分數：`WITH` 和 `W/OUT`。它們的差異 `Δ` 是 plugin 的貢獻。如果案例在有 plugin 和沒有 plugin 的情況下都得分 1.0，則不是 plugin 使其通過。這兩組執行稱為 with-arm 和 without-arm；[Compare against a no-plugin baseline](https://code.claude.com/docs/zh-TW/plugin-evals#compare-against-a-no-plugin-baseline) 涵蓋評分器如何在它們之間評分以及如何關閉基準線。

## 建立您的第一個 eval suite

本逐步解說為您自己的 plugin 編寫一個案例，執行它，並讀取結果。在開始之前，請確保您有：

- Claude Code v2.1.269 或更新版本以及其他 [requirements](https://code.claude.com/docs/zh-TW/plugin-evals#requirements)
- 在 plugin 根目錄開啟的終端機，即包含 `plugin.json` 或 `.claude-plugin/plugin.json` 的目錄
- plugin 中您想測試的一個 skill，以及使用者應該輸入的請求以觸發它

1 Create the cases 從 plugin 根目錄執行：

```
claude plugin eval init

```

如果 Claude Code 還不信任此目錄，它首先會詢問 `Trust this plugin directory?`；回答 `y`。然後開啟互動式 Claude Code 工作階段。Claude 讀取您的 plugin 並詢問您好的結果是什麼樣子，提議應該和不應該觸發 plugin 的提示，為每個設計評分器，試驗它們一次以檢查它們的行為，並在 `evals/` 下為每個提示編寫一個案例目錄，每個都以其提示命名。當 Claude 告訴您套件已準備好時，使用 `/exit` 或 Ctrl+D 退出該工作階段以返回您的 shell。如果您已經在 plugin 根目錄開啟了 Claude Code 工作階段，您可以改為要求 Claude 在該對話中執行 `claude plugin eval init`。Claude 執行命令，然後在該對話中詢問您相同的問題。如果您寧願自己編寫案例以查看檔案包含的確切內容，請遵循 [Write a case manually](https://code.claude.com/docs/zh-TW/plugin-evals#write-a-case-manually) 並返回此處執行它。 2 Run the suite 回到 plugin 根目錄的 shell，執行 `evals/` 下的每個案例：

```
claude plugin eval .

```

您已在步驟 1 中信任此目錄，因此執行立即開始。如果您改為手動編寫案例，執行首先會詢問 `Trust this plugin directory? [y/N]`；回答 `y`。[What a run can access](https://code.claude.com/docs/zh-TW/plugin-evals#security) 解釋了您同意的內容。每個案例使用您的 plugin 執行三次，沒有它執行三次，因此一個案例是六次執行。隨著每次執行完成，進度行會列印，顯示該執行的分數和每個評分器的判決。 3 Read the summary 當套件完成時，您會看到摘要表，然後是報告的位置：

```
CASE        WITH  W/OUT Δ      RUNS COST    NOTES
first-case  1.00  0.33  +0.67  6    $0.41

1 case(s) · mean Δ +0.67 · 74s · $0.41
Report: /Users/you/my-plugin/evals/results/2026-09-10T17-02-11-482Z/report.html
Published: https://claude.ai/... · keep local next time with --no-publish

```

`WITH` 是案例在載入您的 plugin 時的分數，`W/OUT` 是沒有它時的分數，正 `Δ` 表示 plugin 提高了分數。`COST` 是模型呼叫的 list-price estimate，`NOTES` 顯示最高權重失敗評分器的解釋或執行的錯誤，來自 with-arm。 4 Open the report and iterate 開啟 `Published:` URL 或當沒有 `Published:` 行出現時開啟 `Report:` 路徑，以查看每個評分器對每次執行的判決和解釋，以及對於 `llm` 評分器的評判投票和它判斷的摘錄。`Published:` 行僅在您的帳戶可以 [publish reports](https://code.claude.com/docs/zh-TW/plugin-evals#html-report) 時出現。最常見的第一個發現是 `Δ` 接近零，案例的 `tool_used: Skill` 評分器失敗，這意味著 Claude 在自然措辭上沒有選擇您的 skill。調整 skill 的 [`description`](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference)，再次執行 `claude plugin eval .`，並進行比較。若要廉價地迭代單個案例，執行單個 arm 一次。單次執行是有噪音的，因此在信任任何變更之前，請在預設三次執行時確認任何變更。使用一個 arm，表格顯示 `SCORE` 和 `PASS%` 列而不是 `WITH`、`W/OUT` 和 `Δ`：

```
claude plugin eval . --case <case-name> --runs 1 --ablation none

```

將 `<case-name>` 替換為 `evals/` 下的目錄名稱之一。

## 撰寫和改進案例

`claude plugin eval init` 撰寫的案例是純文字檔案，您可以開啟、變更和新增。案例是外掛程式 eval 目錄下的目錄，包含 `prompt.md`、`case.yaml` 或兩者。若要分組案例，請將它們巢狀放在不是案例本身的目錄下；案例目錄內的任何內容（例如 `graders/` 和 fixture 檔案）都屬於該案例。 這是 `claude plugin eval init` 撰寫的配置，也是用於新套件的配置。[eval 套件參考](https://code.claude.com/docs/zh-TW/plugin-evals#eval-suite-reference)包含完整的樹狀結構，包括 mocks 和結果：

```
my-plugin/
├── .claude-plugin/plugin.json
├── skills/...
└── evals/
    ├── first-case/
    │   ├── prompt.md          # frontmatter: case fields; body: the prompt
    │   ├── graders/
    │   │   ├── criteria.md    # frontmatter: type + options; body: rubric or pattern
    │   │   └── skill-fired.md
    │   └── case.yaml          # optional: only for context.* fields
    ├── ignores-unrelated-request/
    │   └── ...
    └── results/               # written by each run; add to .gitignore

```

### 手動撰寫案例

讓 Claude 使用 `claude plugin eval init` 撰寫案例是建議的方式。若要自己撰寫，請從空白範本開始。下列命令會撰寫一個名為 `first-case` 的案例，包含預留位置 `prompt.md` 和一個預留位置 grader，且不執行任何內容：

```
claude plugin eval init --bare first-case

```

```
evals/first-case/
├── prompt.md            # the prompt sent to Claude, plus run limits
└── graders/
    └── criteria.md      # one grader: how to score the result

```

在 `prompt.md` 中，您撰寫 Claude 在每次執行時收到的訊息，並在 frontmatter 中設定執行的限制和案例可能使用的工具。開啟 `evals/first-case/prompt.md` 並將預留位置本文替換為您的請求，用使用者會輸入的方式表述，而不是命名技能。此範例適用於起草提交訊息的技能；請使用您自己的請求：

```
---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Write me a commit message for this change: I renamed getUser to fetchUser and updated the three call sites.

```

每次執行都在空的工作目錄中開始，所以將任務需要的內容放在提示本身中，或[先設定工作區](https://code.claude.com/docs/zh-TW/plugin-evals#add-setup-or-history-with-case-yaml)。[frontmatter 欄位的完整清單](https://code.claude.com/docs/zh-TW/plugin-evals#prompt-md-fields)涵蓋模型、逾時、標籤和環境變數。 `graders/` 下的每個檔案都是執行後套用的一項檢查。開啟 `evals/first-case/graders/criteria.md` 並將預留位置替換為評判模型的評分標準，寫成具體的 PASS 和 FAIL 條件：

```
---
type: llm
---

PASS if <what a correct response contains>.
FAIL if <what a wrong or missing response looks like>.

```

然後新增第二個 grader，檢查您的技能是否是產生答案的原因。建立 `evals/first-case/graders/skill-fired.md`，將 `your-skill-name` 替換為您技能的 `SKILL.md` 中的 `name`：

```
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"'
---

```

當 Claude 在執行期間至少呼叫過該技能一次時，這會通過，包括其命名空間 `plugin-name:skill-name` 形式。[Grader 類型](https://code.claude.com/docs/zh-TW/plugin-evals#grader-types)列出其他可用的檢查，例如符合正規表達式或確認檔案已建立。 兩個檔案都儲存後，按照[快速入門](https://code.claude.com/docs/zh-TW/plugin-evals#create-your-first-eval-suite)的方式執行案例，從外掛程式根目錄執行 `claude plugin eval .`。

### 在 prompt.md 中設定執行限制和工具

在 `prompt.md` frontmatter 中設定案例的 `max_turns`、`timeout_seconds`、`model`、`tags` 和它可能使用的 `allowed_tools`；[prompt.md frontmatter](https://code.claude.com/docs/zh-TW/plugin-evals#prompt-md-fields) 參考列出每個欄位及其預設值。Claude 會完全按照您撰寫的方式接收本文。其中的 `@path` 提及不會展開為檔案附件，所以如果 Claude 需要讀取檔案，請在 `allowed_tools` 中授予工具。

### 選擇和加權 graders

Grader 的 frontmatter 設定其 `type`，以及可選的 `weight` 使其計入執行分數的更多部分，以及控制如何針對基準線評分的 [`arm`](https://code.claude.com/docs/zh-TW/plugin-evals#compare-against-a-no-plugin-baseline)。在六種類型中，`regex`、`tool_used`、`tool_order` 和 `file_exists` 是從文字記錄和檔案計算的，不需要成本，而 `llm` 和 `baseline` 呼叫評判模型並增加執行成本。 沒有自訂程式碼 graders。[Grader 類型](https://code.claude.com/docs/zh-TW/plugin-evals#grader-types)列出每種類型的選項和通過條件，[grader 可以查看的內容](https://code.claude.com/docs/zh-TW/plugin-evals#what-a-grader-can-look-at)列出 `target` 和 `focus` 接受的值。 `llm` 和 `baseline` graders 的評判者預設是小型快速模型。傳遞 `--judge-model sonnet` 或完整模型 ID 以使用更強大的模型來處理細微的評分標準。

#### 選擇提供穩定訊號的 graders

`llm` grader 要求模型提供判決，所以其答案可能在執行之間有所不同，且文字越長差異越大。這些習慣可以讓套件的分數穩定到足以信任：

- 對於長輸出（例如產生的檔案），使用檔案內容上的 `regex` grader 進行評分，它每次都以相同的方式檢查整個檔案。將 `llm` graders 保留用於短輸出，評分標準寫成具體的 PASS 和 FAIL 條件。
- 為每個案例提供一個 grader 來評分結果（例如最終訊息或產生的檔案），以及一個來評分 Claude 如何達成的（例如 `tool_used` 或 `tool_order`）。它們一起告訴您答案是否正確以及您的外掛程式是否產生了它。
- 如果案例的 `tool_used: Skill` grader 通過但 `Δ` 為負，請懷疑評判者而不是外掛程式。小型評判模型可能會因為格式與評分標準描述的不同而將正確答案標記為錯誤。使用 `--judge-model sonnet` 重新執行，並收緊評分標準，使格式不會決定判決。
- 若要檢查建置或測試在執行內通過，請讓提示要求 Claude 執行它並將結果寫入檔案，評分該檔案，並使用 `tool_used` grader（其 `input_match` 命名該命令）判斷命令已執行。

### 針對無外掛程式基準線評分

當外掛程式在測試中時，每個案例預設在兩個 arm 中執行。with-arm 是使用外掛程式載入的執行，without-arm 是沒有外掛程式的相同數量執行。摘要和報告顯示兩個分數和 `Δ`（with-arm 分數減去 without-arm 分數）。傳遞 `--ablation none` 以僅執行 with-arm，當您不需要比較時（例如在迭代 graders 時）成本減半。 在雙 arm 執行中，某些 graders 會以 `scored: false` 報告。像「技能已呼叫」這樣的檢查在沒有外掛程式的情況下永遠無法通過，所以計算它會將 without-arm 推向零並誇大 `Δ`。為了保持兩個 arm 可比較，Claude Code 在兩個 arm 中排除此類 graders 的分數，並在 with-arm 中將其報告為僅通過/失敗指標。這包括：

- 每個 `tool` 為 `Skill` 的 `tool_used` grader
- 任何您標記為 `arm: with-only` 的 grader

如果案例中的每個 grader 都是其中之一，它們會改為正常評分，因為沒有其他內容可評分。在 grader 上設定 `arm: both` 以無論如何在兩個 arm 中評分，這是您想要的「不得呼叫技能」檢查，具有 `min: 0` 和 `max: 0`。在 `--ablation none` 下，沒有任何內容被排除，所以相同的套件在兩種模式中可能產生不同的絕對分數。

### 使用不同的 eval 目錄

如果 `evals/` 已被另一個工具佔用，請將套件保留在不同的目錄中。您可以在外掛程式的 `plugin.json` 中記錄該目錄，以便每次執行和每個協作者都使用它，或在命令列上傳遞它以進行單次執行：

- **在`plugin.json` 中**：新增 `"experimental": { "evals": "quality/evals" }`。
- **在命令列上** ：將 `--eval-dir quality/evals` 傳遞給 `claude plugin eval` 和 `claude plugin eval init`。

如果同時設定兩者，則使用旗標的目錄。給出相對路徑，包含純目錄名稱，例如 `qa` 或 `quality/evals`；絕對路徑或包含 `..` 的路徑會被拒絕：作為旗標值時會出現錯誤，而無法使用的資訊清單值會列印 `Warning:` 行，執行會改用 `evals/`。案例、結果和 `init` 輸出都會移至該目錄。

## 設定 fixtures 和 mocks

案例可能需要的不僅僅是提示：工作區中的檔案或 git 儲存庫、要繼續的早期對話，或您的 plugin 與之交談的 MCP 伺服器的答案。每個都在案例旁邊設定，以便執行保持可重複。

### Seed the workspace or conversation

每次執行都在空工作區中開始。當案例需要的不僅僅是提示時，在 `prompt.md` 旁邊新增 `case.yaml`，其中包含 `context` 區塊。 若要首先建立 fixture 檔案或 git 儲存庫，請在案例目錄中編寫 Bash 指令碼並在 `context.scaffold_script` 中命名它。指令碼以您的身份在代理沙箱外執行，僅當您傳遞 `--scaffold` 時，因此僅對您或您的組織編寫的套件傳遞該標誌。若要繼續早期對話，請將文字記錄保存為 `.jsonl` 檔案並在 `context.history_file` 中命名它，案例的提示變成下一個使用者轉數。若要讓 Claude 在執行期間讀取案例中的 fixture 目錄，請在 `context.add_dirs` 中列出它們。 `case.yaml` 也需要 `schema_version: "1.1"` 和 `name`；[case.yaml fields](https://code.claude.com/docs/zh-TW/plugin-evals#case-yaml-fields) 參考有完整列表。 此 `case.yaml` 從指令碼播種工作區並讓 Claude 從 `resources/` 目錄讀取 fixtures：

```
schema_version: "1.1"
name: changelog-from-diff
tags: [smoke]
context:
  scaffold_script: fixture.sh
  add_dirs: [resources]

```

### Mock MCP servers

您可以評估 plugin，其 skills 呼叫 MCP 工具，而無需它們後面的真實服務。在 `evals/mocks/<server>/<tool>.md` 下為整個套件放置一個 Markdown 檔案，或在案例自己的 `mocks/` 目錄下為一個案例，其中 `<server>` 是您的 plugin 的 [MCP configuration](https://code.claude.com/docs/zh-TW/plugins-reference#mcp-servers) 中伺服器的名稱。 執行永遠不會啟動您的 plugin 的真實 MCP 伺服器，除非您要求。Claude Code 在每個伺服器自己的名稱下註冊替代品。具有 mock 檔案的工具從它回答，並且無需 `--allow-tools` 授予即可允許，具有無 mock 檔案的工具對 Claude 不可用。完全沒有 mocks 的伺服器在案例的 `mocked:` 進度行中顯示為 `plugin_<plugin>_<server>[not started: no mock]`。 檔案的主體是工具返回給 Claude 的內容。此 mock 代替名為 `tracker` 的伺服器上的 `create_issue` 工具，檢查 Claude 發送的輸入，並回顯標題。將其保存為 `evals/mocks/tracker/create_issue.md`：

```
---
expect:
  title: string
  priority: [low, medium, high]
---

Created issue #4821: {{input.title}}

```

使用 `{{input.<field>}}` 從呼叫的輸入插入欄位，使用 `{{file:fixtures/{input.<field>}.json}}` 插入 mock 旁邊的 fixture 檔案的內容。`expect:` 區塊保護輸入。如果呼叫違反它，執行會中止，分數為 0，並記錄原因，因此案例可以斷言您的 plugin 要求伺服器執行的操作。設定 `error: true` 以改為將主體作為工具錯誤返回，或 `type: agent` 讓小型模型從主體中的指令作為伺服器回答。[mock file reference](https://code.claude.com/docs/zh-TW/plugin-evals#mock-files) 列出每個鍵和 `_server.md` 和 `_tools.json` 檔案。 若要評分呼叫本身，請將評分器指向 `target: mock_calls`。 若要改為針對 plugin 的真實 MCP 伺服器執行，請傳遞以下標誌之一。無論哪種方式，這些程序都以您的身份在執行沙箱外執行，其工具需要 [`--allow-tools` 授予](https://code.claude.com/docs/zh-TW/plugin-evals#grant-tools)：

- **`--allow-real-servers`**：為您未 mock 的每個伺服器啟動真實程序，並繼續從其檔案回答 mocked 工具
- **`--mocks off`**：完全忽略`mocks/` 並啟動 plugin 宣告的每個伺服器

#### Replay agent mock answers

`type: agent` mock 使用 [`--judge-model`](https://code.claude.com/docs/zh-TW/plugin-evals#command-options) 呼叫回答，因此其輸出在執行之間變化，如果您變更評判者則會改變。當執行完成而沒有錯誤或中止時，Claude Code 在結果目錄中的 `mock-recordings/` 下保存代理 mock 給出的每個答案。 開啟那裡的 `ADOPT.txt` 以查看每個記錄和 `.replay/<server>/` 目錄以複製到，在產生它的 mock 旁邊。複製記錄後，稍後執行會從它回答相同呼叫，沒有模型呼叫。將 `mocks/.replay/` 與 `mocks/` 的其餘部分一起提交，以便 CI 執行可重複。

## 執行 evals

一旦套件存在，`claude plugin eval` 就執行它。您選擇哪個 plugin 和案例使用目標引數執行，使用 `--allow-tools` 授予案例需要的任何工具超過唯讀集，並使用其他選項控制執行計數、模型、成本和輸出。

### 選擇要評估的內容

大多數時候您從 plugin 根目錄執行 `claude plugin eval .`，它執行套件中 eval 目錄下的每個案例，並載入您所在的 plugin。若要執行單個案例檔案，或評估您安裝的 plugin 而不是您正在開發的 plugin，請傳遞不同的目標：

| Target                                                                                                                                                                                                                           | What runs                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A plugin’s root directory, such as `.`                                                                                                                                                                                           | Every case under its eval directory, with that plugin loaded                                                                                                                                      |
| A single `prompt.md` or `case.yaml` file                                                                                                                                                                                         | That case, with its enclosing plugin loaded                                                                                                                                                       |
| An installed plugin by name, `name` or `name@marketplace`                                                                                                                                                                        | The cases in the installed copy’s eval directory, with the installed copy loaded. Results are written under `./evals/results/` in your current directory, or `./<dir>/results/` with `--eval-dir` |
| `name@skills-dir`                                                                                                                                                                                                                | The same, for a [skills-directory plugin](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)                                                                          |
| Omitted                                                                                                                                                                                                                          | The current directory as a path                                                                                                                                                                   |
| 新增 `--case <glob>` 按案例名稱篩選，`--tag <tag>` 保留具有任何給定標籤的案例。將目標放在 `--tag`、`--allow-tools` 和 `--json` 之前。前兩個採用列表，`--json` 採用可選路徑，因此它們中的每一個都讀取跟隨它的目標作為其自己的值。 |                                                                                                                                                                                                   |

### 授予工具

執行永遠不會停止要求許可。需要您未授予的授予的內建工具，例如 `Bash`、`Write`、`Edit`、`WebFetch` 和 `WebSearch`，會從工作階段中移除，因此 Claude 根本無法呼叫它們。允許清單是案例在 `allowed_tools` 中列出的唯讀工具，來自 `Read`、`Glob`、`Grep`、`NotebookRead`、`Skill`、`Agent`、`TodoWrite` 和任務工具 `TaskCreate`、`TaskGet`、`TaskList`、`TaskUpdate`、`TaskStop` 和 `TaskOutput`，加上您使用 `--allow-tools` 授予的任何內容，它適用於執行中的每個案例。若要讓案例使用 `Bash`、`Write`、`Edit`、`WebFetch` 或 `WebSearch`，請自己授予它們：

```
claude plugin eval . --allow-tools Write Edit "Bash(npm test *)"

```

當案例要求您未授予的工具時，執行在 stderr 上將其列為 `not granted`。[mocked](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers) MCP 伺服器上的工具不需要授予。真實 plugin MCP 伺服器上的工具需要伺服器啟動（使用 `--allow-real-servers` 或 `--mocks off`）和按名稱授予，例如 `--allow-tools "mcp__plugin_my-plugin_github__*"`；plugin 的 MCP 工具命名為 `mcp__plugin_<plugin>_<server>__<tool>`。 當您以任何形式授予 `Bash` 時，每個命令都在 Claude Code 的 [OS-level sandbox](https://code.claude.com/docs/zh-TW/sandboxing) 下執行。寫入限制在執行的工作區、您的主目錄和 Claude Code 設定無法讀取，網路存取限制在您使用 `--allow-tools "WebFetch(domain:example.com)"` 授予的網域。如果您在沒有沙箱後端的機器上授予 Bash 或 PowerShell，Claude Code 拒絕每次執行而不是無限制執行它，案例顯示執行錯誤，通常分數為 0。原生 Windows 沒有後端，因此在 WSL2 下執行 shell 授予套件；在 Linux 上，首先安裝 `bubblewrap` 和 `socat`。請參閱 [sandboxing prerequisites](https://code.claude.com/docs/zh-TW/sandboxing)。

### 命令選項

此表涵蓋執行計數、模型、評分、成本、工具授予、mocks 和輸出的選項。執行 `claude plugin eval --help` 以獲得完整列表，其中還包括 `--case`、`--tag`、`--eval-dir`、`--no-scaffold`、`--report` 和 `--verbose`。

| Option                     | Default                                                                        | Effect                                                                                                                                                                                                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--runs <n>`               | Each case’s `runs`, else 3                                                     | Runs per case per arm                                                                                                                                                                                                                                                                      |
| `-j`, `--concurrency <n>`  | `1`                                                                            | Run up to this many agent runs at once, from 1 to 8. They share your account’s rate limit, so this shortens wall-clock time rather than raising throughput past that limit. Results keep case order                                                                                        |
| `--model <model>`          | Each case’s `model`, else `ANTHROPIC_MODEL` if set, else Claude Code’s default | Model for the agent under test. Pin it in CI so a model rollout isn’t mistaken for a plugin regression                                                                                                                                                                                     |
| `--judge-model <model>`    | A small fast model                                                             | Model for `llm` and `baseline` graders                                                                                                                                                                                                                                                     |
| `--ablation <mode>`        | `with-without` when a plugin resolves, else `none`                             | Whether to also run each case without the plugin to measure what it adds. `none` runs one arm; `with-without` adds the no-plugin baseline                                                                                                                                                  |
| `--threshold <0..1>`       | `1.0`                                                                          | A case passes when its with-arm score is at least this. Any case below it makes the command exit 1                                                                                                                                                                                         |
| `--max-cost-usd <usd>`     | No ceiling                                                                     | A ceiling on the run’s list-price cost estimate, not on plan usage. Checked before each run starts. Once spent, nothing further starts; runs already in flight finish, so spend can pass the ceiling by those runs. If any run is left unstarted, the command exits 2 with partial results |
| `--allow-tools <tools...>` | None                                                                           | Grant tools beyond the read-only set. See [Grant tools](https://code.claude.com/docs/zh-TW/plugin-evals#grant-tools)                                                                                                                                                                       |
| `--scaffold`               | Off                                                                            | Run each case’s [`scaffold_script`](https://code.claude.com/docs/zh-TW/plugin-evals#add-setup-or-history-with-case-yaml)                                                                                                                                                                   |
| `--trust-plugin`           | Off                                                                            | Skip the first-run trust prompt for a plugin whose code and suite you’d run yourself. Pass it in CI so the job is never refused by or left waiting at the prompt. See [What a run can access](https://code.claude.com/docs/zh-TW/plugin-evals#security)                                    |
| `--mocks <mode>`           | `record`                                                                       | `record` answers MCP tool calls from [mocks](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers), doesn’t start the plugin’s real servers, and saves agent-mock answers for replay. `off` ignores mocks and starts the plugin’s real MCP servers                             |
| `--allow-real-servers`     | Off                                                                            | With `--mocks record`, also start the plugin’s real MCP servers for servers that have no mock                                                                                                                                                                                              |
| `--json [path]`            | Off                                                                            | Print the [result document](https://code.claude.com/docs/zh-TW/plugin-evals#json-result) to stdout, or write it to a path ending in `.json`. The run is quiet: no progress lines or summary table                                                                                          |
| `--output-dir <dir>`       | `<eval dir>/results/<timestamp>/`                                              | Where `aggregate-result.json` and `report.html` go                                                                                                                                                                                                                                         |
| `--no-publish`             |                                                                                | Keep the HTML report local. See [HTML report](https://code.claude.com/docs/zh-TW/plugin-evals#html-report)                                                                                                                                                                                 |
| `--publish-report`         |                                                                                | Publish the report even where it would stay local by default, such as a run a Claude Code session started                                                                                                                                                                                  |
| `--keep-temp`              | Off                                                                            | Keep every run’s sandbox directory and print its path, for debugging what Claude produced                                                                                                                                                                                                  |

### 在 CI 中執行 evals

在您的 CI 工作中，使用 `--json` 執行套件以寫入結果以進行存檔，並根據退出代碼使建置失敗。傳遞 `--trust-plugin` 以便工作永遠不會在 [first-run trust prompt](https://code.claude.com/docs/zh-TW/plugin-evals#security) 處等待，固定兩個模型以便分數在一段時間內可比較，保持報告本地，並設定成本上限作為上限：

```
claude plugin eval . \
  --trust-plugin \
  --json results.json \
  --threshold 0.8 \
  --model claude-sonnet-5 \
  --judge-model claude-haiku-4-5 \
  --no-publish \
  --max-cost-usd 20

```

工作的退出代碼告訴您發生了什麼：

| Exit code                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Meaning                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Every case scored at or above `--threshold` and every case file loaded                                                                                                                                         |
| 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | A case scored below the threshold, a case file failed to load, no cases were found, a run couldn’t be started, the plugin directory isn’t trusted and `--trust-plugin` wasn’t passed, or an option was invalid |
| 2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Partial run: the `--max-cost-usd` ceiling was hit, or your credential was rejected before or at the first run. `results.json` is still written with `partial: true` and the reason                             |
| 130                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Interrupted. Partial results are written                                                                                                                                                                       |
| 143                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Terminated, such as by a CI timeout                                                                                                                                                                            |
| 寫入或發佈 HTML 報告的問題永遠不會改變退出代碼。若要查看案例評分低的原因，請在本地執行它而不使用 `--json`，以便列印每次執行的進度和評分器行。 CI 執行器需要 Claude Code 安裝和 [credentials in the environment](https://code.claude.com/docs/zh-TW/authentication)，例如 `ANTHROPIC_API_KEY`。沒有 `--trust-plugin`，其簽出目錄 Claude Code 還不信任的工作在沒有終端時被拒絕，退出代碼 1，或在執行器分配一個時在提示處等待。`claude plugin eval init` 需要終端來詢問您的問題；在 CI 中，執行 `claude plugin eval init --bare <name>` 以獲得空白範本。 若要保持成本可預測，請為快速每次變更套件提供僅不呼叫評判的評分器，在您不需要 `Δ` 的地方使用 `--ablation none`，並將 `partial: true` 文件和具有 `skippedPaidGraders` 的執行排除在您繪製的任何趨勢之外。 |                                                                                                                                                                                                                |

## 讀取結果

每次執行至少一個案例會在 eval 目錄內寫入 `results/<timestamp>/` 目錄，包含 `aggregate-result.json` 和 `report.html`。對於 plugin 下的路徑目標；對於您命名的 plugin，它在您的目前目錄下，如 [target table](https://code.claude.com/docs/zh-TW/plugin-evals#choose-what-to-evaluate) 所示。摘要表、JSON 和報告都呈現相同的結果資料。

### HTML report

`report.html` 是一個單一的自包含檔案，不進行外部請求，因此您可以將其附加到 CI 工作或從磁碟開啟它。這個範例是使用 `--threshold 0.8` 執行三案例套件的報告頂部；顯示的成本是列表價格估計，會因模型和案例數量而異： ![eval 報告的頂部：一條判決行讀取「Plugin effect: +33.3 pts vs baseline, improved 2, flat 1, regressed 0 of 3 cases」，五個摘要磚塊分別用於套件分數、消融差異、基準分數、通過閾值的案例和完美執行，然後是第一個案例及其差異、分數條和一次執行，其兩個評分器都顯示通過](https://mintcdn.com/claude-code/qq7LHDi_F0aeFHgk/images/plugin-eval-report.png?fit=max&auto=format&n=qq7LHDi_F0aeFHgk&q=85&s=106eb6e6a70a6565f891ea3a4564f87d)
> # Image-1
>
> **圖片摘要：**
> commit-helper 外掛評測報告顯示套件分數、基準分數及 rename-commit 案例結果。
>
> **主要元素：**
> 1. 實體: 插件評測報告, 提交輔助外掛, 基準分數, 案例評測, 完美執行
> 2. OCR文字:
> PLUGIN EVAL REPORT
> commit-helper v1.2.0
> Plugin effect: ↑ +33.3 pts vs baseline — improved 2 · flat 1 · regressed 0 of 3 cases.
> · Claude Code v2.1.269　2026-09-11 19:40 UTC　2m 22s　$0.93　18 runs　judge default　threshold 80%
> SUITE SCORE ·
> WITH PLUGIN
> 94.4%
> mean of per-case
> scores
> ABLATION Δ
> ↑ +33.3
> score points vs
> baseline, 3 of 3
> cases
> BASELINE SCORE
> 61.1%
> without the plugin
> CASES
> 3
> 3 of 3 ≥ 80%
> threshold
> PERFECT RUNS
> 88.9%
> runs where every
> grader passed
> HOW TO READ THIS REPORT
> Expand all
> Collapse all
> rename-commit　evals/rename-commit　↑ +66.7 pts　with plugin　100%
> RESULTS
> With plugin　100%　100% of runs perfect
> Run 1　100%　3 turns · $0.05 · 19:40:20 UTC
> ▸ pass　criteria
> ▸ pass　skill-fired　PLUGIN-FIRED INDICATOR
> 3. 主題標籤: 外掛評測, commit-helper, rename-commit, Claude Code, 基準比較
>
> **頁面關聯：**
> commit-helper v1.2.0 外掛評測頁，錨點為 rename-commit人體藝術
從上到下讀取：

- **判決行和磚塊** 回答 plugin 是否在整個套件中有幫助。套件分數是每個案例 with-plugin 分數的平均值，Ablation Δ 是該分數高於或低於基準分數的距離，Cases 計算有多少個達到閾值。Perfect runs 是 with-plugin 執行的比例，其中每個評分器都通過。
- **每個案例卡** 顯示案例自己的 `Δ` 和 with-plugin 分數，在閾值處有一個刻度。`Δ` 為負的案例在左邊緣獲得紅色，因此當您捲動時迴歸會突出顯示。
- **在案例內** ，with-plugin 執行首先出現，基準執行之後。每次執行列出其評分器及通過或失敗晶片。失敗的評分器已經展開並附帶其解釋，`llm` 評分器也顯示法官的投票和它被顯示的證據，這是您發現執行分數低原因的地方。不計入分數的評分器，例如 `tool_used: Skill`，帶有 `plugin-fired indicator` 徽章。
- **Prompt 和 Graders** ，在執行下方，顯示案例的 prompt 和每個評分器的評分標準或模式，因此閱讀報告而不查看套件的人可以看到被要求的內容和什麼被視為良好。

如果您使用 claude.ai 訂閱登入並且 [artifacts](https://code.claude.com/docs/zh-TW/artifacts) 可用於您的帳戶，Claude Code 也會將報告發佈為私人 artifact 並列印 `Published: <url>`。傳遞 `--no-publish` 以保持本地。如果沒有 `Published:` 行出現，例如使用 API 金鑰驗證，本地檔案是報告。 Claude Code 工作階段啟動的執行，例如當您要求 Claude 為您執行套件時，也保持本地，其 `Report:` 行說 `kept local`。將 `--publish-report` 新增到該命令以發佈它。

### JSON result

`aggregate-result.json` 和 `--json` 輸出是版本化文件，具有 `schemaVersion: 1` 供 CI 指令碼解析。欄位名稱是 camelCase，新欄位在不重新命名現有欄位的情況下新增，因此編寫您的指令碼以忽略它不識別的欄位。 這些是把關指令碼通常讀取的欄位。文件還包含套件設定、每個評分器定義和每次執行評分器結果及解釋和證據：

| Field                                             | Meaning                                                                                                                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `partial`, `partialReason`                        | `true` with `cost_ceiling`, `interrupted`, or `auth_failed` when the suite didn’t finish. Leave partial results out of trend charts                                                                                 |
| `aggregates.overallScore`                         | Mean case score across the suite                                                                                                                                                                                    |
| `aggregates.casesPassed`, `aggregates.casesTotal` | Cases at or above `--threshold`, and the total                                                                                                                                                                      |
| `aggregates.meanDelta`                            | Mean `Δ` across cases, under the two-arm mode                                                                                                                                                                       |
| `cases[].name`                                    | Case name                                                                                                                                                                                                           |
| `cases[].aggregates.score`                        | Mean with-arm run score for the case                                                                                                                                                                                |
| `cases[].aggregates.delta`                        | With-arm score minus without-arm score. Omitted when the arms aren’t comparable                                                                                                                                     |
| `cases[].arms.with[].error`                       | `null`, or why a run ended abnormally, such as `timed out after 300s`. A run that started but ended badly is still graded on what it produced, so a non-null error doesn’t imply score 0                            |
| `cases[].arms.with[].aborted`                     | Present when a [mock](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers)’s `expect:` or `abort_when` stopped the run, with `server`, `tool`, and `reason`. The run scores 0 and `error` stays `null` |
| `cases[].arms.with[].skippedPaidGraders`          | `true` when the cost ceiling skipped this run’s judge graders, so its score isn’t comparable                                                                                                                        |
| `costUsd`, `durationSeconds`, `claudeVersion`     | Estimated cost at list price including judge calls, wall-clock seconds, and the Claude Code version that ran the suite                                                                                              |

## What a run can access

`claude plugin eval` 載入目標 plugin 的 skills 和 hooks，並在您的機器上以您的身份執行其 eval 套件。將其指向 plugin 與 `claude --plugin-dir` 相同的信任決定，因此僅評估您信任的 plugins。本節中描述的隔離限制了被測試代理可以到達的內容；它不是針對 plugin 自己程式碼的邊界，通過套件的套件對 plugin 是否安全沒有說明。

### Trust the plugin directory

第一次針對目錄執行 `claude plugin eval` 時，Claude Code 會詢問 `Trust this plugin directory?`，除非您已在互動式 `claude` 工作階段中在那裡接受信任提示。在 git 儲存庫內，回答是信任整個儲存庫，對於互動式工作階段也是如此。當 stdin 或 stdout 不是終端時，或在 `--json` 下，執行無法詢問並被拒絕，退出代碼 1；傳遞 `--trust-plugin` 以自己斷言信任，僅對您會在自己的機器上執行的 plugin。您命名而不是作為路徑給出的目標（意味著已安裝的 plugin 或 skills-directory plugin）跳過提示。 plugin 和套件的某些部分僅在您為該執行傳遞其標誌時執行：案例的 [`scaffold_script`](https://code.claude.com/docs/zh-TW/plugin-evals#add-setup-or-history-with-case-yaml) 使用 `--scaffold`、[tools beyond the read-only set](https://code.claude.com/docs/zh-TW/plugin-evals#grant-tools) 使用 `--allow-tools`，以及 plugin 的 [real MCP servers](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers) 使用 `--allow-real-servers` 或 `--mocks off`。案例的 `allowed_tools` 和 skill 自己的 `allowed-tools` frontmatter 無法擴展它們中的任何一個。當 plugin 發佈您未編寫的 hooks，或您啟動其真實 MCP 伺服器時，除非您在隔離環境（例如容器或 CI 執行器）中執行它，否則將其分數視為建議，因為 hooks 和伺服器在代理沙箱外執行，可能會觸及評分器讀取的檔案。

### How runs are isolated

每次執行都獲得一次性主目錄、工作目錄和 Claude Code 設定，被測試代理在那裡以 `claude -p` 子程序執行，僅載入您的 plugin。在編寫案例時牢記這些後果：

- **沒有個人或專案級別載入。** 您的使用者設定、hooks、`CLAUDE.md` 檔案、MCP 伺服器、其他已安裝的 plugins、記憶和 skills 不存在，沒有專案範圍的 `.claude/` 或 `.mcp.json` 在沙箱上方被讀取。您的大部分 shell 環境也被扣留；僅 [allowlist](https://code.claude.com/docs/zh-TW/plugin-evals#prompt-md-fields) 和 `EVAL_*` 變數到達執行。如果 plugin 需要設定，請在 plugin 中發佈它，在 `scaffold_script` 中建立它，或傳遞 `EVAL_*` 變數。
- **受管理的原則仍然可以限制執行。** 管理員部署到機器的 [managed settings](https://code.claude.com/docs/zh-TW/managed-settings) 中的限制適用於執行內，因此受管理機器上的結果可能因該原則而與非受管理機器不同。
- **Artifact 工具已關閉。** 發佈 [artifact](https://code.claude.com/docs/zh-TW/artifacts) 的 skill 只能在該步驟之前評分其產生的內容。
- **案例定義對代理隱藏。** 執行無法讀取 eval 目錄，因此 Claude 無法看到案例的提示、其評分器或同級案例。
- **shell 命令外沒有網路沙箱。** 您授予的 shell 命令在沙箱的網路規則下執行。`WebFetch(domain:…)` 授予直接到達該網域，plugin 自己的 hooks 和您啟動的任何真實 MCP 伺服器可以到達任何主機。

## Eval suite reference

eval 套件可以包含的所有內容都位於 plugin 的 eval 目錄 `evals/` 下，除非您 [configured another](https://code.claude.com/docs/zh-TW/plugin-evals#use-a-different-eval-directory)。此樹顯示 `claude plugin eval` 在那裡讀取或寫入的每個檔案；案例存在只需要 `prompt.md` 或 `case.yaml`：

```
evals/
├── <case>/                        # one directory per case; nest under a non-case directory to group
│   ├── prompt.md                  # frontmatter: case and run fields; body: the prompt
│   ├── case.yaml                  # optional: context.* fields, or the whole case in one file
│   ├── graders/
│   │   └── <name>.md              # one grader per file; frontmatter: type and options; body: rubric
│   ├── mocks/                     # optional: mocks for this case only, same layout as below
│   └── <fixtures, scripts, transcripts referenced by case.yaml>
├── mocks/                         # optional: suite-wide MCP mocks
│   ├── <server>/
│   │   ├── <tool>.md              # one mocked tool; body: the tool result
│   │   ├── _server.md             # optional: one agent that answers several tools
│   │   ├── _tools.json            # optional: saved tools/list response for real descriptions and schemas
│   │   └── fixtures/              # files inserted with {{file:fixtures/...}}
│   └── .replay/<server>/          # adopted agent-mock recordings, answered without a model call
└── results/<timestamp>/           # written by each run; add results/ to .gitignore
    ├── aggregate-result.json
    ├── report.html
    └── mock-recordings/           # agent-mock answers from clean runs, with ADOPT.txt

```

### prompt.md frontmatter

`prompt.md` frontmatter 接受這些欄位。未知鍵是錯誤：

| Field                  | Default            | Purpose                                                                                                                                                                                                                                                                                                                                     |
| ---------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema_version`       | `"1.1"`，為您設定  | 案例格式版本。寫成 `prompt.md` 的案例會自動取得它，所以您很少設定它                                                                                                                                                                                                                                                                         |
| `name`                 | 目錄名稱           | 案例名稱。`--case` globs 符合它，報告以它為鍵                                                                                                                                                                                                                                                                                               |
| `description`          |                    | 供人類使用。在執行時不使用                                                                                                                                                                                                                                                                                                                  |
| `tags`                 | `[]`               | `--tag` 篩選的標籤。如果任何標籤符合，案例就會執行                                                                                                                                                                                                                                                                                          |
| `plugins`              | 最近的封閉 plugin  | 在測試中的 plugin 目錄，相對於案例目錄。當自動偵測找不到您的 plugin 時，設定 `plugins: ["../.."]`；請參閱 [the plugin didn’t load](https://code.claude.com/docs/zh-TW/plugin-evals#the-baseline-arm-shows-no-plugin-or-delta-is-zero)                                                                                                       |
| `runs`                 | `3`                | 每個 arm 的執行次數，1 到 50。`--runs` 覆蓋它                                                                                                                                                                                                                                                                                               |
| `expected_outcome`     |                    | 供人類使用。在執行時不使用                                                                                                                                                                                                                                                                                                                  |
| `model`                | 子工作階段的預設值 | 被測試代理的模型。`--model` 覆蓋它                                                                                                                                                                                                                                                                                                          |
| `max_turns`            | `10`               | 回合上限，最多 200。達到它會被記錄為執行錯誤，通常會降低分數，所以請慷慨設定                                                                                                                                                                                                                                                                |
| `timeout_seconds`      | `300`              | 每次執行的牆鐘上限，最多 3600                                                                                                                                                                                                                                                                                                               |
| `allowed_tools`        | `[]`               | 案例想要的工具，例如 `[Read, Glob, Grep, Skill]`。唯讀工具在此列出時被授予；對於其他任何東西，請參閱 [Grant tools](https://code.claude.com/docs/zh-TW/plugin-evals#grant-tools)                                                                                                                                                             |
| `append_system_prompt` |                    | 附加到子工作階段系統提示的文字                                                                                                                                                                                                                                                                                                              |
| `env`                  | `{}`               | 子工作階段的額外環境變數。鍵必須符合 `EVAL_[A-Z0-9_]*`；任何其他鍵都會導致執行失敗。執行只從您的 shell 繼承一個允許清單：基本項目如 `PATH` 和語言環境、代理和憑證設定、選擇和驗證您的模型提供者的變數、大多數 `ANTHROPIC_*` 和 `CLAUDE_CODE_*` 設定，以及 `EVAL_*`。要將任何其他東西交給 plugin，例如工具鏈設定，請將其匯出為 `EVAL_*` 變數 |

### case.yaml fields

`case.yaml` 以 YAML 描述相同案例並新增指向其他檔案的欄位。它需要 `schema_version: "1.1"` 和 `name`。`prompt.md` 欄位 `description`、`tags`、`plugins`、`runs` 和 `expected_outcome` 在頂層；`model`、`max_turns`、`timeout_seconds`、`allowed_tools`、`append_system_prompt` 和 `env` 在 `execution:` 下。當兩個檔案都存在時，`prompt.md` frontmatter 覆蓋匹配的 `case.yaml` 欄位，`prompt.md` 主體是提示，`graders/*.md` 在 `case.yaml` 中列出的任何評分器之後新增。 這些欄位僅存在於 `case.yaml` 中：

| Field                     | Purpose                                                                                                                                                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `context.scaffold_script` | 案例目錄中的 Bash 指令碼，在 Claude 啟動前在空工作區中執行，以建立 fixture 檔案或 git 儲存庫。它只在您傳遞 [`--scaffold`](https://code.claude.com/docs/zh-TW/plugin-evals#add-setup-or-history-with-case-yaml) 時執行 |
| `context.history_file`    | 案例目錄中的 `.jsonl` 文字記錄以繼續。案例的提示變成下一個使用者回合                                                                                                                                                  |
| `context.add_dirs`        | 案例目錄內的目錄，Claude 可能在執行期間讀取，被授予唯讀                                                                                                                                                               |
| `execution.prompt`        | 提示，當您將整個案例保留在 `case.yaml` 中並省略 `prompt.md` 時                                                                                                                                                        |
| `graders`                 | 評分器清單，每個都有一個 `name` 加上 `graders/*.md` 檔案在 frontmatter 中採用的相同鍵。對於 `llm` 評分器，將評分標準放在 `criteria` 中                                                                                |

### Grader frontmatter

`graders/` 下的每個評分器檔案在 frontmatter 中採用這些鍵，加上其類型的選項。評分器的名稱是沒有 `.md` 的檔案名稱：

| Key      | Default | Purpose                                                                                                                                                                                           |
| -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`   | 必需    | [grader types](https://code.claude.com/docs/zh-TW/plugin-evals#grader-types) 之一                                                                                                                 |
| `weight` | `1`     | 執行分數中的相對權重。任何正數                                                                                                                                                                    |
| `arm`    | 未設定  | `with-only` 在 [two-arm run](https://code.claude.com/docs/zh-TW/plugin-evals#compare-against-a-no-plugin-baseline) 中排除評分器的評分；`both` 強制 `tool_used: Skill` 評分器在兩個 arm 中都被評分 |

#### What a grader can look at

`regex` 評分器採用 `target`，`llm` 評分器採用 `focus`。兩者都接受相同的值：

| Value                            | What the grader sees                                                                                                                                                                                            |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `last_message`                   | Claude 的最終回應文字。這是預設值                                                                                                                                                                               |
| `trace`                          | 工作階段為 JSON，每行一條訊息。`regex` 評分器看到每條訊息；`llm` 評分器看到前 12 條和最後 12 條。其中的引號和換行符是 JSON 轉義的，所以 regex 符合 `\"` 而不是 `"`                                              |
| `files`                          | Claude 在執行期間建立的路徑清單，每行一個。不是它們的內容，也不是 scaffold 建立或 Claude 只修改的檔案                                                                                                           |
| `{ source: file, path: <path> }` | 執行後工作區中一個檔案的內容。使用此來評分 plugin 產生的內容。PNG、JPEG、GIF 或 WebP 檔案會作為影像顯示給 `llm` 評分器。`llm` 評分器拒絕其他二進位檔案，例如 `.pptx` 或 PDF；將它們渲染為影像或寫出為文字並評分 |
| `mock_calls`                     | Claude 對 [mocked MCP tool](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers) 進行的每次呼叫，及其輸入和 mock 的答案                                                                            |

#### Grader types

下面的每種評分器類型列出其選項和何時通過：

| Type          | Options                               | Passes when                                                                                                                                                                    |
| ------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `regex`       | `pattern`、`flags`、`match`、`target` | JavaScript regex `pattern` 在目標中被找到。設定 `match: not_contains` 以要求缺失或 `match: "count:N"` 以要求恰好 N 個符合。在 `flags: i` 中放置不區分大小寫；不支援內聯 `(?i)` |
| `tool_used`   | `tool`、`input_match`、`min`、`max`   | 對 `tool` 的呼叫次數，其 JSON 編碼的輸入符合可選的 `input_match` regex，介於 `min`（預設 1）和 `max`（預設無限制）之間。要聲稱工具從未被呼叫，請同時設定 `min: 0` 和 `max: 0`  |
| `tool_order`  | `before`、`after`                     | 兩個工具都被呼叫，第一個符合的 `before` 呼叫先於第一個符合的 `after` 呼叫。每個都是工具名稱或 `{ tool, input_match }`                                                          |
| `file_exists` | `path`、`exists`                      | Claude 建立的檔案符合 `path` glob，或沒有符合 `exists: false` 的。只有在執行期間建立的檔案計數                                                                                 |
| `llm`         | `criteria`、`focus`                   | 評分器模型在至少三票中的兩票對評分標準投票通過。在 `.md` 佈局中，檔案主體是評分標準                                                                                            |
| `baseline`    | `baseline_file`、`criteria`           | 評分器發現執行至少與 `baseline_file`（案例目錄中的 `.jsonl`）的參考文字記錄一樣好地滿足評分標準                                                                                |

### Mock files

`mocks/<server>/` 下的 `<tool>.md` 檔案回答一個工具。其主體是工具結果，具有 `{{input.<field>}}` 和 `{{file:fixtures/<name>}}` 替換。其 frontmatter 接受這些鍵：

| Key                                          | Default | Purpose                                                                                                                                                                                                     |
| -------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                                       | `fixed` | `fixed` 按原樣返回主體。`agent` 將主體視為小型模型的指示，該模型為執行播放伺服器並將較早的呼叫視為歷史                                                                                                      |
| `expect`                                     | 未設定  | 從點分輸入路徑到類型名稱（例如 `string`、`number`、`boolean`、`array` 或 `object`）、`/regex/`、字面值或允許的字面值清單的對應。違反它的呼叫會以分數 0 中止執行，並報告為 `aborted`，包含伺服器、工具和原因 |
| `error`                                      | `false` | 僅 `fixed`。將主體作為工具錯誤返回                                                                                                                                                                          |
| `abort_when`                                 | 未設定  | 僅 `agent`。散文列出代理可能中止執行的唯一條件                                                                                                                                                              |
| 兩個可選檔案位於伺服器目錄中的工具檔案旁邊： |         |                                                                                                                                                                                                             |

- **`_server.md`**：一個單一的`type: agent` mock，回答多個工具，在其 `tools:` frontmatter 鍵中列出。相同工具的 `<tool>.md` 優先。在個別 `<tool>.md` 上放置 `expect:` 保護，而不是這裡
- **`_tools.json`**：來自真實伺服器的已保存`tools/list` 回應，因此 mocked 工具帶有其真實描述和輸入架構，而不是寬鬆的佔位符

案例自己的 `mocks/` 目錄使用相同的佈局並逐檔案覆蓋套件的 mocks。

## Troubleshooting

這些是作者最常遇到的問題，按您看到的內容鍵入。

### “plugin eval is currently in early access”

您的建置早於命令的正式發佈。執行 `claude update`，然後在新工作階段中再次執行命令。

### “plugin eval is currently unavailable”

Anthropic 已在伺服器端關閉命令。您的機器上沒有任何內容將其打開；執行 `claude update` 並稍後在新工作階段中重試。

### “is not a trusted plugin directory, and this run cannot stop to ask you about it”

這是針對目錄的第一次執行，Claude Code 還不信任，並且因為 stdin 或 stdout 不是終端或您傳遞了 `--json` 而無法詢問。在終端中執行 `claude plugin eval <dir>` 一次並回答提示，或如果您信任 plugin 的程式碼和套件，請傳遞 `--trust-plugin`。請參閱 [What a run can access](https://code.claude.com/docs/zh-TW/plugin-evals#security)。

### “No eval cases found”

eval 目錄下沒有 `<case>/prompt.md` 或 `<case>/case.yaml` 存在，或您的 `--case` 和 `--tag` 篩選器沒有匹配任何案例。從 plugin 根目錄執行，或執行 `claude plugin eval init` 以建立套件。

### The baseline arm shows no plugin, or delta is zero

如果摘要沒有 `W/OUT` 列，或案例失敗並顯示「ablation requested but no plugin resolved」，則沒有為案例找到 plugin。將 `plugins: ["../.."]` 新增到案例，給出從案例目錄到 plugin 目錄的路徑。 如果 plugin 確實載入並且 `Δ` 仍然接近零，您的 `tool_used: Skill` 評分器失敗，這通常是真實發現，意味著 skill 的 `description` 不會在提示的措辭上觸發。調整描述並重新執行相同的套件。

### Everything scores zero although the right files were produced

您的評分器目標 `files`（建立的路徑列表），當您指的是檔案的內容時。使用 `{ source: file, path: <path> }` 作為 `target` 或 `focus`。另外，`file_exists` 僅計算執行期間建立的檔案，因此 scaffold 建立或 Claude 僅編輯的檔案對它不可見；評分其內容，或在 `Edit` 上使用 `tool_used`。

### A regex over the trace doesn’t match text I can see

預設 `target` 是 `last_message`，不是 trace。當您確實目標 `trace` 時，它是每行 JSON，因此引號顯示為 `\"`。正規表達式使用 JavaScript 語法，因此在 `flags` 中放置 `i` 而不是編寫 `(?i)`。

### Tools are denied, MCP tools are missing, or Bash won’t run

超過唯讀集的任何內容都需要您的授予，例如 `--allow-tools Bash Write`。您的個人 MCP 伺服器永遠不會在執行中載入。plugin 自己的伺服器不會啟動，除非您 [opt in](https://code.claude.com/docs/zh-TW/plugin-evals#mock-mcp-servers)，其工具也需要 `--allow-tools "mcp__plugin_<plugin>_<server>__*"` 授予；mocked 工具不需要任何一個。

### The run exits 1 but the results look fine

預設 `--threshold` 是 1.0，因此當任何案例評分低於完美時，命令退出 1。設定與您的標準相符的閾值。退出 1 也涵蓋案例檔案無法載入，在表格上方的 stderr 上報告。

### “—json output path must end in .json”

您將目標放在 `--json` 之後，因此它被讀取為輸出路徑。將目標放在首位，如 `claude plugin eval . --json`，或給 `--json` 一個明確的 `.json` 路徑。

### A grader shows passed: false under a run that scored 1.0

該評分器在兩個 arm 執行中按設計從分數中排除，其 `scored` 欄位為 `false`。請參閱 [Compare against a no-plugin baseline](https://code.claude.com/docs/zh-TW/plugin-evals#compare-against-a-no-plugin-baseline)。

### Runs fail with a usage-limit or rate-limit error partway through

如果您的帳戶在套件執行時達到其方案的使用限制或 API 速率限制，每次後續執行都會以該錯誤結束，根據其產生的內容進行評分，通常評分為 0。套件仍然完成並未標記為 `partial`，因此結果可能看起來像迴歸。在信任分數之前檢查 `NOTES` 列或 JSON 中的 `cases[].arms.with[].error` 以獲取限制訊息，然後在限制重置後重新執行，如果您需要保持在其下方，則使用 `--runs 1` 或 `--case` 篩選器。

### Runs time out or hit the turn cap

預設值是 10 轉和 300 秒。在案例中提高 `max_turns` 和 `timeout_seconds` 以進行需要更多的任務，並使用 `--max-cost-usd` 作為成本上限而不是緊密的每次執行限制。

## See also

- [Create plugins](https://code.claude.com/docs/zh-TW/plugins)：建立您正在測試的 plugin，並在開發期間使用 `--plugin-dir` 載入它
- [Plugins reference](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-eval)：`plugin eval` 和 `plugin eval init` 命令項目以及資訊清單的 `experimental.evals` 鍵
- [Skills](https://code.claude.com/docs/zh-TW/skills)：skill 的描述如何決定 Claude 何時呼叫它，這是檢查 skill 是否觸發的案例測量的內容
- [Sandboxing](https://code.claude.com/docs/zh-TW/sandboxing)：當您授予 Bash 執行時適用的 OS 級沙箱
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces)：一旦其套件通過，發佈 plugin

是否 助手