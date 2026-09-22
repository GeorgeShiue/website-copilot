根據預設，SDK 會將工作階段文字記錄寫入本機檔案系統上 `~/.claude/projects/` 下的 JSONL 檔案。`SessionStore` 配接器可讓您將這些文字記錄鏡像到您自己的後端，例如物件儲存、鍵值儲存或資料庫，以便在一個主機上建立的工作階段可以在另一個主機上從相符的工作目錄繼續進行。 使用工作階段儲存的常見原因：

- **多主機部署。** 無伺服器函式、自動擴展的工作者和 CI 執行器不共享檔案系統。共用儲存可讓複本繼續彼此的工作階段。
- **耐久性。** 本機容器是暫時的。外部儲存可在重新啟動和重新部署後存活。
- **合規性和稽核。** 將文字記錄保留在您已經管理的儲存中，使用您自己的保留規則、加密和存取控制。

## `SessionStore` 介面

`SessionStore` 是一個物件，具有兩個必需的方法 `append` 和 `load`，以及四個可選方法。SDK 呼叫 `append` 在查詢期間寫入記錄項目，呼叫 `load` 讀取它們以進行恢復。 TypeScript Python

```
// Exported from @anthropic-ai/claude-agent-sdk as
// SessionStore, SessionKey, SessionStoreEntry, SessionSummaryEntry.

type SessionKey = {
  projectKey: string;
  sessionId: string;
  subpath?: string;
};

type SessionStore = {
  // Required
  append(key: SessionKey, entries: SessionStoreEntry[]): Promise<void>;
  load(key: SessionKey): Promise<SessionStoreEntry[] | null>;

  // Optional
  listSessions?(
    projectKey: string,
  ): Promise<Array<{ sessionId: string; mtime: number }>>;
  listSessionSummaries?(projectKey: string): Promise<SessionSummaryEntry[]>;
  delete?(key: SessionKey): Promise<void>;
  listSubkeys?(key: {
    projectKey: string;
    sessionId: string;
  }): Promise<string[]>;
};

type SessionSummaryEntry = {
  sessionId: string;
  mtime: number;
  data: Record<string, unknown>;
};

```

```
# Exported from claude_agent_sdk as
# SessionStore, SessionKey, SessionStoreEntry, SessionSummaryEntry.

class SessionKey(TypedDict):
    project_key: str
    session_id: str
    subpath: NotRequired[str]

class SessionStore(Protocol):
    # Required
    async def append(
        self, key: SessionKey, entries: list[SessionStoreEntry]
    ) -> None: ...
    async def load(self, key: SessionKey) -> list[SessionStoreEntry] | None: ...

    # Optional — omit or raise NotImplementedError
    async def list_sessions(
        self, project_key: str
    ) -> list[SessionStoreListEntry]: ...
    async def list_session_summaries(
        self, project_key: str
    ) -> list[SessionSummaryEntry]: ...
    async def delete(self, key: SessionKey) -> None: ...
    async def list_subkeys(self, key: SessionListSubkeysKey) -> list[str]: ...

class SessionSummaryEntry(TypedDict):
    session_id: str
    mtime: int
    data: dict[str, Any]

```

