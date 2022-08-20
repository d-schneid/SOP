import os
import unittest

import selenium
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTestCase(unittest.TestCase):

    BASE_URL = "http://127.0.0.1:8000/"
    STANDARD_USERNAME_USER = "SeleniumTestUser"
    STANDARD_PASSWORD_USER = "this_is_a_test"
    STANDARD_USERNAME_ADMIN = "SeleniumTestAdmin"
    STANDARD_PASSWORD_ADMIN = "this_is_a_test"

    @classmethod
    def setUpClass(cls) -> None:

        # setup chrome webdriver
        chrome_service = ChromeService(executable_path=ChromeDriverManager().install())

        chrome_options = ChromeOptions()
        chrome_options.headless = True

        cls.driver: selenium.webdriver.Chrome = selenium.webdriver.Chrome(
            service=chrome_service, options=chrome_options
        )

    @classmethod
    def tearDownClass(cls) -> None:
        # stop webdriver
        cls.driver.quit()

    def setUp(self) -> None:
        # get base url
        self.driver.get(SeleniumTestCase.BASE_URL)

        # try to log out
        SeleniumTestCase.logout(self)

    def tearDown(self) -> None:
        # try to log out
        SeleniumTestCase.logout(self)

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

    def upload_dataset(
        self, dataset_path: str, dataset_name: str, dataset_description: str
    ):
        assert os.path.isfile(dataset_path)

        self.driver.find_element(By.LINK_TEXT, "Datasets").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "dataset/overview/sort-by=[a-zA-Z_]+/",
        )

        self.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
        self.assertEqual(
            self.driver.current_url, SeleniumTestCase.BASE_URL + "dataset/upload/"
        )

        self.driver.find_element(By.ID, "id_display_name").send_keys(dataset_name)
        self.driver.find_element(By.ID, "id_description").send_keys(dataset_description)
        absolute_path = os.path.join(os.getcwd(), dataset_path)
        self.driver.find_element(By.ID, "id_path_original").send_keys(absolute_path)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # assert the upload worked
        page_source = self.driver.page_source  # get page source instantly
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "dataset/overview/sort-by=[a-zA-Z_]+/",
        )
        self.assertIn(dataset_name, page_source)
        self.assertIn(dataset_description, page_source)

        # TODO: check maybe visibility of buttons depending on cleaning state
