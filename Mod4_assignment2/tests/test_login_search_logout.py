from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.pim_search_page import PimSearchPage
from utils.logger_config import get_logger

logger = get_logger("test_login_search_logout")

VALID_USERNAME = "Admin"
VALID_PASSWORD = "admin123"


def test_login_search_logout(driver):
    # ---- LOGIN ----
    logger.info("Starting login step")
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(VALID_USERNAME, VALID_PASSWORD)

    dashboard = DashboardPage(driver)
    assert dashboard.is_loaded(), "Dashboard did not load after login"
    logger.info("Login successful, dashboard loaded")

    # ---- SEARCH ----
    logger.info("Starting search step")
    pim_page = PimSearchPage(driver)
    pim_page.open()
    pim_page.search_employee("a")  # broad search, letter 'a' should return results
    assert pim_page.has_results(), "No search results returned"
    logger.info("Search returned results successfully")

    # ---- LOGOUT ----
    logger.info("Starting logout step")
    dashboard.logout()
    login_page_after = LoginPage(driver)
    assert login_page_after.is_visible(LoginPage.USERNAME_INPUT), "Did not return to login page after logout"
    logger.info("Logout successful, back at login page")