`SessionKey` 指向一個記錄。`projectKey` 是工作目錄的穩定、檔案系統安全的編碼，`sessionId` 是工作階段 UUID，`subpath` 在項目屬於子代理記錄或邊車檔案而不是主對話時設定。 因為 `projectKey` 編碼了工作目錄，請從與原始執行的工作目錄相符的工作目錄中從存放區恢復或繼續。在 TypeScript 中，如果您在查詢的 [`env` 選項](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options)中在 `CLAUDE_CONFIG_DIR` 旁邊設定 [`CLAUDE_CODE_PROJECT_DIR_NAME`](https://code.claude.com/docs/zh-TW/sessions#name-the-project-directory-yourself)，SDK 會按該名稱鍵入該查詢的項目，以及其 `resume` 和 `continue` 查詢。因為 `listSessions` 和 `deleteSession` 等獨立協助程式不接受 `env` 並讀取程序環境，請在主機程序環境中也設定 `CLAUDE_CONFIG_DIR` 和相同的名稱。需要 Agent SDK v0.3.234 或更新版本。 將 `subpath` 視為不透明的鍵後綴；它遵循磁碟上的配置，例如 `subagents/agent-<id>`。當 `subpath` 未定義時，鍵指向主記錄。

| 方法                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 必需 | 呼叫時機                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `append`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 是   | 在本機寫入每批記錄項目後。項目是 JSON 安全的物件，本機 JSONL 中每行一個。                                                                                                                                                               |
| `load`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 是   | 在子程序產生之前，當設定 `resume` 時或 `continue: true` 解析最新的存放區工作階段時，以及列出時每個工作階段一次（如果從 `listSessionSummaries` 回退）。如果工作階段未知，傳回 `null`。                                                   |
| `listSessions`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 否   | 由 `listSessions({ sessionStore })` 和 `query()`/`startup()` 與 `continue: true` 呼叫。如果未定義，`continue: true` 會擲出例外，除非實作 `listSessionSummaries`，否則 `listSessions({ sessionStore })` 會擲出例外。                     |
| `listSessionSummaries`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 否   | 由 `listSessions({ sessionStore })` 在一次呼叫中讀取所有工作階段的中繼資料。在 `append` 內維護摘要。如果未定義，列出會回退到 `listSessions` 加上每個工作階段的 `load`。                                                                 |
| `delete`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 否   | 由 `deleteSession({ sessionStore })` 呼叫。刪除主鍵（無 `subpath`）必須級聯到該工作階段的所有子鍵，並且也移除工作階段的摘要項目，因此已刪除的工作階段停止出現在 `listSessionSummaries` 中。如果未定義，刪除是無操作的，適合僅追加後端。 |
| `listSubkeys`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 否   | 在恢復期間，探索子代理記錄。如果未定義，只有主記錄被恢復。                                                                                                                                                                              |
| 在 `SessionSummaryEntry` 中，`mtime` 是邊車的存放區寫入時間，必須與 `listSessions` 傳回的 `mtime` 值共用時鐘來源。`data` 是不透明的 SDK 擁有的狀態；逐字保存它而不解釋它。 透過在 `append` 內的每個批次上呼叫匯出的 `foldSessionSummary` 協助程式（Python 中為 `fold_session_summary`）來建立項目。跳過其鍵具有 `subpath` 的批次；子代理記錄不得對主工作階段的摘要做出貢獻。摺疊永遠不會設定 `mtime`：在保存時透過 TypeScript 中的 `options.mtime` 引數或在 Python 中覆寫傳回項目上的欄位來標記它。同一工作階段的並行 `append` 呼叫可能在邊車上競爭，因此請使用交易、比較和交換或每個工作階段的鎖定來序列化讀取-摺疊-寫入；摺疊本身是純的。 如需 SDK 對記錄 `load` 傳回的內容所做的操作，請參閱[從存放區恢復](https://code.claude.com/docs/zh-TW/agent-sdk/session-storage#resume-from-the-store)。 |      |                                                                                                                                                                                                                                         |

## 快速開始

SDK 附帶一個 `InMemorySessionStore` 用於開發和測試。下面的示例使用附加的存儲運行查詢，從結果消息中捕獲會話 ID，然後在第二個 `query()` 呼叫中從存儲恢復。第二個呼叫傳遞相同的存儲實例加上 `resume`，因此 SDK 從存儲而不是本地檔案系統載入記錄： TypeScript Python

```
import { query, InMemorySessionStore } from "@anthropic-ai/claude-agent-sdk";

const store = new InMemorySessionStore();

let sessionId: string | undefined;
try {
  for await (const message of query({
    prompt: "List the TypeScript files under src/",
    options: { sessionStore: store },
  })) {
    if (message.type === "result") {
      sessionId = message.session_id;
    }
  }
} catch (error) {
  // A single-shot query() throws after yielding an error result. If the
  // failure was an error result, sessionId was already captured by the loop
  // above; connection or process failures yield no result message.
  console.error(`Session ended with an error: ${error}`);
}

// Resume from the store. The agent has full context from the first call.
for await (const message of query({
  prompt: "Summarize what those files do",
  options: { sessionStore: store, resume: sessionId },
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

```

```
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    InMemorySessionStore,
    ResultMessage,
    query,
)

store = InMemorySessionStore()


async def main():
    session_id = None
    try:
        async for message in query(
            prompt="List the Python files under src/",
            options=ClaudeAgentOptions(session_store=store),
        ):
            if isinstance(message, ResultMessage):
                session_id = message.session_id
    except Exception as error:
        # A single-shot query() raises after yielding an error result. If the
        # failure was an error result, session_id was already captured by the
        # loop above; connection or process failures yield no result message.
        print(f"Session ended with an error: {error}")

    # Resume from the store. The agent has full context from the first call.
    async for message in query(
        prompt="Summarize what those files do",
        options=ClaudeAgentOptions(session_store=store, resume=session_id),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())

```

第二個查詢會列印來自第一個查詢的檔案摘要，這表明代理已從存儲恢復並具有完整的上下文。

## 編寫您自己的適配器

針對您的後端實現 `append` 和 `load`。如果您希望 `listSessions()`、一次呼叫的中繼資料讀取、`deleteSession()` 和子代理恢復針對存儲工作，請添加 `listSessions`、`listSessionSummaries`、`delete` 和 `listSubkeys`。 傳遞給 `append` 的條目類型為 `SessionStoreEntry`（一個 `{ type: string; ... }` 物件）。將它們視為不透明的 JSON 安全值：按順序持久化它們，並從 `load` 以相同順序返回它們。`load` 必須返回與追加的條目深度相等的條目；不需要位元組相等的序列化，因此像重新排序物件鍵的二進位 JSON 欄位類型這樣的後端是可以的。

## 參考實現

兩個 SDK 存儲庫在 TypeScript 的 [`examples/session-stores/`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores) 和 Python 的 [`examples/session_stores/`](https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples/session_stores) 下包含可運行的參考適配器。每種存儲類型都有一個適配器，每個都展示了 `append` 和 `load` 如何映射到該類型的後端。它們未發佈為套件；將最接近您後端的類型的適配器複製到您的項目中，安裝您後端的客戶端，並進行調整。

| 存儲類型                                                                                                                                          | 存儲模型                                                                             | 範例適配器                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 物件存儲                                                                                                                                          | 每個 `append()` 一個部分文件；`load()` 列出部分、排序並連接。                        | S3 ([TypeScript](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/s3), [Python](https://github.com/anthropics/claude-agent-sdk-python/blob/main/examples/session_stores/s3_session_store.py))                   |
| 鍵值存儲                                                                                                                                          | 每個記錄一個列表，`append()` 推送到該列表，`load()` 按範圍讀取，加上會話的排序索引。 | Redis ([TypeScript](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/redis), [Python](https://github.com/anthropics/claude-agent-sdk-python/blob/main/examples/session_stores/redis_session_store.py))          |
| 關聯式資料庫或文件存儲                                                                                                                            | 每個條目一行或一個文件，存儲為 JSON 並按插入時分配的鍵排序。                         | Postgres ([TypeScript](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/postgres), [Python](https://github.com/anthropics/claude-agent-sdk-python/blob/main/examples/session_stores/postgres_session_store.py)) |
| 每個適配器都採用預配置的客戶端實例，因此您可以控制認證、TLS、區域和連接池。以下範例將物件存儲適配器連接到 `query()`，然後在另一台主機上從中恢復： |                                                                                      |                                                                                                                                                                                                                                                            |
| TypeScript                                                                                                                                        |                                                                                      |                                                                                                                                                                                                                                                            |

```
import { query } from "@anthropic-ai/claude-agent-sdk";
import { S3Client } from "@aws-sdk/client-s3";
import { S3SessionStore } from "./S3SessionStore"; // copied from examples/session-stores/s3

const store = new S3SessionStore({
  bucket: "my-claude-sessions",
  prefix: "transcripts",
  client: new S3Client({ region: "us-east-1" }),
});

for await (const message of query({
  prompt: "Hello!",
  options: { sessionStore: store },
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// Later, possibly on a different host:
for await (const message of query({
  prompt: "Continue where we left off",
  options: { sessionStore: store, resume: "previous-session-id" },
})) {
  // ...
}

```

### 驗證您的適配器

兩個 SDK 都附帶一個符合性套件，該套件斷言 `append`、`load` 和可選方法必須滿足的行為契約。當未實現這些方法時，可選方法的測試會自動跳過。 在 TypeScript 中，從示例目錄將 [`shared/conformance.ts`](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/examples/session-stores/shared/conformance.ts) 複製到您的測試套件中。在 Python 中，該套件在包中提供。若要使用 pytest 運行它（pytest 不是 SDK 依賴項），請先安裝 pytest：

```
pip install pytest

```

然後在測試文件中將您的適配器作為零參數工廠傳遞給套件，`run_session_store_conformance` 會為每個契約調用一次以構建新的存儲： Python

```
import pytest
from claude_agent_sdk.testing import run_session_store_conformance


@pytest.mark.anyio
async def test_my_store_conformance():
    await run_session_store_conformance(MyRedisStore)

```

按照此示例傳遞 `MyRedisStore` 類本身，當構造函數不帶任何參數時有效。對於採用預配置客戶端的適配器，改為傳遞構造存儲的 lambda。由於契約重複使用相同的會話鍵，工廠返回的每個存儲必須以空存儲開始，因此讓 lambda 為每次調用配置隔離的後端存儲，例如新的記憶體內假對象、唯一的鍵前綴或新的測試資料庫。

## 行為說明

### 雙寫架構

Claude Code 子進程始終首先將每批轉錄條目寫入本地磁碟，然後 SDK 將相同的批次轉發到您的存儲的 `append()`，因此存儲是本地轉錄的鏡像，而不是替代品。哪個副本在運行後保留取決於運行的啟動方式：

- **新會話，或當存儲對該會話沒有任何內容時的恢復** ：您設定目錄下的本地轉錄在運行後保留，存儲接收一份副本。
- **從存儲[恢復的運行](https://code.claude.com/docs/zh-TW/agent-sdk/session-storage#resume-from-the-store)**：本地副本在運行結束時被刪除，因此存儲持有唯一的持久副本。

如果您不希望新會話在本地磁碟上留下轉錄，請在 `options.env` 中將 `CLAUDE_CONFIG_DIR` 設定為臨時目錄。從存儲恢復的運行已經刪除其本地副本，因此不需要此類設定。在 TypeScript 中，也將 `process.env` 展開到 `env` 中，因為 [`env` 選項](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options) 會替換子進程環境。 如果您的應用程式通過設定目錄中的檔案進行登入，例如 OAuth 認證或您的使用者 `settings.json` 中的 `apiKeyHelper`，請先將這些檔案複製到臨時目錄中，或改為在 `env` 中設定 `ANTHROPIC_API_KEY`。否則運行會失敗並顯示 `Not logged in`。 兩個選項與鏡像衝突，如果您將其中任何一個與存儲結合，SDK 會在啟動時拋出異常：

- **TypeScript 中的`persistSession: false`** ：關閉鏡像所基於的本地寫入。Python SDK 沒有等效的選項。
- **檔案檢查點** ，TypeScript 中的 `enableFileCheckpointing` 或 Python 中的 `enable_file_checkpointing`：將其檔案備份直接寫入本地磁碟，SDK 不會將其鏡像到存儲。

### 從存儲恢復

當您傳遞 `resume`，或 TypeScript 中的 `continue: true` 或 Python 中的 `continue_conversation=True`，以及存儲時，SDK 在生成子進程之前會向存儲詢問轉錄：

- **`resume`**：SDK 詢問您傳遞的會話 ID。
- **`continue: true`**或**`continue_conversation=True`**：SDK 詢問存儲的最新會話。

當存儲返回轉錄時，SDK 將其寫入臨時設定目錄，運行子進程時 `CLAUDE_CONFIG_DIR` 指向該目錄，並在運行結束時刪除該目錄。該運行寫入的本地轉錄會隨之刪除，這就是為什麼存儲在此路徑上持有唯一的持久副本。 SDK 還使用來自您真實設定目錄的檔案來初始化臨時目錄。它複製的內容因語言而異：

- **TypeScript** ：認證、`.claude.json` 和您的使用者 `settings.json`。從 `settings.json` 中，它會移除在臨時設定目錄下表現不佳的鍵：`enabledPlugins`、`extraKnownMarketplaces`、其 [`additionalMarketplaces`](https://code.claude.com/docs/zh-TW/settings-reference#extraknownmarketplaces) 別名，以及檔案 `env` 區塊中的任何 `CLAUDE_CONFIG_DIR`。在 Agent SDK v0.3.232 之前，SDK 沒有移除別名。在設定中配置的驗證，例如 [`apiKeyHelper`](https://code.claude.com/docs/zh-TW/settings-reference#apikeyhelper)，在您從存儲恢復時有效。在 Agent SDK v0.3.222 之前，TypeScript SDK 只複製認證和 `.claude.json`。
- **Python** ：僅限認證和 `.claude.json`，因此通過您的使用者 `settings.json` 中的 `apiKeyHelper` 進行驗證的應用程式在從存儲恢復時會失敗並顯示 `Not logged in`。受管或專案設定中的 `apiKeyHelper` 仍然有效，因為 Claude Code 從 `CLAUDE_CONFIG_DIR` 不影響的位置讀取這些檔案。

當存儲對該會話沒有任何內容時，SDK 改為在您的真實設定目錄下運行，結果取決於您傳遞的選項：

- **`resume`**：兩個 SDK 都將 ID 傳遞給子進程，子進程完全按照沒有存儲的`resume` 方式恢復本地轉錄。
- **TypeScript 中的`continue: true`** ：SDK 啟動新會話。
- **Python 中的`continue_conversation=True`** ：SDK 從最新的本地會話繼續。

### 鏡像寫入是盡力而為

如果 `append()` 拒絕，SDK 會以短暫的退避重試該批次最多兩次，總共最多三次嘗試。超時的呼叫不會重試，因為原始呼叫可能仍然會到達。如果批次仍然失敗，SDK 會記錄錯誤，向迭代器發出 `{ type: "system", subtype: "mirror_error" }` 訊息，丟棄批次，並繼續查詢。因為重試的批次可以重新傳遞已經到達的條目，請在您的 `append()` 實現中按 `entry.uuid` 進行去重。 存儲中斷不會中斷代理，因為子進程首先在本地寫入。如果您需要檢測存儲資料遺失，請監視 `mirror_error`。在[從存儲恢復](https://code.claude.com/docs/zh-TW/agent-sdk/session-storage#resume-from-the-store)的運行上，丟棄的批次在運行結束後沒有倖存的副本。

### `getSessionMessages` 返回後壓縮鏈

`getSessionMessages({ sessionStore })` 返回代理在恢復時會看到的連結訊息鏈。自動壓縮後，較早的轉向被摘要替換，因此存儲持有 503 個原始條目的會話可能從 `getSessionMessages` 返回 18 條訊息。對於完整的原始歷史記錄，包括壓縮前的轉向和中繼資料條目，請直接呼叫 `store.load(key)`。

### `forkSession` 不是位元組副本

`forkSession({ sessionStore })` 讀取來源條目，重寫每個 `sessionId` 欄位並重新映射訊息 UUID，然後在新鍵下附加轉換後的條目。適配器層級的副本或 `CopyObject` 快捷方式會產生仍然參考舊會話 ID 的轉錄，因此 SDK 不使用它。

### 子代理轉錄

子代理轉錄在 `subpath: "subagents/agent-<id>"` 下鏡像。`listSubagents({ sessionStore })` 要求適配器實現 `listSubkeys`；`getSubagentMessages({ sessionStore })` 在可用時使用它，但在未定義時回退到直接子路徑。恢復也呼叫 `listSubkeys` 來還原子代理檔案；沒有它，只有主轉錄被具體化。

### 保留

SDK 永遠不會自行從您的存儲中刪除。保留是適配器的責任：根據您的合規要求實現 TTL、S3 生命週期原則或排程清理。`CLAUDE_CONFIG_DIR` 下的本地轉錄由 `cleanupPeriodDays` 設定獨立清掃，遵循[保留清掃規則](https://code.claude.com/docs/zh-TW/claude-directory#cleaned-up-automatically)。[從存儲恢復](https://code.claude.com/docs/zh-TW/agent-sdk/session-storage#resume-from-the-store)的運行不會留下本地轉錄，因此對於這些運行，您的存儲保留是唯一的保留。

## 支持於

以下 TypeScript SDK 函數接受 `sessionStore` 選項，當提供時針對存儲而不是本地文件系統運行：

- [`query()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#query)
- [`startup()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#startup)
- [`listSessions()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#listsessions)
- [`getSessionInfo()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#getsessioninfo)
- [`getSessionMessages()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#getsessionmessages)
- [`renameSession()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#renamesession)
- [`tagSession()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#tagsession)
- [`deleteSession()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)
- [`forkSession()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)
- [`listSubagents()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)
- [`getSubagentMessages()`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript)

在 Python SDK 中，在 [`ClaudeAgentOptions`](https://code.claude.com/docs/zh-TW/agent-sdk/python#claudeagentoptions) 中設定 `session_store` 以針對存儲運行 `query()`。其餘操作各有一個以存儲作為引數的存儲支持 Python 函數：`list_sessions_from_store()`、`get_session_info_from_store()`、`get_session_messages_from_store()`、`list_subagents_from_store()`、`get_subagent_messages_from_store()`、`rename_session_via_store()`、`tag_session_via_store()`、`delete_session_via_store()` 和 `fork_session_via_store()`。`startup()` 沒有 Python 等效項。[Python SDK 參考](https://code.claude.com/docs/zh-TW/agent-sdk/python#functions)中記錄的獨立函數（例如 `list_sessions()`）讀取本地工作階段檔案。

## 相關資源

- [使用會話](https://code.claude.com/docs/zh-TW/agent-sdk/sessions)：在沒有自定義存儲的情況下繼續、恢復和分叉
- [託管 SDK](https://code.claude.com/docs/zh-TW/agent-sdk/hosting)：多主機環境的部署模式
- [TypeScript `Options`](https://code.claude.com/docs/zh-TW/agent-sdk/typescript#options)：完整選項參考
- [參考實作](https://code.claude.com/docs/zh-TW/agent-sdk/session-storage#reference-implementations)：物件存儲、鍵值存儲和資料庫的可運行範例適配器，位於兩個 SDK 儲存庫中

是否 助手
