"""
Assignment 4 - Selenium Automation
Validates login functionality.

NOTE: No real Cisco Wireless Controller was available for this exercise.
The-Internet (https://the-internet.herokuapp.com/login) is a public demo
site built specifically for Selenium practice and follows the same
login -> dashboard workflow. Swap LOGIN_URL / locators for the real
Cisco WLC Web UI when access is available - the flow stays identical.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://the-internet.herokuapp.com/login"
USERNAME = "tomsmith"
PASSWORD = "SuperSecretPassword!"


def test_login_flow():
    # 1. Open browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    try:
        # 2. Navigate to URL
        driver.get(LOGIN_URL)

        # 3. Enter username
        username_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        username_field.send_keys(USERNAME)

        # 4. Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(PASSWORD)

        # 5. Click Login
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # 6. Verify Dashboard (post-login page)
        success_banner = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#flash"))
        )
        assert "You logged into a secure area" in success_banner.text
        print("PASS: Login successful, dashboard/secure area verified.")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_login_flow()
