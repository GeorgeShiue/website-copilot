# 專案採用的 Python 程式設計

本文件整理專案已採用的重點 Python 設計，著重語法與標準庫層面（非系統架構）。路徑相對於 `src/website_copilot/`。
環境：Python 3.13（`requires-python >= 3.13.12`）。

## 總覽

| 主題 | 主要位置 | 使用的語法／機制 |
|---|---|---|
| 型別反射與動態建模 | `config/overrides.py` | `get_origin`／`get_args`、`create_model`、`Annotated` |
| 嚴格 config 驗證 | `config/base_config.py` | pydantic `ConfigDict`、`PrivateAttr`、`AfterValidator`、PEP 695 泛型 |
| asyncio 並行控制 | `utils/http_downloader.py`、`ingestion/augmentation/processors/image_captioner.py` | `Semaphore`、`gather`、`as_completed`、`asyncio.run` |
| Context manager | `utils/log_helper.py`、`storage/run_context.py`、`retrieval/registry.py` | `@contextmanager`、`__enter__`／`__exit__`、`ExitStack` |
| dataclass | `ingestion/augmentation/augmenter.py`、`assets.py` | `astuple`、`zip(strict=True)`、`frozen`、`default_factory` |
| 結構化型別與現代型別語法 | `ingestion/augmentation/augmenter.py` 等 | `Protocol`、`Self`、`Literal`、`TYPE_CHECKING` |
| generator | `ingestion/augmentation/collectors.py`、`processors/office_parser.py`、`server/app.py` | `yield`、`yield from`、async generator |
| 閉包與 partial | `ingestion/augmentation/documents.py`、`ingestion/indexing/node_pipeline.py` | 閉包、`functools.partial` |
| 延遲 import 與模組單例 | `ingestion/augmentation/processors/pdf_parser.py`、`cli/__init__.py` | 函式內 import、`global`＋`threading.Lock` |

## 1. 型別反射與動態建模（`config/overrides.py`）

**問題**：config 有數十個欄位，CLI 要能覆寫任一欄位；手寫第二份「欄位全可選」的 model 會與 config 不同步。

**做法**：執行時走訪 `model_fields`，用 `create_model` 遞迴產生 `{Config}Overrides`。

```python
section = _section_type(annotation)
if section is not None:                      # 巢狀 section → 遞迴
    section_overrides = make_overrides_model(section, section_defaults)
    fields[name] = (section_overrides,
                    Field(default_factory=section_overrides, ...))
else:                                        # 葉欄位 → X | None = None
    fields[name] = (Annotated[annotation | None, arg], Field(default=None, ...))
return create_model(f"{model.__name__}Overrides", __base__=OverridesModel, **fields)
```

**運作原理**
- **註解在 runtime 是物件**：`get_origin`／`get_args` 可拆解 `X | None`、`Annotated`、`Literal`、`list[...]`。`X | None` 的 origin 是 `types.UnionType`，`Optional[X]` 的 origin 是 `typing.Union`，兩者都要比對（`_section_type`）。
- **`model_fields`**：`{欄位名: FieldInfo}`，帶有 `annotation`、`default`、`default_factory`、`description`；必填欄位的 `default` 為 `PydanticUndefined`，用來區分「預設 None」與「無預設」。
- **`create_model`**：等同以 `(型別, Field)` 的 namespace 呼叫 `type()` 建立類別。
- **類別是可呼叫物件**：`default_factory=section_overrides` 傳類別本身，每次建立外層實例都得到新的內層實例。
- **`Annotated[X | None, tyro.conf.arg(...)]`**：把 CLI 說明與 metavar 附在型別上，不改變型別本身。

**流程**：`Config` → `model_fields` 逐欄位判斷（section 遞迴／dict 跳過／葉欄位）→ `create_model` → tyro 解析 CLI → `model_dump(exclude_none=True)` → `prune_empty` 清掉空 dict → `deep_merge` 進設定。`prune_empty` 避免未指定的 section（`{}`）蓋掉設定檔的值。

**限制**：`None` 代表「未指定」，CLI 無法把欄位設為 null；`dict[str, Any]` 欄位 tyro 不支援，直接排除。

## 2. 嚴格 config 驗證（`config/base_config.py`）

```python
model_config = ConfigDict(
    strict=True, extra="forbid", validate_assignment=True, validate_default=True
)
```

