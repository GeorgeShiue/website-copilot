Plugins 讓您使用可在專案和團隊中共享的自訂功能來擴展 Claude Code。本指南涵蓋使用 skills、agents、hooks 和 MCP servers 建立您自己的 plugins。 想要安裝現有的 plugins？請參閱[探索和安裝 plugins](https://code.claude.com/docs/zh-TW/discover-plugins)。如需完整的技術規格，請參閱 [Plugins 參考](https://code.claude.com/docs/zh-TW/plugins-reference)。

## 何時使用 plugins 與獨立配置

Claude Code 支援兩種方式來新增自訂 skills、agents 和 hooks：

| 方法                                                                                                                                                                   | Skill 名稱           | 最適合                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | -------------------------------------------------- |
| **獨立** （`.claude/` 目錄）                                                                                                                                           | `/hello`             | 個人工作流程、專案特定的自訂、快速實驗             |
| **Plugins** （包含 skills、agents、hooks 或 `.claude-plugin/plugin.json` 資訊清單的自包含目錄）                                                                        | `/plugin-name:hello` | 與隊友共享、分發到社群、版本化發佈、跨專案重複使用 |
| 在 `.claude/` 中從獨立配置開始進行快速迭代，然後在準備好共享時[轉換為 plugin](https://code.claude.com/docs/zh-TW/plugins#convert-existing-configurations-to-plugins)。 |                      |                                                    |

## 快速入門

本快速入門將引導您建立具有自訂 skill 的 plugin。您將建立一個清單（定義您的 plugin 的配置檔案）、新增一個 skill，並使用 `--plugin-dir` 旗標在本地進行測試。

### 先決條件

- Claude Code [已安裝並驗證](https://code.claude.com/docs/zh-TW/quickstart#step-1-install-claude-code)

### 建立您的第一個 plugin

1 建立 plugin 目錄 每個 plugin 都位於其自己的目錄中，包含您的 skills、agents 或 hooks，可選地與 `.claude-plugin/plugin.json` 清單並存。位置對於本快速入門並不重要，因為您將在測試步驟中使用 `--plugin-dir` 指向 Claude Code 該目錄。在任何方便的地方建立它，例如暫存資料夾或專案目錄：

```
mkdir my-first-plugin

```

其餘步驟從父目錄執行，並參考相對於它的路徑，例如 `my-first-plugin/...`。 2 建立 plugin 清單 位於 `.claude-plugin/plugin.json` 的清單檔案定義您的 plugin 的身份：其名稱、描述和版本。Claude Code 使用此中繼資料在 plugin 管理器中顯示您的 plugin。在您的 plugin 資料夾內建立 `.claude-plugin` 目錄：

```
mkdir my-first-plugin/.claude-plugin

```

然後使用此內容建立 `my-first-plugin/.claude-plugin/plugin.json`： my-first-plugin/.claude-plugin/plugin.json

```
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}

```

| 欄位                                                                                                                                                                                                                                                              | 用途                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                                                                                                                                                                                                                                                            | 唯一識別碼和 skill 命名空間。Skills 以此為前綴（例如 `/my-first-plugin:hello`）。                                                                                                                                                                                                                                                                                                                                                                                                  |
| `description`                                                                                                                                                                                                                                                     | 在瀏覽或安裝 plugins 時在 plugin 管理器中顯示。                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `version`                                                                                                                                                                                                                                                         | 選用。如果設定，使用者只會在您更新此欄位時收到更新，除了 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)或 plugin [就地載入](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)外；請參閱[版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)。如果省略，版本來自[版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)中的下一個來源。 |
| `author`                                                                                                                                                                                                                                                          | 選用。有助於歸屬。                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 如需 `homepage`、`repository` 和 `license` 等其他欄位，請參閱[完整清單架構](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-manifest-schema)。                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 3                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 新增 skill                                                                                                                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Skills 位於 `skills/` 目錄中。每個 skill 是一個包含 `SKILL.md` 檔案的資料夾。資料夾名稱成為 skill 名稱，以 plugin 的命名空間為前綴（在名為 `my-first-plugin` 的 plugin 中的 `hello/` 建立 `/my-first-plugin:hello`）。在您的 plugin 資料夾中建立一個 skill 目錄： |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

```
mkdir -p my-first-plugin/skills/hello

```

然後使用此內容建立 `my-first-plugin/skills/hello/SKILL.md`： my-first-plugin/skills/hello/SKILL.md

```
---
description: Greet the user with a friendly message
disable-model-invocation: true
---

Greet the user warmly and ask how you can help them today.

```

4 測試您的 plugin 使用 `--plugin-dir` 旗標執行 Claude Code 以載入您的 plugin：

```
claude --plugin-dir ./my-first-plugin

```

Claude Code 啟動後，嘗試您的新 skill：

```
/my-first-plugin:hello

```

您將看到 Claude 以問候語回應。執行 `/help` 並開啟**自訂命令** 標籤，以查看您的 skill 列在 plugin 命名空間下。 **為什麼要命名空間？** Plugin skills 始終被命名空間化（例如 `/my-first-plugin:hello`），以防止多個 plugins 具有相同名稱的 skills 時發生衝突。若要變更命名空間前綴，請更新 `plugin.json` 中的 `name` 欄位。 5 新增 skill 引數 透過接受使用者輸入使您的 skill 動態化。`$ARGUMENTS` 佔位符會擷取使用者在 skill 名稱後提供的任何文字。更新您的 `SKILL.md` 檔案： my-first-plugin/skills/hello/SKILL.md

```
---
description: Greet the user with a personalized message
---

# Hello Skill

Greet the user named "$ARGUMENTS" warmly and ask how you can help them today. Make the greeting personal and encouraging.

```

執行 `/reload-plugins` 以取得變更。然後嘗試使用您的名稱執行 skill：

```
/my-first-plugin:hello Alex

```

Claude 將按名稱向您問候。如需有關將引數傳遞給 skills 的更多資訊，請參閱 [Skills](https://code.claude.com/docs/zh-TW/skills#pass-arguments-to-skills)。 `--plugin-dir` 旗標對於開發和測試很有用。當您準備好與他人共享您的 plugin 時，請參閱[建立和分發 plugin 市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)。

## 在您的 skills 目錄中開發 plugin

與其在每次啟動時傳遞 `--plugin-dir`，您可以在您的 skills 目錄中保留一個 plugin，並讓 Claude Code 自動載入它。`claude plugin init` 會為您建立一個：

```
claude plugin init my-tool

```

這會建立 `~/.claude/skills/my-tool/`，其中包含 `.claude-plugin/plugin.json` 清單和一個入門 `SKILL.md`。在下一個工作階段中，它會以 `my-tool@skills-dir` 的形式載入，無需市場或安裝步驟。 如需自動載入規則、個人與專案範圍、工作區信任要求，以及如何更新或移除一個，請參閱 [Skills-directory plugins](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)。

## Plugin 結構概述

您已建立了具有 skill 的 plugin，但 plugins 可以包含更多內容：自訂 agents、hooks、MCP servers、LSP servers 和背景監視器。 **常見錯誤** ：不要將 `commands/`、`agents/`、`skills/` 或 `hooks/` 放在 `.claude-plugin/` 目錄內。只有 `plugin.json` 應該在 `.claude-plugin/` 內。所有其他目錄必須位於 plugin 根目錄級別。plugin 根目錄是個別 plugin 自己的目錄，例如來自[快速入門](https://code.claude.com/docs/zh-TW/plugins#quickstart)的 `my-first-plugin/`。它永遠不是 `~/.claude/`。例如，Claude Code 不會讀取放在 `~/.claude/.mcp.json` 的 `.mcp.json`。

| 目錄                                                                                                                                                                                                                                                    | 位置          | 用途                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.claude-plugin/`                                                                                                                                                                                                                                       | Plugin 根目錄 | 包含 `plugin.json` 清單（如果元件使用預設位置，則為選用）                                                                                                                                                                     |
| `skills/`                                                                                                                                                                                                                                               | Plugin 根目錄 | 作為 `<name>/SKILL.md` 目錄的 Skills                                                                                                                                                                                          |
| `commands/`                                                                                                                                                                                                                                             | Plugin 根目錄 | 作為平面 Markdown 檔案的 Skills。新 plugins 請使用 `skills/`                                                                                                                                                                  |
| `agents/`                                                                                                                                                                                                                                               | Plugin 根目錄 | 自訂 agent 定義                                                                                                                                                                                                               |
| `hooks/`                                                                                                                                                                                                                                                | Plugin 根目錄 | `hooks.json` 中的事件處理程式                                                                                                                                                                                                 |
| `.mcp.json`                                                                                                                                                                                                                                             | Plugin 根目錄 | MCP server 配置                                                                                                                                                                                                               |
| `.lsp.json`                                                                                                                                                                                                                                             | Plugin 根目錄 | 用於程式碼智慧的 LSP server 配置                                                                                                                                                                                              |
| `monitors/`                                                                                                                                                                                                                                             | Plugin 根目錄 | `monitors.json` 中的背景監視器配置                                                                                                                                                                                            |
| `bin/`                                                                                                                                                                                                                                                  | Plugin 根目錄 | 在啟用 plugin 時新增到 Bash tool 的 `PATH` 的可執行檔。您無法在[透過 claude.ai 組織設定分發的 plugin](https://code.claude.com/docs/zh-TW/plugin-marketplaces#keep-executables-out-of-the-top-level-bin-directory)中包含此目錄 |
| `settings.json`                                                                                                                                                                                                                                         | Plugin 根目錄 | 啟用 plugin 時應用的預設[設定](https://code.claude.com/docs/zh-TW/settings)                                                                                                                                                   |
| 只要 plugin 恰好包含一個 skill，就可以直接在 plugin 根目錄放置 `SKILL.md`，而不需要建立 `skills/` 目錄。Claude Code 會將其載入為單一 skill，並使用 frontmatter 的 `name` 欄位作為叫用名稱。對於可能成長為多個 skill 的 plugins，請使用 `skills/` 配置。 |               |                                                                                                                                                                                                                               |

## 開發更複雜的外掛程式

一旦您熟悉了基本外掛程式，您可以建立更複雜的擴充功能。

### 將 Skills 新增至您的外掛程式

外掛程式可以包含 [Agent Skills](https://code.claude.com/docs/zh-TW/skills) 來擴展 Claude 的功能。Skills 是由模型呼叫的：Claude 會根據任務背景自動使用它們。 在您的外掛程式根目錄新增一個 `skills/` 目錄，其中包含包含 `SKILL.md` 檔案的 Skill 資料夾：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── code-review/
        └── SKILL.md

```

每個 `SKILL.md` 包含 YAML frontmatter 和說明。包含一個 `description`，以便 Claude 知道何時使用該 skill：

```
---
description: Reviews code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage

```

安裝外掛程式後，檢查安裝摘要：如果它報告 `Run /reload-plugins to activate.`，請參閱 [Apply plugin changes without restarting](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting) 以在您目前的工作階段中載入 Skills。如需完整的 Skill 編寫指南（包括漸進式揭露和工具限制），請參閱 [Agent Skills](https://code.claude.com/docs/zh-TW/skills)。

### 將 LSP 伺服器新增至您的外掛程式

對於 TypeScript、Python 和 Rust 等常見語言，請從官方市集安裝預先建立的 LSP 外掛程式。只有在您需要支援尚未涵蓋的語言時，才建立自訂 LSP 外掛程式。 LSP（Language Server Protocol）外掛程式為 Claude 提供即時程式碼智慧。如果您需要支援沒有官方 LSP 外掛程式的語言，您可以透過將 `.lsp.json` 檔案新增至您的外掛程式來建立自己的： .lsp.json

```
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}

```

安裝您外掛程式的使用者必須在其機器上安裝語言伺服器二進位檔。 若要確認伺服器啟動，請啟動啟用外掛程式的 Claude Code 並檢查 `/plugin` 錯誤標籤：無法啟動的語言伺服器會出現在那裡，例如當二進位檔未安裝時出現 `Executable not found in $PATH`。具有無效設定的項目會被跳過；執行 `claude --debug` 以查看原因。 如需完整的 LSP 設定選項，請參閱 [LSP servers](https://code.claude.com/docs/zh-TW/plugins-reference#lsp-servers)。

### 將背景監視器新增至您的外掛程式

背景監視器讓您的外掛程式在背景中監視日誌、檔案或外部狀態，並在事件到達時通知 Claude。Claude Code 在外掛程式啟用時自動啟動每個監視器，因此您不需要指示 Claude 啟動監視。 在外掛程式根目錄新增一個 `monitors/monitors.json` 檔案，其中包含監視器項目的陣列： monitors/monitors.json

```
[
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log"
  }
]

```

來自 `command` 的每個 stdout 行都會在工作階段期間作為通知傳遞給 Claude。如需完整的結構描述（包括 `when` 觸發器和變數替換），請參閱 [Monitors](https://code.claude.com/docs/zh-TW/plugins-reference#monitors)。

### 使用您的外掛程式提供預設設定

外掛程式可以在外掛程式根目錄包含一個 `settings.json` 檔案，以在啟用外掛程式時套用預設設定。目前僅支援 `agent` 和 `subagentStatusLine` 鍵。 設定 `agent` 會啟用外掛程式的其中一個 [custom agents](https://code.claude.com/docs/zh-TW/sub-agents) 作為主執行緒，套用其系統提示、工具限制和模型。這讓外掛程式在啟用時預設改變 Claude Code 的行為方式。 settings.json

```
{
  "agent": "security-reviewer"
}

```

此範例啟用在外掛程式的 `agents/` 目錄中定義的 `security-reviewer` 代理。來自 `settings.json` 的設定優先於在 `plugin.json` 中宣告的 `settings`。未知的鍵會被無聲地忽略。

### 組織複雜的外掛程式

對於具有許多元件的外掛程式，請按功能組織您的目錄結構。如需完整的目錄配置和組織模式，請參閱 [Plugin directory structure](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-directory-structure)。

### 在本機測試您的外掛程式

使用 `--plugin-dir` 旗標在開發期間測試外掛程式。這會直接載入您的外掛程式，無需安裝。

```
claude --plugin-dir ./my-plugin

```

該旗標也接受外掛程式目錄的 `.zip` 封存。

```
claude --plugin-dir ./my-plugin.zip

```

當 `--plugin-dir` 外掛程式的名稱與已安裝的市集外掛程式相同時，本機副本在該工作階段中優先。這讓您可以測試已安裝的外掛程式的變更，而無需先卸載它。例外是受管設定強制啟用或強制停用的外掛程式：`--plugin-dir` 無法覆蓋這些。 當您對外掛程式進行變更時，執行 `/reload-plugins` 以在不重新啟動的情況下取得更新。這會重新載入外掛程式、skills、代理、hooks、外掛程式 MCP 伺服器和外掛程式 LSP 伺服器；在沒有互動式終端的工作階段中，外掛程式 MCP 伺服器變更 [等待您的下一個工作階段](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)。測試您的外掛程式元件：

- 使用 `/plugin-name:skill-name` 嘗試您的 skills
- 檢查代理是否出現在 `/context` 下的 Custom Agents 中，或透過其範圍名稱 @-提及一個
- 觸發每個 hook 匹配的事件，例如要求 Claude 編輯檔案以進行 `PostToolUse` hook，並確認其效果。Claude Code 會記錄哪些 hooks 匹配、其結束代碼和其輸出在 [debug log](https://code.claude.com/docs/zh-TW/hooks#debug-hooks) 中

您可以透過多次指定旗標來一次載入多個外掛程式：

```
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two

```

若要測試外掛程式及其依賴的外掛程式，請參閱 [Test a plugin and its dependency locally](https://code.claude.com/docs/zh-TW/plugin-dependencies#test-a-plugin-and-its-dependency-locally)。 使用 `--plugin-dir` 嘗試外掛程式可以告訴您它是否能夠運作。若要找出 Claude 實際上多常使用它並獲得正確的結果，請使用 [`claude plugin eval`](https://code.claude.com/docs/zh-TW/plugin-evals) 針對一組測試提示執行它。每個提示會在載入和不載入外掛程式的情況下執行多次，因此您可以看到外掛程式的貢獻，並在您變更它或新模型發佈時捕捉迴歸。 若要從一個位置載入多個外掛程式，請傳遞包含它們的資料夾，例如 `--plugin-dir ./plugins`。載入外掛程式資料夾需要 Claude Code v2.1.265 或更新版本。Claude Code 讀取資料夾的頂層以決定哪些外掛程式載入，在互動式工作階段中，它也會監視資料夾以進行後續變更：

- **載入的內容** ：如果資料夾的頂層沒有資訊清單或外掛程式元件，Claude Code 會將其視為外掛程式資料夾。每個具有 `.claude-plugin/plugin.json` 資訊清單的直接子資料夾都會作為單獨的外掛程式載入。Claude Code 會跳過資料夾中的所有其他內容，而不報告錯誤，包括沒有資訊清單的外掛程式。
- **互動式工作階段期間的變更** ：您新增的子資料夾在其資訊清單就位後會作為新外掛程式載入，當您移除子資料夾時，其外掛程式會卸載。Claude Code 會為每個變更在工作階段中列印一行。如果在對話中途套用變更會 [使提示快取失效](https://code.claude.com/docs/zh-TW/prompt-caching#enabling-or-disabling-a-plugin)，Claude Code 會保留它，該行會說執行 `/reload-plugins` 以套用它。

若要測試已封裝為 `.zip` 封存並託管在 URL 上的外掛程式（例如 CI 建置成品），請改用 `--plugin-url`。Claude Code 在啟動時擷取封存並僅為該工作階段載入它。如果 Claude Code 無法擷取封存或封存無效，它會在沒有外掛程式的情況下啟動，並記錄您可以在 `/plugin` 管理員的 **Errors** 標籤中檢閱的外掛程式載入錯誤。與任何外掛程式來源相同的 [trust considerations](https://code.claude.com/docs/zh-TW/discover-plugins#security) 適用：只將此旗標指向您控制或信任的封存。 若要載入多個外掛程式，請為每個 URL 重複該旗標：

```
claude --plugin-url https://example.com/my-plugin.zip --plugin-url https://example.com/other.zip

```

或將空格分隔的 URL 作為一個引用的引數傳遞：

```
claude --plugin-url "https://example.com/my-plugin.zip https://example.com/other.zip"

```

### 偵錯外掛程式問題

如果您的外掛程式未如預期運作：

1. **檢查結構** ：確保您的目錄位於外掛程式根目錄，而不是在 `.claude-plugin/` 內
1. **個別測試元件** ：分別檢查每個 skill、代理和 hook
1. **使用驗證和偵錯工具** ：請參閱 [Debugging and development tools](https://code.claude.com/docs/zh-TW/plugins-reference#debugging-and-development-tools) 以取得 CLI 命令和疑難排解技術

### 分享您的外掛程式

當您的外掛程式準備好分享時：

1. **新增文件** ：包含一個 `README.md`，其中包含安裝和使用說明
1. **選擇版本控制策略** ：決定是否設定明確的 `version` 或依賴 [version management](https://code.claude.com/docs/zh-TW/plugins-reference#version-management) 中描述的後備。
1. **建立或使用市集** ：透過 [plugin marketplaces](https://code.claude.com/docs/zh-TW/plugin-marketplaces) 進行分發以進行安裝
1. **與他人測試** ：在更廣泛的分發之前，讓團隊成員測試外掛程式

一旦您的外掛程式在市集中，其他人可以使用 [Discover and install plugins](https://code.claude.com/docs/zh-TW/discover-plugins) 中的說明安裝它。若要將外掛程式保持在您的團隊內部，請在 [private repository](https://code.claude.com/docs/zh-TW/plugin-marketplaces#private-repositories) 中託管市集。

### 將您的外掛程式提交至社群市集

Anthropic 為 Claude Code 外掛程式維護兩個公開市集：

- **`claude-plugins-official`**：由 Anthropic 維護的精選外掛程式集。Claude Code 在您第一次以互動方式啟動 Claude Code 時自動註冊它。如果您在該首次互動啟動之前以非互動方式執行 Claude Code，或[marketplace policy](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions) 阻止了較早的嘗試，請使用 `claude plugin marketplace add anthropics/claude-plugins-official` 自行註冊。
- **`claude-community`**：公開社群市集，第三方提交在審查後會進入該市集。使用者使用`/plugin marketplace add anthropics/claude-plugins-community` 新增它，並將其安裝為 `@claude-community`。

若要提交您的外掛程式以進行社群市集審查，請使用其中一個應用程式內表單：

- **claude.ai** ：[claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new)
- **Console** ：[platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

claude.ai 表單需要 Team 或 Enterprise 組織和目錄管理存取權；組織擁有者預設具有此存取權。不屬於 Team 或 Enterprise 組織的個別作者可以改用 Console 表單。 在提交之前，在本機執行 `claude plugin validate ./your-plugin`，將 `./your-plugin` 替換為您的外掛程式目錄的路徑。審查管道對每個提交執行相同的檢查，以及自動安全篩選。驗證通過時，Claude Code 會列印 `✔ Validation passed`，或如果有警告，則列印 `✔ Validation passed with warnings`。警告不會導致驗證失敗；新增 `--strict` 以將它們視為錯誤。 已核准的外掛程式會固定到 [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) 目錄中的特定提交 SHA，CI 會在您推送新提交至您的儲存庫時自動提升該固定。公開目錄每晚從審查管道同步，因此核准和您的外掛程式出現在 `marketplace.json` 之間可能會有延遲。若要檢查您的外掛程式是否已可安裝，請在 [community catalog](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json) 中搜尋其名稱。 官方市集 `claude-plugins-official` 是單獨精選的。Anthropic 自行決定要包含哪些外掛程式。沒有申請流程，提交表單不會將外掛程式新增至官方市集。 如果 Anthropic 在官方市集中列出您的外掛程式，您的 CLI 可以提示 Claude Code 使用者安裝它。請參閱 [Recommend your plugin from your CLI](https://code.claude.com/docs/zh-TW/plugin-hints)。

## 將現有配置轉換為 plugins

如果您已經在 `.claude/` 目錄中有 skills 或 hooks，您可以將它們轉換為 plugin，以便更輕鬆地共享和分發。

### 遷移步驟

1 建立 plugin 結構 在您的專案根目錄中建立新的 plugin 目錄，與現有的 `.claude/` 資料夾並排放置，以便下一步中的相對 `cp` 路徑能夠解析：

```
mkdir -p my-plugin/.claude-plugin

```

在 `my-plugin/.claude-plugin/plugin.json` 建立清單檔案： my-plugin/.claude-plugin/plugin.json

```
{
  "name": "my-plugin",
  "description": "Migrated from standalone configuration",
  "version": "1.0.0"
}

```

2 複製您現有的檔案 將您現有的每個配置目錄複製到 plugin 根目錄。您可能沒有全部三個：如果目錄不存在，`cp` 會列印 `No such file or directory` 並且不複製任何內容，因此請跳過該命令或忽略錯誤。

```
cp -r .claude/commands my-plugin/

cp -r .claude/agents my-plugin/

cp -r .claude/skills my-plugin/

```

您的 plugin 現在包含您在 `.claude/` 下擁有的目錄副本。執行 `ls my-plugin` 以確認：您應該看到您複製的每個目錄。 3 遷移 hooks 如果您在設定中有 hooks，請建立一個 hooks 目錄：

```
mkdir my-plugin/hooks

```

使用您的 hooks 配置建立 `my-plugin/hooks/hooks.json`。從您的 `.claude/settings.json` 或 `settings.local.json` 複製 `hooks` 物件，因為格式相同。命令在 stdin 上接收 hook 輸入作為 JSON，因此使用 `jq` 來提取檔案路徑： my-plugin/hooks/hooks.json

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npm run lint:fix" }]
      }
    ]
  }
}

```

4 測試您遷移的 plugin 載入您的 plugin 以驗證一切正常：

```
claude --plugin-dir ./my-plugin

```

測試每個元件：執行您的命令、檢查 agents 是否出現在 `/context` 中，並觸發每個 hook 符合的事件以確認其效果。Claude Code 會在[除錯日誌](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)中記錄哪些 hooks 符合以及它們如何退出。

### 遷移時的變更

| 獨立（`.claude/`）                                                                                                                                                                                                                                                                               | Plugin                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| 僅在一個專案中可用                                                                                                                                                                                                                                                                               | 可以透過市場共享                 |
| `.claude/commands/` 中的檔案                                                                                                                                                                                                                                                                     | `plugin-name/commands/` 中的檔案 |
| `settings.json` 中的 Hooks                                                                                                                                                                                                                                                                       | `hooks/hooks.json` 中的 Hooks    |
| 必須手動複製以共享                                                                                                                                                                                                                                                                               | 使用 `/plugin install` 安裝      |
| 遷移後，從 `.claude/` 中移除原始檔案以避免重複。專案和使用者 `.claude/agents/` 定義會覆蓋同名的 plugin agents，因此 plugin 版本只有在移除原始檔案後才會生效。Plugin skills 會被命名為 `/plugin-name:skill-name`，因此原始的 `/skill-name` 和 plugin 副本都會保持可用，而不是其中一個覆蓋另一個。 |                                  |

## 後續步驟

現在您已了解 Claude Code 的 plugin 系統，以下是針對不同目標的建議路徑：

### 對於 plugin 使用者

- [探索和安裝 plugins](https://code.claude.com/docs/zh-TW/discover-plugins)：瀏覽市場並安裝 plugins
- [配置團隊市場](https://code.claude.com/docs/zh-TW/discover-plugins#configure-team-marketplaces)：為您的團隊設定儲存庫級別的 plugins

### 對於 plugin 開發人員

- [使用 evals 測試 plugins](https://code.claude.com/docs/zh-TW/plugin-evals)：測量您的 plugin 所做的變更並在 CI 上進行把關
- [建立和分發市場](https://code.claude.com/docs/zh-TW/plugin-marketplaces)：打包和共享您的 plugins
- [Plugins 參考](https://code.claude.com/docs/zh-TW/plugins-reference)：完整的技術規格
- 深入探討特定的 plugin 元件：
  - [Skills](https://code.claude.com/docs/zh-TW/skills)：skill 開發詳情
  - [Subagents](https://code.claude.com/docs/zh-TW/sub-agents)：agent 配置和功能
  - [Hooks](https://code.claude.com/docs/zh-TW/hooks)：事件處理和自動化
  - [MCP](https://code.claude.com/docs/zh-TW/mcp)：外部工具整合

是否 助手
