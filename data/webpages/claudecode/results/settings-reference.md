[Skip to main content](https://code.claude.com/docs/zh-TW/settings-reference#content-area) 本參考頁面列出 Claude Code 從設定檔讀取的每個鍵，以及它保存在 `~/.claude.json` 中的[簡短鍵組](https://code.claude.com/docs/zh-TW/settings-reference#global-config-settings)。若要選擇檔案或檢查優先順序，請從[設定檔和優先順序](https://code.claude.com/docs/zh-TW/settings)開始。

## 設定索引

下方的每個鍵都連結到其條目。範圍列出了[檔案](https://code.claude.com/docs/zh-TW/settings#settings-files-and-who-they-affect)，其中可以使用該設定：`User` 是 `~/.claude/settings.json`、`Project` 是 `.claude/settings.json`、`Local` 是 `.claude/settings.local.json`，以及 `Managed` 是[您的組織部署的內容](https://code.claude.com/docs/zh-TW/managed-settings)。`Any file` 表示全部四個，`Global config` 表示 [`~/.claude.json`](https://code.claude.com/docs/zh-TW/settings-reference#global-config-settings)。

| 鍵                                                                                                                                                         | 說明                                                                                                                                                                                                                                                              | 主題                       | 範圍                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ----------------------- |
| [`advisorModel`](https://code.claude.com/docs/zh-TW/settings-reference#advisormodel)                                                                       | 選擇當 Claude 詢問[顧問工具](https://code.claude.com/docs/zh-TW/advisor)時哪個模型回答                                                                                                                                                                            | 模型和回應                 | Any file                |
| [`agent`](https://code.claude.com/docs/zh-TW/settings-reference#agent)                                                                                     | 以命名的[子代理](https://code.claude.com/docs/zh-TW/sub-agents)及其提示、工具和模型開始每個工作階段                                                                                                                                                               | 代理、工作階段和 worktrees | Any file                |
| [`agentPushNotifEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#agentpushnotifenabled)                                                     | 讓 Claude 在決定時傳送[推播通知到您的手機](https://code.claude.com/docs/zh-TW/remote-control#mobile-push-notifications)                                                                                                                                           | 遠端、桌面和通知           | Any file                |
| [`allowAllClaudeAiMcps`](https://code.claude.com/docs/zh-TW/settings-reference#allowallclaudeaimcps)                                                       | 載入 Claude Code 自行擷取的 [claude.ai 連接器](https://code.claude.com/docs/zh-TW/mcp)，以及已部署的 [`managed-mcp.json`](https://code.claude.com/docs/zh-TW/managed-mcp#exclusive-control-with-managed-mcp-json)                                                 | MCP                        | Managed                 |
| [`allowedChannelPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#allowedchannelplugins)                                                     | 取代[頻道外掛程式](https://code.claude.com/docs/zh-TW/channels#restrict-which-channel-plugins-can-run)的預設允許清單，該清單可以推送訊息                                                                                                                          | 外掛程式和技能             | Managed                 |
| [`allowedHttpHookUrls`](https://code.claude.com/docs/zh-TW/settings-reference#allowedhttphookurls)                                                         | 限制[HTTP hooks](https://code.claude.com/docs/zh-TW/hooks)可以針對的 URL                                                                                                                                                                                          | Hooks 和自動化             | Any file                |
| [`allowedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#allowedmcpservers)                                                             | 允許清單，其中列出使用者可以新增的 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)                                                                                                                                                                           | MCP                        | Any file                |
| [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly)                                                     | 僅執行您的組織部署的 [hooks](https://code.claude.com/docs/zh-TW/hooks)                                                                                                                                                                                            | Hooks 和自動化             | Managed                 |
| [`allowManagedMcpServersOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedmcpserversonly)                                           | 使受管理的 [MCP](https://code.claude.com/docs/zh-TW/mcp) 允許清單成為唯一適用的清單                                                                                                                                                                               | MCP                        | Managed                 |
| [`allowManagedPermissionRulesOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedpermissionrulesonly)                                 | 使[受管理的設定](https://code.claude.com/docs/zh-TW/managed-settings)成為[權限規則](https://code.claude.com/docs/zh-TW/permissions#managed-settings)的唯一設定來源                                                                                                | 權限設定                   | Managed                 |
| [`alwaysThinkingEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#alwaysthinkingenabled)                                                     | 為每個工作階段關閉[延伸思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)                                                                                                                                                                   | 模型和回應                 | Any file                |
| [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper)                                                                       | 使用您自己的命令產生 [API 認證](https://code.claude.com/docs/zh-TW/authentication#credential-management)                                                                                                                                                          | 驗證和提供者               | Any file                |
| [`askUserQuestionTimeout`](https://code.claude.com/docs/zh-TW/settings-reference#askuserquestiontimeout)                                                   | 讓未回答的問題在閒置時間後[自動繼續](https://code.claude.com/docs/zh-TW/tools-reference#question-auto-continue-timeout)                                                                                                                                           | 介面和終端                 | User or managed         |
| [`attribution`](https://code.claude.com/docs/zh-TW/settings-reference#attribution)                                                                         | 自訂 Claude Code 新增到提交和提取請求的歸屬                                                                                                                                                                                                                       | Git 和歸屬                 | Any file                |
| [`attribution.commit`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-commit)                                                           | 變更或隱藏 Claude Code 新增到提交的預告片                                                                                                                                                                                                                         | Git 和歸屬                 | Any file                |
| [`attribution.pr`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-pr)                                                                   | 變更或隱藏提取請求說明中的歸屬行                                                                                                                                                                                                                                  | Git 和歸屬                 | Any file                |
| [`attribution.sessionUrl`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-sessionurl)                                                   | 從[雲端](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)和[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)提交中省略 claude.ai 工作階段連結                                                                                               | Git 和歸屬                 | Any file                |
| [`autoCompactEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#autocompactenabled)                                                           | 關閉或開啟[自動壓縮](https://code.claude.com/docs/zh-TW/context-window)                                                                                                                                                                                           | 記憶和內容                 | Any file                |
| [`autoCompactWindow`](https://code.claude.com/docs/zh-TW/settings-reference#autocompactwindow)                                                             | 設定在 Claude Code [壓縮](https://code.claude.com/docs/zh-TW/context-window)之前內容有多滿                                                                                                                                                                        | 記憶和內容                 | Any file                |
| [`autoConnectIde`](https://code.claude.com/docs/zh-TW/settings-reference#autoconnectide)                                                                   | 從外部終端自動連線到執行中的 [VS Code](https://code.claude.com/docs/zh-TW/vs-code) 或 [JetBrains](https://code.claude.com/docs/zh-TW/jetbrains#from-external-terminals) IDE                                                                                       | 全域設定設定               | Global config           |
| [`autoContinueAtUsageLimit`](https://code.claude.com/docs/zh-TW/settings-reference#autocontinueatusagelimit)                                               | 在開啟的工作階段中等待，並在 claude.ai 使用限制重設後[自動繼續工作](https://code.claude.com/docs/zh-TW/interactive-mode#wait-for-a-usage-limit-to-reset)                                                                                                          | 介面和終端                 | User or managed         |
| [`autoInstallIdeExtension`](https://code.claude.com/docs/zh-TW/settings-reference#autoinstallideextension)                                                 | 關閉從 VS Code 終端自動安裝 [IDE 擴充功能](https://code.claude.com/docs/zh-TW/vs-code#install-the-extension)                                                                                                                                                      | 全域設定設定               | Global config           |
| [`autoMemoryDirectory`](https://code.claude.com/docs/zh-TW/settings-reference#automemorydirectory)                                                         | 在您選擇的目錄中儲存[自動記憶](https://code.claude.com/docs/zh-TW/memory#auto-memory)                                                                                                                                                                             | 記憶和內容                 | Any file                |
| [`autoMemoryEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#automemoryenabled)                                                             | 關閉或開啟[自動記憶](https://code.claude.com/docs/zh-TW/memory#auto-memory)                                                                                                                                                                                       | 記憶和內容                 | Any file                |
| [`autoMode`](https://code.claude.com/docs/zh-TW/settings-reference#automode)                                                                               | 將您自己的允許和拒絕規則新增到[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)分類器                                                                                                                              | 權限設定                   | User or managed         |
| [`autoMode.classifyAllShell`](https://code.claude.com/docs/zh-TW/settings-reference#automode-classifyallshell)                                             | 透過[自動模式分類器](https://code.claude.com/docs/zh-TW/permission-modes#what-the-classifier-blocks-by-default)傳送每個 shell 命令，即使是狹隘允許規則相符的命令                                                                                                  | 權限設定                   | User or managed         |
| [`autoScrollEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#autoscrollenabled)                                                             | 在全螢幕呈現中[跟隨新輸出](https://code.claude.com/docs/zh-TW/fullscreen#auto-follow)到底部                                                                                                                                                                       | 介面和終端                 | Any file                |
| [`autoUpdatesChannel`](https://code.claude.com/docs/zh-TW/settings-reference#autoupdateschannel)                                                           | 遵循穩定[發行頻道](https://code.claude.com/docs/zh-TW/setup#configure-release-channel)而不是最新版本                                                                                                                                                              | 更新和版本控制             | Any file                |
| [`availableModels`](https://code.claude.com/docs/zh-TW/settings-reference#availablemodels)                                                                 | [限制人員可以選擇的模型](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)                                                                                                                                                                | 模型和回應                 | Any file                |
| [`awaySummaryEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#awaysummaryenabled)                                                           | 關閉當您回到終端時顯示的[工作階段摘要](https://code.claude.com/docs/zh-TW/interactive-mode#session-recap)                                                                                                                                                         | 遠端、桌面和通知           | Any file                |
| [`awsAuthRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#awsauthrefresh)                                                                   | 使用您自己的命令重新整理 `.aws` 中過期的 [Bedrock 認證](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration)                                                                                                                      | 驗證和提供者               | Any file                |
| [`awsCredentialExport`](https://code.claude.com/docs/zh-TW/settings-reference#awscredentialexport)                                                         | 從您自己的命令以 JSON 形式提供 [Bedrock 認證](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration)                                                                                                                                | 驗證和提供者               | Any file                |
| [`axScreenReader`](https://code.claude.com/docs/zh-TW/settings-reference#axscreenreader)                                                                   | 呈現[螢幕閱讀器友善的輸出](https://code.claude.com/docs/zh-TW/accessibility)                                                                                                                                                                                      | 介面和終端                 | Any file                |
| [`bashEditDiffEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#basheditdiffenabled)                                                         | 在每個權限模式中記錄 [Bash 命令變更的檔案](https://code.claude.com/docs/zh-TW/hooks#bash)                                                                                                                                                                         | 介面和終端                 | User or managed         |
| [`bashOutputMaxChars`](https://code.claude.com/docs/zh-TW/settings-reference#bashoutputmaxchars)                                                           | 設定成功命令的[輸出](https://code.claude.com/docs/zh-TW/tools-reference#output-limits)有多少 Claude 內聯接收                                                                                                                                                      | 記憶和內容                 | Any file                |
| [`blockedMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#blockedmarketplaces)                                                         | 為您的組織封鎖[外掛程式市集](https://code.claude.com/docs/zh-TW/plugin-marketplaces)來源                                                                                                                                                                          | 外掛程式和技能             | Managed                 |
| [`browserExternalPageTools`](https://code.claude.com/docs/zh-TW/settings-reference#browserexternalpagetools)                                               | 在[桌面](https://code.claude.com/docs/zh-TW/desktop)瀏覽器窗格中的外部頁面上關閉 Claude 的工具                                                                                                                                                                    | 工具                       | Managed                 |
| [`channelsEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#channelsenabled)                                                                 | 為您的組織允許[頻道](https://code.claude.com/docs/zh-TW/channels#enable-channels-for-your-organization)                                                                                                                                                           | 外掛程式和技能             | Managed                 |
| [`claudeMd`](https://code.claude.com/docs/zh-TW/settings-reference#claudemd)                                                                               | 從受管理的設定注入組織範圍的 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory#deploy-organization-wide-claude-md) 指示                                                                                                                                       | 記憶和內容                 | Managed                 |
| [`claudeMdExcludes`](https://code.claude.com/docs/zh-TW/settings-reference#claudemdexcludes)                                                               | 在記憶載入時跳過特定的 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory#exclude-specific-claude-md-files) 檔案                                                                                                                                               | 記憶和內容                 | Any file                |
| [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)                                                             | 選擇 Claude Code 在刪除[文字記錄](https://code.claude.com/docs/zh-TW/data-usage#data-retention)之前保留多少天                                                                                                                                                     | 隱私和遙測                 | Any file                |
| [`companyAnnouncements`](https://code.claude.com/docs/zh-TW/settings-reference#companyannouncements)                                                       | 在啟動時顯示您組織的公告                                                                                                                                                                                                                                          | 介面和終端                 | Any file                |
| [`copyOnSelect`](https://code.claude.com/docs/zh-TW/settings-reference#copyonselect)                                                                       | 關閉在[全螢幕呈現](https://code.claude.com/docs/zh-TW/fullscreen#use-the-mouse)和代理檢視中使用滑鼠選擇的文字自動複製                                                                                                                                             | 全域設定設定               | Global config           |
| [`crossSessionInbound`](https://code.claude.com/docs/zh-TW/settings-reference#crosssessioninbound)                                                         | 選擇 Claude Code 是否傳遞[來自您其他工作階段的訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)、顯示通知而不傳遞訊息，或拒絕訊息                                                                                        | 代理、工作階段和 worktrees | Any file                |
| [`defaultShell`](https://code.claude.com/docs/zh-TW/settings-reference#defaultshell)                                                                       | 選擇 Bash 或 PowerShell 執行您使用 [`!` 前置詞](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)輸入的 shell 命令                                                                                                                      | 介面和終端                 | Any file                |
| [`deniedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#deniedmcpservers)                                                               | 按 URL、命令或名稱封鎖特定的 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)                                                                                                                                                                                 | MCP                        | Any file                |
| [`desktopSessionCleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#desktopsessioncleanupperioddays)                                 | 為[Claude Desktop 和 Cowork 文字記錄](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)設定天數年齡限制                                                                                                                               | 隱私和遙測                 | User or managed         |
| [`dialogExpiry`](https://code.claude.com/docs/zh-TW/settings-reference#dialogexpiry)                                                                       | 設定 Claude Code 在取消對話之前等待[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)或 SDK 主機回答轉送對話的時間                                                                                                                                     | 介面和終端                 | User or managed         |
| [`diffTool`](https://code.claude.com/docs/zh-TW/settings-reference#difftool)                                                                               | 選擇 Claude 提議的檔案變更是否在 [VS Code](https://code.claude.com/docs/zh-TW/vs-code) 或 [JetBrains](https://code.claude.com/docs/zh-TW/jetbrains#features) diff 檢視器中開啟，或保留在終端中                                                                    | 全域設定設定               | Global config           |
| [`disableAgentView`](https://code.claude.com/docs/zh-TW/settings-reference#disableagentview)                                                               | 關閉背景代理和[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)                                                                                                                                                                                           | 代理、工作階段和 worktrees | Any file                |
| [`disableAllHooks`](https://code.claude.com/docs/zh-TW/settings-reference#disableallhooks)                                                                 | 一次關閉 [hooks](https://code.claude.com/docs/zh-TW/hooks)、自訂[狀態行](https://code.claude.com/docs/zh-TW/statusline)和自訂 [`@` 檔案建議](https://code.claude.com/docs/zh-TW/interactive-mode#quick-commands)命令                                              | Hooks 和自動化             | Any file                |
| [`disableArtifact`](https://code.claude.com/docs/zh-TW/settings-reference#disableartifact)                                                                 | 已棄用；使用 `enableArtifact` 關閉 [Artifact 工具](https://code.claude.com/docs/zh-TW/artifacts)                                                                                                                                                                  | 遠端、桌面和通知           | Any file                |
| [`disableAutoMode`](https://code.claude.com/docs/zh-TW/settings-reference#disableautomode)                                                                 | 從權限模式循環中移除[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)                                                                                                                                              | 權限設定                   | Any file                |
| [`disableBrowserExternalNavigation`](https://code.claude.com/docs/zh-TW/settings-reference#disablebrowserexternalnavigation)                               | 將[桌面](https://code.claude.com/docs/zh-TW/desktop)瀏覽器窗格限制為人員和 Claude 的 localhost                                                                                                                                                                    | 工具                       | Managed                 |
| [`disableBundledSkills`](https://code.claude.com/docs/zh-TW/settings-reference#disablebundledskills)                                                       | 關閉 Claude Code 包含的[技能](https://code.claude.com/docs/zh-TW/skills#bundled-skills)和[工作流程](https://code.claude.com/docs/zh-TW/workflows)                                                                                                                 | 外掛程式和技能             | Any file                |
| [`disableClaudeAiConnectors`](https://code.claude.com/docs/zh-TW/settings-reference#disableclaudeaiconnectors)                                             | 關閉 [claude.ai 連接器](https://code.claude.com/docs/zh-TW/mcp#disable-claude-ai-connectors)，使 Claude Code 不會擷取它們                                                                                                                                         | MCP                        | Any file                |
| [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources)                                         | 封鎖透過執行市集宣告的命令安裝的[外掛程式](https://code.claude.com/docs/zh-TW/plugins)                                                                                                                                                                            | 外掛程式和技能             | Managed                 |
| [`disableDeepLinkRegistration`](https://code.claude.com/docs/zh-TW/settings-reference#disabledeeplinkregistration)                                         | 停止 Claude Code 註冊 [`claude-cli://` 處理器](https://code.claude.com/docs/zh-TW/deep-links)                                                                                                                                                                     | 遠端、桌面和通知           | Any file                |
| [`disableDesktopLocalSessions`](https://code.claude.com/docs/zh-TW/settings-reference#disabledesktoplocalsessions)                                         | 關閉在裝置上執行的[桌面代碼工作階段](https://code.claude.com/docs/zh-TW/desktop#local-sessions-on-managed-devices)，只留下 SSH 到其他主機和雲端                                                                                                                   | 遠端、桌面和通知           | Managed                 |
| [`disabledMcpjsonServers`](https://code.claude.com/docs/zh-TW/settings-reference#disabledmcpjsonservers)                                                   | 拒絕來自專案 [`.mcp.json`](https://code.claude.com/docs/zh-TW/mcp#project-scope) 的特定伺服器                                                                                                                                                                     | MCP                        | Any file                |
| [`disableMobileSimulatorTools`](https://code.claude.com/docs/zh-TW/settings-reference#disablemobilesimulatortools)                                         | 在[桌面](https://code.claude.com/docs/zh-TW/desktop) iOS 模擬器窗格中封鎖 Claude 的工具                                                                                                                                                                           | 工具                       | Managed                 |
| [`disableRemoteControl`](https://code.claude.com/docs/zh-TW/settings-reference#disableremotecontrol)                                                       | 在可以啟動的任何地方關閉[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)                                                                                                                                                                             | 遠端、桌面和通知           | Any file                |
| [`disableSideloadFlags`](https://code.claude.com/docs/zh-TW/settings-reference#disablesideloadflags)                                                       | 拒絕側載[外掛程式](https://code.claude.com/docs/zh-TW/plugins)、[子代理](https://code.claude.com/docs/zh-TW/sub-agents)和 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)的 CLI 旗標                                                                         | 企業和受管理的設定         | Managed                 |
| [`disableSkillShellExecution`](https://code.claude.com/docs/zh-TW/settings-reference#disableskillshellexecution)                                           | 停止[技能](https://code.claude.com/docs/zh-TW/skills)和自訂命令執行內聯 shell                                                                                                                                                                                     | 外掛程式和技能             | Any file                |
| [`disableWorkflows`](https://code.claude.com/docs/zh-TW/settings-reference#disableworkflows)                                                               | 為所有人關閉[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)；使用 `enableWorkflows` 自行使用                                                                                                                                                         | Hooks 和自動化             | Any file                |
| [`editorMode`](https://code.claude.com/docs/zh-TW/settings-reference#editormode)                                                                           | 在輸入提示中使用 [vim 快捷鍵](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode)                                                                                                                                                                | 介面和終端                 | Any file                |
| [`effortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#effortlevel)                                                                         | 為沒有已儲存等級的模型設定預設[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)                                                                                                                                                     | 模型和回應                 | Any file                |
| [`emojiCompletionEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#emojicompletionenabled)                                                   | 在提示輸入中關閉 [`:shortcode:` emoji 建議和取代](https://code.claude.com/docs/zh-TW/interactive-mode#emoji-shortcodes)                                                                                                                                           | 介面和終端                 | Any file                |
| [`enableAllProjectMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#enableallprojectmcpservers)                                           | 批准專案 [`.mcp.json`](https://code.claude.com/docs/zh-TW/mcp#project-server-approvals-and-workspace-trust) 檔案中的每個伺服器，無需提示                                                                                                                          | MCP                        | Any file                |
| [`enableArtifact`](https://code.claude.com/docs/zh-TW/settings-reference#enableartifact)                                                                   | 使用任何檔案中的 `false` 關閉 [Artifact 工具](https://code.claude.com/docs/zh-TW/artifacts)；沒有檔案可以將其重新開啟                                                                                                                                             | 遠端、桌面和通知           | Any file                |
| [`enabledMcpjsonServers`](https://code.claude.com/docs/zh-TW/settings-reference#enabledmcpjsonservers)                                                     | 批准來自專案 [`.mcp.json`](https://code.claude.com/docs/zh-TW/mcp#project-server-approvals-and-workspace-trust) 的特定伺服器                                                                                                                                      | MCP                        | Any file                |
| [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins)                                                                   | 按範圍開啟或關閉個別[外掛程式](https://code.claude.com/docs/zh-TW/plugins)                                                                                                                                                                                        | 外掛程式和技能             | Any file                |
| [`enableWorkflows`](https://code.claude.com/docs/zh-TW/settings-reference#enableworkflows)                                                                 | 根據您的計畫預設開啟或關閉[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)                                                                                                                                                                            | Hooks 和自動化             | Any file                |
| [`enforceAvailableModels`](https://code.claude.com/docs/zh-TW/settings-reference#enforceavailablemodels)                                                   | 將 [`/model` 預設選擇](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model)保留在您的 `availableModels` 允許清單內                                                                                                        | 模型和回應                 | Any file                |
| [`env`](https://code.claude.com/docs/zh-TW/settings-reference#env)                                                                                         | 為每個工作階段及其子程序設定[環境變數](https://code.claude.com/docs/zh-TW/env-vars#in-settings-files)                                                                                                                                                             | 記憶和內容                 | Any file                |
| [`externalEditorContext`](https://code.claude.com/docs/zh-TW/settings-reference#externaleditorcontext)                                                     | 當您按下 [Ctrl+G](https://code.claude.com/docs/zh-TW/interactive-mode#general-controls) 編輯時，將 Claude 的最後回應顯示為註解                                                                                                                                    | 全域設定設定               | Global config           |
| [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)                                                   | 為存放庫或組織註冊[市集](https://code.claude.com/docs/zh-TW/plugin-marketplaces)                                                                                                                                                                                  | 外掛程式和技能             | Any file                |
| [`fallbackModel`](https://code.claude.com/docs/zh-TW/settings-reference#fallbackmodel)                                                                     | 為主要模型過載時命名[備份模型](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains)                                                                                                                                                             | 模型和回應                 | Any file                |
| [`fastMode`](https://code.claude.com/docs/zh-TW/settings-reference#fastmode)                                                                               | 為可用的工作階段開啟[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)                                                                                                                                                                                      | 模型和回應                 | Any file                |
| [`fastModePerSessionOptIn`](https://code.claude.com/docs/zh-TW/settings-reference#fastmodepersessionoptin)                                                 | 要求人員在每個工作階段中開啟[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)                                                                                                                                                                              | 模型和回應                 | Any file                |
| [`feedbackDrafts`](https://code.claude.com/docs/zh-TW/settings-reference#feedbackdrafts)                                                                   | 控制 Claude 是否為您排隊[回饋草稿](https://code.claude.com/docs/zh-TW/tools-reference#sendfeedback-tool-behavior)以供審查                                                                                                                                         | 隱私和遙測                 | User or managed         |
| [`feedbackSurveyRate`](https://code.claude.com/docs/zh-TW/settings-reference#feedbacksurveyrate)                                                           | 變更[工作階段品質調查](https://code.claude.com/docs/zh-TW/data-usage#session-quality-surveys)出現的頻率                                                                                                                                                           | 隱私和遙測                 | Any file                |
| [`fileCheckpointingEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#filecheckpointingenabled)                                               | 關閉或開啟 [`/rewind`](https://code.claude.com/docs/zh-TW/checkpointing) 還原的檔案快照                                                                                                                                                                           | 記憶和內容                 | Any file                |
| [`fileSuggestion`](https://code.claude.com/docs/zh-TW/settings-reference#filesuggestion)                                                                   | 從您自己的命令提供 [`@` 檔案自動完成](https://code.claude.com/docs/zh-TW/interactive-mode#quick-commands)                                                                                                                                                         | 介面和終端                 | Any file                |
| [`footerLinksRegexes`](https://code.claude.com/docs/zh-TW/settings-reference#footerlinksregexes)                                                           | 將輸出中的問題或審查 ID 變成[可點擊的連結](https://code.claude.com/docs/zh-TW/statusline#clickable-links)，位於輸入框下方                                                                                                                                         | 介面和終端                 | User or managed         |
| [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl)                                                       | 設定登入畫面連線到的[閘道 URL](https://code.claude.com/docs/zh-TW/claude-apps-gateway#set-the-gateway-url)                                                                                                                                                        | 驗證和提供者               | Managed                 |
| [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod)                                                               | [限制登入](https://code.claude.com/docs/zh-TW/authentication#restrict-login-to-your-organization)到 claude.ai、Claude Console 或[雲端閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway)                                                                | 驗證和提供者               | Any file                |
| [`forceLoginOrgUUID`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginorguuid)                                                             | [將 claude.ai 登入釘選到您的組織](https://code.claude.com/docs/zh-TW/authentication#restrict-login-to-your-organization)；只有受管理的來源才能強制執行                                                                                                            | 驗證和提供者               | Any file                |
| [`forceRemoteSettingsRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#forceremotesettingsrefresh)                                           | 阻止啟動，直到[伺服器受管理的設定](https://code.claude.com/docs/zh-TW/server-managed-settings)被新鮮擷取                                                                                                                                                          | 企業和受管理的設定         | Managed                 |
| [`gatewayInternalNetworks`](https://code.claude.com/docs/zh-TW/settings-reference#gatewayinternalnetworks)                                                 | 讓 `/login` 到達您的組織在內部使用的公開 IPv4 空間上的[雲端閘道](https://code.claude.com/docs/zh-TW/claude-apps-gateway#allow-a-gateway-on-public-address-space-you-own)                                                                                          | 驗證和提供者               | Managed                 |
| [`gcpAuthRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#gcpauthrefresh)                                                                   | 使用您自己的命令重新整理 [Google Cloud 認證](https://code.claude.com/docs/zh-TW/google-vertex-ai#advanced-credential-configuration)                                                                                                                               | 驗證和提供者               | Any file                |
| [`hooks`](https://code.claude.com/docs/zh-TW/settings-reference#hooks)                                                                                     | 在 Claude Code 生命週期中的點執行您自己的命令作為 [hooks](https://code.claude.com/docs/zh-TW/hooks)                                                                                                                                                               | Hooks 和自動化             | Any file                |
| [`httpHookAllowedEnvVars`](https://code.claude.com/docs/zh-TW/settings-reference#httphookallowedenvvars)                                                   | 限制 [HTTP hooks](https://code.claude.com/docs/zh-TW/hooks) 可以在標頭中放入的環境變數                                                                                                                                                                            | Hooks 和自動化             | Any file                |
| [`includeCoAuthoredBy`](https://code.claude.com/docs/zh-TW/settings-reference#includecoauthoredby)                                                         | 已棄用；使用 `attribution` 隱藏或變更提交和 PR 歸屬                                                                                                                                                                                                               | Git 和歸屬                 | Any file                |
| [`includeGitInstructions`](https://code.claude.com/docs/zh-TW/settings-reference#includegitinstructions)                                                   | 從[系統提示](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup)中移除內建的提交和 PR 指示                                                                                                                                                       | Git 和歸屬                 | Any file                |
| [`inputNeededNotifEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#inputneedednotifenabled)                                                 | 當 Claude 在等待您時取得[推播通知](https://code.claude.com/docs/zh-TW/remote-control#mobile-push-notifications)                                                                                                                                                   | 遠端、桌面和通知           | Any file                |
| [`isolatePeerMachines`](https://code.claude.com/docs/zh-TW/settings-reference#isolatepeermachines)                                                         | 在 Claude [傳訊另一台機器上的其中一個工作階段](https://code.claude.com/docs/zh-TW/cross-session-messaging#require-approval-for-cross-machine-messages)之前詢問您                                                                                                  | 代理、工作階段和 worktrees | Any file                |
| [`keybindingFlavor`](https://code.claude.com/docs/zh-TW/settings-reference#keybindingflavor)                                                               | 已棄用且無效；字詞編輯快捷鍵始終[遵循 readline 慣例](https://code.claude.com/docs/zh-TW/interactive-mode#make-ctrl-w-delete-back-to-whitespace)                                                                                                                   | 介面和終端                 | Any file                |
| [`language`](https://code.claude.com/docs/zh-TW/settings-reference#language)                                                                               | 讓 Claude 以英文以外的語言回應                                                                                                                                                                                                                                    | 模型和回應                 | Any file                |
| [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers)                                                             | 為每個使用者提供遠端 [MCP 伺服器](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings)，以及他們新增的伺服器                                                                                                                  | MCP                        | Managed                 |
| [`managedSourcesBehavior`](https://code.claude.com/docs/zh-TW/settings-reference#managedsourcesbehavior)                                                   | 組合您部署的每個[受管理的來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)，而不是單獨使用最高優先順序的來源                                                                                                    | 企業和受管理的設定         | Managed                 |
| [`maxEffortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#maxeffortlevel)                                                                   | 在每個提供者上為每個模型或每個模型上限[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)                                                                                                                                             | 模型和回應                 | Any file                |
| [`minimumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#minimumversion)                                                                   | 保持[自動更新](https://code.claude.com/docs/zh-TW/setup#pin-a-minimum-version)不安裝低於版本的任何內容                                                                                                                                                            | 更新和版本控制             | Any file                |
| [`model`](https://code.claude.com/docs/zh-TW/settings-reference#model)                                                                                     | 變更 Claude Code 開始使用的[模型](https://code.claude.com/docs/zh-TW/model-config#set-a-default-model-for-new-sessions)                                                                                                                                           | 模型和回應                 | Any file                |
| [`modelOverrides`](https://code.claude.com/docs/zh-TW/settings-reference#modeloverrides)                                                                   | [將模型 ID 對應](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version)到您提供者的 ID，例如 Bedrock ARN                                                                                                                                 | 模型和回應                 | Any file                |
| [`modelPicker`](https://code.claude.com/docs/zh-TW/settings-reference#modelpicker)                                                                         | 選擇 [`/model` 選擇器](https://code.claude.com/docs/zh-TW/model-config#available-models)列出的模型，按您自己的順序和您自己的標籤                                                                                                                                  | 模型和回應                 | User or managed         |
| [`modelPricing`](https://code.claude.com/docs/zh-TW/settings-reference#modelpricing)                                                                       | 按您組織的合約費率而不是清單價格報告支出                                                                                                                                                                                                                          | 模型和回應                 | Managed                 |
| [`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings)                                                                     | 為每個模型保留已儲存的[努力等級](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)，或上限一個模型的努力                                                                                                                                       | 模型和回應                 | Any file                |
| [`otelHeadersHelper`](https://code.claude.com/docs/zh-TW/settings-reference#otelheadershelper)                                                             | 使用您自己的命令產生旋轉的 [OpenTelemetry](https://code.claude.com/docs/zh-TW/monitoring-usage#dynamic-headers) 標頭                                                                                                                                              | 驗證和提供者               | Any file                |
| [`outputStyle`](https://code.claude.com/docs/zh-TW/settings-reference#outputstyle)                                                                         | 使用[輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)變更 Claude 的角色、語調和輸出格式                                                                                                                                                                | 模型和回應                 | Any file                |
| [`parentSettingsBehavior`](https://code.claude.com/docs/zh-TW/settings-reference#parentsettingsbehavior)                                                   | 應用或放棄[SDK 或 IDE 主機](https://code.claude.com/docs/zh-TW/managed-settings#let-an-embedding-host-add-policy)在您部署[受管理的設定](https://code.claude.com/docs/zh-TW/managed-settings)時傳遞的限制                                                          | 企業和受管理的設定         | Managed                 |
| [`permissionExplainerEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#permissionexplainerenabled)                                           | 在 v2.1.257 中移除，以及 shell 權限提示上的 `Ctrl+E` 命令說明                                                                                                                                                                                                     | 全域設定設定               | Global config           |
| [`permissions`](https://code.claude.com/docs/zh-TW/settings-reference#permissions)                                                                         | 設定允許、詢問和拒絕規則以及啟動[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)                                                                                                                                                                   | 權限設定                   | Any file                |
| [`permissions.additionalDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-additionaldirectories)                             | 給予 Claude 檔案存取權限到[目前目錄外的目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories)                                                                                                                                                  | 權限設定                   | Any file                |
| [`permissions.allow`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-allow)                                                             | 批准列出的[工具使用](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)，無需提示                                                                                                                                                             | 權限設定                   | Any file                |
| [`permissions.ask`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-ask)                                                                 | 在列出的[工具使用](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)之前始終提示                                                                                                                                                             | 權限設定                   | Any file                |
| [`permissions.blockReadsOutsideWorkingDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-blockreadsoutsideworkingdirectories) | 使檔案工具在每個權限模式中拒絕在[工作目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories)外的讀取                                                                                                                                            | 權限設定                   | Any file                |
| [`permissions.defaultMode`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-defaultmode)                                                 | 設定新工作階段開始的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)                                                                                                                                                | 權限設定                   | Any file                |
| [`permissions.deny`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-deny)                                                               | 封鎖列出的[工具使用](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)，包括保存秘密的檔案的讀取                                                                                                                                             | 權限設定                   | Any file                |
| [`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-disablebypasspermissionsmode)               | 防止任何人進入 [bypassPermissions 模式](https://code.claude.com/docs/zh-TW/permission-modes#skip-all-checks-with-bypasspermissions-mode)                                                                                                                          | 權限設定                   | Any file                |
| [`plansDirectory`](https://code.claude.com/docs/zh-TW/settings-reference#plansdirectory)                                                                   | 選擇 [Plan Mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 寫入計畫檔案的位置                                                                                                                                   | 記憶和內容                 | Any file                |
| [`pluginConfigs`](https://code.claude.com/docs/zh-TW/settings-reference#pluginconfigs)                                                                     | 儲存您提供給[外掛程式](https://code.claude.com/docs/zh-TW/plugins)設定對話的答案                                                                                                                                                                                  | 外掛程式和技能             | User or managed         |
| [`pluginSuggestionMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#pluginsuggestionmarketplaces)                                       | 選擇哪些[市集](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)可以在 `/plugin` 中顯示外掛程式安裝建議                                                                                                                    | 外掛程式和技能             | Managed                 |
| [`pluginTrustMessage`](https://code.claude.com/docs/zh-TW/settings-reference#plugintrustmessage)                                                           | 將您自己的文字新增到[外掛程式](https://code.claude.com/docs/zh-TW/plugins)信任警告                                                                                                                                                                                | 外掛程式和技能             | Managed                 |
| [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper)                                                                       | 執行在啟動時計算[受管理的設定](https://code.claude.com/docs/zh-TW/managed-settings#compute-the-policy-with-a-helper-program)的可執行檔                                                                                                                            | 企業和受管理的設定         | Managed                 |
| [`policyHelper.path`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper-path)                                                             | 命名 Claude Code 執行的[協助程式可執行檔](https://code.claude.com/docs/zh-TW/managed-settings#compute-the-policy-with-a-helper-program)                                                                                                                           | 企業和受管理的設定         | Managed                 |
| [`policyHelper.refreshIntervalMs`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper-refreshintervalms)                                   | 在背景中按間隔重新執行[協助程式](https://code.claude.com/docs/zh-TW/managed-settings#compute-the-policy-with-a-helper-program)                                                                                                                                    | 企業和受管理的設定         | Managed                 |
| [`policyHelper.timeoutMs`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper-timeoutms)                                                   | 設定 Claude Code 等待[協助程式](https://code.claude.com/docs/zh-TW/managed-settings#compute-the-policy-with-a-helper-program)的時間                                                                                                                               | 企業和受管理的設定         | Managed                 |
| [`preferredNotifChannel`](https://code.claude.com/docs/zh-TW/settings-reference#preferrednotifchannel)                                                     | 為工作完成選擇[終端鈴聲或桌面通知](https://code.claude.com/docs/zh-TW/terminal-config#get-a-terminal-bell-or-notification)                                                                                                                                        | 遠端、桌面和通知           | Any file                |
| [`prefersReducedMotion`](https://code.claude.com/docs/zh-TW/settings-reference#prefersreducedmotion)                                                       | [減少或關閉](https://code.claude.com/docs/zh-TW/accessibility#accessibility-settings)微調、閃爍和閃光動畫                                                                                                                                                         | 介面和終端                 | Any file                |
| [`processWrapper`](https://code.claude.com/docs/zh-TW/settings-reference#processwrapper)                                                                   | 在 macOS 和 Linux 上透過[公司啟動器](https://code.claude.com/docs/zh-TW/corporate-launcher)執行 Claude Code 的背景程序                                                                                                                                            | 代理、工作階段和 worktrees | User or managed         |
| [`promptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#promptcachettl)                                                                   | 選擇主要對話的[提示快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)                                                                                                                                                                | 模型和回應                 | Any file                |
| [`promptSuggestionEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#promptsuggestionenabled)                                                 | 隱藏輸入框中灰顯的[提示建議](https://code.claude.com/docs/zh-TW/interactive-mode#prompt-suggestions)                                                                                                                                                              | 介面和終端                 | Any file                |
| [`prUrlTemplate`](https://code.claude.com/docs/zh-TW/settings-reference#prurltemplate)                                                                     | 將 PR 連結指向內部程式碼審查工具而不是 github.com                                                                                                                                                                                                                 | Git 和歸屬                 | Any file                |
| [`remote.defaultEnvironmentId`](https://code.claude.com/docs/zh-TW/settings-reference#remote-defaultenvironmentid)                                         | 為 `claude --cloud` 選擇預設[雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)；自託管 `ccpool_` ID 僅從使用者和受管理的設定以及 `--settings` 讀取                                                                                                 | 遠端、桌面和通知           | Any file                |
| [`remoteControlAtStartup`](https://code.claude.com/docs/zh-TW/settings-reference#remotecontrolatstartup)                                                   | 當工作階段開始時自動連線[遠端控制](https://code.claude.com/docs/zh-TW/remote-control#enable-remote-control-for-all-sessions)                                                                                                                                      | 遠端、桌面和通知           | Any file                |
| [`requiredMaximumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#requiredmaximumversion)                                                   | [拒絕在](https://code.claude.com/docs/zh-TW/setup#pin-a-minimum-version)您的組織允許的版本更新的版本上啟動                                                                                                                                                        | 更新和版本控制             | Managed                 |
| [`requiredMinimumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#requiredminimumversion)                                                   | [拒絕在](https://code.claude.com/docs/zh-TW/setup#pin-a-minimum-version)您的組織要求的版本更舊的版本上啟動                                                                                                                                                        | 更新和版本控制             | Managed                 |
| [`respectGitignore`](https://code.claude.com/docs/zh-TW/settings-reference#respectgitignore)                                                               | 將 gitignored 檔案保留在 [`@` 檔案選擇器](https://code.claude.com/docs/zh-TW/interactive-mode#quick-commands)之外                                                                                                                                                 | 介面和終端                 | Any file                |
| [`respondToBashCommands`](https://code.claude.com/docs/zh-TW/settings-reference#respondtobashcommands)                                                     | 停止 Claude 在 [`!` shell 命令](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)執行後回應                                                                                                                                             | 介面和終端                 | Any file                |
| [`sandbox`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox)                                                                                 | 在 macOS、Linux 和 WSL2 上[隔離 Bash 命令](https://code.claude.com/docs/zh-TW/sandboxing)與您的檔案系統和網路                                                                                                                                                     | 沙箱設定                   | Any file                |
| [`sandbox.allowAppleEvents`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-allowappleevents)                                               | 讓[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令在 macOS 上傳送 Apple Events                                                                                                                                                                         | 沙箱設定                   | User or managed         |
| [`sandbox.allowUnsandboxedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-allowunsandboxedcommands)                               | 讓 Claude 在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch)外重試被封鎖的命令，或禁止它                                                                                                                                  | 沙箱設定                   | Any file                |
| [`sandbox.autoAllowBashIfSandboxed`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-autoallowbashifsandboxed)                               | 執行[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing#auto-allow-mode)命令，無需權限提示                                                                                                                                                                     | 沙箱設定                   | Any file                |
| [`sandbox.bwrapPath`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-bwrappath)                                                             | 將[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)指向 `PATH` 外的 bubblewrap 二進位檔                                                                                                                                                                       | 沙箱設定                   | Managed                 |
| [`sandbox.credentials`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials)                                                         | 在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials)內隱藏或遮罩認證檔案和變數                                                                                                                                                             | 沙箱設定                   | Any file                |
| [`sandbox.credentials.allowPlaintextInject`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-allowplaintextinject)               | 讓[遮罩的認證](https://code.claude.com/docs/zh-TW/sandboxing#mask-credentials)到達受信任的測試網路上的純 HTTP 服務                                                                                                                                                | 沙箱設定                   | User or managed         |
| [`sandbox.credentials.awsPairs`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-awspairs)                                       | 將自訂命名的 AWS 金鑰變數連結到一個認證中，以進行[重新簽署](https://code.claude.com/docs/zh-TW/sandboxing#re-sign-aws-requests)                                                                                                                                   | 沙箱設定                   | User or managed         |
| [`sandbox.credentials.envVars`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-envvars)                                         | 在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#mask-environment-variables)內取消設定或遮罩環境變數                                                                                                                                                        | 沙箱設定                   | Any file                |
| [`sandbox.credentials.files`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-files)                                             | 在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)內封鎖或遮罩認證檔案的讀取                                                                                                                                                           | 沙箱設定                   | Any file                |
| [`sandbox.credentials.sigv4`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-sigv4)                                             | 選擇串流、預簽署或[SigV4A AWS 請求](https://code.claude.com/docs/zh-TW/sandboxing#re-sign-aws-requests)是否失敗或通過                                                                                                                                             | 沙箱設定                   | User or managed         |
| [`sandbox.enabled`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-enabled)                                                                 | 在 macOS、Linux 和 WSL2 上開啟 [Bash 沙箱化](https://code.claude.com/docs/zh-TW/sandboxing#get-started)                                                                                                                                                           | 沙箱設定                   | Any file                |
| [`sandbox.enableWeakerNestedSandbox`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-enableweakernestedsandbox)                             | 在無特權容器內執行 Linux [沙箱](https://code.claude.com/docs/zh-TW/sandboxing)                                                                                                                                                                                    | 沙箱設定                   | Any file                |
| [`sandbox.enableWeakerNetworkIsolation`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-enableweakernetworkisolation)                       | 讓 `gh`、`gcloud` 和 `terraform` 在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#troubleshooting)內的 MITM 代理後面驗證 TLS                                                                                                                                | 沙箱設定                   | Any file                |
| [`sandbox.excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands)                                               | 命名始終在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)外執行的命令                                                                                                                                                                                       | 沙箱設定                   | Any file                |
| [`sandbox.failIfUnavailable`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-failifunavailable)                                             | 當[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)無法使用時拒絕啟動，而不是執行未沙箱化的命令                                                                                                                                                               | 沙箱設定                   | Any file                |
| [`sandbox.filesystem`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem)                                                           | 控制[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing#filesystem-isolation)命令可以讀取和寫入的路徑                                                                                                                                                          | 沙箱設定                   | Any file                |
| [`sandbox.filesystem.allowManagedReadPathsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowmanagedreadpathsonly)       | 停止開發人員重新開啟[您的組織封鎖的讀取路徑](https://code.claude.com/docs/zh-TW/sandboxing#keep-developers-from-widening-the-policy)                                                                                                                              | 沙箱設定                   | Managed                 |
| [`sandbox.filesystem.allowRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowread)                                       | 重新開啟在 [`denyRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-denyread) 封鎖的區域內讀取                                                                                                                                       | 沙箱設定                   | Any file                |
| [`sandbox.filesystem.allowWrite`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowwrite)                                     | 新增[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令可以寫入的路徑                                                                                                                                                                                     | 沙箱設定                   | Any file                |
| [`sandbox.filesystem.denyRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-denyread)                                         | 封鎖[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令從讀取特定路徑                                                                                                                                                                                     | 沙箱設定                   | Any file                |
| [`sandbox.filesystem.denyWrite`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-denywrite)                                       | 封鎖[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令寫入特定路徑                                                                                                                                                                                       | 沙箱設定                   | Any file                |
| [`sandbox.filesystem.disabled`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-disabled)                                         | [關閉檔案系統隔離](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，同時保持網路隔離                                                                                                                                                  | 沙箱設定                   | User or managed         |
| [`sandbox.ignoreViolations`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-ignoreviolations)                                               | 沉默違規報告，以取得命令預期探測的路徑                                                                                                                                                                                                                            | 沙箱設定                   | Any file                |
| [`sandbox.network`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network)                                                                 | 控制[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)命令到達的主機、連接埠和通訊端                                                                                                                                                       | 沙箱設定                   | Any file                |
| [`sandbox.network.allowAllUnixSockets`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowallunixsockets)                         | 讓[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令連線到每個 Unix 通訊端                                                                                                                                                                               | 沙箱設定                   | Any file                |
| [`sandbox.network.allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains)                                   | 預先允許網域，使[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令不會提示它們                                                                                                                                                                           | 沙箱設定                   | Any file                |
| [`sandbox.network.allowLocalBinding`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowlocalbinding)                             | 讓[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令在 macOS 上繫結到 localhost 連接埠                                                                                                                                                                   | 沙箱設定                   | Any file                |
| [`sandbox.network.allowMachLookup`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmachlookup)                                 | 讓 macOS [沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)工具（如 iOS 模擬器或 Playwright）到達其 XPC 服務                                                                                                                                                 | 沙箱設定                   | Any file                |
| [`sandbox.network.allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly)                 | 將網路允許清單鎖定到[受管理的設定](https://code.claude.com/docs/zh-TW/sandboxing#keep-developers-from-widening-the-policy)                                                                                                                                        | 沙箱設定                   | Managed                 |
| [`sandbox.network.allowUnixSockets`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowunixsockets)                               | 列出[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令可以在 macOS 上使用的 Unix 通訊端路徑                                                                                                                                                              | 沙箱設定                   | Any file                |
| [`sandbox.network.deniedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-denieddomains)                                     | 為[沙箱化](https://code.claude.com/docs/zh-TW/sandboxing)命令封鎖網域，即使在允許的萬用字元內                                                                                                                                                                     | 沙箱設定                   | Any file                |
| [`sandbox.network.httpProxyPort`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-httpproxyport)                                     | 透過您自己的代理路由[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#custom-proxy-configuration) HTTP 流量                                                                                                                                                    | 沙箱設定                   | Any file                |
| [`sandbox.network.socksProxyPort`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-socksproxyport)                                   | 透過您自己的代理路由[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#custom-proxy-configuration) SOCKS 流量                                                                                                                                                   | 沙箱設定                   | Any file                |
| [`sandbox.network.strictAllowlist`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-strictallowlist)                                 | 拒絕[允許清單](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)外的主機，而不是提示                                                                                                                                                               | 沙箱設定                   | User or managed         |
| [`sandbox.network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate)                                       | 讓[沙箱](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)代理終止 TLS，以便它可以讀取 HTTPS 請求                                                                                                                                                  | 沙箱設定                   | User or managed         |
| [`sandbox.ripgrep`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-ripgrep)                                                                 | 在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)內使用您自己的 ripgrep 二進位檔                                                                                                                                                                            | 沙箱設定                   | User or managed         |
| [`sandbox.socatPath`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-socatpath)                                                             | 將[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)代理指向 `PATH` 外的 `socat` 二進位檔                                                                                                                                                                      | 沙箱設定                   | Managed                 |
| [`showClearContextOnPlanAccept`](https://code.claude.com/docs/zh-TW/settings-reference#showclearcontextonplanaccept)                                       | 在 [Plan Mode 接受畫面](https://code.claude.com/docs/zh-TW/permission-modes#review-and-approve-a-plan)上顯示「清除內容」選項                                                                                                                                      | 介面和終端                 | Any file                |
| [`showThinkingSummaries`](https://code.claude.com/docs/zh-TW/settings-reference#showthinkingsummaries)                                                     | 查看 Claude [思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)的摘要，而不是摺疊的存根                                                                                                                                                     | 模型和回應                 | Any file                |
| [`showTurnDuration`](https://code.claude.com/docs/zh-TW/settings-reference#showturnduration)                                                               | 隱藏每個回應後的「Cooked for」持續時間                                                                                                                                                                                                                            | 介面和終端                 | Any file                |
| [`skillListingBudgetFraction`](https://code.claude.com/docs/zh-TW/settings-reference#skilllistingbudgetfraction)                                           | 為[技能清單](https://code.claude.com/docs/zh-TW/skills#skill-descriptions-are-cut-short)保留更多或更少的內容                                                                                                                                                      | 記憶和內容                 | Any file                |
| [`skillListingMaxDescChars`](https://code.claude.com/docs/zh-TW/settings-reference#skilllistingmaxdescchars)                                               | 在[技能清單](https://code.claude.com/docs/zh-TW/skills#skill-descriptions-are-cut-short)中上限每個技能的說明長度                                                                                                                                                  | 記憶和內容                 | Any file                |
| [`skillOverrides`](https://code.claude.com/docs/zh-TW/settings-reference#skilloverrides)                                                                   | [隱藏或摺疊技能](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings)，無需編輯其 SKILL.md                                                                                                                                          | 外掛程式和技能             | Any file                |
| [`skipAutoPermissionPrompt`](https://code.claude.com/docs/zh-TW/settings-reference#skipautopermissionprompt)                                               | 跳過 Claude Code 在您自己進入[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)而不是透過內建預設時顯示的一次性通知                                                                                                 | 權限設定                   | User or managed         |
| [`skipDangerousModePermissionPrompt`](https://code.claude.com/docs/zh-TW/settings-reference#skipdangerousmodepermissionprompt)                             | 在 [bypassPermissions 模式](https://code.claude.com/docs/zh-TW/permission-modes#skip-all-checks-with-bypasspermissions-mode)之前跳過確認對話                                                                                                                      | 權限設定                   | User, local, or managed |
| [`skipWebFetchPreflight`](https://code.claude.com/docs/zh-TW/settings-reference#skipwebfetchpreflight)                                                     | 當 Anthropic 無法到達時跳過 [WebFetch 主機名稱檢查](https://code.claude.com/docs/zh-TW/tools-reference#webfetch-tool-behavior)                                                                                                                                    | 隱私和遙測                 | Any file                |
| [`spellcheck`](https://code.claude.com/docs/zh-TW/settings-reference#spellcheck)                                                                           | 在提示輸入中用您安裝的[拼字檢查器](https://code.claude.com/docs/zh-TW/interactive-mode#check-spelling-as-you-type)為拼寫錯誤的單字加底線                                                                                                                          | 介面和終端                 | User or managed         |
| [`spinnerTipsEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#spinnertipsenabled)                                                           | 在 Claude 工作時隱藏微調中的提示                                                                                                                                                                                                                                  | 介面和終端                 | Any file                |
| [`spinnerTipsOverride`](https://code.claude.com/docs/zh-TW/settings-reference#spinnertipsoverride)                                                         | 將您自己的提示新增到微調輪換，或取代內建提示                                                                                                                                                                                                                      | 介面和終端                 | Any file                |
| [`spinnerVerbs`](https://code.claude.com/docs/zh-TW/settings-reference#spinnerverbs)                                                                       | 新增或取代轉身執行時顯示的動詞                                                                                                                                                                                                                                    | 介面和終端                 | Any file                |
| [`sshConfigs`](https://code.claude.com/docs/zh-TW/settings-reference#sshconfigs)                                                                           | 將 [SSH 連線](https://code.claude.com/docs/zh-TW/desktop#pre-configure-ssh-connections-for-your-team)新增到桌面環境下拉式清單                                                                                                                                     | 遠端、桌面和通知           | User or managed         |
| [`sshHostAllowlist`](https://code.claude.com/docs/zh-TW/settings-reference#sshhostallowlist)                                                               | 限制[桌面 SSH 工作階段](https://code.claude.com/docs/zh-TW/desktop#restrict-which-ssh-hosts-users-can-connect-to)可以到達的主機                                                                                                                                   | 遠端、桌面和通知           | Managed                 |
| [`statusLine`](https://code.claude.com/docs/zh-TW/settings-reference#statusline)                                                                           | 執行您自己的命令以在提示下方呈現[狀態行](https://code.claude.com/docs/zh-TW/statusline)                                                                                                                                                                           | 介面和終端                 | Any file                |
| [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces)                                                 | 允許清單[市集](https://code.claude.com/docs/zh-TW/plugin-marketplaces)來源使用者可以新增和安裝                                                                                                                                                                    | 外掛程式和技能             | Managed                 |
| [`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization)                                     | 從使用者和專案來源封鎖[技能](https://code.claude.com/docs/zh-TW/skills)、[代理](https://code.claude.com/docs/zh-TW/sub-agents)、[hooks](https://code.claude.com/docs/zh-TW/hooks) 和 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)                         | 外掛程式和技能             | Managed                 |
| [`strictPluginOnlyCustomization.agents`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization-agents)                       | 將[代理](https://code.claude.com/docs/zh-TW/sub-agents)鎖定到外掛程式和受管理的來源                                                                                                                                                                               | 外掛程式和技能             | Managed                 |
| [`strictPluginOnlyCustomization.hooks`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization-hooks)                         | 將 [hooks](https://code.claude.com/docs/zh-TW/hooks) 鎖定到外掛程式和受管理的來源                                                                                                                                                                                 | 外掛程式和技能             | Managed                 |
| [`strictPluginOnlyCustomization.mcp`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization-mcp)                             | 將 [MCP 伺服器](https://code.claude.com/docs/zh-TW/mcp)鎖定到外掛程式和受管理的來源                                                                                                                                                                               | 外掛程式和技能             | Managed                 |
| [`strictPluginOnlyCustomization.skills`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization-skills)                       | 將[技能](https://code.claude.com/docs/zh-TW/skills)鎖定到外掛程式和受管理的來源                                                                                                                                                                                   | 外掛程式和技能             | Managed                 |
| [`subagentPromptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#subagentpromptcachettl)                                                   | 選擇子代理和主要對話外其他請求的[提示快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)                                                                                                                                              | 模型和回應                 | Any file                |
| [`subagentStatusLine`](https://code.claude.com/docs/zh-TW/settings-reference#subagentstatusline)                                                           | 使用您自己的命令重寫[子代理](https://code.claude.com/docs/zh-TW/sub-agents)工作顯示中的列                                                                                                                                                                         | 介面和終端                 | Any file                |
| [`switchModelsOnFlag`](https://code.claude.com/docs/zh-TW/settings-reference#switchmodelsonflag)                                                           | 自動切換模型或在[安全分類器](https://code.claude.com/docs/zh-TW/model-config#ask-before-switching)標記請求時暫停                                                                                                                                                  | 模型和回應                 | Any file                |
| [`syncClaudeAiPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#syncclaudeaiplugins)                                                         | 停止載入[在您的 claude.ai 帳戶上啟用的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins)並停止下載新的外掛程式                                                                                                                        | 外掛程式和技能             | User, local, or managed |
| [`syncClaudeAiSkills`](https://code.claude.com/docs/zh-TW/settings-reference#syncclaudeaiskills)                                                           | 停止載入[在您的 claude.ai 帳戶上啟用的技能](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave)並停止下載新的技能                                                                                                                                 | 外掛程式和技能             | User, local, or managed |
| [`syntaxHighlightingDisabled`](https://code.claude.com/docs/zh-TW/settings-reference#syntaxhighlightingdisabled)                                           | 在 diffs 和程式碼區塊中關閉語法醒目提示                                                                                                                                                                                                                           | 介面和終端                 | Any file                |
| [`taskOutputMaxChars`](https://code.claude.com/docs/zh-TW/settings-reference#taskoutputmaxchars)                                                           | 設定 Claude 內聯接收多少[背景工作](https://code.claude.com/docs/zh-TW/tools-reference#background-commands)的輸出                                                                                                                                                  | 記憶和內容                 | Any file                |
| [`teammateDefaultModel`](https://code.claude.com/docs/zh-TW/settings-reference#teammatedefaultmodel)                                                       | 在 v2.1.234 中移除；請參閱[指定隊友和模型](https://code.claude.com/docs/zh-TW/agent-teams#specify-teammates-and-models)以了解 Claude Code 如何選擇隊友的模型                                                                                                      | 全域設定設定               | Global config           |
| [`teammateMode`](https://code.claude.com/docs/zh-TW/settings-reference#teammatemode)                                                                       | 選擇[代理團隊隊友顯示](https://code.claude.com/docs/zh-TW/agent-teams#choose-a-display-mode)的方式                                                                                                                                                                | 代理、工作階段和 worktrees | Any file                |
| [`terminalProgressBarEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#terminalprogressbarenabled)                                           | 在支援它的終端中隱藏終端進度列                                                                                                                                                                                                                                    | 介面和終端                 | Any file                |
| [`terminalTitleFromRename`](https://code.claude.com/docs/zh-TW/settings-reference#terminaltitlefromrename)                                                 | 停止 [`/rename`](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions) 和 `--name` 變更終端標籤標題                                                                                                                                                     | 介面和終端                 | Any file                |
| [`theme`](https://code.claude.com/docs/zh-TW/settings-reference#theme)                                                                                     | 選擇介面[色彩主題](https://code.claude.com/docs/zh-TW/terminal-config#match-the-color-theme)，內建或自訂                                                                                                                                                          | 介面和終端                 | Any file                |
| [`timeFormat`](https://code.claude.com/docs/zh-TW/settings-reference#timeformat)                                                                           | 在 12 小時或 24 小時時鐘、UTC 或 strftime 模式中顯示介面中的時間                                                                                                                                                                                                  | 介面和終端                 | Any file                |
| [`timeZone`](https://code.claude.com/docs/zh-TW/settings-reference#timezone)                                                                               | 在時區中顯示介面中的時間，而不是您的系統時區                                                                                                                                                                                                                      | 介面和終端                 | Any file                |
| [`tui`](https://code.claude.com/docs/zh-TW/settings-reference#tui)                                                                                         | 選擇[全螢幕](https://code.claude.com/docs/zh-TW/fullscreen)或經典終端呈現器                                                                                                                                                                                       | 介面和終端                 | Any file                |
| [`ultracode`](https://code.claude.com/docs/zh-TW/settings-reference#ultracode)                                                                             | 讓 Claude 為每個實質性工作規劃[工作流程](https://code.claude.com/docs/zh-TW/workflows#let-claude-decide-with-ultracode)，無需被要求                                                                                                                               | 模型和回應                 | Any file                |
| [`useAutoModeDuringPlan`](https://code.claude.com/docs/zh-TW/settings-reference#useautomodeduringplan)                                                     | 讓[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)分類器在 [Plan Mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 中審查 shell 命令；設定 `false` 以改為取得提示 | 權限設定                   | User, local, or managed |
| [`verbose`](https://code.claude.com/docs/zh-TW/settings-reference#verbose)                                                                                 | 顯示[完整工具輸出](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)而不是截斷的摘要；當兩者都設定時，`viewMode` 優先                                                                                                                                   | 介面和終端                 | Any file                |
| [`viewMode`](https://code.claude.com/docs/zh-TW/settings-reference#viewmode)                                                                               | 在[預設、詳細或焦點檢視](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags)中開始每個工作階段                                                                                                                                                            | 介面和終端                 | Any file                |
| [`vimInsertModeRemaps`](https://code.claude.com/docs/zh-TW/settings-reference#viminsertmoderemaps)                                                         | 將兩鍵 [INSERT 模式序列](https://code.claude.com/docs/zh-TW/interactive-mode#remap-insert-mode-key-sequences)（例如 `jj`）對應到 Escape                                                                                                                           | 介面和終端                 | User or managed         |
| [`voice`](https://code.claude.com/docs/zh-TW/settings-reference#voice)                                                                                     | 開啟[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)並選擇按住或點選模式                                                                                                                                                                            | 介面和終端                 | Any file                |
| [`voiceEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#voiceenabled)                                                                       | 使用較舊的單鍵形式開啟[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)                                                                                                                                                                              | 介面和終端                 | Any file                |
| [`wheelScrollAccelerationEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#wheelscrollaccelerationenabled)                                   | 在全螢幕呈現中關閉[滑鼠滾輪加速](https://code.claude.com/docs/zh-TW/fullscreen#mouse-wheel-scrolling)                                                                                                                                                             | 介面和終端                 | Any file                |
| [`workflowKeywordTriggerEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#workflowkeywordtriggerenabled)                                     | 讓提示中的字詞 `ultracode` 啟動[工作流程](https://code.claude.com/docs/zh-TW/workflows)；設定 `false` 以輸入它而不啟動一個                                                                                                                                        | Hooks 和自動化             | Any file                |
| [`workflowSizeGuideline`](https://code.claude.com/docs/zh-TW/settings-reference#workflowsizeguideline)                                                     | 設定 Claude 在[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)中的目標代理計數                                                                                                                                                                        | Hooks 和自動化             | Any file                |
| [`worktree`](https://code.claude.com/docs/zh-TW/settings-reference#worktree)                                                                               | 設定 Claude Code 如何建立 git [worktrees](https://code.claude.com/docs/zh-TW/worktrees)                                                                                                                                                                           | 代理、工作階段和 worktrees | Any file                |
| [`worktree.baseRef`](https://code.claude.com/docs/zh-TW/settings-reference#worktree-baseref)                                                               | 從遠端預設分支或您的本機 HEAD 分支新 [worktrees](https://code.claude.com/docs/zh-TW/worktrees)                                                                                                                                                                    | 代理、工作階段和 worktrees | Any file                |
| [`worktree.bgIsolation`](https://code.claude.com/docs/zh-TW/settings-reference#worktree-bgisolation)                                                       | 讓背景工作階段編輯工作副本，無需 [worktree](https://code.claude.com/docs/zh-TW/worktrees)                                                                                                                                                                         | 代理、工作階段和 worktrees | Any file                |
| [`worktree.sparsePaths`](https://code.claude.com/docs/zh-TW/settings-reference#worktree-sparsepaths)                                                       | 在每個 [worktree](https://code.claude.com/docs/zh-TW/worktrees) 中只簽出您需要的目錄                                                                                                                                                                              | 代理、工作階段和 worktrees | Any file                |
| [`worktree.symlinkDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#worktree-symlinkdirectories)                                         | 將大型目錄符號連結到每個 [worktree](https://code.claude.com/docs/zh-TW/worktrees)，而不是複製它們                                                                                                                                                                 | 代理、工作階段和 worktrees | Any file                |
| [`wslInheritsWindowsSettings`](https://code.claude.com/docs/zh-TW/settings-reference#wslinheritswindowssettings)                                           | 讓 WSL 從 Windows 原則鏈讀取[受管理的設定](https://code.claude.com/docs/zh-TW/managed-settings)                                                                                                                                                                   | 企業和受管理的設定         | Managed                 |

## 模型和回應

選擇 Claude Code 使用的模型及其回應方式。如需了解這些設定如何與 `/model` 指令和環境變數互動，請參閱[模型設定](https://code.claude.com/docs/zh-TW/model-config)。

### `advisorModel`

選擇當 Claude 呼叫伺服器端[顧問工具](https://code.claude.com/docs/zh-TW/advisor)時回答的模型。取消設定以關閉顧問。顧問的能力必須至少與您的主要模型相同。請參閱[選擇顧問模型](https://code.claude.com/docs/zh-TW/advisor#choose-an-advisor-model)以了解接受的配對及選擇未接受的配對時會發生什麼。 您通常不會手動編輯此金鑰。執行 `/advisor` 以開啟選擇器，顯示目前選擇、可以提供建議的模型和**無顧問** 。Claude Code 會將您的選擇儲存到 `~/.claude/settings.json` 中的此金鑰。如果您從[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)用戶端或附加到遠端工作者的工作階段中選擇，該選擇僅適用於該工作階段，不會變更此金鑰。 如果您的帳戶需要[使用額度同意](https://code.claude.com/docs/zh-TW/advisor#fable-advisor-and-usage-credits)，請先執行 `/model fable` 以接受。在您這樣做之前，在 `/advisor` 中選擇 Fable 不會儲存任何內容，Claude Code 會告訴您先執行 `/model fable`。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，為別名 `"fable"`、`"opus"` 或 `"sonnet"` 之一，這些別名會解析為 Claude Code 該模型系列的目前預設版本，或完整模型 ID，例如 `"claude-opus-5"`
- **預設** : 未設定，因此顧問已關閉
- **每個工作階段覆蓋** : `--advisor` 優先於此金鑰一個工作階段。[`CLAUDE_CODE_DISABLE_ADVISOR_TOOL`](https://code.claude.com/docs/zh-TW/env-vars)關閉顧問，此金鑰無法將其重新開啟

settings.json

```
{
  "advisorModel": "opus"
}

```

此金鑰對顧問[不可用](https://code.claude.com/docs/zh-TW/advisor#requirements)的提供者（例如 Amazon Bedrock 和 AWS 上的 Claude Platform）無效。`"fable"` 需要[Fable 存取](https://code.claude.com/docs/zh-TW/advisor#choose-an-advisor-model)。

### `alwaysThinkingEnabled`

透過將此設定為 `false` 來為每個工作階段關閉[延伸思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)。思考預設為開啟，因此 `true` 不會改變任何內容。大多數人透過 `/config` 而不是編輯檔案來設定此項。 在始終思考的模型上，例如 Fable 模型，`false` 無效。在[第三方提供者](https://code.claude.com/docs/zh-TW/third-party-integrations)上，Claude Code 會省略 `thinking` 參數而不是關閉思考，因此自適應推理模型可能仍會思考。在 Anthropic API 上關閉思考時，Claude Code 會傳送努力 `high` 而不是更高級別給它知道[不接受該組合](https://code.claude.com/docs/zh-TW/errors#effort-isnt-available-with-thinking-turned-off)的模型，例如 Opus 5。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 布林值
  - `true`: 無效；思考已經開啟
  - `false`: Claude Code 為每個工作階段關閉延伸思考
- **預設** : 未設定，因此思考對支援它的模型開啟
- **每個工作階段覆蓋** : [`MAX_THINKING_TOKENS`](https://code.claude.com/docs/zh-TW/env-vars)優先於此金鑰一個工作階段：`0` 關閉思考，受相同模型和提供者限制如 `false`，正值開啟思考，即使此金鑰為 `false`。在自適應推理模型上，數字本身被忽略

settings.json

```
{
  "alwaysThinkingEnabled": false
}

```

### `availableModels`

限制人員可以為主要工作階段、[子代理](https://code.claude.com/docs/zh-TW/sub-agents)、[技能](https://code.claude.com/docs/zh-TW/skills)和[顧問](https://code.claude.com/docs/zh-TW/advisor)選擇的模型。受管清單限制 `/model`、`--model` 和開發人員自己檔案中的 `model` 金鑰；清單外的模型無法選擇。單獨來說，這不會觸及預設選項；將其與 [`enforceAvailableModels`](https://code.claude.com/docs/zh-TW/settings-reference#enforceavailablemodels) 配對以實現該目的。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在受管設定中部署以對組織強制執行。
- **類型** : 模型別名或 ID 的陣列
- **預設** : 未設定，因此每個模型都可用

此範例僅允許人員選擇 Sonnet 和 Haiku 模型： settings.json

```
{
  "availableModels": ["sonnet", "haiku"]
}

```

請參閱[限制模型選擇](https://code.claude.com/docs/zh-TW/model-config#restrict-model-selection)。

### `effortLevel`

為您尚未儲存級別的模型設定預設[努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。較低級別在直接任務上更快且更便宜，較高級別在複雜問題上推理更深入。 當您在機器上的互動工作階段中執行 `/effort low`、`medium`、`high` 或 `xhigh` 時，Claude Code 會將級別儲存在 [`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings) 下的活動模型下，而不是寫入此金鑰。在 v2.1.251 之前，`/effort` 寫入此金鑰。 在同一設定檔中，Claude Code 使用模型的儲存級別而不是此金鑰。[`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings)說明跨檔案優先順序。 在附加到遠端工作者的工作階段中，`/effort` 僅適用於該工作階段。在 `-p` 執行或 Agent SDK 中，它也僅適用於該工作階段，[除非模型預設努力有保留](https://code.claude.com/docs/zh-TW/model-config#non-interactive-effort)。[調整努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)列出也僅適用於該工作階段的互動選擇。`/effort` 列印的訊息說明發生了什麼。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，為以下之一：
  - `"low"`: 最少推理，用於短期、範圍內、延遲敏感且不是智慧敏感的任務
  - `"medium"`: 減少成本敏感工作的令牌使用，可以權衡一些智慧
  - `"high"`: 平衡令牌使用和智慧
  - `"xhigh"`: 更深入的推理，令牌支出更高
- **預設** : 未設定
- **每個工作階段覆蓋** : `--effort` 優先於此金鑰一個工作階段，[`CLAUDE_CODE_EFFORT_LEVEL`](https://code.claude.com/docs/zh-TW/env-vars)優先於兩者

settings.json

```
{
  "effortLevel": "xhigh"
}

```

在 Opus 4.7、Opus 4.8 和 Fable 5 上，Claude Code 保留該模型的預設努力，組織設定或內建；[調整努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)說明哪些設定級別的方式結束保留，哪些保留。保留結束後，Claude Code 按 [`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings) 中說明的優先順序解析努力。

### `enforceAvailableModels`

`/model` 選擇器有一個**預設** 選項，當適用時解析為您的[組織預設模型](https://code.claude.com/docs/zh-TW/model-config#organization-default-model)，否則解析為您帳戶類型的預設。[`availableModels`](https://code.claude.com/docs/zh-TW/settings-reference#availablemodels) 允許清單限制您可以命名的模型，但單獨來說它保留**預設** 不變，因此**預設** 仍可解析為清單外的模型。此金鑰關閉該間隙。需要 Claude Code v2.1.175 或更新版本。 當您的組織部署任何受管設定時，Claude Code 僅從受管來源讀取此金鑰，並忽略您其他檔案中的此金鑰。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 布林值
  - `true`: 當**預設** 會解析為 `availableModels` 外的模型時，Claude Code 將其解析為清單中第一個可用模型
  - `false`: **預設** 照常解析，即使解析為 `availableModels` 外的模型
- **預設** : `false`

此範例將命名選擇限制為 Sonnet 和 Haiku 模型，並使**預設** 解析為其中第一個可用的： settings.json

```
{
  "availableModels": ["sonnet", "haiku"],
  "enforceAvailableModels": true
}

```

當 `availableModels` 未設定或為空時，此金鑰無效。請參閱[對預設模型強制執行允許清單](https://code.claude.com/docs/zh-TW/model-config#enforce-the-allowlist-for-the-default-model)。需要 Claude Code v2.1.175 或更新版本。

### `fallbackModel`

命名備份模型供 Claude Code 在您的主要模型過載或不可用時依序嘗試。Claude Code 會為該輪的其餘部分切換到鏈中下一個可用模型，並顯示通知。沒有鏈的情況下，Claude Code 會重試相同模型，然後顯示伺服器的錯誤，您重試或自己切換模型。 切換意味著在備用模型上進行一輪冷[提示快取](https://code.claude.com/docs/zh-TW/prompt-caching#switching-models)；您的下一條訊息首先再次嘗試主要模型。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 模型別名或 ID 的陣列；`"default"` 擴展為預設模型
- **預設** : 未設定，因此失敗的請求不會在另一個模型上重試
- **每個工作階段覆蓋** : `--fallback-model` 優先於此金鑰一個工作階段

此範例在您的主要模型失敗時首先嘗試 Sonnet 5，然後嘗試 Haiku 4.5： settings.json

```
{
  "fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5"]
}

```

與大多數陣列設定不同，此金鑰不會跨設定檔合併：最高優先順序的定義它的檔案提供整個鏈。如果您的專案檔案設定 `["claude-sonnet-5"]`，您的使用者檔案設定 `["claude-haiku-4-5"]`，鏈為 `["claude-sonnet-5"]` 只。Claude Code 從清單中最多保留三個不同的允許模型，忽略其餘的。請參閱[備用模型鏈](https://code.claude.com/docs/zh-TW/model-config#fallback-model-chains)。

### `fastMode`

為可用的工作階段開啟[快速模式](https://code.claude.com/docs/zh-TW/fast-mode)，用於互動工作，例如快速迭代或即時除錯，您想要速度而不是更高的每令牌成本。您通常不會手動編輯此金鑰：執行 `/fast` 會將 `fastMode: true` 寫入 `~/.claude/settings.json`，再次執行以關閉快速模式會移除金鑰。快速模式僅在 Opus 5 和 Opus 4.8 上執行：從另一個模型開啟會將您切換到 Opus，切換到不支援的模型會關閉它。請參閱[在快速模式開啟時切換模型](https://code.claude.com/docs/zh-TW/fast-mode#switch-models-while-fast-mode-is-on)。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 布林值
  - `true`: Claude Code 為可用的工作階段開啟快速模式
  - `false`: 快速模式保持關閉
- **預設** : 未設定，因此快速模式關閉
- **每個工作階段覆蓋** : [`CLAUDE_CODE_DISABLE_FAST_MODE`](https://code.claude.com/docs/zh-TW/env-vars)為一個工作階段關閉快速模式，此金鑰無法將其重新開啟

settings.json

```
{
  "fastMode": true
}

```

### `fastModePerSessionOptIn`

通常，執行 `/fast` 會將 [`fastMode`](https://code.claude.com/docs/zh-TW/settings-reference#fastmode) 儲存到人員的使用者設定，因此快速模式在之後每個工作階段的開始時開啟。將此金鑰設定為 `true` 以停止：儲存的 `fastMode: true` 不再在工作階段開始時開啟快速模式，每個人必須在他們想要的每個工作階段中執行 `/fast`。Claude Code 在其檔案中保留 `fastMode` 金鑰，因此關閉此金鑰會恢復舊行為。Team 或 Enterprise 計畫上的擁有者可以透過[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)在組織範圍內部署它。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 布林值
  - `true`: 儲存的 `fastMode: true` 不再在工作階段開始時開啟快速模式，因此每個人在他們想要的每個工作階段中執行 `/fast`；使用 `--settings` 傳遞的 `fastMode: true` 仍然計為該工作階段，除非受管設定設定此金鑰
  - `false`: 儲存的 `fastMode: true` 在之後每個工作階段的開始時開啟快速模式
- **預設** : `false`

settings.json

```
{
  "fastModePerSessionOptIn": true
}

```

請參閱[需要每個工作階段選擇加入](https://code.claude.com/docs/zh-TW/fast-mode#require-per-session-opt-in)。

### `language`

預設情況下讓 Claude 以英文以外的語言回應。回應沒有固定清單：Claude Code 將值逐字新增到系統提示中，作為始終以該語言回應的指令，因此任何 Claude 可以讀取的語言名稱都有效。Claude Code 不檢查值，因此拼寫錯誤的名稱會按原樣傳遞給 Claude，而不是產生錯誤。相同的值設定[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation#change-the-dictation-language)的語言，它有固定的[支援聽寫語言](https://code.claude.com/docs/zh-TW/voice-dictation#change-the-dictation-language)清單，以及自動生成的工作階段標題。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，任何語言名稱，例如 `"japanese"`、`"spanish"` 或 `"french"`；Claude Code 不驗證它
- **預設** : 未設定；工作階段標題然後符合您對話的語言

settings.json

```
{
  "language": "japanese"
}

```

### `maxEffortLevel`

限制工作階段可以使用的[努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)，保留較低級別可用。任何更高級別都改為在限制處執行，包括來自 `/effort`、`/model` 選擇器、`--effort`、[`CLAUDE_CODE_EFFORT_LEVEL`](https://code.claude.com/docs/zh-TW/env-vars)、技能或子代理的 `effort` frontmatter 或模型自己的預設。Claude Code 在每個請求前自己應用限制，因此它在每個提供者上保留，包括 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry。需要 Claude Code v2.1.267 或更新版本。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在受管設定中部署以對組織強制執行。當多個範圍設定限制時，最低的適用，因此在一個範圍中設定的限制無法從另一個範圍提高
- **類型** : 字串，為 `"low"`、`"medium"`、`"high"`、`"xhigh"` 或 `"max"` 之一。`"max"` 值不設定限制
- **預設** : 未設定，因此無限制適用
- **對 ultracode 的影響** : 低於 `xhigh` 的限制使[ultracode](https://code.claude.com/docs/zh-TW/settings-reference#ultracode)在限制適用的模型上不可用
- **每個模型限制** : 將 `maxEffortLevel` 新增到模型的 [`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings) 項目。該項目僅在設定來源（例如您的使用者設定或一個[受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)）中設定兩者時替換此金鑰。在那裡設定 `"max"` 以豁免模型不受該來源的限制；Claude Code 仍然應用來自其他來源的限制

此範例將每個模型限制在 `medium`，豁免 Sonnet 4.6： settings.json

```
{
  "maxEffortLevel": "medium",
  "modelSettings": {
    "claude-sonnet-4-6": {
      "maxEffortLevel": "max"
    }
  }
}

```

當您的組織也為模型設定[努力限制](https://code.claude.com/docs/zh-TW/model-config#organization-effort-limits)時，兩個限制中較低的適用。

### `model`

設定每個新工作階段使用的模型，因此您不必每次都使用 `/model` 選擇一個。在此設定它不會阻止您在工作階段中期切換。如果您的管理員設定[組織預設模型](https://code.claude.com/docs/zh-TW/model-config#organization-default-model)以覆蓋使用者選擇，即使您在使用者、專案或本機設定中設定此金鑰，您也會獲得該模型。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，模型別名或完整模型 ID
- **預設** : 未設定，因此 Claude Code 使用您帳戶的預設模型
- **每個工作階段覆蓋** : `--model` 優先於 [`ANTHROPIC_MODEL`](https://code.claude.com/docs/zh-TW/env-vars)，兩者優先於此金鑰一個工作階段，包括優先於受管 `model`；[`availableModels`](https://code.claude.com/docs/zh-TW/settings-reference#availablemodels) 清單仍然適用於選擇

settings.json

```
{
  "model": "claude-sonnet-5"
}

```

此處的值優先於 [`ANTHROPIC_DEFAULT_MODEL`](https://code.claude.com/docs/zh-TW/model-config#set-a-default-model-for-new-sessions)，Claude Code 僅在沒有其他內容選擇模型時使用。

### `modelOverrides`

將 Anthropic 模型 ID 對應到提供者特定的模型 ID，例如 Amazon Bedrock 推論設定檔 ARN。每個模型選擇器項目然後在呼叫提供者 API 時使用其對應的值。管理員在[Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version)上使用此項以將每個模型版本路由到特定推論設定檔、版本名稱或部署，以進行治理、成本分配或區域路由。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 將模型 ID 對應到提供者模型 ID 的物件
- **預設** : 未設定

此範例將 Opus 4.6 的每個呼叫路由到命名的 Bedrock 推論設定檔： settings.json

```
{
  "modelOverrides": {
    "claude-opus-4-6": "arn:aws:bedrock:us-east-1:123456789012:inference-profile/example"
  }
}

```

請參閱[按版本覆蓋模型 ID](https://code.claude.com/docs/zh-TW/model-config#override-model-ids-per-version)。

### `modelPicker`

列出 `/model` 選擇器提供的模型，按您寫入的順序和您選擇的標籤下，因此選擇器列出您的組織執行的模型，在內建陣容之後或代替它。每行的 `model` 逐字取用，因此它接受 `--model` 接受的任何內容：別名，例如 `opus`、Anthropic 模型 ID 或 Amazon Bedrock、Google Cloud 的 Agent Platform、Microsoft Foundry 或 LLM 閘道的提供者格式 ID。需要 Claude Code v2.1.242 或更新版本。

- **範圍** : [`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 從受管設定、`--settings` 和使用者設定讀取金鑰，忽略專案和本機設定中的金鑰，因此您複製的儲存庫無法重新標籤選擇器。這三個中最高的設定金鑰的提供整個陣容，Claude Code 永遠不會合併來自兩個來源的陣容。
- **類型** : 具有 `options` 陣列和可選 `replaceBuiltInOptions` 布林值的物件
- **預設** : 未設定，因此選擇器顯示內建陣容

此範例在內建陣容之後新增兩個 Bedrock 部署，在您的團隊識別的名稱下： managed-settings.json

```
{
  "modelPicker": {
    "options": [
      { "model": "us.anthropic.claude-opus-4-8", "label": "Opus (production)" },
      {
        "model": "us.anthropic.claude-sonnet-4-6",
        "label": "Sonnet (production)",
        "description": "Day-to-day work"
      }
    ]
  }
}

```

#### `modelPicker` 的欄位

金鑰採用兩個欄位，一個用於行本身，一個用於它們是否替換內建陣容或新增到它。

| 欄位                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 類型                                                               | 它的作用                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `options`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 行的陣列，每行具有必需的 `model` 和可選的 `label` 和 `description` | 選擇器顯示的行，按此順序，除了灰顯的行移到底部。沒有 `label` 時，Claude Code 用它知道的模型的內建名稱標題行，或模型 ID 否則，沒有 `description` 時它寫通用第二行 |
| `replaceBuiltInOptions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 布林值，預設 `false`                                               | 將其設定為 `true` 以僅顯示這些行、**預設** 和工作階段已在使用的模型的行。保留未設定以在內建陣容之後新增這些行                                                    |
| 開啟 `replaceBuiltInOptions` 時，Claude Code 隱藏每個其他行：內建陣容、它為 [`availableModels`](https://code.claude.com/docs/zh-TW/settings-reference#availablemodels) 項目新增的行、[閘道發現](https://code.claude.com/docs/zh-TW/llm-gateway-protocol#model-discovery)找到的模型和 [`ANTHROPIC_CUSTOM_MODEL_OPTION`](https://code.claude.com/docs/zh-TW/model-config#add-a-custom-model-option)。關閉時，Claude Code 跳過內建陣容已涵蓋的列出模型。標籤改變選擇器顯示的內容，不是 Claude Code 執行的模型。 [`availableModels`](https://code.claude.com/docs/zh-TW/settings-reference#availablemodels) 允許清單仍然適用於這些行。在將列出的模型新增到允許清單之前，請閱讀[合併行為](https://code.claude.com/docs/zh-TW/model-config#merge-behavior)：特定模型 ID 縮小其系列的萬用字元項目。Claude Code 也在顯示選擇器前檢查每行與工作階段： |                                                                    |                                                                                                                                                                  |

- **已刪除** : Claude Code 無法提供的行，例如已停用的模型或您的組織無法存取的模型
- **灰顯** : 您還無法選擇的行，顯示原因
- **沒有行倖存** : Claude Code 保留內建陣容，按允許清單過濾如常

Claude Code 刪除它無法解析的行，保留其餘的。請參閱[修復損壞的設定檔](https://code.claude.com/docs/zh-TW/settings#fix-a-broken-settings-file)。

### `modelPricing`

按您的組織支付的費率而不是清單價格報告支出。當您的組織有合約費率時設定，因此開發人員看到的美元數字符合您的帳單。Claude Code 在 `/usage`、[狀態行](https://code.claude.com/docs/zh-TW/statusline)、Agent SDK 的 `total_cost_usd`、[`--max-budget-usd`](https://code.claude.com/docs/zh-TW/cli-reference) 限制和 [OpenTelemetry](https://code.claude.com/docs/zh-TW/monitoring-usage) 成本指標和事件中應用費率。您提供費率：Claude Code 不從您的合約或 Claude 主控台讀取它們。需要 Claude Code v2.1.242 或更新版本。

- **範圍** : [`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。透過伺服器受管設定、MDM 原則、`managed-settings.json` 檔案或[原則協助程式](https://code.claude.com/docs/zh-TW/managed-settings#compute-the-policy-with-a-helper-program)部署金鑰。Claude Code 忽略它在使用者、專案和本機設定中、在 `--settings` 中，以及在 Windows 中的使用者可寫[HKCU 登錄](https://code.claude.com/docs/zh-TW/managed-settings#where-each-mechanism-stores-the-policy)中。使用伺服器受管設定，每個工作階段按清單價格報告成本，直到該工作階段的[設定擷取](https://code.claude.com/docs/zh-TW/server-managed-settings#fetch-and-caching-behavior)已確認設定。嵌入 Claude Code 的主機應用程式，設定 [`CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`](https://code.claude.com/docs/zh-TW/env-vars)，可以透過 SDK [`managedSettings`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options) 選項提供自己的表格，Claude Code 僅在沒有受管來源設定金鑰時使用，且僅在 Claude Code v2.1.246 或更新版本中。
- **類型** : 具有可選 `multiplier` 和可選 `overrides` 對應的物件
- **預設** : 未設定，因此 Claude Code 報告清單價格，除非主機應用程式提供表格

為 Sonnet 4.6 設定合約費率，然後將每個數字（包括 Sonnet 行）減少 15%。單獨設定 `multiplier` 以獲得統一折扣，單獨設定 `overrides` 以獲得每個模型費率，或兩者： managed-settings.json

```
{
  "modelPricing": {
    "multiplier": 0.85,
    "overrides": {
      "claude-sonnet-4-6": {
        "input": 2.4,
        "output": 12,
        "cacheRead": 0.24,
        "cacheWrite": 3
      }
    }
  }
}

```

將 `multiplier` 設定為 1 以上，最多 10，以標記每個數字。標記需要 Claude Code v2.1.271 或更新版本。較早版本會忽略 `multiplier` 超過 1 並顯示警告，保留設定的其餘部分。 如需步驟，包括如何確認費率有效，請參閱[按合約費率報告支出](https://code.claude.com/docs/zh-TW/costs#report-spend-at-your-contracted-rates)。

#### `modelPricing` 的欄位

| 欄位                                                                                                                                                                                                                                                                                                                                                                                          | 類型                                                                                                  | 它的作用                                                                                                                                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `multiplier`                                                                                                                                                                                                                                                                                                                                                                                  | 大於 0 且最多 10 的數字                                                                               | 縮放 Claude Code 計算的每個成本，無論 `overrides` 行是否涵蓋它。1 以下是折扣，1 以上是標記                                                                                                                                   |
| `overrides`                                                                                                                                                                                                                                                                                                                                                                                   | 將模型 ID 對應到具有 `input`、`output`、`cacheRead` 和 `cacheWrite` 的費率物件的對應，每個 0 到 10000 | 該模型的美元每百萬令牌費率，全部四個必需。`cacheWrite` 涵蓋五分鐘和一小時快取寫入。請參閱[`modelPricing` 行適用於哪些模型](https://code.claude.com/docs/zh-TW/settings-reference#which-models-a-modelpricing-row-applies-to) |
| Claude Code 完全按您寫入的方式使用行的費率，不新增快速模式附加費或[僅限美國推論費率](https://platform.claude.com/docs/en/about-claude/pricing)。如果您也設定 `multiplier`，Claude Code 在行的費率之上應用它。Claude Code 刪除具有無法解析的費率或無法解析的 `multiplier` 的行，保留其餘的；請參閱[修復損壞的設定檔](https://code.claude.com/docs/zh-TW/settings#fix-a-broken-settings-file)。 |                                                                                                       |                                                                                                                                                                                                                              |

#### `modelPricing` 行適用於哪些模型

Claude Code 從行的金鑰決定行適用於哪些模型：

- **內建模型的 ID** : Claude Code 本身為內建模型使用的金鑰，無論該金鑰是模型自己的 ID，例如 `claude-sonnet-4-6`，或其 Bedrock、Agent Platform 或 Foundry ID。Claude Code 將行應用於該模型的每個日期快照 ID 和提供者特定 ID。
- **任何其他金鑰** : 不是內建模型 ID 的金鑰，例如閘道模型別名。Claude Code 將行應用於該一個 ID 只。當模型 ID 完全符合您的一個金鑰，也落在由內建模型 ID 鍵入的行下時，Claude Code 使用完全符合。
- **Bedrock 應用程式推論設定檔** : Claude Code 透過您的 [`modelOverrides`](https://code.claude.com/docs/zh-TW/settings-reference#modeloverrides) 對應或 [`bedrock:GetInferenceProfile` 查詢](https://code.claude.com/docs/zh-TW/amazon-bedrock#iam-configuration)將設定檔解析為它路由到的模型後，Claude Code 將該模型的行應用於設定檔。

### `modelSettings`

為您使用的每個模型儲存[努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)。在機器上的互動工作階段中，當您使用 `/effort` 或 `/model` 選擇器的努力滑塊將 `low`、`medium`、`high` 或 `xhigh` 儲存為預設時，Claude Code 在您使用的模型下將該級別寫入此處，因此您很少手動編輯此金鑰。[`effortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#effortlevel) 項目列出 `/effort` 僅適用於該工作階段的工作階段。需要 Claude Code v2.1.251 或更新版本。 手動編輯金鑰以變更或移除您儲存的級別。 此處模型的 `effortLevel` 優先於同一設定檔中的頂級 [`effortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#effortlevel)。跨檔案，Claude Code 分別解析每個模型：最高優先順序[設定檔](https://code.claude.com/docs/zh-TW/settings#settings-precedence)設定該模型的 `effortLevel` 或頂級 `effortLevel` 決定，因此受管設定中的 `effortLevel` 優先於您在使用者設定中儲存的級別。[調整努力級別](https://code.claude.com/docs/zh-TW/model-config#adjust-effort-level)列出還可以覆蓋儲存級別的內容，例如啟動時的 `--effort`。 要限制一個模型的努力而不是設定其級別，將 [`maxEffortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#maxeffortlevel) 欄位新增到該模型的項目。欄位需要 Claude Code v2.1.267 或更新版本。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 將模型名稱對應到具有 `effortLevel` 欄位（`"low"`、`"medium"`、`"high"` 或 `"xhigh"` 之一）、[`maxEffortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#maxeffortlevel) 欄位或兩者的物件的物件
- **預設** : 未設定

Claude Code 在模型的規範名稱下寫入每個項目，例如 `claude-opus-5`，並將該模型的別名、日期後綴、`[1m]` 和識別的提供者特定 ID 符合到相同項目。 此範例將 Opus 5 保留在 `medium`，而其他模型使用其自己的儲存或預設級別： settings.json

```
{
  "modelSettings": {
    "claude-opus-5": {
      "effortLevel": "medium"
    }
  }
}

```

執行 `/effort auto` 以清除您為正在使用的模型儲存的級別。Claude Code 保留其他項目和任何頂級 `effortLevel`。

### `outputStyle`

按名稱選擇[輸出樣式](https://code.claude.com/docs/zh-TW/output-styles)。輸出樣式是改變 Claude 角色、語調和輸出格式的儲存指令集，例如內建的 Explanatory 和 Learning 樣式或您自己寫的。 如果您在工作階段期間變更此金鑰，Claude 從您的下一條訊息開始使用新樣式。如需該訊息在提示快取中的成本，請參閱[變更輸出樣式](https://code.claude.com/docs/zh-TW/prompt-caching#changing-output-style)。在 v2.1.251 之前，編輯僅在您執行 `/clear` 或開始新工作階段後適用。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，[內建](https://code.claude.com/docs/zh-TW/output-styles#built-in-output-styles)或[自訂](https://code.claude.com/docs/zh-TW/output-styles#create-a-custom-output-style)輸出樣式的名稱
- **預設** : 未設定，因此 Claude Code 使用預設樣式

此範例選擇內建的 Explanatory 樣式，在任務之間新增教育見解： settings.json

```
{
  "outputStyle": "Explanatory"
}

```

### `promptCacheTtl`

選擇[提示快取](https://code.claude.com/docs/zh-TW/prompt-caching)保留主要對話的時間長度。此金鑰適用於您的互動、`-p` 和 Agent SDK 輪，以及 Claude Code 與它們內聯執行的協助程式。一小時的生命週期在較長的中斷中保持快取溫暖，API [在五分鐘生命週期時以更高費率計費每個快取寫入](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing)。需要 Claude Code v2.1.242 或更新版本。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，為以下之一：
  - `"5m"`: 快取保留五分鐘
  - `"1h"`: 快取保留一小時
- **預設** : 未設定，因此每個主要對話請求獲得[其預設生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#which-ttl-each-request-gets)
- **每個工作階段覆蓋** : [`FORCE_PROMPT_CACHING_5M`](https://code.claude.com/docs/zh-TW/env-vars)優先於所有其他，然後 [`CLAUDE_CODE_PROMPT_CACHE_TTL`](https://code.claude.com/docs/zh-TW/env-vars)，然後此金鑰，最後 [`ENABLE_PROMPT_CACHING_1H`](https://code.claude.com/docs/zh-TW/env-vars)

此範例將主要對話保留在一小時生命週期，子代理保留在五分鐘： settings.json

```
{
  "promptCacheTtl": "1h",
  "subagentPromptCacheTtl": "5m"
}

```

如需每個生命週期的成本，請參閱[快取生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#cache-lifetime)。

### `showThinkingSummaries`

在互動工作階段中查看 Claude 的[延伸思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)摘要。如果您想在使用 `Ctrl+O` 展開思考時看到完整摘要，請設定它。未設定或 `false` 時，Anthropic API 編輯思考區塊，Claude Code 顯示摺疊的存根；第三方提供者不編輯。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 布林值
  - `true`: 當您使用 `Ctrl+O` 展開思考時，您看到完整思考摘要
  - `false`: Anthropic API 編輯思考區塊，Claude Code 顯示摺疊的存根
- **預設** : `false`

settings.json

```
{
  "showThinkingSummaries": true
}

```

編輯僅改變您看到的內容，不改變模型生成的內容。要減少思考支出，[降低預算或禁用思考](https://code.claude.com/docs/zh-TW/model-config#extended-thinking)。

### `subagentPromptCacheTtl`

選擇[提示快取](https://code.claude.com/docs/zh-TW/prompt-caching)保留 Claude Code 在主要對話外進行的請求的時間長度。此金鑰適用於[子代理](https://code.claude.com/docs/zh-TW/sub-agents)、[工作流程](https://code.claude.com/docs/zh-TW/workflows)和 Claude Code 自己的背景和協助程式請求，例如壓縮和工作階段標題。一小時的生命週期在較長的中斷中保持快取溫暖，API [在五分鐘生命週期時以更高費率計費每個快取寫入](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing)。需要 Claude Code v2.1.242 或更新版本。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 字串，為以下之一：
  - `"5m"`: 快取保留五分鐘
  - `"1h"`: 快取保留一小時
- **預設** : 未設定，因此這些請求中的每一個獲得[其預設生命週期](https://code.claude.com/docs/zh-TW/prompt-caching#which-ttl-each-request-gets)
- **每個工作階段覆蓋** : [`FORCE_PROMPT_CACHING_5M`](https://code.claude.com/docs/zh-TW/env-vars)優先於所有其他，然後 [`CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`](https://code.claude.com/docs/zh-TW/env-vars)，然後此金鑰，然後 [`ENABLE_PROMPT_CACHING_1H`](https://code.claude.com/docs/zh-TW/env-vars)，要求每個請求的一小時生命週期。如需子代理自己的 frontmatter 值排名的位置，請參閱[自己選擇 TTL](https://code.claude.com/docs/zh-TW/prompt-caching#choose-the-ttl-yourself)

此範例為子代理和主要對話外的其他請求提供一小時生命週期： settings.json

```
{
  "subagentPromptCacheTtl": "1h"
}

```

此金鑰涵蓋 [`promptCacheTtl`](https://code.claude.com/docs/zh-TW/settings-reference#promptcachettl) 不涵蓋的請求，因此設定兩者以為 Claude Code 進行的每個請求選擇生命週期。如需子代理的快取與主要對話的快取有何不同，請參閱[子代理和快取](https://code.claude.com/docs/zh-TW/prompt-caching#subagents-and-the-cache)。

### `switchModelsOnFlag`

選擇當[安全分類器標記請求](https://code.claude.com/docs/zh-TW/model-config#automatic-model-fallback)時會發生什麼：切換到備用模型並繼續，或暫停以便您可以在切換和編輯提示之間選擇。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在 `/config` 中顯示為**訊息被標記時切換模型** 。
- **類型** : 布林值
  - `true`: Claude Code 切換到備用模型並繼續
  - `false`: 在互動工作階段中，Claude Code 暫停以便您可以在切換和編輯提示之間選擇；在無法顯示對話的地方，例如 `-p` 執行，標記的請求以錯誤結束
- **預設** : `true`，自動切換

settings.json

```
{
  "switchModelsOnFlag": false
}

```

請參閱[切換前詢問](https://code.claude.com/docs/zh-TW/model-config#ask-before-switching)。

### `ultracode`

為[ultracode](https://code.claude.com/docs/zh-TW/workflows#let-claude-decide-with-ultracode)可用的工作階段開始。開啟時，Claude 為每個實質任務規劃工作流程，而不是等待您要求。Claude 僅在[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)為您啟用、您的模型支援 `xhigh` 努力且無[努力限制](https://code.claude.com/docs/zh-TW/model-config#organization-effort-limits)低於 `xhigh` 適用時規劃工作流程。無論如何，`ultracode: true` 在 `xhigh` 努力或當努力限制更低時在限制處執行工作階段。Claude Code 讀取此金鑰但永遠不寫入它：`/effort ultracode` 僅為目前工作階段開啟 ultracode。

- **範圍** : [`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** : 布林值
  - `true`: 工作階段在 `xhigh` 努力開始，當動態工作流程為您啟用、您的模型支援 `xhigh` 且無努力限制低於 `xhigh` 時，ultracode 開啟
  - `false`: 工作階段開始時 ultracode 關閉
- **預設** : 未設定，因此 ultracode 關閉
- **每個工作階段覆蓋** : `/effort ultracode` 為一個工作階段開啟 ultracode，不需此金鑰。`--effort ultracode` 也是，需要 Claude Code v2.1.203 或更新版本

settings.json

```
{
  "ultracode": true
}

```

Ultracode 在 `xhigh` 努力執行工作階段，優先於 `effortLevel` 和 [`modelSettings`](https://code.claude.com/docs/zh-TW/settings-reference#modelsettings) 項目。如果[努力限制](https://code.claude.com/docs/zh-TW/model-config#organization-effort-limits)低於 `xhigh` 適用於模型，例如 [`maxEffortLevel`](https://code.claude.com/docs/zh-TW/settings-reference#maxeffortlevel) 設定，工作階段改為在限制處執行，ultracode 保持關閉。Claude 然後不自己規劃工作流程，`/effort` 不提供 `ultracode`。Agent SDK `apply_flag_settings` 控制請求也接受金鑰。

## 權限設定

決定 Claude 可以在不詢問的情況下執行的操作、工作階段啟動時的權限模式，以及自動模式分類器允許的內容。如需規則語法和權限模型，請參閱[設定權限](https://code.claude.com/docs/zh-TW/permissions)。

### `allowManagedPermissionRulesOnly`

使受管設定成為權限規則的唯一設定來源。Claude Code 隨後會忽略使用者、專案、本機和 `--settings` 檔案中的 `allow`、`ask` 和 `deny` 規則，忽略 `--allowedTools`，隱藏權限提示中的永遠允許選項，並停止儲存新規則。 當[來自嵌入主機的父設定](https://code.claude.com/docs/zh-TW/managed-settings#let-an-embedding-host-add-policy)適用時，Claude Code 會將其視為受管層級的一部分。它捨棄其 `allow` 規則和 `additionalDirectories`，並保留其 `deny` 和 `ask` 規則，除了模式以 `!` 開頭的 `Read` 和 `Edit` 規則。主機無法使用 `!` 規則從受管規則中切割出路徑，無論您是否設定此金鑰。 `--disallowedTools` 規則和目前工作階段的 `deny` 和 `ask` 規則仍然適用，包括在 Claude Code 於工作階段中途重新載入設定之後。它們只會限制，因此無法擴大受管規則授予的權限。在 v2.1.257 之前，Claude Code 在第一次設定重新載入時會捨棄這些命令列和工作階段規則。 如需 `--disallowedTools` 或工作階段規則中的 `!` 模式可以切割出什麼，請參閱 [Read 和 Edit 規則](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：受管設定成為權限規則的唯一設定來源
  - `false`：Claude Code 除了套用受管規則外，還會套用來自使用者、專案、本機和 `--settings` 檔案的權限規則
- **預設值** ：未設定，因此 Claude Code 會套用來自使用者、專案和本機設定以及 `--settings` 的權限規則，以及受管規則

managed-settings.json

```
{
  "allowManagedPermissionRulesOnly": true
}

```

此金鑰不會鎖定 MCP 伺服器允許清單；若要執行此操作，請設定 [`allowManagedMcpServersOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedmcpserversonly)。請參閱[僅受管設定](https://code.claude.com/docs/zh-TW/managed-settings#managed-only-settings)。

### `autoMode`

將您自己的規則新增至[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)分類器封鎖和允許的內容。使用它來告訴分類器您的組織信任哪些儲存庫、貯體和網域，以便它停止封鎖例行的內部操作。分類器隨附[內建的允許和拒絕規則](https://code.claude.com/docs/zh-TW/auto-mode-config#inspect-the-defaults-and-your-effective-config)。在陣列中包含字面字串 `"$defaults"` 以在該位置保留這些內建規則，並在其周圍新增您的規則；省略它以用您的規則取代它們。

- **範圍** ：[`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：物件，包含 `environment`、`allow`、`soft_deny` 和 `hard_deny` 散文規則陣列，加上 [`classifyAllShell`](https://code.claude.com/docs/zh-TW/settings-reference#automode-classifyallshell) 布林值
- **預設值** ：未設定，因此分類器僅使用其[內建規則](https://code.claude.com/docs/zh-TW/auto-mode-config#inspect-the-defaults-and-your-effective-config)

此範例透過 `"$defaults"` 保留內建的 `soft_deny` 規則，並新增一個封鎖 `terraform apply` 的規則： settings.json

```
{
  "autoMode": {
    "soft_deny": ["$defaults", "Never run terraform apply"]
  }
}

```

當多個檔案設定相同的陣列時，Claude Code 會連接這些項目。如需規則格式以及如何套用每個陣列，請參閱[設定自動模式](https://code.claude.com/docs/zh-TW/auto-mode-config)。

### `autoMode.classifyAllShell`

在自動模式啟用時，將每個 Bash 和 PowerShell 命令傳送到自動模式分類器。根據預設，自動模式只會暫停可能執行任意程式碼的允許規則：工具範圍和萬用字元規則（例如 `Bash(*)`）以及解譯器或 shell 包裝器前綴（例如 `Bash(python *)`）。與其他允許規則相符的命令（例如 `Bash(npm test)`）會跳過分類器，除非它帶有[每個命令允許的網域](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode)。當它跳過時，規則的前綴未預期的破壞性引數可能會通過而不被看到。設定此金鑰會暫停工作階段的每個 shell 允許規則，以便分類器看到每個命令。需要 Claude Code v2.1.193 或更新版本。

- **範圍** ：[`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。讀取位置與 [`autoMode`](https://code.claude.com/docs/zh-TW/settings-reference#automode) 相同。
- **類型** ：布林值
  - `true`：在自動模式啟用時，Claude Code 會將每個 Bash 和 PowerShell 命令傳送到分類器，並暫停您的 shell 允許規則；在自動模式外，規則仍然適用
  - `false`：自動模式只會暫停可能執行任意程式碼的允許規則，例如 `Bash(*)` 和 `Bash(python *)`；與任何其他允許規則相符的命令會跳過分類器，除非它帶有[每個命令允許的網域](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode)，每個其他 shell 命令都會通過它
- **預設值** ：`false`

settings.json

```
{
  "autoMode": {
    "classifyAllShell": true
  }
}

```

請參閱[將所有 shell 命令路由到分類器](https://code.claude.com/docs/zh-TW/auto-mode-config#route-all-shell-commands-through-the-classifier)。需要 Claude Code v2.1.193 或更新版本。

### `disableAutoMode`

從 `Shift+Tab` 循環中移除[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)。任何原本會[以自動模式啟動](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)的工作階段（無論是來自 `--permission-mode auto`、設定檔或內建預設值）都會改為以 `default` 啟動。管理員在受管設定中設定它，以防止其組織中的開發人員使用自動模式。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。最適合在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中使用，使用者無法覆寫它。也接受在 `permissions` 下作為 `permissions.disableAutoMode`。
- **類型** ：字串 `"disable"`
- **預設值** ：未設定

settings.json

```
{
  "disableAutoMode": "disable"
}

```

### `permissions`

控制 Claude 可以在不詢問的情況下使用哪些工具、哪些工具始終提示，以及哪些工具被封鎖，並設定工作階段啟動時的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。下面的每個 `permissions.*` 金鑰都巢狀在此物件下。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：物件，包含 `allow`、`ask`、`deny`、`additionalDirectories`、`blockReadsOutsideWorkingDirectories`、`defaultMode`、`disableBypassPermissionsMode` 和 `disableAutoMode`
- **預設值** ：未設定

此範例在不詢問的情況下核准 `npm run` 命令，在 `git push` 前提示，封鎖 `.env` 的讀取，並以 `acceptEdits` 啟動工作階段： settings.json

```
{
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)"],
    "defaultMode": "acceptEdits"
  }
}

```

三個規則陣列共享一個語法；請參閱 `permissions.allow` 下的[權限規則語法](https://code.claude.com/docs/zh-TW/settings-reference#permission-rule-syntax)。如需來自不同檔案的權限規則如何組合，請參閱[權限規則如何跨範圍合併](https://code.claude.com/docs/zh-TW/permissions#settings-precedence)；如需設定金鑰的一般組合方式，請參閱設定指南上的[設定優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)。

### `useAutoModeDuringPlan`

選擇 Claude Code 是否在計畫模式中使用自動模式分類器來檢查 shell 命令。使用預設值 `true`，分類器在計畫期間檢查每個命令（當自動模式可用且您看不到提示時）。設定 `false` 以針對內建唯讀集之外的每個命令獲得權限提示。在 `/config` 中顯示為**在計畫期間使用自動模式** 。

- **範圍** ：[`User, local, or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。儲存庫無法為您關閉它。
- **類型** ：布林值
  - `true`：與未設定相同；當自動模式可用時，分類器在計畫期間檢查每個 shell 命令，而不是提示您。任何這些檔案中的 `false` 仍然會關閉它
  - `false`：您會針對內建唯讀集之外的每個命令獲得權限提示
- **預設值** ：`true`

settings.json

```
{
  "useAutoModeDuringPlan": false
}

```

### `permissions.allow`

列出 Claude Code 在不詢問您的情況下核准的工具使用。在 MCP 規則中，`*` 只能出現在 `mcp__<server>__` 前綴之後的工具名稱中，例如 `mcp__github__get_*`；它不能出現在伺服器名稱中。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：權限規則字串陣列
- **預設值** ：未設定
- **每個工作階段的覆寫** ：`--allowedTools` 為一個工作階段新增允許規則，任何設定檔中的拒絕規則仍然會封鎖它命名的工具

此範例核准 `git diff` 並讓 Claude Code 在不詢問的情況下讀取您的 `.zshrc`： settings.json

```
{
  "permissions": {
    "allow": ["Bash(git diff *)", "Read(~/.zshrc)"]
  }
}

```

Claude Code 只有在您接受該資料夾的[工作區信任對話](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)後，才會套用專案 `.claude/settings.json` 中的 `allow` 規則。

#### 權限規則語法

權限規則遵循格式 `Tool` 或 `Tool(specifier)`。Claude Code 首先評估 `deny` 規則，然後 `ask`，然後 `allow`，第一個相符項決定結果，無論每個規則的具體程度如何；請參閱[權限規則評估順序](https://code.claude.com/docs/zh-TW/permissions#manage-permissions)。 每一列顯示一個規則形狀及其相符的內容。

| 規則                                                                                                                                                                                                                 | 相符的內容                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| `Bash`                                                                                                                                                                                                               | 每個 Bash 命令            |
| `Bash(npm run *)`                                                                                                                                                                                                    | 以 `npm run` 開頭的命令   |
| `Read(./.env)`                                                                                                                                                                                                       | `.env` 檔案的讀取         |
| `WebFetch(domain:example.com)`                                                                                                                                                                                       | 對 example.com 的擷取請求 |
| 如需完整的規則語法，包括萬用字元行為、Read、Edit、WebFetch、MCP 和 Agent 規則的工具特定模式，以及 Bash 模式的安全限制，請參閱[權限規則語法](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax)。 |                           |

### `permissions.ask`

列出即使在原本會核准它們的權限模式（例如 `acceptEdits` 或 `bypassPermissions`）中也會提示您確認的工具使用。在 `dontAsk` 模式中，Claude Code 會拒絕相符的工具使用，而不是提示。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：權限規則字串陣列
- **預設值** ：未設定

settings.json

```
{
  "permissions": {
    "ask": ["Bash(git push *)"]
  }
}

```

### `permissions.deny`

列出 Claude Code 封鎖的工具使用。將其用於保存 API 金鑰、機密或環境值的檔案：Claude Code 會從檔案探索和搜尋結果中排除相符的檔案，拒絕讀取它們，並在相符的路徑上封鎖 [Edit 和 Write 工具](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)。 Read 和 Edit 拒絕規則適用於 Claude 的內建檔案工具、Claude Code 在 Bash 中識別的檔案命令（例如 `cat`、`head`、`tail`、`sed` 和 `tee`）以及 Bash [重新導向](https://code.claude.com/docs/zh-TW/permissions#redirections)的目標（例如 `> file` 和 `< file`）；它們不適用於讀取檔案而不命名它們的命令（例如 `grep -r pattern .`）或任意子程序，因此如需作業系統層級的強制執行，請[啟用沙箱](https://code.claude.com/docs/zh-TW/sandboxing)。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：權限規則字串陣列
- **預設值** ：未設定
- **每個工作階段的覆寫** ：`--disallowedTools` 在此金鑰旁邊為一個工作階段新增拒絕規則

此範例拒絕讀取 `.env` 檔案、`secrets` 目錄和認證檔案，並封鎖 `curl` 命令： settings.json

```
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.json)",
      "Bash(curl *)"
    ]
  }
}

```

工具名稱接受 glob 模式，因此 `"*"` 拒絕每個工具，`"mcp__*"` 拒絕每個 MCP 工具。只要任何其他工具仍然可供 Claude 使用，Claude Code 就會忽略 [`EndConversation`](https://code.claude.com/docs/zh-TW/tools-reference#endconversation-tool-behavior) 工具的拒絕規則。`Bash` 拒絕規則與 Claude 寫入的命令相符，因此 `Bash(curl *)` 不會停止 `/usr/bin/curl` 或 `sh -c 'curl …'`；請參閱[Bash 規則不相符的內容](https://code.claude.com/docs/zh-TW/permissions#bash-rule-limits)。此金鑰取代已棄用的 `ignorePatterns` 設定。

### `permissions.additionalDirectories`

給予 Claude 檔案存取權限，以存取您啟動的目錄之外的目錄，作為額外的[工作目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories)。大多數 `.claude/` 設定[未從這些目錄探索](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration)。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：目錄路徑陣列
- **預設值** ：未設定
- **每個工作階段的覆寫** ：`--add-dir` 和 `/add-dir` 在此金鑰旁邊為一個工作階段新增目錄

settings.json

```
{
  "permissions": {
    "additionalDirectories": ["../docs/"]
  }
}

```

與 `allow` 規則一樣，專案 `.claude/settings.json` 中的項目只有在您接受該資料夾的[工作區信任對話](https://code.claude.com/docs/zh-TW/permissions#project-allow-rules-and-workspace-trust)後才會生效。

### `permissions.blockReadsOutsideWorkingDirectories`

停止 Claude 在每個權限模式（包括 `bypassPermissions`）中使用 Read、Grep、Glob 和 LSP 工具讀取工作階段[工作目錄](https://code.claude.com/docs/zh-TW/permissions#working-directories)之外的路徑。通過 Claude Code 識別的檔案命令（例如 `cat`）讀取相符路徑的 Bash 命令會在自動模式和 `bypassPermissions` 模式中提示您。需要 Claude Code v2.1.257 或更新版本。 shell 解析器無法追蹤的 Bash 命令（例如多次變更目錄或執行子 shell 的命令）會在自動模式和 `bypassPermissions` 模式中提示您。即使命令未命名工作目錄外的任何路徑，提示仍然會出現。當命令在[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)中執行且沙箱強制執行封鎖時，此提示不適用。 Claude Code 也會在此處寫入 `true`，當您選擇在[自動模式的提示中封鎖此類讀取（在第一次讀取工作目錄外之前）](https://code.claude.com/docs/zh-TW/permission-modes#first-read-outside-the-working-directories)時。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。如果任何設定來源設定 `true`，則封鎖適用，因此儲存庫的簽入檔案可以為專案開啟封鎖，但無法解除您設定的封鎖。
- **類型** ：布林值
  - `true`：工作目錄外的檔案讀取被封鎖
  - `false`：與未設定相同；任何其他設定檔中的 `true` 仍然會封鎖
- **預設值** ：未設定，因此工作目錄外的讀取遵循您的權限模式和規則

settings.json

```
{
  "permissions": {
    "blockReadsOutsideWorkingDirectories": true
  }
}

```

如果只有儲存庫的簽入設定檔新增目錄，封鎖仍然適用於該處的讀取。當 [`autoMemoryDirectory`](https://code.claude.com/docs/zh-TW/settings-reference#automemorydirectory) 來自專案的 `.claude/settings.json`，或來自被[視為儲存庫提供](https://code.claude.com/docs/zh-TW/permissions#when-your-local-settings-file-needs-trust)的 `.claude/settings.local.json` 時，Claude Code 不會從該目錄載入任何[自動記憶](https://code.claude.com/docs/zh-TW/memory#storage-location)，也不會將任何儲存到其中。Claude Code 本身需要的檔案保持可讀，例如您的技能、外掛程式、規則、代理、命令以及 `~/.claude/` 下的 `CLAUDE.md` 記憶檔案。 當[沙箱](https://code.claude.com/docs/zh-TW/sandboxing)開啟時，封鎖也會拒絕沙箱化命令對工作目錄外的主目錄和掛載磁碟區根目錄的讀取存取。需要批准以[在沙箱外執行](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch)的重試會在 `bypassPermissions` 模式中提示您。工具從您的主目錄讀取的檔案（例如 `~/.gitconfig`）與其餘檔案一起被拒絕；當工具需要它時，使用 [`sandbox.filesystem.allowRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowread) 重新開啟特定路徑。 當工作階段的工作目錄是連結的 [git worktree](https://code.claude.com/docs/zh-TW/worktrees)（包括 Claude Code 在工作階段中途進入的）時，儲存庫的通用 `.git` 目錄對沙箱化命令保持可讀和可寫，因此 git 在該處保持運作。

### `permissions.defaultMode`

設定新工作階段啟動時的[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。當您將其保留為未設定時，工作階段會以您的計畫和表面的[內建預設值](https://code.claude.com/docs/zh-TW/permission-modes#which-mode-a-session-starts-in)啟動。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。`auto` 和 `bypassPermissions` 不會從專案或本機設定生效，因此請改為在 `~/.claude/settings.json` 中設定它們。在 v2.1.257 之前，`bypassPermissions` 會從任何檔案生效。對於 VS Code 擴充功能啟動的對話，Claude Code 只讀取使用者、受管和 `--settings` 值。
- **類型** ：字串，其中之一：
  - `"default"`：Claude Code 只在不詢問的情況下執行讀取
  - `"acceptEdits"`：Claude Code 也在不詢問的情況下執行檔案編輯和常見的檔案系統命令，例如 `mkdir` 和 `mv`
  - `"plan"`：Claude Code 讀取和計畫，但在您核准計畫之前封鎖編輯
  - `"auto"`：Claude Code 執行所有操作，具有背景安全檢查
  - `"dontAsk"`：Claude Code 自動拒絕每個原本會提示的呼叫；讀取、不需要核准的其他操作以及預先核准的工具仍然執行
  - `"bypassPermissions"`：Claude Code 在不詢問的情況下執行所有操作
  - `"manual"`：`"default"` 的別名，在 Claude Code v2.1.200 或更新版本中
- **預設值** ：未設定
- **每個工作階段的覆寫** ：`--permission-mode` 及其 `bypassPermissions` 的等效項 `--dangerously-skip-permissions` 對一個工作階段優先於此金鑰

settings.json

```
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}

```

權限規則分層在每個模式之上：`deny` 規則在每個模式中封鎖，包括 `bypassPermissions`。請參閱[權限模式](https://code.claude.com/docs/zh-TW/permission-modes)。`manual` 命名 CLI 和 VS Code 擴充功能中標記為「Manual」的權限模式；別名需要 Claude Code v2.1.200 或更新版本。在雲端工作階段中，Claude Code 只從此金鑰中接受 `acceptEdits`、`plan`、`default` 和 `auto`。對於 VS Code 擴充功能啟動的對話，請參閱[擴充功能為啟動權限模式讀取的設定](https://code.claude.com/docs/zh-TW/permission-modes#switch-permission-modes)。

### `permissions.disableBypassPermissionsMode`

防止任何人進入 `bypassPermissions` 模式。Claude Code 隨後會拒絕 `--dangerously-skip-permissions` 旗標，並忽略[代理定義](https://code.claude.com/docs/zh-TW/sub-agents#permission-modes)中的 `permissionMode: bypassPermissions`，因此子代理會以父工作階段的權限模式執行。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。通常在[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)中設定以強制執行組織原則。
- **類型** ：字串 `"disable"`
- **預設值** ：未設定
- **每個工作階段的覆寫** ：此金鑰優先於 `--dangerously-skip-permissions`，在設定此金鑰時 Claude Code 會拒絕它

settings.json

```
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}

```

在 v2.1.223 之前，Claude Code 即使在停用繞過時也會套用 frontmatter 權限模式。

### `skipAutoPermissionPrompt`

跳過 Claude Code 在您自己進入自動模式時顯示的一次性通知，描述[自動模式](https://code.claude.com/docs/zh-TW/permission-modes#eliminate-prompts-with-auto-mode)，例如透過您自己的設定或模式選擇器，而不是當內建預設值在其中啟動工作階段時。Claude Code 顯示該通知一次，然後記錄它已顯示，因此此金鑰只在通知尚未出現的地方重要。

- **範圍** ：[`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。儲存庫無法為您設定它。
- **類型** ：布林值
  - `true`：Claude Code 跳過通知
  - `false`：與未設定相同；除非這些檔案中的另一個設定 `true`，否則通知會出現一次
- **預設值** ：未設定，因此通知會出現一次

settings.json

```
{
  "skipAutoPermissionPrompt": true
}

```

### `skipDangerousModePermissionPrompt`

跳過 Claude Code 在工作階段進入 `bypassPermissions` 模式前顯示的確認對話，無論是來自 `--dangerously-skip-permissions` 還是 `defaultMode: "bypassPermissions"`。當您接受該對話一次時，Claude Code 會在您的使用者設定中寫入 `true`。

- **範圍** ：[`User, local, or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。不受信任的儲存庫無法為您跳過對話。
- **類型** ：布林值
  - `true`：Claude Code 在工作階段進入 `bypassPermissions` 模式前跳過確認對話
  - `false`：與未設定相同；除非這些檔案中的另一個設定 `true`，否則對話會出現
- **預設值** ：未設定，因此對話會出現

settings.json

```
{
  "skipDangerousModePermissionPrompt": true
}

```

## Sandbox 設定

將 Claude 執行的命令與您的檔案系統、網路和認證隔離。如需了解沙箱如何運作和平台要求，請參閱 [Sandboxing](https://code.claude.com/docs/zh-TW/sandboxing)。

### `sandbox`

使用 [sandboxing](https://code.claude.com/docs/zh-TW/sandboxing) 將 Claude 執行的 Bash 命令與您的檔案系統和網路隔離。使用 `enabled` 開啟沙箱，然後使用 `filesystem`、`network` 和 `credentials` 子物件縮小或擴大沙箱化命令可以接觸的內容。沙箱在 macOS、Linux 和 WSL2 上執行。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 物件，包含 `enabled`、`failIfUnavailable`、`autoAllowBashIfSandboxed`、`excludedCommands`、`allowUnsandboxedCommands`、`enableWeakerNestedSandbox`、`enableWeakerNetworkIsolation`、`allowAppleEvents`、`bwrapPath`、`socatPath`、`ignoreViolations` 和 `ripgrep`，加上 `filesystem`、`network` 和 `credentials` 物件
- **Default** : 未設定，所以 Claude Code 執行命令時不使用沙箱

這會開啟沙箱、跳過沙箱化命令的權限提示、在沙箱外執行 `docker`、開啟兩個額外的寫入路徑、隱藏您的 AWS 認證檔案，並預先允許 GitHub 和 npm： settings.json

```
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}

```

Claude Code 從優先順序最高的設定範圍取得布林值鍵的值，所以受管的 `enabled` 或 `failIfUnavailable` 會覆蓋開發人員設定的任何內容。它會在工作階段載入的每個設定範圍中合併陣列鍵，所以開發人員可以附加項目；請參閱 [Keep developers from widening the policy](https://code.claude.com/docs/zh-TW/sandboxing#keep-developers-from-widening-the-policy) 以了解僅受管的鎖定。若要為組織要求沙箱，請參閱 [Enforce sandboxing with managed settings](https://code.claude.com/docs/zh-TW/sandboxing#enforce-sandboxing-with-managed-settings)。

### `sandbox.enabled`

為 Bash 命令開啟 [sandboxing](https://code.claude.com/docs/zh-TW/sandboxing)。當您在 `/sandbox` 面板中選擇模式時，Claude Code 會將此鍵寫入目前專案的 `.claude/settings.local.json`；在 `~/.claude/settings.json` 中設定它以沙箱化每個專案。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 沙箱化 Bash 命令
  - `false`: Bash 命令執行時不使用沙箱
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "enabled": true
  }
}

```

在 Linux 和 WSL2 上，沙箱需要 `bubblewrap` 和 `socat`；請參閱 [Set up Linux and WSL2](https://code.claude.com/docs/zh-TW/sandboxing#set-up-linux-and-wsl2)。當沙箱無法啟動時，Claude Code 會顯示警告並執行不使用沙箱的命令，除非您也設定了 [`failIfUnavailable`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-failifunavailable)。

### `sandbox.failIfUnavailable`

當 `sandbox.enabled` 為 `true` 但沙箱無法啟動時（因為缺少相依性或不支援該平台），使 Claude Code 在啟動時以錯誤退出。沒有它，Claude Code 會顯示警告並執行不使用沙箱的命令。在您的組織要求沙箱作為硬性閘道的受管設定中使用它。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: 當 `sandbox.enabled` 為 `true` 但沙箱無法啟動時，Claude Code 在啟動時以錯誤退出
  - `false`: Claude Code 顯示警告並執行不使用沙箱的命令
- **Default** : `false`

這使每台受管機器沙箱化命令或拒絕啟動： managed-settings.json

```
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true
  }
}

```

請參閱 [Enforce sandboxing with managed settings](https://code.claude.com/docs/zh-TW/sandboxing#enforce-sandboxing-with-managed-settings)。

### `sandbox.autoAllowBashIfSandboxed`

讓 Claude Code 執行沙箱化 Bash 命令而不需要權限提示。無法在沙箱中執行的命令仍會經過常規權限流程，`deny` 規則和內容範圍的 `ask` 規則（例如 `Bash(git push *)` ）仍然適用；對於沙箱化命令，會跳過裸 `Bash` ask 規則。將其設定為 `false` 以也透過常規權限流程傳送沙箱化命令，`/sandbox` **Mode** 標籤稱之為常規權限模式。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 執行沙箱化 Bash 命令而不需要權限提示，受 `deny` 規則和內容範圍的 `ask` 規則限制；`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` 關閉自動允許
  - `false`: 沙箱化命令經過常規權限流程，所以您的允許規則和權限模式決定。`/sandbox` **Mode** 標籤稱之為常規權限模式
- **Default** : `true`

這保持沙箱開啟並透過常規權限流程傳送沙箱化命令： settings.json

```
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": false
  }
}

```

請參閱 [Sandbox modes](https://code.claude.com/docs/zh-TW/sandboxing#sandbox-modes) 以了解自動允許模式仍會提示什麼以及它在計畫模式中的行為。

### `sandbox.excludedCommands`

命名 Claude Code 始終在沙箱外執行的命令，例如在沙箱下不起作用的工具。每個項目使用與 `Bash(...)` [permission rule](https://code.claude.com/docs/zh-TW/permissions#permission-rule-syntax) 內容相同的語法：精確命令、前綴（例如 `docker *`）或萬用字元模式。當複合命令的任何部分與項目相符時，Claude Code 執行整個命令而不使用沙箱。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 命令模式陣列
- **Default** : 未設定，所以沒有命令被排除

settings.json

```
{
  "sandbox": {
    "excludedCommands": ["docker *"]
  }
}

```

排除的命令仍會經過常規權限流程。排除是一種便利，不是安全邊界：當工具只需要在特定位置寫入時，優先使用 [`filesystem.allowWrite`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowwrite)。Claude Code 合併工作階段載入的每個設定範圍中的項目，此清單沒有僅受管的鎖定，所以保持受管清單狹窄。

### `sandbox.allowUnsandboxedCommands`

在沙箱阻止命令後，讓 Claude 使用 `dangerouslyDisableSandbox` 參數在沙箱外重試命令。將其設定為 `false` 以便 Claude Code 完全忽略該參數，每個 Claude 執行的命令必須沙箱化或出現在 [`excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands) 中。`/sandbox` **Overrides** 標籤將該狀態顯示為 **Strict sandbox mode** 。在要求嚴格沙箱化的受管設定中使用 `false`。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: 在沙箱阻止命令後，Claude 可以使用 `dangerouslyDisableSandbox` 參數在沙箱外重試命令
  - `false`: Claude Code 忽略該參數，所以每個 Claude 執行的命令都沙箱化或出現在 `excludedCommands` 中
- **Default** : `true`

這為受管設定涵蓋的所有人強制執行嚴格沙箱模式： managed-settings.json

```
{
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false
  }
}

```

不使用沙箱的重試會經過常規權限流程，在手動模式中會出現提示。請參閱 [The unsandboxed retry escape hatch](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch)。 若要查看您在 [`!` shell-mode prompt](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix) 自己輸入的命令何時執行沙箱化，請參閱 [strict sandbox mode](https://code.claude.com/docs/zh-TW/sandboxing#the-unsandboxed-retry-escape-hatch)。

### `sandbox.filesystem`

控制沙箱化命令可以讀取和寫入的路徑。預設情況下，它們可以寫入工作目錄、工作階段臨時目錄以及您使用 `--add-dir`、`/add-dir` 或 `permissions.additionalDirectories` 新增的目錄，並可以讀取檔案系統的其餘部分，包括認證檔案。使用四個路徑清單擴大或縮小該範圍，或使用 `disabled` 關閉檔案系統層。請參閱 [Filesystem isolation](https://code.claude.com/docs/zh-TW/sandboxing#filesystem-isolation) 以了解預設邊界。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 物件，包含 `allowWrite`、`denyWrite`、`denyRead` 和 `allowRead` 陣列，加上 `allowManagedReadPathsOnly` 和 `disabled` 布林值
- **Default** : 未設定，所以預設讀取和寫入邊界適用

這讓沙箱化命令寫入建置目錄和您的 kubeconfig，並隱藏您的 AWS 認證檔案： settings.json

```
{
  "sandbox": {
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials"]
    }
  }
}

```

Claude Code 在 OS 沙箱邊界強制執行這些清單，所以它們適用於沙箱化命令啟動的每個子程序，例如 `kubectl`、`terraform` 或 `npm`，不僅適用於 Claude 的檔案工具。Claude Code 將您的 [permission rules](https://code.claude.com/docs/zh-TW/sandboxing#permission-rules) 新增到相同的清單：`Edit` 允許和拒絕規則到 `allowWrite` 和 `denyWrite`、`Read` 拒絕規則到 `denyRead`，以及 `WebFetch(domain:...)` 允許和拒絕規則到 [`network`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network) 網域清單。 除非設定了僅受管的鎖定，Claude Code 合併工作階段載入的設定檔案中的每個清單。[`allowManagedReadPathsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowmanagedreadpathsonly) 將 `allowRead` 限制為受管設定中的項目，[`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly) 對允許的網域執行相同操作。 [Configure sandboxing](https://code.claude.com/docs/zh-TW/sandboxing#configure-sandboxing) 涵蓋您使用 `--setting-sources` 排除的來源。當您在工作階段期間編輯清單時，Claude Code [applies the change to the running session](https://code.claude.com/docs/zh-TW/settings#when-edits-take-effect)。

#### Sandbox 路徑前綴

`allowWrite`、`denyWrite`、`denyRead`、`allowRead` 和 [`credentials.files`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-files) 中的路徑按其前綴解析：

| 前綴                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 含義                                                             | 範例                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 從檔案系統根目錄的絕對路徑                                       | `/tmp/build` 保持 `/tmp/build`                                         |
| `~/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 相對於主目錄                                                     | `~/.kube` 變成 `$HOME/.kube`                                           |
| `./` 或無前綴                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 相對於專案根目錄（用於專案設定）或 `~/.claude`（用於使用者設定） | `.claude/settings.json` 中的 `./output` 解析為 `<project-root>/output` |
| 絕對路徑的 `//path` 前綴也有效。如果您使用單斜線 `/path` 期望專案相對解析，請切換到 `./path`。此語法不同於 [Read and Edit permission rules](https://code.claude.com/docs/zh-TW/permissions#read-and-edit)，後者使用 `//path` 表示絕對路徑，`/path` 表示專案相對路徑：沙箱檔案系統路徑使用標準慣例，所以 `/tmp/build` 是絕對路徑。 Claude Code 從目錄路徑中去除尾部斜線，所以 `~/.aws` 和 `~/.aws/` 符合相同的目錄。在 v2.1.224 之前，Claude Code 將尾部斜線傳遞給沙箱，Claude 仍然可以讀取或寫入以帶有尾部斜線的 `denyRead` 或 `denyWrite` 項目寫入的路徑下的路徑。 Claude Code 也移除尾部 `/**`，所以 `~/build/**` 和 `~/build` 涵蓋相同的目錄。萬用字元（例如 `*`）是否有效取決於項目所在的清單和平台： |                                                                  |                                                                        |

- **`allowWrite`和`denyWrite`** : 在 macOS 上，萬用字元有效。在 Linux 和 WSL2 上，沙箱掛載具體路徑，所以 Claude Code 在移除尾部 `/**` 後跳過包含 `*`、`?` 或 `[` 的項目，該項目無效。Claude Code 將您的 `Edit` 權限規則中的路徑新增到這些清單，所以相同的限制適用於它們，`/sandbox` 的 **Config** 標籤警告包含萬用字元的 `Edit` 和 `Read` 權限規則。
- **`denyRead`和`allowRead`** : 萬用字元在每個平台上都有效。在 Linux 和 WSL2 上，Claude Code 將讀取項目擴展到它符合的具體路徑，它不對寫入清單執行此操作。

### `sandbox.filesystem.allowWrite`

新增沙箱化命令可以寫入的路徑，超出工作目錄、工作階段臨時目錄以及您使用 `--add-dir`、`/add-dir` 或 `permissions.additionalDirectories` 新增的目錄。當子程序（例如 `kubectl` 或建置工具）需要在專案外寫入時使用它。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 路徑字串陣列，使用 [sandbox path prefixes](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)
- **Default** : 未設定，所以沙箱化命令可以寫入工作目錄、工作階段臨時目錄、您使用 `--add-dir` 或 `/add-dir` 新增的目錄，以及 [`permissions.additionalDirectories`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-additionaldirectories) 中的目錄

這讓建置在 `/tmp/build` 下寫入，讓 `kubectl` 更新您的 kubeconfig： settings.json

```
{
  "sandbox": {
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"]
    }
  }
}

```

Claude Code 合併工作階段載入的每個設定範圍中的項目：使用者、專案、本機和受管路徑結合而不是替換彼此，Claude Code 新增您的 `Edit(...)` 允許權限規則中的路徑。`allowWrite` 項目無法提升 [protected path](https://code.claude.com/docs/zh-TW/sandboxing#protected-paths)。

### `sandbox.filesystem.denyWrite`

阻止沙箱化命令寫入特定路徑，包括在其他可寫入的目錄內的路徑。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 路徑字串陣列，使用 [sandbox path prefixes](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)
- **Default** : 未設定

這防止沙箱化命令更改系統設定或安裝二進位檔案： settings.json

```
{
  "sandbox": {
    "filesystem": {
      "denyWrite": ["/etc", "/usr/local/bin"]
    }
  }
}

```

Claude Code 合併工作階段載入的每個設定範圍中的項目，並新增您的 `Edit(...)` 拒絕權限規則中的路徑。

### `sandbox.filesystem.denyRead`

阻止沙箱化命令讀取特定路徑，例如預設讀取原則會公開的認證檔案。若要保護認證檔案並保持其可透過沙箱代理使用，請改為參閱 [`sandbox.credentials`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials)。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 路徑字串陣列，使用 [sandbox path prefixes](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)
- **Default** : 未設定，所以沙箱化命令保持 [default read access](https://code.claude.com/docs/zh-TW/sandboxing#filesystem-isolation)，包括認證檔案，例如 `~/.aws/credentials`

settings.json

```
{
  "sandbox": {
    "filesystem": {
      "denyRead": ["~/.aws/credentials"]
    }
  }
}

```

Claude Code 合併工作階段載入的每個設定範圍中的項目，並新增您的 `Read(...)` 拒絕權限規則中的路徑。當 [`filesystem.disabled`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-disabled) 為 `true` 時，Claude Code 不強制執行這些項目。

### `sandbox.filesystem.allowRead`

重新開啟 [`denyRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-denyread) 阻止的區域內特定路徑的讀取，以建置僅工作區讀取存取。精確或萬用字元 `denyRead` 項目在更廣泛的 `allowRead` 內保持被阻止，如 [overlap table](https://code.claude.com/docs/zh-TW/sandboxing#configure-sandboxing) 所示。當萬用字元 `denyRead` 項目（例如 `~/**/.env`）符合目錄時，Claude Code 也會阻止讀取其內容。在 v2.1.236 之前的 macOS 上，Claude Code 在更廣泛的 `allowRead` 項目涵蓋它們的任何地方重新開啟萬用字元 `denyRead` 項目符合的路徑，並保持符合目錄的內容可讀。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 路徑字串陣列，使用 [sandbox path prefixes](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)
- **Default** : 未設定

這阻止讀取您的主目錄，除了專案本身： settings.json

```
{
  "sandbox": {
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["."]
    }
  }
}

```

Claude Code 在專案設定中將 `.` 項目解析為專案根目錄，在使用者設定中解析為 `~/.claude`。Claude Code 合併工作階段載入的每個設定檔案中的項目，除非設定了 [`allowManagedReadPathsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowmanagedreadpathsonly)。

### `sandbox.filesystem.allowManagedReadPathsOnly`

僅接受來自受管設定的 [`allowRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowread) 項目，所以開發人員無法重新開啟您的組織阻止的路徑的讀取存取。Claude Code 仍然合併工作階段載入的每個設定範圍中的 `denyRead` 項目。

- **Scope** : [`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 僅接受來自受管設定的 `allowRead` 項目
  - `false`: `allowRead` 項目合併自工作階段載入的每個設定範圍
- **Default** : `false`

這阻止讀取主目錄，重新開啟 `~/work`，並防止開發人員重新開啟任何其他內容： managed-settings.json

```
{
  "sandbox": {
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["~/work"],
      "allowManagedReadPathsOnly": true
    }
  }
}

```

請參閱 [Keep developers from widening the policy](https://code.claude.com/docs/zh-TW/sandboxing#keep-developers-from-widening-the-policy)。

### `sandbox.filesystem.disabled`

跳過檔案系統隔離，同時保持網路隔離。沙箱化命令獲得對主機檔案系統的不受限制的讀取和寫入存取，其網路出口保持限制在 [`network.allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains)。當您沙箱化以控制命令連接的位置而不是它們寫入的內容時使用它。需要 Claude Code v2.1.216 或更新版本。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當受管設定配置 `sandbox.filesystem` 時，或列出帶有 `"mode": "deny"` 的 `sandbox.credentials.files` 項目時，只有受管設定可以設定它。
- **Type** : 布林值
  - `true`: Claude Code 跳過檔案系統隔離並保持網路隔離
  - `false`: 檔案系統隔離保持開啟
- **Default** : `false`，所以檔案系統隔離保持開啟

這使檔案系統開放並將網路出口限制在 GitHub 和 npm： settings.json

```
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "disabled": true
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}

```

關閉該層後，Claude Code 不強制執行 `denyRead` 或 `credentials.files` `deny` 項目，而 `credentials.envVars` 項目和應用的 `mask` 項目保持工作。[`autoAllowBashIfSandboxed`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-autoallowbashifsandboxed) 仍預設為 `true`，所以將其設定為 `false` 以保持提示。請參閱 [Disable filesystem isolation](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation) 以了解可以設定它的完整來源清單以及隔離關閉時的變化。需要 Claude Code v2.1.216 或更新版本。

### `sandbox.ignoreViolations`

沉默沙箱違規報告，針對您期望命令探測並被拒絕的路徑，例如在啟動時檢查 `/etc/hosts` 的工具，所以這些拒絕不會顯示為違規或在 Claude 看到的內容中。沙箱仍然阻止存取；只有報告被抑制。鍵是要與命令相符的子字串，`*` 符合每個命令，值是要為該命令忽略的違規的子字串，例如檔案系統路徑。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 物件，將命令子字串對應到違規子字串陣列，通常是路徑
- **Default** : 未設定，所以每個違規都被報告

settings.json

```
{
  "sandbox": {
    "ignoreViolations": {
      "*": ["/etc/hosts"]
    }
  }
}

```

### `sandbox.enableWeakerNestedSandbox`

在無特權 Docker 容器內執行 Linux 沙箱，其中 bubblewrap 無法掛載新的 `/proc`。相反，內部沙箱綁定掛載容器的現有 `/proc`，這公開了新掛載會隱藏的程序資訊。這降低了安全性；僅當外部容器已提供您需要的隔離時才使用它。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: 內部沙箱綁定掛載容器的現有 `/proc` 而不是掛載新的
  - `false`: 沙箱掛載新的 `/proc`，在無特權 Docker 容器中不起作用
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "enabled": true,
    "enableWeakerNestedSandbox": true
  }
}

```

僅限 Linux 和 WSL2。請參閱 [Bubblewrap fails to start inside a container](https://code.claude.com/docs/zh-TW/sandboxing#troubleshooting)。

### `sandbox.enableWeakerNetworkIsolation`

讓 macOS 上的沙箱化命令到達系統 TLS 信任服務 `com.apple.trustd.agent`。基於 Go 的工具（例如 `gh`、`gcloud` 和 `terraform`）在您使用帶有 MITM 代理和自訂 CA 的 [`network.httpProxyPort`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-httpproxyport) 時需要它來驗證 TLS 憑證。這通過信任服務開啟潛在的資料洩露路徑來降低安全性。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: macOS 上的沙箱化命令可以到達 `com.apple.trustd.agent`
  - `false`: macOS 上的沙箱化命令無法到達系統 TLS 信任服務
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "enabled": true,
    "enableWeakerNetworkIsolation": true
  }
}

```

如果您不使用 MITM 代理，請改為在 [`excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands) 中列出失敗的工具；請參閱 [Go-based CLIs fail TLS verification on macOS](https://code.claude.com/docs/zh-TW/sandboxing#troubleshooting)。

### `sandbox.allowAppleEvents`

讓 macOS 上的沙箱化命令傳送 Apple Events，`open`、`osascript` 和在瀏覽器中開啟 URL 的工具需要它；沒有它們會失敗，錯誤為 `-600`。這移除了程式碼執行隔離：沙箱化命令可以在沒有使用者提示的情況下啟動其他應用程式不使用沙箱，並可以向執行中的應用程式（例如終端機）傳送 AppleScript 命令，受每個應用程式 macOS 自動化同意提示 (TCC) 的限制。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: macOS 上的沙箱化命令可以傳送 Apple Events
  - `false`: macOS 上的沙箱化命令無法傳送 Apple Events，所以 `open` 和 `osascript` 失敗，錯誤為 `-600`
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "enabled": true,
    "allowAppleEvents": true
  }
}

```

若要保持隔離並仍然執行一個這樣的工具，請改為將其新增到 [`excludedCommands`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-excludedcommands)。請參閱 [Apple Events on macOS](https://code.claude.com/docs/zh-TW/sandboxing#security-limitations)。

### `sandbox.ripgrep`

將沙箱指向您自己的 ripgrep 二進位檔案，而不是 Claude Code 使用的，例如當您的平台需要不同建置的 `rg` 時。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 物件，包含 `command`（ripgrep 二進位檔案的路徑）和可選的 `args`（要前置的引數陣列）
- **Default** : 未設定，所以沙箱使用與 Claude Code 相同的 ripgrep 二進位檔案。那是捆綁的二進位檔案，除非您將 [`USE_BUILTIN_RIPGREP`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `0`

settings.json

```
{
  "sandbox": {
    "ripgrep": {
      "command": "/usr/local/bin/rg"
    }
  }
}

```

### `sandbox.bwrapPath`

將沙箱指向安裝在 `PATH` 外的 bubblewrap 二進位檔案，例如在氣隙主機上的供應商副本。Claude Code 將路徑用於啟動相依性檢查和包裝每個沙箱化命令時。

- **Scope** : [`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 僅從受管設定讀取它，以便使用者、專案或本機檔案無法將沙箱指向不同的二進位檔案。
- **Type** : 字串，絕對路徑；Claude Code 丟棄相對路徑並回退到 `PATH` 查詢
- **Default** : 未設定，所以 Claude Code 在 `PATH` 上找到 `bwrap`

managed-settings.json

```
{
  "sandbox": {
    "enabled": true,
    "bwrapPath": "/opt/admin/bwrap"
  }
}

```

僅限 Linux 和 WSL2。

### `sandbox.socatPath`

將沙箱網路代理指向安裝在 `PATH` 外的 `socat` 二進位檔案。

- **Scope** : [`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串，絕對路徑；Claude Code 丟棄相對路徑並回退到 `PATH` 查詢
- **Default** : 未設定，所以 Claude Code 在 `PATH` 上找到 `socat`

managed-settings.json

```
{
  "sandbox": {
    "enabled": true,
    "socatPath": "/opt/admin/socat"
  }
}

```

僅限 Linux 和 WSL2。

### `sandbox.credentials`

宣告認證檔案和環境變數以 [protect from sandboxed commands](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials)。每個項目命名檔案 `path` 或變數 `name` 和 `mode`：`deny` 在沙箱內隱藏認證，`mask` 向沙箱化命令顯示佔位符，同時 [sandbox proxy](https://code.claude.com/docs/zh-TW/sandboxing#mask-credentials) 在出站請求上替換真實值。Claude Code 僅保護您列出的項目；沒有內建認證拒絕清單。需要 Claude Code v2.1.187 或更新版本。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 僅從使用者設定、受管設定和 `--settings` 旗標接受 `mask` 項目、`allowPlaintextInject`、`awsPairs` 和 `sigv4`。
- **Type** : 物件，包含 `files`、`envVars`、`allowPlaintextInject`、`awsPairs` 和 `sigv4`
- **Default** : 未設定，所以沒有認證被保護

這隱藏您的 AWS 認證檔案並從沙箱化命令中移除 `GITHUB_TOKEN`： settings.json

```
{
  "sandbox": {
    "credentials": {
      "files": [{ "path": "~/.aws/credentials", "mode": "deny" }],
      "envVars": [{ "name": "GITHUB_TOKEN", "mode": "deny" }]
    }
  }
}

```

`deny` 檔案保護是檔案系統層的一部分，所以當您 [disable filesystem isolation](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation) 時不適用；環境變數保護仍然適用。需要 Claude Code v2.1.187 或更新版本。

#### 受管設定中的無效認證項目

當受管 `sandbox.credentials` 項目驗證失敗時，Claude Code 盡可能保持保護認證：

- `files` 或 `envVars` 中仍有有效 `path` 或 `name` 和 `mode` 為 `mask` 或 `deny` 的項目（例如其 `extract` 模式沒有捕獲群組的項目）降級為 `mode: "deny"` 並帶有警告，所以認證保持被阻止而不是被遮罩，直到您修復項目。降級的 `files` 項目像明確 `deny` 項目一樣固定 [`filesystem.disabled`](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation)，警告指出如果受管設定關閉檔案系統隔離，其讀取塊不被強制執行。
- 帶有未知 `mode` 或無效 `path` 或 `name` 的項目被去除。
- 每種情況都警告；無論項目是降級還是去除，其餘有效項目仍然被強制執行，完全無效的 `credentials` 值被丟棄，同時 `sandbox` 的其餘部分仍然適用。

適用於 v2.1.191 及更新版本；在 v2.1.221 之前，每個無效項目都被去除。對於具有每個欄位處理的其他受管鍵，請參閱 [Invalid entries in managed settings](https://code.claude.com/docs/zh-TW/managed-settings#invalid-entries-in-managed-settings)。

### `sandbox.credentials.files`

保護認證檔案或目錄免受沙箱化命令。使用 `"mode": "deny"`，Claude Code 在沙箱內阻止路徑的讀取，與 [`sandbox.filesystem.denyRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-denyread) 相同的讀取塊。使用 `"mode": "mask"`，Linux 和 WSL2 上的沙箱化命令讀取檔案的哨兵副本，沙箱代理在該項目的 `injectHosts` 的出站請求上替換真實值；在 macOS 上，檔案在沙箱內不可讀。需要 Claude Code v2.1.187 或更新版本，`"mode": "mask"` 需要 v2.1.221 或更新版本。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 從專案 `.claude/settings.json` 和本機 `.claude/settings.local.json` 丟棄 `mask` 項目。
- **Type** : 物件陣列，每個包含 `path` 和 `"deny"` 或 `"mask"` 的 `mode`，加上可選的 [mask fields for files](https://code.claude.com/docs/zh-TW/settings-reference#mask-fields-for-files)
- **Default** : 未設定，所以沒有認證檔案被保護

這隱藏您的 AWS 認證檔案並遮罩 `gh` hosts 檔案，僅在對 `api.github.com` 的請求上替換真實值： settings.json

```
{
  "sandbox": {
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.config/gh/hosts.yml", "mode": "mask", "injectHosts": ["api.github.com"] }
      ]
    }
  }
}

```

路徑使用與 `sandbox.filesystem.*` 設定相同的 [prefixes](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-path-prefixes)，Claude Code 合併工作階段載入的每個設定範圍中的陣列。[Protect credentials](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) 涵蓋您使用 `--setting-sources` 排除的來源仍然適用的內容。需要 Claude Code v2.1.187 或更新版本；`mask` 項目需要 v2.1.221 或更新版本。 `mask` 替換僅透過沙箱代理執行，所以設定 [`sandbox.network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate) 或 [`allowPlaintextInject`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-allowplaintextinject) 用於純 HTTP 測試網路。`mask` 適用於單個檔案，所以單獨列出每個認證檔案。Claude Code 接受但忽略 `deny` 項目上的 `mask` 欄位。[Mask credential files](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files) 涵蓋接受哪些設定來源以及項目何時回退到 `deny`。

#### 檔案的遮罩欄位

`mask` 項目接受這些可選欄位。沒有 `extract` 或 `decode`，Claude Code 將整個檔案內容替換為一個哨兵。在 macOS 上啟用檔案系統隔離，Claude Code 在 `extract` 或 `decode` 執行前將 `mask` 項目應用為 `deny`；請參閱 [Mask credential files](https://code.claude.com/docs/zh-TW/sandboxing#mask-credential-files)。

| 欄位                                                                                                                                                              | 類型                                                                                                                                                   | 它做什麼                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `extract`                                                                                                                                                         | 字串，至少有一個捕獲群組的正規表達式                                                                                                                   | 僅遮罩每個符合的群組 1 捕獲的文字，所以檔案的其餘部分保持可解析。設定 `decode` 時，Claude Code 檢查每個捕獲作為可能的 JWT，而不是直接替換它。需要 v2.1.221 或更新版本                                                                                                                                                                                                                                                                                                                                                                |
| `onExtractNoMatch`                                                                                                                                                | `"warn"`、`"deny"` 或 `"error"`；預設 `"warn"`                                                                                                         | 當 `extract` 或 `decode` 找不到要遮罩的內容時會發生什麼。`warn` 在沙箱內保持檔案可讀，`deny` 使其不可讀，`error` 停止沙箱設定直到您修復設定。當讀取塊不被強制執行時，Claude Code 將 `deny` 視為 `error`，因為您 [disable filesystem isolation](https://code.claude.com/docs/zh-TW/sandboxing#disable-filesystem-isolation) 或 [`sandbox.filesystem.allowRead`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-filesystem-allowread) 項目重新開啟路徑。需要 v2.1.221 或更新版本；`decode` 情況需要 v2.1.224 或更新版本 |
| `decode`                                                                                                                                                          | 字串 `"jwt"`                                                                                                                                           | 在檔案中找到 JSON Web Tokens (JWTs)，使用內建模式或設定 `extract` 時，驗證每個候選，並將其替換為結構上有效的假令牌，所以沙箱內解碼令牌的程式碼保持工作。當沒有候選驗證時，`onExtractNoMatch` 管理結果。需要 v2.1.224 或更新版本                                                                                                                                                                                                                                                                                                      |
| `maskClaims`                                                                                                                                                      | 字串陣列，至少一個聲明名稱；需要 `decode`                                                                                                              | 僅遮罩每個驗證 JWT 內的命名頂級有效負載聲明並在修改的有效負載周圍重建令牌，所以其他聲明保持可讀。當沒有命名聲明符合時，`onExtractNoMatch` 管理結果。需要 v2.1.224 或更新版本                                                                                                                                                                                                                                                                                                                                                         |
| `maskDuplicates`                                                                                                                                                  | 布林值，預設 `false`                                                                                                                                   | 也替換每個遮罩值在檔案中其他地方的逐字副本，例如貼到註解中的秘密。Claude Code 符合原始子字串，所以為長的、高熵秘密保留它。僅在設定 `extract` 或 `decode` 時查詢。需要 v2.1.221 或更新版本                                                                                                                                                                                                                                                                                                                                            |
| `injectHosts`                                                                                                                                                     | 字串陣列，每個是 [`sandbox.network.allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 也允許的主機 | 縮小沙箱代理替換真實值的主機。未設定時，代理在 `sandbox.network.allowedDomains` 中的每個主機上的請求上替換它。需要 v2.1.221 或更新版本                                                                                                                                                                                                                                                                                                                                                                                               |
| 這僅遮罩 `gh` hosts 檔案中的 `oauth_token` 值，替換檔案中它的每個其他副本，如果模式不符合任何內容則使檔案不可讀，並僅在對 `api.github.com` 的請求上替換真實令牌： |                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| settings.json                                                                                                                                                     |                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

```
{
  "sandbox": {
    "credentials": {
      "files": [
        {
          "path": "~/.config/gh/hosts.yml",
          "mode": "mask",
          "extract": "oauth_token:\\s*(\\S+)",
          "maskDuplicates": true,
          "onExtractNoMatch": "deny",
          "injectHosts": ["api.github.com"]
        }
      ]
    }
  }
}

```

### `sandbox.credentials.envVars`

保護環境變數免受沙箱化命令。使用 `"mode": "deny"`，Claude Code 從沙箱化命令的環境中移除變數。使用 `"mode": "mask"`，沙箱化命令看到每個工作階段的哨兵值，沙箱代理在該項目的 `injectHosts` 的出站請求上替換真實值，所以 `gh` 和 `npm` 等工具保持驗證而不會持有真實認證。需要 Claude Code v2.1.187 或更新版本，`"mode": "mask"` 需要 v2.1.199 或更新版本。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 從專案 `.claude/settings.json` 和本機 `.claude/settings.local.json` 丟棄 `mask` 項目。
- **Type** : 物件陣列，每個包含 `name` 和 `"deny"` 或 `"mask"` 的 `mode`，加上可選的 [mask fields for environment variables](https://code.claude.com/docs/zh-TW/settings-reference#mask-fields-for-environment-variables)
- **Default** : 未設定，所以沒有環境變數被保護

這從沙箱化命令中移除 `NPM_TOKEN` 並遮罩 `GITHUB_TOKEN`，僅在對 `api.github.com` 的請求上替換真實值： settings.json

```
{
  "sandbox": {
    "credentials": {
      "envVars": [
        { "name": "NPM_TOKEN", "mode": "deny" },
        { "name": "GITHUB_TOKEN", "mode": "mask", "injectHosts": ["api.github.com"] }
      ]
    }
  }
}

```

`name` 必須以字母或底線開頭，並僅包含字母、數字和底線。Claude Code 合併工作階段載入的每個設定範圍中的陣列，當相同變數同時出現兩種模式時應用 `deny`。[Protect credentials](https://code.claude.com/docs/zh-TW/sandboxing#protect-credentials) 涵蓋您使用 `--setting-sources` 排除的來源仍然適用的內容。需要 Claude Code v2.1.187 或更新版本；`mask` 項目需要 v2.1.199 或更新版本。 `mask` 替換僅透過沙箱代理執行，所以設定 [`sandbox.network.tlsTerminate`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-tlsterminate) 或 [`allowPlaintextInject`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-allowplaintextinject) 用於純 HTTP 測試網路；請參閱 [Mask environment variables](https://code.claude.com/docs/zh-TW/sandboxing#mask-environment-variables)。Claude Code 接受但忽略 `deny` 項目上的 `mask` 欄位。

#### 環境變數的遮罩欄位

`mask` 項目接受這些可選欄位。沒有 `extract` 或 `decode`，Claude Code 將整個值替換為一個哨兵。`extract` 和 `decode` 無法在同一項目上結合。

| 欄位                                                                                                                                           | 類型                                                                                                                                                   | 它做什麼                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `extract`                                                                                                                                      | 字串，至少有一個捕獲群組的正規表達式                                                                                                                   | 僅遮罩每個符合的群組 1 捕獲的文字，例如 `DATABASE_URL` 連接字串內的密碼，所以值的其餘部分保持可解析。需要 v2.1.224 或更新版本                                                                                                                                                                                                   |
| `onExtractNoMatch`                                                                                                                             | `"warn"`、`"deny"` 或 `"error"`；預設 `"warn"`。在帶有 `decode` 的項目上，僅接受 `"warn"`                                                              | 當 `extract` 不符合任何內容時會發生什麼。`warn` 不遮罩地傳遞變數，`deny` 在沙箱內取消設定它，`error` 停止沙箱設定直到您修復設定。需要 v2.1.224 或更新版本                                                                                                                                                                       |
| `decode`                                                                                                                                       | 字串 `"jwt"`                                                                                                                                           | 驗證整個值是 JWT 並將其替換為結構上有效的假令牌，所以沙箱內解碼令牌的程式碼保持工作；代理在出口上替換整個真實令牌。不驗證的值不遮罩地傳遞並帶有警告。需要 v2.1.224 或更新版本                                                                                                                                                   |
| `maskClaims`                                                                                                                                   | 字串陣列，至少一個聲明名稱；需要 `decode`                                                                                                              | 僅遮罩解碼 JWT 內的命名頂級有效負載聲明並在修改的有效負載周圍重建令牌，所以其他聲明保持可讀。當沒有命名聲明符合時，變數不遮罩地傳遞並帶有警告。需要 v2.1.224 或更新版本                                                                                                                                                         |
| `injectHosts`                                                                                                                                  | 字串陣列，每個是 [`sandbox.network.allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 也允許的主機 | 縮小沙箱代理替換真實值的主機。未設定時，代理在 `sandbox.network.allowedDomains` 中的每個主機上的請求上替換它。將 IPv6 目的地寫為裸壓縮位址，例如 `"::1"`，而不是括號形式；請參閱 [IPv6 destinations in `injectHosts`](https://code.claude.com/docs/zh-TW/sandboxing#ipv6-destinations-in-injecthosts)。需要 v2.1.199 或更新版本 |
| 這僅遮罩 `DATABASE_URL` 內的密碼，如果模式不符合任何內容則取消設定變數，並遮罩 `SERVICE_JWT` 中的 JWT，同時保持除 `api_key` 外的每個聲明可讀： |                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                 |
| settings.json                                                                                                                                  |                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                 |

```
{
  "sandbox": {
    "credentials": {
      "envVars": [
        {
          "name": "DATABASE_URL",
          "mode": "mask",
          "extract": "://[^:]+:([^@]+)@",
          "onExtractNoMatch": "deny"
        },
        {
          "name": "SERVICE_JWT",
          "mode": "mask",
          "decode": "jwt",
          "maskClaims": ["api_key"]
        }
      ]
    }
  }
}

```

### `sandbox.credentials.allowPlaintextInject`

允許 `mask` 替換在純 HTTP 請求以及 TLS 終止 HTTPS 上。在純 HTTP 上，上游身份未驗證，認證以明文形式傳輸，所以在受信任的測試網路外保持關閉。需要 Claude Code v2.1.199 或更新版本。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 允許 `mask` 替換在純 HTTP 請求以及 TLS 終止 HTTPS 上
  - `false`: Claude Code 允許 `mask` 替換僅在 TLS 終止 HTTPS 上
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "credentials": {
      "allowPlaintextInject": true
    }
  }
}

```

需要 Claude Code v2.1.199 或更新版本。

### `sandbox.credentials.awsPairs`

分組遮罩環境變數，形成一個 AWS 認證用於 [SigV4 re-signing](https://code.claude.com/docs/zh-TW/sandboxing#re-sign-aws-requests)，當您的認證存在於具有非標準名稱的變數中時。Claude Code 在您遮罩其整個值時自動連結常規 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY` 和 `AWS_SESSION_TOKEN` 三元組，所以您僅在其他名稱時需要此鍵。需要 Claude Code v2.1.224 或更新版本。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 物件陣列，每個包含 `accessKeyIdVar`、`secretAccessKeyVar` 和可選的 `sessionTokenVar`，命名 `sandbox.credentials.envVars` 項目
- **Default** : 未設定，所以僅常規三元組被配對

這將三個自訂命名變數連結到一個 AWS 認證用於重新簽署： settings.json

```
{
  "sandbox": {
    "credentials": {
      "awsPairs": [
        {
          "accessKeyIdVar": "MY_KEY_ID",
          "secretAccessKeyVar": "MY_SECRET_KEY",
          "sessionTokenVar": "MY_SESSION_TOKEN"
        }
      ]
    }
  }
}

```

每個命名變數必須是 [`sandbox.credentials.envVars`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-envvars) 中的整個值 `mask` 項目，沒有 `extract` 或 `decode`，並且只能填充所有配對中的一個槽位。

### `sandbox.credentials.sigv4`

選擇沙箱代理對 AWS 請求形式執行的操作，它 [can’t re-sign](https://code.claude.com/docs/zh-TW/sandboxing#re-sign-aws-requests)：`streaming` 用於 aws-chunked 串流上傳，`presigned` 用於預簽署 URL，`sigv4a` 用於 SigV4A 非對稱簽名。這僅適用於使用遮罩配對的佔位符存取金鑰 ID 簽署的請求。需要 Claude Code v2.1.224 或更新版本。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 物件，包含 `streaming`、`presigned` 和 `sigv4a`，每個為以下之一：
  - `"deny"`: 代理失敗請求
  - `"passthrough"`: 代理使用遮罩佔位符簽署的請求轉發，所以工具接收 AWS 自己的拒絕
- **Default** : 未設定，所以每個形式為 `"deny"`

這轉發串流上傳而不是在代理失敗它們： settings.json

```
{
  "sandbox": {
    "credentials": {
      "sigv4": {
        "streaming": "passthrough"
      }
    }
  }
}

```

使用 `deny`，代理失敗請求。使用 `passthrough`，代理使用從遮罩佔位符計算的簽名轉發請求，所以 AWS 拒絕它，呼叫工具接收 AWS 自己的回應而不是代理錯誤。

### `sandbox.network`

控制沙箱化命令可以到達的主機、連接埠和通訊端。沙箱透過代理路由出站流量，強制執行這些清單；請參閱 [Network isolation](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation) 以了解代理如何決定以及何時提示。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。`strictAllowlist`、`allowManagedDomainsOnly` 和 `tlsTerminate` 從較少的來源讀取，如其項目所述。
- **Type** : 物件，包含下面的子鍵
- **Default** : 未設定，所以沒有網域被預先允許，沙箱為每個新主機提示

這預先允許 GitHub 和 npm，阻止 `uploads.github.com`，並讓命令綁定到 localhost： settings.json

```
{
  "sandbox": {
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"],
      "deniedDomains": ["uploads.github.com"],
      "allowLocalBinding": true
    }
  }
}

```

Claude Code 合併設定範圍中的陣列子鍵並去重，所以專案可以將網域新增到您的使用者清單。`WebFetch(domain:...)` 允許和拒絕 [permission rules](https://code.claude.com/docs/zh-TW/sandboxing#permission-rules) 饋送相同的允許和拒絕清單。

### `sandbox.network.allowUnixSockets`

列出 macOS 上沙箱化命令可以連接的 Unix 通訊端路徑。Claude Code 在 Linux 和 WSL2 上忽略此清單，其中 seccomp 篩選器無法檢查通訊端路徑；改為在那裡使用 [`allowAllUnixSockets`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowallunixsockets)。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串陣列，每個通訊端路徑
- **Default** : 未設定，所以 macOS 沙箱阻止每個 Unix 通訊端

settings.json

```
{
  "sandbox": {
    "network": {
      "allowUnixSockets": ["~/.ssh/agent-socket"]
    }
  }
}

```

通訊端路徑可以授予廣泛存取：例如允許 `/var/run/docker.sock` 讓沙箱化命令控制 Docker 守護程序。請參閱 [Security limitations](https://code.claude.com/docs/zh-TW/sandboxing#security-limitations)。

### `sandbox.network.allowAllUnixSockets`

讓沙箱化命令連接到每個 Unix 通訊端。在 Linux 和 WSL2 上，沙箱的 [seccomp filter](https://code.claude.com/docs/zh-TW/sandboxing#set-up-linux-and-wsl2) 阻止 `socket(AF_UNIX, ...)` 呼叫，所以這是在那裡允許 Unix 通訊端的唯一方式。當篩選器遺失時，`/sandbox` 在其 Dependencies 標籤上報告，沙箱不阻止 Unix 通訊端呼叫。請參閱 [Set up Linux and WSL2](https://code.claude.com/docs/zh-TW/sandboxing#set-up-linux-and-wsl2) 以了解篩選器來自何處。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: 沙箱化命令可以連接到每個 Unix 通訊端
  - `false`: 沙箱阻止 Unix 通訊端連接：在 macOS 上除了 `allowUnixSockets` 中的路徑，在 Linux 和 WSL2 上透過 seccomp 篩選器（當它存在時）
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "network": {
      "allowAllUnixSockets": true
    }
  }
}

```

在 WSL2 上，`true` 也重新開啟啟動 Windows 二進位檔案（例如 `cmd.exe` 和 `powershell.exe`）的 interop 通訊端。

### `sandbox.network.allowLocalBinding`

讓 macOS 上的沙箱化命令綁定到 localhost 連接埠，例如啟動開發伺服器。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: macOS 上的沙箱化命令可以綁定到 localhost 連接埠
  - `false`: macOS 上的沙箱化命令無法綁定到 localhost 連接埠
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "network": {
      "allowLocalBinding": true
    }
  }
}

```

### `sandbox.network.allowMachLookup`

列出 macOS 沙箱可能查詢的其他 XPC 和 Mach 服務名稱。透過 XPC 通訊的工具（例如 iOS 模擬器或 Playwright）需要在此列出其服務。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串陣列，每個服務名稱；單個尾部 `*` 符合前綴，`"*"` 單獨符合每個服務
- **Default** : 未設定

這允許 `com.apple.coresimulator.` 前綴下的每個服務： settings.json

```
{
  "sandbox": {
    "network": {
      "allowMachLookup": ["com.apple.coresimulator.*"]
    }
  }
}

```

### `sandbox.network.allowedDomains`

預先允許沙箱化命令的出站流量網域，所以沙箱不為它們提示。萬用字元（例如 `*.example.com`）符合子網域，可選的 `:port` 尾碼將項目限制為一個連接埠；沒有連接埠的項目符合每個連接埠。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。僅當設定 [`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly) 時的受管設定。
- **Type** : 字串陣列，每個網域、萬用字元模式或 IP 字面，帶有可選的 `:port` 尾碼
- **Default** : 未設定，所以沙箱在命令首次到達新主機時提示

這預先允許 GitHub 在每個連接埠、每個 npm 子網域和一個 API 主機僅在連接埠 443 上： settings.json

```
{
  "sandbox": {
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org", "api.example.com:443"]
    }
  }
}

```

將 IPv6 字面寫為括號，帶有可選連接埠：`"[::1]"` 允許每個連接埠，`"[::1]:443"` 一個連接埠。括號形式需要 Claude Code v2.1.229 或更新版本。請參閱 [IPv6 addresses in domain lists](https://code.claude.com/docs/zh-TW/sandboxing#ipv6-addresses-in-domain-lists)。

### `sandbox.network.deniedDomains`

阻止沙箱化命令的出站流量網域，使用與 [`allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 相同的萬用字元、連接埠和 IPv6 語法。被拒絕的網域即使 `allowedDomains` 項目也符合它仍保持被阻止。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串陣列，每個網域、萬用字元模式或 IP 字面，帶有可選的 `:port` 尾碼
- **Default** : 未設定

settings.json

```
{
  "sandbox": {
    "network": {
      "deniedDomains": ["sensitive.cloud.example.com"]
    }
  }
}

```

Claude Code 合併工作階段載入的每個設定來源中的此清單，即使設定 `allowManagedDomainsOnly` 時，所以開發人員可以始終收緊拒絕清單。對於 IPv6 字面，請參閱 [IPv6 addresses in domain lists](https://code.claude.com/docs/zh-TW/sandboxing#ipv6-addresses-in-domain-lists)。 以標記完全合格網域名稱的尾部點寫入的項目，例如 `example.com.`，阻止與 `example.com` 相同的連接。

### `sandbox.network.strictAllowlist`

拒絕沙箱化命令存取允許清單外的主機，而不是提示批准。允許清單是 [`allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 加上來自 `WebFetch(domain:...)` 允許規則的網域，或僅當設定 [`allowManagedDomainsOnly`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-allowmanageddomainsonly) 時的受管設定項目。需要 Claude Code v2.1.219 或更新版本。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。儲存庫無法開啟或關閉它。
- **Type** : 布林值
  - `true`: Claude Code 拒絕沙箱化命令存取允許清單外的主機
  - `false`: 除非另一個受信任的設定檔案設定 `true`，Claude Code 根據權限模式而不是直接拒絕決定允許清單外的主機：它在自動模式中檢查主機對命令的 [per-command allowed domains](https://code.claude.com/docs/zh-TW/sandboxing#per-command-allowed-domains-in-auto-mode)，在 `dontAsk` 模式中拒絕，在 `bypassPermissions` 模式中允許，在計畫模式中當旁路可用時允許，否則詢問您
- **Default** : `false`

settings.json

```
{
  "sandbox": {
    "network": {
      "strictAllowlist": true
    }
  }
}

```

Claude Code 僅對沙箱化命令強制執行此；進程內工具（例如 `WebFetch`）仍然遵循其 [permission rules](https://code.claude.com/docs/zh-TW/sandboxing#permission-rules)。當任何接受的來源將其設定為 `true` 時，它保持開啟。請參閱 [Network isolation](https://code.claude.com/docs/zh-TW/sandboxing#network-isolation)。需要 Claude Code v2.1.219 或更新版本。

### `sandbox.network.allowManagedDomainsOnly`

將網路允許清單鎖定到受管設定定義的內容。Claude Code 然後僅接受來自受管設定的 `allowedDomains` 和 `WebFetch(domain:...)` 允許規則，忽略來自使用者、專案、本機和 `--settings` 設定的網域，並自動阻止非允許的網域而不是提示。

- **Scope** : [`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 僅接受來自受管設定的 `allowedDomains` 和 `WebFetch(domain:...)` 允許規則，並自動阻止非允許的網域而不是提示
  - `false`: 來自使用者、專案、本機和 `--settings` 設定的網域合併到允許清單
- **Default** : `false`

這將允許清單鎖定到 GitHub 和 npm，並忽略開發人員新增的任何網域： managed-settings.json

```
{
  "sandbox": {
    "network": {
      "allowManagedDomainsOnly": true,
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}

```

被拒絕的網域仍然合併自工作階段載入的每個來源。請參閱 [Keep developers from widening the policy](https://code.claude.com/docs/zh-TW/sandboxing#keep-developers-from-widening-the-policy)。

### `sandbox.network.httpProxyPort`

將沙箱指向您自己的 HTTP 代理而不是 Claude Code 執行的。組織執行此操作以檢查 HTTPS 流量、應用其自己的篩選規則或記錄每個請求。未設定時，Claude Code 為 HTTP 流量啟動其自己的代理。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 數字，本機 TCP 連接埠
- **Default** : 未設定，所以 Claude Code 執行其自己的代理

settings.json

```
{
  "sandbox": {
    "network": {
      "httpProxyPort": 8080
    }
  }
}

```

如果您的代理也應該攜帶 SOCKS 流量，也設定 [`socksProxyPort`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-socksproxyport)；僅設定其中一個時，Claude Code 仍然為另一個協議執行其自己的代理。請參閱 [Custom proxy configuration](https://code.claude.com/docs/zh-TW/sandboxing#custom-proxy-configuration)。

### `sandbox.network.socksProxyPort`

將沙箱指向您自己的 SOCKS5 代理而不是 Claude Code 執行的。未設定時，Claude Code 為 SOCKS 流量啟動其自己的代理。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 數字，本機 TCP 連接埠
- **Default** : 未設定，所以 Claude Code 執行其自己的代理

settings.json

```
{
  "sandbox": {
    "network": {
      "socksProxyPort": 8081
    }
  }
}

```

請參閱 [Custom proxy configuration](https://code.claude.com/docs/zh-TW/sandboxing#custom-proxy-configuration)。

### `sandbox.network.tlsTerminate`

使沙箱代理終止 TLS，以便它可以讀取 HTTPS 請求的內容。這是實驗性的，`mask` [credential substitution](https://code.claude.com/docs/zh-TW/sandboxing#mask-credentials) 需要它。設定 `{}` 為工作階段生成臨時憑證授權單位，或設定 `caCertPath` 和 `caKeyPath` 以使用您自己的。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。儲存庫無法開啟它或提供憑證授權單位。
- **Type** : 物件，包含可選的 `caCertPath` 和 `caKeyPath` 字串，每個檔案路徑
- **Default** : 未設定，所以代理不終止或檢查 TLS

settings.json

```
{
  "sandbox": {
    "network": {
      "tlsTerminate": {}
    }
  }
}

```

當多個接受的來源設定它時，Claude Code 使用來自優先順序最高的來源的值：受管設定、然後 `--settings` 旗標、然後使用者設定。需要 Claude Code v2.1.199 或更新版本。

## 記憶和上下文

控制 Claude Code 載入上下文的內容、如何壓縮以及在何處保存記憶和計畫。請參閱[管理上下文](https://code.claude.com/docs/zh-TW/context-window)和[記憶](https://code.claude.com/docs/zh-TW/memory)。

### `autoCompactEnabled`

當上下文接近限制時，讓 Claude Code [自動壓縮對話](https://code.claude.com/docs/zh-TW/context-window#when-your-context-fills-up)。在 `/config` 中顯示為**自動壓縮** ，在那裡切換它會將此鍵寫入您的使用者設定。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：當上下文接近限制時，Claude Code 自動壓縮對話
  - `false`：Claude Code 不自動壓縮
- **預設** ：`true`
- **每個工作階段的覆蓋** ：[`DISABLE_AUTO_COMPACT`](https://code.claude.com/docs/zh-TW/env-vars) 關閉一個工作階段的自動壓縮；無論哪一個關閉它，另一個都無法將其重新開啟

settings.json

```
{
  "autoCompactEnabled": false
}

```

手動 `/compact` 命令在自動壓縮關閉時繼續工作。

### `autoCompactWindow`

設定在 Claude Code [自動壓縮](https://code.claude.com/docs/zh-TW/context-window#when-your-context-fills-up)之前上下文視窗有多滿。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：權杖數量，從 `100000` 到 `1000000`。Claude Code 將值上限設定為您的模型的上下文視窗；[模型概覽](https://platform.claude.com/docs/en/about-claude/models/overview)列出每個模型的視窗
- **預設** ：未設定，因此 Claude Code 選擇為您的模型調整的視窗
- **每個工作階段的覆蓋** ：[`--autocompact`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 在一個工作階段內優先於此鍵，[`CLAUDE_CODE_AUTO_COMPACT_WINDOW`](https://code.claude.com/docs/zh-TW/env-vars) 優先於兩者

settings.json

```
{
  "autoCompactWindow": 500000
}

```

使用 [`/autocompact`](https://code.claude.com/docs/zh-TW/commands#all-commands) 命令設定它，該命令將此鍵寫入您的使用者設定。[設定自動壓縮視窗](https://code.claude.com/docs/zh-TW/model-config#set-the-auto-compact-window)涵蓋命令、旗標、變數和設定如何相互作用。

### `autoMemoryDirectory`

將[自動記憶](https://code.claude.com/docs/zh-TW/memory#storage-location)儲存在您選擇的目錄中，而不是每個專案的預設值。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，絕對路徑或 `~/` 前綴的目錄路徑
- **預設** ：未設定，因此 Claude Code 使用 `~/.claude/projects/<project>/memory/`

settings.json

```
{
  "autoMemoryDirectory": "~/my-memory-dir"
}

```

從專案或本機設定，Claude Code 在與 [hooks 相同的工作區信任規則](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder)下遵守此鍵，因為複製的儲存庫可以提供這些檔案。

### `autoMemoryEnabled`

開啟或關閉[自動記憶](https://code.claude.com/docs/zh-TW/memory#enable-or-disable-auto-memory)。當為 `false` 時，Claude 不會從自動記憶目錄讀取或寫入。您也可以在工作階段期間使用 `/memory` 切換它，這會將此鍵寫入您的使用者設定。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：與未設定相同；自動記憶保持開啟，除非優先於此鍵的內容為工作階段關閉它，例如 `--bare`、安全模式或 `CLAUDE_CODE_DISABLE_AUTO_MEMORY`
  - `false`：Claude 不會從自動記憶目錄讀取或寫入
- **預設** ：`true`
- **每個工作階段的覆蓋** ：[`CLAUDE_CODE_DISABLE_AUTO_MEMORY`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段內優先於此鍵，無論哪個方向

settings.json

```
{
  "autoMemoryEnabled": false
}

```

### `bashOutputMaxChars`

設定成功的 Bash 或 PowerShell 命令的[輸出 Claude 內聯接收](https://code.claude.com/docs/zh-TW/tools-reference#output-limits)的字元數。當輸出超過限制時，Claude Code 將其保存到檔案，Claude 接收簡短預覽加上檔案的路徑。當命令輸出（例如詳細的建置或完整的測試套件日誌）經常超過預設值，且您希望 Claude 在不打開檔案的情況下讀取它時，請提高限制。需要 Claude Code v2.1.261 或更高版本。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字元數，正整數。Claude Code 將值限制在 `4000` 到 `128000` 的範圍內
- **預設** ：未設定，因此 Claude 內聯接收最多 30,000 個字元

settings.json

```
{
  "bashOutputMaxChars": 100000
}

```

當您設定此鍵時，Claude Code 忽略 [`BASH_MAX_OUTPUT_LENGTH`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數。

### `claudeMd`

注入 CLAUDE.md 風格的指示作為組織管理的記憶，無需部署單獨的檔案。Claude Code 將文字作為受管記憶條目載入，位於使用者和專案 CLAUDE.md 檔案之前。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，CLAUDE.md 檔案的文字；按照您編寫檔案的方式編寫，包括 Markdown，換行符為 `\n`
- **預設** ：未設定

此範例將兩個規則部署為簡短的 Markdown 清單： managed-settings.json

```
{
  "claudeMd": "# Engineering rules\n\n- Always run make lint before committing.\n- Never push directly to main."
}

```

請參閱[部署組織範圍的 CLAUDE.md](https://code.claude.com/docs/zh-TW/memory#deploy-organization-wide-claude-md)。

### `claudeMdExcludes`

在 Claude Code 載入[記憶](https://code.claude.com/docs/zh-TW/memory#exclude-specific-claude-md-files)時跳過特定的 `CLAUDE.md` 檔案。在大型單一儲存庫中，使用它跳過與您的工作無關的其他團隊的 CLAUDE.md 檔案；[排除無關的 CLAUDE.md 檔案](https://code.claude.com/docs/zh-TW/large-codebases#exclude-irrelevant-claude-md-files)在大型程式碼庫指南中介紹了該情況。模式與絕對檔案路徑匹配。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串陣列，每個都是 glob 模式或絕對路徑
- **預設** ：未設定，因此 Claude Code 載入它找到的每個 CLAUDE.md

settings.json

```
{
  "claudeMdExcludes": ["**/vendor/**/CLAUDE.md"]
}

```

排除僅適用於使用者、專案和本機記憶檔案；受管原則 CLAUDE.md 檔案無法被排除。

### `env`

為每個工作階段和 Claude Code 從中啟動的子程序設定環境變數。[環境變數參考](https://code.claude.com/docs/zh-TW/env-vars)中的任何變數都可以放在這裡，這是如何將其應用於每個工作階段或將其推出到您的團隊的方式。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：將變數名稱對應到字串值的物件
- **預設** ：未設定

此範例關閉自動壓縮並通過代理路由 API 請求： settings.json

```
{
  "env": {
    "DISABLE_AUTO_COMPACT": "1",
    "ANTHROPIC_BASE_URL": "https://proxy.example.com"
  }
}

```

#### `env` 值如何與您的 shell 相互作用

- 此處的值會覆蓋在您的 shell 中匯出的相同變數，當多個設定檔設定一個變數時，[最高優先級](https://code.claude.com/docs/zh-TW/settings#settings-precedence)的值適用。
- 要取消 shell 匯出，請將變數設定為 `""`。Claude Code 將空值視為未設定以進行提供者選擇，子程序繼承空值。
- `NO_COLOR` 和 `FORCE_COLOR` 在此設定只到達子程序。要更改 Claude Code 自己的介面顏色，請在啟動 `claude` 之前在您的 shell 中設定它們。
- 此處的值是設定檔中的純文字，到達 Claude Code 啟動的每個子程序。對於輪換的 OTLP 持有人令牌，使用 [`otelHeadersHelper`](https://code.claude.com/docs/zh-TW/settings-reference#otelheadershelper)；對於 API 認證，使用 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper)。

#### Claude Code 何時應用 `env` 值

- 從使用者設定、`--settings` 和受管設定：在啟動時，以及在執行中的工作階段中當保存的變更改變合併的 `env` 時。
- 從專案和本機設定：在您信任工作區後，或在 `-p` 模式下啟動時（不顯示信任對話），以及當保存的變更改變合併的 `env` 時。
- Claude Code 分類為安全的變數，例如模型選擇、逾時和限制、功能切換和遙測設定：在啟動時從每個設定檔，除了[專案和本機設定無法設定的變數](https://code.claude.com/docs/zh-TW/settings-reference#variables-claude-code-ignores-in-env)。
- 在您在 v2.1.246 或更高版本上使用 `/cd` [移動工作階段](https://code.claude.com/docs/zh-TW/permissions#move-the-session-to-another-directory)後：新目錄的專案和本機 `env` 值，加上前一個目錄的。

#### Claude Code 在 `env` 中忽略的變數

- 專案和本機設定無法設定已簽出的儲存庫不應控制的變數；改為在您的 shell、使用者設定或受管設定中設定這些變數。Claude Code 刪除每個變數並記錄您可以使用 `claude --debug` 看到的警告。它們包括：
  - 選擇 Claude Code 儲存或寫入其自己檔案的位置的變數：`CLAUDE_CONFIG_DIR`、`CLAUDE_CODE_TMPDIR` 和作業系統目錄變數，例如 `HOME`、`TMPDIR`、`TMP`、`TEMP` 和 `XDG_*` 系列。
  - 匯出工作階段內容的變數：[`OTEL_LOG_RAW_API_BODIES`](https://code.claude.com/docs/zh-TW/env-vars#variables) 和詳細的測試版追蹤對 `ENABLE_BETA_TRACING_DETAILED` 和 `BETA_TRACING_ENDPOINT`。
  - 改變 Claude Code 如何啟動或同步的變數，例如 `CLAUDE_CODE_PROCESS_WRAPPER`、`CLAUDE_CODE_SYNC_SKILLS`、`CLAUDE_CODE_SYNC_PLUGINS`、`CLAUDE_CODE_PLUGIN_CACHE_DIR` 和 `CLAUDE_CODE_PLUGIN_SEED_DIR`。 在 v2.1.251 之前，專案和本機設定可以設定此清單命名的每個變數，除了 `HOME`、`XDG_CONFIG_HOME` 和改變 Claude Code 如何啟動或同步的變數。
- Claude Code 的託管環境擁有的身份變數，例如 `CLAUDE_CODE_REMOTE` 和 `CLAUDE_CODE_ACCOUNT_UUID`，從每個檔案中被忽略。
- [`CLAUDE_CODE_MESSAGING_SOCKET` 和 `CLAUDE_CODE_MESSAGING_TOKEN`](https://code.claude.com/docs/zh-TW/env-vars#variables)，Claude Code 自己匯出的，從每個檔案中被忽略。忽略 socket 變數需要 Claude Code v2.1.224 或更高版本，忽略令牌需要 v2.1.228 或更高版本。
- [`CLAUDE_CODE_PROJECT_DIR_NAME`](https://code.claude.com/docs/zh-TW/sessions#name-the-project-directory-yourself)，Claude Code 僅從啟動環境讀取，從每個檔案中被忽略；需要 v2.1.234 或更高版本。
- [`CLAUDE_CODE_RESTRICTED`](https://code.claude.com/docs/zh-TW/env-vars#variables)，Claude Code 僅從啟動環境讀取，從每個檔案中被忽略。

### `fileCheckpointingEnabled`

讓 Claude Code 在每次編輯前快照檔案，以便 [`/rewind`](https://code.claude.com/docs/zh-TW/checkpointing) 可以還原它們。在 `/config` 中顯示為**倒帶程式碼（檢查點）** ，在那裡切換它會將此鍵寫入您的使用者設定。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 在每次編輯前快照檔案，以便 `/rewind` 可以還原它們
  - `false`：Claude Code 不快照檔案，因此 `/rewind` 無法還原它們
- **預設** ：`true`
- **每個工作階段的覆蓋** ：[`CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING`](https://code.claude.com/docs/zh-TW/env-vars) 關閉一個工作階段的檢查點；無論哪一個關閉它，另一個都無法將其重新開啟

settings.json

```
{
  "fileCheckpointingEnabled": false
}

```

在 `-p` 執行或 Agent SDK 工作階段中，Claude Code 忽略此鍵。SDK 使用其 `enableFileCheckpointing` 選項開啟檢查點，裸 `-p` 執行需要 `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true`。請參閱 [Agent SDK 中的檔案檢查點](https://code.claude.com/docs/zh-TW/agent-sdk/file-checkpointing)。

### `plansDirectory`

選擇 Claude Code 在 [plan mode](https://code.claude.com/docs/zh-TW/permission-modes#analyze-before-you-edit-with-plan-mode) 中寫入的計畫檔案的儲存位置。Claude Code 相對於專案根目錄解析路徑，當路徑解析在其外部時保持預設值。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，相對於專案根目錄的路徑
- **預設** ：未設定，因此 Claude Code 使用 `~/.claude/plans`

settings.json

```
{
  "plansDirectory": "./plans"
}

```

### `skillListingBudgetFraction`

每個回合，Claude 看到[您的技能清單](https://code.claude.com/docs/zh-TW/skills#skill-descriptions-are-cut-short)及其描述，Claude Code 將該清單上限設定為上下文視窗的一部分。當清單超過上限時，Claude Code 保留每個技能的名稱，但刪除最少使用技能的描述，因此 Claude 仍然可以呼叫這些技能，但不太可能自己選擇一個。提高此鍵以保持更多描述可見，代價是每個回合更多上下文。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：數字，大於 `0` 且最多 `1` 的分數
- **預設** ：`0.01`，保留上下文視窗的 1%

settings.json

```
{
  "skillListingBudgetFraction": 0.02
}

```

要查看清單使用多少上下文以及哪些技能貢獻最多，請執行 `/doctor`。

### `skillListingMaxDescChars`

每個回合，Claude 看到[您的技能清單](https://code.claude.com/docs/zh-TW/skills#skill-descriptions-are-cut-short)，顯示每個技能的 `description` 和 `when_to_use` 文字。此鍵限制 Claude Code 每個技能顯示多少字元的該文字；較長的文字在上限處被切割。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字元數，正整數
- **預設** ：`1536`

settings.json

```
{
  "skillListingMaxDescChars": 2048
}

```

提高它以保持長描述完整，代價是每個回合更多上下文；降低它以在 [`skillListingBudgetFraction`](https://code.claude.com/docs/zh-TW/settings-reference#skilllistingbudgetfraction) 下適應更多技能。

### `taskOutputMaxChars`

設定[背景工作](https://code.claude.com/docs/zh-TW/tools-reference#background-commands)的輸出字元數，當 Claude 使用 `TaskOutput` 工具讀取工作時，Claude 內聯接收。當完成的工作的輸出更長時，Claude 接收最近的字元。當您的背景工作經常產生超過預設值的輸出時，請提高限制。需要 Claude Code v2.1.261 或更高版本。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字元數，正整數。Claude Code 將值限制在 `4000` 到 `128000` 的範圍內
- **預設** ：未設定，因此 Claude 內聯接收最多 32,000 個字元

settings.json

```
{
  "taskOutputMaxChars": 100000
}

```

當您設定此鍵時，Claude Code 忽略 [`TASK_MAX_OUTPUT_LENGTH`](https://code.claude.com/docs/zh-TW/env-vars) 環境變數。

## 介面和終端

改變 Claude Code 在終端中的外觀和行為：主題、編輯器模式、狀態列、旋轉器、工作階段內的通知和無障礙功能。請參閱[終端設定](https://code.claude.com/docs/zh-TW/terminal-config)。

### `askUserQuestionTimeout`

讓未回答的 [`AskUserQuestion`](https://code.claude.com/docs/zh-TW/tools-reference) 對話框在閒置一段時間後自動繼續，提交您已選擇的任何選項。當您離開時設定此項，讓 Claude 在沒有您的情況下繼續。使用預設值時，問題會等待您回答。需要 Claude Code v2.1.200 或更新版本。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為 `"60s"`、`"5m"`、`"10m"` 或 `"never"` 之一
- **預設** ：`"never"`
- **每個工作階段的覆蓋** ：[`CLAUDE_AFK_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段中優先於此金鑰

settings.json

```
{
  "askUserQuestionTimeout": "5m"
}

```

在 `/config` 中顯示為**問題自動繼續逾時** ，會將此金鑰寫入使用者設定；當受管設定或 `--settings` 旗標設定此金鑰時，Claude Code 會隱藏該列。需要 Claude Code v2.1.200 或更新版本。

### `autoContinueAtUsageLimit`

在 claude.ai 使用限制停止您的工作階段後，在開啟的工作階段中等待，並在重設後自動繼續工作。請參閱[關閉自動繼續](https://code.claude.com/docs/zh-TW/interactive-mode#turn-automatic-continue-off)。需要 Claude Code v2.1.234 或更新版本。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。僅從使用者設定、`--settings` 和受管設定讀取。當這些都未設定此金鑰時，設定此金鑰的專案或本機設定檔會關閉此功能，而不是被忽略。
- **類型** ：布林值
  - `true`：在 claude.ai 使用限制停止您的工作階段後，Claude Code 在開啟的工作階段中等待，並在重設後自動繼續工作
  - `false`：Claude Code 不會自行啟動等待。您仍然可以從使用限制選項功能表[自行啟動等待](https://code.claude.com/docs/zh-TW/interactive-mode#start-a-wait-yourself)
- **預設** ：`true`

settings.json

```
{
  "autoContinueAtUsageLimit": false
}

```

在 `/config` 中顯示為**在使用限制時自動繼續** ，會將此金鑰寫入使用者設定；當受管設定或 `--settings` 旗標設定此金鑰時，Claude Code 會隱藏該列。

### `autoScrollEnabled`

在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen)中跟隨新輸出到對話的底部。關閉它以在 Claude 繼續工作時保持您捲動的位置；權限提示仍會捲動到檢視中。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：對話跟隨新輸出到底部
  - `false`：您在 Claude 繼續工作時保持捲動的位置；權限提示仍會出現在文字記錄下方
- **預設** ：`true`

settings.json

```
{
  "autoScrollEnabled": false
}

```

在全螢幕渲染開啟時，在 `/config` 中顯示為**自動捲動** ，會將此金鑰寫入使用者設定。

### `axScreenReader`

渲染螢幕閱讀器友善的輸出：沒有裝飾性邊框或動畫的平面文字。螢幕閱讀器模式使用經典渲染器，因此在其啟用時 `tui` 設定無效；附加的[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view)仍會全螢幕渲染。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 使用經典渲染器渲染沒有裝飾性邊框或動畫的平面文字
  - `false`：Claude Code 正常渲染
- **預設** ：未設定，因此螢幕閱讀器模式已關閉
- **每個工作階段的覆蓋** ：[`--ax-screen-reader`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 優先於 [`CLAUDE_AX_SCREEN_READER`](https://code.claude.com/docs/zh-TW/env-vars)，兩者都優先於此金鑰在一個工作階段中

settings.json

```
{
  "axScreenReader": true
}

```

### `bashEditDiffEnabled`

選擇 Claude Code 是否記錄 Bash 命令在 Git 存放庫中變更的檔案。當它記錄它們時，您會在命令後在終端中看到它們的差異，您的 [PostToolUse Bash hooks](https://code.claude.com/docs/zh-TW/hooks#bash) 會接收變更檔案清單。 將金鑰設定為 `true` 以在每個權限模式中記錄它們。需要 Claude Code v2.1.269 或更新版本。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。`true` 僅從您的使用者設定、使用 `--settings` 傳遞的 JSON 或[受管設定](https://code.claude.com/docs/zh-TW/managed-settings)計算，因此存放庫的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的 `true` 無法開啟記錄。存放庫檔案中的 `false` 仍會關閉它，除非[更高優先順序](https://code.claude.com/docs/zh-TW/settings#settings-precedence)的檔案設定 `true`。
- **類型** ：布林值
- **預設** ：未設定，因此 Claude Code 在自動模式和 `bypassPermissions` 模式中記錄變更，當它指示 Claude 透過 Bash 編輯檔案時
- **每個工作階段的覆蓋** ：[`CLAUDE_CODE_BASH_EDIT_DIFF`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段中優先於此金鑰

settings.json

```
{
  "bashEditDiffEnabled": true
}

```

### `companyAnnouncements`

在啟動時向使用者顯示您組織的公告。當您列出多個時，Claude Code 為每個工作階段隨機選擇一個；在某人的首次啟動時，它會顯示第一個項目。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串陣列
- **預設** ：未設定，因此不顯示公告

settings.json

```
{
  "companyAnnouncements": [
    "Welcome to Acme Corp! Review our code guidelines at docs.example.com"
  ]
}

```

### `defaultShell`

選擇 Bash 或 PowerShell 是否執行您在輸入框中使用 [`!` 前綴](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)輸入的 shell 命令，以及 Claude Code 直接執行並新增到工作階段的命令。 `"powershell"` 僅在 [PowerShell 工具](https://code.claude.com/docs/zh-TW/tools-reference#powershell-tool)開啟時有效。該工具在沒有 Git Bash 的 Windows 上預設開啟，在有 Git Bash 的 Windows 上用於 claude.ai 和 Console 帳戶。在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 工作階段中，以及在 macOS、Linux 和 WSL 上，設定 `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` 以開啟工具。將該變數設定為 `0` 以關閉工具。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為以下之一：
  - `"bash"`：Claude Code 在 Bash 中執行您的 `!` 命令
  - `"powershell"`：Claude Code 在 PowerShell 中執行您的 `!` 命令
- **預設** ：`"bash"`，或在 Bash 不可用時在 Windows 上為 `"powershell"`

settings.json

```
{
  "defaultShell": "powershell"
}

```

如果您命名的 shell 不可用，Claude Code 會使用另一個：當 PowerShell 工具關閉時 `"powershell"` 會回退到 Bash，當 Bash 未安裝時 `"bash"` 會回退到 PowerShell。

### `dialogExpiry`

為 Claude Code [轉發給遠端用戶端](https://code.claude.com/docs/zh-TW/remote-control#limitations)的對話框（例如遠端控制或 SDK 主機）以及[保留的跨工作階段訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)的核准對話框設定截止期限。在 Claude Code v2.1.236 或更新版本上，相同的截止期限限制了可能沒有人在終端的工作階段中的中途 [Fable 使用額度同意提示](https://code.claude.com/docs/zh-TW/model-config#fable-and-usage-credits)。當在截止期限前未收到答案時，Claude Code 會取消對話框並使用其無操作預設值繼續。需要 Claude Code v2.1.224 或更新版本。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為 `"60s"`、`"5m"`、`"10m"` 或 `"never"` 之一，後者會停用截止期限
- **預設** ：`"5m"`
- **每個工作階段的覆蓋** ：[`CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段中優先於此金鑰

settings.json

```
{
  "dialogExpiry": "10m"
}

```

權限提示和 [`AskUserQuestion`](https://code.claude.com/docs/zh-TW/tools-reference#askuserquestion-tool-behavior) 問題使用自己的流程，不受此截止期限管制。在 `/config` 中顯示為**對話框過期** ，會將此金鑰寫入使用者設定；該列需要 Claude Code v2.1.232 或更新版本，當受管設定或 `--settings` 旗標設定此金鑰時，Claude Code 會隱藏它。

### `editorMode`

選擇輸入提示的快捷鍵模式。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為以下之一：
  - `"normal"`：提示輸入中的標準快捷鍵
  - `"vim"`：vim 風格編輯，具有 NORMAL、INSERT 和 VISUAL 模式
- **預設** ：`"normal"`

settings.json

```
{
  "editorMode": "vim"
}

```

在 `/config` 中顯示為**編輯器模式** ，會將此金鑰寫入使用者設定。

### `emojiCompletionEnabled`

當您在提示輸入中輸入 `:` 加上簡碼時顯示表情符號建議，並將完成的簡碼（例如 `:heart:`）替換為其表情符號。將其設定為 `false` 以關閉兩者。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 在 `:` 後顯示表情符號建議，並將完成的簡碼替換為其表情符號
  - `false`：Claude Code 既不建議表情符號也不替換簡碼
- **預設** ：`true`

settings.json

```
{
  "emojiCompletionEnabled": false
}

```

請參閱[表情符號簡碼](https://code.claude.com/docs/zh-TW/interactive-mode#emoji-shortcodes)。需要 Claude Code v2.1.217 或更新版本。

### `fileSuggestion`

執行您自己的命令來提供 `@` 檔案路徑自動完成，而不是使用內建的檔案建議。內建建議使用快速檔案系統遍歷；大型單倉庫可能會使用專案特定的索引（例如預先建立的檔案索引）更好。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在[狀態列和檔案建議閘道](https://code.claude.com/docs/zh-TW/settings-reference#status-line-and-file-suggestion-gates)下，Claude Code 會關閉命令或僅執行受管值，並在沒有警告的情況下跳過您的命令。
- **類型** ：具有 `type`（始終為 `"command"`）和 `command`（要執行的 shell 命令）的物件
- **預設** ：未設定，因此 Claude Code 使用內建檔案建議

settings.json

```
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  }
}

```

儲存後，在提示中輸入 `@` 後跟部分路徑：建議來自您命令的輸出。

#### 命令輸入和輸出

Claude Code 使用與 [hooks](https://code.claude.com/docs/zh-TW/hooks) 相同的環境變數執行命令，包括 `CLAUDE_PROJECT_DIR`，並在五秒後停止等待。命令在 stdin 上接收 JSON，其中 `query` 欄位保存您到目前為止輸入的內容：

```
{"query": "src/comp"}

```

將換行符分隔的檔案路徑列印到 stdout。Claude Code 最多顯示 15 個：

```
src/components/Button.tsx
src/components/Modal.tsx
src/components/Form.tsx

```

以下指令碼讀取查詢並將其交給存放庫檔案索引：

```
#!/bin/bash
query=$(cat | jq -r '.query')
# Replace your-repo-file-index with your own file search command
your-repo-file-index --query "$query" | head -20

```

### `footerLinksRegexes`

當正規表達式符合轉換輸出時，在輸入框下方的頁尾中渲染額外的可點擊徽章：工具結果，包括檔案內容和擷取的頁面，以及 Claude 自己的回應。使用它將專案 CLI 列印的 ID（例如審查工具和問題追蹤器）轉換為工作階段連結。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：物件陣列，每個物件的 `type` 設定為 `"regex"`、`pattern` 正規表達式、`url` 範本和可選的 `label`；`url` 和 `label` 中的 `{name}` 預留位置從 `pattern` 中的具名擷取群組填充
- **預設** ：未設定，因此不渲染徽章

此範例符合問題金鑰（例如 `PROJ-1234`）並從擷取的金鑰建立每個連結： settings.json

```
{
  "footerLinksRegexes": [
    {
      "type": "regex",
      "pattern": "\\b(?<key>PROJ-\\d+)\\b",
      "url": "https://issues.example.com/browse/{key}",
      "label": "{key}"
    }
  ]
}

```

配置此項後，當 `PROJ-1234` 出現在工具結果或 Claude 的回覆中時，頁尾中會出現 `PROJ-1234` 徽章，連結到 `https://issues.example.com/browse/PROJ-1234`。

#### 徽章限制

每個項目的 URL、標籤和徽章計數受以下限制：

| 限制                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 行為                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| URL 來源                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 擷取的值是 URL 編碼的，構造的 URL 必須共享範本的字面來源。擷取可以填充路徑段或查詢值，但無法改變連結指向的位置                                                                 |
| URL 長度                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 長於 2048 個字元的構造 URL 會被丟棄                                                                                                                                            |
| URL 配置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 必須是 `https`、`http` 或公認的編輯器或工作區深層連結配置：`vscode`、`vscode-insiders`、`cursor`、`windsurf`、`zed`、`jetbrains`、`idea`、`slack`、`linear`、`notion`、`figma` |
| 標籤                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 預設為符合的文字，並截斷為 28 個顯示欄                                                                                                                                         |
| 徽章計數                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 最多渲染 5 個徽章。最舊的被較新的符合項取代，`/clear` 會移除它們                                                                                                               |
| 當轉換完成時，Claude Code 在主執行緒上將每個項目的 `pattern` 正規表達式與轉換輸出進行比對，因此緩慢的正規表達式會阻止 UI 直到完成。嵌套量詞（例如 `(a+)+$`）對某些輸入可能需要指數級長時間並凍結工作階段，因此請保持每個 `pattern` 線性並避免嵌套 `+` 或 `*`。 頁尾徽章與[自訂狀態列](https://code.claude.com/docs/zh-TW/statusline)並排渲染（如果已配置）；兩者都不會取代另一個。使用狀態列來執行從工作階段資料計算自己內容的指令碼驅動列，使用頁尾徽章將對話中的 ID 轉換為連結，而無需指令碼。 |                                                                                                                                                                                |

### `keybindingFlavor`

自 v2.1.261 起已棄用，無效。提示的單字編輯快捷鍵始終[遵循 readline 慣例](https://code.claude.com/docs/zh-TW/interactive-mode#make-ctrl-w-delete-back-to-whitespace)，如 Bash 中所示。Claude Code 仍接受 `keybindingFlavor`，因此設定它的設定檔保持有效。 在 v2.1.238 到 v2.1.260 中，將其設定為 `"readline"` 使 `Ctrl+W` 刪除回到前一個空白字元，而不是僅刪除前一個單字。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，`"classic"` 或 `"readline"`
- **預設** ：未設定

### `prefersReducedMotion`

減少或關閉介面動畫，例如旋轉器、微光和閃爍效果。在 `/config` 中顯示為**減少動作** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 減少或關閉介面動畫，例如旋轉器、微光和閃爍效果
  - `false`：與未設定相同；Claude Code 顯示其動畫
- **預設** ：`false`

settings.json

```
{
  "prefersReducedMotion": true
}

```

### `promptSuggestionEnabled`

顯示或隱藏[提示建議](https://code.claude.com/docs/zh-TW/interactive-mode#prompt-suggestions)，即在您的提示輸入中出現的灰色預測。將其設定為 `false`，或在 `/config` 中關閉**提示建議** ，以隱藏它們。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：您在提示輸入中看到提示建議
  - `false`：Claude Code 隱藏提示建議
- **預設** ：`true`
- **每個工作階段的覆蓋** ：[`CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段中優先於此金鑰

settings.json

```
{
  "promptSuggestionEnabled": false
}

```

提示建議需要啟用遙測的 claude.ai 或 Console 帳戶。在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上，或在遙測關閉時（例如由 [`DISABLE_TELEMETRY`](https://code.claude.com/docs/zh-TW/env-vars)），此金鑰無效，只有 `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=1` 會開啟它們。

### `respectGitignore`

控制 `@` 檔案選擇器是否排除符合 `.gitignore` 模式的檔案。在 `/config` 中顯示為**在檔案選擇器中尊重 .gitignore** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當沒有設定檔設定它時，Claude Code 會回退到 `~/.claude.json` 中的 `respectGitignore`，這是 `/config` 切換寫入的。
- **類型** ：布林值
  - `true`：`@` 檔案選擇器排除符合 `.gitignore` 模式的檔案
  - `false`：`@` 檔案選擇器包括符合 `.gitignore` 模式的檔案
- **預設** ：`true`

settings.json

```
{
  "respectGitignore": false
}

```

### `respondToBashCommands`

選擇在您在輸入框中使用 [`!` 前綴](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)執行 shell 命令後 Claude 是否回應。預設情況下，Claude Code 將命令的輸出新增到對話中，Claude 會回覆。將此金鑰設定為 `false` 以將輸出新增到上下文而不回覆，以便您可以執行多個命令並一起詢問它們。需要 Claude Code v2.1.186 或更新版本。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 將命令的輸出新增到對話中，Claude 會回覆
  - `false`：Claude Code 將輸出新增到上下文而不回覆
- **預設** ：`true`

settings.json

```
{
  "respondToBashCommands": false
}

```

請參閱[使用 `!` 前綴的 Shell 模式](https://code.claude.com/docs/zh-TW/interactive-mode#shell-mode-with-prefix)。需要 Claude Code v2.1.186 或更新版本。

### `showClearContextOnPlanAccept`

當 Claude 在[計畫模式](https://code.claude.com/docs/zh-TW/permission-modes#review-and-approve-a-plan)中完成計畫時，它會顯示核准功能表。計畫可能會使用大量上下文，因此此金鑰會在該功能表中新增第一個選項**是的，清除上下文並…** ，該選項核准計畫、清除對話上下文並開始僅從計畫實施。標籤的其餘部分命名工作階段繼續的權限模式，並顯示計畫使用了多少上下文。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：計畫核准功能表獲得第一個選項**是的，清除上下文並…** ，該選項核准計畫並清除對話上下文
  - `false`：計畫核准功能表不顯示清除上下文選項
- **預設** ：`false`

settings.json

```
{
  "showClearContextOnPlanAccept": true
}

```

### `showTurnDuration`

顯示或隱藏每個回應後的轉換持續時間訊息，例如「Cooked for 1m 6s · done 6:05 PM」。「done」後的時鐘顯示轉換何時完成；[`timeFormat`](https://code.claude.com/docs/zh-TW/settings-reference#timeformat) 和 [`timeZone`](https://code.claude.com/docs/zh-TW/settings-reference#timezone) 控制其格式和時區。在 `/config` 中顯示為**顯示轉換持續時間** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當沒有設定檔設定它時，來自舊版本的 `~/.claude.json` 中的值適用。
- **類型** ：布林值
  - `true`：您在每個回應後看到轉換持續時間訊息
  - `false`：Claude Code 隱藏轉換持續時間訊息
- **預設** ：`true`

settings.json

```
{
  "showTurnDuration": false
}

```

### `spellcheck`

在您輸入時，使用您安裝的拼寫檢查器在提示輸入中為拼寫錯誤的單字加下劃線。Claude Code 僅檢查輸入框中的文字。[在您輸入時檢查拼寫](https://code.claude.com/docs/zh-TW/interactive-mode#check-spelling-as-you-type)涵蓋安裝 aspell、hunspell 或 ispell 以及檢查器涵蓋的內容。需要 Claude Code v2.1.235 或更新版本。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。設定它的最高層級的區塊整體適用。
- **類型** ：具有 `enabled`（布林值）、`checker`（`"aspell"`、`"hunspell"`、`"ispell"` 或 `"auto"`）、`language`（字串，傳遞給檢查器作為其字典名稱）和 `color`（字串，終端顏色名稱、`#rrggbb`、`rgb(r,g,b)`、`ansi256(n)` 或 `ansi:<name>`）的物件
- **預設** ：未設定，因此拼寫檢查已關閉；`checker` 預設為 `"auto"`，`PATH` 上找到的前三個之一；`language` 預設為檢查器自己的字典；`color` 預設為主題的錯誤顏色

settings.json

```
{
  "spellcheck": { "enabled": true, "language": "en_GB" }
}

```

### `spinnerTipsEnabled`

當 Claude 工作時，旋轉器列會輪換顯示有關 Claude Code 功能的簡短提示，例如「使用計畫模式為複雜請求做準備，然後再進行變更。按 Shift+Tab 兩次以啟用。」將此金鑰設定為 `false` 以隱藏它們。在 `/config` 中顯示為**顯示提示** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：您在 Claude 工作時在旋轉器中看到提示
  - `false`：Claude Code 隱藏旋轉器提示
- **預設** ：`true`

settings.json

```
{
  "spinnerTipsEnabled": false
}

```

### `spinnerTipsOverride`

將您自己的提示新增到 Claude Code 在 Claude 工作時顯示的[旋轉器提示](https://code.claude.com/docs/zh-TW/settings-reference#spinnertipsenabled)，或用您的提示取代內建提示。Claude Code 將您的提示放在與內建提示相同的輪換中：它選擇未顯示時間最長的提示，跳過仍在冷卻期中的提示，並按優先順序打破平局。 如果您將 [`spinnerTipsEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#spinnertipsenabled) 設定為 `false`，Claude Code 會隱藏所有提示，包括您的提示。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 從使用者設定、`--settings` 旗標和受管設定中尊重提示物件、`tipsFile`、`label` 和 `excludeDefault`；從專案和本機設定中，它僅讀取純字串提示。
- **類型** ：具有 `tips`、`tipsFile`、`label` 和 `excludeDefault` 欄位的物件，每個都是可選的
- **預設** ：未設定，因此 Claude Code 僅顯示內建提示

提示物件、`tipsFile`、`label` 和「範圍」行的規則（專案和本機設定僅貢獻純字串）需要 Claude Code v2.1.247 或更新版本。在較早的版本上，專案或本機檔案的 `excludeDefault` 也適用。 每個 `tips` 項目是純字串或具有以下欄位的物件：

| 欄位                                                                                                                                                                                                                                                                                                              | 必需 | 說明                                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                                                                                                                                                                                                                                                                                              | 是   | 最多 64 個字母、數字、`.`、`_` 或 `-`。Claude Code 在其上鍵入提示的顯示歷史記錄，因此提示的冷卻期在重新排序列表後仍然存在。在兩個具有相同 id 的項目中，Claude Code 使用第一個 |
| `text`                                                                                                                                                                                                                                                                                                            | 是   | 提示，最多 500 個字元的一行。Claude Code 去除 ANSI 逸出和控制字元，並摺疊空白                                                                                                 |
| `cooldownSessions`                                                                                                                                                                                                                                                                                                | 否   | Claude Code 在再次顯示提示之前等待的工作階段，`0` 到 `1000`，預設 `0`                                                                                                         |
| `priority`                                                                                                                                                                                                                                                                                                        | 否   | 在未顯示時間相同的提示之間的順序，較高的優先，`-10` 到 `10`，預設 `0`                                                                                                         |
| Claude Code 將純字串讀取為具有這些預設值和位置型 id 的提示，因此當您重新排序列表時其顯示歷史記錄會重設。給提示一個 `id` 以在編輯時保持其歷史記錄。 Claude Code 在 `tips` 和 `tipsFile` 中最多讀取 200 個提示，並使用偵錯警告丟棄無效項目，而不是拒絕設定檔。 使用其餘欄位來命名提示檔案、設定前綴和隱藏內建提示： |      |                                                                                                                                                                               |

- `tipsFile`：本機 JSON 檔案的絕對或 `~/` 路徑，保存相同項目的陣列，或具有 `tips` 陣列的物件，最多 256 KB。Claude Code 每個程序讀取一次檔案，因此它在下次啟動時載入您的編輯。您無法透過[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)設定它；在那裡部署內聯 `tips`，或在磁碟上的 `managed-settings.json` 中部署路徑。
- `label`：Claude Code 在來自使用者、`--settings` 和受管設定的提示之前顯示的前綴，最多 40 個字元。預設值是 `Tip`，與內建提示相同的前綴，來自專案和本機設定的提示始終使用它。
- `excludeDefault`：將其設定為 `true` 以隱藏內建提示並僅顯示您的提示。當 Claude Code 無法載入任何您的提示時，例如因為 `tipsFile` 不存在或每個項目都無效，它會保持內建輪換而不是空旋轉器。

當多個設定檔設定金鑰時，Claude Code 顯示來自所有設定檔的提示，並從設定每個的受管設定、`--settings` 旗標和使用者設定中最高優先順序的提示中取得 `tipsFile`、`label` 和 `excludeDefault`。 此範例在您的使用者設定中，在 `Acme tip` 前綴下將純字串提示和物件提示新增到輪換： settings.json

```
{
  "spinnerTipsOverride": {
    "label": "Acme tip",
    "tips": [
      "Run /review before opening a PR",
      {
        "id": "gateway-errors",
        "text": "Seeing 5xx errors? Check the gateway status page first",
        "cooldownSessions": 5,
        "priority": 2
      }
    ]
  }
}

```

範例中的每個欄位都改變了 Claude Code 顯示提示的方式：

- `label`：Claude Code 將兩個提示顯示為 `Acme tip: ...` 而不是 `Tip: ...`。
- 純字串：Claude Code 給它預設值，因此它可以在下一個工作階段中再次出現。
- `id`：Claude Code 在 `gateway-errors` 上鍵入第二個提示的顯示歷史記錄，因此其冷卻期在您新增或重新排序提示後仍然適用。
- `cooldownSessions`：在 Claude Code 顯示 `gateway-errors` 提示後，它在五個工作階段後才再次顯示該提示。
- `priority`：當 `gateway-errors` 提示和另一個提示未顯示相同時間長度時，例如當兩者都尚未顯示時，Claude Code 首先顯示 `gateway-errors`。純字串具有預設優先順序 `0`。

當 Claude 工作時，Claude Code 在旋轉器中使用您的前綴顯示您的提示，例如 `Acme tip: Run /review before opening a PR`。

### `spinnerVerbs`

當轉換進行中時，旋轉器顯示輪換動詞，例如「Accomplishing」、「Architecting」或「Baking」。使用此金鑰將您自己的動詞新增到該輪換或用您的動詞取代內建清單。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：具有 `verbs` 字串陣列和 `mode` 的物件，為以下之一：
  - `"append"`：Claude Code 將您的動詞新增到內建集合
  - `"replace"`：Claude Code 僅顯示您的動詞
- **預設** ：未設定，因此 Claude Code 使用內建動詞

此範例將兩個動詞新增到內建集合： settings.json

```
{
  "spinnerVerbs": {
    "mode": "append",
    "verbs": ["Pondering", "Crafting"]
  }
}

```

在 `"replace"` 模式中使用空 `verbs` 陣列，Claude Code 保持內建動詞。

### `statusLine`

執行您自己的命令來在提示下方渲染[狀態列](https://code.claude.com/docs/zh-TW/statusline)，其中包含模型、成本或 git 分支等上下文。可選欄位調整間距、新增定期重新執行，並在您的指令碼自己渲染 `vim.mode` 時隱藏內建 vim 模式指示器。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly) 開啟時，或 [`disableAllHooks`](https://code.claude.com/docs/zh-TW/settings-reference#disableallhooks) 在受管設定外設定時，僅受管設定值執行。
- **類型** ：具有 `type` 設定為 `"command"` 和 `command` 字串的物件，加上可選的 `padding` 作為字元數、`refreshInterval` 作為秒數（最少 `1`）和 `hideVimModeIndicator` 作為布林值
- **預設** ：未設定，因此沒有狀態列

此範例列印模型名稱和上下文使用情況，並新增兩個字元的水平間距： settings.json

```
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'",
    "padding": 2
  }
}

```

範例需要安裝 [`jq`](https://jqlang.org/) 並在 shell 中執行。如需 PowerShell 和 Git Bash 等效項，請參閱[Windows 設定](https://code.claude.com/docs/zh-TW/statusline#windows-configuration)；如需完整設定，請參閱[手動設定狀態列](https://code.claude.com/docs/zh-TW/statusline#manually-configure-a-status-line)。

### `subagentStatusLine`

當 Claude 執行[子代理](https://code.claude.com/docs/zh-TW/sub-agents)時，Claude Code 在提示下方的工作顯示中列出它們，每個子代理一列顯示 `name · description · token count`。此金鑰讓您執行自己的命令來重寫這些列，例如將每個子代理的上下文使用情況顯示為百分比。在每次重新整理時，Claude Code 在 stdin 上以一個 JSON 物件的形式傳送可見列，其中 `tasks` 陣列包含每個子代理的 `id`、`name`、`status`、`model`、`tokenCount` 等，並將您寫回的每個 `id` 的列替換為 `{"id", "content"}` 行。您未寫回的列保持預設渲染。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly) 開啟時，或 [`disableAllHooks`](https://code.claude.com/docs/zh-TW/settings-reference#disableallhooks) 在受管設定外設定時，僅受管設定值執行。
- **類型** ：具有 `type` 設定為 `"command"` 和 `command` 字串的物件
- **預設** ：未設定，因此 Claude Code 渲染預設列

settings.json

```
{
  "subagentStatusLine": {
    "type": "command",
    "command": "jq -c '.tasks[] | {id, content: \"\\(.name): \\(.tokenCount) tokens\"}'"
  }
}

```

請參閱[子代理狀態列](https://code.claude.com/docs/zh-TW/statusline#subagent-status-lines)。

### `syntaxHighlightingDisabled`

Claude Code 使用其內建高亮器在終端中顯示的差異、程式碼區塊和檔案預覽中按語言為程式碼著色；不涉及外掛程式或語言伺服器。將此金鑰設定為 `true` 以改為將它們顯示為純文字，例如如果顏色與您的終端主題衝突或減慢螢幕閱讀器。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 在差異、程式碼區塊和檔案預覽中關閉語法高亮
  - `false`：Claude Code 高亮語法
- **預設** ：`false`

settings.json

```
{
  "syntaxHighlightingDisabled": true
}

```

### `terminalProgressBarEnabled`

某些終端可以在執行中的程式的標籤或工作列中顯示進度指示器。當 Claude 工作時，Claude Code 向終端報告進行中狀態，因此您可以從另一個標籤或視窗看到工作階段是否仍在忙碌。指示器在轉換結束後保持可見，同時[背景子代理](https://code.claude.com/docs/zh-TW/sub-agents#run-subagents-in-foreground-or-background)或[動態工作流程](https://code.claude.com/docs/zh-TW/workflows)仍在執行，並在工作階段閒置後清除。 Claude Code 僅在支援指示器的終端中報告它：ConEmu、Ghostty 1.2.0 或更新版本，以及 iTerm2 3.6.6 或更新版本。將此金鑰設定為 `false` 以停止 Claude Code 報告它。在 `/config` 中顯示為**終端進度列** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當沒有設定檔設定它時，來自舊版本的 `~/.claude.json` 中的值適用。
- **類型** ：布林值
  - `true`：您在支援它的終端中看到終端進度列
  - `false`：Claude Code 隱藏終端進度列
- **預設** ：`true`

settings.json

```
{
  "terminalProgressBarEnabled": false
}

```

### `terminalTitleFromRename`

Claude Code 設定您的終端標籤標題。預設情況下，它使用從對話生成的標題，一旦您使用 `/rename` 或 `--name` 給工作階段[命名](https://code.claude.com/docs/zh-TW/sessions#name-your-sessions)，標籤會改為顯示該名稱。將此金鑰設定為 `false` 以在您命名工作階段後保持生成的標題在標籤上。名稱本身仍然適用，因此 `/resume <name>` 和工作階段選擇器會找到它。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：終端標籤標題顯示您設定的工作階段名稱
  - `false`：標籤保持 Claude Code 從您的對話生成的標題
- **預設** ：`true`

settings.json

```
{
  "terminalTitleFromRename": false
}

```

若要完全停止 Claude Code 更新終端標題，請改為將 [`CLAUDE_CODE_DISABLE_TERMINAL_TITLE`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1`。

### `theme`

選擇介面的顏色主題。在 `/config` 中顯示為**主題** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當沒有設定檔設定它時，來自舊版本的 `~/.claude.json` 中的值適用。
- **類型** ：字串，為以下之一：
  - `"auto"`：符合您終端的淺色或深色背景
  - `"dark"`：深色主題
  - `"light"`：淺色主題
  - `"dark-daltonized"`：具有色盲友善顏色的深色主題
  - `"light-daltonized"`：具有色盲友善顏色的淺色主題
  - `"dark-ansi"`：僅使用您終端的 ANSI 顏色調色板的深色主題
  - `"light-ansi"`：僅使用您終端的 ANSI 顏色調色板的淺色主題
  - `"custom:<slug>"` 或 `"custom:<plugin-name>:<slug>"`：來自 `~/.claude/themes/` 或外掛程式的自訂主題
- **預設** ：`"dark"`

settings.json

```
{
  "theme": "light-daltonized"
}

```

請參閱[建立自訂主題](https://code.claude.com/docs/zh-TW/terminal-config#create-a-custom-theme)。

### `timeFormat`

選擇 Claude Code 在介面中顯示的時間的寫法方式，例如每個轉換持續時間訊息末尾的 `done 6:05 PM` 和[文字記錄檢視器](https://code.claude.com/docs/zh-TW/interactive-mode#transcript-viewer)中的時間戳記。若要選擇預設值，執行 `/config` 並設定**時間格式** 。需要 Claude Code v2.1.257 或更新版本。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為以下之一：
  - `"auto"`：與未設定相同；每個時間保持其內建格式，在轉換持續時間訊息上遵循您的地區設定
  - `"12-hour"`：12 小時制
  - `"24-hour"`：24 小時制
  - `"24-hour-utc"`：UTC 中的 24 小時制，分鐘後為 `Z`，例如 `18:05Z`；Claude Code 為此預設值忽略 [`timeZone`](https://code.claude.com/docs/zh-TW/settings-reference#timezone)
  - strftime 模式，例如 `"%H:%M"`：Claude Code 使用模式寫入每個時間。任何包含 `%` 的值都是模式，預設值外的任何其他值都計為 `"auto"`
- **預設** ：`"auto"`

settings.json

```
{
  "timeFormat": "24-hour"
}

```

`/config` 僅提供預設值，因此若要使用 strftime 模式，請將金鑰新增到設定檔。此範例將每個時間顯示為兩位數 24 小時制： settings.json

```
{
  "timeFormat": "%H:%M"
}

```

轉換持續時間訊息和文字記錄檢視器隨後顯示時間，例如 `18:05`。在文字記錄檢視器中，模式是整個時間戳記，因此當您想要日期時新增日期指令。此範例將日期放在時鐘前面： settings.json

```
{
  "timeFormat": "%Y-%m-%d %H:%M"
}

```

相同的表面隨後顯示時間，例如 `2026-09-01 18:05`。

### `timeZone`

在時區中顯示介面中的時間，而不是您的系統時區。將其設定為 [IANA 時區名稱](https://www.iana.org/time-zones)，例如 `"UTC"` 或 `"Europe/Dublin"`。[`timeFormat`](https://code.claude.com/docs/zh-TW/settings-reference#timeformat) 控制的時間隨後在此時區中顯示。如果 `timeFormat` 是 `"24-hour-utc"`，時間保持在 UTC 中，Claude Code 忽略此金鑰。`/config` 沒有此金鑰的列，因此在設定檔中設定它。需要 Claude Code v2.1.257 或更新版本。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，IANA 時區名稱。當 Claude Code 不識別名稱時，它使用您的系統時區
- **預設** ：未設定，因此時間在您的系統時區中顯示

settings.json

```
{
  "timeZone": "Europe/Dublin"
}

```

### `tui`

選擇終端 UI 渲染器。使用 `"fullscreen"` 以獲得無閃爍的[替代螢幕渲染器](https://code.claude.com/docs/zh-TW/fullscreen)，具有虛擬化捲回，或使用 `"default"` 以獲得經典主螢幕渲染器。執行 `/tui fullscreen` 或 `/tui default` 會為您寫入此金鑰。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為以下之一：
  - `"default"`：經典主螢幕渲染器
  - `"fullscreen"`：無閃爍的替代螢幕渲染器，具有虛擬化捲回
- **預設** ：未設定，因此 Claude Code [為您選擇渲染器](https://code.claude.com/docs/zh-TW/fullscreen#fullscreen-by-default)
- **每個工作階段的覆蓋** ：[`CLAUDE_CODE_NO_FLICKER`](https://code.claude.com/docs/zh-TW/env-vars) 和 [`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段中優先於此金鑰：`CLAUDE_CODE_NO_FLICKER=1` 開啟全螢幕，`CLAUDE_CODE_NO_FLICKER=0` 或 `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` 關閉它；當兩者都設定時，Claude Code 關閉它

settings.json

```
{
  "tui": "fullscreen"
}

```

在 tmux `-CC` 下或透過 SSH 連線到 Windows，Claude Code 保持經典渲染器，除非您設定 `CLAUDE_CODE_NO_FLICKER=1`。從[代理檢視](https://code.claude.com/docs/zh-TW/agent-view)開啟的背景工作階段始終使用全螢幕渲染器，無論此設定如何。

### `verbose`

預設情況下，文字記錄將每個工具呼叫摺疊為簡短摘要，例如 Claude 執行的命令和其輸出的行數，當您想要詳細資訊時，您按 `Ctrl+O` 將整個文字記錄切換到展開檢視。將此金鑰設定為 `true` 以在發生時內聯顯示每個工具呼叫的完整輸入和輸出，這在您偵錯 hook、MCP 伺服器或長 shell 命令時很有用。在 `/config` 中顯示為**詳細輸出** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。當沒有設定檔設定它時，來自舊版本的 `~/.claude.json` 中的值適用。
- **類型** ：布林值
  - `true`：您看到完整工具輸出
  - `false`：您看到工具輸出的截斷摘要
- **預設** ：`false`
- **每個工作階段的覆蓋** ：[`--verbose`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 在一個工作階段中優先於此金鑰

settings.json

```
{
  "verbose": true
}

```

[`viewMode`](https://code.claude.com/docs/zh-TW/settings-reference#viewmode) 值或粘性 `/focus` 選擇在每個工作階段中覆蓋此金鑰。

### `viewMode`

設定 Claude Code 啟動的文字記錄檢視：`"default"`、`"verbose"` 或 `"focus"`。設定時，它會覆蓋粘性 `/focus` 選擇和 [`verbose`](https://code.claude.com/docs/zh-TW/settings-reference#verbose) 設定。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，為以下之一：
  - `"default"`：具有截斷工具輸出的正常文字記錄
  - `"verbose"`：具有完整工具輸出的文字記錄
  - `"focus"`：僅您的最後提示、工具呼叫的單行摘要，具有編輯差異統計資訊，以及最終回應。焦點檢視需要[全螢幕渲染器](https://code.claude.com/docs/zh-TW/settings-reference#tui)
- **預設** ：未設定，因此 `verbose` 設定和您最後的 `/focus` 選擇適用
- **每個工作階段的覆蓋** ：[`--verbose`](https://code.claude.com/docs/zh-TW/cli-reference#cli-flags) 在一個工作階段中優先於此金鑰

settings.json

```
{
  "viewMode": "focus"
}

```

### `vimInsertModeRemaps`

在[vim 編輯器模式](https://code.claude.com/docs/zh-TW/interactive-mode#vim-editor-mode)中將兩鍵 INSERT 模式序列對應到 Escape。每個金鑰恰好是按順序輸入的兩個可列印字元，`"<Esc>"` 是唯一支援的目標；Claude Code 忽略其他項目。需要 Claude Code v2.1.208 或更新版本。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。存放庫無法重新對應您的按鍵。
- **類型** ：將兩字元序列對應到 `"<Esc>"` 的物件
- **預設** ：未設定

settings.json

```
{
  "vimInsertModeRemaps": {
    "jj": "<Esc>"
  }
}

```

除非 `editorMode` 是 `"vim"`，否則無效。請參閱[重新對應 INSERT 模式快捷鍵序列](https://code.claude.com/docs/zh-TW/interactive-mode#remap-insert-mode-key-sequences)。需要 Claude Code v2.1.208 或更新版本。

### `voice`

開啟[語音聽寫](https://code.claude.com/docs/zh-TW/voice-dictation)並選擇聽寫金鑰的行為方式。當您執行 `/voice` 時，Claude Code 會為您寫入此物件。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：具有 `enabled` 作為布林值、`autoSubmit` 作為僅在保持模式中適用的布林值，以及 `mode` 的物件，為以下之一：
  - `"hold"`：您在說話時按住聽寫金鑰，釋放它以停止
  - `"tap"`：您點擊金鑰一次以開始錄製，再次以傳送
- **預設** ：未設定，因此聽寫已關閉；當 `enabled` 是 `true` 且 `mode` 未設定時，Claude Code 使用 `"hold"`

此範例開啟聽寫並使金鑰點擊一次以開始錄製，再次以傳送： settings.json

```
{
  "voice": {
    "enabled": true,
    "mode": "tap"
  }
}

```

`autoSubmit` 在保持模式中釋放金鑰時傳送提示。語音聽寫需要 claude.ai 帳戶。

### `voiceEnabled`

自 v2.1.92 起已棄用，當 [`voice`](https://code.claude.com/docs/zh-TW/settings-reference#voice) 物件取代它時。Claude Code 仍讀取它，因此較舊的設定檔保持工作，但新配置應設定 `voice.enabled`。 使用在 `voice` 物件之前的單一布林值形式開啟語音聽寫。當兩者都設定時，`voice.enabled` 適用。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：當您使用 claude.ai 帳戶登入且您組織的政策允許語音時，語音聽寫開啟，除非設定了 `voice.enabled`
  - `false`：語音聽寫已關閉，除非設定了 `voice.enabled`
- **預設** ：未設定

settings.json

```
{
  "voiceEnabled": true
}

```

### `wheelScrollAccelerationEnabled`

在[全螢幕渲染](https://code.claude.com/docs/zh-TW/fullscreen#mouse-wheel-scrolling)中快速捲動期間加速滑鼠滾輪捲動速度。將其設定為 `false` 以獲得每個滾輪凹口的恆定捲動速率。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 在快速捲動期間加速滑鼠滾輪捲動速度
  - `false`：Claude Code 以每個滾輪凹口的恆定速率捲動
- **預設** ：`true`

settings.json

```
{
  "wheelScrollAccelerationEnabled": false
}

```

## Git 和歸屬

控制 Claude Code 新增至提交和拉取請求的歸屬，以及它如何與 git 搭配運作。

### `attribution`

自訂 Claude Code 新增至 git 提交和拉取請求的歸屬。提交預設會取得 [git trailer](https://git-scm.com/docs/git-interpret-trailers)，例如 `Co-Authored-By`；拉取請求描述會取得純文字。使用下方的子鍵分別設定每個部分。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 包含 `commit` 和 `pr` 字串以及 `sessionUrl` 布林值的物件
- **Default** : 未設定，因此 Claude Code 使用每個子鍵下方顯示的標準歸屬

此範例會取代提交歸屬、移除拉取請求歸屬，並捨棄工作階段連結： settings.json

```
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>",
    "pr": "",
    "sessionUrl": false
  }
}

```

若要隱藏所有歸屬，請將 [`commit`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-commit) 和 [`pr`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-pr) 設定為空字串，並將 [`sessionUrl`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-sessionurl) 設定為 `false`。一旦您設定 `commit` 或 `pr`，Claude Code 就會忽略已棄用的 `includeCoAuthoredBy` 設定，並對您未設定的兩者使用其預設文字。

### `includeCoAuthoredBy`

自 v2.0.62 起已棄用，當時 [`attribution`](https://code.claude.com/docs/zh-TW/settings-reference#attribution) 取代了它。Claude Code 仍會讀取它，但新設定應該設定 `attribution`。 改用 [`attribution`](https://code.claude.com/docs/zh-TW/settings-reference#attribution)，它會取代此鍵並讓您分別變更或隱藏提交 trailer、拉取請求文字和工作階段連結。Claude Code 仍會接受來自早於 `attribution` 的設定檔中的 `includeCoAuthoredBy: false`，但一旦您設定 `attribution.commit` 或 `attribution.pr`，就會忽略它。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: 與未設定相同；Claude Code 新增提交 trailer 和拉取請求歸屬文字
  - `false`: Claude Code 會省略提交 trailer 和拉取請求歸屬文字，除非 `attribution` 設定 `commit` 或 `pr`，在這種情況下會套用 [`attribution`](https://code.claude.com/docs/zh-TW/settings-reference#attribution) 規則
- **Default** : `true`

settings.json

```
{
  "includeCoAuthoredBy": false
}

```

若要立即隱藏所有歸屬，請將 [`attribution.commit`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-commit) 和 [`attribution.pr`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-pr) 設定為空字串，並將 [`attribution.sessionUrl`](https://code.claude.com/docs/zh-TW/settings-reference#attribution-sessionurl) 設定為 `false`。

### `includeGitInstructions`

在工作階段開始時，Claude Code 會將兩個與 git 相關的部分新增至 Claude 的提示：其內建的提交和拉取請求撰寫方式說明（在 Bash 工具的描述中）以及您存放庫的 git 狀態快照（在系統提示中），意思是目前分支、主要分支、`git status` 輸出和最近的提交。將此鍵設定為 `false` 以將兩者都排除，例如當您使用自己的 git 工作流程技能時。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 包含其內建的提交和拉取請求工作流程說明以及 git 狀態快照。雲端工作階段永遠不會包含快照
  - `false`: Claude Code 將兩者都排除
- **Default** : `true`
- **Per-session overrides** : [`CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS`](https://code.claude.com/docs/zh-TW/env-vars) 對此鍵優先

settings.json

```
{
  "includeGitInstructions": false
}

```

### `prUrlTemplate`

將 Claude Code 呈現的 PR 連結（在頁尾徽章和工具結果摘要中）指向內部程式碼審查工具，而不是 `github.com`。Claude Code 會從 PR URL 替換 `{host}`、`{owner}`、`{repo}`、`{number}` 和 `{url}`。[GitLab 合併請求](https://code.claude.com/docs/zh-TW/interactive-mode#gitlab-merge-requests)連結在兩個表面上都保持其 GitLab URL。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串，使用五個預留位置中任何一個的 URL 範本
- **Default** : 未設定

settings.json

```
{
  "prUrlTemplate": "https://reviews.example.com/{owner}/{repo}/pull/{number}"
}

```

Claude Code 只會將範本套用至它自己呈現的連結；Claude 在訊息中撰寫的 PR 編號（例如 `#123`）會保持 Claude 撰寫的樣子。沒有 `/pull/<number>` 形狀的 URL 會保持不變。

### `attribution.commit`

設定 Claude Code 新增至 git 提交的歸屬文字，包括任何 trailer。將其設定為空字串以隱藏提交歸屬。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串
- **Default** : 未設定，因此 Claude Code 新增 `Co-Authored-By: <name> <noreply@anthropic.com>`。名稱是工作階段的作用中模型，例如 `Claude Sonnet 5`。
  - 當 Claude Code 識別模型為 Claude 模型但無法確認其確切版本時，它會單獨寫入 `Claude`。
  - 當它無法將模型 ID 符合至任何 Claude 模型（例如透過自訂 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/zh-TW/env-vars) 提供的第三方模型）時，它會寫入 `Claude Code`。

此範例會將預設 trailer 取代為自訂行和自訂 `Co-Authored-By` trailer： settings.json

```
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>"
  }
}

```

### `attribution.pr`

設定 Claude Code 新增至拉取請求描述的歸屬文字。將其設定為空字串以隱藏拉取請求歸屬。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 字串
- **Default** : 未設定，因此 Claude Code 新增 `🤖 Generated with [Claude Code](https://claude.com/claude-code)`

settings.json

```
{
  "attribution": {
    "pr": ""
  }
}

```

### `attribution.sessionUrl`

選擇 Claude Code 是否在從[雲端](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)或 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 工作階段提交或開啟拉取請求時附加 claude.ai 工作階段連結。Claude Code 在提交上新增連結作為 `Claude-Session` trailer，並在拉取請求描述中作為連結。將其設定為 `false` 以省略連結。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : 布林值
  - `true`: Claude Code 在從雲端或 Remote Control 工作階段提交或開啟拉取請求時附加 claude.ai 工作階段連結
  - `false`: Claude Code 省略連結
- **Default** : `true`

settings.json

```
{
  "attribution": {
    "sessionUrl": false
  }
}

```

## Hooks 和自動化

註冊 hooks、限制哪些 hooks 執行，以及控制工作流程。如需 hook 事件和承載資料，請參閱 [hooks 參考](https://code.claude.com/docs/zh-TW/hooks)。

### `allowedHttpHookUrls`

限制 [HTTP hooks](https://code.claude.com/docs/zh-TW/hooks#http-hook-fields) 可以目標的 URL。當您定義此金鑰時，Claude Code 只有在 HTTP hook 的 URL 符合其中一個模式時才會執行該 hook，並阻止其餘的而不執行它們；空陣列會阻止每個 HTTP hook。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。陣列在設定檔中合併。
- **類型** ：URL 模式陣列，`*` 作為萬用字元
- **預設** ：未設定，因此允許任何 URL

此範例允許 `https://hooks.example.com/` 下的任何 URL 和任何 `http://localhost` URL： settings.json

```
{
  "allowedHttpHookUrls": ["https://hooks.example.com/*", "http://localhost:*"]
}

```

主機名稱比對不區分大小寫，並將 `hooks.example.com.`（標記完全合格網域名稱的尾部點）視為與 `hooks.example.com` 相同，這是 DNS 的處理方式。允許清單適用於來自每個來源的 hooks，包括受管設定。

### `allowManagedHooksOnly`

限制 hook 執行為您的組織部署的 hooks。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：只有受管 hooks 執行，加上 Agent SDK hooks 和您的受管設定強制啟用的外掛程式中的 hooks。請參閱 [在 `allowManagedHooksOnly` 下執行的內容](https://code.claude.com/docs/zh-TW/settings-reference#what-runs-under-allowmanagedhooksonly)
  - `false`：來自每個設定範圍和外掛程式的 hooks 執行
- **預設** ：未設定，因此來自每個設定範圍和外掛程式的 hooks 執行

managed-settings.json

```
{
  "allowManagedHooksOnly": true
}

```

#### 在 `allowManagedHooksOnly` 下執行的內容

當您將其設定為 `true` 時，Claude Code 會變更哪些 hooks 和類似 hook 的命令載入：

- **受管和 SDK hooks 執行** ：來自受管設定的 hooks 和 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 在程序中註冊的 hooks
- **強制啟用的外掛程式 hooks 執行** ：來自您的受管設定透過 [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 強制啟用的外掛程式的 hooks。Claude Code 在完整的 `plugin@marketplace` ID 上比對，因此來自不同市場的同名外掛程式保持被阻止。這讓您可以透過組織市場分發經過驗證的 hooks，同時阻止其他所有內容
- **其他所有內容被阻止** ：使用者、專案和本機 hooks、來自其他外掛程式的 hooks，以及在代理程式 frontmatter 中宣告的 hooks
- **命令來源的外掛程式被停用** ：Claude Code 也停用具有 [`command` 來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources) 的外掛程式，包括在受管 `enabledPlugins` 中強制啟用的外掛程式，除非您明確將 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources) 設定為 `false`
- **市場`headersHelper` 命令被阻止**：Claude Code 也阻止市場 [`headersHelper` 命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#authenticate-archive-downloads)，除非 [`disableCommandPluginSources`](https://code.claude.com/docs/zh-TW/settings-reference#disablecommandpluginsources) 明確設定為 `false`，受管設定本身宣告的市場除外。需要 Claude Code v2.1.238 或更新版本
- **狀態行和檔案建議縮小到受管設定** ：Claude Code 只從受管設定讀取 [`statusLine`](https://code.claude.com/docs/zh-TW/statusline)、[`fileSuggestion`](https://code.claude.com/docs/zh-TW/settings-reference#filesuggestion) 和 [`subagentStatusLine`](https://code.claude.com/docs/zh-TW/statusline#subagent-status-lines)，遵循 [狀態行和檔案建議閘道](https://code.claude.com/docs/zh-TW/settings-reference#status-line-and-file-suggestion-gates)

當此金鑰設定時，[`/goal`](https://code.claude.com/docs/zh-TW/goal) 命令無法執行，因為它依賴於 hooks。

### `disableAllHooks`

關閉 [hooks](https://code.claude.com/docs/zh-TW/hooks#disable-or-remove-hooks)、任何自訂 [狀態行](https://code.claude.com/docs/zh-TW/statusline) 和任何自訂 [檔案建議](https://code.claude.com/docs/zh-TW/settings-reference#filesuggestion) 命令。使用它可以暫時關閉所有這些，而無需從您的設定中刪除它們。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。只有受管設定可以停用受管 hooks。
- **類型** ：布林值
  - `true`：Claude Code 關閉 hooks、任何自訂狀態行和任何自訂檔案建議命令
  - `false`：hooks、狀態行和檔案建議命令執行
- **預設** ：未設定，因此 hooks 執行

settings.json

```
{
  "disableAllHooks": true
}

```

範圍取決於哪個檔案攜帶該金鑰：

- **在受管設定中** ：Claude Code 停用每個已設定的 hook，包括受管的，並保持執行 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/overview) 在程序中註冊的 hooks
- **在任何其他設定檔中** ：Claude Code 停用使用者、專案、本機和外掛程式 hooks；受管 hooks、Agent SDK hooks 和來自在受管 [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 中強制啟用的外掛程式的 hooks 保持執行

當受管設定設定此金鑰時保持 Agent SDK hooks 執行需要 Claude Code v2.1.242 或更新版本。 當 hooks 被停用時，[`/goal`](https://code.claude.com/docs/zh-TW/goal) 命令無法執行，`/hooks` 功能表顯示通知而不是您的 hooks。

#### 狀態行和檔案建議閘道

Claude Code 為 `statusLine`、`fileSuggestion` 和 `subagentStatusLine` 做出兩個決定，按此順序：

- **完全關閉** ：當受管設定設定 `disableAllHooks` 時，或當資料夾在與 [設定檔中的 hooks 相同的工作區信任規則](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 下不受信任時
- **縮小到受管設定** ：當設定 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly) 時，當在應用 [設定優先順序](https://code.claude.com/docs/zh-TW/hooks#disable-or-remove-hooks) 後 `disableAllHooks` 在受管設定外為 `true` 時，或當您使用 `--safe-mode` 啟動 Claude Code 時

在縮小下，如果部署了受管值，Claude Code 執行該值。否則它會跳過您的值而不發出警告：狀態行被停用，`@` 自動完成回退到內建檔案建議。

### `disableWorkflows`

為您的設定到達的每個人（例如透過受管設定的組織）關閉 [動態工作流程](https://code.claude.com/docs/zh-TW/workflows#turn-workflows-off) 和捆綁的工作流程命令。若要只為自己開啟或關閉工作流程，請改用 [`enableWorkflows`](https://code.claude.com/docs/zh-TW/settings-reference#enableworkflows)，**動態工作流程** 切換在 `/config` 中寫入您的使用者設定。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 為您的設定到達的每個人關閉動態工作流程和捆綁的工作流程命令
  - `false`：與未設定相同；工作流程是否開啟然後遵循 [`enableWorkflows`](https://code.claude.com/docs/zh-TW/settings-reference#enableworkflows) 和您的計畫預設
- **預設** ：`false`
- **每個工作階段覆蓋** ：[`CLAUDE_CODE_DISABLE_WORKFLOWS`](https://code.claude.com/docs/zh-TW/env-vars) 為一個工作階段關閉工作流程；無論兩者中的哪一個關閉它們，另一個無法將它們打開

settings.json

```
{
  "disableWorkflows": true
}

```

### `enableWorkflows`

當您的計畫預設不是您想要的時，為自己開啟或關閉 [動態工作流程](https://code.claude.com/docs/zh-TW/workflows)。在 `/config` 中顯示為 **動態工作流程** ，它將此金鑰寫入您的使用者設定，並在您切換回計畫預設時再次移除它。若要從受管設定為每個人關閉工作流程，請改用 [`disableWorkflows`](https://code.claude.com/docs/zh-TW/settings-reference#disableworkflows)。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 為您開啟動態工作流程
  - `false`：Claude Code 為您關閉動態工作流程
- **預設** ：未設定，因此工作流程開啟，除非您在 Pro 計畫上，其中它們關閉
- **每個工作階段覆蓋** ：[`CLAUDE_CODE_DISABLE_WORKFLOWS`](https://code.claude.com/docs/zh-TW/env-vars) 為一個工作階段關閉工作流程，此處的 `true` 在設定時無法將它們打開

settings.json

```
{
  "enableWorkflows": true
}

```

[`disableWorkflows`](https://code.claude.com/docs/zh-TW/settings-reference#disableworkflows) 和您的組織工作流程政策也優先：`enableWorkflows: true` 在任何來源關閉工作流程時無法將它們打開。當設定檔中的來源（而不是您的使用者設定）設定 `enableWorkflows` 或將 `disableWorkflows` 設定為 `true` 時，Claude Code 隱藏 `/config` 列。

### `hooks`

在 Claude Code 的生命週期中的點（例如在工具呼叫之前或工作階段啟動時）執行您自己的命令、提示、代理程式、HTTP 請求或 MCP 工具作為 [hooks](https://code.claude.com/docs/zh-TW/hooks)；[hooks 參考](https://code.claude.com/docs/zh-TW/hooks#hook-events) 列出每個事件、其承載資料和其結束代碼。每個事件對應到一個匹配器群組清單，每個群組列出當匹配器適用時執行的處理程式。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Hooks 在檔案中合併而不是相互替換，來自受管設定的 hooks 無法從其他檔案中移除。
- **類型** ：由 [hook 事件](https://code.claude.com/docs/zh-TW/hooks#hook-events) 鍵入的物件；每個值是 `{ "matcher", "hooks" }` 群組的陣列，其 `hooks` 項目的 `type` 為 `"command"`、`"prompt"`、`"agent"`、`"http"` 或 `"mcp_tool"`
- **預設** ：未設定，因此沒有 hooks 執行

此範例在每個 Bash 工具呼叫之前執行指令碼： settings.json

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/check-bash.sh" }
        ]
      }
    ]
  }
}

```

對於每個事件、匹配器模式和處理程式欄位，請參閱 [hooks 參考](https://code.claude.com/docs/zh-TW/hooks#configuration)。若要關閉 hooks，請參閱 [`disableAllHooks`](https://code.claude.com/docs/zh-TW/settings-reference#disableallhooks)；若要將 hooks 限制為您的組織部署的 hooks，請參閱 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly)。

### `httpHookAllowedEnvVars`

[HTTP hook](https://code.claude.com/docs/zh-TW/hooks#http-hook-fields) 可以將環境變數的值放入請求標頭中，例如 `Authorization: Bearer $HOOK_TOKEN` 標頭，但僅適用於 hook 在其自己的 `allowedEnvVars` 中列出的變數。此金鑰為每個 HTTP hook 的該清單設定外部限制：hook 只有在其自己的 `allowedEnvVars` 和此金鑰都命名它時才能使用變數。使用它可以防止 hook 讀取它不應該讀取的祕密，即使 hook 的定義要求它。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。陣列在設定檔中合併。
- **類型** ：環境變數名稱陣列
- **預設** ：未設定，因此每個 hook 自己的 `allowedEnvVars` 清單適用

此範例將標頭插值限制為 `MY_TOKEN` 和 `HOOK_SECRET`： settings.json

```
{
  "httpHookAllowedEnvVars": ["MY_TOKEN", "HOOK_SECRET"]
}

```

允許清單適用於來自每個來源的 hooks，包括受管設定。

### `workflowKeywordTriggerEnabled`

選擇在提示中輸入關鍵字 `ultracode` 是否觸發 [動態工作流程](https://code.claude.com/docs/zh-TW/workflows#ask-for-a-workflow-in-your-prompt)。將其設定為 `false` 以輸入該字而不觸發一個。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在 `/config` 中顯示為 **Ultracode 關鍵字觸發** 。
- **類型** ：布林值
  - `true`：在提示中輸入 `ultracode` 觸發動態工作流程
  - `false`：您可以輸入該字而不觸發一個
- **預設** ：`true`

settings.json

```
{
  "workflowKeywordTriggerEnabled": false
}

```

`ultracode` 努力設定、`/workflows` 和已儲存的工作流程命令不受影響。

### `workflowSizeGuideline`

設定 [Claude 在其編寫的動態工作流程中目標的代理程式計數](https://code.claude.com/docs/zh-TW/workflows#set-a-size-guideline)。Claude Code 將值作為建議而不是強制上限發送給 Claude：`"small"` 要求少於 5 個代理程式，`"medium"` 少於 10 個，`"large"` 少於 50 個。當您想要限制工作流程花費時選擇 `"small"`。需要 Claude Code v2.1.219 或更新版本。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。那裡的值優先於 `/config` 中的 **動態工作流程大小** 選擇，Claude Code 將其儲存在 `~/.claude.json` 中，當設定檔設定金鑰時 Claude Code 隱藏該列。
- **類型** ：字串，其中之一：
  - `"unrestricted"`：無指南，因此 Claude 根據任務調整工作流程大小
  - `"small"`：Claude 目標少於 5 個代理程式
  - `"medium"`：Claude 目標少於 10 個代理程式
  - `"large"`：Claude 目標少於 50 個代理程式
- **預設** ：`"medium"`，或 當您在 Pro 計畫上簽入且使用 Claude Code v2.1.271 或更新版本時為 `"small"`

settings.json

```
{
  "workflowSizeGuideline": "small"
}

```

需要 Claude Code v2.1.219 或更新版本；在 v2.1.202 到 v2.1.218 上，改為在 `/config` 中設定指南。

## 外掛程式和技能

啟用外掛程式、註冊市集、限制組織允許的外掛程式來源，以及控制哪些技能載入。如需安裝和建置外掛程式，請參閱 [外掛程式](https://code.claude.com/docs/zh-TW/plugins)。

### `disableBundledSkills`

關閉 Claude Code 隨附的 [技能](https://code.claude.com/docs/zh-TW/skills) 和工作流程。Claude Code 會完全移除隨附的技能和工作流程，而內建命令（例如 `/init`）仍可輸入但會隱藏在模型中。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 移除隨附的技能和工作流程，並隱藏模型中的內建命令（例如 `/init`）
  - `false`：隨附的技能載入
- **預設** ：未設定，因此隨附的技能會載入
- **每個工作階段覆寫** ：[`CLAUDE_CODE_DISABLE_BUNDLED_SKILLS`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 會在一個工作階段中關閉隨附的技能；無論哪一個關閉它們，另一個都無法將其重新開啟

settings.json

```
{
  "disableBundledSkills": true
}

```

來自外掛程式、`.claude/skills/` 和 `.claude/commands/` 的技能不受影響。`/doctor` 與內建命令一樣仍可輸入；若要隱藏它，請改為設定 [`DISABLE_DOCTOR_COMMAND`](https://code.claude.com/docs/zh-TW/env-vars)。

### `disableSkillShellExecution`

關閉 [技能](https://code.claude.com/docs/zh-TW/skills) 和來自使用者、專案、外掛程式或其他目錄來源的自訂命令中 `!`...\`\` 和 \`\`\`\`!`區塊的內嵌 shell 執行。Claude Code 會用`[shell command execution disabled by policy]\` 取代每個命令，而不是執行它。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。受管設定中的 `true` 無法被其他地方的 `false` 覆寫。
- **類型** ：布林值
  - `true`：Claude Code 用 `[shell command execution disabled by policy]` 取代每個內嵌 shell 命令，而不是執行它
  - `false`：內嵌 shell 執行
- **預設** ：未設定，因此內嵌 shell 執行

settings.json

```
{
  "disableSkillShellExecution": true
}

```

隨附的技能和透過受管設定部署的技能不受影響。

### `skillOverrides`

隱藏或摺疊 [技能](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings)，而不編輯其 `SKILL.md`。Claude Code 會將每個技能名稱下的值套用到 Claude 看到的技能清單和您的 `/` 自動完成。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。`/skills` 功能表寫入 `.claude/settings.local.json`。
- **類型** ：將技能名稱對應到以下其中之一的物件：
  - `"on"`：Claude 看到該技能，您可以輸入 `/name`
  - `"name-only"`：Claude 按名稱看到該技能，但不看到其描述
  - `"user-invocable-only"`：Claude 看不到該技能，但您仍可輸入 `/name`
  - `"off"`：Claude 看不到該技能，`/name` 在自動完成中隱藏
- **預設** ：未設定，因此每個技能都是 `"on"`

此範例將 `legacy-context` 僅按名稱列出給 Claude，並隱藏 Claude 和 `/` 自動完成中的 `deploy`： settings.json

```
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}

```

覆寫不適用於外掛程式技能，您可以透過 `/plugin` 管理這些技能。 在受管設定和使用 `--settings` 傳遞的檔案中，隨附技能別名上的金鑰（例如 `/doctor` 的 `checkup`）也適用於該技能；請參閱 [別名金鑰如何與技能自身名稱上的金鑰結合](https://code.claude.com/docs/zh-TW/skills#override-skill-visibility-from-settings)。

### `syncClaudeAiSkills`

關閉 [您在 claude.ai 上啟用的技能](https://code.claude.com/docs/zh-TW/skills#how-synced-skills-behave) 的下載。Claude Code 會將它們下載到 `~/.claude/skills/synced/`，在 [您使用 claude.ai 帳戶登入的終端工作階段](https://code.claude.com/docs/zh-TW/skills#where-synced-skills-load)（互動或非互動）以及在 Cowork 和雲端工作階段中。設定為 `false` 以停止該下載並停止載入已同步的技能。Claude Code 僅接受 `false`：`true` 與未設定相同，不會開啟同步。

- **範圍** ：[`使用者、本機或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)，以及使用 `--settings` 傳遞的檔案。儲存庫無法為您關閉它。
- **類型** ：布林值
  - `false`：Claude Code 停止下載同步的技能，並停止載入 `~/.claude/skills/synced/` 中已有的技能。在使用者或受管設定中，它也會將它們移至 `~/.claude/skills/.trash/`
  - `true`：與未設定相同
- **預設** ：未設定，因此使用 claude.ai 帳戶登入的工作階段會同步您的技能

此範例防止機器在任何工作階段中下載帳戶的技能： settings.json

```
{
  "syncClaudeAiSkills": false
}

```

### `syncClaudeAiPlugins`

關閉 [您在 claude.ai 帳戶上啟用的外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#synced-plugins) 的下載。Claude Code 會將它們下載到 `~/.claude/plugins/synced/`，在您使用 claude.ai 帳戶登入的終端工作階段開始時，以及在 Cowork 和雲端工作階段中，並將每個載入為 `<name>@synced`。設定為 `false` 以停止該下載並停止載入已同步的外掛程式。Claude Code 僅接受 `false`：`true` 與未設定相同，不會開啟同步。需要 Claude Code v2.1.273 或更新版本。

- **範圍** ：[`使用者、本機或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)，以及使用 `--settings` 傳遞的檔案。儲存庫無法為您關閉它。
- **類型** ：布林值
  - `false`：Claude Code 停止下載同步的外掛程式，並停止載入 `~/.claude/plugins/synced/` 中已有的外掛程式。在使用者或受管設定中，它也會將它們移至 `~/.claude/plugins/.trash/`
  - `true`：與未設定相同
- **預設** ：未設定，因此使用 claude.ai 帳戶登入的工作階段會同步您的外掛程式

若要關閉一個同步的外掛程式而不是全部，請在 [`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 中設定 `"<name>@synced": false`。 此範例防止機器在任何工作階段中下載帳戶的外掛程式： settings.json

```
{
  "syncClaudeAiPlugins": false
}

```

### `allowedChannelPlugins`

選擇哪些 [頻道](https://code.claude.com/docs/zh-TW/channels) 外掛程式可以將訊息推送到組織中的工作階段。設定後，Claude Code 會使用您的清單取代預設的 Anthropic 允許清單；每個項目命名一個外掛程式及其來自的市集。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：物件陣列，每個物件都有 `marketplace` 和 `plugin` 字串。項目可以改為 `"plugin@marketplace"` 字串，例如 `"telegram@claude-plugins-official"`，Claude Code 將其視為等效物件。字串形式需要 Claude Code v2.1.267 或更新版本；較早版本在 `allowedChannelPlugins` 包含一個時會拒絕整個值
- **預設** ：未設定，因此 Claude Code 使用預設的 Anthropic 允許清單

此範例開啟頻道，並僅允許來自官方 Anthropic 市集的 Telegram 外掛程式： managed-settings.json

```
{
  "channelsEnabled": true,
  "allowedChannelPlugins": [
    { "marketplace": "claude-plugins-official", "plugin": "telegram" }
  ]
}

```

空陣列會阻止每個頻道外掛程式。 此金鑰在頻道通過帳戶的 [`channelsEnabled`](https://code.claude.com/docs/zh-TW/settings-reference#channelsenabled) 閘道後生效：在 Team 和 Enterprise 方案上，以及在具有受管設定的 Console 帳戶上，這表示 `channelsEnabled: true`。請參閱 [限制哪些頻道外掛程式可以執行](https://code.claude.com/docs/zh-TW/channels#restrict-which-channel-plugins-can-run)。

### `blockedMarketplaces`

為您的組織阻止外掛程式市集來源。Claude Code 在市集新增和外掛程式安裝、更新、重新整理和自動更新時檢查封鎖清單，因此在您設定原則之前某人新增的市集無法用於擷取外掛程式。在下載前檢查被阻止的來源，因此它們永遠不會接觸檔案系統。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：市集來源物件的陣列，形式與 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#allowed-source-types) 相同
- **預設** ：未設定，因此沒有市集被阻止

此範例阻止一個 GitHub 儲存庫作為市集來源： managed-settings.json

```
{
  "blockedMarketplaces": [
    { "source": "github", "repo": "untrusted/plugins" }
  ]
}

```

`github` 項目可能使用 [所有者萬用字元形式](https://code.claude.com/docs/zh-TW/settings-reference#owner-wildcards) `"owner/*"` 來阻止該 GitHub 所有者下的每個儲存庫，這需要 Claude Code v2.1.223 或更新版本。新增 `{ "source": "skills-dir" }` 以停止 Claude Code 從 `~/.claude/skills/` 載入 [`@skills-dir` 外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)，而不限制任何市集。請參閱 [受管市集限制](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)。

### `channelsEnabled`

為您的組織允許 [頻道](https://code.claude.com/docs/zh-TW/channels)。在 claude.ai Team 和 Enterprise 方案上，Claude Code 會阻止頻道，直到您將其設定為 `true`。對於使用 API 金鑰進行驗證的 [Anthropic Console](https://code.claude.com/docs/zh-TW/authentication#claude-console-authentication) 帳戶，預設允許頻道。如果您的組織部署受管設定，Claude Code 也會在這些帳戶上阻止頻道，直到您將此金鑰設定為 `true`。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 為您的組織允許頻道
  - `false`：與未設定相同；頻道是否被阻止取決於您的方案，如預設所述
- **預設** ：未設定；在 Team 和 Enterprise 方案以及具有受管設定的 Console 帳戶上阻止頻道，在 Pro 和 Max 方案以及沒有受管設定的 Console 帳戶上允許

managed-settings.json

```
{
  "channelsEnabled": true
}

```

若要限制啟用後哪些外掛程式可以註冊為頻道，請設定 [`allowedChannelPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#allowedchannelplugins)。請參閱 [企業控制](https://code.claude.com/docs/zh-TW/channels#enterprise-controls)。

### `disableCommandPluginSources`

阻止 [`command` 外掛程式來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#command-sources)，它透過在使用者機器上執行市集宣告的命令來安裝外掛程式。當您將其設定為 `true` 時，Claude Code 永遠不會執行該命令，不會安裝或更新命令來源的外掛程式，並停止載入已安裝的外掛程式。設定為 `false` 以明確允許它們。無論何時阻止命令來源，無論您將其設定為 `true` 還是在 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly) 下保持未設定，它也會阻止市集 [`headersHelper` 命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#authenticate-archive-downloads)，除了受管設定本身宣告的市集。需要 Claude Code v2.1.229 或更新版本，`headersHelper` 阻止需要 v2.1.238 或更新版本。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 永遠不會執行市集宣告的命令，不會安裝或更新命令來源的外掛程式，並停止載入已安裝的外掛程式
  - `false`：Claude Code 明確允許命令來源的外掛程式
- **預設** ：未設定，因此 Claude Code 遵循 [`allowManagedHooksOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedhooksonly)：限制 hook 執行到受管設定的組織也會停用命令來源

managed-settings.json

```
{
  "disableCommandPluginSources": true
}

```

需要 Claude Code v2.1.229 或更新版本。

### `pluginSuggestionMarketplaces`

命名其外掛程式可以作為內容相關安裝建議出現的市集，在微調提示和釘選在 `/plugin` **Discover** 標籤頂部。內建的第一方前端設計提示不受影響。建議來自每個外掛程式在其市集項目中的 `relevance` 宣告。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：市集名稱的陣列
- **預設** ：未設定，因此沒有市集宣告的建議出現

managed-settings.json

```
{
  "pluginSuggestionMarketplaces": ["acme-corp-plugins"]
}

```

名稱僅在市集在機器上註冊且其註冊來源也在相同受管設定中宣告時生效，作為該名稱的 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 項目或作為 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces) 的項目。Claude Code 忽略從不同來源在允許清單名稱下註冊的市集。官方市集豁免於來源要求：僅允許清單其名稱就足夠了，因為該名稱只能從官方 Anthropic 來源註冊。請參閱 [按內容建議外掛程式](https://code.claude.com/docs/zh-TW/plugin-relevance)。

### `pluginTrustMessage`

將您組織自己的文字新增到 Claude Code 在安裝前顯示的外掛程式信任警告中，例如確認來自您內部市集的外掛程式已經過審查。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串
- **預設** ：未設定，因此 Claude Code 僅顯示標準警告

managed-settings.json

```
{
  "pluginTrustMessage": "All plugins from our marketplace are approved by IT"
}

```

### `strictKnownMarketplaces`

限制組織中的人員可以新增和安裝外掛程式的外掛程式市集來源。Claude Code 在市集新增和外掛程式安裝、更新、重新整理和自動更新時強制執行允許清單，在任何網路或檔案系統操作之前，因此在您設定原則之前某人新增的市集一旦其來源不再符合就無法用於擷取外掛程式。被阻止的使用者會看到命名受管原則的錯誤。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：市集來源物件的陣列；請參閱 [允許的來源類型](https://code.claude.com/docs/zh-TW/settings-reference#allowed-source-types)
- **預設** ：未設定，因此使用者可以新增任何市集。空陣列是完全鎖定，阻止每個市集來源，包括官方 Anthropic 市集

此範例允許兩個 GitHub 儲存庫，一個釘選到 `v2.0` ref，一個託管 `marketplace.json` URL： managed-settings.json

```
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/approved-plugins" },
    { "source": "github", "repo": "acme-corp/security-tools", "ref": "v2.0" },
    { "source": "url", "url": "https://plugins.example.com/marketplace.json" }
  ]
}

```

您也可以將此金鑰寫為 `allowedMarketplaces`；[市集金鑰別名](https://code.claude.com/docs/zh-TW/settings-reference#marketplace-key-aliases) 描述 Claude Code 如何處理別名以及哪個版本接受它。此金鑰是原則閘道：它控制使用者可能新增的內容，但不註冊任何內容。若要在一個檔案中限制和預先註冊，請參閱 [與 `extraKnownMarketplaces` 結合](https://code.claude.com/docs/zh-TW/settings-reference#combine-with-extraknownmarketplaces)。如需使用者面向的檢視，請參閱 [受管市集限制](https://code.claude.com/docs/zh-TW/plugin-marketplaces#managed-marketplace-restrictions)。

#### 允許的來源類型

下面每個項目顯示每個來源類型的一個允許清單項目及其接受的欄位。大多數類型完全符合；`hostPattern` 和 `pathPattern` 按正規表達式符合，`github` 項目可以使用 [所有者萬用字元](https://code.claude.com/docs/zh-TW/settings-reference#owner-wildcards)。

| 來源                             | 範例項目                                                                                                                        | 欄位                                                                          |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `github`                         | `{ "source": "github", "repo": "acme-corp/plugins", "ref": "main", "path": "marketplace" }`                                     | `repo` 必需；`ref` 是分支或標籤；`path` 是子目錄                              |
| `git`                            | `{ "source": "git", "url": "https://gitlab.example.com/tools/plugins.git", "ref": "production" }`                               | `url` 必需；`ref` 和 `path` 如 `github`                                       |
| `url`                            | `{ "source": "url", "url": "https://plugins.example.com/marketplace.json", "headers": { "Authorization": "Bearer ${TOKEN}" } }` | `url` 必需；`headers` 為已驗證存取新增 HTTP 標頭                              |
| `npm`                            | `{ "source": "npm", "package": "@acme-corp/claude-plugins" }`                                                                   | `package` 必需，包含 `marketplace.json` 的 npm 套件                           |
| `file`                           | `{ "source": "file", "path": "/opt/acme-corp/plugins/marketplace.json" }`                                                       | `path` 必需，`marketplace.json` 檔案的絕對路徑                                |
| `directory`                      | `{ "source": "directory", "path": "/opt/acme-corp/approved-marketplaces" }`                                                     | `path` 必需，包含 `.claude-plugin/marketplace.json` 的目錄的絕對路徑          |
| `hostPattern`                    | `{ "source": "hostPattern", "hostPattern": "^github\\.example\\.com$" }`                                                        | `hostPattern` 必需，針對市集主機符合的正規表達式                              |
| `pathPattern`                    | `{ "source": "pathPattern", "pathPattern": "^/opt/approved/" }`                                                                 | `pathPattern` 必需，針對 `file` 和 `directory` 來源的 `path` 符合的正規表達式 |
| `skills-dir`                     | `{ "source": "skills-dir" }`                                                                                                    | 無欄位。選擇 `~/.claude/skills/` 外掛程式掃描回入                             |
| 三個來源類型帶有超出表格的規則： |                                                                                                                                 |                                                                               |

- **`url`**：URL 市集僅下載`marketplace.json` 檔案，Claude Code 不會從該伺服器按相對路徑擷取外掛程式檔案，因此其外掛程式必須使用 [外掛程式來源](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugin-sources)，而不是相對路徑，例如存檔 URL，可以在同一主機上。對於具有相對路徑的外掛程式，請改用基於 Git 的市集。請參閱 [URL 型市集中的相對路徑外掛程式失敗](https://code.claude.com/docs/zh-TW/plugin-marketplaces#plugins-with-relative-paths-fail-in-url-based-marketplaces)。
- **`hostPattern`**：使用它允許內部 GitHub Enterprise 或 GitLab 伺服器上的每個市集，而不列出每個儲存庫。Claude Code 針對`github.com` 符合 `github` 來源，從 `url` 來源取得主機名稱，並根據 [git URL](https://git-scm.com/docs/git-clone#_git_urls) 的形式從 `git` 來源取得：
  - 具有配置的 URL，例如 `https://` 或 `ssh://`：URL 中的主機名稱。
  - 沒有配置的 SSH 位址，採用 git 的 `user@host:path` 形式，例如 `git@git.example.com:tools/plugins.git`：`@` 和 `:` 之間的主機，這是 git 連接到的主機。
  - 任何其他沒有配置的形式：沒有主機，因此沒有 `strictKnownMarketplaces` `hostPattern` 項目符合它。對於 `blockedMarketplaces` `hostPattern`，Claude Code 從更廣泛的形式集合中取得主機，因此封鎖清單項目仍可符合此類形式。在 v2.1.234 之前，`strictKnownMarketplaces` `hostPattern` 也符合 git 不視為 SSH 位址的某些形式。 `file` 和 `directory` 來源沒有主機，永遠不符合 `hostPattern` 項目。
- **`pathPattern`**：使用它允許檔案系統市集與網路來源的`hostPattern` 項目一起。`".*"` 允許每個本機路徑；較窄的模式（例如 `"^/opt/approved/"`）限制到目錄。

任何允許清單，即使是空的，也會停止 Claude Code 從 `~/.claude/skills/` 載入 [`@skills-dir` 外掛程式](https://code.claude.com/docs/zh-TW/plugins-reference#skills-directory-plugins)。新增 `{ "source": "skills-dir" }` 項目以繼續載入它們；該項目在此金鑰和 `blockedMarketplaces` 之外沒有意義。

#### 所有者萬用字元

`repo` 值為 `"<owner>/*"` 的 `github` 項目符合該 GitHub 所有者下的每個儲存庫。所有者萬用字元需要 Claude Code v2.1.223 或更新版本，僅在 `strictKnownMarketplaces` 和 `blockedMarketplaces` 中有效。在 `github` 來源出現的其他地方，例如 `extraKnownMarketplaces` 或 `/plugin marketplace add`，`repo` 值必須命名單個儲存庫。在 v2.1.223 之前，Claude Code 按字面比較項目，因此允許清單項目不符合任何儲存庫，封鎖清單項目不阻止任何內容；單儲存庫項目在每個版本上強制執行。 此項目允許 `acme-corp` 組織中的任何市集儲存庫： managed-settings.json

```
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/*" }
  ]
}

```

只有整個儲存庫名稱位置可以是萬用字元。Claude Code 按字面比較項目，例如 `*`、`*/plugins` 或 `acme-corp/tools-*`，因此它們不符合任何儲存庫。 兩個設定之間的符合規則不同：

| 規則         | `strictKnownMarketplaces`                                                                             | `blockedMarketplaces`                                |
| ------------ | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 符合來源拼寫 | 僅 `owner/repo` 形式。複製相同儲存庫的 git URL 不符合                                                 | 任何拼寫，包括解析為相同 github.com 儲存庫的 git URL |
| 所有者大小寫 | 區分大小寫，如精確項目符合                                                                            | 不區分大小寫                                         |
| `ref`        | 遵循精確項目規則：具有 `ref` 的項目僅符合具有該精確 ref 的來源，沒有項目的項目僅符合不指定 ref 的來源 | 沒有 `ref` 的項目阻止它符合的儲存庫的所有 ref        |
| `path`       | 比精確項目規則更寬鬆：具有 `path` 的項目需要該精確值，而沒有項目的項目符合儲存庫內的任何路徑          | 沒有 `path` 的項目阻止它符合的儲存庫的所有路徑       |

#### 精確符合

對於除所有者萬用字元 `github` 項目和正規表達式符合的 `hostPattern` 和 `pathPattern` 項目之外的每個來源類型，Claude Code 僅在市集來源與項目完全符合時允許使用者的新增。對於基於 git 的來源 `github` 和 `git`，精確符合包括可選欄位：

- `repo` 或 `url` 必須完全符合
- `ref` 欄位必須完全符合，或兩者都未定義
- `path` 欄位必須完全符合，或兩者都未定義

例如，Claude Code 將下面的每一對視為兩個不同的來源：

- `{ "source": "github", "repo": "acme-corp/plugins" }` 和 `{ "source": "github", "repo": "acme-corp/plugins", "ref": "main" }`
- `{ "source": "github", "repo": "acme-corp/plugins", "path": "marketplace" }` 和 `{ "source": "github", "repo": "acme-corp/plugins" }`

#### 僅允許官方市集

若要僅允許官方 Anthropic 市集，列出其儲存庫： managed-settings.json

```
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "anthropics/claude-plugins-official" }
  ]
}

```

使用此項目，Claude Code 保持已註冊的官方市集可用，並在新機器上，在您首次以互動方式啟動 Claude Code 時自動註冊市集。自動註冊最常遺漏：

- 在機器首次互動啟動之前執行的非互動環境。
- Claude Code 已在阻止市集的原則下以互動方式執行的機器，例如空陣列鎖定。Claude Code 記錄被阻止的嘗試，不會在原則變更後重試。

在這些機器上，將市集新增到相同 `managed-settings.json` 中的 [`extraKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces)，以便 Claude Code 自動註冊它，或執行 `claude plugin marketplace add anthropics/claude-plugins-official`。

#### 與 `extraKnownMarketplaces` 結合

兩個金鑰執行不同的工作。此表比較它們：

| 方面                                                                          | `strictKnownMarketplaces` | `extraKnownMarketplaces`                                   |
| ----------------------------------------------------------------------------- | ------------------------- | ---------------------------------------------------------- |
| 目的                                                                          | 組織原則強制執行          | 團隊便利                                                   |
| 設定檔                                                                        | 僅受管設定                | 任何設定檔                                                 |
| 行為                                                                          | 阻止非允許清單新增        | 註冊遺漏的市集                                             |
| 何時強制執行                                                                  | 在網路和檔案系統操作之前  | 立即從使用者或受管設定；在儲存庫檔案的工作區信任對話框之後 |
| 可以覆寫                                                                      | 否，最高優先順序          | 是，由更高優先順序的設定                                   |
| 來源格式                                                                      | 直接來源物件              | 具有巢狀 `source` 物件的命名市集                           |
| 若要為所有使用者限制和預先註冊市集，請在 `managed-settings.json` 中設定兩者： |                           |                                                            |
| managed-settings.json                                                         |                           |                                                            |

```
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/plugins" }
  ],
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": { "source": "github", "repo": "acme-corp/plugins" }
    }
  }
}

```

僅設定 `strictKnownMarketplaces` 時，使用者仍可使用 `/plugin marketplace add` 自行新增允許的市集。官方 Anthropic 市集是 Claude Code 自動註冊的唯一市集，僅當允許清單允許時。[僅允許官方市集](https://code.claude.com/docs/zh-TW/settings-reference#allow-only-the-official-marketplace) 列出它遺漏的機器。

### `strictPluginOnlyCustomization`

阻止技能、代理、hooks 和 MCP 伺服器來自使用者和專案來源，因此它們只能來自外掛程式或受管設定。將其與 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces) 結合以控制完整的自訂供應鏈：市集允許清單控制使用者可以安裝哪些外掛程式。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：`true` 以鎖定所有四種自訂，或命名要鎖定的種類的陣列，來自 `"skills"`、`"agents"`、`"hooks"` 和 `"mcp"`
- **預設** ：未設定，因此沒有任何內容被鎖定

此範例鎖定技能和 hooks，並保持代理和 MCP 伺服器解鎖： managed-settings.json

```
{
  "strictPluginOnlyCustomization": ["skills", "hooks"]
}

```

下面的四個子金鑰項目列出每個表面阻止的內容以及仍然載入的內容。Claude Code 忽略它不識別的表面名稱，而不是使設定檔失敗，因此您可以在每個用戶端更新之前新增新的表面名稱。

### `strictPluginOnlyCustomization.skills`

鎖定 `skills` 表面。Claude Code 停止從 `~/.claude/skills/` 和 `.claude/skills/`、`~/.claude/commands/` 和 `.claude/commands/` 的自訂命令、`--add-dir` 目錄下的技能以及從您的 claude.ai 帳戶同步的技能載入技能，並繼續載入外掛程式技能、隨附技能和受管原則目錄中的技能。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：[`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization) 陣列中的字串 `"skills"`
- **預設** ：未鎖定

managed-settings.json

```
{
  "strictPluginOnlyCustomization": ["skills"]
}

```

### `strictPluginOnlyCustomization.agents`

鎖定 `agents` 表面。Claude Code 停止從 `~/.claude/agents/` 和 `.claude/agents/` 載入代理，並繼續載入外掛程式代理、內建代理和受管原則目錄中的代理。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：[`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization) 陣列中的字串 `"agents"`
- **預設** ：未鎖定

managed-settings.json

```
{
  "strictPluginOnlyCustomization": ["agents"]
}

```

### `strictPluginOnlyCustomization.hooks`

鎖定 `hooks` 表面。Claude Code 停止執行來自使用者、專案和本機 `settings.json` 的 hooks，並繼續執行外掛程式 hooks 和受管設定中的 hooks。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：[`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization) 陣列中的字串 `"hooks"`
- **預設** ：未鎖定

managed-settings.json

```
{
  "strictPluginOnlyCustomization": ["hooks"]
}

```

### `strictPluginOnlyCustomization.mcp`

鎖定 `mcp` 表面。Claude Code 停止從 `~/.claude.json` 和 `.mcp.json` 載入 MCP 伺服器，並繼續載入外掛程式 MCP 伺服器、[`managed-mcp.json`](https://code.claude.com/docs/zh-TW/managed-mcp) 伺服器和來自 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 的伺服器。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：[`strictPluginOnlyCustomization`](https://code.claude.com/docs/zh-TW/settings-reference#strictpluginonlycustomization) 陣列中的字串 `"mcp"`
- **預設** ：未鎖定

managed-settings.json

```
{
  "strictPluginOnlyCustomization": ["mcp"]
}

```

### `enabledPlugins`

開啟或關閉個別 [外掛程式](https://code.claude.com/docs/zh-TW/plugins)，由 `plugin-name@marketplace-name` 鍵入。在任何範圍都沒有項目的外掛程式會回退到其 [`defaultEnabled`](https://code.claude.com/docs/zh-TW/plugins-reference#default-enablement) 值。當您使用 `/plugin` 或 `claude plugin enable` 啟用或停用外掛程式時，Claude Code 會為您寫入此金鑰。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：將 `plugin-name@marketplace-name` 對應到布林值的物件
- **預設** ：未設定，因此每個外掛程式遵循其 `defaultEnabled` 值

此範例啟用來自 `team-tools` 市集的兩個外掛程式，並停用來自 `personal` 的一個： settings.json

```
{
  "enabledPlugins": {
    "code-formatter@team-tools": true,
    "deployment-tools@team-tools": true,
    "experimental-features@personal": false
  }
}

```

每個範圍服務於不同的目的：

- **使用者設定** ：您的個人外掛程式偏好設定
- **專案設定** ：與儲存庫中的每個人共享的外掛程式
- **本機設定** ：每台機器的覆寫，當 Claude Code 在那裡儲存設定時被 gitignored
- **受管設定** ：組織範圍的原則。設定為 `false` 的外掛程式在每個範圍都被阻止安裝，並從市集隱藏

專案設定優先於使用者設定，因此在 `~/.claude/settings.json` 中將外掛程式設定為 `false` 不會停用專案的 `.claude/settings.json` 啟用的外掛程式。若要在您的機器上選擇退出專案啟用的外掛程式，請改為在 `.claude/settings.local.json` 中將其設定為 `false`。由受管設定強制啟用的外掛程式無法以這種方式停用，因為受管設定覆寫本機設定。 在專案的 `.claude/settings.json` 中啟用來自外部來源（例如 GitHub 儲存庫或 npm 套件）的外掛程式不會為其他人安裝它。在載入外掛程式的每個路徑上，Claude Code 報告外掛程式未安裝，直到每個使用者 [自行安裝它](https://code.claude.com/docs/zh-TW/discover-plugins#configure-team-marketplaces)。

### `extraKnownMarketplaces`

按名稱註冊其他外掛程式市集，以便開啟儲存庫的人或受管設定到達的每個人都能獲得市集，而無需自行新增。Claude Code 註冊它尚不知道的每個市集。[`enabledPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#enabledplugins) 從它命名的外掛程式是否安裝取決於外掛程式的來源以及哪個檔案啟用它；該項目有規則。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 僅在您接受該資料夾的工作區信任對話框後才接受儲存庫的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的項目；在您未信任的資料夾中，包括 `-p` 執行，它會在沒有訊息的情況下忽略它們。
- **類型** ：將市集名稱對應到具有 `source` 物件和可選 `autoUpdate` 布林值的物件的物件
- **預設** ：未設定

此範例註冊 GitHub 市集和來自自託管 git URL 的市集： settings.json

```
{
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    },
    "security-plugins": {
      "source": {
        "source": "git",
        "url": "https://git.example.com/security/plugins.git"
      }
    }
  }
}

```

[在您信任資料夾之前執行的內容](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 將信任閘道與儲存庫可以提供的其他內容進行比較。您也可以將此金鑰寫為 `additionalMarketplaces`；請參閱 [市集金鑰別名](https://code.claude.com/docs/zh-TW/settings-reference#marketplace-key-aliases)。 設定 `"autoUpdate": true` 與 `source` 一起，使 Claude Code 在啟動後在背景重新整理該市集並更新其已安裝的外掛程式。省略時，`claude-plugins-official` 和大多數其他官方 Anthropic 市集預設為 `true`，第三方市集預設為 `false`。請參閱 [配置自動更新](https://code.claude.com/docs/zh-TW/discover-plugins#configure-auto-updates)。 當多個設定檔在相同名稱下定義市集項目時，Claude Code 使用來自 [最高優先順序檔案](https://code.claude.com/docs/zh-TW/settings#settings-precedence) 的項目。該項目取代較低優先順序的項目，不繼承其任何欄位，因此重新定義無法將一個檔案的 `source.headers` 認證與另一個檔案控制的 URL 結合。在 v2.1.228 之前，Claude Code 按欄位合併相同名稱的項目，因此較高優先順序檔案中的項目可能繼承它未設定的欄位，包括另一個檔案的 `headers`。

#### 市集來源類型

`source` 物件採用以下其中一種形式：

- **`github`**：GitHub 儲存庫，具有`repo`
- **`git`**：任何 git URL，具有`url`
- **`url`**：直接 URL 到`marketplace.json` 檔案，具有 `url` 和可選 `headers` 和 `headersHelper` 用於已驗證存取。`headersHelper` 命名列印標頭的命令，其值太短暫而無法在 `headers` 中列出，並需要 Claude Code v2.1.238 或更新版本
- **`file`**：`marketplace.json` 檔案的本機路徑，具有 `path`
- **`directory`**：本機檔案系統路徑，具有`path` ，僅用於開發
- **`settings`**：直接在設定檔中宣告的內嵌市集，無需託管儲存庫，具有`name` 和 `plugins`

`git` 來源類型適用於任何 git 託管服務，包括自託管 GitLab 和 Bitbucket。Claude Code 使用 `git clone` 在該機器上使用的相同驗證複製儲存庫：已配置的認證助手或 SSH 金鑰。提供者令牌（例如 `GITHUB_TOKEN`）僅透過讀取它的認證助手生效。請參閱 [私人儲存庫](https://code.claude.com/docs/zh-TW/plugin-marketplaces#private-repositories) 以取得設定詳細資訊。 對於 `github` 和 `git` 來源，Claude Code 在複製市集儲存庫以新增或更新時永遠不會下載 [Git LFS](https://git-lfs.com) 內容。LFS 追蹤的檔案會簽出為指標檔案，新增或更新輸出會報告有多少個。 `skipLfs` 欄位在 `source` 物件內被接受且沒有效果。在 v2.1.274 之前，Claude Code 下載 LFS 內容，除非您設定 `"skipLfs": true`。 對於 `url` 來源，當 `headers` 中的認證過期且命令必須產生新認證時，在 `source` 物件內設定 `headersHelper`。需要 Claude Code v2.1.238 或更新版本。如需命令必須列印的內容以及 Claude Code 執行它的位置，請參閱 [編寫 headersHelper 命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#write-the-headershelper-command)，以及 Claude Code 不執行它的情況，請參閱 [何時 Claude Code 跳過 headersHelper 命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#when-claude-code-skips-a-headershelper-command-or-drops-its-output)。在 `https://` 市集 URL 上設定 `headersHelper` 後，Claude Code 在兩個點執行命令，重複使用一次執行的輸出長達 60 秒：

- 在該市集 `marketplace.json` 的每次擷取之前，包括稍後的重新整理。Claude Code 使用該擷取傳送列印的標頭。
- 在市集 URL 來源上的每個外掛程式存檔下載之前，意思是相同的配置、主機和連接埠。Claude Code 使用該下載傳送輸出，沒有其他下載獲得標頭。

Claude Code 忽略在您使用 [`--add-dir`](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 新增的目錄的 `.claude/settings.json` 或 `.claude/settings.local.json` 中設定的任何 `headersHelper`，在 `url` 來源和內嵌外掛程式項目上，並僅傳送在該檔案中設定的固定 `headers`。[使用者如何接受 headersHelper 命令](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-a-headershelper-command) 涵蓋其他設定檔。 在 `settings` 來源中列出的外掛程式必須參考外部來源（例如 GitHub 或 npm），`name` 必須符合市集金鑰。您仍需在 `enabledPlugins` 中分別啟用每個外掛程式。此範例宣告一個內嵌外掛程式： settings.json

```
{
  "extraKnownMarketplaces": {
    "team-tools": {
      "source": {
        "source": "settings",
        "name": "team-tools",
        "plugins": [
          {
            "name": "code-formatter",
            "source": {
              "source": "github",
              "repo": "acme-corp/code-formatter"
            }
          }
        ]
      }
    }
  }
}

```

在 `source: 'settings'` 下的外掛程式項目，其自身 `source` 是 [`archive`](https://code.claude.com/docs/zh-TW/plugin-marketplaces#zip-archives)，可以為存檔下載設定 `headers`。如果您要放在 `headers` 中的值是短暫的，例如您的登錄機構應要求時鑄造的令牌，請改為設定 `headersHelper` 命令。項目可能同時設定兩者。兩個欄位都需要 Claude Code v2.1.238 或更新版本。 Claude Code 傳送項目的 `headers` 和命令列印的任何內容，與該外掛程式的存檔下載以及沒有其他下載。Claude Code 僅在使用者 [自行安裝或更新該一個外掛程式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#how-users-accept-a-headershelper-command) 時執行命令。三個進一步的規則取決於哪個檔案保持項目：

- **`strict`**：與市集`marketplace.json` 中的項目不同，設定檔中的項目不需要 `"strict": false`，因為設定檔不帶有要內嵌的清單欄位。請參閱 [嚴格模式](https://code.claude.com/docs/zh-TW/plugin-marketplaces#strict-mode)。
- **資料夾信任** ：對於專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的項目，Claude Code 僅在使用者也 [信任該資料夾](https://code.claude.com/docs/zh-TW/permissions#what-runs-before-you-trust-a-folder) 後執行命令。
- **標頭篩選** ：Claude Code 從專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 中的項目中刪除 [要求路由和用戶端身分標頭名稱](https://code.claude.com/docs/zh-TW/plugin-marketplaces#when-claude-code-skips-a-headershelper-command-or-drops-its-output)，因為儲存庫可以提供這些檔案。Claude Code 將相同的篩選套用到目錄項目和 `--add-dir` 目錄設定中的項目，不篩選您的使用者設定、`--settings` 檔案或受管設定中的項目。

#### 市集金鑰別名

在 Claude Code v2.1.232 或更新版本上，您可以將 `extraKnownMarketplaces` 寫為 `additionalMarketplaces`，將 `strictKnownMarketplaces` 寫為 `allowedMarketplaces`。Claude Code 按如下方式處理每個別名：

- 較早版本忽略別名，因此在較舊版本也讀取的檔案中保持規範拼寫，例如具有混合 Claude Code 版本的機隊的受管設定檔案。
- 在接受規範金鑰的任何設定檔中，Claude Code 完全按照讀取規範金鑰的方式讀取別名。
- Claude Code 在更新檔案時可能將 `additionalMarketplaces` 重寫為 `extraKnownMarketplaces`。
- 如果您在一個檔案中設定兩個拼寫，Claude Code 使用規範值並忽略別名。

### `pluginConfigs`

儲存您提供給外掛程式 [`userConfig`](https://code.claude.com/docs/zh-TW/plugins-reference#user-configuration) 配置對話框的非敏感答案，由外掛程式 ID 鍵入。當您填寫對話框時，Claude Code 將此金鑰寫入您的使用者設定，因此您無需手動編輯它。Claude Code 將敏感選項儲存在 macOS Keychain 中，當 Keychain 拒絕寫入時回退到 `~/.claude/.credentials.json`；在沒有支援的 keychain 的平台上，它將它們儲存在 `~/.claude/.credentials.json`。

- **範圍** ：[`使用者或受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：將外掛程式 ID 對應到具有 `options` 欄位的物件，將每個選項名稱對應到字串、數字、布林值或字串陣列，以及保持每個伺服器使用者配置值的可選 `mcpServers` 欄位，形式相同
- **預設** ：未設定

此範例儲存來自 `acme-tools` 的 `deployer` 外掛程式的 `api_endpoint` 選項： settings.json

```
{
  "pluginConfigs": {
    "deployer@acme-tools": {
      "options": {
        "api_endpoint": "https://api.example.com"
      }
    }
  }
}

```

內建外掛程式使用相同的金鑰與 `@builtin` 後綴儲存其選項。例如，[**專案指示**](https://code.claude.com/docs/zh-TW/memory#choose-which-instruction-files-load) 設定（控制 Claude Code 是否讀取 `AGENTS.md` 檔案）是 `pluginConfigs["agents-md@builtin"].options.instructionFiles`。 Claude Code 忽略專案和本機項目，因為它將這些值替換到外掛程式 hook、MCP 和 LSP 配置中，而複製的儲存庫不得能夠提供它們。在 v2.1.207 之前，也讀取了專案和本機設定。

## MCP

控制 Claude Code 連接到哪些 MCP 伺服器，以及組織允許哪些伺服器。請參閱[使用 MCP 連接到外部工具](https://code.claude.com/docs/zh-TW/mcp)和[受管 MCP 設定](https://code.claude.com/docs/zh-TW/managed-mcp)。

### `allowAllClaudeAiMcps`

載入 [claude.ai 連接器](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai)，Claude Code 會在部署的 `managed-mcp.json` 旁邊自行擷取這些連接器。沒有此金鑰，`managed-mcp.json` 會獨佔控制 MCP 伺服器並抑制這些連接器。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。使用者無法重新啟用獨佔控制所抑制的連接器。
- **類型** ：布林值
  - `true`：Claude Code 會在部署的 `managed-mcp.json` 旁邊載入 claude.ai 連接器
  - `false`：部署的 `managed-mcp.json` 獨佔控制 MCP 伺服器並抑制 claude.ai 連接器 [Claude Code 自行擷取](https://code.claude.com/docs/zh-TW/mcp#how-connectors-reach-claude-code)
- **預設** ：`false`，因此部署的 `managed-mcp.json` 會抑制 Claude Code 自行擷取的 claude.ai 連接器

managed-settings.json

```
{
  "allowAllClaudeAiMcps": true
}

```

[`allowedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#allowedmcpservers) 和 [`deniedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#deniedmcpservers) 仍然適用於此金鑰載入的連接器。傳遞到[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)的連接器，其主機帶有 `managed-mcp.json`（例如自託管執行器），會保持被抑制。請參閱[允許 claude.ai 連接器與受管集合並存](https://code.claude.com/docs/zh-TW/managed-mcp#allow-claude-ai-connectors-alongside-the-managed-set)。

### `allowedMcpServers`

允許清單列出人員可以新增的 MCP 伺服器。Claude Code 會阻止任何不符合條目的伺服器，無論在何處定義，包括外掛程式伺服器、使用 `--mcp-config` 傳遞的伺服器，以及來自 claude.ai 的伺服器。 內建伺服器（例如 Chrome 中的 Claude、Claude Code 在執行中的 [VS Code](https://code.claude.com/docs/zh-TW/vs-code#the-built-in-ide-mcp-server) 或 [JetBrains](https://code.claude.com/docs/zh-TW/jetbrains#the-built-in-ide-mcp-server) IDE 中連接的 `ide` 伺服器，以及 CLI 本身設定的伺服器）不受允許清單限制，拒絕清單仍然適用於它們。同處理程序 `type: "sdk"` 伺服器不受兩個清單的限制；[啟動工作階段的應用程式](https://code.claude.com/docs/zh-TW/mcp#how-connectors-reach-claude-code)會註冊它們。 您的組織提供的伺服器也不受允許清單限制，拒絕清單仍然適用於它們。豁免涵蓋每個 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 條目，以及任何 [`managed-mcp.json`](https://code.claude.com/docs/zh-TW/managed-mcp#exclusive-control-with-managed-mcp-json) 條目，其值不使用 `${VAR}` 擴展。請參閱[如何評估伺服器](https://code.claude.com/docs/zh-TW/managed-mcp#how-a-server-is-evaluated)以了解完整的檢查順序。在 v2.1.259 之前，來自 `managed-mcp.json` 的伺服器也必須符合。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。來自每個檔案的條目會合併為一個允許清單，除非設定了 [`allowManagedMcpServersOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedmcpserversonly)。在受管設定中部署它以強制執行。
- **類型** ：物件陣列，每個物件恰好有一個金鑰：`serverName`（字串，限制為字母、數字、連字號和底線）；`serverCommand`（命令及其引數的陣列，完全相符）；或 `serverUrl`（具有 `*` 萬用字元的 URL 模式）
- **預設** ：未設定，因此允許每個伺服器；空陣列會阻止使用者新增的每個伺服器

此範例僅允許列出的 `npx` 命令啟動的 stdio 伺服器： settings.json

```
{
  "allowedMcpServers": [
    { "serverCommand": ["npx", "-y", "@modelcontextprotocol/server-filesystem"] }
  ]
}

```

[`deniedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#deniedmcpservers) 條目優先，因此同時在兩個清單上的伺服器會被阻止。一旦清單包含任何 `serverCommand` 條目，stdio 伺服器必須符合 `serverCommand` 條目，一旦它包含任何 `serverUrl` 條目，遠端伺服器必須符合 `serverUrl` 條目：`serverName` 相符不再允許該類伺服器。請參閱[使用允許清單和拒絕清單進行基於原則的控制](https://code.claude.com/docs/zh-TW/managed-mcp#policy-based-control-with-allowlists-and-denylists)。

### `allowManagedMcpServersOnly`

使受管允許清單成為唯一適用的清單。Claude Code 然後僅從受管設定讀取 [`allowedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#allowedmcpservers)，並忽略使用者、專案和本機設定中的允許清單；[`deniedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#deniedmcpservers) 仍然從每個設定範圍合併，因此使用者仍然可以為自己阻止伺服器。管理員設定它，以便使用者自己的設定無法擴大受管允許清單允許的內容。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 僅從受管設定讀取 `allowedMcpServers`，並忽略使用者、專案和本機設定中的允許清單
  - `false`：來自每個設定範圍的允許清單合併
- **預設** ：`false`，因此來自每個設定範圍的允許清單合併

此範例將允許清單鎖定到受管設定，並僅允許名為 `github` 的伺服器： managed-settings.json

```
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverName": "github" }
  ]
}

```

使用者仍然可以新增自己的 MCP 伺服器；只有符合受管允許清單的伺服器才會載入。請參閱[將允許清單限制為僅受管設定](https://code.claude.com/docs/zh-TW/managed-mcp#restrict-the-allowlist-to-managed-settings-only)。

### `deniedMcpServers`

阻止特定的 MCP 伺服器。Claude Code 拒絕載入符合的伺服器，無論在何處定義，包括外掛程式伺服器、使用 `--mcp-config` 傳遞的伺服器、來自 `managed-mcp.json` 的伺服器、來自 [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers) 的伺服器，以及 [它自行擷取](https://code.claude.com/docs/zh-TW/mcp#how-connectors-reach-claude-code)的 claude.ai 連接器。同處理程序 `type: "sdk"` 伺服器不受限制；啟動工作階段的應用程式會註冊它們。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。來自每個檔案的條目會合併為一個拒絕清單，[`allowManagedMcpServersOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedmcpserversonly) 不會改變這一點。在受管設定中部署它以強制執行。
- **類型** ：物件陣列，每個物件恰好有一個金鑰：`serverName`（字串，因此 claude.ai 連接器的顯示名稱（例如 `"claude.ai Slack"`）有效）；`serverCommand`（命令及其引數的陣列，完全相符）；或 `serverUrl`（具有 `*` 萬用字元的 URL 模式）
- **預設** ：未設定，因此不會阻止任何伺服器；空陣列也不會阻止任何內容

settings.json

```
{
  "deniedMcpServers": [
    { "serverName": "filesystem" }
  ]
}

```

拒絕清單優先於 [`allowedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#allowedmcpservers)，因此同時在兩個清單上的伺服器會被阻止。請參閱[使用允許清單和拒絕清單進行基於原則的控制](https://code.claude.com/docs/zh-TW/managed-mcp#policy-based-control-with-allowlists-and-denylists)。

### `disableClaudeAiConnectors`

關閉 [claude.ai MCP 連接器](https://code.claude.com/docs/zh-TW/mcp#use-mcp-servers-from-claude-ai) [Claude Code 自行擷取](https://code.claude.com/docs/zh-TW/mcp#how-connectors-reach-claude-code)，因此它既不擷取也不連接它們。任何設定檔案中的 `true` 都適用：簽入的專案 `.claude/settings.json` 可以選擇退出存放庫中的這些連接器，但專案層級的 `false` 無法覆蓋使用者或受管層級的 `true`。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 既不擷取也不連接這些連接器
  - `false`：與未設定相同；Claude Code 會擷取您的連接器，除非另一個設定檔案或 `ENABLE_CLAUDEAI_MCP_SERVERS` 將其關閉
- **預設** ：`false`，因此 Claude Code 會擷取您的連接器
- **每個工作階段的覆蓋** ：[`ENABLE_CLAUDEAI_MCP_SERVERS`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `false` 會在一個工作階段中關閉連接器；無論兩者中哪一個將其關閉，另一個都無法將其重新開啟

settings.json

```
{
  "disableClaudeAiConnectors": true
}

```

您使用 `--mcp-config` 明確傳遞的伺服器不受影響。若要阻止個別連接器而不是全部，請使用 [`deniedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#deniedmcpservers)。請參閱[禁用 claude.ai 連接器](https://code.claude.com/docs/zh-TW/mcp#disable-claude-ai-connectors)。

### `disabledMcpjsonServers`

拒絕專案 `.mcp.json` 檔案中定義的特定伺服器，以便 Claude Code 永遠不會連接它們或要求您批准它們。任何設定檔案中的拒絕都適用，包括簽入存放庫的專案 `.claude/settings.json`。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串陣列，伺服器名稱如 `.mcp.json` 中所示
- **預設** ：未設定

settings.json

```
{
  "disabledMcpjsonServers": ["filesystem"]
}

```

當您在批准對話方塊中拒絕伺服器時，Claude Code 會將此金鑰寫入 `.claude/settings.local.json`。`claude mcp get <name>` 將被拒絕的伺服器顯示為 `✘ Rejected (see disabledMcpjsonServers in settings)`。拒絕優先於 [`enabledMcpjsonServers`](https://code.claude.com/docs/zh-TW/settings-reference#enabledmcpjsonservers) 和 [`enableAllProjectMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#enableallprojectmcpservers)。

### `enableAllProjectMcpServers`

批准專案 `.mcp.json` 檔案中定義的每個 MCP 伺服器，無需提示。當您在批准對話方塊中選擇批准所有伺服器時，Claude Code 會將此金鑰寫入 `.claude/settings.local.json`。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在您尚未接受信任對話方塊的資料夾中，Claude Code 從使用者設定、受管設定和 `--settings` 中遵守它，並在共用專案檔案中忽略它，無論在工作階段中還是對於 `claude mcp list` 和 `claude mcp get`；[專案伺服器批准和工作區信任](https://code.claude.com/docs/zh-TW/mcp#project-server-approvals-and-workspace-trust)說明何時未追蹤的 `.claude/settings.local.json` 也計算在內。
- **類型** ：布林值
  - `true`：Claude Code 批准專案 `.mcp.json` 檔案中定義的每個 MCP 伺服器，無需提示
  - `false`：Claude Code 要求您批准每個伺服器。在受信任的資料夾中，較高優先順序檔案中的 `false` 會覆蓋較低優先順序檔案中的 `true`；在您尚未信任的資料夾中，任何受尊重檔案中的 `true` 就足夠了
- **預設** ：未設定，因此 Claude Code 要求您批准每個伺服器

settings.json

```
{
  "enableAllProjectMcpServers": true
}

```

[`disabledMcpjsonServers`](https://code.claude.com/docs/zh-TW/settings-reference#disabledmcpjsonservers) 條目仍然會拒絕伺服器。

### `enabledMcpjsonServers`

批准專案 `.mcp.json` 檔案中定義的特定伺服器，以便 Claude Code 連接它們而無需詢問。當您在批准對話方塊中批准伺服器時，Claude Code 會將此金鑰寫入 `.claude/settings.local.json`。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在您尚未接受信任對話方塊的資料夾中，Claude Code 從使用者設定、受管設定和 `--settings` 中遵守它，並在共用專案檔案中忽略它，無論在工作階段中還是對於 `claude mcp list` 和 `claude mcp get`；[專案伺服器批准和工作區信任](https://code.claude.com/docs/zh-TW/mcp#project-server-approvals-and-workspace-trust)說明何時未追蹤的 `.claude/settings.local.json` 也計算在內。
- **類型** ：字串陣列，伺服器名稱如 `.mcp.json` 中所示
- **預設** ：未設定

此範例批准專案 `.mcp.json` 中的 `memory` 和 `github` 伺服器： settings.json

```
{
  "enabledMcpjsonServers": ["memory", "github"]
}

```

[`disabledMcpjsonServers`](https://code.claude.com/docs/zh-TW/settings-reference#disabledmcpjsonservers) 條目仍然會拒絕伺服器。

### `managedMcpServers`

從受管設定為每個使用者提供遠端 MCP 伺服器。使用者保留他們自己新增的伺服器，無法編輯或移除您提供的伺服器。需要 Claude Code v2.1.259 或更新版本。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 在使用者、專案和本機設定中以警告方式捨棄該金鑰，並且不在第三方部署上的 Claude Desktop 應用程式的 Code 標籤中或在應用程式的 Cowork 工作階段中讀取它，其中 Claude Desktop 會供應並鎖定這些工作階段的 MCP 伺服器本身。
- **類型** ：按伺服器名稱鍵入的物件。每個條目都具有 `http` 或 `sse` 伺服器的 `.mcp.json` 形狀：必需的 `https://` `url`，以及可選的 `headers`、`oauth` 和其他 HTTP 和 SSE 選項。Claude Code 捨棄驗證失敗的條目，[條目可以包含的內容](https://code.claude.com/docs/zh-TW/managed-mcp#what-an-entry-can-contain)列出了條件
- **預設** ：未設定，因此受管設定不提供伺服器

此範例提供一個名為 `search` 的 HTTP 伺服器： managed-settings.json

```
{
  "managedMcpServers": {
    "search": {
      "type": "http",
      "url": "https://search.example.com/mcp"
    }
  }
}

```

有關優先順序、提供的伺服器如何與 `managed-mcp.json` 和允許和拒絕清單結合，以及使用者看到的內容，請參閱[通過受管設定提供伺服器](https://code.claude.com/docs/zh-TW/managed-mcp#provide-servers-through-managed-settings)。

## 代理程式、工作階段和 worktrees

設定預設代理程式、控制隊友和跨工作階段訊息，以及設定 worktrees。請參閱 [Subagents](https://code.claude.com/docs/zh-TW/sub-agents) 和 [Worktrees](https://code.claude.com/docs/zh-TW/worktrees)。

### `agent`

將主執行緒作為具名 [subagent](https://code.claude.com/docs/zh-TW/sub-agents#invoke-subagents-explicitly) 執行，以便 Claude Code 將該 subagent 的系統提示、工具限制和模型套用到您的工作階段。相同的金鑰會為您從 `claude agents` 分派的工作階段設定預設代理程式。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : string，內建或自訂代理程式的名稱
- **Default** : 未設定，因此主執行緒以 Claude Code 的預設代理程式執行
- **Per-session overrides** : `--agent` 對一個工作階段優先於此金鑰

settings.json

```
{
  "agent": "code-reviewer"
}

```

外掛程式自己的 `settings.json` 也可以提供此金鑰；請參閱 [Ship default settings with your plugin](https://code.claude.com/docs/zh-TW/plugins#ship-default-settings-with-your-plugin)。

### `crossSessionInbound`

選擇此工作階段如何處理 [來自您其他 Claude Code 工作階段的訊息](https://code.claude.com/docs/zh-TW/cross-session-messaging#control-inbound-messages)。當沒有值適用時，Claude Code 會根據兩個工作階段的權限模式類別逐個訊息決定。需要 Claude Code v2.1.224 或更新版本。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。專案或本機值僅在其比受管設定、`--settings` 旗標或使用者設定提供的值更嚴格時才適用。
- **Type** : string，其中之一：
  - `"accept"`: Claude Code 將訊息傳遞給 Claude
  - `"hold"`: Claude Code 顯示訊息的通知而不傳遞它
  - `"refuse"`: Claude Code 丟棄訊息
- **Default** : 未設定，因此 Claude Code 逐個訊息決定

settings.json

```
{
  "crossSessionInbound": "hold"
}

```

Claude Code 首先讀取受管設定，然後是 `--settings` 旗標，然後是使用者設定，並套用找到的第一個值。`refuse` 比 `hold` 更嚴格，`hold` 比 `accept` 更嚴格。當沒有受信任的來源設定值時，專案或本機 `hold` 或 `refuse` 仍然適用，取代逐個訊息的預設值。在具有跨工作階段訊息的工作階段中，此金鑰在 `/config` 中顯示為 **Messages from your other sessions** ，它將其寫入使用者設定；該列需要 Claude Code v2.1.232 或更新版本，當 `--settings` 旗標或受管設定設定金鑰時，Claude Code 會隱藏它。 Claude Code [warns](https://code.claude.com/docs/zh-TW/errors#crosssessioninbound-must-be-one-of-accept-hold-refuse) 當您設定它無法識別的值時。當該值存在於使用者、專案、本機或 `--settings` 檔案中時，Claude Code 會保留入站訊息，即使優先的來源設定 `accept` 也是如此。另一個來源設定的 `refuse` 仍然適用。修復或移除該值以清除保留。 當無法識別的值在 [managed settings](https://code.claude.com/docs/zh-TW/managed-settings) 中時，Claude Code 改為將其視為 `refuse`，直到管理員修復它。在 v2.1.248 之前，Claude Code 會忽略無法識別的值而不發出警告。

### `disableAgentView`

關閉 [background agents and agent view](https://code.claude.com/docs/zh-TW/agent-view)：`claude agents`、`--bg`、`/background` 和隨需主管。在 [managed settings](https://code.claude.com/docs/zh-TW/managed-settings) 中設定它以對組織強制執行。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : Boolean
  - `true`: Claude Code 關閉 `claude agents`、`--bg`、`/background` 和隨需主管
  - `false`: agent view 可用
- **Default** : 未設定，因此 agent view 可用
- **Per-session overrides** : [`CLAUDE_CODE_DISABLE_AGENT_VIEW`](https://code.claude.com/docs/zh-TW/env-vars) 對一個工作階段關閉 agent view；無論哪一個關閉它，另一個都無法將其重新開啟

settings.json

```
{
  "disableAgentView": true
}

```

### `isolatePeerMachines`

在 Claude 的 `SendMessage` 到達此機器之外的您的工作階段之前，需要您的明確批准；請參閱 [Require approval for cross-machine messages](https://code.claude.com/docs/zh-TW/cross-session-messaging#require-approval-for-cross-machine-messages)。即使在 [`bypassPermissions` mode](https://code.claude.com/docs/zh-TW/permission-modes#skip-all-checks-with-bypasspermissions-mode) 中，批准提示也會出現。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。來自任何範圍的 `true` 都適用，因此簽入的專案檔案可以開啟要求但不能關閉。
- **Type** : Boolean
  - `true`: Claude Code 在 Claude 的 `SendMessage` 到達此機器之外的您的工作階段之前要求您的批准
  - `false`: 跨機器訊息不提示
- **Default** : 未設定，因此跨機器訊息不提示

settings.json

```
{
  "isolatePeerMachines": true
}

```

跨機器 `SendMessage` 批准需要 Claude Code v2.1.224 或更新版本。

### `processWrapper`

在 macOS 和 Linux 上，在 [Claude Code 啟動的背景程序](https://code.claude.com/docs/zh-TW/corporate-launcher#what-the-launcher-covers) 前面放置公司啟動器命令。Claude Code 使用其自己的命令列附加執行啟動器，因此啟動器必須執行到 Claude Code；請參閱 [Run Claude Code behind a corporate launcher](https://code.claude.com/docs/zh-TW/corporate-launcher) 以了解啟動器合約。需要 Claude Code v2.1.210 或更新版本。

- **Scope** : [`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : string，啟動器命令作為 argv 前綴，例如具有選擇性引數的絕對路徑
- **Default** : 未設定，因此背景程序啟動時不包裝
- **Per-session overrides** : [`CLAUDE_CODE_PROCESS_WRAPPER`](https://code.claude.com/docs/zh-TW/env-vars) 對一個工作階段優先於此金鑰

settings.json

```
{
  "processWrapper": "/opt/corp/launcher --profile claude"
}

```

Claude Code 在 Windows 上忽略啟動器並啟動每個程序時不包裝。需要 Claude Code v2.1.210 或更新版本。

### `teammateMode`

選擇 Claude Code 顯示 [agent team](https://code.claude.com/docs/zh-TW/agent-teams) 隊友的位置：在您的主終端窗格內，或在您的終端支援時在分割窗格中。請參閱 [Choose a display mode](https://code.claude.com/docs/zh-TW/agent-teams#choose-a-display-mode)。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 也會讀取舊版本在 `~/.claude.json` 中留下的值。
- **Type** : string，其中之一：
  - `"in-process"`: 隊友在您的主終端窗格內執行
  - `"auto"`: 當您在 tmux 內執行時分割窗格，或在 iTerm2 內執行且 `it2` 在您的 `PATH` 上或安裝了 tmux；否則為 in-process
  - `"tmux"`: 使用 tmux 或 iTerm2 分割窗格，從您的終端偵測
  - `"iterm2"`: iTerm2 原生分割窗格透過 `it2` CLI，在 Claude Code v2.1.186 或更新版本中
- **Default** : `"in-process"`
- **Per-session overrides** : `--teammate-mode` 對一個工作階段優先於此金鑰

settings.json

```
{
  "teammateMode": "auto"
}

```

`iterm2` 值需要 Claude Code v2.1.186 或更新版本。

### `worktree`

設定 Claude Code 如何為 `--worktree`、`EnterWorktree` 工具和隔離的 subagents 和背景工作階段建立和管理 [git worktrees](https://code.claude.com/docs/zh-TW/worktrees)。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : object with `baseRef`, `symlinkDirectories`, `sparsePaths`, and `bgIsolation`
- **Default** : 未設定

此範例從您目前的 `HEAD` 分支新的 worktrees，並將 `node_modules` 符號連結到每一個： settings.json

```
{
  "worktree": {
    "baseRef": "head",
    "symlinkDirectories": ["node_modules"]
  }
}

```

若要將 gitignored 檔案（如 `.env`）複製到新的 worktrees，請改為在專案根目錄中新增 [`.worktreeinclude` 檔案](https://code.claude.com/docs/zh-TW/worktrees#copy-gitignored-files-into-worktrees)，而不是設定。

### `worktree.baseRef`

選擇新的 worktrees 從哪個 ref 分支。`"fresh"` 從 `origin/<default-branch>` 分支以獲得與遠端相符的乾淨樹；`"head"` 從您目前的本機 `HEAD` 分支，因此未推送的提交和功能分支狀態存在於 worktree 中。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : string，其中之一：
  - `"fresh"`: 新的 worktrees 從 `origin/<default-branch>` 分支
  - `"head"`: 新的 worktrees 從您目前的本機 `HEAD` 分支，包括未推送的提交
- **Default** : `"fresh"`

settings.json

```
{
  "worktree": {
    "baseRef": "head"
  }
}

```

在連結的 worktree 內，`"head"` 解析為該 worktree 的 `HEAD`，而不是主簽出的。

### `worktree.symlinkDirectories`

將目錄從主儲存庫符號連結到每個 worktree，以便您不會在磁碟上複製大型目錄。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : array of strings，相對於儲存庫根目錄的目錄路徑
- **Default** : 未設定，因此 Claude Code 不符號連結任何目錄

此範例將 `node_modules` 和 `.cache` 從主儲存庫符號連結到每個新的 worktree： settings.json

```
{
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache"]
  }
}

```

### `worktree.sparsePaths`

透過 git sparse-checkout 在每個 worktree 中僅簽出列出的目錄。Claude Code 僅將這些目錄加上根層級檔案寫入磁碟，在大型 monorepos 中速度更快；請參閱 [Check out only the directories you need](https://code.claude.com/docs/zh-TW/large-codebases#check-out-only-the-directories-you-need)。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : array of strings，相對於儲存庫根目錄的目錄路徑
- **Default** : 未設定，因此每個 worktree 簽出整個樹

此範例在每個 worktree 中僅簽出 `packages/my-app` 和 `shared/utils`，加上根層級檔案： settings.json

```
{
  "worktree": {
    "sparsePaths": ["packages/my-app", "shared/utils"]
  }
}

```

當稀疏 worktree 存在時，git 在儲存庫的共用 `.git/config` 中啟用 `extensions.worktreeConfig`。

### `worktree.bgIsolation`

選擇 [background sessions](https://code.claude.com/docs/zh-TW/agent-view#how-file-edits-are-isolated) 如何隔離其檔案編輯。使用 `"worktree"`，Claude Code 會阻止主簽出中的 `Edit` 和 `Write`，直到工作階段呼叫 `EnterWorktree`；使用 `"none"`，背景工作會直接編輯工作副本。對於 git worktrees 不實用的儲存庫，設定 `"none"`。

- **Scope** : [`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **Type** : string，其中之一：
  - `"worktree"`: Claude Code 會阻止主簽出中的 `Edit` 和 `Write`，直到工作階段呼叫 `EnterWorktree`
  - `"none"`: 背景工作會直接編輯工作副本
- **Default** : `"worktree"`

settings.json

```
{
  "worktree": {
    "bgIsolation": "none"
  }
}

```

在 git 儲存庫外，失敗的 [`WorktreeCreate` hook](https://code.claude.com/docs/zh-TW/worktrees#non-git-version-control) 會釋放區塊，以便工作階段可以就地編輯工作目錄；該釋放需要 Claude Code v2.1.203 或更新版本。

## 遠端、桌面和通知

設定遠端控制、雲端環境、桌面應用程式，以及 Claude Code 在需要您時傳送的通知。請參閱[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)。

### `agentPushNotifEnabled`

允許 Claude 在決定值得傳送時，向您的手機傳送推播通知，例如當長時間任務完成時。Claude Code 會將此選擇同步到您的帳戶，推播會在[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)連線時送達。在 `/config` 中顯示為**Claude 決定時推播** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 也會讀取舊版本在 `~/.claude.json` 中留下的值。
- **類型** ：布林值
  - `true`：Claude 可以在決定值得傳送時，向您的手機傳送推播通知
  - `false`：Claude 不傳送這些通知
- **預設值** ：`false`

settings.json

```
{
  "agentPushNotifEnabled": true
}

```

請參閱[行動推播通知](https://code.claude.com/docs/zh-TW/remote-control#mobile-push-notifications)。

### `awaySummaryEnabled`

當您在離開終端機幾分鐘後返回時，顯示一行工作階段摘要。將其設定為 `false`，或在 `/config` 中關閉**工作階段摘要** ，以停止摘要。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：當您在離開幾分鐘後返回時，您會看到一行工作階段摘要
  - `false`：Claude Code 不顯示摘要
- **預設值** ：未設定，因此摘要已開啟
- **每個工作階段的覆寫** ：[`CLAUDE_CODE_ENABLE_AWAY_SUMMARY`](https://code.claude.com/docs/zh-TW/env-vars) 在一個工作階段中優先於此金鑰，無論哪個方向

settings.json

```
{
  "awaySummaryEnabled": false
}

```

Claude Code 在非互動模式中永遠不會顯示摘要。

### `disableArtifact`

已棄用，已由 [`enableArtifact`](https://code.claude.com/docs/zh-TW/settings-reference#enableartifact) 取代。Claude Code 仍然將 `disableArtifact: true` 視為等同於 `enableArtifact: false`，並忽略 `disableArtifact: false`。 改用 [`enableArtifact`](https://code.claude.com/docs/zh-TW/settings-reference#enableartifact) 來關閉 [Artifact](https://code.claude.com/docs/zh-TW/artifacts) 工具，該工具將工作階段輸出發佈為 claude.ai 上的私人網頁。當您在 `/config` 中關閉 **Artifacts** 列時，Claude Code 會將 `enableArtifact` 寫入您的使用者設定，並清除此金鑰。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 為該檔案適用的每個工作階段關閉 Artifact 工具，且沒有其他檔案將其重新開啟。在 v2.1.242 之前，優先順序較高的檔案可能會覆寫較低檔案的 `true`，而不是該金鑰作為鎖定
  - `false`：忽略；若要保持工具開啟，請移除該金鑰
- **預設值** ：未設定，因此工具遵循您帳戶的[可用性](https://code.claude.com/docs/zh-TW/artifacts#availability)
- **每個工作階段的覆寫** ：[`CLAUDE_CODE_DISABLE_ARTIFACT`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 會為一個工作階段關閉工具

settings.json

```
{
  "disableArtifact": true
}

```

[停用 artifacts](https://code.claude.com/docs/zh-TW/artifacts#disable-artifacts) 列出關閉工具的每一種方式。

### `disableDeepLinkRegistration`

停止 Claude Code 向作業系統註冊 `claude-cli://` 協定處理程式，否則在您傳送互動工作階段的第一個提示後會執行此操作。[深層連結](https://code.claude.com/docs/zh-TW/deep-links)讓外部工具使用預先填入的提示開啟 Claude Code 工作階段。在協定處理程式註冊受限或單獨管理的環境中設定此項。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串 `"disable"`
- **預設值** ：未設定，因此 Claude Code 會註冊處理程式

settings.json

```
{
  "disableDeepLinkRegistration": "disable"
}

```

### `disableDesktopLocalSessions`

在[桌面應用程式](https://code.claude.com/docs/zh-TW/desktop#local-sessions-on-managed-devices)中關閉在裝置上執行的 Code 工作階段，適用於開發人員應該透過 SSH 在遠端機器上工作的部署。在 Code 標籤中，**本機** 環境保留在環境下拉式選單中，但呈灰色且無法選擇，工具提示顯示您的組織已將其關閉；在 Windows 上，WSL 項目以相同方式呈灰色，儘管 WSL 工作階段是否在受管理裝置上執行[由另外管理](https://code.claude.com/docs/zh-TW/admin-setup#wsl-sessions-in-claude-code-desktop)。新工作階段預設為第一個[SSH 連線](https://code.claude.com/docs/zh-TW/desktop#ssh-sessions)（如果已設定），應用程式拒絕在裝置上啟動或繼續工作階段，包括回到同一機器的 SSH 連線。到其他主機的 SSH 工作階段和雲端工作階段不受影響。桌面應用程式讀取此金鑰；終端機 CLI 忽略它。需要 Claude Desktop v1.37937.0 或更新版本。

- **範圍** ：[`受管理`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值；只有 JSON 布林值 `true` 才會生效
  - `true`：桌面應用程式不提供裝置上的 Code 工作階段；現有本機工作階段保留在列表中但無法繼續
  - `false`：本機工作階段保持可用
- **預設值** ：未設定，因此本機工作階段可用

managed-settings.json

```
{
  "disableDesktopLocalSessions": true
}

```

桌面應用程式忽略任何其他值，非布林值的值（例如字串 `"true"` 或 `1`）也會記錄警告。將其與 [`sshConfigs`](https://code.claude.com/docs/zh-TW/settings-reference#sshconfigs) 配對，以便使用者登陸工作連線，並與 [`sshHostAllowlist`](https://code.claude.com/docs/zh-TW/settings-reference#sshhostallowlist) 配對以限制他們可以到達的主機。請參閱[受管理裝置上的本機工作階段](https://code.claude.com/docs/zh-TW/desktop#local-sessions-on-managed-devices)。 Claude Desktop 為 Code 工作階段提供源自您桌面設定的原則，例如第三方部署中的出口允許清單、檔案系統沙箱和 MCP 限制。每當存在[管理員來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)時，Claude Code 會忽略這些父設定：伺服器管理的設定、MDM 或作業系統層級原則，或受管理設定檔。在之前沒有任何設定的裝置上透過其中一個部署此金鑰（如在第三方部署中），因此會停止套用桌面衍生的原則。[讓嵌入主機新增原則](https://code.claude.com/docs/zh-TW/managed-settings#let-an-embedding-host-add-policy)涵蓋何時父設定仍可合併；這適用於您以這種方式部署的任何金鑰，不僅限於此金鑰。

### `disableRemoteControl`

關閉[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)：Claude Code 隨後拒絕 `claude remote-control`、`--remote-control` 旗標、自動啟動和工作階段內切換，並報告您的組織原則已停用它。將其放在[受管理設定](https://code.claude.com/docs/zh-TW/managed-settings)中以進行每個裝置的 MDM 強制執行。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 拒絕 `claude remote-control`、`--remote-control` 旗標、自動啟動和工作階段內切換
  - `false`：遠端控制保持可用
- **預設值** ：`false`

settings.json

```
{
  "disableRemoteControl": true
}

```

### `enableArtifact`

關閉 [Artifact](https://code.claude.com/docs/zh-TW/artifacts) 工具，該工具將工作階段輸出發佈為 claude.ai 上的私人網頁。當您在 `/config` 中關閉 **Artifacts** 列時，Claude Code 會將此金鑰寫入您的使用者設定，因此您通常不會手動編輯它。需要 Claude Code v2.1.196 或更新版本。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。每個檔案都可以關閉工具，但沒有任何檔案可以將其重新開啟。
- **類型** ：布林值
  - `false`：Claude Code 為該檔案適用的每個工作階段關閉 Artifact 工具
  - `true`：與保留金鑰未設定相同，因為它永遠不會覆寫來自另一個檔案的 `false`、[`CLAUDE_CODE_DISABLE_ARTIFACT`](https://code.claude.com/docs/zh-TW/env-vars) 或您的組織[管理員設定](https://code.claude.com/docs/zh-TW/artifacts#manage-artifacts-for-your-organization)
- **預設值** ：未設定，因此工具遵循您帳戶的[可用性](https://code.claude.com/docs/zh-TW/artifacts#availability)

settings.json

```
{
  "enableArtifact": false
}

```

當您自己的使用者設定以外的來源保持工具關閉時，Claude Code 會在 `/config` 中隱藏 **Artifacts** 列，因為在那裡開啟它不會改變任何事情。[停用 artifacts](https://code.claude.com/docs/zh-TW/artifacts#disable-artifacts) 列出關閉工具的每一種方式。在 v2.1.242 之前，Claude Code 在專案和本機設定中忽略此金鑰，[優先順序堆疊](https://code.claude.com/docs/zh-TW/settings#settings-precedence)中較高的檔案可能會在較低檔案的關閉上將工具重新開啟。

### `inputNeededNotifEnabled`

當權限提示或問題等待您的輸入時，在您的手機上獲得推播通知。Claude Code 只在[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)連線時傳送這些通知。在 `/config` 中顯示為**需要操作時推播** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 也會讀取舊版本在 `~/.claude.json` 中留下的值。
- **類型** ：布林值
  - `true`：當權限提示或問題等待時，您會在手機上獲得推播通知，而遠端控制已連線
  - `false`：Claude Code 不傳送此類通知
- **預設值** ：`false`

settings.json

```
{
  "inputNeededNotifEnabled": true
}

```

請參閱[行動推播通知](https://code.claude.com/docs/zh-TW/remote-control#mobile-push-notifications)。

### `preferredNotifChannel`

選擇 Claude Code 在任務完成或權限提示等待時如何通知您。在 `/config` 中顯示為**本機通知** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 也會讀取舊版本在 `~/.claude.json` 中留下的值。
- **類型** ：字串，其中之一：
  - `"auto"`：Claude Code 在 iTerm2、Ghostty 和 Kitty 中傳送桌面通知，在 Terminal.app 中只有在其可聽鈴聲關閉時才響鈴，在其他地方不執行任何操作
  - `"terminal_bell"`：Claude Code 在任何終端機中響鈴字元
  - `"iterm2"`：Claude Code 傳送 iTerm2 桌面通知
  - `"iterm2_with_bell"`：Claude Code 傳送 iTerm2 桌面通知並響鈴
  - `"kitty"`：Claude Code 傳送 Kitty 桌面通知
  - `"ghostty"`：Claude Code 傳送 Ghostty 桌面通知
  - `"notifications_disabled"`：Claude Code 不傳送通知
- **預設值** ：`"auto"`

settings.json

```
{
  "preferredNotifChannel": "terminal_bell"
}

```

使用 `"auto"` 時，Claude Code 在 iTerm2、Ghostty 和 Kitty 中傳送桌面通知。在 Terminal.app 中，只有當您已關閉 Terminal 的可聽鈴聲時，它才會響鈴字元，在其他終端機中不執行任何操作。設定 `"terminal_bell"` 以在任何終端機中響鈴字元。請參閱[獲得終端機鈴聲或通知](https://code.claude.com/docs/zh-TW/terminal-config#get-a-terminal-bell-or-notification)。

### `remote.defaultEnvironmentId`

為您從 CLI 建立的雲端工作階段（例如使用 `claude --cloud`）選擇預設[雲端環境](https://code.claude.com/docs/zh-TW/cloud-environments)。當您使用 [`/remote-env`](https://code.claude.com/docs/zh-TW/cloud-environments#select-an-environment-from-the-cli) 選擇環境時，Claude Code 會將此金鑰寫入您的使用者設定。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。對於自託管環境 ID，僅限使用者或受管理設定，或 `--settings` 旗標。
- **類型** ：字串，環境 ID，例如 `env_...` 或 `ccpool_...`
- **預設值** ：未設定，因此當您的清單中有 Anthropic 託管環境時 Claude Code 會使用它，否則使用清單中不是[遠端控制橋接環境](https://code.claude.com/docs/zh-TW/cloud-environments#the-default-environment)的第一個環境，或當每個環境都是橋接環境時使用第一個環境
- **每個工作階段的覆寫** ：`--environment` 優先於此金鑰，用於它建立的一個雲端工作階段

settings.json

```
{
  "remote": {
    "defaultEnvironmentId": "env_0123abcd"
  }
}

```

Anthropic 託管環境 ID（以 `env_` 開頭）遵循標準設定優先順序，因此儲存庫的專案設定中的值會覆寫您的使用者層級選擇。[自託管環境](https://code.claude.com/docs/zh-TW/self-hosted-environments) ID（以 `ccpool_` 開頭）只能從使用者設定、受管理設定和 `--settings` 旗標中獲得；Claude Code 忽略儲存庫的專案或本機設定中的一個，`/remote-env` 顯示它忽略了哪個值，因此簽入的檔案無法將工作階段引導到您未選擇的自託管環境。

### `remoteControlAtStartup`

當每個互動工作階段啟動時自動連線[遠端控制](https://code.claude.com/docs/zh-TW/remote-control)，而不是等待 `/remote-control`。將其設定為 `true` 以開啟自動連線，`false` 以關閉。在 `/config` 中顯示為**為所有工作階段啟用遠端控制** 。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 也會讀取舊版本在 `~/.claude.json` 中留下的值。
- **類型** ：布林值
  - `true`：Claude Code 在每個互動工作階段啟動時自動連線遠端控制
  - `false`：Claude Code 等待 `/remote-control`
- **預設值** ：未設定，因此自動連線遵循您的組織管理員預設值（如果已設定），否則遵循 Claude Code 的目前預設值
- **每個工作階段的覆寫** ：`--remote-control` 即使此金鑰為 `false` 也會為一個工作階段開啟遠端控制，沒有旗標會為一個工作階段關閉它

settings.json

```
{
  "remoteControlAtStartup": true
}

```

Claude Code 忽略來自專案或本機設定的 `true`，因此儲存庫可以為其簽出關閉自動連線，但無法開啟。如需完整的每個範圍行為，請參閱[為所有工作階段啟用遠端控制](https://code.claude.com/docs/zh-TW/remote-control#enable-remote-control-for-all-sessions)和[較嚴格值適用的安全金鑰](https://code.claude.com/docs/zh-TW/settings#security-keys-where-the-stricter-value-applies)。

### `sshConfigs`

將 SSH 連線新增到[桌面](https://code.claude.com/docs/zh-TW/desktop#pre-configure-ssh-connections-for-your-team)環境下拉式選單。管理員使用它來向團隊分發共用連線。您在受管理設定中定義的連線顯示為受管理，因此使用者可以選擇它們，但無法在應用程式中編輯或刪除它們。

- **範圍** ：[`使用者或受管理`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。桌面應用程式讀取此金鑰。
- **類型** ：物件陣列，每個物件具有必需的 `id`、`name` 和 `sshHost` 以及選用的 `sshPort` 和 `sshIdentityFile`
- **預設值** ：未設定

此範例新增一個名為 `Dev VM` 的連線，連線到 `user@dev.example.com`： settings.json

```
{
  "sshConfigs": [
    {
      "id": "dev-vm",
      "name": "Dev VM",
      "sshHost": "user@dev.example.com"
    }
  ]
}

```

### `sshHostAllowlist`

限制[桌面 SSH 工作階段](https://code.claude.com/docs/zh-TW/desktop#restrict-which-ssh-hosts-users-can-connect-to)可以連線到的主機。只有桌面應用程式讀取此金鑰；CLI 不讀取。模式不區分大小寫：`*` 符合任何主機，`*.example.com` 符合 `example.com` 和每個子網域，其他任何內容都是針對 `~/.ssh/config` 解析後的主機名稱的精確符合。空陣列會關閉 SSH 工作階段。

- **範圍** ：[`受管理`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：主機名稱模式陣列
- **預設值** ：未設定，因此允許任何主機

此範例允許 `devboxes.example.com` 及其子網域，加上精確主機 `bastion.example.com`： managed-settings.json

```
{
  "sshHostAllowlist": ["*.devboxes.example.com", "bastion.example.com"]
}

```

## 驗證和提供者

透過協助指令碼提供認證，對於組織，強制執行登入方法或組織。請參閱[驗證](https://code.claude.com/docs/zh-TW/authentication)。

### `apiKeyHelper`

執行您自己的命令來產生 Claude Code 隨著模型請求傳送的認證。Claude Code 透過系統 shell 執行命令，在 macOS 和 Linux 上為 `/bin/sh`，在 Windows 上為 `cmd`，並將其輸出作為 `X-Api-Key` 和 `Authorization: Bearer` 標頭傳送。將其用於動態或輪換認證，例如從保管庫擷取的短期權杖。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，shell 命令列
- **預設** ：未設定，所以 Claude Code 不執行協助程式

settings.json

```
{
  "apiKeyHelper": "/bin/generate_temp_api_key.sh"
}

```

Claude Code 快取該值，並在以下情況下重新執行命令：

- 在快取生命週期之後，預設為五分鐘，或您使用 [`CLAUDE_CODE_API_KEY_HELPER_TTL_MS`](https://code.claude.com/docs/zh-TW/env-vars) 設定的間隔。
- 當對 Anthropic API 的請求（直接或透過 [LLM gateway](https://code.claude.com/docs/zh-TW/llm-gateway)）失敗並出現 `401` 或 `403` 時。
- 在傳送對 Anthropic API 的請求之前（直接或透過 LLM gateway），當快取的輸出是協助程式產生後過期的 JWT 時。需要 Claude Code v2.1.246 或更新版本。

最後兩種情況僅在協助程式的輸出是 Claude Code 傳送的認證且未設定 `ANTHROPIC_AUTH_TOKEN` 時適用。 在互動式工作階段中，當命令來自專案或本機設定時，Claude Code 在您接受工作區信任提示之前不會執行它。請參閱[認證管理](https://code.claude.com/docs/zh-TW/authentication#credential-management)。

### `awsAuthRefresh`

執行您自己的命令（例如 `aws sso login`），以在 Claude Code 對 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock) 的認證停止運作時重新整理 `.aws` 目錄中的認證。Claude Code 首先根據 STS 檢查目前認證，僅在該檢查失敗時執行命令，然後讀取重新整理的 `.aws` 目錄。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，shell 命令列
- **預設** ：未設定，所以 Claude Code 不為您重新整理 AWS 認證

settings.json

```
{
  "awsAuthRefresh": "aws sso login --profile myprofile"
}

```

當您的重新整理流程寫入 `.aws` 時使用此金鑰；當它改為列印認證時使用 [`awsCredentialExport`](https://code.claude.com/docs/zh-TW/settings-reference#awscredentialexport)。請參閱[進階認證設定](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration)。

### `awsCredentialExport`

執行您自己的命令，該命令將 AWS 認證列印為 JSON，以便 Claude Code 可以使用不存在於 `.aws` 目錄中的認證呼叫 [Amazon Bedrock](https://code.claude.com/docs/zh-TW/amazon-bedrock)。Claude Code 接受 `aws sts` 輸出形狀和平面 `aws configure export-credentials` 形狀，並將認證範圍限定於其自己的 Bedrock 用戶端，因此 Claude Code 執行的 shell 命令仍然會看到您的環境認證。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，shell 命令列
- **預設** ：未設定，所以 Claude Code 使用環境 AWS 認證鏈

settings.json

```
{
  "awsCredentialExport": "/bin/generate_aws_grant.sh"
}

```

與 [`awsAuthRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#awsauthrefresh) 不同，Claude Code 在設定此命令時總是執行它，而不先檢查環境認證。請參閱[進階認證設定](https://code.claude.com/docs/zh-TW/amazon-bedrock#advanced-credential-configuration)。

### `forceLoginMethod`

限制人員可以使用哪種帳戶登入。設定 `"claudeai"` 以僅允許 claude.ai 帳戶，設定 `"console"` 以僅允許 Claude Console 帳戶，或設定 `"gateway"` 以將人員傳送到 [cloud gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 而不是第一方登入。管理員在受管設定中設定它，並將其與 [`forceLoginOrgUUID`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginorguuid) 配對，以將開發人員的 claude.ai 登入保持在一個組織內。如果您在任何設定檔中將其設定為 `"claudeai"` 或 `"console"`，Claude Code 也會停止在該檔案適用的工作階段中提供[無金鑰 Console 登入](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 僅從機器上的受管來源（`managed-settings.json`、macOS plist 或 Windows HKLM 登錄，或原則協助程式）接受 `"gateway"`。它在使用者、專案、本機、HKCU 和伺服器受管設定中將 `"gateway"` 視為未設定，與 [`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl) 的規則相同。
- **類型** ：字串，其中之一：
  - `"claudeai"`：僅 claude.ai 帳戶可以登入
  - `"console"`：僅 Claude Console 帳戶可以登入
  - `"gateway"`：Claude Code 將人員傳送到 cloud gateway 而不是第一方登入
- **預設** ：未設定，所以人員選擇登入方法

settings.json

```
{
  "forceLoginMethod": "claudeai"
}

```

每個第一方登入路徑都適用限制，包括 [VS Code 擴充功能](https://code.claude.com/docs/zh-TW/vs-code)、Agent SDK、`claude setup-token` 和 `/install-github-app`，除了終端機的互動式登入畫面（透過 `/login` 或首次執行上線到達），它預先選擇方法而不強制執行。在 v2.1.212 之前，僅終端機登入適用它。請參閱[限制登入到您的組織](https://code.claude.com/docs/zh-TW/authentication#restrict-login-to-your-organization)，了解每個登入路徑、環境認證和第三方提供者的處理方式。 當機器上的受管來源設定 `"gateway"` 時，Claude Code 不使用剩餘登入、API 金鑰或 `apiKeyHelper` 認證。請參閱[管理員原則需要 Cloud gateway 登入](https://code.claude.com/docs/zh-TW/errors#administrator-policy-requires-a-cloud-gateway-sign-in)，了解每個原則產生的訊息。如果您透過 `CLAUDE_CODE_USE_BEDROCK` 或類似環境變數選擇 cloud 提供者，工作階段不需要 gateway 登入。在 v2.1.261 之前，Claude Code 在這些機器上使用剩餘登入。

### `forceLoginGatewayUrl`

設定 `/login` Cloud gateway 畫面連線到的 gateway URL，以便人員可以到達您的 [cloud gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway) 而無需輸入其位址。該畫面沒有 URL 欄位：設定此金鑰時，它會顯示您的 gateway URL，並在人員按下 Enter 時連線；不設定時，它會告訴他們聯絡其 IT 管理員。 此金鑰或 `forceLoginMethod: "gateway"` 中的任一個都會使機器僅限 gateway，因此 `/login` 在 Cloud gateway 畫面上開啟，沒有登入方法選擇器。請參閱[管理員原則需要 Cloud gateway 登入](https://code.claude.com/docs/zh-TW/errors#administrator-policy-requires-a-cloud-gateway-sign-in)，了解剩餘第一方登入或 API 金鑰會發生什麼。設定兩個金鑰，以便畫面連線而不是顯示錯誤。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。僅從機器上的來源讀取：`managed-settings.json`、macOS plist 或 Windows HKLM 登錄，或原則協助程式。Claude Code 在 HKCU 和伺服器受管設定中忽略它。
- **類型** ：字串，包括配置的完整 URL
- **預設** ：未設定，所以 Cloud gateway 畫面顯示錯誤，告訴人員聯絡其 IT 管理員

managed-settings.json

```
{
  "forceLoginGatewayUrl": "https://claude-gateway.example.com"
}

```

如果值不是有效的 URL，登入畫面會報告它，受管設定檔的其餘部分仍然適用。請參閱[設定 gateway URL](https://code.claude.com/docs/zh-TW/claude-apps-gateway#set-the-gateway-url)。

### `forceLoginOrgUUID`

從受管來源，要求 claude.ai 帳戶登入屬於一個 Anthropic 組織（以單一 UUID 給定）或屬於多個組織（以陣列給定）。從任何設定檔，Claude Code 也使用單一 UUID 在 claude.ai 或 Claude Console 登入期間預先選擇該組織，並為陣列預先選擇任何內容。如果您在任何設定檔中設定金鑰，Claude Code 也會停止在該檔案適用的工作階段中提供[無金鑰 Console 登入](https://code.claude.com/docs/zh-TW/authentication#sign-in-without-an-api-key)，並改為建立 API 金鑰。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。僅受管來源強制執行限制；任何其他設定檔中的單一 UUID 在登入期間預先選擇組織而不限制它。
- **類型** ：字串，一個 UUID，或字串陣列，多個 UUID
- **預設** ：未設定，所以任何組織都可以登入

此範例接受來自兩個組織之一的登入，而不預先選擇一個： managed-settings.json

```
{
  "forceLoginOrgUUID": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"]
}

```

如果受管來源設定空陣列或 Claude Code 無法解析的值，Claude Code 會使用誤設定訊息阻止每個登入。 請參閱[限制登入到您的組織](https://code.claude.com/docs/zh-TW/authentication#restrict-login-to-your-organization)，了解 Claude Code 如何處理 Claude Console 登入、其他登入路徑和環境認證。

### `gatewayInternalNetworks`

宣告您的組織編號其內部網路的公開 IPv4 區塊，以便 `/login` 在那裡接受 [cloud gateway](https://code.claude.com/docs/zh-TW/claude-apps-gateway)。需要 Claude Code v2.1.268 或更新版本。 沒有此金鑰，`/login` 連線到私人位址上的任何 gateway，別無其他。有了它，`/login` 也接受列出區塊內的 gateway，僅透過直接連線。該連線上機器自己的位址也必須在同一區塊內。

- **範圍** ：[`受管`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。僅從機器上的來源讀取：`managed-settings.json`、macOS plist 或 Windows HKLM 登錄，或原則協助程式。Claude Code 在 HKCU 和伺服器受管設定中忽略它。
- **類型** ：字串陣列，最多四個 IPv4 CIDR 區塊，每個 `/8` 到 `/32`，彼此不重疊，且都不與私人空間重疊。
- **預設** ：未設定，所以 `/login` 僅接受私人位址上的 gateway

managed-settings.json

```
{
  "gatewayInternalNetworks": ["203.0.113.0/24"]
}

```

將範例中的文件範圍替換為您自己的區塊。Claude Code 拒絕文件範圍、VPN 和 NAT64 用戶端在本機使用的範圍，以及沒有網路編號的保留空間，例如多播。 如果項目無效，或值不是字串清單，`/login` 會命名問題，並拒絕機器上的每個新 gateway 登入，直到您修正值。現有登入繼續運作。請參閱[允許 gateway 在您擁有的公開位址空間上](https://code.claude.com/docs/zh-TW/claude-apps-gateway#allow-a-gateway-on-public-address-space-you-own)，了解完整規則以及開發人員看到的內容。

### `gcpAuthRefresh`

執行您自己的命令，以在 Claude Code 發現 Google Cloud Application Default Credentials 已過期或無法載入時重新整理它們，以便 [Google Cloud 的 Agent Platform](https://code.claude.com/docs/zh-TW/google-vertex-ai) 請求在您不手動重新驗證的情況下繼續運作。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，shell 命令列
- **預設** ：未設定，所以 Claude Code 的認證錯誤會告訴您自己執行 `gcloud auth application-default login`

settings.json

```
{
  "gcpAuthRefresh": "gcloud auth application-default login"
}

```

請參閱[進階認證設定](https://code.claude.com/docs/zh-TW/google-vertex-ai#advanced-credential-configuration)。

### `otelHeadersHelper`

執行您自己的命令來產生 Claude Code 隨著 OpenTelemetry 匯出傳送的標頭，適用於權杖輪換的後端。Claude Code 在啟動時執行它，之後定期執行，並期望在 stdout 上看到字串標頭值的 JSON 物件。

- **範圍** ：[`任何檔案`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，可執行路徑或 shell 命令列
- **預設** ：未設定，所以 Claude Code 不新增協助程式產生的標頭

settings.json

```
{
  "otelHeadersHelper": "/bin/generate_otel_headers.sh"
}

```

使用 [`CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS`](https://code.claude.com/docs/zh-TW/env-vars) 設定重新整理間隔。請參閱[動態標頭](https://code.claude.com/docs/zh-TW/monitoring-usage#dynamic-headers)，了解指令碼需求以及 Claude Code 報告失敗協助程式的位置。

## 更新和版本控制

選擇更新頻道，並針對組織，固定人員可以執行的版本。請參閱[更新 Claude Code](https://code.claude.com/docs/zh-TW/setup#update-claude-code)。

### `autoUpdatesChannel`

選擇[發行頻道](https://code.claude.com/docs/zh-TW/setup#configure-release-channel)背景自動更新和 `claude update` 遵循的頻道。設定 `"stable"` 以取得通常約一週舊的版本，並跳過具有重大迴歸的發行版本，或設定 `"latest"` 以取得最新發行版本。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在受管設定中設定以在整個組織中強制執行一個頻道。
- **類型** ：字串，其中之一：
  - `"latest"`：更新遵循最新發行版本
  - `"stable"`：更新遵循通常約一週舊的版本，並跳過具有重大迴歸的發行版本
- **預設** ：未設定，因此 Claude Code 遵循 `"latest"`

settings.json

```
{
  "autoUpdatesChannel": "stable"
}

```

當您在 `/config` 中的**自動更新頻道** 下選擇時，Claude Code 會將 `"stable"` 寫入您的使用者設定，並在您在該處切換回最新版本時移除該金鑰。`claude install stable` 和 `claude install latest` 也會儲存您命名的頻道。在 `/config` 中從 `"latest"` 切換到 `"stable"` 時，會詢問是否允許降級或保持在目前版本；保持設定會設定 [`minimumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#minimumversion)。Homebrew 安裝會忽略此金鑰：`claude-code` cask 追蹤穩定版本，`claude-code@latest` 追蹤最新版本，而 `claude update` 遵循 `brew upgrade`。若要完全關閉自動更新，請在 `env` 中設定 [`DISABLE_AUTOUPDATER`](https://code.claude.com/docs/zh-TW/setup#disable-auto-updates)。

### `minimumVersion`

防止背景自動更新和 `claude update` 安裝低於此版本的任何版本，因此移至 `"stable"` 頻道不會從較新的 `"latest"` 組建中降級您。當您在 `/config` 中選擇在切換頻道時保持在目前版本時，Claude Code 會為您寫入此金鑰，並在您切換回 `"latest"` 時清除它。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在受管設定中設定以固定組織範圍的最小值，使用者和專案設定無法降低。
- **類型** ：字串，版本號碼，例如 `"2.1.100"`
- **預設** ：未設定，因此更新可以安裝頻道提供的任何版本

此範例遵循穩定頻道，並拒絕安裝低於 2.1.100 的任何版本： settings.json

```
{
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.100"
}

```

此金鑰僅限制更新。若要讓 Claude Code 拒絕在版本以下啟動，請改用 [`requiredMinimumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#requiredminimumversion)。請參閱[固定最小版本](https://code.claude.com/docs/zh-TW/setup#pin-a-minimum-version)。

### `requiredMaximumVersion`

設定您的組織允許啟動的最新 Claude Code 版本。當執行中的版本較新時，Claude Code 在啟動時退出，並告訴使用者透過您組織的核准方法安裝核准的版本；`claude install <version>` 也可能有效。需要 Claude Code v2.1.163 或更新版本。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 在其他地方忽略金鑰時不會發出警告。
- **類型** ：字串，版本號碼，例如 `"2.1.150"`；不是有效版本的值會被忽略
- **預設** ：未設定，因此不適用上限

managed-settings.json

```
{
  "requiredMaximumVersion": "2.1.150"
}

```

背景自動更新和 `claude update` 會跳過上限以上的版本，因此範圍內的安裝會保持在範圍內。`claude update`、`claude install` 和 `claude doctor` 在上限以上繼續運作，以便使用者可以復原。將其與 [`requiredMinimumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#requiredminimumversion) 配對以強制執行範圍。

### `requiredMinimumVersion`

設定您的組織允許啟動的最舊 Claude Code 版本。當執行中的版本較舊時，Claude Code 在啟動時退出，並告訴使用者透過您組織的核准方法進行更新。檢查僅在啟動時執行，因此已執行的工作階段會繼續。需要 Claude Code v2.1.163 或更新版本。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 在其他地方忽略金鑰時不會發出警告。
- **類型** ：字串，版本號碼，例如 `"2.1.150"`；不是有效版本的值會被忽略
- **預設** ：未設定，因此不適用下限

managed-settings.json

```
{
  "requiredMinimumVersion": "2.1.150"
}

```

`claude update`、`claude install` 和 `claude doctor` 在下限以下繼續運作，以便使用者可以復原。與僅防止降級的 [`minimumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#minimumversion) 不同，此金鑰會阻止啟動。將其與 [`requiredMaximumVersion`](https://code.claude.com/docs/zh-TW/settings-reference#requiredmaximumversion) 配對以強制執行範圍。

## 工具

在 [Claude Code 桌面應用程式](https://code.claude.com/docs/zh-TW/desktop)中關閉特定工具。終端 CLI 會忽略這些金鑰。如需了解工具本身，請參閱 [Claude 可用的工具](https://code.claude.com/docs/zh-TW/tools-reference)。

### `browserExternalPageTools`

防止 Claude 在桌面應用程式的 [Browser 窗格](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)中使用其工具來讀取或作用於外部頁面。您組織中的人員仍然可以自行開啟外部網站，本機開發伺服器預覽會繼續與 Claude 的工具搭配運作。桌面應用程式會讀取此金鑰；終端 CLI 會忽略它。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，`"disabled"`；桌面應用程式也接受 `"disable"`，在任一情況下
- **預設** ：未設定，因此 Claude 的工具可在外部頁面上運作

managed-settings.json

```
{
  "browserExternalPageTools": "disabled"
}

```

任何其他值都會讓 Claude 的工具保持開啟，非空字串若不是兩個接受的值之一，會記錄警告。若要同時為人員和 Claude 封鎖外部網站，請改為設定 [`disableBrowserExternalNavigation`](https://code.claude.com/docs/zh-TW/settings-reference#disablebrowserexternalnavigation)。請參閱 [限制您組織的外部瀏覽](https://code.claude.com/docs/zh-TW/desktop#restrict-external-browsing-for-your-organization)。

### `disableBrowserExternalNavigation`

在桌面應用程式的 [Browser 窗格](https://code.claude.com/docs/zh-TW/desktop#browse-external-sites)中為人員和 Claude 關閉外部瀏覽。Localhost 開發伺服器預覽會繼續運作。桌面應用程式會讀取此金鑰；終端 CLI 會忽略它。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值；只有 JSON 布林值 `true` 會生效
  - `true`：桌面應用程式為人員和 Claude 關閉 Browser 窗格中的外部瀏覽；localhost 預覽會繼續運作
  - `false`：外部瀏覽保持開啟
- **預設** ：未設定，因此外部瀏覽是開啟的

managed-settings.json

```
{
  "disableBrowserExternalNavigation": true
}

```

桌面應用程式會忽略任何其他值，非布林值（例如字串 `"true"` 或 `1`）也會記錄警告。若要保持外部瀏覽開啟但讓 Claude 的工具在外部頁面上關閉，請改為設定 [`browserExternalPageTools`](https://code.claude.com/docs/zh-TW/settings-reference#browserexternalpagetools)。請參閱 [限制您組織的外部瀏覽](https://code.claude.com/docs/zh-TW/desktop#restrict-external-browsing-for-your-organization)。

### `disableMobileSimulatorTools`

封鎖 Claude 對桌面應用程式 [iOS Simulator 窗格](https://code.claude.com/docs/zh-TW/desktop-ios-simulator#turn-off-simulator-access)的工具。人員保留對窗格的手動使用；只有 Claude 的存取被移除，沒有人可以從應用程式內部將其重新開啟。桌面應用程式會讀取此金鑰；終端 CLI 會忽略它。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值；只有 JSON 布林值 `true` 會生效
  - `true`：桌面應用程式封鎖 Claude 對 iOS Simulator 窗格的工具
  - `false`：Claude 的模擬器工具遵循桌面應用程式中每個人的設定切換
- **預設** ：未設定，因此 Claude 的模擬器工具遵循桌面應用程式中每個人的設定切換

managed-settings.json

```
{
  "disableMobileSimulatorTools": true
}

```

桌面應用程式會忽略任何其他值，非布林值（例如字串 `"true"` 或 `1`）也會記錄警告。

## 隱私和遙測

控制 Claude Code 保留工作階段資料的時間長度以及它傳送的內容。關閉使用量指標和錯誤報告的開關是環境變數，而不是設定鍵：在 [`env`](https://code.claude.com/docs/zh-TW/settings-reference#env) 鍵或殼層中設定 `DISABLE_TELEMETRY`、`DISABLE_ERROR_REPORTING` 或 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`。[遙測服務](https://code.claude.com/docs/zh-TW/data-usage#telemetry-services)說明每個開關會停止什麼。兩個例外可從設定檔關閉：下面的 [`feedbackDrafts`](https://code.claude.com/docs/zh-TW/settings-reference#feedbackdrafts) 用於 Claude 起草的回饋，以及下面的 [`feedbackSurveyRate`](https://code.claude.com/docs/zh-TW/settings-reference#feedbacksurveyrate) 用於工作階段調查。

### `cleanupPeriodDays`

設定 Claude Code 在刪除之前保留[工作階段文字記錄和其他應用程式資料](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)的天數。Claude Code 在工作階段開始後作為背景掃描執行刪除，只要它能安全地確定保留期間。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：天數，整數，最小值 `1`
- **預設值** ：`30`

settings.json

```
{
  "cleanupPeriodDays": 20
}

```

設定 `0` 會驗證失敗，因此請選擇較大的值，例如 `3650` 以進行長期保留。若要停止 Claude Code 完全寫入文字記錄，請參閱[純文字儲存](https://code.claude.com/docs/zh-TW/claude-directory#plaintext-storage)。

### `desktopSessionCleanupPeriodDays`

為您在 Claude Desktop 或 Cowork 中啟動或最近繼續的工作階段文字記錄設定天數年齡限制。沒有此鍵，Claude Code [會以任何年齡保留這些文字記錄](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)。Claude Code 在每個文字記錄的年齡超過此限制和 [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays) 時刪除它，因此當 `cleanupPeriodDays` 處於其預設值 30 時，值 `7` 仍會保留它們 30 天。當受管設定設定 `cleanupPeriodDays` 時，該期間改為適用，此鍵被忽略。需要 Claude Code v2.1.248 或更新版本。

- **範圍** ：[`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 也會從您使用 `--settings` 傳遞的檔案中讀取該鍵，並在專案和本機設定中忽略它。
- **類型** ：天數，整數，最小值 `0`
- **預設值** ：`0`，不設定年齡限制

settings.json

```
{
  "desktopSessionCleanupPeriodDays": 90
}

```

### `feedbackDrafts`

控制 [Claude 起草的回饋](https://code.claude.com/docs/zh-TW/tools-reference#sendfeedback-tool-behavior)：Claude 是否可以將回饋草稿排隊供您審查，以及 Claude Code 在 Claude 排隊時是否顯示卡片。

- **範圍** ：[`User or managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，`"notify"`、`"quiet"` 或 `"off"` 之一
  - `"notify"`：當 Claude 排隊草稿時，Claude Code 在提示上方顯示卡片，預設情況下[一個工作階段中最多三張卡片](https://code.claude.com/docs/zh-TW/tools-reference#what-you-see-when-claude-drafts)
  - `"quiet"`：Claude 起草而不顯示卡片。您在提示頁尾看到排隊草稿的計數，並在 `/feedback` 中審查它們
  - `"off"`：Claude Code 移除 SendFeedback 工具，因此 Claude 無法排隊草稿
- **預設值** ：`"notify"`
- **每個工作階段覆蓋** ：[`CLAUDE_CODE_SEND_FEEDBACK`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `0` 會關閉一個工作階段的功能

settings.json

```
{
  "feedbackDrafts": "quiet"
}

```

在 `/config` 中顯示為 **Claude-drafted feedback** ，它將此鍵寫入您的使用者設定。您只在 Claude [可以起草回饋](https://code.claude.com/docs/zh-TW/tools-reference#sessions-without-claude-drafted-feedback)的工作階段中看到 `/config` 列；設定 `"off"` 不會隱藏它，因此您可以從同一列重新開啟功能。受管設定中的值優先於您的使用者設定，因此當管理員設定此鍵時，該列顯示受管值，更改它無效。Claude Code 在專案和本機設定中忽略此鍵。

### `feedbackSurveyRate`

設定[工作階段品質調查](https://code.claude.com/docs/zh-TW/data-usage#session-quality-surveys)在工作階段符合條件時出現的機率。設定 `0` 以防止調查出現。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：`0` 到 `1` 之間的數字
- **預設值** ：未設定，因此 Claude Code 使用 Anthropic 遠端設定的速率，或在 Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上的內建速率 `0.005`，它們不接收遠端設定
- **每個工作階段覆蓋** ：[`CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 會關閉一個工作階段的調查，無論此鍵設定的速率如何

settings.json

```
{
  "feedbackSurveyRate": 0.05
}

```

相同的速率適用於 VS Code 擴充功能中的調查。

### `skipWebFetchPreflight`

跳過 [WebFetch 網域安全檢查](https://code.claude.com/docs/zh-TW/data-usage#webfetch-domain-safety-check)，它在擷取之前將每個請求的主機名稱傳送到 `api.anthropic.com`。在阻止流量到 Anthropic 的環境中設定 `true`，例如 Amazon Bedrock、Google Cloud 的 Agent Platform 或具有限制性出口的 Microsoft Foundry 部署。

- **範圍** ：[`Any file`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 跳過 WebFetch 網域安全檢查
  - `false`：檢查在工作階段中首次擷取每個主機名稱之前執行，以及對於其先前檢查被阻止或失敗的主機名稱再次執行
- **預設值** ：未設定，因此檢查在工作階段中首次擷取每個主機名稱之前執行

settings.json

```
{
  "skipWebFetchPreflight": true
}

```

跳過檢查後，WebFetch 嘗試任何 URL 而不查詢封鎖清單，因此如果您需要限制 Claude 可以到達的網域，請將其與 [`WebFetch` 權限規則](https://code.claude.com/docs/zh-TW/permissions#webfetch)配對。

## 企業和受管設定

組織用來計算、重新整理和合併受管設定的金鑰。請參閱[設定受管設定](https://code.claude.com/docs/zh-TW/admin-setup)。

### `disableSideloadFlags`

在啟動時拒絕 `--plugin-dir`、`--plugin-url`、`--agents` 和 `--mcp-config` CLI 旗標，使用者否則可能會傳遞這些旗標來繞過 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces) 進行單次執行。Claude Code 會以錯誤結束，並命名被拒絕的旗標，並對在桌面應用程式中內部啟動 CLI 的表面套用相同檢查，目前在[Cowork](https://code.claude.com/docs/zh-TW/desktop) 本機工作階段中。在[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)中，Claude Code 會捨棄伺服器透過 `--mcp-config` 傳遞的 MCP 伺服器，除了同處理序 `type: "sdk"` 項目外，並啟動工作階段。需要 Claude Code v2.1.193 或更新版本。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：Claude Code 在啟動時拒絕 `--plugin-dir`、`--plugin-url`、`--agents` 和 `--mcp-config`，並以錯誤結束並命名它們，除了在雲端工作階段中它會捨棄伺服器透過 `--mcp-config` 傳遞的 MCP 伺服器，除了同處理序 `type: "sdk"` 項目外，並啟動工作階段
  - `false`：Claude Code 接受這些旗標
- **預設** ：`false`

managed-settings.json

```
{
  "disableSideloadFlags": true
}

```

Claude Code 仍然接受其伺服器全部為同處理序 `type: "sdk"` 項目的 `--mcp-config`，因此 Agent SDK 和 VS Code 擴充功能保持運作。使用者仍然可以使用 `claude mcp add` 或 `.mcp.json` 檔案新增伺服器；如需個別伺服器控制，也請設定 [`allowedMcpServers`](https://code.claude.com/docs/zh-TW/managed-mcp)。需要 Claude Code v2.1.193 或更新版本。 在雲端工作階段中，Claude Code 也會忽略伺服器傳遞的中途工作階段 MCP 更新，這是雲端工作階段設定和 SDK `setMcpServers()` 呼叫背後的路徑，這些呼叫到達這些工作階段。同處理序 `type: "sdk"` 項目在那裡也保持豁免。在 v2.1.239 之前，伺服器傳遞的 `--mcp-config` 會阻止雲端工作階段啟動。

### `forceRemoteSettingsRefresh`

阻止 CLI 啟動，直到 Claude Code 已重新整理[伺服器受管設定](https://code.claude.com/docs/zh-TW/server-managed-settings)。如果擷取失敗，Claude Code 會結束而不是繼續使用快取或無設定。當您的環境無法接受即使是短暫的時間視窗（在該時間視窗中工作階段執行時沒有其受管原則）時，請設定它。 當金鑰未設定時，Claude Code 不會在擷取時阻止啟動，但當開發人員在啟動時登入時，它會等待最多五秒鐘以進行擷取。雲端閘道工作階段始終會等待，如果無法到達閘道則會結束。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 會接受來自任何管理員控制的受管來源的 `true`，即使它不是最高優先順序的來源。
- **類型** ：布林值
  - `true`：Claude Code 會阻止啟動，直到它已重新整理伺服器受管設定，如果擷取失敗則會結束
  - `false`：Claude Code 不會在擷取時阻止啟動，但在登入啟動時會等待最多五秒鐘以進行擷取
- **預設** ：`false`

managed-settings.json

```
{
  "forceRemoteSettingsRefresh": true
}

```

在 MDM 設定檔或受管設定檔案中設定它，以在第一個伺服器承載到達之前強制執行失敗關閉啟動。Claude Code 只在擷取伺服器受管設定的工作階段中套用檢查，因此[不擷取它們](https://code.claude.com/docs/zh-TW/server-managed-settings#platform-availability)的工作階段會在不等待的情況下啟動。`claude auth` 子命令是豁免的，因此使用者可以在過期認證是擷取失敗原因時重新驗證。請參閱[強制執行失敗關閉啟動](https://code.claude.com/docs/zh-TW/server-managed-settings#enforce-fail-closed-startup)。

### `managedSourcesBehavior`

選擇 Claude Code 是否只套用您的組織傳遞的最高優先順序[受管來源](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)，或合併它傳遞的每個管理員來源。根據預設，Claude Code 會採用攜帶[原則金鑰](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)的最高優先順序來源，並忽略其餘的。原則金鑰是除了此金鑰和 `wslInheritsWindowsSettings` 之外的任何設定金鑰。因此，一旦伺服器受管設定或 MDM 原則傳遞原則金鑰，`managed-settings.json` 檔案只會貢獻 [Claude Code 從每個管理員來源讀取的金鑰](https://code.claude.com/docs/zh-TW/managed-settings#keys-read-from-every-admin-source)。使用 `"merge"`，您傳遞的每個管理員來源都會將其金鑰貢獻給一個合併的原則。需要 Claude Code v2.1.242 或更新版本。 只在您[排名](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)在最高優先順序下方的每個來源都在管理員的控制下時設定 `"merge"`，因為 Claude Code 然後會從較低的來源（例如 `permissions.allow` 規則）新增項目到原則。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 從攜帶此金鑰或原則金鑰的最高優先順序來源讀取此金鑰，並忽略排名較低的每個來源中的此金鑰，因此較低的來源無法選擇自己合併到上方的來源。Windows HKCU 登錄和[來自嵌入主機的父設定](https://code.claude.com/docs/zh-TW/managed-settings#let-an-embedding-host-add-policy)都不參與合併。
- **類型** ：字串，其中之一：
  - `"first-wins"`：攜帶原則金鑰的最高優先順序來源提供原則，較低的來源只貢獻 [Claude Code 從每個管理員來源讀取的金鑰](https://code.claude.com/docs/zh-TW/managed-settings#keys-read-from-every-admin-source)
  - `"merge"`：您傳遞的每個管理員來源都會貢獻其金鑰，按以下規則合併
- **預設** ：`"first-wins"`

在您部署的最高優先順序來源中傳遞金鑰。永遠不會收到伺服器受管設定的機器也需要在其 MDM 設定檔中有金鑰，因為 Claude Code 從攜帶它或原則金鑰的最高優先順序來源讀取金鑰。`managed-settings.json` 檔案是排名最低的管理員來源，因此在那裡設定的 `"merge"` 沒有下方的來源可以合併。在伺服器受管設定中，金鑰看起來像這樣：

```
{
  "managedSourcesBehavior": "merge"
}

```

在 `"merge"` 下，Claude Code 按其種類合併每個金鑰。此表格為每種金鑰提供規則。限制允許清單、整體取值和最高來源專用列命名它們涵蓋的每個金鑰，其他列提供範例：

| 金鑰種類                                                                                                                                     | Claude Code 如何合併它                                                                                                                                   | 金鑰                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 清單                                                                                                                                         | 合併來自每個來源的項目                                                                                                                                   | [`permissions.allow`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-allow)、[`sandbox.network.allowedDomains`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-network-alloweddomains) 和其他清單金鑰                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 鎖定                                                                                                                                         | 套用任何來源設定的最嚴格值。當沒有來源設定嚴格值時，只從最高來源套用較寬鬆的值                                                                           | [`allowManagedPermissionRulesOnly`](https://code.claude.com/docs/zh-TW/settings-reference#allowmanagedpermissionrulesonly)、[`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-disablebypasspermissionsmode) 和其他布林值或列舉鎖定                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 限制允許清單                                                                                                                                 | 從設定它的最高來源整體取值清單，不從較低的來源新增項目。當最高來源未設定時，從下一個較低的來源整體取值                                                   | [`availableModels`](https://code.claude.com/docs/zh-TW/settings-reference#availablemodels)、[`allowedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#allowedmcpservers)、[`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#strictknownmarketplaces)、[`allowedChannelPlugins`](https://code.claude.com/docs/zh-TW/settings-reference#allowedchannelplugins) 和 [`fallbackModel`](https://code.claude.com/docs/zh-TW/settings-reference#fallbackmodel) 鏈                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 整體取值                                                                                                                                     | 從設定它的最高來源整體取值，不合併來自較低來源的項目或欄位。當最高來源未設定時，從下一個較低的來源整體取值                                               | [`sandbox.credentials.awsPairs`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-credentials-awspairs)、[`sandbox.ripgrep`](https://code.claude.com/docs/zh-TW/settings-reference#sandbox-ripgrep)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 提供的 MCP 伺服器                                                                                                                            | 合併來自每個來源的伺服器名稱。當兩個來源設定相同名稱時，套用較高來源的整個項目                                                                           | [`managedMcpServers`](https://code.claude.com/docs/zh-TW/settings-reference#managedmcpservers)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 只從最高優先順序來源讀取                                                                                                                     | 只從攜帶原則金鑰的最高優先順序來源讀取金鑰，因此即使最高來源未設定任何值，較低來源的值也會被忽略                                                         | [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper)、[`awsAuthRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#awsauthrefresh)、[`awsCredentialExport`](https://code.claude.com/docs/zh-TW/settings-reference#awscredentialexport)、[`gcpAuthRefresh`](https://code.claude.com/docs/zh-TW/settings-reference#gcpauthrefresh)、[`otelHeadersHelper`](https://code.claude.com/docs/zh-TW/settings-reference#otelheadershelper)、`proxyAuthHelper`、[`forceLoginOrgUUID`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginorguuid)、[`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 的 `"claudeai"` 和 `"console"` 值、[`parentSettingsBehavior`](https://code.claude.com/docs/zh-TW/settings-reference#parentsettingsbehavior)、[`modelPicker`](https://code.claude.com/docs/zh-TW/settings-reference#modelpicker)、[`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper)、[`permissions.defaultMode`](https://code.claude.com/docs/zh-TW/settings-reference#permissions-defaultmode) |
| `env`                                                                                                                                        | [在管理員來源間按變數合併](https://code.claude.com/docs/zh-TW/managed-settings#keys-read-from-every-admin-source)，在 `"first-wins"` 和 `"merge"` 下都是 | [`env`](https://code.claude.com/docs/zh-TW/settings-reference#env)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 所有其他金鑰                                                                                                                                 | 從設定它的最高來源取值                                                                                                                                   | [`cleanupPeriodDays`](https://code.claude.com/docs/zh-TW/settings-reference#cleanupperioddays)、[`model`](https://code.claude.com/docs/zh-TW/settings-reference#model)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 整體取值 `sandbox.credentials.awsPairs` 和 `sandbox.ripgrep` 需要 Claude Code v2.1.257 或更新版本。 這些金鑰中的幾個新增了表格未顯示的條件： |                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

- **[`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper)**：Claude Code 只在攜帶原則金鑰的最高來源是 MDM 原則或受管設定檔案時接受它，因此在伺服器受管設定下它不適用。
- **[`modelOverrides`](https://code.claude.com/docs/zh-TW/settings-reference#modeloverrides)**：與`availableModels` 配對。Claude Code 從設定它的最高來源取值 `modelOverrides`，除非較高的來源設定 `availableModels` 而不設定 `modelOverrides`。在這種情況下，它會忽略來自每個來源的 `modelOverrides`。
- **[`forceLoginGatewayUrl`](https://code.claude.com/docs/zh-TW/settings-reference#forcelogingatewayurl)、[`gatewayInternalNetworks`](https://code.claude.com/docs/zh-TW/settings-reference#gatewayinternalnetworks) 和 [`forceLoginMethod`](https://code.claude.com/docs/zh-TW/settings-reference#forceloginmethod) 的 `"gateway"` 值**：Claude Code 永遠不會從伺服器受管設定讀取它們，因此那裡的值既不適用也不隱藏在 MDM 原則或受管設定檔案中設定的值。在機器上的管理員來源中，只有攜帶原則金鑰的最高排名來源提供它們，無論伺服器受管設定是否也存在。

若要確認機器上合併了哪些來源，請執行 `/status` 並[讀取 `Setting sources` 行](https://code.claude.com/docs/zh-TW/managed-settings#read-the-source-in-/status)。

### `parentSettingsBehavior`

選擇當管理員部署的受管層級也存在時，Claude Code 是否套用由嵌入主機程序（例如 Agent SDK 或 IDE 擴充功能）提供的受管設定。使用 `"first-wins"`，Claude Code 會捨棄主機提供的設定；使用 `"merge"`，它會透過限制專用篩選器在管理員層級下套用它們。當主機需要將其自己的限制傳遞給它啟動的工作階段時，請設定 `"merge"`，例如 Claude Desktop 傳遞閘道的出口允許清單。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。Claude Code 從最高優先順序管理員控制的受管來源讀取它。
- **類型** ：字串，其中之一：
  - `"first-wins"`：當管理員部署的受管層級存在時，Claude Code 會捨棄主機提供的設定
  - `"merge"`：Claude Code 透過限制專用篩選器在管理員層級下套用主機提供的設定
- **預設** ：`"first-wins"`

managed-settings.json

```
{
  "parentSettingsBehavior": "merge"
}

```

當不存在管理員部署的受管層級時，此金鑰無效：主機的設定然後套用為唯一的受管層級，仍然篩選為限制值。如需篩選器的限制以及受管來源如何互動，請參閱[來自嵌入主機的父設定](https://code.claude.com/docs/zh-TW/managed-settings#parent-settings-from-embedding-hosts)和[限制父設定](https://code.claude.com/docs/zh-TW/claude-apps-gateway#restrict-parent-settings)。

### `policyHelper`

執行您部署的可執行檔，在啟動時計算受管設定，因此您可以從裝置狀態、身分識別或遠端服務衍生原則，而不是靜態檔案。Claude Code 在接受第一個提示之前執行協助程式，並將其發出的設定視為工作階段的受管設定。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。從 macOS plist、Windows HKLM 登錄或受管設定檔案讀取。Claude Code 從攜帶[原則金鑰](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)的最高優先順序受管來源讀取金鑰，並只在該來源是這三個之一時執行協助程式；它忽略伺服器受管設定、HKCU 登錄和主機提供的父設定中的金鑰。
- **類型** ：具有 `path`、`timeoutMs` 和 `refreshIntervalMs` 的物件
- **預設** ：未設定，因此沒有協助程式執行

當伺服器受管設定在啟動時傳遞原則時，它們優先於協助程式的來源，協助程式不執行。 如果稍後的設定擷取報告伺服器受管設定已移除，Claude Code 會在該點執行協助程式，而不是等待下一次啟動。其輸出控制工作階段的其餘部分，失敗的執行會以與[失敗的啟動執行](https://code.claude.com/docs/zh-TW/settings-reference#helper-failures)相同的訊息結束工作階段。 此範例以 5 秒逾時執行協助程式，並每五分鐘重新執行一次： managed-settings.json

```
{
  "policyHelper": {
    "path": "/usr/local/bin/claude-policy",
    "timeoutMs": 5000,
    "refreshIntervalMs": 300000
  }
}

```

#### 寫入協助程式輸出

Claude Code 執行協助程式時不帶任何引數，在其環境中設定 `CLAUDE_CODE_VERSION`，並從 stdout 讀取 JSON 信封，上限為 1 MiB。 將設定放在 `managedSettings` 金鑰下。沒有 `managedSettings` 金鑰的裸設定物件會以 `managedSettings` 未定義的方式解析並不套用任何內容，Claude Code 不報告任何錯誤：

```
{
  "managedSettings": {
    "permissions": { "deny": ["Read(//etc/secrets/**)"] }
  }
}

```

當協助程式發出 `managedSettings` 時，該物件成為執行的唯一受管設定來源：Claude Code 忽略 MDM、檔案和 HKCU 來源，只從協助程式的輸出讀取[跨來源金鑰](https://code.claude.com/docs/zh-TW/managed-settings#keys-read-from-every-admin-source)，並永遠不合併[父設定](https://code.claude.com/docs/zh-TW/managed-settings#parent-settings-from-embedding-hosts)。 啟動 `forceRemoteSettingsRefresh` 檢查在協助程式之前執行，並讀取任何管理員來源。以 0 結束的協助程式，其信封省略 `managedSettings` 不貢獻受管設定，其他來源照常套用。

#### 協助程式失敗

協助程式執行在以下情況下失敗：

- `path` 違反 [`policyHelper.path`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper-path) 中的規則。
- `path` 處沒有常規檔案。Claude Code 在啟動協助程式之前檢查檔案，在相同的 `timeoutMs` 預算內，因此無回應的網路掛載可能導致執行失敗。
- 協助程式以非零結束、在 `timeoutMs` 經過時仍在執行，或根本無法啟動，例如因為它不可執行。
- 協助程式寫入超過 1 MiB 到 stdout 或 stderr。
- stdout 不是單一 JSON 物件，或其 `managedSettings` 有 [Claude Code 無法修復的架構違規](https://code.claude.com/docs/zh-TW/managed-settings#find-entries-claude-code-dropped)。

當啟動執行失敗時，Claude Code 列印原因並拒絕啟動。非零結束後，原因包括協助程式的 stderr，或當 stderr 為空時的 stdout。逾時後，原因命名 `timeoutMs` 限制，不包括協助程式輸出的任何部分。拒絕涵蓋互動式工作階段、`claude -p`、Agent SDK 工作階段、[背景工作階段](https://code.claude.com/docs/zh-TW/agent-view) 和大多數子命令。 拒絕是故意的，因此需要中斷恢復力的協助程式應該從其自己的快取提供並以 0 結束。 當背景重新整理失敗時，Claude Code 保持最後成功的原則有效，`/status` 顯示失敗的重新整理及其原因，直到重新整理成功。每次重新整理在與啟動執行相同的 `timeoutMs` 和失敗規則下執行。 使用 `--debug`，Claude Code 將協助程式的 stderr 從每次執行寫入[偵錯日誌](https://code.claude.com/docs/zh-TW/debug-your-config)。 Claude Code 將無效的 `policyHelper` 值報告為[捨棄的項目](https://code.claude.com/docs/zh-TW/managed-settings#find-entries-claude-code-dropped)，並在剩餘的受管設定上啟動工作階段，不執行協助程式。無效值包括裸路徑字串和低於[其最小值](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper-timeoutms)的 `timeoutMs`。 若要關閉協助程式，請從設定它的來源移除金鑰。

### `policyHelper.path`

命名 Claude Code 執行的協助程式可執行檔。如需路徑違反下列規則時發生的情況，請參閱[協助程式失敗](https://code.claude.com/docs/zh-TW/settings-reference#helper-failures)。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。從 macOS plist、Windows HKLM 登錄或受管設定檔案讀取，無論 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 讀取的位置。
- **類型** ：字串，標準化形式的絕對路徑，沒有 `.` 或 `..` 段；在 Windows 上，以 `.exe` 結尾的磁碟機字母或 UNC 路徑
- **預設** ：無；設定 `policyHelper` 時為必需

managed-settings.json

```
{
  "policyHelper": {
    "path": "/usr/local/bin/claude-policy"
  }
}

```

### `policyHelper.timeoutMs`

設定 Claude Code 在將執行視為失敗之前等待協助程式的時間。逾時的執行失敗方式與非零結束相同，因此在啟動時 Claude Code 拒絕啟動。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。從 macOS plist、Windows HKLM 登錄或受管設定檔案讀取，無論 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 讀取的位置。
- **類型** ：整數，毫秒，最小 `1000`
- **預設** ：`10000`

managed-settings.json

```
{
  "policyHelper": {
    "path": "/usr/local/bin/claude-policy",
    "timeoutMs": 5000
  }
}

```

### `policyHelper.refreshIntervalMs`

讓 Claude Code 在背景按間隔重新執行協助程式，以便原則變更到達執行中的工作階段。當重新整理成功時，其輸出替換先前的受管設定，不需重新啟動；當重新整理失敗時，Claude Code 保持它已有的原則。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。從 macOS plist、Windows HKLM 登錄或受管設定檔案讀取，無論 [`policyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#policyhelper) 讀取的位置。
- **類型** ：整數，毫秒：`0` 以停用重新整理，否則至少 `60000`
- **預設** ：未設定，因此 Claude Code 在啟動時執行協助程式一次

此範例每五分鐘重新執行協助程式： managed-settings.json

```
{
  "policyHelper": {
    "path": "/usr/local/bin/claude-policy",
    "refreshIntervalMs": 300000
  }
}

```

### `wslInheritsWindowsSettings`

讓 WSL 上的 Claude Code 從 Windows 原則鏈讀取受管設定，HKLM 和 Windows 受管設定檔案優先於 `/etc/claude-code` 和下方的 HKCU。當鏈開啟時，Claude Code 只在 `C:\Program Files\ClaudeCode\` 下沒有受管設定檔案或放置項目傳遞[原則金鑰](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)時讀取 `/etc/claude-code`。設定它以將您已在 Windows 上部署的原則擴展到同一機器上的 WSL 工作階段，以便它們遵循與主機工作階段相同的規則。Claude Code 只在 HKLM 登錄金鑰或 `C:\Program Files\ClaudeCode\` 下的受管設定檔案或放置項目中設定時接受它，兩者都需要 Windows 管理員寫入。

- **範圍** ：[`Managed`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在管理員控制的 Windows 來源中。
- **類型** ：布林值
  - `true`：WSL 上的 Claude Code 從 Windows 原則鏈讀取受管設定，並只在 `C:\Program Files\ClaudeCode\` 下沒有受管設定檔案或放置項目傳遞[原則金鑰](https://code.claude.com/docs/zh-TW/managed-settings#how-claude-code-combines-managed-sources)時讀取 `/etc/claude-code`
  - `false`：WSL 只讀取 `/etc/claude-code`
- **預設** ：`false`，因此 WSL 只讀取 `/etc/claude-code`

managed-settings.json

```
{
  "wslInheritsWindowsSettings": true
}

```

一旦管理員來源開啟鏈，HKCU 原則只在 HKCU 也將金鑰設定為 `true` 時加入 WSL 上的鏈。該副本不會自行開啟鏈。只包含此金鑰的 Windows 來源不計為原則來源，因此較低優先順序的來源仍然提供原則。此金鑰對原生 Windows 無效。

## 全域設定

將這些金鑰儲存在 `~/.claude.json` 中，而不是在設定檔中。Claude Code 會忽略其他地方的設定。Claude Code 和 `/config` 會為您寫入大部分設定，您也可以手動編輯它們。

### `autoConnectIde`

當您從外部終端啟動 Claude Code 時，自動連接到執行中的 IDE。當您在 VS Code 或 JetBrains 終端外執行 Claude Code 時，會在 `/config` 中顯示為**自動連接到 IDE（外部終端）** 。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：當您從外部終端啟動 Claude Code 時，它會自動連接到執行中的 IDE
  - `false`：Claude Code 不會從外部終端自動連接；在 VS Code 或 JetBrains 終端內，或使用 `--ide` 時，它仍會連接
- **預設值** ：`false`
- **每個工作階段的覆寫** ：[`CLAUDE_CODE_AUTO_CONNECT_IDE`](https://code.claude.com/docs/zh-TW/env-vars) 在任一方向上優先於此金鑰，持續一個工作階段

~/.claude.json

```
{
  "autoConnectIde": true
}

```

Claude Code 會忽略 `settings.json` 中的此金鑰。

### `autoInstallIdeExtension`

當您從 VS Code 終端執行 Claude Code 時，自動安裝 Claude Code IDE 擴充功能。當您在 VS Code 或 JetBrains 終端內執行 Claude Code 時，會在 `/config` 中顯示為**自動安裝 IDE 擴充功能** 。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：當您從 VS Code 終端執行 Claude Code 時，它會自動安裝 IDE 擴充功能
  - `false`：Claude Code 不會自動安裝擴充功能
- **預設值** ：`true`
- **每個工作階段的覆寫** ：[`CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL`](https://code.claude.com/docs/zh-TW/env-vars) 設定為 `1` 會跳過安裝一個工作階段，即使此金鑰為 `true`

~/.claude.json

```
{
  "autoInstallIdeExtension": false
}

```

Claude Code 會忽略 `settings.json` 中的此金鑰。

### `copyOnSelect`

當您在[全螢幕呈現](https://code.claude.com/docs/zh-TW/fullscreen#use-the-mouse)或[代理程式檢視](https://code.claude.com/docs/zh-TW/agent-view)中用滑鼠完成文字選取時，自動將文字複製到您的剪貼簿。當全螢幕呈現開啟時，會在 `/config` 中顯示為**選取時複製** 。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：當您完成選取文字時，Claude Code 會將文字複製到您的剪貼簿
  - `false`：選取文字不會改變您的剪貼簿，您改為[使用快捷鍵複製選取項目](https://code.claude.com/docs/zh-TW/fullscreen#use-the-mouse)
- **預設值** ：`true`

~/.claude.json

```
{
  "copyOnSelect": false
}

```

Claude Code 會忽略 `settings.json` 中的此金鑰。

### `diffTool`

選擇 Claude Code 在連接 [VS Code](https://code.claude.com/docs/zh-TW/vs-code) 或 [JetBrains](https://code.claude.com/docs/zh-TW/jetbrains#features) IDE 時，顯示其提議的 `Edit` 或 `Write` 變更的差異的位置：`"auto"` 在 IDE 的差異檢視器中開啟它，`"terminal"` 將其保留在終端中。僅當 Claude Code 連接到 VS Code 或 JetBrains IDE 時，才會在 `/config` 中顯示為**差異工具** 。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：字串，其中之一：
  - `"auto"`：當連接 VS Code 或 JetBrains IDE 時，Claude Code 在 IDE 的差異檢視器中開啟差異
  - `"terminal"`：Claude Code 將差異保留在終端中
- **預設值** ：`"auto"`

~/.claude.json

```
{
  "diffTool": "terminal"
}

```

Claude Code 會忽略 `settings.json` 中的此金鑰。

### `externalEditorContext`

當您按下 `Ctrl+G` 時，Claude Code 會在您的[外部編輯器](https://code.claude.com/docs/zh-TW/interactive-mode#general-controls)中開啟您正在輸入的提示。啟用此金鑰時，編輯器緩衝區會以 Claude 的前一個回應作為 `#` 註解行開始，因此您可以在寫入時讀取它，Claude Code 會在您儲存時移除這些行。會在 `/config` 中顯示為**在外部編輯器中顯示最後回應** 。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)
- **類型** ：布林值
  - `true`：編輯器緩衝區以 Claude 的前一個回應作為 `#` 註解行開始，Claude Code 會在您儲存時移除這些行
  - `false`：編輯器緩衝區僅以您的提示開啟
- **預設值** ：`false`

~/.claude.json

```
{
  "externalEditorContext": true
}

```

啟用此功能時，Claude Code 開啟的緩衝區看起來像這樣，只有標記行下方的文字會作為您的提示發送：

```
# ─── Claude's last response (for reference; removed on save) ───
# I added the retry loop to fetchUser in src/api.ts and a test
# for the timeout case. Want me to wire the same retry into
# fetchOrders?
# ─── Write your reply below this line ──────────────────────────

Yes, and cap it at three attempts.

```

Claude Code 保留回應的最後 50 行，並用 `# … (earlier output truncated)` 標記截斷。 Claude Code 會忽略 `settings.json` 中的此金鑰。

### `permissionExplainerEnabled`

在 v2.1.257 中移除，連同 Bash 和 PowerShell 權限提示上的 `Ctrl+E` 命令說明一起移除。在目前版本中設定此項無效。 在 v2.1.256 及更早版本中，您可以在 Bash 或 PowerShell 權限提示上按 `Ctrl+E` 以查看模型產生的命令說明，並將此金鑰設定為 `false` 以關閉該快捷鍵。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在 v2.1.256 及更早版本上。
- **類型** ：布林值
- **預設值** ：`true`

### `teammateDefaultModel`

在 v2.1.234 中移除，連同其 `/config` 列**預設隊友模型** 一起移除。在目前版本中設定此項無效。 在 v2.1.233 及更早版本中，您將此金鑰設定為[代理程式團隊](https://code.claude.com/docs/zh-TW/agent-teams#specify-teammates-and-models)隊友的模型，您的提示未為其命名模型：一個別名，例如 `"sonnet"`，或 `null` 以遵循領導者的模型。如需 Claude Code 現在為此類隊友選擇的模型，請參閱[指定隊友和模型](https://code.claude.com/docs/zh-TW/agent-teams#specify-teammates-and-models)。

- **範圍** ：[`全域設定`](https://code.claude.com/docs/zh-TW/settings-reference#scopes)。在 v2.1.233 及更早版本上。
- **類型** ：字串，模型別名或完整模型 ID，或 `null`
- **預設值** ：未設定

## 另請參閱

- [設定權限](https://code.claude.com/docs/zh-TW/permissions)：規則語法、權限模式和工作區信任
- [環境變數](https://code.claude.com/docs/zh-TW/env-vars)：Claude Code 讀取的每個 `CLAUDE_*`、`ANTHROPIC_*` 和提供者變數
- [Claude 可用的工具](https://code.claude.com/docs/zh-TW/tools-reference)：內建工具及哪些需要核准
- [設定檔範例](https://code.claude.com/docs/zh-TW/settings-example)：個人檔案、團隊檔案和組織的受管檔案
- [設定受管設定](https://code.claude.com/docs/zh-TW/admin-setup)：組織如何決定要強制執行的內容
- [部署受管設定](https://code.claude.com/docs/zh-TW/managed-settings)：傳遞機制、受管層級內的優先順序和受管設定中的無效項目
- [偵錯您的設定](https://code.claude.com/docs/zh-TW/debug-your-config)：`claude doctor` 和設定錯誤對話框

是否 Assistant Responses are generated using AI and may contain mistakes.