| 設定 | 效果 |
|---|---|
| `strict=True` | 不做隱式轉型 |
| `extra="forbid"` | YAML 多寫或拼錯的 key 直接報錯 |
| `validate_assignment=True` | 事後賦值也驗證 |
| `validate_default=True` | 預設值本身也驗證 |

- **載入流程**：讀 YAML → 展開 `extends` → 疊上 CLI overrides（父檔 < 子檔 < overrides）→ **只驗證一次**。
- **錯誤處理**：`_format_validation_error` 轉成「來源: 欄位路徑: 訊息」，以 `raise ... from e` 轉成 `ConfigValidationError`，保留因果鏈。
- **`PrivateAttr`**：`_source`、`_config_name`、`_run_name_fields` 記錄載入來源，不參與驗證與 `model_dump()`。
- **`ClassVar`**：`_CONFIG_FOLDER_PATH`、`_DEFAULT_RUN_NAME_FIELDS` 為類別層級常數。
- **`NonEmptyStr = Annotated[str, AfterValidator(...)]`**：可重用的驗證型別，只檢查、不改寫值。
- **PEP 695 泛型**：`def validate_loaded[M: ConfigModel](cls: type[M], ...) -> M`，回傳型別隨傳入的 config 子類而定。
- **dotted path**：`get_field("init.max_depth")` 以 `getattr` 迴圈逐層取值；`_has_field_path` 用 `model_fields` 在載入時預先驗證路徑。

## 3. asyncio 並行控制（`utils/http_downloader.py`）

```python
async with semaphore:                       # 只在「真的發請求」時佔名額
    result, retryable = await self._fetch_once(client, url, attempts)
if result.ok or not retryable or attempts > self.max_retries:
    return result
await asyncio.sleep(self.retry_backoff * 2 ** (attempts - 1))   # 退避在 semaphore 外
```

- **退避不佔名額**：`sleep` 在 `async with semaphore` 之外，等待重試的請求不會降低並行度。
- **分類與政策分離**：`_fetch_once` 回傳 `(result, retryable)`，重試迴圈只依此決定是否重試。
- **順序保證**：`gather` 的結果順序同輸入，搭配 `dict(zip(unique_urls, results, strict=True))` 對回 URL；`dict.fromkeys(urls)` 去重且保序。
- **串流讀取**：`_read_limited` 先看 `content-length`，再串流累計，超過 `max_bytes` 即中止。
- **同步介面**：`download()` 只是 `asyncio.run(self.adownload(...))`。**不可在已有 running loop 的執行緒中呼叫**，async 路徑要用 `adownload`。
- **VLM 描述批次**：`create_task` 加 `as_completed`，完成一個就更新進度條，單一任務失敗只記 warning；semaphore 在每次 `asyncio.run` 內建立（event loop 隨 `asyncio.run` 建立，不可跨呼叫保存）。
- **SSE**：`server/app.py` 的 `_event_stream` 是 `async def` 加 `yield` 的 async generator。

## 4. Context manager

三種寫法對應三種需求：

| 寫法 | 位置 | 情境 |
|---|---|---|
| 類別式 `__enter__`／`__exit__` | `RAGRegistry` | 物件持有資源，提供 `close()` |
| `@contextmanager` | `log_run_time`、`save_logging_file`、`publish_log_file` | 一次性前置／後置流程 |
| `ExitStack` | `run_workflow_context` | 要進入哪些 context 在 runtime 決定 |

**運作原理**
- `with` 協定：`__exit__` 回傳 falsy 則重新拋出例外；`RAGRegistry.__exit__` 回傳 `False`，只清理不吞例外。
- `@contextmanager` 產生 `_GeneratorContextManager`：正常離開時對 generator 再 `next()`；例外時用 `gen.throw()` 把例外丟進 `yield` 那一行。因此 `try/finally` 內的清理兩種情況都會執行，`finally` 之後的程式碼**只有正常離開才執行**。`run_workflow_context` 利用這點，只在成功時印出 complete。
- `ExitStack`：內部堆疊，`enter_context` 時登記 `__exit__`，離開時**後進先出**；中途某個 `__enter__` 失敗，已進入的也會被清理。
- **可重入 tee**（`utils/log_helper.py`）：`sys.stdout` 是可賦值的模組屬性，換成 `_TeeStream` 就能同時寫終端機與檔案；模組層級 `_tee_depth` 計數巢狀呼叫，歸零才還原 stdout 並關檔。用 `global` 是因為函式內賦值模組層級變數需要宣告。此設計非執行緒安全，單執行緒 pipeline 夠用。
- `publish_log_file`：暫存目錄在 `finally` 以 `shutil.rmtree` 清除，成功失敗都不留垃圾。
- `# noqa: SIM115`：長期持有檔案流，刻意不用 `with`，理由寫在旁邊。

