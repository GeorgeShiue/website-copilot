**plugin marketplace** 是一個目錄，可讓您將 plugin 分發給他人。Marketplace 提供集中式發現、版本追蹤、自動更新，以及對多種來源類型（包括 git 儲存庫和本機路徑）的支援。本指南將向您展示如何建立自己的 marketplace，以與您的團隊或社群分享 plugin。 想要從現有 marketplace 安裝 plugin？請參閱[探索並安裝預先建立的 plugin](https://code.claude.com/docs/zh-TW/discover-plugins)。

## 概述

建立並分發 marketplace 涉及：

1. **建立 plugin** ：使用 skills、agents、hooks、MCP servers 或 LSP servers 建立一個或多個 plugin。本指南假設您已經有要分發的 plugin；有關如何建立 plugin 的詳細資訊，請參閱[建立 plugin](https://code.claude.com/docs/zh-TW/plugins)。
1. **建立 marketplace 檔案** ：定義 `marketplace.json`，列出您的 plugin 及其位置。請參閱[建立 marketplace 檔案](https://code.claude.com/docs/zh-TW/plugin-marketplaces#create-the-marketplace-file)。
1. **託管 marketplace** ：推送到 GitHub、GitLab 或其他 git 主機。請參閱[託管並分發 marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces#host-and-distribute-marketplaces)。
1. **與使用者分享** ：使用者使用 `/plugin marketplace add` 新增您的 marketplace 並安裝個別 plugin。請參閱[探索並安裝 plugin](https://code.claude.com/docs/zh-TW/discover-plugins)。

一旦您的 marketplace 上線，您可以透過推送變更到您的儲存庫來更新它。使用者使用 `/plugin marketplace update` 重新整理其本機副本。

## 逐步解說：建立本機市集

此範例建立一個市集，其中包含一個外掛程式：用於程式碼審查的 `quality-review` 技能。您將建立目錄結構、新增技能、建立外掛程式資訊清單和市集目錄，然後安裝並測試它。 1 建立目錄結構

```
mkdir -p my-marketplace/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/skills/quality-review

```

2 建立技能 建立一個 `SKILL.md` 檔案，定義 `quality-review` 技能的功能。 my-marketplace/plugins/quality-review-plugin/skills/quality-review/SKILL.md

```
---
description: Review code for bugs, security, and performance
---

Review the code I've selected or the recent changes for:
- Potential bugs or edge cases
- Security concerns
- Performance issues
- Readability improvements

Be concise and actionable.

```

3 建立外掛程式資訊清單 建立一個 `plugin.json` 檔案，描述該外掛程式。資訊清單位於 `.claude-plugin/` 目錄中。 my-marketplace/plugins/quality-review-plugin/.claude-plugin/plugin.json

```
{
  "name": "quality-review-plugin",
  "description": "Adds a quality-review skill for quick code reviews",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}

```

設定 `version` 表示使用者只有在您變更此欄位時才會收到更新，因此在每次發行時都要提升版本。具有 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources) 的外掛程式不會由此欄位固定。從市集新增為本機目錄的市集中 [就地載入](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution) 的外掛程式也不會被固定。如果您省略 `version`，版本會來自 [版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management) 中的下一個來源。 4 建立市集檔案 建立列出您的外掛程式的市集目錄。 my-marketplace/.claude-plugin/marketplace.json

```
{
  "name": "my-plugins",
  "owner": {
    "name": "Your Name"
  },
  "plugins": [
    {
      "name": "quality-review-plugin",
      "source": "./plugins/quality-review-plugin",
      "description": "Adds a quality-review skill for quick code reviews"
    }
  ]
}

```

5 新增並安裝 從包含 `my-marketplace` 的目錄啟動 Claude Code 並執行下列命令。安裝命令會開啟外掛程式詳細資料檢視，您可在其中選擇安裝範圍以確認安裝。檢查安裝摘要：如果它報告 `Run /reload-plugins to activate.`，請參閱 [不重新啟動即可套用外掛程式變更](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)。

```
/plugin marketplace add ./my-marketplace
/plugin install quality-review-plugin@my-plugins

```

6 試試看 在編輯器中選擇一些程式碼並執行您的新技能。外掛程式技能會以外掛程式名稱作為命名空間。

```
/quality-review-plugin:quality-review

```

若要深入瞭解外掛程式可以執行的操作，包括 hooks、agents、MCP 伺服器和 LSP 伺服器，請參閱 [Plugins](https://code.claude.com/docs/zh-TW/plugins)。 **外掛程式的安裝方式** ：當使用者安裝外掛程式時，Claude Code 會將外掛程式目錄複製到快取位置，除非外掛程式就地載入。連結模式中的 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode) 會就地載入，從本機目錄新增的市集中的 [相對路徑來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths) 也會就地載入。複製的外掛程式無法使用 `../shared-utils` 之類的路徑參考其目錄外的檔案，因為這些檔案不會被複製。如果您需要在外掛程式之間共用檔案，請使用符號連結。如需詳細資訊，請參閱 [外掛程式快取和檔案解析](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)。

## 建立 marketplace 檔案

在您的儲存庫根目錄中建立 `.claude-plugin/marketplace.json`。此檔案定義您的 marketplace 名稱、擁有者資訊以及包含其來源的 plugin 清單。 每個 plugin 項目至少需要 `name` 和 `source`（告訴 Claude Code 從何處取得）。有關所有可用欄位，請參閱下面的[完整架構](https://code.claude.com/docs/zh-TW/plugin-marketplaces#marketplace-schema)。

```
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@example.com"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "在保存時自動格式化程式碼",
      "version": "2.1.0",
      "author": {
        "name": "DevTools Team"
      }
    },
    {
      "name": "deployment-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin"
      },
      "description": "部署自動化工具"
    }
  ]
}

```

## Marketplace 架構

### 必需欄位

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 類型   | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                        | 範例                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | string | Marketplace 識別碼（kebab-case，無空格、控制字元或雙向格式化字元）。這是公開的：使用者在安裝 plugin 時會看到它（例如，`/plugin install my-tool@your-marketplace`）。每個使用者只能為每個名稱註冊一個 marketplace：新增第二個同名 marketplace 會取代第一個。若要在一個 marketplace 名稱下發佈多個 plugin，請在[單一 `marketplace.json`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#create-the-marketplace-file) 中列出它們全部。 | `"acme-tools"`                                                                              |
| `owner`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | object | Marketplace 維護者資訊。請參閱 [Owner 欄位](https://code.claude.com/docs/zh-TW/plugin-marketplaces#owner-fields)                                                                                                                                                                                                                                                                                                                            |                                                                                             |
| `plugins`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | array  | 可用 plugin 的清單                                                                                                                                                                                                                                                                                                                                                                                                                          | 請參閱 [Plugin 項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-entries) |
| **保留名稱** ：以下 marketplace 名稱保留供 Anthropic 官方使用，第三方 marketplace 無法使用：`claude-code-marketplace`、`claude-code-plugins`、`claude-plugins-official`、`claude-plugins-community`、`claude-community`、`anthropic-marketplace`、`anthropic-plugins`、`agent-skills`、`anthropic-agent-skills`、`knowledge-work-plugins`、`life-sciences`、`claude-for-legal`、`claude-for-financial-services`、`financial-services-plugins`、`first-party-plugins`、`claude-tag-plugins`、`healthcare`。模仿官方 marketplace 的名稱（如 `official-claude-plugins` 或 `anthropic-plugins-v2`）也被阻止。保留這些名稱可防止第三方 marketplace 將自己冒充為 Anthropic 發佈的來源。Claude Code 每次載入 marketplace 時都會重新檢查保留名稱，而不僅在您新增 marketplace 時檢查。在名稱成為保留名稱之前以其中一個名稱註冊的 marketplace 會停止載入，並報告它是[從不受信任的來源註冊](https://code.claude.com/docs/zh-TW/errors#marketplace-is-registered-from-an-untrusted-source)。移除該 marketplace，並從官方 Anthropic 來源重新新增它。受新保留名稱影響的第三方 marketplace 在您以不同名稱重新新增它後立即再次載入。在 v2.1.205 之前，`first-party-plugins` 和 `healthcare` 未被保留，已在保留名稱下註冊的 marketplace 繼續載入。在 v2.1.265 之前，`claude-tag-plugins` 未被保留。您也無法將 marketplace 命名為 `npm`、`pip`、`uv`、`cargo`、`github` 或 `gh`（任何大小寫）。此檢查需要 Claude Code v2.1.275 或更新版本。 |        |                                                                                                                                                                                                                                                                                                                                                                                                                                             |                                                                                             |

### Owner 欄位

| 欄位    | 類型   | 必需 | 描述                            |
| ------- | ------ | ---- | ------------------------------- |
| `name`  | string | 是   | 維護者或團隊的名稱              |
| `email` | string | 否   | 維護者的聯絡電子郵件            |
| `url`   | string | 否   | 網站、GitHub 個人檔案或組織 URL |

### 選用欄位

| 欄位                                                                    | 類型   | 描述                                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$schema`                                                               | string | JSON Schema URL，用於編輯器自動完成和驗證。Claude Code 在載入時會忽略此欄位。                                                                                                                                                                                                                                  |
| `description`                                                           | string | 簡短的 marketplace 描述                                                                                                                                                                                                                                                                                        |
| `version`                                                               | string | Marketplace 版本                                                                                                                                                                                                                                                                                               |
| `metadata.pluginRoot`                                                   | string | Claude Code 解析裸 plugin 來源名稱的目錄。請參閱[相對路徑](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths)。需要 Claude Code v2.1.239 或更新版本。                                                                                                                                      |
| `allowCrossMarketplaceDependenciesOn`                                   | array  | 此 marketplace 中的 plugin 可能依賴的其他 marketplace。來自此處未列出的 marketplace 的相依性在安裝時被阻止。請參閱[依賴來自另一個 marketplace 的 plugin](https://code.claude.com/docs/zh-TW/plugin-dependencies#depend-on-a-plugin-from-another-marketplace)。                                                 |
| `renames`                                                               | object | 從前一個 plugin `name` 對應到其目前名稱，或對應到 `null`（如果 plugin 已移除）的對應。當您重新命名或移除 `plugins` 中的項目時，可讓現有使用者自動遷移。請參閱[重新命名或移除 plugin](https://code.claude.com/docs/zh-TW/plugin-marketplaces#rename-or-remove-a-plugin)。需要 Claude Code v2.1.193 或更新版本。 |
| `description` 和 `version` 也可在 `metadata` 下接受，以保持向後相容性。 |        |                                                                                                                                                                                                                                                                                                                |

## Plugin 項目

`plugins` 陣列中的每個 plugin 項目都描述了一個 plugin 及其位置。您可以包含來自 [plugin manifest schema](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-manifest-schema) 的任何欄位，例如 `description`、`version`、`author`、`commands` 和 `hooks`，加上這些 marketplace 特定欄位：`source`、`category`、`tags`、`strict`、`relevance`、`headers` 和 `headersHelper`。

### 必需欄位

| 欄位     | 類型   | 說明                                                                                                                                                           |
| -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`   | string | Plugin 識別碼，採用 kebab-case 格式，不含空格、控制字元或雙向格式化字元。這是公開的：使用者在安裝時會看到它（例如，`/plugin install my-plugin@marketplace`）。 |
| `source` | string | object                                                                                                                                                         |

### 選用 plugin 欄位

**標準中繼資料欄位：**

| 欄位                                                                                                                                                                                    | 類型    | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `displayName`                                                                                                                                                                           | string  | 在 UI 介面中顯示的人類可讀名稱。當項目和 plugin 的 `plugin.json` 都未設定時，使用者會看到 plugin 的 `name`。可以包含空格和任何大小寫。不用於命名空間或查詢。                                                                                                                                                                                                                                                                                                                                                                                                |
| `description`                                                                                                                                                                           | string  | 簡短的 plugin 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `version`                                                                                                                                                                               | string  | Plugin 版本。如果設定（在此處或在 `plugin.json` 中），plugin 會固定到此字串，使用者只有在版本變更時才會收到更新。具有 [`command` source](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources) 的 plugin 不會由任一欄位固定。從 marketplace 新增為本機目錄且 [loaded in place](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution) 的 plugin 也不會。如果在兩個位置都未設定，版本來自 [version management](https://code.claude.com/docs/zh-TW/plugins-reference#version-management) 中的下一個來源。 |
| `author`                                                                                                                                                                                | object  | Plugin 作者資訊（`name` 必需；`email` 和 `url` 選用）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `homepage`                                                                                                                                                                              | string  | Plugin 首頁或文件 URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `repository`                                                                                                                                                                            | string  | 原始碼儲存庫 URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `license`                                                                                                                                                                               | string  | SPDX 授權識別碼（例如，MIT、Apache-2.0）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `keywords`                                                                                                                                                                              | array   | 用於 plugin 探索和分類的標籤                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `metadata`                                                                                                                                                                              | object  | 自由格式物件，用於您自己的欄位，例如權利或目錄資料。Claude Code 不會讀取它。在 v2.1.222 之前，`claude plugin validate` 會將該鍵報告為無法識別的欄位。                                                                                                                                                                                                                                                                                                                                                                                                       |
| `category`                                                                                                                                                                              | string  | 用於組織的 plugin 類別                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `tags`                                                                                                                                                                                  | array   | 用於搜尋的標籤                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `strict`                                                                                                                                                                                | boolean | 控制 `plugin.json` 是否為元件定義的權威（預設值：true）。請參閱下方的 [Strict mode](https://code.claude.com/docs/zh-TW/plugin-marketplaces#strict-mode)。                                                                                                                                                                                                                                                                                                                                                                                                   |
| `relevance`                                                                                                                                                                             | object  | 告訴 Claude Code 何時向使用者建議此 plugin 的訊號。僅對管理員在受管設定中允許列表的 marketplace 生效。請參閱 [Recommend plugins for your org](https://code.claude.com/docs/zh-TW/plugin-relevance)。                                                                                                                                                                                                                                                                                                                                                        |
| `defaultEnabled`                                                                                                                                                                        | boolean | 安裝後 plugin 是否啟用（預設值：true）。設定為 `false` 以安裝已停用的 plugin，直到使用者選擇加入。優先於 plugin 的 `plugin.json` 中的相同欄位。請參閱 [Default enablement](https://code.claude.com/docs/zh-TW/plugins-reference#default-enablement)。                                                                                                                                                                                                                                                                                                       |
| 項目和 plugin 自己的 `plugin.json` 都可以設定顯示欄位 `displayName`、`description`、`author`、`homepage`、`repository`、`license` 和 `keywords`。在 plugin 清單和詳細資訊中，安裝前後： |         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

- 對於您在項目上設定的欄位，使用者會看到項目的值，即使 `plugin.json` 設定了不同的值。
- 對於項目未設定的欄位，使用者會看到 `plugin.json` 值。

安裝前，Claude Code 只能為具有 [relative-path source](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths) 的項目讀取 `plugin.json`，其 plugin 檔案位於 marketplace 內部。對於具有任何其他來源類型的項目，使用者在安裝 plugin 之前只會看到項目自己的欄位。 **元件設定欄位：**

| 欄位                                                                                                                                                   | 類型   | 說明                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `skills`                                                                                                                                               | string | array                                                                                                                                                                                                                                                                                                                                                    |
| `commands`                                                                                                                                             | string | array                                                                                                                                                                                                                                                                                                                                                    |
| `agents`                                                                                                                                               | string | array                                                                                                                                                                                                                                                                                                                                                    |
| `hooks`                                                                                                                                                | string | object                                                                                                                                                                                                                                                                                                                                                   |
| `mcpServers`                                                                                                                                           | string | object                                                                                                                                                                                                                                                                                                                                                   |
| `lspServers`                                                                                                                                           | string | object                                                                                                                                                                                                                                                                                                                                                   |
| **封存驗證欄位：** 當項目在需要認證的伺服器上具有 [`archive` source](https://code.claude.com/docs/zh-TW/plugin-marketplaces#zip-archives) 時設定這些。 |        |                                                                                                                                                                                                                                                                                                                                                          |
| 欄位                                                                                                                                                   | 類型   | 說明                                                                                                                                                                                                                                                                                                                                                     |
| ---                                                                                                                                                    | ---    | ---                                                                                                                                                                                                                                                                                                                                                      |
| `headers`                                                                                                                                              | object | Claude Code 在下載此項目的封存時傳送的 HTTP 標頭。覆寫 marketplace 的相同名稱的標頭。需要 Claude Code v2.1.238 或更新版本。                                                                                                                                                                                                                              |
| `headersHelper`                                                                                                                                        | string | 命令，將此項目的封存下載的 HTTP 標頭列印為一個 JSON 物件，用於過期的認證。請參閱 [Authenticate archive downloads](https://code.claude.com/docs/zh-TW/plugin-marketplaces#authenticate-archive-downloads)。項目還必須設定 [`"strict": false`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#strict-mode)。需要 Claude Code v2.1.238 或更新版本。 |

## Plugin 來源

Plugin 來源告訴 Claude Code 在您的 marketplace 中列出的每個個別 plugin 從何處取得。這些在 `marketplace.json` 中每個 plugin 項目的 `source` 欄位中設定。 Claude Code 將每個已安裝的 plugin 複製到本機版本化 plugin 快取中，位於 `~/.claude/plugins/cache`，除非 plugin 就地載入。[連結模式中的 `command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode)就地載入，[相對路徑來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths)從本機目錄新增的 marketplace 也是如此。Claude Code 也會[將 plugin 的合格 Node.js 套件相依性安裝](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)到快取副本中。請參閱[Plugin 快取和檔案解析](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)以了解從本機目錄 marketplace 就地載入的 plugin 如何取得您的編輯。

| 來源                                                                | 類型                             | 欄位                               | 備註                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------- | -------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 相對路徑                                                            | `string`（例如 `"./my-plugin"`） | 無                                 | marketplace 儲存庫內的本機目錄。必須以 `./` 開頭，除非您在 [`metadata.pluginRoot`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths) 下寫入裸名稱。Claude Code 相對於 marketplace 根目錄解析路徑，而不是 `.claude-plugin/` 目錄 |
| `github`                                                            | object                           | `repo`、`ref?`、`sha?`             |                                                                                                                                                                                                                                                      |
| `url`                                                               | object                           | `url`、`ref?`、`sha?`              | Git URL 來源                                                                                                                                                                                                                                         |
| `git-subdir`                                                        | object                           | `url`、`path`、`ref?`、`sha?`      | git 儲存庫內的子目錄。稀疏複製以最小化大型 monorepo 的頻寬                                                                                                                                                                                           |
| `npm`                                                               | object                           | `package`、`version?`、`registry?` | npm 套件，使用您的 npm 用戶端取得並解包，不執行安裝指令碼                                                                                                                                                                                            |
| `archive`                                                           | object                           | `url`、`sha256?`                   | 透過 HTTPS 下載的 Zip 封存。在使用者的機器上無需 git 或 npm 即可運作。需要 Claude Code v2.1.224 或更新版本                                                                                                                                           |
| `command`                                                           | object                           | `command`、`timeout?`、`mode?`     | 透過執行本機命令產生的 plugin 目錄，每個工作階段重新執行一次以取得變更。需要 Claude Code v2.1.229 或更新版本                                                                                                                                         |
| **Marketplace 來源與 plugin 來源** ：這些是控制不同事物的不同概念。 |                                  |                                    |                                                                                                                                                                                                                                                      |

- **Marketplace 來源** ：從何處取得 `marketplace.json` 目錄本身。在使用者執行 `/plugin marketplace add` 或在 `extraKnownMarketplaces` 設定中設定。基於 Git 的 marketplace 來源支援 `ref`（分支/標籤）但不支援 `sha`。
- **Plugin 來源** ：從何處取得 marketplace 中列出的個別 plugin。在 `marketplace.json` 內每個 plugin 項目的 `source` 欄位中設定。基於 Git 的 plugin 來源同時支援 `ref`（分支/標籤）和 `sha`（確切提交）。

例如，託管在 `acme-corp/plugin-catalog`（marketplace 來源）的 marketplace 可以列出從 `acme-corp/code-formatter`（plugin 來源）取得的 plugin。marketplace 來源和 plugin 來源指向不同的儲存庫，並獨立固定。 下面的基於 git 的來源類型為 `github`、`url` 和 `git-subdir`。當任何一個上同時設定 `ref` 和 `sha` 時，`sha` 是有效的固定。Claude Code 直接取得並簽出固定的提交。 在大多數 git 主機上，包括 GitHub、GitLab 和 Bitbucket，這表示即使上游的 `ref` 命名的分支或標籤已被刪除，只要提交仍可從儲存庫到達，安裝就會成功。某些伺服器（例如 AWS CodeCommit）不支援透過 SHA 取得提交。在這些伺服器上，`ref` 仍必須存在，且固定的提交必須可從其到達。 如果您透過**組織設定 > Plugins** 分發 plugin，只允許某些來源類型。請參閱[透過組織設定分發](https://code.claude.com/docs/zh-TW/plugin-marketplaces#distribute-through-organization-settings)。

### 相對路徑

對於同一儲存庫中的 plugin，使用以 `./` 開頭的路徑：

```
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin"
}

```

路徑相對於 marketplace 根目錄解析，即包含 `.claude-plugin/` 的目錄。來源 `./plugins/my-plugin` 因此指向 `<repo>/plugins/my-plugin`，即使 `marketplace.json` 位於 `<repo>/.claude-plugin/marketplace.json`。不要使用 `../` 參考 marketplace 根目錄外的路徑。在 macOS 和 Linux 上，Claude Code 拒絕在前導 `./` 之後任何地方有反斜線的項目路徑，因此在每個平台上將分隔符寫為 `/`。 裸名稱是沒有 `/` 的單一目錄名稱，例如 `"formatter"`。若要寫入裸名稱而不是 `./` 路徑，請將 [`metadata.pluginRoot`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#optional-fields) 設定為它們解析的目錄。使用 `"pluginRoot": "./plugins"`，Claude Code 將 `"source": "formatter"` 解析為 `./plugins/formatter`。需要 Claude Code v2.1.239 或更新版本。 `metadata.pluginRoot` 本身必須是 marketplace 內的相對路徑。Claude Code 會忽略已以 `./` 開頭的來源。包含 `/` 的來源（例如 `team-a/formatter`）不是裸名稱，即使設定了 `metadata.pluginRoot`，仍需要 `./` 前綴。 Claude Code 相對於 marketplace 的本機副本解析相對路徑，因此當使用者從 git 來源或本機目錄新增您的 marketplace 時可以運作。如果使用者透過直接 URL 新增您的 marketplace 到 `marketplace.json` 檔案，相對路徑將無法解析，因為 Claude Code 只會下載該檔案。對於基於 URL 的分發，請改用任何其他 [plugin 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-sources)。請參閱[疑難排解](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugins-with-relative-paths-fail-in-url-based-marketplaces)以了解詳細資訊。

### GitHub 儲存庫

```
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo"
  }
}

```

您可以固定到特定分支、標籤或提交：

```
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}

```

| 欄位   | 類型   | 描述                                               |
| ------ | ------ | -------------------------------------------------- |
| `repo` | string | 必需。`owner/repo` 格式的 GitHub 儲存庫            |
| `ref`  | string | 選用。Git 分支或標籤（預設為儲存庫預設分支）       |
| `sha`  | string | 選用。完整的 40 字元 git 提交 SHA 以固定到確切版本 |

### Git 儲存庫

```
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git"
  }
}

```

您可以固定到特定分支、標籤或提交：

```
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git",
    "ref": "main",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}

```

| 欄位  | 類型   | 描述                                                                                                                                 |
| ----- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `url` | string | 必需。完整的 git 儲存庫 URL（`https://` 或 `git@`）。`.git` 後綴是選用的，因此 Azure DevOps 和 AWS CodeCommit URL 不含後綴也可以運作 |
| `ref` | string | 選用。Git 分支或標籤（預設為儲存庫預設分支）                                                                                         |
| `sha` | string | 選用。完整的 40 字元 git 提交 SHA 以固定到確切版本                                                                                   |

### Git 子目錄

使用 `git-subdir` 指向位於 git 儲存庫子目錄內的 plugin。Claude Code 使用稀疏、部分複製來僅取得子目錄，最小化大型 monorepo 的頻寬。

```
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/acme-corp/monorepo.git",
    "path": "tools/claude-plugin"
  }
}

```

您可以固定到特定分支、標籤或提交：

```
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/acme-corp/monorepo.git",
    "path": "tools/claude-plugin",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}

```

`url` 欄位也接受 GitHub 簡寫（`owner/repo`）或 SSH URL（`git@github.com:owner/repo.git`）。

| 欄位   | 類型   | 描述                                                                    |
| ------ | ------ | ----------------------------------------------------------------------- |
| `url`  | string | 必需。Git 儲存庫 URL、GitHub `owner/repo` 簡寫或 SSH URL                |
| `path` | string | 必需。儲存庫內包含 plugin 的子目錄路徑（例如，`"tools/claude-plugin"`） |
| `ref`  | string | 選用。Git 分支或標籤（預設為儲存庫預設分支）                            |
| `sha`  | string | 選用。完整的 40 字元 git 提交 SHA 以固定到確切版本                      |

### npm 套件

npm 來源可以命名公開 npm 登錄表或您的團隊託管的私人登錄表上的任何套件。Claude Code 使用您的 npm 用戶端解析套件、下載 tarball 並將其解包到 plugin 快取中。 套件的安裝指令碼（例如 `preinstall` 或 `postinstall`）永遠不會執行，其相依性在取得期間不會安裝。 如果套件在其 `package.json` 旁邊提供支援的 lockfile，Claude Code 會在單獨的步驟中安裝那些[Node.js 套件相依性](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)，也會停用指令碼。否則，發佈已建置所需一切的 plugin。需要其他套件的 MCP 伺服器可以透過 `npx` 啟動，它在首次執行時安裝它們。

```
{
  "name": "my-npm-plugin",
  "source": {
    "source": "npm",
    "package": "@acme/claude-plugin"
  }
}

```

若要固定到特定版本，請新增 `version` 欄位：

```
{
  "name": "my-npm-plugin",
  "source": {
    "source": "npm",
    "package": "@acme/claude-plugin",
    "version": "2.1.0"
  }
}

```

若要從私人或內部登錄表安裝，請新增 `registry` 欄位：

```
{
  "name": "my-npm-plugin",
  "source": {
    "source": "npm",
    "package": "@acme/claude-plugin",
    "version": "^2.0.0",
    "registry": "https://npm.example.com"
  }
}

```

| 欄位       | 類型   | 描述                                                                 |
| ---------- | ------ | -------------------------------------------------------------------- |
| `package`  | string | 必需。套件名稱或範圍套件（例如，`@org/plugin`）                      |
| `version`  | string | 選用。版本或版本範圍（例如，`2.1.0`、`^2.0.0`、`~1.5.0`）            |
| `registry` | string | 選用。自訂 npm 登錄表 URL。預設為系統 npm 登錄表（通常為 npmjs.org） |

### Zip 封存

使用 `archive` 將 plugin 分發為 Claude Code 透過 HTTPS 下載的 zip 檔案，因此安裝在使用者的機器上無需 git 或 npm 即可運作。在任何靜態檔案伺服器或成品儲存庫上託管該檔案，例如 S3 儲存桶、Artifactory 通用儲存庫或 nginx。需要 Claude Code v2.1.224 或更新版本。在 v2.1.120 到 v2.1.223 版本上，安裝 plugin 失敗，並顯示 `This plugin uses a source type your Claude Code version does not support. Update Claude Code and try again.`；在較舊版本上，包含 `archive` 項目的 marketplace 完全無法載入。 此項目從成品伺服器上的 zip 檔案安裝 plugin：

```
{
  "name": "my-plugin",
  "source": {
    "source": "archive",
    "url": "https://artifacts.example.com/claude-plugins/my-plugin-2.1.0.zip"
  }
}

```

當您建立 zip 時，您可以直接壓縮 plugin 的內容或壓縮 plugin 資料夾本身。Claude Code 在封存的頂部查找 `.claude-plugin/`，然後在單一頂層資料夾內查找，因此兩種配置都會安裝：

```
my-plugin.zip          my-plugin.zip
├── .claude-plugin/    └── my-plugin/
│   └── plugin.json        ├── .claude-plugin/
└── commands/              │   └── plugin.json
                           └── commands/

```

Claude Code 不會查找超過一個資料夾，因此嵌套更深的 plugin 無法安裝。Claude Code 拒絕大於 256 MiB 的封存。 若要固定確切檔案，請新增 `sha256` 欄位，其中包含封存的摘要：

```
{
  "name": "my-plugin",
  "source": {
    "source": "archive",
    "url": "https://artifacts.example.com/claude-plugins/my-plugin-2.1.0.zip",
    "sha256": "6bfa50e3d2e00c052b46abe51fff89346ac803e45771f76dcf6df1ab74cca5e1"
  }
}

```

如果下載的檔案與固定不符，Claude Code 拒絕安裝並報告 [`Plugin archive integrity check failed`](https://code.claude.com/docs/zh-TW/errors#plugin-archive-integrity-check-failed)。 封存來源接受這些欄位：

| 欄位                                                                                                                                                                                                                                                                                              | 類型   | 描述                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `url`                                                                                                                                                                                                                                                                                             | string | 必需。zip 封存的 HTTPS URL。Claude Code 拒絕 `http://` URL，以及迴圈、連結本機和雲端中繼資料主機。每個重新導向躍點都必須滿足相同的規則，否則 Claude Code 拒絕下載 |
| `sha256`                                                                                                                                                                                                                                                                                          | string | 選用。封存的 SHA-256 摘要，為 64 個十六進位字元，大寫或小寫。Claude Code 驗證每次下載並在不符時拒絕安裝                                                           |
| `sha256` 摘要也會在 `plugin.json` 或 marketplace 項目都未宣告版本時作為 plugin 的版本。請參閱[版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)。如果您宣告 `version`，該版本字串是更新信號，因此在變更 zip 及其摘要後，也要提升版本，否則使用者會保留快取副本。 |        |                                                                                                                                                                   |

#### 驗證封存下載

若要驗證封存下載（例如從私人登錄表下載），請設定 Claude Code 隨其發送的 HTTP 標頭。在您註冊 marketplace 的 `url` 來源上設定 `headers`，例如 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 項目。在 Claude Code v2.1.238 或更新版本上，您可以改為在 plugin 的項目上設定它，在 `source` 旁邊。 如果您要放在 `headers` 中的值是短期的，例如您的登錄表應要求時鑄造的權杖，請改為在同一位置設定 `headersHelper` 命令。Claude Code 執行命令並將其列印的 JSON 物件作為該位置的標頭發送。需要 Claude Code v2.1.238 或更新版本。 您選擇的位置決定哪些下載取得標頭以及 Claude Code 何時執行命令：

| 位置                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 取得標頭的下載                                                   | Claude Code 何時執行在該處設定的 `headersHelper`                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Marketplace `url` 來源                                                                                                                                                                                                                                                                                                                                                                                                                               | marketplace URL 來源上的封存下載，意思是相同的配置、主機和連接埠 | 在每次取得 marketplace 的 `marketplace.json` 之前以及在該來源上每次封存下載之前。Claude Code 將一次執行的輸出重複使用最多 60 秒                         |
| Plugin 項目                                                                                                                                                                                                                                                                                                                                                                                                                                          | 該項目的下載只有                                                 | 只有當使用者自行安裝或更新該一個 plugin 並[接受命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-a-headershelper-command)時 |
| 當兩個位置都設定相同名稱的標頭時，Claude Code 發送項目的值。在一個位置內，命令列印的標頭會覆蓋相同名稱的列出標頭。 此項目在 `source` 旁邊設定 `headersHelper`。它也設定 `"strict": false`，Claude Code 要求設定 `headersHelper` 的 `marketplace.json` 項目。使用 [`"strict": false`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#strict-mode)，marketplace 項目是 plugin 的完整定義，因此使用者可以在接受命令之前檢查 plugin 包含的內容： |                                                                  |                                                                                                                                                         |

```
{
  "name": "my-plugin",
  "description": "內部服務的格式化命令",
  "strict": false,
  "commands": "./commands",
  "source": {
    "source": "archive",
    "url": "https://registry.example.com/plugins/my-plugin-2.1.0.zip"
  },
  "headersHelper": "/opt/bin/mint-registry-token.sh"
}

```

若要檢查項目，請執行 `claude plugin install my-plugin@your-marketplace`。Claude Code 向您顯示命令和封存 URL，並在您接受後下載 zip。 在 v2.1.238 之前，Claude Code 下載項目的封存時沒有其 `headers` 或 `headersHelper`，因此依賴它們的安裝失敗，並顯示 `HTTP 401 while downloading plugin archive from`，後面跟著 URL，登錄表的狀態碼代替 401。

#### 寫入 headersHelper 命令

無論您在 marketplace 的 `url` 來源或 plugin 項目上設定 `headersHelper`，請寫入命令以滿足這些要求：

- **命令文字** ：最多 500 個可列印 ASCII 字元，沒有四個或更多空格的執行。
- **輸出** ：在 stdout 上列印一個標頭名稱和字串值的 JSON 物件，然後在 10 秒內以代碼 0 結束。
- **Shell 和工作目錄** ：Claude Code 透過 `sh` 或 Windows 上的 `cmd.exe` 從設定目錄 `~/.claude` 或 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/zh-TW/env-vars#variables) 執行命令。給出絕對路徑或 `PATH` 上的命令，因為相對路徑相對於該目錄解析，而不是使用者的專案。
- **Claude Code 移除的變數** ：從 `marketplace.json` 項目或專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中設定的命令環境中，Claude Code 移除每個名稱包含 `TOKEN`、`SECRET`、`KEY` 或 `AUTH` 等字詞的變數，包括 `ANTHROPIC_API_KEY`。Claude Code 不會將此移除應用於在使用者設定、`--settings` 檔案或受管設定中設定的命令。
- **Claude Code 設定的變數** ：`CLAUDE_CODE_MARKETPLACE_URL` 和 `CLAUDE_CODE_MARKETPLACE_NAME` 用於 `url` 來源的命令，以及 `CLAUDE_CODE_PLUGIN_NAME` 和 `CLAUDE_CODE_PLUGIN_ARCHIVE_URL` 用於項目的命令。`CLAUDE_CODE_MARKETPLACE_NAME` 在使用者透過 URL 新增 marketplace 後的第一次取得時未設定，因為該取得是提供名稱的內容。

鑄造持有人權杖的命令列印如下物件：

```
{"Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9"}

```

#### Claude Code 何時跳過 headersHelper 命令或捨棄其輸出

Claude Code 不執行 `headersHelper` 命令，或在這些情況下捨棄來自 `headers` 或命令輸出的標頭：

- **命令失敗** ：如果命令以非零代碼結束、執行超過 10 秒或列印除字串值的 JSON 物件以外的任何內容，Claude Code 不會進行它執行命令的取得或下載。
- **Marketplace URL 不以`https://` 開頭**：Claude Code 不執行該 `url` 來源的命令，只發送其 `headers` 欄位中列出的標頭。
- **重新導向離開來源** ：當下載從封存 URL 的來源重新導向時，Claude Code 捨棄 marketplace `url` 來源和 plugin 項目的 `headers` 值和命令輸出。
- **項目設定路由或身分標頭** ：Claude Code 從項目的 `headers` 和命令輸出中捨棄請求路由和用戶端身分名稱（例如 `Host`、`Cookie` 和 `X-Forwarded-*`），並保留驗證名稱（例如 `Authorization`）。Claude Code 以這種方式篩選每個 `marketplace.json` 項目，以及[內嵌設定項目](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)取決於哪個檔案宣告它。
- **在`--add-dir` 目錄的設定中設定的命令**：Claude Code 忽略它，在 `url` 來源和[內嵌 plugin 項目](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)上都一樣，只發送該檔案的 `headers`。
- **受管設定阻止命令** ：將 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources) 設定為 `true` 會阻止 `headersHelper` 命令，[`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly) 也會阻止它們，除非 `disableCommandPluginSources` 明確為 `false`。在任一阻止下，Claude Code 仍會為受管設定本身宣告的 marketplace 執行命令。

#### 使用者如何接受 headersHelper 命令

使用者每次從 plugin 的自己的檢視在 `/plugin` 或使用 `claude plugin install` 或 `claude plugin update` 自行安裝或更新該一個 plugin 時接受 plugin 項目的命令。Claude Code 顯示命令和封存 URL，並僅在使用者接受後執行命令。 在非互動式 shell 中，傳遞 [`--yes`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-install) 以接受命令。若要接受只有先前 `--json` 執行顯示的命令，傳遞 [`--accept-command`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-install) 與執行報告的 `sha256`。 Claude Code 只執行它顯示的命令，用於它顯示的封存 URL。如果項目的命令或封存 URL 在中間變更，Claude Code 拒絕安裝或更新。查詢字串中的變更單獨不計算。 在任何其他操作上，而不是單一 plugin 安裝或更新，Claude Code 既不執行項目的命令也不下載其封存，因此 plugin 保持在其已安裝版本或保持未安裝。使用者看到的內容取決於操作：

- **一次安裝多個 plugin、從 plugin 建議或作為另一個 plugin 的相依性** ：Claude Code 拒絕具有命令的 plugin 並將使用者指向該 plugin 在 `/plugin` 中的自己的檢視。批量安裝中的其他 plugin 仍會安裝。依賴被拒絕 plugin 的 plugin 無法安裝，直到使用者自行安裝被拒絕的 plugin。
- **背景自動更新，或工作階段開始用於其封存從未下載的 plugin** ：Claude Code 在 `/plugin` 錯誤標籤中列出 plugin，以便使用者知道手動安裝或更新它。找到項目的自動更新仍會宣傳已安裝版本列出任何內容。

Marketplace `url` 來源的 `headersHelper` 在設定檔案中宣告，例如 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 項目，而不是在 marketplace 發佈的目錄中，因此 Claude Code 不會在每次安裝或更新時詢問使用者接受它。宣告它的設定檔案決定 Claude Code 何時執行它：

| 設定檔案                                                                                                                                                                                                                                                                                                                                                                                                             | Claude Code 何時執行命令                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 使用者設定、`--settings` 檔案或機器上的受管設定檔案                                                                                                                                                                                                                                                                                                                                                                  | 無需詢問，包括在背景 marketplace 重新整理期間                                                                                                                                                    |
| 專案的 `.claude/settings.json` 或 `.claude/settings.local.json`                                                                                                                                                                                                                                                                                                                                                      | 只有在使用者接受該資料夾本身的[工作區信任對話](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)後。`-p` 或 SDK 工作階段不計算為接受它，父資料夾的信任也不計算 |
| 伺服器受管設定                                                                                                                                                                                                                                                                                                                                                                                                       | 只有在使用者在[安全核准對話](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)中核准傳遞的設定後                                                             |
| 在 `-p` 或 SDK 工作階段中，Claude Code 無法顯示安全核准對話。它應用其他傳遞的設定，但 marketplace 取得以及任何需要命令的封存下載失敗，直到使用者在互動式工作階段中核准。 對於這些檔案之一中的[內嵌 plugin 項目](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)，Claude Code 要求與該檔案中 marketplace 層級命令相同的資料夾信任或設定核准，使用者也在每次安裝或更新時接受項目的命令。 |                                                                                                                                                                                                  |

### Command 來源

當本機安裝的工具產生 plugin 目錄時使用 `command`，例如為目前選定的工具鏈呈現其 plugin 的 IDE。Claude Code 在使用者安裝 plugin 時執行命令，並在背景中每個工作階段重新執行一次，因此您的使用者無需重新安裝即可取得工具的變更輸出。需要 Claude Code v2.1.229 或更新版本。在 v2.1.120 到 v2.1.228 上，安裝 plugin 失敗，並顯示 `This plugin uses a source type your Claude Code version does not support. Update Claude Code and try again.`，在較舊版本上整個 marketplace 無法載入。 此項目從工具列印的任何目錄安裝 plugin：

```
{
  "name": "my-plugin",
  "source": {
    "source": "command",
    "command": "my-tool claude-plugin-path"
  }
}

```

Claude Code 透過平台 shell（macOS 和 Linux 上的 `sh` 或 Windows 上的 `cmd.exe`）從使用者的主目錄執行命令。命令必須在 stdout 上列印恰好一行並以代碼 0 結束。該行是包含完整 plugin 的目錄的絕對路徑，命令結束時，路徑可能在執行之間變更。 Claude Code 停止執行時間超過 `timeout` 秒的命令，安裝或更新失敗。Claude Code 也在這些情況下拒絕列印的路徑，安裝或更新以相同方式失敗：

- 目錄在其頂層沒有 plugin 內容，例如 `.claude-plugin/` 目錄或 `skills/`、`commands/`、`agents/` 或 `hooks/` 目錄
- 目錄是 Claude Code 啟動的目錄，或其父目錄之一
- 在 Windows 上，路徑是 UNC 路徑

Command 來源接受這些欄位：

| 欄位      | 類型   | 描述                                                                                                                                                                                            |
| --------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `command` | string | 必需。Shell 命令，在 stdout 上列印 plugin 目錄的絕對路徑作為單一行並結束 0。必須是可列印 ASCII，最多 500 個字元，沒有四個或更多空格的執行，以便使用者可以檢查他們被要求接受的整個命令           |
| `timeout` | number | 選用。放棄前等待命令的整數秒數（預設：60，最大：600）                                                                                                                                           |
| `mode`    | string | 選用。`"copy"`（預設）將列印的目錄複製到 plugin 快取中。`"link"` 使用列印的目錄就地。請參閱[複製模式和連結模式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode) |

#### 複製模式和連結模式

使用預設 `"mode": "copy"`，Claude Code 將列印的目錄複製到版本化 plugin 快取中，並從目錄內容的雜湊衍生[plugin 版本](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)。您的工具可以在命令結束後刪除或重寫目錄，產生相同內容的重新執行計為最新。Claude Code 拒絕安裝大於 256 MiB 或包含超過 20,000 項目的目錄。 為大型 plugin 目錄設定 `"mode": "link"`，不應複製，例如呈現的 SDK 匯出。Claude Code 使用連結填充 plugin 的快取項目到列印目錄的每個頂層項目，並就地使用檔案，因此不複製任何內容、不雜湊檔案內容，大小限制不適用。如果頂層項目是指向列印目錄外的符號連結，安裝失敗。Claude Code 也跳過連結模式 plugin 的 [Node.js 套件相依性安裝](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)，因此列印已包含 plugin 需要的任何 `node_modules` 的目錄。 保持列印的目錄就地，只要 plugin 保持安裝。Claude Code 在每次啟動時透過這些連結載入 plugin。Claude Code 從列印目錄的真實路徑及其頂層項目衍生[plugin 版本](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)，而不是檔案內部，因此列印不同的路徑以表示新內容。在列印目錄或其下方啟動的工作階段中，Claude Code 完全不載入 plugin。 Claude Code 不支援 Windows 上的連結模式，拒絕在那裡安裝連結模式 plugin。改為宣告 `"mode": "copy"`。

#### 使用者如何接受命令

Claude Code 在使用者的機器上執行您的命令，因此它將每次執行繫結到使用者的明確接受：

- 當使用者從 `/plugin` 中的其詳細資訊畫面安裝 plugin，或在互動式終端中使用 `claude plugin install` 或 `claude plugin update` 安裝或更新它時，Claude Code 首先向他們顯示確切的命令字串，並記錄該安裝的已接受命令。可以在相同命令的已記錄接受上進行的 `claude plugin update` 不顯示任何內容。
- 在非互動式 shell 中，例如佈建指令碼，傳遞 `--yes` 到 `claude plugin install` 或 `claude plugin update` 以接受它列印的命令。若要接受只有先前 `--json` 執行顯示的命令，傳遞 [`--accept-command`](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-install) 與執行報告的 `sha256`。
- 每條其他路徑只執行使用者已接受的命令。這包括從 `/plugin` 啟動的更新以及[Claude Code 何時重新執行命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#when-claude-code-re-runs-the-command)中描述的背景執行。當未接受任何內容時，Claude Code 拒絕執行命令並告訴使用者如何檢查它。Claude Code 從不將 command 來源的 plugin 安裝為另一個 plugin 的相依性，因此使用者自行先安裝它。
- 如果您變更項目的 `command` 或切換其 `mode`，使用者保留他們已有的版本，Claude Code 停止重新執行命令。在互動式工作階段中，`/plugin` 錯誤標籤顯示新命令，直到使用者透過執行 `claude plugin update <plugin>@<marketplace>` 檢查並接受它。

系統管理員可以使用受管設定 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources) 在整個組織中阻止 command 來源。如果組織設定 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly)，Claude Code 預設會阻止 command 來源。

#### Claude Code 何時重新執行命令

列印的目錄反映工具在命令執行時的狀態，因此 Claude Code 在這些時間重新執行命令：

- 每次使用者安裝或更新 plugin
- 每個工作階段一次用於每個啟用的 command 來源 plugin，在背景中，工作階段啟動後不久。此執行不透過 marketplace 自動更新進行，因此不取決於 marketplace 的[自動更新設定](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)
- 在啟動或 `/reload-plugins` 上，當啟用的 plugin 的已安裝版本從 plugin 快取中遺失時

當使用者設定 [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/zh-TW/env-vars) 時，Claude Code 跳過兩個背景執行。明確安裝和更新仍會使用該變數集執行命令。 當命令的雜湊輸出已變更時，Claude Code 將結果安裝為新版本，並在執行中的互動式工作階段中重新載入它，切換 [`/reload-plugins` 切換的相同元件](https://code.claude.com/docs/zh-TW/plugins-reference#environment-variables)。使用者看到 plugin 已重新載入的通知。如果就地重新載入會使工作階段的提示快取失效，Claude Code 改為提示使用者執行 `/reload-plugins`，[警告快取成本並在使用 `--force` 重新執行時應用](https://code.claude.com/docs/zh-TW/prompt-caching#enabling-or-disabling-a-plugin)。

### 進階 plugin 項目

此範例顯示使用許多選用欄位的 plugin 項目，包括 commands、agents、hooks 和 MCP servers 的自訂路徑：

```
{
  "name": "enterprise-tools",
  "source": {
    "source": "github",
    "repo": "company/enterprise-plugin"
  },
  "description": "企業工作流程自動化工具",
  "version": "2.1.0",
  "author": {
    "name": "Enterprise Team",
    "email": "enterprise@example.com"
  },
  "homepage": "https://docs.example.com/plugins/enterprise-tools",
  "repository": "https://github.com/company/enterprise-plugin",
  "license": "MIT",
  "keywords": ["enterprise", "workflow", "automation"],
  "category": "productivity",
  "commands": [
    "./commands/core/",
    "./commands/enterprise/",
    "./commands/experimental/preview.md"
  ],
  "agents": ["./agents/security-reviewer.md", "./agents/compliance-checker.md"],
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
          }
        ]
      }
    ]
  },
  "mcpServers": {
    "enterprise-db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  },
  "strict": false
}

```

需要注意的關鍵事項：

- **`commands`和`agents`** ：您可以指定多個目錄或個別檔案。路徑相對於 plugin 根目錄，必須保持在其內部。
  - Claude Code 拒絕解析在 plugin 目錄外的路徑，例如 `./../shared.md`，並顯示 [`path escapes plugin directory`](https://code.claude.com/docs/zh-TW/errors#path-escapes-plugin-directory) 錯誤，仍會載入 plugin 而不包含該元件
- **`${CLAUDE_PLUGIN_ROOT}`**：在 hook 命令和 MCP 伺服器配置中使用此變數來參考 plugin 安裝目錄內的檔案。
  - 請參閱[替換表](https://code.claude.com/docs/zh-TW/plugins-reference#environment-variables)以了解每個伺服器類型的哪些配置欄位會替換它
  - 對於應在 plugin 更新後保留的相依性或狀態，請改用 [`${CLAUDE_PLUGIN_DATA}`](https://code.claude.com/docs/zh-TW/plugins-reference#persistent-data-directory)
- **`strict: false`**：由於此設定為 false，plugin 不需要自己的`plugin.json` 。marketplace 項目定義所有內容。請參閱下面的 [Strict mode](https://code.claude.com/docs/zh-TW/plugin-marketplaces#strict-mode)。

根據預設，plugin 的 skills 從其 `source` 下的 `skills/` 目錄載入。`skills` 欄位中列出的路徑會新增到該掃描中：

```
"skills": ["./skills/", "./extra-skills/"]

```

當多個 plugin 項目在 marketplace 根目錄（`source: "./"`) 共享一個 `skills/` 資料夾時，改為列出特定子目錄，以便每個項目只載入自己的 skills：

```
"source": "./",
"skills": ["./skills/code-review", "./skills/docs"]

```

使用 marketplace 根目錄 `source` 時，列出的路徑是該項目的完整集合，共享 `skills/` 資料夾中的其他目錄不會載入。列出 `./skills/` 本身或 plugin 根目錄會保持完整掃描。如果列出的路徑都不存在，則改為執行預設掃描。

### Strict mode

`strict` 欄位控制 `plugin.json` 是否為元件定義（skills、agents、hooks、MCP servers、輸出樣式）的權威。

| 值                     | 行為                                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| `true`（預設）         | `plugin.json` 是權威。marketplace 項目可以用額外的元件補充它，兩個來源都會合併。                    |
| `false`                | marketplace 項目是完整定義。如果 plugin 也有宣告元件的 `plugin.json`，那就是衝突，plugin 無法載入。 |
| **何時使用每種模式：** |                                                                                                     |

- **`strict: true`**：plugin 有自己的`plugin.json` 並管理自己的元件。marketplace 項目可以在頂部新增額外的 skills 或 hooks。這是預設值，適用於大多數 plugin。
- **`strict: false`**：marketplace 運營商想要完全控制。plugin 儲存庫提供原始檔案，marketplace 項目定義這些檔案中的哪些被公開為 skills、agents、hooks 等。當 marketplace 以不同於 plugin 作者預期的方式重組或策劃 plugin 的元件時很有用。

## 託管並分發 marketplace

當使用者新增託管在 git 儲存庫中的 marketplace，或安裝其列出的 git 型 plugin 時，Claude Code 會將該 marketplace 或 plugin 儲存庫複製到他們的機器上。複製永遠不會下載 [Git LFS](https://git-lfs.com) 內容，因此 LFS 追蹤的檔案會以指標檔案的形式到達。將您的 plugin 需要的檔案保留在 LFS 之外。

### 在 GitHub 上託管（推薦）

GitHub 是託管和分發 marketplace 的推薦方式：

1. **建立儲存庫** ：為您的 marketplace 設定新儲存庫
1. **新增 marketplace 檔案** ：使用您的 plugin 定義建立 `.claude-plugin/marketplace.json`
1. **與團隊分享** ：使用者使用 `/plugin marketplace add owner/repo` 新增您的 marketplace

**優點** ：內建版本控制、問題追蹤和團隊協作功能。

### 在其他 git 服務上託管

任何 git 託管服務都可以使用，例如 GitLab、Bitbucket 和自託管伺服器。使用者使用完整儲存庫 URL 新增：

```
/plugin marketplace add https://gitlab.com/company/plugins.git

```

### 私人儲存庫

Claude Code 支援從私人儲存庫安裝 plugin。如果您改為透過[**組織設定 > Plugins**](https://claude.ai/admin-settings/plugins)分發您的 marketplace，您的 git 認證不涉及其中：組織同步透過您組織在 claude.ai 上的 GitHub 或 GitLab 連線讀取 marketplace 儲存庫。請參閱[透過組織設定分發](https://code.claude.com/docs/zh-TW/plugin-marketplaces#distribute-through-organization-settings)以了解哪些 plugin 來源可以是私人的。

#### 您執行的命令

當您執行 `/plugin marketplace add`、`/plugin install`、`/plugin update` 或 `/plugin marketplace update` 時，Claude Code 使用您現有的 git 認證助手，因此 HTTPS 存取透過 `gh auth login`、macOS Keychain 或 `git-credential-store` 的方式與在您的終端中相同。只要主機已在您的 `known_hosts` 檔案中且金鑰已載入 `ssh-agent`，SSH 存取就可以運作，因為 Claude Code 會抑制主機指紋和金鑰密碼的互動式 SSH 提示。GitHub `owner/repo` 簡寫來源預設透過 SSH 複製；設定 [`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`](https://code.claude.com/docs/zh-TW/env-vars#variables) 以改為透過 HTTPS 複製它們。

#### 背景自動更新

根據預設，背景重新整理會停用 git 認證助手，當它檢查 marketplace 的遠端以尋找新提交時，因此檢查無法對私人儲存庫進行 HTTPS 驗證，即使已配置助手。SSH 遠端不受影響：載入在 `ssh-agent` 中的金鑰會以與您執行的命令相同的方式驗證背景檢查。 當檢查找到新提交，或因為無法到達或驗證遠端而失敗時，Claude Code 會重新複製 marketplace 並交換新複製。如果該複製失敗，現有簽出會保留在原位。重新複製確實會使用您儲存的 git 認證，但它可能會在大型儲存庫上[逾時](https://code.claude.com/docs/zh-TW/plugin-marketplaces#git-operations-time-out)，因此私人 marketplace 自動更新可能會間歇性失敗。 兩個設定使私人 marketplace 的行為可預測：

- 設定 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` 以在背景檢查無法到達或驗證遠端時保留現有簽出，而不嘗試重新複製。您的 plugin 會從最後同步的狀態繼續運作，使用 `/plugin marketplace update` 的手動更新仍會使用您的認證進行驗證。
- 配置 git 認證助手，例如使用 `gh auth setup-git` 針對 GitHub，以便重新複製可以在不提示的情況下進行驗證。

在您的環境中設定提供者令牌（例如 `GITHUB_TOKEN`）本身不會啟用背景驗證。令牌只有透過已配置的認證助手（例如 `gh` CLI 的助手，它讀取 `GH_TOKEN` 和 `GITHUB_TOKEN`）才會生效。 若要使背景檢查本身透過 HTTPS 進行驗證，請配置全域 git URL 重寫。重寫會在遠端 URL 中嵌入令牌，因此即使背景檢查停用認證助手，它也會生效。當檢查發現簽出是最新的時，Claude Code 會跳過重新複製。以下範例會重寫 marketplace 儲存庫的 URL 以包含存取令牌：

```
git config --global url."https://x-access-token:YOUR_TOKEN@github.com/acme-corp/plugins".insteadOf "https://github.com/acme-corp/plugins"

```

將重寫範圍限制在 marketplace 儲存庫或組織路徑。其基礎僅為主機的重寫適用於該機器上對該主機的每次 fetch 和 push，並覆蓋您的正常認證，包括推送到您自己的儲存庫。 每個提供者在重寫的 URL 中預期不同的使用者名稱，相同的路徑範圍適用於每個提供者。對於自託管伺服器，請將主機名稱替換為您的伺服器主機名稱：

| 提供者                                                                                                                                                                                                                                                                                                                                                               | 重寫的 URL 形式                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| GitHub                                                                                                                                                                                                                                                                                                                                                               | `https://x-access-token:YOUR_TOKEN@github.com/acme-corp/plugins`  |
| GitLab                                                                                                                                                                                                                                                                                                                                                               | `https://oauth2:YOUR_TOKEN@gitlab.com/acme-corp/plugins`          |
| Bitbucket                                                                                                                                                                                                                                                                                                                                                            | `https://x-token-auth:YOUR_TOKEN@bitbucket.org/acme-corp/plugins` |
| 重寫會以純文字形式將令牌儲存在您的 gitconfig 中，因此請使用具有對 marketplace 儲存庫的唯讀存取權的令牌。                                                                                                                                                                                                                                                             |                                                                   |
| 在 CI/CD 環境中，在從私人儲存庫安裝 plugin 之前配置 git 認證助手。在 GitHub Actions 上，匯出具有對 marketplace 儲存庫的讀取存取權的令牌作為 `GH_TOKEN`，然後執行 `gh auth setup-git`。預設工作流程令牌只能存取工作流程自己的儲存庫，因此另一個儲存庫中的私人 marketplace 需要個人存取令牌或應用程式令牌。如果您在管道中配置全域 URL 重寫，重寫也會直接驗證背景檢查。 |                                                                   |

### 透過組織設定分發

如果您在 Team 或 Enterprise 方案上透過[**組織設定 > Plugins**](https://claude.ai/admin-settings/plugins)分發 plugin，這些來源規則適用：

- 在 github.com 和 gitlab.com 上，marketplace 儲存庫必須是私人或內部的。組織同步透過符合其主機的連線讀取儲存庫：
  - **github.com** ：Claude GitHub App
  - **您的 GitHub Enterprise Server 主機** ：您組織的 [GitHub Enterprise App](https://code.claude.com/docs/zh-TW/github-enterprise-server#admin-setup)
  - **gitlab.com 或您的自託管 GitLab 執行個體** ：您組織的[GitLab 配置](https://code.claude.com/docs/zh-TW/plugin-marketplaces#sync-a-gitlab-hosted-marketplace)中該主機的存取令牌
- 每個 plugin 來源必須是 `github`、`url` 或 `git-subdir` 類型，或以 `./` 開頭的[相對路徑](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths)。如果您在 `metadata.pluginRoot` 下按裸名稱列出 plugin，組織同步會拒絕它作為不支援的來源，因此請寫出路徑，例如 `./plugins/deploy-tools`。
- Plugin 來源可以在三種情況下是私人的：
  - 共享 marketplace 儲存庫擁有者的 github.com 來源
  - 您組織的 GitHub Enterprise 主機上已安裝 GHE App 的來源
  - 與 marketplace 儲存庫位於同一 GitLab 主機上的 `url` 或 `git-subdir` 來源。在 gitlab.com 上，來源也必須位於與 marketplace 儲存庫相同的頂層群組或使用者命名空間下。
- 任何其他 plugin 來源必須是 github.com、gitlab.com 或 bitbucket.org 上的公開儲存庫，組織同步在沒有認證的情況下取得。組織同步拒絕這些規則不涵蓋的主機上的 plugin 來源。

請參閱[為您的組織管理 plugin](https://support.claude.com/en/articles/13837433)以了解管理員工作流程。 若要包含私人 plugin，請將 plugin 資料夾放在 marketplace 儲存庫內，並使用[相對路徑](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths)參考它們。組織同步在分發期間打包每個 plugin，因此使用者永遠不需要存取單獨的來源儲存庫。 例如，此 `marketplace.json` plugin 項目參考您在 marketplace 儲存庫中的 `plugins/deploy-tools` 提交的 plugin：

```
{
  "name": "deploy-tools",
  "source": "./plugins/deploy-tools"
}

```

#### 同步 GitLab 託管的 marketplace

若要從 gitlab.com 或自託管 GitLab 執行個體同步 marketplace，[擁有者](https://code.claude.com/docs/zh-TW/server-managed-settings#access-control)首先在[**組織設定 > Claude Code**](https://claude.ai/admin-settings/claude-code)為該主機新增 GitLab 配置。GitLab 配置處於公開測試版，僅適用於 plugin marketplace 同步。新增一個不會使 GitLab 儲存庫在[網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#limitations) 中可用。請參閱[為您的組織管理 plugin](https://support.claude.com/en/articles/13837433)以了解設定步驟。 當您新增 marketplace 時，輸入專案的 HTTPS URL，例如 `https://gitlab.example.com/platform/claude-plugins`。嵌套子群組中的專案可以運作。組織同步讀取專案的預設分支。如果您開啟**自動同步** ，只有推送到預設分支才會啟動同步。

#### 將可執行檔保留在頂層 bin 目錄之外

不要在您透過組織設定分發的任何 plugin 中包含頂層 `bin/` 目錄。claude.ai 會拒絕具有該目錄的 plugin，無論 plugin 是透過 marketplace 同步還是直接上傳到達：

- **Marketplace 同步** ：組織同步拒絕該 plugin 並同步 marketplace 的其餘部分。錯誤訊息以 `Plugin contains a top-level bin/ directory` 開頭。
- **直接上傳** ：如果您改為在[**組織設定 > Plugins**](https://claude.ai/admin-settings/plugins)中上傳 plugin，claude.ai 會以相同訊息拒絕上傳。

將可執行檔保留在另一個目錄中，例如 `scripts/`，並從您的[skills、hooks 或 MCP 伺服器配置](https://code.claude.com/docs/zh-TW/plugins-reference#environment-variables)中將它們參考為 `${CLAUDE_PLUGIN_ROOT}/scripts/<name>`。

### 為您的團隊要求 marketplace

您可以配置您的儲存庫，以便當團隊成員[信任專案資料夾](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)時，Claude Code 會為他們新增您的 marketplace，無需單獨提示。將您的 marketplace 新增到 `.claude/settings.json`：

```
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  }
}

```

您也可以指定預設應啟用哪些 plugin：

```
{
  "enabledPlugins": {
    "code-formatter@company-tools": true,
    "deployment-tools@company-tools": true
  }
}

```

有關完整的配置選項，請參閱 [Plugin settings](https://code.claude.com/docs/zh-TW/settings-reference#plugin-settings)。 如果您使用具有相對路徑的本機 `directory` 或 `file` 來源，路徑會針對您的儲存庫的主要簽出進行解析。當您從 git worktree 執行 Claude Code 時，路徑仍然指向主要簽出，因此所有 worktrees 共享相同的 marketplace 位置。Marketplace 狀態每個使用者儲存一次在 `~/.claude/plugins/known_marketplaces.json` 中，而不是每個專案。

### 為容器預先填充 plugin

對於容器映像和 CI 環境，您可以在建置時預先填充 plugin 目錄，以便 Claude Code 啟動時已有 marketplace 和 plugin 可用，無需在執行時複製任何內容。設定 `CLAUDE_CODE_PLUGIN_SEED_DIR` 環境變數以指向此目錄。 若要分層多個種子目錄，請在 Unix 上使用 `:` 或在 Windows 上使用 `;` 分隔路徑。Claude Code 按順序搜尋每個目錄，第一個包含給定 marketplace 或 plugin 快取的種子獲勝。 種子目錄鏡像 `~/.claude/plugins` 的結構：

```
$CLAUDE_CODE_PLUGIN_SEED_DIR/
  known_marketplaces.json
  marketplaces/<name>/...
  cache/<marketplace>/<plugin>/<version>/...

```

建立種子目錄的最簡單方法是在映像建置期間執行 Claude Code 一次，安裝您需要的 plugin，然後將產生的 `~/.claude/plugins` 目錄複製到您的映像中，並將 `CLAUDE_CODE_PLUGIN_SEED_DIR` 指向它。 若要跳過複製步驟，在建置期間將 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 設定為您的目標種子路徑，以便 plugin 直接安裝到那裡：

```
CLAUDE_CODE_PLUGIN_CACHE_DIR=/opt/claude-seed claude plugin marketplace add your-org/plugins
CLAUDE_CODE_PLUGIN_CACHE_DIR=/opt/claude-seed claude plugin install my-tool@your-plugins

```

然後在您的容器的執行時環境中設定 `CLAUDE_CODE_PLUGIN_SEED_DIR=/opt/claude-seed`，以便 Claude Code 在啟動時從種子讀取。 在啟動時，Claude Code 將種子的 `known_marketplaces.json` 中找到的 marketplace 註冊到主要配置中，並使用在 `cache/` 下找到的 plugin 快取，而無需重新複製。這在互動模式和使用 `-p` 旗標的非互動模式中都有效。 行為詳細資訊：

- **唯讀** ：Claude Code 永遠不會寫入種子目錄。
- **自動更新已停用** ：種子 marketplace 不會自動更新。
- **種子項目優先** ：種子中宣告的 marketplace 在每次啟動時覆蓋使用者配置中的任何相符項目。若要選擇退出種子 plugin，請使用 `/plugin disable` 而不是移除 marketplace。
- **路徑解析** ：Claude Code 在執行時透過探測 `$CLAUDE_CODE_PLUGIN_SEED_DIR/marketplaces/<name>/` 來定位 marketplace 內容，而不是信任儲存在種子 JSON 內的路徑。這表示即使在與建置位置不同的路徑上掛載，種子也能正確運作。
- **變更被阻止** ：針對種子管理的 marketplace 執行 `/plugin marketplace remove` 或 `/plugin marketplace update` 會失敗，並提示您要求管理員更新種子映像。
- **與設定組合** ：如果 `extraKnownMarketplaces` 或 `enabledPlugins` 宣告已存在於種子中的 marketplace，Claude Code 使用種子副本而不是複製。

### 受管 marketplace 限制

對於需要對 plugin 來源進行嚴格控制的組織，管理員可以使用受管設定中的 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces) 設定限制使用者允許新增的 plugin marketplace。若要也拒絕為單次執行側載 plugin、agent 和 MCP 伺服器的 CLI 旗標，請將其與 [`disableSideloadFlags`](https://code.claude.com/docs/zh-TW/settings-reference#disablesideloadflags) 配對。若要允許清單化哪些 marketplace 的 plugin 可以顯示為內容相關安裝建議，請設定 [`pluginSuggestionMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#pluginsuggestionmarketplaces)。 `strictKnownMarketplaces` 符合 plugin 來自的 marketplace，而不是其內的項目，因此使用者仍然可以從允許的 marketplace 安裝具有[`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)的 plugin。若要也阻止 command 來源，請設定 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources)。 當在受管設定中配置 `strictKnownMarketplaces` 時，限制行為取決於值：

| 值             | 行為                                                                |
| -------------- | ------------------------------------------------------------------- |
| 未定義（預設） | 無限制。使用者可以新增任何 marketplace                              |
| 空陣列 `[]`    | 完全鎖定。阻止每個 marketplace 來源，包括官方 Anthropic marketplace |
| 來源清單       | 允許清單強制執行。使用者只能新增符合項目的 marketplace              |

#### 常見配置

停用所有 marketplace 新增，包括官方 Anthropic marketplace：

```
{
  "strictKnownMarketplaces": []
}

```

Claude Code 下載[從 claude.ai 同步的](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins) plugin，而不是從 marketplace 下載，因此此鎖定不涵蓋它們。若要也停止這些，請在受管設定中將 [`syncClaudeAiPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#syncclaudeaiplugins) 設定為 `false`，或在 claude.ai 上為您的組織關閉 Skills。 僅允許官方 Anthropic marketplace。單一儲存庫項目的匹配是精確的，因此此項目不涵蓋同一儲存庫的 `ref` 或 `path` 變體：

```
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "anthropics/claude-plugins-official"
    }
  ]
}

```

使用此項目，Claude Code 保持已註冊的官方 marketplace 可用，並在新機器上，在您第一次以互動方式啟動 Claude Code 時自動註冊 marketplace。 自動註冊不涵蓋每台機器。它最常遺漏：

- 在機器首次互動啟動之前執行的非互動環境。
- Claude Code 已在阻止 marketplace 的原則下以互動方式執行的機器，例如空陣列鎖定。Claude Code 記錄被阻止的嘗試，並在原則變更後不重試。

在這些機器上，將 marketplace 新增到同一 `managed-settings.json` 中的 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)，以便 Claude Code 自動註冊它，或執行 `claude plugin marketplace add anthropics/claude-plugins-official`。 僅允許特定 marketplace：

```
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "acme-corp/approved-plugins"
    },
    {
      "source": "github",
      "repo": "acme-corp/security-tools",
      "ref": "v2.0"
    },
    {
      "source": "url",
      "url": "https://plugins.example.com/marketplace.json"
    }
  ]
}

```

使用[擁有者萬用字元](https://code.claude.com/docs/zh-TW/settings-reference#owner-wildcards)項目允許 GitHub 組織下的每個 marketplace 儲存庫。擁有者萬用字元需要 Claude Code v2.1.223 或更新版本。

```
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "acme-corp/*"
    }
  ]
}

```

使用主機上的正規表達式模式匹配允許來自內部 git 伺服器的所有 marketplace。這是 [GitHub Enterprise Server](https://code.claude.com/docs/zh-TW/github-enterprise-server#plugin-marketplaces-on-ghes) 或自託管 GitLab 執行個體的推薦方法：

```
{
  "strictKnownMarketplaces": [
    {
      "source": "hostPattern",
      "hostPattern": "^github\\.example\\.com$"
    }
  ]
}

```

使用路徑上的正規表達式模式匹配允許來自特定目錄的檔案系統型 marketplace：

```
{
  "strictKnownMarketplaces": [
    {
      "source": "pathPattern",
      "pathPattern": "^/opt/approved/"
    }
  ]
}

```

使用 `".*"` 作為 `pathPattern` 以允許任何檔案系統路徑，同時仍使用 `hostPattern` 控制網路來源。 `strictKnownMarketplaces` 限制使用者可以新增的內容，但不會自行註冊 marketplace。若要為使用者自動註冊允許的 marketplace，請將其新增到同一 `managed-settings.json` 中的 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)。官方 Anthropic marketplace 是唯一 Claude Code 自行註冊的，且僅當允許清單允許時。自動註冊也遺漏某些機器，例如非互動環境和早期原則阻止它的機器。若要涵蓋這些機器，也將官方 marketplace 新增到 `extraKnownMarketplaces`。有關兩個設定並排，請參閱 [`strictKnownMarketplaces` 參考](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces)。

#### 限制如何運作

限制在任何網路或檔案系統操作之前進行檢查。檢查在 marketplace 新增以及 plugin 安裝、更新、重新整理和自動更新時執行。如果 marketplace 在配置原則之前被新增，且其來源不再符合允許清單，Claude Code 會拒絕從中安裝或更新 plugin。相同的強制執行也適用於 `blockedMarketplaces`。 若要阻止 GitHub 擁有者下的每個 marketplace 儲存庫，請在 `blockedMarketplaces` 項目中使用擁有者萬用字元形式：`{ "source": "github", "repo": "untrusted-org/*" }`。需要 Claude Code v2.1.223 或更新版本。有關匹配規則（在封鎖清單和允許清單之間不同），請參閱[擁有者萬用字元](https://code.claude.com/docs/zh-TW/settings-reference#owner-wildcards)。 當使用者新增 Claude Code [複製而不是取得](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-other-git-hosts)的 `https://` 儲存庫 URL（例如裸 `github.com` 或 `gitlab.com` 儲存庫 URL）時，Claude Code 也會根據 `blockedMarketplaces` 中的 `url` 項目檢查它。如果項目命名相同的 URL，Claude Code 會阻止新增。在該比較中，Claude Code 忽略 `.git` 後綴和使用者在 `#` 後附加的任何 ref。需要 Claude Code v2.1.232 或更新版本。在 v2.1.232 之前，Claude Code 僅針對它作為託管 `marketplace.json` 檔案取得的 URL 符合 `url` 項目。 允許清單對大多數來源類型使用精確匹配，除了擁有者萬用字元 `github` 項目。若要允許 marketplace，所有指定的欄位必須相符：

- 對於 GitHub 來源：`repo` 是必需的，要麼命名一個儲存庫，要麼使用擁有者萬用字元形式 `owner/*` 涵蓋該擁有者下的每個儲存庫。有關萬用字元項目如何匹配（包括大小寫規則），請參閱[擁有者萬用字元](https://code.claude.com/docs/zh-TW/settings-reference#owner-wildcards)。對於單一儲存庫項目，`ref` 必須精確相符或在 marketplace 來源和允許清單項目中都不存在，相同的規則適用於 `path`
- 對於 URL 來源：完整 URL 必須完全相符
- 對於 `hostPattern` 來源：marketplace 主機與正規表達式模式相符
- 對於 `pathPattern` 來源：marketplace 的檔案系統路徑與正規表達式模式相符

允許清單的精確匹配將僅因尾部斜線、`.git` 後綴或 `ssh://` 和 `https://` 方案而異的 URL 視為不同的值。如果您的組織 marketplace 可以透過多個 URL 形式複製，請優先使用 `hostPattern` 項目而不是字面 URL，以便 `https://`、`ssh://` 和 `user@host:path` 形式都相符。 [託管在 claude.ai 上的 marketplace](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai) 按主機相符：符合 `claude.ai` 的 `hostPattern` 項目在 `strictKnownMarketplaces` 和 `blockedMarketplaces` 中管理它。在允許清單上，此類項目不允許成員的個人 claude.ai 上傳。需要 Claude Code v2.1.273 或更新版本。 因為 `strictKnownMarketplaces` 在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中設定，個別使用者和專案配置無法覆蓋這些限制。 有關完整的配置詳細資訊，包括所有支援的來源類型和與 `extraKnownMarketplaces` 的比較，請參閱 [strictKnownMarketplaces 參考](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces)。

### 版本解析和發行通道

Plugin 版本決定快取路徑和更新偵測：如果解析的版本與使用者已有的版本相符，`/plugin update` 和自動更新會跳過 plugin。對於 git 型來源，如果您省略 `version`，Claude Code 使用來源的解析提交 SHA，因此使用者在該提交變更時獲得更新；這是內部或積極開發的 plugin 的最簡單設定。請參閱[版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)以了解完整的解析順序，包括 `archive` 來源。 設定 `version` 會固定 plugin，除了 [`command`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)（其版本始終包含命令產生內容的雜湊）的每個來源類型。[在原位載入的 plugin](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)來自作為本機目錄新增的 marketplace 也不會被固定。如果您在 `plugin.json` 中宣告 `"version": "1.0.0"` 並推送新提交而不更改該字串，這些來源的現有使用者保留快取副本，因為 Claude Code 看到相同的版本。在每次發行時提升該欄位，或省略它以回退到解析的版本。避免在 `plugin.json` 和 marketplace 項目中同時設定 `version`。Claude Code 總是無聲地使用 `plugin.json` 值，因此過時的 manifest 版本可能會掩蓋您在 `marketplace.json` 中設定的版本。

#### 設定發行通道

若要為您的 plugin 支援「穩定」和「最新」發行通道，您可以設定兩個指向同一儲存庫的不同 ref 或 SHA 的 marketplace。然後，您可以透過以下兩種方式之一透過受管設定將每個使用者群組指派給其自己的 marketplace：

- 將單獨的[端點管理設定](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)（例如受管設定檔案或 MDM 設定檔）部署到每個群組的裝置。[Claude Code 如何組合受管來源](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)說明每個群組檔案或設定檔是否適用於也具有組織範圍來源的裝置。
- 為每個群組定義一個 [Claude apps gateway 原則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#managed)。gateway 適用第一個符合使用者的原則，因此排序原則以便每個使用者到達其群組的原則。群組原則的 `extraKnownMarketplaces` 替換全面原則的對應，而不是與其合併，因此在群組的原則中列出群組需要的每個 marketplace，而不僅僅是其通道 marketplace。

來自管理員主控台的伺服器管理設定[適用於您組織中的每個使用者](https://code.claude.com/docs/zh-TW/server-managed-settings#current-limitations)，因此無法進行每個群組的指派。 每個通道必須解析為不同的版本。如果您使用明確版本，`plugin.json` 必須在每個固定的 ref 處宣告不同的 `version`。如果您省略 `version`，不同的提交 SHA 已經區分通道。如果兩個 ref 解析為相同的版本字串，Claude Code 會將它們視為相同並跳過更新。

```
{
  "name": "stable-tools",
  "plugins": [
    {
      "name": "code-formatter",
      "source": {
        "source": "github",
        "repo": "acme-corp/code-formatter",
        "ref": "stable"
      }
    }
  ]
}

```

```
{
  "name": "latest-tools",
  "plugins": [
    {
      "name": "code-formatter",
      "source": {
        "source": "github",
        "repo": "acme-corp/code-formatter",
        "ref": "latest"
      }
    }
  ]
}

```

透過上述[設定發行通道](https://code.claude.com/docs/zh-TW/plugin-marketplaces#set-up-release-channels)下描述的每個群組端點管理設定或 gateway 原則將每個 marketplace 指派給其使用者群組。例如，穩定群組接收：

```
{
  "extraKnownMarketplaces": {
    "stable-tools": {
      "source": {
        "source": "github",
        "repo": "acme-corp/stable-tools"
      }
    }
  }
}

```

早期存取群組改為接收 `latest-tools`：

```
{
  "extraKnownMarketplaces": {
    "latest-tools": {
      "source": {
        "source": "github",
        "repo": "acme-corp/latest-tools"
      }
    }
  }
}

```

#### 固定依賴版本

Plugin 可以將其依賴限制在 semver 範圍內，以便依賴的更新不會破壞依賴 plugin。請參閱[限制 plugin 依賴版本](https://code.claude.com/docs/zh-TW/plugin-dependencies)以了解 `{plugin-name}--v{version}` git 標籤慣例、範圍語法，以及如何組合對同一依賴的多個限制。

### 重新命名或移除 plugin

Plugin 的 `name` 是其穩定識別碼。使用者在 `enabledPlugins`、`pluginConfigs` 和 `/plugin install` 命令中參考它，因此更改它會破壞每個現有安裝。若要更改 UI 中顯示的標籤而不破壞安裝，請設定 [`displayName`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#optional-plugin-fields) 並保持 `name` 不變。 如果您必須更改 plugin 的 `name`，或您從 `plugins` 陣列中移除 plugin，請新增頂層 `renames` 項目，以便現有使用者遷移而不是看到 `plugin-not-found` 錯誤。自動遷移需要 Claude Code v2.1.193 或更新版本。將每個前名稱對應到其目前名稱，或如果 plugin 不再存在，則對應到 `null`。以下範例將 `formatter` 重新命名為 `code-formatter`，並記錄 `legacy-linter` 已被移除：

```
{
  "name": "acme-tools",
  "owner": { "name": "Acme" },
  "plugins": [
    { "name": "code-formatter", "source": "./plugins/code-formatter" }
  ],
  "renames": {
    "formatter": "code-formatter",
    "legacy-linter": null
  }
}

```

當使用者啟動 Claude Code 時舊名稱仍在其設定中，Claude Code 會遵循 `renames` 對應：

- 如果項目指向新名稱，Claude Code 會在其新名稱下載入 plugin，並顯示一行通知，例如 `已在 "acme-tools" marketplace 中重新命名為 "code-formatter"`。然後它會在使用者、專案和本機設定範圍中重寫舊金鑰為新金鑰，用於 `enabledPlugins` 和 `pluginConfigs`，因此通知只出現一次。
- 對於 `null` 項目，Claude Code 會刪除舊金鑰，通知報告 plugin 已從 marketplace 中移除。
- 如果重新命名的 plugin 使用遠端來源，例如 `github` 或 `npm`，Claude Code 在重新命名後報告 `plugin-cache-miss`，使用者必須執行 `/plugin install` 一次以在新名稱下取得它。

將 `renames` 視為僅附加歷史記錄：即使在您預期每個使用者都已遷移後，也要保持舊項目就位。Claude Code 遵循鏈，因此如果您稍後將 `code-formatter` 重新命名為 `formatter-pro`，請新增第二項而不是編輯第一項。仍然啟用原始 `formatter` 的使用者然後透過兩項解析到 `formatter-pro`。 在編輯對應後執行 `claude plugin validate .`；它會拒絕任何鏈形成循環或不終止於 `null` 或 `plugins` 中列出的名稱的項目。 受管和原則設定對 Claude Code 是唯讀的，因此在那裡啟用的 plugin 無法自動重寫。重新命名的 plugin 仍在每個工作階段載入，但重新命名通知會重複出現，直到管理員更新受管設定檔案中的 `enabledPlugins` 以使用新名稱。相同的情況也適用於透過其他唯讀來源（例如 `--add-dir`）啟用的 plugin。 Claude Code 的早期版本會忽略 `renames` 欄位，並為舊名稱報告 `plugin-not-found`。

## 驗證和測試

在分享前測試您的 marketplace。驗證會檢查檔案結構；若要測試 plugin 是否會改變 Claude 在實際提示上的行為，請在發佈新版本前使用 [`claude plugin eval`](https://code.claude.com/docs/zh-TW/plugin-evals) 執行其評估套件。 從您的 marketplace 目錄，驗證 JSON 語法：

```
claude plugin validate .

```

或從 Claude Code 內：

```
/plugin validate .

```

新增 marketplace 進行測試：

```
/plugin marketplace add ./path/to/marketplace

```

安裝測試 plugin 以驗證一切正常運作：

```
/plugin install test-plugin@marketplace-name

```

有關完整的 plugin 測試工作流程，請參閱[在本機測試您的 plugin](https://code.claude.com/docs/zh-TW/plugins#test-your-plugins-locally)。有關技術疑難排解，請參閱 [Plugins reference](https://code.claude.com/docs/zh-TW/plugins-reference)。

## 從 CLI 管理市集

Claude Code 提供非互動式的 `claude plugin marketplace` 子命令，用於指令碼和自動化。這些命令等同於互動式工作階段中可用的 `/plugin marketplace` 命令。

### Plugin marketplace add

從 GitHub 儲存庫、git URL、遠端 URL 或本機路徑新增市集。

```
claude plugin marketplace add <source> [options]

```

**引數：**

- `<source>`：GitHub `owner/repo` 簡寫、git URL、指向 `marketplace.json` 檔案的遠端 URL，或本機目錄路徑。若要釘選到分支或標籤，請在 GitHub 簡寫後附加 `@ref`，或在 git URL 後附加 `#ref`

URL 必須包含其配置。自 Claude Code v2.1.196 起，未輸入配置的主機（例如 `gitlab.example.com/team/plugins`）會被拒絕為無效的 `owner/repo` 簡寫，錯誤訊息會告訴您新增 `https://` 或使用 `./` 作為本機路徑。較早的版本會將其誤讀為 GitHub 儲存庫路徑，並在複製時因 GitHub 找不到錯誤而失敗。 **選項：**

| 選項                                       | 說明                                                                                                                                                                  | 預設值 |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `--scope <scope>`                          | 宣告市集的位置：`user`、`project` 或 `local`。請參閱 [Plugin 安裝範圍](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-installation-scopes)               | `user` |
| `--sparse <paths...>`                      | 透過 git sparse-checkout 限制簽出到特定目錄。適用於 monorepos                                                                                                         |        |
| `--claudeai`                               | 將引數讀取為 [claude.ai 上託管的市集](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai)的名稱，而不是來源。需要 Claude Code v2.1.273 或更新版本 |        |
| 使用 `owner/repo` 簡寫從 GitHub 新增市集： |                                                                                                                                                                       |        |

```
claude plugin marketplace add acme-corp/claude-plugins

```

使用 `@ref` 釘選到特定分支或標籤：

```
claude plugin marketplace add acme-corp/claude-plugins@v2.0

```

從非 GitHub 主機上的 git URL 新增：

```
claude plugin marketplace add https://gitlab.example.com/team/plugins.git

```

從直接提供 `marketplace.json` 檔案的遠端 URL 新增：

```
claude plugin marketplace add https://example.com/marketplace.json

```

從本機目錄新增以進行測試：

```
claude plugin marketplace add ./my-marketplace

```

在專案範圍宣告市集，以便透過 `.claude/settings.json` 與您的團隊共享：

```
claude plugin marketplace add acme-corp/claude-plugins --scope project

```

對於 monorepo，限制簽出到包含外掛程式內容的目錄：

```
claude plugin marketplace add acme-corp/monorepo --sparse .claude-plugin plugins

```

從 [claude.ai 上託管的市集](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai)新增，使用 `claude plugin marketplace list` 的 `From claude.ai:` 區段中列印的名稱：

```
claude plugin marketplace add --claudeai claudeai-organization-library

```

使用 `--claudeai` 時，命令會拒絕 `--scope` 和 `--sparse`。市集是為您的帳戶託管的，而不是在設定檔中宣告的，因此您無法透過專案的 `.claude/settings.json` 共享它。

### Plugin marketplace list

列出所有已設定的市集。

```
claude plugin marketplace list [options]

```

**選項：**

| 選項                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 說明        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `--json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 輸出為 JSON |
| 使用 `--json` 時，每個項目包括 `name`、`source`、一個 `installLocation` 欄位（包含市集儲存所在的本機快取路徑），以及來源特定的欄位：GitHub 來源的 `repo`、git 和 URL 來源的 `url`，以及本機來源的 `path`。當市集新增時使用釘選的分支或標籤時，GitHub 和 git 來源也包括 `ref` 欄位。 已新增的 [claude.ai 市集](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai)沒有本機複製，因此其項目會改為使用其 claude.ai 識別碼 `marketplaceId` 和 `organizationUuid` 來代替 `installLocation`。 在 [外掛程式從您的 claude.ai 帳戶同步](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)的終端機工作階段中，文字列表的結尾會有一個 `From claude.ai:` 區段，列出 claude.ai 為您的帳戶列出的內容，超出您已新增的市集。若要新增其中一個，請參閱 [從 claude.ai 新增](https://code.claude.com/docs/zh-TW/discover-plugins#add-from-claude-ai)。`--json` 輸出僅涵蓋已設定的市集，並省略該區段。需要 Claude Code v2.1.273 或更新版本。 |             |

### Plugin marketplace remove

移除已設定的市集。別名 `rm` 也可接受。

```
claude plugin marketplace remove <name> [options]

```

**引數：**

- `<name>`：要移除的市集名稱，如 `claude plugin marketplace list` 所示。這是來自 `marketplace.json` 的 `name`，而不是您傳遞給 `add` 的來源

**選項：**

| 選項                                                                                                                                                  | 說明                                                                                                                                                                                                                                                                                                            | 預設值       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `--scope <scope>`                                                                                                                                     | 限制移除到單一設定範圍：`user`、`project` 或 `local`。請參閱 [Plugin 安裝範圍](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-installation-scopes)。省略時，宣告會從每個可編輯的範圍中移除。指定時，只會移除該範圍的宣告；當市集仍在另一個範圍中宣告時，共享狀態、快取和已安裝的外掛程式資料會保留 | （所有範圍） |
| 從其最後剩餘的範圍移除市集也會解除安裝您從中安裝的任何外掛程式。若要重新整理市集而不遺失已安裝的外掛程式，請改用 `claude plugin marketplace update`。 |                                                                                                                                                                                                                                                                                                                 |              |

### Plugin marketplace update

從其來源重新整理市集，以擷取新外掛程式和版本變更。使用分支或標籤 `ref` 新增的市集會更新到該 ref 的最新提交，而不是儲存庫的預設分支。

```
claude plugin marketplace update [name]

```

**引數：**

- `[name]`：要更新的市集名稱，如 `claude plugin marketplace list` 所示。省略時會更新所有市集

當針對種子管理的市集執行時，`remove` 和 `update` 都會失敗，該市集是唯讀的。更新所有市集時，種子管理的項目會被跳過，其他市集仍會更新。若要變更種子提供的外掛程式，請要求您的管理員更新種子映像。請參閱 [為容器預先填入外掛程式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#pre-populate-plugins-for-containers)。

## 疑難排解

### Marketplace 未載入

**症狀** ：無法新增 marketplace 或看不到其中的 plugin **解決方案** ：

- 驗證 marketplace URL 可存取
- 檢查 `.claude-plugin/marketplace.json` 是否存在於指定路徑
- 使用 `claude plugin validate .` 或 `/plugin validate .` 確保 JSON 語法有效。若要檢查 skill、agent 和 command frontmatter，請參閱[驗證沒有 manifest 的 plugin 或目錄](https://code.claude.com/docs/zh-TW/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest)
- 對於私人儲存庫，確認您有存取權限

### Marketplace 驗證錯誤

從您的 marketplace 目錄執行 `claude plugin validate .` 或 `/plugin validate .` 以檢查問題。當指向 marketplace 目錄時，驗證器檢查 `marketplace.json` 是否有架構錯誤、重複的 plugin 名稱和來源路徑遍歷。對於每個 `source` 為本機路徑的項目，它也會驗證該 plugin 自己的 `plugin.json`，並在項目的 `version` 與 `plugin.json` 中的版本不符時發出警告。在 plugin 的 `plugin.json` 中發現的問題會以項目索引作為前綴，形式為 `plugins[2] plugin.json →`。 自 Claude Code v2.1.196 起，每個項目的檢查也會：

- 包含 `source` 為 `.` 的 plugin
- 在 `marketplace.json` 位於 `.claude-plugin` 目錄外時執行，針對檔案自己的目錄解析來源
- 即使檔案的另一部分有架構錯誤，也會報告每個項目的問題

較早的版本會跳過 marketplace 根目錄中的 plugin，並且只從 `.claude-plugin/marketplace.json` 開始下降。 從 marketplace 目錄，Claude Code 不會開啟 plugin 的 skill、agent、command 或 hook 檔案。若要在這些檔案中找到錯誤，請參閱[驗證沒有 manifest 的 plugin 或目錄](https://code.claude.com/docs/zh-TW/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest)。下表列出從 marketplace 目錄最常見的錯誤，以及每個錯誤的原因和修正方式：

| 錯誤                                                                                                     | 原因                                                                                                           | 解決方案                                                                                                                                |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `No manifest found in directory. Expected .claude-plugin/marketplace.json or .claude-plugin/plugin.json` | 您命名的目錄沒有 `.claude-plugin/marketplace.json` 或 `plugin.json`，也沒有 skill、agent 或 command 檔案可檢查 | 從 marketplace 根目錄執行，或使用必需欄位建立 `.claude-plugin/marketplace.json`                                                         |
| `Invalid JSON syntax: Unexpected token...`                                                               | JSON 語法錯誤在 marketplace.json 中                                                                            | 檢查缺少的逗號、多餘的逗號或未引用的字串                                                                                                |
| `Duplicate plugin name "x" found in marketplace`                                                         | 兩個 plugin 共享相同名稱                                                                                       | 為每個 plugin 指定唯一的 `name` 值                                                                                                      |
| `plugins[0].source: Path contains ".."`                                                                  | 來源路徑包含 `..`                                                                                              | 使用相對於 marketplace 根目錄的路徑，不含 `..`。請參閱[相對路徑](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths) |
| `Marketplace name cannot contain control or bidirectional-formatting characters`                         | marketplace `name` 包含 Unicode 雙向格式化字元或控制字元，例如逸出或換行符                                     | 從名稱中移除該字元。在 v2.1.247 之前，這些字元會產生 `Marketplace name impersonates an official Anthropic/Claude marketplace` 錯誤      |
| `Plugin name cannot contain control or bidirectional-formatting characters`                              | plugin `name` 包含 Unicode 雙向格式化字元或控制字元，例如逸出或換行符                                          | 從名稱中移除該字元。在 v2.1.247 之前，Claude Code 不執行此檢查                                                                          |
| **警告** （非阻止性）：                                                                                  |                                                                                                                |                                                                                                                                         |

- `Marketplace has no plugins defined`：將至少一個 plugin 新增到 `plugins` 陣列
- `No marketplace description provided`：新增頂層 `description` 以幫助使用者瞭解您的 marketplace
- `Plugin name "x" is not kebab-case`：重新命名為僅包含小寫字母、數字和連字號（例如，`my-plugin`）。Claude Code 接受其他形式，但 claude.ai marketplace 同步會拒絕它們。
- `Marketplace name "x" is reserved in Claude Desktop`：marketplace 名稱為 `org`、`org-provisioned` 或 `unknown`（任何大小寫）。Claude Code 接受這些名稱，但 Claude Desktop 的受管 marketplace 同步會拒絕整個 marketplace。重新命名 marketplace。在 v2.1.221 之前，`claude plugin validate` 不執行此檢查。
- `Marketplace name "x" is not accepted by Claude Desktop` 或 `Plugin name "x" is not accepted by Claude Desktop`：Claude Desktop 接受最多 128 個字元的名稱，由字母、數字、`.`、`_` 和 `-` 組成，以字母或數字開頭。Claude Code 接受其他形式，但 Claude Desktop 的受管 marketplace 同步會拒絕名稱檢查失敗的 marketplace，並以無聲方式捨棄名稱檢查失敗的 plugin 項目。重新命名 marketplace 或 plugin。在 v2.1.221 之前，`claude plugin validate` 不執行這些檢查。

#### 驗證沒有 manifest 的 plugin 或目錄

若要找到 frontmatter 無法解析的 skill、agent 和 command 檔案，請執行 `claude plugin validate` 並命名保存它們的目錄。Claude Code 不會查看您命名的目錄外的檔案。除了一次針對具有 `plugin.json` 的 plugin 執行外，每次執行都需要 Claude Code v2.1.233 或更新版本。 Claude Code 根據您命名的目錄檢查不同的檔案。在第一欄中找到您想檢查的內容，並執行該列的命令：

| 若要檢查                                                                                                                                                        | 執行                                                                                | Claude Code 檢查                                                                                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 具有 `plugin.json` 的 plugin                                                                                                                                    | `claude plugin validate ./plugins/my-plugin`                                        | `plugin.json`、`hooks/hooks.json` 以及 plugin 根目錄下的 `skills`、`agents` 和 `commands` 目錄                                    |
| 一個 skill、agent 或 command 目錄，例如尚無 `plugin.json` 的 plugin                                                                                             | `claude plugin validate .claude/skills`、`~/.claude/agents` 或 `./my-plugin/agents` | 該目錄中的每個 skill、agent 或 command 檔案                                                                                       |
| 其 skill 為其根 `SKILL.md` 的資料夾                                                                                                                             | `claude plugin validate ./skills`，命名保存該資料夾的 `skills` 目錄                 | 每個資料夾的根 `SKILL.md`。保存目錄必須命名為 `skills`；位於另一個名稱下的資料夾（例如 `plugins/`）沒有檢查其根 `SKILL.md` 的執行 |
| 一個專案的三個目錄一次                                                                                                                                          | `claude plugin validate .claude`，或沒有 `.claude-plugin/` manifest 的專案根目錄    | `.claude/skills`、`.claude/agents` 和 `.claude/commands`                                                                          |
| 您的使用者層級目錄                                                                                                                                              | `claude plugin validate ~/.claude`                                                  | `~/.claude/skills`、`~/.claude/agents` 和 `~/.claude/commands`                                                                    |
| 當您針對 plugin 目錄執行 `claude plugin validate` 時，Claude Code 不檢查 plugin 根目錄下的 `SKILL.md`。當 plugin 位於名為 `skills` 的目錄中時，執行該命令兩次： |                                                                                     |                                                                                                                                   |

- 命名該 `skills` 目錄以檢查 plugin 的根 `SKILL.md`。
- 命名 plugin 目錄以檢查其餘部分。

當 plugin 位於另一個名稱下（例如 `plugins/`）時，`skills` 目錄執行不可用，沒有執行檢查其根 `SKILL.md`。 當您執行 `claude plugin validate` 時，Claude Code 不會跟隨您命名的目錄內的符號連結。它的作用取決於連結的位置：

- **plugin 或`.claude` 根目錄下的連結 `skills`、`agents` 或 `commands` 目錄**：Claude Code 警告其中沒有任何內容被讀取。
- **`skills`、`agents` 或 `commands` 目錄內的連結項目**：Claude Code 跳過它並警告，每個目錄，它跳過了多少個項目，工作階段會載入。
- **您命名的`skills` 、`agents` 或 `commands` 目錄本身是符號連結，或其父 `.claude` 目錄是**：Claude Code 報告錯誤並檢查其中沒有任何內容。改為命名真實目錄。

在兩個 skill 情況下，執行通過並帶有警告。若要檢查連結的檔案，再次執行並命名直接保存它們的目錄：

- **其`skills` 目錄[連結到同級 plugin 的 skill](https://code.claude.com/docs/zh-TW/plugins-reference#share-files-within-a-marketplace-with-symlinks) 的 plugin**：命名同級 plugin 的目錄。
- **`~/.claude/skills`或`.claude/skills` 中的[符號連結 skill 項目](https://code.claude.com/docs/zh-TW/skills#where-skills-live)**：Claude Code 在工作階段中跟隨該項目。若要檢查它，命名一個名為 `skills` 的目錄，保存真實資料夾。

乾淨的執行以 `Validation passed` 結束。 `No manifest found in directory` 表示 Claude Code 在那裡找不到 `plugin.json` 或 `marketplace.json`，也找不到它在其下探測的目錄中的 skill、agent 或 command 檔案。改為命名保存您的檔案的 `skills`、`agents` 或 `commands` 目錄。 Claude Code 從這些執行報告的兩個錯誤，以及每個的修正方式：

- `YAML frontmatter failed to parse: ...`：修正 skill、agent 或 command 檔案的 frontmatter 區塊中的 YAML。在您執行此操作之前，工作階段從檔案讀取沒有 frontmatter 欄位
- `Invalid JSON syntax: ...` 在 `hooks/hooks.json` 上：修正 JSON 語法。在您執行此操作之前，工作階段載入 plugin 而不載入該檔案中的 hook。Claude Code 僅在 plugin 執行中報告此錯誤

在 plugin 執行中，Claude Code 也警告 plugin 根目錄下的 `CLAUDE.md`。對於您透過 `plugin.json` 中的[元件路徑欄位](https://code.claude.com/docs/zh-TW/plugins-reference#component-path-fields)設定的路徑，Claude Code 檢查每個路徑是否存在，但不讀取那裡的檔案。

### Plugin 安裝失敗

**症狀** ：Marketplace 出現但 plugin 安裝失敗 **解決方案** ：

- 驗證 plugin 來源 URL 可存取
- 檢查 plugin 目錄是否包含必需的檔案
- 對於 GitHub 來源，確保儲存庫是公開的或您有存取權
- 透過手動複製/下載測試 plugin 來源
- 如果來源同時固定 `ref` 和 `sha`，已刪除的上游分支或標籤不會阻止在大多數 git 主機（包括 GitHub、GitLab 和 Bitbucket）上的安裝。在不支援按 SHA 擷取提交的伺服器上（例如 AWS CodeCommit），`ref` 仍必須存在，且固定的提交必須可從其到達。如果安裝仍然失敗，請確認固定的提交仍然存在於儲存庫中

### 私人儲存庫驗證失敗

**症狀** ：從私人儲存庫安裝 plugin 時出現驗證錯誤 **解決方案** ： 對於手動安裝和更新：

- 驗證您已使用您的 git 提供者進行驗證（例如，為 GitHub 執行 `gh auth status`）
- 檢查您的認證助手是否正確配置：`git config --global credential.helper`
- 執行 `git ls-remote <marketplace-url>` 以測試 git 是否可以自行驗證。如果 git 要求使用者名稱或密碼，請先儲存認證：對於 GitHub over HTTPS，執行 `gh auth setup-git`，對於 SSH 遠端，將您的金鑰載入 `ssh-agent`

對於背景自動更新：

- 根據預設，背景重新整理會停用 git 認證助手以進行拉取，因此拉取無法透過 HTTPS 進行驗證。具有在 `ssh-agent` 中載入的金鑰的 SSH 遠端仍會進行驗證
- 當拉取無法驗證時，Claude Code 會使用您儲存的認證重新複製 marketplace，但重新複製可能在大型儲存庫上逾時
- 設定 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` 以在背景拉取無法到達或驗證遠端時保留現有複製而不嘗試重新複製
- 配置 git 認證助手（例如 `gh auth setup-git`），以便重新複製可以驗證
- 如果重新複製在大型儲存庫上逾時，請使用 [`CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#git-operations-time-out) 增加限制
- 配置範圍限定於 marketplace 儲存庫的 [git URL 重寫](https://code.claude.com/docs/zh-TW/plugin-marketplaces#private-repositories)，以便背景拉取直接驗證
- 或使用 `/plugin marketplace update <name>` 手動更新私人 marketplace，這會使用您的認證

### Marketplace 更新在離線環境中失敗

**症狀** ：在離線或隔離環境中，背景 marketplace 重新整理無法到達遠端，Claude Code 重複嘗試無法成功的重新複製。 **原因** ：背景重新整理檢查 marketplace 的遠端以尋找新提交，當拉取無法到達遠端時，Claude Code 嘗試再次複製 marketplace。離線時，複製以相同方式失敗，現有複製保持原位。在 v2.1.274 之前，重新整理在現有複製中執行 `git pull`，當拉取失敗時將複製移到一邊以重新複製，並在之後以盡力而為的基礎上還原它。 重新整理在啟動後在背景中執行，因此不會延遲啟動。每個工作階段仍會重複失敗的嘗試，每個 git 操作都可以等待 [120 秒逾時](https://code.claude.com/docs/zh-TW/plugin-marketplaces#git-operations-time-out)。 **解決方案** ：設定 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` 以在拉取無法到達遠端時跳過重新複製嘗試並繼續使用現有複製：

```
export CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1

```

對於儲存庫永遠無法到達的完全離線部署，請改用 [`CLAUDE_CODE_PLUGIN_SEED_DIR`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#pre-populate-plugins-for-containers) 在建置時預先填充 plugin 目錄。

### Git 操作逾時

**症狀** ：Plugin 安裝或 marketplace 更新失敗，出現逾時錯誤，例如 `Git clone timed out after 120s`。 **原因** ：Claude Code 對所有 git 操作（包括複製 plugin 儲存庫和重新複製 marketplace 以更新它）使用 120 秒逾時。大型儲存庫或緩慢的網路連線可能超過此限制。 **解決方案** ：使用 `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` 環境變數增加逾時。值以毫秒為單位：

```
export CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS=300000  # 5 分鐘

```

### 相對路徑 plugin 在基於 URL 的 marketplace 中失敗

**症狀** ：透過 URL（例如 `https://example.com/marketplace.json`）新增 marketplace，但具有相對路徑來源（如 `"./plugins/my-plugin"`）的 plugin 無法安裝，出現 `its marketplace entry path does not stay inside the marketplace directory` 錯誤。已安裝的 plugin 無法載入，出現 `Plugin source path refused` 錯誤。兩個訊息都有[錯誤參考項目](https://code.claude.com/docs/zh-TW/errors#marketplace-entry-path-does-not-stay-inside-the-marketplace-directory)。 **原因** ：新增基於 URL 的 marketplace 僅下載 `marketplace.json` 檔案本身，Claude Code 不會從該伺服器按相對路徑擷取 plugin 檔案。marketplace 項目中的相對路徑參考未下載的遠端伺服器上的檔案。 **解決方案** ：

- **使用外部來源** ：將 plugin 項目變更為相對路徑以外的任何 [plugin 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-sources)：

```
{ "name": "my-plugin", "source": { "source": "github", "repo": "owner/repo" } }

```

- **使用基於 Git 的 marketplace** ：在 Git 儲存庫中託管您的 marketplace 並使用 git URL 新增它。基於 Git 的 marketplace 複製整個儲存庫，使相對路徑正常運作。

### 安裝後找不到檔案

**症狀** ：Plugin 安裝但對檔案的參考失敗，特別是 plugin 目錄外的檔案 **原因** ：Claude Code 將已安裝的 plugin 複製到快取目錄，除非 plugin 就地載入。[連結模式中的 `command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#copy-mode-and-link-mode)就地載入，[本機目錄新增的 marketplace 中的相對路徑來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#relative-paths)也是如此。參考複製 plugin 目錄外檔案的路徑（例如 `../shared-utils`）無法運作，因為這些檔案不會被複製。 **解決方案** ：有關解決方案（包括符號連結和目錄重組），請參閱 [Plugin caching and file resolution](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)。 有關其他偵錯工具和常見問題，請參閱 [Debugging and development tools](https://code.claude.com/docs/zh-TW/plugins-reference#debugging-and-development-tools)。

## 另請參閱

- [探索並安裝預先建立的 plugins](https://code.claude.com/docs/zh-TW/discover-plugins) - 從現有 marketplace 安裝 plugins
- [Plugins](https://code.claude.com/docs/zh-TW/plugins) - 建立您自己的 plugins
- [Plugins reference](https://code.claude.com/docs/zh-TW/plugins-reference) - 完整的技術規格和架構
- [Plugin settings](https://code.claude.com/docs/zh-TW/settings-reference#plugin-settings) - Plugin 配置選項
- [strictKnownMarketplaces reference](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces) - 受管 marketplace 限制

是否 助手
