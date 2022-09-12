import os.path
import unittest

from selenium.webdriver.common.by import By

from systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.LoggedInSeleniumTestCase import (
    LoggedInSeleniumTestCase,
)
from tests.systemtests.selenium_base_test_cases.SeleniumDataset import SeleniumDataset


class DatasetUploadTests(LoggedInSeleniumTestCase):
    def navigate_to_dataset_overview(self):
        self.driver.find_element(By.LINK_TEXT, "Datasets").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.DATASET_OVERVIEW)

    def check_if_visible_in_overview(self, text):
        self.driver.find_element(By.LINK_TEXT, text)

    def test_valid_dataset_upload_download(self):
        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Test Dataset: Canada",
            description="This is the Canada Dataset, used for automated tests"
            " with Selenium.",
            user=self.user,
            failure_expected=False,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        dataset.download_uncleaned()
        dataset.download_cleaned()

    @unittest.expectedFailure
    def test_invalid_dataset_upload(self):
        failing_ds = SeleniumDataset(
            tc=self,
            path=os.path.join(
                "tests", "sample_datasets", "actually_invalid_dataset.csv"
            ),
            name="this is invalid",
            description="This is not valid",
            user=self.user,
            failure_expected=True,
        )

        failing_ds.upload()

    def test_valid_dataset_with_cleaning_failure(self):
        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "valid_dataset.csv"),
            name="Test Dataset: the cleaning will fail",
            description="cleaning fails",
            user=self.user,
            failure_expected=True,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        dataset.download_uncleaned()
        self.assertFalse(
            dataset._get_button_download_cleaned(self.get_whole_page()).is_displayed()
        )

    def test_delete_dataset_success(self):
        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Test Dataset: Canada",
            description="This is the Canada Dataset, used for automated tests"
            " with Selenium.",
            user=self.user,
            failure_expected=False,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        dataset.delete()

    @unittest.expectedFailure
    def test_delete_dataset_failure(self):
        non_existing_ds = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "not_here.csv"),
            name="Test Dataset: missing",
            description="This is missing.",
            user=self.user,
            failure_expected=False,
        )

        # DO NOT UPLOAD, so it does not exist
        non_existing_ds.delete()

    def test_rename_dataset_success(self):
        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Test Dataset: Canada",
            description="This is the Canada Dataset, used for automated tests"
            " with Selenium.",
            user=self.user,
            failure_expected=False,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        dataset.rename(
            new_name="this is a new name", new_description="this_is_a_new_description"
        )

    def test_rename_dataset_failure(self):
        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Test Dataset: Canada",
            description="This is the Canada Dataset, used for automated tests"
            " with Selenium.",
            user=self.user,
            failure_expected=False,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        name = ""
        description = "Sample description"

        other_ds = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Test Dataset: Canada2",
            description="other",
            user=self.user,
            failure_expected=False,
        )

        other_ds.upload()
        other_ds.wait_until_cleaned()

        other_ds.rename(new_name=name, new_description=description, expected_failure=True)

    def test_dataset_overview(self):
        dataset1 = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Dataset1",
            description="Description for Dataset1",
            user=self.user,
            failure_expected=False
        )
        dataset2 = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Dataset2",
            description="Description for Dataset2",
            user=self.user,
            failure_expected=False
        )
        dataset3 = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Dataset3",
            description="Description for Dataset3",
            user=self.user,
            failure_expected=False
        )

        dataset1.upload()
        dataset2.upload()
        dataset3.upload()
        dataset1.wait_until_cleaned()
        dataset2.wait_until_cleaned()
        dataset3.wait_until_cleaned()

        self.navigate_to_dataset_overview()

        self.check_if_visible_in_overview(dataset1.name)
        self.check_if_visible_in_overview(dataset2.name)
        self.check_if_visible_in_overview(dataset3.name)





