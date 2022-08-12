import os.path

from tests.systemtests.selenium_base_test_case.SeleniumTestCase import SeleniumTestCase

from selenium.webdriver.common.by import By


class DatasetUploadTests(SeleniumTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_standard_site(self):
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
        valid_dataset_path = os.path.join("tests", "sample_datasets", "canada.csv")
        print(valid_dataset_path)
        assert os.path.isfile(valid_dataset_path)

        self.driver.find_element(By.LINK_TEXT, "Datasets").click()
        self.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
        self.driver.find_element(By.ID, "id_display_name").send_keys("Test Dataset: Canada")
        self.driver.find_element(By.ID, "id_description").send_keys(
            "This is the Canada Dataset, used for automated tests with Selenium."
        )
        absolute_path = os.path.join(os.getcwd(), valid_dataset_path)
        self.driver.find_element(By.ID, "id_path_original").send_keys(absolute_path)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # assert the upload worked
        self.assertIn(SeleniumTestCase.BASE_URL + "dataset/overview", self.driver.current_url)
        # TODO: weitere Tests, v.a. zu hochgeladenem Datensatz


