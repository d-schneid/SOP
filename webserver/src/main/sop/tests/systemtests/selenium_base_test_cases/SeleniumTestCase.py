import datetime
import os
import shutil
from pathlib import Path

import pyod
from bs4 import BeautifulSoup
from django.conf import settings

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from authentication.models import User
from backend.task.execution.AlgorithmLoader import AlgorithmLoader

from experiments.management.commands import pyodtodb

import selenium
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTestCase(StaticLiveServerTestCase):

    STANDARD_USERNAME_USER: str
    STANDARD_PASSWORD_USER: str
    STANDARD_USERNAME_ADMIN: str
    STANDARD_PASSWORD_ADMIN: str

    MEDIA_DIR_PATH = os.path.join("tests", "systemtests", "media")
    SELENIUM_ERROR_PATH = os.path.join(
        MEDIA_DIR_PATH, "selenium_err_artefacts"
    )

    _PYOD_AGLO_ROOT = settings.ALGORITHM_ROOT_DIR / "pyod_algorithms"

    _BASE_USERNAME_USER = "SeleniumTestUser"
    _BASE_USERNAME_ADMIN = "SeleniumTestAdmin"
    _BASE_PASSWORD = "this_is_a_test"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # add users to the database
        #  generate a unique username
        SeleniumTestCase.STANDARD_USERNAME_USER = SeleniumTestCase._BASE_USERNAME_USER + str(datetime.datetime.now())
        SeleniumTestCase.STANDARD_USERNAME_ADMIN = SeleniumTestCase._BASE_USERNAME_ADMIN + str(datetime.datetime.now())
        assert not User.objects.filter(username=SeleniumTestCase.STANDARD_USERNAME_USER).exists()
        assert not User.objects.filter(username=SeleniumTestCase.STANDARD_USERNAME_ADMIN).exists()

        # set passwords
        SeleniumTestCase.STANDARD_PASSWORD_USER = SeleniumTestCase._BASE_PASSWORD
        SeleniumTestCase.STANDARD_PASSWORD_ADMIN = SeleniumTestCase._BASE_PASSWORD

        #  add them
        User.objects.create_user(
            username=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER
        )
        user_admin = User.objects.create_user(
            username=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN
        )
        user_admin.is_staff = True
        user_admin.is_admin = True
        user_admin.save()

        # add pyod-algos to the database (Code used from pyodtodb command)
        pyod_path = Path(pyod.__path__[0])
        assert not os.path.exists(SeleniumTestCase._PYOD_AGLO_ROOT)

        shutil.copytree(src=pyod_path, dst=SeleniumTestCase._PYOD_AGLO_ROOT)

        AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))

        pyodtodb.rename_algorithm_files_if_needed(SeleniumTestCase._PYOD_AGLO_ROOT / "models")
        pyodtodb.fix_base_detector_imports(SeleniumTestCase._PYOD_AGLO_ROOT / "models")
        pyodtodb.save_algorithms_in_db(SeleniumTestCase._PYOD_AGLO_ROOT / "models")

        # create a media dir for misc. files
        if not os.path.isdir(SeleniumTestCase.SELENIUM_ERROR_PATH):
            os.makedirs(SeleniumTestCase.SELENIUM_ERROR_PATH)

        # setup chrome webdriver
        chrome_service = ChromeService(executable_path=ChromeDriverManager().install())

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--start-maximized")

        cls.driver: selenium.webdriver.Chrome = selenium.webdriver.Chrome(
            service=chrome_service, options=chrome_options
        )

        # setting: wait, if an element is not found
        cls.driver.implicitly_wait(30)

    @classmethod
    def tearDownClass(cls) -> None:
        # stop webdriver
        cls.driver.quit()

        # delete dir of pyod algos
        shutil.rmtree(path=SeleniumTestCase._PYOD_AGLO_ROOT, ignore_errors=True)

        super().tearDownClass()

    def setUp(self) -> None:
        # get base url
        self.driver.get(self.get_base_url())

        # try to log out
        SeleniumTestCase.logout(self)

    def tearDown(self) -> None:
        # if the test failed, take a screenshot and save the page source
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)

        # check if an error has occurred
        if result.errors:
            type = "ERROR"

        # or a failure
        elif result.failures:
            type = "FAILURE"

        else:
            type = None

        # if there is and error, take a screenshot and save the page source
        if type is not None:
            # screenshot
            screenshot_path = os.path.join(
                SeleniumTestCase.SELENIUM_ERROR_PATH,
                "selenium_screenshot_{type}_{method_name}.png",
            ).format(method_name=self._testMethodName, type=type)

            self.driver.save_screenshot(screenshot_path)

            # save page source (original and pretty version)
            page_source_path_base = os.path.join(
                SeleniumTestCase.SELENIUM_ERROR_PATH,
                "selenium_page_source_{type}_{method_name}.html",
            ).format(method_name=self._testMethodName, type=type)

            base_source_parts = page_source_path_base.split(".")

            # save original
            page_source_path_org = (
                base_source_parts[0] + "_org." + base_source_parts[1]
            )

            with open(page_source_path_org, "w") as file:
                file.write(self.driver.page_source)

            # save prettified version
            page_source_path_pretty = (
                base_source_parts[0]
                + "_pretty."
                + base_source_parts[1]
            )

            pretty_source = BeautifulSoup(
                self.driver.page_source, "html.parser"
            ).prettify()
            with open(page_source_path_pretty, "w") as file:
                file.write(pretty_source)

        # try to log out
        SeleniumTestCase.logout(self)

    def get_base_url(self) -> str:
        return self.live_server_url

    def logout(self) -> bool:
        if "Logout" in self.driver.page_source:
            self.driver.find_element(By.LINK_TEXT, "Logout").click()
            return True
        else:
            return False

    def login(self, username, password):
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "id_username").send_keys(username)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.ID, "login-button").click()

        # assert that the login worked
        self.assertTrue(self.driver.current_url in [self.get_base_url(), self.get_base_url() + "/"])

        # check, if links to subpages are in the generated site
        self.assertIn("/experiment/overview", self.driver.page_source)
        self.assertIn("/dataset/overview", self.driver.page_source)
        self.assertIn("/algorithm/overview", self.driver.page_source)

        # logout should be accessible
        self.assertIn("Logout", self.driver.page_source)
        self.assertIn("/logout", self.driver.page_source)

    def upload_dataset(
        self, dataset_path: str, dataset_name: str, dataset_description: str
    ):
        assert os.path.isfile(dataset_path)

        self.driver.find_element(By.LINK_TEXT, "Datasets").click()
        self.assertRegex(
            self.driver.current_url,
            self.get_base_url() + "dataset/overview/sort-by=[a-zA-Z_]+/",
        )

        self.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
        self.assertEqual(
            self.driver.current_url, self.get_base_url() + "dataset/upload/"
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
            self.get_base_url() + "dataset/overview/sort-by=[a-zA-Z_]+/",
        )
        self.assertIn(dataset_name, page_source)
        self.assertIn(dataset_description, page_source)

        # TODO: check maybe visibility of buttons depending on cleaning state
