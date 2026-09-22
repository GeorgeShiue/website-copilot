本頁列出 Claude Code 顯示的執行時錯誤及如何從每個錯誤中復原，以及當回應似乎有問題但沒有錯誤時要檢查的內容。如需安裝錯誤（例如 `command not found` 或設定期間的 TLS 失敗），請參閱[疑難排解安裝和登入](https://code.claude.com/docs/zh-TW/troubleshoot-install)。 除了[包裝程式和 IDE 錯誤](https://code.claude.com/docs/zh-TW/errors#wrapper-and-ide-errors)（由啟動程式列印而非 Claude Code 本身列印）外，這些錯誤和復原命令適用於 CLI、[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop)和[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，因為這三者都包裝相同的 Claude Code CLI。如需其他表面特定的問題，請參閱該表面頁面上的疑難排解部分。 Claude Code 呼叫 Claude API 以取得模型回應，因此大多數執行時錯誤對應到基礎 API 錯誤代碼。本頁涵蓋每個錯誤在 Claude Code 中的含義及如何復原。如需原始 HTTP 狀態代碼定義，請參閱 [Claude Platform 錯誤參考](https://platform.claude.com/docs/en/api/errors)。

## 找到您的錯誤

將您看到的訊息與下面的部分進行比對。

| 訊息                                                                                                                                                                                                                                                                 | 部分                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `API Error: 500 Internal server error`                                                                                                                                                                                                                               | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#api-error-500-internal-server-error)                                                                                               |
| `API Error: Repeated 529 Overloaded errors`                                                                                                                                                                                                                          | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#api-error-repeated-529-overloaded-errors)                                                                                          |
| `Request timed out`                                                                                                                                                                                                                                                  | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#request-timed-out)，或如果訊息提及您的網際網路連線，則為[網路](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api) |
| `API Error: No response from API`                                                                                                                                                                                                                                    | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#no-response-from-api)                                                                                                              |
| `Server error mid-response. The response above may be incomplete.`                                                                                                                                                                                                   | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#the-response-above-may-be-incomplete)                                                                                              |
| `Connection lost mid-response` / `Your computer went to sleep mid-response` / `The response stopped arriving`                                                                                                                                                        | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#the-response-above-may-be-incomplete)                                                                                              |
| `Connection closed mid-response` / `Response stalled mid-stream`                                                                                                                                                                                                     | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#the-response-above-may-be-incomplete)                                                                                              |
| `Connection lost before a response was produced` / `Your computer went to sleep before a response was produced` / `The response stalled before a response was produced`                                                                                              | [自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)                                                                                                                   |
| `Connection closed while thinking` / `Response stalled while thinking`                                                                                                                                                                                               | [自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)                                                                                                                   |
| `Connection lost while your computer was asleep`                                                                                                                                                                                                                     | [自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)                                                                                                                   |
| `<model> is temporarily unavailable, so auto mode cannot determine the safety of...`                                                                                                                                                                                 | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)                                                                                |
| `Auto mode could not evaluate this action and is blocking it for safety`                                                                                                                                                                                             | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)                                                                                |
| `Auto mode classifier transcript exceeded context window`                                                                                                                                                                                                            | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)                                                                                |
| `Agent aborted: auto mode classifier request refused by the safety safeguard`                                                                                                                                                                                        | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)                                                                                |
| `Agent terminated early due to an API error`                                                                                                                                                                                                                         | [伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#agent-terminated-early-due-to-an-api-error)                                                                                        |
| `You've hit your session limit` / `You've hit your weekly limit` / `You've hit your Opus limit` / `You've hit your Sonnet limit`                                                                                                                                     | [使用限制](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-session-limit)                                                                                                        |
| `Usage credits required for 1M context`                                                                                                                                                                                                                              | [使用限制](https://code.claude.com/docs/zh-TW/errors#usage-credits-required-for-1m-context)                                                                                               |
| `the prompt to confirm went unanswered — nothing was sent`                                                                                                                                                                                                           | [使用限制](https://code.claude.com/docs/zh-TW/errors#the-prompt-to-confirm-went-unanswered)                                                                                               |
| `Server is temporarily limiting requests`                                                                                                                                                                                                                            | [使用限制](https://code.claude.com/docs/zh-TW/errors#server-is-temporarily-limiting-requests)                                                                                             |
| `Request rejected (429)`                                                                                                                                                                                                                                             | [使用限制](https://code.claude.com/docs/zh-TW/errors#request-rejected-429)                                                                                                                |
| `Credit balance is too low`                                                                                                                                                                                                                                          | [使用限制](https://code.claude.com/docs/zh-TW/errors#credit-balance-is-too-low)                                                                                                           |
| `You've hit your monthly spend limit` / `You've hit your individual spend limit` / `You've hit your org's monthly spend limit` / `You've hit your channel's monthly spend limit` / `You've hit your team's shared budget` / `You've hit your individual usage limit` | [使用限制](https://code.claude.com/docs/zh-TW/errors#youve-hit-your-monthly-spend-limit)                                                                                                  |
| `Could not update your spend limit`                                                                                                                                                                                                                                  | [使用限制](https://code.claude.com/docs/zh-TW/errors#could-not-update-your-spend-limit)                                                                                                   |
| `spend limit reached` / `spend limit unavailable`                                                                                                                                                                                                                    | [使用限制](https://code.claude.com/docs/zh-TW/errors#spend-limit-reached)                                                                                                                 |
| `Not logged in · Please run /login`                                                                                                                                                                                                                                  |                                                                                                                                                                                           |
| `Could not resolve authentication method`                                                                                                                                                                                                                            |                                                                                                                                                                                           |
| `Invalid API key`                                                                                                                                                                                                                                                    |                                                                                                                                                                                           |
| `Your apiKeyHelper script is failing`                                                                                                                                                                                                                                |                                                                                                                                                                                           |
| `Invalid auth token · Fix external auth token`                                                                                                                                                                                                                       |                                                                                                                                                                                           |
| `Invalid ANTHROPIC_CUSTOM_HEADERS · Fix the environment variable`                                                                                                                                                                                                    |                                                                                                                                                                                           |
| `Invalid request header from the environment · Fix the environment variable`                                                                                                                                                                                         |                                                                                                                                                                                           |
| `This organization has been disabled`                                                                                                                                                                                                                                |                                                                                                                                                                                           |
| `Your organization has disabled API key authentication`                                                                                                                                                                                                              |                                                                                                                                                                                           |
| `Your organization has disabled Claude subscription access`                                                                                                                                                                                                          |                                                                                                                                                                                           |
| `Routines are disabled by your organization's policy`                                                                                                                                                                                                                |                                                                                                                                                                                           |
| `Remote Control is only available when using Claude via api.anthropic.com`                                                                                                                                                                                           |                                                                                                                                                                                           |
| `OAuth token refresh failed — run /login to re-authenticate`                                                                                                                                                                                                         |                                                                                                                                                                                           |
| `JWT refresh failed: no OAuth token — run /login`                                                                                                                                                                                                                    |                                                                                                                                                                                           |
| `Claude.ai login expired`                                                                                                                                                                                                                                            |                                                                                                                                                                                           |
| `Claude.ai login was rejected — run /login, then /remote-control`                                                                                                                                                                                                    |                                                                                                                                                                                           |
| `OAuth token unavailable — run /login to restore Remote Control`                                                                                                                                                                                                     |                                                                                                                                                                                           |
| `Signed out of Claude — run /login, then /remote-control`                                                                                                                                                                                                            |                                                                                                                                                                                           |
| `signed-in claude.ai account or organization changed on this machine`                                                                                                                                                                                                |                                                                                                                                                                                           |
| `Remote Control stopped — the app running this session is now signed in to a different Claude account`                                                                                                                                                               |                                                                                                                                                                                           |
| `Remote Control stopped — the app running this session is signed out of Claude`                                                                                                                                                                                      |                                                                                                                                                                                           |
| `OAuth token revoked` / `OAuth token has expired`                                                                                                                                                                                                                    |                                                                                                                                                                                           |
| `API Error: 401 Invalid authentication credentials`                                                                                                                                                                                                                  |                                                                                                                                                                                           |
| `Login expired · Please run /login`                                                                                                                                                                                                                                  |                                                                                                                                                                                           |
| `Claude login not accepted · Run /login, then try again`                                                                                                                                                                                                             |                                                                                                                                                                                           |
| `Not signed in to the Cloud gateway — run /login.`                                                                                                                                                                                                                   |                                                                                                                                                                                           |
| `Administrator policy requires a Cloud gateway sign-in on this machine`                                                                                                                                                                                              |                                                                                                                                                                                           |
| `Failed to authenticate: OAuth session expired and could not be refreshed`                                                                                                                                                                                           |                                                                                                                                                                                           |
| `Your account is on hold and can't use Claude Code. View details or appeal: https://claude.ai/restricted`                                                                                                                                                            |                                                                                                                                                                                           |
| `Your account is on hold and can't sign in to Claude Code. View details or appeal: https://claude.ai/restricted`                                                                                                                                                     |                                                                                                                                                                                           |
| `Anthropic profile login expired · Re-authenticate your Anthropic profile`                                                                                                                                                                                           |                                                                                                                                                                                           |
| `Anthropic profile login expired · Run /login to use your claude.ai account instead, or re-authenticate the profile`                                                                                                                                                 |                                                                                                                                                                                           |
| `does not meet scope requirement user:profile`                                                                                                                                                                                                                       |                                                                                                                                                                                           |
| `claude.ai rejected the session token` / `session token rejected`                                                                                                                                                                                                    |                                                                                                                                                                                           |
| `MCP server "<name>" needs you to sign in again (run /mcp to re-authenticate)`                                                                                                                                                                                       |                                                                                                                                                                                           |
| `rejected the credential from its headersHelper` / `rejected the Authorization header in its config`                                                                                                                                                                 |                                                                                                                                                                                           |
| `MCP server "<name>" needs additional permissions (scope: "<scope>") — run /mcp to re-authenticate`                                                                                                                                                                  |                                                                                                                                                                                           |
| `MCP server "<name>" requires re-authorization (token expired)`                                                                                                                                                                                                      |                                                                                                                                                                                           |
| `Issuer mismatch in authorization response (RFC 9207)`                                                                                                                                                                                                               |                                                                                                                                                                                           |
| `Cloud gateway session expired — run /login to reconnect.`                                                                                                                                                                                                           |                                                                                                                                                                                           |
| `Cloud gateway <url> no longer accepts this session`                                                                                                                                                                                                                 |                                                                                                                                                                                           |
| `AWS credentials expired or invalid`                                                                                                                                                                                                                                 |                                                                                                                                                                                           |
| `AWS authentication failed`                                                                                                                                                                                                                                          |                                                                                                                                                                                           |
| `Google Cloud credentials expired or invalid`                                                                                                                                                                                                                        |                                                                                                                                                                                           |
| `Google Cloud authentication failed`                                                                                                                                                                                                                                 |                                                                                                                                                                                           |
| `Microsoft Foundry authentication failed`                                                                                                                                                                                                                            |                                                                                                                                                                                           |
| `Gateway refused the request`                                                                                                                                                                                                                                        |                                                                                                                                                                                           |
| `Could not load AWS credentials` / `Could not load Google Cloud credentials`                                                                                                                                                                                         |                                                                                                                                                                                           |
| `AWS default-chain credential resolve timed out`                                                                                                                                                                                                                     |                                                                                                                                                                                           |
| `Timed out after 60s waiting for AWS`                                                                                                                                                                                                                                |                                                                                                                                                                                           |
| `A request to AWS timed out. Check your network and proxy settings, then try again.`                                                                                                                                                                                 |                                                                                                                                                                                           |
| `Could not load the default credentials` on Google Cloud’s Agent Platform                                                                                                                                                                                            |                                                                                                                                                                                           |
| `Unable to connect to API`                                                                                                                                                                                                                                           |                                                                                                                                                                                           |
| `Connection refused —` / `Can't reach the API server —` / `No internet route —` / `Couldn't connect through your proxy` / `Connection dropped`，各以括號中的錯誤代碼結尾                                                                                             |                                                                                                                                                                                           |
| `Unable to connect to Anthropic services` during setup                                                                                                                                                                                                               |                                                                                                                                                                                           |
| `Socket is closed`                                                                                                                                                                                                                                                   |                                                                                                                                                                                           |
| `Waiting for API response · will retry in`                                                                                                                                                                                                                           | [自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)，或如果持續發生，則為[網路](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api)                   |
| `API returned an empty or malformed response`                                                                                                                                                                                                                        |                                                                                                                                                                                           |
| `Streaming response ended before any complete data was received`                                                                                                                                                                                                     |                                                                                                                                                                                           |
| `Bedrock streaming response has content-type "..."; expected "application/vnd.amazon.eventstream"`                                                                                                                                                                   |                                                                                                                                                                                           |
| `SSL certificate verification failed`                                                                                                                                                                                                                                |                                                                                                                                                                                           |
| `SSL certificate error (...)` during login or startup                                                                                                                                                                                                                |                                                                                                                                                                                           |
| `unable to get local issuer certificate`                                                                                                                                                                                                                             |                                                                                                                                                                                           |
| `403` with `x-deny-reason: host_not_allowed` in a cloud or routine session                                                                                                                                                                                           |                                                                                                                                                                                           |
| `proxy refused the connection`                                                                                                                                                                                                                                       |                                                                                                                                                                                           |
| `403` with `This GraphQL query is not enabled for this session` in a cloud session                                                                                                                                                                                   | [GitHub proxy](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy)                                                                                                        |
| `The cloud environments service returned an empty response` / `The cloud environments service returned a response in an unexpected format`                                                                                                                           |                                                                                                                                                                                           |
| `Couldn't reconnect to your Remote Control session`                                                                                                                                                                                                                  |                                                                                                                                                                                           |
| `N sessions ended while this machine was offline — the environment was cleaned up on the server and can't be resumed.`                                                                                                                                               |                                                                                                                                                                                           |
| `Couldn't share the transcript.`                                                                                                                                                                                                                                     |                                                                                                                                                                                           |
| `Prompt is too long` / `Input is too long for requested model`                                                                                                                                                                                                       | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)                                                                                                                  |
| `Prompt is too long · automatic compaction failed:`                                                                                                                                                                                                                  | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)                                                                                                                  |
| `Prompt is too long · this conversation is a single exchange` / `A single-exchange conversation cannot be compacted`                                                                                                                                                 | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)                                                                                                                  |
| `Context limit reached · /compact or /clear to continue`                                                                                                                                                                                                             | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)                                                                                                                  |
| `Context limit reached · /clear to continue`                                                                                                                                                                                                                         | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)                                                                                                                  |
| `capability_rejected: prompt_too_long` on a Claude apps gateway session                                                                                                                                                                                              | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)                                                                                                                  |
| `upstream rejected the request` / `request too large for this upstream` on a Claude apps gateway session                                                                                                                                                             | [上游錯誤訊息](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstream-error-messages)                                                                                     |
| `upstream rate limit exceeded` on a Claude apps gateway session                                                                                                                                                                                                      | [上游錯誤訊息](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstream-error-messages)                                                                                     |
| `all upstreams failed (N attempted)` on a Claude apps gateway session                                                                                                                                                                                                | [上游錯誤訊息](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstream-error-messages)                                                                                     |
| `Claude Code may not be enabled for your organization` after a Claude apps gateway sign-in                                                                                                                                                                           | [Claude apps gateway 疑難排解](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#troubleshooting)                                                                             |
| `Context exceeds the ...-token limit by ... tokens` in `/context` output                                                                                                                                                                                             | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#context-exceeds-the-token-limit)                                                                                                     |
| `Error during compaction: Conversation too long`                                                                                                                                                                                                                     | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#error-during-compaction-conversation-too-long)                                                                                       |
| `Request too large`                                                                                                                                                                                                                                                  | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#request-too-large)                                                                                                                   |
| `Request too large for the API's 32MB request limit`                                                                                                                                                                                                                 | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#request-too-large)                                                                                                                   |
| `Image was too large`                                                                                                                                                                                                                                                | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#image-was-too-large)                                                                                                                 |
| `Unable to resize image`                                                                                                                                                                                                                                             | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#unable-to-resize-image)                                                                                                              |
| `PDF too large` / `PDF is password protected`                                                                                                                                                                                                                        | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#pdf-errors)                                                                                                                          |
| `Extra inputs are not permitted`                                                                                                                                                                                                                                     | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#extra-inputs-are-not-permitted)                                                                                                      |
| `API Error: 400 ... tools.N.custom.input_schema: JSON schema is invalid` / `Property keys should match pattern`                                                                                                                                                      | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#tool-input-schema-is-invalid)                                                                                                        |
| `There's an issue with the selected model`                                                                                                                                                                                                                           | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#theres-an-issue-with-the-selected-model)                                                                                             |
| `Model ... is not a recognized model id`                                                                                                                                                                                                                             | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#model-is-not-a-recognized-model-id)                                                                                                  |
| `Model ... not found`                                                                                                                                                                                                                                                | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#model-not-found)                                                                                                                     |
| `Claude Opus is not available with the Claude Pro plan`                                                                                                                                                                                                              | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#claude-opus-is-not-available-with-the-claude-pro-plan)                                                                               |
| `Claude Code ... does not support this model; version ... or newer is required`                                                                                                                                                                                      | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#claude-code-does-not-support-this-model)                                                                                             |
| `Claude Code ... is older than the minimum version required by your organization's policy`                                                                                                                                                                           | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#claude-code-does-not-support-this-model)                                                                                             |
| `Model ... is restricted by your organization's settings`                                                                                                                                                                                                            | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#model-is-restricted-by-your-organizations-settings)                                                                                  |
| `Model switch ... blocked by a PreModelSwitch hook`                                                                                                                                                                                                                  | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#model-switch-was-blocked-by-a-premodelswitch-hook)                                                                                   |
| `couldn't save it as your default` / `couldn't confirm it was saved as your default`                                                                                                                                                                                 | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#couldnt-save-it-as-your-default)                                                                                                     |
| `thinking.type.enabled is not supported for this model`                                                                                                                                                                                                              | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#thinking-type-enabled-is-not-supported-for-this-model)                                                                               |
| `Effort '<level>' isn't available with thinking turned off on this model`                                                                                                                                                                                            | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#effort-isnt-available-with-thinking-turned-off)                                                                                      |
| `effort '<level>' is not supported when thinking is disabled`                                                                                                                                                                                                        | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#effort-isnt-available-with-thinking-turned-off)                                                                                      |
| `max_tokens must be greater than thinking.budget_tokens`                                                                                                                                                                                                             | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#thinking-budget-exceeds-output-limit)                                                                                                |
| `API Error: 400 due to tool use concurrency issues`                                                                                                                                                                                                                  | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#tool-use-or-thinking-block-mismatch)                                                                                                 |
| `[Unsupported tool content removed]`                                                                                                                                                                                                                                 | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#unsupported-tool-content-removed)                                                                                                    |
| `server_tool_use.name: Input should be` on every turn of a resumed session                                                                                                                                                                                           | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#unsupported-tool-content-removed)                                                                                                    |
| `<model> can't help with this. Start a new session to continue`                                                                                                                                                                                                      | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#usage-policy-refusal)                                                                                                                |
| `Claude Code is unable to respond to this request, which appears to violate our Usage Policy`                                                                                                                                                                        | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#usage-policy-refusal)                                                                                                                |
| `<model>'s safeguards flagged this message`                                                                                                                                                                                                                          | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#safety-measures-flagged-a-cybersecurity-topic)                                                                                       |
| `<model> has safety measures that flagged this message for a cybersecurity topic`                                                                                                                                                                                    | [請求錯誤](https://code.claude.com/docs/zh-TW/errors#safety-measures-flagged-a-cybersecurity-topic)                                                                                       |
| `Installation was killed before it could finish (exit code 137)`                                                                                                                                                                                                     | [安裝錯誤](https://code.claude.com/docs/zh-TW/errors#installation-was-killed-before-it-could-finish)                                                                                      |
| `The connection dropped while downloading the update`                                                                                                                                                                                                                | [安裝錯誤](https://code.claude.com/docs/zh-TW/errors#the-connection-dropped-while-downloading-the-update)                                                                                 |
| `Download timed out: exceeded the total deadline`                                                                                                                                                                                                                    | [安裝錯誤](https://code.claude.com/docs/zh-TW/errors#the-connection-dropped-while-downloading-the-update)                                                                                 |
| `--bg and --print conflict`                                                                                                                                                                                                                                          | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#command-line-errors)                                                                                                               |
| `Cloud sessions cannot be created from a --restricted session`                                                                                                                                                                                                       | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cloud-sessions-cannot-be-created-from-a-restricted-session)                                                                        |
| `Cloud sessions are disabled by your organization's policy`                                                                                                                                                                                                          | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cloud-sessions-are-disabled-by-your-organizations-policy)                                                                          |
| `Couldn't verify your organization's policy for cloud sessions`                                                                                                                                                                                                      | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cloud-sessions-are-disabled-by-your-organizations-policy)                                                                          |
| `Error: --json-schema is not a valid JSON Schema`                                                                                                                                                                                                                    | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#command-line-errors)                                                                                                               |
| `Error: Invalid --agents configuration:`                                                                                                                                                                                                                             | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#invalid-agents-configuration)                                                                                                      |
| `Error: Settings file exceeds the 2MiB limit`                                                                                                                                                                                                                        | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#settings-file-exceeds-the-2mib-limit)                                                                                              |
| `The current directory no longer exists (it was deleted or moved)` / `Can't read the current directory`                                                                                                                                                              | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#the-current-directory-no-longer-exists)                                                                                            |
| `couldn't be resolved to a real location, so its skills, commands, and agents weren't loaded`                                                                                                                                                                        | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#directory-couldnt-be-resolved-to-a-real-location)                                                                                  |
| `Error: Workspace not trusted` when starting Remote Control                                                                                                                                                                                                          | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#workspace-not-trusted-when-starting-remote-control)                                                                                |
| \`\`<flag>`before`remote-control` is not carried over to the sessions Remote Control starts`                                                                                                                                                                         | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#not-carried-over-to-the-sessions-remote-control-starts)                                                                            |
| \`\`claude import` is not yet available in this build`                                                                                                                                                                                                               | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#claude-import-is-not-yet-available-in-this-build)                                                                                  |
| `Could not read Claude Code config`                                                                                                                                                                                                                                  | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#could-not-read-claude-code-config)                                                                                                 |
| `Could not import <server>: <reason>`                                                                                                                                                                                                                                | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#could-not-import-a-server-from-claude-desktop)                                                                                     |
| `Cannot add MCP server to scope: managed`                                                                                                                                                                                                                            | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cannot-add-mcp-server-to-the-managed-scope)                                                                                        |
| `is Anthropic-hosted and doesn't support local OAuth`                                                                                                                                                                                                                | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#anthropic-hosted-and-doesnt-support-local-oauth)                                                                                   |
| `Can't read .mcp.json: it isn't a regular file or is larger than 2097152 bytes`                                                                                                                                                                                      | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cant-read-mcp-json)                                                                                                                |
| `Server rejected the Authorization header minted by the configured headersHelper`                                                                                                                                                                                    | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#server-rejected-the-authorization-header-minted-by-the-configured-headershelper)                                                   |
| `Error: MCP tool <name> (passed via --permission-prompt-tool) not found`                                                                                                                                                                                             | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#mcp-permission-prompt-tool-not-found)                                                                                              |
| `OAuth callback port <port> is already in use — another process may be holding it`                                                                                                                                                                                   | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#oauth-callback-port-is-already-in-use)                                                                                             |
| `No available ports for OAuth redirect`                                                                                                                                                                                                                              | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#no-available-ports-for-oauth-redirect)                                                                                             |
| `Shell command failed for pattern "..."`, from `/security-review` or any skill that injects dynamic context                                                                                                                                                          | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#security-review-fails-without-origin-head)                                                                                         |
| `Shell command permission check failed for pattern "..."`, from a skill that injects dynamic context                                                                                                                                                                 | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#security-review-fails-without-origin-head)                                                                                         |
| `Skill <name> requires bash (`shell: bash` in frontmatter) but Git Bash was not found`                                                                                                                                                                               | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#security-review-fails-without-origin-head)                                                                                         |
| `Input must be provided either through stdin or as a prompt argument when using --print`                                                                                                                                                                             | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#input-must-be-provided-when-using-print)                                                                                           |
| `Error: Input contained only whitespace`                                                                                                                                                                                                                             | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#input-contained-only-whitespace)                                                                                                   |
| `Blank prompt — the message was only whitespace, so nothing was sent to the model.`                                                                                                                                                                                  | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#input-contained-only-whitespace)                                                                                                   |
| `Error: stream-json input carried over 256M characters with no newline`                                                                                                                                                                                              | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#stream-json-input-carried-over-256m-characters-with-no-newline)                                                                    |
| `Unknown command: /<name>`, with or without a `Did you mean` suggestion                                                                                                                                                                                              | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#unknown-command)                                                                                                                   |
| `Diff is too large for ultrareview` / `PR #<N> is too large for ultrareview`                                                                                                                                                                                         | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#diff-is-too-large-for-ultrareview)                                                                                                 |
| `Could not find merge-base with <branch>`                                                                                                                                                                                                                            | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#could-not-find-merge-base-with-the-base-branch)                                                                                    |
| `Your checkout has no branches (detached HEAD only)`                                                                                                                                                                                                                 | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#your-checkout-has-no-branches)                                                                                                     |
| `Ultrareview clones <owner>/<repo> in the cloud with the GitHub account connected to your Claude account, and none is connected`                                                                                                                                     | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#no-github-account-is-connected-to-your-claude-account)                                                                             |
| `Your connected GitHub account can't see <owner>/<repo>`                                                                                                                                                                                                             | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#your-connected-github-account-cant-see-the-repository)                                                                             |
| `The GitHub App preflight failed transiently (network or service hiccup) — retry in a moment to start from GitHub instead`                                                                                                                                           | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#the-github-app-preflight-failed-transiently)                                                                                       |
| `GitHub isn't connected to your Claude account, so this repository can't be cloned in the cloud`                                                                                                                                                                     | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#github-isnt-connected-to-your-claude-account)                                                                                      |
| `Single sign-on authorization needed`                                                                                                                                                                                                                                | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#single-sign-on-authorization-needed)                                                                                               |
| `Failed to resume the conversation`                                                                                                                                                                                                                                  | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#failed-to-resume-the-conversation)                                                                                                 |
| `No conversation found with session ID: <session-id>`                                                                                                                                                                                                                | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#no-conversation-found-with-the-session-id)                                                                                         |
| `Cannot switch renderers in this session`                                                                                                                                                                                                                            | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cannot-switch-renderers-in-this-session)                                                                                           |
| `Cannot switch renderers while work is running in the background`                                                                                                                                                                                                    | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#cannot-switch-renderers-in-this-session)                                                                                           |
| `Couldn't read your Zed keymap` / `Couldn't back up your Zed keymap` / `Couldn't update your Zed keymap`                                                                                                                                                             | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#terminal-setup-left-your-zed-keymap-unchanged)                                                                                     |
| `Your Zed keymap isn't a readable list of keybindings`                                                                                                                                                                                                               | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#terminal-setup-left-your-zed-keymap-unchanged)                                                                                     |
| `Skill usage reports are not available on this connection.`                                                                                                                                                                                                          | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#skill-usage-reports-are-not-available-on-this-connection)                                                                          |
| `Custom output styles can't be selected over Remote Control or from a relayed message`                                                                                                                                                                               | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#custom-output-styles-cant-be-selected-over-remote-control)                                                                         |
| `Output styles are saved to local settings (.claude/settings.local.json), which this session doesn't load`                                                                                                                                                           | [命令列錯誤](https://code.claude.com/docs/zh-TW/errors#output-styles-are-saved-to-local-settings-which-this-session-doesnt-load)                                                          |
| `` plugin eval` is currently in early access` /  ``plugin eval` is currently unavailable`                                                                                                                                                                            | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-eval-is-currently-in-early-access)                                                                                         |
| `Marketplace "<name>" is registered from an untrusted source`                                                                                                                                                                                                        | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#marketplace-is-registered-from-an-untrusted-source)                                                                               |
| `references ${user_config.*} in a shell-form command`                                                                                                                                                                                                                | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config)                                                                                            |
| `Monitor "<name>" from plugin <plugin> references ${user_config.*} in its command`                                                                                                                                                                                   | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config)                                                                                            |
| `headersHelper for MCP server '<name>' references ${user_config.*}`                                                                                                                                                                                                  | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-command-references-user-config)                                                                                            |
| `Plugin archive integrity check failed`                                                                                                                                                                                                                              | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#plugin-archive-integrity-check-failed)                                                                                            |
| `path escapes plugin directory`                                                                                                                                                                                                                                      | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#path-escapes-plugin-directory)                                                                                                    |
| `path could not be checked`                                                                                                                                                                                                                                          | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#path-could-not-be-checked)                                                                                                        |
| `its marketplace entry path does not stay inside the marketplace directory`                                                                                                                                                                                          | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#marketplace-entry-path-does-not-stay-inside-the-marketplace-directory)                                                            |
| `Plugin source path refused`                                                                                                                                                                                                                                         | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#marketplace-entry-path-does-not-stay-inside-the-marketplace-directory)                                                            |
| `Failed to load marketplace configuration`                                                                                                                                                                                                                           | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#failed-to-load-marketplace-configuration)                                                                                         |
| `Marketplace configuration file is corrupted`                                                                                                                                                                                                                        | [Plugin 錯誤](https://code.claude.com/docs/zh-TW/errors#failed-to-load-marketplace-configuration)                                                                                         |
| `would be spawned with zero tools — refusing`                                                                                                                                                                                                                        | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#agent-would-be-spawned-with-zero-tools)                                                                                              |
| `File is covered by a Read deny rule in your permission settings`                                                                                                                                                                                                    | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#file-is-covered-by-a-read-deny-rule)                                                                                                 |
| `subagent_type is required: the general-purpose agent is not available in this session`                                                                                                                                                                              | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#subagent-type-is-required)                                                                                                           |
| `Error: this write left the memory index at MEMORY.md at ..., over its ... read limit`                                                                                                                                                                               | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#memory-index-is-over-its-read-limit)                                                                                                 |
| `pkill: refusing to run`                                                                                                                                                                                                                                             | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#pkill-pattern-matches-the-claude-code-process)                                                                                       |
| `Failed to write to <name>'s inbox — nothing was sent`                                                                                                                                                                                                               | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#failed-to-write-to-a-teammate-inbox)                                                                                                 |
| `Failed to write the plan approval request to the lead's inbox — plan not submitted`                                                                                                                                                                                 | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#failed-to-write-to-a-teammate-inbox)                                                                                                 |
| `Its agent definition was not restored: the folder its definition file came from is not trusted`                                                                                                                                                                     | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#teammate-agent-definition-not-restored)                                                                                              |
| `Message too large for cross-session delivery`                                                                                                                                                                                                                       | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#message-too-large-for-cross-session-delivery)                                                                                        |
| `Too many messages to this session just now`                                                                                                                                                                                                                         | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#too-many-messages-to-this-session-just-now)                                                                                          |
| `Refusing to send: reply target is a symlink` / `Refusing to send: cannot vet reply target`                                                                                                                                                                          | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-to-send-a-cross-session-message)                                                                                            |
| `Refusing to send: connected endpoint is not the expected process` / `Refusing to send: connected endpoint identity could not be read`                                                                                                                               | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-to-send-a-cross-session-message)                                                                                            |
| `Refusing to send: connected endpoint is not owned by this user` / `Refusing to send: connected endpoint owner could not be read`                                                                                                                                    | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-to-send-a-cross-session-message)                                                                                            |
| `Refusing to send: connected endpoint is a different process with the expected pid`                                                                                                                                                                                  | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-to-send-a-cross-session-message)                                                                                            |
| `Refusing to read <path>: its symlink resolution changed after permission was checked (<reason>)` / `Refusing to search <path>: its symlink resolution changed after permission was checked`                                                                         | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-after-a-symlink-changed)                                                                                                    |
| `Refusing to write <path>: its parent-directory symlink resolution changed after permission was checked` / `Refusing to write <path>: it is a symbolic link. Write to the link's target path instead`                                                                | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-after-a-symlink-changed)                                                                                                    |
| `Refusing to write through symlink: <path>` / `Refusing to write into symlinked directory: <path>`                                                                                                                                                                   | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-after-a-symlink-changed)                                                                                                    |
| `Refusing to search <path>: a path one of its Read deny rules is written through changed while the search was being prepared` / `Refusing to search <path>: it could not be opened`                                                                                  | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-after-a-symlink-changed)                                                                                                    |
| `its permission check expired before it ran (too many concurrent file operations)` / `ripgrep was found only by name on PATH`                                                                                                                                        | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#refusing-after-a-symlink-changed)                                                                                                    |
| `task output swap refused (tasks dir moved or linked)`                                                                                                                                                                                                               | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#task-output-swap-refused)                                                                                                            |
| `Command killed: its output file was replaced or could no longer be verified`                                                                                                                                                                                        | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#task-output-swap-refused)                                                                                                            |
| `the source file is not valid UTF-8 text` / `the source file is not valid UTF-16 text`                                                                                                                                                                               | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#the-source-file-is-not-valid-utf-8-text)                                                                                             |
| `the source file has the replacement character U+FFFD`                                                                                                                                                                                                               | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#the-source-file-is-not-valid-utf-8-text)                                                                                             |
| `Reading a local file from outside this session's connected folders, or through a link, needs the approval card`                                                                                                                                                     | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#reading-a-local-file-from-outside-the-connected-folders)                                                                             |
| `cannot read file_path (...) — the file could not be examined, and no one can answer the approval card`                                                                                                                                                              | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#reading-a-local-file-from-outside-the-connected-folders)                                                                             |
| `WebFetch cannot fetch localhost or other hostnames without a dot`                                                                                                                                                                                                   | [工具錯誤](https://code.claude.com/docs/zh-TW/errors#webfetch-cannot-fetch-localhost)                                                                                                     |
| `Can't open MCP settings while no terminal is attached to this background session`                                                                                                                                                                                   | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#commands-refused-in-a-background-session)                                                                                    |
| `Can't open MCP settings in a background session`                                                                                                                                                                                                                    | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#commands-refused-in-a-background-session)                                                                                    |
| `blocked because the path is spelled in a form that cannot be safely resolved`                                                                                                                                                                                       | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#write-or-command-blocked-because-the-path-cannot-be-safely-resolved)                                                         |
| `blocked because the path is network-shaped`                                                                                                                                                                                                                         | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#write-or-command-blocked-because-the-path-names-a-network-location)                                                          |
| `This session has no saved transcript`                                                                                                                                                                                                                               | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#this-session-has-no-saved-transcript)                                                                                        |
| `Can't open — this session is running in another terminal`                                                                                                                                                                                                           | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#this-session-is-running-in-another-terminal)                                                                                 |
| `This conversation is already open in another running Claude session`                                                                                                                                                                                                | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#this-session-is-running-in-another-terminal)                                                                                 |
| `This session's saved conversation is no longer on disk`                                                                                                                                                                                                             | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#this-sessions-saved-conversation-is-no-longer-on-disk)                                                                       |
| `kept <id> — its worktree is still at <path>`                                                                                                                                                                                                                        | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#worktree-has-commits-that-are-not-pushed-anywhere)                                                                           |
| `kept <id> — <n> unpushed commits on <branch>`                                                                                                                                                                                                                       | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#worktree-has-commits-that-are-not-pushed-anywhere)                                                                           |
| `kept <id> — worktree has commits that are not pushed anywhere`                                                                                                                                                                                                      | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#worktree-has-commits-that-are-not-pushed-anywhere)                                                                           |
| `terminal host process died — press Enter to restart` / `This session's terminal host process died`                                                                                                                                                                  | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#terminal-host-process-died)                                                                                                  |
| `Session isn't responding` / `Press enter again to restart this session — it isn't responding`                                                                                                                                                                       | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#session-isnt-responding)                                                                                                     |
| `Session <id> was stopped while the respawn was in flight`                                                                                                                                                                                                           | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#session-was-stopped-while-the-respawn-was-in-flight)                                                                         |
| `This session was running agent '<name>', which is no longer available`                                                                                                                                                                                              | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#session-agent-no-longer-available)                                                                                           |
| `CLAUDE_CODE_PROCESS_WRAPPER: launcher ...`                                                                                                                                                                                                                          | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#claude_code_process_wrapper-launcher-errors)                                                                                 |
| `EUNKNOWN: unknown error, uv_spawn`                                                                                                                                                                                                                                  | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#eunknown-when-starting-a-background-session)                                                                                 |
| `EACCES: permission denied, posix_spawn`                                                                                                                                                                                                                             | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#eacces-when-starting-a-background-session)                                                                                   |
| `exited before it became reachable`                                                                                                                                                                                                                                  | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#background-service-exited-before-it-became-reachable)                                                                        |
| `Couldn't start a background session (working directory no longer exists or is not accessible: ...)`                                                                                                                                                                 | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#working-directory-no-longer-exists-when-starting-a-background-session)                                                       |
| `Claude Code is being updated by npm on this machine (still not runnable after 2 min, ...)`                                                                                                                                                                          | [背景工作階段錯誤](https://code.claude.com/docs/zh-TW/errors#eacces-when-starting-a-background-session)                                                                                   |
| `Claude Code process exited with code N`                                                                                                                                                                                                                             | [包裝程式和 IDE 錯誤](https://code.claude.com/docs/zh-TW/errors#claude-code-process-exited-with-code-n)                                                                                   |
| `The connection to Claude Code ended before this message completed`                                                                                                                                                                                                  | [包裝程式和 IDE 錯誤](https://code.claude.com/docs/zh-TW/errors#the-connection-to-claude-code-ended-before-this-message-completed)                                                        |
| `Could not locate the Claude CLI on PATH`                                                                                                                                                                                                                            | [包裝程式和 IDE 錯誤](https://code.claude.com/docs/zh-TW/errors#could-not-locate-the-claude-cli-on-path)                                                                                  |
| `Restored the code, but skipped N files`                                                                                                                                                                                                                             | [Rewind 警告和錯誤](https://code.claude.com/docs/zh-TW/errors#restored-the-code-but-skipped-files)                                                                                        |
| `No files were restored: N files failed (backup missing, or the file could not be updated)`                                                                                                                                                                          | [Rewind 警告和錯誤](https://code.claude.com/docs/zh-TW/errors#no-files-were-restored)                                                                                                     |
| `Transcript writes are failing (...)`                                                                                                                                                                                                                                | [工作階段儲存警告](https://code.claude.com/docs/zh-TW/errors#transcript-writes-are-failing)                                                                                               |
| `Transcript saving is off — CLAUDE_CODE_SKIP_PROMPT_HISTORY is set`                                                                                                                                                                                                  | [工作階段儲存警告](https://code.claude.com/docs/zh-TW/errors#transcript-saving-is-off-skip-prompt-history)                                                                                |
| `Transcript saving is off — inherited CLAUDE_CODE_CHILD_SESSION marker`                                                                                                                                                                                              | [工作階段儲存警告](https://code.claude.com/docs/zh-TW/errors#transcript-saving-is-off-child-session-marker)                                                                               |
| `Claude Code's fullscreen renderer didn't finish starting last time on this machine` / `Claude Code's fullscreen renderer has repeatedly failed to start on this machine`                                                                                            | [設定警告](https://code.claude.com/docs/zh-TW/errors#fullscreen-failed-start-notice)                                                                                                      |
| `Claude Code exited after an unrecoverable interface error (...)`                                                                                                                                                                                                    | [設定警告](https://code.claude.com/docs/zh-TW/errors#exited-after-an-unrecoverable-interface-error)                                                                                       |
| `Agent descriptions are over the 15.0k-token limit`                                                                                                                                                                                                                  | [設定警告](https://code.claude.com/docs/zh-TW/errors#agent-descriptions-are-over-the-15000-token-limit)                                                                                   |
| `Ignoring N permissions.allow entries from ... this workspace has not been trusted`                                                                                                                                                                                  | [設定警告](https://code.claude.com/docs/zh-TW/errors#workspace-has-not-been-trusted)                                                                                                      |
| `is a network path, which cannot be added as a working directory`                                                                                                                                                                                                    | [設定警告](https://code.claude.com/docs/zh-TW/errors#working-directory-is-a-network-path)                                                                                                 |
| `Remote managed settings failed to load (<cause>)`                                                                                                                                                                                                                   | [設定警告](https://code.claude.com/docs/zh-TW/errors#remote-managed-settings-failed-to-load)                                                                                              |
| `Managed settings were not approved; exiting without applying them.`                                                                                                                                                                                                 | [設定警告](https://code.claude.com/docs/zh-TW/errors#managed-settings-were-not-approved)                                                                                                  |
| `MCP server <name> is blocked by enterprise managed policy`                                                                                                                                                                                                          | [設定警告](https://code.claude.com/docs/zh-TW/errors#mcp-server-is-blocked-by-enterprise-managed-policy)                                                                                  |
| `Managed settings document could not be parsed as a JSON object; none of its settings are in effect. Fix or remove it.`                                                                                                                                              | [設定警告](https://code.claude.com/docs/zh-TW/errors#managed-settings-document-could-not-be-parsed)                                                                                       |
| `Managed settings drop-in directory could not be read`                                                                                                                                                                                                               | [設定警告](https://code.claude.com/docs/zh-TW/errors#managed-settings-document-could-not-be-parsed)                                                                                       |
| `"crossSessionInbound" must be one of "accept", "hold", "refuse"`                                                                                                                                                                                                    | [設定警告](https://code.claude.com/docs/zh-TW/errors#crosssessioninbound-must-be-one-of-accept-hold-refuse)                                                                               |
| `headersHelper not run — this workspace has no persisted trust`                                                                                                                                                                                                      | [設定警告](https://code.claude.com/docs/zh-TW/errors#headershelper-not-run)                                                                                                               |
| `Invalid permission rule "..." was skipped: Malformed Tool(content) rule`                                                                                                                                                                                            | [設定警告](https://code.claude.com/docs/zh-TW/errors#malformed-tool-content-rule)                                                                                                         |
| `... is not matched by file permission checks`                                                                                                                                                                                                                       | [設定警告](https://code.claude.com/docs/zh-TW/errors#is-not-matched-by-file-permission-checks)                                                                                            |
| `... has a wildcard before the rest of the command`                                                                                                                                                                                                                  | [設定警告](https://code.claude.com/docs/zh-TW/errors#has-a-wildcard-before-the-rest-of-the-command)                                                                                       |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT is set, but the 200K limit isn't enforced`                                                                                                                                                                                           | [設定警告](https://code.claude.com/docs/zh-TW/errors#the-200k-limit-isnt-enforced)                                                                                                        |
| `[claude-code:unrecognized_model]`                                                                                                                                                                                                                                   | [設定警告](https://code.claude.com/docs/zh-TW/errors#unrecognized-model-id-on-a-request)                                                                                                  |
| `Stale sandbox mask files left by a killed session`                                                                                                                                                                                                                  | [設定警告](https://code.claude.com/docs/zh-TW/errors#stale-sandbox-mask-files-left-by-a-killed-session)                                                                                   |
| 回應品質似乎比平常低                                                                                                                                                                                                                                                 | [回應品質](https://code.claude.com/docs/zh-TW/errors#responses-seem-lower-quality-than-usual)                                                                                             |

## 自動重試

Claude Code 會在顯示錯誤之前，以指數退避方式重試暫時性故障最多 10 次。它不會總是重試在 Claude 回應中途出現的故障。當您看到本頁面上的其中一個錯誤時，Claude Code 已經對該故障進行了適用的重試；下面的清單說明哪些故障會獲得完整的重試預算、哪些會獲得較小的預算，以及哪些不會獲得任何預算。 Claude Code 會重試這些故障：

- 伺服器錯誤、過載回應，以及在 Claude 回應開始串流之前到達的請求逾時。
- 連線中斷。當連線在 Claude 完成其回應的任何部分（包括其思考）之前中途中斷時，Claude Code 會以相同的退避方式重新發出請求，並且回合會繼續，即使某些文字已經開始串流。當連線在 Claude 完成思考之後但在開始任何文字或工具呼叫之前中斷時，Claude Code 會改為快速連續重新發出請求最多兩次，如果連線在該點持續中斷，則以 `Connection lost before a response was produced` 結束回合。
- Claude Code 偵測到的連線在您的電腦進入睡眠狀態時在請求中途被中斷。Claude Code 將其計為上述規則下的連線中斷；一旦重試標籤命名了具體原因，它會讀作 `Connection lost while your computer was asleep`，如果回合在 Claude 完成思考但在任何文字或工具呼叫之前結束，訊息會讀作 `Your computer went to sleep before a response was produced`。
- 停滯的回應串流，當回應標頭已到達但 Claude 回應的任何部分都未到達，或當 Claude 完成思考但尚未開始任何文字或工具呼叫時：Claude Code 會中止停滯的連線，並最多重新發出一次請求，不在上述 10 次嘗試預算內。如果在 Claude 完成思考但在任何文字或工具呼叫之前回應停滯第二次，Claude Code 會以 `The response stalled before a response was produced` 結束回合。
- 串流請求 API 從未以回應標頭回答，在 [first-byte deadline 執行](https://code.claude.com/docs/zh-TW/network-config#streaming-idle-watchdogs) 的連線上：Claude Code 在截止時間中止它，並在重試預算內最多每個模型請求重新發送一次，然後如果該嘗試也未獲得回答，則以 [No response from API](https://code.claude.com/docs/zh-TW/errors#no-response-from-api) 結束回合。在其他連線上，請求會等待 `API_TIMEOUT_MS`。當您設定 `CLAUDE_CODE_RETRY_WATCHDOG` 時，一次重試上限不適用。
- 暫時性 429 節流，但不是閘道的支出限制 `429`，這不是節流；請參閱 [Spend limit reached](https://code.claude.com/docs/zh-TW/errors#spend-limit-reached)。
  - 當您使用 claude.ai 訂閱登入時，這包括不帶有您計畫配額標頭的 429 節流。在 v2.1.199 之前，Claude Code 僅針對 API 金鑰和企業登入重試這些節流。
- 因為輸入加上 `max_tokens` 超過內容限制而被拒絕的請求。以相同方式重新發送它會以相同方式失敗，所以 Claude Code 會以縮減的 `max_tokens` 重試，並在兩種情況下停止重試並改為壓縮：
  - 當沒有縮減可以適應時，例如當對話本身幾乎填滿內容視窗時。
  - 當重試無法進一步縮減 `max_tokens` 時。在 v2.1.218 之前，Claude Code 可以重新發送仍然不適應的縮減請求，例如當擴展思考預算超過剩餘內容時，直到重試預算用盡。
- 在 [Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 上過期或遺失的 Google Cloud 認證，或在您的機器上無法載入的 AWS 認證。Claude Code 會捨棄其快取的認證並重試最多兩次，然後報告錯誤，以便您可以立即重新驗證，如 [Could not load AWS or Google Cloud credentials](https://code.claude.com/docs/zh-TW/errors#could-not-load-aws-or-google-cloud-credentials) 下所述。在 v2.1.228 之前，Claude Code 會透過完整重試預算重試失敗的 Google Cloud 認證，然後才顯示錯誤。
- 來自 Anthropic API 的 `401` 或 `403`，直接或透過 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway)，而 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 指令碼提供認證。Claude Code 會重新執行指令碼並使用其新輸出重試，在完整重試預算內。當指令碼本身在重新執行時失敗時，Claude Code 會改為顯示 [Your apiKeyHelper script is failing](https://code.claude.com/docs/zh-TW/errors#your-apikeyhelper-script-is-failing)。

在 v2.1.227 之前，`Connection lost before a response was produced` 讀作 `Connection closed while thinking, before producing a response`，`The response stalled before a response was produced` 讀作 `Response stalled while thinking, before producing a response`。 Claude Code 不會重試這些故障：

- TLS 憑證驗證失敗，例如 TLS 檢查代理、遺失的 `NODE_EXTRA_CA_CERTS` 套件，或過期的憑證。Claude Code 在第一次嘗試時報告錯誤，以便您可以立即修正憑證設定；請參閱 [SSL certificate errors](https://code.claude.com/docs/zh-TW/errors#ssl-certificate-errors)。Claude Code 仍會重試暫時性 TLS 條件，例如握手逾時。在 v2.1.199 之前，Claude Code 會透過完整重試預算重試憑證失敗，然後才顯示錯誤。
- 伺服器錯誤、連線中斷，或停滯的串流在 Claude 完成文字區塊或工具呼叫之後到達，或在完成思考後開始一個但在完成回應之前。Claude Code 不會重新執行請求，因為這可能會執行相同的工具呼叫兩次。它會保留 Claude 完成的內容，執行 Claude 完成的任何工具呼叫，並從其結果繼續回合。關於您在互動式工作階段和非互動式工作階段中看到的內容，請閱讀 [The response above may be incomplete](https://code.claude.com/docs/zh-TW/errors#the-response-above-may-be-incomplete)。在 v2.1.199 之前，當伺服器錯誤在串流中途到達時，Claude Code 會捨棄部分輸出並將整個回合報告為錯誤。
- 在 Claude 完成回應之後到達的故障：不需要重試任何內容，所以 Claude Code 會保留完整回應並正常結束回合。
- [Amazon Bedrock 串流回應具有意外的 content-type](https://code.claude.com/docs/zh-TW/errors#bedrock-streaming-response-has-an-unexpected-content-type)，因為重寫回應的閘道或代理會以相同方式重寫重試。需要 Claude Code v2.1.208 或更新版本。
- 失敗的串流請求的非串流重試獲得成功狀態但 [body 中沒有 Claude API 訊息](https://code.claude.com/docs/zh-TW/errors#api-returned-an-empty-or-malformed-response)。Claude Code 以該錯誤結束回合。
- 您的組織的原則檢查拒絕的請求，其表現為帶有拒絕訊息的 `API Error:` 行。您的組織管理員使用 [Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks)（Claude 企業功能）設定檢查，訊息以他們設定的指示結尾，或預設告訴您聯絡他們。Claude Code 不會將被拒絕的請求重新發送到相同的模型或 [fallback model](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains)，因為拒絕是關於請求的內容而不是模型。在 v2.1.239 之前，Claude Code 可以重新發送被拒絕的請求，不進行串流或在設定的後備模型上，然後才向您顯示拒絕。

### 當 Claude Code 重試或等待時您看到的內容

重試時，微調器在錯誤標籤後顯示 `Retrying in Ns · attempt x/y` 倒數計時。標籤命名第一次嘗試的具體原因，用於您可以立即採取行動的故障：網路已關閉、TLS 握手失敗，或您達到速率限制。對於其他錯誤，它最初讀作 `API error`。從 v2.1.198 開始，它會切換到第三次嘗試的具體原因，或當 `CLAUDE_CODE_MAX_RETRIES` 允許少於三次時在最後一次嘗試；較早的版本僅在最後一次嘗試時切換。 從 v2.1.198 開始，在重試期間會隱藏通常的微調器提示。一旦錯誤原因被揭示，如果故障是 529 過載，倒數計時下方的行也會命名檢查服務狀態的位置：Anthropic API 上的 `status.claude.com`，或其他設定上的訊息中命名的提供者或閘道主機。 如果在請求仍待處理時，回應串流上 20 秒內沒有資料到達，微調器會在任何重試開始之前顯示 `Waiting for API response · will retry in … · check your network`。請求尚未失敗：倒數計時執行到 Claude Code 中止停滯連線的點。中止後，您看到的內容取決於回應已進行的距離：

- 在 Claude 完成文字區塊或工具呼叫之前，或在完成思考後開始一個，Claude Code 會重試請求或以錯誤結束回合。[Automatic retries](https://code.claude.com/docs/zh-TW/errors#automatic-retries) 說明它重試哪些停滯以及重試多少次。
- 在 Claude 完成文字區塊或工具呼叫之後，或在完成思考後開始一個，但在 Claude 完成回應之前，Claude Code 會保留 Claude 完成的內容，從 Claude 完成的任何工具呼叫繼續回合，並顯示 [The response above may be incomplete](https://code.claude.com/docs/zh-TW/errors#the-response-above-may-be-incomplete)。在非互動式工作階段中，以及在任何工作階段中的子代理回應，Claude Code 可能會先提示 Claude 繼續回應；該項目說明何時執行以及何時您仍在那裡看到通知。
- 在 Claude 完成回應之後，Claude Code 正常結束回合。

一旦資料恢復或重試成功，橫幅會自動清除。如果它在每次嘗試時重新出現，請將其視為 [network issue](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api)。在 v2.1.185 之前，橫幅在 10 秒後出現，措辭不同。 當 Claude 正在諮詢 [advisor](https://code.claude.com/docs/zh-TW/advisor) 時，橫幅在 90 秒無資料後出現，而不是 20 秒，因為長時間的顧問審查可以發送超過 20 秒的任何內容。在 v2.1.214 之前，20 秒的閾值也適用於顧問呼叫，所以橫幅在顧問審查期間出現，即使沒有任何問題。

### 調整重試行為

您可以使用這些環境變數調整重試行為：

| 變數                                                                                 | 預設   | 效果                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`CLAUDE_CODE_MAX_RETRIES`](https://code.claude.com/docs/zh-TW/env-vars)             | 10     | 重試嘗試次數。從 v2.1.186 開始上限為 15；從 v2.1.199 開始 `CLAUDE_CODE_RETRY_WATCHDOG` 會提高預設值並移除上限。降低它以在指令碼中更快地顯示故障。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| [`CLAUDE_CODE_RETRY_WATCHDOG`](https://code.claude.com/docs/zh-TW/env-vars)          | 未設定 | 在無人值守的工作階段（例如 CI 工作）中設定為 `1`，以無限期重試 `429` 和 `529` 容量錯誤，而不是在 `CLAUDE_CODE_MAX_RETRIES` 嘗試後失敗。Claude Code 在報告支出限制或耗盡使用額度的 `429` 上立即失敗，即使是來自 [gateway spend cap](https://code.claude.com/docs/zh-TW/errors#spend-limit-reached) 的重新設定排程。在 v2.1.239 之前，看門狗無限期重試這些。在 v2.1.199 或更新版本上，它也會提高其他暫時性錯誤（例如伺服器錯誤、逾時和連線中斷）的預設重試計數至 300，大約三小時的退避，如果您明確設定該變數，則移除 `CLAUDE_CODE_MAX_RETRIES` 的上限 15。如需快速模式請求，請參閱 [Handle rate limits](https://code.claude.com/docs/zh-TW/fast-mode#handle-rate-limits)。 |
| [`API_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars)                      | 600000 | 每個請求的逾時（毫秒）。為慢速網路或代理提高它。它也會上限 Claude Code 等待回應標頭的時間，如 [No response from API](https://code.claude.com/docs/zh-TW/errors#no-response-from-api) 中所述。                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| [`CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) | 未設定 | 串流請求的第一個回應位元組的截止時間（毫秒）。需要 Claude Code v2.1.242 或更新版本。關於當此未設定時 Claude Code 如何選擇截止時間，請參閱 [No response from API](https://code.claude.com/docs/zh-TW/errors#no-response-from-api)。                                                                                                                                                                                                                                                                                                                                                                                                                                       |

## 伺服器錯誤

大多數這些錯誤來自推論提供者：Anthropic 在 Anthropic API 上的服務，以及該提供者在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或自訂閘道上的端點後面的服務。[Auto mode 無法判斷動作的安全性](https://code.claude.com/docs/zh-TW/errors#auto-mode-cannot-determine-the-safety-of-an-action)和[Agent 因 API 錯誤而提前終止](https://code.claude.com/docs/zh-TW/errors#agent-terminated-early-due-to-an-api-error)也涵蓋您這一方的原因，例如無法叫用分類器模型的 Amazon Bedrock 帳戶或達到使用限制的子代理。

### API Error: 500 Internal server error

Claude Code 會顯示任何 5xx 回應的狀態碼和 API 的錯誤訊息。下面的範例顯示 Anthropic API 上的 500 回應：

```
API Error: 500 Internal server error. This is a server-side issue, usually temporary — try again in a moment. If it persists, check https://status.claude.com.

```

尾部句子名稱檢查服務健康狀況的位置，並因提供者而異。Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 設定會名稱該提供者的服務狀態。自訂 `ANTHROPIC_BASE_URL` 會名稱閘道主機。 這表示 API 內部發生意外故障。它不是由您的提示、設定或帳戶引起的。 **該怎麼做：**

- 檢查 [status.claude.com](https://status.claude.com) 或訊息中名稱的提供者狀態頁面，查看是否有活躍的事件
- 等待一分鐘，然後再次傳送您的訊息。您的原始訊息仍在對話中，因此對於較長的提示，您可以輸入 `try again` 而不是貼上整個內容。
- 如果錯誤持續存在且沒有發佈的事件，請執行 `/feedback`，以便 Anthropic 可以使用您的請求詳細資訊進行調查。如果您的環境中無法使用 `/feedback`，請參閱[報告錯誤](https://code.claude.com/docs/zh-TW/errors#report-an-error)。

### API Error: Repeated 529 Overloaded errors

API 在所有使用者中暫時達到容量。Claude Code 在顯示此訊息之前已經重試了多次：

```
API Error: Repeated 529 Overloaded errors. The API is at capacity — this is usually temporary. Try again in a moment. If it persists, check https://status.claude.com.

```

尾部句子因提供者而異，方式與上面的 500 錯誤相同。 529 不是您的使用限制，也不會計入您的配額。 **該怎麼做：**

- 檢查 [status.claude.com](https://status.claude.com) 或訊息中名稱的提供者狀態頁面，查看容量通知
- 在幾分鐘後重試
- 執行 `/model` 並切換到不同的模型以繼續工作，因為容量是按模型追蹤的。Claude Code 會在一個模型負載特別高時提示您執行此操作，例如 `Opus is experiencing high load, please use /model to switch to Sonnet`。

### Request timed out

API 在連線截止時間之前沒有回應。

```
Request timed out

```

這可能在高負載期間或模型生成非常大的回應時發生。預設請求逾時為 10 分鐘。 **該怎麼做：**

- 重試請求
- 對於長時間執行的任務，將工作分解為較小的提示
- 如果緩慢的網路或代理是原因，請按照[自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)中的說明提高 `API_TIMEOUT_MS`
- 如果逾時頻繁且您的網路在其他方面狀況良好，請參閱下面的[網路和連線錯誤](https://code.claude.com/docs/zh-TW/errors#network-and-connection-errors)

### No response from API

Claude Code 傳送了串流請求，API 在第一個位元組的截止時間內沒有返回回應標頭，因此 Claude Code 中止了請求，而不是等待完整的 `API_TIMEOUT_MS` 請求逾時（預設為 10 分鐘）。Claude Code 最多再傳送一次請求，如果[重試預算](https://code.claude.com/docs/zh-TW/errors#tune-retry-behavior)允許的話。當重試也沒有得到回應時，該輪次以此訊息結束，該訊息顯示每次嘗試等待了多長時間。當您設定 [`CLAUDE_CODE_RETRY_WATCHDOG`](https://code.claude.com/docs/zh-TW/env-vars) 時，一次重試的上限不適用，Claude Code 會在[調整重試行為](https://code.claude.com/docs/zh-TW/errors#tune-retry-behavior)中描述的預算下重試。

```
API Error: No response from API (waited 3m, then 10m on the retry). If a proxy or gateway on your network holds responses until they complete, raise API_TIMEOUT_MS or CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS to wait longer.

```

Claude Code 分別為第一次嘗試的等待回應標頭和重試的等待設定：

- **第一次嘗試** ：當您將其設定為 1 或更多時，[`CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars)，限制在 10 秒到 30 分鐘之間。否則 Claude Code 會使用[串流空閒監視程式](https://code.claude.com/docs/zh-TW/network-config#streaming-idle-watchdogs)中列出的位元組級監視程式逾時，因此改變該逾時的變數也會改變此等待。無論哪種方式，Claude Code 都會為請求正文的每 32KB 添加一秒。
- **重試** ：比 `API_TIMEOUT_MS` 少一秒，預設略低於 10 分鐘，以便重試可以超過保持回應直到生成完成的代理或閘道。在 Amazon Bedrock 上，重試使用與第一次嘗試相同的截止時間，訊息顯示一個持續時間而不是兩個。

兩個等待都不超過正 `API_TIMEOUT_MS` 少一秒，正 `API_TIMEOUT_MS` 在 11 秒以下會關閉截止時間。位元組級監視程式僅在回應標頭到達後才開始，因此在此之後停止傳送位元組的回應遵循[停滯串流規則](https://code.claude.com/docs/zh-TW/errors#automatic-retries)而不是此截止時間。 **該怎麼做：**

- 再次傳送您的訊息。您的原始訊息仍在對話中，因此對於較長的提示，您可以輸入 `try again` 而不是貼上整個內容。
- 如果重複出現，將其視為[網路或代理問題](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api)。接受連線但從不轉發請求的代理會在每次嘗試時產生此錯誤。
- 如果您網路上的代理或閘道保持回應直到完成，請提高 `API_TIMEOUT_MS` 以便重試等待更長時間。在 Amazon Bedrock 上，也請提高 `CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS`。
- 如果第一次嘗試持續逾時，然後重試成功，請提高 `CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS` 以便第一次嘗試也等待足夠長的時間。

在 v2.1.242 之前，Claude Code 在未回應的串流請求失敗之前等待完整的 `API_TIMEOUT_MS` 請求逾時（預設為 10 分鐘）。在 v2.1.261 之前，重試等待與第一次嘗試相同的截止時間，訊息沒有顯示持續時間。

### The response above may be incomplete

串流請求在回應仍在進行中時失敗，在 Claude 完成一個文字區塊或工具呼叫之後，或在完成思考後開始一個。重新傳送請求可能會執行相同的工具呼叫兩次，因此 Claude Code 會保留 Claude 完成的輸出並附加此通知，而不是丟棄該輪次。您看到的變體名稱原因：

```
API Error: Server error mid-response. The response above may be incomplete.
API Error: Connection lost mid-response. The response above may be incomplete.
API Error: Your computer went to sleep mid-response. The response above may be incomplete.
API Error: The response stopped arriving. The response above may be incomplete.

```

- `Server error mid-response`：中流過載或 5xx 伺服器錯誤。此變體需要 Claude Code v2.1.199 或更高版本；在此之前，該情況會丟棄部分輸出並將整個輪次報告為錯誤。
- `Connection lost mid-response`：連線中斷。
- `Your computer went to sleep mid-response`：Claude Code 偵測到您的電腦在回應串流時進入睡眠狀態。一旦您的電腦喚醒，Claude Code 會將連線視為中斷並停止從中讀取。
- `The response stopped arriving`：連線保持開啟但停止傳遞資料，因此串流空閒監視程式中止了它。在 v2.1.222 之前，Claude Code 也可能在通過 `ANTHROPIC_BASE_URL` 或 `ANTHROPIC_AWS_BASE_URL` 到達的[閘道](https://code.claude.com/docs/zh-TW/gateways)連線上報告此故障，同時伺服器的保活 ping 仍在到達，因為它只計算那裡解析的回應事件；升級會停止這些虛假逾時在這些路由上。通過提供者基礎 URL（例如 `ANTHROPIC_BEDROCK_BASE_URL`）到達的閘道不被位元組監視程式包裝；請參閱[串流空閒監視程式](https://code.claude.com/docs/zh-TW/network-config#streaming-idle-watchdogs)。

在 v2.1.227 之前，`Connection lost mid-response` 讀作 `Connection closed mid-response`，`The response stopped arriving` 讀作 `Response stalled mid-stream`。 在四種情況下，Claude Code 會在不立即顯示此通知的情況下處理故障：

- 在回應的早期，Claude Code 要麼重試故障，要麼以不同的錯誤結束輪次。請參閱[自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)。
- 當這些故障之一在 Claude 完成回應後到達時，Claude Code 會保留完整回應並正常結束輪次，沒有此通知。在 v2.1.222 之前，Claude Code 在連線中斷或在回應完成後停滯時顯示此通知，並將輪次報告為錯誤，儘管回應是完整的。
- 在[非互動式工作階段](https://code.claude.com/docs/zh-TW/headless)中，例如 `-p` 執行、[Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 執行或[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，當截斷回應在主對話中且包含文字但沒有工具呼叫時，您不必自己傳送 `continue`：Claude Code 會保留部分輸出並提示 Claude 從停止的地方繼續，最多連續三次。您只有在 Claude Code 用完這些繼續後才會看到此通知。在 v2.1.246 之前，Claude Code 在第一次截斷時以此通知結束非互動式輪次。
- 在[子代理](https://code.claude.com/docs/zh-TW/sub-agents#api-errors-in-subagents)中，無論工作階段是否互動：當其截斷回應包含文字但沒有工具呼叫時，Claude Code 會提示子代理繼續。通知僅在這些繼續用完後才成為子代理的最後一條訊息。在 v2.1.257 之前，子代理在第一次截斷時顯示此通知。

**該怎麼做：**

- 在互動式工作階段中，閱讀螢幕上保留的回應：Claude Code 保留 Claude 在錯誤之前完成的每個區塊，但在輪次結束時丟棄中斷的最後區塊，因此最後的句子或工具呼叫可能會遺失。回覆 `continue` 以讓 Claude 從其最後完成的區塊繼續。
- 在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)（`-p`）中：
  - 使用預設文字輸出，Claude Code 會列印它仍然從輪次早期保留的最後完成的文字區塊，然後是此訊息。當它沒有保留任何內容時，Claude Code 會單獨列印此訊息，例如因為 Claude Code 在輪次中間壓縮了對話並清除了該文字。在 v2.1.219 之前，Claude Code 在 `-p` 文字輸出中只列印此訊息並丟棄它已經產生的回應。
  - 使用 `--output-format json` 或 `stream-json`，Claude Code 會在 `result` 欄位中報告此訊息。
  - 一旦連線穩定，要繼續該輪次，請恢復工作階段並按照[繼續對話](https://code.claude.com/docs/zh-TW/headless#continue-conversations)中的說明傳送 `continue`。

### Auto mode cannot determine the safety of an action

[auto mode](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode) 使用的模型無法產生決定來分類動作，因此 auto mode 沒有自動批准該動作。您看到的訊息取決於分類器如何失敗。 讀取、搜尋和編輯您的工作目錄內的內容會跳過分類器，因此它們在所有這些情況下都能繼續工作。 當分類器模型不可用時：

```
<model> is temporarily unavailable, so auto mode cannot determine the safety of <tool> right now. Wait a moment and then try this action again.

```

當 Claude Code 可以判斷故障類別時，它會在 `temporarily unavailable` 後面的括號中名稱該類別，例如 `<model> is temporarily unavailable (rate-limited), so auto mode cannot determine the safety of <tool> right now`。類別為 `(rate-limited)`、`(overloaded)`、`(server error)`、`(timed out)` 和 `(connection failed)`。速率限制、過載和伺服器錯誤是暫時的，重試有效。如果 `(timed out)` 或 `(connection failed)` 重複，請檢查您的連線；請參閱[無法連線到 API](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api)。在 v2.1.229 之前，訊息從不名稱類別，讀作 `Wait briefly and then try this action again`。 當沒有類別符合時，訊息出現時括號中沒有類別；多個故障會產生該形式。在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 上，包括 [Mantle 端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint)，當您的 AWS 帳戶無法叫用訊息中名稱的模型時，它也會出現，該故障在每次重試時重複，直到您的帳戶被授予存取該模型的權限。 **該怎麼做：**

- 在幾秒後重試；Claude 會看到相同的訊息，通常會自動重試。暫時故障與 [auto mode 資格](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)無關；您不需要變更設定
- 如果重試持續失敗，請繼續進行唯讀任務，稍後再回到被阻止的動作
- 在 Amazon Bedrock 上，如果訊息在每次重試時返回，請檢查您的帳戶是否可以叫用它名稱的模型：對於標準 Amazon Bedrock 模型，確認您的 [IAM 政策](https://code.claude.com/docs/zh-TW/amazon-bedrock#iam-configuration)允許叫用它；對於 Mantle 模型 ID，[聯絡您的 AWS 帳戶團隊](https://code.claude.com/docs/zh-TW/amazon-bedrock#mantle-endpoint-errors)

當分類器請求失敗是因為您的 OAuth 令牌過期或被另一個工作階段輪換時，Claude Code 會重新整理令牌並重試請求一次，因此例行令牌過期不會作為此訊息出現。在 v2.1.216 之前，過期或輪換的令牌會導致每個分類器請求失敗，auto mode 會以此訊息拒絕每個檢查的動作，直到令牌被重新整理。 當分類器返回無法解析的回應時：

```
Auto mode could not evaluate this action and is blocking it for safety — run with --debug for details

```

**該怎麼做：**

- 重試該動作；這通常在下一次嘗試時成功
- 執行 `claude --debug` 並重複該動作以在偵錯日誌中查看基礎分類器回應

當單獨的 API 安全檢查因為早期對話內容而阻止分類器請求時：

```
Auto mode could not evaluate this action and is blocking it for safety — a safety check separate from auto mode blocked this request because of earlier conversation content — it isn't about the action itself — run with --debug for details

```

Claude Code 拒絕該動作，但告訴 Claude 這不是對該動作不安全的判斷，並繼續進行其他任務而不是重試。這些拒絕不計入 [auto mode 的暫停閾值](https://code.claude.com/docs/zh-TW/permission-modes#when-auto-mode-falls-back)。在[非互動式](https://code.claude.com/docs/zh-TW/headless) `-p` 執行中，Claude Code 不會停止執行。Claude 接收的內容取決於它在哪裡請求該動作：

- 對於 `-p` 執行中沒有 `--input-format stream-json` 的[背景子代理](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)，Claude Code 會返回包含 `Agent aborted: auto mode classifier request refused by the safety safeguard in headless mode` 的錯誤結果
- 在其他地方，包括互動式工作階段和 `-p` 執行的主對話，Claude Code 會將該拒絕返回給 Claude

在 v2.1.225 之前，Claude Code 計算這些拒絕以達到暫停閾值，並返回與真正分類器區塊相同的拒絕訊息。 **該怎麼做：**

- 這不是對您的動作的決定。您對話中已有的內容在 auto mode 將對話傳送給分類器時觸發了 API 上的安全篩選器
- 重試無法幫助；相同的對話內容將再次觸發篩選器
- 在互動式工作階段中，切換到不同的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)，以便您可以在提示時批准該動作
- 開始一個新的對話，不包含觸發內容

當對話增長超過分類器的上下文視窗時：

```
Auto mode classifier transcript exceeded context window — falling back to manual approval (try /compact to reduce conversation size)

```

動作發生的情況取決於 Claude 在哪裡請求它：

- 在互動式工作階段中，auto mode 會回退到該動作的正常權限提示，以便您可以手動批准或拒絕它
- 對於 [非互動式](https://code.claude.com/docs/zh-TW/headless) `-p` 執行中沒有 `--input-format stream-json` 的[背景子代理](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)，Claude Code 會返回包含 `Agent aborted: auto mode classifier transcript exceeded context window in headless mode` 的錯誤結果，執行繼續
- 在 `-p` 執行中的其他地方，沒有 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)，沒有提示可以回退到，因此動作不執行，執行繼續

**該怎麼做：**

- 在互動式工作階段中，在出現的提示中批准或拒絕該動作
- 在互動式工作階段中，執行 `/compact` 以減少對話大小，以便後續動作再次適應分類器視窗

### Agent terminated early due to an API error

[子代理](https://code.claude.com/docs/zh-TW/sub-agents)的 API 請求終止失敗，例如因為達到使用限制或伺服器錯誤的重試用完，所以子代理在完成其任務之前停止。此訊息需要 Claude Code v2.1.199 或更高版本；在此之前，API 錯誤文字被返回給 Claude，就像它是子代理的結果一樣。

```
Agent terminated early due to an API error: <error detail>

```

**該怎麼做：**

- 將冒號後的錯誤詳細資訊與此頁面上的其自己的部分相符，例如[使用限制](https://code.claude.com/docs/zh-TW/errors#usage-limits)或[伺服器錯誤](https://code.claude.com/docs/zh-TW/errors#server-errors)，並遵循該部分的步驟
- 一旦基礎錯誤清除，請要求 Claude 重試任務或[恢復子代理](https://code.claude.com/docs/zh-TW/sub-agents#resume-subagents)

當速率限制、過載或伺服器錯誤中斷已經產生文字輸出的前景子代理時，Claude 會收到該部分輸出標記為不完整，而不是此錯誤。其唯一輸出是工具呼叫的子代理也會收到此錯誤；在 v2.1.199 中，該形狀返回了空部分結果。請參閱[子代理中的 API 錯誤](https://code.claude.com/docs/zh-TW/sub-agents#api-errors-in-subagents)。

## 使用限制

本節中的大多數錯誤表示與您的帳戶或方案相關的配額已達到。其中三個的運作方式不同：[`伺服器暫時限制請求`](https://code.claude.com/docs/zh-TW/errors#server-is-temporarily-limiting-requests) 是與您的方案配額無關的伺服器端節流，[`1M 上下文需要使用額度`](https://code.claude.com/docs/zh-TW/errors#usage-credits-required-for-1m-context) 是權利檢查而非耗盡的配額，[`確認提示未獲回應`](https://code.claude.com/docs/zh-TW/errors#the-prompt-to-confirm-went-unanswered) 表示使用額度同意提示已關閉且未獲回應，無論是否達到配額。

### 您已達到工作階段限制

訂閱方案包括滾動使用額度。當額度用完時，您會看到以下其中一條訊息：

```
You've hit your session limit · resets 3:45pm
You've hit your weekly limit · resets Mon 12:00am
You've hit your Opus limit · resets 3:45pm
You've hit your Sonnet limit · resets 3:45pm

```

Claude Code 會阻止進一步的請求，直到訊息中顯示的重設時間。工作階段和每週限制在所有模型中共享，因此切換模型不會恢復存取。Opus 和 Sonnet 限制各自僅適用於對該模型系列的請求，因此使用 `/model` 切換到該系列外的模型可讓您繼續工作。 在使用 claude.ai 訂閱登入的互動式工作階段中，Claude Code 也可以在開啟的工作階段中等待，並在重設後不久繼續中斷的任務。等待時，工作階段底部的一行會顯示 `Usage limit reached · continuing automatically at 3:45pm · esc to cancel`。在空提示處按 `Esc` 可取消等待。請參閱[等待使用限制重設](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)以了解您看到的內容、如何開始或取消等待，以及如何關閉自動繼續。在 v2.1.234 之前，Claude Code 不提供此等待功能。 使用量同時計入工作階段和每週額度。單次大量活動突發（例如大型工作流程扇出）可能會在工作階段視窗重設之前耗盡每週額度。 **該怎麼做：**

- 等待錯誤中顯示的重設時間
- 在[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop)的 Code 標籤中，工作階段限制卡片提供**達到限制時自動繼續** 核取方塊。每週限制卡片則不提供。勾選後，桌面應用程式會在重設後重試中斷的回合，並在卡片上顯示重試時間。桌面核取方塊和 CLI 在 `/config` 中的**達到使用限制時自動繼續** 設定是分開的，因此請分別關閉每一個。
- 對於 Opus 或 Sonnet 限制，執行 `/model` 並切換到該系列外的模型以繼續工作。每個模型都有自己的提示快取，因此下一個請求會重新讀取整個對話，沒有快取命中；請參閱[切換模型](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)
- 執行 `/usage` 以查看您的方案限制和重設時間
- 執行 `/usage-credits` 以在 Pro 和 Max 上購買額外使用量，或在 Team 和 Enterprise 上向您的管理員請求。請參閱[付費方案的使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)以了解如何計費。
- 若要升級您的方案以獲得更高的基本限制，請參閱 [claude.com/pricing](https://claude.com/pricing)

在視窗用完之前，Claude Code 可以警告您已使用大部分額度，訊息例如 `You've used 85% of your session limit · resets 3:45pm`。若要持續監視您的剩餘額度，請將 `rate_limits` 欄位新增至[自訂狀態行](https://code.claude.com/docs/zh-TW/statusline#rate-limit-usage)，或在桌面應用程式中按一下模型選擇器旁的[使用量環](https://code.claude.com/docs/zh-TW/desktop#check-usage)。

### 1M 上下文需要使用額度

選定的模型使用 1M 權杖擴展上下文視窗，而您的方案僅透過使用額度包括它。

```
API Error: Usage credits required for 1M context · run /usage-credits to turn them on (they take effect after you restart Claude Code), or /model to switch to standard context

```

這是權利檢查，而非配額耗盡。即使您的工作階段和每週額度有剩餘容量，它也會觸發。請參閱[擴展上下文](https://code.claude.com/docs/zh-TW/model-config#extended-context)以了解哪些方案直接包括 1M 上下文，哪些需要使用額度。Claude Code 在您使用 `/model` 選擇模型時執行此檢查，且僅在直接連接到 Anthropic API 時執行；如果您將 `ANTHROPIC_BASE_URL` 指向[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)，`/model` 允許 `[1m]` 選擇，閘道決定請求是否成功。 當此錯誤在對話中期出現，因為上下文增長超過 200K 權杖時，Claude Code 會自動將對話壓縮回標準上下文限制以下，並之後將工作階段保持在該限制，因此無需採取任何行動。在 v2.1.172 之前的版本上，錯誤會在每個後續請求（包括 `/compact`）上重複；在這些版本上執行 `/clear` 以恢復。以下步驟適用於您明確選擇 `[1m]` 模型的情況。 **該怎麼做：**

- 執行 `/model` 並選擇不帶 `[1m]` 後綴的變體以回退到標準上下文視窗
- 訊息提及 `/usage-credits` 的地方，執行它以在 Pro 和 Max 上為 1M 變體開啟計量計費，或在 Team 和 Enterprise 上向您的管理員請求使用額度。重新啟動 Claude Code 一次使用額度開啟。在您重新啟動之前，工作階段會保持在標準上下文限制。
- 如果 `/model` 後錯誤仍然存在，1M 模型 ID 可能在其他地方設定。請參閱[設定您的模型](https://code.claude.com/docs/zh-TW/model-config#setting-your-model)以按優先順序檢查設定位置。
- 若要從模型選擇器中完全移除 1M 變體，請設定 [`CLAUDE_CODE_DISABLE_1M_CONTEXT=1`](https://code.claude.com/docs/zh-TW/env-vars)

在 v2.1.268 之前，訊息以 `run /usage-credits to turn them on, or /model to switch to standard context` 結尾，並未提及重新啟動。

### 確認提示未獲回應

如果您的帳戶需要 [Fable 使用額度同意](https://code.claude.com/docs/zh-TW/model-config#fable-and-usage-credits)，Claude Code 會要求您在 Fable 請求計費使用額度之前確認。當沒有人在可能沒有人在其終端的工作階段中回應該同意提示時，Claude Code 會關閉提示並以以下其中一條訊息結束回合：

```
Fable limit reached · continuing on Fable 5.1 uses usage credits, and the prompt to confirm went unanswered — nothing was sent · answer it where this session is running, or /model to change
Fable 5.1 now uses usage credits · the prompt to confirm went unanswered — nothing was sent · answer it where this session is running, or /model to change

```

訊息會命名工作階段的 Fable 模型，因此在 Fable 5 上它們會讀作 `continuing on Fable 5` 和 `Fable 5 now uses usage credits`。在 v2.1.257 之前，第一條訊息以 `Fable 5 limit reached` 開頭。 這發生在[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)工作階段、[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)和[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友工作階段中。Claude Code 僅在工作階段自己的互動式檢視中顯示同意提示：執行它的終端，或對於背景工作階段，一旦您附加，[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)。遠端控制用戶端無法顯示它。Claude Code 在 [`dialogExpiry`](https://code.claude.com/docs/zh-TW/settings-reference#dialogexpiry) 截止時間（預設為五分鐘）關閉提示，或在沒有人在該終端輸入時立即有新提示到達，例如從遠端控制用戶端發送的提示。在執行工作階段的終端輸入會取消截止時間，Claude Code 會等待您的回答。在附加的背景工作階段檢視中，輸入不會取消截止時間，新提示仍會關閉同意提示，因此請在任一情況發生之前回答。Claude Code 不發送任何內容並保持您的模型，因此當您發送下一個提示時，Claude Code 會再次顯示同意提示。 **該怎麼做：**

- 在執行工作階段的終端，發送另一個提示，當同意提示重新出現時回答它。對於背景工作階段，請先從[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)附加到它。從遠端控制用戶端重新發送會再次顯示此訊息，因為用戶端無法顯示提示。
- 執行 `/model` 以切換到不計費使用額度的模型
- 若要給自己更多時間到達該終端，請將 [`dialogExpiry`](https://code.claude.com/docs/zh-TW/settings-reference#dialogexpiry) 設定為更長的值或 `"never"`

在 v2.1.236 之前，此訊息不會出現：當遠端控制用戶端已連接時，Claude Code 會等待 60 秒以獲得答案，然後在您的預設模型上繼續回合。

### 伺服器暫時限制請求

API 應用了與您的方案配額無關的短期節流。

```
API Error: Server is temporarily limiting requests (not your usage limit)

```

Claude Code 通過真實限制回應所攜帶的統一配額標頭的缺失來區分這些。自 v2.1.199 起，無論您如何驗證，這都會[自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)並進行退避，然後才顯示。在較早的版本上，使用 claude.ai 訂閱登入的工作階段在第一次出現時失敗回合；只有 API 金鑰和 Enterprise 登入重試它。 **該怎麼做：**

- 稍等片刻後重試
- 如果問題持續，請檢查 [status.claude.com](https://status.claude.com)

### 請求被拒絕 (429)

您已達到為您的 API 金鑰、Amazon Bedrock 專案或 Google Cloud 專案設定的速率限制。

```
API Error: Request rejected (429) · this may be a temporary capacity issue. If it persists, check https://status.claude.com.

```

尾部句子命名檢查服務健康狀況的位置，並因提供者而異。Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 設定會命名該提供者的服務狀態，而不是 Anthropic 狀態頁面。自訂 `ANTHROPIC_BASE_URL` 會命名閘道主機。 **該怎麼做：**

- 執行 `/status` 並確認作用中的認證是您預期的認證。環境中的流浪 `ANTHROPIC_API_KEY` 可能會透過低階金鑰而不是您的訂閱路由請求。
- 檢查您的提供者主控台以了解作用中的限制，並在需要時請求更高的層級
- 對於 Anthropic API 金鑰，請參閱[速率限制參考](https://platform.claude.com/docs/en/api/rate-limits)以了解層級如何運作以及如何設定每個工作區的上限
- 降低並行性：降低 [`CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`](https://code.claude.com/docs/zh-TW/env-vars)、避免執行許多平行子代理，或使用 `/model` 切換到較小的模型以進行高容量指令碼執行

### 您已達到每月支出限制

您的方案包含的使用量無法涵蓋此請求，而原本會為其付費的[使用額度](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)已達到支出限制。這發生在您的方案的其中一個使用視窗已用完時，或當請求是僅由使用額度支付的請求時，例如對[計費至使用額度](https://code.claude.com/docs/zh-TW/model-config#fable-and-usage-credits)的模型的請求。訊息會命名哪個限制阻止了您。`·` 後面的文字說明如何提高該限制，並因您的方案和您是否管理計費而異：

```
You've hit your monthly spend limit · raise it at claude.ai/settings/usage
You've hit your individual spend limit · ask your admin for a higher limit
You've hit your org's monthly spend limit · visit claude.ai/admin-settings/usage to raise it
You've hit your team's shared budget · ask your admin to raise it at claude.ai/admin-settings/usage
You've hit your channel's monthly spend limit · an org owner or channel manager can raise it in the channel's Claude settings

```

`team's shared budget` 是管理員分配給您所屬群組的集區預算；訊息不會命名該群組。`channel's monthly spend limit` 是工作階段執行所在的 Slack 頻道的預算，因此您的組織可能在其外仍有預算。 當您的方案的其中一個視窗是用完的視窗時，訊息也會說明該視窗何時重設，例如 `· your session limit resets 3:45pm`，存取會在那時返回，無需任何人提高限制。在具有基於使用量的計費的組織上，訊息會說 `usage limit` 而不是 `spend limit`，如 `You've hit your individual usage limit`。 在 v2.1.239 之前，訊息不會命名方案視窗的重設時間。在 v2.1.268 之前，群組的集區預算產生了 `individual spend limit` 訊息，而不是 `team's shared budget`。 如果您透過 Claude 應用程式閘道連接並看到小寫 `spend limit reached`，那是您的閘道運營商的上限；請參閱[支出限制已達到](https://code.claude.com/docs/zh-TW/errors#spend-limit-reached)。 **該怎麼做：**

- 在 Pro 和 Max 上，在 claude.ai 的[**設定 > 使用量**](https://claude.ai/settings/usage)中提高您的每月支出限制，或執行 `/usage-credits`
- 在 Team 和 Enterprise 上，如果您管理計費，請在[**管理設定 > 使用量**](https://claude.ai/admin-settings/usage)中提高限制，或要求管理員提高。`/usage-credits` 會為您向您的管理員發送該請求
- 對於頻道的限制，要求組織擁有者或頻道的管理員在 claude.ai 上提高它。請參閱 Claude Tag 文件中的[每頻道限制](https://claude.com/docs/claude-tag/admins/set-spend-limit#per-channel-limits)
- 如果訊息命名您的方案視窗的重設時間，您可以改為等待它
- 執行 `/usage` 以查看您的方案視窗和每個視窗何時重設

### 已達到支出限制

您透過[Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)連接，並已超過閘道運營商設定的[支出上限](https://code.claude.com/docs/zh-TW/claude-apps-gateway-spend-limits)。閘道會阻止您的請求，直到命名的期間重設或運營商提高上限。它將每個被阻止的 `429` 回應標記為 `x-should-retry: false`，因此 Claude Code 會顯示此訊息而不重試。

```
spend limit reached (daily; resets 2026-08-09 00:00 UTC)

```

訊息會命名上限的期間和重設時間，當運營商設定了 `blocked_message` 時，他們的指示會跟在它後面。在 v2.1.225 之前，訊息只讀 `spend limit reached`；較舊版本上的閘道仍會發送該較短的形式。 **該怎麼做：**

- 等待訊息命名的重設時間，或如果訊息包含運營商的指示，請遵循它們
- 如果您經常達到上限，請要求您的閘道運營商提高上限

相關訊息 `spend limit unavailable` 表示閘道無法讀取其支出記錄，並作為預防措施而不是超過您的上限而阻止了請求。它通常會自行清除；如果它持續，請告訴您的閘道運營商。

### 信用額度餘額過低

您的 Console 組織已用完預付額度，或 Claude Code 正在使用 Console API 金鑰發送您的請求，而您打算使用您的訂閱。

```
Credit balance is too low

```

**該怎麼做：**

- 如果您有 Pro、Max、Team 或 Enterprise 方案並看到此訊息，執行 `/status` 並檢查 `API key` 列。環境中已核准的 `ANTHROPIC_API_KEY` 會透過該金鑰而不是您的訂閱路由請求。在目前的 shell 中取消設定它，並從您的 shell 設定檔中移除它，然後重新啟動 `claude`。如果您還沒有使用您的訂閱登入，請執行 `/login`。
- 在 [platform.claude.com/settings/billing](https://platform.claude.com/settings/billing) 新增額度，並考慮在那裡啟用自動重新載入，以便在餘額達到零之前重新填充
- 在 Console 中設定每個工作區的支出上限，以防止單個專案耗盡組織餘額。請參閱[有效管理成本](https://code.claude.com/docs/zh-TW/costs)。

### 無法更新您的支出限制

伺服器拒絕了您從達到支出限制時出現的提示中進行的支出限制變更。

```
Could not update your spend limit: <reason from the server>

```

當伺服器解釋拒絕時，訊息以該原因結尾，重試相同值會再次失敗。當失敗沒有伺服器提供的原因（例如連接中斷）時，訊息會讀作 `Could not update your spend limit. Press Enter to retry.`，重試可能會成功。在 v2.1.216 之前，Claude Code 為每個失敗顯示通用形式。 **該怎麼做：**

- 如果訊息包含原因，請選擇滿足它的限制，例如較低的金額
- 如果訊息僅顯示通用形式，請重試；失敗可能是暫時的
- 如果變更持續失敗，請改為在瀏覽器中從您的 [claude.ai 計費設定](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)進行變更

## 驗證錯誤

這些錯誤表示 Claude Code 無法向 API 證明您的身份。隨時執行 `/status` 以查看目前哪個認證資格處於活動狀態。

### 未登入

此工作階段沒有有效的認證資格可用。

```
Not logged in · Please run /login

```

**該怎麼做：**

- 執行 `/login` 以使用您的 Claude 訂閱或 Console 帳戶進行驗證
- 如果您預期環境變數會驗證您，請確認 `ANTHROPIC_API_KEY` 已在啟動 `claude` 的 shell 中設定並匯出
- 對於無法進行互動式登入的 CI 或自動化，請設定一個 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 指令碼，在啟動時擷取金鑰
- 請參閱[驗證優先順序](https://code.claude.com/docs/zh-TW/authentication#authentication-precedence)以瞭解當存在多個認證資格時 Claude Code 使用哪一個

如果系統反覆提示您登入，請參閱[未登入或權杖已過期](https://code.claude.com/docs/zh-TW/troubleshoot-install#not-logged-in-or-token-expired)以取得系統時鐘檢查和 macOS 認證儲存復原步驟。

### 無法解析驗證方法

工作階段到達 API 用戶端時沒有任何認證資格。[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)和雲端工作階段在背景工作程序啟動時沒有認證資格時會顯示此訊息。互動式、`-p` 和 Agent SDK 執行會將相同條件報告為[未登入](https://code.claude.com/docs/zh-TW/errors#not-logged-in)，並僅將此字串寫入其偵錯記錄，因此如果您在那裡找到它，請改為遵循該項目。

```
Could not resolve authentication method. Expected one of apiKey, authToken, credentials, config, or profile to be set. Or for one of the "X-Api-Key" or "Authorization" headers to be explicitly omitted

```

在目前版本上，此錯誤表示背景工作程序沒有可用的認證資格。在 v2.1.174 之前，指派給閒置預初始化背景工作程序的背景工作階段即使在設定了有效認證資格時也可能以此方式失敗。在 v2.1.176 之前，在被聲稱之前處於閒置狀態的雲端工作階段也可能如此。請升級以復原。 **該怎麼做：**

- 如果此訊息出現在背景或雲端工作階段中，且您的認證資格已設定，請升級至 v2.1.176 或更新版本
- 確認 `ANTHROPIC_API_KEY`、`CLAUDE_CODE_OAUTH_TOKEN` 或您的雲端提供者認證資格已在啟動背景工作程序的環境中設定，而不僅在您的互動式 shell 中設定
- 對於 Agent SDK，請參閱[快速入門中的驗證設定](https://code.claude.com/docs/zh-TW/agent-sdk/quickstart#setup)
- 在相同環境中的互動式工作階段中執行 `/status` 以確認哪個認證資格來源會解析

### 無效的 API 金鑰

`ANTHROPIC_API_KEY` 環境變數或 `apiKeyHelper` 指令碼傳回的金鑰被 API 拒絕，或 Claude Code 在傳送前阻止了來自 `ANTHROPIC_API_KEY` 的金鑰。

```
Invalid API key · Fix external API key

```

當訊息在 `Fix external API key` 之後繼續，並帶有描述（例如 `Invalid X-Api-Key header value from ANTHROPIC_API_KEY: it contains a line break at character 41 (120 characters on 2 lines).`）時，API 從未看到該金鑰。Claude Code 發現了 HTTP 標頭無法攜帶的字元，並在傳送前停止了請求。請參閱[無效的請求標頭值](https://code.claude.com/docs/zh-TW/errors#invalid-request-header-value)以瞭解如何讀取描述並修正該值。 **該怎麼做：**

- 檢查拼寫錯誤，並確認金鑰未在 [Console](https://platform.claude.com/settings/keys) 中被撤銷
- 在相同的 shell 中，執行 `env | grep ANTHROPIC`，或在 PowerShell 中執行 `Get-ChildItem Env:ANTHROPIC*`。direnv、dotenv shell 外掛程式和 IDE 終端機等工具可以從您專案中的 `.env` 檔案載入過時的金鑰，而無需您明確設定它
- 取消設定 `ANTHROPIC_API_KEY` 並執行 `/login` 以改用訂閱驗證
- 如果金鑰來自 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 指令碼，請直接執行該指令碼以確認它在 stdout 上列印有效的金鑰
- 執行 `/status` 以確認 Claude Code 實際使用的認證資格來源

### 您的 apiKeyHelper 指令碼失敗

Claude Code 執行了您的 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 設定中的命令，但沒有取回金鑰。沒有金鑰，請求會到達 API，並帶有預留位置認證資格，API 會以 `401` 拒絕它。終端機中的 `Authentication` 面板顯示發生了以下哪種情況：

- 命令以錯誤結束或逾時
- 命令未向 stdout 列印任何內容
- 命令列印了除金鑰以外的內容，例如登入橫幅或記錄行。面板顯示 `returned output that cannot be used as an API key` 並說明出了什麼問題，而不重複輸出。在 v2.1.227 之前，Claude Code 會傳送命令列印的任何內容，在修剪周圍空白後。

```
Your apiKeyHelper script is failing · This usually means you need to re-authenticate with your provider · Run /status to see the script's error output

```

在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)中，stderr 也會帶有具體原因，前綴為 `apiKeyHelper failed:`。 Claude Code 會重新執行指令碼並在顯示此訊息之前最多重試請求兩次，因此失敗會在三次嘗試內出現。在 v2.1.208 之前，Claude Code 會花費完整的[重試預算](https://code.claude.com/docs/zh-TW/errors#automatic-retries)使用預留位置認證資格重新傳送請求，然後報告通用 `401` 驗證錯誤，而不是指令碼失敗。 執行 `/login` 在這裡沒有幫助：只要設定存在，協助程式的輸出就會[優先於](https://code.claude.com/docs/zh-TW/authentication#authentication-precedence)已儲存的登入。 **該怎麼做：**

- 直接在您的 shell 中執行在 `apiKeyHelper` 中設定的命令以重現失敗
- 如果命令報告工作階段已過期，請使用您的認證資格提供者重新驗證，例如再次登入您的 SSO 或機密保管庫
- 修正命令，使其僅將金鑰列印到 stdout，作為單一可列印 ASCII 權杖，最多 16,384 個字元，並以代碼 0 結束。請參閱[使用 apiKeyHelper 輪換認證資格](https://code.claude.com/docs/zh-TW/llm-gateway-connect#rotate-credentials-with-apikeyhelper)以取得有效的設定。
- 執行 `/status` 以確認 `apiKeyHelper` 是活動認證資格來源。每次命令失敗時，其結束代碼和錯誤輸出都會出現在終端機中的 `Authentication` 面板中。在 v2.1.212 之前，該面板的標題為 `Cloud authentication`。

### 無效的請求標頭值

Claude Code 即將作為請求標頭傳送的值包含 HTTP 標頭無法攜帶的字元：換行符、NUL 位元組或 `U+00FF` 以上的字元，例如彎引號或零寬空格。Claude Code 在傳送任何內容之前停止請求，並命名要修正的變數或設定。常見原因是從帶有隱藏字元或雜散換行符的文件或聊天中貼上的認證資格。 Claude Code 在直接向 Claude API 或透過 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)傳送請求時執行此檢查。在第三方雲端提供者（例如 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)）上，Claude Code 在傳送前不執行此檢查。

```
Invalid auth token · Fix external auth token
Invalid ANTHROPIC_CUSTOM_HEADERS · Fix the environment variable
Invalid request header from the environment · Fix the environment variable

```

訊息的第一部分取決於不良值的來源：

- `Invalid auth token`：來自 [`ANTHROPIC_AUTH_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars) 或 [`CLAUDE_CODE_OAUTH_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars) 的持有人權杖
- `Invalid ANTHROPIC_CUSTOM_HEADERS`：您在 [`ANTHROPIC_CUSTOM_HEADERS`](https://code.claude.com/docs/zh-TW/env-vars) 中設定的標頭名稱或值。描述計算哪個 `Name: Value` 對有問題，例如 `distinct header 2 of 3 parsed from ANTHROPIC_CUSTOM_HEADERS`，而不重複名稱或值，因為您選擇了兩者。
- `Invalid request header from the environment`：Claude Code 從另一個環境變數（例如 `CLAUDE_AGENT_SDK_CLIENT_APP`）複製到請求標頭中的值。描述命名要修正的變數。

Claude Code 將此檢查捕獲的不良 `ANTHROPIC_API_KEY` 報告為[無效的 API 金鑰](https://code.claude.com/docs/zh-TW/errors#invalid-api-key)，具有相同的尾部描述。它將不良的已儲存 `/login` 認證資格報告為[未登入](https://code.claude.com/docs/zh-TW/errors#not-logged-in)；執行 `/login` 以儲存新的認證資格。[`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 指令碼的輸出永遠不會到達此檢查：Claude Code 在指令碼執行時驗證它，標頭無法攜帶的輸出會失敗，並顯示[您的 apiKeyHelper 指令碼失敗](https://code.claude.com/docs/zh-TW/errors#your-apikeyhelper-script-is-failing)。 在第二個 `·` 之後，訊息描述問題，如此完整範例所示：

```
Invalid auth token · Fix external auth token · Invalid Authorization header value from ANTHROPIC_AUTH_TOKEN: it contains a line break at character 41 (120 characters on 2 lines).

```

位置從 1 開始計算字元。描述是從固定短語和字元計數建立的，因此它永遠不包括值本身。它僅在字元是眾所周知的隱藏或排版字元（例如位元組順序標記、零寬空格或彎引號）時命名該字元，並將其他任何內容報告為 `a non-ASCII character`。 **該怎麼做：**

- 重新設定訊息命名的變數或設定，重新輸入報告位置周圍的字元，而不是從相同來源再次貼上
- 對於 `ANTHROPIC_CUSTOM_HEADERS`，每行保留一個 `Name: Value` 對，並重寫訊息計數的對
- 執行 `/status` 以確認哪個認證資格來源處於活動狀態

### 此組織已被停用

Claude Code 正在使用來自已停用 Console 組織的過時 `ANTHROPIC_API_KEY`。當您有已儲存的訂閱登入時，金鑰會覆蓋它。

```
Your ANTHROPIC_API_KEY belongs to a disabled organization · Unset the environment variable to use your subscription instead
Your ANTHROPIC_API_KEY belongs to a disabled organization · Update or unset the environment variable
API Error: 400 ... This organization has been disabled.

```

`·` 之後的提示取決於您的已儲存認證資格：當已儲存的 `/login` 可以在您取消設定金鑰後接管時出現第一種形式，當金鑰是您唯一的認證資格時出現第二種形式。 環境變數優先於 `/login`，因此在您的 shell 設定檔中匯出或從 `.env` 檔案載入的金鑰即使在您有有效的 Pro 或 Max 訂閱時也會被使用。在非互動式模式 (`-p`) 中，當存在金鑰時總是使用該金鑰。 **該怎麼做：**

- 在目前的 shell 中取消設定 `ANTHROPIC_API_KEY` 並從您的 shell 設定檔中移除它，然後重新啟動 `claude`
- 如果訊息說 `Update or unset`，您沒有已儲存的登入可以回退到。取消設定金鑰並執行 `/login`，或將金鑰替換為來自活動 Console 組織的金鑰。
- 之後執行 `/status` 以確認活動認證資格是您的訂閱
- 如果未設定環境變數且錯誤仍然存在，已停用的組織是與您的 `/login` 相關聯的組織。聯絡支援或使用不同帳戶登入。

### 您的組織已停用 API 金鑰驗證

此訊息需要 Claude Code v2.1.169 或更新版本。您的 Console 組織管理員已關閉 API 金鑰驗證，因此 API 拒絕 Claude Code 正在傳送的金鑰。恢復提示在 `·` 之後會根據金鑰的來源而異：

```
Your organization has disabled API key authentication · Run /login to sign in with your claude.ai account
Your organization has disabled API key authentication · Unset ANTHROPIC_API_KEY to use your claude.ai account instead
Your organization has disabled API key authentication · Unset ANTHROPIC_API_KEY and run /login to sign in with your claude.ai account
Your organization has disabled API key authentication · Unset the apiKeyHelper setting and run /login to sign in with your claude.ai account

```

環境變數和 `apiKeyHelper` 優先於 `/login`，因此在任一個仍在提供金鑰時單獨執行 `/login` 沒有幫助。請參閱[驗證優先順序](https://code.claude.com/docs/zh-TW/authentication#authentication-precedence)。 **該怎麼做：**

- 如果訊息命名 `ANTHROPIC_API_KEY`，在目前的 shell 中取消設定它，並從您的 shell 設定檔或 `.env` 檔案中移除它，然後重新啟動 `claude`
- 如果訊息命名 `apiKeyHelper`，從您的 `settings.json` 中移除 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper) 設定
- 執行 `/login` 以使用您的 claude.ai 帳戶登入
- 之後執行 `/status` 以確認活動認證資格是您的訂閱，而不是 API 金鑰
- 如果您需要 API 金鑰驗證來進行自動化，請要求您的組織管理員在 Console 中重新啟用它

### 您的組織已停用 Claude 訂閱存取

您的 Claude 組織不允許使用訂閱登入登入 Claude Code。使用相同帳戶再次執行 `/login` 會傳回相同的錯誤。

```
Your organization has disabled Claude subscription access for Claude Code · Use an Anthropic API key instead, or ask your admin to enable access

```

這是伺服器端組織設定，因此無法從本機設定、環境變數或 CLI 旗標覆蓋。 Agent SDK 和 `-p` 非互動式模式將此呈現為 `oauth_org_not_allowed` 錯誤代碼。 **該怎麼做：**

- 要求您的管理員為您的組織啟用 Claude Code 存取
- 使用 Console API 金鑰而不是您的訂閱進行驗證。請參閱 [Claude Console 驗證](https://code.claude.com/docs/zh-TW/authentication#claude-console-authentication)以取得設定。
- 如果您是管理員且看不到啟用存取的選項，請聯絡 [Anthropic 支援](https://support.claude.com)

### 您的組織政策已停用例行程序

您的 Team 或 Enterprise 組織中的擁有者已在組織層級關閉例行程序。當您嘗試建立或執行例行程序時會出現此錯誤，例如從 claude.ai/code 上的[例行程序](https://code.claude.com/docs/zh-TW/routines) UI。在 Claude Code v2.1.227 或更新版本上，相同的設定也會[隱藏 CLI 中的 `/schedule`](https://code.claude.com/docs/zh-TW/routines#troubleshooting)。

```
Routines are disabled by your organization's policy.

```

這是伺服器端設定，因此無法從本機設定、環境變數或 CLI 旗標覆蓋。 **該怎麼做：**

- 要求您的組織中的擁有者在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 啟用**例行程序** 切換
- 對於不需要組織層級例行程序的一次性排程工作，請參閱[排程工作](https://code.claude.com/docs/zh-TW/scheduled-tasks)

### Remote Control 需要 Anthropic API

工作階段未直接與 Anthropic API 通訊，因此沒有 claude.ai 後端供 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 配對。

```
Remote Control is only available when using Claude via api.anthropic.com. CLAUDE_CODE_USE_BEDROCK is set, so this session is using Amazon Bedrock — unset it (or run in a shell without it) to use Remote Control.

```

第二句解釋了什麼將工作階段路由到遠離 Anthropic API；在 v2.1.219 之前，訊息僅為第一句。根據原因，訊息命名：

- `CLAUDE_CODE_USE_*` 提供者變數，例如 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 的 `CLAUDE_CODE_USE_BEDROCK` 或 [Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 的 `CLAUDE_CODE_USE_VERTEX`
- [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 指向 `api.anthropic.com` 以外的主機，例如 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)或代理，即使您使用 claude.ai 登入；在 v2.1.196 之前，自訂基礎 URL 不會阻止 Remote Control
- `ANTHROPIC_UNIX_SOCKET` 已設定，因此工作階段透過本機 socket 而不是向 `api.anthropic.com` 傳送其請求
- 企業[雲端閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)透過 `/login` 進行的登入，不支援 Remote Control，且沒有變數可取消設定

**該怎麼做：**

- 取消設定訊息命名的變數，例如 `CLAUDE_CODE_USE_BEDROCK` 或 `ANTHROPIC_BASE_URL`，並重新啟動工作階段，或從直接與 Anthropic API 通訊的工作階段啟動 Remote Control
- 如果變數未在您的 shell 中設定，請檢查您的[設定檔](https://code.claude.com/docs/zh-TW/settings#where-settings-live)中的 `env` 金鑰，該金鑰將環境變數套用到每個工作階段
- 對於此和其他 Remote Control 啟動訊息，請參閱[疑難排解 Remote Control](https://code.claude.com/docs/zh-TW/remote-control#troubleshooting)

### Remote Control 無法重新整理您的登入

Claude Code 在短期認證資格上執行即時 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 連線，該認證資格是使用您已儲存的 claude.ai 登入取得和更新的。當 claude.ai 停止接受該登入，或 Claude Code 沒有剩餘的已儲存登入時，Claude Code 會停止 Remote Control 並需要您再次登入。任一失敗都可能在 Claude Code 仍在連線時或稍後在更新認證資格時發生。 當 Claude Code 要求登入服務重新整理您的已儲存登入並且沒有收到答案時，它會保持 Remote Control 執行並在連線的目前認證資格仍然有效時再次嘗試重新整理。當 Claude Code 無法到達登入服務、請求逾時或服務在不拒絕您的登入的情況下失敗時，重新整理會沒有答案。如果登入服務在該認證資格過期時仍未回答，Claude Code 會停止 Remote Control 並報告 `OAuth token refresh failed`。 當 Claude Code 停止 Remote Control 時，它會在警告和以 `Remote Control disconnected` 開頭的文字記錄行中顯示原因。您的本機工作階段會繼續執行，但沒有 Remote Control。本節涵蓋這些行：

```
Remote Control disconnected — Claude.ai login expired — run /login to restore Remote Control
Remote Control disconnected — Claude.ai login expired — run /login, then /remote-control
Remote Control disconnected — Claude.ai login was rejected — run /login, then /remote-control
Remote Control disconnected — OAuth token unavailable — run /login to restore Remote Control
Remote Control disconnected — OAuth token refresh failed — run /login to re-authenticate
Remote Control disconnected — JWT refresh failed: no OAuth token — run /login
Remote Control disconnected — Signed out of Claude — run /login, then /remote-control

```

Claude Code 在訊息中間命名原因：

- ` Claude.ai login expired` 和 `Claude.ai login was rejected`：claude.ai 不再接受您的已儲存登入權杖，因為它已過期或被撤銷
- ` OAuth token unavailable`：當連線的認證資格到期進行更新時，Claude Code 沒有已儲存的登入權杖
- `OAuth token refresh failed`：claude.ai 在 Claude Code 重新連線時拒絕了您的已儲存登入權杖，重新整理權杖未產生新的權杖
- `JWT refresh failed: no OAuth token`：Claude Code 找不到已儲存的登入權杖來更新
- ` Signed out of Claude`：您在此機器上登出，例如在另一個終端機中執行 `/logout`，因此 Claude Code 沒有剩餘的已儲存登入來更新連線

**該怎麼做：**

- 執行 `/login` 以再次登入
- 執行 `/remote-control` 以重新連線工作階段。以 `run /login to restore Remote Control` 結尾的訊息不需要此步驟：Claude Code 在您登入後會自動重新連線。

在 v2.1.224 之前，`OAuth token refresh failed — run /login to re-authenticate` 讀作 `OAuth token refresh failed — re-authenticate, then re-enable Remote Control`，`JWT refresh failed: no OAuth token — run /login` 讀作 `no OAuth token available for recovery (code <N>)`。` Claude.ai login expired`、`Claude.ai login was rejected` 和 `OAuth token unavailable` 訊息已在 v2.1.225 中新增。 在 v2.1.238 之前，Claude Code 將現在說 `Signed out of Claude` 的情況報告為 `JWT refresh failed: no OAuth token — run /login`，並在一次登入重新整理沒有收到答案時立即停止 Remote Control，並顯示 `Claude.ai login expired — run /login to restore Remote Control`。

### Remote Control 因為已登入帳戶已變更而停止

Claude Code 在 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段期間顯示此行，當您在此機器上登入不同的 claude.ai 帳戶或組織時。您在 Claude Code 工作階段外進行了切換，例如在另一個終端機中執行 `/login`。 您在透過 `/login` 登入時啟動的 Remote Control 工作階段屬於當時登入的 claude.ai 帳戶和組織。

```
Remote Control disconnected — signed-in claude.ai account or organization changed on this machine — run /remote-control to start a session for the current account, or /login to switch back, then /remote-control

```

Claude Code 在 claude.ai 確認帳戶或組織已變更後立即停止 Remote Control 工作階段。您的本機工作階段會繼續執行，但沒有 Remote Control。 **該怎麼做：**

- 執行 `/remote-control` 以在目前帳戶或組織下啟動新的 Remote Control 工作階段
- 若要切換回去，請執行 `/login` 並再次登入先前的帳戶或組織。然後執行 `/remote-control`。

在 v2.1.234 之前，當您在 Claude Code 工作階段外切換到不同帳戶或組織時，Claude Code 沒有注意到。Claude Code 保持 Remote Control 工作階段連線，直到稍後對 Remote Control 伺服器的請求失敗，並顯示 `Remote Control server rejected the request (HTTP 404)`。該失敗可能在切換後數小時才出現。

### Remote Control 因為執行工作階段的應用程式登出或切換帳戶而停止

當 Claude 桌面應用程式或 IDE 主持您的工作階段時，Claude Code 從該應用程式而不是從 `/login` 取得其登入權杖。當 claude.ai 拒絕該權杖時，Claude Code 要求應用程式提供新的權杖。如果應用程式回答它已登出，或它現在已登入不同的 Claude 帳戶，Claude Code 會結束 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段並向應用程式傳送以下其中一行：

```
Remote Control stopped — the app running this session is now signed in to a different Claude account
Remote Control stopped — the app running this session is signed out of Claude. Sign in there, then turn Remote Control back on

```

您的本機工作階段會繼續執行，但沒有 Remote Control。 **該怎麼做：**

- 如果應用程式已登出，請再次登入，然後在應用程式中重新開啟 Remote Control
- 如果應用程式切換了帳戶，Claude Code 無法在新帳戶下繼續已結束的工作階段。在該帳戶下啟動新的 Remote Control 工作階段。

在 v2.1.238 之前，Claude Code 在兩種情況下都向應用程式傳送了[Remote Control 無法重新整理您的登入](https://code.claude.com/docs/zh-TW/errors#remote-control-couldnt-refresh-your-login)下列出的 `run /login` 訊息。

### OAuth 權杖已撤銷或已過期

您的已儲存登入不再有效。撤銷的權杖表示您在任何地方登出或管理員移除了存取；已過期的權杖表示自動重新整理在工作階段中失敗。 兩個訊息都報告 API 為 Claude Code 傳送的請求傳回的拒絕。當已儲存的登入在失敗的重新整理後已被清除時，您會看到[登入已過期](https://code.claude.com/docs/zh-TW/errors#login-expired)。如果您在 [`CLAUDE_CODE_OAUTH_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars) 中使用長期權杖進行驗證，當該權杖過期或被撤銷時，您會看到相同的訊息。

```
OAuth token revoked · Please run /login
Please run /login · API Error: 401 OAuth token has expired ...

```

**該怎麼做：**

- 執行 `/login` 以再次登入
- 如果在重新驗證後同一工作階段內錯誤返回，請先執行 `/logout` 以完全清除已儲存的權杖，然後執行 `/login`
- 如果您使用 `CLAUDE_CODE_OAUTH_TOKEN` 環境變數進行驗證，Claude Code 會在請求失敗並顯示 401 後繼續傳送您設定的值，而不是切換到已儲存登入的權杖。[`/status`](https://code.claude.com/docs/zh-TW/commands) 將此認證資格顯示為讀取 `CLAUDE_CODE_OAUTH_TOKEN` 的 `Auth token` 列。使用 [`claude setup-token`](https://code.claude.com/docs/zh-TW/authentication#generate-a-long-lived-token) 產生新的權杖並使用它重新啟動，或取消設定變數並執行 `/login`。在 v2.1.225 之前，Claude Code 可以在工作階段中期用已儲存登入的短期存取權杖替換變數的值，一旦該權杖過期，工作階段就會再次失敗，並顯示 401 錯誤。
- 對於跨啟動的重複登入提示，請參閱[疑難排解](https://code.claude.com/docs/zh-TW/troubleshoot-install#not-logged-in-or-token-expired)中的系統時鐘檢查和 macOS 認證儲存復原步驟
- 對於其他失敗，包括 `403 Forbidden` 和 OAuth 瀏覽器問題，請參閱[登入和驗證](https://code.claude.com/docs/zh-TW/troubleshoot-install#login-and-authentication)

### API 錯誤：401 無效的驗證認證資格

API 識別了您的認證資格格式，但拒絕了其背後的帳戶或組織。當認證資格最近被撤銷、組織被停用或移除了您的存取，或帳戶本身被停用時，Anthropic 會傳回此訊息，因此過期的權杖不是原因。認證資格可以是您的已儲存登入或已核准的 `ANTHROPIC_API_KEY`，修正方式不同，因此首先執行 `/status` 以查看哪一個處於活動狀態。

```
Please run /login · API Error: 401 Invalid authentication credentials

```

**該怎麼做：**

- 如果 `/status` 顯示未標記為未使用的 `API key` 列，則已核准的 [`ANTHROPIC_API_KEY`](https://code.claude.com/docs/zh-TW/authentication#authentication-precedence) 是活動認證資格，優先於您的登入，因此 `/login` 不會替換它。在 Claude Console 中輪換金鑰，或執行 `unset ANTHROPIC_API_KEY` 回退到您的訂閱，或在 PowerShell 中執行 `Remove-Item Env:ANTHROPIC_API_KEY`。
- 如果 `/status` 僅顯示您的登入，請執行 `/login` 一次。如果認證資格被撤銷，新的登入會替換它。
- 如果相同的訊息對相同的登入帳戶返回，則帳戶或組織不再活動。檢查 `/status` 報告的帳戶和組織，並要求您的組織管理員恢復存取。
- 如果 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 指向 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)，`401` 之後的文字是您的閘道訊息，而不是 Anthropic 的訊息，`/login` 不會改變它。改為修正您的閘道期望的認證資格。

### 登入已過期

Claude Code 嘗試更新您已儲存的 claude.ai 或 Claude Console 登入，OAuth 服務拒絕了已儲存的重新整理權杖，因此 Claude Code 清除了已儲存的認證資格。之後，每個模型請求在到達 API 之前都會在本機停止，並顯示此訊息，因為只有 `/login` 可以建立新的認證資格。 在 v2.1.206 之前，Claude Code 無論如何都會傳送模型請求，並使用環境中剩餘的任何認證資格，每個模型都會失敗，並顯示[所選模型有問題](https://code.claude.com/docs/zh-TW/errors#theres-an-issue-with-the-selected-model)或 401，而不是登入提示。

```
Login expired · Please run /login

```

在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)(`-p`) 和 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 中，訊息讀作如下，結構化錯誤代碼為 `authentication_failed`：

```
Failed to authenticate: OAuth session expired and could not be refreshed

```

這與[OAuth 權杖已撤銷或已過期](https://code.claude.com/docs/zh-TW/errors#oauth-token-revoked-or-expired)的狀態不同。這些訊息報告 API 傳回的拒絕。Claude Code 本身為已失敗更新的登入產生 `Login expired`，因此它不傳送請求。當更新失敗是因為帳戶本身被暫停而不是登入過時時，Claude Code 會改為顯示[您的帳戶已被暫停](https://code.claude.com/docs/zh-TW/errors#your-account-is-on-hold)。 使用 API 金鑰、[`CLAUDE_CODE_OAUTH_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars) 或第三方提供者進行驗證的工作階段不使用已儲存的登入，永遠不會看到此訊息。 您可以在請求失敗之前檢查此狀態：[`/status`](https://code.claude.com/docs/zh-TW/commands) 顯示讀作 `Expired — log in again` 的 `Login` 列，加上它為過期登入儲存的組織和電子郵件。該列僅在已儲存的登入是您的活動認證資格且無法再更新時出現。以其他方式進行驗證的工作階段不會顯示該列，即使已儲存的過期登入仍然存在。在 v2.1.210 之前，`/status` 在此狀態下沒有指示登入曾經存在過，因為已清除的認證資格沒有留下任何內容供其報告。 **該怎麼做：**

- 執行 `/login` 以再次登入。在不登入的情況下重試會在每個請求上顯示相同的訊息。
- 在非互動式模式中，在相同環境中執行 `claude`，完成 `/login`，然後重新執行您的命令。對於無法以互動方式登入的自動化，使用 `ANTHROPIC_API_KEY` 或[使用 `claude setup-token` 產生長期權杖](https://code.claude.com/docs/zh-TW/authentication#generate-a-long-lived-token)進行驗證。
- 如果登入持續失敗，請參閱[登入和驗證](https://code.claude.com/docs/zh-TW/troubleshoot-install#login-and-authentication)

### Claude 登入未被接受

您嘗試啟動[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，伺服器以 401 拒絕建立它：它未接受此機器傳送的 Claude 登入，通常是因為登入已過期或被撤銷。 該行的第一部分是伺服器自己的原因（如果它給出的話）。否則該行讀作：

```
Claude login not accepted · Run /login, then try again

```

**該怎麼做：**

- 執行 `/login`，完成登入，然後再次啟動工作階段

### 管理員政策需要雲端閘道登入

此機器上的管理員[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)將 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 設定為 `"gateway"` 或設定 [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl)。除非您透過 `CLAUDE_CODE_USE_BEDROCK` 等變數選擇雲端提供者，Claude Code 只接受 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)登入。您會看到以下兩個訊息之一：

```
Not signed in to the Cloud gateway — run /login.

```

當工作階段沒有閘道登入時，模型請求會失敗，並顯示此訊息，例如因為您自政策到達機器後未執行 `/login`。 如果您也有 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 認證資格已設定，且受管設定設定了 `forceLoginMethod`，Claude Code 會在啟動時改為結束，並顯示以下開頭的訊息：

```
Administrator policy requires a Cloud gateway sign-in on this machine; the
Anthropic-issued credential configured here (ANTHROPIC_API_KEY,
ANTHROPIC_AUTH_TOKEN, or apiKeyHelper) is not used.

```

**該怎麼做：**

- 執行 `/login` 並在**雲端閘道** 畫面上完成登入
- 對於啟動訊息，移除您設定的 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 設定，然後啟動 `claude` 並執行 `/login`
- 如果您認為機器不應該需要閘道，請要求管理該機器的管理員從其受管設定中移除 `forceLoginMethod` 和 `forceLoginGatewayUrl`

在 v2.1.265 上，迴歸也在某些使用 API 金鑰、`apiKeyHelper` 或自訂標頭進行驗證的 LLM 閘道和代理設定中顯示第一個訊息，即使機器上沒有管理員要求。更新至 v2.1.266 或更新版本。您不需要變更您的設定。 在 v2.1.261 之前，在將 `forceLoginMethod` 設定為 `"gateway"` 的機器上，Claude Code 使用剩餘的已儲存登入，而不是失敗模型請求，並報告已設定的環境認證資格，並顯示 `This machine's managed settings require a first-party login` 而不是啟動訊息。在 v2.1.265 之前，其受管設定僅設定 `forceLoginGatewayUrl` 的機器不需要閘道登入，Claude Code 在那裡使用剩餘的認證資格。

### 您的帳戶已被暫停

Claude 帳戶背後的登入已被暫停。Claude Code 在嘗試更新您的已儲存登入並瞭解暫停時顯示第一個訊息，在您在瀏覽器中完成的登入報告時顯示第二個訊息：

```
Your account is on hold and can't use Claude Code. View details or appeal: https://claude.ai/restricted
Your account is on hold and can't sign in to Claude Code. View details or appeal: https://claude.ai/restricted

```

使用相同帳戶再次登入不會清除訊息，因為暫停是在帳戶上，而不是登入上。在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)(`-p`) 和 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 中，結構化錯誤代碼為 `account_on_hold`。在 v2.1.235 之前，Claude Code 將被暫停的帳戶報告為[登入已過期 · 請執行 /login](https://code.claude.com/docs/zh-TW/errors#login-expired)，其復原步驟無法清除暫停。 **該怎麼做：**

- 開啟訊息中的連結以檢視暫停的詳細資訊或對其提出異議
- 如果您有另一個 Claude 帳戶或不受暫停影響的 API 金鑰，您可以在暫停解決期間繼續工作：執行 `/login` 使用該帳戶，或使用 `ANTHROPIC_API_KEY` 設定金鑰

### Anthropic 設定檔登入已過期

Claude Code 透過 Anthropic 認證資格設定檔進行驗證，其已儲存的登入認證資格已過期，且設定檔沒有 Claude Code 可用來更新它的重新整理認證資格。Claude Code 在本機停止每個請求，不重試，因為重試會讀取相同的過期認證資格。

```
Anthropic profile login expired · Re-authenticate your Anthropic profile
Anthropic profile login expired · Run /login to use your claude.ai account instead, or re-authenticate the profile

```

這僅在活動認證資格來自 Anthropic 認證資格設定檔時出現，您可以使用 `ANTHROPIC_PROFILE` 環境變數選擇該設定檔，Claude Code 在您的 Anthropic 設定目錄中發現為活動設定檔，或 Claude Code 在您[登入時沒有 API 金鑰](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)時寫入。使用 `/login` 的 claude.ai 選項、API 金鑰、持有人權杖（例如 `ANTHROPIC_AUTH_TOKEN`）或第三方提供者進行驗證的工作階段永遠不會看到此訊息。 在[提供無金鑰登入](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)的機器上，執行 `/login`，選擇 Anthropic Console 帳戶，然後再次登入以更新無金鑰 Console 登入或 Claude Platform CLI 的 `ant auth login` 寫入的設定檔。Claude Code 替換該設定檔中的過期認證資格。對於聯盟設定檔或另一個工具建立的設定檔，`/login` 不會更新認證資格。您看到的形式取決於您是否明確選擇了設定檔或 Claude Code 發現了它：

- 當您明確設定 `ANTHROPIC_PROFILE` 時，訊息以 `Re-authenticate your Anthropic profile` 結尾。
- 當 Claude Code 從您的設定目錄發現設定檔時，訊息提供 `/login`，因為 Claude Code 優先使用有效的 `/login` 而不是發現的設定檔，然後改為使用您的 claude.ai 或 Console 帳戶進行驗證。在 v2.1.234 之前，Claude Code 在此情況下也顯示 `Re-authenticate your Anthropic profile` 形式。

**該怎麼做：**

- 再次登入設定檔，然後重試：在[提供無金鑰登入](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)的機器上，執行 `/login` 並為無金鑰 Console 登入或 Claude Platform CLI 的 `ant auth login` 寫入的設定檔選擇 Anthropic Console 帳戶；對於其他設定檔，使用建立它們的工具
- 如果管理員佈建了設定檔的認證資格，請要求他們簽發新的認證資格
- 執行 `/status` 以確認活動認證資格來源和設定檔名稱
- 若要停止使用設定檔，如果您設定了 `ANTHROPIC_PROFILE`，請取消設定它，然後以其他方式進行驗證，例如 `/login` 或 `ANTHROPIC_API_KEY`

### OAuth 範圍要求

已儲存的權杖早於較新功能需要的權限範圍。您最常從 `/usage` 和狀態行使用指標看到此訊息：

```
OAuth token does not meet scope requirement: user:profile

```

**該怎麼做：**

- 執行 `/login` 以取得具有目前範圍的新權杖。您不需要先登出。

### claude.ai 拒絕了工作階段權杖

[claude.ai 連接器](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)請求失敗，因為 claude.ai 拒絕了來自您的 Claude Code 登入的權杖，通常是已過期且無法更新的登入。被拒絕的權杖是您的登入，而不是連接器在 claude.ai 中的自身授權，因此再次授權連接器不會解決它。在 `/mcp` 中，連接器顯示為 `connected · session token rejected`，其詳細資訊檢視讀作：

```
claude.ai rejected the session token. Run /login, then reconnect.

```

**該怎麼做：**

- 執行 `/login` 以再次登入
- 從 `/mcp` 重新連線連接器，或執行 `/mcp reconnect <server>`。在您再次登入之前重新連線會使連接器處於相同狀態。`/mcp` 面板的**重新連線** 選項報告 `your claude.ai session token was rejected`；輸入的 `/mcp reconnect <server>` 形式報告成功重新連線，即使權杖仍被拒絕。

在 v2.1.222 之前，Claude Code 改為將連接器標記為需要驗證，這指向您進行連接器的授權流程，即使完成它也不會解決狀態。

### MCP 伺服器需要您再次登入

遠端 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)在工作階段中期拒絕了工具呼叫上的認證資格，通常是因為登入或權杖已過期或因為權杖缺少工具需要的權限。工具呼叫失敗，`/mcp` 將伺服器標記為[需要驗證](https://code.claude.com/docs/zh-TW/mcp#authenticate-with-remote-mcp-servers)。 對於您從 Claude Code 登入的伺服器，包括 claude.ai 連接器，登入已過期或被撤銷：

```
MCP server "<name>" needs you to sign in again (run /mcp to re-authenticate)

```

執行 `/mcp`，選擇伺服器，然後從其功能表再次登入。 對於使用 [`headersHelper`](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication) 指令碼設定的伺服器，Claude Code 已重新執行協助程式並在顯示此訊息之前重試呼叫一次：

```
MCP server "<name>" rejected the credential from its headersHelper (check the helper and run /mcp to reconnect, or to authenticate if the server also uses OAuth)

```

檢查協助程式傳回伺服器接受的認證資格，然後從 `/mcp` 重新連線，這會再次執行協助程式。 對於在其設定中具有靜態 `Authorization` 標頭的伺服器：

```
MCP server "<name>" rejected the Authorization header in its config (update it, then run /mcp to reconnect)

```

在伺服器設定的位置更新標頭值，然後從 `/mcp` 重新連線。 在 v2.1.273 之前，已過期登入、`headersHelper` 和 `Authorization` 標頭情況都顯示 `MCP server "<name>" requires re-authorization (token expired)`。 伺服器也可以拒絕帶有 HTTP 403 `insufficient_scope` 的工具呼叫，以要求您授權範圍，有時是您的權杖已列出的範圍。訊息命名該範圍：

```
MCP server "<name>" needs additional permissions (scope: "<scope>") — run /mcp to re-authenticate

```

執行 `/mcp`，選擇伺服器，然後從其功能表再次驗證。 當伺服器的設定既未設定 [`oauth.scopes`](https://code.claude.com/docs/zh-TW/mcp#restrict-oauth-scopes) 也未設定 [`authServerMetadataUrl`](https://code.claude.com/docs/zh-TW/mcp#override-oauth-metadata-discovery) 時，Claude Code 要求伺服器命名的範圍。使用任一設定，Claude Code 改為要求該設定的範圍。如果您釘選了 `oauth.scopes`，在再次驗證之前將遺漏的範圍新增到該列表。 在 v2.1.274 之前，此情況顯示 `needs you to sign in again` 訊息，在 v2.1.273 之前它顯示 `requires re-authorization (token expired)` 如其他情況。

### 授權回應中的簽發者不匹配

在 [MCP OAuth 登入](https://code.claude.com/docs/zh-TW/mcp#authenticate-with-remote-mcp-servers)期間，授權伺服器重新導向回 Claude Code，並帶有 `iss` 參數，該參數不命名 Claude Code 從伺服器的 OAuth 中繼資料預期的簽發者。此步驟中的簽發者錯誤是授權伺服器混合攻擊的樣子，因此 Claude Code 失敗登入，而不是交換授權代碼。Claude Code 在瀏覽器登入後在 `/mcp` 伺服器功能表中顯示錯誤：

```
Issuer mismatch in authorization response (RFC 9207): expected "https://auth.example.com", received "https://other.example.com"

```

`expected` 是來自伺服器的 OAuth 中繼資料的簽發者，`received` 是重新導向攜帶的 `iss` 值。其重新導向不攜帶 `iss` 參數的登入通過檢查，除非伺服器的中繼資料設定 `authorization_response_iss_parameter_supported`，在這種情況下 Claude Code 失敗登入。 **該怎麼做：**

- 嘗試從 `/mcp` 再次登入
- 如果錯誤重複，請向伺服器操作員報告。修正是伺服器端的：授權伺服器必須在 `iss` 參數中傳回與在其中繼資料中宣傳的相同簽發者
- 若要在伺服器被修正時進行連線，請使用 [`MCP_SDK_GENERATION=v1`](https://code.claude.com/docs/zh-TW/env-vars) 啟動 Claude Code，其[執行時](https://code.claude.com/docs/zh-TW/mcp#mcp-client-runtimes)不執行此檢查。這會移除對混合攻擊的保護，因此偏好伺服器端修正

在 v2.1.232 之前，Claude Code 僅在逐步推出中或當您設定 `MCP_SDK_GENERATION=v2` 時使用 v2 執行時。

### AWS 認證資格已過期或無效

您的 AWS 工作階段權杖已過期或被拒絕。此訊息出現在來自 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 或 [Mantle 端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint) 的 401 上，這是這些提供者報告過期安全權杖的方式。 中間的動作提示會根據您的設定而異。穩定的部分是前導 `AWS credentials expired or invalid`：

```
AWS credentials expired or invalid · run /login and select "Claude Platform on AWS · refresh credentials", or run `aws sso login --profile myprofile` in another terminal · API Error: 401 ...

```

在 v2.1.273 之前，此訊息僅在您的設定檔中設定 [`awsAuthRefresh`](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration) 時出現。 **該怎麼做：**

- 如果提示說認證資格由此環境管理，啟動 Claude Code 的應用程式擁有認證資格，此處的其他步驟不適用：重試，或聯絡您的管理員
- 在另一個終端機中執行訊息中命名的命令，例如 `aws sso login --profile myprofile`，並完成瀏覽器登入，然後重試。否則自己重新整理您使用的 AWS 認證資格：您的 SSO 登入、存取金鑰、API 金鑰或代理權杖
- 在互動式工作階段中，您可以改為執行 `/login`，選擇**第三方平台** ，然後在**使用第三方平台** 下選擇 **Claude Platform on AWS · refresh credentials** 以執行相同命令，而無需重新啟動 Claude Code。請參閱[設定 AWS 認證資格](https://code.claude.com/docs/zh-TW/claude-platform-on-aws#1-configure-aws-credentials)
- 如果重新整理命令成功後錯誤重複，請在相同 shell 和設定檔中使用 `aws sts get-caller-identity` 確認身份在 Claude Code 外有效

### AWS 驗證失敗

您的 AWS 提供者傳回 403，或 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 傳回 401。 Amazon Bedrock 將過期的安全權杖報告為 403，但 403 也是它報告授權拒絕的方式，例如來自遺漏 IAM 權限或未為您的帳戶啟用的模型的 `AccessDeniedException`。Claude Code 無法判斷您遇到了哪個原因。 來自 Amazon Bedrock 的 401 也會落在這裡，而不是在[AWS 認證資格已過期或無效](https://code.claude.com/docs/zh-TW/errors#aws-credentials-expired-or-invalid)下，因為 Amazon Bedrock 不將過期的權杖報告為 401。來自該端點的 401 通常來自請求路徑中的其他內容，例如公司代理。 認證資格重新整理可以修正過期的權杖，無法修正其他原因，因此訊息提供兩者：

```
AWS authentication failed · run /login and select "Claude Platform on AWS · refresh credentials", or run `aws sso login --profile myprofile` in another terminal · if credentials are current, check AWS permissions and model access · API Error: 403 ...

```

中間的動作提示會根據您的設定而異。穩定的部分是前導 `AWS authentication failed`。 當 403 是 Amazon Bedrock 的答案，表示您沒有使用指定的模型 ID 存取該模型時，提示改為告訴您在 Amazon Bedrock 主控台中為您的帳戶和區域啟用該模型。 在 v2.1.273 之前，此訊息僅在您的設定檔中設定 [`awsAuthRefresh`](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration) 時出現。 **該怎麼做：**

- 如果提示說認證資格由此環境管理，啟動 Claude Code 的應用程式擁有認證資格，此處的其他步驟不適用：重試，或聯絡您的管理員
- 重新整理您的 AWS 認證資格，以防過期的認證資格是原因：執行訊息中命名的命令（如果設定了一個），或自己重新整理您的 SSO 登入、存取金鑰、API 金鑰或代理權杖
- 如果您的認證資格是最新的，請確認 [IAM 設定](https://code.claude.com/docs/zh-TW/amazon-bedrock#iam-configuration)中的 IAM 權限已附加到您使用的身份，且所選模型已為您的帳戶和區域啟用
- 執行 `aws sts get-caller-identity` 以確認您的請求使用哪個身份；過時的 `AWS_PROFILE` 或預設設定檔是權限不匹配的常見原因

### 無法載入 AWS 或 Google Cloud 認證資格

Claude Code 無法從 AWS 認證資格提供者鏈或從它執行的機器上的 Google 應用程式預設認證資格取得可用的認證資格，因此沒有請求到達您的雲端提供者。Claude Code 清除其快取的認證資格並在顯示此訊息之前重試兩次。`·` 之後的詳細資訊命名具體原因，例如過期的 SSO 工作階段、遺漏的應用程式預設認證資格報告為 `Could not load the default credentials`，或被拒絕的登入報告為 `invalid_grant`：

```
API Error: Could not load AWS credentials · Could not load credentials from any providers. Check or refresh your AWS credentials and try again.
API Error: Could not load Google Cloud credentials · invalid_grant. Check or refresh your Google Cloud credentials and try again.

```

在[非互動式模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p` 和在 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 中，結構化錯誤代碼為 `cloud_credential_error`。在 v2.1.267 之前，訊息僅顯示 `API Error:` 之後的詳細資訊文字，結構化代碼為 `server_error` 或 `unknown`。 **該怎麼做：**

- 執行您的提供者的登入命令，例如 `aws sso login --profile myprofile` 或 `gcloud auth application-default login`，然後重試。[Bedrock、Agent Platform 或 Foundry 認證資格未載入](https://code.claude.com/docs/zh-TW/troubleshoot-install#bedrock-agent-platform-or-foundry-credentials-not-loading)顯示如何在 Claude Code 外確認認證資格
- 如果詳細資訊讀作 `AWS default-chain credential resolve timed out`，鏈掛起而不是失敗，因此改為遵循 [AWS default-chain credential resolve timed out](https://code.claude.com/docs/zh-TW/errors#aws-default-chain-credential-resolve-timed-out)

### AWS default-chain credential resolve 逾時

AWS 預設認證資格提供者鏈未在 60 秒內產生認證資格，因此 Claude Code 停止了解析並失敗了請求。此逾時是[無法載入 AWS 或 Google Cloud 認證資格](https://code.claude.com/docs/zh-TW/errors#could-not-load-aws-or-google-cloud-credentials)的一個原因。失敗是本機認證資格解析：請求永遠不會到達 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 或 [Mantle 端點](https://code.claude.com/docs/zh-TW/amazon-bedrock#use-the-mantle-endpoint)。Claude Code 在此錯誤出現之前清除其[認證資格快取](https://code.claude.com/docs/zh-TW/amazon-bedrock#credential-caching-and-resolution-timeout)並重試，因此到您看到它時，鏈已在重複嘗試中停滯。

```
API Error: Could not load AWS credentials · AWS default-chain credential resolve timed out. Check or refresh your AWS credentials and try again.

```

常見原因是您的 AWS 設定檔中的 `credential_process` 命令等待它無法接收的輸入，以及其執行個體中繼資料服務 (IMDS) 永遠不會回答鏈探測的容器或 VM。 在 v2.1.267 之前，訊息讀作 `API Error: AWS default-chain credential resolve timed out`。 在 v2.1.207 之前，停滯的鏈使請求無限期等待，而不是失敗。 **該怎麼做：**

- 在相同 shell 中使用相同 `AWS_PROFILE` 執行 `aws sts get-caller-identity`。如果它也掛起，請修正設定檔；以互動方式提示的 `credential_process` 命令是常見原因。
- 在啟動 Claude Code 之前完成登入步驟，例如 `aws sso login --profile myprofile`，以便鏈從本機 SSO 快取解析，而不是等待瀏覽器流程
- 如果您的鏈執行合法需要超過 60 秒的互動式登入，例如透過 `aws-vault` 等包裝程式的 SSO 與 MFA，請使用 [`CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) 以毫秒為單位提高限制

### Bedrock 設定驗證逾時等待 AWS

在 [Bedrock 設定精靈](https://code.claude.com/docs/zh-TW/amazon-bedrock#sign-in-with-bedrock)的認證資格驗證期間對 AWS 的呼叫（例如認證資格查詢或身份檢查）未在 60 秒限制內完成。精靈停止等待並失敗驗證步驟：

```
Timed out after 60s waiting for AWS. Check your network and proxy settings; if a credential helper needs longer to prompt you, raise CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS.

```

該數字反映您的限制：預設 60 秒，或您在 [`CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) 中設定的值。 常見原因是停滯對 AWS 的請求的網路或代理，包括 SSO 權杖重新整理，以及仍在等待您看不到的輸入的認證資格協助程式。僅在協助程式合法需要更多時間時提高限制。 對 AWS 的單一停滯請求也可能在其自身的每個請求逾時上失敗，這在相同步驟上顯示較短的訊息：

```
A request to AWS timed out. Check your network and proxy settings, then try again.

```

當相同的逾時發生在模型釘選步驟上時，精靈會將模型標記為 `unreachable`，而不是顯示任一訊息。 **該怎麼做：**

- 在相同 shell 中執行 `aws sts get-caller-identity`。如果它也掛起，停滯在 Claude Code 外，在您的網路、您的代理或您的 AWS 設定檔中的認證資格協助程式中；首先修正那個。
- 在開啟精靈之前完成任何互動式登入，例如 `aws sso login --profile myprofile`
- 如果您的 AWS 設定檔中的認證資格協助程式合法需要超過 60 秒來提示您，請使用 [`CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) 以毫秒為單位提高限制

### 雲端閘道工作階段已過期

您透過 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)登入，此機器上儲存的閘道工作階段已過期且無法更新，或閘道不再接受它，例如在閘道的 [JWT 機密被替換](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#jwt-secret-rotation)後。如果您在以互動方式啟動 `claude` 時看到此行，工作階段已開啟，未登入閘道：

```
Cloud gateway session expired — run /login to reconnect.

```

相同的行可以在工作階段中期出現，當閘道認證資格過期且 Claude Code 無法更新它時。 在[非互動式](https://code.claude.com/docs/zh-TW/headless)執行、背景或其他無人值守工作階段或 `claude` 子命令（除了 `claude auth`）中，Claude Code 會在閘道不再接受工作階段時改為結束，並顯示此訊息：

```
Cloud gateway <url> no longer accepts this session. Start `claude` and sign in again with /login.

```

**該怎麼做：**

- 在工作階段中執行 `/login` 並完成瀏覽器登入
- 對於非互動式啟動，在相同環境中啟動 `claude`，執行 `/login`，然後重新執行您的命令

### 閘道拒絕了請求

您透過 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)登入，請求傳回 403：閘道或其背後的上游拒絕了它。再次登入不會改變拒絕，因此訊息指向您的閘道管理員：

```
Gateway refused the request · signing in again won't change this — check with your gateway administrator · API Error: 403 ...

```

**該怎麼做：**

- 要求您的閘道管理員查詢請求。`API Error:` 尾部攜帶閘道傳回的拒絕
- 對於管理員：閘道上的[存取控制規則](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#http-tuning)傳回 403，[稽核記錄](https://code.claude.com/docs/zh-TW/claude-apps-gateway-deploy#logs)會記錄其原因，上游的授權拒絕會根據[上游錯誤訊息](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstream-error-messages)傳遞

在 v2.1.273 之前，閘道工作階段上的 403 顯示通用 `Please run /login` 或 `Failed to authenticate` 訊息，再次登入不會清除拒絕。

### Google Cloud 認證資格已過期或無效

您的 [Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) Google Cloud 認證資格已過期或被拒絕：請求傳回 401，這是 Agent Platform 報告認證資格過期的方式。 中間的動作提示會根據您的設定而異。穩定的部分是前導 `Google Cloud credentials expired or invalid`：

```
Google Cloud credentials expired or invalid · refresh your Google Cloud credentials (application default sign-in, or the key file in GOOGLE_APPLICATION_CREDENTIALS) and retry · API Error: 401 ...

```

**該怎麼做：**

- 如果提示說認證資格由此環境管理，啟動 Claude Code 的應用程式擁有認證資格，此處的其他步驟不適用：重試，或聯絡您的管理員
- 如果您使用應用程式預設認證資格進行驗證，請執行訊息中命名的 [`gcpAuthRefresh`](https://code.claude.com/docs/zh-TW/google-vertex-ai#advanced-credential-configuration) 命令或 `gcloud auth application-default login`，並完成登入，然後重試
- 如果您透過設定 `CLAUDE_CODE_SKIP_VERTEX_AUTH` 的 [LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)路由，請重新整理 `ANTHROPIC_AUTH_TOKEN` 或 `ANTHROPIC_CUSTOM_HEADERS` 中的閘道權杖，然後重試
- 如果您使用服務帳戶金鑰檔案進行驗證，請確認 `GOOGLE_APPLICATION_CREDENTIALS` 指向有效的金鑰。請參閱[設定 GCP 認證資格](https://code.claude.com/docs/zh-TW/google-vertex-ai#3-configure-gcp-credentials)
- 如果重新整理後錯誤重複，請在相同 shell 中使用 `gcloud auth application-default print-access-token` 確認身份在 Claude Code 外有效

在 v2.1.273 之前，來自 Agent Platform 的 401 顯示通用 `Please run /login` 或 `Failed to authenticate` 訊息，無法重新整理 Google Cloud 認證資格。

### Google Cloud 驗證失敗

[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 傳回 403，它用於授權拒絕而不是過期的認證資格。通常您驗證的身份缺少 IAM 權限，或該模型未為您的專案啟用。 中間的動作提示會根據您的設定而異。穩定的部分是前導 `Google Cloud authentication failed`：

```
Google Cloud authentication failed · refresh your Google Cloud credentials (application default sign-in, or the key file in GOOGLE_APPLICATION_CREDENTIALS) and retry · if credentials are current, check GCP IAM permissions and Vertex AI model access · API Error: 403 ...

```

**該怎麼做：**

- 如果提示說認證資格由此環境管理，啟動 Claude Code 的應用程式擁有認證資格，此處的其他步驟不適用：重試，或聯絡您的管理員
- 確認 [IAM 設定](https://code.claude.com/docs/zh-TW/google-vertex-ai#iam-configuration)中的角色已授予您驗證的身份
- 確認該模型已為您的專案啟用。請參閱[要求模型存取](https://code.claude.com/docs/zh-TW/google-vertex-ai#2-request-model-access)

在 v2.1.273 之前，來自 Agent Platform 的 403 顯示通用 `Please run /login` 或 `Failed to authenticate` 訊息，無法重新整理 Google Cloud 認證資格。

### Microsoft Foundry 驗證失敗

[Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 傳回 401 或 403：請求上的 Azure 認證資格被拒絕，或其背後的身份沒有存取 Foundry 資源的權限。`/login` 無法鑄造 Azure 認證資格。中間的動作提示會根據您的設定而異。穩定的部分是前導 `Microsoft Foundry authentication failed`：

```
Microsoft Foundry authentication failed · refresh your Foundry credential (ANTHROPIC_FOUNDRY_AUTH_TOKEN, ANTHROPIC_FOUNDRY_API_KEY, Azure sign-in for Entra, or your proxy token) and retry · if credentials are current, check access to the Foundry resource · API Error: 401 ...

```

**該怎麼做：**

- 如果提示說認證資格由此環境管理，啟動 Claude Code 的應用程式擁有認證資格，此處的其他步驟不適用：重試，或聯絡您的管理員
- 重新整理您在[設定 Azure 認證資格](https://code.claude.com/docs/zh-TW/microsoft-foundry#2-configure-azure-credentials)中設定的認證資格：輪換 `ANTHROPIC_FOUNDRY_API_KEY`、鑄造新的 `ANTHROPIC_FOUNDRY_AUTH_TOKEN`，或執行 `az login` 以便預設 Microsoft Entra 認證資格鏈可以再次登入
- 如果認證資格是最新的，請確認身份有權存取 Foundry 資源。請參閱 [Azure RBAC 設定](https://code.claude.com/docs/zh-TW/microsoft-foundry#azure-rbac-configuration)

在 v2.1.273 之前，來自 Microsoft Foundry 的 401 或 403 顯示通用 `Please run /login` 或 `Failed to authenticate` 訊息，無法重新整理 Azure 認證資格。

## 網路和連線錯誤

大多數這些錯誤表示來自 Claude Code 的網路請求無法到達其目的地，或 Claude Code 和 API 之間的某些東西在回程中改變了回應；如果條目也有本機原因（例如失敗的封存寫入），其內容會說明。它們通常源自您的本機網路、代理或防火牆，或雲端環境的網路原則。

### 無法連線到 API

到 API 的 TCP 連線失敗或從未完成。對於常見的連線錯誤代碼，訊息會命名失敗的類型並在括號中保留代碼：

```
Unable to connect to API. Check your internet connection
Connection refused — a firewall or proxy may be blocking it (ConnectionRefused)
Can't reach the API server — check your internet or DNS (ENOTFOUND)
No internet route — check your connection or VPN (EHOSTUNREACH)
Couldn't connect through your proxy (ERR_PROXY_TUNNEL) — the proxy refused the tunnel: check its credentials and that it allows this host
Connection dropped (ECONNRESET)
fetch failed
Request timed out. Check your internet connection and proxy settings

```

Claude Code 無法識別的代碼會顯示為 `Unable to connect to API` 後跟括號中的代碼。某些這些訊息可以顯示多個代碼：例如 `Connection refused` 可以顯示 `ConnectionRefused` 或 `ECONNREFUSED`，而 `Can't reach the API server` 可以顯示 `ENOTFOUND` 或 `FailedToOpenSocket`。 在 v2.1.227 之前，這些編碼訊息中的每一個都讀作 `Unable to connect to API` 後跟代碼，例如 `Unable to connect to API (ECONNREFUSED)`。 常見原因包括沒有網際網路存取、阻止 `api.anthropic.com` 的 VPN，或未設定的必需公司代理。 **該怎麼做：**

- 通過從同一個 shell 執行 `curl -I https://api.anthropic.com` 來確認您可以到達 API 主機。在 Windows PowerShell 上使用 `curl.exe -I https://api.anthropic.com`，以便不使用內建的 `Invoke-WebRequest` 別名。
- 如果您在公司代理後面，在啟動 Claude Code 之前設定 `HTTPS_PROXY` 並查看[網路設定](https://code.claude.com/docs/zh-TW/network-config)
- 如果您通過 LLM 閘道或中繼路由，將 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 設定為其位址。請參閱[將 Claude Code 連線到 LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway-connect)以進行設定。
- 確保您的防火牆允許[網路存取要求](https://code.claude.com/docs/zh-TW/network-config#network-access-requirements)中列出的主機
- 間歇性故障會[自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)；持續故障指向本機網路問題

如果 `curl` 成功但 Claude Code 仍然失敗，原因通常是執行時和網路之間的某些東西，而不是網路本身：

- 在 Linux 和 WSL 上，檢查 `/etc/resolv.conf` 是否有無法到達的名稱伺服器。特別是 WSL 可以從主機繼承損壞的解析器。
- 在 macOS 上，已斷開連線或卸載的 VPN 用戶端可能會留下隧道介面或路由規則。檢查 `ifconfig` 是否有過時的 `utun` 介面，並在系統設定中移除 VPN 的網路擴充功能。
- Docker Desktop 和類似的容器執行時可以攔截出站流量。退出它們並重試以排除這種可能性。

### 無法連線到 Anthropic 服務

在首次執行設定期間，Claude Code 會檢查它是否可以到達 `api.anthropic.com` 和 `platform.claude.com`，然後才顯示登入步驟。當任一檢查失敗時，Claude Code 會列印原因並退出。

```
Unable to connect to Anthropic services
Failed to connect to api.anthropic.com: ECONNREFUSED
Connection to api.anthropic.com timed out after 10 seconds
A proxy is configured via HTTPS_PROXY. Check that it allows connections to the host above.

```

Claude Code 通過與 API 請求相同的[代理設定](https://code.claude.com/docs/zh-TW/network-config)發送檢查，並給每個探測 10 秒。當失敗的探測通過代理時，訊息會命名設定它的環境變數，例如 `HTTPS_PROXY`。在 v2.1.222 之前，檢查使用不同的代理傳輸，沒有逾時：在具有 `https://` 方案的代理 URL 後面，它可能會在 `Checking connectivity...` 上無限期停滯，然後即使通過同一代理的 API 請求成功也會失敗。 當[受管設定檔案、MDM 原則或原則協助程式](https://code.claude.com/docs/zh-TW/managed-settings)將 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 設定為 `"gateway"`，或設定 [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl) 而不設定 `forceLoginMethod` 時，Claude Code 會跳過此檢查。使用任一設定，Claude Code 會在**雲端閘道** 畫面上開啟登入步驟，而不是 Anthropic 登入方法。當機器上存在受管設定來源但無法讀取時，Claude Code 也會跳過檢查，因為該來源可能保有閘道設定。在 v2.1.247 之前，Claude Code 在此設定下也執行檢查，當 Anthropic 的端點無法到達時以此錯誤退出。 **該怎麼做：**

- 如果訊息命名代理變數，檢查其值是否指向正確的代理，並要求您的網路團隊允許通過它到訊息中主機的 HTTPS 連線。請參閱[網路設定](https://code.claude.com/docs/zh-TW/network-config)。
- 完成[無法連線到 API](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api) 中的檢查。那裡的 `curl` 測試和防火牆指導也適用於此檢查。
- 如果您的組織通過[雲端閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)登入，並且此錯誤出現在首次執行時，請更新到 Claude Code v2.1.247 或更新版本。
- 如果您的網路是開放的，故障仍然存在，Claude Code 可能在您的國家[無法使用](https://www.anthropic.com/supported-countries)

### Socket 已關閉

`Socket is closed` 表示承載串流回應的連線在回應仍在到達時被關閉。最常見的原因是 Windows 上的公司代理在回應中途丟棄已建立的隧道。 根據回應進行的距離，Claude Code 會重試請求、保留 Claude 產生的內容，或結束回合。請參閱[自動重試](https://code.claude.com/docs/zh-TW/errors#automatic-retries)。 在 v2.1.214 之前，Claude Code 不會重試此故障，回合會停止並出現包含 `Socket is closed` 的錯誤。 **該怎麼做：**

- 如果您看到此錯誤，請使用 `claude update` 更新到 v2.1.214 或更新版本，然後再次傳送您的訊息
- 如果在更新後回合在同一代理後面持續失敗，請完成[無法連線到 API](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api) 並檢查[網路設定](https://code.claude.com/docs/zh-TW/network-config)中的代理設定

### API 傳回空的或格式不正確的回應

當 Claude Code 對失敗的串流請求進行非串流重試時，如果獲得 HTTP 成功狀態但主體不是 Claude API 訊息，Claude Code 會顯示此錯誤：通常是 HTML 錯誤或登入頁面、空主體或其他格式的 JSON。代理、閘道或網路登入頁面代替 API 回答是常見來源。Claude Code 不會重試請求，回合以此錯誤結束。

```
API returned an empty or malformed response (HTTP 200) — check for a proxy or gateway intercepting the request.

```

在該開頭之後，訊息會報告返回的內容以及哪個請求失敗：

- 一個 `Response:` 子句，包含內容類型、主體類型（例如 `body is an HTML page` 或 `empty body`）、其大小（以位元組為單位），以及回應是否攜帶 Anthropic 請求 id。當回應命名可識別的伺服器（例如 `nginx` 或 `cloudflare`）或攜帶中介標頭（例如 `cf-ray` 或 `via`）時，子句也會列出這些。
- 一個句子，命名失敗的串流請求的 id 和觸發重試的故障。當串流在故障前開啟時，它也會報告有多少串流事件到達，以及如果有的話，當嘗試失敗時串流已沉默多長時間。

在 v2.1.234 之前，訊息在 `intercepting the request` 後結束。 在 v2.1.271 之前，在非 JSON 內容類型（例如 `text/plain`）下攜帶有效 API 訊息的回覆也會以此錯誤結束回合。某些 LLM 閘道對非串流回覆使用該內容類型。 **該怎麼做：**

- 閱讀 `Response:` 子句以查看哪個系統回答。HTML 主體、沒有 Anthropic 請求 id 或命名的伺服器（例如 `nginx` 或 `cloudflare`）表示 Claude Code 和 API 之間的某些東西代替它回答
- 如果您通過[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway-connect#troubleshoot-gateway-errors)路由，使用直接請求測試路由，並修復返回非 API 回應的跳躍
- 在具有登入頁面的網路上（例如訪客 Wi-Fi），在瀏覽器中完成登入，然後重試
- 如果只有通過您的閘道的非串流路由損壞，設定 [`CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1`](https://code.claude.com/docs/zh-TW/env-vars#variables)，以便在串流中途失敗的請求進入正常重試路徑而不是此回退，除非串流端點本身傳回 `404`，Claude Code 仍然會回退

### 串流回應在收到任何完整資料之前結束

來自您的模型提供者的串流回應完成，但未傳遞任何可用資料，因此 Claude Code 重新傳送請求而不進行串流以完成回合。Claude Code 每個工作階段顯示一次警告，僅在互動式工作階段中。在 v2.1.239 之前，Claude Code 無聲地重試而不進行串流。

```
Streaming response ended before any complete data was received. Retrying without streaming. If this keeps happening, check any proxy or gateway between Claude Code and your model provider.

```

Claude Code 傳送每個受影響的請求兩次：空串流嘗試和重試。常見原因是在回程中消耗或轉換串流回應主體的代理或閘道。 **該怎麼做：**

- 設定 Claude Code 和您的模型提供者之間的任何代理或閘道，以未修改的方式傳遞串流回應主體及其標頭
- 在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 上，請參閱[閘道或代理後面的串流錯誤](https://code.claude.com/docs/zh-TW/amazon-bedrock#streaming-errors-behind-a-gateway-or-proxy)以了解標頭和主體要求

### Bedrock 串流回應具有意外的 content-type

Claude Code 和 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 之間的閘道或代理正在轉換串流回應主體或其 `Content-Type` 標頭。Amazon Bedrock 將回應串流為 `application/vnd.amazon.eventstream`。Claude Code 不會解碼無法讀取的主體，而是拒絕報告不同 content-type 的成功串流回應。Claude Code 不會重試請求。

```
Bedrock streaming response has content-type "text/event-stream"; expected "application/vnd.amazon.eventstream". A gateway or proxy between Claude Code and Bedrock is likely transforming the response body — Bedrock's binary event-stream format must be passed through unmodified. Set CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD=1 to suppress this check while the gateway is being fixed.

```

在 v2.1.208 之前，相同的設定錯誤在整個回應被緩衝後顯示為 `API Error: Truncated event message received`。 **該怎麼做：**

- 設定閘道以未修改的方式傳遞 `InvokeModelWithResponseStream` 回應主體及其 `Content-Type` 標頭。重新發出串流為伺服器傳送事件的中介是常見原因。
- 設定 [`CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD=1`](https://code.claude.com/docs/zh-TW/env-vars) 會隱藏此錯誤，但 Claude Code 不會在重寫的標頭下解碼二進位主體，因此這些請求會回退到較慢的非串流路徑。請參閱[閘道或代理後面的串流錯誤](https://code.claude.com/docs/zh-TW/amazon-bedrock#streaming-errors-behind-a-gateway-or-proxy)。

### SSL 憑證錯誤

您網路上的代理或安全應用程式正在使用自己的憑證攔截 TLS 流量，Claude Code 不信任它。

```
Unable to connect to API: SSL certificate verification failed (UNABLE_TO_GET_ISSUER_CERT_LOCALLY). The certificate comes from an authority Claude Code doesn't trust, usually a TLS-inspecting corporate proxy or a gateway signed by a private CA: set NODE_EXTRA_CA_CERTS to that CA bundle, or add it to the system certificate store · see https://code.claude.com/docs/en/network-config
Unable to connect to API: Self-signed certificate detected (SELF_SIGNED_CERT_IN_CHAIN). The certificate comes from an authority Claude Code doesn't trust, usually a TLS-inspecting corporate proxy or a gateway signed by a private CA: set NODE_EXTRA_CA_CERTS to that CA bundle, or add it to the system certificate store · see https://code.claude.com/docs/en/network-config

```

在 v2.1.273 之前，兩個訊息都在 `Check your proxy or corporate SSL certificates` 結束，沒有 OpenSSL 代碼或 `NODE_EXTRA_CA_CERTS` 提示。 從 v2.1.199 開始，憑證驗證失敗不會重試，因此此錯誤會在第一次嘗試時出現，而不是在完整[重試預算](https://code.claude.com/docs/zh-TW/errors#automatic-retries)後出現。較早的版本在顯示它之前花費幾分鐘重試。暫時性 TLS 條件（例如握手逾時）仍然會重試。 在 `/login` 和啟動連線檢查期間，相同的故障會產生不同的訊息：

```
SSL certificate error (UNABLE_TO_GET_ISSUER_CERT_LOCALLY). If you are behind a corporate proxy or TLS-intercepting firewall, set NODE_EXTRA_CA_CERTS to your CA bundle path, or ask IT to allowlist *.anthropic.com. Run `claude doctor` for details.

```

在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 上，Claude Code 本身發送給 AWS 的請求（例如 STS 和 SSO 角色認證呼叫、模型發現和設定精靈的檢查）取決於相同的憑證設定。請參閱[TLS 檢查代理後面的憑證錯誤](https://code.claude.com/docs/zh-TW/amazon-bedrock#certificate-errors-behind-a-tls-inspecting-proxy)。 **該怎麼做：**

- 匯出您組織的 CA 套件，並使用 `NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.pem` 將 Claude Code 指向它
- 請參閱[網路設定](https://code.claude.com/docs/zh-TW/network-config#custom-ca-certificates)以了解完整設定說明
- 不要設定 `NODE_TLS_REJECT_UNAUTHORIZED=0`，這會完全停用憑證驗證

### 雲端工作階段中不允許主機

來自雲端工作階段或例行程式的出站 HTTP 請求被環境的網路原則阻止。

```
HTTP 403
x-deny-reason: host_not_allowed

```

您也可能看到與目的地的真實憑證不符的 TLS 憑證。雲端工作階段通過代理路由出站流量，該代理強制執行網路原則，因此不符的憑證表示代理終止了連線，而不是目的地。 這不是用戶端網路問題。雲端工作階段和[例行程式](https://code.claude.com/docs/zh-TW/routines)在沙箱 VM 內執行，其通過工作階段網路的出站流量被過濾到[雲端環境的](https://code.claude.com/docs/zh-TW/cloud-environments)允許清單；[GitHub 操作](https://code.claude.com/docs/zh-TW/cloud-environments#github-proxy)和 MCP 連接器流量使用單獨的通道，這就是為什麼它們可以在其他主機被阻止時繼續工作。**預設** 環境使用**信任** 存取，允許[預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)的套件登錄、雲端提供者 API、容器登錄和常見開發網域，並阻止該路徑上的其他網域。 **該怎麼做：** 這些步驟會變更您自己的環境之一。[組織共享環境](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)在選擇器中以唯讀方式開啟，因此請要求擁有者從[管理設定](https://claude.ai/admin-settings)中的**雲端環境** 頁面變更其網路存取。

- 開啟例行程式進行編輯，或啟動雲端工作階段。選擇顯示您環境名稱的雲端圖示（例如**預設** ）以開啟選擇器。將滑鼠懸停在您的環境上，然後按一下設定圖示。
- 在**更新雲端環境** 對話方塊中，將**網路存取** 從**信任** 變更為**自訂** ，然後將被阻止的網域新增到**允許的網域** 。每行輸入一個網域。檢查**也包括常見套件管理員的預設清單** 以在您的自訂網域旁邊保留[預設允許清單](https://code.claude.com/docs/zh-TW/cloud-environments#default-allowed-domains)。如果您想要不受限制的存取，請改為選擇**完整** 。
- 按一下**儲存變更** 。下一次執行使用更新的允許清單。

請參閱[網路存取](https://code.claude.com/docs/zh-TW/cloud-environments#network-access)以了解存取層級和預設允許清單。本機 CLI 工作階段不受此原則影響。

### 代理拒絕了連線

當 Claude 通過您在 `HTTPS_PROXY` 中設定的代理或相關[代理變數](https://code.claude.com/docs/zh-TW/network-config#environment-variables)讀取[成品](https://code.claude.com/docs/zh-TW/artifacts)時，您會看到此訊息。成品內容來自 `*.frame.claudeusercontent.com`，因此 Claude Code 首先向代理傳送 `CONNECT` 請求，要求它開啟到該主機的隧道。當代理拒絕時，沒有任何東西到達主機，訊息攜帶代理的 HTTP 狀態：

```
artifact content fetch failed (proxy refused the connection: HTTP 407)
artifact content fetch failed (proxy refused the connection: HTTP 403)
the proxy refused the connection to the artifact's content host (HTTP 502)

```

狀態是代理對 `CONNECT` 的回答。主機從未回答，因此每個狀態指向不同的修復：

- `HTTP 407`：代理需要它沒有獲得的認證。將它們放在代理 URL 中，如[基本驗證](https://code.claude.com/docs/zh-TW/network-config#basic-authentication)所示。
- `HTTP 403`：代理拒絕隧道到 `*.frame.claudeusercontent.com`。要求運行代理的人允許該主機，[網路存取要求](https://code.claude.com/docs/zh-TW/network-config#network-access-requirements)會列出該主機。
- 任何其他狀態，例如 `HTTP 502`：代理因其自身原因未開啟隧道，例如無法到達主機。在代理的日誌中查詢狀態。
- `unreadable reply` 代替狀態：代理位址上的任何東西都沒有用 HTTP 狀態行回答。檢查位址是否為 HTTP 代理。

**該怎麼做：**

- 檢查代理變數中的位址和認證，如[代理設定](https://code.claude.com/docs/zh-TW/network-config#proxy-configuration)所述，然後從啟動 Claude Code 的 shell 執行 `curl -x http://proxy.example.com:8080 -I https://api.anthropic.com`，使用您自己的代理 URL。在 Windows PowerShell 上，執行 `curl.exe`。如果此探測以相同方式失敗，請先修復代理設定。如果成功，拒絕特定於成品主機。
- 如果您的網路讓 Claude Code 直接到達成品主機，將 `.frame.claudeusercontent.com` 新增到 [`NO_PROXY`](https://code.claude.com/docs/zh-TW/network-config#environment-variables)。保持條目狹窄：更廣泛的 `.claudeusercontent.com` 條目也會繞過 `bridge.claudeusercontent.com` 的代理，具有 [IP 允許清單](https://code.claude.com/docs/zh-TW/network-config#organization-ip-allowlists-and-proxy-egress)的組織需要將其保留在代理上。

在 v2.1.238 之前，Claude Code 將拒絕的隧道報告為通用網路錯誤。

### 雲端環境服務傳回空的或意外的回應

Claude Code 在多個點請求您的[雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)清單，例如當您從 CLI 建立雲端工作階段或執行 [`/remote-env`](https://code.claude.com/docs/zh-TW/cloud-environments#select-an-environment-from-the-cli) 時。當它無法讀取伺服器的回答時，它會顯示以下其中一個訊息：

```
The cloud environments service returned an empty response (HTTP 200 with no body). This is usually temporary — try again in a moment.
The cloud environments service returned a response in an unexpected format (HTTP 200 with a non-JSON body). This is usually temporary — try again in a moment.
The cloud environments service returned a response in an unexpected format (HTTP 200 without a usable environments list). This is usually temporary — try again in a moment.

```

伺服器接受了請求，但用不是環境清單的主體回答：空、不是 JSON 或沒有清單的 JSON。這通常伴隨服務端中斷，並自行清除。根據請求清單的表面，Claude Code 可能會新增前綴，例如 `/remote-env` 對話方塊中的 `couldn't list environments:`。 **該怎麼做：**

- 重試該操作。Claude Code 每次都會再次請求清單
- 如果訊息持續出現，請檢查 [status.claude.com](https://status.claude.com) 以了解活躍的事件

在 v2.1.236 之前，Claude Code 顯示原始 JavaScript TypeError 而不是這些訊息。

### 無法重新連線到您的 Remote Control 工作階段

```
Couldn't reconnect to your Remote Control session. Retry, or start a fresh session without --resume.

```

使用 `claude --resume` 或 `claude --continue` 重新開始會重新連線到該對話中記錄的 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段。此訊息表示重新連線因可能是暫時的原因（例如網路中斷或伺服器錯誤）而失敗，因此 Claude Code 無法確認遠端工作階段是否仍然存在。您的本機工作階段在沒有 Remote Control 的情況下繼續執行。 **該怎麼做：**

- 執行 `/remote-control` 以重試連線
- 使用 `claude --remote-control` 啟動新工作階段以建立新的 Remote Control 工作階段
- 對於其他 Remote Control 啟動訊息，請參閱[Remote Control 疑難排解](https://code.claude.com/docs/zh-TW/remote-control#troubleshooting)

如果伺服器改為報告前一個工作階段已消失，您不會看到此訊息。Claude Code 會在其位置啟動新工作階段或顯示 [`Previous session is unavailable — run /remote-control to start a new one`](https://code.claude.com/docs/zh-TW/remote-control#previous-session-is-unavailable)，取決於[對話的重新連線記錄](https://code.claude.com/docs/zh-TW/remote-control#resume-outcomes)。從 v2.1.227 到 v2.1.231，Claude Code 改為顯示以 `Remote Control could not resume the previous session under the current login` 開頭的訊息，[較早的版本行為也不同](https://code.claude.com/docs/zh-TW/remote-control#reconnect-history)。

### 此機器離線時工作階段已結束

Claude Code 在執行 [`claude remote-control`](https://code.claude.com/docs/zh-TW/remote-control#start-a-remote-control-session) 的終端中顯示此訊息，在您的機器離線足夠長的時間後，伺服器清理了您的機器正在提供的 Remote Control 環境。該環境中的工作階段已結束，您無法恢復它們。計數是已結束的工作階段數。

```
2 sessions ended while this machine was offline — the environment was cleaned up on the server and can't be resumed.

```

**該怎麼做：**

- 當 Claude Code 在此訊息下列出保留的 worktrees 時，從它們中拿起任何未提交的工作
- 執行 `claude remote-control` 以啟動新環境

### 無法共享文字記錄

在您同意從調查提示（例如[工作階段品質調查](https://code.claude.com/docs/zh-TW/data-usage#session-quality-surveys)）共享您的工作階段文字記錄後，Claude Code 將其上傳到 Anthropic，或在第三方提供者上、[Claude apps 閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)工作階段上以及當沒有 Anthropic 認證可用時改為儲存本機封存。此訊息表示共享未完成。

```
Couldn't share the transcript.

```

上傳必須符合 8 MiB 限制。在長工作階段上，Claude Code 逐步丟棄共享的部分，最後一個請求的模型設定優先，然後是結構化對話和子代理文字記錄，並且只在無法傳送任何縮減版本或網路或伺服器錯誤停止上傳時顯示此訊息。當 Claude Code 改為儲存本機封存時，訊息表示它無法寫入封存。 **該怎麼做：**

- 執行 `/feedback` 以傳送文字記錄並描述發生了什麼。如果您的環境中無法使用 `/feedback`，請參閱[報告錯誤](https://code.claude.com/docs/zh-TW/errors#report-an-error)
- 如果其他請求也失敗，請檢查您的網路連線並查看[無法連線到 API](https://code.claude.com/docs/zh-TW/errors#unable-to-connect-to-api)

## 請求錯誤

這些錯誤與您的請求內容有關。大多數來自 API 在拒絕請求後的回應；少數是由 Claude Code 在發送任何請求之前在本地產生的。

### 提示詞過長

對話加上附加檔案超過了模型的上下文視窗。

```
Prompt is too long

```

在互動式工作階段中，Claude Code 將此錯誤顯示為：

```
Context limit reached · /compact or /clear to continue

```

當設定了 [`DISABLE_COMPACT`](https://code.claude.com/docs/zh-TW/env-vars) 時，該行僅命名 `/clear`。較長形式的錯誤，例如下面的壓縮失敗形式，保留 `Prompt is too long ·` 的措辭。在 `-p` 輸出和文字記錄中，文字保持為 `Prompt is too long`。 當您在 [使用者設定](https://code.claude.com/docs/zh-TW/settings-reference#autocompactenabled) 中關閉自動壓縮時，該行也會說明這一點：

```
Context limit reached · /compact or /clear to continue · auto-compact is off · /config to turn it on

```

`/config` 中的 **Auto-compact** 切換會將 `autoCompactEnabled` 寫入使用者設定。該提示僅在 `/config` 變更會生效時出現。例如，當 [`DISABLE_AUTO_COMPACT`](https://code.claude.com/docs/zh-TW/env-vars) 或 [`DISABLE_COMPACT`](https://code.claude.com/docs/zh-TW/env-vars) 關閉自動壓縮時，它不會出現。當更高優先級的範圍（例如專案或受管設定）將 `autoCompactEnabled` 設定為 `false` 時，它也不會出現。在 v2.1.235 之前，該行不包含自動壓縮提示。 Amazon Bedrock 將此狀況報告為 `Input is too long for requested model.`，Claude Code 以相同方式處理。在 v2.1.217 之前，Claude Code 沒有識別 Bedrock 的措辭，因此自動壓縮從未在其上觸發，`/compact` 失敗並出現相同錯誤。 [Claude apps gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway-config#upstream-error-messages) 在雲端上游以提供者自己的錯誤形狀拒絕請求時，將此狀況報告為 `capability_rejected: prompt_too_long`。Claude Code 將該令牌視為與 `Prompt is too long` 相同。在 v2.1.228 之前，Claude Code 沒有識別該令牌，因此自動壓縮沒有在其上觸發。 當自動壓縮在此輪上執行並在基礎錯誤（例如不可用的模型或驗證失敗）上失敗時，該訊息在分隔符後命名該錯誤：

```
Prompt is too long · automatic compaction failed: <the underlying error>

```

首先解決命名的錯誤；在您這樣做之前，`/compact` 會在相同錯誤上失敗。在 v2.1.229 之前，失敗的自動壓縮會顯示 `Prompt is too long` 而不顯示原因。 當自動壓縮在此錯誤上執行時，它通常會總結您最舊的交換並保留最新的。作為最後手段，Claude Code 會以不同方式進行總結：

- 當它無法總結任何完整交換時，Claude Code 會逐字保留您最新的提示，並總結其前面的所有內容。
- 在這種情況下，當對話不以您的提示結尾時，Claude Code 會改為總結整個對話。

Claude Code 在它會轉發的內容不包含模型回覆且您自己的文字少於約 1,000 個令牌（例如在超大貼上後發送的短重試）時跳過此恢復。執行 `/clear` 以重新開始。在 v2.1.269 之前，每當壓縮無法總結完整交換時就會失敗，因此處於該狀態的工作階段在每輪上都會再次遇到此錯誤。 單一交換對話沒有較早的輪次可以總結。當自動壓縮會在其上執行時，Claude Code 會跳過嘗試並解釋填充請求的內容。當 API 在其錯誤中不報告令牌計數時，訊息讀取：

```
Prompt is too long · this conversation is a single exchange and cannot be compacted — the request size comes mostly from system prompt, tool definitions, or attachments.

```

當 API 在其錯誤中報告令牌計數時，Claude Code 將其與自己對對話大小的估計進行比較，以判斷請求的大部分是什麼：對話自己的內容，或 Claude Code 與其一起發送的系統提示、工具定義和附加內容。當對話自己的內容是請求的大部分時，訊息讀取：

```
Prompt is too long · the request is ~<request tokens> tokens (limit <limit>) and this conversation's own content is most of it. A single-exchange conversation cannot be compacted; start with less content (smaller files or pasted text).

```

當請求的大部分在對話之外時，訊息讀取：

```
Prompt is too long · the request is ~<request tokens> tokens (limit <limit>) but this conversation is only ~<conversation tokens> tokens — the rest is system prompt, tool definitions, and attachment content. A single-exchange conversation cannot be compacted; reduce attached files/tools or start with less context.

```

在 v2.1.162 之前，Claude Code 嘗試了壓縮，並在失敗時顯示裸露的 `Prompt is too long`。 **該怎麼辦：**

- 執行 `/compact` 以總結較早的輪次並釋放空間，或執行 `/clear` 以重新開始。如果 `/compact` 回答 `Not enough messages to compact.`，對話是單一交換，沒有較早的內容可以總結，因此空間由該單一提示和 Claude Code 與每個請求一起發送的內容佔用：執行 `/clear` 並使用較少的貼上文字或較小的附加檔案重新發送，或使用下面的步驟減少工具定義和記憶檔案
- 執行 `/context` 以查看視窗消耗內容的分解：系統提示、工具、記憶檔案和訊息
- 使用 `/mcp disable <name>` 禁用您未使用的 MCP 伺服器，以從上下文中移除其工具定義
- 修剪大型 `CLAUDE.md` 記憶檔案，或將指示移至 [路徑範圍規則](https://code.claude.com/docs/zh-TW/memory#path-specific-rules)，這些規則僅在相關時載入
- 子代理繼承父工作階段的每個 MCP 工具定義，這可能在第一輪之前填滿其上下文視窗。在生成子代理之前，禁用您未使用的 MCP 伺服器。
- 自動壓縮預設為開啟，通常可防止此錯誤。如果您在 `/config` 中或使用 [`DISABLE_AUTO_COMPACT`](https://code.claude.com/docs/zh-TW/env-vars) 關閉了它，請將其重新開啟。如果您保持關閉，請在視窗填滿之前自己執行 `/compact`。

請參閱 [探索上下文視窗](https://code.claude.com/docs/zh-TW/context-window) 以互動方式查看上下文如何填滿。

### 上下文超過令牌限制

當對話超過模型的上下文視窗時，`/context` 在其輸出頂部顯示此警告。在您釋放空間之前，請求會失敗並出現 [`Prompt is too long`](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)。互動式工作階段將該錯誤顯示為 `Context limit reached` 行。

```
Context exceeds the 200k-token limit by 94k tokens — run /compact or /clear to continue.

```

當您超過的限制是小於模型上下文視窗的壓縮視窗（例如 1M 上下文模型上的 200K 邊界）時，警告讀取方式不同。壓縮視窗可以位於模型的上下文視窗下方，因此在其之外的請求仍然可以成功。

```
Context is 94k tokens past the 200k-token compaction window — run /compact to reduce usage.

```

當您設定了 [`DISABLE_COMPACT`](https://code.claude.com/docs/zh-TW/env-vars) 時，兩種形式都命名 `/clear` 而不是 `/compact`。 **該怎麼辦：**

- 在多輪對話中，執行 `/compact` 以總結較早的輪次並釋放空間。若要重新開始，請執行 `/clear`
- 有關減少使用量的更多方式，請參閱 [Prompt is too long](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long)

在 v2.1.216 之前，`/context` 顯示使用量超過 100%，沒有警告行解釋這意味著什麼或如何恢復。

### 壓縮期間出錯：對話過長

`/compact` 本身失敗，因為沒有足夠的可用上下文來保存它產生的摘要。

```
Error during compaction: Conversation too long. Press esc twice to go up a few messages and try again.

```

當視窗在自動壓縮觸發時已滿，或當您在看到 [`Prompt is too long`](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long) 後執行 `/compact` 時，可能會發生這種情況。在互動式工作階段中，該錯誤是 `Context limit reached` 行。 **該怎麼辦：**

- 按 Esc 兩次以開啟訊息清單並回退幾輪。這會從上下文中刪除最近的訊息。然後再次執行 `/compact`。
- 如果回退沒有釋放足夠的空間，請執行 `/clear` 以在同一專案中開始新的工作階段。您之前的對話已保存在磁碟上，可以使用 `/resume` 重新開啟。

此訊息和其他 `/compact` 失敗以錯誤樣式顯示。在 v2.1.216 之前，它們以與成功命令輸出相同的暗淡樣式呈現，因此您可能將失敗的壓縮讀取為成功。

### 請求過大

原始請求正文在令牌化之前超過了 API 的 32MB 限制，通常是由於大型貼上內容、工具結果或附加檔案。此限制與 [上下文視窗](https://code.claude.com/docs/zh-TW/errors#prompt-is-too-long) 分開。

```
Request too large (max 32MB). Accumulated images and attachments in the conversation pushed the request over the limit. Run /compact, or double press esc to go back and remove attachments.

```

當請求直接進入 Claude API 且 API 本身拒絕它時，Claude Code 會測量對話並根據恢復是否可行來措辭訊息。通過代理、閘道或雲端提供者，您會收到一般訊息。測量的形式：

- `Request too large (max 32MB; 20.1MB of about 33.4MB is images or documents).`：影像或文件將請求推過限制。Claude Code 會在去除它們後重試。
- `Request too large for the API's 32MB request limit`：訊息本身超過限制，因此訊息說 `compacting cannot make it fit`，Claude Code 不會重試。在 [非互動模式](https://code.claude.com/docs/zh-TW/headless) 中，訊息告訴您減少輸入或改為開始新工作階段。

在 v2.1.212 之前，具有足夠累積影像的對話在每輪上都失敗，出現 `Request too large (max 32MB). Double press esc to go back and try with a smaller file.` 在 v2.1.229 之前，Claude Code 為每次拒絕顯示附加建議，即使壓縮無法幫助。 **該怎麼辦：**

- 如果訊息說 `compacting cannot make it fit`，按 Esc 兩次以回退到添加大型內容的輪次之前，或執行 `/clear` 以重新開始
- 否則，執行 `/compact`，它會刪除累積的影像和附加檔案
- 按路徑參考大型檔案而不是貼上其內容，以便 Claude 可以分塊讀取它們
- 對於影像，請參閱下面的 [Image was too large](https://code.claude.com/docs/zh-TW/errors#image-was-too-large)

### 影像過大

貼上或附加的影像超過了 API 的大小或尺寸限制。

```
Image was too large. Double press esc to go back and try again with a smaller image.
API Error: 400 ... image dimensions exceed max allowed size

```

Claude Code 用文字佔位符替換無法處理的影像並重試，因此後續訊息成功。在 2.1.142 之前的版本上，貼上的影像可能保留在對話中，並在後續每條訊息上重複相同的錯誤。若要在這些版本上恢復，按 Esc 兩次並回退到添加影像的輪次之前。 **該怎麼辦：**

- 在貼上之前調整影像大小。API 接受單個影像最長邊最多 8000 像素的影像，或當許多影像在上下文中時為 2000 像素。
- 拍攝相關區域的更緊密螢幕截圖，而不是整個螢幕

### 無法調整影像大小

Claude Code 無法在將附加影像發送到 API 之前對其進行縮小。

```
Unable to resize image — image processing is unavailable and dimensions could not be read from the file header. Please convert the image to PNG, JPEG, GIF, or WebP.
Unable to resize image — dimensions exceed the 2000x2000px limit and image processing failed. Please resize the image to reduce its pixel dimensions.
Unable to resize image (… raw, … base64). The image exceeds the … API limit and compression failed. Please resize the image manually or use a smaller image.
Unable to resize image — could not verify image dimensions are within the 2000x2000px API limit.
Unable to resize image — it is a CMYK JPEG, which Claude Code cannot decode, and at …px it is over the 2000x2000px limit, so it cannot be sent. Re-save it as an RGB PNG or JPEG and try again.
Unable to resize image — it is an animated WebP whose first frame Claude Code cannot decode, and at …px it is over the 2000x2000px limit, so it cannot be sent. Save its first frame as a PNG or JPEG and try again.
Unable to resize image — its pixels could not be decoded (the file may be damaged, or use an encoding Claude Code cannot read), and it is over the … API limit (… raw, … base64), so it cannot be sent. Re-save it as a PNG or JPEG and try again.

```

Claude Code 通常會自動調整大型影像的大小。這些錯誤意味著無法解碼或調整影像大小以適應 API 限制。 **該怎麼辦：**

- 如果訊息要求您轉換影像，請將其轉換為 PNG、JPEG、GIF 或 WebP，然後再次附加。Claude Code 可以從檔案標頭驗證這些格式的尺寸，而無需解碼影像。
- 如果訊息報告尺寸或大小限制，請在附加之前將影像調整大小或重新壓縮到該限制以下。
- 如果訊息命名原因，例如 CMYK JPEG、動畫 WebP 或可能損壞的檔案，請以訊息建議的格式重新保存影像並再次附加。

### PDF 錯誤

您附加的 PDF 無法處理。訊息在此處以非互動形式顯示；在互動式工作階段中，它們會提示您按 Esc 兩次並重試。

```
PDF too large (max 100 pages, 20MB). Try reading the file a different way (e.g., extract text with pdftotext).
PDF is password protected. Try using a CLI tool to extract or convert the PDF.
The PDF file was not valid. Try converting it to text first (e.g., pdftotext).

```

**該怎麼辦：**

- 對於超大 PDF，要求 Claude 使用 Read 工具讀取頁面範圍而不是附加整個檔案，或使用 `pdftotext` 之類的工具提取文字並按路徑參考輸出檔案
- 對於受保護或無效的 PDF，移除密碼或從其來源應用程式重新匯出檔案，然後重試

### 不允許額外輸入

Claude Code 和 API 之間的代理或 LLM 閘道去除了 `anthropic-beta` 請求標頭，因此 API 拒絕了依賴它的欄位。

```
API Error: 400 ... Extra inputs are not permitted ... context_management
API Error: 400 ... Unexpected value(s) for the `anthropic-beta` header

```

Claude Code 發送測試版專用欄位（例如 `context_management` 和 `effort`）以及啟用它們的 `anthropic-beta` 標頭。當閘道轉發正文但刪除標頭時，API 會看到它不識別的欄位。 **該怎麼辦：**

- 配置您的閘道以轉發 `anthropic-beta` 標頭。請參閱 [feature pass-through](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#feature-pass-through) 以了解閘道必須轉發的內容。
- 作為備用方案，在啟動前設定 [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`](https://code.claude.com/docs/zh-TW/env-vars)。[Disable pre-release capabilities](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#disable-pre-release-capabilities) 涵蓋確切範圍。

### 工具輸入架構無效

請求中的工具聲明了 `input_schema`，該架構未通過 API 的 JSON Schema 驗證，因此 API 拒絕了整個請求。`tools.` 後面的數字是失敗工具在請求的工具清單中的位置，而不是您可以查找的名稱。

```
API Error: 400 ... tools.N.custom.input_schema: JSON schema is invalid
API Error: 400 ... tools.N.custom.input_schema.properties: Property keys should match pattern '^[a-zA-Z0-9_.-]{1,64}$'

```

第一種形式意味著架構不是有效的 JSON Schema draft 2020-12。第二種意味著頂級屬性名稱與訊息引用的模式不匹配。 Claude Code [在載入伺服器的工具時排除輸入架構會失敗此驗證的 MCP 工具](https://code.claude.com/docs/zh-TW/mcp#tools-with-invalid-input-schemas)，因此請求通常永遠不會包含一個。 在 [標誌擷取關閉的部署](https://code.claude.com/docs/zh-TW/env-vars#features-that-need-feature-flag-fetching) 上，或在標誌從未到達的機器上，Claude Code 在伺服器的日誌中記錄哪個工具會被拒絕，但仍然發送它，因此此錯誤仍然可能發生。 該錯誤也可能發生在工具的架構在 `$schema` 中聲明 JSON Schema 方言而不是 draft 2020-12 的工具上。Claude Code 不會根據 JSON Schema 元架構檢查這些架構，儘管頂級屬性名稱檢查仍然適用。 在 v2.1.216 之前，沒有部署執行排除檢查。 **該怎麼辦：**

- 如果您的 Claude Code 版本早於 v2.1.216，請執行 `claude update`。
- 移除或 [禁用](https://code.claude.com/docs/zh-TW/mcp#disable-a-server-without-removing-it) 聲明無效架構的 MCP 伺服器。該錯誤僅按位置命名工具。在 v2.1.216 或更新版本上，檢查每個伺服器的日誌以查找命名工具的行，其輸入架構會被拒絕。如果沒有日誌命名一個，請逐個禁用伺服器。
- 如果您維護伺服器，請修復工具的 `input_schema`。架構必須是有效的 JSON Schema，頂級屬性名稱必須為 1 到 64 個字元長，並且只能使用 ASCII 字母和數字、`_`、`.` 和 `-`。請參閱 [Tools with invalid input schemas](https://code.claude.com/docs/zh-TW/mcp#tools-with-invalid-input-schemas)。

### 選定的模型有問題

配置的模型名稱未被識別，或您的帳戶缺乏對其的存取權限。從 v2.1.160 開始，尾部提示（此處以其互動形式顯示）因表面而異。

```
There's an issue with the selected model (claude-...). It may not exist or you may not have access to it. Run /model to pick a different model.

```

**該怎麼辦：**

- **互動式 CLI** ：執行 `/model` 以從您帳戶可用的模型中選擇。
- **非互動模式 (`-p`)**：使用有效的別名或 ID 傳遞 `--model`，或設定 [`ANTHROPIC_MODEL`](https://code.claude.com/docs/zh-TW/env-vars)。錯誤文字在此表面上顯示 `Run --model`。
- **Agent SDK** ：錯誤文字省略提示，因為模型是以程式設計方式設定的。在 TypeScript 中的 [`Options` 上設定 `model`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options)，或在 Python 中設定 [`ClaudeAgentOptions(model=...)`](https://code.claude.com/docs/zh-TW/agent-sdk/python#claudeagentoptions)，並處理結構化 `model_not_found` 錯誤以顯示您自己的重試或模型選擇器。
- 使用別名（例如 `sonnet` 或 `opus`）而不是完整版本化 ID。別名解析為維護的預設值，因此它們不會過時。請參閱 [Model configuration](https://code.claude.com/docs/zh-TW/model-config)。
- 如果錯誤的模型在 CLI 中不斷出現，則在某處設定了過時的 ID。按 [優先順序](https://code.claude.com/docs/zh-TW/model-config#setting-your-model) 檢查您可以設定模型的位置，並移除過時的值。
- 新推出的模型可能在 Anthropic API 上可用，但在 Amazon Bedrock、Google Cloud 的 Agent Platform 或 Microsoft Foundry 上可用之前。如果您在其中一個提供者上固定了新模型 ID 並看到此錯誤，請檢查您提供者的模型目錄以了解您區域的可用性，並保持固定先前版本，直到新版本出現。
- Claude Code 將過期的 claude.ai 登入報告為 [Login expired](https://code.claude.com/docs/zh-TW/errors#login-expired)，而不是此錯誤。在 v2.1.206 之前，無法再刷新的過期登入對每個模型失敗，出現此錯誤；如果您在較舊版本上看到這種情況，請執行 `/login`。
- 對於 Google Cloud 的 Agent Platform 部署，請參閱 [Google Cloud 的 Agent Platform 故障排除](https://code.claude.com/docs/zh-TW/google-vertex-ai#troubleshooting)。

### 模型不是公認的模型 ID

您傳遞給模型切換的模型字串不是模型別名、此 Claude Code 版本知道的模型 ID，也不是以 `claude-` 開頭的 ID。常見原因是 ID 中的拼寫錯誤、顯示名稱（例如 `Sonnet 5`，其中需要 ID `claude-sonnet-5`），或只有較新 Claude Code 版本識別的別名。Claude Code 立即拒絕切換。在 v2.1.200 之前，Claude Code 保存字串並在下一個請求上失敗，出現 [There’s an issue with the selected model](https://code.claude.com/docs/zh-TW/errors#theres-an-issue-with-the-selected-model)。

```
Model "claud-sonnet-5" is not a recognized model id. Did you mean 'claude-sonnet-5'?

```

尾部提示命名最接近的匹配別名或模型 ID。當沒有足夠接近的內容時，它讀取 `Run /model to see available models.`。 Claude Code 在請求切換的時刻在本地產生此錯誤，在任何 API 請求之前。它適用於通過 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/typescript) `setModel()` 方法設定模型、由執行 Claude Code CLI 的應用程式（例如 [Desktop app](https://code.claude.com/docs/zh-TW/desktop)）設定，或當您從通過 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 連接的裝置選擇模型時。在 v2.1.260 之前，檢查不涵蓋 Remote Control 選擇，因此 Claude Code 應用了選擇，下一個請求失敗，出現 [There’s an issue with the selected model](https://code.claude.com/docs/zh-TW/errors#theres-an-issue-with-the-selected-model)。 **該怎麼辦：**

- 執行 `/model` 不帶引數以開啟選擇器並從您帳戶可用的模型中選擇，然後傳遞那裡顯示的別名或 ID
- 如果您使用了較新 Claude Code 版本支援的別名，請執行 `claude update`。以 `claude-` 開頭的完整 ID 即使模型比您的 Claude Code 版本更新，也會通過此本地檢查。伺服器仍然可能需要該模型的最低版本；請參閱 [Claude Code does not support this model](https://code.claude.com/docs/zh-TW/errors#claude-code-does-not-support-this-model)。
- v2.1.200 之前保存的模型不會被此檢查修復。如果過時的值不斷出現，請從 [Setting your model](https://code.claude.com/docs/zh-TW/model-config#setting-your-model) 下列出的位置移除它。
- 檢查僅在 Anthropic API 上執行。在任何其他提供者或閘道上，包括自訂 `ANTHROPIC_BASE_URL`，提供者定義模型名稱，因此 Claude Code 接受任何字串並將其傳遞。Claude Code 仍然可以在請求時寫入 [unrecognized-model diagnostic line](https://code.claude.com/docs/zh-TW/errors#unrecognized-model-id-on-a-request)，在每個提供者上。

### 找不到模型

您使用 `/model <name>` 選擇了模型，Claude Code 無法確認存在具有該名稱的模型。當名稱不是 [model alias](https://code.claude.com/docs/zh-TW/model-config#model-aliases) 或 Claude Code 在本地接受的另一種拼寫時，`/model` 使用最小 API 請求驗證它，此錯誤通常是您的 API 端點的答案。無法成為模型 ID 的名稱（例如包含空格的名稱）會收到相同訊息。

```
Model 'claude-opus-9' not found

```

在具有提供者特定模型 ID 的提供者上，訊息可能會添加 `Try '...' instead` 建議，該建議命名您提供者的備用模型 ID。 **該怎麼辦：**

- 執行 `/model` 不帶引數並從您帳戶可用的模型中選擇，或使用 [model alias](https://code.claude.com/docs/zh-TW/model-config#model-aliases)（例如 `sonnet`），它解析為維護的預設值
- 如果您輸入了完整 ID，請根據您提供者的模型目錄檢查它。新推出的模型可能在 Anthropic API 上可用，但您的提供者或區域尚未提供。
- 在 v2.1.265 之前，`/model` 也以此錯誤拒絕了 `opusplan[1m]` 別名拼寫。在這些版本上，更新 Claude Code，或在 [settings](https://code.claude.com/docs/zh-TW/model-config#setting-your-model) 中或使用 `--model` 設定模型。

### Claude Opus 不適用於 Claude Pro 方案

您的有效訂閱方案不包括您選擇的模型。

```
Claude Opus is not available with the Claude Pro plan. If you have updated your subscription plan recently, run /logout and /login for the plan to take effect.

```

**該怎麼辦：**

- 執行 `/model` 並選擇您的方案包括的模型
- 如果您最近升級了方案但仍然看到這個，請執行 `/logout` 然後 `/login`。儲存的令牌反映您登入時的方案，因此在現有工作階段中在網路上升級不會生效，直到您重新驗證。
- 請參閱 [claude.com/pricing](https://claude.com/pricing) 以了解每個方案包括哪些模型

### Claude Code 不支援此模型

API 因為您的 Claude Code 版本低於所需最低版本而拒絕了請求，出現 400。您選擇的模型需要較新版本（伺服器按模型檢查），或您的組織政策需要一個。400 帶有錯誤代碼 `claude_code_version_too_old`，訊息說明適用的最低版本。

```
API Error: 400 Claude Code 2.1.219 does not support this model; version 2.1.255 or newer is required. Run 'claude update', or update the Claude desktop app, then try again.

```

組織政策措辭讀取：

```
API Error: 400 Claude Code 2.1.240 is older than the minimum version required by your organization's policy. Run 'claude update', or update the Claude desktop app, to continue.

```

**該怎麼辦：**

- 執行 `claude update`，或更新 Claude 桌面應用程式，然後開始新的工作階段
- 對於按模型措辭，您可以通過使用 `/model` 切換到另一個模型來在目前工作階段中繼續工作
- 對於組織政策措辭，在繼續之前更新

### 模型受您的組織設定限制

您的組織管理員已在 claude.ai 管理控制台中禁用此模型，或它被受管設定中的 [`availableModels`](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection) 允許清單排除。當受限制的模型使用 `--model`、`ANTHROPIC_MODEL` 或 `model` 設定設定時，Claude Code 替換允許的模型並繼續。為受限制的模型輸入 `/model <name>` 被拒絕，出現 `Run /model to choose a different model.`，工作階段保持其目前模型。替換通知可能也會在工作階段中途出現，在管理員在 claude.ai 管理控制台中禁用工作階段正在執行的模型之後。

```
Model "claude-opus-4-8" is restricted by your organization's settings. Using claude-sonnet-4-6 instead.

```

以代理、技能或命令名稱為前綴的通知意味著限制適用於該 [子代理的請求模型](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)：子代理在替換模型上執行，您的工作階段模型保持不變。在 v2.1.223 之前，Claude Code 僅對使用 Agent 工具啟動的子代理顯示通知。 Claude Code 將模型系列別名（`opus`、`sonnet`、`haiku` 或 `fable` 之一）視為對該系列的請求，而不是對其最新版本的請求。在 Anthropic API 和 [Claude Platform on AWS](https://code.claude.com/docs/zh-TW/claude-platform-on-aws) 上，受限制的系列別名解析為您的組織和 `availableModels` 允許清單允許的系列的最新版本，替換通知命名該版本。Claude Code 僅在系列的每個版本都受限制時拒絕 `/model <alias>`。在 v2.1.205 之前，系列別名基於其最新版本單獨替換或拒絕，即使同一系列的較舊版本被允許。 **該怎麼辦：**

- 執行 `/model` 以從您的組織允許的模型中選擇。受限制的模型在選擇器中隱藏。
- 如果受限制的模型在 `--model`、`ANTHROPIC_MODEL`、設定檔案的 `model` 欄位或 [subagent](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)、技能或命令的 `model` frontmatter 中設定，請移除或更新該值，以便通知不會再次出現
- 如果您需要存取受限制的模型，請要求您的組織管理員啟用它。請參閱 [Organization model restrictions](https://code.claude.com/docs/zh-TW/model-config#organization-model-restrictions)。

### 模型切換被 PreModelSwitch hook 阻止

[PreModelSwitch hook](https://code.claude.com/docs/zh-TW/hooks#premodelswitch) 沒有批准您或用戶端請求的模型切換，因此工作階段保持其目前模型。當切換來自 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 主機或 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 而不是您輸入的命令時，訊息讀取 `Model switch blocked by a PreModelSwitch hook` 而不命名目標模型。

```
Model switch to Opus 4.6 was blocked by a PreModelSwitch hook: Opus 4.6 is retired for this project. Use a newer model.

```

冒號後的原因說明拒絕切換的原因：

- **hook 寫入的原因** ：PreModelSwitch hook 在 [拒絕切換或要求確認](https://code.claude.com/docs/zh-TW/hooks#premodelswitch-decision-control) 時提供了該原因。解決它要求的內容，或選擇您的 hook 允許的模型。
- **`PreModelSwitch hook <name> did not respond before its timeout`**：在其[timeout](https://code.claude.com/docs/zh-TW/hooks#timeouts) 之前沒有回答的 hook 會阻止切換。修復掛起的命令或提高該 hook 的 `timeout`，然後再次切換。
- **`confirmation required, and this session cannot ask`**：hook 回答`ask` 而沒有原因，控制請求無法顯示確認提示。[`-p` 執行](https://code.claude.com/docs/zh-TW/headless) 中的控制請求以原因後的 `(run /model interactively to confirm)` 報告相同狀況。從互動式工作階段進行切換，或更改 hook 對此模型的決定。
- **`so organization-managed PreModelSwitch hooks could not be checked`**：Claude Code 無法判斷您的組織的[managed plugins](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 提供哪些 PreModelSwitch hook，例如因為受管外掛程式無法載入。其中一個 hook 可能會阻止切換，因此 Claude Code 拒絕而不是應用未檢查的切換。原因的開始命名失敗的內容。Claude Code 在每次切換嘗試時重新檢查，因此已清除的失敗停止阻止；如果它繼續失敗，執行 `claude --debug` 並再次切換以捕獲詳細資訊，然後修復外掛程式或要求您的管理員修復它。
- **`a PreModelSwitch hook failed before answering`**或**`PreModelSwitch hooks were cancelled (the control stream closed) before answering`**：hook 執行在沒有判決的情況下結束，Claude Code 不將其視為批准。執行`claude --debug` 以查看失敗的內容，然後再次切換。

在 v2.1.260 之前，受管外掛程式拒絕讀取 `plugin hooks could not be loaded, so PreModelSwitch hooks could not be checked; see the debug log`。Claude Code 重試外掛程式載入一次，然後在工作階段中拒絕後續切換，即使您的組織沒有受管外掛程式。在這些版本上重新啟動工作階段以再次執行外掛程式載入。

### 無法將其保存為您的預設值

您選擇了一個模型以保存為您的預設值，例如使用 `/model <name>` 或 `/model` 選擇器中的 Enter，Claude Code 無法將選擇寫入您的使用者設定檔案 `~/.claude/settings.json`。切換本身已應用，因此目前工作階段在您選擇的模型上執行，但您的預設值保持不變，下一個工作階段在舊值上開始。

```
Set model to Fable 5.1 for this session only · couldn't save it as your default: ~/.claude/settings.json can't be written (EROFS)

```

檔案路徑後的原因說明失敗的內容：

- **`can't be written (<code>)`**：寫入失敗，出現括號中的作業系統錯誤代碼，例如當檔案或它連結到的檔案位於拒絕寫入的檔案系統上時的`EROFS` 。使檔案可寫入並再次切換。如果另一個工具產生檔案，請在該工具中設定 `model` 鍵；請參閱 [A change you made in Claude Code is lost in new sessions](https://code.claude.com/docs/zh-TW/settings#a-change-you-made-in-claude-code-is-lost-in-new-sessions)。
- **`isn't valid JSON`**：磁碟上的檔案不解析，Claude Code 保持不動而不是覆蓋它無法讀回的內容。修復語法錯誤，然後再次切換；請參閱[Fix a broken settings file](https://code.claude.com/docs/zh-TW/settings#fix-a-broken-settings-file)。

以 `couldn't confirm it was saved as your default (~/.claude/settings.json is still being written)` 結尾的通知意味著寫入在三秒後未完成。它在背景中繼續，因此預設值可能仍然被保存；檢查您的下一個工作階段開始的模型，或再次執行 `/model <name>`。 在 v2.1.265 之前，通知說模型被 `saved as your default for new sessions`，即使寫入失敗。

### 此模型不支援 thinking.type.enabled

您的 Claude Code 版本早於所選模型的最低版本。CLI 發送了模型不再接受的思考配置。

```
API Error: 400 ... "thinking.type.enabled" is not supported for this model. Use "thinking.type.adaptive" and "output_config.effort" to control thinking behavior.

```

**該怎麼辦：**

- 執行 `claude update` 並重新啟動 Claude Code。Opus 4.7 需要 v2.1.111 或更新版本。Opus 4.8 需要 v2.1.154 或更新版本。Sonnet 5 需要 v2.1.197 或更新版本。Opus 5 需要 v2.1.219 或更新版本
- 如果您無法升級，執行 `/model` 並改為選擇 Opus 4.6 或 Sonnet 4.6
- 如果您在 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 中遇到這個，請改為升級 SDK 套件。Opus 4.8 需要 TypeScript SDK v0.3.154 或更新版本和 Python SDK v0.2.88 或更新版本。Sonnet 5 需要 TypeScript SDK v0.3.197 或更新版本。Opus 5 需要 TypeScript SDK v0.3.219 或更新版本

### 關閉思考時努力不可用

您關閉了 [extended thinking](https://code.claude.com/docs/zh-TW/model-config#extended-thinking) 並以 [effort level](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level) 高於 `high` 執行。模型不接受該組合，因此 API 拒絕了請求。

```
API Error: Effort 'xhigh' isn't available with thinking turned off on this model · run /effort high to continue, or turn thinking back on (unset MAX_THINKING_TOKENS=0)

```

**該怎麼辦：**

- [降低努力級別](https://code.claude.com/docs/zh-TW/model-config#set-the-effort-level) 至 `high` 或以下。
- 打開思考，例如通過取消設定 [`MAX_THINKING_TOKENS`](https://code.claude.com/docs/zh-TW/env-vars) 或從您的設定中移除 [`"alwaysThinkingEnabled": false`](https://code.claude.com/docs/zh-TW/settings-reference#alwaysthinkingenabled)。

在 v2.1.242 之前，Claude Code 顯示 API 自己的訊息：`API Error: 400 output_config.effort 'xhigh' is not supported when thinking is disabled on this model. Use effort 'high' or below, or enable thinking.` 在 v2.1.251 之前，Claude Code 在您設定的努力級別發送請求，因此 Opus 5 拒絕了關閉思考時高於 `high` 的每個請求。Claude Code 現在改為向它知道拒絕該組合的模型（例如 Opus 5）發送努力 `high`，因此在 v2.1.251 或更新版本上，此錯誤僅從 Claude Code 不知道拒絕它的模型到達您。

### 思考預算超過輸出限制

配置的擴展思考預算超過最大回應長度，因此實際答案沒有剩餘空間。

```
API Error: 400 ... max_tokens must be greater than thinking.budget_tokens

```

Claude Code 在 Anthropic API 上自動調整這些值。當 [`MAX_THINKING_TOKENS`](https://code.claude.com/docs/zh-TW/env-vars) 設定高於提供者的輸出限制，或當計畫模式提高思考預算時，您通常在 Amazon Bedrock 或 Google Cloud 的 Agent Platform 上看到此錯誤。 **該怎麼辦：**

- 降低 `MAX_THINKING_TOKENS`，或提高 [`CLAUDE_CODE_MAX_OUTPUT_TOKENS`](https://code.claude.com/docs/zh-TW/env-vars) 高於思考預算
- 請參閱 [Extended thinking](https://code.claude.com/docs/zh-TW/model-config#extended-thinking) 以了解預算如何與輸出長度互動

### 工具使用或思考區塊不匹配

對話歷史記錄到達 API 時處於不一致狀態，通常在工具呼叫被中斷或輪次在串流中途被編輯後。

```
API Error: 400 due to tool use concurrency issues. Run /rewind to recover the conversation.
API Error: 400 ... unexpected `tool_use_id` found in `tool_result` blocks
API Error: 400 ... thinking blocks ... cannot be modified

```

所有三個變體都意味著相同的事情：歷史記錄中 `tool_use`、`tool_result` 和 `thinking` 區塊的序列不再與 API 期望的相符。 **該怎麼辦：**

- 如果您使用 Opus 4.7 或 Opus 4.8，請先執行 `claude update`。v2.1.156 之前的版本可以在正常工具使用期間觸發此錯誤，`/rewind` 不會清除它。
- 執行 `/rewind`，或按 Esc 兩次，以回退到損壞輪次之前的檢查點並從那裡繼續。請參閱 [Checkpointing](https://code.claude.com/docs/zh-TW/checkpointing) 以了解檢查點如何建立和恢復。

### 移除了不支援的工具內容

當 Claude Code 直接連接到 Anthropic API 並載入或預覽已保存的工作階段時，它會移除 Anthropic API 不接受的工具內容，並在兩個思考區塊之間移除的內容所在的位置留下此行：

```
[Unsupported tool content removed]

```

當 API 格式以外的內容回答時，此類內容到達工作階段檔案，通常是通過 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 設定的第三方代理，它轉譯另一個提供者的工具呼叫。Claude Code 僅在工作階段直接連接到 Anthropic API 時移除它，並在工作階段通過代理或在另一個提供者上執行時按原樣載入已保存的歷史記錄。在 v2.1.246 之前，Claude Code 將工具使用及其結果發送回 API，已恢復工作階段的每輪都失敗，出現 400 錯誤，例如 `messages.1.content.0.server_tool_use.name: Input should be 'web_search', 'web_fetch', ...`。 **該怎麼辦：**

- 當您看到佔位符行時，無需執行任何操作。工作階段在沒有移除內容的情況下繼續。
- 如果已恢復工作階段的每輪都失敗，出現 400 錯誤，請執行 `claude update` 並再次恢復工作階段。v2.1.246 之前的版本不會移除內容。

### 使用政策拒絕

API 拒絕回應，因為對話中的內容觸發了 [Usage Policy](https://www.anthropic.com/legal/aup) 檢查。訊息包括您可以引用給支援的請求 ID，如果您認為拒絕不正確。

```
API Error: Opus 4.6 can't help with this. Start a new session to continue.

Send feedback with /feedback or learn more: https://www.anthropic.com/legal/aup

```

訊息命名拒絕的模型，或當沒有記錄模型時命名 `Claude`。 檢查評估完整對話，而不僅是您的最新提示，因此在同一工作階段中發送新訊息通常會重新觸發相同的拒絕。使用 `--continue` 或 `--resume` 退出並重新開啟工作階段後也是如此，因為磁碟上的文字記錄仍然包含觸發內容。在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 和 [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 上，此訊息也涵蓋模型的安全措施標記為網路安全主題的請求。請參閱 [Safety measures flagged a cybersecurity topic](https://code.claude.com/docs/zh-TW/errors#safety-measures-flagged-a-cybersecurity-topic)。 在 v2.1.219 之前，訊息讀取 `Claude Code is unable to respond to this request, which appears to violate our Usage Policy (https://www.anthropic.com/legal/aup). Please double press esc to edit your last message or start a new session for Claude Code to assist with a different task.` **該怎麼辦：**

- 按 Esc 兩次或執行 `/rewind` 以回退到觸發拒絕的輪次之前的檢查點，然後重新措辭或採取不同的方法。請參閱 [Checkpointing](https://code.claude.com/docs/zh-TW/checkpointing)。
- 如果您無法識別哪個輪次導致了它，執行 `/clear` 以在同一專案中開始新的對話。您之前的對話保存在磁碟上，並在 `/resume` 中保持可用。
- 在 [非互動模式](https://code.claude.com/docs/zh-TW/headless) (`-p`) 中，其中倒帶不可用，使用重新措辭的提示在沒有 `--continue` 的新工作階段中重試。政策檢查因模型而異，因此使用 `--model` 切換到不同的模型也可能在某些情況下解決拒絕。

### 安全措施標記了網路安全主題

模型的安全措施將對話中的內容標記為網路安全主題。訊息命名標記請求的模型：

```
API Error: Opus 4.8's safeguards flagged this message. Our intentionally broad safeguards allow us to deliver more capabilities faster, but can sometimes flag legitimate cybersecurity work. Apply to the Cyber Verification Program to reduce these interruptions. Send feedback with /feedback or learn more: https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude

```

訊息連結到 [Cyber Verification Program](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude)，它為合法網路安全工作授予存取權限。 在 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)、[Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 和 [Microsoft Foundry](https://code.claude.com/docs/zh-TW/microsoft-foundry) 上，網路安全標記會改為產生 [Usage Policy refusal](https://code.claude.com/docs/zh-TW/errors#usage-policy-refusal) 訊息。 防護本身是伺服器端的，早於 v2.1.203；自那時以來的用戶端版本僅更改了訊息的措辭。 從 v2.1.203 到 v2.1.218，訊息讀取 `<model> has safety measures that flagged this message for a cybersecurity topic. To learn about the Cyber Verification Program and apply for access, visit our help center:` 後跟相同的說明中心連結，互動式工作階段附加 `If you were not engaging in a cybersecurity topic, please send feedback via /feedback.` 在 v2.1.203 之前，它讀取 `<model>'s safeguards flagged this message for a cybersecurity topic. If your work requires this access, you can apply for an exemption:` 後跟豁免表單連結。 **該怎麼辦：**

- 如果您的工作需要此內容，請通過 [Cyber Verification Program](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude) 申請存取權限
- 如果您的請求不是關於網路安全主題，執行 `/feedback` 以報告誤報
- 若要在同一工作階段中繼續工作，按 Esc 兩次或執行 `/rewind` 以回退到觸發標記的輪次之前的檢查點，然後採取不同的方法。請參閱 [Checkpointing](https://code.claude.com/docs/zh-TW/checkpointing)。

## 安裝錯誤

這些錯誤會在安裝或更新 Claude Code 時出現，來自 [安裝指令碼](https://code.claude.com/docs/zh-TW/setup#install-claude-code)、`claude install` 或 `claude update`。如需 `command not found`、PATH、權限和設定期間的 TLS 問題，請參閱 [疑難排解安裝和登入](https://code.claude.com/docs/zh-TW/troubleshoot-install)。

### 安裝在完成前被中止

安裝指令碼會在 `claude install` 步驟被信號終止時報告。在 Linux 上，結束代碼 137 表示程序收到 SIGKILL，在低記憶體主機上通常是核心記憶體不足 (OOM) 殺手。指令碼會列印此說明並以代碼 137 結束：

```
Installation was killed before it could finish (exit code 137). This usually means the system ran out of memory.
Claude Code needs roughly 512MB of free memory to install. Free up memory, then run this script again.

```

對於任何其他致命信號，以及 macOS 上的結束代碼 137，指令碼會列印 `Installation was killed before it could finish (exit code <N>)`，其中包含實際結束代碼，並省略記憶體不足的說明。該訊息來自 macOS 和 Linux 使用的安裝指令碼，也涵蓋 WSL 內的安裝；原生 Windows 安裝指令碼永遠不會列印它。在 v2.1.200 之前，指令碼只以 shell 的裸 `Killed` 行結束。 **該怎麼做：**

- 停止其他程序以釋放記憶體，然後重新執行安裝程式
- 新增交換空間或移至更大的執行個體。請參閱 [在低記憶體 Linux 伺服器上安裝被中止](https://code.claude.com/docs/zh-TW/troubleshoot-install#install-killed-on-low-memory-linux-servers) 以取得交換檔案命令。

### 下載更新時連線中斷

在 `claude install`、`claude update` 或 [自動更新程式](https://code.claude.com/docs/zh-TW/setup#auto-updates) 擷取 Claude Code 二進位檔案時，與下載伺服器的連線已關閉，且重試未能復原。Claude Code 會在連線中斷、傳輸停滯或下載的檔案未通過總和檢查時重試下載，總共最多三次嘗試。已完成的 HTTP 錯誤（例如 404）不會重試，因為伺服器已經回應。在 v2.1.202 之前，單一連線中斷會立即導致下載失敗，並顯示裸錯誤 `aborted`，而不是重試。

```
The connection dropped while downloading the update (attempt 3/3: aborted). Check your network — proxies sometimes cut off large downloads.

```

括號中的文字命名失敗的嘗試和基礎網路錯誤。`claude update` 在 stderr 上以 `Error: Failed to install native update` 開頭該訊息。 保持連線但未在 10 分鐘內完成的下載會失敗，並顯示 `Download timed out: exceeded the total deadline`。Claude Code 不會重試逾時的下載，因為連線太慢而無法在期限內完成，在立即重試時也不會完成。以下步驟適用於兩個訊息。 通常的原因是代理或閘道在傳輸完成前關閉長傳輸。Claude Code 二進位檔案是大型下載，因此永遠不會影響正常 API 流量的代理連線限制仍然可能中斷它。 **該怎麼做：**

- 再次執行 `claude update`。在網路狀況良好的情況下，下載通常在下次執行時成功。對於逾時訊息，請從更快或限制較少的網路重新執行。
- 如果您的網路需要代理，請在執行安裝程式或 `claude update` 之前設定 `HTTPS_PROXY`。請參閱 [檢查網路連線](https://code.claude.com/docs/zh-TW/troubleshoot-install#check-network-connectivity)。
- 如果公司代理持續關閉傳輸，請要求您的網路團隊允許從 `downloads.claude.ai` 進行完整下載。請參閱 [網路存取需求](https://code.claude.com/docs/zh-TW/network-config#network-access-requirements)。
- 從您的 shell 執行 `claude doctor` 以進行安裝診斷

## 命令列錯誤

這些錯誤來自 `claude` 命令列及其子命令、您在提示符處提交的命令名稱，以及 `/security-review` 等命令，這些命令在執行提示之前透過執行 shell 命令來收集上下文。它們也來自 `/tui`，它會重新啟動 CLI。

### —bg 和 —print 之間的衝突

此訊息需要 Claude Code v2.1.198 或更新版本。您在同一個 `claude` 呼叫中結合了 `--bg` 與 `-p` 或 `--print`。`--bg` 啟動一個[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view#from-your-shell)，您稍後可以使用 `claude agents` 附加到該工作階段，而 `--print` 以[非互動方式](https://code.claude.com/docs/zh-TW/headless)執行，永遠不會啟動 `claude agents` 附加到的互動工作階段。在 v2.1.198 之前，此組合會無聲地建立一個永遠無法附加的背景工作。

```
--bg and --print conflict: --print never starts the interactive session that `claude agents` attaches to, so the job would be unattachable. The prompt is the positional — drop --print: `claude --bg '<task>'`.

```

**該怎麼做：**

- 移除 `-p` 或 `--print`。`--bg` 將提示作為其位置引數，所以 `claude --bg "<task>"` 是完整命令。請參閱[從您的 shell 分派新代理](https://code.claude.com/docs/zh-TW/agent-view#from-your-shell)。
- 若要以非互動方式執行提示並列印結果而不是建立背景工作階段，請移除 `--bg` 並執行 `claude -p "<task>"`

### 無效的 —agents 設定

您傳遞給 `--agents` 的值無效，所以 `claude` 以代碼 1 結束而不是啟動工作階段。當您傳遞 `--safe-mode`、`--resume` 或 `--continue`，或設定 [`CLAUDE_CODE_SAFE_MODE`](https://code.claude.com/docs/zh-TW/env-vars#variables) 時，Claude Code 不會檢查該值並啟動工作階段。在 v2.1.242 之前，Claude Code 仍然啟動工作階段並省略了它無法載入的定義。

```
Error: Invalid --agents configuration:
<what failed>

```

第一行之後的內容取決於值如何失敗。Claude Code 按順序執行這些檢查，並在第一個失敗的檢查處停止。如果您的值有兩種問題，您只有在修復第一個問題後才會看到第二個：

1. 當值不能解析為 JSON 時，Claude Code 列印一行 `invalid JSON:` 並帶有 JSON 解析器自己的訊息
1. 當它解析但代理定義不符合 [CLI 定義的子代理](https://code.claude.com/docs/zh-TW/sub-agents#choose-the-subagent-scope) 的架構時，Claude Code 每個問題列印一行
1. 當代理名稱以 `-` 開頭時，Claude Code 列印 `<name>: agent names must not start with '-'`

當有超過 20 行問題時，Claude Code 列印前 20 行並用 `…and N more` 替換其餘部分。 **該怎麼做：**

- 修復訊息列出的每個問題，然後再次執行命令。請參閱 [CLI 定義的子代理採用的欄位](https://code.claude.com/docs/zh-TW/sub-agents#choose-the-subagent-scope)。

### 無法從 —restricted 工作階段建立雲端工作階段

當您使用 [`--restricted`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 啟動工作階段時，Claude Code 拒絕從中建立[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud)，因為新工作階段將在受限制的程序之外執行，不會強制執行受限制的模式。Claude Code 在用戶端拒絕，在聯絡伺服器之前，所以不會建立雲端工作階段：

```
Cloud sessions cannot be created from a --restricted session: they would not enforce it.

```

**該怎麼做：**

- 在受限制的工作階段中本地執行任務
- 如果您控制工作階段的啟動方式，啟動一個沒有 `--restricted` 的新 `claude` 工作階段，並從那裡建立雲端工作階段

在 v2.1.248 之前，Claude Code 沒有 `--restricted` 旗標；較早的版本以未知選項錯誤拒絕該旗標。

### 您的組織政策已停用雲端工作階段

您的組織的 `allow_remote_sessions` 政策已關閉，所以[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)和使用它們的命令不可用：

```
Cloud sessions are disabled by your organization's policy. Contact your organization admin to enable them.

```

當您[從終端建立雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#from-terminal-to-cloud)時會出現此訊息，當您提交需要雲端工作階段的命令時，例如 `/teleport`、`/remote-env` 或 `/web-setup`。在 v2.1.268 之前，提交其中一個命令會傳回 [`Unknown command`](https://code.claude.com/docs/zh-TW/errors#unknown-command)。 這是伺服器端組織政策，所以無法從本地設定、環境變數或 CLI 旗標覆蓋。 如果 Claude Code 尚未載入您的組織政策或無法擷取它，這些命令會改為回答 `Couldn't verify your organization's policy for cloud sessions. Check your network connection, then restart Claude Code and try again.`。 **該怎麼做：**

- 要求您的組織中的[擁有者](https://code.claude.com/docs/zh-TW/server-managed-settings#access-control)在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 的 Claude Code 管理設定中啟用雲端工作階段
- 如果訊息說它無法驗證政策，請檢查您的網路連線，然後重新啟動 Claude Code 並再試一次

### —json-schema 值不是有效的 JSON Schema

您傳遞給 [`--json-schema`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 的架構在[非互動模式](https://code.claude.com/docs/zh-TW/headless#get-structured-output)中未能通過 JSON Schema 編譯，所以 `claude` 以代碼 1 結束而不是執行提示。在 v2.1.205 之前，無效的架構產生無結構的輸出且沒有錯誤，任何使用 `format` 關鍵字的架構都被視為無效。

```
Error: --json-schema is not a valid JSON Schema: data/type must be equal to one of the allowed values

```

第二個冒號後的文字是驗證器的診斷，並命名失敗的關鍵字或位置。使用 `format` 關鍵字的架構，例如 `"format": "email"`，是有效的：Claude Code 接受 `format` 作為註釋，不強制執行它。 Claude Code 在架構編譯之前執行兩個檢查：它以 `Error: --json-schema is not valid JSON` 拒絕不可解析的 JSON 值，以及有效但不是物件的 JSON 以 `Error: --json-schema must be a JSON object` 拒絕。 **該怎麼做：**

- 修復診斷命名的架構部分，然後重新執行命令
- 如果診斷是 `schema too large`，請減少架構的巢狀和 `$ref` 重複使用
- 請參閱[取得結構化輸出](https://code.claude.com/docs/zh-TW/headless#get-structured-output)以取得有效的架構和命令

### 設定檔超過 2MiB 限制

您傳遞給 [`--settings`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 的檔案大於 2 MiB，所以 `claude` 在啟動時以代碼 1 結束而不是載入它。設定檔是一個小型 JSON 文件，所以這麼大的檔案通常意味著路徑指向錯誤的檔案。在 v2.1.214 之前，Claude Code 讀取檔案時沒有大小檢查，多 GB 檔案或 `/dev/zero` 等裝置檔案會無限制地增加記憶體。

```
Error: Settings file exceeds the 2MiB limit: /path/to/settings.json

```

Claude Code 以相同方式拒絕不是常規檔案的 `--settings` 路徑：裝置、FIFO 或 socket 報告 `Error: Cannot use settings file (Not a regular file (device, FIFO, or socket))` 後跟路徑，目錄報告 `EISDIR` 原因。 **該怎麼做：**

- 將 `--settings` 指向 2 MiB 以下的常規 JSON 設定檔。請參閱[設定](https://code.claude.com/docs/zh-TW/settings)以了解格式。

### 目前目錄不再存在

您從一個在您的 shell 進入後被刪除或移動的目錄啟動 `claude`，例如 worktree 或另一個 shell 移除的臨時目錄。Claude Code 無法讀取其工作目錄，所以它在啟動工作階段之前以代碼 1 結束，在互動和[非互動](https://code.claude.com/docs/zh-TW/headless)模式中都是如此。在 v2.1.239 之前，Claude Code 使用縮小的套件來源和原始 `ENOENT ... uv_cwd` 堆疊在 stderr 上崩潰，而不是此訊息。

```
The current directory no longer exists (it was deleted or moved). Start Claude Code from an existing directory.
error: The current working directory was deleted, so that command didn't work. Please cd into a different directory and try again.

```

兩種形式的原因和修復都是相同的。 當 Claude Code 因為不同的原因（例如權限變更）無法讀取工作目錄時，訊息會命名錯誤代碼：`Can't read the current directory (EACCES). Start Claude Code from a different directory.` 在 macOS 上，`~/Desktop`、`~/Documents`、`~/Downloads` 或 iCloud Drive 中目錄的 `EPERM` 通常意味著 macOS 阻止您的終端應用程式存取該資料夾。讀取該資料夾的其他命令也會以相同方式失敗：即使使用 `sudo`，`ls` 也會報告 `Operation not permitted`。 **該怎麼做：**

- 變更到存在的目錄，例如您的主目錄或專案目錄，然後再次執行 `claude`
- 如果目錄在相同路徑重新建立，您的 shell 仍然保有已刪除的目錄。執行 `cd "$PWD"` 或離開並重新進入目錄，然後執行 `claude`
- 對於 macOS 上的 `EPERM`，使用 Cmd+Q 結束您的終端應用程式，重新開啟它，返回該資料夾，然後執行 `claude`。如果該資料夾中的 `ls` 仍然失敗，開啟**系統設定 > 隱私與安全 > 檔案和資料夾**，為您的終端應用程式開啟該資料夾，然後重新開啟終端

### 目錄無法解析為真實位置

您為工作目錄的子目錄執行了 `/add-dir`，Claude Code 無法將目錄解析為其真實位置。 您已經可以存取工作目錄的子目錄，所以 `/add-dir` 只載入其 skills、命令和代理。在載入它們之前，Claude Code 檢查目錄的真實位置（解析任何符號連結）是否在工作目錄內。當 Claude Code 無法解析該位置時，它不載入任何內容並顯示此訊息：

```
packages/app couldn't be resolved to a real location, so its skills, commands, and agents weren't loaded. Check that it is a directory inside the working directory and try again.

```

**該怎麼做：**

- 檢查路徑是否命名工作目錄內的真實目錄，然後再次執行 `/add-dir`
- 訊息不會變更您的檔案存取；它只報告目錄的 `.claude/` 內容未被載入

在 v2.1.261 之前，當工作目錄在 `/net/<host>` 自動掛載上時，此訊息也會為每個 `/add-dir <subdirectory>` 出現，Claude Code 根據設計拒絕解析路徑；目錄很好，重試無法幫助。

### 啟動遠端控制時工作區未受信任

您在未信任的目錄中使用 `claude remote-control` 或其 `claude rc` 別名啟動[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)伺服器模式。該命令本身不顯示工作區信任對話框，所以它以代碼 1 結束並命名修復：

```
Error: Workspace not trusted. Please run `claude` in /Users/you/project first to review and accept the workspace trust dialog.

```

在您的主目錄中，訊息是不同的，因為工作區信任對話框永遠不會為主目錄儲存信任，所以在那裡接受它無法滿足此檢查。在 v2.1.214 之前，主目錄顯示上述訊息，其建議無法在那裡成功。

```
Error: Workspace not trusted. /Users/you is your home directory, and for security home-directory trust is never saved, so running `claude` here first won't help. Run `claude rc` from a project directory instead (run `claude` there once to accept the trust dialog).

```

**該怎麼做：**

- 在目錄中執行 `claude`，接受[工作區信任對話框](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)，然後再次執行 `claude remote-control`
- 在您的主目錄中，變更到專案目錄並在那裡啟動遠端控制

### 未帶到遠端控制啟動的工作階段

您使用全域 `claude` 旗標在 `remote-control` 動詞之前啟動[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)，該旗標會限制或設定遠端控制啟動的工作階段，例如 `--settings`、`--setting-sources`、`--permission-mode`、`--disallowed-tools` 或 `--mcp-config`。放在動詞之前的旗標永遠不會到達這些工作階段。Claude Code 拒絕啟動，命名該旗標：

```
Error: `--settings` before `remote-control` is not carried over to the sessions Remote Control starts, so Remote Control refuses to start rather than drop it — remove it, and give Remote Control's own options after the verb (see `claude remote-control --help`).

```

Claude Code 不拒絕無害的全域旗標，例如 `--verbose`、`--model` 或包裝器注入的 `--session-id` 或 `--plugin-dir`：它忽略它們，遠端控制啟動。 Claude Code 也拒絕為它尚未識別為無害的全域旗標啟動，所以在較新版本中新增的旗標可能會在此訊息中出現，直到稍後的版本將其標記為無害。 **該怎麼做：**

- 從動詞之前移除旗標，並在其後傳遞[遠端控制自己的選項](https://code.claude.com/docs/zh-TW/remote-control#start-a-remote-control-session)；`claude remote-control --help` 列出它們
- 當被拒絕的旗標是 `--permission-mode` 時，執行 `claude remote-control --permission-mode <mode>` 以設定遠端控制啟動的工作階段的權限模式

在 v2.1.248 之前，當全域旗標首先出現時，`claude remote-control` 不接受自己的旗標，命令失敗並出現未知選項錯誤。

### claude import 在此組建中尚不可用

您執行了 [`claude import`](https://code.claude.com/docs/zh-TW/cli-reference#cli-commands)，Claude Code 發現匯入流程已關閉，所以命令以代碼 1 結束而不是啟動匯入。在 v2.1.222 之前，關閉匯入流程的組建將 `import` 視為提示並啟動互動工作階段，而不是列印此訊息。

```
`claude import` is not yet available in this build. Run `claude` and use /mcp or edit ~/.claude/settings.json directly.

```

Claude Code 透過從 Anthropic 擷取並在磁碟上快取的功能旗標開啟 `claude import`。此訊息意味著快取的值已關閉。原因通常是以下之一：

- 您自安裝以來尚未啟動工作階段，所以 Claude Code 尚未擷取旗標。第一個 `claude import` 即使功能對您可用，也可能列印此訊息。
- 您透過 Amazon Bedrock、Google Cloud 的代理平台、Microsoft Foundry、AWS 上的 Claude Platform 或透過 [Claude 應用程式閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway#availability-and-limitations)使用 Claude Code。Claude Code 在這些工作階段中不擷取功能旗標，所以 `claude import` 保持不可用。
- 您設定了 `DISABLE_TELEMETRY`、`DO_NOT_TRACK`、`DISABLE_GROWTHBOOK` 或 [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/zh-TW/env-vars)，它們關閉功能旗標擷取，所以 `claude import` 保持不可用。

**該怎麼做：**

- 在全新安裝上，啟動 `claude`，等待工作階段載入，結束，然後再次執行 `claude import`
- 功能旗標擷取保持關閉的地方，自己設定設定：使用 [`claude mcp add`](https://code.claude.com/docs/zh-TW/mcp#installing-mcp-servers) 新增 MCP 伺服器，並建立您想要帶過來的 [`CLAUDE.md` 檔案](https://code.claude.com/docs/zh-TW/memory#how-claude-md-files-load)、[skills 和命令](https://code.claude.com/docs/zh-TW/skills#where-skills-live)和[子代理](https://code.claude.com/docs/zh-TW/sub-agents#choose-the-subagent-scope)。訊息也命名 `~/.claude/settings.json`。在 `claude import` 帶來的設定中，該檔案只保有[權限模式](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings)；Claude Code 不從中讀取 MCP 伺服器。

### 無法讀取 Claude Code 設定

您執行了 [`claude import`](https://code.claude.com/docs/zh-TW/cli-reference#cli-commands)，而 Claude Code 無法解析 `~/.claude.json`，它儲存您的登入和每個專案狀態的檔案。子命令讀取該檔案以檢查可用性，但不顯示互動工作階段顯示的復原對話框，所以它以代碼 1 結束。在 v2.1.222 之前，具有不可讀設定檔的 `claude import` 啟動互動工作階段，其復原對話框處理該檔案。

```
Could not read Claude Code config — run `claude` with no arguments to recover it.

```

**該怎麼做：**

- 執行沒有引數的 `claude`。Claude Code 偵測無效檔案並提供重設它。然後再次執行 `claude import`。
- 若要保留您所做的手動編輯，請在編輯器中修復 `~/.claude.json` 中的 JSON 語法，然後重新執行 `claude import`

### 無法從 Claude Desktop 匯入伺服器

Claude Code 無法新增您在 `claude mcp add-from-claude-desktop` 中選擇的其中一個伺服器。該命令仍然匯入其他選定的伺服器，並為每個它無法新增的伺服器列印一行。在 v2.1.205 之前，第一個失敗的伺服器停止匯入，沒有選定的伺服器被新增。

```
Could not import my server: Invalid name my server. Names can only contain letters, numbers, hyphens, and underscores.

```

伺服器名稱後的文字是原因。最常見的是名稱檢查：Claude Desktop 允許伺服器名稱中的字元，例如空格和句號，而 `claude mcp` 限制為字母、數字、連字號和底線。其他原因包括無法通過驗證的伺服器設定和被您的組織的 [MCP 政策](https://code.claude.com/docs/zh-TW/managed-mcp)阻止的伺服器。 **該怎麼做：**

- 在 `claude_desktop_config.json` 中重新命名伺服器以僅使用字母、數字、連字號和底線，然後再次執行 `claude mcp add-from-claude-desktop`
- 使用有效名稱直接使用 `claude mcp add` 或 `claude mcp add-json` 新增該伺服器。請參閱[從 Claude Desktop 匯入 MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp#import-mcp-servers-from-claude-desktop)。

### 無法將 MCP 伺服器新增到受管範圍

您使用 `--scope managed` 執行了 `claude mcp add` 或 `claude mcp add-json`。該範圍保有您的組織透過 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 受管設定提供的伺服器。Claude Code 只從受管設定讀取它們，所以命令無法將伺服器寫入該範圍。

```
Cannot add MCP server to scope: managed

```

**該怎麼做：**

- 將伺服器新增到您可以寫入的範圍：`local`、`user` 或 `project`。沒有 `--scope`，命令使用 `local`。請參閱 [MCP 安裝範圍](https://code.claude.com/docs/zh-TW/mcp#mcp-installation-scopes)
- 若要為您的組織中的每個使用者提供伺服器，請將其新增到您部署的受管設定中的 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers)

### 無法讀取 .mcp.json

讀取專案的 [`.mcp.json`](https://code.claude.com/docs/zh-TW/mcp#project-scope) 的命令，例如 `claude mcp add` 或 `claude mcp add-json` 搭配 `--scope project`，或 `claude mcp remove`，發現您目前目錄中的檔案不是常規檔案或大於 2 MiB，所以它以此錯誤結束而不是讀取檔案。

```
Can't read .mcp.json: it isn't a regular file or is larger than 2097152 bytes. Fix or remove it, then run the command again.

```

在 v2.1.257 之前，`.mcp.json` 的 FIFO 讓命令無限期等待且沒有輸出，到 `/dev/zero` 等裝置檔案的符號連結會無限制地增加記憶體，直到程序被殺死。 **該怎麼做：**

- 檢查您目前目錄中 `.mcp.json` 的內容。將其替換為 [project-scope 格式](https://code.claude.com/docs/zh-TW/mcp#project-scope)中的普通 JSON 檔案，或刪除它，然後執行命令。

### 伺服器是 Anthropic 託管的，不支援本地 OAuth

您為 URL 指向透過第三方身份提供者進行身份驗證的 Anthropic 託管連接器主機的 MCP 伺服器啟動了登入。這些主機包括 `microsoft365.mcp.claude.com`、`gmail.mcp.claude.com` 和 `gcal.mcp.claude.com`。Claude Code 拒絕為這些主機從 `/mcp` 面板和 `claude mcp login` 啟動其本地 OAuth 流程，因為[它們的登入僅透過 claude.ai 運作](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)。

```
"gmail" is Anthropic-hosted and doesn't support local OAuth. Connect it via Settings → Connectors on claude.ai (requires `claude login`), then it'll be available here automatically.

```

Claude Code 按 URL 匹配這些主機，所以當您使用 `claude mcp add` 或在 `.mcp.json` 中新增的伺服器指向其中之一時，訊息會出現。 **該怎麼做：**

- 使用 `claude mcp remove <name>` 移除您的項目，以便它無法隱藏相同 URL 的 claude.ai 連接器
- 移除後，在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 連接服務，同時登入您在 Claude Code 中使用的帳戶。連接後，如果您的活躍身份驗證方法是 claude.ai 訂閱登入，[連接器會自動出現在 Claude Code 中](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)

### 伺服器拒絕了由設定的 headersHelper 鑄造的授權標頭

其 [`headersHelper`](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication) 提供 `Authorization` 標頭的 MCP 伺服器以 HTTP 401 或 403 回答連線，所以 Claude Code 報告連線失敗。因為 helper 提供 `Authorization` 標頭，Claude Code [不會回退到 OAuth](https://code.claude.com/docs/zh-TW/mcp#authenticate-with-remote-mcp-servers) 用於伺服器：

```
Server rejected the Authorization header minted by the configured headersHelper (HTTP 401). Check that the helper command returns a valid credential for this MCP endpoint — OAuth fallback is disabled when the helper supplies Authorization.

```

Claude Code 在每次連線嘗試時重新執行 helper，所以在暫時拒絕後重試（例如令牌輪換競爭）可以使用新認證成功。 **該怎麼做：**

- 按照 Claude Code 執行它的方式自己執行 `headersHelper` 命令：從 [Claude Code 執行它的目錄](https://code.claude.com/docs/zh-TW/mcp#where-the-helper-runs)，使用 [Claude Code 為其設定的環境變數](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication)，以及沒有 [Claude Code 為來自專案 `.mcp.json`、外掛程式或專案代理檔案的伺服器移除的認證變數](https://code.claude.com/docs/zh-TW/mcp#which-variables-a-helper-can-read)。檢查它列印的 `Authorization` 值伺服器的端點接受
- 修復 helper 或其認證來源後，在 `/mcp` 中選擇伺服器並選擇**重新連線**

在 v2.1.248 之前，Claude Code 為其 helper 提供 `Authorization` 標頭的伺服器執行 OAuth 發現。該發現可能失敗並出現 `Incompatible auth server: does not support dynamic client registration` 而不是報告被拒絕的認證。

### 找不到 MCP 權限提示工具

您傳遞給 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 的工具在執行首次需要權限決定時不在連接的 MCP 工具中，要麼因為其伺服器從未連接，要麼因為沒有連接的伺服器公開該名稱的工具。Claude Code 仍然傳送您的提示：[非互動](https://code.claude.com/docs/zh-TW/headless)執行在第一個需要批准的工具呼叫時以此錯誤和結束代碼 1 結束，所以即使提出了請求，它也不產生答案。在第一個提示之前，Claude Code 等待最多由 [`MCP_TIMEOUT`](https://code.claude.com/docs/zh-TW/env-vars) 設定的每個伺服器連線逾時 30 秒，以便該伺服器連接。在 v2.1.206 之前，啟動不等待伺服器完成連接，所以啟動緩慢但健康的伺服器也產生此錯誤。

```
Error: MCP tool mcp__permissions__approve (passed via --permission-prompt-tool) not found. Available MCP tools: none

```

`Available MCP tools:` 後的清單命名等待結束時連接的 MCP 工具。 **該怎麼做：**

- 檢查伺服器啟動並保持連接：在相同目錄中執行 `claude mcp list` 並確認伺服器列為已連接
- 確認工具名稱符合伺服器公開的 `mcp__<server>__<tool>` 名稱
- 如果伺服器需要超過 30 秒才能啟動，請提高 [`MCP_TIMEOUT`](https://code.claude.com/docs/zh-TW/env-vars)

### OAuth 回呼連接埠已在使用中

當您使用 OAuth 登入遠端 MCP 伺服器時，Claude Code 啟動本地接聽器以接收登入回呼。如果該接聽器需要的連接埠被另一個程序佔用，登入失敗並出現此訊息。這主要發生在[固定回呼連接埠](https://code.claude.com/docs/zh-TW/mcp#use-a-fixed-oauth-callback-port)透過 [`MCP_OAUTH_CALLBACK_PORT`](https://code.claude.com/docs/zh-TW/env-vars) 變數或 `--callback-port` 設定時，因為沒有一個 Claude Code 會選擇可用的連接埠。

```
OAuth callback port <port> is already in use — another process may be holding it. Run `lsof -ti:<port> -sTCP:LISTEN` to find it.

```

在 Windows 上，建議的命令是 `netstat -ano | findstr :<port>`。 **該怎麼做：**

- 執行訊息中的命令以找到佔用連接埠的程序，並停止它或等待它完成
- 如果另一個程式永久需要該連接埠，使用伺服器註冊不同的重定向 URI，並使用 `MCP_OAUTH_CALLBACK_PORT` 或 `--callback-port` 設定其連接埠，以您使用的為準
- 然後再次啟動登入，例如在 `/mcp` 中選擇伺服器

### 沒有可用的 OAuth 重定向連接埠

當您使用[OAuth](https://code.claude.com/docs/zh-TW/mcp#authenticate-with-remote-mcp-servers)登入遠端 MCP 伺服器時，Claude Code 啟動本地接聽器以接收登入回呼。當 Claude Code 無法為其繫結本地連接埠時，登入失敗並出現此訊息。機器上的某些內容阻止它在 `127.0.0.1` 上接聽，例如安全軟體或拒絕本地接聽器的沙箱政策。

```
No available ports for OAuth redirect

```

在 v2.1.268 之前，Claude Code 不回退到作業系統指派的連接埠，所以當只有其自選連接埠無法繫結時，訊息也會出現。這可能發生在 Hyper-V 保留涵蓋 Claude Code 選擇的連接埠的連接埠範圍的 Windows 主機上。 **該怎麼做：**

- 檢查安全軟體或沙箱政策是否阻止程序在 `127.0.0.1` 上接聽，並允許 Claude Code 繫結本地連接埠
- 然後再次啟動登入，例如在 `/mcp` 中選擇伺服器

### /security-review 在沒有 origin/HEAD 的情況下失敗

[`/security-review`](https://code.claude.com/docs/zh-TW/commands#all-commands) 透過針對 `origin/HEAD` 進行差異來建立其審查上下文，這是記錄您的 `origin` 遠端上哪個分支是預設分支的本地 ref。當該 ref 不存在時，收集差異的 git 命令失敗，審查在開始前停止。

```
Error: Shell command failed for pattern "!`git diff --name-only origin/HEAD...`": [stderr]
fatal: ambiguous argument 'origin/HEAD...': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'

```

訊息可能引用 `git log` 或不同的 `git diff`。Git 只在遠端公告預設分支且您的擷取 refspec 涵蓋它時建立 `origin/HEAD`，完整的遠端 `git clone` 帶有提交時會執行此操作。ref 在這些設定中遺失：

- 單一分支或 CI 檢出，擷取太窄的 refspec
- 伺服器端 HEAD 指向沒有人推送的分支的遠端
- 沒有 `origin` 遠端的儲存庫，或您從未擷取的儲存庫

Claude Code 為任何 [injects dynamic context](https://code.claude.com/docs/zh-TW/skills#when-an-injected-command-fails) 的 skill 顯示相同的錯誤，失敗的注入命令中止該 skill 的呼叫。兩個同級字串在命令執行之前就會觸發：

- `Shell command permission check failed for pattern "..."`: 命令的權限檢查不允許它。[Permission checks on injected commands](https://code.claude.com/docs/zh-TW/skills#permission-checks-on-injected-commands) 涵蓋在每個權限模式中哪些結果中止以及如何使用 `allowed-tools` 預先批准命令
- `Skill <name> requires bash (`shell: bash` in frontmatter) but Git Bash was not found`: skill 的 frontmatter 在沒有它的機器上要求 bash。安裝 Git for Windows 或將 frontmatter 變更為 `shell: powershell`。請參閱[注入命令如何執行](https://code.claude.com/docs/zh-TW/skills#how-injected-commands-run)

**該怎麼做：**

- 透過命名您的遠端的預設分支建立 ref：`git remote set-head origin <default-branch>`。只要本地追蹤 ref `origin/<default-branch>` 存在，這就有效。如果它不存在，如在單一分支複製中，首先擷取分支：執行 `git remote set-branches --add origin <branch>`，然後 `git fetch origin`，然後重新執行 set-head 命令。重新執行 `/security-review`。
- 如果您寧願不命名分支，執行 `git fetch origin` 然後 `git remote set-head origin --auto`，它詢問遠端其預設分支是什麼。當遠端不公告預設分支時它失敗並出現 `error: Cannot determine remote HEAD`，因為它是空的或其 HEAD 指向沒有人推送的分支；改為明確命名分支。當您的複製不擷取該分支時它失敗並出現 `error: Not a valid ref`；首先如上所述擴寬 refspec。
- 如果儲存庫沒有遠端，使用 `git remote add origin <url>` 新增一個並在建立 ref 之前擷取。如果遠端是空的，首先使用 `git push -u origin HEAD` 推送您的分支，並在 set-head 命令中命名該分支；`origin/HEAD` 然後指向您剛推送的分支，所以 `/security-review` 看到空差異，直到分支與它分歧。

### 使用 —print 時必須提供輸入

裸 `claude` 需要 stdout 是終端才能啟動互動 UI。當 stdout 被重定向或主控台不是真實終端時，例如 PowerShell ISE 和某些 IDE 輸出窗格，`claude` 改為以[非互動](https://code.claude.com/docs/zh-TW/headless)模式執行。這與 `claude -p` 相同，它需要提示，所以訊息命名 `--print` 即使您沒有傳遞旗標。在任何地方傳遞沒有提示的 `-p`/`--print` 且 stdin 上沒有任何內容產生相同的錯誤。

```
Error: Input must be provided either through stdin or as a prompt argument when using --print

```

**該怎麼做：**

- 對於互動使用，在真實終端中執行 `claude`：Windows Terminal 或 PowerShell 主控台而不是 ISE，以及您的 IDE 的整合終端而不是輸出窗格
- 對於一次性使用，傳遞提示：`claude -p "your question"`，或使用 `echo "your question" | claude -p` 管道它

### 輸入僅包含空白

在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中，Claude Code 拒絕完全由空格、製表符或換行符組成的提示，而不是傳送它，因為 API 拒絕沒有可見文字的訊息。您看到的訊息取決於空白提示來自何處：

- **`claude -p`的提示引數或管道 stdin** ：`claude` 以 `Error: Input contained only whitespace. Provide a prompt with text through stdin or as a prompt argument when using --print` 結束
- **提交給執行中的`--input-format stream-json` 或 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 工作階段的訊息**：Claude Code 在不呼叫模型的情況下結束輪次，工作階段保持可用。拒絕作為資訊訊息和輪次的結果文字到達：`Blank prompt — the message was only whitespace, so nothing was sent to the model.`

在 v2.1.229 之前，Claude Code 將空白訊息傳送到 API，API 以 400 錯誤拒絕請求。 **該怎麼做：**

- 在提示中包含可見文字。如果指令碼從變數或檔案建立提示，請在呼叫 Claude Code 之前檢查來源是否不為空。

### stream-json 輸入在沒有換行符的情況下超過 256M 字元

您的程式在 stdin 上傳送了超過 268,435,456 個字元，沒有換行符到 `claude -p --input-format stream-json` 執行，所以 Claude Code 將此錯誤列印到 stderr 並以代碼 1 結束，而不是緩衝更多輸入。訊息將該預算陳述為 `256M`。在 v2.1.257 之前，Claude Code 無限制地緩衝此類輸入，增加記憶體，直到程序崩潰或被殺死。

```
Error: stream-json input carried over 256M characters with no newline. Each stream-json message must be a single newline-terminated JSON line: either the producer is not newline-terminating its messages, or one message exceeded this budget.

```

沒有換行符的這麼長的輸入通常意味著製作者根本不是 stream-json 製作者，例如二進位檔案或意外管道的純日誌輸出。超過預算的單一訊息失敗相同的檢查。 **該怎麼做：**

- 檢查什麼被管道到 stdin。使用 [`--input-format stream-json`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)，每個訊息必須是一個換行符終止的 JSON 行
- 若要改為傳送純文字，請移除 `--input-format stream-json`；`claude -p` 預設從 stdin 讀取純文字提示

### 未知命令

在互動終端工作階段中，您提交了一個 `/` 名稱，它不符合此工作階段中的任何命令，所以 Claude Code 報告該名稱而不是執行任何操作：

```
Unknown command: /hepl. Did you mean /help?

```

Claude Code 建議此工作階段中菜單列出的最接近的命令名稱或別名。當沒有接近的時，訊息在名稱後結束。原因通常是以下之一：

- 打字錯誤，例如 `/hepl` 代替 `/help`。[How the command menu matches what you type](https://code.claude.com/docs/zh-TW/commands#how-the-command-menu-matches-what-you-type) 涵蓋在提交前選擇接近的匹配
- 存在但在此工作階段中不可用的命令，因為不符合要求，例如您的平台、計畫或身份驗證方法。[`/web-setup`](https://code.claude.com/docs/zh-TW/web-quickstart#web-setup-shows-no-commands-match-or-unknown-command) 和 [`/schedule`](https://code.claude.com/docs/zh-TW/routines#schedule-returns-unknown-command) 的故障排除項目演練兩個常見情況。某些命令在您的組織政策停用它們時以自己的訊息回答，例如 [`Cloud sessions are disabled by your organization's policy`](https://code.claude.com/docs/zh-TW/errors#cloud-sessions-are-disabled-by-your-organizations-policy)
- 來自此工作階段中未安裝或未連接的[外掛程式](https://code.claude.com/docs/zh-TW/plugins)或 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp#use-mcp-prompts-as-commands)的命令

Claude Code 只在互動終端工作階段中以此方式回答不符合的 `/` 名稱。在每個其他工作階段中，它改為將提示傳送給 Claude 作為普通訊息，並帶有命令未執行的注意和 Claude 可以在工作階段中執行的命令清單。這些工作階段包括：

- `-p` 執行
- [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 應用程式
- [Desktop 應用程式](https://code.claude.com/docs/zh-TW/desktop)的代碼標籤
- [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)的聊天面板
- [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)和[例程](https://code.claude.com/docs/zh-TW/routines)

對於無法在其中一個工作階段中執行的內建命令，Claude Code 仍然回答命令不可用，而不是將其傳送給 Claude。在 v2.1.274 之前，只有雲端工作階段和例程將不符合的名稱傳送給 Claude。在 v2.1.273 之前，它們也回答 `Unknown command`。 Claude Code 不將每個以 `/` 開頭的提示視為命令。當 `/` 後的第一個單詞以標點符號開頭時，它將提示傳送給 Claude 作為普通訊息，例如開啟 Lean 文件註釋的 `/--`，或是路徑，例如 `/var/log/syslog`。 在 v2.1.236 之前，如果您在命令菜單列出您輸入的名稱的接近匹配時按下 `Enter`，Claude Code 執行該匹配，所以 `/hepl` 等打字錯誤執行 `/help` 而不是產生此訊息。 **該怎麼做：**

- 執行建議的名稱，或輸入 `/` 後跟名稱的一部分以查看此工作階段中可用的內容
- 如果 Claude Code 報告文件化命令為未知，請檢查[命令參考](https://code.claude.com/docs/zh-TW/commands)中其行以了解它命名的要求

### 差異對於 ultrareview 來說太大

您的分支與基礎分支之間的差異，包括未提交和暫存的變更，超過 [ultrareview](https://code.claude.com/docs/zh-TW/ultrareview) 的大小限制，所以 `/code-review ultra` 和 `claude ultrareview` 子命令在雲端工作階段啟動前拒絕審查。被拒絕的審查不使用免費執行，不計費使用額度。訊息命名有效的限制、您的差異大小和貢獻最多變更行的檔案。在 v2.1.216 之前，訊息只顯示原始差異統計。

```
Diff is too large for ultrareview: 812 files, 96,410 lines changed (limits: 500 files, 8,000 lines). Largest files: package-lock.json (41,904 lines), dist/bundle.js (18,210 lines), src/generated/api.ts (9,876 lines). Pass a closer base branch (`/code-review ultra <branch>`) to narrow the scope, or split the change.

```

審查拉取請求應用相同的限制；該形式的訊息以 `PR #<N> is too large for ultrareview` 開頭，並命名 PR 的檔案和行計數。 **該怎麼做：**

- 傳遞更接近您工作的基礎分支，例如 `/code-review ultra develop`，以便審查只涵蓋針對該分支的差異
- 將變更分割成較小的分支，並審查每一個。訊息命名的檔案貢獻最多變更行，所以首先將這些移到自己的分支。

### 找不到與基礎分支的合併基礎

`/code-review ultra` 和 `claude ultrareview` 子命令審查您的分支與基礎分支之間的差異，這需要兩者共享的提交。當 `git merge-base` 找不到時，Claude Code 在雲端工作階段啟動前拒絕審查。在 Claude Code 可以驗證完整的複製上，至少有一個分支，它改為回退到[審查每個追蹤檔案](https://code.claude.com/docs/zh-TW/ultrareview#diff-limits-and-fallbacks)而不是拒絕。您在基礎分支根本找不到時、Claude Code 無法驗證您的複製完整時，或在罕見的儲存庫中看到此拒絕，其中整個樹差異不可能，例如 SHA-256 物件格式。

```
Could not find merge-base with main. Pass the base branch explicitly (e.g. `/code-review ultra develop`) or make sure you're in a git repo with a main branch.

```

第一句後的提示取決於 Claude Code 觀察到的內容：

- **您沒有傳遞基礎分支** ：Claude Code 與儲存庫的預設分支進行比較，並建議明確傳遞您的基礎，如上例所示
- **您傳遞的基礎分支已在您的複製中** ：提示讀取 `Make sure <branch> exists locally or on origin (try `git fetch origin <branch>`)`
- **您傳遞的基礎分支不在您的複製中** ：Claude Code 在比較前從 origin 擷取它。提示讀取 `<branch> was fetched from origin but shares no history with HEAD. If another branch is your real base, pass it explicitly (`/code-review ultra <branch>`)`；當 Claude Code 無法判斷您的複製是否淺時，它改為建議 `git fetch --unshallow origin`。在 v2.1.221 之前，提示為每個擷取的基礎分支建議 `git fetch --unshallow origin`，在完整複製上該命令失敗並出現 `fatal: --unshallow on a complete repository does not make sense`。

**該怎麼做：**

- 如果另一個分支是您的真實基礎，明確傳遞它：`/code-review ultra <branch>`
- 如果您的複製可能沒有完整歷史，執行 `git fetch --unshallow origin` 並重新執行審查

### 您的檢出沒有分支

檢出可以有提交但沒有分支：如果您執行 `git init` 後跟 `git fetch <url>` 和 `git checkout FETCH_HEAD`，您會得到一個分離的 HEAD，沒有 refs。Claude Code 將您的儲存庫打包為 git 套件以上傳以進行 [ultrareview](https://code.claude.com/docs/zh-TW/ultrareview)，它無法打包沒有分支或其他 refs 的儲存庫，所以 `/code-review ultra` 和 `claude ultrareview` 子命令在雲端工作階段啟動前拒絕審查。

```
Your checkout has no branches (detached HEAD only), which cloud review can't bundle. Create one first — `git checkout -b <name>` — then rerun /code-review ultra.

```

在 v2.1.221 之前，Claude Code 嘗試審查此檢出中的每個追蹤檔案，上傳失敗。 **該怎麼做：**

- 使用 `git checkout -b <name>` 在您目前的提交建立分支，然後重新執行審查

### 沒有 GitHub 帳戶連接到您的 Claude 帳戶

您執行了 `/code-review ultra <PR#>` 或 `claude ultrareview <PR#>`，在建立雲端工作階段前，Claude Code 詢問伺服器[連接到您的 Claude 帳戶的 GitHub 帳戶](https://code.claude.com/docs/zh-TW/ultrareview#review-a-pull-request)是否可以到達 PR 的儲存庫。沒有帳戶連接，或連接已過期，所以雲端複製會失敗，Claude Code 拒絕啟動。Claude Code 不為被拒絕的啟動花費免費執行或計費使用額度。

```
Ultrareview clones <owner>/<repo> in the cloud with the GitHub account connected to your Claude account, and none is connected (or the connection expired). To fix: run /web-setup to reuse your GitHub CLI login, or connect an account at https://claude.ai/connect-github — then re-run /code-review ultra 1234 (allow a minute after connecting).

```

當 [`/web-setup`](https://code.claude.com/docs/zh-TW/web-quickstart#connect-from-your-terminal) 在您的工作階段中不可用時，訊息只命名 claude.ai 連結。 **該怎麼做：**

- 執行 `/web-setup` 以將您的 GitHub CLI 登入連接到您的 Claude 帳戶，或在 [claude.ai/connect-github](https://claude.ai/connect-github) 連接帳戶
- 連接後一分鐘重新執行審查

在 v2.1.248 之前，Claude Code 不在啟動前檢查此項。

### 您連接的 GitHub 帳戶看不到儲存庫

您執行了 `/code-review ultra <PR#>` 或 `claude ultrareview <PR#>`，[連接到您的 Claude 帳戶的 GitHub 帳戶](https://code.claude.com/docs/zh-TW/ultrareview#review-a-pull-request)無法讀取 PR 的儲存庫，所以雲端複製會失敗，Claude Code 拒絕啟動。Claude Code 不為被拒絕的啟動花費免費執行或計費使用額度。

```
Your connected GitHub account can't see <owner>/<repo> — usually the Claude GitHub app isn't installed on <owner> or wasn't granted this repo (web-connected accounts need it for private repos), or a different GitHub account is connected. To fix: run /web-setup to reuse your GitHub CLI login, or install the app at https://github.com/apps/claude/installations/new — then re-run /code-review ultra 1234.

```

當 [`/web-setup`](https://code.claude.com/docs/zh-TW/web-quickstart#connect-from-your-terminal) 在您的工作階段中不可用時，訊息只命名應用程式安裝。 **該怎麼做：**

- 如果您的本地 `gh` CLI 可以讀取儲存庫，執行 `/web-setup` 以將該登入連接到您的 Claude 帳戶
- 變更後重新執行審查

在 v2.1.248 之前，Claude Code 不在啟動前檢查此項。

### GitHub 應用程式預檢暫時失敗

您從本地儲存庫啟動了[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，兩個步驟一起失敗。Claude Code 無法建立或上傳您的儲存庫套件。在上傳前，它檢查雲端服務是否可以從 GitHub 複製儲存庫，而不是明確的答案，該檢查以重試可以清除的錯誤結束，例如網路錯誤、逾時或暫時伺服器錯誤。完整訊息以停止套件的內容開頭，例如 `Could not upload repo bundle (<error>)`，並以預檢句子結尾：

```
Could not upload repo bundle (<error>). The GitHub App preflight failed transiently (network or service hiccup) — retry in a moment to start from GitHub instead

```

**該怎麼做：**

- 片刻後重新執行命令。當 GitHub 檢查通過時，Claude Code 可以從 GitHub 複製啟動工作階段，所以失敗的上傳不再阻止啟動
- 如果重試持續失敗，訊息的開頭命名停止上傳的內容。當該原因是您可以修復的內容時，修復它以便工作階段可以改為從您的本地儲存庫啟動

在 v2.1.251 之前，Claude Code 以 `Please set up GitHub on https://claude.ai/code` 結尾訊息，即使 GitHub 檢查只暫時失敗，設定建議無法清除暫時失敗。

### GitHub 未連接到您的 Claude 帳戶

您從本地儲存庫啟動了[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)，例如使用 `/autofix-pr`。沒有 GitHub 帳戶連接到您的 Claude 帳戶，或連接已過期，所以 Claude Code 拒絕啟動：

```
GitHub isn't connected to your Claude account, so this repository can't be cloned in the cloud. Run /web-setup to connect with your GitHub CLI login, or connect on the web at https://claude.ai/connect-github

```

當您使用 [`/schedule`](https://code.claude.com/docs/zh-TW/routines) 建立例程時，相同的訊息作為命名儲存庫的設定注意出現；注意不阻止建立例程。 **該怎麼做：**

- 執行 `/web-setup` 以使用您的 GitHub CLI 登入連接到您的 Claude 帳戶，或在 [claude.ai/connect-github](https://claude.ai/connect-github) 連接帳戶。請參閱 [GitHub 身份驗證選項](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#github-authentication-options)以了解兩者的差異。
- 連接後一分鐘重新執行命令

在 v2.1.268 之前，Claude Code 報告此為 Claude GitHub 應用程式檢查的暫時失敗，並建議重試或安裝應用程式；兩者都不連接 GitHub 帳戶。

### 需要單一登入授權

您執行了 [`/install-github-app`](https://code.claude.com/docs/zh-TW/github-actions#quick-setup)，並選擇了其組織強制執行 SAML 單一登入的儲存庫。在設定前，Claude Code 使用 GitHub CLI 檢查您對儲存庫的存取，GitHub 拒絕該檢查，因為您的 `gh` 令牌尚未針對組織授權。精靈顯示帶有授權步驟的警告：

```
Single sign-on authorization needed
<owner>/<repo> belongs to an organization that enforces SAML single sign-on, and your GitHub CLI token isn't authorized for it yet.

```

**該怎麼做：**

- 透過執行 `gh auth refresh -h github.com -s repo,workflow` 使用 `repo` 和 `workflow` 範圍重新授權您的 GitHub CLI 登入，並在 GitHub 提示單一登入時授權組織
- 如果您使用 `GH_TOKEN` 中的個人存取令牌進行身份驗證，開啟 [github.com/settings/tokens](https://github.com/settings/tokens)，在令牌上選擇**設定 SSO** ，並授權組織
- 再次執行 `/install-github-app`

在 v2.1.273 之前，Claude Code 為此條件顯示 `Admin permissions required` 警告。

### 無法恢復對話

Claude Code 無法讀取或處理您從 [`claude --resume` 選擇器](https://code.claude.com/docs/zh-TW/sessions#use-the-session-picker)選擇的工作階段的已儲存文字記錄，所以它結束程序而不是在部分載入狀態下繼續。訊息包括重試的命令：

```
Failed to resume the conversation.
Run claude --resume <session-id> to retry, or claude to start a new session.

```

Claude Code 在顯示訊息後以代碼 1 結束。執行中工作階段內的 `/resume` 選擇器報告對話中的 `Failed to resume conversation`，您目前的工作階段保持執行。在 v2.1.216 之前，來自 `claude --resume` 選擇器的失敗恢復在 `Resuming conversation…` 微調器上無限期停留，而不是顯示此訊息。 **該怎麼做：**

- 執行 `claude --resume <session-id>`，使用訊息中的工作階段 ID 重試
- 如果重試再次失敗，執行 `claude` 啟動新工作階段

### 找不到具有工作階段 ID 的對話

您傳遞了工作階段 ID 給 `claude --resume <session-id>`，沒有已儲存的文字記錄符合它：

```
No conversation found with session ID: <session-id>

```

Claude Code 在顯示訊息後以代碼 1 結束。Claude Code [首先搜尋目前專案，然後搜尋此機器上的每個其他專案](https://code.claude.com/docs/zh-TW/sessions#resume-a-session)以尋找 ID。在 v2.1.223 之前，查詢在目前專案目錄及其 git worktrees 停止，所以從工作階段最後工作的目錄恢復。 常見原因：

- **打字錯誤的 ID** ：對於非互動執行，ID 是 [`--output-format json` 輸出](https://code.claude.com/docs/zh-TW/headless#get-structured-output)的 `session_id` 欄位
- **已刪除的文字記錄** ：Claude Code 在[保留期](https://code.claude.com/docs/zh-TW/sessions#where-transcripts-are-stored)後移除文字記錄，預設 30 天，遵循[保留掃描規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)
- **不同的機器** ：Claude Code 在本地儲存文字記錄，所以在執行工作階段的機器上恢復工作階段
- **重複副本** ：如果您在 `~/.claude/projects` 下複製了專案目錄，使兩個文字記錄帶有相同 ID，Claude Code 報告此訊息而不是任意恢復一個副本

**該怎麼做：**

- 對於互動工作階段，使用 `claude --resume` 開啟[工作階段選擇器](https://code.claude.com/docs/zh-TW/sessions#use-the-session-picker)，按 `Ctrl+A` 將其擴寬到此機器上的每個專案，然後選擇工作階段
- 使用 `claude -p` 或 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 建立的工作階段不會出現在選擇器中，所以重新檢查 ID 與您的原始執行列印的 `session_id`

### 無法在此工作階段中切換轉譯器

當您切換轉譯器時，Claude Code 重新啟動其程序。您在 Claude Code 拒絕重新啟動的工作階段中執行了 [`/tui`](https://code.claude.com/docs/zh-TW/fullscreen#enable-fullscreen-rendering)，所以它不切換並保存任何內容。您看到的訊息告訴您原因：

- `Cannot switch renderers while work is running in the background`：您有在背景執行的工作，重新啟動會放棄，例如背景 shell 或子代理。等待工作完成或使用 [`/tasks`](https://code.claude.com/docs/zh-TW/commands) 停止它，然後再次執行 `/tui fullscreen` 或 `/tui default`
- `Cannot switch renderers in this session`：工作階段有 Claude Code 無法傳遞給重新啟動程序的限制。在 v2.1.234 之前，Claude Code 無論如何重新啟動，重新啟動的工作階段執行時沒有它們

在限制訊息中，括號中的部分命名 Claude Code 發現的限制：

```
Cannot switch renderers in this session — it has restrictions a restart can't carry over (permission rules set for this session only). Nothing was changed. Running /tui fullscreen in a session started without them switches every later session too.

```

訊息可以在括號中顯示的每個原因：

- `launch flags: a custom system prompt, a tool allowlist, or restricted settings`：您使用 Claude Code 不傳遞回重新啟動程序的旗標啟動了工作階段。這些旗標包括 [`--system-prompt`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)、`--system-prompt-file`、`--append-system-prompt-file`、[`--tools`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 允許清單、[`--setting-sources`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 和 [`--permission-prompt-tool`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)
- `permission rules set for this session only`：來自 hook 或 SDK 呼叫者的[權限更新](https://code.claude.com/docs/zh-TW/hooks#permission-update-entries)新增了帶有 `session` 目的地的拒絕或詢問規則。工作階段範圍的允許規則不觸發拒絕。重新啟動會移除它們，Claude Code 改為再次提示
- `ask-before-running rules with no command-line form`：來自 hook 或 SDK 呼叫者的權限更新新增了詢問規則以及 Claude Code 傳遞回 `--allowed-tools` 和 `--disallowed-tools` 的規則。詢問規則不存在旗標
- `permission rules a command line cannot carry intact` 和 `added directories a command line cannot carry intact`：權限更新在工作階段中期新增了規則或目錄路徑。重新啟動程序的命令列無法將其文字作為相同值帶回

**該怎麼做：**

- 在沒有這些限制的工作階段中，執行 `/tui fullscreen` 或 `/tui default` 切換回。Claude Code 在那裡儲存 [`tui` 設定](https://code.claude.com/docs/zh-TW/settings-reference#tui)

### /terminal-setup 讓您的 Zed 快捷鍵保持不變

您在 Zed 中執行了 [`/terminal-setup`](https://code.claude.com/docs/zh-TW/terminal-config#enter-multiline-prompts)，Claude Code 無法完成對您的 Zed `keymap.json` 的更新，所以它讓檔案保持原樣。 每個訊息命名您的快捷鍵的路徑，並以您自己新增的快捷鍵區塊結尾：

```
Couldn't update your Zed keymap, so it was left unchanged.
To add the binding yourself, add this block to the keymap array in <path to keymap.json>:
{ "context": "Terminal", "bindings": { "shift-enter": ["terminal::SendText", "\u001b\r"] } }

```

訊息的第一行命名原因：

- `Couldn't read your Zed keymap, so it was left unchanged.`：Claude Code 無法讀取檔案，例如因為檔案權限
- `Your Zed keymap isn't a readable list of keybindings, so it was left unchanged.`：檔案讀取良好，但不解析為快捷鍵區塊的陣列，即使允許 `//` 註釋和尾隨逗號
- `Couldn't back up your Zed keymap; not modifying it.`：Claude Code 無法將檔案複製到其旁邊的 `.bak` 備份，所以它沒有變更任何內容
- `Couldn't update your Zed keymap, so it was left unchanged.`：合併的結果未驗證為帶有快捷鍵的有效快捷鍵，所以 Claude Code 丟棄它而不是寫入。具有重複鍵的快捷鍵區塊可能導致此

**該怎麼做：**

- 將訊息中的區塊複製到訊息命名的路徑中 `keymap.json` 中的頂級陣列
- 對於 `isn't a readable list of keybindings`，修復語法錯誤，或使檔案的頂級值成為陣列，然後再次執行 `/terminal-setup`

在 v2.1.247 之前，`/terminal-setup` 無法解析使用 `//` 註釋或尾隨逗號的 Zed 快捷鍵，它用只有自己的快捷鍵替換整個檔案，同時報告快捷鍵已安裝。若要恢復較早版本替換的快捷鍵，請使用[輸入多行提示](https://code.claude.com/docs/zh-TW/terminal-config#enter-multiline-prompts)下描述的 `.bak` 備份檔案。

### 此連線上無法使用 Skill 使用情況報告

您在[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)上執行了 [`/skill-doctor`](https://code.claude.com/docs/zh-TW/skills#find-unused-skills)，從您的手機或瀏覽器。Claude Code 不透過遠端控制傳送 skill 使用情況報告，改為以此訊息回答：

```
Skill usage reports are not available on this connection.

```

**該怎麼做：**

- 在工作階段執行的機器上的終端中執行 `/skill-doctor`，或在那裡執行 `claude -p "/skill-doctor"`

### 無法在遠端控制上選擇自訂輸出樣式

您從行動應用程式或網路透過[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)執行了 [`/output-style`](https://code.claude.com/docs/zh-TW/output-styles#change-your-output-style)，或命令在轉送到工作階段的訊息中到達。因為此類輪次可能不來自帳戶擁有者，Claude Code 只列出並選擇[內建樣式](https://code.claude.com/docs/zh-TW/output-styles#built-in-output-styles)，並在命令列出樣式或不識別您給定的名稱時新增此注意。[自訂樣式](https://code.claude.com/docs/zh-TW/output-styles#create-a-custom-output-style)名稱獲得與不存在的名稱相同的回答：

```
Custom output styles can't be selected over Remote Control or from a relayed message. Select one in the session itself, or pick a built-in style here.

```

**該怎麼做：**

- 選擇內建樣式，例如 `/output-style concise`
- 若要使用自訂樣式，在專案的 `.claude/settings.local.json` 中設定 [`outputStyle`](https://code.claude.com/docs/zh-TW/settings-reference#outputstyle)，或在工作階段自己的終端中執行 `/output-style <style>`（如果有的話）

### 輸出樣式已儲存到此工作階段不載入的本地設定

您嘗試使用 `/output-style <style>` 或 `/config outputStyle=<style>` 在其設定來源排除 `local` 的工作階段中切換[輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)。範例是[Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/typescript) 工作階段，其 [`settingSources`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options) 遺漏 `"local"` 和使用 [`--setting-sources`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 值遺漏 `local` 啟動的 CLI 工作階段。兩個命令都將樣式儲存到 `.claude/settings.local.json`，此類工作階段永遠不會讀回，所以 Claude Code 拒絕而不是寫入沒有效果的設定：

```
Output styles are saved to local settings (.claude/settings.local.json), which this session doesn't load, so the style can't be changed here.

```

**該怎麼做：**

- 將 `local` 新增到工作階段的設定來源並再次切換
- 在工作階段確實載入的設定檔中設定 [`outputStyle`](https://code.claude.com/docs/zh-TW/settings-reference#outputstyle) 鍵，例如專案中的 `.claude/settings.json` 或 `~/.claude/settings.json`。在 TypeScript SDK 中，改為在內聯 `settings` 物件內設定 `outputStyle`；請參閱[啟動輸出樣式](https://code.claude.com/docs/zh-TW/agent-sdk/modifying-system-prompts#activate-an-output-style)

## Plugin 錯誤

這些錯誤來自 [plugin](https://code.claude.com/docs/zh-TW/plugins) 和 [marketplace](https://code.claude.com/docs/zh-TW/plugin-marketplaces) 設定。對於不會產生此頁面上其中一則訊息的 plugin 問題，例如無法載入的 marketplace URL 或已安裝但未出現的 plugin，請參閱 [Plugin 疑難排解](https://code.claude.com/docs/zh-TW/discover-plugins#troubleshooting)。

### plugin eval 目前處於早期存取階段

您執行了 [`claude plugin eval`](https://code.claude.com/docs/zh-TW/plugin-evals) 或 `claude plugin eval init`，它在執行任何操作之前以退出代碼 1 和以下其中一則訊息結束：

```
`plugin eval` is currently in early access

```

```
`plugin eval` is currently unavailable

```

第一則訊息表示您的組建版本早於 v2.1.269，這是該命令正式推出的第一個版本。第二則訊息表示 Anthropic 已在伺服器端關閉該命令；您的機器上沒有任何設定可以將其重新開啟。 **該怎麼做：**

- 執行 `claude --version`，然後執行 `claude update`，並在新的工作階段中再次執行該命令。請參閱 [plugin evals 的需求](https://code.claude.com/docs/zh-TW/plugin-evals#requirements)
- 如果您在目前的組建版本上看到第二則訊息，請在執行另一個 `claude update` 後稍後再試一次

### Marketplace 是從不受信任的來源註冊的

Marketplace 是以 [為官方 Anthropic marketplace 保留的名稱](https://code.claude.com/docs/zh-TW/plugin-marketplaces#marketplace-schema) 註冊的，但其註冊的來源不是 `anthropics` GitHub 儲存庫。Claude Code 每次載入或重新整理 marketplace 時都會重新檢查保留的名稱，因此 marketplace 及從中安裝的 plugin 會停止載入。在 v2.1.205 之前，名稱只在新增 marketplace 時檢查，因此在其名稱變成保留名稱之前註冊的項目會繼續載入。

```
Marketplace "claude-community" is registered from an untrusted source: The name 'claude-community' is reserved for official Anthropic marketplaces. Only repositories from 'github.com/anthropics/' can use this name. To fix it, remove the marketplace and re-add it from the official source.

```

對於來源不是 GitHub 儲存庫或 Git URL 的 marketplace（例如本機目錄），中間句子改為 `can only be used with GitHub sources from the 'anthropics' organization`。`claude plugin marketplace add` 執行相同的檢查，並以 `Failed to add marketplace:` 後跟相同的保留名稱句子拒絕保留的名稱。 **該怎麼做：**

- 如果 marketplace 已經註冊，執行 `claude plugin marketplace remove <name>`，然後從官方 `github.com/anthropics` 儲存庫重新新增它
- 如果您發佈了在其名稱變成保留名稱之前使用該名稱的第三方 marketplace，請重新命名它並要求使用者從您的來源重新新增它
- 請參閱 [Marketplace schema](https://code.claude.com/docs/zh-TW/plugin-marketplaces#marketplace-schema) 下的保留名稱清單

### Plugin 命令在 shell 命令中參考 user_config

Plugin hook、[monitor](https://code.claude.com/docs/zh-TW/plugins-reference#monitors) 或 MCP [`headersHelper`](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication) 命令參考 `${user_config.KEY}` [plugin 選項](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration)，而替換後的字串會被傳遞到 shell。設定的值包含 `$(...)` 、反引號或 `;` 會在該處作為程式碼執行，因此 Claude Code 拒絕啟動該元件而不是替換該值。檢查在命令範本上執行，因此即使尚未設定任何值，錯誤也會出現。在 v2.1.207 之前，該值被替換到 shell 命令中。 措辭取決於哪個介面參考了該選項。Shell 形式的 hook 報告：

```
Hook from plugin formatter@acme-tools references ${user_config.*} in a shell-form command. The substituted value would be re-parsed by the shell. Use exec form instead — {"command": "<executable>", "args": ["${user_config.KEY}", ...]} — or read $CLAUDE_PLUGIN_OPTION_<KEY> from the hook's environment. Command: ./scripts/notify.sh ${user_config.webhook_url}

```

Monitor 報告：

```
Monitor "deploy-status" from plugin deploy-tools references ${user_config.*} in its command. The substituted value would be passed to a shell. Monitor commands cannot safely reference ${user_config.*}; have the monitor script read the value from a config file or prompt instead.

```

MCP `headersHelper` 報告：

```
headersHelper for MCP server 'internal-api' references ${user_config.*}. The substituted value would be passed to a shell; read the value inside the helper script instead (e.g. from an env var set in the server's "env" block).

```

**該怎麼做：**

- 對於 hook，新增 `args` 陣列使其以 [exec 形式](https://code.claude.com/docs/zh-TW/hooks#exec-form-and-shell-form) 執行，其中每個 `${user_config.KEY}` 變成一個沒有 shell 的單一引數。或者移除參考並在指令碼內讀取 `$CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數
- 對於 monitor，移除參考並讓 monitor 指令碼從設定檔讀取該值
- 對於 `headersHelper`，將 `${user_config.KEY}` 移到伺服器的 `headers` 欄位（不會進行 shell 解析），或在 helper 指令碼內讀取該值

### Plugin 封存完整性檢查失敗

Plugin 的 marketplace 項目使用具有 `sha256` 釘選的 [`archive` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#zip-archives)，而下載檔案的摘要與釘選不符。Claude Code 拒絕安裝，因此 plugin 快取中沒有任何變更。不符有三個可能的原因：

- 作者計算釘選後，URL 上的檔案已變更
- 作者在 marketplace 項目中輸入了錯誤的摘要
- URL 提供的檔案與作者釘選的檔案不同

```
Plugin archive integrity check failed for https://artifacts.example.com/claude-plugins/my-plugin.zip: expected sha256 6bfa50e3d2e00c052b46abe51fff89346ac803e45771f76dcf6df1ab74cca5e1, got ac52220c0914ef8ca6a602e4a7362f88d30fb021110f72a6d15b68c3fe7df2b7. The archive was not installed. Verify the sha256 in the marketplace entry, or that the URL serves the intended file.

```

**該怎麼做：**

- 如果您發佈 plugin，使用 `shasum -a 256 my-plugin.zip` 或在 PowerShell 中使用 `Get-FileHash -Algorithm SHA256 my-plugin.zip` 重新計算 URL 提供的確切檔案的摘要，並更新 marketplace 項目中的 `sha256`
- 如果您安裝 plugin，執行 `/plugin marketplace update <name>` 以重新整理目錄以防項目已更正，然後重試安裝
- 如果在重新整理後摘要仍然不符，請在安裝前詢問 marketplace 擁有者他們釘選了哪個檔案

### 路徑逃逸 plugin 目錄

Plugin 元件路徑（在 plugin 的 `plugin.json` 或其 [marketplace 項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-entries) 中宣告）解析到 plugin 自己的目錄之外。Claude Code 捨棄該路徑並載入 plugin 的其餘部分。訊息中的元件名稱（例如 `commands` 或 `hooks`）命名了宣告路徑的欄位。

```
commands path escapes plugin directory: ./../shared.md

```

在 `claude plugin` 命令輸出中，相同的錯誤讀作 `Path escapes plugin directory: ./../shared.md (commands)`。 Claude Code 拒絕指向 plugin 外部的路徑（如 `../shared-utils`）和導致 plugin 外部的符號連結，以及 [marketplace 符號連結規則](https://code.claude.com/docs/zh-TW/plugins-reference#share-files-within-a-marketplace-with-symlinks) 不允許的符號連結。對於符號連結，訊息也會說明路徑解析的位置：

```
commands path escapes plugin directory: ./commands/deploy.md — it resolves to /home/user/shared/deploy.md, outside the plugin directory

```

在 macOS 和 Linux 上，Claude Code 也拒絕包含反斜線的元件路徑，即使路徑保持在 plugin 內。使用 Windows 風格分隔符的元件路徑的 plugin 在 Windows 上載入並在其他平台上觸發此拒絕：

```
commands path escapes plugin directory: ./commands\deploy.md — its path contains a backslash, which is not resolved reliably on this platform

```

在 v2.1.251 之前，Claude Code 載入在 marketplace 項目中宣告的 `commands` 路徑，即使它指向 plugin 目錄外。Claude Code 已經拒絕在 `plugin.json` 中宣告的路徑和 marketplace 項目中的其他元件路徑。 在 v2.1.257 之前，檢查只查看路徑的拼寫，而不是符號連結導向的位置。 **該怎麼做：**

- 將參考的檔案移到 plugin 目錄內，並使用 `./` 相對路徑指向它
- 如果路徑是指向 plugin 外部檔案的符號連結，請用檔案副本替換符號連結
- 如果訊息說路徑包含反斜線，請使用正斜線寫入路徑，例如 `./commands/deploy.md`
- 若要與同一 marketplace 中的其他 plugin 共享檔案，請使用 plugin 目錄內的符號連結連結它們，遵循 [符號連結規則](https://code.claude.com/docs/zh-TW/plugins-reference#share-files-within-a-marketplace-with-symlinks)

### 無法檢查路徑

Claude Code 詢問作業系統 plugin 路徑是否存在，並收到除「找不到」以外的錯誤，因此它不會載入路徑命名的內容。plugin 的多少部分載入取決於哪個路徑失敗：

- Plugin 的其中一個 [預設元件位置](https://code.claude.com/docs/zh-TW/plugins-reference#file-locations-reference)（例如 `skills/` 資料夾、`monitors/monitors.json` 檔案或 plugin 根目錄的 [`SKILL.md`](https://code.claude.com/docs/zh-TW/plugins-reference#skills)）：plugin 的其他元件仍會載入
- Plugin 自己的目錄：該 plugin 中沒有任何內容載入

對於根本不存在的路徑，您看不到此錯誤。在 `/plugin` 中，錯誤出現在 plugin 下方，並命名路徑和作業系統傳回的程式碼：

```
skills path could not be checked: /home/user/my-plugin/skills (ELOOP)

```

在 `claude plugin list` 中，相同的錯誤讀作 `Path not found: /home/user/my-plugin/skills (skills, ELOOP)`。 產生此錯誤的原因包括：

- `ELOOP`：路徑中的符號連結指向自己或形成迴圈
- `EIO` 或 `ESTALE`：路徑在損壞或陳舊的網路掛載上
- `EACCES`：路徑上方的其中一個目錄拒絕您遍歷它的權限

**該怎麼做：**

- 用真實資料夾替換指向自己的符號連結，或刪除它
- 如果路徑在網路掛載上，重新掛載共享
- 如果程式碼是 `EACCES`，恢復您在路徑上方目錄上的執行權限
- 修復路徑後執行 `/reload-plugins`，或重新啟動 Claude Code，以載入 plugin 或元件

在 v2.1.265 之前，Claude Code 將無法檢查的預設元件資料夾視為不存在，並在沒有錯誤的情況下載入 plugin 而不包含該元件。

### Marketplace 項目路徑不保持在 marketplace 目錄內

Plugin 的 [marketplace 項目](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-entries) 宣告了一個來源路徑，Claude Code 無法將其解析到 marketplace 自己的目錄內的位置，因此 plugin 不會安裝或載入。拒絕涵蓋：

- 絕對的項目路徑、使用 `..` 爬出 marketplace 或拼寫成網路路徑的項目路徑
- 從遠端來源（例如 git 或 URL）擷取的 marketplace 中的項目，通過解析到 marketplace 目錄外的符號連結到達其目標
- 相對項目在從直接 URL 新增到其 `marketplace.json` 的 marketplace 中：Claude Code 只下載該檔案，因此路徑命名的本機 plugin 檔案不存在。請參閱 [相對路徑的 Plugin 在基於 URL 的 marketplace 中失敗](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugins-with-relative-paths-fail-in-url-based-marketplaces)

`claude plugin install` 報告拒絕如下：

```
Cannot install my-plugin@my-marketplace: its marketplace entry path does not stay inside the marketplace directory (an absolute, climbing, network-shaped, backslash-containing or link-traversing entry, an entry of a fetched marketplace that resolves or opens outside its tree — or a relative entry in a url-catalog marketplace, which has no local directory)

```

當已安裝的 plugin 的項目失敗相同的檢查時，`claude plugin list` 將 plugin 顯示為 `failed to load`，並顯示：

```
Plugin source path refused: ./my-plugin does not stay inside its marketplace directory. Check that the marketplace entry has a plain relative path.

```

**該怎麼做：**

- 如果您維護 marketplace，將項目的 `source` 寫成純相對路徑（例如 `./plugins/my-plugin`），並保持它跨越的任何符號連結指向 marketplace 目錄內
- 如果您從直接 URL 新增了 marketplace，相對項目無法解析。要求 marketplace 作者使用 [另一個 plugin 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-sources)，或改為從其 git 儲存庫新增 marketplace

### 無法載入 marketplace 設定

Claude Code 將您新增的 plugin marketplace 保留在 `~/.claude/plugins/known_marketplaces.json` 的登錄檔案中。當 Claude Code 無法使用該檔案時，需要登錄的 plugin 命令（例如 `claude plugin install`）會失敗，並顯示以下兩則訊息之一：

- `Failed to load marketplace configuration`：檔案不是有效的 JSON，或無法讀取。空檔案也會以這種方式失敗。
- `Marketplace configuration file is corrupted`：檔案是有效的 JSON，但其內容與登錄架構不符。

遺失的檔案不是失敗：Claude Code 將其視為沒有 marketplace 的登錄。 使用空檔案時，`claude plugin install` 報告：

```
✘ Failed to install plugin "my-plugin": Failed to load marketplace configuration: JSON Parse error: Unexpected EOF

```

在 v2.1.246 之前，`claude plugin install` 沒有報告此失敗。 **該怎麼做：**

- 開啟 `~/.claude/plugins/known_marketplaces.json` 並修復 JSON，或修復訊息命名為與登錄架構不符的項目
- 如果您無法修復它，刪除檔案或用 `{}` 替換其內容，然後使用 `claude plugin marketplace add <source>` 重新新增每個 marketplace。Claude Code 在您下次在已信任的資料夾中啟動它時，重新註冊您的使用者或受管設定在 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 中宣告的 marketplace。

## 工具錯誤

這些錯誤來自 Claude 的內建工具。Claude 會自動修正大多數工具錯誤。當需要您進行變更時，該錯誤的**應該怎麼做** 清單會說明要變更的內容。

### Agent would be spawned with zero tools

子代理的 [`tools` 清單](https://code.claude.com/docs/zh-TW/sub-agents#supported-frontmatter-fields)中的每個項目都無法符合可用的工具，因此 Claude Code 拒絕啟動子代理：沒有工具，它就無法行動。該訊息會按照出錯的原因將您的項目分組：

- **Unrecognized** ：該項目不符合任何工具名稱，通常是打字錯誤，例如 `Grpe` 而非 `Grep`。
- **Not available to subagents** ：該項目命名了一個[子代理無法使用](https://code.claude.com/docs/zh-TW/sub-agents#available-tools)的真實工具。背景子代理保持較小的內建工具集，因此當子代理在背景中執行時（這是預設行為），只有前景子代理才能使用的項目會出現在此處。如果您列出 `Agent`，該訊息會改為在下一個群組下報告它。
- **Matched no tools in this session** ：該項目有效，但目前工作階段中沒有工具符合它，例如沒有連接 GitHub MCP 伺服器的 `mcp__github__*`，或在[深度限制](https://code.claude.com/docs/zh-TW/sub-agents#let-subagents-spawn-their-own-subagents)處的子代理的 `Agent`。

省略 `tools` 欄位永遠不會觸發此拒絕。如果您將 `tools` 清單留空，或 `disallowedTools` 移除其中的每個項目，Claude Code 也會跳過拒絕並啟動沒有工具的子代理。 在 v2.1.208 之前，子代理啟動時沒有工具，可能會傳回空的或令人困惑的結果。

```
Agent 'code-reviewer' would be spawned with zero tools — refusing. Its tools list resolved to nothing: unrecognized [Grpe]. Fix the agent's tools frontmatter or pass a different subagent_type.

```

**應該怎麼做：**

- 根據[子代理可用的工具](https://code.claude.com/docs/zh-TW/sub-agents#available-tools)修正錯誤命名的每個項目
- 移除工作階段沒有的工具項目，例如來自未連接伺服器的 MCP 工具
- 對於[背景子代理會捨棄](https://code.claude.com/docs/zh-TW/sub-agents#available-tools)的工具（例如 `LSP`），移除該項目。若要保留該工具，請[關閉 fork 模式](https://code.claude.com/docs/zh-TW/sub-agents#turn-fork-mode-on-or-off)並要求 Claude 在前景中執行子代理
- 刪除 `tools` 欄位而不是列出工具，以給予子代理[子代理可用的每個工具](https://code.claude.com/docs/zh-TW/sub-agents#available-tools)
- 對於只包含 `Agent` 的 `tools` 清單，提高[深度限制](https://code.claude.com/docs/zh-TW/sub-agents#let-subagents-spawn-their-own-subagents)或給予代理至少一個其他工具：Claude Code 在該限制處會拒絕提供 `Agent`，因此只有其他工具的清單會解析為沒有工具

### File is covered by a Read deny rule

Edit 或 Write 工具在由 [`Read` 拒絕規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)符合的路徑上被呼叫，包括在該路徑建立新檔案。兩個工具都會變更 Claude 必須能夠讀回的內容，因此 Claude Code 在任何檔案存取之前拒絕該呼叫。NotebookEdit 不受 `Read` 拒絕規則涵蓋。在 v2.1.228 之前，該規則僅阻止 Edit 工具，在 v2.1.208 之前，只有 `Edit` 拒絕規則會阻止編輯。

```
File is covered by a Read deny rule in your permission settings and cannot be edited.

```

當 Claude Code 拒絕 Write 工具時，訊息結尾改為 `and cannot be written`。 **應該怎麼做：**

- 如果 Claude 應該能夠變更檔案，請在 `/permissions` 或[設定](https://code.claude.com/docs/zh-TW/settings-reference#permission-settings)中移除或縮小 `Read` 拒絕規則
- 如果檔案必須保持未觸及，請保留該規則並為相同路徑新增 `Edit` 拒絕規則以同時阻止 NotebookEdit 工具

### subagent_type is required

```
subagent_type is required: the general-purpose agent is not available in this session. Available agents: ...

```

Claude 呼叫了 [Agent 工具](https://code.claude.com/docs/zh-TW/tools-reference#agent-tool-behavior)但沒有 `subagent_type`，而此工作階段沒有[通用子代理](https://code.claude.com/docs/zh-TW/sub-agents#built-in-subagents)可作為備用。這在兩種設定中是這樣的情況：

- [`CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`](https://code.claude.com/docs/zh-TW/env-vars) 在非互動模式中設定，這會移除每個內建子代理
- 工作階段的主執行緒代理有一個 [`tools: Agent(...)` 允許清單](https://code.claude.com/docs/zh-TW/sub-agents#restrict-which-subagents-can-be-spawned)，其中不包括 `general-purpose`

**應該怎麼做：**

- 通常不需要做任何事：該訊息列出工作階段確實擁有的子代理，因此 Claude 可以使用其中一個重試
- 如果 Claude 持續失敗，請將 `general-purpose` 新增到 `tools: Agent(...)` 允許清單，或取消設定 `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS`

在 v2.1.235 之前，相同的呼叫失敗並顯示 `Agent type 'general-purpose' not found`。

### Memory index is over its read limit

Claude 寫入[自動記憶](https://code.claude.com/docs/zh-TW/memory#auto-memory)索引 `MEMORY.md` 並將其留在其中一個讀取限制之上：200 行或 25KB。寫入成功，但只有前 200 行或 25KB（以先到者為準）在工作階段開始時載入，因此超過限制的所有內容在每次讀取索引時都會被捨棄。在 v2.1.210 之前，超過限制的索引在下次載入時會被無聲地截斷，沒有寫入時間訊號。

```
Error: this write left the memory index at MEMORY.md at 214 lines, over its 200-line read limit. The write succeeded, but everything past the limit is silently dropped each time the index is loaded — entries at the end are already invisible to readers. Rewrite it to under 140 lines now: keep one line per entry, move detail into topic files, and merge or drop stale entries.

```

只有載入的內容才計入限制。YAML frontmatter 和區塊級 HTML 註解在索引載入前會被移除，因此它們被排除在測量之外。在 v2.1.211 之前，Claude Code 測量原始檔案，frontmatter 或註解可能會觸發此錯誤，即使載入的內容符合。 Claude Code 在寫入後將錯誤傳遞給 Claude，而不是在您的終端中列印為橫幅，因此您可能只在文字記錄中注意到它。 當 Claude 的寫入使檔案接近限制但未超過時，Claude Code 會傳回更溫和的提醒以壓縮索引，而不是此錯誤。 **應該怎麼做：**

- 讓 Claude 重寫 `MEMORY.md`，或要求它：每個項目保留一行，將詳細資訊移到主題檔案中，並合併或捨棄過時的項目
- 若要自己修剪索引，請參閱[稽核和編輯您的記憶](https://code.claude.com/docs/zh-TW/memory#audit-and-edit-your-memory)

### pkill pattern matches the Claude Code process

Bash 工具呼叫中的 `pkill` 命令使用了一個模式（通常使用 `-f`），該模式符合 Claude Code 程序本身，因此 Claude Code 拒絕該命令而不是讓它結束工作階段。Claude Code 在執行 `pkill` 之前使用 `pgrep` 測試該模式，並在其自己的程序 ID 在結果中時拒絕。該檢查僅在 Linux 上執行；在 macOS 上，`pkill` 不經修改地執行。在 v2.1.214 之前，該命令執行，符合的模式會在轉換中途殺死 Claude Code 工作階段。

```
pkill: refusing to run — this pattern matches the Claude CLI process (PID 12345). Narrow the pattern, or target your own children with `pkill -P $$ ...`.

```

拒絕出現在 Bash 工具結果中，而不是作為您終端中的橫幅，Claude 通常會自行調整命令。 **應該怎麼做：**

- 縮小模式，使其僅符合預期的程序，例如目標二進位檔的完整路徑而不是短子字串
- 若要停止由目前 shell 啟動的程序，請使用 `pkill -P $$` 搭配模式，這會將符合限制為 shell 自己的子程序

### Failed to write to a teammate’s inbox

Claude Code 無法將訊息寫入 `~/.claude/teams/{team-name}/inboxes/` 下的隊友信箱檔案，因此收件人沒有收到任何內容。當 Claude Code 無法建立或更新檔案時寫入失敗，例如因為磁碟已滿、目錄不可寫，或另一個代理長時間持有收件箱鎖定。在 v2.1.224 之前，Claude Code 即使寫入失敗也會報告訊息已傳送。 該錯誤出現在傳送代理的工具結果中，而不是作為您終端中的橫幅，其文字告訴 Claude 重試：

```
Failed to write to researcher's inbox — nothing was sent. Try again, or message the lead.

```

結構化[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)協議訊息以相同方式失敗，錯誤命名未傳遞的訊息：當 Claude Code 無法寫入計畫核准、計畫拒絕、關閉要求或關閉拒絕時，錯誤讀作 `Failed to write the <message> to <name>'s inbox — nothing was sent`。該清單中的 `plan approval` 是領導者核准隊友計畫的決定；隊友的計畫提交是單獨的 `plan approval request` 訊息。該訊息和另外兩個協議訊息帶有自己的訊息文字和後果：

- `Failed to write the plan approval request to the lead's inbox — plan not submitted; try again`：隊友的計畫從未到達領導者，隊友保持在計畫模式，直到重新提交成功
- `The permission request could not be delivered to the team lead (mailbox write failed)`：隊友的權限要求從未到達領導者，因此沒有人核准工具呼叫
- `The confirmation could not be written to team-lead's inbox.`：關閉核准本身生效，隊友退出；只有對領導者的確認遺失

當您自己訊息隊友時，在領導者工作階段中輸入 `@name` 後跟訊息，相同的失敗會顯示為通知 `Couldn't write to @name's inbox — message not sent. Try again.`，Claude Code 會將您的文字保留在提示框中，以便您可以再次傳送。 **應該怎麼做：**

- 要求傳送者重新傳送訊息；收件箱鎖定的爭用是暫時的，在重試時會清除
- 檢查可用磁碟空間，並檢查 `~/.claude/teams` 及其下的檔案是否可由您的使用者寫入

### Teammate’s agent definition was not restored

Claude 訊息了一個已停止的[代理團隊](https://code.claude.com/docs/zh-TW/agent-teams)隊友，Claude Code 將其恢復而沒有重新應用它生成的[子代理定義](https://code.claude.com/docs/zh-TW/agent-teams#use-subagent-definitions-for-teammates)，因為其定義檔案來自沒有已儲存信任的資料夾。該通知在傳送代理的工具結果中的恢復報告之後：

```
Its agent definition was not restored: the folder its definition file came from is not trusted (source: projectSettings), so the teammate is running with the team-essential tools and no custom instructions. To restore it, the user needs to run Claude Code in that folder once and accept the trust dialog (the --debug log names the folder); do not change trust settings on the user's behalf.

```

該檢查適用於專案的 `.claude/agents/` 目錄或 `--add-dir` 目錄中的定義，接受父資料夾的信任對話不滿足它。 **應該怎麼做：**

- 在[偵錯日誌](https://code.claude.com/docs/zh-TW/debug-your-config)命名的資料夾中執行 `claude` 並接受信任對話。下次 Claude Code 恢復隊友時會重新應用定義；您不需要重新啟動領導者工作階段
- 或在 `~/.claude.json` 中將 `hasTrustDialogAccepted` 項目設定為 `true`，使用偵錯日誌列印的確切 `projects["<path>"]` 鍵

### Message too large for cross-session delivery

Claude 的[跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)到此機器上您的另一個工作階段太長而無法傳送。Claude Code 拒絕了它，接收工作階段沒有收到任何內容。拒絕出現在傳送工作階段的工具結果中，而不是作為您終端中的橫幅。它命名了兩個大小以及如何使訊息符合：

```
Failed to send to api-worker: Message too large for cross-session delivery: the serialized message is 1,203,844 characters and the limit is 1,048,576. Shorten the message text — put bulk content in a file the recipient can read rather than in the message — or split it into smaller messages.

```

重新傳送相同的文字以相同的方式失敗。 **應該怎麼做：**

- 要求 Claude 總結訊息，或將大量內容放在收件人可以讀取的檔案中並傳送檔案的路徑
- 要求 Claude 將內容分割成幾個較短的訊息

在 v2.1.235 之前，Claude Code 報告超大訊息已傳送。接收工作階段未讀就捨棄了它。

### Too many messages to this session just now

Claude 向此機器上您的一個工作階段傳送了快速的[跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)爆發，該爆發達到了該工作階段的收件箱接受的內容。Claude Code 拒絕了下一個傳送，接收工作階段沒有收到任何內容。拒絕出現在傳送工作階段的工具結果中，而不是作為您終端中的橫幅：

```
Failed to send to api-worker: Too many messages to this session just now: 30 were sent recently and more would be dropped by its rate limit, so this one was not sent. Batch what remains into one message, or wait a little before sending more.

```

**應該怎麼做：**

- 通常不需要做任何事：Claude 將剩餘內容批次處理為一個訊息，或在傳送更多內容之前等待
- 如果您自己提示了爆發，請要求 Claude 將剩餘內容合併為單一訊息

在 v2.1.236 之前，Claude Code 報告這些傳送已傳送。接收工作階段未讀就捨棄了它們。

### Refusing to send a cross-session message

在 Claude Code 將[跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging)寫入此機器上您的另一個工作階段之前，它會檢查目標工作階段的收件箱通訊端是否是訊息定址到的端點。當檢查失敗時，Claude Code 在傳送工作階段中拒絕傳送，目標工作階段沒有收到任何內容。對於 Claude 傳送的訊息，拒絕出現在傳送工作階段的工具結果中：

```
Failed to send to api-worker: Refusing to send: reply target is a symlink

```

`Refusing to send:` 之後的文字命名失敗的檢查：

- `reply target is a symlink`：符號連結位於目標工作階段的通訊端路徑。Claude Code 不會透過它傳遞，因為連結可能會將訊息重新導向到目標工作階段未建立的端點。
- `cannot vet reply target`：Claude Code 根本無法檢查目標路徑，例如因為讀取失敗並出現權限錯誤。
- `connected endpoint is not the expected process`：持有通訊端的程序不是訊息定址到的工作階段，因此位址已過時或另一個程序取代了通訊端。
- `connected endpoint identity could not be read`：Claude Code 已連接但無法讀取哪個程序持有另一端，因此無法確認目標。這可能是暫時的。
- `connected endpoint is not owned by this user`：持有通訊端的程序以不同的使用者帳戶執行，因此它不是您的其中一個工作階段。
- `connected endpoint owner could not be read`：Claude Code 已連接但無法讀取哪個使用者帳戶擁有另一端，因此無法確認端點是您的。
- `connected endpoint is a different process with the expected pid`：程序 ID 符合訊息定址到的 ID，但 Claude Code 無法確認它是相同的程序。通常該工作階段已退出，作業系統重新使用了其程序 ID，因此位址已過時。

**應該怎麼做：**

- 通常不需要做任何事：檢查會防止訊息到達定址到的工作階段以外的端點，沒有傳送任何內容
- 要求 Claude 再次列出您的工作階段並重新傳送；由過時位址引起的拒絕在 Claude 傳送到目前的工作階段後會清除
- 如果 `reply target is a symlink` 對一個工作階段重複，請檢查在該工作階段的通訊端路徑建立連結的內容，顯示在其 `/status` 下的 `Peer address`
- 對於 `connected endpoint identity could not be read`，重新傳送；該條件可能是暫時的
- 如果 `connected endpoint is not owned by this user` 出現在共用機器上，該位址處的工作階段以另一個使用者的帳戶執行，因此 Claude 無法從您的帳戶訊息它

在 v2.1.248 之前，Claude Code 沒有檢查端點的擁有使用者或程序啟動時間，因此命名這些檢查的拒絕不會出現在較早的版本上。

### Refusing to read, write, or search a path

Claude Code 檢查檔案路徑的[權限規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)，然後在工具開啟檔案或啟動搜尋時再次確認該解析。當它無法確認路徑仍然導向檢查核准的位置時，Claude Code 拒絕該操作而不是跟隨它。拒絕出現在工具結果中：

```
Refusing to read /path/to/file: its symlink resolution changed after permission was checked (a link on the way now leads somewhere the check did not see). If a link in the working directory is being rewritten concurrently, stop that and retry.

```

每個拒絕命名其原因：

- `its symlink resolution changed after permission was checked`：路徑上的符號連結或 Grep 或 Glob 搜尋根目錄在權限檢查和操作之間被取代。在讀取拒絕中，括號中的短語命名哪個比較失敗。
- `its parent-directory symlink resolution changed after permission was checked`：寫入路徑通過的目錄不再解析為核准的位置
- `it is a symbolic link. Write to the link's target path instead`：符號連結位於核准的寫入位置本身，例如 `CLAUDE.md` 是 `AGENTS.md` 的符號連結；訊息指導 Claude 到連結的目標
- `Refusing to write through symlink: <path>. Resolve the symlink and pass the real target path explicitly.`：相同的條件在另一個寫入器開啟檔案時被捕捉，例如寫入符號連結的 `.mcp.json`
- `Refusing to write into symlinked directory: <path>`：持有檔案的目錄本身是符號連結，例如專案的 `.claude/` 目錄連結到另一個位置
- `a path one of its Read deny rules is written through changed while the search was being prepared. Retry.`：搜尋的 `Read` 拒絕規則命名通過符號連結的路徑，該連結在 Claude Code 準備搜尋時變更
- `it could not be opened (EACCES) — it is unreadable, or is being replaced concurrently.`：搜尋根目錄存在但無法開啟；括號中的代碼是作業系統錯誤
- `its permission check expired before it ran (too many concurrent file operations). Retry.`：Claude Code 在許多同時檔案操作下驅逐了核准記錄，然後工具使用它；重試執行新的權限檢查
- `ripgrep was found only by name on PATH, and a search outside the working directory cannot apply your Read deny rules in that configuration`：Claude Code 無法將 `rg` 二進位檔解析為絕對路徑，因此它拒絕在工作目錄外的搜尋，而不是執行您的拒絕規則不涵蓋的搜尋

**應該怎麼做：**

- 通常不需要做任何事：拒絕到達 Claude 作為工具結果，被拒絕的操作不執行
- 如果符號連結拒絕在一個路徑上重複，請找到持續重寫連結的內容，例如建置工具或檔案監視程式，或要求 Claude 使用檔案的已解析路徑而不是連結的路徑
- 如果此拒絕在 Windows 上的 AppContainer 或受限權杖沙箱內執行 Claude Code 時出現在每個檔案上，請升級到 v2.1.265 或更新版本
- 如果讀取拒絕在 macOS 上出現在沒有任何內容重寫的檔案上，例如拖入提示的螢幕擷取畫面，請升級到 v2.1.273 或更新版本
- 對於 ripgrep 拒絕，使用您的套件管理員安裝 ripgrep，以便 `rg` 在 `PATH` 上解析為絕對路徑，或將搜尋保留在工作目錄下

在 v2.1.251 之前，Claude Code 僅對檔案寫入重新檢查路徑的解析，因此在權限檢查後取代的連結可能會將讀取或搜尋重新導向到不同的位置，沒有訊息。在這些拒絕中，只有父目錄、透過符號連結和符號連結目錄寫入拒絕出現在較早的版本上。

### Task output swap refused

Claude Code 將每個 Bash 命令的輸出儲存到其暫存目錄下的檔案。每次它開啟其中一個檔案時，它都會檢查路徑是否仍然導向它建立的檔案，沒有符號連結、額外硬連結或移動的目錄重新導向它。此訊息表示該檢查失敗，因此 Claude Code 拒絕了該操作，而不是透過該路徑寫入或讀取輸出。該訊息出現在 Bash 工具結果中：

```
task output swap refused (tasks dir moved or linked): /private/tmp/claude-501/-Users-you-my-project/1f0e62dc-4b0a-4f5e-9c2d-8a7b6c5d4e3f/tasks/b7k2f9m3q.output. To recover: restart Claude Code with CLAUDE_CODE_TMPDIR set to a fresh directory; or, if /private/tmp/claude-501/-Users-you-my-project is a stray directory or a symbolic link that should not be there, remove that entry itself (not what it points to) and restart.

```

括號中的文字命名失敗的檢查。原因例如 `output symlink was re-pointed`、`output file identity changed` 和 `not a regular file` 都報告相同的條件：輸出路徑上或沿著的某些內容不再是 Claude Code 建立的檔案。只有某些原因帶有 `To recover:` 句子。 如果檢查在命令仍在執行時失敗，Claude Code 會停止命令，其結果報告：

```
Command killed: its output file was replaced or could no longer be verified

```

**應該怎麼做：**

- 升級到 v2.1.260 或更新版本。較早的版本有時在沒有連結或移動目錄存在時顯示此訊息
- 使用設定為新目錄的 [`CLAUDE_CODE_TMPDIR`](https://code.claude.com/docs/zh-TW/env-vars) 重新啟動 Claude Code
- 或檢查 Claude Code 暫存目錄下的專案目錄，範例訊息中的 `/private/tmp/claude-501/-Users-you-my-project`。如果該路徑是符號連結，或不應該存在的目錄，請移除連結或目錄本身而不是連結的目標，然後重新啟動 Claude Code
- 如果拒絕重複，程序在工作階段執行時會取代、連結或移除 Claude Code 暫存目錄下的項目。將 [`CLAUDE_CODE_TMPDIR`](https://code.claude.com/docs/zh-TW/env-vars) 設定為沒有其他內容管理的目錄並重新啟動

### The source file is not valid UTF-8 text

Claude 嘗試從位元組不解碼為文字的檔案發佈[成品](https://code.claude.com/docs/zh-TW/artifacts)，或其文字已包含替換字元 `U+FFFD`，因此 Claude Code 在上傳任何內容之前拒絕發佈。該訊息出現在成品工具結果中，並命名要修正的第一個位置：

```
file_path: the source file is not valid UTF-8 text (first invalid byte at line 12, column 40). It may be saved in another encoding or contain binary data. Rewrite it as UTF-8, then publish again. Nothing was published.

file_path: the source file has the replacement character U+FFFD at line 12, column 40, usually left where an earlier edit or paste lost a character. Replace it with the intended text (in HTML, write an intended U+FFFD as &#xFFFD;), then publish again. Nothing was published.

```

Claude Code 將檔案解碼為 UTF-8，或當它以小端 UTF-16 位元組順序標記開頭時解碼為 UTF-16。當這樣的 UTF-16 檔案無法解碼時，第一個訊息命名 `UTF-16` 並仍然告訴您將檔案重寫為 UTF-8。當更多位置跟隨命名的位置時，訊息在位置之後新增計數，例如 `(+2 more)`。 **應該怎麼做：**

- 通常不需要做任何事：Claude 重寫檔案並再次發佈
- 如果檔案是您寫入或匯出的，請再次將其儲存為 UTF-8，並將每個 `U+FFFD` 取代為較早的編輯、貼上或轉換遺失的字元
- 若要在頁面上顯示有意的 `U+FFFD`，請在 HTML 中將其寫為 `&#xFFFD;` 而不是字面字元

在 v2.1.267 之前，Claude Code 上傳這樣的檔案而不檢查它，伺服器改為拒絕發佈。

### Reading a local file from outside the connected folders in a Cowork session

在 Claude Desktop 應用程式中在您的機器上執行的 [Cowork](https://claude.com/docs/cowork/overview) 工作階段中，Claude 為[成品](https://code.claude.com/docs/zh-TW/artifacts)命名了本機檔案。Claude Code 無法確認檔案是工作階段連接資料夾內的純檔案：路徑位於這些資料夾外、通過符號連結或以可能命名不同檔案的方式拼寫。讀取這樣的檔案需要您的核准，在無法向您顯示核准卡的工作階段中，例如設定為跳過所有核准的工作階段，Claude Code 拒絕讀取。 拒絕出現在成品工具結果中；當檔案根本無法檢查時，它改為命名該失敗：

```
Reading a local file from outside this session's connected folders, or through a link, needs the approval card, and no one can answer it in this Cowork session. Use a plain file inside the connected folders; do not retry this file in this session.

cannot read file_path (ENOENT) — the file could not be examined, and no one can answer the approval card in this Cowork session. Check that the file exists as a plain file inside the connected folders, then retry with that path.

```

**應該怎麼做：**

- 通常不需要做任何事：訊息告訴 Claude 改為使用連接資料夾內的純檔案
- 若要將該確切檔案放在成品中，請將其複製到工作階段的其中一個連接資料夾中作為常規檔案（不是符號連結），然後再次詢問

### WebFetch cannot fetch localhost

Claude 呼叫了 [WebFetch](https://code.claude.com/docs/zh-TW/tools-reference#webfetch-tool-behavior)，其 URL 的主機名沒有點，例如 `http://localhost:3000` 或裸內部網路名稱如 `http://wiki/`。WebFetch 在進行任何要求之前拒絕這些 URL：

```
WebFetch cannot fetch localhost or other hostnames without a dot. To reach a local server, use Bash with curl instead.

```

**應該怎麼做：**

- 通常不需要做任何事：訊息將 Claude 指向透過 Bash 工具的 `curl`，它可以到達本機和內部網路伺服器

在 v2.1.268 之前，WebFetch 使用通用 `Invalid URL` 錯誤報告這些 URL。

## 背景工作階段錯誤

[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)在沒有互動式終端的情況下執行，因此需要終端的命令在那裡的行為會有所不同。這些訊息會出現在背景工作階段的文字記錄中、附加到背景工作階段的終端中、您分派的工作階段或殼層中，或者對於下面的[worktree-guard 項目](https://code.claude.com/docs/zh-TW/errors#write-or-command-blocked-because-the-path-cannot-be-safely-resolved)，會出現在任何在 worktree 中隔離或執行 worktree 隔離子代理的工作階段中；當訊息特定於某個表面時，其項目會說明。

### 在背景工作階段中拒絕的命令

開啟互動式對話框的命令在沒有終端附加到背景工作階段時無法執行。`/install-github-app`、`/mcp` 設定清單和 MCP 伺服器選單中的驗證動作會回應一則訊息，工作階段會在[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)中的 **Needs input** 下出現，以便您可以找到它、附加並再次執行命令。當終端附加時，這些命令正常運作。 在 v2.1.216 之前，工作階段在其中一個拒絕後不會在 **Needs input** 下出現。在 v2.1.213 到 v2.1.215 中，命令在附加終端時仍然有效，拒絕訊息告訴您附加並再次執行命令。從 v2.1.208 到 v2.1.212，Claude Code 即使在附加終端時也拒絕它們，訊息如 `Can't open MCP settings in a background session`；在這些版本上，改為從常規 `claude` 工作階段執行命令，或升級。在 v2.1.208 之前，它們在背景工作階段內開啟其對話框。在 v2.1.208 中，Claude Code 也拒絕了背景工作階段中的 `/model` 選擇器，`/upgrade` 列印升級 URL 而不是開啟瀏覽器。 措辭會命名該命令。`/mcp` 設定清單報告：

```
Can't open MCP settings while no terminal is attached to this background session. This session now shows "needs input" in agent view — open it and run /mcp to manage servers, or use `/mcp enable|disable|reconnect <server>` to steer without the panel.

```

**該怎麼做：**

- 從代理檢視附加到工作階段，其中它列在 **Needs input** 下，並再次執行命令
- 或使用訊息命名的形式，例如 `/mcp reconnect <server>`、`/mcp enable` 或 `/mcp disable`，這些在不附加的情況下有效

### 寫入或命令被阻止，因為路徑無法安全解析

Claude 透過 [worktree 隔離防護](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated)無法解析為一個可驗證位置的拼寫來定址檔案或工作目錄。防護檢查[任何在 worktree 中隔離的工作階段](https://code.claude.com/docs/zh-TW/worktrees#how-claude-code-enforces-isolation)中的寫入和命令工作目錄，互動式或背景，以及[worktree 隔離子代理](https://code.claude.com/docs/zh-TW/worktrees#isolate-subagents-with-worktrees)中的寫入和命令工作目錄。它在檢查操作不會到達共享簽出之前解析符號連結，當解析失敗時，它會阻止操作而不是讓它落在那裡。訊息命名它拒絕的路徑形式以及如何重試：

```
This write was blocked because the path is spelled in a form that cannot be safely resolved (for example through a symlink storing a raw dot segment, a network-share or device-namespace shape, or an unreadable ancestor directory). If the file is inside the worktree /path/to/worktree, address it by its direct symlink-free path instead.

```

被阻止的命令報告其工作目錄的相同原因，並以 `re-run the command from its direct symlink-free path` 結尾。在 v2.1.217 之前，防護比較路徑拼寫而不解析符號連結，因此這些拼寫未被阻止，透過符號連結路由的寫入可能會落在共享簽出中。 **該怎麼做：**

- 通常什麼都不做：完整訊息作為工具錯誤傳遞給 Claude，Claude 使用它命名的直接路徑重試。對於被阻止的檔案編輯，對話檢視只顯示簡短的 `Error editing file` 行；完整訊息出現在文字記錄檢視中，您可以使用 `Ctrl+O` 開啟。被阻止的命令在其命令輸出中列印它。
- 如果同一檔案上的阻止重複，路徑可能透過已提交的符號連結執行，其目標包含 `..`，例如 `docs/current -> ../README.md`；要求 Claude 透過其真實路徑編輯目標檔案，而不是透過連結

### 寫入或命令被阻止，因為路徑命名網路位置

Claude 透過命名不在您機器上的磁碟機、UNC 共享（例如 `\\server\share\file`）或 `/net` 自動掛載路徑的路徑來定址檔案或工作目錄，而工作階段的簽出在本機磁碟上。相同的 [worktree 隔離防護](https://code.claude.com/docs/zh-TW/errors#write-or-command-blocked-because-the-path-cannot-be-safely-resolved)無法驗證這樣的路徑保持在共享簽出之外，因此它會阻止操作。在 worktree 中隔離工作階段不會解除阻止。訊息命名要改用的路徑形式：

```
This write was blocked because the path is network-shaped (a UNC share or /net automount spelling) while this session's checkout is local. Isolating cannot unblock it. If the file is genuinely inside the worktree /path/to/worktree, address it by its local, plainly-spelled path instead.

```

被阻止的命令報告其工作目錄的相同原因，並以 `re-run the command from its local, plainly-spelled path` 結尾。在 v2.1.217 之前，防護只比較路徑文字，因此透過 UNC 或 `/net` 路徑定址簽出內的檔案未被阻止。 **該怎麼做：**

- 通常什麼都不做：Claude 使用訊息要求的本機拼寫重試
- 如果檔案在網路共享上而不是用網路路徑拼寫的本機檔案，它在工作階段的本機工作區之外；改為從常規互動式工作階段編輯它

### 此工作階段沒有已儲存的文字記錄

您附加到已停止的[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)，該工作階段使用 `←` 或 `/background` 從另一個對話背景化，並在其第一個回應完成之前停止。在該第一個回應完成之前，對話仍然只存在於背景化它的工作階段中，因此 `claude attach` 拒絕啟動已停止的工作階段，而不是在相同工作階段 ID 下開始空白對話。訊息以此工作階段的 `claude respawn` 命令結尾：

```
This session has no saved transcript — it was stopped before its first response finished. If it was backgrounded from another conversation, that one is still intact; `claude respawn <id>` starts this one fresh.

```

在[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)中開啟相同工作階段的列在清單下方顯示 `Press enter again to restart this session fresh`，列上的第二個 `Enter` 使用空白對話重新啟動工作階段。在 v2.1.212 之前，開啟列顯示拒絕訊息，無法從代理檢視重新啟動。在 v2.1.211 之前，開啟已停止的工作階段無聲地啟動該空白對話，並可以重新執行工作階段的原始提示。 **該怎麼做：**

- 您背景化的對話完整無缺：使用 [`claude --resume`](https://code.claude.com/docs/zh-TW/sessions) 繼續它或繼續在其中工作
- 要無論如何啟動已停止的工作階段，請使用訊息中的 ID 執行 `claude respawn <id>`，或在代理檢視中的其列上按 `Enter` 兩次
- 如果工作階段確實完成了回應，您仍在 v2.1.214 之前的版本上看到此拒絕，`~/.claude/projects` 中的不可讀資料夾可能會使文字記錄掃描遺漏已儲存的對話；更新到 v2.1.214 或更新版本，其在掃描期間容許不可讀資料夾

### 此工作階段在另一個終端中執行

您在[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)中開啟了已停止工作階段的列，其已儲存的對話已在此機器上的另一個即時 Claude Code 程序中開啟，因此 Claude Code 拒絕啟動將寫入相同文字記錄的第二個程序。您看到的訊息取決於[什麼保持對話](https://code.claude.com/docs/zh-TW/agent-view#opening-a-session-says-the-conversation-is-already-open)：

```
Can't open — this session is running in another terminal
This conversation is already open in another running Claude session — use that one, or close it and try again

```

- **`running in another terminal`**：終端保持對話，例如您使用`claude --resume` 或 `/resume` 繼續它的終端。列也顯示 `Open in a terminal`。
- **`already open in another running Claude session`**：另一個非互動式 Claude Code 程序保持它，例如相同對話的[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)程序，尚未退出。

Claude Code 儲存您在開啟列時輸入的回覆，並在工作階段下次啟動時將其作為工作階段的下一個提示傳送。 **該怎麼做：**

- 在保持它開啟的程序中繼續對話，或退出該程序並再次開啟列

在 v2.1.248 之前，只有 `already open in another running Claude session` 拒絕存在：在終端中繼續的對話不計為開啟，開啟列啟動寫入相同對話的第二個 Claude Code 程序。

### 此工作階段的已儲存對話不再在磁碟上

您開啟了在背景服務關閉時結束的[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)，[文字記錄清理](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)已移除其已儲存的對話，例如在機器關閉數週後。通常開啟這樣的列會[繼續其已儲存的對話](https://code.claude.com/docs/zh-TW/agent-view#sessions-show-as-failed-after-shutdown)。沒有什麼可繼續，Claude Code 拒絕而不是在不詢問的情況下重新執行工作階段的原始提示：

```
This session's saved conversation is no longer on disk (it ended while the background service was off, and old transcripts are cleaned up), so there is nothing to resume. `claude rm 7c5dcf5d` deletes the row; `claude respawn 7c5dcf5d` runs its original prompt again instead.

```

`claude attach <id>` 列印此文字。在代理檢視中，頁腳較短，以 `ctrl+x deletes the row` 結尾。 **該怎麼做：**

- 執行 `claude rm <id>` 刪除列。當其中一個[保留案例](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)適用時，`claude rm` 保留列和 worktree，並命名原因
- 要再次執行工作階段的原始提示作為新對話，請執行 `claude respawn <id>`

在 v2.1.248 之前，開啟這樣的列會重新執行工作階段的原始提示，而不是拒絕，將數週前的任務拉回前景。

### Worktree 有未推送到任何地方的提交

您嘗試刪除[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view#what-deleting-a-session-removes)，其 worktree 保持 Claude Code 無法確認在其他地方儲存的提交。Claude Code 保留 worktree 和工作階段列，而不是銷毀提交。`claude rm` 命名分支和未推送的提交，並說明如何進行：

```
kept 7c5dcf5d — its worktree is still at "/home/you/project/.claude/worktrees/fix-login"
  2 unpushed commits on "claude/fix-login": a1b2c3d "Fix login flow" and 1 more. They exist on no remote, so deleting the worktree would lose them.
  push them and run 'claude rm 7c5dcf5d' again, or discard the worktree and its commits: claude rm 7c5dcf5d --discard-unpushed a1b2c3d000000000000000000000000000000000@0123456789abcdef0123456789abcdef

```

當 Claude Code 無法總結提交時，詳細行讀取 `The worktree has unpushed commits`。在[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)中，工作階段的列顯示 `not deleted`，原因相同。 遠端上的提交不會阻止刪除。本機複製您的 `origin` 遠端預設分支上的提交也不會，只要該分支在您的主簽出中簽出，即儲存庫目錄本身而不是 worktree。 **該怎麼做：**

- 要保留提交，推送 worktree 的分支，或將其合併到在主簽出中簽出的預設分支，然後再次刪除工作階段
- 要捨棄提交，執行訊息列印的 `claude rm <id> --discard-unpushed` 命令，或在代理檢視中的工作階段列上再次按 `Ctrl+X` 兩次。這會移除工作階段和 worktree 以及其分支、未推送的提交和任何未提交的變更。如果 worktree 自拒絕以來獲得了提交，Claude Code 再次保留它並顯示更新的狀態
- 當訊息說 worktree 也由另一個已完成的工作階段記錄時，再次刪除不會捨棄它：推送提交，然後再次刪除工作階段

在 v2.1.268 之前，`claude rm` 將提交摘要放在 `kept` 行本身上。當 `claude rm` 無法總結提交時，`kept` 行讀取 `worktree has commits that are not pushed anywhere` 代替摘要。 在 v2.1.260 之前，訊息未命名分支或提交，再次刪除被拒絕的方式相同：刪除工作階段而不推送意味著使用 `git worktree remove --force <path>` 自己移除 worktree，然後再次執行 `claude rm <id>`。 在 v2.1.248 之前，在主簽出中簽出的預設分支不計算：您已經合併到那裡的分支仍然觸發此拒絕，直到其提交到達遠端。

### 終端主機程序已死亡

每個[背景工作階段的](https://code.claude.com/docs/zh-TW/agent-view)終端在背景服務下的主機程序中執行，該程序在服務仍保持其連線時死亡，因此無法到達工作階段。 在 Linux 和 WSL 上，背景服務每隔幾秒檢查每個主機程序，當程序已退出但其與服務的連線從未關閉時標記工作階段失敗，並在[代理檢視](https://code.claude.com/docs/zh-TW/agent-view#read-session-state)中的其列上顯示原因：

```
terminal host process died — press Enter to restart

```

如果您在檢查執行之前開啟列，頁腳顯示 `This session's terminal host process died (the conversation is saved) — press Enter to restart it`，列變為失敗。 從殼層，`claude attach <id>` 重新啟動已標記為死主機失敗的工作階段，否則列印原因並退出：

```
Couldn't attach to <id> — This session's terminal host process died (the conversation is saved) — run `claude attach <id>` again to restart it on a fresh host.

```

無論如何對話都會儲存。 執行[殼層命令](https://code.claude.com/docs/zh-TW/agent-view#run-a-shell-command)的列改為顯示 `terminal host process died — its output is gone; the command was not run again`，`claude attach` 列印 `This command's terminal host process died — its output is gone and the command was not run again`。Claude Code 永遠不會為您重新執行命令。 **該怎麼做：**

- 在代理檢視中，在失敗的列上按 `Enter`；工作階段在新主機程序上重新啟動，對話繼續
- 從殼層，再次執行 `claude attach <id>`。Claude Code 列印 `Session <id>'s terminal host died — restarting it on a fresh one…` 並重新開啟工作階段
- 您無法以這種方式重新啟動殼層命令列；再次分派命令以重新執行它

在 v2.1.247 之前，死主機程序可能通過背景服務執行的每個活躍性檢查，因此開啟工作階段無限期地顯示 `opening… · esc to cancel`，`claude attach <id>` 等待而不報告錯誤。

### 工作階段沒有回應

您開啟了[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)，背景服務接受了開啟，但約十秒內沒有輸出到達，因此 Claude Code 得出結論，中繼工作階段終端的程序無法傳遞輸出，並結束嘗試而不是等待。 在代理檢視中，Claude Code 在頁腳中提供重新啟動：

```
Press enter again to restart this session — it isn't responding (its conversation is saved and resumes).

```

從殼層，`claude attach <id>` 列印原因並退出：

```
Couldn't attach to <id> — Session isn't responding — `claude stop <id>`, then `claude attach <id>` restarts it (the conversation is saved).

```

Claude Code 永遠不會為您重新啟動執行[殼層命令](https://code.claude.com/docs/zh-TW/agent-view#run-a-shell-command)的列，因為重新啟動會再次執行命令。 **該怎麼做：**

- 在代理檢視中，在相同列上再次按 `Enter`。Claude Code 停止無回應的程序並重新啟動工作階段，對話繼續。沒有第二次按下，什麼都不會停止
- 從殼層，執行 `claude stop <id>`，然後 `claude attach <id>`
- 對於殼層命令列，在代理檢視中按 `Ctrl+X` 或執行 `claude stop <id>` 停止它；再次分派命令以重新執行它

### 工作階段在重新生成進行中時被停止

您開啟了[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)，其程序未執行，當 Claude Code 重新啟動它時，另一個 Claude Code 程序停止了它，例如在另一個終端中的 `claude stop`。Claude Code 保持工作階段停止：

```
Session <id> was stopped while the respawn was in flight

```

開啟您剛分派的工作階段，當其程序仍在啟動時，等待程序。在 v2.1.246 之前，在那一刻開啟它可能會停止它並顯示此訊息。 **該怎麼做：**

- 如果您沒有停止工作階段，在代理檢視中再次開啟其列或執行 `claude respawn <id>` 重新啟動它
- 如果您自己停止了它，沒有什麼剩下要做的：工作階段保持停止

### 工作階段代理不再可用

您繼續了執行[自訂代理](https://code.claude.com/docs/zh-TW/sub-agents#invoke-subagents-explicitly)的工作階段，使用 `--agent` 或 `agent` 設定啟動，Claude Code 未找到該名稱的代理。它首先搜索工作階段的原始目錄，當您[信任該工作區](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)時，然後搜索您繼續的目錄。工作階段仍然繼續，但使用預設工具，因此代理的工具限制不再適用：

```
This session was running agent 'code-reviewer', which is no longer available (no agent by that name in /home/you/project). Continuing with the default tools and system prompt — the agent's tool restrictions no longer apply. To restore it, re-create the agent, or resume with an explicit --agent <name>.

```

訊息只命名 Claude Code 搜索的目錄，無論您喚醒[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)、執行 `/resume` 或 `claude --resume`，還是在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中繼續，它都會出現在繼續的對話中，它也會進入 stderr。使用 `--input-format stream-json` 的工作階段不顯示它，因為 Agent SDK 在啟動後提供代理。 Claude Code 不會將回退儲存到工作階段，因此警告在每次繼續時重複，直到您採取行動。內建 `claude` 代理不觸發警告，因為回退到預設工具集對它沒有變化。在 v2.1.216 之前，Claude Code 無聲地繼續作為預設代理，查詢僅涵蓋您繼續的目錄，因此專案範圍的代理在從另一個目錄繼續時丟失。 **該怎麼做：**

- 在工作階段的專案中的 `.claude/agents/<name>.md` 或個人代理的 `~/.claude/agents/<name>.md` 重新建立代理檔案，然後再次繼續
- 或使用 `--agent <name>` 繼續，命名確實存在的代理，以改為作為該代理執行工作階段
- 如果代理是專案範圍的，您尚未信任工作階段的原始目錄，請在那裡執行 Claude Code 一次，接受信任對話，然後再次繼續

### CLAUDE_CODE_PROCESS_WRAPPER 啟動器錯誤

[`CLAUDE_CODE_PROCESS_WRAPPER`](https://code.claude.com/docs/zh-TW/corporate-launcher)已設定，其值無法使用，因此 Claude Code 拒絕啟動受影響的程序，而不是在沒有啟動器的情況下執行它。配置問題報告為以變數名稱開頭並說明原因的訊息，例如：

```
CLAUDE_CODE_PROCESS_WRAPPER: launcher `/opt/corp/launcher` is not an executable regular file

```

啟動但在不用 Claude Code 替換自己的情況下退出的啟動器會使其啟動的工作階段失敗，工作階段在代理檢視中的列報告啟動器 `must exec, not daemonize`，後跟啟動器列印的任何內容。無法啟動或到達背景服務的工作階段因啟動器報告啟動器問題作為 `Couldn't reach the background service (...)` 內的原因。 **該怎麼做：**

- 將變數設定為以呼叫 `exec "$@"` 結尾的可執行檔的絕對路徑。有關完整合約，請參閱[啟動器合約](https://code.claude.com/docs/zh-TW/corporate-launcher#the-launcher-contract)
- 檢查 `/status`，其在 Self-exec 項中顯示已解析的啟動命令，並在執行中的背景服務不符合時警告，或從殼層執行 `claude daemon status`
- 在[設定](https://code.claude.com/docs/zh-TW/corporate-launcher#set-up-the-launcher)的 `env` 區塊中修復值後，使用 `claude daemon stop --any` 重新啟動背景服務，以便下次分派啟動包裝的服務

### 啟動背景工作階段時 EUNKNOWN

Windows 拒絕使用沒有標準名稱的錯誤代碼啟動程式，因此失敗表現為 `EUNKNOWN`。通常的觸發器是軟體限制原則，例如群組原則或 AppLocker，阻止正在啟動的程式。當您使用 `/background` 或 `claude --bg` 啟動[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)時，錯誤出現：

```
Couldn't reach the background service (spawn background service: EUNKNOWN: unknown error, uv_spawn) — run 'claude daemon status'

```

在某些帳戶上，訊息在 `daemon` 位置說 `background service`。 在 npm 安裝上，在 `npm install -g @anthropic-ai/claude-code` 替換二進位檔案時出現的 `EUNKNOWN` 與[重新安裝期間的 `EACCES`](https://code.claude.com/docs/zh-TW/errors#eacces-when-starting-a-background-session) 有相同的原因，並在您在安裝完成後重試時清除。 Claude Code 透過 PowerShell 啟動背景服務，以便服務在關閉終端時存活，在安裝時使用 PowerShell 7，否則使用 Windows PowerShell 5.1。當兩個 PowerShell 都無法執行時，Claude Code 改為直接啟動服務，因此只阻止 PowerShell 的原則不會導致此錯誤。如果您在沒有 npm 安裝執行時看到它，原則會阻止 Claude Code 可執行檔本身。 在 v2.1.212 之前，Claude Code 僅使用 Windows PowerShell 5.1 啟動服務，因此任何群組原則阻止 PowerShell 5.1 的機器失敗，訊息為 `Couldn't start the session — EUNKNOWN: unknown error, uv_spawn`，即使安裝了 PowerShell 7。 **該怎麼做：**

- 如果訊息讀取 `Couldn't start the session`，升級到 v2.1.212 或更新版本。在較早的版本上，您也可以在單獨的終端中首先執行 `claude daemon run`，然後再次啟動背景工作階段。該命令在終端的前景中執行背景服務，因此服務僅在該終端保持開啟時持續。
- 如果 npm 安裝正在替換二進位檔案，等待它完成，然後再次啟動背景工作階段
- 如果錯誤在 v2.1.212 或更新版本上出現，沒有 npm 安裝執行，請要求您的 Windows 管理員在限制原則中允許 Claude Code 可執行檔
- 如果關閉終端時背景服務停止，Claude Code 在沒有 PowerShell 的情況下啟動它。安裝 PowerShell 7，或要求您的管理員解除阻止 PowerShell，以便服務可以超越終端。

### 啟動背景工作階段時 EACCES

Claude Code 無法執行其自己的二進位檔案來啟動[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)，該服務託管背景工作階段。在 npm 安裝上，這通常意味著 `npm install -g @anthropic-ai/claude-code` 在那一刻替換二進位檔案，無論您執行它還是[自動更新程式](https://code.claude.com/docs/zh-TW/setup#auto-updates)執行。當您從[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)開啟工作階段時，錯誤出現：

```
Couldn't start the background service — spawn background service: EACCES: permission denied, posix_spawn '/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude'

```

當您使用 `/background` 或 `claude --bg` 啟動工作階段時，相同的原因出現在 `Couldn't reach the background service (...)` 內。在相同重新安裝視窗期間，錯誤可能命名另一個代碼，例如 `ENOENT` 或 `ENOEXEC`，或 Windows 上的 `EUNKNOWN` 或 `EPERM`；跨重試持續的 `EUNKNOWN` 有[不同的原因](https://code.claude.com/docs/zh-TW/errors#eunknown-when-starting-a-background-session)。 在 npm 安裝上，Claude Code 等待重新安裝完成並自動重試：最多十秒，以及在 npm 安裝 Claude Code 在機器上明顯仍在執行時最多兩分鐘，涵蓋另一個 Claude Code 程序下載更新。當安裝超過該等待時，失敗命名更新而不是裸錯誤代碼：

```
Claude Code is being updated by npm on this machine (still not runnable after 2 min, EACCES) — try again when the update finishes

```

在 v2.1.257 之前，等待在每種情況下停止在十秒，因此此錯誤在另一個 Claude Code 程序仍在下載更新時出現。在 v2.1.246 之前，Claude Code 立即失敗，沒有等待。 **該怎麼做：**

- 等待幾秒，然後開啟工作階段或再次分派。當訊息說 Claude Code 正在更新時，在更新完成後重試。
- 如果錯誤在沒有 npm 安裝執行時持續，您的使用者無法執行已安裝的二進位檔案。檢查其權限及其目錄的，或重新安裝 Claude Code。

### 背景服務在變得可到達之前退出

Claude Code 啟動為[背景服務](https://code.claude.com/docs/zh-TW/agent-view#the-supervisor-process)的程序在變得可到達之前退出，因此 Claude Code 無法開啟您的工作階段。當服務在退出前列印錯誤時，括號中的原因給出退出代碼或訊號以及服務列印的第一行，其命名停止它的內容：

```
Couldn't reach the background service (background service exited before it became reachable (exit code N): <the service's first error line>) — run 'claude daemon status'

```

當您從[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)開啟工作階段時，相同的原因跟隨 `Couldn't start the background service —`。當服務在退出前未列印任何內容時，訊息改為說 `nothing on stderr`。 Claude Code 使用服務的錯誤行報告失敗。在 v2.1.246 之前，失敗僅在 45 秒等待後表現，為 `background service did not become reachable within 45s`，沒有服務的錯誤行。 兩個引用的原因有已知的原因：

- `Error: claude native binary not installed.`：npm 安裝在那一刻替換 Claude Code 二進位檔案，因此服務執行 npm 的佔位符。在安裝完成後重試；如果沒有安裝執行時行持續，[完成 npm 安裝](https://code.claude.com/docs/zh-TW/troubleshoot-install#native-binary-not-found-after-npm-install)。在 v2.1.257 之前，macOS npm 自我更新在安裝視窗期間在每次啟動時產生此失敗。
- Windows 上每次啟動時 `nothing on stderr` 和退出代碼 1：`daemon.lock` 命名 Claude Code 既無法訊號也無法證明已消失的程序，因此每個新服務得出結論另一個保持鎖定並退出。Claude Code 可以證明其寫入器已消失的鎖定會自動替換，不會產生此失敗。當失敗在每次啟動時重複時，刪除 `~/.claude/daemon.lock`，然後開啟工作階段或再次分派。在 v2.1.257 之前，這樣的鎖定阻止每次啟動，直到您刪除檔案。

**該怎麼做：**

- 如果訊息引用一行，修復它命名的內容，然後開啟工作階段或再次分派。下次嘗試再次啟動服務
- 執行 `claude daemon status` 檢查現在是否有服務執行

### 啟動背景工作階段時工作目錄不再存在

您嘗試在不再存在的目錄中啟動[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)。當您從代理檢視分派或在您工作的目錄被刪除或移動後執行 `/background` 時，會發生這種情況。當您附加到或重新啟動其程序已退出且其目錄已消失的工作階段時，也會發生這種情況，因為新程序會在相同目錄中啟動。Claude Code 不啟動工作階段，訊息命名遺漏的目錄：

```
Couldn't start a background session (working directory no longer exists or is not accessible: /tmp/demo)

```

在 v2.1.257 之前，工作階段似乎啟動，然後在代理檢視中顯示為失敗列，原因相同。 **該怎麼做：**

- 重新建立訊息命名的目錄，或從存在的目錄分派，然後再試一次

## 包裝程式和 IDE 錯誤

這些錯誤來自啟動 Claude Code 的程式，例如 IDE 擴充功能或 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 應用程式，而不是來自 Claude Code 本身。

### Claude Code 程序以代碼 N 結束

底層 `claude` 程序以非零代碼結束。結束代碼本身不會說明失敗的原因：真正的錯誤在於程序自己的輸出，包裝程式會在捕獲時附加該輸出，否則將其保留在日誌中。

```
Error: Claude Code process exited with code 1

```

在 Windows 上，原生組建可能在轉換完成後立即以代碼 `4294967295` 結束。當該結束發生在轉換邊界，沒有訊息等待且沒有背景工作執行時，[VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)會安靜地關閉工作階段，而不是顯示此錯誤。您的下一條訊息會繼續對話。 在 v2.1.273 之前，擴充功能在每個轉換邊界都會顯示該結束的錯誤，即使沒有任何內容遺失。 **該怎麼做：**

- 在 VS Code 中，按照錯誤顯示的**檢視輸出日誌** 連結查看底層失敗
- 在 Agent SDK 應用程式中，在訊息迴圈周圍捕獲錯誤。[CLI 程序結束](https://code.claude.com/docs/zh-TW/agent-sdk/troubleshooting#cli-process-exit)下的項目涵蓋了您的程式碼在每個 SDK 語言中接收的內容。
- 在終端機中的同一專案中執行 `claude`。失敗通常會在那裡重現，並顯示其真實錯誤訊息，您可以在此頁面上查詢。
- 在終端機中執行 `claude doctor` 以檢查安裝和設定

### 無法在 PATH 上找到 Claude CLI

當您在整合終端機中開啟 Claude Code、終端機的殼層是 PowerShell，且擴充功能無法在 PATH 上找到已安裝的 `claude` 可執行檔時，[VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)會在 Windows 上顯示此錯誤。擴充功能拒絕啟動 Claude Code，直到它在 PATH 上找到已安裝的 `claude`。

```
Failed to run Claude Code: Error: Could not locate the Claude CLI on PATH. Launching by name in a PowerShell terminal would run a 'claude' from the open folder instead of the installed CLI, so the launch was blocked. Make sure the Claude CLI's install directory is on your system PATH (not only your PowerShell profile), then restart VS Code and try again. VS Code reads PATH when it starts, so PATH changes take effect only after a restart.

```

**該怎麼做：**

- 在 VS Code 外開啟新的 PowerShell 視窗並執行 `where.exe claude`。如果它沒有列印路徑，CLI 不在您的 PATH 上：按照[驗證您的 PATH](https://code.claude.com/docs/zh-TW/troubleshoot-install#verify-your-path)新增其安裝目錄。如果它列印了路徑，該項目來自您的 PowerShell 設定檔或來自 VS Code 尚未取得的 PATH 變更；接下來的兩個步驟涵蓋了這些情況。
- 將 PATH 項目設定為使用者或系統環境變數，而不是在您的 PowerShell 設定檔中。擴充功能不執行您的設定檔，因此只存在於那裡的 PATH 編輯永遠無法到達它。
- 變更 PATH 後重新啟動 VS Code。擴充功能檢查 VS Code 在啟動時捕獲的 PATH，因此 PATH 變更只有在重新啟動後才會生效。

### Claude Code 的連線在此訊息完成前結束

[VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)將您的訊息傳送到 `claude` 程序，連線在程序確認或完成訊息之前結束，且沒有錯誤。擴充功能無法判斷訊息是否已被處理，因此它要求您再次傳送訊息：

```
The connection to Claude Code ended before this message completed — it may not have been processed, so please send it again.

```

**該怎麼做：**

- 再次傳送訊息。下一條訊息會啟動一個新的 `claude` 程序，繼續對話。
- 如果它重複發生，在同一專案中的終端機中執行 `claude`。持續結束程序的失敗通常會在那裡重現，並顯示其真實錯誤訊息。

## Rewind 警告和錯誤

這些訊息來自 [`/rewind`](https://code.claude.com/docs/zh-TW/checkpointing) 程式碼還原。`Restored the code, but skipped N files` 是一個警告，表示 Claude Code 跳過了某些路徑。`No files were restored` 是一個錯誤，表示它沒有還原任何內容。

### Restored the code, but skipped files

`/rewind` 程式碼還原跳過了一個或多個追蹤的路徑，而不是透過它們進行寫入或刪除。Claude Code 在以下情況下會跳過路徑：

- 它是或已成為符號連結、硬連結或其他非一般檔案
- 其目錄自檢查點以來已變更
- 其備份無法安全讀取

跳過的路徑保留其目前的內容。在 v2.1.216 之前，`/rewind` 會透過追蹤路徑上的連結進行寫入和刪除，並且不會報告部分還原。

```
Restored the code, but skipped 2 files: the tracked path is (or became) a link or other non-regular file, its directory changed since the checkpoint, or its backup could not be safely read. Skipped files were left untouched — run with --debug for the paths.

```

**該怎麼做：**

- 識別哪些檔案被跳過，以便您可以使用下面的步驟處理每個檔案。訊息只提供計數；位於 `~/.claude/debug/<session-id>.txt` 的偵錯日誌會在還原執行時列出每個跳過的路徑，因此在下次還原之前使用 `/debug` 開啟偵錯日誌。在 macOS 或 Linux 上，您可以改為直接找到連結：`find . -type l` 用於符號連結，`find . -type f -links +1` 用於硬連結檔案。
- 如果跳過的檔案是您有意建立的連結，例如由 dotfile 管理器管理的設定檔或由 pnpm 等工具硬連結的檔案，rewind 會保留其內容不變。若要復原工作階段對其所做的變更，請要求 Claude 反轉編輯或自行編輯檔案
- 如果您沒有建立連結，請在信任其內容之前檢查路徑：某些東西在檢查點之後替換了該檔案

### No files were restored

當您使用 [`/rewind`](https://code.claude.com/docs/zh-TW/checkpointing) 還原程式碼，且無法還原該檢查點中的任何檔案時，Claude Code 會顯示此訊息。對於每個檔案，Claude Code 在編輯前儲存的備份遺失，或 Claude Code 無法寫入或刪除該檔案。

```
Failed to restore the code:
No files were restored: 1 file failed (backup missing, or the file could not be updated)

```

Claude Code 在[保留掃描](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)中刪除工作階段的備份，預設情況下約在工作階段最後一次儲存後 30 天。如果您在之後恢復工作階段，`/rewind` 仍會列出其檢查點，但還原到其中一個可能會因此錯誤而失敗。如果訊息還說 `N paths were skipped for link safety`，請參閱[Restored the code, but skipped files](https://code.claude.com/docs/zh-TW/errors#restored-the-code-but-skipped-files) 以了解這些路徑。 **該怎麼做：**

- 以其他方式復原變更：要求 Claude 反轉其編輯，或從版本控制還原檔案。當備份消失時，再次執行 `/rewind` 會以相同方式失敗。
- 如果 Claude Code 無法寫入或刪除檔案，請修復阻止寫入的問題，例如檔案權限，然後再次執行 `/rewind`。
- 若要在未來的工作階段中保留備份更長時間，請提高 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)。

在 v2.1.260 之前，Claude Code 會無聲地跳過備份遺失的檔案，還原似乎成功。

## 工作階段儲存警告

Claude Code 在輸入框下方的持續行上顯示這些警告，當它未儲存您的工作階段文字記錄時。無論哪種方式，工作階段都會繼續運作；警告告訴您工作階段稍後可能會在 [`--resume`](https://code.claude.com/docs/zh-TW/sessions) 中遺失。

### 文字記錄寫入失敗

Claude Code 在您工作時將文字記錄儲存到磁碟，其對[文字記錄檔案](https://code.claude.com/docs/zh-TW/sessions#where-transcripts-are-stored)的寫入失敗。該訊息以基礎錯誤代碼命名原因，例如磁碟已滿：

```
Transcript writes are failing (disk full — ENOSPC) · recent messages may not be saved for resume

```

警告根據錯誤在不同時間點出現：

- 在不會自行清除的條件首次失敗時：磁碟已滿、超過磁碟配額、檔案系統唯讀、路徑超過檔案系統長度限制，或在 macOS 和 Linux 上，權限錯誤
- 在至少跨越一分鐘的重複失敗後，包括 Windows 上的權限錯誤，其中防毒軟體掃描可能會導致單次寫入失敗，然後在重試時成功

在 v2.1.217 之前，Claude Code 會在沒有警告的情況下放棄失敗的寫入，稍後 `--resume` 遺失最近訊息是第一個跡象。 **該怎麼做：**

- 修復錯誤代碼命名的條件：為 `ENOSPC` 釋放磁碟空間；為 `EDQUOT` 提高或清除配額；為 `EACCES`、`EPERM` 或 `EROFS` 恢復文字記錄位置的寫入存取
- 警告在下一次成功寫入時自動清除；不需要重新啟動
- 在警告顯示時傳送的訊息稍後恢復工作階段時可能仍會遺失

### 因為設定了 CLAUDE_CODE_SKIP_PROMPT_HISTORY 所以文字記錄儲存已關閉

此工作階段啟動時設定了 [`CLAUDE_CODE_SKIP_PROMPT_HISTORY`](https://code.claude.com/docs/zh-TW/env-vars)，因此 Claude Code 不會為其寫入文字記錄或提示歷史記錄：

```
Transcript saving is off — CLAUDE_CODE_SKIP_PROMPT_HISTORY is set · --resume will not find this session; if unintended, unset it and restart

```

該變數是針對暫時性指令碼工作階段的有意選擇退出，但它也可以透過殼層設定檔、包裝指令碼或匯出它的父程序到達工作階段。 **該怎麼做：**

- 如果您有意設定該變數，不需要採取任何行動；該通知確認工作階段不會出現在 `--resume`、`--continue` 或向上箭頭歷史記錄中
- 如果您沒有，請從啟動 `claude` 的殼層或指令碼中移除該變數，然後啟動新工作階段。目前工作階段的訊息不會被追溯儲存。

### 因為繼承了 CLAUDE_CODE_CHILD_SESSION 標記所以文字記錄儲存已關閉

Claude Code 在它產生的子程序中設定 [`CLAUDE_CODE_CHILD_SESSION`](https://code.claude.com/docs/zh-TW/env-vars)，並將繼承它的互動式工作階段視為巢狀：Claude Code 不會為其儲存文字記錄，因此 Claude 本身啟動的工作階段不會填滿您的 `--resume` 清單。此通知表示您目前的工作階段繼承了該標記：

```
Transcript saving is off — inherited CLAUDE_CODE_CHILD_SESSION marker · restart with CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1 to keep future transcripts

```

當您從另一個 Claude Code 工作階段內執行 `claude` 時，該通知是預期的；當標記透過長期存在的中介（例如終端機、`screen` 工作階段或 Claude Code 工作階段原本啟動的啟動器）洩漏時，它會發出誤分類的訊號。 在 tmux 內，Claude Code 會偵測透過 tmux 伺服器全域環境到達的標記，並繼續儲存，因此該通知不會出現在該情況下。 **該怎麼做：**

- 如果您有意從另一個 Claude Code 工作階段內啟動此工作階段，不需要採取任何行動
- 如果這是頂層工作階段，請結束並使用設定的 [`CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1`](https://code.claude.com/docs/zh-TW/env-vars) 重新啟動。儲存從重新啟動時開始套用，因此在此之前傳送的訊息不會被儲存。
- 若要修復從相同終端機或啟動器的未來啟動，請從其環境中移除 `CLAUDE_CODE_CHILD_SESSION`

## 設定警告

Claude Code 將大多數這些訊息寫入 stderr，而不是寫入對話中，並在啟動時寫入大多數訊息。當訊息出現在其他地方（例如在偵錯日誌中或作為對話檢視中的啟動通知）或在其他時間（例如[要求時的無法辨識模型診斷行](https://code.claude.com/docs/zh-TW/errors#unrecognized-model-id-on-a-request)）時，條目會說明這一點。

### 全螢幕轉譯器未完成啟動

此機器上的先前[全螢幕](https://code.claude.com/docs/zh-TW/fullscreen)工作階段在完成啟動前退出，因此 Claude Code 在傳統轉譯器上啟動此工作階段並列印以下其中一個通知：

```
Claude Code 的全螢幕轉譯器上次在此機器上未完成啟動，因此此次啟動使用傳統轉譯器。它將在下次啟動時嘗試全螢幕；/tui default 保持傳統轉譯器。

Claude Code 的全螢幕轉譯器在此機器上多次啟動失敗，因此已在此處關閉。執行 /tui fullscreen 以再次嘗試（這也會在更新後重設）。

```

**該怎麼做：**

- 遵循[全螢幕轉譯](https://code.claude.com/docs/zh-TW/fullscreen#fullscreen-renderer-didnt-finish-starting)。它說明您會收到哪個通知、Claude Code 在後續工作階段中的作用，以及如何再次嘗試全螢幕或保持傳統轉譯器。
- 如果已終止的工作階段列印了結束訊息，請參閱 [Claude Code 在無法復原的介面錯誤後退出](https://code.claude.com/docs/zh-TW/errors#exited-after-an-unrecoverable-interface-error)以了解它命名的內容。

在 v2.1.236 之前，Claude Code 未列印通知，並在啟動失敗後繼續在全螢幕轉譯中啟動工作階段。

### Claude Code 在無法復原的介面錯誤後退出

當 Claude Code 退出時會列印此訊息，因為其終端介面遇到無法復原的錯誤，在任一轉譯器中都是如此。第二句僅在[全螢幕](https://code.claude.com/docs/zh-TW/fullscreen)轉譯器啟動時發生錯誤時出現：

```
Claude Code 在無法復原的介面錯誤 (<error>) 後退出。它在全螢幕轉譯器啟動時發生，因此下次啟動將使用傳統轉譯器（CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1 隨時強制執行）。

```

**該怎麼做：**

- 再次啟動 Claude Code。若要繼續進行對話，請在同一目錄中執行 `claude --resume`。
- 如果訊息命名全螢幕轉譯器，[全螢幕轉譯](https://code.claude.com/docs/zh-TW/fullscreen#fullscreen-renderer-didnt-finish-starting)會說明下次啟動的作用，這取決於您如何開啟全螢幕，以及如何再次嘗試全螢幕或保持傳統轉譯器。

在 v2.1.236 之前，Claude Code 在此類錯誤後退出而不列印訊息。

### 代理程式描述超過 15.0k 令牌限制

Claude Code 在對話檢視中顯示此警告作為啟動通知，而不是在 stderr 上。您的[子代理程式](https://code.claude.com/docs/zh-TW/sub-agents)（除了內建代理程式外）的組合描述超過 15,000 個令牌，如 Claude Code 估計的那樣。每個代理程式計算其名稱加上其 `description` frontmatter。Claude Code 無論總數是否超過限制都會載入每個代理程式，因此警告不會改變載入的內容。

```
代理程式描述超過 15.0k 令牌限制（~16.2k 令牌）· 要求 Claude 修剪 .claude/agents/ 中的代理程式描述

```

**該怎麼做：**

- 縮短您的代理程式檔案的 `description` frontmatter，或要求 Claude 為您修剪它們。
- 移除您不再使用的代理程式檔案。

### 工作區尚未受信任

Claude Code 在專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中找到 `permissions.allow` 規則或 `permissions.additionalDirectories` 項目，但未應用它們，因為[來自專案設定的允許規則需要工作區信任](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)。計數、設定名稱和訊息中命名的檔案因您的設定而異。`deny` 和 `ask` 規則不受影響。

```
忽略來自 .claude/settings.local.json 的 2 個 permissions.allow 項目：此工作區尚未受信任。在此處以互動方式執行 Claude Code 一次並接受信任對話，或在 /Users/you/.claude.json 中設定 projects["/Users/you/project"].hasTrustDialogAccepted: true。

```

**該怎麼做：**

- 在目錄中執行 `claude` 並接受信任對話。[專案允許規則和工作區信任](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)說明該接受涵蓋哪個資料夾。
- 在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p` 不會顯示對話。使用訊息列印的確切 `projects` 金鑰在 `~/.claude.json` 中設定 `hasTrustDialogAccepted` 項目。
- 如果訊息命名 `.claude/settings.local.json` 且您在 git 儲存庫外或在主目錄中啟動 Claude Code，請更新至 v2.1.200 或更新版本。版本 2.1.196 至 2.1.199 在這些工作區中將您自己的 `.claude/settings.local.json` 視為儲存庫提供的。在 v2.1.207 及更新版本上，如果您尚未信任資料夾，在 git 儲存庫外更新還不夠：確定資料夾不在儲存庫內會執行 git，Claude Code 僅在您接受信任對話後才執行該檢查，因此請使用第一步。您的主目錄和任何其他[設定主目錄](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)豁免且不等待對話。請參閱[專案允許規則和工作區信任](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)。

### 工作目錄是網路路徑

Claude Code 不會將網路路徑新增為工作目錄。查詢網路路徑可以聯絡它命名的主機，在 Windows 上該聯絡可以將您的認證傳送給主機，因此 Claude Code 拒絕該路徑而不查詢它。當您使用此類路徑執行 `/add-dir` 時，或作為啟動時的警告時，您會看到此訊息。當它在啟動時出現時，Claude Code 啟動時不包含該目錄。

```
\\server\share 是網路路徑，無法新增為工作目錄。在 Windows 上，將共用對應到磁碟機代號，並在啟動時使用 --add-dir 傳遞它（在工作階段中新增的磁碟機代號尚未帶有遠端讀取信任）。

```

Claude Code 以此方式拒絕的路徑包括：

- UNC 共用，例如 `\\server\share`
- 自動掛載路徑，例如 `/net/<host>`，除非您從該主機的自動掛載下的目錄啟動 Claude Code
- 透過符號連結或連接點到達網路位置的本機路徑

對應的磁碟機代號和 `\\wsl$` 路徑不計為網路路徑。 **該怎麼做：**

- 在 Windows 上，將共用對應到磁碟機代號，例如使用 `net use Z: \\server\share`，並在啟動時使用 `claude --add-dir Z:\` 傳遞磁碟機。
- 在 macOS 或 Linux 上，在本機路徑掛載共用並改為新增該路徑。
- 如果路徑在 `permissions.additionalDirectories` 中，請從列出它的設定檔中移除它。

在 v2.1.257 之前，Claude Code 接受可到達的網路路徑作為工作目錄。

### 遠端受管設定無法載入

您的工作階段符合[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)的資格，但 Claude Code 無法擷取它們，因此在互動工作階段中顯示此警告。括號中的原因命名失敗的內容，例如 `network error`、`request timed out` 或 `authentication rejected (401)`，行的其餘部分說明工作階段執行的策略：

- **從較早成功擷取快取的設定** ：Claude Code 在該快取策略上執行工作階段，除了[隱藏的環境變數](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)，行讀取 `using cached policy`。
- **無快取** ：Claude Code 在沒有伺服器受管設定的情況下執行工作階段，行讀取 `no remote policy applied`。

**該怎麼做：**

- 對訊息命名的原因採取行動：對於網路原因，檢查此機器是否可以到達 `api.anthropic.com`；對於驗證原因，使用 `/status` 檢查您的登入
- 執行 `/status` 或 `claude doctor` 以取得完整診斷

在 v2.1.248 之前，Claude Code 僅在偵錯日誌中報告設定擷取失敗。

### 受管設定未獲批准

您的組織的[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)包括需要您批准的設定，且您拒絕了[安全批准對話](https://code.claude.com/docs/zh-TW/server-managed-settings#security-approval-dialogs)，因此 Claude Code 退出而不應用它們：

```
受管設定未獲批准；退出而不應用它們。

```

**該怎麼做：**

- 再次啟動 Claude Code 並批准對話以在您的組織設定下繼續。拒絕的對話不會被記住，因此在下次啟動時會再次出現。
- 如果您對對話列出的設定不確定，在批准前詢問維護您的組織受管設定的人

### MCP 伺服器被企業受管策略阻止

您在 `/mcp` 中選擇了伺服器上的**重新連線** ，或在那裡重新開啟了已停用的伺服器，且[限制 MCP 伺服器](https://code.claude.com/docs/zh-TW/managed-mcp)的設定阻止該伺服器。Claude Code 拒絕連線它並顯示：

```
MCP 伺服器 <name> 被企業受管策略阻止

```

以下任何設定都可能產生訊息：

- 與伺服器相符的 [`deniedMcpServers`](https://code.claude.com/docs/zh-TW/managed-mcp#policy-based-control-with-allowlists-and-denylists) 項目，包括您自己的 `~/.claude/settings.json` 或專案的 `.claude/settings.json` 中的項目
- 伺服器不相符的 [`allowedMcpServers`](https://code.claude.com/docs/zh-TW/managed-mcp#policy-based-control-with-allowlists-and-denylists) 清單
- [`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization) 且 `mcp` 已鎖定，這會阻止在 `~/.claude.json` 和 `.mcp.json` 中設定的伺服器
- [`disableClaudeAiConnectors`](https://code.claude.com/docs/zh-TW/mcp#disable-claude-ai-connectors)，當伺服器是 claude.ai 連接器時

**該怎麼做：**

- 檢查您自己的使用者和專案設定檔案中是否有這些設定之一，並變更或移除它
- 如果您自己的設定都不能解釋該阻止，請詢問您的管理員哪個受管設定阻止了伺服器

在 v2.1.257 之前，**重新連線** 和在 `/mcp` 中重新啟用可以連線伺服器，該伺服器被中途工作階段策略更新阻止。

### 受管設定文件無法解析

您的組織部署[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)，且其中一個已部署的文件存在但無法解析為 JSON 物件，因此 Claude Code 在啟動時以代碼 1 退出，而不是執行而不使用文件帶來的策略。行在訊息前命名失敗的來源：

```
/Library/Application Support/ClaudeCode/managed-settings.json：受管設定文件無法解析為 JSON 物件；其設定都不生效。修復或移除它。

```

來源是以下其中之一：

- `managed-settings.json` 檔案的路徑或 `managed-settings.d` 下的放入檔案
- macOS 受管偏好設定設定檔、`per-user managed preferences` 或 `device-level managed preferences`
- Windows 登錄值、`Registry: HKLM\SOFTWARE\Policies\ClaudeCode\Settings`

[尋找 Claude Code 放棄的項目](https://code.claude.com/docs/zh-TW/managed-settings#find-entries-claude-code-dropped)列出使每個來源無法解析的原因。 Claude Code 拒絕啟動，即使另一個管理來源提供有效策略。您在互動工作階段、`claude -p`、Agent SDK 工作階段、[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)和大多數子命令（包括 `claude doctor`）中看到此錯誤。拒絕故意失敗關閉：Claude Code 無法解析的文件中的設定無法強制執行，啟動時不應用組織的控制項會執行工作階段。 可解析文件中的架構問題不會產生此錯誤。[尋找 Claude Code 放棄的項目](https://code.claude.com/docs/zh-TW/managed-settings#find-entries-claude-code-dropped)涵蓋 Claude Code 對其所做的操作。 當 `managed-settings.d/` 目錄存在但無法列出時，Claude Code 報告 `Managed settings drop-in directory could not be read:` 後跟基礎錯誤。[尋找 Claude Code 放棄的項目](https://code.claude.com/docs/zh-TW/managed-settings#find-entries-claude-code-dropped)涵蓋讀取失敗在啟動時退出的時間。 **該怎麼做：**

- 如果您管理機器，修復命名的文件使其解析為 JSON 物件，或移除檔案、設定檔或登錄值。空的 `managed-settings.json` 計為 `{}` 且不會阻止啟動。
- 如果您不管理，請要求您的管理員修復已部署的文件。您自己的設定檔案中沒有任何內容會導致或清除此錯誤。

### headersHelper 未執行

Claude Code 僅使用其靜態 `headers` 連線了 MCP 伺服器，並跳過了伺服器的 [`headersHelper`](https://code.claude.com/docs/zh-TW/mcp#use-dynamic-headers-for-custom-authentication)，因為協助程式是 shell 命令且資料夾沒有已儲存的信任。當您手動在 `~/.claude.json` 中設定其項目時，或在主目錄外，當您在互動工作階段中為其接受信任對話時，資料夾會獲得已儲存的信任。請參閱[在 headersHelper 執行前信任資料夾](https://code.claude.com/docs/zh-TW/mcp#trust-a-folder-before-its-headershelper-runs)以了解此檢查適用於哪些伺服器。 Claude Code 僅在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中寫入此行，每個伺服器一次。在互動工作階段中，它改為將相同的拒絕寫入偵錯日誌。

```
MCP 伺服器 'internal-api'：headersHelper 未執行 — 此工作區沒有持久化信任；在此處以互動方式接受信任對話一次，或在 /Users/you/.claude.json 中設定 projects["/Users/you/project"].hasTrustDialogAccepted。

```

訊息列印的 `projects` 金鑰是資料夾[專案允許規則和工作區信任](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)說明 Claude Code 信任的金鑰。為父資料夾接受信任對話不滿足檢查，`-p` 或 SDK 工作階段也不滿足。 **該怎麼做：**

- 在訊息命名的資料夾中執行 `claude`，接受信任對話，然後再次執行您的 `-p` 或 SDK 命令
- 在 `~/.claude.json` 中自己設定 `hasTrustDialogAccepted` 項目，使用訊息列印的確切 `projects` 金鑰
- 如果您在主目錄中啟動工作階段，請從您已信任的專案目錄工作。當您在主目錄中接受信任對話時，Claude Code 僅在目前工作階段中保持該信任。

### 格式不正確的 Tool(content) 規則

您的設定檔案中的[權限規則](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)沒有 `Tool` 或 `Tool(content)` 的形狀，例如因為文字跟在右括號後面或其中一個括號遺失。Claude Code 跳過規則，並在互動工作階段啟動時在無效設定對話中列出它，以及在 [`claude doctor`](https://code.claude.com/docs/zh-TW/debug-your-config#check-resolved-settings) 輸出中：

```
無效權限規則 "Bash(ls) x" 已跳過：格式不正確的 Tool(content) 規則。規則採用 Tool 或 Tool(content) 的形式，必須在右括號 ")" 處結束；括號內的內容是字面意思

```

**該怎麼做：**

- 在訊息列出的設定檔中，重寫規則使其在其右括號處結束，例如用 `Bash(ls *)` 代替 `Bash(ls) x`
- 將括號內的內容保留原樣。它們是字面意思，因此規則如 `Edit(./Finance (2024)/*)` 無需逃逸即有效

在 v2.1.260 之前，Claude Code 將括號不相符的規則報告為 `Mismatched parentheses`。

### 不符合檔案權限檢查

Claude Code 在您的[設定檔案](https://code.claude.com/docs/zh-TW/settings#where-settings-live)、[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)或 `--allowedTools`、`--disallowedTools` 或 `--settings` 旗標值中找到了具有路徑的 `Write`、`NotebookEdit`、`MultiEdit` 或 `Glob`[權限規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)。它僅針對 `Edit` 和 `Read` 規則檢查檔案權限，因此它永遠不會查詢命名其他檔案工具之一的路徑規則。它保留規則並不改變其他任何內容；警告命名規則、其在括號中的來源和要寫入的替換：

```
權限拒絕規則 (.claude/settings.json)：Write(docs/**) 不符合檔案權限檢查 — 僅 Edit(path) 規則。改用 Edit(docs/**)（Edit 規則涵蓋所有檔案編輯工具）。

```

**該怎麼做：**

- 將 `Write(path)`、`NotebookEdit(path)` 和舊版 `MultiEdit(path)` 規則替換為 `Edit(path)`。`Edit` 規則涵蓋所有檔案編輯工具。
- 除了在 `--allowedTools` 中，Claude Code 接受 `Glob` 規則而不警告，將 `Glob(path)` 規則替換為 `Read(path)`。
- 在警告在括號中命名的來源處修復規則：設定檔案路徑，或 `--allowed-tools` 和 `--disallowed-tools` 的旗標本身。不存在於磁碟上的 `claude-settings-<hash>.json` 路徑代表內聯 `--settings` 值。修復您傳遞給該旗標的 JSON。
- 將裸工具名稱規則（例如 `Write` 或 `Glob`）保留原樣。Claude Code 在[工具級別](https://code.claude.com/docs/zh-TW/permissions#match-all-uses-of-a-tool)上相符它們，不會警告它們。
- 如果來源讀取 `managed policy settings`，將警告轉發給維護您受管設定的人，因為您無法自己清除它。

在[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)或使用 `--output-format json` 或 `stream-json` 時，Claude Code 將警告寫入偵錯日誌而不是 stderr，因此機器讀取輸出保持乾淨。使用 `--debug` 在 `~/.claude/debug/<session-id>.txt` 處擷取它。在 v2.1.210 之前，Claude Code 接受這些規則而不警告。

### 在命令的其餘部分之前有萬用字元

Claude Code 在您的[設定檔案](https://code.claude.com/docs/zh-TW/settings#where-settings-live)、[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)或 `--allowedTools` 或 `--settings` 旗標值中找到了 `Bash` 允許規則，其 `*` 在決定它是哪個命令的後續單詞之前，例如 `Bash(git * main)` 或 `Bash(git -C * status *)`。`*` 符合任何文字，包括在該位置插入的選項：`Bash(git * main)` 也批准 `git -c core.fsmonitor=<script> diff main`，其中 `-c` 使 git 執行命令命名的程式。[萬用字元模式](https://code.claude.com/docs/zh-TW/permissions#wildcard-patterns)顯示相符規則。 警告存在是為了讓您縮小萬用字元比您預期更寬的規則。Claude Code 保留規則並不改變它相符的方式；警告命名規則及其在括號中的來源：

```
權限允許規則 (.claude/settings.json)：Bash(git -C * status *) 在命令的其餘部分之前有萬用字元，因此它也符合在該位置插入的任何選項並批准它們而不提示。對於 git，選項如 -c 和 --exec-path 可以執行任意命令。將該 * 替換為您的確切值，或僅在子命令後使用 *（例如 Bash(git status *)）。

```

**該怎麼做：**

- 將子命令前的 `*` 替換為您的確切值：用 `Bash(git checkout main)` 代替 `Bash(git * main)`。
- 將每個 `*` 移到子命令後：用 `Bash(git status *)` 代替 `Bash(git -C * status *)`。為您想允許的每個子命令寫一個規則。
- 在警告在括號中命名的來源處修復規則：設定檔案路徑，或 `--allowed-tools` 旗標本身。不存在於磁碟上的 `claude-settings-<hash>.json` 路徑代表內聯 `--settings` 值。修復您傳遞給該旗標的 JSON。
- 如果來源讀取 `managed policy settings`，將警告轉發給維護您受管設定的人，因為您無法自己清除它。

Claude Code 不警告具有相同形狀的拒絕和詢問規則：它拒絕或提示它們相符的額外命令，而不是批准它們。它也不警告子命令在第一個 `*` 之前的規則，例如 `Bash(git commit *)`，或沒有單詞（除了選項）跟在 `*` 後的規則，例如 `Bash(git *)`，或關於 `:*` 前綴規則如 `Bash(git:*)`。 在[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)或使用 `--output-format json` 或 `stream-json` 時，Claude Code 將警告寫入偵錯日誌而不是 stderr，因此機器讀取輸出保持乾淨。使用 `--debug` 在 `~/.claude/debug/<session-id>.txt` 處擷取它。在 v2.1.246 之前，Claude Code 接受這些規則而不警告。

### crossSessionInbound 必須是 accept、hold、refuse 之一

設定檔案將 [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound) 設定為 Claude Code 無法辨識的值，例如打字錯誤 `"reject"`。警告的第二句取決於哪個檔案保持該值；在使用者、專案、本機或 `--settings` 檔案中讀取：

```
"crossSessionInbound" 必須是 "accept"、"hold"、"refuse" 之一；收到 "reject"。此值被忽略；當它存在時，跨工作階段訊息被保持以供您批准，而不是被傳遞。將其設定為上述值之一。

```

在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中，Claude Code 將無法辨識的值視為 `refuse`（最限制的值），警告說跨工作階段訊息被拒絕，直到管理員修復它。有關保持如何與您其他設定檔案中的值結合，請參閱 [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound)。 **該怎麼做：**

- 將金鑰設定為 `"accept"`、`"hold"` 或 `"refuse"`，或移除它
- 當警告命名受管設定時，要求管理員修復該值

在 v2.1.248 之前，Claude Code 忽略無法辨識的值而不警告。

### 200K 限制未強制執行

您設定了 [`CLAUDE_CODE_DISABLE_1M_CONTEXT=1`](https://code.claude.com/docs/zh-TW/env-vars)，這通常使[自動壓縮](https://code.claude.com/docs/zh-TW/model-config#default-auto-compact-thresholds)在 1M 上下文模型上保持工作階段至 200K 視窗，但沒有壓縮閾值將此工作階段限制在或低於 200K，因此對話可以超過它。

```
CLAUDE_CODE_DISABLE_1M_CONTEXT 已設定，但 <model> 的 200K 限制未強制執行，因此此工作階段可以超過它。若要強制執行，設定 CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000（或 autoCompactWindow 設定）。

```

Claude Code 為它辨識為具有原生 1M 視窗的每個模型自行強制執行 200K 限制，對於它無法辨識的模型 ID，它在它假設的視窗處壓縮。當其他設定擊敗該強制執行時出現警告：

- 模型 ID 不是 Claude Code 辨識的，例如[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)別名，且您設定了 [`CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1`](https://code.claude.com/docs/zh-TW/env-vars) 或使用 [`CLAUDE_CODE_MAX_CONTEXT_TOKENS`](https://code.claude.com/docs/zh-TW/env-vars) 將假設的視窗提高到 200K 以上。在此情況下，訊息也提供 `or update to a Claude Code version that recognizes <model>` 作為補救。
- 透過 [`ANTHROPIC_BETAS`](https://code.claude.com/docs/zh-TW/env-vars) 或 [`--betas`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 旗標要求的 `context-1m` 測試版仍要求 API 在接受該測試版的模型上使用 1M 視窗，而沒有任何內容在 200K 處壓縮工作階段

**該怎麼做：**

- 設定 [`CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000`](https://code.claude.com/docs/zh-TW/env-vars)，或 [`autoCompactWindow`](https://code.claude.com/docs/zh-TW/settings-reference#autocompactwindow) 設定為 `200000`，以便自動壓縮在 200K 邊界處壓縮
- 如果訊息命名此版本無法辨識的模型 ID，執行 `claude update`。辨識 ID 為 1M 上下文模型的版本無需進一步設定即可強制執行限制。
- 如果您想讓工作階段改為使用模型的完整視窗，取消設定 `CLAUDE_CODE_DISABLE_1M_CONTEXT`；警告僅報告 200K 限制未強制執行

在[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)或使用 `--output-format json` 或 `stream-json` 時，Claude Code 將警告寫入偵錯日誌而不是 stderr。

### 要求上無法辨識的模型 ID

Claude Code 為您的 Claude Code 版本無法辨識的模型 ID 傳送了要求，並找不到將該 ID 對應到它辨識的模型的 [`modelOverrides`](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version) 項目。Claude Code 仍使用您設定的 ID 傳送要求，不退出或切換模型。

```
[claude-code:unrecognized_model] {"model":"my-proxy-model","query_source":"sdk"}

```

在讀取 stderr 的指令碼或工具中，符合 `[claude-code:unrecognized_model]` 前綴。在前綴和一個空格之後，Claude Code 寫入一行 JSON 物件。Claude Code 可以在更新版本中向其新增欄位，因此忽略您不期望的任何欄位。它至少寫入這兩個：

- `model`：您設定的模型字串
- `query_source`：使用模型的要求路徑。Claude Code 為 `-p` 執行報告 `sdk`，為子代理程式報告以 `agent:` 開頭的值。

Claude Code 根據您執行它的方式將行寫入兩個位置之一：

- 在[非互動模式](https://code.claude.com/docs/zh-TW/headless)中使用 `-p`，Claude Code 在每個 `--output-format` 下將其寫入 stderr，因此您可以解析 stdout 而不過濾行
- 在互動工作階段或[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)中，Claude Code 改為將其寫入偵錯日誌；使用 `--debug` 在 `~/.claude/debug/<session-id>.txt` 處擷取它

Claude Code 每個模型字串每個程序寫入行一次。它為每個進一步的無法辨識的 ID 寫入單獨的行，例如[子代理程式](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)或[背景功能](https://code.claude.com/docs/zh-TW/costs#background-token-usage)使用的 ID。 Claude Code 不為它解析為它辨識的模型的提供者 ID 寫入行，例如 Amazon Bedrock `us.anthropic.claude-...` ID、Google Cloud 的 Agent Platform ID 帶有 `@` 版本後綴，以及包含 Claude 模型 ID 的 Microsoft Foundry 部署名稱。Claude Code 檢查 Amazon Bedrock[應用程式推論設定檔 ARN](https://code.claude.com/docs/zh-TW/amazon-bedrock#map-each-model-version-to-an-inference-profile) 後面的模型，而不是 ARN 本身。它為無法解析的 ARN（例如打字錯誤的 ARN）寫入無行。 **該怎麼做：**

- 如果您故意設定 ID，例如[LLM 閘道](https://code.claude.com/docs/zh-TW/llm-gateway)別名，將 [`modelOverrides`](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version) 項目新增到您的[設定檔案](https://code.claude.com/docs/zh-TW/settings#where-settings-live)，以 ID 作為其值。使用 Anthropic 模型 ID 作為金鑰，而不是家族別名如 `opus`。對於範例行中的 `my-proxy-model`，新增此項目：

```
{
  "modelOverrides": {
    "claude-opus-4-6": "my-proxy-model"
  }
}

```

Claude Code 然後將 `my-proxy-model` 視為 `claude-opus-4-6` 並停止寫入行。

- 如果 ID 命名比您的 Claude Code 版本更新的模型，執行 `claude update`
- 如果 ID 是打字錯誤，在您可以設定模型的[位置](https://code.claude.com/docs/zh-TW/model-config#setting-your-model)或[別名變數](https://code.claude.com/docs/zh-TW/model-config#environment-variables)中修復它。如果 `query_source` 以 `agent:` 開頭，改為在您設定[子代理程式模型](https://code.claude.com/docs/zh-TW/sub-agents#choose-a-model)的位置修復它。

在 v2.1.233 之前，Claude Code 為無法辨識的模型 ID 傳送要求時未寫入行。

### 被殺死的工作階段留下的過時沙箱遮罩檔案

`claude doctor` 在其診斷中列印此警告，`/status` 列出相同的行。它在 Linux 和 WSL2 上出現，當[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)啟用且檔案系統隔離開啟時。 當沙箱化命令執行時，沙箱透過在那裡建立 0 位元組唯讀佔位符來保持對尚不存在的檔案的寫入拒絕，並在之後移除它。在該清理執行前被殺死的工作階段（例如透過 SIGKILL）會留下佔位符。後續工作階段在每次啟動時再次唯讀繫結它們，因此設定寫入（例如儲存「是，不要再問」）在其中一個所在的位置失敗。

```
- 被殺死的工作階段留下的過時沙箱遮罩檔案：/home/you/project/.claude/settings.local.json
  修復：在該專案中沒有其他 Claude Code 工作階段執行時，使用 `rm <path>` 移除每個 — 0 位元組唯讀檔案（其中設定檔案所在）使「是，不要再問」無法儲存，沙箱在每次啟動時再次唯讀繫結它

```

**該怎麼做：**

- 退出在該專案中執行的任何其他 Claude Code 工作階段，然後使用 `rm` 刪除每個列出的檔案。警告命名最多三個檔案並計算其餘的，因此在刪除後重新執行 `claude doctor` 直到警告不再出現。另一個工作階段的沙箱仍在使用的佔位符是該工作階段寫入保護的活躍部分
- 如果您使用「是，不要再問」儲存的權限選擇未堅持，在刪除佔位符後再次儲存它

在 v2.1.257 之前，`claude doctor` 未標記這些檔案；較早版本在工作階段被殺死時留下相同的佔位符。

## 回應品質似乎低於預期

如果 Claude 的回答似乎不如您預期的那樣有能力，但沒有顯示錯誤，原因通常是對話狀態而非模型本身。Claude Code 不會無聲地更改模型版本。它只能在三種特定情況下切換到備用模型：

- 配置的 [`--fallback-model`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 在可用性錯誤後接管該輪次，並在文字記錄中顯示通知
- Amazon Bedrock 或 Google Cloud 的 Agent Platform 啟動檢查發現您的預設模型不可用
- [自動模型備用](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)在 Fable 5.1、Fable 5 和 Opus 5 上將工作階段移至標記類別的備用模型（當該類別有備用模型時），並在文字記錄中顯示通知

下面的模型選擇檢查可以捕捉第二和第三種情況；第一種情況顯示為文字記錄通知而非 `/model` 變更。[模型設定](https://code.claude.com/docs/zh-TW/model-config)說明每個備用何時適用。 首先檢查這些項目：

- **模型選擇** ：執行 `/model` 以確認您在預期的模型上。先前的 `/model` 選擇或 `ANTHROPIC_MODEL` 環境變數可能使您在比預期更小的模型上。
- **努力程度** ：執行 `/effort` 以檢查目前的推理程度，並為困難的除錯或設計工作提高它。預設值因模型而異，所以在假設您低於最大值之前請先檢查。請參閱[調整努力程度](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)以了解每個模型的預設值和 `ultrathink` 快捷方式。
- **上下文壓力** ：執行 `/context` 以查看視窗有多滿。如果接近容量，請在自然斷點執行 `/compact` 或執行 `/clear` 以重新開始。請參閱[探索上下文視窗](https://code.claude.com/docs/zh-TW/context-window)以了解自動壓縮如何影響較早的輪次。
- **過時的指示** ：大型或過時的 `CLAUDE.md` 檔案和 MCP 工具定義會消耗上下文並可能引導回應。`/doctor` 檢查會標記超大的記憶檔案和未使用的擴充功能，而 `/context` 會顯示 MCP 工具的權杖使用情況。在 v2.1.205 之前，`/doctor` 開啟了一個診斷畫面，標記超大的記憶檔案和子代理定義。

當回應出錯時，回溯通常比用更正回覆效果更好。按 Esc 兩次或執行 `/rewind` 以回到不良輪次之前，然後用更多細節重新表述提示。在執行緒中更正會將錯誤的嘗試保留在上下文中，這可能會將後來的答案錨定到它。請參閱[檢查點](https://code.claude.com/docs/zh-TW/checkpointing)。 如果在檢查上述項目後品質仍然似乎有問題，請執行 `/feedback` 並描述您預期的內容與您得到的內容。以這種方式提交的回饋包括對話文字記錄，這是 Anthropic 診斷真實迴歸的最快方式。如果 `/feedback` 在您的環境中不可用，請參閱[報告錯誤](https://code.claude.com/docs/zh-TW/errors#report-an-error)。 如果 Claude 警告懷疑提示注入，或因懷疑注入而拒絕請求，而警告命名的文字是 Claude Code 自動添加到對話中的上下文而非檔案或網路內容，請執行 `claude update` 並重試。如果更新後警告重複出現，請[報告它](https://code.claude.com/docs/zh-TW/errors#report-an-error)而不是將標記的內容貼回提示中。在 v2.1.201 之前，Sonnet 5 以相同方式拒絕了一些請求。

## 回報錯誤

如需了解此頁面未涵蓋的元件錯誤，請參閱相關指南：

- MCP 伺服器連線或驗證失敗：[MCP](https://code.claude.com/docs/zh-TW/mcp)
- Hook 指令碼失敗或阻止了工具：[Debug hooks](https://code.claude.com/docs/zh-TW/hooks#debug-hooks)
- 安裝期間權限被拒或檔案系統錯誤：[Troubleshoot installation and login](https://code.claude.com/docs/zh-TW/troubleshoot-install)

如果此處未列出錯誤或建議的修正方法無法幫助：

- 在 Claude Code 內執行 `/feedback` 以將文字記錄和說明傳送給 Anthropic。該命令也提供開啟預先填入的 GitHub issue 的選項。傳送給 Anthropic 需要[驗證](https://code.claude.com/docs/zh-TW/authentication)。在 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 和其他第三方提供者上，或當未設定 Anthropic 認證時，`/feedback` 會儲存本機封存，您可以改為傳送給您的 Anthropic 帳戶代表。
- 從您的 shell 執行 `claude doctor` 以進行安裝的唯讀診斷，或在 Claude Code 內執行 `/doctor` 檢查以尋找並修正設定問題
- 檢查 [status.claude.com](https://status.claude.com) 以了解活躍的事件
- 在 GitHub 上搜尋[現有 issue](https://github.com/anthropics/claude-code/issues)

是否 助手
