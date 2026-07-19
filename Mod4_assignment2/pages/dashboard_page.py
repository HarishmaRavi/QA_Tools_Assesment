from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DashboardPage(BasePage):
    HEADER_TITLE = (By.CSS_SELECTOR, ".oxd-topbar-header-breadcrumb h6")
    USER_DROPDOWN = (By.CSS_SELECTOR, ".oxd-userdropdown-tab")
    LOGOUT_LINK = (By.XPATH, "//a[text()='Logout']")

    def is_loaded(self) -> bool:
        return self.is_visible(self.HEADER_TITLE)

    def logout(self):
        self.click(self.USER_DROPDOWN)
        self.click(self.LOGOUT_LINK)
