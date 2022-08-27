import copy
import datetime
from enum import Enum
import os
import re
import shutil
from pathlib import Path
from time import sleep

import pyod
from bs4 import BeautifulSoup
from django.conf import settings

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from authentication.models import User
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from experiments.management.commands import pyodtodb

from tests.generic import MediaMixin

import selenium
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


def _add_users_to_db():
    #  generate a unique username
    SeleniumTestCase.STANDARD_USERNAME_USER = (
        SeleniumTestCase._BASE_USERNAME_USER
    )
    SeleniumTestCase.STANDARD_USERNAME_ADMIN = (
        SeleniumTestCase._BASE_USERNAME_ADMIN
    )
    assert not User.objects.filter(
        username=SeleniumTestCase.STANDARD_USERNAME_USER
    ).exists()
    assert not User.objects.filter(
        username=SeleniumTestCase.STANDARD_USERNAME_ADMIN
    ).exists()

    # set passwords
    SeleniumTestCase.STANDARD_PASSWORD_USER = SeleniumTestCase._BASE_PASSWORD
    SeleniumTestCase.STANDARD_PASSWORD_ADMIN = SeleniumTestCase._BASE_PASSWORD

    #  add them
    User.objects.create_user(
        username=SeleniumTestCase.STANDARD_USERNAME_USER,
        password=SeleniumTestCase.STANDARD_PASSWORD_USER,
    )
    user_admin = User.objects.create_user(
        username=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
        password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
    )
    user_admin.is_staff = True
    user_admin.is_superuser = True
    user_admin.save()


def _add_pyod_algos_to_db():
    # code was taken from pyodtodb command
    #  the command itself was not used directly as it was not possible without
    #  bigger restructuring of the production code

    # add a new attribute, which is a deepcopy of the attribute PYOD_ALGORITHMS
    # so the original values are saved
    # (and the original attribute can be reset, s. below)
    # as the renaming will not work otherwise (after the first time)
    setattr(pyodtodb, "ORG_PYOD_DATA", copy.deepcopy(pyodtodb.PYOD_ALGORITHMS))

    pyod_path = Path(pyod.__path__[0])
    assert not os.path.exists(SeleniumTestCase.PYOD_AGLO_ROOT)

    shutil.copytree(src=pyod_path, dst=SeleniumTestCase.PYOD_AGLO_ROOT)

    AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))

    pyodtodb.rename_algorithm_files_if_needed(
        SeleniumTestCase.PYOD_AGLO_ROOT / "models"
    )
    pyodtodb.fix_base_detector_imports(SeleniumTestCase.PYOD_AGLO_ROOT / "models")
    pyodtodb.save_algorithms_in_db(SeleniumTestCase.PYOD_AGLO_ROOT / "models")

    # reset the original attribute
    pyodtodb.PYOD_ALGORITHMS = pyodtodb.ORG_PYOD_DATA


