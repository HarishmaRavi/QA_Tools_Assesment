import os
import pytest
from utils.driver_factory import get_driver
from utils.logger_config import get_logger

logger = get_logger("conftest")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def pytest_addoption(parser):
    # Configurable browser execution: pytest --browser=firefox
    parser.addoption("--browser", action="store", default="chrome",
                      help="Browser to run tests on: chrome or firefox")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    logger.info(f"Launching browser: {browser}")
    drv = get_driver(browser)
    yield drv
    logger.info("Closing browser")
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Takes a screenshot automatically whenever a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{item.name}.png")
            driver.save_screenshot(screenshot_path)
            logger.error(f"Test '{item.name}' FAILED. Screenshot saved: {screenshot_path}")
