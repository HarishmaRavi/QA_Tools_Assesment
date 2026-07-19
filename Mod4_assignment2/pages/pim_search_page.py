from selenium.webdriver.common.by import By
from pages.base_page import BasePage

PIM_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList"


class PimSearchPage(BasePage):
    EMPLOYEE_NAME_INPUT = (By.XPATH, "(//div[@class='oxd-autocomplete-text-input']/input)[1]")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    RESULT_TABLE_ROWS = (By.CSS_SELECTOR, ".oxd-table-card")

    def open(self):
        self.driver.get(PIM_URL)
        return self

    def search_employee(self, name: str):
        self.type_text(self.EMPLOYEE_NAME_INPUT, name)
        self.click(self.SEARCH_BUTTON)

    def has_results(self) -> bool:
        return self.is_visible(self.RESULT_TABLE_ROWS)
