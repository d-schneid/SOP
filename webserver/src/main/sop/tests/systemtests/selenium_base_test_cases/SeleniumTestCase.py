import datetime
import os
import re
import shutil
from enum import Enum
from time import sleep

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from tests.systemtests.selenium_base_test_cases import SeleniumTestHelper


class SeleniumTestCase(StaticLiveServerTestCase):
    class UrlsSuffixRegex(Enum):
        _ignore_ = [
            "_pattern_overview",
            "_pattern_create",
            "_pattern_upload",
            "_admin_base",
            "_admin_authentication",
            "_admin_authentication_user",
        ]

        _pattern_overview: str = "{topic}/overview/sort-by=[A-Za-z_]+"
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

    BROWSER_ENV_VAR_NAME = "SELENIUM_BROWSER"
    BROWSER_ENV_VAR_VALUE_FIREFOX = "firefox"
    BROWSER_ENV_VAR_VALUE_CHROME = "chrome"
    SCHEDULER_ENV_VAR_NAME = "SELENIUM_SCHEDULER"
    SCHEDULER_ENV_VAR_VALUE_DEBUG = "debug"
    SCHEDULER_ENV_VAR_VALUE_REAL = "production"

    _BASE_USERNAME_USER = "SeleniumTestUser"
    _BASE_USERNAME_ADMIN = "SeleniumTestAdmin"
    _BASE_PASSWORD = "this_is_a_test"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # create a media dir for misc. files
        if not os.path.isdir(SeleniumTestCase.SELENIUM_ERROR_PATH):
            os.makedirs(SeleniumTestCase.SELENIUM_ERROR_PATH)

        # setting up the Webdriver
        cls.driver = SeleniumTestHelper.initialize_the_webdriver(
            browser_env_var_name=SeleniumTestCase.BROWSER_ENV_VAR_NAME,
            browser_value_firefox=SeleniumTestCase.BROWSER_ENV_VAR_VALUE_FIREFOX,
            browser_value_chrome=SeleniumTestCase.BROWSER_ENV_VAR_VALUE_CHROME,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        # stop webdriver
        cls.driver.quit()

        super().tearDownClass()

    def setUp(self) -> None:
        # delete old dirs
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        assert not os.path.isdir(settings.MEDIA_ROOT)

        # depending on the environment variables, run with the debug scheduler
        if (
            os.environ.get(
                SeleniumTestCase.SCHEDULER_ENV_VAR_NAME,
                SeleniumTestCase.SCHEDULER_ENV_VAR_VALUE_DEBUG,
            )
            == SeleniumTestCase.SCHEDULER_ENV_VAR_VALUE_REAL
        ):
            print("[Selenium Tests]  Running with normal, production Scheduler")
        else:
            Scheduler.default_scheduler = DebugScheduler
            print("[Selenium Tests]  Running with DebugScheduler")

        super().setUp()

        # add users to db
        SeleniumTestCase.STANDARD_USERNAME_USER = SeleniumTestCase._BASE_USERNAME_USER
        SeleniumTestCase.STANDARD_USERNAME_ADMIN = SeleniumTestCase._BASE_USERNAME_ADMIN
        SeleniumTestCase.STANDARD_PASSWORD_USER = SeleniumTestCase._BASE_PASSWORD
        SeleniumTestCase.STANDARD_PASSWORD_ADMIN = SeleniumTestCase._BASE_PASSWORD

        SeleniumTestHelper.add_users_to_db(
            username_user=SeleniumTestCase.STANDARD_USERNAME_USER,
            username_admin=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password_user=SeleniumTestCase.STANDARD_PASSWORD_USER,
            password_admin=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )

        # import pyod algos
        SeleniumTestHelper.add_pyod_algos_to_db()

        # get base url
        self.driver.get(self.get_base_url())

        # try to log out
        SeleniumTestCase.logout(self)

    def tearDown(self) -> None:

        # if the test failed, take a screenshot and save the page source
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)

        SeleniumTestHelper.save_artefacts_if_failure(
            driver=self.driver,
            result=result,
            test_method_name=self._testMethodName,
            save_path=SeleniumTestCase.SELENIUM_ERROR_PATH,
        )

        # try to log out
        SeleniumTestCase.logout(self)

        super().tearDown()

        # delete old dirs (this includes the pyod algo directory)

        # cancel all still running tasks in the scheduler
        if Scheduler._instance is not None:
            Scheduler.get_instance().hard_shutdown()
            Scheduler._instance = None

        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        assert not os.path.isdir(settings.MEDIA_ROOT)

    # ------------ Helper Methods -----------------

    def get_base_url(self) -> str:
        return self.live_server_url

    def logout(self) -> bool:
        if "Logout" in self.driver.page_source:
            self.driver.find_element(By.LINK_TEXT, "Logout").click()
            return True
        else:
            return False

    def get_whole_page(self) -> WebElement:
        return self.driver.find_element(By.TAG_NAME, "html")

    # -------------- Additional asserts -----------

    def assertUrlMatches(
        self,
        url_suffix_regex: UrlsSuffixRegex,
        timeout: float = 30,
        interval: float = 0.5,
    ):
        prefix_slash: str = "/?"
        suffix_slash: str = "/?"

        if url_suffix_regex.value == "":
            url_suffix_regex_pattern = prefix_slash
        else:
            url_suffix_regex_pattern = (
                prefix_slash + url_suffix_regex.value + suffix_slash
            )

        url_pattern_full = re.escape(self.get_base_url()) + url_suffix_regex_pattern

        # wait dynamically for the new page to load;
        # if the loading takes longer than the timeout, fail the test
        start_time = datetime.datetime.now()
        while not re.fullmatch(url_pattern_full, self.driver.current_url):
            sleep(interval)
            if (datetime.datetime.now() - start_time) > datetime.timedelta(
                seconds=timeout
            ):
                self.fail(
                    "URL-Check failed. Either an error occured "
                    "or the loading took too long."
                )
