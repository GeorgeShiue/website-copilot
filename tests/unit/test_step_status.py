"""StepStatus：與舊的裸字串狀態值相容，且能擋住不合法的值。"""

import pytest

from website_copilot.ingestion.augmentation.augmenter import ImageEntry
from website_copilot.ingestion.augmentation.documents import DocumentEntry
from website_copilot.ingestion.augmentation.status import StepStatus


def test_values_equal_legacy_strings() -> None:
    assert StepStatus.SUCCESS == "success"
    assert StepStatus.FAILED == "failed"
    assert StepStatus.PENDING == ""
    assert {"success": 1}[StepStatus.SUCCESS] == 1


def test_pending_is_falsy_and_others_truthy() -> None:
    assert not StepStatus.PENDING
    assert StepStatus.SUCCESS
    assert StepStatus.FAILED


def test_invalid_value_raises() -> None:
    with pytest.raises(ValueError):
        StepStatus("sucess")


def test_entries_start_pending() -> None:
    image, document = ImageEntry(), DocumentEntry()

    assert image.download_status is StepStatus.PENDING
    assert image.summarize_status is StepStatus.PENDING
    assert document.download_status is StepStatus.PENDING
