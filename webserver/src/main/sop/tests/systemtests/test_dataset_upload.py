import os.path

from tests.systemtests.selenium_base_test_cases.SeleniumDataset import SeleniumDataset
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class DatasetUploadTests(SeleniumTestCase):
    def test_standard_site(self):
        user = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        user.login()

        # for the standard user, admin should not be visible
        self.assertNotIn("Admin", self.driver.page_source)
        self.assertNotIn("/admin/login", self.driver.page_source)

    def test_valid_dataset_upload(self):
        user = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        user.login()

        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Test Dataset: Canada",
            description="This is the Canada Dataset, used for automated tests"
                        " with Selenium.",
            user=user,
            failure_expected=False,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        dataset.download_uncleaned()
        dataset.download_cleaned()
