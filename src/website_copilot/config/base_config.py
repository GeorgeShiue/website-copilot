"""模組 config 的共用基底類。

- ConfigModel：所有 config（含巢狀 section）的共用基底，設定 strict／extra="forbid"／
  validate_assignment／validate_default。
- BaseModuleConfig：模組 config 的基底，提供 from_yaml() 與 run_name；
  config_name、run_name_fields 與來源描述由 loader 設為 PrivateAttr，不參與驗證與 model_dump。

欄位預設值為唯一的預設值來源，設定檔只寫與預設值不同的部分；不經設定檔也可直接建立
（如 `RetrieverConfig()`）。巢狀 section 以 ConfigModel 子類宣告，與 YAML 的巢狀 key 一一對應。

子類必須設定 ClassVar：
- `_CONFIG_FOLDER_PATH`：YAML 設定檔所在目錄。
- `_DEFAULT_RUN_NAME_FIELDS`（可選）：設定檔未寫 `run_name_fields` 時使用的 run name 欄位。
"""

from pathlib import Path
from typing import Annotated, Any, ClassVar, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, PrivateAttr, ValidationError

from website_copilot.config.yaml_helper import (
    CONFIG_SUFFIX,
    deep_merge,
    load_config_dict,
)
from website_copilot.utils.config_helper import ConfigValidationError

RUN_NAME_FIELDS_KEY = "run_name_fields"
DEFAULT_CONFIG_NAME = "default"


def _check_not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("不可為空白字串")
    return value


# 非空字串：只檢查、不改寫值（prompt 等欄位的前後空白須原樣保留）
NonEmptyStr = Annotated[str, AfterValidator(_check_not_blank)]


class ConfigModel(BaseModel):
    """所有 config（含巢狀 section）的共用基底。"""

    # validate_default：預設值也經過驗證（含跨欄位規則），避免誤寫的預設值靜默通過
    model_config = ConfigDict(
        strict=True, extra="forbid", validate_assignment=True, validate_default=True
    )


def format_validation_error(source: str, error: ValidationError) -> str:
    """將 pydantic 的 ValidationError 轉成「來源: 欄位路徑: 訊息」的多行字串。"""
    lines = []
    for err in error.errors():
        loc = ".".join(str(part) for part in err["loc"])
        # 自訂 validator 的 ValueError 會被加上 "Value error, " 前綴，改用原始訊息
        if err["type"] == "value_error" and "ctx" in err:
            message = str(err["ctx"]["error"])
        else:
            message = err["msg"]
        lines.append(f"{source}: {loc}: {message}" if loc else f"{source}: {message}")
    return "\n".join(lines)


def validate_loaded[M: ConfigModel](
    cls: type[M], data: dict[str, Any], source: str
) -> M:
    """驗證載入的設定 dict；失敗時轉成帶來源（設定檔路徑與繼承鏈）的 ConfigValidationError。"""
    try:
        return cls.model_validate(data)
    except ValidationError as e:
        raise ConfigValidationError(format_validation_error(source, e)) from e


class LoadedConfigModel(ConfigModel):
    """由 YAML loader 建立的 config 基底：記錄載入來源（不參與驗證與 model_dump）。"""

    _source: str = PrivateAttr(default="")

    @property
    def source(self) -> str:
        """載入來源描述，如 `configs/rag/test.yml (extends: default)`；未經 loader 建立時為空字串。"""
        return self._source


