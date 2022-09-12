import os

from selenium.webdriver.common.by import By

from experiments.models import Algorithm
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class SeleniumAlgorithm:
    def __init__(
        self,
        tc: SeleniumTestCase,
        name: str,
        description: str,
        group: Algorithm.AlgorithmGroup,
        path: str,
        user: SeleniumUser,
    ):
        assert os.path.isfile(path)

        self._tc = tc
        self._name = name
        self._description = description
        self._group = group
        self._path = path
        self._user = user

    def upload(self):
        self._tc.driver.find_element(By.LINK_TEXT, "Algorithms").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)

        self._tc.driver.find_element(By.LINK_TEXT, "Upload algorithm").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_UPLOAD)

        self._tc.driver.find_element(By.ID, "id_display_name").send_keys(self._name)
        self._tc.driver.find_element(By.ID, "id_description").send_keys(
            self._description
        )
        self._tc.driver.find_element(By.ID, "id_group")
        dropdown = self._tc.driver.find_element(By.ID, "id_group")
        dropdown.find_element(
            By.XPATH,
            "//option[normalize-space(text()) = '"
            + self._group.value.replace("-", " ")
            + "']",
        ).click()
        absolute_path = os.path.join(os.getcwd(), self._path)
        self._tc.driver.find_element(By.ID, "id_path").send_keys(absolute_path)

        self._tc.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        page_source = self._tc.driver.page_source
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)
        self._tc.assertIn(self._name, page_source)
        self._tc.assertIn(self._description, page_source)

        # database check
        algo: Algorithm = self.get_from_db()
        self._tc.assertEqual(algo.display_name, self._name)
        self._tc.assertEqual(algo.description, self._description)
        self._tc.assertEqual(algo.user, self._user.get_from_db())

        algo_group_regex = self._group.value.replace(" ", "[\s\-]")  # noqa: W605

        self._tc.assertRegex(algo.group, algo_group_regex)

        # TODO: select the correct div so that asserts are also valid
        #  with more than one algo uploaded
        # TODO: check info displayed on the page

    def get_from_db(self):
        algos_in_db = Algorithm.objects.filter(display_name=self._name)
        self._tc.assertEqual(len(algos_in_db), 1)
        return algos_in_db.first()

    def delete(self):
        algo = self.get_from_db()
        self._tc.driver.find_element(By.LINK_TEXT, "Algorithms").click()
        self._tc.driver.find_element(
            By.CSS_SELECTOR, f"#collapse_{algo.pk} .d-flex > .btn-danger > .bi"
        ).click()
        self._tc.driver.find_element(
            By.CSS_SELECTOR, f"#deleteModal{algo.pk} form > .btn"
        ).click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)
        self._tc.assertEqual(Algorithm.objects.filter(pk=algo.pk).count(), 0)

    @property
    def name(self):
        return self._name
