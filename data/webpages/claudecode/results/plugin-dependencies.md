一個 plugin 可以通過在 `plugin.json` 或其 marketplace 條目中列出其他 plugin 來依賴它們。預設情況下，依賴會追蹤最新可用版本，因此上游版本發佈可能會在沒有警告的情況下更改您 plugin 的依賴。版本約束讓您可以將依賴保持在經過測試的版本範圍內，直到您選擇升級。 當您安裝聲明依賴的 plugin 時，Claude Code 會自動解析並安裝它們，除了依賴的 marketplace 條目具有 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-the-command) 或 [`headersHelper`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-a-headershelper-command) 的依賴，您需要先自行安裝。稍後，`/reload-plugins`、依賴 plugin 的 marketplace 自動更新、重新執行依賴 plugin 上的 `claude plugin install`，以及 `claude plugin marketplace add` 都會在相同規則下安裝任何未安裝的已聲明依賴；如果有一個保持未解決，請參閱[解決依賴錯誤](https://code.claude.com/docs/zh-TW/plugin-dependencies#resolve-dependency-errors)。 本指南適用於在 `plugin.json` 中聲明依賴的 plugin 作者，以及標記版本發佈的 marketplace 維護者。此處的依賴是其他 plugin；對於 plugin 本身使用的 npm 和 Bun 套件，請參閱 [Node.js 套件依賴](https://code.claude.com/docs/zh-TW/plugins-reference#node-js-package-dependencies)。若要安裝具有依賴的 plugin，請參閱[發現並安裝 plugin](https://code.claude.com/docs/zh-TW/discover-plugins)。如需完整的 manifest 架構，請參閱 [Plugins 參考](https://code.claude.com/docs/zh-TW/plugins-reference)。

## 為什麼要限制依賴版本

考慮一個內部 marketplace，其中兩個團隊發佈 plugin。平台團隊維護 `secrets-vault`，這是一個包裝 secrets 後端的 MCP 伺服器。部署團隊維護 `deploy-kit`，它在部署期間調用 `secrets-vault` 來獲取認證。 `deploy-kit` 已針對 `secrets-vault` v2.1.0 進行測試。沒有版本約束的情況下，下次平台團隊標記重新命名 MCP 工具的版本發佈時，自動更新會將每個工程師的 `secrets-vault` 移至新版本，`deploy-kit` 就會損壞。 使用版本約束，`deploy-kit` 聲明它需要 `~2.1.0` 範圍內的 `secrets-vault`。安裝了 `deploy-kit` 的工程師會保持在最高匹配的 `2.1.x` 修補程式版本。部署團隊通過發佈具有更寬鬆約束的新 `deploy-kit` 版本，按照自己的時間表進行升級。

## 聲明具有版本約束的依賴

在 plugin 的 `.claude-plugin/plugin.json` 的 `dependencies` 陣列中列出依賴。 以下 manifest 聲明了一個未版本化的依賴和一個受約束的依賴： .claude-plugin/plugin.json

```
{
  "name": "deploy-kit",
  "version": "3.1.0",
  "dependencies": [
    "audit-logger",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}

```

一個條目可以是只包含 plugin 名稱的純字符串，如 `"audit-logger"` 在 `deploy-kit` manifest 中，它依賴於該 plugin 的 marketplace 提供的任何版本。為了獲得更多控制，請使用具有以下欄位的物件：

| 欄位                                                                                         | 類型   | 描述                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                                                                                       | string | Plugin 名稱。在與聲明 plugin 相同的 marketplace 內解析。必需。                                                                                                                                                                                                                               |
| `version`                                                                                    | string | 一個 [semver 範圍](https://github.com/npm/node-semver#ranges)，例如 `~2.1.0`、`^2.0`、`>=1.4` 或 `=2.1.0`。依賴會在滿足此範圍的最高標記版本處獲取。                                                                                                                                          |
| `marketplace`                                                                                | string | 一個不同的 marketplace 來在其中解析 `name`。跨 marketplace 依賴被阻止，除非目標 marketplace 在根 marketplace 的 `marketplace.json` 中的 [`allowCrossMarketplaceDependenciesOn`](https://code.claude.com/docs/zh-TW/plugin-dependencies#depend-on-a-plugin-from-another-marketplace) 中列出。 |
| 預發佈版本（如 `2.0.0-beta.1`）被排除，除非您的範圍使用預發佈後綴（如 `^2.0.0-0`）選擇加入。 |        |                                                                                                                                                                                                                                                                                              |

## 為團隊組合外掛程式

除了必需的 `name` 之外，外掛程式資訊清單可以只包含一個 `dependencies` 陣列。安裝它會拉入每個依賴項，這使其成為在一個安裝後面打包精選外掛程式集的方式。 例如，平台團隊可以在內部市場中發佈角色特定的組合，以便工程師執行一個 `claude plugin install` 而不是分別安裝每個工具： .claude-plugin/plugin.json

```
{
  "name": "backend-standard",
  "version": "1.0.0",
  "description": "Standard plugin set for backend engineers",
  "dependencies": [
    "secrets-vault",
    "deploy-kit",
    { "name": "db-migrate", "version": "^3.0" },
    "oncall-runbook"
  ]
}

```

安裝 `backend-standard` 會解析並安裝所有四個依賴項。 若要稍後將工具新增至標準集，請發佈新的 `backend-standard` 版本並包含額外的依賴項。除非市場[自動更新](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)，工程師可以透過以下兩種方式之一取得新版本：

- 在 `/plugin` 中為市場啟用自動更新。下一次自動更新會將組合移至新版本並安裝它新增的任何依賴項。
- 執行 `claude plugin update backend-standard`，然後執行 `/reload-plugins` 以安裝新增的依賴項。

若要在整個組織中推出組合，請將組合外掛程式新增至[受管設定](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins)中的 `enabledPlugins`。

## 依賴來自另一個 marketplace 的 plugin

預設情況下，Claude Code 拒絕自動安裝位於與聲明它的 plugin 不同的 marketplace 中的依賴。這可防止一個 marketplace 無聲地從您未審查的來源拉入 plugin。 若要允許此操作，根 marketplace 的維護者將目標 marketplace 名稱添加到 `marketplace.json` 中的 `allowCrossMarketplaceDependenciesOn`。根 marketplace 是託管用戶正在安裝的 plugin 的 marketplace；只有其允許清單被查詢，因此信任不會通過中間 marketplace 鏈接。 以下 `marketplace.json` 允許 `deploy-kit` 依賴來自 `acme-shared` 的 plugin： .claude-plugin/marketplace.json

```
{
  "name": "acme-tools",
  "owner": { "name": "Acme" },
  "allowCrossMarketplaceDependenciesOn": ["acme-shared"],
  "plugins": [
    {
      "name": "deploy-kit",
      "source": "./deploy-kit",
      "dependencies": [
        { "name": "audit-logger", "marketplace": "acme-shared" }
      ]
    }
  ]
}

```

如果欄位缺失或不包含目標 marketplace，安裝將失敗，並出現 `cross-marketplace` 錯誤，命名要設置的欄位。用戶仍然可以先手動安裝依賴，這會滿足約束而無需更改允許清單。

## 在本機測試外掛程式及其依賴項

如果您同時開發一個外掛程式及其所依賴的外掛程式，請使用 `--plugin-dir` 載入兩者：

```
claude --plugin-dir ./my-dependency --plugin-dir ./my-plugin

```

依賴項的本機副本滿足您外掛程式的依賴項條目，即使該條目命名了市集，您也不需要從其市集安裝依賴項。Claude Code 不會針對本機副本檢查[版本限制](https://code.claude.com/docs/zh-TW/plugin-dependencies#declare-a-dependency-with-a-version-constraint)，因此本機 `plugin.json` 不需要 `version`。在 v2.1.242 之前，命名市集的依賴項條目永遠不會與本機副本相符，Claude Code 會在載入時停用您的外掛程式。 當兩個外掛程式位於同一個父資料夾時，您可以將該資料夾傳遞給 `--plugin-dir` 一次。如果該資料夾本身不是外掛程式，Claude Code 會載入每個具有 `.claude-plugin/plugin.json` 的子資料夾。需要 Claude Code v2.1.265 或更新版本。 如果您尚未從其市集安裝依賴項，當本機副本消失時，您的外掛程式會停止載入：

- **您停用了本機副本** ：Claude Code 會在下一次外掛程式載入時停用您的外掛程式。對於命名市集的依賴項條目，Claude Code 會報告 `Dependency "<name>@inline" is disabled — enable it or remove the dependency`；對於裸名稱條目，它會按其裸名稱報告依賴項。`<name>@inline` 是 Claude Code 識別每個 `--plugin-dir` 和 `--plugin-url` 外掛程式的方式。
- **您啟動了一個沒有依賴項`--plugin-dir` 旗標的工作階段**：Claude Code 會報告依賴項未安裝。再次傳遞該旗標，或從其市集安裝依賴項。

## 版本解析的標籤外掛程式發佈

Claude Code 針對託管依賴項的儲存庫上的 git 標籤解析版本約束：`github`、`url` 和 `git-subdir` [外掛程式來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-sources)的外掛程式自身儲存庫，或市集儲存庫中市集透過相對路徑參考的外掛程式。為了讓 Claude Code 找到依賴項的可用版本，上游外掛程式的發佈必須使用特定的命名慣例進行標籤標記。 將每個發佈標記為 `{plugin-name}--v{version}`，其中 `{version}` 與該提交的 `plugin.json` 中的 `version` 欄位相符。從外掛程式目錄執行：

```
claude plugin tag --push

```

`claude plugin tag` 命令從外掛程式的資訊清單和封閉的市集項目衍生標籤名稱。在建立標籤之前，它會驗證外掛程式內容，檢查 `plugin.json` 和市集項目是否在版本上一致，要求外掛程式目錄下的工作樹乾淨，如果標籤已存在則拒絕。

- `--push` 將標籤推送到 `origin` 遠端，因此儲存庫需要配置的 `origin` 遠端。傳遞 `--remote` 以推送到不同的遠端。
- 如果推送失敗，標籤仍會在本機建立，命令會以錯誤狀態結束。
- 使用 `--push` 時，成功執行會以 `Created tag secrets-vault--v2.1.0` 和 `Pushed to origin` 結束，其中最後一行命名推送到的遠端。不使用 `--push` 時，命令會改為列印要執行的 `git push` 命令。
- `--dry-run` 列印將被標記的內容而不建立它。

直接執行 `git tag secrets-vault--v2.1.0` 是等效的，如果您自己保持 `plugin.json` 和市集項目同步。 外掛程式名稱前綴讓一個市集儲存庫可以託管多個具有獨立版本線的外掛程式。`--v` 分隔符被解析為完整外掛程式名稱上的前綴匹配，因此包含連字號的外掛程式名稱會被正確處理。 當您安裝宣告 `{ "name": "secrets-vault", "version": "~2.1.0" }` 的外掛程式時，Claude Code 會列出託管 `secrets-vault` 的儲存庫上的標籤，篩選以 `secrets-vault--v` 開頭的標籤，並擷取滿足 `~2.1.0` 的最高版本。如果外掛程式自身儲存庫上沒有標籤滿足該範圍，安裝會失敗，並顯示 `Dependency "secrets-vault@acme-tools" has no git tag satisfying ~2.1.0`，其中命名依賴項及其市集。對於沒有匹配標籤的相對路徑外掛程式，Claude Code 會改為安裝市集的目前副本，並在外掛程式載入時檢查約束。 對於市集透過相對路徑參考的外掛程式，作為本機資料夾路徑新增的市集在資料夾是 git 儲存庫時以相同方式解析標籤。這需要 Claude Code v2.1.196 或更新版本。在兩種情況下，Claude Code 會改為從資料夾的目前內容安裝依賴項：

- 較早版本不會從本機資料夾市集讀取標籤，因此受約束的依賴項只有在該副本滿足範圍時才會載入。
- 不是 git 儲存庫的本機資料夾沒有標籤，無論版本如何。

已解析標籤的 semver 與 `plugin.json` 的 `version` 分開記錄，因此約束檢查使用實際擷取的標籤，即使該提交的 `plugin.json` 有過時的值。標籤解析安裝的快取目錄名稱包含 12 字元的提交 SHA 後綴，因此如果維護者強制將標籤移動到不同的提交，下次安裝會取得新的快取目錄，而不是重複使用過時的內容。 對於具有 `npm`、`archive` 或 `command` [外掛程式來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-sources)的依賴項，約束不控制擷取的版本，因為標籤型解析僅適用於 git 支援的來源。約束仍會在載入時檢查，如果安裝的版本不滿足約束，依賴外掛程式會被停用，狀態為 `dependency-version-unsatisfied`。對於 `command` 來源，Claude Code 會檢查依賴項的 `plugin.json` 中的版本，並忽略內容雜湊後綴；其 `plugin.json` 未設定版本的依賴項不滿足任何約束，因此在約束它之前請設定一個版本。Claude Code 永遠不會自行安裝具有 `command` 來源的依賴項，因此使用者[首先安裝它](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-the-command)。Claude Code 也永遠不會在依賴項的市集項目上執行 `headersHelper`，因此使用者[首先安裝該外掛程式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-a-headershelper-command)。

## 約束如何相互作用

當多個已安裝的 plugins 限制同一依賴時，Claude Code 會交集它們的範圍，並將依賴解析為滿足所有範圍的最高版本。下表顯示常見組合如何解析。

| Plugin A 要求                                                                                                                                                                                                                                                                                                                                                | Plugin B 要求 | 結果                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- | --------------------------------------------------------------------------------------- |
| `^2.0`                                                                                                                                                                                                                                                                                                                                                       | `>=2.1`       | 在最高 `2.x` 標籤處進行一次安裝，該標籤位於 `2.1.0` 或更高版本。兩個 plugins 都會載入。 |
| `~2.1`                                                                                                                                                                                                                                                                                                                                                       | `~3.0`        | Plugin B 的安裝失敗，出現 `range-conflict` 錯誤。Plugin A 和依賴保持原樣。              |
| `=2.1.0`                                                                                                                                                                                                                                                                                                                                                     | 無            | 依賴保持在 `2.1.0`。在安裝了 Plugin A 時，自動更新會跳過較新版本。                      |
| 自動更新會在滿足每個已安裝 plugin 範圍的最高 git 標籤處取得受約束的依賴，而不是在 marketplace 的最新版本處，因此依賴會在其允許的範圍內繼續接收更新。如果沒有標籤滿足所有範圍，自動更新會跳過該依賴，並在 `/plugin` 錯誤標籤中列出跳過，並命名限制 plugin。 當您卸載最後一個限制依賴的 plugin 時，依賴不再被保持，並在下次更新時恢復追蹤其 marketplace 條目。 |               |                                                                                         |

## 啟用或禁用具有依賴的 plugin

本節涵蓋從 marketplace 安裝的 plugins。對於您使用 `--plugin-dir` 載入的副本，請參閱[在本地測試 plugin 及其依賴](https://code.claude.com/docs/zh-TW/plugin-dependencies#test-a-plugin-and-its-dependency-locally)。 啟用 plugin 也會啟用它所依賴的 plugins，禁用 plugin 如果另一個已啟用的 plugin 仍然需要它則會被阻止。 當您啟用 plugin 時，Claude Code 也會在相同的範圍內啟用其依賴。如果依賴有其自己的依賴，Claude Code 也會啟用那些。成功訊息會列出隨著您命名的 plugin 一起啟用的其他內容。如果依賴無法啟用，命令會拒絕並告訴您什麼在阻止以及如何修復：

| 條件                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 結果                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 依賴未安裝                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 啟用失敗並為每個遺失的依賴列印 `claude plugin install` 命令。     |
| 依賴被您組織的 plugin 政策阻止                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 啟用失敗並命名被阻止的依賴。                                      |
| 依賴在優先級高於目標範圍的範圍內設置為 `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 啟用失敗。在該範圍內啟用依賴，或傳遞 `--scope` 以在那裡寫入。     |
| 所有依賴都已安裝且被允許                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 啟用成功並為 plugin 和每個在目標範圍內尚未啟用的依賴寫入 `true`。 |
| 這甚至在依賴在其 manifest 中設置 [`defaultEnabled: false`](https://code.claude.com/docs/zh-TW/plugins-reference#default-enablement) 時也成立，因為 Claude Code 為其寫入明確的 `true`。同樣的情況也適用於安裝：為滿足活躍 plugin 而引入的依賴會安裝 `true`，無論其自己的預設值如何。 當您禁用 plugin 時，Claude Code 拒絕如果另一個已啟用的 plugin 仍然依賴它。錯誤命名依賴它的 plugins 並給您一個鏈接命令，以正確的順序禁用它們，以您要求的那個結尾。 例如，如果 `deploy-kit` 依賴 `secrets-vault`，單獨禁用 `secrets-vault` 失敗，輸出類似於以下內容： |                                                                   |

```
secrets-vault is still required by deploy-kit. Disable that plugin first, or
disable everything together: claude plugin disable deploy-kit@acme-tools && claude plugin disable secrets-vault@acme-tools

```

從錯誤複製鏈接命令以在一個步驟中禁用完整集合。

## 移除孤立的自動安裝依賴

自動安裝的依賴在安裝它們的 plugins 被卸載後仍會保留在磁碟上，以防您重新安裝依賴 plugin 或想要直接繼續使用依賴。若要清理它們，請執行 `claude plugin prune` 以列出不再有任何已安裝 plugin 需要的自動安裝依賴，並在確認提示後移除它們。

```
claude plugin prune

```

如果沒有任何項目符合移除條件，該命令會列印 `Nothing to prune` 並顯示原因後退出。這是全新安裝時的預期輸出，不是錯誤。 預設情況下，prune 在使用者範圍內運作，並在移除任何內容前要求確認：

- `--scope project` 或 `--scope local` 針對不同的範圍。
- `--dry-run` 列出將被移除的內容而不更改任何內容。
- `-y` 跳過確認提示。當 stdin 或 stdout 不是終端時，prune 會列出孤立項並退出，除非您傳遞 `-y`。

若要在卸載時進行 prune，請將 `--prune` 傳遞給 `claude plugin uninstall`。移除命名的 plugin 後，Claude Code 會掃描並移除現在孤立的任何自動安裝依賴。您自己安裝的 plugins 永遠不會被 prune，只有通過另一個 plugin 的 `dependencies` 陣列自動安裝的 plugins 才會被 prune。 相同的確認行為適用。當 stdin 或 stdout 不是終端時，卸載仍會完成，但 prune 步驟會列出孤立項並且不移除任何內容，除非您傳遞 `-y`。 例如，若要卸載 `deploy-kit` 並清理它留下的依賴：

```
claude plugin uninstall deploy-kit --prune

```

## 解析依賴錯誤

依賴問題會在 `claude plugin list` 和 `/plugin` 介面中出現，以描述性錯誤訊息的形式呈現，而不是此表中的字面代碼。Claude Code 會禁用受影響的 plugin，直到您解析錯誤。下表列出最常見的錯誤及其解決方法。

| 錯誤                                                                                                                                                   | 含義                                                                                                                       | 如何解析                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dependency-unsatisfied`                                                                                                                               | 聲明的依賴未安裝，或已安裝但被禁用。                                                                                       | 執行錯誤訊息中顯示的 `claude plugin install` 命令。如果依賴的 marketplace 尚未配置，請使用 `claude plugin marketplace add` 添加它，Claude Code 將自動解析依賴。如果依賴被禁用，請啟用它。 |
| `range-conflict`                                                                                                                                       | 依賴的版本要求無法組合。錯誤訊息命名原因：沒有版本滿足所有範圍、範圍不是有效的 semver 語法，或組合的範圍太複雜而無法交集。 | 卸載或更新其中一個衝突的 plugin，修復任何無效的 `version` 字符串，簡化長 \`                                                                                                               |
| `dependency-version-unsatisfied`                                                                                                                       | 已安裝的依賴版本在此 plugin 的聲明範圍之外。                                                                               | 執行 `claude plugin install <dependency>@<marketplace>` 以根據所有當前約束重新解析依賴。                                                                                                  |
| `no-matching-tag`                                                                                                                                      | 依賴的儲存庫沒有滿足範圍的 `{name}--v*` 標籤。                                                                             | 檢查上游是否使用上述約定標記了版本發佈，或放寬您的範圍。                                                                                                                                  |
| 若要以程式設計方式檢查這些錯誤，請執行 `claude plugin list --json`。有問題的 plugin 包含列出這些錯誤的 `errors` 欄位。乾淨載入的 plugin 會省略此欄位。 |                                                                                                                            |                                                                                                                                                                                           |

## 另請參閱

- [建立 plugins](https://code.claude.com/docs/zh-TW/plugins)：使用 skills、agents 和 hooks 建立 plugins
- [建立並分發 plugin marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces)：為您的團隊託管 plugins
- [Plugins 參考](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-manifest-schema)：完整的 `plugin.json` 架構
- [版本管理](https://code.claude.com/docs/zh-TW/plugins-reference#version-management)：plugin 版本如何被解析並用作快取金鑰

是否 助手
