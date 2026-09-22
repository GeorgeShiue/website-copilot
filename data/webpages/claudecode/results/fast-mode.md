快速模式處於[研究預覽](https://code.claude.com/docs/zh-TW/fast-mode#research-preview)階段。該功能、定價和可用性可能會根據反饋而改變。 快速模式是 Claude Opus 的高速配置，使模型速度提升最高 2.5 倍，但每個 token 的成本更高。當您需要速度進行互動式工作（如快速迭代或實時調試）時，使用 `/fast` 切換開啟，當成本比延遲更重要時，切換關閉。 快速模式不是不同的模型。它使用 Claude Opus 搭配不同的 API 配置，優先考慮速度而非成本效率。您獲得相同的品質和功能，只是回應速度更快。快速模式在 Opus 5 和 Opus 4.8 上受支援。它在 Sonnet、Haiku 或其他模型上不可用。 Claude Code 將 Opus 4.7 視為任何其他不支援快速模式的模型：切換至它會關閉快速模式。Opus 4.7 的快速模式已於 2026 年 6 月 25 日棄用，並於 2026 年 7 月 24 日移除。 需要了解的事項：

- 使用 `/fast` 在 Claude Code CLI 中切換快速模式。VS Code 擴充功能遵循您的 [`fastMode` 設定](https://code.claude.com/docs/zh-TW/fast-mode#toggle-fast-mode)，並在選定的模型支援快速模式時提供**切換快速模式** 命令。
- 快速模式定價在 Opus 5 和 Opus 4.8 上為 10/10/10/50 MTok 輸入/輸出。
- 適用於訂閱方案（Pro/Max/Team/Enterprise）上的 Claude Code 使用者和 Claude Console。Team 和 Enterprise 組織需要擁有者先啟用它，Console 組織需要先佈建存取權限，兩者均在[需求](https://code.claude.com/docs/zh-TW/fast-mode#requirements)下說明。
- 對於訂閱方案（Pro/Max/Team/Enterprise）上的 Claude Code 使用者，快速模式僅透過使用額度提供，不包含在訂閱速率限制中。

## 切換快速模式

在 CLI 中，透過以下任一方式切換快速模式：

- 輸入 `/fast` 並按 Tab 鍵切換開啟或關閉
- 在您的[使用者設定檔案](https://code.claude.com/docs/zh-TW/settings)中設定 `"fastMode": true`

預設情況下，在互動式工作階段中開啟的快速模式會在工作階段之間保持。您可以配置快速模式在每個工作階段重設。詳見[要求每個工作階段選擇加入](https://code.claude.com/docs/zh-TW/fast-mode#require-per-session-opt-in)以了解詳情。 在[雲端工作階段](https://code.claude.com/docs/zh-TW/fast-mode#use-fast-mode-in-cloud-sessions)外，在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p` 旗標時，`/fast` 僅在使用快速模式在其 [`--settings`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 值中啟動的工作階段中運作，例如 `claude -p --settings '{"fastMode": true}'`；切換則僅適用於該工作階段，不會儲存為您的預設值。`-p` 形式需要 Claude Code v2.1.205 或更新版本。在非互動式模式的其他地方，該命令會報告快速模式不可用。 您可以在 Claude 工作時執行 `/fast`，Claude Code 會在不等待回合結束的情況下切換快速模式。Claude Code 會以原始速度完成執行中的回合，因此速度變更會從您的下一個回合開始生效。如果您目前的模型不支援快速模式，開啟它也會切換您的模型，Claude Code 會在該回合的下一個請求中使用新模型。 為了獲得最佳成本效率，在工作階段開始時啟用快速模式，而不是在對話中途切換。詳見[了解成本權衡](https://code.claude.com/docs/zh-TW/fast-mode#understand-the-cost-tradeoff)以了解詳情。 當您啟用快速模式時：

- 如果您目前的模型不支援快速模式，Claude Code 會切換到 Opus
- 您會看到確認訊息：「Fast mode ON」
- 快速模式啟用時，提示旁會出現一個小的 `↯` 圖示
- 隨時再次執行 `/fast` 以檢查快速模式是否開啟或關閉

Opus 5 是 Claude Code v2.1.219 及更新版本中的快速模式預設值。在 v2.1.219 之前，快速模式在 v2.1.154 至 v2.1.218 版本上預設為 Opus 4.8，在 v2.1.142 至 v2.1.153 版本上預設為 Opus 4.7。 當您再次使用 `/fast` 關閉快速模式時，您仍保持在 Opus 上。要切換到不同的模型，請使用 `/model`。

### 在快速模式開啟時切換模型

快速模式會在兩個方向上跟隨您的模型切換：

- **切換離開** ：當您切換到不支援快速模式的模型時，Claude Code 會關閉快速模式。這包括 Opus 4.7；在 v2.1.221 之前，快速模式在切換到 Opus 4.7 後會保持開啟，API 會拒絕請求。
- **切換回來** ：當您儲存的快速模式偏好設定為開啟時，切換回支援的 Opus 模型會再次開啟快速模式，這與新工作階段預設啟動的偏好設定相同。模型切換永遠不會為儲存偏好設定為關閉的工作階段開啟快速模式，配置了[每個工作階段選擇加入](https://code.claude.com/docs/zh-TW/fast-mode#require-per-session-opt-in)時，切換回來也不會開啟它；執行 `/fast` 以重新啟用它。

每當模型切換開啟或關閉快速模式時，Claude Code 會顯示 `Fast mode ON` 或 `Fast mode OFF` 確認，快速模式開啟時會出現 `↯` 圖示。無論您使用 `/model`、[`/config model=<model>`](https://code.claude.com/docs/zh-TW/settings) 切換，或從透過[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)連接的裝置切換，都是如此。 Claude Code 會在模型切換、重新連接或失敗的[可用性檢查](https://code.claude.com/docs/zh-TW/fast-mode#use-fast-mode-behind-proxies-and-llm-gateways)後，將工作階段的快速模式狀態重新傳送到透過遠端控制連接的裝置。

### 在雲端工作階段中使用快速模式

快速模式在[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)中運作，當它在您的帳戶上可用時，無論工作階段是在 Anthropic 管理的基礎設施上執行，還是在[自託管執行器](https://code.claude.com/docs/zh-TW/self-hosted-environments)上執行。需要工作階段環境中的 Claude Code v2.1.271 或更新版本。 在工作階段中輸入 `/fast on` 以開啟快速模式。它僅在該工作階段中保持開啟，不會儲存為您的預設值。[要求](https://code.claude.com/docs/zh-TW/fast-mode#requirements)也適用於雲端工作階段。

## 了解成本權衡

快速模式的每個 token 定價高於標準 Opus：

| 模型                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 輸入 (MTok) | 輸出 (MTok) |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ----------- |
| Opus 5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | $10         | $50         |
| Opus 4.8                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | $10         | $50         |
| 快速模式定價在整個 1M token 上下文視窗中是固定的。如需與標準 Opus 費率進行比較，請參閱 [Claude 定價參考](https://platform.claude.com/docs/zh-TW/about-claude/pricing)。 當您在對話中首次啟用快速模式時，您需要為整個對話上下文支付完整的快速模式未快取輸入 token 價格。對話進行得越深入，成本就越高，因此從一開始就啟用快速模式會更便宜。成本每個對話只適用一次，因此稍後關閉並再次開啟快速模式不會重複計費。如需了解機制，請參閱[快速模式如何與 prompt cache 互動](https://code.claude.com/docs/zh-TW/prompt-caching#turning-on-fast-mode)。 |             |             |

### 查看快速模式支出出現的位置

您看到快速模式支出的位置取決於您如何登入，因此請先執行 [`/status`](https://code.claude.com/docs/zh-TW/commands) 來檢查。如果它顯示 `Login method` 列（例如 `Claude Max account`），表示您使用 Claude 訂閱登入。如果改為顯示 `API key` 列，您的請求將計費到 Claude Console 組織。

- **Pro 和 Max** ：您從使用額度中支付快速模式費用。前往 claude.ai 上的 [**設定 > 使用情況**](https://claude.ai/settings/usage)，其中 **使用額度** 部分顯示您本月在使用額度中花費了多少。該數字包括快速模式，但不會單獨列出。
- **Team 和 Enterprise** ：您的組織從其使用額度中支付您的快速模式使用費用。若要查看您自己的使用額度支出，請執行 [`/usage`](https://code.claude.com/docs/zh-TW/costs#check-your-usage-credits-spend)。如需了解您的組織在何處查看該支出，請參閱 [Claude for Teams and Enterprise](https://code.claude.com/docs/zh-TW/costs#claude-for-teams-and-enterprise)。
- **Claude Console** ：您的組織使用其 API 使用的其餘部分支付快速模式費用。在 Console [使用情況](https://platform.claude.com/usage) 和 [成本](https://platform.claude.com/cost) 頁面上，在 **分組依據** 選單中選擇 **Speed (Research Preview)** 以將快速模式與標準速度使用分開。只有當選定的日期範圍包括快速模式使用時，您才會看到該選項。

## 決定何時使用快速模式

快速模式最適合用於回應延遲比成本更重要的互動式工作：

- 快速迭代程式碼變更
- 實時調試工作階段
- 時間敏感的工作，有緊迫的截止日期

標準模式更適合：

- 速度不那麼重要的長期自主任務
- 批次處理或 CI/CD 管道
- 成本敏感的工作負載

### 快速模式與努力等級

快速模式和努力等級都會影響回應速度，但方式不同：

| 設定                                                                                                                                              | 效果                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **快速模式**                                                                                                                                      | 相同的模型品質、更低的延遲、更高的成本             |
| **較低的努力等級**                                                                                                                                | 較少的思考時間、更快的回應、複雜任務上可能品質較低 |
| 您可以結合兩者：在直接任務上使用快速模式搭配較低的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)以獲得最大速度。 |                                                    |

## 需求

快速模式需要以下所有條件：

- **僅限 Anthropic API 或訂閱** ：快速模式可透過 Anthropic Console API 和使用額度的 Claude 訂閱方案取得。在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或 AWS 上的 Claude Platform 上無法使用。Console 組織還必須[為您的組織佈建快速模式存取](https://code.claude.com/docs/zh-TW/fast-mode#enable-fast-mode-for-your-organization)。
- **為訂閱方案開啟使用額度** ：在 Pro、Max、Team 或 Enterprise 方案上，您的帳戶必須[開啟使用額度](https://code.claude.com/docs/zh-TW/costs#add-usage-credits-to-your-subscription)，這允許超出您方案包含使用量的計費。在開啟之前，`/fast` 會報告「快速模式需要使用額度」。您開啟它們的方式取決於您的方案：
  - 在 Pro 和 Max 上，在 claude.ai 上的 [**設定 > 使用量**](https://claude.ai/settings/usage) 的 **使用額度** 部分開啟它們，或執行 `/usage-credits` 以開啟該頁面。
  - 在 Team 和 Enterprise 上，具有計費存取權限的成員在 [**管理設定 > 使用量**](https://claude.ai/admin-settings/usage) 為組織開啟它們，沒有存取權限的成員執行 `/usage-credits` 以向組織的管理員發送請求。

快速模式使用量直接從使用額度中扣除，即使您在方案上還有剩餘使用量。

- **付費 Console 組織** ：Claude Console 帳戶不使用使用額度，您的組織按令牌為快速模式付費，與其餘 API 使用量一起。在 Console 的免費評估方案上，`/fast` 顯示「評估期間快速模式不可用。請購買額度。」若要清除它，請在您的 [Console 計費設定](https://platform.claude.com/settings/billing)中購買額度。
- **Team 和 Enterprise 的擁有者啟用** ：快速模式在預設情況下對 Team 和 Enterprise 組織停用。擁有者必須明確[啟用快速模式](https://code.claude.com/docs/zh-TW/fast-mode#enable-fast-mode-for-your-organization)，使用者才能存取它。

兩個組織設定可以阻止使用 `/fast` 開啟快速模式：

- **快速模式未啟用** ：如果尚未為您的組織啟用快速模式，使用 `/fast` 開啟快速模式會顯示「快速模式已被您的組織停用。」
- **快速模式模型不允許** ：如果您組織的 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 允許清單排除快速模式 Opus 模型，開啟它會被拒絕，顯示「不在您組織的允許模型中」。在已在支援快速模式的允許 Opus 模型上執行的工作階段中，`/fast` 改為在您目前的模型上啟用快速模式，而不是切換模型。

### 為您的組織啟用快速模式

您啟用快速模式的位置取決於您的組織使用哪個產品：

- **Console** （API 客戶）：管理員在 [Claude Code 偏好設定](https://platform.claude.com/claude-code/preferences)中啟用它。快速模式處於[研究預覽](https://code.claude.com/docs/zh-TW/fast-mode#research-preview)中，因此您的組織還必須在快速模式請求成功之前佈建快速模式存取。若要取得存取權，請聯絡您的帳戶經理或加入等候清單，如 [Claude API 上的快速模式](https://platform.claude.com/docs/en/build-with-claude/fast-mode)中所述。 沒有佈建的存取權，API 會以 429 拒絕每個快速模式請求，Claude Code 會將每個拒絕視為[快速模式速率限制](https://code.claude.com/docs/zh-TW/fast-mode#handle-rate-limits)。與速率限制的冷卻時間不同，拒絕會持續到佈建存取權為止。
- **Claude AI** （Team 和 Enterprise）：擁有者在 [管理設定 > Claude Code](https://claude.ai/admin-settings/claude-code) 啟用它

另一個完全停用快速模式的選項是設定 `CLAUDE_CODE_DISABLE_FAST_MODE=1`。請參閱[環境變數](https://code.claude.com/docs/zh-TW/env-vars)。

### 在代理和 LLM 閘道後面使用快速模式

在提供快速模式之前，Claude Code 會透過直接向 `api.anthropic.com` 的請求檢查您組織的快速模式可用性。該檢查不遵循 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-base-url-and-credential)，因此在將 Claude 流量路由透過 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)並阻止直接出口到 `api.anthropic.com` 的網路上，即使推理請求有效，檢查也會失敗。該檢查確實使用已設定的 [HTTP 代理](https://code.claude.com/docs/zh-TW/network-config#proxy-configuration)，因此網路阻止只在 `api.anthropic.com` 即使透過代理也無法到達的地方才會使檢查失敗。 當檢查失敗時，`/fast` 報告「由於網路連線問題，快速模式不可用」，請求以標準速度執行，即使您的組織已啟用快速模式。過去成功的檢查會從其快取結果繼續工作，因此被阻止的檢查主要影響新安裝。 當檢查到達 `api.anthropic.com` 但呈現 Anthropic 拒絕的認證時，開放網路上也會出現相同的連線訊息。其解析金鑰是閘道發行的認證的工作階段，保存在 [`ANTHROPIC_API_KEY`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-base-url-and-credential) 中或由 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 產生，會使用該金鑰發送檢查，被拒絕的請求會報告為連線失敗。 若要復原快速模式，在網路阻止是原因的地方允許直接出口到 `api.anthropic.com`，或設定與檢查失敗方式相符的任何變數：

- `CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1` 將失敗的檢查視為可用，並仍然遵守「已被您的組織停用」的回應。當您的網路拒絕連線，或當 Anthropic 拒絕閘道認證時使用它；允許清單無法幫助認證情況，因為沒有任何東西被阻止。
- `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1` 完全跳過檢查。當您的網路攔截請求而不是拒絕它時使用它。

兩個閘道配置報告「快速模式已被您的組織停用」而不是連線訊息，即使您的組織已啟用快速模式：

- 僅使用 [`ANTHROPIC_AUTH_TOKEN`](https://code.claude.com/docs/zh-TW/llm-gateway-connect#set-the-base-url-and-credential) 進行驗證的工作階段會跳過檢查：沒有 claude.ai 登入或 Anthropic API 金鑰，以及沒有快取的成功檢查，Claude Code 會將快速模式視為由您的組織停用，而不發送請求。
- 攔截檢查並用自己的頁面回答的代理，例如傳回 HTTP 200 阻止頁面的 TLS 檢查代理，被讀取為回應，表示您的組織已停用快速模式。

在這兩種情況下，設定 `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1` 以復原快速模式。`CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS` 不適用於任何一種情況，因為它只繞過失敗的檢查，而這兩種都會產生停用回應。允許清單直接出口無法幫助持有人令牌情況，它永遠不會發送請求。 這些變數只影響用戶端檢查。當您的組織已停用快速模式時，API 會拒絕快速模式請求，無論是否設定了它們。被 API 拒絕的請求即使設定了跳過變數也會成立。Claude Code 會以標準速度重試被拒絕的請求，關閉快速模式，並且 `/fast` 報告您的組織已停用快速模式。 設定 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 也會抑制可用性檢查。沒有先前快取的成功檢查，`/fast` 報告「快速模式目前不可用」；兩個跳過變數在該配置中也會復原快速模式。

### 需要每個工作階段的選擇加入

預設情況下，使用者在互動式工作階段中開啟的快速模式會在工作階段之間持續。若要變更此設定，請在任何[設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)中將 `fastModePerSessionOptIn` 設定為 `true`，這會導致每個工作階段以快速模式關閉開始，並要求使用者使用 `/fast` 明確啟用它。[Team](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=fast_mode_teams#team-&-enterprise) 或 [Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=fast_mode_enterprise) 方案上的擁有者可以透過[伺服器管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings)在整個組織範圍內部署它。

```
{
  "fastModePerSessionOptIn": true
}

```

這對於在使用者執行多個並行工作階段的組織中控制成本很有用。使用者的快速模式偏好設定仍會被保存，因此移除此設定會復原預設的持續行為。

## 處理速率限制

快速模式與標準 Opus 有不同的速率限制。所有支援的 Opus 模型共享一個快速模式速率限制池：任何模型上的使用都會從相同的限制中扣除。當您達到快速模式速率限制時：

1. 快速模式自動回退到標準速度
1. `↯` 圖示變灰以指示冷卻
1. 您以標準速度和定價繼續工作
1. 冷卻期過期時，快速模式自動重新啟用

要手動禁用快速模式而不是等待冷卻，請再次執行 `/fast`。 如果您在工作階段中途用完使用額度，Claude Code 會在標準速度和定價下重試每個被拒絕的快速模式請求，因此您可以繼續工作，且沒有冷卻期。您看到拒絕的方式取決於工作階段類型：

- 在互動式工作階段中，Claude Code 會顯示「快速模式已禁用 · 使用額度已耗盡」通知，並在工作階段的其餘時間關閉快速模式。您儲存的快速模式偏好設定不會改變；執行 `/fast` 以重新開啟快速模式。
- 在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `--output-format stream-json`，以及透過 Agent SDK，Claude Code 會在訊息串流上以 `system` 訊息的形式發出相同的文字，子類型為 `notification`，在您用完使用額度時每個回合發出一次。快速模式保持開啟。需要 Claude Code v2.1.221 或更新版本。

## 研究預覽

快速模式是研究預覽功能。這意味著：

- 該功能可能會根據反饋而改變
- 可用性和定價可能會改變
- 底層 API 配置可能會演變

透過您通常的 Anthropic 支援管道報告問題或反饋。

## 另請參閱

- [模型配置](https://code.claude.com/docs/zh-TW/model-config)：切換模型和調整努力等級
- [有效管理成本](https://code.claude.com/docs/zh-TW/costs)：追蹤 token 使用量並降低成本
- [狀態行配置](https://code.claude.com/docs/zh-TW/statusline)：顯示模型和上下文資訊

是否 助手
