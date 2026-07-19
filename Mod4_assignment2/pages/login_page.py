from selenium.webdriver.common.by import By
from pages.base_page import BasePage

# NOTE: No real internal login system was provided, so the OrangeHRM
# public demo (built specifically for Selenium framework practice) is
# used here. Swap URL/locators for the real target app when available.
LOGIN_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"


class LoginPage(BasePage):
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_ALERT = (By.CSS_SELECTOR, ".oxd-alert-content-text")

    def open(self):
        self.driver.get(LOGIN_URL)
        return self

    def login(self, username: str, password: str):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