## 5. dataclass（`ingestion/augmentation/augmenter.py`、`assets.py`）

```python
@dataclass
class PageStats:
    cost_usd: float = 0.0
    success: int = 0
    ...
    def __add__(self, other: "PageStats") -> "PageStats":
        return PageStats(
            *(a + b for a, b in zip(astuple(self), astuple(other), strict=True))
        )
```

- **欄位順序即 log 表格欄位順序**；新增欄位時 `__add__` 與表格輸出都不用改。
- **原理**：`@dataclass` 依 `__annotations__` 的宣告順序產生 `__init__`／`__repr__`／`__eq__`；`astuple` 依欄位順序展開，`zip` 配對後以 `*` 解包回建構參數；`strict=True` 在長度不一致時立即報錯。
- **`field(default_factory=list)`**：預設值只在定義時求值一次，`dataclass` 直接禁止 `xs: list = []`；`Asset.refs` 以 `default_factory` 避免實例共用。
- **`@property`**：`PageStats.failure` 為衍生值，不佔欄位也不會不同步。
- **`frozen=True`**：`DownloadResult` 等結果物件建立後不可改，並自動產生 `__hash__`。
- **注意**：`astuple` 會遞迴複製巢狀 list／dict／dataclass；目前欄位全是數字沒問題，若新增容器欄位，`__add__` 的語意要重新考慮。

## 6. 結構化型別與現代型別語法

- **`Protocol`**：`Downloader` 只宣告 `download` 簽章；`HttpDownloader` 與測試 fake 都不必繼承。
- **`Self`**：`from_yaml`（classmethod）與 `RAGRegistry.__enter__` 回傳 `Self`，子類得到子類型別。
- **`Literal`**：`Asset.kind: Literal["image", "document"]`。
- **`TYPE_CHECKING`**：`cli/run.py`、`utils/config_helper.py` 只在型別檢查時 import，避免循環引用與載入成本。
- **`Annotated`**：把驗證器或 CLI 參數附在型別上。
- **關鍵字專用參數**：`Augmenter.__init__(self, *, downloader, ...)`。

## 7. generator、閉包與 partial

- **generator**：`iter_markdown_links()` 回傳 `Iterator[tuple[str, str, str]]`；`office_parser.py` 以遞迴 `yield from` 走訪文件樹，不建中間 list。
- **`next(gen, default)`**：`_insert_captions` 用 `iter(range(...))` 當計數器，`next(counter, None)` 處理「佔位符比圖片多」，免 `try/except StopIteration`。
- **閉包**：`_insert_captions` 的 `replace(_match)` 捕捉 `counter`、`urls`，交給 `re.sub` 的 callable 版本，達成「第 n 個佔位符換成第 n 張圖」。
- **`functools.partial`**：`partial(self._build_file_metadata, results_json, site_id=site_id)` 把多參數函式適配成 LlamaIndex 期望的單參數 callback。
- **walrus**：`recoverable_failures` 在推導式條件內 `(entry := self._entries.get(asset.url)) is not None`，一次 `get` 同時完成過濾與取值。

## 8. 延遲 import 與模組單例

- **CLI 子命令延遲 import**（`cli/__init__.py`）：頂層只 import 參數用的 dataclass，執行邏輯在 `main()` 內才 import，避免例如 `serve` 間接載入爬蟲依賴。
- **重依賴延遲建立**（`processors/pdf_parser.py`）：`docling` 在 `_get_converter()` 內才 import；`_converter` 為模組層級單例，以 `global` 加 `threading.Lock` 保護，並在 docstring 註明「呼叫端須持有 `_lock`」。

## 9. 其他慣例

- `zip(strict=True)`、`dict.fromkeys`、`dict.setdefault`（「第一個勝出」）、`str.removesuffix`、`endswith(tuple)`。
- 模組層級 `re.compile` 常數；長 pattern 以相鄰字串字面值拼接並逐段註解；`re.sub` 搭配 callable。
- `PurePosixPath` 處理 URL path，不依賴作業系統分隔符。
- `__all__` 明確宣告公開介面；底線前綴區分私有 helper，並以 `undersort` 在 CI 強制 class 方法排序。
- 自訂例外階層：`ConfigValidationError(ValueError)`、`DocumentParseError`、`UnsupportedModelError` 等。
