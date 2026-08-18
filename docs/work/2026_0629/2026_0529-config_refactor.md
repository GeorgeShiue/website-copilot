# Config Refactor (2026/5/29)

本文整理這一輪對 [utils/config_helper.py](utils/config_helper.py) 與 [app/website_crawler_config.py](app/website_crawler_config.py) 的重構設計，重點是把「載入、覆寫、驗證、留檔」拆成可重用的共用流程，並讓 website crawler 的 config 變成更薄的 dataclass 外殼。

## 1. 重構目標

這次重構主要想解決三件事：

1. 多 section config 的載入邏輯分散在各個模組內，容易重複。
2. 載入與覆寫對未知 key 的處理方式不一致，行為容易漂移。
3. `WebsiteCrawlerConfig` 內部的驗證與 wrapper 方法過多，不利維護。

因此目前的方向是：

- 把「section 讀取」與「跨 section 合併」集中到 `config_helper`。
- 把「未知 key 的過濾」統一成同一套 helper。
- 讓 `website_crawler_config.py` 只保留模組自己的欄位定義與驗證規則。

## 2. `config_helper.py` 的設計

`utils/config_helper.py` 現在是 config 系統的共用基礎層，負責處理 TOML I/O、key 過濾、留檔與紀錄。

### 2.1 讀取流程

目前的讀取流程分成兩層：

- `load_config_section_from_toml(config_path, config_section, allowed_keys)`
- `load_config_from_toml(config_path, sections_to_keys)`

前者負責單一 section，後者負責整個模組 config。

單一 section 的流程是：

1. 先確認檔案存在。
2. 再讀取指定 section。
3. section 必須存在，否則丟出 `ConfigNotFoundError`。
4. section 必須是 table，否則丟出 `ConfigInvalidTypeError`。
5. 使用 `_filter_allowed_config_keys` 只保留白名單內的 key。
6. 若有未知 key，記錄 warning，但不讓它們進入最後的 config。

跨 section 的流程則是：

1. 依照 `sections_to_keys` 逐個 section 載入。
2. 每個 section 都先經過相同的 key 過濾。
3. 依序 merge 成單一 dict 回傳。

這樣的設計讓所有模組都能共用同一條 TOML 讀取路徑，而不是各自實作一套不同的 loader。

### 2.2 覆寫流程

`override_config(config, overrides, sections_to_keys)` 是這次新增的多 section 覆寫 helper。

它的設計重點是和載入流程一致：

- 先從 `sections_to_keys` 彙總所有允許的 key。
- 再用 `_filter_allowed_config_keys` 過濾 overrides。
- 最後把有效 overrides merge 回原本的 config。

這樣可以確保「從 TOML 讀進來」與「執行時覆寫」對未知 key 的處理方式完全一致。

### 2.3 留檔流程

`save_module_config_as_toml()` 仍然保留在 helper 層，負責把 module config 寫回 sectioned TOML。

目前的特性是：

- 依 `sections_to_keys` 分 section 寫出。
- 只輸出有列入 metadata 的欄位。
- `config_path` 與 `sections_to_keys` 本身不會被寫入。
- 若有空白 section，會用 residual section 的方式處理，但只支援一個空白 section。

這讓 module config 的序列化規則與載入規則維持對稱。

## 3. `website_crawler_config.py` 的設計

`WebsiteCrawlerConfig` 的重構核心，是把它變成「欄位定義 + 驗證規則 + 少量語意方法」，而不是自己維護整套 config I/O。

### 3.1 目前的資料結構

`WebsiteCrawlerConfig` 現在直接描述 crawler 需要的欄位：

- `url`
- `config_name`
- `max_depth: int | None = None`
- `max_pages`
- `content_threshold`
- `light_mode`
- `wait_for_images`
- `url_patterns`
- `allowed_domains`
- `exclude_words: list[str] | None`

這裡有兩個重要的型態調整：

- `max_depth` 改成可為 `None`，代表不限制深度。
- `exclude_words` 改成 `list[str] | None`，和 TOML/JSON 的自然資料型態對齊。

### 3.2 載入流程

`from_toml()` 現在只做三件事：

1. 組出 `config/website_crawler/{config_name}.toml`。
2. 呼叫 `load_config_from_toml(config_path, SECTIONS_TO_KEYS)`。
3. 套用 runtime overrides，再補上 `config_name`。

也就是說，`website_crawler_config.py` 不再自己拆 section 讀取，也不再維護自己的 section loader wrapper。

這個改動的目的是讓 crawler config 的行為直接依附在共用 helper 上，減少重複與分歧。

### 3.3 覆寫流程

`override_init_config()` 與 `override_crawl_config()` 的最終方向，是交給共用 helper 處理，而不是自己再包一層過濾或合併邏輯。

這代表覆寫時的規則與載入時一致：

- 只接受 `sections_to_keys` 定義過的欄位。
- 未知 key 不會進入最終 config。
- 過濾規則由 `config_helper` 統一維護。

### 3.4 驗證流程

`WebsiteCrawlerConfig` 把原本分散的驗證整併成單一 `_validate_config()`。

驗證仍維持模組專屬的語意檢查，例如：

- `max_depth` 必須是整數或 `None`，且不能小於 0。
- `max_pages` 若有設定，必須大於 0。
- `content_threshold` 必須落在 0 到 1。
- `url` 必須是非空字串。
- `url_patterns`、`allowed_domains`、`exclude_words` 都要符合各自允許的容器與元素型態。

重構的重點不是拿掉驗證，而是把驗證收斂成單一入口，讓資料結構與規則更容易閱讀與修改。

### 3.5 run name

`run_name` 仍然沿用註解驅動的方式：

- 透過 `filter_commented_configs()` 讀取 TOML 中帶有 `run name` 註解的欄位。
- 只把這些欄位串成 run name。

這個設計沒有改變，但現在更容易追蹤：run name 並不是由全部欄位組成，而是由標記過的欄位組成。

## 4. 這次重構後的資料流

目前 website crawler 的 config 流程可以簡化成：

1. `WebsiteCrawlerConfig.from_toml()` 決定 config 檔案位置。
2. `load_config_from_toml()` 依 `sections_to_keys` 載入整份設定。
3. `override_config()` 套用 runtime overrides。
4. `WebsiteCrawlerConfig.__post_init__()` 做模組驗證。
5. `save_module_config_as_toml()` 在執行時把最終 config 留檔。

這條路徑的好處是：

- 讀取與覆寫都走同一套 key 過濾邏輯。
- 模組只保留自己的 business rules。
- TOML 的 section 結構是由 metadata 驅動，而不是由手寫流程驅動。

## 5. 目前的邊界與限制

這次設計也保留了幾個明確邊界：

- `sections_to_keys` 必須存在，否則無法正確載入或留檔。
- `save_module_config_as_toml()` 目前只支援一個 residual section。
- 未知 key 會被忽略並警告，不會自動升級成錯誤。
- `WebsiteCrawlerConfig` 的驗證仍然是模組責任，不會被共用 helper 取代。

這些限制是刻意保留的，目的是讓共用層負責機制，模組層負責語意。

## 6. 結論

這輪重構的本質，是把 config 系統從「各模組自行處理 TOML」整理成「共用 helper 負責 I/O 與 key 規則，模組負責欄位與驗證」。

對 [app/website_crawler_config.py](app/website_crawler_config.py) 來說，結果是 wrapper 減少、驗證集中、型態更貼近實際資料。

對 [utils/config_helper.py](utils/config_helper.py) 來說，結果是 loader 與 override 的行為統一，後續若要擴充其他 config 模組，也能直接沿用。