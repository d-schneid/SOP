import datetime
import os
import re
import shutil
from enum import Enum
from time import sleep
from typing import List

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from authentication.models import User
from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from experiments.models import Experiment, Algorithm
from experiments.models.dataset import Dataset, CleaningState
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

    class AlgoGroup(Enum):
        PROBABILISTIC: str = "Probabilistic"
        LINEAR_MODEL: str = "Linear Model"
        PROXIMITY_BASED: str = "Proximity Based"
        OUTLIER_ENSEMBLES: str = "Outlier Ensembles"
        NEURONAL_NETWORKS: str = "Neural Networks"
        COMBINATION: str = "Combination"
        OTHER: str = "Other"

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
        self,
        dataset_path: str,
        dataset_name: str,
        dataset_description: str,
        username: str,
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
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_OVERVIEW)
        whole_page = self.get_whole_page()
        dataset_div = SeleniumTestHelper.get_dataset_div(whole_page, dataset_name)

        self.assertIn(dataset_name, dataset_div.text)
        self.assertIn(dataset_description, dataset_div.text)

        # check visibility of buttons
        download_button_cleaned = (
            SeleniumTestHelper.get_dataset_button_download_cleaned(
                whole_page, dataset_name
            )
        )
        download_button_uncleaned = (
            SeleniumTestHelper.get_dataset_button_download_uncleaned(
                whole_page, dataset_name
            )
        )

        self.assertTrue(download_button_uncleaned.is_displayed())

        if (
            self.get_dataset_cleaning_state(whole_page, dataset_name)
            == CleaningState.FINISHED
        ):
            self.assertTrue(download_button_cleaned.is_displayed())
        else:
            self.assertFalse(download_button_cleaned.is_displayed())

        # check in the database
        dataset = self.get_dataset_from_db(dataset_name)
        self.assertEqual(dataset.description, dataset_description)
        self.assertEqual(dataset.user, self.get_user_from_db(username))

    def create_experiment(
        self,
        experiment_name: str,
        dataset_name: str,
        list_algos: List[str],
        username: str,
    ):

        self.driver.find_element(By.LINK_TEXT, "Experiments").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        self.driver.find_element(By.LINK_TEXT, "Create experiment").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_CREATE)

        # select dataset
        self.driver.find_element(By.ID, "id_display_name").send_keys(experiment_name)
        dropdown = self.driver.find_element(By.ID, "id_dataset")
        dropdown.find_element(
            By.XPATH,
            "//select/option[normalize-space(text()) = '" + dataset_name + "']",
        ).click()

        # add algorithms
        # therefore, first open all flex-grow-elements
        # (so that algorithms can be selected from them)
        # -> special procedure ensures, that every element is acutally clickable
        #    (in this case this means mainly in screen)
        group_xpath_list = [
            "//div[@id='group_Probabilistic']/div",
            "//div[@id='group_LinearModel']/div",
            "//div[@id='group_Proximity-Based']/div",
            "//div[@id='group_OutlierEnsembles']/div",
            "//div[@id='group_NeuralNetworks']/div",
            "//div[@id='group_Combination']/div",
            "//div[@id='group_Other']/div",
        ]

        for group_xpath in group_xpath_list:
            group_element = self.driver.find_element(By.XPATH, group_xpath)
            self.driver.execute_script("arguments[0].scrollIntoView();", group_element)

            sleep(0.5)

            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(group_element)
            )
            group_element.click()

        for current_algo in list_algos:
            algo_element = self.driver.find_element(
                By.XPATH, "//span[contains(.,'" + current_algo + "')]/parent::*"
            )
            # scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView();", algo_element)

            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(algo_element)
            )
            algo_element.click()

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # asserts
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)
        whole_page = self.get_whole_page()

        self.assertIn(experiment_name, whole_page.text)
        self.assertIn(dataset_name, whole_page.text)
        for algo in list_algos:
            self.assertIn(algo, whole_page.text)

        # TODO: select the correct divs (a bit more complex here)
        #      so that asserts are also valid
        #      with more than one experiment created

        # check in the database
        experiment = self.get_experiment_from_db(experiment_name)
        self.assertEqual(experiment.dataset, self.get_dataset_from_db(dataset_name))
        self.assertEqual(experiment.user, self.get_user_from_db(username))
        self.assertListEqual(
            list(experiment.algorithms.all()), self.get_algos_from_db(list_algos)
        )

    def upload_algorithm(
        self,
        algo_name: str,
        algo_description: str,
        algo_group: AlgoGroup,
        algo_path: str,
        username: str,
    ):
        assert os.path.isfile(algo_path)

        self.driver.find_element(By.LINK_TEXT, "Algorithms").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)

        self.driver.find_element(By.LINK_TEXT, "Upload algorithm").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_UPLOAD)

        self.driver.find_element(By.ID, "id_display_name").send_keys(algo_name)
        self.driver.find_element(By.ID, "id_description").send_keys(algo_description)
        self.driver.find_element(By.ID, "id_group")
        dropdown = self.driver.find_element(By.ID, "id_group")
        dropdown.find_element(
            By.XPATH, "//option[normalize-space(text()) = '" + algo_group.value + "']"
        ).click()
        absolute_path = os.path.join(os.getcwd(), algo_path)
        self.driver.find_element(By.ID, "id_path").send_keys(absolute_path)

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        page_source = self.driver.page_source
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)
        self.assertIn(algo_name, page_source)
        self.assertIn(algo_description, page_source)

        # database check
        algo: Algorithm = self.get_algos_from_db([algo_name])[0]
        self.assertEqual(algo.display_name, algo_name)
        self.assertEqual(algo.description, algo_description)
        self.assertEqual(algo.user, self.get_user_from_db(username))

        algo_group_regex = algo_group.value.replace(" ", "[\s\-]")  # noqa: W605

        self.assertRegex(algo.group, algo_group_regex)

        # TODO: select the correct div so that asserts are also valid
        #  with more than one algo uploaded
        # TODO: check info displayed on the page

    def get_whole_page(self) -> WebElement:
        return self.driver.find_element(By.TAG_NAME, "html")

    def wait_until_dataset_ready(self, dataset_name: str, failure_expected: bool):
        # wait until cleaned (or cleaning failed)
        while True:
            sleep(1)
            cleaning_state = self.get_dataset_cleaning_state(
                self.get_whole_page(), dataset_name
            )
            if (cleaning_state == CleaningState.FINISHED) or (
                cleaning_state == CleaningState.FINISHED_WITH_ERROR
            ):
                break

        # check the database
        dataset = self.get_dataset_from_db(dataset_name)
        self.assertNotEqual(dataset.is_cleaned, failure_expected)
        self.assertTrue(dataset.has_finished)
        self.assertEqual(dataset.has_error, failure_expected)

    def get_dataset_cleaning_state(
        self, whole_page: WebElement, dataset_name: str
    ) -> CleaningState:
        text = SeleniumTestHelper.get_dataset_status_element(
            whole_page, dataset_name
        ).text

        if text == "cleaning in progress":
            return CleaningState["RUNNING"]
        elif text == "cleaned":
            return CleaningState["FINISHED"]
        elif text == "cleaning failed":
            return CleaningState["FINISHED_WITH_ERROR"]
        else:
            self.fail("Unexpected Cleaning State of the Dataset: |" + text + "|")

    def get_user_from_db(self, username: str):
        user_list = User.objects.filter(username=username)
        self.assertEqual(len(user_list), 1)
        return user_list.first()

    def get_dataset_from_db(self, dataset_name: str) -> Dataset:
        dataset_list = Dataset.objects.filter(display_name=dataset_name)
        self.assertEqual(len(dataset_list), 1)
        return dataset_list.first()

    def get_experiment_from_db(self, experiment_name: str):
        experiment_list = Experiment.objects.filter(display_name=experiment_name)
        self.assertEqual(len(experiment_list), 1)
        return experiment_list.first()

    def get_algos_from_db(self, algo_list: List[str]) -> List[Algorithm]:
        result_list: List[Algorithm] = []

        for algo_str in algo_list:
            algos_in_db = Algorithm.objects.filter(display_name=algo_str)
            self.assertEqual(len(algos_in_db), 1)
            result_list.append(algos_in_db.first())

        return result_list

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
