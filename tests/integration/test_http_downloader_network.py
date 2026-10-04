"""HttpDownloader 對真實站點的下載（network：連網但不產生費用）。"""

import pytest

from website_copilot.utils.http_downloader import HttpDownloader

# ncucsie 的下載 API：URL 無副檔名，回應為 application/octet-stream，檔名在 Content-Disposition
NCUCSIE_DOWNLOADFILE = (
    "https://www.csie.ncu.edu.tw/app/index.php?Action=downloadfile"
    "&file=WVhSMFlXTm9MelUzTDNCMFlWOHhOemt6WHpRNU1URXpOalJmTVRVNU56SXVjR1Jt"
)


@pytest.mark.network
def test_download_ncucsie_downloadfile_link() -> None:
    downloader = HttpDownloader(
        max_concurrency=2, timeout=30.0, max_retries=2, max_bytes=50 * 1024 * 1024
    )

    result = downloader.download([NCUCSIE_DOWNLOADFILE])[NCUCSIE_DOWNLOADFILE]

    assert result.ok, result.error
    assert result.status_code == 200
    assert "content-disposition" in result.headers
    assert result.content is not None
    assert result.content.startswith(b"%PDF")
