import os
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from experiments.models.dataset import CleaningState, Dataset
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class SeleniumDataset:
    def __init__(
        self,
        tc: SeleniumTestCase,
        path: str,
        name: str,
        description: str,
        user: SeleniumUser,
        failure_expected: bool,
    ):
        assert os.path.isfile(path)

        self._tc = tc
        self._path = path
        self._name = name
        self._description = description
        self._user = user
        self._failure_expected = failure_expected

    def upload(self):
        self._tc.driver.find_element(By.LINK_TEXT, "Datasets").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_OVERVIEW)

        self._tc.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_UPLOAD)

        self._tc.driver.find_element(By.ID, "id_display_name").send_keys(self._name)
        self._tc.driver.find_element(By.ID, "id_description").send_keys(
            self._description
        )
        absolute_path = os.path.join(os.getcwd(), self._path)
        self._tc.driver.find_element(By.ID, "id_path_original").send_keys(absolute_path)

        self._tc.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # assert the upload worked
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_OVERVIEW)
        whole_page = self._tc.get_whole_page()
        dataset_div = self._get_whole_div(whole_page)

        self._tc.assertIn(self._name, dataset_div.text)
        self._tc.assertIn(self._description, dataset_div.text)

        # check visibility of buttons
        download_button_cleaned = self._get_button_download_cleaned(whole_page)
        download_button_uncleaned = self._get_button_download_uncleaned(whole_page)

        self._tc.assertTrue(download_button_uncleaned.is_displayed())

        if self._get_cleaning_state(whole_page, self._name) == CleaningState.FINISHED:
            self._tc.assertTrue(download_button_cleaned.is_displayed())
        else:
            self._tc.assertFalse(download_button_cleaned.is_displayed())

        # check in the database
        dataset = self.get_from_db()
        self._tc.assertEqual(dataset.description, self._description)
        self._tc.assertEqual(dataset.user, self._user.get_from_db())

    def wait_until_cleaned(self):
        # wait until cleaned (or cleaning failed)
        while True:
            sleep(1)
            cleaning_state = self._get_cleaning_state(
                self._tc.get_whole_page(), self._name
            )
            if (cleaning_state == CleaningState.FINISHED) or (
                cleaning_state == CleaningState.FINISHED_WITH_ERROR
            ):
                break

        # check the database
        dataset = self.get_from_db()
        self._tc.assertNotEqual(dataset.is_cleaned, self._failure_expected)
        self._tc.assertTrue(dataset.has_finished)
        self._tc.assertEqual(dataset.has_error, self._failure_expected)

    def download_uncleaned(self):
        pass  # TODO implement

    def download_cleaned(self):
        pass  # TODO: implement

    def delete(self):
        pass  # TODO: implement

    def get_from_db(self):
        dataset_list = Dataset.objects.filter(display_name=self._name)
        self._tc.assertEqual(len(dataset_list), 1)
        return dataset_list.first()

    def _get_cleaning_state(self, whole_page: WebElement, name: str) -> CleaningState:
        text = self._get_dataset_status_element(whole_page).text

        if text == "cleaning in progress":
            return CleaningState["RUNNING"]
        elif text == "cleaned":
            return CleaningState["FINISHED"]
        elif text == "cleaning failed":
            return CleaningState["FINISHED_WITH_ERROR"]
        else:
            self._tc.fail("Unexpected Cleaning State of the Dataset: |" + text + "|")

    def _get_whole_div(self, whole_page: WebElement) -> WebElement:
        return whole_page.find_element(
            By.XPATH,
            "//a[normalize-space(text()) = '"
            + self._name
            + "']/parent::*/parent::*/parent::*",
        )

    def _get_button_download_uncleaned(
        self,
        whole_page: WebElement,
    ) -> WebElement:
        return self._get_whole_div(whole_page).find_element(
            By.XPATH,
            "//a[contains(text(),'Uncleaned')]",
        )

    def _get_button_download_cleaned(
        self,
        whole_page: WebElement,
    ) -> WebElement:
        return self._get_whole_div(whole_page).find_element(
            By.XPATH,
            "//a[contains(text(),'Cleaned')]",
        )

    def _get_dataset_status_element(
        self,
        whole_page: WebElement,
    ) -> WebElement:
        return self._get_whole_div(whole_page).find_element(
            By.CLASS_NAME, "dataset-status"
        )

    def rename(self, new_name, new_description):
        pass  # TODO: implement

    @property
    def name(self):
        return self._name

    @property
    def user(self):
        return self._user
