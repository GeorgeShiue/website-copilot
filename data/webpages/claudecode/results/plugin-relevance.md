如果您為組織運營外掛程式 marketplace，您可以根據使用者正在進行的工作，讓 Claude Code 向使用者建議特定的外掛程式。在 `marketplace.json` 中的外掛程式項目中新增 `relevance` 區塊，然後在受管設定中將 marketplace 加入允許清單。當使用者的工作階段符合其中一個已宣告的信號時，Claude Code 會顯示該外掛程式的安裝建議。 Marketplace 宣告的建議是透過[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)按 marketplace 選擇加入的。在管理員將任何 marketplace 新增至允許清單之前，該 marketplace 的 `relevance` 宣告都不會產生建議，包括官方 Anthropic marketplace。Claude Code 還包括一個獨立於此允許清單的內建建議；當 [`spinnerTipsEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#spinnertipsenabled) 設定為 `false` 時，該提示和所有 marketplace 宣告的提示都會被停用。 此頁面適用於 marketplace 運營商和企業管理員。如果您想要安裝外掛程式，請參閱[探索和安裝外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins)。

## 運作方式

`marketplace.json` 中的每個外掛程式項目都可以包含一個 `relevance` 物件。該物件命名一個主題和一個或多個信號。信號是 Claude Code 針對目前工作階段測試的模式，例如工作目錄或 Claude 已讀取的檔案。 信號比對在使用者的機器上本地進行。比對不會增加任何網路流量，也不會向 Anthropic 或 marketplace 運營商報告哪些信號相符或其值。 當信號相符且外掛程式尚未安裝時，Claude Code 會在三個位置顯示該外掛程式：

- **Spinner 提示** ：當 Claude 正在回應時，spinner 下方會出現「使用 _主題_ ？安裝 _外掛程式_ 外掛程式」訊息，並附帶 `/plugin install` 命令。
- **工作階段開始建議** ：如果 `cwd` 信號符合工作目錄，在第一個回合之前會出現一行 `plugin suggestion: <name>@<marketplace> · /plugin` 通知。
- **`/plugin`Discover 標籤** ：外掛程式會被釘選到 Discover 清單的頂部，並附帶註解，例如「建議用於此目錄」或「建議用於 stripe 命令」。

Spinner 提示和工作階段開始通知是 spinner 提示系統的一部分。當 `spinnerTipsEnabled` 在您的設定檔中解析為 `false`，或當 `excludeDefault` 在使用者、`--settings` 和受管設定中的 [`spinnerTipsOverride`](https://code.claude.com/docs/zh-TW/settings-reference#spinnertipsoverride) 鍵中解析為 `true`，且這些鍵至少配置一個提示或 `tipsFile` 時，Claude Code 會停用兩者。 Discover 標籤釘選獨立於提示設定。 Claude Code 永遠不會自動安裝外掛程式。使用者始終需要確認。

## 為外掛程式項目新增相關性

在您的 `marketplace.json` 中的外掛程式項目中新增 `relevance` 物件。以下範例宣告當 Claude 讀取 `.tf` 檔案或執行 `terraform` 時，`terraform-helpers` 外掛程式是相關的：

```
{
  "name": "acme-corp-plugins",
  "owner": { "name": "Acme Platform Team" },
  "plugins": [
    {
      "name": "terraform-helpers",
      "source": "./plugins/terraform-helpers",
      "description": "Acme conventions and helpers for Terraform",
      "relevance": {
        "topic": "Terraform",
        "signals": {
          "cli": ["terraform"],
          "filesRead": ["**/*.tf"]
        }
      }
    }
  ]
}

```

具有 `relevance` 區塊但沒有相符信號的外掛程式的行為與任何其他 marketplace 項目相同。它會在 Discover 清單中以其正常位置出現，永遠不會顯示為 spinner 提示。

## 欄位參考

### `relevance`

| 欄位      | 類型 | 說明                                                                                                                                                                                                                                 |
| --------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `topic`   | 字串 | 選用。填充 spinner 提示中「使用 _主題_ ？」的片語。通常是產品名稱，例如 `Stripe`。當外掛程式名稱不能自然地作為主題讀取時，使用 `design` 等網域。預設為外掛程式名稱，每個連字號段落大寫。工作階段開始通知不使用此值。最多 64 個字元。 |
| `signals` | 物件 | 決定外掛程式何時相關的匹配器。至少需要一個信號才能使外掛程式可被建議。請參閱下表。                                                                                                                                                   |

### `relevance.signals`

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 類型     | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cwd`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 字串陣列 | 與工作階段工作目錄相符的 Glob 模式。作為絕對路徑相符，當在 git 儲存庫內時，作為相對於儲存庫根目錄的路徑相符。正斜線正規化且不區分大小寫。每個模式都符合目錄本身及其下的所有內容，因此 `infra`、`infra/` 和 `infra/**` 的行為相同。這是唯一可以在工作階段開始時（在第一個回合之前）相符的信號。最多 10 個模式，每個 256 個字元。                                                                                                                                                                                                                                                                |
| `cli`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 字串陣列 | Claude 在此工作階段執行的 shell 命令中的命令名稱，例如 `["stripe"]`。適用於每個平台：在 Windows 上透過 PowerShell 或 Git Bash 執行的命令以相同方式記錄。Claude Code 為每個 shell 工具呼叫記錄一個命令名稱：任何前導環境變數指派和 `sudo` 之後的第一個權杖。複合命令只貢獻其前導命令，因此 `cd infra && terraform plan` 記錄 `cd`，而不是 `terraform`。完全相符。最多 10 個項目，每個 64 個字元。                                                                                                                                                                                               |
| `hosts`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 字串陣列 | 此工作階段中 Bash 命令中 `http://` 或 `https://` URL 中看到的主機名稱，例如 `["api.stripe.com"]`。僅限裸露小寫主機名稱：無配置、連接埠或路徑。完全不區分大小寫相符。最多 20 個項目，每個 128 個字元。                                                                                                                                                                                                                                                                                                                                                                                          |
| `filesRead`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 字串陣列 | 與 Claude 在此工作階段讀取的檔案路徑相符的 Glob 模式，例如 `["**/*.tf"]`。正斜線正規化且不區分大小寫。最多 10 個模式，每個 256 個字元。                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `manifestDeps`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 物件陣列 | Claude 在此工作階段讀取的套件資訊清單中宣告的相依性。每個項目都是 `{ "file": "...", "pattern": "..." }`，其中 `file` 是與資訊清單檔案路徑相符的正規表達式（如工作階段狀態中所記錄，通常是絕對路徑），`pattern` 是與該檔案內容相符的正規表達式。在 `file` 的末尾錨定，例如 JSON 逸出形式中的 `[/\\\\]package\\.json$`，因為開始錨定的模式永遠不會符合絕對路徑。路徑不會針對此信號進行分隔符號正規化，因此 Windows 路徑使用反斜線。大於 512 KB 的資訊清單檔案會被跳過。兩個值都是最多 256 個字元的 JavaScript `RegExp` 來源字串。`file` 不區分大小寫相符。`pattern` 區分大小寫。最多 10 個項目。 |
| `cli`、`hosts`、`filesRead` 和 `manifestDeps` 信號需要工作階段歷史記錄，因此它們只能在 spinner 提示和 Discover 標籤上相符。 `filesRead` 和 `manifestDeps` 信號測試工作階段的記錄檔案狀態，其中也包括 Claude 已寫入或編輯的檔案以及自動載入的 `CLAUDE.md` 記憶體檔案。對於這兩個信號，Claude Code 會跳過其自身[設定目錄](https://code.claude.com/docs/zh-TW/claude-directory)及其暫存目錄下的路徑。 以下範例使用 `manifestDeps` 在 Claude 讀取依賴 `stripe` 的 `package.json` 後建議 Stripe 外掛程式。`file` 模式使用 `[/\\\\]` 以便符合正斜線和反斜線路徑分隔符號，以及 `\\.` 以便點是字面意思。在 JSON 中，正規表達式中的每個反斜線都寫兩次。 |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

```
{
  "name": "stripe-helpers",
  "source": "./plugins/stripe-helpers",
  "relevance": {
    "topic": "Stripe",
    "signals": {
      "manifestDeps": [
        {
          "file": "[/\\\\]package\\.json$",
          "pattern": "\"stripe\"\\s*:"
        }
      ]
    }
  }
}

```

Claude Code 在載入時會忽略 `relevance` 和 `relevance.signals` 下的未知欄位，因此較舊的用戶端會繼續載入您的 marketplace。

## 在受管設定中啟用建議

在 `marketplace.json` 中宣告 `relevance` 本身是不夠的。管理員必須在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中將 marketplace 加入允許清單，才能向使用者顯示其建議。 將 marketplace 名稱新增至 `pluginSuggestionMarketplaces`。對於官方 Anthropic marketplace 以外的任何 marketplace，也在相同的受管設定中宣告 marketplace 來源，可以是該名稱在 `extraKnownMarketplaces` 中的項目，或在 `strictKnownMarketplaces` 中的項目。如果在機器上註冊的 marketplace 來自不同的來源，允許清單中的名稱會被忽略。這可防止無關的來源以允許清單中的名稱進行註冊，以便在整個組織中建議其外掛程式。 以下 `managed-settings.json` 從 GitHub 儲存庫註冊組織 marketplace 並啟用其建議：

```
{
  "extraKnownMarketplaces": {
    "acme-corp-plugins": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    }
  },
  "pluginSuggestionMarketplaces": ["acme-corp-plugins"]
}

```

官方 marketplace 不受來源宣告要求的限制，因為其名稱只能從官方 Anthropic 來源進行註冊。僅允許清單中的名稱就足夠了：

```
{
  "pluginSuggestionMarketplaces": ["claude-plugins-official"]
}

```

## 使用者看到的內容

當工作階段期間信號相符時，spinner 提示會讀取：

```
Working with Terraform? Install the terraform-helpers plugin:
/plugin install terraform-helpers@acme-corp-plugins

```

在工作階段開始時，相符的 `cwd` 信號會顯示一行通知：

```
plugin suggestion: terraform-helpers@acme-corp-plugins · /plugin

```

給定外掛程式的建議在 spinner 提示和工作階段開始通知的組合中最多每三個工作階段出現一次，安裝外掛程式後兩者都不會重複。工作階段開始通知在建議顯示兩次後還會停止出現。 在 `/plugin` Discover 標籤中，外掛程式會被釘選在其他結果上方，並附帶命名相符信號的註解，例如 `suggested for this directory` 或 `suggested for terraform commands`。Discover 標籤釘選給定的外掛程式一次；稍後的訪問會以正常順序列出它。

## 驗證您的 marketplace

針對您的 marketplace 目錄執行 `claude plugin validate` 以在發佈前檢查 `relevance` 區塊：

```
claude plugin validate ./my-marketplace

```

驗證器將 `relevance` 和 `relevance.signals` 下的未知鍵報告為警告，標記不是物件的 `relevance` 值，並拒絕包含配置、連接埠或路徑的 `signals.hosts` 項目。

## 另請參閱

- [建立和發佈外掛程式 marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces)：建立託管您的外掛程式的 marketplace
- [從您的 CLI 推薦您的外掛程式](https://code.claude.com/docs/zh-TW/plugin-hints)：從您自己的 CLI 而不是從 Claude Code 的工作階段信號提示使用者
- [所有設定](https://code.claude.com/docs/zh-TW/settings-reference#pluginsuggestionmarketplaces)：`pluginSuggestionMarketplaces` 和 `extraKnownMarketplaces`

是否 助手
