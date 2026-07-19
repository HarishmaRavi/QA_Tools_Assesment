"""
Configurable browser execution: pass --browser=chrome or --browser=firefox
when running pytest, e.g.  pytest --browser=firefox
Defaults to chrome if not specified.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def get_driver(browser: str = "chrome"):
    browser = (browser or "chrome").lower()

    if browser == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)
    else:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

    driver.maximize_window()
    driver.implicitly_wait(0)  # explicit waits are used instead, see pages/
    return driver
