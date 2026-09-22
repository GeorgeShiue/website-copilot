## 可用模型

對於 Claude Code 中的 `model` 設定，您可以配置以下任一項：

- 一個**模型別名**
- 一個**模型名稱**
  - Anthropic API：完整的\*\*[模型名稱](https://platform.claude.com/docs/zh-TW/about-claude/models/overview)\*\*
  - Amazon Bedrock：推論設定檔 ARN
  - Microsoft Foundry：部署名稱
  - Google Cloud 的 Agent Platform：版本名稱

如需有關哪個模型和努力程度適合不同類型工作的指導，請參閱部落格上的 [Choosing a Claude model and effort level in Claude Code](https://claude.com/blog/claude-model-and-effort-level-in-claude-code)。 `ANTHROPIC_BASE_URL` 改變請求的發送位置，而不是哪個模型回答它們。若要透過 LLM 閘道路由 Claude，請參閱 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)。

### 模型別名

模型別名提供了一種便捷的方式來選擇模型設定，無需記住確切的版本號：

| 模型別名                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 行為                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`default`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 特殊值，可清除任何模型覆蓋並還原為您帳戶類型的推薦模型，或當管理員設定了[組織預設模型](https://code.claude.com/docs/zh-TW/model-config#organization-default-model)時還原為該模型。本身不是模型別名                                                                                                                                     |
| **`best`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 在您的組織有權限的地方使用 Fable 5，否則使用最新的 Opus 模型                                                                                                                                                                                                                                                                           |
| **`fable`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 使用 Claude Fable 5 進行您最困難和最長時間執行的任務                                                                                                                                                                                                                                                                                   |
| **`sonnet`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 使用最新的 Sonnet 模型進行日常編碼任務                                                                                                                                                                                                                                                                                                 |
| **`opus`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 使用最新的 Opus 模型進行複雜推理任務                                                                                                                                                                                                                                                                                                   |
| **`haiku`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 使用快速高效的 Haiku 模型進行簡單任務                                                                                                                                                                                                                                                                                                  |
| **`sonnet[1m]`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 使用 Sonnet 搭配[100 萬個 token 的 context window](https://platform.claude.com/docs/zh-TW/build-with-claude/context-windows#context-window-sizes-by-model)進行長時間會話。當 `sonnet` 已解析為具有原生 1M window 的 Sonnet 5 時無效；在 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)後方時，會為 Sonnet 5 選擇 1M window |
| **`opus[1m]`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 使用 Opus 搭配[100 萬個 token 的 context window](https://platform.claude.com/docs/zh-TW/build-with-claude/context-windows#context-window-sizes-by-model)進行長時間會話                                                                                                                                                                 |
| **`opusplan`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 特殊模式，在 Plan Mode 期間使用 `opus`，然後在執行時切換到 `sonnet`                                                                                                                                                                                                                                                                    |
| `opus` 和 `sonnet` 別名解析為什麼取決於提供者：                                                                                                                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                        |
| 提供者                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `opus`                                                                                                                                                                                                                                                                                                                                 |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | ---                                                                                                                                                                                                                                                                                                                                    |
| Anthropic API                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Opus 4.8                                                                                                                                                                                                                                                                                                                               |
| [AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)                                                                                                                                                                                                                                                                                                                                                                                           | Opus 4.8                                                                                                                                                                                                                                                                                                                               |
| Amazon Bedrock、Google Cloud 的 Agent Platform                                                                                                                                                                                                                                                                                                                                                                                                                                  | Opus 4.8                                                                                                                                                                                                                                                                                                                               |
| Microsoft Foundry                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Opus 4.6                                                                                                                                                                                                                                                                                                                               |
| 當別名解析為較舊的模型時，透過明確選擇完整模型名稱或設定 `ANTHROPIC_DEFAULT_OPUS_MODEL` 或 `ANTHROPIC_DEFAULT_SONNET_MODEL`，可以使用較新的模型。 在 v2.1.207 之前，`opus` 在 AWS 上的 Claude Platform 上解析為 Opus 4.7，在 Amazon Bedrock 和 Google Cloud 的 Agent Platform 上解析為 Opus 4.6。 別名指向您提供者的推薦版本，並隨著時間推移而更新。若要固定到特定版本，請使用完整模型名稱（例如 `claude-opus-4-8`），或設定相應的環境變數，如 `ANTHROPIC_DEFAULT_OPUS_MODEL`。 |                                                                                                                                                                                                                                                                                                                                        |
| Sonnet 5 需要 Claude Code v2.1.197 或更新版本。Opus 4.8 需要 v2.1.154 或更新版本。執行 `claude update` 以升級。                                                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                        |

### 使用 Fable 5

[Claude Fable 5](https://platform.claude.com/docs/zh-TW/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) 是 Claude Code 中最強大的模型，適合於超過單次會話的任務。它能維持長時間的自主會話，在行動前進行調查，並比較小的模型更頻繁地驗證其工作。 Fable 5 不是預設模型。使用 `/model fable` 選擇它。其安全分類器標記的請求，最常見於網路安全和生物學領域，會觸發[自動模型回退](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)。 若要充分利用 Fable 5：

- **描述結果，而不是步驟** ：給它您想要的結果，讓它規劃路徑。若要讓它持續工作直到該結果成立，[設定目標](https://code.claude.com/docs/zh-TW/goal)。
- **交給它模糊的問題** ：根本原因調查、中斷除錯和架構決策是額外調查和驗證發揮作用的地方。
- **跳過驗證提醒** ：它以較少的提示驗證自己的工作，所以測試或檢查的提醒通常是不必要的。
- **規劃更大的任務** ：給它您通常會分成多個部分的工作。它能維持長時間的會話而不失去思路。

Fable 5 需要 Claude Code v2.1.170 或更新版本。較舊的版本不會在模型選擇器中顯示 Fable 5，也無法選擇它。執行 `claude update` 以升級。Fable 5 在[零資料保留](https://code.claude.com/docs/zh-TW/zero-data-retention)下不可用，其中 `/model` 選擇器要麼省略它，要麼將其顯示為已停用。

### 設定您的模型

您可以透過多種方式配置模型，按優先順序列出：

1. **在會話期間** ：使用 `/model <alias|name>` 立即切換，或執行 `/model` 不帶任何引數以開啟選擇器。當會話有先前的輸出時，選擇器會要求確認，因為下一個回應會重新讀取完整歷史記錄而不使用快取的 context
1. **在啟動時** ：使用 `claude --model <alias|name>` 啟動
1. **環境變數** ：設定 `ANTHROPIC_MODEL=<alias|name>`
1. **設定** ：在設定檔中使用 `model` 欄位永久配置

自 v2.1.153 起，`/model` 會透過在您的使用者設定中寫入 `model` 欄位，將您的選擇儲存為新會話的預設值。在選擇器中：

- `Enter`：切換模型並儲存為您的預設值
- `s`：僅針對此會話切換模型

直接輸入 `/model <name>` 的行為類似於 `Enter`。在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `/model` 設定的模型，搭配 `-p` 旗標，僅適用於目前會話，不會儲存為您的預設值。專案和受管設定仍然優先，並在下次啟動時重新應用。您的管理員配置的[組織預設模型](https://code.claude.com/docs/zh-TW/model-config#organization-default-model)也會在下次啟動時重新應用。 在 v2.1.144 至 v2.1.152 中，`/model` 僅適用於目前會話，選擇器中的 `d` 儲存預設值。 `--model` 旗標和 `ANTHROPIC_MODEL` 環境變數僅適用於您啟動它們的會話。若要同時在不同終端中執行不同的模型，請使用各自的 `--model` 旗標啟動每個終端，而不是使用 `/model` 切換。 當 Claude Code 與 Anthropic API 通訊時，`/model` 選擇器中的價格會出現，直接或透過代理它的 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)，而一列上的價格是該列選擇的模型的價格。在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/third-party-integrations) 等第三方提供者上，以及在 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)上，您的提供者或閘道決定您支付的費用，所以選擇器列不顯示價格。價格僅是顯示標籤；它不會影響一列選擇哪個模型或您的提供者計費的內容。在 v2.1.206 之前，[AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 和閘道會話顯示 Anthropic 列表價格，一列可能顯示與其選擇的模型不同的模型的價格。 使用 `claude --resume`、`--continue` 或 `/resume` 選擇器啟動的已恢復會話會保持它們在儲存文字記錄時使用的模型，無論目前的 `model` 設定如何。如果該模型已被淘汰或被 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 排除，會話會回到正常的優先順序。這可防止另一個會話的 `/model` 選擇在恢復時改變模型。 您在新啟動時使用 `--model` 或 `ANTHROPIC_MODEL` 選擇的模型仍然優先於還原的模型。自 v2.1.195 起，[`ANTHROPIC_DEFAULT_OPUS_MODEL`](https://code.claude.com/docs/zh-TW/model-config#environment-variables) 系列變數也是如此。 當啟動時的活動模型來自專案或受管設定而非您自己的選擇時，啟動標題會顯示哪個設定檔設定了它。執行 `/model` 以覆蓋；專案或受管設定會在下次啟動時重新應用。 當透過 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) `setModel()` 方法或由執行 Claude Code CLI 的應用程式（例如 [Desktop app](https://code.claude.com/docs/zh-TW/desktop)）要求模型切換時，Claude Code 會檢查該字串是否為它識別的字串，然後再儲存它。此檢查需要 Claude Code v2.1.200 或更新版本。在 Anthropic API 上，Claude Code 識別：

- 一個模型別名
- 來自 `/model` 選擇器的項目
- 任何以 `claude-` 開頭的名稱
- 您自己配置為[自訂模型選項](https://code.claude.com/docs/zh-TW/model-config#add-a-custom-model-option)或在 [`modelOverrides`](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version) 中的值

Claude Code 會以 `Model "<name>" is not a recognized model id.` 拒絕無法識別的字串，會話會保持其目前的模型，而不是儲存該字串並在下一個請求時失敗。請參閱[錯誤參考](https://code.claude.com/docs/zh-TW/errors#model-is-not-a-recognized-model-id)以了解復原步驟。 檢查僅在 Anthropic API 上執行。在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry、[AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 和 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)後方或自訂 `ANTHROPIC_BASE_URL` 後方，您的提供者或閘道定義模型名稱，所以 Claude Code 會不檢查地傳遞任何字串。檢查也不涵蓋 `--model` 旗標、`ANTHROPIC_MODEL` 環境變數或 `model` 設定；在那裡輸入錯誤的值會在第一個請求時產生[所選模型有問題](https://code.claude.com/docs/zh-TW/errors#theres-an-issue-with-the-selected-model)。 當請求的模型有排定的淘汰日期或自動重新對應到較新版本時，Claude Code 會顯示一個警告，其中命名了請求的模型。互動式會話會將其顯示為啟動通知。從 v2.1.182 起，當使用預設文字輸出格式時，相同的警告會在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中寫入 stderr。檢查也涵蓋在[子代理 frontmatter](https://code.claude.com/docs/zh-TW/sub-agents) 中設定的 `model`。對於 `--output-format json` 和 `stream-json`，stderr 警告會被抑制；改為從[結果訊息](https://code.claude.com/docs/zh-TW/headless#get-structured-output)的 `modelUsage` 欄位讀取實際模型。 使用範例：

```
# 使用 Opus 啟動
claude --model opus

# 在會話期間切換到 Sonnet
/model sonnet

```

設定檔範例：

```
{
    "permissions": {
        ...
    },
    "model": "opus"
}

```

## 限制模型選擇

企業管理員可以在[受管理或政策設定](https://code.claude.com/docs/zh-TW/settings#settings-files)中使用 `availableModels` 來限制使用者可以選擇的模型。項目符合模型系列（例如 `sonnet`）、版本前綴（例如 `claude-sonnet-4-5`）或完整模型 ID（例如 `claude-sonnet-4-5-20250929`）。 設定 `availableModels` 後，允許清單適用於使用者可以指定模型的每個位置：

- **主要會話模型** ：`/model`、`--model` 旗標、`ANTHROPIC_MODEL` 環境變數、`model` 設定，以及[恢復會話](https://code.claude.com/docs/zh-TW/model-config#setting-your-model)時還原的模型
- **別名解析** ：`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL` 和 `ANTHROPIC_DEFAULT_FABLE_MODEL` 環境變數無法將允許的別名重新導向到清單外的模型
- **快速模式** ：`/fast` 在隱含切換到清單外的 Opus 模型時拒絕切換，並顯示訊息「不在您組織的允許模型中」
- **子代理模型** ：[子代理](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model) frontmatter 中的 `model` 欄位、Agent 工具的 `model` 參數、`CLAUDE_CODE_SUBAGENT_MODEL`，以及在 v2.1.197 及更早版本上，`/agents` 精靈中的模型選擇器
- **技能和命令模型** ：[技能和命令](https://code.claude.com/docs/zh-TW/skills)中的 `model` frontmatter
- **顧問模型** ：已設定的 [`advisorModel`](https://code.claude.com/docs/zh-TW/advisor) 設定和 `--advisor` 旗標
- **背景代理模型** ：在[分派選擇器](https://code.claude.com/docs/zh-TW/agent-view)中選擇的模型

在 Anthropic API 和 [AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 上，模型系列別名 `opus`、`sonnet`、`haiku` 或 `fable` 解析為允許清單允許的其系列的最新版本。當允許清單固定特定版本時，例如 `["sonnet", "claude-opus-4-6"]`，`/model opus` 和 `--model opus` 都會選擇 Claude Opus 4.6（最新允許的 Opus），並顯示一個通知，命名所要求和替代的模型。在 v2.1.205 之前，其最新發佈版本在清單外的別名會被拒絕或替換，就像任何其他被阻止的選擇一樣，即使清單允許較舊版本。 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 [Mantle](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint) 使用提供者特定的部署 ID 而不是 Anthropic 模型 ID，因此被阻止的別名在那裡遵循下面的拒絕和替換行為。 Claude Code 根據模型的設定位置處理任何其他被阻止的選擇：

- **`/model`**：切換被拒絕並出現錯誤
- **`--model`旗標、`ANTHROPIC_MODEL` 或 `model` 設定**：該值在啟動時被替換為警告，命名所要求和替代的模型，會話會在預設模型上啟動
- **子代理、技能或命令覆蓋** ：覆蓋會回退到繼承或預設模型，而不是使請求失敗
- **`advisorModel`設定** ：該會話的顧問被停用
- **`--advisor`旗標** ：Claude Code 在啟動時以錯誤退出

排除的模型會從 `/model` 選擇器中隱藏。清單中沒有內建選擇器列的完整模型 ID（例如清單固定的較舊版本）會在 `/model` 選擇器中顯示為其自己的標記列。在 v2.1.199 之前，此類 ID 只能透過輸入 `/model <id>` 選擇。 Claude Code 代表您進行的模型變更會以相同方式檢查：

- **[後備模型鏈](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains)** ：清單外的元素會被捨棄
- **Plan Mode 升級** ：在 Anthropic API 和 AWS 上的 Claude Platform 上，升級（例如 [`opusplan`](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting)）到排除的模型會使用升級系列的最新允許版本。在具有提供者特定模型 ID 的提供者上，以及當沒有版本被允許時，升級會被跳過，計畫會在會話的模型上繼續
- **[自動模型後備](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)** ：目標被排除的後備不會執行，因此標記的請求會以拒絕結束
- **[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)** ：當會話之後執行的模型在允許清單外時，啟用快速模式會被拒絕

```
{
  "availableModels": ["sonnet", "haiku"]
}

```

### 表面覆蓋

每個表面都會強制執行它接收的允許清單。哪個傳遞機制到達每個表面不同：

| 傳遞機制                                                                                       | CLI 和 IDE | 桌面本機會話 | Web、行動和雲端會話 | Agent SDK 和非互動式 | Cowork             |
| ---------------------------------------------------------------------------------------------- | ---------- | ------------ | ------------------- | -------------------- | ------------------ |
| 來自管理員主控台的[伺服器管理設定](https://code.claude.com/docs/zh-TW/server-managed-settings) | 強制執行   | 強制執行     | 強制執行            | 強制執行             | 未傳遞             |
| [MDM 或受管理設定檔](https://code.claude.com/docs/zh-TW/settings#settings-files)               | 強制執行   | 強制執行     | 未傳遞              | 強制執行             | 在部署位置強制執行 |

- 雲端會話在[網路上的 Claude Code](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 或桌面應用程式中執行，在 Anthropic 管理的 VM 上執行：部署到您的裝置的設定無法到達它們，因此請透過伺服器管理設定傳遞允許清單。雲端會話中的中途會話模型切換在要求的模型被允許清單排除時被拒絕。會話建立時的伺服器端拒絕適用於[組織模型限制](https://code.claude.com/docs/zh-TW/model-config#organization-model-restrictions)，而不是 `availableModels` 設定鍵。
- Cowork 是 Claude 桌面應用程式中的代理工作標籤，不是 Claude Code 表面，根據設計不接收伺服器管理設定。受管理設定檔在會話執行的位置存在時適用於 Cowork 會話；遠端 Cowork 會話在 Anthropic 管理的 VM 上執行，其中不存在裝置部署的檔案。
- [第三方提供者](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)（例如 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 [AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)）上的會話不接收伺服器管理設定，因此請在那裡透過 MDM 或受管理設定檔傳遞允許清單。
- 伺服器管理傳遞也需要會話使用組織登入或直接設定的 API 金鑰進行驗證。只透過 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings#available-settings) 指令碼產生金鑰的艦隊應透過 MDM 或受管理設定檔傳遞允許清單。
- 桌面代碼標籤也裝載 [SSH 會話](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions)，它們從執行所在的遠端主機讀取受管理設定檔。請參閱[桌面受管理設定](https://code.claude.com/docs/zh-TW/desktop#managed-settings)。
- claude.ai 和桌面應用程式中的模型選擇器會隱藏或灰顯您組織的允許清單排除的模型。選擇器狀態是使用者的便利；強制執行發生在會話中。

### 預設模型行為

根據預設，模型選擇器中的「預設」選項不受 `availableModels` 影響，除非也設定了 [`enforceAvailableModels`](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model)。單獨使用 `availableModels` 會保持「預設」可用，根據帳戶的[執行時預設](https://code.claude.com/docs/zh-TW/model-config#default-model-setting)解析為系統預設值。如果該預設值是您想要限制的模型，也請設定 `enforceAvailableModels`。 空的 `availableModels` 陣列永遠不會啟用「預設」模型強制執行：使用 `availableModels: []` 時，具名模型選擇會被阻止，但帳戶類型的「預設」模型無論 `enforceAvailableModels` 為何都保持可用。

### 對「預設」模型強制執行允許清單

在受管理設定中將 `enforceAvailableModels: true` 與非空的 `availableModels` 一起設定，以將允許清單擴展到「預設」選項。這需要 Claude Code v2.1.175 或更新版本。

```
{
  "availableModels": ["sonnet", "haiku"],
  "enforceAvailableModels": true
}

```

「預設」選項解析為帳戶類型預設值，或當管理員設定了[組織預設模型](https://code.claude.com/docs/zh-TW/model-config#organization-default-model)時解析為該模型。當該模型不在允許清單中時，「預設」選項會改為解析為第一個 `availableModels` 項目，該項目命名允許的、可用的模型，而 `/model` 選擇器的「預設」列會顯示該模型。這適用於到達預設值的每個位置：會話啟動、在 `/model` 中選擇「預設」、[後備模型鏈](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains)中的 `"default"` 關鍵字，以及排除選擇被捨棄時使用的後備。 當 `availableModels` 未設定或為空時，`enforceAvailableModels` 無效：使用 `availableModels: []` 時，帳戶類型的「預設」模型保持可用，因此該設定無法將使用者鎖定在每個模型之外。當 `availableModels` 非空但沒有項目解析為允許的、可用的模型時，強制執行會降級，「預設」會回退到帳戶類型預設值，警告僅在 `--debug` 下可見。在清單中保留至少一個保證可用的項目以避免這種情況。 在[最高優先順序受管理來源](https://code.claude.com/docs/zh-TW/settings#settings-precedence)中部署兩個鍵：管理員部署的受管理來源不會合併，因此放在受管理設定檔中的一對在管理員主控台傳遞任何設定時會被忽略。

### 控制使用者執行的模型

`model` 設定是初始選擇，而非強制執行。它設定會話啟動時哪個模型處於活動狀態，但使用者仍然可以開啟 `/model` 並選擇「預設」，這會解析為系統的[執行時預設](https://code.claude.com/docs/zh-TW/model-config#default-model-setting)，無論 `model` 設定為何，除非 [`enforceAvailableModels`](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model) 重新導向它。 若要完全控制模型體驗，請結合這些設定：

- **`availableModels`**：限制使用者可以切換到的具名模型
- **`enforceAvailableModels`**：將`availableModels` 允許清單擴展到「預設」選項，因此「預設」無法解析為清單外的模型
- **`model`**：設定會話啟動時的初始模型選擇
- **`ANTHROPIC_DEFAULT_SONNET_MODEL`**/**`ANTHROPIC_DEFAULT_OPUS_MODEL`**/**`ANTHROPIC_DEFAULT_HAIKU_MODEL`**/**`ANTHROPIC_DEFAULT_FABLE_MODEL`**：控制「預設」選項以及`sonnet` 、`opus`、`haiku` 和 `fable` 別名解析為什麼

此範例在 Sonnet 4.5 上啟動使用者，將選擇器限制為 Sonnet 和 Haiku，並確保「預設」解析為允許清單上的模型，而不是層級預設值：

```
{
  "model": "claude-sonnet-4-5",
  "availableModels": ["claude-sonnet-4-5", "haiku"],
  "enforceAvailableModels": true,
  "env": {
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-5"
  }
}

```

沒有 `enforceAvailableModels` 或 `env` 區塊，在選擇器中選擇「預設」的使用者會獲得其層級的最新版本，繞過 `model` 和 `availableModels` 中的版本固定。這兩個設定涵蓋不同的範圍：`enforceAvailableModels` 使「預設」遵守允許清單，而 `env` 區塊固定允許的別名（例如 `sonnet`）解析為哪個版本。當限制模型系列就足夠時，單獨使用 `enforceAvailableModels`；當您還需要固定特定版本時，新增 `env` 區塊。

### 合併行為

當[最高優先順序受管理設定來源](https://code.claude.com/docs/zh-TW/server-managed-settings#settings-precedence)定義 `availableModels` 時，該清單單獨適用：使用者、專案或本機設定中的項目無法擴展它，而管理員部署的受管理來源不會彼此合併，因此在伺服器管理設定傳遞任何鍵時，部署在受管理設定檔中的清單會被忽略。否則，來自使用者、專案和本機設定的清單會像其他陣列設定一樣[連接和去重](https://code.claude.com/docs/zh-TW/settings#settings-precedence)。自 Claude Code v2.1.175 起，受管理清單會取代較低優先順序的項目；較早版本會合併它們。 在有效清單中，命名系列中特定模型的項目（無論是版本前綴還是完整模型 ID）會停用該系列的萬用字元項目：`["sonnet", "claude-sonnet-4-5"]` 只允許 Sonnet 4.5 版本，而不是每個 Sonnet 模型。

### Mantle 模型 ID

當[Amazon Bedrock Mantle 端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint)啟用時，`availableModels` 中以 `anthropic.` 開頭的項目會作為自訂選項新增到 `/model` 選擇器，並路由到 Mantle 端點。這是[為第三方部署固定模型](https://code.claude.com/docs/zh-TW/model-config#pin-models-for-third-party-deployments)中描述的別名符合的例外。該設定仍然將選擇器限制為列出的項目，而 Mantle ID 嵌入系列名稱，因此它計為特定項目並停用該系列的萬用字元：在任何 Mantle ID 旁邊，列出您想要保持可選擇的版本前綴或完整 ID。請參閱[合併行為](https://code.claude.com/docs/zh-TW/model-config#merge-behavior)。

### 組織模型限制

Claude Enterprise 計畫上的組織管理員透過在 claude.ai 管理員主控台中停用個別模型來限制成員可以執行的模型。此限制在 Claude Code 驗證時與帳戶的權利一起傳遞，與設定中的任何 `availableModels` 清單分開，而伺服器在建立會話時獨立強制執行相同的限制。需要 Claude Code v2.1.187 或更新版本。 當成員登入或使用自己的 API 金鑰時，限制適用。組織範圍的認證（例如組織服務金鑰）未與使用者相關聯，因此限制不適用於它們。 Claude Console 沒有模型限制控制。沒有 Claude Enterprise 計畫的組織（包括其成員透過 Anthropic API 進行驗證的組織）改為在[受管理設定](https://code.claude.com/docs/zh-TW/settings#settings-files)中使用 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 限制模型，新增 [`enforceAvailableModels`](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model) 以涵蓋「預設」選項。這些設定由 Claude Code 本身強制執行，而不是由伺服器強制執行。 受限制的模型會從 `/model` 選擇器中隱藏。使用 `--model`、`ANTHROPIC_MODEL` 環境變數或 `model` 設定按名稱選擇它會顯示通知 `Model "<name>" is restricted by your organization's settings. Using <model> instead.`，會話會在允許的模型上啟動。為受限制的模型輸入 `/model <name>` 會被拒絕，並顯示 `Model '<name>' is restricted by your organization's settings. Run /model to choose a different model.`，會話會保持其目前模型。 [模型系列別名](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)（例如 `opus`）解析為組織允許的其系列的最新版本，具有相同的替代通知。`/model <alias>` 只有在其系列的每個版本都被限制時才會被拒絕；使用 `--model`、`ANTHROPIC_MODEL` 或 `model` 設定設定的別名在該情況下仍在啟動時被替換。在 v2.1.205 之前，系列別名是根據其最新發佈版本單獨進行替代或拒絕的，即使允許了較舊版本。 限制適用於組織範圍或按角色：

- 在組織層級停用模型會將其移除給每個成員。
- 角色級別存取為不同的自訂角色授予不同的模型，持有多個角色的成員可以使用其任何角色授予的模型。
- Haiku 模型始終可用，無法停用，因此每個成員至少保留一個可用模型。
- 存取變更在約一分鐘內對新請求生效；`/model` 選擇器在下次會話啟動時反映它。

這兩個限制組合：只有當模型被 `availableModels` 允許且未被組織限制時，它才可選擇。組織限制會傳遞到 Anthropic API 和 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)部署上的會話。Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 AWS 上的 Claude Platform 上的會話不接收它們，因此請改為在這些提供者上使用 `availableModels`。

## 組織預設模型

Claude Enterprise 計畫上的組織管理員可以從 claude.ai 管理員主控台為 Claude Code 成員設定預設模型，適用於整個組織或按自訂角色。設定後，「預設」選項會解析為該模型，而不是[帳戶類型預設](https://code.claude.com/docs/zh-TW/model-config#default-model-setting)。需要 Claude Code v2.1.196 或更新版本。 `/model` 選擇器中的「預設」列會顯示組織預設值的名稱，標籤為「Org default」。無論管理員是為整個組織還是為您的角色設定預設值，標籤都會讀取「Org default」。角色預設值涵蓋該自訂角色的成員，並優先於組織範圍的預設值；當您的多個角色設定不同的預設值時，最強大的模型適用。 組織預設值是起點，而非限制，任何其他模型選擇都優先於它：

- `--model` 旗標和 `ANTHROPIC_MODEL` 環境變數
- [受管理設定](https://code.claude.com/docs/zh-TW/settings#settings-files)中的 `model` 值或透過 `--settings` 提供
- 您的使用者、專案或本機設定中的 `model` 值，包括您使用 `/model` 儲存的模型

管理員也可以配置組織預設值以覆蓋使用者選擇。啟用覆蓋後，它優先於使用者、專案和本機設定中的 `model` 值，因此您使用 `/model` 儲存的模型適用於目前會話，組織預設值在下次啟動時返回。當您的選擇不同時，`/model` 會顯示 `Your organization's default (<model>) applies on restart`。`--model` 旗標、`ANTHROPIC_MODEL`、受管理設定和 `--settings` 即使啟用覆蓋也仍然優先。覆蓋可用於有限的組織集合；詢問您的 Anthropic 帳戶團隊有關可用性。 若要限制成員可以選擇的模型，請改用[組織模型限制](https://code.claude.com/docs/zh-TW/model-config#organization-model-restrictions)或 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)。 Claude Code 在啟動時讀取組織預設值一次，因此管理員在會話中途變更的預設值在下次啟動時生效。 當組織預設值不覆蓋使用者選擇時，管理員變更後的第一次互動式啟動會從您的使用者設定中清除 `model` 鍵一次，以便新預設值適用。它不改變檔案中的任何其他內容，您在該啟動後使用 `/model` 儲存的模型會被保留。 組織預設值在被採用前會通過與任何其他「預設」模型相同的限制檢查：

- [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 本身永遠不會限制「預設」選項，因此允許清單外的組織預設值仍然適用。當也設定了 [`enforceAvailableModels`](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model) 時，允許清單外的組織預設值會重新對應到第一個允許清單項目，就像任何其他「預設」一樣
- [組織模型限制](https://code.claude.com/docs/zh-TW/model-config#organization-model-restrictions)拒絕的組織預設值會被替換為其系列中最新的允許模型，或當該系列的每個版本都被限制時被替換為較低成本的系列
- 對您的帳戶完全不可用的組織預設值，例如[零資料保留](https://code.claude.com/docs/zh-TW/zero-data-retention)下的 Fable 5，會被跳過，「預設」選項會解析為帳戶類型預設值

自 v2.1.199 起，當組織預設值是與您帳戶類型的常用預設值不同的模型系列時，`/model` 選擇器會為該常用系列保留一個單獨的列，因此您仍然可以為會話切換到它。在 v2.1.196 至 v2.1.198 中，該列在選擇器中缺失。 組織預設值會傳遞到使用 Anthropic API 進行驗證的會話。[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)部署、Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 [AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 上的會話不接收它。若要在這些部署上設定預設值，請改用[受管理設定](https://code.claude.com/docs/zh-TW/settings#settings-files)中的 `model` 鍵。

## 組織努力限制

Claude Enterprise 計畫上的組織管理員可以為每個自訂角色設定每個模型的最大[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)，以及角色級別[組織模型限制](https://code.claude.com/docs/zh-TW/model-config#organization-model-restrictions)。超過上限的等級不會在 `/effort` 選擇器中提供，使用 `--effort` 或 `/effort` 命名更高等級會改為在上限處執行。在互動式會話和純文字 `--print` 執行中，警告會命名所要求和應用的等級；使用 `json` 或 `stream-json` 輸出或在背景代理中，限制會無聲地應用。上限是按模型的，因此切換模型可以改變哪些等級可用。當您的多個角色授予相同的模型時，最寬鬆的上限適用。需要 Claude Code v2.1.195 或更新版本。 努力限制與[組織模型限制](https://code.claude.com/docs/zh-TW/model-config#organization-model-restrictions)一起傳遞，並遵循相同的提供者可用性：Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 [AWS 上的 Claude Platform](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 上的會話不接收它們。

## 特殊模型行為

### `default` 模型設定

`default` 的行為取決於您的帳戶類型：

- **Max、Team Premium、Enterprise 隨用隨付和 Anthropic API** ：預設為 Opus 4.8
- **AWS 上的 Claude Platform、Amazon Bedrock 和 Google Cloud 的 Agent Platform** ：預設為 Opus 4.8
- **Pro、Team Standard 和 Enterprise 訂閱席位** ：預設為 Sonnet 5
- **Microsoft Foundry** ：預設為 Sonnet 4.5

Enterprise 隨用隨付是指按使用量計費而非按訂閱席位計費的 Enterprise 組織。 在 v2.1.207 之前，`default` 在 AWS 上的 Claude Platform 上解析為 Opus 4.7，在 Amazon Bedrock 和 Google Cloud 的 Agent Platform 上解析為 Sonnet 4.5。 當管理員設定了[組織預設模型](https://code.claude.com/docs/zh-TW/model-config#organization-default-model)時，`default` 會解析為該模型，而不是上述帳戶類型預設值。需要 Claude Code v2.1.196 或更新版本。 當受管設定[強制執行 Default 模型的允許清單](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model)且帳戶類型預設不在 `availableModels` 中時，`default` 會解析為強制執行的 Default，而不是上述帳戶類型預設。當兩者都適用時，組織預設值首先取代帳戶類型預設值，然後強制執行適用於它：允許清單上的組織預設值會被保留，而清單外的會解析為強制執行的 Default。 Fable 5 不是任何帳戶類型的預設模型。會話僅在您選擇 Fable 5 後才使用它，使用 `/model fable`、`model` 設定或 `best` 別名（其中 Fable 5 可用）。使用 `/model` 選擇它會將其儲存為您使用者設定中的選定模型，因此後續會話會在 Fable 5 上啟動，直到您變更模型。

### `opusplan` 模型設定

`opusplan` 模型別名提供了一種自動化的混合方法：

- **在 Plan Mode 中** ：使用 `opus` 進行複雜推理和架構決策
- **在執行模式中** ：自動切換到 `sonnet` 進行程式碼生成和實現

這為您提供了兩全其美的方案：Opus 優越的推理能力用於計畫，Sonnet 的效率用於執行。 Plan Mode Opus 階段使用與 `opus` 模型設定相同的 context window。在訂閱層級上，Opus 會[自動升級到 1M context](https://code.claude.com/docs/zh-TW/model-config#extended-context)，`opusplan` 在 Plan Mode 中也會獲得升級。若要在您不在自動升級層級上時強制兩個階段都使用 1M context，請將模型設定為 `opusplan[1m]`。 當 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 排除最新的 Opus 但允許較舊版本時，例如 `["sonnet", "claude-opus-4-6"]`，`opusplan` 會為計畫使用最新允許的 Opus，並且僅在排除每個 Opus 時才保持在 Sonnet 上。通常會在 Plan Mode 中升級到 Sonnet 的 Haiku 會話同樣會使用最新允許的 Sonnet，並且僅在排除每個 Sonnet 時才保持在 Haiku 上。在 v2.1.205 之前，當排除升級系列的最新版本時，Plan Mode 會保持在會話的模型上，即使允許清單允許較舊版本。 較舊允許版本的替換適用於 Anthropic API 和 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws)。在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和 Mantle 上，其部署使用提供者特定的模型 ID，當升級模型被排除時，Plan Mode 會保持在會話的模型上。 如需混合方法，其中 Claude 在任務中途決定何時諮詢第二個模型，而不是在計畫邊界處切換，請參閱 [advisor tool](https://code.claude.com/docs/zh-TW/advisor)。

### 回退模型鏈

當主要模型過載、不可用或傳回另一個不可重試的伺服器錯誤時，Claude Code 可以切換到回退模型，而不是使請求失敗。驗證、計費、速率限制、請求大小和傳輸錯誤永遠不會觸發切換；這些遵循其正常的重試和錯誤處理。 配置一個或多個回退模型，Claude Code 會按順序嘗試它們，在切換時顯示通知。切換僅持續目前輪次，因此您的下一條訊息會再次首先嘗試主要模型。鏈在重複移除後限制為三個模型，額外項目會被忽略。 使用 `--fallback-model` 旗標為一個會話設定鏈，該旗標接受逗號分隔的清單：

```
claude --fallback-model sonnet,haiku

```

若要在會話間持續保存鏈，請在 [settings](https://code.claude.com/docs/zh-TW/settings) 中設定 `fallbackModel` 為陣列：

```
{
  "fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5"]
}

```

`--fallback-model` 旗標優先於 `fallbackModel` 設定。每個元素接受模型名稱或別名，`"default"` 會展開為預設模型。 兩種情況會導致元素被跳過：

- **不可用的模型** ：無法到達的模型，例如在設定中固定的已停用模型，會被跳過，Claude Code 會繼續到下一個元素。
- **超出允許清單** ：不被 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 允許的元素在讀取鏈時會被刪除，永遠不會被嘗試。

### 自動模型回退

本節涵蓋來自 Fable 5 的基於內容的回退。如需模型過載或不可用時的基於可用性的回退，請參閱 [Fallback model chains](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains)。 Fable 5 使用網路安全和生物學內容的安全分類器執行。當分類器標記請求時，Claude Code 會在您提供者的預設 Opus 模型上重新執行該請求，並在記錄中顯示通知。在 Anthropic API、[LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway) 部署和 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 上，該模型是 Opus 4.8。在 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 上，它是 Opus 4.7，除非您將 [`opus` 別名](https://code.claude.com/docs/zh-TW/model-config#environment-variables)指向另一個模型。 會話隨後在該 Opus 模型上繼續。若要返回 Fable 5，請執行 `/model fable`。 回退目標會根據 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 進行檢查。當它被阻止時，不會發生回退。拒絕會作為正常錯誤出現，會話的模型保持不變。

#### 檢查觸發回退的原因

回退可以在會話的第一個請求上觸發，在您發送任何不尋常的內容之前，因為第一個請求會攜帶工作區上下文，例如您的 CLAUDE.md 內容和 git 狀態。包含安全或生物學材料的儲存庫可以單獨在該上下文上觸發分類器。 若要檢查自訂是否是觸發器，請使用 `claude --safe-mode` 啟動會話，這會禁用自訂，例如 CLAUDE.md、skills、MCP 伺服器和 hooks。Git 狀態和目錄名稱不是自訂，仍然包含在內。

#### 在切換前詢問

若要決定每次請求被標記時發生的情況，而不是自動切換，請執行 `/config` 並關閉「當訊息被標記時切換模型」。標記的請求隨後會暫停會話，有兩個選項：切換到 Opus 模型，或編輯提示並在 Fable 5 上重試。 某些情況的行為不同：

- 如果兩個模型都標記相同的請求，您可以編輯提示並重試，或啟動新會話。
- 在行動裝置 [Claude Code on the web](https://code.claude.com/docs/zh-TW/claude-code-on-the-web) 會話上，不支援編輯和重試。切換模型，或從桌面瀏覽器或桌面應用程式繼續會話。
- 在 [non-interactive mode](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 和無法顯示提示的 SDK 整合中，標記的請求以拒絕結束輪次。
- 當回退目標被 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 阻止時，不會顯示提示。標記的請求以拒絕結束，與目標被阻止時的自動回退相同。

#### 在 Bedrock、Agent Platform 和 Foundry 上啟用回退

在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 和 [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 上，模型 ID 是提供者特定的，因此自動回退僅在 Claude Code 可以識別涉及的兩個模型時運作：

- Claude Code 必須將目前模型識別為 Fable 5：模型 ID 包含 `claude-fable-5`、符合 `ANTHROPIC_DEFAULT_FABLE_MODEL` 的值，或使用 [`modelOverrides`](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version) 對應。
- 回退目標必須解析為 Opus 模型：`ANTHROPIC_DEFAULT_OPUS_MODEL` 的值（如果設定），否則提供者模型清單中的 Opus 4.8 項目。

如果任一模型無法識別，Claude Code 不會自動切換。標記的請求以拒絕訊息結束，您可以使用 [`/model`](https://code.claude.com/docs/zh-TW/model-config#setting-your-model) 切換模型並重試。若要在這些提供者上啟用自動回退，請將 `ANTHROPIC_DEFAULT_FABLE_MODEL` 設定為您的 Fable 5 模型 ID，並將 `ANTHROPIC_DEFAULT_OPUS_MODEL` 設定為您的 Opus 4.8 模型 ID。

#### 安全研究和生物學工作負載

進攻性安全或生物學中的工作負載，包括滲透測試、Capture the Flag (CTF) 練習和生物學相鄰程式碼庫，經常觸發回退，通常在第一個請求上。對於實質性生物學工作，預期幾乎所有請求都會重新路由。 這是這些領域的預期路由，不是帳戶標記。如果您的組織需要 Fable 級別的能力來進行此工作，請詢問您的 Anthropic 帳戶團隊有關受信任存取計畫。

### 調整努力等級

[努力等級](https://platform.claude.com/docs/en/build-with-claude/effort)控制自適應推理，讓模型根據任務複雜性決定是否以及在每一步上思考多少。較低的努力對於直接的任務更快且更便宜，而較高的努力為複雜問題提供更深入的推理。 可用的努力等級取決於模型。此處未列出的模型不支援努力：

| 模型                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 等級                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Fable 5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `low`、`medium`、`high`、`xhigh`、`max` |
| Sonnet 5、Opus 4.8 和 Opus 4.7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `low`、`medium`、`high`、`xhigh`、`max` |
| Opus 4.6 和 Sonnet 4.6                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `low`、`medium`、`high`、`max`          |
| 如果您設定活動模型不支援的等級，Claude Code 會回退到您設定的等級處或以下的最高支援等級。例如，`xhigh` 在 Opus 4.6 上執行為 `high`。您的組織也可以限制模型可用的等級；請參閱[組織努力限制](https://code.claude.com/docs/zh-TW/model-config#organization-effort-limits)。 Fable 5、Sonnet 5、Opus 4.8、Opus 4.6 和 Sonnet 4.6 上的預設努力為 `high`，Opus 4.7 上的預設努力為 `xhigh`。 當您首次執行 Fable 5、Opus 4.8 或 Opus 4.7 時，Claude Code 會應用該模型的預設努力，即使您之前為另一個模型設定了不同的等級：Fable 5 和 Opus 4.8 上的 `high`，以及 Opus 4.7 上的 `xhigh`。執行 `/effort` 以在切換後選擇不同的等級。該預設值在會話間保持，直到您進行明確的努力選擇，例如在互動式會話中執行 `/effort` 或使用 `--effort` 啟動。在 [non-interactive mode](https://code.claude.com/docs/zh-TW/headless) 中使用 `/effort` 設定的等級，使用 `-p` 旗標，僅適用於目前會話，不會儲存為您的預設值。非互動式 `/effort` 也無法釋放上述模型預設值保持：在 Fable 5、Opus 4.8 和 Opus 4.7 上，它報告 `Not applied`，會話保持在模型的預設努力，因此改為在啟動時傳遞 `--effort`。`max` 提供最深入的推理，對 token 支出沒有限制，並且僅適用於目前會話，除非透過 `CLAUDE_CODE_EFFORT_LEVEL` 環境變數設定。 `/effort` 選單也提供 `ultracode`。Ultracode 是 Claude Code 設定而非模型努力等級：它向模型發送 `xhigh`，並額外讓 Claude 為實質性任務協調[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)。它僅適用於目前會話。 您可以透過以下任何方式開啟 ultracode： |                                         |

- **`/effort`**：執行`/effort ultracode` ，或從選單中選擇它
- **`--effort`旗標** ：使用 `claude --effort ultracode` 啟動，這會以 `xhigh` 努力和 ultracode 開啟會話
- **`--settings`或 Agent SDK 控制請求** ：傳遞 `"ultracode": true`。[`applyFlagSettings()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#applyflagsettings) 請求也接受 `effortLevel: "ultracode"`

將 `ultracode` 傳遞給 `--effort` 旗標或 Agent SDK `effortLevel` 值需要 Claude Code v2.1.203 或更新版本。在 v2.1.203 之前，`--effort ultracode` 列印 `Unknown --effort value 'ultracode'`，會話以預設努力啟動。 持續的 `effortLevel` 設定和 `CLAUDE_CODE_EFFORT_LEVEL` 環境變數不接受 `ultracode`。 當 ultracode 不可用時，例如當[工作流程被關閉](https://code.claude.com/docs/zh-TW/workflows#turn-workflows-off)時，`--effort ultracode` 僅設定 `xhigh` 努力。

#### 選擇努力等級

每個等級都在 token 支出和能力之間進行權衡。預設值適合大多數編碼任務；當您想要不同的平衡時進行調整。

| 等級                                                                     | 何時使用                                                                                                                                     |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `low`                                                                    | 保留用於短期、範圍有限、延遲敏感且不是智能敏感的任務                                                                                         |
| `medium`                                                                 | 減少成本敏感工作的 token 使用，可以權衡一些智能                                                                                              |
| `high`                                                                   | 平衡 token 使用和智能。Fable 5、Sonnet 5、Opus 4.8、Opus 4.6 和 Sonnet 4.6 上的預設值                                                        |
| `xhigh`                                                                  | 更深入的推理，token 支出更高。Opus 4.7 上的預設值                                                                                            |
| `max`                                                                    | 可以改善困難任務的效能，但可能顯示遞減回報，容易過度思考。在廣泛採用前進行測試                                                               |
| `ultracode`                                                              | 一個 Claude Code 設定，為每個實質性任務規劃[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)，每條訊息進行 `xhigh` 推理。僅限會話 |
| 努力量表按模型進行校準，因此相同的等級名稱在模型之間不代表相同的基礎值。 |                                                                                                                                              |

#### 使用 ultrathink 進行一次性深入推理

在您的提示中的任何地方包含 `ultrathink` 以請求在該輪上進行更深入的推理，而不改變您的會話努力設定。Claude Code 識別該關鍵字並新增一個上下文指令。發送到 API 的努力等級保持不變。其他短語如「think」、「think hard」和「think more」會作為普通提示文本傳遞，不被識別為關鍵字。

#### 設定努力等級

您可以透過以下任何方式改變努力：

- **`/effort`**：執行`/effort` 不帶引數以開啟互動式滑塊，執行 `/effort` 後跟等級名稱以直接設定，或執行 `/effort auto` 以重設為模型預設值
- **在`/model` 中**：選擇模型時使用左/右箭頭鍵調整努力滑塊
- **`--effort`旗標** ：在啟動 Claude Code 時傳遞等級名稱以為單一會話設定
- **環境變數** ：設定 `CLAUDE_CODE_EFFORT_LEVEL` 為等級名稱或 `auto`
- **設定** ：在設定檔中設定 `effortLevel` 為 `low`、`medium`、`high` 或 `xhigh`。`max` 和 `ultracode` 是[僅限會話](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)，此處不接受
- **Skill 和 subagent frontmatter** ：在 [skill](https://code.claude.com/docs/zh-TW/skills#frontmatter-reference) 或 [subagent](https://code.claude.com/docs/zh-TW/sub-agents#supported-frontmatter-fields) markdown 檔案中設定 `effort` 以在該 skill 或 subagent 執行時覆蓋努力等級

環境變數優先於所有其他方法，然後是您配置的等級，然後是模型預設值。Frontmatter 努力在該 skill 或 subagent 活動時適用，覆蓋會話等級但不覆蓋環境變數。 當選擇支援的模型時，努力滑塊會出現在 `/model` 中。目前的努力等級也會顯示在標誌和微調器旁邊，例如「with low effort」，因此您可以確認哪個設定處於活動狀態，而無需開啟 `/model`。

#### 自適應推理和固定思考預算

自適應推理使思考在每一步上都是可選的，因此 Claude 可以更快地回應常規提示，並為受益於思考的步驟保留更深入的思考。如果您想要 Claude 比目前等級產生的更頻繁或更少地思考，您可以直接在您的提示或 `CLAUDE.md` 中說明；模型在其努力設定範圍內回應該指導。 Fable 5、Sonnet 5 和 Opus 4.7 及更新版本始終使用自適應推理。固定思考預算模式和 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` 不適用於它們。 在 Opus 4.6 和 Sonnet 4.6 上，您可以設定 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` 以恢復到由 `MAX_THINKING_TOKENS` 控制的先前固定思考預算。請參閱[環境變數](https://code.claude.com/docs/zh-TW/env-vars)。

### 擴展思考

擴展思考是 Claude 在回應前發出的推理。在支援[自適應推理](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)的模型上，努力等級是控制發生多少思考的主要控制項；下面的設定會開啟或關閉思考，並控制其顯示方式。

| 控制項                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 如何設定                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 目前會話的切換                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 在 macOS 上按 `Option+T` 或在 Windows 和 Linux 上按 `Alt+T`                                                                                                                                                                                                                                                                                                                                        |
| 設定全域預設值                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 執行 `/config` 並切換思考模式。儲存為 `~/.claude/settings.json` 中的 `alwaysThinkingEnabled`                                                                                                                                                                                                                                                                                                       |
| 無論努力如何禁用                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 設定 [`MAX_THINKING_TOKENS=0`](https://code.claude.com/docs/zh-TW/env-vars)，這會在 Anthropic API 上關閉思考，除了 Fable 5。在[第三方提供者](https://code.claude.com/docs/zh-TW/third-party-integrations)上，這會改為省略 `thinking` 參數，自適應推理模型可能仍然思考。其他值僅適用於[固定思考預算](https://code.claude.com/docs/zh-TW/model-config#adaptive-reasoning-and-fixed-thinking-budgets) |
| 思考無法在 Fable 5 上關閉。會話切換、`alwaysThinkingEnabled` 和 `MAX_THINKING_TOKENS=0` 在那裡沒有效果，Fable 5 根據努力等級決定每一步思考多少。 思考輸出預設為摺疊。按 `Ctrl+O` 以切換詳細模式並將推理視為灰色斜體文本。Anthropic API 上的互動式會話預設會收到編輯的思考區塊，因此如果您想要在展開時可用的完整摘要，請在[設定](https://code.claude.com/docs/zh-TW/settings)中設定 `showThinkingSummaries: true`。您需要為所有生成的思考 token 付費，即使它們被摺疊或編輯。 |                                                                                                                                                                                                                                                                                                                                                                                                    |

### 擴展 context

Fable 5、Sonnet 5、Opus 4.6 及更新版本和 Sonnet 4.6 支援[100 萬個 token 的 context window](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-window-sizes-by-model)，用於具有大型程式碼庫的長時間會話。 可用性因模型和計畫而異。在 Anthropic API 上，Fable 5、Sonnet 5、Opus 4.8 和 Opus 4.7 始終使用 1M window 執行。在 Max、Team 和 Enterprise 計畫上，Opus 會自動升級到 1M context，無需額外配置。這適用於 Team Standard 和 Team Premium 席位。Sonnet 4.6 搭配 1M context 不是自動升級的一部分，需要在每個訂閱計畫上進行[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)，包括 Max。

| 計畫                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Opus 搭配 1M context                                                                              | Sonnet 4.6 搭配 1M context                                                                        |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Max、Team 和 Enterprise                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 包含在訂閱中                                                                                      | 需要[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) |
| Pro                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 需要[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) | 需要[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) |
| API 和隨用隨付                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 完全存取                                                                                          | 完全存取                                                                                          |
| 若要完全禁用 1M context，請設定 `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`。這會從模型選擇器中移除 1M 模型變體。請參閱[環境變數](https://code.claude.com/docs/zh-TW/env-vars)。 1M context window 使用標準模型定價，超過 200K 的 token 無需額外費用。對於訂閱中包含擴展 context 的計畫，使用量仍由您的訂閱涵蓋。對於透過使用額度存取擴展 context 的計畫，token 會計入使用額度。 如果您的帳戶支援 1M context，該選項會出現在最新版本 Claude Code 的 `/model` 選擇器中。如果您看不到它，請嘗試重新啟動您的會話。 您也可以將 `[1m]` 後綴與模型別名或完整模型名稱一起使用： |                                                                                                   |                                                                                                   |

```
# 使用 opus[1m] 或 sonnet[1m] 別名
/model opus[1m]
/model sonnet[1m]

# 或將 [1m] 附加到完整模型名稱
/model claude-opus-4-8[1m]

```

#### Sonnet 5 context window

在 Anthropic API 上，Sonnet 5 始終使用 1M context window 執行。沒有 200K 變體，沒有可選擇的 `[1m]` 後綴，任何計畫都不需要使用額度。會話會在 window 填滿前自動壓縮，預設約在 967K 個 token 時；設定 [`CLAUDE_CODE_AUTO_COMPACT_WINDOW`](https://code.claude.com/docs/zh-TW/env-vars) 以選擇不同的閾值。 兩種配置會改為以 200K 計算 window，並在該邊界自動壓縮：

- **LLM gateway** ：當 `ANTHROPIC_BASE_URL` 指向[gateway](https://code.claude.com/docs/zh-TW/llm-gateway)時，Claude Code 無法驗證 1M 支援。若要使用完整的 window，請在模型選擇器中選擇 Sonnet 5 (1M context)，它會對應到 `sonnet[1m]`。
- **`CLAUDE_CODE_DISABLE_1M_CONTEXT=1`**：將 Sonnet 5 會話視為具有 200K window，適用於需要限制 context 的部署。

## 檢查您目前的模型

您可以在兩個地方查看您目前使用的模型：

- 在[狀態行](https://code.claude.com/docs/zh-TW/statusline)中（如果已配置）
- 在 `/status` 中，它也會顯示您的帳戶資訊

## 新增自訂模型選項

使用 `ANTHROPIC_CUSTOM_MODEL_OPTION` 將單一自訂項目新增到 `/model` 選擇器，而無需取代內建別名。這對於測試 Claude Code 預設不列出的模型 ID 很有用。對於 LLM 閘道部署，當設定 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` 時，Claude Code 可以從閘道的 `/v1/models` 端點填入選擇器，因此只有在探索被停用或未傳回您想要的模型時，才需要此變數。請參閱 [gateway model discovery](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#model-discovery)。 此範例設定所有三個變數以使閘道路由的 Opus 部署可選擇：

```
export ANTHROPIC_CUSTOM_MODEL_OPTION="my-gateway/claude-opus-4-8"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Opus via Gateway"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="Custom deployment routed through the internal LLM gateway"

```

自訂項目出現在 `/model` 選擇器的底部。`ANTHROPIC_CUSTOM_MODEL_OPTION_NAME` 和 `ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION` 是可選的。如果省略，模型 ID 會用作名稱，描述預設為 `Custom model (<model-id>)`。 Claude Code 會跳過在 `ANTHROPIC_CUSTOM_MODEL_OPTION` 中設定的模型 ID 的驗證，因此您可以使用您的 API 端點接受的任何字串。當設定 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 時，也要在允許清單中包含自訂模型 ID：自訂項目會從選擇器中篩選出來，對其進行 `--model` 選擇會被拒絕，就像任何其他被排除的模型一樣。嵌入家族名稱的自訂 ID（例如 `my-gateway/claude-opus-4-8`）會計為該家族的特定項目，並停用其萬用字元，因此也要列出您打算保持可選擇的版本。請參閱 [Merge behavior](https://code.claude.com/docs/zh-TW/model-config#merge-behavior)。

## 環境變數

您可以使用以下環境變數來控制別名對應到的模型名稱。每個值必須是完整的模型名稱，或您的 API 提供者的等效識別碼。

| 環境變數                                                                          | 描述                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_DEFAULT_FABLE_MODEL`                                                   | 用於 `fable` 的模型，以及 Claude Code 識別為 Fable 5 的模型 ID，用於第三方提供者上的[自動模型回退](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)                                                                                                                                                                                                     |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`                                                    | 用於 `opus` 的模型，或在 Plan Mode 活動時用於 `opusplan` 的模型。                                                                                                                                                                                                                                                                                                                |
| `ANTHROPIC_DEFAULT_SONNET_MODEL`                                                  | 用於 `sonnet` 的模型，或在 Plan Mode 未活動時用於 `opusplan` 的模型。                                                                                                                                                                                                                                                                                                            |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL`                                                   | 用於 `haiku` 的模型，或[背景功能](https://code.claude.com/docs/zh-TW/costs#background-token-usage)                                                                                                                                                                                                                                                                               |
| `CLAUDE_CODE_SUBAGENT_MODEL`                                                      | 用於所有 [subagents](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)、[agent teams](https://code.claude.com/docs/zh-TW/agent-teams) 和 [workflow](https://code.claude.com/docs/zh-TW/workflows) 執行的代理的模型。接受別名（例如 `haiku`）或完整模型名稱，並覆蓋每次調用的 `model` 參數和 subagent 定義的 `model` frontmatter。設定為 `inherit` 以改用一般模型解析 |
| 注意：`ANTHROPIC_SMALL_FAST_MODEL` 已棄用，改用 `ANTHROPIC_DEFAULT_HAIKU_MODEL`。 |                                                                                                                                                                                                                                                                                                                                                                                  |

### 為第三方部署固定模型

當透過 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud’s Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai)、[Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 或 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 部署 Claude Code 時，在向使用者推出前固定模型版本。 不固定模型時，Claude Code 使用模型別名（例如 `fable`、`opus`、`sonnet` 和 `haiku`），這些別名會解析為每個提供者的內建預設模型 ID。該預設值可能落後於最新的 Anthropic 版本，而且它指向的模型可能尚未在使用者的帳戶中啟用。當預設值不可用時，Amazon Bedrock 和 Google Cloud’s Agent Platform 使用者會看到通知並回退到該會話的先前版本，或當預設值是 Opus 模型且沒有 Opus 版本可用時回退到預設 Sonnet 模型。Microsoft Foundry 使用者會看到錯誤，因為 Microsoft Foundry 沒有等效的啟動檢查。 在初始設定中將模型環境變數設定為特定版本 ID。固定讓您控制使用者何時移動到新模型。 使用以下環境變數搭配您提供者的版本特定模型 ID：

| 提供者                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 範例                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Amazon Bedrock                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | `export ANTHROPIC_DEFAULT_OPUS_MODEL='us.anthropic.claude-opus-4-8'` |
| Google Cloud’s Agent Platform                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | `export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'`              |
| Microsoft Foundry                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'`              |
| 對 `ANTHROPIC_DEFAULT_FABLE_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL` 和 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 應用相同的模式。有關所有提供者的目前和舊版模型 ID，請參閱[模型概述](https://platform.claude.com/docs/en/about-claude/models/overview)。若要將使用者升級到新模型版本，請更新這些環境變數並重新部署。 若要為固定模型啟用[擴展 context](https://code.claude.com/docs/zh-TW/model-config#extended-context)，請將 `[1m]` 附加到 `ANTHROPIC_DEFAULT_OPUS_MODEL` 或 `ANTHROPIC_DEFAULT_SONNET_MODEL` 中的模型 ID： |                                                                      |

```
export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8[1m]'

```

`[1m]` 後綴將 1M context window 應用於 `opus` 和 `sonnet` 別名的所有使用，包括 [`opusplan`](https://code.claude.com/docs/zh-TW/model-config#opusplan-model-setting) 的 plan-mode Opus 階段。

- Claude Code 在將模型 ID 發送到您的提供者之前會移除該後綴。
- 只有當基礎模型[支援 1M context](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-window-sizes-by-model) 時，才附加 `[1m]`。
- 後綴是按變數讀取的，而不是按模型讀取的。在 Amazon Bedrock、Google Cloud’s Agent Platform 和 Microsoft Foundry 上，一個變數中沒有 `[1m]` 的模型 ID 會使用 200K context，即使另一個變數設定相同的模型並帶有後綴。Sonnet 5 在這些提供者上始終以 1M window 執行，永遠不需要後綴。

使用第三方提供者時，透過 [MDM 或受管設定檔](https://code.claude.com/docs/zh-TW/settings#settings-files) 傳遞的 `availableModels` 允許清單仍然適用；[伺服器管理的設定不會在那裡傳遞](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)。篩選會根據模型別名（例如 `opus`）、版本前綴（例如 `claude-opus-4-8`）或完整提供者形式模型 ID 進行匹配。提供者特定的前綴（例如 `us.anthropic.`）不會被移除，因此若要允許特定模型，請列出選擇器顯示的相同提供者形式 ID，或透過 [`modelOverrides`](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version) 對應它。任何 `[1m]` 後綴會從允許清單項目和請求的模型中移除，然後進行匹配。

### 自訂固定模型顯示和能力

當您在第三方提供者上固定模型時，提供者特定的 ID 會按原樣出現在 `/model` 選擇器中，Claude Code 可能無法識別模型支援的功能。您可以使用每個固定模型的伴隨環境變數覆蓋顯示名稱並宣告能力。 這些變數在 Amazon Bedrock、Google Cloud’s Agent Platform 和 Microsoft Foundry 等第三方提供者上生效。`_NAME` 和 `_DESCRIPTION` 變數在 `ANTHROPIC_BASE_URL` 指向 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway) 時也會生效。當直接連接到 `api.anthropic.com` 時無效。

| 環境變數                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 描述                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | `/model` 選擇器中固定 Opus 模型的顯示名稱。未設定時預設為模型 ID                                 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | `/model` 選擇器中固定 Opus 模型的顯示描述。未設定時預設為 `Custom Opus model`                    |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 固定 Opus 模型支援的能力的逗號分隔清單                                                           |
| 相同的 `_NAME`、`_DESCRIPTION` 和 `_SUPPORTED_CAPABILITIES` 後綴可用於 `ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`ANTHROPIC_DEFAULT_FABLE_MODEL` 和 `ANTHROPIC_CUSTOM_MODEL_OPTION`。 Claude Code 透過將模型 ID 與已知模式進行匹配來啟用[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)和[擴展思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)等功能。提供者特定的 ID（例如 Amazon Bedrock ARN 或自訂部署名稱）通常不符合這些模式，導致支援的功能被禁用。設定 `_SUPPORTED_CAPABILITIES` 以告訴 Claude Code 模型實際支援的功能： |                                                                                                  |
| 能力值                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 啟用                                                                                             |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | ---                                                                                              |
| `effort`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | [努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)和 `/effort` 命令 |
| `xhigh_effort`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `xhigh` 努力等級                                                                                 |
| `max_effort`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `max` 努力等級                                                                                   |
| `thinking`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | [擴展思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)                    |
| `adaptive_thinking`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 根據任務複雜性動態分配思考的自適應推理                                                           |
| `interleaved_thinking`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 工具呼叫之間的思考                                                                               |
| 當設定 `_SUPPORTED_CAPABILITIES` 時，列出的能力會為匹配的固定模型啟用，未列出的能力會被禁用。當變數未設定時，Claude Code 會回退到基於模型 ID 的內建檢測。 此範例將 Opus 固定到 Amazon Bedrock 自訂模型 ARN，設定友善名稱，並宣告其能力：                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                  |

```
export ANTHROPIC_DEFAULT_OPUS_MODEL='arn:aws:bedrock:us-east-1:123456789012:custom-model/abc'
export ANTHROPIC_DEFAULT_OPUS_MODEL_NAME='Opus via Bedrock'
export ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION='Opus 4.7 routed through a Bedrock custom endpoint'
export ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES='effort,xhigh_effort,max_effort,thinking,adaptive_thinking,interleaved_thinking'

```

### 按版本覆蓋模型 ID

家族級環境變數上述為每個家族別名配置一個模型 ID。如果您需要將同一家族內的多個版本對應到不同的提供者 ID，請改用 `modelOverrides` 設定。 `modelOverrides` 將個別 Anthropic 模型 ID 對應到 Claude Code 發送到您提供者 API 的提供者特定字串。當使用者在 `/model` 選擇器中選擇對應的模型時，Claude Code 會使用您配置的值而不是內建預設值。 這讓企業管理員可以將每個模型版本路由到特定的 Amazon Bedrock 推論設定檔 ARN、Google Cloud’s Agent Platform 版本名稱或 Microsoft Foundry 部署名稱，以進行治理、成本分配或區域路由。 在您的[設定檔](https://code.claude.com/docs/zh-TW/settings#settings-files)中設定 `modelOverrides`：

```
{
  "modelOverrides": {
    "claude-opus-4-7": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-prod",
    "claude-opus-4-6": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-46-prod",
    "claude-sonnet-4-6": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/sonnet-prod"
  }
}

```

鍵必須是[模型概述](https://platform.claude.com/docs/en/about-claude/models/overview)中列出的 Anthropic 模型 ID。對於日期模型 ID，請包含日期後綴，完全如其所示。未知的鍵會被忽略。 覆蓋會取代支援 `/model` 選擇器中每個項目的內建模型 ID。在 Amazon Bedrock 上，`modelOverrides` 項目優先於 Claude Code 在啟動時自動發現的任何推論設定檔。Claude Code 會將已經是提供者原生的值（例如 Amazon Bedrock 推論設定檔 ARN 或 Microsoft Foundry 部署名稱）按原樣傳遞給提供者。 當您直接透過 `--model`、`ANTHROPIC_MODEL` 環境變數或 `ANTHROPIC_DEFAULT_*_MODEL` 環境變數傳遞 Anthropic 模型 ID 時，覆蓋也會適用。在 Amazon Bedrock、Google Cloud’s Agent Platform 和 [Mantle](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint) 上，沒有 `modelOverrides` 項目的 Anthropic 模型 ID 會解析為與該版本的 `/model` 選擇器列相同的提供者特定 ID（當提供者支援該版本時）。Mantle 支援版本的子集。對於該子集之外的 Anthropic 模型 ID，Claude Code 會將原始 ID 發送到 Mantle 而不進行對應，除非 `modelOverrides` 項目涵蓋它。在 v2.1.200 之前，`--model` 和環境變數值會按原樣到達提供者，不會通過覆蓋對應。 `modelOverrides` 與 `availableModels` 一起運作。允許清單會根據 Anthropic 模型 ID 進行評估，而不是覆蓋值，因此 `availableModels` 中的項目（如 `"opus"`）即使 Opus 版本對應到 ARN 時仍會繼續匹配。當在受管設定中設定 `enforceAvailableModels` 時，強制執行的預設值會從[最高優先順序受管來源](https://code.claude.com/docs/zh-TW/server-managed-settings#settings-precedence)透過 `modelOverrides` 解析。管理員的對應（例如固定到推論設定檔 ARN 的版本）會在強制執行的預設值中受到尊重。來自使用者或專案設定的覆蓋不會影響它。 當 `availableModels` 在[受管設定](https://code.claude.com/docs/zh-TW/settings#settings-files)中設定時，只有來自該受管來源的 `modelOverrides` 適用於直接透過 `--model` 或上述環境變數傳遞的 Anthropic 模型 ID。Claude Code 會忽略來自使用者或專案設定的這些 ID 的覆蓋，並且永遠不會透過來自任何設定來源的 `modelOverrides` 解析受管清單排除的 ID。此受管來源限制需要 Claude Code v2.1.200 或更新版本。請參閱[限制模型選擇](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)以瞭解如何處理被阻止的 ID。

### Prompt caching 配置

Claude Code 自動使用 [prompt caching](https://code.claude.com/docs/zh-TW/prompt-caching) 來優化效能並降低成本。您可以全域禁用 prompt caching 或針對特定模型層級禁用：

| 環境變數                                                                                                                                       | 描述                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `DISABLE_PROMPT_CACHING`                                                                                                                       | 設定為 `1` 以禁用所有模型的 prompt caching。優先於每個模型的設定 |
| `DISABLE_PROMPT_CACHING_HAIKU`                                                                                                                 | 設定為 `1` 以僅禁用 Haiku 模型的 prompt caching                  |
| `DISABLE_PROMPT_CACHING_SONNET`                                                                                                                | 設定為 `1` 以僅禁用 Sonnet 模型的 prompt caching                 |
| `DISABLE_PROMPT_CACHING_OPUS`                                                                                                                  | 設定為 `1` 以僅禁用 Opus 模型的 prompt caching                   |
| `DISABLE_PROMPT_CACHING_FABLE`                                                                                                                 | 設定為 `1` 以僅禁用 Fable 模型的 prompt caching                  |
| 若要變更快取 TTL 或瞭解什麼會觸發快取未命中，請參閱 [Claude Code 如何使用 prompt caching](https://code.claude.com/docs/zh-TW/prompt-caching)。 |                                                                  |
| 是否                                                                                                                                           |                                                                  |
| 助手                                                                                                                                           |                                                                  |
