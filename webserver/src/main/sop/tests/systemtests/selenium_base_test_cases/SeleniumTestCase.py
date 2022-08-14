import unittest

import selenium
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTestCase(unittest.TestCase):

    BASE_URL = "http://127.0.0.1:8000/"

    @classmethod
    def setUpClass(cls) -> None:

        # setup chrome webdriver
        chrome_service = ChromeService(executable_path=ChromeDriverManager().install())

        chrome_options = ChromeOptions()
        chrome_options.headless = True

        cls.driver: selenium.webdriver.Chrome = selenium.webdriver.Chrome(
            service=chrome_service,
            options=chrome_options
        )

        # log in
        cls.driver.get(SeleniumTestCase.BASE_URL)

        # maybe log out first before logging in
        SeleniumTestCase.logout(cls)
        SeleniumTestCase.login(cls, "SeleniumTestUser", "this_is_a_test")

    @classmethod
    def tearDownClass(cls) -> None:
        # log out
        cls.driver.find_element(By.LINK_TEXT, "Logout").click()

        # stop webdriver
        cls.driver.quit()

    @staticmethod
    def logout(cls) -> bool:
        if "Logout" in cls.driver.page_source:
            cls.driver.find_element(By.LINK_TEXT, "Logout").click()
            return True
        else:
            return False

    @staticmethod
    def login(cls, username, password) -> bool:
        if "Login" in cls.driver.page_source:
            cls.driver.find_element(By.LINK_TEXT, "Login").click()
            cls.driver.find_element(By.ID, "id_username").send_keys(username)
            cls.driver.find_element(By.ID, "id_password").send_keys(password)
            cls.driver.find_element(By.ID, "login-button").click()
            return True
        else:
            return False
