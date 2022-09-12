import os.path

from selenium.webdriver.common.by import By

from experiments.models import Algorithm
from systemtests.selenium_base_test_cases.SeleniumAlgorithm import SeleniumAlgorithm
from systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.LoggedInSeleniumTestCase import (
    LoggedInSeleniumTestCase,
)


class AlgorithmTests(LoggedInSeleniumTestCase):
    def navigate_to_dataset_overview(self):
        self.driver.find_element(By.LINK_TEXT, "Algorithms").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)

    def check_if_visible_in_overview(self, text):
        self.driver.find_element(By.LINK_TEXT, text)

    def test_algorithm_upload(self):
        algorithm = SeleniumAlgorithm(
            tc=self,
            name="Algorithm1",
            description="Description for Algorithm1",
            group=Algorithm.AlgorithmGroup.OTHER,
            path=os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py"),
            user=self.user,
        )
        algorithm.upload()
        self.check_if_visible_in_overview(algorithm.name)

    def test_delete_algorithm(self):
        algorithm = SeleniumAlgorithm(
            tc=self,
            name="Algorithm1",
            description="Description for Algorithm1",
            group=Algorithm.AlgorithmGroup.OTHER,
            path=os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py"),
            user=self.user,
        )
        algorithm.upload()
        algorithm.delete()

    def test_algorithm_edit(self):
        pass  # TODO: implement

    def test_overview(self):
        algorithm1 = SeleniumAlgorithm(
            tc=self,
            name="Algorithm1",
            description="Description for Algorithm1",
            group=Algorithm.AlgorithmGroup.OTHER,
            path=os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py"),
            user=self.user,
        )
        algorithm2 = SeleniumAlgorithm(
            tc=self,
            name="Algorithm2",
            description="Description for Algorithm2",
            group=Algorithm.AlgorithmGroup.GRAPH_BASED,
            path=os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py"),
            user=self.user,
        )
        algorithm3 = SeleniumAlgorithm(
            tc=self,
            name="Algorithm3",
            description="Description for Algorithm3",
            group=Algorithm.AlgorithmGroup.GRAPH_BASED,
            path=os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py"),
            user=self.user,
        )
        algorithm1.upload()
        algorithm2.upload()
        algorithm3.upload()

        self.check_if_visible_in_overview(algorithm1.name)
        self.check_if_visible_in_overview(algorithm1._group)
        self.check_if_visible_in_overview(algorithm2.name)
        self.check_if_visible_in_overview(algorithm2._group)
        self.check_if_visible_in_overview(algorithm3.name)
        self.check_if_visible_in_overview(algorithm3._group)
