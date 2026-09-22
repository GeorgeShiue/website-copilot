Skills 擴展了 Claude 能做的事情。建立一個 `SKILL.md` 檔案，其中包含指示，Claude 就會將其新增到其工具組中。Claude 在相關時使用 skills，或者您可以使用 `/skill-name` 直接叫用一個。 當您不斷將相同的指示、檢查清單或多步驟程序貼到聊天中時，或當 CLAUDE.md 的某個部分已經發展成程序而不是事實時，請建立一個 skill。與 CLAUDE.md 內容不同，skill 的主體只在使用時載入，因此長參考資料在您需要之前幾乎不需要任何成本。 如需內建命令（如 `/help` 和 `/compact`）以及捆綁的 skills（如 `/debug` 和 `/code-review`），請參閱[命令參考](https://code.claude.com/docs/zh-TW/commands)。**自訂命令已合併到 skills 中。** `.claude/commands/deploy.md` 中的檔案和 `.claude/skills/deploy/SKILL.md` 中的 skill 都會建立 `/deploy` 並以相同方式運作。您現有的 `.claude/commands/` 檔案會繼續運作。Skills 新增了選用功能：支援檔案的目錄、[控制您或 Claude 是否叫用它們](https://code.claude.com/docs/zh-TW/skills#control-who-invokes-a-skill)的 frontmatter，以及 Claude 在相關時自動載入它們的能力。 Claude Code skills 遵循 [Agent Skills](https://agentskills.io) 開放標準，該標準適用於多個 AI 工具。Claude Code 使用額外功能擴展了該標準，例如[叫用控制](https://code.claude.com/docs/zh-TW/skills#control-who-invokes-a-skill)、[子代理執行](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)和[動態上下文注入](https://code.claude.com/docs/zh-TW/skills#inject-dynamic-context)。請參閱[在 Claude Code 外使用 skill frontmatter](https://code.claude.com/docs/zh-TW/skills#using-skill-frontmatter-outside-claude-code)，了解哪些 frontmatter 欄位是標準的一部分，哪些是 Claude Code 擴展。

## 捆綁技能

Claude Code 包含一組捆綁技能，例如 `/doctor`、`/code-review`、`/batch`、`/debug`、`/loop` 和 `/claude-api`。捆綁技能是基於提示的：它們為 Claude 提供詳細的指示，並讓它使用其工具來協調工作。大多數內建命令則直接執行固定邏輯。 您可以透過輸入 `/` 後跟技能名稱的方式來調用捆綁技能，就像調用任何其他技能一樣。Claude 會在相關時自動調用某些捆綁技能；其他技能（包括 `/verify`）只有在您調用時才會執行，這讓您可以控制這些耗時較長的檢查何時花費時間和 token。 大多數捆綁技能在每個工作階段中都可用。少數技能取決於特定功能：例如 `/workflow-authoring` 只有在[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)啟用時才可用。 若要關閉捆綁技能，請使用 [`disableBundledSkills`](https://code.claude.com/docs/zh-TW/settings-reference#disablebundledskills) 設定。 在 Claude Code v2.1.205 及更新版本中，當 `disableBundledSkills` 開啟時，[`/doctor`](https://code.claude.com/docs/zh-TW/commands#all-commands) 設定檢查仍可輸入。若要隱藏它，請設定 `DISABLE_DOCTOR_COMMAND` 環境變數或 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 項目 `"doctor": "off"`。在 v2.1.205 之前，`/doctor` 是內建命令而非捆綁技能。 捆綁技能與內建命令一起列在[命令參考](https://code.claude.com/docs/zh-TW/commands)中，在「用途」欄中標記為**技能** 。

### 執行並驗證您的應用程式

三個捆綁技能協同工作以啟動您的應用程式，並根據執行中的應用程式而非僅測試來確認變更：

| 技能                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 用途                                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `/run`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 啟動並驅動您的應用程式以查看變更是否有效                                         |
| `/verify`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 建置並執行您的應用程式以確認程式碼變更是否達到預期效果，無需回退到測試或型別檢查 |
| `/run-skill-generator`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 教導 `/run` 和 `/verify` 如何建置和啟動您的專案                                  |
| `/run` 和 `/verify` 無需設定即可運作。它們會根據您的專案類型（CLI、伺服器、TUI、瀏覽器驅動）以及 README、`package.json` 或 `Makefile` 中的內容推斷啟動方式。對於需要超出標準啟動範圍的專案（資料庫、env 檔案、圖形工作階段、多步驟建置），該推斷變得不可靠。 `/run-skill-generator` 會改為記錄配方。它從乾淨環境中讓您的應用程式執行，捕捉有效的內容（安裝命令、環境變數、啟動指令碼），並將其提交為位於 `.claude/skills/run-<name>/` 的每個專案技能。之後，`/run`、`/verify` 和儲存庫中的任何其他代理都會遵循記錄的配方，而不是重新發現它。每個專案執行一次 `/run-skill-generator`，如果建置或啟動程序變更，則再執行一次。 `/verify` 也可以記錄自己的配方。當它必須在沒有記錄配方的情況下建置和驅動您的應用程式時，它會將有效的內容寫入儲存庫根目錄的 `.claude/skills/verify/SKILL.md`，或在 monorepo 中的觸及套件目錄中，以便稍後的執行和其他代理遵循相同的步驟。在儲存庫根目錄，記錄的技能會取代捆綁的 `/verify`。這需要 Claude Code v2.1.200 或更新版本。 Claude 只有在引導執行出錯時（例如失敗的命令或缺少的步驟）才會編輯記錄的檔案，因此您可以提交檔案而無需每個工作階段的差異。在 v2.1.205 之前，捆綁技能告訴 Claude 要折疊執行學到的任何內容，這導致頻繁的合併衝突。 |                                                                                  |

## 開始使用

### 建立您的第一個 skill

此範例建立一個 skill，可以總結您 git 儲存庫中未提交的變更，並標記任何有風險的項目。它會在 Claude 讀取之前將即時差異拉入提示中，因此回應是基於您的實際工作樹，而不是 Claude 從開啟的檔案中猜測的內容。當您詢問您的變更時，Claude 會自動載入該 skill，或者您可以使用 `/summarize-changes` 直接叫用它。 1 建立 skill 目錄 在您的個人 skills 資料夾中為該 skill 建立一個目錄。個人 skills 可在所有專案中使用。

```
mkdir -p ~/.claude/skills/summarize-changes

```

2 編寫 SKILL.md 每個 skill 都需要一個 `SKILL.md` 檔案，包含兩個部分：`---` 標記之間的 YAML frontmatter，告訴 Claude 何時使用該 skill，以及包含 Claude 在 skill 執行時遵循的指示的 markdown 內容。目錄名稱會變成您輸入的命令，而 `description` 可幫助 Claude 決定何時自動載入該 skill。將此儲存到 `~/.claude/skills/summarize-changes/SKILL.md`：

```
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.

```

`!`git diff HEAD\`\` 這一行使用[動態內容注入](https://code.claude.com/docs/zh-TW/skills#inject-dynamic-context)：Claude Code 執行該命令，並在 Claude 看到 skill 內容之前將該行替換為其輸出，因此指示會隨著目前的差異已內聯而到達。 3 測試 skill 開啟一個 git 專案，對任何檔案進行小編輯，並透過執行 `claude` 啟動 Claude Code。您可以透過兩種方式測試該 skill。**讓 Claude 自動叫用它** ，方法是詢問與描述相符的內容：

```
What did I change?

```

**或使用 skill 名稱直接叫用它** ：

```
/summarize-changes

```

無論哪種方式，Claude 都應該以您編輯的簡短摘要和風險清單進行回應。

## 選擇技能的載入位置

技能的儲存位置決定了哪些工作階段會載入它。將其儲存在主目錄下，可在每個專案中使用；將其提交到儲存庫，可與該處的所有人共享；或透過外掛程式或受管設定分發，以覆蓋整個團隊。

| 位置                       | 路徑                                                                                                                               | 載入於                                                                                                                                                                                                                   |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 企業                       | `.claude/skills/<skill-name>/SKILL.md` 在[受管設定目錄](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)中 | 您的組織部署它的機器上的所有使用者                                                                                                                                                                                       |
| 個人                       | `~/.claude/skills/<skill-name>/SKILL.md`                                                                                           | 此機器上的所有專案，但不包括[協作或雲端工作階段](https://code.claude.com/docs/zh-TW/skills#skills-in-cowork-and-cloud-sessions)                                                                                          |
| 專案                       | `.claude/skills/<skill-name>/SKILL.md`                                                                                             | 此儲存庫中的工作階段。提交它，您的團隊也會獲得它                                                                                                                                                                         |
| 巢狀                       | `<subdir>/.claude/skills/<skill-name>/SKILL.md`                                                                                    | 在 `<subdir>` 中或其下方啟動的工作階段。在上方啟動的工作階段在 Claude 處理該處的檔案時會載入技能一次。請參閱[單一儲存庫和子目錄](https://code.claude.com/docs/zh-TW/skills#discovery-from-parent-and-nested-directories) |
| 其他目錄                   | `.claude/skills/<skill-name>/SKILL.md` 在您使用 `--add-dir` 傳遞的目錄中                                                           | 該工作階段。請參閱[專案外的目錄](https://code.claude.com/docs/zh-TW/skills#skills-from-additional-directories)                                                                                                           |
| 外掛程式                   | `<plugin>/skills/<skill-name>/SKILL.md`                                                                                            | [外掛程式](https://code.claude.com/docs/zh-TW/plugins)啟用的任何位置，作為 `/plugin-name:skill-name`                                                                                                                     |
| claude.ai 帳戶             | 為您的 claude.ai 帳戶啟用的技能                                                                                                    | 協作和雲端工作階段，以及您使用該帳戶登入的終端工作階段。請參閱[從 claude.ai 同步的技能](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave)                                                              |
| 技能資料夾也遵循這些規則： |                                                                                                                                    |                                                                                                                                                                                                                          |

- **符號連結資料夾** ：企業、個人或專案位置中的 `<skill-name>` 項目可以是指向磁碟上其他位置的目錄的符號連結。Claude Code 從目標讀取 `SKILL.md` 並載入技能一次，即使多個位置指向同一目標。外掛程式技能[以不同方式處理符號連結](https://code.claude.com/docs/zh-TW/plugins-reference#share-files-within-a-marketplace-with-symlinks)。
- **保留名稱** ：不要將技能資料夾命名為 `synced`，無論大小寫如何。Claude Code 使用 `~/.claude/skills/synced/` 來[儲存從 claude.ai 下載的技能](https://code.claude.com/docs/zh-TW/skills#where-synced-skills-load)，並跳過您在企業、個人和專案位置中以該名稱編寫的技能。
- **命令檔案** ：`.claude/commands/` 中的 Markdown 檔案是較舊的格式，仍然有效。它支持相同的[前置資料](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference)，除了 `name` 和 `paths`。若要找到您輸入以叫用它的名稱，請參閱[技能如何獲得其命令名稱](https://code.claude.com/docs/zh-TW/skills#how-a-skill-gets-its-command-name)。對於新工作，建議使用技能，因為技能也支持[支援檔案](https://code.claude.com/docs/zh-TW/skills#add-supporting-files)。
- **技能資料夾作為外掛程式** ：將 `.claude-plugin/plugin.json` 新增到技能資料夾，它會載入為[外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)，名稱為 `<name>@skills-dir`，因此它可以捆綁代理、hooks 和 MCP 伺服器。在專案的 `.claude/skills/` 中，這需要先接受工作區信任對話。

### 在單一儲存庫和子目錄中載入技能

Claude Code 從啟動它的目錄中的 `.claude/skills/` 以及直到儲存庫根目錄的每個父目錄中載入專案技能，因此在 `packages/frontend/` 中啟動仍會拾取在根目錄定義的技能。當您在 v2.1.246 或更新版本上[使用 `/cd` 移動工作階段](https://code.claude.com/docs/zh-TW/permissions#move-the-session-to-another-directory)時，Claude Code 會新增新目錄的專案技能。 `.claude/skills/` 目錄中啟動位置下方的技能在啟動時不會載入。它們在 Claude 首次讀取或編輯該子目錄中的檔案時載入，並在工作階段的其餘時間保持可用。在此之前，它們不會出現在 `/` 功能表中，您無法按名稱叫用它們。若要更快載入它們，請使用子目錄的路徑執行 `/add-dir`，這需要 Claude Code v2.1.257 或更新版本。 當巢狀技能與另一個技能共享名稱時，兩者都保持可用。在儲存庫根目錄有 `deploy` 技能，在 `apps/web/.claude/skills/` 中有另一個：

- `/deploy` 執行根技能。Claude Code 也會為 Claude 列出目錄限定的變體，並提供指示以叫用其目錄保存它正在處理的檔案的變體，因此巢狀技能仍適用於 `apps/web/` 中的工作。
- `/apps/web:deploy` 單獨執行巢狀技能。其描述命名它適用的目錄。

### 從專案外的目錄載入技能

當您使用 `--add-dir` 或 `/add-dir` 新增目錄時，Claude Code 會載入該目錄的 `.claude/skills/` 中的技能，以及其 `.claude/commands/` 和 `.claude/agents/`。Agent SDK 透過 TypeScript 中的 [`additionalDirectories`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options) 或 Python 中的 [`add_dirs`](https://code.claude.com/docs/zh-TW/agent-sdk/python#claudeagentoptions) 新增的目錄以相同方式載入，因為 SDK 將它們作為 `--add-dir` 傳遞。`settings.json` 中的 `permissions.additionalDirectories` 設定僅授予檔案存取權限，不載入這些中的任何一個。 Claude Code 監視您在啟動時使用 `--add-dir` 傳遞的目錄中的 `.claude/skills/`，如[在工作階段期間編輯技能](https://code.claude.com/docs/zh-TW/skills#live-change-detection)所述。它不監視新增目錄的 `.claude/commands/` 或 `.claude/agents/`，因此在更改該處的檔案後重新啟動工作階段。 這些載入取決於 `project` [設定來源](https://code.claude.com/docs/zh-TW/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources)，預設為開啟。[`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization) 原則、[裸機模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)和 [`--safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 各自進一步限制它們，如這些頁面所述。請參閱[其他目錄授予檔案存取權限，而非設定](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration)以了解新增目錄載入的完整表格，包括 `CLAUDE.md` 和外掛程式設定。

### 解決共享名稱的技能

當兩個技能共享名稱時，每個技能來自的位置決定了 `/name` 執行的是哪一個。該表涵蓋企業、個人、專案、巢狀、外掛程式和 claude.ai 位置、捆綁技能和命令檔案：

| 相同名稱在                                                                                                          | 執行哪一個                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 企業、個人和專案中的兩個                                                                                            | 企業優於個人，個人優於專案。在 `~/.claude/skills/` 和專案的 `.claude/skills/` 中都有 `deploy` 時，`/deploy` 執行個人的                                                                                 |
| 這些位置中的任何一個和[捆綁技能](https://code.claude.com/docs/zh-TW/skills#bundled-skills)                          | 您的技能替換捆綁命令，但不替換其別名。專案 `code-review` 技能替換 `/code-review`，捆綁別名 `/review` 永遠不會執行您的技能                                                                              |
| 技能和 `.claude/commands/` 中的檔案                                                                                 | 技能                                                                                                                                                                                                   |
| 專案根技能和巢狀技能                                                                                                | 兩者都載入。請參閱[單一儲存庫和子目錄](https://code.claude.com/docs/zh-TW/skills#discovery-from-parent-and-nested-directories)                                                                         |
| 外掛程式技能和上述任何位置的技能                                                                                    | 兩者都載入，因為外掛程式技能被命名為 `/plugin-name:skill-name`                                                                                                                                         |
| 上述任何一個和[從您的 claude.ai 帳戶同步的技能](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave) | 另一個技能或命令。同步技能仍作為 `/anthropic-skills:<name>` 執行。請參閱[當同步技能名稱與另一個命令相符時](https://code.claude.com/docs/zh-TW/skills#when-a-synced-skill-name-matches-another-command) |

### 在協作和雲端工作階段中使用技能

[協作](https://claude.com/product/cowork)工作階段和[雲端工作階段](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)，包括[例行工作](https://code.claude.com/docs/zh-TW/routines)，不會讀取您機器上的 `~/.claude/skills/`。互動式和排程協作工作階段都會載入為您的 claude.ai 帳戶啟用的技能，在工作階段開始時同步；從桌面應用程式側邊欄中的**自訂** 或從 claude.ai 上的技能設定管理它們。雲端工作階段另外載入提交到複製儲存庫的 `.claude/skills/` 的專案技能。 如果技能僅存在於您機器上的 `~/.claude/skills/` 中，當[例行工作](https://code.claude.com/docs/zh-TW/routines)叫用它時，Claude Code 會報告找不到該技能，因為每次例行工作執行都會作為新的雲端工作階段啟動。若要在這些工作階段中提供個人技能：

- 對於協作和雲端工作階段，為您的 claude.ai 帳戶啟用該技能。
- 對於雲端工作階段，您可以改為將技能提交到儲存庫的 `.claude/skills/`，或在儲存庫的 `.claude/settings.json` 中宣告的外掛程式中提供它。儲存庫宣告的外掛程式[在工作階段開始時安裝](https://code.claude.com/docs/zh-TW/cloud-environments#what-carries-over-from-your-setup)；僅在您的使用者設定中啟用的外掛程式不會轉移。

[桌面排程工作](https://code.claude.com/docs/zh-TW/desktop-scheduled-tasks)在您的機器上本機執行，因此它們確實載入 `~/.claude/skills/`。

### 從 claude.ai 同步的技能

本節適用於您，如果您使用協作或雲端工作階段，或在終端中使用 claude.ai 帳戶登入 Claude Code。在這些工作階段中，Claude Code 會載入為您的 claude.ai 帳戶啟用的技能，無需您進行任何設定，如[同步技能的載入位置](https://code.claude.com/docs/zh-TW/skills#where-synced-skills-load)所述。這些技能包括您在 claude.ai 設定中建立或開啟的技能、您的組織在那裡提供的技能，以及 Anthropic 的內建技能，例如 `pdf` 和 `xlsx`。 Claude Code 從您的帳戶下載同步技能，而不是讀取您在執行工作階段的機器上編寫的檔案，因此它對同步技能應用不適用於您儲存在[技能位置](https://code.claude.com/docs/zh-TW/skills#where-skills-live)中的技能的規則。

#### 同步技能的載入位置

在協作或雲端工作階段中，Claude Code 載入為您的 claude.ai 帳戶啟用的技能，[協作和雲端工作階段中的技能](https://code.claude.com/docs/zh-TW/skills#skills-in-cowork-and-cloud-sessions)說明如何選擇這些工作階段獲得的技能。 在您的終端中，Claude Code 在您使用 claude.ai 帳戶登入的工作階段中同步這些技能。當工作階段啟動時，Claude Code 會在背景中將您帳戶的技能下載到 `~/.claude/skills/synced/`，然後在工作階段執行時大約每 10 分鐘檢查一次 claude.ai 是否有變更。當檢查發現技能在 claude.ai 上被新增、編輯或關閉時，Claude Code 會在執行中的工作階段中新增、更新或移除它，無需重新啟動。終端工作階段中的同步需要 Claude Code v2.1.273 或更新版本。 同步永遠不會延遲啟動，因為 Claude 只在叫用技能時才等待技能的下載。因此，短[非互動式](https://code.claude.com/docs/zh-TW/headless)執行可能在新增的技能下載之前完成，在這種情況下，稍後的工作階段會下載它。若要讓非互動式執行下載您的技能並在回答提示之前等待清單，請將 [`CLAUDE_CODE_SYNC_SKILLS`](https://code.claude.com/docs/zh-TW/env-vars#variables) 設定為 `1`。 Claude Code 僅在使用您的 claude.ai 帳戶登入的工作階段中同步，並[從 Anthropic 取得功能旗標](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)。它不在這些工作階段中同步：

- 不使用 `/login` 儲存的登入的工作階段，例如使用 API 金鑰驗證的工作階段，或 `ANTHROPIC_AUTH_TOKEN`、`CLAUDE_CODE_OAUTH_TOKEN` 或 `apiKeyHelper` 指令碼提供認證的工作階段
- 不取得功能旗標的工作階段，例如 Amazon Bedrock 上的工作階段或您設定 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 的工作階段
- [裸機模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)中的工作階段或您使用 `--safe-mode` 啟動的工作階段
- 您的組織的受管設定[將技能鎖定到外掛程式來源](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization-skills)的工作階段，或您使用[`--setting-sources`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)清單啟動的工作階段，該清單省略了 `user`

如果您在工作階段期間使用 `/login` 登入，請重新啟動 Claude Code 以開始同步。 較早工作階段同步的技能保留在磁碟上。Claude Code 在稍後使用相同帳戶登入的工作階段中載入它們，即使它無法連接到 claude.ai。 若要查看哪些技能已同步，請執行 `/skills`。功能表在 `claude.ai sync` 下列出它們。 Anthropic 的某些技能，例如 `pdf` 和 `xlsx`，始終同步。對於其餘的，在 claude.ai 上的技能設定中開啟或關閉技能以變更它是否同步。 若要停止在機器上同步，請在您的使用者設定中將 [`syncClaudeAiSkills`](https://code.claude.com/docs/zh-TW/settings-reference#syncclaudeaiskills) 設定為 `false`。Claude Code 停止下載，下次啟動時會將已同步的技能移動到 `~/.claude/skills/.trash/`，並不再載入它們。您的組織可以透過在 claude.ai 上關閉技能來為所有人關閉同步。若要在保持技能開啟的情況下停止同步，它可以在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中設定相同的金鑰。 如果您的組織在 claude.ai 上關閉技能，Claude Code 會移除下載的技能，它們停止載入。移除的技能會移動到 `~/.claude/skills/.trash/`，您可以在[保留掃描](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)刪除它們之前復原檔案。一旦您的組織重新開啟技能，Claude Code 會在下次同步時下載您啟用的技能。

#### 當同步技能名稱與另一個命令相符時

您可以透過其完整名稱 `/anthropic-skills:<name>` 或其短名稱 `/<name>` 叫用同步技能。當另一個命令使用該短名稱時，`/<name>` 執行另一個命令，同步技能僅作為 `/anthropic-skills:<name>` 執行。在本機 `deploy` 技能和同步 `deploy` 的情況下，`/deploy` 執行本機技能，`/anthropic-skills:deploy` 執行同步技能。在 v2.1.269 之前，同步技能僅有其短名稱。 另一個命令可以是以下任何一個：

- 內建命令或[捆綁技能](https://code.claude.com/docs/zh-TW/skills#bundled-skills)，包括在您的工作階段中不可用的命令，例如在您關閉捆綁技能後
- 任何[本機層級](https://code.claude.com/docs/zh-TW/skills#where-skills-live)的技能或 `.claude/commands/` 中的檔案
- 外掛程式技能
- [MCP 提示](https://code.claude.com/docs/zh-TW/mcp#use-mcp-prompts-as-commands)

Claude Code 標籤同步技能，以便您可以判斷它們來自何處。`/skills` 功能表和 `/context` 在 `claude.ai sync` 下分組同步技能，`/` 命令功能表將它們標記為來自 claude.ai。 比較名稱時，Claude Code 忽略大小寫、間距和不可見字元，並將相容性形式（如全寬字母和破折號變體）視為其純等效項。例如，名為 `Commit` 的同步技能和名為 `commit` 的本機技能計為相同名稱，因此 `/commit` 繼續執行您的本機技能。 僅因另一個字母表中的相似字母而不同的名稱計為不同名稱，`claude.ai sync` 標籤是您區分兩者的方式。這些檢查和標籤需要 Claude Code v2.1.228 或更新版本。

#### Claude Code 如何處理同步技能的前置資料

Claude Code 對同步技能的前置資料應用兩個規則：

- Claude Code 在每種工作階段中都遵守前置資料，因此 `allowed-tools` 授予會通過正常的[權限流程](https://code.claude.com/docs/zh-TW/permissions)。
- Claude Code 清理技能提供的顯示文字，例如其描述。它移除控制字元，在到達 Claude 的文字（例如描述）中，它也會逸出角括號，以便文字無法模仿 Claude Code 的內部格式。此清理需要 Claude Code v2.1.228 或更新版本。

#### Claude Code 如何處理同步技能的主體

Claude Code 對同步技能主體的處理取決於工作階段執行的位置：

- 在雲端工作階段中，主體保持本機技能具有的行為，因為工作階段在隔離容器中執行。
- 在您桌面上的協作工作階段中，主體保持本機技能具有的行為，除了 Claude Code 將每個 `!` 命令行替換為 [`disableSkillShellExecution` 預留位置](https://code.claude.com/docs/zh-TW/skills#inject-dynamic-context)，就像它對您在那裡提供的每個技能所做的一樣。
- 在您機器上的任何其他工作階段中，Claude Code 不執行 [`!` 命令](https://code.claude.com/docs/zh-TW/skills#inject-dynamic-context)，不附加 `@` 參考命名的檔案（就像它對本機技能所做的那樣），也不替換 `${CLAUDE_PROJECT_DIR}` 和 `${CLAUDE_SESSION_ID}` 預留位置，因此 `@` 參考和兩個預留位置都作為字面文字到達 Claude。`!` 命令行也作為字面文字到達 Claude，或在 `disableSkillShellExecution` 開啟時作為該預留位置。此處理需要 Claude Code v2.1.228 或更新版本。

### 在工作階段期間編輯技能

Claude Code 監視技能目錄的檔案變更，除了在[裸機模式](https://code.claude.com/docs/zh-TW/headless#start-faster-with-bare-mode)中。當您在 `~/.claude/skills/`、專案 `.claude/skills/` 或 `--add-dir` 目錄內的 `.claude/skills/` 下新增、編輯或移除技能時，Claude Code 在目前工作階段內拾取變更，無需重新啟動。如果您建立工作階段啟動時不存在的頂層技能目錄，請重新啟動 Claude Code，以便它可以監視新目錄。 即時變更偵測僅涵蓋 `SKILL.md` 文字。對於也是[外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)的技能資料夾，`hooks/`、`.mcp.json`、`agents/` 和 `output-styles/` 的變更需要 `/reload-plugins` 才能生效。

### 移除技能

移除技能的方式取決於它來自何處：

- **個人或專案技能** ：刪除技能的目錄，`~/.claude/skills/<skill-name>/` 或 `.claude/skills/<skill-name>/`。Claude Code [在目前工作階段中將其從 `/skills` 中移除](https://code.claude.com/docs/zh-TW/skills#live-change-detection)；Claude Code 已從其載入的內容遵循[技能內容生命週期](https://code.claude.com/docs/zh-TW/skills#skill-content-lifecycle)。
- **企業技能** ：管理員從[受管設定目錄](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)內的 `.claude/skills/` 刪除技能的目錄，例如 Linux 上的 `/etc/claude-code/.claude/skills/<skill-name>/`。
- **外掛程式技能** ：從 `/plugin` 功能表禁用或卸載提供它的外掛程式，或使用 `/plugin uninstall <plugin-name>@<marketplace-name>`。Claude Code 在[變更應用](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)時或當您重新啟動時卸載外掛程式的技能。
- **從 claude.ai 同步的技能** ：在您[啟用它](https://code.claude.com/docs/zh-TW/skills#skills-in-cowork-and-cloud-sessions)的相同位置為您的 claude.ai 帳戶關閉該技能。Claude Code 在下次[同步您的技能](https://code.claude.com/docs/zh-TW/skills#where-synced-skills-load)時將其從 `~/.claude/skills/synced/` 中移除。如果您改為手動刪除目錄，下次同步會在技能在 claude.ai 上保持啟用時再次下載它。
- **捆綁技能** ：設定 [`disableBundledSkills`](https://code.claude.com/docs/zh-TW/skills#bundled-skills) 為 `true` 以關閉捆綁技能，或在 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 中將一個技能設定為 `"off"` 以隱藏它。

若要保留個人或專案技能但停止 Claude 自動叫用它，請在其前置資料中設定 [`disable-model-invocation: true`](https://code.claude.com/docs/zh-TW/skills#control-who-invokes-a-skill)，或在不想編輯檔案時在 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 中設定 `"user-invocable-only"`。

## 設定 skills

Skills 透過位於 `SKILL.md` 頂部的 YAML frontmatter 和隨後的 markdown 內容進行設定。

### Skills 內容的類型

Skill 檔案可以包含任何指示，但思考您想如何調用它們有助於指導應該包含的內容： **參考內容** 新增 Claude 應用於您目前工作的知識。慣例、模式、風格指南、領域知識。此內容以內聯方式運行，因此 Claude 可以將其與您的對話上下文一起使用。

```
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation

```

**任務內容** 為特定操作（如部署、提交或程式碼生成）提供 Claude 逐步指示。這些通常是您想直接使用 `/skill-name` 調用的操作，而不是讓 Claude 決定何時運行它們。新增 `disable-model-invocation: true` 以防止 Claude 自動觸發它。下面的範例新增了 `context: fork`，它在自己的 subagent 上下文中運行 skill；請參閱[在 subagent 中運行 skills](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)。

```
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target

```

保持主體本身簡潔。一旦 skill 載入，其內容[在各個回合中保持在上下文中](https://code.claude.com/docs/zh-TW/skills#skill-content-lifecycle)，因此每一行都是一個重複的 token 成本。說明要做什麼，而不是敘述如何或為什麼，並應用與[CLAUDE.md 內容](https://code.claude.com/docs/zh-TW/best-practices#write-an-effective-claude-md)相同的簡潔性測試。

### Frontmatter 參考

除了 markdown 內容外，您可以使用位於 `SKILL.md` 檔案頂部 `---` 標記之間的 YAML frontmatter 欄位來設定 skill 行為：

```
---
name: my-skill
description: What this skill does
disable-model-invocation: true
allowed-tools: Read Grep
---

Your skill instructions here...

```

所有欄位都是選用的。只建議使用 `description`，以便 Claude 知道何時使用該 skill。 Claude Code 僅在開啟的 `---` 是檔案的第一行時才讀取 frontmatter。否則，它會將整個檔案（包括 `---` 標記）視為 skill 內容。 布林欄位接受 `yes`、`no`、`on`、`off`、`1` 和 `0`（任何字母大小寫），以及 `true` 和 `false`。在 v2.1.218 之前，Claude Code 僅識別 `true` 和 `false`。

| 欄位                       | 必需 | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| -------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                     | 否   | 在 skill 清單中顯示的顯示名稱。預設為目錄名稱。請參閱[skill 如何獲得其命令名稱](https://code.claude.com/docs/zh-TW/skills#how-a-skill-gets-its-command-name)以了解該欄位如何與您鍵入以調用 skill 的名稱互動。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `description`              | 建議 | skill 的功能及何時使用。Claude 使用此項來決定何時應用該 skill。如果省略，則使用 markdown 內容的第一段。將關鍵用例放在首位：組合的 `description` 和 `when_to_use` 文字在 skill 清單中被截斷為 1,536 個字元，以減少上下文使用。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `when_to_use`              | 否   | Claude 應何時調用該 skill 的其他上下文，例如觸發短語或範例請求。附加到 skill 清單中的 `description`，並計入 1,536 字元上限。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `argument-hint`            | 否   | 在自動完成期間顯示的提示，以指示預期的引數。範例：`[issue-number]` 或 `[filename] [format]`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `arguments`                | 否   | 用於 skill 內容中[`$name` 替換](https://code.claude.com/docs/zh-TW/skills#available-string-substitutions)的具名位置引數。接受以空格分隔的字串或 YAML 清單。名稱按順序對應到引數位置。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `disable-model-invocation` | 否   | 設定為 `true` 以防止 Claude 自動載入此 skill。用於您想使用 `/name` 手動觸發的工作流程。也防止 skill 被[預載入 subagents](https://code.claude.com/docs/zh-TW/sub-agents#preload-skills-into-subagents)。從 v2.1.196 開始，也防止 skill 在[排程任務](https://code.claude.com/docs/zh-TW/scheduled-tasks)以該 skill 作為其提示時運行。預設值：`false`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `user-invocable`           | 否   | 當只有 Claude 應調用該 skill 時設定為 `false`：Claude Code 將其從 `/` 功能表中隱藏，並且當您鍵入 `/name` 時不會運行它。用於使用者不應直接調用的背景知識。預設值：`true`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `allowed-tools`            | 否   | Claude 在調用此 skill 的回合中可以使用而無需請求許可的工具。當您傳送下一條訊息時，授予將被清除。接受以空格或逗號分隔的字串或 YAML 清單。請參閱[為 skill 預先批准工具](https://code.claude.com/docs/zh-TW/skills#pre-approve-tools-for-a-skill)。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `disallowed-tools`         | 否   | 此 skill 處於活動狀態時從 Claude 可用工具池中移除的工具。用於不應呼叫某些工具的自主 skills，例如背景迴圈的 `AskUserQuestion`。接受以空格或逗號分隔的字串或 YAML 清單。當您傳送下一條訊息時，限制將被清除。與拒絕規則一樣，當任何其他工具保持時，該欄位無法移除[`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior)。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `model`                    | 否   | 此 skill 處於活動狀態時要使用的模型。覆蓋適用於目前回合的其餘部分，不會儲存到設定。當您傳送下一個提示時，工作階段模型會繼續。接受與[`/model`](https://code.claude.com/docs/zh-TW/model-config)相同的值，或 `inherit` 以保持活動模型。您組織的[`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)允許清單排除的值不會被使用，工作階段會保持其目前模型。在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)中，以及在[計畫模式中分類器檢查命令時](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode)，自動模式不支援的模型也不會被使用，工作階段會保持其目前模型。使用 `context: fork` 時，該值設定[分叉 subagent 的模型](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)，而被排除的值遵循[與 subagent 模型覆蓋相同的規則](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)。 |
| `effort`                   | 否   | 此 skill 處於活動狀態時的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。覆蓋工作階段努力等級。預設值：從工作階段繼承。選項：`low`、`medium`、`high`、`xhigh`、`max`；可用等級取決於模型。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `context`                  | 否   | 設定為 `fork` 以在分叉 subagent 上下文中運行。請參閱[在 subagent 中運行 skills](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `agent`                    | 否   | 設定 `context: fork` 時要使用的 subagent 類型。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `background`               | 否   | 僅適用於 `context: fork`。設定為 `false` 以在調用該 skill 的回合中等待分叉 subagent 的結果，而不是[在背景中運行它](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)。預設值：`true`。需要 Claude Code v2.1.218 或更新版本。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `hooks`                    | 否   | Claude Code 在調用該 skill 時註冊並在工作階段的其餘部分保持運行的 hooks。請參閱[skills 和 agents 中的 Hooks](https://code.claude.com/docs/zh-TW/hooks#hooks-in-skills-and-agents)以了解設定格式和 `once` 選項。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `paths`                    | 否   | Glob 模式，限制何時啟動此 skill。接受以逗號分隔的字串或 YAML 清單。設定後，Claude 僅在處理與模式相符的檔案時自動載入該 skill。使用與[路徑特定規則](https://code.claude.com/docs/zh-TW/memory#path-specific-rules)相同的格式。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `shell`                    | 否   | 用於此 skill 中的 `!`command\`\` 和 \`\`\`\`!`區塊的 shell。接受`bash`（預設）或 `powershell`。設定 `powershell`在啟用[PowerShell 工具](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool)時透過 PowerShell 運行內聯 shell 命令：在沒有 Git Bash 的 Windows 上預設開啟，在具有 Git Bash 的 claude.ai 和 Console 帳戶上預設開啟，在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 工作階段以及 macOS、Linux 和 WSL 上需要`CLAUDE_CODE_USE_POWERSHELL_TOOL=1`。將其設定為 `0\` 以關閉工具。                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `metadata`                 | 否   | 您自己的鍵值資料的自由格式 YAML 對應，例如權利或目錄欄位，由您自己的工具從 `SKILL.md` 讀取。Claude Code 不對其內容進行操作，並會丟棄不是對應的值。不要重複使用 frontmatter 欄位名稱（例如 `paths`）作為鍵。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `license`                  | 否   | 涵蓋該 skill 的授權。[Agent Skills](https://agentskills.io) 規格的一部分；請參閱[在 Claude Code 外使用 skill frontmatter](https://code.claude.com/docs/zh-TW/skills#using-skill-frontmatter-outside-claude-code)。Claude Code 接受該欄位但不對其進行操作。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `compatibility`            | 否   | skill 的環境要求，例如預期的產品或系統先決條件，如[Agent Skills](https://agentskills.io) 規格所定義；請參閱[在 Claude Code 外使用 skill frontmatter](https://code.claude.com/docs/zh-TW/skills#using-skill-frontmatter-outside-claude-code)。接受最多 500 個字元的字串。Claude Code 接受該欄位但不對其進行操作。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

#### 在 Claude Code 外使用 skill frontmatter

Claude Code 接受上表中的每個欄位。在 Claude Code 外，您只能使用[Agent Skills](https://agentskills.io) 規格中的欄位：

| 發佈路徑                                                                                                                                                                                                                                                                      | 您可以使用的 Frontmatter 欄位                                                  |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Claude Code skills 在[任何等級](https://code.claude.com/docs/zh-TW/skills#where-skills-live)，包括[plugin](https://code.claude.com/docs/zh-TW/plugins) skills                                                                                                                 | 上表中的每個欄位                                                               |
| claude.ai skill 上傳、Skills API 和使用 [anthropics/skills](https://github.com/anthropics/skills) 中的 `package_skill.py` 進行打包                                                                                                                                            | `name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools` |
| 當您為[Cowork 和雲端工作階段](https://code.claude.com/docs/zh-TW/skills#skills-in-cowork-and-cloud-sessions)啟用個人 skill（包括例行程序）時，您會將其上傳到 claude.ai，因此適用相同的規則。 如果您包含規格不允許的任何欄位，打包或上傳將失敗並出現硬錯誤，而不是忽略該欄位： |                                                                                |

```
Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name

```

將 frontmatter 限制為規格的六個欄位可避免上述意外鍵錯誤。[Agent Skills 規格](https://agentskills.io)和[Skills API 要求](https://docs.claude.com/en/api/skills-guide)定義這些路徑驗證的所有其他內容。Claude Code 專用的主體功能，例如[動態上下文注入](https://code.claude.com/docs/zh-TW/skills#inject-dynamic-context)，在 claude.ai 聊天或透過 API 中不起作用。Claude Code 接受所有六個欄位，因此遵循規格的 frontmatter 在 Claude Code 中無需更改即可載入。

#### skill 如何獲得其命令名稱

您鍵入以調用 skill 的命令來自 skill 檔案的位置，對於 plugin skills，也來自 frontmatter `name` 欄位。在個人或專案 skill 中，`name` 僅設定在 skill 清單中顯示的顯示標籤，命令仍來自目錄名稱。在 plugin skill 中，`name` 設定命令的最後一段，plugin 前綴保持不變。 下表顯示了每個佈局的命令名稱來自何處：

| Skill 位置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 命令名稱來源                                                                     | 範例                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `~/.claude/skills/` 或 `.claude/skills/` 下的 Skill 目錄                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 目錄名稱                                                                         | `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging`                                                                                                   |
| [嵌套](https://code.claude.com/docs/zh-TW/skills#where-skills-live)`.claude/skills/` 目錄，當名稱與另一個 skill 衝突時                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 相對於工作目錄的子目錄路徑，然後是 skill 目錄名稱                                | `apps/web/.claude/skills/deploy/SKILL.md` → `/apps/web:deploy`                                                                                                 |
| `.claude/commands/` 下的檔案                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 檔案名稱（不含副檔名）                                                           | `.claude/commands/deploy.md` → `/deploy`                                                                                                                       |
| `.claude/commands/` 的子目錄中的檔案                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 相對於 `commands/` 的子目錄路徑，每個 `/` 替換為 `:`，然後是不含副檔名的檔案名稱 | `.claude/commands/frontend/component.md` → `/frontend:component`                                                                                               |
| Plugin `skills/` 子目錄                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Frontmatter `name` 或目錄名稱，由 plugin 命名空間                                | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review`，或使用 `name: fancy` 時為 `/my-plugin:fancy`                                                         |
| Plugin 根 `SKILL.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Frontmatter `name`，以 plugin 目錄名稱作為後備                                   | `my-plugin/SKILL.md` 搭配 `name: review` → `/my-plugin:review`。請參閱[路徑行為規則](https://code.claude.com/docs/zh-TW/plugins-reference#path-behavior-rules) |
| Skill [從 claude.ai 同步](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 您 claude.ai 帳戶上的 skill 名稱，前綴為 `anthropic-skills:`                     | 帳戶 skill `deploy` → `/anthropic-skills:deploy`，或在沒有其他命令使用該名稱時為 `/deploy`                                                                     |
| 在 plugin skill 中，frontmatter `name` 替換命令最後一段中的目錄名稱，因此 `my-plugin/skills/review/SKILL.md` 搭配 `name: fancy` 變成 `/my-plugin:fancy`。除非另一個命令已使用該名稱，否則裸 `/fancy` 也會調用該 skill。如果您寫的 `name` 已經以 plugin 自己的前綴開頭，Claude Code 在 v2.1.246 或更新版本上不會再次新增前綴。例如，`name: my-plugin:fancy` 仍然變成 `/my-plugin:fancy`。從 v2.1.216 到 v2.1.245，當 `name` 已經帶有前綴時，Claude Code 會加倍前綴。 在[非互動式工作階段](https://code.claude.com/docs/zh-TW/headless)中，名稱 `help` 和 `feedback` 不是為其僅限終端的內建命令保留的，因此具有其中一個名稱的 plugin skill 在那裡保持其裸命令。每個其他僅限終端的內建命令的名稱（例如 `/login`）即使該命令無法在這些工作階段中運行，仍然保留。 對於 plugin 根 `SKILL.md`，沒有 skill 目錄可以從中獲取名稱，因此 `name` 提供整個最後一段。沒有 `name` 欄位，Claude Code 會回退到 plugin 的目錄名稱。 |                                                                                  |                                                                                                                                                                |

#### 可用的字串替換

Skills 支援 skill 內容中動態值的字串替換：

| 變數                                                                                                                                                                                                                                                                                                                                                                                                                      | 說明                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$ARGUMENTS`                                                                                                                                                                                                                                                                                                                                                                                                              | 調用 skill 時傳遞的所有引數。當沒有佔位符接收引數時，Claude Code 將它們附加為 `ARGUMENTS: <value>`。請參閱[將引數傳遞給 skills](https://code.claude.com/docs/zh-TW/skills#pass-arguments-to-skills)。                                                                     |
| `$ARGUMENTS[N]`                                                                                                                                                                                                                                                                                                                                                                                                           | 按 0 為基礎的索引存取特定引數，例如 `$ARGUMENTS[0]` 表示第一個引數。                                                                                                                                                                                                      |
| `$N`                                                                                                                                                                                                                                                                                                                                                                                                                      | `$ARGUMENTS[N]` 的簡寫，例如 `$0` 表示第一個引數或 `$1` 表示第二個引數。                                                                                                                                                                                                  |
| `$name`                                                                                                                                                                                                                                                                                                                                                                                                                   | 在[`arguments`](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference) frontmatter 清單中宣告的具名引數。名稱按順序對應到位置，因此使用 `arguments: [issue, branch]` 時，佔位符 `$issue` 擴展為第一個引數，`$branch` 擴展為第二個引數。                         |
| `${CLAUDE_SESSION_ID}`                                                                                                                                                                                                                                                                                                                                                                                                    | 目前工作階段 ID。用於記錄、建立工作階段特定檔案或將 skill 輸出與工作階段相關聯。                                                                                                                                                                                          |
| `${CLAUDE_EFFORT}`                                                                                                                                                                                                                                                                                                                                                                                                        | 目前努力等級：`low`、`medium`、`high`、`xhigh` 或 `max`。Ultracode 不是一個不同的等級，報告為 `xhigh`。使用此項根據活動努力設定調整 skill 指示。                                                                                                                          |
| `${CLAUDE_SKILL_DIR}`                                                                                                                                                                                                                                                                                                                                                                                                     | 包含 skill 的 `SKILL.md` 檔案的目錄。對於 plugin skills，這是 plugin 內 skill 的子目錄，而不是 plugin 根。在 bash 注入命令中使用此項以參考與 skill 捆綁的指令碼或檔案，無論目前工作目錄如何。                                                                             |
| `${CLAUDE_PROJECT_DIR}`                                                                                                                                                                                                                                                                                                                                                                                                   | 專案根目錄。這是與 [hooks](https://code.claude.com/docs/zh-TW/hooks#reference-scripts-by-path) 和 MCP 伺服器相同的路徑，作為 `CLAUDE_PROJECT_DIR` 接收。使用此項參考專案本地指令碼或檔案，例如 `${CLAUDE_PROJECT_DIR}/.claude/hooks/helper.sh`，獨立於 skill 的安裝位置。 |
| `${CLAUDE_PLUGIN_ROOT}`                                                                                                                                                                                                                                                                                                                                                                                                   | Plugin 的安裝目錄。僅在 plugin skills 中替換。使用此項參考 plugin 中任何位置的捆綁指令碼或檔案，包括在 plugin 的 skills 之間共用的資源。請參閱[plugin 環境變數](https://code.claude.com/docs/zh-TW/plugins-reference#environment-variables)。                             |
| `${CLAUDE_PLUGIN_DATA}`                                                                                                                                                                                                                                                                                                                                                                                                   | Plugin 的[持久資料目錄](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)，在 plugin 更新後仍然存在。僅在 plugin skills 中替換。使用此項參考已安裝的相依性、生成的檔案或必須超越更新的快取。                                                |
| Claude Code 在兩個位置替換 `${CLAUDE_SKILL_DIR}` 和 `${CLAUDE_PROJECT_DIR}`：skill 的 markdown 內容和[`allowed-tools`](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference) frontmatter 中的 Bash 規則。在 plugin skill 中，Claude Code 在相同的兩個位置替換 `${CLAUDE_PLUGIN_ROOT}` 和 `${CLAUDE_PLUGIN_DATA}`。在兩個位置使用相同的變數可讓 skill 運行捆綁的指令碼而無需許可提示。以下 skill 顯示了該模式： |                                                                                                                                                                                                                                                                           |

```
---
name: render-chart
description: Render a chart from a CSV file
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---

Run `${CLAUDE_SKILL_DIR}/scripts/render.sh <csv-file>` to render the chart.

```

如果此 skill 安裝在 `~/.claude/skills/render-chart/`，`${CLAUDE_SKILL_DIR}` 的兩個出現都會擴展為該目錄。`allowed-tools` 規則然後與 skill 主體告訴 Claude 運行的確切命令相符，因此指令碼運行而無需提示。 `${CLAUDE_PROJECT_DIR}` 替換需要 Claude Code v2.1.196 或更新版本。 索引引數使用 shell 風格的引用，因此將多字值包裝在引號中以將其作為單個引數傳遞。例如，`/my-skill "hello world" second` 使 `$0` 擴展為 `hello world`，`$1` 擴展為 `second`。`$ARGUMENTS` 佔位符始終擴展為鍵入的完整引數字串。 沒有對應引數的索引佔位符（例如僅傳遞一個引數時的 `$2`）在內容中保持不變。來自[`arguments`](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference) frontmatter 的具名佔位符，沒有匹配的引數，擴展為空字串。 如果您傳遞的引數值本身包含文字（例如 `$1` 或 `$ARGUMENTS`），Claude Code 會將其插入為文字，不會擴展它。例如，如果 skill 的主體包含 `Summarize $0`，您運行 `/summarize "$ARGUMENTS from yesterday"`，Claude 會收到 `Summarize $ARGUMENTS from yesterday`。Claude Code 仍然在插入引數後替換 `${CLAUDE_*}` 變數（例如 `${CLAUDE_SKILL_DIR}`）。 要在數字、`ARGUMENTS` 或宣告的引數名稱之前包含文字 `$`（例如散文中的 `$1.00`），請使用反斜線進行轉義：`\$1.00`。任何其他 `$` 之前的反斜線保持不變。只有直接在令牌之前的單個反斜線才能轉義它。雙反斜線（例如 `\\$1`）將兩個反斜線保留在原位，`$1` 仍然擴展為引數值。反斜線轉義僅涵蓋這些引數佔位符。反斜線不會防止 `${CLAUDE_*}` 變數的替換，其中變數適用。 **使用替換的範例：**

```
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS

```

### 新增支援檔案

Skills 可以在其目錄中包含多個檔案。這使 `SKILL.md` 專注於基本要素，同時讓 Claude 僅在需要時存取詳細參考資料。大型參考文件、API 規格或範例集合不需要在每次 skill 運行時載入上下文。

```
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)

```

從 `SKILL.md` 參考支援檔案，以便 Claude 知道每個檔案包含什麼以及何時載入它：

```
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)

```

將 `SKILL.md` 保持在 500 行以下。將詳細參考資料移至單獨的檔案。

### 控制誰調用 skill

預設情況下，您和 Claude 都可以調用任何 skill。您可以鍵入 `/skill-name` 直接調用它，Claude 可以在與您的對話相關時自動載入它。兩個 frontmatter 欄位可讓您限制此項：

- **`disable-model-invocation: true`**：只有您可以調用該 skill。用於具有副作用或您想控制時機的工作流程，例如`/commit` 、`/deploy` 或 `/send-slack-message`。您不希望 Claude 因為您的程式碼看起來準備好就決定部署。
- **`user-invocable: false`**：只有 Claude 可以調用該 skill。用於不可作為命令操作的背景知識。`legacy-system-context` skill 解釋舊系統的工作方式。Claude 應在相關時知道這一點，但 `/legacy-system-context` 對使用者來說不是一個有意義的操作。

此範例建立一個只有您可以觸發的部署 skill。如果您設定 `disable-model-invocation: true`，Claude 無法自動運行該 skill：

```
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded

```

如果 Claude 仍然嘗試，Claude Code 會阻止呼叫並指示它不要以另一種方式重現部署步驟，因此預期 Claude 會建議您自己運行 `/deploy`。 以下是兩個欄位如何影響調用和上下文載入的方式：

| Frontmatter                                                                                                                                                                                                                                                           | 您可以調用 | Claude 可以調用 | 何時載入到上下文中                       |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------- | ---------------------------------------- |
| （預設）                                                                                                                                                                                                                                                              | 是         | 是              | 描述始終在上下文中，調用時載入完整 skill |
| `disable-model-invocation: true`                                                                                                                                                                                                                                      | 是         | 否              | 描述不在上下文中，您調用時載入完整 skill |
| `user-invocable: false`                                                                                                                                                                                                                                               | 否         | 是              | 描述始終在上下文中，調用時載入完整 skill |
| 在常規工作階段中，skill 描述被載入到上下文中，以便 Claude 知道什麼可用，但完整 skill 內容僅在調用時載入。[具有預載入 skills 的 Subagents](https://code.claude.com/docs/zh-TW/sub-agents#preload-skills-into-subagents)的工作方式不同：完整 skill 內容在啟動時被注入。 |            |                 |                                          |

### Skill 內容生命週期

當您或 Claude 調用 skill 時，呈現的 `SKILL.md` 內容作為單個訊息進入對話，並在後續回合中保持在那裡。此持久性適用於 skill 的指示，而不是其許可：[`allowed-tools`](https://code.claude.com/docs/zh-TW/skills#pre-approve-tools-for-a-skill) 授予在您傳送下一條訊息時被清除。Claude Code 不會在後續回合中重新讀取 skill 檔案，因此將應該在整個任務中應用的指導寫為常設指示，而不是一次性步驟。 當 Claude 重新調用其呈現內容與上下文中已有的副本相同的 skill 時，Claude Code 新增一個簡短說明該 skill 已載入的註記，而不是內容的第二份副本。當呈現內容不同時（因為引數改變或[動態上下文](https://code.claude.com/docs/zh-TW/skills#inject-dynamic-context)命令產生新輸出），Claude Code 會再次附加完整內容。 [自動壓縮](https://code.claude.com/docs/zh-TW/how-claude-code-works#when-context-fills-up)在 token 預算內進行調用的 skills。當對話被摘要以釋放上下文時，Claude Code 在摘要後重新附加每個 skill 的最新調用，保留每個的前 5,000 個 token。重新附加的 skills 共用 25,000 個 token 的組合預算。Claude Code 從最近調用的 skill 開始填充此預算，因此如果您在一個工作階段中調用了許多，較舊的 skills 可能在壓縮後完全被丟棄。 如果 skill 似乎在第一個回應後停止影響行為，內容通常仍然存在，模型正在選擇其他工具或方法。加強 skill 的 `description` 和指示，以便模型繼續偏好它，或使用[hooks](https://code.claude.com/docs/zh-TW/hooks)以確定性地強制行為。如果 skill 很大或您在它之後調用了其他幾個，在壓縮後重新調用它以恢復完整內容。

### 為 skill 預先批准工具

`allowed-tools` 欄位在調用 skill 的回合中授予列出的工具的許可，因此 Claude 可以使用它們而無需提示您批准。當您傳送下一條訊息時，授予被清除，即使 skill 內容[保持在上下文中](https://code.claude.com/docs/zh-TW/skills#skill-content-lifecycle)；再次調用 skill 會為該回合重新應用它。它不限制哪些工具可用：每個工具仍然可呼叫，您的[許可設定](https://code.claude.com/docs/zh-TW/permissions)仍然管理未列出的工具。要為整個工作階段而不是單個回合預先批准工具，請改為將允許規則新增到這些許可設定。 工作區信任不會限制此欄位。Claude Code 在您或 Claude 調用該 skill 時應用專案 skill 的 `allowed-tools`，包括在您從未信任的資料夾中的 `-p` 運行中。skill 可以授予自己廣泛的工具存取權限，因此在您在存放庫中運行 Claude Code 之前，請檢查 skills 的 `allowed-tools`。 此 skill 讓 Claude 在您調用它時無需每次使用批准即可運行 git 命令：

```
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---

```

要在 skill 處於活動狀態時從 Claude 的可用工具池中移除工具，請在 skill 的 frontmatter 中的 `disallowed-tools` 中列出它們。當您傳送下一條訊息時，限制被清除。與拒絕規則一樣，該欄位無法在任何其他工具保持時移除[`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior)。要在所有 skills 和提示中阻止工具，請在您的[許可設定](https://code.claude.com/docs/zh-TW/permissions)中新增拒絕規則。

### 將引數傳遞給 skills

您和 Claude 都可以在調用 skill 時傳遞引數。引數可透過 `$ARGUMENTS` 佔位符取得。 此 skill 按編號修復 GitHub 問題。`$ARGUMENTS` 佔位符被替換為 skill 名稱後面的任何內容：

```
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit

```

當您運行 `/fix-issue 123` 時，Claude 會收到「Fix GitHub issue 123 following our coding standards…」 如果您使用引數調用 skill，但 skill 內容中沒有佔位符接收一個，Claude Code 會將 `ARGUMENTS: <your input>` 附加到 skill 內容的末尾，以便 Claude 仍然看到您鍵入的內容。佔位符是 `$ARGUMENTS`、索引形式（例如 `$1`）或具名引數。沒有其位置引數的索引佔位符保持為文字，不計為接收一個。具名佔位符計數，即使其位置沒有引數，因為它擴展為空字串。 您也可以在一條訊息的開始時堆疊多個 skills。鍵入 `/write-tests /fix-issue 123` 會載入兩個 skills，並將尾隨文字 `123` 作為 `$ARGUMENTS` 傳遞給每個。在 v2.1.199 之前，只有第一個 skill 載入並接收 `/fix-issue 123` 作為文字引數文字。 Claude Code 擴展第一個 skill 加上最多五個堆疊在其後的。擴展在第一個不是內聯使用者可調用 skill 的令牌處停止，因此運行為[分叉 subagent](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent) 的 skill（例如[`/code-review`](https://code.claude.com/docs/zh-TW/code-review#review-a-diff-locally)）或其引數本身可能以斜線命令開頭的 skill（例如 `/loop`）也在那裡結束運行。該令牌及其後的所有內容都成為每個擴展 skill 的引數文字。從 v2.1.218 開始，`/code-review` 作為分叉 subagent 運行；在較早的版本上，它以內聯方式運行並堆疊。 要按位置存取個別引數，請使用 `$ARGUMENTS[N]` 或較短的 `$N`：

```
---
name: migrate-component
description: Migrate a component from one language to another
---

Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].
Preserve all existing behavior and tests.

```

運行 `/migrate-component SearchBar JavaScript TypeScript` 會將 `$ARGUMENTS[0]` 替換為 `SearchBar`，`$ARGUMENTS[1]` 替換為 `JavaScript`，`$ARGUMENTS[2]` 替換為 `TypeScript`。使用 `$N` 簡寫的相同 skill：

```
---
name: migrate-component
description: Migrate a component from one language to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.

```

## 進階模式

### 注入動態內容

`!`<command>``  語法在技能內容傳送給 Claude 之前執行 shell 命令。命令輸出會取代佔位符，所以 Claude 會收到實際資料，而不是命令本身。當技能從您的 claude.ai 帳戶[同步](https://code.claude.com/docs/zh-TW/skills#how-claude-code-handles-the-body-of-a-synced-skill)時，Claude Code 不會在您的機器上執行這些命令。此限制需要 Claude Code v2.1.228 或更新版本。 此技能透過使用 GitHub CLI 擷取即時 PR 資料來總結拉取請求。`!`gh pr diff `` 和其他命令會先執行，其輸出會插入到提示中：

```
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...

```

替換在原始檔案上執行一次。命令輸出會以純文字形式插入，不會重新掃描以尋找進一步的 `!`<command>``  佔位符，所以命令無法發出佔位符供稍後的傳遞展開。 內聯形式只有在 `!` 出現在行首或緊接在空白字元之後時才會被識別。如果 `!` 跟在另一個字元之後，如 `KEY=!`cmd ``，佔位符會保留為字面文字，命令不會執行。 對於多行命令，請使用以 \`\`\`\`!\` 開啟的圍欄程式碼區塊，而不是內聯形式：

````
## Environment
```!
node --version
git status --short
````

```

若要為來自使用者、專案、外掛程式或[其他目錄](https://code.claude.com/docs/zh-TW/skills#skills-from-additional-directories)來源的技能和自訂命令停用此行為，請在[設定](https://code.claude.com/docs/zh-TW/settings)中設定 `"disableSkillShellExecution": true`。每個命令都會被替換為 `[shell command execution disabled by policy]` 而不是被執行。捆綁和受管理的技能不受影響。此設定在[受管理設定](https://code.claude.com/docs/zh-TW/managed-settings)中最有用，使用者無法覆寫它。 當命令出現在從您的 claude.ai 帳戶[同步的技能](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave)中時，Claude Code 永遠不會在您的機器上執行這些命令，無論此設定如何。此限制需要 Claude Code v2.1.228 或更新版本。[Claude Code 如何處理同步技能的主體](https://code.claude.com/docs/zh-TW/skills#how-claude-code-handles-the-body-of-a-synced-skill)說明了在每種工作階段中 Claude 會收到什麼來取代命令。
若要在技能執行時要求更深入的推理，請在技能內容中的任何地方包含 `ultrathink`。請參閱[使用 ultrathink 進行一次性深入推理](https://code.claude.com/docs/zh-TW/model-config#use-ultrathink-for-one-off-deep-reasoning)。
####  注入命令如何執行
Claude Code 從技能的 frontmatter 中的 `shell` 鍵和您的環境中選擇執行技能注入命令的工具。除了一個會直接導致呼叫失敗的組合外，每個組合都會透過 Bash 工具或 PowerShell 工具執行命令：
  * `shell: powershell`，且[PowerShell 工具](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool)已啟用：命令透過 PowerShell 工具執行。
  * `shell: bash` 當 bash 不可用時：呼叫在任何命令執行之前失敗。這發生在沒有 Git Bash 的 Windows 上。Claude Code 會顯示 `Skill <name> requires bash (`shell: bash` in frontmatter) but Git Bash was not found`。
  * 任何其他組合：當 bash 可用時，命令透過 Bash 工具執行。當它不可用時，它們透過 PowerShell 工具執行。

任一工具執行命令的方式與執行 Claude 自己的 shell 命令的方式相同。它們共享工作目錄、逾時和輸出處理：
  * **工作目錄** ：Claude Code 在工作階段 shell 的目前工作目錄中執行每個命令。當 Claude 執行 `cd` 時，該目錄會移動。在必須每次都以相同方式解析的路徑中使用 [`${CLAUDE_SKILL_DIR}` 或 `${CLAUDE_PROJECT_DIR}`](https://code.claude.com/docs/zh-TW/skills#available-string-substitutions)。
  * **stderr** ：使用預設 `bash` shell，Claude Code 會將 stderr 合併到 stdout。命令寫入 stderr 的任何內容都會出現在注入的文字中。
  * **逾時** ：每個命令在 Bash 工具的預設 2 分鐘[逾時](https://code.claude.com/docs/zh-TW/tools-reference#timeout-and-output-limits)下執行。當 Bash 工具[將逾時命令移到背景](https://code.claude.com/docs/zh-TW/tools-reference#background-commands)時，技能仍會呈現。注入的文字會報告移動並命名背景工作和收集命令輸出的檔案。當命令是 Bash 工具永遠不會自動背景執行的命令時，Claude Code 會在逾時時終止它。該失敗會[中止呼叫](https://code.claude.com/docs/zh-TW/skills#when-an-injected-command-fails)。
  * **輸出大小** ：超過 Bash 工具內聯上限的輸出會作為檔案路徑加上簡短預覽到達，而不是截斷的文字。[輸出限制](https://code.claude.com/docs/zh-TW/tools-reference#output-limits)涵蓋上限以及如何調整每個邊界。

PowerShell 工具對其執行的命令應用相同的逾時、背景執行和輸出上限行為。請參閱 [PowerShell 工具](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool)部分以了解其具體內容。
####  當注入命令失敗時
失敗的命令會中止整個技能呼叫，而不僅僅是其自己的佔位符。Claude 永遠不會看到該呼叫的技能內容。中止會顯示 `Shell command failed for pattern "..."`。錯誤訊息包括命令在 `[stderr]` 下的輸出。 使用預設 `bash` shell，任何非零結束代碼都算作失敗。有一個例外適用：Claude Code 將來自[搜尋和比較命令](https://code.claude.com/docs/zh-TW/tools-reference#output-limits)的結束代碼 1 視為正常結果並注入其輸出。結束代碼 2 或更高的代碼即使對於這些命令也會失敗。 哪些命令獲得例外取決於 shell：
  * 預設 `bash` shell：[輸出限制](https://code.claude.com/docs/zh-TW/tools-reference#output-limits)下列出的命令
  * `shell: powershell`，當 PowerShell 工具啟用時：一個[不同的集合](https://code.claude.com/docs/zh-TW/tools-reference#shell-selection-in-settings-hooks-and-skills)，包括 `grep` 和 `git diff` 但不包括 `find` 或 `diff`

使用預設 `bash` shell，將 `|| true` 附加到任何您預期會以非零結束的其他命令。一個在發現問題時結束代碼為 1 的檢查指令碼就是一個例子。
####  注入命令的權限檢查
注入命令在技能呈現時永遠不會提示權限。Claude Code 首先根據您的[權限規則](https://code.claude.com/docs/zh-TW/permissions)檢查每一個。拒絕規則匹配的命令會中止呼叫，顯示 `Shell command permission check failed for pattern "..."`。 在[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)之外，當命令的權限檢查返回除允許以外的任何內容時，Claude Code 會中止呼叫。這包括通常會詢問您的規則。若要防止不匹配的命令在此處中止，請使用 [`allowed-tools`](https://code.claude.com/docs/zh-TW/skills#pre-approve-tools-for-a-skill) 預先批准它。拒絕和詢問規則仍會覆寫 `allowed-tools`。請參閱[管理權限](https://code.claude.com/docs/zh-TW/permissions#manage-permissions)。 在自動模式中，原本需要您批准的命令不會中止呼叫。技能會載入一個指示，告訴 Claude 先執行命令，然後 Claude 自己的呼叫會通過[自動模式的常規檢查](https://code.claude.com/docs/zh-TW/permission-modes#how-the-classifier-evaluates-actions)。在設定 `agent` 的[分叉技能](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)中，以及在 Claude 沒有[執行注入命令的 shell 工具](https://code.claude.com/docs/zh-TW/skills#how-injected-commands-run)的工作階段中，呼叫仍會中止。
###  在子代理中執行技能
當您希望技能在隔離環境中執行時，請在 frontmatter 中新增 `context: fork`。Claude Code 會啟動在 `agent` 欄位中設定的類型的新子代理，並將技能內容作為其提示提供。子代理看不到您的對話歷史記錄，所以技能的指示必須獨立存在。
儘管名稱如此，具有 `context: fork` 的技能不會在[目前對話的分叉](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)中執行，這會將您迄今為止討論的所有內容交給子代理。當工作取決於該歷史記錄時，請分叉對話而不是使用 `context: fork`。
分叉的子代理在[背景](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)中執行：您可以在它執行時繼續工作，其結果在完成時到達您的對話。在 frontmatter 中設定 `background: false` 以改為在呼叫技能的回合中等待結果。在 v2.1.218 之前，分叉技能總是阻止回合直到它們完成。 Claude Code 也會等待結果，即使技能沒有設定 `background: false`，在以下情況下：
  * 在非互動模式中，使用 `-p` 旗標或 Agent SDK
  * 當您將 [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 時，這也會關閉所有其他背景工作功能
  * 當您在同一技能的較早呼叫仍在執行時呼叫分叉技能時
  * 當[排程工作](https://code.claude.com/docs/zh-TW/scheduled-tasks)以技能作為其提示時觸發

背景分叉也會使用[適用於背景子代理的較窄工具集](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)執行：技能的子代理是常規代理類型，所以分叉對話的子代理豁免不涵蓋它。如果您的技能步驟取決於該集合外的工具，請設定 `background: false` 以保持完整工具集。 在背景中執行的分叉技能會在您工作階段的[檢查點](https://code.claude.com/docs/zh-TW/checkpointing)之外應用其編輯，所以 `/rewind` 不會撤銷它們；使用 git 來還原它們。
`context: fork` 只對具有明確指示的技能有意義。如果您的技能包含「使用這些 API 慣例」之類的指南而沒有工作，子代理會收到指南但沒有可操作的提示，並返回而沒有有意義的輸出。
技能和[子代理](https://code.claude.com/docs/zh-TW/sub-agents)在兩個方向上協同工作：
| 方法  | 系統提示  | 工作  | 也會載入  |
| --- | --- | --- | --- |
| 具有 `context: fork` 的技能  | 來自代理類型  | SKILL.md 內容  | CLAUDE.md，根據代理的[啟動內容](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup)  |
| 具有 `skills` 欄位的子代理  | 子代理的 markdown 主體  | Claude 的委派訊息  | 預載入的技能 + CLAUDE.md，根據子代理的[啟動內容](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup)  |
使用 `context: fork`，您在技能中編寫工作並選擇代理類型來執行它。內建的 Explore 和 Plan 代理[跳過 CLAUDE.md 和 git 狀態](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup)以保持其內容較小，所以使用 `agent: Explore` 的分叉技能只會看到 SKILL.md 內容和代理自己的系統提示。對於相反的情況，您定義使用技能作為參考資料的自訂子代理，請參閱[子代理](https://code.claude.com/docs/zh-TW/sub-agents#preload-skills-into-subagents)。
####  範例：使用 Explore 代理的研究技能
此技能在分叉的 Explore 代理中執行研究。技能內容會成為工作，代理提供針對程式碼庫探索最佳化的唯讀工具：

```

______________________________________________________________________

## name: deep-research description: Research a topic thoroughly context: fork agent: Explore

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
1. Read and analyze the code
1. Summarize findings with specific file references

```

當此技能執行時：
  1. 建立新的隔離內容
  2. 子代理接收技能內容作為其提示（「Research $ARGUMENTS thoroughly…」）
  3. `agent` 欄位決定執行環境（模型、工具和權限）
  4. 子代理總結其結果並在完成時將其返回到您的主要對話

`agent` 欄位指定要使用的子代理配置。選項包括內建代理（`Explore`、`Plan`、`general-purpose`）或來自 `.claude/agents/` 的任何自訂子代理。如果省略，使用 `general-purpose`。
###  限制 Claude 的技能存取
預設情況下，Claude 可以呼叫任何沒有設定 `disable-model-invocation: true` 的技能。定義 `allowed-tools` 的技能會授予 Claude 在呼叫技能的回合期間存取這些工具而無需逐次批准的權限；當您傳送下一條訊息時，授予會清除。您的[權限設定](https://code.claude.com/docs/zh-TW/permissions)仍然控制所有其他工具的基線批准行為。一些內建命令也可透過 Skill 工具使用，包括 `/init` 和 `/security-review`。其他內建命令如 `/compact` 則不可用。 控制 Claude 可以呼叫哪些技能的三種方式： **透過在`/permissions` 中拒絕 Skill 工具來停用所有技能**：

```

# Add to deny rules:

Skill

```

**使用[權限規則](https://code.claude.com/docs/zh-TW/permissions)允許或拒絕特定技能**：

```

# Allow only specific skills

Skill(commit) Skill(review-pr \*)

# Deny specific skills

Skill(deploy \*)

```

權限語法：`Skill(name)` 用於精確匹配，`Skill(name *)` 用於帶有任何引數的前綴匹配。 如果您的 `deny` 規則命名別名或不合格的名稱而不是技能自己的名稱，Claude Code 仍會阻止技能：使用 `Skill(review)` 它會透過其 `/review` 別名阻止捆綁的 `/code-review`，使用 `Skill(deploy)` 它會阻止[巢狀技能](https://code.claude.com/docs/zh-TW/skills#where-skills-live)列為 `apps/web:deploy` 透過其不合格的名稱。在 v2.1.260 之前，當拒絕規則僅命名不合格的名稱時，Claude Code 不會阻止列在其合格名稱下的巢狀技能。 Claude Code 只針對技能自己的名稱和 Claude 呼叫中的名稱匹配 `allow` 規則。 **透過在其 frontmatter 中新增`disable-model-invocation: true` 來隱藏個別技能**。這會從 Claude 的內容中完全移除技能。
使用 `user-invocable: false`，您無法呼叫技能，但 Claude 仍然可以。若要防止 Claude 透過 Skill 工具呼叫它，請設定 `disable-model-invocation: true`。
###  從設定覆寫技能可見性
`skillOverrides` 設定從您的[設定](https://code.claude.com/docs/zh-TW/settings)而不是技能自己的 frontmatter 控制技能可見性。將其用於您不想編輯 SKILL.md 的技能，例如簽入共享專案儲存庫的技能。`/skills` 選單會為您編寫它：突出顯示技能並按 `Space` 循環狀態，然後按 `Esc` 儲存到 `.claude/settings.local.json`。 每個鍵是技能名稱，每個值是四種狀態之一：
| 值  | 列給 Claude  | 在 `/` 選單中  |
| --- | --- | --- |
| `"on"`  | 名稱和描述  | 是  |
| `"name-only"`  | 僅名稱  | 是  |
| `"user-invocable-only"`  | 隱藏  | 是  |
| `"off"`  | 隱藏  | 隱藏  |
`/skills` 選單將 `"user-invocable-only"` 狀態標記為 `user-only`。 從 v2.1.199 開始，`"off"` 也會從廣告給[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)用戶端和 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/skills#discover-available-commands) 呼叫者的命令列表中隱藏技能，除了終端 `/` 選單外。按其完整名稱呼叫隱藏技能仍會返回 `skillOverrides` 錯誤而不是執行它。 不在 `skillOverrides` 中的技能被視為 `"on"`。下面的範例將一個技能摺疊為其名稱，並完全關閉另一個：

```

{ "skillOverrides": { "legacy-context": "name-only", "deploy": "off" } }

```

某些捆綁技能有別名，例如 `/doctor` 的 `checkup`。如果您在[受管理設定](https://code.claude.com/docs/zh-TW/managed-settings)中或在您使用 `--settings` 旗標傳遞的檔案中的別名下設定 `skillOverrides` 項目，Claude Code 會將其應用於別名後面的技能。您只能透過別名進一步限制技能，永遠無法使其更可見，如果您也在受管理設定中的技能自己的名稱下設定項目，該項目優先。在 v2.1.260 之前，Claude Code 不會在任何設定來源中的別名下將項目應用於技能。 在使用者、專案和本機設定中，Claude Code 只針對技能名稱匹配項目。如果您在那裡為 `review` 設定項目，它適用於名為 `review` 的技能，而不是透過其 `/review` 別名的捆綁 `/code-review`。 外掛程式技能不受 `skillOverrides` 影響。透過 `/plugin` 管理這些。
###  尋找未使用的技能
[技能列表](https://code.claude.com/docs/zh-TW/skills#skill-descriptions-are-cut-short)中的每個技能都會在每個回合上增加到您的內容，無論 Claude 是否曾使用過它。執行 `/skill-doctor` 以查看每個技能的成本以及使用頻率，以便您可以決定關閉哪些。在互動工作階段中，報告會在 `/plugin` 管理器的 **Stats** 標籤中開啟。在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p`，Claude Code 會將其列印為文字。 報告涵蓋您工作階段中的技能，除了捆綁技能和企業技能。它標記列表中從未被呼叫的技能，並說明在哪裡關閉它們。在它告訴您在哪裡關閉的技能中，從具有最高內容成本的技能開始。報告還列出您最近未使用的外掛程式。 `/skill-doctor` 需要 Claude Code v2.1.252 或更新版本，在跳過[功能旗標擷取](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching)的工作階段中不可用。如果您從手機或瀏覽器透過[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)執行 `/skill-doctor`，Claude Code 會回覆[`Skill usage reports are not available on this connection.`](https://code.claude.com/docs/zh-TW/errors#skill-usage-reports-are-not-available-on-this-connection)。在執行工作階段的機器上的終端中執行 `/skill-doctor`。
##  評估並迭代技能
看到技能觸發告訴你 Claude 找到了它，但不代表它做了你想要的事。要知道技能是否正常運作，需要分別測量兩件事：Claude 是否在應該使用的提示上調用它，以及當它確實調用時輸出是否符合你的預期。 兩者的檢查都是基線比較。收集幾個真實的提示，在有技能可用的新會話中運行每一個，然後在[禁用](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings)它的情況下再運行一次，並比較結果。新會話很重要，因為編寫技能時留下的上下文會掩蓋書面指示中的漏洞。 兩個工具可以自動化該比較。對於在[外掛](https://code.claude.com/docs/zh-TW/plugins)中發布的技能，[`claude plugin eval`](https://code.claude.com/docs/zh-TW/plugin-evals)在隔離的會話中運行每個提示，有和沒有外掛，使用你定義的或它為你編寫的評分器進行評分，並在低於閾值時以非零值退出，以便你可以在 CI 上進行控制。對於在 Claude Code 對話中迭代單個技能，下面的 skill-creator 外掛運行類似的迴圈，使用其自己的 `evals/evals.json` 格式。這兩種格式不可互換。
###  使用 skill-creator 運行評估
[`skill-creator` 外掛](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)在 Claude Code 內自動化比較迴圈。從官方市場安裝它：

```

/plugin install skill-creator@claude-plugins-official

```

如果安裝失敗，請匹配 Claude Code 報告的訊息：
  * `Marketplace "claude-plugins-official" not found`：使用 `/plugin marketplace add anthropics/claude-plugins-official` 新增市場，然後重試安裝。
  * 外掛[在市場中找不到](https://code.claude.com/docs/zh-TW/discover-plugins#install-plugins)：檢查外掛名稱。

如果安裝摘要報告 `Run /reload-plugins to activate.`，Claude Code 會為你運行該重新載入。如果重新載入警告你的下一則訊息會重新讀取對話，請運行 `/reload-plugins --force` 以在目前會話中啟用外掛的技能。然後要求 Claude 評估現有技能，例如 `evaluate my summarize-changes skill with skill-creator`。外掛會引導你完成編寫測試案例並運行迴圈：
  * **測試案例** ：在技能目錄內的 `evals/evals.json` 中儲存提示、輸入檔案和預期行為
  * **隔離運行** ：為每個測試案例生成一個[子代理](https://code.claude.com/docs/zh-TW/sub-agents)，以便每次運行都以乾淨的上下文開始，並記錄權杖計數和持續時間
  * **評分** ：針對輸出檢查每個斷言，並將通過或失敗與證據寫入 `grading.json`
  * **基準** ：將有技能與無技能的通過率、時間和權杖彙總到 `benchmark.json` 中，以便你可以比較通過率改進與權杖和時間開銷
  * **版本比較** ：在技能的兩個版本之間運行盲目 A/B 測試，以便你可以在提交編輯之前確認它是一項改進
  * **描述調整** ：生成應該觸發和不應該觸發的提示，測量命中率，並在技能在錯誤的請求上啟動時提議描述編輯
  * **檢視查看器** ：開啟 HTML 報告，你可以在其中檢查每個輸出並記錄下一次迭代讀取的定性反饋

有關評估檔案格式和完整迭代工作流程，請參閱 agentskills.io 上的[評估技能輸出品質](https://agentskills.io/skill-creation/evaluating-skills)。有關基準和比較模式的背景，請參閱 [skill-creator 公告](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)。
##  分享技能
技能可以根據您的受眾在不同的範圍內分發：
  * **專案技能** ：將 `.claude/skills/` 提交到版本控制
  * **外掛程式** ：在您的[外掛程式](https://code.claude.com/docs/zh-TW/plugins)中建立 `skills/` 目錄
  * **受管理** ：透過[受管理設定](https://code.claude.com/docs/zh-TW/managed-settings)在整個組織範圍內部署


###  產生視覺輸出
技能可以捆綁並執行任何語言的指令碼，為 Claude 提供超越單一提示可能實現的功能。一種模式是產生視覺輸出：在瀏覽器中開啟的互動式 HTML 檔案，用於探索資料、除錯或建立報告。 此範例建立一個程式碼庫探索工具：一個互動式樹狀檢視，您可以在其中展開和摺疊目錄、一目瞭然地查看檔案大小，並按顏色識別檔案類型。 建立技能目錄：

```

mkdir -p ~/.claude/skills/codebase-visualizer/scripts

```

將此儲存到 `~/.claude/skills/codebase-visualizer/SKILL.md`。描述告訴 Claude 何時啟動此技能，說明告訴 Claude 執行捆綁的指令碼。指令碼路徑使用 [`${CLAUDE_SKILL_DIR}`](https://code.claude.com/docs/zh-TW/skills#available-string-substitutions)，因此無論技能是在個人、專案或外掛程式層級安裝，它都能正確解析：

```

______________________________________________________________________

## name: codebase-visualizer description: Generate an interactive collapsible tree visualization of your codebase. Use when exploring a new repo, understanding project structure, or identifying large files. allowed-tools: Bash(python3 \*)

# Codebase Visualizer

Generate an interactive HTML tree view that shows your project's file structure with collapsible directories.

## Usage

Run the visualization script from your project root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` in the current directory and opens it in your default browser.

## What the visualization shows

- **Collapsible directories**: Click folders to expand/collapse
- **File sizes**: Displayed next to each file
- **Colors**: Different colors for different file types
- **Directory totals**: Shows aggregate size of each folder

```

將此儲存到 `~/.claude/skills/codebase-visualizer/scripts/visualize.py`。此指令碼掃描目錄樹並產生一個自包含的 HTML 檔案，包含：
  * 一個**摘要側邊欄** ，顯示檔案計數、目錄計數、總大小和檔案類型數量
  * 一個**長條圖** ，按檔案類型（按大小排名前 8 個）分解程式碼庫
  * 一個**可摺疊樹** ，您可以在其中展開和摺疊目錄，並帶有顏色編碼的檔案類型指示器

該指令碼需要 Python 3，但僅使用內建程式庫，因此無需安裝任何套件：

```

#!/usr/bin/env python3 """Generate an interactive collapsible tree visualization of a codebase."""

import json import sys import webbrowser from html import escape from pathlib import Path from collections import Counter

IGNORE = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}

def scan(path: Path, stats: dict) -> dict: result = {"name": path.name, "children": [], "size": 0} try: for item in sorted(path.iterdir()): if item.name in IGNORE or item.name.startswith('.'): continue if item.is_file(): size = item.stat().st_size ext = item.suffix.lower() or '(no ext)' result["children"].append({"name": item.name, "size": size, "ext": ext}) result["size"] += size stats["files"] += 1 stats["extensions"][ext] += 1 stats["ext_sizes"][ext] += size elif item.is_dir(): stats["dirs"] += 1 child = scan(item, stats) if child\["children"\]: result["children"].append(child) result["size"] += child["size"] except PermissionError: pass return result

def generate_html(data: dict, stats: dict, output: Path) -> None: ext_sizes = stats["ext_sizes"] total_size = sum(ext_sizes.values()) or 1 sorted_exts = sorted(ext_sizes.items(), key=lambda x: -x[1])[:8] colors = { '.js': '#f7df1e', '.ts': '#3178c6', '.py': '#3776ab', '.go': '#00add8', '.rs': '#dea584', '.rb': '#cc342d', '.css': '#264de4', '.html': '#e34c26', '.json': '#6b7280', '.md': '#083fa1', '.yaml': '#cb171e', '.yml': '#cb171e', '.mdx': '#083fa1', '.tsx': '#3178c6', '.jsx': '#61dafb', '.sh': '#4eaa25', } lang_bars = "".join( f'<div class="bar-row"><span class="bar-label">{ext}</span>' f'\<div class="bar" style="width:{(size/total_size)\*100}%;background:{colors.get(ext,"#6b7280")}"></div>' f'<span class="bar-pct">{(size/total_size)\*100:.1f}%</span></div>' for ext, size in sorted_exts ) def fmt(b): if b < 1024: return f"{b} B" if b < 1048576: return f"{b/1024:.1f} KB" return f"{b/1048576:.1f} MB"

```
html = f'''<!DOCTYPE html>
```

<html><head>
  <meta charset="utf-8"><title>Codebase Explorer</title>
  <style>
    body {{ font: 14px/1.5 system-ui, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
    .container {{ display: flex; height: 100vh; }}
    .sidebar {{ width: 280px; background: #252542; padding: 20px; border-right: 1px solid #3d3d5c; overflow-y: auto; flex-shrink: 0; }}
    .main {{ flex: 1; padding: 20px; overflow-y: auto; }}
    h1 {{ margin: 0 0 10px 0; font-size: 18px; }}
    h2 {{ margin: 20px 0 10px 0; font-size: 14px; color: #888; text-transform: uppercase; }}
    .stat {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #3d3d5c; }}
    .stat-value {{ font-weight: bold; }}
    .bar-row {{ display: flex; align-items: center; margin: 6px 0; }}
    .bar-label {{ width: 55px; font-size: 12px; color: #aaa; }}
    .bar {{ height: 18px; border-radius: 3px; }}
    .bar-pct {{ margin-left: 8px; font-size: 12px; color: #666; }}
    .tree {{ list-style: none; padding-left: 20px; }}
    details {{ cursor: pointer; }}
    summary {{ padding: 4px 8px; border-radius: 4px; }}
    summary:hover {{ background: #2d2d44; }}
    .folder {{ color: #ffd700; }}
    .file {{ display: flex; align-items: center; padding: 4px 8px; border-radius: 4px; }}
    .file:hover {{ background: #2d2d44; }}
    .size {{ color: #888; margin-left: auto; font-size: 12px; }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }}
  </style>
</head><body>
  <div class="container">
    <div class="sidebar">
      <h1>📊 Summary</h1>
      <div class="stat"><span>Files</span><span class="stat-value">{stats["files"]:,}</span></div>
      <div class="stat"><span>Directories</span><span class="stat-value">{stats["dirs"]:,}</span></div>
      <div class="stat"><span>Total size</span><span class="stat-value">{fmt(data["size"])}</span></div>
      <div class="stat"><span>File types</span><span class="stat-value">{len(stats["extensions"])}</span></div>
      <h2>By file type</h2>
      {lang_bars}
    </div>
    <div class="main">
      <h1>📁 {escape(data["name"])}</h1>
      <ul class="tree" id="root"></ul>
    </div>
  </div>
  <script>
    const data = {json.dumps(data)};
    const colors = {json.dumps(colors)};
    function fmt(b) {{ if (b < 1024) return b + ' B'; if (b < 1048576) return (b/1024).toFixed(1) + ' KB'; return (b/1048576).toFixed(1) + ' MB'; }}
    function esc(s) {{ return s.replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c])); }}
    function render(node, parent) {{
      if (node.children) {{
        const det = document.createElement('details');
        det.open = parent === document.getElementById('root');
        det.innerHTML = `<summary><span class="folder">📁 ${{esc(node.name)}}</span><span class="size">${{fmt(node.size)}}</span></summary>`;
        const ul = document.createElement('ul'); ul.className = 'tree';
        node.children.sort((a,b) => (b.children?1:0)-(a.children?1:0) || a.name.localeCompare(b.name));
        node.children.forEach(c => render(c, ul));
        det.appendChild(ul);
        const li = document.createElement('li'); li.appendChild(det); parent.appendChild(li);
      }} else {{
        const li = document.createElement('li'); li.className = 'file';
        li.innerHTML = `<span class="dot" style="background:${{colors[node.ext]||'#6b7280'}}"></span>${{esc(node.name)}}<span class="size">${{fmt(node.size)}}</span>`;
        parent.appendChild(li);
      }}
    }}
    data.children.forEach(c => render(c, document.getElementById('root')));
  </script>
</body></html>'''
    output.write_text(html)

if __name__ == '__main__': target = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve() stats = {"files": 0, "dirs": 0, "extensions": Counter(), "ext_sizes": Counter()} data = scan(target, stats) out = Path('codebase-map.html') generate_html(data, stats, out) print(f'Generated {out.absolute()}') webbrowser.open(f'file://{out.absolute()}')

```

See all 133 lines
若要測試，請在任何專案中開啟 Claude Code 並詢問「Visualize this codebase.」Claude 執行指令碼，該指令碼會列印產生的檔案路徑，例如 `Generated /path/to/codebase-map.html`，並在您的瀏覽器中開啟它。如果您在無瀏覽器開啟的無頭環境中工作，列印的路徑會確認指令碼成功。 此模式適用於任何視覺輸出：相依性圖表、測試涵蓋範圍報告、API 文件或資料庫架構視覺化。捆綁的指令碼執行工作，而 Claude 處理協調。
##  疑難排解
###  Skill 未觸發
如果 Claude 在預期時未使用您的 skill：
  1. 檢查描述是否包含使用者會自然說出的關鍵字
  2. 驗證 skill 是否出現在「What skills are available?」中
  3. 嘗試重新表述您的請求以更密切地符合描述
  4. 如果 skill 可由使用者叫用，請使用 `/skill-name` 直接叫用它

如果 frontmatter YAML 格式不正確，Claude Code 會以空的中繼資料載入 skill 主體，因此 `/skill-name` 仍然有效，但 Claude 無法對您的 `description` 進行比對。使用 `--debug` 執行以查看解析錯誤。 如果 skill 隨附在 plugin 中，您可以測量它在實際提示中觸發的頻率，而不是逐一檢查：使用 [`tool_used: Skill` grader](https://code.claude.com/docs/zh-TW/plugin-evals#create-your-first-eval-suite) 撰寫評估案例，並在每次描述變更後使用 `claude plugin eval` 執行它。 若要找到 frontmatter 無法解析的 `SKILL.md` 檔案，請在 skills 目錄上執行 [`claude plugin validate`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest)，例如針對專案 skills 執行 `claude plugin validate .claude/skills`，或針對個人 skills 執行 `claude plugin validate ~/.claude/skills`。需要 Claude Code v2.1.233 或更新版本。
###  Skill 觸發過於頻繁
如果 Claude 在您不想要時使用您的 skill：
  1. 使描述更具體
  2. 如果您只想要手動叫用，請新增 `disable-model-invocation: true`


###  Skill 描述被截斷
Claude Code 會將 skill 名稱和描述的清單載入到上下文中，以便 Claude 知道有哪些可用的。清單始終包含每個 skill 名稱，但如果您有許多 skills，Claude Code 會縮短描述以符合清單的字元預算，這可能會移除 Claude 需要比對您的請求的關鍵字。預算按模型上下文視窗的 1% 進行調整。當清單超出預算時，Claude Code 會從您叫用最少的 skills 開始刪除描述，因此您使用最多的 skills 會保留其完整文字。 執行 `/doctor` 以估計清單的上下文成本及其最大貢獻者。若要找到值得關閉的 skills，請執行 [`/skill-doctor`](https://code.claude.com/docs/zh-TW/skills#find-unused-skills)。當清單超出其預算時，Claude Code 也會將警告寫入偵錯日誌，可透過 [`--debug`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 查看。 `/context` 中的 Skills 列會報告套用預算後清單的大小，因此它與模型接收的內容相符。在 v2.1.196 之前，該列會計算每個描述的完整文字，並且可能顯示的值比設定的預算大好幾倍。 若要提高預算，請設定 [`skillListingBudgetFraction`](https://code.claude.com/docs/zh-TW/settings-reference#skilllistingbudgetfraction) 設定（例如 `0.02` = 2%）或 `SLASH_COMMAND_TOOL_CHAR_BUDGET` 環境變數為固定字元計數。若要為其他 skills 釋放預算，請在 [`skillOverrides`](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings) 中將低優先順序項目設定為 `"name-only"`，以便它們在沒有描述的情況下列出。您也可以在來源處修剪 `description` 和 `when_to_use` 文字：將關鍵使用案例放在首位，因為每個項目的組合文字上限為 1,536 個字元，無論預算如何。上限可透過 [`skillListingMaxDescChars`](https://code.claude.com/docs/zh-TW/settings-reference#skilllistingmaxdescchars) 進行設定。
##  相關資源
  * **[除錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config)** ：診斷為什麼 skill 沒有出現或觸發
  * **[評估 skill 輸出品質](https://agentskills.io/skill-creation/evaluating-skills)** ：agentskills.io 上的 eval 檔案格式和反覆運算工作流程
  * **[Skill 編寫最佳實踐](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)** ：適用於 Claude 產品的編寫指導
  * **[Subagents](https://code.claude.com/docs/zh-TW/sub-agents)** ：委派任務給專門的代理
  * **[Plugins](https://code.claude.com/docs/zh-TW/plugins)** ：使用其他擴展功能打包和分發 skills
  * **[Hooks](https://code.claude.com/docs/zh-TW/hooks)** ：自動化工具事件周圍的工作流程
  * **[Memory](https://code.claude.com/docs/zh-TW/memory)** ：管理 CLAUDE.md 檔案以取得持久上下文
  * **[Commands](https://code.claude.com/docs/zh-TW/commands)** ：內建命令和捆綁 skills 的參考
  * **[Permissions](https://code.claude.com/docs/zh-TW/permissions)** ：控制工具和 skill 存取
  * **[Claude Tag skills](https://claude.com/docs/claude-tag/admins/skills-repo)** ：提交到儲存庫的專案 skills 在該儲存庫用於 Claude Tag 頻道時也會載入


是否
助手
```
