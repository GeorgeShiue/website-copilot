透過 OpenTelemetry (OTel) 匯出遙測資料，追蹤 Claude Code 在整個組織中的使用情況、成本和工具活動。Claude Code 透過標準指標協議匯出指標作為時間序列資料、透過日誌/事件協議匯出事件，以及可選地透過[追蹤協議](https://code.claude.com/docs/zh-TW/monitoring-usage#traces-beta)匯出分散式追蹤。

## 快速開始

使用環境變數配置 OpenTelemetry：

```
# 1. 啟用遙測
export CLAUDE_CODE_ENABLE_TELEMETRY=1

# 2. 選擇匯出器（兩者都是可選的 - 僅配置您需要的）
export OTEL_METRICS_EXPORTER=otlp       # 選項：otlp、prometheus、console、none
export OTEL_LOGS_EXPORTER=otlp          # 選項：otlp、console、none

# 3. 配置 OTLP 端點（用於 OTLP 匯出器）
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 4. 設定身份驗證（如果需要）
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# 5. 用於除錯：減少匯出間隔，並在生產環境中重設它們
export OTEL_METRIC_EXPORT_INTERVAL=10000  # 10 秒（預設：60000ms）
export OTEL_LOGS_EXPORT_INTERVAL=5000     # 5 秒（預設：5000ms）

# 6. 執行 Claude Code
claude

```

若要驗證匯出指標的設定，請檢查您的後端是否有 `claude_code.session.count` 指標，Claude Code 會在工作階段啟動時發出此指標。若要驗證僅限日誌的設定，請提交提示並檢查 `claude_code.user_prompt` 事件。 如果沒有任何內容到達，請執行 `claude --debug` 並檢查除錯日誌。Claude Code 會將您配置的匯出器失敗報告為 `[3P telemetry]` 錯誤，其中 3P 表示第三方。以 `[Anthropic telemetry]` 為前綴的行描述 [Anthropic 的獨立營運遙測](https://code.claude.com/docs/zh-TW/data-usage#telemetry-services)，不表示您的設定有問題。 如需完整配置選項，請參閱 [OpenTelemetry 規範](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md#configuration-options)。

## 管理員配置

管理員可以透過[受管設定檔](https://code.claude.com/docs/zh-TW/managed-settings#delivery-mechanisms)為所有使用者配置 OpenTelemetry 設定。請參閱[設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)以了解有關如何應用設定的更多資訊。 受管設定配置範例：

```
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer example-token"
  }
}

```

Claude Code 不會將 `OTEL_*` 環境變數傳遞給它產生的子程序，包括 Bash 工具、hooks、MCP 伺服器和語言伺服器。透過 Bash 工具執行的 OpenTelemetry 檢測應用程式不會繼承 Claude Code 的匯出器端點或標頭，因此如果該應用程式需要匯出自己的遙測，請直接在命令中設定這些變數。

### 受管設定如何鎖定 OTLP 目的地

當您在受管設定中設定 `OTEL_EXPORTER_OTLP_*` 變數時，Claude Code 會在啟動時移除衝突的開發人員設定變數，並記錄您可以透過 `claude --debug` 查看的警告。它移除的內容取決於您設定的變數：

- **端點** ：當您設定 `OTEL_EXPORTER_OTLP_ENDPOINT` 時，Claude Code 會移除每個開發人員設定的每個信號端點。開發人員無法將一個信號指向不同的收集器，因此您不需要在受管設定中也設定每個信號的端點變數。
- **協議** ：當您設定 `OTEL_EXPORTER_OTLP_PROTOCOL` 時，Claude Code 會移除每個開發人員設定的每個信號協議。
- **認證** ：當您設定 `OTEL_EXPORTER_OTLP_HEADERS`、`OTEL_EXPORTER_OTLP_CLIENT_KEY` 或 `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` 時，Claude Code 會移除該變數的開發人員設定每個信號版本，加上每個開發人員設定的端點變數（通用或每個信號），因為這些認證否則會到達受管設定未選擇的收集器。
- **匯出器選擇器** ：`OTEL_METRICS_EXPORTER`、`OTEL_LOGS_EXPORTER` 和測試版 `OTEL_TRACES_EXPORTER` 遵循正常的每個鍵優先順序。開發人員的設定仍然可以禁用信號或將其切換到控制台匯出器，因此如果您需要鎖定選擇器，也請在受管設定中設定它們。在[管理員來源](https://code.claude.com/docs/zh-TW/managed-settings#precedence-within-the-managed-tier)中，`OTEL_LOGS_EXPORTER` 遵循[遙測單位](https://code.claude.com/docs/zh-TW/server-managed-settings#per-key-exceptions-across-managed-sources)，而其他兩個選擇器按鍵合併。需要 Claude Code v2.1.223 或更新版本。
- **測試版追蹤端點** ：當[詳細測試版追蹤](https://code.claude.com/docs/zh-TW/monitoring-usage#traces-beta)啟用時，Claude Code 會將日誌和追蹤匯出到 `BETA_TRACING_ENDPOINT` 而不是透過日誌和追蹤匯出器。因此，Claude Code 會在以下任何受管設定決定任一信號的目的地時移除開發人員設定的 `BETA_TRACING_ENDPOINT`：
  - 通用或日誌/追蹤端點或認證
  - 一個 [`otelHeadersHelper`](https://code.claude.com/docs/zh-TW/settings-reference#otelheadershelper)
  - 日誌或追蹤匯出器選擇器設定為 `none`、`console` 或空白，這些值會將信號保持在收集器之外
  - `CLAUDE_CODE_ENABLE_TELEMETRY` 關閉 僅限指標的端點或認證不會移除它。在 v2.1.251 之前，開發人員設定的 `BETA_TRACING_ENDPOINT` 會重新導向詳細測試版追蹤匯出的日誌和追蹤，即使受管設定固定了收集器。

Claude Code 不會移除您在受管設定本身中設定的每個信號變數，因此您可以透過在其中設定其變數來將一個信號路由到不同的收集器，如[SIEM 範例](https://code.claude.com/docs/zh-TW/monitoring-usage#send-events-to-a-siem)所示。如果您在其中設定每個信號認證，Claude Code 會移除該信號的開發人員設定端點。 此移除行為改變遙測的傳遞位置，而不是 Claude Code 收集的內容。 在 v2.1.217 之前，每個變數獨立遵循每個鍵設定優先順序，因此在使用者設定或 shell 中設定的信號特定端點會將該信號重新導向離開受管收集器。 當桌面應用程式或[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments)執行器啟動 Claude Code 並在其提供的環境中命名 OTLP 端點時，Claude Code 會以相同方式固定目的地：啟動器的遙測變數移除開發人員設定的變數，完全如受管設定所做的那樣。Claude Code 不會移除啟動器本身設定的變數。需要 Claude Code v2.1.251 或更新版本。

## 設定詳細資訊

### 常見設定變數

這些變數為所有部署設定匯出工具、端點和匯出行為。如果您設定每個信號端點或協議變數（例如 `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`），Claude Code 會改用它而不是該信號的通用變數。如果您設定每個信號標頭變數（例如 `OTEL_EXPORTER_OTLP_METRICS_HEADERS`），Claude Code 會將其與該信號的通用 `OTEL_EXPORTER_OTLP_HEADERS` 合併。在具有受管設定的機器上，請參閱[受管設定如何鎖定 OTLP 目的地](https://code.claude.com/docs/zh-TW/monitoring-usage#how-managed-settings-lock-the-otlp-destination)以了解 Claude Code 移除的內容。

| 環境變數                                                                                                                                                                                                                                                                     | 說明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 範例值                                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE_CODE_ENABLE_TELEMETRY`                                                                                                                                                                                                                                               | 啟用遙測收集（必需）                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `1`                                                                                                                       |
| `OTEL_METRICS_EXPORTER`                                                                                                                                                                                                                                                      | 指標匯出工具類型，以逗號分隔。使用 `none` 停用                                                                                                                                                                                                                                                                                                                                                                                                                                          | `console`、`otlp`、`prometheus`、`none`                                                                                   |
| `OTEL_LOGS_EXPORTER`                                                                                                                                                                                                                                                         | 日誌/事件匯出工具類型，以逗號分隔。使用 `none` 停用                                                                                                                                                                                                                                                                                                                                                                                                                                     | `console`、`otlp`、`none`                                                                                                 |
| `OTEL_EXPORTER_OTLP_PROTOCOL`                                                                                                                                                                                                                                                | OTLP 匯出工具的協議，適用於所有信號。Claude Code 沒有預設協議，因此請為您啟用的每個 `otlp` 匯出工具設定此項或信號特定協議變數                                                                                                                                                                                                                                                                                                                                                           | `grpc`、`http/json`、`http/protobuf`                                                                                      |
| `OTEL_EXPORTER_OTLP_ENDPOINT`                                                                                                                                                                                                                                                | 所有信號的 OTLP 收集器端點                                                                                                                                                                                                                                                                                                                                                                                                                                                              | `http://localhost:4317`                                                                                                   |
| `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL`                                                                                                                                                                                                                                        | 指標的協議，覆蓋通用設定                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `grpc`、`http/json`、`http/protobuf`                                                                                      |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`                                                                                                                                                                                                                                        | OTLP 指標端點，覆蓋通用設定                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `http://localhost:4318/v1/metrics`                                                                                        |
| `OTEL_EXPORTER_OTLP_LOGS_PROTOCOL`                                                                                                                                                                                                                                           | 日誌的協議，覆蓋通用設定                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `grpc`、`http/json`、`http/protobuf`                                                                                      |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`                                                                                                                                                                                                                                           | OTLP 日誌端點，覆蓋通用設定                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `http://localhost:4318/v1/logs`                                                                                           |
| `OTEL_EXPORTER_OTLP_HEADERS`                                                                                                                                                                                                                                                 | OTLP 的驗證標頭                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `Authorization=Bearer token`                                                                                              |
| `OTEL_EXPORTER_OTLP_METRICS_HEADERS`                                                                                                                                                                                                                                         | 指標的驗證標頭，與通用標頭合併                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `Authorization=Bearer token`                                                                                              |
| `OTEL_EXPORTER_OTLP_LOGS_HEADERS`                                                                                                                                                                                                                                            | 日誌的驗證標頭，與通用標頭合併                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `Authorization=Bearer token`                                                                                              |
| `OTEL_METRIC_EXPORT_INTERVAL`                                                                                                                                                                                                                                                | 匯出間隔（毫秒）（預設值：60000）                                                                                                                                                                                                                                                                                                                                                                                                                                                       | `5000`、`60000`                                                                                                           |
| `OTEL_LOGS_EXPORT_INTERVAL`                                                                                                                                                                                                                                                  | 日誌匯出間隔（毫秒）（預設值：5000）                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `1000`、`10000`                                                                                                           |
| `OTEL_LOG_USER_PROMPTS`                                                                                                                                                                                                                                                      | 啟用使用者提示內容的日誌記錄（預設值：停用）                                                                                                                                                                                                                                                                                                                                                                                                                                            | `1` 啟用                                                                                                                  |
| `OTEL_LOG_ASSISTANT_RESPONSES`                                                                                                                                                                                                                                               | 在 `assistant_response` 事件上啟用助理回應文字的日誌記錄（預設值：停用）。未設定時，回退到 `OTEL_LOG_USER_PROMPTS` 的值。需要 Claude Code v2.1.193 或更新版本                                                                                                                                                                                                                                                                                                                           | `1` 啟用，`0` 保持編輯                                                                                                    |
| `OTEL_LOG_TOOL_DETAILS`                                                                                                                                                                                                                                                      | 啟用工具事件和追蹤跨度屬性中的工具參數和輸入引數的日誌記錄：Bash 命令、MCP 伺服器和工具名稱、技能名稱、使用者撰寫的工作流程名稱和工具輸入。也在 `user_prompt` 事件上啟用自訂、外掛程式和 MCP 命令名稱（預設值：停用）。對於 Claude Desktop 的內建伺服器，在 Claude Desktop 擁有的工作階段中，即使關閉旗標，`mcp_server_name`/`mcp_tool_name` 也會在 `tool_decision`/`tool_result` 上發出。例外需要 Claude Code v2.1.214 或更新版本                                                      | `1` 啟用                                                                                                                  |
| `OTEL_LOG_TOOL_CONTENT`                                                                                                                                                                                                                                                      | 啟用 [`tool.output` 跨度事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-output-span-event)中工具內容的日誌記錄（預設值：停用）。跨度屬性在[其自己的閘道](https://code.claude.com/docs/zh-TW/monitoring-usage#new-context-gates)下攜帶工具內容。需要[追蹤](https://code.claude.com/docs/zh-TW/monitoring-usage#traces-beta)。內容在內容限制處截斷（預設值：60 KB）                                                                                                        | `1` 啟用                                                                                                                  |
| `OTEL_LOG_RAW_API_BODIES`                                                                                                                                                                                                                                                    | 將完整的 Anthropic Messages API 請求和回應 JSON 作為 `api_request_body` / `api_response_body` 日誌事件發出（預設值：停用）。主體包括整個對話歷史記錄。啟用此項意味著同意 `OTEL_LOG_USER_PROMPTS`、`OTEL_LOG_TOOL_DETAILS` 和 `OTEL_LOG_TOOL_CONTENT` 會揭露的所有內容                                                                                                                                                                                                                   | `1` 表示在內容限制處截斷的內聯主體（預設值：60 KB），或 `file:<dir>` 表示磁碟上未截斷的主體，在事件中帶有 `body_ref` 指標 |
| `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH`                                                                                                                                                                                                                                        | 內容限制：內容承載屬性（例如模型回應、工具內容、系統提示和原始 API 主體）的最大長度，包括截斷標記，以 UTF-16 程式碼單位計（預設值：61440，即 60 KB）。預設值適用於將屬性值上限設為 64 KB 的後端；只有在您的後端接受更大的值時才提高它，或降低它以減少遙測量。當設定了 OpenTelemetry SDK 屬性限制 `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` 或其日誌記錄和跨度變體之一時，Claude Code 會在該較小的值處截斷，以便 `[TRUNCATED ...]` 標記保持在 SDK 限制內。需要 Claude Code v2.1.214 或更新版本 | `262144`                                                                                                                  |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE`                                                                                                                                                                                                                          | 指標時間性偏好（預設值：`delta`）。如果您的後端期望累積時間性，請設定為 `cumulative`                                                                                                                                                                                                                                                                                                                                                                                                    | `delta`、`cumulative`                                                                                                     |
| `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS`                                                                                                                                                                                                                                | 重新整理動態標頭的間隔（預設值：1740000ms / 29 分鐘）                                                                                                                                                                                                                                                                                                                                                                                                                                   | `900000`                                                                                                                  |
| 對於 `http/protobuf` 和 `http/json` 協議，Claude Code 會使用 `Content-Length` 標頭傳送每個匯出請求。在 v2.1.212 之前，v2.1.191 及以後的 Claude Code 版本使用分塊傳輸編碼傳送這些請求；Azure Monitor 和其他需要宣告長度的端點以 `411 Length Required` 或 `400` 錯誤拒絕它們。 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                           |

### mTLS 驗證

您為 OTLP 匯出工具設定用戶端憑證的方式取決於該信號使用的 OTLP 協議，透過 `OTEL_EXPORTER_OTLP_PROTOCOL` 或每個信號的覆蓋設定。相同的設定適用於指標、日誌和追蹤。

| 協議                                                                                                                                                                                                                                                                                              | 用戶端憑證變數                                                                                                                                                                              | 信任收集器的 CA 使用             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `http/protobuf`、`http/json`                                                                                                                                                                                                                                                                      | `CLAUDE_CODE_CLIENT_CERT`、`CLAUDE_CODE_CLIENT_KEY` 和選擇性的 `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE`。請參閱[網路設定](https://code.claude.com/docs/zh-TW/network-config#mtls-authentication) | `NODE_EXTRA_CA_CERTS`            |
| `grpc`                                                                                                                                                                                                                                                                                            | `OTEL_EXPORTER_OTLP_CLIENT_KEY` 和 `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE`，或每個信號的變體（例如 `OTEL_EXPORTER_OTLP_METRICS_CLIENT_KEY`）以針對每個信號使用不同的憑證                    | `OTEL_EXPORTER_OTLP_CERTIFICATE` |
| 對於 `grpc`，OpenTelemetry SDK 直接讀取標準 OTLP 變數，因此設定每個信號指標變數的現有設定會繼續運作。在具有受管設定的機器上，Claude Code [可能在啟動時移除開發人員設定的每個信號認證和端點](https://code.claude.com/docs/zh-TW/monitoring-usage#how-managed-settings-lock-the-otlp-destination)。 |                                                                                                                                                                                             |                                  |

### 指標基數控制

下列環境變數控制指標中包含哪些屬性以管理基數：

| 環境變數                                                               | 說明                                                                                                                                                         | 預設值  | 停用範例 |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | -------- |
| `OTEL_METRICS_INCLUDE_SESSION_ID`                                      | 在指標中包含 session.id 屬性                                                                                                                                 | `true`  | `false`  |
| `OTEL_METRICS_INCLUDE_VERSION`                                         | 在指標中包含 app.version 屬性                                                                                                                                | `false` | `true`   |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`                                    | 在指標中包含 user.account_uuid 和 user.account_id 屬性                                                                                                       | `true`  | `false`  |
| `OTEL_METRICS_INCLUDE_ENTRYPOINT`                                      | 在指標中包含 app.entrypoint 屬性                                                                                                                             | `false` | `true`   |
| `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES`                             | 將 `OTEL_RESOURCE_ATTRIBUTES` 中的金鑰作為屬性包含在指標資料點上                                                                                             | `true`  | `false`  |
| `OTEL_METRICS_INCLUDE_REPOSITORY`                                      | 在指標和事件上包含 `vcs.*` [儲存庫身分屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#repository-attributes)。需要 Claude Code v2.1.269 或更新版本 | `false` | `true`   |
| 較低的基數通常意味著更好的效能和更低的儲存成本，但分析的資料粒度較低。 |                                                                                                                                                              |         |          |

### 追蹤（測試版）

分散式追蹤匯出跨度，將每個使用者提示連結到它觸發的 API 請求和工具執行，因此您可以在追蹤後端中將完整請求檢視為單一追蹤。 追蹤預設為關閉。若要啟用它，請同時設定 `CLAUDE_CODE_ENABLE_TELEMETRY=1` 和 `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`，然後設定 `OTEL_TRACES_EXPORTER` 以選擇跨度的傳送位置。追蹤重複使用[常見 OTLP 設定](https://code.claude.com/docs/zh-TW/monitoring-usage#common-configuration-variables)以取得端點、協議、標頭和 [mTLS](https://code.claude.com/docs/zh-TW/monitoring-usage#mtls-authentication)。在具有受管設定的機器上，Claude Code [可能在啟動時移除開發人員設定的每個信號認證和端點](https://code.claude.com/docs/zh-TW/monitoring-usage#how-managed-settings-lock-the-otlp-destination)。

| 環境變數                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 說明                                                          | 範例值                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ------------------------------------ |
| `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 啟用跨度追蹤（必需）。也接受 `ENABLE_ENHANCED_TELEMETRY_BETA` | `1`                                  |
| `OTEL_TRACES_EXPORTER`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 追蹤匯出工具類型，以逗號分隔。使用 `none` 停用                | `console`、`otlp`、`none`            |
| `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 追蹤的協議，覆蓋 `OTEL_EXPORTER_OTLP_PROTOCOL`                | `grpc`、`http/json`、`http/protobuf` |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | OTLP 追蹤端點，覆蓋 `OTEL_EXPORTER_OTLP_ENDPOINT`             | `http://localhost:4318/v1/traces`    |
| `OTEL_EXPORTER_OTLP_TRACES_HEADERS`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 追蹤的驗證標頭，與 `OTEL_EXPORTER_OTLP_HEADERS` 合併          | `Authorization=Bearer token`         |
| `OTEL_TRACES_EXPORT_INTERVAL`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 跨度批次匯出間隔（毫秒）（預設值：5000）                      | `1000`、`10000`                      |
| 跨度預設會編輯使用者提示文字、工具輸入詳細資訊和工具內容。設定 `OTEL_LOG_USER_PROMPTS=1`、`OTEL_LOG_TOOL_DETAILS=1` 和 `OTEL_LOG_TOOL_CONTENT=1` 以包含它們。 當追蹤處於作用中時，Bash 和 PowerShell 子程序會自動繼承包含作用中工具執行跨度的 W3C 追蹤內容的 `TRACEPARENT` 環境變數。這讓任何讀取 `TRACEPARENT` 的子程序都可以在相同追蹤下將其自己的跨度作為父項，啟用透過 Claude 執行的指令碼和命令的端對端分散式追蹤。 當追蹤處於作用中且 Claude Code 直接連線到 Anthropic API 時，每個模型請求都會攜帶設定為 `claude_code.llm_request` 跨度內容的 W3C `traceparent` 標頭，API 的 `traceresponse` 標頭會記錄為跨度連結。這些一起透過任何相容的中介將 Claude Code 的用戶端跨度連線到伺服器端追蹤。出站 HTTP MCP 請求以相同方式攜帶 `traceparent`。標頭不會傳送給第三方提供者。 預設情況下，模型和 HTTP MCP 請求上的 `traceparent` 標頭僅在 `ANTHROPIC_BASE_URL` 未設定或指向 Anthropic API 時傳送，因為某些代理會拒絕無法識別的標頭。子程序 `TRACEPARENT` 變數由相同的開關控制以保持一致性。如果您透過自訂 `ANTHROPIC_BASE_URL` 代理執行 Claude Code 並想要傳播追蹤內容，請設定 `CLAUDE_CODE_PROPAGATE_TRACEPARENT=1`。 在 Agent SDK 和以 `-p` 啟動的非互動式工作階段中，Claude Code 也會在啟動每個互動跨度時從其自己的環境讀取 `TRACEPARENT` 和 `TRACESTATE`。這讓嵌入程序將其作用中的 W3C 追蹤內容傳遞到子程序，以便 Claude Code 的跨度顯示為呼叫者分散式追蹤的子項。互動式工作階段會忽略入站 `TRACEPARENT` 以避免意外繼承來自 CI 或容器環境的環境值。 入站追蹤內容也適用於[事件](https://code.claude.com/docs/zh-TW/monitoring-usage#events)。在設定了 `TRACEPARENT` 的 Agent SDK 和 `-p` 工作階段中，每個 OTLP 事件日誌記錄都會攜帶 `trace_id` 和 `span_id` 值，將其連結到您的應用程式追蹤，即使未設定追蹤匯出工具，您的日誌後端也可以將事件與追蹤的其餘部分相關聯。 在互動作用中時發出的記錄會攜帶互動跨度的 ID，即使 Claude Code 在跨度的非同步內容外發出它，例如在權限提示回呼或在啟動期間緩衝並稍後匯出的記錄中。在沒有作用中互動跨度的情況下發出的記錄會直接攜帶入站 `TRACEPARENT` ID。在 v2.1.214 之前，在跨度的非同步內容外發出的記錄會攜帶入站 `TRACEPARENT` ID 而不是跨度的 ID。在 v2.1.212 之前，在作用中跨度外發出的事件記錄不會攜帶 `trace_id` 或 `span_id`。 |                                                               |                                      |

#### 跨度階層

每個使用者提示都會啟動 `claude_code.interaction` 根跨度。API 呼叫、工具呼叫和掛鉤執行會記錄為其子項。工具跨度有兩個自己的子跨度：一個用於等待權限決定的時間，一個用於執行本身。當 Agent 工具或舊版 Task 工具產生子代理時，子代理的 API 和工具跨度會巢狀在父項的 `claude_code.tool` 跨度下。

```
claude_code.interaction
├── claude_code.llm_request
├── claude_code.hook                    (requires detailed beta tracing)
└── claude_code.tool
    ├── claude_code.tool.blocked_on_user
    ├── claude_code.tool.execution
    └── (Agent tool) subagent claude_code.llm_request / claude_code.tool spans

```

在 Agent SDK 和 `claude -p` 工作階段中，當環境中設定了 `TRACEPARENT` 時，`claude_code.interaction` 本身會成為呼叫者跨度的子項。 當 `PreToolUse` 掛鉤[延遲工具呼叫](https://code.claude.com/docs/zh-TW/hooks#defer-a-tool-call-for-later)時，Claude Code 會儲存延遲它的回合的追蹤內容。當您繼續工作階段且工具重新執行時，工具的跨度會作為該較早回合的 `claude_code.interaction` 跨度的子項加入該回合的追蹤。

#### 跨度屬性

每個跨度都會攜帶[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)加上與其名稱相符的 `span.type` 屬性。下表列出在每個跨度上設定的其他屬性。`llm_request`、`tool.execution` 和 `hook` 跨度在記錄失敗時設定 OpenTelemetry 狀態 `ERROR`；其他跨度始終以狀態 `UNSET` 結束。 **`claude_code.interaction`**

| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 說明                                                                                                                                                                                                                                                                                             | 由以下控制                     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ |
| `user_prompt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 提示文字。除非設定了閘道，否則值為 `<REDACTED>`                                                                                                                                                                                                                                                  | `OTEL_LOG_USER_PROMPTS`        |
| `user_prompt_length`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 提示長度（字元）                                                                                                                                                                                                                                                                                 |                                |
| `interaction.sequence`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 互動的 1 為基礎計數器，按 Claude Code 程序而不是按工作階段計數，如 [`event.sequence`](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes) 所述                                                                                                                     |                                |
| `parent.source`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 跨度如何獲得其追蹤父項：當它在入站 `TRACEPARENT` 下作為父項時為 `env`，當它啟動自己的追蹤時為 `none`。需要 Claude Code v2.1.268 或更新版本                                                                                                                                                       |                                |
| `interaction.duration_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 回合的掛鐘持續時間                                                                                                                                                                                                                                                                               |                                |
| **`claude_code.llm_request`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                                                                                                                                                                                                                                                                                                  |                                |
| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 說明                                                                                                                                                                                                                                                                                             | 由以下控制                     |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | ---                                                                                                                                                                                                                                                                                              | ---                            |
| `model`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 模型識別碼                                                                                                                                                                                                                                                                                       |                                |
| `gen_ai.system`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 始終為 `anthropic`。OpenTelemetry GenAI 語義慣例                                                                                                                                                                                                                                                 |                                |
| `gen_ai.request.model`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 與 `model` 相同的值。OpenTelemetry GenAI 語義慣例                                                                                                                                                                                                                                                |                                |
| `query_source`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 發出請求的子系統，例如 `repl_main_thread` 或子代理名稱                                                                                                                                                                                                                                           | `ENABLE_BETA_TRACING_DETAILED` |
| `query_source_safe`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `query_source` 的有界形式，無論詳細測試版追蹤是否作用中都會發出，具有 `repl_main_thread` 或 `agent.builtin.general-purpose` 等值。`:` 變成 `.`，使用者命名的代理顯示為 `agent.custom`。需要 Claude Code v2.1.268 或更新版本                                                                      |                                |
| `agent_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 發出請求的子代理或隊友的識別碼。在主工作階段上不存在                                                                                                                                                                                                                                             |                                |
| `parent_agent_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 產生此代理的代理的識別碼。對於主工作階段和直接從它產生的代理不存在                                                                                                                                                                                                                               |                                |
| `workflow.run_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 產生此代理的[工作流程](https://code.claude.com/docs/zh-TW/workflows)工具執行的執行識別碼，前綴為 `wf_`。對於不是由工作流程產生的代理不存在                                                                                                                                                       |                                |
| `workflow.name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 產生此代理的工作流程的名稱。使用者撰寫的名稱會被替換為 `custom`，除非設定了閘道                                                                                                                                                                                                                  | `OTEL_LOG_TOOL_DETAILS`        |
| `speed`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | `fast` 或 `normal`                                                                                                                                                                                                                                                                               |                                |
| `llm_request.context`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 根據父項跨度為 `interaction`、`tool` 或 `standalone`                                                                                                                                                                                                                                             |                                |
| `duration_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 掛鐘持續時間，包括重試                                                                                                                                                                                                                                                                           |                                |
| `ttft_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 首個權杖的時間（毫秒）                                                                                                                                                                                                                                                                           |                                |
| `first_content_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 從請求開始到成功嘗試的第一個內容區塊的時間（毫秒）。在回退到非串流路徑的請求上不存在。需要 Claude Code v2.1.268 或更新版本                                                                                                                                                                       |                                |
| `input_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 來自 API 使用量區塊的輸入權杖計數                                                                                                                                                                                                                                                                |                                |
| `output_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 輸出權杖計數                                                                                                                                                                                                                                                                                     |                                |
| `cache_read_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 從提示快取讀取的權杖                                                                                                                                                                                                                                                                             |                                |
| `cache_creation_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 寫入提示快取的權杖                                                                                                                                                                                                                                                                               |                                |
| `request_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 來自 `request-id` 回應標頭的 Anthropic API 請求 ID                                                                                                                                                                                                                                               |                                |
| `gen_ai.response.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 與 `request_id` 相同的值。OpenTelemetry GenAI 語義慣例                                                                                                                                                                                                                                           |                                |
| `client_request_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 最終嘗試的用戶端產生的 `x-client-request-id`                                                                                                                                                                                                                                                     |                                |
| `attempt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 為此請求進行的總嘗試次數                                                                                                                                                                                                                                                                         |                                |
| `success`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | `true` 或 `false`                                                                                                                                                                                                                                                                                |                                |
| `status_code`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 請求失敗時的 HTTP 狀態碼                                                                                                                                                                                                                                                                         |                                |
| `error`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 請求失敗時的錯誤訊息                                                                                                                                                                                                                                                                             |                                |
| `error_class`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 請求失敗時的簡短錯誤類別權杖，例如 `api_timeout` 或 `server_overload`。需要 Claude Code v2.1.268 或更新版本                                                                                                                                                                                      |                                |
| `response.has_tool_call`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 當回應包含工具使用區塊時為 `true`                                                                                                                                                                                                                                                                |                                |
| `stop_reason`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | API 回應 `stop_reason`，例如 `end_turn`、`tool_use`、`max_tokens`、`stop_sequence`、`pause_turn` 或 `refusal`                                                                                                                                                                                    |                                |
| `gen_ai.response.finish_reasons`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 與 `stop_reason` 相同的值，包裝在字串陣列中。OpenTelemetry GenAI 語義慣例                                                                                                                                                                                                                        |                                |
| 每次重試嘗試也會記錄為 `gen_ai.request.attempt` 跨度事件，具有 `attempt` 和 `client_request_id` 屬性。 **`claude_code.tool`**                                                                                                                                                                                                                                                                                                                                                                                                                                                |                                                                                                                                                                                                                                                                                                  |                                |
| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 說明                                                                                                                                                                                                                                                                                             | 由以下控制                     |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | ---                                                                                                                                                                                                                                                                                              | ---                            |
| `tool_name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 工具名稱                                                                                                                                                                                                                                                                                         |                                |
| `tool_name_safe`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `tool_name` 的形式，不攜帶任何使用者選擇的名稱。內建工具名稱逐字傳遞。MCP 工具名稱顯示為 `mcp_other`，除了符合幾個固定形狀的工具名稱，例如名為 `browser_*` 的 Playwright 工具，它們逐字傳遞。需要 Claude Code v2.1.268 或更新版本                                                                |                                |
| `bash_command_class`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 對於 Bash 工具：命令的第一個程式的類別，來自固定清單，例如 `vcs` 或 `package_manager`。對於清單外的程式為 `other`，當行無法解析時為 `unparsed`。需要 Claude Code v2.1.268 或更新版本                                                                                                             |                                |
| `bash_argv0`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 對於 Bash 工具：當命令的第一個程式在相同的固定清單上時，例如 `git` 或 `npm`。對於清單外的任何程式為 `other`。需要 Claude Code v2.1.268 或更新版本                                                                                                                                                |                                |
| `duration_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 掛鐘持續時間，包括權限等待和執行                                                                                                                                                                                                                                                                 |                                |
| `result_tokens`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 工具結果的近似權杖大小                                                                                                                                                                                                                                                                           |                                |
| `agent_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 執行工具的子代理或隊友的識別碼。在主工作階段上不存在                                                                                                                                                                                                                                             |                                |
| `parent_agent_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 產生此代理的代理的識別碼。對於主工作階段和直接從它產生的代理不存在                                                                                                                                                                                                                               |                                |
| `workflow.run_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 產生此代理的工作流程工具執行的執行識別碼，前綴為 `wf_`。對於不是由工作流程產生的代理不存在                                                                                                                                                                                                       |                                |
| `workflow.name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 產生此代理的工作流程的名稱。使用者撰寫的名稱會被替換為 `custom`，除非設定了閘道                                                                                                                                                                                                                  | `OTEL_LOG_TOOL_DETAILS`        |
| `tool_use_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 此呼叫的模型 `tool_use` 區塊 ID。與 [tool_result](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-result-event) 和 [tool_decision](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-decision-event) 事件上的 `tool_use_id` 以及掛鉤承載中的相符，因此您可以將跨度連結到這些記錄 |                                |
| `gen_ai.tool.call.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 與 `tool_use_id` 相同的值。OpenTelemetry GenAI 語義慣例                                                                                                                                                                                                                                          |                                |
| `file_path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Read、Edit 和 Write 工具的目標檔案路徑                                                                                                                                                                                                                                                           | `OTEL_LOG_TOOL_DETAILS`        |
| `full_command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Bash 工具的命令字串                                                                                                                                                                                                                                                                              | `OTEL_LOG_TOOL_DETAILS`        |
| `skill_name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Skill 工具的技能名稱                                                                                                                                                                                                                                                                             | `OTEL_LOG_TOOL_DETAILS`        |
| `subagent_type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Agent 工具或舊版 Task 工具的子代理類型                                                                                                                                                                                                                                                           | `OTEL_LOG_TOOL_DETAILS`        |
| **`tool.output`跨度事件在`claude_code.tool` 上** 如果您設定 `OTEL_LOG_TOOL_CONTENT=1`，Read 和 Bash 呼叫可以在 `claude_code.tool` 跨度上記錄 `tool.output` 跨度事件。Edit 和 Write 呼叫僅在您也設定 `OTEL_LOG_TOOL_DETAILS=1` 時才記錄一個。該變數不限於這兩個工具，因此請檢查其[設定表中的列](https://code.claude.com/docs/zh-TW/monitoring-usage#common-configuration-variables)以了解它在其他地方新增的引數。 Claude Code 從工具呼叫的成功返回寫入此事件，因此引發錯誤的呼叫不會記錄任何內容，無論工具如何。在確實返回的呼叫中，它不會為以下項目記錄 `tool.output` 事件： |                                                                                                                                                                                                                                                                                                  |                                |

- 對除 Read、Edit、Write 和 Bash 之外的任何工具的呼叫，包括 MCP 工具和 WebFetch
- 返回除檔案文字以外的任何內容的 Read，例如影片、PDF 或重新讀取其內容未變更的檔案
- Edit 或 Write 呼叫，除非您也設定 `OTEL_LOG_TOOL_DETAILS=1`

該事件攜帶這些屬性，每個都在內容限制處截斷（預設值：60 KB）。`由以下控制` 命名屬性在 `OTEL_LOG_TOOL_CONTENT=1` 之上需要的變數，對於 Edit 和 Write，該變數控制事件本身而不是屬性。

| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 說明                                                                                                                                                                             | 由以下控制                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `content`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Read 工具返回的文字，或 Write 呼叫被要求寫入的文字                                                                                                                               | `OTEL_LOG_TOOL_DETAILS` 對於 Write 工具 |
| `output`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Bash 命令的組合輸出，stderr 交錯到 stdout                                                                                                                                        |                                         |
| `diff`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Edit 工具應用的結構化修補程式                                                                                                                                                    | `OTEL_LOG_TOOL_DETAILS`                 |
| `file_path`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Read、Edit 和 Write 工具的目標檔案路徑，重複跨度屬性的相同名稱                                                                                                                   | `OTEL_LOG_TOOL_DETAILS`                 |
| `bash_command`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Bash 工具的命令字串                                                                                                                                                              | `OTEL_LOG_TOOL_DETAILS`                 |
| 父項跨度的 `tool_name` 屬性告訴您事件來自哪個工具。在內容限制處切割的屬性伴隨著 `<attribute>_truncated` 和 `<attribute>_original_length`。 **`claude_code.tool.blocked_on_user`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                                                                                                                                                                                  |                                         |
| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 說明                                                                                                                                                                             | 由以下控制                              |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | ---                                                                                                                                                                              | ---                                     |
| `duration_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 等待權限決定所花費的時間                                                                                                                                                         |                                         |
| `decision`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | `accept` 或 `reject`                                                                                                                                                             |                                         |
| `source`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 決定來源，與[工具決定事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-decision-event)相符                                                                          |                                         |
| **`claude_code.tool.execution`**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                  |                                         |
| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 說明                                                                                                                                                                             | 由以下控制                              |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | ---                                                                                                                                                                              | ---                                     |
| `duration_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 執行工具主體所花費的時間                                                                                                                                                         |                                         |
| `tool_use_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 與父項 `claude_code.tool` 跨度上的相同值                                                                                                                                         |                                         |
| `gen_ai.tool.call.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 與 `tool_use_id` 相同的值。OpenTelemetry GenAI 語義慣例                                                                                                                          |                                         |
| `success`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | `true` 或 `false`                                                                                                                                                                |                                         |
| `error`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 執行失敗時的錯誤類別字串，例如 `Error:ENOENT` 或 `ShellError`。當設定了閘道時包含完整的錯誤訊息                                                                                  | `OTEL_LOG_TOOL_DETAILS`                 |
| `error_class`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 識別碼形式的錯誤類別，字母、數字和底線以外的字元被替換為 `_`，例如 `Error_ENOENT` 或 `ShellError`。即使 `error` 攜帶完整訊息，也會攜帶類別。需要 Claude Code v2.1.268 或更新版本 |                                         |
| **`claude_code.hook`** 此跨度僅在詳細測試版追蹤作用中時出現，這需要 `ENABLE_BETA_TRACING_DETAILED=1` 和 `BETA_TRACING_ENDPOINT`，一對也會[變更日誌和追蹤的去向](https://code.claude.com/docs/zh-TW/env-vars#variables)。在您的殼層、使用者設定或受管設定中設定該對；兩個變數都會在[專案和本機設定](https://code.claude.com/docs/zh-TW/settings-reference#variables-claude-code-ignores-in-env)中被忽略。`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA` 單獨不會產生它。 在互動式 CLI 工作階段中，詳細測試版追蹤也需要您的組織被列入該功能的允許清單。Agent SDK 和非互動式 `-p` 工作階段不需要允許清單。                                                                                                                                                                                                                           |                                                                                                                                                                                  |                                         |
| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 說明                                                                                                                                                                             | 由以下控制                              |
| ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | ---                                                                                                                                                                              | ---                                     |
| `hook_event`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 掛鉤事件類型，例如 `PreToolUse`                                                                                                                                                  |                                         |
| `hook_name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 完整掛鉤名稱，例如 `PreToolUse:Write`                                                                                                                                            |                                         |
| `num_hooks`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 執行的相符掛鉤命令數                                                                                                                                                             |                                         |
| `hook_definitions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | JSON 序列化的掛鉤設定                                                                                                                                                            | `OTEL_LOG_TOOL_DETAILS`                 |
| `duration_ms`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 所有相符掛鉤的掛鐘持續時間                                                                                                                                                       |                                         |
| `num_success`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 成功完成的掛鉤計數                                                                                                                                                               |                                         |
| `num_blocking`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 傳回阻止決定的掛鉤計數                                                                                                                                                           |                                         |
| `num_non_blocking_error`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 在不阻止的情況下失敗的掛鉤計數                                                                                                                                                   |                                         |
| `num_cancelled`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 在完成前取消的掛鉤計數                                                                                                                                                           |                                         |
| 其他內容承載屬性（例如 `new_context`、`system_prompt_preview`、`user_system_prompt`、`tool_input` 和 `response.model_output`）僅在詳細測試版追蹤作用中時發出。它們不是穩定跨度架構的一部分。`new_context` 上的閘道取決於哪個跨度攜帶它，每個副本都在內容限制處截斷（預設值：60 KB）。在 `claude_code.tool` 跨度上，它攜帶該工具呼叫的結果，無論工具如何，並需要 `OTEL_LOG_TOOL_CONTENT=1`。在 `claude_code.interaction` 跨度上，它攜帶使用者提示，在 `claude_code.llm_request` 跨度上，它攜帶該請求的新使用者訊息和工具結果。這兩者都需要 `OTEL_LOG_USER_PROMPTS=1`。`user_system_prompt` 另外需要 `OTEL_LOG_USER_PROMPTS=1`。它僅攜帶您透過 `systemPrompt` SDK 選項或 `--system-prompt` 和 `--append-system-prompt` 旗標提供的系統提示文字，在內容限制處截斷（預設值：60 KB），並且每個工作階段而不是每個請求發出一次。 |                                                                                                                                                                                  |                                         |

### 動態標頭

對於需要動態驗證的企業環境，您可以設定指令碼以動態產生標頭。動態標頭僅適用於 `http/protobuf` 和 `http/json` 協議。使用 `grpc` 協議，Claude Code 僅使用靜態標頭變數 `OTEL_EXPORTER_OTLP_HEADERS` 及其每個信號的變體。

#### 設定設定

新增到您的 `.claude/settings.json`，將路徑替換為您自己的指令碼：

```
{
  "otelHeadersHelper": "/path/to/generate-otel-headers.sh"
}

```

該值可以是可執行檔的路徑，包括包含空格的路徑，或帶有引數的殼層命令行。在 Windows 上，該值始終透過殼層執行，因此在 JSON 值內引用包含空格的路徑。

#### 指令碼需求

指令碼必須輸出有效的 JSON，其中包含代表 HTTP 標頭的字串鍵值對：

```
#!/bin/bash
# Example: Multiple headers
echo "{\"Authorization\": \"Bearer $(get-token.sh)\", \"X-API-Key\": \"$(get-api-key.sh)\"}"

```

如果幫助程式失敗或列印不符合這些需求的輸出，Claude Code 會在以下位置報告錯誤：

- `/status` 輸出
- 偵錯日誌，當使用 [`--debug`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 執行或在工作階段中執行 `/debug` 後
- stderr，在以 `-p` 啟動的非互動式工作階段中

#### 重新整理行為

標頭幫助程式指令碼在啟動時執行，之後定期執行以支援權杖重新整理。預設情況下，指令碼每 29 分鐘執行一次。使用 `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` 環境變數自訂間隔。

### 多團隊組織支援

具有多個團隊或部門的組織可以使用 `OTEL_RESOURCE_ATTRIBUTES` 環境變數新增自訂屬性以區分不同的群組：

```
# Add custom attributes for team identification
export OTEL_RESOURCE_ATTRIBUTES="department=engineering,team.id=platform,cost_center=eng-123"

```

這些自訂屬性包含在所有指標和事件中，允許您：

- 按團隊或部門篩選指標
- 追蹤每個成本中心的成本
- 建立團隊特定的儀表板
- 為特定團隊設定警示

Claude Code 將這些值作為屬性附加到每個指標資料點和事件記錄，除了在 OTLP 資源區塊中傳送它們。因為大多數指標後端將資料點屬性公開為可查詢的標籤，您可以直接按自訂金鑰分組和篩選指標。除了 `vcs.*` [儲存庫屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#repository-attributes)，自訂金鑰永遠不會覆蓋[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)（例如 `user.id` 或 `session.id`）：當金鑰衝突時，Claude Code 會保留內建值。 每個自訂金鑰都會成為每個指標系列上的標籤，因此高基數值會增加指標後端中的儲存成本。若要僅在資源區塊中傳送自訂屬性並從資料點標籤中省略它們，請設定 `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES=false`。請參閱[指標基數控制](https://code.claude.com/docs/zh-TW/monitoring-usage#metrics-cardinality-control)。 `OTEL_RESOURCE_ATTRIBUTES` 環境變數使用逗號分隔的鍵值對，具有嚴格的格式要求：

- **不允許空格** ：值不能包含空格。例如，`user.organizationName=My Company` 無效
- **格式** ：必須是逗號分隔的鍵值對：`key1=value1,key2=value2`
- **允許的字元** ：僅限 US-ASCII 字元，不包括控制字元、空格、雙引號、逗號、分號和反斜線
- **特殊字元** ：允許範圍外的字元必須進行百分比編碼

對於需要空格的值，請改用底線或 camelCase。以下範例使用每種形式設定 `org.name`：

```
export OTEL_RESOURCE_ATTRIBUTES="org.name=Johns_Organization"
export OTEL_RESOURCE_ATTRIBUTES="org.name=JohnsOrganization"

```

您可以對任何字元進行百分比編碼，不僅是被排除的字元。此範例對空格和撇號進行編碼：

```
export OTEL_RESOURCE_ATTRIBUTES="org.name=John%27s%20Organization"

```

將值包裝在引號中不會逃脫空格。例如，`org.name="My Company"` 會導致字面值 `"My Company"`（包括引號），而不是 `My Company`。

### 範例設定

在執行 `claude` 之前設定這些環境變數。下面的每個案例都顯示完整的設定，每個變數都在[常見設定變數](https://code.claude.com/docs/zh-TW/monitoring-usage#common-configuration-variables)下進行說明。若要確認設定生效，請在啟動工作階段後檢查您的後端以查看 `claude_code.session.count` 指標；[快速入門](https://code.claude.com/docs/zh-TW/monitoring-usage#quick-start)涵蓋僅日誌驗證以及當沒有任何內容到達時要檢查的內容。 對於具有 1 秒匯出間隔的主控台偵錯：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=1000

```

對於透過 gRPC 的 OTLP：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

```

對於 Prometheus，從 `http://localhost:9464/metrics` 抓取：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=prometheus

```

在[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments-reference#pass-through-session-child-metrics)上，工作階段僅在執行器的預設容量為 1 時繫結連接埠 9464。在更高的容量下，執行器會改為在其自己的 `/metrics` 端點上重新公開工作階段計數器和量表。 若要將指標傳送到多個匯出工具：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console,otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json

```

若要將指標和日誌傳送到不同的端點或後端：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://metrics.example.com:4318
export OTEL_EXPORTER_OTLP_LOGS_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://logs.example.com:4317

```

若要僅匯出指標，不匯出事件或日誌：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

```

若要僅匯出事件和日誌，不匯出指標：

```
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

```

## 可用的指標和事件

### 標準屬性

所有指標和事件都共享這些標準屬性：

| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 描述                                                                                                                                                          | 控制方式                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `session.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 唯一的工作階段識別碼                                                                                                                                          | `OTEL_METRICS_INCLUDE_SESSION_ID`（預設值：true）                                        |
| `app.version`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 目前的 Claude Code 版本                                                                                                                                       | `OTEL_METRICS_INCLUDE_VERSION`（預設值：false）                                          |
| `app.entrypoint`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 工作階段的啟動方式，例如 `cli`、`sdk-cli`、`sdk-ts`、`sdk-py` 或 `claude-vscode`                                                                              | `OTEL_METRICS_INCLUDE_ENTRYPOINT`（預設值：false）                                       |
| `organization.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 組織 UUID（已驗證時）                                                                                                                                         | 可用時一律包含                                                                           |
| `user.account_uuid`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 帳戶 UUID（已驗證時）                                                                                                                                         | `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`（預設值：true）                                      |
| `user.account_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 帳戶 ID，採用與 Anthropic 管理 API 相符的標籤格式（已驗證時），例如 `user_01BWBeN28...`                                                                       | `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`（預設值：true）                                      |
| `user.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 在首次執行時產生並保存在 `~/.claude.json` 中的隨機匿名識別碼。它不包含任何個人資訊，也不是從您的 Claude 帳戶衍生的。刪除該檔案會在下次執行時產生新的無關值。  | 一律包含                                                                                 |
| `user.email`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 使用者電子郵件地址，來自您的登入或在[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)中來自工作階段本身的認證                         | 可用時一律包含                                                                           |
| `terminal.type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 終端機類型，例如 `iTerm.app`、`vscode`、`cursor` 或 `tmux`                                                                                                    | 偵測到時一律包含                                                                         |
| 來自 `OTEL_RESOURCE_ATTRIBUTES` 的金鑰                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 您設定的自訂屬性，例如 `department` 或 `team.id`。請參閱[多團隊組織支援](https://code.claude.com/docs/zh-TW/monitoring-usage#multi-team-organization-support) | `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES`（預設值：true）                               |
| `vcs.repository.url.full`、`vcs.owner.name`、`vcs.repository.name`、`vcs.provider.name`                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 工作階段儲存庫的身分，衍生自其 `origin` 遠端。請參閱[儲存庫屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#repository-attributes)                   | `OTEL_METRICS_INCLUDE_REPOSITORY`（預設值：false）。需要 Claude Code v2.1.269 或更新版本 |
| 當 Claude Code 登入到[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)時，CLI 會使用來自閘道工作階段的已驗證身分戳記匯出：`user.id` 是 IdP 主體而非匿名安裝識別碼，`user.email` 是已登入的電子郵件，`user.groups` 會以逗號分隔的字串形式攜帶 IdP 群組成員資格。每個匯出也會攜帶 `identity.source: gateway-oidc`。閘道身分最後套用，因此透過 `OTEL_RESOURCE_ATTRIBUTES` 設定的 `user.*` 和 `identity.*` 金鑰在閘道工作階段上會被忽略。 事件另外還包括以下屬性。這些永遠不會附加到指標，因為它們會導致無限的基數： |                                                                                                                                                               |                                                                                          |

- `prompt.id`：UUID，將使用者提示與所有後續事件關聯到下一個提示。請參閱[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)。
- `workspace.host_paths`：在桌面應用程式中選擇的主機工作區目錄，作為字串陣列
- `workflow.run_id`：執行識別碼，前綴為 `wf_`，在屬於[工作流程](https://code.claude.com/docs/zh-TW/workflows)工具執行的代理程式發出的 API 和工具事件上。按一個 `workflow.run_id` 篩選事件會重建該執行的 API 請求和工具結果。識別碼涵蓋工作流程指令碼產生的代理程式以及這些代理程式依次產生的任何代理程式，例如技能叫用。它與工作流程工具結果中報告的執行識別碼相符。在所有其他事件上不存在。需要 Claude Code v2.1.202 或更新版本
- `workflow.name`：工作流程的名稱，其指令碼的 `meta.name`，與 `workflow.run_id` 一起發出。內建工作流程名稱在執行未修改的內建指令碼時逐字出現。使用者撰寫的名稱（包括內建指令碼的編輯副本）會被替換為 `custom`，除非設定了 `OTEL_LOG_TOOL_DETAILS=1`。需要 Claude Code v2.1.202 或更新版本

#### 儲存庫屬性

設定 `OTEL_METRICS_INCLUDE_REPOSITORY=true` 以使用工作階段儲存庫的身分標籤指標和事件，以便共用收集器可以按儲存庫歸因使用情況。需要 Claude Code v2.1.269 或更新版本。 Claude Code 每個工作階段從儲存庫的 `origin` 遠端衍生這些屬性一次。一個儲存庫的 HTTPS 和 SSH 遠端會產生相同的值：

| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 值                                                                                                                  |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `vcs.repository.url.full`                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 儲存庫的瀏覽器 URL，不含 `.git`，例如 `https://github.com/example-org/example-repo`                                 |
| `vcs.owner.name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 擁有者或群組路徑，例如 `example-org`；當遠端路徑只有一個區段時省略                                                  |
| `vcs.repository.name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 裸儲存庫名稱，例如 `example-repo`                                                                                   |
| `vcs.provider.name`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 當 Claude Code 將遠端的主機或 URL 形狀識別為其中一個提供者時為 `github`、`gitlab`、`bitbucket` 或 `gitea`；否則省略 |
| 值會轉換為小寫，遠端 URL 中的認證、查詢字串和片段永遠不會出現在其中。當工作階段沒有 `origin` 遠端、遠端不是 URL 形狀或唯一的封閉儲存庫是您的主目錄時，屬性會被省略。 您在 [`OTEL_RESOURCE_ATTRIBUTES`](https://code.claude.com/docs/zh-TW/monitoring-usage#multi-team-organization-support) 中宣告的 `vcs.*` 金鑰會替換該金鑰的衍生值。如果您宣告 `vcs.repository.url.full`，Claude Code 永遠不會讀取遠端，只會報告您宣告的金鑰。 屬性只流向您自己的匯出器；Anthropic 的遙測會捨棄每個 `vcs.*` 金鑰。 |                                                                                                                     |

### 指標

Claude Code 匯出以下指標。「單位」欄顯示附加到每個指標的 OpenTelemetry 單位字串；計數指標不包含任何單位。

| 指標名稱                                                                                                                                                                                                                                                                                                                              | 描述                         | 單位   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ------ |
| `claude_code.session.count`                                                                                                                                                                                                                                                                                                           | 啟動的 CLI 工作階段計數      | 無     |
| `claude_code.lines_of_code.count`                                                                                                                                                                                                                                                                                                     | 修改的程式碼行數計數         | 無     |
| `claude_code.pull_request.count`                                                                                                                                                                                                                                                                                                      | 建立的提取請求數             | 無     |
| `claude_code.commit.count`                                                                                                                                                                                                                                                                                                            | 建立的 git 提交數            | 無     |
| `claude_code.cost.usage`                                                                                                                                                                                                                                                                                                              | Claude Code 工作階段的成本   | USD    |
| `claude_code.token.usage`                                                                                                                                                                                                                                                                                                             | 使用的權杖數                 | tokens |
| `claude_code.code_edit_tool.decision`                                                                                                                                                                                                                                                                                                 | 程式碼編輯工具權限決定的計數 | 無     |
| `claude_code.active_time.total`                                                                                                                                                                                                                                                                                                       | 總活躍時間                   | s      |
| 當 `prometheus` 是 `OTEL_METRICS_EXPORTER` 中列出的唯一匯出器時，Claude Code 會從匯出的指標中省略 `USD`、`tokens` 和 `s` 單位，以便抓取保持有效的 Prometheus 文字格式。指標名稱不會變更，結合匯出器的設定（例如 `otlp,prometheus`）會保留單位。在 v2.1.216 之前，Prometheus 抓取包含一些抓取器拒絕的僅限 OpenMetrics 的 `# UNIT` 行。 |                              |        |

### 指標詳細資訊

每個指標都包括上面列出的標準屬性。具有其他內容特定屬性的指標如下所述。

#### 工作階段計數器

在每個工作階段開始時遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `start_type`：工作階段的啟動方式。`"fresh"`、`"resume"`、`"continue"` 或 `"agents_view"` 之一。`"agents_view"` 值識別 `claude agents` 儀表板程序，這是使用者啟動的本機 UI 而非對話工作階段。在儀表板中篩選此值以將 UI 程序啟動與對話工作階段分開。

#### 程式碼行計數器

在新增或移除程式碼時遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `type`：（`"added"`、`"removed"`）
- `model`：進行變更的模型的模型識別碼（例如 “claude-sonnet-5”）

#### 提取請求計數器

當 Claude Code 透過 shell 命令或 MCP 工具建立提取請求或合併請求時遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)

#### 提交計數器

透過 Claude Code 建立 git 提交時遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)

#### 成本計數器

在每個 API 請求後遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `model`：模型識別碼（例如 “claude-sonnet-5”）
- `query_source`：發出請求的子系統的類別。`"main"`、`"subagent"` 或 `"auxiliary"` 之一
- `speed`：當請求使用快速模式時為 `"fast"`。否則不存在
- `effort`：套用到請求的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)：`"low"`、`"medium"`、`"high"`、`"xhigh"` 或 `"max"`。當模型不支援努力時不存在。
- `agent.name`：發出請求的子代理程式類型。內建代理程式名稱和來自官方市場的外掛程式的代理程式逐字出現。其他使用者定義的代理程式名稱會被替換為 `"custom"`。當請求不是由具名子代理程式類型發出時不存在。
- `skill.name`：對請求有效的技能，由技能工具、`/` 命令設定或由產生的子代理程式繼承。內建、捆綁、使用者定義和官方市場外掛程式技能名稱逐字出現。第三方外掛程式技能名稱會被替換為 `"third-party"`。當沒有技能有效時不存在。
- `plugin.name`：當有效技能或子代理程式由外掛程式提供時的擁有外掛程式。官方市場外掛程式名稱逐字出現。第三方外掛程式名稱會被替換為 `"third-party"`。當技能和子代理程式都沒有擁有外掛程式時不存在。
- `marketplace.name`：擁有外掛程式的安裝來源市場。僅針對官方市場外掛程式發出。否則不存在。
- `mcp_server.name`：此請求消耗其工具結果的 MCP 伺服器。內建、claude.ai 代理和官方登錄伺服器名稱逐字出現。使用者設定的伺服器名稱會被替換為 `"custom"`。當請求未消耗任何 MCP 工具結果時不存在。在 v2.1.222 之前，Claude Code 在每個 MCP 工具呼叫後的每個請求上設定此屬性，而不僅是在消耗工具結果的請求上，因此聚合它的儀表板在升級後會顯示下降。
- `mcp_tool.name`：此請求消耗其結果的 MCP 工具，具有與 `mcp_server.name` 相同的編輯和版本行為。當請求未消耗任何 MCP 工具結果時不存在。

#### 權杖計數器

在每個 API 請求後遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `type`：（`"input"`、`"output"`、`"cacheRead"`、`"cacheCreation"`）
- `model`：模型識別碼（例如 “claude-sonnet-5”）
- `query_source`：發出請求的子系統的類別。`"main"`、`"subagent"` 或 `"auxiliary"` 之一
- `speed`：當請求使用快速模式時為 `"fast"`。否則不存在
- `effort`：套用到請求的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。請參閱[成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#cost-counter)以取得詳細資訊。
- `agent.name`、`skill.name`、`plugin.name`、`marketplace.name`、`mcp_server.name`、`mcp_tool.name`：請求的技能、外掛程式、代理程式和 MCP 歸因。請參閱[成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#cost-counter)以取得定義和編輯行為。

#### 程式碼編輯工具決定計數器

當使用者接受或拒絕 Edit、Write 或 NotebookEdit 工具使用時遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `tool_name`：工具名稱（`"Edit"`、`"Write"`、`"NotebookEdit"`）
- `decision`：使用者決定（`"accept"`、`"reject"`）
- `source`：決定的來源。`"config"`、`"hook"`、`"user_permanent"`、`"user_temporary"`、`"user_abort"` 或 `"user_reject"` 之一。請參閱[工具決定事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-decision-event)以瞭解每個值的含義。
- `language`：編輯檔案的程式設計語言，例如 `"TypeScript"`、`"Python"`、`"JavaScript"` 或 `"Markdown"`。對於無法識別的副檔名傳回 `"unknown"`。

#### 活躍時間計數器

追蹤實際花費在主動使用 Claude Code 上的時間，不包括閒置時間。此指標在使用者互動期間（例如輸入和讀取回應）以及 CLI 處理期間（例如工具執行和 AI 回應產生）遞增。 **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `type`：`"user"` 用於鍵盤互動，`"cli"` 用於工具執行和 AI 回應

### 事件

Claude Code 透過 OpenTelemetry 日誌/事件匯出以下事件（當設定了 `OTEL_LOGS_EXPORTER` 時）：

#### 事件關聯屬性

當使用者提交提示時，Claude Code 可能會進行多個 API 呼叫並執行多個工具。`prompt.id` 屬性可讓您將所有這些事件與觸發它們的單一提示相關聯。

| 屬性                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 描述                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt.id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | UUID v4 識別碼，連結處理單一使用者提示時產生的所有事件                                                                                                                                                                                                                                                                                               |
| `event.sequence`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0 為基礎的計數器，用於排序事件，按 Claude Code 程序而非按工作階段計數                                                                                                                                                                                                                                                                                |
| `message.uuid`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 訊息的 UUID，如工作階段文字記錄中所保存，`~/.claude/projects/*/*.jsonl` 檔案。出現在 `assistant_response` 上，以及 `user_prompt` 上，除了命令分派外，它可以產生零個或多個訊息。在 `assistant_response` 上，這是回應的最終文字記錄項目，下一個回合的 `parentUuid` 從其鏈接。需要 Claude Code v2.1.214 或更新版本                                      |
| `client_request_id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 用戶端產生的 UUID，作為 `x-client-request-id` 請求標頭傳送。出現在第一方 API 連線上的 `api_request` 和 `api_error` 上；在第三方提供者後端上不存在，以及當請求透過非串流回退重試時。將請求與其回應配對，並且對於永遠不會產生伺服器 `request_id` 的逾時等失敗仍然可用。與 `llm_request` 追蹤跨度上的相同屬性相符。需要 Claude Code v2.1.214 或更新版本 |
| 若要追蹤由單一提示觸發的所有活動，請按特定 `prompt.id` 值篩選您的事件。這會傳回 user_prompt 事件、任何 api_request 事件以及處理該提示時發生的任何 tool_result 事件。 `event.sequence` 在每次 Claude Code 程序啟動時從 0 開始，並在該程序的生命週期內計數。它在 `/clear` 後繼續計數，這會指派新的 `session.id`。如果您[在不分叉的情況下繼續工作階段](https://code.claude.com/docs/zh-TW/how-claude-code-works#resume-or-fork-sessions)，工作階段會保留其 `session.id`，但從繼續它的程序中取得其 `event.sequence` 值，因此在一個工作階段內，稍後的事件可能會攜帶比較早的事件更低的值，或重複一個。若要排序工作階段的事件，請按 `event.timestamp` 排序，並使用 `event.sequence` 排序共享時間戳記的事件。 對於訊息層級重建，每個事件類別都攜帶與工作階段文字記錄中的欄位相符的金鑰。文字記錄項目格式是[Claude Code 內部的](https://code.claude.com/docs/zh-TW/sessions#where-transcripts-are-stored)，在版本之間變更，因此在這些欄位上聯接的管道可能會在任何版本上中斷；將聯接視為版本特定的而非穩定的合約： |                                                                                                                                                                                                                                                                                                                                                      |

- `message.uuid` 在 `user_prompt` 和 `assistant_response` 上
- `request_id` 在 API 事件上，在文字記錄的助理項目上保存為 `requestId`
- `tool_use_id` 在 `tool_result` 和 `tool_decision` 事件上

#### 使用者提示事件

當使用者提交提示時記錄。 **事件名稱** ：`claude_code.user_prompt` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"user_prompt"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `prompt_length`：提示的長度
- `prompt`：提示內容。預設情況下編輯。設定 `OTEL_LOG_USER_PROMPTS=1` 以包含它
- `message.uuid`：產生的使用者訊息的 UUID，與保存的文字記錄項目相符。在命令分派上不存在，它可以產生零個或多個訊息。需要 Claude Code v2.1.214 或更新版本
- `command_name`：當提示叫用命令時的命令名稱。內建和捆綁的命令名稱（例如 `compact` 或 `debug`）按原樣發出；別名（例如 `reset`）按輸入的方式發出而非規範名稱。自訂、外掛程式和 MCP 命令名稱會摺疊為 `custom` 或 `mcp`，除非設定了 `OTEL_LOG_TOOL_DETAILS=1`
- `command_source`：命令存在時的來源：`builtin`、`custom` 或 `mcp`。外掛程式提供的命令報告為 `custom`

#### 助理回應事件

在每個傳回來自模型的文字內容的 API 請求後記錄。僅包含回應的文字區塊；思考區塊和工具使用區塊被排除。需要 Claude Code v2.1.193 或更新版本。 **事件名稱** ：`claude_code.assistant_response` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"assistant_response"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `response_length`：回應文字的長度（以字元為單位）
- `response`：回應文字，在內容限制處截斷（預設為 60 KB）。預設情況下編輯為 `<REDACTED>`。設定 `OTEL_LOG_ASSISTANT_RESPONSES=1` 以包含它。當 `OTEL_LOG_ASSISTANT_RESPONSES` 未設定時，`OTEL_LOG_USER_PROMPTS` 會控制它，因此設定 `OTEL_LOG_ASSISTANT_RESPONSES=0` 以在啟用提示記錄時保持回應編輯
- `model`：模型識別碼（例如 “claude-sonnet-5”）
- `request_id`：來自回應的 `request-id` 標頭的 Anthropic API 請求 ID。僅當 API 傳回時才存在
- `message.uuid`：回應的最終文字記錄項目的 UUID。API 回應會保存為每個內容區塊一個文字記錄項目；這是最後一個，下一個回合的 `parentUuid` 從其鏈接。需要 Claude Code v2.1.214 或更新版本
- `query_source`：發出請求的子系統，例如 `"repl_main_thread"`、`"compact"` 或子代理程式名稱

#### 工具結果事件

當工具完成執行時記錄。如果工具呼叫被拒絕，則不發出；請參閱[工具決定事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-decision-event)以取得拒絕。 **事件名稱** ：`claude_code.tool_result` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"tool_result"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `tool_name`：工具的名稱
- `tool_use_id`：此工具叫用的唯一識別碼。與傳遞給鉤子的 `tool_use_id` 相符，允許 OTel 事件和鉤子擷取資料之間的關聯。
- `success`：`"true"` 或 `"false"`
- `duration_ms`：執行時間（以毫秒為單位）
- `error_type`：工具失敗時的錯誤類別字串，例如 `"Error:ENOENT"` 或 `"ShellError"`
- `error`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：工具失敗時的完整錯誤訊息
- `decision_type`：一律為 `"accept"`，因為此事件僅在工具執行後發出。拒絕的呼叫不會產生工具結果
- `decision_source`：權限決定的來源。`"config"`、`"hook"`、`"user_permanent"` 或 `"user_temporary"` 之一。請參閱[工具決定事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-decision-event)以瞭解每個值的含義。僅拒絕的來源 `"user_abort"` 和 `"user_reject"` 永遠不會出現在此事件上。
- `tool_input_size_bytes`：JSON 序列化工具輸入的大小（以位元組為單位）
- `tool_result_size_bytes`：工具結果的大小（以位元組為單位）
- `mcp_server_scope`：MCP 伺服器範圍識別碼（用於 MCP 工具）
- `vcs.ref.head.revision`、`vcs.ref.head.name`、`vcs.ref.head.type`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：由 Bash 或 PowerShell 工具執行的成功 `git commit` 執行的提交身分。`vcs.ref.head.revision` 是提交 SHA，`vcs.ref.head.name` 是提交所在的分支，`vcs.ref.head.type` 是 `branch`。當提交在分離的 HEAD 上進行時，名稱和類型會被省略。需要 Claude Code v2.1.269 或更新版本
- `tool_parameters`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：包含工具特定參數的 JSON 字串。對於 Claude Desktop 的內建伺服器，在 Claude Desktop 擁有的工作階段中，即使關閉旗標，`mcp_server_name`/`mcp_tool_name` 配對也會包含，與[工具決定事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-decision-event)相同的主機撰寫例外，需要 Claude Code v2.1.214 或更新版本。參數因工具而異：
  - 對於 Bash 工具：包括 `bash_command`、`full_command`、`timeout`、`description` 和 `dangerouslyDisableSandbox`，以及當 `git commit` 命令成功時的 `git_commit_id` 和 `git_branch`。當提交是工作階段工作目錄的 HEAD 時，`git_commit_id` 是完整提交 SHA，否則是 git 的縮寫 SHA。`git_branch` 是提交所在的分支，在分離的 HEAD 上省略
  - 對於桌面應用程式的工作區 Bash 工具，它也將 `tool_name` 報告為 `Bash`：僅包括 `bash_command`、`full_command` 和 `timeout`
  - 對於 MCP 工具：包括 `mcp_server_name`、`mcp_tool_name`
  - 對於技能工具：包括 `skill_name`
  - 對於代理程式工具或舊版工作工具：包括 `subagent_type`
- `tool_input`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：JSON 序列化工具引數。超過 512 個字元的個別值會被截斷，完整承載限制在約 4 K 個字元。適用於所有工具，包括 MCP 工具。

#### API 請求事件

針對每個 API 請求記錄到 Claude。 **事件名稱** ：`claude_code.api_request` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"api_request"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `model`：使用的模型（例如 “claude-sonnet-5”）
- `cost_usd`：以美元計的估計成本
- `cost_usd_micros`：以美元百萬分之一計的估計成本，作為整數發出
- `duration_ms`：請求持續時間（以毫秒為單位）
- `input_tokens`：輸入權杖數
- `output_tokens`：輸出權杖數
- `cache_read_tokens`：從快取讀取的權杖數
- `cache_creation_tokens`：用於快取建立的權杖數
- `request_id`：來自回應的 `request-id` 標頭的 Anthropic API 請求 ID，例如 `"req_011..."`。僅當 API 傳回時才存在。
- `client_request_id`：用戶端產生的 UUID，作為 `x-client-request-id` 請求標頭傳送；請參閱[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)表以瞭解何時存在。需要 Claude Code v2.1.214 或更新版本
- `speed`：`"fast"` 或 `"normal"`，指示快速模式是否有效
- `query_source`：發出請求的子系統，例如 `"repl_main_thread"`、`"compact"` 或子代理程式名稱
- `effort`：套用到請求的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)：`"low"`、`"medium"`、`"high"`、`"xhigh"` 或 `"max"`。當模型不支援努力時不存在。
- `agent.name`、`skill.name`、`plugin.name`、`marketplace.name`、`mcp_server.name`、`mcp_tool.name`：請求的技能、外掛程式、代理程式和 MCP 歸因。請參閱[成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#cost-counter)以取得定義和編輯行為。

#### API 錯誤事件

當 API 請求到 Claude 失敗時記錄。 **事件名稱** ：`claude_code.api_error` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"api_error"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `model`：使用的模型（例如 “claude-sonnet-5”）
- `error`：錯誤訊息
- `status_code`：HTTP 狀態碼作為數字。對於非 HTTP 錯誤（例如連線失敗）不存在。
- `duration_ms`：請求持續時間（以毫秒為單位）
- `attempt`：進行的嘗試總數，包括初始請求（`1` 表示未發生重試）
- `request_id`：來自回應的 `request-id` 標頭的 Anthropic API 請求 ID，例如 `"req_011..."`。僅當 API 傳回時才存在。
- `client_request_id`：用戶端產生的 UUID，作為 `x-client-request-id` 請求標頭傳送。即使失敗（例如逾時或連線錯誤）永遠不會產生伺服器 `request_id` 時也可用；請參閱[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)表以瞭解何時存在。需要 Claude Code v2.1.214 或更新版本
- `speed`：`"fast"` 或 `"normal"`，指示快速模式是否有效
- `query_source`：發出請求的子系統，例如 `"repl_main_thread"`、`"compact"` 或子代理程式名稱
- `effort`：套用到請求的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。當模型不支援努力時不存在。
- `agent.name`、`skill.name`、`plugin.name`、`marketplace.name`、`mcp_server.name`、`mcp_tool.name`：請求的技能、外掛程式、代理程式和 MCP 歸因。請參閱[成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#cost-counter)以取得定義和編輯行為。

#### API 拒絕事件

當 API 請求傳回 `stop_reason: "refusal"` 時記錄。拒絕到達成功回應串流上，而非作為 HTTP 錯誤，因此 `api_error` 事件不會針對它們觸發。此事件可讓您追蹤拒絕頻率並按與 `api_request` 和 `api_error` 相同的屬性分組拒絕。 **事件名稱** ：`claude_code.api_refusal` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"api_refusal"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `model`：來自請求的模型識別碼
- `request_id`：來自回應的 `request-id` 標頭的 Anthropic API 請求 ID，例如 `"req_011..."`。僅當 API 傳回時才存在。
- `query_source`：發出請求的子系統，例如 `"repl_main_thread"`、`"compact"` 或子代理程式名稱。請參閱 [`api_request`](https://code.claude.com/docs/zh-TW/monitoring-usage#api-request-event) 以取得定義。
- `speed`：當[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)有效時為 `"fast"`，或 `"normal"`
- `attempt`：重試嘗試編號。第一次嘗試是 `1`。
- `effort`：套用到請求的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。當模型不支援努力時不存在。
- `server_fallback_hop`：當 API 的伺服器端模型回退已在不同模型上重試此拒絕時為 `true`，因此使用者未看到此特定拒絕。當請求以拒絕結束時為 `false`。單一回合可以發出 `true` 跳躍事件和稍後的 `false` 最終事件，當回退模型也拒絕時。
- `has_category`：當 API 回應攜帶 `stop_details.category` 為 `"cyber"`、`"bio"`、`"frontier_llm"` 或 `"reasoning_extraction"` 時為 `true`。當回應未攜帶類別或值在該集合外時為 `false`。當 `server_fallback_hop` 為 `true` 時不存在，因為跳躍區塊不攜帶 `stop_details`。
- `has_explanation`：當 API 回應攜帶 `stop_details.explanation` 時為 `true`，否則為 `false`。當 `server_fallback_hop` 為 `true` 時不存在。
- `category`：來自 API 回應的 `stop_details.category` 值。`"cyber"`、`"bio"`、`"frontier_llm"` 或 `"reasoning_extraction"` 之一。僅當設定了 `OTEL_LOG_TOOL_DETAILS=1` 且 `has_category` 為 `true` 時才存在。
- `agent.name`、`skill.name`、`plugin.name`、`marketplace.name`、`mcp_server.name`、`mcp_tool.name`：請求的技能、外掛程式、代理程式和 MCP 歸因。請參閱[成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#cost-counter)以取得定義和編輯行為。

#### API 請求本體事件

當設定了 `OTEL_LOG_RAW_API_BODIES` 時，針對每個 API 請求嘗試記錄。每次嘗試發出一個事件，因此使用調整參數的重試各自產生自己的事件。 **事件名稱** ：`claude_code.api_request_body` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"api_request_body"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `body`：JSON 序列化的 Messages API 請求參數，例如系統提示、訊息和工具，在內容限制處截斷（預設為 60 KB）。先前助理回合中的擴展思考內容會被編輯。僅在內聯模式下發出（`OTEL_LOG_RAW_API_BODIES=1`）。
- `body_ref`：包含未截斷本體的 `<dir>/<uuid>.request.json` 檔案的絕對路徑。僅在檔案模式下發出（`OTEL_LOG_RAW_API_BODIES=file:<dir>`）。
- `body_length`：未截斷的本體長度。當 `OTEL_LOG_RAW_API_BODIES=file:<dir>` 時為 UTF-8 位元組，或當 `=1` 時為 UTF-16 程式碼單位
- `body_truncated`：當發生內聯截斷時為 `"true"`。在檔案模式下不存在，未發生截斷時不存在。
- `model`：來自請求參數的模型識別碼
- `query_source`：發出請求的子系統（例如 `"compact"`）
- `request_body_id`：識別此嘗試請求本體的 UUID。成功的嘗試的 [`api_response_body` 事件](https://code.claude.com/docs/zh-TW/monitoring-usage#api-response-body-event)會攜帶相同的值，因此您可以將回應與產生它的確切請求配對。需要 Claude Code v2.1.274 或更新版本

#### API 回應本體事件

當設定了 `OTEL_LOG_RAW_API_BODIES` 時，針對每個成功的 API 回應記錄。 在檔案模式下（`OTEL_LOG_RAW_API_BODIES=file:<dir>`），Claude Code 也會為每個成功的回應將一個 JSON 行附加到 `<dir>/index.jsonl`，包含欄位 `timestamp`、`session_id`、`query_source`、`model`、`request_id`、`message_id`、`message_uuid`、`request_file` 和 `response_file`。讀取它以找到給定文字記錄訊息後面的請求和回應檔案，而無需查詢您的遙測後端。索引檔案需要 Claude Code v2.1.274 或更新版本。 **事件名稱** ：`claude_code.api_response_body` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"api_response_body"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `body`：JSON 序列化的 Messages API 回應，包括 id、內容區塊、使用情況和停止原因，在內容限制處截斷（預設為 60 KB）。擴展思考內容會被編輯。僅在內聯模式下發出（`OTEL_LOG_RAW_API_BODIES=1`）。
- `body_ref`：包含未截斷本體的 `<dir>/<request_id>.response.json` 檔案的絕對路徑。僅在檔案模式下發出（`OTEL_LOG_RAW_API_BODIES=file:<dir>`）。
- `body_length`：未截斷的本體長度。當 `OTEL_LOG_RAW_API_BODIES=file:<dir>` 時為 UTF-8 位元組，或當 `=1` 時為 UTF-16 程式碼單位
- `body_truncated`：當發生內聯截斷時為 `"true"`。在檔案模式下不存在，未發生截斷時不存在。
- `model`：模型識別碼
- `query_source`：發出請求的子系統
- `request_id`：來自回應的 `request-id` 標頭的 Anthropic API 請求 ID，例如 `"req_011..."`。僅當 API 傳回時才存在。
- `request_body_id`：此回應回答的 [`api_request_body` 事件](https://code.claude.com/docs/zh-TW/monitoring-usage#api-request-body-event)的 `request_body_id`。需要 Claude Code v2.1.274 或更新版本
- `message.id`：API 指派給回應的訊息 ID，回應本體的 `id` 欄位。需要 Claude Code v2.1.274 或更新版本
- `message.uuid`：回應的最終文字記錄項目的 UUID。與 `request_body_id` 一起，它將文字記錄訊息連結到其後面的請求和回應本體。需要 Claude Code v2.1.274 或更新版本

#### 工具決定事件

當進行工具權限決定（接受/拒絕）時記錄。 **事件名稱** ：`claude_code.tool_decision` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"tool_decision"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `tool_name`：工具的名稱（例如 “Read”、“Edit”、“Write”、“NotebookEdit”）
- `tool_use_id`：此工具叫用的唯一識別碼。與傳遞給鉤子的 `tool_use_id` 相符，允許 OTel 事件和鉤子擷取資料之間的關聯。
- `decision`：`"accept"` 或 `"reject"`
- `tool_source`：一律存在。工具的來源，作為 CLI 撰寫值的封閉集合。需要 Claude Code v2.1.214 或更新版本
  - `"builtin"`：CLI 自己的工具
  - `"mcp"`：一般 MCP 伺服器
  - `"sdk_host_builtin_mcp"`：內建於 Claude Desktop 本身的進程內伺服器，在 Claude Desktop 擁有的工作階段中。Claude Desktop 擁有它從自己的其中一個進入點 `claude-desktop`、`claude-desktop-3p` 或 `local-agent` 啟動的工作階段，當該工作階段不是嵌套子項時；嵌套工作階段（包括 Claude Code 本身產生的工作階段）將這些伺服器報告為 `"mcp"`
- `source`：決定的來源：
  - `"config"`：自動決定，無需提示，基於專案設定、使用者個人設定中的允許或拒絕規則、企業受管原則、`--allowedTools` 或 `--disallowedTools` 旗標、有效的權限模式、來自同一互動 CLI 工作階段中較早提示的工作階段範圍授予，或因為工具本質上是安全的。事件不指示這些來源中的哪一個相符。Claude Code 也會在權限提示請求本身失敗時報告 `"config"`，例如當代理程式 SDK 的 [`canUseTool`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#canusetool) 回呼或 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 工具傳回無效結果時，或當輸入串流在請求待處理時關閉時。在 v2.1.216 之前，Claude Code 將這些失敗報告為 `"user_reject"`。
  - `"hook"`：`PreToolUse` 或 `PermissionRequest` 鉤子傳回決定。
  - `"user_permanent"`：當使用者在權限提示中選擇「是，不要再問…」時發出，這會將允許規則儲存到其個人設定。在互動 CLI 中，這僅針對該選擇本身發出；稍後與儲存規則相符的呼叫發出 `"config"`。在代理程式 SDK 或非互動 `-p` 工作階段中，初始選擇和稍後的規則相符都發出 `"user_permanent"`。視為接受。
  - `"user_temporary"`：當使用者在權限提示中選擇「是」進行一次性核准時發出，或在檔案編輯或讀取提示上選擇授予工作階段其餘部分存取權限的選項時發出。在互動 CLI 中，這僅針對選擇本身發出；稍後由該工作階段範圍授予允許的呼叫發出 `"config"`。在代理程式 SDK 或非互動 `-p` 工作階段中，選擇和稍後的相符都發出 `"user_temporary"`。視為接受。
  - `"user_abort"`：當使用者在未回答的情況下關閉權限提示時發出。在代理程式 SDK 和非互動 `-p` 工作階段中，這包括在 `canUseTool` 或 `--permission-prompt-tool` 權限請求待處理時中斷回合；在 v2.1.216 之前，Claude Code 將該中斷報告為 `"user_reject"`。視為拒絕。
  - `"user_reject"`：當使用者在提示時選擇「否」時發出。在互動 CLI 中，這僅針對該選擇本身發出；與使用者個人設定中的拒絕規則相符的呼叫發出 `"config"`。在代理程式 SDK 或非互動 `-p` 工作階段中，與個人設定中的拒絕規則相符的呼叫發出 `"user_reject"`。視為拒絕。
- `tool_parameters`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：包含工具特定參數的 JSON 字串。與[工具結果事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-result-event)相同的形狀，減去執行後欄位，例如 `git_commit_id`。對於接受的呼叫，如果權限決定透過 `updatedInput` 重寫工具輸入，值可能與 `tool_result` 不同。使用此屬性查看當 `decision` 為 `"reject"` 時拒絕了哪個命令。
  - 對於 `"sdk_host_builtin_mcp"` 工具：即使關閉 `OTEL_LOG_TOOL_DETAILS`，也會包含 `mcp_server_name` 和 `mcp_tool_name`，因為主應用程式定義這些名稱；沒有它們，對這些內建伺服器之一的拒絕呼叫在預設串流上將無法歸因。對於使用者設定的 MCP 伺服器，事件的 `tool_name` 一律是字面 `"mcp_tool"`，伺服器和工具名稱僅在啟用旗標時出現在 `tool_parameters` 中；引數內容在任何地方都需要旗標。需要 Claude Code v2.1.214 或更新版本
  - 對於 Bash 工具：包括 `bash_command`、`full_command`、`timeout`、`description`、`dangerouslyDisableSandbox`。桌面應用程式的工作區 bash 工具也將 `tool_name` 報告為 `Bash`，但僅包括 `bash_command`、`full_command` 和 `timeout`
  - 對於 MCP 工具：包括 `mcp_server_name`、`mcp_tool_name`
  - 對於技能工具：包括 `skill_name`
  - 對於代理程式工具或舊版工作工具：包括 `subagent_type`

#### 權限模式變更事件

當權限模式變更時記錄，例如從 `Shift+Tab` 循環、退出計畫模式或自動模式閘道檢查。 **事件名稱** ：`claude_code.permission_mode_changed` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"permission_mode_changed"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `from_mode`：先前的權限模式，例如 `"default"`、`"plan"`、`"acceptEdits"`、`"auto"` 或 `"bypassPermissions"`
- `to_mode`：新的權限模式
- `trigger`：導致變更的原因。`"shift_tab"`、`"exit_plan_mode"`、`"auto_gate_denied"` 或 `"auto_opt_in"` 之一。當轉換源自 SDK 或橋接時不存在。

#### 驗證事件

當 `/login` 或 `/logout` 完成時記錄。 **事件名稱** ：`claude_code.auth` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"auth"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `action`：`"login"` 或 `"logout"`
- `success`：`"true"` 或 `"false"`
- `auth_method`：驗證方法，例如 `"oauth"`
- `error_category`：當動作失敗時的分類錯誤類型。永遠不包含原始錯誤訊息
- `status_code`：當動作因 HTTP 錯誤而失敗時的 HTTP 狀態碼作為字串

#### MCP 伺服器連線事件

當 MCP 伺服器連線、斷開連線或無法連線時記錄。 **事件名稱** ：`claude_code.mcp_server_connection` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"mcp_server_connection"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `status`：`"connected"`、`"failed"` 或 `"disconnected"`
- `transport_type`：伺服器傳輸，例如 `"stdio"`、`"sse"` 或 `"http"`
- `server_scope`：伺服器設定的範圍，例如 `"user"`、`"project"` 或 `"local"`
- `duration_ms`：連線嘗試持續時間（以毫秒為單位）
- `error_code`：連線失敗時的錯誤碼
- `is_plugin`：當伺服器由外掛程式提供時為 `true`，否則為 `false`
- `plugin_id_hash`（當 `is_plugin` 為 `true` 時）：外掛程式名稱和市場的穩定雜湊，用於按外掛程式分組事件而不暴露名稱。Claude Code 按[外掛程式載入事件](https://code.claude.com/docs/zh-TW/monitoring-usage#plugin-loaded-event)下所述計算它
- `plugin.name`（當 `is_plugin` 為 `true` 時）：提供伺服器的外掛程式的名稱。對於第三方外掛程式，此值是字面字串 `"third-party"`，除非 `OTEL_LOG_TOOL_DETAILS=1`；這可保護第三方外掛程式名稱預設不出現在日誌中。來自官方 Anthropic 來源的外掛程式一律按名稱識別。`plugin_id_hash` 和 `plugin.name` 屬性流向您自己的監控後端，不會傳送給 Anthropic
- `server_name`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：設定的伺服器名稱
- `error`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：連線失敗時的完整錯誤訊息

#### 內部錯誤事件

當 Claude Code 捕捉到意外的內部錯誤時記錄。僅記錄錯誤類別名稱和 errno 樣式碼。永遠不包含錯誤訊息和堆疊追蹤。針對 Amazon Bedrock、Google Cloud 的代理程式平台或 Microsoft Foundry 執行時，或設定了 `DISABLE_ERROR_REPORTING` 時，不發出此事件。 **事件名稱** ：`claude_code.internal_error` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"internal_error"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `error_name`：錯誤類別名稱，例如 `"TypeError"` 或 `"SyntaxError"`
- `error_code`：Node.js errno 碼，例如錯誤上存在時的 `"ENOENT"`

#### 外掛程式已安裝事件

當外掛程式完成安裝時記錄，來自 `claude plugin install` CLI 命令和互動 `/plugin` UI。 **事件名稱** ：`claude_code.plugin_installed` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"plugin_installed"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `marketplace.is_official`：如果市場是官方 Anthropic 市場則為 `"true"`，否則為 `"false"`
- `install.trigger`：`"cli"` 或 `"ui"`
- `plugin.name`：已安裝外掛程式的名稱。對於第三方市場，僅當 `OTEL_LOG_TOOL_DETAILS=1` 時才包含
- `plugin.version`：在市場項目中宣告時的外掛程式版本。對於第三方市場，僅當 `OTEL_LOG_TOOL_DETAILS=1` 時才包含
- `marketplace.name`：外掛程式的安裝來源市場。對於第三方市場，僅當 `OTEL_LOG_TOOL_DETAILS=1` 時才包含

#### 外掛程式已載入事件

在工作階段開始時針對每個啟用的外掛程式記錄一次。使用此事件來清點您的整個車隊中哪些外掛程式有效，作為記錄安裝動作本身的 `plugin_installed` 的補充。 **事件名稱** ：`claude_code.plugin_loaded` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"plugin_loaded"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `plugin.name`：外掛程式的名稱。對於官方市場和內建捆綁之外的外掛程式，除非 `OTEL_LOG_TOOL_DETAILS=1`，否則值為 `"third-party"`
- `marketplace.name`：外掛程式的安裝來源市場（已知時）。在與 `plugin.name` 相同的條件下編輯為 `"third-party"`
- `plugin.version`：來自外掛程式資訊清單的版本。僅當名稱未編輯且資訊清單宣告版本時才包含
- `plugin.scope`：外掛程式的來源類別：`"official"`、`"community"`、`"org"`、`"user-local"` 或 `"default-bundle"`
- `enabled_via`：外掛程式啟用的方式：`"default-enable"`、`"org-policy"`、`"admin-install"`、`"seed-mount"` 或 `"user-install"`。`"admin-install"` 值表示外掛程式在[**組織設定 > 外掛程式**](https://claude.ai/admin-settings/plugins)中設定為您的組織所需或自動安裝。在 v2.1.246 之前，Claude Code 將這些外掛程式報告為 `"user-install"` 或 `"seed-mount"`
- `plugin_id_hash`：外掛程式名稱和市場的確定性雜湊，僅傳送到您設定的匯出器。可讓您計算整個車隊中載入的不同第三方外掛程式，而無需記錄其名稱。對於[從 claude.ai 同步的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)，Claude Code 使用 claude.ai 為外掛程式報告的市場名稱或 `synced` 雜湊外掛程式名稱。在 v2.1.246 之前，Claude Code 在雜湊中未使用 claude.ai 報告的市場名稱
- `has_hooks`：外掛程式是否貢獻鉤子
- `has_mcp`：外掛程式是否貢獻 MCP 伺服器
- `host_owned_mcp`：當 SDK 主機管理此外掛程式的 MCP 連線且 Claude Code 跳過讀取外掛程式的 MCP 伺服器設定時為 `true`，否則為 `false`。需要 Claude Code v2.1.172 或更新版本
- `skill_path_count`：外掛程式宣告的技能目錄數
- `command_path_count`：外掛程式宣告的命令目錄數
- `agent_path_count`：外掛程式宣告的代理程式目錄數
- `safe_mode`：當工作階段以 [`--safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference) 啟動時為 `"true"`，否則為 `"false"`。在安全模式中，此事件僅報告設定的清單；外掛程式的命令、技能、鉤子和 MCP 伺服器不會載入。需要 Claude Code v2.1.169 或更新版本

#### 技能已啟動事件

當叫用技能時記錄，無論 Claude 是透過技能工具呼叫它還是您將其作為 `/` 命令執行。 **事件名稱** ：`claude_code.skill_activated` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"skill_activated"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `skill.name`：技能的名稱。對於使用者定義和第三方外掛程式技能，除非 `OTEL_LOG_TOOL_DETAILS=1`，否則值為佔位符 `"custom_skill"`
- `invocation_trigger`：技能的觸發方式（`"user-slash"`、`"claude-proactive"` 或 `"nested-skill"`）
- `skill.source`：技能的載入來源（例如 `"bundled"`、`"userSettings"`、`"projectSettings"`、`"plugin"`）
- `skill.kind`：當技能是工作流程技能時為 `"workflow"`。否則不存在
- `plugin.name`（當 `OTEL_LOG_TOOL_DETAILS=1` 或外掛程式來自官方市場時）：當技能由外掛程式提供時的擁有外掛程式的名稱
- `marketplace.name`（當 `OTEL_LOG_TOOL_DETAILS=1` 或外掛程式來自官方市場時）：當技能由外掛程式提供時，擁有外掛程式的安裝來源市場

#### @ 提及事件

當 Claude Code 解析提示中的 `@` 提及時記錄。並非每個提及都發出事件：早期退出路徑，例如權限拒絕、超大檔案、PDF 參考附件和目錄列表失敗，會在不記錄的情況下傳回。 **事件名稱** ：`claude_code.at_mention` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"at_mention"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `mention_type`：提及的類型（`"file"`、`"directory"`、`"agent"`、`"mcp_resource"`、`"peer"`）。`"peer"` 值表示您提及了[您的其他 Claude Code 工作階段之一](https://code.claude.com/docs/zh-TW/cross-session-messaging)。需要 Claude Code v2.1.232 或更新版本
- `success`：提及是否成功解析（`"true"` 或 `"false"`）

#### API 重試已耗盡事件

當 API 請求在多次嘗試後失敗時記錄一次。與最終 `api_error` 事件一起發出。 **事件名稱** ：`claude_code.api_retries_exhausted` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"api_retries_exhausted"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `model`：使用的模型
- `error`：最終錯誤訊息
- `status_code`：HTTP 狀態碼作為數字。對於非 HTTP 錯誤不存在。
- `total_attempts`：進行的嘗試總數
- `total_retry_duration_ms`：所有嘗試的總掛鐘時間
- `speed`：`"fast"` 或 `"normal"`

#### 鉤子已註冊事件

在工作階段開始時針對每個設定的鉤子記錄一次。使用此事件來清點您的整個車隊中哪些鉤子有效，作為每次執行 `hook_execution_start` 和 `hook_execution_complete` 事件的補充。 **事件名稱** ：`claude_code.hook_registered` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"hook_registered"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `hook_event`：鉤子事件類型，例如 `"PreToolUse"` 或 `"PostToolUse"`
- `hook_type`：鉤子實作類型：`"command"`、`"prompt"`、`"mcp_tool"`、`"http"` 或 `"agent"`
- `hook_source`：鉤子的定義位置：`"userSettings"`、`"projectSettings"`、`"localSettings"`、`"flagSettings"`、`"policySettings"` 或 `"pluginHook"`
- `safe_mode`：當工作階段以 [`--safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference) 啟動時為 `"true"`，否則為 `"false"`。需要 Claude Code v2.1.169 或更新版本
- `hook_matcher`（當 `OTEL_LOG_TOOL_DETAILS=1` 時）：鉤子設定中的匹配器字串（已設定時）
- `plugin.name`（當 `hook_source` 為 `"pluginHook"` 時）：貢獻外掛程式的名稱。對於官方市場和內建捆綁之外的外掛程式，除非 `OTEL_LOG_TOOL_DETAILS=1`，否則值為 `"third-party"`
- `plugin_id_hash`（當 `hook_source` 為 `"pluginHook"` 時）：外掛程式名稱和市場的確定性雜湊，僅傳送到您設定的匯出器。可讓您計算不同的貢獻外掛程式而無需記錄其名稱。Claude Code 按[外掛程式載入事件](https://code.claude.com/docs/zh-TW/monitoring-usage#plugin-loaded-event)下所述計算它

#### 鉤子執行開始事件

當一個或多個鉤子開始針對鉤子事件執行時記錄。 **事件名稱** ：`claude_code.hook_execution_start` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"hook_execution_start"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `hook_event`：鉤子事件類型，例如 `"PreToolUse"` 或 `"PostToolUse"`
- `hook_name`：完整鉤子名稱，包括匹配器，例如 `"PreToolUse:Write"`
- `num_hooks`：相符鉤子命令的數量
- `managed_only`：當僅允許受管原則鉤子時為 `"true"`
- `hook_source`：`"policySettings"` 或 `"merged"`
- `safe_mode`：當工作階段以 [`--safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference) 啟動時為 `"true"`，否則為 `"false"`。需要 Claude Code v2.1.169 或更新版本
- `hook_definitions`：JSON 序列化的鉤子設定。僅當啟用詳細 Beta 追蹤和 `OTEL_LOG_TOOL_DETAILS=1` 時才包含

#### 鉤子執行完成事件

當鉤子事件的所有鉤子完成時記錄。 **事件名稱** ：`claude_code.hook_execution_complete` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"hook_execution_complete"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `hook_event`：鉤子事件類型
- `hook_name`：完整鉤子名稱，包括匹配器
- `num_hooks`：相符鉤子命令的數量
- `num_success`：成功完成的計數
- `num_blocking`：傳回阻止決定的計數
- `num_non_blocking_error`：在不阻止的情況下失敗的計數
- `num_cancelled`：在完成前取消的計數
- `total_duration_ms`：所有相符鉤子的掛鐘持續時間
- `managed_only`：當僅允許受管原則鉤子時為 `"true"`
- `hook_source`：`"policySettings"` 或 `"merged"`
- `safe_mode`：當工作階段以 [`--safe-mode`](https://code.claude.com/docs/zh-TW/cli-reference) 啟動時為 `"true"`，否則為 `"false"`。需要 Claude Code v2.1.169 或更新版本
- `hook_definitions`：JSON 序列化的鉤子設定。僅當啟用詳細 Beta 追蹤和 `OTEL_LOG_TOOL_DETAILS=1` 時才包含

#### 鉤子外掛程式指標事件

當官方市場外掛程式鉤子發出每次叫用指標時記錄。僅從官方 Anthropic 市場安裝的外掛程式可以發出這些。第三方市場外掛程式和使用者設定的鉤子不會發出到此事件。使用此事件從您自己的可觀測性堆疊監控外掛程式行為，例如尋找率、成本和持續時間。 **事件名稱** ：`claude_code.hook_plugin_metrics` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"hook_plugin_metrics"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `plugin_id`：`<name>@<marketplace>` 形式的外掛程式識別碼
- `hook_event`：發出指標的鉤子事件類型
- 最多 20 個外掛程式發出的指標金鑰。名稱符合 `^[a-z][a-z0-9_]{0,39}$`。值為布林值或數字。

#### 壓縮事件

當對話壓縮完成時記錄。 **事件名稱** ：`claude_code.compaction` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"compaction"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `trigger`：`"auto"` 或 `"manual"`
- `success`：`"true"` 或 `"false"`
- `duration_ms`：壓縮持續時間
- `pre_tokens`：壓縮前的近似權杖計數
- `post_tokens`：壓縮後的近似權杖計數
- `error`：壓縮失敗時的錯誤訊息
- `precompute_reuse`：僅在 `trigger` 為 `"manual"` 時設定。自動壓縮可以在內容視窗填滿之前在背景中準備摘要，此屬性記錄 `/compact` 是否重用該準備的摘要。`"hit"` 表示它被重用；`"miss_custom_instructions"`、`"miss_hook"` 和 `"miss_not_ready"` 給出改為計算新摘要的原因。需要 Claude Code v2.1.153 或更新版本

#### 子代理程式已完成事件

當[子代理程式](https://code.claude.com/docs/zh-TW/sub-agents)完成並將其結果傳回啟動它的對話時記錄。使用它按子代理程式類型匯總工具使用和執行時間；對於權杖或成本匯總，使用[權杖計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#token-counter)和[成本計數器](https://code.claude.com/docs/zh-TW/monitoring-usage#cost-counter)篩選到 `query_source` `"subagent"`，因為此事件的 `total_tokens` 僅涵蓋最終請求。`"subagent"` 類別也計算來自代理程式型鉤子的請求，它不發出子代理程式事件。 **事件名稱** ：`claude_code.subagent_completed` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"subagent_completed"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `agent_type`：子代理程式類型。內建代理程式名稱和來自官方市場外掛程式的代理程式逐字出現；其他代理程式名稱會被替換為 `"custom"`，除非設定了 `OTEL_LOG_TOOL_DETAILS=1`
- `agent.source`：代理程式定義的來源：`built-in`、`plugin` 或定義自訂代理程式的設定來源，例如 `userSettings` 或 `projectSettings`
- `is_built_in`：子代理程式是否為內建代理程式類型
- `is_async`：子代理程式是否在[背景](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)中執行
- `total_tokens`：子代理程式最終 API 請求的權杖足跡：該一個請求的輸入、快取建立、快取讀取和輸出權杖，大約是子代理程式在完成時的內容大小。不是整個執行的總和
- `total_tool_uses`：子代理程式在整個執行過程中進行的工具呼叫數
- `duration_ms`：執行時間（以毫秒為單位）
- `model`：子代理程式解析為執行的模型
- `final_model`：產生子代理程式最終回應的模型，在回退等中途切換後與 `model` 不同。需要 Claude Code v2.1.212 或更新版本
- `model_swapped`：是否有多個模型為子代理程式的請求提供服務。需要 Claude Code v2.1.212 或更新版本
- `plugin_id_hash`、`plugin.name`：針對外掛程式提供的代理程式存在。官方市場外掛程式名稱逐字出現；其他外掛程式名稱會被替換為 `"third-party"`，除非設定了 `OTEL_LOG_TOOL_DETAILS=1`

#### 意見反應調查事件

當顯示或回答工作階段品質調查時記錄。請參閱[工作階段品質調查](https://code.claude.com/docs/zh-TW/data-usage#session-quality-surveys)以瞭解調查收集的內容以及如何控制它們。 **事件名稱** ：`claude_code.feedback_survey` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"feedback_survey"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `event_type`：調查生命週期事件，例如 `"appeared"`、`"responded"` 或 `"transcript_prompt_appeared"`
- `appearance_id`：唯一 ID，連結為一個調查實例發出的事件
- `survey_type`：哪個調查產生事件。`"session"` 是「Claude 做得如何？」評分提示
- `response`：使用者在 `responded` 事件上的選擇
- `enabled_via_override`：當設定了 [`CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL`](https://code.claude.com/docs/zh-TW/env-vars) 時為 `true`。作為布林值而非字串發出。出現在 `session` 調查事件上。篩選此屬性以確認整個車隊中套用了覆蓋

#### 保留期掃描事件

在保留期清理掃描執行時記錄一次，該掃描刪除[工作階段文字記錄和其他應用程式資料](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)早於 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 設定的資料。Claude Code 在背景中最多每個工作階段執行一次掃描，刪除任何內容的執行仍會發出事件。如果 Claude Code 在過去 24 小時內在同一機器上的任何工作階段中執行了掃描，它會將此工作階段的掃描延遲至少 10 分鐘，因此更早退出的工作階段不會發出任何內容。當您使用 `--bare` 執行 `claude -p` 時，Claude Code 不會執行掃描，也不會發出任何內容。 與此頁面上的每個 OTel 事件一樣，它僅流向您設定的遙測後端。需要 Claude Code v2.1.227 或更新版本。 當 Claude Code 無法安全地確定保留期時，它會暫停掃描並發出事件，`result` 設定為 `"skipped"` 和 `skip_reason`。當[受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)設定 `cleanupPeriodDays` 時，受管值會固定保留期，即使較低優先順序範圍中的設定檔案損壞或無效，掃描也會執行。當 `managed-settings.json` 本身無法讀取時，Claude Code 仍會暫停掃描，除非[受管層](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)從其他地方（例如伺服器受管設定或損壞檔案旁的 `managed-settings.d/` 放置）提供 `cleanupPeriodDays`。刪除計數器屬性僅在 `result` 為 `"complete"` 時存在。 **事件名稱** ：`claude_code.retention_sweep` **屬性** ：

- 所有[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)
- `event.name`：`"retention_sweep"`
- `event.timestamp`：ISO 8601 時間戳記
- `event.sequence`：單調遞增的計數器，用於排序工作階段內的事件，在[事件關聯屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#event-correlation-attributes)下所述
- `result`：掃描執行時為 `"complete"`，Claude Code 暫停時為 `"skipped"`
- `period_days`：來自合併設定的 `cleanupPeriodDays` 值（以天為單位），或當沒有來源設定時為 `30`。在跳過的事件上，掃描會使用的值，從 Claude Code 可以讀取的設定來源計算
- `used_default`：當沒有可讀的設定來源設定 `cleanupPeriodDays` 時為 `"true"`，否則為 `"false"`。在完成事件上，`"true"` 表示套用了 30 天預設值
- `skip_reason`：Claude Code 暫停掃描的原因。僅當 `result` 為 `"skipped"` 時存在：
  - `"user_source_disabled"`：使用者設定被排除，例如透過 [`--setting-sources`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 旗標或 SDK 的 [`settingSources`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options) 選項，且沒有啟用的來源提供 `cleanupPeriodDays`
  - `"settings_unknowable"`：設定檔案無法讀取或解析，因此 `cleanupPeriodDays` 或 `desktopSessionCleanupPeriodDays` 可能設定為 Claude Code 無法看到的值
  - `"settings_invalid_key_set"`：設定有驗證錯誤且 `cleanupPeriodDays` 或 `desktopSessionCleanupPeriodDays` 已明確設定，因此回退到預設值可能會刪除或保留針對該設定的檔案
- `transcripts_deleted`：掃描刪除的工作階段文字記錄（頂層 `~/.claude/projects/*/*.jsonl` 檔案）數
- `transcripts_exempted_desktop`：超過保留期的文字記錄數，掃描在 [Claude Desktop 和 Cowork 規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)下保留。這些不計入 `files_past_cutoff`。需要 Claude Code v2.1.248 或更新版本
- `session_files_deleted`：工作階段檔案掃描刪除的成品數：文字記錄加上每個工作階段的伴隨檔案，例如邊車、錄製和工具結果
- `artifacts_deleted`：掃描跨越的資料目錄刪除的總項目，包括工作階段檔案。某些掃描將整個移除的目錄樹計為一個項目，少數清理通過不貢獻計數器，因此將值視為下限而非精確檔案計數
- `files_retained_fresh`：檢查並保留在原位的檔案，因為它們仍在保留期內。僅每個檔案掃描計算這些，因此值是下限；非零值是正常穩定狀態
- `files_past_cutoff`：早於保留期的檔案，掃描無法刪除，例如因為權限錯誤或檔案被保持開啟。值高於零表示檔案超過了設定的保留期；零不是沒有任何檔案的證明，因為整個目錄的移除失敗計入 `error_count`
- `error_count`：掃描在列出或刪除檔案時遇到的錯誤數

## 解釋指標和事件資料

匯出的指標和事件支援一系列分析：

### 使用情況監控

| 指標                                                          | 分析機會                                                                                         |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `claude_code.token.usage`                                     | 按 `type`（輸入/輸出）、使用者、團隊、模型、`skill.name`、`plugin.name` 或 `agent.name` 進行細分 |
| `claude_code.session.count`                                   | 追蹤一段時間內的採用和參與度                                                                     |
| `claude_code.lines_of_code.count`                             | 透過追蹤程式碼新增和移除來衡量生產力，按模型進行細分                                             |
| `claude_code.commit.count` & `claude_code.pull_request.count` | 了解對開發工作流程的影響                                                                         |

### 成本監控

`claude_code.cost.usage` 指標有助於：

- 追蹤跨團隊或個人的使用趨勢
- 識別高使用量工作階段以進行最佳化
- 透過 `skill.name`、`plugin.name` 和 `agent.name` 屬性將支出歸因於特定技能、外掛程式或子代理類型

成本指標是近似值。如需官方帳單資料，請參閱您的 API 提供者（Claude Console、Amazon Bedrock 或 Google Cloud 的 Agent Platform）。 Claude Code 將每個串流回應計入成本和權杖指標中恰好一次，包括當閘道或代理在 `ANTHROPIC_BASE_URL` 後面跨多個框架逐步串流使用情況時。在 v2.1.214 之前，在多個框架中攜帶使用情況的串流會使 `claude_code.cost.usage` 和 `claude_code.token.usage` 膨脹，大約每個額外框架增加一個完整請求。

### 警報和分段

要考慮的常見警報：

- 成本尖峰
- 異常的權杖消耗
- 來自特定使用者的高工作階段量

所有指標都可以按[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)進行分段。`model` 屬性可在 `claude_code.token.usage`、`claude_code.cost.usage` 上使用，以及從 v2.1.172 開始，`claude_code.lines_of_code.count` 上也可使用。 提交的按模型細分只能透過在 `session.id` 上與權杖或成本指標進行聯接來近似，因為一個工作階段可以跨越多個模型。篩選權杖或成本端的列，使 `query_source` 為 `"main"`，以便輔助和子代理請求不會將工作階段的提交歸因於未進行提交的模型。

### 偵測重試耗盡

Claude Code 在內部重試失敗的 API 請求，並僅在放棄後才發出單個 `claude_code.api_error` 事件，因此事件本身是該請求的終端訊號。中間重試嘗試不會作為單獨的事件記錄。 事件上的 `attempt` 屬性記錄進行的嘗試總次數。`CLAUDE_CODE_MAX_RETRIES` 預設為 10，上限為 15。在 v2.1.199 或更新版本上，您可以設定 `CLAUDE_CODE_RETRY_WATCHDOG` 以提高預設值並移除上限。 當請求在暫時性錯誤上耗盡所有重試時，`attempt` 等於該有效限制加一：預設為 11，除非設定了看門狗，否則永遠不超過 16。較低的值表示不可重試的錯誤，例如 `400` 回應，或具有自己較小重試預算的原因。例如，Claude Code 最多重試兩次載入 AWS 或 Google Cloud 認證的失敗。 若要區分從一個恢復的工作階段與停滯的工作階段，請按 `session.id` 分組事件，並檢查錯誤後是否存在更晚的 `api_request` 事件。

### 事件分析

事件資料提供了對 Claude Code 互動的詳細見解： **工具使用模式** ：分析工具結果事件以識別：

- 最常使用的工具
- 工具成功率
- 平均工具執行時間
- 按工具類型的錯誤模式

**效能監控** ：追蹤 API 請求持續時間和工具執行時間以識別效能瓶頸。

## 稽核安全事件

OpenTelemetry 事件是 Claude Code 活動的稽核資料來源。每個事件都帶有身份屬性，將工具呼叫、MCP 活動和權限決定與觸發它們的使用者相關聯。OTLP 日誌匯出器可以將這些事件傳遞到任何具有 OTLP 接收器的安全資訊和事件管理 (SIEM) 平台，或轉發到您的 SIEM 的 OpenTelemetry Collector。

### 將屬性操作歸因於使用者

每個事件上的[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)包括已驗證使用者的身份：使用 Claude 帳戶登入時的 `user.email`、`user.account_uuid`、`user.account_id` 和 `organization.id`，或在[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)中，當工作階段自身的認證攜帶它們時，加上 `user.id` 和每個工作階段的 `session.id`。`user.id` 是安裝範圍的識別碼，除了在 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 工作階段上，其中它是來自閘道簽發令牌的 IdP 主體。 MCP 工具呼叫、Bash 命令和檔案編輯因此歸因於啟動工作階段的開發人員。Claude Code 不在單獨的服務帳戶下運作；每個事件上記錄的身份是開發人員自己的 Claude 帳戶，或開發人員在 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 工作階段上的 IdP 身份。 當 Claude Code 使用直接 API 金鑰進行身份驗證，或針對 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 進行身份驗證時，工作階段中沒有 Claude 帳戶，僅填充 `user.id` 和 `session.id`。在這些部署中，使用 `OTEL_RESOURCE_ATTRIBUTES` 自行附加使用者身份，透過[受管設定](https://code.claude.com/docs/zh-TW/monitoring-usage#administrator-configuration)檔案或啟動包裝器按使用者設定。Claude apps gateway 工作階段不需要任何這些：CLI 會自動標記 IdP 身份，如[標準屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#standard-attributes)中所述。

```
export OTEL_RESOURCE_ATTRIBUTES="enduser.id=jdoe@example.com,enduser.directory_id=S-1-5-21-..."

```

### 稽核 MCP 活動

若要使用完整呼叫詳情捕捉 MCP 伺服器活動，請啟用日誌匯出器並設定 `OTEL_LOG_TOOL_DETAILS=1`。每個 MCP 操作然後產生結構化事件，其中包含伺服器名稱、工具名稱和呼叫引數以及標準身份屬性：

| 事件                                                   | 它為 MCP 記錄的內容                                                                                                                                                  |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mcp_server_connection`                                | 伺服器連線、斷開連線和連線失敗，包含 `server_name`、`transport_type`、`server_scope` 和錯誤詳情                                                                      |
| `tool_result`                                          | 每個 MCP 工具呼叫，包含 `tool_name` 和 `mcp_server_scope`、包含 `mcp_server_name` 和 `mcp_tool_name` 的 `tool_parameters` 承載，以及包含呼叫引數的 `tool_input` 承載 |
| `tool_decision`                                        | 呼叫是否被允許或拒絕，以及決定是來自配置、hook 還是使用者，以及包含 `mcp_server_name` 和 `mcp_tool_name` 的 `tool_parameters` 承載                                   |
| 沒有 `OTEL_LOG_TOOL_DETAILS`，這些事件會捨棄識別詳情： |                                                                                                                                                                      |

- `tool_result`：保留 `mcp_server_scope` 和 `tool_name` 對使用者設定的伺服器編輯為字面上的 `"mcp_tool"`，省略引數內容。對於 Claude Desktop 的內建伺服器，在 Claude Desktop 擁有的工作階段中，它也保留 `tool_parameters` 內的 `mcp_server_name`/`mcp_tool_name` 配對，與 `tool_decision` 相同的主機編寫例外，需要 Claude Code v2.1.214 或更新版本
- `tool_decision`：保留 `tool_source` 和 `tool_name` 對使用者設定的伺服器編輯為字面上的 `"mcp_tool"`，省略引數內容。對於 Claude Desktop 的內建伺服器，在 Claude Desktop 擁有的工作階段中，它也保留 `tool_parameters` 內的 `mcp_server_name`/`mcp_tool_name` 配對；`tool_source` 和名稱配對都需要 Claude Code v2.1.214 或更新版本
- `mcp_server_connection`：省略 `server_name` 和錯誤訊息，但保留 `is_plugin`、`plugin_id_hash` 和 `plugin.name`，非 Anthropic plugin 名稱被編輯為字面上的 `"third-party"`，因此 plugin 提供的伺服器在沒有詳細日誌的情況下仍然可以區分

### 將安全問題對應到事件

建立偵測規則時，查詢您想要監控的訊號並查詢您的後端以取得相應的事件和屬性：

| 訊號                                                                                                     | 事件                                                                              | 關鍵屬性                                                     |
| -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 工具呼叫被允許或拒絕，以及由什麼                                                                         | `tool_decision`                                                                   | `decision`、`source`、`tool_name`、`tool_parameters`         |
| 權限模式升級                                                                                             | `permission_mode_changed`                                                         | `from_mode`、`to_mode`、`trigger`                            |
| 原則 hook 阻止了操作                                                                                     | `hook_execution_complete`                                                         | `hook_event`、`num_blocking`                                 |
| 登入、登出和身份驗證失敗                                                                                 | `auth`                                                                            | `action`、`success`、`error_category`                        |
| MCP 伺服器連線或失敗                                                                                     | `mcp_server_connection`                                                           | `status`、`server_name`、`is_plugin`、`error_code`           |
| Plugin 已安裝及其來源                                                                                    | `plugin_installed`                                                                | `plugin.name`、`marketplace.name`、`marketplace.is_official` |
| 執行的命令和觸及的檔案                                                                                   | `tool_result`（已執行）或 `tool_decision`（已拒絕）搭配 `OTEL_LOG_TOOL_DETAILS=1` | `tool_parameters`；`tool_input`（僅限 `tool_result`）        |
| Claude Code 僅發出原始事件流。異常偵測、基線設定、跨工作階段關聯和警報是您的 SIEM 或可觀測性後端的責任。 |                                                                                   |                                                              |

### 將事件傳送到 SIEM

將 `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` 指向您的 SIEM 的 OTLP 接收器，或指向轉發到您的 SIEM 的原生擷取 API 的 OpenTelemetry Collector。以下受管設定範例僅匯出事件，並啟用完整工具詳情以進行 MCP 和 Bash 稽核：

```
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_LOG_TOOL_DETAILS": "1",
    "OTEL_EXPORTER_OTLP_LOGS_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://siem.example.com:4318/v1/logs",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer your-siem-token"
  }
}

```

若要確認事件已到達，請在執行此設定的工作階段中提交提示，並檢查您的 SIEM 是否有 `claude_code.user_prompt` 事件。如果沒有任何內容到達，請執行 `claude --debug` 並檢查偵錯日誌中的 `[3P telemetry]` 匯出錯誤。

## 後端考量

您選擇的指標、日誌和追蹤後端決定了您可以執行的分析類型：

### 對於指標

- **時間序列資料庫** ：速率計算、聚合指標
- **欄式存儲** ：複雜查詢、唯一使用者分析
- **功能完整的可觀測性平台** ：進階查詢、視覺化、警報

### 對於事件/日誌

- **日誌聚合系統** ：全文搜尋、日誌分析
- **欄式存儲** ：結構化事件分析
- **功能完整的可觀測性平台** ：指標和事件之間的關聯

### 對於追蹤

選擇支援分散式追蹤儲存和跨度關聯的後端：

- **分散式追蹤系統** ：跨度視覺化、請求瀑布圖、延遲分析
- **功能完整的可觀測性平台** ：追蹤搜尋和與指標和日誌的關聯

對於需要日活躍使用者/週活躍使用者/月活躍使用者 (DAU/WAU/MAU) 指標的組織，請考慮支援高效唯一值查詢的後端。

## 服務資訊

所有指標和事件都使用以下資源屬性匯出：

- `service.name`：終端機工作階段為 `claude-code`，從 [Claude Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop)中的 Code 標籤啟動的工作階段為 `claude-code-desktop`
- `service.version`：目前的 Claude Code 版本，或 Code 標籤工作階段的 Desktop 應用程式版本
- `os.type`：作業系統類型（例如，`linux`、`darwin`、`windows`）
- `os.version`：作業系統版本字串
- `host.arch`：主機架構（例如，`amd64`、`arm64`）
- `wsl.version`：WSL 版本號（僅在 Windows Subsystem for Linux 上執行時出現）
- 計量器名稱：`com.anthropic.claude_code`

如果您的收集器管道或儀表板在 `service.name = claude-code` 上進行篩選，請將 `claude-code-desktop` 新增至篩選條件，以同時擷取來自 Code 標籤工作階段的遙測資料。

## ROI 測量資源

如需有關測量 Claude Code 投資回報率的綜合指南，包括遙測設定、成本分析、生產力指標和自動化報告，請參閱 [Claude Code ROI 測量指南](https://github.com/anthropics/claude-code-monitoring-guide)。此儲存庫提供現成可用的 Docker Compose 配置、Prometheus 和 OpenTelemetry 設定，以及用於產生與 Linear 等工具整合的生產力報告的範本。

## 安全性和隱私

- OpenTelemetry 匯出到您的後端是選擇加入的，需要明確配置。如需了解 Anthropic 的獨立營運遙測以及如何停用它，請參閱[資料使用](https://code.claude.com/docs/zh-TW/data-usage#telemetry-services)
- 原始檔案內容和程式碼片段不包含在指標或事件中。追蹤跨度是單獨的資料路徑：請參閱下面的 `OTEL_LOG_TOOL_CONTENT` 項目
- 透過 OAuth 驗證時，`user.email` 包含在遙測屬性中，僅傳送到您配置的 OTel 端點，絕不會傳送到 Anthropic。如果這對您的組織是個問題，請與您的遙測後端合作以篩選或編輯此欄位
- 預設不收集使用者提示內容。僅記錄提示長度。若要包含提示內容，請設定 `OTEL_LOG_USER_PROMPTS=1`。在詳細的測試版追蹤下，此變數的作用範圍更廣：它也控制 [`new_context` 跨度屬性](https://code.claude.com/docs/zh-TW/monitoring-usage#new-context-gates)，該屬性在 `claude_code.llm_request` 跨度上帶有工具結果
- 助理回應文字預設不收集。僅記錄回應長度。若要包含回應文字，請設定 `OTEL_LOG_ASSISTANT_RESPONSES=1`。如同 Claude Code 的所有 OpenTelemetry 資料，回應文字僅傳送到您配置的 OTel 端點，絕不會傳送到 Anthropic。當此變數未設定時，`OTEL_LOG_USER_PROMPTS` 會用作備用方案，因此如果您想要提示內容而不要回應內容，請設定 `OTEL_LOG_ASSISTANT_RESPONSES=0`
- 工具輸入引數和參數預設不記錄。若要包含它們，請設定 `OTEL_LOG_TOOL_DETAILS=1`。針對 Claude Desktop 的內建伺服器，在 Claude Desktop 擁有的工作階段中，`tool_decision` 和 `tool_result` 帶有 `mcp_server_name`/`mcp_tool_name` 配對，即主機撰寫的名稱而非引數內容，即使旗標關閉也是如此。此例外需要 Claude Code v2.1.214 或更新版本。此資料僅傳送到您配置的 OTEL 端點，絕不會傳送到 Anthropic。引數仍可能包含敏感值，因此請根據需要配置您的遙測後端以篩選或編輯這些屬性。啟用時：
  - `tool_result` 和 `tool_decision` 事件包含 `tool_parameters` 屬性，其中包含 Bash 命令、MCP 伺服器和工具名稱以及技能名稱。`full_command` 等欄位未截斷地發出
  - `tool_result` 事件另外包含 `tool_input` 屬性，其中包含檔案路徑、URL、搜尋模式和其他引數。超過 512 個字元的個別值會被截斷，總計上限約為 4 K 字元
  - `user_prompt` 事件包含自訂、plugin 和 MCP 命令的逐字 `command_name`
  - 追蹤跨度包含相同的 `tool_input` 屬性和輸入衍生屬性，例如 `file_path`，截斷方式與 `tool_input` 相同
- 工具內容預設不在追蹤跨度中記錄。若要包含它，請設定 `OTEL_LOG_TOOL_CONTENT=1`。`claude_code.tool` 跨度隨後帶有 [`tool.output` 跨度事件](https://code.claude.com/docs/zh-TW/monitoring-usage#tool-output-span-event)，其中包含原始檔案內容和 Bash 命令輸出，在內容限制（預設 60 KB）處按屬性截斷。工具內容也透過 [`new_context` 到達跨度，其控制因跨度而異](https://code.claude.com/docs/zh-TW/monitoring-usage#new-context-gates)。根據需要配置您的遙測後端以篩選或編輯這些屬性
- 原始 Anthropic Messages API 請求和回應主體預設不記錄。若要包含它們，請在您的 shell、使用者設定或受管設定中設定 `OTEL_LOG_RAW_API_BODIES`。在[專案和本機設定](https://code.claude.com/docs/zh-TW/settings-reference#variables-claude-code-ignores-in-env)中會被忽略。主體包含完整的對話歷史記錄，包括系統提示、每個先前的使用者和助手輪次以及工具結果，因此啟用此選項意味著同意其他 `OTEL_LOG_*` 內容旗標會揭露的所有內容。Claude Code 始終從這些主體中編輯 Claude 的擴展思考內容，無論其他設定如何。您設定的值決定了 Claude Code 如何傳遞主體：
  - 使用 `=1` 時，Claude Code 為每個 API 呼叫發出 `api_request_body` 和 `api_response_body` 日誌事件。事件的 `body` 屬性帶有 JSON 序列化的承載，在內容限制（預設 60 KB）處截斷
  - 使用 `=file:<dir>` 時，Claude Code 將未截斷的主體寫入該目錄下的 `.request.json` 和 `.response.json` 檔案，事件帶有 `body_ref` 路徑而不是內聯主體。使用日誌收集器或邊車傳送目錄，而不是透過遙測流 對於每個成功的回應，Claude Code 也會在該目錄中的 `index.jsonl` 附加一行，將回應檔案連結到產生它的請求檔案以及它成為的文字記錄訊息。每一行不包含任何訊息內容，[API 回應主體事件](https://code.claude.com/docs/zh-TW/monitoring-usage#api-response-body-event)部分列出其欄位。索引檔案需要 Claude Code v2.1.274 或更新版本

## 在 Amazon Bedrock 上監控 Claude Code

如需 Amazon Bedrock 上 Claude Code 使用情況監控的詳細指南，請參閱 [Claude Code 監控實作 (Amazon Bedrock)](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md)。 是否 助手
