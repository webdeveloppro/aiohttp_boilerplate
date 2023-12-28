import json
import logging
# import mock

# from aiohttp_boilerplate.test_utils import E2ETestCase
from aiohttp_boilerplate.logging import get_logger

def test_error_log(capsys):
    logger = get_logger("tests", logging.INFO, format="json", stack_info=False, stacklevel=0)

    logger.error(
        "Exception when render document",
        "Test error: variable XYZ not defined",
    )

    result_log = json.loads(capsys.readouterr().err)
    del result_log['time']

    expected_results = {
        "message": "Exception when render document",
        "component": "tests",
        "serviceContext": {},
        "error": "Test error: variable XYZ not defined",
        "severity": "ERROR"
    }

    assert result_log == expected_results

def test_info_log(capsys):
    logger = get_logger("tests", logging.INFO, format="json", stack_info=False, stacklevel=0)

    logger.info("Hello world!")

    result_log = json.loads(capsys.readouterr().err)
    del result_log['time']

    expected_results = {
        "message": "Hello world!",
        "component": "tests",
        "serviceContext": {},
        "severity": "INFO"
    }

    assert result_log == expected_results

def test_warning_log_with_extra_info(capsys):
    logger = get_logger(
        "tests",
        logging.INFO,
        format="json",
        stack_info=False,
        stacklevel=0,
        extra_labels={
            "user_id": "123456789",
        }
    )

    logger.info(
        "Upps, something is wrong",
        "Error: request timeout to stripe"
    )

    result_log = json.loads(capsys.readouterr().err)
    del result_log['time']

    expected_results = {
        "message": "Upps, something is wrong",
        "error": "Error: request timeout to stripe",
        "component": "tests",
        "serviceContext": {
            "user_id": "123456789",
        },
        "severity": "INFO"
    }

    assert result_log == expected_results