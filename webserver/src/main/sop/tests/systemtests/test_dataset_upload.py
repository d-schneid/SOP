import os.path

from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase


class DatasetUploadTests(SeleniumTestCase):
    def test_standard_site(self):
        # login
        self.login(
            SeleniumTestCase.STANDARD_USERNAME_USER,
            SeleniumTestCase.STANDARD_PASSWORD_USER,
        )

        # check, if links to subpages are in the generated site
        self.assertIn("/experiment/overview", self.driver.page_source)
        self.assertIn("/dataset/overview", self.driver.page_source)
        self.assertIn("/algorithm/overview", self.driver.page_source)

        # logout should be accessible
        self.assertIn("Logout", self.driver.page_source)
        self.assertIn("/logout", self.driver.page_source)

        # for the standard user, admin should not be visible
        self.assertNotIn("Admin", self.driver.page_source)
        self.assertNotIn("/admin/login", self.driver.page_source)

    def test_valid_dataset_upload(self):
        # login
        self.login(
            SeleniumTestCase.STANDARD_USERNAME_USER,
            SeleniumTestCase.STANDARD_PASSWORD_USER,
        )

        valid_dataset_path = os.path.join("tests", "sample_datasets", "canada.csv")

        dataset_name = "Test Dataset: Canada"
        dataset_description = (
            "This is the Canada Dataset, used for automated tests with Selenium."
        )

        self.upload_dataset(valid_dataset_path, dataset_name, dataset_description)
