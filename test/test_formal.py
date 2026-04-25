from main import main
from utils.log_helper import setup_logging

setup_logging("debug")


def test_main():
    main(max_pages=10)  # test
