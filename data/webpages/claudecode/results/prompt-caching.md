Prompt caching 讓 Claude Code 更快速且更具成本效益。沒有快取的情況下，API 會在每一回合重新處理您的完整歷史記錄。有了快取，它會重複使用已經處理過的內容，以[快取代幣費率](https://platform.claude.com/docs/en/about-claude/pricing)計費重新讀取，並且只完整處理已變更的部分。 Claude Code 會為您自動處理 prompt caching，除非您[停用它](https://code.claude.com/docs/zh-TW/prompt-caching#disable-prompt-caching)。了解 prompt caching 的運作方式仍然很有用，因為某些操作會使快取失效，並在重建時使下一個回應變得更慢且更昂貴。本頁面涵蓋哪些操作會這樣做、為什麼某些設定需要等待重新啟動才能套用，以及當使用量看起來很高時如何檢查快取效能。

## 快取的組織方式

每次您在 Claude Code 中傳送訊息時，它都會發出新的 API 請求。模型在請求之間不會記住任何內容，因此 Claude Code 會重新傳送完整的上下文：系統提示、您的專案上下文、每個先前的訊息和工具結果，以及您的新訊息。新內容會附加在末尾，這表示每個請求的大部分內容與前一個請求相同。Prompt caching 是 API 避免重新處理未變更部分的方式。 API 透過將每個請求的開始部分（稱為前綴）與最近處理的內容進行比對來進行快取。在正常的回合中，前綴是整個先前的請求，只有最新的交換是新的。比對是精確的，因此前綴中任何地方的變更都會重新計算其後的所有內容。沒有按檔案或按區段的快取。請參閱 API 參考中的 [prompt caching 如何運作](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#how-prompt-caching-works)以了解基礎機制。 ![四個回合顯示為不斷增長的水平條。每個回合的請求包含前一個回合的所有內容加上末尾附加的最新交換。在第二和第三個回合中，未變更的前綴從快取中讀取，只有新的交換被處理。在第四個回合中，系統提示已變更，因此前綴不再比對，整個請求被重新處理並寫入。](https://mintcdn.com/claude-code/VbDJw--l6T9a9Wvm/images/prompt-caching-prefix.svg?fit=max&auto=format&n=VbDJw--l6T9a9Wvm&q=85&s=f2e8f0b8298a50305fe428ca3f1d1594)

![四個回合顯示為不斷增長的水平條。每個回合的請求包含前一個回合的所有內容加上末尾附加的最新交換。在第二和第三個回合中，未變更的前綴從快取中讀取，只有新的交換被處理。在第四個回合中，系統提示已變更，因此前綴不再比對，整個請求被重新處理並寫入。](https://mintcdn.com/claude-code/_xqph1dUOslCOwsj/images/prompt-caching-prefix-dark.svg?fit=max&auto=format&n=_xqph1dUOslCOwsj&q=85&s=297dc1c639f0915cae858d0c4b6f3be5)
為了充分利用前綴比對，Claude Code 會組織每個請求，使得在回合之間很少變更的內容優先出現：

| 層級                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 內容                                  | 變更時機                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- | ------------------------------------------------ |
| 系統提示                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 核心指示、工具定義                    | 已載入的工具定義集合變更時                       |
| 專案上下文                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | CLAUDE.md、自動記憶、未限定範圍的規則 | 工作階段開始時，或在 `/clear` 或 `/compact` 之後 |
| 對話                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 您的訊息、Claude 的回應、工具結果     | 每個回合                                         |
| 對對話層的變更會保留系統提示和專案上下文的快取。對系統提示的變更會使所有內容失效，因為所有後續內容現在位於不同的前綴後面。第三欄提供常見的觸發器，而不是詳盡的清單，下面的章節涵蓋完整的集合。 前綴比對規則解釋了此頁面上的大多數行為。例如，[Plan Mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 和 [skill loading](https://code.claude.com/docs/zh-TW/skills) 會將其指示附加為對話訊息，因此快取的前綴保持完整。 有兩個設定不會出現在層級表中，但仍會影響保留的快取內容： |                                       |                                                  |

- **Model** ：每個模型都有自己的快取。切換模型會重新計算整個請求，即使內容相同。請參閱下面的 [Switching models](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)。
- **Effort level** ：在大多數模型上，每個 effort level 都有自己的快取，因此在工作階段中途變更 effort 會重新計算整個請求。在具有 API 金鑰或 Claude 訂閱的 Fable 5.1 上，快取預設保持完整。請參閱下面的 [Changing effort level](https://code.claude.com/docs/zh-TW/prompt-caching#changing-effort-level)。

在工作階段的開始選擇您的模型和 effort level，然後在任務之間的自然中斷處保存 `/compact`。您在任務中途進行的變更越少，快取命中率就越高。

### 快取的位置

快取發生在伺服器端，在提供您的模型的任何基礎設施中。位置取決於您的身份驗證方式：

- **API 金鑰、Claude 訂閱或[Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)**：快取位於 Anthropic 的基礎設施中，透過 [Claude API](https://platform.claude.com/docs) 存取
- **Amazon Bedrock 或 Google Cloud 的 Agent Platform** ：快取位於您的雲端提供者的提供基礎設施中
- **Microsoft Foundry** ：取決於部署的 [hosting option](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options)。在 Azure 部署上託管的部署在 Azure 基礎設施上提供；在 Anthropic 部署上託管的部署在 Anthropic 的基礎設施上提供
- **自訂`ANTHROPIC_BASE_URL` 或 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway)**：快取位於您的請求被轉發的位置，快取是否有效取決於閘道

Claude Code 也會在對話中途附加系統上下文，例如檔案變更通知，並在每個提供者和連線上標記該區塊以進行快取，除非您設定 [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#disable-pre-release-capabilities)，在這種情況下該區塊會以未快取的方式傳送。 在提供者自己的端點、Amazon Bedrock 及其 [Mantle endpoint](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint)、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上，快取該區塊的方式與 Claude API 相同。 當您的請求通過 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway)、自訂 `ANTHROPIC_BASE_URL` 或雲端提供者基礎 URL 覆蓋（例如 [`ANTHROPIC_BEDROCK_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars)）時，保留的快取取決於閘道如何處理 Claude Code 傳送的 [`cache_control` 標記](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints)：

- **原封不動地轉發它們** ：該區塊和您的對話快取方式與在提供者自己的端點上相同。
- **以命名`cache_control` 的 `400` 錯誤拒絕標記的請求**：Claude Code 會重新傳送請求，將標記從區塊移到您的最後一條對話訊息上，並在對話的其餘部分保持在那裡。該區塊計費為未快取的輸入；您的對話保持快取。
- **在返回成功時移除標記** ：您的整個對話歷史記錄在每個回合上計費為未快取的輸入。將區塊形式的系統內容轉換為純字串的閘道會以相同的方式丟棄標記。

有關每個提供者儲存和處理的內容，請參閱 [data usage](https://code.claude.com/docs/zh-TW/data-usage)。無論快取位於何處，條目在一段時間不活動後過期，下面的 [Cache lifetime](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime) 涵蓋 TTL 以及如何延長它。

## 使快取失效的動作

這些動作會導致下一個請求遺漏部分或全部快取。您會看到一次較慢、成本較高的回合，之後新的前綴會被快取。一旦您知道它們有成本，大多數動作在任務進行中是可以避免的。模型切換可能感覺沒有成本，直到您注意到隨後的較慢回合。

- [切換模型](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)
- [變更努力程度](https://code.claude.com/docs/zh-TW/prompt-caching#changing-effort-level)
- [開啟快速模式](https://code.claude.com/docs/zh-TW/prompt-caching#turning-on-fast-mode)
- [連接或斷開 MCP 伺服器](https://code.claude.com/docs/zh-TW/prompt-caching#connecting-or-disconnecting-an-mcp-server)
- [啟用或停用外掛程式](https://code.claude.com/docs/zh-TW/prompt-caching#enabling-or-disabling-a-plugin)
- [拒絕整個工具](https://code.claude.com/docs/zh-TW/prompt-caching#denying-an-entire-tool)
- [壓縮對話](https://code.claude.com/docs/zh-TW/prompt-caching#compacting-the-conversation)
- [累積許多影像](https://code.claude.com/docs/zh-TW/prompt-caching#accumulating-many-images)
- [升級 Claude Code](https://code.claude.com/docs/zh-TW/prompt-caching#upgrading-claude-code)

### 切換模型

每個模型都有自己的快取。使用 [`/model`](https://code.claude.com/docs/zh-TW/model-config#setting-your-model) 切換意味著下一個請求會讀取整個對話歷史記錄而沒有快取命中，即使內容相同。 當您在終端執行 `/model` 時，Claude Code 會要求您確認切換，但僅限於快取仍然溫暖且新模型不是產生最後一個回應的模型時。快取在 Claude Code 在此對話中最後一次傳送請求或 Claude 最後一次回應後的一個[快取 TTL](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime) 內保持溫暖。一旦該時間過去，快取就會過期，因此 Claude Code 會在不詢問的情況下進行切換。 在 v2.1.238 之前，Claude Code 沒有檢查快取 TTL，即使在快取過期後也會詢問。 您也可以使用 [PreModelSwitch hook](https://code.claude.com/docs/zh-TW/hooks#premodelswitch-decision-control) 要求此確認或跳過它。 [`opusplan` 模型設定](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting)在計畫模式期間解析為 Opus，在執行期間解析為 Sonnet，因此每次計畫模式切換都是模型切換並啟動新的快取。 [自動模型回退](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)在 Fable 模型和 Opus 5 上也是模型切換。當安全分類器在具有回退模型的類別中標記請求時，Claude Code 會在該模型上重新執行請求，並且工作階段會在那裡繼續。 當技能或命令的前置資料命名一個[`model`](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference)不同於工作階段目前模型時，該回合也是模型切換：下一個請求會讀取整個對話歷史記錄而沒有快取命中。工作階段模型會在您的下一個提示時繼續。`context: fork` 技能會設定[分叉子代理的模型](https://code.claude.com/docs/zh-TW/skills#run-skills-in-a-subagent)。

### 變更努力程度

在大多數模型上，在工作階段中途變更[努力程度](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)意味著下一個請求會讀取整個對話歷史記錄而沒有快取命中。當快取仍然溫暖時，Claude Code 會要求您先確認變更。 在具有 API 金鑰或 Claude 訂閱的 Fable 5.1 上，變更努力程度會保留快取，Claude Code 會在不詢問的情況下套用新的程度。這不適用於 Amazon Bedrock、Google Cloud 的 Agent Platform 或 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)，或當您設定 [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#disable-pre-release-capabilities) 或您的組織具有 HIPAA 設定時。 在 v2.1.260 之前，在具有 API 金鑰或 Claude 訂閱的 Fable 5.1 上變更努力程度也會使快取失效。

### 開啟快速模式

啟用[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)會新增一個請求標頭，該標頭是快取金鑰的一部分，因此 Claude Code 傳送的第一個啟用快速模式的請求會讀取整個對話歷史記錄而沒有快取命中。Claude Code 在回合開始時設定該標頭一次，並為整個回合保留它，因此當您在 Claude 工作時開啟快速模式時，標頭的快取遺漏會在您下一個回合的第一個請求時發生。這些未快取的輸入令牌按[快速模式費率](https://code.claude.com/docs/zh-TW/fast-mode#understand-the-cost-tradeoff)計費，這就是為什麼在工作階段開始時開啟它的成本比在長工作階段深處開啟它的成本要低。如果您目前的模型不支援快速模式，啟用快速模式也會[切換您的模型](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)，該切換本身會從執行回合中的下一個請求開始啟動新的快取。 成本每個對話應用一次。在第一個快速模式回合之後，Claude Code 會繼續傳送標頭，並且僅改變請求的速度設定，這不是快取金鑰的一部分。關閉快速模式、[達到速率限制後自動回退到標準速度](https://code.claude.com/docs/zh-TW/fast-mode#handle-rate-limits)以及稍後重新開啟都會保留快取。如果您[在工作階段中途用完使用額度](https://code.claude.com/docs/zh-TW/fast-mode#handle-rate-limits)，Claude Code 會以相同方式在標準速度下重試每個被拒絕的快速模式請求，因此此回退也會保留快取。`/clear` 和 `/compact` 會重設此設定，因為它們無論如何都會在這些點重建快取。

### 連接或斷開 MCP 伺服器

工具定義位於系統提示層，因此當請求中的工具定義集合在回合之間變更時，快取會失效。切換[顧問工具](https://code.claude.com/docs/zh-TW/advisor)是一個例外：其定義位於快取中斷點之後，因此啟用或停用 `/advisor` 會保留快取的前綴完整。[MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)變更是否執行此操作取決於其工具是否由[工具搜尋](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search)延遲或載入到前綴中：

- **延遲工具** ，在支援的模型上為預設值：伺服器連接、斷開或變更其工具清單只會附加新內容，不會擾亂已快取的任何內容。
- **載入到前綴中的工具** ：對它們的任何變更都會使快取失效。這發生在[工具搜尋不可用或已停用](https://code.claude.com/docs/zh-TW/mcp#configure-tool-search)時，例如在早於 Claude 4.5 世代的 Google Cloud Agent Platform 模型上、使用自訂 `ANTHROPIC_BASE_URL` 閘道或在 Microsoft Foundry [部署在 Azure 上](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options)一旦 Claude Code 偵測到部署拒絕工具搜尋時。它也發生在標記為 [`alwaysLoad`](https://code.claude.com/docs/zh-TW/mcp#exempt-a-server-from-deferral) 的伺服器或工具上，以及由[基於閾值的載入](https://code.claude.com/docs/zh-TW/mcp#configure-tool-search)保留在前面的定義上。

當工具載入到前綴中時，失效最常見的原因是伺服器在工作階段中途連接或斷開，這可能在沒有您採取任何動作的情況下發生：stdio 伺服器的程序退出、HTTP 工作階段過期或伺服器[在暫時性故障後自動重新連接](https://code.claude.com/docs/zh-TW/mcp#automatic-reconnection)。連接的伺服器也可以推送[動態工具更新](https://code.claude.com/docs/zh-TW/mcp#dynamic-tool-updates)來變更其工具清單。 編輯您的 MCP 設定本身不會變更快取。新設定只有在重新啟動後才會生效，這是伺服器連接或斷開的時候。

### 啟用或停用外掛程式

當您啟用或停用[外掛程式](https://code.claude.com/docs/zh-TW/plugins)時，變更的成本取決於外掛程式提供的元件類型。下面的案例涵蓋每個元件類型、Claude Code 何時套用變更，以及在同一工作階段中再次停用外掛程式時會發生什麼。

#### 保留快取的外掛程式元件

Claude Code 永遠不會使外掛程式的技能、命令、代理、hooks、監視器或主題的快取失效。它會在現有對話之後附加其內容，因此下一個請求會為該內容付費，並且仍然會從快取中讀取其之前的所有內容。

#### 提供 MCP 伺服器的外掛程式

當您啟用或停用提供 [MCP 伺服器](https://code.claude.com/docs/zh-TW/plugins-reference#mcp-servers) 的外掛程式時，Claude Code 會遵循與[連接或斷開 MCP 伺服器](https://code.claude.com/docs/zh-TW/prompt-caching#connecting-or-disconnecting-an-mcp-server)相同的規則：

- 如果 Claude Code 延遲伺服器的工具，它會保留快取。
- 如果 Claude Code 將它們載入到前綴中，下一個請求會重新讀取整個對話。

#### 程式碼智慧外掛程式

當您啟用[程式碼智慧外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins#code-intelligence)時，Claude 會取得 [LSP 工具](https://code.claude.com/docs/zh-TW/tools-reference#lsp-tool-behavior)。

#### 外掛程式變更何時套用

您在 `/plugin` 功能表中所做的變更會通過 [`/reload-plugins`](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting) 進行，Claude Code 會在您關閉功能表時為您執行。您會支付成本，無論是附加的公告還是完整重新讀取，都是在變更套用後的第一個回合。Claude Code 也可以自行套用變更：

- 對於具有 `command` 來源的外掛程式，Claude Code [可以自行重新載入外掛程式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#when-claude-code-re-runs-the-command)。
- 當您[從 `/plugin` 介面安裝外掛程式](https://code.claude.com/docs/zh-TW/discover-plugins#install-plugins)時，Claude Code 可以在安裝期間啟動它。安裝摘要會告訴您它是否執行了此操作。
- 當您在 v2.1.246 或更新版本上使用 `/cd` [移動工作階段](https://code.claude.com/docs/zh-TW/permissions#move-the-session-to-another-directory)時，Claude Code 會在移動過程中套用新目錄的設定啟用的外掛程式，而不會出現保留 `/reload-plugins` 的完整重新讀取警告。
- 在互動式工作階段中，當您在使用 `--plugin-dir` 傳遞的[外掛程式資料夾](https://code.claude.com/docs/zh-TW/plugins#test-your-plugins-locally)中新增或移除外掛程式時，變更會立即套用。如果套用它會觸發完整重新讀取，Claude Code 會改為保留變更並顯示通知以執行 `/reload-plugins`。需要 Claude Code v2.1.265 或更新版本。

當 `/reload-plugins` 執行且重新載入會觸發完整重新讀取時，Claude Code 會顯示警告且不套用重新載入。執行 `/reload-plugins --force` 以無論如何套用它。 `/reload-plugins` 也在沒有互動式終端的工作階段中執行，例如桌面應用程式、Agent SDK 和[非互動式模式](https://code.claude.com/docs/zh-TW/headless)搭配 `-p`，當您直接將其輸入工作階段時。需要 Claude Code v2.1.260 或更新版本。 在這些工作階段中，重新載入會套用除了外掛程式 MCP 伺服器變更之外的所有內容，這些變更[在您的下一個工作階段中生效](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)，因此永遠不會在工作階段中途造成完整重新讀取的成本。

#### 您在一個工作階段中啟用然後停用的外掛程式

當您停用您在工作階段中較早啟用的外掛程式時，Claude Code 會還原先前的請求形狀。如果該前綴仍在其[快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)內，下一個請求會讀取較舊的快取項目，而不是重建。

### 拒絕整個工具

新增裸工具名稱（如 `Bash` 或 `WebFetch`）作為[拒絕規則](https://code.claude.com/docs/zh-TW/permissions#manage-permissions)，Claude 無法從您的下一個請求開始呼叫該工具，無論您是通過 `/permissions` 新增規則還是通過[直接編輯設定檔](https://code.claude.com/docs/zh-TW/settings#when-edits-take-effect)。這包括您在回合中途通過 `/permissions` 新增的規則。 當[工具搜尋](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search)處於活動狀態時（在支援的模型上為預設值），請求的工具定義不會變更，快取的前綴會保留。當工具搜尋不可用或已停用時，Claude Code 會從下一個請求中移除定義，這會使快取失效，稍後移除規則也會如此。 只有在工具名稱位置相符的拒絕規則才有此效果：裸工具名稱、等效的 `Bash(*)` 形式或[工具名稱 glob](https://code.claude.com/docs/zh-TW/permissions#tool-name-wildcards)（如 `"*"`）。與只有 MCP 工具相符的 glob（如 `"mcp__*"`）會以相同方式阻止這些工具。範圍拒絕規則（如 `Bash(rm *)`）以及所有允許和詢問規則都不會變更 Claude 看到的工具。Claude Code 在 Claude 嘗試呼叫時檢查它們，保留前綴完整。

### 壓縮對話

[壓縮](https://code.claude.com/docs/zh-TW/context-window#what-survives-compaction)會用摘要取代您的訊息歷史記錄。根據設計，這會使對話層失效，因為下一個請求具有新的、較短的歷史記錄，不與舊歷史記錄共享前綴。Claude Code 會重複使用系統提示層，除非對話是[在保留會以其他方式變更的系統提示的同時繼續](https://code.claude.com/docs/zh-TW/prompt-caching#resuming-a-session)；在這種情況下，第一次壓縮會切換到目前提示，該層會重建一次。它會從磁碟重新載入專案內容，只有在工作階段開始以來 CLAUDE.md 和記憶未變更時才會快取命中。 為了產生摘要，Claude Code 會傳送一個單獨的請求，其中包含與您的對話相同的系統提示、工具和歷史記錄，加上作為最終使用者訊息附加的摘要指令。當快取溫暖時，該請求會從快取讀取您的前綴，因此工作階段中途的 `/compact` 成本是內容大小建議的一小部分，並且大部分時間花在產生摘要上。 在超過[快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)的中斷後，沒有快取可讀取，因此摘要請求會將完整歷史記錄重新處理為未快取的輸入。這就是為什麼當您[繼續舊工作階段](https://code.claude.com/docs/zh-TW/sessions#resume-from-a-summary)時 `/compact` 成本最高。在溫暖和冷的情況下，壓縮後的回合只會為更短的摘要重建對話快取，因此該回合不是較慢的部分。 當您捨棄的內容是您不再需要的內容時，壓縮對您有利。為了選擇其開銷何時發生，請在工作的自然中斷處（例如任務之間）執行 `/compact`，而不是等待自動壓縮在任務中途觸發。如果您走上了想要完全放棄的路徑，請改為[`/rewind`](https://code.claude.com/docs/zh-TW/prompt-caching#rewinding-the-conversation)到較早的回合。重新開始會截斷回到已快取的前綴，而不是像壓縮那樣建立新的前綴。

### 累積許多影像

API 限制每個請求可以攜帶多少影像和 PDF。如需目前的數字，請參閱 API 文件中的[請求限制](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits)。Claude Code 也會限制請求中影像和 PDF 的總大小，因此大型螢幕擷取畫面會以比小型螢幕擷取畫面更少的影像數量達到限制。 當下一個請求會超過任一限制時，Claude Code 會從其傳送的內容中移除一批最舊的影像和 PDF，這會為更多內容騰出空間，然後才需要再次移除任何內容。Claude 無法再看到移除的影像。如果 Claude 稍後需要其中一個，請再次共享它。 移除影像會變更保存它們的訊息，因此下一個請求會從這些訊息中最早的訊息開始重新處理對話。因為 Claude Code 一次移除一批，您會看到每批一個較慢的回合，而不是每個新螢幕擷取畫面一個。

### 升級 Claude Code

新的 Claude Code 版本通常會更新系統提示或工具定義，因此您在升級後開始的第一個對話會從頭開始建立其快取。[自動更新](https://code.claude.com/docs/zh-TW/setup#auto-updates)會在背景下載新版本，但在下一次啟動時套用它們，永遠不會在工作階段中途，因此您會看到這是重新啟動後的未快取第一個回合，而不是工作階段期間的驚喜。設定 `DISABLE_AUTOUPDATER=1` 以控制何時套用升級。 如需繼續您在升級前開始的對話的成本，請參閱[繼續工作階段](https://code.claude.com/docs/zh-TW/prompt-caching#resuming-a-session)。

## 保留快取的動作

這些動作要麼附加到對話的末尾，要麼根本不觸及請求。其中一些動作（例如編輯 CLAUDE.md）保留快取的原因與變更在執行中的工作階段中不會生效直到 `/clear`、`/compact` 或重新啟動的原因相同。

- [編輯您的儲存庫中的檔案](https://code.claude.com/docs/zh-TW/prompt-caching#editing-files-in-your-repository)
- [在工作階段中編輯 CLAUDE.md](https://code.claude.com/docs/zh-TW/prompt-caching#editing-claude-md-mid-session)
- [變更權限模式](https://code.claude.com/docs/zh-TW/prompt-caching#changing-permission-mode)
- [變更輸出樣式](https://code.claude.com/docs/zh-TW/prompt-caching#changing-output-style)
- [叫用技能和命令](https://code.claude.com/docs/zh-TW/prompt-caching#invoking-skills-and-commands)
- [執行 `/recap`](https://code.claude.com/docs/zh-TW/prompt-caching#running-%2Frecap)
- [倒帶對話](https://code.claude.com/docs/zh-TW/prompt-caching#rewinding-the-conversation)
- [生成子代理](https://code.claude.com/docs/zh-TW/prompt-caching#subagents-and-the-cache)

### 編輯您的儲存庫中的檔案

檔案內容只有在 Claude 讀取時才會進入上下文，而讀取會附加到對話中。編輯 Claude 之前讀過的檔案不會追溯性地改變歷史記錄中的早期讀取。相反，Claude Code 會附加一個 `<system-reminder>` 注意到檔案已變更，如果需要，Claude 會重新讀取它。

### 在工作階段中編輯 CLAUDE.md

您的專案根目錄和使用者層級 CLAUDE.md 檔案在工作階段開始時讀取一次並保存在記憶體中。在工作階段中編輯它們不會使快取失效，但編輯也不會應用。Claude 繼續使用在工作階段開始時載入的版本。新內容在下一次 `/clear`、`/compact` 或重新啟動時載入。 [子目錄中的巢狀 CLAUDE.md 檔案](https://code.claude.com/docs/zh-TW/memory)和[具有 `paths:` frontmatter 的規則](https://code.claude.com/docs/zh-TW/memory#path-specific-rules)稍後載入，當 Claude 首次讀取匹配的檔案時。在它載入之前編輯它確實會生效。載入後，內容是對話歷史記錄的一部分，因此在工作階段中編輯不會追溯性地改變它。

### 變更權限模式

在[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)之間切換，例如從手動切換到接受編輯，不會改變系統提示或工具定義，因此模式變更是快取安全的。例外是使用 [`opusplan`](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting) 模型設定的計畫模式，它在您進入或離開計畫模式時在 Opus 和 Sonnet 之間切換模型。這使得模式切換成為[模型切換](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)。

### 變更輸出樣式

當您在工作階段中使用 [`/output-style`](https://code.claude.com/docs/zh-TW/output-styles#change-your-output-style)、`/config` 或 `outputStyle` 設定切換[輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)時，Claude 從您的下一條訊息開始使用新樣式。Claude Code 將新樣式的指示作為對話中的訊息傳遞，因此該請求仍然從快取中讀取系統提示和較早的對話。 在 v2.1.251 之前，在工作階段中切換樣式會保留快取，但在您執行 `/clear` 或開始新工作階段之前不會應用。

### 叫用技能和命令

[技能](https://code.claude.com/docs/zh-TW/skills)和[命令](https://code.claude.com/docs/zh-TW/commands)在叫用點將其指示作為使用者訊息注入。對話中較早的任何內容都不會改變。frontmatter 命名 `model` 的技能或命令可以是該輪的[模型切換](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)。

### 執行 `/recap`

[`/recap`](https://code.claude.com/docs/zh-TW/interactive-mode#session-recap) 生成一個摘要以在您的終端中顯示。與 `/compact` 不同，它將摘要附加為命令輸出，而不是替換您的訊息歷史記錄，因此快取的前綴保持完整。

### 倒帶對話

[`/rewind`](https://code.claude.com/docs/zh-TW/checkpointing) 將您的對話截斷回較早的輪次。剩餘的歷史記錄是快取在該點建立時的相同內容，系統提示和專案上下文層保持不變，因此下一個請求會命中較早的快取項目。自那時以來的每一輪都已讀過該前綴，即使原始輪次比 TTL 更久遠，也保持了該項目的活躍狀態。 將檔案檢查點與對話一起還原對快取沒有單獨的影響。檔案內容只有在 Claude 讀取時才會進入上下文，與[編輯您的儲存庫中的檔案](https://code.claude.com/docs/zh-TW/prompt-caching#editing-files-in-your-repository)相同。

## 復原工作階段

當您[復原工作階段](https://code.claude.com/docs/zh-TW/sessions#resume-a-session)時，Claude Code 會重新傳送整個對話，而請求會從快取中讀取其前綴中未變更且仍在[快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)內的任何部分。本頁頂部的圖層表說明每個圖層的變更內容。 系統提示會在[Claude Code 升級](https://code.claude.com/docs/zh-TW/prompt-caching#upgrading-claude-code)後或在復原時使用不同的[`--append-system-prompt`](https://code.claude.com/docs/zh-TW/cli-reference#system-prompt-flags)文字時變更。根據預設，復原的對話會保留其開始時的系統提示，因此其歷史記錄仍位於相同提示後面，變更會在對話壓縮或新對話中生效。[復原對話中的系統提示旗標](https://code.claude.com/docs/zh-TW/cli-reference#system-prompt-flags-in-resumed-conversations)涵蓋 Claude Code 在每個請求上重新建置提示的情況。

## 快取生命週期

快取的前綴在一段時間的不活動後會過期。每個命中快取的請求都會重置計時器，因此只要您持續工作，快取就會保持溫暖。經過足夠長的間隔後，下一個請求會重新計算完整輸入並重新建立快取，這就是為什麼在離開後回來的第一個轉向可能會明顯變慢。 在 Pro 或 Max 方案上，當您在長時間中斷後恢復大型工作階段時，Claude Code [提供從摘要恢復](https://code.claude.com/docs/zh-TW/sessions#resume-from-a-summary)，以便後續請求不會攜帶完整歷史記錄。 生存時間 (TTL) 控制快取存活的間隔長度。API 提供兩種：五分鐘 TTL 和[一小時 TTL](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration)，後者可在較長的中斷期間保持快取溫暖，但[以更高的速率計費快取寫入](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing)。較長的 TTL 在您讓工作階段閒置並返回時很有幫助，因為您可以跳過過期前綴所需的重新處理。對於從不閒置超過五分鐘的短工作突發，成本更高，因為更高的寫入速率適用，而較長的快取生命週期未被使用。

### 每個請求獲得的 TTL

Claude Code 按請求決定 TTL，每個請求都屬於以下兩個固定桶之一：

- **主要對話** ：您的互動式轉向、非互動式 `-p` 執行和 Agent SDK 轉向，加上 Claude Code 與它們內聯執行的幫助程式
- **其他所有內容** ：Claude Code 在該對話之外進行的請求，例如[子代理](https://code.claude.com/docs/zh-TW/sub-agents)、[工作流程](https://code.claude.com/docs/zh-TW/workflows)、進程內[隊友](https://code.claude.com/docs/zh-TW/agent-teams)、分支、壓縮和工作階段標題

除非您自己選擇 TTL，否則 Claude Code 僅在您方案的包含使用量內的 Claude 訂閱上請求一小時 TTL。在那裡，它為主要對話請求一小時，加上 Anthropic 在伺服器端控制的一小組幫助程式請求。此表格提供兩種計費方式下每個桶的預設 TTL。

| 請求桶                                                                                                                                                                                                                                                                                                                                      | Claude 訂閱，在方案使用量內                            | 使用額度、API 金鑰或雲端提供者 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------ |
| 主要對話                                                                                                                                                                                                                                                                                                                                    | 一小時                                                 | 五分鐘                         |
| 其他所有內容                                                                                                                                                                                                                                                                                                                                | 五分鐘，除了伺服器控制的幫助程式請求外，它們獲得一小時 | 五分鐘                         |
| 一旦您超過方案的使用量限制，Claude Code 會使用[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)，您將為該使用量計費，因此 Claude Code 會將主要對話降低到更便宜的五分鐘 TTL。要在那裡保持一小時 TTL，[自己選擇 TTL](https://code.claude.com/docs/zh-TW/prompt-caching#choose-the-ttl-yourself)。 |                                                        |                                |

### 自己選擇 TTL

您可以為任一桶設定 TTL。每個控制項採用 `5m` 或 `1h`，Claude Code 會忽略任何其他值。

- **主要對話** ：[`promptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#promptcachettl) 設定，或 `CLAUDE_CODE_PROMPT_CACHE_TTL` [環境變數](https://code.claude.com/docs/zh-TW/env-vars)
- **其他所有內容** ：[`subagentPromptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#subagentpromptcachettl) 設定，或 `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` 環境變數

兩個設定和兩個環境變數都需要 Claude Code v2.1.242 或更新版本。如果您使用 API 金鑰登入或使用雲端提供者，請將 `promptCacheTtl` 設定為 `1h` 以為主要對話提供一小時快取。其外的請求保持五分鐘預設值，直到您也為該桶選擇 TTL。 當多個控制項適用時，Claude Code 按此順序採用第一個匹配項：

1. `FORCE_PROMPT_CACHING_5M=1`，為兩個桶強制五分鐘
1. 桶的環境變數
1. 桶的設定
1. 對於子代理的請求，子代理的 [`experimental` frontmatter 欄位](https://code.claude.com/docs/zh-TW/sub-agents#supported-frontmatter-fields)中的 `cacheTtl` 值，需要 Claude Code v2.1.248 或更新版本。當您的 Claude 訂閱使用使用額度時，Claude Code 會忽略那裡的 `1h`
1. `ENABLE_PROMPT_CACHING_1H=1`，為兩個桶請求一小時
1. [請求桶的預設值](https://code.claude.com/docs/zh-TW/prompt-caching#which-ttl-each-request-gets)

當您調試快取行為、比較兩個 TTL 或覆蓋在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中設定的較長 TTL 時，設定 `FORCE_PROMPT_CACHING_5M=1`。 要確認您的主要對話的快取寫入使用了哪個 TTL，請執行 `claude -p "hello" --output-format json` 並讀取結果中的 `usage.cache_creation`。Claude Code 在 `ephemeral_1h_input_tokens` 下報告一小時快取寫入，在 `ephemeral_5m_input_tokens` 下報告五分鐘快取寫入。 通過您使用 `ANTHROPIC_BASE_URL` 設定的 LLM 閘道，部分一小時請求在 `anthropic-beta` 標頭中傳輸，因此請配置閘道以[原封不動地轉發該標頭](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#request-headers)。一小時 TTL 不可通過[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway#availability-and-limitations)使用。在 Amazon Bedrock 上，prompt caching 支援、最小可快取前綴長度和一小時 TTL 可用性都因模型而異。如果快取令牌計數保持為零，請檢查 Amazon Bedrock 文件中的[支援的模型、區域和限制](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-models)。

## 快取範圍

在 Claude Code 中，快取實際上是限定在一台機器和一個目錄的範圍內。每個對話都會帶有工作目錄、平台、shell 和作業系統版本，系統提示會命名您的自動記憶路徑，因此在不同目錄中的兩個工作階段會建立不同的前綴並且會錯過彼此的快取。這包括同一個儲存庫的 worktrees，因為每個 worktree 都有自己的工作目錄。 您在同一目錄中並行執行的工作階段會建立相符的前綴並讀取彼此的快取。順序工作階段只有在啟動時取得的 git 狀態快照相符時才會共享前綴，因為每個對話也會帶有該快照中的分支和最近的提交。 底層 API 快取的範圍更廣。快取在組織之間是隔離的，在某些提供者上，[在組織內的工作區之間隔離](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-storage-and-sharing)。在這些邊界內，任何兩個具有相同模型和前綴的請求都會讀取相同的快取。對於執行自動化程序群隊的 Agent SDK 呼叫者，請參閱[改善跨使用者和機器的提示快取](https://code.claude.com/docs/zh-TW/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)以抑制系統提示的每台機器部分並在機器之間共享快取。

## 檢查快取效能

快取效能會在 API 對每個回應報告的兩個權杖計數中顯示。最直接的方式是使用[狀態列指令碼](https://code.claude.com/docs/zh-TW/statusline)來監看 `current_usage` 物件：

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 意義                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `cache_creation_input_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 在此輪次寫入快取的權杖，按快取寫入費率計費            |
| `cache_read_input_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 在此輪次從快取提供的權杖，按標準輸入費率的約 10% 計費 |
| 高讀取與建立比率表示快取運作良好。如果建立在輪次之間保持高位，表示您的前綴中有所變更。[使快取失效的動作](https://code.claude.com/docs/zh-TW/prompt-caching#actions-that-invalidate-the-cache)章節列出常見原因。 如需每個工作階段的摘要，請執行 `/usage`。在主要對話的第一個回應之後，Claude Code 會在工作階段區塊中新增[`Prompt cache (main)` 行](https://code.claude.com/docs/zh-TW/costs#prompt-cache-statistics)，顯示工作階段的命中率、未命中計數，以及快取目前是否為熱狀態。狀態列指令碼可以從 [`prompt_cache` 物件](https://code.claude.com/docs/zh-TW/statusline#prompt-cache-fields)讀取相同的數字。兩者都需要 Claude Code v2.1.251 或更新版本。 當 Claude Code 能夠識別時，`Prompt cache (main)` 行也會命名最後一次未命中的可能原因，例如 `likely cause: tool definitions changed`。可能原因文字需要 Claude Code v2.1.260 或更新版本。 如需整個組織的可見性，OpenTelemetry 匯出器會報告每個使用者和工作階段的快取讀取和建立權杖。請參閱[監控使用情況](https://code.claude.com/docs/zh-TW/monitoring-usage)以取得度量和事件屬性參考。 |                                                       |

## 子代理與快取

[子代理](https://code.claude.com/docs/zh-TW/sub-agents)會以自己的系統提示和工具集開始新的對話，與父代理分開。它的第一個請求不會讀取父代理的快取，因為兩個前綴不同，並且它會在自己的轉換過程中預熱自己的快取。子代理位於主對話[TTL 時間桶](https://code.claude.com/docs/zh-TW/prompt-caching#which-ttl-each-request-gets)之外，因此即使在訂閱上也能獲得五分鐘，直到您[選擇更長的時間](https://code.claude.com/docs/zh-TW/prompt-caching#choose-the-ttl-yourself)。 父代理的快取不受影響。從父代理的角度來看，子代理的呼叫和結果會附加到對話中，保持父代理的前綴完整。 相比之下，[分支](https://code.claude.com/docs/zh-TW/sub-agents#fork-the-current-conversation)會完全繼承父代理的系統提示、工具和對話歷史，因此它的第一個請求會讀取父代理的快取。 其他請求也可以讀取較早請求快取的前綴：

- **工作階段副本** ：您[使用 `/fork` 複製的工作階段](https://code.claude.com/docs/zh-TW/agent-view#copy-the-session-with-%2Ffork)會在複製的對話末尾收到其隔離指令作為訊息，因此原始對話建立的快取保持完整。
- **壓縮** ：[壓縮對話](https://code.claude.com/docs/zh-TW/prompt-caching#compacting-the-conversation)中描述的摘要化呼叫使用相同的前綴共享方法。
- **已恢復的子代理** ：當 Claude [恢復子代理](https://code.claude.com/docs/zh-TW/sub-agents#resume-subagents)時，已恢復執行的第一個請求可以讀取原始執行預熱的快取。
- **工作流扇出** ：在[工作流扇出](https://code.claude.com/docs/zh-TW/workflows#prompt-caching-in-a-fan-out)中，Claude Code 預設會將除第一個代理外的所有代理保留最多 5 秒，因此它們的第一個請求可以讀取第一個代理快取的前綴。

## 停用 prompt caching

在針對特定模型或提供者除錯 caching 行為時，停用 caching 偶爾會很有用。若要將其關閉，請將以下其中一個環境變數設定為 `1`：

| 變數                                                                                                                                                                                                                                                               | 效果                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------ |
| `DISABLE_PROMPT_CACHING`                                                                                                                                                                                                                                           | 停用所有模型的 caching   |
| `DISABLE_PROMPT_CACHING_HAIKU`                                                                                                                                                                                                                                     | 僅停用 Haiku 的 caching  |
| `DISABLE_PROMPT_CACHING_SONNET`                                                                                                                                                                                                                                    | 僅停用 Sonnet 的 caching |
| `DISABLE_PROMPT_CACHING_OPUS`                                                                                                                                                                                                                                      | 僅停用 Opus 的 caching   |
| `DISABLE_PROMPT_CACHING_FABLE`                                                                                                                                                                                                                                     | 僅停用 Fable 的 caching  |
| 若要在整個組織中設定 caching 原則，請將這些變數或 [TTL 變數](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime) 中的任何一個放在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)的 `env` 區塊中。在正常使用時，請保持 caching 啟用。 |                          |

## 相關資源

- [從建立 Claude Code 中學到的課程：Prompt caching 就是一切](https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything)：Plan Mode、延遲工具加載和壓縮的設計基本原理
- [探索上下文視窗](https://code.claude.com/docs/zh-TW/context-window)：什麼加載到上下文以及何時加載
- [減少令牌使用](https://code.claude.com/docs/zh-TW/costs#reduce-token-usage)：超越快取的策略，用於管理上下文大小
- [追蹤和減少成本](https://code.claude.com/docs/zh-TW/agent-sdk/cost-tracking)：Agent SDK 呼叫者的快取令牌追蹤和 TTL 配置
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)：基礎 API 機制、中斷點和定價

是否 助手
