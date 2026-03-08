import os
import re
import shutil

from pathlib import Path
from urllib.parse import urlparse


class MdFileManager:
    @staticmethod
    def _first_heading_from_md(content: str) -> str | None:
        """從 markdown 內容取第一個 ATX 標題（# 開頭）文字，無則回傳 None。"""
        for line in content.split("\n"):
            s = line.strip()
            if s.startswith("#"):
                return re.sub(r"^#+\s*", "", s).strip() or None
        return None

    @staticmethod
    def _safe_suffix(s: str, index: int, max_length: int = 80) -> str:
        """將字串截斷並加上編號前綴，作為檔名後半段。"""
        s = (s[:max_length].rstrip("_") if len(s) > max_length else s) or "page"
        return f"{index:03d}_{s}"

    @classmethod
    def _url_to_safe_basename(cls, url: str, index: int, max_length: int = 80) -> str:
        """從 URL path 產生可作為檔名的安全字串。"""
        path = (urlparse(url).path or "/").strip("/") or "index"
        path = re.sub(r"_+", "_", re.sub(r"[^\w\-.]", "_", path)).strip("_")
        return cls._safe_suffix(path, index, max_length)

    @classmethod
    def _title_to_safe_basename(cls, raw: str, index: int, max_length: int = 80) -> str:
        """將標題轉成可作為檔名的安全字串。"""
        s = (raw or "").strip()
        s = re.sub(r"[^\w\s\-.]", "", s)
        s = re.sub(r"_+", "_", re.sub(r"\s+", "_", s).strip("_"))
        return cls._safe_suffix(s, index, max_length)

    # ----- 對外 API -----
    @staticmethod
    def load_md_files(
        directory: str,
        limit: int | None = None,
    ) -> list[str]:
        """從指定目錄讀取 markdown 檔案內容，可選限制數量。"""
        markdown_files = sorted(os.listdir(directory))
        if limit is not None:
            markdown_files = markdown_files[:limit]
        markdown_contents = []
        for markdown_file in markdown_files:
            with open(f"{directory}/{markdown_file}", "r") as f:
                markdown_contents.append(f.read())
        return markdown_contents

    @classmethod
    def save_md_files(
        cls,
        directory: str,
        markdown_contents: list[str],
        *,
        filename_prefix: str = "",
    ) -> list[Path]:
        """將 markdown 內容存成 .md 至本地指定目錄。"""
        md_file_paths: list[Path] = []
        if not markdown_contents:
            return md_file_paths
        out_dir = Path(directory)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, content in enumerate(markdown_contents):
            title = cls._first_heading_from_md(content)
            basename = (
                cls._title_to_safe_basename(title, i)
                if title
                else cls._safe_suffix("page", i)
            )
            path = (out_dir / f"{filename_prefix}{basename}").with_suffix(".md")
            path.write_text(content, encoding="utf-8")
            md_file_paths.append(path)
        return md_file_paths
