此頁面記錄了較早的 Slack 中的 Claude Code，它在每個工作階段下以個別使用者的帳戶運行。

- **Team 和 Enterprise 方案：** Anthropic 正在停用此版本，改用 [Claude Tag](https://claude.com/product/tag)，它以 @Claude 身份作為您組織的共享身份運行，具有管理員配置的存取權限。您現有的 Slack 應用程式和 @Claude 控制代碼保持不變，您的 Anthropic 帳戶團隊可以告訴您轉換日期。[設定 Claude Tag](https://claude.com/docs/claude-tag/overview) 以建立新工作區；若要移動已使用此版本的工作區，請參閱[從較早的 Slack 中的 Claude 遷移](https://claude.com/docs/claude-tag/admins/migrate-from-earlier)。
- **Pro 和 Max 方案：** Claude Tag 在個人方案上不可用，因此此頁面仍然是設定路徑。

Slack 中的 Claude Code 將 Claude Code 的強大功能直接帶入您的 Slack 工作區。當您提及 `@Claude` 並附帶編碼任務時，Claude 會自動檢測意圖並在雲端建立 Claude Code 工作階段，讓您無需離開團隊對話即可委派開發工作。 此整合建立在現有的 Claude for Slack 應用程式基礎上，但為編碼相關請求添加了智能路由到雲端的 Claude Code。每個工作階段在您自己的 Claude 帳戶下運行，使用您連接的儲存庫和您的方案限制。

## 使用案例

- **錯誤調查和修復** ：要求 Claude 在 Slack 頻道中報告錯誤時立即調查和修復。
- **快速代碼審查和修改** ：讓 Claude 根據團隊反饋實現小功能或重構代碼。
- **協作調試** ：當團隊討論提供關鍵背景資訊（例如錯誤重現或用戶報告）時，Claude 可以使用該資訊來指導其調試方法。
- **並行任務執行** ：在 Slack 中啟動編碼任務，同時繼續其他工作，完成時接收通知。

## 先決條件

在使用 Slack 中的 Claude Code 之前，請確保您具有以下條件：

| 要求         | 詳情                                                                                          |
| ------------ | --------------------------------------------------------------------------------------------- |
| Claude 計畫  | Pro、Max、Team 或 Enterprise，具有 Claude Code 存取權限（高級席位或 Chat + Claude Code 席位） |
| 雲端工作階段 | [雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)已為您的帳戶啟用     |
| GitHub 帳戶  | 在 [claude.ai/code](https://claude.ai/code) 連接，至少有一個存儲庫已驗證                      |
| Slack 驗證   | 您的 Slack 帳戶通過 Claude 應用程式連接到您的 Claude 帳戶                                     |

## 在 Slack 中設定 Claude Code

1 在 Slack 中安裝 Claude 應用程式 工作區管理員必須從 Slack 應用程式市場安裝 Claude 應用程式。訪問 [Slack 應用程式市場](https://slack.com/marketplace/A08SF47R6P4) 並點擊「Add to Slack」以開始安裝程序。 2 連接您的 Claude 帳戶 應用程式安裝後，驗證您的個人 Claude 帳戶：

1. 通過點擊您的應用程式部分中的「Claude」在 Slack 中開啟 Claude 應用程式
1. 開啟應用程式首頁標籤
1. 點擊「Connect」以將您的 Slack 帳戶與您的 Claude 帳戶連接
1. 在您的瀏覽器中完成驗證流程

3 設定雲端工作階段 確保雲端工作階段已為您的帳戶正確設定：

- 訪問 [claude.ai/code](https://claude.ai/code) 並使用您連接到 Slack 的同一帳戶登入
- 如果尚未連接，請連接您的 GitHub 帳戶
- 驗證至少一個您希望 Claude 使用的存儲庫

4 選擇您的路由模式 連接帳戶後，設定 Claude 如何在 Slack 中處理您的訊息。開啟 Slack 中的 Claude 應用程式首頁以找到**路由模式** 設定。

| 模式                                                                                                                                                                                                            | 行為                                                                                                                                                                 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **僅代碼**                                                                                                                                                                                                      | Claude 將所有 @mentions 路由到 Claude Code 工作階段。最適合使用 Claude in Slack 專門用於開發任務的團隊。                                                             |
| **代碼 + 聊天**                                                                                                                                                                                                 | Claude 分析每條訊息並智能地在 Claude Code（用於編碼任務）和 Claude Chat（用於寫作、分析和一般問題）之間路由。最適合希望為所有類型工作提供單一 @Claude 入口點的團隊。 |
| 在代碼 + 聊天模式中，如果 Claude 將訊息路由到聊天但您想要編碼工作階段，您可以點擊「Retry as Code」以改為建立 Claude Code 工作階段。同樣，如果它被路由到代碼但您想要聊天工作階段，您可以在該執行緒中選擇該選項。 |                                                                                                                                                                      |
| 5                                                                                                                                                                                                               |                                                                                                                                                                      |
| 將 Claude 新增到頻道                                                                                                                                                                                            |                                                                                                                                                                      |
| Claude 在安裝後不會自動新增到任何頻道。要在頻道中使用 Claude，請通過在該頻道中輸入 `/invite @Claude` 來邀請它。Claude 只能在已新增它的頻道中回應 @mentions。                                                    |                                                                                                                                                                      |

## 工作原理

### 自動檢測

在 Code + Chat 路由模式中，當您在 Slack 頻道或執行緒中提及 @Claude 時，Claude 會自動偵測您的訊息是否為編碼任務。編碼任務會被路由到 Claude Code 雲端工作階段。其他任何內容都會收到常規聊天回覆。在 Code 專用模式中，每個 @mention 都會進入 Claude Code。 您也可以明確告訴 Claude 將請求作為編碼任務處理，即使它沒有自動檢測到。 Slack 中的 Claude Code 僅在頻道（公開或私人）中工作。它在直接訊息 (DM) 中不起作用。

### 背景資訊收集

**來自執行緒** ：當您在執行緒中 @mention Claude 時，它會從該執行緒中的所有訊息收集背景資訊以理解完整對話。 **來自頻道** ：當直接在頻道中提及時，Claude 會查看最近的頻道訊息以獲取相關背景資訊。 此背景資訊幫助 Claude 理解問題、選擇適當的存儲庫並指導其任務方法。 當在 Slack 中調用 @Claude 時，Claude 會獲得對對話背景資訊的存取權限以更好地理解您的請求。Claude 可能會遵循背景資訊中其他訊息的指示，因此使用者應確保僅在受信任的 Slack 對話中使用 Claude。

### 工作階段流程

1. **啟動** ：您 @mention Claude 並提出編碼請求
1. **檢測** ：Claude 分析您的訊息並檢測編碼意圖
1. **工作階段建立** ：在 claude.ai/code 上建立新的 Claude Code 工作階段
1. **進度更新** ：Claude 在工作進行時向您的 Slack 執行緒發佈狀態更新
1. **完成** ：完成後，Claude @mentions 您並提供摘要和操作按鈕
1. **審查** ：點擊「View Session」以查看完整記錄，或點擊「Create PR」以開啟拉取請求

## 用戶介面元素

### 訊息操作

- **View Session** ：在您的瀏覽器中打開完整的 Claude Code 工作階段，您可以在其中查看所有執行的工作、繼續工作階段或提出其他請求。
- **Create PR** ：直接從工作階段的更改建立拉取請求。
- **Retry as Code** ：如果 Claude 最初作為聊天助手回應但您想要編碼工作階段，點擊此按鈕以將請求重試為 Claude Code 任務。
- **Change Repo** ：允許您選擇不同的存儲庫，如果 Claude 選擇不正確。

### 存儲庫選擇

Claude 根據您的 Slack 對話中的背景資訊自動選擇存儲庫。如果多個存儲庫可能適用，Claude 可能會顯示一個下拉菜單，允許您選擇正確的存儲庫。

## 存取和權限

### 用戶級別存取

| 存取類型             | 要求                                                           |
| -------------------- | -------------------------------------------------------------- |
| Claude Code 工作階段 | 每個用戶在其自己的 Claude 帳戶下運行工作階段                   |
| 使用情況和速率限制   | 工作階段計入個人用戶的計畫限制                                 |
| 存儲庫存取           | 用戶只能存取他們個人連接的存儲庫                               |
| 工作階段歷史記錄     | 工作階段出現在您的 Claude Code 歷史記錄中，位於 claude.ai/code |

### 工作區級別存取

Slack 工作區管理員控制 Claude 應用程式是否可在其工作區中使用：

| 控制                 | 描述                                                                            |
| -------------------- | ------------------------------------------------------------------------------- |
| 應用程式安裝         | 工作區管理員決定是否從 Slack 應用程式市場安裝 Claude 應用程式                   |
| Enterprise Grid 分發 | 對於 Enterprise Grid 組織，組織管理員可以控制哪些工作區有權存取 Claude 應用程式 |
| 應用程式移除         | 從工作區移除應用程式會立即撤銷該工作區中所有用戶的存取權限                      |

### 基於頻道的存取控制

安裝應用程式不會將 Claude 添加到任何頻道。Claude 只在已添加它的頻道中回應 @mentions；使用 `/invite @Claude` 邀請它。它在公開和私人頻道中都可以工作。管理員可以通過管理 Claude 被邀請到哪些頻道以及誰有權存取這些頻道來控制誰使用 Claude Code。這在工作區級別權限之外增加了一層存取控制。

## 在何處可以存取什麼

**在 Slack 中** ：您將看到狀態更新、完成摘要和操作按鈕。完整記錄被保留並始終可存取。 **在 claude.ai/code** ：完整的 Claude Code 工作階段，包含完整對話歷史記錄、所有代碼更改和檔案操作。工作階段保存在您的 Claude Code 歷史記錄中，位於 [claude.ai/code](https://claude.ai/code)，您可以在其中繼續過去的工作階段、參考它們或建立拉取請求。 對於 Enterprise 和 Team 帳戶，從 Slack 中的 Claude 建立的工作階段會自動對組織可見。有關更多詳情，請參閱 [雲端工作階段共享](https://code.claude.com/docs/zh-TW/claude-code-on-the-web#share-sessions)。

## 最佳實踐

### 撰寫有效的請求

- **具體明確** ：在相關時提供檔案名稱、函式名稱或錯誤訊息。
- **提供背景資訊** ：如果從對話中不清楚，請提及儲存庫或專案。
- **定義成功** ：解釋「完成」的樣子。Claude 應該撰寫測試嗎？更新文件？建立 PR？
- **使用執行緒** ：在討論錯誤或功能時在執行緒中回覆，以便 Claude 可以收集完整的背景資訊。

### 何時使用 Slack 與網頁

**使用 Slack 的時機** ：背景資訊已存在於 Slack 討論中、您想非同步啟動任務，或您正在與需要可見性的隊友協作。 **直接使用網頁的時機** ：您需要上傳檔案、想要在開發期間進行即時互動，或正在處理更長、更複雜的任務。

## 故障排除

### “Claude Code 未為您的帳戶啟用”

此錯誤表示您的 Claude 帳戶尚未有雲端環境。使用您連接到 Slack 的同一帳戶登入 [claude.ai/code](https://claude.ai/code) 一次，並完成[網路快速入門](https://code.claude.com/docs/zh-TW/web-quickstart#connect-github)，這會建立您的預設雲端環境或要求您建立它。錯誤會在您下次提及時清除。每位使用者必須個別執行此操作。

### 工作階段未啟動

1. 驗證您的 Claude 帳戶已在 Claude 應用程式首頁中連接
1. 檢查您的帳戶是否已啟用雲端工作階段
1. 確保您至少有一個 GitHub 存儲庫連接到 Claude Code

### 來自 Claude Tag 頻道的工作階段無法啟動

此項目適用於使用 [Claude Tag](https://claude.com/docs/claude-tag/overview) 的工作區，其中 Claude 在頻道中以您組織的共享身分工作，而不是以任何成員的帳戶工作。如果您在 [claude.ai/code](https://claude.ai/code) 建立了頻道的雲端環境，它屬於您的個人帳戶，Claude 無法在個人環境中啟動頻道工作階段。Claude Code 會立即使工作階段失敗，重試也無法幫助。 如果您是擁有者且環境是您自己的，請從環境選擇器[與組織共享](https://code.claude.com/docs/zh-TW/cloud-environments#organization-shared-environments)。否則，擁有者應從[管理設定](https://claude.ai/admin-settings)中的**雲端環境** 頁面將其重新建立為組織共享環境。 您可以透過兩種方式應用它：

- 在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 將其設定為組織預設值。
- [在 Claude Tag 管理設定中的頻道上設定它](https://claude.com/docs/claude-tag/admins/troubleshooting#channel-sessions-use-the-wrong-environment-or-can%E2%80%99t-find-one)。

如果您不是擁有者，請將此項目傳送給擁有者。

### 存儲庫未顯示

1. 在 [claude.ai/code](https://claude.ai/code) 連接存儲庫
1. 驗證您對該存儲庫的 GitHub 權限
1. 嘗試斷開並重新連接您的 GitHub 帳戶

### 選擇了錯誤的存儲庫

1. 點擊「Change Repo」按鈕以選擇不同的存儲庫
1. 在您的請求中包括存儲庫名稱以獲得更準確的選擇

### 驗證錯誤

1. 在應用程式首頁中斷開並重新連接您的 Claude 帳戶
1. 確保您在瀏覽器中登入正確的 Claude 帳戶
1. 檢查您的 Claude 計畫是否包括 Claude Code 存取

## 目前限制

- **僅 GitHub** ：存儲庫必須在 GitHub 上。
- **一次一個拉取請求** ：每個工作階段可以建立一個拉取請求。
- **需要雲端工作階段存取** ：使用者需要存取[雲端工作階段](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)；沒有存取權限的使用者會收到標準聊天回應。

## 相關資源

## [雲端上的 Claude Code 深入瞭解雲端工作階段 ](https://code.claude.com/docs/zh-TW/claude-code-on-the-web)

## [Claude for Slack Claude for Slack 的一般文件 ](https://claude.com/claude-and-slack)

## [Claude Tag 在 Slack 中由組織管理的 @Claude，具有管理員設定的存取權限 ](https://claude.com/docs/claude-tag/overview)

## [Slack App Marketplace 從 Slack Marketplace 安裝 Claude 應用程式 ](https://slack.com/marketplace/A08SF47R6P4)

## [Claude 說明中心 取得額外支援 ](https://support.claude.com)

是否 助手
