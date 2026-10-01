"""模組 config 的共用基底類。

- ConfigModel：所有 config（含巢狀 section）的共用基底，設定 strict／extra="forbid"／
  validate_assignment。
- BaseModuleConfig：模組 config 的基底，提供 from_yaml() 與 run_name；
  config_name、run_name_fields 與來源描述由 loader 設為 PrivateAttr，不參與驗證與 model_dump。

子類必須設定 ClassVar `_CONFIG_FOLDER_PATH`（YAML 設定檔所在目錄）。
巢狀 section 以 ConfigModel 子類宣告，與 YAML 的巢狀 key 一一對應。
"""

from typing import Annotated, Any, ClassVar, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, PrivateAttr, ValidationError

from website_copilot.config.yaml_helper import deep_merge, load_config_dict
from website_copilot.utils.config_helper import ConfigValidationError

RUN_NAME_FIELDS_KEY = "run_name_fields"


def _check_not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("不可為空白字串")
    return value


# 非空字串：只檢查、不改寫值（prompt 等欄位的前後空白須原樣保留）
NonEmptyStr = Annotated[str, AfterValidator(_check_not_blank)]


class ConfigModel(BaseModel):
    """所有 config（含巢狀 section）的共用基底。"""

    model_config = ConfigDict(strict=True, extra="forbid", validate_assignment=True)


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


class BaseModuleConfig(ConfigModel):
    """模組 config 的共用基底類。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = ""

    _config_name: str = PrivateAttr(default="")
    _run_name_fields: list[str] = PrivateAttr(default_factory=list)
    _source: str = PrivateAttr(default="")

    @property
    def config_name(self) -> str:
        return self._config_name

    @property
    def run_name_fields(self) -> list[str]:
        return self._run_name_fields

    @property
    def source(self) -> str:
        """載入來源描述，如 `configs/rag/test.yml (extends: default)`，有套用 overrides 時
        結尾加上 ` + overrides`；未經 loader 建立時為空字串。"""
        return self._source

    @classmethod
    def from_yaml(
        cls, config_name: str = "default", overrides: dict[str, Any] | None = None
    ) -> Self:
        """從 YAML 設定檔（展開 extends）建立 config。

        最上層保留 key `run_name_fields`（dotted path 的 list）取出後不參與驗證。
        overrides 為巢狀 dict（如 `{"retriever": {"similarity_top_k": 20}}`），以與 extends
        相同的 deep merge 疊在最上層（父檔 < 子檔 < overrides），最後只驗證一次。
        """
        loaded = load_config_dict(cls._CONFIG_FOLDER_PATH, config_name)
        data = loaded.data
        run_name_fields = cls._pop_run_name_fields(data, loaded.source)
        source = loaded.source
        if overrides:
            data = deep_merge(data, overrides)
            source = f"{source} + overrides"

        try:
            config = cls.model_validate(data)
        except ValidationError as e:
            raise ConfigValidationError(format_validation_error(source, e)) from e
        config._config_name = config_name
        config._run_name_fields = run_name_fields
        config._source = source
        return config

    @classmethod
    def _pop_run_name_fields(cls, data: dict[str, Any], source: str) -> list[str]:
        """取出並檢查 run_name_fields：必須是 list，且每個 dotted path 都指向模型欄位。"""
        fields = data.pop(RUN_NAME_FIELDS_KEY, None)
        if fields is None:
            return []
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
        if not self._run_name_fields:
            return "default"

        run_name = ""
        for field_path in self._run_name_fields:
            value = self.get_field(field_path)
            if value is not None:
                run_name += f"{field_path.rsplit('.', 1)[-1]}-{value}_"
        run_name = run_name.rstrip("_")
        return self._post_process_run_name(run_name)

    def _post_process_run_name(self, run_name: str) -> str:
        """子類可覆寫以自訂 run_name 的後處理邏輯。"""
        return run_name


def _section_model(cls: type[BaseModel], name: str) -> type[ConfigModel]:
    annotation = cls.model_fields[name].annotation
    assert isinstance(annotation, type) and issubclass(annotation, ConfigModel)
    return annotation


def _is_section(cls: type[BaseModel], name: str) -> bool:
    """欄位型別為 ConfigModel 子類即為 section（對應 YAML 的巢狀 mapping）。"""
    annotation = cls.model_fields[name].annotation
    return isinstance(annotation, type) and issubclass(annotation, ConfigModel)


def _has_field_path(cls: type[BaseModel], dotted_path: str) -> bool:
    """dotted path 的每一段都是模型欄位（中間段必須是 section）。"""
    parts = dotted_path.split(".")
    model: type[BaseModel] = cls
    for i, part in enumerate(parts):
        if part not in model.model_fields:
            return False
        if i < len(parts) - 1:
            if not _is_section(model, part):
                return False
            model = _section_model(model, part)
    return True
