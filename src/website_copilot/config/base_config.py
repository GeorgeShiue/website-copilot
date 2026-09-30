"""模組 config 的共用基底類。

- ConfigModel：所有 config（含巢狀 section）的共用基底，設定 strict／extra="forbid"／
  validate_assignment。
- BaseModuleConfig：模組 config 的基底，提供 from_toml() 與 run_name；
  config_name 與 run name 欄位由 loader 設為 PrivateAttr，不參與驗證與 model_dump。

子類必須設定 ClassVar `_CONFIG_FOLDER_PATH`（TOML 設定檔所在目錄）。
巢狀 section 以 ConfigModel 子類宣告，與 TOML 的 [section] 一一對應。
"""

import tomllib
from pathlib import Path
from typing import Annotated, Any, ClassVar, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, PrivateAttr, ValidationError

from website_copilot.utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
)


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

    @property
    def config_name(self) -> str:
        return self._config_name

    @property
    def run_name_fields(self) -> list[str]:
        return self._run_name_fields

    @classmethod
    def config_path(cls, config_name: str) -> Path:
        return Path(cls._CONFIG_FOLDER_PATH) / f"{config_name}.toml"

    @classmethod
    def from_toml(cls, config_name: str = "default", **overrides: Any) -> Self:
        """從 TOML 設定檔建立 config，overrides 為扁平欄位名稱（如 similarity_top_k）。"""
        config_path = cls.config_path(config_name)
        if not config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with config_path.open("rb") as file:
            data = tomllib.load(file)
        cls._apply_flat_overrides(data, overrides, source=str(config_path))

        try:
            config = cls.model_validate(data)
        except ValidationError as e:
            raise ConfigValidationError(
                format_validation_error(str(config_path), e)
            ) from e
        config._config_name = config_name
        config._run_name_fields = filter_commented_configs(str(config_path), "run name")
        return config

    @classmethod
    def _apply_flat_overrides(
        cls, data: dict[str, Any], overrides: dict[str, Any], source: str
    ) -> None:
        """將扁平的 overrides 放到所屬 section（過渡用，Phase C 改為巢狀 overrides）。

        欄位名稱在頂層與各 section 中皆唯一；找不到對應欄位時報錯。
        """
        for key, value in overrides.items():
            if key in cls.model_fields and not _is_section(cls, key):
                data[key] = value
                continue
            sections = [
                name
                for name in cls.model_fields
                if _is_section(cls, name)
                and key in _section_model(cls, name).model_fields
            ]
            if len(sections) != 1:
                raise ConfigValidationError(f"{source}: 未知的 override 欄位：{key}")
            data.setdefault(sections[0], {})[key] = value

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
    """欄位型別為 ConfigModel 子類即為 section（對應 TOML 的 [section]）。"""
    annotation = cls.model_fields[name].annotation
    return isinstance(annotation, type) and issubclass(annotation, ConfigModel)