class BaseModuleConfig(LoadedConfigModel):
    """模組 config 的共用基底類。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = ""
    _DEFAULT_RUN_NAME_FIELDS: ClassVar[tuple[str, ...]] = ()

    _config_name: str = PrivateAttr(default="")
    # None：使用 class 的 _DEFAULT_RUN_NAME_FIELDS（設定檔未寫或未經 loader 建立）
    _run_name_fields: list[str] | None = PrivateAttr(default=None)

    @property
    def config_name(self) -> str:
        return self._config_name

    @property
    def run_name_fields(self) -> list[str]:
        if self._run_name_fields is None:
            return list(self._DEFAULT_RUN_NAME_FIELDS)
        return self._run_name_fields

    @classmethod
    def from_yaml(
        cls, config_name: str = "default", overrides: dict[str, Any] | None = None
    ) -> Self:
        """從 YAML 設定檔（展開 extends）建立 config，設定檔未寫的欄位使用欄位預設值。

        最上層保留 key `run_name_fields`（dotted path 的 list）取出後不參與驗證。
        overrides 為巢狀 dict（如 `{"retriever": {"similarity_top_k": 20}}`），以與 extends
        相同的 deep merge 疊在最上層（父檔 < 子檔 < overrides），最後只驗證一次。

        `default` 的設定檔可省略：檔案不存在時等於欄位預設值（其他名稱找不到檔案時報錯；
        `extends: default` 指向不存在的檔案時也照舊報錯）。
        """
        data, source = cls._load(config_name)
        run_name_fields = cls._pop_run_name_fields(data, source)
        if overrides:
            data = deep_merge(data, overrides)
            source = f"{source} + overrides"

        config = validate_loaded(cls, data, source)
        config._config_name = config_name
        config._run_name_fields = run_name_fields
        config._source = source
        return config

    @classmethod
    def _load(cls, config_name: str) -> tuple[dict[str, Any], str]:
        """讀取設定檔（展開 extends），回傳 (設定 dict, 來源描述)。"""
        path = Path(cls._CONFIG_FOLDER_PATH) / f"{config_name}{CONFIG_SUFFIX}"
        if config_name == DEFAULT_CONFIG_NAME and not path.is_file():
            return {}, f"{cls.__name__} 預設值（{path} 不存在）"
        loaded = load_config_dict(cls._CONFIG_FOLDER_PATH, config_name)
        return loaded.data, loaded.source

    @classmethod
    def _pop_run_name_fields(
        cls, data: dict[str, Any], source: str
    ) -> list[str] | None:
        """取出並檢查 run_name_fields：必須是 list，且每個 dotted path 都指向模型欄位。

        未寫時回傳 None（使用 class 的 _DEFAULT_RUN_NAME_FIELDS）。
        """
        if RUN_NAME_FIELDS_KEY not in data:
            return None
        fields = data.pop(RUN_NAME_FIELDS_KEY)
        if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            raise ConfigValidationError(
                f"{source}: {RUN_NAME_FIELDS_KEY} 必須是 dotted path 字串的 list"
            )
        for field_path in fields:
            if not _has_field_path(cls, field_path):
                raise ConfigValidationError(
                    f"{source}: {RUN_NAME_FIELDS_KEY}: 找不到欄位 {field_path}"
                )
        return fields

    def get_field(self, dotted_path: str) -> Any:
        """以 dotted path（如 "init.max_depth"）取得巢狀欄位值。"""
        value: Any = self
        for part in dotted_path.split("."):
            value = getattr(value, part)
        return value

    @property
    def run_name(self) -> str:
        """根據 run name 欄位生成 run name（以最後一段欄位名組成，如 max_depth-2）。"""
        run_name_fields = self.run_name_fields
        if not run_name_fields:
            return "default"

        run_name = ""
        for field_path in run_name_fields:
            value = self.get_field(field_path)
            if value is not None:
                run_name += f"{field_path.rsplit('.', 1)[-1]}-{value}_"
        run_name = run_name.rstrip("_")
        return self._post_process_run_name(run_name)

    def _post_process_run_name(self, run_name: str) -> str:
        """子類可覆寫以自訂 run_name 的後處理邏輯。"""
        return run_name


def _has_field_path(cls: type[BaseModel], dotted_path: str) -> bool:
    """dotted path 的每一段都是模型欄位（中間段必須是 section）。

    section 為欄位型別恰為 ConfigModel 子類者（對應 YAML 的巢狀 mapping）；
    可選 section（`Model | None`）可能是 None，不能作為路徑中段。
    """
    parts = dotted_path.split(".")
    model: type[BaseModel] = cls
    for i, part in enumerate(parts):
        if part not in model.model_fields:
            return False
        if i < len(parts) - 1:
            annotation = model.model_fields[part].annotation
            if not (
                isinstance(annotation, type) and issubclass(annotation, ConfigModel)
            ):
                return False
            model = annotation
    return True
