import os.path
import unittest

from tests.systemtests.selenium_base_test_cases.LoggedInSeleniumTestCase import (
    LoggedInSeleniumTestCase,
)
from tests.systemtests.selenium_base_test_cases.SeleniumDataset import SeleniumDataset


class DatasetUploadTests(LoggedInSeleniumTestCase):
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

        name = "Test Dataset: Canada"
        description = (
            "This is the Canada Dataset, used for automated tests with Selenium."
        )

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

        other_ds.rename(new_name=name, new_description=description)

    def test_dataset_overview(self):
        pass  # TODO: implement