class SeleniumTestCase(StaticLiveServerTestCase, MediaMixin):
    class UrlsSuffixRegex(Enum):
        _ignore_ = [
            "_pattern_overview",
            "_pattern_create",
            "_pattern_upload",
            "_admin_base",
            "_admin_authentication",
            "_admin_authentication_user",
        ]

        _pattern_overview: str = "{topic}/overview/sort\-by=[A-Za-z_]+"
        _pattern_create: str = "{topic}/create"
        _pattern_upload: str = "{topic}/upload"
        _admin_base: str = "admin"
        _admin_authentication: str = _admin_base + "/authentication"
        _admin_authentication_user: str = _admin_authentication + "/user"

        LOGIN = "login"
        HOMEPAGE = ""
        DATASET_OVERVIEW = _pattern_overview.format(topic="dataset")
        EXPERIMENT_OVERVIEW = _pattern_overview.format(topic="experiment")
        EXPERIMENT_CREATE = _pattern_create.format(topic="experiment")
        EXECUTION_CREATE = "experiment/[0-9]+/execution/create"
        ALGORITHM_OVERVIEW = _pattern_overview.format(topic="algorithm")
        ALGORITHM_UPLOAD = _pattern_upload.format(topic="algorithm")
        DATASET_UPLOAD = _pattern_upload.format(topic="dataset")
        ADMIN_BASE = _admin_base
        ADMIN_AUTHENTICATION_USER = _admin_authentication_user
        ADMIN_AUTHENTICATION_USER_ADD = _admin_authentication_user + "/add"
        ADMIN_AUTHENTICATION_USER_CHANGE = _admin_authentication_user + "/[0-9]+/change"

    STANDARD_USERNAME_USER: str
    STANDARD_PASSWORD_USER: str
    STANDARD_USERNAME_ADMIN: str
    STANDARD_PASSWORD_ADMIN: str

    MEDIA_DIR_PATH = os.path.join("tests", "systemtests", "media")
    SELENIUM_ERROR_PATH = os.path.join(MEDIA_DIR_PATH, "selenium_err_artefacts")
    PYOD_AGLO_ROOT = settings.ALGORITHM_ROOT_DIR / "pyod_algorithms"

    _BASE_USERNAME_USER = "SeleniumTestUser"
    _BASE_USERNAME_ADMIN = "SeleniumTestAdmin"
    _BASE_PASSWORD = "this_is_a_test"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

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

        super().tearDownClass()

    def setUp(self) -> None:
        # add users to db
        _add_users_to_db()

        # import pyod algos
        _add_pyod_algos_to_db()

        # get base url
        self.driver.get(self.get_base_url())

        # try to log out
        SeleniumTestCase.logout(self)

    def tearDown(self) -> None:
        # delete dir of pyod algos
        shutil.rmtree(path=SeleniumTestCase.PYOD_AGLO_ROOT)

        # if the test failed, take a screenshot and save the page source
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)

        # check if an error has occurred
        if result.errors:
            err_type = "ERROR"
        # or a failure
        elif result.failures:
            err_type = "FAILURE"
        else:
            err_type = None

        # if there is and error, take a screenshot and save the page source
        if err_type is not None:
            # screenshot
            screenshot_path = os.path.join(
                SeleniumTestCase.SELENIUM_ERROR_PATH,
                "selenium_screenshot_{err_type}_{method_name}.png",
            ).format(method_name=self._testMethodName, err_type=err_type)

            self.driver.save_screenshot(screenshot_path)

            # save page source (original and pretty version)
            page_source_path_base = os.path.join(
                SeleniumTestCase.SELENIUM_ERROR_PATH,
                "selenium_page_source_{err_type}_{method_name}.html",
            ).format(method_name=self._testMethodName, err_type=err_type)

            base_source_parts = page_source_path_base.split(".")

            # save original
            page_source_path_org = base_source_parts[0] + "_org." + base_source_parts[1]

            with open(page_source_path_org, "w") as file:
                file.write(self.driver.page_source)

            # save prettified version
            page_source_path_pretty = (
                base_source_parts[0] + "_pretty." + base_source_parts[1]
            )

            pretty_source = BeautifulSoup(
                self.driver.page_source, "html.parser"
            ).prettify()
            with open(page_source_path_pretty, "w") as file:
                file.write(pretty_source)

        # try to log out
        SeleniumTestCase.logout(self)

    # ------------ Helper Methods -----------------

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
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.HOMEPAGE)

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
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_OVERVIEW)

        self.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_UPLOAD)

        self.driver.find_element(By.ID, "id_display_name").send_keys(dataset_name)
        self.driver.find_element(By.ID, "id_description").send_keys(dataset_description)
        absolute_path = os.path.join(os.getcwd(), dataset_path)
        self.driver.find_element(By.ID, "id_path_original").send_keys(absolute_path)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # assert the upload worked
        page_source = self.driver.page_source  # get page source instantly
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_OVERVIEW)
        self.assertIn(dataset_name, page_source)
        self.assertIn(dataset_description, page_source)

        # TODO: check maybe visibility of buttons depending on cleaning state
        # TODO: check directly in the database, if the dataset was added correctly

    def wait_until_dataset_cleaned(self, dataset_name: str):

        start_time = datetime.datetime.now()  # TODO: debug

        while True:
            sleep(1)
            dataset_div = self.driver.find_element(
                By.XPATH,
                "//a[normalize-space(text()) = '" +
                dataset_name +
                "']/parent::*/following-sibling::a"
            )
            if dataset_div.text == "cleaned":
                break

            print("Dataset: " + dataset_name + ", Status: "
                  + dataset_div.text + " | Time: "
                  + str(datetime.datetime.now() - start_time)
                  + " | " + self.driver.current_url
                  )  # TODO: debug

    # -------------- Additional asserts -----------

    def assertUrlMatches(self, url_suffix_regex: UrlsSuffixRegex):
        prefix_slash: str = "/?"
        suffix_slash: str = "/?"

        if url_suffix_regex.value == "":
            url_suffix_regex_pattern = prefix_slash
        else:
            url_suffix_regex_pattern = (
                prefix_slash + url_suffix_regex.value + suffix_slash
            )

        url_pattern_full = re.escape(self.get_base_url()) + url_suffix_regex_pattern

        self.assertRegex(self.driver.current_url, url_pattern_full)
