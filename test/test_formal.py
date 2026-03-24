import logging

from main import main

logger = logging.getLogger(__name__)


def test_main():
    main(max_pages=10)  # test
