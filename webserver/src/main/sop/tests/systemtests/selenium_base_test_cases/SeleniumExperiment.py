import datetime
from time import sleep
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from experiments.models import Experiment, Algorithm, Execution
from tests.systemtests.selenium_base_test_cases.SeleniumDataset import SeleniumDataset
from tests.systemtests.selenium_base_test_cases.SeleniumExecution import (
    SeleniumExecution,
)
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class SeleniumExperiment:
    def __init__(
        self,
        tc: SeleniumTestCase,
        dataset: SeleniumDataset,
        name: str,
        list_algo_names: List[str],
        user: SeleniumUser,
    ):
        self._tc = tc
        self._dataset = dataset
        self._name = name
        self._list_algo_names = list_algo_names
        self._user = user
        self._executions = List[SeleniumExecution]

    def create(self):
        self._tc.driver.find_element(By.LINK_TEXT, "Experiments").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        self._tc.driver.find_element(By.LINK_TEXT, "Create experiment").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_CREATE)

        # select dataset
        self._tc.driver.find_element(By.ID, "id_display_name").send_keys(self._name)
        dropdown = self._tc.driver.find_element(By.ID, "id_dataset")
        dropdown.find_element(
            By.XPATH,
            "//select/option[normalize-space(text()) = '" + self._dataset.name + "']",
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
        ]

        for group_xpath in group_xpath_list:
            group_element = self._tc.driver.find_element(By.XPATH, group_xpath)
            self._tc.driver.execute_script(
                "arguments[0].scrollIntoView();", group_element
            )

            sleep(0.5)

            WebDriverWait(self._tc.driver, 30).until(
                EC.element_to_be_clickable(group_element)
            )
            group_element.click()

        for current_algo in self._list_algo_names:
            algo_element = self._tc.driver.find_element(
                By.XPATH, "//span[contains(.,'" + current_algo + "')]/parent::*"
            )
            # scroll into view
            self._tc.driver.execute_script(
                "arguments[0].scrollIntoView();", algo_element
            )

            WebDriverWait(self._tc.driver, 30).until(
                EC.element_to_be_clickable(algo_element)
            )
            algo_element.click()

        self._tc.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # asserts
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)
        whole_page = self._tc.get_whole_page()

        self._tc.assertIn(self._name, whole_page.text)
        self._tc.assertIn(self._dataset.name, whole_page.text)
        for algo in self._list_algo_names:
            self._tc.assertIn(algo, whole_page.text)

        # TODO: select the correct divs (a bit more complex here)
        #      so that asserts are also valid
        #      with more than one experiment created

        # check in the database
        experiment = self.get_from_db()
        self._tc.assertEqual(experiment.dataset, self._dataset.get_from_db())
        self._tc.assertEqual(experiment.user, self._user.get_from_db())
        self._tc.assertListEqual(
            list(experiment.algorithms.all()),
            self.get_algo_from_db(),
        )

    def add_execution(self, execution: SeleniumExecution):
        self._tc.driver.find_element(
            By.LINK_TEXT, "New Execution"
        ).click()  # TODO mehrere Excecutions safe
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXECUTION_CREATE)

        # add subspace options
        self._tc.driver.find_element(By.ID, "id_subspace_amount").send_keys(
            execution.subspace_amount
        )
        self._tc.driver.find_element(By.ID, "id_subspaces_min").send_keys(
            execution.subspaces_min
        )
        self._tc.driver.find_element(By.ID, "id_subspaces_max").send_keys(
            execution.subspace_max
        )
        self._tc.driver.find_element(By.ID, "id_subspace_generation_seed").send_keys(
            execution.subspace_gen_seed
        )

        # change algorithm parameters for all algorithms
        for current_algo in execution.algos:

            # get all labels
            all_labels = self._tc.driver.find_elements(
                By.XPATH,
                "//div[text() = '"
                + current_algo["key"]
                + "']/parent::*/parent::*/descendant::label",
            )

            # set options
            for option in current_algo:
                if option != "key":

                    option_is_set = False

                    for current_label in all_labels:
                        if (option + " =") == current_label.text:
                            input_element = self._tc.driver.find_element(
                                By.ID, current_label.get_dom_attribute("for")
                            )
                            input_element.clear()
                            input_element.send_keys(current_algo[option])

                            option_is_set = True
                            break

                    # if the option was not set, fail the testcase (something is wrong)
                    if not option_is_set:
                        self._tc.fail(
                            "The option "
                            + str(option)
                            + " for algorithm "
                            + str(current_algo)
                            + " was not set."
                        )

        self._tc.driver.find_element(By.XPATH, "//input[@type='submit']").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

    def download_execution_result(self, execution):
        # TODO: make safe for than one execution
        self._tc.driver.find_element(By.XPATH, "//a[contains(text(),'Result')]").click()

    def wait_until_execution_finished(self, execution, timeout: int = 120):
        # TODO make safe for more than one execution and include db checks
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time) < datetime.timedelta(
            seconds=timeout
        ):
            sleep(1)
            dl_button = self._tc.driver.find_element(
                By.XPATH, "//a[contains(text(),'Result')]"
            )
            if dl_button.is_displayed():
                return

        # if a timeout occurred, fail
        db_executions = Execution.objects.all()
        db_single_exec: Execution = db_executions.first()
        print("-------DEBUG failed wait-----")
        print(db_executions)
        print(db_single_exec)
        print(db_single_exec.pk)
        print(db_single_exec.status)
        print(db_single_exec.progress)
        print("-------DEBUG END failed wait-----")

        self._tc.fail(
            "A timout occcured while waiting for the execution '"
            + str(execution)
            + "' to finish."
        )

    def get_from_db(self):
        experiment_list = Experiment.objects.filter(display_name=self._name)
        self._tc.assertEqual(len(experiment_list), 1)
        return experiment_list.first()

    def get_algo_from_db(self):
        result_list: List[Algorithm] = []

        for algo_str in self._list_algo_names:
            algos_in_db = Algorithm.objects.filter(display_name=algo_str)
            self._tc.assertEqual(len(algos_in_db), 1)
            result_list.append(algos_in_db.first())

        return result_list
